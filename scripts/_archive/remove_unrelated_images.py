#!/usr/bin/env python3
"""
연관 없는 이미지와 다이어그램을 제거하는 스크립트
"""

import re
from pathlib import Path

# 연관 없는 이미지 패턴 (주제별로 제거할 이미지)
UNRELATED_IMAGE_PATTERNS = {
    'npm': ['docker_vs_vm', 'container_security_layers', 'user_namespaces', 'devsecops_workflow'],
    'karpenter': ['docker_vs_vm', 'container_security_layers', 'kubernetes_architecture'],
    'incident': ['docker_vs_vm'],
    'general': ['docker_vs_vm', 'kubernetes_architecture'],  # 일반 포스팅에서도 docker_vs_vm, kubernetes_architecture는 대부분 무관
    'isms': ['kubernetes_architecture'],  # ISMS-P 인증 관련 포스팅에서 Kubernetes는 직접 관련 없음
}

# 연관 없는 Mermaid 다이어그램 패턴
UNRELATED_MERMAID_PATTERNS = {
    'npm': ['container', 'kubernetes', 'docker', 'security layers', 'user namespace'],
    'karpenter': ['container security', 'security layers'],
}

def extract_topic_from_filename(filename: str) -> str:
    """파일명에서 주제 추출"""
    filename_lower = filename.lower()
    
    if 'npm' in filename_lower or 'shai-hulud' in filename_lower:
        return 'npm'
    elif 'karpenter' in filename_lower:
        return 'karpenter'
    elif 'incident' in filename_lower or 'post-mortem' in filename_lower:
        return 'incident'
    elif 'isms' in filename_lower or 'isms-p' in filename_lower:
        return 'isms'
    elif 'gcp' in filename_lower and 'gke' in filename_lower:
        return 'gcp-gke'  # GKE 관련이면 Kubernetes 아키텍처 관련 있을 수 있음
    else:
        return 'general'

def remove_unrelated_images(content: str, topic: str) -> tuple[str, int]:
    """연관 없는 이미지 제거"""
    if topic not in UNRELATED_IMAGE_PATTERNS:
        return content, 0
    
    removed_count = 0
    patterns = UNRELATED_IMAGE_PATTERNS[topic]
    
    for pattern in patterns:
        # 이미지 마크다운 패턴 찾기
        img_pattern = rf'!\[.*?\]\([^)]*{re.escape(pattern)}[^)]*\)'
        matches = re.finditer(img_pattern, content, re.IGNORECASE)
        
        for match in list(matches):
            # 이미지 앞뒤의 빈 줄과 캡션도 함께 제거
            start = match.start()
            end = match.end()
            
            # 캡션 찾기 (다음 줄에 *그림: ...* 형태)
            caption_pattern = r'\*그림:.*?\*'
            caption_match = re.search(caption_pattern, content[end:end+200])
            if caption_match:
                end = end + caption_match.end()
            
            # 앞뒤 빈 줄 제거
            before = content[:start].rstrip()
            after = content[end:].lstrip()
            
            # 빈 줄이 2개 이상이면 1개만 남기기
            if before.endswith('\n\n'):
                before = before.rstrip('\n') + '\n'
            if after.startswith('\n\n'):
                after = '\n' + after.lstrip('\n')
            
            content = before + after
            removed_count += 1
    
    return content, removed_count

def remove_unrelated_mermaid(content: str, topic: str) -> tuple[str, int]:
    """연관 없는 Mermaid 다이어그램 제거"""
    if topic not in UNRELATED_MERMAID_PATTERNS:
        return content, 0
    
    removed_count = 0
    patterns = UNRELATED_MERMAID_PATTERNS[topic]
    
    # Mermaid 다이어그램 찾기
    mermaid_pattern = r'```mermaid\s*\n(.*?)```'
    
    def should_remove(match):
        diagram_content = match.group(1).lower()
        for pattern in patterns:
            if pattern in diagram_content:
                # 주제 관련 키워드가 있는지 확인
                topic_keywords = {
                    'npm': ['npm', 'package', 'supply-chain', 'supply chain'],
                    'karpenter': ['karpenter', 'node', 'consolidation'],
                }
                if topic in topic_keywords:
                    for keyword in topic_keywords[topic]:
                        if keyword in diagram_content:
                            return False  # 주제 관련 키워드가 있으면 유지
                return True  # 주제 관련 키워드가 없으면 제거
        return False
    
    def replace_func(match):
        nonlocal removed_count
        if should_remove(match):
            removed_count += 1
            return ''  # 다이어그램 제거
        return match.group(0)  # 유지
    
    content = re.sub(mermaid_pattern, replace_func, content, flags=re.DOTALL | re.IGNORECASE)
    
    # 연속된 빈 줄 정리
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content, removed_count

def process_file(file_path: Path) -> dict:
    """파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        topic = extract_topic_from_filename(file_path.name)
        
        # 연관 없는 이미지 제거
        content, img_count = remove_unrelated_images(content, topic)
        
        # 연관 없는 Mermaid 다이어그램 제거
        content, mermaid_count = remove_unrelated_mermaid(content, topic)
        
        # 변경사항이 있으면 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {
                'file': file_path.name,
                'topic': topic,
                'images_removed': img_count,
                'mermaid_removed': mermaid_count,
                'success': True
            }
        else:
            return {
                'file': file_path.name,
                'topic': topic,
                'images_removed': 0,
                'mermaid_removed': 0,
                'success': False
            }
            
    except Exception as e:
        return {
            'file': file_path.name,
            'error': str(e),
            'success': False
        }

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"오류: {posts_dir} 디렉토리를 찾을 수 없습니다.")
        return
    
    print("연관 없는 이미지 및 다이어그램 제거 중...\n")
    
    results = []
    for md_file in sorted(posts_dir.glob('*.md')):
        result = process_file(md_file)
        results.append(result)
    
    # 결과 출력
    processed = [r for r in results if r.get('success') and (r.get('images_removed', 0) > 0 or r.get('mermaid_removed', 0) > 0)]
    
    if processed:
        print(f"처리 완료: {len(processed)}개 파일\n")
        
        total_images = sum(r.get('images_removed', 0) for r in processed)
        total_mermaid = sum(r.get('mermaid_removed', 0) for r in processed)
        
        for result in processed:
            print(f"✓ {result['file']}")
            if result.get('images_removed', 0) > 0:
                print(f"  - 이미지 제거: {result['images_removed']}개")
            if result.get('mermaid_removed', 0) > 0:
                print(f"  - Mermaid 제거: {result['mermaid_removed']}개")
        
        print(f"\n총 제거: 이미지 {total_images}개, Mermaid {total_mermaid}개")
    else:
        print("제거할 연관 없는 이미지/다이어그램이 없습니다.")

if __name__ == '__main__':
    main()
