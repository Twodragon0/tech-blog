#!/usr/bin/env python3
"""Regression tests for the news-card ``summary`` truncation contract.

Background — corpus audit 2026-08-06:
128 of 1,756 emitted news cards ended mid-sentence, and their lengths cluster
exactly on the cap (``len == 200`` x93, ``199`` x24). Root cause:
``generate_news_section`` sliced with a raw ``ko_summary[:200]`` while the very
same module already owns a boundary-aware truncator
(``_truncate_korean_sentence``) that the excerpt and table-summary paths use.
The card was the one place cutting blind, so readers got fragments like
"…지원하는 방식으로 확".

These tests assert the contract at the *generation* boundary, so a future edit
cannot reintroduce a blind slice.
"""

from __future__ import annotations

import itertools
import re

from scripts.news.content_generator import generate_news_section

_CAP = 200
_SENTENCE_END = ("다.", "요.", ".", "!", "?")


_seq = itertools.count()


def _build_item(*, title: str = "x", summary: str = "y", **overrides):
    # KOREAN_SUMMARY_CACHE is keyed by id/url/title, and it is module-global —
    # a shared URL makes one test return another test's summary.
    uniq = next(_seq)
    item = {
        "title_ko": title,
        "title": title,
        "summary_ko": summary,
        "summary": summary,
        "url": f"https://example.com/post-{uniq}",
        "source_name": "Example",
        "category": "tech",
        "image": "https://example.com/post.jpg",
        "content": "x" * 800,
    }
    item.update(overrides)
    return item


def _card_summary(section: str) -> str:
    m = re.search(r'\n\s*summary="(.*?)"\n', section, re.DOTALL)
    assert m, f"no summary attribute emitted; section was:\n{section[:400]}"
    return m.group(1)


# _korean_brief_summary keeps the FIRST TWO sentences and only boundary-cuts
# above 220 chars, so the fixture must make those two sentences exceed the 200
# cap — that is the shape that reaches the blind slice and produced the 128
# corpus defects.
_LONG = (
    "상업용 PhaaS 툴킷인 Greatness가 OAuth 2.0 Device Authorization Grant를 "
    "악용하는 device code phishing 기능을 추가하여 다단계 인증을 우회하고 사용자 "
    "계정을 탈취하는 최신 범죄웨어로 부상했으며 여러 산업군에서 피해가 확인되고 "
    "있습니다. 방어 측은 조건부 액세스 정책과 디바이스 준수 상태를 함께 점검해야 "
    "합니다."
)


def test_long_summary_is_not_cut_mid_sentence():
    assert len(_LONG) > _CAP, "fixture must exceed the cap to exercise truncation"
    summary = _card_summary(generate_news_section(_build_item(summary=_LONG), "1.1"))
    assert summary.endswith(_SENTENCE_END), (
        f"card summary must end on a sentence boundary, got: …{summary[-40:]!r}. "
        "Use _truncate_korean_sentence, not a raw slice."
    )


def test_long_summary_does_not_land_exactly_on_the_cap():
    """A raw slice makes len == cap; a boundary-aware cut essentially never does."""
    summary = _card_summary(generate_news_section(_build_item(summary=_LONG), "1.1"))
    assert len(summary) != _CAP, (
        "length identical to the cap is the fingerprint of a blind slice "
        f"({_CAP} chars); expected a sentence-boundary cut."
    )


def test_short_summary_is_not_truncated():
    """Below the cap, the text must reach the card intact.

    `_korean_brief_summary` strips the trailing period of every Korean-path
    summary (`.strip(" .")`), so the passthrough form is period-less. That is a
    separate pre-existing behaviour and NOT what this fix changes — asserting
    the substring keeps this test honest about the truncation contract only.
    """
    short = "짧은 요약입니다."
    summary = _card_summary(generate_news_section(_build_item(summary=short), "1.1"))
    assert summary.rstrip(".") == short.rstrip(".")
    assert len(summary) < _CAP


def test_truncated_summary_is_a_prefix_of_the_original():
    """Truncation may only drop a tail — it must never rewrite earlier text."""
    summary = _card_summary(generate_news_section(_build_item(summary=_LONG), "1.1"))
    head = summary.rstrip("…")
    # The boundary helper may append a closing clause when no sentence end is
    # reachable; the leading run must still match the source verbatim.
    common = 0
    for a, b in zip(head, _LONG):
        if a != b:
            break
        common += 1
    assert common >= 100, (
        f"only {common} leading chars match the source summary — truncation must "
        "not paraphrase or reorder the original text."
    )


def test_summary_stays_within_a_sane_bound():
    """Boundary-aware cutting may overshoot slightly, but not without limit."""
    summary = _card_summary(generate_news_section(_build_item(summary=_LONG), "1.1"))
    assert len(summary) <= _CAP + 20, f"summary grew to {len(summary)} chars"


# --- the card and the "#### 요약" block must not print the same text ---------
#
# `_includes/news-card.html:54` already renders `summary=` in a `<p class=
# "news-card__summary">`. The fallback path then emitted `#### 요약` with the
# SAME text, so the reader saw one sentence twice, ~1 line apart.
#
# Measured 2026-09-10 over the corpus: 1,583 of 2,043 `#### 요약` blocks (77%)
# are byte-identical to the `summary=` above them, across 193 of 217 digests —
# 215,858 characters of second printing. Confirmed in built HTML: the same
# sentence appears in `<p class="news-card__summary">` and again under
# `<h4 id="요약">`.
#
# The block is NOT always redundant: the card truncates at 200 chars, so a
# longer `ko_summary` carries information the card does not show. The rule is
# therefore "skip the block only when the card already shows all of it", not
# "never emit the block" — and both halves are asserted below.

