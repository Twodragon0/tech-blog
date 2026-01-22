#!/usr/bin/env python3
"""
Tech News Draft Generator - 뉴스 초안 생성 스크립트 (Local AI Version)

수집된 뉴스를 기반으로 _posts 수준의 깊이 있는 블로그 포스트 초안을 생성합니다.
로컬 Claude/Cursor와 함께 사용하기 위한 프롬프트를 생성합니다.

Usage:
    # 1단계: 뉴스 수집
    python3 scripts/collect_tech_news.py --hours 24

    # 2단계: 분석 프롬프트 생성
    python3 scripts/generate_news_draft.py --prepare --max-posts 3

    # 3단계: Claude/Cursor에서 프롬프트 실행 (수동)
    # _drafts/prompts/ 폴더의 프롬프트를 복사하여 Claude에 전달

    # 4단계: 결과를 초안으로 저장
    python3 scripts/generate_news_draft.py --finalize
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import frontmatter
import requests
from bs4 import BeautifulSoup


# ============================================================================
# 설정
# ============================================================================

CATEGORY_MAP = {
    "security": "security",
    "cloud": "cloud",
    "tech": "devops",
    "kubernetes": "kubernetes",
    "devops": "devops",
    "devsecops": "devsecops",
}

CATEGORY_EMOJI = {
    "security": "🔒",
    "cloud": "☁️",
    "devops": "⚙️",
    "kubernetes": "🚀",
    "devsecops": "🛡️",
    "incident": "🚨",
    "finops": "💰",
}

TARGET_AUDIENCE = {
    "security": "보안 엔지니어, DevSecOps 엔지니어, SOC 분석가",
    "cloud": "클라우드 아키텍트, SRE, DevOps 엔지니어",
    "devops": "DevOps 엔지니어, SRE, 플랫폼 엔지니어",
    "kubernetes": "쿠버네티스 관리자, 플랫폼 엔지니어, SRE",
    "devsecops": "DevSecOps 엔지니어, 보안 엔지니어, 개발자",
}


# ============================================================================
# 원문 콘텐츠 가져오기
# ============================================================================


def fetch_original_content(url: str) -> str:
    """원문 URL에서 콘텐츠 가져오기"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # 불필요한 요소 제거
        for tag in soup(
            ["script", "style", "nav", "footer", "header", "aside", "iframe"]
        ):
            tag.decompose()

        # 본문 텍스트 추출
        text = soup.get_text(separator="\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)

        return text[:6000].strip()
    except Exception as e:
        print(f"    Warning: Could not fetch content: {e}")
        return ""


# ============================================================================
# 관련 포스트 찾기
# ============================================================================


def find_related_posts(news_item: dict, posts_dir: Path) -> List[dict]:
    """기존 포스트 중 관련된 것 찾기"""
    related = []
    category = news_item.get("category", "")

    try:
        for post_file in sorted(posts_dir.glob("*.md"), reverse=True)[:50]:
            try:
                post = frontmatter.load(post_file)
                post_category = post.get("category", "")
                post_tags = [t.lower() for t in post.get("tags", [])]
                post_title = post.get("title", "")

                # 카테고리 일치
                if post_category == category:
                    related.append(
                        {
                            "title": post_title,
                            "file": post_file.name,
                            "category": post_category,
                            "tags": post.get("tags", [])[:3],
                        }
                    )
                    if len(related) >= 5:
                        break
            except:
                continue
    except:
        pass

    return related


# ============================================================================
# 프롬프트 생성 (Claude/Cursor용)
# ============================================================================


def generate_analysis_prompt(
    news_item: dict, original_content: str, related_posts: List[dict]
) -> str:
    """Claude/Cursor용 분석 프롬프트 생성"""

    category = news_item.get("category", "tech")
    audience = TARGET_AUDIENCE.get(category, "IT 실무자")

    related_info = ""
    if related_posts:
        related_info = "\n### 관련 기존 포스트 (참고용)\n"
        for post in related_posts:
            related_info += f"- **{post['title']}** (카테고리: {post['category']})\n"

    prompt = f"""# 기술 뉴스 블로그 포스트 작성 요청

당신은 DevSecOps 전문 기술 블로거입니다. 다음 기술 뉴스를 바탕으로 **한국어** 블로그 포스트를 작성해주세요.

---

## 뉴스 정보

| 항목 | 내용 |
|------|------|
| **제목** | {news_item["title"]} |
| **원문 URL** | {news_item["url"]} |
| **출처** | {news_item["source_name"]} |
| **카테고리** | {category} |
| **발행일** | {news_item.get("published", "N/A")[:10]} |

### 원문 요약
{news_item.get("summary", "요약 없음")}

### 원문 내용 (발췌)
```
{original_content[:3500] if original_content else "원문을 가져오지 못했습니다. 위 URL을 직접 참조해주세요."}
```
{related_info}

---

## 작성 요구사항

### 1. 포스트 구조 (필수)

```markdown
---
layout: post
title: "한국어 제목 (50자 이내)"
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} +0900
category: {category}
categories: [{category}]
tags: [태그1, 태그2, 태그3, 태그4, 태그5]
excerpt: "150-200자 SEO 요약"
original_url: {news_item["url"]}
original_source: {news_item["source_name"]}
comments: true
toc: true
---

[AI 요약 카드 - 아래 템플릿 사용]

## 서론
(이 뉴스의 중요성과 배경 설명)

## 📊 빠른 참조
(핵심 정보 테이블)

## 1. 개요
### 1.1 배경 및 맥락
### 1.2 핵심 내용

## 2. 기술적 분석
### 2.1 주요 기술 요소
### 2.2 아키텍처/구현 (코드 예시 포함)

## 3. 실무 영향
### 3.1 영향 범위
### 3.2 주의 사항

## 4. 대응 방안
### 4.1 즉시 조치 사항 (테이블)
### 4.2 체크리스트

## 5. 관련 리소스
### 5.1 공식 문서
### 5.2 관련 도구/GitHub 저장소

## 결론
(요약 및 향후 전망)
```

### 2. AI 요약 카드 템플릿 (본문 시작 부분에 추가)

```html
<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">[한국어 제목]</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag {category}">{category.capitalize()}</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">[태그1]</span>
      <span class="tag">[태그2]</span>
      <span class="tag">[태그3]</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>[핵심 포인트 1]</li>
      <li>[핵심 포인트 2]</li>
      <li>[핵심 포인트 3]</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">{audience}</span>
  </div>
</div>
</div>
```

### 3. 품질 요구사항

- **분량**: 본문 2500자 이상
- **언어**: 한국어 (기술 용어는 영어 병기 가능)
- **테이블**: 최소 2개 이상 (빠른 참조, 대응 방안)
- **체크리스트**: 실무자용 행동 항목 5개 이상
- **코드**: 실용적인 코드 예시 1개 이상 (bash, yaml, python 등)
- **링크**: 실제 존재하는 URL만 사용 (공식 문서, GitHub 등)
- **이모지**: 섹션 제목에만 적절히 사용

### 4. 주의사항

- 존재하지 않는 URL 사용 금지
- 추측성 내용 최소화, 원문 기반 작성
- 실무에 바로 적용 가능한 내용 포함
- 한국 독자를 위한 맥락 설명 추가

---

위 요구사항에 맞춰 완전한 블로그 포스트를 작성해주세요. Front matter부터 결론까지 전체를 작성합니다.
"""
    return prompt


# ============================================================================
# 기본 템플릿 생성 (AI 없이)
# ============================================================================


def generate_template_draft(news_item: dict, original_content: str) -> str:
    """기본 템플릿 초안 생성"""

    category = news_item.get("category", "tech")
    audience = TARGET_AUDIENCE.get(category, "IT 실무자")
    emoji = CATEGORY_EMOJI.get(category, "📰")
    title = news_item["title"]
    url = news_item["url"]
    source = news_item["source_name"]
    summary = news_item.get("summary", "")
    pub_date = news_item.get("published", "")[:10]

    content = f"""<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">{title}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag {category}">{category.capitalize()}</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">{category.capitalize()}</span>
      <span class="tag">Tech-News</span>
      <span class="tag">{source.replace(" ", "-")}</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>출처: {source}</li>
      <li>카테고리: {category}</li>
      <li>상세 분석 필요</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">{audience}</span>
  </div>
</div>
</div>

## 서론

{emoji} **{summary if summary else f"{source}에서 발표한 {category} 관련 중요 뉴스입니다."}**

이 포스트에서는 "{title}"에 대해 심층 분석하고 실무 대응 방안을 제시합니다.

## 📊 빠른 참조

| 항목 | 내용 |
|------|------|
| **출처** | [{source}]({url}) |
| **카테고리** | {category} |
| **발행일** | {pub_date} |
| **대상 독자** | {audience} |

## 1. 개요

### 1.1 배경 및 맥락

{source}에서 발표한 이 뉴스는 {category} 분야의 최신 동향을 다루고 있습니다.

> **원문 요약**: {summary if summary else "원문 참조 필요"}

### 1.2 핵심 내용

원문 링크: [{title}]({url})

**원문 발췌:**
```
{original_content[:1500] if original_content else "원문을 가져오지 못했습니다. 위 URL을 직접 참조해주세요."}
```

## 2. 기술적 분석

### 2.1 주요 기술 요소

> **TODO**: 원문을 분석하여 기술적 세부 사항을 추가하세요.

| 기술 요소 | 설명 | 중요도 |
|----------|------|--------|
| - | - | - |

### 2.2 아키텍처/구현

> **TODO**: 관련 코드 예시나 아키텍처 다이어그램을 추가하세요.

```bash
# 예시 명령어
# TODO: 실제 명령어로 교체
```

## 3. 실무 영향

### 3.1 영향 범위

이 뉴스는 다음과 같은 실무자에게 영향을 미칩니다:

- {audience}

### 3.2 주의 사항

| 구분 | 내용 | 우선순위 |
|------|------|----------|
| - | - | - |

## 4. 대응 방안

### 4.1 즉시 조치 사항

| 우선순위 | 조치 항목 | 담당 | 기한 |
|---------|----------|------|------|
| 🔴 높음 | 원문 확인 및 분석 | 담당자 | 즉시 |
| 🟡 중간 | 영향도 평가 | 팀 | 1주 내 |
| 🟢 낮음 | 문서화 | 담당자 | 2주 내 |

### 4.2 체크리스트

- [ ] 원문 내용 상세 확인
- [ ] 우리 환경에 적용 여부 검토
- [ ] 관련 시스템/서비스 영향도 평가
- [ ] 필요시 대응 계획 수립
- [ ] 팀 내 공유 및 교육

## 5. 관련 리소스

### 5.1 공식 문서

- [원문: {title}]({url})

### 5.2 관련 도구/GitHub 저장소

> **TODO**: 관련 도구나 GitHub 저장소 링크를 추가하세요.

## 결론

{source}의 이 뉴스는 {category} 분야에서 중요한 의미를 가집니다. 관련 실무자는 원문을 확인하고 위 체크리스트에 따라 필요한 조치를 취하시기 바랍니다.

---

> ⚠️ **이 포스트는 자동 생성된 초안입니다.**
> 
> 게시 전 다음 사항을 확인하세요:
> 1. 원문을 참조하여 상세 내용 추가
> 2. 기술적 분석 섹션 보강
> 3. 실제 대응 방안 작성
> 4. 관련 레퍼런스 검증
> 5. `draft: true` 제거 후 `_posts/`로 이동

---

## 📚 원문 정보

- **출처**: [{source}]({url})
- **원문 제목**: {title}
- **발행일**: {pub_date}

---

**마지막 업데이트**: {datetime.now().strftime("%Y-%m-%d")}
"""
    return content


def generate_filename(title: str, date: datetime) -> str:
    """영문 파일명 생성"""
    english_title = re.sub(r"[^a-zA-Z0-9\s-]", "", title)
    english_title = re.sub(r"\s+", "_", english_title.strip())

    if len(english_title) > 80:
        english_title = english_title[:80].rsplit("_", 1)[0]

    if not english_title:
        english_title = "Tech_News"

    date_str = date.strftime("%Y-%m-%d")
    return f"{date_str}-{english_title}.md"


def create_frontmatter(news_item: dict, date: datetime) -> dict:
    """Front Matter 생성"""
    category = CATEGORY_MAP.get(news_item["category"], "devops")

    return {
        "layout": "post",
        "title": news_item["title"],
        "date": date.strftime("%Y-%m-%d %H:%M:%S +0900"),
        "category": category,
        "categories": [category],
        "tags": [
            category.capitalize(),
            "Tech-News",
            news_item["source_name"].replace(" ", "-"),
        ],
        "excerpt": news_item.get("summary", "")[:200]
        or f"{news_item['source_name']}에서 발표한 {category} 관련 뉴스입니다.",
        "original_url": news_item["url"],
        "original_source": news_item["source_name"],
        "comments": True,
        "toc": True,
        "auto_generated": True,
        "draft": True,
    }


# ============================================================================
# 메인 함수
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Tech News Draft Generator (Local AI Version)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="_data/collected_news.json",
        help="Input JSON file with collected news",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="_drafts",
        help="Output directory for draft posts",
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=3,
        help="Maximum number of posts to generate (default: 3)",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Filter by category (security, cloud, tech, kubernetes, devops)",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Generate prompts for Claude/Cursor analysis",
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Generate template drafts (without AI analysis)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without saving",
    )

    args = parser.parse_args()

    # 프로젝트 루트
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # 입력 파일 확인
    input_path = project_root / args.input
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        print("Run 'python3 scripts/collect_tech_news.py' first.")
        sys.exit(1)

    # 뉴스 데이터 로드
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    print(f"\n📰 Loaded {len(items)} news items")

    # 카테고리 필터링
    if args.category:
        items = [item for item in items if item["category"] == args.category]
        print(f"   Filtered to {len(items)} items in category '{args.category}'")

    # 최대 개수 제한
    items = items[: args.max_posts]

    if not items:
        print("No items to process.")
        return

    # 출력 디렉토리
    output_dir = project_root / args.output_dir
    prompts_dir = output_dir / "prompts"
    posts_dir = project_root / "_posts"

    # 모드 결정
    if args.prepare:
        mode = "prepare"
        print(f"\n🔧 Mode: Preparing prompts for Claude/Cursor")
    elif args.template:
        mode = "template"
        print(f"\n📝 Mode: Generating template drafts")
    else:
        mode = "template"  # 기본값
        print(
            f"\n📝 Mode: Generating template drafts (use --prepare for Claude prompts)"
        )

    print(f"📁 Output: {output_dir}")
    print(f"{'=' * 60}\n")

    generated = []
    processed_ids = []

    for i, item in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {item['title'][:55]}...")

        # 원문 콘텐츠 가져오기
        print("    Fetching original content...")
        original_content = fetch_original_content(item["url"])
        if original_content:
            print(f"    ✅ Fetched {len(original_content)} chars")
        else:
            print(f"    ⚠️ Could not fetch content")

        # 관련 포스트 찾기
        related_posts = find_related_posts(item, posts_dir)
        if related_posts:
            print(f"    📎 Found {len(related_posts)} related posts")

        # 날짜
        try:
            pub_date = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
        except:
            pub_date = datetime.now(timezone.utc)

        # 파일명 생성
        filename = generate_filename(item["title"], pub_date)

        if mode == "prepare":
            # 프롬프트 생성
            prompt = generate_analysis_prompt(item, original_content, related_posts)

            if args.dry_run:
                print(
                    f"    Would create prompt: prompts/{filename.replace('.md', '_prompt.md')}"
                )
            else:
                prompts_dir.mkdir(parents=True, exist_ok=True)
                prompt_file = prompts_dir / filename.replace(".md", "_prompt.md")
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.write(prompt)
                print(f"    ✅ Created: prompts/{prompt_file.name}")
                generated.append(prompt_file)

        else:  # template mode
            # 템플릿 초안 생성
            fm = create_frontmatter(item, pub_date)
            content = generate_template_draft(item, original_content)

            if args.dry_run:
                print(f"    Would create: {filename}")
            else:
                output_dir.mkdir(parents=True, exist_ok=True)

                post = frontmatter.Post(content)
                post.metadata = fm

                output_path = output_dir / filename
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(frontmatter.dumps(post))

                print(f"    ✅ Created: {filename} ({len(content)} chars)")
                generated.append(output_path)

        processed_ids.append(item["id"])

    # 처리된 ID 저장
    if not args.dry_run and processed_ids:
        processed_file = project_root / "_data" / "processed_news_ids.json"
        existing_ids = set()

        if processed_file.exists():
            with open(processed_file, "r", encoding="utf-8") as f:
                existing_ids = set(json.load(f))

        existing_ids.update(processed_ids)

        processed_file.parent.mkdir(parents=True, exist_ok=True)
        with open(processed_file, "w", encoding="utf-8") as f:
            json.dump(list(existing_ids), f)

    # 결과 요약
    print(f"\n{'=' * 60}")
    print("📊 Summary")
    print(f"{'=' * 60}")
    print(f"Processed: {len(items)} items")

    if not args.dry_run:
        print(f"Generated: {len(generated)} files")
        print()

        if mode == "prepare":
            print("🚀 Next steps:")
            print(f"   1. Open prompts in {prompts_dir}/")
            print("   2. Copy prompt content to Claude/Cursor")
            print("   3. Ask Claude to generate the blog post")
            print("   4. Save the result as a .md file in _drafts/")
            print("   5. Review and move to _posts/ when ready")
        else:
            print("🚀 Next steps:")
            print("   1. Review drafts in _drafts/")
            print("   2. Use Claude/Cursor to enhance content:")
            print(f"      - Run: python3 scripts/generate_news_draft.py --prepare")
            print("      - Or ask Claude directly to improve each draft")
            print("   3. Add images if needed")
            print("   4. Remove 'draft: true' from front matter")
            print("   5. Move to _posts/ when ready")


if __name__ == "__main__":
    main()
