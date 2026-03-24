#!/usr/bin/env python3
"""Unit tests for check_posts.py validation functions."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.check_posts import (
    extract_front_matter,
    check_dummy_links,
    check_image_paths,
    check_long_code_blocks,
    check_ai_summary_card,
    check_news_card_severity,
    check_table_cell_truncation,
    check_duplicate_practical_points,
)


# ---------------------------------------------------------------------------
# extract_front_matter
# ---------------------------------------------------------------------------

class TestExtractFrontMatter:
    def test_returns_parsed_dict_for_valid_front_matter(self):
        content = "---\ntitle: Hello\nlayout: post\n---\nBody text"
        fm, body = extract_front_matter(content)
        assert fm["title"] == "Hello"
        assert fm["layout"] == "post"

    def test_body_contains_content_after_second_delimiter(self):
        content = "---\ntitle: Test\n---\nThis is the body."
        _, body = extract_front_matter(content)
        assert "This is the body." in body

    def test_returns_empty_dict_when_no_front_matter_delimiter(self):
        content = "Just plain content without front matter."
        fm, _ = extract_front_matter(content)
        assert fm == {}

    def test_returns_empty_dict_for_incomplete_front_matter(self):
        content = "---\ntitle: Broken"
        fm, _ = extract_front_matter(content)
        assert fm == {}

    def test_returns_empty_dict_for_invalid_yaml(self):
        content = "---\n: invalid: yaml: content\n---\nBody"
        fm, _ = extract_front_matter(content)
        assert fm == {}

    def test_handles_empty_front_matter_block(self):
        content = "---\n---\nBody"
        fm, body = extract_front_matter(content)
        assert isinstance(fm, dict)
        assert "Body" in body


# ---------------------------------------------------------------------------
# check_dummy_links
# ---------------------------------------------------------------------------

class TestCheckDummyLinks:
    def test_detects_github_example_link(self):
        content = "See https://github.com/example/repo for details."
        issues = check_dummy_links(content)
        assert any("github.com/example" in i for i in issues)

    def test_detects_placeholder_url(self):
        content = "Visit https://example.com/placeholder/endpoint"
        issues = check_dummy_links(content)
        assert any("placeholder" in i for i in issues)

    def test_detects_korean_dummy_word(self):
        content = "This is a 더미 link."
        issues = check_dummy_links(content)
        assert any("더미" in i for i in issues)

    def test_clean_content_returns_no_issues(self):
        content = "Visit https://real-site.com/actual-path for more info."
        issues = check_dummy_links(content)
        assert issues == []

    def test_reports_correct_line_number(self):
        content = "Line one.\nLine two with github.com/example/test here."
        issues = check_dummy_links(content)
        assert any("line 2" in i for i in issues)


# ---------------------------------------------------------------------------
# check_image_paths
# ---------------------------------------------------------------------------

class TestCheckImagePaths:
    def test_detects_korean_in_markdown_image_path(self):
        content = "![alt text](/assets/images/한글이미지.png)"
        issues = check_image_paths(content)
        assert any("Korean" in i for i in issues)

    def test_detects_korean_in_html_img_src(self):
        content = '<img src="/assets/images/이미지파일.png" alt="test"/>'
        issues = check_image_paths(content)
        assert any("Korean" in i for i in issues)

    def test_clean_english_path_returns_no_issues(self):
        content = "![diagram](/assets/images/architecture-diagram.svg)"
        issues = check_image_paths(content)
        assert issues == []

    def test_reports_correct_line_number_for_korean_image(self):
        content = "First line.\n![img](/assets/images/한글.png)"
        issues = check_image_paths(content)
        assert any("line 2" in i for i in issues)


# ---------------------------------------------------------------------------
# check_long_code_blocks
# ---------------------------------------------------------------------------

class TestCheckLongCodeBlocks:
    def test_flags_code_block_with_30_or_more_lines(self):
        block_lines = "\n".join(f"line {i}" for i in range(30))
        content = f"```python\n{block_lines}\n```"
        issues = check_long_code_blocks(content)
        assert len(issues) == 1
        assert "Long code block" in issues[0]

    def test_flags_code_block_exceeding_1000_chars(self):
        long_line = "x" * 1001
        content = f"```bash\n{long_line}\n```"
        issues = check_long_code_blocks(content)
        assert len(issues) == 1

    def test_short_code_block_returns_no_issues(self):
        content = "```python\nprint('hello')\n```"
        issues = check_long_code_blocks(content)
        assert issues == []

    def test_skips_code_block_inside_html_comment(self):
        block_lines = "\n".join(f"line {i}" for i in range(30))
        content = f"<!-- \n```python\n{block_lines}\n```\n-->"
        issues = check_long_code_blocks(content)
        assert issues == []

    def test_skips_code_block_inside_details_element(self):
        block_lines = "\n".join(f"line {i}" for i in range(30))
        content = f"<details>\n```python\n{block_lines}\n```\n</details>"
        issues = check_long_code_blocks(content)
        assert issues == []


# ---------------------------------------------------------------------------
# check_ai_summary_card
# ---------------------------------------------------------------------------

class TestCheckAiSummaryCard:
    def test_returns_warning_when_summary_card_absent(self):
        content = "Some content without any summary card."
        issues = check_ai_summary_card(content)
        assert len(issues) == 1
        assert "AI summary card" in issues[0]

    def test_no_issue_when_summary_card_present(self):
        content = "{% include ai-summary-card.html %}"
        issues = check_ai_summary_card(content)
        assert issues == []

    def test_case_insensitive_detection(self):
        content = "{% include AI-SUMMARY-CARD.html %}"
        issues = check_ai_summary_card(content)
        assert issues == []


# ---------------------------------------------------------------------------
# check_news_card_severity
# ---------------------------------------------------------------------------

class TestCheckNewsCardSeverity:
    def test_flags_news_card_missing_severity(self):
        content = '{% include news-card.html title="Breach discovered" %}'
        issues = check_news_card_severity(content)
        assert len(issues) == 1
        assert "severity" in issues[0]

    def test_no_issue_when_severity_present(self):
        content = '{% include news-card.html title="Breach" severity="high" %}'
        issues = check_news_card_severity(content)
        assert issues == []

    def test_multiple_cards_each_missing_severity_each_flagged(self):
        content = (
            '{% include news-card.html title="A" %}\n'
            '{% include news-card.html title="B" severity="low" %}\n'
            '{% include news-card.html title="C" %}'
        )
        issues = check_news_card_severity(content)
        assert len(issues) == 2

    def test_no_cards_in_content_returns_no_issues(self):
        content = "Regular content with no news cards."
        issues = check_news_card_severity(content)
        assert issues == []


# ---------------------------------------------------------------------------
# check_table_cell_truncation
# ---------------------------------------------------------------------------

class TestCheckTableCellTruncation:
    def test_flags_cell_ending_with_trailing_comma(self):
        content = "| Header |\n|--------|\n| some content, |"
        issues = check_table_cell_truncation(content)
        assert any("잘림" in i for i in issues)

    def test_flags_cell_ending_with_dangling_preposition(self):
        content = "| Col1 | Col2 |\n|------|------|\n| value | connected with |"
        issues = check_table_cell_truncation(content)
        assert any("잘림" in i for i in issues)

    def test_clean_table_returns_no_issues(self):
        content = "| Name | Value |\n|------|-------|\n| Alpha | 완료됨 |"
        issues = check_table_cell_truncation(content)
        assert issues == []

    def test_separator_row_not_flagged(self):
        # The dashes-only separator row |---|---| must not produce issues.
        # Use realistic header text that avoids single-letter preposition triggers.
        content = "| Name | Status |\n|------|--------|\n| Alpha | 완료됨 |"
        issues = check_table_cell_truncation(content)
        assert issues == []

    def test_non_table_lines_not_flagged(self):
        content = "This line has a trailing comma,\nBut it is not a table row."
        issues = check_table_cell_truncation(content)
        assert issues == []


# ---------------------------------------------------------------------------
# check_duplicate_practical_points
# ---------------------------------------------------------------------------

class TestCheckDuplicatePracticalPoints:
    def test_flags_bullet_repeated_three_or_more_times(self):
        bullet = "- 보안 정책을 수립하세요."
        section = "## 실무 적용 포인트\n" + (bullet + "\n") * 3
        issues = check_duplicate_practical_points(section)
        assert len(issues) == 1
        assert "반복" in issues[0]

    def test_no_flag_when_bullet_appears_twice(self):
        bullet = "- 팀 내 공유 필요."
        section = "## 실무 적용 포인트\n" + (bullet + "\n") * 2
        issues = check_duplicate_practical_points(section)
        assert issues == []

    def test_no_flag_outside_practical_points_section(self):
        content = "## 다른 섹션\n- 같은 내용\n- 같은 내용\n- 같은 내용\n"
        issues = check_duplicate_practical_points(content)
        assert issues == []

    def test_section_ends_at_next_heading(self):
        content = (
            "## 실무 적용 포인트\n"
            "- 반복 항목\n" * 3
            + "## 다른 섹션\n"
            "- 반복 항목\n" * 3
        )
        issues = check_duplicate_practical_points(content)
        # Only counted within the section, not across sections
        assert len(issues) == 1
