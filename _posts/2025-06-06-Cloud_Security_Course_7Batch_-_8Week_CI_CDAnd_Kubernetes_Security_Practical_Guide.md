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

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag devops">Kubernetes</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">CI/CD</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">Security</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">GitOps</span>
      <span class="tag">Pipeline-Security</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>CI/CD 파이프라인 보안</strong>: GitHub Actions 보안 설정(permissions 최소화, Secret 관리), SAST/DAST 통합(Semgrep, SonarQube, Gitleaks, Trivy, OWASP ZAP), Secret 스캐닝, 의존성 취약점 스캔</li>
      <li><strong>Kubernetes 클러스터 보안</strong>: RBAC(Role, RoleBinding, ClusterRole, ClusterRoleBinding), Pod Security Standards(Restricted/Baseline/Privileged), Network Policy(트래픽 제어, 네임스페이스 격리), Service Account 최소 권한</li>
      <li><strong>이미지 서명 및 Secret 관리</strong>: Cosign 이미지 서명, Kubernetes Secrets 관리, External Secrets Operator, Sealed Secrets, Vault 통합</li>
      <li><strong>런타임 보안</strong>: Kyverno 정책 엔진(Admission Control, Policy as Code), Falco 이상 행위 탐지, GitOps 보안 모범 사례(ArgoCD, Flux), 실무 적용 체크리스트</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Kubernetes, GitHub Actions, Kyverno, Falco, Cosign</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">클라우드 보안 전문가, DevOps 엔지니어, 보안 담당자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

<img src="{{ '/assets/images/2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide_image.png' | relative_url }}" alt="Cloud Security Course 7Batch 8Week: CI/CD and Kubernetes Security Practical Guide" loading="lazy" class="post-image">

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
```yaml
# 개발자용 제한된 Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
 namespace: development
 name: developer-role
rules:
# Pod 읽기 및 로그 확인만 허용
- apiGroups: [""]
 resources: ["pods", "pods/log"]
 verbs: ["get", "list", "watch"]
# ConfigMap과 Secret 읽기만 허용
- apiGroups: [""]
 resources: ["configmaps", "secrets"]
 verbs: ["get", "list"]
# Deployment 상태 확인만 허용
- apiGroups: ["apps"]
 resources: ["deployments"]
 verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
 name: developer-binding
 namespace: development
subjects:
- kind: Group
 name: developers
 apiGroup: rbac.authorization.k8s.io
roleRef:
 kind: Role
 name: developer-role
 apiGroup: rbac.authorization.k8s.io

```
-->

### 2.2 ServiceAccount 보안

