#!/usr/bin/env python3
"""
Vendor News Draft Generator - 보안 벤더 블로그 기반 초안 포스팅 생성

보안 벤더들(Jamf, Zscaler, Cloudflare, Okta, Datadog 등)의 블로그에서
수집한 뉴스를 기반으로 블로그 초안을 생성합니다.

Usage:
    python3 scripts/generate_vendor_news_draft.py
    python3 scripts/generate_vendor_news_draft.py --vendors jamf,cloudflare,okta
    python3 scripts/generate_vendor_news_draft.py --hours 168 --max-items 20
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

VENDOR_SOURCES = [
    "jamf",
    "zscaler",
    "zscaler_research",
    "cloudflare",
    "okta",
    "okta_security",
    "datadog",
    "datadog_security",
    "crowdstrike",
    "paloalto",
    "unit42",
    "snyk",
    "hashicorp",
    "wiz",
    "lacework",
    "sentinelone",
    "aquasec",
    "sysdig",
    "tenable",
    "rapid7",
    "splunk",
    "mandiant",
    "elastic_security",
]

VENDOR_CATEGORIES = {
    "endpoint": ["jamf", "crowdstrike", "sentinelone"],
    "network": ["zscaler", "zscaler_research", "cloudflare", "paloalto", "unit42"],
    "identity": ["okta", "okta_security"],
    "observability": ["datadog", "datadog_security", "splunk", "elastic_security"],
    "devsecops": ["snyk", "aquasec", "sysdig", "wiz", "lacework"],
    "infrastructure": ["hashicorp"],
    "threat_intel": ["mandiant", "tenable", "rapid7"],
}

CATEGORY_NAMES = {
    "endpoint": "엔드포인트 보안",
    "network": "네트워크/클라우드 보안",
    "identity": "ID 및 접근 관리",
    "observability": "관측성 및 SIEM",
    "devsecops": "DevSecOps 및 컨테이너 보안",
    "infrastructure": "인프라 자동화",
    "threat_intel": "위협 인텔리전스",
}


def collect_vendor_news(vendors: List[str], hours: int) -> Optional[dict]:
    script_dir = Path(__file__).parent
    collect_script = script_dir / "collect_tech_news.py"

    if not collect_script.exists():
        print(f"Error: {collect_script} not found")
        return None

    sources = ",".join(vendors)
    cmd = [
        sys.executable,
        str(collect_script),
        "--sources",
        sources,
        "--hours",
        str(hours),
    ]

    print(f"Collecting news from {len(vendors)} vendor sources...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error collecting news: {result.stderr}")
        return None

    output_file = script_dir.parent / "_data" / "collected_news.json"
    if not output_file.exists():
        print(f"Error: Output file not found: {output_file}")
        return None

    with open(output_file, "r", encoding="utf-8") as f:
        return json.load(f)


def categorize_items(items: List[dict]) -> Dict[str, List[dict]]:
    categorized = {cat: [] for cat in VENDOR_CATEGORIES}

    for item in items:
        source = item.get("source", "")
        for category, sources in VENDOR_CATEGORIES.items():
            if source in sources:
                categorized[category].append(item)
                break

    return categorized


def generate_draft_content(items: List[dict], title: str, date_str: str) -> str:
    categorized = categorize_items(items)

    all_tags = set()
    vendors_mentioned = set()

    for item in items:
        all_tags.update(item.get("tags", []))
        source = item.get("source", "")
        if source:
            vendors_mentioned.add(source.replace("_", "-").title())

    tags = ["Security-Vendor-News", "DevSecOps", "Cloud-Security"]
    for vendor in list(vendors_mentioned)[:5]:
        clean_vendor = re.sub(r"[^a-zA-Z0-9-]", "", vendor)
        if clean_vendor:
            tags.append(clean_vendor)
    tags.append(datetime.now().strftime("%Y"))

    front_matter = f"""---
layout: post
title: "{title}"
date: {date_str}
categories: [security, devsecops]
tags: [{", ".join(tags)}]
excerpt: "주요 보안 벤더들의 최신 블로그 포스팅 모음. Jamf, Zscaler, Cloudflare, Okta, Datadog, CrowdStrike, Palo Alto Networks, Snyk 등 보안 업계 동향과 위협 인텔리전스 요약."
comments: true
toc: true
---

"""

    content = f"""## 서론

안녕하세요, **Twodragon**입니다.

이번 포스팅에서는 주요 보안 벤더들의 최신 블로그 포스팅을 정리했습니다.
엔드포인트 보안, 네트워크 보안, ID 관리, DevSecOps 등 다양한 분야의 최신 동향을 확인할 수 있습니다.

**수집 기간**: 최근 7일간 발행된 포스팅
**수집 소스**: {len(vendors_mentioned)}개 벤더 블로그

---

## 📊 빠른 참조

