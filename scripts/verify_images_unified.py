#!/usr/bin/env python3
"""
통합 이미지 검증 스크립트
- 이미지 파일 존재 여부 확인
- 이미지 파일명이 영어로 되어 있는지 확인
- 포스팅 파일의 이미지 경로와 실제 파일 매칭
- 관련 없는 이미지 확인
- Gemini CLI 명령어 생성 (선택사항)
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
GEMINI_GUIDE = PROJECT_ROOT / "GEMINI_IMAGE_GUIDE.md"


def has_korean(text: str) -> bool:
    """한글이 포함되어 있는지 확인"""
    korean_pattern = re.compile(r'[가-힣]')
    return bool(korean_pattern.search(text))


def extract_image_paths(content: str) -> List[str]:
    """포스팅 내용에서 이미지 경로 추출"""
    image_paths = []
    
    # Front Matter의 image 필드
    fm_match = re.search(r'^image:\s*(.+)$', content, re.MULTILINE)
    if fm_match:
        image_paths.append(fm_match.group(1).strip())
    
    # HTML img 태그
    img_tags = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    image_paths.extend(img_tags)
    
    # 마크다운 이미지 링크
    md_images = re.findall(r'!\[.*?\]\(([^)]+)\)', content)
    image_paths.extend(md_images)
    
    # Jekyll relative_url 필터 제거
    cleaned_paths = []
    for path in image_paths:
        # {{ '/assets/images/...' | relative_url }} 형식 처리
        if "| relative_url" in path:
            path = path.split("|")[0].strip().strip("'\"")
        # /assets/images/로 시작하는 경로만
        if '/assets/images/' in path:
            filename = path.split('/assets/images/')[-1]
            cleaned_paths.append(filename)
        elif path.startswith('/assets/images/'):
            cleaned_paths.append(path.replace('/assets/images/', ''))
    
    return list(set(cleaned_paths))  # 중복 제거


def check_image_exists(image_path: str) -> Tuple[bool, Optional[Path]]:
    """이미지 파일 존재 여부 확인"""
    if not image_path:
        return False, None
    
    # /assets/images/... 형식에서 실제 경로 추출
    if image_path.startswith('/assets/images/'):
        image_file = PROJECT_ROOT / image_path.lstrip('/')
    else:
        image_file = IMAGES_DIR / Path(image_path).name
    
    return image_file.exists(), image_file


def check_image_file(filename: str) -> Dict:
    """이미지 파일 검증"""
    result = {
        'filename': filename,
        'exists': False,
        'has_korean': False,
        'file_path': None,
    }
    
    image_file = IMAGES_DIR / filename
    result['file_path'] = image_file
    result['exists'] = image_file.exists()
    result['has_korean'] = has_korean(filename)
    
    return result


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


def process_post_file(file_path: Path, generate_commands: bool = False) -> Dict:
    """포스팅 파일 처리"""
    result = {
        'file': str(file_path),
        'images': [],
        'issues': [],
        'post_info': None,
    }
    
    try:
        content = file_path.read_text(encoding='utf-8')
        image_paths = extract_image_paths(content)
        post_info = extract_post_info(file_path)
        result['post_info'] = post_info
        
        for img_path in image_paths:
            img_result = check_image_file(img_path)
            result['images'].append(img_result)
            
            if not img_result['exists']:
                result['issues'].append(f"이미지 파일을 찾을 수 없습니다: {img_path}")
            
            if img_result['has_korean']:
                result['issues'].append(f"이미지 파일명에 한글이 포함되어 있습니다: {img_path}")
        
        # 메인 이미지 확인
        if post_info['image']:
            has_image, image_path = check_image_exists(post_info['image'])
            if not has_image:
                result['issues'].append(f"Front matter의 메인 이미지를 찾을 수 없습니다: {post_info['image']}")
                if generate_commands:
                    result['gemini_command'] = generate_gemini_command(post_info)
        
        return result
        
    except Exception as e:
        result['issues'].append(f"처리 중 오류 발생: {str(e)}")
        return result


def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='통합 이미지 검증 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 모든 포스팅 확인
  python3 scripts/verify_images_unified.py --all
  
  # 이미지가 없는 포스팅만 표시
  python3 scripts/verify_images_unified.py --missing
  
  # Gemini CLI 명령어 생성
  python3 scripts/verify_images_unified.py --all --generate-commands
        """
    )
    
    parser.add_argument('--all', action='store_true', help='모든 포스팅 확인')
    parser.add_argument('--missing', action='store_true', help='이미지가 없는 포스팅만 표시')
    parser.add_argument('--recent', type=int, default=10, help='최근 N개 포스팅만 확인')
    parser.add_argument('--generate-commands', action='store_true', help='Gemini CLI 명령어 생성')
    
    args = parser.parse_args()
    
    if not POSTS_DIR.exists():
        print(f"❌ 포스팅 디렉토리를 찾을 수 없습니다: {POSTS_DIR}")
        sys.exit(1)
    
    if not IMAGES_DIR.exists():
        print(f"❌ 이미지 디렉토리를 찾을 수 없습니다: {IMAGES_DIR}")
        sys.exit(1)
    
    # 포스팅 파일 목록
    if args.all:
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    else:
        posts = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)[:args.recent]
    
    print(f"📊 {len(posts)}개 포스팅 이미지 확인 중...\n")
    
    results = []
    total_issues = 0
    missing_images = []
    korean_filenames = []
    
    for post_file in posts:
        result = process_post_file(post_file, generate_commands=args.generate_commands)
        
        if args.missing and not result['issues']:
            continue
        
        if result['issues']:
            results.append(result)
            total_issues += len(result['issues'])
            
            # 결과 출력
            print(f"📄 {post_file.name}")
            print(f"   제목: {result['post_info']['title'][:60] if result['post_info'] else 'N/A'}...")
            
            for issue in result['issues']:
                print(f"  ⚠️  {issue}")
                
                if "찾을 수 없습니다" in issue:
                    missing_images.append({
                        'file': post_file.name,
                        'image': issue.split(': ')[-1] if ': ' in issue else ''
                    })
                elif "한글이 포함" in issue:
                    korean_filenames.append({
                        'file': post_file.name,
                        'image': issue.split(': ')[-1] if ': ' in issue else ''
                    })
            
            if args.generate_commands and 'gemini_command' in result:
                print(f"   💡 생성 명령어:")
                print(f"   {result['gemini_command']}")
            
            print()
    
    # 요약 통계
    print("=" * 80)
    print("📊 이미지 파일 통계")
    print("=" * 80)
    print(f"전체 포스팅: {len(posts)}")
    print(f"문제 발견: {len(results)}")
    print(f"총 문제 수: {total_issues}")
    
    if missing_images:
        print(f"\n❌ 이미지 파일을 찾을 수 없는 포스팅 ({len(missing_images)}개):")
        for item in missing_images:
            print(f"  - {item['file']}: {item['image']}")
    
    if korean_filenames:
        print(f"\n⚠️  이미지 파일명에 한글이 포함된 포스팅 ({len(korean_filenames)}개):")
        for item in korean_filenames:
            print(f"  - {item['file']}: {item['image']}")
    
    if not results:
        print("\n✅ 모든 이미지 파일이 정상적으로 검증되었습니다!")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
