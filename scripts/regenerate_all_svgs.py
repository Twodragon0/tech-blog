#!/usr/bin/env python3
"""Regenerate all blog post SVG images to match the reference template quality.

Reference: 2026-03-24-Tech_Security_Weekly_Digest_Malware_Data_AWS_AI.svg
- Dark gradient background with grid lines
- Decorative icon (connected circles) on right side
- Alert dots + background circles
- Left accent bar (6px gradient)
- Date badge, 2-line title (font-size 46), subtitle, accent line
- Category label, 3 keyword tag pills, bottom rule + footer
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime

POSTS_DIR = "/Users/yong/Desktop/personal/tech-blog/_posts"
IMAGES_DIR = "/Users/yong/Desktop/personal/tech-blog/assets/images"

# Month name lookup
MONTHS = {
    1: "JANUARY", 2: "FEBRUARY", 3: "MARCH", 4: "APRIL",
    5: "MAY", 6: "JUNE", 7: "JULY", 8: "AUGUST",
    9: "SEPTEMBER", 10: "OCTOBER", 11: "NOVEMBER", 12: "DECEMBER",
}

# Color themes by category
THEMES = {
    "security": {
        "primary": "#ef4444",
        "secondary": "#f59e0b",
        "bg_end": "#1a0a0a",
        "pill1_fill": "rgba(239,68,68,0.18)",
        "pill1_stroke": "rgba(239,68,68,0.4)",
        "pill1_text": "#fca5a5",
        "icon_fill": "rgba(239,68,68,0.08)",
        "icon_stroke": "rgba(239,68,68,0.3)",
        "icon_line": "rgba(239,68,68,0.25)",
        "dot_colors": ["rgba(239,68,68,0.3)", "rgba(239,68,68,0.25)", "rgba(239,68,68,0.2)"],
        "badge_fill": "rgba(239,68,68,0.2)",
        "badge_stroke": "rgba(239,68,68,0.4)",
        "label": "SECURITY",
    },
    "cloud": {
        "primary": "#3b82f6",
        "secondary": "#06b6d4",
        "bg_end": "#0a0a1a",
        "pill1_fill": "rgba(59,130,246,0.18)",
        "pill1_stroke": "rgba(59,130,246,0.4)",
        "pill1_text": "#93c5fd",
        "icon_fill": "rgba(59,130,246,0.08)",
        "icon_stroke": "rgba(59,130,246,0.3)",
        "icon_line": "rgba(59,130,246,0.25)",
        "dot_colors": ["rgba(59,130,246,0.3)", "rgba(59,130,246,0.25)", "rgba(59,130,246,0.2)"],
        "badge_fill": "rgba(59,130,246,0.2)",
        "badge_stroke": "rgba(59,130,246,0.4)",
        "label": "CLOUD",
    },
    "devsecops": {
        "primary": "#a855f7",
        "secondary": "#3b82f6",
        "bg_end": "#12061a",
        "pill1_fill": "rgba(168,85,247,0.18)",
        "pill1_stroke": "rgba(168,85,247,0.4)",
        "pill1_text": "#d8b4fe",
        "icon_fill": "rgba(168,85,247,0.08)",
        "icon_stroke": "rgba(168,85,247,0.3)",
        "icon_line": "rgba(168,85,247,0.25)",
        "dot_colors": ["rgba(168,85,247,0.3)", "rgba(168,85,247,0.25)", "rgba(168,85,247,0.2)"],
        "badge_fill": "rgba(168,85,247,0.2)",
        "badge_stroke": "rgba(168,85,247,0.4)",
        "label": "DEVSECOPS",
    },
    "devops": {
        "primary": "#22c55e",
        "secondary": "#06b6d4",
        "bg_end": "#0a1a0a",
        "pill1_fill": "rgba(34,197,94,0.18)",
        "pill1_stroke": "rgba(34,197,94,0.4)",
        "pill1_text": "#86efac",
        "icon_fill": "rgba(34,197,94,0.08)",
        "icon_stroke": "rgba(34,197,94,0.3)",
        "icon_line": "rgba(34,197,94,0.25)",
        "dot_colors": ["rgba(34,197,94,0.3)", "rgba(34,197,94,0.25)", "rgba(34,197,94,0.2)"],
        "badge_fill": "rgba(34,197,94,0.2)",
        "badge_stroke": "rgba(34,197,94,0.4)",
        "label": "DEVOPS",
    },
    "finops": {
        "primary": "#f59e0b",
        "secondary": "#ef4444",
        "bg_end": "#1a0f0a",
        "pill1_fill": "rgba(245,158,11,0.18)",
        "pill1_stroke": "rgba(245,158,11,0.4)",
        "pill1_text": "#fbbf24",
        "icon_fill": "rgba(245,158,11,0.08)",
        "icon_stroke": "rgba(245,158,11,0.3)",
        "icon_line": "rgba(245,158,11,0.25)",
        "dot_colors": ["rgba(245,158,11,0.3)", "rgba(245,158,11,0.25)", "rgba(245,158,11,0.2)"],
        "badge_fill": "rgba(245,158,11,0.2)",
        "badge_stroke": "rgba(245,158,11,0.4)",
        "label": "FINOPS",
    },
    "kubernetes": {
        "primary": "#3b82f6",
        "secondary": "#06b6d4",
        "bg_end": "#0a0a1a",
        "pill1_fill": "rgba(59,130,246,0.18)",
        "pill1_stroke": "rgba(59,130,246,0.4)",
        "pill1_text": "#93c5fd",
        "icon_fill": "rgba(59,130,246,0.08)",
        "icon_stroke": "rgba(59,130,246,0.3)",
        "icon_line": "rgba(59,130,246,0.25)",
        "dot_colors": ["rgba(59,130,246,0.3)", "rgba(59,130,246,0.25)", "rgba(59,130,246,0.2)"],
        "badge_fill": "rgba(59,130,246,0.2)",
        "badge_stroke": "rgba(59,130,246,0.4)",
        "label": "KUBERNETES",
    },
    "incident": {
        "primary": "#ef4444",
        "secondary": "#f59e0b",
        "bg_end": "#1a0a0a",
        "pill1_fill": "rgba(239,68,68,0.18)",
        "pill1_stroke": "rgba(239,68,68,0.4)",
        "pill1_text": "#fca5a5",
        "icon_fill": "rgba(239,68,68,0.08)",
        "icon_stroke": "rgba(239,68,68,0.3)",
        "icon_line": "rgba(239,68,68,0.25)",
        "dot_colors": ["rgba(239,68,68,0.3)", "rgba(239,68,68,0.25)", "rgba(239,68,68,0.2)"],
        "badge_fill": "rgba(239,68,68,0.2)",
        "badge_stroke": "rgba(239,68,68,0.4)",
        "label": "INCIDENT",
    },
}

# Generic words to remove from titles
GENERIC_WORDS = {
    "complete", "guide", "practical", "analysis", "overview", "understanding",
    "introduction", "comprehensive", "master", "setup", "basic", "advanced",
    "tutorial", "definitive", "essential", "ultimate", "deep", "dive",
    "from", "and", "the", "for", "with", "about", "into", "through",
    "based", "oriented", "driven", "focused", "using", "via",
}


def sanitize_text(text):
    """Make text safe for SVG XML."""
    text = text.replace("&amp;", "and").replace("&", "and")
    text = text.replace('"', "").replace("'", "").replace("<", "").replace(">", "")
    text = text.replace("&lt;", "").replace("&gt;", "").replace("&quot;", "")
    # Remove HTML entities
    text = re.sub(r"&\w+;", "", text)
    # Remove ampamp, amplsquo etc artifacts
    text = re.sub(r"amp[a-z]+", "", text)
    return text.strip()


def extract_title_from_filename(filename):
    """Extract English keywords from filename for title lines."""
    # Remove date prefix and extension
    name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", filename)
    name = name.replace(".md", "").replace(".svg", "")

    # Replace separators
    name = name.replace("_", " ").replace("-", " ")

    # Clean up encoded chars
    name = re.sub(r"amp[a-z]*", "", name)

    # Split into words
    words = name.split()

    # Filter generic words but keep tech terms
    filtered = []
    for w in words:
        wl = w.lower()
        if wl in GENERIC_WORDS:
            continue
        if len(w) <= 1:
            continue
        filtered.append(w)

    if not filtered:
        filtered = words[:6]

    return filtered


def make_title_lines(words, max_chars=30):
    """Split words into 2 title lines, each max ~max_chars."""
    if not words:
        return ["Tech Blog", "Post"]

    # Join all words
    full = " ".join(words)

    # If short enough for one line, split at midpoint
    if len(full) <= max_chars:
        return [full, ""]

    # Try to split into 2 balanced lines
    line1_words = []
    line2_words = []
    line1_len = 0

    # Target: first line slightly shorter
    target = len(full) // 2

    for w in words:
        if line1_len + len(w) + 1 <= target + 5 and not line2_words:
            line1_words.append(w)
            line1_len += len(w) + 1
        else:
            line2_words.append(w)

    line1 = " ".join(line1_words) if line1_words else words[0]
    line2 = " ".join(line2_words) if line2_words else ""

    # Truncate if too long
    if len(line1) > 40:
        line1 = line1[:37] + "..."
    if len(line2) > 40:
        line2 = line2[:37] + "..."

    return [line1, line2]


def get_tag_labels(tags, categories, filename_words):
    """Get 3 keyword labels for tag pills."""
    candidates = []

    # Prefer tags
    for t in tags:
        t_clean = t.replace("-", " ").strip()
        if t_clean and len(t_clean) <= 20:
            candidates.append(t_clean)

    # Then categories
    for c in categories:
        c_clean = c.strip().capitalize()
        if c_clean and c_clean not in candidates and len(c_clean) <= 20:
            candidates.append(c_clean)

    # Then filename words
    for w in filename_words:
        if w not in candidates and len(w) <= 20 and w.lower() not in GENERIC_WORDS:
            candidates.append(w)

    # Ensure 3
    while len(candidates) < 3:
        candidates.append("Tech")

    return candidates[:3]


def parse_post(filepath):
    """Parse a post's front matter to extract metadata."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read(5000)

    # Extract front matter
    fm_match = re.match(r"---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None

    fm = fm_match.group(1)

    # Parse image path
    img_match = re.search(r"image:\s*(.+)", fm)
    image_path = img_match.group(1).strip().strip("\"'") if img_match else None

    # Parse categories
    categories = []
    # Multi-line format
    cat_block = re.search(r"categories:\s*\n((?:\s*-\s*.+\n)+)", fm)
    if cat_block:
        categories = re.findall(r"-\s*(.+)", cat_block.group(1))
    else:
        # Inline format
        cat_inline = re.search(r"categories:\s*\[([^\]]*)\]", fm)
        if cat_inline:
            categories = [c.strip().strip("\"'") for c in cat_inline.group(1).split(",")]
        else:
            cat_single = re.search(r"category:\s*\[?([^\]\n]+)\]?", fm)
            if cat_single:
                categories = [c.strip().strip("\"'") for c in cat_single.group(1).split(",")]

    categories = [c.strip().lower() for c in categories if c.strip()]

    # Parse tags
    tags = []
    tag_block = re.search(r"tags:\s*\n((?:\s*-\s*.+\n)+)", fm)
    if tag_block:
        tags = re.findall(r"-\s*(.+)", tag_block.group(1))
    else:
        tag_inline = re.search(r"tags:\s*\[([^\]]*)\]", fm)
        if tag_inline:
            tags = [t.strip().strip("\"'") for t in tag_inline.group(1).split(",")]

    tags = [t.strip() for t in tags if t.strip()]

    return {
        "image_path": image_path,
        "categories": categories,
        "tags": tags,
    }


def check_svg_quality(svg_path):
    """Check if SVG already has 2 title lines at font-size 46 AND 3 tag pills."""
    try:
        tree = ET.parse(svg_path)
        root = tree.getroot()
        ns = "http://www.w3.org/2000/svg"

        texts = root.findall(f".//{{{ns}}}text")
        title_46 = [t for t in texts if t.get("font-size") == "46"]

        rects = root.findall(f".//{{{ns}}}rect")
        pills = [r for r in rects if r.get("rx") == "18" and r.get("height") == "36"]

        return len(title_46) >= 2 and len(pills) >= 3
    except Exception:
        return False


def get_theme(categories):
    """Get color theme based on categories."""
    for cat in categories:
        cat_lower = cat.lower()
        if cat_lower in THEMES:
            return THEMES[cat_lower]
    # Default to security
    return THEMES["security"]


def estimate_text_width(text, font_size=14):
    """Rough estimate of text width in pixels."""
    # Approximate: each char ~8px at size 14
    char_width = font_size * 0.55
    return len(text) * char_width + 24  # 24px padding


def generate_svg(date_str, title_line1, title_line2, subtitle, category_label,
                 tag1, tag2, tag3, theme):
    """Generate SVG content matching the reference template."""

    # Calculate pill widths
    pill1_w = max(estimate_text_width(tag1), 80)
    pill2_w = max(estimate_text_width(tag2), 80)
    pill3_w = max(estimate_text_width(tag3), 80)

    pill1_x = 80
    pill2_x = pill1_x + pill1_w + 14
    pill3_x = pill2_x + pill2_w + 14

    pill1_text_x = pill1_x + pill1_w / 2
    pill2_text_x = pill2_x + pill2_w / 2
    pill3_text_x = pill3_x + pill3_w / 2

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{sanitize_text(title_line1 + " " + title_line2)}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0c1a"/>
      <stop offset="100%" stop-color="{theme["bg_end"]}"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{theme["primary"]}"/>
      <stop offset="100%" stop-color="{theme["secondary"]}"/>
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
  <!-- Pipeline icon -->
  <circle cx="920" cy="200" r="18" fill="{theme["icon_fill"]}" stroke="{theme["icon_stroke"]}" stroke-width="1.5"/>
  <circle cx="990" cy="200" r="18" fill="{theme["icon_fill"]}" stroke="{theme["icon_stroke"]}" stroke-width="1.5"/>
  <circle cx="955" cy="270" r="18" fill="{theme["icon_fill"]}" stroke="{theme["icon_stroke"]}" stroke-width="1.5"/>
  <line x1="938" y1="200" x2="972" y2="200" stroke="{theme["icon_line"]}" stroke-width="1.5"/>
  <line x1="930" y1="215" x2="945" y2="255" stroke="{theme["icon_line"]}" stroke-width="1.5"/>
  <line x1="980" y1="215" x2="965" y2="255" stroke="{theme["icon_line"]}" stroke-width="1.5"/>
  <!-- Alert dots -->
  <circle cx="870" cy="400" r="6" fill="{theme["dot_colors"][0]}"/>
  <circle cx="900" cy="420" r="4" fill="{theme["dot_colors"][1]}"/>
  <circle cx="860" cy="440" r="5" fill="{theme["dot_colors"][2]}"/>
  <!-- Background circles -->
  <circle cx="1050" cy="450" r="200" fill="rgba(255,255,255,0.02)"/>
  <circle cx="1050" cy="450" r="140" fill="rgba(255,255,255,0.02)"/>
  <!-- Left accent bar -->
  <rect x="0" y="0" width="6" height="630" fill="url(#accent)"/>
  <!-- Date badge -->
  <rect x="80" y="60" width="200" height="32" rx="4" fill="{theme["badge_fill"]}" stroke="{theme["badge_stroke"]}" stroke-width="1"/>
  <text x="180" y="81" font-family="system-ui,sans-serif" font-size="14" fill="rgba(255,255,255,0.8)" text-anchor="middle" letter-spacing="1">{date_str}</text>
  <!-- Main title -->
  <text x="80" y="185" font-family="system-ui,sans-serif" font-size="46" font-weight="700" fill="white" letter-spacing="-1">{sanitize_text(title_line1)}</text>
  <text x="80" y="245" font-family="system-ui,sans-serif" font-size="46" font-weight="700" fill="white" letter-spacing="-1">{sanitize_text(title_line2)}</text>
  <!-- Subtitle -->
  <text x="80" y="300" font-family="system-ui,sans-serif" font-size="19" fill="rgba(255,255,255,0.6)">{sanitize_text(subtitle)}</text>
  <!-- Accent line -->
  <rect x="80" y="325" width="420" height="3" rx="1" fill="url(#accent)"/>
  <!-- Category label -->
  <text x="80" y="370" font-family="system-ui,sans-serif" font-size="14" fill="rgba(255,255,255,0.4)" letter-spacing="2">{category_label}</text>
  <!-- Keyword tags -->
  <rect x="{pill1_x}" y="420" width="{pill1_w:.0f}" height="36" rx="18" fill="{theme["pill1_fill"]}" stroke="{theme["pill1_stroke"]}" stroke-width="1"/>
  <text x="{pill1_text_x:.0f}" y="443" font-family="system-ui,sans-serif" font-size="14" fill="{theme["pill1_text"]}" text-anchor="middle" font-weight="600">{sanitize_text(tag1)}</text>
  <rect x="{pill2_x:.0f}" y="420" width="{pill2_w:.0f}" height="36" rx="18" fill="rgba(245,158,11,0.18)" stroke="rgba(245,158,11,0.4)" stroke-width="1"/>
  <text x="{pill2_text_x:.0f}" y="443" font-family="system-ui,sans-serif" font-size="14" fill="#fbbf24" text-anchor="middle" font-weight="600">{sanitize_text(tag2)}</text>
  <rect x="{pill3_x:.0f}" y="420" width="{pill3_w:.0f}" height="36" rx="18" fill="rgba(59,130,246,0.18)" stroke="rgba(59,130,246,0.4)" stroke-width="1"/>
  <text x="{pill3_text_x:.0f}" y="443" font-family="system-ui,sans-serif" font-size="14" fill="#93c5fd" text-anchor="middle" font-weight="600">{sanitize_text(tag3)}</text>
  <!-- Bottom rule -->
  <rect x="80" y="520" width="1040" height="1" fill="rgba(255,255,255,0.08)"/>
  <text x="80" y="545" font-family="system-ui,sans-serif" font-size="13" fill="rgba(255,255,255,0.3)" letter-spacing="1">tech.2twodragon.com</text>
  <text x="1120" y="545" font-family="system-ui,sans-serif" font-size="13" fill="rgba(255,255,255,0.3)" text-anchor="end">{category_label.capitalize()}</text>
</svg>'''

    return svg


def main():
    # Collect all posts and their image references
    posts = {}
    for fname in sorted(os.listdir(POSTS_DIR)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(POSTS_DIR, fname)
        meta = parse_post(fpath)
        if meta and meta["image_path"]:
            img_basename = os.path.basename(meta["image_path"])
            posts[img_basename] = {
                "post_file": fname,
                **meta,
            }

    print(f"Found {len(posts)} posts with image references")

    # Track results
    skipped_good = 0
    skipped_no_post = 0
    regenerated = 0
    errors = 0

    # Get all SVGs
    all_svgs = sorted(f for f in os.listdir(IMAGES_DIR) if f.endswith(".svg"))
    print(f"Found {len(all_svgs)} SVG files total")

    # Process only SVGs referenced by posts
    for svg_name in all_svgs:
        # Skip non-post SVGs
        if svg_name.startswith(("section-", "og-", "news-fallback")):
            skipped_no_post += 1
            continue

        # Skip SVGs not referenced by any post
        if svg_name not in posts:
            skipped_no_post += 1
            continue

        svg_path = os.path.join(IMAGES_DIR, svg_name)

        # Check if already good quality
        if check_svg_quality(svg_path):
            skipped_good += 1
            continue

        # Get post metadata
        post = posts[svg_name]
        post_file = post["post_file"]
        categories = post["categories"]
        tags = post["tags"]

        # Extract date from filename
        date_match = re.match(r"(\d{4})-(\d{2})-(\d{2})", post_file)
        if not date_match:
            print(f"  SKIP (no date): {svg_name}")
            skipped_no_post += 1
            continue

        year = int(date_match.group(1))
        month = int(date_match.group(2))
        day = int(date_match.group(3))
        date_str = f"{MONTHS[month]} {day:02d}, {year}"

        # Get theme
        theme = get_theme(categories)

        # Extract title words from filename
        title_words = extract_title_from_filename(post_file)
        title_line1, title_line2 = make_title_lines(title_words)

        # Build subtitle from categories
        cats_display = [c.capitalize() for c in categories[:3]]
        subtitle = " | ".join(cats_display) if cats_display else "Tech Blog"

        # Category label
        category_label = theme["label"]

        # Tag pills
        tag_labels = get_tag_labels(tags, categories, title_words)

        # Generate SVG
        svg_content = generate_svg(
            date_str, title_line1, title_line2, subtitle, category_label,
            tag_labels[0], tag_labels[1], tag_labels[2], theme,
        )

        # Validate XML
        try:
            ET.fromstring(svg_content.encode("utf-8"))
        except ET.ParseError as e:
            print(f"  ERROR (XML invalid): {svg_name}: {e}")
            errors += 1
            continue

        # Write file
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)

        regenerated += 1

    print()
    print("=" * 60)
    print(f"Results:")
    print(f"  Skipped (already good quality): {skipped_good}")
    print(f"  Skipped (not a post image):     {skipped_no_post}")
    print(f"  Regenerated:                    {regenerated}")
    print(f"  Errors:                         {errors}")
    print(f"  Total SVGs processed:           {skipped_good + regenerated + errors}")
    print("=" * 60)


if __name__ == "__main__":
    main()
