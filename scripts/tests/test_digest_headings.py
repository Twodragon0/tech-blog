#!/usr/bin/env python3
"""참고자료 헤딩은 정의가 하나여야 한다 — 표기가 둘이기 때문이다.

사건 (2026-09-19)
-----------------
`content_generator` 가 두 번째 표기를 쓰기 시작했다. 상호참조가 있으면
`## 관련 포스트 및 참고 자료`, 없으면 `## 참고 자료`. 소비자 넷이 옛 표기를 **정확
문자열**로 들고 있었고, 변형은 옛 문자열을 부분문자열로 포함하지 **않는다**. 그래서
넷 다 변형에 눈이 멀었다. 같은 날 실측: 변형을 단 포스트 13건 전부가 `## 참고 자료`
를 아예 갖고 있지 않았고, `enrich_digest_references` 는 13건 모두에서 섹션이 없다고
보고했다.

이건 CLAUDE.md 가 이름 붙여 둔 실패다 — *a content gate keyed to one exact string
is blind to the variant*. 고치는 방법은 "세 군데에 문자열을 하나씩 더 적기"가 아니다.
그건 목록만 길어진 같은 결함이고, 실제로 네 번째 소비자에서 그대로 재발했다
(`restore_digest_structure` 의 손복사본 — 멤버십 드리프트 가드가 통과시켰다).

그래서 이 파일이 검사하는 것은 두 가지다.

1. **구조**: 생산자와 소비자가 `scripts.lib.digest_headings` 를 읽는가. 리터럴을
   다시 적으면 여기서 걸린다.
2. **동작**: 각 소비자가 두 표기 **모두**에서 섹션을 찾는가. 1만 있으면 import 해
   놓고 안 쓰는 코드를 통과시키므로 공허해진다.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from scripts.lib.digest_headings import (  # noqa: E402
    REFERENCE_HEADING,
    REFERENCE_HEADING_RE,
    REFERENCE_HEADING_WITH_POSTS,
    REFERENCE_HEADINGS,
    is_reference_heading,
)
from scripts.lib.source_text import without_comments  # noqa: E402

# 생산자 1 + 소비자 4. 각 항목은 (경로, 그 파일이 써야 하는 이름들).
_SHARERS = {
    "scripts/news/content_generator.py": ("REFERENCE_HEADING_WITH_POSTS",),
    "scripts/enrich_digest_references.py": ("REFERENCE_HEADING_RE",),
    "scripts/backfill_digest_native_sections.py": ("is_reference_heading",),
    "scripts/backfill_digest_structure.py": ("REFERENCE_HEADING_ALTERNATION",),
}


@pytest.mark.parametrize("rel,names", sorted(_SHARERS.items()))
def test_every_site_reads_the_shared_definition(rel: str, names: tuple) -> None:
    """리터럴이 아니라 공용 모듈에서 읽어야 한다.

    주석을 접고 본다: 이 파일들은 사건을 설명하면서 옛 문자열을 인용하고 있고,
    단순 grep 은 인용을 사용과 구별하지 못한다 (`scripts/lib/source_text`).
    """
    src = without_comments((REPO_ROOT / rel).read_text(encoding="utf-8"), suffix=".py")
    assert "scripts.lib.digest_headings" in src, (
        f"{rel} 가 공용 정의를 읽지 않는다. 헤딩 표기를 직접 적으면 세 번째 표기가 "
        "생겼을 때 이 파일만 남겨진다 — 2026-09-19 에 네 파일이 그렇게 됐다."
    )
    for name in names:
        assert name in src, f"{rel} 가 {name} 를 쓰지 않는다."


@pytest.mark.parametrize("rel", sorted(_SHARERS))
def test_no_site_hardcodes_a_heading_spelling(rel: str) -> None:
    """공용 모듈을 import 해 놓고 옆에 리터럴을 남겨두는 것도 같은 결함이다."""
    src = without_comments((REPO_ROOT / rel).read_text(encoding="utf-8"), suffix=".py")
    for spelling in REFERENCE_HEADINGS:
        assert spelling not in src, (
            f"{rel} 가 {spelling!r} 를 코드에 직접 적고 있다. 공용 상수를 쓰라 — "
            "표기가 늘어날 때 갱신이 누락되는 지점이 정확히 여기다."
        )


def test_the_two_spellings_do_not_contain_each_other() -> None:
    """이 사건이 조용했던 이유. 부분문자열이었다면 옛 게이트가 그대로 잡았다."""
    assert REFERENCE_HEADING not in REFERENCE_HEADING_WITH_POSTS
    assert REFERENCE_HEADING_WITH_POSTS not in REFERENCE_HEADING


@pytest.mark.parametrize("heading", REFERENCE_HEADINGS)
def test_regex_and_predicate_agree_on_every_spelling(heading: str) -> None:
    assert is_reference_heading(heading)
    assert REFERENCE_HEADING_RE.search(f"본문\n\n{heading}\n\n표\n")


def test_regex_does_not_match_a_mention_inside_prose() -> None:
    """줄 시작 앵커가 필요한 이유 — 본문이나 표 셀의 언급은 섹션 헤더가 아니다."""
    assert not REFERENCE_HEADING_RE.search("아래 ## 참고 자료 절을 보라.\n")
    assert not REFERENCE_HEADING_RE.search("| 항목 | ## 참고 자료 |\n")


# --- 동작: 소비자가 두 표기 모두에서 섹션을 실제로 찾는가 -------------------

_BODY = """---
title: "t"
---

## 1. 보안 뉴스

### 1.1 기사

본문.

{heading}

| 자료 | 용도 |
|---|---|
| [원문](https://example.test/a) | 원문 |
"""


@pytest.mark.parametrize("heading", REFERENCE_HEADINGS)
def test_enrich_locates_the_section_under_both_spellings(heading: str) -> None:
    """2026-09-19 에 13건 전부가 '섹션 없음' 으로 보고된 바로 그 경로."""
    import enrich_digest_references as enrich

    assert enrich._split_reference_section(_BODY.format(heading=heading)) is not None, (
        f"{heading!r} 를 쓴 다이제스트에서 참고자료 섹션을 찾지 못했다."
    )


@pytest.mark.parametrize("heading", REFERENCE_HEADINGS)
def test_enrich_abort_check_compares_only_the_part_above(heading: str) -> None:
    """중단 검사가 공허해지지 않아야 한다.

    옛 코드는 `text.split("## 참고 자료")[0]` 이었다. 변형을 쓴 포스트에서는 분할이
    일어나지 않아 **문서 전체**가 반환됐고, 검사는 같은 문서 둘을 비교하게 되어
    섹션 밖 변경이 있어도 절대 발화할 수 없었다.
    """
    import enrich_digest_references as enrich

    text = _BODY.format(heading=heading)
    above = enrich._before_refs(text)
    assert above != text, "참고자료 위쪽만 잘라내야 하는데 문서 전체가 돌아왔다."
    assert heading not in above


@pytest.mark.parametrize("heading", REFERENCE_HEADINGS)
def test_native_sections_inserts_above_the_reference_section(heading: str) -> None:
    """체크리스트 삽입 지점. 헤딩을 못 찾으면 EOF 로 떨어져 참고자료 **아래**로 간다."""
    import backfill_digest_native_sections as native

    lines = _BODY.format(heading=heading).split("\n")
    idx = native._find_reference_line(lines)
    assert idx is not None, f"{heading!r} 를 삽입 지점으로 찾지 못했다."
    assert lines[idx].strip() == heading
