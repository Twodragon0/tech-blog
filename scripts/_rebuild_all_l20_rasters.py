#!/usr/bin/env python3
"""Rebuild raster variants for every L20 cover. One-shot after renderer enrichment."""
from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO / "_data" / "l20_covers"
ASSETS = REPO / "assets" / "images"

OG_W, OG_H = 1200, 630
CARD_W, CARD_H = 525, 295


def build_one(svg_name: str) -> tuple[str, bool, str]:
    from PIL import Image  # type: ignore

    svg = ASSETS / svg_name
    base = svg.with_suffix("").name
    og_png = ASSETS / f"{base}_og.png"
    try:
        subprocess.run(
            ["rsvg-convert", "-w", str(OG_W), "-h", str(OG_H), "-o", str(og_png), str(svg)],
            check=True,
            capture_output=True,
        )
        with Image.open(og_png) as og:
            og.load()
            og.save(ASSETS / f"{base}_og.webp", "WEBP", quality=80)
            og.save(ASSETS / f"{base}_og.avif", "AVIF", quality=60)
            card = og.resize((CARD_W, CARD_H), Image.LANCZOS)
            card.save(ASSETS / f"{base}_card.webp", "WEBP", quality=80)
            card.save(ASSETS / f"{base}_card.avif", "AVIF", quality=60)
        return (svg_name, True, "")
    except Exception as exc:
        return (svg_name, False, str(exc))


def main() -> None:
    targets = []
    for spec in sorted(SPECS_DIR.glob("*.yml")):
        # spec name == "{date}-{slug}.yml"; expected SVG is "{date}-{slug}.svg" in assets/
        svg_name = spec.with_suffix(".svg").name
        if (ASSETS / svg_name).exists():
            targets.append(svg_name)
    print(f"[start] rebuilding rasters for {len(targets)} L20 covers")

    ok = fail = 0
    with ProcessPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(build_one, name): name for name in targets}
        for fut in as_completed(futures):
            name, success, err = fut.result()
            if success:
                ok += 1
            else:
                print(f"[fail] {name}: {err}")
                fail += 1
            if (ok + fail) % 20 == 0:
                print(f"  progress: {ok + fail}/{len(targets)}")

    print(f"\n[done] {ok}/{len(targets)} rebuilt ({fail} failed)")
    if fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
