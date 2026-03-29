#!/usr/bin/env python3
"""Batch regenerate SVG hero images using reference template style.

Reads post metadata and generates consistent, professional SVG images
with unique color schemes per category.
"""

import json
import os
import re
import hashlib
import xml.etree.ElementTree as ET
from io import StringIO
from datetime import datetime

# Color schemes by category
COLOR_SCHEMES = {
    'security': {
        'bg_end': '#1a0a0a',
        'accent_start': '#ef4444', 'accent_end': '#f59e0b',
        'tag_colors': [
            ('#ef4444', '#fca5a5'),
            ('#f59e0b', '#fbbf24'),
            ('#3b82f6', '#93c5fd'),
        ]
    },
    'devsecops': {
        'bg_end': '#0a1a0a',
        'accent_start': '#22c55e', 'accent_end': '#06b6d4',
        'tag_colors': [
            ('#22c55e', '#86efac'),
            ('#06b6d4', '#67e8f9'),
            ('#3b82f6', '#93c5fd'),
        ]
    },
    'cloud': {
        'bg_end': '#0a0a1a',
        'accent_start': '#3b82f6', 'accent_end': '#06b6d4',
        'tag_colors': [
            ('#3b82f6', '#93c5fd'),
            ('#f59e0b', '#fbbf24'),
            ('#06b6d4', '#67e8f9'),
        ]
    },
    'kubernetes': {
        'bg_end': '#0a0c1a',
        'accent_start': '#6366f1', 'accent_end': '#8b5cf6',
        'tag_colors': [
            ('#6366f1', '#a5b4fc'),
            ('#8b5cf6', '#c4b5fd'),
            ('#3b82f6', '#93c5fd'),
        ]
    },
    'devops': {
        'bg_end': '#0a1a12',
        'accent_start': '#14b8a6', 'accent_end': '#22c55e',
        'tag_colors': [
            ('#14b8a6', '#5eead4'),
            ('#22c55e', '#86efac'),
            ('#f59e0b', '#fbbf24'),
        ]
    },
    'finops': {
        'bg_end': '#0a0c12',
        'accent_start': '#eab308', 'accent_end': '#f59e0b',
        'tag_colors': [
            ('#eab308', '#fde047'),
            ('#22c55e', '#86efac'),
            ('#3b82f6', '#93c5fd'),
        ]
    },
    'incident': {
        'bg_end': '#1a0a10',
        'accent_start': '#ef4444', 'accent_end': '#ec4899',
        'tag_colors': [
            ('#ef4444', '#fca5a5'),
            ('#ec4899', '#f9a8d4'),
            ('#f59e0b', '#fbbf24'),
        ]
    },
}

