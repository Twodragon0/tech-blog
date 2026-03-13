#!/usr/bin/env python3
"""
fix_missing_front_matter_close.py

Fixes Jekyll posts that are missing the closing `---` after YAML front matter.

Problem structure:
  ---
  (YAML fields)
  {%- include ai-summary-card.html ...  ← Liquid starts without closing ---

Fixed structure:
  ---
  (YAML fields)
  ---
  {%- include ai-summary-card.html ...

Usage:
  python3 scripts/fix_missing_front_matter_close.py              # dry-run all posts
  python3 scripts/fix_missing_front_matter_close.py --fix        # apply fixes
  python3 scripts/fix_missing_front_matter_close.py path/to/post.md       # dry-run one file
  python3 scripts/fix_missing_front_matter_close.py --fix path/to/post.md # fix one file
"""

import os
import sys
import re
import argparse
from pathlib import Path


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def is_yaml_line(line: str) -> bool:
    """Return True if the line looks like valid YAML front matter content."""
    stripped = line.rstrip('\n')

    # blank line is ambiguous — we treat it as YAML-compatible (continuation gap)
    # but we'll use it as a soft signal in the caller
    if stripped == '':
        return True  # tolerate blank lines inside YAML

    # YAML key: value  (e.g. "title: foo", "layout: post")
    if re.match(r'^[A-Za-z_][A-Za-z0-9_\-]*\s*:', stripped):
        return True

    # YAML list item  (e.g. "- security")
    if re.match(r'^\s*-\s+', stripped):
        return True

    # Continuation indent (multi-line scalar, e.g. description block)
    if re.match(r'^[ \t]+\S', stripped):
        return True

    return False


def is_liquid_or_content_start(line: str) -> bool:
    """Return True if the line marks the beginning of post content (not YAML)."""
    stripped = line.rstrip('\n')

    # Liquid tags: {% ... %} or {%- ... -%}
    if stripped.startswith('{%') or stripped.startswith('{%-'):
        return True

    # Markdown heading
    if stripped.startswith('#'):
        return True

    # HTML tags (sometimes used directly after front matter)
    if stripped.startswith('<') and not stripped.startswith('<!--'):
        return True

    # Explicit horizontal rule used as separator (three or more dashes)
    # But we only treat standalone --- as "content" if we've already passed YAML
    # (handled in the caller)

    return False


def find_insertion_point(lines: list[str]) -> int | None:
    """
    Scan lines (0-indexed) starting from line index 1 (after opening ---).

    Returns the 0-based index where `---\\n` should be INSERTED (i.e. the line
    currently at that index will be shifted down).

    Returns None if the file already has a proper closing --- within 60 lines,
    or if we cannot determine a safe insertion point.
    """
    if not lines:
        return None

    # Line 0 must be the opening ---
    if lines[0].rstrip('\n') != '---':
        return None

    # Check if there is already a closing --- within the first 60 lines
    for i in range(1, min(61, len(lines))):
        line = lines[i].rstrip('\n')
        if line == '---':
            return None  # already properly closed

        # If we hit Liquid/content before finding ---, we need to insert
        if is_liquid_or_content_start(lines[i]):
            # Walk backwards to find last non-blank YAML line
            insert_at = i  # default: insert right before this line
            # Look back for the last substantive YAML line
            j = i - 1
            while j >= 1 and lines[j].strip() == '':
                j -= 1
            # Insert after that last YAML line (and after any trailing blanks)
            # We want: last_yaml_line \n ---\n \n liquid_line
            # So insertion index = j + 1
            insert_at = j + 1
            return insert_at

    # Scanned 60 lines without finding either --- or Liquid — skip
    return None


