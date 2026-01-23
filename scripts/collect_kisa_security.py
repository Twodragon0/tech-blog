#!/usr/bin/env python3
"""
KISA 보호나라 보안공지 수집 스크립트

KISA 보호나라(https://www.boho.or.kr)의 보안공지를 수집하고,
관련 CVE/취약점 정보, 레퍼런스를 매핑하여 블로그 초안을 생성합니다.

Usage:
    python3 scripts/collect_kisa_security.py
    python3 scripts/collect_kisa_security.py --days 7
    python3 scripts/collect_kisa_security.py --generate-draft
"""

import os
import re
import json
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("필수 패키지를 설치하세요: pip install requests beautifulsoup4")
    exit(1)


# 상수 정의
KISA_BASE_URL = "https://www.boho.or.kr"
KISA_SECURITY_LIST_URL = f"{KISA_BASE_URL}/kr/bbs/list.do"
KISA_SECURITY_VIEW_URL = f"{KISA_BASE_URL}/kr/bbs/view.do"
DATA_DIR = Path("_data")
DRAFTS_DIR = Path("_drafts")
CACHE_FILE = DATA_DIR / "kisa_security_notices.json"

# CVE 관련 레퍼런스 매핑
CVE_REFERENCES = {
    "nvd": "https://nvd.nist.gov/vuln/detail/",
    "mitre": "https://cve.mitre.org/cgi-bin/cvename.cgi?name=",
    "cvedetails": "https://www.cvedetails.com/cve/",
}

# 벤더별 보안 공지 URL 매핑
VENDOR_SECURITY_URLS = {
    "microsoft": "https://msrc.microsoft.com/update-guide/",
    "ms": "https://msrc.microsoft.com/update-guide/",
    "adobe": "https://helpx.adobe.com/security.html",
    "apple": "https://support.apple.com/en-us/HT201222",
    "google": "https://www.google.com/about/appsecurity/",
    "chrome": "https://chromereleases.googleblog.com/",
    "oracle": "https://www.oracle.com/security-alerts/",
    "cisco": "https://tools.cisco.com/security/center/publicationListing.x",
    "vmware": "https://www.vmware.com/security/advisories.html",
    "fortinet": "https://www.fortiguard.com/psirt",
    "paloalto": "https://security.paloaltonetworks.com/",
    "juniper": "https://supportportal.juniper.net/s/security-advisories",
    "f5": "https://my.f5.com/manage/s/article/K00000000",
    "atlassian": "https://www.atlassian.com/trust/security/advisories",
    "jenkins": "https://www.jenkins.io/security/advisories/",
    "apache": "https://httpd.apache.org/security/vulnerabilities.html",
    "nginx": "https://nginx.org/en/security_advisories.html",
    "linux": "https://www.kernel.org/category/releases.html",
    "redhat": "https://access.redhat.com/security/security-updates/",
    "ubuntu": "https://ubuntu.com/security/notices",
    "debian": "https://www.debian.org/security/",
    "mongodb": "https://www.mongodb.com/alerts",
    "postgresql": "https://www.postgresql.org/support/security/",
    "mysql": "https://www.oracle.com/security-alerts/",
    "wordpress": "https://wordpress.org/news/category/security/",
    "drupal": "https://www.drupal.org/security",
    "tp-link": "https://www.tp-link.com/us/support/security-advisory/",
    "hpe": "https://support.hpe.com/hpesc/public/home",
    "trendmicro": "https://success.trendmicro.com/dcx/s/vulnerability-response",
    "trend micro": "https://success.trendmicro.com/dcx/s/vulnerability-response",
    "n8n": "https://github.com/n8n-io/n8n/security/advisories",
    "airoha": "https://www.airoha.com/",
}

# 카테고리 키워드 매핑
CATEGORY_KEYWORDS = {
    "ransomware": ["랜섬웨어", "ransomware", "암호화", "복호화"],
    "phishing": ["피싱", "phishing", "스미싱", "smishing", "큐싱", "quishing"],
    "vulnerability": ["취약점", "vulnerability", "CVE", "보안 업데이트"],
    "malware": ["악성코드", "malware", "트로이목마", "백도어"],
    "apt": ["APT", "지능형 지속 위협", "타깃 공격"],
    "ddos": ["DDoS", "디도스", "서비스 거부"],
    "data_breach": ["정보유출", "개인정보", "데이터 유출"],
}


