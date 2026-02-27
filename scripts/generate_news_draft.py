#!/usr/bin/env python3
"""
Tech News Draft Generator - 뉴스 초안 생성 스크립트 (Enhanced Version)

수집된 뉴스를 기반으로 _posts 수준의 깊이 있는 블로그 포스트 초안을 생성합니다.
로컬 Claude/Cursor와 함께 사용하기 위한 상세 프롬프트를 생성합니다.

Usage:
    # 1단계: 뉴스 수집
    python3 scripts/collect_tech_news.py --hours 24

    # 2단계: 분석 프롬프트 생성
    python3 scripts/generate_news_draft.py --prepare --max-posts 3

    # 3단계: Claude/Cursor에서 프롬프트 실행
    # _drafts/prompts/ 폴더의 프롬프트를 복사하여 Claude에 전달
    # 또는 직접 Claude에게 "이 프롬프트 파일을 읽고 포스트를 작성해줘" 요청
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

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

CATEGORY_CONTEXT = {
    "security": """
보안 뉴스는 다음 관점에서 분석해주세요:
- 공격 기법 및 TTP (Tactics, Techniques, Procedures)
- 취약점 유형 (CVE, CWE 등)
- 영향받는 시스템/소프트웨어
- IoC (Indicators of Compromise) 가능하면 포함
- MITRE ATT&CK 프레임워크 매핑
- 방어 전략 및 탐지 방법
- CISA, NIST 등 공식 가이드라인 참조
""",
    "cloud": """
클라우드 뉴스는 다음 관점에서 분석해주세요:
- AWS/GCP/Azure 특정 서비스 관련성
- 아키텍처 변경 사항
- 비용 영향 (FinOps 관점)
- 보안 영향 (Shared Responsibility Model)
- 마이그레이션 고려사항
- Well-Architected Framework 관점
""",
    "kubernetes": """
쿠버네티스 뉴스는 다음 관점에서 분석해주세요:
- K8s 버전 호환성
- CRD, Operator 관련 변경
- 네트워크 정책 영향
- RBAC 및 보안 컨텍스트
- Helm 차트 업데이트 필요성
- GitOps 워크플로우 영향
""",
    "devops": """
DevOps 뉴스는 다음 관점에서 분석해주세요:
- CI/CD 파이프라인 영향
- IaC (Infrastructure as Code) 관련성
- 자동화 기회
- 모니터링 및 관찰성
- SRE 실무 적용점
- 개발 생산성 향상 방안
""",
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
        response = requests.get(url, headers=headers, timeout=15, verify=False)
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

        return text[:8000].strip()
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
    title_words = set(news_item.get("title", "").lower().split())

    try:
        for post_file in sorted(posts_dir.glob("*.md"), reverse=True)[:100]:
            try:
                with open(post_file, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                post_category = str(post.get("category", ""))
                raw_tags = post.get("tags", [])
                post_tags = [
                    str(t).lower()
                    for t in (raw_tags if isinstance(raw_tags, list) else [])
                    if t
                ]
                post_title = str(post.get("title", ""))
                post_excerpt = str(post.get("excerpt", ""))

                # 카테고리 일치 또는 키워드 일치
                score = 0
                if post_category == category:
                    score += 2

                # 태그 일치
                news_tags = [t.lower() for t in news_item.get("tags", [])]
                matching_tags = set(post_tags) & set(news_tags)
                score += len(matching_tags)

                # 제목 단어 일치
                post_title_words = set(post_title.lower().split())
                matching_words = title_words & post_title_words
                score += len(matching_words) * 0.5

                if score >= 1:
                    tags_raw = post.get("tags", [])
                    tags_slice = post_tags[:5] if post_tags else []
                    related.append(
                        {
                            "title": post_title,
                            "file": post_file.name,
                            "category": post_category,
                            "tags": tags_slice,
                            "excerpt": post_excerpt[:200] if post_excerpt else "",
                            "score": score,
                        }
                    )
            except:
                continue
    except:
        pass

    # 점수순 정렬
    related.sort(key=lambda x: x.get("score", 0), reverse=True)
    return related[:5]


# ============================================================================
# 상세 프롬프트 생성 (Claude/Cursor용)
# ============================================================================


def generate_detailed_prompt(
    news_item: dict, original_content: str, related_posts: List[dict]
) -> str:
    """Claude/Cursor용 상세 분석 프롬프트 생성"""

    category = news_item.get("category", "tech")
    blog_category = CATEGORY_MAP.get(category, "devops")
    audience = TARGET_AUDIENCE.get(category, "IT 실무자")
    category_context = CATEGORY_CONTEXT.get(category, "")
    emoji = CATEGORY_EMOJI.get(blog_category, "📰")

    # 관련 포스트 정보
    related_info = ""
    if related_posts:
        related_info = """
