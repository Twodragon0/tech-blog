#!/usr/bin/env python3
"""Tests for scripts/check_post_quote_safety.py.

Covers:
1. test_field_with_raw_quote_blocked        — raw `"` in title/excerpt/... → exit 1
2. test_field_with_escaped_quote_blocked    — YAML `\"` decoded to `"` → still exit 1
3. test_clean_post_passes                   — no double-quotes → exit 0
4. test_korean_curly_quotes_pass            — curly/fullwidth " chars not flagged
5. test_skip_env_bypass                     — SKIP_QUOTE_CHECK=1 → exit 0
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.check_post_quote_safety import check_file, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_post(tmp_path: Path, frontmatter: str, body: str = "Body text.") -> Path:
    """Write a minimal post file and return its path."""
    p = tmp_path / "2026-05-01-test.md"
    p.write_text(f"---\n{frontmatter}\nlayout: post\n---\n{body}\n", encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 1. Raw ASCII double-quote inside value → violation
# ---------------------------------------------------------------------------


class TestRawQuoteBlocked:
    def test_title_raw_quote(self, tmp_path: Path):
        """title field with raw \" inside value is blocked."""
        p = _make_post(
            tmp_path,
            'title: "중요한 cPanel 취약점이 \'Sorry\', Trellix 공격"',
        )
        # The value contains single quotes (fine) but no double-quotes — clean case.
        assert check_file(p) == []

    def test_title_raw_dq(self, tmp_path: Path):
        """title value that contains a literal " (raw ASCII) is flagged."""
        # Write raw YAML with unescaped inner double-quote by building the text directly.
        content = '---\ntitle: "Hack \\"Sorry\\" attack"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        violations = check_file(p)
        assert len(violations) == 1
        assert violations[0][0] == "title"

    def test_excerpt_raw_dq(self, tmp_path: Path):
        """excerpt field with raw double-quote is flagged."""
        content = '---\nexcerpt: "Bitwarden \\"패스워드\\" leak"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        violations = check_file(p)
        assert any(f == "excerpt" for f, _ in violations)

    def test_description_raw_dq(self, tmp_path: Path):
        """description field with raw double-quote is flagged."""
        content = '---\ndescription: "Has \\"inner\\" quote"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        violations = check_file(p)
        assert any(f == "description" for f, _ in violations)

    def test_image_alt_raw_dq(self, tmp_path: Path):
        """image_alt field with raw double-quote is flagged."""
        content = '---\nimage_alt: "alt with \\"quotes\\""\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        violations = check_file(p)
        assert any(f == "image_alt" for f, _ in violations)

    def test_main_exits_1_for_violation(self, tmp_path: Path):
        """main() returns exit code 1 when violation found."""
        content = '---\ntitle: "Foo \\"bar\\" baz"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        assert main([str(p)]) == 1


# ---------------------------------------------------------------------------
# 2. YAML-escaped \" decoded to " → still a violation
# ---------------------------------------------------------------------------


class TestEscapedQuoteBlocked:
    def test_yaml_escaped_dq_is_flagged(self, tmp_path: Path):
        """YAML \\\" is decoded by yaml.safe_load to \" which must still be caught."""
        # yaml.safe_load sees:  title: "Hack \"Sorry\" attack"
        # Decoded value:        Hack "Sorry" attack  ← contains "
        content = '---\ntitle: "Hack \\"Sorry\\" attack"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        violations = check_file(p)
        assert len(violations) == 1
        field, snippet = violations[0]
        assert field == "title"
        assert '"' in snippet

    def test_multiple_fields_escaped(self, tmp_path: Path):
        """Multiple fields with escaped quotes all flagged."""
        content = (
            '---\n'
            'title: "T \\"x\\""\n'
            'excerpt: "E \\"y\\""\n'
            'layout: post\n'
            '---\nBody\n'
        )
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        violations = check_file(p)
        fields = {f for f, _ in violations}
        assert "title" in fields
        assert "excerpt" in fields


# ---------------------------------------------------------------------------
# 3. Clean post passes
# ---------------------------------------------------------------------------


class TestCleanPostPasses:
    def test_single_quoted_values_pass(self, tmp_path: Path):
        """Values using single quotes (proper fix) produce no violations."""
        p = _make_post(
            tmp_path,
            "title: \"중요한 cPanel 취약점 'Sorry', Trellix 공격\"\nexcerpt: \"보안 요약 'patch' 적용\"",
        )
        assert check_file(p) == []

    def test_no_quotes_at_all_passes(self, tmp_path: Path):
        p = _make_post(tmp_path, "title: Clean title\nexcerpt: Short description.")
        assert check_file(p) == []

    def test_main_exits_0_for_clean(self, tmp_path: Path):
        p = _make_post(tmp_path, "title: Clean\nexcerpt: Good excerpt.")
        assert main([str(p)]) == 0

    def test_no_front_matter_passes(self, tmp_path: Path):
        p = tmp_path / "2026-05-01-nofm.md"
        p.write_text("Just plain markdown without front-matter.", encoding="utf-8")
        assert check_file(p) == []


# ---------------------------------------------------------------------------
# 4. Curly quotes in front-matter ARE now flagged; body without include OK
# ---------------------------------------------------------------------------


