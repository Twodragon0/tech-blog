#!/usr/bin/env python3
"""Generate high-quality SVG images for blog posts using AI CLIs (claude/codex/gemini)."""

import argparse
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


POSTS_DIR = Path("_posts")
IMAGES_DIR = Path("assets/images")


def extract_english_title(title: str, filename: str) -> str:
    """Convert Korean title to English keywords from filename."""
    # If title has Korean, use filename keywords instead
    if re.search(r'[\uac00-\ud7af]', title):
        name = filename.replace('.md', '')
        name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', name)
        words = re.sub(r'[_-]+', ' ', name).split()
        # Remove generic words
        skip = {'and', 'the', 'for', 'from', 'to', 'in', 'of', 'a', 'an', 'is',
                'complete', 'guide', 'practical', 'analysis', 'overview', 'ampamp',
                'amplsquo', 'amprsquo', 'ampquot'}
        words = [w for w in words if w.lower() not in skip and len(w) > 1]
        return ' '.join(words[:8])
    return title


def format_date(date_str: str) -> str:
    """Convert 2026-03-22 to MARCH 22, 2026."""
    months = ['', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
              'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']
    parts = date_str.split('-')
    if len(parts) == 3:
        return f"{months[int(parts[1])]} {int(parts[2])}, {parts[0]}"
    return date_str


def parse_post(filepath: Path) -> dict:
    """Extract metadata from post front matter."""
    content = filepath.read_text(encoding='utf-8')
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return {}

    fm = fm_match.group(1)
    result = {'filename': filepath.name}

    # Title
    m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', fm, re.MULTILINE)
    result['title'] = m.group(1) if m else ''

    # Date from filename
    dm = re.match(r'(\d{4}-\d{2}-\d{2})', filepath.name)
    result['date'] = dm.group(1) if dm else ''

    # Categories
    cats = re.findall(r'^\s*-\s+(\w+)', fm[fm.find('categories'):fm.find('categories')+200], re.MULTILINE) if 'categories' in fm else []
    if not cats:
        m = re.search(r'^category:\s*(\w+)', fm, re.MULTILINE)
        cats = [m.group(1)] if m else ['security']
    result['categories'] = cats

    # Image path
    m = re.search(r'^image:\s*(.*?)$', fm, re.MULTILINE)
    result['image'] = m.group(1).strip() if m else ''

    # Excerpt
    m = re.search(r'^excerpt:\s*["\']?(.*?)["\']?\s*$', fm, re.MULTILINE)
    result['excerpt'] = m.group(1)[:150] if m else ''

    return result


def build_prompt(post: dict) -> str:
    """Build SVG generation prompt for Claude CLI."""
    en_title = extract_english_title(post['title'], post['filename'])
    date = format_date(post['date'])
    cat = post['categories'][0] if post['categories'] else 'security'

    # Split title into 2 lines
    words = en_title.split()
    mid = len(words) // 2
    line1 = ' '.join(words[:mid]) if mid > 0 else en_title
    line2 = ' '.join(words[mid:]) if mid > 0 else ''

    return f"""Generate an SVG image (viewBox="0 0 1200 630" width="1200" height="630") for a tech blog post.

Topic: {en_title}
Date: {date}
Category: {cat}

Structure (follow exactly):
1. Dark gradient background: <rect fill with linearGradient from #0a0c1a to #1a0a0a>
2. Grid: 4 horizontal lines at y=105,210,315,420 + 4 vertical at x=240,480,720,960 (stroke rgba white 0.03-0.04)
3. RIGHT SIDE ILLUSTRATION (x=880-1140, y=130-320): Create a UNIQUE decorative icon using SVG shapes (circles, paths, rects, polygons) that visually represents "{en_title}". Use semi-transparent fills (opacity 0.06-0.15) and strokes (opacity 0.2-0.4). This is the most important part - make it distinctive and recognizable.
4. Alert dots: 3 small circles at (870,400), (900,420), (860,440)
5. Background circles: 2 at (1050,450) r=200 and r=140, very subtle
6. Left accent bar: rect x=0 y=0 width=6 height=630, gradient fill
7. Date badge: rect at (80,60) width=200 height=32 rx=4 + text "{date}"
8. Title line 1: <text x="80" y="185" font-size="46" font-weight="700" fill="white">{line1}</text>
9. Title line 2: <text x="80" y="245" font-size="46" font-weight="700" fill="white">{line2}</text>
10. Subtitle: <text x="80" y="300" font-size="19"> with category info
11. Accent line: rect at y=325 width=420 height=3
12. Category label: text at y=370, font-size 14, uppercase
13. Three tag pills at y=420: rx=18 height=36, different colors (red/amber/blue)
14. Footer: text "tech.2twodragon.com" at (80,545), category at (1120,545)

ALL text must be English only. Output ONLY the raw SVG XML, no markdown, no explanation."""


