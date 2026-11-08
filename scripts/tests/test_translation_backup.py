"""Local snapshots and matched-state restore never reset accounting or locks."""

import hashlib
import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.news.translation_backup import LedgerBackup
from scripts.news.translation_budget import BudgetError, BudgetLedger
from scripts.news.translation_production import ProductionBudgetLedger

ROOT = Path(__file__).resolve().parents[2]
DAY = datetime(2026, 11, 8, tzinfo=timezone.utc)


def prepare(tmp_path):
    path = tmp_path / "budget.sqlite"
    with BudgetLedger(path, daily_limit_microusd=1000, batch_limit_microusd=1000).batch(
        "original"
    ) as batch:
        batch.reserve("attempt", 500, at=DAY)
    ledger = ProductionBudgetLedger(
        path, daily_limit_microusd=1000, batch_limit_microusd=1000
    )
    return path, ledger, LedgerBackup(ledger)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_snapshot_roundtrip_preserves_rows_unsettled_policy_and_history(tmp_path):
    path, ledger, tool = prepare(tmp_path)
    before = path.read_bytes()
    inode = path.with_name(path.name + ".lock").stat().st_ino
    snapshot = tmp_path / "snapshot"
    report = tool.backup(snapshot)
    assert report["status"] == "backed_up"
    manifest = json.loads((snapshot / "manifest.json").read_text())
    assert manifest["sha256"] == digest(snapshot / "budget.sqlite")
    assert manifest["counts"]["unsettled"] == 1
    assert manifest["counts"]["charged_microusd"] == 500
    assert path.read_bytes() == before
    for file in (snapshot / "budget.sqlite", snapshot / "manifest.json"):
        assert file.stat().st_mode & 0o777 == 0o600
    assert snapshot.stat().st_mode & 0o777 == 0o700
    frozen = {file.name: digest(file) for file in snapshot.iterdir()}
    ledger.enter_maintenance("restore-one", "restore")
    marker = ledger.maintenance_path.read_bytes()
    result = tool.restore(snapshot, "restore-one")
    assert result["status"] == "restored"
    assert ledger.maintenance_path.read_bytes() == marker
    assert path.with_name(path.name + ".lock").stat().st_ino == inode
    assert {file.name: digest(file) for file in snapshot.iterdir()} == frozen
    assert path.read_bytes() == (snapshot / "budget.sqlite").read_bytes()
    ledger.clear_maintenance("restore-one")
    with ledger.batch("remaining") as batch:
        with pytest.raises(BudgetError):
            batch.reserve("too-much", 501, at=DAY)


def test_maintenance_required_and_wrong_operation_rejected_without_active_write(
    tmp_path,
):
    path, ledger, tool = prepare(tmp_path)
    snap = tmp_path / "snapshot"
    tool.backup(snap)
    before = path.read_bytes()
    with pytest.raises(BudgetError):
        tool.restore(snap, "restore-one")
    ledger.enter_maintenance("restore-one", "restore")
    with pytest.raises(BudgetError):
        tool.restore(snap, "wrong-id")
    assert path.read_bytes() == before and ledger.maintenance_path.exists()


def test_stale_snapshot_missing_400_cost_cannot_be_restored(tmp_path):
    path, ledger, tool = prepare(tmp_path)
    snap = tmp_path / "old"
    tool.backup(snap)
    with ledger.batch("latest") as batch:
        batch.reserve("later", 400, at=DAY)
    before = path.read_bytes()
    ledger.enter_maintenance("restore-one", "restore")
    with pytest.raises(BudgetError):
        tool.restore(snap, "restore-one")
    assert path.read_bytes() == before
    assert ledger.maintenance_path.exists()
    assert not list(tmp_path.glob(".budget-quarantine-*"))


