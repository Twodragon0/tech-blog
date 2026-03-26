#!/usr/bin/env python3
"""
SVG 파일에서 "..."로 잘린 제목 텍스트를 수정하는 스크립트.

전략:
1. assets/images/*.svg 에서 <text> 태그 내 "..."로 끝나는 텍스트 탐지
2. 원본 제목 소스 우선순위:
   a. 대응 _posts/*.md 파일의 image_alt 필드
   b. 잘린 text 자체 (앞부분) + 파일명 재구성
   c. SVG 파일명에서 제목 재구성
3. generate_post_images.py의 _truncate_title()로 새 축약 제목 생성 (max_len=45)
4. 2줄 제목 (연속된 glow 필터 text 태그) → 1줄로 합침
5. 한글 텍스트 포함 SVG는 건너뜀
"""

import glob
import re
import sys
from pathlib import Path

# generate_post_images.py의 _truncate_title import
sys.path.insert(0, str(Path(__file__).parent))
try:
    from generate_post_images import _truncate_title, _escape_svg_text
except ImportError:
    # fallback: 직접 정의
    def _truncate_title(title: str, max_len: int = 50) -> str:
        if not title:
            return "Tech Blog Post"
        if len(title) <= max_len:
            return title
        for delim in [" - ", ": ", ", ", " | "]:
            parts = [p.strip() for p in title.split(delim) if p.strip()]
            if len(parts) >= 2:
                result = parts[0]
                for part in parts[1:]:
                    candidate = result + " + " + part
                    if len(candidate) <= max_len:
                        result = candidate
                    else:
                        break
                if len(result) <= max_len:
                    return result
        skip_words = {
            "the", "a", "an", "and", "or", "of", "in", "on", "to", "for",
            "with", "from", "by", "is", "are", "was", "were", "be", "been",
            "complete", "guide", "practical", "comprehensive", "understanding",
            "overview", "introduction", "analysis", "perspective", "strategy",
        }
        words = [w for w in title.split() if w.lower() not in skip_words]
        result = ""
        for word in words:
            candidate = (result + " " + word).strip() if result else word
            if len(candidate) <= max_len:
                result = candidate
            else:
                break
        return result.rstrip(" ,;:-") if result else title.split()[0]

    def _escape_svg_text(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )


def has_korean(text: str) -> bool:
    """한글 문자 포함 여부 확인"""
    return bool(re.search(r'[\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F]', text))


def filename_to_title(stem: str) -> str:
    """SVG 파일명(확장자 제외)에서 영문 제목 재구성"""
    # YYYY-MM-DD- 제거
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', stem)
    # HTML entity 치환
    name = (name
            .replace('_ampamp_', ' & ')
            .replace('_amplsquo_', "'")
            .replace('_amprsquo_', "'")
            .replace('_ampquot_', '"')
            .replace('_amp_', ' & ')
            .replace('_-_', ' - '))
    # underscore → space
    name = name.replace('_', ' ')
    # 다중 공백 정리
    name = re.sub(r' +', ' ', name).strip()
    return name


