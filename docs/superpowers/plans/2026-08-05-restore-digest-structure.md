# Digest 구조 무손실 복원 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 레거시 digest 125개의 구조 위반 601건을 **독자 노출 텍스트를 삭제하지 않고** 결정적 변환으로 해소한다 (티어 A/B/C/E 117개, 601 → 8).

**Architecture:** 신규 스크립트 `scripts/restore_digest_structure.py`가 5개 무손실 룰(R1~R5)을 순서대로 적용한다. 기존 `scripts/backfill_digest_structure.py`와 LLM 발행 경로(`scripts/news/content_generator.py`)는 **수정하지 않는다** — 그 경로의 `transform_body`는 체크박스 블록을 *삭제*하므로 무손실 정책과 의미가 다르다. 공유 정규식은 복제하되 drift 가드 테스트로 동기화를 강제한다.

**Tech Stack:** Python 3.11 stdlib(`re`, `argparse`, `pathlib`, `subprocess`), pytest.

## Global Constraints

- **무손실**: 독자에게 보이는 텍스트를 삭제하지 않는다. 헤딩→볼드, 체크박스→불릿처럼 마커만 바꾼다.
- **스코프**: `_is_digest_post`(파일명에 `Weekly_Digest` 포함)만 대상. 비-digest 포스트는 건드리지 않는다.
- **`backfill_digest_structure.py` 및 `scripts/news/**` 무변경.**
- **`check_digest_structure.py` 무변경** — 게이트를 약화하지 않는다.
- **멱등**: `transform(transform(x)) == transform(x)`.
- **커밋 메시지**: `Co-Authored-By: Claude` 금지 (CLAUDE.md). conventional commits.
- **pre-commit이 자동 실행**되므로 `_posts/` 커밋 시 게이트 통과가 강제된다.
- 티어 D 8개(`실무 체크리스트` 부재 = 섹션 생성 필요)는 **이 계획의 범위 밖**.

---

### Task 1: 스캐폴드 + R1 (item 영역 헤딩 강등)

**Files:**
- Create: `scripts/restore_digest_structure.py`
- Test: `scripts/tests/test_restore_digest_structure.py`

**Interfaces:**
- Consumes: `scripts/backfill_digest_structure.py`의 `_split_front_matter`, `_split_preserved_segments` (import)
- Produces:
  - `ITEM_HEADING_RE: re.Pattern` — `^### \d+\.\d+`
  - `TOP_SECTION_RE: re.Pattern` — 최상위 섹션 whitelist
  - `demote_item_headings(text: str) -> str` (R1)
  - `transform(text: str) -> str` — Task 6에서 R1~R5를 합성

- [ ] **Step 1: 실패하는 테스트 작성**

`scripts/tests/test_restore_digest_structure.py`:

```python
"""Tests for scripts/restore_digest_structure.py (lossless structure restore).

Contract (docs/superpowers/specs/2026-08-04-digest-structure-backfill-design.md):
  - R1..R5 are LOSSLESS: reader-visible text is never deleted, only markers change
  - item-region scoped: section intros / global checklist are untouched
  - idempotent
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from restore_digest_structure import (  # noqa: E402
    demote_item_headings,
)

_FM = '---\ntitle: "x"\n---\n'


def test_demotes_h1_inside_item_region():
    body = (
        "## 1. 보안 뉴스\n"
        "### 1.1 어떤 기사\n"
        "# DevSecOps 관점 분석: 안드로이드 스파이 도구\n"
        "본문.\n"
    )
    out = demote_item_headings(_FM + body)
    assert "#### DevSecOps 관점 분석: 안드로이드 스파이 도구" in out
    # heading TEXT survives verbatim (lossless)
    assert "DevSecOps 관점 분석: 안드로이드 스파이 도구" in out


def test_does_not_touch_top_level_section_heading():
    body = "## 1. 보안 뉴스\n### 1.1 기사\n본문.\n## 실무 체크리스트\n- [ ] 항목\n"
    out = demote_item_headings(_FM + body)
    assert "## 1. 보안 뉴스" in out
    assert "## 실무 체크리스트" in out


def test_does_not_touch_headings_outside_item_region():
    # 경영진 브리핑 등 섹션 intro는 item 영역이 아니므로 verbatim.
    body = "## 경영진 브리핑\n### 이번 주 하이라이트\n요약.\n"
    out = demote_item_headings(_FM + body)
    assert "### 이번 주 하이라이트" in out


def test_front_matter_preserved():
    out = demote_item_headings(_FM + "## 1. 보안 뉴스\n")
    assert out.startswith(_FM)
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'restore_digest_structure'`

