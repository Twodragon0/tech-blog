#!/usr/bin/env python3
"""Regression tests for quote-safety in ai-summary-card Liquid include generation.

Prevents recurrence of the 2026-04-20 Palantir post build error where a headline
containing inner single quotes broke the Liquid include parser (outer single-quoted
arg + inner literal ' prematurely terminated the argument).

API disabling and path setup are handled by conftest.py.
"""

import re
from pathlib import Path

import pytest
from auto_publish_news import (
    _html_escape_quotes,
    generate_post_content,
    generate_tech_blog_content,
)


# ---------------------------------------------------------------------------
# Unit tests for _html_escape_quotes
# ---------------------------------------------------------------------------


class TestHtmlEscapeQuotes:
    """Tests for the _html_escape_quotes() helper."""

    def test_single_quote_replaced(self):
        assert "&#x27;" in _html_escape_quotes("포용성과 '퇴행적' 문화")

    def test_no_literal_single_quote_survives(self):
        result = _html_escape_quotes("포용성과 '퇴행적' 문화")
        assert "'" not in result

    def test_double_quote_replaced(self):
        result = _html_escape_quotes('She said "hello"')
        assert "&quot;" in result
        assert '"' not in result

    def test_ampersand_escaped_first(self):
        # Ensure & is escaped before others to avoid double-escaping
        result = _html_escape_quotes("AT&T 's deal")
        assert "&amp;" in result
        assert "&#x27;" in result
        # Must not double-encode the &amp; back into &amp;amp;
        assert "&amp;amp;" not in result

    def test_plain_text_unchanged(self):
        text = "Apple NIST Kubernetes 2026"
        assert _html_escape_quotes(text) == text

    def test_korean_no_quotes_unchanged(self):
        text = "보안 위협 분석 보고서"
        assert _html_escape_quotes(text) == text

    def test_mixed_quotes(self):
        result = _html_escape_quotes("'single' and \"double\"")
        assert "&#x27;" in result
        assert "&quot;" in result
        assert "'" not in result
        assert '"' not in result

    def test_empty_string(self):
        assert _html_escape_quotes("") == ""

    def test_already_entity_no_double_encode(self):
        # If someone passes &amp; it should not become &amp;amp;
        result = _html_escape_quotes("&amp;")
        assert result == "&amp;amp;"  # This is correct: & -> &amp;, rest unchanged


# ---------------------------------------------------------------------------
# Integration: generate_post_content (security mode) title= arg safety
# ---------------------------------------------------------------------------

def _make_security_items_with_single_quotes():
    """Minimal news item list whose title contains inner single quotes."""
    return [
        {
            "title": "Palantir, 포용성과 '퇴행적' 문화를 비난하는 소형 선언문 게시",
            "summary": "Palantir posted a manifesto criticising DEI.",
            "url": "https://example.com/palantir",
            "source_name": "TechCrunch Security",
            "source": "TechCrunch Security",
            "category": "security",
            "published": "2026-04-20T01:00:00Z",
        },
        {
            "title": "Apple 계정 변경 알림을 악용한 피싱 이메일 발송",
            "summary": "Phishing campaign targeting Apple users.",
            "url": "https://example.com/apple",
            "source_name": "BleepingComputer",
            "source": "BleepingComputer",
            "category": "security",
            "published": "2026-04-20T02:00:00Z",
        },
    ]


def _make_categorized(items):
    """Build a minimal categorized dict suitable for generate_post_content."""
    from datetime import datetime, timezone
    return {
        "security": items,
        "ai": [],
        "cloud": [],
        "devops": [],
        "blockchain": [],
        "tech": [],
    }


_TEST_DATE = __import__("datetime").datetime(2026, 4, 20, 10, 0, 0,
                                              tzinfo=__import__("datetime").timezone.utc)


class TestGeneratePostContentQuoteSafety:
    """Regression tests: ai-summary-card title arg must not contain literal inner '."""

    def test_title_arg_uses_double_quote_outer(self):
        """The title= arg in generated include must use double-quote outer."""
        items = _make_security_items_with_single_quotes()
        content = generate_post_content(items, _make_categorized(items), _TEST_DATE)
        # Find the title= line in the include block
        match = re.search(r'\{%[- ]* include ai-summary-card\.html(.*?)%\}', content, re.DOTALL)
        assert match, "ai-summary-card include block not found in generated content"
        include_block = match.group(0)
        # title= must be double-quoted outer
        assert re.search(r'\btitle="', include_block), (
            "title= arg should use double-quote outer in ai-summary-card include.\n"
            f"Include block:\n{include_block}"
        )

    def test_title_arg_no_literal_single_quote(self):
        """No literal unescaped single quote inside the title= value."""
        items = _make_security_items_with_single_quotes()
        content = generate_post_content(items, _make_categorized(items), _TEST_DATE)
        match = re.search(r'title="([^"]*)"', content)
        assert match, "title=\"...\" pattern not found in generated content"
        title_value = match.group(1)
        assert "'" not in title_value, (
            f"Literal single quote found in title= value: {title_value!r}\n"
            "This would cause a Liquid parse error."
        )

    def test_title_arg_single_quote_encoded_as_entity(self):
        """Single quotes from headline are encoded as &#x27; in the title= value."""
        items = _make_security_items_with_single_quotes()
        content = generate_post_content(items, _make_categorized(items), _TEST_DATE)
        # The title keywords derived from the items should encode single quotes
        match = re.search(r'title="([^"]*)"', content)
        if match:
            title_value = match.group(1)
            # If the title contains what would have been a single quote, it must be &#x27;
            if "퇴행적" in title_value or "Palantir" in title_value:
                assert "&#x27;" in title_value, (
                    f"Expected &#x27; encoding for inner single quotes in: {title_value!r}"
                )


