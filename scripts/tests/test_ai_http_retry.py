#!/usr/bin/env python3
"""Tests for scripts/news/enhancer.post_with_retry.

Why this exists
---------------
An untranslated English summary reaching main is not a translation-quality
problem — it is a dropped HTTP call. In blogwatcher run 32794655444 the DeepSeek
endpoint raised ``ConnectionResetError(104)`` three times inside one digest, and
because a failed call returned ``""`` the caller fell straight through to the
English template. Two of those became the English summaries fixed by hand in
commit 8dc5dd2e.

The distinction that matters, and the one these tests pin: a transport fault or
a 429/5xx is worth retrying, a plain 4xx is not. Retrying a retired model or a
bad key just burns the job's wall clock and buries the reason in the log.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.news import enhancer  # noqa: E402


class _Response:
    def __init__(self, status_code: int):
        self.status_code = status_code
        self.text = f"body-{status_code}"


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    """Keep the backoff logic exercised but the suite fast."""
    monkeypatch.setattr(enhancer.time, "sleep", lambda _s: None)


@pytest.fixture
def fake_requests(monkeypatch):
    """Install a stub ``requests`` module that records every POST."""
    calls: list[dict] = []
    module = types.SimpleNamespace()

    def _install(outcomes):
        """``outcomes``: list of Response or Exception, consumed per attempt."""
        seq = list(outcomes)

        def _post(url, headers=None, json=None, timeout=None):
            calls.append({"url": url, "timeout": timeout})
            outcome = seq.pop(0) if seq else _Response(200)
            if isinstance(outcome, Exception):
                raise outcome
            return outcome

        module.post = _post
        monkeypatch.setitem(sys.modules, "requests", module)
        return calls

    return _install


class TestTransientFaults:
    def test_connection_reset_is_retried_and_recovers(self, fake_requests):
        """The exact fault that cost 2026-08-25 two Korean summaries."""
        calls = fake_requests(
            [ConnectionResetError(104, "Connection reset by peer"), _Response(200)]
        )
        resp = enhancer.post_with_retry("https://api.example/x", label="t")
        assert resp is not None and resp.status_code == 200
        assert len(calls) == 2, "a reset must be retried, not surfaced as failure"

    @pytest.mark.parametrize("status", [429, 500, 502, 503])
    def test_rate_limit_and_server_errors_are_retried(self, fake_requests, status):
        calls = fake_requests([_Response(status), _Response(200)])
        resp = enhancer.post_with_retry("https://api.example/x", label="t")
        assert resp is not None and resp.status_code == 200
        assert len(calls) == 2

    def test_returns_none_when_retries_are_exhausted(self, fake_requests):
        calls = fake_requests([ConnectionResetError(104, "reset")] * 9)
        resp = enhancer.post_with_retry("https://api.example/x", label="t")
        assert resp is None, (
            "an exhausted call must return None so the caller can fall back "
            "deliberately rather than dereference a phantom response"
        )
        assert len(calls) == enhancer._TRANSIENT_RETRIES + 1


class TestRealAnswersAreNotRetried:
    @pytest.mark.parametrize("status", [400, 401, 403, 404])
    def test_client_errors_return_immediately(self, fake_requests, status):
        """A retired model ID (404) is an answer, not a blip.

        gemini-2.0-flash 404'd on every call for weeks. Retrying that would
        have tripled the wasted wall clock while telling the reader nothing.
        """
        calls = fake_requests([_Response(status), _Response(200)])
        resp = enhancer.post_with_retry("https://api.example/x", label="t")
        assert resp is not None and resp.status_code == status
        assert len(calls) == 1, f"{status} must not be retried"

    def test_success_makes_exactly_one_call(self, fake_requests):
        calls = fake_requests([_Response(200)])
        resp = enhancer.post_with_retry("https://api.example/x", label="t")
        assert resp is not None and resp.status_code == 200
        assert len(calls) == 1


class TestMissingDependency:
    def test_absent_requests_yields_none(self, monkeypatch):
        """Callers used to guard this with their own try/except ImportError.

        Those guards were removed when they became unreachable, so the helper
        now owns the case and must still return None rather than raise.
        """
        import builtins

        real_import = builtins.__import__

        def _fail(name, *a, **kw):
            if name == "requests":
                raise ImportError("no requests")
            return real_import(name, *a, **kw)

        monkeypatch.delitem(sys.modules, "requests", raising=False)
        monkeypatch.setattr(builtins, "__import__", _fail)
        assert enhancer.post_with_retry("https://api.example/x", label="t") is None


class TestGeminiModelIsConfigurable:
    def test_model_id_comes_from_config_not_a_literal(self):
        """gemini-2.0-flash was hardcoded in the URL and silently 404'd.

        The whole point of the fix is that swapping the model never again
        requires a code change, so the literal must be gone from the source.
        """
        src = (REPO_ROOT / "scripts" / "news" / "enhancer.py").read_text("utf-8")
        # Code lines only — the comments name the retired ID on purpose, to
        # explain why it must not come back.
        code = "\n".join(
            ln for ln in src.splitlines() if not ln.lstrip().startswith("#")
        )
        assert "gemini-2.0-flash" not in code, (
            "a retired Gemini model ID is hardcoded again; use "
            "AUTO_PUBLISH_GEMINI_MODEL via _cfg._GEMINI_MODEL"
        )
        assert "_cfg._GEMINI_MODEL" in src, (
            "the Gemini REST URL no longer reads the configurable model id"
        )
