#!/usr/bin/env python3
"""Tests for scripts/backfill_digest_native_sections.py.

Covers the two grounding-source parsers and the transform contract:
  (a) 4-column highlights table still parses (no regression),
  (b) 5-column highlights table reads the correct first four fields,
  (c) April summary_card.highlights + CVE table → CVSS-band severity,
  (d) skip-on-no-source (neither table nor summary_card+CVE) → None,
  (e) idempotency (a second pass inserts nothing new).

All fixtures are inline; no network or file I/O.
"""
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from scripts import backfill_digest_native_sections as mod  # noqa: E402

# --- Fixtures -------------------------------------------------------------

_FRONT_MIN = "---\ntitle: t\n---\n"

_HL_4COL_BODY = """
## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 취약점 | CISA | vCenter CVE-2024-1 긴급 패치 | 🔴 |
| AI 보안 | HashiCorp | 에이전틱 제로트러스트 | 🟡 |

---

## 실무 체크리스트

### P0 (즉시)

- 기존 항목 하나
- 기존 항목 둘
- 기존 항목 셋
- 기존 항목 넷
- 기존 항목 다섯

---

## 참고 자료

- link
"""

_HL_5COL_BODY = """
## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 | 긴급도 |
|------|------|----------|--------|--------|
| 취약점 | CISA | vCenter CVE-2024-1 KEV 추가 | 높음 | 긴급 |
| 제로데이 | Fortinet | FortiGate SSO 우회 공격 | 높음 | 긴급 |
| 클라우드 | Google | Airflow 3.1 통합 | 중간 | 낮음 |

---

## 참고 자료

- link
"""

_APRIL_FRONT = """---
title: "2026년 4월 1주차 보안 다이제스트 주간 롤업"
summary_card:
  title: "rollup"
  highlights:
    - { source: "제로데이", title: "TrueConf CVE-2026-3502 정부기관 표적 APT 캠페인 확인" }
    - { source: "공급망 위협", title: "Axios npm 해킹으로 오픈소스 생태계 위협 심화" }
    - { source: "클라우드 컴플라이언스", title: "AWS LZA Universal Configuration 가이드 발표" }
---
"""

_APRIL_BODY = """
## 개요

이번 주 요약 문단.

---

## 일별 다이제스트 인덱스

| 날짜 | 주요 이슈 |
|------|-----------|
| 4/1 | x |

---

## 주요 CVE 요약

| CVE | 대상 | CVSS | 상태 |
|-----|------|------|------|
| CVE-2026-3502 | TrueConf 클라이언트 | 7.8 | 제로데이 악용 확인 |

---

## 실무 우선순위 체크리스트

### P0 (즉시)
- [ ] a
- [ ] b
- [ ] c
- [ ] d
- [ ] e
- [ ] f
- [ ] g
- [ ] h

---
"""


# --- (a) 4-column highlights table still parses --------------------------

def test_parse_highlights_4col():
    items = mod.parse_highlights(_HL_4COL_BODY)
    assert len(items) == 2
    assert items[0]["source"] == "CISA"
    assert items[0]["title"] == "vCenter CVE-2024-1 긴급 패치"
    assert items[0]["category"] == "security"
    assert items[0]["severity"] == "Critical"  # 🔴
    assert items[1]["severity"] == "Medium"  # 🟡


# --- (b) 5-column highlights table reads the correct four fields ----------

def test_parse_highlights_5col_reads_first_four():
    items = mod.parse_highlights(_HL_5COL_BODY)
    assert len(items) == 3
    # col1=분야, col2=소스, col3=핵심 내용, col4=영향도; col5(긴급도) ignored
    assert items[0]["source"] == "CISA"
    assert items[0]["title"] == "vCenter CVE-2024-1 KEV 추가"
    assert items[1]["source"] == "Fortinet"
    assert items[1]["title"] == "FortiGate SSO 우회 공격"
    # The 긴급도 column ("긴급") must NOT leak into any field.
    for it in items:
        assert "긴급" not in it["title"]
        assert it["source"] in {"CISA", "Fortinet", "Google"}


