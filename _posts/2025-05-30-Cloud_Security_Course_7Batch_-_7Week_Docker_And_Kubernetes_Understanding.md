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
author: Twodragon
certifications: [ckad, cka]
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

> **참고**: Docker 기본 명령어 관련 내용은 [Docker 공식 문서](https://docs.docker.com/) 및 [Docker 공식 예제](https://github.com/docker/awesome-compose)를 참조하세요.
> 
> ```bash
> # 이미지 다운로드...
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

# 컨테이너 중지 및 삭제
docker stop my-nginx && docker rm my-nginx

```
-->

## 2. Kubernetes 핵심 개념

### 2.1 Kubernetes 아키텍처

Kubernetes는 컨테이너화된 워크로드와 서비스를 관리하기 위한 **오케스트레이션 플랫폼**입니다.

```mermaid
flowchart TD
    CP["Control Plane"]
    API["API Server"]
    ETCD["etcd"]
    SCHED["Scheduler"]
    CM["Controller Manager"]
    
    CP --> API
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

### 2.2 주요 Kubernetes 리소스

#### Pod
가장 작은 배포 단위로, 하나 이상의 컨테이너를 포함합니다.

> **참고**: Kubernetes Pod 관련 내용은 [Kubernetes Pod 문서](https://kubernetes.io/docs/concepts/workloads/pods/) 및 [Kubernetes 예제](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
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
-->

#### Deployment
Pod의 선언적 업데이트를 제공합니다.

> **참고**: Kubernetes Deployment 관련 내용은 [Kubernetes Deployment 문서](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/) 및 [Kubernetes 예제](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> apiVersion: apps/v1...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
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
-->

#### Service
Pod 집합에 대한 네트워크 서비스를 노출합니다.

> **참고**: Kubernetes Service 관련 내용은 [Kubernetes Service 문서](https://kubernetes.io/docs/concepts/services-networking/service/) 및 [Kubernetes 예제](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> apiVersion: v1...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
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
-->

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

> **참고**: Kubernetes Security Context 관련 내용은 [Kubernetes Security Context 문서](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/) 및 [Kubernetes 예제](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # SecurityContext 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
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
-->

### 3.3 네트워크 정책

> **참고**: Kubernetes Network Policy 관련 내용은 [Kubernetes Network Policy 문서](https://kubernetes.io/docs/concepts/services-networking/network-policies/) 및 [Network Policy 예제](https://github.com/kubernetes/examples)를 참조하세요.

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

> **참고**: Minikube 설치 관련 내용은 [Minikube 공식 문서](https://minikube.sigs.k8s.io/docs/) 및 [Minikube GitHub 저장소](https://github.com/kubernetes/minikube)를 참조하세요.

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

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

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

## 5. 2025년 Kubernetes 보안 업데이트

### 5.1 Kubernetes 릴리스 현황

Kubernetes는 2025년에도 활발하게 발전하고 있습니다.

| 버전 | 코드네임 | 출시일 | 주요 특징 |
|------|----------|--------|-----------|
| **1.32** | Penelope | 2024년 말 | Kubernetes 첫 10년의 마지막 릴리스 |
| **1.35** | Timbernetes | 2025년 12월 | World Tree Release, 새로운 10년의 시작 |

### 5.2 주요 보안 기능 업데이트

#### Fine-grained Kubelet API Authorization (KEP-2862)

Kubernetes 1.32+에서 `KubeletFineGrainedAuthz` feature gate를 통해 kubelet API에 대한 세밀한 접근 제어가 가능해졌습니다.

> **참고**: Kubelet API 접근 제어 관련 내용은 [Kubernetes Kubelet 문서](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet/) 및 [Kubernetes RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)를 참조하세요.

```yaml
# kubelet 설정에서 Fine-grained 인가 활성화
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
featureGates:
  KubeletFineGrainedAuthz: true
authorization:
  mode: Webhook
```

이 기능을 통해:
- Pod별로 kubelet API 접근 권한을 세밀하게 제어
- 특정 노드의 리소스에 대한 접근을 제한
- 최소 권한 원칙을 kubelet 레벨까지 확장

#### Credential Tracking

인증서 서명 기반의 credential ID 생성으로 보안 포렌식이 크게 향상되었습니다.

> **참고**: Kubernetes Audit 및 credential 추적 관련 내용은 [Kubernetes Audit 문서](https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/)를 참조하세요.

```bash
# 인증서 기반 credential 추적 확인
kubectl get certificatesigningrequests -o wide

# Audit 로그에서 credential ID 확인
kubectl logs -n kube-system kube-apiserver-* | grep credentialID
```

**보안 이점:**
- 각 인증 세션에 고유 ID 부여
- 보안 사고 발생 시 추적 용이
- 인증서 갱신 및 폐기 이력 관리

#### User Namespaces Support

User Namespaces는 컨테이너 내 root 사용자를 호스트의 비권한 사용자로 매핑하여 컨테이너 탈출 공격의 위험을 크게 감소시킵니다:

<img src="{{ '/assets/images/diagrams/2025-05-30-Cloud_Security_Course_7Batch_-_7Week_Docker_And_Kubernetes_Understanding/2025-05-30-Cloud_Security_Course_7Batch_-_7Week_Docker_And_Kubernetes_Understanding_mermaid_chart_1.png' | relative_url }}" alt="mermaid_chart_1" loading="lazy" class="post-image">

Linux 커널 6.3 이상에서 사용 가능한 User Namespaces가 Kubernetes에서 정식 지원됩니다.

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
  name: userns-pod
spec:
  hostUsers: false  # User Namespace 활성화
  containers:
  - name: app
    image: myapp:latest
    securityContext:
      runAsUser: 1000
      runAsGroup: 1000

```
-->

**보안 강화 효과:**
- 컨테이너 내 root 사용자가 호스트에서는 비특권 사용자로 매핑
- 컨테이너 탈출 공격 시 피해 최소화
- 워크로드 간 격리 강화

#### Pod Certificates for mTLS (KEP-4317)

kubelet이 Pod용 인증서를 자동으로 요청하고 마운트하는 기능이 추가되었습니다.

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
  name: mtls-pod
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: pod-cert
      mountPath: /etc/pod-certs
      readOnly: true
  volumes:
  - name: pod-cert
    projected:
      sources:
      - serviceAccountToken:
          path: token
          expirationSeconds: 3600
      - clusterTrustBundle:
          path: ca.crt
          name: my-cluster-bundle

```
-->

**주요 특징:**
- 자동 인증서 rotation으로 운영 부담 감소
- Pod 간 mTLS 통신 간소화
- 인증서 만료로 인한 서비스 중단 방지

### 5.3 EKS 1.32 Anonymous Authentication 제한

Amazon EKS 1.32에서는 익명 인증이 health check endpoint로 제한됩니다.

> **참고**: Amazon EKS 보안 관련 내용은 [Amazon EKS 문서](https://docs.aws.amazon.com/eks/latest/userguide/) 및 [EKS 보안 모범 사례](https://aws.github.io/aws-eks-best-practices/security/docs/)를 참조하세요.
> 
> ```yaml
> # EKS 1.32+ 에서의 익명 인증 설정...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# EKS 1.32+ 에서의 익명 인증 설정
# 기존의 익명 접근이 제한됨에 따라 명시적 인증 필요
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: health-check-role
rules:
- nonResourceURLs:
  - "/healthz"
  - "/readyz"
  - "/livez"
  verbs: ["get"]

```
-->

### 5.4 Deprecation 주의사항

> **참고**: Kubernetes Deprecated 기능 관련 내용은 [Kubernetes Deprecation Guide](https://kubernetes.io/docs/reference/using-api/deprecation-guide/)를 참조하세요.
> 
> ```yaml
> # Deprecated (사용 자제)...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# Deprecated (사용 자제)
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-sa
  annotations:
    # 이 annotation은 deprecated됨
    kubernetes.io/enforce-mountable-secrets: "true"

# 권장 방식: Pod SecurityContext에서 직접 제어
spec:
  automountServiceAccountToken: false

```
-->

## 6. 마무리

이번 주차에서는 Docker와 Kubernetes의 기본 개념부터 보안 모범 사례, 그리고 2025년 최신 Kubernetes 보안 업데이트까지 다뤘습니다. 다음 주차에서는 **CI/CD와 Kubernetes 보안**에 대해 더 깊이 있게 다룰 예정입니다.

> **다음 주차 예고:** CI/CD 파이프라인에서의 보안 통합과 Kubernetes 보안 도구 실습

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
