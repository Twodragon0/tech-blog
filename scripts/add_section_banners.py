#!/usr/bin/env python3
"""Add section banner SVG images to posts that are missing them.

GROUP A: Digest posts get banners before each numbered section (## N. Title).
GROUP B: Non-digest posts get a single banner before the first ## heading.

Idempotent: skips if banner already exists.
"""

import re
import os
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

# Banner image paths
BANNERS = {
    "security": "/assets/images/section-security.svg",
    "ai-ml": "/assets/images/section-ai-ml.svg",
    "cloud": "/assets/images/section-cloud.svg",
    "devops": "/assets/images/section-devops.svg",
    "devsecops": "/assets/images/section-devsecops.svg",
    "blockchain": "/assets/images/section-blockchain.svg",
}

# Alt text for each banner type
ALT_TEXT = {
    "security": "Security News Section Banner",
    "ai-ml": "AI ML News Section Banner",
    "cloud": "Cloud Infrastructure News Section Banner",
    "devops": "DevOps Platform News Section Banner",
    "devsecops": "DevSecOps Section Banner",
    "blockchain": "Blockchain Web3 News Section Banner",
}

# Keywords to determine banner type for digest section headings
SECTION_KEYWORDS = {
    "security": [
        "보안", "Security", "위협", "Threat", "CVE", "Patch", "취약점",
        "Vulnerability", "Ransomware", "랜섬웨어", "Malware", "악성",
        "해킹", "Hacking", "침해", "Breach", "MITRE", "ATT&CK",
        "피싱", "Phishing", "인증", "Auth", "제로데이", "Zero-Day",
        "CISO", "SOC", "SIEM", "WAF", "방화벽", "Firewall",
    ],
    "ai-ml": [
        "AI", "ML", "LLM", "GPT", "Gemini", "Claude", "인공지능",
        "머신러닝", "딥러닝", "Deep Learning", "NLP", "Agent",
        "에이전트", "Tech", "기술",
    ],
    "cloud": [
        "클라우드", "Cloud", "AWS", "GCP", "Azure", "인프라",
        "Infrastructure", "서버리스", "Serverless", "컨테이너",
        "Container", "Lambda", "S3", "EC2",
    ],
    "devops": [
        "DevOps", "Docker", "Kubernetes", "CI/CD", "CI", "CD",
        "배포", "Deploy", "파이프라인", "Pipeline", "Terraform",
        "Ansible", "개발", "Development", "Go", "Rust", "개발자",
        "Developer", "플랫폼", "Platform",
    ],
    "blockchain": [
        "블록체인", "Blockchain", "Bitcoin", "비트코인", "Crypto",
        "암호화폐", "Web3", "DeFi", "NFT", "이더리움", "Ethereum",
        "코인", "Coin",
    ],
}

# GROUP A: Digest posts that need per-section banners
GROUP_A_PATTERNS = [
    "2026-01-31-Tech_Security_Weekly_Digest_ShinyHunters_Vishing_Chrome_Extension_OT_Attack",
    "2026-03-08-Tech_Security_Weekly_Digest_AI_Security",
    "2026-03-09-Tech_Security_Weekly_Digest_AI_Security_Go_Bitcoin",
    "2026-03-10-Tech_Security_Weekly_Digest_AI_Malware_Security_Data",
    "2026-02-03-Weekly_Security_DevOps_Digest",
    "2026-02-16-Daily_Tech_Digest_RSS_Roundup",
    "2026-01-22-Security_Vendor_Blog_Weekly_Review",
]

# GROUP B: Non-digest posts with their assigned banner types
GROUP_B_MAPPING = {
    "2026-01-01-Tesla_FSD": "devsecops",
    "2026-01-03-OWASP": "security",
    "2026-01-06-DevSecOps_Viewing": "devsecops",
    "2026-01-08-Blockchain": "blockchain",
    "2026-01-08-Cloud_Security_Course": "cloud",
    "2026-01-10-2026_DevSecOps_Roadmap": "devsecops",
    "2026-01-11-AI_Music_Video": "ai-ml",
    "2026-01-14-2025_ISMS-P": "security",
    "2026-01-14-AWS_Cloud_Security": "cloud",
    "2026-01-14-CSPM_DataDog": "cloud",
    "2026-01-14-GCP_Cloud_Security": "cloud",
    "2026-01-15-Cloud_Security_Course": "cloud",
    "2026-01-16-Postmortem": "devops",
    "2026-01-17-AI_Coding_Assistants": "ai-ml",
    "2026-01-22-AWS_GCP_Cloud_Updates": "cloud",
    "2026-01-22-Cloud_Security_Course": "cloud",
    "2026-01-22-Cloud_Security_Trends": "cloud",
    "2026-01-22-KARA_Ransomware": "security",
    "2026-01-22-KISA_Security": "security",
    "2026-01-28-Claude_MD_Security": "security",
    "2026-02-01-Agentic_AI_Security": "ai-ml",
    "2026-02-04-AI_vs_Claude_Code": "ai-ml",
    "2026-02-05-AI_Content_Creator": "ai-ml",
    "2026-02-18-Krebs_Security": "security",
    "2026-02-25-Claude_Code_OpenCode": "ai-ml",
    "2026-02-28-AI_Agent_Security": "ai-ml",
    "2026-03-07-LLM_Security": "security",
}


