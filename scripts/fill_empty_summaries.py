#!/usr/bin/env python3
"""
빈 핵심 내용을 채우는 스크립트
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"


def extract_excerpt(post_file: Path) -> str:
    """포스팅에서 excerpt 추출"""
    content = post_file.read_text(encoding='utf-8')
    
    # Front matter에서 excerpt 추출
    front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        for line in front_matter_text.split('\n'):
            if line.startswith('excerpt:'):
                excerpt = line.split(':', 1)[1].strip().strip('"').strip("'")
                return excerpt
    
    return ""


def clean_excerpt_for_summary(excerpt: str) -> str:
    """excerpt를 요약용으로 정리"""
    if not excerpt:
        return ""
    
    # 서론 제거 패턴들
    intro_patterns = [
        r'^안녕하세요[^.]*\.',
        r'^[^.]*Twodragon[^.]*\.',
        r'^[^.]*이번 포스트[^.]*\.',
        r'^[^.]*이번 포스팅[^.]*\.',
        r'^[^.]*본 포스팅[^.]*\.',
        r'^[^.]*이번 달에는[^.]*\.',
        r'^[^.]*이번 주차[^.]*\.',
        r'^[^.]*온라인 미팅[^.]*\.',
        r'^[^.]*게더 타운[^.]*\.',
        r'^[^.]*20분[^.]*\.',
        r'^[^.]*5분[^.]*\.',
        r'^[^.]*지난[^.]*\.',
        r'^[^.]*12월은[^.]*\.',
        r'^[^.]*이번 달[^.]*\.',
        r'^[^.]*참석하며[^.]*\.',
        r'^[^.]*느낄 수 있었습니다[^.]*\.',
        r'^[^.]*본 포스팅에서는[^.]*\.',
        r'\.\.\.$',  # 말줄임표
    ]
    
    cleaned = excerpt
    for pattern in intro_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # 연속된 공백 정리
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def fill_empty_summary(post_file: Path):
    """빈 핵심 내용 채우기"""
    content = post_file.read_text(encoding='utf-8')
    
    # 빈 핵심 내용 찾기
    empty_match = re.search(
        r'> \*\*핵심 내용\*\*:\s*\n(> ---|> \*이 포스팅)',
        content,
        re.MULTILINE
    )
    
    if not empty_match:
        return False
    
    # excerpt 추출 및 정리
    excerpt = extract_excerpt(post_file)
    cleaned_excerpt = clean_excerpt_for_summary(excerpt)
    
    if not cleaned_excerpt:
        return False
    
    # 핵심 내용 채우기
    new_content = (
        content[:empty_match.start()] +
        f"> **핵심 내용**: {cleaned_excerpt}\n" +
        content[empty_match.end():]
    )
    
    post_file.write_text(new_content, encoding='utf-8')
    return True


def main():
    posts = list(POSTS_DIR.glob("*.md"))
    print(f"📊 {len(posts)}개 포스팅 확인 중...")
    
    filled = 0
    for post_file in posts:
        if fill_empty_summary(post_file):
            print(f"✅ 채움: {post_file.name}")
            filled += 1
    
    print(f"\n완료: {filled}개 파일의 핵심 내용 채움")


if __name__ == '__main__':
    main()
