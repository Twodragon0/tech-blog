#!/usr/bin/env python3
"""Rasterize SVG cover images that lack an _og.png companion.

Idempotent — skips covers whose _og.png already exists. Designed to run
in build.sh between favicon generation and backfill_og_modern_variants.py
so the modern-variants hook then derives _og.{webp,avif} from the fresh
PNGs in the same build.

Backend cascade (first available wins):
  1. `rsvg-convert` CLI (librsvg) — preferred. Local dev usually has it
     via Homebrew (`brew install librsvg`). CI runners install with
     `apt-get install -y librsvg2-bin` (Debian/Ubuntu).
  2. `cairosvg` Python — works when system libcairo is available.
  3. Soft-fail with a warning and zero exit. The build keeps going on
     thin runtimes (e.g. Vercel without librsvg) — the only consequence
     is that SVG-only posts ship without an _og.png that build, and the
     <picture> in _layouts/post.html falls through to the SVG via the
     existing `is-svg-image` class hook (PR #348).

"Cover" definition: an SVG referenced by `image:` in a post's front
matter. This is intentionally narrower than just "any SVG without an
_og.png" — the repo also ships dozens of inline diagram SVGs used in
post bodies (devsecops-learning-path, EC2_G7e_GPU_Architecture, etc.)
that should NOT get an _og.png companion.

Output dimensions are 1200×630 — matches Open Graph spec, the SVG cover
viewBox we ship for L20 Hero+2-Card, and what scripts/regenerate_og_images.py
already uses, so downstream PNG → AVIF/WebP encodings stay consistent.

Exit codes:
  0  success or no work to do
  1  one or more conversions raised an exception (other covers still
     produced)
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = REPO_ROOT / "assets" / "images"
POSTS_DIR = REPO_ROOT / "_posts"

OG_WIDTH = 1200
OG_HEIGHT = 630

# Match `image: /assets/images/foo.svg` (with or without surrounding quotes)
# as a top-level YAML scalar in the first ~3000 bytes of a post.
_IMAGE_FRONTMATTER_RE = re.compile(
    r"^image:\s*['\"]?(?P<path>[^\s'\"]+\.svg)['\"]?\s*$",
    re.MULTILINE,
)


def _cover_svgs_from_frontmatter() -> set[Path]:
    """Collect every SVG referenced as `image:` in any post's front matter.

    This is the authoritative cover set — anything else under
    assets/images/*.svg is an inline diagram or section asset and must
    NOT receive an _og.png companion.
    """
    covers: set[Path] = set()
    if not POSTS_DIR.is_dir():
        return covers
    for post in POSTS_DIR.glob("*.md"):
        try:
            head = post.read_text(errors="replace")[:3000]
        except OSError:
            continue
        m = _IMAGE_FRONTMATTER_RE.search(head)
        if not m:
            continue
        # Front-matter paths are site-absolute (start with /); resolve
        # relative to repo root.
        rel = m.group("path").lstrip("/")
        covers.add(REPO_ROOT / rel)
    return covers


def _candidates() -> list[Path]:
    """Return SVG covers that exist on disk but lack an _og.png companion."""
    out = []
    for svg in sorted(_cover_svgs_from_frontmatter()):
        if not svg.is_file():
            continue  # broken front-matter reference; not our problem
        png = IMG_DIR / f"{svg.stem}_og.png"
        if not png.exists():
            out.append(svg)
    return out


def _convert_via_rsvg(svg: Path, png: Path) -> None:
    subprocess.run(
        [
            "rsvg-convert",
            "-w", str(OG_WIDTH),
            "-h", str(OG_HEIGHT),
            "-o", str(png),
            str(svg),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _convert_via_cairosvg(svg: Path, png: Path) -> None:
    import cairosvg  # imported lazily so missing libcairo is a soft fail
    cairosvg.svg2png(
        url=str(svg),
        write_to=str(png),
        output_width=OG_WIDTH,
        output_height=OG_HEIGHT,
    )


def _pick_backend(force: str | None = None):
    """Return (backend_name, convert_callable) for the requested backend.

    Parameters
    ----------
    force:
        ``None`` or ``"auto"``  — existing cascade: rsvg-convert → cairosvg
                                  → (None, None) soft-fail.
        ``"rsvg-convert"``       — only try rsvg; hard-fail (SystemExit 1) if
                                   rsvg-convert is not on PATH.
        ``"cairosvg"``           — only try cairosvg; hard-fail (SystemExit 1)
                                   if the import fails.
    """
    if force in (None, "auto"):
        # Original cascade — soft-fail when neither is available.
        if shutil.which("rsvg-convert"):
            return "rsvg-convert", _convert_via_rsvg
        try:
            import cairosvg  # noqa: F401  — probe only
            return "cairosvg", _convert_via_cairosvg
        except Exception:  # noqa: BLE001 — libcairo missing is the common case
            return None, None

    if force == "rsvg-convert":
        if not shutil.which("rsvg-convert"):
            print(
                "ERROR: --backend rsvg-convert requested but rsvg-convert is not "
                "on PATH. Install librsvg2-bin (apt) or librsvg (brew).",
                file=sys.stderr,
            )
            raise SystemExit(1)
        return "rsvg-convert", _convert_via_rsvg

    if force == "cairosvg":
        try:
            import cairosvg  # noqa: F401  — probe only
            return "cairosvg", _convert_via_cairosvg
        except Exception as exc:  # noqa: BLE001
            print(
                f"ERROR: --backend cairosvg requested but import failed: {exc}. "
                "Install cairosvg (pip) and ensure libcairo is available.",
                file=sys.stderr,
            )
            raise SystemExit(1)

    # Should never reach here; argparse choices= guards this.
    raise ValueError(f"Unknown backend: {force!r}")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rasterize SVG cover images to _og.png companions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "rsvg-convert", "cairosvg"],
        default="auto",
        help=(
            "Rasterization backend to use. "
            "'auto' (default) tries rsvg-convert then cairosvg and soft-fails "
            "if neither is available. "
            "'rsvg-convert' and 'cairosvg' force that backend and exit 1 if "
            "it is unavailable."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    force = None if args.backend == "auto" else args.backend

    if not IMG_DIR.is_dir():
        print(f"ERROR: {IMG_DIR} not found", file=sys.stderr)
        return 1

    candidates = _candidates()
    if not candidates:
        print("SVG covers: 0 missing _og.png (nothing to do)")
        return 0

    backend, convert = _pick_backend(force=force)
    if backend is None:
        print(
            f"WARN: rsvg-convert and cairosvg both unavailable — "
            f"skipping SVG → PNG rasterization for {len(candidates)} cover(s). "
            f"Install librsvg2-bin (apt) / librsvg (brew) to enable. "
            f"Posts will fall through to <img src=\"...svg\"> via the "
            f"is-svg-image hero class hook."
        )
        return 0

    generated = errors = 0
    for svg in candidates:
        png = IMG_DIR / f"{svg.stem}_og.png"
        try:
            convert(svg, png)
            generated += 1
        except subprocess.CalledProcessError as e:
            errors += 1
            stderr = (e.stderr or "").strip().splitlines()
            tail = stderr[-1] if stderr else "(no stderr)"
            print(f"ERROR: {svg.name}: {tail}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            errors += 1
            print(f"ERROR: {svg.name}: {e}", file=sys.stderr)

    print(
        f"SVG → PNG rasterization via {backend}: "
        f"candidates={len(candidates)} generated={generated} errors={errors}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
