#!/usr/bin/env python3
"""Backfill missing _card.avif and _card.webp variants (525w) from _og.png.

Mirrors backfill_og_modern_variants.py but emits a smaller 525w pair sized
to match the homepage / post-card display width. The post-card.html
<picture> emits a `srcset="{{ card_sm }} 525w, {{ card }} 1120w"` only when
both files exist, so generating these unlocks responsive serving on every
listing page (PSI: ~94 KiB savings flagged on the homepage).

Idempotent — skips files that already exist. Safe to run on every Vercel
build via build.sh and as a one-shot for repo-wide backfilling.

Output: 525x295 (16:9, mirrors the source 1120x630).
Quality: WebP=80, AVIF=60 (matches og variants).

Exit codes:
  0  success (or skipped — Pillow not available is a soft warning)
  1  one or more conversions raised an exception
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IMG_DIR = REPO_ROOT / "assets" / "images"

CARD_WIDTH = 525
CARD_HEIGHT = 295  # 525 * 630/1120 -> 295.3, rounded to keep aspect close to 16:9


def main() -> int:
    try:
        from PIL import Image
    except ImportError:
        print(
            "Pillow not available — skipping _card.avif / _card.webp backfill. "
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
        avif_path = IMG_DIR / f"{base}_card.avif"
        webp_path = IMG_DIR / f"{base}_card.webp"

        need_avif = not avif_path.exists()
        need_webp = not webp_path.exists()
        if not (need_avif or need_webp):
            skipped += 1
            continue

        try:
            with Image.open(png_path) as src:
                rgb = src.convert("RGB")
                resized = rgb.resize(
                    (CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS
                )
                if need_webp:
                    resized.save(webp_path, "WEBP", quality=80)
                    webp_made += 1
                if need_avif:
                    resized.save(avif_path, "AVIF", quality=60)
                    avif_made += 1
        except Exception as e:  # noqa: BLE001 — keep going on individual failures
            errors += 1
            print(f"ERROR: {png_path.name}: {e}", file=sys.stderr)

    print(
        f"PNG inputs: {len(pngs)} | "
        f"card.avif generated: {avif_made} | "
        f"card.webp generated: {webp_made} | "
        f"already complete: {skipped} | "
        f"errors: {errors}"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
