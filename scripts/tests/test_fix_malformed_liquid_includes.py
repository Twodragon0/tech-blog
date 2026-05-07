#!/usr/bin/env python3
"""Tests for scripts/fix_malformed_liquid_includes.py.

Covers:
1.  test_single_quoted_inner_apostrophe_detected
2.  test_single_quoted_inner_apostrophe_auto_fixed_to_curly
3.  test_double_quoted_inner_quote_detected
4.  test_double_quoted_inner_quote_auto_fixed
5.  test_no_false_positive_on_clean_includes
6.  test_idempotent_after_fix
7.  test_check_mode_returns_nonzero_on_violations
8.  (existing) curly-quote normalisation
9.  (existing) malformed %% tag patterns
10. pre-existing: detect_attr_conflicts API
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.fix_malformed_liquid_includes import (
    check_content,
    detect_attr_conflicts,
    fix_content,
    process_file,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NEWS_BLOCK_CLEAN = """\
{% include news-card.html
  title='Normal title'
  url='https://example.com'
  summary='Short summary.'
%}"""

_AI_BLOCK_CLEAN = """\
{% include ai-summary-card.html
  title="Digest title"
  highlights_html='<li>Item one</li><li>Item two</li>'
  period='2026-05-07'
%}"""

_AI_BLOCK_APOSTROPHE_CONFLICT = """\
{% include ai-summary-card.html
  title="Test"
  highlights_html='<li>Google Cloud Next '26</li>'
  period='2026-05-06'
%}"""

_AI_BLOCK_APOSTROPHE_FIXED = """\
{% include ai-summary-card.html
  title="Test"
  highlights_html='<li>Google Cloud Next \u201926</li>'
  period='2026-05-06'
%}"""

_NEWS_BLOCK_DQ_CONFLICT = """\
{% include news-card.html title="He said "hello" there" url='https://x.com' %}"""

_NEWS_BLOCK_DQ_FIXED = """\
{% include news-card.html title="He said \u201dhello\u201d there" url='https://x.com' %}"""


def _make_md(body: str) -> str:
    return f"---\nlayout: post\ntitle: Test\n---\n{body}\n"


# ---------------------------------------------------------------------------
# 1. detect_attr_conflicts — single-quoted inner apostrophe DETECTED
# ---------------------------------------------------------------------------


class TestSingleQuotedInnerApostropheDetected:
    def test_conflict_reported_for_apostrophe_in_single_quoted(self):
        conflicts = detect_attr_conflicts(_AI_BLOCK_APOSTROPHE_CONFLICT)
        assert len(conflicts) >= 1

    def test_conflict_attr_name_is_highlights_html(self):
        conflicts = detect_attr_conflicts(_AI_BLOCK_APOSTROPHE_CONFLICT)
        attr_names = [c[0] for c in conflicts]
        assert "highlights_html" in attr_names

    def test_conflict_description_mentions_apostrophe(self):
        conflicts = detect_attr_conflicts(_AI_BLOCK_APOSTROPHE_CONFLICT)
        descs = " ".join(c[1] for c in conflicts)
        assert "apostrophe" in descs

    def test_clean_block_has_no_conflicts(self):
        assert detect_attr_conflicts(_NEWS_BLOCK_CLEAN) == []

    def test_clean_ai_block_has_no_conflicts(self):
        assert detect_attr_conflicts(_AI_BLOCK_CLEAN) == []

    def test_inline_apostrophe_conflict(self):
        block = "{% include news-card.html title='Next '26 release' %}"
        conflicts = detect_attr_conflicts(block)
        assert len(conflicts) == 1
        assert conflicts[0][0] == "title"

    def test_multiple_attrs_only_broken_ones_flagged(self):
        block = (
            "{% include news-card.html "
            "title='Clean title' "
            "summary='Has '26 apostrophe' "
            "url='https://clean.com' %}"
        )
        conflicts = detect_attr_conflicts(block)
        attr_names = [c[0] for c in conflicts]
        assert "summary" in attr_names
        assert "title" not in attr_names
        assert "url" not in attr_names


# ---------------------------------------------------------------------------
# 2. fix_content — single-quoted inner apostrophe AUTO-FIXED to curly (U+2019)
# ---------------------------------------------------------------------------


class TestSingleQuotedInnerApostropheAutoFixed:
    def test_apostrophe_replaced_with_curly(self):
        content = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        fixed, changes = fix_content(content)
        assert changes >= 1
        assert "\u2019" in fixed  # curly apostrophe present
        assert "Next \u201926" in fixed

    def test_outer_quotes_preserved_after_fix(self):
        content = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        fixed, _ = fix_content(content)
        # The outer single-quote delimiters must still be present
        assert "highlights_html='" in fixed
        assert "period='" in fixed

    def test_fix_matches_expected_block(self):
        fixed, changes = fix_content(_AI_BLOCK_APOSTROPHE_CONFLICT)
        assert _AI_BLOCK_APOSTROPHE_FIXED in fixed

    def test_inline_fix_apostrophe(self):
        block = "{% include news-card.html title='Next '26 release' %}"
        expected = "{% include news-card.html title='Next \u201926 release' %}"
        fixed, changes = fix_content(block)
        assert changes >= 1
        assert expected in fixed


# ---------------------------------------------------------------------------
# 3. detect_attr_conflicts — double-quoted inner double-quote DETECTED
# ---------------------------------------------------------------------------


class TestDoubleQuotedInnerQuoteDetected:
    def test_conflict_reported_for_dq_in_double_quoted(self):
        conflicts = detect_attr_conflicts(_NEWS_BLOCK_DQ_CONFLICT)
        assert len(conflicts) >= 1

    def test_conflict_attr_name_is_title(self):
        conflicts = detect_attr_conflicts(_NEWS_BLOCK_DQ_CONFLICT)
        attr_names = [c[0] for c in conflicts]
        assert "title" in attr_names

    def test_conflict_description_mentions_double_quote(self):
        conflicts = detect_attr_conflicts(_NEWS_BLOCK_DQ_CONFLICT)
        descs = " ".join(c[1] for c in conflicts)
        assert "double-quote" in descs

    def test_clean_double_quoted_no_conflict(self):
        block = '{% include news-card.html title="Clean title" %}'
        assert detect_attr_conflicts(block) == []


# ---------------------------------------------------------------------------
# 4. fix_content — double-quoted inner double-quote AUTO-FIXED to curly
# ---------------------------------------------------------------------------


class TestDoubleQuotedInnerQuoteAutoFixed:
    def test_dq_replaced_with_curly(self):
        content = _make_md(_NEWS_BLOCK_DQ_CONFLICT)
        fixed, changes = fix_content(content)
        assert changes >= 1
        assert "\u201d" in fixed

    def test_fix_matches_expected_block(self):
        fixed, changes = fix_content(_NEWS_BLOCK_DQ_CONFLICT)
        assert changes >= 1
        assert _NEWS_BLOCK_DQ_FIXED in fixed


# ---------------------------------------------------------------------------
# 5. No false positives on clean includes
# ---------------------------------------------------------------------------


class TestNoFalsePositiveOnCleanIncludes:
    def test_clean_news_block(self):
        content = _make_md(_NEWS_BLOCK_CLEAN)
        _, changes = fix_content(content)
        assert changes == 0

    def test_clean_ai_block(self):
        content = _make_md(_AI_BLOCK_CLEAN)
        _, changes = fix_content(content)
        assert changes == 0

    def test_curly_apostrophe_in_value_is_safe(self):
        """U+2019 inside a single-quoted attr does NOT conflict."""
        block = "{% include news-card.html title='Google\u2019s feature' %}"
        _, changes = fix_content(block)
        assert changes == 0
        assert detect_attr_conflicts(block) == []

    def test_html_entity_apostrophe_is_safe(self):
        """&#x27; is not an ASCII apostrophe — must not trigger."""
        block = "{% include news-card.html title='Google&#x27;s feature' %}"
        assert detect_attr_conflicts(block) == []

    def test_curly_left_single_in_single_quoted_is_safe(self):
        """U+2018 LEFT SINGLE QUOTATION MARK is not ASCII ' — no conflict."""
        block = "{% include news-card.html title='\u2018quoted\u2019 title' %}"
        assert detect_attr_conflicts(block) == []

    def test_non_include_block_ignored(self):
        content = "{% if x == 'y' %}hello{% endif %}"
        violations = check_content(content)
        assert violations == []

    def test_no_include_at_all(self):
        content = _make_md("No include tags here.\n")
        violations = check_content(content)
        assert violations == []


