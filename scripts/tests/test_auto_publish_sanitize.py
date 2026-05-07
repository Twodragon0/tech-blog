#!/usr/bin/env python3
"""Tests for sanitize_quotes_for_yaml in scripts/news/content_generator.py.

Covers:
1. raw `"` → `'`
2. already-sanitized text is idempotent
3. Korean curly quotes (U+201C / U+201D) are preserved
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.news.content_generator import sanitize_quotes_for_yaml


class TestSanitizeQuotesForYaml:
    # ------------------------------------------------------------------
    # 1. Raw ASCII double-quote is replaced with single quote
    # ------------------------------------------------------------------

    def test_raw_dq_replaced(self):
        result = sanitize_quotes_for_yaml('Title with "quoted" word')
        assert '"' not in result
        assert "'" in result

    def test_raw_dq_at_start(self):
        result = sanitize_quotes_for_yaml('"Leading quote')
        assert result.startswith("'")

    def test_raw_dq_at_end(self):
        result = sanitize_quotes_for_yaml('Trailing quote"')
        assert result.endswith("'")

    def test_multiple_raw_dqs(self):
        result = sanitize_quotes_for_yaml('a "b" and "c"')
        assert '"' not in result
        assert result == "a 'b' and 'c'"

    # ------------------------------------------------------------------
    # 2. Already-sanitized text is idempotent
    # ------------------------------------------------------------------

    def test_idempotent_no_dq(self):
        text = "No double quotes here"
        assert sanitize_quotes_for_yaml(text) == text

    def test_idempotent_single_quotes(self):
        text = "Title with 'inner' single quotes"
        assert sanitize_quotes_for_yaml(text) == text

    def test_idempotent_korean_no_dq(self):
        text = "중요한 CVE 취약점 'Sorry' 공격"
        assert sanitize_quotes_for_yaml(text) == text

    # ------------------------------------------------------------------
    # 3. Korean curly/fullwidth quotes are preserved
    # ------------------------------------------------------------------

    def test_left_double_quotation_mark_preserved(self):
        """\u201c (U+201C) is NOT ASCII double-quote, must be kept as-is."""
        text = "\u201cSmart quote\u201d"
        result = sanitize_quotes_for_yaml(text)
        assert "\u201c" in result
        assert "\u201d" in result

    def test_fullwidth_quotation_preserved(self):
        """Fullwidth double-quote (U+FF02) is kept as-is."""
        text = "\uff02fullwidth\uff02"
        result = sanitize_quotes_for_yaml(text)
        assert "\uff02" in result

    def test_mixed_curly_and_ascii(self):
        """Only ASCII \" (U+0022) is replaced; curly quotes survive."""
        text = '\u201cSmart\u201d and "ascii" here'
        result = sanitize_quotes_for_yaml(text)
        assert '"' not in result          # ASCII dq gone
        assert "\u201c" in result         # curly left quote still there
        assert "\u201d" in result         # curly right quote still there

    # ------------------------------------------------------------------
    # 4. HTML entity &quot; and literal \u0022 decoded then sanitized
    # ------------------------------------------------------------------

    def test_html_entity_quot_decoded(self):
        """&quot; from upstream feed is decoded to ' (not left as &quot;)."""
        result = sanitize_quotes_for_yaml("Title &quot;Sorry&quot; attack")
        assert "&quot;" not in result
        assert '"' not in result
        assert "'" in result

    def test_literal_u0022_sequence(self):
        r"""Literal \\u0022 sequence in text → replaced with single quote."""
        result = sanitize_quotes_for_yaml("Title \\u0022word\\u0022 end")
        assert "\\u0022" not in result
        assert '"' not in result

    # ------------------------------------------------------------------
    # 5. Empty / None guard
    # ------------------------------------------------------------------

    def test_empty_string(self):
        assert sanitize_quotes_for_yaml("") == ""

    def test_none_like_empty(self):
        # The function signature accepts str; passing empty is the safe test
        assert sanitize_quotes_for_yaml("") == ""
