#!/usr/bin/env python3
"""Guard: a feed summary the publisher already cut must not reach a table cell
still ending mid-word.

RSS feeds hand us summaries truncated on their side, marked with a trailing
ellipsis. Measured 2026-09-07 on a live collection: 32 of 165 items, at 90-170
characters — comfortably UNDER every length cap in this pipeline. That is what
made the bug invisible:

* ``_korean_brief_summary`` stripped the ellipsis (``.replace("...", " ")``),
  destroying the only evidence of the cut, and
* ``_table_summary``'s cleanup hung off ``len(cleaned) > max_len``, so a short
  pre-cut fragment skipped ``_truncate_korean_sentence`` entirely.

Consequence: the 09-07 digest was rejected at the publish gate with
``L259 TRUNCATED: … 성장하는 시스템에 가`` (one lost day), and because that gate
only fires on tails that happen to be a dangling particle, quieter cases had
already shipped — a corpus sweep found 36+ cells ending mid-word (``수 시``
-> 시간, ``버전 관`` -> 관리, ``자체 최`` -> 최적화), nearly all in cron digests.

Where the fix is NOT
--------------------
``_table_summary`` is left alone on purpose. Both of its callers pass
``_korean_brief_summary(item)``, and the ellipsis never survives that far —
verified 0 times out of 6 live ellipsis-terminated items. A "was the source
cut?" branch there would be unreachable code. ``test_table_summary_*`` below
pins that decision so it is not "fixed" later.
"""

from __future__ import annotations

import re

import news.content_generator as cg
import pytest
from digest_quality_report import _TRUNCATION_PARTICLES

# The two real cells from the rejected 2026-09-07 draft, with the feed's
# trailing ellipsis restored (the artifact shows them after erasure).
ROW9_SRC = (
    "요즘 AI 로 개발을 진행하다 보니 작업 시켜두고 기다리기에 지루한 시간들이 자주 생기더라구요. "
    "앱을 다운로드 해서 하자니 뭔가 번거롭기도 하고 광고에 시달리기도 귀찮고 구형 폰이라서 최신 "
    "게임도 잘 안 돌아가고 해서 심심풀이로 Codex Sol Max 로 그냥 개발해보라고 했는데 퀄리티가 "
    "나름 괜찮아서 틈..."
)
ROW10_SRC = (
    "OpenAI는 추론 모델의 발전이 재귀적 자기개선(RSI) 으로 이어질 수 있다고 예상하며, 정렬과 "
    "감시 역량이 지능 향상을 따라가지 못하는 만큼 개발 속도를 안전성에 맞춰 제한 해야 한다고 "
    "강조함 AI는 사람이 설계한 규칙보다 대규모 최적화로 성장하는 시스템에 가..."
)

# A single trailing Hangul syllable after a space is the mid-word signature that
# the particle gate misses (`틈` of 틈틈이, `관` of 관리).
_SINGLE_SYLLABLE_TAIL = re.compile(r"\s[가-힣]$")


def _cell_for(source: str) -> str:
    """Run the real production path: brief summary -> table cell."""
    cg.KOREAN_SUMMARY_CACHE.clear()
    item = {
        "title": "t",
        "url": "https://example.invalid/x",
        "summary": source,
        "category": "tech",
        "source_name": "GeekNews",
    }
    return cg._table_summary(cg._korean_brief_summary(item).replace("\n", " "))


@pytest.mark.parametrize("source", [ROW9_SRC, ROW10_SRC], ids=["row9", "row10"])
def test_pretruncated_source_does_not_yield_a_mid_word_cell(source):
    cell = _cell_for(source)
    assert not _TRUNCATION_PARTICLES.search(cell), (
        f"cell ends in a dangling particle, which blocks publication: {cell[-30:]!r}"
    )
    assert not _SINGLE_SYLLABLE_TAIL.search(cell), (
        "cell ends in a lone Hangul syllable — the mid-word cut the publish gate "
        f"does NOT catch, so it would ship: {cell[-30:]!r}"
    )


