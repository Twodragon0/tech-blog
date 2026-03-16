#!/usr/bin/env python3
"""
Convert Tech Security Weekly Digest posts to use {% include news-card.html %}.

For each article section (### X.X Title), extracts:
- Title from heading
- URL from > **출처**: [Source](URL)
- Summary from first paragraph after #### 요약 or #### 개요
- Source name from the 출처 link text

Inserts {% include news-card.html %} block after the ### heading, before #### 요약.
Also adds section banner images where missing.

Idempotent: skips articles that already have news-card.html nearby.
"""

import os
import re
import sys
from pathlib import Path

POSTS_DIR = Path("/Users/yong/Desktop/tech-blog/_posts")

# Files to skip (already converted)
SKIP_FILES = {
    "2026-03-08-Tech_Security_Weekly_Digest_AI_Security.md",
    "2026-03-09-Tech_Security_Weekly_Digest_AI_Security_Go_Bitcoin.md",
    "2026-03-10-Tech_Security_Weekly_Digest_AI_Malware_Security_Data.md",
}

# Section banners mapping
SECTION_BANNERS = {
    "보안": ("Security News Section Banner", "/assets/images/section-security.svg"),
    "AI": ("AI ML News Section Banner", "/assets/images/section-ai-ml.svg"),
    "클라우드": (
        "Cloud Infrastructure News Section Banner",
        "/assets/images/section-cloud.svg",
    ),
    "DevOps": (
        "DevOps Platform News Section Banner",
        "/assets/images/section-devops.svg",
    ),
    "블록체인": (
        "Blockchain Web3 News Section Banner",
        "/assets/images/section-blockchain.svg",
    ),
}

# Category prefix mapping based on section heading
CATEGORY_PREFIXES = {}


def detect_category(section_heading: str) -> str:
    """Detect category prefix from the parent ## section heading."""
    heading_lower = section_heading.lower()
    if "보안" in heading_lower or "security" in heading_lower:
        return "[보안]"
    if "ai" in heading_lower or "ml" in heading_lower:
        return "[AI/ML]"
    if "클라우드" in heading_lower or "cloud" in heading_lower:
        return "[클라우드]"
    if "devops" in heading_lower or "데브옵스" in heading_lower:
        return "[DevOps]"
    if (
        "블록체인" in heading_lower
        or "blockchain" in heading_lower
        or "web3" in heading_lower
    ):
        return "[블록체인]"
    return ""


def determine_severity(title: str, summary: str, category: str) -> str:
    """Determine severity from title/summary keywords."""
    text = f"{title} {summary}".lower()
    is_security = "보안" in category or "security" in category.lower()
    has_cve = bool(re.search(r"cve-\d{4}-\d+", text))
    critical_phrases = [
        "critical", "rce", "zero-day", "0-day", "제로데이",
        "actively exploited", "in the wild", "emergency patch",
        "긴급 패치", "remote code execution", "원격 코드 실행",
        "ransomware attack", "data breach", "데이터 유출",
    ]
    high_keywords = [
        "취약점", "vulnerability", "exploit", "malware", "악성코드",
        "backdoor", "백도어", "공격", "attack", "privilege escalation",
        "권한 상승", "authentication bypass", "인증 우회",
        "supply chain", "공급망", "botnet", "봇넷", "랜섬웨어",
    ]
    for phrase in critical_phrases:
        if phrase in text:
            return "Critical" if (is_security or has_cve) else "High"
    for kw in high_keywords:
        if kw in text:
            return "High" if (is_security or has_cve) else "Medium"
    return "Medium"


def escape_quotes(text: str) -> str:
    """Escape double quotes for use in include parameters."""
    return text.replace('"', "&quot;")


def truncate_summary(text: str, max_len: int = 200) -> str:
    """Truncate text to max_len chars, ending at a sentence boundary if possible."""
    text = text.strip()
    if len(text) <= max_len:
        return text

    # Try to find a sentence boundary (., !, ?) before max_len
    truncated = text[:max_len]
    # Look for last sentence-ending punctuation
    for i in range(len(truncated) - 1, max(0, len(truncated) - 60), -1):
        if truncated[i] in ".!?。":
            # Check if followed by space or end
            if i == len(truncated) - 1 or truncated[i + 1] in " \n":
                return truncated[: i + 1]
            # For Korean, period may be followed directly by next char
            if truncated[i] in "." and i > 0:
                return truncated[: i + 1]

    # No sentence boundary found; try to end at a comma or space
    last_space = truncated.rfind(" ")
    last_comma = truncated.rfind(",")
    last_break = max(last_space, last_comma)
    if last_break > max_len - 50:
        return truncated[:last_break].rstrip(",") + "..."

    return truncated + "..."


