"""Existing-only production entry and durable maintenance are API-free."""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from scripts.news.translation_budget import BudgetBusy, BudgetError, BudgetLedger
from scripts.news.translation_production import ProductionBudgetLedger

ROOT = Path(__file__).resolve().parents[2]
DAY = datetime(2026, 11, 8, tzinfo=timezone.utc)


def production(path, daily=100):
    return ProductionBudgetLedger(
        path, daily_limit_microusd=daily, batch_limit_microusd=80
    )


def bootstrap(path):
    with BudgetLedger(path, daily_limit_microusd=100, batch_limit_microusd=80).batch(
        "fixture"
    ) as batch:
        batch.reserve("attempt", 40, at=DAY)


def records(path):
    with sqlite3.connect(path) as db:
        return (
            db.execute("SELECT * FROM runs ORDER BY run_id").fetchall(),
            db.execute("SELECT * FROM reservations ORDER BY reservation_id").fetchall(),
        )


def assert_blocked(guard):
    attempts = []
    with pytest.raises(BudgetError):
        guard.check_ready()
    with pytest.raises(BudgetError):
        with guard.batch("blocked") as batch:
            batch.reserve("attempt", 10, at=DAY)
            attempts.append("API would run here")
    assert attempts == []


def test_missing_production_storage_never_bootstraps_or_makes_directories(tmp_path):
    path = tmp_path / "absent" / "budget.sqlite"
    assert_blocked(production(path))
    assert not path.parent.exists()


def test_missing_db_with_existing_lock_remains_absent(tmp_path):
    path = tmp_path / "budget.sqlite"
    path.with_name(path.name + ".lock").touch(mode=0o600)
    assert_blocked(production(path))
    assert not path.exists()


def test_missing_lock_does_not_get_recreated(tmp_path):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    before = records(path)
    lock = path.with_name(path.name + ".lock")
    lock.unlink()
    assert_blocked(production(path))
    assert not lock.exists() and records(path) == before


@pytest.mark.parametrize("kind", ["empty", "corrupt", "policy"])
def test_bad_storage_never_initializes_new_run(tmp_path, kind):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    if kind == "empty":
        path.write_bytes(b"")
    elif kind == "corrupt":
        path.write_bytes(b"corrupt original evidence")
    before = path.read_bytes()
    assert_blocked(production(path, daily=1000 if kind == "policy" else 100))
    assert path.read_bytes() == before


def test_preflight_is_readonly_and_clear_keeps_costs_and_lock_inode(tmp_path):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)
    before = records(path)
    inode = path.with_name(path.name + ".lock").stat().st_ino
    guard.check_ready()
    assert records(path) == before
    guard.enter_maintenance("restore-1", "restore")
    assert_blocked(production(path))
    with pytest.raises(BudgetError):
        guard.clear_maintenance("wrong-id")
    assert guard.maintenance_path.exists()
    guard.clear_maintenance("restore-1")
    assert not guard.maintenance_path.exists()
    production(path).check_ready()
    assert records(path) == before
    assert path.with_name(path.name + ".lock").stat().st_ino == inode
    with production(path).batch("after-clear") as batch:
        with pytest.raises(BudgetError):
            batch.reserve("too-much", 61, at=DAY)


@pytest.mark.parametrize(
    "shape",
    ["invalid-json", "extra", "directory", "symlink", "broken-symlink", "unreadable"],
)
def test_bad_marker_blocks_and_cannot_be_automatically_cleared(tmp_path, shape):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)
    marker = guard.maintenance_path
    if shape == "directory":
        marker.mkdir()
    elif shape in ("symlink", "broken-symlink"):
        target = tmp_path / "target.json"
        if shape == "symlink":
            target.write_text(
                '{"version":1,"operation_id":"restore-1","reason_code":"restore"}'
            )
        marker.symlink_to(target)
    else:
        marker.write_text(
            "broken"
            if shape == "invalid-json"
            else json.dumps(
                {
                    "version": 1,
                    "operation_id": "restore-1",
                    "reason_code": "restore",
                    "extra": "untrusted",
                }
                if shape == "extra"
                else {
                    "version": 1,
                    "operation_id": "restore-1",
                    "reason_code": "restore",
                }
            )
        )
        if shape == "unreadable":
            marker.chmod(0)
    before = records(path)
    assert_blocked(guard)
    with pytest.raises(BudgetError):
        guard.clear_maintenance("restore-1")
    assert os.path.lexists(marker)
    assert records(path) == before


def test_missing_marker_clear_is_rejected(tmp_path):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    with pytest.raises(BudgetError):
        production(path).clear_maintenance("restore-1")


