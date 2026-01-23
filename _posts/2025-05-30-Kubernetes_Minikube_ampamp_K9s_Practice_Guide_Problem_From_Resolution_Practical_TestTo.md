---
layout: post
title: "Kubernetes Minikube & K9s 실습 가이드: 문제 해결부터 실전 테스트까지"
date: 2025-05-30 01:11:00 +0900
categories: [kubernetes]
tags: [Kubernetes, Minikube, K9s, K8s, Troubleshooting]
excerpt: "Kubernetes Minikube &amp; K9s 실습 가이드 2024-2025: Minikube 1.37.0+ 설치 및 설정(containerd 기본 런타임, AI 워크로드 지원 krunkit 드라이버, AMD GPU 지원, 리소스/하이퍼바이저/네트워크 문제 해결), K9s 터미널 UI 활용(실시간 모니터링, 네임스페이스 기반 관리, 성능 최적화, 보안 고려사항), Kubernetes 2024-2025 보안 강화(User Namespaces, Bound Service Account Tokens, mTLS Pod Certificates, Dynamic Resource Allocation), 실전 테스트 시나리오(Pod/Deployment/Service 배포, ConfigMap/Secret 관리, HPA/Network Policy 적용)까지 최신 best practices 반영한 실무 중심 가이드."
comments: true
original_url: https://twodragon.tistory.com/687
image: /assets/images/2025-05-30-Kubernetes_Minikube_ampamp_K9s_Guide_From_Practical_To.svg
image_alt: "Kubernetes Minikube and K9s Practical Guide: From Problem Solving to Practical Testing"
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
    <span class="summary-value">Kubernetes Minikube & K9s 실습 가이드: 문제 해결부터 실전 테스트까지</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag devops">Kubernetes</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Kubernetes</span>
      <span class="tag">Minikube</span>
      <span class="tag">K9s</span>
      <span class="tag">K8s</span>
      <span class="tag">Troubleshooting</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>Minikube 설치 및 설정</strong>: 최신 버전(1.37.0+) 설치, containerd 기본 런타임, AI 워크로드 지원(krunkit 드라이버), AMD GPU 지원, 리소스 부족/하이퍼바이저 충돌/네트워크 문제 해결</li>
      <li><strong>K9s 터미널 UI 활용</strong>: 실시간 모니터링, 네임스페이스 기반 리소스 관리, 성능 최적화(대규모 클러스터), 보안 고려사항(읽기 전용 모드, RBAC), 커스텀 뷰 설정</li>
      <li><strong>Kubernetes 2024-2025 보안 강화</strong>: User Namespaces(1.33+), Bound Service Account Tokens(1.32+), mTLS Pod Certificates(1.35 Beta), Dynamic Resource Allocation(1.34 Stable)</li>
      <li><strong>실전 테스트 시나리오</strong>: Pod/Deployment/Service 배포, ConfigMap/Secret 관리, 문제 해결(로그 분석, 리소스 모니터링, 네트워크 디버깅), HPA 및 Network Policy 적용</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Kubernetes, Minikube, K9s</span>
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

## 서론

Kubernetes는 현대적인 컨테이너 오케스트레이션의 표준이 되었으며, 로컬 개발 환경에서 Kubernetes를 학습하고 테스트하기 위한 도구들이 지속적으로 발전하고 있습니다. Minikube는 로컬에서 Kubernetes 클러스터를 쉽게 구성할 수 있게 해주는 도구이며, K9s는 터미널 기반의 강력한 Kubernetes 클러스터 관리 UI입니다.

이 글에서는 2024-2025년 최신 best practices를 반영하여 Minikube와 K9s를 활용한 실습 가이드를 제공합니다. 실제 운영 환경에서 겪을 수 있는 문제 해결 방법부터 최신 보안 기능까지 실무 중심으로 상세히 다룹니다.

<img src="{{ '/assets/images/2025-05-30-Kubernetes_Minikube_ampamp_K9s_Guide_From_Practical_To_image.png' | relative_url }}" alt="Kubernetes Minikube and K9s Practical Guide: From Problem Solving to Practical Testing" loading="lazy" class="post-image">

## 1. 개요

### 1.1 배경 및 필요성

로컬 개발 환경에서 Kubernetes를 학습하고 테스트하는 것은 클라우드 네이티브 애플리케이션 개발의 핵심입니다. Minikube는 최소한의 리소스로 로컬 Kubernetes 클러스터를 구성할 수 있게 해주며, K9s는 복잡한 kubectl 명령어 없이도 직관적인 UI로 클러스터를 관리할 수 있게 해줍니다.