- [ ] **Step 3: 최소 구현**

`scripts/restore_digest_structure.py`:

```python
#!/usr/bin/env python3
"""Lossless structural restore for legacy digest posts.

WHY THIS IS NOT backfill_digest_structure.py
--------------------------------------------
backfill_digest_structure.transform_body (the LLM publish path, PR #452) resolves
the per-item checklist defect by DELETING the checkbox block. Measured on the
corpus that path takes 601 violations to 21 — but 211 of them by removing
reader-visible content. Owner decision (2026-08-04) is lossless restore only, so
this module converts markers instead:

    R1  item-region '#'/'##'/'###' non-section heading  ->  '####'
    R2  '#{1,4} 대응 체크리스트'                        ->  '**대응 체크리스트**'
    R3  item-region '- [ ] x'                          ->  '- x'
    R4  remaining top-level '## N.' sections           ->  renumbered 1..N
    R5  '## N. 실무 체크리스트'                         ->  '## 실무 체크리스트'

Order matters: R1 before R2 (R1 demotes '## 대응 체크리스트' to '####', which R2
must still catch), and R4 before R5 (R5 removes a number, which would otherwise
shift R4's contiguity calculation).

backfill_digest_structure.py and scripts/news/** are NOT modified. See
docs/superpowers/specs/2026-08-04-digest-structure-backfill-design.md.
"""
import argparse
import glob
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from scripts.backfill_digest_structure import (  # noqa: E402
    _split_front_matter,
    _split_preserved_segments,
)

# Copied from backfill_digest_structure.transform_body, where they are
# function-local and cannot be imported. test_restore_digest_structure.py has a
# drift guard (Task 7) that fails if the two definitions diverge.
ITEM_HEADING_RE = re.compile(r"^### \d+\.\d+")
TOP_SECTION_RE = re.compile(
    r"^(## \d+\. (보안|AI/ML|클라우드|DevOps|블록체인|기타|트렌드|"
    r"GeekNews|Open Source)|"
    r"## 실무 체크리스트|## 서론|## 분석가 시점|## 경영진 브리핑|"
    r"## 위험 스코어카드|## 참고 자료|## 📊)"
)

_ANY_HEADING_RE = re.compile(r"^(#{1,4})\s+(.*)$")


def demote_item_headings(text: str) -> str:
    """R1: inside an item region, demote a stray #/##/### heading to ####.

    An item region opens at '### N.M ...' and closes at the next whitelisted
    top-level section heading. Outside an item region every line is verbatim,
    which is what preserves section intros ('### 이번 주 하이라이트' etc).
    The item heading itself is the region delimiter, not part of the body.
    """
    front, body = _split_front_matter(text)
    out = []
    in_item = False
    for line in body.split("\n"):
        if ITEM_HEADING_RE.match(line):
            in_item = True
            out.append(line)
            continue
        if TOP_SECTION_RE.match(line):
            in_item = False
            out.append(line)
            continue
        m = _ANY_HEADING_RE.match(line)
        if in_item and m and len(m.group(1)) < 4:
            out.append(f"#### {m.group(2)}")
        else:
            out.append(line)
    return front + "\n".join(out)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: `4 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/restore_digest_structure.py scripts/tests/test_restore_digest_structure.py