> **참고**: Kubernetes ServiceAccount 보안 관련 내용은 [Kubernetes ServiceAccount 문서](https://kubernetes.io/docs/concepts/security/service-accounts/) 및 [Kubernetes RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)를 참조하세요.
>
> ```yaml
> # 전용 ServiceAccount 생성...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# 전용 ServiceAccount 생성
apiVersion: v1
kind: ServiceAccount
metadata:
 name: app-service-account
 namespace: production
automountServiceAccountToken: false # 자동 마운트 비활성화
---
apiVersion: apps/v1
kind: Deployment
metadata:
 name: secure-app
spec:
 template:
 spec:
 serviceAccountName: app-service-account
 automountServiceAccountToken: false
 containers:
 - name: app
 image: myapp:latest
 securityContext:
 runAsNonRoot: true
 runAsUser: 1000
 readOnlyRootFilesystem: true
 allowPrivilegeEscalation: false

```
-->

## 3. Pod Security Standards (PSS)

### 3.1 Namespace 레벨 보안 정책

> **참고**: Pod Security Standards 관련 내용은 [Kubernetes Pod Security Standards 문서](https://kubernetes.io/docs/concepts/security/pod-security-standards/) 및 [Kubernetes 예제](https://github.com/kubernetes/examples)를 참조하세요.

```yaml
# Restricted 정책이 적용된 Namespace
apiVersion: v1
kind: Namespace
metadata:
 name: secure-namespace
 labels:
 pod-security.kubernetes.io/enforce: restricted
 pod-security.kubernetes.io/audit: restricted
 pod-security.kubernetes.io/warn: restricted
```

### 3.2 보안 컨텍스트 모범 사례

> **참고**: Kubernetes Security Context 관련 내용은 [Kubernetes Security Context 문서](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) 및 [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)를 참조하세요.
>
> ```yaml
> apiVersion: apps/v1...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
 name: hardened-deployment
spec:
 replicas: 3
 selector:
 matchLabels:
 app: hardened-app
 template:
 metadata:
 labels:
 app: hardened-app
 spec:
 securityContext:
 runAsNonRoot: true
 runAsUser: 65534
 runAsGroup: 65534
 fsGroup: 65534
 seccompProfile:
 type: RuntimeDefault
 containers:
 - name: app
 image: myapp:v1.0.0@sha256:abc123... # Digest 고정
 securityContext:
 allowPrivilegeEscalation: false
 readOnlyRootFilesystem: true
 capabilities:
 drop:
 - ALL
 resources:
 limits:
 cpu: "500m"
 memory: "256Mi"
 requests:
 cpu: "100m"
 memory: "128Mi"
 volumeMounts:
 - name: tmp
 mountPath: /tmp
 - name: cache
 mountPath: /var/cache
 volumes:
 - name: tmp
 emptyDir: {}
 - name: cache
 emptyDir: {}

```
-->

## 4. Network Policy 구현

### 4.1 기본 거부 정책

> **참고**: Kubernetes Network Policy 관련 내용은 [Kubernetes Network Policy 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/) 및 [Network Policy 예제](https://github.com/kubernetes/examples)를 참조하세요.
>
> ```yaml
> # 모든 인그레스/이그레스 트래픽 차단 (기본)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 모든 인그레스/이그레스 트래픽 차단 (기본)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
 name: default-deny-all
 namespace: production
spec:
 podSelector: {}
 policyTypes:
 - Ingress
 - Egress

```
-->

### 4.2 필요한 트래픽만 허용

> **참고**: Kubernetes Network Policy 관련 내용은 [Kubernetes Network Policy 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/) 및 [Network Policy 예제](https://github.com/kubernetes/examples)를 참조하세요.
>
> ```yaml
> # Frontend -> Backend 통신만 허용...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Frontend -> Backend 통신만 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
 name: backend-policy
 namespace: production
spec:
 podSelector:
 matchLabels:
 app: backend
 policyTypes:
 - Ingress
 - Egress
 ingress:
 - from:
 - podSelector:
 matchLabels:
 app: frontend
 ports:
 - protocol: TCP
 port: 8080
 egress:
 - to:
 - podSelector:
 matchLabels:
 app: database
 ports:
 - protocol: TCP
 port: 5432
 # DNS 허용
 - to:
 - namespaceSelector: {}
 podSelector:
 matchLabels:
 k8s-app: kube-dns
 ports:
 - protocol: UDP
 port: 53

```
-->

## 5. Secret 관리

### 5.1 External Secrets Operator

> **참고**: External Secrets Operator 관련 내용은 [External Secrets Operator GitHub 저장소](https://github.com/external-secrets/external-secrets) 및 [External Secrets Operator 문서](https://external-secrets.io/latest/)를 참조하세요.
>
> ```yaml
> # AWS Secrets Manager와 연동...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# AWS Secrets Manager와 연동
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
 name: aws-secrets-manager
 namespace: production
spec:
 provider:
 aws:
 service: SecretsManager
 region: ap-northeast-2
 auth:
 jwt:
 serviceAccountRef:
 name: external-secrets-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
 name: database-credentials
 namespace: production
spec:
 refreshInterval: 1h
 secretStoreRef:
 name: aws-secrets-manager
 kind: SecretStore
 target:
 name: db-secret
 creationPolicy: Owner
 data:
 - secretKey: username
 remoteRef:
 key: prod/database
 property: username
 - secretKey: password
 remoteRef:
 key: prod/database
 property: password

```
-->

### 5.2 Sealed Secrets (GitOps 환경)

> **참고**: Sealed Secrets 관련 내용은 [Sealed Secrets GitHub 저장소](https://github.com/bitnami-labs/sealed-secrets) 및 [Sealed Secrets 문서](https://sealed-secrets.netlify.app/)를 참조하세요.

```bash
# Sealed Secrets 컨트롤러 설치
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Secret을 SealedSecret으로 암호화
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# Git에 안전하게 커밋 가능
git add sealed-secret.yaml
git commit -m "Add encrypted database credentials"
```

## 6. 이미지 보안

### 6.1 Admission Controller로 이미지 검증

> **참고**: Kyverno를 통한 이미지 검증 관련 내용은 [Kyverno GitHub 저장소](https://github.com/kyverno/kyverno) 및 [Kyverno 공식 문서](https://kyverno.io/docs/)를 참조하세요.
>
> ```yaml
> # Kyverno 정책: 서명된 이미지만 허용...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Kyverno 정책: 서명된 이미지만 허용
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
 name: verify-image-signature
spec:
 validationFailureAction: enforce
 background: false
 rules:
 - name: check-image-signature
 match:
 any:
 - resources:
 kinds:
 - Pod
 verifyImages:
 - imageReferences:
 - "myregistry.io/*"
 attestors:
 - entries:
 - keys:
 publicKeys: |
 -----BEGIN PUBLIC KEY-----
 MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
 -----END PUBLIC KEY-----

```
-->

### 6.2 취약점이 있는 이미지 차단

{% raw %}
> **참고**: Kyverno를 통한 취약점 이미지 차단 관련 내용은 [Kyverno GitHub 저장소](https://github.com/kyverno/kyverno) 및 [Kyverno 공식 문서](https://kyverno.io/docs/)를 참조하세요.
>
> ```yaml
> # Kyverno 정책: Critical 취약점 차단...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Kyverno 정책: Critical 취약점 차단
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
 name: block-vulnerable-images
spec:
 validationFailureAction: enforce
 rules:
 - name: check-vulnerabilities
 match:
 any:
 - resources:
 kinds:
 - Pod
 validate:
 message: "Images with CRITICAL vulnerabilities are not allowed"
 deny:
 conditions:
 any:
 - key: "{{ images.*.vulnerabilities[?severity=='CRITICAL'] | length(@) }}"
 operator: GreaterThan
 value: 0

```
-->
{% endraw %}

## 7. 런타임 보안

### 7.1 Falco 규칙 설정

> **참고**: Falco 런타임 보안 모니터링 관련 내용은 [Falco 공식 저장소](https://github.com/falcosecurity/falco) 및 [Falco 문서](https://falco.org/docs/)를 참조하세요.
>
> ```yaml
> # 의심스러운 활동 탐지 규칙...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 의심스러운 활동 탐지 규칙
- rule: Terminal shell in container
 desc: A shell was used as the entrypoint/exec point into a container
 condition: >
 spawned_process and container
 and shell_procs and proc.tty != 0
 and container_entrypoint
 and not user_expected_terminal_shell_in_container_conditions
 output: >
 A shell was spawned in a container with an attached terminal
 (user=%user.name container_id=%container.id container_name=%container.name
 shell=%proc.name parent=%proc.pname cmdline=%proc.cmdline)
 priority: NOTICE
 tags: [container, shell, mitre_execution]

- rule: Write below etc
 desc: an attempt to write to any file below /etc
 condition: write_etc_common
 output: "File below /etc opened for writing (user=%user.name command=%proc.cmdline file=%fd.name)"
 priority: ERROR
 tags: [filesystem, mitre_persistence]

```
-->

## 8. 2025년 Kubernetes 보안 업데이트

### 8.1 Kubernetes 1.32~1.35 주요 보안 기능

Kubernetes는 2024년 말 1.32 "Penelope"를 시작으로 2025년 12월 1.35 "Timbernetes"까지 보안 기능을 대폭 강화했습니다.

#### Fine-grained Kubelet API Authorization (KEP-2862)

kubelet API에 대한 세밀한 접근 제어가 가능해졌습니다.

> **참고**: Kubelet API 접근 제어 관련 내용은 [Kubernetes Kubelet 문서](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/) 및 [Kubernetes RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)를 참조하세요.
>
> ```yaml
> # RBAC을 통한 kubelet API 세밀한 제어...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# RBAC을 통한 kubelet API 세밀한 제어
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: kubelet-api-reader
rules:
# 특정 노드의 Pod 정보만 읽기 허용
- apiGroups: [""]
  resources: ["nodes/proxy"]
  verbs: ["get"]
  resourceNames: ["node-1", "node-2"]
# Pod 로그 접근 제한
- apiGroups: [""]
  resources: ["pods/log"]
  verbs: ["get"]
---
# kubelet 설정에서 Fine-grained 인가 활성화
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
featureGates:
  KubeletFineGrainedAuthz: true
authorization:
  mode: Webhook
  webhook:
    cacheAuthorizedTTL: 5m
    cacheUnauthorizedTTL: 30s

```
-->

**보안 이점:**
- 노드별, Pod별 kubelet API 접근 권한 세밀 제어
- 측면 이동(Lateral Movement) 공격 방지
- 침해 발생 시 피해 범위 최소화

#### Credential Tracking for Forensics

인증서 서명 기반 credential ID 생성으로 포렌식 기능이 강화되었습니다.

> **참고**: Kubernetes Audit 및 credential 추적 관련 내용은 [Kubernetes Audit 문서](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)를 참조하세요.
>
> ```yaml
> # Audit Policy에서 credential 추적 활성화...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# Audit Policy에서 credential 추적 활성화
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  users: ["system:serviceaccount:*:*"]
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
  omitStages:
  - RequestReceived
# 모든 인증 요청에 credential ID 로깅
- level: Metadata
  nonResourceURLs:
  - "/api/*"
  - "/apis/*"

```
-->

> **참고**: Kubernetes Audit 로그 분석 관련 내용은 [Kubernetes Audit 문서](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)를 참조하세요.
>
> ```bash
> # Audit 로그에서 credential 추적 예시...
> ```

<!-- 전체 코드는 위 링크 참조
```bash
# Audit 로그에서 credential 추적 예시
{
  "kind": "Event",
  "apiVersion": "audit.k8s.io/v1",
  "user": {
    "username": "system:serviceaccount:default:my-sa",
    "uid": "abc-123",
    "extra": {
      "authentication.kubernetes.io/credential-id": ["JTI=xyz789"]
    }
  }
}

```
-->

#### User Namespaces Support (Linux Kernel 6.3+)

User Namespaces는 컨테이너 내 root 사용자를 호스트의 비권한 사용자로 매핑하여 컨테이너 탈출 공격의 위험을 크게 감소시킵니다:

워크로드 격리를 크게 강화하는 User Namespaces가 정식 지원됩니다.

> **참고**: Kubernetes User Namespaces 관련 내용은 [Kubernetes User Namespaces 문서](https://kubernetes.io/docs/concepts/security/user-namespaces/) 및 [Kubernetes 예제](https://github.com/kubernetes/examples)를 참조하세요.
>
> ```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: isolated-pod
spec:
  hostUsers: false  # User Namespace 활성화 (핵심 설정)
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true

```
-->

**User Namespace 보안 효과:**
| 공격 시나리오 | 기존 | User Namespace 적용 |
|---------------|------|---------------------|
| 컨테이너 탈출 후 root 권한 | 호스트 root 획득 가능 | 비특권 사용자로 제한 |
| /proc, /sys 접근 | 민감 정보 노출 | 접근 권한 격리 |
| 다른 컨테이너 침해 | 가능 | 격리로 차단 |

#### Pod Certificates for mTLS (KEP-4317)

kubelet이 Pod용 인증서를 자동으로 요청하고 마운트합니다.

> **참고**: Kubernetes Pod Certificates 관련 내용은 [Kubernetes Certificate Signing Requests 문서](https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/) 및 [Kubernetes 예제](https://github.com/kubernetes/examples)를 참조하세요.
>
> ```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mtls-enabled-app
spec:
  containers:
  - name: app
    image: myapp:latest
    env:
    - name: TLS_CERT_PATH
      value: /etc/pod-certs/tls.crt
    - name: TLS_KEY_PATH
      value: /etc/pod-certs/tls.key
    - name: CA_CERT_PATH
      value: /etc/pod-certs/ca.crt
    volumeMounts:
    - name: pod-certs
      mountPath: /etc/pod-certs
      readOnly: true
  volumes:
  - name: pod-certs
    projected:
      defaultMode: 0400
      sources:
      - serviceAccountToken:
          path: token
          expirationSeconds: 3600
          audience: my-service
      - clusterTrustBundle:
          path: ca.crt
          name: cluster-trust-bundle
          optional: false

```
-->

**자동 인증서 Rotation:**
> **참고**: Kubernetes 인증서 관리 관련 내용은 [Kubernetes Certificate Signing Requests 문서](https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/)를 참조하세요.
>
> ```yaml
> # CertificateSigningRequest 자동 생성 및 갱신...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# CertificateSigningRequest 자동 생성 및 갱신
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: pod-cert-request
spec:
  signerName: kubernetes.io/kubelet-serving
  usages:
  - digital signature
  - key encipherment
  - server auth
  - client auth
  expirationSeconds: 86400  # 24시간 후 자동 갱신

```
-->

### 8.2 EKS 1.32 Anonymous Authentication 제한

Amazon EKS 1.32부터 익명 인증이 health check endpoint로 제한됩니다.

> **참고**: Amazon EKS 보안 관련 내용은 [Amazon EKS 문서](https://docs.aws.amazon.com/eks/latest/userguide/) 및 [EKS 보안 모범 사례](https://aws.github.io/aws-eks-best-practices/security/docs/)를 참조하세요.
>
> ```yaml
> # EKS 1.32+ 익명 접근 허용 endpoint...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# EKS 1.32+ 익명 접근 허용 endpoint
# /healthz, /readyz, /livez 만 익명 접근 가능

# 기존 익명 접근에 의존하던 서비스는 명시적 인증 필요
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: monitoring-access
subjects:
- kind: ServiceAccount
  name: monitoring-sa
  namespace: monitoring
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io

```
-->

### 8.3 Deprecated 기능 및 마이그레이션

> **참고**: Kubernetes Deprecated 기능 관련 내용은 [Kubernetes Deprecation Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)를 참조하세요.
>
> ```yaml
> # DEPRECATED: ServiceAccount의 enforce-mountable-secrets annotation...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# DEPRECATED: ServiceAccount의 enforce-mountable-secrets annotation
# 이 방식은 더 이상 권장되지 않음
apiVersion: v1
kind: ServiceAccount
metadata:
  name: legacy-sa
  annotations:
    kubernetes.io/enforce-mountable-secrets: "true"  # Deprecated

---
# 권장: Pod 레벨에서 직접 제어
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  serviceAccountName: my-sa
  automountServiceAccountToken: false  # 권장 방식
  containers:
  - name: app
    image: myapp:latest
    # 필요한 경우에만 명시적으로 token 마운트
    volumeMounts:
    - name: sa-token
      mountPath: /var/run/secrets/kubernetes.io/serviceaccount
      readOnly: true
  volumes:
  - name: sa-token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          expirationSeconds: 3600  # 단기 토큰 사용

```
-->

### 8.4 2025년 보안 강화 체크리스트

| 기능 | 버전 | 상태 | 적용 권장 |
|------|------|------|-----------|
| Fine-grained Kubelet AuthZ | 1.32+ | GA | 즉시 적용 |
| Credential Tracking | 1.32+ | GA | 포렌식 환경 필수 |
| User Namespaces | 1.32+ | GA | Linux 6.3+ 환경에서 적용 |
| Pod Certificates (mTLS) | 1.33+ | Beta | Zero Trust 환경 적용 |
| Anonymous Auth 제한 | EKS 1.32 | 적용됨 | EKS 사용자 필수 검토 |

## 9. CI/CD 보안 체크리스트

| 항목 | 설명 | 도구 |
|------|------|------|
| **Secret 스캐닝** | 코드 내 하드코딩된 시크릿 탐지 | Gitleaks, TruffleHog |
| **SAST** | 정적 애플리케이션 보안 테스트 | Semgrep, SonarQube |
| **SCA** | 오픈소스 의존성 취약점 스캔 | Trivy, Snyk |
| **컨테이너 스캔** | 이미지 취약점 스캔 | Trivy, Clair |
| **IaC 스캐닝** | 인프라 코드 보안 검사 | Checkov, KICS |
| **DAST** | 동적 애플리케이션 보안 테스트 | OWASP ZAP |
| **이미지 서명** | 빌드 아티팩트 무결성 보장 | Cosign, Notary |

## 10. 실무 적용 체크리스트

### CI/CD 파이프라인 보안

- [ ] GitHub Actions workflows에서 최소 권한(permissions) 설정 적용
- [ ] Secret 스캐닝 도구(Gitleaks, TruffleHog) CI 파이프라인에 통합
- [ ] SAST 도구(Semgrep, SonarQube) PR 검사에 적용
- [ ] 컨테이너 이미지 스캔(Trivy) 빌드 단계에 통합
- [ ] IaC 스캐닝(Checkov) Terraform/Kubernetes 매니페스트에 적용

### Kubernetes 클러스터 보안

- [ ] RBAC 정책 최소 권한 원칙으로 설정
- [ ] Pod Security Standards(Restricted) 프로덕션 네임스페이스에 적용
- [ ] Network Policy로 기본 거부 정책 설정
- [ ] ServiceAccount 자동 마운트 비활성화
- [ ] User Namespaces 활성화 (Linux 6.3+ 환경)

### Secret 관리

- [ ] External Secrets Operator 또는 Sealed Secrets 도입
- [ ] 하드코딩된 시크릿 코드에서 제거
- [ ] Secret 로테이션 자동화 설정

### 런타임 보안

- [ ] Falco 런타임 모니터링 배포
- [ ] Kyverno/OPA Gatekeeper 정책 엔진 적용
- [ ] 이미지 서명(Cosign) 및 검증 정책 설정

## 11. Executive Summary (경영진 요약)

### 11.1 CI/CD 및 Kubernetes 보안의 비즈니스 가치

**핵심 메시지**: DevSecOps 보안 자동화는 비용 절감과 리스크 관리를 동시에 달성합니다.

#### ROI 분석

| 영역 | 투자 전 | 투자 후 | 개선 효과 |
|------|---------|---------|-----------|
| **보안 사고 대응 시간** | 평균 72시간 | 평균 4시간 | 94% 감소 |
| **취약점 탐지 주기** | 월 1회 | 실시간 | 지속적 모니터링 |
| **배포 롤백률** | 15% | 3% | 80% 감소 |
| **컴플라이언스 감사 비용** | 연 ₩50M | 연 ₩15M | 70% 절감 |

#### 비즈니스 리스크 완화

**공급망 공격(Supply Chain Attack) 방어**:
- CI/CD 파이프라인 보안으로 악의적 코드 삽입 차단
- 이미지 서명 및 검증으로 무결성 보장
- 의존성 취약점 스캔으로 알려진 위협 사전 제거

**컴플라이언스 자동화**:
- ISMS-P, ISO 27001, PCI DSS 요구사항 자동 충족
- 감사 증적 자동 수집 및 보고서 생성
- 정책 위반 실시간 탐지 및 차단

**비즈니스 연속성 보장**:
- Zero-downtime 배포로 서비스 중단 최소화
- 자동 롤백으로 장애 복구 시간 단축
- 다중 리전 배포로 재해 복구 능력 확보

### 11.2 2025년 보안 투자 우선순위

| 우선순위 | 투자 영역 | 예상 ROI | 구현 기간 |
|----------|-----------|----------|-----------|
| **1** | CI/CD 파이프라인 보안 자동화 | 300% | 1-2개월 |
| **2** | Kubernetes RBAC 및 Network Policy | 250% | 2-3개월 |
| **3** | Secret 관리 자동화 (External Secrets) | 200% | 1개월 |
| **4** | 런타임 보안 모니터링 (Falco) | 400% | 2개월 |
| **5** | 이미지 서명 및 검증 (Cosign) | 150% | 1개월 |

**예산 배분 권장**:
- 보안 도구 라이선스: 30%
- 교육 및 트레이닝: 20%
- 구현 및 통합: 30%
- 운영 및 유지보수: 20%

## 12. MITRE ATT&CK Framework Mapping

### 12.1 CI/CD 공격 기법 매핑

#### T1195.002 - Supply Chain Compromise: Software Supply Chain

**공격 시나리오**:
공격자가 CI/CD 파이프라인에 악의적 코드를 삽입하여 프로덕션 환경에 배포합니다.

**실제 사례**: SolarWinds 공격 (2020), CodeCov 침해 (2021)

**방어 대책**:

```yaml
# GitHub Actions: 써드파티 액션 SHA 고정
name: Secure Pipeline
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab  # v3.5.2 (SHA 고정)

    # 써드파티 액션 사용 전 검증
    - name: Verify action signature
      run: |
        gh api /repos/actions/checkout/commits/8e5e7e5ab8b370d6c329ec480221332ada57f0ab \
          --jq '.sha' | grep -q 8e5e7e5ab8b370d6c329ec480221332ada57f0ab
```

**탐지 쿼리 (Splunk)**:

```spl
index=github_audit action="workflows.completed"
| where workflow_run.conclusion="failure" AND workflow_run.name="security-scan"
| stats count by repository, actor, workflow_run.head_commit.message
```

#### T1072 - Software Deployment Tools

**공격 시나리오**:
공격자가 Kubernetes API 서버 또는 CI/CD 도구의 인증 정보를 탈취하여 악의적 워크로드를 배포합니다.

**방어 대책**:

```yaml
# Kubernetes Audit Policy: 배포 활동 감시
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  verbs: ["create", "update", "patch"]
  resources:
  - group: "apps"
    resources: ["deployments", "daemonsets", "statefulsets"]
  - group: ""
    resources: ["pods"]
  omitStages:
  - RequestReceived
```

**탐지 쿼리 (AWS CloudWatch Insights)**:

```
fields @timestamp, user.username, requestURI, objectRef.name
| filter verb in ["create", "update", "patch"]
| filter objectRef.resource in ["deployments", "pods"]
| filter user.username not in ["system:serviceaccount:kube-system:*"]
| stats count() by user.username, objectRef.namespace
```

#### T1610 - Deploy Container

**공격 시나리오**:
공격자가 특권 컨테이너를 배포하여 호스트 시스템을 침해합니다.

**방어 대책**:

```yaml
# Kyverno Policy: 특권 컨테이너 차단
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: disallow-privileged-containers
spec:
  validationFailureAction: enforce
  rules:
  - name: check-privileged
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Privileged containers are not allowed"
      pattern:
        spec:
          containers:
          - =(securityContext):
              =(privileged): false
```

**탐지 쿼리 (Falco)**:

```yaml
- rule: Launch Privileged Container
  desc: Detect the initial process started in a privileged container
  condition: >
    container_started and container.privileged=true
  output: >
    Privileged container started (user=%user.name command=%proc.cmdline
    container_id=%container.id container_name=%container.name image=%container.image.repository)
  priority: WARNING
  tags: [container, cis, mitre_execution, mitre_privilege_escalation]
```

### 12.2 Kubernetes 공격 기법 매핑

#### T1078.004 - Valid Accounts: Cloud Accounts

**공격 시나리오**:
공격자가 유출된 ServiceAccount 토큰을 사용하여 클러스터에 접근합니다.

**방어 대책**:

```yaml
# ServiceAccount 토큰 자동 마운트 비활성화
apiVersion: v1
kind: ServiceAccount
metadata:
  name: secure-app-sa
  namespace: production
automountServiceAccountToken: false
---
# Pod에서 필요시에만 단기 토큰 사용
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
spec:
  serviceAccountName: secure-app-sa
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: token
      mountPath: /var/run/secrets/kubernetes.io/serviceaccount
  volumes:
  - name: token
    projected:
      sources:
      - serviceAccountToken:
          path: token
          expirationSeconds: 3600  # 1시간 후 만료
          audience: api
```

**탐지 쿼리 (Kubernetes Audit Log)**:

```
fields @timestamp, user.username, sourceIPs, responseStatus.code
| filter verb == "get" and objectRef.resource == "secrets"
| filter user.username like /system:serviceaccount:*/
| filter sourceIPs.0 not like /10.0.*/  # 내부 IP가 아닌 경우
| stats count() by user.username, sourceIPs.0
```

## 13. CI/CD 파이프라인 보안 강화 (Advanced)

### 13.1 GitHub Actions OIDC Federation

Secret 없이 AWS, GCP, Azure 리소스에 안전하게 접근합니다.

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

**AWS IAM Role 설정**:

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

### 13.2 Secret Scanning 자동화

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

**커스텀 Gitleaks 설정** (`.gitleaks.toml`):

```toml
title = "Custom Gitleaks Configuration"

[[rules]]
description = "AWS Access Key ID"
regex = '''AKIA[0-9A-Z]{16}'''
tags = ["aws", "credentials"]

[[rules]]
description = "Generic API Key"
regex = '''(?i)(api[_-]?key|apikey|api[_-]?secret)\s*[:=]\s*['"]?[a-zA-Z0-9]{32,}['"]?'''
tags = ["api", "key"]

[[rules]]
description = "Private Key"
regex = '''-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----'''
tags = ["private", "key"]

[allowlist]
paths = [
  '''^\.git/''',
  '''node_modules/''',
  '''vendor/'''
]
```

### 13.3 SAST/DAST 통합

```yaml
# .github/workflows/sast-dast.yml
name: SAST and DAST
on:
  pull_request:
    branches: [main]

jobs:
  sast:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    # Semgrep SAST
    - name: Run Semgrep
      uses: returntocorp/semgrep-action@v1
      with:
        config: >-
          p/security-audit
          p/secrets
          p/owasp-top-ten
          p/kubernetes
        generateSarif: true

    # SonarQube SAST
    - name: SonarQube Scan
      uses: sonarsource/sonarqube-scan-action@master
      env:
        SONAR_TOKEN: {% raw %}${{ secrets.SONAR_TOKEN }}{% endraw %}
        SONAR_HOST_URL: {% raw %}${{ secrets.SONAR_HOST_URL }}{% endraw %}

    # Upload SARIF results to GitHub Security
    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: semgrep.sarif

  dast:
    needs: sast
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    # OWASP ZAP DAST
    - name: ZAP Scan
      uses: zaproxy/action-baseline@v0.7.0
      with:
        target: 'https://staging.example.com'
        rules_file_name: '.zap/rules.tsv'
        cmd_options: '-a'
```

## 14. Kubernetes 런타임 보안 (Advanced)

### 14.1 Falco 고급 규칙

```yaml
# /etc/falco/falco_rules.local.yaml
- rule: Detect crypto mining
  desc: Detect cryptocurrency mining processes
  condition: >
    spawned_process and (
      proc.name in (xmrig, minerd, ccminer, ethminer) or
      proc.cmdline contains "stratum+tcp" or
      proc.cmdline contains "pool.minergate.com"
    )
  output: >
    Cryptocurrency mining detected (user=%user.name command=%proc.cmdline
    container=%container.name image=%container.image.repository)
  priority: CRITICAL
  tags: [process, mitre_execution, crypto_mining]

- rule: Detect reverse shell
  desc: Detect reverse shell connection attempts
  condition: >
    spawned_process and (
      (proc.name in (nc, ncat, netcat) and (proc.args contains "-e" or proc.args contains "-c")) or
      (proc.name = bash and proc.args contains "/dev/tcp/") or
      (proc.name = python and proc.args contains "socket")
    )
  output: >
    Reverse shell detected (user=%user.name command=%proc.cmdline
    container=%container.name image=%container.image.repository)
  priority: CRITICAL
  tags: [network, mitre_execution, reverse_shell]

- rule: Detect sensitive file access
  desc: Detect access to sensitive files in containers
  condition: >
    open_read and container and (
      fd.name in (/etc/shadow, /etc/passwd, /etc/sudoers, /root/.ssh/id_rsa) or
      fd.name pmatch (/root/.ssh/*)
    )
  output: >
    Sensitive file accessed (user=%user.name file=%fd.name
    command=%proc.cmdline container=%container.name)
  priority: WARNING
  tags: [filesystem, mitre_credential_access]

- rule: Kubernetes client tool in container
  desc: Detect kubectl or helm execution in container
  condition: >
    spawned_process and container and
    proc.name in (kubectl, helm, kubectx, kubens)
  output: >
    Kubernetes client tool executed in container (user=%user.name
    command=%proc.cmdline container=%container.name image=%container.image.repository)
  priority: NOTICE
  tags: [process, mitre_execution, k8s]
```

### 14.2 Admission Controller 심화

```yaml
# Kyverno: 이미지 출처 제한
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: restrict-image-registries
spec:
  validationFailureAction: enforce
  rules:
  - name: check-registry
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Images must come from approved registries"
      pattern:
        spec:
          containers:
          - image: "registry.example.com/* | ecr.example.com/* | gcr.io/my-project/*"
```

```yaml
# Kyverno: 리소스 쿼터 자동 적용
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-default-resources
spec:
  rules:
  - name: add-default-requests-limits
    match:
      any:
      - resources:
          kinds:
          - Pod
    mutate:
      patchStrategicMerge:
        spec:
          containers:
          - (name): "*"
            resources:
              requests:
                +(memory): "128Mi"
                +(cpu): "100m"
              limits:
                +(memory): "512Mi"
                +(cpu): "500m"
```

```yaml
# OPA Gatekeeper: 네임스페이스별 레이블 강제
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          properties:
            labels:
              type: array
              items: {type: string}
  targets:
  - target: admission.k8s.gatekeeper.sh
    rego: |
      package k8srequiredlabels
      violation[{"msg": msg, "details": {"missing_labels": missing}}] {
        provided := {label | input.review.object.metadata.labels[label]}
        required := {label | label := input.parameters.labels[_]}
        missing := required - provided
        count(missing) > 0
        msg := sprintf("you must provide labels: %v", [missing])
      }
---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Namespace"]
  parameters:
    labels: ["team", "cost-center", "environment"]
```

## 15. 위협 헌팅 쿼리 (Threat Hunting Queries)

### 15.1 CI/CD 로그 분석

**GitHub Actions 이상 행위 탐지**:

```spl
# Splunk Query: 비정상 시간대 워크플로우 실행
index=github_audit action="workflows.completed"
| eval hour=strftime(_time, "%H")
| where hour >= 2 AND hour <= 6  # 새벽 2-6시
| stats count by repository, actor, workflow_name
| where count > 5
| sort -count
```

**Jenkins 비인가 접근 탐지**:

```spl
# Splunk Query: 실패한 인증 시도 후 성공
index=jenkins sourcetype=jenkins_audit
| transaction user maxspan=5m
| search action="login_failed" AND action="login_success"
| stats count by user, src_ip
```

### 15.2 Kubernetes Audit 로그 분석

**Secret 무단 접근 탐지**:

```
# AWS CloudWatch Insights
fields @timestamp, user.username, objectRef.name, objectRef.namespace
| filter verb == "get" and objectRef.resource == "secrets"
| filter user.username != "system:serviceaccount:external-secrets:external-secrets-operator"
| filter user.username != /system:serviceaccount:kube-system:.*/
| stats count() as access_count by user.username, objectRef.namespace
| filter access_count > 10
```

**특권 escalation 시도 탐지**:

```
# Kubernetes Audit Log Query (Elasticsearch)
GET /k8s-audit-*/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"verb": "create"}},
        {"terms": {"objectRef.resource": ["clusterrolebindings", "rolebindings"]}},
        {"term": {"responseStatus.code": 201}}
      ],
      "must_not": [
        {"prefix": {"user.username": "system:serviceaccount:kube-system"}}
      ]
    }
  },
  "aggs": {
    "by_user": {
      "terms": {"field": "user.username"}
    }
  }
}
```

**Exec into Pod 행위 모니터링**:

```
fields @timestamp, user.username, objectRef.name, objectRef.namespace
| filter verb == "create" and objectRef.subresource == "exec"
| filter user.username != /system:serviceaccount:kube-system:.*/
| stats count() as exec_count by user.username, objectRef.namespace, objectRef.name
| sort -exec_count
```

### 15.3 Falco 이벤트 분석

**Falco 이벤트를 SIEM에 전송**:

```yaml
# Falco Helm Values: Elasticsearch 통합
falco:
  jsonOutput: true
  jsonIncludeOutputProperty: true
  httpOutput:
    enabled: true
    url: "https://elasticsearch.example.com:9200/falco-events/_doc"
```

**Splunk 쿼리: 컨테이너 탈출 시도 탐지**:

```spl
index=falco priority="CRITICAL" OR priority="WARNING"
| search rule="*container escape*" OR rule="*host filesystem*"
| stats count by container.name, container.image.repository, rule, output
| sort -count
```

## 16. 한국 기업 영향 분석

### 16.1 ISMS-P CI/CD 보안 요구사항

**정보보호 및 개인정보보호 관리체계 인증 (ISMS-P)** 2.8.2항 (개발 보안):

| ISMS-P 요구사항 | 구현 방법 | 관련 도구 |
|-----------------|-----------|-----------|
| **2.8.2.1 - 시큐어 코딩** | SAST 도구 CI 통합, 정적 분석 | Semgrep, SonarQube |
| **2.8.2.2 - 소스코드 보안 취약점 점검** | 자동화된 보안 스캔, PR 검사 | GitHub Advanced Security, Snyk |
| **2.8.2.3 - 형상 관리** | Git 버전 관리, 변경 이력 추적 | GitHub, GitLab |
| **2.8.2.4 - 테스트 데이터 보안** | 프로덕션 데이터 마스킹, 합성 데이터 생성 | Faker, Anonymization tools |

**실무 적용 예시**:

```yaml
# ISMS-P 2.8.2.2 - PR 보안 검사 자동화
name: ISMS-P Compliance Check
on:
  pull_request:
    branches: [main, develop]

jobs:
  security-compliance:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4

    # 시큐어 코딩 검사
    - name: Secure Coding Check (SAST)
      uses: returntocorp/semgrep-action@v1
      with:
        config: p/owasp-top-ten

    # 취약점 점검
    - name: Vulnerability Scan
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        severity: 'CRITICAL,HIGH'
        exit-code: '1'

    # Secret 검사
    - name: Secret Scanning
      uses: gitleaks/gitleaks-action@v2

    # 컴플라이언스 보고서 생성
    - name: Generate Compliance Report
      run: |
        echo "ISMS-P 2.8.2 Compliance Check - $(date)" > compliance-report.txt
        echo "SAST: PASSED" >> compliance-report.txt
        echo "Vulnerability Scan: PASSED" >> compliance-report.txt
        echo "Secret Scanning: PASSED" >> compliance-report.txt

    - name: Upload Report
      uses: actions/upload-artifact@v3
      with:
        name: isms-p-compliance-report
        path: compliance-report.txt
```

### 16.2 금융권 DevSecOps 규제

**금융보안원 DevSecOps 보안 가이드라인** (2024년 개정):

| 항목 | 요구사항 | 구현 방법 |
|------|----------|-----------|
| **이중 인증** | 프로덕션 배포 시 2인 이상 승인 | GitHub Environments + Required Reviewers |
| **변경 추적** | 모든 배포 이력 90일 이상 보관 | Audit Logs + S3 장기 보관 |
| **롤백 절차** | 5분 이내 이전 버전 복구 가능 | Blue/Green Deployment + ArgoCD Rollback |
| **접근 제어** | 프로덕션 환경 접근 IP 제한 | VPN + AWS Security Groups |

**금융권 배포 파이프라인 예시**:

```yaml
# .github/workflows/fintech-deploy.yml
name: Financial Grade Deployment
on:
  push:
    branches: [main]

jobs:
  deploy-to-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://prod.example.com
    steps:
    - uses: actions/checkout@v4

    # 이중 인증: GitHub Environment Protection Rules로 2인 승인 필수
    # (GitHub Settings -> Environments -> production -> Required reviewers)

    # 변경 추적
    - name: Log Deployment
      run: |
        echo "Deployment initiated by {% raw %}${{ github.actor }}{% endraw %}" >> deploy.log
        echo "Commit: {% raw %}${{ github.sha }}{% endraw %}" >> deploy.log
        echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> deploy.log
        aws s3 cp deploy.log s3://audit-logs/deployments/$(date +%Y%m%d)/ --region ap-northeast-2

    # 보안 스캔
    - name: Final Security Scan
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        severity: 'CRITICAL'
        exit-code: '1'

    # Blue/Green Deployment
    - name: Deploy to Green
      run: |
        kubectl apply -f k8s/green-deployment.yaml
        kubectl wait --for=condition=available --timeout=300s deployment/myapp-green

    # Health Check
    - name: Verify Green Deployment
      run: |
        for i in {1..5}; do
          if curl -f https://green.example.com/health; then
            echo "Health check passed"
            break
          fi
          sleep 10
        done

    # Traffic Switch
    - name: Switch Traffic to Green
      run: |
        kubectl patch service myapp -p '{"spec":{"selector":{"version":"green"}}}'

    # Rollback 준비
    - name: Keep Blue for Rollback
      run: |
        echo "Blue deployment kept for 24 hours for rollback capability"
        kubectl annotate deployment myapp-blue rollback-ready=true
```

### 16.3 개인정보보호법 준수

**개인정보의 안전성 확보조치 기준** (2023년 개정):

| 조항 | 요구사항 | CI/CD 구현 |
|------|----------|------------|
| **제4조 - 접근 권한 관리** | 최소 권한 원칙 적용 | Kubernetes RBAC + OIDC |
| **제6조 - 접근통제** | 인증/인가 로그 6개월 보관 | Audit Logs → S3 Glacier |
| **제7조 - 암호화** | 개인정보 저장 시 암호화 | External Secrets + KMS |
| **제10조 - 보안 프로그램 | 보안 취약점 점검 및 조치 | SAST/DAST + Trivy |

## 17. 경영진 보고 포맷 (Board Reporting)

### 17.1 월간 보안 대시보드

```markdown
# CI/CD 및 Kubernetes 보안 현황 (2025년 6월)

## 주요 지표 (KPI)

| 지표 | 현재 | 전월 | 목표 | 상태 |
|------|------|------|------|------|
| **Critical 취약점 평균 해결 시간** | 2시간 | 4시간 | <4시간 | ✅ 목표 달성 |
| **배포 실패율** | 2.3% | 3.1% | <5% | ✅ 목표 달성 |
| **보안 스캔 통과율** | 97.8% | 95.2% | >95% | ✅ 목표 달성 |
| **Secret 유출 사고** | 0건 | 0건 | 0건 | ✅ 목표 달성 |
| **컴플라이언스 위반** | 0건 | 1건 | 0건 | ✅ 개선됨 |

## 보안 사고 현황

- **총 탐지된 위협**: 47건
  - CRITICAL: 2건 (모두 해결)
  - HIGH: 8건 (7건 해결, 1건 진행 중)
  - MEDIUM: 37건 (32건 해결, 5건 예정)

## 주요 성과

1. **Kubernetes User Namespaces 적용** (2025-06-01)
   - 컨테이너 탈출 리스크 95% 감소
   - 프로덕션 환경 100% 적용 완료

2. **GitHub Actions OIDC 전환** (2025-06-15)
   - Secret 관리 부담 70% 감소
   - 자동 credential rotation 구현

3. **Falco 런타임 모니터링 배포** (2025-06-20)
   - 실시간 위협 탐지 활성화
   - 이상 행위 47건 탐지 및 차단

## 위험 요인 및 대응

| 위험 | 심각도 | 영향 | 대응 계획 |
|------|--------|------|-----------|
| EKS 1.32 익명 인증 변경 | 중 | 모니터링 도구 영향 가능 | 7월 15일까지 RBAC 마이그레이션 완료 |
| Log4Shell 유사 취약점 | 고 | 의존성 취약점 노출 | 자동 스캔 및 패치 프로세스 운영 중 |

## 다음 달 계획

1. Pod Certificates (mTLS) Beta 테스트 (7월 5일)
2. Kyverno Policy 확대 적용 (7월 10일)
3. DevSecOps 교육 프로그램 실시 (7월 20일)
```

### 17.2 분기별 ROI 보고서

```markdown
# DevSecOps 투자 수익률 (ROI) 보고서 - 2025 Q2

## Executive Summary

2025년 2분기 DevSecOps 보안 자동화 투자로 **연간 ₩450M 비용 절감** 및 **보안 리스크 85% 감소** 달성.

## 투자 내역

| 항목 | Q2 투자 | 누적 |
|------|---------|------|
| 보안 도구 라이선스 | ₩18M | ₩72M |
| 교육 및 트레이닝 | ₩12M | ₩48M |
| 구현 및 통합 | ₩15M | ₩60M |
| 운영 및 유지보수 | ₩10M | ₩40M |
| **총계** | **₩55M** | **₩220M** |

## 비용 절감 효과

| 항목 | 절감액 (연간 추정) | 상세 |
|------|-------------------|------|
| **보안 사고 대응 비용 감소** | ₩180M | 사고 대응 인력/시간 94% 감소 |
| **컴플라이언스 감사 비용** | ₩35M | 자동화로 외부 감사 비용 70% 절감 |
| **인력 효율성 개선** | ₩150M | 수동 작업 자동화로 FTE 3명 절감 |
| **배포 실패 비용 감소** | ₩85M | 롤백 및 긴급 패치 80% 감소 |
| **총 절감액** | **₩450M** | - |

**ROI = (절감액 - 투자액) / 투자액 = (₩450M - ₩220M) / ₩220M = 105%**

## 보안 리스크 감소

| 위협 유형 | 기존 리스크 | 현재 리스크 | 개선율 |
|-----------|-------------|-------------|--------|
| Supply Chain 공격 | 높음 | 낮음 | 85% ↓ |
| Secret 유출 | 중간 | 매우 낮음 | 95% ↓ |
| 컨테이너 탈출 | 높음 | 낮음 | 90% ↓ |
| 내부자 위협 | 중간 | 낮음 | 70% ↓ |

## 권장 사항

1. **Q3 투자 우선순위**: Pod Certificates (mTLS) 전사 확대 (예산: ₩25M)
2. **교육 강화**: DevSecOps 인증 프로그램 (예산: ₩15M)
3. **도구 통합**: SIEM 연동 고도화 (예산: ₩10M)
```

## 18. 마무리

이번 주차에서는 CI/CD 파이프라인과 Kubernetes 환경의 보안을 강화하는 다양한 방법을 학습했습니다. 또한 2025년 Kubernetes 보안 업데이트를 통해 Fine-grained Kubelet API Authorization, Credential Tracking, User Namespaces, Pod Certificates 등 최신 보안 기능들을 살펴보았습니다. **Shift-Left Security** 원칙에 따라 개발 초기 단계부터 보안을 적용하는 것이 중요합니다.

> **다음 주차 예고:** DevSecOps 전체 통합 정리 및 실무 적용 가이드

---

## 참고 자료

### 외부 참고 자료

1. **Kubernetes Security**
   - [Kubernetes RBAC 공식 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
   - [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
   - [Kubernetes Security Best Practices](https://kubernetes.io/docs/concepts/security/)
   - [User Namespaces Documentation](https://kubernetes.io/docs/concepts/security/user-namespaces/)

2. **CI/CD Security**
   - [GitHub Actions Security Guides](https://docs.github.com/en/actions/security-guides)
   - [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)
   - [CNCF Security Whitepaper](https://github.com/cncf/tag-security)
   - [SLSA Framework (Supply Chain Levels for Software Artifacts)](https://slsa.dev/)

3. **Security Tools**
   - [Falco Runtime Security](https://falco.org/docs/)
   - [Kyverno Policy Engine](https://kyverno.io/docs/)
   - [Trivy Vulnerability Scanner](https://aquasecurity.github.io/trivy/)
   - [Gitleaks Secret Detection](https://github.com/gitleaks/gitleaks)
   - [Semgrep SAST](https://semgrep.dev/docs/)

4. **MITRE ATT&CK Framework**
   - [MITRE ATT&CK for Containers](https://attack.mitre.org/matrices/enterprise/containers/)
   - [T1195.002 - Supply Chain Compromise](https://attack.mitre.org/techniques/T1195/002/)
   - [T1610 - Deploy Container](https://attack.mitre.org/techniques/T1610/)

5. **Compliance**
   - [ISMS-P 인증기준 (정보보호 및 개인정보보호 관리체계)](https://www.kisa.or.kr/)
   - [금융보안원 DevSecOps 가이드](https://www.fsec.or.kr/)
   - [개인정보의 안전성 확보조치 기준](https://www.law.go.kr/)
   - [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)

6. **Cloud Provider Security**
   - [Amazon EKS Best Practices Guide - Security](https://aws.github.io/aws-eks-best-practices/security/docs/)
   - [Google GKE Security Hardening Guide](https://cloud.google.com/kubernetes-engine/docs/how-to/hardening-your-cluster)
   - [Azure AKS Security Baseline](https://learn.microsoft.com/en-us/security/benchmark/azure/baselines/aks-security-baseline)

7. **Secret Management**
   - [External Secrets Operator](https://external-secrets.io/latest/)
   - [Sealed Secrets by Bitnami](https://sealed-secrets.netlify.app/)
   - [HashiCorp Vault with Kubernetes](https://developer.hashicorp.com/vault/tutorials/kubernetes)

8. **GitOps Security**
   - [Argo CD Security Best Practices](https://argo-cd.readthedocs.io/en/stable/operator-manual/security/)
   - [Flux Security Documentation](https://fluxcd.io/flux/security/)

9. **Container Image Security**
   - [Sigstore Cosign](https://docs.sigstore.dev/cosign/overview/)
   - [Docker Content Trust](https://docs.docker.com/engine/security/trust/)
   - [Harbor Image Registry](https://goharbor.io/docs/)

10. **Industry Reports**
    - [CNCF Annual Survey 2024](https://www.cncf.io/reports/cncf-annual-survey-2024/)
    - [Snyk State of Open Source Security 2025](https://snyk.io/reports/)
    - [Aqua Security Cloud Native Threat Report 2025](https://www.aquasec.com/resources/threat-reports/)

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| **CI/CD 보안** | 파이프라인 보안, Secret 관리, 이미지 스캔 자동화 | [수강하기](https://edu.2twodragon.com/courses/cicd-security) |
| **Kubernetes 보안** | 클러스터 보안, RBAC, Network Policies, Pod Security | [수강하기](https://edu.2twodragon.com/courses/kubernetes-security) |
| **DevSecOps 실전** | DevSecOps 전략, 보안 자동화, 모니터링 | [수강하기](https://edu.2twodragon.com/courses/devsecops) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| **AWS WAF 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

---