@pytest.mark.parametrize("source", [ROW9_SRC, ROW10_SRC], ids=["row9", "row10"])
def test_control_same_sources_break_without_the_ellipsis_signal(source, monkeypatch):
    """Control: these fixtures really are violations.

    Without this, the test above passes just as well against a source that was
    never truncated, and the whole file would prove nothing. Disabling the
    trailing-ellipsis detector reproduces the pre-fix behaviour exactly.
    """
    monkeypatch.setattr(cg, "_TRAILING_ELLIPSIS_RE", re.compile(r"(?!x)x"))
    cell = _cell_for(source)
    broken = bool(_TRUNCATION_PARTICLES.search(cell)) or bool(
        _SINGLE_SYLLABLE_TAIL.search(cell)
    )
    assert broken, (
        "with the fix disabled this source produced a clean cell, so it is not a "
        f"reproduction of the bug: {cell[-30:]!r}"
    )


def test_ellipsis_detector_accepts_both_spellings_and_ignores_mid_string():
    rx = cg._TRAILING_ELLIPSIS_RE
    assert rx.search("잘린 문장...")
    assert rx.search("잘린 문장…")
    assert rx.search("잘린 문장... ")
    assert not rx.search("중간에 ... 있는 문장"), (
        "a mid-string ellipsis is not a truncation marker; treating it as one "
        "would rewrite well-formed summaries"
    )


def test_cut_at_sentence_boundary_rewinds_and_refuses_an_early_cut():
    late = "앞 문장입니다. 뒤쪽에서 끝나는 두 번째 문장입니다. 잘린 조"
    got = cg._cut_at_sentence_boundary(late, len(late))
    assert got.endswith("두 번째 문장입니다.")

    # A terminator inside the first 40 % is refused: cutting there would throw
    # away most of the summary.
    early = "짧다. " + "그리고 이어지는 긴 설명이 계속됩니다만 종결부호가 없음" * 2
    assert cg._cut_at_sentence_boundary(early, len(early)) == ""


def test_finish_korean_fragment_drops_a_trailing_connective():
    """`괜찮아서 등이 확인되었습니다.` is broken Korean — the connective demands
    a following clause, so it must go before the closing phrase is appended."""
    out = cg._finish_korean_fragment("퀄리티가 나름 괜찮아서 틈")
    assert "괜찮아서" not in out, f"connective survived: {out!r}"
    assert out.endswith("등이 확인되었습니다.")


def test_long_input_path_is_unchanged():
    """`_truncate_korean_sentence` still owns the over-cap case.

    The helper extraction must not have altered it; this is the path every
    existing summary already flows through.
    """
    text = "첫 문장입니다. " + "가나다라마바사 " * 60
    got = cg._truncate_korean_sentence(text, 200)
    assert len(got) <= 200 + len(" 등이 확인되었습니다.")
    assert cg._truncate_korean_sentence("짧은 문장", 200) == "짧은 문장"


def test_table_summary_deliberately_ignores_a_trailing_ellipsis():
    """Pins the decision documented in this module's docstring.

    If someone adds a source-was-cut branch here, it is unreachable in
    production and the real erasure site goes unfixed again.
    """
    assert cg._table_summary("짧게 잘린 조각...", 200) == "짧게 잘린 조각"


def test_decorative_ellipsis_after_a_finished_sentence_is_not_a_cut():
    """A trailing ellipsis alone is not the signal.

    Publishers write one after a complete sentence too. Treating that as a cut
    rewrote "공격이 확산되고 있습니다..." into "공격이 확산되고 등이
    확인되었습니다." — a finished sentence replaced by boilerplate. Caught by
    test_korean_summary_period while this fix was being written, so the
    condition also requires that the remaining text does NOT already end on a
    sentence-ending morpheme.
    """
    cell = _cell_for("공격이 확산되고 있습니다...")
    assert "있습니다" in cell, f"the finished sentence was rewritten: {cell!r}"
    assert "등이 확인되었습니다" not in cell


def test_noun_ending_source_is_still_treated_as_cut():
    """Contrast with the test above: no sentence morpheme means the ellipsis is
    load-bearing, so the fragment must be closed rather than left mid-word."""
    cell = _cell_for(
        "공격 표면 점검과 로그 보존 절차, 그리고 대응 담당자 배정 및 후속 조..."
    )
    assert not _SINGLE_SYLLABLE_TAIL.search(cell), cell[-24:]
    # The partial token is gone and the fragment is closed. No trailing period:
    # _table_summary's `.strip(" .")` removes it by design, which is why the
    # assertion checks the phrase rather than the punctuation.
    assert not cell.endswith("조"), f"partial token survived: {cell[-20:]!r}"
    assert "등이 확인되었습니다" in cell, f"fragment left unclosed: {cell[-30:]!r}"
