---
layout: post
title: "클라우드 시큐리티 과정 7기 - 7주차: Docker 및 Kubernetes 이해"
date: 2025-05-30 00:04:58 +0900
categories: [kubernetes]
tags: [Docker, Kubernetes, Container, K8s, Cloud-Security, DevSecOps]
excerpt: "Docker 및 Kubernetes 기초와 보안 Best Practices 정리"
original_url: https://twodragon.tistory.com/686
image: /assets/images/2025-05-30-Cloud_Security_Course_7Batch_-_7Week_Docker_and_Kubernetes.svg
image_alt: "Cloud Security Course 7Batch 7Week: Docker and Kubernetes Understanding"
toc: true
description: "Docker 기초(이미지, 컨테이너, Dockerfile), Kubernetes 아키텍처(Control Plane, Node, Pod), 컨테이너 보안 Best Practices, 런타임 보안(Trivy, Falco), 2025년 업데이트까지 실무 중심 정리."
keywords: [Docker, Kubernetes, Container, K8s, Cloud-Security, DevSecOps]
author: "Yongho Ha"
certifications: [ckad, cka]
schema_type: Article
---

## 📋 포스팅 요약

> **제목**: 클라우드 시큐리티 과정 7기 - 7주차: Docker 및 Kubernetes 이해

> **카테고리**: kubernetes

> **태그**: Docker, Kubernetes, Container, K8s, Cloud-Security, DevSecOps

> **핵심 내용**: 
> - Docker 및 Kubernetes 기초와 보안 Best Practices 정리

> **주요 기술/도구**: Docker, Kubernetes, Security, DevSecOps, kubernetes

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
    <span class="summary-value">클라우드 시큐리티 과정 7기 - 7주차: Docker 및 Kubernetes 이해</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag devops">Kubernetes</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Docker</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">Container</span>
      <span class="tag">K8s</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">DevSecOps</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>Docker 기초</strong>: 이미지/컨테이너/Dockerfile 개념, 기본 Docker 명령어(pull, run, ps, logs, stop, rm), Registry(Docker Hub), 컨테이너 격리 및 실행 환경</li>
      <li><strong>Kubernetes 아키텍처</strong>: Control Plane(API Server, etcd, Scheduler, Controller Manager), Node(kubelet, Pods), 주요 리소스(Pod, Deployment, Service, ConfigMap, Secret, Namespace)</li>
      <li><strong>컨테이너 보안 Best Practices</strong>: 최소 권한 원칙, 이미지 스캔(Trivy, Snyk), Secret 관리(Kubernetes Secrets, External Secrets Operator), 비루트 사용자 실행, 읽기 전용 파일시스템</li>
      <li><strong>런타임 보안</strong>: Trivy 취약점 스캔, Falco 이상 행위 탐지, Pod Security Standards 적용, Network Policy 구현, Minikube/K9s 실습 가이드</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Docker, Kubernetes, Minikube, K9s, Trivy</span>
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

<img src="{{ '/assets/images/2025-05-30-Cloud_Security_Course_7Batch_-_7Week_Docker_and_Kubernetes_image.png' | relative_url }}" alt="Cloud Security Course 7Batch 7Week: Docker and Kubernetes Understanding" loading="lazy" class="post-image">

## Executive Summary

컨테이너 기술은 현대 클라우드 인프라의 핵심이며, Docker와 Kubernetes는 가장 널리 사용되는 표준입니다. 본 문서는 컨테이너 보안의 전체 생명주기(Build → Ship → Run)를 다루며, 2025년 최신 보안 업데이트와 실무 적용 방법을 제공합니다.

### 주요 보안 위험