@dataclass
class SecurityNotice:
    """보안 공지 데이터 클래스"""

    id: str
    title: str
    date: str
    url: str
    views: int
    has_attachment: bool
    content: Optional[str] = None
    cves: Optional[List[str]] = None
    vendor: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[str] = None
    references: Optional[List[Dict[str, str]]] = None


def mask_sensitive_info(text: str) -> str:
    """민감 정보 마스킹"""
    patterns = [
        (
            r'(api[_-]?key|token|secret|password|pwd)\s*[=:]\s*["\']?[\w-]+["\']?',
            r"\1=***MASKED***",
        ),
        (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "***IP_MASKED***"),
    ]
    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def safe_log(message: str, level: str = "INFO") -> None:
    """안전한 로그 출력"""
    safe_message = mask_sensitive_info(message)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {safe_message}")


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    )
    session.verify = False
    return session


def fetch_security_notices(
    session: requests.Session, page: int = 1
) -> List[SecurityNotice]:
    """KISA 보안공지 목록 수집"""
    notices = []

    params = {
        "menuNo": "205020",
        "bbsId": "B0000133",
        "pageIndex": page,
    }

    try:
        response = session.get(KISA_SECURITY_LIST_URL, params=params, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 게시물 테이블 파싱
        rows = soup.select("table tbody tr")

        for row in rows:
            try:
                # 제목 링크 추출
                title_link = row.select_one("td a")
                if not title_link:
                    continue

                title = title_link.get_text(strip=True)
                href = title_link.get("href", "")

                ntt_id_match = re.search(r"nttId=(\d+)", str(href))
                ntt_id = ntt_id_match.group(1) if ntt_id_match else ""

                # 조회수 추출
                views_td = row.select("td")
                views = 0
                if len(views_td) >= 3:
                    views_text = views_td[-2].get_text(strip=True)
                    views = (
                        int(views_text.replace(",", ""))
                        if views_text.isdigit() or "," in views_text
                        else 0
                    )

                # 날짜 추출
                date_td = views_td[-1] if views_td else None
                date_str = date_td.get_text(strip=True) if date_td else ""

                # 첨부파일 여부
                has_attachment = bool(row.select_one("img[src*='attach']"))

                # 전체 URL 생성
                full_url = f"{KISA_BASE_URL}/kr/bbs/view.do?menuNo=205020&bbsId=B0000133&nttId={ntt_id}"

                notice = SecurityNotice(
                    id=ntt_id,
                    title=title,
                    date=date_str,
                    url=full_url,
                    views=views,
                    has_attachment=has_attachment,
                )

                # 벤더 추출
                notice.vendor = extract_vendor(title)

                # 카테고리 분류
                notice.category = classify_category(title)

                notices.append(notice)

            except Exception as e:
                safe_log(f"Row parsing error: {e}", "WARNING")
                continue

    except requests.RequestException as e:
        safe_log(f"Failed to fetch notices: {e}", "ERROR")

    return notices


def fetch_notice_detail(
    session: requests.Session, notice: SecurityNotice
) -> SecurityNotice:
    """개별 보안공지 상세 내용 수집"""
    try:
        response = session.get(notice.url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 본문 내용 추출
        content_div = soup.select_one(".board_view_con") or soup.select_one(
            ".view_content"
        )
        if content_div:
            notice.content = content_div.get_text(separator="\n", strip=True)

        # CVE 번호 추출
        if notice.content:
            cve_pattern = r"CVE-\d{4}-\d{4,7}"
            cves = re.findall(cve_pattern, notice.content, re.IGNORECASE)
            notice.cves = list(set(cves)) if cves else None

        # 심각도 추출 시도
        notice.severity = extract_severity(notice.content or notice.title)

        # 레퍼런스 생성
        notice.references = generate_references(notice)

    except requests.RequestException as e:
        safe_log(f"Failed to fetch detail for {notice.id}: {e}", "WARNING")

    return notice


def extract_vendor(title: str) -> Optional[str]:
    """제목에서 벤더 추출"""
    title_lower = title.lower()

    for vendor, url in VENDOR_SECURITY_URLS.items():
        if vendor.lower() in title_lower:
            return vendor.title()

    return None


def classify_category(title: str) -> str:
    """제목 기반 카테고리 분류"""
    title_lower = title.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in title_lower:
                return category

    if "업데이트" in title or "update" in title_lower:
        return "vulnerability"

    return "security"


def extract_severity(text: str) -> Optional[str]:
    """심각도 추출"""
    text_lower = text.lower()

    if any(word in text_lower for word in ["긴급", "critical", "심각"]):
        return "Critical"
    elif any(word in text_lower for word in ["높음", "high", "중요"]):
        return "High"
    elif any(word in text_lower for word in ["보통", "medium", "중간"]):
        return "Medium"
    elif any(word in text_lower for word in ["낮음", "low"]):
        return "Low"

    return None


def generate_references(notice: SecurityNotice) -> List[Dict[str, str]]:
    """보안공지에 대한 레퍼런스 URL 생성"""
    references = []

    # KISA 원본 링크
    references.append(
        {
            "name": "KISA 보안공지",
            "url": notice.url,
        }
    )

    # CVE 레퍼런스
    if notice.cves:
        for cve in notice.cves[:5]:  # 최대 5개
            references.append(
                {
                    "name": f"NVD - {cve}",
                    "url": f"{CVE_REFERENCES['nvd']}{cve}",
                }
            )

    # 벤더 보안 페이지
    if notice.vendor:
        vendor_lower = notice.vendor.lower()
        if vendor_lower in VENDOR_SECURITY_URLS:
            references.append(
                {
                    "name": f"{notice.vendor} Security",
                    "url": VENDOR_SECURITY_URLS[vendor_lower],
                }
            )

    return references


def collect_notices(days: int = 30, max_pages: int = 3) -> List[SecurityNotice]:
    """보안공지 수집 (최근 N일)"""
    session = get_session()
    all_notices = []
    cutoff_date = datetime.now() - timedelta(days=days)

    safe_log(f"Collecting KISA security notices (last {days} days)...")

    for page in range(1, max_pages + 1):
        notices = fetch_security_notices(session, page)

        if not notices:
            break

        for notice in notices:
            try:
                # 날짜 파싱
                notice_date = datetime.strptime(notice.date, "%Y-%m-%d")

                if notice_date < cutoff_date:
                    safe_log(f"Reached cutoff date at page {page}")
                    return all_notices

                # 상세 정보 수집
                notice = fetch_notice_detail(session, notice)
                all_notices.append(notice)

                safe_log(f"Collected: {notice.title[:50]}...")

            except ValueError:
                # 공지사항 (날짜 없음) 스킵
                continue

    return all_notices


def save_notices(notices: List[SecurityNotice]) -> None:
    """수집한 보안공지 저장"""
    DATA_DIR.mkdir(exist_ok=True)

    data = {
        "collected_at": datetime.now().isoformat(),
        "count": len(notices),
        "notices": [asdict(n) for n in notices],
    }

    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    safe_log(f"Saved {len(notices)} notices to {CACHE_FILE}")


def load_cached_notices() -> List[SecurityNotice]:
    """캐시된 보안공지 로드"""
    if not CACHE_FILE.exists():
        return []

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        notices = []
        for item in data.get("notices", []):
            notices.append(SecurityNotice(**item))

        return notices
    except Exception as e:
        safe_log(f"Failed to load cache: {e}", "WARNING")
        return []


def generate_blog_draft(notice: SecurityNotice) -> Tuple[str, str]:
    """보안공지 기반 블로그 초안 생성"""

    # 파일명용 영문 제목 생성
    title_slug = re.sub(r"[^\w\s-]", "", notice.title)
    title_slug = re.sub(r"\s+", "_", title_slug)[:50]

    # 태그 생성
    tags = ["KISA", "Security", "보안공지"]
    if notice.vendor:
        tags.append(notice.vendor)
    if notice.cves:
        tags.extend(notice.cves[:3])
    if notice.category:
        tags.append(notice.category.title())

    # 카테고리 결정
    category = "security"
    if notice.category == "ransomware":
        category = "incident"
    elif notice.category in ["vulnerability"]:
        category = "devsecops"

    # CVE 섹션 생성
    cve_section = ""
    if notice.cves:
        cve_section = "\n## CVE 정보\n\n"
        cve_section += "| CVE ID | NVD 링크 |\n"
        cve_section += "|--------|----------|\n"
        for cve in notice.cves[:10]:
            cve_section += f"| {cve} | [NVD]({CVE_REFERENCES['nvd']}{cve}) |\n"

    # 레퍼런스 섹션 생성
    ref_section = "\n## 참고 자료\n\n"
    if notice.references:
        for ref in notice.references:
            ref_section += f"- [{ref['name']}]({ref['url']})\n"

    # 대응 방안 섹션
    response_section = """
## 대응 방안

### 즉시 조치 사항
1. 영향받는 시스템 확인
2. 보안 패치 적용
3. 시스템 모니터링 강화

### 장기 대응
1. 정기적인 보안 업데이트 점검
2. 취약점 스캔 도구 활용
3. 보안 정책 검토 및 업데이트
"""

    # 초안 내용 생성
    content = f'''---
layout: post
title: "{notice.title}"
date: {notice.date} 09:00:00 +0900
category: {category}
categories: [{category}, security]
tags: [{", ".join(tags)}]
excerpt: "KISA 보안공지 - {notice.title[:100]}"
image: /assets/images/{notice.date}-KISA_Security_Notice.svg
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">KISA 보안공지</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">{notice.title}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">공지일</span>
    <span class="summary-value">{notice.date}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">심각도</span>
    <span class="summary-value">{notice.severity or "확인 필요"}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">영향 벤더</span>
    <span class="summary-value">{notice.vendor or "여러 벤더"}</span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>KISA 보안공지 기반 보안 위협 분석</li>
      <li>영향받는 시스템 및 대응 방안 안내</li>
      <li>관련 CVE 및 레퍼런스 정리</li>
    </ul>
  </div>
</div>
</div>

## 개요

{notice.content[:500] if notice.content else notice.title}...

> **원본 공지**: [{notice.title}]({notice.url})

{cve_section}

{response_section}

{ref_section}

## 마무리

보안 위협에 대한 신속한 대응이 중요합니다. KISA 보안공지를 정기적으로 확인하고, 
관련 시스템에 대한 보안 패치를 적용하시기 바랍니다.

---

> **면책 조항**: 본 포스팅은 KISA 보안공지를 바탕으로 작성되었으며, 
> 상세한 기술 정보는 원본 공지를 참조하시기 바랍니다.
'''

    return content, title_slug


def generate_drafts(notices: List[SecurityNotice], max_drafts: int = 5) -> List[Path]:
    """블로그 초안 파일 생성"""
    DRAFTS_DIR.mkdir(exist_ok=True)

    generated_files = []

    for notice in notices[:max_drafts]:
        content, title_slug = generate_blog_draft(notice)

        # 파일명 생성
        filename = f"{notice.date}-KISA_{title_slug}.md"
        filepath = DRAFTS_DIR / filename

        # 파일 저장
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        generated_files.append(filepath)
        safe_log(f"Generated draft: {filepath}")

    return generated_files


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="KISA 보안공지 수집 및 블로그 초안 생성"
    )
    parser.add_argument("--days", type=int, default=30, help="수집 기간 (일)")
    parser.add_argument("--pages", type=int, default=3, help="수집할 페이지 수")
    parser.add_argument(
        "--generate-draft", action="store_true", help="블로그 초안 생성"
    )
    parser.add_argument("--max-drafts", type=int, default=5, help="생성할 초안 수")
    parser.add_argument("--use-cache", action="store_true", help="캐시된 데이터 사용")

    args = parser.parse_args()

    # 보안공지 수집
    if args.use_cache:
        notices = load_cached_notices()
        if not notices:
            safe_log("No cached data found, collecting fresh data...")
            notices = collect_notices(args.days, args.pages)
            save_notices(notices)
    else:
        notices = collect_notices(args.days, args.pages)
        save_notices(notices)

    safe_log(f"Total notices collected: {len(notices)}")

    # 블로그 초안 생성
    if args.generate_draft:
        drafts = generate_drafts(notices, args.max_drafts)
        safe_log(f"Generated {len(drafts)} draft files")

        print("\n생성된 초안 파일:")
        for draft in drafts:
            print(f"  - {draft}")

    # 요약 출력
    print("\n=== 수집된 보안공지 요약 ===")
    for notice in notices[:10]:
        cve_info = f" ({len(notice.cves)} CVEs)" if notice.cves else ""
        print(f"- [{notice.date}] {notice.title[:60]}...{cve_info}")


if __name__ == "__main__":
    main()
