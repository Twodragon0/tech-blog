#!/usr/bin/env python3
"""
upgrade_svg_banners.py - Upgrade all post header SVG banners to the latest style.

Usage:
    python3 scripts/upgrade_svg_banners.py [options]

Options:
    --dry-run       Only list what would be changed, no files written
    --force         Overwrite existing files (default: skip already-upgraded)
    --skip-recent   Skip SVG files modified in last 24 hours
    --post FILE     Generate only for a specific post file (path to .md)
    --help          Show this help message
"""

import os
import sys
import re
import html
import argparse
import textwrap
from pathlib import Path
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
POSTS_DIR = REPO_ROOT / "_posts"
IMAGES_DIR = REPO_ROOT / "assets" / "images"

# ---------------------------------------------------------------------------
# Color themes per category
# ---------------------------------------------------------------------------
THEMES = {
    "security": {
        "bg": ("#0a0c1a", "#1a0a0a"),
        "accent": ("#ef4444", "#f59e0b"),
        "badge_bg": "rgba(239,68,68,0.2)",
        "badge_border": "rgba(239,68,68,0.4)",
        "tag_colors": ["#fca5a5", "#fbbf24", "#93c5fd"],
        "tag_bgs": [
            "rgba(239,68,68,0.18)",
            "rgba(245,158,11,0.15)",
            "rgba(59,130,246,0.15)",
        ],
        "tag_borders": [
            "rgba(239,68,68,0.4)",
            "rgba(245,158,11,0.35)",
            "rgba(59,130,246,0.35)",
        ],
    },
    "cloud": {
        "bg": ("#0a0c1a", "#0a1525"),
        "accent": ("#06b6d4", "#3b82f6"),
        "badge_bg": "rgba(6,182,212,0.2)",
        "badge_border": "rgba(6,182,212,0.4)",
        "tag_colors": ["#67e8f9", "#93c5fd", "#a78bfa"],
        "tag_bgs": [
            "rgba(6,182,212,0.18)",
            "rgba(59,130,246,0.15)",
            "rgba(139,92,246,0.15)",
        ],
        "tag_borders": [
            "rgba(6,182,212,0.4)",
            "rgba(59,130,246,0.35)",
            "rgba(139,92,246,0.35)",
        ],
    },
    "devsecops": {
        "bg": ("#0a0c1a", "#0a1a15"),
        "accent": ("#22c55e", "#06b6d4"),
        "badge_bg": "rgba(34,197,94,0.2)",
        "badge_border": "rgba(34,197,94,0.4)",
        "tag_colors": ["#86efac", "#67e8f9", "#fbbf24"],
        "tag_bgs": [
            "rgba(34,197,94,0.18)",
            "rgba(6,182,212,0.15)",
            "rgba(245,158,11,0.15)",
        ],
        "tag_borders": [
            "rgba(34,197,94,0.4)",
            "rgba(6,182,212,0.35)",
            "rgba(245,158,11,0.35)",
        ],
    },
    "devops": {
        "bg": ("#0a0c1a", "#0a150a"),
        "accent": ("#22c55e", "#a3e635"),
        "badge_bg": "rgba(34,197,94,0.2)",
        "badge_border": "rgba(34,197,94,0.4)",
        "tag_colors": ["#86efac", "#d9f99d", "#fbbf24"],
        "tag_bgs": [
            "rgba(34,197,94,0.18)",
            "rgba(163,230,53,0.15)",
            "rgba(245,158,11,0.15)",
        ],
        "tag_borders": [
            "rgba(34,197,94,0.4)",
            "rgba(163,230,53,0.35)",
            "rgba(245,158,11,0.35)",
        ],
    },
    "kubernetes": {
        "bg": ("#0a0c1a", "#0f0a25"),
        "accent": ("#8b5cf6", "#06b6d4"),
        "badge_bg": "rgba(139,92,246,0.2)",
        "badge_border": "rgba(139,92,246,0.4)",
        "tag_colors": ["#a78bfa", "#67e8f9", "#86efac"],
        "tag_bgs": [
            "rgba(139,92,246,0.18)",
            "rgba(6,182,212,0.15)",
            "rgba(34,197,94,0.15)",
        ],
        "tag_borders": [
            "rgba(139,92,246,0.4)",
            "rgba(6,182,212,0.35)",
            "rgba(34,197,94,0.35)",
        ],
    },
    "finops": {
        "bg": ("#0a0c1a", "#1a1a0a"),
        "accent": ("#f59e0b", "#22c55e"),
        "badge_bg": "rgba(245,158,11,0.2)",
        "badge_border": "rgba(245,158,11,0.4)",
        "tag_colors": ["#fbbf24", "#86efac", "#93c5fd"],
        "tag_bgs": [
            "rgba(245,158,11,0.18)",
            "rgba(34,197,94,0.15)",
            "rgba(59,130,246,0.15)",
        ],
        "tag_borders": [
            "rgba(245,158,11,0.4)",
            "rgba(34,197,94,0.35)",
            "rgba(59,130,246,0.35)",
        ],
    },
    "default": {
        "bg": ("#0a0c1a", "#130820"),
        "accent": ("#8b5cf6", "#06b6d4"),
        "badge_bg": "rgba(139,92,246,0.2)",
        "badge_border": "rgba(139,92,246,0.4)",
        "tag_colors": ["#a78bfa", "#67e8f9", "#fbbf24"],
        "tag_bgs": [
            "rgba(139,92,246,0.18)",
            "rgba(6,182,212,0.15)",
            "rgba(245,158,11,0.15)",
        ],
        "tag_borders": [
            "rgba(139,92,246,0.4)",
            "rgba(6,182,212,0.35)",
            "rgba(245,158,11,0.35)",
        ],
    },
}

