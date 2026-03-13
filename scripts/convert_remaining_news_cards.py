#!/usr/bin/env python3
"""
Convert remaining 9 blog posts to use news-card.html includes.

These posts were not converted by the previous script. This script handles:
- Posts with `> **출처**: [Source](url)` format
- Posts with `> 출처: [Source](url)` format (no bold)
- Posts with `| **출처** | [Source](url) |` table format
- Articles with `#### 요약` sub-sections
- Section banner image insertion before `## N.` headings
- Category prefix detection from parent `## N.` section
- Skips sections that already have news-card includes
"""

import os
import re
import sys

# Posts to process
POSTS = [
    "_posts/2026-01-25-Tech_Security_Weekly_Digest_VMware_vCenter_Fortinet_SSO_Sandworm_DynoWiper_AI_Agents.md",
    "_posts/2026-01-26-Tech_Security_Weekly_Digest_Zero_Trust_Agentic_AI_Chrome_Tech_Support_Scam_Terraform_Stacks.md",
    "_posts/2026-01-27-Tech_Security_Weekly_Digest_MS_Office_Zero_Day_Kimi_K25_Kimwolf_Botnet_AWS_G7e.md",
    "_posts/2026-01-28-Tech_Security_Weekly_Digest_MS_Office_Zero_Day_CTEM_Grist_Core_RCE.md",
    "_posts/2026-01-29-Tech_Security_Weekly_Digest_n8n_RCE_D_Link_Zero_Day_Kubernetes_AI_Agent.md",
    "_posts/2026-01-30-Tech_Security_Weekly_Digest_Ollama_AI_SolarWinds_RCE_Google_IPIDEA.md",
    "_posts/2026-02-01-Tech_Security_Weekly_Digest_AI_OpenSSL_Zero_Day_OWASP_Agentic_Fortinet.md",
    "_posts/2026-02-07-Tech_Security_Weekly_Digest_AI_Malware_Go_Security.md",
    "_posts/2026-02-12-Tech_Security_Weekly_Digest_AI_Cloud_Security_Agent.md",
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Section banner mapping
SECTION_BANNERS = {
    "security": "![Security News Section Banner](/assets/images/section-security.svg)",
    "ai": "![AI ML News Section Banner](/assets/images/section-ai-ml.svg)",
    "cloud": "![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)",
    "devops": "![DevOps Platform News Section Banner](/assets/images/section-devops.svg)",
    "blockchain": "![Blockchain Web3 News Section Banner](/assets/images/section-blockchain.svg)",
}

# Category prefix mapping
CATEGORY_PREFIXES = {
    "security": "[보안]",
    "ai": "[AI/ML]",
    "cloud": "[클라우드]",
    "devops": "[DevOps]",
    "blockchain": "[블록체인]",
}

# Keywords for section classification
SECTION_KEYWORDS = {
    "security": [
        "보안",
        "security",
        "threat",
        "vulnerability",
        "취약점",
        "위협",
        "exploit",
        "malware",
        "zero-day",
        "제로데이",
        "패치",
        "CVE",
        "APT",
        "공격",
        "침해",
        "인텔리전스",
        "공급망",
        "RCE",
        "Critical",
        "Zero-Day",
        "봇넷",
        "botnet",
        "위협 인텔리전스",
    ],
    "ai": [
        "AI",
        "ML",
        "LLM",
        "인공지능",
        "머신러닝",
        "에이전트",
        "agent",
        "GPT",
        "Gemini",
        "OpenAI",
    ],
    "cloud": [
        "클라우드",
        "cloud",
        "AWS",
        "GCP",
        "Azure",
        "인프라",
        "오케스트레이션",
        "Kubernetes",
        "k8s",
    ],
    "devops": [
        "DevOps",
        "CICD",
        "CI/CD",
        "Docker",
        "컨테이너",
        "container",
        "Terraform",
        "IaC",
        "플랫폼",
        "개발",
    ],
    "blockchain": [
        "블록체인",
        "blockchain",
        "비트코인",
        "bitcoin",
        "crypto",
        "암호화폐",
        "Web3",
        "DeFi",
        "지갑",
        "wallet",
    ],
}


def classify_section(section_title):
    """Classify a section heading into a category."""
    title_lower = section_title.lower()
    scores = {}
    for cat, keywords in SECTION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in title_lower)
        if score > 0:
            scores[cat] = score
    if not scores:
        return None
    return max(scores, key=scores.get)


