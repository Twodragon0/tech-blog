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


def test_ops_queries_only_selected_project_and_unresolved(monkeypatch) -> None:
    monkeypatch.setenv("SENTRY_AUTH_TOKEN", "fixture-token")
    monkeypatch.setenv("SENTRY_ORG", "fixture-org")
    monkeypatch.setenv("SENTRY_PROJECT", "fixture-project")
    requests = []

    def respond(request, **_kwargs):
        requests.append(request)
        return io.BytesIO(b"[]")

    monkeypatch.setattr(ops.urllib.request, "urlopen", respond)
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
    monkeypatch.setattr(
        ops.urllib.request, "urlopen", lambda *_a, **_k: io.BytesIO(payload)
    )
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

    monkeypatch.setattr(ops.urllib.request, "urlopen", denied)
    result = ops.check_sentry(0)
    assert not result.ok and result.priority == "P1"
    assert "private-response" not in result.summary
    assert "event:read" in result.recommendation


@pytest.mark.parametrize(
    "status,payload,success",
    [
        (200, "[]", True),
        (403, '{"detail":"private-response"}', False),
        (200, "{}", False),
    ],
)
def test_workflow_issues_access_is_required(tmp_path, status, payload, success) -> None:
    workflow = yaml.safe_load(
        (ROOT / ".github/workflows/sentry-healthcheck.yml").read_text()
    )
    step = next(
        s
        for s in workflow["jobs"]["sentry-healthcheck"]["steps"]
        if s.get("id") == "token"
    )
    fake = tmp_path / "curl"
    fake.write_text("""#!/usr/bin/env python3
import os,sys
from pathlib import Path
args=sys.argv[1:]; out=Path(args[args.index('-o')+1]); url=args[-1]
project='/projects/' in url
out.write_text('{}' if project else os.environ['FIXTURE_PAYLOAD'])
print('200' if project else os.environ['FIXTURE_STATUS'], end='')
""")
    fake.chmod(0o700)
    env = os.environ | {
        "PATH": str(tmp_path) + ":" + os.environ["PATH"],
        "RUNNER_TEMP": str(tmp_path),
        "GITHUB_OUTPUT": str(tmp_path / "output"),
        "SENTRY_ORG": "fixture-org",
        "SENTRY_PROJECT": "fixture-project",
        "SENTRY_AUTH_TOKEN": "fixture-token",
        "FIXTURE_PAYLOAD": payload,
        "FIXTURE_STATUS": str(status),
    }
    result = subprocess.run(
        ["bash", "-e", "-c", step["run"]], env=env, text=True, capture_output=True
    )
    assert (result.returncode == 0) is success
    assert "private-response" not in result.stdout + result.stderr
    assert "fixture-token" not in result.stdout + result.stderr
    if not success:
        assert "issues_ok=true" not in (tmp_path / "output").read_text()
