---
author: Twodragon
categories:
- security
- devsecops
- kubernetes
category: kubernetes
comments: true
date: 2026-01-15 18:25:00 +0900
description: '클라우드 보안 과정 8기 7주차: Docker 컨테이너 보안(이미지 스캔, Secret 관리, 비루트 실행), Kubernetes
  보안 아키텍처(Pod Security Standards, User Namespaces, Network Policies, RBAC), 최신 K8s
  1.32-1.35+ 보안 기능까지 실무 가이드'
excerpt: Docker/K8s 보안, Pod Security Standards, User Namespaces, 이미지 스캔, 런타임 모니터링
image: /assets/images/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.svg
image_alt: 'Cloud Security Course 8Batch 7Week: Docker and Kubernetes Security Practical
  Guide'
keywords:
- Docker-Security
- Kubernetes-Security
- Container-Security
- Pod-Security-Standards
- User-Namespaces
- Network-Policies
- Trivy
- Falco
- Minikube
- K9s
- DevSecOps
- Image-Scanning
layout: post
original_url: https://twodragon.tistory.com/708
schema_type: Article
tags:
- Docker
- Kubernetes
- Container-Security
- K8s
- Cloud-Security
- DevSecOps
- Minikube
- K9s
- Pod-Security-Standards
- User-Namespaces
title: "\U0001F680 클라우드 보안 과정 8기 7주차: Docker & Kubernetes 보안 실전 가이드 - 컨테이너 보안부터 클러스터
  보안까지"
toc: true
---

## 요약

- **핵심 요약**: Docker/K8s 보안, Pod Security Standards, User Namespaces, 이미지 스캔, 런타임 모니터링
- **주요 주제**: 🚀 클라우드 보안 과정 8기 7주차: Docker & Kubernetes 보안 실전 가이드 - 컨테이너 보안부터 클러스터 보안까지
- **키워드**: Docker, Kubernetes, Container-Security, K8s, Cloud-Security

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">🚀 클라우드 보안 과정 8기 7주차: Docker & Kubernetes 보안 실전 가이드</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span> <span class="category-tag kubernetes">Kubernetes</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Docker</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">Container-Security</span>
      <span class="tag">K8s</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Minikube</span>
      <span class="tag">K9s</span>
      <span class="tag">Pod-Security-Standards</span>
      <span class="tag">User-Namespaces</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>컨테이너 보안 Best Practices</strong>: 이미지 스캔(Trivy, Snyk), Secret 관리(Kubernetes Secrets, External Secrets Operator), 비루트 사용자 실행, 읽기 전용 파일시스템, 최소 권한 원칙</li>
      <li><strong>Kubernetes 보안 아키텍처</strong>: Pod Security Standards(PSS), User Namespaces(Kubernetes 1.33+), Network Policies, RBAC 최소 권한, Bound Service Account Tokens</li>
      <li><strong>Kubernetes 보안 Best Practices</strong>: 이미지 서명 및 검증(Cosign, Docker Content Trust), 런타임 보안 모니터링(Falco, Sysdig), 자동화된 보안 검증(CI/CD 통합), 정기적인 보안 감사</li>
      <li><strong>최신 보안 기능 (2024-2026)</strong>: Kubernetes 1.32-1.35 보안 강화(User Namespaces Beta-by-Default, mTLS Pod Certificates), Kubernetes 1.36+ 예상 기능, Minikube 1.37.0+ 기능, K9s 보안 모범 사례</li>
      <li><strong>Docker/Container/Kubernetes 기본 이해</strong>: Docker 이미지/컨테이너 개념, VM vs Container 비교, Kubernetes 핵심 리소스(Pod, Deployment, Service, Namespace), 컨테이너 격리 원리</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Docker, Kubernetes, Minikube, K9s, Trivy, Snyk, Falco, External Secrets Operator</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 엔지니어, 클라우드 보안 전문가, DevOps 엔지니어, 컨테이너 보안 담당자</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다.

지난 6주차에서는 AWS WAF/CloudFront 보안 아키텍처와 GitHub DevSecOps 실전을 다루었습니다. 이번 **클라우드 보안 과정 8기 7주차**에서는 **Docker & Kubernetes 보안 실전 가이드**를 통해 컨테이너 보안부터 클러스터 보안까지 실무 중심으로 다루고자 합니다.