def run_claude(prompt: str) -> str:
    """Run Claude CLI and extract SVG."""
    try:
        result = subprocess.run(
            ['claude', '-p', prompt, '--output-format', 'text', '--model', 'sonnet'],
            capture_output=True, text=True, timeout=180
        )
        output = result.stdout
        # Clean terminal escape sequences
        output = re.sub(r'\x1b[^a-zA-Z]*[a-zA-Z]', '', output)
        output = re.sub(r'\x1b\][^\x07\x1b]*[\x07\x1b]?', '', output)
        # Extract SVG
        m = re.search(r'(<svg[\s\S]*?</svg>)', output)
        return m.group(1) if m else ''
    except Exception as e:
        print(f"    Claude error: {e}", file=sys.stderr)
        return ''


def run_codex(prompt: str) -> str:
    """Run Codex CLI and extract SVG."""
    try:
        result = subprocess.run(
            ['codex', '-q', '--full-auto', prompt],
            capture_output=True, text=True, timeout=90
        )
        m = re.search(r'(<svg[\s\S]*?</svg>)', result.stdout)
        return m.group(1) if m else ''
    except Exception as e:
        print(f"    Codex error: {e}", file=sys.stderr)
        return ''


def validate_svg(svg_content: str) -> bool:
    """Validate SVG content."""
    if not svg_content or '<svg' not in svg_content:
        return False
    try:
        ET.fromstring(svg_content)
    except ET.ParseError:
        # Try fixing bare &
        fixed = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', svg_content)
        try:
            ET.fromstring(fixed)
            return True
        except:
            return False
    # Check for Korean
    if re.search(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]', svg_content):
        return False
    return True


def fix_svg(svg_content: str) -> str:
    """Fix common SVG issues."""
    svg_content = re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#)', '&amp;', svg_content)
    # Remove Korean characters from text elements
    svg_content = re.sub(r'[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f]+', '', svg_content)
    return svg_content


def main():
    parser = argparse.ArgumentParser(description='Generate SVG images using AI CLIs')
    parser.add_argument('--engine', default='claude', choices=['claude', 'codex', 'gemini'])
    parser.add_argument('--recent', type=int, default=0, help='Process N most recent posts')
    parser.add_argument('--force', action='store_true', help='Regenerate even if exists')
    parser.add_argument('post_file', nargs='?', help='Single post file')
    args = parser.parse_args()

    # Get post files
    if args.post_file:
        posts = [Path(args.post_file)]
    else:
        posts = sorted(POSTS_DIR.glob('*.md'), reverse=True)
        if args.recent > 0:
            posts = posts[:args.recent]

    print(f"{'='*50}")
    print(f"  AI SVG Generator | Engine: {args.engine}")
    print(f"  Posts: {len(posts)} | Force: {args.force}")
    print(f"{'='*50}\n")

    success = failed = skipped = 0
    engines = {'claude': run_claude, 'codex': run_codex}
    generate = engines.get(args.engine, run_claude)

    for post_path in posts:
        post = parse_post(post_path)
        if not post.get('image'):
            print(f"SKIP: {post_path.name} (no image field)")
            skipped += 1
            continue

        svg_file = IMAGES_DIR / os.path.basename(post['image'])
        if not args.force and svg_file.exists():
            skipped += 1
            continue

        en_title = extract_english_title(post['title'], post['filename'])
        print(f"Processing: {post_path.name}")
        print(f"  Title: {en_title}")

        prompt = build_prompt(post)
        svg_content = generate(prompt)

        if svg_content:
            svg_content = fix_svg(svg_content)
            if validate_svg(svg_content):
                svg_file.write_text(svg_content, encoding='utf-8')
                print(f"  ✅ Generated: {svg_file}")
                success += 1
                continue

        # Fallback to claude if primary failed
        if args.engine != 'claude':
            print(f"  Fallback to Claude...")
            svg_content = run_claude(prompt)
            if svg_content:
                svg_content = fix_svg(svg_content)
                if validate_svg(svg_content):
                    svg_file.write_text(svg_content, encoding='utf-8')
                    print(f"  ✅ Generated (fallback): {svg_file}")
                    success += 1
                    continue

        print(f"  ❌ Failed")
        failed += 1

    print(f"\n{'='*50}")
    print(f"  Results: {success} ✅ | {skipped} skipped | {failed} ❌")
    print(f"{'='*50}")


if __name__ == '__main__':
    main()
