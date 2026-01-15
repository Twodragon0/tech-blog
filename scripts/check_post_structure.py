#!/usr/bin/env python3
"""
포스팅 구조 완전성 검사 스크립트
- AI 요약 카드 존재 여부
- 서론 섹션 존재 여부
- 본문 길이 확인
- 최신 자료 반영 여부 확인
"""

import re
import sys
from pathlib import Path
from typing import Dict, List

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"

def check_ai_summary(content: str) -> bool:
    """AI 요약 카드 존재 여부 확인"""
    return '<div class="ai-summary-card">' in content or '## 📋 포스팅 요약' in content

def check_introduction(content: str) -> bool:
    """서론 섹션 존재 여부 확인"""
    return bool(re.search(r'^## 서론', content, re.MULTILINE))

def get_body_length(content: str) -> int:
    """본문 길이 확인 (Front Matter와 AI 요약 제외)"""
    # Front Matter 제거
    content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    
    # AI 요약 카드 제거
    content = re.sub(r'<div class="ai-summary-card">.*?</div>\s*</div>', '', content, flags=re.DOTALL)
    content = re.sub(r'## 📋 포스팅 요약.*?(?=## |$)', '', content, flags=re.DOTALL)
    
    # 이미지 태그 제거
    content = re.sub(r'<img[^>]+>', '', content)
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    
    # 코드 블록 제거
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    
    # HTML 태그 제거
    content = re.sub(r'<[^>]+>', '', content)
    
    # 마크다운 링크 제거
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)
    
    # 공백 정리
    content = re.sub(r'\s+', ' ', content)
    
    return len(content.strip())

def check_recent_references(content: str) -> Dict[str, bool]:
    """최신 자료 참조 확인"""
    checks = {
        'has_2025': bool(re.search(r'2025', content)),
        'has_2026': bool(re.search(r'2026', content)),
        'has_recent_versions': bool(re.search(r'(Kubernetes 1\.(3[2-5]|4[0-9])|K8s 1\.(3[2-5]|4[0-9])|v1\.(3[2-5]|4[0-9]))', content)),
        'has_owasp_2025': bool(re.search(r'OWASP.*2025|OWASP Top 10.*2025', content, re.IGNORECASE)),
        'has_nist_csf_2': bool(re.search(r'NIST CSF 2\.0|NIST CSF 2', content)),
    }
    return checks

def extract_front_matter(content: str) -> tuple[Dict[str, str], str]:
    """Front Matter 추출"""
    front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(front_matter_pattern, content, re.DOTALL)
    
    if not match:
        return {}, content
    
    front_matter_text = match.group(1)
    body = match.group(2)
    
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

def process_post_file(file_path: Path) -> Dict[str, any]:
    """포스팅 파일 처리"""
    result = {
        'file': str(file_path.name),
        'has_ai_summary': False,
        'has_introduction': False,
        'body_length': 0,
        'recent_refs': {},
        'issues': [],
        'warnings': [],
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        front_matter, body = extract_front_matter(content)
        
        # AI 요약 카드 확인
        result['has_ai_summary'] = check_ai_summary(content)
        if not result['has_ai_summary']:
            result['issues'].append("AI 요약 카드가 없습니다")
        
        # 서론 확인
        result['has_introduction'] = check_introduction(content)
        if not result['has_introduction']:
            result['issues'].append("서론 섹션이 없습니다")
        
        # 본문 길이 확인
        result['body_length'] = get_body_length(content)
        if result['body_length'] < 1500:
            result['warnings'].append(f"본문이 너무 짧습니다 ({result['body_length']}자, 권장: 1500자 이상)")
        
        # 최신 자료 참조 확인
        result['recent_refs'] = check_recent_references(content)
        
        # 날짜 확인
        date_str = front_matter.get('date', '')
        if '2025' in date_str or '2026' in date_str:
            # 최신 포스트인데 최신 자료 참조가 없으면 경고
            if not any(result['recent_refs'].values()):
                result['warnings'].append("최신 포스트이지만 최신 자료 참조가 부족합니다")
        
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
    
    print(f"총 {len(post_files)}개의 포스팅 파일을 검사합니다...\n")
    
    files_with_issues = []
    files_with_warnings = []
    
    for post_file in post_files:
        result = process_post_file(post_file)
        
        if result['issues'] or result['warnings']:
            if result['issues']:
                print(f"❌ {result['file']}")
                for issue in result['issues']:
                    print(f"   ⚠️  {issue}")
                files_with_issues.append(result['file'])
            
            if result['warnings']:
                if not result['issues']:
                    print(f"⚠️  {result['file']}")
                for warning in result['warnings']:
                    print(f"   ⚠️  {warning}")
                files_with_warnings.append(result['file'])
            
            print(f"   본문 길이: {result['body_length']}자")
            print()
    
    print(f"\n검사 완료:")
    print(f"  - 총 파일 수: {len(post_files)}")
    print(f"  - 문제가 있는 파일: {len(files_with_issues)}")
    print(f"  - 경고가 있는 파일: {len(files_with_warnings)}")
    
    if files_with_issues:
        print(f"\n❌ 구조적 문제가 있는 파일:")
        for file in files_with_issues:
            print(f"  - {file}")

if __name__ == "__main__":
    main()
