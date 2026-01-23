#!/usr/bin/env python3
"""
최종 포스팅 구조 검증 스크립트
- Front Matter 구조 검증
- 필수 필드 확인
- 이미지 파일 검증
"""

import re
import sys
from pathlib import Path
from typing import Dict, List

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# 필수 필드
REQUIRED_FIELDS = ['layout', 'title', 'date', 'categories', 'tags', 'excerpt']

# 표준 필드 순서
STANDARD_ORDER = [
    'layout', 'title', 'date', 'categories', 'tags', 
    'excerpt', 'comments', 'original_url', 'image', 
    'image_alt', 'toc', 'certifications'
]

def extract_front_matter(content: str) -> tuple[Dict[str, str], str]:
    """Front Matter 추출"""
    front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    
    if not match:
        return {}, content
    
    front_matter_text = match.group(1)
    body = match.group(2)
    
    # Front Matter 파싱
    front_matter = {}
    current_key = None
    current_value = []
    
    for line in front_matter_text.split('\n'):
        key_match = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if key_match:
            if current_key:
                front_matter[current_key] = '\n'.join(current_value).strip()
            current_key = key_match.group(1)
            value = key_match.group(2).strip()
            current_value = [value] if value else []
        elif current_key:
            if line.strip() or current_value:
                current_value.append(line)
    
    if current_key:
        front_matter[current_key] = '\n'.join(current_value).strip()
    
    return front_matter, body

def check_field_order(front_matter: Dict[str, str]) -> List[str]:
    """필드 순서 확인"""
    issues = []
    keys = list(front_matter.keys())
    
    # 표준 순서와 비교
    for i, standard_field in enumerate(STANDARD_ORDER):
        if standard_field in keys:
            actual_index = keys.index(standard_field)
            if actual_index != i:
                # 순서가 다르지만 필수 필드는 아니므로 경고만
                if standard_field in REQUIRED_FIELDS:
                    issues.append(f"필수 필드 '{standard_field}'의 순서가 표준과 다릅니다 (예상: {i}, 실제: {actual_index})")
    
    return issues

def check_required_fields(front_matter: Dict[str, str]) -> List[str]:
    """필수 필드 확인"""
    issues = []
    
    for field in REQUIRED_FIELDS:
        if field not in front_matter or not front_matter[field]:
            issues.append(f"필수 필드 '{field}'가 없습니다")
    
    return issues

def check_image_exists(image_path: str) -> bool:
    """이미지 파일 존재 여부 확인"""
    if not image_path:
        return False
    
    if '/assets/images/' in image_path:
        filename = image_path.split('/assets/images/')[-1]
    else:
        filename = image_path
    
    image_file = IMAGES_DIR / filename
    return image_file.exists()

def has_ai_summary(content: str) -> bool:
    """AI 요약 카드 존재 여부 확인"""
    return '<div class="ai-summary-card">' in content or '## 📋 포스팅 요약' in content

def process_post_file(file_path: Path) -> Dict[str, any]:
    """포스팅 파일 처리"""
    result = {
        'file': str(file_path.name),
        'issues': [],
        'warnings': [],
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        front_matter, body = extract_front_matter(content)
        
        if not front_matter:
            result['issues'].append("Front Matter를 찾을 수 없습니다")
            return result
        
        # 필수 필드 확인
        required_issues = check_required_fields(front_matter)
        result['issues'].extend(required_issues)
        
        # 필드 순서 확인 (경고만)
        order_warnings = check_field_order(front_matter)
        result['warnings'].extend(order_warnings)
        
        # 이미지 확인
        image_path = front_matter.get('image', '')
        if image_path:
            if not check_image_exists(image_path):
                result['issues'].append(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        else:
            result['warnings'].append("image 필드가 없습니다")
        
        # AI 요약 확인
        if not has_ai_summary(content):
            result['warnings'].append("AI 요약 카드가 없습니다")
        
        return result
        
    except Exception as e:
        result['issues'].append(f"처리 중 오류 발생: {str(e)}")
        return result

def main():
    """메인 함수"""
    if not POSTS_DIR.exists():
        print(f"포스팅 디렉토리를 찾을 수 없습니다: {POSTS_DIR}")
        sys.exit(1)
    
    post_files = sorted(POSTS_DIR.glob("*.md"))
    
    if not post_files:
        print("처리할 포스팅 파일이 없습니다.")
        return
    
    print(f"총 {len(post_files)}개의 포스팅 파일을 검증합니다...\n")
    
    total_issues = 0
    total_warnings = 0
    files_with_issues = []
    files_with_warnings = []
    
    for post_file in post_files:
        result = process_post_file(post_file)
        
        if result['issues'] or result['warnings']:
            if result['issues']:
                print(f"❌ {result['file']}")
                for issue in result['issues']:
                    print(f"   ⚠️  {issue}")
                    total_issues += 1
                files_with_issues.append(result['file'])
            
            if result['warnings']:
                if not result['issues']:
                    print(f"⚠️  {result['file']}")
                for warning in result['warnings']:
                    print(f"   ⚠️  {warning}")
                    total_warnings += 1
                files_with_warnings.append(result['file'])
            
            if result['issues'] or result['warnings']:
                print()
    
    print(f"\n검증 완료:")
    print(f"  - 총 파일 수: {len(post_files)}")
    print(f"  - 문제가 있는 파일: {len(files_with_issues)}")
    print(f"  - 경고가 있는 파일: {len(files_with_warnings)}")
    print(f"  - 총 문제 수: {total_issues}")
    print(f"  - 총 경고 수: {total_warnings}")
    
    if not files_with_issues and not files_with_warnings:
        print("\n✅ 모든 포스팅 파일이 정상적으로 검증되었습니다!")
    elif not files_with_issues:
        print("\n✅ 모든 필수 필드가 정상적으로 설정되었습니다!")
        print("   (일부 경고가 있지만 필수 사항은 모두 충족)")

if __name__ == "__main__":
    main()
