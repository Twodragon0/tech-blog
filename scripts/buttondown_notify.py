#!/usr/bin/env python3
"""
Buttondown Email Notification Script
Automatically sends email to subscribers when new blog posts are published.
"""

import os
import sys
import re
import yaml
import requests
from pathlib import Path
from urllib.parse import quote

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


def parse_frontmatter(file_path: str) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract frontmatter between --- markers
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}

    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}


def get_post_content(file_path: str) -> str:
    """Get the main content of a markdown file (without frontmatter)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove frontmatter
    match = re.match(r'^---\s*\n.*?\n---\s*\n(.*)$', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return content.strip()


def generate_post_url(file_path: str, site_url: str) -> str:
    """Generate the URL for a blog post based on permalink structure."""
    filename = Path(file_path).stem

    # Parse date and title from filename (YYYY-MM-DD-title format)
    match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)', filename)
    if not match:
        return f"{site_url}/posts/{filename}/"

    year, month, day, title = match.groups()

    return f"{site_url}/posts/{year}/{month}/{title}/"


def create_email_content(frontmatter: dict, post_url: str, excerpt: str = None) -> tuple:
    """Create email subject and body for Buttondown."""
    title = frontmatter.get('title', 'New Post')
    description = frontmatter.get('excerpt', frontmatter.get('description', ''))
    tags = frontmatter.get('tags', [])
    category = frontmatter.get('categories', frontmatter.get('category', ''))

    # Email subject
    subject = f"[새 글] {title}"

    # Email body (Markdown format)
    body_parts = [
        f"# {title}",
        "",
    ]

    if description:
        body_parts.extend([description, ""])

    # Tags section
    if tags:
        tag_str = ', '.join([f"`{tag}`" for tag in tags[:5]])
        body_parts.extend([f"**태그:** {tag_str}", ""])

    # Category
    if category:
        if isinstance(category, list):
            category = category[0] if category else ''
        body_parts.extend([f"**카테고리:** {category}", ""])

    # Call to action
    body_parts.extend([
        "---",
        "",
        f"[👉 전체 글 읽기]({post_url})",
        "",
        "---",
        "",
        "이 이메일은 [TwoDragon's Tech Blog](https://tech.2twodragon.com)의 새 글 알림입니다.",
        "",
        "구독 해지를 원하시면 아래 링크를 클릭하세요.",
    ])

    body = "\n".join(body_parts)

    return subject, body


def send_buttondown_email(subject: str, body: str, api_key: str) -> bool:
    """Send email via Buttondown API."""
    url = "https://api.buttondown.com/v1/emails"

    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "subject": subject,
        "body": body,
        "status": "about_to_send"  # Immediately send to subscribers
    }

    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)

        if response.status_code in [200, 201]:
            print(f"✅ Email sent successfully!")
            print(f"   Subject: {subject}")
            return True
        else:
            print(f"❌ Failed to send email: {response.status_code}")
            print(f"   Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python buttondown_notify.py <post_file_path>")
        sys.exit(1)

    post_path = sys.argv[1].strip()
    
    # Remove quotes if present
    if post_path.startswith('"') and post_path.endswith('"'):
        post_path = post_path[1:-1]
    if post_path.startswith("'") and post_path.endswith("'"):
        post_path = post_path[1:-1]

    # Convert to Path object for better handling
    post_file = Path(post_path)
    
    # Try to resolve the path
    if not post_file.is_absolute():
        # If relative, try from project root
        project_root = Path(__file__).parent.parent
        post_file = project_root / post_path
    
    # Validate file exists
    if not post_file.exists():
        print(f"❌ Post file not found: {post_path}")
        print(f"   Resolved path: {post_file}")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Available files in _posts/ (first 10):")
        posts_dir = Path(__file__).parent.parent / '_posts'
        if posts_dir.exists():
            for f in list(posts_dir.glob('*.md'))[:10]:
                print(f"     - {f.name}")
        sys.exit(1)
    
    # Use resolved path
    post_path = str(post_file)

    # Get API key from environment
    api_key = os.environ.get('BUTTONDOWN_API_KEY')
    if not api_key:
        print("❌ BUTTONDOWN_API_KEY environment variable not set")
        sys.exit(1)

    # Get site URL
    site_url = os.environ.get('SITE_URL', 'https://tech.2twodragon.com')

    print(f"📧 Processing post: {post_path}")

    # Parse post metadata
    frontmatter = parse_frontmatter(post_path)
    if not frontmatter:
        print("⚠️ No frontmatter found in post")
        frontmatter = {'title': Path(post_path).stem}

    # Check if post should be published (not draft)
    if frontmatter.get('draft', False):
        print("⏭️ Skipping draft post")
        sys.exit(0)

    # Generate post URL
    post_url = generate_post_url(post_path, site_url)
    print(f"🔗 Post URL: {post_url}")

    # Create email content
    subject, body = create_email_content(frontmatter, post_url)

    # Send email
    success = send_buttondown_email(subject, body, api_key)

    if success:
        print("✅ Buttondown notification complete!")
    else:
        print("❌ Failed to send Buttondown notification")
        sys.exit(1)


if __name__ == "__main__":
    main()