# Decorative icons by index
ICONS = {
    0: '''  <!-- Shield icon -->
  <path d="M950,140 L1030,170 L1030,250 Q1030,310 950,340 Q870,310 870,250 L870,170 Z" fill="rgba({r},{g},{b},0.06)" stroke="rgba({r},{g},{b},0.25)" stroke-width="1.5"/>
  <path d="M950,160 L1015,185 L1015,250 Q1015,295 950,318 Q885,295 885,250 L885,185 Z" fill="rgba({r},{g},{b},0.04)"/>
  <rect x="935" y="220" width="30" height="24" rx="4" fill="none" stroke="rgba({r},{g},{b},0.4)" stroke-width="1.5"/>
  <path d="M940,220 L940,210 Q940,198 950,198 Q960,198 960,210 L960,220" fill="none" stroke="rgba({r},{g},{b},0.35)" stroke-width="1.5"/>''',
    1: '''  <!-- Cloud icon -->
  <ellipse cx="970" cy="220" rx="80" ry="50" fill="rgba({r},{g},{b},0.05)" stroke="rgba({r},{g},{b},0.2)" stroke-width="1.5"/>
  <ellipse cx="930" cy="240" rx="50" ry="35" fill="rgba({r},{g},{b},0.04)" stroke="rgba({r},{g},{b},0.15)" stroke-width="1"/>
  <ellipse cx="1010" cy="240" rx="45" ry="30" fill="rgba({r},{g},{b},0.04)" stroke="rgba({r},{g},{b},0.15)" stroke-width="1"/>
  <rect x="920" y="270" width="100" height="60" rx="6" fill="rgba({r},{g},{b},0.04)" stroke="rgba({r},{g},{b},0.2)" stroke-width="1"/>''',
    2: '''  <!-- Pipeline icon -->
  <circle cx="920" cy="200" r="18" fill="rgba({r},{g},{b},0.08)" stroke="rgba({r},{g},{b},0.3)" stroke-width="1.5"/>
  <circle cx="990" cy="200" r="18" fill="rgba({r},{g},{b},0.08)" stroke="rgba({r},{g},{b},0.3)" stroke-width="1.5"/>
  <circle cx="955" cy="270" r="18" fill="rgba({r},{g},{b},0.08)" stroke="rgba({r},{g},{b},0.3)" stroke-width="1.5"/>
  <line x1="938" y1="200" x2="972" y2="200" stroke="rgba({r},{g},{b},0.25)" stroke-width="1.5"/>
  <line x1="930" y1="215" x2="945" y2="255" stroke="rgba({r},{g},{b},0.25)" stroke-width="1.5"/>
  <line x1="980" y1="215" x2="965" y2="255" stroke="rgba({r},{g},{b},0.25)" stroke-width="1.5"/>''',
    3: '''  <!-- Lock icon -->
  <rect x="925" y="210" width="60" height="50" rx="8" fill="rgba({r},{g},{b},0.06)" stroke="rgba({r},{g},{b},0.25)" stroke-width="1.5"/>
  <path d="M935,210 L935,190 Q935,170 955,170 Q975,170 975,190 L975,210" fill="none" stroke="rgba({r},{g},{b},0.3)" stroke-width="2"/>
  <circle cx="955" cy="235" r="6" fill="rgba({r},{g},{b},0.3)"/>
  <line x1="955" y1="241" x2="955" y2="250" stroke="rgba({r},{g},{b},0.3)" stroke-width="2"/>''',
    4: '''  <!-- Chart icon -->
  <line x1="900" y1="310" x2="900" y2="180" stroke="rgba({r},{g},{b},0.2)" stroke-width="1.5"/>
  <line x1="900" y1="310" x2="1030" y2="310" stroke="rgba({r},{g},{b},0.2)" stroke-width="1.5"/>
  <rect x="920" y="260" width="20" height="50" rx="2" fill="rgba({r},{g},{b},0.15)"/>
  <rect x="950" y="220" width="20" height="90" rx="2" fill="rgba({r},{g},{b},0.2)"/>
  <rect x="980" y="240" width="20" height="70" rx="2" fill="rgba({r},{g},{b},0.15)"/>''',
}


