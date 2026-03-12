#!/usr/bin/env python3
"""
포스팅 중복 내용 검증 스크립트
- 중복된 이미지 경로 확인
- 중복된 텍스트 섹션 확인
- 중복된 코드 블록 확인
"""

import re
from collections import defaultdict
from difflib import SequenceMatcher
from pathlib import Path


def extract_images(content):
    """이미지 경로 추출"""
    # Markdown 이미지: ![alt](path)
    markdown_images = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
    # HTML 이미지: <img src="path">
    html_images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    # Jekyll 이미지: {{ '/assets/images/...' | relative_url }}
    jekyll_images = re.findall(r"['\"]([^'\"]*assets/images[^'\"]*)['\"]", content)

    all_images = markdown_images + html_images + jekyll_images
    # 상대 경로 정규화
    normalized = []
    for img in all_images:
        # 상대 경로나 절대 경로에서 실제 파일명 추출
        img = img.split('|')[0].strip().strip("'\"")
        if img.startswith('/assets/images/'):
            normalized.append(img)
        elif 'assets/images' in img:
            normalized.append('/' + img.lstrip('/'))
    return normalized

def extract_code_blocks(content):
    """코드 블록 추출 (길이가 50자 이상인 것만)"""
    code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
    # 긴 코드 블록만 반환 (50자 이상)
    return [cb.strip() for cb in code_blocks if len(cb.strip()) > 50]

def extract_long_text_sections(content):
    """긴 텍스트 섹션 추출 (100자 이상)"""
    # 헤더로 구분된 섹션 추출
    sections = re.split(r'^#{1,6}\s+', content, flags=re.MULTILINE)
    long_sections = []
    for section in sections[1:]:  # 첫 번째는 헤더 없음
        # 코드 블록 제거
        section = re.sub(r'```.*?```', '', section, flags=re.DOTALL)
        # 이미지 제거
        section = re.sub(r'!\[.*?\]\(.*?\)', '', section)
        section = re.sub(r'<img[^>]+>', '', section)
        # 공백 정리
        section = ' '.join(section.split())
        if len(section) > 100:
            long_sections.append(section[:200])  # 처음 200자만
    return long_sections

def similarity(a, b):
    """두 문자열의 유사도 계산"""
    return SequenceMatcher(None, a, b).ratio()

def check_duplicates(posts_dir):
    """중복 내용 확인"""
    posts = list(posts_dir.glob('*.md'))

    # 이미지 경로 중복 확인
    image_usage = defaultdict(list)
    code_block_usage = defaultdict(list)
    text_similarity = []

    print("=" * 80)
    print("포스팅 중복 내용 검증 시작")
    print("=" * 80)

    for post_file in posts:
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # 이미지 추출
            images = extract_images(content)
            for img in images:
                image_usage[img].append(post_file.name)

            # 코드 블록 추출
            code_blocks = extract_code_blocks(content)
            for cb in code_blocks:
                # 코드 블록의 해시 생성 (처음 100자)
                cb_hash = cb[:100]
                code_block_usage[cb_hash].append((post_file.name, cb[:150]))

            # 텍스트 섹션 추출
            sections = extract_long_text_sections(content)
            for section in sections:
                text_similarity.append((post_file.name, section))

        except Exception as e:
            print(f"⚠️  오류 처리 중 {post_file.name}: {e}")

    # 결과 출력
    print("\n" + "=" * 80)
    print("1. 중복된 이미지 경로")
    print("=" * 80)
    duplicate_images = {img: files for img, files in image_usage.items() if len(files) > 1}
    if duplicate_images:
        for img, files in sorted(duplicate_images.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"\n📷 이미지: {img}")
            print(f"   사용된 파일 수: {len(files)}")
            for f in files[:5]:  # 최대 5개만 표시
                print(f"   - {f}")
            if len(files) > 5:
                print(f"   ... 외 {len(files) - 5}개 파일")
    else:
        print("✅ 중복된 이미지 경로 없음")

    print("\n" + "=" * 80)
    print("2. 중복된 코드 블록 (유사도 높은 것)")
    print("=" * 80)
    duplicate_code = {cb: files for cb, files in code_block_usage.items() if len(files) > 1}
    if duplicate_code:
        for cb_hash, files in sorted(duplicate_code.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            print(f"\n💻 코드 블록 (처음 100자): {cb_hash[:100]}...")
            print(f"   사용된 파일 수: {len(files)}")
            for f, code_preview in files[:3]:  # 최대 3개만 표시
                print(f"   - {f}")
                print(f"     {code_preview[:80]}...")
    else:
        print("✅ 중복된 코드 블록 없음")

    print("\n" + "=" * 80)
    print("3. 유사한 텍스트 섹션 (유사도 80% 이상)")
    print("=" * 80)
    similar_texts = []
    for i, (file1, text1) in enumerate(text_similarity):
        for j, (file2, text2) in enumerate(text_similarity[i+1:], i+1):
            if file1 != file2:
                sim = similarity(text1, text2)
                if sim > 0.8:
                    similar_texts.append((file1, file2, sim, text1[:100]))

    if similar_texts:
        # 유사도 높은 순으로 정렬
        similar_texts.sort(key=lambda x: x[2], reverse=True)
        for file1, file2, sim, preview in similar_texts[:20]:  # 최대 20개만 표시
            print(f"\n📝 유사도: {sim:.1%}")
            print(f"   파일 1: {file1}")
            print(f"   파일 2: {file2}")
            print(f"   미리보기: {preview}...")
    else:
        print("✅ 유사한 텍스트 섹션 없음")

    # 요약
    print("\n" + "=" * 80)
    print("검증 요약")
    print("=" * 80)
    print(f"총 포스트 수: {len(posts)}")
    print(f"중복 이미지 경로: {len(duplicate_images)}개")
    print(f"중복 코드 블록: {len(duplicate_code)}개")
    print(f"유사 텍스트 섹션: {len(similar_texts)}개")

    return {
        'duplicate_images': duplicate_images,
        'duplicate_code': duplicate_code,
        'similar_texts': similar_texts
    }

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'

    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return

    check_duplicates(posts_dir)

if __name__ == '__main__':
    main()
