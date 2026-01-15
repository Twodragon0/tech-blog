#!/usr/bin/env python3
"""
프로세스/워크플로우 이미지를 Mermaid 다이어그램으로 대체하는 스크립트
"""

import re
import os
from pathlib import Path

# Mermaid 다이어그램 템플릿
MERMAID_TEMPLATES = {
    'container_security_layers': '''```mermaid
graph TB
    subgraph SecurityLayers["Security Layers"]
        ImageScan["Image Scanning<br/>Trivy, Snyk"]
        SecretMgmt["Secret Management<br/>K8s Secrets, Vault"]
        NonRoot["Non-root User<br/>runAsNonRoot"]
        ReadOnly["Read-only Filesystem<br/>readOnlyRootFilesystem"]
        CapDrop["Capabilities Drop<br/>capabilities.drop: ALL"]
        NetworkPolicy["Network Policies<br/>Pod Isolation"]
    end
    
    App["Application Container"]
    
    ImageScan --> SecretMgmt
    SecretMgmt --> NonRoot
    NonRoot --> ReadOnly
    ReadOnly --> CapDrop
    CapDrop --> NetworkPolicy
    NetworkPolicy --> App
    
    style ImageScan fill:#e1f5ff
    style SecretMgmt fill:#e1f5ff
    style NonRoot fill:#e1f5ff
    style ReadOnly fill:#e1f5ff
    style CapDrop fill:#e1f5ff
    style NetworkPolicy fill:#e1f5ff
    style App fill:#fff4e1
```''',
    
    'devsecops_workflow': '''```mermaid
graph LR
    subgraph Dev["Dev Phase"]
        Code["Code<br/>Secure Dockerfile"]
        Build["Build<br/>Image Scanning"]
    end
    
    subgraph Sec["Sec Phase"]
        Scan["Security Scan<br/>Trivy, Snyk"]
        Policy["Policy Check<br/>K8s YAML Validation"]
    end
    
    subgraph Ops["Ops Phase"]
        Deploy["Deploy<br/>Secure Deployment"]
        Monitor["Monitor<br/>Runtime Security"]
    end
    
    Code --> Build
    Build --> Scan
    Scan --> Policy
    Policy --> Deploy
    Deploy --> Monitor
    Monitor --> Code
    
    style Code fill:#e1f5ff
    style Build fill:#fff4e1
    style Scan fill:#ffebee
    style Policy fill:#fff4e1
    style Deploy fill:#e8f5e9
    style Monitor fill:#f3e5f5
```''',
    
    'pod_security_standards': '''```mermaid
graph LR
    Privileged["Privileged<br/>No restrictions<br/>System Pods"]
    Baseline["Baseline<br/>Minimal security<br/>General Apps"]
    Restricted["Restricted<br/>Strongest policies<br/>Sensitive Workloads"]
    
    Privileged --> Baseline
    Baseline --> Restricted
    
    style Privileged fill:#ffebee
    style Baseline fill:#fff4e1
    style Restricted fill:#e8f5e9
```''',
    
    'user_namespaces': '''```mermaid
graph TB
    subgraph Host["Host System"]
        HostRoot["Host Root User<br/>UID 0"]
        HostUser["Host Non-root User<br/>UID 1000"]
    end
    
    subgraph Container["Container"]
        ContainerRoot["Container Root<br/>UID 0"]
        ContainerApp["Container App<br/>UID 1000"]
    end
    
    ContainerRoot -.->|"User Namespace Mapping"| HostUser
    ContainerApp -.->|"Direct Mapping"| HostUser
    HostRoot -.->|"Isolated"| ContainerRoot
    
    style HostRoot fill:#ffebee
    style HostUser fill:#e8f5e9
    style ContainerRoot fill:#fff4e1
    style ContainerApp fill:#e1f5ff
```''',
}

# 이미지 패턴 매칭
IMAGE_PATTERNS = {
    'container_security_layers': r'!\[.*?Container.*?Security.*?Layers.*?\]\([^)]+container_security_layers[^)]+\)',
    'devsecops_workflow': r'!\[.*?Devsecops.*?Workflow.*?\]\([^)]+devsecops_workflow[^)]+\)',
    'pod_security_standards': r'!\[.*?Pod.*?Security.*?Standards.*?\]\([^)]+pod_security_standards[^)]+\)',
    'user_namespaces': r'!\[.*?User.*?Namespaces.*?\]\([^)]+user_namespaces[^)]+\)',
}

