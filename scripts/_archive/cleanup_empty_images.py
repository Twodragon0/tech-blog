#!/usr/bin/env python3
"""
빈 이미지 파일 제거 및 한글 파일명을 영어로 변환하는 스크립트
"""

import os
import re
from pathlib import Path
from typing import List

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
    """빈 이미지 파일 찾기 (1KB 미만 또는 손상된 파일)"""
    empty_files = []
    
    # 다이어그램 파일 패턴
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
                # 파일 크기 확인 (1KB 미만이면 빈 이미지로 간주)
                size = img_file.stat().st_size
                if size < 1024:
                    empty_files.append(img_file)
                    print(f"빈 이미지 발견: {img_file.name} ({size} bytes)")
            except Exception as e:
                empty_files.append(img_file)
                print(f"확인 불가: {img_file.name} ({e})")
    
    return empty_files


def find_korean_filenames() -> List[Path]:
    """한글이 포함된 파일명 찾기"""
    korean_files = []
    
    # 다이어그램 파일만 확인
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
            if re.search(r'[가-힣]', img_file.name):
                korean_files.append(img_file)
    
    return korean_files


def update_post_references(old_path: str, new_path: str):
    """포스트 파일의 이미지 참조 업데이트"""
    updated_count = 0
    
    for post_file in POSTS_DIR.glob('*.md'):
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            old_ref = f"/assets/images/{Path(old_path).name}"
            new_ref = f"/assets/images/{Path(new_path).name}"
            
            if old_ref in content:
                content = content.replace(old_ref, new_ref)
                with open(post_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                updated_count += 1
                print(f"  업데이트: {post_file.name}")
        except Exception as e:
            print(f"  오류 ({post_file.name}): {e}")
    
    return updated_count


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="빈 이미지 파일 정리 및 한글 파일명 변환")
    parser.add_argument("--yes", "-y", action="store_true", help="자동으로 모든 작업 수행")
    args = parser.parse_args()
    
    print("=" * 60)
    print("빈 이미지 파일 정리 및 한글 파일명 변환")
    print("=" * 60)
    
    # 1. 빈 이미지 파일 찾기 및 제거
    print("\n1. 빈 이미지 파일 확인 중...")
    empty_files = find_empty_images()
    
    if empty_files:
        print(f"\n빈 이미지 파일 {len(empty_files)}개 발견:")
        for f in empty_files:
            print(f"  - {f.name}")
        
        if args.yes:
            response = 'y'
        else:
            response = input("\n이 파일들을 삭제하시겠습니까? (y/N): ")
        
        if response.lower() == 'y':
            for f in empty_files:
                # 포스트 참조 제거
                update_post_references(str(f), '')
                f.unlink()
                print(f"  삭제됨: {f.name}")
            print(f"\n총 {len(empty_files)}개 파일 삭제 완료")
        else:
            print("삭제 취소됨")
    else:
        print("빈 이미지 파일 없음")
    
    # 2. 한글 파일명을 영어로 변환
    print("\n2. 한글 파일명 확인 중...")
    korean_files = find_korean_filenames()
    
    if korean_files:
        print(f"\n한글 파일명 {len(korean_files)}개 발견:")
        for f in korean_files[:10]:  # 처음 10개만 표시
            english_name = translate_korean_to_english(f.stem) + f.suffix
            print(f"  {f.name}")
            print(f"  -> {english_name}")
        if len(korean_files) > 10:
            print(f"  ... 외 {len(korean_files) - 10}개")
        
        if args.yes:
            response = 'y'
        else:
            response = input("\n이 파일들의 이름을 영어로 변경하시겠습니까? (y/N): ")
        
        if response.lower() == 'y':
            renamed_count = 0
            for old_file in korean_files:
                english_name = translate_korean_to_english(old_file.stem) + old_file.suffix
                new_file = old_file.parent / english_name
                
                # 중복 확인
                if new_file.exists() and new_file != old_file:
                    print(f"  건너뜀 (이미 존재): {new_file.name}")
                    # 기존 파일 삭제하고 참조 업데이트
                    update_post_references(str(old_file), str(new_file))
                    old_file.unlink()
                    continue
                
                try:
                    old_file.rename(new_file)
                    update_post_references(str(old_file), str(new_file))
                    renamed_count += 1
                    print(f"  변경됨: {old_file.name} -> {new_file.name}")
                except Exception as e:
                    print(f"  오류 ({old_file.name}): {e}")
            
            print(f"\n총 {renamed_count}개 파일명 변경 완료")
        else:
            print("변경 취소됨")
    else:
        print("한글 파일명 없음")
    
    print("\n작업 완료!")


if __name__ == "__main__":
    main()
