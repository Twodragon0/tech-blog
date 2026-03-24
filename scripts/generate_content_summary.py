#!/usr/bin/env python3
"""
Content Summary Infographic Generator

Generates content-summary SVG infographics (+ optional PNG) for each blog post.
Extracts front matter, AI summary highlights, H2/H3 sections, and technical terms
to produce one of 5 layout types automatically selected by post metadata heuristics.

Layouts:
  1. Section Map    - grid of topic cards (default)
  2. Flow Diagram   - timeline/steps (incident/postmortem)
  3. Highlight Cards - key highlights (weekly digest)
  4. Architecture    - layered diagram (cloud/k8s guide)
  5. Comparison Grid - table layout (analysis/comparison)

Usage:
  python3 scripts/generate_content_summary.py --all
  python3 scripts/generate_content_summary.py --recent 5
  python3 scripts/generate_content_summary.py --post _posts/2026-02-23-Example.md
  python3 scripts/generate_content_summary.py --all --force
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))
from scripts.lib.logging_utils import log_message

import frontmatter

try:
    import cairosvg

    CAIROSVG_AVAILABLE = True
except ImportError:
    CAIROSVG_AVAILABLE = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Category config (mirrors generate_post_images.py)
# ---------------------------------------------------------------------------
CATEGORY_SVG_CONFIG = {
    "security": {
        "gradient_start": "#dc2626",
        "gradient_end": "#991b1b",
        "label": "SECURITY",
        "icon": "!",
        "accent": "#ef4444",
    },
    "devsecops": {
        "gradient_start": "#8b5cf6",
        "gradient_end": "#6d28d9",
        "label": "DEVSECOPS",
        "icon": "SEC",
        "accent": "#a78bfa",
    },
    "cloud": {
        "gradient_start": "#10b981",
        "gradient_end": "#059669",
        "label": "CLOUD",
        "icon": "AWS",
        "accent": "#34d399",
    },
    "devops": {
        "gradient_start": "#f59e0b",
        "gradient_end": "#d97706",
        "label": "DEVOPS",
        "icon": "DEV",
        "accent": "#fbbf24",
    },
    "kubernetes": {
        "gradient_start": "#3b82f6",
        "gradient_end": "#1d4ed8",
        "label": "KUBERNETES",
        "icon": "K8S",
        "accent": "#60a5fa",
    },
    "finops": {
        "gradient_start": "#14b8a6",
        "gradient_end": "#0d9488",
        "label": "FINOPS",
        "icon": "$",
        "accent": "#2dd4bf",
    },
    "incident": {
        "gradient_start": "#ef4444",
        "gradient_end": "#b91c1c",
        "label": "INCIDENT",
        "icon": "!!",
        "accent": "#f87171",
    },
    "tech": {
        "gradient_start": "#3b82f6",
        "gradient_end": "#1d4ed8",
        "label": "TECH",
        "icon": "AI",
        "accent": "#60a5fa",
    },
}

# Known English technical terms for extraction
KNOWN_TECH_TERMS = {
    "AI",
    "ML",
    "LLM",
    "GPT",
    "NLP",
    "API",
    "SDK",
    "CLI",
    "CI/CD",
    "AWS",
    "GCP",
    "Azure",
    "Terraform",
    "Ansible",
    "Docker",
    "Kubernetes",
    "K8s",
    "Helm",
    "Istio",
    "Prometheus",
    "Grafana",
    "ArgoCD",
    "Jenkins",
    "GitHub",
    "GitLab",
    "Bitbucket",
    "Jira",
    "Slack",
    "Vercel",
    "Netlify",
    "Cloudflare",
    "NGINX",
    "Apache",
    "Redis",
    "PostgreSQL",
    "MongoDB",
    "MySQL",
    "Kafka",
    "RabbitMQ",
    "Elasticsearch",
    "Kibana",
    "Splunk",
    "Datadog",
    "Sentry",
    "PagerDuty",
    "OpsGenie",
    "Vault",
    "Consul",
    "CVE",
    "CVSS",
    "OWASP",
    "Zero-Day",
    "XSS",
    "CSRF",
    "SQLi",
    "RCE",
    "SIEM",
    "SOC",
    "SOAR",
    "EDR",
    "WAF",
    "IAM",
    "MFA",
    "SSO",
    "ZTNA",
    "RBAC",
    "mTLS",
    "TLS",
    "SSL",
    "PKI",
    "HSM",
    "KMS",
    "DevOps",
    "DevSecOps",
    "SRE",
    "FinOps",
    "MLOps",
    "AIOps",
    "GitOps",
    "IaC",
    "ISMS",
    "ISMS-P",
    "GDPR",
    "CCPA",
    "SOC2",
    "ISO27001",
    "VPC",
    "ALB",
    "EKS",
    "ECS",
    "Lambda",
    "S3",
    "EC2",
    "RDS",
    "CloudFront",
    "BGP",
    "CDN",
    "DNS",
    "TCP",
    "UDP",
    "HTTP",
    "HTTPS",
    "gRPC",
    "REST",
    "JSON",
    "YAML",
    "TOML",
    "XML",
    "CSV",
    "Parquet",
    "Python",
    "Go",
    "Rust",
    "Java",
    "TypeScript",
    "JavaScript",
    "Ruby",
    "React",
    "Next.js",
    "Vue",
    "Svelte",
    "Node.js",
    "FastAPI",
    "Flask",
    "Linux",
    "macOS",
    "Windows",
    "Ubuntu",
    "CentOS",
    "Alpine",
    "Bitcoin",
    "Ethereum",
    "Blockchain",
    "DeFi",
    "NFT",
    "Web3",
    "OpenAI",
    "Anthropic",
    "Claude",
    "Gemini",
    "Llama",
    "Mistral",
    "Ransomware",
    "Malware",
    "Phishing",
    "APT",
    "DDoS",
    "Botnet",
    "CNCF",
    "Karpenter",
    "Falco",
    "OPA",
    "Trivy",
    "Snyk",
    "Copilot",
    "Cursor",
    "Replit",
    "Notion",
    "Zapier",
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------



# ---------------------------------------------------------------------------
# SVG text helpers
# ---------------------------------------------------------------------------


def _escape_svg_text(text: str) -> str:
    """Escape text for safe SVG embedding."""
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _truncate(text: str, max_len: int = 50) -> str:
    """Truncate text with ellipsis."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _has_korean(text: str) -> bool:
    """Return True if text contains Korean characters."""
    return bool(re.search(r"[\uac00-\ud7a3\u3131-\u3163\u1100-\u11ff]", text))