2024-2025년에는 Kubernetes의 보안 기능이 크게 강화되었고, Minikube와 K9s도 최신 Kubernetes 버전을 지원하며 새로운 기능들을 추가했습니다. 이 가이드는 이러한 최신 변화를 반영하여 실무에서 바로 활용할 수 있는 실습 가이드를 제공합니다.

### 1.2 주요 개념

이 가이드에서 다루는 주요 개념:

- **보안 우선**: 최신 보안 기능 활용 및 최소 권한 원칙 적용
- **효율성**: 리소스 최적화 및 자동화를 통한 운영 효율성 향상
- **모범 사례**: 2024-2025년 검증된 best practices 적용
- **실무 중심**: 실제 운영 환경에서 발생하는 문제 해결 방법

## 2. Minikube 설치 및 설정

### 2.1 Minikube 설치

최신 Minikube 버전(1.37.0 이상)을 설치합니다:

```bash
# macOS (Homebrew)
brew install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Windows (Chocolatey)
choco install minikube
```

### 2.2 Minikube 시작 및 기본 설정

#### 최신 Kubernetes 버전으로 시작

```bash
# 최신 안정 버전으로 시작
minikube start --kubernetes-version=stable

# 특정 Kubernetes 버전 지정 (예: 1.34.0)
minikube start --kubernetes-version=v1.34.0

# 리소스 할당 설정 (메모리 4GB, CPU 2개)
minikube start --memory=4096 --cpus=2

# 드라이버 선택 (macOS의 경우 krunkit 드라이버로 AI 워크로드 지원)
minikube start --driver=krunkit  # macOS AI 워크로드용
minikube start --driver=docker    # Docker Desktop
minikube start --driver=podman    # Podman
```

#### containerd 런타임 사용 (2024-2025 권장)

Minikube 1.37.0부터 기본 컨테이너 런타임이 Docker에서 containerd로 변경되었습니다:

```bash
# containerd 런타임으로 시작
minikube start --container-runtime=containerd

# 런타임 확인
minikube ssh -- docker ps  # Docker 사용 시
minikube ssh -- crictl ps  # containerd 사용 시
```

### 2.3 Minikube 문제 해결

#### 리소스 부족 문제

```bash
# 현재 리소스 확인
minikube status

# 리소스 증가
minikube stop
minikube start --memory=8192 --cpus=4

# 또는 minikube config 설정
minikube config set memory 8192
minikube config set cpus 4
```

#### 하이퍼바이저 충돌

```bash
# 현재 드라이버 확인
minikube config get driver

# 드라이버 변경
minikube stop
minikube delete
minikube start --driver=docker  # 또는 podman, virtualbox 등
```

#### 네트워크 문제

```bash
# 네트워크 재설정
minikube stop
minikube delete
minikube start --network-plugin=cni

# DNS 문제 해결
minikube ssh
sudo systemctl restart systemd-resolved
```

### 2.4 Minikube Addons 활용

```bash
# 사용 가능한 addons 확인
minikube addons list

# 유용한 addons 활성화
minikube addons enable metrics-server    # 리소스 메트릭 수집
minikube addons enable ingress           # Ingress 컨트롤러
minikube addons enable dashboard         # Kubernetes Dashboard
minikube addons enable kubetail          # 로그 통합 도구 (최신 추가)

# addon 상태 확인
minikube addons list
```

## 3. K9s 설치 및 활용

### 3.1 K9s 설치

```bash
# macOS (Homebrew)
brew install k9s

# Linux
wget https://github.com/derailed/k9s/releases/download/v0.31.0/k9s_Linux_amd64.tar.gz
tar -xzf k9s_Linux_amd64.tar.gz
sudo mv k9s /usr/local/bin/

# Windows (Scoop)
scoop install k9s
```

### 3.2 K9s 기본 사용법

```bash
# K9s 시작
k9s

# 특정 네임스페이스로 시작
k9s -n production

# 읽기 전용 모드 (보안 감사 시 유용)
k9s --readonly
```

### 3.3 K9s 주요 단축키 및 기능

| 단축키 | 기능 | 설명 |
|--------|------|------|
| `:` | 명령 모드 | kubectl 명령어 직접 실행 |
| `/` | 필터 모드 | 리소스 필터링 |
| `Ctrl+A` | 모든 리소스 선택 | 대량 작업 시 유용 |
| `d` | Describe | 리소스 상세 정보 |
| `e` | Edit | 리소스 편집 |
| `l` | Logs | Pod 로그 확인 |
| `s` | Shell | Pod 내부 쉘 접근 |
| `x` | Port-forward | 포트 포워딩 설정 |

