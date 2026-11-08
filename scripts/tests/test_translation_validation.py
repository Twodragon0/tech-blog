"""T6 validation uses fixture transport, isolated files and no credentials."""

import json
import socket
from pathlib import Path

import pytest
import requests

from scripts.validate_translation_pipeline import ValidationError, validate_fixture

FIXTURE = Path(__file__).parent / "fixtures/translation-validation.json"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("No network in T6 fixture mode")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


def test_fixture_reaches_t2_t4_t5_and_real_render_gates(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "must-never-read-this-key")
    report = validate_fixture(
        FIXTURE, tmp_path / "out", tmp_path / "budget.sqlite", "offline-1"
    )
    assert report["status"] == "validated"
    assert report["live_calls"] == 0 and report["fixture_requests"] == 3
    assert report["rendered_articles"] == 3 and report["quality_score"] >= 80
    content = (tmp_path / "out/candidate.md").read_text()
    assert "Acme" in content and "업데이트" in content
    assert not (tmp_path / "_posts").exists()
    assert "must-never-read" not in (tmp_path / "out/report.json").read_text()
    assert (tmp_path / "out/candidate.md").stat().st_mode & 0o777 == 0o600


def test_validation_refuses_repository_outputs():
    with pytest.raises(ValidationError):
        validate_fixture(FIXTURE, Path.cwd() / "_posts", Path("unused"), "bad")


def test_validation_refuses_overwrite(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    with pytest.raises(ValidationError):
        validate_fixture(FIXTURE, output, tmp_path / "budget", "bad")
    assert list(output.iterdir()) == []


def test_bad_translation_preserves_failure_without_candidate(tmp_path):
    data = json.loads(FIXTURE.read_text())
    data["articles"][0]["translation"]["korean_summary"] = "피해는 999건이다."
    fixture = tmp_path / "bad.json"
    fixture.write_text(json.dumps(data))
    with pytest.raises(ValidationError):
        validate_fixture(fixture, tmp_path / "out", tmp_path / "budget", "bad")
    report = json.loads((tmp_path / "out/report.json").read_text())
    assert report["status"] == "failed" and report["live_calls"] == 0
    assert not (tmp_path / "out/candidate.md").exists()


def test_budget_exhaustion_makes_zero_fixture_requests(tmp_path):
    with pytest.raises(ValidationError):
        validate_fixture(
            FIXTURE,
            tmp_path / "out",
            tmp_path / "budget",
            "small",
            daily_limit_microusd=1,
            batch_limit_microusd=1,
        )
    report = json.loads((tmp_path / "out/report.json").read_text())
    assert report["fixture_requests"] == 0 and report["status"] == "failed"


def test_cli_has_no_live_or_provider_mode():
    from scripts.validate_translation_pipeline import main

    with pytest.raises(SystemExit) as caught:
        main(["--live"])
    assert caught.value.code == 2


def test_workflow_is_manual_readonly_without_secrets_or_publish():
    import yaml

    path = Path(__file__).parents[2] / ".github/workflows/translation-validation.yml"
    text = path.read_text()
    workflow = yaml.safe_load(text)
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) == {"workflow_dispatch"}
    assert workflow["permissions"] == {"contents": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] is False
    assert "secrets." not in text and "--live" not in text
    assert "persist-credentials: false" in text
    assert "validate_translation_pipeline.py" in text
    assert "candidate.md" not in text
    assert "--require-existing-ledger" in text
    assert "rehearse_translation_backup.py" in text
    run_steps = [
        step.get("run", "")
        for step in workflow["jobs"][next(iter(workflow["jobs"]))]["steps"]
    ]
    commands = [
        command
        for command in run_steps
        if "validate_translation_pipeline.py" in command
    ]
    assert any("--require-existing-ledger" not in command for command in commands)
    assert any("--require-existing-ledger" in command for command in commands)
    artifacts = {
        step["with"]["name"]: step["with"]["path"]
        for step in workflow["jobs"]["validate"]["steps"]
        if "actions/upload-artifact@" in step.get("uses", "")
    }
    assert artifacts == {
        "translation-backup-rehearsal-report": "${{ runner.temp }}/translation-backup-rehearsal/report.json",
        "translation-bootstrap-report": "${{ runner.temp }}/translation-validation-bootstrap/report.json",
        "translation-offline-report": "${{ runner.temp }}/translation-validation/report.json",
    }


