#!/usr/bin/env python3
"""
이미지 파일 확인 및 생성 가이드 스크립트
포스팅별 이미지 파일 존재 여부를 확인하고 Gemini CLI 명령어를 생성합니다.
"""

import os
import re
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
GEMINI_GUIDE = PROJECT_ROOT / "GEMINI_IMAGE_GUIDE.md"


def extract_post_info(post_file: Path) -> Dict:
    """포스팅 파일에서 정보 추출"""
    content = post_file.read_text(encoding='utf-8')
    
    # Front matter 추출
    front_matter_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
    front_matter = {}
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        for line in front_matter_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                front_matter[key.strip()] = value.strip().strip('"')
    
    return {
        'title': front_matter.get('title', ''),
        'category': front_matter.get('categories', front_matter.get('category', '')),
        'tags': front_matter.get('tags', '[]'),
        'image': front_matter.get('image', ''),
        'filename': post_file.name,
        'date': front_matter.get('date', '')
    }


def check_image_exists(image_path: str) -> Tuple[bool, Path]:
    """이미지 파일 존재 여부 확인"""
    if not image_path:
        return False, None
    
    # /assets/images/... 형식에서 실제 경로 추출
    if image_path.startswith('/assets/images/'):
        image_file = PROJECT_ROOT / image_path.lstrip('/')
    else:
        image_file = IMAGES_DIR / Path(image_path).name
    
    return image_file.exists(), image_file


def generate_gemini_command(post_info: Dict, image_type: str = "architecture") -> str:
    """Gemini CLI 명령어 생성"""
    title = post_info['title']
    category = post_info['category']
    
    # 카테고리에 따른 기본 명령어 템플릿
    templates = {
        'cloud': f"""Create a nano banana style AWS architecture diagram for: {title}
Style: minimalist, clean lines, professional tech illustration
Colors: AWS orange (#FF9900), Blue for networking, Green for security
Layout: horizontal, optimized for blog post
Include: Korean labels for key components""",
        
        'security': f"""Create a nano banana style security architecture diagram for: {title}
Style: minimalist security illustration
Colors: Red (#CC0000) for threats, Green (#00AA44) for security measures
Layout: horizontal flow showing security layers
Include: Korean labels (보안 레이어, 위협, 보호)""",
        
        'incident': f"""Create a nano banana style incident timeline for: {title}
Style: minimalist timeline illustration
Colors: Red for incident start, Orange for investigation, Yellow for response, Green for recovery
Layout: horizontal timeline
Include: Korean labels (인지, 조사, 대응, 복구)""",
        
        'devsecops': f"""Create a nano banana style DevSecOps pipeline diagram for: {title}
Style: minimalist CI/CD security illustration
Colors: Blue for CI/CD, Green for security, Orange for deployment
Layout: horizontal pipeline flow
Include: Korean labels (개발, 보안, 배포)"""
    }
    
    template = templates.get(category, templates['cloud'])
    
    return f"""gemini "{template}\""""


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='이미지 파일 확인 및 생성 가이드')
    parser.add_argument('--all', action='store_true', help='모든 포스팅 확인')
    parser.add_argument('--missing', action='store_true', help='이미지가 없는 포스팅만 표시')
    parser.add_argument('--recent', type=int, default=10, help='최근 N개 포스팅만 확인')
    parser.add_argument('--generate-commands', action='store_true', help='Gemini CLI 명령어 생성')
    
    args = parser.parse_args()
    
    # 포스팅 파일 목록
    if args.all:
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    else:
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:args.recent]
    
    print(f"📊 {len(posts)}개 포스팅 이미지 확인 중...\n")
    
    results = []
    for post_file in posts:
        post_info = extract_post_info(post_file)
        has_image, image_path = check_image_exists(post_info['image'])
        
        result = {
            'post': post_info,
            'has_image': has_image,
            'image_path': image_path
        }
        
        if args.missing and has_image:
            continue
        
        results.append(result)
        
        # 결과 출력
        status = "✅" if has_image else "❌"
        print(f"{status} {post_info['filename']}")
        print(f"   제목: {post_info['title'][:60]}...")
        print(f"   이미지: {post_info['image'] if post_info['image'] else '(없음)'}")
        
        if has_image and image_path:
            file_size = image_path.stat().st_size / 1024  # KB
            print(f"   파일 크기: {file_size:.1f} KB")
        
        if not has_image and args.generate_commands:
            command = generate_gemini_command(post_info)
            print(f"   💡 생성 명령어:")
            print(f"   {command}")
        
        print()
    
    # 요약 통계
    total = len(results)
    with_image = sum(1 for r in results if r['has_image'])
    missing_image = total - with_image
    
    print("=" * 80)
    print("📊 이미지 파일 통계")
    print("=" * 80)
    print(f"전체 포스팅: {total}")
    print(f"이미지 있음: {with_image} ({with_image/total*100:.1f}%)")
    print(f"이미지 없음: {missing_image} ({missing_image/total*100:.1f}%)")
    
    if missing_image > 0:
        print(f"\n❌ 이미지가 없는 포스팅:")
        for r in results:
            if not r['has_image']:
                print(f"  - {r['post']['filename']}")
                print(f"    제목: {r['post']['title']}")


if __name__ == '__main__':
    main()
