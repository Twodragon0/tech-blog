#!/usr/bin/env python3
"""
소셜 미디어 이미지 검증 스크립트
Facebook, Twitter, LinkedIn 등 플랫폼별 이미지 최적화 확인
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from PIL import Image
import json

# 플랫폼별 권장 이미지 크기
PLATFORM_SPECS = {
    "facebook": {"width": 1200, "height": 630, "name": "Facebook/Open Graph"},
    "twitter": {"width": 1200, "height": 675, "name": "Twitter Cards"},
    "linkedin": {"width": 1200, "height": 630, "name": "LinkedIn"},
    "instagram": {"width": 1080, "height": 1080, "name": "Instagram"},
}

def extract_front_matter(content: str) -> Dict[str, str]:
    """Front Matter 추출"""
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}

    fm_text = match.group(1)
    fm_data = {}

    for line in fm_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            fm_data[key.strip()] = value.strip().strip('"\'')

    return fm_data

def check_image_size(image_path: Path) -> Dict[str, any]:
    """이미지 크기 확인 및 플랫폼 호환성 검증"""
    if not image_path.exists():
        return {"exists": False}

    try:
        img = Image.open(image_path)
        width, height = img.size

        compatible = []
        for platform, spec in PLATFORM_SPECS.items():
            if width == spec["width"] and height == spec["height"]:
                compatible.append(platform)

        return {
            "exists": True,
            "size": (width, height),
            "compatible_platforms": compatible,
            "format": img.format
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

def generate_validator_urls(post_url: str) -> Dict[str, str]:
    """소셜 미디어 검증 URL 생성"""
    return {
        "facebook": f"https://developers.facebook.com/tools/debug/?q={post_url}",
        "twitter": f"https://cards-dev.twitter.com/validator?url={post_url}",
        "linkedin": f"https://www.linkedin.com/post-inspector/?url={post_url}"
    }

def get_post_url(post_filename: str, base_url: str) -> Optional[str]:
    """포스트 파일명에서 URL 생성"""
    date_match = re.match(r'(\d{4})-(\d{2})-(\d{2})-(.+)\.md', post_filename)
    if date_match:
        year, month, day, slug = date_match.groups()
        return f"{base_url}/{year}/{month}/{day}/{slug}/"
    return None

def verify_posts(posts: List[Path], base_url: str) -> List[Dict]:
    """포스트 목록 검증"""
    results = []

    for post_file in posts:
        try:
            content = post_file.read_text(encoding='utf-8')
        except Exception as e:
            results.append({
                "post": post_file.name,
                "status": "ERROR",
                "message": f"Failed to read file: {str(e)}"
            })
            continue

        fm = extract_front_matter(content)

        if not fm.get("image"):
            results.append({
                "post": post_file.name,
                "status": "ERROR",
                "message": "Missing 'image' field in front matter"
            })
            continue

        # 이미지 파일 확인 (SVG와 PNG 모두 체크)
        image_path = Path(fm["image"].lstrip('/'))
        png_path = image_path.with_suffix('.png')

        # PNG 우선, 없으면 원본 경로
        check_path = png_path if png_path.exists() else image_path
        image_info = check_image_size(check_path)

        # 포스트 URL 생성
        post_url = get_post_url(post_file.name, base_url)

        results.append({
            "post": post_file.name,
            "title": fm.get("title", "No title"),
            "image": fm.get("image"),
            "image_alt": fm.get("image_alt"),
            "image_checked": str(check_path),
            "image_info": image_info,
            "post_url": post_url,
            "validators": generate_validator_urls(post_url) if post_url else None,
            "status": "OK" if image_info.get("exists") else "ERROR"
        })

    return results

def print_markdown_report(results: List[Dict]) -> None:
    """마크다운 형식 리포트 출력"""
    print("# 소셜 미디어 이미지 검증 결과\n")
    print(f"총 {len(results)}개 포스트 검증\n")

    # 통계
    ok_count = sum(1 for r in results if r["status"] == "OK")
    error_count = len(results) - ok_count
    print(f"- ✅ 정상: {ok_count}개")
    print(f"- ❌ 오류: {error_count}개\n")

    print("---\n")

    for r in results:
        print(f"## {r['post']}")
        print(f"**제목:** {r.get('title', 'N/A')}\n")

        if r["status"] == "ERROR":
            print(f"❌ **오류:** {r.get('message', 'Unknown error')}\n")
            continue

        info = r['image_info']
        if info.get("exists"):
            size = info.get("size", ("Unknown", "Unknown"))
            platforms = info.get("compatible_platforms", [])

            print(f"✅ **이미지:** `{r['image']}`")
            print(f"- 파일: `{r.get('image_checked', 'N/A')}`")
            print(f"- 크기: {size[0]}x{size[1]}px")
            print(f"- 포맷: {info.get('format', 'Unknown')}")

            if platforms:
                print(f"- 호환 플랫폼: {', '.join(p.title() for p in platforms)}")
            else:
                print("- ⚠️  표준 소셜 미디어 크기가 아닙니다")
                print("\n  **권장 크기:**")
                for platform, spec in PLATFORM_SPECS.items():
                    print(f"  - {spec['name']}: {spec['width']}x{spec['height']}px")
        else:
            print(f"❌ **이미지 파일 없음:** `{r['image']}`")

        if r.get("image_alt"):
            print(f"\n**대체 텍스트:** {r['image_alt']}")

        if r.get("post_url"):
            print(f"\n**포스트 URL:** {r['post_url']}")

        if r.get("validators"):
            print("\n**검증 도구:**")
            for platform, url in r["validators"].items():
                print(f"- [{platform.title()} Validator]({url})")

        print("\n---\n")

def print_json_report(results: List[Dict]) -> None:
    """JSON 형식 리포트 출력"""
    print(json.dumps(results, indent=2, ensure_ascii=False))

def main():
    parser = argparse.ArgumentParser(
        description="소셜 미디어 이미지 검증 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all                           # 모든 포스트 검증
  %(prog)s --post 2026-02-04-example.md    # 특정 포스트 검증
  %(prog)s --all --format json             # JSON 형식 출력
  %(prog)s --all --output report.md        # 파일로 저장

Platforms:
  - Facebook/Open Graph: 1200x630px
  - Twitter Cards: 1200x675px
  - LinkedIn: 1200x630px
  - Instagram: 1080x1080px
        """
    )
    parser.add_argument("--all", action="store_true", help="모든 포스트 검증")
    parser.add_argument("--post", help="특정 포스트 검증 (파일명)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown",
                        help="출력 형식 (기본: markdown)")
    parser.add_argument("--output", help="결과를 파일로 저장")
    parser.add_argument("--base-url", default="https://tech.2twodragon.com/posts",
                        help="기본 URL (기본: https://tech.2twodragon.com/posts)")

    args = parser.parse_args()

    # 입력 검증
    if not args.all and not args.post:
        parser.print_help()
        sys.exit(1)

    posts_dir = Path("_posts")
    if not posts_dir.exists():
        print(f"❌ Error: Posts directory not found: {posts_dir}", file=sys.stderr)
        sys.exit(1)

    # 포스트 목록 수집
    if args.all:
        posts = sorted(posts_dir.glob("*.md"))
        if not posts:
            print(f"❌ Error: No posts found in {posts_dir}", file=sys.stderr)
            sys.exit(1)
    else:
        post_path = posts_dir / args.post
        if not post_path.exists():
            print(f"❌ Error: Post not found: {post_path}", file=sys.stderr)
            sys.exit(1)
        posts = [post_path]

    # 검증 수행
    results = verify_posts(posts, args.base_url)

    # 결과 출력
    if args.output:
        original_stdout = sys.stdout
        with open(args.output, 'w', encoding='utf-8') as f:
            sys.stdout = f
            if args.format == "markdown":
                print_markdown_report(results)
            else:
                print_json_report(results)
        sys.stdout = original_stdout
        print(f"✅ Report saved to: {args.output}")
    else:
        if args.format == "markdown":
            print_markdown_report(results)
        else:
            print_json_report(results)

    # 종료 코드 설정
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    sys.exit(1 if error_count > 0 else 0)

if __name__ == "__main__":
    main()
