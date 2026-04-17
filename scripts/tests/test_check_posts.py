#!/usr/bin/env python3
"""Unit tests for check_posts.py validation functions."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.check_posts import (
    check_ai_summary_card,
    check_dummy_links,
    check_duplicate_practical_points,
    check_image_exists,
    check_image_files,
    check_image_paths,
    check_long_code_blocks,
    check_news_card_severity,
    check_practical_points_uniqueness,
    check_svg_text_density,
    check_table_cell_truncation,
    extract_front_matter,
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

    def test_flag_when_bullet_appears_twice(self):
        """Threshold lowered from 3→2: duplicate bullets are now flagged on
        the first repeat so the generator's fallback branch regression is
        caught immediately rather than waiting for a third occurrence."""
        bullet = "- 팀 내 공유 필요."
        section = "## 실무 적용 포인트\n" + (bullet + "\n") * 2
        issues = check_duplicate_practical_points(section)
        assert len(issues) == 1
        assert "반복 2회" in issues[0]

    def test_no_flag_outside_practical_points_section(self):
        content = "## 다른 섹션\n- 같은 내용\n- 같은 내용\n- 같은 내용\n"
        issues = check_duplicate_practical_points(content)
        assert issues == []

    def test_section_ends_at_next_heading(self):
        content = (
            "## 실무 적용 포인트\n- 반복 항목\n" * 3 + "## 다른 섹션\n- 반복 항목\n" * 3
        )
        issues = check_duplicate_practical_points(content)
        # Only counted within the section, not across sections
        assert len(issues) == 1


# ---------------------------------------------------------------------------
# check_practical_points_uniqueness
# ---------------------------------------------------------------------------


class TestCheckPracticalPointsUniqueness:
    """Regression checks for the per-item uniqueness feature.

    The contract enforced here: a multi-section digest post must not render
    every practical-point section as a bare 3-bullet fallback. At least one
    section must expose an item-specific marker — either a ``[label]``
    prefix on the first bullet or a 4th uniqueness bullet.
    """

    def test_flags_when_all_sections_miss_markers(self):
        """Two sections, both raw 3-bullet fallback → regression flagged."""
        content = (
            "#### 실무 적용 포인트\n"
            "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인\n"
            "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검\n"
            "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정\n"
            "\n---\n\n"
            "#### 실무 적용 포인트\n"
            "- 컨테이너 이미지 보안 스캔 및 베이스 이미지 최신화 검토\n"
            "- Docker 환경에서의 네트워크 격리 및 접근 제어 설정 확인\n"
            "- 컨테이너 런타임 보안 모니터링 강화\n"
            "\n---\n"
        )
        issues = check_practical_points_uniqueness(content)
        assert len(issues) == 1
        assert "uniqueness 누락" in issues[0]

    def test_pass_when_label_prefix_present(self):
        """First-bullet ``[label]`` marker present → no regression."""
        content = (
            "#### 실무 적용 포인트\n"
            "- [Docker Buildx CVE] 컨테이너 이미지 보안 스캔 및 베이스 이미지 최신화 검토\n"
            "- Docker 환경에서의 네트워크 격리 및 접근 제어 설정 확인\n"
            "- 컨테이너 런타임 보안 모니터링 강화\n"
            "\n---\n\n"
            "#### 실무 적용 포인트\n"
            "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인\n"
            "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검\n"
            "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정\n"
            "\n---\n"
        )
        issues = check_practical_points_uniqueness(content)
        assert issues == [], f"unexpected issues: {issues}"

    def test_pass_when_fourth_bullet_present(self):
        """A 4th uniqueness bullet is enough evidence the feature is active."""
        content = (
            "#### 실무 적용 포인트\n"
            "- 컨테이너 이미지 보안 스캔 및 베이스 이미지 최신화 검토\n"
            "- Docker 환경에서의 네트워크 격리 및 접근 제어 설정 확인\n"
            "- 컨테이너 런타임 보안 모니터링 강화\n"
            "- Docker Buildx 관련 서드파티·SaaS 의존성 맵 갱신 및 벤더 로그 기록\n"
            "\n---\n\n"
            "#### 실무 적용 포인트\n"
            "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인\n"
            "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검\n"
            "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정\n"
            "- Kubernetes RBAC 사례를 내부 런북·체크리스트에 기록\n"
            "\n---\n"
        )
        issues = check_practical_points_uniqueness(content)
        assert issues == []

    def test_ignored_for_single_section_post(self):
        """Single practical-point sections are too ambiguous to flag."""
        content = (
            "#### 실무 적용 포인트\n"
            "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인\n"
            "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검\n"
            "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정\n"
            "\n---\n"
        )
        issues = check_practical_points_uniqueness(content)
        assert issues == []

    def test_partial_coverage_does_not_flag(self):
        """Mixed content (one section has marker, one doesn't) is tolerated.

        The checker only fires when ALL sections miss the marker, so a
        legitimate ``None``-item fallback mixed with real-item sections
        does not produce a false positive.
        """
        content = (
            "#### 실무 적용 포인트\n"
            "- [Docker Buildx] 컨테이너 이미지 보안 스캔 및 베이스 이미지 최신화 검토\n"
            "- Docker 환경에서의 네트워크 격리 및 접근 제어 설정 확인\n"
            "- 컨테이너 런타임 보안 모니터링 강화\n"
            "\n---\n\n"
            "#### 실무 적용 포인트\n"
            "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인\n"
            "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검\n"
            "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정\n"
            "\n---\n"
        )
        issues = check_practical_points_uniqueness(content)
        assert issues == []


# ---------------------------------------------------------------------------
# check_image_exists (filesystem)
# ---------------------------------------------------------------------------


class TestCheckImageExists:
    def test_existing_svg_found(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        (images_dir / "test.svg").write_text("<svg></svg>")
        import scripts.check_posts as cp

        monkeypatch.setattr(cp, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(cp, "IMAGES_DIR", images_dir)
        exists, path = check_image_exists("/assets/images/test.svg")
        assert exists is True
        assert path.name == "test.svg"

    def test_missing_image_returns_false(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        import scripts.check_posts as cp

        monkeypatch.setattr(cp, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(cp, "IMAGES_DIR", images_dir)
        exists, path = check_image_exists("/assets/images/nonexistent.svg")
        assert exists is False

    def test_empty_path_returns_false(self):
        exists, path = check_image_exists("")
        assert exists is False
        assert path is None

    def test_relative_path_resolved(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        (images_dir / "relative.png").write_text("PNG")
        import scripts.check_posts as cp

        monkeypatch.setattr(cp, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(cp, "IMAGES_DIR", images_dir)
        exists, _ = check_image_exists("assets/images/relative.png")
        assert exists is True

    def test_bare_filename_uses_images_dir(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        (images_dir / "bare.svg").write_text("<svg/>")
        import scripts.check_posts as cp

        monkeypatch.setattr(cp, "PROJECT_ROOT", tmp_path)
        monkeypatch.setattr(cp, "IMAGES_DIR", images_dir)
        exists, _ = check_image_exists("bare.svg")
        assert exists is True


# ---------------------------------------------------------------------------
# check_image_files (filesystem)
# ---------------------------------------------------------------------------


class TestCheckImageFiles:
    def _make_post(self, tmp_path, front_matter_image, body="", images_dir=None):
        if images_dir is None:
            images_dir = tmp_path / "assets" / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

        import unittest.mock as mock

        import scripts.check_posts as cp

        with (
            mock.patch.object(cp, "PROJECT_ROOT", tmp_path),
            mock.patch.object(cp, "IMAGES_DIR", images_dir),
        ):
            post_file = tmp_path / "test_post.md"
            content = f"---\ntitle: Test\nimage: {front_matter_image}\n---\n{body}"
            post_file.write_text(content, encoding="utf-8")
            fm = {"image": front_matter_image}
            return check_image_files(post_file, fm)

    def test_no_issues_when_image_exists(self, tmp_path):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        (images_dir / "hero.svg").write_text("<svg/>")
        issues = self._make_post(
            tmp_path, "/assets/images/hero.svg", images_dir=images_dir
        )
        assert issues == []

    def test_missing_main_image_reported(self, tmp_path):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        issues = self._make_post(
            tmp_path, "/assets/images/missing.svg", images_dir=images_dir
        )
        assert any("Main image file not found" in i for i in issues)

    def test_missing_body_image_reported(self, tmp_path):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        (images_dir / "hero.svg").write_text("<svg/>")
        body = "![diagram](/assets/images/diagram.png)"
        import unittest.mock as mock

        import scripts.check_posts as cp

        with (
            mock.patch.object(cp, "PROJECT_ROOT", tmp_path),
            mock.patch.object(cp, "IMAGES_DIR", images_dir),
        ):
            post_file = tmp_path / "test.md"
            post_file.write_text(
                f"---\ntitle: T\nimage: /assets/images/hero.svg\n---\n{body}"
            )
            issues = check_image_files(post_file, {"image": "/assets/images/hero.svg"})
        assert any("Image file not found" in i for i in issues)

    def test_html_img_tag_checked(self, tmp_path):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        (images_dir / "hero.svg").write_text("<svg/>")
        body = '<img src="/assets/images/photo.jpg" alt="photo">'
        import unittest.mock as mock

        import scripts.check_posts as cp

        with (
            mock.patch.object(cp, "PROJECT_ROOT", tmp_path),
            mock.patch.object(cp, "IMAGES_DIR", images_dir),
        ):
            post_file = tmp_path / "test.md"
            post_file.write_text(
                f"---\ntitle: T\nimage: /assets/images/hero.svg\n---\n{body}"
            )
            issues = check_image_files(post_file, {"image": "/assets/images/hero.svg"})
        assert any("Image file not found" in i for i in issues)


# ---------------------------------------------------------------------------
# check_svg_text_density (filesystem)
# ---------------------------------------------------------------------------


class TestCheckSvgTextDensity:
    def _make_svg_and_check(self, tmp_path, svg_content, image_name="test.svg"):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        (images_dir / image_name).write_text(svg_content, encoding="utf-8")
        import unittest.mock as mock

        import scripts.check_posts as cp

        with (
            mock.patch.object(cp, "PROJECT_ROOT", tmp_path),
            mock.patch.object(cp, "IMAGES_DIR", images_dir),
        ):
            fm = {"image": f"/assets/images/{image_name}"}
            return check_svg_text_density(fm)

    def test_clean_svg_no_issues(self, tmp_path):
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><text>Hello</text><text>World</text></svg>'
        issues = self._make_svg_and_check(tmp_path, svg)
        assert issues == []

    def test_too_many_text_nodes_flagged(self, tmp_path):
        # Threshold was raised to 40 nodes in commit 130a12d0. Use 45 to trip it.
        texts = "".join(f"<text>Node {i}</text>" for i in range(45))
        svg = f'<svg xmlns="http://www.w3.org/2000/svg">{texts}</svg>'
        issues = self._make_svg_and_check(tmp_path, svg)
        assert any("text nodes" in i for i in issues)

    def test_too_many_chars_flagged(self, tmp_path):
        # Threshold was raised to 800 chars in commit 130a12d0. Use 900 to trip it.
        long_text = "A" * 900
        svg = f'<svg xmlns="http://www.w3.org/2000/svg"><text>{long_text}</text></svg>'
        issues = self._make_svg_and_check(tmp_path, svg)
        assert any("too much text" in i for i in issues)

    def test_repeated_labels_flagged(self, tmp_path):
        labels = "<text>security</text>" * 6
        svg = f'<svg xmlns="http://www.w3.org/2000/svg">{labels}</svg>'
        issues = self._make_svg_and_check(tmp_path, svg)
        assert any("repeated label" in i for i in issues)

    def test_invalid_xml_returns_warning(self, tmp_path):
        issues = self._make_svg_and_check(tmp_path, "<svg><not closed")
        assert any("Invalid SVG XML" in i for i in issues)

    def test_non_svg_image_skipped(self, tmp_path):
        import unittest.mock as mock

        import scripts.check_posts as cp

        with mock.patch.object(cp, "PROJECT_ROOT", tmp_path):
            fm = {"image": "/assets/images/photo.png"}
            issues = check_svg_text_density(fm)
        assert issues == []

    def test_missing_svg_returns_empty(self, tmp_path):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        import unittest.mock as mock

        import scripts.check_posts as cp

        with (
            mock.patch.object(cp, "PROJECT_ROOT", tmp_path),
            mock.patch.object(cp, "IMAGES_DIR", images_dir),
        ):
            fm = {"image": "/assets/images/missing.svg"}
            issues = check_svg_text_density(fm)
        assert issues == []

    def test_no_truncated_text_in_svg(self, tmp_path):
        """SVG text 내 '...'로 끝나는 잘린 텍스트가 없어야 함"""
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><text>Cloud Security Course 7Batch 4Week: AWS Vulnerabi...</text></svg>'
        issues = self._make_svg_and_check(tmp_path, svg)
        assert any("truncat" in i.lower() or "..." in i for i in issues)

    def test_clean_text_no_truncation_warning(self, tmp_path):
        """정상 텍스트에는 잘림 경고가 없어야 함"""
        svg = '<svg xmlns="http://www.w3.org/2000/svg"><text>Cloud Security Course</text></svg>'
        issues = self._make_svg_and_check(tmp_path, svg)
        assert not any("truncat" in i.lower() for i in issues)
