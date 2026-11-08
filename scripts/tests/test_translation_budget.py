"""Persistent micro-USD reservations and cross-process serialization, API-free."""

import json
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from scripts.news.translation_budget import BudgetBusy, BudgetError, BudgetLedger

ROOT = Path(__file__).resolve().parents[2]
DAY = datetime(2026, 11, 8, tzinfo=timezone.utc)


def ledger(path, daily=100, batch=80):
    return BudgetLedger(path, daily_limit_microusd=daily, batch_limit_microusd=batch)


def charges(path):
    with sqlite3.connect(path) as db:
        return db.execute(
            "SELECT utc_day,reserved_microusd,actual_microusd FROM reservations ORDER BY rowid"
        ).fetchall()


@pytest.mark.parametrize("value", [0, -1, True, False, 1.5, "10", None, 2**63])
@pytest.mark.parametrize("field", ["daily_limit_microusd", "batch_limit_microusd"])
def test_invalid_limits_fail_before_storage(tmp_path, value, field):
    policy = {"daily_limit_microusd": 100, "batch_limit_microusd": 80, field: value}
    with pytest.raises(BudgetError):
        BudgetLedger(tmp_path / "budget.db", **policy)
    assert not (tmp_path / "budget.db").exists()


def test_reserve_settle_lower_and_daily_cost_survives_restart(tmp_path):
    path = tmp_path / "budget.db"
    with ledger(path).batch("run-one") as batch:
        rid = batch.reserve("attempt-one", 60, at=DAY)
        assert charges(path) == [("2026-11-08", 60, None)]
        batch.settle(rid, 20)
    with ledger(path).batch("run-two") as batch:
        batch.reserve("attempt-two", 80, at=DAY)
    with ledger(path).batch("run-three") as batch:
        with pytest.raises(BudgetError):
            batch.reserve("attempt-three", 1, at=DAY)
    assert charges(path) == [("2026-11-08", 60, 20), ("2026-11-08", 80, None)]


def test_utc_day_not_local_day_and_settlement_charges_original_day(tmp_path):
    path = tmp_path / "budget.db"
    kst = timezone(timedelta(hours=9))
    with ledger(path, daily=10, batch=30).batch("run") as batch:
        before = batch.reserve(
            "before", 10, at=datetime(2026, 11, 8, 8, 59, tzinfo=kst)
        )
        batch.reserve("after", 10, at=datetime(2026, 11, 8, 9, 0, tzinfo=kst))
        with pytest.raises(BudgetError):
            batch.reserve(
                "same-utc-day", 1, at=datetime(2026, 11, 8, 23, 0, tzinfo=kst)
            )
        batch.settle(before, 0)
    assert charges(path) == [("2026-11-07", 10, 0), ("2026-11-08", 10, None)]


def test_batch_limit_spans_utc_days_and_limits_are_independent(tmp_path):
    with ledger(tmp_path / "b.db", daily=100, batch=10).batch("run") as batch:
        batch.reserve("one", 6, at=DAY)
        with pytest.raises(BudgetError):
            batch.reserve("two", 5, at=DAY + timedelta(days=1))


@pytest.mark.parametrize("value", [0, -1, True, 1.0, "1", None, 2**63])
def test_bad_reservations_rejected(tmp_path, value):
    with ledger(tmp_path / "b.db").batch("run") as batch:
        with pytest.raises(BudgetError):
            batch.reserve("attempt", value, at=DAY)


def test_settlement_cannot_exceed_reserve_or_repeat_and_cannot_use_other_run(tmp_path):
    path = tmp_path / "b.db"
    with ledger(path).batch("one") as batch:
        rid = batch.reserve("attempt", 10, at=DAY)
        for actual in (11, -1, True, 1.0, None):
            with pytest.raises(BudgetError):
                batch.settle(rid, actual)
        batch.settle(rid, 0)
        with pytest.raises(BudgetError):
            batch.settle(rid, 0)
    with ledger(path).batch("two") as batch:
        with pytest.raises(BudgetError):
            batch.settle(rid, 0)
        with pytest.raises(BudgetError):
            batch.settle("unknown", 0)


