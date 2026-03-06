#!/usr/bin/env python3
"""Generate rich SVG images for digest posts matching the reference style."""

import os
import re
import yaml
import hashlib
from pathlib import Path

POSTS_DIR = Path("/Users/yong/Desktop/tech-blog/_posts")
IMAGES_DIR = Path("/Users/yong/Desktop/tech-blog/assets/images")

# Reference SVG style from 2026-03-05 - the "good" style
# Posts that already have the good style - skip these
SKIP_FILES = set()  # Regenerate all

# Topic keyword -> (icon_color, topic_label, icon_svg_snippet)
TOPIC_ICONS = {
    "ransomware": ("#ef4444", "Ransomware", "lock"),
    "malware": ("#ef4444", "Malware", "bug"),
    "phishing": ("#f87171", "Phishing", "mail"),
    "zero-day": ("#dc2626", "Zero-Day", "alert"),
    "zero_day": ("#dc2626", "Zero-Day", "alert"),
    "cve": ("#ef4444", "CVE Alert", "alert"),
    "vulnerability": ("#ef4444", "Vulnerability", "alert"),
    "exploit": ("#dc2626", "Exploit", "alert"),
    "botnet": ("#f87171", "Botnet", "network"),
    "ddos": ("#ef4444", "DDoS", "network"),
    "vishing": ("#f87171", "Vishing", "phone"),
    "ai": ("#818cf8", "AI/ML", "brain"),
    "llm": ("#818cf8", "LLM", "brain"),
    "agentic": ("#a78bfa", "AI Agent", "brain"),
    "openai": ("#818cf8", "OpenAI", "brain"),
    "gemini": ("#818cf8", "Gemini AI", "brain"),
    "docker": ("#2496ed", "Docker", "container"),
    "kubernetes": ("#326ce5", "Kubernetes", "container"),
    "k8s": ("#326ce5", "Kubernetes", "container"),
    "cloud": ("#06b6d4", "Cloud", "cloud"),
    "aws": ("#ff9900", "AWS", "cloud"),
    "gcp": ("#4285f4", "GCP", "cloud"),
    "azure": ("#0078d4", "Azure", "cloud"),
    "blockchain": ("#f59e0b", "Blockchain", "chain"),
    "bitcoin": ("#f7931a", "Bitcoin", "chain"),
    "crypto": ("#f59e0b", "Crypto", "chain"),
    "devops": ("#10b981", "DevOps", "gear"),
    "devsecops": ("#8b5cf6", "DevSecOps", "shield"),
    "security": ("#ef4444", "Security", "shield"),
    "threat": ("#ef4444", "Threat Intel", "shield"),
    "zero_trust": ("#6366f1", "Zero Trust", "shield"),
    "zero-trust": ("#6366f1", "Zero Trust", "shield"),
    "fortinet": ("#ef4444", "Fortinet", "shield"),
    "solarwinds": ("#ef4444", "SolarWinds", "shield"),
    "vmware": ("#607078", "VMware", "server"),
    "microsoft": ("#0078d4", "Microsoft", "server"),
    "chrome": ("#4285f4", "Chrome", "browser"),
    "terraform": ("#7b42bc", "Terraform", "gear"),
    "golang": ("#00add8", "Go", "code"),
    "go": ("#00add8", "Go", "code"),
    "rust": ("#dea584", "Rust", "code"),
    "data": ("#3b82f6", "Data", "database"),
    "rce": ("#dc2626", "RCE", "alert"),
    "supply_chain": ("#f59e0b", "Supply Chain", "chain"),
    "ot": ("#f59e0b", "OT/ICS", "gear"),
    "patch": ("#10b981", "Patch", "shield"),
    "finops": ("#3b82f6", "FinOps", "chart"),
    "prometheus": ("#e6522c", "Prometheus", "chart"),
    "rss": ("#f59e0b", "RSS Feed", "feed"),
}