### 3.4 K9s Best Practices (2024-2025)

#### 1. 네임스페이스 기반 리소스 관리

```bash
# 특정 네임스페이스에 집중하여 성능 향상
k9s -n default

# 여러 네임스페이스 전환 단축키 설정
# ~/.config/k9s/hotkeys.yml에 설정
```

#### 2. 성능 최적화

```yaml
# ~/.config/k9s/config.yml
k9s:
  refreshRate: 2  # 대규모 클러스터(1000+ pods)에서는 5-10초로 증가
  maxConnRetry: 5
  readOnly: false
  noExitOnCtrlC: false
  ui:
    enableMouse: true
    headless: false
    logoless: false
    crumbsless: false
    reactive: false
    noIcons: false
```

#### 3. 보안 고려사항

K9s를 사용할 때는 다음 보안 고려사항을 준수해야 합니다:

```bash
# 읽기 전용 모드로 감사 수행
k9s --readonly

# 환경별 kubeconfig 분리
export KUBECONFIG=~/.kube/config-dev
k9s

# RBAC 기반 최소 권한 원칙 적용
# ServiceAccount에 적절한 Role/RoleBinding 설정
```

#### 4. 커스텀 뷰 설정

```yaml
# ~/.config/k9s/views.yml
views:
  v1/pods:
    columns:
      - NAME
      - STATUS
      - READY
      - RESTARTS
      - AGE
      - CPU(cores)
      - MEMORY(bytes)
```

### 3.5 K9s 고급 활용

#### 포트 포워딩 설정

```bash
# K9s 내에서 포트 포워딩
# 1. Service 또는 Pod 선택
# 2. 'x' 키 누르기
# 3. 포트 매핑 입력 (예: 8080:80)
```

#### 로그 통합 확인

```bash
# 여러 Pod 로그 동시 확인
# 1. Pod 리스트에서 여러 Pod 선택 (Space)
# 2. 'l' 키로 로그 확인
```

#### 리소스 모니터링

```bash
# 리소스 사용량 실시간 모니터링
# 1. Pod 리스트에서 CPU/MEMORY 컬럼 확인
# 2. 'd' 키로 상세 메트릭 확인
```

## 4. 실전 테스트 시나리오

### 4.1 기본 Pod 배포 및 관리

```yaml
# nginx-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
```

```bash
# Pod 생성
kubectl apply -f nginx-pod.yaml

# K9s에서 확인
# 1. k9s 실행
# 2. 'po' 입력하여 Pod 리스트 확인
# 3. 'd' 키로 상세 정보 확인
# 4. 'l' 키로 로그 확인
```

### 4.2 Deployment 및 Service 노출

```yaml
# nginx-deployment.yaml
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
        image: nginx:1.25
        ports:
        - containerPort: 80
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
---
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

```bash
# Deployment 및 Service 생성
kubectl apply -f nginx-deployment.yaml

# K9s에서 모니터링
# 1. 'deploy' 입력하여 Deployment 확인
# 2. 'svc' 입력하여 Service 확인
# 3. 'x' 키로 포트 포워딩 설정
```

### 4.3 ConfigMap 및 Secret 관리

```yaml
# configmap-example.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database_url: "postgresql://localhost:5432/mydb"
  log_level: "info"
---
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
stringData:
  password: "YOUR_SECRET_PASSWORD_HERE"  # 실제 비밀번호로 교체
  api_key: "sk-***MASKED***"  # 실제 API 키로 교체
```

```bash
# ConfigMap 및 Secret 생성
kubectl apply -f configmap-example.yaml

# K9s에서 확인
# 1. 'cm' 입력하여 ConfigMap 확인
# 2. 'sec' 입력하여 Secret 확인
# 3. 'd' 키로 상세 내용 확인 (Secret은 base64 인코딩됨)
```

### 4.4 문제 해결 시나리오

#### Pod가 시작되지 않는 경우

```bash
# 1. Pod 상태 확인
kubectl get pods
k9s  # 'po' 입력하여 Pod 리스트 확인

# 2. Pod 이벤트 확인
kubectl describe pod <pod-name>
# K9s에서 'd' 키 사용

# 3. Pod 로그 확인
kubectl logs <pod-name>
# K9s에서 'l' 키 사용

