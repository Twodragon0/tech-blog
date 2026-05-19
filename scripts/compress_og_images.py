#!/usr/bin/env python3
"""Batch-compress existing ``*_og.png`` files under ``assets/images/``.

Why this exists
---------------
Audit (2026-05-19) found ~188 OG cards averaging 244 KB (111 over 200 KB,
some up to 415 KB). Large OG PNGs inflate Google's image crawl cost and
make Twitter/Facebook/KakaoTalk preview fetches slower, which contributes
weakly to the GSC-indexing slowdown. The OG renderer
(``scripts/news/svg_generator._convert_svg_to_og_png``) now compresses on
generation; this script applies the same Pillow palette quantization
retroactively to the existing 188 files so the back-catalogue benefits too.

Usage
-----
::

    python3 scripts/compress_og_images.py                # dry-run
    python3 scripts/compress_og_images.py --apply        # write changes
    python3 scripts/compress_og_images.py --apply --sample 5
    python3 scripts/compress_og_images.py --apply --threshold-kb 150
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "assets" / "images"

sys.path.insert(0, str(ROOT / "scripts"))


def _compress_one(png_path: Path, max_kb: int, apply: bool) -> tuple[int, int]:
    """Return (size_before, size_after_or_zero). size_after=0 when skipped."""
    size_before = png_path.stat().st_size
    if size_before <= max_kb * 1024:
        return size_before, 0

    try:
        from PIL import Image
    except Exception:
        return size_before, 0

    try:
        with Image.open(png_path) as img:
            img.load()
            rgb = img.convert("RGB")
        paletted = rgb.quantize(
            colors=128,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
        tmp = png_path.with_suffix(".png.tmp")
        paletted.save(tmp, format="PNG", optimize=True)
        size_after = tmp.stat().st_size
        if size_after >= size_before:
            tmp.unlink(missing_ok=True)
            return size_before, 0
        if apply:
            tmp.replace(png_path)
        else:
            tmp.unlink(missing_ok=True)
        return size_before, size_after
    except Exception as exc:
        print(f"  ! {png_path.name}: {exc}", file=sys.stderr)
        return size_before, 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default: dry-run)"
    )
    parser.add_argument(
        "--threshold-kb",
        type=int,
        default=200,
        help="Skip files already under this size (KB). Default: 200",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="If >0, process only the N largest files (for QA)",
    )
    args = parser.parse_args()

    files = sorted(IMAGES_DIR.glob("*_og.png"))
    if not files:
        print(f"No *_og.png files under {IMAGES_DIR}", file=sys.stderr)
        return 1

    if args.sample > 0:
        files = sorted(files, key=lambda p: p.stat().st_size, reverse=True)[
            : args.sample
        ]

    total_before = 0
    total_after = 0
    n_compressed = 0
    n_skipped = 0
    n_unchanged = 0
    biggest_savings: list[tuple[int, str]] = []

    for p in files:
        before, after = _compress_one(p, args.threshold_kb, apply=args.apply)
        total_before += before
        if after == 0:
            if before <= args.threshold_kb * 1024:
                n_skipped += 1
            else:
                n_unchanged += 1
            total_after += before
            continue
        n_compressed += 1
        total_after += after
        biggest_savings.append((before - after, p.name))
        print(
            f"  {p.name}: {before // 1024:>4} → {after // 1024:>4} KB "
            f"(-{(before - after) * 100 // before}%)"
        )

    print()
    print("=" * 60)
    print(f"Files scanned    : {len(files)}")
    print(f"  Already small  : {n_skipped} (≤{args.threshold_kb}KB)")
    print(f"  Compressed     : {n_compressed}")
    print(f"  No-gain        : {n_unchanged} (quantize didn't shrink)")
    saved = total_before - total_after
    pct = (saved * 100 // total_before) if total_before else 0
    print(
        f"Total size       : {total_before / 1024 / 1024:.1f} MB → "
        f"{total_after / 1024 / 1024:.1f} MB (-{pct}%)"
    )
    if biggest_savings:
        biggest_savings.sort(reverse=True)
        print()
        print("Top 5 savings:")
        for delta, name in biggest_savings[:5]:
            print(f"  -{delta // 1024:>4} KB  {name}")
    if not args.apply:
        print()
        print("Dry-run only. Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
