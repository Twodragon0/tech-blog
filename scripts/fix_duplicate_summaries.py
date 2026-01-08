#!/usr/bin/env python3
"""
중복된 요약 섹션 수정 스크립트
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"


def fix_duplicate_summary(post_file: Path):
    """중복된 요약 섹션 수정"""
    content = post_file.read_text(encoding='utf-8')
    
    # 요약 섹션 찾기
    summary_match = re.search(
        r'(## 📋 포스팅 요약\n\n)(.*?)(\n\n[^>]|\Z)',
        content,
        re.DOTALL
    )
    
    if not summary_match:
        return False
    
    summary_section = summary_match.group(2)
    
    # 중복된 "> **카테고리**", "> **태그**", "> **핵심 내용**" 패턴 찾기
    # 첫 번째 완전한 요약만 유지
    lines = summary_section.split('\n')
    seen = set()
    cleaned_lines = []
    in_summary = False
    
    for line in lines:
        if line.strip().startswith('> **'):
            key = line.strip().split(':')[0] if ':' in line else line.strip()
            if key in seen and key.startswith('> **카테고리') or key.startswith('> **태그') or key.startswith('> **핵심 내용'):
                # 중복 발견, 이 이후의 내용은 건너뛰기
                if '---' in line or '*이 포스팅은' in line:
                    cleaned_lines.append(line)
                continue
            seen.add(key)
        cleaned_lines.append(line)
    
    # 빈 핵심 내용 제거
    final_lines = []
    skip_empty_core = False
    for i, line in enumerate(cleaned_lines):
        if '> **핵심 내용**:' in line and not cleaned_lines[i+1].strip():
            skip_empty_core = True
            continue
        if skip_empty_core and line.strip() and not line.startswith('>'):
            skip_empty_core = False
        if not skip_empty_core:
            final_lines.append(line)
    
    new_summary = '\n'.join(final_lines)
    
    # 파일 업데이트
    new_content = (
        content[:summary_match.start(2)] +
        new_summary +
        content[summary_match.end(2):]
    )
    
    post_file.write_text(new_content, encoding='utf-8')
    return True


def main():
    posts = list(POSTS_DIR.glob("*.md"))
    print(f"📊 {len(posts)}개 포스팅 확인 중...")
    
    fixed = 0
    for post_file in posts:
        if fix_duplicate_summary(post_file):
            print(f"✅ 수정: {post_file.name}")
            fixed += 1
    
    print(f"\n완료: {fixed}개 파일 수정됨")


if __name__ == '__main__':
    main()
