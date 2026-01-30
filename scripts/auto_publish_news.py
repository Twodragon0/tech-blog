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

Usage:
    python3 scripts/auto_publish_news.py
    python3 scripts/auto_publish_news.py --dry-run
    python3 scripts/auto_publish_news.py --hours 48
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

# ============================================================================
# 설정
# ============================================================================

POSTS_DIR = Path("_posts")
IMAGES_DIR = Path("assets/images")
DATA_DIR = Path("_data")  # 실제 데이터 디렉토리

CATEGORY_PRIORITY = {
    "security": 1,
    "devsecops": 2,
    "cloud": 3,
    "devops": 4,
    "tech": 5,
}

CATEGORY_EMOJI = {
    "security": "🔒",
    "devsecops": "🛡️",
    "cloud": "☁️",
    "devops": "⚙️",
    "tech": "💻",
    "kubernetes": "🚀",
    "finops": "💰",
}

CATEGORY_COLOR = {
    "security": "#ef4444",
    "devsecops": "#8b5cf6",
    "cloud": "#22c55e",
    "devops": "#f59e0b",
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
}

MIN_NEWS_COUNT = 5  # 최소 뉴스 수
MAX_NEWS_PER_CATEGORY = 3  # 카테고리당 최대 뉴스 수


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
            print(f"  📅 Data age: {data_age_hours:.1f}h (collected at {collected_at_str})")
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
                print(f"  ⏰ Time window relaxed: {hours}h → {window:.0f}h ({len(filtered)} items)")
            break
    else:
        # 모든 윈도우에서 부족하면 전체 아이템을 날짜순 정렬 후 사용
        print(f"  ⚠️ All time windows insufficient. Using all {len(items)} items sorted by date.")
        filtered = sorted(
            items,
            key=lambda x: x.get("published", ""),
            reverse=True,
        )

    # 우선순위 정렬
    def get_priority(item):
        source_priority = SOURCE_PRIORITY.get(item.get("source", ""), 5)
        category_priority = CATEGORY_PRIORITY.get(item.get("category", "tech"), 5)
        return (source_priority, category_priority)

    filtered.sort(key=get_priority)
    return filtered


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
    """뉴스를 카테고리별로 분류"""
    categorized = defaultdict(list)

    for item in items:
        category = item.get("category", "tech")
        # security, devsecops는 security로 통합
        if category in ("security", "devsecops"):
            category = "security"
        elif category in ("devops", "kubernetes"):
            category = "devops"

        if len(categorized[category]) < MAX_NEWS_PER_CATEGORY:
            categorized[category].append(item)

    return dict(categorized)