git commit -m "feat(digest): R1 무손실 헤딩 강등 — item 영역 내 stray 헤딩을 ####로"
```

---

### Task 2: R2 (`대응 체크리스트` 헤딩 → 볼드)

**Files:**
- Modify: `scripts/restore_digest_structure.py`
- Test: `scripts/tests/test_restore_digest_structure.py`

**Interfaces:**
- Consumes: Task 1의 `_ANY_HEADING_RE`
- Produces: `boldify_response_checklist(text: str) -> str`

- [ ] **Step 1: 실패하는 테스트 작성**

`scripts/tests/test_restore_digest_structure.py`의 import에 `boldify_response_checklist` 추가하고 아래를 append:

```python
def test_boldifies_response_checklist_heading():
    # 게이트는 '#{2,4} 대응 체크리스트' 헤딩을 결함으로 잡는다. 텍스트는 살리고
    # 헤딩만 볼드 강조로 바꾼다 (무손실).
    body = "#### 대응 체크리스트\n- 패치 적용\n"
    out = boldify_response_checklist(_FM + body)
    assert "**대응 체크리스트**" in out
    assert "#### 대응 체크리스트" not in out
    assert "- 패치 적용" in out


def test_boldifies_two_hash_form_too():
    # R1이 강등하지 못한 경우(item 영역 밖)도 게이트는 '## 대응 체크리스트'를 잡는다.
    out = boldify_response_checklist(_FM + "## 대응 체크리스트\n본문.\n")
    assert "**대응 체크리스트**" in out


def test_leaves_other_headings_alone():
    out = boldify_response_checklist(_FM + "#### 권장 조치\n- 패치.\n")
    assert "#### 권장 조치" in out
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: FAIL — `ImportError: cannot import name 'boldify_response_checklist'`

- [ ] **Step 3: 최소 구현**

`scripts/restore_digest_structure.py`에 추가:

