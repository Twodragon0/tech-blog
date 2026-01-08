#!/usr/bin/env python3
"""
포스팅 요약 섹션 형식 통일 및 중복 제거 스크립트
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def extract_front_matter(file_path: Path) -> Dict:
    """Front matter에서 메타데이터 추출"""
    content = file_path.read_text(encoding='utf-8')
    
    front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    front_matter = {}
    if front_matter_match:
        for line in front_matter_match.group(1).split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip('"').strip("'")
                    front_matter[key] = value
    
    return front_matter

def parse_tags(tags_str: str) -> list:
    """태그 문자열을 리스트로 변환"""
    if not tags_str:
        return []
    
    # 리스트 형식인 경우
    if tags_str.startswith('['):
        tags = re.findall(r'\[(.*?)\]', tags_str)
        if tags:
            tags = tags[0].split(',')
            return [t.strip() for t in tags]
    
    # 쉼표로 구분된 문자열인 경우
    if ',' in tags_str:
        return [t.strip() for t in tags_str.split(',')]
    
    return [tags_str.strip()] if tags_str.strip() else []

def extract_core_content(excerpt: str, title: str) -> list:
    """excerpt에서 핵심 내용 추출 (3-5개 bullet points)"""
    core_points = []
    
    # excerpt가 충분히 길면 여러 포인트로 분리
    if len(excerpt) > 200:
        # 문장 단위로 분리
        sentences = re.split(r'[.!?]\s+', excerpt)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 핵심 문장 선택 (3-5개)
        for i, sentence in enumerate(sentences[:5]):
            if len(sentence) > 20:  # 너무 짧은 문장 제외
                core_points.append(sentence)
    else:
        # 짧은 경우 그대로 사용
        core_points.append(excerpt)
    
    return core_points[:5]  # 최대 5개

def extract_technologies(tags: list, title: str, category: str) -> list:
    """주요 기술/도구 추출"""
    tech_list = []
    
    # 태그에서 기술 관련 항목 추출
    tech_keywords = ['AWS', 'Kubernetes', 'Docker', 'Terraform', 'GitHub', 
                     'Cloudflare', 'Datadog', 'Zscaler', 'Security', 'DevSecOps',
                     'FinOps', 'SIEM', 'WAF', 'IAM', 'VPC', 'GuardDuty']
    
    for tag in tags:
        for keyword in tech_keywords:
            if keyword.lower() in tag.lower():
                tech_list.append(keyword)
                break
    
    # 제목에서도 추출
    for keyword in tech_keywords:
        if keyword.lower() in title.lower() and keyword not in tech_list:
            tech_list.append(keyword)
    
    # 카테고리 추가
    if category and category not in tech_list:
        tech_list.append(category)
    
    return tech_list[:8] if tech_list else tags[:8]  # 최대 8개

def get_target_audience(category: str, tags: list) -> str:
    """대상 독자 결정"""
    audiences = {
        'security': '기업 보안 담당자, 보안 엔지니어, CISO',
        'cloud': '클라우드 아키텍트, DevOps 엔지니어, 클라우드 관리자',
        'devsecops': 'DevSecOps 엔지니어, 보안 엔지니어, 개발자',
        'finops': 'FinOps 전문가, 클라우드 관리자, 재무 담당자',
        'incident': 'SRE, 인시던트 대응 담당자, 운영 엔지니어'
    }
    
    category_lower = category.lower()
    for key, value in audiences.items():
        if key in category_lower:
            return value
    
    # 기본값
    return '클라우드 보안 전문가, DevOps 엔지니어, 보안 담당자'

def generate_standard_summary(front_matter: Dict) -> str:
    """표준 요약 섹션 생성"""
    title = front_matter.get('title', '').replace('&amp;', '&').replace('&lsquo;', "'").replace('&rsquo;', "'")
    category = front_matter.get('categories', front_matter.get('category', ''))
    tags_str = front_matter.get('tags', '')
    excerpt = front_matter.get('excerpt', '')
    
    # 카테고리 정리
    if isinstance(category, str) and category.startswith('['):
        category = re.findall(r'\[(.*?)\]', category)
        category = category[0] if category else ''
    
    # 태그 파싱
    tags = parse_tags(tags_str)
    tags_display = ', '.join(tags) if tags else '없음'
    
    # 핵심 내용 추출
    core_points = extract_core_content(excerpt, title)
    if not core_points:
        core_points = [excerpt[:200] + '...' if len(excerpt) > 200 else excerpt]
    
    # 핵심 내용 포맷팅
    core_content = '\n'.join([f"> - {point}" for point in core_points])
    
    # 주요 기술/도구 추출
    technologies = extract_technologies(tags, title, category)
    tech_display = ', '.join(technologies) if technologies else tags_display
    
    # 대상 독자
    audience = get_target_audience(category, tags)
    
    summary = f"""## 📋 포스팅 요약