def test_row_re_matches_both_widths():
    assert mod._ROW_RE.match("| a | b | c | d |")
    assert mod._ROW_RE.match("| a | b | c | d | e |")
    # fewer than 4 columns must NOT match
    assert not mod._ROW_RE.match("| a | b | c |")


# --- (c) April summary_card + CVE table → CVSS-band severity --------------

def test_parse_cve_table_numeric_band():
    body = "## 주요 CVE 요약\n\n| CVE | 대상 | CVSS | 상태 |\n|--|--|--|--|\n| CVE-2026-3502 | x | 7.8 | y |\n\n## next\n"
    assert mod._parse_cve_table(body) == {"CVE-2026-3502": "High"}


def test_parse_cve_table_korean_word():
    body = "## 주요 CVE 요약\n\n| CVE | 대상 | 심각도 | 상태 |\n|--|--|--|--|\n| CVE-2026-33032 | Nginx UI | 치명적 | z |\n"
    assert mod._parse_cve_table(body) == {"CVE-2026-33032": "Critical"}


def test_cvss_band_boundaries():
    assert mod._cvss_band_to_severity(9.0) == "Critical"
    assert mod._cvss_band_to_severity(7.0) == "High"
    assert mod._cvss_band_to_severity(4.0) == "Medium"
    assert mod._cvss_band_to_severity(3.9) == "Low"


def test_parse_summary_card_cve_items():
    items = mod.parse_summary_card_cve(_APRIL_FRONT, _APRIL_BODY)
    assert len(items) == 3
    by_title = {it["title"]: it for it in items}
    # CVE-bearing highlight → severity from the CVE table (7.8 → High)
    cve_item = next(it for it in items if "CVE-2026-3502" in it["title"])
    assert cve_item["severity"] == "High"
    # non-CVE highlights → Medium
    non_cve = [it for it in items if "CVE-" not in it["title"]]
    assert len(non_cve) == 2
    assert all(it["severity"] == "Medium" for it in non_cve)
    # sources preserved from summary_card
    assert cve_item["source"] == "제로데이"


def test_april_transform_adds_exec_risk_not_checklist():
    text = _APRIL_FRONT + _APRIL_BODY
    new_text, info = mod.transform_text(text)
    assert new_text is not None
    assert info["source"] == "summary_card_cve"
    assert info["exec_added"] is True
    assert info["checklist_action"] == "none"
    assert "## 경영진 브리핑" in new_text
    assert "## 위험 스코어카드" in new_text
    # existing checklist untouched (still exactly one, still qualified heading)
    assert new_text.count("## 실무 우선순위 체크리스트") == 1
    assert "## 실무 체크리스트\n" not in new_text
    # exec/risk lands between 개요 and 일별 인덱스
    assert new_text.index("## 경영진 브리핑") < new_text.index("## 일별 다이제스트 인덱스")


# --- (d) skip-on-no-source → None ----------------------------------------

def test_skip_when_no_source():
    text = _FRONT_MIN + "\n## 개요\n\n본문만 있고 표가 없습니다.\n"
    new_text, info = mod.transform_text(text)
    assert new_text is None
    assert info.get("skip") is True


def test_skip_when_highlights_absent_and_summary_card_absent():
    # summary_card present but NO CVE table → April path also skips.
    text = _APRIL_FRONT + "\n## 개요\n\n표 없음.\n"
    assert mod.parse_summary_card_cve(_APRIL_FRONT, "\n## 개요\n\n표 없음.\n") == []


# --- (e) idempotency ------------------------------------------------------

def test_idempotent_april():
    text = _APRIL_FRONT + _APRIL_BODY
    once, _ = mod.transform_text(text)
    twice, info2 = mod.transform_text(once)
    assert twice == once  # second pass is a no-op
    assert info2["exec_added"] is False


def test_idempotent_highlights_checklist_convert():
    text = _FRONT_MIN + _HL_4COL_BODY
    once, info1 = mod.transform_text(text)
    assert once is not None
    # existing plain bullets under 실무 체크리스트 converted to checkboxes
    assert once.count("- [ ] 기존 항목") == 5
    twice, _ = mod.transform_text(once)
    assert twice == once  # stable


