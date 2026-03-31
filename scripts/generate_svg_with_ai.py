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

    keywords = [w for w in en_title.split() if len(w) > 2][:6]
    topic_str = ' '.join(keywords)

    # Build visual element descriptions based on keywords
    visuals = []
    kw_lower = ' '.join(keywords).lower()
    if any(w in kw_lower for w in ['ransomware', 'malware', 'threat']):
        visuals.append('A padlock with chains (ransomware/malware)')
    if any(w in kw_lower for w in ['ai', 'llm', 'agent', 'gpt', 'claude']):
        visuals.append('A brain silhouette with circuit/neural lines (AI/LLM)')
    if any(w in kw_lower for w in ['kubernetes', 'k8s', 'docker', 'container']):
        visuals.append('Hexagonal pods connected by lines (Kubernetes)')
    if any(w in kw_lower for w in ['cloud', 'aws', 'gcp', 'azure']):
        visuals.append('Cloud shape with data flow arrows (cloud infrastructure)')
    if any(w in kw_lower for w in ['supply chain', 'supply', 'sbom']):
        visuals.append('A broken chain link (supply chain attack)')
    if any(w in kw_lower for w in ['cve', 'vulnerability', 'patch', 'zero-day', 'zero day']):
        visuals.append('A shield with a crack/warning symbol (vulnerability)')
    if any(w in kw_lower for w in ['bitcoin', 'blockchain', 'crypto']):
        visuals.append('Chain links and coin symbols (blockchain)')
    if any(w in kw_lower for w in ['finops', 'cost', 'billing']):
        visuals.append('Dollar sign in dashboard gauges (FinOps)')
    if any(w in kw_lower for w in ['devops', 'ci/cd', 'pipeline', 'devsecops']):
        visuals.append('Pipeline arrows with gear icons (DevOps/CI-CD)')
    if any(w in kw_lower for w in ['zero trust', 'ztna', 'network']):
        visuals.append('Network nodes with dashed trust boundaries')
    if any(w in kw_lower for w in ['security', 'isms', 'compliance']):
        visuals.append('A large shield with checkmark (security/compliance)')
    if any(w in kw_lower for w in ['data', 'breach', 'leak']):
        visuals.append('Database cylinder with warning icons (data breach)')
    if any(w in kw_lower for w in ['botnet', 'ddos']):
        visuals.append('Multiple connected bot nodes attacking a server')
    if not visuals:
        visuals.append('A shield with lock and circuit patterns (tech security)')

    visual_desc = '\n- '.join(visuals[:5])

    # Split title for 2 lines
    words_list = topic_str.split()
    mid = len(words_list) // 2 or 1
    line1 = ' '.join(words_list[:mid])
    line2 = ' '.join(words_list[mid:])

    return f"""Write an SVG file to {IMAGES_DIR}/{os.path.splitext(post['filename'])[0]}.svg (1200x630) for "{topic_str}".

Modern glassmorphism design inspired by Figma/Dribbble 2026 trends:
- Dark navy bg #0f172a with subtle dot grid pattern and ambient glow orbs
- RIGHT SIDE: 2-3 frosted glass cards (rx=16, translucent fill, gradient border glow) containing:
  - {visual_desc}
  - Cards overlap slightly for depth, floating particles between them
- LEFT SIDE: category pill at top, title "{line1}" and "{line2}" (font-size 42, white, bold), thin gradient accent line, 3 rounded tag chips, date "{date}", footer tech.2twodragon.com
- Gradient accents: blue #3b82f6 + coral #f43f5e
- SVG filters for glass blur and glow effects

All text English only. Make it visually stunning."""


def run_claude(prompt: str, expected_path: str = '') -> str:
    """Run Claude CLI. It may write file directly or return SVG in stdout."""
    try:
        result = subprocess.run(
            ['claude', '-p', prompt],
            capture_output=True, text=True, timeout=180
        )
        # Check if Claude wrote the file directly
        if expected_path and os.path.exists(expected_path):
            with open(expected_path) as f:
                svg = f.read()
            if '<svg' in svg:
                return svg

        # Otherwise extract from stdout
        output = result.stdout
        output = re.sub(r'\x1b[^a-zA-Z]*[a-zA-Z]', '', output)
        output = re.sub(r'\x1b\][^\x07\x1b]*[\x07\x1b]?', '', output)
        m = re.search(r'(<svg[\s\S]*?</svg>)', output)
        return m.group(1) if m else ''
    except Exception as e:
        # Check if file was created despite timeout
        if expected_path and os.path.exists(expected_path):
            with open(expected_path) as f:
                svg = f.read()
            if '<svg' in svg:
                return svg
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
        expected = str(svg_file)
        if args.engine == 'claude':
            svg_content = run_claude(prompt, expected)
        else:
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
