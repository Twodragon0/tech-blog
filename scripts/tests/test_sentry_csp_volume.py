#!/usr/bin/env python3
"""Guard the exit-code asymmetry in scripts/sentry_csp_volume.py.

The script reports CSP report-channel volume from Sentry. Its exit codes encode
a deliberate asymmetry that is easy to "simplify" away later:

  - missing secret            -> 1  (SENTRY_* are configured; absence = regression)
  - HTTP 401/403              -> 0  (standing scope gap; fail-closed here would
                                     make a daily cron permanently red, which
                                     gets muted — see the module docstring)
  - any other API failure     -> 2  ("could not measure" != "nothing was wrong")

Collapsing 401/403 into the generic error branch turns the nightly Sentry
healthcheck red every night until someone grants the token `event:read`. Making
every failure exit 0 hides real breakage. These tests pin both directions.
"""

from __future__ import annotations

import email.message
import importlib.util
import json
import urllib.error
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "sentry_csp_volume.py"


def _load():
    spec = importlib.util.spec_from_file_location("sentry_csp_volume", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def mod():
    return _load()


@pytest.fixture
def creds(monkeypatch):
    monkeypatch.setenv("SENTRY_AUTH_TOKEN", "dummy-not-a-real-token")
    monkeypatch.setenv("SENTRY_ORG", "example-org")
    monkeypatch.setenv("SENTRY_PROJECT", "example-project")


def _http_error(code: int) -> urllib.error.HTTPError:
    # hdrs must be a Message, not None: HTTPError stores it verbatim (fp=None
    # skips addinfourl init), and only `.code` is read by the code under test.
    return urllib.error.HTTPError(
        url="https://sentry.io/api/0/",
        code=code,
        msg="test",
        hdrs=email.message.Message(),
        fp=None,
    )


def test_missing_secret_exits_1(mod, monkeypatch):
    for key in ("SENTRY_AUTH_TOKEN", "SENTRY_ORG", "SENTRY_PROJECT"):
        monkeypatch.delenv(key, raising=False)
    assert mod.main() == 1


def test_missing_secret_never_prints_values(mod, monkeypatch, capsys):
    monkeypatch.setenv("SENTRY_AUTH_TOKEN", "super-secret-value")
    monkeypatch.delenv("SENTRY_ORG", raising=False)
    monkeypatch.delenv("SENTRY_PROJECT", raising=False)
    mod.main()
    captured = capsys.readouterr()
    assert "super-secret-value" not in (captured.out + captured.err)


@pytest.mark.parametrize("code", [401, 403])
def test_authorization_failure_stays_green_but_says_it_measured_nothing(
    mod, creds, monkeypatch, capsys, code
):
    monkeypatch.setattr(
        mod, "_fetch", lambda *_a, **_k: (_ for _ in ()).throw(_http_error(code))
    )
    assert mod.main() == 0
    out = capsys.readouterr().out
    # A green run that produced no data must not read as "volume is zero".
    assert "MEASURED NOTHING" in out
    assert str(code) in out
    assert "event:read" in out
    assert "::warning::" in out


@pytest.mark.parametrize("code", [400, 404, 429, 500, 503])
def test_other_http_errors_are_fail_closed(mod, creds, monkeypatch, code):
    monkeypatch.setattr(
        mod, "_fetch", lambda *_a, **_k: (_ for _ in ()).throw(_http_error(code))
    )
    assert mod.main() == 2


def test_network_failure_is_fail_closed(mod, creds, monkeypatch):
    def boom(*_a, **_k):
        raise urllib.error.URLError("no route to host")

    monkeypatch.setattr(mod, "_fetch", boom)
    assert mod.main() == 2


def test_unexpected_response_shape_is_fail_closed(mod, creds, monkeypatch):
    monkeypatch.setattr(mod, "_fetch", lambda *_a, **_k: {"detail": "not a list"})
    assert mod.main() == 2


def test_successful_report_buckets_and_totals(mod, creds, monkeypatch, capsys):
    issues = [
        {
            "count": "10",
            "title": "CSP: script-src-elem",
            "culprit": "chrome-extension://x/a.js",
        },
        {"count": 5, "title": "CSP: script-src-elem inline", "culprit": "about"},
        {
            "count": 2,
            "title": "CSP: connect-src",
            "culprit": "https://tech.2twodragon.com/",
        },
    ]
    monkeypatch.setattr(mod, "_fetch", lambda *_a, **_k: issues)
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "| extension | 10 |" in out
    assert "| translate | 5 |" in out
    assert "| first-party | 2 |" in out
    assert "Total CSP events: **17**" in out


def test_full_page_is_declared_a_floor_not_a_total(mod, creds, monkeypatch, capsys):
    # No silent caps: hitting the API page limit must be stated, or the number
    # reads as complete when it is not.
    issues = [{"count": 1, "title": "CSP", "culprit": "https://example.com/"}] * 100
    monkeypatch.setattr(mod, "_fetch", lambda *_a, **_k: issues)
    assert mod.main() == 0
    assert "floor" in capsys.readouterr().out


def test_zero_events_does_not_claim_the_channel_is_quiet(
    mod, creds, monkeypatch, capsys
):
    monkeypatch.setattr(mod, "_fetch", lambda *_a, **_k: [])
    assert mod.main() == 0
    out = capsys.readouterr().out
    assert "inbound filters" in out


def test_malformed_count_does_not_crash(mod, creds, monkeypatch, capsys):
    issues = [{"count": "n/a", "title": "CSP", "culprit": "https://example.com/"}]
    monkeypatch.setattr(mod, "_fetch", lambda *_a, **_k: issues)
    assert mod.main() == 0
    assert "Total CSP events: **0**" in capsys.readouterr().out


def test_classify_buckets(mod):
    assert (
        mod.classify({"culprit": "chrome-extension://abc/injected.js"}) == "extension"
    )
    assert mod.classify({"culprit": "moz-extension://abc/injected.js"}) == "extension"
    assert mod.classify({"title": "CSP: inline", "culprit": "about"}) == "translate"
    assert mod.classify({"culprit": "https://tech.2twodragon.com/"}) == "first-party"


def test_docstring_records_why_401_403_is_not_fail_closed(mod):
    # The exemption is only defensible with its reason attached. If someone
    # strips the rationale, the next reader sees an unexplained green-on-error.
    doc = mod.__doc__ or ""
    assert "401/403" in doc
    assert "event:read" in doc
    assert "permanently red" in doc


def test_json_decode_error_is_fail_closed(mod, creds, monkeypatch):
    def boom(*_a, **_k):
        raise json.JSONDecodeError("bad", "", 0)

    monkeypatch.setattr(mod, "_fetch", boom)
    assert mod.main() == 2