def extract_source_info(
    lines: list[str], start: int, end: int
) -> tuple[str, str] | None:
    """
    Extract (source_name, url) from > **출처**: [Source](URL) within line range.
    """
    for i in range(start, min(end, len(lines))):
        line = lines[i]
        # Pattern: > **출처**: [Source Name](URL)
        m = re.match(r">\s*\*\*출처\*\*\s*:\s*\[([^\]]+)\]\(([^)]+)\)", line)
        if m:
            return m.group(1).strip(), m.group(2).strip()
    return None


def extract_summary(lines: list[str], start: int, end: int) -> str | None:
    """
    Extract first meaningful paragraph after #### 요약 or #### 개요 within line range.
    If no such heading, extract first paragraph after the ### heading.
    """
    summary_start = None

    for i in range(start, min(end, len(lines))):
        line = lines[i].strip()
        if re.match(r"^####\s+(요약|개요)", line):
            summary_start = i + 1
            break

    # If no #### 요약/개요 found, try to get the first paragraph after the ### heading
    if summary_start is None:
        # Start right after the ### heading
        summary_start = start + 1

    # Skip blank lines to find first paragraph
    for i in range(summary_start, min(end, len(lines))):
        line = lines[i].strip()
        if not line:
            continue
        # Skip lines that are headings, blockquotes, tables, images, HTML, includes
        if line.startswith(("#", ">", "|", "!", "<", "{%", "```", "---")):
            continue
        # Found a content paragraph
        return line

    return None


def find_article_sections(lines: list[str]) -> list[dict]:
    """
    Find all article sections (### X.X Title pattern) and their ranges.
    Returns list of dicts with: line_idx, title, number, section_heading.
    """
    articles = []
    current_section = ""

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Track ## sections for category detection
        m_section = re.match(r"^##\s+(\d+)\.\s+(.+)", stripped)
        if m_section:
            current_section = stripped
            continue

        # Find ### X.X articles
        m_article = re.match(r"^###\s+(\d+\.\d+)\s+(.+)", stripped)
        if m_article:
            articles.append(
                {
                    "line_idx": i,
                    "number": m_article.group(1),
                    "title": m_article.group(2).strip(),
                    "section_heading": current_section,
                }
            )

    # Set end boundaries for each article
    for i, article in enumerate(articles):
        if i + 1 < len(articles):
            article["end_idx"] = articles[i + 1]["line_idx"]
        else:
            article["end_idx"] = len(lines)

    return articles


def has_news_card_nearby(lines: list[str], start: int, end: int) -> bool:
    """Check if there's already a news-card.html include near this article."""
    for i in range(start, min(end, len(lines))):
        if "news-card.html" in lines[i]:
            return True
    return False


def add_section_banners(lines: list[str]) -> tuple[list[str], int]:
    """Add missing section banner images before ## N. Section headings."""
    new_lines = []
    banners_added = 0

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Check for ## N. Section heading
        m = re.match(r"^##\s+\d+\.\s+(.+)", stripped)
        if m:
            section_text = m.group(1)

            # Determine which banner to use
            banner_key = None
            for key in SECTION_BANNERS:
                if key.lower() in section_text.lower():
                    banner_key = key
                    break

            if banner_key:
                alt_text, img_path = SECTION_BANNERS[banner_key]

                # Check if previous non-blank lines (in both original and new_lines) already have a banner
                has_banner = False
                # Check in original lines (look backward from current position)
                for j in range(i - 1, max(0, i - 5), -1):
                    prev = lines[j].strip()
                    if not prev or prev == "---":
                        continue
                    if prev.startswith("![") and "section-" in prev:
                        has_banner = True
                    break

                # Also check in new_lines (what we've built so far)
                if not has_banner:
                    for j in range(len(new_lines) - 1, max(0, len(new_lines) - 5), -1):
                        prev = new_lines[j].strip()
                        if not prev or prev == "---":
                            continue
                        if prev.startswith("![") and "section-" in prev:
                            has_banner = True
                        break

                if not has_banner:
                    # Add banner before this heading
                    # Ensure blank line before banner
                    if new_lines and new_lines[-1].strip():
                        new_lines.append("\n")
                    new_lines.append(f"![{alt_text}]({img_path})\n")
                    new_lines.append("\n")
                    banners_added += 1

        new_lines.append(line)

    return new_lines, banners_added


