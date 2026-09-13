#!/usr/bin/env python3
"""Floor guard: the template-branch suite must not shrink.

Why this file exists
--------------------
``CLAUDE.md`` §Template Branch Rules carried the sentence "테스트 현황 …
`test_news_templates.py` **439건**" and it went stale three times in a row —
``287`` (a phantom number belonging to neither the file nor the suite), then
``5083 + 5`` (2026-09-01), then ``5541 + 5`` (2026-09-10) against a measured
``5706`` on 2026-09-13. The previous revision's answer was to write "그러니 이
수치를 읽고 인용하지 말고 다시 재라" in bold; the commit that wrote that warning
was itself the start of the third staleness. A warning is not a mechanism.

So the number moved out of the document and into here. The document now points
at this file instead of restating a count, and the count it does keep — 439 —
is the one that actually stays put: it was 439 on 2026-09-01, 439 on 2026-09-10
and 439 on 2026-09-13, across a whole-suite growth of +623.

Direction
---------
Asserted as a FLOOR, never as an exact value — the same rule
``scripts/tests/test_ci_coverage_floor_guard.py`` already applies to the two
coverage floors ("Numbers are asserted as 'not lowered', never as an exact
value, so improving coverage does not trip it"). Adding template-branch tests
must never turn this red; deleting a batch of them must.

What this does NOT claim
------------------------
It cannot see "a branch was added without a test" — that is
``TestBranchPriorityConflicts`` and the coverage floors. It catches the other
direction: coverage quietly disappearing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_SUITE = Path(__file__).with_name("test_news_templates.py")

# Measured 439 on 2026-09-01, 2026-09-10 and 2026-09-13. The floor sits below
# that with room for a refactor that merges a few parametrized cases, and not
# so far below that a wholesale deletion slips through.
BRANCH_TEST_FLOOR = 430


def _collected_count() -> int:
    """Number of test cases pytest collects from the template-branch suite.

    Collection, not execution: this must stay cheap enough to live in the
    normal suite, and a failing template test is already reported by that test
    rather than by this guard.
    """
    import subprocess
    import sys

    proc = subprocess.run(
        # --color=no matters: pytest wraps the summary in ANSI codes when the
        # parent run is coloured, and `int()` on "\x1b[32m439" is a confusing
        # failure that looks like a collection problem.
        [
            sys.executable,
            "-m",
            "pytest",
            str(TEMPLATE_SUITE),
            "--collect-only",
            "-q",
            "--color=no",
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    # Last non-empty line is pytest's summary, e.g. "439 tests collected in 0.59s".
    for line in reversed(proc.stdout.splitlines()):
        line = line.strip()
        if "collected" in line:
            return int(line.split()[0])
    raise AssertionError(
        "could not read a collection count from pytest.\n"
        f"stdout tail: {proc.stdout[-600:]!r}\nstderr tail: {proc.stderr[-600:]!r}"
    )


def test_template_suite_exists():
    """Canary: a rename must fail loudly rather than pass vacuously."""
    assert TEMPLATE_SUITE.is_file(), f"{TEMPLATE_SUITE} not found"


def test_template_branch_coverage_does_not_shrink():
    count = _collected_count()
    assert count >= BRANCH_TEST_FLOOR, (
        f"test_news_templates.py collects {count} cases, below the floor of "
        f"{BRANCH_TEST_FLOOR}. Template branches are added without tests unless "
        "something objects — this is that something. Lower the floor only with "
        "a reason in the PR body."
    )


def test_the_floor_is_not_set_above_reality():
    """A floor you cannot meet is a floor someone deletes.

    Pins the other direction: the constant must stay a floor, not creep up to
    the current value and turn every added-or-removed test into a doc edit —
    which is the failure this whole file exists to end.
    """
    count = _collected_count()
    assert BRANCH_TEST_FLOOR <= count, "floor exceeds the live count"
    assert BRANCH_TEST_FLOOR >= count - 100, (
        f"the floor ({BRANCH_TEST_FLOOR}) has drifted {count - BRANCH_TEST_FLOOR} "
        "cases below the live count and no longer catches a meaningful deletion."
    )


def test_claude_md_points_at_this_guard_instead_of_restating_a_total():
    """The document must not grow a whole-suite count back.

    That number is what went stale three times. It changes no reader's
    behaviour, so the fix was to delete it rather than to keep refreshing it.
    """
    text = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "test_news_templates_floor_guard.py" in text, (
        "CLAUDE.md no longer points at this guard, so the count it states has "
        "nothing standing behind it again."
    )
    stale = [n for n in ("5083", "5541", "5706") if n in text]
    assert not stale, (
        f"CLAUDE.md carries whole-suite test totals again: {stale}. Those are the "
        "exact values that went stale three times; measure with "
        "`python3 -m pytest scripts/tests/ -q | tail -2` instead."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
