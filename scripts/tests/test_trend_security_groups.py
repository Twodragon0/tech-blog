#!/usr/bin/env python3
"""Guard: the three security trend groups, and the audit behind each keyword.

A security digest had no trend group for "vulnerability", none for "malware",
and none for "data leak". 165 of the then-1274 unmatched card titles fell into
these three — re-measured against the post-blockchain baseline rather than
reused from the original research, which said 188 before the blockchain group
absorbed 23 of them.

Two things this file pins that a keyword list alone does not say:

* **What was rejected, and why.** Seven candidates yielded exactly zero and are
  kept out on the same rule that removed `blockchain` and `etf`. The corpus is
  Korean-translated, so an English synonym of a covered Korean term never fires.
* **That a generic group does not displace a specific one.** `취약점/CVE` could
  swallow the headline the way `기타` did, since a zero-day is also a
  vulnerability. Simulated over 203 digests: 7 headlines change and none is
  taken from 제로데이 or 랜섬웨어.

Research: ``.omc/research/trend-defs-coverage-2026-09-09.md``
"""

from __future__ import annotations

import re

import pytest
from news import qa_gate
from news.content_generator import _generate_trend_analysis

EXPECTED = {
    "취약점/CVE": ["cve-", "취약점", "rce", "sqli"],
    "악성코드/피싱": ["악성", "malware", "피싱", "rat", "botnet"],
    "데이터 유출": ["유출", "노출", "leak"],
}

# Rejected candidates with the measurement that rejected each.
ZERO_YIELD = [
    "vulnerability",
    "vulnerabilities",
    "xss",
    "phishing",
    "트로이",
    "breach",
    "exposed",
]

REDUNDANT = {
    "악성코드": "`악성` subsumes it as a substring, so listing both is "
    "redundant rather than additive",
}


def _item(title: str, category: str = "security", source: str = "Src") -> dict:
    return {
        "title": title,
        "summary": "",
        "content": "",
        "category": category,
        "source_name": source,
    }


def _defs_source() -> str:
    """The ``trend_defs`` literal with comments removed.

    Removing them is not tidiness. The first version of this file read the raw
    text and ``test_a_zero_yield_candidate_stays_out[vulnerability]`` failed —
    not because the keyword was added, but because a comment a few lines above
    says `none for "vulnerability"`. A source guard that also reads its own
    commentary trips on prose, which is the same trap
    ``test_inline_gate_registry._code_only`` was written for. That helper is not
    importable here (conftest puts ``scripts/`` on the path, not
    ``scripts/tests/``), so this is a deliberate second copy of the idea, kept
    small: within this literal every comment occupies a whole line and no
    keyword contains ``#``, both asserted below.
    """
    import inspect

    source = inspect.getsource(_generate_trend_analysis)
    match = re.search(r"trend_defs = \{(.+?)\n    \}", source, re.S)
    assert match, "trend_defs was restructured; re-anchor this guard"
    body = match.group(1)

    code = "\n".join(
        line for line in body.splitlines() if not line.lstrip().startswith("#")
    )
    assert "#" not in code, (
        "a `#` survived comment stripping, so either a keyword contains one or "
        "an inline comment appeared. Line-based stripping is no longer safe "
        "here — switch to tokenize."
    )
    return code


def _rows(items):
    rows, _citations = qa_gate.extract_trend_rows_and_citations(
        _generate_trend_analysis(items, 7)
    )
    return rows


# ---------------------------------------------------------------------------
# Definition
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("group", EXPECTED)
def test_the_group_is_declared(group):
    assert f'"{group}"' in _defs_source(), f"{group} is gone from trend_defs"


@pytest.mark.parametrize(
    "group,keyword",
    [(g, k) for g, kws in EXPECTED.items() for k in kws],
    ids=[f"{g}:{k}" for g, kws in EXPECTED.items() for k in kws],
)
def test_each_kept_keyword_is_present(group, keyword):
    assert f'"{keyword}"' in _defs_source(), (
        f"{keyword!r} was dropped from {group}. Every keyword here yields at "
        "least one corpus match — re-measure before removing."
    )


@pytest.mark.parametrize("keyword", ZERO_YIELD)
def test_a_zero_yield_candidate_stays_out(keyword):
    assert f'"{keyword}"' not in _defs_source(), (
        f"{keyword!r} was added. It matched exactly ZERO corpus titles — the "
        "corpus is Korean-translated, so English synonyms of covered Korean "
        "terms never fire. Same rule that keeps `blockchain` and `etf` out."
    )


@pytest.mark.parametrize("keyword,why", REDUNDANT.items())
def test_a_redundant_keyword_stays_out(keyword, why):
    assert f'"{keyword}"' not in _defs_source(), f"{keyword!r} was added: {why}."


def test_the_subsumption_claim_is_true():
    """`악성코드` is excluded on a substring claim; check the claim itself."""
    assert "악성" in "악성코드"
    assert "악성" in "악성코드 캠페인, RAT 배포".lower()


