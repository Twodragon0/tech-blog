"""Tests for scripts/build/rasterize_svg_covers.py.

The script must:
  1. Treat as a "cover" only an SVG that some post references via
     `image:` in its front matter — never an inline diagram SVG.
  2. Skip when the _og.png companion already exists (idempotent).
  3. Soft-fail when no rasterization backend is available, so the
     build.sh hook keeps the deploy moving on Vercel-style runtimes
     that lack librsvg + system libcairo.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "build" / "rasterize_svg_covers.py"


@pytest.fixture
def rasterize_module(tmp_path, monkeypatch):
    """Load rasterize_svg_covers.py with REPO_ROOT pointed at a temp tree."""
    posts = tmp_path / "_posts"
    images = tmp_path / "assets" / "images"
    posts.mkdir(parents=True)
    images.mkdir(parents=True)

    spec = importlib.util.spec_from_file_location("rasterize_svg_covers", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["rasterize_svg_covers"] = module
    spec.loader.exec_module(module)

    monkeypatch.setattr(module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(module, "IMG_DIR", images)
    monkeypatch.setattr(module, "POSTS_DIR", posts)
    return module, tmp_path


class TestCoverDiscovery:
    """Front-matter scan must isolate covers from inline-diagram SVGs."""

    def test_only_svgs_referenced_in_frontmatter_are_covers(
        self, rasterize_module
    ):
        module, root = rasterize_module
        # Post with an SVG cover
        (root / "_posts" / "2026-05-01-foo.md").write_text(
            "---\n"
            "layout: post\n"
            "title: foo\n"
            "image: /assets/images/2026-05-01-foo.svg\n"
            "---\n"
        )
        # Inline diagram SVG (NOT referenced by any image:)
        (root / "assets" / "images" / "2026-05-01-foo.svg").write_text("<svg/>")
        (root / "assets" / "images" / "inline-diagram.svg").write_text("<svg/>")

        covers = module._cover_svgs_from_frontmatter()

        assert {p.name for p in covers} == {"2026-05-01-foo.svg"}
        assert "inline-diagram.svg" not in {p.name for p in covers}

    def test_quoted_frontmatter_paths_are_picked_up(self, rasterize_module):
        module, root = rasterize_module
        (root / "_posts" / "p.md").write_text(
            '---\nimage: "/assets/images/quoted.svg"\n---\n'
        )
        (root / "assets" / "images" / "quoted.svg").write_text("<svg/>")
        covers = module._cover_svgs_from_frontmatter()
        assert {p.name for p in covers} == {"quoted.svg"}

    def test_png_image_does_not_produce_cover(self, rasterize_module):
        module, root = rasterize_module
        (root / "_posts" / "p.md").write_text(
            "---\nimage: /assets/images/already-png.png\n---\n"
        )
        covers = module._cover_svgs_from_frontmatter()
        assert covers == set()

    def test_candidates_excludes_covers_with_existing_png(self, rasterize_module):
        module, root = rasterize_module
        # Cover that already has _og.png — skip
        (root / "_posts" / "p.md").write_text(
            "---\nimage: /assets/images/done.svg\n---\n"
        )
        (root / "assets" / "images" / "done.svg").write_text("<svg/>")
        (root / "assets" / "images" / "done_og.png").write_bytes(b"\x89PNG\r\n")

        # Cover that does not — include
        (root / "_posts" / "q.md").write_text(
            "---\nimage: /assets/images/todo.svg\n---\n"
        )
        (root / "assets" / "images" / "todo.svg").write_text("<svg/>")

        candidate_names = [p.name for p in module._candidates()]
        assert candidate_names == ["todo.svg"]


class TestSoftFailWithoutBackend:
    """Build.sh contract: missing librsvg + cairosvg must NOT fail the build."""

    def test_main_returns_zero_when_no_backend_available(
        self, rasterize_module, monkeypatch, capsys
    ):
        module, root = rasterize_module
        # One real candidate
        (root / "_posts" / "p.md").write_text(
            "---\nimage: /assets/images/cold.svg\n---\n"
        )
        (root / "assets" / "images" / "cold.svg").write_text("<svg/>")

        # Pretend neither backend is installed
        monkeypatch.setattr(module, "_pick_backend", lambda: (None, None))

        rc = module.main()
        out = capsys.readouterr().out

        assert rc == 0, "must soft-fail so build.sh doesn't abort the deploy"
        assert "WARN" in out
        assert "cold.svg" not in out  # don't dump the candidate list — just the count
        assert "1 cover" in out or "1 cover(s)" in out


class TestNoWorkPath:
    """Steady-state: nothing missing → no backend probe needed."""

    def test_main_returns_zero_when_nothing_to_do(self, rasterize_module, capsys):
        module, _ = rasterize_module
        rc = module.main()
        out = capsys.readouterr().out
        assert rc == 0
        assert "nothing to do" in out
