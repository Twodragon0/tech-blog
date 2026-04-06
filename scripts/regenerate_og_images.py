#!/usr/bin/env python3
"""Regenerate OG images (PNG/WebP/AVIF) from SVG files using cairosvg."""

import glob
import os
import sys


def main():
    try:
        import cairosvg
    except ImportError:
        # Try venv
        venv_python = "/tmp/svg-env/bin/python3"
        if os.path.exists(venv_python):
            os.execv(venv_python, [venv_python] + sys.argv)
        print("ERROR: cairosvg not available. Install: pip install cairosvg")
        sys.exit(1)

    try:
        from PIL import Image
    except ImportError:
        print("WARNING: PIL not available, skipping WebP/AVIF")
        Image = None

    img_dir = "assets/images"
    svg_files = sorted(glob.glob(os.path.join(img_dir, "*.svg")))
    svg_files = [
        f
        for f in svg_files
        if not os.path.basename(f).startswith(("section-", "og-", "news-"))
    ]

    converted = errors = 0
    for svg_path in svg_files:
        basename = os.path.splitext(os.path.basename(svg_path))[0]
        png_path = os.path.join(img_dir, f"{basename}_og.png")

        try:
            cairosvg.svg2png(
                url=svg_path, write_to=png_path, output_width=1200, output_height=630
            )
            converted += 1

            if Image:
                img = Image.open(png_path).convert("RGB")
                img.save(png_path.replace("_og.png", "_og.webp"), "WEBP", quality=80)
                img.save(png_path.replace("_og.png", "_og.avif"), "AVIF", quality=60)
        except Exception as e:
            errors += 1
            if errors <= 3:
                print(f"ERROR: {os.path.basename(svg_path)}: {e}")

    print(f"Converted: {converted}, Errors: {errors}")


if __name__ == "__main__":
    main()
