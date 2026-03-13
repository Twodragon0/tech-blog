---
layout: post
title: '클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드'
date: 2025-06-06 19:45:40 +0900
categories:
- kubernetes
tags:
- CI/CD
- Kubernetes
- Security
- DevSecOps
- GitOps
- Pipeline-Security
excerpt: "CI/CD 파이프라인 보안(GitHub Actions, SAST/DAST, Secret 스캐닝), Kubernetes 클러스터"
description: CI/CD 파이프라인 보안(GitHub Actions, SAST/DAST, Secret 스캐닝), Kubernetes 클러스터
  보안(RBAC, Pod Security Standards, Network Policy), 이미지 서명, 런타임 보안까지 정리.
image: /assets/images/2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide.svg
toc: true
keywords:
- CI/CD
- Kubernetes
- Security
- DevSecOps
- GitOps
- Pipeline-Security
author: Yongho Ha
comments: true
image_alt: 'Cloud Security Course 7Batch 8Week: CI/CD and Kubernetes Security Practical
  Guide'
certifications:
- ckad
- cka
original_url: https://twodragon.tistory.com/689
series: "Cloud Security Course 7기"
series_order: 6
series_total: 7
---

{%- include ai-summary-card.html
  title='클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드'
  categories_html='<span class="category-tag devops">Kubernetes</span>'
  tags_html='<span class="tag">CI/CD</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">Security</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">GitOps</span>
      <span class="tag">Pipeline-Security</span>'
  highlights_html='<li><strong>CI/CD 파이프라인 보안</strong>: GitHub Actions 보안 설정(permissions 최소화, Secret 관리), SAST/DAST 통합(Semgrep, SonarQube, Gitleaks, Trivy, OWASP ZAP), Secret 스캐닝, 의존성 취약점 스캔</li>
      <li><strong>Kubernetes 클러스터 보안</strong>: RBAC(Role, RoleBinding, ClusterRole, ClusterRoleBinding), Pod Security Standards(Restricted/Baseline/Privileged), Network Policy(트래픽 제어, 네임스페이스 격리), Service Account 최소 권한</li>
      <li><strong>이미지 서명 및 Secret 관리</strong>: Cosign 이미지 서명, Kubernetes Secrets 관리, External Secrets Operator, Sealed Secrets, Vault 통합</li>
      <li><strong>런타임 보안</strong>: Kyverno 정책 엔진(Admission Control, Policy as Code), Falco 이상 행위 탐지, GitOps 보안 모범 사례(ArgoCD, Flux), 실무 적용 체크리스트</li>'
  audience='클라우드 보안 전문가, DevOps 엔지니어, 보안 담당자'
-%}

<img src="{{ '/assets/images/2025-06-06-Cloud_Security_Course_7Batch_-_8Week_CICDand_Kubernetes_Security_Practical_Guide_image.png' | relative_url }}" alt="Cloud Security Course 7Batch 8Week: CI/CD and Kubernetes Security Practical Guide" loading="lazy" class="post-image">

![DevOps Platform News Section Banner](/assets/images/section-devops.svg)

## Executive Summary

본 가이드는 클라우드 시큐리티 과정 7기 8주차에서 다룬 CI/CD 파이프라인 보안과 Kubernetes 클러스터 보안의 핵심 내용을 실무 관점에서 정리합니다.

현대 클라우드 네이티브 환경에서 컨테이너와 Kubernetes는 애플리케이션 배포의 표준이 되었습니다. 그러나 이 편리함 뒤에는 새로운 공격 표면(Attack Surface)이 존재합니다. 소프트웨어 공급망 공격(Supply Chain Attack), 컨테이너 탈출(Container Escape), 권한 상승(Privilege Escalation) 등의 위협이 증가하고 있습니다.

**핵심 결론:**
- CI/CD 파이프라인은 코드부터 배포까지 전 단계에 보안 통제가 필요합니다.
- Kubernetes RBAC와 Pod Security Standards는 최소 권한 원칙의 핵심입니다.
- 이미지 서명(Cosign)과 정책 엔진(Kyverno)으로 공급망 공격을 방어합니다.
- 런타임 보안(Falco)으로 배포 후 이상 행위를 실시간 탐지합니다.