# Color palettes for different primary themes
ACCENT_PALETTES = {
    "security": {"accent1": "#ef4444", "accent1_dark": "#dc2626", "accent2": "#6366f1", "accent2_dark": "#4f46e5"},
    "ai": {"accent1": "#6366f1", "accent1_dark": "#4f46e5", "accent2": "#10b981", "accent2_dark": "#059669"},
    "cloud": {"accent1": "#06b6d4", "accent1_dark": "#0891b2", "accent2": "#8b5cf6", "accent2_dark": "#7c3aed"},
    "blockchain": {"accent1": "#f59e0b", "accent1_dark": "#d97706", "accent2": "#ef4444", "accent2_dark": "#dc2626"},
    "devops": {"accent1": "#10b981", "accent1_dark": "#059669", "accent2": "#3b82f6", "accent2_dark": "#2563eb"},
    "default": {"accent1": "#6366f1", "accent1_dark": "#4f46e5", "accent2": "#ef4444", "accent2_dark": "#dc2626"},
}

# Icon SVG snippets for left-side visualization
ICON_SVGS = {
    "shield": """<path d="M60 0 L120 30 L120 75 C120 120 90 150 60 165 C30 150 0 120 0 75 L0 30 Z" fill="url(#accent)" opacity="0.9"/>
    <path d="M60 15 L110 40 L110 75 C110 112 85 138 60 150 C35 138 10 112 10 75 L10 40 Z" fill="none" stroke="{light}" stroke-width="2"/>
    <text x="60" y="90" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="36" font-weight="bold">!</text>""",
    "lock": """<rect x="25" y="60" width="70" height="80" rx="8" fill="url(#accent)" opacity="0.9"/>
    <path d="M35 60 V40 C35 18 85 18 85 40 V60" fill="none" stroke="{light}" stroke-width="3"/>
    <circle cx="60" cy="100" r="10" fill="white"/>
    <rect x="57" y="100" width="6" height="18" rx="2" fill="white"/>""",
    "bug": """<ellipse cx="60" cy="80" rx="35" ry="45" fill="url(#accent)" opacity="0.9"/>
    <circle cx="48" cy="60" r="8" fill="white" opacity="0.8"/>
    <circle cx="72" cy="60" r="8" fill="white" opacity="0.8"/>
    <line x1="20" y1="60" x2="35" y2="70" stroke="{light}" stroke-width="2"/>
    <line x1="100" y1="60" x2="85" y2="70" stroke="{light}" stroke-width="2"/>
    <line x1="15" y1="90" x2="30" y2="85" stroke="{light}" stroke-width="2"/>
    <line x1="105" y1="90" x2="90" y2="85" stroke="{light}" stroke-width="2"/>""",
    "brain": """<circle cx="60" cy="70" r="45" fill="url(#accent)" opacity="0.15"/>
    <circle cx="60" cy="70" r="45" fill="none" stroke="{color}" stroke-width="2.5"/>
    <path d="M40 55 Q50 35 60 50 Q70 35 80 55" fill="none" stroke="{light}" stroke-width="2"/>
    <path d="M35 75 Q45 60 55 75 Q65 60 75 75 Q85 60 90 75" fill="none" stroke="{light}" stroke-width="2"/>
    <text x="60" y="105" text-anchor="middle" fill="{color}" font-family="monospace" font-size="14" font-weight="bold">AI</text>""",
    "cloud": """<path d="M90 120 L30 120 C13 120 0 107 0 90 C0 75 10 63 24 60 C24 35 45 15 70 15 C92 15 110 30 115 50 C128 52 138 63 138 78 C138 95 125 108 108 108" fill="none" stroke="{color}" stroke-width="2.5"/>
    <path d="M50 75 L65 90 L90 60" fill="none" stroke="{light}" stroke-width="3"/>""",
    "container": """<rect x="10" y="30" width="100" height="90" rx="6" fill="url(#accent)" opacity="0.2"/>
    <rect x="10" y="30" width="100" height="90" rx="6" fill="none" stroke="{color}" stroke-width="2.5"/>
    <line x1="10" y1="55" x2="110" y2="55" stroke="{color}" stroke-width="1.5"/>
    <circle cx="25" cy="43" r="4" fill="{light}"/>
    <circle cx="38" cy="43" r="4" fill="{light}"/>
    <circle cx="51" cy="43" r="4" fill="{light}"/>
    <rect x="20" y="65" width="80" height="8" rx="3" fill="{color}" opacity="0.4"/>
    <rect x="20" y="80" width="60" height="8" rx="3" fill="{color}" opacity="0.3"/>
    <rect x="20" y="95" width="70" height="8" rx="3" fill="{color}" opacity="0.35"/>""",
    "chain": """<circle cx="35" cy="50" r="20" fill="none" stroke="{color}" stroke-width="3"/>
    <circle cx="85" cy="50" r="20" fill="none" stroke="{light}" stroke-width="3"/>
    <circle cx="60" cy="100" r="20" fill="none" stroke="{color}" stroke-width="3"/>
    <line x1="50" y1="40" x2="70" y2="40" stroke="{light}" stroke-width="2"/>
    <line x1="45" y1="65" x2="50" y2="85" stroke="{color}" stroke-width="2"/>
    <line x1="75" y1="65" x2="70" y2="85" stroke="{light}" stroke-width="2"/>
    <text x="60" y="110" text-anchor="middle" fill="{color}" font-family="monospace" font-size="16" font-weight="bold">B</text>""",
    "network": """<circle cx="60" cy="40" r="15" fill="url(#accent)" opacity="0.8"/>
    <circle cx="20" cy="110" r="12" fill="url(#accent2)" opacity="0.8"/>
    <circle cx="100" cy="110" r="12" fill="url(#accent)" opacity="0.8"/>
    <circle cx="60" cy="140" r="10" fill="url(#accent2)" opacity="0.6"/>
    <line x1="60" y1="55" x2="20" y2="98" stroke="{light}" stroke-width="1.5"/>
    <line x1="60" y1="55" x2="100" y2="98" stroke="{light}" stroke-width="1.5"/>
    <line x1="20" y1="122" x2="60" y2="130" stroke="{light}" stroke-width="1.5"/>
    <line x1="100" y1="122" x2="60" y2="130" stroke="{light}" stroke-width="1.5"/>""",
    "alert": """<path d="M60 5 L115 120 L5 120 Z" fill="url(#accent)" opacity="0.9"/>
    <path d="M60 20 L105 115 L15 115 Z" fill="none" stroke="{light}" stroke-width="2"/>
    <text x="60" y="85" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="40" font-weight="bold">!</text>
    <circle cx="60" cy="100" r="4" fill="white"/>""",
    "gear": """<circle cx="60" cy="70" r="30" fill="url(#accent)" opacity="0.2"/>
    <circle cx="60" cy="70" r="30" fill="none" stroke="{color}" stroke-width="2.5"/>
    <circle cx="60" cy="70" r="12" fill="none" stroke="{light}" stroke-width="2"/>
    <rect x="55" y="35" width="10" height="15" rx="2" fill="{color}"/>
    <rect x="55" y="90" width="10" height="15" rx="2" fill="{color}"/>
    <rect x="25" y="65" width="15" height="10" rx="2" fill="{color}"/>
    <rect x="80" y="65" width="15" height="10" rx="2" fill="{color}"/>""",
    "server": """<rect x="15" y="10" width="90" height="40" rx="6" fill="url(#accent)" opacity="0.2" stroke="{color}" stroke-width="2"/>
    <circle cx="90" cy="30" r="5" fill="{light}"/>
    <rect x="25" y="25" width="40" height="4" rx="2" fill="{color}" opacity="0.5"/>
    <rect x="15" y="60" width="90" height="40" rx="6" fill="url(#accent)" opacity="0.2" stroke="{color}" stroke-width="2"/>
    <circle cx="90" cy="80" r="5" fill="{light}"/>
    <rect x="25" y="75" width="40" height="4" rx="2" fill="{color}" opacity="0.5"/>
    <rect x="15" y="110" width="90" height="40" rx="6" fill="url(#accent)" opacity="0.2" stroke="{color}" stroke-width="2"/>
    <circle cx="90" cy="130" r="5" fill="{light}"/>
    <rect x="25" y="125" width="40" height="4" rx="2" fill="{color}" opacity="0.5"/>""",
    "code": """<rect x="10" y="15" width="100" height="120" rx="8" fill="url(#accent)" opacity="0.15" stroke="{color}" stroke-width="2"/>
    <text x="60" y="55" text-anchor="middle" fill="{light}" font-family="monospace" font-size="18">&lt;/&gt;</text>
    <rect x="25" y="70" width="70" height="6" rx="3" fill="{color}" opacity="0.4"/>
    <rect x="25" y="85" width="50" height="6" rx="3" fill="{color}" opacity="0.3"/>
    <rect x="25" y="100" width="60" height="6" rx="3" fill="{color}" opacity="0.35"/>
    <rect x="25" y="115" width="40" height="6" rx="3" fill="{color}" opacity="0.3"/>""",
    "database": """<ellipse cx="60" cy="35" rx="45" ry="15" fill="url(#accent)" opacity="0.3" stroke="{color}" stroke-width="2"/>
    <path d="M15 35 V100 C15 110 60 120 60 120 C60 120 105 110 105 100 V35" fill="none" stroke="{color}" stroke-width="2"/>
    <ellipse cx="60" cy="60" rx="45" ry="12" fill="none" stroke="{color}" stroke-width="1" opacity="0.5"/>
    <ellipse cx="60" cy="85" rx="45" ry="12" fill="none" stroke="{color}" stroke-width="1" opacity="0.5"/>""",
    "chart": """<rect x="10" y="100" width="20" height="50" rx="3" fill="{color}" opacity="0.6"/>
    <rect x="40" y="70" width="20" height="80" rx="3" fill="{color}" opacity="0.7"/>
    <rect x="70" y="40" width="20" height="110" rx="3" fill="url(#accent)" opacity="0.8"/>
    <rect x="100" y="60" width="20" height="90" rx="3" fill="{color}" opacity="0.7"/>
    <path d="M15 95 L50 65 L80 35 L110 55" fill="none" stroke="{light}" stroke-width="2"/>""",
    "feed": """<circle cx="25" cy="125" r="10" fill="{color}"/>
    <path d="M25 80 C80 80 100 100 100 155" fill="none" stroke="{color}" stroke-width="6" opacity="0.7"/>
    <path d="M25 40 C110 40 140 70 140 155" fill="none" stroke="{color}" stroke-width="6" opacity="0.4"/>""",
    "mail": """<rect x="5" y="30" width="110" height="80" rx="6" fill="url(#accent)" opacity="0.2" stroke="{color}" stroke-width="2"/>
    <polyline points="5,30 60,80 115,30" fill="none" stroke="{light}" stroke-width="2"/>
    <line x1="5" y1="110" x2="40" y2="75" stroke="{color}" stroke-width="1.5" opacity="0.5"/>
    <line x1="115" y1="110" x2="80" y2="75" stroke="{color}" stroke-width="1.5" opacity="0.5"/>""",
    "phone": """<rect x="25" y="0" width="70" height="130" rx="10" fill="url(#accent)" opacity="0.2" stroke="{color}" stroke-width="2"/>
    <rect x="32" y="15" width="56" height="85" rx="3" fill="#1e293b"/>
    <circle cx="60" cy="115" r="7" fill="none" stroke="{color}" stroke-width="1.5"/>
    <text x="60" y="60" text-anchor="middle" fill="{light}" font-family="monospace" font-size="16">CALL</text>""",
    "browser": """<rect x="5" y="10" width="110" height="130" rx="8" fill="url(#accent)" opacity="0.15" stroke="{color}" stroke-width="2"/>
    <rect x="5" y="10" width="110" height="25" rx="8" fill="{color}" opacity="0.3"/>
    <circle cx="20" cy="22" r="4" fill="{light}" opacity="0.6"/>
    <circle cx="33" cy="22" r="4" fill="{light}" opacity="0.6"/>
    <circle cx="46" cy="22" r="4" fill="{light}" opacity="0.6"/>
    <rect x="15" y="50" width="90" height="8" rx="3" fill="{color}" opacity="0.3"/>
    <rect x="15" y="65" width="70" height="8" rx="3" fill="{color}" opacity="0.25"/>
    <rect x="15" y="80" width="80" height="8" rx="3" fill="{color}" opacity="0.3"/>""",
}

