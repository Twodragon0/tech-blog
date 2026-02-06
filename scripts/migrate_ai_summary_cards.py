#!/usr/bin/env python3
"""
AI Summary Card HTML을 Jekyll include로 마이그레이션
기존 67개 포스트의 직접 HTML → Jekyll include 전환 스크립트
"""
import re
import sys
from pathlib import Path
from typing import Optional, Dict, List


def extract_ai_summary_html(content: str) -> Optional[Dict]:
    """기존 AI Summary Card HTML 파싱

    Returns:
        dict with 'html_block' and 'params' keys, or None if not found
    """
    # <div class="ai-summary-card"> ... </div> 블록 찾기
    pattern = r'<div class="ai-summary-card">.*?</div>\s*</div>'
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return None

    html_block = match.group(0)
    params = {}

    # 제목 추출 (첫 번째 summary-value)
    title_match = re.search(
        r'<span class="summary-label">제목</span>\s*<span class="summary-value">([^<]+)</span>',
        html_block
    )
    if title_match:
        params['title'] = title_match.group(1).strip()

    # 카테고리 HTML 추출
    cat_match = re.search(
        r'<span class="summary-label">카테고리</span>\s*<span class="summary-value">(.+?)</span>',
        html_block,
        re.DOTALL
    )
    if cat_match:
        cat_html = cat_match.group(1).strip()
        # 내부 span 태그만 추출
        params['categories_html'] = cat_html

    # 태그 HTML 추출
    tag_match = re.search(
        r'<span class="summary-label">태그</span>\s*<span class="summary-value tags">(.+?)</span>\s*</div>',
        html_block,
        re.DOTALL
    )
    if tag_match:
        tag_html = tag_match.group(1).strip()
        params['tags_html'] = tag_html

    # 핵심 내용 추출 (ul.summary-list)
    highlight_match = re.search(
        r'<span class="summary-label">핵심 내용</span>.*?<ul class="summary-list">(.+?)</ul>',
        html_block,
        re.DOTALL
    )
    if highlight_match:
        highlights_html = highlight_match.group(1).strip()
        params['highlights_html'] = highlights_html

    # 수집 기간 추출
    period_match = re.search(
        r'<span class="summary-label">수집 기간</span>\s*<span class="summary-value">([^<]+)</span>',
        html_block
    )
    if period_match:
        params['period'] = period_match.group(1).strip()

    # 대상 독자 추출
    audience_match = re.search(
        r'<span class="summary-label">대상 독자</span>\s*<span class="summary-value">([^<]+)</span>',
        html_block
    )
    if audience_match:
        params['audience'] = audience_match.group(1).strip()

    return {
        'html_block': html_block,
        'params': params
    }


def generate_include_tag(params: Dict) -> str:
    """Jekyll include 태그 생성

    복잡한 HTML을 포함할 수 있으므로 여러 줄 형식 사용
    """
    lines = ["{% include ai-summary-card.html"]

    for key, value in params.items():
        # 특수 문자 이스케이프 처리
        escaped = value.replace('"', '\\"')

        # 여러 줄 값의 경우 처리
        if '\n' in escaped or len(escaped) > 80:
            # 여러 줄이거나 긴 경우
            lines.append(f'  {key}="{escaped}"')
        else:
            lines.append(f'  {key}="{escaped}"')

    lines.append("%}")

    return "\n".join(lines)


def migrate_post(filepath: Path, dry_run: bool = True) -> bool:
    """포스트 마이그레이션

    Args:
        filepath: 포스트 파일 경로
        dry_run: True면 수정하지 않고 예상만 표시

    Returns:
        bool: 성공 여부
    """
    try:
        content = filepath.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ {filepath.name}: Failed to read - {e}")
        return False

    # AI Summary HTML 추출
    extracted = extract_ai_summary_html(content)

    if not extracted:
        print(f"⚠️  {filepath.name}: No AI Summary Card found")
        return False

    if not extracted['params'].get('title'):
        print(f"⚠️  {filepath.name}: Failed to extract title, skipping")
        return False

    # Include 태그 생성
    include_tag = generate_include_tag(extracted['params'])

    # HTML 블록 교체
    new_content = content.replace(extracted['html_block'], include_tag)

    if dry_run:
        print(f"✅ {filepath.name}: Would migrate")
        print(f"   Title: {extracted['params'].get('title', 'N/A')[:50]}")
        print(f"   Old HTML size: {len(extracted['html_block'])} chars")
        print(f"   New include size: {len(include_tag)} chars")
        print(f"   Size reduction: {len(extracted['html_block']) - len(include_tag)} chars saved")
        return True
    else:
        try:
            filepath.write_text(new_content, encoding='utf-8')
            print(f"✅ {filepath.name}: Migrated successfully")
            return True
        except Exception as e:
            print(f"❌ {filepath.name}: Failed to write - {e}")
            return False


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description='AI Summary Card HTML을 Jekyll include로 마이그레이션'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=True,
        help='Preview only (default)'
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Actually modify files'
    )
    parser.add_argument(
        '--pattern',
        default='_posts/*.md',
        help='File pattern to process (default: _posts/*.md)'
    )
    parser.add_argument(
        'files',
        nargs='*',
        help='Post files to migrate (optional, uses --pattern if not provided)'
    )

    args = parser.parse_args()
    dry_run = not args.apply

    # 파일 목록 결정
    if args.files:
        filepaths = [Path(f) for f in args.files]
    else:
        from glob import glob
        filepaths = [Path(f) for f in glob(args.pattern)]
        if not filepaths:
            print(f"❌ No files matching pattern: {args.pattern}")
            sys.exit(1)

    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    else:
        print("⚠️  APPLYING CHANGES TO FILES\n")

    success_count = 0
    fail_count = 0

    for filepath in sorted(filepaths):
        if filepath.exists() and filepath.suffix == '.md':
            if migrate_post(filepath, dry_run=dry_run):
                success_count += 1
            else:
                fail_count += 1
        elif filepath.exists():
            print(f"⚠️  {filepath.name}: Not a markdown file, skipping")
        else:
            print(f"❌ {filepath.name}: File not found")
            fail_count += 1

    print(f"\n📊 Summary: {success_count} success, {fail_count} failed")

    if dry_run:
        print("\n💡 Run with --apply to actually modify files")
        print(f"   Example: python3 scripts/migrate_ai_summary_cards.py --apply {args.pattern}")


if __name__ == '__main__':
    main()