def build_post_index(posts_dir: str) -> dict:
    """포스트 파일 인덱스 빌드: stem → {image_alt, title}"""
    index = {}
    for p in glob.glob(f'{posts_dir}/*.md'):
        stem = Path(p).stem
        try:
            with open(p, encoding='utf-8') as f:
                text = f.read(3000)
        except Exception:
            continue
        # image_alt 추출 (따옴표 포함 가능)
        alt_m = re.search(r'^image_alt:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
        title_m = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
        image_alt = alt_m.group(1).strip("\"' ") if alt_m else None
        post_title = title_m.group(1).strip("\"' ") if title_m else None
        index[stem] = {
            'image_alt': image_alt if image_alt else None,
            'title': post_title if post_title else None,
        }
    return index


def get_source_title(stem: str, post_index: dict) -> str:
    """원본 제목 결정: image_alt > 잘린 텍스트 복원 > 파일명"""
    post = post_index.get(stem, {})

    # 1순위: image_alt (영문 제목)
    image_alt = post.get('image_alt')
    if image_alt and not has_korean(image_alt):
        return image_alt.strip("\"' ")

    # 2순위: 포스트 title이 영문이면 사용
    post_title = post.get('title')
    if post_title and not has_korean(post_title):
        return post_title.strip("\"' ")

    # 3순위: 파일명에서 재구성
    return filename_to_title(stem)


def fix_svg_file(svg_path: str, post_index: dict) -> tuple[bool, str]:
    """
    SVG 파일의 잘린 제목 수정.
    Returns: (수정됨, 파일명)
    """
    try:
        with open(svg_path, encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"읽기 실패: {e}"

    stem = Path(svg_path).stem

    # 한글 포함 SVG 건너뜀
    if has_korean(content):
        return False, "한글 포함 건너뜀"

    # "..."로 끝나는 <text> 태그 확인
    trunc_pattern = re.compile(r'(<text[^>]*>)([^<]*\.\.\.)([^<]*</text>)')
    has_truncation = bool(trunc_pattern.search(content))

    if not has_truncation:
        return False, "잘린 텍스트 없음"

    # 원본 제목 확보
    source_title = get_source_title(stem, post_index)

    # _truncate_title로 새 축약 제목 생성 (max_len=45, "..."가 없어야 함)
    new_title = _truncate_title(source_title, 45)
    new_title_escaped = _escape_svg_text(new_title)

    original_content = content

    # --- 케이스 1: 2줄 제목 처리 (연속된 glow 필터 text 태그) ---
    # 패턴: <text ... filter="url(#glow...)">line1</text> 바로 뒤에 같은 패턴
    two_line_pattern = re.compile(
        r'(<text([^>]*)filter="url\(#glow[^"]*\)"([^>]*)>)([^<]+)(</text>)\s*\n'
        r'(\s*<text([^>]*)filter="url\(#glow[^"]*\)"([^>]*)>)([^<]+)(</text>)',
        re.MULTILINE
    )
    two_line_match = two_line_pattern.search(content)

    if two_line_match:
        # 2줄을 1줄로: 첫 번째 태그만 유지하고 두 번째 제거
        # font-size="30" → font-size="28" (긴 제목 수용)
        first_open = two_line_match.group(1)
        first_close = two_line_match.group(5)
        second_full = two_line_match.group(6) + two_line_match.group(9) + two_line_match.group(10)

        # font-size 축소
        new_first_open = re.sub(r'font-size="30"', 'font-size="28"', first_open)

        replacement = f'{new_first_open}{new_title_escaped}{first_close}'
        content = content[:two_line_match.start()] + replacement + content[two_line_match.end():]
    else:
        # --- 케이스 2: 단일 잘린 텍스트 교체 ---
        # 주 제목 text 태그 (glow 필터 또는 font-size="30")
        # font-size="30" → 28로 줄이기 (긴 제목 수용)
        def replace_truncated(m):
            open_tag = m.group(1)
            text_content = m.group(2)
            close_tag = m.group(3)
            # font-size 축소
            new_open = re.sub(r'font-size="30"', 'font-size="28"', open_tag)
            return f'{new_open}{new_title_escaped}{close_tag}'

        content = trunc_pattern.sub(replace_truncated, content)

    if content == original_content:
        return False, "변경 없음"

    # 파일 저장
    try:
        with open(svg_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        return False, f"저장 실패: {e}"

    return True, Path(svg_path).name


def main():
    base_dir = Path(__file__).parent.parent
    svg_dir = base_dir / 'assets' / 'images'
    posts_dir = base_dir / '_posts'

    print("포스트 인덱스 빌드 중...")
    post_index = build_post_index(str(posts_dir))
    print(f"  포스트 수: {len(post_index)}")

    svg_files = sorted(glob.glob(str(svg_dir / '*.svg')))
    print(f"  SVG 파일 수: {len(svg_files)}")
    print()

    fixed = []
    skipped = []
    errors = []

    for svg_path in svg_files:
        modified, reason = fix_svg_file(svg_path, post_index)
        if modified:
            fixed.append(reason)
            print(f"수정됨: {reason}")
        elif reason in ("한글 포함 건너뜀", "잘린 텍스트 없음", "변경 없음"):
            skipped.append((Path(svg_path).name, reason))
        else:
            errors.append((Path(svg_path).name, reason))
            print(f"오류: {Path(svg_path).name} - {reason}", file=sys.stderr)

    print()
    print(f"=== 완료 ===")
    print(f"수정됨: {len(fixed)}개")
    print(f"건너뜀: {len(skipped)}개")
    print(f"오류: {len(errors)}개")

    if errors:
        print("\n오류 목록:")
        for name, reason in errors:
            print(f"  {name}: {reason}")


if __name__ == '__main__':
    main()
