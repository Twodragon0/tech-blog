#!/usr/bin/env python3
"""
뉴스 콘텐츠 처리 공통 유틸리티

원문 콘텐츠 가져오기, 파싱, 캐싱 관련 공통 함수를 제공합니다.
"""

import logging
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

# 로깅 설정
logger = logging.getLogger(__name__)


def fetch_original_content(
    url: str, timeout: int = 15, max_chars: int = 8000
) -> str:
    """
    원문 URL에서 콘텐츠 가져오기

    Args:
        url: 원문 URL
        timeout: 요청 타임아웃 (초)
        max_chars: 최대 문자 제한

    Returns:
        추출된 원문 콘텐츠 (문자열)
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 불필요한 요소 제거
        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "iframe", "ad"]
        ):
            tag.decompose()

        # 본문 텍스트 추출
        text = soup.get_text(separator="\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        return text[: max_chars].strip()

    except Exception as e:
        logger.warning(f"Failed to fetch original content from {url}: {e}")
        return ""


def extract_article_content(html_content: str, max_chars: int = 8000) -> str:
    """
    HTML 콘텐츠에서 기사 본문 추출

    Args:
        html_content: HTML 콘텐츠
        max_chars: 최대 문자 제한

    Returns:
        추출된 기사 본문
    """
    try:
        soup = BeautifulSoup(html_content, "html.parser")

        # 불필요한 요소 제거
        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "iframe", "ad"]
        ):
            tag.decompose()

        # 여러 패턴으로 본문 추출 시도
        content = ""
        for selector in ["article", "main", ".post-content", ".entry-content", ".content"]:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator="\n", strip=True)
                break

        if not content:
            content = soup.get_text(separator="\n", strip=True)

        # 정규화
        content = re.sub(r"\n{3,}", "\n\n", content)
        content = re.sub(r" {2,}", " ", content)

        return content[:max_chars].strip()

    except Exception as e:
        logger.warning(f"Failed to extract article content: {e}")
        return ""


def validate_url(url: str) -> bool:
    """
    URL 유효성 검증

    Args:
        url: 검증할 URL

    Returns:
        유효한 URL인 경우 True
    """
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(url_pattern, url, re.IGNORECASE))


def clean_text(text: str) -> str:
    """
    텍스트 정규화 및 정제

    Args:
        text: 원본 텍스트

    Returns:
        정제된 텍스트
    """
    # 연속된 공백 제거
    text = re.sub(r" {2,}", " ", text)
    # 연속된 줄바꿈 제거
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 양쪽 공백 제거
    return text.strip()