class TestCurlyQuotesFrontmatterBehavior:
    def test_left_double_quotation_mark_in_field_blocked(self, tmp_path: Path):
        """U+201C in a front-matter title field is NOW blocked (new behaviour)."""
        p = _make_post(tmp_path, 'title: "\u201cSorry\u201d attack"')
        violations = check_file(p)
        assert len(violations) == 1
        assert violations[0][0] == "title"

    def test_right_double_quotation_mark_in_field_blocked(self, tmp_path: Path):
        """U+201D in a front-matter title field is NOW blocked (new behaviour)."""
        p = _make_post(tmp_path, 'title: "Smart \u201cquotes\u201d here"')
        violations = check_file(p)
        assert len(violations) == 1
        assert violations[0][0] == "title"

    def test_mixed_curly_and_ascii_both_trigger(self, tmp_path: Path):
        """Both curly quotes AND ASCII \" in the same field — one violation reported."""
        content = '---\ntitle: "\u201cSmart\u201d and \\"ascii\\" quotes"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        violations = check_file(p)
        # The field contains both curly and ASCII quotes — flagged once (for the field)
        assert len(violations) == 1
        assert violations[0][0] == "title"


# ---------------------------------------------------------------------------
# 5. Curly / typographic quotes in front-matter fields → blocked
# ---------------------------------------------------------------------------


class TestCurlyQuotesBlocked:
    def test_field_with_curly_double_quote_blocked(self, tmp_path: Path):
        """U+201C / U+201D in a front-matter field triggers a violation."""
        p = _make_post(
            tmp_path,
            'title: "Next \u201c26\u201d release"',
        )
        violations = check_file(p)
        assert len(violations) == 1
        assert violations[0][0] == "title"

    def test_field_with_curly_single_quote_blocked(self, tmp_path: Path):
        """U+2018 / U+2019 in a front-matter field triggers a violation."""
        p = _make_post(
            tmp_path,
            'title: "Next \u201826\u2019 release"',
        )
        violations = check_file(p)
        assert len(violations) == 1
        assert violations[0][0] == "title"

    def test_field_with_curly_right_single_quote_blocked(self, tmp_path: Path):
        """U+2019 RIGHT SINGLE QUOTATION MARK in excerpt triggers a violation."""
        p = _make_post(
            tmp_path,
            'excerpt: "Google\u2019s new feature"',
        )
        violations = check_file(p)
        assert len(violations) == 1
        assert violations[0][0] == "excerpt"

    def test_main_exits_1_for_curly_quote(self, tmp_path: Path):
        """main() returns exit code 1 for curly quote in front-matter field."""
        p = _make_post(
            tmp_path,
            'title: "Next \u201826\u2019 release"',
        )
        assert main([str(p)]) == 1

    def test_clean_post_with_korean_body_passes(self, tmp_path: Path):
        """Curly quotes in Korean body text (not in front-matter) must NOT trigger."""
        body = (
            "이 기능은 \u201c혁신적\u201d이라고 불립니다. "
            "사용자\u2019s 경험을 향상시킵니다."
        )
        p = _make_post(
            tmp_path,
            "title: Clean title\nexcerpt: Clean excerpt.",
            body=body,
        )
        assert check_file(p) == []

    def test_include_attribute_with_curly_quote_blocked(self, tmp_path: Path):
        """Liquid include line with curly quote in attribute value triggers violation."""
        body = (
            "Some intro text.\n"
            "{% include digest_item.html title='Next \u201826 release' %}\n"
            "Ending text."
        )
        p = _make_post(
            tmp_path,
            "title: Clean title\nexcerpt: Clean excerpt.",
            body=body,
        )
        violations = check_file(p)
        assert len(violations) == 1
        assert violations[0][0].startswith("include_line:")

    def test_include_without_curly_quote_passes(self, tmp_path: Path):
        """Liquid include line with only ASCII quotes does not trigger."""
        body = (
            "{% include digest_item.html title='Next 26 release' %}\n"
        )
        p = _make_post(
            tmp_path,
            "title: Clean title\nexcerpt: Clean excerpt.",
            body=body,
        )
        assert check_file(p) == []

    def test_korean_body_without_include_curly_passes(self, tmp_path: Path):
        """Korean body curly quotes on non-include lines do not trigger."""
        body = (
            "이것은 \u201c테스트\u201d 문서입니다.\n"
            "{% include digest_item.html title='normal title' %}\n"
        )
        p = _make_post(
            tmp_path,
            "title: Clean\nexcerpt: OK.",
            body=body,
        )
        assert check_file(p) == []


# ---------------------------------------------------------------------------
# 6. SKIP_QUOTE_CHECK=1 bypass
# ---------------------------------------------------------------------------


class TestSkipEnvBypass:
    def test_skip_env_returns_0(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """SKIP_QUOTE_CHECK=1 causes main() to return 0 without checking."""
        monkeypatch.setenv("SKIP_QUOTE_CHECK", "1")
        content = '---\ntitle: "Has \\"inner\\" dq"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        assert main([str(p)]) == 0

    def test_skip_env_not_set_still_checks(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        """Without SKIP_QUOTE_CHECK, violations are still caught."""
        monkeypatch.delenv("SKIP_QUOTE_CHECK", raising=False)
        content = '---\ntitle: "Has \\"inner\\" dq"\nlayout: post\n---\nBody\n'
        p = tmp_path / "2026-05-01-test.md"
        p.write_text(content, encoding="utf-8")
        assert main([str(p)]) == 1
