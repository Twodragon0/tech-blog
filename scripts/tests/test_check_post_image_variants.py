#!/usr/bin/env python3
"""Unit tests for check_post_image_variants.py."""

import sys
from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml")

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import scripts.check_post_image_variants as m


# ---------------------------------------------------------------------------
# _extract_image_field
# ---------------------------------------------------------------------------


class TestExtractImageField:
    def test_present(self, tmp_path):
        p = tmp_path / "post.md"
        p.write_text("---\nimage: /assets/images/foo.svg\n---\nBody\n")
        assert m._extract_image_field(p) == "/assets/images/foo.svg"

    def test_absent(self, tmp_path):
        p = tmp_path / "post.md"
        p.write_text("---\ntitle: No image here\n---\nBody\n")
        assert m._extract_image_field(p) is None

    def test_no_frontmatter(self, tmp_path):
        p = tmp_path / "post.md"
        p.write_text("Just plain content without front matter delimiters.\n")
        assert m._extract_image_field(p) is None

    def test_malformed_yaml(self, tmp_path):
        p = tmp_path / "post.md"
        p.write_text("---\nimage: [unclosed bracket\n---\nBody\n")
        # Must not raise; must return None gracefully
        assert m._extract_image_field(p) is None


# ---------------------------------------------------------------------------
# _base_stem
# ---------------------------------------------------------------------------


class TestBaseStem:
    def test_svg(self):
        assert m._base_stem("/assets/images/2026-05-06-Foo.svg") == "2026-05-06-Foo"

    def test_og_png(self):
        assert m._base_stem("/assets/images/2026-05-06-Foo_og.png") == "2026-05-06-Foo"

    def test_plain_png(self):
        assert m._base_stem("/assets/images/2026-05-06-Foo.png") == "2026-05-06-Foo"


# ---------------------------------------------------------------------------
# check_post  (filesystem-isolated via monkeypatch)
# ---------------------------------------------------------------------------


def _make_post(tmp_path: Path, image_field: str) -> Path:
    p = tmp_path / "2026-05-06-Test.md"
    p.write_text(
        f"---\nlayout: post\ntitle: Test\nimage: {image_field}\n---\nBody\n"
    )
    return p


class TestCheckPost:
    def test_primary_present_via_og_png(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        stem = "2026-05-06-Test"
        (images_dir / f"{stem}_og.png").write_bytes(b"PNG")
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)

        post = _make_post(tmp_path, f"/assets/images/{stem}.svg")
        result = m.check_post(post)
        assert result is not None
        assert result.missing_primary == []

    def test_primary_present_via_literal_svg(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        stem = "2026-05-06-Test"
        # Only the literal .svg file exists; no _og.png
        (images_dir / f"{stem}.svg").write_text("<svg/>")
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)

        post = _make_post(tmp_path, f"/assets/images/{stem}.svg")
        result = m.check_post(post)
        assert result is not None
        assert result.missing_primary == []

    def test_primary_missing(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        stem = "2026-05-06-Test"
        # No files at all in images_dir
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)

        post = _make_post(tmp_path, f"/assets/images/{stem}.svg")
        result = m.check_post(post)
        assert result is not None
        assert len(result.missing_primary) > 0

    def test_secondary_missing(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        stem = "2026-05-06-Test"
        # Primary present, no modern/card variants
        (images_dir / f"{stem}_og.png").write_bytes(b"PNG")
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)

        post = _make_post(tmp_path, f"/assets/images/{stem}.svg")
        result = m.check_post(post)
        assert result is not None
        assert result.missing_primary == []
        missing_names = [Path(p).name for p in result.missing_secondary]
        assert f"{stem}_og.avif" in missing_names
        assert f"{stem}_og.webp" in missing_names
        assert f"{stem}_card.avif" in missing_names
        assert f"{stem}_card.webp" in missing_names


# ---------------------------------------------------------------------------
# run_check
# ---------------------------------------------------------------------------


def _make_full_post(tmp_path: Path, images_dir: Path, stem: str) -> Path:
    """Create a post and all required image variants under images_dir."""
    post = tmp_path / f"{stem}.md"
    post.write_text(
        f"---\nlayout: post\ntitle: Full\nimage: /assets/images/{stem}.svg\n---\nBody\n"
    )
    for suffix in ("_og.png", "_og.avif", "_og.webp", "_card.avif", "_card.webp"):
        (images_dir / f"{stem}{suffix}").write_bytes(b"data")
    return post


class TestRunCheck:
    def test_passes_when_clean(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)

        post = _make_full_post(tmp_path, images_dir, "2026-05-06-Clean")
        assert m.run_check([post]) == 0

    def test_fails_on_primary_missing(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)

        post = _make_post(tmp_path, "/assets/images/2026-05-06-Bad.svg")
        assert m.run_check([post], warn_only=False) == 1

    def test_warn_only_returns_zero_on_failure(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)

        post = _make_post(tmp_path, "/assets/images/2026-05-06-Bad.svg")
        assert m.run_check([post], warn_only=True) == 0


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain:
    def test_skip_env(self, monkeypatch):
        monkeypatch.setenv("SKIP_VARIANT_CHECK", "1")
        assert m.main([]) == 0

    def test_clean_tree(self, tmp_path, monkeypatch):
        images_dir = tmp_path / "assets" / "images"
        images_dir.mkdir(parents=True)
        monkeypatch.setattr(m, "IMAGES_DIR", images_dir)
        monkeypatch.setattr(m, "PROJECT_ROOT", tmp_path)
        monkeypatch.delenv("SKIP_VARIANT_CHECK", raising=False)

        posts_dir = tmp_path / "_posts"
        posts_dir.mkdir()
        _make_full_post(posts_dir, images_dir, "2026-05-06-MainTest")

        assert m.main(["--posts-dir", str(posts_dir)]) == 0
