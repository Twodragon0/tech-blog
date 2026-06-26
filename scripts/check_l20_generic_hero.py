#!/usr/bin/env python3
"""Gate: no L20 digest cover may render a generic-pool placeholder as its hero.

``extract_three_stories`` pads missing digest story slots from a generic pool
(``Security Update`` / ``Threat Analysis`` / ``Patch Advisory``,
``scripts/news/l20_dispatch.py``). That pool is a LAST-RESORT base fallback,
meant to be overridden by ``_apply_real_content`` with the post's real lead
story (from ``summary_card.highlights`` or the body highlights table). When the
override has no source — historically the cron path never parsed
``summary_card``, so digests with no body table kept the placeholder — the hero
shipped a meaningless ``Security Update`` headline.

The generator now surfaces the real lead story on the cron + regen paths (shared
``load_post_fields`` parser; see
``.omc/plans/l20-digest-hero-generic-pool-fix.md``). This gate is the corpus-
level regression backstop for the bug CLASS: it fails if any published L20 cover
draws an EXACT generic-pool string in its hero ``<text>`` slot, catching a future
table-less digest or a blogwatcher cron publishing via a stale code path.

Only the HERO band is checked. The generic-pool strings are produced solely by
the digest extractor (content covers use ``extract_content_stories`` with
category-themed fallbacks), so a generic-pool hero can only be a digest cover.

Usage:
    python3 scripts/check_l20_generic_hero.py            # scan all L20 covers
    python3 scripts/check_l20_generic_hero.py <svg>...   # scan specific files
Exit 0 = clean, 1 = at least one generic-pool hero found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets" / "images"

_L20_MARKER = "L20 Hero+2-Card"
# Mirror the generic pool in l20_dispatch.extract_three_stories (the LAST-RESORT
# base headlines that _apply_real_content is supposed to override). Kept inline
# (not imported) so this gate runs in a minimal CI env without the generator's
# dependency chain.
_GENERIC_POOL = frozenset({"Security Update", "Threat Analysis", "Patch Advisory"})

# Hero headline <text> in render_l20_hero is drawn at x=54 y=146 (font-size 31,
# weight 800). Side-card headlines are at x=670, so this anchor isolates the
# hero band.
_HERO_TEXT_RE = re.compile(
    r'<text x="54" y="146"[^>]*font-size="31"[^>]*>([^<]*)</text>'
)


def _hero_text(svg_text: str) -> Optional[str]:
    """Return the hero band's headline <text> content, or None if absent."""
    m = _HERO_TEXT_RE.search(svg_text)
    return m.group(1) if m else None


def check_file(svg_path: Path) -> Tuple[bool, str]:
    """Return (ok, message) for one SVG. Non-L20 covers are skipped (ok)."""
    try:
        text = svg_path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - unreadable file
        return False, f"unreadable: {exc}"
    if _L20_MARKER not in text:
        return True, "skip (not L20)"
    hero = _hero_text(text)
    if hero is None:
        return True, "skip (no hero text)"
    if hero in _GENERIC_POOL:
        return False, f"hero is a generic-pool placeholder: {hero!r}"
    return True, "clean"


def _targets(argv: List[str]) -> List[Path]:
    if argv:
        return [Path(a) for a in argv]
    return sorted(ASSETS.glob("*.svg"))


def main(argv: List[str]) -> int:
    targets = _targets(argv)
    if not targets:
        print("[generic-hero] no SVGs to scan")
        return 0
    violations = []
    scanned = 0
    for svg in targets:
        ok, msg = check_file(svg)
        if "skip" in msg:
            continue
        scanned += 1
        if not ok:
            violations.append((svg, msg))
    if violations:
        print(
            f"[generic-hero] FAIL — {len(violations)} L20 cover(s) render a "
            f"generic-pool placeholder as the hero:"
        )
        for svg, msg in violations:
            print(f"  ✗ {svg.name}: {msg}")
        print("  Fix: regenerate via the cron L20 path "
              "(scripts/regen_l20_digest_covers.py), which now surfaces the")
        print("  post's real lead story from summary_card.highlights via "
              "load_post_fields. See _digest_panels / _apply_real_content.")
        return 1
    print(f"[generic-hero] OK — {scanned} L20 cover(s) checked, 0 generic-pool heroes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
