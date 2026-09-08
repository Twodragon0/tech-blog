#!/usr/bin/env python3
"""Ratchet: stats-block inconsistencies in the corpus must only go down.

``validate_stats_consistency`` checks that the per-category counts in a
digest's ``**수집 통계:**`` block sum to its stated ``총 뉴스 수``. It is an
INTERNAL consistency claim about that block, not a claim about the body —
measured: for all 23 violating posts the body's item count (``### N.N``) matches
neither the category sum nor the stated total (0/23 either way), because the
body only writes up a capped subset.

``run_qa_gate`` runs at publish time on new content only, so a text baseline
file would be a dormant artifact. This test is the baseline: it sweeps every
published digest on every pytest run, and ``MAX_VIOLATIONS`` can only be
lowered.

Why the 23 are NOT repaired here
--------------------------------
Neither side is recoverable ground truth, so any "fix" would be a guess written
into reader-visible numbers:

* Recomputing the total from the categories would UNDERSTATE the collected
  count. The mechanism is ``MAX_NEWS_PER_CATEGORY = 5``: those older posts
  reported capped per-category counts against an uncapped total, which is why
  ``stated - sum`` is ``{+5: 22, -5: 1}`` regardless of post size.
  (Verified not to be a parser artifact — the regex reads all five category
  lines, e.g. 2026-03-12 genuinely lists ``0+0+0+0+5`` against a total of 10.)
* Recomputing the categories needs the original collection data, which is gone
  for 2026-02..04.
* A third statement cannot arbitrate: the title's ``(N건)`` matches neither the
  total nor the category sum in 0/23, and even among the 160 consistent posts it
  matches the total only 107 times — it is a fourth number with its own meaning.

Verdict and full measurements:
.omc/plans/validate-stats-consistency-promotion-2026-09-08.md
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.news.qa_gate import validate_stats_consistency

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS = REPO_ROOT / "_posts"

# Measured 2026-09-08: 160 consistent, 23 violating, all in 2026-02 (1),
# 03 (14) and 04 (8). Nothing since 2026-05 — the generator has emitted the
# total and the categories from one computation since then (see
# test_stats_single_source.py), so a new entry is a regression.
MAX_VIOLATIONS = 23

GRANDFATHERED = frozenset(
    {
        "2026-02-17-Tech_Security_Weekly_Digest_AI_Agent_Cloud_Security.md",
        "2026-03-11-Tech_Security_Weekly_Digest_AI_Agent_Data_Malware.md",
        "2026-03-12-Tech_Security_Weekly_Digest_AI_Malware_AWS_Patch.md",
        "2026-03-16-Tech_Security_Weekly_Digest_AI_Agent_Open-Source_Update.md",
        "2026-03-17-Tech_Security_Weekly_Digest_Malware_AI_AWS_Botnet.md",
        "2026-03-18-Tech_Security_Weekly_Digest_AI_AWS_Data_Ransomware.md",
        "2026-03-19-Tech_Security_Weekly_Digest_Zero-Day_CVE_Ransomware_Patch.md",
        "2026-03-20-Tech_Security_Weekly_Digest_Malware_Data_Security_Threat.md",
        "2026-03-21-Tech_Security_Weekly_Digest_Security_CVE_AI_Malware.md",
        "2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.md",
        "2026-03-23-Tech_Security_Weekly_Digest_Ransomware.md",
        "2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI.md",
        "2026-03-25-Tech_Security_Weekly_Digest_AI_LLM_Malware_Agent.md",
        "2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day.md",
        "2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.md",
        "2026-04-01-Tech_Security_Weekly_Digest_Zero-Day_Go_AI_AWS.md",
        "2026-04-02-Tech_Security_Weekly_Digest_AI_Malware.md",
        "2026-04-03-Tech_Security_Weekly_Digest_CVE_Patch_AWS_AI.md",
        "2026-04-04-Tech_Security_Weekly_Digest_Go_AI_Data_Security.md",
        "2026-04-05-Tech_Security_Weekly_Digest_AWS_AI_Security_Malware.md",
        "2026-04-06-Tech_Security_Weekly_Digest_Patch_AI.md",
        "2026-04-10-Tech_Security_Weekly_Digest_AI_Malware_Go_Agent.md",
        "2026-04-11-Tech_Security_Weekly_Digest_AI_Go_CVE_Update.md",
    }
)


def _violations() -> dict:
    offenders = {}
    for post in sorted(POSTS.glob("*Weekly_Digest*.md")):
        issues = validate_stats_consistency(post.read_text(encoding="utf-8"))
        if issues:
            offenders[post.name] = issues
    return offenders


def test_the_corpus_has_digest_posts_to_scan():
    """Canary: an empty glob makes every assertion below vacuously true."""
    assert len(list(POSTS.glob("*Weekly_Digest*.md"))) > 100


def test_the_rule_actually_reads_a_stats_block():
    """Canary on the extractor.

    ``validate_stats_consistency`` returns [] when it cannot find the block, so
    a regex that stopped matching would report a spotless corpus. Most digests
    carry the block, so a low count means the extractor broke, not that the
    posts changed.
    """
    with_block = sum(
        1
        for p in POSTS.glob("*Weekly_Digest*.md")
        if re.search(r"\*\*수집 통계:\*\*", p.read_text(encoding="utf-8"))
    )
    assert with_block > 150, (
        f"only {with_block} digests appear to have a 수집 통계 block; the "
        "extractor probably stopped matching"
    )


def test_violations_do_not_grow():
    offenders = _violations()
    assert len(offenders) <= MAX_VIOLATIONS, (
        f"stats-block inconsistencies grew to {len(offenders)} "
        f"(> {MAX_VIOLATIONS}). The generator derives the total from the "
        "category counts, so a new one means that single source was broken:\n  "
        + "\n  ".join(f"{k}: {v[0]}" for k, v in offenders.items())
    )


def test_no_grandfathered_entry_is_stale():
    """A repaired post must lower the constant in the same commit.

    Otherwise the ratchet drifts: the constant stays at 23 while the real
    number is 21, and the next two regressions land unnoticed.
    """
    stale = sorted(GRANDFATHERED - set(_violations()))
    assert not stale, (
        "these posts no longer violate — drop them from GRANDFATHERED and lower "
        "MAX_VIOLATIONS in the same commit:\n  " + "\n  ".join(stale)
    )


def test_every_violation_is_grandfathered():
    fresh = sorted(set(_violations()) - GRANDFATHERED)
    assert not fresh, (
        "new stats-block inconsistency, which the generator's own invariant "
        "should have made impossible:\n  " + "\n  ".join(fresh)
    )
