#!/usr/bin/env python3
"""Regression guard: an API key must never be built into a request URL.

Why this exists
---------------
`scripts/news/enhancer.py` used to call the Gemini REST API as
``…:generateContent?key={_GEMINI_API_KEY}``. That makes the URL itself a secret,
and a URL is far leakier than a header:

- ``requests`` stringifies the full URL into its exception messages. Measured:

      >>> requests.post("https://127.0.0.1:9/...?key=<KEY>", timeout=2)
      ConnectionError: HTTPSConnectionPool(host='127.0.0.1', port=9):
        Max retries exceeded with url: /...?key=<KEY> (Caused by ...)

  and `enhancer.py` logged exactly that object (``logging.warning(f"… {e}")``).
  This repo is PUBLIC, so Actions logs are public.
- CodeQL's `py/clear-text-logging-sensitive-data` flagged the neighbouring
  *response body* log and it was dismissed as a false positive. That dismissal
  was correct about the body — a bad key answers "API key not valid. Please
  pass a valid API key." and never echoes the key. What nobody checked was the
  exception line two lines below, which is the real exposure.

The lesson, and why this is a path-shaped guard rather than a log-shaped one:
masking at each log call is a discipline you must remember every time. Keeping
the key out of the URL removes the whole class — exceptions, redirects, proxy
logs, Referer, retry traces.

Google accepts the header form; verified against the live endpoint with a
control:

    header x-goog-api-key + fake key -> 400 "API key not valid"      (header read)
    no key at all                    -> 403 "unregistered callers"   (control)

Direction: ABSENCE assertion. Adding a key back into a URL trips it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

# `key=` immediately after ? or & followed by an interpolation of something
# key-shaped. Deliberately narrow: a literal `?key=` in a docstring or a test
# fixture is not a finding, an f-string splicing a credential is.
_KEY_IN_URL = re.compile(
    r"""[?&]key=\{[^}]*(?:KEY|TOKEN|SECRET|_key|_token)[^}]*\}""",
    re.IGNORECASE,
)

# The masking helper and its own tests legitimately contain the pattern as data.
_EXEMPT = {
    "scripts/lib/security.py",
    "scripts/tests/test_lib_security.py",
    "scripts/tests/test_api_key_not_in_url.py",
}


def _python_sources() -> list[Path]:
    """Every Python source that must not embed a credential in a URL.

    Exempt files are filtered out HERE rather than skipped inside the test. A
    skip whose reason is a static fact about the repo reports nothing and is
    rejected by test_skip_path_policy.py — correctly: if the exemption list
    goes stale, an absent parametrize case is honest whereas a green skip is
    not.
    """
    out: list[Path] = []
    for d in ("scripts", "api"):
        root = REPO_ROOT / d
        if root.is_dir():
            out.extend(p for p in root.rglob("*.py") if "__pycache__" not in p.parts)
    return sorted(
        p for p in out if p.relative_to(REPO_ROOT).as_posix() not in _EXEMPT
    )


def _code_lines(path: Path) -> list[tuple[int, str]]:
    """Line number + text, comment-only lines dropped.

    The fixed call sites explain the hazard in prose and name the old
    `?key=<API key>` shape on purpose. Matching raw text would flag the
    explanation and, worse, would keep passing if someone deleted the comment
    while reintroducing the bug.
    """
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return [
        (i + 1, ln) for i, ln in enumerate(lines) if not ln.lstrip().startswith("#")
    ]


@pytest.mark.parametrize("path", _python_sources(), ids=lambda p: str(p.name))
def test_no_credential_interpolated_into_a_url(path: Path):
    rel = path.relative_to(REPO_ROOT).as_posix()
    hits = [(n, ln.strip()) for n, ln in _code_lines(path) if _KEY_IN_URL.search(ln)]
    assert not hits, (
        f"{rel} builds a credential into a request URL: {hits}\n"
        "A URL carrying a key leaks through requests' exception strings (which "
        "this repo logs, publicly). Send it as a header instead — Gemini "
        "accepts x-goog-api-key."
    )


class TestTheFixedCallSitesUseHeaders:
    """Pin the four sites that were converted, so none silently reverts."""

    @pytest.mark.parametrize(
        "rel",
        [
            "scripts/news/enhancer.py",
            "scripts/ai_improve_posts.py",
            "scripts/generate_post_images.py",
            "scripts/generate_missing_diagrams.py",
        ],
    )
    def test_site_sends_the_key_as_a_header(self, rel: str):
        src = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "x-goog-api-key" in src, (
            f"{rel} no longer sends the Gemini key as a header. If the call was "
            "removed entirely, drop it from this list in the same commit and say "
            "why; otherwise the key is back in the URL."
        )
