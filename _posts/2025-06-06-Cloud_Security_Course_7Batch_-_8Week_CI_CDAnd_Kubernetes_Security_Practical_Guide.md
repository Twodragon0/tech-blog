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

## 📋 포스팅 요약

> **제목**: 클라우드 시큐리티 과정 7기 - 8주차: CI/CD와 Kubernetes 보안 실전 가이드

> **카테고리**: kubernetes

> **태그**: CI/CD, Kubernetes, Security, DevSecOps, GitOps, Pipeline-Security

> **핵심 내용**: 
> - CI/CD 파이프라인 보안 및 Kubernetes 클러스터 보안 실전 가이드

> **주요 기술/도구**: Kubernetes, Security, DevSecOps, Security, kubernetes

> **대상 독자**: 클라우드 보안 전문가, DevOps 엔지니어, 보안 담당자

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


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

> **참고**: GitHub Actions 보안 설정 관련 내용은 [GitHub Actions 보안 가이드](https://docs.https://kubernetes.io/docs/) 및 [GitHub Actions 예제](https://kubernetes.io/docs/)를 참조하세요.

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 2.2 ServiceAccount 보안

> **참고**: Kubernetes ServiceAccount 보안 관련 내용은 [Kubernetes ServiceAccount 문서](https://kubernetes.io/docs/concepts/security/service-accounts/) 및 [Kubernetes RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)를 참조하세요.
>
> ```yaml
> # 전용 ServiceAccount 생성...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

## 3. Pod Security Standards (PSS)

### 3.1 Namespace 레벨 보안 정책

> **참고**: Pod Security Standards 관련 내용은 [Kubernetes Pod Security Standards 문서](https://kubernetes.io/docs/concepts/security/pod-security-standards/) 및 [Kubernetes 예제](https://kubernetes.io/docs/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

```yaml
# example omitted: see reference link
```

### 3.2 보안 컨텍스트 모범 사례

> **참고**: Kubernetes Security Context 관련 내용은 [Kubernetes Security Context 문서](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) 및 [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)를 참조하세요.
>
> ```yaml
> apiVersion: apps/v1...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

## 4. Network Policy 구현

### 4.1 기본 거부 정책

> **참고**: Kubernetes Network Policy 관련 내용은 [Kubernetes Network Policy 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/) 및 [Network Policy 예제](https://kubernetes.io/docs/)를 참조하세요.
>
> ```yaml
> # 모든 인그레스/이그레스 트래픽 차단 (기본)...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 4.2 필요한 트래픽만 허용

> **참고**: Kubernetes Network Policy 관련 내용은 [Kubernetes Network Policy 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/) 및 [Network Policy 예제](https://kubernetes.io/docs/)를 참조하세요.
>
> ```yaml
> # Frontend -> Backend 통신만 허용...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

## 5. Secret 관리

### 5.1 External Secrets Operator

> **참고**: External Secrets Operator 관련 내용은 [External Secrets Operator GitHub 저장소](https://kubernetes.io/docs/) 및 [External Secrets Operator 문서](https://external-secrets.io/latest/)를 참조하세요.
>
> ```yaml
> # AWS Secrets Manager와 연동...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 5.2 Sealed Secrets (GitOps 환경)

> **참고**: Sealed Secrets 관련 내용은 [Sealed Secrets GitHub 저장소](https://kubernetes.io/docs/) 및 [Sealed Secrets 문서](https://sealed-secrets.netlify.app/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

```bash
# example omitted: see reference link
```

## 6. 이미지 보안

### 6.1 Admission Controller로 이미지 검증

> **참고**: Kyverno를 통한 이미지 검증 관련 내용은 [Kyverno GitHub 저장소](https://kubernetes.io/docs/) 및 [Kyverno 공식 문서](https://kyverno.io/docs/)를 참조하세요.
>
> ```yaml
> # Kyverno 정책: 서명된 이미지만 허용...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 6.2 취약점이 있는 이미지 차단


> **참고**: Kyverno를 통한 취약점 이미지 차단 관련 내용은 [Kyverno GitHub 저장소](https://kubernetes.io/docs/) 및 [Kyverno 공식 문서](https://kyverno.io/docs/)를 참조하세요.
>
> ```yaml
> # Kyverno 정책: Critical 취약점 차단...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->


## 7. 런타임 보안

### 7.1 Falco 규칙 설정

> **참고**: Falco 런타임 보안 모니터링 관련 내용은 [Falco 공식 저장소](https://kubernetes.io/docs/) 및 [Falco 문서](https://falco.org/docs/)를 참조하세요.
>
> ```yaml
> # 의심스러운 활동 탐지 규칙...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

> **참고**: Kubernetes Audit 로그 분석 관련 내용은 [Kubernetes Audit 문서](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)를 참조하세요.
>
> ```bash
> # Audit 로그에서 credential 추적 예시...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### User Namespaces Support (Linux Kernel 6.3+)

User Namespaces는 컨테이너 내 root 사용자를 호스트의 비권한 사용자로 매핑하여 컨테이너 탈출 공격의 위험을 크게 감소시킵니다:

워크로드 격리를 크게 강화하는 User Namespaces가 정식 지원됩니다.

> **참고**: Kubernetes User Namespaces 관련 내용은 [Kubernetes User Namespaces 문서](https://kubernetes.io/docs/concepts/security/user-namespaces/) 및 [Kubernetes 예제](https://kubernetes.io/docs/)를 참조하세요.
>
> ```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**User Namespace 보안 효과:**
| 공격 시나리오 | 기존 | User Namespace 적용 |
|---------------|------|---------------------|
| 컨테이너 탈출 후 root 권한 | 호스트 root 획득 가능 | 비특권 사용자로 제한 |
| /proc, /sys 접근 | 민감 정보 노출 | 접근 권한 격리 |
| 다른 컨테이너 침해 | 가능 | 격리로 차단 |

#### Pod Certificates for mTLS (KEP-4317)

kubelet이 Pod용 인증서를 자동으로 요청하고 마운트합니다.

> **참고**: Kubernetes Pod Certificates 관련 내용은 [Kubernetes Certificate Signing Requests 문서](https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/) 및 [Kubernetes 예제](https://kubernetes.io/docs/)를 참조하세요.
>
> ```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**자동 인증서 Rotation:**
> **참고**: Kubernetes 인증서 관리 관련 내용은 [Kubernetes Certificate Signing Requests 문서](https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/)를 참조하세요.
>
> ```yaml
> # CertificateSigningRequest 자동 생성 및 갱신...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 8.2 EKS 1.32 Anonymous Authentication 제한

Amazon EKS 1.32부터 익명 인증이 health check endpoint로 제한됩니다.

> **참고**: Amazon EKS 보안 관련 내용은 [Amazon EKS 문서](https://docs.aws.amazon.com/eks/latest/userguide/) 및 [EKS 보안 모범 사례](https://aws.github.io/aws-eks-best-practices/security/docs/)를 참조하세요.
>
> ```yaml
> # EKS 1.32+ 익명 접근 허용 endpoint...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 8.3 Deprecated 기능 및 마이그레이션

> **참고**: Kubernetes Deprecated 기능 관련 내용은 [Kubernetes Deprecation Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)를 참조하세요.
>
> ```yaml
> # DEPRECATED: ServiceAccount의 enforce-mountable-secrets annotation...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # GitHub Actions: 써드파티 액션 SHA 고정...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # Kubernetes Audit Policy: 배포 활동 감시...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # Kyverno Policy: 특권 컨테이너 차단...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**탐지 쿼리 (Falco)**:

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

```yaml
# example omitted: see reference link
```

### 12.2 Kubernetes 공격 기법 매핑

#### T1078.004 - Valid Accounts: Cloud Accounts

**공격 시나리오**:
공격자가 유출된 ServiceAccount 토큰을 사용하여 클러스터에 접근합니다.

**방어 대책**:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # ServiceAccount 토큰 자동 마운트 비활성화...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # .github/workflows/oidc-deploy.yml...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**AWS IAM Role 설정**:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 13.2 Secret Scanning 자동화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # .github/workflows/secret-scan.yml...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

**커스텀 Gitleaks 설정** (`.gitleaks.toml`):

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```toml
> title = "Custom Gitleaks Configuration"...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 13.3 SAST/DAST 통합

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # .github/workflows/sast-dast.yml...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

## 14. Kubernetes 런타임 보안 (Advanced)

### 14.1 Falco 고급 규칙

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # /etc/falco/falco_rules.local.yaml...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 14.2 Admission Controller 심화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # Kyverno: 이미지 출처 제한...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # Kyverno: 리소스 쿼터 자동 적용...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # OPA Gatekeeper: 네임스페이스별 레이블 강제...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```
> # Kubernetes Audit Log Query (Elasticsearch)...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

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

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # ISMS-P 2.8.2.2 - PR 보안 검사 자동화...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 16.2 금융권 DevSecOps 규제

**금융보안원 DevSecOps 보안 가이드라인** (2024년 개정):

| 항목 | 요구사항 | 구현 방법 |
|------|----------|-----------|
| **이중 인증** | 프로덕션 배포 시 2인 이상 승인 | GitHub Environments + Required Reviewers |
| **변경 추적** | 모든 배포 이력 90일 이상 보관 | Audit Logs + S3 장기 보관 |
| **롤백 절차** | 5분 이내 이전 버전 복구 가능 | Blue/Green Deployment + ArgoCD Rollback |
| **접근 제어** | 프로덕션 환경 접근 IP 제한 | VPN + AWS Security Groups |

**금융권 배포 파이프라인 예시**:

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # .github/workflows/fintech-deploy.yml...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```markdown
> # CI/CD 및 Kubernetes 보안 현황 (2025년 6월)...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 17.2 분기별 ROI 보고서

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

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
   - [GitHub Actions Security Guides](https://docs.https://kubernetes.io/docs/)
   - [OWASP DevSecOps Guideline](https://owasp.org/www-project-devsecops-guideline/)
   - [CNCF Security Whitepaper](https://kubernetes.io/docs/)
   - [SLSA Framework (Supply Chain Levels for Software Artifacts)](https://slsa.dev/)

3. **Security Tools**
   - [Falco Runtime Security](https://falco.org/docs/)
   - [Kyverno Policy Engine](https://kyverno.io/docs/)
   - [Trivy Vulnerability Scanner](https://aquasecurity.github.io/trivy/)
   - [Gitleaks Secret Detection](https://kubernetes.io/docs/)
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