# 이미지 설명 텍스트 패턴
CAPTION_PATTERNS = {
    'container_security_layers': r'\*그림:.*?Container.*?Security.*?Layers.*?\*',
    'devsecops_workflow': r'\*그림:.*?Devsecops.*?Workflow.*?\*',
    'pod_security_standards': r'\*그림:.*?Pod.*?Security.*?Standards.*?\*',
    'user_namespaces': r'\*그림:.*?User.*?Namespaces.*?\*',
}


def replace_image_with_mermaid(content: str, image_type: str) -> str:
    """이미지를 Mermaid 다이어그램으로 대체"""
    if image_type not in MERMAID_TEMPLATES:
        return content
    
    # 이미지 패턴 찾기
    image_pattern = IMAGE_PATTERNS[image_type]
    caption_pattern = CAPTION_PATTERNS[image_type]
    
    # 이미지와 캡션을 함께 찾아서 대체
    combined_pattern = rf'({image_pattern})\s*\n\s*({caption_pattern})'
    
    def replace_func(match):
        # 이미지 앞의 텍스트 확인
        before = content[:match.start()]
        lines_before = before.split('\n')
        
        # 제목이나 설명이 있는지 확인
        title_text = ""
        if len(lines_before) >= 2:
            prev_line = lines_before[-1].strip()
            prev_prev_line = lines_before[-2].strip() if len(lines_before) >= 2 else ""
            
            # 제목 패턴 확인 (####, ### 등)
            if prev_prev_line.startswith('####') or prev_prev_line.startswith('###'):
                title_text = prev_prev_line + "\n\n"
            elif prev_line.startswith('####') or prev_line.startswith('###'):
                title_text = prev_line + "\n\n"
        
        # Mermaid 다이어그램으로 대체
        mermaid_code = MERMAID_TEMPLATES[image_type]
        
        # 제목이 있으면 제목 포함, 없으면 설명 추가
        if title_text:
            return title_text + mermaid_code
        else:
            # 이미지 타입에 따른 설명 추가
            descriptions = {
                'container_security_layers': '컨테이너 보안은 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다:\n\n',
                'devsecops_workflow': '컨테이너 보안은 DevSecOps 사이클을 통해 코드로 관리됩니다:\n\n',
                'pod_security_standards': 'Pod Security Standards는 세 가지 보안 레벨을 제공합니다:\n\n',
                'user_namespaces': 'User Namespaces는 컨테이너 내 root 사용자를 호스트의 비권한 사용자로 매핑하여 컨테이너 탈출 공격의 위험을 크게 감소시킵니다:\n\n',
            }
            return descriptions.get(image_type, '') + mermaid_code
    
    # 대체 실행
    new_content = re.sub(combined_pattern, replace_func, content, flags=re.IGNORECASE | re.MULTILINE)
    
    return new_content


def process_file(file_path: Path) -> bool:
    """파일 처리"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 각 이미지 타입별로 대체
        for image_type in MERMAID_TEMPLATES.keys():
            content = replace_image_with_mermaid(content, image_type)
        
        # 변경사항이 있으면 저장
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 처리 완료: {file_path.name}")
            return True
        else:
            print(f"- 변경 없음: {file_path.name}")
            return False
            
    except Exception as e:
        print(f"✗ 오류 발생 ({file_path.name}): {e}")
        return False


def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"오류: {posts_dir} 디렉토리를 찾을 수 없습니다.")
        return
    
    print("프로세스 이미지를 Mermaid 다이어그램으로 대체 중...\n")
    
    processed_count = 0
    total_count = 0
    
    for md_file in sorted(posts_dir.glob('*.md')):
        total_count += 1
        if process_file(md_file):
            processed_count += 1
    
    print(f"\n처리 완료: {processed_count}/{total_count} 파일")


if __name__ == '__main__':
    main()
