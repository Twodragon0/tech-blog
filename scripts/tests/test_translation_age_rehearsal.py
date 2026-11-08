"""Explicit temporary age tools exercise fixture-only encryption and key cleanup."""

import json
import os
import socket
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest
import requests

from scripts.rehearse_translation_age import AgeRehearsalError, main, run_age_rehearsal

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("No network in age fixture rehearsal")

    monkeypatch.setattr(socket, "create_connection", blocked)
    monkeypatch.setattr(requests.sessions.Session, "request", blocked)


@pytest.fixture
def binaries():
    paths = [os.getenv("AGE_REHEARSAL_BIN"), os.getenv("AGE_REHEARSAL_KEYGEN_BIN")]
    if not all(paths):
        pytest.skip(
            "Explicit trusted age executables are not available in this environment; set AGE_REHEARSAL_BIN and AGE_REHEARSAL_KEYGEN_BIN"
        )
    age, keygen = (Path(value) for value in paths)
    assert age.is_file() and keygen.is_file(), "Explicit age tool paths must exist"
    return age.resolve(), keygen.resolve()


def assert_valid(report):
    assert report["mode"] == "offline_age_fixture" and report["status"] == "validated"
    assert report["live_calls"] == 0 and report["age_version"]
    for name in (
        "primary_roundtrip",
        "escrow_roundtrip",
        "wrong_identity_rejected",
        "tampered_ciphertext_rejected",
        "plaintext_preserved",
        "snapshot_accounting_preserved",
    ):
        assert report[name] is True


def test_real_native_age_roundtrips_negative_checks_private_keys_and_report_only(
    tmp_path, binaries, monkeypatch
):
    import scripts.rehearse_translation_age as module

    factory = module.tempfile.TemporaryDirectory
    original = module.subprocess.run
    created = []
    identities = []

    def record_temp(*args, **kwargs):
        directory = factory(*args, **kwargs)
        created.append(Path(directory.name))
        return directory

    def observe(command, **kwargs):
        result = original(command, **kwargs)
        if command[0] == str(binaries[1]) and "-o" in command:
            identity = Path(command[command.index("-o") + 1])
            identities.append(identity)
            assert identity.stat().st_mode & 0o777 == 0o600
        return result

    original_archive = module._archive

    def inspect_archive(snapshot, archive):
        original_archive(snapshot, archive)
        with tarfile.open(archive, "r:") as bundle:
            members = bundle.getmembers()
            assert len(members) == 2
            assert {member.name for member in members} == {
                "budget.sqlite",
                "manifest.json",
            }
            assert all(
                member.isfile() and not member.issym() and not member.islnk()
                for member in members
            )

    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", record_temp)
    monkeypatch.setattr(module.subprocess, "run", observe)
    monkeypatch.setattr(module, "_archive", inspect_archive)
    output = tmp_path / "report"
    report = run_age_rehearsal(output, *binaries)
    assert_valid(report)
    assert len(identities) == 3 and all(not path.exists() for path in identities)
    assert created and all(not path.exists() for path in created)
    assert {path.name for path in output.iterdir()} == {"report.json"}
    text = (output / "report.json").read_text()
    assert json.loads(text) == report
    for forbidden in ("AGE-SECRET-KEY", "age1", str(tmp_path), str(binaries[0].parent)):
        assert forbidden not in text
    assert output.stat().st_mode & 0o777 == 0o700
    assert (output / "report.json").stat().st_mode & 0o777 == 0o600


def test_real_age_cli_uses_only_explicit_binaries(tmp_path, binaries, capsys):
    output = tmp_path / "cli"
    code = main(
        [
            "--output",
            str(output),
            "--age-bin",
            str(binaries[0]),
            "--age-keygen-bin",
            str(binaries[1]),
        ]
    )
    assert code == 0
    assert_valid(json.loads(capsys.readouterr().out))
    assert {path.name for path in output.iterdir()} == {"report.json"}


def test_missing_binary_fails_safely_without_install_or_download(tmp_path):
    output = tmp_path / "failed"
    report = run_age_rehearsal(output, tmp_path / "no-age", tmp_path / "no-keygen")
    assert report["status"] == "failed" and report["live_calls"] == 0
    assert {path.name for path in output.iterdir()} == {"report.json"}
    assert "no-age" not in (output / "report.json").read_text()


def test_partial_private_key_failure_is_cleaned_and_never_exported(
    tmp_path, monkeypatch
):
    import scripts.rehearse_translation_age as module

    factory = module.tempfile.TemporaryDirectory
    created = []
    key_paths = []

    def record_temp(*args, **kwargs):
        directory = factory(*args, **kwargs)
        created.append(Path(directory.name))
        return directory

    def fake(command, **kwargs):
        if "--version" in command:
            return subprocess.CompletedProcess(command, 0, b"v1.3.2\n", b"")
        if "-o" in command:
            identity = Path(command[command.index("-o") + 1])
            identity.write_text("AGE-SECRET-KEY-PRIVATE-TEST-DO-NOT-EXPORT")
            identity.chmod(0o600)
            key_paths.append(identity)
            raise RuntimeError(
                "AGE-SECRET-KEY-PRIVATE-TEST-DO-NOT-EXPORT raw tool error"
            )
        pytest.fail("Unexpected command")

    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", record_temp)
    monkeypatch.setattr(module.subprocess, "run", fake)
    output = tmp_path / "failed"
    report = run_age_rehearsal(output, Path(sys.executable), Path(sys.executable))
    assert report["status"] == "failed"
    assert key_paths and all(not path.exists() for path in key_paths)
    assert created and all(not path.exists() for path in created)
    text = (output / "report.json").read_text()
    assert "PRIVATE-TEST" not in text and not any(str(path) in text for path in created)
    assert {path.name for path in output.iterdir()} == {"report.json"}


def test_existing_checkout_and_symlink_outputs_refused(tmp_path):
    missing = tmp_path / "missing-binary"
    existing = tmp_path / "existing"
    existing.mkdir()
    (existing / "report.json").write_text("keep")
    for output in (existing, ROOT, ROOT / "new-age-output"):
        with pytest.raises(AgeRehearsalError):
            run_age_rehearsal(output, missing, missing)
    assert (existing / "report.json").read_text() == "keep"
    alias = tmp_path / "alias"
    alias.symlink_to(tmp_path / "target", target_is_directory=True)
    with pytest.raises(AgeRehearsalError):
        run_age_rehearsal(alias, missing, missing)
    assert not (tmp_path / "target").exists()


@pytest.mark.parametrize(
    "flag",
    ["--ledger", "--source", "--identity", "--recipient", "--plaintext", "--live"],
)
def test_no_user_data_key_or_live_modes(tmp_path, flag):
    with pytest.raises(SystemExit) as caught:
        main(
            [
                "--output",
                str(tmp_path / "output"),
                "--age-bin",
                "/bin/false",
                "--age-keygen-bin",
                "/bin/false",
                flag,
                "unused",
            ]
        )
    assert caught.value.code == 2
    assert not (tmp_path / "output").exists()
