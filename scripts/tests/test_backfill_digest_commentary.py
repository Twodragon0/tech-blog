"""Tests for `scripts/backfill_digest_commentary.py`.

Validates:
  - Date filtering (--since)
  - Idempotency (skips posts that already have commentary)
  - Dry-run produces no writes
  - --no-llm path uses fake commentary
  - Insertion happens after `## 위험 스코어카드` block
  - Headline extraction from H3 and bold-link patterns
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
from pathlib import Path

import pytest

# Load the script as a module without requiring package install.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SCRIPT_PATH = _REPO_ROOT / "scripts" / "backfill_digest_commentary.py"
_spec = importlib.util.spec_from_file_location(
    "backfill_digest_commentary", _SCRIPT_PATH
)
backfill = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(backfill)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Sample post fixtures
# ---------------------------------------------------------------------------


def _sample_post_with_h3_headlines(date_str: str = "2026-05-07") -> str:
    return f"""---
layout: post
title: "Tech Security Weekly Digest"
date: {date_str} 09:00:00 +0900
categories: [security, devsecops]
---

## 서론

안녕하세요, **Twodragon**입니다.

## 경영진 브리핑

- **긴급 대응 필요**: 사례 1, 사례 2 등 Critical 등급 위협 2건이 확인되었습니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 |

## 1. 보안 뉴스

### 1.1 Apache HTTP/2의 치명적 취약점 (CVE-2026-23918)

본문 내용 1.

### 1.2 GitHub Actions OIDC 토큰 권한 누설 사례

본문 내용 2.

### 1.3 AWS IAM Identity Center 권한 검토

본문 내용 3.
"""


def _sample_post_with_existing_commentary(date_str: str = "2026-05-06") -> str:
    return f"""---
layout: post
title: "Tech Security Weekly Digest"
date: {date_str} 09:00:00 +0900
---

## 위험 스코어카드

| 영역 | 위험도 |
|------|--------|
| A | High |

## 분석가 시점

이미 작성된 commentary가 있다.

## 1. 보안 뉴스

### 1.1 무엇

본문.
"""


# ---------------------------------------------------------------------------
# Headline extraction
# ---------------------------------------------------------------------------


class TestHeadlineExtraction:
    def test_extracts_h3_news_titles(self):
        body = _sample_post_with_h3_headlines().split("---\n", 2)[-1]
        headlines = backfill._extract_headlines_from_body(body, max_n=3)
        assert len(headlines) == 3
        assert "Apache HTTP/2" in headlines[0]["title"]
        assert "GitHub Actions OIDC" in headlines[1]["title"]
        assert "AWS IAM" in headlines[2]["title"]

    def test_skips_subsection_boilerplate_headers(self):
        body = """## 위험 스코어카드

| A | B |

## 1. 보안 뉴스

### 1.1 Real Headline About Something Critical

### 기술적 배경 및 위협 분석

Should be skipped.

### 1.2 Another Real Headline About AWS
"""
        headlines = backfill._extract_headlines_from_body(body, max_n=3)
        titles = [h["title"] for h in headlines]
        assert "기술적 배경 및 위협 분석" not in titles
        assert any("Real Headline" in t for t in titles)

    def test_falls_back_to_bold_link_titles(self):
        body = """## 위험 스코어카드

## 1. 보안 뉴스

