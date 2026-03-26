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

import argparse
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import yaml
except ModuleNotFoundError:
    print(
        "❌ Missing dependency: PyYAML. Run `pip install -r scripts/requirements.txt` and retry.",
        file=sys.stderr,
    )
    raise SystemExit(2)

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
]
OPTIONAL_FIELDS = ["comments", "original_url", "image_alt", "toc"]
DEPRECATED_FIELDS = ["schema_type", "category"]
GENERIC_TITLE_PATTERNS = [
    r"^클라우드 보안, 보안 위협, AI$",
    r"^보안 위협, AI, 클라우드 보안$",
    r"^기술 블로그 주간 다이제스트:\s*(기술 동향|클라우드|AI)(,\s*.*)?$",
    r"^(보안 위협|기술 동향|클라우드 보안|AI)(,\s*(보안 위협|기술 동향|클라우드 보안|AI|DevOps|블록체인)){1,3}$",
]


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

    # Deprecated fields check
    for field in DEPRECATED_FIELDS:
        if field in front_matter:
            issues.append(f"⚠️ Deprecated field '{field}' should be removed")

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

    title = str(front_matter.get("title", "")).strip()
    if title:
        for pattern in GENERIC_TITLE_PATTERNS:
            if re.match(pattern, title):
                issues.append(f"⚠️ Generic title should be more specific: {title}")
                break

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
    """긴 코드 블록 확인 (30줄 이상 또는 1000자 이상)"""
    issues = []

    code_block_pattern = r"```(\w+)?\n(.*?)```"
    matches = re.finditer(code_block_pattern, content, re.DOTALL)

    for match in matches:
        # Skip code blocks inside HTML comments
        last_comment_open = content.rfind("<!--", 0, match.start())
        last_comment_close = content.rfind("-->", 0, match.start())
        if last_comment_open > last_comment_close:
            comment_end = content.find("-->", match.end())
            if comment_end != -1:
                continue

        # Skip code blocks inside <details> (already collapsed)
        last_details_open = content.rfind("<details>", 0, match.start())
        last_details_close = content.rfind("</details>", 0, match.start())
        if last_details_open > last_details_close:
            continue

        code = match.group(2)
        lines = code.count("\n")
        length = len(code)

        if lines >= 30 or length >= 1000:
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


def check_svg_text_density(front_matter: dict[str, object]) -> list[str]:
    issues = []
    image_path = str(front_matter.get("image", ""))
    if not image_path.endswith(".svg"):
        return issues

    exists, image_file = check_image_exists(image_path)
    if not exists or image_file is None:
        return issues

    try:
        root = ET.fromstring(image_file.read_text(encoding="utf-8"))
    except ET.ParseError:
        return [f"⚠️ Invalid SVG XML: {image_path}"]

    text_nodes = [
        " ".join((node.itertext())).strip()
        for node in root.iter()
        if node.tag.endswith("text")
    ]
    text_nodes = [text for text in text_nodes if text]
    total_chars = sum(len(text) for text in text_nodes)

    if len(text_nodes) > 10:
        issues.append(
            f"⚠️ SVG text too dense ({len(text_nodes)} text nodes): {image_path}"
        )
    if total_chars > 300:
        issues.append(
            f"⚠️ SVG contains too much text ({total_chars} chars): {image_path}"
        )

    noisy_markers = [
        "weekly digest",
        "news collected",
        "security",
        "cloud",
        "devops",
        "ai/ml",
        "blockchain",
    ]
    repeated_labels = sum(
        1
        for text in text_nodes
        if text.strip().lower() in noisy_markers
        or text.strip().lower().endswith(" news")
    )
    if repeated_labels >= 5:
        issues.append(
            f"⚠️ SVG relies on repeated label text instead of a single concept: {image_path}"
        )

    return issues