# ---------------------------------------------------------------------------
# Category-based illustrations (right-side decorative, NO text nodes)
# ---------------------------------------------------------------------------
ILLUSTRATIONS = {
    "security": """\
  <!-- Shield icon -->
  <path d="M950,140 L1030,170 L1030,250 Q1030,310 950,340 Q870,310 870,250 L870,170 Z" fill="rgba(239,68,68,0.06)" stroke="rgba(239,68,68,0.25)" stroke-width="1.5"/>
  <path d="M950,160 L1015,185 L1015,250 Q1015,295 950,318 Q885,295 885,250 L885,185 Z" fill="rgba(239,68,68,0.04)"/>
  <!-- Lock -->
  <rect x="935" y="220" width="30" height="24" rx="4" fill="none" stroke="rgba(239,68,68,0.4)" stroke-width="1.5"/>
  <path d="M940,220 L940,210 Q940,198 950,198 Q960,198 960,210 L960,220" fill="none" stroke="rgba(239,68,68,0.35)" stroke-width="1.5"/>
  <!-- Alert dots -->
  <circle cx="870" cy="400" r="6" fill="rgba(239,68,68,0.3)"/>
  <circle cx="900" cy="420" r="4" fill="rgba(245,158,11,0.25)"/>
  <circle cx="860" cy="440" r="5" fill="rgba(239,68,68,0.2)"/>""",
    "cloud": """\
  <!-- Cloud shape -->
  <ellipse cx="970" cy="200" rx="110" ry="50" fill="rgba(6,182,212,0.07)" stroke="rgba(6,182,212,0.2)" stroke-width="1.5"/>
  <ellipse cx="935" cy="218" rx="75" ry="38" fill="rgba(6,182,212,0.05)"/>
  <ellipse cx="1010" cy="222" rx="65" ry="33" fill="rgba(6,182,212,0.05)"/>
  <!-- Server rack -->
  <rect x="920" y="320" width="80" height="100" rx="6" fill="rgba(59,130,246,0.06)" stroke="rgba(59,130,246,0.2)" stroke-width="1"/>
  <line x1="920" y1="350" x2="1000" y2="350" stroke="rgba(59,130,246,0.15)" stroke-width="1"/>
  <line x1="920" y1="380" x2="1000" y2="380" stroke="rgba(59,130,246,0.15)" stroke-width="1"/>
  <circle cx="985" cy="335" r="4" fill="rgba(34,197,94,0.4)"/>
  <circle cx="985" cy="365" r="4" fill="rgba(34,197,94,0.3)"/>
  <circle cx="985" cy="395" r="4" fill="rgba(245,158,11,0.3)"/>""",
    "devsecops": """\
  <!-- Pipeline flow -->
  <circle cx="880" cy="200" r="20" fill="none" stroke="rgba(34,197,94,0.4)" stroke-width="2"/>
  <line x1="900" y1="200" x2="940" y2="200" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
  <circle cx="960" cy="200" r="20" fill="none" stroke="rgba(6,182,212,0.4)" stroke-width="2"/>
  <line x1="980" y1="200" x2="1020" y2="200" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>
  <circle cx="1040" cy="200" r="20" fill="none" stroke="rgba(139,92,246,0.4)" stroke-width="2"/>
  <!-- Infinity loop -->
  <path d="M900,350 Q960,290 1020,350 Q960,410 900,350" fill="none" stroke="rgba(34,197,94,0.25)" stroke-width="2"/>
  <path d="M940,350 Q1000,290 1060,350 Q1000,410 940,350" fill="none" stroke="rgba(6,182,212,0.25)" stroke-width="2"/>""",
    "devops": """\
  <!-- Container boxes -->
  <rect x="880" y="170" width="60" height="50" rx="6" fill="rgba(34,197,94,0.06)" stroke="rgba(34,197,94,0.3)" stroke-width="1.5"/>
  <rect x="960" y="170" width="60" height="50" rx="6" fill="rgba(34,197,94,0.06)" stroke="rgba(34,197,94,0.3)" stroke-width="1.5"/>
  <rect x="920" y="240" width="60" height="50" rx="6" fill="rgba(163,230,53,0.06)" stroke="rgba(163,230,53,0.25)" stroke-width="1.5"/>
  <!-- Arrows -->
  <line x1="910" y1="220" x2="940" y2="240" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
  <line x1="990" y1="220" x2="960" y2="240" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
  <!-- Gear -->
  <circle cx="950" cy="370" r="25" fill="none" stroke="rgba(34,197,94,0.3)" stroke-width="2"/>
  <circle cx="950" cy="370" r="10" fill="none" stroke="rgba(34,197,94,0.2)" stroke-width="1.5"/>""",
    "kubernetes": """\
  <!-- K8s hexagon -->
  <polygon points="950,150 990,172 990,218 950,240 910,218 910,172" fill="rgba(139,92,246,0.06)" stroke="rgba(139,92,246,0.35)" stroke-width="1.5"/>
  <circle cx="950" cy="195" r="18" fill="none" stroke="rgba(139,92,246,0.3)" stroke-width="1"/>
  <!-- Pod boxes -->
  <rect x="880" y="310" width="45" height="35" rx="5" fill="rgba(6,182,212,0.06)" stroke="rgba(6,182,212,0.3)" stroke-width="1.5"/>
  <rect x="940" y="310" width="45" height="35" rx="5" fill="rgba(6,182,212,0.06)" stroke="rgba(6,182,212,0.3)" stroke-width="1.5"/>
  <rect x="1000" y="310" width="45" height="35" rx="5" fill="rgba(34,197,94,0.06)" stroke="rgba(34,197,94,0.25)" stroke-width="1.5"/>
  <line x1="925" y1="327" x2="940" y2="327" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
  <line x1="985" y1="327" x2="1000" y2="327" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>""",
    "finops": """\
  <!-- Cost graph bars -->
  <rect x="880" y="260" width="30" height="80" rx="4" fill="rgba(245,158,11,0.12)" stroke="rgba(245,158,11,0.3)" stroke-width="1.5"/>
  <rect x="920" y="220" width="30" height="120" rx="4" fill="rgba(245,158,11,0.16)" stroke="rgba(245,158,11,0.4)" stroke-width="1.5"/>
  <rect x="960" y="240" width="30" height="100" rx="4" fill="rgba(245,158,11,0.12)" stroke="rgba(245,158,11,0.3)" stroke-width="1.5"/>
  <rect x="1000" y="180" width="30" height="160" rx="4" fill="rgba(34,197,94,0.12)" stroke="rgba(34,197,94,0.3)" stroke-width="1.5"/>
  <!-- Trend line -->
  <polyline points="895,270 935,230 975,250 1015,190" fill="none" stroke="rgba(34,197,94,0.5)" stroke-width="2"/>
  <circle cx="1015" cy="190" r="5" fill="rgba(34,197,94,0.5)"/>""",
    "default": """\
  <!-- Abstract nodes -->
  <circle cx="920" cy="200" r="18" fill="none" stroke="rgba(139,92,246,0.4)" stroke-width="2"/>
  <circle cx="990" cy="240" r="14" fill="none" stroke="rgba(6,182,212,0.35)" stroke-width="1.5"/>
  <circle cx="950" cy="310" r="16" fill="none" stroke="rgba(139,92,246,0.3)" stroke-width="1.5"/>
  <line x1="920" y1="218" x2="990" y2="226" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
  <line x1="990" y1="254" x2="950" y2="294" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
  <line x1="950" y1="294" x2="920" y2="218" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
  <!-- Abstract shape -->
  <rect x="900" y="370" width="100" height="60" rx="8" fill="rgba(139,92,246,0.05)" stroke="rgba(139,92,246,0.2)" stroke-width="1"/>""",
}