# ---------------------------------------------------------------------------
# Behaviour on real titles (verbatim from published digests)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "group,title",
    [
        (
            "취약점/CVE",
            "[보안] n8n 치명적 취약점 CVE-2026-25049, 악성 워크플로로 시스템 명령 실행 가능",
        ),
        (
            "취약점/CVE",
            "[보안] Fortinet, CVE-2026-21643 Critical SQLi 취약점 긴급 패치",
        ),
        (
            "악성코드/피싱",
            "[보안] DEAD#VAX 악성코드 캠페인, IPFS 기반 피싱으로 AsyncRAT 배포",
        ),
        ("악성코드/피싱", "[보안] APT36/SideCopy 크로스플랫폼 RAT 캠페인"),
        (
            "악성코드/피싱",
            "[보안] 악성 NGINX 설정을 악용한 대규모 웹 트래픽 하이재킹 캠페인",
        ),
        ("데이터 유출", "[보안] JWT 서명키 유출: 전체 인증 체계 침해"),
        (
            "데이터 유출",
            "인터넷에 노출된 24,650개의 BMC가 로그인 전 IPMI 비밀번호 해시를 노출",
        ),
    ],
)
def test_a_real_title_reaches_its_group(group, title):
    rows = _rows([_item(title), _item(title + " (속보)")])
    assert any(name == group for name, _count in rows), (
        f"{title!r} did not classify as {group}; rows={sorted(rows)}"
    )


def test_rat_is_word_boundary_matched_not_a_substring():
    """`rat` is three characters, so the matcher requires a word boundary.

    All 12 corpus hits are genuine Remote Access Trojan stories. This pins the
    boundary behaviour rather than the audit result, because it is the boundary
    that keeps the audit true for titles not yet written.
    """
    inside_a_word = "Corporate strategy 발표"  # contains "rat" in "Corporate"
    rows = _rows([_item(inside_a_word), _item(inside_a_word + " 후속")])
    assert not any(name == "악성코드/피싱" for name, _c in rows), (
        f"'{inside_a_word}' matched the malware group — `rat` is matching as a "
        f"substring, not a word. rows={sorted(rows)}"
    )


def test_a_fund_outflow_is_not_forced_into_the_data_leak_group_alone():
    """The one audited exception, recorded as behaviour.

    `유출` matches fund-outflow stories too: 20 of the 21 newly-matched titles
    are genuine data leaks, and this one is a market story.

    The first draft of this test asserted the blockchain group already gave it a
    home, so the cost was only a double count. **That was wrong** — it was
    inferred from an aggregate overlap count without checking this title, which
    carries `ETH` and `바이낸스`, neither of which was a blockchain keyword. It
    really was landing in 데이터 유출 alone: a fund outflow filed as a data leak.

    Adding the `btc` and `eth` tickers fixed it at the source, so the claim is
    now true and this test is what keeps it true.
    """
    title = "바이낸스 자금 유출 3배 증가한 12억 달러, ETH 인출 3년래 최고치 기록"
    rows = _rows([_item(title), _item(title + " 후속")])
    names = {name for name, _c in rows}
    assert "데이터 유출" in names, "the audited behaviour changed; re-run the audit"
    assert "블록체인/암호화폐" in names, (
        "the fund-outflow title lost its blockchain classification, which is "
        "what made the 유출 false positive tolerable"
    )


# ---------------------------------------------------------------------------
# The second-order risk: a generic group taking the headline
# ---------------------------------------------------------------------------


def test_a_specific_trend_still_outranks_the_generic_one_at_equal_size():
    """A zero-day is also a 취약점, so both groups count the same article.

    With equal counts the generic group must not win. `max` is stable on the
    first of the equals, so this depends on declaration order — 제로데이 is
    declared before 취약점/CVE, and this test is what makes that ordering
    load-bearing instead of incidental.
    """
    items = [
        _item("Chrome 제로데이 취약점 긴급 패치"),
        _item("Windows 제로데이 취약점 악용 확인"),
    ]
    content = _generate_trend_analysis(items, 7)
    rows, citations = qa_gate.extract_trend_rows_and_citations(content)
    assert ("제로데이", 2) in rows and ("취약점/CVE", 2) in rows, sorted(rows)
    assert citations == [("제로데이", 2)], (
        f"the generic group took the headline from 제로데이 at equal size: "
        f"{citations}. Check the declaration order in trend_defs."
    )


def test_the_generic_group_is_declared_after_the_specific_ones():
    """The ordering the test above relies on, asserted directly."""
    names = re.findall(r'^        "([^"]+)":', _defs_source(), re.M)
    for specific, generic in (
        ("제로데이", "취약점/CVE"),
        ("랜섬웨어", "악성코드/피싱"),
    ):
        assert names.index(specific) < names.index(generic), (
            f"{generic} is now declared before {specific}. At equal counts the "
            f"generic group would take the headline, which is the failure mode "
            f"`기타` used to cause."
        )