def test_duplicate_run_and_attempt_rejected_even_after_settlement(tmp_path):
    path = tmp_path / "b.db"
    with ledger(path).batch("one") as batch:
        rid = batch.reserve("attempt", 10, at=DAY)
        batch.settle(rid, 0)
        with pytest.raises(BudgetError):
            batch.reserve("attempt", 1, at=DAY)
    with pytest.raises(BudgetError):
        with ledger(path).batch("one"):
            pass


def test_exception_keeps_reservation_and_releases_lock(tmp_path):
    path = tmp_path / "b.db"
    with pytest.raises(RuntimeError):
        with ledger(path).batch("one") as batch:
            batch.reserve("attempt", 80, at=DAY)
            raise RuntimeError("ambiguous provider failure")
    with ledger(path).batch("two") as batch:
        with pytest.raises(BudgetError):
            batch.reserve("other", 21, at=DAY)


def child(path, run, maximum, crash=False):
    program = """import os,sys
from pathlib import Path
from datetime import datetime, timezone
from scripts.news.translation_budget import BudgetLedger,BudgetBusy,BudgetError
try:
    with BudgetLedger(Path(sys.argv[1]),daily_limit_microusd=100,batch_limit_microusd=80).batch(sys.argv[2]) as batch:
        batch.reserve("attempt",int(sys.argv[3]),at=datetime(2026,11,8,tzinfo=timezone.utc))
        if sys.argv[4]=="crash": os._exit(7)
except BudgetBusy:
    sys.exit(21)
except BudgetError:
    sys.exit(22)
"""
    return subprocess.run(
        [
            sys.executable,
            "-c",
            program,
            str(path),
            run,
            str(maximum),
            "crash" if crash else "normal",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_separate_process_busy_then_atomic_daily_cap_after_release(tmp_path):
    path = tmp_path / "b.db"
    with ledger(path).batch("parent") as batch:
        batch.reserve("parent-attempt", 60, at=DAY)
        assert child(path, "child-busy", 50).returncode == 21
    assert child(path, "child-over-cap", 50).returncode == 22
    assert child(path, "child-fit", 40).returncode == 0
    assert sum(row[1] for row in charges(path)) == 100


def test_crashed_process_releases_lock_but_not_reserved_cost(tmp_path):
    path = tmp_path / "b.db"
    assert child(path, "crashed", 80, crash=True).returncode == 7
    assert charges(path) == [("2026-11-08", 80, None)]
    assert child(path, "remaining", 20).returncode == 0
    assert child(path, "over", 1).returncode == 22


def test_corrupt_db_fails_closed_and_does_not_replace_evidence(tmp_path):
    path = tmp_path / "b.db"
    raw = b"not a sqlite database; evidence"
    path.write_bytes(raw)
    with pytest.raises(BudgetError):
        with ledger(path).batch("one"):
            pass
    assert path.read_bytes() == raw


def test_naive_timestamp_and_invalid_ids_fail_without_reserving(tmp_path):
    path = tmp_path / "b.db"
    with ledger(path).batch("run") as batch:
        with pytest.raises(BudgetError):
            batch.reserve("attempt", 1, at=datetime(2026, 11, 8))
        for bad in ("", "../escape", "x" * 129):
            with pytest.raises(BudgetError):
                batch.reserve(bad, 1, at=DAY)
    assert charges(path) == []


def test_inactive_batch_cannot_charge_and_same_process_batch_is_busy(tmp_path):
    path = tmp_path / "b.db"
    context = ledger(path).batch("run")
    with pytest.raises(BudgetError):
        context.reserve("attempt", 1, at=DAY)
    with context:
        with pytest.raises(BudgetBusy):
            with ledger(path).batch("other"):
                pass
    with pytest.raises(BudgetError):
        context.reserve("after", 1, at=DAY)


def test_existing_schema_is_not_recreated_when_reservations_disappear(tmp_path):
    path = tmp_path / "b.db"
    with ledger(path).batch("original") as batch:
        batch.reserve("attempt", 80, at=DAY)
    with sqlite3.connect(path) as db:
        db.execute("DROP TABLE reservations")
    with pytest.raises(BudgetError):
        with ledger(path).batch("new"):
            pytest.fail("Missing cost evidence was silently repaired")
    with sqlite3.connect(path) as db:
        assert not db.execute(
            "SELECT name FROM sqlite_master WHERE name='reservations'"
        ).fetchall()
        assert db.execute("SELECT run_id FROM runs").fetchall() == [("original",)]


def test_zero_settlement_only_confirmed_actual_and_reserve_precedes_callable(tmp_path):
    path = tmp_path / "b.db"
    observations = []
    with ledger(path).batch("run") as batch:
        reservation = batch.reserve("attempt", 10, at=DAY)

        def fake_attempt():
            observations.extend(charges(path))
            return 0

        actual = fake_attempt()
        batch.settle(reservation, actual)
    assert observations == [("2026-11-08", 10, None)]
    assert charges(path) == [("2026-11-08", 10, 0)]


@pytest.mark.parametrize("daily,batch", [(1000, 80), (100, 800), (50, 80), (100, 40)])
def test_persisted_policy_cannot_be_silently_changed(tmp_path, daily, batch):
    path = tmp_path / "b.db"
    with ledger(path).batch("one") as batch_run:
        batch_run.reserve("attempt", 60, at=DAY)
    with pytest.raises(BudgetError, match="policy"):
        with ledger(path, daily=daily, batch=batch).batch("other"):
            pytest.fail("Mismatched budget policy accepted")
    assert charges(path) == [("2026-11-08", 60, None)]
    with ledger(path).batch("valid") as batch_run:
        batch_run.reserve("remaining", 40, at=DAY)


def test_hardlink_alias_rejected_and_symlink_alias_uses_same_lock(tmp_path):
    import os

    path = tmp_path / "b.db"
    with ledger(path).batch("one"):
        symlink = tmp_path / "symlink.db"
        symlink.symlink_to(path)
        with pytest.raises(BudgetBusy):
            with ledger(symlink).batch("alias"):
                pytest.fail("Alias bypassed batch lock")
    hardlink = tmp_path / "hardlink.db"
    os.link(path, hardlink)
    with pytest.raises(BudgetError, match="Hard-linked"):
        with ledger(hardlink).batch("hardlink"):
            pytest.fail("Hard-link alias accepted")
    assert path.stat().st_mode & 0o777 == 0o600
    assert path.with_name(path.name + ".lock").stat().st_mode & 0o777 == 0o600


@pytest.mark.parametrize("kind", ["zero", "sqlite-empty"])
def test_existing_empty_database_is_not_treated_as_new_budget(tmp_path, kind):
    path = tmp_path / "b.db"
    if kind == "zero":
        path.touch()
    else:
        with sqlite3.connect(path) as db:
            db.execute("VACUUM")
        assert path.stat().st_size > 0
    before = path.read_bytes()
    with pytest.raises(BudgetError, match="empty"):
        with ledger(path).batch("new"):
            pytest.fail("Existing empty database erased cost history")
    assert path.read_bytes() == before


def test_sigkill_releases_lock_without_refunding_reservation(tmp_path):
    import select

    path = tmp_path / "b.db"
    program = """import sys,time
from pathlib import Path
from datetime import datetime, timezone
from scripts.news.translation_budget import BudgetLedger
with BudgetLedger(Path(sys.argv[1]),daily_limit_microusd=100,batch_limit_microusd=80).batch("killed") as batch:
    batch.reserve("attempt",80,at=datetime(2026,11,8,tzinfo=timezone.utc))
    print("reserved",flush=True)
    time.sleep(60)
"""
    process = subprocess.Popen(
        [sys.executable, "-c", program, str(path)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None
        readable, _, _ = select.select([process.stdout], [], [], 5)
        assert readable and process.stdout.readline().strip() == "reserved"
        with pytest.raises(BudgetBusy):
            with ledger(path).batch("busy"):
                pytest.fail("Signalled worker did not retain exclusive batch lock")
        process.kill()
        process.wait(timeout=5)
        with ledger(path).batch("after-kill") as batch:
            batch.reserve("remaining", 20, at=DAY)
        assert charges(path) == [("2026-11-08", 80, None), ("2026-11-08", 20, None)]
    finally:
        if process.poll() is None:
            process.kill()
        process.communicate(timeout=5)