# 4. 이전 컨테이너 로그 확인 (재시작된 경우)
kubectl logs <pod-name> --previous
```

#### 리소스 부족 문제

```bash
# 리소스 사용량 확인
kubectl top pods
kubectl top nodes

# K9s에서 CPU/MEMORY 컬럼 확인
# 1. 'po' 입력
# 2. CPU/MEMORY 컬럼 확인
# 3. 리소스 사용량이 높은 Pod 식별
```

#### 네트워크 연결 문제

```bash
# Service 엔드포인트 확인
kubectl get endpoints

# 포트 포워딩으로 직접 테스트
kubectl port-forward svc/nginx-service 8080:80

# K9s에서 포트 포워딩
# 1. Service 선택
# 2. 'x' 키
# 3. 포트 매핑 입력
```

## 5. Kubernetes 2024-2025 업데이트 및 보안 강화

### 5.1 Kubernetes 버전 업데이트

2024-2025년 Kubernetes의 주요 버전 업데이트:

#### Kubernetes 1.32 (2024년 12월)

- **Bound Service Account Tokens (Stable)**: 서비스 계정 토큰을 특정 Pod에 안전하게 바인딩하여 무단 접근 위험 감소
- **Projected Service Account Tokens for Kubelet Image Credential Providers (Alpha)**: Kubelet의 이미지 자격 증명 검색 보안 강화

```bash
# Kubernetes 1.32로 클러스터 시작
minikube start --kubernetes-version=v1.32.0
```

#### Kubernetes 1.33 (2025년 4월)

- **ClusterTrustBundles (Beta)**: 클러스터 내 보안 통신을 위한 인증서 검증 프로세스 개선
- **User Namespaces in Pods (Beta)**: Pod 내 사용자 및 그룹 ID 분리를 통한 워크로드 보안 강화

#### Kubernetes 1.34 (2025년 9월)

- **Dynamic Resource Allocation (DRA) Stable**: AI/ML 워크로드를 위한 디바이스 할당 및 공유 표준화
- **Structured Authentication Configuration**: API 서버 클라이언트 인증 관리를 위한 안정적인 설정 파일 형식

#### Kubernetes 1.35 (2025년 12월)

- **User Namespaces: Beta-by-Default Isolation**: 기본 활성화, 컨테이너 UID 0(root)을 호스트의 비권한 UID로 매핑하여 컨테이너 탈출 취약점 위험 감소
- **mTLS Pod Certificates (Beta)**: Pod와 API 서버 간 제로 트러스트 네트워킹을 위한 일급 mTLS 지원
- **Robust Image Pull Authorization (Beta)**: `imagePullCredentialsVerificationPolicy`로 캐시된 이미지에 대해서도 레지스트리 자격 증명 재검증

```bash
# Kubernetes 버전 확인
kubectl version --short

# Minikube에서 최신 안정 버전으로 시작
minikube start --kubernetes-version=stable

# 특정 버전 지정 (예: 1.34.0)
minikube start --kubernetes-version=v1.34.0
```

> **참고**: Kubernetes 클러스터 관리 관련 내용은 [Kubernetes 공식 문서](https://kubernetes.io/docs/) 및 [Kubernetes GitHub 저장소](https://github.com/kubernetes/kubernetes)를 참조하세요.

### 5.2 보안 강화 기능

#### User Namespaces Support (Kubernetes 1.33+)

User Namespaces는 컨테이너 내 root 사용자를 호스트의 비권한 사용자로 매핑하여 컨테이너 탈출 공격의 위험을 크게 감소시킵니다:

컨테이너 격리를 강화하는 사용자 네임스페이스 지원:

```yaml
# User Namespace 활성화 Pod 예시
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  hostUsers: false  # User Namespace 활성화
  containers:
  - name: app
    image: nginx:1.25
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      allowPrivilegeEscalation: false
      capabilities:
        drop:
        - ALL
```

**주요 보안 이점**:
- **루트리스 컨테이너**: 컨테이너 내 루트가 호스트에서는 비권한 사용자로 매핑
- **보안 강화**: 컨테이너 탈출 공격 위험 감소
- **호환성**: 대부분의 워크로드와 호환

> **참고**: 전체 예제는 [Kubernetes 공식 문서 - User Namespaces](https://kubernetes.io/docs/concepts/security/pod-security-standards/)를 참조하세요.

#### Bound Service Account Tokens (Kubernetes 1.32+)

서비스 계정 토큰을 특정 Pod에 안전하게 바인딩:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  serviceAccountName: app-sa
  automountServiceAccountToken: true
  containers:
  - name: app
    image: myapp:latest
```

