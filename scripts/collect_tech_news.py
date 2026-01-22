#!/usr/bin/env python3
"""
Tech News Collector - 기술/보안 뉴스 수집 스크립트

주요 기술 블로그 및 보안 뉴스 사이트에서 최신 뉴스를 수집합니다.
수집된 뉴스는 JSON 파일로 저장되어 초안 생성에 사용됩니다.

Usage:
    python3 scripts/collect_tech_news.py
    python3 scripts/collect_tech_news.py --sources aws,gcp
    python3 scripts/collect_tech_news.py --hours 24
"""

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse

import feedparser
import requests
from bs4 import BeautifulSoup


# ============================================================================
# 뉴스 소스 설정
# ============================================================================

NEWS_SOURCES = {
    # 한국 기술 뉴스
    "geeknews": {
        "name": "GeekNews (긱뉴스)",
        "url": "https://news.hada.io",
        "feed_url": "https://news.hada.io/rss/news",  # Atom format
        "category": "tech",
        "language": "ko",
        "priority": 1,
    },
    # AWS
    "aws": {
        "name": "AWS Blog",
        "url": "https://aws.amazon.com/blogs/",
        "feed_url": "https://aws.amazon.com/blogs/aws/feed/",
        "category": "cloud",
        "language": "en",
        "priority": 2,
    },
    "aws_security": {
        "name": "AWS Security Blog",
        "url": "https://aws.amazon.com/blogs/security/",
        "feed_url": "https://aws.amazon.com/blogs/security/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "aws_korea": {
        "name": "AWS Korea Blog",
        "url": "https://aws.amazon.com/ko/blogs/tech/",
        "feed_url": "https://aws.amazon.com/ko/blogs/tech/feed/",
        "category": "cloud",
        "language": "ko",
        "priority": 1,
    },
    # Google Cloud
    "gcp": {
        "name": "Google Cloud Blog",
        "url": "https://cloud.google.com/blog/",
        "feed_url": "https://cloudblog.withgoogle.com/rss/",
        "category": "cloud",
        "language": "en",
        "priority": 2,
    },
    # Microsoft
    "microsoft_security": {
        "name": "Microsoft Security Blog",
        "url": "https://www.microsoft.com/en-us/security/blog/",
        "feed_url": "https://www.microsoft.com/en-us/security/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "azure": {
        "name": "Azure Blog",
        "url": "https://azure.microsoft.com/en-us/blog/",
        "feed_url": "https://azure.microsoft.com/en-us/blog/feed/",
        "category": "cloud",
        "language": "en",
        "priority": 2,
    },
    # 보안 기관
    "cisa": {
        "name": "CISA",
        "url": "https://www.cisa.gov/",
        "feed_url": "https://www.cisa.gov/news-events/cybersecurity-advisories/all.xml",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # 보안 뉴스
    "datadog_security": {
        "name": "Datadog Security Labs",
        "url": "https://securitylabs.datadoghq.com/",
        "feed_url": "https://securitylabs.datadoghq.com/rss/feed.xml",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "thehackernews": {
        "name": "The Hacker News",
        "url": "https://thehackernews.com/",
        "feed_url": "https://feeds.feedburner.com/TheHackersNews",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "krebsonsecurity": {
        "name": "Krebs on Security",
        "url": "https://krebsonsecurity.com/",
        "feed_url": "https://krebsonsecurity.com/feed/",
        "category": "security",
        "language": "en",
        "priority": 2,
    },
    # 기술 뉴스
    "hackernews": {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/",
        "feed_url": "https://hnrss.org/frontpage",
        "category": "tech",
        "language": "en",
        "priority": 2,
    },
    # Kubernetes & DevOps
    "kubernetes": {
        "name": "Kubernetes Blog",
        "url": "https://kubernetes.io/blog/",
        "feed_url": "https://kubernetes.io/feed.xml",
        "category": "kubernetes",
        "language": "en",
        "priority": 1,
    },
    "cncf": {
        "name": "CNCF Blog",
        "url": "https://www.cncf.io/blog/",
        "feed_url": "https://www.cncf.io/feed/",
        "category": "devops",
        "language": "en",
        "priority": 2,
    },
    # OWASP
    "owasp": {
        "name": "OWASP Blog",
        "url": "https://owasp.org/blog/",
        "feed_url": "https://owasp.org/feed.xml",
        "category": "security",
        "language": "en",
        "priority": 2,
    },
}


# ============================================================================
# 데이터 클래스
# ============================================================================


@dataclass
class NewsItem:
    """뉴스 아이템 데이터 클래스"""

    id: str
    title: str
    url: str
    source: str
    source_name: str
    category: str
    language: str
    published: str
    summary: str = ""
    content: str = ""
    tags: List[str] = field(default_factory=list)
    author: str = ""
    priority: int = 2

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# 뉴스 수집 함수
# ============================================================================


def generate_id(url: str) -> str:
    """URL을 기반으로 고유 ID 생성"""
    return hashlib.md5(url.encode()).hexdigest()[:12]


def parse_date(date_str: str) -> Optional[datetime]:
    """다양한 형식의 날짜 문자열 파싱"""
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def clean_html(html_content: str) -> str:
    """HTML 태그 제거 및 텍스트 정리"""
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    # 스크립트, 스타일 태그 제거
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator=" ")

    # 연속 공백 제거
    text = re.sub(r"\s+", " ", text).strip()

    # 최대 500자로 제한
    if len(text) > 500:
        text = text[:497] + "..."

    return text


def fetch_rss_feed(
    source_key: str, source_config: dict, hours: int = 24
) -> List[NewsItem]:
    """RSS 피드에서 뉴스 수집"""
    items = []
    feed_url = source_config.get("feed_url")

    if not feed_url:
        return items

    try:
        print(f"  Fetching: {source_config['name']}...")

        # feedparser로 RSS 파싱
        feed = feedparser.parse(feed_url)

        if feed.bozo and feed.bozo_exception:
            print(f"    Warning: Feed parsing issue - {feed.bozo_exception}")

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        for entry in feed.entries[:20]:  # 최대 20개만 처리
            # 날짜 확인
            published = None
            for date_field in ["published", "updated", "created"]:
                if hasattr(entry, date_field):
                    published = parse_date(getattr(entry, date_field))
                    if published:
                        break

            if not published:
                published = datetime.now(timezone.utc)

            # timezone-aware로 변환
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)

            # 시간 필터링
            if published < cutoff_time:
                continue

            # 뉴스 아이템 생성
            title = entry.get("title", "").strip()
            url = entry.get("link", "").strip()

            if not title or not url:
                continue

            # 요약 추출
            summary = ""
            if hasattr(entry, "summary"):
                summary = clean_html(entry.summary)
            elif hasattr(entry, "description"):
                summary = clean_html(entry.description)

            # 콘텐츠 추출
            content = ""
            if hasattr(entry, "content") and entry.content:
                content = clean_html(entry.content[0].get("value", ""))

            # 태그 추출
            tags = []
            if hasattr(entry, "tags"):
                tags = [tag.get("term", "") for tag in entry.tags if tag.get("term")]

            # 작성자 추출
            author = ""
            if hasattr(entry, "author"):
                author = entry.author

            item = NewsItem(
                id=generate_id(url),
                title=title,
                url=url,
                source=source_key,
                source_name=source_config["name"],
                category=source_config["category"],
                language=source_config["language"],
                published=published.isoformat(),
                summary=summary,
                content=content,
                tags=tags[:5],  # 최대 5개 태그
                author=author,
                priority=source_config.get("priority", 2),
            )
            items.append(item)

        print(f"    Found {len(items)} items")

    except Exception as e:
        print(f"    Error: {e}")

    return items


def fetch_all_news(
    sources: Optional[List[str]] = None, hours: int = 24
) -> List[NewsItem]:
    """모든 소스에서 뉴스 수집"""
    all_items = []

    # 소스 필터링
    if sources:
        active_sources = {k: v for k, v in NEWS_SOURCES.items() if k in sources}
    else:
        active_sources = NEWS_SOURCES

    print(
        f"\nCollecting news from {len(active_sources)} sources (last {hours} hours)...\n"
    )

    for source_key, source_config in active_sources.items():
        items = fetch_rss_feed(source_key, source_config, hours)
        all_items.extend(items)

    # 중복 제거 (URL 기준)
    seen_urls = set()
    unique_items = []
    for item in all_items:
        if item.url not in seen_urls:
            seen_urls.add(item.url)
            unique_items.append(item)

    # 우선순위 및 날짜로 정렬
    unique_items.sort(key=lambda x: (x.priority, x.published), reverse=True)

    print(f"\nTotal: {len(unique_items)} unique items collected")

    return unique_items


# ============================================================================
# 저장 함수
# ============================================================================


def save_news_to_json(items: List[NewsItem], output_path: Path) -> None:
    """뉴스 아이템을 JSON 파일로 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "total_items": len(items),
        "items": [item.to_dict() for item in items],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {output_path}")


def load_processed_ids(processed_file: Path) -> set:
    """이미 처리된 뉴스 ID 로드"""
    if not processed_file.exists():
        return set()

    with open(processed_file, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_processed_ids(processed_ids: set, processed_file: Path) -> None:
    """처리된 뉴스 ID 저장"""
    processed_file.parent.mkdir(parents=True, exist_ok=True)

    with open(processed_file, "w", encoding="utf-8") as f:
        json.dump(list(processed_ids), f)


def filter_new_items(items: List[NewsItem], processed_file: Path) -> List[NewsItem]:
    """이미 처리된 뉴스 제외"""
    processed_ids = load_processed_ids(processed_file)
    new_items = [item for item in items if item.id not in processed_ids]

    print(f"Filtered: {len(items)} -> {len(new_items)} new items")

    return new_items


# ============================================================================
# 메인 함수
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="Tech News Collector")
    parser.add_argument(
        "--sources",
        type=str,
        help="Comma-separated list of sources to fetch (e.g., aws,gcp,geeknews)",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours to look back for news (default: 24)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="_data/collected_news.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="List available news sources",
    )
    parser.add_argument(
        "--filter-processed",
        action="store_true",
        help="Filter out already processed news",
    )

    args = parser.parse_args()

    # 소스 목록 출력
    if args.list_sources:
        print("\nAvailable news sources:\n")
        for key, config in NEWS_SOURCES.items():
            print(f"  {key:20} - {config['name']} ({config['category']})")
        return

    # 프로젝트 루트 찾기
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # 소스 파싱
    sources = None
    if args.sources:
        sources = [s.strip() for s in args.sources.split(",")]
        invalid = [s for s in sources if s not in NEWS_SOURCES]
        if invalid:
            print(f"Error: Unknown sources: {invalid}")
            print(f"Available: {list(NEWS_SOURCES.keys())}")
            sys.exit(1)

    # 뉴스 수집
    items = fetch_all_news(sources=sources, hours=args.hours)

    # 이미 처리된 뉴스 필터링
    if args.filter_processed:
        processed_file = project_root / "_data" / "processed_news_ids.json"
        items = filter_new_items(items, processed_file)

    if not items:
        print("\nNo new items to save.")
        return

    # 저장
    output_path = project_root / args.output
    save_news_to_json(items, output_path)

    # 카테고리별 통계
    print("\n--- Statistics ---")
    categories = {}
    for item in items:
        cat = item.category
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    print(f"\nTotal: {len(items)} items")


if __name__ == "__main__":
    main()
