#!/usr/bin/env python3
"""
Tistory 블로그 포스트에서 이미지를 가져와서 로컬에 저장하고 포스트에 추가하는 스크립트
"""

import os
import re
import sys
import time
import requests
from pathlib import Path
from urllib.parse import urlparse, urljoin, unquote
from typing import Optional, List, Tuple
import urllib3

# SSL 경고 비활성화 (일부 환경에서 인증서 문제 발생 가능)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ beautifulsoup4가 설치되지 않았습니다.")
    print("   설치 방법: pip3 install --break-system-packages beautifulsoup4 lxml")
    sys.exit(1)

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# User-Agent 설정 (봇 차단 방지)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def extract_images_from_tistory(url: str) -> List[str]:
    """
    Tistory 블로그 포스트에서 이미지 URL을 추출합니다.
    
    Args:
        url: Tistory 블로그 포스트 URL
        
    Returns:
        이미지 URL 리스트
    """
    try:
        print(f"  📥 Fetching: {url}")
        # SSL 검증 경고 무시 (일부 환경에서 인증서 문제 발생 가능)
        response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        image_urls = []
        
        # Tistory 이미지 URL 패턴 찾기
        # 1. img 태그의 src 속성
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if src:
                # Tistory CDN 이미지 URL 확인
                if 'blog.kakaocdn.net' in src or 'img1.daumcdn.net' in src:
                    # 상대 경로를 절대 경로로 변환
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif src.startswith('/'):
                        src = urljoin(url, src)
                    image_urls.append(src)
        
        # 2. 메타 태그에서 이미지 찾기 (og:image 등)
        for meta in soup.find_all('meta', property=re.compile(r'og:image')):
            content = meta.get('content')
            if content and ('blog.kakaocdn.net' in content or 'img1.daumcdn.net' in content):
                if content.startswith('//'):
                    content = 'https:' + content
                elif content.startswith('/'):
                    content = urljoin(url, content)
                image_urls.append(content)
        
        # 중복 제거
        image_urls = list(dict.fromkeys(image_urls))
        
        print(f"  ✅ Found {len(image_urls)} image(s)")
        return image_urls
        
    except Exception as e:
        print(f"  ❌ Error fetching {url}: {e}")
        return []

def download_image(image_url: str, save_path: Path) -> bool:
    """
    이미지를 다운로드합니다.
    
    Args:
        image_url: 이미지 URL
        save_path: 저장할 경로
        
    Returns:
        성공 여부
    """
    try:
        # 이미 파일이 존재하면 스킵
        if save_path.exists():
            print(f"    ⏭️  Already exists: {save_path.name}")
            return True
        
        print(f"    📥 Downloading: {image_url[:80]}...")
        response = requests.get(image_url, headers=HEADERS, timeout=30, stream=True, verify=False)
        response.raise_for_status()
        
        # Content-Type 확인
        content_type = response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            print(f"    ⚠️  Not an image: {content_type}")
            return False
        
        # 파일 저장
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"    ✅ Saved: {save_path.name}")
        return True
        
    except Exception as e:
        print(f"    ❌ Error downloading {image_url}: {e}")
        return False

def get_image_filename(post_file: Path, image_index: int = 0) -> str:
    """
    포스트 파일명을 기반으로 이미지 파일명을 생성합니다.
    
    Args:
        post_file: 포스트 파일 경로
        image_index: 이미지 인덱스 (여러 이미지가 있을 경우)
        
    Returns:
        이미지 파일명
    """
    post_name = post_file.stem  # 확장자 제거
    
    # 이미지 확장자는 다운로드 시 결정 (일단 png로 설정)
    if image_index == 0:
        return f"{post_name}_image.png"
    else:
        return f"{post_name}_image_{image_index}.png"

def extract_image_extension_from_url(url: str) -> str:
    """
    URL에서 이미지 확장자를 추출합니다.
    
    Args:
        url: 이미지 URL
        
    Returns:
        확장자 (예: .png, .jpg)
    """
    # URL에서 확장자 추출
    parsed = urlparse(url)
    path = unquote(parsed.path)
    
    # 확장자 확인
    if path.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
        ext = Path(path).suffix
        return ext
    
    # Content-Type에서 확장자 추정
    try:
        response = requests.head(url, headers=HEADERS, timeout=10, verify=False)
        content_type = response.headers.get('Content-Type', '')
        if 'png' in content_type:
            return '.png'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            return '.jpg'
        elif 'gif' in content_type:
            return '.gif'
        elif 'webp' in content_type:
            return '.webp'
        elif 'svg' in content_type:
            return '.svg'
    except:
        pass
    
    return '.png'  # 기본값