**보안 이점**:
- 토큰이 특정 Pod에 바인딩되어 무단 사용 방지
- 향상된 추적성 및 사용성
- 토큰 만료 시 자동 갱신

#### mTLS Pod Certificates (Kubernetes 1.35 Beta)

Pod와 API 서버 간 제로 트러스트 네트워킹:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mtls-pod
spec:
  containers:
  - name: app
    image: myapp:latest
  # mTLS 인증서는 자동으로 마운트됨
```

> **참고**: mTLS Pod Certificates는 현재 Beta 기능입니다. 자세한 내용은 [Kubernetes Enhancement Proposal](https://github.com/kubernetes/enhancements)을 참조하세요.
> 
> ```yaml
> # Fine-grained Kubelet Authorization 설정 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Fine-grained Kubelet Authorization 설정 예시
apiVersion: authorization.k8s.io/v1
kind: SubjectAccessReview
spec:
  resourceAttributes:
    namespace: default
    verb: get
    group: ""
    resource: pods
    subresource: log
  user: system:node:worker-1

```
-->

### 5.3 Minikube 최신 기능 (1.37.0+)

#### AI 워크로드 지원 (macOS)

```bash
# krunkit 드라이버로 GPU 가속 활성화
minikube start --driver=krunkit

# AI 워크로드 실행을 위한 GPU 확인
minikube ssh -- nvidia-smi  # NVIDIA GPU
minikube ssh -- rocm-smi     # AMD GPU
```

#### AMD GPU 지원

```bash
# AMD GPU 지원 활성화
minikube start --gpus=amd

# GPU 리소스 확인
kubectl describe node minikube | grep -i gpu
```

#### containerd 기본 런타임

Minikube 1.37.0부터 기본 컨테이너 런타임이 containerd로 변경되었습니다:

```bash
# containerd 런타임 확인
minikube ssh -- crictl version

# 이미지 관리
minikube ssh -- crictl images
minikube ssh -- crictl pull nginx:1.25
```

**containerd 사용의 이점**:
- 더 가벼운 런타임 (Docker보다 리소스 사용량 적음)
- Kubernetes 네이티브 통합
- 향상된 성능 및 보안

#### Podman 드라이버 개선

```bash
# Podman 드라이버로 시작 (실험적 단계에서 벗어남)
minikube start --driver=podman

# Podman 버전 확인
minikube ssh -- podman version
```

> **참고**: Minikube 최신 기능은 [Minikube 공식 문서](https://minikube.sigs.k8s.io/docs/) 및 [Minikube GitHub 저장소](https://github.com/kubernetes/minikube)를 참조하세요.

### 5.4 Minikube 업데이트 및 관리

```bash
# Minikube 업데이트
brew upgrade minikube  # macOS
# 또는
minikube update-check

# 최신 Kubernetes 버전으로 클러스터 생성
minikube start --kubernetes-version=stable

# 특정 버전 지정
minikube start --kubernetes-version=v1.34.0

# 클러스터 정보 확인
minikube kubectl -- cluster-info

# Minikube 버전 확인
minikube version

# 클러스터 상태 확인
minikube status
```

### 5.5 보안 점검 체크리스트

Kubernetes 2024-2025 업데이트를 적용할 때 확인해야 할 보안 항목:

| 항목 | 설명 | 명령어/확인 방법 |
|------|------|-----------------|
| User Namespace | hostUsers: false 설정 확인 | Pod spec 검토, `kubectl get pods -o yaml \| grep hostUsers` |
| Bound Service Account Tokens | 토큰 바인딩 활성화 확인 | Pod spec에서 `automountServiceAccountToken: true` 확인 |
| Security Context | runAsNonRoot, capabilities drop 설정 | `kubectl get pods -o yaml \| grep -A 10 securityContext` |
| RBAC | 최소 권한 원칙 준수 | `kubectl get roles,rolebindings -A` |
| Network Policy | 네트워크 정책 적용 | `kubectl get networkpolicies -A` |
| Image Pull Policy | 이미지 풀 정책 및 자격 증명 검증 | `kubectl get pods -o yaml \| grep imagePullPolicy` |
| Resource Limits | 리소스 제한 설정 | `kubectl top pods`, `kubectl describe pod` |
| Pod Security Standards | Pod 보안 표준 준수 | `kubectl get namespace <ns> -o yaml \| grep pod-security` |

### 5.6 Kubernetes Best Practices (2024-2025)

#### 리소스 최적화

```yaml
# HPA (Horizontal Pod Autoscaler) 설정 예시
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### 네트워크 정책 적용

