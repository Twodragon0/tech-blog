---
layout: post
title: "🚀 클라우드 보안 과정 8기 7주차: Docker & Kubernetes 보안 실전 가이드 - 컨테이너 보안부터 클러스터 보안까지"
date: 2026-01-15 18:25:00 +0900
categories: [security, devsecops, kubernetes]
tags: [Docker, Kubernetes, Container-Security, K8s, Cloud-Security, DevSecOps, Minikube, K9s, Pod-Security-Standards, User-Namespaces]
excerpt: "Docker/K8s 보안, Pod Security Standards, User Namespaces, 이미지 스캔, 런타임 모니터링"
description: "클라우드 보안 과정 8기 7주차: Docker 컨테이너 보안(이미지 스캔, Secret 관리, 비루트 실행), Kubernetes 보안 아키텍처(Pod Security Standards, User Namespaces, Network Policies, RBAC), 최신 K8s 1.32-1.35+ 보안 기능까지 실무 가이드"
keywords: [Docker-Security, Kubernetes-Security, Container-Security, Pod-Security-Standards, User-Namespaces, Network-Policies, Trivy, Falco, Minikube, K9s, DevSecOps, Image-Scanning]
author: Twodragon
comments: true
original_url: https://twodragon.tistory.com/708
image: /assets/images/2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide.svg
image_alt: "Cloud Security Course 8Batch 7Week: Docker and Kubernetes Security Practical Guide"
toc: true
schema_type: Article
category: kubernetes
---

