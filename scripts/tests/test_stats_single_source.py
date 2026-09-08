#!/usr/bin/env python3
"""Guard: the stats block's total is derived from the category counts.

The plan that led here assumed this needed building. It did not — measured
2026-09-08, BOTH digest generators already derive one number from the other and
assert it:

* security mode — ``total = sum(stats.values())`` at the call site, and
  ``_format_stats_block`` re-checks with ``assert shown_sum == total``.
* tech-blog mode — ``assert group_sum == total`` before the block is written.

That is why the corpus has been clean since 2026-05 while 23 posts from
2026-02..04 are inconsistent: those predate the helper. A visible fingerprint —
``_format_stats_block`` SKIPS a zero-count category, and 2026-03-12 prints
``보안 0개 / AI-ML 0개 / 클라우드 0개 / DevOps 0개``, so it cannot have come from
this code path.

So this file does not add an invariant; it pins the two that exist, because
nothing else did. Both are load-bearing for promoting
``validate_stats_consistency`` to a blocking gate, and both are one refactor
away from silently disappearing.

A caveat worth writing down rather than "fixing": these are ``assert``
statements, which ``python -O`` / ``PYTHONOPTIMIZE`` strips. Neither is set in
this repo (checked: no occurrence in .github/workflows or scripts), so they are
live in production today. If that ever changes, the invariant is gone with no
error — and this test would still pass, because pytest does not run optimised.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from scripts.news.content_generator import _format_stats_block

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = REPO_ROOT / "scripts" / "news" / "content_generator.py"


def test_the_helper_refuses_an_inconsistent_total():
    """The security-mode invariant, exercised rather than read."""
    with pytest.raises(AssertionError, match="Stats block category sum mismatch"):
        _format_stats_block({"security": 3, "ai": 2}, 10)


def test_the_helper_accepts_a_consistent_total():
    """Control: the test above must not be passing because everything raises."""
    block = _format_stats_block({"security": 3, "ai": 2}, 5)
    assert block.splitlines()[0] == "- **총 뉴스 수**: 5개"
    assert "- **보안 뉴스**: 3개" in block
    assert "- **AI/ML 뉴스**: 2개" in block


def test_unknown_categories_are_rolled_into_기타_rather_than_dropped():
    """A dropped category would be an inconsistency the assert then catches;
    rolling it up is what keeps the sum honest."""
    block = _format_stats_block({"security": 2, "weird": 3}, 5)
    assert "- **기타 뉴스**: 3개" in block


def test_a_zero_count_category_is_omitted():
    """Pins the fingerprint that dates the 23 grandfathered posts.

    They print explicit zero lines, which this code path cannot produce — that
    is the evidence they predate the single-sourcing rather than escaping it.
    """
    block = _format_stats_block({"security": 5, "ai": 0}, 5)
    assert "AI/ML" not in block


def _generator_source() -> str:
    return GENERATOR.read_text(encoding="utf-8")


def test_the_security_mode_total_is_derived_not_passed_in():
    source = _generator_source()
    assert re.search(r"^\s*total = sum\(stats\.values\(\)\)", source, re.M), (
        "the security-mode total is no longer derived from the category stats, "
        "so the two numbers can disagree again"
    )


def test_the_tech_blog_mode_invariant_is_present():
    source = _generator_source()
    assert re.search(r"assert group_sum == total", source), (
        "the tech-blog invariant is gone; its stats block interpolates `total` "
        "and four `len(topic_groups[...])` independently, so nothing would "
        "notice an item counted twice or not at all"
    )


def test_both_stats_blocks_are_still_the_only_two():
    """A third writer would need its own invariant.

    Pinned because the two guards above are anchored per call site: a new
    generator mode copying the block would be covered by neither.
    """
    source = _generator_source()
    assert source.count("**수집 통계:**") == 2, (
        f"found {source.count('**수집 통계:**')} stats blocks; a new one needs a "
        "derived total and an invariant of its own, plus a guard here"
    )
