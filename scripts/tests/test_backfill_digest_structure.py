import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from backfill_digest_structure import transform_body

_POST = """---
title: x
---
## 1. 보안 뉴스
### 1.1 항목
# DevSecOps 관점 분석
## 1. 기술적 배경
내용
## 3. 대응 체크리스트
- [ ] 패치
## 2. AI/ML 뉴스
## 실무 체크리스트
### P0 (즉시)
"""


def test_transform_removes_body_h1_and_collision():
    out = transform_body(_POST)
    assert "\n# DevSecOps" not in out
    assert "## 1. 기술적 배경" not in out
    assert "#### 기술적 배경" in out


def test_transform_removes_per_item_checklist():
    out = transform_body(_POST)
    assert "대응 체크리스트" not in out
    assert "- [ ] 패치" not in out
    assert "## 실무 체크리스트" in out  # global one preserved


def test_transform_is_idempotent():
    once = transform_body(_POST)
    assert transform_body(once) == once


def test_frontmatter_preserved():
    assert transform_body(_POST).startswith("---\ntitle: x\n---\n")


_POST_WITH_PRE_ITEM_SUBHEADING = """---
title: z
---
## 📊 빠른 참조
### 이번 주 하이라이트
| 분야 | 소스 |
|------|------|
| 보안 | X |

## 1. 보안 뉴스
### 1.1 항목
# body H1
## 1. 기술적 배경
내용
## 3. 대응 체크리스트
- [ ] y
"""


def test_pre_item_subheading_not_demoted():
    """### 이번 주 하이라이트 appears BEFORE any ### N.M item heading, under
    a non-item section (## 📊 빠른 참조). It must stay ### verbatim, not be
    swept into _normalize_deep_analysis and demoted to ####."""
    out = transform_body(_POST_WITH_PRE_ITEM_SUBHEADING)
    assert "### 이번 주 하이라이트" in out
    assert "#### 이번 주 하이라이트" not in out


def test_item_region_still_normalized_alongside_pre_item_subheading():
    out = transform_body(_POST_WITH_PRE_ITEM_SUBHEADING)
    assert "\n# body H1" not in out
    assert "## 1. 기술적 배경" not in out
    assert "#### 기술적 배경" in out
    assert "- [ ] y" not in out


# --- Finding 1: prose '#### 권장 조치' advisory must survive, while a
# sibling deep-analysis collision in the same item is still demoted. ---

_POST_WITH_PROSE_ADVISORY = """---
title: y
---
## 1. 보안 뉴스
### 1.1 항목
# 어떤 분석
#### 권장 조치

- 관련 시스템 확인
- 벤더 권고

## 2. AI/ML 뉴스
"""


def test_prose_advisory_preserved():
    out = transform_body(_POST_WITH_PROSE_ADVISORY)
    assert "#### 권장 조치" in out
    assert "- 관련 시스템 확인" in out
    assert "- 벤더 권고" in out


def test_sibling_h1_still_demoted_alongside_prose_advisory():
    out = transform_body(_POST_WITH_PROSE_ADVISORY)
    assert "\n# 어떤 분석" not in out
    assert "#### 어떤 분석" in out


def test_prose_advisory_preservation_is_idempotent():
    once = transform_body(_POST_WITH_PROSE_ADVISORY)
    assert transform_body(once) == once


# --- Finding 2: tech-mode section titles must be recognized as top-level
# boundaries, not swept into item-region normalization. ---

_POST_TECH_MODE_OPEN_SOURCE = """---
title: t
---
## 2. AI/ML 뉴스
### 2.1 항목
내용
## 3. Open Source
### 3.1 항목
내용
"""


def test_tech_mode_open_source_boundary_recognized():
    """'## 3. Open Source' follows an already-open item region (### 2.1).
    The old whitelist didn't know this title, so it would be swept into
    the item-region buffer and demoted/ordinal-stripped by
    _normalize_deep_analysis instead of closing the region as its own
    top-level heading."""
    out = transform_body(_POST_TECH_MODE_OPEN_SOURCE)
    assert "## 3. Open Source" in out
    assert "#### Open Source" not in out
