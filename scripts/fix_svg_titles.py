#!/usr/bin/env python3
"""SVG 파일에 누락된 <title> 요소를 일괄 삽입하는 스크립트"""

import argparse
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

PROJECT_ROOT = Path(__file__).parent.parent
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# Date prefix pattern: YYYY-MM-DD-
DATE_PREFIX_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-")

# Special encoding replacements in filenames
ENCODING_MAP = {
    "ampamp": "&",
    "ampquot": '"',
    "amplsquo": "'",
    "amprsquo": "'",
}


def extract_title(filename: str) -> str:
    """파일명에서 SVG title 텍스트를 추출한다."""
    stem = Path(filename).stem  # 확장자 제거
    # 날짜 접두사 제거
    stem = DATE_PREFIX_RE.sub("", stem)
    # 언더스코어 → 공백
    stem = stem.replace("_", " ")
    # 특수 인코딩 치환
    for encoded, decoded in ENCODING_MAP.items():
        stem = stem.replace(encoded, decoded)
    return stem.strip()


def insert_title(content: str, title: str) -> str:
    """SVG 내용에 <title> 요소를 삽입한다.

    <svg ...> 태그 닫는 > 바로 다음 줄에 삽입한다.
    멀티라인 svg 태그도 처리한다.
    """
    # <svg ...> 태그 끝 위치 찾기 (속성이 여러 줄에 걸칠 수 있음)
    svg_close = content.find(">")
    if svg_close == -1:
        return content  # 잘못된 SVG

    before = content[: svg_close + 1]
    after = content[svg_close + 1 :]

    title_line = f"\n  <title>{xml_escape(title)}</title>"
    return before + title_line + after


def process_file(path: Path, dry_run: bool) -> bool:
    """파일을 처리한다. 변경됐으면 True 반환."""
    content = path.read_text(encoding="utf-8")

    if "<title>" in content:
        return False  # 이미 title 있음

    title = extract_title(path.name)
    new_content = insert_title(content, title)

    if dry_run:
        print(f"[DRY-RUN] {path.name}")
        print(f"          title: {title}")
        return True

    path.write_text(new_content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SVG 파일에 누락된 <title> 요소를 일괄 삽입합니다."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="변경을 적용하지 않고 대상 파일만 출력합니다.",
    )
    args = parser.parse_args()

    svg_files = sorted(IMAGES_DIR.glob("*.svg"))
    if not svg_files:
        print(f"SVG 파일을 찾을 수 없습니다: {IMAGES_DIR}", file=sys.stderr)
        return 1

    changed = 0
    skipped = 0

    for path in svg_files:
        if process_file(path, args.dry_run):
            changed += 1
        else:
            skipped += 1

    mode = "DRY-RUN" if args.dry_run else "완료"
    print(
        f"\n[{mode}] 처리: {changed}개 파일 {'대상' if args.dry_run else '수정'} / "
        f"{skipped}개 파일 건너뜀 (이미 title 있음) / 전체 {len(svg_files)}개"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
