#!/usr/bin/env python3
"""Regenerate generator-style digest SVGs for the current redesign batch."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parent.parent
POSTS_DIR = BASE_DIR / "_posts"
IMAGES_DIR = BASE_DIR / "assets" / "images"

if str(BASE_DIR / "scripts") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "scripts"))

from auto_publish_news import _convert_svg_to_og_png, generate_svg_image

TARGET_IMAGES = [
    "2026-02-01-Tech_Security_Weekly_Digest_AI_OpenSSL_Zero_Day_OWASP_Agentic_Fortinet.svg",
    "2026-02-02-Weekly_Security_Threat_Intelligence_Digest.svg",
    "2026-02-02-Weekly_Tech_AI_Blockchain_Digest.svg",
    "2026-02-03-Weekly_Security_DevOps_Digest.svg",
    "2026-02-04-Tech_Security_Weekly_Digest_AI_Docker_Data_Go.svg",
    "2026-02-05-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.svg",
    "2026-02-06-Tech_Security_Weekly_Digest_AI_Botnet_Cloud_Threat.svg",
    "2026-02-07-Tech_Security_Weekly_Digest_AI_Malware_Go_Security.svg",
    "2026-02-08-Tech_Security_Weekly_Digest_AI_Ransomware_Data.svg",
    "2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin.svg",
    "2026-02-09-Security_Cloud_Digest_AI_VirusTotal_AWS_Agentic.svg",
    "2026-02-10-AI_Cloud_Digest_Meta_Prometheus_Google_OTLP_AWS.svg",
    "2026-02-10-DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin.svg",
    "2026-02-10-Security_Digest_SolarWinds_UNC3886_LLM_Attack.svg",
    "2026-02-11-Tech_Security_Weekly_Digest_Security_Ransomware_Patch_AI.svg",
    "2026-02-12-Tech_Security_Weekly_Digest_AI_Cloud_Security_Agent.svg",
    "2026-02-13-Tech_Security_Weekly_Digest_AI_Go_Security_Agent.svg",
    "2026-02-14-Weekly_Security_Digest_Microsoft_Zero_Day_Apple_Ivanti_EPMM.svg",
    "2026-02-16-Daily_Tech_Digest_RSS_Roundup.svg",
    "2026-02-17-Tech_Security_Weekly_Digest_AI_Agent_Cloud_Security.svg",
    "2026-02-17-Weekly_Tech_Security_Digest_AI_Cloud_Risk.svg",
    "2026-02-18-Krebs_Security_Digest_Kimwolf_Patch_Tuesday.svg",
    "2026-02-18-Tech_Security_Weekly_Digest_AI_Cloud_Malware_Update.svg",
    "2026-02-19-Tech_Security_Weekly_Digest_AWS_Security_Zero-Day_CVE.svg",
    "2026-02-20-Tech_Blog_Weekly_Digest_AI_Data_Cloud.svg",
    "2026-02-20-Tech_Security_Weekly_Digest_Gemini_AI_Supply_Chain_Kubernetes.svg",
    "2026-02-21-Tech_Security_Weekly_Digest_Data_Rust_AI_Threat.svg",
    "2026-02-22-Tech_Security_Weekly_Digest_AI_Threat_Vulnerability_Security.svg",
    "2026-02-23-Tech_Security_Weekly_Digest_AI_Ransomware_Data_Bitcoin.svg",
    "2026-02-24-Tech_Security_Weekly_Digest_Malware_AI_Docker_LLM.svg",
    "2026-02-25-Tech_Security_Weekly_Digest_AI_Malware_Ransomware_LLM.svg",
    "2026-02-26-Tech_Security_Weekly_Digest_AI_Go_AWS_API.svg",
    "2026-02-27-Tech_Security_Weekly_Digest_AI_Botnet_Blockchain_Go.svg",
    "2026-02-28-Tech_Security_Weekly_Digest_Go_AI_Malware.svg",
    # April 2026 batch
    "2026-04-02-Tech_Security_Weekly_Digest_AI_Malware.svg",
    "2026-04-03-Tech_Security_Weekly_Digest_CVE_Patch_AWS_AI.svg",
    "2026-04-04-Tech_Security_Weekly_Digest_Go_AI_Data_Security.svg",
    "2026-04-05-Tech_Security_Weekly_Digest_AWS_AI_Security_Malware.svg",
    "2026-04-06-Tech_Security_Weekly_Digest_Patch_AI.svg",
    "2026-04-07-Tech_Security_Weekly_Digest_AI_Ransomware_Go_Palantir.svg",
    "2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.svg",
]


def load_front_matter(post_path: Path) -> dict:
    text = post_path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def parse_post_date(post_name: str) -> datetime:
    match = re.match(r"(\d{4}-\d{2}-\d{2})", post_name)
    if not match:
        raise ValueError(f"Cannot parse post date from {post_name}")
    return datetime.fromisoformat(f"{match.group(1)}T00:00:00")


def build_news_items(front_matter: dict, post_name: str) -> list[dict]:
    title = str(front_matter.get("title", "")).strip()
    excerpt = str(front_matter.get("excerpt", "")).strip()
    tags = [
        str(tag).strip() for tag in front_matter.get("tags", []) if str(tag).strip()
    ]

    seeds = [title] + tags[:3]
    items: list[dict] = []
    for index, seed in enumerate(seeds):
        item_title = seed if index == 0 else f"{seed} briefing"
        items.append({"title": item_title, "summary": excerpt})

    if not items:
        items.append({"title": post_name, "summary": excerpt})
    return items


def build_categorized(
    front_matter: dict, news_items: list[dict]
) -> dict[str, list[dict]]:
    categorized: defaultdict[str, list[dict]] = defaultdict(list)
    primary = str(front_matter.get("category", "")).strip().lower()
    secondary = [
        str(category).strip().lower()
        for category in front_matter.get("categories", [])
        if str(category).strip()
    ]
    keys = [key for key in [primary] + secondary if key]
    if not keys:
        keys = ["tech"]

    for key in keys:
        categorized[key].append(news_items[0])
    return dict(categorized)


def index_posts_by_image() -> dict[str, Path]:
    post_map: dict[str, Path] = {}
    for post_path in sorted(POSTS_DIR.glob("*.md")):
        front_matter = load_front_matter(post_path)
        image = str(front_matter.get("image", "")).strip()
        if image:
            post_map[Path(image).name] = post_path
    return post_map


def regenerate_image(image_name: str, post_map: dict[str, Path], dry_run: bool) -> str:
    post_path = post_map.get(image_name)
    if not post_path:
        return f"SKIP no-post {image_name}"

    front_matter = load_front_matter(post_path)
    if not front_matter:
        return f"SKIP no-front-matter {post_path.name}"

    news_items = build_news_items(front_matter, post_path.name)
    categorized = build_categorized(front_matter, news_items)
    post_date = parse_post_date(post_path.name)
    svg_path = IMAGES_DIR / image_name

    if dry_run:
        return f"DRY-RUN {image_name} <- {post_path.name}"

    svg_content = generate_svg_image(post_date, categorized, news_items)
    svg_path.write_text(svg_content, encoding="utf-8")
    _convert_svg_to_og_png(svg_path)
    return f"UPDATED {image_name} <- {post_path.name}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show target mappings without writing SVG files.",
    )
    parser.add_argument(
        "--image",
        action="append",
        dest="images",
        help="Regenerate only the specified image filename. Can be passed multiple times.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the default generator target list and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    targets = args.images or TARGET_IMAGES
    if args.list:
        for image_name in targets:
            print(image_name)
        return 0

    post_map = index_posts_by_image()
    for image_name in targets:
        print(regenerate_image(image_name, post_map, args.dry_run))

    print(f"Done. Targets processed: {len(targets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
