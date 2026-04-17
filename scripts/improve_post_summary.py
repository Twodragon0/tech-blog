#!/usr/bin/env python3
"""
포스팅 요약 개선 및 이미지 확인 스크립트
Gemini CLI를 활용하여 포스팅 요약을 개선하고 이미지 파일을 확인합니다.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.lib import image_utils as _image_utils

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"


def extract_summary_from_post(post_file: Path) -> Dict[str, str]:
    """포스팅 파일에서 요약 정보 추출"""
    content = post_file.read_text(encoding="utf-8")

    # Front matter 추출
    front_matter_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    front_matter = {}
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        for line in front_matter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                front_matter[key.strip()] = value.strip().strip('"')

    # 요약 섹션 추출
    summary_match = re.search(r"## 📋 포스팅 요약\n\n(.*?)\n\n", content, re.DOTALL)
    summary_text = summary_match.group(1) if summary_match else ""

    # 본문 추출 (요약 섹션 이후)
    body_match = re.search(r"## 📋 포스팅 요약\n\n.*?\n\n(.*)", content, re.DOTALL)
    body_text = body_match.group(1) if body_match else content

    return {
        "title": front_matter.get("title", ""),
        "category": front_matter.get("categories", front_matter.get("category", "")),
        "tags": front_matter.get("tags", "[]"),
        "excerpt": front_matter.get("excerpt", ""),
        "summary": summary_text,
        "body": body_text[:1000],  # 처음 1000자만
        "image": front_matter.get("image", ""),
        "filename": post_file.name,
    }


def check_image_exists(image_path: str) -> bool:
    """이미지 파일 존재 여부 확인 (공용 `image_utils.image_exists` 래퍼)."""
    return _image_utils.image_exists(
        image_path,
        project_root=PROJECT_ROOT,
        images_dir=IMAGES_DIR,
    )


def improve_summary_with_gemini(post_data: Dict[str, str]) -> str:
    """Gemini CLI를 사용하여 요약 개선"""
    prompt = f"""다음 기술 블로그 포스팅의 요약을 개선해주세요.

**제목**: {post_data["title"]}
**카테고리**: {post_data["category"]}
**태그**: {post_data["tags"]}

**현재 요약**:
{post_data["summary"]}

**본문 일부**:
{post_data["body"]}

**개선 요청사항**:
1. 핵심 내용을 더 명확하고 구조화된 형식으로 정리
2. 기술적 키워드와 주요 개념을 강조
3. AI가 이해하기 쉬운 구조화된 형식 유지
4. 한글로 작성하되, 기술 용어는 영어 병기
5. 다음 형식으로 작성:
   - 제목
   - 카테고리
   - 태그
   - 핵심 내용 (3-5개 주요 포인트)
   - 주요 기술/도구
   - 실무 적용 포인트