특히 이번 주에는 **2024-2026년 최신 Kubernetes 보안 기능**과 **실전 보안 사례**를 결합하여, DevSecOps 관점에서 컨테이너 보안을 강화하는 방법을 깊이 있게 다뤄보겠습니다.

본 과정은 **온라인 미팅**으로 진행되며, **'20분 강의 + 5분 휴식'** 사이클로 멘티분들의 집중력을 최대로 유지하며 진행됩니다.

---

### **📅 7주차 타임테이블 (Agenda)**

| 시간 | 주제 | 내용 |
|------|------|------|
| **10:00 - 10:20** | **근황 토크 & 과제 피드백** | 한 주간의 보안 이슈 공유 및 Q&A |
| **10:25 - 10:50** | **Docker/Container/Kubernetes 기본 이해** | Docker 이미지/컨테이너 개념, VM vs Container, Kubernetes 핵심 리소스 |
| **11:00 - 11:25** | **컨테이너 보안 Best Practices** | Docker 이미지 보안, Secret 관리, 비루트 실행, 이미지 스캔(Trivy, Snyk) |
| **11:30 - 11:50** | **Kubernetes 보안 아키텍처 & Best Practices** | Pod Security Standards, User Namespaces, Network Policies, RBAC, 보안 모범 사례 |
| **11:55 - 12:00** | **실습 및 Q&A** | Minikube 보안 환경 구성, 실전 보안 강화 사례 |

---

## 1. Docker/Container/Kubernetes 기본 이해

컨테이너와 Kubernetes를 이해하기 전에 기본 개념을 명확히 하는 것이 중요합니다.

#### **1.1 Docker 기본 개념**

##### **Docker의 핵심 구성 요소**

| 개념 | 설명 | 비유 |
|------|------|------|
| **Image** | 컨테이너 실행에 필요한 파일과 설정을 포함한 템플릿 | 빵을 만드는 레시피 |
| **Container** | 이미지를 기반으로 실행되는 인스턴스 | 레시피로 만든 빵 |
| **Dockerfile** | 이미지를 빌드하기 위한 명령어 스크립트 | 레시피 작성 방법 |
| **Registry** | 이미지를 저장하고 공유하는 저장소 (Docker Hub 등) | 빵 레시피 도서관 |

##### **Docker 구성 요소 관계도**

*Docker의 핵심 구성 요소 관계도는 위 이미지를 참조하세요.*

##### **기본 Docker 명령어**

