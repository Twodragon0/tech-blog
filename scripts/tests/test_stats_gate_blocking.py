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


# ---------------------------------------------------------------------------
# Reachability: where the heal actually helps, measured on the real corpus
# ---------------------------------------------------------------------------
#
# Verdict 2026-09-09, after the promoted gate's first live cron publish:
# `.omc/plans/stats-self-heal-honesty-2026-09-09.md`
#
# The 2026-09-09 digest passed the gate WITHOUT it firing, and that post has all
# six categories at MAX_NEWS_PER_CATEGORY — the exact shape the heal declines.
# So the run proved the gate does not fire on consistent generator output; it
# proved nothing about the heal. Classifying every one of the 184 posts that
# carry a stats block by why `heal_stats_total` returns None:
#
#     178  refuses  (a category sits at the cap)
#       6  no-op    (already consistent, nothing to rewrite)
#       0  cannot locate the stats block
#       0  would repair
#
# All 23 current mismatches fall in the refusal group. So the heal's repair rate
# on this corpus is zero, and the question raised was whether `self_heal=True`
# in INLINE_PUBLISH_GATES is therefore dishonest.
#
# It is not, and the registry stays two-state. `self_heal` is a CONTRACT — "a
# repair path runs ahead of the block" — and that contract holds: the repair
# region is reachable (6 posts have no capped category) and the repair works
# there, which the first test below proves against a real post rather than a
# synthetic fixture. A rate of zero is a property of today's CONTENT, not of the
# code, and would flip the day an uncapped digest mismatches. Encoding a corpus
# statistic as a schema flag would make the registry wrong in the other
# direction, so the frequency is pinned here, where it can be re-measured.
#
# What the run did establish: this gate's safety comes from the generator
# asserting `shown_sum == total` at derivation (content_generator.py:1501 and
# :1948), NOT from the heal. Do not remember it as "there is a heal, so a false
# positive cannot cost a publish day" — for the dominant capped shape a mismatch
# is a block, by design, because the true total is not recoverable.

REPO_POSTS = Path(__file__).resolve().parents[2] / "_posts"
_STATS_BLOCK_RE = re.compile(r"\*\*수집 통계:\*\*\s*\n((?:- .+\n)+)")
_TOTAL_RE = re.compile(r"\*\*총 뉴스 수\*\*\s*:\s*(\d+)\s*개")
_CATS_RE = re.compile(r"- \*\*(?!총 뉴스 수)[^*]+\*\*\s*:\s*(\d+)\s*개")


def _stats_posts():
    """Every post carrying a parseable stats block, with its category counts."""
    out = []
    for post in sorted(REPO_POSTS.glob("*.md")):
        text = post.read_text(encoding="utf-8")
        block_match = _STATS_BLOCK_RE.search(text)
        if not block_match or not _TOTAL_RE.search(block_match.group(0)):
            continue
        counts = [int(c) for c in _CATS_RE.findall(block_match.group(0))]
        if counts:
            out.append((post, text, counts))
    return out


def test_the_heal_is_reachable_on_a_real_post_not_only_a_fixture():
    """The repair region exists in the corpus, and the repair works there.

    ``test_an_inconsistent_total_is_rederived_from_the_categories`` already
    proves the repair on a hand-built block. That is not enough to answer
    "is this heal dead code?", because a synthetic fixture can satisfy
    preconditions no real post ever satisfies. So: find a real post with no
    capped category, break its total, and require a repair.
    """
    uncapped = [
        (p, t)
        for p, t, counts in _stats_posts()
        if not any(c == MAX_NEWS_PER_CATEGORY for c in counts)
    ]
    assert uncapped, (
        "no post has an uncapped category any more, so the heal's repair "
        "region is empty in this corpus. That does NOT mean delete it — it "
        "means a low-volume digest can no longer occur, which is worth "
        "checking before acting on."
    )

    post, text = uncapped[0]
    total_match = _TOTAL_RE.search(text)
    broken = text.replace(total_match.group(0), "**총 뉴스 수**: 999개", 1)
    assert validate_stats_consistency(broken), f"{post.name} did not break"

    healed = heal_stats_total(broken)
    assert healed is not None, (
        f"the heal declined {post.name}, which has no capped category. The "
        "repair region is now unreachable and the promotion's premise is gone."
    )
    assert validate_stats_consistency(healed) == []


