"""A 403 from the issues API must name the token's scopes, never its value."""

import io
import json
import urllib.error

import pytest

from scripts.lib import sentry_monitor as monitor


class Response(io.BytesIO):
    status = 200
    headers: dict[str, str] = {}


def _config():
    return monitor.SentryConfig("fixture-org", "fixture-project", "secret-token-value")


def _respond(root_payload):
    def respond(request, **_kwargs):
        url = request.full_url
        if url.endswith("/projects/fixture-org/fixture-project/"):
            return Response(b'{"id": "1"}')
        if "/issues/" in url:
            raise urllib.error.HTTPError(url, 403, "Forbidden", {}, io.BytesIO(b"body"))
        if url == f"{monitor.API_ROOT}/":
            if root_payload is None:
                raise urllib.error.HTTPError(url, 401, "No", {}, io.BytesIO(b""))
            return Response(json.dumps(root_payload).encode())
        raise AssertionError(url)

    return respond


def test_issues_403_reports_scopes_and_missing_event_read(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "out"))
    payload = {"auth": {"scopes": ["project:releases", "org:read", "project:read"]}}
    monkeypatch.setattr(monitor, "_open", _respond(payload))
    with pytest.raises(monitor.SentryMonitorError) as error:
        monitor._healthcheck(_config())
    message = str(error.value)
    assert "HTTP 403" in message
    assert "token scopes: org:read, project:read, project:releases" in message
    assert "missing event:read" in message
    assert "secret-token-value" not in message
    assert "issues_ok=false" in (tmp_path / "out").read_text()


def test_scope_lookup_failure_keeps_the_original_error(monkeypatch, tmp_path):
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "out"))
    monkeypatch.setattr(monitor, "_open", _respond(None))
    with pytest.raises(monitor.SentryMonitorError) as error:
        monitor._healthcheck(_config())
    assert str(error.value) == "Sentry issues API returned HTTP 403"
