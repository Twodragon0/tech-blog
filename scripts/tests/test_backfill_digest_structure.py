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
