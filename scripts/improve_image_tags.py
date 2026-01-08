#!/usr/bin/env python3
"""
기존 HTML 이미지 태그를 개선하는 스크립트
- lazy loading 추가
- 클래스 추가
- 성능 최적화
"""

import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def improve_image_tags(content: str) -> str:
    """
    기존 HTML 이미지 태그를 개선
    
    변경 전: <img src="{{ '...' | relative_url }}" alt="...">
    변경 후: <img src="{{ '...' | relative_url }}" alt="..." loading="lazy" class="post-image">
    """
    # 패턴: <img src="{{ 'path' | relative_url }}" alt="...">
    # 이미 loading이나 class가 없는 경우에만 추가
    pattern = r'<img src="\{\{\s*[\'"]([^\'"]+)[\'"]\s*\|\s*relative_url\s*\}\}" alt="([^"]+)"(?:\s+[^>]*)?>'
    
    def replace_func(match):
        image_path = match.group(1)
        alt_text = match.group(2)
        full_match = match.group(0)
        
        # 이미 loading이나 class가 있으면 스킵
        if 'loading=' in full_match or 'class=' in full_match:
            return full_match
        
        # 개선된 태그 생성
        return f'<img src="{{ \'{image_path}\' | relative_url }}" alt="{alt_text}" loading="lazy" class="post-image">'
    
    return re.sub(pattern, replace_func, content)

def process_post(post_file: Path) -> bool:
    """단일 포스트 파일 처리"""
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 변경 전 내용 저장
        original_content = content
        
        # 이미지 태그 개선
        improved_content = improve_image_tags(content)
        
        # 변경사항이 있으면 파일 저장
        if improved_content != original_content:
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(improved_content)
            print(f"✅ Improved: {post_file.name}")
            return True
        else:
            print(f"⏭️  No changes: {post_file.name}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {post_file.name}: {e}")
        return False

def main():
    """메인 함수"""
    if not POSTS_DIR.exists():
        print(f"❌ Posts directory not found: {POSTS_DIR}")
        sys.exit(1)
    
    post_files = list(POSTS_DIR.glob("*.md"))
    print(f"📄 Found {len(post_files)} post files")
    print("🔧 Improving image tags with lazy loading and classes...\n")
    
    improved_count = 0
    for post_file in sorted(post_files):
        if process_post(post_file):
            improved_count += 1
    
    print(f"\n✨ Improved {improved_count} out of {len(post_files)} files")

if __name__ == "__main__":
    main()