개선된 요약을 마크다운 형식으로 제공해주세요."""

    try:
        # Gemini CLI 실행
        result = subprocess.run(
            ["gemini", prompt],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=PROJECT_ROOT,
        )

        if result.returncode == 0:
            return result.stdout.strip()
        else:
            print(f"⚠️  Gemini CLI 오류: {result.stderr}", file=sys.stderr)
            return None
    except subprocess.TimeoutExpired:
        print("⚠️  Gemini CLI 타임아웃", file=sys.stderr)
        return None
    except FileNotFoundError:
        print(
            "⚠️  Gemini CLI를 찾을 수 없습니다. 설치되어 있는지 확인하세요.",
            file=sys.stderr,
        )
        return None
    except Exception as e:
        print(f"⚠️  오류 발생: {e}", file=sys.stderr)
        return None


def analyze_post(post_file: Path, use_gemini: bool = False) -> Dict:
    """포스팅 분석 및 개선"""
    print(f"\n📄 분석 중: {post_file.name}")
    print("=" * 80)

    # 요약 추출
    post_data = extract_summary_from_post(post_file)

    # 이미지 확인
    image_exists = check_image_exists(post_data["image"])

    result = {
        "file": post_file.name,
        "title": post_data["title"],
        "has_summary": bool(post_data["summary"]),
        "has_image": image_exists,
        "image_path": post_data["image"],
        "summary": post_data["summary"],
        "improved_summary": None,
    }

    # 이미지 상태 출력
    if image_exists:
        print(f"✅ 이미지 파일 존재: {post_data['image']}")
    else:
        print(f"❌ 이미지 파일 없음: {post_data['image']}")
        # 이미지 파일명 추정
        image_filename = post_file.stem + ".svg"
        print(f"   예상 이미지 파일명: {image_filename}")

    # 요약 상태 출력
    if post_data["summary"]:
        print("✅ 요약 섹션 존재")
        print("\n현재 요약 (일부):")
        print(post_data["summary"][:200] + "...")
    else:
        print("❌ 요약 섹션 없음")

    # Gemini를 사용한 요약 개선
    if use_gemini and post_data["summary"]:
        print("\n🤖 Gemini CLI로 요약 개선 중...")
        improved = improve_summary_with_gemini(post_data)
        if improved:
            result["improved_summary"] = improved
            print("✅ 요약 개선 완료")
            print("\n개선된 요약 (일부):")
            print(improved[:300] + "...")
        else:
            print("⚠️  요약 개선 실패")

    return result


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="포스팅 요약 개선 및 이미지 확인")
    parser.add_argument(
        "post", nargs="?", help="분석할 포스팅 파일명 (전체 경로 또는 파일명만)"
    )
    parser.add_argument("--all", action="store_true", help="모든 포스팅 분석")
    parser.add_argument(
        "--gemini", action="store_true", help="Gemini CLI를 사용하여 요약 개선"
    )
    parser.add_argument(
        "--recent", type=int, default=5, help="최근 N개 포스팅만 분석 (기본값: 5)"
    )

    args = parser.parse_args()

    # 포스팅 파일 목록 가져오기
    if args.post:
        # 특정 포스팅 분석
        if os.path.isabs(args.post):
            post_file = Path(args.post)
        else:
            post_file = POSTS_DIR / args.post

        if not post_file.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {post_file}")
            sys.exit(1)

        posts = [post_file]
    elif args.all:
        # 모든 포스팅 분석
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )
    else:
        # 최근 포스팅만 분석
        posts = sorted(
            POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
        )[: args.recent]

    print(f"📊 {len(posts)}개 포스팅 분석 시작...")

    results = []
    for post_file in posts:
        result = analyze_post(post_file, use_gemini=args.gemini)
        results.append(result)

    # 요약 리포트 출력
    print("\n" + "=" * 80)
    print("📊 분석 결과 요약")
    print("=" * 80)

    total = len(results)
    with_summary = sum(1 for r in results if r["has_summary"])
    with_image = sum(1 for r in results if r["has_image"])

    print(f"전체 포스팅: {total}")
    print(f"요약 섹션 있음: {with_summary} ({with_summary / total * 100:.1f}%)")
    print(f"이미지 파일 있음: {with_image} ({with_image / total * 100:.1f}%)")

    # 이미지가 없는 포스팅 목록
    missing_images = [r for r in results if not r["has_image"]]
    if missing_images:
        print(f"\n❌ 이미지가 없는 포스팅 ({len(missing_images)}개):")
        for r in missing_images:
            print(f"  - {r['file']}")

    # 요약이 없는 포스팅 목록
    missing_summaries = [r for r in results if not r["has_summary"]]
    if missing_summaries:
        print(f"\n❌ 요약이 없는 포스팅 ({len(missing_summaries)}개):")
        for r in missing_summaries:
            print(f"  - {r['file']}")

    # 개선된 요약이 있는 경우 저장 옵션 제공
    improved_posts = [r for r in results if r["improved_summary"]]
    if improved_posts:
        print(f"\n✅ 개선된 요약이 있는 포스팅 ({len(improved_posts)}개):")
        for r in improved_posts:
            print(f"  - {r['file']}")
            print("    개선된 요약을 파일에 저장하시겠습니까? (수동으로 확인 필요)")


if __name__ == "__main__":
    main()
