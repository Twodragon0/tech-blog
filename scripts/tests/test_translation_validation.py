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
