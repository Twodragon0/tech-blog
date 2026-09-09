#!/usr/bin/env python3
"""Guard: the blockchain trend group, and the keywords deliberately kept out.

`블록체인 뉴스` is the SECOND largest collected category (882 articles across
184 digests) and `trend_defs` had no group for it, so 428 of the 1704 unmatched
card titles — 25% — were blockchain stories counted as `기타`. An omission, not
a tuning problem.

Keywords were chosen by marginal contribution over the others, measured on 2449
real card titles. What was rejected matters as much as what was kept, so both
are pinned here: a future reader adding `crypto` back would otherwise have to
rediscover why it is wrong.

Research: ``.omc/research/trend-defs-coverage-2026-09-09.md``
"""

from __future__ import annotations

import logging
import re

import pytest
from news import qa_gate
from news.content_generator import _generate_trend_analysis

GROUP = "블록체인/암호화폐"

EXPECTED_KEYWORDS = [
    "bitcoin",
    "비트코인",
    "블록체인",
    "암호화폐",
    "스테이블코인",
    "ethereum",
    "defi",
    "xrp",
    # Tickers, added while auditing the `유출` keyword of the security groups:
    # without them "바이낸스 자금 유출 … ETH 인출" had no blockchain home and was
    # filed as a data leak alone. `btc` +9 titles, `eth` +5.
    "btc",
    "eth",
]

# Rejected, with the measurement that rejected each one.
REJECTED = {
    "blockchain": "marginal contribution +0 — the English word always co-occurs "
    "with 블록체인 or bitcoin in this corpus",
    "etf": "marginal contribution +0",
    "crypto": "+14, but substring matching places it inside Encryptor, "
    "decryptor and cryptography, so it classifies ransomware and "
    "cryptography stories as blockchain",
    "토큰": "matches 게이트웨이 토큰 탈취 (auth) and 100만 토큰 컨텍스트 (AI), "
    "both already covered by other groups",
}


def _item(title: str, category: str = "security", source: str = "Src") -> dict:
    return {
        "title": title,
        "summary": "",
        "content": "",
        "category": category,
        "source_name": source,
    }


def _rows(items):
    content = _generate_trend_analysis(items, 7)
    rows, _citations = qa_gate.extract_trend_rows_and_citations(content)
    return rows


def _trend_defs_source() -> str:
    """The ``trend_defs`` literal, as text, from the generator's own source.

    ``trend_defs`` is a local inside ``_generate_trend_analysis``, so there is
    no object to import. This reads the literal instead, which makes the
    keyword tests below **drift guards on the definition** — they check what is
    written, not what the matcher does with it.

    That distinction is the reason the behavioural tests further down exist and
    are not redundant: a keyword could be present here and never applied (or
    applied through a different path). Presence is asserted here; effect is
    asserted there. Neither substitutes for the other.
    """
    import inspect

    source = inspect.getsource(_generate_trend_analysis)
    match = re.search(r"trend_defs = \{(.+?)\n    \}", source, re.S)
    assert match, "trend_defs was restructured; re-anchor this guard"
    return match.group(1)


def _trend_group_names() -> list[str]:
    """The group names, in declaration order, read from the same literal.

    Derived rather than hardcoded: the coverage line reports how many groups
    ran, and pinning that as a number made this file break every time a group
    was added — which is a guard that trains people to edit the guard. Counting
    the keys keeps the assertion meaningful (a log saying 8 while 11 exist still
    fails) without being a maintenance tax.

    Keys sit at eight spaces; keyword strings inside a multi-line list sit at
    twelve, and comments start with `#`, so neither is picked up.
    """
    return re.findall(r'^        "([^"]+)":', _trend_defs_source(), re.M)


# ---------------------------------------------------------------------------
# The group exists and carries exactly the measured keyword set
# ---------------------------------------------------------------------------


def test_the_group_is_registered():
    body = _trend_defs_source()
    assert f'"{GROUP}"' in body, (
        f"{GROUP} is gone from trend_defs. 블록체인 뉴스 is the second largest "
        "collected category; without this group a quarter of unmatched titles "
        "fall to 기타."
    )


@pytest.mark.parametrize("keyword", EXPECTED_KEYWORDS)
def test_each_measured_keyword_is_present(keyword):
    assert f'"{keyword}"' in _trend_defs_source(), (
        f"{keyword!r} was dropped from the blockchain group. Each keyword was "
        "kept for a measured marginal contribution — re-measure before removing."
    )


@pytest.mark.parametrize("keyword,why", REJECTED.items())
def test_each_rejected_keyword_stays_out(keyword, why):
    assert f'"{keyword}"' not in _trend_defs_source(), (
        f"{keyword!r} was added to trend_defs. It was rejected: {why}."
    )


def test_the_crypto_rejection_is_grounded_in_substring_behaviour():
    """Not an opinion — the matcher does plain substring matching for len > 3.

    Pinned so that "crypto looks harmless" cannot be argued from intuition. If
    the matcher ever gains word-boundary matching for longer keywords, this
    test is where the rejection should be revisited.
    """
    assert "crypto" in "stormencryptor"
    assert "crypto" in "decryptor"
    assert "crypto" in "cryptography"
    # And the corpus really does carry such a title.
    ransomware_title = (
        "중국 연계 해커, N-central 취약점 통해 신종 StormEncryptor 랜섬웨어 배포"
    )
    assert "crypto" in ransomware_title.lower()


# ---------------------------------------------------------------------------
# Behaviour on real titles
# ---------------------------------------------------------------------------

