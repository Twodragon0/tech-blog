"""Existing-only local production budget admission and durable maintenance.

No bootstrap, API calls, deployment, credentials, or automatic date-based clear.
All participating processes must share one local filesystem and canonical lock.
Maintenance controls are nonblocking: they cannot interrupt an active batch.
"""

from __future__ import annotations

import fcntl
import json
import os
import sqlite3
import stat
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from typing import BinaryIO

from scripts.news.translation_budget import (
    BudgetBusy,
    BudgetError,
    BudgetLedger,
    _existing_identity,
    _identity,
    _validate_existing_db,
)

_REASONS = frozenset(
    {"restore", "policy_migration", "storage_incident", "planned_maintenance"}
)


def _unique_fields(pairs: list[tuple[str, object]]) -> dict[str, object]:
    fields: dict[str, object] = {}
    for name, value in pairs:
        if name in fields:
            raise BudgetError("Duplicate maintenance marker field")
        fields[name] = value
    return fields


class ProductionBudgetLedger(BudgetLedger):
    """Never create missing DB/lock; require explicit maintenance clearance."""

    def __init__(
        self, path: Path, *, daily_limit_microusd: int, batch_limit_microusd: int
    ) -> None:
        super().__init__(
            path,
            daily_limit_microusd=daily_limit_microusd,
            batch_limit_microusd=batch_limit_microusd,
            require_existing=True,
        )
        self.maintenance_path = self.path.with_name(
            self.path.name + ".maintenance.json"
        )

    def _before_open_locked(self) -> None:
        try:
            self.maintenance_path.lstat()
        except FileNotFoundError:
            return
        except OSError:
            raise BudgetError("Maintenance state cannot be inspected") from None
        raise BudgetError("Production translation is in maintenance")

    @staticmethod
    def _lock_identity(held: BinaryIO, path: Path) -> tuple[int, int]:
        descriptor = os.fstat(held.fileno())
        current = path.lstat()
        if not stat.S_ISREG(current.st_mode) or (
            descriptor.st_dev,
            descriptor.st_ino,
        ) != (current.st_dev, current.st_ino):
            raise BudgetError("Existing regular budget lock required")
        return current.st_dev, current.st_ino

    @contextmanager
    def _locked(self) -> Iterator[None]:
        lock_path = self.path.with_name(self.path.name + ".lock")
        try:
            descriptor = os.open(lock_path, os.O_RDWR | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "r+b") as held:
                self._lock_identity(held, lock_path)
                try:
                    fcntl.flock(held.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise BudgetBusy("Another budget batch is active") from None
                self._lock_identity(held, lock_path)
                yield
        except BudgetError:
            raise
        except (OSError, sqlite3.Error, UnicodeError, ValueError):
            raise BudgetError("Production budget control failed") from None

    def _validate_locked(self) -> None:
        before = _existing_identity(self.path)
        with closing(
            sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, timeout=0)
        ) as db:
            _validate_existing_db(
                db, self.daily_limit_microusd, self.batch_limit_microusd
            )
        if _existing_identity(self.path) != before:
            raise BudgetError("Production budget storage changed during validation")

    def check_ready(self) -> None:
        """Read-only admission check under the existing flock, without run history."""
        with self._locked():
            self._before_open_locked()
            self._validate_locked()

    def _sync_directory(self) -> None:
        descriptor = os.open(self.path.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _publish_marker(self, raw: bytes) -> None:
        descriptor = os.open(
            self.maintenance_path,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
        )
        with os.fdopen(descriptor, "wb") as marker:
            marker.write(raw)
            marker.flush()
            os.fsync(marker.fileno())
        self._sync_directory()

    def enter_maintenance(self, operation_id: str, reason_code: str) -> None:
        """Freeze even missing/corrupt DB incidents; never overwrite a marker."""
        operation = _identity(operation_id)
        if not isinstance(reason_code, str) or reason_code not in _REASONS:
            raise BudgetError("Unsupported maintenance reason code")
        raw = json.dumps(
            {"version": 1, "operation_id": operation, "reason_code": reason_code},
            sort_keys=True,
        ).encode()
        with self._locked():
            self._publish_marker(raw)

    def _read_marker(self) -> tuple[bytes, tuple[int, int], dict[str, object]]:
        info = self.maintenance_path.lstat()
        if (
            not stat.S_ISREG(info.st_mode)
            or not info.st_mode & 0o444
            or not 0 < info.st_size <= 2048
        ):
            raise BudgetError("Maintenance marker is not a readable regular record")
        descriptor = os.open(self.maintenance_path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(descriptor, "rb") as marker:
            actual = os.fstat(marker.fileno())
            if (actual.st_dev, actual.st_ino) != (info.st_dev, info.st_ino):
                raise BudgetError("Maintenance marker changed while reading")
            raw = marker.read(2049)
        data = json.loads(raw, object_pairs_hook=_unique_fields)
        if not isinstance(data, dict) or set(data) != {
            "version",
            "operation_id",
            "reason_code",
        }:
            raise BudgetError("Invalid maintenance marker schema")
        if (
            type(data["version"]) is not int
            or data["version"] != 1
            or not isinstance(data["reason_code"], str)
            or data["reason_code"] not in _REASONS
        ):
            raise BudgetError("Invalid maintenance marker policy")
        _identity(data["operation_id"])
        return raw, (info.st_dev, info.st_ino), data

    def clear_maintenance(self, operation_id: str) -> None:
        """Clear one valid matching operation only after healthy RO validation."""
        operation = _identity(operation_id)
        with self._locked():
            raw, identity, data = self._read_marker()
            if data["operation_id"] != operation:
                raise BudgetError("Maintenance operation does not match")
            self._validate_locked()
            current = self.maintenance_path.lstat()
            if (current.st_dev, current.st_ino) != identity or not stat.S_ISREG(
                current.st_mode
            ):
                raise BudgetError("Maintenance marker changed before clearance")
            self.maintenance_path.unlink()
            try:
                self._sync_directory()
            except OSError:
                # Try to re-block a failed clearance. If storage also prevents
                # re-publication, callers need out-of-band containment; an
                # absent marker cannot prove successful durable clearance.
                try:
                    self._publish_marker(raw)
                except OSError:
                    pass
                raise BudgetError("Unable to persist maintenance clearance") from None