def test_quality_repair_cannot_replace_validated_translation(tmp_path, monkeypatch):
    import scripts.validate_translation_pipeline as validation

    def tamper(path, target):
        path.write_text(
            path.read_text().replace("Acme 업데이트 공개", "다른 기사 제목")
        )
        return 100

    monkeypatch.setattr(validation, "_run_post_quality_gate", tamper)
    with pytest.raises(ValidationError):
        validate_fixture(FIXTURE, tmp_path / "out", tmp_path / "budget", "tamper")
    assert not (tmp_path / "out/candidate.md").exists()
    assert json.loads((tmp_path / "out/report.json").read_text())["status"] == "failed"


def test_new_validation_run_keeps_previous_daily_spend(tmp_path):
    options = {"daily_limit_microusd": 2_000, "batch_limit_microusd": 2_000}
    validate_fixture(
        FIXTURE, tmp_path / "first", tmp_path / "budget", "run-1", **options
    )
    with pytest.raises(ValidationError):
        validate_fixture(
            FIXTURE, tmp_path / "second", tmp_path / "budget", "run-2", **options
        )
    report = json.loads((tmp_path / "second/report.json").read_text())
    assert report["status"] == "failed" and report["fixture_requests"] == 0


def _cli_validation(fixture, output, ledger_path, run_id, *, protected=False):
    import os
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[2]
    command = [
        sys.executable,
        str(root / "scripts/validate_translation_pipeline.py"),
        "--fixture",
        str(fixture),
        "--output",
        str(output),
        "--ledger",
        str(ledger_path),
        "--run-id",
        run_id,
    ]
    if protected:
        command.append("--require-existing-ledger")
    env = os.environ.copy()
    for name in (
        "OPENAI_API_KEY",
        "CLAUDE_API_KEY",
        "GEMINI_API_KEY",
        "DEEPSEEK_API_KEY",
    ):
        env.pop(name, None)
    return subprocess.run(
        command, cwd=root, env=env, capture_output=True, text=True, timeout=30
    )


def _ledger_records(path):
    import sqlite3
    from contextlib import closing

    with closing(sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)) as db:
        return (
            db.execute("SELECT * FROM runs ORDER BY run_id").fetchall(),
            db.execute("SELECT * FROM reservations ORDER BY reservation_id").fetchall(),
        )


def test_protected_cli_missing_storage_reports_zero_requests_and_never_bootstraps(
    tmp_path,
):
    ledger_path = tmp_path / "production" / "budget.sqlite"
    output = tmp_path / "blocked"
    result = _cli_validation(FIXTURE, output, ledger_path, "missing", protected=True)
    assert result.returncode != 0
    report = json.loads((output / "report.json").read_text())
    assert report["ledger_policy"] == "existing_only"
    assert report["fixture_requests"] == 0 and report["live_calls"] == 0
    assert report["status"] == "failed"
    assert not ledger_path.exists() and not ledger_path.parent.exists()
    assert not (output / "candidate.md").exists()


