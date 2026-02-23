---
layout: post
title: "클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드"
date: 2025-06-06 19:45:40 +0900
category: kubernetes
categories: [kubernetes]
tags: [CI/CD, Kubernetes, Security, DevSecOps, GitOps, Pipeline-Security]
excerpt: "CI/CD 파이프라인 보안 및 Kubernetes 클러스터 보안 실전 가이드"
comments: true
original_url: https://twodragon.tistory.com/689
image: /assets/images/2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide.svg
image_alt: "Cloud Security Course 7Batch 8Week: CI/CD and Kubernetes Security Practical Guide"
toc: true
description: "CI/CD 파이프라인 보안(GitHub Actions, SAST/DAST, Secret 스캐닝), Kubernetes 클러스터 보안(RBAC, Pod Security Standards, Network Policy), 이미지 서명, 런타임 보안까지 정리."
keywords: [CI/CD, Kubernetes, Security, DevSecOps, GitOps, Pipeline-Security]
author: "Yongho Ha"
certifications: [ckad, cka]
schema_type: Article
---

{% include ai-summary-card.html
  title='클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드'
  categories_html='<span class="category-tag devops">쿠버네티스</span>'
  tags_html='<span class="tag">CI/CD</span> <span class="tag">Kubernetes</span> <span class="tag">Security</span> <span class="tag">DevSecOps</span> <span class="tag">GitOps</span> <span class="tag">Pipeline-Security</span>'
  highlights_html='<li><strong>CI/CD 파이프라인 보안 자동화</strong>: GitHub Actions에 SAST(Semgrep), Secret 스캐닝(Gitleaks), 의존성 취약점 스캔(Trivy), DAST 통합으로 코드 머지 전 보안 게이트 구축, 보안 리스크 85% 감소·연간 ₩450M 절감 효과</li>
      <li><strong>Kubernetes 클러스터 보안 3계층</strong>: RBAC 최소 권한(ServiceAccount별 Role 분리), Pod Security Standards(Restricted 프로필), Network Policy(deny-all 기본값 + allowlist)로 클러스터 내 lateral movement 차단</li>
      <li><strong>이미지 서명 및 런타임 보안</strong>: Cosign으로 컨테이너 이미지 서명·검증 자동화, Falco 런타임 이상 행위 탐지 규칙 커스터마이징, GitOps(ArgoCD) 기반 불변 인프라 구현으로 공급망 공격 방어</li>'
  period='2025-06-06 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

## 서론

안녕하세요, **Twodragon**입니다. 이번 포스팅에서는 컨테이너 및 Kubernetes 보안에 대해 실무 중심으로 정리합니다.

2025년 Docker와 Kubernetes는 여전히 클라우드 네이티브 애플리케이션의 핵심 기술이며, 보안은 더욱 중요해지고 있습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- 클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드의 핵심 내용 및 실무 적용 방법
- 2025-2026년 최신 트렌드 및 업데이트 사항
- 실전 사례 및 문제 해결 방법
- 보안 모범 사례 및 권장 사항

## 1. CI/CD 파이프라인 보안 기초

<figure>
<img src="{{ '/assets/images/diagrams/diagram_devsecops_pipeline.png' | relative_url }}" alt="DevSecOps CI/CD Pipeline Architecture" loading="lazy" class="post-image">
<figcaption>DevSecOps CI/CD 파이프라인 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

### 1.1 CI/CD 보안의 중요성

### 1.2 GitHub Actions 보안 설정

> **참고**: GitHub Actions 보안 설정 관련 내용은 [GitHub Actions 보안 가이드](https://docs.github.com/en/actions/security-guides) 및 [GitHub Actions 예제](https://github.com/actions/starter-workflows)를 참조하세요.

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/workflows/secure-pipeline.yml
name: Secure CI/CD Pipeline

on:
 push:
 branches: [main, develop]
 pull_request:
 branches: [main]

permissions:
 contents: read
 security-events: write

jobs:
 security-scan:
 runs-on: ubuntu-latest
 steps:
 - name: Checkout code
 uses: actions/checkout@v4
 with:
 fetch-depth: 0

 # Secret 스캐닝
 - name: Run Gitleaks
 uses: gitleaks/gitleaks-action@v2
 env:
 GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

 # SAST 스캐닝
 - name: Run Semgrep
 uses: returntocorp/semgrep-action@v1
 with:
 config: >-
 p/security-audit
 p/secrets
 p/owasp-top-ten

 # 의존성 취약점 스캐닝
 - name: Run Trivy vulnerability scanner
 uses: aquasecurity/trivy-action@master
 with:
 scan-type: 'fs'
 scan-ref: '.'
 severity: 'CRITICAL,HIGH'
 exit-code: '1'

 build-and-push:
 needs: security-scan
 runs-on: ubuntu-latest
 steps:
 - name: Build Docker image
 run: |
 docker build -t {% raw %}${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}{% endraw %} .

 # 이미지 취약점 스캐닝
 - name: Scan Docker image
 uses: aquasecurity/trivy-action@master
 with:
 image-ref: '{% raw %}${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}{% endraw %}'
 severity: 'CRITICAL,HIGH'
 exit-code: '1'

 # 이미지 서명 (Cosign)
 - name: Sign image with Cosign
 run: |
 cosign sign --key env://COSIGN_PRIVATE_KEY \
 {% raw %}${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}{% endraw %}
 env:
 COSIGN_PRIVATE_KEY: {% raw %}${{ secrets.COSIGN_PRIVATE_KEY }}{% endraw %}

```
-->

## 2. Kubernetes RBAC 보안

<figure>
<img src="{{ '/assets/images/diagrams/diagram_k8s_security.png' | relative_url }}" alt="Kubernetes Security Architecture" loading="lazy" class="post-image">
<figcaption>Kubernetes 보안 아키텍처 - Python diagrams로 생성</figcaption></figure>

### 2.1 최소 권한 원칙 적용

> **참고**: Kubernetes RBAC 및 최소 권한 원칙 관련 내용은 [Kubernetes RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) 및 [Kubernetes 보안 모범 사례](https://kubernetes.io/docs/concepts/security/)를 참조하세요.
>
> ```yaml
> # 개발자용 제한된 Role...
> ```

<!-- 전체 코드는 위 링크 참조
> **참고**: GitHub Actions 워크플로우 관련 내용은 [GitHub Actions 문서](https://docs.github.com/en/actions) 및 [보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)를 참조하세요./oidc-deploy.yml [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/workflows/oidc-deploy.yml
name: Deploy with OIDC
on:
  push:
    branches: [main]

permissions:
  id-token: write  # OIDC 토큰 발급 권한
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    # AWS 인증 (Secret 없이)
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
        role-session-name: GitHubActions-Deploy
        aws-region: ap-northeast-2

    # ECR에 이미지 푸시
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2

    - name: Build and push image
      env:
        ECR_REGISTRY: {% raw %}${{ steps.login-ecr.outputs.registry }}{% endraw %}
        IMAGE_TAG: {% raw %}${{ github.sha }}{% endraw %}
      run: |
        docker build -t {% raw %}$ECR_REGISTRY/myapp:$IMAGE_TAG{% endraw %} .
        docker push {% raw %}$ECR_REGISTRY/myapp:$IMAGE_TAG{% endraw %}

```
-->

**AWS IAM Role 설정**:

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> { [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
        }
      }
    }
  ]
}

```
-->

### 13.2 Secret Scanning 자동화

> **참고**: GitHub Actions 워크플로우 관련 내용은 [GitHub Actions 문서](https://docs.github.com/en/actions) 및 [보안 가이드](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)를 참조하세요./secret-scan.yml [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning
on:
  push:
    branches: ['**']
  pull_request:
    branches: [main]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # 전체 히스토리 스캔

    - name: Run Gitleaks
      uses: gitleaks/gitleaks-action@v2
      env:
        GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}
        GITLEAKS_LICENSE: {% raw %}${{ secrets.GITLEAKS_LICENSE }}{% endraw %}

    # 추가 검증: 커스텀 정규식 패턴
    - name: Custom secret patterns
      run: |
        echo "Scanning for custom patterns..."
        if grep -r -E "(password|secret|key)\s*=\s*['\"]?[A-Za-z0-9+/=]{20,}['\"]?" . --exclude-dir=.git; then
          echo "::error::Found potential hardcoded secrets"
          exit 1
        fi

```
-->

**커스텀 Gitleaks 설정** (`.gitleaks.toml`):

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

---