# ---------------------------------------------------------------------------
# Category label mapping
# ---------------------------------------------------------------------------
CATEGORY_LABELS = {
    "security": "SECURITY WEEKLY DIGEST",
    "cloud": "CLOUD SECURITY DIGEST",
    "devops": "DEVOPS DIGEST",
    "devsecops": "DEVSECOPS DIGEST",
    "kubernetes": "KUBERNETES DIGEST",
    "finops": "FINOPS DIGEST",
    "incident": "INCIDENT ANALYSIS",
    "blockchain": "BLOCKCHAIN DIGEST",
}

# Tags to skip (generic/date-like)
SKIP_TAGS = {
    "2024", "2025", "2026", "2027",
    "weekly-digest", "security-weekly", "weekly",
    "digest", "tech", "daily", "monthly",
}

_KOREAN_RE = re.compile(r'[\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F]')

# Month names for date badge
MONTHS = [
    "", "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
    "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER",
]


# ---------------------------------------------------------------------------
# YAML front matter parser (minimal, no external deps)
# ---------------------------------------------------------------------------
def parse_front_matter(text: str) -> dict:
    """Extract front matter from a Jekyll post. Returns a dict."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = i
            break
    if end is None:
        return {}
    fm_lines = lines[1:end]
    fm = {}
    current_key = None
    current_list = None
    for line in fm_lines:
        # List item
        if line.startswith("- "):
            if current_list is not None:
                current_list.append(line[2:].strip().strip("'\""))
            continue
        # Inline list: key: [a, b, c]
        m = re.match(r'^(\w[\w-]*):\s*\[(.+)\]\s*$', line)
        if m:
            key = m.group(1)
            values = [v.strip().strip("'\"") for v in m.group(2).split(",")]
            fm[key] = values
            current_key = None
            current_list = None
            continue
        # Key: value
        m = re.match(r'^(\w[\w-]*):\s*(.*)', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            if val == "" or val == "|" or val == ">":
                # Possibly a block or list follows
                current_key = key
                current_list = []
                fm[key] = current_list
            else:
                fm[key] = val.strip("'\"")
                current_key = key
                current_list = None
            continue
        # Continuation of list
        stripped = line.strip()
        if stripped.startswith("- ") and current_list is not None:
            current_list.append(stripped[2:].strip().strip("'\""))
    return fm


def read_post_meta(md_path: Path) -> dict | None:
    """Read post file and return a metadata dict, or None on error."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except OSError as e:
        print(f"  [WARN] Cannot read {md_path.name}: {e}")
        return None
    fm = parse_front_matter(text)
    if not fm:
        return None

    # Normalise categories/tags to lists
    cats = fm.get("categories", fm.get("category", []))
    if isinstance(cats, str):
        cats = [cats]

    tags_raw = fm.get("tags", [])
    if isinstance(tags_raw, str):
        tags_raw = [tags_raw]

    image_path = fm.get("image", "")
    title = fm.get("title", "")
    date_str = fm.get("date", "")

    return {
        "title": title,
        "date": date_str,
        "categories": [c.lower() for c in cats],
        "tags": tags_raw,
        "image": image_path,
    }


