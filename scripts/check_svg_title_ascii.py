#!/usr/bin/env python3
"""SVG <title>/<desc> ASCII gate — rejects non-ASCII codepoints.

Positive-rule check: every character in <title> and <desc> element content
MUST have codepoint < 128 (strict ASCII). This catches residue that the
Hangul-only denylist missed (e.g. U+00B7 middle-dot, U+2022 bullet).

Usage:
    python3 scripts/check_svg_title_ascii.py --staged    # only git-cached SVGs
    python3 scripts/check_svg_title_ascii.py --all       # every assets/images/*.svg
    python3 scripts/check_svg_title_ascii.py path/a.svg path/b.svg
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator

REPO = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO / "assets" / "images"

# Match <title>...</title> and <desc>...</desc>, including multi-line content.
# The SVG namespace variant <svg:title> is not used in this project, so a
# simple tag name match is sufficient.
_ELEMENT_RE = re.compile(
    r"<(title|desc)(?:\s[^>]*)?>([^<]*)</(?:title|desc)>",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------

def _violations(path: Path) -> list[tuple[int, int, int, str, str]]:
    """Return list of (line, col, codepoint, char, context) for each violation.

    A violation is any character with ord(c) >= 128 inside a <title> or
    <desc> element.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    hits: list[tuple[int, int, int, str, str]] = []
    lines = text.splitlines(keepends=True)
    # Build a line-offset map so we can convert string offsets → (line, col).
    offsets: list[int] = []
    acc = 0
    for ln in lines:
        offsets.append(acc)
        acc += len(ln)

    for m in _ELEMENT_RE.finditer(text):
        content = m.group(2)
        content_start = m.start(2)  # absolute offset of content start
        for rel, ch in enumerate(content):
            if ord(ch) >= 128:
                abs_off = content_start + rel
                # Binary-search offsets to find line number.
                line_idx = _offset_to_line(offsets, abs_off)
                col = abs_off - offsets[line_idx]
                # Context: up to 30 chars around the bad char.
                ctx_start = max(0, rel - 15)
                ctx_end = min(len(content), rel + 16)
                context = repr(content[ctx_start:ctx_end])
                hits.append((line_idx + 1, col + 1, ord(ch), ch, context))
    return hits


def _offset_to_line(offsets: list[int], target: int) -> int:
    """Return 0-based line index for absolute character offset."""
    lo, hi = 0, len(offsets) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offsets[mid] <= target:
            lo = mid
        else:
            hi = mid - 1
    return lo


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def _staged_svg_paths() -> list[Path]:
    """Return staged assets/images/*.svg paths from the git index."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=str(REPO),
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths = []
    for line in out.splitlines():
        p = line.strip()
        if re.match(r"^assets/images/[^/]+\.svg$", p):
            full = REPO / p
            if full.exists():
                paths.append(full)
    return sorted(paths)


def _all_svg_paths() -> list[Path]:
    """Return all *.svg files under assets/images/."""
    return sorted(IMAGES_DIR.glob("*.svg"))


def _explicit_paths(args: list[str]) -> list[Path]:
    """Resolve explicit file paths (absolute or relative to cwd/repo)."""
    paths = []
    for a in args:
        p = Path(a)
        if not p.is_absolute():
            p = Path.cwd() / p
            if not p.exists():
                p = REPO / a
        if p.exists():
            paths.append(p)
        else:
            print(f"[title-ascii] WARNING: file not found: {a}", file=sys.stderr)
    return paths


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reject non-ASCII chars in SVG <title>/<desc> elements."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Only check files in git staging area (assets/images/*.svg).",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Check every SVG under assets/images/.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Explicit SVG file paths to check.",
    )
    args = parser.parse_args()

    if args.staged:
        files = _staged_svg_paths()
    elif args.all:
        files = _all_svg_paths()
    elif args.paths:
        files = _explicit_paths(args.paths)
    else:
        # Default: behave like --all so bare invocation is useful.
        files = _all_svg_paths()

    if not files:
        print("[title-ascii] No SVG files to check.")
        sys.exit(0)

    total_violations = 0
    for path in files:
        hits = _violations(path)
        if hits:
            rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
            for line, col, cp, ch, context in hits:
                print(
                    f"{rel}:{line}:{col} char=U+{cp:04X} ({ch!r}) context={context}",
                    file=sys.stderr,
                )
            total_violations += len(hits)

    if total_violations:
        print(
            f"\n[title-ascii] FAIL — {total_violations} non-ASCII codepoint(s) in "
            f"<title>/<desc> elements. All content must be ASCII (codepoint < 128).",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[title-ascii] OK — {len(files)} file(s) checked, 0 violations.")
    sys.exit(0)


if __name__ == "__main__":
    main()