## 위험 스코어카드

아래 표는 CI/CD 및 Kubernetes 환경에서 발생할 수 있는 주요 보안 위험도를 평가한 스코어카드입니다.

| 위험 항목 | 위험도 | 발생 가능성 | 영향도 | 우선순위 |
|-----------|--------|------------|--------|---------|
| CI/CD Secret 노출 | 🔴 긴급 | 높음 | 매우 높음 | P0 |
| 컨테이너 이미지 취약점 | 🔴 긴급 | 높음 | 높음 | P0 |
| RBAC 과도한 권한 부여 | 🟠 높음 | 중간 | 높음 | P1 |
| 네트워크 정책 미적용 | 🟠 높음 | 높음 | 중간 | P1 |
| Pod Security Standards 미준수 | 🟡 중간 | 중간 | 중간 | P2 |
| 이미지 서명 검증 미적용 | 🟡 중간 | 낮음 | 높음 | P2 |
| 런타임 보안 모니터링 부재 | 🟡 중간 | 높음 | 중간 | P2 |
| etcd 암호화 미설정 | 🟢 낮음 | 낮음 | 높음 | P3 |

> **위험도 기준**: P0(즉시 조치), P1(1주 내 조치), P2(1개월 내 조치), P3(분기 내 조치)

## 서론

안녕하세요, Twodragon입니다. 이번 포스팅에서는 컨테이너 및 Kubernetes 보안에 대해 실무 중심으로 정리합니다.

2025년 Docker와 Kubernetes는 여전히 클라우드 네이티브 애플리케이션의 핵심 기술이며, 보안은 더욱 중요해지고 있습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- CI/CD 파이프라인 보안: GitHub Actions, SAST/DAST, Secret 스캐닝
- Kubernetes 클러스터 보안: RBAC, Pod Security Standards, Network Policy
- 컨테이너 이미지 보안: 취약점 스캔, 이미지 서명
- Secret 관리: Vault, External Secrets Operator, Sealed Secrets
- 런타임 보안: Falco 이상 행위 탐지, Kyverno 정책 엔진

## 1. CI/CD 파이프라인 보안 기초

<figure>
<img src="{{ '/assets/images/diagrams/diagram_devsecops_pipeline.png' | relative_url }}" alt="DevSecOps CI/CD Pipeline Architecture" loading="lazy" class="post-image">
<figcaption>DevSecOps CI/CD 파이프라인 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

### 1.1 CI/CD 보안의 중요성

CI/CD 파이프라인은 소프트웨어 개발 생명주기 전반에 걸쳐 자동화된 빌드, 테스트, 배포를 수행합니다. 이 과정에서 보안을 소홀히 하면 다음과 같은 위험이 발생합니다.

**주요 위협 벡터:**
- **Secret 노출**: 환경 변수나 로그에 API 키, 비밀번호 노출
- **소프트웨어 공급망 공격**: 악의적인 의존성 패키지 삽입
- **권한 상승**: 파이프라인 실행 컨텍스트를 통한 클라우드 리소스 접근
- **이미지 변조**: 검증되지 않은 컨테이너 이미지 배포

**DevSecOps 보안 통제 레이어:**

| 단계 | 보안 도구 | 설명 |
|------|----------|------|
| 코드 커밋 | Gitleaks, truffleHog | Secret 스캐닝 |
| 빌드 | Semgrep, SonarQube | SAST 정적 분석 |
| 이미지 스캔 | Trivy, Grype | 컨테이너 취약점 스캔 |
| 테스트 | OWASP ZAP, Burp | DAST 동적 분석 |
| 배포 | Cosign, Notary | 이미지 서명 검증 |
| 런타임 | Falco, Sysdig | 이상 행위 탐지 |

### 1.2 GitHub Actions 보안 설정

