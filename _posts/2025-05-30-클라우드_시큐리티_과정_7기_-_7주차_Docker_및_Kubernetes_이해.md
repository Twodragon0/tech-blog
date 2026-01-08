---
layout: post
title: "클라우드 시큐리티 과정 7기 - 7주차: Docker 및 Kubernetes 이해"
date: 2025-05-30 00:04:58 +0900
category: kubernetes
tags: [Docker, Kubernetes, Container, K8s, Cloud-Security, DevSecOps]
excerpt: "안녕하세요, **Twodragon**입니다. 이번 포스트에서는 클라우드 보안 과정 7기의 **Docker 및 Kubernetes 이해**에 관련된 내용을 다루고자 합니다. 이 과정은 게더 타운(Gather Town)에서 진행되며, 각 세션은 **20분 강의 후 5분 휴식** 패턴으로 구성되어 있습니다."
comments: true
toc: true
original_url: https://twodragon.tistory.com/686
image: /assets/images/2025-05-30-클라우드_시큐리티_과정_7기_-_7주차_Docker_및_Kubernetes_이해.svg
---

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
      <li>Docker 기초 및 핵심 개념 (이미지, 컨테이너, Dockerfile)</li>
      <li>Kubernetes 아키텍처 및 주요 리소스 (Pod, Deployment, Service)</li>
      <li>컨테이너 보안 Best Practices 및 런타임 보안</li>
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

```bash
# 이미지 다운로드
docker pull nginx:latest

# 컨테이너 실행
docker run -d -p 8080:80 --name my-nginx nginx:latest

# 실행 중인 컨테이너 확인
docker ps

# 컨테이너 로그 확인
docker logs my-nginx

# 컨테이너 중지 및 삭제
docker stop my-nginx && docker rm my-nginx
```

## 2. Kubernetes 핵심 개념

### 2.1 Kubernetes 아키텍처

Kubernetes는 컨테이너화된 워크로드와 서비스를 관리하기 위한 **오케스트레이션 플랫폼**입니다.

```
┌─────────────────────────────────────────────────────┐
│ Control Plane │
│ ┌─────────────┐ ┌─────────────┐ ┌───────────────┐ │
│ │ API Server │ │ etcd │ │ Scheduler │ │
│ └─────────────┘ └─────────────┘ └───────────────┘ │
│ ┌─────────────────────────────────────────────┐ │
│ │ Controller Manager │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
 │
 ┌────────────────┼────────────────┐
 ▼ ▼ ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Node 1 │ │ Node 2 │ │ Node 3 │
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
│ │ kubelet │ │ │ │ kubelet │ │ │ │ kubelet │ │
│ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
│ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │
│ │ Pods │ │ │ │ Pods │ │ │ │ Pods │ │
│ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │
└─────────────┘ └─────────────┘ └─────────────┘
```

### 2.2 주요 Kubernetes 리소스

#### Pod
가장 작은 배포 단위로, 하나 이상의 컨테이너를 포함합니다.

```yaml
apiVersion: v1
kind: Pod
metadata:
 name: nginx-pod
 labels:
 app: nginx
spec:
 containers:
 - name: nginx
 image: nginx:1.21
 ports:
 - containerPort: 80
```

#### Deployment
Pod의 선언적 업데이트를 제공합니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
 name: nginx-deployment
spec:
 replicas: 3
 selector:
 matchLabels:
 app: nginx
 template:
 metadata:
 labels:
 app: nginx
 spec:
 containers:
 - name: nginx
 image: nginx:1.21
 ports:
 - containerPort: 80
```

#### Service
Pod 집합에 대한 네트워크 서비스를 노출합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
 name: nginx-service
spec:
 selector:
 app: nginx
 ports:
 - protocol: TCP
 port: 80
 targetPort: 80
 type: LoadBalancer
```

## 3. 컨테이너 보안 Best Practices

### 3.1 이미지 보안

1. **신뢰할 수 있는 베이스 이미지 사용**
 - 공식 이미지 또는 검증된 이미지 사용
 - 최소한의 베이스 이미지 선택 (Alpine, Distroless)

2. **취약점 스캐닝**
 ```bash
 # Trivy를 사용한 이미지 스캔
 trivy image nginx:latest
 ```

3. **이미지 서명 및 검증**
 - Docker Content Trust 활성화
 - Cosign을 통한 이미지 서명

### 3.2 런타임 보안

```yaml
# SecurityContext 설정 예시
apiVersion: v1
kind: Pod
metadata:
 name: secure-pod
spec:
 securityContext:
 runAsNonRoot: true
 runAsUser: 1000
 fsGroup: 2000
 containers:
 - name: app
 image: myapp:latest
 securityContext:
 allowPrivilegeEscalation: false
 readOnlyRootFilesystem: true
 capabilities:
 drop:
 - ALL
```

### 3.3 네트워크 정책

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

## 4. 실습 환경 구성

### 4.1 Minikube 설치

```bash
# macOS
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 클러스터 시작
minikube start --driver=docker --cpus=2 --memory=4096
```

### 4.2 K9s로 클러스터 관리

K9s는 터미널 기반 Kubernetes 대시보드입니다.

```bash
# 설치
brew install k9s

# 실행
k9s
```

**K9s 주요 단축키:**
- `:pod` - Pod 목록 보기
- `:deploy` - Deployment 목록 보기
- `:svc` - Service 목록 보기
- `l` - 로그 보기
- `s` - Shell 접속
- `d` - Describe 보기

## 5. 마무리

이번 주차에서는 Docker와 Kubernetes의 기본 개념부터 보안 모범 사례까지 다뤘습니다. 다음 주차에서는 **CI/CD와 Kubernetes 보안**에 대해 더 깊이 있게 다룰 예정입니다.

> **다음 주차 예고:** CI/CD 파이프라인에서의 보안 통합과 Kubernetes 보안 도구 실습

---

📚 **참고 자료:**
- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Docker 공식 문서](https://docs.docker.com/)
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes)
