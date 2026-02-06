#!/usr/bin/env python3
"""
AI 강화 결과 캐싱 시스템 (7일 TTL)

AI 분석 결과를 효율적으로 캐싱하고 관리합니다.
"""

import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

# 로깅 설정
logger = logging.getLogger(__name__)

# 캐시 파일 위치
CACHE_FILE = Path(__file__).parent.parent / "_data" / "ai_cache.json"
TTL_DAYS = 7


def get_cache_key(url: str) -> str:
    """
    URL 기반 캐시 키 생성

    Args:
        url: 원본 URL

    Returns:
        SHA256 기반 16자 캐시 키
    """
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def load_cache() -> Dict:
    """
    캐시 파일 로드

    Returns:
        캐시 딕셔너리
    """
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return {}
    return {}


def save_cache(cache: Dict) -> bool:
    """
    캐시 파일 저장

    Args:
        cache: 저장할 캐시 딕셔너리

    Returns:
        성공 여부
    """
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save cache: {e}")
        return False


def is_cache_valid(timestamp_str: str) -> bool:
    """
    캐시 항목의 유효성 검사 (7일 TTL)

    Args:
        timestamp_str: ISO 형식 타임스탬프

    Returns:
        캐시가 유효한 경우 True
    """
    try:
        cached_time = datetime.fromisoformat(timestamp_str)
        age = datetime.now() - cached_time
        return age < timedelta(days=TTL_DAYS)
    except Exception:
        return False


def get_cached_analysis(url: str) -> Optional[str]:
    """
    캐시된 AI 분석 조회 (7일 이내만 반환)

    Args:
        url: 조회할 URL

    Returns:
        캐시된 분석 결과 (없으면 None)
    """
    cache = load_cache()
    key = get_cache_key(url)

    if key in cache:
        entry = cache[key]
        if is_cache_valid(entry.get("timestamp", "")):
            return entry.get("analysis")
        else:
            # 만료된 캐시 제거
            del cache[key]
            save_cache(cache)
            logger.info(f"Removed expired cache entry for {url}")

    return None


def cache_analysis(url: str, analysis: str) -> bool:
    """
    AI 분석 결과 캐싱

    Args:
        url: 원본 URL
        analysis: AI 분석 결과

    Returns:
        캐싱 성공 여부
    """
    cache = load_cache()
    key = get_cache_key(url)

    cache[key] = {
        "url": url,
        "analysis": analysis,
        "timestamp": datetime.now().isoformat(),
    }

    return save_cache(cache)


def clear_expired_cache() -> int:
    """
    만료된 캐시 항목 정리

    Returns:
        삭제된 항목 개수
    """
    cache = load_cache()
    initial_size = len(cache)

    # 만료된 항목 제거
    cache = {
        k: v
        for k, v in cache.items()
        if is_cache_valid(v.get("timestamp", ""))
    }

    if len(cache) < initial_size:
        save_cache(cache)
        removed = initial_size - len(cache)
        logger.info(f"Removed {removed} expired cache entries")
        return removed

    return 0


def get_cache_stats() -> Dict:
    """
    캐시 통계 조회

    Returns:
        캐시 통계 정보
    """
    cache = load_cache()

    total_entries = len(cache)
    valid_entries = sum(
        1
        for v in cache.values()
        if is_cache_valid(v.get("timestamp", ""))
    )
    expired_entries = total_entries - valid_entries

    total_size = sum(
        len(v.get("analysis", "")) for v in cache.values()
    )

    return {
        "total_entries": total_entries,
        "valid_entries": valid_entries,
        "expired_entries": expired_entries,
        "total_size_chars": total_size,
        "ttl_days": TTL_DAYS,
    }


def print_cache_stats():
    """캐시 통계 출력"""
    stats = get_cache_stats()
    print("\n📊 AI Cache Statistics")
    print(f"{'=' * 50}")
    print(f"Total entries: {stats['total_entries']}")
    print(f"Valid entries: {stats['valid_entries']}")
    print(f"Expired entries: {stats['expired_entries']}")
    print(f"Total size: {stats['total_size_chars']:,} chars")
    print(f"TTL: {stats['ttl_days']} days")
    print(f"{'=' * 50}\n")
