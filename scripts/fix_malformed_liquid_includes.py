#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


def fix_content(content: str) -> tuple[str, int]:
    fixed = content
    changes = 0

    patterns = [
        ("{%% include", "{% include"),
        ("%%}", "%}"),
    ]

    for old, new in patterns:
        count = fixed.count(old)
        if count:
            fixed = fixed.replace(old, new)
            changes += count

    return fixed, changes


def process_file(path: Path, write: bool) -> int:
    original = path.read_text(encoding="utf-8")
    fixed, changes = fix_content(original)
    if changes and write:
        path.write_text(fixed, encoding="utf-8")
    return changes


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fix malformed Liquid include tags")
    parser.add_argument(
        "--path",
        default="_posts",
        help="target posts directory (default: _posts)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="check only; exit 1 if malformed tags are found",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path)
    if not root.exists():
        print(f"skip: path not found: {root}")
        return 0

    total_files = 0
    total_changes = 0
    files_with_changes = 0

    for post in sorted(root.glob("*.md")):
        changes = process_file(post, write=not args.check)
        total_files += 1
        if changes:
            files_with_changes += 1
            total_changes += changes
            print(f"{post}: fixed {changes} malformed include tokens")

    if files_with_changes == 0:
        print(f"ok: scanned {total_files} files; no malformed include tags")
        return 0

    print(
        f"{'detected' if args.check else 'fixed'}: {files_with_changes} files, {total_changes} tokens"
    )
    return 1 if args.check else 0


if __name__ == "__main__":
    raise SystemExit(main())