# ---------------------------------------------------------------------------
# Category → theme resolution
# ---------------------------------------------------------------------------
def resolve_theme(categories: list[str]) -> dict:
    # Higher priority = more specific/dominant category
    priority = ["kubernetes", "finops", "security", "cloud", "devsecops", "devops"]
    for p in priority:
        if p in categories:
            return THEMES[p]
    return THEMES["default"]


def resolve_illustration(categories: list[str]) -> str:
    priority = ["kubernetes", "finops", "security", "cloud", "devsecops", "devops"]
    for p in priority:
        if p in categories:
            return ILLUSTRATIONS[p]
    return ILLUSTRATIONS["default"]


def resolve_category_label(categories: list[str]) -> str:
    priority = ["kubernetes", "finops", "incident", "blockchain", "security", "cloud", "devsecops", "devops"]
    for p in priority:
        if p in categories:
            return CATEGORY_LABELS.get(p, "TECH DIGEST")
    return "TECH DIGEST"


# ---------------------------------------------------------------------------
# Tag selection (up to 3, filter generics)
# ---------------------------------------------------------------------------
def select_tags(tags: list[str]) -> list[str]:
    selected = []
    for t in tags:
        if t.lower() in SKIP_TAGS:
            continue
        if _KOREAN_RE.search(t):
            continue  # skip Korean-language tags
        selected.append(t)
        if len(selected) == 3:
            break
    return selected


