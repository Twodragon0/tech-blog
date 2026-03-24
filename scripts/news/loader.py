"""News loading, filtering, and prioritization functions."""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List

from scripts.news.config import (
    CATEGORY_PRIORITY,
    DATA_DIR,
    MAX_NEWS_PER_CATEGORY,
    MIN_NEWS_COUNT,
    PUBLISHED_URLS_FILE,
    PUBLISHED_URLS_TTL_DAYS,
    SOURCE_PRIORITY,
)


def load_collected_news() -> Dict:
    """Load collected news data."""
    news_file = DATA_DIR / "collected_news.json"
    if not news_file.exists():
        print("No collected news found. Run collect_tech_news.py first.")
        sys.exit(1)

    with open(news_file, "r", encoding="utf-8") as f:
        return json.load(f)


def load_published_urls(days: int = PUBLISHED_URLS_TTL_DAYS) -> set:
    """Load URLs published in recent posts to prevent cross-day duplicates."""
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

    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=PUBLISHED_URLS_TTL_DAYS)
    ).isoformat()
    existing_entries = [e for e in existing_entries if e.get("expires_at", "") > cutoff]

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
    print(f"  Published URL tracker updated: {len(existing_entries)} entries")


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
            f"  Cross-day dedup: removed {removed} items already published in recent posts"
        )
    return filtered


def filter_and_prioritize_news(news_data: Dict, hours: int = 24) -> List[Dict]:
    """Filter and prioritize news with progressive relaxation."""
    items = news_data.get("items", [])
    if not items:
        return []

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
                f"  Data age: {data_age_hours:.1f}h (collected at {collected_at_str})"
            )
        except (ValueError, TypeError):
            pass

    effective_hours = hours + data_age_hours
    time_windows = [hours, effective_hours, hours * 2, hours * 3]

    for window in time_windows:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=window)
        filtered = _filter_by_cutoff(items, cutoff)
        if len(filtered) >= MIN_NEWS_COUNT:
            if window > hours:
                print(
                    f"  Time window relaxed: {hours}h -> {window:.0f}h ({len(filtered)} items)"
                )
            break
    else:
        print(
            f"  All time windows insufficient. Using all {len(items)} items sorted by date."
        )
        filtered = sorted(
            items,
            key=lambda x: x.get("published", ""),
            reverse=True,
        )

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
        print(f"  Blocked {blocked_count} items containing excluded keywords")

    for item in filtered:
        summary = item.get("summary", "").strip()
        content_text = item.get("content", "").strip()
        if not summary and not content_text:
            item["_empty_content"] = True

    filtered = _deduplicate_crypto_stories(filtered)

    def get_priority(item):
        source_priority = SOURCE_PRIORITY.get(item.get("source", ""), 5)
        category_priority = CATEGORY_PRIORITY.get(item.get("category", "tech"), 5)
        empty_penalty = 10 if item.get("_empty_content") else 0
        return (empty_penalty, source_priority, category_priority)

    filtered.sort(key=get_priority)
    return filtered


def _deduplicate_crypto_stories(items: List[Dict]) -> List[Dict]:
    """Group related Bitcoin/crypto crash stories and keep only the 2 most substantive."""
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
        crypto_price_items.sort(
            key=lambda x: len(x.get("summary", "")) + len(x.get("content", "")),
            reverse=True,
        )
        other_items.extend(crypto_price_items[:2])
    else:
        other_items.extend(crypto_price_items)

    return other_items


def _filter_by_cutoff(items: List[Dict], cutoff: datetime) -> List[Dict]:
    """Filter news by cutoff time."""
    filtered = []
    for item in items:
        try:
            pub_date = datetime.fromisoformat(
                item.get("published", "").replace("Z", "+00:00")
            )
            if pub_date >= cutoff:
                filtered.append(item)
        except (ValueError, TypeError):
            filtered.append(item)
    return filtered


def categorize_news(items: List[Dict]) -> Dict[str, List[Dict]]:
    """Categorize news items with content-based reclassification."""
    categorized = defaultdict(list)

    for item in items:
        category = item.get("category", "tech")

        title_lower = (item.get("title", "") or "").lower()
        summary_lower = (item.get("summary", "") or "").lower()
        combined = f"{title_lower} {summary_lower}"

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

        if category not in ("security", "devsecops"):
            security_indicators = [
                "vulnerability",
                "exploit",
                "cve-",
                "\ucde8\uc57d\uc810",
                "malware",
                "\uc545\uc131\ucf54\ub4dc",
                "ransomware",
                "\ub79c\uc12c\uc6e8\uc5b4",
                "attack",
                "\uacf5\uaca9",
                "breach",
                "\uce68\ud574",
            ]
            security_score = sum(1 for kw in security_indicators if kw in combined)
            if security_score >= 2:
                category = "security"

        if category in ("security", "devsecops"):
            category = "security"
        elif category == "kubernetes":
            category = "devops"

        item["category"] = category

        if len(categorized[category]) < MAX_NEWS_PER_CATEGORY:
            if category not in ("security", "devsecops"):
                url = item.get("url", "")
                current_year = datetime.now(timezone.utc).year
                url_year_match = re.search(r"/(\d{4})/", url)
                if url_year_match:
                    url_year = int(url_year_match.group(1))
                    if 2000 <= url_year < current_year - 1:
                        continue
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
    """Select top news by category priority."""
    selected = []

    for category in sorted(
        categorized.keys(), key=lambda c: CATEGORY_PRIORITY.get(c, 5)
    ):
        for item in categorized[category]:
            if len(selected) >= max_total:
                break
            selected.append(item)

    return selected
