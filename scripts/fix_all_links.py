#!/usr/bin/env python3
"""
모든 포스트 파일의 부적절한 링크를 적절한 링크로 교체하는 스크립트
"""
import re
from pathlib import Path
from typing import Dict, Tuple

# 링크 매핑: (패턴, 코드_타입_키워드) -> (새_링크, 새_텍스트)
LINK_REPLACEMENTS = [
    # GitHub Actions/Dependabot 관련
    (r'github\.com/kubernetes/examples.*dependabot|dependabot.*github\.com/kubernetes/examples',
     r'[GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot)'),
    
    # GitHub Actions 워크플로우
    (r'github\.com/kubernetes/examples.*workflows|\.github/workflows.*github\.com/kubernetes/examples',
     r'[GitHub Actions 문서](https://docs.github.com/en/actions)'),
    
    # CodeQL 관련
    (r'github\.com/kubernetes/examples.*codeql|codeql.*github\.com/kubernetes/examples',
     r'[GitHub CodeQL 문서](https://docs.github.com/en/code-security/code-scanning/using-codeql-code-scanning-with-your-ci)'),
    
    # AWS WAF/CloudFront
    (r'github\.com/aws-samples.*waf|waf.*github\.com/aws-samples|cloudfront.*github\.com/aws-samples',
     r'[AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)'),
    
    # 자동차 보안 GitHub Actions
    (r'github\.com/kubernetes/examples.*automotive|automotive.*github\.com/kubernetes/examples',
     r'[GitHub Actions 보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)'),
    
    # Falco 관련
    (r'github\.com/kubernetes/examples.*falco|falco.*github\.com/kubernetes/examples',
     r'[Falco 공식 저장소](https://github.com/falcosecurity/falco)'),
    
    # SBOM 관련
    (r'github\.com/kubernetes/examples.*sbom|sbom.*github\.com/kubernetes/examples',
     r'[CycloneDX](https://github.com/CycloneDX/cyclonedx-cli) 및 [SPDX](https://github.com/spdx/tools)'),
]

def find_code_context(content: str, match_pos: int, context_size: int = 200) -> str:
    """매칭된 위치 주변의 코드 컨텍스트 추출"""
    start = max(0, match_pos - context_size)
    end = min(len(content), match_pos + context_size)
    return content[start:end].lower()

def fix_links_in_file(file_path: Path) -> bool:
    """파일 내 링크 수정"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        modified = False
        
        # 패턴 1: GitHub Actions/Dependabot 워크플로우
        if '.github/workflows' in content or 'dependabot' in content.lower():
            # Dependabot 설정
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?dependabot',
                r'> **참고**: Dependabot 설정 관련 자세한 내용은 [GitHub Dependabot 문서](https://docs.github.com/en/code-security/dependabot) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
            
            # GitHub Actions 워크플로우
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?\.github/workflows',
                r'> **참고**: GitHub Actions 워크플로우 관련 내용은 [GitHub Actions 문서](https://docs.github.com/en/actions) 및 [보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)를 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
            
            # CodeQL
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?codeql',
                r'> **참고**: CodeQL 분석 설정 관련 내용은 [GitHub CodeQL 문서](https://docs.github.com/en/code-security/code-scanning/using-codeql-code-scanning-with-your-ci) 및 [CodeQL Action](https://github.com/github/codeql-action)을 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        # 패턴 2: AWS WAF/CloudFront
        if 'waf' in content.lower() or 'cloudfront' in content.lower():
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/aws-samples\).*?(?:waf|cloudfront)',
                r'> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        # 패턴 3: 자동차 보안
        if 'automotive' in content.lower() or '자동차' in content:
            # SAST/보안 스캔
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?(?:sast|보안|security)',
                r'> **참고**: 자동차 보안 스캔 관련 내용은 [GitHub Actions 보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions) 및 [SonarQube](https://github.com/SonarSource/sonarqube)를 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
            
            # Falco
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?falco',
                r'> **참고**: Falco 런타임 보안 모니터링 관련 내용은 [Falco 공식 저장소](https://github.com/falcosecurity/falco)를 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
            
            # SBOM
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?sbom',
                r'> **참고**: SBOM 생성 관련 내용은 [CycloneDX](https://github.com/CycloneDX/cyclonedx-cli) 및 [SPDX](https://github.com/spdx/tools)를 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        # 패턴 4: 블록체인 보안
        if 'blockchain' in content.lower() or '블록체인' in content or 'solidity' in content.lower():
            content = re.sub(
                r'> \*\*코드 예시\*\*: 전체 코드는 \[GitHub 예제 저장소\]\(https://github\.com/kubernetes/examples\).*?(?:security-audit|securify)',
                r'> **참고**: 블록체인 보안 감사 관련 내용은 [Slither](https://github.com/crytic/slither), [Mythril](https://github.com/ConsenSys/mythril) 및 [Securify](https://github.com/eth-sri/securify2)를 참조하세요.',
                content,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        if content != original_content:
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
