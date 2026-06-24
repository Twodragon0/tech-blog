#!/usr/bin/env python3
"""One-shot cleanup: remove duplicate '#### 실무 적용 포인트' blocks from posts.

Thin wrapper around the canonical fixer in ``check_posts`` so there is a single
implementation. The pre-2026-06-24 generator could emit the same advice block in
two news-item sections (the _pick_variant collision fixed in 4400c901). Prefer
``python3 scripts/check_posts.py --fix`` for the integrated path; this remains
for targeting specific files with a dry-run preview.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_posts import fix_duplicate_practical_points  # noqa: E402


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
        new, removed = fix_duplicate_practical_points(
            path.read_text(encoding="utf-8"), overlap=args.overlap
        )
        if removed == 0:
            print(f"OK     {path.name}: no duplicate blocks")
        elif args.dry_run:
            print(f"WOULD  {path.name}: remove {removed} duplicate block(s)")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"FIXED  {path.name}: removed {removed} duplicate block(s)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
