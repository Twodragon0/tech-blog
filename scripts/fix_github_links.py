#!/usr/bin/env python3
"""
⚠️ DEPRECATED: 이 스크립트는 더 이상 사용되지 않습니다.
대신 `fix_links_unified.py`를 사용하세요.

포스트 파일의 GitHub 링크를 검증하고 개선하는 스크립트
"""
import re
import os
from pathlib import Path
from typing import Optional

# GitHub 도메인 패턴
GITHUB_PATTERN = r'https?://(?:www\.)?github\.com/'

# 부적절한 링크 매핑 (GitHub가 아닌 링크)
INVALID_LINKS = {
    'https://www.gnu.org/software/bash/manual/bash.html': {
        'text': 'Bash 공식 문서',
        'link': 'https://www.gnu.org/software/bash/manual/bash.html'
    },
    'https://www.json.org/json-en.html': {
        'text': 'JSON 공식 문서',
        'link': 'https://www.json.org/json-en.html'
    }
}

def is_github_link(url: str) -> bool:
    """URL이 GitHub 링크인지 확인"""
    return bool(re.search(GITHUB_PATTERN, url))

def fix_link_text(match) -> str:
    """링크 텍스트를 적절하게 수정"""
    full_match = match.group(0)
    url = match.group(2)
    
    # GitHub 링크인지 확인
    if is_github_link(url):
        return full_match  # GitHub 링크는 그대로 유지
    
    # GitHub가 아닌 링크 처리
    if url in INVALID_LINKS:
        info = INVALID_LINKS[url]
        # "GitHub 예제 저장소"를 적절한 텍스트로 변경
        new_text = match.group(1).replace('GitHub 예제 저장소', info['text'])
        new_text = new_text.replace('GitHub 예제', info['text'])
        return f'[{new_text}]({url})'
    
    # 기타 GitHub가 아닌 링크
    new_text = match.group(1).replace('GitHub 예제 저장소', '공식 문서')
    new_text = new_text.replace('GitHub 예제', '공식 문서')
    return f'[{new_text}]({url})'

def fix_code_blocks(content: str) -> str:
    """코드 블록 관련 문제 수정"""
    # 1. 주석 처리된 짧은 코드 블록 복원 (DNS 레코드, 설정 예시 등)
    # 주석 처리된 코드 블록 패턴
    comment_pattern = r'<!-- (?:긴 코드 블록 제거됨|코드 블록 제거됨).*?```(\w+)?\n(.*?)```\n-->'
    
    def restore_short_code(match):
        language = match.group(1) or ''
        code_block = match.group(2)
        
        # 코드 블록 길이 확인
        lines = code_block.strip().split('\n')
        code_length = len(code_block.strip())
        
        # 짧은 코드 블록 (5줄 이하, 200자 이하)은 복원
        if len(lines) <= 5 and code_length <= 200:
            # DNS 레코드, 설정 예시, DMARC 설정 등은 복원
            keywords = ['dns', 'txt', 'record', '레코드', '설정', 'config', 'dmarc', 'spf', 'dkim', 'v=dmarc', 'v=spf']
            if any(keyword in code_block.lower() for keyword in keywords):
                return f'```{language}\n{code_block}\n```'
        
        return match.group(0)  # 긴 코드는 주석 유지
    
    content = re.sub(comment_pattern, restore_short_code, content, flags=re.DOTALL)
    
    # 2. 주석 내 "위 GitHub 링크 참조" 텍스트 수정
    # GitHub가 아닌 링크인 경우 주석 텍스트 수정
    comment_link_pattern = r'<!-- 전체 코드는 위 (GitHub )?링크 참조'
    
    def fix_comment_text(match):
        # 앞뒤 맥락 확인하여 GitHub 링크인지 확인
        start_pos = match.start()
        # 앞 500자 확인
        context = content[max(0, start_pos-500):start_pos+100]
        if 'github.com' not in context.lower():
            return '<!-- 전체 코드는 위 링크 참조'
        return match.group(0)
    
    content = re.sub(comment_link_pattern, fix_comment_text, content)
    
    # 3. 링크 텍스트 수정
    link_pattern = r'\[([^\]]+)\]\((https?://[^\)]+)\)'
    content = re.sub(link_pattern, fix_link_text, content)
    
    # 4. JSON 코드 블록의 경우 GitHub 링크 대신 공식 문서 링크 사용
    json_pattern = r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/[^\)]+\)를 참조하세요\.\n> \n> ```json\n'
    json_replacement = r'> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.\n> \n> ```json\n'
    content = re.sub(json_pattern, json_replacement, content)
    
    return content

def process_post_file(file_path: Path) -> bool:
    """포스트 파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 수정 전 내용 저장
        original_content = content
        
        # 코드 블록 및 링크 수정
        new_content = fix_code_blocks(content)
        
        # 변경사항이 있는지 확인
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    processed = 0
    updated = 0
    
    for post_file in posts_dir.glob('*.md'):
        processed += 1
        if process_post_file(post_file):
            updated += 1
            print(f"Updated: {post_file.name}")
    
    print(f"\nProcessed: {processed} files")
    print(f"Updated: {updated} files")

if __name__ == '__main__':
    main()
