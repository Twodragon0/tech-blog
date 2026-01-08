#!/usr/bin/env python3
"""
포스트에서 중복된 원본 포스트 링크 제거 스크립트
레이아웃에서 이미 표시하므로 본문의 중복 링크를 제거합니다.
"""

import re
from pathlib import Path
from typing import Tuple

def remove_duplicate_original_links(content: str) -> Tuple[str, int]:
    """
    포스트 본문에서 중복된 원본 포스트 링크를 제거합니다.
    
    Returns:
        (cleaned_content, removed_count): 정리된 내용과 제거된 링크 개수
    """
    removed_count = 0
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 원본 포스트 링크 패턴 감지
        # 패턴 1: "원본 포스트: https://..."
        # 패턴 2: "원본 포스트: [https://...](https://...)"
        # 패턴 3: "**원본 포스트**: [https://...](https://...)"
        # 패턴 4: "---" 다음에 나오는 원본 포스트 링크들
        
        original_patterns = [
            r'^원본 포스트:\s*https?://',
            r'^원본 포스트:\s*\[https?://[^\]]+\]\(https?://[^\)]+\)',
            r'^\*\*원본 포스트\*\*:\s*\[https?://[^\]]+\]\(https?://[^\)]+\)',
            r'^원본 포스트:\s*\[https?://[^\]]+\]\(https?://[^\)]+\)',
        ]
        
        is_original_link = any(re.match(pattern, line.strip()) for pattern in original_patterns)
        
        if is_original_link:
            # 다음 줄들도 확인 (빈 줄이나 "---"가 나올 때까지)
            removed_count += 1
            i += 1
            
            # 연속된 빈 줄이나 구분선도 함께 제거
            while i < len(lines):
                next_line = lines[i].strip()
                if next_line == '' or next_line == '---':
                    # 빈 줄이나 구분선이면 제거하고 계속
                    if next_line == '---':
                        # 구분선 다음에 또 원본 포스트 링크가 있는지 확인
                        if i + 1 < len(lines):
                            next_next = lines[i + 1].strip()
                            if any(re.match(pattern, next_next) for pattern in original_patterns):
                                i += 1  # 구분선 건너뛰기
                                removed_count += 1
                                i += 1  # 중복 링크 건너뛰기
                                continue
                    i += 1
                elif any(re.match(pattern, next_line) for pattern in original_patterns):
                    # 또 다른 원본 포스트 링크 발견
                    removed_count += 1
                    i += 1
                else:
                    break
            continue
        
        result_lines.append(line)
        i += 1
    
    # 마지막에 남은 불필요한 구분선 제거
    while result_lines and result_lines[-1].strip() in ('', '---'):
        result_lines.pop()
    
    return '\n'.join(result_lines), removed_count

def process_post(post_file: Path) -> bool:
    """단일 포스트 파일 처리"""
    try:
        content = post_file.read_text(encoding='utf-8')
        original_content = content
        
        # Front matter와 본문 분리
        if not content.startswith('---'):
            print(f"⚠️  {post_file.name}: Front matter가 없습니다. 건너뜁니다.")
            return False
        
        # Front matter 끝 찾기
        front_matter_end = content.find('---', 3)
        if front_matter_end == -1:
            print(f"⚠️  {post_file.name}: Front matter가 올바르지 않습니다. 건너뜁니다.")
            return False
        
        front_matter = content[:front_matter_end + 3]
        body = content[front_matter_end + 3:].lstrip('\n')
        
        # 본문에서 중복 링크 제거
        cleaned_body, removed_count = remove_duplicate_original_links(body)
        
        if removed_count > 0:
            new_content = front_matter + '\n' + cleaned_body
            post_file.write_text(new_content, encoding='utf-8')
            print(f"✅ {post_file.name}: {removed_count}개의 중복 링크 제거")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ {post_file.name}: 오류 발생 - {e}")
        return False

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"❌ _posts 디렉토리를 찾을 수 없습니다: {posts_dir}")
        return
    
    post_files = list(posts_dir.glob('*.md'))
    
    if not post_files:
        print("포스트 파일을 찾을 수 없습니다.")
        return
    
    print(f"📝 {len(post_files)}개의 포스트 파일을 검사합니다...\n")
    
    processed = 0
    for post_file in sorted(post_files):
        if process_post(post_file):
            processed += 1
    
    print(f"\n✅ 완료: {processed}개의 포스트에서 중복 링크를 제거했습니다.")

if __name__ == '__main__':
    main()
