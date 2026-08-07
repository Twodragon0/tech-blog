"""Regression tests: a Korean summary must keep its sentence-final period.

Corpus audit 2026-08-06/07 traced the "headline-shaped fragment" summaries to
TWO different causes, and only one of them is ours:

* 14 cards end with a sentence-ending morpheme but NO period — caused by
  ``_korean_brief_summary``'s ``.strip(" .")``, which exists to clean up
  ellipsis residue but also eats a legitimate final period. Recurrence is live
  and rising: 2026-04 x3, 05 x2, 06 x2, **07 x7**.
* 11 cards end on a noun ("…취약점 탐지, 검증, 수정 제안") because the SOURCE
  text is a headline. Nothing here can fix that without rewriting content, so
  these tests pin that such text is left alone — a period must NOT be bolted
  onto a noun-ended fragment.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scripts.news import content_generator as cg  # noqa: E402


@pytest.fixture(autouse=True)
def _no_llm(monkeypatch):
    monkeypatch.setattr(cg, "_GEMINI_AVAILABLE", False, raising=False)
    monkeypatch.setattr(cg, "_GEMINI_CIRCUIT_OPEN", True, raising=False)
    cg.KOREAN_SUMMARY_CACHE.clear()


_seq = iter(range(10_000))


def summarize(text):
    return cg._korean_brief_summary(
        {"summary": text, "title": "t", "url": f"https://e.example/{next(_seq)}", "content": ""}
    )


# --- period restored ---------------------------------------------------------


@pytest.mark.parametrize(
    "text,tail",
    [
        ("공격자가 npm 패키지를 장악했습니다. 방어 측은 SBOM을 점검해야 합니다.", "합니다."),
        ("공격자가 npm 패키지를 장악했습니다.", "습니다."),
        ("보고서는 국내외 랜섬웨어 이슈를 요약한다.", "한다."),
        ("공격이 확산되고 있습니다...", "있습니다."),
    ],
)
def test_sentence_ending_keeps_its_period(text, tail):
    assert summarize(text).endswith(tail)


def test_ellipsis_is_still_removed():
    assert "..." not in summarize("공격이 확산되고 있습니다...")
    assert "…" not in summarize("공격이 확산되고 있습니다…")


# --- what must NOT gain a period --------------------------------------------


@pytest.mark.parametrize(
    "headline",
    [
        "OpenAI Codex Security - AI 기반 보안 에이전트로 취약점 탐지, 검증, 수정 제안",
        "Mozilla 파트너십으로 Firefox에서 22개 보안 취약점 발견 (14개 High)",
        "스테이블코인 월간 거래량 1.8조 달러 사상 최고치, USDC가 70% 차지",
    ],
)
def test_noun_ended_headline_is_left_alone(headline):
    """The source text is a headline; bolting on a period would be wrong Korean."""
    out = summarize(headline)
    assert not out.endswith(".")
    assert out == headline


# --- safety ------------------------------------------------------------------


def test_no_double_period():
    assert not summarize("공격자가 침투했습니다.").endswith("..")


def test_empty_input_returns_empty():
    assert summarize("") == ""


def test_helper_is_idempotent():
    once = cg._restore_sentence_period("공격자가 침투했습니다")
    assert cg._restore_sentence_period(once) == once


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("공격자가 침투했습니다", "공격자가 침투했습니다."),
        ("공격자가 침투했습니다.", "공격자가 침투했습니다."),
        ("취약점 탐지, 검증, 수정 제안", "취약점 탐지, 검증, 수정 제안"),
        ("", ""),
    ],
)
def test_restore_sentence_period_unit(raw, expected):
    assert cg._restore_sentence_period(raw) == expected
