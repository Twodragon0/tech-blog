#!/usr/bin/env python3
"""Strip '실무 포인트' filler from blog posts.

Removes two forms (per 2026-07-14 editorial decision):
  1. Inline one-liners:  `**실무 포인트**: ...` and plain `실무 포인트: ...`
  2. Heading sections:   `#### 실무 적용 포인트` / `## 실무 포인트` (bare-label
     headings) together with their body, up to the next heading / `---` /
     `{% ... %}` / table / EOF.

PRESERVES table columns that merely *name* a `실무 적용 포인트` column
(lines starting with `|`) — those carry real per-row analysis.

Idempotent. Collapses runs of blank lines left behind to a single blank line.

Usage:
  python3 scripts/dev/strip_practical_points.py [--check] [PATHS...]
    --check  : report what would change, exit 1 if any file would change,
               make no edits (for CI regression gating).
  Default PATHS = _posts/*.md
"""
from __future__ import annotations

import glob
import re
import sys

# A heading whose entire label is (optionally bolded) 실무[ 적용] 포인트.
SECTION_TITLE_RE = re.compile(r"^\s*#{1,6}\s*\*{0,2}\s*실무\s*(?:적용\s*)?포인트\s*\*{0,2}\s*$")
# An inline one-liner: optional bold wrapper, then a colon.
INLINE_RE = re.compile(r"^\s*\*{0,2}\s*실무\s*(?:적용\s*)?포인트\s*\*{0,2}\s*:")
# Boundaries that terminate a removed heading section.
BOUNDARY_RE = re.compile(r"^\s*(?:#{1,6}\s|---\s*$|\{%|\{{)")


def strip_text(text: str) -> tuple[str, int, int]:
    lines = text.split("\n")
    out: list[str] = []
    i, n = 0, len(lines)
    removed_inline = removed_sections = 0
    while i < n:
        line = lines[i]
        s = line.strip()
        if s.startswith("|"):  # never touch table rows
            out.append(line)
            i += 1
            continue
        if SECTION_TITLE_RE.match(line):
            removed_sections += 1
            i += 1
            while i < n:
                bs = lines[i].strip()
                if bs.startswith("|") or BOUNDARY_RE.match(lines[i]):
                    break
                i += 1
            continue
        if INLINE_RE.match(line):
            removed_inline += 1
            i += 1
            continue
        out.append(line)
        i += 1

    # Nothing removed → return original untouched (don't reformat unrelated files).
    if removed_inline == 0 and removed_sections == 0:
        return text, 0, 0

    # collapse 2+ consecutive blank lines to a single blank line
    collapsed: list[str] = []
    prev_blank = False
    for l in out:
        blank = l.strip() == ""
        if blank and prev_blank:
            continue
        collapsed.append(l)
        prev_blank = blank
    return "\n".join(collapsed), removed_inline, removed_sections


def main(argv: list[str]) -> int:
    check = "--check" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        paths = sorted(glob.glob("_posts/*.md"))

    changed = 0
    tot_inline = tot_sections = 0
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        new, ri, rs = strip_text(original)
        if new != original:
            changed += 1
            tot_inline += ri
            tot_sections += rs
            if check:
                print(f"WOULD CHANGE {path}: -{ri} inline, -{rs} section(s)")
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                print(f"cleaned {path}: -{ri} inline, -{rs} section(s)")

    verb = "would change" if check else "changed"
    print(f"\n{changed} file(s) {verb}; removed {tot_inline} inline + {tot_sections} heading-section(s).")
    if check and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
