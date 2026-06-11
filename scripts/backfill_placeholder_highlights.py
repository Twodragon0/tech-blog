#!/usr/bin/env python3
"""Backfill ``summary_card.highlights`` for legacy digests that carry the
``"포인트 N"`` placeholder source, using the REAL ``(source, title)`` rows from
the post's body highlights table.

Context: the digest generator already emits real sources (see
``scripts/news/content_generator.py``); ``포인트 N`` only survives in ~24 legacy
Feb-Mar 2026 posts whose ``summary_card.highlights`` were placeholders. This is a
one-off, idempotent data backfill — it does NOT touch the generator.

- Idempotent: a post WITHOUT the ``포인트 N`` marker is skipped unchanged.
- Surgical: only the ``  highlights:`` block inside the front matter is replaced;
  every other byte of the file is preserved.
- Safe: skips (does not fabricate) any post whose body table yields no usable row.

Usage:
    python3 scripts/backfill_placeholder_highlights.py            # dry-run (default)
    python3 scripts/backfill_placeholder_highlights.py --apply    # write changes
    python3 scripts/backfill_placeholder_highlights.py --apply path/to/post.md ...
"""
from __future__ import annotations

import argparse
import glob
import re
import sys
from typing import List, Optional, Tuple

# The highlights table opens with a (category, source) header — current
# "분야 | 소스 | …" or legacy "카테고리 | 출처 | …". Parsing is anchored to the
# contiguous rows after this header (mirrors l20_dispatch._digest_table_panels)
# so secondary body tables are never read.
_HEADER_RE = re.compile(r"^\|\s*(?:분야|카테고리)\s*\|\s*(?:소스|출처)\s*\|")
_ROW_RE = re.compile(r"^\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|([^|\n]*)\|\s*$")
_PLACEHOLDER_RE = re.compile(r'source:\s*"포인트\s*\d+"')
_SEP_CHARS = set("-: ")
# Capture the front matter WITH its trailing newline (group 2 ends in "\n") so
# the last highlights item line keeps the newline the block regex needs.
_FRONT_MATTER_RE = re.compile(r"^(---\n)(.*?\n)(---\n)(.*)$", re.DOTALL)
# Within the front matter, the highlights block: the `  highlights:` line plus
# its more-indented list items, up to (not including) the next 2-space sibling
# key or a less-indented line.
_HIGHLIGHTS_BLOCK_RE = re.compile(
    r"(?m)^(?P<head>  highlights:[ \t]*\n)(?P<items>(?:    .*\n|      .*\n|\n)*)"
)


def has_placeholder(text: str) -> bool:
    """True iff the post still carries a ``포인트 N`` placeholder source."""
    return bool(_PLACEHOLDER_RE.search(text))


def extract_real_highlights(body: str, limit: int = 3) -> List[Tuple[str, str]]:
    """Up to ``limit`` ``(source, title)`` pairs from the body highlights table.

    Anchored to the highlights table; skips the header/separator and any row
    with an empty source/title or an empty severity column. Returns the raw
    Korean title and real source (highlights are displayed on-page, not on the
    ASCII-only cover, so Korean is fine here)."""
    out: List[Tuple[str, str]] = []
    in_table = False
    for line in body.splitlines():
        if not in_table:
            if _HEADER_RE.match(line):
                in_table = True
            continue
        m = _ROW_RE.match(line)
        if not m:
            break  # blank / non-table line ends the highlights table
        col1, source, title, col4 = (c.strip() for c in m.groups())
        if set(col1) <= _SEP_CHARS:  # |---|---| separator row
            continue
        if not source or not title or set(col4) <= _SEP_CHARS:
            continue
        out.append((source, title))
        if len(out) >= limit:
            break
    return out


def _yaml_dq(s: str) -> str:
    """A YAML double-quoted scalar (escape backslash, double-quote, and control
    chars so it always round-trips). Table rows are single-line, so control
    chars are not expected — escaped only for robustness if reused."""
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    s = s.replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    return '"' + s + '"'


def render_highlights_block(highlights: List[Tuple[str, str]]) -> str:
    """The replacement ``  highlights:`` YAML block (flow-style items, matching
    the existing post format), with a trailing newline."""
    lines = ["  highlights:"]
    for src, title in highlights:
        lines.append(f"    - {{ source: {_yaml_dq(src)}, title: {_yaml_dq(title)} }}")
    return "\n".join(lines) + "\n"


def backfill_text(text: str) -> Optional[str]:
    """Return the post text with placeholder highlights replaced by real ones,
    or ``None`` when nothing should change (no placeholder, no front matter, no
    highlights block, or no usable body-table row)."""
    fm_match = _FRONT_MATTER_RE.match(text)
    if not fm_match:
        return None
    open_d, front, close_d, body = fm_match.groups()
    # Gate on the FRONT MATTER only — a 포인트-like string in the body prose must
    # not trigger a front-matter rewrite (matches the "placeholder source" intent).
    if not has_placeholder(front) or not _HIGHLIGHTS_BLOCK_RE.search(front):
        return None
    highlights = extract_real_highlights(body)
    if not highlights:
        return None  # do not fabricate
    new_block = render_highlights_block(highlights)
    new_front = _HIGHLIGHTS_BLOCK_RE.sub(
        lambda _m: new_block, front, count=1
    )
    if new_front == front:
        return None
    return open_d + new_front + close_d + body


def _iter_targets(paths: List[str]) -> List[str]:
    if paths:
        return paths
    return sorted(glob.glob("_posts/2026-*.md"))


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", help="specific post files (default: all _posts)")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args(argv)

    changed, skipped_no_rows = [], []
    for path in _iter_targets(args.paths):
        try:
            text = open(path, encoding="utf-8").read()
        except OSError:
            continue
        if not has_placeholder(text):
            continue
        new_text = backfill_text(text)
        if new_text is None:
            skipped_no_rows.append(path)
            continue
        changed.append(path)
        # show the new highlights for review
        block = _HIGHLIGHTS_BLOCK_RE.search(_FRONT_MATTER_RE.match(new_text).group(2))
        print(f"\n{'[APPLY]' if args.apply else '[DRY-RUN]'} {path}")
        print((block.group(0) if block else "").rstrip())
        if args.apply:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)

    print(f"\n{'Applied' if args.apply else 'Would change'}: {len(changed)} post(s)")
    if skipped_no_rows:
        print(f"Skipped (placeholder but no usable body table): {len(skipped_no_rows)}")
        for p in skipped_no_rows:
            print(f"  - {p}")
    if not args.apply and changed:
        print("Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
