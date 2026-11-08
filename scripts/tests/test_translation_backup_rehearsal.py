"""The rehearsal uses only its own disposable DB and emits a safe report."""

import json
import os
import socket
import subprocess
import sys
from pathlib import Path

import pytest
import requests

from scripts.rehearse_translation_backup import RehearsalError, main, run_rehearsal

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("No live network during a ledger rehearsal")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


def assert_validated(report):
    assert report["mode"] == "offline_backup_restore"
    assert report["status"] == "validated" and report["live_calls"] == 0
    assert report["counts"] == {
        "runs": 1,
        "reservations": 2,
        "unsettled": 1,
        "charged_microusd": 500,
    }
    for field in (
        "maintenance_retained",
        "lock_inode_preserved",
        "snapshot_sha256_unchanged",
        "accounting_preserved",
    ):
        assert report[field] is True


def test_rehearsal_real_management_clis_clean_fixture_and_emit_report_only(
    tmp_path, monkeypatch
):
    import scripts.rehearse_translation_backup as module

    temp_factory = module.tempfile.TemporaryDirectory
    created = []

    def record_temporary(*args, **kwargs):
        directory = temp_factory(*args, **kwargs)
        created.append(Path(directory.name))
        return directory

    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", record_temporary)
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-export-private-key")
    monkeypatch.setenv("CLAUDE_API_KEY", "must-not-export-private-claude-key")
    original = module.subprocess.run
    calls = []

    def observe(command, **kwargs):
        assert "manage_translation_ledger.py" in command[1]
        assert not any(
            name in kwargs["env"]
            for name in (
                "OPENAI_API_KEY",
                "CLAUDE_API_KEY",
                "ANTHROPIC_API_KEY",
                "GEMINI_API_KEY",
                "DEEPSEEK_API_KEY",
            )
        )
        calls.append(command[2])
        return original(command, **kwargs)

    monkeypatch.setattr(module.subprocess, "run", observe)
    output = tmp_path / "report"
    report = run_rehearsal(output)
    assert_validated(report)
    assert calls == ["backup", "restore"]
    assert created and all(not path.exists() for path in created)
    assert [file.name for file in output.iterdir()] == ["report.json"]
    assert json.loads((output / "report.json").read_text()) == report
    assert "private-key" not in (output / "report.json").read_text()
    assert (output / "report.json").stat().st_mode & 0o777 == 0o600
    assert output.stat().st_mode & 0o777 == 0o700


def test_actual_cli_reports_success_without_ledger_or_production_arguments(tmp_path):
    output = tmp_path / "cli-report"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/rehearse_translation_backup.py"),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert_validated(json.loads((output / "report.json").read_text()))
    assert_validated(json.loads(result.stdout))
    assert {file.name for file in output.iterdir()} == {"report.json"}


@pytest.mark.parametrize("flag", ["--ledger", "--production", "--live"])
def test_no_production_or_live_mode(flag, tmp_path):
    with pytest.raises(SystemExit) as caught:
        main(["--output", str(tmp_path / "out"), flag, "unused"])
    assert caught.value.code == 2
    assert not (tmp_path / "out").exists()


def test_existing_or_checkout_output_is_refused_without_overwrite(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    marker = existing / "report.json"
    marker.write_text("keep")
    with pytest.raises(RehearsalError):
        run_rehearsal(existing)
    assert marker.read_text() == "keep"
    for target in (ROOT, ROOT / "new-rehearsal-output"):
        with pytest.raises(RehearsalError):
            run_rehearsal(target)
    assert not (ROOT / "new-rehearsal-output").exists()


def test_forced_restore_failure_emits_safe_failure_and_cleans_temp(
    tmp_path, monkeypatch
):
    import scripts.rehearse_translation_backup as module

    original = module.subprocess.run
    temp_factory = module.tempfile.TemporaryDirectory
    created = []

    def record_temporary(*args, **kwargs):
        directory = temp_factory(*args, **kwargs)
        created.append(Path(directory.name))
        return directory

    def fail_restore(command, **kwargs):
        if command[2] == "restore":
            return subprocess.CompletedProcess(
                command, 1, "", "raw secret exception do-not-export"
            )
        return original(command, **kwargs)

    monkeypatch.setattr(module.tempfile, "TemporaryDirectory", record_temporary)
    monkeypatch.setattr(module.subprocess, "run", fail_restore)
    output = tmp_path / "failed"
    assert main(["--output", str(output)]) == 1
    report = json.loads((output / "report.json").read_text())
    assert report["status"] == "failed" and report["live_calls"] == 0
    assert "do-not-export" not in (output / "report.json").read_text()
    assert created and all(not path.exists() for path in created)
    assert {path.name for path in output.iterdir()} == {"report.json"}


def test_symlink_output_is_not_followed(tmp_path):
    alias = tmp_path / "alias"
    target = tmp_path / "target"
    alias.symlink_to(target, target_is_directory=True)
    with pytest.raises(RehearsalError):
        run_rehearsal(alias)
    assert not target.exists()