```python
_RESP_HEADING_RE = re.compile(r"^#{1,4}\s+(.*대응 체크리스트.*?)\s*$")


def boldify_response_checklist(text: str) -> str:
    """R2: a per-item '대응 체크리스트' HEADING becomes bold emphasis.

    The gate flags the heading form (`^#{2,4}\\s+.*대응 체크리스트`), not the
    content. Converting to '**...**' keeps every word the reader sees while
    removing the heading that made it a second checklist surface.
    """
    front, body = _split_front_matter(text)
    out = []
    for line in body.split("\n"):
        m = _RESP_HEADING_RE.match(line)
        out.append(f"**{m.group(1)}**" if m else line)
    return front + "\n".join(out)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: `7 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/restore_digest_structure.py scripts/tests/test_restore_digest_structure.py
git commit -m "feat(digest): R2 대응 체크리스트 헤딩을 볼드로 — 텍스트 보존"
```

---

### Task 3: R3 (item 영역 체크박스 → 불릿)

**Files:**
- Modify: `scripts/restore_digest_structure.py`
- Test: `scripts/tests/test_restore_digest_structure.py`

**Interfaces:**
- Consumes: `ITEM_HEADING_RE`, `TOP_SECTION_RE`
- Produces: `unbox_item_checkboxes(text: str) -> str`

- [ ] **Step 1: 실패하는 테스트 작성**

import에 `unbox_item_checkboxes` 추가하고 append:

```python
def test_unboxes_checkbox_inside_item_region():
    body = (
        "## 1. 보안 뉴스\n"
        "### 1.1 기사\n"
        "- [ ] 패치 적용\n"
        "- [x] 로그 점검\n"
    )
    out = unbox_item_checkboxes(_FM + body)
    assert "- 패치 적용" in out and "- 로그 점검" in out
    assert "[ ]" not in out and "[x]" not in out


def test_keeps_global_checklist_checkboxes():
    # 전역 '## 실무 체크리스트' 하위 체크박스는 정당한 산출물이므로 보존.
    body = (
        "## 1. 보안 뉴스\n"
        "### 1.1 기사\n"
        "본문.\n"
        "## 실무 체크리스트\n"
        "- [ ] 전역 항목\n"
    )
    out = unbox_item_checkboxes(_FM + body)
    assert "- [ ] 전역 항목" in out


def test_preserves_checkbox_text_exactly():
    body = "## 1. 보안 뉴스\n### 1.1 기사\n- [ ]   여백 있는 항목\n"
    out = unbox_item_checkboxes(_FM + body)
    assert "여백 있는 항목" in out
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: FAIL — `ImportError: cannot import name 'unbox_item_checkboxes'`

- [ ] **Step 3: 최소 구현**

```python
_ITEM_CHECKBOX_RE = re.compile(r"^(\s*)-\s*\[[ xX]?\]\s*(.*)$")


def unbox_item_checkboxes(text: str) -> str:
    """R3: inside an item region, '- [ ] x' becomes a plain '- x' bullet.

    Scoped to item regions on purpose: the checkboxes under the global
    '## 실무 체크리스트' are the intended deliverable and must survive.
    """
    front, body = _split_front_matter(text)
    out = []
    in_item = False
    for line in body.split("\n"):
        if ITEM_HEADING_RE.match(line):
            in_item = True
            out.append(line)
            continue
        if TOP_SECTION_RE.match(line):
            in_item = False
            out.append(line)
            continue
        m = _ITEM_CHECKBOX_RE.match(line) if in_item else None
        out.append(f"{m.group(1)}- {m.group(2)}" if m else line)
    return front + "\n".join(out)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: `10 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/restore_digest_structure.py scripts/tests/test_restore_digest_structure.py
git commit -m "feat(digest): R3 item 체크박스를 일반 불릿으로 — 항목 텍스트 보존"
```

---

### Task 4: R4 (최상위 섹션 재넘버링)

**Files:**
- Modify: `scripts/restore_digest_structure.py`
- Test: `scripts/tests/test_restore_digest_structure.py`

**Interfaces:**
- Produces: `renumber_sections(text: str) -> str`

- [ ] **Step 1: 실패하는 테스트 작성**

import에 `renumber_sections` 추가하고 append:

```python
def test_renumbers_broken_sequence():
    body = "## 1. 보안 뉴스\n본문\n## 3. AI/ML 뉴스\n본문\n## 7. 클라우드 뉴스\n"
    out = renumber_sections(_FM + body)
    assert "## 1. 보안 뉴스" in out
    assert "## 2. AI/ML 뉴스" in out
    assert "## 3. 클라우드 뉴스" in out


def test_renumber_preserves_section_titles():
    out = renumber_sections(_FM + "## 5. 보안 뉴스\n")
    assert "보안 뉴스" in out


def test_renumber_ignores_unnumbered_sections():
    body = "## 1. 보안 뉴스\n## 실무 체크리스트\n## 4. AI/ML 뉴스\n"
    out = renumber_sections(_FM + body)
    assert "## 실무 체크리스트" in out
    assert "## 2. AI/ML 뉴스" in out


def test_renumber_leaves_correct_sequence_untouched():
    body = "## 1. 보안 뉴스\n## 2. AI/ML 뉴스\n"
    assert renumber_sections(_FM + body) == _FM + body
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: FAIL — `ImportError: cannot import name 'renumber_sections'`

- [ ] **Step 3: 최소 구현**

```python
_NUMBERED_TOP_RE = re.compile(r"^##\s+(\d+)\.\s*(.*)$")


def renumber_sections(text: str) -> str:
    """R4: renumber top-level '## N. ...' sections to a contiguous 1..N.

    Only the number changes. Unnumbered sections ('## 실무 체크리스트') are not
    part of the sequence and pass through untouched. Runs AFTER R1, because most
    of the corpus' broken sequences were item-body headings mis-counted as
    top-level sections — R1 removes those, leaving only genuine gaps.
    """
    front, body = _split_front_matter(text)
    out = []
    n = 0
    for line in body.split("\n"):
        m = _NUMBERED_TOP_RE.match(line)
        if m:
            n += 1
            out.append(f"## {n}. {m.group(2)}")
        else:
            out.append(line)
    return front + "\n".join(out)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: `14 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/restore_digest_structure.py scripts/tests/test_restore_digest_structure.py
git commit -m "feat(digest): R4 최상위 섹션 연속 재넘버링"
```

---

### Task 5: R5 (`## N. 실무 체크리스트` 번호 제거)

**Files:**
- Modify: `scripts/restore_digest_structure.py`
- Test: `scripts/tests/test_restore_digest_structure.py`

**Interfaces:**
- Produces: `canonicalize_checklist_heading(text: str) -> str`

- [ ] **Step 1: 실패하는 테스트 작성**

import에 `canonicalize_checklist_heading` 추가하고 append:

```python
def test_removes_number_from_checklist_heading():
    # check_digest_structure.py:80 은 리터럴 '## 실무 체크리스트'를 센다. 번호형은
    # 인식되지 않아 'found 0'으로 오보고된다 (티어 C 6건).
    out = canonicalize_checklist_heading(_FM + "## 9. 실무 체크리스트\n- [ ] 항목\n")
    assert "## 실무 체크리스트" in out
    assert "## 9. 실무 체크리스트" not in out
    assert "- [ ] 항목" in out


def test_leaves_plain_checklist_heading_alone():
    body = _FM + "## 실무 체크리스트\n- [ ] 항목\n"
    assert canonicalize_checklist_heading(body) == body


def test_does_not_touch_other_numbered_sections():
    out = canonicalize_checklist_heading(_FM + "## 3. 보안 뉴스\n")
    assert "## 3. 보안 뉴스" in out
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: FAIL — `ImportError: cannot import name 'canonicalize_checklist_heading'`

- [ ] **Step 3: 최소 구현**

```python
_NUMBERED_CHECKLIST_RE = re.compile(r"^##\s+\d+\.\s*(실무 체크리스트)\s*$")


def canonicalize_checklist_heading(text: str) -> str:
    """R5: '## 9. 실무 체크리스트' -> '## 실무 체크리스트'.

    check_digest_structure.py counts the LITERAL '## 실무 체크리스트', so the
    numbered legacy form reads as 'found 0'. Converging the content on the
    canonical form fixes that without touching the gate. Runs AFTER R4: removing
    a number takes that section out of R4's contiguity sequence.
    """
    front, body = _split_front_matter(text)
    out = [
        f"## {m.group(1)}" if (m := _NUMBERED_CHECKLIST_RE.match(line)) else line
        for line in body.split("\n")
    ]
    return front + "\n".join(out)
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: `17 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/restore_digest_structure.py scripts/tests/test_restore_digest_structure.py
git commit -m "feat(digest): R5 번호형 실무 체크리스트 헤딩을 canonical로"
```

---

### Task 6: `transform()` 합성 + 무손실 불변식 + CLI

**Files:**
- Modify: `scripts/restore_digest_structure.py`
- Test: `scripts/tests/test_restore_digest_structure.py`

**Interfaces:**
- Consumes: R1~R5 함수 5개
- Produces:
  - `transform(text: str) -> str`
  - `lossless_tokens(text: str) -> collections.Counter` (테스트 헬퍼 겸 공개 API)
  - `main(argv: list) -> int` — `--dry-run`, `--limit`, `--posts-glob`, 파일 인자

- [ ] **Step 1: 실패하는 테스트 작성**

import에 `transform`, `lossless_tokens`, `main` 추가하고 append:

```python
import collections
import subprocess
import tempfile
from pathlib import Path

_DEFECTIVE = (
    "## 1. 보안 뉴스\n"
    "### 1.1 어떤 기사\n"
    "# DevSecOps 관점 분석: 리눅스 익스플로잇\n"
    "본문 문단.\n"
    "#### 대응 체크리스트\n"
    "- [ ] 패치 적용\n"
    "- [x] 로그 점검\n"
    "## 5. AI/ML 뉴스\n"
    "### 5.1 다른 기사\n"
    "## 기술적 배경\n"
    "설명.\n"
    "## 9. 실무 체크리스트\n"
    "- [ ] 전역 항목\n"
)


def test_transform_is_lossless_on_token_multiset():
    """핵심 불변식: 마크다운 마커를 제거한 뒤 토큰 다중집합이 동일해야 한다.

    숫자 토큰은 R4/R5가 의도적으로 바꾸므로 제외한다. 이 검사가 '삭제 금지'를
    규칙이 아니라 테스트로 강제한다 (5·6월 proper-noun 파티션의 토큰 감사 기법).
    """
    before = lossless_tokens(_FM + _DEFECTIVE)
    after = lossless_tokens(transform(_FM + _DEFECTIVE))
    assert before == after, f"lost/added tokens: {before - after} / {after - before}"


def test_transform_resolves_all_four_kinds():
    out = transform(_FM + _DEFECTIVE)
    assert "# DevSecOps" not in out.replace("#### DevSecOps", "")  # H1 gone
    assert "#### 대응 체크리스트" not in out and "**대응 체크리스트**" in out
    assert "## 2. AI/ML 뉴스" in out                              # renumbered
    assert "## 실무 체크리스트" in out                             # number removed
    assert "- [ ] 전역 항목" in out                                # global box kept


def test_transform_is_idempotent():
    once = transform(_FM + _DEFECTIVE)
    assert transform(once) == once


def test_order_matters_r1_before_r2():
    # R2를 먼저 돌리면 R1이 '## 대응 체크리스트'를 '#### …'로 강등해 결함이 되살아난다.
    body = _FM + "## 1. 보안 뉴스\n### 1.1 기사\n## 대응 체크리스트\n- 항목\n"
    wrong = demote_item_headings(boldify_response_checklist(body))
    assert "#### 대응 체크리스트" in wrong          # 잘못된 순서의 증거
    assert "**대응 체크리스트**" in transform(body)  # 올바른 순서


def test_order_matters_r4_before_r5():
    # R5를 먼저 돌리면 체크리스트가 시퀀스에서 빠져 R4가 다른 번호를 매긴다.
    body = _FM + "## 1. 보안 뉴스\n## 3. 실무 체크리스트\n## 7. AI/ML 뉴스\n"
    assert "## 2. AI/ML 뉴스" in renumber_sections(canonicalize_checklist_heading(body))
    assert "## 3. AI/ML 뉴스" in transform(body)


def test_dry_run_does_not_write(tmp_path):
    p = tmp_path / "2026-01-01-X_Weekly_Digest.md"
    p.write_text(_FM + _DEFECTIVE, encoding="utf-8")
    original = p.read_text(encoding="utf-8")
    rc = main(["--dry-run", str(p)])
    assert rc == 0
    assert p.read_text(encoding="utf-8") == original


def test_apply_writes_and_skips_non_digest(tmp_path):
    d = tmp_path / "2026-01-01-X_Weekly_Digest.md"
    d.write_text(_FM + _DEFECTIVE, encoding="utf-8")
    other = tmp_path / "2026-01-01-Regular_Post.md"
    other.write_text(_FM + _DEFECTIVE, encoding="utf-8")
    assert main([str(d), str(other)]) == 0
    assert "**대응 체크리스트**" in d.read_text(encoding="utf-8")
    assert other.read_text(encoding="utf-8") == _FM + _DEFECTIVE  # 스코프 밖
```

- [ ] **Step 2: 테스트 실패 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: FAIL — `ImportError: cannot import name 'transform'`

- [ ] **Step 3: 최소 구현**

`scripts/restore_digest_structure.py`에 추가 (상단 import에 `collections` 추가):

```python
_RULES = (
    demote_item_headings,          # R1 — must precede R2
    boldify_response_checklist,    # R2
    unbox_item_checkboxes,         # R3
    renumber_sections,             # R4 — must precede R5
    canonicalize_checklist_heading, # R5
)


def transform(text: str) -> str:
    """Apply R1..R5 in order. Deterministic and idempotent."""
    for rule in _RULES:
        text = rule(text)
    return text


_MARKER_RE = re.compile(r"(?:^\s*#{1,6}\s+)|(?:^\s*-\s*(?:\[[ xX]?\]\s*)?)|\*\*", re.MULTILINE)
_NUMERIC_RE = re.compile(r"^\d+\.?$")


def lossless_tokens(text: str) -> "collections.Counter":
    """Whitespace-separated tokens with markdown markers stripped.

    Numeric-only tokens are excluded because R4/R5 change section numbers by
    design. Everything else must survive a transform unchanged — that equality is
    the lossless contract.
    """
    stripped = _MARKER_RE.sub(" ", text)
    return collections.Counter(
        t for t in stripped.split() if not _NUMERIC_RE.match(t)
    )


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", help="post paths")
    ap.add_argument("--posts-glob", help="glob instead of explicit paths")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    files = [Path(p) for p in (args.paths or [])]
    if args.posts_glob:
        files += [Path(p) for p in sorted(glob.glob(args.posts_glob))]
    files = [f for f in files if _is_digest_post(f)]
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("[restore-structure] no digest post files to process.")
        return 0

    changed = 0
    for f in files:
        original = f.read_text(encoding="utf-8")
        new = transform(original)
        if new == original:
            print(f"OK   {f}")
            continue
        before, after = lossless_tokens(original), lossless_tokens(new)
        if before != after:
            print(
                f"ABORT {f}: lossless invariant violated "
                f"(lost={list((before - after).elements())[:5]})",
                file=sys.stderr,
            )
            return 1
        changed += 1
        if args.dry_run:
            print(f"DRY  {f}")
        else:
            f.write_text(new, encoding="utf-8")
            print(f"FIXED {f}")
    verb = "would rewrite" if args.dry_run else "rewrote"
    print(f"[restore-structure] {verb} {changed}/{len(files)} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: 테스트 통과 확인**

Run: `python3 -m pytest scripts/tests/test_restore_digest_structure.py -q`
Expected: `24 passed`

- [ ] **Step 5: 커밋**

```bash
git add scripts/restore_digest_structure.py scripts/tests/test_restore_digest_structure.py
git commit -m "feat(digest): transform() 합성 + 무손실 불변식 + CLI (dry-run/limit)"
```

---

### Task 7: 공유 정규식 drift 가드

**Files:**
- Test: `scripts/tests/test_restore_digest_structure.py`

**Interfaces:**
- Consumes: `ITEM_HEADING_RE`, `TOP_SECTION_RE`

- [ ] **Step 1: 실패하는 테스트 작성**

append:

```python
def test_shared_regexes_have_not_drifted():
    """ITEM_HEADING_RE / TOP_SECTION_RE 는 backfill_digest_structure.transform_body
    에서 복사했다. 그쪽은 function-local이라 import가 불가하므로 소스를 스캔해
    두 정의가 갈라지면 실패시킨다. 갈라지면 두 경로가 서로 다른 '섹션'을 인식해
    강등 범위가 조용히 달라진다.
    """
    src = (
        Path(__file__).resolve().parents[1] / "backfill_digest_structure.py"
    ).read_text(encoding="utf-8")
    assert r'r"^### \d+\.\d+"' in src, (
        "backfill_digest_structure.py 의 item-heading 정규식이 바뀌었다. "
        "restore_digest_structure.ITEM_HEADING_RE 를 맞춰 갱신하라."
    )
    for member in (
        "보안", "AI/ML", "클라우드", "DevOps", "블록체인", "기타", "트렌드",
        "GeekNews", "Open Source", "## 실무 체크리스트", "## 서론",
        "## 분석가 시점", "## 경영진 브리핑", "## 위험 스코어카드",
        "## 참고 자료", "## 📊",
    ):
        assert member in src, (
            f"backfill_digest_structure.py 의 섹션 whitelist 에서 {member!r} 가 "
            "사라졌다. restore_digest_structure.TOP_SECTION_RE 를 맞춰 갱신하라."
        )
        assert member in TOP_SECTION_RE.pattern, (
            f"TOP_SECTION_RE 에 {member!r} 가 없다 — backfill 쪽과 불일치."
        )
```

- [ ] **Step 2: 테스트 실패 확인 (non-vacuous 검증)**

Run:
```bash
python3 -m pytest scripts/tests/test_restore_digest_structure.py::test_shared_regexes_have_not_drifted -q
```
Expected: PASS (실제 파일과 일치)

가드가 vacuous하지 않은지 확인 — 임시 복사본에서 whitelist 멤버를 지우고 실패를 확인:
```bash
python3 - <<'EOF'
import re, importlib.util
from pathlib import Path
p = Path("scripts/restore_digest_structure.py")
src = p.read_text(encoding="utf-8")
mutated = src.replace("GeekNews|Open Source", "Open Source")
p.write_text(mutated, encoding="utf-8")
EOF
python3 -m pytest scripts/tests/test_restore_digest_structure.py::test_shared_regexes_have_not_drifted -q
git checkout -- scripts/restore_digest_structure.py
```
Expected: 변형 시 FAIL, `git checkout` 후 다시 PASS

- [ ] **Step 3: 커밋**

```bash
git add scripts/tests/test_restore_digest_structure.py
git commit -m "test(digest): 복사된 공유 정규식 drift 가드 (backfill↔restore 동기화)"
```

---

### Task 8: B1 파일럿 — 티어 A 3개

**Files:**
- Modify: `_posts/2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.md`
- Modify: `_posts/2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.md`
- Modify: `_posts/2026-04-01-Tech_Security_Weekly_Digest_Zero-Day_Go_AI_AWS.md`

세 파일 모두 티어 A(`BOX+H1+NUM+RESP`)이며 PR #495가 건드리는 19개와 **겹치지 않는다**.

- [ ] **Step 1: 변환 전 위반 계량 (baseline 기록)**

```bash
python3 - <<'EOF'
import importlib.util, collections
def load(p,n):
    s=importlib.util.spec_from_file_location(n,p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
chk=load('scripts/check_digest_structure.py','c')
FILES=["_posts/2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.md",
       "_posts/2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.md",
       "_posts/2026-04-01-Tech_Security_Weekly_Digest_Zero-Day_Go_AI_AWS.md"]
c=collections.Counter()
for f in FILES:
    for v in chk.check_post(f): c[chk._kind(v)]+=1
print("BEFORE:", dict(c), "total:", sum(c.values()))
EOF
```
Expected: 4가지 kind, 합계 17건 (03-22: 6, 03-31: 6, 04-01: 5)

- [ ] **Step 2: dry-run diff 검토**

```bash
python3 scripts/restore_digest_structure.py --dry-run \
  _posts/2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.md \
  _posts/2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.md \
  _posts/2026-04-01-Tech_Security_Weekly_Digest_Zero-Day_Go_AI_AWS.md
```
Expected: `DRY` 3줄 + `would rewrite 3/3`. `ABORT`가 나오면 무손실 불변식 위반이므로 **중단하고 룰을 고친다**.

- [ ] **Step 3: 적용**

```bash
python3 scripts/restore_digest_structure.py \
  _posts/2026-03-22-Tech_Security_Weekly_Digest_CVE_Patch_AI_Apple.md \
  _posts/2026-03-31-Tech_Security_Weekly_Digest_Vulnerability_Patch_AI_GPT.md \
  _posts/2026-04-01-Tech_Security_Weekly_Digest_Zero-Day_Go_AI_AWS.md
```
Expected: `FIXED` 3줄 + `rewrote 3/3`

- [ ] **Step 4: 변환 후 위반 재계량 + 게이트**

```bash
# Step 1 스크립트를 다시 실행 → AFTER 카운트
git add _posts/2026-03-22-*.md _posts/2026-03-31-*.md _posts/2026-04-01-*.md
python3 scripts/check_digest_structure.py --staged --ratchet
python3 scripts/check_digest_proper_nouns.py --staged
python3 -m pytest scripts/tests/ -q
python3 scripts/check_posts.py 2>&1 | grep -ciE "truncated|text too dense"
python3 scripts/score_cover_honesty.py --all --baseline tests/cover_honesty_baseline.txt --strict 2>&1 | tail -4
```
Expected: AFTER total **0**; ratchet `0 new violations`; proper-nouns `0 violations`; pytest all pass; SVG 경고 `0`; honesty FAIL `0`

- [ ] **Step 5: 멱등성 + 렌더 확인**

```bash
python3 scripts/restore_digest_structure.py \
  _posts/2026-03-22-*.md _posts/2026-03-31-*.md _posts/2026-04-01-*.md
git diff --stat _posts/   # 재적용 후 추가 변경 없어야 함
bundle exec jekyll build --destination /tmp/_site_b1 2>&1 | tail -5
```
Expected: 재적용 시 `OK` 3줄(변경 0), Jekyll 빌드 성공

- [ ] **Step 6: 커밋**

```bash
git add _posts/2026-03-22-*.md _posts/2026-03-31-*.md _posts/2026-04-01-*.md
git commit -m "fix(digest): B1 파일럿 — 티어 A 3개 구조 무손실 복원 (위반 17 → 0)"
```

---

## 후속 배치 (이 계획 범위 밖, 동일 절차 반복)

| 배치 | 대상 | 파일 수 |
|---|---|---:|
| B2~B5 | 티어 A 잔여 | 96 |
| B6 | 티어 B | 11 |
| B7 | 티어 C | 6 |
| B8 | 티어 E (코드펜스, 개별 판단 — spec §4.3) | 1 |

각 배치는 Task 8의 6단계를 그대로 따르고, PR 본문에 kind별 before/after를 명시한다.
