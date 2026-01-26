---
layout: post
title: "클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드"
date: 2025-06-06 19:45:40 +0900
category: kubernetes
categories: [kubernetes]
tags: [CI/CD, Kubernetes, Security, DevSecOps, GitOps, Pipeline-Security]
excerpt: "CI/CD 파이프라인 보안: GitHub Actions 보안 설정(permissions 최소화, Secret 관리), SAST/DAST 통합(Semgrep, SonarQube, Gitleaks, Trivy, OWASP ZAP), Secret 스캐닝, 의존성 취약점 스캔"
comments: true
original_url: https://twodragon.tistory.com/689
image: /assets/images/2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide.svg
image_alt: "Cloud Security Course 7Batch 8Week: CI/CD and Kubernetes Security Practical Guide"
toc: true
certifications: [ckad, cka]
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
 GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

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
 docker build -t ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} .

 # 이미지 취약점 스캐닝
 - name: Scan Docker image
 uses: aquasecurity/trivy-action@master
 with:
 image-ref: '${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}'
 severity: 'CRITICAL,HIGH'
 exit-code: '1'

 # 이미지 서명 (Cosign)
 - name: Sign image with Cosign
 run: |
 cosign sign --key env://COSIGN_PRIVATE_KEY \
 ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
 env:
 COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}

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

## 11. 마무리

이번 주차에서는 CI/CD 파이프라인과 Kubernetes 환경의 보안을 강화하는 다양한 방법을 학습했습니다. 또한 2025년 Kubernetes 보안 업데이트를 통해 Fine-grained Kubelet API Authorization, Credential Tracking, User Namespaces, Pod Certificates 등 최신 보안 기능들을 살펴보았습니다. **Shift-Left Security** 원칙에 따라 개발 초기 단계부터 보안을 적용하는 것이 중요합니다.

> **다음 주차 예고:** DevSecOps 전체 통합 정리 및 실무 적용 가이드

---

## 관련 자료

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

📚 **외부 참고 자료:**
- [Kubernetes RBAC 공식 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [CNCF Security Whitepaper](https://github.com/cncf/tag-security)
