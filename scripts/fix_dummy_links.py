#!/usr/bin/env python3
"""
더미 링크를 실제 링크로 교체하는 스크립트
"""

import re
from pathlib import Path

POSTS_DIR = Path("_posts")

# 더미 링크 패턴과 실제 링크 매핑
LINK_REPLACEMENTS = [
    # GitHub Actions starter-workflows
    (
        r'https://github\.com/actions/starter-workflows[^)]*',
        'https://github.com/actions/starter-workflows'
    ),
    (
        r'\[GitHub Actions 예제\]\(https://github\.com/actions/starter-workflows[^)]*\)',
        '[GitHub Actions 예제](https://github.com/actions/starter-workflows)'
    ),
    
    # Kubernetes examples
    (
        r'https://github\.com/kubernetes/examples[^)]*',
        'https://github.com/kubernetes/examples'
    ),
    (
        r'\[Kubernetes 예제\]\(https://github\.com/kubernetes/examples[^)]*\)',
        '[Kubernetes 예제](https://github.com/kubernetes/examples)'
    ),
    (
        r'\[Kubernetes Service 문서\]\(https://github\.com/kubernetes/examples[^)]*\)',
        '[Kubernetes Service 문서](https://kubernetes.io/docs/concepts/services-networking/service/)'
    ),
    
    # Kubernetes examples tree/master
    (
        r'https://github\.com/kubernetes/examples/tree/master[^)]*',
        'https://github.com/kubernetes/examples'
    ),
    
    # Kubernetes kubernetes/blob/master
    (
        r'https://github\.com/kubernetes/kubernetes/blob/master[^)]*',
        'https://github.com/kubernetes/kubernetes'
    ),
    
    # GitHub example (제거)
    (
        r'\[.*?\]\(https://github\.com/example[^)]*\)',
        ''
    ),
    (
        r'https://github\.com/example[^)]*',
        ''
    ),
]

def fix_dummy_links(file_path: Path) -> bool:
    """더미 링크를 실제 링크로 교체"""
    content = file_path.read_text(encoding="utf-8")
    original_content = content
    updated = False
    
    for pattern, replacement in LINK_REPLACEMENTS:
        new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        if new_content != content:
            content = new_content
            updated = True
    
    if updated:
        file_path.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    """메인 함수"""
    post_files = sorted(POSTS_DIR.glob("*.md"))
    updated_count = 0
    
    for post_file in post_files:
        if fix_dummy_links(post_file):
            print(f"✓  {post_file.name}: Links fixed")
            updated_count += 1
    
    print(f"\n✓  Updated {updated_count} files")

if __name__ == "__main__":
    main()
