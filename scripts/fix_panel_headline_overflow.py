#!/usr/bin/env python3
"""In-place fix for L20 side-panel headline overflow.

Truncates the headline text at x=670, y={140,404}, font-size=24 down to
27 chars max (with " ..." continuation), preserving the rest of the SVG.
This is intentionally surgical — it does NOT regenerate the cover, so the
body-derived topic headlines authored by the original L22 path remain
intact.

Usage:
    python3 scripts/fix_panel_headline_overflow.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.lib.svg_l20_hero import _fit_panel_headline  # noqa: E402

IMAGES_DIR = REPO_ROOT / "assets" / "images"

PANEL_HEADLINE_RE = re.compile(
    r'(<text x="670" y="(?:140|404)" font-family="Inter, Helvetica, Arial, sans-serif" '
    r'font-size="24" font-weight="800" fill="#F5F7FA">)([^<]+)(</text>)'
)


def fix_svg(path: Path) -> tuple[bool, list[tuple[str, str]]]:
    """Patch a single SVG. Returns (changed, [(old, new), ...])."""
    text = path.read_text(encoding="utf-8")
    changes: list[tuple[str, str]] = []

    def _repl(match: re.Match[str]) -> str:
        prefix, headline, suffix = match.group(1), match.group(2), match.group(3)
        capped = _fit_panel_headline(headline)
        if capped != headline:
            changes.append((headline, capped))
            return f"{prefix}{capped}{suffix}"
        return match.group(0)

    new_text = PANEL_HEADLINE_RE.sub(_repl, text)
    if changes:
        path.write_text(new_text, encoding="utf-8")
        return True, changes
    return False, []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="report only, do not write")
    args = parser.parse_args()

    modified = 0
    for svg in sorted(IMAGES_DIR.glob("*.svg")):
        text = svg.read_text(encoding="utf-8")
        if not PANEL_HEADLINE_RE.search(text):
            continue
        # Probe without writing first
        will_change = any(
            len(m.group(2)) > 27 for m in PANEL_HEADLINE_RE.finditer(text)
        )
        if not will_change:
            continue
        if args.dry_run:
            print(f"WOULD FIX  {svg.name}")
            for m in PANEL_HEADLINE_RE.finditer(text):
                hl = m.group(2)
                if len(hl) > 27:
                    print(f"           {len(hl):3d} -> {len(_fit_panel_headline(hl)):3d} :: {hl!r}")
            modified += 1
            continue
        changed, edits = fix_svg(svg)
        if changed:
            print(f"FIXED      {svg.name}")
            for old, new in edits:
                print(f"           {len(old):3d} -> {len(new):3d} :: {old!r} -> {new!r}")
            modified += 1

    print(f"\n{'Would modify' if args.dry_run else 'Modified'}: {modified} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
