"""API-free backup/restore rehearsal on a disposable synthetic ledger ONLY."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.news.translation_budget import BudgetError, BudgetLedger
from scripts.news.translation_production import ProductionBudgetLedger


class RehearsalError(ValueError):
    """Safe output configuration failure; no existing state may be overwritten."""


def _state(path: Path) -> tuple[str, dict[str, int]]:
    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        runs = db.execute("SELECT run_id,state FROM runs ORDER BY run_id").fetchall()
        reservations = db.execute(
            "SELECT reservation_id,run_id,attempt_id,utc_day,reserved_microusd,actual_microusd FROM reservations ORDER BY reservation_id"
        ).fetchall()
        policy = db.execute(
            "SELECT singleton,daily_limit_microusd,batch_limit_microusd FROM policy ORDER BY singleton"
        ).fetchall()
    fingerprint = hashlib.sha256(
        json.dumps([runs, reservations, policy], separators=(",", ":")).encode()
    ).hexdigest()
    return fingerprint, {
        "runs": len(runs),
        "reservations": len(reservations),
        "unsettled": sum(row[5] is None for row in reservations),
        "charged_microusd": sum(
            row[4] if row[5] is None else row[5] for row in reservations
        ),
    }


def _sha(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _manage(action: str, ledger: Path, snapshot: Path) -> None:
    command = [
        sys.executable,
        str(ROOT / "scripts/manage_translation_ledger.py"),
        action,
        "--ledger",
        str(ledger),
        "--snapshot-dir",
        str(snapshot),
        "--daily-limit-microusd",
        "1000",
        "--batch-limit-microusd",
        "800",
    ]
    if action == "restore":
        command += ["--operation-id", "offline-restore"]
    environment = os.environ.copy()
    for name in (
        "OPENAI_API_KEY",
        "CLAUDE_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "DEEPSEEK_API_KEY",
    ):
        environment.pop(name, None)
    result = subprocess.run(
        command, cwd=ROOT, env=environment, capture_output=True, text=True, timeout=30
    )
    if result.returncode or len(result.stdout) > 65_536:
        raise RehearsalError("Synthetic ledger CLI operation failed")
    payload = json.loads(result.stdout)
    expected = "backed_up" if action == "backup" else "restored"
    if (
        payload.get("action") != action
        or payload.get("result", {}).get("status") != expected
    ):
        raise RehearsalError("Synthetic ledger CLI outcome was not verified")


def _new_output(output: Path) -> Path:
    if not isinstance(output, Path) or output.is_symlink():
        raise RehearsalError("Explicit fresh output directory required")
    target = output.resolve()
    if target == ROOT or ROOT in target.parents:
        raise RehearsalError("Rehearsal output must be outside the checkout")
    if target.exists():
        raise RehearsalError("Rehearsal output already exists")
    missing = []
    parent = target.parent
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    for parent in reversed(missing):
        parent.mkdir(mode=0o700)
    target.mkdir(mode=0o700, exist_ok=False)
    return target


def run_rehearsal(output: Path) -> dict[str, Any]:
    """Use private disposable fixture state, exporting only a safe result report."""
    destination = _new_output(output)
    report: dict[str, Any] = {
        "mode": "offline_backup_restore",
        "status": "failed",
        "live_calls": 0,
        "counts": {"runs": 0, "reservations": 0, "unsettled": 0, "charged_microusd": 0},
        "maintenance_retained": False,
        "lock_inode_preserved": False,
        "snapshot_sha256_unchanged": False,
        "accounting_preserved": False,
    }
    try:
        with tempfile.TemporaryDirectory(
            prefix="techblog-backup-rehearsal-"
        ) as temporary:
            base = Path(temporary).resolve()
            path, snapshot = base / "budget.sqlite", base / "snapshot"
            with BudgetLedger(
                path, daily_limit_microusd=1000, batch_limit_microusd=800
            ).batch("offline-fixture") as batch:
                now = datetime.now(timezone.utc)
                confirmed = batch.reserve("confirmed", 700, at=now)
                batch.settle(confirmed, 200)
                batch.reserve("pending", 300, at=now)
            before, counts = _state(path)
            report["counts"] = counts
            expected_counts = {
                "runs": 1,
                "reservations": 2,
                "unsettled": 1,
                "charged_microusd": 500,
            }
            if counts != expected_counts:
                raise RehearsalError("Synthetic accounting fixture is inconsistent")
            lock = path.with_name(path.name + ".lock")
            info = lock.stat()
            lock_identity = info.st_dev, info.st_ino
            _manage("backup", path, snapshot)
            frozen = {
                name: _sha(snapshot / name)
                for name in ("budget.sqlite", "manifest.json")
            }
            guard = ProductionBudgetLedger(
                path, daily_limit_microusd=1000, batch_limit_microusd=800
            )
            guard.enter_maintenance("offline-restore", "restore")
            marker = guard.maintenance_path.read_bytes()
            _manage("restore", path, snapshot)
            after, after_counts = _state(path)
            report["accounting_preserved"] = before == after and counts == after_counts
            info = lock.stat()
            report["lock_inode_preserved"] = lock_identity == (info.st_dev, info.st_ino)
            report["snapshot_sha256_unchanged"] = frozen == {
                name: _sha(snapshot / name) for name in frozen
            }
            try:
                guard.check_ready()
            except BudgetError:
                report["maintenance_retained"] = (
                    guard.maintenance_path.read_bytes() == marker
                )
            else:
                raise RehearsalError("Restored fixture unexpectedly resumed admission")
            if not all(
                report[field]
                for field in (
                    "accounting_preserved",
                    "lock_inode_preserved",
                    "snapshot_sha256_unchanged",
                    "maintenance_retained",
                )
            ):
                raise RehearsalError("Synthetic recovery invariants failed")
        # All DB/snapshot/quarantine/marker data is gone before report publication.
        report["status"] = "validated"
    except Exception:
        # Never export source paths, child stdout/stderr, or raw exceptions.
        report["status"] = "failed"
    with (destination / "report.json").open("x", encoding="utf-8") as file:
        os.fchmod(file.fileno(), 0o600)
        json.dump(report, file, sort_keys=True, indent=2)
        file.flush()
        os.fsync(file.fileno())
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        report = run_rehearsal(arguments.output)
    except (RehearsalError, OSError):
        print(
            "Offline rehearsal output refused; no production state was selected.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "validated" else 1


if __name__ == "__main__":
    raise SystemExit(main())
