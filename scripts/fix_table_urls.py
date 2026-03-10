#!/usr/bin/env python3
"""
fix_table_urls.py - Fix table URL issues in Jekyll blog posts

Issue 1: [https://...](https://...) where link text IS the URL → replace with short label
Issue 2: Bare https://... URLs in table cells → wrap with [label](url)
Issue 3: Table cells >150 chars → truncate to ~120 chars with ...
"""

import re
import os
import sys
from pathlib import Path


def get_label_for_url(url: str) -> str:
    """Generate a short descriptive label for a URL based on domain rules."""
    # Strip protocol and www
    domain_part = re.sub(r'^https?://', '', url)
    domain = domain_part.split('/')[0].lower()
    path = '/' + '/'.join(domain_part.split('/')[1:]) if '/' in domain_part else ''

    # Domain-specific rules (ordered from most specific to least)
    if 'docs.datadoghq.com' in domain:
        return 'DataDog Docs'
    if 'learn.datadoghq.com' in domain:
        return 'DataDog Learn'
    if 'docs.aws.amazon.com' in domain or ('aws.amazon.com' in domain):
        return 'AWS 문서'
    if 'cloud.google.com' in domain:
        return 'GCP 문서'
    if 'azure.microsoft.com' in domain:
        return 'Azure 문서'
    if 'learn.microsoft.com' in domain or 'devblogs.microsoft.com' in domain:
        return 'MS 문서'
    if 'github.com' in domain:
        return 'GitHub'
    if 'attack.mitre.org' in domain:
        return 'MITRE ATT&CK'
    if 'cisecurity.org' in domain:
        return 'CIS'
    if 'owasp.org' in domain or 'cheatsheetseries.owasp.org' in domain:
        return 'OWASP'
    if 'kubernetes.io' in domain:
        return 'K8s 문서'
    if 'sans.org' in domain:
        return 'SANS'
    if domain.endswith('.kisa.or.kr') or domain == 'kisa.or.kr':
        return 'KISA'
    if 'law.go.kr' in domain:
        return '법령정보'
    if 'fsec.or.kr' in domain:
        return '금융보안원'
    if 'pcisecuritystandards.org' in domain:
        return 'PCI SSC'
    if 'iso.org' in domain:
        return 'ISO'
    if 'nist.gov' in domain:
        return 'NIST'
    if 'splunk.com' in domain:
        return 'Splunk'
    if 'registry.terraform.io' in domain:
        return 'Terraform Registry'
    if 'cloudsecurityalliance.org' in domain:
        return 'CSA'
    if 'skshieldus.com' in domain:
        return 'SK Shieldus'
    if 'news.hada.io' in domain:
        return 'GeekNews'
    if 'cointelegraph.com' in domain:
        return 'CoinTelegraph'
    # Blog pattern
    if '/blog' in path:
        return '블로그'
    # Default fallback: clean domain name
    return '링크'


def fix_url_as_link_text(line: str) -> tuple[str, int]:
    """
    Issue 1: Replace [https://...](https://...) where link text IS the URL.
    Returns (modified_line, count_of_changes).
    """
    count = 0

    def replace_url_link(m):
        nonlocal count
        link_text = m.group(1)
        link_url = m.group(2)
        # Only replace if link text IS a URL (starts with http)
        if re.match(r'^https?://', link_text.strip()):
            label = get_label_for_url(link_url)
            count += 1
            return f'[{label}]({link_url})'
        return m.group(0)

    # Pattern: [http(s)://...](http(s)://...)
    pattern = r'\[(\s*https?://[^\]]+)\]\((https?://[^)]+)\)'
    new_line = re.sub(pattern, replace_url_link, line)
    return new_line, count


def fix_bare_urls(line: str) -> tuple[str, int]:
    """
    Issue 2: Wrap bare https://... URLs in table cells with [label](url).
    Returns (modified_line, count_of_changes).
    """
    count = 0

    def replace_bare_url(m):
        nonlocal count
        # Check the context: make sure it's not already inside []() or ()
        url = m.group(0)
        label = get_label_for_url(url)
        count += 1
        return f'[{label}]({url})'

    # Match bare URLs not preceded by ]( or [ (i.e., not already in markdown link)
    # We look for https?:// that is NOT preceded by ]( or [
    pattern = r'(?<!\])\(?(https?://[^\s<>\|\]`"\']+?)(?=[|\s\]`"\'<]|$)'

    # More careful: match URLs not already wrapped in markdown syntax
    # Split line by existing markdown links first, then process non-link parts
    # Use a different approach: find all positions that are bare URLs

    # First, mark all existing markdown links to avoid double-processing
    temp_line = line
    placeholders = {}
    placeholder_idx = 0

    # Protect existing markdown links [text](url)
    link_pattern = r'\[[^\]]*\]\([^)]*\)'
    for m in re.finditer(link_pattern, temp_line):
        key = f'\x00LINK{placeholder_idx}\x00'
        placeholders[key] = m.group(0)
        placeholder_idx += 1

    # Replace protected links with placeholders
    for key, val in placeholders.items():
        temp_line = temp_line.replace(val, key, 1)

    # Now find bare URLs in the remaining text
    bare_url_pattern = r'https?://[^\s<>\|\]`"\')\x00]+'

    def replace_in_unprotected(m):
        nonlocal count
        url = m.group(0)
        # Clean trailing punctuation that might not be part of URL
        url = url.rstrip('.,;:!?)')
        label = get_label_for_url(url)
        count += 1
        return f'[{label}]({url})'

    temp_line = re.sub(bare_url_pattern, replace_in_unprotected, temp_line)

    # Restore placeholders
    for key, val in placeholders.items():
        temp_line = temp_line.replace(key, val)

    return temp_line, count


