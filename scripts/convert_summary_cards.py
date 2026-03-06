#!/usr/bin/env python3
"""Convert <div class="ai-summary-card"> inline HTML to {% include ai-summary-card.html %} format.
Also handles English title Korean-ization for digest posts."""

import os
import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

# Title conversion mappings
TITLE_REPLACEMENTS = {
    "Tech & Security Weekly Digest:": "기술·보안 주간 다이제스트:",
    "Weekly Security Threat Intelligence Digest:": "주간 보안 위협 인텔리전스 다이제스트:",
    "Weekly Tech & AI & Blockchain Digest:": "주간 기술·AI·블록체인 다이제스트:",
    "Weekly Security & DevOps Digest:": "주간 보안·DevOps 다이제스트:",
}

# Special full-title replacements (file -> new title)
FULL_TITLE_REPLACEMENTS = {
    "2026-02-17-Tech_Security_Weekly_Digest_AI_Agent_Cloud_Security.md":
        "기술·보안 주간 다이제스트: AI 에이전트 토큰 탈취, 패스워드 매니저 취약점, 서버리스 방어",
    "2026-02-18-Krebs_Security_Digest_Kimwolf_Patch_Tuesday.md":
        "KrebsOnSecurity 다이제스트: Kimwolf 봇넷 · 2026년 2월 패치 화요일",
    "2026-02-25-Claude_Code_OpenCode_Best_Practices.md":
        "Claude Code & OpenCode 실전 가이드: 38가지 베스트 프랙티스",
}


def extract_summary_block(content):
    """Find and extract the ai-summary-card div block from content using balanced div counting."""
    start_marker = '<div class="ai-summary-card">'
    start_idx = content.find(start_marker)
    if start_idx == -1:
        return None, None, None

    # Count balanced divs
    depth = 0
    pos = start_idx
    while pos < len(content):
        open_match = content.find("<div", pos)
        close_match = content.find("</div>", pos)

        if close_match == -1:
            break

        if open_match != -1 and open_match < close_match:
            depth += 1
            pos = open_match + 4
        else:
            depth -= 1
            pos = close_match + 6
            if depth == 0:
                return start_idx, pos, content[start_idx:pos]

    return None, None, None


def extract_field(html, label):
    """Extract a field value by its label from the summary card HTML."""
    # Find the label
    label_pattern = f'<span class="summary-label">{label}</span>'
    label_idx = html.find(label_pattern)
    if label_idx == -1:
        return None

    # For highlights, extract <ul> content
    if label == "핵심 내용":
        ul_start = html.find('<ul class="summary-list">', label_idx)
        if ul_start == -1:
            return None
        inner_start = ul_start + len('<ul class="summary-list">')
        ul_end = html.find("</ul>", inner_start)
        if ul_end == -1:
            return None
        return html[inner_start:ul_end].strip()

    # For other fields, extract span.summary-value content
    value_start = html.find('<span class="summary-value', label_idx)
    if value_start == -1:
        return None

    # Find the closing > of the opening tag
    tag_end = html.find(">", value_start)
    if tag_end == -1:
        return None
    inner_start = tag_end + 1

    # Find balanced closing </span>
    depth = 1
    pos = inner_start
    while pos < len(html) and depth > 0:
        open_span = html.find("<span", pos)
        close_span = html.find("</span>", pos)

        if close_span == -1:
            break

        if open_span != -1 and open_span < close_span:
            depth += 1
            pos = open_span + 5
        else:
            depth -= 1
            if depth == 0:
                return html[inner_start:close_span].strip()
            pos = close_span + 7

    return None


def escape_liquid_quotes(text):
    """Escape single quotes for Liquid include parameters."""
    return text.replace("'", "&#39;")


def clean_whitespace(text):
    """Normalize whitespace in extracted HTML while preserving structure."""
    # Collapse multiple spaces/newlines between tags
    text = re.sub(r'\n\s*', '\n      ', text)
    return text.strip()


