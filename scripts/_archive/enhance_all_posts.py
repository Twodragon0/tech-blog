#!/usr/bin/env python3
"""
모든 포스팅의 요약 섹션을 보강하는 스크립트
각 포스팅의 front matter에서 태그와 카테고리를 추출하여 요약 섹션에 추가
"""

import re
from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def extract_front_matter(file_path):
    """Front matter에서 메타데이터 추출"""
    content = file_path.read_text(encoding='utf-8')

    # Front matter 추출
    front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not front_matter_match:
        return None

    front_matter = {}
    for line in front_matter_match.group(1).split('\n'):
        if ':' in line and not line.strip().startswith('#'):
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip().strip('"').strip("'")
                front_matter[key] = value

    return front_matter

def enhance_summary_section(file_path, front_matter):
    """요약 섹션 보강"""
    content = file_path.read_text(encoding='utf-8')

    # 요약 섹션 찾기
    summary_pattern = r'(## 📋 포스팅 요약\n\n.*?)(\n\n[^#]|\Z)'
    summary_match = re.search(summary_pattern, content, re.DOTALL)

    if not summary_match:
        return False

    summary_section = summary_match.group(1)

    # 이미 보강된 경우 스킵
    if '**태그**:' in summary_section and '**핵심 내용**:' in summary_section:
        return False

    # 태그 추출
    tags = front_matter.get('tags', '')
    if isinstance(tags, str):
        # 리스트 형식인 경우 파싱
        if tags.startswith('['):
            tags = re.findall(r'\[(.*?)\]', tags)
            if tags:
                tags = tags[0].split(',')
                tags = [t.strip() for t in tags]
        else:
            tags = [tags] if tags else []
    elif not isinstance(tags, list):
        tags = []

    tags_str = ', '.join(tags) if tags else '없음'

    # 카테고리 추출
    category = front_matter.get('categories', front_matter.get('category', ''))
    if isinstance(category, str) and category.startswith('['):
        category = re.findall(r'\[(.*?)\]', category)
        if category:
            category = category[0]
        else:
            category = ''

    # 새로운 요약 섹션 생성
    title = front_matter.get('title', '').replace('&amp;', '&').replace('&lsquo;', "'").replace('&rsquo;', "'")
    excerpt = front_matter.get('excerpt', '')

    # 핵심 내용 추출 (excerpt 기반)
    core_content = excerpt[:200] + "..." if len(excerpt) > 200 else excerpt

    new_summary = f"""## 📋 포스팅 요약

> **제목**: {title}

> **카테고리**: {category}

> **태그**: {tags_str}

> **핵심 내용**: 
> {core_content}

> **주요 기술/도구**: {tags_str}

> **대상 독자**: 클라우드 보안 전문가, DevOps 엔지니어, 보안 담당자

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*"""

    # 요약 섹션 교체
    new_content = content[:summary_match.start()] + new_summary + content[summary_match.end(1):]

    file_path.write_text(new_content, encoding='utf-8')
    return True

def main():
    """메인 함수"""
    enhanced_count = 0

    for post_file in sorted(POSTS_DIR.glob("*.md")):
        try:
            front_matter = extract_front_matter(post_file)
            if not front_matter:
                continue

            if enhance_summary_section(post_file, front_matter):
                enhanced_count += 1
                print(f"✓ Enhanced: {post_file.name}")
        except Exception as e:
            print(f"✗ Error processing {post_file.name}: {e}")

    print(f"\nTotal enhanced: {enhanced_count} posts")

if __name__ == "__main__":
    main()
