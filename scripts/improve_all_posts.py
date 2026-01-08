#!/usr/bin/env python3
"""
모든 포스팅 요약 개선 및 이미지 확인 스크립트
서론 제거, 핵심 내용만 추출하여 요약 개선
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"


def extract_post_info(post_file: Path) -> Dict:
    """포스팅 파일에서 정보 추출"""
    content = post_file.read_text(encoding='utf-8')
    
    # Front matter 추출
    front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    front_matter = {}
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        for line in front_matter_text.split('\n'):
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip('"').strip("'")
                    front_matter[key] = value
    
    # 요약 섹션 추출
    summary_match = re.search(r'## 📋 포스팅 요약\n\n(.*?)\n\n', content, re.DOTALL)
    summary_text = summary_match.group(1) if summary_match else ""
    
    # 본문 추출 (요약 섹션 이후)
    body_start = content.find('## 📋 포스팅 요약')
    if body_start != -1:
        body_end = content.find('\n\n', body_start + 20)
        if body_end != -1:
            body_text = content[body_end+2:body_end+2000]  # 처음 2000자
        else:
            body_text = content[body_start+20:]
    else:
        body_text = content[:2000]
    
    return {
        'title': front_matter.get('title', ''),
        'category': front_matter.get('categories', front_matter.get('category', '')),
        'tags': front_matter.get('tags', '[]'),
        'excerpt': front_matter.get('excerpt', ''),
        'summary': summary_text,
        'body': body_text,
        'image': front_matter.get('image', ''),
        'filename': post_file.name,
        'content': content
    }


def clean_summary(summary_text: str, post_data: Dict) -> str:
    """요약에서 서론 제거 및 핵심만 추출"""
    if not summary_text:
        return ""
    
    # 핵심 내용 부분 추출
    core_match = re.search(r'\*\*핵심 내용\*\*:\s*(.*?)(?:\n\n|$)', summary_text, re.DOTALL)
    if not core_match:
        # 핵심 내용이 없으면 전체 요약에서 추출 시도
        core_match = re.search(r'핵심 내용[:\s]*(.*?)(?:\n\n|$)', summary_text, re.DOTALL)
        if not core_match:
            return ""
    
    core_content = core_match.group(1).strip()
    
    # 서론 제거 패턴들 (더 정확하게)
    intro_patterns = [
        r'^안녕하세요[^.]*\.',
        r'^[^.]*Twodragon[^.]*\.',
        r'^[^.]*이번 포스트[^.]*\.',
        r'^[^.]*이번 포스팅[^.]*\.',
        r'^[^.]*본 포스팅[^.]*\.',
        r'^[^.]*이번 달에는[^.]*\.',
        r'^[^.]*이번 주차[^.]*\.',
        r'^[^.]*온라인 미팅[^.]*\.',
        r'^[^.]*게더 타운[^.]*\.',
        r'^[^.]*20분[^.]*\.',
        r'^[^.]*5분[^.]*\.',
        r'^[^.]*지난[^.]*\.',
        r'^[^.]*12월은[^.]*\.',
        r'^[^.]*이번 달[^.]*\.',
        r'^[^.]*참석하며[^.]*\.',
        r'^[^.]*느낄 수 있었습니다[^.]*\.',
        r'^[^.]*본 포스팅에서는[^.]*\.',
        r'^[^.]*\.\.\.$',  # 말줄임표로 끝나는 경우
        r'^[^.]*강의[^.]*\.',
        r'^[^.]*수업[^.]*\.',
        r'^[^.]*과정[^.]*\.',
    ]
    
    cleaned = core_content
    for pattern in intro_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # 연속된 공백 정리
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 핵심 내용이 너무 짧거나 비어있으면 excerpt 사용
    if len(cleaned) < 50:
        excerpt = post_data.get('excerpt', '')
        if excerpt:
            cleaned = excerpt
            # excerpt에서도 서론 제거
            for pattern in intro_patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 핵심 내용이 여전히 비어있으면 본문에서 추출
    if len(cleaned) < 50:
        body = post_data.get('body', '')
        # 본문에서 첫 번째 섹션 추출
        section_match = re.search(r'^##\s+(.+?)\n\n(.*?)(?=\n##|\Z)', body, re.DOTALL)
        if section_match:
            cleaned = section_match.group(2)[:300].strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            # 본문에서도 서론 제거
            for pattern in intro_patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    # 최종 정리: 앞뒤 불필요한 문구 제거
    cleaned = re.sub(r'^(이|그|이번|본|이번|지난|이번 달|이번 주차|온라인|게더)[^.]*\.', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def check_image_exists(image_path: str) -> Tuple[bool, Path]:
    """이미지 파일 존재 여부 확인"""
    if not image_path:
        return False, None
    
    if image_path.startswith('/assets/images/'):
        image_file = PROJECT_ROOT / image_path.lstrip('/')
    else:
        image_file = IMAGES_DIR / Path(image_path).name
    
    return image_file.exists(), image_file


def improve_summary_section(post_data: Dict) -> str:
    """요약 섹션 개선"""
    title = post_data.get('title', '')
    category = post_data.get('category', '')
    tags = post_data.get('tags', '[]')
    core_content = clean_summary(post_data.get('summary', ''), post_data)
    
    # 태그 파싱
    tag_list = []
    if tags:
        tag_match = re.search(r'\[(.*?)\]', tags)
        if tag_match:
            tag_list = [t.strip() for t in tag_match.group(1).split(',')]
    
    # 구조화된 요약 생성
    summary_lines = [
        f"> **제목**: {title}",
        "",
        f"> **카테고리**: {category}",
        "",
        f"> **태그**: {', '.join(tag_list) if tag_list else tags}",
        "",
        f"> **핵심 내용**: {core_content}",
        "",
        "> ---",
        "",
        "> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*"
    ]
    
    return "\n".join(summary_lines)


def process_post(post_file: Path, dry_run: bool = False) -> Dict:
    """포스팅 처리"""
    print(f"\n📄 처리 중: {post_file.name}")
    
    post_data = extract_post_info(post_file)
    
    # 이미지 확인
    has_image, image_path = check_image_exists(post_data.get('image', ''))
    
    # 요약 개선
    improved_summary = improve_summary_section(post_data)
    
    result = {
        'file': post_file.name,
        'title': post_data.get('title', ''),
        'has_image': has_image,
        'image_path': post_data.get('image', ''),
        'old_summary': post_data.get('summary', ''),
        'new_summary': improved_summary,
        'needs_update': post_data.get('summary', '') != improved_summary
    }
    
    # 결과 출력
    if has_image:
        print(f"  ✅ 이미지: {post_data.get('image', 'N/A')}")
    else:
        print(f"  ❌ 이미지 없음")
    
    if result['needs_update']:
        print(f"  🔄 요약 개선 필요")
        if not dry_run:
            # 파일 업데이트
            content = post_data['content']
            # 요약 섹션 전체를 찾아서 교체
            old_summary_match = re.search(
                r'(## 📋 포스팅 요약\n\n)(.*?)(\n\n[^>])',
                content,
                re.DOTALL
            )
            if old_summary_match:
                # 요약 섹션 이후의 첫 번째 줄이 ">"로 시작하지 않는 부분까지 찾기
                new_content = (
                    content[:old_summary_match.start(1)] +
                    old_summary_match.group(1) +
                    improved_summary +
                    "\n\n" +
                    content[old_summary_match.end(2):]
                )
                post_file.write_text(new_content, encoding='utf-8')
                print(f"  ✅ 파일 업데이트 완료")
            else:
                # 패턴이 맞지 않으면 더 넓은 범위로 시도
                old_summary_match = re.search(
                    r'(## 📋 포스팅 요약\n\n)(.*?)(\n\n)',
                    content,
                    re.DOTALL
                )
                if old_summary_match:
                    new_content = (
                        content[:old_summary_match.start(1)] +
                        old_summary_match.group(1) +
                        improved_summary +
                        old_summary_match.group(3) +
                        content[old_summary_match.end():]
                    )
                    post_file.write_text(new_content, encoding='utf-8')
                    print(f"  ✅ 파일 업데이트 완료")
    else:
        print(f"  ✓ 요약 이미 최적화됨")
    
    return result


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='모든 포스팅 요약 개선 및 이미지 확인')
    parser.add_argument('--dry-run', action='store_true', help='실제 파일 수정 없이 미리보기')
    parser.add_argument('--limit', type=int, help='처리할 포스팅 수 제한')
    
    args = parser.parse_args()
    
    # 모든 포스팅 파일 가져오기
    posts = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if args.limit:
        posts = posts[:args.limit]
    
    print(f"📊 {len(posts)}개 포스팅 처리 시작...")
    if args.dry_run:
        print("🔍 DRY RUN 모드: 파일 수정 없이 미리보기만 합니다.")
    
    results = []
    for post_file in posts:
        result = process_post(post_file, dry_run=args.dry_run)
        results.append(result)
    
    # 요약 리포트
    print("\n" + "=" * 80)
    print("📊 처리 결과 요약")
    print("=" * 80)
    
    total = len(results)
    with_image = sum(1 for r in results if r['has_image'])
    needs_update = sum(1 for r in results if r['needs_update'])
    
    print(f"전체 포스팅: {total}")
    print(f"이미지 있음: {with_image} ({with_image/total*100:.1f}%)")
    print(f"요약 개선 필요: {needs_update} ({needs_update/total*100:.1f}%)")
    
    if needs_update > 0 and args.dry_run:
        print(f"\n다음 포스팅들의 요약이 개선됩니다:")
        for r in results:
            if r['needs_update']:
                print(f"  - {r['file']}")


if __name__ == '__main__':
    main()