# ---------------------------------------------------------------------------
# Title → two English lines
# ---------------------------------------------------------------------------
def derive_svg_title(title: str, tags: list[str], md_path: Path) -> tuple[str, str, str]:
    """
    Returns (svg_title_attr, line1, line2) all in English.

    Strategy:
    1. If the title is predominantly ASCII (English), use it directly.
    2. Otherwise, derive English from the filename stem (which is always English).
    """

    def has_korean(s: str) -> bool:
        return bool(re.search(r'[\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F]', s))

    if title and not has_korean(title):
        english_title = title
    else:
        # Derive from filename: replace _ and - with spaces, strip date prefix
        stem = md_path.stem  # e.g. "2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day"
        # Remove YYYY-MM-DD- prefix
        stem = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem)
        english_title = stem.replace("_", " ").replace("-", " ")

    # Sanitise: remove HTML entities and special punctuation
    english_title = re.sub(r'&[a-z]+;', ' ', english_title)
    english_title = re.sub(r'["""''`]', '', english_title)
    english_title = english_title.strip()

    # Build a short title for the <title> element using first 80 chars
    svg_title_attr = english_title[:80]

    # Split into two lines (~30 chars each for readability)
    words = english_title.split()
    if not words:
        return svg_title_attr, "Tech Digest", ""

    line1 = ""
    line2 = ""
    for i, word in enumerate(words):
        candidate = (line1 + " " + word).strip() if line1 else word
        if len(candidate) <= 30:
            line1 = candidate
        else:
            line2 = " ".join(words[i:])
            break

    # Truncate line2 if it's too long
    if len(line2) > 32:
        line2 = line2[:29].rsplit(" ", 1)[0] + "..."

    return svg_title_attr, line1, line2


# ---------------------------------------------------------------------------
# Date badge text: "2026-03-28 10:00:00 +0900" → "MARCH 28, 2026"
# ---------------------------------------------------------------------------
def format_date_badge(date_str: str) -> str:
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', date_str)
    if not m:
        return date_str.upper()[:20]
    year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    month_name = MONTHS[month] if 1 <= month <= 12 else str(month)
    return f"{month_name} {day}, {year}"


# ---------------------------------------------------------------------------
# Subtitle: top 3 tags joined with " | "
# ---------------------------------------------------------------------------
def build_subtitle(tags: list[str], selected: list[str]) -> str:
    parts = [t.replace("-", " ").replace("_", " ") for t in selected]
    return " | ".join(parts) if parts else "Security & Technology"