# Verbatim from published digests, chosen to cover distinct keywords.
REAL_BLOCKCHAIN_TITLES = [
    "Goldman Sachs, Bitcoin ETF 11억 달러 보유 공시",
    "CFTC 스테이블코인 기준 확대: 국가 신탁은행 포함",
    "Buterin, Ethereum 재단 비판에 반박하며 중립성 재확약",
    "DeFi 프로토콜 스마트 컨트랙트 취약점으로 1.2억 달러 유출",
    "블록체인 기반 클라우드 감사 로그 무결성 보장 방법론",
    "SEC, 가짜 AI 트레이딩 봇으로 1230만 달러 암호화폐 사기 친 텍사스 남성 기소",
]


@pytest.mark.parametrize("title", REAL_BLOCKCHAIN_TITLES)
def test_a_real_blockchain_title_reaches_the_group(title):
    # Two copies so the trend clears the headline floor and is not just a row.
    rows = _rows([_item(title), _item(title + " (속보)")])
    assert any(name == GROUP for name, _count in rows), (
        f"{title!r} did not classify as {GROUP}; rows={sorted(rows)}"
    )


@pytest.mark.parametrize(
    "title,expected_absent_reason",
    [
        (
            "중국 연계 해커, N-central 취약점 통해 신종 StormEncryptor 랜섬웨어 배포",
            "Encryptor contains the substring `crypto`",
        ),
        (
            "Infostealer, AI 에이전트 설정 파일 및 게이트웨이 토큰 탈취",
            "an auth token is not a blockchain token",
        ),
        (
            "OpenAI GPT-5.4 출시 — 네이티브 컴퓨터 사용과 100만 토큰 컨텍스트",
            "an LLM context token is not a blockchain token",
        ),
        (
            "Post-quantum cryptography 마이그레이션 가이드",
            "cryptography contains the substring `crypto`",
        ),
    ],
)
def test_a_non_blockchain_title_does_not_reach_the_group(title, expected_absent_reason):
    rows = _rows([_item(title), _item(title + " 후속")])
    assert not any(name == GROUP for name, _count in rows), (
        f"{title!r} was classified as {GROUP} — {expected_absent_reason}. "
        "This is the over-matching the rejected keywords would cause."
    )


def test_a_blockchain_trend_can_now_be_headlined_over_a_larger_catch_all():
    """The end-to-end point: these stories used to become `기타`."""
    content = _generate_trend_analysis(
        [
            _item("Goldman Sachs, Bitcoin ETF 11억 달러 보유 공시", "blockchain"),
            _item("CFTC 스테이블코인 기준 확대: 국가 신탁은행 포함", "blockchain"),
            _item("정원 이야기 A", "tech"),
            _item("정원 이야기 B", "tech"),
            _item("정원 이야기 C", "tech"),
        ],
        7,
    )
    rows, citations = qa_gate.extract_trend_rows_and_citations(content)
    assert ("기타", 3) in rows, "the catch-all must still be a row"
    assert citations == [(GROUP, 2)], (
        f"expected the blockchain trend to be headlined over the larger "
        f"catch-all, got {citations}"
    )


# ---------------------------------------------------------------------------
# Coverage logging
# ---------------------------------------------------------------------------


def test_coverage_is_logged_with_matched_and_unmatched(caplog):
    """The figure a published post cannot be asked for afterwards.

    The matcher reads every collected item; only a subset becomes a card. So a
    retrospective reconstruction can only sample, which the 2026-09-09
    investigation had to state as an open limitation. This line closes it.
    """
    items = [
        _item("Goldman Sachs, Bitcoin ETF 11억 달러 보유 공시", "blockchain"),
        _item("정원 이야기 A", "tech"),
        _item("정원 이야기 B", "tech"),
        _item("정원 이야기 C", "tech"),
    ]
    with caplog.at_level(logging.INFO):
        _generate_trend_analysis(items, 7)

    lines = [r.message for r in caplog.records if "Trend coverage" in r.message]
    assert len(lines) == 1, f"expected one coverage line, got {lines}"
    line = lines[0]
    assert "1/4 (25%)" in line, line
    assert "3 unmatched" in line, line
    expected_groups = len(_trend_group_names())
    assert f"{expected_groups} trend groups" in line, (
        f"the coverage line reports a different group count than trend_defs "
        f"declares ({expected_groups}): {line}"
    )


def test_the_logged_counts_partition_the_input(caplog):
    """matched + unmatched == total, on every shape.

    A coverage line that does not add up is worse than none: it would be quoted
    as evidence while double-counting or dropping items.
    """
    shapes = {
        "all matched": [_item("비트코인 급등"), _item("랜섬웨어 공격")],
        "none matched": [_item("정원 이야기"), _item("요리 이야기")],
        "mixed": [_item("비트코인 급등"), _item("정원 이야기"), _item("요리")],
    }
    for name, items in shapes.items():
        caplog.clear()
        with caplog.at_level(logging.INFO):
            _generate_trend_analysis(items, 7)
        line = next(r.message for r in caplog.records if "Trend coverage" in r.message)
        matched, total = map(int, re.search(r"coverage (\d+)/(\d+)", line).groups())
        unmatched = int(re.search(r"(\d+) unmatched", line).group(1))
        assert matched + unmatched == total == len(items), f"{name}: {line}"


def test_no_coverage_line_when_there_is_nothing_to_cover(caplog):
    """Avoid a 0/0 division and a meaningless log entry."""
    with caplog.at_level(logging.INFO):
        _generate_trend_analysis([], 7)
    assert not [r for r in caplog.records if "Trend coverage" in r.message]