def add_image_to_post(post_file: Path, image_path: Path, image_index: int = 0) -> bool:
    """
    포스트 파일에 이미지 참조를 추가합니다.
    
    Args:
        post_file: 포스트 파일 경로
        image_path: 이미지 파일 경로 (assets/images 기준)
        image_index: 이미지 인덱스
        
    Returns:
        성공 여부
    """
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Front matter 파싱
        metadata, body = parse_frontmatter(content)
        
        # 이미지 경로 (assets/images 기준)
        image_ref = f"/assets/images/{image_path.name}"
        
        # 이미 이미지가 front matter에 있는지 확인
        if 'image' in metadata:
            existing_image = metadata['image']
            # 같은 이미지면 스킵
            if existing_image == image_ref:
                print(f"    ℹ️  Image already in front matter")
                return True
        
        # 본문에 이미지가 이미 있는지 확인
        image_markdown = f"![이미지]({image_ref})"
        if image_markdown in content or image_ref in content:
            print(f"    ℹ️  Image already in content")
            return True
        
        # Front matter 재구성
        if content.startswith('---'):
            end_match = re.search(r'\n---\n', content[3:])
            if end_match:
                frontmatter_text = content[3:end_match.start() + 3]
                body = content[end_match.end():]
            else:
                body = content
                frontmatter_text = ""
        else:
            body = content
            frontmatter_text = ""
        
        # 서론 섹션 찾기
        intro_pattern = r'## 서론'
        intro_match = re.search(intro_pattern, body)
        
        if intro_match:
            # 서론 섹션 끝 부분 찾기
            intro_end = intro_match.end()
            # 다음 섹션 시작까지 찾기
            next_section = re.search(r'\n## ', body[intro_end:])
            if next_section:
                insert_pos = intro_end + next_section.start()
            else:
                insert_pos = intro_end + 200  # 서론 섹션 끝 부분
        else:
            # 서론이 없으면 첫 번째 섹션 앞에 삽입
            first_section = re.search(r'\n## ', body)
            if first_section:
                insert_pos = first_section.start()
            else:
                insert_pos = 100
        
        # 이미지 삽입
        image_block = f"\n\n![포스트 이미지]({image_ref})\n*그림: 포스트 이미지*\n\n"
        body = body[:insert_pos] + image_block + body[insert_pos:]
        
        # 전체 내용 재구성
        if frontmatter_text:
            content = f"---{frontmatter_text}\n---\n{body}"
        else:
            content = body
        
        # 파일 저장
        with open(post_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"    ✅ Added image reference to post")
        return True
        
    except Exception as e:
        print(f"    ❌ Error adding image to post: {e}")
        return False

def parse_frontmatter(content: str) -> Tuple[dict, str]:
    """
    Front matter를 파싱합니다.
    
    Args:
        content: 파일 내용
        
    Returns:
        (metadata 딕셔너리, 본문)
    """
    metadata = {}
    body = content
    
    # Front matter 시작 확인
    if content.startswith('---'):
        # Front matter 끝 찾기
        end_match = re.search(r'\n---\n', content[3:])
        if end_match:
            frontmatter_text = content[3:end_match.start() + 3]
            body = content[end_match.end():]
            
            # 간단한 YAML 파싱
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    metadata[key] = value
    
    return metadata, body

def process_post(post_file: Path, force: bool = False) -> Tuple[int, int]:
    """
    단일 포스트를 처리합니다.
    
    Args:
        post_file: 포스트 파일 경로
        force: 이미 존재하는 이미지도 다시 다운로드할지 여부
        
    Returns:
        (성공한 이미지 수, 실패한 이미지 수)
    """
    print(f"\n📄 Processing: {post_file.name}")
    
    # Front matter 읽기
    try:
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        metadata, _ = parse_frontmatter(content)
    except Exception as e:
        print(f"  ❌ Error reading post: {e}")
        return (0, 0)
    
    # original_url 확인
    original_url = metadata.get('original_url', '')
    if not original_url or 'twodragon.tistory.com' not in original_url:
        print(f"  ⏭️  No tistory URL found")
        return (0, 0)
    
    # 이미지 URL 추출
    image_urls = extract_images_from_tistory(original_url)
    if not image_urls:
        print(f"  ⚠️  No images found")
        return (0, 0)
    
    # 첫 번째 이미지만 사용 (메인 이미지)
    main_image_url = image_urls[0]
    
    # 이미지 확장자 확인
    image_ext = extract_image_extension_from_url(main_image_url)
    
    # 이미지 파일명 생성
    image_filename = get_image_filename(post_file, 0)
    # 확장자 교체
    image_filename = Path(image_filename).stem + image_ext
    image_path = IMAGES_DIR / image_filename
    
    # 이미지 다운로드
    if force or not image_path.exists():
        success = download_image(main_image_url, image_path)
        if not success:
            return (0, 1)
    else:
        print(f"    ℹ️  Image already exists: {image_filename}")
    
    # 포스트에 이미지 추가
    add_image_to_post(post_file, image_path)
    
    return (1, 0)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch images from Tistory blog posts')
    parser.add_argument('--test', action='store_true', help='Test mode: process only first post')
    parser.add_argument('--force', action='store_true', help='Force re-download existing images')
    args = parser.parse_args()
    
    print("🚀 Starting Tistory image fetch process...\n")
    
    # 디렉토리 확인
    if not POSTS_DIR.exists():
        print(f"❌ Posts directory not found: {POSTS_DIR}")
        sys.exit(1)
    
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 모든 포스트 파일 찾기
    post_files = sorted(POSTS_DIR.glob("*.md"))
    
    if not post_files:
        print("❌ No post files found")
        sys.exit(1)
    
    # 테스트 모드: 첫 번째 포스트만 처리
    if args.test:
        post_files = post_files[:1]
        print("🧪 Test mode: processing first post only\n")
    
    print(f"📚 Found {len(post_files)} post file(s) to process\n")
    
    # 처리 통계
    total_success = 0
    total_failed = 0
    processed = 0
    
    # 각 포스트 처리
    for post_file in post_files:
        success, failed = process_post(post_file, force=args.force)
        total_success += success
        total_failed += failed
        processed += 1
        
        # Rate limiting (서버 부하 방지)
        if processed < len(post_files):
            time.sleep(2)
    
    # 결과 출력
    print(f"\n{'='*60}")
    print(f"✅ Processed: {processed} post(s)")
    print(f"✅ Success: {total_success} image(s)")
    print(f"❌ Failed: {total_failed} image(s)")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