# --- (f) legacy-surface duplicate guards ---------------------------------
# Class D digests carry the briefing/risk surfaces in a NARRATIVE form
# (## Executive Summary + a "> **경영진 브리핑**:" blockquote + ### 위험도 평가)
# that the old guard ("## 경영진 브리핑" in body / "스코어카드" in body) did NOT
# recognize, so the exec/risk block would be inserted a SECOND time. These
# tests pin the broadened guard.

_LEGACY_NARRATIVE_BODY = """
## Executive Summary

> **경영진 브리핑**: 이번 주 핵심 위협 한 줄 요약.

### 위험도 평가

| 항목 | 위험도 | 설명 |
|------|--------|------|
| 취약점 | 높음 | vCenter |

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 취약점 | CISA | vCenter CVE-2024-1 긴급 패치 | 🔴 |
| AI 보안 | HashiCorp | 에이전틱 제로트러스트 | 🟡 |

---

## 6. 실무 체크리스트

### 6.1 이번 주 필수 점검 항목

- 기존 항목 하나
- 기존 항목 둘

## 참고 자료

- link
"""


def test_guard_recognizes_executive_summary_and_risk():
    # Unit: the broadened detectors fire on the legacy narrative surfaces.
    assert mod._has_briefing(_LEGACY_NARRATIVE_BODY) is True
    assert mod._has_risk(_LEGACY_NARRATIVE_BODY) is True


def test_legacy_narrative_no_exec_reinsert():
    # (1) A post with ## Executive Summary + "> **경영진 브리핑**" blockquote
    # + ### 위험도 평가 must NOT get a second briefing/risk block.
    text = _FRONT_MIN + _LEGACY_NARRATIVE_BODY
    new_text, info = mod.transform_text(text)
    assert new_text is not None
    assert info["exec_added"] is False
    # native canonical headings never inserted (would duplicate the narrative)
    assert "## 경영진 브리핑" not in new_text
    assert "## 위험 스코어카드" not in new_text
    # the existing Executive Summary / 위험도 평가 surfaces survive verbatim
    assert new_text.count("## Executive Summary") == 1
    assert new_text.count("### 위험도 평가") == 1


def test_risk_guard_recognizes_위험도평가_h3():
    # (2) ### 위험도 평가 (no 스코어카드 token) is a risk surface.
    assert mod._has_risk("본문\n### 위험도 평가\n| a | b |\n") is True
    # ### 위험 평가 스코어카드 is also recognized (via bare 스코어카드).
    assert mod._has_risk("### 위험 평가 스코어카드\n") is True
    # a post with neither is not.
    assert mod._has_risk("## 개요\n일반 본문.\n") is False


def test_legacy_numbered_checklist_not_duplicated():
    # A legacy "## N. 실무 체크리스트" must not spawn a second
    # "## 실무 체크리스트"; the fresh-insert path is skipped.
    text = _FRONT_MIN + _LEGACY_NARRATIVE_BODY
    new_text, info = mod.transform_text(text)
    assert new_text is not None
    # exactly one checklist surface (the pre-existing numbered one)
    assert new_text.count("실무 체크리스트") == 1
    assert "## 6. 실무 체크리스트" in new_text
    assert info["checklist_action"] == "skipped (existing checklist surface)"


def test_fresh_post_still_inserts_briefing_and_risk():
    # (3) regression: a post with a highlights table and NONE of the
    # briefing/risk/checklist surfaces still gets the native sections.
    fresh_body = """
## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 취약점 | CISA | vCenter CVE-2024-1 긴급 패치 | 🔴 |
| AI 보안 | HashiCorp | 에이전틱 제로트러스트 | 🟡 |

---

## 서론

본문.

## 참고 자료

- link
"""
    text = _FRONT_MIN + fresh_body
    assert mod._has_briefing(fresh_body) is False
    assert mod._has_risk(fresh_body) is False
    assert mod._has_checklist(fresh_body) is False
    new_text, info = mod.transform_text(text)
    assert new_text is not None
    assert info["exec_added"] is True
    assert "## 경영진 브리핑" in new_text
    assert "## 위험 스코어카드" in new_text
    # no prior checklist → a fresh canonical checklist is inserted (once)
    assert info["checklist_action"] == "inserted"
    assert new_text.count("## 실무 체크리스트") == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
