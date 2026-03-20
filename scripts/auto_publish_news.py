#!/usr/bin/env python3
"""
Auto Publish News - 자동 뉴스 포스트 발행 스크립트

RSS에서 수집된 뉴스를 기반으로 고품질 블로그 포스트를 자동 생성하고
_posts 폴더에 직접 발행합니다.

Features:
- AI 요약 카드 자동 생성
- SVG 이미지 자동 생성
- 기존 포스트 스타일과 일관성 유지
- 뉴스 카테고리별 분류 및 분석
- 보안 다이제스트 / 테크 블로그 다이제스트 모드 지원

Usage:
    python3 scripts/auto_publish_news.py
    python3 scripts/auto_publish_news.py --dry-run
    python3 scripts/auto_publish_news.py --hours 48
    python3 scripts/auto_publish_news.py --mode tech-blog
    python3 scripts/auto_publish_news.py --mode security --force
"""

import argparse
import html
import json
import logging
import os
import re
import subprocess
import sys
import unicodedata
import yaml
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# ============================================================================
# 설정
# ============================================================================

POSTS_DIR = Path("_posts")
IMAGES_DIR = Path("assets/images")
DATA_DIR = Path("_data")  # 실제 데이터 디렉토리
PUBLISHED_URLS_FILE = DATA_DIR / "published_news_urls.json"
PUBLISHED_URLS_TTL_DAYS = 7  # Track published URLs for 7 days
KOREAN_SUMMARY_CACHE: Dict[str, str] = {}
KOREAN_TITLE_CACHE: Dict[str, str] = {}

CATEGORY_PRIORITY = {
    "security": 1,
    "devsecops": 2,
    "ai": 3,
    "cloud": 4,
    "devops": 5,
    "blockchain": 6,
    "tech": 7,
}

CATEGORY_EMOJI = {
    "security": "🔒",
    "devsecops": "🛡️",
    "ai": "🤖",
    "cloud": "☁️",
    "devops": "⚙️",
    "tech": "💻",
    "kubernetes": "🚀",
    "blockchain": "⛓️",
    "finops": "💰",
}

CATEGORY_COLOR = {
    "security": "#ef4444",
    "devsecops": "#8b5cf6",
    "ai": "#6366f1",
    "cloud": "#22c55e",
    "devops": "#f59e0b",
    "blockchain": "#f97316",
    "tech": "#3b82f6",
}

SOURCE_PRIORITY = {
    "thehackernews": 1,
    "microsoft_security": 1,
    "aws_security": 1,
    "gcp": 2,
    "hashicorp": 2,
    "cncf": 2,
    "geeknews": 2,
    "hackernews": 3,
    "skshieldus": 2,
    "skshieldus_report": 2,
    "palantir": 1,
    "openai": 1,
    "google_ai": 1,
    "meta_engineering": 1,
    "huggingface": 2,
    "google_research": 1,
    "netflix_tech": 2,
    "bitcoin_magazine": 1,
    "cointelegraph": 2,
    "vitalik": 1,
    "chainalysis": 1,
    "microsoft_devblogs": 1,
    "microsoft_dotnet": 2,
    "github_blog": 1,
    "stripe": 2,
    "slack_engineering": 2,
    "x_engineering": 1,
    "apple_ml": 1,
    "spotify_engineering": 2,
    "discord": 2,
    "docker": 1,
    "google_developers": 1,
    "rust_lang": 2,
    "golang": 2,
    "apple_developer": 1,
    "apple_newsroom": 2,
    "webkit": 2,
    "worldmonitor_tech": 1,
    # Korean tech blogs
    "kakao_tech": 1,
    "naver_d2": 1,
    "line_engineering": 2,
    "toss_tech": 1,
    "woowahan_tech": 2,
    "daangn_tech": 2,
    "coupang_tech": 2,
    # Korean security vendors
    "ahnlab_asec": 1,
    # AI/ML blogs
    "nvidia_ai": 1,
    # DevOps/Platform blogs
    "gitlab": 1,
    "vercel": 2,
    # Additional security vendors
    "sophos": 2,
}

# Tech blog sources (non-security, non-blockchain)
TECH_BLOG_SOURCES = {
    "geeknews",
    "hackernews",
    "palantir",
    "openai",
    "google_ai",
    "meta_engineering",
    "huggingface",
    "google_research",
    "netflix_tech",
    "microsoft_devblogs",
    "microsoft_dotnet",
    "github_blog",
    "stripe",
    "slack_engineering",
    "x_engineering",
    "apple_ml",
    "spotify_engineering",
    "discord",
    "docker",
    "google_developers",
    "rust_lang",
    "golang",
    "apple_developer",
    "apple_newsroom",
    "webkit",
    "hashicorp",
    "cncf",
    "gcp",
    "worldmonitor_tech",
    # Korean tech blogs
    "kakao_tech",
    "naver_d2",
    "line_engineering",
    "toss_tech",
    "woowahan_tech",
    "daangn_tech",
    "coupang_tech",
    # AI/ML blogs
    "nvidia_ai",
    # DevOps/Platform blogs
    "gitlab",
    "vercel",
}

MIN_NEWS_COUNT = 5  # 최소 뉴스 수
MAX_NEWS_PER_CATEGORY = 5  # 카테고리당 최대 뉴스 수


# ============================================================================
# 뉴스 로드 및 필터링
# ============================================================================


def load_collected_news() -> Dict:
    """수집된 뉴스 로드"""
    news_file = DATA_DIR / "collected_news.json"
    if not news_file.exists():
        print("❌ No collected news found. Run collect_tech_news.py first.")
        sys.exit(1)

    with open(news_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_published_urls(days: int = PUBLISHED_URLS_TTL_DAYS) -> set:
    """Load URLs published in recent posts to prevent cross-day duplicates.

    Returns a set of URLs that were included in posts within the last `days` days.
    """
    if not PUBLISHED_URLS_FILE.exists():
        return set()

    try:
        with open(PUBLISHED_URLS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return set()

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    urls = set()
    for entry in data.get("entries", []):
        if entry.get("expires_at", "") > cutoff:
            urls.add(entry.get("url", ""))
    urls.discard("")
    return urls


def save_published_urls(selected_items: List[Dict], date_str: str) -> None:
    """Append selected items' URLs to the published tracker and prune expired entries."""
    existing_entries: List[Dict] = []
    if PUBLISHED_URLS_FILE.exists():
        try:
            with open(PUBLISHED_URLS_FILE, "r", encoding="utf-8") as f:
                existing_entries = json.load(f).get("entries", [])
        except (json.JSONDecodeError, OSError):
            existing_entries = []

    # Prune expired entries
    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=PUBLISHED_URLS_TTL_DAYS)
    ).isoformat()
    existing_entries = [e for e in existing_entries if e.get("expires_at", "") > cutoff]

    # Build set of already-tracked URLs to avoid duplicates in the tracker itself
    tracked_urls = {e.get("url") for e in existing_entries}

    expires_at = (
        datetime.now(timezone.utc) + timedelta(days=PUBLISHED_URLS_TTL_DAYS)
    ).isoformat()

    for item in selected_items:
        url = item.get("url", item.get("link", ""))
        if url and url not in tracked_urls:
            existing_entries.append(
                {
                    "url": url,
                    "title": item.get("title", "")[:80],
                    "published_date": date_str,
                    "expires_at": expires_at,
                }
            )
            tracked_urls.add(url)

    PUBLISHED_URLS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PUBLISHED_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "entries": existing_entries,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"  📋 Published URL tracker updated: {len(existing_entries)} entries")


def filter_published_urls(items: List[Dict], published_urls: set) -> List[Dict]:
    """Remove items whose URL was already published in recent posts."""
    if not published_urls:
        return items
    before = len(items)
    filtered = [
        item
        for item in items
        if item.get("url", item.get("link", "")) not in published_urls
    ]
    removed = before - len(filtered)
    if removed > 0:
        print(
            f"  🔄 Cross-day dedup: removed {removed} items already published in recent posts"
        )
    return filtered


def filter_and_prioritize_news(news_data: Dict, hours: int = 24) -> List[Dict]:
    """뉴스 필터링 및 우선순위 정렬 (프로그레시브 완화 포함)"""
    items = news_data.get("items", [])
    if not items:
        return []

    # collected_at 기준으로 데이터 신선도 확인
    collected_at_str = news_data.get("collected_at", "")
    data_age_hours = 0
    if collected_at_str:
        try:
            collected_at = datetime.fromisoformat(
                collected_at_str.replace("Z", "+00:00")
            )
            data_age_hours = (
                datetime.now(timezone.utc) - collected_at
            ).total_seconds() / 3600
            print(
                f"  📅 Data age: {data_age_hours:.1f}h (collected at {collected_at_str})"
            )
        except (ValueError, TypeError):
            pass

    # 데이터가 오래된 경우 시간 윈도우를 자동 확장
    effective_hours = hours + data_age_hours

    # 프로그레시브 완화: hours → hours*2 → hours*3 → 전체
    time_windows = [hours, effective_hours, hours * 2, hours * 3]

    for window in time_windows:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window)
        filtered = _filter_by_cutoff(items, cutoff)
        if len(filtered) >= MIN_NEWS_COUNT:
            if window > hours:
                print(
                    f"  ⏰ Time window relaxed: {hours}h → {window:.0f}h ({len(filtered)} items)"
                )
            break
    else:
        # 모든 윈도우에서 부족하면 전체 아이템을 날짜순 정렬 후 사용
        print(
            f"  ⚠️ All time windows insufficient. Using all {len(items)} items sorted by date."
        )
        filtered = sorted(
            items,
            key=lambda x: x.get("published", ""),
            reverse=True,
        )

    # Remove items containing blocked keywords in title/summary/content
    BLOCKED_KEYWORDS = ["openclaw"]
    before_block = len(filtered)
    filtered = [
        item
        for item in filtered
        if not any(
            kw
            in (
                item.get("title", "")
                + item.get("summary", "")
                + item.get("content", "")
            ).lower()
            for kw in BLOCKED_KEYWORDS
        )
    ]
    blocked_count = before_block - len(filtered)
    if blocked_count > 0:
        print(f"  🚫 Blocked {blocked_count} items containing excluded keywords")

    # Deprioritize items with empty summary AND empty content
    for item in filtered:
        summary = item.get("summary", "").strip()
        content_text = item.get("content", "").strip()
        if not summary and not content_text:
            item["_empty_content"] = True

    # Group related Bitcoin/crypto crash stories - deduplicate
    filtered = _deduplicate_crypto_stories(filtered)

    # 우선순위 정렬
    def get_priority(item):
        source_priority = SOURCE_PRIORITY.get(item.get("source", ""), 5)
        category_priority = CATEGORY_PRIORITY.get(item.get("category", "tech"), 5)
        # Items with empty content get deprioritized
        empty_penalty = 10 if item.get("_empty_content") else 0
        return (empty_penalty, source_priority, category_priority)

    filtered.sort(key=get_priority)
    return filtered


def _deduplicate_crypto_stories(items: List[Dict]) -> List[Dict]:
    """Group related Bitcoin/crypto crash stories and keep only the 2 most substantive"""
    crypto_keywords = ["bitcoin", "btc", "crypto", "cryptocurrency"]
    price_keywords = [
        "crash",
        "drop",
        "fall",
        "plunge",
        "dump",
        "price",
        "surge",
        "rally",
    ]

    crypto_price_items = []
    other_items = []

    for item in items:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        is_crypto = any(kw in text for kw in crypto_keywords)
        is_price = any(kw in text for kw in price_keywords)
        category = item.get("category", "")

        if category == "blockchain" and is_crypto and is_price:
            crypto_price_items.append(item)
        else:
            other_items.append(item)

    if len(crypto_price_items) >= 3:
        # Keep the 2 most substantive (longest summary + content)
        crypto_price_items.sort(
            key=lambda x: len(x.get("summary", "")) + len(x.get("content", "")),
            reverse=True,
        )
        other_items.extend(crypto_price_items[:2])
    else:
        other_items.extend(crypto_price_items)

    return other_items


def _filter_by_cutoff(items: List[Dict], cutoff: datetime) -> List[Dict]:
    """cutoff 시간 기준으로 뉴스 필터링"""
    filtered = []
    for item in items:
        try:
            pub_date = datetime.fromisoformat(
                item.get("published", "").replace("Z", "+00:00")
            )
            if pub_date >= cutoff:
                filtered.append(item)
        except (ValueError, TypeError):
            # 날짜 파싱 실패 시 포함
            filtered.append(item)
    return filtered


def categorize_news(items: List[Dict]) -> Dict[str, List[Dict]]:
    """뉴스를 카테고리별로 분류 - 콘텐츠 기반 재분류 포함"""
    categorized = defaultdict(list)

    for item in items:
        category = item.get("category", "tech")

        # Content-based category validation
        title_lower = (item.get("title", "") or "").lower()
        summary_lower = (item.get("summary", "") or "").lower()
        combined = f"{title_lower} {summary_lower}"

        # Override blockchain category if content is actually about AI/security
        if category == "blockchain":
            ai_security_keywords = [
                "anthropic",
                "openai",
                "pentagon",
                "military",
                "claude ai",
                "gpt",
                "llm",
                "machine learning",
            ]
            if any(kw in combined for kw in ai_security_keywords):
                security_keywords = [
                    "pentagon",
                    "military",
                    "supply chain risk",
                    "vulnerability",
                    "exploit",
                    "breach",
                ]
                if any(kw in combined for kw in security_keywords):
                    category = "security"
                else:
                    category = "ai"

        # Cross-category security reclassification: if a non-security item
        # clearly discusses vulnerabilities/exploits, move it to security
        if category not in ("security", "devsecops"):
            security_indicators = [
                "vulnerability",
                "exploit",
                "cve-",
                "취약점",
                "malware",
                "악성코드",
                "ransomware",
                "랜섬웨어",
                "attack",
                "공격",
                "breach",
                "침해",
            ]
            security_score = sum(1 for kw in security_indicators if kw in combined)
            if security_score >= 2:  # At least 2 security keywords
                category = "security"

        # security, devsecops는 security로 통합
        if category in ("security", "devsecops"):
            category = "security"
        elif category == "kubernetes":
            category = "devops"

        # Update item's category for downstream use
        item["category"] = category

        if len(categorized[category]) < MAX_NEWS_PER_CATEGORY:
            # Filter out stale items for non-security categories
            if category not in ("security", "devsecops"):
                # Check URL for old year indicators (e.g., /2023/ or /2024/)
                url = item.get("url", "")
                current_year = datetime.now(timezone.utc).year
                url_year_match = re.search(r"/(\d{4})/", url)
                if url_year_match:
                    url_year = int(url_year_match.group(1))
                    if 2000 <= url_year < current_year - 1:
                        continue
                # Also check published date
                try:
                    pub_date = datetime.fromisoformat(
                        item.get("published", "").replace("Z", "+00:00")
                    )
                    if (datetime.now(timezone.utc) - pub_date).days > 90:
                        continue
                except (ValueError, TypeError):
                    pass
            categorized[category].append(item)

    return dict(categorized)


def select_top_news(
    categorized: Dict[str, List[Dict]], max_total: int = 15
) -> List[Dict]:
    """상위 뉴스 선택"""
    selected = []

    # 카테고리 우선순위대로 선택
    for category in sorted(
        categorized.keys(), key=lambda c: CATEGORY_PRIORITY.get(c, 5)
    ):
        for item in categorized[category]:
            if len(selected) >= max_total:
                break
            selected.append(item)

    return selected


# ============================================================================
# AI 강화 시스템 (Gemini API → Gemini CLI → DeepSeek API 폴백 체인)
# ============================================================================

_GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
_CLAUDE_API_KEY: str = os.getenv("CLAUDE_API_KEY", "")
_OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
_GEMINI_AVAILABLE: Optional[bool] = None  # Cached CLI availability check
_GEMINI_CONSECUTIVE_FAILURES: int = 0  # Circuit breaker counter
_GEMINI_CIRCUIT_OPEN: bool = False  # Circuit breaker state
_AI_MODE: str = os.getenv("AUTO_PUBLISH_USE_AI", "auto").lower()
_GEMINI_CALL_TIMEOUT: int = max(8, int(os.getenv("AUTO_PUBLISH_GEMINI_TIMEOUT", "15")))
_GEMINI_MAX_RETRIES: int = max(1, int(os.getenv("AUTO_PUBLISH_GEMINI_RETRIES", "1")))
_CLAUDE_MODEL: str = os.getenv("AUTO_PUBLISH_CLAUDE_MODEL", "claude-3-5-sonnet-latest")
_OPENAI_Codex_MODEL: str = os.getenv("AUTO_PUBLISH_OPENAI_CODEX_MODEL", "gpt-5.3-codex")
_OPENAI_GPT54_MODEL: str = os.getenv("AUTO_PUBLISH_OPENAI_GPT54_MODEL", "gpt-5.4")


