#!/usr/bin/env python3
"""CI gate: assert 3 visually-distinct primitives across L22 ultra digest covers.

Each auto-published L22 cover must contain exactly 3 ``<!-- band-visual: {kind} -->``
comment markers (one per band) with all-distinct kind values.

Files that pre-date the marker injection (legacy covers) emit a WARN and are
excluded from the failure count, so the gate is forward-only.

Exit codes:
    0  All covers with markers pass the 3-distinct check.
    1  One or more covers fail the distinct-primitives assertion.

Usage:
    python3 scripts/check_l22_visual_variety.py --all
    python3 scripts/check_l22_visual_variety.py --glob 'assets/images/2026-05-*.svg'
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

_MARKER_RE = re.compile(r"<!--\s*band-visual:\s*(\w+)\s*-->")

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GLOB = "assets/images/2026-*-Tech_Security_Weekly_Digest_*.svg"


def _extract_markers(path: Path) -> Optional[List[str]]:
    """Return list of visual kind strings from ``<!-- band-visual: ... -->`` comments.

    Returns ``None`` when the file cannot be read.
    Returns ``[]`` when the file contains no markers (legacy cover).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    return _MARKER_RE.findall(text)


def check_file(path: Path) -> Tuple[str, Optional[str]]:
    """Check one SVG file.

    Returns:
        (status, message) where status is one of ``"PASS"``, ``"FAIL"``, ``"WARN"``.
        ``message`` is ``None`` on PASS, a human-readable string otherwise.
    """
    markers = _extract_markers(path)
    if markers is None:
        return "FAIL", f"cannot read file: {path}"

    if not markers:
        return "WARN", f"no band-visual markers (legacy cover — skipping): {path.name}"

    if len(markers) != 3:
        return "FAIL", (
            f"expected 3 band-visual markers, got {len(markers)} "
            f"({', '.join(markers)}): {path.name}"
        )

    if len(set(markers)) != 3:
        dupes = [k for k in markers if markers.count(k) > 1]
        return "FAIL", (
            f"duplicate primitives {dupes} — bands must be visually distinct "
            f"({', '.join(markers)}): {path.name}"
        )

    return "PASS", None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--all", action="store_true", help="Scan all L22 digest covers under assets/images/")
    group.add_argument("--glob", metavar="PATTERN", help="Glob pattern relative to repo root")
    p.add_argument("--quiet", action="store_true", help="Suppress PASS lines; only print WARN/FAIL")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    if args.all:
        pattern = DEFAULT_GLOB
        base = REPO_ROOT
    elif args.glob:
        pattern = args.glob
        # Resolve --glob relative to cwd so tests can point at tmp_path fixtures.
        base = Path.cwd()
    else:
        pattern = DEFAULT_GLOB
        base = REPO_ROOT

    paths = sorted(base.glob(pattern))

    if not paths:
        print(f"WARN: no files matched pattern '{pattern}'")
        return 0

    total = len(paths)
    with_markers = 0
    passes = 0
    failures: List[str] = []
    warnings: List[str] = []

    for path in paths:
        status, msg = check_file(path)
        if status == "PASS":
            passes += 1
            with_markers += 1
            if not args.quiet:
                print(f"PASS  {path.name}")
        elif status == "WARN":
            warnings.append(msg or path.name)
            print(f"WARN  {msg}")
        else:
            with_markers += 1  # file has markers, just wrong count/dupes
            failures.append(msg or path.name)
            print(f"FAIL  {msg}")

    # Summary line — always printed for CI log parsing.
    marker_ratio = f"{with_markers}/{total}"
    print(
        f"\n--- L22 visual-variety gate: {passes} pass, "
        f"{len(failures)} fail, {len(warnings)} warn "
        f"(covers with markers: {marker_ratio}) ---"
    )

    if failures:
        print("\nFailed covers:")
        for f in failures:
            print(f"  {f}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