# Topic tag colors
TAG_COLORS = [
    ("#991b1b", "#fca5a5"),  # red
    ("#7c2d12", "#fdba74"),  # orange
    ("#312e81", "#a5b4fc"),  # indigo
    ("#064e3b", "#6ee7b7"),  # green
    ("#78350f", "#fbbf24"),  # amber
    ("#581c87", "#d8b4fe"),  # purple
    ("#164e63", "#67e8f9"),  # cyan
]


def extract_front_matter(filepath):
    """Extract YAML front matter from a markdown file."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read(3000)  # Read just enough for front matter

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def detect_topics(title, tags, excerpt, filename):
    """Detect key topics from post metadata."""
    searchable = f"{title} {' '.join(str(t) for t in (tags or []))} {excerpt or ''} {filename}".lower()
    topics = []
    seen_labels = set()

    for keyword, (color, label, icon) in TOPIC_ICONS.items():
        if keyword.lower() in searchable and label not in seen_labels:
            topics.append((keyword, color, label, icon))
            seen_labels.add(label)

    return topics[:6]  # Max 6 topics


def get_palette(topics):
    """Choose a color palette based on primary topic."""
    if not topics:
        return ACCENT_PALETTES["default"]

    first_icon = topics[0][3]
    if first_icon in ("shield", "lock", "bug", "alert"):
        return ACCENT_PALETTES["security"]
    elif first_icon == "brain":
        return ACCENT_PALETTES["ai"]
    elif first_icon in ("cloud",):
        return ACCENT_PALETTES["cloud"]
    elif first_icon == "chain":
        return ACCENT_PALETTES["blockchain"]
    elif first_icon in ("gear", "container"):
        return ACCENT_PALETTES["devops"]
    return ACCENT_PALETTES["default"]


def format_date(date_val):
    """Format date for display."""
    if hasattr(date_val, "strftime"):
        return date_val.strftime("%B %d, %Y")
    date_str = str(date_val)
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", date_str)
    if match:
        months = ["", "January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        y, m, d = match.groups()
        return f"{months[int(m)]} {int(d):02d}, {y}"
    return date_str


def split_title(title, max_chars=32):
    """Split title into two lines for SVG display."""
    if len(title) <= max_chars:
        return title, ""

    # Try splitting at common delimiters
    for delim in [": ", " - ", ", ", " & "]:
        if delim in title:
            parts = title.split(delim, 1)
            return parts[0] + (delim.strip() if delim != " - " else ""), parts[1]

    # Split at word boundary near middle
    words = title.split()
    mid = len(words) // 2
    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])
    return line1, line2


def make_network_dots(seed_str):
    """Generate unique network visualization dots based on seed."""
    h = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
    dots = []
    colors = ["#f87171", "#fb923c", "#818cf8", "#34d399", "#fbbf24"]
    for i in range(10):
        x = 30 + ((h >> (i * 3)) % 200)
        y = 30 + ((h >> (i * 2 + 1)) % 200)
        r = 3 + (i % 4)
        c = colors[i % len(colors)]
        dots.append(f'    <circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/>')

    lines = []
    for i in range(0, min(len(dots), 8), 1):
        j = (i + 1) % len(dots)
        x1 = 30 + ((h >> (i * 3)) % 200)
        y1 = 30 + ((h >> (i * 2 + 1)) % 200)
        x2 = 30 + ((h >> (j * 3)) % 200)
        y2 = 30 + ((h >> (j * 2 + 1)) % 200)
        lines.append(f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#475569" stroke-width="1"/>')

    return "\n".join(dots + lines)


def english_title_from_filename(filename_stem):
    """Extract English title from filename (SVG must be English only)."""
    # Remove date prefix: 2026-03-06-Rest_Of_Name
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', filename_stem)
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    return name


def generate_svg(post_data, filename_stem):
    """Generate a rich SVG in the reference style."""
    # Use English title from filename (Korean not allowed in SVG text)
    title = english_title_from_filename(filename_stem)
    date = post_data.get("date", "2026-01-01")
    tags = post_data.get("tags", [])
    excerpt = post_data.get("excerpt", "")
    original_title = post_data.get("title", "")

    topics = detect_topics(original_title, tags, excerpt, filename_stem)
    palette = get_palette(topics)

    # Choose primary and secondary icons
    primary_icon = topics[0][3] if topics else "shield"
    secondary_icon = topics[1][3] if len(topics) > 1 else "brain"

    # Get icon SVGs
    icon1_svg = ICON_SVGS.get(primary_icon, ICON_SVGS["shield"])
    icon2_svg = ICON_SVGS.get(secondary_icon, ICON_SVGS["brain"])

    # Light color for icon details
    accent1_light = {
        "#ef4444": "#fca5a5", "#dc2626": "#fca5a5", "#f87171": "#fecaca",
        "#6366f1": "#a5b4fc", "#818cf8": "#c7d2fe", "#a78bfa": "#ddd6fe",
        "#06b6d4": "#67e8f9", "#10b981": "#6ee7b7", "#f59e0b": "#fbbf24",
        "#326ce5": "#93c5fd", "#2496ed": "#93c5fd", "#f7931a": "#fdba74",
        "#00add8": "#67e8f9", "#dea584": "#fde68a", "#3b82f6": "#93c5fd",
        "#8b5cf6": "#c4b5fd", "#0078d4": "#93c5fd", "#4285f4": "#93c5fd",
        "#ff9900": "#fbbf24", "#607078": "#94a3b8", "#7b42bc": "#c4b5fd",
        "#e6522c": "#fca5a5",
    }.get(topics[0][1] if topics else "#6366f1", "#a5b4fc")

    icon1_rendered = icon1_svg.replace("{color}", palette["accent1"]).replace("{light}", accent1_light)
    icon2_rendered = icon2_svg.replace("{color}", palette["accent2"]).replace("{light}", "#94a3b8")

    # Title splitting
    line1, line2 = split_title(title)
    if len(line1) > 35:
        line1_size = 36
    else:
        line1_size = 42
    if len(line2) > 35:
        line2_size = 32
    else:
        line2_size = 36

    # Date formatting
    date_str = format_date(date)

    # Generate stat cards based on topics
    stat_cards = []
    stat_topics = topics[:3] if len(topics) >= 3 else topics + [("security", "#ef4444", "Security", "shield")] * (3 - len(topics))

    stat_labels = []
    for i, (kw, color, label, _) in enumerate(stat_topics[:3]):
        stat_labels.append((label, color))

    # Stats card SVG
    card_width = 200
    for i, (label, color) in enumerate(stat_labels):
        x_offset = i * 220
        stat_cards.append(f"""    <rect x="{x_offset}" y="0" width="{card_width}" height="90" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
    <text x="{x_offset + 20}" y="30" fill="{color}" font-family="Arial, sans-serif" font-size="12" font-weight="bold">{label.upper()}</text>
    <text x="{x_offset + 20}" y="65" fill="#f8fafc" font-family="Arial, sans-serif" font-size="28" font-weight="bold">{label}</text>
    <text x="{x_offset + 20}" y="80" fill="#64748b" font-family="Arial, sans-serif" font-size="13">analysis</text>""")

    # Topic tags
    tag_pills = []
    tag_x = 0
    for i, (kw, color, label, _) in enumerate(topics[:4]):
        bg_color, text_color = TAG_COLORS[i % len(TAG_COLORS)]
        pill_width = len(label) * 9 + 30
        tag_pills.append(f"""    <rect x="{tag_x}" y="0" width="{pill_width}" height="32" rx="16" fill="{bg_color}" opacity="0.7"/>
    <text x="{tag_x + pill_width // 2}" y="21" text-anchor="middle" fill="{text_color}" font-family="Arial, sans-serif" font-size="13">{label}</text>""")
        tag_x += pill_width + 15

    # Count articles if available
    article_count = len(tags) if tags else 15
    article_count = max(article_count, 10)

    # Topic summary for bottom
    topic_names = [t[2] for t in topics[:4]]
    topics_str = " | ".join(topic_names) if topic_names else "Security | AI | Cloud"

    # Network dots
    network_dots = make_network_dots(filename_stem)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" fill="none">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1200" y2="630">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{palette['accent1']}"/>
      <stop offset="100%" stop-color="{palette['accent1_dark']}"/>
    </linearGradient>
    <linearGradient id="accent2" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{palette['accent2']}"/>
      <stop offset="100%" stop-color="{palette['accent2_dark']}"/>
    </linearGradient>
  </defs>

  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bg)"/>

  <!-- Grid pattern -->
  <g opacity="0.05" stroke="#94a3b8" stroke-width="1">
    <line x1="0" y1="100" x2="1200" y2="100"/>
    <line x1="0" y1="200" x2="1200" y2="200"/>
    <line x1="0" y1="300" x2="1200" y2="300"/>
    <line x1="0" y1="400" x2="1200" y2="400"/>
    <line x1="0" y1="500" x2="1200" y2="500"/>
    <line x1="200" y1="0" x2="200" y2="630"/>
    <line x1="400" y1="0" x2="400" y2="630"/>
    <line x1="600" y1="0" x2="600" y2="630"/>
    <line x1="800" y1="0" x2="800" y2="630"/>
    <line x1="1000" y1="0" x2="1000" y2="630"/>
  </g>

  <!-- Primary icon -->
  <g transform="translate(80, 180)">
    {icon1_rendered}
  </g>

  <!-- Secondary icon -->
  <g transform="translate(80, 380)">
    {icon2_rendered}
  </g>

  <!-- Main title area -->
  <g transform="translate(260, 100)">
    <text x="0" y="0" fill="#f8fafc" font-family="Arial, sans-serif" font-size="18" font-weight="bold" letter-spacing="4">TECH SECURITY WEEKLY DIGEST</text>
    <text x="0" y="60" fill="#f8fafc" font-family="Arial, sans-serif" font-size="{line1_size}" font-weight="bold">{_escape_xml(line1)}</text>
    <text x="0" y="110" fill="#94a3b8" font-family="Arial, sans-serif" font-size="{line2_size}" font-weight="300">{_escape_xml(line2)}</text>
  </g>

  <!-- Date badge -->
  <rect x="260" y="240" width="200" height="36" rx="18" fill="url(#accent)" opacity="0.9"/>
  <text x="360" y="264" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="16" font-weight="bold">{date_str}</text>

  <!-- Stats cards -->
  <g transform="translate(260, 310)">
{chr(10).join(stat_cards)}
  </g>

  <!-- Key topics -->
  <g transform="translate(260, 440)">
{chr(10).join(tag_pills)}
  </g>

  <!-- Network visualization -->
  <g transform="translate(900, 180)" opacity="0.4">
{network_dots}
  </g>

  <!-- Bottom bar -->
  <rect x="0" y="510" width="1200" height="120" fill="#0f172a" opacity="0.8"/>
  <rect x="0" y="510" width="1200" height="2" fill="url(#accent)" opacity="0.5"/>

  <!-- Bottom text -->
  <text x="80" y="560" fill="#94a3b8" font-family="Arial, sans-serif" font-size="16">tech.2twodragon.com</text>
  <text x="80" y="590" fill="#64748b" font-family="Arial, sans-serif" font-size="13">DevSecOps Weekly Security Intelligence</text>

  <!-- Bottom right -->
  <text x="1120" y="560" text-anchor="end" fill="#64748b" font-family="Arial, sans-serif" font-size="14">{article_count} curated articles</text>
  <text x="1120" y="590" text-anchor="end" fill="#64748b" font-family="Arial, sans-serif" font-size="13">{topics_str}</text>
</svg>
"""
    return svg


