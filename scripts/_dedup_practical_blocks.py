#!/usr/bin/env python3
"""One-shot cleanup: remove duplicate '#### 실무 적용 포인트' blocks from a post.

The pre-2026-06-24 generator could emit the IDENTICAL 3-bullet block in two
different news-item sections (the _pick_variant collision fixed in 4400c901).
This surgically drops every REPEAT of an already-seen block (header + its
blank lines + bullet lines), keeping the first occurrence and everything else
untouched. Use --dry-run to preview. Idempotent.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HEADER = "#### 실무 적용 포인트"


def _blocks(lines):
    """Yield (start, end, body_key) for each practical-point block.

    A block = the HEADER line, any blank lines right after it, and the run of
    consecutive '- ' bullet lines. ``end`` is exclusive. ``body_key`` is the
    tuple of bullet texts (order-independent) used to detect duplicates.
    """
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].strip() == HEADER:
            j = i + 1
            while j < n and lines[j].strip() == "":
                j += 1
            bullets = []
            while j < n and lines[j].lstrip().startswith("- "):
                bullets.append(lines[j].strip())
                j += 1
            # absorb a single trailing blank so removal leaves no double gap
            end = j
            if end < n and lines[end].strip() == "":
                end += 1
            yield (i, end, tuple(sorted(bullets)))
            i = end
        else:
            i += 1


def dedup(text: str, overlap: int = 2):
    """Remove a practical-point block when it is redundant with an earlier one.

    Redundant = its full bullet set already appeared (exact duplicate) OR it
    shares >= ``overlap`` bullets with bullets seen in earlier blocks (the
    _pick_variant collision repeats the same 2-3 advice bullets across two
    different news items, even when the per-item context/impact bullets differ).
    The first occurrence is always kept.
    """
    lines = text.split("\n")
    seen_blocks = set()
    seen_bullets: set = set()
    drop = set()
    removed = 0
    for start, end, key in _blocks(lines):
        if not key:
            continue
        bullets = set(key)
        is_exact = key in seen_blocks
        shared = len(bullets & seen_bullets)
        if is_exact or shared >= overlap:
            drop.update(range(start, end))
            removed += 1
        else:
            seen_blocks.add(key)
            seen_bullets |= bullets
    if not drop:
        return text, 0
    kept = [ln for idx, ln in enumerate(lines) if idx not in drop]
    return "\n".join(kept), removed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="+", help="post .md files")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overlap", type=int, default=2,
                    help="drop a block sharing >= N bullets with earlier blocks")
    args = ap.parse_args()
    rc = 0
    for p in args.paths:
        path = Path(p)
        if not path.exists():
            print(f"MISSING {p}")
            rc = 1
            continue
        text = path.read_text(encoding="utf-8")
        new, removed = dedup(text, overlap=args.overlap)
        if removed == 0:
            print(f"OK     {path.name}: no duplicate blocks")
            continue
        if args.dry_run:
            print(f"WOULD  {path.name}: remove {removed} duplicate block(s)")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"FIXED  {path.name}: removed {removed} duplicate block(s)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