def escape_for_include(text):
    """Escape text for use in Jekyll include parameters (double-quoted)."""
    text = text.replace('"', "&quot;")
    text = text.replace("\n", " ").replace("\r", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def truncate_summary(text, max_len=200):
    """Truncate summary to max_len characters, ending at a word boundary."""
    # Strip markdown bold/italic
    clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    clean = re.sub(r"\*([^*]+)\*", r"\1", clean)
    if len(clean) <= max_len:
        return clean
    truncated = clean[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len * 0.6:
        truncated = truncated[:last_space]
    return truncated.rstrip(".,;:!? ") + "..."


def is_source_line(line):
    """Check if a line is a source citation."""
    stripped = line.strip()
    # > **출처**: [...](...) or > 출처: [...](...)
    if re.match(r"^>\s*\*?\*?출처\*?\*?\s*:\s*\[", stripped):
        return True
    return False


def extract_source_from_line(line):
    """Extract (source_name, url) from a source citation line."""
    match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", line)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None


def find_source_line(lines, start_idx, end_idx):
    """
    Find source citation within a range.
    Checks both blockquote format and table format.
    Returns (line_index, source_name, url) or (None, None, None).
    """
    for i in range(start_idx, min(end_idx, len(lines))):
        line = lines[i].strip()
        # Blockquote format: > **출처**: [...](...) or > 출처: [...](...)
        if is_source_line(lines[i]):
            source_name, url = extract_source_from_line(line)
            if source_name and url:
                return i, source_name, url
        # Table format: | **출처** | [Source](url) |
        if re.match(r"^\|\s*\*\*출처\*\*\s*\|", line):
            source_name, url = extract_source_from_line(line)
            if source_name and url:
                return i, source_name, url
    return None, None, None


def find_summary_paragraph(lines, heading_idx, source_idx):
    """
    Find the first content paragraph after a ### heading.
    Handles:
    - Direct paragraph after heading
    - Paragraph after #### 요약 sub-heading
    - Skips blank lines, severity markers, sub-headings (except #### 요약)
    Returns (summary_text, line_index) or (None, None).
    """
    search_end = min(heading_idx + 20, len(lines))
    if source_idx is not None:
        search_end = min(search_end, source_idx + 3)

    for i in range(heading_idx + 1, search_end):
        line = lines[i].strip()
        if not line:
            continue
        # Skip severity markers
        if line.startswith(">") and ("심각도" in line or "**심각도**" in line):
            continue
        # Skip source lines
        if is_source_line(lines[i]):
            continue
        # #### 요약 - look at the next line(s) for actual content
        if re.match(r"^#{4}\s+요약", line):
            # Find content after this sub-heading
            for j in range(i + 1, min(i + 5, len(lines))):
                sub_line = lines[j].strip()
                if not sub_line:
                    continue
                if sub_line.startswith("#") or sub_line.startswith(">"):
                    break
                if sub_line.startswith("|"):
                    break
                return sub_line, j
            continue
        # Skip other sub-headings
        if line.startswith("#"):
            # If it's #### (not ####요약), keep looking
            if line.startswith("####") and "요약" not in line:
                continue
            break
        # Skip tables
        if line.startswith("|"):
            continue
        # Skip images
        if line.startswith("!["):
            continue
        # Found a paragraph
        return line, i
    return None, None


def find_section_end(lines, heading_idx, heading_level):
    """Find where a section ends (next heading of same or higher level, or EOF)."""
    pattern = r"^#{1," + str(heading_level) + r"}\s"
    for i in range(heading_idx + 1, len(lines)):
        if re.match(pattern, lines[i]):
            return i
    return len(lines)


def get_existing_banner_lines(lines, heading_idx):
    """Check if there's already a section banner image before a heading."""
    for i in range(max(0, heading_idx - 3), heading_idx):
        if "section-" in lines[i] and "/assets/images/section-" in lines[i]:
            return i
    return None


def has_news_card_in_section(lines, heading_idx, section_end):
    """Check if a section already has a news-card include."""
    for i in range(heading_idx, min(section_end, len(lines))):
        if "news-card.html" in lines[i]:
            return True
    return False


def process_file(filepath):
    """Process a single post file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    insertions = []
    converted_count = 0
    banner_count = 0

    # Track current parent section
    current_section_title = None
    current_section_category = None

    # First pass: add section banners for ## N. headings
    banner_insertions = []
    for i, line in enumerate(lines):
        # Match ## N. Section Title or ## Section Title (without number)
        match = re.match(r"^##\s+(\d+\.)?\s*(.+)", line)
        if match and not line.startswith("###"):
            section_title = match.group(2).strip() if match.group(2) else ""
            category = classify_section(section_title)
            if category:
                existing = get_existing_banner_lines(lines, i)
                if existing is None:
                    banner = SECTION_BANNERS[category]
                    banner_insertions.append((i, f"\n{banner}\n"))
                    banner_count += 1

    # Second pass: find ### headings with source citations
    for i, line in enumerate(lines):
        # Track current ## section (with or without number)
        if re.match(r"^##\s+", line) and not line.startswith("###"):
            match = re.match(r"^##\s+(\d+\.?)?\s*(.+)", line)
            if match:
                title = match.group(2).strip() if match.group(2) else ""
                cat = classify_section(title)
                if cat:
                    current_section_title = title
                    current_section_category = cat

        # Match ### headings
        match = re.match(r"^###\s+(.+)", line)
        if not match:
            continue

        heading_title = match.group(1).strip()

        # Skip headings that are clearly not articles
        skip_patterns = [
            r"^(빠른 참조|긴급 조치|실무 체크리스트|P\d|핵심 요약|관련 포스팅|다음 주|이번 주 하이라이트|"
            r"카테고리별|경영진 요약|위험도|위협 분석|한국 영향|MITRE|헌팅 시나리오|탐지 및 대응|"
            r"3줄 요약|이번 주 핵심|이번 주 필수|종합 참고|핵심 인사이트|이번 주 액션|긴급 대응|"
            r"위협 헌팅|데이터 주권|참고 링크|참고 자료)",
        ]
        if any(re.match(pat, heading_title) for pat in skip_patterns):
            continue

        # Find the end of this section
        section_end = find_section_end(lines, i, 3)

        # Skip if already has news-card
        if has_news_card_in_section(lines, i, section_end):
            continue

        # Look for source citation within this section
        source_idx, source_name, url = find_source_line(lines, i + 1, section_end)

        if source_idx is None:
            continue

        # Find summary paragraph
        summary_text, summary_idx = find_summary_paragraph(lines, i, source_idx)
        if not summary_text:
            continue

        # Determine category prefix
        category = current_section_category or "security"
        prefix = CATEGORY_PREFIXES.get(category, "[보안]")

        # Strip number prefix from heading for card title (e.g., "1.1 Title" -> "Title")
        clean_title = re.sub(r"^\d+\.\d+\s+", "", heading_title)
        card_title = f"{prefix} {clean_title}"
        card_title = escape_for_include(card_title)

        # Build summary
        summary = truncate_summary(summary_text)
        summary = escape_for_include(summary)

        # Escape source name
        source_escaped = escape_for_include(source_name)

        # Build the include block
        news_card = (
            "\n{%- include news-card.html\n"
            f'  title="{card_title}"\n'
            f'  url="{url}"\n'
            f'  summary="{summary}"\n'
            f'  source="{source_escaped}"\n'
            "-%}\n"
        )

        # Insert after the ### heading line
        insertions.append((i + 1, news_card))
        converted_count += 1

    # Apply all insertions in reverse order
    all_insertions = banner_insertions + insertions
    all_insertions.sort(key=lambda x: x[0], reverse=True)

    for idx, text in all_insertions:
        lines.insert(idx, text)

    new_content = "\n".join(lines)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)

    return converted_count, banner_count


def main():
    total_converted = 0
    total_banners = 0
    results = []

    for post_path in POSTS:
        filepath = os.path.join(BASE_DIR, post_path)
        if not os.path.exists(filepath):
            print(f"  SKIP (not found): {post_path}")
            continue

        count, banners = process_file(filepath)
        total_converted += count
        total_banners += banners
        results.append((os.path.basename(post_path), count, banners))
        print(
            f"  {count:2d} articles, {banners:2d} banners: {os.path.basename(post_path)}"
        )

    print(f"\n{'=' * 70}")
    print(
        f"Total: {total_converted} articles converted, {total_banners} banners added across {len(results)} files"
    )
    print(f"{'=' * 70}")

    for name, count, banners in results:
        print(f"  {count:2d} articles, {banners:2d} banners | {name}")


if __name__ == "__main__":
    main()
