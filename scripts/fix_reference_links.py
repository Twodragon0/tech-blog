#!/usr/bin/env python3
"""
⚠️ DEPRECATED: 이 스크립트는 더 이상 사용되지 않습니다.
대신 `fix_links_unified.py`를 사용하세요.

참고자료 링크의 주요 문제 패턴을 찾아서 일괄 수정하는 스크립트
"""
import re
from pathlib import Path
from typing import List, Tuple

# 링크 교체 규칙: (패턴, 교체할 텍스트)
LINK_FIXES = [
    # Kubernetes 보안 Best Practices (404 오류)
    (
        r'https://kubernetes\.io/docs/concepts/security/best-practices/',
        'https://kubernetes.io/docs/concepts/security/security-checklist/'
    ),
    # Trivy 구버전 다운로드 링크
    (
        r'https://github\.com/aquasecurity/trivy/releases/latest/download/trivy_\d+\.\d+\.\d+_Linux-64bit\.tar\.gz',
        'https://github.com/aquasecurity/trivy/releases'
    ),
]

# 링크 텍스트 교체 규칙: (패턴, 새 텍스트)
TEXT_FIXES = [
    # docker-library 링크를 컨텍스트에 맞게 교체
    (
        r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/docker-library\)를 참조하세요\.',
        '> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.'
    ),
]

def fix_links_in_file(file_path: Path) -> Tuple[bool, List[str]]:
    """
    파일 내 링크 수정
    
    Returns:
        (수정 여부, 수정된 링크 목록)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        fixed_links = []
        
        # URL 교체
        for pattern, replacement in LINK_FIXES:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, replacement, content)
                fixed_links.extend([f'{m} -> {replacement}' for m in matches])
        
        # 텍스트 교체
        for pattern, replacement in TEXT_FIXES:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixed_links.append(f'링크 텍스트 교체')
        
        # 변경사항 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, fixed_links
        
        return False, []
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []

def main():
    """메인 함수"""
    script_dir = Path(__file__).parent
    posts_dir = script_dir.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    print("=" * 80)
    print("참고자료 링크 일괄 수정")
    print("=" * 80)
    print()
    
    processed = 0
    updated = 0
    all_fixed_links = []
    
    for post_file in sorted(posts_dir.glob('*.md')):
        processed += 1
        was_updated, fixed_links = fix_links_in_file(post_file)
        
        if was_updated:
            updated += 1
            all_fixed_links.extend([(post_file.name, link) for link in fixed_links])
            print(f"✅ 수정: {post_file.name}")
            for link in fixed_links:
                print(f"   - {link}")
    
    print()
    print("=" * 80)
    print(f"처리 완료: {processed}개 파일")
    print(f"수정됨: {updated}개 파일")
    print(f"총 수정된 링크: {len(all_fixed_links)}개")
    print("=" * 80)

if __name__ == '__main__':
    main()