### 🔗 관련 기존 포스트 (연관성 분석 및 참조용)

다음 기존 포스트들과의 연관성을 분석하고, 적절히 참조하거나 링크를 포함해주세요:

"""
        for i, post in enumerate(related_posts, 1):
            related_info += f"""**{i}. {post["title"]}**
- 파일: `{post["file"]}`
- 카테고리: {post["category"]}
- 태그: {", ".join(post["tags"])}
- 요약: {post["excerpt"][:150]}...

"""

    prompt = f"""# 📝 기술 뉴스 심층 분석 블로그 포스트 작성 요청

당신은 **Twodragon의 Tech Blog**의 DevSecOps 전문 기술 블로거입니다.
다음 기술 뉴스를 바탕으로 **_posts 폴더의 기존 포스트 수준**의 깊이 있는 한국어 블로그 포스트를 작성해주세요.

---

## 📰 뉴스 정보

| 항목 | 내용 |
|------|------|
| **제목** | {news_item["title"]} |
| **원문 URL** | {news_item["url"]} |
| **출처** | {news_item["source_name"]} |
| **카테고리** | {category} → 블로그 카테고리: `{blog_category}` |
| **발행일** | {news_item.get("published", "N/A")[:10]} |
| **대상 독자** | {audience} |

### 원문 요약
{news_item.get("summary", "요약 없음")}

### 원문 내용 (발췌)
```
{original_content[:5000] if original_content else "원문을 가져오지 못했습니다. 위 URL을 직접 방문하여 내용을 확인하고 분석해주세요."}
```
{related_info}

---

## 📋 카테고리별 분석 가이드

{category_context if category_context else "일반적인 기술 분석 관점에서 작성해주세요."}

---

## 🎯 작성 요구사항 (매우 중요!)

### 분량 요구사항
- **최소 3000자 이상** (코드 제외)
- **테이블 최소 3개 이상** (빠른 참조, 비교 분석, 대응 방안 등)
- **코드 예시 최소 2개 이상** (실제 동작하는 코드)
- **체크리스트 1개 이상** (실무 활용)

### 콘텐츠 품질 요구사항
1. **심층 분석**: 단순 요약이 아닌, 기술적 깊이 있는 분석
2. **실무 관점**: 실제 업무에 어떻게 적용할지 구체적 가이드
3. **맥락 제공**: 이 뉴스가 나온 배경, 업계 동향과의 연관성
4. **비판적 시각**: 장단점, 주의사항, 한계점 분석
5. **액션 아이템**: 독자가 바로 실행할 수 있는 구체적 조치

---

## 📄 포스트 구조 (이 구조를 정확히 따라주세요)

