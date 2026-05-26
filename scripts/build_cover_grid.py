#!/usr/bin/env python3
"""Build a visual catalog of every L20 cover.

Walks ``_data/l20_covers/*.yml`` and emits a self-contained HTML grid
to ``assets/images/cover_grid_index.html``. The grid is grouped by
month (newest first) and shows the rendered cover (via the on-disk
``_og.webp`` raster — falls back to the SVG when the raster is
missing) with a metadata overlay carrying the three story headlines.

Usage::

  python3 scripts/build_cover_grid.py
  python3 scripts/build_cover_grid.py --output assets/images/cover_grid_index.html
  python3 scripts/build_cover_grid.py --open      # open the result in the default browser

Exit code: 0 on success, 1 if no specs were found.
"""
from __future__ import annotations

import argparse
import html
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import yaml

REPO = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO / "_data" / "l20_covers"
ASSETS = REPO / "assets" / "images"
DEFAULT_OUTPUT = ASSETS / "cover_grid_index.html"


def _pick_raster(date: str, slug: str) -> str:
    """Return the relative href for the most efficient raster variant on disk."""
    base = f"{date}-{slug}"
    # Prefer WebP (smaller, near-universal browser support); fall back to PNG,
    # then to the SVG when the raster pipeline hasn't run yet.
    for ext in ("_og.webp", "_og.png", ".svg"):
        if (ASSETS / f"{base}{ext}").exists():
            return f"{base}{ext}"
    return f"{base}.svg"


def _short(text: str, limit: int = 90) -> str:
    s = (text or "").strip()
    if len(s) <= limit:
        return s
    return s[: limit - 1].rstrip() + "…"


def _month_label(yyyy_mm: str) -> str:
    return datetime.strptime(yyyy_mm, "%Y-%m").strftime("%B %Y")


def load_specs() -> List[Dict]:
    specs: List[Dict] = []
    for path in sorted(SPECS_DIR.glob("*.yml")):
        try:
            with path.open() as f:
                data = yaml.safe_load(f)
        except Exception as exc:
            print(f"[warn] failed to read {path.name}: {exc}", file=sys.stderr)
            continue
        if not isinstance(data, dict) or "date" not in data or "slug" not in data:
            continue
        data["_spec_path"] = path
        specs.append(data)
    return specs