# ---------------------------------------------------------------------------
# 6. Idempotent: running fix twice yields same result
# ---------------------------------------------------------------------------


class TestIdempotentAfterFix:
    def test_fix_apostrophe_idempotent(self):
        content = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        fixed1, _ = fix_content(content)
        fixed2, changes2 = fix_content(fixed1)
        assert fixed1 == fixed2
        assert changes2 == 0

    def test_fix_dq_idempotent(self):
        content = _make_md(_NEWS_BLOCK_DQ_CONFLICT)
        fixed1, _ = fix_content(content)
        fixed2, changes2 = fix_content(fixed1)
        assert fixed1 == fixed2
        assert changes2 == 0

    def test_already_fixed_block_unchanged(self):
        """Blocks that are already correct must not be modified."""
        content = _make_md(_AI_BLOCK_APOSTROPHE_FIXED)
        _, changes = fix_content(content)
        assert changes == 0

    def test_clean_block_unchanged(self):
        content = _make_md(_NEWS_BLOCK_CLEAN)
        fixed, changes = fix_content(content)
        assert changes == 0
        assert fixed == content


# ---------------------------------------------------------------------------
# 7. check_mode: returns non-zero exit on violations
# ---------------------------------------------------------------------------


class TestCheckModeReturnsNonzeroOnViolations:
    def test_check_content_returns_violations_for_apostrophe(self):
        content = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        violations = check_content(content)
        assert len(violations) >= 1

    def test_check_content_violation_has_correct_lineno(self):
        content = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        violations = check_content(content)
        linenos = [v[0] for v in violations]
        # The include block starts at line 5 (after 4 front-matter lines + body start)
        assert all(ln >= 1 for ln in linenos)

    def test_check_content_returns_empty_for_clean(self):
        content = _make_md(_NEWS_BLOCK_CLEAN)
        assert check_content(content) == []

    def test_process_file_check_returns_violation_count(self, tmp_path: Path):
        p = tmp_path / "2026-05-06-test.md"
        p.write_text(_make_md(_AI_BLOCK_APOSTROPHE_CONFLICT), encoding="utf-8")
        count = process_file(p, write=False)
        assert count >= 1

    def test_process_file_check_does_not_modify_file(self, tmp_path: Path):
        p = tmp_path / "2026-05-06-test.md"
        original = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        p.write_text(original, encoding="utf-8")
        process_file(p, write=False)
        assert p.read_text(encoding="utf-8") == original

    def test_process_file_write_fixes_file(self, tmp_path: Path):
        p = tmp_path / "2026-05-06-test.md"
        p.write_text(_make_md(_AI_BLOCK_APOSTROPHE_CONFLICT), encoding="utf-8")
        count = process_file(p, write=True)
        assert count >= 1
        fixed = p.read_text(encoding="utf-8")
        # After fix, check_content should find no violations
        assert check_content(fixed) == []


