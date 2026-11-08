"""Persistent integer micro-USD reservations on ONE shared local filesystem.

POSIX flock serializes whole batches across local Linux/macOS processes. This
is not a distributed ledger for separate Actions runners. Only confirmed usage
may settle a reservation; exceptions, timeouts, and crashes never auto-refund.
Callers provide trusted aware timestamps; settlement stays on reservation's UTC
calendar day. Caps are persisted and mismatched policies fail, requiring explicit
coordinated migration rather than resetting or silently increasing the budget. No credentials, source content, API calls, or dependencies here.
"""

from __future__ import annotations

import errno
import fcntl
import os
import re
import sqlite3
import stat
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from types import TracebackType
from typing import BinaryIO, Literal

_MAX_INTEGER = 2**63 - 1
_CHARGED = (
    "CASE WHEN actual_microusd IS NULL THEN reserved_microusd ELSE actual_microusd END"
)


class BudgetError(ValueError):
    """Safe budget/configuration/storage failure; no call is authorized."""


class BudgetBusy(BudgetError):
    """Another batch owns the local ledger lock; no waiting or API calls."""


def _integer(value: object, *, allow_zero: bool = False) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not (0 if allow_zero else 1) <= value <= _MAX_INTEGER
    ):
        raise BudgetError("Budget values must be bounded integer micro-USD")
    return value


def _identity(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}", value
    ):
        raise BudgetError("Invalid budget operation identity")
    return value


def _existing_identity(path: Path) -> tuple[int, int]:
    try:
        info = path.stat()
    except OSError:
        raise BudgetError("Existing budget storage is unavailable") from None
    if not stat.S_ISREG(info.st_mode) or info.st_size == 0 or info.st_nlink != 1:
        raise BudgetError("Existing budget storage is not a nonempty single-link file")
    return info.st_dev, info.st_ino


def _validate_existing_db(
    db: sqlite3.Connection, daily_limit_microusd: int, batch_limit_microusd: int
) -> None:
    """Shared read-only validation; never creates schema or records a run."""
    if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
        raise BudgetError("Budget storage integrity check failed")
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    if db.execute("PRAGMA user_version").fetchone() != (1,) or tables != {
        "runs",
        "reservations",
        "policy",
    }:
        raise BudgetError("Unsupported or incomplete budget storage schema")
    if db.execute("PRAGMA journal_mode").fetchone() != ("delete",):
        raise BudgetError("Unexpected budget journal mode")
    policy = db.execute(
        "SELECT daily_limit_microusd,batch_limit_microusd FROM policy WHERE singleton=1"
    ).fetchall()
    if policy != [(daily_limit_microusd, batch_limit_microusd)]:
        raise BudgetError("Persisted budget policy differs from requested limits")
    # Never recreate missing tables or columns on an existing version: that
    # could silently discard the only evidence of previously reserved cost.
    if [row[1] for row in db.execute("PRAGMA table_info(reservations)")] != [
        "reservation_id",
        "run_id",
        "attempt_id",
        "utc_day",
        "reserved_microusd",
        "actual_microusd",
    ]:
        raise BudgetError("Invalid budget reservation schema")
    if db.execute("PRAGMA foreign_key_check").fetchall():
        raise BudgetError("Budget storage reference check failed")


class BudgetLedger:
    """Persist charges, applying the explicit policy supplied by each caller."""

    def __init__(
        self,
        path: Path,
        *,
        daily_limit_microusd: int,
        batch_limit_microusd: int,
        require_existing: bool = False,
    ) -> None:
        if not isinstance(path, Path):
            raise BudgetError("Explicit ledger Path required")
        self.daily_limit_microusd = _integer(daily_limit_microusd)
        self.batch_limit_microusd = _integer(batch_limit_microusd)
        self.path = path.resolve()
        if not isinstance(require_existing, bool):
            raise BudgetError("Existing-only policy must be boolean")
        self._require_existing = require_existing

    def _before_open_locked(self) -> None:
        """Extension point for production admission while holding the flock."""

    def batch(self, run_id: str) -> BudgetBatch:
        """Create one context; run IDs are single-use, attempts unique per run."""
        return BudgetBatch(self, _identity(run_id))


