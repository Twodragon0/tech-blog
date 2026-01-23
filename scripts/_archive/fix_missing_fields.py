#!/usr/bin/env python3
"""
누락된 필수 필드 자동 보완 스크립트
- category -> categories 변환
- AI 요약 카드에서 categories, tags 추출
- excerpt 생성 또는 AI 요약에서 추출
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"

def extract_categories_from_summary(content: str) -> Optional[List[str]]:
    """AI 요약 카드에서 categories 추출"""
    # HTML 형식
    pattern = r'<span class="category-tag\s+(\w+)">([^<]+)</span>'
    matches = re.findall(pattern, content)
    if matches:
        return [match[0] for match in matches]
    
    # 마크다운 형식
    pattern = r'\*\*카테고리\*\*:\s*([^\n]+)'
    match = re.search(pattern, content)
    if match:
        categories_text = match.group(1)
        # 쉼표로 구분된 카테고리 추출
        categories = [c.strip() for c in categories_text.split(',')]
        return categories
    
    return None

def extract_tags_from_summary(content: str) -> Optional[List[str]]:
    """AI 요약 카드에서 tags 추출"""
    # HTML 형식
    pattern = r'<span class="tag">([^<]+)</span>'
    matches = re.findall(pattern, content)
    if matches:
        return [tag.strip() for tag in matches]
    
    # 마크다운 형식
    pattern = r'\*\*태그\*\*:\s*([^\n]+)'
    match = re.search(pattern, content)
    if match:
        tags_text = match.group(1)
        tags = [t.strip() for t in tags_text.split(',')]
        return tags
    
    return None

def extract_excerpt_from_summary(content: str) -> Optional[str]:
    """AI 요약 카드의 핵심 내용에서 excerpt 생성"""
    # 핵심 내용 추출
    pattern = r'<ul class="summary-list">(.*?)</ul>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        # 첫 번째 항목의 텍스트 추출
        first_item = re.search(r'<li>(.*?)</li>', match.group(1), re.DOTALL)
        if first_item:
            text = re.sub(r'<[^>]+>', '', first_item.group(1)).strip()
            # 첫 200자만 사용
            if len(text) > 200:
                text = text[:197] + "..."
            return text
    
    return None

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

def build_front_matter(front_matter: Dict[str, str]) -> str:
    """Front Matter 재구성"""
    standard_order = [
        'layout', 'title', 'date', 'categories', 'tags', 
        'excerpt', 'comments', 'original_url', 'image', 
        'image_alt', 'toc', 'certifications'
    ]
    
    lines = ['---']
    added_fields = set()
    
    # 표준 순서대로 필드 추가
    for field in standard_order:
        if field in front_matter:
            value = front_matter[field]
            if field == 'title':
                if not (value.startswith('"') and value.endswith('"')):
                    lines.append(f'{field}: "{value}"')
                else:
                    lines.append(f'{field}: {value}')
            elif field in ['categories', 'tags', 'certifications']:
                # 배열 형식 확인
                if isinstance(value, list):
                    lines.append(f'{field}: {value}')
                elif value.startswith('['):
                    lines.append(f'{field}: {value}')
                else:
                    # 단일 값을 배열로 변환
                    lines.append(f'{field}: [{value}]')
            else:
                lines.append(f'{field}: {value}')
            added_fields.add(field)
    
    # 추가 필드들
    for key, value in front_matter.items():
        if key not in added_fields:
            lines.append(f'{key}: {value}')
    
    lines.append('---')
    return '\n'.join(lines)

def process_post_file(file_path: Path) -> Dict[str, any]:
    """포스팅 파일 처리"""
    result = {
        'file': str(file_path.name),
        'fixed': False,
        'changes': [],
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        front_matter, body = extract_front_matter(content)
        
        if not front_matter:
            return result
        
        # category -> categories 변환
        if 'category' in front_matter and 'categories' not in front_matter:
            category_value = front_matter['category']
            front_matter['categories'] = f'[{category_value}]'
            del front_matter['category']
            result['changes'].append(f"category -> categories 변환: {category_value}")
            result['fixed'] = True
        
        # categories가 없으면 AI 요약에서 추출
        if 'categories' not in front_matter or not front_matter.get('categories'):
            categories = extract_categories_from_summary(content)
            if categories:
                front_matter['categories'] = f'[{", ".join(categories)}]'
                result['changes'].append(f"categories 추가: {categories}")
                result['fixed'] = True
        
        # tags가 없으면 AI 요약에서 추출
        if 'tags' not in front_matter or not front_matter.get('tags'):
            tags = extract_tags_from_summary(content)
            if tags:
                front_matter['tags'] = f'[{", ".join(tags)}]'
                result['changes'].append(f"tags 추가: {tags}")
                result['fixed'] = True
        
        # excerpt가 없으면 AI 요약에서 추출
        if 'excerpt' not in front_matter or not front_matter.get('excerpt'):
            excerpt = extract_excerpt_from_summary(content)
            if excerpt:
                front_matter['excerpt'] = f'"{excerpt}"'
                result['changes'].append("excerpt 추가")
                result['fixed'] = True
        
        if result['fixed']:
            # Front Matter 재구성
            new_front_matter = build_front_matter(front_matter)
            new_content = new_front_matter + '\n\n' + body
            
            # 파일 저장
            file_path.write_text(new_content, encoding='utf-8')
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
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
    
    for post_file in post_files:
        result = process_post_file(post_file)
        
        if result.get('fixed'):
            print(f"✅ {result['file']}")
            for change in result['changes']:
                print(f"   - {change}")
            print()
            fixed_count += 1
    
    print(f"\n처리 완료:")
    print(f"  - 총 파일 수: {len(post_files)}")
    print(f"  - 수정된 파일: {fixed_count}")

if __name__ == "__main__":
    main()
