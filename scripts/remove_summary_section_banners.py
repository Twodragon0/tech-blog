#!/usr/bin/env python3
"""
Remove section banner SVG images that appear before NON-content (summary/reference) sections.
These banners should NOT appear before summary/reference headings like:
- ## 6. 기타 주목할 뉴스, ## 6. 기타
- ## 7. 트렌드 분석, ## 7. 트렌드
- ## 실무 체크리스트, ## 실무 액션
- ## 참고 자료, ## 참고 링크
- ## Checklist
- Any ## heading containing: 체크리스트, 참고, 기타 주목, 트렌드 분석
"""

import re
import os
from pathlib import Path

POSTS_DIR = Path("/Users/yong/Desktop/tech-blog/_posts")

# Pattern to match section banner lines
BANNER_PATTERN = re.compile(r'^!\[.*?\]\(/assets/images/section-.*?\.svg\)\s*$')

# Keywords that indicate a NON-content (summary/reference) heading
SUMMARY_HEADING_PATTERNS = [
    re.compile(r'^## \d+\. 기타 주목할 뉴스'),
    re.compile(r'^## \d+\. 기타\b'),
    re.compile(r'^## \d+\. 트렌드 분석'),
    re.compile(r'^## \d+\. 트렌드\b'),
    re.compile(r'^## 실무 체크리스트'),
    re.compile(r'^## 실무 액션'),
    re.compile(r'^## 참고 자료'),
    re.compile(r'^## 참고 링크'),
    re.compile(r'^## Checklist'),
    # Generic patterns: any ## heading containing these keywords
    re.compile(r'^## .*체크리스트'),
    re.compile(r'^## .*참고'),
    re.compile(r'^## .*기타 주목'),
    re.compile(r'^## .*트렌드 분석'),
]


def is_summary_heading(line: str) -> bool:
    """Check if a line is a summary/reference section heading."""
    line = line.strip()
    for pattern in SUMMARY_HEADING_PATTERNS:
        if pattern.match(line):
            return True
    return False


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """
    Process a single markdown file, removing banner lines before summary headings.
    Returns number of banners removed.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    removed_count = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line is a section banner
        if BANNER_PATTERN.match(line.rstrip('\n')):
            # Look ahead for the next non-blank line
            j = i + 1
            blank_lines_after = []
            while j < len(lines) and lines[j].strip() == '':
                blank_lines_after.append(lines[j])
                j += 1

            # Check if the next non-blank line is a summary heading
            if j < len(lines) and is_summary_heading(lines[j]):
                # Remove the banner line and blank lines between it and the heading
                # Keep exactly one blank line before the heading
                removed_count += 1
                # Add one blank line before heading (for spacing), then skip to heading
                new_lines.append('\n')
                i = j  # Skip banner + blank lines, let the heading be processed next iteration
                continue

        new_lines.append(line)
        i += 1

    if removed_count > 0 and not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    return removed_count


def main():
    dry_run = False  # Set to True to preview changes without writing

    total_removed = 0
    files_modified = 0

    md_files = sorted(POSTS_DIR.glob("*.md"))
    print(f"Processing {len(md_files)} markdown files in {POSTS_DIR}...")
    print()

    for filepath in md_files:
        count = process_file(filepath, dry_run=dry_run)
        if count > 0:
            files_modified += 1
            total_removed += count
            print(f"  [{count} removed] {filepath.name}")

    print()
    print(f"Summary: {total_removed} banner(s) removed across {files_modified} file(s).")
    if dry_run:
        print("(DRY RUN - no files were modified)")


if __name__ == "__main__":
    main()