def test_enter_can_freeze_missing_or_corrupt_db_without_initializing_it(tmp_path):
    for kind in ("missing", "corrupt"):
        folder = tmp_path / kind
        folder.mkdir()
        path = folder / "budget.sqlite"
        path.with_name(path.name + ".lock").touch(mode=0o600)
        if kind == "corrupt":
            path.write_bytes(b"evidence")
        guard = production(path)
        guard.enter_maintenance("incident-1", "storage_incident")
        assert guard.maintenance_path.exists()
        with pytest.raises(BudgetError):
            guard.clear_maintenance("incident-1")
        assert guard.maintenance_path.exists()
        assert (
            not path.exists() if kind == "missing" else path.read_bytes() == b"evidence"
        )


def test_existing_marker_never_overwritten_and_reason_allowlist(tmp_path):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)
    with pytest.raises(BudgetError):
        guard.enter_maintenance("one", "secret-free-text")
    assert not guard.maintenance_path.exists()
    guard.enter_maintenance("one", "planned_maintenance")
    before = guard.maintenance_path.read_bytes()
    with pytest.raises(BudgetError):
        guard.enter_maintenance("two", "restore")
    assert guard.maintenance_path.read_bytes() == before


def test_new_process_retains_maintenance_and_controls_obey_same_flock(tmp_path):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    program = """import sys
from pathlib import Path
from scripts.news.translation_budget import BudgetBusy,BudgetError
from scripts.news.translation_production import ProductionBudgetLedger
ledger=ProductionBudgetLedger(Path(sys.argv[1]),daily_limit_microusd=100,batch_limit_microusd=80)
try:
    if sys.argv[2]=="enter": ledger.enter_maintenance("op","restore")
    elif sys.argv[2]=="clear": ledger.clear_maintenance("op")
    else: ledger.check_ready()
except BudgetBusy: sys.exit(21)
except BudgetError: sys.exit(22)
"""

    def child(action):
        return subprocess.run(
            [sys.executable, "-c", program, str(path), action],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        ).returncode

    guard = production(path)
    with guard.batch("active"):
        assert child("enter") == 21
        assert child("clear") == 21
        assert not guard.maintenance_path.exists()
    guard.enter_maintenance("op", "restore")
    assert child("check") == 22
    assert child("clear") == 0
    assert child("check") == 0


def test_deleted_db_during_strict_batch_cannot_be_recreated(tmp_path):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    with pytest.raises(BudgetError):
        with production(path).batch("active") as batch:
            path.unlink()
            batch.reserve("blocked", 1, at=DAY)
    assert not path.exists()
    assert path.with_name(path.name + ".lock").exists()


def test_clear_directory_fsync_failure_restores_blocking_marker(tmp_path, monkeypatch):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)
    guard.enter_maintenance("op", "restore")
    original = os.fsync
    failed = []

    def fail_once(fd):
        if not failed:
            failed.append(True)
            raise OSError("injected clear sync failure")
        return original(fd)

    monkeypatch.setattr(os, "fsync", fail_once)
    with pytest.raises(BudgetError):
        guard.clear_maintenance("op")
    assert os.path.lexists(guard.maintenance_path)
    assert_blocked(production(path))


@pytest.mark.parametrize("reason", [[], {}, None, 1])
def test_enter_rejects_nontext_reason_without_marker(tmp_path, reason):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)
    with pytest.raises(BudgetError):
        guard.enter_maintenance("op", reason)
    assert not os.path.lexists(guard.maintenance_path)


@pytest.mark.parametrize(
    "raw",
    [
        '{"version":1,"operation_id":"op","reason_code":[]}',
        '{"version":1,"operation_id":"op","reason_code":{}}',
        '{"version":true,"operation_id":"op","reason_code":"restore"}',
        '{"version":1,"operation_id":"wrong","operation_id":"op","reason_code":"restore"}',
    ],
)
def test_malformed_marker_fields_never_clear(tmp_path, raw):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)
    guard.maintenance_path.write_text(raw)
    assert_blocked(guard)
    with pytest.raises(BudgetError):
        guard.clear_maintenance("op")
    assert guard.maintenance_path.read_text() == raw


@pytest.mark.parametrize("operation", ["preflight", "batch"])
def test_db_deleted_after_flock_never_recreated(tmp_path, monkeypatch, operation):
    import fcntl

    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)
    original = fcntl.flock

    def remove_after_lock(fd, flags):
        original(fd, flags)
        path.unlink()

    monkeypatch.setattr(fcntl, "flock", remove_after_lock)
    with pytest.raises(BudgetError):
        if operation == "preflight":
            guard.check_ready()
        else:
            with guard.batch("blocked"):
                pytest.fail("Deleted DB was reopened")
    assert not path.exists()


def test_enter_sync_failure_keeps_a_blocking_marker(tmp_path, monkeypatch):
    path = tmp_path / "budget.sqlite"
    bootstrap(path)
    guard = production(path)

    def fail(_):
        raise OSError("injected sync failure")

    monkeypatch.setattr(os, "fsync", fail)
    with pytest.raises(BudgetError):
        guard.enter_maintenance("op", "restore")
    assert os.path.lexists(guard.maintenance_path)
    assert_blocked(guard)
