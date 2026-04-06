#!/usr/bin/env python3
"""포스트 간 크로스 레퍼런스 자동 추가 스크립트

Weekly Digest 포스트에서 동일 뉴스/사건이 여러 날에 걸쳐 반복 보도될 때,
관련 포스트 간 링크를 자동으로 삽입합니다.
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"

# 크로스 레퍼런스 마커 (중복 감지용)
CROSS_REF_MARKER = "📌 **관련 보도**"

# 포스트 날짜 패턴 (파일명에서 추출)
POST_DATE_PATTERN = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")


def parse_front_matter(content: str) -> dict:
    """front matter에서 title, date 파싱"""
    if not content.startswith("---"):
        return {}

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    fm_text = parts[1]
    result = {}

    # title 추출 (따옴표 있는/없는 경우 모두 처리)
    title_match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', fm_text, re.MULTILINE)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # date 추출
    date_match = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", fm_text, re.MULTILINE)
    if date_match:
        result["date"] = date_match.group(1)

    return result


def build_jekyll_permalink(filename: str) -> str:
    """파일명에서 Jekyll permalink 생성: /posts/YYYY/MM/DD/파일명-날짜제외/"""
    m = POST_DATE_PATTERN.match(filename)
    if not m:
        return ""
    date_str, slug = m.group(1), m.group(2)
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return ""
    return f"/posts/{dt.year}/{dt.month:02d}/{dt.day:02d}/{slug}/"


def scan_posts(days: int) -> list[dict]:
    """_posts/ 디렉토리에서 포스트 스캔, 날짜 필터 적용"""
    cutoff = None
    if days > 0:
        cutoff = datetime.now() - timedelta(days=days)

    posts = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        m = POST_DATE_PATTERN.match(path.name)
        if not m:
            continue

        date_str = m.group(1)
        try:
            post_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            continue

        if cutoff and post_date < cutoff:
            continue

        content = path.read_text(encoding="utf-8")
        fm = parse_front_matter(content)
        title = fm.get("title", path.stem)
        permalink = build_jekyll_permalink(path.name)

        posts.append(
            {
                "path": path,
                "filename": path.name,
                "date": post_date,
                "date_str": date_str,
                "title": title,
                "permalink": permalink,
                "content": content,
            }
        )

    return posts


def find_keyword_posts(posts: list[dict], keyword: str) -> list[dict]:
    """키워드를 포함한 포스트 목록 반환 (대소문자 무시)"""
    matched = []
    kw_lower = keyword.lower()
    for post in posts:
        if kw_lower in post["content"].lower():
            matched.append(post)
    return matched


def split_into_sections(content: str) -> list[tuple[int, int, str]]:
    """### 레벨 헤딩 섹션으로 분리. (start, end, heading_text) 목록 반환"""
    sections = []
    lines = content.splitlines(keepends=True)
    heading_pattern = re.compile(r"^### (.+)")

    current_start = None
    current_heading = None

    for i, line in enumerate(lines):
        if heading_pattern.match(line):
            if current_start is not None:
                sections.append((current_start, i, current_heading))
            current_start = i
            current_heading = heading_pattern.match(line).group(1).strip()

    if current_start is not None:
        sections.append((current_start, len(lines), current_heading))

    return sections


def section_has_cross_ref(lines: list[str], start: int, end: int) -> bool:
    """섹션 내 크로스 레퍼런스 마커 존재 여부 확인"""
    for line in lines[start:end]:
        if CROSS_REF_MARKER in line:
            return True
    return False


def find_section_last_content_line(lines: list[str], start: int, end: int) -> int:
    """섹션 마지막 실질 내용 라인 인덱스 반환 (빈 줄 및 --- 구분선 제외)"""
    last = start
    for i in range(start, end):
        stripped = lines[i].rstrip()
        if stripped and stripped != "---":
            last = i
    return last


def build_cross_ref_line(post: dict) -> str:
    """크로스 레퍼런스 삽입 텍스트 생성"""
    date_display = post["date"].strftime("%Y년 %m월 %d일")
    return f"> {CROSS_REF_MARKER}: [{post['title']} ({date_display})]({post['permalink']})\n"


