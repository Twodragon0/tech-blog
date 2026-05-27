"""Unit tests for scripts/check_spec_slug_consistency.py.

Covers:
- Spec slug matches post image: path exactly → PASS
- Spec slug uppercase, post image lowercase → FAIL (reproducer for the macOS bug)
- Orphan spec (no matching post) → FAIL
- Post has no image: field → FAIL
- Post image points to different basename (rename leftover) → FAIL
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

# Make the scripts/ directory importable.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_spec_slug_consistency import _check_spec, _extract_image, _find_post, _parse_spec  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_spec(tmp_path: Path, name: str, date: str, slug: str) -> Path:
    """Write a minimal digest cover YAML spec and return its Path."""
    spec = tmp_path / "_data" / "digest_covers" / name
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(f"date: '{date}'\nslug: {slug}\n", encoding="utf-8")
    return spec


def _write_post(tmp_path: Path, filename: str, image: str | None) -> Path:
    """Write a minimal Jekyll post with optional image: field."""
    posts = tmp_path / "_posts"
    posts.mkdir(parents=True, exist_ok=True)
    post = posts / filename
    if image is not None:
        front = textwrap.dedent(f"""\
            ---
            layout: post
            title: "Test post"
            date: 2025-01-01 09:00:00 +0900
            image: {image}
            ---
            Body text.
        """)
    else:
        front = textwrap.dedent("""\
            ---
            layout: post
            title: "Test post"
            date: 2025-01-01 09:00:00 +0900
            ---
            Body text.
        """)
    post.write_text(front, encoding="utf-8")
    return post


# ---------------------------------------------------------------------------
# _parse_spec
# ---------------------------------------------------------------------------


class TestParseSpec:
    def test_parses_date_and_slug(self, tmp_path):
        spec = _write_spec(tmp_path, "2025-05-24-Foo_Bar.yml", "2025-05-24", "Foo_Bar")
        date_str, slug = _parse_spec(spec)
        assert date_str == "2025-05-24"
        assert slug == "Foo_Bar"

    def test_missing_slug_returns_none(self, tmp_path):
        spec = tmp_path / "noSlug.yml"
        spec.write_text("date: '2025-01-01'\n", encoding="utf-8")
        date_str, slug = _parse_spec(spec)
        assert date_str is None or slug is None

    def test_missing_date_returns_none(self, tmp_path):
        spec = tmp_path / "noDate.yml"
        spec.write_text("slug: Foo_Bar\n", encoding="utf-8")
        date_str, slug = _parse_spec(spec)
        assert date_str is None or slug is None


# ---------------------------------------------------------------------------
# _extract_image
# ---------------------------------------------------------------------------


class TestExtractImage:
    def test_extracts_image_field(self, tmp_path):
        post = _write_post(tmp_path, "2025-01-01-Foo.md", "/assets/images/2025-01-01-Foo.svg")
        assert _extract_image(post) == "/assets/images/2025-01-01-Foo.svg"

    def test_returns_none_when_no_image_field(self, tmp_path):
        post = _write_post(tmp_path, "2025-01-01-Foo.md", None)
        assert _extract_image(post) is None

    def test_nonexistent_file_returns_none(self, tmp_path):
        fake = tmp_path / "ghost.md"
        assert _extract_image(fake) is None


# ---------------------------------------------------------------------------
# Integration tests via _check_spec (monkeypatching POSTS_DIR)
# ---------------------------------------------------------------------------


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    """Set up a minimal fake repo and patch module-level constants."""
    import check_spec_slug_consistency as m

    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir()
    covers_dir = tmp_path / "_data" / "digest_covers"
    covers_dir.mkdir(parents=True)

    monkeypatch.setattr(m, "REPO", tmp_path)
    monkeypatch.setattr(m, "POSTS_DIR", posts_dir)
    monkeypatch.setattr(m, "DIGEST_COVERS_DIR", covers_dir)

    return tmp_path


class TestCheckSpec:
    # ------------------------------------------------------------------
    # PASS case
    # ------------------------------------------------------------------

    def test_exact_match_passes(self, repo):
        """Spec slug matches post filename and image: field exactly — no violations."""
        date, slug = "2025-05-24", "Amazon_Q_DeveloperAnd_GitHub_Security"
        spec = _write_spec(repo, f"{date}-{slug}.yml", date, slug)
        _write_post(
            repo,
            f"{date}-{slug}.md",
            f"/assets/images/{date}-{slug}.svg",
        )
        violations = _check_spec(spec)
        assert violations == [], f"Expected no violations, got: {violations}"

    # ------------------------------------------------------------------
    # FAIL: uppercase slug vs lowercase image (the macOS bug reproducer)
    # ------------------------------------------------------------------

    def test_uppercase_slug_lowercase_image_fails(self, repo):
        """Spec slug has uppercase letters; post image: uses lowercase → FAIL.

        This is the exact bug class from commit ebff34a1:
        spec slug 'DeveloperAnd' vs post image 'developerand'.
        """
        date = "2025-05-24"
        slug = "Amazon_Q_DeveloperAnd_GitHub_Security"
        slug_lower = "Amazon_Q_Developerand_GitHub_Security"  # macOS drift

        spec = _write_spec(repo, f"{date}-{slug_lower}.yml", date, slug)
        # Post filename uses different casing (the macOS case-insensitive variant)
        _write_post(
            repo,
            f"{date}-{slug}.md",
            f"/assets/images/{date}-{slug_lower}.svg",  # image uses lowercase slug
        )
        violations = _check_spec(spec)
        assert len(violations) == 1
        assert "slug-vs-image-mismatch" in violations[0]
        assert slug in violations[0], "Expected spec slug in violation message"
        assert slug_lower in violations[0], "Expected actual image path in violation message"

    # ------------------------------------------------------------------
    # FAIL: orphan spec (no matching post)
    # ------------------------------------------------------------------

    def test_orphan_spec_fails(self, repo):
        """Spec exists but there is no post with matching date → FAIL."""
        date, slug = "2025-06-01", "Ghost_Post_Never_Written"
        spec = _write_spec(repo, f"{date}-{slug}.yml", date, slug)
        # No post written
        violations = _check_spec(spec)
        assert len(violations) == 1
        assert "orphan-spec" in violations[0]

    # ------------------------------------------------------------------
    # FAIL: post has no image: field
    # ------------------------------------------------------------------

    def test_post_missing_image_field_fails(self, repo):
        """Post exists but has no image: field in front matter → FAIL."""
        date, slug = "2025-07-15", "Post_Without_Image"
        spec = _write_spec(repo, f"{date}-{slug}.yml", date, slug)
        _write_post(repo, f"{date}-{slug}.md", None)  # no image field
        violations = _check_spec(spec)
        assert len(violations) == 1
        assert "missing-image" in violations[0]

    # ------------------------------------------------------------------
    # FAIL: post image points to different basename (rename leftover)
    # ------------------------------------------------------------------

    def test_renamed_image_leftover_fails(self, repo):
        """Post image: points to an old/different basename — slug mismatch → FAIL."""
        date, slug = "2025-08-20", "New_Canonical_Slug"
        old_slug = "Old_Short_Name"  # renamed leftover
        spec = _write_spec(repo, f"{date}-{slug}.yml", date, slug)
        _write_post(
            repo,
            f"{date}-{slug}.md",
            f"/assets/images/{date}-{old_slug}.svg",  # stale image path
        )
        violations = _check_spec(spec)
        assert len(violations) == 1
        assert "slug-vs-image-mismatch" in violations[0]
        assert old_slug in violations[0], "Old slug should appear in actual= part"
