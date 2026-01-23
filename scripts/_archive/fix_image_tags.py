#!/usr/bin/env python3
"""
마크다운 이미지 태그를 HTML 형식으로 변경하는 스크립트
kramdown이 마크다운 링크 내부의 Liquid 문법을 처리하지 못하는 문제 해결
"""

import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def fix_image_tags(content: str) -> str:
    """
    마크다운 이미지 태그를 HTML 형식으로 변경 (개선된 버전)
    
    변경 전: ![포스트 이미지]({{ '/assets/images/...' | relative_url }})
    변경 후: <img src="{{ '/assets/images/...' | relative_url }}" alt="포스트 이미지" loading="lazy" class="post-image">
    """
    # 패턴: ![alt text]({{ 'path' | relative_url }})
    pattern = r'!\[([^\]]+)\]\(\{\{\s*[\'"]([^\'"]+)[\'"]\s*\|\s*relative_url\s*\}\}\)'
    
    def replace_func(match):
        alt_text = match.group(1)
        image_path = match.group(2)
        # lazy loading과 클래스 추가로 성능 및 스타일 개선
        return '<img src="{{ \'' + image_path + '\' | relative_url }}" alt="' + alt_text + '" loading="lazy" class="post-image">'
    
    return re.sub(pattern, replace_func, content)

def process_post(post_file: Path) -> bool:
    """단일 포스트 파일 처리"""
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 변경 전 내용 저장
        original_content = content
        
        # 이미지 태그 수정
        fixed_content = fix_image_tags(content)
        
        # 변경사항이 있으면 파일 저장
        if fixed_content != original_content:
            with open(post_file, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            print(f"✅ Fixed: {post_file.name}")
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
    
    fixed_count = 0
    for post_file in sorted(post_files):
        if process_post(post_file):
            fixed_count += 1
    
    print(f"\n✨ Fixed {fixed_count} out of {len(post_files)} files")

if __name__ == "__main__":
    main()