# ---------------------------------------------------------------------------
# Tag pill SVG fragments
# ---------------------------------------------------------------------------
def build_tags_svg(selected: list[str], theme: dict) -> str:
    if not selected:
        return ""
    lines = []
    # Widths are estimated: ~10px per char + 32px padding
    x = 80
    y_rect = 420
    for i, tag in enumerate(selected):
        label = tag.replace("-", " ").replace("_", " ")
        # truncate
        if len(label) > 14:
            label = label[:13] + "."
        # estimated pill width
        width = max(80, len(label) * 9 + 36)
        cx = x + width // 2
        cy = y_rect + 18  # vertical centre of 36-tall pill
        color = theme["tag_colors"][i] if i < len(theme["tag_colors"]) else "#ffffff"
        bg = theme["tag_bgs"][i] if i < len(theme["tag_bgs"]) else "rgba(255,255,255,0.1)"
        border = theme["tag_borders"][i] if i < len(theme["tag_borders"]) else "rgba(255,255,255,0.3)"
        # Escape label for XML
        label_escaped = html.escape(label)
        lines.append(
            f'  <rect x="{x}" y="{y_rect}" width="{width}" height="36" rx="18"'
            f' fill="{bg}" stroke="{border}" stroke-width="1"/>'
        )
        lines.append(
            f'  <text x="{cx}" y="{cy + 5}" font-family="system-ui,sans-serif"'
            f' font-size="14" fill="{color}" text-anchor="middle"'
            f' font-weight="600">{label_escaped}</text>'
        )
        x += width + 14
        if x > 900:
            break
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SVG generator
# ---------------------------------------------------------------------------
def generate_svg(meta: dict, md_path: Path) -> str:
    categories = meta["categories"]
    tags = meta["tags"]
    theme = resolve_theme(categories)
    illustration = resolve_illustration(categories)
    category_label = resolve_category_label(categories)
    selected_tags = select_tags(tags)
    date_badge = format_date_badge(meta["date"])
    svg_title_attr, line1, line2 = derive_svg_title(meta["title"], tags, md_path)
    subtitle = build_subtitle(tags, selected_tags)
    tags_svg = build_tags_svg(selected_tags, theme)

    # Escape text for XML
    def esc(s: str) -> str:
        return html.escape(s)

    bg1, bg2 = theme["bg"]
    acc1, acc2 = theme["accent"]

    svg = f"""\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{esc(svg_title_attr)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{bg1}"/>
      <stop offset="100%" stop-color="{bg2}"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{acc1}"/>
      <stop offset="100%" stop-color="{acc2}"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <!-- Grid lines -->
  <line x1="0" y1="105" x2="1200" y2="105" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
  <line x1="0" y1="210" x2="1200" y2="210" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
  <line x1="0" y1="315" x2="1200" y2="315" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
  <line x1="0" y1="420" x2="1200" y2="420" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>
  <line x1="240" y1="0" x2="240" y2="630" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
  <line x1="480" y1="0" x2="480" y2="630" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
  <line x1="720" y1="0" x2="720" y2="630" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
  <line x1="960" y1="0" x2="960" y2="630" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
{illustration}
  <!-- Background circles -->
  <circle cx="1050" cy="450" r="200" fill="rgba(255,255,255,0.02)"/>
  <circle cx="1050" cy="450" r="140" fill="rgba(255,255,255,0.02)"/>
  <!-- Left accent bar -->
  <rect x="0" y="0" width="6" height="630" fill="url(#accent)"/>
  <!-- Date badge -->
  <rect x="80" y="60" width="200" height="32" rx="4" fill="{theme['badge_bg']}" stroke="{theme['badge_border']}" stroke-width="1"/>
  <text x="180" y="81" font-family="system-ui,sans-serif" font-size="14" fill="rgba(255,255,255,0.8)" text-anchor="middle" letter-spacing="1">{esc(date_badge)}</text>
  <!-- Main title -->
  <text x="80" y="185" font-family="system-ui,sans-serif" font-size="46" font-weight="700" fill="white" letter-spacing="-1">{esc(line1)}</text>
  <text x="80" y="245" font-family="system-ui,sans-serif" font-size="46" font-weight="700" fill="white" letter-spacing="-1">{esc(line2)}</text>
  <!-- Subtitle -->
  <text x="80" y="300" font-family="system-ui,sans-serif" font-size="19" fill="rgba(255,255,255,0.6)">{esc(subtitle)}</text>
  <!-- Accent line -->
  <rect x="80" y="325" width="420" height="3" rx="1" fill="url(#accent)"/>
  <!-- Category label -->
  <text x="80" y="370" font-family="system-ui,sans-serif" font-size="14" fill="rgba(255,255,255,0.4)" letter-spacing="2">{esc(category_label)}</text>
  <!-- Keyword tags (3 max) -->
{tags_svg}
  <!-- Bottom rule -->
  <rect x="80" y="520" width="1040" height="1" fill="rgba(255,255,255,0.08)"/>
  <text x="80" y="545" font-family="system-ui,sans-serif" font-size="13" fill="rgba(255,255,255,0.3)" letter-spacing="1">tech.2twodragon.com</text>
  <text x="1120" y="545" font-family="system-ui,sans-serif" font-size="13" fill="rgba(255,255,255,0.3)" text-anchor="end">DevSecOps</text>
</svg>
"""
    return svg


