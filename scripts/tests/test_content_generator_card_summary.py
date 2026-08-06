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
