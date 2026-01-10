#!/usr/bin/env python3
"""
모든 포스트의 부적절한 GitHub 링크를 컨텍스트에 맞게 수정하는 스크립트
"""
import re
from pathlib import Path
from typing import Dict, Tuple, Optional

# 링크 교체 매핑: (패턴, 컨텍스트 키워드) -> (새 링크, 새 텍스트)
LINK_REPLACEMENTS = {
    # AWS 관련
    ('aws-samples', 'cost', '비용', 'Cost Explorer'): {
        'link': 'https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/Welcome.html',
        'text': 'AWS Cost Explorer API 문서'
    },
    ('aws-samples', 'guardduty', 'GuardDuty'): {
        'link': 'https://docs.aws.amazon.com/guardduty/',
        'text': 'AWS GuardDuty 문서'
    },
    ('aws-samples', 'security-agent', 'Security Agent'): {
        'link': 'https://docs.aws.amazon.com/security/',
        'text': 'AWS Security 문서'
    },
    ('aws-samples', 'compute-optimizer', 'Compute Optimizer'): {
        'link': 'https://docs.aws.amazon.com/compute-optimizer/',
        'text': 'AWS Compute Optimizer 문서'
    },
    ('aws-samples', 'database', '데이터베이스', 'RDS', 'NLB'): {
        'link': 'https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html',
        'text': 'AWS RDS 보안 모범 사례'
    },
    ('aws-samples', 'architecture', '아키텍처', 'Architecture'): {
        'link': 'https://aws.amazon.com/architecture/well-architected/',
        'text': 'AWS Well-Architected Framework'
    },
    ('aws-samples', 'datadog', 'Datadog', 'SIEM'): {
        'link': 'https://docs.datadoghq.com/security/',
        'text': 'Datadog Security Monitoring'
    },
    ('aws-samples', 'control-tower', 'Control Tower', 'SCP'): {
        'link': 'https://docs.aws.amazon.com/controltower/',
        'text': 'AWS Control Tower 문서'
    },
    
    # Kubernetes 관련
    ('kubernetes/examples', 'network-policy', 'Network Policy'): {
        'link': 'https://kubernetes.io/docs/concepts/services-networking/network-policies/',
        'text': 'Kubernetes Network Policy 문서'
    },
    ('kubernetes/examples', 'external-secrets', 'External Secrets', 'Secrets Manager'): {
        'link': 'https://github.com/external-secrets/external-secrets',
        'text': 'External Secrets Operator'
    },
    ('kubernetes/examples', 'kyverno', 'Kyverno', 'admission'): {
        'link': 'https://kyverno.io/docs/',
        'text': 'Kyverno 공식 문서'
    },
    ('kubernetes/examples', 'kubelet', 'kubelet API'): {
        'link': 'https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/',
        'text': 'Kubernetes Kubelet 문서'
    },
    ('kubernetes/examples', 'audit', 'Audit', 'credential'): {
        'link': 'https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/',
        'text': 'Kubernetes Audit 문서'
    },
    ('kubernetes/examples', 'certificate', 'Certificate', 'CSR'): {
        'link': 'https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/',
        'text': 'Kubernetes Certificate Signing Requests 문서'
    },
    ('kubernetes/examples', 'eks', 'EKS', 'anonymous'): {
        'link': 'https://docs.aws.amazon.com/eks/latest/userguide/',
        'text': 'Amazon EKS 문서'
    },
    ('kubernetes/examples', 'deprecated', 'Deprecated'): {
        'link': 'https://kubernetes.io/docs/reference/using-api/deprecation-guide/',
        'text': 'Kubernetes Deprecation Guide'
    },
    ('kubernetes/examples', 'karpenter', 'Karpenter', 'NodePool', 'PDB'): {
        'link': 'https://karpenter.sh/',
        'text': 'Karpenter 공식 문서'
    },
    ('kubernetes/examples', 'prometheus', 'Prometheus', 'Alert'): {
        'link': 'https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/',
        'text': 'Prometheus Alert Rules 문서'
    },
    ('kubernetes/examples', 'datadog', 'Datadog'): {
        'link': 'https://docs.datadoghq.com/',
        'text': 'Datadog 공식 문서'
    },
}

def find_context(content: str, match_pos: int, context_size: int = 300) -> str:
    """매칭된 위치 주변의 컨텍스트 추출"""
    start = max(0, match_pos - context_size)
    end = min(len(content), match_pos + context_size)
    return content[start:end].lower()