| 분야 | 주요 벤더 | 포스팅 수 |
|------|----------|----------|
"""

    for category, cat_items in categorized.items():
        if cat_items:
            vendor_list = ", ".join(
                [item.get("source_name", "").split()[0] for item in cat_items[:3]]
            )
            content += f"| **{CATEGORY_NAMES.get(category, category)}** | {vendor_list} | {len(cat_items)} |\n"

    content += "\n---\n\n"

    section_num = 1
    for category, cat_items in categorized.items():
        if not cat_items:
            continue

        content += f"## {section_num}. {CATEGORY_NAMES.get(category, category)}\n\n"

        for item in cat_items[:5]:
            title_text = item.get("title", "Untitled")
            url = item.get("url", "#")
            source_name = item.get("source_name", "Unknown")
            summary = item.get("summary", "")[:300]
            published = item.get("published", "")[:10]

            content += f"### {source_name}: {title_text}\n\n"
            content += f"- **URL**: [{url}]({url})\n"
            content += f"- **발행일**: {published}\n\n"

            if summary:
                content += f"> {summary}\n\n"

            content += "---\n\n"

        section_num += 1

    content += """## 결론

이번 주 보안 벤더들의 블로그에서 주목할 만한 주제들:

1. **위협 동향**: 최신 공격 기법과 위협 인텔리전스
2. **제품 업데이트**: 각 벤더의 새로운 기능과 개선 사항
3. **모범 사례**: 보안 운영 및 DevSecOps 베스트 프랙티스
4. **규정 준수**: 컴플라이언스 관련 가이드라인

정기적인 벤더 블로그 모니터링을 통해 최신 보안 트렌드를 파악하시기 바랍니다.

---

## 참고 자료

| 벤더 | 블로그 URL |
|------|------------|
| Jamf | [https://www.jamf.com/blog/](https://www.jamf.com/blog/) |
| Zscaler | [https://www.zscaler.com/blogs](https://www.zscaler.com/blogs) |
| Cloudflare | [https://blog.cloudflare.com/](https://blog.cloudflare.com/) |
| Okta | [https://www.okta.com/blog/](https://www.okta.com/blog/) |
| Datadog | [https://www.datadoghq.com/blog/](https://www.datadoghq.com/blog/) |
| CrowdStrike | [https://www.crowdstrike.com/blog/](https://www.crowdstrike.com/blog/) |
| Palo Alto Networks | [https://www.paloaltonetworks.com/blog/](https://www.paloaltonetworks.com/blog/) |
| Snyk | [https://snyk.io/blog/](https://snyk.io/blog/) |
"""

    return front_matter + content


def save_draft(content: str, filename: str, drafts_dir: Path) -> Path:
    drafts_dir.mkdir(parents=True, exist_ok=True)
    filepath = drafts_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def main():
    parser = argparse.ArgumentParser(description="Generate vendor news draft post")
    parser.add_argument(
        "--vendors",
        type=str,
        help=f"Comma-separated vendor sources (default: all). Available: {', '.join(VENDOR_SOURCES)}",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=168,
        help="Hours to look back (default: 168 = 7 days)",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=30,
        help="Maximum items per draft (default: 30)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="_drafts",
        help="Output directory for drafts (default: _drafts)",
    )
    parser.add_argument(
        "--list-vendors", action="store_true", help="List available vendor sources"
    )

    args = parser.parse_args()

    if args.list_vendors:
        print("\nAvailable vendor sources:\n")
        for category, sources in VENDOR_CATEGORIES.items():
            print(f"  {CATEGORY_NAMES.get(category, category)}:")
            for source in sources:
                print(f"    - {source}")
        return

    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    if args.vendors:
        vendors = [v.strip() for v in args.vendors.split(",")]
        invalid = [v for v in vendors if v not in VENDOR_SOURCES]
        if invalid:
            print(f"Error: Unknown vendors: {invalid}")
            print(f"Available: {VENDOR_SOURCES}")
            sys.exit(1)
    else:
        vendors = VENDOR_SOURCES

    news_data = collect_vendor_news(vendors, args.hours)

    if not news_data or not news_data.get("items"):
        print("No news items collected.")
        return

    items = news_data.get("items", [])[: args.max_items]
    print(f"\nProcessing {len(items)} items for draft generation...")

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S +0900")
    date_prefix = now.strftime("%Y-%m-%d")

    title = f"보안 벤더 블로그 주간 리뷰 ({now.strftime('%Y년 %m월 %d일')})"
    filename = f"{date_prefix}-Security_Vendor_Blog_Weekly_Review.md"

    content = generate_draft_content(items, title, date_str)

    drafts_dir = project_root / args.output_dir
    filepath = save_draft(content, filename, drafts_dir)

    print(f"\n✅ Draft generated: {filepath}")
    print(f"   - Total items: {len(items)}")
    print(f"   - Vendors: {len(vendors)}")
    print("\nTo publish, move to _posts/:")
    print(f"   mv {filepath} _posts/")


if __name__ == "__main__":
    main()