def check_news_card_severity(content: str) -> List[str]:
    """Check that all news-card includes have an explicit severity parameter."""
    issues = []
    # Find all news-card include blocks
    pattern = re.compile(
        r"\{%-?\s*include\s+news-card\.html\b(.*?)%\}",
        re.DOTALL,
    )
    for i, match in enumerate(pattern.finditer(content), 1):
        block = match.group(1)
        if "severity=" not in block:
            # Try to extract title for better reporting
            title_match = re.search(r'title="([^"]{0,60})', block)
            title_hint = title_match.group(1) if title_match else f"card #{i}"
            issues.append(f'⚠️ News card missing severity: "{title_hint}..."')
    return issues


def check_table_cell_truncation(content: str) -> List[str]:
    """마크다운 테이블 셀이 문장 중간에 잘린 패턴 감지 (양성 지표 기반)"""
    issues = []

    # --- 양성 잘림 지표 (positive truncation indicators) ---
    # 1. 쉼표 뒤 바로 끝나는 셀
    trailing_comma_pattern = re.compile(r",\s*$")
    # 2. 영문 관사/전치사로 끝나는 셀 (Q&A 등 약어 제외)
    dangling_english_pattern = re.compile(
        r"(?<![&/])\b(?:the|a|an|in|of|for|to|with|and|or)\s*$", re.IGNORECASE
    )
    # 3. 한국어 접속사/복합 조사로 끝나는 셀 (단일 글자 조사 제외 - 오탐 방지)
    dangling_korean_pattern = re.compile(
        r"(?:\s(?:및|또는|그리고|하지만|그래서|따라서|때문에))\s*$"
    )
    # 4. 좌측 잘림: 소문자 영문으로 시작하되 알려진 기술 용어 제외
    _LOWERCASE_TECH_TERMS = {
        "eSIM", "iOS", "iPad", "iPhone", "iCloud", "iMac", "iTerm",
        "macOS", "npm", "nmap", "kubectl", "git", "curl", "wget",
        "sudo", "ssh", "http", "https", "localhost", "terraform",
        "ansible", "docker", "podman", "systemd", "rsync", "cron",
        "chmod", "chown", "grep", "sed", "awk", "jq", "yq",
    }

    for line_num, line in enumerate(content.split("\n"), 1):
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        if re.match(r"^\|[\s\-:]+\|[\s\-:|]*$", stripped):
            continue

        cells = stripped[1:-1].split("|")
        for cell in cells:
            cell_stripped = cell.strip()
            if not cell_stripped or len(cell_stripped) <= 5:
                continue

            if trailing_comma_pattern.search(cell_stripped):
                snippet = cell_stripped[-40:] if len(cell_stripped) > 40 else cell_stripped
                issues.append(
                    f"WARNING: line {line_num} - 테이블 셀이 문장 중간에 잘림: \"{snippet}\""
                )
            elif dangling_english_pattern.search(cell_stripped):
                snippet = cell_stripped[-40:] if len(cell_stripped) > 40 else cell_stripped
                issues.append(
                    f"WARNING: line {line_num} - 테이블 셀이 문장 중간에 잘림: \"{snippet}\""
                )
            elif dangling_korean_pattern.search(cell_stripped) and len(cell_stripped) > 10:
                snippet = cell_stripped[-40:] if len(cell_stripped) > 40 else cell_stripped
                issues.append(
                    f"WARNING: line {line_num} - 테이블 셀이 조사/접속사로 끝남: \"{snippet}\""
                )
            elif cell_stripped[0].islower() and not cell_stripped.startswith("http"):
                # Skip code/config patterns that legitimately start lowercase
                if (
                    "`" in cell_stripped  # code snippets with backticks
                    or "\\" in cell_stripped  # escaped quotes/code patterns
                    or "=" in cell_stripped.split()[0]  # key=value config (p=quarantine)
                    or "[.]" in cell_stripped  # defanged domains (evil[.]com)
                    or re.match(r"^[a-z]+\(", cell_stripped)  # function calls
                ):
                    continue
                raw_first = cell_stripped.split()[0].rstrip(",:;\"'") if cell_stripped.split() else ""
                first_word = re.split(r"[,/;:\-]", raw_first)[0]
                if (
                    len(first_word) >= 2
                    and first_word not in _LOWERCASE_TECH_TERMS
                    and not re.match(r"^[a-z][\w\-.:/]+$", raw_first)  # skip identifiers/paths
                    and not re.match(r"^[a-z]+[A-Z]", raw_first)  # skip camelCase
                ):
                    snippet = cell_stripped[:40] if len(cell_stripped) > 40 else cell_stripped
                    issues.append(
                        f"WARNING: line {line_num} - 테이블 셀이 좌측에서 잘림: \"{snippet}\""
                    )

    return issues


