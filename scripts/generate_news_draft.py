#!/usr/bin/env python3
"""
Tech News Draft Generator - 뉴스 초안 생성 스크립트

수집된 뉴스를 기반으로 블로그 포스트 초안을 생성합니다.
Gemini API를 사용하여 한국어로 요약 및 분석을 작성합니다.

Usage:
    python3 scripts/generate_news_draft.py
    python3 scripts/generate_news_draft.py --input _data/collected_news.json
    python3 scripts/generate_news_draft.py --max-posts 5
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
import yaml


# ============================================================================
# 설정
# ============================================================================

# 카테고리 매핑 (뉴스 카테고리 -> 블로그 카테고리)
CATEGORY_MAP = {
    "security": "security",
    "cloud": "cloud",
    "tech": "devops",
    "kubernetes": "kubernetes",
    "devops": "devops",
    "devsecops": "devsecops",
}

# 카테고리별 아이콘/이모지
CATEGORY_EMOJI = {
    "security": "🔒",
    "cloud": "☁️",
    "devops": "⚙️",
    "kubernetes": "🚀",
    "devsecops": "🛡️",
    "incident": "🚨",
    "finops": "💰",
}

# 기본 태그
DEFAULT_TAGS = {
    "security": ["Security", "보안"],
    "cloud": ["Cloud", "클라우드"],
    "devops": ["DevOps"],
    "kubernetes": ["Kubernetes", "Container"],
    "devsecops": ["DevSecOps", "Security"],
}


# ============================================================================
# AI 요약 생성 (Gemini API)
# ============================================================================


def generate_summary_with_gemini(news_item: dict, api_key: str) -> Optional[dict]:
    """Gemini API를 사용하여 뉴스 요약 생성"""
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""다음 기술 뉴스를 한국어로 요약하고 분석해주세요.

제목: {news_item["title"]}
원문 URL: {news_item["url"]}
출처: {news_item["source_name"]}
카테고리: {news_item["category"]}
요약 (영어): {news_item.get("summary", "")}

다음 형식으로 JSON 응답해주세요:
{{
    "korean_title": "한국어 제목 (원문 의미를 살린 자연스러운 번역)",
    "summary": "2-3문장의 핵심 요약",
    "key_points": ["핵심 포인트 1", "핵심 포인트 2", "핵심 포인트 3"],
    "impact": "이 뉴스가 DevSecOps/보안 실무자에게 주는 의미와 영향",
    "tags": ["관련 태그 1", "관련 태그 2", "관련 태그 3"]
}}

응답은 반드시 유효한 JSON 형식이어야 합니다."""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # JSON 추출
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            return json.loads(json_match.group())

        return None

    except Exception as e:
        print(f"    Gemini API error: {e}")
        return None


def generate_summary_fallback(news_item: dict) -> dict:
    """API 없이 기본 요약 생성"""
    title = news_item["title"]
    source = news_item["source_name"]
    category = news_item["category"]

    return {
        "korean_title": title,
        "summary": f"{source}에서 발표한 {category} 관련 뉴스입니다.",
        "key_points": [
            f"출처: {source}",
            f"카테고리: {category}",
            "원문을 참조하여 상세 내용을 확인하세요.",
        ],
        "impact": "관련 분야 실무자는 원문을 확인하여 최신 동향을 파악하시기 바랍니다.",
        "tags": DEFAULT_TAGS.get(category, ["Tech"]),
    }


# ============================================================================
# 포스트 생성
# ============================================================================


def create_post_content(news_item: dict, ai_summary: dict) -> str:
    """포스트 본문 생성"""
    category = news_item["category"]
    emoji = CATEGORY_EMOJI.get(category, "📰")

    content = f"""
{emoji} **{ai_summary["summary"]}**

## 핵심 포인트

"""

    for point in ai_summary.get("key_points", []):
        content += f"- {point}\n"

    content += f"""
## 실무 영향

{ai_summary.get("impact", "")}

## 원문 정보

- **출처**: [{news_item["source_name"]}]({news_item["url"]})
- **원문 제목**: {news_item["title"]}
- **발행일**: {news_item.get("published", "N/A")[:10]}

---

> 이 포스트는 자동 수집된 뉴스를 기반으로 작성된 초안입니다.
> 게시 전 내용을 검토하고 필요시 수정해주세요.
"""

    return content.strip()


