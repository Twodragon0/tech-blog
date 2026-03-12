#!/usr/bin/env python3
"""
포스팅에서 연관 없는 이미지를 찾는 스크립트
"""

import re
from pathlib import Path

# 연관 없는 이미지 패턴 (주제와 무관한 일반적인 이미지들)
UNRELATED_PATTERNS = {
    'docker_vs_vm': r'docker_vs_vm',
    'kubernetes_architecture': r'kubernetes_architecture',
    'container_security_layers': r'container_security_layers',
    'user_namespaces': r'user_namespaces',
    'devsecops_workflow': r'devsecops_workflow',
    'pod_security_standards': r'pod_security_standards',
}

# 포스팅 주제별로 관련 있는 이미지 타입
TOPIC_RELATED_IMAGES = {
    'npm': ['npm', 'supply-chain', 'package'],
    'karpenter': ['karpenter', 'node', 'consolidation'],
    'aws': ['aws', 'eks', 'vpc', 'iam'],
    'kubernetes': ['kubernetes', 'k8s', 'pod', 'deployment'],
    'docker': ['docker', 'container'],
    'security': ['security', 'vulnerability', 'attack'],
    'incident': ['incident', 'post-mortem', 'timeline'],
}

def extract_topic_from_filename(filename: str) -> str:
    """파일명에서 주제 추출"""
    filename_lower = filename.lower()

    if 'npm' in filename_lower or 'shai-hulud' in filename_lower:
        return 'npm'
    elif 'karpenter' in filename_lower:
        return 'karpenter'
    elif 'aws' in filename_lower or 'eks' in filename_lower:
        return 'aws'
    elif 'kubernetes' in filename_lower or 'k8s' in filename_lower:
        return 'kubernetes'
    elif 'docker' in filename_lower:
        return 'docker'
    elif 'incident' in filename_lower or 'post-mortem' in filename_lower:
        return 'incident'
    else:
        return 'general'

def check_image_relevance(file_path: Path) -> dict:
    """파일에서 이미지 관련성 확인"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 이미지 찾기
        image_pattern = r'!\[.*?\]\(([^)]+)\)'
        images = re.findall(image_pattern, content)

        # Mermaid 다이어그램 찾기
        mermaid_pattern = r'```mermaid\s*\n(.*?)```'
        mermaid_diagrams = re.findall(mermaid_pattern, content, re.DOTALL)

        topic = extract_topic_from_filename(file_path.name)

        unrelated_images = []
        unrelated_mermaid = []

        # 이미지 관련성 확인
        for img_path in images:
            img_lower = img_path.lower()
            is_unrelated = False

            # 연관 없는 패턴 확인
            for pattern_name, pattern in UNRELATED_PATTERNS.items():
                if re.search(pattern, img_lower):
                    # 주제별 예외 확인
                    if topic == 'kubernetes' and pattern_name in ['kubernetes_architecture', 'pod_security_standards']:
                        continue
                    if topic == 'docker' and pattern_name == 'docker_vs_vm':
                        continue
                    if topic == 'aws' and pattern_name == 'kubernetes_architecture':
                        continue

                    is_unrelated = True
                    unrelated_images.append({
                        'path': img_path,
                        'pattern': pattern_name,
                        'line': content[:content.find(img_path)].count('\n') + 1
                    })
                    break

        # Mermaid 다이어그램 관련성 확인
        for i, diagram in enumerate(mermaid_diagrams):
            diagram_lower = diagram.lower()

            # 주제와 무관한 다이어그램 확인
            if topic == 'npm' and ('container' in diagram_lower or 'kubernetes' in diagram_lower or 'docker' in diagram_lower):
                if 'npm' not in diagram_lower and 'package' not in diagram_lower and 'supply-chain' not in diagram_lower:
                    unrelated_mermaid.append({
                        'index': i + 1,
                        'content': diagram[:100] + '...',
                        'line': content[:content.find(diagram)].count('\n') + 1
                    })
            elif topic == 'karpenter' and ('container' in diagram_lower or 'security layers' in diagram_lower):
                if 'karpenter' not in diagram_lower and 'node' not in diagram_lower and 'consolidation' not in diagram_lower:
                    unrelated_mermaid.append({
                        'index': i + 1,
                        'content': diagram[:100] + '...',
                        'line': content[:content.find(diagram)].count('\n') + 1
                    })

        return {
            'file': file_path.name,
            'topic': topic,
            'unrelated_images': unrelated_images,
            'unrelated_mermaid': unrelated_mermaid,
            'total_images': len(images),
            'total_mermaid': len(mermaid_diagrams)
        }

    except Exception as e:
        return {
            'file': file_path.name,
            'error': str(e)
        }

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'

    if not posts_dir.exists():
        print(f"오류: {posts_dir} 디렉토리를 찾을 수 없습니다.")
        return

    print("포스팅에서 연관 없는 이미지 확인 중...\n")

    results = []
    for md_file in sorted(posts_dir.glob('*.md')):
        result = check_image_relevance(md_file)
        if 'error' not in result:
            if result['unrelated_images'] or result['unrelated_mermaid']:
                results.append(result)

    # 결과 출력
    if results:
        print(f"연관 없는 이미지/다이어그램이 발견된 포스팅: {len(results)}개\n")

        for result in results:
            print(f"📄 {result['file']}")
            print(f"   주제: {result['topic']}")
            print(f"   총 이미지: {result['total_images']}개, Mermaid: {result['total_mermaid']}개")

            if result['unrelated_images']:
                print(f"   ⚠️  연관 없는 이미지 ({len(result['unrelated_images'])}개):")
                for img in result['unrelated_images']:
                    print(f"      - {img['pattern']}: {img['path']} (라인 {img['line']})")

            if result['unrelated_mermaid']:
                print(f"   ⚠️  연관 없는 Mermaid 다이어그램 ({len(result['unrelated_mermaid'])}개):")
                for mermaid in result['unrelated_mermaid']:
                    print(f"      - 다이어그램 #{mermaid['index']} (라인 {mermaid['line']})")

            print()
    else:
        print("✅ 모든 포스팅의 이미지가 주제와 관련이 있습니다.")

if __name__ == '__main__':
    main()