| 위험 | 영향도 | 발생 빈도 | 비즈니스 영향 |
|------|--------|-----------|--------------|
| 취약한 컨테이너 이미지 | 높음 | 매우 높음 | 데이터 유출, 서비스 중단 |
| 과도한 권한 실행 | 높음 | 높음 | 권한 상승, 호스트 침투 |
| 비암호화 Secret 관리 | 높음 | 중간 | 자격 증명 노출, 무단 접근 |
| 네트워크 정책 부재 | 중간 | 높음 | 측면 이동, 내부 정찰 |
| 런타임 모니터링 부족 | 중간 | 높음 | 공격 탐지 지연, 사고 대응 실패 |

### 권장 보안 통제

1. **Build Phase**: 이미지 스캔 자동화, Multi-stage 빌드, Distroless 이미지
2. **Ship Phase**: 이미지 서명 검증, Registry 접근 제어, 취약점 정책 적용
3. **Run Phase**: Pod Security Standards, Network Policy, Runtime 모니터링 (Falco)
4. **Governance**: RBAC, Admission Controller, Audit Logging

### 즉시 적용 가능한 액션 아이템

- [ ] 모든 프로덕션 이미지에 Trivy 스캔 통합
- [ ] Pod Security Standards (Restricted) 적용
- [ ] Network Policy로 기본 Deny-All 구현
- [ ] Falco 런타임 탐지 규칙 배포
- [ ] User Namespaces 활성화 (Kubernetes 1.32+)

## 서론

안녕하세요, **Twodragon**입니다. 이번 포스팅에서는 컨테이너 및 Kubernetes 보안에 대해 실무 중심으로 정리합니다.

2025년 Docker와 Kubernetes는 여전히 클라우드 네이티브 애플리케이션의 핵심 기술이며, 보안은 더욱 중요해지고 있습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- 클라우드 시큐리티 과정 7기 - 7주차: Docker 및 Kubernetes 이해의 핵심 내용 및 실무 적용 방법
- 2025-2026년 최신 트렌드 및 업데이트 사항
- 실전 사례 및 문제 해결 방법
- 보안 모범 사례 및 권장 사항

## 1. Docker 기초 이해

### 1.1 Docker란?

Docker는 애플리케이션을 **컨테이너**라는 격리된 환경에서 실행할 수 있게 해주는 플랫폼입니다. 컨테이너는 애플리케이션과 그 종속성을 함께 패키징하여 어디서든 일관되게 실행할 수 있습니다.

### 1.2 Docker의 핵심 개념

| 개념 | 설명 |
|------|------|
| **Image** | 컨테이너 실행에 필요한 파일과 설정을 포함한 템플릿 |
| **Container** | 이미지를 기반으로 실행되는 인스턴스 |
| **Dockerfile** | 이미지를 빌드하기 위한 명령어 스크립트 |
| **Registry** | 이미지를 저장하고 공유하는 저장소 (Docker Hub 등) |

### 1.3 기본 Docker 명령어