def _escape_xml(text):
    """Escape XML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))


def find_svg_path(post_path):
    """Find the corresponding SVG image path for a post."""
    stem = post_path.stem
    # Check exact match first
    svg_path = IMAGES_DIR / f"{stem}.svg"
    if svg_path.exists():
        return svg_path

    # Check for image reference in front matter
    fm = extract_front_matter(post_path)
    image = fm.get("image", "")
    if image:
        img_name = Path(image).name
        svg_candidate = IMAGES_DIR / img_name
        if svg_candidate.exists():
            return svg_candidate

    return svg_path  # Return expected path even if doesn't exist


def main():
    """Main function to generate/update all digest SVGs."""
    # Find all digest posts
    digest_posts = []
    for post_file in sorted(POSTS_DIR.glob("*.md")):
        name_lower = post_file.stem.lower()
        if "digest" in name_lower or "weekly" in name_lower:
            digest_posts.append(post_file)

    print(f"Found {len(digest_posts)} digest posts")

    updated = 0
    skipped = 0

    for post_file in digest_posts:
        stem = post_file.stem

        # Skip already-good SVGs
        if stem in SKIP_FILES:
            print(f"  SKIP (already good): {stem}")
            skipped += 1
            continue

        # Find SVG path
        svg_path = find_svg_path(post_file)

        # Check if existing SVG is already in new style
        if svg_path.exists():
            try:
                with open(svg_path, "r", encoding="utf-8") as f:
                    content = f.read(200)
                    if "Key topics" in content or "key topics" in content:
                        print(f"  SKIP (new style): {stem}")
                        skipped += 1
                        continue
            except (UnicodeDecodeError, OSError):
                pass  # Not a text SVG, will overwrite

        # Read post metadata
        fm = extract_front_matter(post_file)
        if not fm:
            print(f"  SKIP (no front matter): {stem}")
            skipped += 1
            continue

        # Determine output path
        image_ref = fm.get("image", "")
        if image_ref:
            out_name = Path(image_ref).name
            out_path = IMAGES_DIR / out_name
        else:
            out_path = IMAGES_DIR / f"{stem}.svg"

        # Generate SVG
        svg_content = generate_svg(fm, stem)

        # Write SVG
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        print(f"  UPDATED: {out_path.name}")
        updated += 1

    print(f"\nDone! Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
