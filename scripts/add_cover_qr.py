#!/usr/bin/env python3
"""Add a QR code block to a 1200x630 SVG cover.

Inserts a white rounded rect with the QR pattern (encoded as a single
`<path>`) at the bottom-right corner, plus a "scan / full post" caption.
Idempotent: skips files that already contain the QR marker.

Usage:
    python3 scripts/add_cover_qr.py <svg_path> <url>

The QR is generated with `qrcode` (error correction M, version chosen
automatically). The resulting path is rendered inside a 100x100 frame
positioned at translate(1080, 504), matching the layout of the
2026-04-22 reference cover.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_M

QR_MARKER = "<!-- cover-qr:"


def build_qr_path_data(modules: list[list[bool]]) -> str:
    """Build a single SVG path 'd' attribute that fills 1x1 squares for
    every dark QR module. Coordinates are in module units (caller scales)."""
    parts: list[str] = []
    n = len(modules)
    for y in range(n):
        x = 0
        while x < n:
            if not modules[y][x]:
                x += 1
                continue
            run_start = x
            while x < n and modules[y][x]:
                x += 1
            run_len = x - run_start
            parts.append(f"M{run_start} {y}h{run_len}v1h-{run_len}z")
    return "".join(parts)


def build_qr_block(url: str) -> tuple[str, int]:
    """Generate the QR `<g>` block. Returns (svg_xml, qr_module_count)."""
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_M, box_size=1, border=0)
    qr.add_data(url)
    qr.make(fit=True)
    modules = [[bool(cell) for cell in row] for row in qr.modules]
    n = len(modules)
    path_d = build_qr_path_data(modules)
    # Frame is 84x84 (100 outer minus 8px white border on each side baked
    # into the white rect). Path is in module units (0..n), so scale by
    # 84/n to make it fit. Center via translate.
    inner_size = 84.0
    scale = inner_size / n
    return (
        f"""<g transform=\"translate(1080,504)\" filter=\"url(#softShadow)\">
  <rect x=\"-8\" y=\"-8\" width=\"100\" height=\"100\" rx=\"6\" fill=\"#FFFFFF\"/>
  <g transform=\"scale({scale:.6f})\" fill=\"#0A1020\">
    <path d=\"{path_d}\"/>
  </g>
</g>
<text x=\"1122\" y=\"614\" font-family=\"Inter, Helvetica, Arial, sans-serif\" font-size=\"10\" font-weight=\"700\" fill=\"#F5F7FA\" text-anchor=\"middle\">scan / full post</text>
""",
        n,
    )


def needs_soft_shadow_filter(svg: str) -> bool:
    return "id=\"softShadow\"" not in svg


def soft_shadow_def() -> str:
    return (
        "<filter id=\"softShadow\" x=\"-10%\" y=\"-10%\" width=\"130%\" height=\"130%\">"
        "<feGaussianBlur in=\"SourceAlpha\" stdDeviation=\"2.5\"/>"
        "<feOffset dx=\"1\" dy=\"3\"/>"
        "<feComponentTransfer><feFuncA type=\"linear\" slope=\"0.55\"/></feComponentTransfer>"
        "<feMerge><feMergeNode/><feMergeNode in=\"SourceGraphic\"/></feMerge>"
        "</filter>"
    )


def add_qr(svg_path: Path, url: str) -> None:
    text = svg_path.read_text(encoding="utf-8")
    if QR_MARKER in text:
        print(f"[skip] {svg_path.name}: QR already present")
        return
    if "</svg>" not in text:
        raise SystemExit(f"[error] {svg_path}: no closing </svg> tag")

    qr_block, n = build_qr_block(url)
    marker = f"{QR_MARKER} {url} : {n}x{n} -->\n"

    insertion = marker + qr_block

    # If softShadow filter missing, inject a minimal one inside <defs> so the
    # QR drop shadow renders. Most covers in this repo already define it.
    if needs_soft_shadow_filter(text):
        if "</defs>" in text:
            text = text.replace("</defs>", soft_shadow_def() + "</defs>", 1)
        else:
            # No defs at all — inject one right after <svg ...>
            after_svg = text.find(">", text.find("<svg")) + 1
            text = (
                text[:after_svg]
                + f"\n<defs>{soft_shadow_def()}</defs>\n"
                + text[after_svg:]
            )

    text = text.replace("</svg>", insertion + "</svg>", 1)
    svg_path.write_text(text, encoding="utf-8")
    print(f"[ok]   {svg_path.name}: QR added ({n}x{n} for {url})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="path to .svg cover file")
    parser.add_argument("url", type=str, help="URL to encode in the QR")
    args = parser.parse_args()

    if not args.svg.exists():
        print(f"[error] {args.svg} not found", file=sys.stderr)
        return 1
    add_qr(args.svg, args.url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
