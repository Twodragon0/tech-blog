"""Exercise dedicated monitoring with fake HTTP and synthetic credentials."""

from __future__ import annotations

import io
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import ops_health_orchestrator as ops  # noqa: E402

from scripts.lib import sentry_monitor as monitor  # noqa: E402


@pytest.fixture
def dedicated(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SENTRY_MONITOR_MODE", "dedicated")
    monkeypatch.setenv("SENTRY_MONITOR_AUTH_TOKEN", "dedicated-fixture")
    monkeypatch.setenv("SENTRY_AUTH_TOKEN", "shared-fixture")
    monkeypatch.setenv("SENTRY_ORG", "test-org")
    monkeypatch.setenv("SENTRY_PROJECT", "test-project")


class Response(io.BytesIO):
    def __init__(self, payload: object, link: str = "", status: int = 200) -> None:
        super().__init__(json.dumps(payload).encode())
        self.headers = {"Link": link}
        self.status = status


def test_dedicated_missing_never_falls_back(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SENTRY_MONITOR_AUTH_TOKEN")
    with pytest.raises(monitor.SentryMonitorError, match="SENTRY_MONITOR_AUTH_TOKEN"):
        monitor.load_config()


def test_unknown_mode_cannot_select_shared(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SENTRY_MONITOR_MODE", "unexpected")
    with pytest.raises(monitor.SentryMonitorError, match="Invalid SENTRY_MONITOR_MODE"):
        monitor.load_config()


def test_default_mode_uses_existing_shared_token(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("SENTRY_MONITOR_MODE")
    assert monitor.load_config().token == "shared-fixture"


def test_pagination_keeps_target_and_token(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    responses = iter(
        [
            Response(
                [{"title": "private first title"}],
                '<https://other.invalid/ignored?cursor=0%3A1%3A0>; rel="next"; results="true"',
            ),
            Response([{"title": "private second title"}]),
        ]
    )
    queries = []

    def respond(request, **_kwargs):
        url = urllib.parse.urlsplit(request.full_url)
        assert url.hostname == "sentry.io"
        assert url.path == "/api/0/organizations/test-org/issues/"
        assert request.get_header("Authorization") == "Bearer dedicated-fixture"
        params = urllib.parse.parse_qs(url.query)
        assert params["project"] == ["test-project"]
        assert params["query"] == ["is:unresolved"]
        queries.append(params)
        return next(responses)

    monkeypatch.setattr(monitor, "_open", respond)
    page = monitor.read_issues(monitor.load_config(), max_pages=2)
    assert page.complete
    assert len(page.issues) == 2
    assert "cursor" not in queries[0]
    assert queries[1]["cursor"] == ["0:1:0"]


@pytest.mark.parametrize("payload", [{"detail": "private body"}, [123], None])
def test_wrong_response_type_is_unmeasured(
    dedicated: None, monkeypatch: pytest.MonkeyPatch, payload: object
) -> None:
    monkeypatch.setattr(monitor, "_open", lambda *_a, **_k: Response(payload))
    with pytest.raises(monitor.SentryMonitorError, match="issue list"):
        monitor.read_issues(monitor.load_config())


def test_page_limit_produces_partial_measurement(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        monitor,
        "_open",
        lambda *_a, **_k: Response(
            [], '<https://sentry.io/>; rel="next"; results="true"; cursor="0:1:0"'
        ),
    )
    assert not monitor.read_issues(monitor.load_config(), max_pages=1).complete


def test_incomplete_pagination_metadata_is_unmeasured(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        monitor,
        "_open",
        lambda *_a, **_k: Response([{}], '<https://sentry.io/>; rel="previous"'),
    )
    with pytest.raises(monitor.SentryMonitorError, match="invalid pagination"):
        monitor.read_issues(monitor.load_config(), limit=1)


def test_later_page_failure_is_unmeasured(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    first = Response(
        [{"title": "private first-page title"}],
        '<https://sentry.io/>; rel="next"; results="true"; cursor="0:1:0"',
    )

    def respond(request, **_kwargs):
        if "cursor" in request.full_url:
            raise urllib.error.HTTPError(
                "https://sentry.io", 429, "private body", {}, None
            )
        return first

    monkeypatch.setattr(monitor, "_open", respond)
    with pytest.raises(monitor.SentryMonitorError, match="HTTP 429") as caught:
        monitor.read_issues(monitor.load_config())
    assert "private" not in str(caught.value)


def test_deadline_is_checked_before_requesting_next_page(
    dedicated: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    ticks = iter([10.0, 11.0, 35.0])
    monkeypatch.setattr(monitor.time, "monotonic", lambda: next(ticks))

    def respond(request, *, timeout):
        assert "cursor" not in request.full_url
        assert timeout == 24
        return Response(
            [], '<https://sentry.io/>; rel="next"; results="true"; cursor="0:1:0"'
        )

    monkeypatch.setattr(monitor, "_open", respond)
    with pytest.raises(monitor.SentryMonitorError, match="deadline exceeded"):
        monitor.read_issues(monitor.load_config())


@pytest.mark.parametrize(
    "failure", [TimeoutError("private timeout"), ValueError("private JSON")]
)
def test_transport_and_json_failures_hide_exception_detail(
    dedicated: None, monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    def fail(*_args, **_kwargs):
        raise failure

    monkeypatch.setattr(monitor, "_open", fail)
    with pytest.raises(
        monitor.SentryMonitorError, match="request or JSON decoding failed"
    ) as caught:
        monitor.read_issues(monitor.load_config())
    assert "private" not in str(caught.value)


def test_redirect_handler_declines_cross_host_redirect() -> None:
    request = urllib.request.Request("https://sentry.io/")
    result = monitor.NoRedirect().redirect_request(
        request, None, 302, "Found", {}, "https://untrusted.invalid/"
    )
    assert result is None


def test_dedicated_ops_http_failure_blocks_entry_point(
    dedicated: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ops", "--skip-lint", "--skip-vercel", "--skip-github-actions"],
    )

    def denied(*_args, **_kwargs):
        raise urllib.error.HTTPError(
            "https://sentry.io", 403, "private reason", {}, io.BytesIO(b"private body")
        )

    monkeypatch.setattr(monitor, "_open", denied)
    assert ops.main() == 1
    out = capsys.readouterr().out
    assert "403" in out and "no issues measured" in out
    assert "private body" not in out and "private reason" not in out


def test_dedicated_ops_issue_count_does_not_leak_title_or_block(
    dedicated: None, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ops", "--skip-lint", "--skip-vercel", "--skip-github-actions"],
    )
    monkeypatch.setattr(
        monitor,
        "_open",
        lambda *_a, **_k: Response([{"title": "private title sentinel"}]),
    )
    assert ops.main() == 0
    out = capsys.readouterr().out
    assert "unresolved issues: 1" in out
    assert "private title sentinel" not in out
