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
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
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
    "meta_ai": 1,
    "huggingface": 2,
    "databricks": 2,
    "snowflake": 2,
    "bitcoin_magazine": 1,
    "cointelegraph": 2,
    "theblock": 2,
    "vitalik": 1,
    "chainalysis": 1,
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
        elif category == "kubernetes":
            category = "devops"
        # ai, blockchain은 독립 카테고리로 유지
        # cloud, devops, tech도 그대로 유지

        if len(categorized[category]) < MAX_NEWS_PER_CATEGORY:
            # Filter out stale items for non-security categories
            if category not in ("security", "devsecops"):
                # Check URL for old year indicators (e.g., /2023/ or /2024/)
                url = item.get("url", "")
                current_year = datetime.now(timezone.utc).year
                url_year_match = re.search(r'/(\d{4})/', url)
                if url_year_match:
                    url_year = int(url_year_match.group(1))
                    if 2000 <= url_year < current_year - 1:
                        continue
                # Also check published date
                try:
                    pub_date = datetime.fromisoformat(item.get("published", "").replace("Z", "+00:00"))
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
# 포스트 생성
# ============================================================================


def generate_post_content(
    news_items: List[Dict], categorized: Dict[str, List[Dict]], date: datetime, topics_slug: str = ""
) -> str:
    """고품질 포스트 컨텐츠 생성"""

    date_str = date.strftime("%Y년 %m월 %d일")
    date_file = date.strftime("%Y-%m-%d")
    image_filename = f"{date_file}-Tech_Security_Weekly_Digest_{topics_slug}.svg" if topics_slug else f"{date_file}-Tech_Security_Weekly_Digest.svg"

    stats = {cat: len(items) for cat, items in categorized.items()}
    total = sum(stats.values())

    # 핵심 뉴스 추출
    security_news = categorized.get("security", [])[:3]
    ai_news = categorized.get("ai", [])[:3]
    cloud_news = categorized.get("cloud", [])[:3]
    devops_news = categorized.get("devops", [])[:3]
    blockchain_news = categorized.get("blockchain", [])[:2]
    tech_news = categorized.get("tech", [])[:2]

    # 핵심 하이라이트 생성
    highlights = []
    for item in (security_news + cloud_news)[:4]:
        source = item.get("source_name", item.get("source", "Unknown"))
        title = item.get("title", "")
        if len(title) > 60:
            # Truncate at word boundary
            title = title[:57].rsplit(" ", 1)[0] + "..."
        source = html.escape(source)
        title = html.escape(title)
        highlights.append(f"<li><strong>{source}</strong>: {title}</li>")

    highlights_html = (
        "\n      ".join(highlights)
        if highlights
        else "<li>오늘의 주요 뉴스를 확인하세요</li>"
    )

    topics = _extract_key_topics(news_items)

    # 임팩트 높은 뉴스 우선 선택 (CVE, Zero-Day, Critical 키워드 우선)
    impact_keywords = ["cve", "zero-day", "0-day", "critical", "rce", "제로데이"]
    scored_items = []
    for item in news_items:
        t = item.get("title", "")
        score = sum(1 for kw in impact_keywords if kw in t.lower())
        scored_items.append((score, t))
    scored_items.sort(key=lambda x: x[0], reverse=True)

    # 핵심 키워드만 추출하여 간결한 제목 생성
    strip_prefixes = ["The ", "How ", "New ", "A "]
    top_titles = []
    for _, t in scored_items[:3]:
        for prefix in strip_prefixes:
            if t.startswith(prefix):
                t = t[len(prefix):]
                break
        # Extract just the key phrase (up to first comma, colon, or dash after 15 chars)
        short = t[:45]
        for sep in [", ", ": ", " - ", " — "]:
            idx = short.find(sep)
            if idx > 10:
                short = short[:idx]
                break
        top_titles.append(short.rstrip("., "))
    title_keywords = ", ".join(top_titles) if top_titles else "DevSecOps News"

    # Total title cap: "Tech & Security Weekly Digest: " = 32 chars, so keywords max ~88 chars
    if len(title_keywords) > 88:
        title_keywords = title_keywords[:85] + "..."

    base_tags = ["Security-Weekly", "DevSecOps", "Cloud-Security", "Weekly-Digest", str(date.year)]
    topic_tags = [t for t in topics if t not in base_tags]
    tags = base_tags + topic_tags[:5]

    top_sources = list({item.get("source_name", ""): True for item in news_items[:5]}.keys())[:3]
    source_list = ", ".join(top_sources)

    content = f'''---
layout: post
title: "Tech & Security Weekly Digest: {title_keywords}"
date: {date.strftime("%Y-%m-%d %H:%M:%S")} +0900
categories: [security, devsecops]
tags: [{", ".join(tags)}]
excerpt: "{date_str} 주요 보안/기술 뉴스 {total}건 - {", ".join(topics[:3])}"
description: "{date_str} 보안 뉴스: {source_list} 등 {total}건. {", ".join(topics[:4])} 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [{", ".join(tags[:8])}]
author: Twodragon
comments: true
image: /assets/images/{image_filename}
image_alt: "Tech Security Weekly Digest {date.strftime('%B %d %Y')} {' '.join(topics[:3])}"
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

    # 하이라이트 테이블 생성
    for item in news_items[:5]:
        source = item.get("source_name", item.get("source", "Unknown"))[:15]
        title = item.get("title", "")[:50]
        category = item.get("category", "tech")
        emoji = CATEGORY_EMOJI.get(category, "📰")
        severity = _determine_severity(item)
        severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(severity, "🟡")
        content += (
            f"| {emoji} **{category.title()}** | {source} | {title}... | {severity_emoji} {severity} |\n"
        )

    content += "\n---\n\n"

    section_num = 1

    # 보안 뉴스 섹션 - 첫 번째는 상세 분석
    if security_news:
        content += f"## {section_num}. 보안 뉴스\n\n"
        for i, item in enumerate(security_news, 1):
            is_critical = (i == 1)  # 첫 번째 뉴스는 상세 분석
            content += generate_news_section(item, f"{section_num}.{i}", is_critical=is_critical)
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
            title = item.get("title", "")[:50]
            source = item.get("source_name", "")
            url = item.get("url", "")
            summary = item.get("summary", "")[:80]
            content += f"| [{title}...]({url}) | {source} | {summary}... |\n"
        content += "\n"
        section_num += 1

    # 트렌드 분석 섹션
    content += _generate_trend_analysis(news_items, section_num)
    section_num += 1

    # 뉴스 기반 실무 체크리스트
    content += _generate_news_specific_checklist(news_items)

    content += """
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


def _determine_severity(item: Dict) -> str:
    """뉴스 심각도 결정"""
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    critical_keywords = [
        "critical", "rce", "zero-day", "제로데이", "0-day",
        "cvss 9", "cvss 10", "unauthenticated", "actively exploited",
    ]
    high_keywords = [
        "high", "권한 상승", "privilege escalation",
        "authentication bypass", "인증 우회", "ssrf", "injection",
    ]

    for kw in critical_keywords:
        if kw in text:
            return "Critical"
    for kw in high_keywords:
        if kw in text:
            return "High"
    return "Medium"


def _extract_cve_ids(item: Dict) -> List[str]:
    """뉴스 아이템에서 모든 CVE ID 추출"""
    text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}"
    cves = re.findall(r'CVE-\d{4}-\d+', text)
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
    summary = item.get("summary", "")
    if not summary:
        return ""

    # 문장 단위로 분리하여 핵심 포인트 생성
    sentences = re.split(r'[.!?]\s+', summary)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 15]

    if not sentences:
        return ""

    points = ""
    for s in sentences[:4]:
        # 마침표 제거 후 포인트로
        s = s.rstrip(".")
        points += f"- {s}\n"
    return points


def generate_news_section(item: Dict, section_num: str, is_critical: bool = False) -> str:
    """개별 뉴스 섹션 생성 - 고품질 분석 포함"""
    title = item.get("title", "Untitled")
    url = item.get("url", "")
    source = item.get("source_name", item.get("source", "Unknown"))
    summary = item.get("summary", "")
    content_text = item.get("content", "")
    category = item.get("category", "tech")

    severity = _determine_severity(item)
    cve_ids = _extract_cve_ids(item)

    section = f"### {section_num} {title}\n\n"

    # 심각도 및 CVE 뱃지
    if cve_ids or severity == "Critical":
        severity_emoji = {"Critical": "🔴", "High": "🟠", "Medium": "🟡"}.get(severity, "🟡")
        section += f"> {severity_emoji} **심각도**: {severity}"
        if cve_ids:
            section += f" | **CVE**: {', '.join(cve_ids[:5])}"
        section += "\n\n"

    # 개요 추가
    section += "#### 개요\n\n"
    if summary:
        section += f"{summary}\n\n"
    elif content_text:
        section += f"{content_text[:800]}...\n\n"

    section += f"> **출처**: [{source}]({url})\n\n"

    # 핵심 포인트
    key_points = _generate_key_points(item)
    if key_points:
        section += "#### 핵심 포인트\n\n"
        section += key_points + "\n"

    # 카테고리별 상세 분석 템플릿
    if category in ("security", "devsecops") and is_critical:
        section += _generate_security_analysis_template(item)
    elif category in ("security", "devsecops"):
        section += _generate_security_brief_template()
    elif category == "ai":
        section += _generate_ai_analysis_template(item)
    elif category in ("cloud", "devops", "kubernetes"):
        section += _generate_devops_template()

    section += "\n---\n\n"
    return section


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


def _generate_security_brief_template() -> str:
    return """
#### 실무 영향

- 보안 담당자는 원문을 검토하여 자사 환경 해당 여부를 확인하시기 바랍니다
- 영향받는 시스템이 있는 경우 벤더 권고에 따라 패치 또는 완화 조치를 적용하세요
- SIEM 탐지 룰에 관련 IOC를 추가하는 것을 권장합니다

"""


def _generate_ai_analysis_template(item: Dict) -> str:
    """AI/ML 관련 뉴스 분석 템플릿"""
    title = item.get("title", "")
    summary = item.get("summary", "")

    template = """
#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검

"""
    return template


def _generate_devops_template() -> str:
    return """
#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

"""


def _generate_trend_analysis(news_items: List[Dict], section_num: int) -> str:
    """뉴스 기반 트렌드 분석 섹션 생성"""
    content = f"\n---\n\n## {section_num}. 트렌드 분석\n\n"

    # 트렌드 키워드 카운트
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
        matched_kws = set()
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
            for kw in keywords:
                if kw in text:
                    count += 1
                    matched_kws.add(kw)
                    break  # 뉴스당 1번만 카운트
        if count > 0:
            trend_results.append((trend_name, count, ", ".join(list(matched_kws)[:3])))

    trend_results.sort(key=lambda x: x[1], reverse=True)

    if trend_results:
        content += "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        content += "|--------|-------------|------------|\n"
        for name, count, kws in trend_results[:7]:
            content += f"| **{name}** | {count}건 | {kws} |\n"
        content += "\n"

        # 트렌드 분석 코멘트
        top = trend_results[0]
        content += f"이번 주기에서 가장 많이 언급된 트렌드는 **{top[0]}** ({top[1]}건)입니다. "
        if len(trend_results) > 1:
            second = trend_results[1]
            content += f"그 다음으로 **{second[0]}** ({second[1]}건)이 주목받고 있습니다. "
        content += "실무에서는 해당 트렌드와 관련된 보안 정책 및 모니터링 체계를 점검하시기 바랍니다.\n\n"
    else:
        content += "이번 주기에는 두드러진 트렌드가 감지되지 않았습니다.\n\n"

    return content


def _generate_news_specific_checklist(news_items: List[Dict]) -> str:
    """뉴스 기반 실무 체크리스트 생성"""
    content = "---\n\n## 실무 체크리스트\n\n"

    p0_items = []
    p1_items = []

    for item in news_items:
        severity = _determine_severity(item)
        title = item.get("title", "")[:60]
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
        content += "- [ ] 긴급 보안 패치 적용\n"
        content += "- [ ] 취약 시스템 모니터링 강화\n"

    content += "\n### P1 (7일 내)\n\n"
    if p1_items:
        content += "\n".join(p1_items[:5]) + "\n"
    else:
        content += "- [ ] SIEM 탐지 룰 업데이트\n"
        content += "- [ ] 보안 정책 검토\n"

    content += "\n### P2 (30일 내)\n\n"
    content += "- [ ] 공격 표면 인벤토리 갱신\n"
    content += "- [ ] 접근 제어 감사\n"

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
        elif unicodedata.category(char).startswith('L'):
            # Non-ASCII letter - skip (Korean, etc.)
            continue
        else:
            result.append(' ')
    # Clean up multiple spaces
    cleaned = ' '.join(''.join(result).split())
    if not cleaned.strip():
        return "Security News Update"
    return cleaned.strip()


def _truncate_text(text: str, max_len: int) -> str:
    """텍스트 길이 제한 (영문 기준)"""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


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
    ]

    for item in news_items[:6]:
        title = item.get("title", "")
        for kw in keywords:
            if kw.lower() in title.lower() and kw not in topics:
                topics.append(kw)
                if len(topics) >= 4:
                    return topics
    return topics[:4] if topics else ["Security", "Cloud", "DevOps", "AI"]


def generate_svg_image(
    date: datetime, categorized: Dict[str, List[Dict]], news_items: List[Dict]
) -> str:
    """고품질 SVG 이미지 생성 - 카드 기반 레이아웃"""

    date_display = date.strftime("%B %d, %Y")
    date_short = date.strftime("%Y.%m.%d")

    # 통계 계산
    total = sum(len(items) for items in categorized.values())
    stats = {cat: len(items) for cat, items in categorized.items()}

    # 핵심 토픽 추출
    topics = _extract_key_topics(news_items)
    subtitle_topics = " | ".join(_to_english_svg_text(t) for t in topics)

    # 상위 뉴스 6개 선택 (카드용)
    top_items = news_items[:6]

    # SVG 헤더 및 정의
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">
  <defs>
    <!-- Background Gradient -->
    <linearGradient id="bgGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f0f23"/>
      <stop offset="50%" style="stop-color:#1a1a3e"/>
      <stop offset="100%" style="stop-color:#0d1117"/>
    </linearGradient>
    
    <!-- Card Gradient -->
    <linearGradient id="cardGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e293b"/>
      <stop offset="100%" style="stop-color:#0f172a"/>
    </linearGradient>
    
    <!-- Category Gradients -->
    <linearGradient id="redGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#dc2626"/>
      <stop offset="100%" style="stop-color:#991b1b"/>
    </linearGradient>
    <linearGradient id="blueGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#3b82f6"/>
      <stop offset="100%" style="stop-color:#1d4ed8"/>
    </linearGradient>
    <linearGradient id="purpleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#8b5cf6"/>
      <stop offset="100%" style="stop-color:#6d28d9"/>
    </linearGradient>
    <linearGradient id="greenGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#10b981"/>
      <stop offset="100%" style="stop-color:#059669"/>
    </linearGradient>
    <linearGradient id="orangeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f59e0b"/>
      <stop offset="100%" style="stop-color:#d97706"/>
    </linearGradient>
    <linearGradient id="indigoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#6366f1"/>
      <stop offset="100%" style="stop-color:#4f46e5"/>
    </linearGradient>
    
    <!-- Glow Filter -->
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    
    <!-- Shadow Filter -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.3"/>
    </filter>
    <pattern id="grid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#334155" stroke-width="0.3" opacity="0.4"/>
    </pattern>
    <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="0.8" fill="#475569" opacity="0.3"/>
    </pattern>
  </defs>
  
  <!-- Background -->
  <rect width="1200" height="630" fill="url(#bgGradient)"/>
  
  <!-- Grid Pattern -->
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#ffffff" stroke-opacity="0.03" stroke-width="1"/>
  </pattern>
  <rect width="1200" height="630" fill="url(#grid)"/>
  
  <!-- Decorative Circles -->
  <circle cx="100" cy="100" r="200" fill="#3b82f6" fill-opacity="0.05"/>
  <circle cx="1100" cy="530" r="250" fill="#8b5cf6" fill-opacity="0.05"/>
  <circle cx="600" cy="315" r="300" fill="#dc2626" fill-opacity="0.03"/>
  
  <!-- Header Section -->
  <rect x="40" y="30" width="200" height="36" rx="18" fill="url(#redGradient)" filter="url(#shadow)"/>
  <text x="140" y="54" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">WEEKLY DIGEST</text>
  
  <!-- Date Badge -->
  <rect x="960" y="30" width="200" height="36" rx="18" fill="url(#blueGradient)" filter="url(#shadow)"/>
  <text x="1060" y="54" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white" text-anchor="middle">{date_display}</text>
  
  <!-- Main Title -->
  <text x="600" y="110" font-family="Arial, sans-serif" font-size="42" font-weight="bold" fill="white" text-anchor="middle" filter="url(#glow)">Tech &amp; Security Weekly Digest</text>
  <text x="600" y="155" font-family="Arial, sans-serif" font-size="20" fill="#94a3b8" text-anchor="middle">{_escape_svg_text(subtitle_topics)}</text>
'''

    # 카드 레이아웃 생성 (최대 6개 카드, 3x2 그리드)
    card_positions = [
        (50, 190, 340, 180),  # Row 1, Card 1
        (430, 190, 340, 180),  # Row 1, Card 2
        (810, 190, 340, 180),  # Row 1, Card 3
        (50, 400, 340, 160),  # Row 2, Card 1
        (430, 400, 340, 160),  # Row 2, Card 2
        (810, 400, 340, 160),  # Row 2, Card 3
    ]

    gradient_map = {
        "security": "redGradient",
        "devsecops": "purpleGradient",
        "ai": "indigoGradient",
        "cloud": "greenGradient",
        "devops": "orangeGradient",
        "blockchain": "orangeGradient",
        "tech": "blueGradient",
    }

    for idx, item in enumerate(top_items):
        if idx >= len(card_positions):
            break

        x, y, width, height = card_positions[idx]
        category = item.get("category", "tech")
        if category in ("security", "devsecops"):
            category_display = "security"
        elif category in ("devops", "kubernetes"):
            category_display = "devops"
        elif category == "ai":
            category_display = "ai"
        elif category == "blockchain":
            category_display = "blockchain"
        else:
            category_display = category

        config = CATEGORY_SVG_CONFIG.get(category_display, CATEGORY_SVG_CONFIG["tech"])
        gradient = gradient_map.get(category_display, "blueGradient")

        title = _escape_svg_text(_truncate_text(_to_english_svg_text(item.get("title", "News Update")), 35))
        source = _escape_svg_text(
            _truncate_text(_to_english_svg_text(item.get("source_name", item.get("source", "Source"))), 15)
        )

        # 요약 또는 컨텐츠에서 핵심 정보 추출
        summary = item.get("summary", item.get("content", ""))
        summary_lines = []
        if summary:
            words = summary.split()
            line = ""
            for word in words:
                if len(line + " " + word) > 40:
                    summary_lines.append(line.strip())
                    line = word
                    if len(summary_lines) >= 2:
                        break
                else:
                    line = line + " " + word if line else word
            if line and len(summary_lines) < 2:
                summary_lines.append(line.strip())

        svg += f'''
  <!-- Card {idx + 1}: {config["label"]} -->
  <g transform="translate({x}, {y})">
    <rect width="{width}" height="{height}" rx="16" fill="url(#cardGradient)" filter="url(#shadow)"/>
    <rect x="0" y="0" width="{width}" height="6" rx="3" fill="url(#{gradient})"/>
    
    <!-- Icon -->
    <circle cx="40" cy="50" r="24" fill="url(#{gradient})" fill-opacity="0.2"/>
    <text x="40" y="58" font-family="Arial, sans-serif" font-size="16" fill="{config["icon_color"]}" text-anchor="middle">{config["icon"]}</text>
    
    <text x="80" y="45" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="{config["icon_color"]}">{config["label"]}</text>
    <text x="80" y="65" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="white">{title}</text>
'''

        # 요약 라인 추가
        for line_idx, line in enumerate(summary_lines[:2]):
            y_offset = 95 + line_idx * 18
            svg += f'    <text x="20" y="{y_offset}" font-family="Arial, sans-serif" font-size="12" fill="#94a3b8">{_escape_svg_text(_to_english_svg_text(line))}</text>\n'

        # 소스 배지
        badge_y = height - 25 if height > 160 else height - 20
        svg += f'''
    <rect x="20" y="{badge_y}" width="100" height="18" rx="9" fill="url(#{gradient})" fill-opacity="0.2"/>
    <text x="70" y="{badge_y + 13}" font-family="Arial, sans-serif" font-size="10" fill="{config["icon_color"]}" text-anchor="middle">{source}</text>
  </g>
'''

    # Footer 섹션
    svg += f'''
  <!-- Footer -->
  <line x1="50" y1="585" x2="1150" y2="585" stroke="#334155" stroke-width="1"/>
  
  <!-- Stats -->
  <g transform="translate(50, 600)">
    <text font-family="Arial, sans-serif" font-size="13" fill="#64748b">{total} News Collected</text>
  </g>
  <g transform="translate(250, 600)">
    <text font-family="Arial, sans-serif" font-size="13" fill="#64748b">{stats.get("security", 0)} Security</text>
  </g>
  <g transform="translate(400, 600)">
    <text font-family="Arial, sans-serif" font-size="13" fill="#64748b">{stats.get("cloud", 0)} Cloud</text>
  </g>
  <g transform="translate(520, 600)">
    <text font-family="Arial, sans-serif" font-size="13" fill="#64748b">{stats.get("devops", 0)} DevOps</text>
  </g>
  <g transform="translate(650, 600)">
    <text font-family="Arial, sans-serif" font-size="13" fill="#64748b">{stats.get("ai", 0)} AI/ML</text>
  </g>
  
  <!-- Blog Info -->
  <text x="1150" y="612" font-family="Arial, sans-serif" font-size="14" font-weight="bold" fill="#94a3b8" text-anchor="end">tech.2twodragon.com</text>
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
    parser.add_argument("--max-news", type=int, default=15, help="Maximum news items")
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

    topics = _extract_key_topics(selected)
    topics_slug = "_".join(topics[:4]) if topics else "News"
    
    post_content = generate_post_content(selected, categorized, now, topics_slug)
    post_filename = f"{date_str}-Tech_Security_Weekly_Digest_{topics_slug}.md"
    post_path = POSTS_DIR / post_filename

    # SVG 이미지 생성
    svg_content = generate_svg_image(now, categorized, selected)
    svg_filename = f"{date_str}-Tech_Security_Weekly_Digest_{topics_slug}.svg"
    svg_path = IMAGES_DIR / svg_filename

    # 기존 포스트 존재 확인 (수동 작성된 고품질 포스트 보호)
    if post_path.exists():
        existing_size = post_path.stat().st_size
        new_size = len(post_content.encode("utf-8"))
        if existing_size > new_size:
            print(f"⏭️ Existing post is larger ({existing_size}B > {new_size}B). Skipping to preserve manual post.")
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