> **참고**: Docker 기본 명령어는 [Docker 공식 문서](https://docs.docker.com/) 및 [Docker 공식 예제](https://github.com/docker/awesome-compose)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```bash
> # 이미지 다운로드...
> ```



---

## 2. 컨테이너 보안 Best Practices

컨테이너 보안은 DevSecOps의 핵심입니다. 이미지 빌드 단계부터 런타임까지 전 과정에서 보안을 고려해야 합니다.

#### **2.1 Docker 이미지 보안**

##### **컨테이너 보안 레이어 (Defense in Depth)**

컨테이너 보안은 여러 레이어로 구성된 Defense in Depth 전략을 통해 강화됩니다:

<figure>
  
  <figcaption>Docker의 핵심 구성 요소: Dockerfile로 이미지를 빌드하고, Registry에 저장하며, Container로 실행</figcaption>
</figure>

##### **최소 권한 원칙 적용**

*최소 권한 원칙 적용: 비루트 사용자, 읽기 전용 파일시스템, Capabilities 제거, Secret 관리*

| 보안 항목 | 취약한 예시 | 보안 강화 예시 | 설명 |
|----------|-----------|--------------|------|
| **사용자 권한** | `USER root` | `USER 1000:1000` | 비루트 사용자로 실행 |
| **파일시스템** | 읽기/쓰기 가능 | `readOnlyRootFilesystem: true` | 읽기 전용 파일시스템 |
| **Capabilities** | 모든 권한 | `capabilities.drop: ALL` | 불필요한 권한 제거 |
| **환경 변수** | 평문 Secret | Kubernetes Secrets | Secret 관리 도구 사용 |

> **참고**: Docker 보안 모범 사례는 [Docker 보안 문서](https://docs.docker.com/engine/security/) 및 [OWASP Docker 보안 체크리스트](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```dockerfile
> # 보안 강화 Dockerfile 예시...
> ```



#### **2.2 Secret 관리**

##### **Kubernetes Secrets vs External Secrets Operator**

| 방식 | 설명 | 장점 | 단점 |
|------|------|------|------|
| **Kubernetes Secrets** | 네이티브 Secret 리소스 | 간단한 설정 | Base64 인코딩(암호화 아님) |
| **External Secrets Operator** | 외부 Secret Store 통합 | 중앙 관리, 자동 동기화 | 추가 Operator 필요 |
| **Sealed Secrets** | 암호화된 Secret | Git에 안전하게 저장 가능 | 추가 도구 필요 |

##### **Secret 관리 방식 비교**

*Secret 관리 방식 비교: Kubernetes Secrets, External Secrets Operator, Sealed Secrets*

> **참고**: External Secrets Operator 설정은 [External Secrets Operator 문서](https://external-secrets.io/) 및 [AWS Secrets Manager 통합](https://external-secrets.io/latest/provider/aws-secrets-manager/)을 참조하세요.

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://github.com/aws-samples/integrate-httpapi-with-cloudfront-and-waf)를 참조하세요. 네트워크 시나리오** | AWS WAF와 전체적인 네트워크 보안 구성 | [시청하기](https://youtu.be/r84IuPv_4TI) |

### 외부 참고 자료

- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Kubernetes 보안 체크리스트](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Minikube 공식 문서](https://minikube.sigs.k8s.io/docs/)
- [K9s 공식 문서](https://k9scli.io/)
- [Trivy GitHub 저장소](https://github.com/aquasecurity/trivy)
- [External Secrets Operator 문서](https://external-secrets.io/)

---

<div class="post-metadata">
  <div class="metadata-item">
    <strong>마지막 업데이트</strong>
    <span>2026-01-15</span>
  </div>
  <div class="metadata-item">
    <strong>작성 기준</strong>
    <span>클라우드 보안 과정 8기 7주차 강의 자료</span>
  </div>
</div>

<!-- quality-upgrade:v1 -->
## Executive Summary
이 문서는 운영자가 즉시 실행할 수 있는 보안 우선 실행 항목과 검증 포인트를 중심으로 재정리했습니다.

### 위험 스코어카드
| 영역 | 현재 위험도 | 영향도 | 우선순위 |
|---|---|---|---|
| 공급망/의존성 | Medium | High | P1 |
| 구성 오류/권한 | Medium | High | P1 |
| 탐지/가시성 공백 | Low | Medium | P2 |

### 운영 개선 지표
| 지표 | 현재 기준 | 목표 | 검증 방법 |
|---|---|---|---|
| 탐지 리드타임 | 주 단위 | 일 단위 | SIEM 알림 추적 |
| 패치 적용 주기 | 월 단위 | 주 단위 | 변경 티켓 감사 |
| 재발 방지율 | 부분 대응 | 표준화 | 회고 액션 추적 |

### 실행 체크리스트
- [ ] 핵심 경고 룰을 P1/P2로 구분하고 온콜 라우팅을 검증한다.
- [ ] 취약점 조치 SLA를 서비스 등급별로 재정의한다.
- [ ] IAM/시크릿/네트워크 변경 이력을 주간 기준으로 리뷰한다.
- [ ] 탐지 공백 시나리오(로그 누락, 파이프라인 실패)를 월 1회 리허설한다.
- [ ] 경영진 보고용 핵심 지표(위험도, 비용, MTTR)를 월간 대시보드로 고정한다.

### 시각 자료
![Post Visual](/assets/images/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.svg)

<!-- quality-upgrade:v2 -->
### 교차 참조 및 후속 학습
- 관련 분석: [{% post_url 2026-02-12-Tech_Security_Weekly_Digest_AI_Cloud_Security_Agent %}]

### 추가 비교 표
| 항목 | 최소 기준 | 권장 기준 |
|---|---|---|
| 로그 보존 기간 | 30일 | 90일 이상 |
| 취약점 재검증 | 월 1회 | 주 1회 |
| 재해 복구 점검 | 분기 1회 | 월 1회 |

