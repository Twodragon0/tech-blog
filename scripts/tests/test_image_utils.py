#!/usr/bin/env python3
"""scripts/lib/image_utils.py 단위 테스트."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.lib.image_utils import (
    ImageIssue,
    check_image_exists,
    check_image_references,
    extract_image_paths,
    has_korean,
    image_exists,
    iter_image_files,
    normalize_image_path,
)

# ---------------------------------------------------------------------------
# has_korean
# ---------------------------------------------------------------------------


def test_has_korean_true_for_korean():
    assert has_korean("보안_다이어그램.svg") is True


def test_has_korean_false_for_english():
    assert has_korean("2025-01-01-architecture.svg") is False


def test_has_korean_false_for_empty():
    assert has_korean("") is False


def test_has_korean_false_for_none_safe():
    # None이 들어와도 터지지 않아야 함 (안전한 기본값)
    assert has_korean(None) is False  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# extract_image_paths
# ---------------------------------------------------------------------------


def test_extract_front_matter_image():
    content = "---\nimage: /assets/images/2025-01-01-diagram.svg\n---\n"
    assert "2025-01-01-diagram.svg" in extract_image_paths(content)


def test_extract_markdown_image():
    assert "chart.png" in extract_image_paths("![alt](/assets/images/chart.png)")


def test_extract_html_img():
    content = '<img src="/assets/images/logo.webp" alt="logo">'
    assert "logo.webp" in extract_image_paths(content)


def test_extract_relative_url_filter():
    content = "![img]({{ '/assets/images/banner.svg' | relative_url }})"
    assert "banner.svg" in extract_image_paths(content)


def test_extract_deduplicates():
    content = (
        "---\nimage: /assets/images/same.svg\n---\n![img](/assets/images/same.svg)"
    )
    assert extract_image_paths(content).count("same.svg") == 1


def test_extract_returns_empty_for_no_images():
    assert extract_image_paths("---\ntitle: x\n---\n\nJust text.") == []


def test_extract_handles_nested_assets_images_prefix():
    # site relative 경로 프리픽스 케이스
    content = "![x](assets/images/nested/thing.png)"
    assert "nested/thing.png" in extract_image_paths(content)


def test_extract_ignores_external_urls():
    # 외부 URL은 결과에 포함되지 않아야 함
    content = "![remote](https://example.com/img.png)"
    assert extract_image_paths(content) == []


# ---------------------------------------------------------------------------
# normalize_image_path / image_exists / check_image_exists
# ---------------------------------------------------------------------------


def test_normalize_absolute_assets_path(tmp_path):
    result = normalize_image_path(
        "/assets/images/foo.svg", project_root=tmp_path, images_dir=tmp_path / "assets/images"
    )
    assert result == tmp_path / "assets" / "images" / "foo.svg"


def test_normalize_relative_assets_path(tmp_path):
    result = normalize_image_path(
        "assets/images/foo.svg", project_root=tmp_path, images_dir=tmp_path / "assets/images"
    )
    assert result == tmp_path / "assets" / "images" / "foo.svg"


def test_normalize_bare_filename(tmp_path):
    images = tmp_path / "assets" / "images"
    result = normalize_image_path("foo.svg", project_root=tmp_path, images_dir=images)
    assert result == images / "foo.svg"


def test_image_exists_true_when_file_present(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    (images / "ok.svg").write_text("<svg/>")
    assert image_exists("/assets/images/ok.svg", project_root=tmp_path, images_dir=images)


def test_image_exists_false_for_missing(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    assert not image_exists(
        "/assets/images/missing.svg", project_root=tmp_path, images_dir=images
    )


def test_image_exists_false_for_empty_string():
    assert not image_exists("")


def test_check_image_exists_returns_none_for_empty():
    ok, resolved = check_image_exists("")
    assert ok is False and resolved is None


def test_check_image_exists_tuple_for_present_file(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    (images / "present.svg").write_text("<svg/>")
    ok, resolved = check_image_exists(
        "/assets/images/present.svg", project_root=tmp_path, images_dir=images
    )
    assert ok is True
    assert resolved == images / "present.svg"


# ---------------------------------------------------------------------------
# check_image_references
# ---------------------------------------------------------------------------


def test_check_image_references_flags_missing_and_korean(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    post = tmp_path / "_posts" / "2025-01-01-demo.md"
    post.parent.mkdir(parents=True)
    post.write_text(
        "---\ntitle: Test\n---\n\n![x](/assets/images/한글.svg)\n",
        encoding="utf-8",
    )
    issues = check_image_references(post, project_root=tmp_path, images_dir=images)
    reasons = {i.reason for i in issues}
    assert "korean_filename" in reasons
    assert "missing" in reasons


def test_check_image_references_clean_post(tmp_path):
    images = tmp_path / "assets" / "images"
    images.mkdir(parents=True)
    (images / "ok.svg").write_text("<svg/>")
    post = tmp_path / "post.md"
    post.write_text(
        "---\nimage: /assets/images/ok.svg\n---\nBody.\n", encoding="utf-8"
    )
    assert check_image_references(post, project_root=tmp_path, images_dir=images) == []


def test_check_image_references_read_error(tmp_path):
    missing = tmp_path / "ghost.md"
    issues = check_image_references(missing, project_root=tmp_path)
    assert len(issues) == 1 and issues[0].reason.startswith("read_error")


# ---------------------------------------------------------------------------
# iter_image_files
# ---------------------------------------------------------------------------


def test_iter_image_files_filters_by_extension(tmp_path):
    (tmp_path / "a.svg").write_text("<svg/>")
    (tmp_path / "b.txt").write_text("text")
    (tmp_path / "c.png").write_bytes(b"\x89PNG")
    files = {p.name for p in iter_image_files(tmp_path)}
    assert files == {"a.svg", "c.png"}


def test_image_issue_is_hashable():
    # dataclass(frozen=True) 덕분에 set/dict key로 사용 가능
    issue = ImageIssue(post=Path("a.md"), image="x.svg", reason="missing")
    assert {issue} == {issue}


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
