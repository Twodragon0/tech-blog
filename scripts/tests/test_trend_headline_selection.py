#!/usr/bin/env python3
"""Guard: `기타` is never the cycle's key trend, and one article is never a trend.

``기타`` collects the articles no trend keyword matched, so it is the absence of
a trend rather than one. Because the trend list is sorted by count it landed
first in **126 of the 174** published digests (72%), which is how
"이번 주기의 핵심 트렌드는 **기타**(12건)입니다" shipped that often — including
the 2026-09-09 cron digest, whose citation was ``기타``(12건).

It remains a TABLE ROW: the row counts have to account for every article. It is
only barred from the headline.

The `>= 2` floor is measured, not chosen for tidiness. Of the 120 such digests
that do have a real alternative, the alternative's size distributes as

    1건 13 · 2건 23 · 3건 29 · 4건 30 · 5건 16 · 6건 9

so at `>= 2`, 107 of 120 (89%) get a real headline and the remaining 13 fall
through to the no-trend sentence — the honest output when the only real trend is
a single article.

Scope, measured: this defect is confined to ``_generate_trend_analysis`` (the
security-mode generator, 181 posts). ``_generate_tech_trend_analysis`` (7 posts)
also writes a bolded ``(N건)`` citation in source, but all 7 of its published
posts headline a real trend (AI/ML, AI/LLM), and their trend names are not
bolded so the citation extractor does not see them at all. It is left alone
deliberately rather than by oversight.

Verdict: ``.omc/plans/etc-top-trend-citation-2026-09-09.md``
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from news import qa_gate
from news.content_generator import (
    _NO_PROMINENT_TREND,
    _TREND_CATCH_ALL,
    _TREND_HEADLINE_MIN,
    _generate_trend_analysis,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


def _item(title: str, category: str = "security", source: str = "Src") -> dict:
    return {
        "title": title,
        "summary": "",
        "content": "",
        "category": category,
        "source_name": source,
    }


def _run(items):
    content = _generate_trend_analysis(items, 7)
    rows, citations = qa_gate.extract_trend_rows_and_citations(content)
    return content, rows, citations


def test_the_constants_are_what_this_file_assumes():
    """Canary. Every assertion below is read against these two values."""
    assert _TREND_CATCH_ALL == "기타"
    assert _TREND_HEADLINE_MIN == 2, (
        "the headline floor moved. Re-measure the alternative-size distribution "
        "before accepting it: at 3 the real-headline share drops from 89% to "
        "70%, at 4 to 45%."
    )


def test_a_smaller_real_trend_beats_a_bigger_catch_all():
    """The defect this closes, end to end."""
    content, rows, citations = _run(
        [
            _item("랜섬웨어 공격 하나"),
            _item("랜섬웨어 공격 둘"),
            _item("정원 이야기 A", "tech"),
            _item("정원 이야기 B", "tech"),
            _item("정원 이야기 C", "tech"),
        ]
    )
    assert (_TREND_CATCH_ALL, 3) in rows, "기타 must still be a table row"
    assert ("랜섬웨어", 2) in rows
    assert citations == [("랜섬웨어", 2)], (
        f"expected the real trend to be headlined over the larger catch-all, "
        f"got {citations}"
    )
    assert f"핵심 트렌드는 **{_TREND_CATCH_ALL}**" not in content


def test_the_catch_all_keeps_its_row_so_the_counts_still_add_up():
    """Barring it from the headline must not remove it from the table.

    The row exists so the trend counts account for every article; dropping it
    would make the table silently under-report the digest.
    """
    content, rows, _citations = _run(
        [_item("랜섬웨어 하나"), _item("랜섬웨어 둘"), _item("정원", "tech")]
    )
    assert (_TREND_CATCH_ALL, 1) in rows
    assert f"| **{_TREND_CATCH_ALL}** | 1건" in content


@pytest.mark.parametrize(
    "items, why",
    [
        ([_item("정원 이야기", "tech")], "only the catch-all exists"),
        (
            [_item("랜섬웨어 하나"), _item("제로데이 하나")],
            "every real trend has a single article",
        ),
        (
            [_item("랜섬웨어 하나"), _item("정원 A", "tech"), _item("정원 B", "tech")],
            "the one real trend is below the floor and the catch-all is bigger",
        ),
        ([], "there are no articles at all"),
    ],
)
def test_nothing_worth_headlining_says_so(items, why):
    content, _rows, citations = _run(items)
    assert citations == [], f"{why}: expected no citation, got {citations}"
    assert _NO_PROMINENT_TREND in content, why


def test_the_floor_is_exclusive_at_one_and_inclusive_at_two():
    """Boundary, both sides — a floor asserted on one side can be off by one."""
    _c1, _r1, at_one = _run([_item("랜섬웨어 하나"), _item("정원", "tech")])
    assert at_one == [], f"a single-article trend was headlined: {at_one}"

    _c2, _r2, at_two = _run([_item("랜섬웨어 하나"), _item("랜섬웨어 둘")])
    assert at_two == [("랜섬웨어", 2)], (
        f"a two-article trend must be headlined, got {at_two}"
    )


def test_the_largest_eligible_trend_is_the_one_headlined():
    """Ordering survives the filter."""
    _content, rows, citations = _run(
        [
            _item("랜섬웨어 하나"),
            _item("랜섬웨어 둘"),
            _item("제로데이 하나"),
            _item("제로데이 둘"),
            _item("제로데이 셋"),
        ]
    )
    assert ("제로데이", 3) in rows and ("랜섬웨어", 2) in rows
    assert citations == [("제로데이", 3)], citations


def test_the_filter_reads_the_constants_and_not_inline_literals():
    """So the two names above cannot drift from what the generator applies."""
    source = (REPO_ROOT / "scripts" / "news" / "content_generator.py").read_text(
        encoding="utf-8"
    )
    # Terminate on the list's closing bracket at the start of a line, not on
    # the first `]` — a non-greedy `(.+?)\s*\]` stops inside `t[0]` and captures
    # the string "t[0", which then fails for a reason that has nothing to do
    # with the invariant.
    match = re.search(
        r"headline_pool = \[\s*t\s*for t in trend_results\s*if (.+?)\n\s*\]",
        source,
        re.S,
    )
    assert match, "the headline filter was restructured; re-anchor this guard"
    condition = " ".join(match.group(1).split())
    assert condition == ("t[0] != _TREND_CATCH_ALL and t[1] >= _TREND_HEADLINE_MIN"), (
        f"the headline filter now reads {condition!r}. Keep it on the named "
        "constants so test_the_constants_are_what_this_file_assumes stays "
        "load-bearing."
    )


def test_no_published_digest_headlines_the_catch_all_any_more():
    """Corpus ratchet, not a clean-corpus claim.

    The 126 already-published digests keep their `기타` headline: the fix
    changes the generator, not history, and rewriting 126 posts' prose is a
    separate decision. So the count is pinned rather than driven to zero — a
    NEW one can only come from a generator regression, which is the thing worth
    catching. Backfilling later should lower this number, never raise it.
    """
    offenders = []
    for post in sorted((REPO_ROOT / "_posts").glob("*.md")):
        _rows, citations = qa_gate.extract_trend_rows_and_citations(
            post.read_text(encoding="utf-8")
        )
        if citations and citations[0][0].strip() == _TREND_CATCH_ALL:
            offenders.append(post.name)
    # Recorded, not asserted away: 126 measured on 2026-09-09.
    assert len(offenders) <= 126, (
        f"{len(offenders)} digests headline the catch-all, up from the 126 "
        "measured when the generator was fixed. A NEW one means the generator "
        "regressed — the fix only covers posts written after it."
    )