def add_cross_references_to_post(
    target_post: dict,
    related_posts: list[dict],
    keyword: str,
    dry_run: bool,
) -> int:
    """
    target_post에서 keyword가 포함된 ### 섹션을 찾아
    related_posts 링크를 삽입합니다.
    반환값: 삽입된 레퍼런스 수
    """
    content = target_post["content"]
    lines = content.splitlines(keepends=True)
    kw_lower = keyword.lower()

    sections = split_into_sections(content)

    # 삽입할 (라인 인덱스, 텍스트) 목록 - 역순 처리용
    insertions: list[tuple[int, str]] = []

    for sec_start, sec_end, heading_text in sections:
        # 섹션 텍스트에 키워드 포함 여부 확인
        section_text = "".join(lines[sec_start:sec_end])
        if kw_lower not in section_text.lower():
            continue

        # 이미 크로스 레퍼런스 있으면 스킵
        if section_has_cross_ref(lines, sec_start, sec_end):
            continue

        # 삽입할 관련 포스트 링크들 (자기 자신 제외)
        ref_lines = []
        for related in related_posts:
            if related["path"] == target_post["path"]:
                continue
            ref_lines.append(build_cross_ref_line(related))

        if not ref_lines:
            continue

        # 섹션 마지막 실질 내용 라인 다음에 삽입
        insert_after = find_section_last_content_line(lines, sec_start, sec_end)
        ref_block = "\n" + "".join(ref_lines)
        insertions.append((insert_after, ref_block))

    if not insertions:
        return 0

    if dry_run:
        print(f"\n  [미리보기] {target_post['filename']}")
        for insert_after, ref_block in insertions:
            print(f"    → 라인 {insert_after + 1} 다음에 삽입:")
            for ref_line in ref_block.strip().splitlines():
                print(f"      {ref_line}")
        return len(insertions)

    # 역순으로 삽입 (라인 번호 밀림 방지)
    insertions.sort(key=lambda x: x[0], reverse=True)
    for insert_after, ref_block in insertions:
        lines.insert(insert_after + 1, ref_block)

    new_content = "".join(lines)
    target_post["path"].write_text(new_content, encoding="utf-8")
    return len(insertions)


def confirm_proceed(count: int, dry_run: bool, auto_yes: bool) -> bool:
    """작업 진행 여부 확인"""
    if dry_run or auto_yes:
        return True
    print(f"\n총 {count}개 포스트에 크로스 레퍼런스를 추가합니다.")
    answer = input("계속하시겠습니까? [y/N] ").strip().lower()
    return answer in ("y", "yes")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="포스트 간 크로스 레퍼런스 자동 추가",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python3 scripts/add_cross_references.py --keyword "Trivy"
  python3 scripts/add_cross_references.py --keyword "Trivy" --keyword "Log4Shell"
  python3 scripts/add_cross_references.py --keyword "SolarWinds" --dry-run
  python3 scripts/add_cross_references.py --keyword "Trivy" --days 30
        """,
    )
    parser.add_argument(
        "--keyword",
        action="append",
        required=True,
        metavar="KEYWORD",
        help="검색 키워드 (여러 번 지정 가능)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="변경 없이 미리보기만 출력",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=0,
        metavar="N",
        help="최근 N일 포스트만 대상 (0=전체, 기본값: 0)",
    )
    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="확인 없이 실행",
    )
    args = parser.parse_args()

    auto_yes = (
        args.yes
        or os.getenv("TECH_BLOG_AUTO_YES", "") == "1"
        or os.getenv("CI", "") == "1"
    )

    if args.dry_run:
        print("=== 드라이런 모드: 실제 파일은 변경되지 않습니다 ===\n")

    print(
        f"포스트 스캔 중... (대상: {'최근 ' + str(args.days) + '일' if args.days > 0 else '전체'})"
    )
    all_posts = scan_posts(args.days)
    print(f"  총 {len(all_posts)}개 포스트 발견\n")

    total_modified = 0
    total_insertions = 0

    for keyword in args.keyword:
        print(f"키워드 '{keyword}' 검색 중...")
        matched = find_keyword_posts(all_posts, keyword)

        if len(matched) < 2:
            print(
                f"  → '{keyword}' 포함 포스트가 {len(matched)}개로 크로스 레퍼런스 생성 불가 (최소 2개 필요)\n"
            )
            continue

        print(f"  → {len(matched)}개 포스트에서 발견:")
        for p in matched:
            print(f"     - {p['date_str']} {p['title']}")

        if not confirm_proceed(len(matched), args.dry_run, auto_yes):
            print("  → 건너뜁니다.\n")
            continue

        modified = 0
        insertions = 0

        for target in matched:
            count = add_cross_references_to_post(
                target_post=target,
                related_posts=matched,
                keyword=keyword,
                dry_run=args.dry_run,
            )
            if count > 0:
                modified += 1
                insertions += count
                if not args.dry_run:
                    print(f"  ✓ {target['filename']}: {count}개 섹션에 레퍼런스 추가")

        if not args.dry_run:
            print(
                f"\n  키워드 '{keyword}': {modified}개 포스트, {insertions}개 섹션 업데이트\n"
            )
        else:
            print(f"\n  키워드 '{keyword}': {insertions}개 섹션에 삽입 예정\n")

        total_modified += modified
        total_insertions += insertions

    if args.dry_run:
        print(f"=== 드라이런 완료: 총 {total_insertions}개 섹션에 삽입 예정 ===")
    else:
        print(
            f"=== 완료: 총 {total_modified}개 포스트, {total_insertions}개 섹션 업데이트 ==="
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
