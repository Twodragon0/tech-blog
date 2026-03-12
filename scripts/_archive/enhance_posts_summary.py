#!/usr/bin/env python3
"""
포스팅에 AI 활용을 위한 구조화된 요약 섹션 추가
"""

from pathlib import Path

POSTS_DIR = Path(__file__).parent.parent / "_posts"

def create_summary_box(title, excerpt, tags, categories):
    """AI 활용을 위한 요약 박스 생성"""
    summary = f"""## 📋 포스팅 요약

> **제목**: {title}
> 
> **카테고리**: {', '.join(categories) if isinstance(categories, list) else categories}
> 
> **태그**: {', '.join(tags) if isinstance(tags, list) else tags}
> 
> **핵심 내용**: {excerpt}
> 
> ---
> 
> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*

"""
    return summary

def extract_front_matter_metadata(content):
    """프론트매터에서 메타데이터 추출"""
    if not content.startswith('---'):
        return None, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content

    front_matter = parts[1]
    body = parts[2]

    metadata = {}
    for line in front_matter.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")

            # 리스트 처리
            if value.startswith('[') and value.endswith(']'):
                value = [v.strip().strip('"').strip("'") for v in value[1:-1].split(',')]

            metadata[key] = value

    return metadata, body

def add_summary_to_body(body, metadata):
    """본문에 요약 섹션 추가"""
    # 이미 요약 섹션이 있으면 건너뛰기
    if '## 📋 포스팅 요약' in body or '## 포스팅 요약' in body:
        return body

    title = metadata.get('title', '').strip('"')
    excerpt = metadata.get('excerpt', '').strip('"')
    tags = metadata.get('tags', [])
    categories = metadata.get('categories', metadata.get('category', ''))

    if not excerpt:
        # excerpt가 없으면 첫 문단 사용
        first_paragraph = body.split('\n\n')[0] if '\n\n' in body else body[:200]
        excerpt = first_paragraph.strip()[:200]

    summary_box = create_summary_box(title, excerpt, tags, categories)

    # 본문 시작 부분에 추가 (첫 번째 헤더나 첫 번째 문단 앞)
    lines = body.split('\n')
    insert_pos = 0

    # 첫 번째 비어있지 않은 줄 찾기
    for i, line in enumerate(lines):
        if line.strip() and not line.strip().startswith('원본 포스트'):
            insert_pos = i
            break

    # 요약 박스 삽입
    lines.insert(insert_pos, summary_box)

    return '\n'.join(lines)

def process_post_file(file_path):
    """단일 포스팅 파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 메타데이터와 본문 분리
        metadata, body = extract_front_matter_metadata(content)

        if metadata:
            # 본문에 요약 섹션 추가
            body = add_summary_to_body(body, metadata)

            # 재조합
            front_matter = content.split('---', 2)[1]
            content = f"---{front_matter}---{body}"

        # 변경사항이 있으면 파일 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    if not POSTS_DIR.exists():
        print(f"Posts directory not found: {POSTS_DIR}")
        return

    post_files = list(POSTS_DIR.glob("*.md"))
    print(f"Found {len(post_files)} post files")

    updated_count = 0
    for post_file in sorted(post_files):
        if process_post_file(post_file):
            print(f"✓ Updated: {post_file.name}")
            updated_count += 1
        else:
            print(f"- Skipped: {post_file.name}")

    print(f"\n✅ Processed {len(post_files)} files, updated {updated_count} files")

if __name__ == '__main__':
    main()
