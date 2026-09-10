#!/usr/bin/env python3
"""Wiring guard: every ``scripts/seo_*.py`` must have a real call site.

Why this guard exists
---------------------
``seo_inject_related_links.py`` was written for the 2026-05-19 GSC orphan audit,
ran once by hand, and then had **zero call sites** — no workflow, no hook, no
publisher. Nothing failed, nothing went red, and internal linking simply froze
at that date. Measured 2026-09-10: posts carrying an outbound internal link went
34/34 in 2026-04 to 1/30 in 2026-06 and 2/30 in 2026-07, and 163 of 293 posts
(55%) had no inbound internal link at all.

A dead SEO script is invisible in exactly the way a dead gate is: the failure is
an absence, so no test and no CI job can notice it. The only thing that catches
it is asking "who calls this?" — which is what this file does, for the family
rather than for the one instance that prompted the audit.

Direction
---------
Presence assertion over the whole ``scripts/seo_*.py`` glob, so a NEW seo script
added without wiring trips it immediately rather than years later. Test files do
not count as call sites — importing a module to test it does not make it run in
production, and that is precisely how this one looked alive for four months.

If a script is intentionally one-off, it does not belong in ``scripts/seo_*.py``
under this glob; move it to ``scripts/dev/`` (out of scope here) or delete it
after the campaign, and say which in the PR.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
PUBLISHER = SCRIPTS / "auto_publish_news.py"

SEO_SCRIPTS = sorted(p.name for p in SCRIPTS.glob("seo_*.py"))

# Where a call site may legitimately live. Deliberately excludes
# scripts/tests/** — see the docstring.
_SEARCH_GLOBS = ("scripts/*.py", "scripts/**/*.py", ".github/workflows/*.yml")


def _call_sites(module: str) -> list[str]:
    """Files that reference ``module`` and are not itself or a test."""
    found: set[str] = set()
    for pattern in _SEARCH_GLOBS:
        for path in REPO_ROOT.glob(pattern):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel.startswith("scripts/tests/") or rel == f"scripts/{module}.py":
                continue
            try:
                if module in path.read_text(encoding="utf-8"):
                    found.add(rel)
            except (OSError, UnicodeDecodeError):
                continue
    return sorted(found)


def test_there_are_seo_scripts_to_check():
    """Canary: a rename that empties the glob must fail, not pass vacuously."""
    assert SEO_SCRIPTS, (
        "no scripts/seo_*.py found — this guard is now inspecting nothing. If "
        "they moved, update the glob in the same PR."
    )


@pytest.mark.parametrize("name", SEO_SCRIPTS)
def test_every_seo_script_has_a_non_test_call_site(name: str):
    module = name[:-3]
    sites = _call_sites(module)
    assert sites, (
        f"scripts/{name} has no call site outside scripts/tests/. That is the "
        "exact state seo_inject_related_links.py sat in from 2026-05-19 to "
        "2026-09-10 while internal linking decayed from 34/34 to 1/30 posts per "
        "month — a dead script raises no error, so nothing else can catch this. "
        "Wire it into the publish path or remove it."
    )


def test_both_known_seo_steps_run_on_the_publish_path():
    """The publisher is where these have to run: the cron commits with no hooks.

    Named explicitly (not just 'some call site') because the publish path is the
    only one that sees a post before it is pushed to main.
    """
    body = PUBLISHER.read_text(encoding="utf-8")
    for module in ("seo_diversify_excerpts", "seo_inject_related_links"):
        assert module in body, (
            f"{module} is no longer invoked from scripts/auto_publish_news.py. "
            "The daily digest would publish without it and nothing would fail."
        )


@pytest.mark.parametrize(
    "module", ["seo_diversify_excerpts", "seo_inject_related_links"]
)
def test_publish_path_invocation_actually_writes(module: str):
    """`apply=True` is what separates a real run from a dry run.

    Both helpers default to dry-run. Losing the flag leaves the import, the
    try/except and the log line in place while the post is never modified —
    a call site that reads as wired and does nothing.
    """
    body = PUBLISHER.read_text(encoding="utf-8")
    # The invocation lives a few lines below the import; scan the region after
    # the module name rather than a fixed line offset.
    at = body.index(module)
    region = body[at : at + 1600]
    assert re.search(r"apply=True", region), (
        f"the {module} call on the publish path no longer passes apply=True, so "
        "it computes a change and discards it. The log line would still print "
        "nothing and the post would ship unmodified."
    )