def process_file(filepath: Path) -> tuple[int, int]:
    """
    Process a single file. Returns (articles_converted, banners_added).
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    # Preserve original line endings
    # Re-add newlines for processing (we'll join without extra newline later)
    lines_with_nl = [line + "\n" for line in lines]
    # Last line might not have newline
    if content.endswith("\n"):
        lines_with_nl[-1] = lines[-1] + "\n"
    else:
        lines_with_nl[-1] = lines[-1]

    # Step 1: Add section banners
    lines_with_nl, banners_added = add_section_banners(lines_with_nl)
    # Update plain lines
    lines = [l.rstrip("\n") for l in lines_with_nl]

    # Step 2: Find article sections
    articles = find_article_sections(lines)

    # Process articles in reverse order to preserve line indices
    articles_converted = 0

    if not articles and banners_added == 0:
        return 0, 0

    for article in reversed(articles):
        idx = article["line_idx"]
        end_idx = article["end_idx"]
        title = article["title"]
        section_heading = article["section_heading"]

        # Skip if already has news-card
        if has_news_card_nearby(lines, idx, min(idx + 15, end_idx)):
            continue

        # Extract source info
        source_info = extract_source_info(lines, idx, end_idx)
        if not source_info:
            # No 출처 found, skip this article
            continue

        source_name, url = source_info

        # Extract summary
        summary = extract_summary(lines, idx, end_idx)
        if not summary:
            summary = title  # Fallback to title

        # Truncate and escape
        summary = truncate_summary(summary, 200)
        escaped_summary = escape_quotes(summary)
        escaped_title_text = escape_quotes(title)

        # Determine category prefix
        category = detect_category(section_heading)
        card_title = (
            f"{category} {escaped_title_text}" if category else escaped_title_text
        )

        # Build the news-card include block
        severity = determine_severity(title, summary, section_heading)
        card_block = [
            "",
            "{%- include news-card.html",
            f'  title="{card_title}"',
            f'  url="{url}"',
            f'  summary="{escaped_summary}"',
            f'  source="{escape_quotes(source_name)}"',
            f'  severity="{severity}"',
            "-%}",
            "",
        ]

        # Find insertion point: right after the ### heading line
        insert_idx = idx + 1

        # Check if there's a blank line after heading
        # We want to insert after the heading, before #### 요약
        # But also handle cases where there might be other content between heading and 요약

        # Find #### 요약 or #### 개요 position
        summary_heading_idx = None
        for j in range(idx + 1, min(end_idx, len(lines))):
            stripped = lines[j].strip()
            if re.match(r"^####\s+(요약|개요)", stripped):
                summary_heading_idx = j
                break
            # If we hit another ### or ## heading, stop
            if re.match(r"^#{2,3}\s+", stripped):
                break

        if summary_heading_idx is not None:
            # Insert right before #### 요약
            insert_idx = summary_heading_idx
        else:
            # No #### 요약 found; insert right after the ### heading
            insert_idx = idx + 1

        # Insert the card block
        for k, card_line in enumerate(card_block):
            lines.insert(insert_idx + k, card_line)

        articles_converted += 1

    # Write back
    new_content = "\n".join(lines)
    # Ensure file ends with newline
    if not new_content.endswith("\n"):
        new_content += "\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return articles_converted, banners_added


def main():
    # Collect target files
    target_files = []

    # All Tech_Security_Weekly_Digest files
    for f in sorted(POSTS_DIR.glob("*Tech_Security_Weekly_Digest*.md")):
        if f.name not in SKIP_FILES:
            target_files.append(f)

    # Also include the Security_Cloud_Digest file
    extra = POSTS_DIR / "2026-02-09-Security_Cloud_Digest_AI_VirusTotal_AWS_Agentic.md"
    if extra.exists() and extra.name not in SKIP_FILES:
        target_files.append(extra)

    if not target_files:
        print("No target files found.")
        sys.exit(1)

    print(f"Found {len(target_files)} files to process.\n")

    total_articles = 0
    total_banners = 0
    modified_files = []

    for filepath in target_files:
        articles_converted, banners_added = process_file(filepath)
        if articles_converted > 0 or banners_added > 0:
            modified_files.append((filepath.name, articles_converted, banners_added))
            total_articles += articles_converted
            total_banners += banners_added
            print(
                f"  ✓ {filepath.name}: {articles_converted} articles, {banners_added} banners"
            )
        else:
            print(f"  - {filepath.name}: no changes needed")

    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Files modified: {len(modified_files)}")
    print(f"  Articles converted: {total_articles}")
    print(f"  Banners added: {total_banners}")
    print(f"{'=' * 60}")

    if modified_files:
        print("\nModified files:")
        for name, arts, bans in modified_files:
            print(f"  {name} ({arts} articles, {bans} banners)")


if __name__ == "__main__":
    main()
