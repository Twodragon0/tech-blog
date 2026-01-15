#!/usr/bin/env python3
"""
포스팅 구조 표준화 스크립트
- Front Matter 정리 (불필요한 내용 제거)
- 필드 순서 표준화
- 이미지 경로 검증
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# 표준 Front Matter 필드 순서
STANDARD_FIELDS = [
    "layout",
    "title",
    "date",
    "categories",
    "tags",
    "excerpt",
    "comments",
    "original_url",
    "image",
    "image_alt",
    "toc",
    "certifications",
]

def extract_front_matter(content: str) -> Tuple[Dict[str, str], str, str]:
    """Front Matter를 추출하고 본문과 분리"""
    front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    
    if not match:
        return {}, content, ""
    
    front_matter_text = match.group(1)
    body = match.group(2)
    
    # Front Matter 파싱
    front_matter = {}
    current_key = None
    current_value = []
    
    for line in front_matter_text.split('\n'):
        # 키-값 쌍 매칭
        key_match = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if key_match:
            # 이전 키 저장
            if current_key:
                front_matter[current_key] = '\n'.join(current_value).strip()
            current_key = key_match.group(1)
            value = key_match.group(2).strip()
            current_value = [value] if value else []
        elif current_key and line.strip():
            # 멀티라인 값
            current_value.append(line)
        elif current_key and not line.strip():
            # 빈 줄은 값의 일부로 간주
            if current_value:
                current_value.append('')
    
    # 마지막 키 저장
    if current_key:
        front_matter[current_key] = '\n'.join(current_value).strip()
    
    return front_matter, body, front_matter_text

def clean_front_matter(front_matter: Dict[str, str]) -> Dict[str, str]:
    """Front Matter 정리 (불필요한 내용 제거)"""
    cleaned = {}
    
    for key, value in front_matter.items():
        # mermaid 다이어그램이나 코드 블록이 포함된 경우 제거
        if '```mermaid' in value or '```' in value:
            continue
        # 빈 값 제거
        if not value or not value.strip():
            continue
        cleaned[key] = value
    
    return cleaned

def build_standard_front_matter(front_matter: Dict[str, str]) -> str:
    """표준 형식의 Front Matter 생성"""
    lines = ['---']
    
    # 표준 순서대로 필드 추가
    for field in STANDARD_FIELDS:
        if field in front_matter:
            value = front_matter[field]
            # 배열 형식 처리
            if isinstance(value, list):
                lines.append(f"{field}: {value}")
            elif field in ['categories', 'tags', 'certifications'] and value.startswith('['):
                lines.append(f"{field}: {value}")
            else:
                # 문자열 값은 따옴표 처리
                if '\n' in value:
                    # 멀티라인 값
                    lines.append(f"{field}: |")
                    for line in value.split('\n'):
                        lines.append(f"  {line}")
                else:
                    lines.append(f"{field}: {value}")
    
    # 표준 필드에 없는 추가 필드들 (나중에 추가)
    for key, value in front_matter.items():
        if key not in STANDARD_FIELDS:
            if isinstance(value, list):
                lines.append(f"{key}: {value}")
            elif '\n' in value:
                lines.append(f"{key}: |")
                for line in value.split('\n'):
                    lines.append(f"  {line}")
            else:
                lines.append(f"{key}: {value}")
    
    lines.append('---')
    return '\n'.join(lines)

def check_image_exists(image_path: str) -> bool:
    """이미지 파일 존재 여부 확인"""
    if not image_path:
        return False
    
    # 경로에서 /assets/images/ 제거하고 파일명만 추출
    if '/assets/images/' in image_path:
        filename = image_path.split('/assets/images/')[-1]
    else:
        filename = image_path
    
    image_file = IMAGES_DIR / filename
    return image_file.exists()

def process_post_file(file_path: Path) -> Dict[str, any]:
    """포스팅 파일 처리"""
    result = {
        'file': str(file_path),
        'fixed': False,
        'issues': [],
        'image_exists': False,
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Front Matter 추출
        front_matter, body, original_fm_text = extract_front_matter(content)
        
        if not front_matter:
            result['issues'].append("Front Matter를 찾을 수 없습니다")
            return result
        
        # Front Matter 정리
        cleaned_fm = clean_front_matter(front_matter)
        
        # 이미지 경로 확인
        image_path = cleaned_fm.get('image', '')
        if image_path:
            result['image_exists'] = check_image_exists(image_path)
            if not result['image_exists']:
                result['issues'].append(f"이미지 파일을 찾을 수 없습니다: {image_path}")
        
        # Front Matter에 불필요한 내용이 있는지 확인
        if original_fm_text != build_standard_front_matter(cleaned_fm):
            # mermaid나 코드 블록이 포함되어 있는지 확인
            if '```mermaid' in original_fm_text or '```' in original_fm_text:
                result['issues'].append("Front Matter에 코드 블록이 포함되어 있습니다")
                result['fixed'] = True
                
                # 정리된 Front Matter로 재구성
                new_front_matter = build_standard_front_matter(cleaned_fm)
                new_content = new_front_matter + '\n\n' + body
                
                # 파일 저장
                file_path.write_text(new_content, encoding='utf-8')
                result['fixed'] = True
        
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
    
    print(f"총 {len(post_files)}개의 포스팅 파일을 처리합니다...\n")
    
    fixed_count = 0
    issues_count = 0
    missing_images = []
    
    for post_file in post_files:
        result = process_post_file(post_file)
        
        if result['issues']:
            print(f"📄 {post_file.name}")
            for issue in result['issues']:
                print(f"  ⚠️  {issue}")
                issues_count += 1
            
            if result['fixed']:
                print(f"  ✅ 수정 완료")
                fixed_count += 1
            
            if not result['image_exists'] and result.get('image_path'):
                missing_images.append({
                    'file': post_file.name,
                    'image': result.get('image_path', '')
                })
            print()
    
    print(f"\n처리 완료:")
    print(f"  - 총 파일 수: {len(post_files)}")
    print(f"  - 수정된 파일: {fixed_count}")
    print(f"  - 발견된 문제: {issues_count}")
    
    if missing_images:
        print(f"\n이미지 파일을 찾을 수 없는 포스팅:")
        for item in missing_images:
            print(f"  - {item['file']}: {item['image']}")

if __name__ == "__main__":
    main()