def test_protected_cli_bootstrap_maintenance_clear_resume_preserves_spend_and_inode(
    tmp_path,
):
    from scripts.news.translation_budget import BudgetError
    from scripts.news.translation_production import ProductionBudgetLedger

    ledger_path = tmp_path / "budget.sqlite"
    first = _cli_validation(FIXTURE, tmp_path / "bootstrap", ledger_path, "bootstrap")
    assert first.returncode == 0, first.stdout + first.stderr
    bootstrap_report = json.loads((tmp_path / "bootstrap/report.json").read_text())
    assert bootstrap_report["ledger_policy"] == "fixture_bootstrap"
    assert bootstrap_report["fixture_requests"] == 3
    lock = ledger_path.with_name(ledger_path.name + ".lock")
    inode = lock.stat().st_ino
    prior = _ledger_records(ledger_path)
    second = _cli_validation(
        FIXTURE, tmp_path / "protected", ledger_path, "protected-one", protected=True
    )
    assert second.returncode == 0, second.stdout + second.stderr
    report = json.loads((tmp_path / "protected/report.json").read_text())
    assert report["ledger_policy"] == "existing_only" and report["quality_score"] >= 80
    assert report["fixture_requests"] == 3 and report["rendered_articles"] == 3
    before_maintenance = _ledger_records(ledger_path)
    guard = ProductionBudgetLedger(
        ledger_path, daily_limit_microusd=1_000_000, batch_limit_microusd=250_000
    )
    guard.enter_maintenance("restore-one", "restore")
    blocked = _cli_validation(
        FIXTURE, tmp_path / "maintenance", ledger_path, "blocked", protected=True
    )
    assert blocked.returncode != 0
    blocked_report = json.loads((tmp_path / "maintenance/report.json").read_text())
    assert blocked_report["ledger_policy"] == "existing_only"
    assert (
        blocked_report["fixture_requests"] == 0 and blocked_report["status"] == "failed"
    )
    assert not (tmp_path / "maintenance/candidate.md").exists()
    assert _ledger_records(ledger_path) == before_maintenance
    with pytest.raises(BudgetError):
        guard.clear_maintenance("wrong-id")
    assert guard.maintenance_path.exists()
    guard.clear_maintenance("restore-one")
    resumed = _cli_validation(
        FIXTURE, tmp_path / "resumed", ledger_path, "resumed", protected=True
    )
    assert resumed.returncode == 0, resumed.stdout + resumed.stderr
    resumed_report = json.loads((tmp_path / "resumed/report.json").read_text())
    assert resumed_report["ledger_policy"] == "existing_only"
    assert resumed_report["fixture_requests"] == 3 and resumed_report["live_calls"] == 0
    assert resumed_report["quality_score"] >= 80
    final = _ledger_records(ledger_path)
    assert all(row in final[0] for row in prior[0])
    assert all(row in final[1] for row in prior[1])
    assert len(final[1]) == 9
    assert sum(row[-1] for row in final[1]) == 4_500
    assert lock.stat().st_ino == inode


@pytest.mark.parametrize("kind", ["empty", "corrupt", "policy"])
def test_protected_cli_invalid_existing_storage_cannot_make_requests(tmp_path, kind):
    from scripts.news.translation_budget import BudgetLedger

    path = tmp_path / "budget.sqlite"
    if kind == "policy":
        with BudgetLedger(
            path, daily_limit_microusd=100, batch_limit_microusd=80
        ).batch("fixture"):
            pass
    else:
        path.write_bytes(b"" if kind == "empty" else b"corrupt evidence")
        path.with_name(path.name + ".lock").touch(mode=0o600)
    before = path.read_bytes()
    output = tmp_path / kind
    result = _cli_validation(FIXTURE, output, path, "blocked", protected=True)
    assert result.returncode != 0
    report = json.loads((output / "report.json").read_text())
    assert report["ledger_policy"] == "existing_only"
    assert report["fixture_requests"] == 0 and report["live_calls"] == 0
    assert not (output / "candidate.md").exists()
    assert path.read_bytes() == before


@pytest.mark.parametrize("flag", [None, 0, 1, "true"])
def test_require_existing_policy_must_be_a_real_boolean(tmp_path, flag):
    with pytest.raises(ValidationError):
        validate_fixture(
            FIXTURE,
            tmp_path / "out",
            tmp_path / "budget",
            "bad-flag",
            require_existing_ledger=flag,
        )
    assert not (tmp_path / "budget").exists()


def test_protected_cli_missing_lock_is_not_recreated_or_charged(tmp_path):
    path = tmp_path / "budget.sqlite"
    assert (
        _cli_validation(FIXTURE, tmp_path / "bootstrap", path, "bootstrap").returncode
        == 0
    )
    lock = path.with_name(path.name + ".lock")
    lock.unlink()
    before = _ledger_records(path)
    result = _cli_validation(
        FIXTURE, tmp_path / "blocked", path, "missing-lock", protected=True
    )
    assert result.returncode != 0
    report = json.loads((tmp_path / "blocked/report.json").read_text())
    assert (
        report["ledger_policy"] == "existing_only" and report["fixture_requests"] == 0
    )
    assert not lock.exists() and _ledger_records(path) == before
    assert not (tmp_path / "blocked/candidate.md").exists()


def test_protected_report_declares_policy_even_when_fixture_load_fails(tmp_path):
    malformed = tmp_path / "malformed.json"
    malformed.write_text("not JSON")
    with pytest.raises(ValidationError):
        validate_fixture(
            malformed,
            tmp_path / "failed",
            tmp_path / "missing-db",
            "bad-fixture",
            require_existing_ledger=True,
        )
    report = json.loads((tmp_path / "failed/report.json").read_text())
    assert (
        report["ledger_policy"] == "existing_only" and report["fixture_requests"] == 0
    )
    assert not (tmp_path / "missing-db").exists()
