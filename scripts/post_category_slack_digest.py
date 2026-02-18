#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

import yaml


PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"

DEFAULT_SITE_URL = "https://tech.2twodragon.com"
DEFAULT_TZ_OFFSET = timezone(timedelta(hours=9))

ALIAS_TAGS = {
    "security": "#security",
    "dev": "#dev",
    "ops": "#ops",
}

ALIAS_CATEGORIES = {
    "security": ["security"],
    "dev": ["devsecops"],
    "ops": ["devops"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Slack digest per category")
    parser.add_argument(
        "--window-hours",
        type=int,
        default=24,
        help="Lookback window in hours (default: 24)",
    )
    parser.add_argument(
        "--channel-alias",
        choices=sorted(ALIAS_TAGS.keys()),
        required=True,
        help="Category alias to build digest for",
    )
    parser.add_argument(
        "--site-url",
        default=DEFAULT_SITE_URL,
        help="Base site URL",
    )
    return parser.parse_args()


def parse_post_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    date_str = str(value).strip()
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")
    except ValueError:
        try:
            naive = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return naive.replace(tzinfo=DEFAULT_TZ_OFFSET)
        except ValueError:
            return None


def build_post_url(filename: str, site_url: str) -> str:
    stem = filename[:-3]
    parts = stem.split("-", 3)
    if len(parts) < 4:
        return f"{site_url}/posts/{stem}/"
    year, month, day, slug = parts
    return f"{site_url}/posts/{year}/{month}/{day}/{slug}/"


def load_posts() -> Iterable[Tuple[Path, Dict]]:
    for post_file in POSTS_DIR.glob("*.md"):
        content = post_file.read_text(encoding="utf-8")
        if not content.startswith("---"):
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue
        front_matter = yaml.safe_load(parts[1]) or {}
        yield post_file, front_matter


def normalize_categories(raw: object) -> List[str]:
    if isinstance(raw, list):
        return [str(item).strip().lower() for item in raw if str(item).strip()]
    if isinstance(raw, str):
        return [raw.strip().lower()] if raw.strip() else []
    return []


def build_digest(
    window_hours: int, site_url: str, categories: List[str]
) -> List[Tuple[str, str]]:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(hours=window_hours)
    digest: List[Tuple[str, str]] = []

    for post_file, front_matter in load_posts():
        post_date = parse_post_date(front_matter.get("date"))
        if not post_date:
            continue
        post_date_utc = post_date.astimezone(timezone.utc)
        if post_date_utc < window_start:
            continue

        post_categories = normalize_categories(front_matter.get("categories"))
        title = str(front_matter.get("title", post_file.stem)).strip()
        url = build_post_url(post_file.name, site_url)

        if any(category in post_categories for category in categories):
            digest.append((title, url))

    return digest


def build_message(alias: str, items: List[Tuple[str, str]], window_hours: int) -> str:
    tag = ALIAS_TAGS[alias]
    header = f"{tag} {alias.upper()} | 최근 {window_hours}시간 포스트 {len(items)}건"
    lines = [header]
    for title, url in items:
        lines.append(f"- {title}\n  {url}")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    alias = args.channel_alias
    categories = ALIAS_CATEGORIES[alias]
    digest = build_digest(args.window_hours, args.site_url, categories)
    if not digest:
        return
    message = build_message(alias, digest, args.window_hours)
    print(message)


if __name__ == "__main__":
    main()