def truncate_long_cells(line: str) -> tuple[str, int]:
    """
    Issue 3: Truncate table cells >150 chars to ~120 chars with ...
    Only truncates plain text content, not URLs or markdown links.
    Returns (modified_line, count_of_changes).
    """
    count = 0
    if not line.startswith('|'):
        return line, count

    # Split into cells
    # Remove leading/trailing | and split
    cells = line.split('|')
    # cells[0] is before first |, cells[-1] is after last |
    modified = False
    new_cells = []
    for i, cell in enumerate(cells):
        if len(cell) > 150:
            # Check if cell contains links or URLs - if so, don't truncate
            # Only truncate if it's mostly plain text
            has_link = bool(re.search(r'\[.*?\]\(.*?\)|https?://', cell))
            if not has_link:
                # Truncate plain text
                stripped = cell.strip()
                if len(stripped) > 150:
                    truncated = stripped[:120] + '...'
                    # Preserve leading/trailing whitespace style
                    leading = len(cell) - len(cell.lstrip())
                    trailing = len(cell) - len(cell.rstrip())
                    cell = cell[:leading] + truncated + cell[len(cell)-trailing:] if trailing > 0 else cell[:leading] + truncated
                    count += 1
                    modified = True
        new_cells.append(cell)

    if modified:
        return '|'.join(new_cells), count
    return line, count


def is_separator_row(line: str) -> bool:
    """Check if line is a markdown table separator (---|---|---)."""
    stripped = line.strip().strip('|').strip()
    return bool(re.match(r'^[\s\-:]+$', stripped)) and '-' in stripped


def process_file(filepath: Path) -> dict:
    """Process a single file and return change statistics."""
    stats = {
        'file': str(filepath),
        'url_link_text_fixes': 0,
        'bare_url_fixes': 0,
        'truncations': 0,
        'modified': False,
    }

    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        stats['error'] = str(e)
        return stats

    lines = content.split('\n')
    new_lines = []
    in_code_block = False
    in_front_matter = False
    front_matter_count = 0

    for i, line in enumerate(lines):
        # Track front matter
        if i == 0 and line.strip() == '---':
            in_front_matter = True
            new_lines.append(line)
            continue
        if in_front_matter:
            if line.strip() == '---':
                in_front_matter = False
                front_matter_count += 1
            new_lines.append(line)
            continue

        # Track code blocks
        if line.strip().startswith('```') or line.strip().startswith('~~~'):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue

        if in_code_block:
            new_lines.append(line)
            continue

        # Only process table lines
        if not line.startswith('|') or is_separator_row(line):
            new_lines.append(line)
            continue

        # Apply fixes
        modified_line = line

        # Issue 1: URL-as-link-text
        modified_line, c1 = fix_url_as_link_text(modified_line)
        stats['url_link_text_fixes'] += c1

        # Issue 2: Bare URLs
        modified_line, c2 = fix_bare_urls(modified_line)
        stats['bare_url_fixes'] += c2

        # Issue 3: Long cells
        modified_line, c3 = truncate_long_cells(modified_line)
        stats['truncations'] += c3

        new_lines.append(modified_line)

    total_changes = stats['url_link_text_fixes'] + stats['bare_url_fixes'] + stats['truncations']
    if total_changes > 0:
        stats['modified'] = True
        new_content = '\n'.join(new_lines)
        filepath.write_text(new_content, encoding='utf-8')

    return stats


def main():
    posts_dir = Path('/Users/yong/Desktop/tech-blog/_posts')
    if not posts_dir.exists():
        print(f"ERROR: Posts directory not found: {posts_dir}")
        sys.exit(1)

    post_files = sorted(posts_dir.glob('*.md'))
    print(f"Found {len(post_files)} post files")
    print('=' * 60)

    total_files_modified = 0
    total_url_link_text = 0
    total_bare_urls = 0
    total_truncations = 0
    errors = []

    for filepath in post_files:
        stats = process_file(filepath)

        if 'error' in stats:
            errors.append(f"ERROR {filepath.name}: {stats['error']}")
            continue

        if stats['modified']:
            total_files_modified += 1
            total_url_link_text += stats['url_link_text_fixes']
            total_bare_urls += stats['bare_url_fixes']
            total_truncations += stats['truncations']
            print(f"FIXED {filepath.name}")
            if stats['url_link_text_fixes']:
                print(f"  Issue 1 (URL-as-link-text): {stats['url_link_text_fixes']} fixes")
            if stats['bare_url_fixes']:
                print(f"  Issue 2 (Bare URLs): {stats['bare_url_fixes']} fixes")
            if stats['truncations']:
                print(f"  Issue 3 (Long cells): {stats['truncations']} truncations")

    print()
    print('=' * 60)
    print('SUMMARY')
    print('=' * 60)
    print(f"Files processed:          {len(post_files)}")
    print(f"Files modified:           {total_files_modified}")
    print(f"Issue 1 fixes (URL text): {total_url_link_text}")
    print(f"Issue 2 fixes (bare URL): {total_bare_urls}")
    print(f"Issue 3 truncations:      {total_truncations}")
    print(f"Total changes:            {total_url_link_text + total_bare_urls + total_truncations}")

    if errors:
        print()
        print('ERRORS:')
        for e in errors:
            print(f"  {e}")


if __name__ == '__main__':
    main()