# ---------------------------------------------------------------------------
# 8. Existing curly-quote normalisation behaviour preserved
# ---------------------------------------------------------------------------


class TestCurlyQuoteNormalisationPreserved:
    def test_curly_double_in_include_fixed(self):
        block = "{% include news-card.html title='\u201cTest\u201d title' %}"
        fixed, changes = fix_content(block)
        assert changes >= 1
        # After fix, no curly double quotes remain in the block
        assert "\u201c" not in fixed
        assert "\u201d" not in fixed

    def test_curly_single_in_include_fixed(self):
        block = "{% include news-card.html title='\u2018Left\u2019right' %}"
        fixed, changes = fix_content(block)
        assert changes >= 1

    def test_content_outside_include_unchanged(self):
        """Curly quotes in regular markdown body should NOT be touched."""
        content = (
            "---\nlayout: post\ntitle: Test\n---\n"
            "이 기능은 \u201c혁신적\u201d이라고 불립니다.\n"
        )
        fixed, changes = fix_content(content)
        assert changes == 0
        assert "\u201c" in fixed


# ---------------------------------------------------------------------------
# 9. Existing malformed %% tag patterns preserved
# ---------------------------------------------------------------------------


class TestMalformedTagPatterns:
    def test_double_percent_open_fixed(self):
        content = "{%% include news-card.html title='T' %%}"
        fixed, changes = fix_content(content)
        assert changes >= 1
        assert "{%%" not in fixed

    def test_double_percent_close_fixed(self):
        content = "{% include news-card.html title='T' %%}"
        fixed, changes = fix_content(content)
        assert changes >= 1
        assert "%%}" not in fixed


# ---------------------------------------------------------------------------
# 10. check_content API: lineno, include_name, description
# ---------------------------------------------------------------------------


class TestCheckContentAPI:
    def test_violation_tuple_has_three_elements(self):
        content = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        violations = check_content(content)
        assert all(len(v) == 3 for v in violations)

    def test_violation_include_name_correct(self):
        content = _make_md(_AI_BLOCK_APOSTROPHE_CONFLICT)
        violations = check_content(content)
        include_names = [v[1] for v in violations]
        assert "ai-summary-card" in include_names

    def test_violation_for_curly_quote_outside_value_detected(self):
        """A curly quote that sits OUTSIDE an attribute value is flagged.

        This can happen when Liquid's naive parser terminates a value early
        (due to an inner apostrophe), leaving a curly quote as stray text
        between attributes.  We simulate that by placing a curly character
        in the attribute-name position (before any =), which is outside all
        values.
        """
        # Build a block where a curly quote sits between attribute assignments,
        # i.e. outside any quoted value — that is a genuine violation.
        block = (
            "{% include news-card.html "
            "title='Clean' "
            "\u2019stray"  # curly apostrophe outside any value
            " url='https://x.com' %}"
        )
        violations = check_content(block)
        assert len(violations) >= 1
        assert any("U+2019" in v[2] or "curly" in v[2].lower() for v in violations)

    def test_mixed_violations_both_reported(self):
        """A block with BOTH curly quote and apostrophe conflict — both detected."""
        # curly \u2018 gets normalised to ASCII ' first, which then creates a conflict
        block = "{% include news-card.html title='\u2018Next '26\u2019' %}"
        violations = check_content(block)
        assert len(violations) >= 1
