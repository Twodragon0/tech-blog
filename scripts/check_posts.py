#!/usr/bin/env python3
"""
통합 포스팅 검증 스크립트
모든 포스팅의 일관성과 규칙 준수를 확인합니다.

검증 항목:
- Front matter 필수 필드
- 이미지 파일명 (한글 확인)
- 더미 링크
- 긴 코드 블록
- AI 요약 카드
- 이미지 파일 존재 여부
- 링크 유효성
"""

import os
import re
import yaml
from pathlib import Path
from typing import List, Dict, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

REQUIRED_FIELDS = [
    "layout",
    "title",
    "date",
    "categories",
    "tags",
    "excerpt",
    "image",
    "toc",
]
OPTIONAL_FIELDS = ["comments", "original_url", "image_alt", "category"]


def extract_front_matter(content: str) -> tuple[dict[str, object], str]:
    """Front matter 추출"""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    try:
        front_matter = yaml.safe_load(parts[1])
        body = parts[2] if len(parts) > 2 else ""
        return front_matter or {}, body
    except yaml.YAMLError:
        return {}, content


def check_front_matter(file_path: Path) -> List[str]:
    """Front matter 검증"""
    issues = []
    content = file_path.read_text(encoding="utf-8")
    front_matter, _ = extract_front_matter(content)

    # 필수 필드 확인
    for field in REQUIRED_FIELDS:
        if field not in front_matter:
            issues.append(f"❌ Missing required field: {field}")

    # 이미지 파일명이 영어인지 확인
    if "image" in front_matter:
        image_path = str(front_matter["image"])
        # 한글 문자 확인
        if re.search(r"[가-힣]", image_path):
            issues.append(f"⚠️ Image filename contains Korean: {image_path}")

    # categories가 배열인지 확인
    if "categories" in front_matter and not isinstance(
        front_matter["categories"], list
    ):
        issues.append("⚠️ categories should be a list")

    # tags가 배열인지 확인
    if "tags" in front_matter and not isinstance(front_matter["tags"], list):
        issues.append("⚠️ tags should be a list")

    return issues


def check_dummy_links(content: str) -> List[str]:
    """더미 링크 확인"""
    issues = []

    # 더미 링크 패턴
    dummy_patterns = [
        r"github\.com/example(?:/[^\s\)]*)?",
        r"https?://[^\s\)]*(?:dummy|placeholder)[^\s\)]*",
        r"\b(?:더미|dummy|placeholder)\b",
    ]

    for pattern in dummy_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            line_num = content[: match.start()].count("\n") + 1
            issues.append(f"⚠️ Possible dummy link at line {line_num}: {match.group()}")

    return issues


def check_image_paths(content: str) -> List[str]:
    """이미지 경로 확인"""
    issues = []

    # 마크다운 이미지 패턴
    md_image_pattern = r"!\[.*?\]\(([^)]+)\)"
    # HTML img 태그 패턴
    html_image_pattern = r'<img[^>]+src=["\']([^"\']+)["\']'

    for pattern in [md_image_pattern, html_image_pattern]:
        matches = re.finditer(pattern, content)
        for match in matches:
            image_path = match.group(1)
            # 한글 문자 확인
            if re.search(r"[가-힣]", image_path):
                line_num = content[: match.start()].count("\n") + 1
                issues.append(
                    f"⚠️ Image path contains Korean at line {line_num}: {image_path}"
                )

    return issues


def check_long_code_blocks(content: str) -> List[str]:
    """긴 코드 블록 확인 (10줄 이상 또는 500자 이상)"""
    issues = []

    code_block_pattern = r"```(\w+)?\n(.*?)```"
    matches = re.finditer(code_block_pattern, content, re.DOTALL)

    for match in matches:
        last_comment_open = content.rfind("<!--", 0, match.start())
        last_comment_close = content.rfind("-->", 0, match.start())
        if last_comment_open > last_comment_close:
            comment_end = content.find("-->", match.end())
            if comment_end != -1:
                continue

        code = match.group(2)
        lines = code.count("\n")
        length = len(code)

        if lines >= 10 or length >= 500:
            line_num = content[: match.start()].count("\n") + 1
            issues.append(
                f"💡 Long code block at line {line_num} ({lines} lines, {length} chars) - consider replacing with link"
            )

    return issues


def check_ai_summary_card(content: str) -> List[str]:
    """AI 요약 카드 확인"""
    issues = []

    if "ai-summary-card" not in content.lower():
        issues.append("⚠️ AI summary card not found")

    return issues


