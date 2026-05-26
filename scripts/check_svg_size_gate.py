#!/usr/bin/env python3
"""SVG Quality Gate — size-band check shared by pre-commit and CI.

Three profiles, matched in this order on each post-date SVG
(``assets/images/YYYY-MM-DD-*.svg``):

  1. rollup cover         (WEEKLY ROLLUP / MONTHLY INDEX, ``bgRoll*`` defs)
                          → 38000-83968 bytes
  2. high-quality cover   (``profile: high-quality-cover``, ``bgSpread*``,
                          ``heroPanel*``, scene-glow / float keyframes)
                          → 18000-73728 bytes
  3. lane / digest        (everything else)
                          → 5000-24576 bytes

Exempt filenames: ``section-*``, ``news-fallback.svg``, ``*-mermaid-*``,
``*-og.svg``. Non-date filenames are skipped silently.

Usage::

  python3 scripts/check_svg_size_gate.py --staged          # files in git index
  python3 scripts/check_svg_size_gate.py --changed BASE    # diff BASE..HEAD
  python3 scripts/check_svg_size_gate.py --all             # every SVG in repo
  python3 scripts/check_svg_size_gate.py path/to/file.svg  # explicit list

Exit codes:
  0  no violations OR warn-only mode (default)
  1  one or more files outside their profile band (with --strict)
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "assets" / "images"


# Profile bands (keep in sync with scripts/check_svg_precommit.sh).
BANDS = {
    "std": (5000, 24576),
    "hq": (18000, 73728),
    "rollup": (38000, 83968),
}


HQ_RE = re.compile(
    r'sceneGlow1|sceneGlow2|@keyframes [^ ]*floatUp|clipPath id="[^"]*clip"'
    r'|profile: high-quality-cover|id="bgSpread[A-Z0-9]*"'
    r'|id="heroPanel[A-Z0-9]*"|id="bandA[A-Z0-9]+"'
)
ROLLUP_RE = re.compile(
    r'>WEEKLY ROLLUP<|>MONTHLY INDEX<|id="bgRoll[A-Z0-9]+"|id="hdrGrad[A-Z0-9]+"'
)
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")
EXEMPT_PATTERNS = (
    re.compile(r"^section-"),
    re.compile(r"^news-fallback\.svg$"),
    re.compile(r"-mermaid-"),
    re.compile(r"-og\.svg$"),
)


def is_exempt(name: str) -> bool:
    return any(p.search(name) for p in EXEMPT_PATTERNS)


def classify(svg: Path) -> str:
    """Return 'rollup' / 'hq' / 'std' per the marker rules above."""
    text = svg.read_text(encoding="utf-8", errors="replace")
    if ROLLUP_RE.search(text):
        return "rollup"
    if HQ_RE.search(text):
        return "hq"
    return "std"


def check_one(svg: Path) -> List[str]:
    """Return list of WARN strings (empty if file passes)."""
    if not svg.exists():
        return [f"[svg-gate] WARN: {svg} does not exist."]
    if is_exempt(svg.name) or not DATE_PREFIX_RE.match(svg.name):
        return []
    size = svg.stat().st_size
    profile = classify(svg)
    mn, mx = BANDS[profile]
    if size < mn:
        return [
            f"[svg-gate] WARN: {svg} is {size} bytes (< {mn}) for a "
            f"{profile} SVG profile."
        ]
    if size > mx:
        return [
            f"[svg-gate] WARN: {svg} is {size} bytes (> {mx}) for a "
            f"{profile} SVG profile."
        ]
    return []


def _run_git(*args: str) -> List[str]:
    out = subprocess.run(
        ["git", "-C", str(REPO), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        return []
    return [line for line in out.stdout.splitlines() if line]


def _filter_post_svgs(paths: Iterable[str]) -> List[Path]:
    keep = []
    for raw in paths:
        # Restrict to assets/images/*.svg (root of that dir, no subdirs).
        p = Path(raw)
        if (
            p.parts[:2] == ("assets", "images")
            and len(p.parts) == 3
            and p.suffix == ".svg"
        ):
            keep.append(REPO / p)
    return keep


def collect_staged() -> List[Path]:
    return _filter_post_svgs(
        _run_git("diff", "--cached", "--name-only", "--diff-filter=ACM")
    )


def collect_changed(base: str) -> List[Path]:
    return _filter_post_svgs(
        _run_git("diff", "--name-only", "--diff-filter=ACM", f"{base}...HEAD")
    )


def collect_all() -> List[Path]:
    return sorted(p for p in ASSETS.glob("*.svg") if not is_exempt(p.name))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--staged", action="store_true", help="Check files in the git index (default for pre-commit).")
    group.add_argument("--changed", metavar="BASE", help="Check files changed since BASE (e.g. origin/main).")
    group.add_argument("--all", action="store_true", help="Check every post-date SVG in assets/images/.")
    parser.add_argument("paths", nargs="*", help="Explicit file paths to check (overrides selector flags).")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any WARN (default warn-only).")
    args = parser.parse_args()

    if args.paths:
        targets = [Path(p) if Path(p).is_absolute() else REPO / p for p in args.paths]
    elif args.all:
        targets = collect_all()
    elif args.changed:
        targets = collect_changed(args.changed)
    else:
        # Default: --staged
        targets = collect_staged()

    if not targets:
        return 0

    warnings: List[str] = []
    for svg in targets:
        warnings.extend(check_one(svg))

    if warnings:
        for w in warnings:
            print(w)
        print(
            f"[svg-gate] {len(warnings)} file(s) outside their expected size band.\n"
            "           Bands (std / hq / rollup):\n"
            f"             std   : {BANDS['std'][0]}-{BANDS['std'][1]} bytes\n"
            f"             hq    : {BANDS['hq'][0]}-{BANDS['hq'][1]} bytes\n"
            f"             rollup: {BANDS['rollup'][0]}-{BANDS['rollup'][1]} bytes"
        )
        return 1 if args.strict else 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