def _allow_gemini() -> bool:
    return _AI_MODE in {"auto", "gemini"}


def _allow_deepseek() -> bool:
    return _AI_MODE in {"auto", "deepseek"}


def check_gemini_available() -> bool:
    """Gemini 사용 가능 여부 확인 (API 키 또는 CLI)"""
    global _GEMINI_AVAILABLE, _GEMINI_CIRCUIT_OPEN
    if not _allow_gemini():
        return False
    if _GEMINI_CIRCUIT_OPEN:
        return False
    # API key takes priority (much faster than CLI)
    if _GEMINI_API_KEY:
        return True
    if _GEMINI_AVAILABLE is not None:
        return _GEMINI_AVAILABLE
    try:
        result = subprocess.run(["gemini", "--version"], capture_output=True, timeout=5)
        _GEMINI_AVAILABLE = result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        _GEMINI_AVAILABLE = False
    return _GEMINI_AVAILABLE


def _gemini_api_call(prompt: str, timeout: int = 20) -> str:
    """Direct Gemini REST API call (fast, no process overhead).

    Uses GEMINI_API_KEY env var. Returns response text or empty string.
    """
    if not _GEMINI_API_KEY:
        return ""

    try:
        import requests

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={_GEMINI_API_KEY}",
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=timeout,
        )
        if response.status_code == 200:
            data = response.json()
            text = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )
            return text.strip()
        else:
            logging.warning(
                f"Gemini API status {response.status_code}: {response.text[:100]}"
            )
    except ImportError:
        logging.debug("requests library not available for Gemini API")
    except Exception as e:
        logging.warning(f"Gemini API error: {e}")

    return ""