def check_image_exists(image_path: str) -> Tuple[bool, Optional[Path]]:
    """이미지 파일 존재 여부 확인"""
    if not image_path:
        return False, None

    # /assets/images/... 형식에서 실제 경로 추출
    if image_path.startswith("/assets/images/"):
        image_file = PROJECT_ROOT / image_path.lstrip("/")
    elif image_path.startswith("assets/images/"):
        image_file = PROJECT_ROOT / image_path
    else:
        image_file = IMAGES_DIR / Path(image_path).name

    return image_file.exists(), image_file


def check_image_files(file_path: Path, front_matter: dict[str, object]) -> list[str]:
    """이미지 파일 존재 여부 확인"""
    issues = []

    # Front matter의 메인 이미지 확인
    if "image" in front_matter:
        image_path = str(front_matter["image"])
        exists, _ = check_image_exists(image_path)
        if not exists:
            issues.append(f"❌ Main image file not found: {image_path}")

    # 본문의 이미지 확인
    content = file_path.read_text(encoding="utf-8")
    image_patterns = [
        r"!\[.*?\]\(([^)]+)\)",  # 마크다운 이미지
        r'<img[^>]+src=["\']([^"\']+)["\']',  # HTML img 태그
    ]

    for pattern in image_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            image_path = match.group(1)
            if "/assets/images/" in image_path or image_path.startswith(
                "/assets/images/"
            ):
                exists, _ = check_image_exists(image_path)
                if not exists:
                    line_num = content[: match.start()].count("\n") + 1
                    issues.append(
                        f"❌ Image file not found at line {line_num}: {image_path}"
                    )

    return issues


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="통합 포스팅 검증 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 모든 포스팅 검증
  python3 scripts/check_posts.py
  
  # 상세 리포트만 (요약 제외)
  python3 scripts/check_posts.py --detailed-only
  
  # 특정 파일만 검증
  python3 scripts/check_posts.py _posts/2025-01-01-example.md
        """,
    )

    parser.add_argument(
        "--detailed-only", action="store_true", help="상세 리포트만 출력 (요약 제외)"
    )
    parser.add_argument("file", nargs="?", help="검증할 특정 파일 (선택사항)")

    args = parser.parse_args()

    if not POSTS_DIR.exists():
        print(f"❌ Posts directory not found: {POSTS_DIR}")
        return

    # 파일 목록
    if args.file:
        post_files = [Path(args.file)]
        if not post_files[0].is_absolute():
            post_files[0] = PROJECT_ROOT / post_files[0]
    else:
        post_files = sorted(POSTS_DIR.glob("*.md"))

    if not args.detailed_only:
        print(f"📝 Found {len(post_files)} post files\n")

    all_issues = {}
    total_issues = 0

    for post_file in post_files:
        if not post_file.exists():
            print(f"⚠️  File not found: {post_file}")
            continue

        if not args.detailed_only:
            print(f"Checking: {post_file.name}")

        issues = []
        content = post_file.read_text(encoding="utf-8")
        front_matter, _ = extract_front_matter(content)

        # Front matter 검증
        issues.extend(check_front_matter(post_file))

        # 이미지 파일 존재 여부 확인
        issues.extend(check_image_files(post_file, front_matter))

        # 더미 링크 확인
        issues.extend(check_dummy_links(content))

        # 이미지 경로 확인
        issues.extend(check_image_paths(content))

        # 긴 코드 블록 확인
        issues.extend(check_long_code_blocks(content))

        # AI 요약 카드 확인
        issues.extend(check_ai_summary_card(content))

        if issues:
            all_issues[post_file.name] = issues
            total_issues += len(issues)
            if not args.detailed_only:
                print(f"  Found {len(issues)} issues")
        else:
            if not args.detailed_only:
                print(f"  ✅ No issues found")

    if not args.detailed_only:
        print(f"\n{'=' * 60}")
        print(f"Summary: {total_issues} total issues found in {len(all_issues)} files")
        print(f"{'=' * 60}\n")

    # 상세 리포트
    if all_issues:
        print("Detailed Report:\n")
        for filename, issues in all_issues.items():
            print(f"\n📄 {filename}:")
            for issue in issues:
                print(f"  {issue}")
    elif args.detailed_only:
        print("✅ No issues found in all posts!")


if __name__ == "__main__":
    main()