def title_from_svg_path(svg_path: str) -> str:
    """Extract clean English title from SVG filename."""
    basename = os.path.basename(svg_path)
    # Remove date prefix and extension
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', basename)
    name = name.replace('.svg', '')
    # Replace underscores and clean up
    name = name.replace('_', ' ')
    # Remove HTML entity artifacts
    name = re.sub(r'amp[a-z]*;?', '', name)
    name = re.sub(r'ampamp', 'and', name)
    name = re.sub(r'amplsquo|amprsquo|ampquot', '', name)
    # Clean up dashes between words
    name = re.sub(r'\s*-\s*', ' - ', name)
    # Remove consecutive punctuation
    name = re.sub(r'[,\s]{2,}', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip(' -,')
    return name


def korean_to_english_title(title: str, svg_path: str = '') -> tuple:
    """Convert Korean title to clean English SVG title (2 lines max)."""
    title = title.strip("'\"")

    # Remove HTML entities first
    clean = re.sub(r'&[a-z]+;', ' ', title)
    clean = re.sub(r'amp[a-z]*;?', '', clean)

    # Remove Korean chars
    clean = re.sub(r'[가-힣]+', ' ', clean)
    # Clean up special chars
    clean = re.sub(r'[!?·•—""''<>]+', ' ', clean)
    clean = re.sub(r'\s*[,]\s*', ', ', clean)
    clean = re.sub(r'\s*[-:]\s*', ' - ', clean)
    # Remove batch pattern
    clean = re.sub(r'\s*\d+\s*Batch\s*-?\s*', ' ', clean, flags=re.IGNORECASE)
    # Clean up
    clean = re.sub(r'\s+', ' ', clean).strip()
    clean = clean.strip(' -:,')
    # Remove leading/trailing commas and dashes
    clean = re.sub(r'^[\s,\-:]+|[\s,\-:]+$', '', clean)

    # Count meaningful alpha chars
    alpha = sum(1 for c in clean if c.isalpha())

    # If title is too sparse, fall back to SVG filename
    if alpha < 8 and svg_path:
        clean = title_from_svg_path(svg_path)

    # Final cleanup
    clean = re.sub(r'\s+', ' ', clean).strip(' -:,')
    clean = re.sub(r'^[\s,\-:]+|[\s,\-:]+$', '', clean)

    if not clean or len(clean) < 3:
        clean = 'Tech Blog Post'

    # Split into 2 lines (max ~35 chars per line for font-size 46)
    if len(clean) <= 35:
        return (clean, '')

    words = clean.split()
    mid = len(clean) // 2
    best_pos = 0
    best_diff = len(clean)
    pos = 0
    for i, word in enumerate(words):
        pos += len(word) + 1
        diff = abs(pos - mid)
        if diff < best_diff:
            best_diff = diff
            best_pos = i + 1

    line1 = ' '.join(words[:best_pos])
    line2 = ' '.join(words[best_pos:])

    if len(line1) > 42:
        line1 = line1[:39] + '...'
    if len(line2) > 42:
        line2 = line2[:39] + '...'

    return (line1, line2)


def format_date(date_str: str) -> str:
    """Format date string to 'MONTH DD, YYYY'."""
    try:
        dt = datetime.strptime(date_str[:10], '%Y-%m-%d')
        return dt.strftime('%B %d, %Y').upper().replace(' 0', ' ')
    except:
        return date_str[:10]


def get_color_scheme(categories: list) -> dict:
    for cat in categories:
        cat_lower = cat.lower()
        if cat_lower in COLOR_SCHEMES:
            return COLOR_SCHEMES[cat_lower]
    return COLOR_SCHEMES['security']


def generate_svg(entry: dict) -> str:
    """Generate SVG content for a blog post."""
    title = entry.get('title', '')
    date = entry.get('date', '')
    categories = entry.get('categories', [])
    tags = entry.get('tags', [])[:3]

    line1, line2 = korean_to_english_title(title, entry.get('svg', ''))
    date_str = format_date(date)
    scheme = get_color_scheme(categories)

    icon_idx = int(hashlib.md5(title.encode()).hexdigest(), 16) % len(ICONS)

    accent = scheme['accent_start']
    r = int(accent[1:3], 16)
    g = int(accent[3:5], 16)
    b = int(accent[5:7], 16)

    icon_svg = ICONS[icon_idx].format(r=r, g=g, b=b)

    cat_str = ' | '.join(c.title() for c in categories[:3]) if categories else 'Tech Blog'
    if tags:
        cat_str += ' | ' + tags[0].replace('-', ' ')

    cat_label = categories[0].upper() if categories else 'TECH'

    # Tag pills
    tag_pills = ''
    x_offset = 80
    for i, tag in enumerate(tags[:3]):
        if i >= len(scheme['tag_colors']):
            break
        bg_color, text_color = scheme['tag_colors'][i]
        tag_text = tag.replace('-', ' ')
        tag_width = max(len(tag_text) * 9 + 30, 70)
        tag_cx = x_offset + tag_width // 2

        br = int(bg_color[1:3], 16)
        bg = int(bg_color[3:5], 16)
        bb = int(bg_color[5:7], 16)

        tag_pills += f'  <rect x="{x_offset}" y="420" width="{tag_width}" height="36" rx="18" fill="rgba({br},{bg},{bb},0.18)" stroke="rgba({br},{bg},{bb},0.4)" stroke-width="1"/>\n'
        tag_pills += f'  <text x="{tag_cx}" y="443" font-family="system-ui,sans-serif" font-size="14" fill="{text_color}" text-anchor="middle" font-weight="600">{tag_text}</text>\n'
        x_offset += tag_width + 14

    full_title = f"{line1} {line2}".strip()

    title_line2 = ''
    if line2:
        title_line2 = f'  <text x="80" y="245" font-family="system-ui,sans-serif" font-size="46" font-weight="700" fill="white" letter-spacing="-1">{line2}</text>'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630">
  <title>{full_title}</title>
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0c1a"/>
      <stop offset="100%" stop-color="{scheme['bg_end']}"/>
    </linearGradient>
    <linearGradient id="accent" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{scheme['accent_start']}"/>
      <stop offset="100%" stop-color="{scheme['accent_end']}"/>
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
{icon_svg}
  <!-- Alert dots -->
  <circle cx="870" cy="400" r="6" fill="rgba({r},{g},{b},0.3)"/>
  <circle cx="900" cy="420" r="4" fill="rgba({r},{g},{b},0.25)"/>
  <circle cx="860" cy="440" r="5" fill="rgba({r},{g},{b},0.2)"/>
  <!-- Background circles -->
  <circle cx="1050" cy="450" r="200" fill="rgba(255,255,255,0.02)"/>
  <circle cx="1050" cy="450" r="140" fill="rgba(255,255,255,0.02)"/>
  <!-- Left accent bar -->
  <rect x="0" y="0" width="6" height="630" fill="url(#accent)"/>
  <!-- Date badge -->
  <rect x="80" y="60" width="200" height="32" rx="4" fill="rgba({r},{g},{b},0.2)" stroke="rgba({r},{g},{b},0.4)" stroke-width="1"/>
  <text x="180" y="81" font-family="system-ui,sans-serif" font-size="14" fill="rgba(255,255,255,0.8)" text-anchor="middle" letter-spacing="1">{date_str}</text>
  <!-- Main title -->
  <text x="80" y="185" font-family="system-ui,sans-serif" font-size="46" font-weight="700" fill="white" letter-spacing="-1">{line1}</text>
{title_line2}
  <!-- Subtitle -->
  <text x="80" y="300" font-family="system-ui,sans-serif" font-size="19" fill="rgba(255,255,255,0.6)">{cat_str}</text>
  <!-- Accent line -->
  <rect x="80" y="325" width="420" height="3" rx="1" fill="url(#accent)"/>
  <!-- Category label -->
  <text x="80" y="370" font-family="system-ui,sans-serif" font-size="14" fill="rgba(255,255,255,0.4)" letter-spacing="2">{cat_label}</text>
  <!-- Keyword tags -->
{tag_pills}  <!-- Bottom rule -->
  <rect x="80" y="520" width="1040" height="1" fill="rgba(255,255,255,0.08)"/>
  <text x="80" y="545" font-family="system-ui,sans-serif" font-size="13" fill="rgba(255,255,255,0.3)" letter-spacing="1">tech.2twodragon.com</text>
  <text x="1120" y="545" font-family="system-ui,sans-serif" font-size="13" fill="rgba(255,255,255,0.3)" text-anchor="end">{cat_label.title()}</text>
</svg>'''

    return svg


def validate_and_fix_svg(svg_content: str) -> str:
    """Validate SVG XML and fix common issues."""
    try:
        ET.fromstring(svg_content)
        return svg_content  # Already valid
    except ET.ParseError:
        # Fix bare & (not part of existing entities)
        fixed = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', svg_content)
        try:
            ET.fromstring(fixed)
            return fixed
        except ET.ParseError as e:
            print(f"  WARNING: SVG XML still invalid after fix attempt: {e}")
            return fixed  # Return best-effort fix


def main():
    with open('/tmp/svg_regen_list.json') as f:
        entries = json.load(f)

    count = 0
    for entry in entries:
        svg_path = entry['svg']
        svg_content = generate_svg(entry)
        svg_content = validate_and_fix_svg(svg_content)

        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)

        count += 1
        if count % 20 == 0:
            print(f"  Generated {count}/{len(entries)}...")

    print(f"\nDone! Regenerated {count} SVG images.")


if __name__ == '__main__':
    main()