```markdown
---
layout: post
title: "한국어 제목 (원문의 핵심을 살린 자연스러운 번역, 50자 이내)"
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} +0900
category: {blog_category}
categories: [{blog_category}]
tags: [태그1, 태그2, 태그3, 태그4, 태그5, 태그6]
excerpt: "이 포스트의 핵심 내용을 담은 SEO 최적화 요약 (150-200자)"
original_url: {news_item["url"]}
original_source: {news_item["source_name"]}
comments: true
toc: true
---

[아래 AI 요약 카드 HTML을 여기에 삽입]

## 서론

안녕하세요, **Twodragon**입니다.

[이 뉴스의 중요성, 왜 주목해야 하는지, 업계 맥락에서의 의미 설명]
[최근 관련 동향과 연결]
[이 포스트에서 다룰 내용 예고]

## 📊 빠른 참조

### 핵심 요약

| 항목 | 내용 |
|------|------|
| **주요 내용** | [핵심 내용 1줄 요약] |
| **영향 범위** | [영향받는 시스템/서비스/사용자] |
| **심각도** | [높음/중간/낮음 + 이유] |
| **즉시 조치** | [필요/권장/불필요] |
| **관련 기술** | [관련 기술 스택] |

### [추가 비교/분석 테이블]

| 비교 항목 | 이전 | 이후/현재 | 영향 |
|----------|------|----------|------|
| ... | ... | ... | ... |

## 1. 개요

### 1.1 배경 및 맥락

[이 뉴스가 나온 배경]
[관련 업계 동향]
[이전 사건/발표와의 연관성]

### 1.2 핵심 내용 분석

[뉴스의 핵심 내용을 상세히 분석]
[기술적 세부사항]
[관련 수치/데이터 분석]

## 2. 기술적 분석

### 2.1 주요 기술 요소

[핵심 기술 개념 설명]
[아키텍처/구조 분석]

| 기술 요소 | 설명 | 중요도 |
|----------|------|--------|
| ... | ... | ... |

### 2.2 구현/코드 예시

[실제 적용 가능한 코드 예시]

```bash
# 예시: 관련 명령어나 스크립트
# 실제 동작하는 코드로 작성
```

```python
# 예시: Python 코드 (해당되는 경우)
# 실제 동작하는 코드로 작성
```

### 2.3 아키텍처/플로우

[관련 아키텍처나 플로우 설명]
[가능하면 다이어그램 설명]

## 3. 실무 영향

### 3.1 영향 범위

[누가 영향을 받는지]
[어떤 시스템/서비스가 영향을 받는지]
[비즈니스 영향]

### 3.2 주의 사항

| 구분 | 내용 | 우선순위 |
|------|------|----------|
| [주의사항1] | [상세 내용] | 🔴 높음 |
| [주의사항2] | [상세 내용] | 🟡 중간 |
| [주의사항3] | [상세 내용] | 🟢 낮음 |

## 4. 대응 방안

### 4.1 즉시 조치 사항

| 우선순위 | 조치 항목 | 담당 | 예상 소요 |
|---------|----------|------|----------|
| 🔴 Critical | [조치1] | [담당팀] | [시간] |
| 🟡 High | [조치2] | [담당팀] | [시간] |
| 🟢 Medium | [조치3] | [담당팀] | [시간] |

### 4.2 실무 체크리스트

- [ ] [체크항목 1: 구체적인 액션]
- [ ] [체크항목 2: 구체적인 액션]
- [ ] [체크항목 3: 구체적인 액션]
- [ ] [체크항목 4: 구체적인 액션]
- [ ] [체크항목 5: 구체적인 액션]

### 4.3 장기 대응 전략

[장기적인 관점에서의 대응 방안]
[프로세스 개선 제안]
[모니터링/자동화 방안]

## 5. 관련 리소스

### 5.1 공식 문서 및 레퍼런스

- [원문: {news_item["title"]}]({news_item["url"]})
- [관련 공식 문서 1](URL) - 설명
- [관련 공식 문서 2](URL) - 설명

### 5.2 관련 도구 및 GitHub 저장소

| 도구/저장소 | 용도 | 링크 |
|------------|------|------|
| [도구명] | [용도 설명] | [GitHub URL] |

### 5.3 추가 학습 자료

- [관련 강의/튜토리얼]
- [관련 서적/문서]

## 결론

[이 뉴스의 핵심 시사점 요약]
[실무자에게 주는 의미]
[향후 전망 및 주시해야 할 부분]
[마무리 멘트]

---

**마지막 업데이트**: {datetime.now().strftime("%Y-%m-%d")}
```

---

## 🎨 AI 요약 카드 HTML (본문 시작 부분에 삽입)

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
    <span class="summary-value"><span class="category-tag {blog_category}">{blog_category.capitalize()}</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">[태그1]</span>
      <span class="tag">[태그2]</span>
      <span class="tag">[태그3]</span>
      <span class="tag">[태그4]</span>
      <span class="tag">[태그5]</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>[핵심1 제목]</strong>: [핵심1 내용 설명]</li>
      <li><strong>[핵심2 제목]</strong>: [핵심2 내용 설명]</li>
      <li><strong>[핵심3 제목]</strong>: [핵심3 내용 설명]</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">[관련 기술 및 도구 나열]</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">{audience}</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>
