#!/usr/bin/env python3
"""
cleanup_bold_and_severity.py

Task 1: Remove severity blockquote lines (> 🔴 **심각도**: ... patterns)
Task 2: Strip **bold** markers from body text (not headings, code blocks, HTML, includes, captures)
Task 3: Remove > **출처** / > 출처 lines
"""

import re
import os
import glob
from pathlib import Path

POSTS_DIR = Path("/Users/yong/Desktop/tech-blog/_posts")

# --- Patterns ---

# Task 1: severity blockquote lines
SEVERITY_PATTERN = re.compile(
    r'^>\s*[🔴🟠🟡🟢🔵⚫⚪]\s*\*\*심각도\*\*'
)

# Task 3: 출처 lines
CHULCHEO_PATTERN = re.compile(
    r'^>\s*\*?\*?출처\*?\*?'
)


def is_heading(line: str) -> bool:
    return bool(re.match(r'^#{1,6}\s', line))


def is_html_line(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith('<') and not stripped.startswith('<!--')


def is_include_line(line: str) -> bool:
    stripped = line.strip()
    return '{%' in stripped and 'include' in stripped


def strip_bold(line: str) -> tuple[str, int]:
    """Remove ** bold markers from a line. Returns (new_line, count_removed)."""
    new_line, count = re.subn(r'\*\*', '', line)
    return new_line, count


def process_file(filepath: Path) -> dict:
    """Process a single markdown file. Returns stats dict."""
    text = filepath.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)

    result_lines = []
    stats = {
        'severity_removed': 0,
        'bold_cleaned': 0,
        'chulcheo_removed': 0,
        'modified': False,
    }

    in_code_block = False
    in_capture_block = False
    in_front_matter = False
    front_matter_count = 0

    i = 0
    while i < len(lines):
        raw = lines[i]
        line = raw.rstrip('\n').rstrip('\r')

        # --- Front matter detection ---
        if i == 0 and line.strip() == '---':
            in_front_matter = True
            front_matter_count = 1
            result_lines.append(raw)
            i += 1
            continue

        if in_front_matter:
            result_lines.append(raw)
            if line.strip() == '---':
                front_matter_count += 1
                if front_matter_count >= 2:
                    in_front_matter = False
            i += 1
            continue

        # --- Code block toggle ---
        if re.match(r'^```', line):
            in_code_block = not in_code_block
            result_lines.append(raw)
            i += 1
            continue

        # --- Capture block toggle ---
        if re.match(r'^\{%-?\s*capture\b', line):
            in_capture_block = True
            result_lines.append(raw)
            i += 1
            continue
        if re.match(r'^\{%-?\s*endcapture\b', line):
            in_capture_block = False
            result_lines.append(raw)
            i += 1
            continue

        # Inside protected blocks: pass through unchanged
        if in_code_block or in_capture_block:
            result_lines.append(raw)
            i += 1
            continue

        # --- Task 1: Remove severity lines ---
        if SEVERITY_PATTERN.match(line):
            stats['severity_removed'] += 1
            stats['modified'] = True
            # Also skip immediately following blank lines
            i += 1
            while i < len(lines) and lines[i].strip() == '':
                i += 1
            continue

        # --- Task 3: Remove 출처 lines ---
        if CHULCHEO_PATTERN.match(line):
            stats['chulcheo_removed'] += 1
            stats['modified'] = True
            i += 1
            continue

        # --- Task 2: Strip bold markers ---
        should_strip_bold = True

        if is_heading(line):
            should_strip_bold = False
        elif is_html_line(line):
            should_strip_bold = False
        elif is_include_line(line):
            should_strip_bold = False
        elif '**' not in line:
            should_strip_bold = False

        if should_strip_bold:
            new_line, count = strip_bold(line)
            if count > 0:
                stats['bold_cleaned'] += count // 2  # each pair of ** = 1 marker
                stats['modified'] = True
                # Preserve original line ending
                ending = ''
                if raw.endswith('\r\n'):
                    ending = '\r\n'
                elif raw.endswith('\n'):
                    ending = '\n'
                elif raw.endswith('\r'):
                    ending = '\r'
                result_lines.append(new_line + ending)
                i += 1
                continue

        result_lines.append(raw)
        i += 1

    if stats['modified']:
        filepath.write_text(''.join(result_lines), encoding='utf-8')

    return stats


def main():
    md_files = sorted(POSTS_DIR.glob('*.md'))
    if not md_files:
        print(f"No markdown files found in {POSTS_DIR}")
        return

    total_files_modified = 0
    total_severity = 0
    total_bold = 0
    total_chulcheo = 0

    for fp in md_files:
        stats = process_file(fp)
        if stats['modified']:
            total_files_modified += 1
            total_severity += stats['severity_removed']
            total_bold += stats['bold_cleaned']
            total_chulcheo += stats['chulcheo_removed']
            parts = []
            if stats['severity_removed']:
                parts.append(f"severity={stats['severity_removed']}")
            if stats['bold_cleaned']:
                parts.append(f"bold={stats['bold_cleaned']}")
            if stats['chulcheo_removed']:
                parts.append(f"chulcheo={stats['chulcheo_removed']}")
            print(f"  MODIFIED {fp.name}: {', '.join(parts)}")

    print()
    print("=" * 60)
    print(f"Files modified     : {total_files_modified} / {len(md_files)}")
    print(f"Severity lines removed : {total_severity}")
    print(f"Bold markers cleaned   : {total_bold}")
    print(f"출처 lines removed     : {total_chulcheo}")
    print("=" * 60)


if __name__ == '__main__':
    main()