def detect_banner_type(heading_text: str) -> str:
    """Detect the appropriate banner type from heading text using keyword matching."""
    # Score each category
    scores = {}
    text_upper = heading_text.upper()

    for category, keywords in SECTION_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw.upper() in text_upper:
                score += 1
        scores[category] = score

    # Find best match
    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best

    # Default to security for digest posts (most common topic)
    return "security"


def make_banner_line(banner_type: str) -> str:
    """Create a markdown image line for the given banner type."""
    return f"![{ALT_TEXT[banner_type]}]({BANNERS[banner_type]})"


def has_banner_nearby(lines: list[str], idx: int) -> bool:
    """Check if there's already a section banner near the given line index."""
    # Check up to 3 lines above
    for i in range(max(0, idx - 3), idx):
        if "section-" in lines[i] and "Section Banner" in lines[i]:
            return True
    return False


def is_in_front_matter(lines: list[str], idx: int) -> bool:
    """Check if the line at idx is inside YAML front matter."""
    fence_count = 0
    for i in range(idx):
        if lines[i].strip() == "---":
            fence_count += 1
    # Inside front matter if we've seen exactly 1 fence (opening)
    return fence_count < 2


def process_group_a(filepath: Path) -> int:
    """Process a digest post: add banners before each ## N. heading."""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")
    insertions = []  # (line_index, banner_type)

    # Find all ## N. headings
    numbered_heading = re.compile(r"^## \d+\.\s+(.+)")

    for i, line in enumerate(lines):
        match = numbered_heading.match(line)
        if match and not is_in_front_matter(lines, i):
            if not has_banner_nearby(lines, i):
                heading_text = match.group(1)
                banner_type = detect_banner_type(heading_text)
                insertions.append((i, banner_type))

    if not insertions:
        return 0

    # Insert banners from bottom to top to preserve line indices
    for idx, banner_type in reversed(insertions):
        banner_line = make_banner_line(banner_type)
        # Insert blank line + banner + blank line before the heading
        lines.insert(idx, "")
        lines.insert(idx, banner_line)
        # Check if line above is already blank
        if idx > 0 and lines[idx - 1].strip() != "":
            lines.insert(idx, "")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return len(insertions)


def find_first_heading_after_content_start(lines: list[str]) -> int | None:
    """Find the first ## heading after front matter and ai-summary-card."""
    in_front_matter = False
    front_matter_ended = False
    passed_summary_card = False
    heading_pattern = re.compile(r"^## ")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Track front matter
        if line == "---":
            if not in_front_matter and not front_matter_ended:
                in_front_matter = True
                i += 1
                continue
            elif in_front_matter:
                in_front_matter = False
                front_matter_ended = True
                i += 1
                continue

        if in_front_matter:
            i += 1
            continue

        if not front_matter_ended:
            i += 1
            continue

        # After front matter, look for first ## heading
        # Skip past ai-summary-card blocks
        if "ai-summary-card" in line or "capture" in line:
            passed_summary_card = True
            i += 1
            continue

        if heading_pattern.match(lines[i]):
            return i

        i += 1

    return None


def process_group_b(filepath: Path, banner_type: str) -> int:
    """Process a non-digest post: add a single banner before the first ## heading."""
    content = filepath.read_text(encoding="utf-8")
    lines = content.split("\n")

    # Check if banner already exists anywhere in the file
    for line in lines:
        if "section-" in line and "Section Banner" in line:
            return 0

    heading_idx = find_first_heading_after_content_start(lines)
    if heading_idx is None:
        return 0

    banner_line = make_banner_line(banner_type)

    # Insert banner before the first heading
    lines.insert(heading_idx, "")
    lines.insert(heading_idx, banner_line)
    # Add blank line above if needed
    if heading_idx > 0 and lines[heading_idx - 1].strip() != "":
        lines.insert(heading_idx, "")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    return 1


def find_post_file(pattern: str) -> Path | None:
    """Find a post file matching the given pattern prefix."""
    for f in POSTS_DIR.iterdir():
        if f.name.startswith(pattern) and f.suffix == ".md":
            return f
    return None


def main():
    total_banners = 0
    files_modified = 0

    print("=" * 60)
    print("Section Banner Insertion Script")
    print("=" * 60)

    # Process GROUP A (digest posts)
    print("\n--- GROUP A: Digest Posts (per-section banners) ---\n")
    for pattern in GROUP_A_PATTERNS:
        filepath = find_post_file(pattern)
        if filepath is None:
            print(f"  [SKIP] No file matching: {pattern}")
            continue

        count = process_group_a(filepath)
        if count > 0:
            print(f"  [OK] {filepath.name}: +{count} banners")
            total_banners += count
            files_modified += 1
        else:
            print(f"  [SKIP] {filepath.name}: already has banners or no numbered sections")

    # Process GROUP B (non-digest posts)
    print("\n--- GROUP B: Non-Digest Posts (single banner) ---\n")
    for pattern, banner_type in GROUP_B_MAPPING.items():
        filepath = find_post_file(pattern)
        if filepath is None:
            print(f"  [SKIP] No file matching: {pattern}")
            continue

        count = process_group_b(filepath, banner_type)
        if count > 0:
            print(f"  [OK] {filepath.name}: +{count} banner ({banner_type})")
            total_banners += count
            files_modified += 1
        else:
            print(f"  [SKIP] {filepath.name}: already has banner or no heading found")

    # Summary
    print("\n" + "=" * 60)
    print(f"TOTAL: {total_banners} banners added across {files_modified} files")
    print("=" * 60)


if __name__ == "__main__":
    main()
