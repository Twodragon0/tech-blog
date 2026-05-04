#!/usr/bin/env python3
"""Backfill missing _og.avif and _og.webp variants from existing _og.png covers.

Idempotent — skips files that already exist. Designed to be safe to run
on every Vercel build via build.sh, and also as a one-shot for repo-wide
backfilling.

Quality settings mirror scripts/regenerate_og_images.py so SVG → PNG
regenerations and PNG → modern-format passes stay consistent:
  WebP: quality=80
  AVIF: quality=60

Exit codes:
  0  success (or skipped — Pillow not available is a soft warning, not a
     hard failure, so the build keeps going on machines that lack the
     dependency)
  1  one or more conversions raised an exception
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = REPO_ROOT / "assets" / "images"


def main() -> int:
    try:
        from PIL import Image
    except ImportError:
        print(
            "Pillow not available — skipping _og.avif / _og.webp backfill. "
            "Install with: pip install Pillow"
        )
        return 0

    if not IMG_DIR.is_dir():
        print(f"ERROR: {IMG_DIR} not found", file=sys.stderr)
        return 1

    pngs = sorted(IMG_DIR.glob("*_og.png"))
    avif_made = webp_made = skipped = errors = 0

    for png_path in pngs:
        base = png_path.name[: -len("_og.png")]
        avif_path = IMG_DIR / f"{base}_og.avif"
        webp_path = IMG_DIR / f"{base}_og.webp"

        need_avif = not avif_path.exists()
        need_webp = not webp_path.exists()
        if not (need_avif or need_webp):
            skipped += 1
            continue

        try:
            with Image.open(png_path) as src:
                rgb = src.convert("RGB")
                if need_webp:
                    rgb.save(webp_path, "WEBP", quality=80)
                    webp_made += 1
                if need_avif:
                    rgb.save(avif_path, "AVIF", quality=60)
                    avif_made += 1
        except Exception as e:  # noqa: BLE001 — keep going on individual failures
            errors += 1
            print(f"ERROR: {png_path.name}: {e}", file=sys.stderr)

    print(
        f"PNG inputs: {len(pngs)} | "
        f"avif generated: {avif_made} | "
        f"webp generated: {webp_made} | "
        f"already complete: {skipped} | "
        f"errors: {errors}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