```

---

## ⚠️ 주의사항

1. **실제 존재하는 URL만 사용**: 가짜 URL 절대 금지, 확실하지 않으면 생략
2. **코드는 실행 가능해야 함**: 문법 오류 없는 실제 동작 코드
3. **한국어로 작성**: 기술 용어는 영어 병기 가능 (예: 쿠버네티스 (Kubernetes))
4. **이모지는 섹션 제목에만**: 본문에는 이모지 최소화
5. **추측 금지**: 확실하지 않은 내용은 "추가 확인 필요" 명시
6. **저작권 주의**: 원문 직접 인용은 최소화, 분석/재해석 중심

---

## ✅ 최종 체크리스트

포스트 작성 완료 후 다음을 확인하세요:

- [ ] 분량이 3000자 이상인가?
- [ ] 테이블이 3개 이상 포함되어 있는가?
- [ ] 실행 가능한 코드 예시가 2개 이상인가?
- [ ] 체크리스트가 포함되어 있는가?
- [ ] AI 요약 카드가 올바르게 작성되었는가?
- [ ] 모든 링크가 실제 존재하는가?
- [ ] 한국어가 자연스러운가?
- [ ] Front matter가 올바른 형식인가?

---

위 요구사항에 맞춰 **완전한 블로그 포스트**를 작성해주세요.
Front matter부터 결론까지 전체를 작성하며, 기존 _posts 폴더의 포스트들과 동일한 품질 수준을 유지해주세요.
"""
    return prompt


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


# ============================================================================
# 메인 함수
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Tech News Draft Generator (Enhanced Version)"
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
        help="Generate detailed prompts for Claude/Cursor analysis",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without saving",
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Backward-compatible flag (deprecated, prompts are generated regardless)",
    )

    args = parser.parse_args()

    if args.use_ai:
        print(
            "ℹ️ '--use-ai' is deprecated in this script. Generating prompts for AI-assisted writing."
        )

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

    print("\n🔧 Mode: Generating detailed prompts for Claude/Cursor")
    print(f"📁 Output: {prompts_dir}")
    print(f"{'=' * 60}\n")

    generated = []
    processed_ids = []

    # SSL 경고 무시
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    for i, item in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {item['title'][:55]}...")

        # 원문 콘텐츠 가져오기
        print("    📥 Fetching original content...")
        original_content = fetch_original_content(item["url"])
        if original_content:
            print(f"    ✅ Fetched {len(original_content)} chars")
        else:
            print("    ⚠️ Could not fetch content (will use summary only)")

        # 관련 포스트 찾기
        related_posts = find_related_posts(item, posts_dir)
        if related_posts:
            print(f"    🔗 Found {len(related_posts)} related posts")
            for rp in related_posts[:3]:
                print(f"       - {rp['title'][:40]}...")

        # 날짜
        try:
            pub_date = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
        except:
            pub_date = datetime.now(timezone.utc)

        # 파일명 생성
        filename = generate_filename(item["title"], pub_date)

        # 상세 프롬프트 생성
        prompt = generate_detailed_prompt(item, original_content, related_posts)

        if args.dry_run:
            print(
                f"    Would create prompt: prompts/{filename.replace('.md', '_prompt.md')}"
            )
            print(f"    Prompt length: {len(prompt)} chars")
        else:
            prompts_dir.mkdir(parents=True, exist_ok=True)
            prompt_file = prompts_dir / filename.replace(".md", "_prompt.md")
            with open(prompt_file, "w", encoding="utf-8") as f:
                f.write(prompt)
            print(f"    ✅ Created: prompts/{prompt_file.name} ({len(prompt)} chars)")
            generated.append(prompt_file)

        processed_ids.append(item["id"])
        print()

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
    print(f"{'=' * 60}")
    print("📊 Summary")
    print(f"{'=' * 60}")
    print(f"Processed: {len(items)} news items")

    if not args.dry_run and generated:
        print(f"Generated: {len(generated)} prompt files")
        print(f"\n📁 Prompt files saved to: {prompts_dir}/")
        print()
        print("🚀 Next Steps:")
        print("─" * 40)
        print("1. Open a prompt file in _drafts/prompts/")
        print("2. Copy the entire content")
        print("3. Paste it to Claude/Cursor and ask to generate the post")
        print("4. Save Claude's output as a .md file in _drafts/")
        print("5. Review and move to _posts/ when ready")
        print()
        print("💡 Or directly tell Claude:")
        print(f'   "Read {prompts_dir}/<filename>_prompt.md and write the blog post"')


if __name__ == "__main__":
    main()
