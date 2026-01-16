#!/usr/bin/env python3
"""
Preview Buttondown Email Template
Shows how the email will look before sending.
"""

import os
import sys
import re
import yaml
from pathlib import Path

# .env 파일에서 환경 변수 로드
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / '.env'

if ENV_FILE.exists():
    with open(ENV_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Import functions from buttondown_notify.py
sys.path.insert(0, str(SCRIPT_DIR))
from buttondown_notify import (
    parse_frontmatter,
    get_post_content,
    generate_post_url,
    create_email_content
)


def preview_email(post_path: str, output_file: str = None):
    """Preview email content without sending."""
    post_file = Path(post_path)
    
    if not post_file.exists():
        print(f"❌ Post file not found: {post_path}")
        sys.exit(1)
    
    if not post_file.is_absolute():
        post_file = PROJECT_ROOT / post_path
    
    # Get site URL
    site_url = os.environ.get('SITE_URL', 'https://tech.2twodragon.com')
    
    print("=" * 70)
    print("📧 ButtonDown Email Preview")
    print("=" * 70)
    print(f"📄 Post: {post_file.name}")
    print("")
    
    # Parse post metadata
    frontmatter = parse_frontmatter(str(post_file))
    if not frontmatter:
        print("⚠️ No frontmatter found in post")
        frontmatter = {'title': post_file.stem}
    
    # Generate post URL
    post_url = generate_post_url(str(post_file), site_url)
    
    # Get post content
    post_content = get_post_content(str(post_file))
    filename = post_file.name
    
    # Create email content
    subject, body = create_email_content(frontmatter, post_url, post_content, filename)
    
    # Display preview
    print("=" * 70)
    print("📌 SUBJECT")
    print("=" * 70)
    print(subject)
    print("")
    
    print("=" * 70)
    print("📝 BODY (Markdown)")
    print("=" * 70)
    print(body)
    print("")
    
    # Save to file if requested
    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n\n")
            f.write("=" * 70 + "\n")
            f.write("Email Body (Markdown)\n")
            f.write("=" * 70 + "\n\n")
            f.write(body)
        print(f"✅ Email preview saved to: {output_path}")
    
    print("=" * 70)
    print("💡 Tip: This is how the email will appear to subscribers")
    print("=" * 70)


def main():
    if len(sys.argv) < 2:
        print("Usage: python preview_buttondown_email.py <post_file_path> [output_file.md]")
        print("")
        print("Examples:")
        print("  python preview_buttondown_email.py _posts/2026-01-15-Example.md")
        print("  python preview_buttondown_email.py _posts/2026-01-15-Example.md preview.md")
        sys.exit(1)
    
    post_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    preview_email(post_path, output_file)


if __name__ == "__main__":
    main()
