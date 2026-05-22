#!/usr/bin/env python3
"""Build raster variants for the 21 newly-rendered Feb 2026 L20 covers.

Produces per SVG:
  - {basename}_og.png   (1200x630, rsvg-convert)
  - {basename}_og.webp  (PIL, q=80)
  - {basename}_og.avif  (PIL, q=60)
  - {basename}_card.webp (PIL, 525x295, q=80)
  - {basename}_card.avif (PIL, 525x295, q=60)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets" / "images"

OG_W, OG_H = 1200, 630
CARD_W, CARD_H = 525, 295


def build(svg: Path) -> None:
    base = svg.with_suffix("").name
    og_png = ASSETS / f"{base}_og.png"
    og_webp = ASSETS / f"{base}_og.webp"
    og_avif = ASSETS / f"{base}_og.avif"
    card_webp = ASSETS / f"{base}_card.webp"
    card_avif = ASSETS / f"{base}_card.avif"

    # Step 1: SVG → og.png via rsvg-convert
    subprocess.run(
        ["rsvg-convert", "-w", str(OG_W), "-h", str(OG_H), "-o", str(og_png), str(svg)],
        check=True,
    )

    # Step 2: og.png → og.webp / og.avif
    from PIL import Image  # type: ignore

    with Image.open(og_png) as og:
        og.load()
        og.save(og_webp, "WEBP", quality=80)
        og.save(og_avif, "AVIF", quality=60)

        # Step 3: og.png → card.{webp,avif} (resize)
        card = og.resize((CARD_W, CARD_H), Image.LANCZOS)
        card.save(card_webp, "WEBP", quality=80)
        card.save(card_avif, "AVIF", quality=60)


def main() -> None:
    svgs = sorted(ASSETS.glob("2026-02-*-Tech_Security_Weekly_Digest_*.svg"))
    if not svgs:
        print("[error] no 2026-02 SVGs found")
        sys.exit(1)

    ok = 0
    fail = 0
    for svg in svgs:
        try:
            build(svg)
            print(f"[ok] {svg.name}")
            ok += 1
        except Exception as exc:
            print(f"[fail] {svg.name}: {exc}")
            fail += 1
    print(f"\n[done] built {ok}/{len(svgs)} ({fail} failed)")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