def render_html(specs: List[Dict]) -> str:
    by_month: Dict[str, List[Dict]] = defaultdict(list)
    for spec in specs:
        date = str(spec["date"])
        yyyy_mm = date[:7]
        by_month[yyyy_mm].append(spec)

    # Newest month first; within each month newest date first.
    months_sorted = sorted(by_month.keys(), reverse=True)
    for m in months_sorted:
        by_month[m].sort(key=lambda s: str(s["date"]), reverse=True)

    total = len(specs)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    parts: List[str] = []
    parts.append("<!doctype html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('  <meta charset="utf-8">')
    parts.append('  <meta name="viewport" content="width=device-width, initial-scale=1">')
    parts.append("  <title>L20 Cover Catalog</title>")
    parts.append(
        "  <style>\n"
        "    :root { color-scheme: dark; }\n"
        "    * { box-sizing: border-box; }\n"
        "    body {\n"
        "      margin: 0; padding: 32px 24px 64px;\n"
        "      font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', sans-serif;\n"
        "      background: #050813; color: #F8FAFC;\n"
        "    }\n"
        "    header { max-width: 1280px; margin: 0 auto 32px; }\n"
        "    header h1 { font-size: 32px; margin: 0 0 8px; letter-spacing: -0.5px; }\n"
        "    header p { margin: 0; color: #8FB8FF; font-size: 14px; letter-spacing: 1.5px; }\n"
        "    .month { max-width: 1280px; margin: 0 auto 48px; }\n"
        "    .month h2 {\n"
        "      font-size: 20px; margin: 0 0 16px; padding: 8px 14px;\n"
        "      background: #0F1A2F; border-left: 4px solid #E63946; color: #F5F7FA;\n"
        "      letter-spacing: 0.5px;\n"
        "    }\n"
        "    .grid {\n"
        "      display: grid;\n"
        "      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));\n"
        "      gap: 18px;\n"
        "    }\n"
        "    .card {\n"
        "      background: #0F1A2F; border: 1px solid #1B2742; border-radius: 10px;\n"
        "      overflow: hidden; display: flex; flex-direction: column;\n"
        "      transition: border-color 0.15s ease, transform 0.15s ease;\n"
        "    }\n"
        "    .card:hover { border-color: #3B82F6; transform: translateY(-2px); }\n"
        "    .card img {\n"
        "      display: block; width: 100%; height: auto; aspect-ratio: 1200 / 630;\n"
        "      background: #050813;\n"
        "    }\n"
        "    .meta { padding: 12px 14px 14px; flex: 1; display: flex; flex-direction: column; gap: 6px; }\n"
        "    .meta .date { font-size: 11px; letter-spacing: 1.6px; color: #7DA3D9; font-weight: 700; }\n"
        "    .meta .slug { font-size: 13px; color: #F5F7FA; font-weight: 600; line-height: 1.35; }\n"
        "    .stories { margin-top: 6px; font-size: 11px; color: #A5B4C4; line-height: 1.45; }\n"
        "    .stories li { margin-bottom: 4px; }\n"
        "    .stories li::marker { color: #E63946; }\n"
        "    a { color: inherit; text-decoration: none; }\n"
        "    a:focus-visible .card { outline: 2px solid #3B82F6; outline-offset: 2px; }\n"
        "  </style>"
    )
    parts.append("</head>")
    parts.append("<body>")
    parts.append("  <header>")
    parts.append('    <p>WEEKLY DIGEST  /  L20 HERO+2-CARD CATALOG</p>')
    parts.append(f"    <h1>{total} L20 covers, generated {generated_at}</h1>")
    parts.append("  </header>")

    for month in months_sorted:
        parts.append('  <section class="month">')
        parts.append(f"    <h2>{_month_label(month)} — {len(by_month[month])} covers</h2>")
        parts.append('    <div class="grid">')
        for spec in by_month[month]:
            date = str(spec["date"])
            slug = str(spec["slug"])
            url = str(spec.get("url", "#"))
            title = _short(str(spec.get("post_title", slug)), 110)
            raster = _pick_raster(date, slug)

            hero_headline = _short(str(spec.get("hero", {}).get("headline", "")), 60)
            tr_headline = _short(str(spec.get("top_right", {}).get("headline", "")), 60)
            br_headline = _short(str(spec.get("bottom_right", {}).get("headline", "")), 60)

            parts.append(
                f'      <a href="{html.escape(url)}" target="_blank" rel="noopener" '
                f'title="{html.escape(title)}">'
            )
            parts.append('        <article class="card">')
            parts.append(
                f'          <img src="{html.escape(raster)}" '
                f'alt="{html.escape(title)}" loading="lazy" decoding="async" />'
            )
            parts.append('          <div class="meta">')
            parts.append(f'            <div class="date">{html.escape(date)}</div>')
            parts.append(f'            <div class="slug">{html.escape(title)}</div>')
            parts.append('            <ol class="stories">')
            for line in (hero_headline, tr_headline, br_headline):
                if line:
                    parts.append(f"              <li>{html.escape(line)}</li>")
            parts.append("            </ol>")
            parts.append("          </div>")
            parts.append("        </article>")
            parts.append("      </a>")
        parts.append("    </div>")
        parts.append("  </section>")

    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT, help="HTML output path.")
    parser.add_argument("--open", action="store_true", help="Open the generated file in the default browser.")
    args = parser.parse_args()

    specs = load_specs()
    if not specs:
        print(f"[error] no L20 specs found under {SPECS_DIR}", file=sys.stderr)
        return 1

    html_text = render_html(specs)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(html_text, encoding="utf-8")
    size_kb = len(html_text.encode("utf-8")) / 1024
    print(f"[ok] wrote {len(specs)} covers → {args.output} ({size_kb:.1f} KB)")

    if args.open:
        subprocess.run(["open", str(args.output)], check=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
