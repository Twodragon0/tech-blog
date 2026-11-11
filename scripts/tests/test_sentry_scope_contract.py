"""Sentry monitoring must distinguish access failure from an empty project."""

import io
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import ops_health_orchestrator as ops  # noqa: E402

from scripts.lib import sentry_monitor as monitor  # noqa: E402


class Response(io.BytesIO):
    status = 200
    headers: dict[str, str] = {}


def test_ops_queries_only_selected_project_and_unresolved(monkeypatch) -> None:
    monkeypatch.setenv("SENTRY_AUTH_TOKEN", "fixture-token")
    monkeypatch.setenv("SENTRY_ORG", "fixture-org")
    monkeypatch.setenv("SENTRY_PROJECT", "fixture-project")
    requests = []

    def respond(request, **_kwargs):
        requests.append(request)
        return Response(b"[]")

    monkeypatch.setattr(monitor, "_open", respond)
    result = ops.check_sentry(0)
    assert result.ok
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(requests[0].full_url).query)
    assert query == {
        "project": ["fixture-project"],
        "query": ["is:unresolved"],
        "limit": ["100"],
    }


@pytest.mark.parametrize("payload", [b'{"detail":"not issues"}', b"[1]", b"not-json"])
def test_ops_invalid_issue_payload_is_not_clean(monkeypatch, payload) -> None:
    for name in ("SENTRY_AUTH_TOKEN", "SENTRY_ORG", "SENTRY_PROJECT"):
        monkeypatch.setenv(name, "fixture")
    monkeypatch.setattr(monitor, "_open", lambda *_a, **_k: Response(payload))
    result = ops.check_sentry(0)
    assert not result.ok
    assert result.priority == "P1"


@pytest.mark.parametrize("status", [401, 403])
def test_ops_auth_failure_is_p1_without_private_body(monkeypatch, status) -> None:
    for name in ("SENTRY_AUTH_TOKEN", "SENTRY_ORG", "SENTRY_PROJECT"):
        monkeypatch.setenv(name, "fixture")

    def denied(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://sentry.io", status, "Denied", {}, io.BytesIO(b"private-response")
        )

    monkeypatch.setattr(monitor, "_open", denied)
    result = ops.check_sentry(0)
    assert not result.ok and result.priority == "P1"
    assert "private-response" not in result.summary
    assert "event:read" in result.recommendation


def _fixture_http_environment(tmp_path, status, payload, mode="dedicated"):
    (tmp_path / "sitecustomize.py").write_text("""
import io
import os
import urllib.request

class Response(io.BytesIO):
    headers = {}

class FixtureOpener:
    def open(self, request, *, timeout):
        assert request.full_url.startswith("https://sentry.io/api/0/")
        assert request.get_header("Authorization") == "Bearer " + os.environ["EXPECTED_TOKEN"]
        project = "/projects/" in request.full_url
        response = Response(b"{}" if project else os.environ["FIXTURE_PAYLOAD"].encode())
        response.status = 200 if project else int(os.environ["FIXTURE_STATUS"])
        return response

urllib.request.build_opener = lambda *_a, **_k: FixtureOpener()
""")
    return os.environ | {
        "PYTHONPATH": str(tmp_path),
        "GITHUB_OUTPUT": str(tmp_path / "output"),
        "SENTRY_ORG": "fixture-org",
        "SENTRY_PROJECT": "fixture-project",
        "SENTRY_MONITOR_MODE": mode,
        "EXPECTED_TOKEN": f"{mode}-fixture",
        "SENTRY_MONITOR_AUTH_TOKEN": "dedicated-fixture",
        "SENTRY_AUTH_TOKEN": "shared-fixture",
        "FIXTURE_PAYLOAD": payload,
        "FIXTURE_STATUS": str(status),
    }


@pytest.mark.parametrize(
    "status,payload,success",
    [
        (200, "[]", True),
        (403, '{"detail":"private-response"}', False),
        (200, "{}", False),
    ],
)
@pytest.mark.parametrize("mode", ["shared", "dedicated"])
def test_workflow_issues_access_is_required(
    tmp_path, status, payload, success, mode
) -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/sentry-healthcheck.yml").read_text()
    )
    step = next(
        s
        for s in workflow["jobs"]["sentry-healthcheck"]["steps"]
        if s.get("id") == "token"
    )
    env = _fixture_http_environment(tmp_path, status, payload, mode)
    result = subprocess.run(
        ["bash", "-e", "-c", step["run"]],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    assert (result.returncode == 0) is success
    assert "private-response" not in result.stdout + result.stderr
    assert "dedicated-fixture" not in result.stdout + result.stderr
    assert "shared-fixture" not in result.stdout + result.stderr
    if not success:
        assert "issues_ok=true" not in (tmp_path / "output").read_text()


@pytest.mark.parametrize(
    "mode,status,payload,expected",
    [
        ("dedicated", 200, "[]", 0),
        ("dedicated", 200, '[{"title":"private-response"}]', 0),
        ("dedicated", 403, '{"detail":"private-response"}', 1),
        ("dedicated", 200, '{"detail":"private-response"}', 1),
        ("dedicated", 200, "private-response", 1),
        ("shared", 403, '{"detail":"private-response"}', 0),
    ],
)
def test_monitoring_script_exit_reflects_measurement(
    tmp_path, mode, status, payload, expected
) -> None:
    env = _fixture_http_environment(tmp_path, status, payload, mode)
    for name, script in (
        (
            "curl",
            '#!/bin/sh\n[ "${!#}" = "https://blog.invalid" ] || exit 9\nprintf 200\n',
        ),
        ("vercel", "#!/bin/sh\nexit 1\n"),
    ):
        fake = tmp_path / name
        fake.write_text(script.replace("#!/bin/sh", "#!/bin/bash"))
        fake.chmod(0o700)
    env["PATH"] = f"{tmp_path}:{os.environ['PATH']}"
    env["VERCEL_TOKEN"] = ""
    result = subprocess.run(
        [
            "bash",
            "scripts/monitor_vercel_builds.sh",
            "https://blog.invalid",
            "--alert-only",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == expected
    output = result.stdout + result.stderr
    assert "private-response" not in output
    assert "dedicated-fixture" not in output and "shared-fixture" not in output
    if status != 200 or payload.startswith("{") or not payload.startswith("["):
        assert "All checks passed!" not in output
        assert "Unresolved Sentry issues: 0" not in output
        assert "unmeasured" in output


def test_ops_on_demand_wrapper_propagates_failed_access(tmp_path) -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/ops-orchestrator.yml").read_text()
    )
    steps = workflow["jobs"]["on_demand"]["steps"]
    checks = next(step for step in steps if step.get("id") == "checks")
    final = next(
        step
        for step in steps
        if step["name"] == "Fail run if ops health checks reported a blocking issue"
    )
    env = _fixture_http_environment(tmp_path, 403, '{"detail":"private-response"}')
    env.update(
        RUN_LINT_CHECKS="false",
        RUN_VERCEL_CHECKS="false",
        RUN_GITHUB_ACTIONS_CHECKS="false",
        RUN_SENTRY_CHECKS="true",
        AUTO_RECOVER_GHA="false",
    )
    (tmp_path / "scripts").symlink_to(ROOT / "scripts")
    run = subprocess.run(
        ["bash", "-c", checks["run"]],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0
    output = (tmp_path / "output").read_text()
    assert "rc=1" in output.splitlines()
    assert "403" in output and "private-response" not in output
    result = subprocess.run(
        ["bash", "-c", final["run"]],
        cwd=tmp_path,
        env=env | {"OPS_RC": "1"},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
