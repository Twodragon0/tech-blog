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

import socket

import feedparser
import requests
from bs4 import BeautifulSoup

# 기본 소켓 타임아웃 설정 (개별 피드 행 방지)
DEFAULT_FEED_TIMEOUT = 30  # seconds


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
    "aws_ml": {
        "name": "AWS Machine Learning Blog",
        "url": "https://aws.amazon.com/blogs/machine-learning/",
        "feed_url": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "category": "ai",
        "language": "en",
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
    "gcp_security": {
        "name": "Google Cloud Security Bulletins",
        "url": "https://cloud.google.com/support/bulletins",
        "feed_url": "https://cloud.google.com/feeds/google-cloud-security-bulletins.xml",
        "category": "security",
        "language": "en",
        "priority": 1,
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
    "azure_security": {
        "name": "Azure Security Blog",
        "url": "https://azure.microsoft.com/en-us/blog/category/security/",
        "feed_url": "https://azure.microsoft.com/en-us/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "microsoft_intune": {
        "name": "Microsoft Intune Blog",
        "url": "https://techcommunity.microsoft.com/t5/microsoft-intune-blog/bg-p/MicrosoftEndpointManagerBlog",
        "feed_url": "https://techcommunity.microsoft.com/plugins/custom/microsoft/o365/custom-blog-rss?tid=-292701202&board=MicrosoftEndpointManagerBlog&size=20",
        "category": "security",
        "language": "en",
        "priority": 1,
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
    # ============================================================================
    # Security Vendors (Jamf, Zscaler, Cloudflare, Okta, Datadog, etc.)
    # ============================================================================
    # Jamf
    "jamf": {
        "name": "Jamf Blog",
        "url": "https://www.jamf.com/blog/",
        "feed_url": "https://www.jamf.com/blog/rss/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Zscaler
    "zscaler": {
        "name": "Zscaler Blog",
        "url": "https://www.zscaler.com/blogs",
        "feed_url": "https://www.zscaler.com/blogs/feed",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "zscaler_research": {
        "name": "Zscaler ThreatLabz",
        "url": "https://www.zscaler.com/blogs/security-research",
        "feed_url": "https://www.zscaler.com/blogs/security-research/feed",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Cloudflare
    "cloudflare": {
        "name": "Cloudflare Blog",
        "url": "https://blog.cloudflare.com/",
        "feed_url": "https://blog.cloudflare.com/rss/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Okta
    "okta": {
        "name": "Okta Blog",
        "url": "https://www.okta.com/blog/",
        "feed_url": "https://www.okta.com/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "okta_security": {
        "name": "Okta Security Blog",
        "url": "https://sec.okta.com/",
        "feed_url": "https://sec.okta.com/rss",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Datadog
    "datadog": {
        "name": "Datadog Blog",
        "url": "https://www.datadoghq.com/blog/",
        "feed_url": "https://www.datadoghq.com/blog/feed/",
        "category": "devops",
        "language": "en",
        "priority": 1,
    },
    # CrowdStrike
    "crowdstrike": {
        "name": "CrowdStrike Blog",
        "url": "https://www.crowdstrike.com/blog/",
        "feed_url": "https://www.crowdstrike.com/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Palo Alto Networks
    "paloalto": {
        "name": "Palo Alto Networks Blog",
        "url": "https://www.paloaltonetworks.com/blog/",
        "feed_url": "https://www.paloaltonetworks.com/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    "unit42": {
        "name": "Unit 42 (Palo Alto)",
        "url": "https://unit42.paloaltonetworks.com/",
        "feed_url": "https://unit42.paloaltonetworks.com/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Snyk
    "snyk": {
        "name": "Snyk Blog",
        "url": "https://snyk.io/blog/",
        "feed_url": "https://snyk.io/blog/feed/",
        "category": "devsecops",
        "language": "en",
        "priority": 1,
    },
    # HashiCorp
    "hashicorp": {
        "name": "HashiCorp Blog",
        "url": "https://www.hashicorp.com/blog/",
        "feed_url": "https://www.hashicorp.com/blog/feed.xml",
        "category": "devops",
        "language": "en",
        "priority": 1,
    },
    # Wiz
    "wiz": {
        "name": "Wiz Blog",
        "url": "https://www.wiz.io/blog/",
        "feed_url": "https://www.wiz.io/blog/rss.xml",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Lacework
    "lacework": {
        "name": "Lacework Blog",
        "url": "https://www.lacework.com/blog/",
        "feed_url": "https://www.lacework.com/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 2,
    },
    # SentinelOne
    "sentinelone": {
        "name": "SentinelOne Blog",
        "url": "https://www.sentinelone.com/blog/",
        "feed_url": "https://www.sentinelone.com/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Aqua Security
    "aquasec": {
        "name": "Aqua Security Blog",
        "url": "https://blog.aquasec.com/",
        "feed_url": "https://blog.aquasec.com/rss.xml",
        "category": "devsecops",
        "language": "en",
        "priority": 1,
    },
    # Sysdig
    "sysdig": {
        "name": "Sysdig Blog",
        "url": "https://sysdig.com/blog/",
        "feed_url": "https://sysdig.com/blog/feed/",
        "category": "devsecops",
        "language": "en",
        "priority": 1,
    },
    # Tenable
    "tenable": {
        "name": "Tenable Blog",
        "url": "https://www.tenable.com/blog/",
        "feed_url": "https://www.tenable.com/blog/feed",
        "category": "security",
        "language": "en",
        "priority": 2,
    },
    # Rapid7
    "rapid7": {
        "name": "Rapid7 Blog",
        "url": "https://www.rapid7.com/blog/",
        "feed_url": "https://www.rapid7.com/blog/feed/",
        "category": "security",
        "language": "en",
        "priority": 2,
    },
    # Splunk
    "splunk": {
        "name": "Splunk Blog",
        "url": "https://www.splunk.com/en_us/blog.html",
        "feed_url": "https://www.splunk.com/en_us/blog/feed.xml",
        "category": "security",
        "language": "en",
        "priority": 2,
    },
    # Mandiant (Google)
    "mandiant": {
        "name": "Mandiant Blog",
        "url": "https://www.mandiant.com/resources/blog",
        "feed_url": "https://www.mandiant.com/resources/blog/rss.xml",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Elastic Security
    "elastic_security": {
        "name": "Elastic Security Labs",
        "url": "https://www.elastic.co/security-labs/",
        "feed_url": "https://www.elastic.co/security-labs/rss/feed.xml",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # Google Online Security
    "google_security": {
        "name": "Google Online Security Blog",
        "url": "https://security.googleblog.com/",
        "feed_url": "https://security.googleblog.com/feeds/posts/default",
        "category": "security",
        "language": "en",
        "priority": 1,
    },
    # ============================================================================
    # AI & Machine Learning
    # ============================================================================
    # TensorFlow
    "tensorflow": {
        "name": "TensorFlow Blog",
        "url": "https://blog.tensorflow.org/",
        "feed_url": "https://blog.tensorflow.org/feeds/posts/default",
        "category": "ai",
        "language": "en",
        "priority": 1,
    },
    # Palantir
    "palantir": {
        "name": "Palantir Blog",
        "url": "https://blog.palantir.com/",
        "feed_url": "https://blog.palantir.com/feed",
        "category": "ai",
        "language": "en",
        "priority": 1,
    },
    # OpenAI
    "openai": {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog",
        "feed_url": "https://openai.com/blog/rss.xml",
        "category": "ai",
        "language": "en",
        "priority": 1,
    },
    # Google AI
    "google_ai": {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/",
        "feed_url": "https://blog.google/technology/ai/rss/",
        "category": "ai",
        "language": "en",
        "priority": 1,
    },
    # Hugging Face
    "huggingface": {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog",
        "feed_url": "https://huggingface.co/blog/feed.xml",
        "category": "ai",
        "language": "en",
        "priority": 2,
    },
    # Meta Engineering (Data + AI)
    "meta_engineering": {
        "name": "Meta Engineering Blog",
        "url": "https://engineering.fb.com/",
        "feed_url": "https://engineering.fb.com/feed/",
        "category": "ai",
        "language": "en",
        "priority": 1,
    },
    # Google Research (AI/ML)
    "google_research": {
        "name": "Google Research Blog",
        "url": "https://blog.research.google/",
        "feed_url": "https://blog.research.google/feeds/posts/default",
        "category": "ai",
        "language": "en",
        "priority": 1,
    },
    # Netflix Tech Blog (Data Engineering, ML)
    "netflix_tech": {
        "name": "Netflix Tech Blog",
        "url": "https://netflixtechblog.com/",
        "feed_url": "https://netflixtechblog.com/feed",
        "category": "ai",
        "language": "en",
        "priority": 2,
    },
    # ============================================================================
    # Blockchain & Cryptocurrency
    # ============================================================================
    # Ethereum
    "ethereum": {
        "name": "Ethereum Foundation Blog",
        "url": "https://blog.ethereum.org/",
        "feed_url": "https://blog.ethereum.org/feed",
        "category": "blockchain",
        "language": "en",
        "priority": 1,
    },
    # CoinDesk
    "coindesk": {
        "name": "CoinDesk",
        "url": "https://www.coindesk.com/",
        "feed_url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "category": "blockchain",
        "language": "en",
        "priority": 1,
    },
    # Bitcoin Magazine
    "bitcoin_magazine": {
        "name": "Bitcoin Magazine",
        "url": "https://bitcoinmagazine.com/",
        "feed_url": "https://bitcoinmagazine.com/.rss/full/",
        "category": "blockchain",
        "language": "en",
        "priority": 1,
    },
    # Cointelegraph
    "cointelegraph": {
        "name": "Cointelegraph",
        "url": "https://cointelegraph.com/",
        "feed_url": "https://cointelegraph.com/rss",
        "category": "blockchain",
        "language": "en",
        "priority": 2,
    },
    # Vitalik Buterin Blog
    "vitalik": {
        "name": "Vitalik Buterin Blog",
        "url": "https://vitalik.eth.limo/",
        "feed_url": "https://vitalik.eth.limo/feed.xml",
        "category": "blockchain",
        "language": "en",
        "priority": 1,
    },
    # Chainalysis
    "chainalysis": {
        "name": "Chainalysis Blog",
        "url": "https://www.chainalysis.com/blog/",
        "feed_url": "https://www.chainalysis.com/blog/feed/",
        "category": "blockchain",
        "language": "en",
        "priority": 1,
    },
    # ============================================================================
    # DevSecOps
    # ============================================================================
    # DevSecOps.org
    "devsecops_org": {
        "name": "DevSecOps.org Blog",
        "url": "https://www.devsecops.org/blog",
        "feed_url": "https://www.devsecops.org/blog?format=rss",
        "category": "devsecops",
        "language": "en",
        "priority": 1,
    },
    # ============================================================================
    # Korean Security Vendors
    # ============================================================================
    # SK쉴더스 EQST insight (월간 보안 뉴스레터)
    "skshieldus_eqst": {
        "name": "SK쉴더스 EQST insight",
        "url": "https://www.skshieldus.com/kor/media/newsletter/insight.do",
        "feed_url": None,  # No RSS - custom scraper
        "scraper": "skshieldus_eqst",
        "category": "security",
        "language": "ko",
        "priority": 1,
    },
    # SK쉴더스 보안 리포트 (KARA 랜섬웨어 보고서, 보안 가이드 등)
    "skshieldus_report": {
        "name": "SK쉴더스 보안 리포트",
        "url": "https://www.skshieldus.com/kor/media/newsletter/insight.do",
        "feed_url": None,  # No RSS - custom scraper
        "scraper": "skshieldus_report",
        "category": "security",
        "language": "ko",
        "priority": 1,
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


def fetch_skshieldus_insight(
    source_key: str, source_config: dict, hours: int = 24
) -> List[NewsItem]:
    """SK쉴더스 인사이트 페이지에서 뉴스 수집 (EQST insight / Report)"""
    items = []
    base_url = "https://www.skshieldus.com"
    insight_url = f"{base_url}/kor/media/newsletter/insight.do"

    try:
        print(f"  Fetching: {source_config['name']}...")

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        response = requests.get(insight_url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        scraper_type = source_config.get("scraper", "")

        if scraper_type == "skshieldus_eqst":
            items = _parse_skshieldus_eqst(soup, source_key, source_config, cutoff_time)
        elif scraper_type == "skshieldus_report":
            items = _parse_skshieldus_report(
                soup, source_key, source_config, cutoff_time
            )

        print(f"    Found {len(items)} items")

    except Exception as e:
        print(f"    Error fetching SK쉴더스: {e}")

    return items


def _extract_title_from_url(url: str) -> str:
    """URL의 o_fname 파라미터에서 파일명(제목) 추출"""
    from urllib.parse import unquote, urlparse, parse_qs

    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        if "o_fname" in params:
            filename = unquote(params["o_fname"][0])
            title = filename.replace(".pdf", "").replace("_", " ")
            title = re.sub(r"\s+", " ", title).strip()
            return title
    except (ValueError, KeyError, AttributeError, IndexError) as e:
        # URL 파싱 실패는 정상적인 경우일 수 있으므로 조용히 처리
        # 개발 환경에서만 디버깅을 위한 로그 출력
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            print(f"    Warning: Failed to extract title from URL: {type(e).__name__}")
    except Exception as e:
        # 예상치 못한 예외는 로깅
        if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
            print(f"    Warning: Unexpected error extracting title from URL: {type(e).__name__}: {e}")
    return ""


def _parse_skshieldus_eqst(
    soup: BeautifulSoup, source_key: str, source_config: dict, cutoff_time: datetime
) -> List[NewsItem]:
    """EQST insight 탭 파싱"""
    items = []
    base_url = "https://www.skshieldus.com"

    eqst_items = soup.select('[fs-cmsfilter-element="list-2"] [role="listitem"]')

    for item_el in eqst_items[:20]:
        try:
            year = "2025"
            month = "01"

            text_content = item_el.get_text()
            year_match = re.search(r"(\d{4})\s*년", text_content)
            month_match = re.search(r"(\d{1,2})\s*월", text_content)

            if year_match:
                year = year_match.group(1)
            if month_match:
                month = month_match.group(1).zfill(2)

            published = datetime(int(year), int(month), 1, tzinfo=timezone.utc)

            download_link = item_el.select_one('a[href*="download"]')
            if download_link:
                url = str(download_link.get("href", ""))
                if not url.startswith("http"):
                    url = base_url + url
                title = _extract_title_from_url(url)
            else:
                url = f"{base_url}/kor/media/newsletter/insight.do#eqst-{year}-{month}"
                title = ""

            if not title or len(title) < 5:
                title = f"SK쉴더스 EQST insight {year}년 {month}월호"

            category_text = ""
            for div in item_el.select("div"):
                text = div.get_text(strip=True)
                if (
                    "Headline" in text
                    or "Ransomware" in text
                    or "Special Report" in text
                ):
                    category_text = text
                    break

            tags = ["SK쉴더스", "EQST", "보안인사이트", f"{year}년{month}월"]
            if "Ransomware" in category_text or "랜섬웨어" in title:
                tags.append("랜섬웨어")
            if "제로트러스트" in title:
                tags.append("제로트러스트")

            item = NewsItem(
                id=generate_id(url),
                title=title,
                url=url,
                source=source_key,
                source_name=source_config["name"],
                category=source_config["category"],
                language=source_config["language"],
                published=published.isoformat(),
                summary=f"SK쉴더스 EQST insight {year}년 {month}월호 - {category_text}"
                if category_text
                else title,
                content="",
                tags=tags[:5],
                author="SK쉴더스 EQST",
                priority=source_config.get("priority", 1),
            )
            items.append(item)

        except Exception as e:
            continue

    return items


def _parse_skshieldus_report(
    soup: BeautifulSoup, source_key: str, source_config: dict, cutoff_time: datetime
) -> List[NewsItem]:
    """보안 리포트 탭 파싱"""
    items = []
    base_url = "https://www.skshieldus.com"

    report_items = soup.select('[fs-cmsfilter-element="list"] [role="listitem"]')

    for item_el in report_items[:20]:
        try:
            download_link = item_el.select_one('a[href*="download"]')
            if not download_link:
                continue

            url = str(download_link.get("href", ""))
            if not url.startswith("http"):
                url = base_url + url

            title = _extract_title_from_url(url)

            if not title or len(title) < 5:
                title_el = item_el.select_one('[class*="title"], [class*="name"]')
                if title_el:
                    title = title_el.get_text(strip=True)
                else:
                    for div in item_el.select("div"):
                        text = div.get_text(strip=True)
                        if text and len(text) > 10 and "Download" not in text:
                            title = text
                            break

            if not title or len(title) < 5:
                continue

            published = datetime.now(timezone.utc)
            if "'25" in title or "2025" in title:
                published = datetime(2025, 1, 15, tzinfo=timezone.utc)
            elif "'24" in title or "2024" in title:
                published = datetime(2024, 6, 15, tzinfo=timezone.utc)

            tags = ["SK쉴더스", "보안리포트"]
            if "KARA" in title or "랜섬웨어" in title:
                tags.extend(["KARA", "랜섬웨어"])
            if "ISMS" in title or "관리체계" in title:
                tags.append("ISMS-P")
            if "CSPM" in title or "AWS" in title:
                tags.extend(["CSPM", "클라우드보안"])
            if "LLM" in title or "AI" in title:
                tags.append("AI보안")
            if "취약점" in title:
                tags.append("취약점")

            item = NewsItem(
                id=generate_id(url),
                title=title.replace('"', "").replace("'", ""),
                url=url,
                source=source_key,
                source_name=source_config["name"],
                category=source_config["category"],
                language=source_config["language"],
                published=published.isoformat(),
                summary=f"SK쉴더스 보안 리포트: {title[:100]}",
                content="",
                tags=list(set(tags))[:5],
                author="SK쉴더스",
                priority=source_config.get("priority", 1),
            )
            items.append(item)

        except Exception as e:
            continue

    return items


def fetch_rss_feed(
    source_key: str, source_config: dict, hours: int = 24, timeout: int = 30
) -> List[NewsItem]:
    """RSS 피드에서 뉴스 수집 (per-feed socket timeout 적용)"""
    items = []
    feed_url = source_config.get("feed_url")

    if not feed_url:
        return items

    # per-feed socket timeout 설정
    old_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)

    try:
        print(f"  Fetching: {source_config['name']}...")

        # feedparser로 RSS 파싱 (request_headers로 타임아웃 힌트)
        feed = feedparser.parse(
            feed_url,
            request_headers={"User-Agent": "TechBlog-NewsCollector/1.0"}
        )

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
                # Skip items without a publication date - they're likely archive items
                continue

            # timezone-aware로 변환
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)

            # 시간 필터링
            if published < cutoff_time:
                continue

            raw_title = entry.get("title", "")
            title = raw_title.strip() if isinstance(raw_title, str) else ""
            raw_url = entry.get("link", "")
            url = raw_url.strip() if isinstance(raw_url, str) else ""

            if not title or not url:
                continue

            summary = ""
            raw_summary = getattr(entry, "summary", None)
            if raw_summary and isinstance(raw_summary, str):
                summary = clean_html(raw_summary)
            elif not summary:
                raw_desc = getattr(entry, "description", None)
                if raw_desc and isinstance(raw_desc, str):
                    summary = clean_html(raw_desc)

            content = ""
            raw_content = getattr(entry, "content", None)
            if raw_content and isinstance(raw_content, list) and len(raw_content) > 0:
                content_val = raw_content[0].get("value", "") if isinstance(raw_content[0], dict) else ""
                if isinstance(content_val, str):
                    content = clean_html(content_val)

            tags: list[str] = []
            raw_tags = getattr(entry, "tags", None)
            if raw_tags and isinstance(raw_tags, list):
                tags = [str(tag.get("term", "")) for tag in raw_tags if isinstance(tag, dict) and tag.get("term")]

            author = ""
            raw_author = getattr(entry, "author", None)
            if raw_author and isinstance(raw_author, str):
                author = raw_author

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

    except socket.timeout:
        print(f"    Timeout: {source_config['name']} ({timeout}s)")
    except Exception as e:
        print(f"    Error: {e}")
    finally:
        socket.setdefaulttimeout(old_timeout)

    return items


def fetch_all_news(
    sources: Optional[List[str]] = None,
    hours: int = 24,
    feed_timeout: int = DEFAULT_FEED_TIMEOUT,
) -> List[NewsItem]:
    """모든 소스에서 뉴스 수집"""
    all_items = []

    # 소스 필터링
    if sources:
        active_sources = {k: v for k, v in NEWS_SOURCES.items() if k in sources}
    else:
        active_sources = NEWS_SOURCES

    print(
        f"\nCollecting news from {len(active_sources)} sources (last {hours} hours, timeout {feed_timeout}s/feed)...\n"
    )

    for source_key, source_config in active_sources.items():
        scraper = source_config.get("scraper")
        if scraper and scraper.startswith("skshieldus"):
            items = fetch_skshieldus_insight(source_key, source_config, hours)
        else:
            items = fetch_rss_feed(source_key, source_config, hours, timeout=feed_timeout)
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


def load_recent_post_titles(posts_dir: Path = Path("_posts"), days: int = 7) -> set:
    """최근 포스트에서 사용된 뉴스 제목들을 로드하여 중복 방지"""
    titles = set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    for post_file in sorted(posts_dir.glob("*.md"), reverse=True)[:14]:  # Last 14 posts
        try:
            filename = post_file.name
            # Extract date from filename
            date_str = filename[:10]
            post_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if post_date < cutoff:
                break

            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract titles from markdown headers (### x.x Title)
                for match in re.finditer(r'### \d+\.\d+ (.+)', content):
                    titles.add(match.group(1).strip().lower()[:50])
        except (ValueError, OSError):
            continue

    return titles


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
    parser.add_argument(
        "--feed-timeout",
        type=int,
        default=DEFAULT_FEED_TIMEOUT,
        help=f"Per-feed socket timeout in seconds (default: {DEFAULT_FEED_TIMEOUT})",
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
    items = fetch_all_news(
        sources=sources, hours=args.hours, feed_timeout=args.feed_timeout
    )

    # 최근 포스트에서 다룬 뉴스 제목 중복 제거
    recent_titles = load_recent_post_titles()
    if recent_titles:
        before_count = len(items)
        items = [item for item in items if item.title.strip().lower()[:50] not in recent_titles]
        dedup_count = before_count - len(items)
        if dedup_count > 0:
            print(f"\nDeduplicated: removed {dedup_count} items already covered in recent posts")

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
