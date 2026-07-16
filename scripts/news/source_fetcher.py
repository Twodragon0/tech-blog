"""Read-only, cached fetch of public news article text (Sub-project A).

Fail-closed: any error / empty / too-short body returns None so the caller
keeps the existing short summary. Never raises to the caller. Cache mirrors
loader.load_published_urls (per-key expires_at ISO, 7-day TTL).
"""
import hashlib
import json
import logging
import os
import re
from datetime import datetime, timedelta
from typing import Optional

_MIN_TEXT_LEN = 400  # below this we treat as paywall/empty → fail closed
_UA = "Mozilla/5.0 (compatible; tech-blog-digest/1.0; +https://tech.2twodragon.com)"


def _key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def _http_get(url: str, timeout: int = 10) -> str:
    import requests  # lazy, matches repo pattern
    resp = requests.get(url, headers={"User-Agent": _UA}, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def _extract_text(html: str) -> str:
    # strip script/style, tags → whitespace-collapsed text
    html = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&[a-zA-Z#0-9]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _load_cache(path: Optional[str]) -> dict:
    if not path or not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _save_cache(path: Optional[str], data: dict) -> None:
    if not path:
        return
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
    except OSError:
        logging.debug("source_fetcher: cache write failed for %s", path)


def fetch_article(url: str, *, cache_path: Optional[str] = None,
                  ttl_days: int = 7, now: Optional[datetime] = None) -> Optional[str]:
    if not url or not url.startswith(("http://", "https://")):
        return None
    now = now or datetime.now()
    cache = _load_cache(cache_path)
    key = _key(url)
    entry = cache.get(key)
    if entry:
        try:
            if datetime.fromisoformat(entry["expires_at"]) > now:
                return entry.get("text") or None
        except (KeyError, ValueError):
            pass
    try:
        html = _http_get(url)
    except Exception as exc:  # fail-closed on ANY fetch error
        logging.info("source_fetcher: fetch failed (%s) — keeping short summary", exc)
        return None
    text = _extract_text(html)
    if len(text) < _MIN_TEXT_LEN:
        return None
    cache[key] = {"text": text, "expires_at": (now + timedelta(days=ttl_days)).isoformat()}
    _save_cache(cache_path, cache)
    return text
