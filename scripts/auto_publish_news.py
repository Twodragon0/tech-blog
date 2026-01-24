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
DATA_DIR = Path("data")  # 프로젝트 구조에 맞춰 data/ 사용

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
    """뉴스 필터링 및 우선순위 정렬"""
    items = news_data.get("items", [])
    if not items:
        return []

    # 시간 필터링
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
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

    # 우선순위 정렬
    def get_priority(item):
        source_priority = SOURCE_PRIORITY.get(item.get("source", ""), 5)
        category_priority = CATEGORY_PRIORITY.get(item.get("category", "tech"), 5)
        return (source_priority, category_priority)

    filtered.sort(key=get_priority)
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
excerpt: "{date_str} 주요 기술/보안 뉴스 심층 분석: DevSecOps 실무에 필요한 보안 위협, 클라우드 업데이트, AI/ML 동향을 정리했습니다. 총 {total}개 뉴스 중 핵심 내용만 선별하여 분석합니다."
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

    # 보안 뉴스 섹션
    if security_news:
        content += "## 1. 보안 뉴스\n\n"
        for i, item in enumerate(security_news, 1):
            content += generate_news_section(item, f"1.{i}")

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
        for item in tech_news[:3]:
            title = item.get("title", "")
            url = item.get("url", "")
            source = item.get("source_name", "")
            content += f"### {title[:50]}...\n\n"
            content += f"> **출처**: [{source}]({url})\n\n"

    # 체크리스트
    content += """---

## 5. DevSecOps 실무 체크리스트

이번 뉴스를 바탕으로 한 점검 항목:

### 긴급 (이번 주 내 조치)

- [ ] 보안 업데이트 및 패치 현황 점검
- [ ] MFA 설정 상태 확인
- [ ] 의심스러운 로그 모니터링

### 중요 (이번 달 내 계획)

- [ ] 보안 정책 검토 및 업데이트
- [ ] 클라우드 리소스 권한 감사
- [ ] 백업 및 복구 테스트

---

## 결론

오늘의 주요 뉴스에서 가장 중요한 포인트는 **지속적인 보안 모니터링과 업데이트**입니다.

다음에도 DevSecOps 실무에 도움이 되는 핵심 뉴스를 선별하여 분석해 드리겠습니다.

---

**참고 자료:**
- [The Hacker News](https://thehackernews.com/)
- [Google Cloud Blog](https://cloud.google.com/blog/)
- [HashiCorp Blog](https://www.hashicorp.com/blog/)
- [GeekNews](https://news.hada.io/)
"""

    return content


def generate_news_section(item: Dict, section_num: str) -> str:
    """개별 뉴스 섹션 생성"""
    title = item.get("title", "Untitled")
    url = item.get("url", "")
    source = item.get("source_name", item.get("source", "Unknown"))
    summary = item.get("summary", "")[:300]
    content_text = item.get("content", "")[:500]

    section = f"### {section_num} {title}\n\n"

    if summary:
        section += f"{summary}\n\n"
    elif content_text:
        section += f"{content_text}...\n\n"

    section += f"> **출처**: [{source}]({url})\n\n---\n\n"

    return section


# ============================================================================
# SVG 이미지 생성
# ============================================================================