# ---------------------------------------------------------------------------
# Detect sub-image SVGs (section-*, news-fallback, etc.)
# ---------------------------------------------------------------------------
def build_post_header_svg_set() -> set[str]:
    """Collect the set of SVG basenames that are referenced as post headers."""
    referenced = set()
    for md_path in sorted(POSTS_DIR.glob("*.md")):
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = parse_front_matter(text)
        image_val = fm.get("image", "")
        if image_val and image_val.endswith(".svg"):
            basename = Path(image_val).name
            referenced.add(basename)
    return referenced


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------
def process_posts(args) -> None:
    # Gather the set of SVG filenames used as post headers
    header_svgs = build_post_header_svg_set()
    print(f"Found {len(header_svgs)} unique post-header SVG references.\n")

    now = datetime.now()
    cutoff = now - timedelta(hours=24)

    # Determine which posts to process
    if args.post:
        md_paths = [Path(args.post).resolve()]
    else:
        md_paths = sorted(POSTS_DIR.glob("*.md"))

    upgraded = 0
    skipped = 0
    errors = 0
    would_upgrade = 0

    for md_path in md_paths:
        meta = read_post_meta(md_path)
        if meta is None:
            skipped += 1
            continue

        image_path = meta.get("image", "")
        if not image_path:
            skipped += 1
            continue

        if not image_path.endswith(".svg"):
            skipped += 1
            continue

        svg_basename = Path(image_path).name

        # Skip if not a post-header SVG
        if svg_basename not in header_svgs:
            skipped += 1
            continue

        svg_dest = IMAGES_DIR / svg_basename

        # --skip-recent: skip if the SVG was modified in the last 24h
        if args.skip_recent and svg_dest.exists():
            mtime = datetime.fromtimestamp(svg_dest.stat().st_mtime)
            if mtime > cutoff:
                print(f"  [SKIP-RECENT] {svg_basename}")
                skipped += 1
                continue

        # --force not set: skip if file already exists
        if not args.force and svg_dest.exists() and not args.dry_run:
            skipped += 1
            continue

        # Generate SVG content
        try:
            svg_content = generate_svg(meta, md_path)
        except Exception as e:
            print(f"  [ERROR] Generating SVG for {md_path.name}: {e}")
            errors += 1
            continue

        if args.dry_run:
            would_upgrade += 1
            print(f"  [DRY-RUN] Would write: {svg_basename}")
            print(f"           Post: {md_path.name}")
            print(f"           Categories: {meta['categories']}")
            print(f"           Tags: {meta['tags'][:5]}")
            print()
        else:
            try:
                svg_dest.write_text(svg_content, encoding="utf-8")
                upgraded += 1
                print(f"  [OK] {svg_basename}")
            except OSError as e:
                print(f"  [ERROR] Writing {svg_basename}: {e}")
                errors += 1

    print()
    if args.dry_run:
        print(f"Dry-run complete: {would_upgrade} would be upgraded, {skipped} skipped.")
    else:
        print(f"Done: {upgraded} upgraded, {skipped} skipped, {errors} errors.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Upgrade post header SVG banners to the latest style.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python3 scripts/upgrade_svg_banners.py --dry-run
              python3 scripts/upgrade_svg_banners.py --force
              python3 scripts/upgrade_svg_banners.py --post _posts/2026-03-28-Tech_Security_Weekly_Digest_AI_Cloud_Zero_Day.md
              python3 scripts/upgrade_svg_banners.py --force --skip-recent
        """),
    )
    parser.add_argument("--dry-run", action="store_true", help="List changes without writing files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing SVG files")
    parser.add_argument("--skip-recent", action="store_true", help="Skip SVGs modified in last 24 hours")
    parser.add_argument("--post", metavar="FILE", help="Process only a specific post .md file")
    args = parser.parse_args()

    print("SVG Banner Upgrade Script")
    print("=========================")
    print(f"Repo root : {REPO_ROOT}")
    print(f"Posts dir : {POSTS_DIR}")
    print(f"Images dir: {IMAGES_DIR}")
    print(f"Mode      : {'DRY-RUN' if args.dry_run else 'WRITE'}")
    print(f"Force     : {args.force}")
    print(f"Skip recent: {args.skip_recent}")
    if args.post:
        print(f"Single post: {args.post}")
    print()

    process_posts(args)


if __name__ == "__main__":
    main()
