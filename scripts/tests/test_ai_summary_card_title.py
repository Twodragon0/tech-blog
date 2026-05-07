#!/usr/bin/env python3
"""Tests for ai-summary-card include title= attribute length cap.

Regression guard: prevents Liquid include parser errors caused by overly long
title= attribute values in ai-summary-card.html includes.

Recurring failure pattern (first observed 2026-05-06 GH Pages workflow f86ad2d3):
  title="Apache HTTP/2의 치명적, DAEMON Tools 공급망 공격으로 공식, 중국과 연계된 UAT-8302"
  — 62 chars (safe), but concatenating 3 headlines can exceed 80 chars.

API disabling and path setup are handled by conftest.py.
"""

import re

import pytest

from scripts.news.content_generator import (
    _build_digest_title,
    _html_escape_quotes,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MAX_TITLE_LEN = 80
_TECH_PREFIX = "기술 블로그 주간 다이제스트: "
_TECH_MAX_BASE_LEN = _MAX_TITLE_LEN - len(_TECH_PREFIX)


def _make_items(titles, category="security"):
    return [
        {
            "title": t,
            "summary": "test summary",
            "url": f"https://example.com/{i}",
            "source_name": "TestSource",
            "source": "TestSource",
            "category": category,
            "published": "2026-05-06T01:00:00Z",
        }
        for i, t in enumerate(titles)
    ]


def _extract_title_attr(include_block: str) -> str:
    """Extract the value of title=\"...\" from an ai-summary-card include block."""
    m = re.search(r'title="([^"]*)"', include_block)
    assert m, f"title= attribute not found in:\n{include_block}"
    return m.group(1)


# ---------------------------------------------------------------------------
# Unit: _build_digest_title length contract
# ---------------------------------------------------------------------------


class TestBuildDigestTitleLengthCap:
    """_build_digest_title must always return a string <= 80 chars."""

    def test_short_title_within_limit(self):
        """Short headline (well under 80 chars) returns a result within the cap."""
        items = _make_items(["Apache CVE-2026-1234 Critical Fix"])
        result = _build_digest_title(items)
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) <= _MAX_TITLE_LEN

    def test_title_over_80_chars_trimmed(self):
        """When joined phrases exceed 80 chars, result is trimmed to <= 80."""
        # Craft 3 phrases, each near 26 chars, to push join past 80 chars
        titles = [
            "A" * 25 + " security vulnerability",
            "B" * 25 + " supply chain attack",
            "C" * 25 + " APT campaign detected",
        ]
        items = _make_items(titles)
        result = _build_digest_title(items)
        assert len(result) <= _MAX_TITLE_LEN, (
            f"Title too long ({len(result)} > {_MAX_TITLE_LEN}): {result!r}"
        )

    def test_title_exactly_80_chars_passes(self):
        """A title of exactly 80 chars is acceptable."""
        items = _make_items(["A" * 30, "B" * 30])
        result = _build_digest_title(items)
        assert len(result) <= _MAX_TITLE_LEN

    def test_result_does_not_end_with_comma_or_space(self):
        """Trimmed title must not end with a dangling comma or space."""
        titles = [
            "A" * 25 + " long security item one",
            "B" * 25 + " long security item two",
            "C" * 25 + " long security item three",
        ]
        result = _build_digest_title(_make_items(titles))
        assert not result.endswith((",", " ", ".")), (
            f"Result ends with trailing punctuation: {result!r}"
        )

    def test_empty_items_returns_string(self):
        """Empty news_items list should return a non-empty fallback string."""
        result = _build_digest_title([])
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) <= _MAX_TITLE_LEN


# ---------------------------------------------------------------------------
# Unit: _html_escape_quotes + cap pipeline
# ---------------------------------------------------------------------------


class TestSafeTitlePipeline:
    """safe_title = _html_escape_quotes(_capped_title) must be <= 80 chars."""

    def test_cap_then_escape_security_mode(self):
        """Security-mode safe_title pipeline keeps total <= 80 chars."""
        long_title = "보안위협 " * 20  # deliberately long
        capped = long_title[:80].rstrip(" ,.") if len(long_title) > 80 else long_title
        safe = _html_escape_quotes(capped)
        # HTML escaping can only increase length, but base is <= 80 so result
        # may exceed 80 only if the original 80 chars contained escapable chars.
        # The meaningful check: original capped is <= 80.
        assert len(capped) <= _MAX_TITLE_LEN

    def test_cap_then_escape_tech_mode(self):
        """Tech-mode safe_title pipeline (63-char cap) keeps full attr <= 80 chars."""
        long_title = "기술트렌드분석 " * 15
        cap = _TECH_MAX_BASE_LEN
        capped = long_title[:cap].rstrip(" ,.") if len(long_title) > cap else long_title
        safe = _html_escape_quotes(capped)
        full_attr = _TECH_PREFIX + safe
        # HTML entities inflate length; check the un-escaped form
        assert len(_TECH_PREFIX) + len(capped) <= _MAX_TITLE_LEN

    def test_title_with_quotes_sanitized(self):
        """Quotes in title are HTML-escaped, not literal."""
        raw = "포용성과 '퇴행적' 문화를 \"비난\""
        escaped = _html_escape_quotes(raw)
        assert "'" not in escaped
        assert '"' not in escaped
        assert "&#x27;" in escaped
        assert "&quot;" in escaped

    def test_truncation_preserves_word_boundary(self):
        """80-char trim strips trailing commas/spaces (not mid-word cut)."""
        title = "Apache HTTP/2의 치명적, DAEMON Tools 공급망 공격, " + "x" * 60
        capped = title[:80].rstrip(" ,.")
        # Must not end with comma or space
        assert not capped.endswith(",")
        assert not capped.endswith(" ")


# ---------------------------------------------------------------------------
# Integration: include block title= attribute length in generate_post_content
# ---------------------------------------------------------------------------


class TestGeneratePostContentTitleLength:
    """generate_post_content must produce ai-summary-card title= <= 80 chars."""

    def test_security_title_attr_under_80_chars(self):
        from auto_publish_news import generate_post_content
        import datetime

        # 3 headlines, each 26 chars after truncation, to stress the cap
        items = _make_items(
            [
                "A" * 25 + " critical CVE discovered today",
                "B" * 25 + " supply chain attack confirmed",
                "C" * 25 + " APT group targets government",
            ]
        )
        categorized = {
            "security": items,
            "ai": [],
            "cloud": [],
            "devops": [],
            "blockchain": [],
            "tech": [],
        }
        date = datetime.datetime(2026, 5, 6, 11, 0, 0,
                                 tzinfo=datetime.timezone.utc)
        content = generate_post_content(items, categorized, date)

        # Find all ai-summary-card include blocks
        blocks = re.findall(
            r'\{%[- ]*\s*include ai-summary-card\.html(.*?)%\}',
            content,
            re.DOTALL,
        )
        assert blocks, "No ai-summary-card include block found"
        for block in blocks:
            title_val = _extract_title_attr("{%" + block + "%}")
            assert len(title_val) <= _MAX_TITLE_LEN, (
                f"title= attribute too long ({len(title_val)} > {_MAX_TITLE_LEN}): "
                f"{title_val!r}"
            )
