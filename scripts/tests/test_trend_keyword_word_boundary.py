#!/usr/bin/env python3
"""Guard: the trend-table keyword extractor must not end a phrase mid-word.

``_extract_trend_keyword``'s Korean branch used to hard slice at 40 characters
(``segment = segment[:40]``) while the English branch immediately below already
rewound to a word boundary (``phrase[:60].rsplit(" ", 1)[0]``). The two cells
grandfathered into ``scripts/digest_midword_baseline.txt`` as
"category rollup rows" came from exactly that slice:

    Amazon Bedrock Agents와 AWS Support 자동화 워크플로 구축하기
      -> 'Amazon Bedrock Agents와 AWS Support 자동화 워'      (워 of 워크플로)

    당근이 AWS CloudHSM으로 대규모 서명키 관리 시스템을 구축한 방법 – 3부: …
      -> '당근이 AWS CloudHSM으로 대규모 서명키 관리 시스템을 구축한 방'  (방 of 방법)

This was a latent publish blocker, not a cosmetic defect: a trailing lone
syllable is what ``digest_quality_report``'s mid-word gate rejects, and that
gate blocks the cron publish. The 2026-09-07 truncation fix addressed the RSS
pre-truncation path only and never touched this one.

Measured over the 334 over-cap Korean title segments in the corpus
(``_data/collected_news.json`` + every digest post's link titles):

    hard slice                     -> 58 rejected (51 lone syllable, 7 particle)
    _smart_truncate_korean only    -> 14 (rewinds, but leaves a hanging `및`/`수`)
    + _drop_dangling_lone_syllable ->  0

The 10 rejections that remain corpus-wide are titles at or under the cap, so no
truncation runs on them at all — they are natural endings (``2026년 초``,
``7개 주요 Bitcoin 채굴 풀``) that the gate's allow-list does not cover. That is
an allow-list question, deliberately out of scope here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from digest_quality_report import (
    _SINGLE_SYLLABLE_ALLOW,
    _SINGLE_SYLLABLE_TAIL,
    _TRUNCATION_PARTICLES,
)

from scripts.news import content_generator as cg

# CLOUDHSM is the verbatim source title, still present in its own post
# (2026-07-31, line 72). BEDROCK is a reconstruction: the 2026-04-18 post keeps
# only the truncated cell, so the full headline is not recoverable from the
# repo. It earns its place by reproducing the baselined cell byte-for-byte under
# the old hard slice — verified, not assumed.
BEDROCK = "Amazon Bedrock Agents와 AWS Support 자동화 워크플로 구축하기"
CLOUDHSM = (
    "당근이 AWS CloudHSM으로 대규모 서명키 관리 시스템을 구축한 방법 – 3부: "
    "서명 시스템 구현, 트러블슈팅, 무중단 키 전환"
)
# NOT a hard-slice reproduction — measured: `segment[:40]` yields
# '…Extension으로 몇 분 만에 코드를', which the gate accepts. This title breaks the
# *rewind*: _smart_truncate_korean cuts at `…으로 몇 분`, and one drop then exposes
# `…으로 몇`. It belongs to the loop test, not the control.
CASCADE = "Gemini CLI DevOps Extension으로 몇 분 만에 코드를 배포하세요"

CAP = 40


def _gate_verdict(cell: str) -> str | None:
    """Return why the publish gate would reject `cell`, or None if it passes."""
    if _TRUNCATION_PARTICLES.search(cell):
        return "dangling particle"
    match = _SINGLE_SYLLABLE_TAIL.search(cell)
    if match and match.group(1) not in _SINGLE_SYLLABLE_ALLOW:
        return f"lone syllable {match.group(1)!r}"
    return None


@pytest.mark.parametrize(
    "title", [BEDROCK, CLOUDHSM, CASCADE], ids=["bedrock", "cloudhsm", "cascade"]
)
def test_over_cap_korean_title_is_not_cut_mid_word(title):
    out = cg._extract_trend_keyword(title, "AWS Korea Blog")
    verdict = _gate_verdict(out)
    assert verdict is None, f"the publish gate would reject {out!r}: {verdict}"


@pytest.mark.parametrize("title", [BEDROCK, CLOUDHSM], ids=["bedrock", "cloudhsm"])
def test_control_hard_slice_really_does_break_these_titles(title, monkeypatch):
    """Control: these fixtures reproduce the bug.

    Without it, the test above would pass just as well against a title that was
    never over the cap, and this file would prove nothing. Restoring the old
    hard slice must make the gate reject every fixture.
    """
    monkeypatch.setattr(
        cg, "_smart_truncate_korean", lambda text, max_len: text[:max_len]
    )
    monkeypatch.setattr(
        cg, "_drop_dangling_lone_syllable", lambda text, min_len=12: text
    )
    out = cg._extract_trend_keyword(title, "AWS Korea Blog")
    assert _gate_verdict(out) is not None, (
        f"with the fix disabled this title produced a clean cell ({out!r}), so it "
        "is not a reproduction of the defect"
    )


def test_a_single_drop_is_not_enough():
    """Pins the loop in _drop_dangling_lone_syllable.

    A non-looping version turned `…으로 몇 분` into `…으로 몇` — still rejected,
    and shorter. The helper must reach a fixed point.
    """
    once = cg._smart_truncate_korean(re.split(r"[,:\-–—·]", CASCADE)[0].strip(), CAP)
    assert once.endswith("몇 분"), f"fixture drifted; _smart_truncate gave {once!r}"
    assert cg._drop_dangling_lone_syllable(once) == "Gemini CLI DevOps Extension으로"


def test_allow_listed_ending_is_preserved():
    """`앱` ends a Korean noun phrase on its own, so it must survive."""
    out = cg._extract_trend_keyword(
        "사용자 데이터를 대규모로 수집하던 가짜 통화 기록 앱", "src"
    )
    assert out.endswith("앱"), f"a legitimate ending was stripped: {out!r}"


def test_allow_list_is_imported_from_the_gate_not_restated():
    """Lockstep: the generator must not keep its own drifting copy.

    If these diverge, the generator strips a word the gate accepts (mangling
    good keywords) or keeps one the gate rejects (blocking the publish).

    Identity (``is``) cannot be asserted, and that is worth knowing: this repo
    imports the checker under two names — ``scripts.digest_quality_report``
    (the generator's convention, matching ``scripts.news.analyzer``) and bare
    ``digest_quality_report`` (what ``scripts/tests`` gets on sys.path). Python
    loads those as two separate modules, so the two frozensets are equal but
    not the same object. Equality is therefore the strongest runtime check, and
    the source assertion below is what actually forbids a second literal.
    """
    assert cg._SINGLE_SYLLABLE_ALLOW == _SINGLE_SYLLABLE_ALLOW

    source = Path(cg.__file__).read_text(encoding="utf-8")
    assert (
        "from scripts.digest_quality_report import _SINGLE_SYLLABLE_ALLOW" in source
    ), "the generator no longer imports the gate's allow-list"
    assert not re.search(r"^_SINGLE_SYLLABLE_ALLOW\s*=", source, re.MULTILINE), (
        "the generator restates the allow-list instead of importing it; the two "
        "copies will drift and one side will start rejecting or mangling cells"
    )


def test_result_still_respects_the_cap():
    for title in (BEDROCK, CLOUDHSM, CASCADE):
        out = cg._extract_trend_keyword(title, "src")
        assert len(out) <= CAP, f"{len(out)} chars > {CAP}: {out!r}"


def test_under_cap_titles_are_returned_untouched():
    """The fix is scoped to the over-cap path.

    `_smart_truncate_korean` also runs `_trim_dangling_particles` on its
    early-return path, so calling it unconditionally would rewrite short
    keywords too. It is called only inside `len(segment) > 40`.
    """
    short = "쿠버네티스 런타임 보안 강화 방안"
    assert cg._extract_trend_keyword(short, "src") == short


def test_stub_refusal_returns_the_input_rather_than_a_fragment():
    """A drop that would leave a stub is refused on purpose.

    Deliberately loud: 0 of the 334 corpus segments hit this, and a gate
    failure is better than shipping a meaningless cell.
    """
    assert cg._drop_dangling_lone_syllable("보안 팁 등 것 수", min_len=40) == (
        "보안 팁 등 것 수"
    )