def test_every_current_mismatch_is_a_deliberate_refusal():
    """Pins the REASON, not just the outcome.

    A mismatch the heal cannot parse (no stats block, no total line) returns
    None exactly like a principled refusal, and both read as "did not heal".
    Separating them has to be behavioural: asking "is it capped?" with this
    file's own regex would explain the refusal without ever establishing that
    ``heal_stats_total`` could see the block. So each mismatched post is probed
    with its caps lowered and its total made impossible — nothing then justifies
    a refusal, and a heal that still declines is one that cannot parse.

    A note on verifying this test, because the first attempt drew the wrong
    conclusion. Breaking the heal's stats-block pattern appeared to leave this
    test GREEN, which looked like proof the check was vacuous. It was not: the
    same search was written out twice, character for character, in
    ``validate_stats_consistency`` and in ``heal_stats_total``, and a
    single-occurrence replace had hit the GATE. With the gate blind, no post
    was a mismatch, the loop below never ran, and passing meant nothing.

    That duplication is gone — both now read through ``_parse_stats_block``,
    verified equivalent over 293 posts on both the normal and repair paths — so
    a mutation to the pattern reaches the gate and the heal together, and the
    ambiguity that produced the false conclusion cannot recur. The general
    lesson survives the fix: when a probe reports MISSED, first establish that
    the mutation landed where you aimed it.
    """
    stalled = []
    for post, text, counts in _stats_posts():
        if not validate_stats_consistency(text):
            continue
        if heal_stats_total(text) is not None:
            continue  # would repair — fine, and informative

        # Remove the documented reason for refusing, and only that.
        probe = re.sub(
            r"(- \*\*(?!총 뉴스 수)[^*]+\*\*\s*:\s*)%d(\s*개)" % MAX_NEWS_PER_CATEGORY,
            r"\g<1>4\g<2>",
            text,
        )
        probe = _TOTAL_RE.sub("**총 뉴스 수**: 999개", probe, count=1)
        assert validate_stats_consistency(probe), f"{post.name} probe is consistent"

        if heal_stats_total(probe) is None:
            stalled.append(post.name)

    assert not stalled, (
        f"{stalled}: with no capped category and an impossible total, the heal "
        "STILL declined. That is not the documented refusal — heal_stats_total "
        "cannot parse these blocks. Check its stats-block pattern before "
        "touching anything else."
    )


def test_the_stats_block_is_located_in_exactly_one_place():
    """The gate and the heal must not carry separate copies of the search.

    They did until 2026-09-09, and the duplication was not merely untidy: a
    mutation aimed at one copy landed on the other, the gate went blind, and a
    corpus test whose loop never executed reported green. A single parser makes
    that class of confusion impossible, so the count is pinned.
    """
    source = (REPO_POSTS.parent / "scripts" / "news" / "qa_gate.py").read_text(
        encoding="utf-8"
    )
    compiled = re.findall(r"re\.compile\(r\"\\\*\\\*수집 통계", source)
    inline = re.findall(r"re\.search\(r\"\\\*\\\*수집 통계", source)
    assert len(compiled) == 1, (
        f"expected exactly one compiled stats-block pattern, found {len(compiled)}"
    )
    assert not inline, (
        f"{len(inline)} inline re.search for the stats block — route it through "
        "_parse_stats_block instead, or a mutation to one copy will silently "
        "leave the other in charge"
    )


def test_both_callers_read_through_the_shared_parser():
    """The other direction: one parser that nobody uses is not single-sourcing."""
    source = (REPO_POSTS.parent / "scripts" / "news" / "qa_gate.py").read_text(
        encoding="utf-8"
    )
    for symbol in ("validate_stats_consistency", "heal_stats_total"):
        start = source.index(f"def {symbol}(")
        body = source[start:]
        end = body.find("\ndef ", 1)
        body = body[:end] if end != -1 else body
        assert "_parse_stats_block(content)" in body, (
            f"{symbol} no longer reads the stats block through the shared "
            "parser, so it can drift from the other caller"
        )
