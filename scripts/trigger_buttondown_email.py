#!/usr/bin/env python3
"""
Trigger Buttondown email for an existing post.
Supports dry-run (preview) and live sending.
"""

import argparse
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ENV_FILE = PROJECT_ROOT / ".env"

if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                value = value.strip().strip('"').strip("'")
                os.environ[key.strip()] = value

sys.path.insert(0, str(SCRIPT_DIR))
from buttondown_notify import (
    create_email_content,
    generate_post_url,
    get_post_content,
    parse_frontmatter,
    send_buttondown_email,
)


def main():
    parser = argparse.ArgumentParser(description="Trigger Buttondown email for a post")
    parser.add_argument("post_path", help="Path to the blog post file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation")
    parser.add_argument("--preview-html", help="Save HTML preview to file")
    args = parser.parse_args()

    post_file = Path(args.post_path)
    if not post_file.is_absolute():
        post_file = PROJECT_ROOT / args.post_path
    if not post_file.exists():
        print(f"Post file not found: {args.post_path}")
        sys.exit(1)

    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key and not args.dry_run:
        print("BUTTONDOWN_API_KEY not set. Use --dry-run to preview.")
        sys.exit(1)

    site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")

    frontmatter = parse_frontmatter(str(post_file))
    if not frontmatter:
        frontmatter = {"title": post_file.stem}

    if frontmatter.get("draft", False):
        print("Skipping draft post")
        sys.exit(0)

    post_url = generate_post_url(str(post_file), site_url)
    post_content = get_post_content(str(post_file))
    subject, body = create_email_content(frontmatter, post_url, post_content, post_file.name)

    print(f"Post: {post_file.name}")
    print(f"Subject: {subject}")
    print(f"URL: {post_url}")
    print(f"Body size: {len(body):,} bytes")

    if args.preview_html:
        with open(args.preview_html, "w", encoding="utf-8") as f:
            f.write(body)
        print(f"Preview saved: {args.preview_html}")

    if args.dry_run:
        print("Dry run complete (email not sent)")
        return

    auto_yes = args.yes or os.environ.get("TECH_BLOG_AUTO_YES") or os.environ.get("CI")
    if not auto_yes:
        confirm = input("Send to ALL subscribers? (yes/no): ").strip().lower()
        if confirm not in ["yes", "y"]:
            print("Cancelled")
            return

    success = send_buttondown_email(subject, body, api_key)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