{% include ai-summary-card.html
  title='🚀 클라우드 보안 과정 8기 7주차: Docker &amp; Kubernetes 보안 실전 가이드 - 컨테이너 보안부터 클러스터 보안까지'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span> <span class="category-tag devops">쿠버네티스</span>'
  tags_html='<span class="tag">Docker</span> <span class="tag">Kubernetes</span> <span class="tag">Container-Security</span> <span class="tag">K8s</span> <span class="tag">Cloud-Security</span> <span class="tag">DevSecOps</span> <span class="tag">Minikube</span> <span class="tag">K9s</span>'
  highlights_html='<li><strong>포인트 1</strong>: Docker/K8s 보안, Pod Security Standards, User Namespaces, 이미지 스캔, 런타임 모니터링</li> <li><strong>포인트 2</strong>: 실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다</li> <li><strong>포인트 3</strong>: 운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다</li>'
  period='2026-01-15 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

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

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```bash
> # 이미지 다운로드...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```bash
> # 이미지 다운로드 [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 이미지 다운로드
docker pull nginx:latest

# 컨테이너 실행
docker run -d -p 8080:80 --name my-nginx nginx:latest

# 실행 중인 컨테이너 확인
docker ps

# 컨테이너 로그 확인
docker logs my-nginx

# 컨테이너 중지
docker stop my-nginx

# 컨테이너 삭제
docker rm my-nginx


```
-->
-->
-->

#### **1.2 Container 이해**

##### **VM vs Container 비교**

![VM vs Container 아키텍처 비교](/assets/images/diagrams/vm_vs_container_comparison.png)

*가상머신과 컨테이너의 차이: VM은 전체 OS를 포함하지만, Container는 호스트 커널을 공유하여 경량화*

| 항목 | 가상머신(VM) | 컨테이너 |
|------|------------|---------|
| **실행 단위** | 전체 OS 포함 | 앱 + 라이브러리 |
| **성능** | 무겁고 느림 | 경량, 빠름 |
| **실행 환경** | 독립적 커널 | 호스트 커널 공유 |
| **사용 목적** | 레거시 시스템, 완전 격리 | 마이크로서비스, DevOps |
| **리소스 사용** | 높음 (GB 단위) | 낮음 (MB 단위) |
| **시작 시간** | 느림 (분 단위) | 빠름 (초 단위) |

##### **컨테이너 격리 원리**

*컨테이너 격리 원리: Linux 커널의 Namespaces, Cgroups, Union File Systems를 활용한 격리*

컨테이너는 Linux 커널의 다음 기능을 활용하여 격리를 제공합니다:

| Linux 기능 | 설명 | 격리 효과 |
|-----------|------|----------|
| **Namespaces** | 프로세스, 네트워크, 파일시스템 격리 | 각 컨테이너가 독립적인 환경을 가짐 |
| **Cgroups** | CPU, 메모리, I/O 리소스 제한 | 리소스 사용량 제어 |
| **Union File Systems** | 레이어드 파일시스템 | 이미지 효율적 관리 |

##### **컨테이너 격리 메커니즘**

*컨테이너 격리 메커니즘은 위 이미지를 참조하세요.*

#### **1.3 Kubernetes 기본 개념**

##### **Kubernetes 핵심 리소스**

*Kubernetes 핵심 리소스: Pod는 최소 배포 단위, Deployment는 Pod를 관리, Service는 네트워크 엔드포인트 제공*

| 리소스 | 설명 | 비유 |
|--------|------|------|
| **Pod** | 하나 이상의 컨테이너로 구성된 최소 배포 단위 | 컨테이너를 담는 상자 |
| **Deployment** | Pod의 배포, 업데이트, 스케일링을 관리 | Pod를 관리하는 관리자 |
| **Service** | Pod에 대한 안정적인 네트워크 엔드포인트 제공 | Pod를 찾는 전화번호부 |
| **Namespace** | 리소스를 논리적으로 분리하는 가상 클러스터 | 아파트의 층 구분 |
| **ConfigMap** | 설정 데이터를 저장하는 리소스 | 설정 파일 저장소 |
| **Secret** | 민감한 데이터를 저장하는 리소스 | 비밀 정보 저장소 |

##### **Kubernetes 아키텍처**

*Kubernetes 아키텍처: Control Plane(API Server, etcd, Scheduler)과 Worker Node(kubelet, kube-proxy)로 구성*

| 구성 요소 | 설명 | 역할 |
|----------|------|------|
| **Control Plane** | 클러스터 관리 및 제어 | API Server, etcd, Scheduler, Controller Manager |
| **Node** | 실제 워크로드가 실행되는 서버 | kubelet, kube-proxy, 컨테이너 런타임 |
| **API Server** | Kubernetes API를 제공하는 중앙 엔드포인트 | 모든 요청의 진입점 |
| **etcd** | 클러스터 상태를 저장하는 분산 키-값 저장소 | 클러스터의 데이터베이스 |
| **Scheduler** | Pod를 적절한 Node에 배치 | 리소스 할당 결정 |
| **kubelet** | Node에서 Pod를 관리하는 에이전트 | Pod 생명주기 관리 |

##### **Kubernetes 클러스터 아키텍처**

*Kubernetes 클러스터는 Control Plane과 Worker Node로 구성되어 있습니다.*

> **참고**: Kubernetes 기본 개념은 [Kubernetes 공식 문서](https://kubernetes.io/docs/concepts/) 및 [Kubernetes GitHub 저장소](https://github.com/kubernetes/kubernetes)를 참조하세요.

##### **기본 Kubernetes 명령어**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 클러스터 정보 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 클러스터 정보 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 클러스터 정보 확인 [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 클러스터 정보 확인
kubectl cluster-info

# Node 목록 확인
kubectl get nodes

# Pod 목록 확인
kubectl get pods

# Namespace 목록 확인
kubectl get namespaces

# Deployment 생성
kubectl create deployment nginx --image=nginx:latest

# Deployment 확인
kubectl get deployments

# Pod 상세 정보 확인
kubectl describe pod <pod-name>

# Pod 로그 확인
kubectl logs <pod-name>

# Pod 삭제
kubectl delete pod <pod-name>


```
-->
-->
-->

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

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```dockerfile
> # 보안 강화 Dockerfile 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [GitHub 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```dockerfile
> # 보안 강화 Dockerfile 예시 [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```dockerfile
# 보안 강화 Dockerfile 예시
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
# 비루트 사용자 생성 및 사용
RUN addgroup -g 1000 -S nodejs && \
    adduser -S nodejs -u 1000
USER nodejs
WORKDIR /app
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --chown=nodejs:nodejs . .
# 읽기 전용 파일시스템 설정 (런타임에서)
CMD ["node", "server.js"]


```
-->
-->
-->

##### **이미지 스캔 자동화**

*이미지 스캔 자동화: CI/CD 파이프라인에 통합하여 배포 전 취약점 탐지*

| 도구 | 설명 | CI/CD 통합 | 특징 |
|------|------|-----------|------|
| **Trivy** | 오픈소스 취약점 스캐너 | GitHub Actions, GitLab CI | 빠른 스캔, 다양한 포맷 지원 |
| **Snyk** | 상용/오픈소스 스캐너 | GitHub, GitLab, Jenkins | 상세한 취약점 정보, 수정 가이드 |
| **Clair** | Quay.io의 오픈소스 스캐너 | Kubernetes Operator | 컨테이너 레지스트리 통합 |

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # GitHub Actions에서 Trivy 스캔 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # GitHub Actions에서 Trivy 스캔 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # GitHub Actions에서 Trivy 스캔 예시 [truncated]
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# GitHub Actions에서 Trivy 스캔 예시
name: Security Scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:latest'
          format: 'table'
          exit-code: '1'
          severity: 'CRITICAL,HIGH'


```
-->
-->
-->

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