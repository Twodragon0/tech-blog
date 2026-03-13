#!/usr/bin/env python3
"""
Cleanup script for news-card blog posts:
1. Remove `> **출처**` / `> 출처:` lines from files that contain news-card.html
2. Strip markdown bold (**...**) from summary= and title= in news-card includes
3. Clean up consecutive blank lines left after removal

Idempotent: running twice produces the same result.
"""

import glob
import os
import re
import sys


def strip_bold_in_param(match_obj):
    """Remove ** markers from a matched parameter value."""
    prefix = match_obj.group(1)  # e.g., summary=" or title="
    value = match_obj.group(2)  # the content between quotes
    suffix = match_obj.group(3)  # closing "
    cleaned = value.replace("**", "")
    return prefix + cleaned + suffix


def process_file(filepath):
    """Process a single markdown file. Returns (chulcheo_removed, bold_cleaned)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Only process files that contain news-card.html
    if "news-card.html" not in content:
        return 0, 0

    lines = content.split("\n")
    original_line_count = len(lines)

    # --- Cleanup 1: Remove > **출처** / > 출처: lines ---
    chulcheo_removed = 0
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Match lines starting with > that contain 출처
        if re.match(r"^>\s*(\*\*)?출처(\*\*)?", stripped):
            chulcheo_removed += 1
            # Also check if the previous line is an empty blockquote (just ">")
            # and remove it if so
            if new_lines and new_lines[-1].strip() in (">", ""):
                prev = new_lines[-1].strip()
                if prev == ">":
                    new_lines.pop()
            i += 1
            continue

        new_lines.append(line)
        i += 1

    # --- Clean up consecutive blank lines (max 2 newlines = 1 blank line between content) ---
    cleaned_lines = []
    consecutive_blank = 0
    for line in new_lines:
        if line.strip() == "":
            consecutive_blank += 1
            if consecutive_blank <= 2:
                cleaned_lines.append(line)
        else:
            consecutive_blank = 0
            cleaned_lines.append(line)

    content = "\n".join(cleaned_lines)

    # --- Cleanup 2: Strip ** from summary= and title= in news-card blocks ---
    # Match news-card include blocks
    bold_cleaned = 0

    # Pattern to find summary="..." and title="..." parameters
    # These can contain escaped quotes and other content
    def clean_param(param_name, text):
        nonlocal bold_cleaned
        # Match param="value" where value may contain **
        pattern = rf'({param_name}=")((?:[^"\\]|\\.)*)(")'

        def replacer(m):
            nonlocal bold_cleaned
            prefix, value, suffix = m.group(1), m.group(2), m.group(3)
            if "**" in value:
                count = value.count("**")
                bold_cleaned += count
                return prefix + value.replace("**", "") + suffix
            return m.group(0)

        return re.sub(pattern, replacer, text)

    # Only clean bold markers inside news-card blocks
    # Find each news-card block and clean within it
    def clean_news_card_block(match):
        block = match.group(0)
        block = clean_param("summary", block)
        block = clean_param("title", block)
        return block

    # Match {% include news-card.html ... %} blocks (potentially multi-line)
    content = re.sub(
        r"\{%-?\s*include\s+news-card\.html\s.*?-?%\}",
        clean_news_card_block,
        content,
        flags=re.DOTALL,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return chulcheo_removed, bold_cleaned


def main():
    posts_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_posts"
    )
    files = sorted(glob.glob(os.path.join(posts_dir, "2026-*.md")))

    if not files:
        print("No 2026-*.md files found in _posts/")
        sys.exit(1)

    total_chulcheo = 0
    total_bold = 0
    files_modified = 0

    print(f"Processing {len(files)} files...\n")

    for filepath in files:
        filename = os.path.basename(filepath)
        chulcheo, bold = process_file(filepath)

        if chulcheo > 0 or bold > 0:
            files_modified += 1
            print(f"  {filename}")
            if chulcheo > 0:
                print(f"    - Removed {chulcheo} 출처 lines")
            if bold > 0:
                print(f"    - Cleaned {bold} bold markers (**)")

        total_chulcheo += chulcheo
        total_bold += bold

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Files modified:  {files_modified}")
    print(f"  출처 lines removed: {total_chulcheo}")
    print(f"  Bold markers cleaned: {total_bold}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