> **참고**: Docker 기본 명령어 관련 내용은 [Docker 공식 문서](https://docs.docker.com/) 및 [Docker 공식 예제](https://kubernetes.io/docs/)를 참조하세요.
>
> ```bash
> # 이미지 다운로드...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 1.4 Dockerfile 작성 Best Practices

안전하고 효율적인 Dockerfile 작성 원칙입니다.

#### Multi-stage Build로 이미지 크기 최소화

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```dockerfile
> # Build stage...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### 보안 강화 Dockerfile 예시

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```dockerfile
> # 최소 베이스 이미지 사용...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 1.5 Docker 보안 검증 체크리스트

| 항목 | 검증 방법 | 위험도 |
|------|-----------|--------|
| 베이스 이미지 출처 확인 | `docker history <image>` | 높음 |
| 취약점 스캔 | `trivy image <image>` | 높음 |
| 비루트 사용자 실행 | Dockerfile에서 `USER` 확인 | 높음 |
| Secrets 하드코딩 확인 | 코드 리뷰, git-secrets | 매우 높음 |
| 불필요한 패키지 제거 | 이미지 크기 및 레이어 분석 | 중간 |
| Health check 구현 | `HEALTHCHECK` 지시어 확인 | 중간 |

## 2. Kubernetes 핵심 개념

### 2.1 Kubernetes 아키텍처

Kubernetes는 컨테이너화된 워크로드와 서비스를 관리하기 위한 **오케스트레이션 플랫폼**입니다.

<!-- 전체 코드는 외부 참조 링크를 확인하세요. --> API
    CP --> ETCD
    CP --> SCHED
    CP --> CM

    CP --> N1["Node 1"]
    CP --> N2["Node 2"]
    CP --> N3["Node 3"]

    N1 --> K1["kubelet"]
    N1 --> P1["Pods"]

    N2 --> K2["kubelet"]
    N2 --> P2["Pods"]

    N3 --> K3["kubelet"]
    N3 --> P3["Pods"]


```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
> # EncryptionConfiguration...
> ```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
> apiVersion: apps/v1...
> ```
# example omitted: see reference link
```yaml
> apiVersion: apps/v1...
> ```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Namespace별 네트워크 격리

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> apiVersion: networking.k8s.io/v1...
> ```
# example omitted: see reference link
```bash
 # Trivy를 사용한 이미지 스캔
 trivy image nginx:latest
 ```
# example omitted: see reference link
```yaml
> ...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Cosign 이미지 서명 및 검증

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```bash
> # 1. 키 생성...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 3.2 런타임 보안

> **참고**: Kubernetes Security Context 관련 내용은 [Kubernetes Security Context 문서](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) 및 [Kubernetes 예제](https://kubernetes.io/docs/)를 참조하세요.
>
> ```yaml
> # SecurityContext 설정 예시...
> ```
# example omitted: see reference link
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

#### AppArmor 프로파일 적용

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

#### Seccomp 프로파일 적용

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
 name: deny-all-ingress
spec:
 podSelector: {}
 policyTypes:
 - Ingress
 ingress: []
```

#### 계층별 네트워크 정책 예시

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> ---...
> ```
# example omitted: see reference link
```bash
# etcd 암호화 확인
kubectl get secrets -n kube-system | grep encryption

# Secret 생성
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password='$tr0ng_p@ssw0rd' \
  --namespace=production
```

#### External Secrets Operator

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> apiVersion: external-secrets.io/v1beta1...
> ```
# example omitted: see reference link
```bash
# Sealed Secrets Controller 설치
kubectl apply -f https://kubernetes.io/docs/

# Secret 암호화
kubeseal --format=yaml < secret.yaml > sealed-secret.yaml

# Git에 안전하게 커밋
git add sealed-secret.yaml
git commit -m "Add encrypted secret"
```
# example omitted: see reference link
```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 클러스터 시작
minikube start --driver=docker --cpus=2 --memory=4096
```
# example omitted: see reference link
```bash
# 설치
brew install k9s

# 실행
k9s
```
# example omitted: see reference link
```bash
> # 1. 취약한 애플리케이션 배포...
> ```
# example omitted: see reference link
```yaml
# kubelet 설정에서 Fine-grained 인가 활성화
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
featureGates:
  KubeletFineGrainedAuthz: true
authorization:
  mode: Webhook
```
# example omitted: see reference link
```bash
# 인증서 기반 credential 추적 확인
kubectl get certificatesigningrequests -o wide

# Audit 로그에서 credential ID 확인
kubectl logs -n kube-system kube-apiserver-* | grep credentialID
```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```yaml
> # EKS 1.32+ 에서의 익명 인증 설정...
> ```
# example omitted: see reference link
```yaml
> # Deprecated (사용 자제)...
> ```
# example omitted: see reference link
```bash
# Helm으로 Falco 설치
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm repo update

helm install falco falcosecurity/falco \
  --namespace falco \
  --create-namespace \
  --set driver.kind=modern_ebpf \
  --set tty=true
```

#### Falco 커스텀 규칙 예시

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```yaml
> # custom-rules.yaml...
> ```
# example omitted: see reference link
```yaml
> # Audit Policy for Personal Data Processing...
> ```
# example omitted: see reference link
```yaml
> apiVersion: v1...
> ```
# example omitted: see reference link
```mermaid
> graph TB...
> ```
# example omitted: see reference link
```

### 9.2 컨테이너 공격 시나리오 및 방어 계층

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->|Mitigated by| D1
    A1 -->|Blocked by| D2

    A2 -->|Protected by| D3
    A2 -->|Isolated by| D4

    A3 -->|Monitored by| D5

    D1 --> SECURE[Secure Workload]
    D2 --> SECURE
    D3 --> SECURE
    D4 --> SECURE
    D5 --> SECURE


```
# example omitted: see reference link
```bash
> # 1. Privileged Pod 생성 탐지...
> ```
# example omitted: see reference link
```bash
# Falco 로그에서 컨테이너 탈출 시도 추출
cat /var/log/falco/events.txt | \
  grep -E "(Container Drift Detected|Write Below Root|Contact K8S API)" | \
  jq -r '[.time, .rule, .output_fields.container_name, .output_fields.proc_cmdline] | @csv'
```

### 10.2 비정상 네트워크 활동 탐지

#### kubectl 기반 네트워크 분석

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```bash
> # 1. Service 없이 직접 통신하는 Pod 탐지...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

### 10.3 Secret 접근 이상 탐지

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://kubernetes.io/docs/)를 참조하세요.
> 
> ```bash
> # 1. Secret 접근 Audit Log 분석...
> ```
# example omitted: see reference link
```bash
> # 1. Pod 상태 확인...
> ```
# example omitted: see reference link
```bash
> # 1. 현재 적용된 Network Policy 확인...
> ```
# example omitted: see reference link
```bash
> # 1. ImagePullBackOff 이벤트 확인...
> ```

<!-- 전체 코드는 외부 참조 링크를 확인하세요. -->

## 12. 종합 레퍼런스

### 12.1 공식 문서

| 리소스 | URL | 설명 |
|--------|-----|------|
| Kubernetes 공식 문서 | https://kubernetes.io/docs/ | K8s 전체 레퍼런스 |
| Docker 공식 문서 | https://docs.docker.com/ | Docker 엔진 및 Compose |
| CIS Kubernetes Benchmark | https://www.cisecurity.org/benchmark/kubernetes | 보안 베스트 프랙티스 |
| OWASP Kubernetes Top 10 | https://owasp.org/www-project-kubernetes-top-ten/ | 주요 보안 위협 |
| Falco 문서 | https://falco.org/docs/ | 런타임 보안 |
| Trivy 문서 | https://aquasecurity.github.io/trivy/ | 이미지 스캔 |

### 12.2 보안 도구

| 도구 | 용도 | 라이센스 | 추천도 |
|------|------|----------|--------|
| **Trivy** | 이미지/파일시스템 취약점 스캔 | Apache 2.0 | ⭐⭐⭐⭐⭐ |
| **Falco** | 런타임 이상 행위 탐지 | Apache 2.0 | ⭐⭐⭐⭐⭐ |
| **OPA Gatekeeper** | Policy as Code | Apache 2.0 | ⭐⭐⭐⭐ |
| **Kyverno** | Kubernetes Native Policy | Apache 2.0 | ⭐⭐⭐⭐ |
| **Snyk** | 의존성 취약점 스캔 | Freemium | ⭐⭐⭐⭐ |
| **kube-bench** | CIS Benchmark 검사 | Apache 2.0 | ⭐⭐⭐⭐ |
| **kube-hunter** | 클러스터 침투 테스트 | Apache 2.0 | ⭐⭐⭐ |
| **Cosign** | 이미지 서명/검증 | Apache 2.0 | ⭐⭐⭐⭐ |

### 12.3 학습 리소스

#### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| **Docker 보안** | 컨테이너 보안, 이미지 스캔, Secret 관리 | [수강하기](https://edu.2twodragon.com/courses/docker-security) |
| **Kubernetes 보안** | 클러스터 보안, RBAC, Network Policies | [수강하기](https://edu.2twodragon.com/courses/kubernetes-security) |
| **DevSecOps 실전** | DevSecOps 전략, 보안 자동화 | [수강하기](https://edu.2twodragon.com/courses/devsecops) |

#### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| **AWS WAF 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

#### 커뮤니티

- **Kubernetes Slack**: https://slack.k8s.io/
- **CNCF Slack - #falco**: https://cloud-native.slack.com/
- **Reddit - r/kubernetes**: https://www.reddit.com/r/kubernetes/

### 12.4 인증 자격증 가이드

| 자격증 | 난이도 | 준비 기간 | 비용 | 추천 대상 |
|--------|--------|-----------|------|-----------|
| **CKA** (Certified Kubernetes Administrator) | 중상 | 2-3개월 | $395 | K8s 관리자, DevOps 엔지니어 |
| **CKAD** (Certified Kubernetes Application Developer) | 중 | 1-2개월 | $395 | 개발자, 애플리케이션 배포 담당자 |
| **CKS** (Certified Kubernetes Security Specialist) | 상 | 3-4개월 | $395 | 보안 전문가, DevSecOps |
| **Docker Certified Associate** | 중하 | 1개월 | $195 | Docker 초급자 |

**CKS 시험 준비 팁:**
1. CKA 선수 자격증 필수
2. Trivy, Falco, OPA 실습 필수
3. Network Policy 및 RBAC 숙지
4. kube-bench, kube-hunter 도구 활용

## 마무리

이번 주차에서는 Docker와 Kubernetes의 기본 개념부터 보안 모범 사례, 그리고 2025년 최신 Kubernetes 보안 업데이트까지 다뤘습니다. 다음 주차에서는 **CI/CD와 Kubernetes 보안**에 대해 더 깊이 있게 다룰 예정입니다.

> **다음 주차 예고:** CI/CD 파이프라인에서의 보안 통합과 Kubernetes 보안 도구 실습

### 즉시 실행 가능한 액션 아이템

- [ ] **Week 1**: Trivy를 CI/CD 파이프라인에 통합
- [ ] **Week 2**: Falco DaemonSet 배포 및 알림 설정
- [ ] **Week 3**: Network Policy 기본 Deny-All 적용
- [ ] **Week 4**: Pod Security Standards (Restricted) 활성화
- [ ] **Month 2**: User Namespaces 활성화 (Kubernetes 1.32+)
- [ ] **Month 3**: External Secrets Operator 도입

---

## 관련 자료

### 온라인 강의 (edu.2twodragon.com)

| 과정 | 설명 | 링크 |
|------|------|------|
| **Docker 보안** | 컨테이너 보안, 이미지 스캔, Secret 관리 | [수강하기](https://edu.2twodragon.com/courses/docker-security) |
| **Kubernetes 보안** | 클러스터 보안, RBAC, Network Policies | [수강하기](https://edu.2twodragon.com/courses/kubernetes-security) |
| **DevSecOps 실전** | DevSecOps 전략, 보안 자동화 | [수강하기](https://edu.2twodragon.com/courses/devsecops) |

### YouTube 영상

| 주제 | 설명 | 링크 |
|------|------|------|
| **AWS WAF 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

---

📚 **외부 참고 자료:**
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Docker 공식 문서](https://docs.docker.com/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
- [OWASP Kubernetes Top 10](https://owasp.org/www-project-kubernetes-top-ten/)
- [Falco Runtime Security](https://falco.org/docs/)
- [Aqua Security Trivy](https://aquasecurity.github.io/trivy/)
- [MITRE ATT&CK for Containers](https://attack.mitre.org/matrices/enterprise/containers/)
- [NSA/CISA Kubernetes Hardening Guidance](https://www.nsa.gov/Press-Room/News-Highlights/Article/Article/2716980/nsa-cisa-release-kubernetes-hardening-guidance/)