> **제목**: {title}

> **카테고리**: {category}

> **태그**: {tags_display}

> **핵심 내용**: 
{core_content}

> **주요 기술/도구**: {tech_display}

> **대상 독자**: {audience}

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*
"""
    
    return summary

def fix_summary_section(file_path: Path) -> bool:
    """요약 섹션 수정"""
    try:
        content = file_path.read_text(encoding='utf-8')
        front_matter = extract_front_matter(file_path)
        
        if not front_matter:
            return False
        
        # 요약 섹션 찾기
        summary_pattern = r'(## 📋 포스팅 요약\n\n)(.*?)(\n\n## |\n\n## 서론|\n\n## 1\.|\Z)'
        summary_match = re.search(summary_pattern, content, re.DOTALL)
        
        if not summary_match:
            # 요약 섹션이 없으면 추가
            front_matter_end = content.find('---\n', 4)  # 두 번째 --- 찾기
            if front_matter_end != -1:
                standard_summary = generate_standard_summary(front_matter)
                new_content = content[:front_matter_end+4] + '\n' + standard_summary + '\n' + content[front_matter_end+4:]
                file_path.write_text(new_content, encoding='utf-8')
                return True
            return False
        
        # 기존 요약 섹션 제거
        summary_start = summary_match.start()
        summary_end = summary_match.end(2)  # 요약 내용 끝
        
        # 표준 요약 생성
        standard_summary = generate_standard_summary(front_matter)
        
        # 요약 섹션 교체
        new_content = content[:summary_start] + standard_summary + content[summary_end:]
        
        # 중복된 요약 섹션 제거 (혹시 모를 경우)
        # "## 📋 포스팅 요약"이 두 번 이상 나타나는 경우
        summary_count = new_content.count('## 📋 포스팅 요약')
        if summary_count > 1:
            # 첫 번째 것만 유지
            first_summary_end = new_content.find('*이 포스팅은 AI', summary_start)
            if first_summary_end != -1:
                first_summary_end = new_content.find('\n', first_summary_end) + 1
                # 두 번째 요약 섹션 찾기
                second_summary_start = new_content.find('## 📋 포스팅 요약', first_summary_end)
                if second_summary_start != -1:
                    # 두 번째 요약 섹션 제거
                    second_summary_end = new_content.find('\n\n## ', second_summary_start)
                    if second_summary_end == -1:
                        second_summary_end = new_content.find('\n\n## 서론', second_summary_start)
                    if second_summary_end == -1:
                        second_summary_end = new_content.find('\n\n## 1.', second_summary_start)
                    if second_summary_end != -1:
                        new_content = new_content[:second_summary_start] + new_content[second_summary_end+2:]
        
        file_path.write_text(new_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"오류 발생 ({file_path.name}): {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    fixed_count = 0
    total_count = 0
    
    print("=" * 60)
    print("포스팅 요약 섹션 형식 통일 및 중복 제거")
    print("=" * 60)
    print()
    
    for post_file in sorted(POSTS_DIR.glob("*.md")):
        total_count += 1
        print(f"[{total_count}] 처리 중: {post_file.name}")
        
        if fix_summary_section(post_file):
            fixed_count += 1
            print(f"  ✓ 수정 완료")
        else:
            print(f"  - 스킵 (이미 올바른 형식이거나 오류)")
    
    print()
    print("=" * 60)
    print(f"완료: {fixed_count}/{total_count}개 포스팅 수정")
    print("=" * 60)

if __name__ == "__main__":
    main()
