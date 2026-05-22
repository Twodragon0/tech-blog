#!/usr/bin/env python3
"""Add last_modified_at front-matter to Jekyll posts using git log timestamps.

Usage:
    python3 scripts/add_last_modified_at.py --dry-run   # preview only (default)
    python3 scripts/add_last_modified_at.py --commit    # actually write files
"""

import argparse
import glob
import os
import re
import subprocess
import sys
from datetime import datetime, timezone


def get_git_last_modified(filepath: str) -> str | None:
    """Return the last commit ISO 8601 timestamp for the given file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        ts = result.stdout.strip()
        return ts if ts else None
    except subprocess.CalledProcessError:
        return None


def parse_iso8601(ts: str) -> datetime | None:
    """Parse an ISO 8601 timestamp string to an aware datetime."""
    # Handle +09:00 style offsets that fromisoformat may not support pre-3.11
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def extract_frontmatter_bounds(content: str) -> tuple[int, int] | None:
    """Return (start_line_idx, end_line_idx) of the YAML front matter block.

    Returns None if no valid front matter found.
    Line indices are into content.splitlines().
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return (0, i)
    return None


def process_file(filepath: str, commit: bool, add_only: bool = False) -> tuple[str, bool]:
    """Process a single post file.

    Returns (status_message, was_changed).
    """
    git_ts = get_git_last_modified(filepath)
    if not git_ts:
        return (f"SKIP (no git history): {filepath}", False)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    bounds = extract_frontmatter_bounds(content)
    if bounds is None:
        return (f"SKIP (no front matter): {filepath}", False)

    _, fm_end = bounds
    lines = content.splitlines(keepends=True)

    # Check if last_modified_at already exists
    existing_match = re.search(
        r"^last_modified_at:\s*(.+)$", content, re.MULTILINE
    )

    if add_only and existing_match:
        return (
            f"SKIP (add-only, already present): {os.path.basename(filepath)}",
            False,
        )

    if existing_match:
        existing_val = existing_match.group(1).strip()
        existing_dt = parse_iso8601(existing_val)
        git_dt = parse_iso8601(git_ts)
        if existing_dt and git_dt:
            # Keep whichever is more recent (preserve manual edits)
            if existing_dt >= git_dt:
                return (
                    f"KEEP (manual newer): {os.path.basename(filepath)} → {existing_val}",
                    False,
                )
            # git timestamp is newer — update
            new_content = re.sub(
                r"^(last_modified_at:\s*)(.+)$",
                f"\\g<1>{git_ts}",
                content,
                count=1,
                flags=re.MULTILINE,
            )
            action = f"UPDATE {existing_val} → {git_ts}"
        else:
            # Cannot parse, leave it alone
            return (
                f"SKIP (unparseable date): {os.path.basename(filepath)}",
                False,
            )
    else:
        # Insert after `date:` line if found, otherwise before closing `---`
        date_match = re.search(r"^date:.*$", content, re.MULTILINE)
        if date_match:
            insert_pos = date_match.end()
            new_content = (
                content[:insert_pos]
                + f"\nlast_modified_at: {git_ts}"
                + content[insert_pos:]
            )
        else:
            # Insert before the closing --- of front matter
            fm_end_idx = None
            char_pos = 0
            line_count = 0
            for ch in content:
                if line_count == fm_end:
                    fm_end_idx = char_pos
                    break
                if ch == "\n":
                    line_count += 1
                char_pos += 1
            if fm_end_idx is None:
                return (f"SKIP (cannot find fm end): {filepath}", False)
            new_content = (
                content[:fm_end_idx]
                + f"last_modified_at: {git_ts}\n"
                + content[fm_end_idx:]
            )
        action = f"ADD {git_ts}"

    # Verify frontmatter is still valid (bounds still exist)
    check_bounds = extract_frontmatter_bounds(new_content)
    if check_bounds is None:
        return (f"ERROR (fm broken after edit): {filepath}", False)

    if commit:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)

    return (f"{action}: {os.path.basename(filepath)}", True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add last_modified_at front-matter to Jekyll posts."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview changes without writing (default behavior)",
    )
    parser.add_argument(
        "--commit",
        action="store_true",
        default=False,
        help="Actually write changes to files",
    )
    parser.add_argument(
        "--add-only",
        action="store_true",
        default=False,
        help="Only ADD the field to posts missing it; skip posts that already have last_modified_at",
    )
    args = parser.parse_args()

    # Default to dry-run unless --commit specified
    do_commit = args.commit and not args.dry_run

    posts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "_posts")
    post_files = sorted(glob.glob(os.path.join(posts_dir, "*.md")))

    if not post_files:
        print("No post files found.", file=sys.stderr)
        sys.exit(1)

    mode = "COMMIT" if do_commit else "DRY-RUN"
    print(f"Mode: {mode} | Posts found: {len(post_files)}\n")

    changed = 0
    skipped = 0
    kept = 0
    errors = 0

    for filepath in post_files:
        msg, was_changed = process_file(filepath, commit=do_commit, add_only=args.add_only)
        print(msg)
        if "ERROR" in msg:
            errors += 1
        elif was_changed:
            changed += 1
        elif "KEEP" in msg:
            kept += 1
        else:
            skipped += 1

    print(f"\n{'='*60}")
    print(f"Summary ({mode}):")
    print(f"  Changed/Added : {changed}")
    print(f"  Kept (manual) : {kept}")
    print(f"  Skipped       : {skipped}")
    print(f"  Errors        : {errors}")
    print(f"  Total posts   : {len(post_files)}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
