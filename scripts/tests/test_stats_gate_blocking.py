#!/usr/bin/env python3
"""Guard: the stats-consistency gate blocks, heals first, and refuses to guess.

Promoted from advisory on 2026-09-08. What licensed it:

* the generator derives the total from the category counts and asserts it, so a
  violation means that single source was bypassed (pinned by
  ``test_stats_single_source.py``);
* nothing published since 2026-05 violates — the 23 grandfathered posts are all
  2026-02..04 and predate the helper (ratchet:
  ``test_stats_consistency_corpus_ratchet.py``);
* a repair exists that introduces no guess — re-derive the total from the
  category lines, the same direction the generator uses.

Only the stats rule was promoted. ``run_qa_gate`` as a whole stays advisory: it
also carries ``validate_trend_analysis`` and
``validate_sentence_completeness``, and this is the only one of the three with
both a clean recent corpus and a guess-free repair.

The load-bearing behaviour here is the REFUSAL. ``heal_stats_total`` declines
the capped shape instead of rewriting the total, because that shape is the
fingerprint of the historical defect — capped per-category counts against an
uncapped total — and "fixing" it would silently understate the collected count.
A refusal must block, not pass.
"""

from __future__ import annotations

import re
from pathlib import Path

import auto_publish_news as apn

from scripts.news.config import MAX_NEWS_PER_CATEGORY
from scripts.news.qa_gate import heal_stats_total, validate_stats_consistency

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLISHER = REPO_ROOT / "scripts" / "auto_publish_news.py"


def _block(total: int, *categories: int) -> str:
    lines = [f"- **총 뉴스 수**: {total}개"]
    labels = ["보안 뉴스", "AI/ML 뉴스", "클라우드 뉴스", "DevOps 뉴스"]
    for label, count in zip(labels, categories):
        lines.append(f"- **{label}**: {count}개")
    return "**수집 통계:**\n" + "\n".join(lines) + "\n"


def test_a_consistent_block_needs_no_heal():
    """Control: the assertions below must not pass because everything heals."""
    content = _block(6, 4, 2)
    assert validate_stats_consistency(content) == []
    assert heal_stats_total(content) is None


def test_an_inconsistent_total_is_rederived_from_the_categories():
    content = _block(10, 3, 2)
    assert validate_stats_consistency(content), "fixture is not a violation"
    healed = heal_stats_total(content)
    assert healed is not None
    assert "- **총 뉴스 수**: 5개" in healed
    assert validate_stats_consistency(healed) == []


def test_the_heal_only_touches_the_total_line():
    content = _block(10, 3, 2)
    healed = heal_stats_total(content)
    assert "- **보안 뉴스**: 3개" in healed
    assert "- **AI/ML 뉴스**: 2개" in healed
    assert healed.count("총 뉴스 수") == 1


def test_the_heal_refuses_the_capped_shape():
    """The fingerprint of the 23 historical violations.

    A category sitting exactly at MAX_NEWS_PER_CATEGORY means the counts may be
    capped while the total is not. Re-deriving would understate the collected
    count, so the heal declines and the caller blocks.
    """
    content = _block(10, MAX_NEWS_PER_CATEGORY, 0)
    assert validate_stats_consistency(content), "fixture is not a violation"
    assert heal_stats_total(content) is None, (
        "the heal rewrote a capped block, which understates the collected count"
    )


def test_the_heal_declines_when_there_is_no_stats_block():
    assert heal_stats_total("본문만 있는 포스트\n") is None


def test_a_real_grandfathered_post_is_refused_not_rewritten():
    """End-to-end on actual corpus content, not a synthetic fixture.

    2026-03-12 lists 0/0/0/0/5 against a total of 10 — capped shape, so the heal
    must decline. If it ever rewrote this, the ratchet's grandfathered set would
    start disagreeing with the corpus.
    """
    post = (
        REPO_ROOT
        / "_posts"
        / "2026-03-12-Tech_Security_Weekly_Digest_AI_Malware_AWS_Patch.md"
    )
    assert post.is_file(), f"{post.name} moved; re-anchor this test"
    content = post.read_text(encoding="utf-8")
    assert validate_stats_consistency(content), "the post no longer violates"
    assert heal_stats_total(content) is None


# --- wiring guards on the publisher ------------------------------------------


def _source() -> str:
    return PUBLISHER.read_text(encoding="utf-8")


def test_the_gate_is_registered_as_blocking_with_a_self_heal():
    entry = [
        e for e in apn.INLINE_PUBLISH_GATES if e[0] == "validate_stats_consistency"
    ]
    assert entry, "the promoted gate is not in INLINE_PUBLISH_GATES"
    _symbol, _canonical, blocking, self_heal = entry[0]
    assert blocking, "the registry still calls this advisory"
    assert self_heal, "a blocking gate without a self-heal costs a publish day"


def test_the_heal_runs_before_the_block():
    source = _source()
    heal = source.find("healed_content = heal_stats_total(post_content)")
    exit_pos = source.find("Stats consistency gate FAILED")
    assert heal != -1, "the stats self-heal is gone; the gate rejects immediately"
    assert exit_pos != -1, "the stats rejection block moved; re-anchor this guard"
    assert heal < exit_pos, "the heal runs after the rejection, so it never helps"


def test_the_reverify_is_unguarded():
    """A `try`/`or []` here turns the self-heal into a bypass."""
    source = _source()
    match = re.search(
        r"\n\s*stats_issues = validate_stats_consistency\(post_content\)\n", source
    )
    assert match, "the re-verification after the stats heal is gone"
    assert match.group(0).strip() == (
        "stats_issues = validate_stats_consistency(post_content)"
    ), match.group(0)


def test_the_healed_content_is_what_gets_written():
    """The heal mutates the in-memory content, which the write below uses.

    If the assignment back to `post_content` is dropped, the gate passes on
    healed text while the ORIGINAL inconsistent block reaches the corpus — the
    worst of both outcomes.
    """
    source = _source()
    assert re.search(r"^\s+post_content = healed_content$", source, re.M), (
        "the healed content is no longer assigned back to post_content"
    )
