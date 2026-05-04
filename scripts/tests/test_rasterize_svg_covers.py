"""Tests for scripts/build/rasterize_svg_covers.py.

The script must:
  1. Treat as a "cover" only an SVG that some post references via
     `image:` in its front matter — never an inline diagram SVG.
  2. Skip when the _og.png companion already exists (idempotent).
  3. Soft-fail when no rasterization backend is available, so the
     build.sh hook keeps the deploy moving on Vercel-style runtimes
     that lack librsvg + system libcairo.
  4. --backend flag forces a specific tier (rsvg-convert, cairosvg, auto)
     and hard-fails (exit 1) when the forced backend is unavailable.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def _make_cover_post(root: Path, stem: str) -> Path:
    """Write a minimal post with an SVG cover and return the SVG path."""
    posts = root / "_posts"
    images = root / "assets" / "images"
    posts.mkdir(parents=True, exist_ok=True)
    images.mkdir(parents=True, exist_ok=True)
    (posts / f"2026-05-01-{stem}.md").write_text(
        f"---\nlayout: post\ntitle: {stem}\n"
        f"image: /assets/images/{stem}.svg\n---\n"
    )
    svg = images / f"{stem}.svg"
    svg.write_text("<svg xmlns='http://www.w3.org/2000/svg'><rect width='1' height='1'/></svg>")
    return svg


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

        # Pretend neither backend is installed (force=None → auto cascade)
        monkeypatch.setattr(module, "_pick_backend", lambda force=None: (None, None))

        rc = module.main([])
        out = capsys.readouterr().out

        assert rc == 0, "must soft-fail so build.sh doesn't abort the deploy"
        assert "WARN" in out
        assert "cold.svg" not in out  # don't dump the candidate list — just the count
        assert "1 cover" in out or "1 cover(s)" in out


class TestNoWorkPath:
    """Steady-state: nothing missing → no backend probe needed."""

    def test_main_returns_zero_when_nothing_to_do(self, rasterize_module, capsys):
        module, _ = rasterize_module
        rc = module.main([])
        out = capsys.readouterr().out
        assert rc == 0
        assert "nothing to do" in out


# ---------------------------------------------------------------------------
# New tests for --backend flag
# ---------------------------------------------------------------------------


class TestPickBackendAuto:
    """_pick_backend(force=None) / force='auto' — cascade behaviour."""

    def test_auto_picks_rsvg_when_available(self, rasterize_module, monkeypatch):
        """Test 1: auto with rsvg available → picks rsvg."""
        module, _ = rasterize_module
        monkeypatch.setattr(module.shutil, "which", lambda name: "/usr/bin/rsvg-convert" if name == "rsvg-convert" else None)
        name, fn = module._pick_backend(force=None)
        assert name == "rsvg-convert"
        assert fn is module._convert_via_rsvg

    def test_auto_falls_through_to_cairosvg_when_rsvg_missing(
        self, rasterize_module, monkeypatch
    ):
        """Test 2: auto with rsvg unavailable, cairosvg available → picks cairosvg."""
        module, _ = rasterize_module
        monkeypatch.setattr(module.shutil, "which", lambda name: None)

        fake_cairosvg = MagicMock()
        with patch.dict(sys.modules, {"cairosvg": fake_cairosvg}):
            name, fn = module._pick_backend(force=None)

        assert name == "cairosvg"
        assert fn is module._convert_via_cairosvg

    def test_auto_returns_none_when_both_unavailable(
        self, rasterize_module, monkeypatch
    ):
        """Test 3: auto with both unavailable → soft-fail returns (None, None)."""
        module, _ = rasterize_module
        monkeypatch.setattr(module.shutil, "which", lambda name: None)

        # Ensure cairosvg import fails
        with patch.dict(sys.modules, {"cairosvg": None}):
            # Remove cairosvg from sys.modules to force ImportError
            sys.modules.pop("cairosvg", None)
            name, fn = module._pick_backend(force=None)

        assert name is None
        assert fn is None


class TestPickBackendForced:
    """_pick_backend(force=...) — hard-fail when backend is unavailable."""

    def test_force_rsvg_exits_1_when_rsvg_missing(
        self, rasterize_module, monkeypatch, capsys
    ):
        """Test 4: --backend rsvg-convert with rsvg unavailable → exit 1 with clear stderr."""
        module, _ = rasterize_module
        monkeypatch.setattr(module.shutil, "which", lambda name: None)

        with pytest.raises(SystemExit) as exc_info:
            module._pick_backend(force="rsvg-convert")

        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "rsvg-convert" in err
        assert "ERROR" in err

    def test_force_cairosvg_exits_1_when_import_fails(
        self, rasterize_module, monkeypatch, capsys
    ):
        """Test 5: --backend cairosvg with cairosvg import failing → exit 1 with clear stderr."""
        module, _ = rasterize_module

        # Patch the builtins.__import__ to raise ImportError for cairosvg
        original_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

        def mock_import(name, *args, **kwargs):
            if name == "cairosvg":
                raise ImportError("No module named 'cairosvg'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            # Remove cairosvg from sys.modules cache so import is attempted fresh
            sys.modules.pop("cairosvg", None)
            with pytest.raises(SystemExit) as exc_info:
                module._pick_backend(force="cairosvg")

        assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "cairosvg" in err
        assert "ERROR" in err

    def test_force_rsvg_succeeds_and_returns_callable(
        self, rasterize_module, monkeypatch
    ):
        """Test 6: --backend rsvg-convert with rsvg available → returns correct callable."""
        module, _ = rasterize_module
        monkeypatch.setattr(
            module.shutil, "which", lambda name: "/usr/bin/rsvg-convert" if name == "rsvg-convert" else None
        )

        name, fn = module._pick_backend(force="rsvg-convert")

        assert name == "rsvg-convert"
        assert fn is module._convert_via_rsvg


class TestBackendFlagArgparse:
    """Argparse integration — --backend flag is wired end-to-end."""

    def test_invalid_backend_exits_2(self, rasterize_module):
        """Test 7: invalid --backend foo → argparse error exit 2."""
        module, _ = rasterize_module

        with pytest.raises(SystemExit) as exc_info:
            module._parse_args(["--backend", "foo"])

        assert exc_info.value.code == 2

    def test_help_flag_shows_backend_choices(self, rasterize_module, capsys):
        """--help output includes the --backend flag and its choices."""
        module, _ = rasterize_module

        with pytest.raises(SystemExit):
            module._parse_args(["--help"])

        out = capsys.readouterr().out
        assert "--backend" in out
        assert "rsvg-convert" in out
        assert "cairosvg" in out

    def test_default_backend_is_auto(self, rasterize_module):
        """Passing no flags gives backend='auto'."""
        module, _ = rasterize_module
        args = module._parse_args([])
        assert args.backend == "auto"

    def test_main_with_backend_rsvg_and_no_rsvg_exits_1(
        self, rasterize_module, monkeypatch, capsys
    ):
        """End-to-end: main(--backend rsvg-convert) with rsvg absent → exit 1."""
        module, root = rasterize_module
        _make_cover_post(root, "cover-a")
        monkeypatch.setattr(module.shutil, "which", lambda name: None)

        with pytest.raises(SystemExit) as exc_info:
            module.main(["--backend", "rsvg-convert"])

        assert exc_info.value.code == 1

    def test_main_with_backend_auto_and_rsvg_available_converts(
        self, rasterize_module, monkeypatch, capsys, tmp_path
    ):
        """End-to-end: main(--backend auto) with rsvg available → calls convert fn."""
        module, root = rasterize_module
        svg = _make_cover_post(root, "cover-b")

        monkeypatch.setattr(
            module.shutil, "which",
            lambda name: "/usr/bin/rsvg-convert" if name == "rsvg-convert" else None,
        )

        # Mock the convert function so we don't actually invoke rsvg-convert
        converted_calls = []

        def fake_convert(s, p):
            converted_calls.append((s, p))
            p.write_bytes(b"\x89PNG\r\n\x1a\n")  # minimal PNG header

        monkeypatch.setattr(module, "_convert_via_rsvg", fake_convert)

        # Re-patch _pick_backend to use the fake converter
        orig_pick = module._pick_backend

        def patched_pick(force=None):
            name, fn = orig_pick(force=force)
            if name == "rsvg-convert":
                return name, fake_convert
            return name, fn

        monkeypatch.setattr(module, "_pick_backend", patched_pick)

        rc = module.main(["--backend", "auto"])
        out = capsys.readouterr().out

        assert rc == 0
        assert len(converted_calls) == 1
        assert converted_calls[0][0] == svg
        assert "rsvg-convert" in out
