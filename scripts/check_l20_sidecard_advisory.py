#!/usr/bin/env python3
"""Gate: no L20 digest cover may render the advisory shield in a SIDE card.

``vb_security_advisory`` is authored at HERO scale; in a side card (top_right /
bottom_right) its ``SECURITY ADVISORY`` header is drawn ~82px above the visual
centre, where it OCCLUDES the band headline, and two side bands that both
downgrade render two identical shields. The generator now demotes side-card
advisory to a neutral motif (``_demote_sidecard_advisory`` in
``scripts/news/l20_dispatch.py``), and the hero keeps the panel where it fits.

This gate is the regression backstop for that rule: it fails if any L20 cover
draws ``SECURITY ADVISORY`` in a band whose visual centre is on the right
column (x≈800), e.g. when an unattended blogwatcher cron publishes a cover via
a stale code path. The hero advisory (visual centre x≈332) is allowed.

Usage:
    python3 scripts/check_l20_sidecard_advisory.py            # scan all L20 covers
    python3 scripts/check_l20_sidecard_advisory.py <svg>...   # scan specific files
Exit 0 = clean, 1 = at least one side-card advisory found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets" / "images"

_L20_MARKER = "L20 Hero+2-Card"
_ADVISORY_LABEL = "SECURITY ADVISORY"
# Band visual centres in render_l20_hero: hero=(332,360), top_right=(800,230),
# bottom_right=(800,490). Anything with centre x on the right column is a side
# card; >600 cleanly separates the hero (332) from the side cards (800).
_SIDE_CARD_MIN_X = 600
_TRANSLATE_RE = re.compile(r"translate\((\d+)\s*,\s*\d+\)")


def _side_card_advisory_offsets(svg_text: str) -> List[int]:
    """Return the char offsets of each SIDE-card advisory panel in ``svg_text``.

    For every ``SECURITY ADVISORY`` label, find the nearest preceding
    ``translate(cx,cy)`` (the panel's band-centre group) and flag it when
    ``cx`` is on the right column (a side card).
    """
    hits: List[int] = []
    for m in re.finditer(re.escape(_ADVISORY_LABEL), svg_text):
        prefix = svg_text[: m.start()]
        last = None
        for t in _TRANSLATE_RE.finditer(prefix):
            last = t
        if last is not None and int(last.group(1)) >= _SIDE_CARD_MIN_X:
            hits.append(m.start())
    return hits


def check_file(svg_path: Path) -> Tuple[bool, str]:
    """Return (ok, message) for one SVG. Non-L20 covers are skipped (ok)."""
    try:
        text = svg_path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - unreadable file
        return False, f"unreadable: {exc}"
    if _L20_MARKER not in text:
        return True, "skip (not L20)"
    hits = _side_card_advisory_offsets(text)
    if hits:
        return False, f"{len(hits)} side-card advisory panel(s) — occludes the band headline"
    return True, "clean"


def _targets(argv: List[str]) -> List[Path]:
    if argv:
        return [Path(a) for a in argv]
    return sorted(ASSETS.glob("*.svg"))


def main(argv: List[str]) -> int:
    targets = _targets(argv)
    if not targets:
        print("[sidecard-advisory] no SVGs to scan")
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
        print(f"[sidecard-advisory] FAIL — {len(violations)} cover(s) draw the advisory shield in a side card:")
        for svg, msg in violations:
            print(f"  ✗ {svg.name}: {msg}")
        print("  Fix: regenerate via the cron L20 path (auto_publish_news._render_l20_svg_string),")
        print("  which demotes side-card advisory to a neutral motif. See _demote_sidecard_advisory.")
        return 1
    print(f"[sidecard-advisory] OK — {scanned} L20 cover(s) checked, 0 side-card advisory panels.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
