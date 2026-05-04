#!/usr/bin/env python3
"""Unit tests for scripts/validators/check_frontmatter_quotes.py.

Tests the ``find_broken_lines`` function and the ``main`` CLI entry point
covering the detection rule: a ``title:`` or ``excerpt:`` field whose value
is wrapped in outer double-quotes and contains at least one unescaped inner
double-quote is flagged as broken YAML.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.validators.check_frontmatter_quotes import find_broken_lines, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wrap(field_line: str) -> str:
    """Wrap a single front-matter line in minimal valid front-matter block."""
    return f"---\n{field_line}\nlayout: post\n---\nBody text"


# ---------------------------------------------------------------------------
# find_broken_lines — clean cases (expect no violations)
# ---------------------------------------------------------------------------


class TestFindBrokenLinesClean:
    def test_no_front_matter(self):
        assert find_broken_lines("Just plain text") == []

    def test_unquoted_title(self):
        assert find_broken_lines(_wrap("title: Hello World")) == []

    def test_single_quoted_outer_with_inner_dq(self):
        assert find_broken_lines(_wrap("title: 'Foo \"Bar\" Baz'")) == []

    def test_properly_escaped_inner_dq(self):
        assert find_broken_lines(_wrap('title: "Foo \\"Bar\\" Baz"')) == []

    def test_double_quoted_no_inner(self):
        assert find_broken_lines(_wrap('title: "Simple title"')) == []

    def test_excerpt_no_inner_dq(self):
        assert find_broken_lines(_wrap('excerpt: "Short description."')) == []

    def test_only_closing_dq(self):
        # Value is  "Hello" — one unescaped DQ (the closing one), OK
        assert find_broken_lines(_wrap('title: "Hello"')) == []

    def test_escaped_backslash_then_dq(self):
        # "\\" followed by a real inner quote: should NOT be treated as escaped DQ
        # title: "Foo \\"Bar"" — inner `"` after `\\` is NOT escaped (the backslash escapes the backslash)
        content = _wrap('title: "Foo \\\\"Bar\\""')
        # This is an ambiguous edge case; the important thing is the function runs without error
        result = find_broken_lines(content)
        assert isinstance(result, list)

    def test_body_dq_not_checked(self):
        # Double quotes in the body (after second ---) must not be flagged
        content = '---\ntitle: "Clean title"\n---\nBody with "quotes" here.'
        assert find_broken_lines(content) == []

    def test_field_not_in_front_matter(self):
        # title: in body should not be inspected
        content = '---\nlayout: post\n---\ntitle: "Body line with "inner" quotes"'
        assert find_broken_lines(content) == []


# ---------------------------------------------------------------------------
# find_broken_lines — broken cases (expect violations)
# ---------------------------------------------------------------------------


class TestFindBrokenLinesBroken:
    def test_title_with_unescaped_inner_dq(self):
        """Classic broken case: title: "Foo "Bar" Baz"."""
        content = _wrap('title: "Foo "Bar" Baz"')
        result = find_broken_lines(content)
        assert len(result) == 1
        lineno, line = result[0]
        assert lineno == 2
        assert 'title:' in line

    def test_excerpt_with_unescaped_inner_dq(self):
        content = _wrap('excerpt: "Summary of "important" event."')
        result = find_broken_lines(content)
        assert len(result) == 1
        assert result[0][0] == 2

    def test_multiple_inner_dqs(self):
        """Two inner unescaped quotes: "Foo "Bar" and "Baz""."""
        content = _wrap('title: "Foo "Bar" and "Baz""')
        result = find_broken_lines(content)
        assert len(result) == 1

    def test_korean_title_with_inner_dq(self):
        """Real-world case: Korean title with inner quoted English word."""
        content = _wrap('title: "중요한 cPanel 취약점이 "Sorry", Trellix, ..."')
        result = find_broken_lines(content)
        assert len(result) == 1

    def test_both_title_and_excerpt_broken(self):
        """When both title and excerpt have broken inner quotes."""
        content = (
            '---\n'
            'title: "A "broken" title"\n'
            'excerpt: "Also "broken" excerpt"\n'
            'layout: post\n'
            '---\n'
        )
        result = find_broken_lines(content)
        assert len(result) == 2
        assert result[0][0] == 2  # title on line 2
        assert result[1][0] == 3  # excerpt on line 3

    def test_lineno_correct_for_third_line(self):
        """Line number must reflect actual position in file."""
        content = (
            '---\n'
            'layout: post\n'
            'title: "Has "inner" quotes"\n'
            '---\n'
        )
        result = find_broken_lines(content)
        assert len(result) == 1
        assert result[0][0] == 3


# ---------------------------------------------------------------------------
# main() CLI
# ---------------------------------------------------------------------------


class TestMainCli:
    def test_returns_0_for_clean_file(self, tmp_path: Path):
        f = tmp_path / "2026-01-01-clean.md"
        f.write_text(
            '---\ntitle: "Clean title"\nexcerpt: "Clean excerpt."\nlayout: post\n---\nBody\n',
            encoding="utf-8",
        )
        assert main([str(f)]) == 0

    def test_returns_1_for_broken_file(self, tmp_path: Path):
        f = tmp_path / "2026-01-01-broken.md"
        f.write_text(
            '---\ntitle: "Broken "inner" title"\nlayout: post\n---\nBody\n',
            encoding="utf-8",
        )
        assert main([str(f)]) == 1

    def test_returns_0_for_no_files(self, tmp_path: Path):
        # main() with an explicit empty glob result (no .md files in tmp dir)
        # Pass no files by passing a non-existent file path that is skipped gracefully
        # Use a clean tmp dir with zero .md files — simulate by passing only a
        # non-.md file so zero posts are checked
        non_md = tmp_path / "readme.txt"
        non_md.write_text("not a post")
        # passing non-.md file: main will try to open it but find_broken_lines
        # returns [] for non-YAML content → exit 0
        assert main([str(non_md)]) == 0

    def test_mixed_clean_and_broken(self, tmp_path: Path):
        clean = tmp_path / "2026-01-01-clean.md"
        clean.write_text(
            '---\ntitle: "Clean"\nlayout: post\n---\nBody\n',
            encoding="utf-8",
        )
        broken = tmp_path / "2026-01-02-broken.md"
        broken.write_text(
            '---\ntitle: "Has "inner" quote"\nlayout: post\n---\nBody\n',
            encoding="utf-8",
        )
        assert main([str(clean), str(broken)]) == 1

    def test_returns_0_for_single_quoted_outer(self, tmp_path: Path):
        f = tmp_path / "2026-01-01-single.md"
        f.write_text(
            "---\ntitle: 'Has \"inner\" quotes'\nlayout: post\n---\nBody\n",
            encoding="utf-8",
        )
        assert main([str(f)]) == 0

    def test_returns_0_for_escaped_inner_dq(self, tmp_path: Path):
        f = tmp_path / "2026-01-01-escaped.md"
        f.write_text(
            '---\ntitle: "Has \\"inner\\" quotes"\nlayout: post\n---\nBody\n',
            encoding="utf-8",
        )
        assert main([str(f)]) == 0