GitHub Actions 워크플로우에서 보안을 강화하기 위한 핵심 설정입니다.

**최소 권한 원칙 적용 예시:**

```yaml
permissions:
  contents: read
  packages: write
  id-token: write
```

**주요 보안 설정 항목:**

| 설정 항목 | 권장값 | 설명 |
|----------|--------|------|
| permissions | 최소 필요 권한만 | 워크플로우 레벨 권한 제한 |
| GITHUB_TOKEN | 스코프 최소화 | 기본 토큰 권한 제한 |
| environment | 보호된 환경 사용 | 프로덕션 배포 승인 필요 |
| timeout-minutes | 30 이하 | 무한 실행 방지 |
| pull_request_target | 주의 사용 | 포크 PR 위험 방지 |

> 참고: GitHub Actions 보안 설정 관련 내용은 [GitHub Actions 보안 가이드](https://docs.github.com/en/actions) 및 [GitHub Actions 예제](https://docs.github.com/en/actions/using-workflows/workflow-templates)를 참조하세요.

### 1.3 SAST/DAST 통합

**SAST(Static Application Security Testing) 도구 비교:**

| 도구 | 언어 지원 | 특징 | 라이선스 |
|------|----------|------|---------|
| Semgrep | 30+ 언어 | 커스텀 룰 작성 용이 | OSS/상용 |
| SonarQube | 25+ 언어 | 품질 게이트 통합 | 상용/무료 |
| CodeQL | 10+ 언어 | GitHub 네이티브 | 무료(GitHub) |
| Bandit | Python | Python 특화 | OSS |
| ESLint Security | JavaScript | JS/TS 특화 | OSS |

Trivy를 이용한 컨테이너 이미지 스캔 예시:

```bash
trivy image --severity HIGH,CRITICAL \
  --exit-code 1 \
  myapp:latest
```

### 1.4 Secret 스캐닝 및 관리

파이프라인에서 Secret이 노출되는 것을 방지하기 위한 접근 방법입니다.

**pre-commit 훅으로 커밋 전 검사:**

```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**Secret 관리 도구 비교:**

| 도구 | 유형 | 특징 | Kubernetes 통합 |
|------|------|------|----------------|
| HashiCorp Vault | 자체 호스팅 | 동적 Secret 생성 | External Secrets |
| AWS Secrets Manager | 관리형 | AWS 네이티브 | External Secrets |
| GCP Secret Manager | 관리형 | GCP 네이티브 | External Secrets |
| Azure Key Vault | 관리형 | Azure 네이티브 | CSI Driver |
| Sealed Secrets | K8s 네이티브 | GitOps 친화적 | 네이티브 |

## 2. Kubernetes RBAC 보안

<figure>
<img src="{{ '/assets/images/diagrams/diagram_k8s_security.png' | relative_url }}" alt="Kubernetes Security Architecture" loading="lazy" class="post-image">
<figcaption>Kubernetes 보안 아키텍처 - Python diagrams로 생성</figcaption>
</figure>

### 2.1 최소 권한 원칙 적용

Kubernetes RBAC는 API 서버에 대한 접근을 제어하는 핵심 보안 메커니즘입니다.

**RBAC 구성 요소:**

| 리소스 | 범위 | 설명 |
|--------|------|------|
| Role | Namespace | 네임스페이스 내 권한 정의 |
| ClusterRole | Cluster | 클러스터 전체 권한 정의 |
| RoleBinding | Namespace | 사용자/그룹에 Role 바인딩 |
| ClusterRoleBinding | Cluster | 사용자/그룹에 ClusterRole 바인딩 |

개발자용 최소 권한 Role 예시:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-role
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch"]
```

> 참고: Kubernetes RBAC 및 최소 권한 원칙 관련 내용은 [Kubernetes RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) 및 [Kubernetes 보안 모범 사례](https://kubernetes.io/docs/concepts/security/)를 참조하세요.

### 2.2 Service Account 보안

Service Account는 Pod가 Kubernetes API에 접근할 때 사용하는 ID입니다. 잘못 구성된 Service Account는 권한 상승의 주요 경로가 됩니다.

**Service Account 보안 모범 사례:**
- 각 애플리케이션에 전용 Service Account 생성
- `automountServiceAccountToken: false` 기본 설정
- 필요한 경우에만 토큰 마운트 허용
- IRSA(IAM Roles for Service Accounts) 활용 (AWS EKS)

**Service Account 토큰 자동 마운트 비활성화:**

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
automountServiceAccountToken: false
```

### 2.3 Pod Security Standards

Pod Security Standards(PSS)는 Kubernetes 1.25에서 GA된 Pod 보안 정책의 후속 기능입니다.

**PSS 정책 수준 비교:**

| 수준 | 설명 | 사용 권장 환경 |
|------|------|--------------|
| Privileged | 제한 없음 | 시스템 컴포넌트만 |
| Baseline | 기본 보안 | 일반 애플리케이션 |
| Restricted | 최고 보안 | 보안이 중요한 워크로드 |

네임스페이스에 Restricted 정책 적용:

```bash
kubectl label namespace prod \
  pod-security.kubernetes.io/enforce=restricted
```

### 2.4 Network Policy 구성

Kubernetes Network Policy는 Pod 간 트래픽을 제어하는 L3/L4 방화벽 역할을 합니다.

**기본 거부(Default Deny) 정책 예시:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

**네임스페이스 간 격리 설정:**

| 정책 유형 | 방향 | 대상 | 효과 |
|----------|------|------|------|
| Default Deny | Ingress+Egress | 모든 Pod | 외부 트래픽 차단 |
| Allow DNS | Egress | kube-dns | DNS 조회 허용 |
| Allow Internal | Ingress | 같은 네임스페이스 | 내부 통신 허용 |
| Allow Monitoring | Ingress | Prometheus | 메트릭 수집 허용 |

## 3. 컨테이너 이미지 보안

### 3.1 이미지 취약점 스캔

컨테이너 이미지의 취약점을 파이프라인 단계에서 사전에 탐지하고 차단합니다.

**Trivy를 이용한 이미지 스캔 예시:**

```bash
trivy image --format sarif \
  --output results.sarif \
  myapp:v1.0.0
```

**이미지 스캔 도구 비교:**

| 도구 | 스캔 대상 | CI/CD 통합 | 특징 |
|------|----------|-----------|------|
| Trivy | OS, 라이브러리, IaC | 매우 쉬움 | 빠른 속도, 광범위한 지원 |
| Grype | OS, 라이브러리 | 쉬움 | Anchore 기반 |
| Snyk | 이미지, 코드, IaC | 쉬움 | 개발자 친화적 |
| Clair | OS 패키지 | 복잡함 | 서버 기반 |
| Docker Scout | 이미지 | Docker 네이티브 | Docker Desktop 통합 |

### 3.2 이미지 서명 및 검증

Cosign을 이용하여 컨테이너 이미지에 디지털 서명을 추가하고, 배포 시 검증합니다.

**Cosign으로 이미지 서명:**

```bash
cosign sign --key cosign.key \
  myregistry/myapp:v1.0.0
```

**서명 검증 워크플로우:**

| 단계 | 도구 | 동작 |
|------|------|------|
| 이미지 빌드 | Docker/Buildkit | 이미지 빌드 |
| SBOM 생성 | Syft | 소프트웨어 목록 생성 |
| 이미지 서명 | Cosign | 개인 키로 서명 |
| 레지스트리 푸시 | docker push | 이미지 및 서명 업로드 |
| 배포 검증 | Kyverno/Gatekeeper | 서명 검증 후 허용 |

### 3.3 베이스 이미지 보안 강화

**안전한 베이스 이미지 선택 기준:**

| 이미지 유형 | 크기 | 공격 표면 | 권장 용도 |
|-----------|------|----------|---------|
| scratch | 0MB | 없음 | Go 정적 바이너리 |
| distroless | ~20MB | 최소 | 프로덕션 서비스 |
| alpine | ~5MB | 낮음 | 유틸리티 포함 필요 시 |
| ubuntu-minimal | ~30MB | 중간 | 디버깅이 필요한 경우 |
| ubuntu | ~80MB | 높음 | 개발/테스트 환경 |

## 4. Secret 관리 및 GitOps 보안

### 4.1 External Secrets Operator

External Secrets Operator(ESO)는 외부 Secret 저장소(Vault, AWS Secrets Manager 등)에서 Kubernetes Secret을 동기화합니다.

**ESO 설치 및 구성:**

```bash
helm repo add external-secrets \
  https://charts.external-secrets.io
helm install external-secrets \
  external-secrets/external-secrets
```

**SecretStore 구성 예시 (AWS):**

| 필드 | 설명 | 예시 값 |
|------|------|--------|
| provider | 외부 Secret 제공자 | aws |
| region | AWS 리전 | ap-northeast-2 |
| auth.jwt | IRSA 인증 방식 | serviceAccountRef |
| refreshInterval | 동기화 주기 | 1h |

### 4.2 Sealed Secrets

Sealed Secrets는 암호화된 Secret을 Git에 안전하게 저장할 수 있게 해주는 GitOps 친화적인 솔루션입니다.

**Sealed Secret 생성 및 사용:**

```bash
kubeseal --format=yaml \
  < secret.yaml > sealed-secret.yaml
```

**Vault vs Sealed Secrets 비교:**

| 비교 항목 | HashiCorp Vault | Sealed Secrets |
|----------|----------------|----------------|
| 복잡도 | 높음 | 낮음 |
| GitOps 친화성 | 중간 | 높음 |
| 동적 Secret | 지원 | 미지원 |
| 감사 로그 | 상세 | 기본 |
| 학습 곡선 | 가파름 | 완만함 |
| 운영 오버헤드 | 높음 | 낮음 |

### 4.3 GitOps 보안 모범 사례

GitOps를 안전하게 운영하기 위한 핵심 원칙입니다.

**ArgoCD 보안 강화 포인트:**
- 프로젝트 별 접근 제어(AppProject RBAC)
- SSO 통합(Dex, OIDC)
- 레포지토리 접근 제한
- 웹훅 시크릿 설정
- 배포 승인 워크플로우

## 5. 런타임 보안

### 5.1 Falco 이상 행위 탐지

Falco는 Kubernetes 런타임에서 비정상적인 행동을 실시간으로 탐지하는 오픈소스 보안 도구입니다.

**Falco 주요 탐지 시나리오:**

| 탐지 항목 | 심각도 | 설명 |
|----------|--------|------|
| 컨테이너 내 쉘 실행 | 높음 | `/bin/bash`, `/bin/sh` 실행 탐지 |
| 민감 파일 접근 | 높음 | `/etc/shadow`, `/etc/passwd` 접근 |
| 네트워크 도구 실행 | 중간 | `curl`, `wget` 등 실행 |
| 권한 상승 시도 | 긴급 | `sudo`, `su` 명령 실행 |
| 이상 프로세스 생성 | 중간 | 예상치 못한 프로세스 실행 |

**Falco 설치 (Helm):**

```bash
helm repo add falcosecurity \
  https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --set falco.grpc.enabled=true
```

### 5.2 Kyverno 정책 엔진

Kyverno는 Kubernetes 네이티브 정책 엔진으로 Admission Control을 통해 Policy as Code를 구현합니다.

**Kyverno 정책 유형:**

| 정책 유형 | 동작 | 사용 시나리오 |
|----------|------|-------------|
| validate | 검증 | 보안 기준 미충족 리소스 거부 |
| mutate | 변환 | 기본값 자동 설정 |
| generate | 생성 | 리소스 자동 생성 |
| verifyImages | 이미지 검증 | 서명된 이미지만 허용 |

**이미지 서명 검증 정책 예시:**

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  rules:
    - name: check-image-signature
      verifyImages:
        - imageReferences: ["myregistry/*"]
```

### 5.3 런타임 보안 아키텍처

**계층별 런타임 보안 도구:**

| 계층 | 도구 | 기능 |
|------|------|------|
| 호스트 OS | AppArmor, SELinux | 시스템 콜 제한 |
| 컨테이너 런타임 | gVisor, Kata Containers | 샌드박싱 |
| Kubernetes | Kyverno, OPA/Gatekeeper | 정책 적용 |
| 애플리케이션 | Falco, Sysdig | 이상 행위 탐지 |
| 네트워크 | Cilium, Calico | 네트워크 정책 |

## 6. 보안 체크리스트 및 실무 적용

### 6.1 CI/CD 파이프라인 보안 체크리스트

파이프라인 구성 전 반드시 확인해야 할 항목입니다.

**파이프라인 설정 검토:**
- [ ] GitHub Actions permissions를 최소 필요 권한으로 제한했는가?
- [ ] 모든 Secret을 GitHub Secrets 또는 외부 Secret 관리 도구에 저장했는가?
- [ ] SAST 도구(Semgrep, SonarQube)가 파이프라인에 통합되어 있는가?
- [ ] 컨테이너 이미지 취약점 스캔(Trivy)이 빌드 단계에서 실행되는가?
- [ ] 프로덕션 배포 전 수동 승인 단계가 있는가?
- [ ] 파이프라인 실행 로그가 감사 목적으로 보존되는가?
- [ ] Gitleaks 또는 truffleHog로 커밋 전 Secret 스캐닝을 수행하는가?
- [ ] 의존성 취약점 스캔(npm audit, pip audit)이 자동화되어 있는가?
- [ ] 이미지 서명(Cosign)이 배포 파이프라인에 적용되어 있는가?
- [ ] SBOM(Software Bill of Materials)이 생성 및 관리되고 있는가?

### 6.2 Kubernetes 클러스터 보안 체크리스트

Kubernetes 클러스터 배포 전후 확인 항목입니다.

**클러스터 보안 검토:**
- [ ] RBAC가 활성화되어 있으며 최소 권한 원칙이 적용되어 있는가?
- [ ] Pod Security Standards(Restricted)가 프로덕션 네임스페이스에 적용되어 있는가?
- [ ] Network Policy(Default Deny)가 모든 네임스페이스에 설정되어 있는가?
- [ ] etcd 데이터가 암호화되어 있는가?
- [ ] API 서버에 익명 접근이 비활성화되어 있는가?
- [ ] kube-bench로 CIS Kubernetes Benchmark를 실행했는가?
- [ ] Falco 또는 런타임 보안 도구가 활성화되어 있는가?
- [ ] 클러스터 감사 로그(Audit Logging)가 활성화되어 있는가?
- [ ] Service Account 토큰 자동 마운트가 비활성화되어 있는가?
- [ ] 컨테이너 이미지가 서명되고 검증 정책이 적용되어 있는가?

### 6.3 보안 성숙도 모델

조직의 Kubernetes 보안 성숙도를 평가하는 기준입니다.

| 레벨 | 명칭 | 특징 | 주요 도구 |
|------|------|------|----------|
| 1 | 초기 | 기본 RBAC, 이미지 스캔 | kubectl, Trivy |
| 2 | 관리됨 | PSS, Network Policy | Kyverno, Falco |
| 3 | 정의됨 | 이미지 서명, Vault | Cosign, Vault |
| 4 | 측정됨 | 자동화된 감사, SIEM 통합 | Elastic, Splunk |
| 5 | 최적화됨 | 제로트러스트, eBPF 기반 | Cilium, Tetragon |

---

## 관련 포스트

- [이메일 발송 신뢰도 높이기: SendGrid SPF, DKIM, DMARC 설정 완벽 가이드]({% post_url 2025-06-05-Email_Delivery_Trust_Improve_SendGrid_SPF_DKIM_DMARC_Setup_Complete_Guide %})