class BudgetBatch:
    """Hold a nonblocking process lock from context entry through exit."""

    def __init__(self, ledger: BudgetLedger, run_id: str) -> None:
        self._ledger = ledger
        self._run_id = run_id
        self._db: sqlite3.Connection | None = None
        self._lock: BinaryIO | None = None
        self._owner_pid = os.getpid()
        self._created_storage = False
        self._storage_identity: tuple[int, int] | None = None

    def _connection(self) -> sqlite3.Connection:
        if self._db is None or self._owner_pid != os.getpid():
            raise BudgetError("Budget batch is inactive or belongs to another process")
        if (
            self._ledger._require_existing
            and _existing_identity(self._ledger.path) != self._storage_identity
        ):
            raise BudgetError("Production budget storage was removed or replaced")
        return self._db

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        db = self._connection()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except sqlite3.Error:
            if db.in_transaction:
                db.rollback()
            raise BudgetError("Budget storage transaction failed") from None
        except BaseException:
            if db.in_transaction:
                db.rollback()
            raise

    def _initialize(self) -> None:
        db = self._connection()
        if self._ledger._require_existing:
            _validate_existing_db(
                db, self._ledger.daily_limit_microusd, self._ledger.batch_limit_microusd
            )
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("PRAGMA synchronous=FULL")
            return
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA journal_mode=DELETE")
        db.execute("PRAGMA synchronous=FULL")
        if db.execute("PRAGMA quick_check").fetchall() != [("ok",)]:
            raise BudgetError("Budget storage integrity check failed")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        tables = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
        }
        if version == 0 and not tables:
            if not self._created_storage:
                raise BudgetError(
                    "Existing empty budget storage cannot be initialized automatically"
                )
            with self._transaction() as transaction:
                transaction.execute(
                    "CREATE TABLE runs (run_id TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('open','closed')))"
                )
                transaction.execute("""CREATE TABLE reservations (
                    reservation_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    attempt_id TEXT NOT NULL,
                    utc_day TEXT NOT NULL,
                    reserved_microusd INTEGER NOT NULL CHECK(reserved_microusd > 0),
                    actual_microusd INTEGER CHECK(actual_microusd >= 0 AND actual_microusd <= reserved_microusd),
                    UNIQUE(run_id, attempt_id)
                )""")
                transaction.execute(
                    "CREATE TABLE policy (singleton INTEGER PRIMARY KEY CHECK(singleton=1), "
                    "daily_limit_microusd INTEGER NOT NULL CHECK(daily_limit_microusd>0), "
                    "batch_limit_microusd INTEGER NOT NULL CHECK(batch_limit_microusd>0))"
                )
                transaction.execute(
                    "INSERT INTO policy VALUES (1,?,?)",
                    (
                        self._ledger.daily_limit_microusd,
                        self._ledger.batch_limit_microusd,
                    ),
                )
                transaction.execute("PRAGMA user_version=1")
        elif version != 1 or tables != {"runs", "reservations", "policy"}:
            raise BudgetError("Unsupported or incomplete budget storage schema")
        _validate_existing_db(
            db, self._ledger.daily_limit_microusd, self._ledger.batch_limit_microusd
        )

    def __enter__(self) -> BudgetBatch:
        if self._lock is not None or self._db is not None:
            raise BudgetError("Budget batch is already active")
        try:
            lock_path = self._ledger.path.with_name(self._ledger.path.name + ".lock")
            if self._ledger._require_existing:
                descriptor = os.open(lock_path, os.O_RDWR | os.O_NOFOLLOW)
                self._lock = os.fdopen(descriptor, "r+b")
                info = os.fstat(self._lock.fileno())
                linked = lock_path.lstat()
                if not stat.S_ISREG(info.st_mode) or (info.st_dev, info.st_ino) != (
                    linked.st_dev,
                    linked.st_ino,
                ):
                    raise BudgetError("Existing regular budget lock required")
            else:
                self._ledger.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                self._lock = lock_path.open("a+b")
                os.fchmod(self._lock.fileno(), 0o600)
            try:
                fcntl.flock(self._lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                if error.errno in (errno.EACCES, errno.EAGAIN):
                    raise BudgetBusy("Another budget batch is active") from None
                raise
            if self._ledger._require_existing:
                held, current = os.fstat(self._lock.fileno()), lock_path.lstat()
                if not stat.S_ISREG(current.st_mode) or (held.st_dev, held.st_ino) != (
                    current.st_dev,
                    current.st_ino,
                ):
                    raise BudgetError("Budget lock changed during acquisition")
            self._ledger._before_open_locked()
            if self._ledger._require_existing:
                self._storage_identity = _existing_identity(self._ledger.path)
                self._db = sqlite3.connect(
                    self._ledger.path.as_uri() + "?mode=rw",
                    uri=True,
                    timeout=0,
                    isolation_level=None,
                )
            else:
                if self._ledger.path.exists() and self._ledger.path.stat().st_nlink > 1:
                    raise BudgetError("Hard-linked budget storage is not supported")
                try:
                    descriptor = os.open(
                        self._ledger.path, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600
                    )
                except FileExistsError:
                    self._created_storage = False
                    if self._ledger.path.stat().st_size == 0:
                        raise BudgetError(
                            "Existing empty budget storage cannot be initialized automatically"
                        )
                else:
                    os.close(descriptor)
                    self._created_storage = True
                if self._ledger.path.stat().st_nlink > 1:
                    raise BudgetError("Hard-linked budget storage is not supported")
                self._ledger.path.chmod(0o600)
                self._db = sqlite3.connect(
                    self._ledger.path, timeout=0, isolation_level=None
                )
            self._initialize()
            with self._transaction() as db:
                db.execute(
                    "INSERT INTO runs(run_id,state) VALUES (?, 'open')", (self._run_id,)
                )
            return self
        except BudgetError:
            self._close()
            raise
        except (OSError, sqlite3.Error):
            self._close()
            raise BudgetError("Unable to open budget storage") from None

    def _close(self) -> None:
        if self._db is not None:
            self._db.close()
            self._db = None
        if self._lock is not None:
            # Do not unlink the lock file: a new inode would bypass flock.
            self._lock.close()
            self._lock = None

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        try:
            with self._transaction() as db:
                db.execute(
                    "UPDATE runs SET state='closed' WHERE run_id=?", (self._run_id,)
                )
        except BudgetError:
            if exc_type is None:
                raise
        finally:
            self._close()
        return False

    def reserve(self, attempt_id: str, maximum_microusd: int, *, at: datetime) -> str:
        """Atomically reserve worst-case cost BEFORE authorizing an attempt."""
        attempt = _identity(attempt_id)
        maximum = _integer(maximum_microusd)
        if not isinstance(at, datetime) or at.utcoffset() is None:
            raise BudgetError(
                "Budget reservation requires an aware UTC-convertible timestamp"
            )
        day = at.astimezone(timezone.utc).date().isoformat()
        reservation = uuid.uuid4().hex
        with self._transaction() as db:
            daily = db.execute(
                f"SELECT COALESCE(SUM({_CHARGED}),0) FROM reservations WHERE utc_day=?",
                (day,),
            ).fetchone()[0]
            batch = db.execute(
                f"SELECT COALESCE(SUM({_CHARGED}),0) FROM reservations WHERE run_id=?",
                (self._run_id,),
            ).fetchone()[0]
            if maximum > self._ledger.daily_limit_microusd - daily:
                raise BudgetError("Daily translation budget exceeded")
            if maximum > self._ledger.batch_limit_microusd - batch:
                raise BudgetError("Batch translation budget exceeded")
            db.execute(
                "INSERT INTO reservations VALUES (?,?,?,?,?,NULL)",
                (reservation, self._run_id, attempt, day, maximum),
            )
        return reservation

    def settle(self, reservation_id: str, actual_microusd: int) -> None:
        """Replace only this run's reservation with confirmed actual cost once."""
        reservation = _identity(reservation_id)
        actual = _integer(actual_microusd, allow_zero=True)
        with self._transaction() as db:
            row = db.execute(
                "SELECT reserved_microusd,actual_microusd FROM reservations WHERE reservation_id=? AND run_id=?",
                (reservation, self._run_id),
            ).fetchone()
            if row is None or row[1] is not None:
                raise BudgetError("Unknown or already settled budget reservation")
            if actual > row[0]:
                raise BudgetError("Actual cost exceeds reserved maximum")
            db.execute(
                "UPDATE reservations SET actual_microusd=? WHERE reservation_id=?",
                (actual, reservation),
            )
