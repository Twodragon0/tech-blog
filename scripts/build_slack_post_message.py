#!/usr/bin/env python3
"""Build Slack notification message for new blog posts.

Usage:
    python3 scripts/build_slack_post_message.py "path1.md\npath2.md"

Outputs GitHub Actions output format:
    message<<EOF
    ...message content...
    EOF
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

SITE_URL = os.environ.get("SITE_URL", "https://tech.2twodragon.com")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def extract_frontmatter(post_path: Path) -> dict:
    """Extract YAML frontmatter from a post file."""
    content = post_path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    return yaml.safe_load(parts[1]) or {}


def build_post_url(filename: str) -> str:
    """Build post URL from filename."""
    stem = Path(filename).stem
    parts = stem.split("-", 3)
    if len(parts) < 4:
        return f"{SITE_URL}/posts/{stem}/"
    year, month, _day, slug = parts
    return f"{SITE_URL}/posts/{year}/{month}/{slug}/"


def get_category(fm: dict) -> str:
    """Extract category from frontmatter."""
    cats = fm.get("categories", fm.get("category", ""))
    if isinstance(cats, list) and cats:
        return str(cats[0])
    return str(cats) if cats else ""


def main() -> None:
    if len(sys.argv) < 2:
        print("message=No posts provided", flush=True)
        return

    raw_input = sys.argv[1]
    post_files = [p.strip() for p in raw_input.split("\n") if p.strip()]

    if not post_files:
        print("message=No posts provided", flush=True)
        return

    lines = [f"📝 새 포스트 {len(post_files)}건이 발행되었습니다"]

    for pf in post_files:
        post_path = PROJECT_ROOT / pf
        if not post_path.exists():
            continue

        fm = extract_frontmatter(post_path)
        title = fm.get("title", post_path.stem)
        category = get_category(fm)
        url = build_post_url(post_path.name)

        if category:
            lines.append(f"• <{url}|{title}> [{category}]")
        else:
            lines.append(f"• <{url}|{title}>")

    lines.append("")
    lines.append(f"🔗 {SITE_URL}")

    message = "\n".join(lines)

    print("message<<EOF")
    print(message)
    print("EOF")


if __name__ == "__main__":
    main()
