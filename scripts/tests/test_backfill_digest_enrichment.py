import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import backfill_digest_enrichment as bde  # noqa: E402
from scripts.news import content_generator  # noqa: E402


_POST = """---
title: x
---
## 1. 보안 뉴스

### 1.1 Example Title One

{% include news-card.html
  title="Example Title One"
  url="https://example.com/one"
  summary="summary one"
  source="Example Source"
  severity="Critical"
%}

#### DevSecOps 관점에서 본 분석

#### 기술적 배경 및 위협 분석

원본 짧은 분석 내용 1.

#### 실무 영향 분석

원본 실무 영향 1.

---

### 1.2 Example Title Two

{% include news-card.html
  title="Example Title Two"
  url="https://example.com/two"
  summary="summary two"
  source="Example Source"
  severity="High"
%}

#### 기술적 배경 및 위협 분석

원본 짧은 분석 내용 2.

---

### 1.3 No Deep Analysis Item

{% include news-card.html
  title="No Deep Analysis Item"
  url="https://example.com/three"
  summary="summary three"
  source="Example Source"
  severity="Medium"
%}

#### 요약

그냥 요약만 있는 항목.

---

## 2. AI/ML 뉴스

### 2.1 Another Section Item

{% include news-card.html
  title="Another Section Item"
  url="https://example.com/four"
  summary="summary four"
  source="Example Source"
  severity="Critical"
%}

#### 기술적 배경 및 위협 분석

원본 짧은 분석 내용 4.

---
"""

_CANNED = "#### 기술적 배경\n\n출처 기반 확장된 분석 내용입니다.\n\n#### 실무 영향\n\n출처 기반 실무 영향 내용입니다."


def _fresh_stats():
    return {"items_with_deep_analysis": 0, "fetched_ok": 0, "expanded_ok": 0, "replaced": 0}


def test_replaces_deep_analysis_when_expansion_returns_text(monkeypatch):
    monkeypatch.setattr(content_generator, "_maybe_source_expansion", lambda item: _CANNED)
    stats = _fresh_stats()
    out = bde.transform_body(_POST, stats)
    assert "출처 기반 확장된 분석 내용입니다." in out
    assert "원본 짧은 분석 내용 1." not in out
    assert stats["replaced"] == 3  # items 1.1, 1.2, 2.1 have deep-analysis
    assert stats["items_with_deep_analysis"] == 3


def test_item_unchanged_when_expansion_returns_none(monkeypatch):
    monkeypatch.setattr(content_generator, "_maybe_source_expansion", lambda item: None)
    stats = _fresh_stats()
    out = bde.transform_body(_POST, stats)
    assert "원본 짧은 분석 내용 1." in out
    assert "원본 짧은 분석 내용 2." in out
    assert "원본 짧은 분석 내용 4." in out
    assert stats["replaced"] == 0
    assert stats["items_with_deep_analysis"] == 3


def test_newscard_and_heading_and_separator_preserved(monkeypatch):
    monkeypatch.setattr(content_generator, "_maybe_source_expansion", lambda item: _CANNED)
    stats = _fresh_stats()
    out = bde.transform_body(_POST, stats)
    assert "### 1.1 Example Title One" in out
    assert 'url="https://example.com/one"' in out
    assert "{% include news-card.html" in out
    assert out.count("\n---\n") >= 3


def test_idempotent(monkeypatch):
    monkeypatch.setattr(content_generator, "_maybe_source_expansion", lambda item: _CANNED)
    stats1 = _fresh_stats()
    once = bde.transform_body(_POST, stats1)
    stats2 = _fresh_stats()
    twice = bde.transform_body(once, stats2)
    assert once == twice


def test_non_deep_analysis_item_untouched(monkeypatch):
    monkeypatch.setattr(content_generator, "_maybe_source_expansion", lambda item: _CANNED)
    stats = _fresh_stats()
    out = bde.transform_body(_POST, stats)
    assert "그냥 요약만 있는 항목." in out
    assert "#### 요약" in out


def test_frontmatter_preserved(monkeypatch):
    monkeypatch.setattr(content_generator, "_maybe_source_expansion", lambda item: _CANNED)
    stats = _fresh_stats()
    out = bde.transform_body(_POST, stats)
    assert out.startswith("---\ntitle: x\n---\n")


def test_correct_url_extracted_and_passed_to_expansion(monkeypatch):
    seen = {}

    def fake_expansion(item):
        seen[item["url"]] = item.get("title")
        return _CANNED

    monkeypatch.setattr(content_generator, "_maybe_source_expansion", fake_expansion)
    stats = _fresh_stats()
    bde.transform_body(_POST, stats)
    assert seen["https://example.com/one"] == "Example Title One"
    assert seen["https://example.com/two"] == "Example Title Two"
    assert seen["https://example.com/four"] == "Another Section Item"
    assert "https://example.com/three" not in seen  # no-deep-analysis item never called


def test_fetch_and_expand_counted_via_real_maybe_source_expansion(monkeypatch):
    """Prove stats granularity works through the real _maybe_source_expansion
    (not a mock of it) by mocking one level deeper — fetch + expand — the
    same way the real flag-on path would call them."""
    monkeypatch.setenv("DIGEST_SOURCE_EXPANSION", "1")
    monkeypatch.setattr(
        content_generator, "_fetch_article_for", lambda url: "some article text " * 50
    )
    monkeypatch.setattr(
        content_generator, "_expand_summary_for", lambda item, article: _CANNED
    )
    stats = _fresh_stats()
    out = bde.transform_body(_POST, stats)
    assert stats["fetched_ok"] == 3
    assert stats["expanded_ok"] == 3
    assert stats["replaced"] == 3
    assert "출처 기반 확장된 분석 내용입니다." in out


def test_flag_off_keeps_original_and_zero_stats(monkeypatch):
    monkeypatch.delenv("DIGEST_SOURCE_EXPANSION", raising=False)
    stats = _fresh_stats()
    out = bde.transform_body(_POST, stats)
    assert "원본 짧은 분석 내용 1." in out
    assert stats["replaced"] == 0
    assert stats["fetched_ok"] == 0
    assert stats["expanded_ok"] == 0