@pytest.mark.parametrize(
    "kind",
    [
        "checksum",
        "policy",
        "duplicate-json",
        "extra-json",
        "symlink-db",
        "hardlink-db",
        "symlink-dir",
    ],
)
def test_untrusted_snapshot_rejected_before_write(tmp_path, kind):
    path, ledger, tool = prepare(tmp_path)
    snap = tmp_path / "snapshot"
    tool.backup(snap)
    manifest = snap / "manifest.json"
    data = json.loads(manifest.read_text())
    if kind == "checksum":
        (snap / "budget.sqlite").write_bytes(b"changed")
    elif kind == "policy":
        data["policy"]["daily_limit_microusd"] = 999
        manifest.write_text(json.dumps(data))
    elif kind == "duplicate-json":
        manifest.write_text(
            manifest.read_text().replace('"version": 1', '"version": 9, "version": 1')
        )
    elif kind == "extra-json":
        data["override"] = True
        manifest.write_text(json.dumps(data))
    elif kind == "symlink-db":
        original = tmp_path / "source.sqlite"
        (snap / "budget.sqlite").rename(original)
        (snap / "budget.sqlite").symlink_to(original)
    elif kind == "hardlink-db":
        import os

        os.link(snap / "budget.sqlite", tmp_path / "alias.sqlite")
    else:
        alias = tmp_path / "alias"
        alias.symlink_to(snap, target_is_directory=True)
        snap = alias
    ledger.enter_maintenance("restore-one", "restore")
    before = path.read_bytes()
    with pytest.raises(BudgetError):
        tool.restore(snap, "restore-one")
    assert path.read_bytes() == before and ledger.maintenance_path.exists()


@pytest.mark.parametrize("kind", ["missing", "empty", "corrupt"])
def test_missing_or_corrupt_current_state_cannot_prove_safe_restore(tmp_path, kind):
    path, ledger, tool = prepare(tmp_path)
    snap = tmp_path / "snapshot"
    tool.backup(snap)
    ledger.enter_maintenance("restore-one", "storage_incident")
    if kind == "missing":
        path.unlink()
    else:
        path.write_bytes(b"" if kind == "empty" else b"corrupt evidence")
    before = path.read_bytes() if path.exists() else None
    with pytest.raises(BudgetError):
        tool.restore(snap, "restore-one")
    assert (path.read_bytes() if path.exists() else None) == before
    assert ledger.maintenance_path.exists()


def test_backup_never_overwrites_or_uses_active_paths(tmp_path):
    path, ledger, tool = prepare(tmp_path)
    snap = tmp_path / "snapshot"
    tool.backup(snap)
    original = (snap / "manifest.json").read_bytes()
    for target in (
        snap,
        path,
        path.parent,
        ledger.maintenance_path,
        path.with_name(path.name + ".lock"),
        snap / "nested",
    ):
        with pytest.raises(BudgetError):
            tool.backup(target)
    assert (snap / "manifest.json").read_bytes() == original


def test_backup_missing_source_uses_readonly_and_cannot_create_files(tmp_path):
    path = tmp_path / "missing.sqlite"
    path.with_name(path.name + ".lock").touch(mode=0o600)
    ledger = ProductionBudgetLedger(
        path, daily_limit_microusd=1000, batch_limit_microusd=1000
    )
    with pytest.raises(BudgetError):
        LedgerBackup(ledger).backup(tmp_path / "snapshot")
    assert not path.exists() and not (tmp_path / "snapshot").exists()


def test_pre_replace_failure_keeps_active_and_marker(tmp_path, monkeypatch):
    import scripts.news.translation_backup as module

    path, ledger, tool = prepare(tmp_path)
    snap = tmp_path / "snapshot"
    tool.backup(snap)
    ledger.enter_maintenance("restore-one", "restore")
    before = path.read_bytes()
    marker = ledger.maintenance_path.read_bytes()

    def fail(*args, **kwargs):
        raise OSError("injected replacement failure")

    monkeypatch.setattr(module.os, "replace", fail)
    with pytest.raises(BudgetError):
        tool.restore(snap, "restore-one")
    assert (
        path.read_bytes() == before and ledger.maintenance_path.read_bytes() == marker
    )