```yaml
# NetworkPolicy 예시
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  # 기본적으로 모든 트래픽 차단
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app
spec:
  podSelector:
    matchLabels:
      app: nginx
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
```

> **참고**: Kubernetes Best Practices는 [Kubernetes 보안 체크리스트](https://kubernetes.io/docs/concepts/security/security-checklist/)를 참조하세요.

## 6. 모범 사례 요약

### 6.1 보안 모범 사례

- **최소 권한 원칙**: RBAC를 통한 최소 권한 접근 제어
- **Pod Security Standards**: 네임스페이스 레벨에서 Pod 보안 표준 적용
- **Network Policies**: 네트워크 트래픽 제어를 통한 방어 심화
- **정기적인 보안 점검**: 취약점 스캔 및 보안 감사 자동화
- **이미지 보안**: 신뢰할 수 있는 레지스트리 사용 및 이미지 스캔

### 6.2 운영 모범 사례

- **리소스 관리**: HPA/VPA를 통한 자동 스케일링
- **모니터링**: 메트릭 수집 및 알림 설정
- **로깅**: 중앙화된 로그 관리
- **백업**: etcd 백업 및 재해 복구 계획
- **CI/CD 통합**: 자동화된 배포 파이프라인 구축

### 6.3 Minikube Best Practices

- **리소스 할당**: 개발 환경에 적합한 리소스 설정
- **드라이버 선택**: 환경에 맞는 최적의 드라이버 사용
- **Addons 활용**: 필요한 기능을 addon으로 활성화
- **버전 관리**: Kubernetes 버전을 명시적으로 지정

### 6.4 K9s Best Practices

- **네임스페이스 필터링**: 특정 네임스페이스에 집중하여 성능 향상
- **읽기 전용 모드**: 감사 및 모니터링 시 활용
- **커스텀 뷰**: 팀 워크플로우에 맞는 뷰 설정
- **단축키 활용**: 효율적인 클러스터 관리

## 결론

이 가이드에서는 Kubernetes Minikube & K9s를 활용한 실습 환경 구축부터 최신 보안 기능까지 실무 중심으로 다루었습니다. 2024-2025년 Kubernetes 업데이트에서는 보안이 크게 강화되었으며, 특히 User Namespaces, Bound Service Account Tokens, mTLS Pod Certificates 등이 주요 변화입니다.

Minikube 1.37.0에서는 AI 워크로드 지원, AMD GPU 지원, containerd 기본 런타임 등이 추가되었으며, K9s는 대규모 클러스터 관리와 보안 감사를 위한 기능들이 개선되었습니다.

올바른 설정과 지속적인 모니터링, 그리고 최신 best practices를 적용함으로써 안전하고 효율적인 Kubernetes 환경을 구축할 수 있습니다.

## 참고 자료

### 공식 문서

- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Kubernetes GitHub 저장소](https://github.com/kubernetes/kubernetes)
- [Kubernetes 공식 예제](https://github.com/kubernetes/examples)
- [Minikube 공식 문서](https://minikube.sigs.k8s.io/docs/)
- [Minikube GitHub 저장소](https://github.com/kubernetes/minikube)
- [K9s 공식 문서](https://k9scli.io/)
- [K9s GitHub 저장소](https://github.com/derailed/k9s)

### Kubernetes 보안 관련

- [Kubernetes 보안 체크리스트](https://kubernetes.io/docs/concepts/security/security-checklist/)
- [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [RBAC 문서](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

### Kubernetes 릴리스 노트

- [Kubernetes 1.32 릴리스 노트](https://github.com/kubernetes/kubernetes)
- [Kubernetes 1.33 릴리스 노트](https://github.com/kubernetes/kubernetes)
- [Kubernetes 1.34 릴리스 노트](https://github.com/kubernetes/kubernetes)
- [Kubernetes 1.35 릴리스 노트](https://github.com/kubernetes/kubernetes)

### 추가 학습 자료

- [Kubernetes 공식 튜토리얼](https://kubernetes.io/docs/tutorials/)
- [Kubernetes 실습 환경](https://kubernetes.io/docs/tasks/)
- [Minikube 시작 가이드](https://minikube.sigs.k8s.io/docs/start/)
- [K9s 사용 가이드](https://k9scli.io/topics/commands/)