def build_diff_preview(lines: list[str], insert_at: int, filepath: str) -> str:
    """Return a human-readable diff-like preview of the change."""
    context = 3
    start = max(0, insert_at - context)
    end = min(len(lines), insert_at + context)

    parts = [f"  File: {filepath}"]
    parts.append(f"  Inserting '---' at line {insert_at + 1} (1-indexed)\n")

    for i in range(start, insert_at):
        parts.append(f"   {i+1:4d}  {lines[i].rstrip()}")

    parts.append(f"  +{insert_at+1:4d}  ---   ← inserted")

    for i in range(insert_at, end):
        parts.append(f"   {i+1:4d}  {lines[i].rstrip()}")

    return '\n'.join(parts)


def process_file(filepath: str, fix: bool) -> tuple[str, str | None]:
    """
    Process a single file.

    Returns (status, detail) where status is one of:
      'ok'      — already has proper front matter closing
      'fixed'   — was fixed (only in --fix mode)
      'would_fix' — would be fixed (dry-run)
      'skipped' — no opening ---, not a Jekyll post
      'error'   — read/write error
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
    except OSError as e:
        return ('error', str(e))

    if not lines or lines[0].rstrip('\n') != '---':
        return ('skipped', 'no opening ---')

    insert_at = find_insertion_point(lines)

    if insert_at is None:
        return ('ok', None)

    preview = build_diff_preview(lines, insert_at, filepath)

    if fix:
        new_lines = lines[:insert_at] + ['---\n'] + lines[insert_at:]
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
        except OSError as e:
            return ('error', str(e))
        return ('fixed', preview)
    else:
        return ('would_fix', preview)


def collect_posts(posts_dir: str) -> list[str]:
    """Return sorted list of .md file paths in posts_dir."""
    p = Path(posts_dir)
    if not p.is_dir():
        return []
    return sorted(str(f) for f in p.glob('*.md'))


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Fix Jekyll posts missing the closing --- after YAML front matter.'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        default=False,
        help='Apply fixes (default: dry-run only)',
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Specific .md files to process (default: all files in _posts/)',
    )
    args = parser.parse_args()

    # Resolve file list
    if args.files:
        filepaths = [os.path.abspath(f) for f in args.files]
    else:
        repo_root = Path(__file__).resolve().parent.parent
        posts_dir = repo_root / '_posts'
        filepaths = collect_posts(str(posts_dir))

    if not filepaths:
        print('No files found to process.')
        sys.exit(0)

    mode_label = 'FIX MODE' if args.fix else 'DRY-RUN MODE'
    print(f'\n=== fix_missing_front_matter_close.py  [{mode_label}] ===\n')

    counts = {'ok': 0, 'fixed': 0, 'would_fix': 0, 'skipped': 0, 'error': 0}
    previews = []

    for fp in filepaths:
        status, detail = process_file(fp, fix=args.fix)
        counts[status] += 1

        short = os.path.basename(fp)
        if status == 'ok':
            pass  # silent for clean files
        elif status in ('fixed', 'would_fix'):
            verb = 'FIXED' if status == 'fixed' else 'WOULD FIX'
            print(f'[{verb}] {short}')
            if detail:
                previews.append(detail)
        elif status == 'skipped':
            print(f'[SKIP]  {short}  ({detail})')
        elif status == 'error':
            print(f'[ERROR] {short}  ({detail})')

    # Print diff previews
    if previews:
        print('\n' + '─' * 70)
        print('CHANGE PREVIEWS:')
        print('─' * 70)
        for prev in previews:
            print(prev)
            print()

    # Summary
    total = len(filepaths)
    print('─' * 70)
    print('SUMMARY:')
    print(f'  Total files   : {total}')
    print(f'  Already OK    : {counts["ok"]}')
    print(f'  Skipped       : {counts["skipped"]}')
    if args.fix:
        print(f'  Fixed         : {counts["fixed"]}')
    else:
        print(f'  Would fix     : {counts["would_fix"]}')
        if counts['would_fix'] > 0:
            print(f'\n  Run with --fix to apply changes.')
    if counts['error']:
        print(f'  Errors        : {counts["error"]}')
    print()


if __name__ == '__main__':
    main()
