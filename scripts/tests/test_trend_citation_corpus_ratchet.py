#!/usr/bin/env python3
"""Ratchet: the corpus's trend-citation violations must only ever go down.

``validate_trend_analysis`` runs at publish time on new content only — there is
no corpus-wide invocation of ``run_qa_gate``, so a text baseline file would be a
dormant artifact nobody reads. This test IS the baseline: it runs over every
published digest on every pytest invocation, and the constant below can only be
lowered.

The 4 grandfathered posts are genuine prose/table contradictions from
2026-03/04, all of the same shape — the prose names a trend the table does not
carry:

    2026-03-16-…AI_Bitcoin        블록체인 규제 리스크(5건)   row: 블록체인/규제(5건)
    2026-04-04-…Go_AI_Data…       AI 플랫폼 진화(2건)        row: AI 플랫폼(2건)
    2026-04-06-…Patch_AI          북한 연계 대형 해킹(1건)    no such row at all
    2026-04-08-…AI_CVE_Docker…    AI 플랫폼 확장(3건)        row: AI 플랫폼 & 비용(3건)

Three are a prettified label the generator no longer writes; the fourth cites a
trend that does not exist. Repairing the prose of four published posts is a
follow-up, not a blocker on the rule.

Everything from 2026-05 onward is clean, which is what makes this a ratchet
rather than a target.
"""

from __future__ import annotations

from pathlib import Path

from scripts.news.qa_gate import validate_trend_analysis

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS = REPO_ROOT / "_posts"

# Measured 2026-09-08: 169 of the 173 digests that carry both a trend table and
# a prose citation pass. Lower this when a post is repaired; raising it means a
# new contradiction shipped, which is a regression, not a grandfather.
MAX_VIOLATIONS = 4

GRANDFATHERED = frozenset(
    {
        "2026-03-16-Tech_Security_Weekly_Digest_AI_Bitcoin.md",
        "2026-04-04-Tech_Security_Weekly_Digest_Go_AI_Data_Security.md",
        "2026-04-06-Tech_Security_Weekly_Digest_Patch_AI.md",
        "2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.md",
    }
)


def _violations() -> dict:
    offenders = {}
    for post in sorted(POSTS.glob("*Weekly_Digest*.md")):
        issues = validate_trend_analysis(post.read_text(encoding="utf-8"))
        if issues:
            offenders[post.name] = issues
    return offenders


def test_the_corpus_has_digest_posts_to_scan():
    """Canary: an empty glob makes every assertion below vacuously true."""
    assert len(list(POSTS.glob("*Weekly_Digest*.md"))) > 100


def test_violations_do_not_grow():
    offenders = _violations()
    assert len(offenders) <= MAX_VIOLATIONS, (
        f"trend-citation violations grew to {len(offenders)} (> {MAX_VIOLATIONS}). "
        "A digest now cites a trend its own table does not carry:\n  "
        + "\n  ".join(f"{k}: {v[0]}" for k, v in offenders.items())
    )


def test_no_grandfathered_entry_is_stale():
    """A stale entry means a post was repaired and the count was not lowered.

    Without this the ratchet drifts: the constant stays at 4 while the real
    number is 2, and the next two regressions land unnoticed.
    """
    offenders = set(_violations())
    stale = sorted(GRANDFATHERED - offenders)
    assert not stale, (
        "these posts no longer violate — drop them from GRANDFATHERED and lower "
        f"MAX_VIOLATIONS to {len(offenders)} in the same commit:\n  "
        + "\n  ".join(stale)
    )


def test_every_violation_is_grandfathered():
    offenders = set(_violations())
    fresh = sorted(offenders - GRANDFATHERED)
    assert not fresh, (
        "new trend-citation contradiction(s), which the publish gate would have "
        "warned about at generation time:\n  " + "\n  ".join(fresh)
    )
