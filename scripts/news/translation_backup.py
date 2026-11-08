"""Local, lock-coordinated snapshots and EXACT-accounting-state restoration.

No bootstrap, API, history mutation, cost reconciliation, or maintenance clear.
All writers/clients must honor the same existing flock on one local filesystem.
Missing/corrupt current state requires a separately reviewed recovery procedure.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import uuid
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from scripts.news.translation_budget import (
    BudgetError,
    _existing_identity,
    _identity,
    _validate_existing_db,
)
from scripts.news.translation_production import ProductionBudgetLedger

_TABLES = {
    "runs": "CREATE TABLE runs (run_id TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('open','closed')))",
    "reservations": "CREATE TABLE reservations (reservation_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(run_id), attempt_id TEXT NOT NULL, utc_day TEXT NOT NULL, reserved_microusd INTEGER NOT NULL CHECK(reserved_microusd > 0), actual_microusd INTEGER CHECK(actual_microusd >= 0 AND actual_microusd <= reserved_microusd), UNIQUE(run_id, attempt_id))",
    "policy": "CREATE TABLE policy (singleton INTEGER PRIMARY KEY CHECK(singleton=1), daily_limit_microusd INTEGER NOT NULL CHECK(daily_limit_microusd>0), batch_limit_microusd INTEGER NOT NULL CHECK(batch_limit_microusd>0))",
}
_FIELDS = {
    "version",
    "schema_version",
    "policy",
    "created_at_utc",
    "sha256",
    "bytes",
    "counts",
    "accounting_fingerprint",
}


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for name, value in pairs:
        if name in result:
            raise BudgetError("Duplicate snapshot manifest field")
        result[name] = value
    return result


def _regular(path: Path, *, nonempty: bool = True) -> None:
    info = path.lstat()
    if (
        not stat.S_ISREG(info.st_mode)
        or info.st_nlink != 1
        or (nonempty and info.st_size == 0)
    ):
        raise BudgetError("Snapshot files must be regular single-link files")


def _sync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _sha(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _copy(source: Path, target: Path) -> None:
    with source.open("rb") as original, target.open("xb") as saved:
        target.chmod(0o600)
        shutil.copyfileobj(original, saved)
        saved.flush()
        os.fsync(saved.fileno())


class LedgerBackup:
    def __init__(self, ledger: ProductionBudgetLedger) -> None:
        if not isinstance(ledger, ProductionBudgetLedger):
            raise BudgetError("Production ledger admission is required")
        self.ledger = ledger

    def _directory(self, requested: Path, *, new: bool = False) -> Path:
        if not isinstance(requested, Path) or requested.is_symlink():
            raise BudgetError("Explicit non-symlink snapshot directory required")
        path = requested.resolve()
        protected = (
            self.ledger.path,
            self.ledger.path.with_name(self.ledger.path.name + ".lock"),
            self.ledger.maintenance_path,
        )
        if any(
            path == item or path in item.parents or item in path.parents
            for item in protected
        ):
            raise BudgetError("Snapshot path overlaps active ledger state")
        if new:
            for parent in path.parents:
                if os.path.lexists(parent / "manifest.json"):
                    raise BudgetError(
                        "Snapshot directories cannot be nested in completed artifacts"
                    )
            missing = []
            parent = path.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            for parent in reversed(missing):
                parent.mkdir(mode=0o700)
                _sync_dir(parent.parent)
            path.mkdir(mode=0o700, exist_ok=False)
            _sync_dir(path.parent)
        elif not path.is_dir():
            raise BudgetError("Snapshot directory is missing")
        return path

    def _audit(self, path: Path) -> dict[str, Any]:
        _regular(path)
        before = _existing_identity(path)
        with closing(
            sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0)
        ) as db:
            _validate_existing_db(
                db, self.ledger.daily_limit_microusd, self.ledger.batch_limit_microusd
            )
            if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise BudgetError("Snapshot integrity validation failed")
            schema = db.execute(
                "SELECT type,name,sql FROM sqlite_master WHERE name NOT LIKE 'sqlite_%'"
            ).fetchall()

            def normalize(value: str) -> str:
                return re.sub(r"\s+", "", value)

            if len(schema) != 3 or {
                name: normalize(sql) for kind, name, sql in schema if kind == "table"
            } != {name: normalize(sql) for name, sql in _TABLES.items()}:
                raise BudgetError(
                    "Snapshot schema differs from the approved ledger schema"
                )
            runs = db.execute(
                "SELECT run_id,state FROM runs ORDER BY run_id"
            ).fetchall()
            reservations = db.execute(
                "SELECT reservation_id,run_id,attempt_id,utc_day,reserved_microusd,actual_microusd FROM reservations ORDER BY reservation_id"
            ).fetchall()
            policy_rows = db.execute(
                "SELECT singleton,daily_limit_microusd,batch_limit_microusd FROM policy ORDER BY singleton"
            ).fetchall()
        if _existing_identity(path) != before:
            raise BudgetError("Ledger file changed during audit")
        state = {"runs": runs, "reservations": reservations, "policy": policy_rows}
        return {
            "policy": {
                "daily_limit_microusd": self.ledger.daily_limit_microusd,
                "batch_limit_microusd": self.ledger.batch_limit_microusd,
            },
            "counts": {
                "runs": len(runs),
                "reservations": len(reservations),
                "unsettled": sum(row[5] is None for row in reservations),
                "charged_microusd": sum(
                    row[4] if row[5] is None else row[5] for row in reservations
                ),
            },
            "accounting_fingerprint": hashlib.sha256(
                _canonical_json(state)
            ).hexdigest(),
        }

    @staticmethod
    def _write_manifest(path: Path, data: dict) -> None:
        with path.open("x", encoding="utf-8") as file:
            path.chmod(0o600)
            json.dump(data, file, sort_keys=True, indent=2)
            file.flush()
            os.fsync(file.fileno())
        _sync_dir(path.parent)

    def _verify(self, snapshot: Path) -> tuple[dict[str, Any], dict[str, Any]]:
        manifest_path, database = snapshot / "manifest.json", snapshot / "budget.sqlite"
        _regular(manifest_path)
        _regular(database)
        if manifest_path.stat().st_size > 16_384:
            raise BudgetError("Snapshot manifest exceeds size limit")
        manifest = json.loads(manifest_path.read_bytes(), object_pairs_hook=_unique)
        if not isinstance(manifest, dict) or set(manifest) != _FIELDS:
            raise BudgetError("Invalid snapshot manifest schema")
        if (
            type(manifest["version"]) is not int
            or manifest["version"] != 1
            or type(manifest["schema_version"]) is not int
            or manifest["schema_version"] != 1
        ):
            raise BudgetError("Unsupported snapshot manifest version")
        for field in ("sha256", "accounting_fingerprint"):
            if not isinstance(manifest[field], str) or not re.fullmatch(
                r"[0-9a-f]{64}", manifest[field]
            ):
                raise BudgetError("Invalid snapshot fingerprint")
        if (
            type(manifest["bytes"]) is not int
            or manifest["bytes"] <= 0
            or database.stat().st_size != manifest["bytes"]
            or _sha(database) != manifest["sha256"]
        ):
            raise BudgetError("Snapshot checksum or size mismatch")
        created = datetime.fromisoformat(manifest["created_at_utc"])
        if created.utcoffset() != timedelta(0):
            raise BudgetError("Snapshot timestamp must be UTC aware")
        audit = self._audit(database)
        for field in ("policy", "counts"):
            if (
                not isinstance(manifest[field], dict)
                or set(manifest[field]) != set(audit[field])
                or any(
                    type(value) is not int or value < 0
                    for value in manifest[field].values()
                )
            ):
                raise BudgetError("Invalid snapshot accounting metadata")
        if any(manifest[field] != audit[field] for field in audit):
            raise BudgetError("Snapshot accounting metadata does not match DB")
        return manifest, audit

    def backup(self, snapshot_dir: Path) -> dict:
        """Make a new consistent private snapshot; completion manifest is last."""
        try:
            with self.ledger._locked():
                original = self._audit(self.ledger.path)
                snapshot = self._directory(snapshot_dir, new=True)
                database = snapshot / "budget.sqlite"
                descriptor = os.open(
                    database, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
                os.close(descriptor)
                with (
                    closing(
                        sqlite3.connect(
                            self.ledger.path.as_uri() + "?mode=ro", uri=True, timeout=0
                        )
                    ) as source,
                    closing(
                        sqlite3.connect(database.as_uri() + "?mode=rw", uri=True)
                    ) as target,
                ):
                    target.execute("PRAGMA synchronous=FULL")
                    source.backup(target)
                if self._audit(database) != original:
                    raise BudgetError("Snapshot differs from locked current ledger")
                with database.open("rb") as file:
                    os.fsync(file.fileno())
                manifest = {
                    "version": 1,
                    "schema_version": 1,
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "sha256": _sha(database),
                    "bytes": database.stat().st_size,
                    **original,
                }
                self._write_manifest(snapshot / "manifest.json", manifest)
                self._verify(snapshot)
                return {
                    "status": "backed_up",
                    "snapshot_dir": str(snapshot),
                    **manifest,
                }
        except BudgetError:
            raise
        except (OSError, sqlite3.Error, ValueError, TypeError):
            raise BudgetError(
                "Ledger backup failed; partial artifacts require review"
            ) from None

    def restore(self, snapshot_dir: Path, operation_id: str) -> dict:
        """Restore ONLY identical current accounting; never clear maintenance."""
        operation = _identity(operation_id)
        try:
            with self.ledger._locked():
                marker_raw, marker_identity, marker = self.ledger._read_marker()
                _regular(self.ledger.maintenance_path)
                if marker["operation_id"] != operation:
                    raise BudgetError("Restore maintenance operation does not match")
                snapshot = self._directory(snapshot_dir)
                manifest, saved = self._verify(snapshot)
                current = self._audit(self.ledger.path)
                if current != saved:
                    raise BudgetError(
                        "Snapshot does not preserve exact current accounting"
                    )
                staged = (
                    self.ledger.path.parent
                    / f".budget-restore-{uuid.uuid4().hex}.sqlite"
                )
                _copy(snapshot / "budget.sqlite", staged)
                if self._audit(staged) != current or _sha(staged) != manifest["sha256"]:
                    raise BudgetError("Staged restore validation failed")
                quarantine = (
                    self.ledger.path.parent / f".budget-quarantine-{uuid.uuid4().hex}"
                )
                quarantine.mkdir(mode=0o700)
                _copy(self.ledger.path, quarantine / self.ledger.path.name)
                sidecars = []
                for suffix in ("-journal", "-wal", "-shm"):
                    sidecar = self.ledger.path.with_name(self.ledger.path.name + suffix)
                    if os.path.lexists(sidecar):
                        _regular(sidecar, nonempty=False)
                        _copy(sidecar, quarantine / sidecar.name)
                        sidecars.append(sidecar)
                self._write_manifest(
                    quarantine / "manifest.json",
                    {
                        "version": 1,
                        "accounting_fingerprint": current["accounting_fingerprint"],
                        "sha256": _sha(self.ledger.path),
                        "counts": current["counts"],
                        "sidecars": [file.name for file in sidecars],
                    },
                )
                _sync_dir(self.ledger.path.parent)
                if (
                    self.ledger._read_marker()[:2] != (marker_raw, marker_identity)
                    or self._audit(self.ledger.path) != current
                ):
                    raise BudgetError("Current state changed before restore")
                for sidecar in sidecars:
                    sidecar.unlink()
                os.replace(staged, self.ledger.path)
                self.ledger.path.chmod(0o600)
                _sync_dir(self.ledger.path.parent)
                if (
                    self._audit(self.ledger.path) != current
                    or _sha(snapshot / "budget.sqlite") != manifest["sha256"]
                ):
                    raise BudgetError(
                        "Restored ledger needs review; maintenance retained"
                    )
                return {
                    "status": "restored",
                    "snapshot_dir": str(snapshot),
                    "quarantine_dir": str(quarantine),
                    "accounting_fingerprint": current["accounting_fingerprint"],
                    "counts": current["counts"],
                }
        except BudgetError:
            raise
        except (OSError, sqlite3.Error, ValueError, TypeError):
            raise BudgetError(
                "Ledger restore failed; maintenance and artifacts require review"
            ) from None
