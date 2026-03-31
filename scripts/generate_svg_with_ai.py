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


def read_post_content(filepath: Path) -> str:
    """Read first 500 chars of post body (after front matter) for context."""
    content = filepath.read_text(encoding='utf-8')
    m = re.match(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
    if m:
        body = m.group(1).strip()
        body = re.sub(r'\{%.*?%\}', '', body)  # Remove Liquid tags
        body = re.sub(r'!\[.*?\]\(.*?\)', '', body)  # Remove images
        body = re.sub(r'```[\s\S]*?```', '', body)  # Remove code blocks
        body = re.sub(r'[#*>\-|]', '', body)  # Remove markdown
        body = ' '.join(body.split())[:500]
        return body
    return ''


def build_prompt(post: dict, filepath: Path = None) -> str:
    """Build content-aware SVG generation prompt."""
    en_title = extract_english_title(post['title'], post['filename'])
    date = format_date(post['date'])
    cat = post['categories'][0] if post['categories'] else 'security'
    excerpt = post.get('excerpt', '')

    # Read actual post content for richer context
    body_preview = ''
    if filepath and filepath.exists():
        body_preview = read_post_content(filepath)

    # Extract key English terms only
    keywords = [w for w in en_title.split() if len(w) > 2][:6]
    topic_str = ' '.join(keywords)

    return f"""SVG 1200x630 for "{topic_str}" ({date}, {cat}).

Dark bg #0a0c1a. Right side (x=700-1150): unique illustration for {topic_str} using layered SVG shapes. Left side: title "{topic_str}" in 2 lines (y=185,245 font-size 46 white), date badge "{date}", 3 tag pills at y=420, footer tech.2twodragon.com.

Make the illustration SPECIFIC to {topic_str} - not generic. All text English. Output ONLY SVG XML."""


def run_claude(prompt: str) -> str:
    """Run Claude CLI and extract SVG."""
    try:
        result = subprocess.run(
            ['claude', '-p', prompt, '--output-format', 'text', '--model', 'haiku'],
            capture_output=True, text=True, timeout=90
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

        prompt = build_prompt(post, post_path)
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