def generate_svg_image(
    date: datetime, categorized: Dict[str, List[Dict]], news_items: List[Dict]
) -> str:
    """SVG 이미지 생성"""

    date_str = date.strftime("%Y.%m.%d")

    # 통계 계산
    total = sum(len(items) for items in categorized.values())
    security_pct = int(len(categorized.get("security", [])) / max(total, 1) * 100)
    cloud_pct = int(len(categorized.get("cloud", [])) / max(total, 1) * 100)
    devops_pct = int(len(categorized.get("devops", [])) / max(total, 1) * 100)
    tech_pct = 100 - security_pct - cloud_pct - devops_pct

    # 상위 뉴스 제목
    top_news = []
    for item in news_items[:4]:
        title = item.get("title", "")[:45]
        source = item.get("source_name", "")[:12]
        top_news.append((title, source))

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f172a"/>
      <stop offset="50%" style="stop-color:#1e293b"/>
      <stop offset="100%" style="stop-color:#0f172a"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#3b82f6"/>
      <stop offset="50%" style="stop-color:#8b5cf6"/>
      <stop offset="100%" style="stop-color:#ec4899"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="shadow">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.3"/>
    </filter>
  </defs>
  
  <rect width="1200" height="630" fill="url(#bgGrad)"/>
  
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#334155" stroke-width="0.5" opacity="0.3"/>
  </pattern>
  <rect width="1200" height="630" fill="url(#grid)"/>
  
  <circle cx="100" cy="100" r="200" fill="#3b82f6" opacity="0.05"/>
  <circle cx="1100" cy="530" r="250" fill="#8b5cf6" opacity="0.05"/>
  
  <rect x="0" y="0" width="1200" height="4" fill="url(#accentGrad)"/>
  
  <rect x="40" y="30" width="150" height="36" rx="18" fill="#3b82f6" opacity="0.2"/>
  <text x="115" y="54" font-family="system-ui, sans-serif" font-size="14" font-weight="600" fill="#60a5fa" text-anchor="middle">{date_str}</text>
  
  <text x="600" y="100" font-family="system-ui, sans-serif" font-size="42" font-weight="800" fill="#f8fafc" text-anchor="middle" filter="url(#glow)">Tech &amp; Security Weekly Digest</text>
  <text x="600" y="140" font-family="system-ui, sans-serif" font-size="18" fill="#94a3b8" text-anchor="middle">DevSecOps Insights - {total} News Analyzed</text>
  
  <rect x="400" y="160" width="400" height="2" fill="url(#accentGrad)" rx="1"/>
  
  <!-- Stats -->
  <g transform="translate(60, 200)">
    <rect width="250" height="180" rx="16" fill="#1e293b" filter="url(#shadow)"/>
    <text x="125" y="40" font-family="system-ui" font-size="16" font-weight="600" fill="#f8fafc" text-anchor="middle">Distribution</text>
    
    <g transform="translate(30, 70)">
      <rect width="{security_pct * 1.8}" height="20" rx="4" fill="#ef4444"/>
      <text x="0" y="45" font-family="system-ui" font-size="12" fill="#94a3b8">Security {security_pct}%</text>
    </g>
    <g transform="translate(30, 95)">
      <rect width="{cloud_pct * 1.8}" height="20" rx="4" fill="#22c55e"/>
      <text x="0" y="45" font-family="system-ui" font-size="12" fill="#94a3b8">Cloud {cloud_pct}%</text>
    </g>
    <g transform="translate(30, 120)">
      <rect width="{devops_pct * 1.8}" height="20" rx="4" fill="#f59e0b"/>
      <text x="0" y="45" font-family="system-ui" font-size="12" fill="#94a3b8">DevOps {devops_pct}%</text>
    </g>
  </g>
  
  <!-- Top News -->
  <g transform="translate(340, 200)">
    <rect width="800" height="180" rx="16" fill="#1e293b" filter="url(#shadow)"/>
    <text x="400" y="35" font-family="system-ui" font-size="16" font-weight="600" fill="#f8fafc" text-anchor="middle">Top Headlines</text>
'''

    colors = ["#ef4444", "#22c55e", "#3b82f6", "#f59e0b"]
    for i, (title, source) in enumerate(top_news):
        y_pos = 65 + i * 35
        svg += f'''    <g transform="translate(20, {y_pos})">
      <circle cx="8" cy="8" r="5" fill="{colors[i % len(colors)]}"/>
      <text x="25" y="12" font-family="system-ui" font-size="13" fill="#e2e8f0">{title}...</text>
      <text x="700" y="12" font-family="system-ui" font-size="11" fill="#64748b" text-anchor="end">{source}</text>
    </g>
'''

    svg += """  </g>
  
  <!-- Footer -->
  <rect x="0" y="520" width="1200" height="110" fill="#0f172a" opacity="0.8"/>
  
  <text x="60" y="565" font-family="system-ui" font-size="24" font-weight="700" fill="#f8fafc">Twodragon</text>
  <text x="60" y="595" font-family="system-ui" font-size="14" fill="#64748b">tech.2twodragon.com</text>
  
  <g transform="translate(400, 555)">
    <rect width="80" height="26" rx="13" fill="#3b82f6" opacity="0.2"/>
    <text x="40" y="18" font-family="system-ui" font-size="11" fill="#60a5fa" text-anchor="middle">#Security</text>
  </g>
  <g transform="translate(490, 555)">
    <rect width="90" height="26" rx="13" fill="#8b5cf6" opacity="0.2"/>
    <text x="45" y="18" font-family="system-ui" font-size="11" fill="#a78bfa" text-anchor="middle">#DevSecOps</text>
  </g>
  <g transform="translate(590, 555)">
    <rect width="70" height="26" rx="13" fill="#22c55e" opacity="0.2"/>
    <text x="35" y="18" font-family="system-ui" font-size="11" fill="#4ade80" text-anchor="middle">#Cloud</text>
  </g>
  
  <g transform="translate(1020, 550)">
    <rect width="120" height="40" rx="20" fill="url(#accentGrad)"/>
    <text x="60" y="26" font-family="system-ui" font-size="13" font-weight="600" fill="#ffffff" text-anchor="middle">Read More</text>
  </g>
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
    parser.add_argument("--max-news", type=int, default=10, help="Maximum news items")
    args = parser.parse_args()

    print("📰 Auto Publish News")
    print("=" * 50)

    # 뉴스 로드
    news_data = load_collected_news()
    print(f"✅ Loaded {news_data.get('total_items', 0)} news items")

    # 필터링 및 분류
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
