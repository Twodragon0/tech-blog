#!/usr/bin/env python3
"""Gate: every cover raster must have a base .svg (no orphans from renames).

Cover assets come in families: ``<slug>.svg`` plus the generated rasters
``<slug>_og.png`` / ``<slug>_og.webp`` / ``<slug>_og.avif`` /
``<slug>_card.webp`` / ``<slug>_card.avif``. When a cover is RENAMED, the old
SVG is replaced under a new slug but the old-slug rasters are easy to leave
behind — dead weight that ships to production and bloats the repo. (45 such
files accumulated and were removed 2026-06-22.)

This gate fails if any raster has no sibling ``<slug>.svg``. Run after any
cover rename or bulk raster rebuild.

Usage:
    python3 scripts/check_orphan_cover_rasters.py            # scan assets/images
    python3 scripts/check_orphan_cover_rasters.py <dir>      # scan a dir
Exit 0 = clean, 1 = orphan raster(s) found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets" / "images"

_RASTER_RE = re.compile(r"^(?P<base>.+?)_(?:og|card)\.(?:png|webp|avif)$")


def orphan_rasters(images_dir: Path) -> List[Path]:
    """Return raster files whose base ``<slug>.svg`` is absent."""
    orphans: List[Path] = []
    for p in sorted(images_dir.iterdir()):
        if not p.is_file():
            continue
        m = _RASTER_RE.match(p.name)
        if not m:
            continue
        if not (images_dir / f"{m.group('base')}.svg").exists():
            orphans.append(p)
    return orphans


def main(argv: List[str]) -> int:
    images_dir = Path(argv[0]) if argv else ASSETS
    if not images_dir.is_dir():
        print(f"[orphan-rasters] not a directory: {images_dir}")
        return 0
    orphans = orphan_rasters(images_dir)
    if orphans:
        print(f"[orphan-rasters] FAIL — {len(orphans)} raster(s) have no base .svg (likely a rename left them behind):")
        for o in orphans:
            print(f"  ✗ {o.name}")
        print("  Fix: git rm the orphans (after confirming the slug is referenced nowhere), or")
        print("  regenerate the base SVG if the rename was unintended.")
        return 1
    print("[orphan-rasters] OK — every cover raster has a base .svg.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