def create_post_frontmatter(news_item: dict, ai_summary: dict, date: datetime) -> dict:
    """포스트 Front Matter 생성"""
    category = CATEGORY_MAP.get(news_item["category"], "devops")

    # 태그 생성
    tags = list(
        set(
            DEFAULT_TAGS.get(category, [])
            + ai_summary.get("tags", [])[:3]
            + news_item.get("tags", [])[:2]
        )
    )[:6]  # 최대 6개

    # 파일명에 사용할 영문 제목 생성
    title = ai_summary.get("korean_title", news_item["title"])

    return {
        "layout": "post",
        "title": title,
        "date": date.strftime("%Y-%m-%d %H:%M:%S +0900"),
        "category": category,
        "categories": [category],
        "tags": tags,
        "excerpt": ai_summary.get("summary", "")[:200],
        "original_url": news_item["url"],
        "original_source": news_item["source_name"],
        "auto_generated": True,
        "draft": True,
    }


def generate_filename(title: str, date: datetime) -> str:
    """영문 파일명 생성"""
    # 영문/숫자만 추출
    english_title = re.sub(r"[^a-zA-Z0-9\s-]", "", title)

    # 공백을 하이픈으로
    english_title = re.sub(r"\s+", "-", english_title.strip())

    # 소문자로
    english_title = english_title.lower()

    # 너무 길면 자르기
    if len(english_title) > 50:
        english_title = english_title[:50].rsplit("-", 1)[0]

    # 비어있으면 기본값
    if not english_title:
        english_title = "tech-news"

    date_str = date.strftime("%Y-%m-%d")
    return f"{date_str}-{english_title}.md"


def save_draft(fm: dict, content: str, output_dir: Path, filename: str) -> Path:
    """초안 저장"""
    output_dir.mkdir(parents=True, exist_ok=True)

    post = frontmatter.Post(content)
    post.metadata = fm

    output_path = output_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(frontmatter.dumps(post))

    return output_path


# ============================================================================
# 메인 함수
# ============================================================================


def main():
    parser = argparse.ArgumentParser(description="Tech News Draft Generator")
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
        default=10,
        help="Maximum number of posts to generate",
    )
    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Use Gemini AI for summary generation",
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Filter by category (security, cloud, tech, etc.)",
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
    print(f"\nLoaded {len(items)} news items")

    # 카테고리 필터링
    if args.category:
        items = [item for item in items if item["category"] == args.category]
        print(f"Filtered to {len(items)} items in category '{args.category}'")

    # 최대 개수 제한
    items = items[: args.max_posts]

    if not items:
        print("No items to process.")
        return

    # Gemini API 키 확인
    api_key = os.getenv("GEMINI_API_KEY", "")
    use_ai = args.use_ai and bool(api_key)

    if args.use_ai and not api_key:
        print("Warning: GEMINI_API_KEY not set, using fallback summary generation")

    # 출력 디렉토리
    output_dir = project_root / args.output_dir

    print(f"\nGenerating {len(items)} drafts...")
    print(f"AI Summary: {'Enabled' if use_ai else 'Disabled'}")
    print(f"Output: {output_dir}\n")

    generated = []
    processed_ids = []

    for i, item in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {item['title'][:60]}...")

        # AI 요약 생성
        if use_ai:
            ai_summary = generate_summary_with_gemini(item, api_key)
            if not ai_summary:
                ai_summary = generate_summary_fallback(item)
            time.sleep(1)  # API rate limit
        else:
            ai_summary = generate_summary_fallback(item)

        # 날짜
        try:
            pub_date = datetime.fromisoformat(item["published"].replace("Z", "+00:00"))
        except:
            pub_date = datetime.now(timezone.utc)

        # Front matter 및 콘텐츠 생성
        fm = create_post_frontmatter(item, ai_summary, pub_date)
        content = create_post_content(item, ai_summary)

        # 파일명 생성
        filename = generate_filename(item["title"], pub_date)

        if args.dry_run:
            print(f"    Would create: {filename}")
            print(f"    Title: {fm['title']}")
            print(f"    Category: {fm['category']}")
            print()
        else:
            # 저장
            output_path = save_draft(fm, content, output_dir, filename)
            print(f"    Created: {output_path.name}")
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

        print(f"\nUpdated processed IDs: {len(existing_ids)} total")

    # 결과 요약
    print(f"\n--- Summary ---")
    print(f"Processed: {len(items)} items")
    if not args.dry_run:
        print(f"Generated: {len(generated)} drafts")
        print(f"Output directory: {output_dir}")
        print(f"\nNext steps:")
        print(f"  1. Review drafts in {output_dir}/")
        print(f"  2. Edit and improve content")
        print(f"  3. Move to _posts/ when ready to publish")
        print(f"  4. Remove 'draft: true' from front matter")


if __name__ == "__main__":
    main()
