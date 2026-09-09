#!/usr/bin/env python3
"""Guard: the trend table and the prose citations stay one source.

``_generate_trend_analysis`` renders ``trend_results`` twice — once as table
rows, once as a prose citation — and ``_assert_trend_single_source`` re-reads
both to prove they agree. These tests pin that assertion, and pin the extractor
it leans on.

Why an assertion here instead of promoting the gate
---------------------------------------------------
``validate_trend_analysis`` was left advisory on purpose: promotion needs a
self-heal, and the only repair anyone could name (rewrite the citation to the
table's largest row) was rejected by the corpus, because two hand-edited posts
headline a smaller-but-better trend and one post's numeric top is the catch-all
``기타``. See ``.omc/plans/advisory-rules-promotion-verdict-2026-09-08.md``.

The order of business below matters. The membership check —
"every citation is a table row" — is satisfied by recovering NO citations at
all, and that vacuity was live: a pipe inside an article title moved the
prose-slice boundary and swallowed the first citation, after which the gate
reported zero issues for a post it had read half of. So the extractor is
attacked first, then the count, then membership.
"""

from __future__ import annotations

import io
import re
import tokenize
from pathlib import Path

import pytest
from news import qa_gate
from news.content_generator import (
    _assert_trend_single_source,
    _generate_trend_analysis,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GENERATOR = REPO_ROOT / "scripts" / "news" / "content_generator.py"


def _item(title: str, category: str = "security", source: str = "Src") -> dict:
    return {
        "title": title,
        "summary": "",
        "content": "",
        "category": category,
        "source_name": source,
    }


# Every distinct path through the prose builder, found by reading the branches
# rather than by guessing: one trend, several trends, `기타` only, `기타` second
# (the two-citation branch), and the dynamic-text path where an article title
# reaches the prose verbatim.
GENERATOR_PATHS = {
    "several trends": [
        _item("Kubernetes zero-day container escape"),
        _item("AWS cloud IAM misconfiguration"),
        _item("New ransomware campaign"),
        _item("LLM prompt injection bypass", "ai"),
        _item("Supply chain attack on npm"),
    ],
    "single trend": [_item("Ransomware group leaks data")],
    "기타 only": [_item("An entirely unrelated gardening story", "tech")],
    "기타 second (two citations)": [
        _item("컨테이너 취약점 하나"),
        _item("컨테이너 취약점 둘"),
        _item("정원 가꾸기 이야기", "tech"),
    ],
    "korean titles (dynamic text live)": [
        _item("쿠버네티스 제로데이 컨테이너 탈출 취약점 공개"),
        _item("랜섬웨어 조직이 병원을 공격했다"),
    ],
    "title containing a pipe": [
        _item("쿠버네티스 | 치명적 RCE 패치 공개"),
        _item("랜섬웨어 | 이중 협박 재확산"),
    ],
    "title containing asterisks": [
        _item("쿠버네티스 **치명적** RCE 공개"),
        _item("랜섬웨어 **신종** 변종 등장"),
    ],
    "no news at all": [],
}


# ---------------------------------------------------------------------------
# 1. Attack the extractor first
# ---------------------------------------------------------------------------


def test_the_extractor_reads_a_known_section():
    """Canary. If this collapses, every assertion below passes vacuously."""
    content = _generate_trend_analysis(GENERATOR_PATHS["several trends"], 7)
    rows, citations = qa_gate.extract_trend_rows_and_citations(content)
    assert len(rows) >= 2, f"row extraction collapsed to {rows}"
    assert len(citations) >= 1, f"citation extraction collapsed to {citations}"


def test_prose_is_sliced_at_the_last_row_line_not_the_last_pipe():
    """The bug this replaced, in isolation.

    ``block.rfind("|")`` treats a pipe as "end of table" wherever it occurs.
    Here the pipe sits in the prose, so the character-based slice starts after
    it and loses everything before — including a whole citation.
    """
    block = (
        "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        "|--------|-------------|------------|\n"
        "| **랜섬웨어** | 1건 | 랜섬웨어 | 이중 협박 재확산 |\n"
        "\n"
        "이번 주기의 핵심 트렌드는 **랜섬웨어**(1건)입니다. "
        "랜섬웨어 | 이중 협박 재확산 등이 주요 이슈입니다.\n"
    )
    prose = qa_gate._trend_prose(block)
    assert "핵심 트렌드는" in prose, (
        "the prose slice lost the sentence that carries the citation"
    )
    assert "| 트렌드 |" not in prose, "the slice leaked the table header back in"

    old_slice = block[block.rfind("|") + 1 :]
    assert not qa_gate._TREND_CITATION_RE.findall(old_slice), (
        "this fixture no longer reproduces the old behaviour, so it has stopped "
        "guarding anything — rebuild it around a pipe that sits in the prose"
    )
    assert qa_gate._TREND_CITATION_RE.findall(prose), (
        "the new slice must recover the citation the old one dropped"
    )


def test_the_pipe_case_recovers_both_citations_end_to_end():
    """The same defect through the real generator, not a hand-built block."""
    content = _generate_trend_analysis(GENERATOR_PATHS["title containing a pipe"], 7)
    assert " | " in content, "the fixture's pipe did not reach the output"
    _rows, citations = qa_gate.extract_trend_rows_and_citations(content)
    assert len(citations) == 2, (
        f"expected both citations to be readable, got {citations}"
    )


# ---------------------------------------------------------------------------
# 2. The generator satisfies its own assertion on every path
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("items", GENERATOR_PATHS.values(), ids=GENERATOR_PATHS.keys())
def test_generator_output_holds_the_invariant(items):
    """No AssertionError, and the citations really are table rows."""
    content = _generate_trend_analysis(items, 7)
    rows, citations = qa_gate.extract_trend_rows_and_citations(content)
    for cited in citations:
        assert cited in rows, f"{cited} is cited but is not a row of {rows}"


def test_the_two_citation_branch_is_actually_exercised():
    """Control for the parametrization above.

    Without this, "every path holds" would be satisfied by a fixture set that
    never reaches the second citation — the branch most likely to drift, since
    it only fires when the runner-up trend has no representative titles.
    """
    content = _generate_trend_analysis(
        GENERATOR_PATHS["기타 second (two citations)"], 7
    )
    _rows, citations = qa_gate.extract_trend_rows_and_citations(content)
    assert len(citations) == 2, (
        f"the second-citation branch stopped firing for this fixture: {citations}"
    )
    assert "도 주목할 트렌드입니다" in content


# ---------------------------------------------------------------------------
# 3. The assertion is not vacuous
# ---------------------------------------------------------------------------

_TABLE = (
    "\n---\n\n## 7. 트렌드 분석\n\n"
    "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
    "|--------|-------------|------------|\n"
    "| **랜섬웨어** | 2건 | 랜섬웨어 |\n"
    "| **기타** | 1건 | 기타 주제 |\n\n"
)


def test_assertion_passes_on_agreeing_content():
    """Control. A guard that rejects everything is not measuring agreement."""
    content = _TABLE + "이번 주기의 핵심 트렌드는 **랜섬웨어**(2건)입니다.\n\n"
    _assert_trend_single_source(content, [("랜섬웨어", 2)])


def test_assertion_catches_a_citation_that_is_not_a_row():
    content = _TABLE + "이번 주기의 핵심 트렌드는 **제로데이**(2건)입니다.\n\n"
    with pytest.raises(AssertionError, match="not in the table"):
        _assert_trend_single_source(content, [("제로데이", 2)])


def test_assertion_catches_a_count_that_disagrees_with_its_row():
    """Same name, different number — the citation contradicts the table."""
    content = _TABLE + "이번 주기의 핵심 트렌드는 **랜섬웨어**(9건)입니다.\n\n"
    with pytest.raises(AssertionError, match="not in the table"):
        _assert_trend_single_source(content, [("랜섬웨어", 9)])


def test_assertion_catches_a_citation_that_cannot_be_read_back():
    """The vacuity half: written but unreadable.

    This is what the membership check alone cannot see, because recovering
    nothing satisfies "every recovered citation is a row".
    """
    content = _TABLE + "이번 주기의 핵심 트렌드는 랜섬웨어 2건입니다.\n\n"
    with pytest.raises(AssertionError, match="round-trip lost one"):
        _assert_trend_single_source(content, [("랜섬웨어", 2)])


# ---------------------------------------------------------------------------
# 4. The wiring cannot be dropped, and the two sides cannot drift apart
# ---------------------------------------------------------------------------


def _code_only(source: str) -> str:
    """Blank comments and string literals, preserving offsets.

    So that a source guard does not trip on prose that merely quotes the thing
    it forbids — the mistake that broke ``test_inline_gate_registry`` once.
    """
    lines = source.splitlines(keepends=True)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line))
    out = list(source)
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type not in (tokenize.COMMENT, tokenize.STRING):
            continue
        (srow, scol), (erow, ecol) = token.start, token.end
        for i in range(starts[srow - 1] + scol, min(starts[erow - 1] + ecol, len(out))):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def test_the_generator_still_calls_the_assertion():
    """A silently removed call would leave every test above still passing.

    They all re-derive the invariant themselves; only this one proves the
    generator is the thing enforcing it.
    """
    source = _code_only(GENERATOR.read_text(encoding="utf-8"))
    calls = re.findall(r"_assert_trend_single_source\(", source)
    assert len(calls) == 2, (
        f"expected exactly 2 occurrences (the def and one call), found "
        f"{len(calls)}. If the call was removed, the trend table and its prose "
        f"can diverge again with nothing objecting."
    )


def test_the_generator_does_not_re_implement_the_extractor():
    """One extractor, shared. Two would agree with each other and drift from the gate."""
    source = _code_only(GENERATOR.read_text(encoding="utf-8"))
    assert "extract_trend_rows_and_citations" in source, (
        "the generator stopped using the gate's extractor"
    )
    assert "건\\)" not in source and "건 \\|" not in source, (
        "the generator appears to carry its own citation/row pattern. Use "
        "qa_gate.extract_trend_rows_and_citations so the assertion and the "
        "gate cannot disagree."
    )


def test_the_gate_uses_the_same_extractor():
    """The other direction of the same requirement."""
    source = _code_only(
        (REPO_ROOT / "scripts" / "news" / "qa_gate.py").read_text("utf-8")
    )
    body = source[source.index("def validate_trend_analysis") :]
    body = body[: body.index("def run_qa_gate")]
    assert "extract_trend_rows_and_citations" in body, (
        "validate_trend_analysis no longer reads through the shared extractor, "
        "so the generator's assertion and the publish gate can now disagree"
    )
    assert "rfind" not in body, "the character-based prose slice came back"
