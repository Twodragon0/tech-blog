"""The local backup CLI keeps production admission and maintenance intact."""

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from scripts.manage_translation_ledger import main
from scripts.news.translation_budget import BudgetLedger
from scripts.news.translation_production import ProductionBudgetLedger

ROOT = Path(__file__).resolve().parents[2]


def _bootstrap(path):
    with BudgetLedger(path, daily_limit_microusd=1000, batch_limit_microusd=800).batch(
        "fixture"
    ) as batch:
        reservation = batch.reserve("confirmed", 700, at=datetime.now(timezone.utc))
        batch.settle(reservation, 200)
        batch.reserve("pending", 300, at=datetime.now(timezone.utc))


def _run(command, ledger, snapshot, operation=None):
    args = [
        sys.executable,
        str(ROOT / "scripts/manage_translation_ledger.py"),
        command,
        "--ledger",
        str(ledger),
        "--snapshot-dir",
        str(snapshot),
        "--daily-limit-microusd",
        "1000",
        "--batch-limit-microusd",
        "800",
    ]
    if operation is not None:
        args += ["--operation-id", operation]
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=30)


def test_cli_verified_backup_restore_keeps_marker_and_lock(tmp_path):
    ledger, snapshot = tmp_path / "budget.sqlite", tmp_path / "snapshot"
    _bootstrap(ledger)
    lock = ledger.with_name(ledger.name + ".lock")
    inode = lock.stat().st_ino
    backup = _run("backup", ledger, snapshot)
    assert backup.returncode == 0, backup.stderr
    assert json.loads(backup.stdout)["action"] == "backup"
    digest = hashlib.sha256((snapshot / "budget.sqlite").read_bytes()).hexdigest()
    guard = ProductionBudgetLedger(
        ledger, daily_limit_microusd=1000, batch_limit_microusd=800
    )
    guard.enter_maintenance("cli-restore", "restore")
    restored = _run("restore", ledger, snapshot, "cli-restore")
    assert restored.returncode == 0, restored.stderr
    restored_report = json.loads(restored.stdout)
    assert restored_report["action"] == "restore"
    assert restored_report["result"]["counts"] == {
        "runs": 1,
        "reservations": 2,
        "unsettled": 1,
        "charged_microusd": 500,
    }
    assert guard.maintenance_path.exists()
    assert lock.stat().st_ino == inode
    assert (
        hashlib.sha256((snapshot / "budget.sqlite").read_bytes()).hexdigest() == digest
    )


def test_cli_missing_ledger_never_bootstraps(tmp_path):
    ledger = tmp_path / "missing" / "budget.sqlite"
    result = _run("backup", ledger, tmp_path / "snapshot")
    assert result.returncode == 1
    assert not ledger.exists() and not ledger.parent.exists()


def test_cli_restore_without_maintenance_does_not_touch_active(tmp_path):
    ledger, snapshot = tmp_path / "budget.sqlite", tmp_path / "snapshot"
    _bootstrap(ledger)
    assert _run("backup", ledger, snapshot).returncode == 0
    before = ledger.read_bytes()
    result = _run("restore", ledger, snapshot, "not-active")
    assert result.returncode == 1 and ledger.read_bytes() == before


def test_cli_refuses_checkout_snapshot_destination(tmp_path):
    ledger = tmp_path / "budget.sqlite"
    _bootstrap(ledger)
    result = _run("backup", ledger, ROOT / "_site" / "private-ledger")
    assert result.returncode == 1


def test_cli_has_no_force_or_maintenance_clear_switch(tmp_path):
    import pytest

    with pytest.raises(SystemExit) as caught:
        main(
            [
                "restore",
                "--ledger",
                str(tmp_path / "ledger"),
                "--snapshot-dir",
                str(tmp_path / "snapshot"),
                "--daily-limit-microusd",
                "1000",
                "--batch-limit-microusd",
                "800",
                "--operation-id",
                "op",
                "--force",
            ]
        )
    assert caught.value.code == 2


def test_cli_refuses_dangling_snapshot_symlink_before_resolving(tmp_path):
    ledger = tmp_path / "budget.sqlite"
    _bootstrap(ledger)
    target, alias = tmp_path / "new-snapshot", tmp_path / "alias"
    alias.symlink_to(target, target_is_directory=True)
    result = _run("backup", ledger, alias)
    assert result.returncode == 1
    assert not target.exists()
