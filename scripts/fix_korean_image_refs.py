#!/usr/bin/env python3
"""
포스트에서 한글 이미지 파일명 참조를 영어로 변환하고,
빈 이미지 파일을 제거하는 스크립트
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
POSTS_DIR = PROJECT_ROOT / "_posts"

# 한글-영어 변환 사전
KOREAN_TO_ENGLISH = {
    '클라우드': 'Cloud',
    '보안': 'Security',
    '완벽': 'Complete',
    '가이드': 'Guide',
    '과정': 'Course',
    '주차': 'Week',
    '기': 'Batch',
    '부터': 'From',
    '까지': 'To',
    '및': 'And',
    '실무': 'Practical',
    '중심': 'Centered',
    '아키텍처': 'Architecture',
    'IAM': 'IAM',
    'GKE': 'GKE',
    'GCP': 'GCP',
    'AWS': 'AWS',
    'EKS': 'EKS',
    '시큐리티': 'Security',
    '인프라': 'Infrastructure',
    '본질': 'Essence',
    '미래': 'Future',
    '로드맵': 'Roadmap',
    '분석': 'Analysis',
    '장애': 'Incident',
    '해결기': 'Resolution',
    '데이터베이스': 'Database',
    '접근': 'Access',
    '게이트웨이': 'Gateway',
    '구축하기': 'Build',
    '노드': 'Node',
    '통합': 'Integration',
    '대규모': 'Large_Scale',
    '회고': 'Review',
    '컨퍼런스': 'Conference',
    '블록체인': 'Blockchain',
    '암호화폐': 'Cryptocurrency',
    '관점에서': 'From_Perspective',
    '본': 'View',
    '도구': 'Tools',
    '모범': 'Best',
    '사례': 'Practice',
    '자동차': 'Automotive',
    '바라보는': 'Viewing',
    '글로벌': 'Global',
    '대응': 'Response',
    '일지': 'Log',
    '안내': 'Guide',
    '실무형': 'Practical',
    '인재로': 'Talent',
    '도약하라': 'Leap',
    '핵심': 'Core',
    '정복': 'Conquer',
    '실전': 'Practical',
    '취약점': 'Vulnerability',
    '점검': 'Inspection',
    '인증': 'Certification',
    '거버넌스': 'Governance',
    '기반': 'Based',
    '이메일': 'Email',
    '발송': 'Delivery',
    '신뢰도': 'Trust',
    '높이기': 'Improve',
    '설정': 'Setup',
    '공용': 'Public',
    'PC': 'PC',
    '안전하게': 'Safely',
    '패스키': 'Passkey',
    'OTP': 'OTP',
    '강력한': 'Strong',
    '암호': 'Password',
    '관리': 'Management',
    '활용법': 'Usage',
    '이슈': 'Issue',
    '확인': 'Check',
    '교체': 'Replace',
    '중요성': 'Importance',
    '마스터': 'Master',
    '셋업': 'Setup',
    '규정': 'Regulation',
    '준수': 'Compliance',
    '올인원': 'All-in-One',
    '감사': 'Audit',
    '공략': 'Strategy',
    '통합으로': 'Integration',
    '인한': 'Due_to',
    '의': '_',
    '와': '_and_',
    '를': '',
    '을': '',
    '이': '',
    '가': '',
    '에': '_in_',
    '에서': '_in_',
    '로': '_to_',
    '으로': '_to_',
    '위한': '_for_',
    '통한': '_through_',
    '활용': 'using',
    '방법': 'method',
    '년': '_year_',
    '월': '_month_',
    '일': '_day_',
}


def translate_korean_to_english(text: str) -> str:
    """한글을 영어로 변환"""
    result = text
    
    # 사전 기반 변환 (긴 단어부터)
    for korean, english in sorted(KOREAN_TO_ENGLISH.items(), key=lambda x: -len(x[0])):
        result = result.replace(korean, english)
    
    # 남은 한글 제거
    result = re.sub(r'[가-힣]', '', result)
    
    # 특수 문자를 언더스코어로 변환
    result = re.sub(r'[^\w\-]', '_', result)
    # 여러 언더스코어를 하나로
    result = re.sub(r'_+', '_', result)
    # 시작/끝 언더스코어 제거
    result = result.strip('_')
    
    return result


def find_empty_images() -> List[Path]:
    """빈 이미지 파일 찾기 (1KB 미만)"""
    empty_files = []
    
    diagram_patterns = [
        '*_docker_vs_vm.png',
        '*_kubernetes_architecture.png',
        '*_container_security_layers.png',
        '*_pod_security_standards.png',
        '*_user_namespaces.png',
        '*_devsecops_workflow.png',
    ]
    
    for pattern in diagram_patterns:
        for img_file in ASSETS_IMAGES_DIR.glob(pattern):
            try:
                size = img_file.stat().st_size
                if size < 1024:  # 1KB 미만
                    empty_files.append(img_file)
            except Exception:
                pass
    
    return empty_files


def fix_post_references(auto_yes: bool = False):
    """포스트의 한글 이미지 파일명 참조를 영어로 변환"""
    updated_posts = []
    
    for post_file in POSTS_DIR.glob('*.md'):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            # 한글이 포함된 이미지 경로 찾기
            pattern = r'/assets/images/([^)]+\.png)'
            matches = re.findall(pattern, content)
            
            for old_filename in matches:
                if re.search(r'[가-힣]', old_filename):
                    # 영어 파일명으로 변환
                    english_filename = translate_korean_to_english(old_filename)
                    
                    # 실제 파일 확인
                    old_path = ASSETS_IMAGES_DIR / old_filename
                    new_path = ASSETS_IMAGES_DIR / english_filename
                    
                    # 영어 파일명이 존재하면 참조 업데이트
                    if new_path.exists():
                        old_ref = f"/assets/images/{old_filename}"
                        new_ref = f"/assets/images/{english_filename}"
                        content = content.replace(old_ref, new_ref)
                        modified = True
                        print(f"  업데이트: {old_filename} -> {english_filename}")
                    elif old_path.exists():
                        # 한글 파일명이 존재하면 영어로 변경
                        try:
                            old_path.rename(new_path)
                            old_ref = f"/assets/images/{old_filename}"
                            new_ref = f"/assets/images/{english_filename}"
                            content = content.replace(old_ref, new_ref)
                            modified = True
                            print(f"  파일명 변경 및 참조 업데이트: {old_filename} -> {english_filename}")
                        except Exception as e:
                            print(f"  오류 ({old_filename}): {e}")
            
            if modified:
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_posts.append(post_file.name)
                print(f"✅ 업데이트 완료: {post_file.name}")
        
        except Exception as e:
            print(f"❌ 오류 ({post_file.name}): {e}")
    
    return updated_posts


def remove_empty_images(auto_yes: bool = False):
    """빈 이미지 파일 제거"""
    empty_files = find_empty_images()
    
    if not empty_files:
        print("빈 이미지 파일 없음")
        return []
    
    print(f"\n빈 이미지 파일 {len(empty_files)}개 발견:")
    for f in empty_files:
        print(f"  - {f.name}")
    
    if not auto_yes:
        response = input("\n이 파일들을 삭제하시겠습니까? (y/N): ")
        if response.lower() != 'y':
            print("삭제 취소됨")
            return []
    
    removed = []
    for f in empty_files:
        # 포스트 참조 제거
        for post_file in POSTS_DIR.glob('*.md'):
            try:
                with open(post_file, 'r', encoding='utf-8') as f_post:
                    content = f_post.read()
                
                old_ref = f"/assets/images/{f.name}"
                if old_ref in content:
                    # 이미지 참조 제거
                    content = re.sub(rf'!\[[^\]]*\]\({re.escape(old_ref)}\)\s*\n\*그림:[^\*]*\*\s*\n', '', content)
                    content = re.sub(rf'!\[[^\]]*\]\({re.escape(old_ref)}\)\s*\n', '', content)
                    
                    with open(post_file, 'w', encoding='utf-8') as f_post:
                        f_post.write(content)
                    print(f"  참조 제거: {post_file.name}")
            except Exception as e:
                print(f"  오류 ({post_file.name}): {e}")
        
        f.unlink()
        removed.append(f.name)
        print(f"  삭제됨: {f.name}")
    
    print(f"\n총 {len(removed)}개 파일 삭제 완료")
    return removed


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="한글 이미지 파일명 참조 수정 및 빈 이미지 제거")
    parser.add_argument("--yes", "-y", action="store_true", help="자동으로 모든 작업 수행")
    args = parser.parse_args()
    
    print("=" * 60)
    print("한글 이미지 파일명 참조 수정 및 빈 이미지 제거")
    print("=" * 60)
    
    # 1. 빈 이미지 파일 제거
    print("\n1. 빈 이미지 파일 확인 중...")
    remove_empty_images(auto_yes=args.yes)
    
    # 2. 포스트 참조 수정
    print("\n2. 포스트의 한글 이미지 파일명 참조 수정 중...")
    updated = fix_post_references(auto_yes=args.yes)
    
    print(f"\n총 {len(updated)}개 포스트 업데이트 완료")
    print("\n작업 완료!")


if __name__ == "__main__":
    main()
