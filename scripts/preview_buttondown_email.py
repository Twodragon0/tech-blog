#!/usr/bin/env python3
"""
Preview Buttondown Email Template
Generates HTML preview file to verify email design before sending.
"""

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
)


def preview_email(post_path: str, output_file: "str | None" = None):
    post_file = Path(post_path)
    if not post_file.is_absolute():
        post_file = PROJECT_ROOT / post_path

    if not post_file.exists():
        print(f"Post file not found: {post_path}")
        sys.exit(1)

    site_url = os.environ.get("SITE_URL", "https://tech.2twodragon.com")

    frontmatter = parse_frontmatter(str(post_file))
    if not frontmatter:
        frontmatter = {"title": post_file.stem}

    post_url = generate_post_url(str(post_file), site_url)
    post_content = get_post_content(str(post_file))
    filename = post_file.name

    subject, body = create_email_content(frontmatter, post_url, post_content, filename)

    print(f"Subject: {subject}")
    print(f"Post: {post_file.name}")
    print(f"URL: {post_url}")

    # Default output to /tmp (Markdown - Buttondown renders it)
    if not output_file:
        output_file = f"/tmp/email_preview_{post_file.stem[:40]}.md"

    output_path = Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(body)

    print(f"Preview saved: {output_path}")
    print(f"Open in browser: file://{output_path.resolve()}")


def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python preview_buttondown_email.py <post_file_path> [output.html]"
        )
        print("")
        print("Examples:")
        print("  python preview_buttondown_email.py _posts/2026-03-09-Example.md")
        print(
            "  python preview_buttondown_email.py _posts/2026-03-09-Example.md preview.html"
        )
        sys.exit(1)

    post_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    preview_email(post_path, output_file)


if __name__ == "__main__":
    main()
