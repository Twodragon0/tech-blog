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
    # 3. Curly quotes normalised; fullwidth (U+FF02) preserved
    # ------------------------------------------------------------------

    def test_left_double_quotation_mark_normalised(self):
        """U+201C LEFT DOUBLE QUOTATION MARK is now normalised to ASCII apostrophe."""
        text = "\u201cSmart quote\u201d"
        result = sanitize_quotes_for_yaml(text)
        # Curly quotes are removed (normalised), NOT preserved
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "'" in result

    def test_fullwidth_quotation_preserved(self):
        """Fullwidth double-quote (U+FF02) is kept as-is."""
        text = "\uff02fullwidth\uff02"
        result = sanitize_quotes_for_yaml(text)
        assert "\uff02" in result

    def test_mixed_curly_and_ascii_all_normalised(self):
        """Both ASCII \" (U+0022) and curly quotes are replaced with apostrophe."""
        text = '\u201cSmart\u201d and "ascii" here'
        result = sanitize_quotes_for_yaml(text)
        assert '"' not in result          # ASCII dq gone
        assert "\u201c" not in result     # curly left quote normalised
        assert "\u201d" not in result     # curly right quote normalised
        assert "'" in result              # replaced with apostrophe

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

    # ------------------------------------------------------------------
    # 6. Curly / typographic quote normalisation (new behaviour)
    # ------------------------------------------------------------------

    def test_curly_double_quote_left_normalized(self):
        """U+201C LEFT DOUBLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("Next \u201c26\u201d release")
        assert "\u201c" not in result
        assert "'" in result

    def test_curly_double_quote_right_normalized(self):
        """U+201D RIGHT DOUBLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("version \u201d1.0\u201d end")
        assert "\u201d" not in result
        assert "'" in result

    def test_curly_single_quote_left_normalized(self):
        """U+2018 LEFT SINGLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("Next \u201826\u2019 release")
        assert "\u2018" not in result
        assert "'" in result

    def test_curly_single_quote_right_normalized(self):
        """U+2019 RIGHT SINGLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("it\u2019s fine")
        assert "\u2019" not in result
        assert "'" in result

    def test_html_entity_curly_quotes_decoded(self):
        """HTML entities &ldquo; &rdquo; &lsquo; &rsquo; decoded and normalised."""
        result = sanitize_quotes_for_yaml(
            "&ldquo;hello&rdquo; and &lsquo;world&rsquo;"
        )
        # No curly quote code points remain
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "\u2018" not in result
        assert "\u2019" not in result
        # No raw ASCII double-quote either
        assert '"' not in result
        # All replaced with apostrophe
        assert "'" in result

    def test_html_entity_numeric_curly_quotes_decoded(self):
        """HTML numeric entities &#8216; &#8217; &#8220; &#8221; decoded and normalised."""
        result = sanitize_quotes_for_yaml(
            "&#8220;double&#8221; and &#8216;single&#8217;"
        )
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "\u2018" not in result
        assert "\u2019" not in result
        assert '"' not in result
        assert "'" in result

    def test_idempotent_on_pre_normalized(self):
        """Applying sanitize_quotes_for_yaml twice gives identical result."""
        original = "Next \u201826 \u201Crelease\u201D has &ldquo;patch&rdquo;"
        once = sanitize_quotes_for_yaml(original)
        twice = sanitize_quotes_for_yaml(once)
        assert once == twice

    def test_mixed_curly_and_ascii_all_normalized(self):
        """ASCII dq, curly dq, and curly sq all normalised in one pass."""
        result = sanitize_quotes_for_yaml(
            'say "hi" and \u201chello\u201d and \u2018world\u2019'
        )
        assert '"' not in result
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "\u2018" not in result
        assert "\u2019" not in result