- **[First Important Story](https://x.test/1)**: detail
- **[Second Major Vulnerability Disclosure](https://x.test/2)**: detail
- **[Third Threat Report](https://x.test/3)**: detail
"""
        headlines = backfill._extract_headlines_from_body(body, max_n=3)
        assert len(headlines) >= 1
        # If only short titles, may filter; ensure at least one clean title.
        titles = [h["title"] for h in headlines]
        assert any("Important Story" in t or "Vulnerability" in t for t in titles)


# ---------------------------------------------------------------------------
# Idempotency / detection
# ---------------------------------------------------------------------------


class TestIdempotency:
    def test_skips_post_with_existing_commentary(self, tmp_path: Path):
        post = tmp_path / "2026-05-06-Tech_Security_Weekly_Digest_X.md"
        post.write_text(_sample_post_with_existing_commentary(), encoding="utf-8")

        changed, msg = backfill.process_post(post, dry_run=True, no_llm=True)
        assert changed is False
        assert "already has" in msg


# ---------------------------------------------------------------------------
# Insertion
# ---------------------------------------------------------------------------


class TestInsertion:
    def test_inserts_after_scorecard_before_news(self):
        body = _sample_post_with_h3_headlines().split("---\n", 2)[-1]
        new_body = backfill._insert_commentary(body, "fake commentary text")
        # Order: 위험 스코어카드 -> 분석가 시점 -> 1. 보안 뉴스
        sc_idx = new_body.find("## 위험 스코어카드")
        cm_idx = new_body.find("## 분석가 시점")
        nw_idx = new_body.find("## 1. 보안 뉴스")
        assert sc_idx < cm_idx < nw_idx
        assert "fake commentary text" in new_body

    def test_no_anchor_returns_unchanged(self):
        body = "## 다른 섹션\n\n내용\n"
        new_body = backfill._insert_commentary(body, "x")
        # No "## 위험 스코어카드" and no "## N." -> unchanged.
        assert new_body == body


# ---------------------------------------------------------------------------
# Date filtering
# ---------------------------------------------------------------------------


class TestDateFiltering:
    def test_filter_by_date_keeps_recent(self, tmp_path: Path):
        today = _dt.date.today()
        recent_name = f"{today.isoformat()}-Tech_Security_Weekly_Digest_X.md"
        old = today - _dt.timedelta(days=200)
        old_name = f"{old.isoformat()}-Tech_Security_Weekly_Digest_Y.md"
        recent = tmp_path / recent_name
        old_p = tmp_path / old_name
        recent.write_text("x", encoding="utf-8")
        old_p.write_text("x", encoding="utf-8")

        out = backfill._filter_by_date([recent, old_p], since_days=60)
        assert recent in out
        assert old_p not in out


# ---------------------------------------------------------------------------
# Dry-run no-write
# ---------------------------------------------------------------------------


class TestDryRunNoWrite:
    def test_dry_run_does_not_modify_file(self, tmp_path: Path):
        post = tmp_path / "2026-05-07-Tech_Security_Weekly_Digest_X.md"
        original = _sample_post_with_h3_headlines()
        post.write_text(original, encoding="utf-8")

        changed, msg = backfill.process_post(post, dry_run=True, no_llm=True)

        assert changed is True
        assert post.read_text(encoding="utf-8") == original  # unchanged on disk

    def test_apply_writes_file(self, tmp_path: Path):
        post = tmp_path / "2026-05-07-Tech_Security_Weekly_Digest_X.md"
        post.write_text(_sample_post_with_h3_headlines(), encoding="utf-8")

        changed, msg = backfill.process_post(post, dry_run=False, no_llm=True)
        assert changed is True
        new_text = post.read_text(encoding="utf-8")
        assert "## 분석가 시점" in new_text
        # last_modified_at should have been added.
        assert "last_modified_at:" in new_text


# ---------------------------------------------------------------------------
# Frontmatter helpers
# ---------------------------------------------------------------------------


class TestFrontmatterHelpers:
    def test_extract_frontmatter(self):
        text = _sample_post_with_h3_headlines()
        fm, body = backfill._extract_frontmatter_and_body(text)
        assert fm.startswith("---")
        assert fm.rstrip().endswith("---")
        assert body.lstrip().startswith("## 서론")

    def test_update_last_modified_at_inserts(self):
        fm = """---
layout: post
title: "X"
---"""
        out = backfill._update_last_modified_at(fm)
        assert "last_modified_at:" in out
        # Header preserved
        assert 'title: "X"' in out
        # Closing fence preserved
        assert out.rstrip().endswith("---")

    def test_update_last_modified_at_replaces_existing(self):
        fm = """---
layout: post
last_modified_at: 1999-01-01 00:00:00 +0900
title: "X"
---"""
        out = backfill._update_last_modified_at(fm)
        assert "1999-01-01" not in out
        assert "last_modified_at:" in out


# ---------------------------------------------------------------------------
# CLI smoke
# ---------------------------------------------------------------------------


class TestCli:
    def test_no_matches_returns_1(self, tmp_path, capsys, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rc = backfill.main(
            ["--posts-glob", "_posts/_does_not_exist_*.md", "--dry-run"]
        )
        assert rc == 1
