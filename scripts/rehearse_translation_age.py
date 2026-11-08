"""Native age fixture rehearsal using explicit tools and temporary keys ONLY.

No source/key/recipient selection, downloads, network, production paths, or key
installation. Caller must establish executable trust separately; version output
is not a signature or supply-chain verification. All fixture data is disposable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.news.translation_backup import LedgerBackup
from scripts.news.translation_budget import BudgetLedger
from scripts.news.translation_production import ProductionBudgetLedger

_FLAGS = (
    "primary_roundtrip",
    "escrow_roundtrip",
    "wrong_identity_rejected",
    "tampered_ciphertext_rejected",
    "plaintext_preserved",
    "snapshot_accounting_preserved",
)
_ENTRIES = {"budget.sqlite", "manifest.json"}


class AgeRehearsalError(ValueError):
    """Safe configuration/rehearsal failure; never includes tool output or keys."""


def _environment() -> dict[str, str]:
    environment = os.environ.copy()
    for name in (
        "OPENAI_API_KEY",
        "CLAUDE_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
        "DEEPSEEK_API_KEY",
    ):
        environment.pop(name, None)
    return environment


def _capture(command: list[str]) -> bytes:
    result = subprocess.run(
        command, env=_environment(), capture_output=True, timeout=30
    )
    if result.returncode or len(result.stdout) > 4096:
        raise AgeRehearsalError("Age tool operation failed")
    return result.stdout


def _to_file(command: list[str], output: Path) -> int:
    with output.open("xb") as saved:
        os.fchmod(saved.fileno(), 0o600)
        result = subprocess.run(
            command,
            env=_environment(),
            stdout=saved,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    return result.returncode


def _sha(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def _binary(path: Path) -> str:
    if not isinstance(path, Path) or not path.is_file() or not os.access(path, os.X_OK):
        raise AgeRehearsalError("Explicit executable age tool paths required")
    return str(path.resolve())


def _identity(keygen: str, path: Path) -> str:
    _capture([keygen, "-o", str(path)])
    if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o777 != 0o600:
        raise AgeRehearsalError("Temporary native identity is not private")
    recipient = _capture([keygen, "-y", str(path)]).decode("ascii").strip()
    if not re.fullmatch(r"age1[0-9a-z]{50,100}", recipient):
        raise AgeRehearsalError("Expected one native age recipient")
    return recipient


def _archive(snapshot: Path, archive: Path) -> None:
    with archive.open("xb") as output:
        os.fchmod(output.fileno(), 0o600)
        with tarfile.open(fileobj=output, mode="w") as bundle:
            for name in sorted(_ENTRIES):
                source = snapshot / name
                member = bundle.gettarinfo(str(source), arcname=name)
                if not member.isfile():
                    raise AgeRehearsalError("Snapshot archive requires regular files")
                with source.open("rb") as file:
                    bundle.addfile(member, file)


def _unpack(archive: Path, destination: Path) -> None:
    destination.mkdir(mode=0o700)
    with tarfile.open(archive, "r:") as bundle:
        members = bundle.getmembers()
        if (
            len(members) != 2
            or {member.name for member in members} != _ENTRIES
            or any(
                not member.isfile() or not 0 < member.size <= 2_000_000
                for member in members
            )
        ):
            raise AgeRehearsalError("Decrypted archive structure is invalid")
        for member in members:
            file = bundle.extractfile(member)
            if file is None:
                raise AgeRehearsalError("Decrypted archive file is missing")
            with file, (destination / member.name).open("xb") as output:
                os.fchmod(output.fileno(), 0o600)
                shutil.copyfileobj(file, output)


def _new_output(output: Path) -> Path:
    if not isinstance(output, Path) or output.is_symlink():
        raise AgeRehearsalError("Explicit fresh output directory required")
    target = output.resolve()
    if target == ROOT or ROOT in target.parents or target.exists():
        raise AgeRehearsalError("Output must be fresh and outside the checkout")
    missing = []
    parent = target.parent
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    for parent in reversed(missing):
        parent.mkdir(mode=0o700)
    target.mkdir(mode=0o700, exist_ok=False)
    return target


def run_age_rehearsal(
    output: Path, age_binary: Path, keygen_binary: Path
) -> dict[str, Any]:
    """Encrypt an owned fixture for primary+escrow and verify both independently."""
    destination = _new_output(output)
    report: dict[str, Any] = {
        "mode": "offline_age_fixture",
        "status": "failed",
        "live_calls": 0,
        "age_version": "",
        **{name: False for name in _FLAGS},
    }
    try:
        age, keygen = _binary(age_binary), _binary(keygen_binary)
        version = _capture([age, "--version"]).decode("ascii").strip()
        if not re.fullmatch(r"v?\d+\.\d+\.\d+", version):
            raise AgeRehearsalError("Unrecognized age version response")
        report["age_version"] = version
        with tempfile.TemporaryDirectory(prefix="techblog-age-rehearsal-") as temporary:
            base = Path(temporary).resolve()
            base.chmod(0o700)
            path, snapshot = base / "budget.sqlite", base / "snapshot"
            with BudgetLedger(
                path, daily_limit_microusd=1000, batch_limit_microusd=800
            ).batch("offline-age") as batch:
                now = datetime.now(timezone.utc)
                confirmed = batch.reserve("confirmed", 700, at=now)
                batch.settle(confirmed, 200)
                batch.reserve("pending", 300, at=now)
            guard = ProductionBudgetLedger(
                path, daily_limit_microusd=1000, batch_limit_microusd=800
            )
            tool = LedgerBackup(guard)
            tool.backup(snapshot)
            _, original_audit = tool._verify(snapshot)
            original_files = {name: _sha(snapshot / name) for name in _ENTRIES}
            identities = {
                name: base / f"{name}.identity"
                for name in ("primary", "escrow", "wrong")
            }
            recipients = {
                name: _identity(keygen, identity)
                for name, identity in identities.items()
            }
            archive, cipher = base / "snapshot.tar", base / "snapshot.tar.age"
            _archive(snapshot, archive)
            original_tar = _sha(archive)
            if _to_file(
                [
                    age,
                    "--encrypt",
                    "--recipient",
                    recipients["primary"],
                    "--recipient",
                    recipients["escrow"],
                    str(archive),
                ],
                cipher,
            ):
                raise AgeRehearsalError("Fixture encryption failed")
            accounting_matches = []
            for name in ("primary", "escrow"):
                plaintext = base / f"{name}.tar"
                code = _to_file(
                    [
                        age,
                        "--decrypt",
                        "--identity",
                        str(identities[name]),
                        str(cipher),
                    ],
                    plaintext,
                )
                report[f"{name}_roundtrip"] = (
                    code == 0 and _sha(plaintext) == original_tar
                )
                if not report[f"{name}_roundtrip"]:
                    raise AgeRehearsalError("Fixture roundtrip failed")
                unpacked = base / f"{name}-snapshot"
                _unpack(plaintext, unpacked)
                _, restored_audit = tool._verify(unpacked)
                accounting_matches.append(restored_audit == original_audit)
            wrong_output = base / "wrong.tar"
            report["wrong_identity_rejected"] = (
                _to_file(
                    [
                        age,
                        "--decrypt",
                        "--identity",
                        str(identities["wrong"]),
                        str(cipher),
                    ],
                    wrong_output,
                )
                != 0
            )
            tampered = base / "tampered.age"
            data = bytearray(cipher.read_bytes())
            data[-1] ^= 1
            with tampered.open("xb") as file:
                os.fchmod(file.fileno(), 0o600)
                file.write(data)
            report["tampered_ciphertext_rejected"] = (
                _to_file(
                    [
                        age,
                        "--decrypt",
                        "--identity",
                        str(identities["primary"]),
                        str(tampered),
                    ],
                    base / "tampered.tar",
                )
                != 0
            )
            report["plaintext_preserved"] = _sha(
                archive
            ) == original_tar and original_files == {
                name: _sha(snapshot / name) for name in _ENTRIES
            }
            report["snapshot_accounting_preserved"] = all(accounting_matches)
            if not all(report[name] for name in _FLAGS):
                raise AgeRehearsalError("Encryption rehearsal invariants failed")
        # No keys, recipients, plaintext, ciphertext, or private paths leave temp.
        report["status"] = "validated"
    except Exception:
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
    parser.add_argument("--age-bin", type=Path, required=True)
    parser.add_argument("--age-keygen-bin", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = run_age_rehearsal(args.output, args.age_bin, args.age_keygen_bin)
    except (AgeRehearsalError, OSError):
        print(
            "Offline age rehearsal output refused; no user source or identity was selected.",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "validated" else 1


if __name__ == "__main__":
    raise SystemExit(main())
