#!/usr/bin/env python3
"""Unit tests for verify_images_unified.py.

Tests cover:
- has_korean: Korean character detection in filenames
- extract_image_paths: image reference extraction from front matter, HTML tags,
  and markdown syntax, including Jekyll relative_url filter stripping
- check_image_exists: file existence logic for absolute and relative paths
- check_image_file: compound validation (exists + has_korean flags)
- extract_post_info: front matter parsing for title, category, image fields
- generate_gemini_command: category-driven command template selection
- process_post_file: integration path (issues collected, missing image detected)
- Edge cases: empty content, no images, Korean filenames, duplicate paths
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from verify_images_unified import (
    check_image_exists,
    check_image_file,
    extract_image_paths,
    extract_post_info,
    generate_gemini_command,
    has_korean,
    process_post_file,
)

# ---------------------------------------------------------------------------
# has_korean
# ---------------------------------------------------------------------------


def test_has_korean_returns_true_for_korean_filename():
    assert has_korean("보안_다이어그램.svg") is True


def test_has_korean_returns_false_for_english_filename():
    assert has_korean("2025-01-01-architecture.svg") is False


def test_has_korean_returns_false_for_empty_string():
    assert has_korean("") is False


def test_has_korean_returns_false_for_mixed_ascii_and_digits():
    assert has_korean("image-123_final.png") is False


def test_has_korean_returns_true_for_single_korean_character():
    assert has_korean("a가b") is True


# ---------------------------------------------------------------------------
# extract_image_paths
# ---------------------------------------------------------------------------


def test_extract_image_paths_finds_front_matter_image():
    content = "---\nimage: /assets/images/2025-01-01-diagram.svg\n---\n"
    paths = extract_image_paths(content)
    assert "2025-01-01-diagram.svg" in paths


def test_extract_image_paths_finds_markdown_image_syntax():
    content = "![alt text](/assets/images/chart.png)"
    paths = extract_image_paths(content)
    assert "chart.png" in paths


def test_extract_image_paths_finds_html_img_tag():
    content = '<img src="/assets/images/logo.webp" alt="logo">'
    paths = extract_image_paths(content)
    assert "logo.webp" in paths


def test_extract_image_paths_strips_relative_url_filter():
    content = "![img]({{ '/assets/images/banner.svg' | relative_url }})"
    paths = extract_image_paths(content)
    assert "banner.svg" in paths


def test_extract_image_paths_returns_empty_list_for_no_images():
    content = "---\ntitle: Post\n---\n\nJust text, no images."
    paths = extract_image_paths(content)
    assert paths == []


def test_extract_image_paths_deduplicates_repeated_references():
    content = (
        "---\nimage: /assets/images/same.svg\n---\n![img](/assets/images/same.svg)"
    )
    paths = extract_image_paths(content)
    assert paths.count("same.svg") == 1


# ---------------------------------------------------------------------------
# check_image_exists
# ---------------------------------------------------------------------------


def test_check_image_exists_returns_false_for_nonexistent_file(tmp_path):
    with patch("verify_images_unified.PROJECT_ROOT", tmp_path):
        exists, path = check_image_exists("/assets/images/missing.svg")
    assert exists is False


def test_check_image_exists_returns_true_for_existing_file(tmp_path):
    img_dir = tmp_path / "assets" / "images"
    img_dir.mkdir(parents=True)
    (img_dir / "present.svg").write_text("<svg/>")
    with patch("verify_images_unified.PROJECT_ROOT", tmp_path):
        with patch("verify_images_unified.IMAGES_DIR", img_dir):
            exists, path = check_image_exists("/assets/images/present.svg")
    assert exists is True


def test_check_image_exists_returns_false_for_empty_path():
    exists, path = check_image_exists("")
    assert exists is False
    assert path is None


# ---------------------------------------------------------------------------
# check_image_file
# ---------------------------------------------------------------------------


def test_check_image_file_flags_korean_filename(tmp_path):
    img_dir = tmp_path / "assets" / "images"
    img_dir.mkdir(parents=True)
    with patch("verify_images_unified.IMAGES_DIR", img_dir):
        result = check_image_file("한글이미지.svg")
    assert result["has_korean"] is True
    assert result["exists"] is False  # file was not created


def test_check_image_file_reports_exists_true_when_file_present(tmp_path):
    img_dir = tmp_path / "assets" / "images"
    img_dir.mkdir(parents=True)
    (img_dir / "photo.png").write_text("fake")
    with patch("verify_images_unified.IMAGES_DIR", img_dir):
        result = check_image_file("photo.png")
    assert result["exists"] is True
    assert result["has_korean"] is False


def test_check_image_file_reports_exists_false_for_missing_file(tmp_path):
    img_dir = tmp_path / "assets" / "images"
    img_dir.mkdir(parents=True)
    with patch("verify_images_unified.IMAGES_DIR", img_dir):
        result = check_image_file("ghost.svg")
    assert result["exists"] is False


# ---------------------------------------------------------------------------
# extract_post_info
# ---------------------------------------------------------------------------


def test_extract_post_info_parses_title_and_image(tmp_path):
    post = tmp_path / "2025-01-01-test.md"
    post.write_text(
        '---\ntitle: "Security Guide"\nimage: /assets/images/sec.svg\n---\nBody.\n',
        encoding="utf-8",
    )
    info = extract_post_info(post)
    assert info["title"] == "Security Guide"
    assert info["image"] == "/assets/images/sec.svg"


def test_extract_post_info_falls_back_to_empty_strings_when_fields_missing(tmp_path):
    post = tmp_path / "2025-01-01-minimal.md"
    post.write_text("---\n---\nBody.\n", encoding="utf-8")
    info = extract_post_info(post)
    assert info["title"] == ""
    assert info["image"] == ""


def test_extract_post_info_prefers_categories_over_category(tmp_path):
    post = tmp_path / "2025-01-01-cat.md"
    post.write_text(
        "---\ncategory: old\ncategories: security\n---\nBody.\n",
        encoding="utf-8",
    )
    info = extract_post_info(post)
    assert info["category"] == "security"


# ---------------------------------------------------------------------------
# generate_gemini_command
# ---------------------------------------------------------------------------


def test_generate_gemini_command_includes_title_in_output():
    info = {"title": "Kubernetes Network Policy", "category": "cloud"}
    cmd = generate_gemini_command(info)
    assert "Kubernetes Network Policy" in cmd


def test_generate_gemini_command_selects_security_template_for_security_category():
    info = {"title": "Zero Trust Architecture", "category": "security"}
    cmd = generate_gemini_command(info)
    assert "security" in cmd.lower()


def test_generate_gemini_command_falls_back_to_cloud_template_for_unknown_category():
    info = {"title": "Some Post", "category": "unknown_category"}
    cmd = generate_gemini_command(info)
    # Falls back to cloud template which mentions AWS
    assert "AWS" in cmd or "gemini" in cmd


# ---------------------------------------------------------------------------
# process_post_file (integration)
# ---------------------------------------------------------------------------


def test_process_post_file_reports_missing_front_matter_image(tmp_path):
    img_dir = tmp_path / "assets" / "images"
    img_dir.mkdir(parents=True)
    post = tmp_path / "2025-01-01-missing-img.md"
    post.write_text(
        "---\ntitle: Test\nimage: /assets/images/nonexistent.svg\n---\nBody.\n",
        encoding="utf-8",
    )
    with patch("verify_images_unified.PROJECT_ROOT", tmp_path):
        with patch("verify_images_unified.IMAGES_DIR", img_dir):
            result = process_post_file(post)
    assert any("메인 이미지를 찾을 수 없습니다" in issue for issue in result["issues"])


def test_process_post_file_reports_korean_image_filename(tmp_path):
    img_dir = tmp_path / "assets" / "images"
    img_dir.mkdir(parents=True)
    post = tmp_path / "2025-01-01-korean.md"
    post.write_text(
        "---\ntitle: Test\n---\n\n![img](/assets/images/한글파일.svg)\n",
        encoding="utf-8",
    )
    with patch("verify_images_unified.IMAGES_DIR", img_dir):
        result = process_post_file(post)
    assert any("한글이 포함" in issue for issue in result["issues"])


def test_process_post_file_returns_no_issues_for_clean_post_with_existing_image(
    tmp_path,
):
    img_dir = tmp_path / "assets" / "images"
    img_dir.mkdir(parents=True)
    (img_dir / "diagram.svg").write_text("<svg/>")
    post = tmp_path / "2025-01-01-ok.md"
    post.write_text(
        "---\ntitle: OK Post\nimage: /assets/images/diagram.svg\n---\nBody.\n",
        encoding="utf-8",
    )
    with patch("verify_images_unified.PROJECT_ROOT", tmp_path):
        with patch("verify_images_unified.IMAGES_DIR", img_dir):
            result = process_post_file(post)
    assert result["issues"] == []


def test_process_post_file_returns_error_issue_for_unreadable_file(tmp_path):
    missing = tmp_path / "ghost.md"
    result = process_post_file(missing)
    assert any("오류 발생" in issue or "Error" in issue for issue in result["issues"])
