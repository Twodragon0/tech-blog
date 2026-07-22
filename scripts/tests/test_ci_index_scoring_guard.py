"""CI config regression guard — monthly-index genre scoring vs the pre-commit floor.

Invariant locked here (OWASP CICD-SEC-1 / NIST SSDF PW.4):

  Every monthly-index aggregator post must score >= the pre-commit quality
  gate's ``FAIL_BELOW`` value, so that editing/staging an index page never
  hard-blocks a commit.

Why this guard exists (concrete incident):
  Before genre-aware scoring, monthly-index pages scored 49/53/53 under the
  digest-only rubric. ``scripts/pre-commit-quality-check.sh`` runs
  ``validate_post_quality.py --fail-below 60`` with ``set -e`` on every staged
  ``_posts/*.md``, so any edit to an index page hard-FAILED the commit. The
  ``is_index_post`` / ``_score_index`` genre branch in validate_post_quality.py
  lifted them to 87/100/100. If that branch is silently removed or broken, the
  index pages drop below 60 again and the pre-commit gate starts blocking edits
  to them — a regression invisible until someone happens to touch an index page.

This test ties the two together: it reads the ACTUAL ``FAIL_BELOW`` from the
pre-commit script and asserts every real index post clears it under the current
scorer. Removing the genre branch makes this fail loudly in CI.

Direction:
  * ``FAIL_BELOW`` is pinned (==) to its known value; an intentional change must
    update ``EXPECTED_FAIL_BELOW`` here (forces a conscious review).
  * index scores use ``>=`` the gate (ratchet-up stays green).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PRECOMMIT = REPO_ROOT / "scripts" / "pre-commit-quality-check.sh"
POSTS_DIR = REPO_ROOT / "_posts"
SCRIPTS_DIR = REPO_ROOT / "scripts"

# The pre-commit hard floor this guard is bound to. If the hook intentionally
# changes its FAIL_BELOW, update this constant in the same PR (conscious review).
EXPECTED_FAIL_BELOW = 60

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_post_quality import is_index_post, validate_post  # noqa: E402


def _read_fail_below() -> int:
    """Extract the FAIL_BELOW= value from the pre-commit quality hook."""
    text = PRECOMMIT.read_text(encoding="utf-8")
    m = re.search(r"^\s*FAIL_BELOW=(\d+)", text, re.MULTILINE)
    assert m, "FAIL_BELOW= not found in pre-commit-quality-check.sh"
    return int(m.group(1))


def _index_posts() -> list[Path]:
    return [
        p
        for p in sorted(POSTS_DIR.glob("*.md"))
        if is_index_post(p.read_text(encoding="utf-8"), p.name)
    ]


def test_precommit_hook_exists():
    assert PRECOMMIT.is_file(), f"{PRECOMMIT} not found (moved/renamed?)"


def test_fail_below_pinned():
    """The pre-commit floor must stay at its reviewed value.

    If you intentionally change FAIL_BELOW in the hook, update
    EXPECTED_FAIL_BELOW here so the change is reviewed alongside the gate.
    """
    assert _read_fail_below() == EXPECTED_FAIL_BELOW, (
        f"pre-commit FAIL_BELOW changed from {EXPECTED_FAIL_BELOW}; "
        "if intentional, update EXPECTED_FAIL_BELOW in this guard."
    )


def test_index_posts_detected():
    """Sanity: the genre detector still finds the monthly-index pages.

    A vacuous pass (0 index posts → nothing to check) would hide a broken
    detector, so require at least one and that each is a *Monthly_Index* file.
    """
    idx = _index_posts()
    assert idx, "no monthly-index posts detected — is_index_post regressed?"
    for p in idx:
        assert "Monthly_Index" in p.name, f"unexpected index detection: {p.name}"


@pytest.mark.parametrize(
    "post", _index_posts(), ids=lambda p: p.name
)
def test_index_post_clears_precommit_floor(post):
    """Each monthly-index post must score >= the pre-commit FAIL_BELOW.

    Removing/breaking the genre branch drops these to 49/53 (<60) and trips
    this — the whole point of the guard.
    """
    floor = _read_fail_below()
    result = validate_post(post)
    total = result["total"]
    assert total >= floor, (
        f"{post.name} scores {total} < pre-commit floor {floor}: the "
        "monthly-index genre-scoring branch (is_index_post/_score_index) is "
        "missing or broken, which would hard-block commits editing index pages."
    )
