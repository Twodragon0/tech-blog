#!/usr/bin/env python3
"""An absent `gemini` binary must be latched, not rediscovered on every call.

Measured on the 2026-08-27 scheduled run (33043799857): 43 identical
``Gemini CLI error: [Errno 2] No such file or directory: 'gemini'`` warnings,
one per enhancement call, each paying a spawn that could not succeed.

Three things had to line up for that, and the fix only removes the third:

1. ``_gemini_available()`` returns True at the API-key check *before* it probes
   the CLI, so ``_GEMINI_AVAILABLE`` is left at ``None``.
2. ``_gemini_call`` gates the CLI attempt on ``is not False`` — ``None`` passes.
3. Nothing in the failure path ever set the flag.

The circuit breaker was not the missing guard and must not be pressed into the
role: the API fallback kept succeeding (0 API errors in that run), which resets
the consecutive-failure counter, so the breaker correctly never opened. A
missing binary is a permanent condition and needs its own latch; a transient
spawn error is not, and must NOT latch — that distinction is what
``test_transient_subprocess_error_does_not_latch`` pins.
"""

from __future__ import annotations

import subprocess

import pytest
from news import enhancer

# Take the config module off `enhancer` rather than importing it here.
# `enhancer.py` does `import scripts.news.config as _cfg`, so `news.config` and
# `scripts.news.config` are two distinct objects in sys.modules; patching the
# wrong one leaves the code reading untouched state and every assertion below
# measures nothing. The first draft of this file did exactly that and reported
# "0 spawns" — which reads like a passing latch, not like a broken test.
_cfg = enhancer._cfg


@pytest.fixture(autouse=True)
def _isolate_gemini_state(monkeypatch):
    """Give each test a clean, CLI-eligible starting state."""
    monkeypatch.setattr(_cfg, "_GEMINI_AVAILABLE", None, raising=False)
    monkeypatch.setattr(_cfg, "_GEMINI_CIRCUIT_OPEN", False, raising=False)
    monkeypatch.setattr(_cfg, "_GEMINI_CONSECUTIVE_FAILURES", 0, raising=False)
    monkeypatch.setattr(_cfg, "_GEMINI_API_KEY", "", raising=False)


def _count_spawns(monkeypatch, exc):
    """Run three _gemini_call()s where the spawn raises `exc`; count attempts."""
    calls = []

    def _fake_run(cmd, *a, **k):
        calls.append(cmd)
        raise exc

    monkeypatch.setattr(enhancer.subprocess, "run", _fake_run)
    for _ in range(3):
        enhancer._gemini_call("prompt")
    return calls


def test_missing_binary_is_latched_after_the_first_attempt(monkeypatch):
    calls = _count_spawns(
        monkeypatch, FileNotFoundError(2, "No such file or directory", "gemini")
    )
    assert len(calls) == 1, (
        f"the absent binary was spawned {len(calls)} times across 3 calls. It "
        "must be attempted once and then latched, which is the 43-spawn "
        "regression this test exists for."
    )
    assert _cfg._GEMINI_AVAILABLE is False


# With no API key the pre-existing circuit breaker opens after the second call
# (the failure counter is incremented twice per call in that configuration), so
# the spawn count is 2, not 3. That is untouched behaviour; asserting an exact 3
# here would be testing a number this change never promised. What matters is
# that the CLI was retried at all rather than latched off after the first error.
def test_transient_subprocess_error_does_not_latch(monkeypatch):
    """A one-off spawn failure must not disable the CLI for the whole run."""
    calls = _count_spawns(monkeypatch, subprocess.SubprocessError("transient"))
    assert len(calls) > 1, (
        "a transient error latched the CLI off after one attempt. Only "
        "FileNotFoundError means the binary is absent; everything else may "
        "succeed on the next call."
    )
    assert _cfg._GEMINI_AVAILABLE is not False


def test_timeout_does_not_latch(monkeypatch):
    calls = _count_spawns(monkeypatch, subprocess.TimeoutExpired("gemini", 35))
    assert len(calls) > 1
    assert _cfg._GEMINI_AVAILABLE is not False


def test_latching_does_not_disable_the_api_path(monkeypatch):
    """The behaviour that must NOT change: Gemini still answers, via the API.

    In the measured run the API path served all 43 calls successfully. Latching
    the CLI off is a noise/efficiency fix, so the API must still be reached —
    and reached on the very first call, not only after the latch.
    """
    monkeypatch.setattr(_cfg, "_GEMINI_API_KEY", "dummy-key", raising=False)

    def _fake_run(cmd, *a, **k):
        raise FileNotFoundError(2, "No such file or directory", "gemini")

    api_calls = []

    def _fake_api(prompt, timeout=20):
        api_calls.append(prompt)
        return "x" * 50  # >20 chars, so it counts as a success

    monkeypatch.setattr(enhancer.subprocess, "run", _fake_run)
    monkeypatch.setattr(enhancer, "_gemini_api_call", _fake_api)

    assert enhancer._gemini_call("first") == "x" * 50
    assert enhancer._gemini_call("second") == "x" * 50
    assert len(api_calls) == 2, "the API path stopped being used after the latch"
    assert _cfg._GEMINI_AVAILABLE is False


def test_successful_api_keeps_the_breaker_closed(monkeypatch):
    """Why the breaker was never the guard for this.

    A succeeding API call resets the consecutive-failure counter, so the
    breaker stays closed however many times the CLI is missing. That is
    correct, and it is exactly why the absent binary needs a separate latch.
    """
    monkeypatch.setattr(_cfg, "_GEMINI_API_KEY", "dummy-key", raising=False)
    monkeypatch.setattr(
        enhancer.subprocess,
        "run",
        lambda *a, **k: (_ for _ in ()).throw(
            FileNotFoundError(2, "No such file or directory", "gemini")
        ),
    )
    monkeypatch.setattr(enhancer, "_gemini_api_call", lambda p, timeout=20: "y" * 50)

    for _ in range(5):
        enhancer._gemini_call("p")

    assert _cfg._GEMINI_CIRCUIT_OPEN is False
    assert _cfg._GEMINI_CONSECUTIVE_FAILURES == 0