def select_top_news(
    categorized: Dict[str, List[Dict]], max_total: int = 10
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
# 포스트 생성
# ============================================================================


def generate_post_content(
    news_items: List[Dict], categorized: Dict[str, List[Dict]], date: datetime
) -> str:
    """고품질 포스트 컨텐츠 생성"""

    date_str = date.strftime("%Y년 %m월 %d일")
    date_file = date.strftime("%Y-%m-%d")

    # 카테고리별 통계
    stats = {cat: len(items) for cat, items in categorized.items()}
    total = sum(stats.values())

    # 핵심 뉴스 추출
    security_news = categorized.get("security", [])[:2]
    cloud_news = categorized.get("cloud", [])[:2]
    devops_news = categorized.get("devops", [])[:2]
    tech_news = categorized.get("tech", [])[:2]

    # 핵심 하이라이트 생성
    highlights = []
    for item in (security_news + cloud_news)[:4]:
        source = item.get("source_name", item.get("source", "Unknown"))
        title = item.get("title", "")[:60]
        highlights.append(f"<li><strong>{source}</strong>: {title}</li>")

    highlights_html = (
        "\n      ".join(highlights)
        if highlights
        else "<li>오늘의 주요 뉴스를 확인하세요</li>"
    )

    # 태그 생성
    tags = [
        "Security-Weekly",
        "DevSecOps",
        "Cloud-Security",
        "Zero-Trust",
        "AI-Security",
        "Weekly-Digest",
        str(date.year),
    ]

    content = f'''---
layout: post
title: "Tech & Security Weekly Digest ({date_str})"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [security, devsecops]
tags: [{", ".join(tags)}]
excerpt: "{date_str} 주요 기술/보안 뉴스 {total}건 심층 분석"
description: "{date_str} 보안/기술 뉴스: DevSecOps 실무에 필요한 보안 위협, 클라우드 업데이트, AI/ML 동향을 정리했습니다. 총 {total}개 뉴스 중 핵심 내용만 선별하여 분석합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Zero-Trust, AI-Security, Weekly-Digest]
author: Twodragon
comments: true
image: /assets/images/{date_file}-Tech_Security_Weekly_Digest.svg
image_alt: "Tech and Security Weekly Digest {date.strftime("%B %Y")}"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Tech & Security Weekly Digest ({date_str})</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Security-Weekly</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">{date.year}</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      {highlights_html}
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">수집 기간</span>
    <span class="summary-value">{date_str} (24시간)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다.

{date_str} 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: {total}개
- **보안 뉴스**: {stats.get("security", 0)}개
- **클라우드 뉴스**: {stats.get("cloud", 0)}개
- **DevOps 뉴스**: {stats.get("devops", 0)}개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
'''

    # 하이라이트 테이블 생성
    for item in news_items[:5]:
        source = item.get("source_name", item.get("source", "Unknown"))[:15]
        title = item.get("title", "")[:40]
        category = item.get("category", "tech")
        emoji = CATEGORY_EMOJI.get(category, "📰")
        content += (
            f"| {emoji} **{category.title()}** | {source} | {title}... | 중간 |\n"
        )

    content += "\n---\n\n"

    # 보안 뉴스 섹션 - 첫 번째는 상세 분석
    if security_news:
        content += "## 1. 보안 뉴스\n\n"
        for i, item in enumerate(security_news, 1):
            is_critical = (i == 1)  # 첫 번째 뉴스는 상세 분석
            content += generate_news_section(item, f"1.{i}", is_critical=is_critical)

    # 클라우드 뉴스 섹션
    if cloud_news:
        content += "## 2. 클라우드 & 인프라 뉴스\n\n"
        for i, item in enumerate(cloud_news, 1):
            content += generate_news_section(item, f"2.{i}")

    # DevOps 뉴스 섹션
    if devops_news:
        content += "## 3. DevOps & 개발 뉴스\n\n"
        for i, item in enumerate(devops_news, 1):
            content += generate_news_section(item, f"3.{i}")

    # 기타 뉴스
    if tech_news:
        content += "## 4. 기타 주목할 뉴스\n\n"
        content += "| 제목 | 출처 | 핵심 내용 |\n"
        content += "|------|------|----------|\n"
        for item in tech_news[:5]:
            title = item.get("title", "")[:50]
            source = item.get("source_name", "")
            url = item.get("url", "")
            summary = item.get("summary", "")[:80]
            content += f"| [{title}...]({url}) | {source} | {summary}... |\n"
        content += "\n"

    # 실무 체크리스트 (간결한 버전)
    content += """---

## 실무 체크리스트

### P0 (즉시)

- [ ] 긴급 보안 패치 적용
- [ ] 취약 시스템 모니터링 강화

### P1 (7일 내)

- [ ] SIEM 탐지 룰 업데이트
- [ ] 보안 정책 검토

### P2 (30일 내)

- [ ] 공격 표면 인벤토리 갱신
- [ ] 접근 제어 감사

---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
"""

    return content


def generate_news_section(item: Dict, section_num: str, is_critical: bool = False) -> str:
    """개별 뉴스 섹션 생성 - 고품질 분석 포함"""
    title = item.get("title", "Untitled")
    url = item.get("url", "")
    source = item.get("source_name", item.get("source", "Unknown"))
    summary = item.get("summary", "")
    content_text = item.get("content", "")
    category = item.get("category", "tech")

    section = f"### {section_num} {title}\n\n"

    # 개요 추가
    section += "#### 개요\n\n"
    if summary:
        # 전체 summary 사용 (truncate 제거)
        section += f"{summary}\n\n"
    elif content_text:
        section += f"{content_text[:800]}...\n\n"

    section += f"> **출처**: [{source}]({url})\n\n"

    # 보안 뉴스의 경우 상세 분석 템플릿 추가
    if category in ("security", "devsecops") and is_critical:
        section += _generate_security_analysis_template(title)
    elif category in ("security", "devsecops"):
        section += _generate_security_brief_template()
    elif category in ("cloud", "devops", "kubernetes"):
        section += _generate_devops_template()

    section += "\n---\n\n"
    return section


def _generate_security_analysis_template(title: str) -> str:
    """보안 뉴스 상세 분석 템플릿"""
    # CVE 패턴 추출
    cve_match = re.search(r'CVE-\d{4}-\d+', title)
    cve_id = cve_match.group(0) if cve_match else "N/A"

    template = f"""
#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | {cve_id} |
| **영향 범위** | 확인 필요 |
| **심각도** | 확인 필요 (원문 참조) |
| **익스플로잇 상태** | 확인 필요 |

#### 권장 조치

- [ ] 영향받는 시스템 식별
- [ ] 패치 가용성 확인
- [ ] 보안 모니터링 강화
- [ ] 필요시 임시 완화 조치 적용

"""
    return template


def _generate_security_brief_template() -> str:
    """보안 뉴스 간략 분석 템플릿"""
    return """
#### 실무 영향

보안 담당자는 해당 내용을 검토하고 필요시 조치 계획을 수립하시기 바랍니다.

"""


def _generate_devops_template() -> str:
    """DevOps/Cloud 뉴스 템플릿"""
    return """
#### 실무 적용 포인트

- 인프라 및 운영 환경에 대한 영향 검토
- 기존 워크플로우와의 통합 가능성 확인
- 팀 내 공유 및 테스트 계획 수립

"""


# ============================================================================
# SVG 이미지 생성
# ============================================================================


def generate_svg_image(
    date: datetime, categorized: Dict[str, List[Dict]], news_items: List[Dict]
) -> str:
    """고품질 SVG 이미지 생성 (영어)"""

    date_str = date.strftime("%Y.%m.%d")
    month_year = date.strftime("%B %Y")

    # 통계 계산
    total = sum(len(items) for items in categorized.values())
    security_count = len(categorized.get("security", []))
    cloud_count = len(categorized.get("cloud", []))
    devops_count = len(categorized.get("devops", []))
    tech_count = len(categorized.get("tech", []))

    # 상위 뉴스 제목 (영어만 사용)
    top_news = []
    for item in news_items[:3]:
        title = item.get("title", "")[:50]
        source = item.get("source_name", "")[:15]
        category = item.get("category", "tech")
        top_news.append((title, source, category))

    # 첫 번째 보안 뉴스를 Critical로 표시
    first_security = None
    for item in news_items:
        if item.get("category") in ("security", "devsecops"):
            first_security = item.get("title", "")[:45]
            break

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0a0f1a"/>
      <stop offset="30%" style="stop-color:#1a1f35"/>
      <stop offset="70%" style="stop-color:#0f172a"/>
      <stop offset="100%" style="stop-color:#0a0f1a"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#ef4444"/>
      <stop offset="25%" style="stop-color:#f97316"/>
      <stop offset="50%" style="stop-color:#eab308"/>
      <stop offset="75%" style="stop-color:#22c55e"/>
      <stop offset="100%" style="stop-color:#3b82f6"/>
    </linearGradient>
    <linearGradient id="cardGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#1e293b"/>
      <stop offset="100%" style="stop-color:#0f172a"/>
    </linearGradient>
    <linearGradient id="alertGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#ef4444"/>
      <stop offset="100%" style="stop-color:#dc2626"/>
    </linearGradient>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow">
      <feDropShadow dx="0" dy="6" stdDeviation="10" flood-opacity="0.4"/>
    </filter>
    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#334155" stroke-width="0.3" opacity="0.4"/>
    </pattern>
    <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.8" fill="#475569" opacity="0.3"/>
    </pattern>
  </defs>

  <rect width="1200" height="630" fill="url(#bgGrad)"/>
  <rect width="1200" height="630" fill="url(#grid)"/>
  <rect width="1200" height="630" fill="url(#dots)"/>

  <circle cx="0" cy="0" r="300" fill="#ef4444" opacity="0.03"/>
  <circle cx="1200" cy="630" r="350" fill="#3b82f6" opacity="0.03"/>

  <rect x="0" y="0" width="1200" height="5" fill="url(#accentGrad)"/>

  <g transform="translate(40, 25)">
    <rect width="120" height="40" rx="20" fill="#1e293b" stroke="#475569" stroke-width="1"/>
    <text x="60" y="26" font-family="system-ui, sans-serif" font-size="14" font-weight="600" fill="#94a3b8" text-anchor="middle">{date_str}</text>
  </g>

  <text x="600" y="100" font-family="system-ui, sans-serif" font-size="44" font-weight="800" fill="#f8fafc" text-anchor="middle" filter="url(#glow)">Tech &amp; Security Weekly Digest</text>
  <text x="600" y="140" font-family="system-ui, sans-serif" font-size="18" fill="#94a3b8" text-anchor="middle">DevSecOps Insights - {total} News Analyzed</text>

  <rect x="350" y="160" width="500" height="2" fill="url(#accentGrad)" rx="1"/>
'''

    # Critical Alert Card (if security news exists)
    if first_security:
        svg += f'''
  <g transform="translate(50, 190)">
    <rect width="350" height="180" rx="16" fill="url(#cardGrad)" filter="url(#shadow)" stroke="#ef4444" stroke-width="2"/>
    <rect x="0" y="0" width="350" height="40" rx="16" fill="#ef4444" opacity="0.15"/>
    <rect x="0" y="25" width="350" height="15" fill="#ef4444" opacity="0.15"/>
    <g transform="translate(15, 10)">
      <circle cx="10" cy="10" r="10" fill="#ef4444"/>
      <text x="10" y="15" font-family="system-ui" font-size="12" font-weight="700" fill="#fff" text-anchor="middle">!</text>
    </g>
    <text x="45" y="26" font-family="system-ui" font-size="14" font-weight="700" fill="#fca5a5">SECURITY ALERT</text>
    <text x="20" y="65" font-family="system-ui" font-size="12" font-weight="600" fill="#f8fafc">{first_security[:40]}...</text>
    <text x="20" y="90" font-family="system-ui" font-size="11" fill="#94a3b8">Review and apply patches immediately</text>
    <g transform="translate(20, 110)">
      <rect width="80" height="24" rx="6" fill="#dc2626"/>
      <text x="40" y="16" font-family="system-ui" font-size="11" font-weight="700" fill="#fff" text-anchor="middle">CRITICAL</text>
    </g>
    <g transform="translate(110, 110)">
      <rect width="90" height="24" rx="6" fill="#f97316" opacity="0.2"/>
      <text x="45" y="16" font-family="system-ui" font-size="10" font-weight="600" fill="#fb923c" text-anchor="middle">PATCH NOW</text>
    </g>
    <text x="20" y="165" font-family="system-ui" font-size="10" fill="#64748b">Source: The Hacker News</text>
  </g>
'''

    # Top Headlines Card
    svg += f'''
  <g transform="translate(420, 190)">
    <rect width="730" height="180" rx="16" fill="url(#cardGrad)" filter="url(#shadow)"/>
    <text x="365" y="30" font-family="system-ui" font-size="16" font-weight="600" fill="#f8fafc" text-anchor="middle">Top Headlines</text>
'''

    colors = {"security": "#ef4444", "devsecops": "#ef4444", "cloud": "#22c55e", "devops": "#f59e0b", "tech": "#3b82f6"}
    for i, (title, source, category) in enumerate(top_news):
        y_pos = 55 + i * 40
        color = colors.get(category, "#3b82f6")
        svg += f'''    <g transform="translate(20, {y_pos})">
      <circle cx="8" cy="8" r="6" fill="{color}"/>
      <text x="25" y="12" font-family="system-ui" font-size="12" font-weight="600" fill="#e2e8f0">{title}...</text>
      <text x="680" y="12" font-family="system-ui" font-size="10" fill="#64748b" text-anchor="end">{source}</text>
    </g>
'''

    svg += """  </g>
"""

    # Stats Section
    svg += f'''
  <g transform="translate(50, 390)">
    <rect width="1100" height="100" rx="16" fill="url(#cardGrad)" filter="url(#shadow)"/>
    <g transform="translate(80, 25)">
      <text x="0" y="0" font-family="system-ui" font-size="32" font-weight="800" fill="#f8fafc">{total}</text>
      <text x="0" y="22" font-family="system-ui" font-size="11" fill="#94a3b8">Total News</text>
    </g>
    <g transform="translate(250, 25)">
      <text x="0" y="0" font-family="system-ui" font-size="32" font-weight="800" fill="#ef4444">{security_count}</text>
      <text x="0" y="22" font-family="system-ui" font-size="11" fill="#fca5a5">Security</text>
      <rect x="0" y="35" width="100" height="6" rx="3" fill="#1e293b"/>
      <rect x="0" y="35" width="{min(security_count * 20, 100)}" height="6" rx="3" fill="#ef4444"/>
    </g>
    <g transform="translate(450, 25)">
      <text x="0" y="0" font-family="system-ui" font-size="32" font-weight="800" fill="#22c55e">{cloud_count}</text>
      <text x="0" y="22" font-family="system-ui" font-size="11" fill="#4ade80">Cloud</text>
      <rect x="0" y="35" width="100" height="6" rx="3" fill="#1e293b"/>
      <rect x="0" y="35" width="{min(cloud_count * 20, 100)}" height="6" rx="3" fill="#22c55e"/>
    </g>
    <g transform="translate(650, 25)">
      <text x="0" y="0" font-family="system-ui" font-size="32" font-weight="800" fill="#f59e0b">{devops_count}</text>
      <text x="0" y="22" font-family="system-ui" font-size="11" fill="#fbbf24">DevOps</text>
      <rect x="0" y="35" width="100" height="6" rx="3" fill="#1e293b"/>
      <rect x="0" y="35" width="{min(devops_count * 20, 100)}" height="6" rx="3" fill="#f59e0b"/>
    </g>
    <g transform="translate(850, 25)">
      <text x="0" y="0" font-family="system-ui" font-size="32" font-weight="800" fill="#3b82f6">{tech_count}</text>
      <text x="0" y="22" font-family="system-ui" font-size="11" fill="#60a5fa">Tech</text>
      <rect x="0" y="35" width="100" height="6" rx="3" fill="#1e293b"/>
      <rect x="0" y="35" width="{min(tech_count * 20, 100)}" height="6" rx="3" fill="#3b82f6"/>
    </g>
  </g>
'''

    # Footer
    svg += f'''
  <rect x="0" y="510" width="1200" height="120" fill="#0a0f1a" opacity="0.9"/>

  <text x="60" y="555" font-family="system-ui" font-size="24" font-weight="800" fill="#f8fafc">Twodragon</text>
  <text x="60" y="580" font-family="system-ui" font-size="13" fill="#64748b">tech.2twodragon.com</text>

  <g transform="translate(350, 545)">
    <rect width="85" height="26" rx="13" fill="#ef4444" opacity="0.2"/>
    <text x="42" y="18" font-family="system-ui" font-size="10" fill="#fca5a5" text-anchor="middle">#Security</text>
  </g>
  <g transform="translate(445, 545)">
    <rect width="95" height="26" rx="13" fill="#3b82f6" opacity="0.2"/>
    <text x="47" y="18" font-family="system-ui" font-size="10" fill="#60a5fa" text-anchor="middle">#DevSecOps</text>
  </g>
  <g transform="translate(550, 545)">
    <rect width="70" height="26" rx="13" fill="#22c55e" opacity="0.2"/>
    <text x="35" y="18" font-family="system-ui" font-size="10" fill="#4ade80" text-anchor="middle">#Cloud</text>
  </g>
  <g transform="translate(630, 545)">
    <rect width="75" height="26" rx="13" fill="#8b5cf6" opacity="0.2"/>
    <text x="37" y="18" font-family="system-ui" font-size="10" fill="#a78bfa" text-anchor="middle">#Weekly</text>
  </g>

  <g transform="translate(1020, 540)">
    <rect width="130" height="42" rx="21" fill="url(#accentGrad)" filter="url(#shadow)"/>
    <text x="65" y="27" font-family="system-ui" font-size="13" font-weight="700" fill="#ffffff" text-anchor="middle">Read More</text>
  </g>

  <rect x="0" y="625" width="1200" height="5" fill="url(#accentGrad)"/>
</svg>'''

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
    parser.add_argument("--max-news", type=int, default=10, help="Maximum news items")
    args = parser.parse_args()

    print("📰 Auto Publish News")
    print("=" * 50)

    # 뉴스 로드
    news_data = load_collected_news()
    print(f"✅ Loaded {news_data.get('total_items', 0)} news items")

    # 데이터 신선도 체크
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
                print(f"⚠️ Data is {data_age_hours:.1f}h old. Time filter will be relaxed automatically.")
        except (ValueError, TypeError):
            pass

    # 필터링 및 분류 (프로그레시브 완화 포함)
    filtered = filter_and_prioritize_news(news_data, hours=args.hours)
    if len(filtered) < MIN_NEWS_COUNT:
        print(f"⚠️ Not enough news ({len(filtered)} < {MIN_NEWS_COUNT}). Skipping.")
        return

    categorized = categorize_news(filtered)
    selected = select_top_news(categorized, args.max_news)

    print(f"✅ Selected {len(selected)} top news items")
    for cat, items in categorized.items():
        print(f"   - {cat}: {len(items)} items")

    # 날짜 설정
    now = datetime.now(timezone(timedelta(hours=9)))  # KST
    date_str = now.strftime("%Y-%m-%d")

    # 포스트 생성
    post_content = generate_post_content(selected, categorized, now)
    post_filename = f"{date_str}-Tech_Security_Weekly_Digest.md"
    post_path = POSTS_DIR / post_filename

    # SVG 이미지 생성
    svg_content = generate_svg_image(now, categorized, selected)
    svg_filename = f"{date_str}-Tech_Security_Weekly_Digest.svg"
    svg_path = IMAGES_DIR / svg_filename

    if args.dry_run:
        print("\n📝 [DRY RUN] Would create:")
        print(f"   - Post: {post_path}")
        print(f"   - Image: {svg_path}")
        print("\n--- Post Preview (first 500 chars) ---")
        print(post_content[:500])
        return

    # 파일 저장
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    with open(post_path, "w", encoding="utf-8") as f:
        f.write(post_content)
    print(f"✅ Created post: {post_path}")

    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"✅ Created image: {svg_path}")

    print("\n🎉 Auto publish completed!")


if __name__ == "__main__":
    main()
