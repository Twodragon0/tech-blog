#!/usr/bin/env python3
"""Generate missing `_og.png` variants for every post that has an SVG cover.

Background: ``_includes/head.html`` swaps the post's ``image`` from SVG to a
matching ``.png`` or ``_og.png`` when one of those exists in
``site.static_files``. KakaoTalk and X (Twitter) cannot render SVG previews,
so without a PNG variant the OG meta falls back to ``og-default.png`` and
the cover shown in the share preview is generic.

This script scans ``_posts/*.md`` for posts whose front-matter ``image``
field points to ``/assets/images/<file>.svg`` and emits a sibling
``<file>_og.png`` (1200x630) using ``rsvg-convert`` whenever neither
``<file>.png`` nor ``<file>_og.png`` already exists.

Usage::

    python3 scripts/generate_missing_og_pngs.py            # render all missing
    python3 scripts/generate_missing_og_pngs.py --dry-run  # only report
    python3 scripts/generate_missing_og_pngs.py --force    # re-render even if PNG exists

Requirements: ``rsvg-convert`` (librsvg) on PATH.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS = REPO_ROOT / "_posts"
ASSETS = REPO_ROOT / "assets" / "images"

IMAGE_RE = re.compile(r"^image:\s*(/assets/images/[^\s]+\.svg)\s*$", re.MULTILINE)


def _scan_posts() -> list[tuple[Path, Path]]:
    """Return list of (post_md, svg_path) for posts whose image is an SVG."""
    out: list[tuple[Path, Path]] = []
    for md in sorted(POSTS.glob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")[:4000]
        m = IMAGE_RE.search(text)
        if not m:
            continue
        rel = m.group(1).lstrip("/")
        svg = REPO_ROOT / rel
        if svg.exists() and svg.suffix == ".svg":
            out.append((md, svg))
    return out


def _needs_og_png(svg: Path, force: bool) -> Path | None:
    """Return target PNG path if rendering is required, else None."""
    base = svg.with_suffix("")
    plain_png = base.with_name(base.name + ".png")
    og_png = base.with_name(base.name + "_og.png")
    if force:
        return og_png
    if plain_png.exists() or og_png.exists():
        return None
    return og_png


def _render(svg: Path, png: Path, rsvg: str) -> tuple[Path, bool, str]:
    """Render ``svg`` -> ``png`` at 1200x630. Returns (png, ok, message)."""
    try:
        result = subprocess.run(
            [rsvg, "-w", "1200", "-h", "630", str(svg), "-o", str(png)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return png, False, result.stderr.strip()[:200]
        return png, True, ""
    except subprocess.TimeoutExpired:
        return png, False, "timeout"
    except Exception as exc:  # pragma: no cover - reported per-file
        return png, False, f"{type(exc).__name__}: {exc}"


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true", help="report only, do not render")
    p.add_argument("--force", action="store_true", help="re-render even if a PNG exists")
    p.add_argument("--workers", type=int, default=4, help="parallel render workers")
    return p.parse_args()


def main() -> int:
    args = _parse_args()
    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        print("ERROR: rsvg-convert not on PATH (brew install librsvg)", file=sys.stderr)
        return 2

    targets = _scan_posts()
    todo: list[tuple[Path, Path]] = []
    for _md, svg in targets:
        png = _needs_og_png(svg, args.force)
        if png is not None:
            todo.append((svg, png))

    print(f"posts with svg image: {len(targets)}")
    print(f"missing og png variants: {len(todo)}")

    if not todo:
        print("nothing to do.")
        return 0

    if args.dry_run:
        for svg, png in todo[:20]:
            print(f"  WOULD-RENDER {svg.name} -> {png.name}")
        if len(todo) > 20:
            print(f"  ... ({len(todo) - 20} more)")
        return 0

    ok_count = 0
    failed: list[tuple[Path, str]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(_render, svg, png, rsvg): (svg, png) for svg, png in todo}
        for fut in as_completed(futures):
            png, ok, msg = fut.result()
            svg, _ = futures[fut]
            if ok:
                ok_count += 1
                print(f"  ok   {png.name}")
            else:
                failed.append((svg, msg))
                print(f"  FAIL {svg.name}: {msg}")

    print(f"\nDone: {ok_count}/{len(todo)} rendered.")
    if failed:
        print(f"Failures: {len(failed)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