def get_replacement(link_type: str, context: str) -> Optional[Dict]:
    """컨텍스트에 맞는 링크 교체 정보 반환"""
    for (pattern, *keywords), replacement in LINK_REPLACEMENTS.items():
        if pattern in link_type.lower():
            if any(keyword.lower() in context for keyword in keywords):
                return replacement
    return None

def fix_links_in_file(file_path: Path) -> bool:
    """파일 내 링크 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # 패턴 1: GitHub 예제 저장소 링크
        patterns = [
            (r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/([^\)]+)\)를 참조하세요\.',
             r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github.com/\1\)를 참조하세요.'),
            (r'> \*\*참고\*\*: 관련 예제는 \[GitHub 예제 저장소\]\(https://github\.com/([^\)]+)\)를 참조하세요\.',
             r'> \*\*참고\*\*: 관련 예제는 \[GitHub 예제 저장소\]\(https://github.com/\1\)를 참조하세요.'),
        ]
        
        for pattern, replacement in patterns:
            def replace_with_context(match):
                full_match = match.group(0)
                link_type = match.group(1)
                match_pos = match.start()
                
                # 컨텍스트 추출
                context = find_context(content, match_pos)
                
                # 교체 정보 찾기
                replacement_info = get_replacement(link_type, context)
                
                if replacement_info:
                    # 링크 교체
                    new_text = replacement_info['text']
                    new_link = replacement_info['link']
                    return f'> **참고**: {new_text} 관련 내용은 [{new_text}]({new_link})를 참조하세요.'
                
                # 기본 교체 (kubernetes/examples는 적절할 수 있음)
                if 'kubernetes/examples' in link_type:
                    if any(kw in context for kw in ['network', 'policy', 'pod', 'service', 'deployment']):
                        return full_match  # Kubernetes 리소스는 적절
                    else:
                        # 부적절한 경우
                        if 'prometheus' in context:
                            return '> **참고**: Prometheus 관련 내용은 [Prometheus 공식 문서](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)를 참조하세요.'
                        elif 'datadog' in context:
                            return '> **참고**: Datadog 관련 내용은 [Datadog 공식 문서](https://docs.datadoghq.com/)를 참조하세요.'
                        elif 'karpenter' in context:
                            return '> **참고**: Karpenter 관련 내용은 [Karpenter 공식 문서](https://karpenter.sh/)를 참조하세요.'
                
                # aws-samples 기본 교체
                if 'aws-samples' in link_type:
                    if 'cost' in context or '비용' in context:
                        return '> **참고**: AWS Cost Management 관련 내용은 [AWS Cost Explorer API 문서](https://docs.aws.amazon.com/aws-cost-management/latest/APIReference/Welcome.html)를 참조하세요.'
                    elif 'guardduty' in context:
                        return '> **참고**: AWS GuardDuty 관련 내용은 [AWS GuardDuty 문서](https://docs.aws.amazon.com/guardduty/)를 참조하세요.'
                    elif 'security' in context:
                        return '> **참고**: AWS 보안 관련 내용은 [AWS Security 문서](https://docs.aws.amazon.com/security/)를 참조하세요.'
                    elif 'database' in context or 'rds' in context or '데이터베이스' in context:
                        return '> **참고**: AWS 데이터베이스 보안 관련 내용은 [AWS RDS 보안 모범 사례](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.html)를 참조하세요.'
                    else:
                        return '> **참고**: AWS 관련 내용은 [AWS 공식 문서](https://docs.aws.amazon.com/)를 참조하세요.'
                
                return full_match
            
            new_content = re.sub(pattern, replace_with_context, content, flags=re.MULTILINE)
            if new_content != content:
                content = new_content
                modified = True
        
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """메인 함수"""
    posts_dir = Path(__file__).parent.parent / '_posts'
    
    if not posts_dir.exists():
        print(f"Posts directory not found: {posts_dir}")
        return
    
    processed = 0
    updated = 0
    
    for post_file in sorted(posts_dir.glob('*.md')):
        processed += 1
        if fix_links_in_file(post_file):
            updated += 1
            print(f"Updated: {post_file.name}")
    
    print(f"\nProcessed: {processed} files")
    print(f"Updated: {updated} files")

if __name__ == '__main__':
    main()