# ---------------------------------------------------------------------------
# Content extraction
# ---------------------------------------------------------------------------


def extract_post_info(post_file: Path) -> Optional[Dict]:
    """Extract structured info from a markdown post file."""
    try:
        with open(post_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
    except Exception as e:
        log_message(f"Failed to parse {post_file.name}: {e}", "ERROR")
        return None

    meta = post.metadata
    title = meta.get("title", "")
    categories = meta.get("categories", [])
    if isinstance(categories, str):
        categories = [categories]
    categories = [str(c) for c in categories]  # coerce to str
    category = categories[0] if categories else str(meta.get("category", "tech"))
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]
    tags = [str(t) for t in tags]  # coerce ints (e.g. 2026) to str
    image_path = meta.get("image", "")
    excerpt = meta.get("excerpt", "")
    date_raw = meta.get("date", "")
    content = post.content

    # Parse date
    if isinstance(date_raw, datetime):
        date_obj = date_raw
    elif isinstance(date_raw, str) and date_raw:
        try:
            date_obj = datetime.strptime(date_raw[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                date_obj = datetime.strptime(date_raw[:10], "%Y-%m-%d")
            except ValueError:
                date_obj = datetime.now()
    else:
        date_obj = datetime.now()

    # Extract AI summary highlights (two patterns)
    highlights = _extract_highlights(content)

    # Extract H2/H3 section headers
    sections = _extract_sections(content)

    # Extract English technical terms
    tech_terms = _extract_tech_terms(title, tags, content)

    return {
        "title": title,
        "category": category.lower() if category else "tech",
        "categories": [c.lower() for c in categories],
        "tags": tags,
        "image": image_path,
        "excerpt": excerpt,
        "date": date_obj,
        "content": content,
        "highlights": highlights,
        "sections": sections,
        "tech_terms": tech_terms,
        "filename": post_file.name,
        "stem": post_file.stem,
    }


def _extract_highlights(content: str) -> List[Dict[str, str]]:
    """Extract AI summary card highlights from both old and new patterns.

    Returns list of {"key": ..., "desc": ...} dicts.
    """
    highlights = []

    # Pattern 1 (old): <ul class="summary-list"> ... <li><strong>KEY</strong>: desc</li>
    old_match = re.search(
        r'<ul\s+class=["\']summary-list["\']>(.*?)</ul>', content, re.DOTALL
    )
    if old_match:
        items = re.findall(
            r"<li>\s*<strong>(.*?)</strong>\s*:?\s*(.*?)</li>",
            old_match.group(1),
            re.DOTALL,
        )
        for key, desc in items:
            key_clean = re.sub(r"<[^>]+>", "", key).strip()
            desc_clean = re.sub(r"<[^>]+>", "", desc).strip()
            if key_clean:
                highlights.append({"key": key_clean, "desc": desc_clean})

    # Pattern 2 (new, include-based): highlights_html='<li><strong>KEY</strong>: desc</li>'
    new_match = re.search(
        r"highlights_html\s*=\s*(['\"])(.+?)\1\s*(?:period|audience|%\})",
        content[:5000],
        re.DOTALL,
    )
    if new_match and not highlights:
        items = re.findall(
            r"<li>\s*<strong>(.*?)</strong>\s*:?\s*(.*?)</li>",
            new_match.group(2),
            re.DOTALL,
        )
        for key, desc in items:
            key_clean = re.sub(r"<[^>]+>", "", key).strip()
            desc_clean = re.sub(r"<[^>]+>", "", desc).strip()
            if key_clean:
                highlights.append({"key": key_clean, "desc": desc_clean})

    return highlights[:6]


def _extract_sections(content: str) -> List[Dict[str, str]]:
    """Extract H2 and H3 section headers from markdown content."""
    sections = []
    for match in re.finditer(r"^(#{2,3})\s+(.+)$", content, re.MULTILINE):
        level = len(match.group(1))
        text = match.group(2).strip()
        # Remove emoji prefixes and numbering
        text = re.sub(r"^[\U0001f300-\U0001f9ff\u2600-\u27bf]+\s*", "", text)
        text = re.sub(r"^\d+(\.\d+)*\.?\s*", "", text)
        text = text.strip()
        if text and text not in ("---",):
            sections.append({"level": level, "text": text})
    return sections


def _extract_tech_terms(title: str, tags: List[str], content: str) -> List[str]:
    """Extract English technical terms from post content."""
    found = set()

    # From tags
    for tag in tags:
        tag_clean = tag.replace("-", " ").replace("_", " ")
        for word in tag_clean.split():
            if word in KNOWN_TECH_TERMS:
                found.add(word)
            elif word.upper() in KNOWN_TECH_TERMS:
                found.add(word.upper())

    # From title - uppercase words and known terms
    for word in _extract_ascii_words(title):
        if word in KNOWN_TECH_TERMS:
            found.add(word)
        elif word.upper() in KNOWN_TECH_TERMS:
            found.add(word.upper())

    # CamelCase from title (ASCII only)
    for word in re.findall(r"[A-Z][a-z]+(?:[A-Z][a-z]+)+", title, re.ASCII):
        found.add(word)

    # If not enough, scan first 2000 chars of content
    if len(found) < 4:
        snippet = content[:2000]
        for term in KNOWN_TECH_TERMS:
            if term in snippet:
                found.add(term)
            if len(found) >= 8:
                break

    return sorted(found)[:8]


# ---------------------------------------------------------------------------
# English title generation
# ---------------------------------------------------------------------------


def _make_english_title(post_info: Dict) -> str:
    """Create an English title from category, tags, and tech terms."""
    cfg = _get_config(post_info["category"])
    label = cfg["label"]
    terms = post_info.get("tech_terms", [])

    # Try to extract English words from the original title
    title = post_info.get("title", "")
    english_words = [
        w for w in _extract_ascii_words(title) if len(w) > 1 and w[0].isupper()
    ]

    if english_words:
        key_part = " ".join(english_words[:5])
        return _truncate(f"{label}: {key_part}", 55)

    if terms:
        key_part = ", ".join(terms[:4])
        return _truncate(f"{label}: {key_part}", 55)

    # Fallback to tags
    tags = post_info.get("tags", [])
    eng_tags = [t for t in tags if not _has_korean(t)][:4]
    if eng_tags:
        key_part = ", ".join(eng_tags)
        return _truncate(f"{label}: {key_part}", 55)

    return f"{label}: Technical Analysis"


def _make_english_subtitle(post_info: Dict) -> str:
    """Short subtitle from tech terms or tags."""
    terms = post_info.get("tech_terms", [])
    if terms:
        return " | ".join(terms[:5])
    tags = post_info.get("tags", [])
    eng_tags = [t for t in tags if not _has_korean(t)][:5]
    return " | ".join(eng_tags) if eng_tags else "Technical Analysis"


def _section_to_english(text: str, post_info: Dict) -> str:
    """Convert a section header to English-safe text."""
    # If already English, keep it
    if not _has_korean(text):
        return _truncate(text, 35)

    # Extract English words from the section
    english_parts = _extract_ascii_words(text)
    if english_parts:
        return _truncate(" ".join(english_parts[:5]), 35)

    # Map common Korean section prefixes to English
    kr_to_en = {
        "서론": "Introduction",
        "결론": "Conclusion",
        "개요": "Overview",
        "요약": "Summary",
        "참고": "References",
        "보안": "Security",
        "위협": "Threats",
        "대응": "Response",
        "분석": "Analysis",
        "설치": "Installation",
        "설정": "Configuration",
        "실습": "Hands-on Lab",
        "아키텍처": "Architecture",
        "모니터링": "Monitoring",
        "배포": "Deployment",
        "테스트": "Testing",
        "운영": "Operations",
        "비용": "Cost Analysis",
        "성능": "Performance",
        "사례": "Case Study",
        "트렌드": "Trends",
        "뉴스": "News",
        "블록체인": "Blockchain",
        "클라우드": "Cloud",
        "컨테이너": "Containers",
        "네트워크": "Network",
        "데이터": "Data",
        "인프라": "Infrastructure",
        "핵심 포인트": "Key Points",
        "빠른 참조": "Quick Reference",
        "포스팅 요약": "Post Summary",
        "위험 스코어카드": "Risk Scorecard",
    }
    for kr, en in kr_to_en.items():
        if kr in text:
            return en

    return "Topic"


def _extract_ascii_words(text: str) -> List[str]:
    """Extract ASCII-only words from mixed text (no Unicode word chars)."""
    return re.findall(r"[A-Za-z][A-Za-z0-9./_-]*", text)


def _highlight_to_english(key: str, desc: str) -> Tuple[str, str]:
    """Convert a highlight key/desc pair to English-safe text."""
    # If key is already English
    if not _has_korean(key):
        en_key = _truncate(key, 25)
    else:
        en_parts = _extract_ascii_words(key)
        en_key = " ".join(en_parts[:3]) if en_parts else "Highlight"
        en_key = _truncate(en_key, 25)

    if not _has_korean(desc):
        en_desc = _truncate(desc, 50)
    else:
        en_parts = _extract_ascii_words(desc)
        en_desc = " ".join(en_parts[:6]) if en_parts else "See details in post"
        en_desc = _truncate(en_desc, 50)

    return en_key, en_desc


# ---------------------------------------------------------------------------
# Layout selection
# ---------------------------------------------------------------------------


def select_layout(category: str, title: str, tags: List[str]) -> str:
    """Select the best SVG layout type based on post metadata."""
    cat = category.lower()
    title_lower = title.lower()

    if cat == "incident" or "postmortem" in title_lower or "post-mortem" in title_lower:
        return "flow"

    if (
        "weekly digest" in title_lower
        or "weekly-digest" in title_lower
        or "weekly_digest" in title_lower
        or "weekly digest" in title_lower.replace("_", " ")
        or "Weekly-Digest" in tags
        or "weekly digest" in " ".join(tags).lower().replace("-", " ")
    ):
        return "highlights"

    if cat in ("cloud", "kubernetes") and any(
        w in title_lower
        for w in (
            "architecture",
            "guide",
            "course",
            "complete",
            "master",
            "가이드",
            "과정",
            "아키텍처",
            "구축",
        )
    ):
        return "architecture"

    if any(w in title_lower for w in ("comparison", " vs ", " vs. ", "비교")):
        return "comparison"

    return "section_map"


def _get_config(category: str) -> Dict:
    """Get SVG config for category with fallback."""
    return CATEGORY_SVG_CONFIG.get(category.lower(), CATEGORY_SVG_CONFIG["tech"])


# ---------------------------------------------------------------------------
# SVG common parts
# ---------------------------------------------------------------------------


def _svg_header(config: Dict) -> str:
    """Common SVG header with defs, background, grid pattern."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <title>{config.get("title", "Tech Blog Content Summary")}</title>
  <defs>
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f0f23"/>
      <stop offset="50%" style="stop-color:#1a1a3e"/>
      <stop offset="100%" style="stop-color:#0d1117"/>
    </linearGradient>
    <linearGradient id="cardGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e293b"/>
      <stop offset="100%" style="stop-color:#0f172a"/>
    </linearGradient>
    <linearGradient id="catGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{config["gradient_start"]}"/>
      <stop offset="100%" style="stop-color:{config["gradient_end"]}"/>
    </linearGradient>
    <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#3b82f6"/>
      <stop offset="50%" style="stop-color:#8b5cf6"/>
      <stop offset="100%" style="stop-color:#ec4899"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.3"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bgGradient)"/>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#ffffff" stroke-opacity="0.03" stroke-width="1"/>
  </pattern>
  <rect width="1200" height="630" fill="url(#grid)"/>

  <!-- Ambient circles -->
  <circle cx="100" cy="100" r="200" fill="{config["accent"]}" fill-opacity="0.05"/>
  <circle cx="1100" cy="530" r="250" fill="#8b5cf6" fill-opacity="0.05"/>
  <circle cx="600" cy="315" r="300" fill="{config["gradient_start"]}" fill-opacity="0.03"/>
'''


def _svg_top_badges(config: Dict, date_str: str) -> str:
    """Category badge (left) and date badge (right)."""
    return f"""  <!-- Top badges -->
  <rect x="40" y="30" width="180" height="36" rx="18" fill="url(#catGradient)" filter="url(#shadow)"/>
  <text x="130" y="54" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">{_escape_svg_text(config["label"])}</text>

  <rect x="980" y="30" width="180" height="36" rx="18" fill="url(#accentGradient)" filter="url(#shadow)"/>
  <text x="1070" y="54" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">{_escape_svg_text(date_str)}</text>
"""


def _svg_title_block(
    title: str, subtitle: str, y_title: int = 110, y_sub: int = 145
) -> str:
    """Title and subtitle centered text."""
    return f'''  <!-- Title -->
  <text x="600" y="{y_title}" font-family="Arial, sans-serif" font-size="32" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">{_escape_svg_text(title)}</text>
  <text x="600" y="{y_sub}" font-family="Arial, sans-serif" font-size="16" fill="#94a3b8" text-anchor="middle">{_escape_svg_text(subtitle)}</text>
  <rect x="350" y="{y_sub + 15}" width="500" height="3" fill="url(#accentGradient)" rx="1.5"/>
'''


def _svg_footer() -> str:
    """Blog branding footer."""
    return """  <!-- Footer -->
  <line x1="50" y1="565" x2="1150" y2="565" stroke="#334155" stroke-width="1"/>
  <text x="60" y="593" font-family="Arial, sans-serif" font-size="18" font-weight="bold" fill="white">Twodragon Tech Blog</text>
  <text x="60" y="615" font-family="Arial, sans-serif" font-size="13" fill="#64748b">tech.2twodragon.com</text>
  <text x="1150" y="605" font-family="Arial, sans-serif" font-size="13" fill="#64748b" text-anchor="end">DevSecOps | Cloud | Security</text>
</svg>"""


# ---------------------------------------------------------------------------
# Layout 1: Section Map (default)
# ---------------------------------------------------------------------------


def _generate_section_map(post_info: Dict) -> str:
    """Grid of topic cards from H2 sections."""
    config = _get_config(post_info["category"])
    date_str = post_info["date"].strftime("%B %d, %Y")
    title = _make_english_title(post_info)
    subtitle = _make_english_subtitle(post_info)

    # Collect H2 sections only, skip meta sections
    skip_words = {"summary", "references", "conclusion", "source"}
    h2_sections = []
    for s in post_info["sections"]:
        if s["level"] == 2:
            en = _section_to_english(s["text"], post_info)
            if en.lower() not in skip_words and en != "Topic":
                h2_sections.append(en)
    # Fill with tech terms if not enough sections
    while len(h2_sections) < 4:
        terms = post_info.get("tech_terms", [])
        idx = len(h2_sections)
        if idx < len(terms):
            h2_sections.append(terms[idx])
        else:
            h2_sections.append(f"Section {len(h2_sections) + 1}")
    h2_sections = h2_sections[:6]

    svg = _svg_header(config)
    svg += _svg_top_badges(config, date_str)
    svg += _svg_title_block(title, subtitle)

    # Grid layout: up to 3 columns x 2 rows
    cols = min(3, len(h2_sections))
    rows = (len(h2_sections) + cols - 1) // cols
    card_w = 320
    card_h = 100 if rows <= 2 else 80
    gap_x = 30
    gap_y = 20
    grid_w = cols * card_w + (cols - 1) * gap_x
    start_x = (1200 - grid_w) // 2
    start_y = 185

    svg += "\n  <!-- Section grid -->\n"
    for i, section in enumerate(h2_sections):
        col = i % cols
        row = i // cols
        x = start_x + col * (card_w + gap_x)
        y = start_y + row * (card_h + gap_y)
        accent = config["accent"]

        svg += f'  <rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="12" fill="url(#cardGradient)" filter="url(#shadow)"/>\n'
        svg += f'  <rect x="{x}" y="{y}" width="{card_w}" height="4" rx="2" fill="{accent}"/>\n'
        # Section number circle
        cx = x + 30
        cy = y + card_h // 2
        svg += f'  <circle cx="{cx}" cy="{cy}" r="16" fill="{accent}" fill-opacity="0.2"/>\n'
        svg += f'  <text x="{cx}" y="{cy + 5}" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="{accent}" text-anchor="middle">{i + 1}</text>\n'
        # Section text
        tx = x + 58
        ty = y + card_h // 2 + 5
        svg += f'  <text x="{tx}" y="{ty}" font-family="Arial, sans-serif" font-size="15" fill="white">{_escape_svg_text(_truncate(section, 32))}</text>\n'

    # Tag pills below grid
    tag_y = start_y + rows * (card_h + gap_y) + 20
    tags = [t for t in post_info.get("tags", []) if not _has_korean(t)][:5]
    if tags:
        svg += "\n  <!-- Tags -->\n"
        tag_x = start_x
        for tag in tags:
            tag_text = f"#{tag}"
            tag_w = len(tag_text) * 7 + 20
            svg += f'  <rect x="{tag_x}" y="{tag_y}" width="{tag_w}" height="26" rx="13" fill="{config["accent"]}" fill-opacity="0.15"/>\n'
            svg += f'  <text x="{tag_x + tag_w // 2}" y="{tag_y + 17}" font-family="Arial, sans-serif" font-size="11" fill="{config["accent"]}" text-anchor="middle">{_escape_svg_text(tag_text)}</text>\n'
            tag_x += tag_w + 10

    svg += "\n"
    svg += _svg_footer()
    return svg


# ---------------------------------------------------------------------------
# Layout 2: Flow Diagram (incident/postmortem)
# ---------------------------------------------------------------------------


def _generate_flow(post_info: Dict) -> str:
    """Timeline/steps layout for incident and postmortem posts."""
    config = _get_config(post_info["category"])
    date_str = post_info["date"].strftime("%B %d, %Y")
    title = _make_english_title(post_info)
    subtitle = _make_english_subtitle(post_info)

    # Collect steps from H2/H3 sections
    steps = []
    for s in post_info["sections"]:
        en = _section_to_english(s["text"], post_info)
        if en and en != "Topic" and en.lower() not in ("post summary", "references"):
            steps.append(en)
    steps = steps[:6]
    while len(steps) < 3:
        steps.append(f"Phase {len(steps) + 1}")

    svg = _svg_header(config)
    svg += _svg_top_badges(config, date_str)

    # Add "INCIDENT TIMELINE" label next to category badge
    svg += '  <rect x="240" y="30" width="200" height="36" rx="18" fill="#1e293b" stroke="#f87171" stroke-width="1"/>\n'
    svg += '  <text x="340" y="54" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="#f87171" text-anchor="middle">INCIDENT TIMELINE</text>\n'

    svg += _svg_title_block(title, subtitle)

    # Timeline
    n = len(steps)
    timeline_y = 280
    margin_x = 80
    usable_w = 1200 - 2 * margin_x
    step_gap = usable_w / max(n - 1, 1) if n > 1 else 0

    svg += "\n  <!-- Timeline -->\n"

    # Horizontal line
    line_x1 = margin_x + 20
    line_x2 = 1200 - margin_x - 20
    svg += f'  <line x1="{line_x1}" y1="{timeline_y}" x2="{line_x2}" y2="{timeline_y}" stroke="{config["accent"]}" stroke-width="3" stroke-opacity="0.4"/>\n'

    # Arrow at end
    svg += f'  <polygon points="{line_x2},{timeline_y - 6} {line_x2 + 12},{timeline_y} {line_x2},{timeline_y + 6}" fill="{config["accent"]}" fill-opacity="0.6"/>\n'

    colors = ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#10b981", "#ec4899"]

    for i, step in enumerate(steps):
        cx = margin_x + 20 + i * step_gap if n > 1 else 600
        cy = timeline_y
        color = colors[i % len(colors)]

        # Node circle
        svg += f'  <circle cx="{cx}" cy="{cy}" r="22" fill="{color}" fill-opacity="0.2" stroke="{color}" stroke-width="2"/>\n'
        svg += f'  <text x="{cx}" y="{cy + 5}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="{color}" text-anchor="middle">{i + 1}</text>\n'

        # Step label (alternate above/below for readability)
        if i % 2 == 0:
            label_y = cy - 40
        else:
            label_y = cy + 50

        label = _escape_svg_text(_truncate(step, 18))
        svg += f'  <text x="{cx}" y="{label_y}" font-family="Arial, sans-serif" font-size="12" fill="white" text-anchor="middle">{label}</text>\n'

    # Summary cards below timeline
    card_y = 370
    highlights = post_info.get("highlights", [])[:3]
    if highlights:
        svg += "\n  <!-- Summary cards -->\n"
        card_w = 340
        card_gap = 25
        total_w = len(highlights) * card_w + (len(highlights) - 1) * card_gap
        sx = (1200 - total_w) // 2
        for i, h in enumerate(highlights):
            x = sx + i * (card_w + card_gap)
            en_key, en_desc = _highlight_to_english(h["key"], h["desc"])
            svg += f'  <rect x="{x}" y="{card_y}" width="{card_w}" height="70" rx="10" fill="url(#cardGradient)" filter="url(#shadow)"/>\n'
            svg += f'  <rect x="{x}" y="{card_y}" width="{card_w}" height="4" rx="2" fill="{colors[i % len(colors)]}"/>\n'
            svg += f'  <text x="{x + 15}" y="{card_y + 28}" font-family="Arial, sans-serif" font-size="13" font-weight="bold" fill="{colors[i % len(colors)]}">{_escape_svg_text(en_key)}</text>\n'
            svg += f'  <text x="{x + 15}" y="{card_y + 50}" font-family="Arial, sans-serif" font-size="11" fill="#94a3b8">{_escape_svg_text(_truncate(en_desc, 45))}</text>\n'

    svg += "\n"
    svg += _svg_footer()
    return svg


# ---------------------------------------------------------------------------
# Layout 3: Highlight Cards (weekly digest)
# ---------------------------------------------------------------------------


def _generate_highlights(post_info: Dict) -> str:
    """Prominent highlight cards for weekly digest posts."""
    config = _get_config(post_info["category"])
    date_str = post_info["date"].strftime("%B %d, %Y")
    title = _make_english_title(post_info)
    subtitle = _make_english_subtitle(post_info)

    highlights = post_info.get("highlights", [])
    # If no highlights, use sections
    if not highlights:
        for s in post_info["sections"]:
            if s["level"] == 2:
                en = _section_to_english(s["text"], post_info)
                if en != "Topic":
                    highlights.append({"key": en, "desc": ""})
        highlights = highlights[:4]
    else:
        highlights = highlights[:4]

    # Pad to at least 3
    while len(highlights) < 3:
        highlights.append(
            {
                "key": f"Update {len(highlights) + 1}",
                "desc": "See details in the full post",
            }
        )

    svg = _svg_header(config)
    svg += _svg_top_badges(config, date_str)
    svg += _svg_title_block(title, subtitle)

    # Highlight cards - large prominent cards
    n = len(highlights)
    card_w = 250
    card_h = 200
    gap = 25
    total_w = n * card_w + (n - 1) * gap
    start_x = (1200 - total_w) // 2
    start_y = 185

    icons = ["01", "02", "03", "04"]
    colors = ["#ef4444", "#3b82f6", "#10b981", "#f59e0b"]

    svg += "\n  <!-- Highlight cards -->\n"
    for i, h in enumerate(highlights):
        x = start_x + i * (card_w + gap)
        y = start_y
        color = colors[i % len(colors)]
        en_key, en_desc = _highlight_to_english(h["key"], h["desc"])

        # Card background
        svg += f'  <rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="16" fill="url(#cardGradient)" filter="url(#shadow)"/>\n'
        # Top accent bar
        svg += f'  <rect x="{x}" y="{y}" width="{card_w}" height="5" rx="3" fill="{color}"/>\n'

        # Icon area
        icon_cx = x + card_w // 2
        icon_cy = y + 50
        svg += f'  <circle cx="{icon_cx}" cy="{icon_cy}" r="24" fill="{color}" fill-opacity="0.15"/>\n'
        svg += f'  <text x="{icon_cx}" y="{icon_cy + 6}" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="{color}" text-anchor="middle">{icons[i]}</text>\n'

        # Key text
        svg += f'  <text x="{icon_cx}" y="{y + 100}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">{_escape_svg_text(_truncate(en_key, 28))}</text>\n'

        # Description (wrap into 2 lines)
        if en_desc:
            line1 = _truncate(en_desc, 30)
            rest = en_desc[30:].strip() if len(en_desc) > 30 else ""
            line2 = _truncate(rest, 30) if rest else ""
            svg += f'  <text x="{icon_cx}" y="{y + 125}" font-family="Arial, sans-serif" font-size="11" fill="#94a3b8" text-anchor="middle">{_escape_svg_text(line1)}</text>\n'
            if line2:
                svg += f'  <text x="{icon_cx}" y="{y + 142}" font-family="Arial, sans-serif" font-size="11" fill="#94a3b8" text-anchor="middle">{_escape_svg_text(line2)}</text>\n'

    # Tags below cards
    tag_y = start_y + card_h + 25
    tags = [t for t in post_info.get("tags", []) if not _has_korean(t)][:6]
    if tags:
        svg += "\n  <!-- Tags -->\n"
        tag_x = start_x
        for tag in tags:
            tag_text = f"#{tag}"
            tag_w = len(tag_text) * 7 + 18
            svg += f'  <rect x="{tag_x}" y="{tag_y}" width="{tag_w}" height="24" rx="12" fill="{config["accent"]}" fill-opacity="0.15"/>\n'
            svg += f'  <text x="{tag_x + tag_w // 2}" y="{tag_y + 16}" font-family="Arial, sans-serif" font-size="10" fill="{config["accent"]}" text-anchor="middle">{_escape_svg_text(tag_text)}</text>\n'
            tag_x += tag_w + 8

    svg += "\n"
    svg += _svg_footer()
    return svg


# ---------------------------------------------------------------------------
# Layout 4: Architecture Overview (cloud/k8s guide)
# ---------------------------------------------------------------------------


def _generate_architecture(post_info: Dict) -> str:
    """3-layer architecture diagram for cloud/k8s guide posts."""
    config = _get_config(post_info["category"])
    date_str = post_info["date"].strftime("%B %d, %Y")
    title = _make_english_title(post_info)
    subtitle = _make_english_subtitle(post_info)

    # Classify sections into 3 layers
    top_layer = []  # management / control / security
    mid_layer = []  # services / compute / application
    bot_layer = []  # infrastructure / network / storage

    top_kw = {
        "security",
        "management",
        "control",
        "monitoring",
        "policy",
        "iam",
        "governance",
        "compliance",
        "audit",
    }
    bot_kw = {
        "infrastructure",
        "network",
        "storage",
        "vpc",
        "dns",
        "cdn",
        "bgp",
        "load",
        "alb",
        "data",
    }

    for s in post_info["sections"]:
        en = _section_to_english(s["text"], post_info)
        if en == "Topic" or en.lower() in ("post summary", "references", "conclusion"):
            continue
        lower = en.lower()
        if any(k in lower for k in top_kw):
            top_layer.append(en)
        elif any(k in lower for k in bot_kw):
            bot_layer.append(en)
        else:
            mid_layer.append(en)

    # Rebalance
    while len(top_layer) < 2 and mid_layer:
        top_layer.append(mid_layer.pop(0))
    while len(bot_layer) < 2 and mid_layer:
        bot_layer.append(mid_layer.pop())

    # Pad with tech terms if needed
    terms = post_info.get("tech_terms", [])
    for layer, defaults in [
        (top_layer, ["Security", "Management", "Monitoring"]),
        (mid_layer, ["Services", "Compute", "Application"]),
        (bot_layer, ["Infrastructure", "Network", "Storage"]),
    ]:
        idx = 0
        while len(layer) < 2:
            if idx < len(terms):
                layer.append(terms[idx])
                idx += 1
            elif defaults:
                layer.append(defaults.pop(0))
            else:
                layer.append("Component")

    top_layer = top_layer[:4]
    mid_layer = mid_layer[:4]
    bot_layer = bot_layer[:4]

    svg = _svg_header(config)
    svg += _svg_top_badges(config, date_str)
    svg += _svg_title_block(title, subtitle, y_title=105, y_sub=135)

    # Three horizontal layers
    layer_colors = ["#8b5cf6", "#3b82f6", "#10b981"]
    layer_labels = ["Control Plane", "Services", "Infrastructure"]
    layers = [top_layer, mid_layer, bot_layer]

    layer_h = 95
    layer_gap = 15
    start_y = 170
    margin_x = 60

    svg += "\n  <!-- Architecture layers -->\n"
    for li, (items, color, label) in enumerate(zip(layers, layer_colors, layer_labels)):
        y = start_y + li * (layer_h + layer_gap)
        # Layer background
        svg += f'  <rect x="{margin_x}" y="{y}" width="{1200 - 2 * margin_x}" height="{layer_h}" rx="12" fill="{color}" fill-opacity="0.08" stroke="{color}" stroke-width="1" stroke-opacity="0.3"/>\n'
        # Layer label
        svg += f'  <text x="{margin_x + 15}" y="{y + 22}" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="{color}">{label}</text>\n'

        # Items as boxes inside layer
        n_items = len(items)
        item_w = 220
        item_h = 42
        items_total_w = n_items * item_w + (n_items - 1) * 15
        ix = (1200 - items_total_w) // 2
        iy = y + 38

        for j, item in enumerate(items):
            bx = ix + j * (item_w + 15)
            svg += f'  <rect x="{bx}" y="{iy}" width="{item_w}" height="{item_h}" rx="8" fill="#0f172a" stroke="{color}" stroke-width="1" stroke-opacity="0.5"/>\n'
            svg += f'  <text x="{bx + item_w // 2}" y="{iy + item_h // 2 + 5}" font-family="Arial, sans-serif" font-size="13" fill="white" text-anchor="middle">{_escape_svg_text(_truncate(item, 25))}</text>\n'

    # Vertical connectors between layers
    svg += "\n  <!-- Connectors -->\n"
    for li in range(2):
        y1 = start_y + li * (layer_h + layer_gap) + layer_h
        y2 = y1 + layer_gap
        for cx in [400, 600, 800]:
            svg += f'  <line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}" stroke="#475569" stroke-width="1" stroke-dasharray="4,4"/>\n'
            svg += f'  <polygon points="{cx - 4},{y2 - 4} {cx + 4},{y2 - 4} {cx},{y2}" fill="#475569"/>\n'

    # Tags row
    tag_y = start_y + 3 * (layer_h + layer_gap) + 10
    tags = [t for t in post_info.get("tags", []) if not _has_korean(t)][:6]
    if tags:
        svg += "\n  <!-- Tags -->\n"
        tag_x = margin_x
        for tag in tags:
            tag_text = f"#{tag}"
            tag_w = len(tag_text) * 7 + 18
            svg += f'  <rect x="{tag_x}" y="{tag_y}" width="{tag_w}" height="24" rx="12" fill="{config["accent"]}" fill-opacity="0.15"/>\n'
            svg += f'  <text x="{tag_x + tag_w // 2}" y="{tag_y + 16}" font-family="Arial, sans-serif" font-size="10" fill="{config["accent"]}" text-anchor="middle">{_escape_svg_text(tag_text)}</text>\n'
            tag_x += tag_w + 8

    svg += "\n"
    svg += _svg_footer()
    return svg


# ---------------------------------------------------------------------------
# Layout 5: Comparison Grid
# ---------------------------------------------------------------------------


def _generate_comparison(post_info: Dict) -> str:
    """Table-like comparison grid for analysis/comparison posts."""
    config = _get_config(post_info["category"])
    date_str = post_info["date"].strftime("%B %d, %Y")
    title = _make_english_title(post_info)
    subtitle = _make_english_subtitle(post_info)

    # Build comparison items from H2 sections or highlights
    items = []
    for s in post_info["sections"]:
        if s["level"] == 2:
            en = _section_to_english(s["text"], post_info)
            if en != "Topic" and en.lower() not in (
                "post summary",
                "references",
                "conclusion",
            ):
                items.append(en)
    items = items[:6]

    while len(items) < 3:
        terms = post_info.get("tech_terms", [])
        idx = len(items)
        items.append(terms[idx] if idx < len(terms) else f"Aspect {len(items) + 1}")

    # Extract comparison subjects from title (A vs B)
    vs_match = re.search(
        r"(.+?)\s+vs\.?\s+(.+?)(?:\s*[:|-]|\s*$)", post_info["title"], re.IGNORECASE
    )
    if vs_match:
        col_a = _truncate(vs_match.group(1).strip(), 20)
        col_b = _truncate(vs_match.group(2).strip(), 20)
        # Clean Korean if needed
        if _has_korean(col_a):
            parts = re.findall(r"[A-Za-z][\w./-]+", col_a)
            col_a = " ".join(parts[:2]) if parts else "Option A"
        if _has_korean(col_b):
            parts = re.findall(r"[A-Za-z][\w./-]+", col_b)
            col_b = " ".join(parts[:2]) if parts else "Option B"
    else:
        col_a = "Option A"
        col_b = "Option B"

    svg = _svg_header(config)
    svg += _svg_top_badges(config, date_str)
    svg += _svg_title_block(title, subtitle)

    # Table layout
    table_x = 100
    table_w = 1000
    col_w_aspect = 300
    col_w_val = 350
    row_h = 50
    header_h = 45
    start_y = 185

    svg += "\n  <!-- Comparison grid -->\n"

    # Header row
    svg += f'  <rect x="{table_x}" y="{start_y}" width="{table_w}" height="{header_h}" rx="10" fill="{config["accent"]}" fill-opacity="0.15"/>\n'
    svg += f'  <text x="{table_x + col_w_aspect // 2}" y="{start_y + 28}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="{config["accent"]}" text-anchor="middle">ASPECT</text>\n'
    svg += f'  <text x="{table_x + col_w_aspect + col_w_val // 2}" y="{start_y + 28}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#3b82f6" text-anchor="middle">{_escape_svg_text(col_a)}</text>\n'
    svg += f'  <text x="{table_x + col_w_aspect + col_w_val + col_w_val // 2}" y="{start_y + 28}" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#10b981" text-anchor="middle">{_escape_svg_text(col_b)}</text>\n'

    # Data rows
    row_colors = ["#1e293b", "#162032"]
    for i, item in enumerate(items):
        ry = start_y + header_h + i * row_h
        bg = row_colors[i % 2]
        rx_val = "0" if i < len(items) - 1 else "10"

        if i == len(items) - 1:
            svg += f'  <rect x="{table_x}" y="{ry}" width="{table_w}" height="{row_h}" rx="0" fill="{bg}"/>\n'
            # Bottom rounded corners hack: overlay
            svg += f'  <rect x="{table_x}" y="{ry + row_h - 10}" width="{table_w}" height="10" rx="10" fill="{bg}"/>\n'
        else:
            svg += f'  <rect x="{table_x}" y="{ry}" width="{table_w}" height="{row_h}" fill="{bg}"/>\n'

        # Aspect name
        svg += f'  <text x="{table_x + 20}" y="{ry + 30}" font-family="Arial, sans-serif" font-size="13" fill="white">{_escape_svg_text(_truncate(item, 35))}</text>\n'

        # Placeholder comparison dots
        dot_y = ry + 25
        for col_offset, color in [
            (col_w_aspect + col_w_val // 2, "#3b82f6"),
            (col_w_aspect + col_w_val + col_w_val // 2, "#10b981"),
        ]:
            cx = table_x + col_offset
            # Rating dots (visual)
            n_dots = (i % 3) + 3
            dot_start = cx - (n_dots * 14) // 2
            for d in range(5):
                dx = dot_start + d * 14
                opacity = "1.0" if d < n_dots else "0.2"
                svg += f'  <circle cx="{dx}" cy="{dot_y}" r="5" fill="{color}" fill-opacity="{opacity}"/>\n'

    svg += "\n"
    svg += _svg_footer()
    return svg


# ---------------------------------------------------------------------------
# SVG generation dispatcher
# ---------------------------------------------------------------------------

LAYOUT_GENERATORS = {
    "section_map": _generate_section_map,
    "flow": _generate_flow,
    "highlights": _generate_highlights,
    "architecture": _generate_architecture,
    "comparison": _generate_comparison,
}


def generate_content_summary_svg(post_info: Dict) -> str:
    """Generate SVG content summary for a post, auto-selecting layout."""
    layout = select_layout(
        post_info["category"],
        post_info["title"],
        post_info["tags"],
    )
    log_message(f"  Layout: {layout} | Category: {post_info['category']}")
    generator = LAYOUT_GENERATORS[layout]
    return generator(post_info)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_svg(svg_content: str, filename: str) -> bool:
    """Validate SVG is well-formed XML and contains no Korean text."""
    ok = True

    # XML parse check
    try:
        ET.fromstring(svg_content)
    except ET.ParseError as e:
        log_message(f"  SVG XML parse error in {filename}: {e}", "ERROR")
        ok = False

    # Korean text check (scan text content only, not attributes like font-family)
    # Extract text between > and <
    text_segments = re.findall(r">([^<]+)<", svg_content)
    for seg in text_segments:
        seg_clean = seg.strip()
        if seg_clean and _has_korean(seg_clean):
            log_message(
                f"  Korean text found in {filename}: '{_truncate(seg_clean, 40)}'",
                "WARNING",
            )
            ok = False
            break

    return ok


# ---------------------------------------------------------------------------
# PNG conversion
# ---------------------------------------------------------------------------


def convert_to_png(svg_path: Path, png_path: Path) -> bool:
    """Convert SVG to PNG using cairosvg."""
    if not CAIROSVG_AVAILABLE:
        return False
    try:
        cairosvg.svg2png(
            url=str(svg_path),
            write_to=str(png_path),
            output_width=1200,
            output_height=630,
        )
        return True
    except Exception as e:
        log_message(f"  PNG conversion failed: {e}", "WARNING")
        return False


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------


def _get_image_stem(post_info: Dict) -> str:
    """Determine the image filename stem from post metadata."""
    image_field = post_info.get("image", "")
    if image_field:
        # /assets/images/STEM.svg -> STEM
        stem = Path(image_field).stem
        if stem:
            return stem

    # Fallback: use post filename stem
    return post_info["stem"]


def process_post(post_file: Path, force: bool = False) -> bool:
    """Process a single post: extract info, generate SVG + PNG."""
    post_info = extract_post_info(post_file)
    if not post_info:
        return False

    stem = _get_image_stem(post_info)
    svg_path = IMAGES_DIR / f"{stem}-content-summary.svg"
    png_path = IMAGES_DIR / f"{stem}-content-summary.png"

    # Skip if both exist and not forcing
    if not force and svg_path.exists() and png_path.exists():
        log_message(f"  Skip (exists): {svg_path.name}", "INFO")
        return True

    if not force and svg_path.exists() and not CAIROSVG_AVAILABLE:
        log_message(f"  Skip (SVG exists, no cairosvg): {svg_path.name}", "INFO")
        return True

    # Generate SVG
    try:
        svg_content = generate_content_summary_svg(post_info)
    except Exception as e:
        log_message(f"  SVG generation failed for {post_file.name}: {e}", "ERROR")
        return False

    # Validate
    is_valid = validate_svg(svg_content, svg_path.name)
    if not is_valid:
        log_message(
            f"  SVG validation issues for {svg_path.name} (writing anyway)", "WARNING"
        )

    # Write SVG
    try:
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        log_message(f"  SVG saved: {svg_path.name}", "SUCCESS")
    except Exception as e:
        log_message(f"  SVG write failed: {e}", "ERROR")
        return False

    # Convert to PNG
    if CAIROSVG_AVAILABLE:
        if convert_to_png(svg_path, png_path):
            log_message(f"  PNG saved: {png_path.name}", "SUCCESS")
        else:
            log_message("  PNG conversion skipped", "WARNING")
    else:
        log_message("  PNG skipped (cairosvg not available)", "INFO")

    return True


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate content-summary SVG infographics for blog posts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/generate_content_summary.py --all
  python3 scripts/generate_content_summary.py --recent 5
  python3 scripts/generate_content_summary.py --post _posts/2026-02-23-Example.md
  python3 scripts/generate_content_summary.py --all --force
        """,
    )
    parser.add_argument("--all", action="store_true", help="Process all posts")
    parser.add_argument(
        "--recent", type=int, default=0, help="Process N most recent posts"
    )
    parser.add_argument(
        "--post", type=str, default="", help="Process a specific post file"
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing images"
    )

    args = parser.parse_args()

    # Determine which posts to process
    posts: List[Path] = []

    if args.post:
        p = Path(args.post)
        if not p.is_absolute():
            p = PROJECT_ROOT / p
        if not p.exists():
            log_message(f"Post file not found: {p}", "ERROR")
            sys.exit(1)
        posts = [p]
    elif args.all:
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda x: x.name)
    elif args.recent > 0:
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda x: x.name, reverse=True)[
            : args.recent
        ]
    else:
        # Default: most recent 1
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda x: x.name, reverse=True)[:1]

    if not posts:
        log_message("No posts found to process.", "ERROR")
        sys.exit(1)

    log_message(
        f"Processing {len(posts)} post(s)  |  force={args.force}  |  cairosvg={'yes' if CAIROSVG_AVAILABLE else 'no'}"
    )
    log_message("=" * 70)

    stats = {"success": 0, "skipped": 0, "failed": 0}
    layout_counts: Dict[str, int] = {}

    for post_file in posts:
        log_message(f"Post: {post_file.name}")
        try:
            # Peek at layout for stats
            info = extract_post_info(post_file)
            if info:
                layout = select_layout(info["category"], info["title"], info["tags"])
                layout_counts[layout] = layout_counts.get(layout, 0) + 1

            result = process_post(post_file, force=args.force)
            if result:
                stats["success"] += 1
            else:
                stats["failed"] += 1
        except Exception as e:
            log_message(f"  Unexpected error: {e}", "ERROR")
            stats["failed"] += 1

    # Summary
    log_message("=" * 70)
    log_message(f"Results: {stats['success']} success, {stats['failed']} failed")
    log_message(f"Layout distribution: {layout_counts}")
    if not CAIROSVG_AVAILABLE:
        log_message("Install cairosvg for PNG output: pip install cairosvg", "INFO")
    log_message("Done.")


if __name__ == "__main__":
    main()