def child_try_batch(path):
    program = """from pathlib import Path
import sys
from scripts.news.translation_production import ProductionBudgetLedger
from scripts.news.translation_budget import BudgetBusy
try:
    with ProductionBudgetLedger(Path(sys.argv[1]),daily_limit_microusd=1000,batch_limit_microusd=1000).batch("child"): pass
except BudgetBusy: sys.exit(21)
"""
    return subprocess.run(
        [sys.executable, "-c", program, str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    ).returncode


def test_backup_writer_exclusion_both_directions(tmp_path, monkeypatch):
    path, ledger, tool = prepare(tmp_path)
    with ledger.batch("active"):
        with pytest.raises(BudgetError):
            tool.backup(tmp_path / "busy")
    assert not (tmp_path / "busy").exists()
    original = tool._audit
    observed = []

    def audit(target):
        if target == path:
            observed.append(child_try_batch(path))
        return original(target)

    monkeypatch.setattr(tool, "_audit", audit)
    tool.backup(tmp_path / "snapshot")
    assert observed and all(code == 21 for code in observed)


def test_policy_mismatch_current_ledger_cannot_make_backup(tmp_path):
    path, _, _ = prepare(tmp_path)
    before = path.read_bytes()
    wrong = ProductionBudgetLedger(
        path, daily_limit_microusd=900, batch_limit_microusd=1000
    )
    with pytest.raises(BudgetError):
        LedgerBackup(wrong).backup(tmp_path / "snapshot")
    assert path.read_bytes() == before and not (tmp_path / "snapshot").exists()


def test_cold_nonhot_sidecars_preserved_in_quarantine_and_removed_before_replace(
    tmp_path,
):
    path, ledger, tool = prepare(tmp_path)
    snapshot = tmp_path / "snapshot"
    tool.backup(snapshot)
    sidecar = path.with_name(path.name + "-journal")
    sidecar.write_bytes(b"")
    ledger.enter_maintenance("restore-one", "restore")
    result = tool.restore(snapshot, "restore-one")
    quarantined = Path(result["quarantine_dir"]) / sidecar.name
    assert quarantined.exists() and quarantined.read_bytes() == b""
    assert not sidecar.exists() and ledger.maintenance_path.exists()


def test_quoted_check_literal_change_is_not_normalized_into_approved_schema(tmp_path):
    path, _, tool = prepare(tmp_path)
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA writable_schema=ON")
        db.execute(
            "UPDATE sqlite_master SET sql=replace(sql, '''open''', '''Open''') WHERE name='runs'"
        )
        db.execute("PRAGMA writable_schema=OFF")
    with pytest.raises(BudgetError, match="schema"):
        tool.backup(tmp_path / "snapshot")
    assert not (tmp_path / "snapshot").exists()


def test_new_snapshot_and_quarantine_parent_are_synced_before_replace(
    tmp_path, monkeypatch
):
    import scripts.news.translation_backup as module

    path, ledger, tool = prepare(tmp_path)
    snapshot = tmp_path / "snapshot"
    events = []
    sync = module._sync_dir
    replace = module.os.replace

    def record_sync(directory):
        events.append(("sync", directory))
        return sync(directory)

    def record_replace(source, destination):
        events.append(("replace", destination))
        return replace(source, destination)

    monkeypatch.setattr(module, "_sync_dir", record_sync)
    monkeypatch.setattr(module.os, "replace", record_replace)
    tool.backup(snapshot)
    assert ("sync", snapshot.parent) in events
    events.clear()
    ledger.enter_maintenance("restore-one", "restore")
    result = tool.restore(snapshot, "restore-one")
    quarantine = Path(result["quarantine_dir"])
    child_sync = events.index(("sync", quarantine))
    parent_sync = events.index(("sync", path.parent), child_sync + 1)
    replaced = events.index(("replace", path))
    assert child_sync < parent_sync < replaced


def test_each_new_snapshot_ancestor_is_synced_before_completion(tmp_path, monkeypatch):
    import scripts.news.translation_backup as backup_module

    _, _, tool = prepare(tmp_path)
    synced = []
    original = backup_module._sync_dir

    def record(path):
        synced.append(path)
        original(path)

    monkeypatch.setattr(backup_module, "_sync_dir", record)
    tool.backup(tmp_path / "new-root" / "new-group" / "snapshot")
    assert synced[:3] == [
        tmp_path,
        tmp_path / "new-root",
        tmp_path / "new-root/new-group",
    ]