# ---------------------------------------------------------------------------
# Integration: generate_tech_blog_content title= arg safety
# ---------------------------------------------------------------------------

class TestGenerateTechBlogContentQuoteSafety:
    """Same regression tests for the tech-blog variant."""

    def _make_tech_items(self):
        return [
            {
                "title": "TypeScript 5.0's 'satisfies' operator explained",
                "summary": "New TS feature explanation.",
                "url": "https://example.com/ts5",
                "source_name": "GeekNews",
                "source": "GeekNews",
                "category": "tech",
                "published": "2026-04-20T03:00:00Z",
            },
            {
                "title": "Rust's borrow checker improvements",
                "summary": "Borrow checker got better.",
                "url": "https://example.com/rust",
                "source_name": "Hacker News",
                "source": "Hacker News",
                "category": "tech",
                "published": "2026-04-20T04:00:00Z",
            },
        ]

    def _make_tech_categorized(self, items):
        return {
            "security": [],
            "ai": [],
            "cloud": [],
            "devops": [],
            "blockchain": [],
            "tech": items,
        }

    def test_title_arg_uses_double_quote_outer(self):
        items = self._make_tech_items()
        content = generate_tech_blog_content(
            items, self._make_tech_categorized(items), _TEST_DATE
        )
        match = re.search(r'\{%[- ]* include ai-summary-card\.html(.*?)%\}', content, re.DOTALL)
        assert match, "ai-summary-card include block not found in tech blog content"
        include_block = match.group(0)
        assert re.search(r'\btitle="', include_block), (
            "title= arg should use double-quote outer in ai-summary-card include.\n"
            f"Include block:\n{include_block}"
        )

    def test_title_arg_no_literal_single_quote(self):
        items = self._make_tech_items()
        content = generate_tech_blog_content(
            items, self._make_tech_categorized(items), _TEST_DATE
        )
        match = re.search(r'title="([^"]*)"', content)
        assert match, "title=\"...\" pattern not found in tech blog content"
        title_value = match.group(1)
        assert "'" not in title_value, (
            f"Literal single quote found in title= value: {title_value!r}"
        )


# ---------------------------------------------------------------------------
# Post-level scan: guard historical pattern across _posts/ latest files
# ---------------------------------------------------------------------------

_POSTS_DIR = Path(__file__).parent.parent.parent / "_posts"

# Pattern that would indicate a broken include: outer single-quote wrapping title
# and a literal unescaped ' inside it.
_BROKEN_TITLE_PATTERN = re.compile(
    r'\btitle=\'[^\']*\'[^\']*\'',  # title='...'...' — 3+ single quotes = broken
    re.DOTALL,
)

# Pattern for outer-single-quoted title with inner literal single quote.
# [^\'\n] excludes newlines so the match stays on one line and does not
# bleed into the next include argument (which starts on the next line).
_OUTER_SINGLE_INNER_SINGLE = re.compile(
    r"\btitle='([^'\n]*'[^'\n]*)'",
)


def _get_recent_posts(n: int = 10) -> list:
    """Return the n most recently modified .md files under _posts/."""
    if not _POSTS_DIR.exists():
        return []
    posts = sorted(_POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return posts[:n]


class TestPostLevelQuoteSafetyGuard:
    """Scan recent _posts/ files for the historical broken include pattern."""

    def test_no_outer_single_quote_with_inner_single_in_ai_summary_title(self):
        """In any ai-summary-card include block found in recent posts, the title=
        arg must not have a literal inner single quote when using outer single quotes.
        """
        violations = []
        for post_path in _get_recent_posts(10):
            text = post_path.read_text(encoding="utf-8")
            # Find all ai-summary-card include blocks
            for block_match in re.finditer(
                r'\{%[- ]*\s*include ai-summary-card\.html(.*?)%\}',
                text,
                re.DOTALL,
            ):
                block = block_match.group(0)
                # Check title= with outer single-quote that has inner literal '
                for m in _OUTER_SINGLE_INNER_SINGLE.finditer(block):
                    inner = m.group(1)
                    violations.append(
                        f"{post_path.name}: title='{inner}' contains unescaped single quote"
                    )

        assert not violations, (
            "Found ai-summary-card include blocks with unescaped inner single quotes "
            "in outer-single-quoted title= args:\n" + "\n".join(violations)
        )