def _gemini_call(prompt: str, timeout: int = 35) -> str:
    """Gemini call with CLI-first strategy and circuit breaker.

    Priority: CLI (free OAuth) → REST API fallback (API key) → empty string.
    """
    global _GEMINI_CONSECUTIVE_FAILURES, _GEMINI_CIRCUIT_OPEN

    if _GEMINI_CIRCUIT_OPEN:
        return ""

    # 1. Try CLI first (free OAuth, no API key cost)
    if _GEMINI_AVAILABLE is not False:
        try:
            proc = subprocess.run(
                ["gemini", "-p", prompt],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if proc.returncode == 0 and len(proc.stdout.strip()) > 20:
                _GEMINI_CONSECUTIVE_FAILURES = 0
                return proc.stdout.strip()
            _GEMINI_CONSECUTIVE_FAILURES += 1
        except subprocess.TimeoutExpired:
            _GEMINI_CONSECUTIVE_FAILURES += 1
            logging.warning(f"Gemini CLI timeout ({timeout}s)")
        except (subprocess.SubprocessError, OSError) as e:
            _GEMINI_CONSECUTIVE_FAILURES += 1
            logging.warning(f"Gemini CLI error: {e}")

    # 2. Fallback to REST API (fast but uses API key quota)
    if _GEMINI_API_KEY and _GEMINI_CONSECUTIVE_FAILURES > 0:
        api_timeout = min(timeout, 20)
        result = _gemini_api_call(prompt, timeout=api_timeout)
        if result and len(result) > 20:
            _GEMINI_CONSECUTIVE_FAILURES = 0
            return result
        _GEMINI_CONSECUTIVE_FAILURES += 1

    if not _GEMINI_AVAILABLE and not _GEMINI_API_KEY:
        _GEMINI_CONSECUTIVE_FAILURES += 1

    # Circuit breaker: after 3 consecutive failures, skip Gemini entirely
    if _GEMINI_CONSECUTIVE_FAILURES >= 3:
        _GEMINI_CIRCUIT_OPEN = True
        logging.warning(
            f"Gemini circuit breaker OPEN after {_GEMINI_CONSECUTIVE_FAILURES} "
            "consecutive failures - switching to DeepSeek/template for remaining items"
        )
    return ""


def enhance_with_gemini(item: Dict, max_retries: Optional[int] = None) -> str:
    """Gemini CLI로 뉴스 심층 분석 (무료)

    Uses a compact prompt to reduce latency and timeout risk.
    Circuit breaker skips Gemini after 3 consecutive failures.
    """
    title = item.get("title", "")
    summary = item.get("summary", "")[:300]  # Truncate to reduce prompt size
    url = item.get("url", "")

    if not title:
        return ""

    # Compact prompt - shorter = faster response
    prompt = (
        f"DevSecOps 관점에서 다음 뉴스를 한국어 분석 (500자 이내, 마크다운):\n"
        f"제목: {title}\n요약: {summary}\n출처: {url}\n\n"
        f"형식: ### 제목\n1. **기술 배경** (2-3문장)\n"
        f"2. **실무 영향** (구체적 시스템/도구)\n"
        f"3. **체크리스트** (- [ ] 3-4개)\n"
        f"4. **MITRE ATT&CK** (해당 시)"
    )

    retries = max_retries if max_retries is not None else _GEMINI_MAX_RETRIES

    for attempt in range(retries):
        content = _gemini_call(prompt, timeout=_GEMINI_CALL_TIMEOUT)
        if content and len(content) > 100:
            logging.info(f"Gemini enhanced: {title[:50]}...")
            return content

        if _GEMINI_CIRCUIT_OPEN:
            break  # Don't retry if circuit is open

        if attempt < retries - 1:
            import time

            time.sleep(2)  # Brief pause before retry

    logging.info(f"Gemini enhancement failed, falling back: {title[:50]}")
    return ""


def enhance_with_deepseek(item: Dict) -> str:
    """DeepSeek API 폴백 (off-peak 할인 활용)

    Args:
        item: 뉴스 아이템 딕셔너리

    Returns:
        DeepSeek API 생성 분석 텍스트 (실패 시 빈 문자열)
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        logging.debug("DeepSeek API key not found, skipping")
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")
    url = item.get("url", "")

    if not title:
        return ""

    try:
        # DeepSeek API 호출 준비
        import requests

        prompt = f"""다음 보안/기술 뉴스를 DevSecOps 실무자 관점에서 분석:
제목: {title}
요약: {summary}
출처: {url}

다음 형식으로 한국어로 작성 (500-800자):
1. 기술적 배경 및 위협 분석
2. 실무 영향 분석
3. 대응 체크리스트 (- [ ] 형식, 3-5개)

마크다운 형식으로 작성."""

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000,
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            if len(content) > 100:
                logging.info(f"DeepSeek API enhanced: {title[:50]}...")
                return content.strip()
        else:
            logging.warning(f"DeepSeek API returned status {response.status_code}")

    except ImportError:
        logging.warning("requests library not available for DeepSeek API")
    except Exception as e:
        logging.warning(f"DeepSeek API error: {e}")

    return ""


def enhance_with_claude(item: Dict) -> str:
    api_key = _CLAUDE_API_KEY
    if not api_key:
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")[:500]
    url = item.get("url", "")
    if not title:
        return ""

    prompt = f"""다음 보안/기술 뉴스를 DevSecOps 실무자 관점에서 분석:
제목: {title}
요약: {summary}
출처: {url}

다음 형식으로 한국어로 작성 (500-800자):
1. 기술적 배경 및 위협 분석
2. 실무 영향 분석
3. 대응 체크리스트 (- [ ] 형식, 3-5개)
4. 우선순위(P0/P1/P2) 제안

마크다운 형식으로 작성."""

    try:
        import requests

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": _CLAUDE_MODEL,
                "max_tokens": 1200,
                "temperature": 0.4,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            parts = data.get("content", [])
            text_parts = [
                part.get("text", "") for part in parts if part.get("type") == "text"
            ]
            content = "\n".join(text_parts).strip()
            if len(content) > 100:
                logging.info(f"Claude enhanced: {title[:50]}...")
                return content
        else:
            logging.warning(f"Claude API returned status {response.status_code}")
    except ImportError:
        logging.warning("requests library not available for Claude API")
    except Exception as e:
        logging.warning(f"Claude API error: {e}")

    return ""


def enhance_with_openai_codex_medium(item: Dict) -> str:
    api_key = _OPENAI_API_KEY
    if not api_key:
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")[:500]
    url = item.get("url", "")
    if not title:
        return ""

    prompt = f"""다음 보안/기술 뉴스를 DevSecOps 실무자 관점에서 분석:
제목: {title}
요약: {summary}
출처: {url}

다음 형식으로 한국어로 작성 (500-800자):
1. 기술적 배경 및 위협 분석
2. 실무 영향 분석
3. 대응 체크리스트 (- [ ] 형식, 3-5개)
4. 우선순위(P0/P1/P2) 제안

마크다운 형식으로 작성."""

    try:
        import requests

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _OPENAI_Codex_MODEL,
                "temperature": 0.4,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if len(content) > 100:
                logging.info(f"OpenAI Codex enhanced: {title[:50]}...")
                return content
        else:
            logging.warning(f"OpenAI API returned status {response.status_code}")
    except ImportError:
        logging.warning("requests library not available for OpenAI API")
    except Exception as e:
        logging.warning(f"OpenAI API error: {e}")

    return ""


def enhance_with_openai_gpt54(item: Dict) -> str:
    api_key = _OPENAI_API_KEY
    if not api_key:
        return ""

    title = item.get("title", "")
    summary = item.get("summary", "")[:500]
    url = item.get("url", "")
    if not title:
        return ""

    prompt = f"""다음 보안/기술 뉴스를 DevSecOps 실무자 관점에서 분석:
제목: {title}
요약: {summary}
출처: {url}

다음 형식으로 한국어로 작성 (500-800자):
1. 기술적 배경 및 위협 분석
2. 실무 영향 분석
3. 대응 체크리스트 (- [ ] 형식, 3-5개)
4. 우선순위(P0/P1/P2) 제안

마크다운 형식으로 작성."""

    try:
        import requests

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _OPENAI_GPT54_MODEL,
                "temperature": 0.3,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=20,
        )

        if response.status_code == 200:
            data = response.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            if len(content) > 100:
                logging.info(f"OpenAI GPT-5.4 enhanced: {title[:50]}...")
                return content
        else:
            logging.warning(
                f"OpenAI GPT-5.4 API returned status {response.status_code}"
            )
    except ImportError:
        logging.warning("requests library not available for OpenAI API")
    except Exception as e:
        logging.warning(f"OpenAI GPT-5.4 API error: {e}")

    return ""


def enhance_content_with_fallback(item: Dict) -> str:
    """3단계 폴백 체인: Gemini CLI → DeepSeek API → Template

    Uses circuit breaker: if Gemini fails 3 times consecutively,
    all remaining items go straight to DeepSeek/template.
    """
    title_short = item.get("title", "")[:50]

    if _AI_MODE == "none":
        title_short = item.get("title", "")[:50]
        logging.info(f"✓ Template fallback (AI disabled): {title_short}")
        return ""

    if _AI_MODE in {"auto", "claude"}:
        content = enhance_with_claude(item)
        if content:
            logging.info(f"✓ Claude: {title_short}")
            return content

    # 1순위: Gemini CLI (무료) - skipped if circuit breaker is open
    if _AI_MODE in {"auto", "gemini"} and check_gemini_available():
        content = enhance_with_gemini(item)
        if content:
            logging.info(f"✓ Gemini CLI: {title_short}")
            return content

    if _AI_MODE in {"auto", "gpt-5.4"}:
        content = enhance_with_openai_gpt54(item)
        if content:
            logging.info(f"✓ OpenAI GPT-5.4: {title_short}")
            return content

    if _AI_MODE in {"auto", "codex-medium"}:
        content = enhance_with_openai_codex_medium(item)
        if content:
            logging.info(f"✓ OpenAI Codex: {title_short}")
            return content

    # 2순위: DeepSeek API (off-peak 할인)
    content = ""
    if _AI_MODE in {"auto", "gemini", "deepseek"}:
        content = enhance_with_deepseek(item)
    if content:
        logging.info(f"✓ DeepSeek API: {title_short}")
        return content

    # 3순위: 기본 템플릿
    logging.info(f"✓ Template fallback: {title_short}")
    return ""


# ============================================================================
# Executive Summary 강화 도구
# ============================================================================


def generate_risk_scorecard(
    news_items: List[Dict], report_date: Optional[datetime] = None
) -> str:
    """위험 스코어카드 ASCII art 생성

    Args:
        news_items: 뉴스 아이템 리스트

    Returns:
        위험 스코어카드 문자열
    """
    report_date = report_date or datetime.now(timezone.utc)
    scorecard = f"""```
+================================================================+
|          {report_date.strftime("%Y-%m-%d")} 주간 보안 위험 스코어카드                      |
+================================================================+
|                                                                |
|  항목                    위험도   점수    조치 시급도             |
|  ----------------------------------------------------------   |
"""

    # Critical/High 뉴스만 스코어카드에 포함
    critical_news = [
        n for n in news_items if _determine_severity(n) in ["Critical", "High"]
    ]

    for news in critical_news[:5]:  # 최대 5개
        title = news.get("title", "")[:30]
        severity = _determine_severity(news)
        score = 9 if severity == "Critical" else 7
        bars = "█" * score + "░" * (10 - score)
        priority = "[즉시]" if severity == "Critical" else "[7일 이내]"

        scorecard += f"|  {title:<24} {bars}  {score}/10   {priority:<15}     |\n"

    # 종합 위험 수준
    if critical_news:
        avg_score = sum(
            9 if _determine_severity(n) == "Critical" else 7 for n in critical_news
        ) / len(critical_news)
    else:
        avg_score = 5

    level = "HIGH" if avg_score >= 7 else "MEDIUM" if avg_score >= 5 else "LOW"
    bars = "█" * int(avg_score) + "░" * (10 - int(avg_score))

    scorecard += f"""|  ----------------------------------------------------------   |
|  종합 위험 수준: {bars} {level} ({avg_score:.1f}/10)                         |
|                                                                |
+================================================================+
```
"""
    return scorecard


def extract_cve_id(title: str, summary: str) -> Optional[str]:
    """CVE ID 추출

    Args:
        title: 제목
        summary: 요약

    Returns:
        CVE ID (없으면 None)
    """
    pattern = r"CVE-\d{4}-\d{4,7}"
    for text in [title, summary]:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def generate_mitre_mapping(cve_id: str, item: Dict) -> str:
    """MITRE ATT&CK 매핑 생성

    Args:
        cve_id: CVE ID
        item: 뉴스 아이템 (컨텍스트용)

    Returns:
        MITRE 매핑 YAML 문자열
    """
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()

    # 텍스트 기반 MITRE 매핑
    techniques = []

    if any(kw in text for kw in ["rce", "remote code execution", "exploit"]):
        techniques.append("T1203  # Exploitation for Client Execution")

    if any(kw in text for kw in ["authentication", "credential", "bypass"]):
        techniques.append("T1078  # Valid Accounts")

    if any(kw in text for kw in ["injection", "sql", "xss"]):
        techniques.append("T1190  # Exploit Public-Facing Application")

    if any(kw in text for kw in ["privilege", "권한 상승"]):
        techniques.append("T1068  # Exploitation for Privilege Escalation")

    if not techniques:
        techniques.append("T1190  # Exploit Public-Facing Application")

    techniques_yaml = "\n    - ".join(techniques)

    return f"""
#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - {techniques_yaml}
```
"""


# ============================================================================
# 포스트 생성
# ============================================================================


def _extract_meaningful_topics(news_items: List[Dict], mode: str = "security") -> str:
    if mode == "tech-blog":
        category_labels = {
            "ai": "AI",
            "cloud": "클라우드",
            "devops": "DevOps",
            "tech": "기술 동향",
            "security": "보안",
            "blockchain": "블록체인",
        }
        category_weights = {
            "ai": 3,
            "cloud": 3,
            "devops": 3,
            "security": 2,
            "blockchain": 2,
            "tech": 1,
        }
        source_profiles = [
            (r"OpenAI|Anthropic|Google AI|DeepMind|Hugging Face|NVIDIA AI", "AI", 3),
            (r"Docker|Kubernetes|Red Hat|HashiCorp|Vercel", "DevOps", 3),
            (r"AWS|Google Cloud|Cloudflare|Azure", "클라우드", 3),
            (r"GitHub|GitLab", "개발 플랫폼", 2),
            (r"GeekNews|Hacker News", "기술 동향", 1),
        ]
        topic_patterns = [
            (r"\b(AI Agent|Agentic AI)\b", "AI 에이전트"),
            (r"\b(Claude Code|Cursor|Copilot|ChatGPT|Gemini|LLM)\b", "AI 개발도구"),
            (r"\b(Open Source|Open-Source|OSS)\b", "오픈소스"),
            (r"\b(Kubernetes|K8s)\b", "쿠버네티스"),
            (r"\b(Docker|Container)\b", "컨테이너"),
            (r"\b(Rust|Golang|Go\s+\d|TypeScript)\b", "개발 언어"),
            (r"\b(React|Next\.?js|Vue|Svelte)\b", "프론트엔드"),
            (r"\b(AWS|Azure|GCP|Cloud)\b", "클라우드"),
            (r"\b(GitHub|GitLab)\b", "개발 플랫폼"),
            (r"\b(Apple|Google|Microsoft|Meta|Tesla|Spotify)\b", "빅테크 전략"),
            (r"\b(WebAssembly|WASM|gRPC|GraphQL)\b", "플랫폼 기술"),
            (r"\b(DevOps|CI/CD|Platform Engineering)\b", "플랫폼 엔지니어링"),
        ]
        fallback_topics = ["기술 동향", "DevOps"]
    else:
        category_labels = {
            "security": "보안 위협",
            "devsecops": "DevSecOps",
            "ai": "AI",
            "cloud": "클라우드 보안",
            "devops": "DevOps",
            "blockchain": "블록체인",
            "tech": "기술 동향",
        }
        category_weights = {
            "security": 4,
            "cloud": 3,
            "blockchain": 3,
            "ai": 2,
            "devsecops": 2,
            "devops": 2,
            "tech": 1,
        }
        source_profiles = [
            (
                r"The Hacker News|BleepingComputer|Dark Reading|Krebs|SANS ISC",
                "보안 위협",
                4,
            ),
            (
                r"Cloudflare|AWS|Google Cloud|Microsoft Security|Azure",
                "클라우드 보안",
                3,
            ),
            (r"Cointelegraph|CoinDesk|Bitcoin Magazine|The Block", "블록체인", 3),
            (r"OpenAI|Anthropic|NVIDIA AI|Meta Engineering", "AI", 2),
            (r"GeekNews|Hacker News", "기술 동향", 1),
        ]
        topic_patterns = [
            (r"(CVE-\d{4}-\d+)", "CVE"),
            (r"\b(ransomware|랜섬웨어)\b", "랜섬웨어"),
            (r"\b(zero-day|0-day|제로데이)\b", "제로데이"),
            (
                r"\b(Fortinet|Cisco|Palo Alto|CrowdStrike|SonicWall|Ivanti)\b",
                "보안 벤더",
            ),
            (r"\b(Chrome|Firefox|Windows|Linux|macOS|Android|iOS)\b", "플랫폼 보안"),
            (r"\b(APT\d+|Lazarus|APT28|APT29|Kimsuky)\b", "APT"),
            (r"\b(phishing|피싱)\b", "피싱"),
            (r"\b(supply chain|공급망)\b", "공급망 보안"),
            (r"\b(botnet|봇넷)\b", "봇넷"),
            (r"\b(malware|악성코드)\b", "악성코드"),
            (r"\b(authentication|MFA|SSO|인증)\b", "계정 보호"),
            (r"\b(RCE|remote code execution)\b", "원격 코드 실행"),
            (r"\b(AWS|Azure|GCP|Cloud)\b", "클라우드 보안"),
            (r"\b(Kubernetes|K8s|Docker)\b", "컨테이너 보안"),
            (r"\b(Bitcoin|Ethereum|Crypto|Web3|Blockchain|DeFi)\b", "블록체인"),
            (r"\b(AI Agent|Agentic AI|OpenAI|Gemini|LLM|AI)\b", "AI"),
        ]
        fallback_topics = ["주요 보안 이슈", "기술 동향"]

    scores: Counter[str] = Counter()
    first_seen: Dict[str, int] = {}

    for idx, item in enumerate(news_items):
        category = str(item.get("category", "tech")).lower()
        category_label = category_labels.get(category)
        if category_label:
            scores[category_label] += category_weights.get(category, 1)
            first_seen.setdefault(category_label, idx)

        source_name = str(item.get("source_name", item.get("source", "")))
        for pattern, label, weight in source_profiles:
            if re.search(pattern, source_name, re.IGNORECASE):
                scores[label] += weight
                first_seen.setdefault(label, idx)

        text = f"{item.get('title', '')} {item.get('summary', '')}"
        for pattern, label in topic_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                scores[label] += 2
                first_seen.setdefault(label, idx)

    ranked_topics = [
        topic
        for topic, _ in sorted(
            scores.items(), key=lambda item: (-item[1], first_seen.get(item[0], 999))
        )
    ]

    if not ranked_topics:
        ranked_topics = fallback_topics

    if len(ranked_topics) >= 3 and ranked_topics[0] != "기술 동향":
        ranked_topics = [t for t in ranked_topics if t != "기술 동향"] + [
            t for t in ranked_topics if t == "기술 동향"
        ]

    title_keywords = ", ".join(ranked_topics[:3])
    if len(title_keywords) > 80:
        title_keywords = title_keywords[:80].rstrip(" ,.")
    return title_keywords


def _extract_digest_title_phrases(
    news_items: List[Dict], mode: str = "security", limit: int = 3
) -> List[str]:
    """Build a more specific digest title from top headlines."""
    phrases: List[str] = []
    seen: set[str] = set()

    for item in news_items[:8]:
        raw_title = _korean_display_title(item, max_len=72)
        candidate = re.split(r"\s*[|:]+\s*|\s+-\s+", raw_title)[0].strip()
        candidate = re.sub(r"\s+", " ", candidate).strip(" ,.")

        if len(candidate) < 8:
            candidate = raw_title.strip(" ,.")
        if len(candidate) > 26:
            candidate = candidate[:26].rsplit(" ", 1)[0].rstrip(" ,.")
        if not candidate:
            continue

        dedupe_key = candidate.lower()
        if dedupe_key in seen:
            continue

        seen.add(dedupe_key)
        phrases.append(candidate)
        if len(phrases) >= limit:
            break

    if mode == "tech-blog":
        generic = {"기술 동향", "개발 플랫폼", "빅테크 전략"}
    else:
        generic = {"보안 위협", "클라우드 보안", "AI", "기술 동향"}

    phrases = [p for p in phrases if p not in generic]
    return phrases[:limit]


def _extract_digest_title_labels(
    news_items: List[Dict], mode: str = "security"
) -> List[str]:
    """Fallback title labels built from high-signal keywords."""
    label_map = [
        (r"zero-day|0-day|제로데이|cve-", "제로데이"),
        (r"ransomware|랜섬웨어", "랜섬웨어"),
        (r"malware|악성코드", "악성코드"),
        (r"byovd|driver|edr", "BYOVD EDR"),
        (r"dns|exfil|data leak|유출", "DNS 유출"),
        (r"telnet", "Telnetd"),
        (r"cisco|fmc", "Cisco FMC"),
        (r"dprk|north korea|북한", "북한 위협"),
        (r"ai agent|agentic|llm|model", "AI 에이전트"),
        (r"kubernetes|k8s|gke|cluster", "쿠버네티스"),
        (r"cloud|aws|azure|gcp", "클라우드"),
        (r"patch|update", "패치"),
    ]
    labels: List[str] = []
    seen: set[str] = set()

    for item in news_items[:8]:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        for pattern, label in label_map:
            if re.search(pattern, text) and label not in seen:
                seen.add(label)
                labels.append(label)
                if len(labels) >= 3:
                    return labels

    fallback = _extract_meaningful_topics(news_items, mode=mode).split(", ")
    for label in fallback:
        if label not in seen:
            labels.append(label)
        if len(labels) >= 3:
            break

    normalized_labels: List[str] = []
    for label in labels:
        if label == "AI" and any(existing.startswith("AI ") for existing in labels):
            continue
        if label == "클라우드" and any("쿠버네티스" in existing for existing in labels):
            continue
        if label not in normalized_labels:
            normalized_labels.append(label)
    return normalized_labels[:3]


def _build_digest_title(news_items: List[Dict], mode: str = "security") -> str:
    """Prefer specific headline-driven titles over generic topic buckets."""
    headline_phrases = _extract_digest_title_phrases(news_items, mode=mode, limit=3)
    weak_english_starts = (
        "how ",
        "when ",
        "why ",
        "what ",
        "inside ",
        "introducing ",
        "announcing ",
        "from ",
    )

    weak_phrase_count = sum(
        1 for p in headline_phrases if p.lower().startswith(weak_english_starts)
    )
    headline_joined = " ".join(headline_phrases)
    has_korean = bool(re.search(r"[가-힣]", headline_joined))
    has_markdown_noise = any("*" in p or "#" in p for p in headline_phrases)

    if headline_phrases and not (
        has_markdown_noise or (weak_phrase_count >= 1 and not has_korean)
    ):
        title = ", ".join(headline_phrases)
        if len(title) <= 80:
            return title

    label_title = ", ".join(_extract_digest_title_labels(news_items, mode=mode))
    if label_title:
        return label_title[:80].rstrip(" ,.")

    return _extract_meaningful_topics(news_items, mode=mode)


def _generate_executive_and_risk_sections(
    news_items: List[Dict], mode: str = "security"
) -> str:
    critical_count = 0
    high_count = 0
    medium_count = 0
    critical_titles = []
    high_titles = []

    for item in news_items:
        severity = _determine_severity(item)
        title = _korean_display_title(item, max_len=35)
        if severity == "Critical":
            critical_count += 1
            critical_titles.append(title)
        elif severity == "High":
            high_count += 1
            high_titles.append(title)
        else:
            medium_count += 1

    if critical_count > 0 or high_count >= 3:
        overall = "High"
    elif high_count > 0 or medium_count >= 5:
        overall = "Medium"
    else:
        overall = "Low"

    severity_rank = {"Critical": 0, "High": 1, "Medium": 2}
    ranked_items = sorted(
        news_items,
        key=lambda item: (
            severity_rank.get(_determine_severity(item), 3),
            CATEGORY_PRIORITY.get(str(item.get("category", "tech")).lower(), 99),
        ),
    )
    top_items = ranked_items[:3]
    text_blob = " ".join(
        f"{item.get('title', '')} {item.get('summary', '')}" for item in news_items
    ).lower()

    if mode == "tech-blog":
        briefing_lines = []
        for item in top_items[:2]:
            title = _korean_display_title(item, max_len=54)
            action = _generate_contextual_action_point(item)
            briefing_lines.append(f"- {title} 이슈는 {action}")
        if len(briefing_lines) < 2:
            briefing_lines.extend(
                [
                    "- 이번 주기는 기술 도입 속도보다 표준화된 검증 흐름 설계가 더 중요합니다.",
                    "- 배포 전 검증, 권한 통제, 장애 복구 연습을 같은 운영 주기로 관리해야 합니다.",
                ][len(briefing_lines) :]
            )

        rows = [
            "| 영역 | 현재 위험도 | 즉시 조치 |",
            "|------|-------------|-----------|",
            f"| 배포 안정성 | {overall} | 릴리즈 체크리스트와 롤백 절차 점검 |",
            "| 개발 생산성 | Medium | 핵심 도구 표준화 및 팀 가이드 업데이트 |",
        ]
        for item in top_items:
            area = {
                "ai": "AI 자동화",
                "cloud": "플랫폼 운영",
                "devops": "배포 안정성",
                "kubernetes": "클러스터 운영",
            }.get(str(item.get("category", "tech")).lower(), "기술 운영")
            rows.append(
                f"| {area} | {_determine_severity(item)} | {_korean_display_title(item, max_len=34)} 점검 |"
            )
    else:
        briefing_lines = []
        if critical_titles:
            briefing_lines.append(
                f"- **긴급 대응 필요**: {', '.join(critical_titles[:2])} 등 Critical 등급 위협 {critical_count}건이 확인되었습니다."
            )
        if high_titles:
            briefing_lines.append(
                f"- **주요 모니터링 대상**: {', '.join(high_titles[:3])} 등 High 등급 위협 {high_count}건에 대한 탐지 강화가 필요합니다."
            )
        if any(
            kw in text_blob for kw in ["ransomware", "랜섬웨어", "encryption", "암호화"]
        ):
            briefing_lines.append(
                "- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다."
            )
        elif any(kw in text_blob for kw in ["zero-day", "제로데이", "0-day"]):
            briefing_lines.append(
                "- 제로데이 취약점이 보고되었으며, 임시 완화 조치 적용과 벤더 패치 일정 확인이 시급합니다."
            )
        elif any(kw in text_blob for kw in ["supply chain", "공급망"]):
            briefing_lines.append(
                "- 공급망 보안 위협이 확인되었으며, 서드파티 의존성 검토와 SBOM 업데이트를 권고합니다."
            )
        if not briefing_lines:
            briefing_lines = [
                "- 이번 주기는 취약점 대응과 탐지 체계 운영이 동시에 요구됩니다.",
                "- 노출 자산 우선순위 기반의 패치와 룰 업데이트가 가장 높은 개선 효과를 제공합니다.",
            ]

        candidate_rows = [
            (
                "위협 대응",
                f"| 위협 대응 | {overall} | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |",
            ),
            (
                "탐지/모니터링",
                "| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |",
            ),
        ]
        if any(
            kw in text_blob
            for kw in ["cve", "취약점", "vulnerability", "patch", "패치"]
        ):
            cve_level = "Critical" if critical_count > 0 else "High"
            candidate_rows.append(
                (
                    "취약점 관리",
                    f"| 취약점 관리 | {cve_level} | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |",
                )
            )
        if any(
            kw in text_blob
            for kw in ["cloud", "aws", "gcp", "azure", "kubernetes", "k8s", "iam"]
        ):
            candidate_rows.append(
                (
                    "클라우드 보안",
                    "| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |",
                )
            )
        if any(
            kw in text_blob for kw in ["ai", "llm", "agent", "ml", "prompt injection"]
        ):
            candidate_rows.append(
                (
                    "AI/ML 보안",
                    "| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |",
                )
            )
        if any(
            kw in text_blob for kw in ["ransomware", "랜섬웨어", "encryption", "암호화"]
        ):
            candidate_rows.append(
                (
                    "운영 복원력",
                    "| 운영 복원력 | Medium | 백업/복구 및 사고 대응 절차 리허설 |",
                )
            )

        ordered_labels = [
            "위협 대응",
            "탐지/모니터링",
            "취약점 관리",
            "클라우드 보안",
            "AI/ML 보안",
            "운영 복원력",
        ]
        row_map = {label: row for label, row in candidate_rows}
        selected_rows = [
            row_map[label] for label in ordered_labels if label in row_map
        ][:4]
        rows = [
            "| 영역 | 현재 위험도 | 즉시 조치 |",
            "|------|-------------|-----------|",
            *selected_rows,
        ]

    briefing = "\n".join(briefing_lines)

    return (
        "## 경영진 브리핑\n\n"
        f"{briefing}\n\n"
        "## 위험 스코어카드\n\n" + "\n".join(rows) + "\n\n"
    )


def _run_post_quality_gate(post_path: Path, target: int = 80) -> None:
    try:
        from upgrade_digest_post_quality import process_file as _upgrade_post
        from validate_post_quality import validate_post as _validate_post
    except Exception as e:
        logging.debug(f"quality gate import skipped: {e}")
        return

    first = _validate_post(post_path)
    first_score = first.get("total", 0)
    score_before = first_score if isinstance(first_score, int) else 0

    if score_before >= target:
        logging.info(f"Post quality score {score_before}/100 (target {target})")
        return

    upgraded = _upgrade_post(post_path)
    if not upgraded:
        logging.warning(
            f"Post quality score {score_before}/100 below target {target} (no auto-upgrade applied)"
        )
        return

    second = _validate_post(post_path)
    second_score = second.get("total", 0)
    score_after = second_score if isinstance(second_score, int) else score_before
    logging.info(
        f"Post quality auto-upgrade: {score_before}/100 -> {score_after}/100 (target {target})"
    )


def generate_post_content(
    news_items: List[Dict],
    categorized: Dict[str, List[Dict]],
    date: datetime,
    topics_slug: str = "",
) -> str:
    """고품질 포스트 컨텐츠 생성"""

    date_str = date.strftime("%Y년 %m월 %d일")
    date_file = date.strftime("%Y-%m-%d")
    image_filename = (
        f"{date_file}-Tech_Security_Weekly_Digest_{topics_slug}.svg"
        if topics_slug
        else f"{date_file}-Tech_Security_Weekly_Digest.svg"
    )

    stats = {cat: len(items) for cat, items in categorized.items()}
    total = sum(stats.values())

    # 핵심 뉴스 추출
    security_news = categorized.get("security", [])[:3]
    ai_news = categorized.get("ai", [])[:3]
    cloud_news = categorized.get("cloud", [])[:3]
    devops_news = categorized.get("devops", [])[:3]
    blockchain_news = categorized.get("blockchain", [])[:3]
    tech_news = categorized.get("tech", [])[:3]

    # 핵심 하이라이트 생성
    highlights = []
    for item in (security_news + cloud_news)[:4]:
        source = item.get("source_name", item.get("source", "Unknown"))
        title = _korean_display_title(item)
        if len(title) > 60:
            title = title[:60].rsplit(" ", 1)[0].rstrip(" ,.")
        source = html.escape(source)
        title = html.escape(title)
        highlights.append(f"<li><strong>{source}</strong>: {title}</li>")

    highlights_html = (
        "\n      ".join(highlights)
        if highlights
        else "<li>오늘의 주요 뉴스를 확인하세요</li>"
    )

    topics = _extract_key_topics(news_items)

    # Better title generation: extract meaningful topics from content
    title_keywords = _build_digest_title(news_items, mode="security")

    base_tags = [
        "Security-Weekly",
        "DevSecOps",
        "Cloud-Security",
        "Weekly-Digest",
        str(date.year),
    ]
    topic_tags = [t for t in topics if t not in base_tags]
    tags = base_tags + topic_tags[:5]

    top_sources = list(
        {item.get("source_name", ""): True for item in news_items[:5]}.keys()
    )[:3]
    source_list = ", ".join(top_sources)

    # Generate Jekyll include tag for AI summary card - dynamic tags from actual content
    categories_html = '<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
    # Build tags from actual topics instead of hardcoding
    dynamic_tags = ["Security-Weekly"]
    for topic in topics[:4]:
        if topic not in dynamic_tags:
            dynamic_tags.append(topic)
    dynamic_tags.append(str(date.year))
    tags_html = "\n      ".join(
        f'<span class="tag">{t}</span>' for t in dynamic_tags[:6]
    )

    content = f'''---
layout: post
title: "{title_keywords}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [security, devsecops]
tags: [{", ".join(tags)}]
excerpt: "{title_keywords}를 중심으로 {date_str} 주요 보안/기술 뉴스 {total}건과 대응 우선순위를 정리합니다."
description: "{date_str} 보안 뉴스 요약. {source_list} 등 {total}건을 분석하고 {title_keywords} 중심의 DevSecOps 대응 포인트를 정리합니다."
keywords: [{", ".join(tags[:8])}]
author: Twodragon
comments: true
image: /assets/images/{image_filename}
image_alt: "{_to_english_svg_text(title_keywords)} security digest overview"
toc: true
---

{{% include ai-summary-card.html
  title='{title_keywords}'
  categories_html='{categories_html}'
  tags_html='{tags_html}'
  highlights_html='{highlights_html}'
  period='{date_str} (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}}

---

## 서론

안녕하세요, **Twodragon**입니다.

{date_str} 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: {total}개
- **보안 뉴스**: {stats.get("security", 0)}개
- **AI/ML 뉴스**: {stats.get("ai", 0)}개
- **클라우드 뉴스**: {stats.get("cloud", 0)}개
- **DevOps 뉴스**: {stats.get("devops", 0)}개
- **블록체인 뉴스**: {stats.get("blockchain", 0)}개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
'''

    # 하이라이트 테이블 생성 (주요 섹션 포괄)
    highlight_items = []
    for cat_items in [
        security_news,
        ai_news,
        cloud_news,
        devops_news,
        blockchain_news,
        tech_news,
    ]:
        for it in cat_items:
            if it not in highlight_items:
                highlight_items.append(it)
    for item in highlight_items[:10]:
        source = item.get("source_name", item.get("source", "Unknown"))[:20]
        title = _korean_display_title(item, max_len=60)
        category = item.get("category", "tech")
        emoji = CATEGORY_EMOJI.get(category, "📰")
        # Category display name mapping
        cat_display = {
            "security": "Security",
            "devsecops": "DevSecOps",
            "ai": "AI/ML",
            "cloud": "Cloud",
            "devops": "DevOps",
            "blockchain": "Blockchain",
            "tech": "Tech",
            "kubernetes": "K8s",
            "finops": "FinOps",
        }.get(category, category.title())
        severity = _determine_severity(item)
        severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(
            severity, "🟡"
        )
        content += f"| {emoji} **{cat_display}** | {source} | {title} | {severity_emoji} {severity} |\n"

    content += "\n---\n\n"

    content += _generate_executive_and_risk_sections(news_items, mode="security")

    section_num = 1

    # 보안 뉴스 섹션 - SK Shieldus 그룹핑 포함
    if security_news:
        content += f"## {section_num}. 보안 뉴스\n\n"

        # Separate SK Shieldus reports from regular security news
        skshieldus_reports = [
            item for item in security_news if item.get("source") == "skshieldus_report"
        ]
        regular_security = [
            item for item in security_news if item.get("source") != "skshieldus_report"
        ]

        for i, item in enumerate(regular_security, 1):
            is_critical = i <= 5  # 상위 5개 뉴스에 AI 강화 적용
            content += generate_news_section(
                item, f"{section_num}.{i}", is_critical=is_critical
            )

        # SK Shieldus reports grouped into a single subsection
        if skshieldus_reports:
            sub_idx = len(regular_security) + 1
            month_str = (
                date.strftime("%-m월")
                if sys.platform != "win32"
                else date.strftime("%m월").lstrip("0")
            )
            content += (
                f"### {section_num}.{sub_idx} SK쉴더스 {month_str} 보안 리포트\n\n"
            )
            content += "SK쉴더스에서 발행한 최신 보안 리포트 모음입니다.\n\n"
            for report in skshieldus_reports:
                report_title = report.get("title", "보안 리포트")
                report_url = report.get("url", "")
                report_summary = report.get("summary", "")
                content += f"- **[{report_title}]({report_url})**"
                if report_summary:
                    short_summary = report_summary[:100].rstrip(".")
                    content += f": {short_summary}"
                content += "\n"
            content += "\n> SK쉴더스 보안 리포트는 국내 보안 환경에 특화된 위협 분석을 제공합니다. 원문을 다운로드하여 상세 내용을 확인하시기 바랍니다.\n\n"
            content += "---\n\n"

        section_num += 1

    # AI/ML 뉴스 섹션
    if ai_news:
        content += f"## {section_num}. AI/ML 뉴스\n\n"
        for i, item in enumerate(ai_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # 클라우드 뉴스 섹션
    if cloud_news:
        content += f"## {section_num}. 클라우드 & 인프라 뉴스\n\n"
        for i, item in enumerate(cloud_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # DevOps 뉴스 섹션
    if devops_news:
        content += f"## {section_num}. DevOps & 개발 뉴스\n\n"
        for i, item in enumerate(devops_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # 블록체인 뉴스 섹션
    if blockchain_news:
        content += f"## {section_num}. 블록체인 뉴스\n\n"
        for i, item in enumerate(blockchain_news, 1):
            content += generate_news_section(item, f"{section_num}.{i}")
        section_num += 1

    # 기타 뉴스
    if tech_news:
        content += f"## {section_num}. 기타 주목할 뉴스\n\n"
        content += "| 제목 | 출처 | 핵심 내용 |\n"
        content += "|------|------|----------|\n"
        for item in tech_news[:5]:
            title = _korean_display_title(item, max_len=50)
            source = item.get("source_name", "")
            url = item.get("url", "")
            summary = _table_summary(_korean_brief_summary(item).replace("\n", " "))
            content += f"| [{title}]({url}) | {source} | {summary} |\n"
        content += "\n"
        section_num += 1

    # 트렌드 분석 섹션
    content += _generate_trend_analysis(news_items, section_num)
    section_num += 1

    # 뉴스 기반 실무 체크리스트
    content += _generate_news_specific_checklist(news_items)

    content += """## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
"""

    return content


def generate_tech_blog_content(
    news_items: List[Dict],
    categorized: Dict[str, List[Dict]],
    date: datetime,
    topics_slug: str = "",
) -> str:
    """Tech Blog Weekly Digest 컨텐츠 생성.

    Filters for geeknews, hackernews, and tech blog sources (NOT security/blockchain).
    Groups by topic: AI/ML, DevOps/Cloud, Open Source, General.
    Uses GeekNews Korean summaries prominently.
    """
    date_str = date.strftime("%Y년 %m월 %d일")
    date_file = date.strftime("%Y-%m-%d")
    image_filename = (
        f"{date_file}-Tech_Blog_Weekly_Digest_{topics_slug}.svg"
        if topics_slug
        else f"{date_file}-Tech_Blog_Weekly_Digest.svg"
    )

    total = len(news_items)

    # Group items by topic
    topic_groups = {
        "AI/ML": [],
        "DevOps/Cloud": [],
        "Open Source": [],
        "General": [],
    }

    ai_keywords = [
        "ai",
        "ml",
        "llm",
        "gpt",
        "claude",
        "gemini",
        "chatgpt",
        "copilot",
        "machine learning",
        "deep learning",
        "neural",
        "transformer",
        "agent",
    ]
    devops_keywords = [
        "kubernetes",
        "k8s",
        "docker",
        "cloud",
        "aws",
        "azure",
        "gcp",
        "terraform",
        "ci/cd",
        "devops",
        "sre",
        "infrastructure",
        "helm",
        "container",
        "serverless",
        "microservice",
    ]
    oss_keywords = [
        "open source",
        "open-source",
        "oss",
        "github",
        "rust",
        "golang",
        "go ",
        "python",
        "typescript",
        "linux",
        "apache",
        "mit license",
        "cncf",
    ]

    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()
        category = item.get("category", "tech")

        if any(kw in text for kw in ai_keywords) or category == "ai":
            topic_groups["AI/ML"].append(item)
        elif any(kw in text for kw in devops_keywords) or category in (
            "devops",
            "cloud",
        ):
            topic_groups["DevOps/Cloud"].append(item)
        elif any(kw in text for kw in oss_keywords):
            topic_groups["Open Source"].append(item)
        else:
            topic_groups["General"].append(item)

    # Title generation for tech-blog mode
    title_keywords = _build_digest_title(news_items, mode="tech-blog")

    topics = _extract_key_topics(news_items)
    base_tags = ["Tech-Blog", "Weekly-Digest", "Developer", str(date.year)]
    topic_tags = [t for t in topics if t not in base_tags]
    tags = base_tags + topic_tags[:5]

    # GeekNews items for prominent display
    geeknews_items = [item for item in news_items if item.get("source") == "geeknews"]

    top_sources = list(
        {item.get("source_name", ""): True for item in news_items[:5]}.keys()
    )[:3]
    source_list = ", ".join(top_sources)

    # Build highlights from top items
    highlights = []
    for item in news_items[:4]:
        source = html.escape(item.get("source_name", item.get("source", "Unknown")))
        title = _korean_display_title(item)
        if len(title) > 60:
            title = title[:60].rsplit(" ", 1)[0].rstrip(" ,.")
        title = html.escape(title)
        highlights.append(f"<li><strong>{source}</strong>: {title}</li>")

    highlights_html = (
        "\n      ".join(highlights)
        if highlights
        else "<li>이번 주 주요 기술 뉴스를 확인하세요</li>"
    )

    # Generate Jekyll include tag for AI summary card - dynamic tags from actual content
    categories_html = '<span class="category-tag tech">기술</span> <span class="category-tag devops">DevOps</span>'
    # Build tags from actual topics
    dynamic_tags = ["Tech-Blog"]
    for topic in topics[:4]:
        if topic not in dynamic_tags:
            dynamic_tags.append(topic)
    dynamic_tags.append(str(date.year))
    tags_html = "\n      ".join(
        f'<span class="tag">{t}</span>' for t in dynamic_tags[:6]
    )

    content = f'''---
layout: post
title: "기술 블로그 주간 다이제스트: {title_keywords}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [tech, devops]
tags: [{", ".join(tags)}]
excerpt: "{title_keywords}를 중심으로 {date_str} 주요 기술 블로그 뉴스 {total}건과 개발자 관점의 적용 포인트를 정리합니다."
description: "{date_str} 기술 블로그 다이제스트. {source_list} 등 {total}건을 분석하고 {title_keywords} 중심의 개발자 트렌드와 운영 시사점을 정리합니다."
keywords: [{", ".join(tags[:8])}]
author: Twodragon
comments: true
image: /assets/images/{image_filename}
image_alt: "{_to_english_svg_text(title_keywords)} tech digest overview"
toc: true
---

{{% include ai-summary-card.html
  title='기술 블로그 주간 다이제스트: {title_keywords}'
  categories_html='{categories_html}'
  tags_html='{tags_html}'
  highlights_html='{highlights_html}'
  period='{date_str} (24시간)'
  audience='소프트웨어 개발자, DevOps 엔지니어, 테크 리드, CTO'
%}}

---

{_generate_executive_and_risk_sections(news_items, mode="tech-blog")}
## 서론

안녕하세요, **Twodragon**입니다.

{date_str} 기준, 주요 기술 블로그와 커뮤니티에서 발표된 개발자 뉴스를 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: {total}개
- **AI/ML**: {len(topic_groups["AI/ML"])}개
- **DevOps/Cloud**: {len(topic_groups["DevOps/Cloud"])}개
- **Open Source**: {len(topic_groups["Open Source"])}개
- **General**: {len(topic_groups["General"])}개

---

'''

    section_num = 1

    # GeekNews 하이라이트 (Korean summaries prominently displayed)
    if geeknews_items:
        content += f"## {section_num}. GeekNews 하이라이트\n\n"
        content += "GeekNews에서 주목받은 기술 뉴스입니다.\n\n"
        for item in geeknews_items[:5]:
            title = _korean_display_title(item)
            url = item.get("url", "")
            source_name = item.get("source_name", "GeekNews")
            ko_summary = _korean_brief_summary(item)

            content += f"### {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략
        section_num += 1

    # AI/ML 섹션
    if topic_groups["AI/ML"]:
        content += f"## {section_num}. AI/ML 트렌드\n\n"
        for i, item in enumerate(topic_groups["AI/ML"][:5], 1):
            title = _korean_display_title(item)
            url = item.get("url", "")
            source = item.get("source_name", item.get("source", "Unknown"))
            ko_summary = _korean_brief_summary(item)

            content += f"### {section_num}.{i} {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략

            # Key points
            key_points = _generate_key_points(item)
            if key_points:
                content += "**핵심 포인트:**\n\n"
                content += key_points + "\n"
        section_num += 1

    # DevOps/Cloud 섹션
    if topic_groups["DevOps/Cloud"]:
        content += f"## {section_num}. DevOps & Cloud\n\n"
        for i, item in enumerate(topic_groups["DevOps/Cloud"][:5], 1):
            title = _korean_display_title(item)
            url = item.get("url", "")
            source = item.get("source_name", item.get("source", "Unknown"))
            ko_summary = _korean_brief_summary(item)

            content += f"### {section_num}.{i} {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략
        section_num += 1

    # Open Source 섹션
    if topic_groups["Open Source"]:
        content += f"## {section_num}. Open Source\n\n"
        for i, item in enumerate(topic_groups["Open Source"][:5], 1):
            title = _korean_display_title(item)
            url = item.get("url", "")
            source = item.get("source_name", item.get("source", "Unknown"))
            ko_summary = _korean_brief_summary(item)

            content += f"### {section_num}.{i} {title}\n\n"
            if ko_summary:
                content += f"{ko_summary}\n\n"
            # 출처는 news-card에 포함되므로 별도 blockquote 생략
        section_num += 1

    # General 섹션
    if topic_groups["General"]:
        content += f"## {section_num}. 기타 주목할 뉴스\n\n"
        content += "| 제목 | 출처 | 핵심 내용 |\n"
        content += "|------|------|----------|\n"
        for item in topic_groups["General"][:5]:
            title = _korean_display_title(item, max_len=50)
            source = item.get("source_name", "")
            url = item.get("url", "")
            ko_summary = _table_summary(_korean_brief_summary(item).replace("\n", " "))
            content += f"| [{title}]({url}) | {source} | {ko_summary} |\n"
        content += "\n"
        section_num += 1

    # 트렌드 분석
    content += _generate_tech_trend_analysis(news_items, section_num)
    content += _generate_news_specific_checklist(news_items)

    content += """---

**작성자**: Twodragon
"""

    return content


def _generate_tech_trend_analysis(news_items: List[Dict], section_num: int) -> str:
    """기술 블로그 트렌드 분석 섹션 생성"""
    content = f"\n---\n\n## {section_num}. 트렌드 분석\n\n"

    trend_defs = {
        "AI/LLM": [
            "ai",
            "llm",
            "gpt",
            "claude",
            "gemini",
            "machine learning",
            "인공지능",
            "생성형",
        ],
        "Cloud Native": ["cloud", "aws", "azure", "gcp", "serverless", "클라우드"],
        "Container/K8s": ["kubernetes", "k8s", "container", "docker", "컨테이너"],
        "Developer Tools": [
            "ide",
            "editor",
            "cli",
            "developer experience",
            "dx",
            "cursor",
            "copilot",
        ],
        "Open Source": ["open source", "open-source", "oss", "github", "cncf"],
        "Programming Languages": [
            "rust",
            "golang",
            "typescript",
            "python",
            "java",
            "swift",
        ],
        "Platform Engineering": [
            "platform",
            "internal developer",
            "golden path",
            "backstage",
        ],
    }

    trend_results = []
    for trend_name, keywords in trend_defs.items():
        count = 0
        matched_kws = set()
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            for kw in keywords:
                if kw in text:
                    count += 1
                    matched_kws.add(kw)
                    break
        if count > 0:
            trend_results.append((trend_name, count, ", ".join(list(matched_kws)[:3])))

    trend_results.sort(key=lambda x: x[1], reverse=True)

    if trend_results:
        content += "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        content += "|--------|-------------|------------|\n"
        for name, count, kws in trend_results[:7]:
            content += f"| **{name}** | {count}건 | {kws} |\n"
        content += "\n"

        top = trend_results[0]
        content += (
            f"이번 주기에서 가장 많이 언급된 트렌드는 **{top[0]}** ({top[1]}건)입니다. "
        )
        if len(trend_results) > 1:
            second = trend_results[1]
            content += (
                f"그 다음으로 **{second[0]}** ({second[1]}건)이 주목받고 있습니다. "
            )
        content += (
            "관련 기술 동향을 파악하고 팀 내 기술 공유에 활용하시기 바랍니다.\n\n"
        )
    else:
        content += "이번 주기에는 두드러진 트렌드가 감지되지 않았습니다.\n\n"

    return content


def _determine_severity(item: Dict) -> str:
    """뉴스 심각도 결정 - news_utils.determine_severity 위임."""
    try:
        from news_utils import determine_severity
    except ImportError:
        from scripts.news_utils import determine_severity

    text = (
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}"
    )
    category = item.get("category", "tech")
    return determine_severity(text, category)


def _extract_cve_ids(item: Dict) -> List[str]:
    """뉴스 아이템에서 모든 CVE ID 추출"""
    text = (
        f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}"
    )
    cves = re.findall(r"CVE-\d{4}-\d+", text)
    # 중복 제거하면서 순서 유지
    seen = set()
    unique = []
    for cve in cves:
        if cve not in seen:
            seen.add(cve)
            unique.append(cve)
    return unique


def _generate_key_points(item: Dict) -> str:
    """뉴스 아이템에서 핵심 포인트 추출"""
    summary = _korean_brief_summary(item)
    if not summary:
        return ""

    # 문장 단위로 분리하여 핵심 포인트 생성
    sentences = re.split(r"(?<=[.!?。다])\s+", summary)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if not sentences:
        return ""

    points = ""
    for s in sentences[:4]:
        # 마침표 제거 후 포인트로
        s = s.rstrip(".")
        points += f"- {s}\n"
    return points


def _generate_contextual_action_point(item: Dict) -> str:
    """Generate a context-aware action point based on actual article content.

    Extracts keywords from the title/summary to produce specific advice
    instead of generic category-based text.
    """
    title = (item.get("title", "") or "").lower()
    summary = (item.get("summary", "") or "").lower()
    combined = f"{title} {summary}"
    category = item.get("category", "tech")

    # Security-specific contextual hints
    if category in ("security", "devsecops"):
        if any(kw in combined for kw in ["patch", "update", "패치", "업데이트"]):
            return "영향받는 시스템 버전을 확인하고 패치 적용 일정을 수립하세요."
        if any(kw in combined for kw in ["ransomware", "랜섬웨어"]):
            return "백업 상태 확인, 네트워크 세그먼테이션 점검, 이메일 필터링 강화를 권장합니다."
        if any(kw in combined for kw in ["phishing", "피싱", "credential", "자격증명"]):
            return "MFA 적용 현황 점검 및 사용자 보안 인식 교육을 강화하세요."
        if any(kw in combined for kw in ["supply chain", "공급망", "dependency"]):
            return "서드파티 의존성 감사(SCA)를 수행하고 SBOM을 최신 상태로 유지하세요."
        if any(kw in combined for kw in ["data breach", "유출", "leak"]):
            return "영향 범위 파악, 인시던트 대응 절차 발동, 규제 기관 통보 여부를 확인하세요."
        if any(kw in combined for kw in ["malware", "악성코드", "trojan", "backdoor"]):
            return "EDR/SIEM에서 IoC 기반 탐지 룰을 업데이트하세요."
        if re.search(r"cve-\d{4}-\d+", combined):
            return (
                "해당 CVE의 영향 범위와 CVSS 점수를 확인 후 패치 우선순위를 결정하세요."
            )
        return "보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요."

    # AI category
    if category == "ai":
        if any(kw in combined for kw in ["agent", "에이전트", "agentic"]):
            return (
                "AI Agent 도입 시 권한 범위 설정과 출력 검증 체계를 사전에 수립하세요."
            )
        if any(
            kw in combined
            for kw in [
                "coding",
                "코딩",
                "copilot",
                "cursor",
                "코드 생성",
                "code generation",
            ]
        ):
            return "AI 생성 코드에 대한 보안 스캔(SAST/SCA) 게이트를 CI/CD에 필수 적용하세요."
        if any(kw in combined for kw in ["llm", "gpt", "claude", "gemini"]):
            return "LLM 서빙 환경의 접근 제어와 프롬프트 인젝션 방어 체계를 점검하세요."
        if any(
            kw in combined for kw in ["gpu", "nvidia", "compute", "training", "factory"]
        ):
            return "AI 인프라 도입 시 보안 경계 설계와 데이터 프라이버시 규정 준수를 확인하세요."
        if any(
            kw in combined
            for kw in ["open source", "오픈소스", "hugging face", "ollama"]
        ):
            return "오픈소스 모델 도입 시 출처 검증, 라이선스 및 학습 데이터 리스크를 평가하세요."
        if any(kw in combined for kw in ["model", "모델"]):
            return (
                "자사 AI 워크로드에 적용 가능성과 비용/성능 트레이드오프를 평가하세요."
            )
        return "AI/ML 파이프라인 및 서비스에 미치는 영향을 검토하세요."

    # Cloud / DevOps
    if category in ("cloud", "devops", "kubernetes"):
        if any(kw in combined for kw in ["rbac", "iam", "권한", "identity"]):
            return (
                "IAM/RBAC 정책의 최소 권한 원칙 준수와 서비스 계정 감사를 수행하세요."
            )
        if any(kw in combined for kw in ["kubernetes", "k8s", "쿠버네티스"]):
            return "클러스터 버전 호환성과 워크로드 영향을 확인하세요."
        if any(kw in combined for kw in ["docker", "container", "컨테이너"]):
            return "컨테이너 이미지 업데이트 및 런타임 보안 설정을 점검하세요."
        if any(kw in combined for kw in ["terraform", "iac", "인프라 코드"]):
            return "IaC 템플릿 보안 스캔(Checkov/tfsec)과 드리프트 탐지를 확인하세요."
        if any(
            kw in combined for kw in ["serverless", "lambda", "서버리스", "function"]
        ):
            return "서버리스 함수의 IAM 역할 최소화와 실행 환경 보안 설정을 점검하세요."
        if any(kw in combined for kw in ["aws", "azure", "gcp"]):
            return "클라우드 서비스 변경사항이 인프라 구성에 미치는 영향을 확인하세요."
        return "인프라 및 운영 환경 영향을 검토하세요."

    # Blockchain
    if category == "blockchain":
        if any(
            kw in combined
            for kw in [
                "hack",
                "exploit",
                "attack",
                "공격",
                "breach",
                "침해",
                "vulnerability",
            ]
        ):
            return "블록체인 보안 사고 관련 IoC를 확인하고 유사 공격 벡터에 대한 방어 체계를 점검하세요."
        if any(
            kw in combined
            for kw in [
                "regulation",
                "규제",
                "법안",
                "act",
                "compliance",
                "컴플라이언스",
                "sec",
                "cftc",
            ]
        ):
            return "규제 변화에 따른 컴플라이언스 영향을 법무팀과 사전 검토하세요."
        if any(
            kw in combined
            for kw in [
                "defi",
                "protocol",
                "프로토콜",
                "swap",
                "스왑",
                "lending",
                "대출",
            ]
        ):
            return "관련 DeFi 프로토콜의 스마트 컨트랙트 감사 현황과 비상 정지 메커니즘을 확인하세요."
        if any(
            kw in combined
            for kw in ["conference", "컨퍼런스", "summit", "speaker", "연사"]
        ):
            return "대규모 행사 전후로 관련 토큰 사기 및 가짜 이벤트 피싱이 증가합니다. 공식 채널만 이용하세요."
        if any(kw in combined for kw in ["bitcoin", "비트코인", "btc"]):
            return "시장 변동성 확대 시기에 피싱 도메인 모니터링을 강화하고 고액 출금 인증 절차를 점검하세요."
        if any(
            kw in combined
            for kw in ["ethereum", "이더리움", "eth", "stablecoin", "스테이블코인"]
        ):
            return "스마트 컨트랙트 기반 서비스의 접근 제어와 트랜잭션 모니터링을 점검하세요."
        return "관련 프로토콜 및 스마트 컨트랙트 영향을 확인하세요."

    return "실무 적용 전에 상세 내용을 확인하세요."


def _translate_to_korean_deepseek(
    text: str, context: str = "기술 뉴스", mode: str = "summary"
) -> str:
    """DeepSeek API를 활용한 한국어 번역 폴백

    Args:
        text: 번역할 영어 텍스트
        context: 번역 컨텍스트 (예: "기술 뉴스 제목", "보안 뉴스 요약")
        mode: "title" (제목 번역) 또는 "summary" (요약 번역)

    Returns:
        한국어 번역 텍스트 (실패 시 빈 문자열)
    """
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key or not text:
        return ""

    try:
        import requests

        if mode == "title":
            prompt = (
                f"다음 {context} 제목을 한국어로 자연스럽게 번역해 주세요. "
                "고유명사(회사명/제품명)는 원문 표기를 유지하세요. "
                "답변은 번역된 제목 한 줄만 출력하세요. "
                "따옴표, 번호, 불릿, 설명은 포함하지 마세요.\n\n"
                f"원문: {text}\n번역:"
            )
        else:
            prompt = (
                f"다음 {context}를 한국어 2~3문장으로 간결하게 요약해 주세요. "
                "기술 용어와 고유명사는 원문 표기를 유지하세요. "
                "마크다운, 불릿, 번호 없이 순수 문장만 출력하세요.\n\n"
                f"원문: {text[:1000]}\n요약:"
            )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 300,
        }

        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )

        if response.status_code == 200:
            result = response.json()
            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )
            translated = re.sub(r"\s+", " ", content.strip()).strip("\"'")
            if translated and re.search(r"[가-힣]", translated):
                logging.info(f"DeepSeek translated ({mode}): {text[:40]}...")
                return translated
        else:
            logging.warning(f"DeepSeek translate API status {response.status_code}")
    except ImportError:
        logging.debug("requests library not available for DeepSeek translation")
    except Exception as e:
        logging.warning(f"DeepSeek translate error: {e}")

    return ""


def _korean_display_title(item: Dict, max_len: int = 72) -> str:
    raw_title = (item.get("title", "") or "").strip()
    if not raw_title:
        return "제목 없음"

    if re.search(r"[가-힣]", raw_title):
        return raw_title

    cache_key = item.get("id") or item.get("url") or raw_title
    if cache_key in KOREAN_TITLE_CACHE:
        return KOREAN_TITLE_CACHE[cache_key]

    translated = ""
    if check_gemini_available():
        prompt = (
            "다음 기술 뉴스 제목을 한국어 한 줄로 번역. "
            "고유명사는 원문 유지. 따옴표/번호/설명 금지.\n"
            f"원문: {raw_title}\n번역:"
        )
        candidate = _gemini_call(prompt, timeout=15)
        if candidate:
            candidate = re.sub(r"\s+", " ", candidate).strip("\"'")
            if re.search(r"[가-힣]", candidate):
                translated = candidate

    if translated:
        KOREAN_TITLE_CACHE[cache_key] = translated
        return translated

    # Gemini 실패 시: DeepSeek API 폴백
    category = item.get("category", "tech")
    if _allow_deepseek():
        deepseek_translated = _translate_to_korean_deepseek(
            raw_title, context=f"{category} 뉴스", mode="title"
        )
        if deepseek_translated:
            KOREAN_TITLE_CACHE[cache_key] = deepseek_translated
            return deepseek_translated

    if raw_title:
        # AI 번역 실패 시: 실제 RSS 제목을 그대로 사용 (일반적 토픽 구문 대신)
        # CVE가 포함된 경우만 한국어 레이블 추가
        cve_match = re.search(r"CVE-\d{4}-\d+", raw_title, re.IGNORECASE)
        category_label = {
            "security": "보안",
            "devsecops": "DevSecOps",
            "ai": "AI",
            "cloud": "클라우드",
            "devops": "DevOps",
            "blockchain": "블록체인",
            "kubernetes": "쿠버네티스",
            "tech": "기술",
        }.get(category, "기술")

        if cve_match:
            display_title = (
                f"[{category_label}] {cve_match.group(0).upper()} 취약점 보안 업데이트"
            )
        else:
            # 실제 영문 제목을 그대로 사용하여 구체성 유지
            display_title = raw_title

        if len(display_title) > max_len:
            display_title = display_title[:max_len].rsplit(" ", 1)[0].rstrip(" ,.")

        KOREAN_TITLE_CACHE[cache_key] = display_title
        return display_title
    source_name = (
        item.get("source_name", "") or item.get("source", "해외 기술 매체")
    ).strip()
    if not source_name:
        source_name = "해외 기술 매체"
    fallback = f"{source_name} 기술 업데이트"
    KOREAN_TITLE_CACHE[cache_key] = fallback
    return fallback


def _korean_brief_summary(item: Dict, max_sentences: int = 2) -> str:
    summary = (item.get("summary", "") or "").strip()
    content_text = (item.get("content", "") or "").strip()
    text = summary or content_text
    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"URL:\s*https?://\S+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"https?://\S+", "", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    selected = sentences[:max_sentences] if sentences else [text[:220]]

    has_korean = bool(re.search(r"[가-힣]", text))
    if has_korean:
        needs_refine = len(text) > 220 or "URL:" in summary or "http" in summary
        if needs_refine and check_gemini_available():
            prompt = (
                "다음 기술 뉴스를 한국어 2문장 요약. URL/불릿/번호 금지.\n"
                f"제목: {item.get('title', '')}\n본문: {text[:600]}\n요약:"
            )
            generated = _gemini_call(prompt, timeout=15)
            if generated:
                generated = re.sub(r"\s+", " ", generated)
                generated = generated.replace("...", " ").replace("…", " ").strip(" .")
                if len(generated) >= 25:
                    return generated

        concise = " ".join(selected).replace("...", " ").replace("…", " ").strip(" .")
        if len(concise) > 220:
            concise = concise[:220].rsplit(" ", 1)[0].rstrip(" ,.")
        return concise

    cache_key = item.get("id") or item.get("url") or item.get("title") or text[:80]
    if cache_key in KOREAN_SUMMARY_CACHE:
        return KOREAN_SUMMARY_CACHE[cache_key]

    if check_gemini_available():
        prompt = (
            "다음 기술 뉴스를 한국어 2문장으로 요약. 마크다운/불릿 금지.\n"
            f"제목: {item.get('title', '')}\n요약: {text[:500]}\n응답:"
        )
        generated = _gemini_call(prompt, timeout=15)
        if generated:
            generated = re.sub(r"\s+", " ", generated)
            if len(generated) >= 30 and re.search(r"[가-힣]", generated):
                KOREAN_SUMMARY_CACHE[cache_key] = generated
                return generated

    # Gemini 실패 시: DeepSeek API 폴백으로 한국어 번역
    raw_summary = (item.get("summary", "") or "").strip()
    raw_content = (item.get("content", "") or "").strip()
    raw_text = raw_summary or raw_content

    if raw_text:
        category = item.get("category", "tech")
        title_text = item.get("title", "")
        translate_input = f"제목: {title_text}\n내용: {raw_text[:800]}"

        if _allow_deepseek():
            deepseek_translated = _translate_to_korean_deepseek(
                translate_input,
                context=f"{category} 뉴스 요약",
                mode="summary",
            )
            if deepseek_translated:
                # Use translated content directly; contextual action points are
                # added by generate_news_section() to avoid duplication
                KOREAN_SUMMARY_CACHE[cache_key] = deepseek_translated
                return deepseek_translated

        # AI 번역 실패 시: 실제 RSS 요약 텍스트를 정리하여 사용
        # 일반적 템플릿 문구 대신 원본 콘텐츠의 구체성을 유지
        source_name = item.get("source_name", item.get("source", ""))

        # HTML 태그 제거 및 정리
        clean_text = re.sub(r"<[^>]+>", "", raw_text)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()

        # 첫 2~3문장 추출 (최대 300자)
        sentences = re.split(r"(?<=[.!?。])\s+", clean_text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        summary_text = " ".join(sentences[:3])
        if len(summary_text) > 300:
            summary_text = summary_text[:297].rsplit(" ", 1)[0] + "..."

        action = _generate_contextual_action_point(item)
        if summary_text:
            result = f"{summary_text} {action}"
        else:
            title_ko = _korean_display_title(item)
            result = f"{title_ko}. {action}"

        KOREAN_SUMMARY_CACHE[cache_key] = result
        return result

    # No raw_text at all - use title-based fallback
    category = item.get("category", "tech")
    title_ko = _korean_display_title(item)
    source_name = item.get("source_name", item.get("source", ""))
    fallback = f"{title_ko} ({source_name}). 상세 내용은 출처 링크를 참조하세요."
    KOREAN_SUMMARY_CACHE[cache_key] = fallback
    return fallback


def generate_news_section(
    item: Dict, section_num: str, is_critical: bool = False
) -> str:
    """개별 뉴스 섹션 생성 - 고품질 분석 포함"""
    title = _korean_display_title(item)
    url = item.get("url", "")
    source = item.get("source_name", item.get("source", "Unknown"))
    content_text = item.get("content", "")
    category = item.get("category", "tech")

    severity = _determine_severity(item)
    cve_ids = _extract_cve_ids(item)
    image = item.get("image", "")
    ko_summary = _korean_brief_summary(item)

    section = f"### {section_num} {title}\n\n"

    # 뉴스 카드 (이미지 + 요약)
    if image or ko_summary:
        card_parts = [
            "{% include news-card.html",
            '  title="%s"' % title.replace('"', '\\"'),
            '  url="%s"' % url,
        ]
        if image:
            # Strip query params that break Jekyll include parser
            clean_image = image.split("?")[0] if "?" in image else image
            card_parts.append('  image="%s"' % clean_image)
        if ko_summary:
            card_summary = ko_summary[:200].replace('"', '\\"')
            card_parts.append('  summary="%s"' % card_summary)
        card_parts.append('  source="%s"' % source.replace('"', '\\"'))
        card_parts.append('  severity="%s"' % severity)
        card_parts.append("%}")
        section += "\n".join(card_parts) + "\n\n"

    # 심각도 및 CVE 뱃지
    if cve_ids or severity == "Critical":
        severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(
            severity, "🟡"
        )
        section += f"> {severity_emoji} **심각도**: {severity}"
        if cve_ids:
            section += f" | **CVE**: {', '.join(cve_ids[:5])}"
        section += "\n\n"

    # AI 강화 시도 (Critical/High 보안 뉴스만) - 3단계 폴백 체인 사용
    if is_critical and category in ("security", "devsecops"):
        enhanced = enhance_content_with_fallback(item)
        if enhanced:
            section += enhanced + "\n\n"

            # CVE가 있으면 MITRE 매핑 추가
            if cve_ids:
                section += generate_mitre_mapping(cve_ids[0], item)

            section += "\n---\n\n"
            return section

    # 폴백: 기존 템플릿
    section += "#### 요약\n\n"
    if ko_summary:
        section += f"{ko_summary}\n\n"
    elif content_text:
        section += f"{content_text[:800]}...\n\n"

    # Context-aware action point (skip if summary already contains 실무 포인트)
    if "실무 포인트" not in (ko_summary or ""):
        action_point = _generate_contextual_action_point(item)
        if action_point:
            section += f"**실무 포인트**: {action_point}\n\n"

    # 출처는 news-card에 포함되므로 별도 blockquote 생략

    # 핵심 포인트 - only if content differs from summary
    key_points = _generate_key_points(item)
    if key_points:
        # Check if key points are substantially different from summary
        ko_summary_stripped = (ko_summary or "").replace(" ", "").replace("\n", "")
        key_points_stripped = (
            key_points.replace("- ", "").replace(" ", "").replace("\n", "")
        )
        # Only show if less than 70% overlap
        if ko_summary_stripped and key_points_stripped:
            overlap = sum(
                1 for c in key_points_stripped[:100] if c in ko_summary_stripped[:200]
            )
            similarity = overlap / max(len(key_points_stripped[:100]), 1)
            if similarity < 0.7:
                section += "#### 핵심 포인트\n\n"
                section += key_points + "\n"

    # 카테고리별 상세 분석 템플릿
    if category in ("security", "devsecops") and is_critical:
        section += _generate_security_analysis_template(item)
    elif category in ("security", "devsecops"):
        section += _generate_security_brief_template(item)
    elif category == "ai":
        section += _generate_ai_analysis_template(item)
    elif category in ("cloud", "devops", "kubernetes"):
        section += _generate_devops_template(item)

    section += "\n---\n\n"
    return section


def _table_summary(text: str, max_len: int = 120) -> str:
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    cleaned = cleaned.replace("...", " ").replace("…", " ").strip(" .")
    if len(cleaned) <= max_len:
        return cleaned
    clipped = cleaned[:max_len].rsplit(" ", 1)[0].rstrip(" ,.")
    return clipped


def _generate_security_analysis_template(item: Dict) -> str:
    """보안 뉴스 상세 분석 템플릿 - 실제 데이터 기반"""
    cve_ids = _extract_cve_ids(item)
    severity = _determine_severity(item)
    text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()

    # 대응 우선순위 결정
    priority = "P0 - 즉시 대응" if severity == "Critical" else "P1 - 7일 이내 검토 권장"

    template = "\n#### 위협 분석\n\n"
    template += "| 항목 | 내용 |\n"
    template += "|------|------|\n"

    if cve_ids:
        template += f"| **CVE ID** | {', '.join(cve_ids[:5])} |\n"
    else:
        template += "| **CVE ID** | 미공개 또는 해당 없음 |\n"

    template += f"| **심각도** | {severity} |\n"
    template += f"| **대응 우선순위** | {priority} |\n"
    template += "\n"

    # SIEM 탐지 힌트 (취약점 유형 기반)
    siem_hints = []
    mitre_techniques = []

    if "rce" in text or "remote code execution" in text:
        siem_hints.append(
            '```splunk\nindex=security sourcetype=syslog ("exploit" OR "remote code execution" OR "shell")\n| stats count by src_ip, dest_ip, action\n| where count > 3\n```'
        )
        mitre_techniques.append("T1203 (Exploitation for Client Execution)")
    if "authentication" in text or "인증" in text or "auth bypass" in text:
        siem_hints.append(
            '```splunk\nindex=security sourcetype=auth ("bypass" OR "unauthorized" OR "failed_login")\n| stats count by user, src_ip\n| where count > 10\n```'
        )
        mitre_techniques.append("T1078 (Valid Accounts)")
    if "injection" in text or "sql" in text or "xss" in text:
        siem_hints.append(
            '```splunk\nindex=web sourcetype=access_combined (SELECT OR UNION OR script OR "\\x" OR "%27")\n| stats count by uri, src_ip\n| where count > 5\n```'
        )
        mitre_techniques.append("T1190 (Exploit Public-Facing Application)")
    if "supply chain" in text or "공급망" in text:
        mitre_techniques.append("T1195 (Supply Chain Compromise)")
    if "zero-day" in text or "제로데이" in text or "0-day" in text:
        mitre_techniques.append("T1068 (Exploitation for Privilege Escalation)")
    if "privilege" in text or "권한 상승" in text:
        mitre_techniques.append("T1068 (Exploitation for Privilege Escalation)")

    if siem_hints:
        template += "#### SIEM 탐지 쿼리 (참고용)\n\n"
        template += siem_hints[0] + "\n\n"

    if mitre_techniques:
        template += "#### MITRE ATT&CK 매핑\n\n"
        for tech in mitre_techniques[:3]:
            template += f"- **{tech}**\n"
        template += "\n"

    template += """#### 권장 조치

- [ ] 영향받는 시스템/소프트웨어 인벤토리 확인
- [ ] 벤더 패치 및 보안 권고 확인
- [ ] SIEM/EDR 탐지 룰 업데이트 검토
- [ ] 필요시 네트워크 격리 또는 임시 완화 조치 적용
- [ ] 보안팀 내 공유 및 모니터링 강화

"""
    return template


def _generate_security_brief_template(item: Optional[Dict] = None) -> str:
    """보안 뉴스 간략 분석 템플릿 - 토픽별 맞춤 조언 제공"""
    if item is None:
        return """
#### 권장 조치

- 관련 시스템 목록 확인
- 보안 담당자는 원문을 검토하여 자사 환경 해당 여부를 확인하시기 바랍니다
- 영향받는 시스템이 있는 경우 벤더 권고에 따라 패치 또는 완화 조치를 적용하세요
- SIEM 탐지 룰에 관련 IOC를 추가하는 것을 권장합니다

"""

    text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()

    # Ransomware-related advice
    if any(kw in text for kw in ["ransomware", "랜섬웨어", "ransom", "encrypt"]):
        return """
#### 권장 조치

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인

"""

    # Authentication-related advice
    if any(
        kw in text
        for kw in [
            "authentication",
            "인증",
            "credential",
            "password",
            "mfa",
            "sso",
            "auth bypass",
            "인증 우회",
            "login",
        ]
    ):
        return """
#### 권장 조치

- 관련 시스템의 인증 정보(Credential) 즉시 로테이션 검토
- MFA(다중 인증) 적용 현황 점검 및 미적용 시스템 식별
- SSO/IdP 로그에서 비정상 인증 시도 모니터링 강화
- 서비스 계정 및 API 키 사용 현황 감사

"""

    # Supply chain-related advice
    if any(
        kw in text
        for kw in [
            "supply chain",
            "공급망",
            "dependency",
            "package",
            "npm",
            "pypi",
            "maven",
            "sbom",
        ]
    ):
        return """
#### 권장 조치

- 의존성 감사(dependency audit) 즉시 실행: `npm audit`, `pip audit`, `bundle audit`
- SBOM(Software Bill of Materials) 최신 상태 확인
- 서드파티 라이브러리 버전 고정 및 무결성 검증(checksum/signature)
- CI/CD 파이프라인의 의존성 스캔 정책 점검

"""

    # Zero-day / exploit advice
    if any(
        kw in text
        for kw in ["zero-day", "제로데이", "0-day", "exploit", "actively exploited"]
    ):
        return """
#### 권장 조치

- 영향받는 소프트웨어/버전 인벤토리 즉시 확인 및 패치 적용
- 패치 불가 시 WAF 규칙 추가 또는 취약 서비스 네트워크 격리
- CISA KEV 카탈로그 등재 여부 확인 및 패치 SLA 적용
- EDR/NDR에서 관련 공격 패턴 탐지 룰 활성화

"""

    # Phishing / social engineering advice
    if any(
        kw in text
        for kw in [
            "phishing",
            "피싱",
            "social engineering",
            "사회공학",
            "vishing",
            "smishing",
        ]
    ):
        return """
#### 권장 조치

- 직원 대상 피싱 인식 교육 및 시뮬레이션 테스트 실시
- 이메일 보안 게이트웨이(SEG) 필터링 정책 업데이트
- 피싱 신고 채널 점검 및 의심 이메일 자동 격리 설정
- DMARC/SPF/DKIM 설정 상태 확인 및 정책 강화

"""

    # Data breach / leak advice
    if any(
        kw in text
        for kw in ["data breach", "데이터 유출", "leak", "유출", "exposed", "노출"]
    ):
        return """
#### 권장 조치

- 유출 범위 파악: 영향받는 데이터 유형, 건수, 시스템 식별
- 관련 계정 비밀번호 즉시 로테이션 및 세션 무효화
- 개인정보 유출 시 관할 기관 신고 의무 타임라인 확인
- DLP 정책 점검 및 민감 데이터 접근 로그 감사

"""

    # Default: improved generic
    return """
#### 권장 조치

- 관련 시스템 목록 확인 및 자사 환경 해당 여부 평가
- 벤더 보안 권고 확인 후 패치 또는 완화 조치 적용
- SIEM/EDR 탐지 룰에 관련 IoC 추가
- 보안팀 내 공유 및 모니터링 강화

"""


def _generate_ai_analysis_template(item: Dict) -> str:
    """AI/ML 관련 뉴스 분석 템플릿"""
    title = item.get("title", "")
    summary = item.get("summary", "")

    text = f"{title} {summary}".lower()

    template = "\n#### 실무 적용 포인트\n\n"
    if any(kw in text for kw in ["agent", "에이전트", "agentic"]):
        template += "- AI 에이전트 도구 호출 권한 및 접근 범위 최소화 설계\n"
        template += "- 에이전트 행동 로깅 및 감사 파이프라인 구축 검토\n"
        template += "- 에이전트 출력에 대한 검증 및 사람 감독(Human-in-the-Loop) 설계\n"
    elif any(kw in text for kw in ["llm", "gpt", "claude", "gemini", "model"]):
        template += "- LLM 입출력 데이터 보안 및 프라이버시 검토\n"
        template += "- 모델 서빙 환경의 접근 제어 및 네트워크 격리 확인\n"
        template += "- 프롬프트 인젝션 등 적대적 공격 대응 방안 점검\n"
    elif any(
        kw in text
        for kw in ["gpu", "nvidia", "인프라", "factory", "compute", "training"]
    ):
        template += "- 대규모 AI 인프라 도입 시 보안 경계 및 접근 제어 설계 검토\n"
        template += "- GPU 클러스터 운영 환경의 취약점 관리 및 패치 정책 수립\n"
        template += "- AI 워크로드 데이터 프라이버시 규정(GDPR, HIPAA) 준수 확인\n"
    elif any(
        kw in text
        for kw in ["simulation", "시뮬레이션", "digital twin", "optimize", "최적화"]
    ):
        template += (
            "- 시뮬레이션 기반 인프라 검증으로 배포 전 보안 취약점 사전 식별 활용\n"
        )
        template += "- AI 서비스 성능 최적화와 보안 모니터링 균형 설계\n"
        template += "- 운영 비용 절감 효과와 보안 투자 ROI 분석\n"
    elif any(
        kw in text
        for kw in [
            "coding",
            "코딩",
            "copilot",
            "cursor",
            "code generation",
            "코드 생성",
            "devtool",
            "ide",
            "vscode",
        ]
    ):
        template += "- AI 코딩 도구가 생성한 코드에 대한 자동 보안 스캔(SAST/SCA) 게이트 필수 적용\n"
        template += "- AI 생성 코드의 시크릿/자격증명 하드코딩 여부 자동 탐지 설정\n"
        template += "- 개발자 대상 AI 코딩 도구 보안 사용 가이드라인 수립 및 교육\n"
    elif any(
        kw in text for kw in ["attack", "공격", "threat", "위협", "malware", "악성"]
    ):
        template += "- AI 기반 위협 탐지 및 자동 대응 파이프라인 구축 검토\n"
        template += "- AI 모델 자체의 적대적 공격(Adversarial Attack) 방어 설계\n"
        template += "- 보안 팀의 AI 도구 활용 역량 강화 교육 계획 수립\n"
    elif any(
        kw in text
        for kw in [
            "open source",
            "오픈소스",
            "hugging face",
            "허깅페이스",
            "올라마",
            "ollama",
        ]
    ):
        template += "- 오픈소스 AI 모델 도입 시 라이선스 및 보안 취약점 검토\n"
        template += "- 모델 다운로드 출처 검증 및 체크섬/서명 확인 절차 수립\n"
        template += "- 오픈소스 모델의 학습 데이터 편향 및 프라이버시 리스크 평가\n"
    else:
        logging.info(
            f"AI template fallback triggered for: {item.get('title', '')[:60]}"
        )
        template += "- AI/ML 기술 도입 시 데이터 파이프라인 보안 및 접근 제어 검토\n"
        template += "- 모델 학습/추론 환경의 네트워크 격리 및 인증 체계 확인\n"
        template += "- 관련 기술의 자사 환경 적용 가능성 평가 및 보안 영향 분석\n"

    template += "\n"
    return template


def _generate_devops_template(item: Optional[Dict] = None) -> str:
    if item is None:
        return """
#### 실무 적용 포인트

- 운영 환경 변경 시 보안 구성 검증 자동화 파이프라인 점검
- 인프라 코드(IaC) 보안 스캔 도구 통합 및 정책 업데이트
- 변경 관리 프로세스에 보안 검토 단계 포함 확인

"""

    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    template = "\n#### 실무 적용 포인트\n\n"

    if any(kw in text for kw in ["docker", "container", "컨테이너"]):
        template += "- 컨테이너 이미지 보안 스캔 및 베이스 이미지 최신화 검토\n"
        template += "- Docker 환경에서의 네트워크 격리 및 접근 제어 설정 확인\n"
        template += "- 컨테이너 런타임 보안 모니터링 강화\n"
    elif any(
        kw in text
        for kw in [
            "rbac",
            "admission controller",
            "pod security",
            "psa",
            "psp",
            "opa",
            "gatekeeper",
        ]
    ):
        template += "- Kubernetes RBAC 역할 및 바인딩 최소 권한 원칙 준수 감사\n"
        template += "- Admission Controller/OPA 정책으로 비인가 리소스 생성 차단\n"
        template += "- Pod Security Admission(PSA) restricted 프로필 적용 현황 점검\n"
    elif any(
        kw in text
        for kw in [
            "image",
            "이미지",
            "registry",
            "레지스트리",
            "cosign",
            "sigstore",
            "sbom",
        ]
    ):
        template += (
            "- 컨테이너 이미지 서명(cosign/sigstore) 및 무결성 검증 파이프라인 확인\n"
        )
        template += "- 프라이빗 레지스트리 접근 제어 및 이미지 스캔 정책 점검\n"
        template += "- SBOM 기반 이미지 의존성 취약점 추적 자동화 설정\n"
    elif any(kw in text for kw in ["서비스 메시", "service mesh", "istio", "envoy"]):
        template += "- mTLS 기반 서비스 간 통신 암호화 적용 검토\n"
        template += "- 서비스 메시 관측성 활용한 이상 트래픽 탐지 설계\n"
        template += "- 네트워크 폴리시와 서비스 메시 정책 통합 관리\n"
    elif any(
        kw in text
        for kw in ["network policy", "네트워크 폴리시", "ingress", "egress", "cilium"]
    ):
        template += "- Kubernetes NetworkPolicy로 Pod 간 불필요한 통신 차단 설정\n"
        template += "- Ingress/Egress 트래픽 암호화(mTLS) 적용 현황 검토\n"
        template += "- 네트워크 관측성 도구(Cilium Hubble 등)로 이상 트래픽 탐지 강화\n"
    elif any(
        kw in text for kw in ["kubecon", "conference", "컨퍼런스", "행사", "summit"]
    ):
        template += "- 컨퍼런스에서 발표된 새로운 보안 프레임워크 및 도구 검토\n"
        template += "- 커뮤니티 모범 사례의 자사 환경 적용 가능성 평가\n"
        template += "- 발표된 오픈소스 프로젝트의 보안 성숙도 및 도입 로드맵 검토\n"
    elif any(kw in text for kw in ["kubernetes", "k8s", "kcd", "cncf"]):
        template += "- Kubernetes 클러스터 보안 벤치마크(CIS) 준수 점검\n"
        template += "- API 서버 접근 제어 및 감사 로그(Audit Log) 활성화 확인\n"
        template += "- 클러스터 업그레이드 주기 및 보안 패치 적용 현황 검토\n"
    elif any(
        kw in text for kw in ["ci/cd", "pipeline", "github action", "jenkins", "배포"]
    ):
        template += "- CI/CD 파이프라인 보안 강화: 시크릿 관리, 토큰 권한 최소화\n"
        template += "- 서드파티 Actions/플러그인의 출처 검증 및 버전 고정\n"
        template += "- 빌드/배포 로그 모니터링으로 비정상 행위 탐지\n"
    elif any(
        kw in text
        for kw in [
            "database",
            "데이터베이스",
            "db",
            "sql",
            "cache",
            "캐시",
            "redis",
            "valkey",
            "memorystore",
        ]
    ):
        template += "- 데이터베이스/캐시 서비스 업그레이드 시 데이터 무결성 검증 및 접근 제어 점검\n"
        template += (
            "- DB 연결 암호화(SSL/TLS) 설정이 모든 복제본/노드에 적용되는지 확인\n"
        )
        template += (
            "- 자동 확장 이벤트 감사 로그 모니터링으로 비정상 리소스 증가 탐지\n"
        )
    elif any(
        kw in text
        for kw in [
            "mobile",
            "모바일",
            "maui",
            "flutter",
            "react native",
            "ios",
            "android app",
        ]
    ):
        template += "- 모바일 앱 업데이트에 포함된 보안 패치 및 의존성 변경사항 검토\n"
        template += "- API 키 및 민감 데이터의 클라이언트 측 노출 방지 설정 점검\n"
        template += "- 사용자 데이터 수집 시 개인정보 보호 정책(GDPR, 개인정보보호법) 준수 확인\n"
    elif any(kw in text for kw in ["네트워크", "network"]):
        template += "- 네트워크 세그멘테이션 및 방화벽 규칙 최신화 점검\n"
        template += "- 비정상 트래픽 패턴 탐지를 위한 모니터링 강화\n"
        template += "- 네트워크 접근 제어 정책(Zero Trust) 적용 현황 검토\n"
    else:
        logging.info(
            f"DevOps template fallback triggered for: {item.get('title', '')[:60]}"
        )
        template += "- 운영 환경 변경 시 보안 구성 드리프트 탐지 자동화 확인\n"
        template += "- 인프라 변경사항의 보안 영향 사전 평가 프로세스 점검\n"
        template += "- 관련 기술 스택의 취약점 데이터베이스 모니터링 설정\n"

    template += "\n"
    return template


def _generate_trend_analysis(news_items: List[Dict], section_num: int) -> str:
    """뉴스 기반 트렌드 분석 섹션 생성 - 기사 제목 기반 구체적 키워드 추출"""
    content = f"\n---\n\n## {section_num}. 트렌드 분석\n\n"

    # 트렌드 키워드 카운트 + 대표 기사 수집
    trend_defs = {
        "AI/ML": ["ai", "ml", "llm", "gpt", "machine learning", "인공지능", "생성형"],
        "Zero-Day": ["zero-day", "0-day", "제로데이"],
        "Cloud Security": ["cloud", "aws", "azure", "gcp", "클라우드"],
        "Supply Chain": ["supply chain", "공급망", "dependency", "package"],
        "Ransomware": ["ransomware", "랜섬웨어"],
        "Container/K8s": ["kubernetes", "k8s", "container", "docker", "컨테이너"],
        "Authentication": ["authentication", "인증", "credential", "identity", "sso"],
    }

    trend_results = []
    for trend_name, keywords in trend_defs.items():
        count = 0
        representative_titles = []
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            for kw in keywords:
                if kw in text:
                    count += 1
                    # Extract short descriptive keyword from article title
                    title = item.get("title", "")
                    source = item.get("source_name", "")
                    # Create concise reference: "Source Product/Topic"
                    short_ref = _extract_trend_keyword(title, source)
                    if short_ref and short_ref not in representative_titles:
                        representative_titles.append(short_ref)
                    break  # count each news item once
        if count > 0:
            # Show article-specific keywords instead of generic match keywords
            display_kws = (
                ", ".join(representative_titles[:3])
                if representative_titles
                else trend_name
            )
            trend_results.append(
                (trend_name, count, display_kws, representative_titles)
            )

    trend_results.sort(key=lambda x: x[1], reverse=True)

    if trend_results:
        content += "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        content += "|--------|-------------|------------|\n"
        for name, count, kws, _ in trend_results[:7]:
            content += f"| **{name}** | {count}건 | {kws} |\n"
        content += "\n"

        # Generate specific analysis based on actual articles
        top = trend_results[0]
        top_refs = top[3][:2]  # top 2 representative titles
        content += f"이번 주기의 핵심 트렌드는 **{top[0]}**({top[1]}건)입니다. "
        if top_refs:
            content += f"{', '.join(top_refs)} 등이 주요 이슈입니다. "

        if len(trend_results) > 1:
            second = trend_results[1]
            second_refs = second[3][:2]
            if second_refs:
                content += f"**{second[0]}** 분야에서는 {', '.join(second_refs)} 관련 동향에 주목할 필요가 있습니다."
            else:
                content += f"**{second[0]}**({second[1]}건)도 주목할 트렌드입니다."
        content += "\n\n"
    else:
        content += "이번 주기에는 두드러진 트렌드가 감지되지 않았습니다.\n\n"

    return content


def _extract_trend_keyword(title: str, source: str) -> str:
    """Extract concise descriptive keyword from article title for trend table"""
    if not title:
        return ""
    # Remove common prefixes/noise
    title = re.sub(r"^\[.*?\]\s*", "", title)
    # For Korean titles, extract key noun phrases
    if re.search(r"[가-힣]", title):
        # Try to extract the main topic (first meaningful segment)
        parts = re.split(r"[,:\-–—·]", title)
        segment = parts[0].strip()
        if len(segment) > 30:
            segment = segment[:30]
        return segment
    # For English titles, extract product/topic name
    # Remove articles and common words
    words = title.split()
    if len(words) <= 4:
        return title.strip()
    # Take first meaningful phrase (up to 5 words, max 40 chars)
    phrase = " ".join(words[:5])
    if len(phrase) > 40:
        phrase = phrase[:40].rsplit(" ", 1)[0]
    return phrase


def _generate_news_specific_checklist(news_items: List[Dict]) -> str:
    """뉴스 기반 실무 체크리스트 생성"""
    content = "---\n\n## 실무 체크리스트\n\n"

    p0_items = []
    p1_items = []

    for item in news_items:
        category = item.get("category", "tech")
        # Only include security-relevant items in the checklist
        if category not in (
            "security",
            "devsecops",
            "ai",
            "cloud",
            "devops",
            "kubernetes",
        ):
            continue
        severity = _determine_severity(item)
        title = _korean_display_title(item, max_len=50)
        cve_ids = _extract_cve_ids(item)
        cve_str = f" ({', '.join(cve_ids[:2])})" if cve_ids else ""
        if severity == "Critical":
            p0_items.append(f"- [ ] **{title}**{cve_str} 관련 긴급 패치 및 영향도 확인")
        elif severity == "High":
            p1_items.append(f"- [ ] **{title}**{cve_str} 관련 보안 검토 및 모니터링")

    content += "### P0 (즉시)\n\n"
    if p0_items:
        content += "\n".join(p0_items[:5]) + "\n"
    else:
        # Generate specific P0 from top security news
        sec_items = [n for n in news_items if n.get("category") == "security"]
        if sec_items:
            top_sec = sec_items[0]
            title = _korean_display_title(top_sec, max_len=40)
            content += f"- [ ] **{title}** 관련 보안 영향도 분석 및 모니터링 강화\n"
        else:
            content += "- [ ] 이번 주기 주요 보안 이슈 영향도 분석\n"

    content += "\n### P1 (7일 내)\n\n"
    if p1_items:
        content += "\n".join(p1_items[:5]) + "\n"
    else:
        # Generate P1 from actual news categories
        categories_present = {n.get("category", "tech") for n in news_items}
        if "security" in categories_present:
            content += "- [ ] 보안 뉴스 기반 SIEM/EDR 탐지 룰 업데이트\n"
        if "cloud" in categories_present or "devops" in categories_present:
            cloud_items = [
                n for n in news_items if n.get("category") in ("cloud", "devops")
            ]
            if cloud_items:
                title = _korean_display_title(cloud_items[0], max_len=40)
                content += f"- [ ] **{title}** 관련 인프라 설정 점검\n"
        if not p1_items and "security" not in categories_present:
            content += "- [ ] 이번 주기 기술 동향 기반 보안 정책 검토\n"

    content += "\n### P2 (30일 내)\n\n"
    # Generate dynamic P2 based on news content
    p2_items = []
    categories_present = {n.get("category", "tech") for n in news_items}
    if "ai" in categories_present:
        ai_items = [n for n in news_items if n.get("category") == "ai"]
        if ai_items:
            title = _korean_display_title(ai_items[0], max_len=40)
            p2_items.append(f"- [ ] **{title}** 관련 AI 보안 정책 검토")
    if "cloud" in categories_present:
        p2_items.append("- [ ] 클라우드 인프라 보안 설정 정기 감사")
    if "blockchain" in categories_present:
        p2_items.append("- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검")
    if not p2_items:
        p2_items.append("- [ ] 이번 주기 트렌드 기반 보안 아키텍처 검토")
    content += "\n".join(p2_items[:3]) + "\n"

    return content


# ============================================================================
# SVG 이미지 생성 - 고품질 카드 기반 레이아웃
# ============================================================================

# 카테고리별 그라디언트 및 아이콘 설정
CATEGORY_SVG_CONFIG = {
    "security": {
        "gradient": ("dc2626", "991b1b"),  # red
        "label": "SECURITY",
        "icon": "!",
        "icon_color": "#dc2626",
    },
    "cloud": {
        "gradient": ("10b981", "059669"),  # green
        "label": "CLOUD",
        "icon": "AWS",
        "icon_color": "#10b981",
    },
    "devops": {
        "gradient": ("f59e0b", "d97706"),  # orange
        "label": "DEVOPS",
        "icon": "DEV",
        "icon_color": "#f59e0b",
    },
    "tech": {
        "gradient": ("3b82f6", "1d4ed8"),  # blue
        "label": "TECH",
        "icon": "AI",
        "icon_color": "#3b82f6",
    },
    "devsecops": {
        "gradient": ("8b5cf6", "6d28d9"),  # purple
        "label": "DEVSECOPS",
        "icon": "SEC",
        "icon_color": "#8b5cf6",
    },
    "ai": {
        "gradient": ("6366f1", "4f46e5"),  # indigo
        "label": "AI/ML",
        "icon": "AI",
        "icon_color": "#6366f1",
    },
    "blockchain": {
        "gradient": ("f97316", "ea580c"),  # orange
        "label": "BLOCKCHAIN",
        "icon": "BC",
        "icon_color": "#f97316",
    },
}


def _escape_svg_text(text: str) -> str:
    """SVG 텍스트 이스케이프 처리"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _to_english_svg_text(text: str) -> str:
    """SVG 텍스트에서 비영문 문자 제거 (SVG는 영문만 허용)"""
    result = []
    for char in text:
        if ord(char) < 128:  # ASCII
            result.append(char)
        elif unicodedata.category(char).startswith("L"):
            # Non-ASCII letter - skip (Korean, etc.)
            continue
        else:
            result.append(" ")
    # Clean up multiple spaces
    cleaned = " ".join("".join(result).split())
    if not cleaned.strip():
        return "Security News Update"
    return cleaned.strip()


def _truncate_text(text: str, max_len: int) -> str:
    """텍스트 길이 제한 (단어 경계에서 자름)"""
    if len(text) <= max_len:
        return text
    # Find last space before max_len to avoid cutting mid-word
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len * 0.6:  # Only use word boundary if reasonable
        return truncated[:last_space]
    return truncated.rstrip(" ,.")


def _extract_key_topics(news_items: List[Dict]) -> List[str]:
    """뉴스에서 핵심 토픽 추출"""
    topics = []
    keywords = [
        "Zero-Day",
        "CVE",
        "Vulnerability",
        "Patch",
        "Update",
        "AI",
        "ML",
        "Cloud",
        "Kubernetes",
        "Docker",
        "AWS",
        "Azure",
        "GCP",
        "Security",
        "Threat",
        "Malware",
        "Ransomware",
        "Botnet",
        "Bitcoin",
        "Ethereum",
        "DeFi",
        "Web3",
        "Blockchain",
        "LLM",
        "GPT",
        "Agent",
        "Data",
        "Palantir",
        "Tesla",
        "Apple",
        "Rust",
        "Go",
        "Open-Source",
        "API",
    ]

    for item in news_items[:6]:
        title = item.get("title", "")
        for kw in keywords:
            if kw.lower() in title.lower() and kw not in topics:
                topics.append(kw)
                if len(topics) >= 4:
                    return topics
    return topics[:4] if topics else ["Security", "Cloud", "DevOps", "AI"]


def _extract_visual_focus_labels(news_items: List[Dict], limit: int = 3) -> List[str]:
    """Return short English labels for low-text digest SVGs."""
    label_patterns = [
        (r"zero-day|0-day|제로데이|cve-", "ZERO DAY"),
        (r"ransomware|랜섬웨어", "RANSOM"),
        (r"byovd|driver|edr", "BYOVD"),
        (r"dns|exfil|data leak|유출", "DNS EXFIL"),
        (r"malware|악성코드", "MALWARE"),
        (r"telnet", "TELNETD"),
        (r"cisco|fmc", "FMC"),
        (r"dprk|north korea|북한", "DPRK"),
        (r"ai agent|agentic|llm|model", "AI AGENT"),
        (r"kubernetes|k8s|gke|cluster", "K8S"),
        (r"cloud|aws|azure|gcp", "CLOUD"),
        (r"patch|update", "PATCH"),
    ]

    labels: List[str] = []
    seen: set[str] = set()
    for item in news_items[:8]:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        for pattern, label in label_patterns:
            if re.search(pattern, text) and label not in seen:
                seen.add(label)
                labels.append(label)
                if len(labels) >= limit:
                    return labels

    for topic in _extract_key_topics(news_items):
        label = _truncate_text(_to_english_svg_text(topic).upper(), 12)
        if label and label not in seen:
            seen.add(label)
            labels.append(label)
            if len(labels) >= limit:
                break

    return labels[:limit] if labels else ["SECURITY", "CLOUD", "AI"]


def _convert_svg_to_og_png(svg_path: Path) -> None:
    """Convert SVG to PNG for Open Graph social media previews using rsvg-convert."""
    import shutil

    rsvg = shutil.which("rsvg-convert")
    if not rsvg:
        logging.debug("rsvg-convert not found, skipping PNG conversion")
        return

    png_path = svg_path.with_name(svg_path.stem + "_og.png")
    try:
        result = subprocess.run(
            [rsvg, "-w", "1200", "-h", "630", str(svg_path), "-o", str(png_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"✅ Created OG image: {png_path}")
        else:
            logging.warning(f"rsvg-convert failed: {result.stderr[:200]}")
    except Exception as e:
        logging.warning(f"PNG conversion skipped: {e}")


def generate_svg_image(
    date: datetime, categorized: Dict[str, List[Dict]], news_items: List[Dict]
) -> str:
    """Generate low-text digest SVG focused on standalone comprehension."""

    date_display = date.strftime("%B %d, %Y")
    focus_labels = _extract_visual_focus_labels(news_items, limit=3)

    if categorized.get("security") or categorized.get("devsecops"):
        main_category = "security"
    elif categorized.get("ai"):
        main_category = "ai"
    elif categorized.get("cloud"):
        main_category = "cloud"
    else:
        main_category = "tech"

    config = CATEGORY_SVG_CONFIG.get(main_category, CATEGORY_SVG_CONFIG["tech"])
    accent = config["icon_color"]
    headline = "THREAT SIGNAL MAP" if main_category == "security" else "TECH SIGNAL MAP"
    subtitle = "  ".join(focus_labels)
    node_colors = [accent, "#67e8f9", "#f59e0b"]
    node_positions = [(250, 360), (600, 210), (950, 360)]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1120"/>
      <stop offset="55%" stop-color="#151b32"/>
      <stop offset="100%" stop-color="#181024"/>
    </linearGradient>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="22"/>
    </filter>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="10" stdDeviation="18" flood-color="#020617" flood-opacity="0.5"/>
    </filter>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <circle cx="210" cy="170" r="180" fill="{accent}" opacity="0.14" filter="url(#glow)"/>
  <circle cx="980" cy="220" r="170" fill="#2563eb" opacity="0.12" filter="url(#glow)"/>
  <circle cx="930" cy="500" r="180" fill="#f59e0b" opacity="0.1" filter="url(#glow)"/>

  <rect x="70" y="58" width="170" height="34" rx="17" fill="#0f172a" stroke="#334155"/>
  <text x="155" y="81" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#cbd5e1" text-anchor="middle">WEEKLY DIGEST</text>

  <text x="90" y="164" font-family="Arial, sans-serif" font-size="52" font-weight="700" fill="#f8fafc">{headline}</text>
  <text x="92" y="204" font-family="Arial, sans-serif" font-size="20" fill="#cbd5e1">{_escape_svg_text(subtitle)}</text>

  <g transform="translate(600 336)" filter="url(#shadow)">
    <circle r="102" fill="#111827" stroke="{accent}" stroke-width="2.5"/>
    <circle r="44" fill="#0f172a" stroke="#e2e8f0" stroke-width="2"/>
    <path d="M-18 0 h36" stroke="#e2e8f0" stroke-width="8" stroke-linecap="round"/>
    <path d="M0 -18 v36" stroke="#e2e8f0" stroke-width="8" stroke-linecap="round"/>
    <text x="0" y="138" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#e2e8f0" text-anchor="middle">CORE</text>
  </g>
"""

    # Node icon templates keyed by label keyword
    _node_icons = {
        "malware": '<circle r="16" fill="{c}" opacity="0.2"/><circle cx="-12" cy="-8" r="6" fill="{c}" opacity="0.5"/><circle cx="12" cy="8" r="6" fill="{c}" opacity="0.5"/><circle cx="8" cy="-12" r="4" fill="{c}" opacity="0.4"/>',
        "ransom": '<rect x="-22" y="-4" width="44" height="36" rx="8" fill="#221617" stroke="{c}" stroke-width="2"/><path d="M-12 -4 v-16 c0-18 24-18 24 0 v16" stroke="{c}" stroke-width="4" fill="none" stroke-linecap="round"/><circle cx="0" cy="16" r="6" fill="{c}"/><rect x="-2" y="20" width="4" height="10" rx="2" fill="{c}"/>',
        "phish": '<path d="M-20 -8 L0 12 L20 -8" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/><rect x="-24" y="-16" width="48" height="36" rx="4" fill="none" stroke="{c}" stroke-width="2"/><circle cx="0" cy="-24" r="4" fill="{c}"/>',
        "cve": '<rect x="-20" y="-16" width="40" height="32" rx="6" fill="#1a1020" stroke="{c}" stroke-width="2"/><text x="0" y="-2" font-family="Courier New" font-size="11" font-weight="700" fill="{c}" text-anchor="middle">CVE</text><text x="0" y="12" font-family="Courier New" font-size="8" fill="{c}" text-anchor="middle" opacity="0.7">PATCH</text>',
        "cloud": '<path d="M-16 10 C-28 10 -32 -2 -32 -10 C-32 -20 -24 -26 -14 -26 C-10 -36 0 -42 10 -42 C24 -42 32 -32 32 -26 C40 -26 44 -20 44 -10 C44 -2 40 10 28 10 Z" fill="#0b1628" stroke="{c}" stroke-width="2" transform="scale(0.7)"/>',
        "ai": '<rect x="-28" y="-20" width="56" height="40" rx="8" fill="#111c35" stroke="{c}" stroke-width="2"/><circle cx="0" cy="-4" r="14" fill="#12345c" stroke="{c}" stroke-width="1.5"/><text x="0" y="1" font-family="Arial" font-size="12" font-weight="700" fill="{c}" text-anchor="middle">AI</text>',
        "k8s": '<circle cx="-16" cy="-12" r="12" fill="#09261d" stroke="{c}" stroke-width="1.5"/><circle cx="16" cy="-12" r="12" fill="#09261d" stroke="{c}" stroke-width="1.5"/><circle cx="0" cy="16" r="12" fill="#09261d" stroke="{c}" stroke-width="1.5"/><path d="M-8 -6 L8 -6 M-12 2 L0 14 M12 2 L0 14" stroke="{c}" stroke-width="1.5"/>',
        "dns": '<circle r="16" fill="{c}" opacity="0.15"/><circle cx="-10" cy="-6" r="5" fill="{c}" opacity="0.6"/><circle cx="10" cy="6" r="5" fill="{c}" opacity="0.6"/><circle cx="12" cy="-10" r="3" fill="{c}" opacity="0.4"/>',
        "edr": '<rect x="-22" y="-18" width="44" height="36" rx="6" fill="#0f172a" stroke="{c}" stroke-width="2"/><path d="M-12 -6 L-4 6 L14 -10" fill="none" stroke="{c}" stroke-width="3" stroke-linecap="round"/><line x1="-14" y1="14" x2="14" y2="14" stroke="{c}" stroke-width="1.5" opacity="0.5"/>',
        "default": '<circle r="18" fill="{c}" opacity="0.18"/><circle r="8" fill="{c}" opacity="0.3"/>',
    }

    def _match_icon(label: str) -> str:
        lbl = label.lower()
        for key in _node_icons:
            if key in lbl:
                return key
        if any(k in lbl for k in ["exploit", "vuln", "patch", "zero"]):
            return "cve"
        if any(k in lbl for k in ["encrypt", "lock", "ransom"]):
            return "ransom"
        if any(k in lbl for k in ["aws", "gcp", "azure", "cloud"]):
            return "cloud"
        if any(k in lbl for k in ["agent", "llm", "model"]):
            return "ai"
        if any(k in lbl for k in ["k8s", "kube", "gke", "eks"]):
            return "k8s"
        if any(k in lbl for k in ["bot", "worm", "trojan"]):
            return "malware"
        return "default"

    # Build attack-flow arrows from core to nodes
    arrow_svg = ""
    for idx, label in enumerate(focus_labels[:3]):
        x, y = node_positions[idx]
        color = node_colors[idx % len(node_colors)]
        # Curved arrow path
        cx1 = 600 + (x - 600) * 0.3
        cy1 = 336 + (y - 336) * 0.1
        cx2 = 600 + (x - 600) * 0.7
        cy2 = 336 + (y - 336) * 0.9
        arrow_svg += f'  <path d="M600 336 C{cx1:.0f} {cy1:.0f} {cx2:.0f} {cy2:.0f} {x} {y}" fill="none" stroke="{color}" stroke-width="3" stroke-dasharray="12 10" stroke-linecap="round" opacity="0.8"/>\n'

    svg += arrow_svg

    for idx, label in enumerate(focus_labels[:3]):
        x, y = node_positions[idx]
        color = node_colors[idx % len(node_colors)]
        icon_key = _match_icon(label)
        icon_svg = _node_icons[icon_key].replace("{c}", color)
        svg += f"""
  <g transform="translate({x} {y})" filter="url(#shadow)">
    <circle r="58" fill="#0f172a" stroke="{color}" stroke-width="2"/>
    {icon_svg}
    <text x="0" y="92" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="{color}" text-anchor="middle">{_escape_svg_text(label)}</text>
  </g>
"""

    svg += f"""
  <rect x="70" y="532" width="1060" height="1.5" fill="#334155" opacity="0.8"/>
  <text x="90" y="574" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8">{date_display}</text>
  <text x="1110" y="574" font-family="Arial, sans-serif" font-size="14" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
</svg>"""

    return svg


# ============================================================================
# 메인 실행
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="Auto publish news to _posts")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without publishing"
    )
    parser.add_argument("--hours", type=int, default=24, help="Hours to look back")
    parser.add_argument("--max-news", type=int, default=15, help="Maximum news items")
    parser.add_argument(
        "--mode",
        choices=["security", "tech-blog"],
        default="security",
        help="Post mode: security (default) or tech-blog digest",
    )
    parser.add_argument(
        "--use-ai",
        choices=[
            "auto",
            "claude",
            "gemini",
            "gpt-5.4",
            "codex-medium",
            "deepseek",
            "none",
        ],
        default=os.getenv("AUTO_PUBLISH_USE_AI", "auto"),
        help="AI enrichment mode (default: auto)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force publish even if same-day post exists",
    )
    parser.add_argument(
        "--date",
        type=str,
        default="",
        help="Target publish date in YYYY-MM-DD (default: today KST)",
    )
    parser.add_argument(
        "--post-filename",
        type=str,
        default="",
        help="Override output post filename (e.g., 2026-02-21-...md)",
    )
    parser.add_argument(
        "--image-filename",
        type=str,
        default="",
        help="Override output image filename (e.g., 2026-02-21-...svg)",
    )
    args = parser.parse_args()

    global _AI_MODE
    _AI_MODE = args.use_ai

    print(f"📰 Auto Publish News (mode: {args.mode}, ai: {_AI_MODE})")
    print("=" * 50)

    # Load news
    news_data = load_collected_news()
    print(f"✅ Loaded {news_data.get('total_items', 0)} news items")

    # Data freshness check
    collected_at_str = news_data.get("collected_at", "")
    if collected_at_str:
        try:
            collected_at = datetime.fromisoformat(
                collected_at_str.replace("Z", "+00:00")
            )
            data_age_hours = (
                datetime.now(timezone.utc) - collected_at
            ).total_seconds() / 3600
            if data_age_hours > 24:
                print(
                    f"⚠️ Data is {data_age_hours:.1f}h old. Time filter will be relaxed automatically."
                )
        except (ValueError, TypeError):
            pass

    # Filter and categorize
    filtered = filter_and_prioritize_news(news_data, hours=args.hours)

    # Cross-day dedup: remove items already published in recent posts
    published_urls = load_published_urls()
    if published_urls:
        print(f"  📋 Loaded {len(published_urls)} previously published URLs")
    filtered = filter_published_urls(filtered, published_urls)

    if len(filtered) < MIN_NEWS_COUNT:
        print(f"⚠️ Not enough news ({len(filtered)} < {MIN_NEWS_COUNT}). Skipping.")
        return

    categorized = categorize_news(filtered)

    # Date setup
    now = datetime.now(timezone(timedelta(hours=9)))  # KST
    if args.date:
        try:
            forced_date = datetime.strptime(args.date, "%Y-%m-%d")
            now = now.replace(
                year=forced_date.year,
                month=forced_date.month,
                day=forced_date.day,
            )
        except ValueError:
            print(f"❌ Invalid --date format: {args.date} (expected YYYY-MM-DD)")
            return
    date_str = now.strftime("%Y-%m-%d")

    # Duplicate check - only ONE post per day (any pattern)
    if not args.force:
        existing = list(POSTS_DIR.glob(f"{date_str}-*Digest*.md"))
        existing += list(POSTS_DIR.glob(f"{date_str}-*Weekly*.md"))
        # Deduplicate by filename
        existing = list({p.name: p for p in existing}.values())
        if existing:
            print(
                f"⏭️ Same-day post already exists ({len(existing)} found): {existing[0].name}"
            )
            print("   Only 1 post per day is allowed. Use --force to override.")
            return

    if args.mode == "tech-blog":
        # Filter for tech blog content only
        tech_categorized = {
            k: v
            for k, v in categorized.items()
            if k in ("tech", "devops", "ai", "cloud")
        }
        if not tech_categorized:
            print("⚠️ No tech blog content found. Skipping.")
            return
        selected = select_top_news(tech_categorized, args.max_news)
        topics = _extract_key_topics(selected)
        topics_slug = "_".join(topics[:3]) if topics else "Tech"

        post_content = generate_tech_blog_content(
            selected, tech_categorized, now, topics_slug
        )
        post_filename = f"{date_str}-Tech_Blog_Weekly_Digest_{topics_slug}.md"
        svg_filename = f"{date_str}-Tech_Blog_Weekly_Digest_{topics_slug}.svg"
    else:
        selected = select_top_news(categorized, args.max_news)
        topics = _extract_key_topics(selected)
        topics_slug = "_".join(topics[:4]) if topics else "News"

        post_content = generate_post_content(selected, categorized, now, topics_slug)
        post_filename = f"{date_str}-Tech_Security_Weekly_Digest_{topics_slug}.md"
        svg_filename = f"{date_str}-Tech_Security_Weekly_Digest_{topics_slug}.svg"

    if args.post_filename:
        post_filename = Path(args.post_filename).name
    if args.image_filename:
        svg_filename = Path(args.image_filename).name
        post_content = re.sub(
            r"^image:\s+.+$",
            f"image: /assets/images/{svg_filename}",
            post_content,
            flags=re.MULTILINE,
        )

    post_path = POSTS_DIR / post_filename
    svg_path = IMAGES_DIR / svg_filename

    print(f"✅ Selected {len(selected)} top news items")
    for cat, items in categorized.items():
        print(f"   - {cat}: {len(items)} items")

    # Generate SVG
    svg_content = generate_svg_image(now, categorized, selected)

    # Existing post protection
    if post_path.exists():
        existing_size = post_path.stat().st_size
        new_size = len(post_content.encode("utf-8"))
        if existing_size > new_size and not args.force:
            print(
                f"⏭️ Existing post is larger ({existing_size}B > {new_size}B). Skipping to preserve manual post."
            )
            print(f"   File: {post_path}")
            return
        else:
            print(f"📝 Overwriting existing post ({existing_size}B → {new_size}B)")

    if args.dry_run:
        print("\n📝 [DRY RUN] Would create:")
        print(f"   - Post: {post_path}")
        print(f"   - Image: {svg_path}")
        print("\n--- Post Preview (first 500 chars) ---")
        print(post_content[:500])
        return

    # Save files
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    with open(post_path, "w", encoding="utf-8") as f:
        f.write(post_content)
    _run_post_quality_gate(post_path, target=80)
    print(f"✅ Created post: {post_path}")

    # Track published URLs for cross-day dedup
    save_published_urls(selected, date_str)

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"✅ Created image: {svg_path}")

    # Generate PNG for Open Graph social previews
    _convert_svg_to_og_png(svg_path)

    print(f"\n🎉 Auto publish completed! (mode: {args.mode})")


if __name__ == "__main__":
    main()