_SUMMARY_BLOCK_RE = re.compile(r"^####\s*요약\s*$", re.MULTILINE)


def _summary_block_body(section: str) -> str | None:
    """Prose under the first ``#### 요약``, or None when there is no such block."""
    m = _SUMMARY_BLOCK_RE.search(section)
    if not m:
        return None
    rest = section[m.end() :]
    body = re.split(r"\n\s*\n|\n#{2,4}\s|\n---", rest, maxsplit=1)[0]
    return body.strip()


_SHORT = "Microsoft가 윈도우 11에 연령 인식 API를 추가했습니다. 생년월일을 노출하지 않습니다."


def test_short_summary_emits_no_duplicate_block():
    """The card shows all of it, so the block would be a second printing."""
    assert len(_SHORT) <= _CAP, "fixture must fit under the cap to be a duplicate"
    section = generate_news_section(_build_item(summary=_SHORT), "1.1")
    card = _card_summary(section)
    body = _summary_block_body(section)
    assert card.strip(), "control: a card summary must still be emitted"
    assert body != card.strip(), (
        "the '#### 요약' block repeats the card summary verbatim. The reader sees "
        "the same sentence twice, one line apart — 1,583 corpus instances."
    )
    assert body is None, (
        f"expected no '#### 요약' block at all when the card is complete, got {body!r}"
    )


def test_long_summary_keeps_the_block_because_the_card_is_truncated():
    """Direction check: the block must survive when it adds text.

    Without this, "remove the duplicate" would slide into "remove the block",
    silently dropping the tail of every summary longer than 200 chars.
    """
    section = generate_news_section(_build_item(summary=_LONG), "1.1")
    card = _card_summary(section)
    body = _summary_block_body(section)
    assert len(card) <= _CAP + 5, f"card unexpectedly untruncated: {len(card)}"
    assert body, "the '#### 요약' block was dropped even though the card is truncated"
    assert len(body) > len(card), (
        f"block ({len(body)}) should carry more than the card ({len(card)})"
    )


# --- the quote case: the producer and the gate must agree ------------------
#
# `_SHORT` above carries no quote character, so it pinned nothing about the one
# input where the two sides disagreed. `_sanitize_liquid_param` maps an inner
# ASCII `"` to U+201D — Liquid include attributes are delimited by ASCII `"` and
# honour no backslash escape, so an unmapped quote would terminate the attribute
# early. The card therefore differs from `ko_summary` by exactly that glyph, a
# byte comparison called them different, and the block was emitted. The gate
# (`scripts/check_duplicate_card_summary.py`) folds quote glyphs, so it saw the
# duplicate and failed. That gate runs fail-closed on the cron publish path with
# no self-heal, so the disagreement costs a whole day's digest, and only for
# items that happen to carry a quote under the 200-char cap — intermittent
# enough to survive four published digests before it was found.

_SHORT_QUOTED = (
    'APT28이 "MacroMaze"라는 웹훅 기반 백도어를 배포했습니다. 다단계 인증을 우회합니다.'
)


def test_quoted_short_summary_emits_no_duplicate_block():
    assert '"' in _SHORT_QUOTED, "fixture must carry the character under test"
    assert len(_SHORT_QUOTED) <= _CAP, "fixture must fit under the cap"

    section = generate_news_section(_build_item(summary=_SHORT_QUOTED), "1.1")
    card = _card_summary(section)

    # Control: without this the test could pass vacuously on a build where the
    # sanitizer no longer rewrites the quote, and would stop covering the defect.
    assert "”" in card, (
        f"the card summary no longer carries the sanitized quote: {card!r}. "
        "This test is only meaningful while _sanitize_liquid_param rewrites it."
    )

    assert _summary_block_body(section) is None, (
        "the '#### 요약' block came back for a quoted summary. The card already "
        "shows this sentence; check_duplicate_card_summary.py folds the quote "
        "glyph and fails the publish, which aborts the cron digest."
    )


def test_quoted_long_summary_still_keeps_its_block():
    """Direction: folding the quote must not swallow a real tail."""
    # A quote inside _LONG, so the two-sentence brief summary still exceeds the
    # cap. Prepending a short sentence instead would keep it under 200 and the
    # test would assert nothing about truncation.
    quoted_long = _LONG.replace("Greatness가", '"Greatness"가', 1)
    assert '"' in quoted_long and len(quoted_long) > _CAP
    section = generate_news_section(_build_item(summary=quoted_long), "1.1")
    card = _card_summary(section)
    body = _summary_block_body(section)
    assert body, "the block was dropped even though the card is truncated"
    assert len(body) > len(card), (
        f"block ({len(body)}) should carry more than the card ({len(card)})"
    )


def test_block_survives_when_there_is_no_card_summary():
    """Control: with no card summary, the block is the ONLY summary.

    The fallback fills it from ``content`` in that case. Suppressing it here
    would leave the item with no prose at all — the opposite failure to the one
    being fixed, and the reason the rule is keyed on equality with the card
    rather than on "a card exists".
    """
    section = generate_news_section(_build_item(summary=""), "1.1")
    body = _summary_block_body(section)
    assert body, "the item lost its only summary text"
