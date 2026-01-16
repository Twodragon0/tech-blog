#!/usr/bin/env python3
"""
머메이드 차트의 점선 화살표(`-.->`)를 일반 화살표(`-->`)로 변경하는 스크립트
머메이드 10.9.5 호환성을 위해 수정
"""
import os
import re
from pathlib import Path

def fix_mermaid_dotted_arrows(file_path):
    """파일의 점선 화살표를 일반 화살표로 변경"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 점선 화살표를 일반 화살표로 변경
        original_content = content
        # -\.-> 패턴을 --> 로 변경
        content = content.replace('-.->', '-->')
        
        # 변경사항이 있으면 파일 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
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
    
    files_modified = 0
    files_with_dotted = []
    
    # 모든 마크다운 파일 검색
    for md_file in posts_dir.glob('*.md'):
        # 점선 화살표가 있는지 확인
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if '-.->' in content:
                    files_with_dotted.append(md_file)
        except Exception as e:
            print(f"Error reading {md_file}: {e}")
            continue
    
    # 점선 화살표가 있는 파일 수정
    for md_file in files_with_dotted:
        if fix_mermaid_dotted_arrows(md_file):
            files_modified += 1
            print(f"Fixed: {md_file.name}")
    
    print(f"\nTotal files with dotted arrows: {len(files_with_dotted)}")
    print(f"Files modified: {files_modified}")

if __name__ == '__main__':
    main()
