#!/usr/bin/env python3
"""
⚠️ DEPRECATED: 이 스크립트는 더 이상 사용되지 않습니다.
대신 `verify_images_unified.py`를 사용하세요.

이미지 파일 검증 스크립트
- 이미지 파일 존재 여부 확인
- 이미지 파일명이 영어로 되어 있는지 확인
- 포스팅 파일의 이미지 경로와 실제 파일 매칭
"""

import re
import sys
from pathlib import Path
from typing import Dict, List

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

def has_korean(text: str) -> bool:
    """한글이 포함되어 있는지 확인"""
    korean_pattern = re.compile(r'[가-힣]')
    return bool(korean_pattern.search(text))

def extract_image_paths(content: str) -> List[str]:
    """포스팅 내용에서 이미지 경로 추출"""
    image_paths = []
    
    # Front Matter의 image 필드
    fm_match = re.search(r'^image:\s*(.+)$', content, re.MULTILINE)
    if fm_match:
        image_paths.append(fm_match.group(1).strip())
    
    # HTML img 태그
    img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    image_paths.extend(img_tags)
    
    # 마크다운 이미지 링크
    md_images = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
    image_paths.extend(md_images)
    
    # Jekyll relative_url 필터 제거
    cleaned_paths = []
    for path in image_paths:
        # {{ '/assets/images/...' | relative_url }} 형식 처리
        if "| relative_url" in path:
            path = path.split("|")[0].strip().strip("'\"")
        # /assets/images/로 시작하는 경로만
        if '/assets/images/' in path:
            filename = path.split('/assets/images/')[-1]
            cleaned_paths.append(filename)
        elif path.startswith('/assets/images/'):
            cleaned_paths.append(path.replace('/assets/images/', ''))
    
    return list(set(cleaned_paths))  # 중복 제거

def check_image_file(filename: str) -> Dict[str, any]:
    """이미지 파일 검증"""
    result = {
        'filename': filename,
        'exists': False,
        'has_korean': False,
        'file_path': None,
    }
    
    image_file = IMAGES_DIR / filename
    result['file_path'] = image_file
    result['exists'] = image_file.exists()
    result['has_korean'] = has_korean(filename)
    
    return result

def process_post_file(file_path: Path) -> Dict[str, any]:
    """포스팅 파일 처리"""
    result = {
        'file': str(file_path),
        'images': [],
        'issues': [],
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        image_paths = extract_image_paths(content)
        
        for img_path in image_paths:
            img_result = check_image_file(img_path)
            result['images'].append(img_result)
            
            if not img_result['exists']:
                result['issues'].append(f"이미지 파일을 찾을 수 없습니다: {img_path}")
            
            if img_result['has_korean']:
                result['issues'].append(f"이미지 파일명에 한글이 포함되어 있습니다: {img_path}")
        
        return result
        
    except Exception as e:
        result['issues'].append(f"처리 중 오류 발생: {str(e)}")
        return result

def main():
    """메인 함수"""
    if not POSTS_DIR.exists():
        print(f"포스팅 디렉토리를 찾을 수 없습니다: {POSTS_DIR}")
        sys.exit(1)
    
    if not IMAGES_DIR.exists():
        print(f"이미지 디렉토리를 찾을 수 없습니다: {IMAGES_DIR}")
        sys.exit(1)
    
    post_files = sorted(POSTS_DIR.glob("*.md"))
    
    if not post_files:
        print("처리할 포스팅 파일이 없습니다.")
        return
    
    print(f"총 {len(post_files)}개의 포스팅 파일을 검증합니다...\n")
    
    total_issues = 0
    missing_images = []
    korean_filenames = []
    
    for post_file in post_files:
        result = process_post_file(post_file)
        
        if result['issues']:
            print(f"📄 {post_file.name}")
            for issue in result['issues']:
                print(f"  ⚠️  {issue}")
                total_issues += 1
                
                if "찾을 수 없습니다" in issue:
                    missing_images.append({
                        'file': post_file.name,
                        'image': issue.split(': ')[-1] if ': ' in issue else ''
                    })
                elif "한글이 포함" in issue:
                    korean_filenames.append({
                        'file': post_file.name,
                        'image': issue.split(': ')[-1] if ': ' in issue else ''
                    })
            print()
    
    print(f"\n검증 완료:")
    print(f"  - 총 파일 수: {len(post_files)}")
    print(f"  - 발견된 문제: {total_issues}")
    
    if missing_images:
        print(f"\n⚠️  이미지 파일을 찾을 수 없는 포스팅 ({len(missing_images)}개):")
        for item in missing_images:
            print(f"  - {item['file']}: {item['image']}")
    
    if korean_filenames:
        print(f"\n⚠️  이미지 파일명에 한글이 포함된 포스팅 ({len(korean_filenames)}개):")
        for item in korean_filenames:
            print(f"  - {item['file']}: {item['image']}")
    
    if not missing_images and not korean_filenames:
        print("\n✅ 모든 이미지 파일이 정상적으로 검증되었습니다!")

if __name__ == "__main__":
    main()
