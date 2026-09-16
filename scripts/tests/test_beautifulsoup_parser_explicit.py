#!/usr/bin/env python3
"""Guard: every ``BeautifulSoup(...)`` call must name its parser.

Why this exists
---------------
``lxml`` was removed from ``scripts/requirements.txt`` on 2026-09-16 as a dead
declaration: nothing imported it, no installed package required it, and all 15
``BeautifulSoup(`` call sites passed ``"html.parser"`` explicitly. That last fact
is what made the removal safe, because bs4 does **not** default to html.parser —
it picks the *best available* parser, preferring lxml when lxml happens to be
importable.

So a call written as ``BeautifulSoup(html)`` is environment-dependent by
construction: it parses with lxml on a machine where some unrelated package
pulled lxml in, and with html.parser on one where nothing did. The two differ on
malformed markup, which is most of what a news scraper sees. Before the removal
that hazard was masked (lxml was always installed); after it, the same code can
silently parse differently in CI and on a developer's machine.

Naming the parser removes the dependence entirely, which the codebase already
did everywhere. This keeps it that way — the convention was previously held by
nothing but consistency.

If you deliberately want lxml, re-declare it in requirements AND pass "lxml"
explicitly at the call site; do not rely on auto-selection.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SEARCH_DIRS = ("scripts", "api")

# `BeautifulSoup(` followed by its first argument, then a comma (a second
# positional/keyword arg = a named parser) or `)` (no parser named).
_CALL_RE = re.compile(r"BeautifulSoup\(\s*([^)]*?)\s*\)", re.DOTALL)


_SELF = Path(__file__).resolve()


def _python_files() -> list[Path]:
    # This module is excluded: its own docstring and assertion message spell
    # `BeautifulSoup(markup)` to describe the defect, and the first draft
    # reported those three as violations. A scanner that reads the file
    # describing the rule will always find the rule's own counter-example.
    out: list[Path] = []
    for d in SEARCH_DIRS:
        root = REPO_ROOT / d
        if not root.is_dir():
            continue
        out += [
            p
            for p in root.rglob("*.py")
            if "_archive" not in p.parts and p.resolve() != _SELF
        ]
    return sorted(out)


def _calls() -> list[tuple[Path, int, str]]:
    found: list[tuple[Path, int, str]] = []
    for path in _python_files():
        text = path.read_text(encoding="utf-8")
        for m in _CALL_RE.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            found.append((path, line, m.group(1)))
    return found


def test_scanner_is_not_vacuous() -> None:
    """A scanner that finds no calls would pass this file trivially forever."""
    calls = _calls()
    assert len(calls) >= 10, (
        f"Only {len(calls)} BeautifulSoup call(s) found — the codebase had 15 on "
        "2026-09-16. Either they moved (update SEARCH_DIRS) or _CALL_RE stopped "
        "matching; a silent zero makes the guard below vacuous."
    )


def test_every_beautifulsoup_call_names_a_parser() -> None:
    """No positional-only ``BeautifulSoup(markup)`` — bs4 would auto-select.

    bs4 prefers lxml when importable and falls back to html.parser otherwise, so
    an unnamed parser makes output depend on which packages happen to be
    installed. `scripts/requirements.txt` no longer declares lxml, which means
    the same call can resolve differently in CI and locally.
    """
    offenders = [
        f"{path.relative_to(REPO_ROOT)}:{line}  BeautifulSoup({args[:60]})"
        for path, line, args in _calls()
        if "," not in args
    ]
    assert offenders == [], (
        "BeautifulSoup called without naming a parser:\n  "
        + "\n  ".join(offenders)
        + '\n\nPass "html.parser" explicitly (what every other call site does). '
        "bs4 auto-selects lxml when it is importable, so an unnamed parser "
        "silently changes behaviour with the installed package set."
    )