def check_duplicate_practical_points(content: str) -> List[str]:
    """Check for duplicate '실무 적용 포인트' bullet points within a single post.

    Detects when the same bullet text appears 3+ times, which indicates
    copy-pasted generic templates that should be replaced with
    context-specific content.
    """
    issues = []
    # Extract all bullet lines under "실무 적용 포인트" or "실무 포인트" sections
    bullets: List[str] = []
    in_section = False
    for line in content.split("\n"):
        stripped = line.strip()
        # Detect section headers
        if "실무 적용 포인트" in stripped or "실무 포인트" in stripped:
            in_section = True
            continue
        # Exit section on next header or separator
        if in_section and (
            stripped.startswith("#")
            or stripped.startswith("---")
            or (stripped.startswith("{%") and "include" in stripped)
        ):
            in_section = False
        # Collect bullet points
        if in_section and stripped.startswith("- "):
            bullets.append(stripped[2:].strip())

    # Count occurrences
    from collections import Counter

    counts = Counter(bullets)
    for text, count in counts.most_common():
        if count >= 3:
            issues.append(f'⚠️ 실무 포인트 반복 {count}회: "{text[:50]}..."')
    return issues


def main():
    """메인 함수"""
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
    parser.add_argument(
        "--changed",
        action="store_true",
        help="Git 기준 변경된 포스트(_posts/*.md)만 검증",
    )
    parser.add_argument("file", nargs="?", help="검증할 특정 파일 (선택사항)")

    args = parser.parse_args()

    if not POSTS_DIR.exists():
        print(f"❌ Posts directory not found: {POSTS_DIR}")
        return

    def _resolve_changed_posts() -> list[Path]:
        changed: set[str] = set()
        # PR environment: compare against origin/main
        # Local: compare HEAD for staged/unstaged changes
        commands = [
            ["git", "diff", "--name-only", "origin/main...HEAD", "--", "_posts/*.md"],
            ["git", "diff", "--name-only", "HEAD", "--", "_posts/*.md"],
            ["git", "ls-files", "--others", "--exclude-standard", "--", "_posts/*.md"],
        ]

        for command in commands:
            try:
                result = subprocess.run(
                    command,
                    cwd=PROJECT_ROOT,
                    check=False,
                    capture_output=True,
                    text=True,
                )
            except OSError:
                continue

            if result.returncode != 0:
                continue

            for line in result.stdout.splitlines():
                entry = line.strip()
                if entry.endswith(".md") and entry.startswith("_posts/"):
                    changed.add(entry)

        return [PROJECT_ROOT / rel for rel in sorted(changed)]

    # 파일 목록
    if args.file:
        post_files = [Path(args.file)]
        if not post_files[0].is_absolute():
            post_files[0] = PROJECT_ROOT / post_files[0]
    elif args.changed:
        post_files = _resolve_changed_posts()
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

        issues.extend(check_svg_text_density(front_matter))

        # 더미 링크 확인
        issues.extend(check_dummy_links(content))

        # 이미지 경로 확인
        issues.extend(check_image_paths(content))

        # 긴 코드 블록 확인
        issues.extend(check_long_code_blocks(content))

        # AI 요약 카드 확인
        issues.extend(check_ai_summary_card(content))

        # 뉴스 카드 severity 확인
        issues.extend(check_news_card_severity(content))

        # 실무 포인트 반복 감지
        issues.extend(check_duplicate_practical_points(content))

        # 테이블 셀 잘림 감지
        issues.extend(check_table_cell_truncation(content))

        if issues:
            all_issues[post_file.name] = issues
            total_issues += len(issues)
            if not args.detailed_only:
                print(f"  Found {len(issues)} issues")
        else:
            if not args.detailed_only:
                print("  ✅ No issues found")

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