def build_include_tag(html_block):
    """Build the {% include ai-summary-card.html %} tag from extracted fields."""
    fields = {
        "title": extract_field(html_block, "제목"),
        "categories_html": extract_field(html_block, "카테고리"),
        "tags_html": extract_field(html_block, "태그"),
        "highlights_html": extract_field(html_block, "핵심 내용"),
        "period": extract_field(html_block, "수집 기간"),
        "audience": extract_field(html_block, "대상 독자"),
    }

    lines = ["{%- include ai-summary-card.html"]
    for param, value in fields.items():
        if value is not None:
            val = escape_liquid_quotes(clean_whitespace(value))
            lines.append(f"  {param}='{val}'")

    lines.append("-%}")
    return "\n".join(lines)


def convert_title_to_korean(content, filename):
    """Convert English titles to Korean in front matter."""
    basename = os.path.basename(filename)

    # Check full title replacements first
    if basename in FULL_TITLE_REPLACEMENTS:
        new_title = FULL_TITLE_REPLACEMENTS[basename]
        # Handle multi-line YAML title
        # Match title field - could be single or multi-line
        title_match = re.search(
            r"^title:\s*['\"]?(.+?)(?:['\"]?\s*$)",
            content[:3000],
            re.MULTILINE
        )
        if title_match:
            old_line = title_match.group(0)
            new_line = f"title: '{new_title}'"
            content = content.replace(old_line, new_line, 1)
            return content, True
        return content, False

    # Check prefix replacements
    for eng, kor in TITLE_REPLACEMENTS.items():
        if eng in content[:3000]:
            content = content.replace(eng, kor, 1)
            # Also replace in the summary card title if present
            return content, True

    return content, False


def process_file(filepath):
    """Process a single markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    changes = []

    # 1. Convert title to Korean if needed
    content, title_changed = convert_title_to_korean(content, filepath)
    if title_changed:
        changes.append("title_korean")

    # 2. Convert inline HTML to include format
    start_idx, end_idx, html_block = extract_summary_block(content)
    if html_block:
        include_tag = build_include_tag(html_block)
        content = content[:start_idx] + include_tag + content[end_idx:]
        changes.append("include_convert")

    if changes:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

    return changes


def main():
    dry_run = "--dry-run" in sys.argv
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    total_files = 0
    title_count = 0
    include_count = 0
    errors = []

    for filepath in sorted(POSTS_DIR.glob("*.md")):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Check if needs title conversion
            basename = filepath.name
            needs_title = False
            if basename in FULL_TITLE_REPLACEMENTS:
                needs_title = True
            else:
                for eng in TITLE_REPLACEMENTS:
                    if eng in content[:3000]:
                        needs_title = True
                        break

            # Check if needs include conversion
            needs_include = '<div class="ai-summary-card">' in content

            if not needs_title and not needs_include:
                continue

            if dry_run:
                tasks = []
                if needs_title:
                    tasks.append("title")
                if needs_include:
                    tasks.append("include")
                print(f"  [DRY] {basename}: {', '.join(tasks)}")
                total_files += 1
                if needs_title:
                    title_count += 1
                if needs_include:
                    include_count += 1
                continue

            changes = process_file(filepath)
            if changes:
                total_files += 1
                if "title_korean" in changes:
                    title_count += 1
                if "include_convert" in changes:
                    include_count += 1
                if verbose:
                    print(f"  [OK] {basename}: {', '.join(changes)}")

        except Exception as e:
            errors.append((filepath.name, str(e)))
            print(f"  [ERR] {filepath.name}: {e}")

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Summary:")
    print(f"  Files processed: {total_files}")
    print(f"  Titles converted: {title_count}")
    print(f"  Includes converted: {include_count}")
    if errors:
        print(f"  Errors: {len(errors)}")
        for name, err in errors:
            print(f"    - {name}: {err}")


if __name__ == "__main__":
    main()
