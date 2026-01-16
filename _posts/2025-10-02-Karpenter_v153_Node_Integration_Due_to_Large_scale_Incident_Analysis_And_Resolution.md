---
layout: post
title: "Karpenter v1.5.3 노드 통합으로 인한 대규모 장애 분석 및 해결기"
date: 2025-10-02 17:25:43 +0900
categories: [incident]
tags: [Karpenter, Kubernetes, AWS, Post-Mortem, Incident, EKS]
excerpt: "Karpenter v1.5.3 노드 통합 장애 분석: 공격적 Consolidation 정책과 PodDisruptionBudget 미설정으로 20개 이상 Pod 동시 재시작, 약 10분간 서비스 장애 발생. 근본 원인 분석, NodePool 설정 수정(Consolidation 정책 조정), PodDisruptionBudget 적용을 통한 재발 방지 대책, Karpenter v1.0 GA 업데이트 반영까지 실무 중심 정리."
comments: true
original_url: https://twodragon.tistory.com/695
image: /assets/images/2025-10-02-Karpenter_v153_Node_Integration_Due_to_Large-scale_Incident_Analysis_and_Resolution.svg
image_alt: "Karpenter v1.5.3 Large-Scale Incident Analysis and Resolution Due to Node Integration"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Karpenter v1.5.3 노드 통합으로 인한 대규모 장애 분석 및 해결기</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Incident</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Karpenter</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">AWS</span>
      <span class="tag">Post-Mortem</span>
      <span class="tag">Incident</span>
      <span class="tag">EKS</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>Karpenter v1.5.3 공격적 노드 통합 정책으로 인한 장애 분석</li>
      <li>PodDisruptionBudget 미설정으로 20개 이상 Pod 동시 재시작</li>
      <li>NodePool 설정 수정 및 PDB 적용을 통한 재발 방지 대책</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">Karpenter, Kubernetes, AWS EKS, PodDisruptionBudget</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">SRE, 인시던트 대응 담당자, 운영 엔지니어</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

<img src="{{ '/assets/images/2025-10-02-Karpenter_v153_Node_Integration_Due_to_Large-scale_Incident_Analysis_and_Resolution_image.png' | relative_url }}" alt="Karpenter v1.5.3 Large-Scale Incident Analysis and Resolution Due to Node Integration" loading="lazy" class="post-image">


## 서론

안녕하세요, **Twodragon**입니다. 이번 포스팅에서는 Kubernetes 오토스케일링에 대해 실무 중심으로 정리합니다.

Karpenter는 Kubernetes 클러스터의 오토스케일링을 혁신적으로 개선했지만, 최신 버전에서 중요한 변경사항이 있었습니다.

이번 포스팅에서는 다음 내용을 다룹니다:
- Karpenter v1.5.3 노드 통합으로 인한 대규모 장애 분석 및 해결기의 핵심 내용 및 실무 적용 방법
- 2025-2026년 최신 트렌드 및 업데이트 사항
- 실전 사례 및 문제 해결 방법
- 보안 모범 사례 및 권장 사항

## 📊 빠른 참조

### 인시던트 요약

| 항목 | 내용 |
|------|------|
| **발생 일시** | 2025-10-02 15:43:00 KST |
| **장애 지속 시간** | 약 10분 (15:43:00 ~ 15:53:00) |
| **영향 범위** | 20개 이상 Pod 동시 재시작, API Gateway 장애 |
| **근본 원인** | Karpenter v1.5.3 공격적 노드 통합 정책 + PDB 미설정 |
| **해결 방법** | NodePool 설정 수정, PodDisruptionBudget 적용 |

### 장애 타임라인 요약

| 시간 | 이벤트 | 영향 |
|------|--------|------|
| 15:43:00 | Karpenter 노드 통합 시작 | - |
| 15:43:15 | Node 드레인 시작 | - |
| 15:43:20 | 20+ Pod 동시 Terminating | 서비스 영향 시작 |
| 15:43:30 | API Gateway health check 실패 | 장애 인지 |
| 15:44:00 | 서비스 전체 장애 | 사용자 영향 |
| 15:50:00 | 수동 노드 추가 | 복구 시작 |
| 15:53:00 | 서비스 복구 완료 | 정상화 |

### 문제가 된 NodePool 설정

| 설정 항목 | 문제 값 | 권장 값 | 설명 |
|----------|---------|---------|------|
| **consolidationPolicy** | WhenEmptyOrUnderutilized | WhenEmpty | 너무 공격적 |
| **consolidateAfter** | 30s | 5m | 너무 짧은 대기 시간 |
| **budgets.nodes** | "100%" | "10%" | 모든 노드 동시 삭제 가능 |

### 해결 방안 요약

| 조치 항목 | Before | After | 효과 |
|----------|--------|-------|------|
| **Consolidation 정책** | WhenEmptyOrUnderutilized | WhenEmpty | 공격적 통합 방지 |
| **ConsolidateAfter** | 30s | 5m | 안정적인 대기 시간 |
| **Disruption Budget** | "100%" | "10%" | 동시 삭제 제한 |
| **PodDisruptionBudget** | 미설정 | minAvailable: 50% | Pod 보호 |

### Karpenter v1.0 GA 개선 사항 (2025년 업데이트)

| 개선 항목 | 설명 | 이 장애와의 연관성 |
|----------|------|-------------------|
| **API 안정성** | `karpenter.sh/v1` API stable 전환 | 프로덕션 준비 완료 |
| **Consolidation 알고리즘** | 더 스마트한 비용 최적화 | 공격적 통합 문제 개선 |
| **Disruption Budgets** | 더 세밀한 disruption 제어 | PDB 존중 강화 |
| **Pod Readiness 확인** | Pod readiness 확인 후 다음 노드 종료 | 순차적 종료 보장 |

### 모범 사례 체크리스트

| 항목 | 상태 | 설명 |
|------|------|------|
| **PDB 설정** | ✅ 필수 | 모든 중요 Pod에 PDB 적용 |
| **Consolidation 정책** | ✅ WhenEmpty 권장 | 공격적 정책 지양 |
| **Disruption Budget** | ✅ 10% 이하 권장 | 동시 삭제 제한 |
| **모니터링** | ✅ 필수 | 노드 통합 이벤트 모니터링 |
| **롤백 계획** | ✅ 필수 | 문제 발생 시 즉시 롤백 가능 |

### Karpenter 노드 통합 프로세스

Karpenter의 노드 통합(Consolidation)은 비용 최적화를 위해 여러 노드에 분산된 Pod를 더 적은 수의 노드로 모아 빈 노드를 삭제하는 프로세스입니다:

```mermaid
graph TB
    subgraph Before["Before Consolidation"]
        Node1["Node 1 - Pod A, Pod B - CPU: 30%"]
        Node2["Node 2 - Pod C - CPU: 15%"]
        Node3["Node 3 - Pod D - CPU: 20%"]
    end
    
    subgraph Karpenter["Karpenter Consolidation"]
        Analyze["Analyze - Node Utilization"]
        Schedule["Schedule - Pod Migration"]
        Drain["Drain Nodes - Pod Eviction"]
    end
    
    subgraph After["After Consolidation"]
        Node1New["Node 1 - Pod A, Pod B, Pod C, Pod D - CPU: 65%"]
        Node2Del["Node 2 - (Deleted)"]
        Node3Del["Node 3 - (Deleted)"]
    end
    
    Before -> Analyze
    Analyze -> Schedule
    Schedule -> Drain
    Drain -> After
    
    style Node1 fill:#e1f5ff
    style Node2 fill:#fff4e1
    style Node3 fill:#fff4e1
    style Analyze fill:#e8f5e9
    style Schedule fill:#fff4e1
    style Drain fill:#ffebee
    style Node1New fill:#e8f5e9
    style Node2Del fill:#ffebee
    style Node3Del fill:#ffebee
```

### 장애 발생 시나리오

문제가 된 설정으로 인해 발생한 장애 시나리오:

```mermaid
graph LR
    subgraph Config["Problematic Configuration"]
        Policy["consolidationPolicy: - WhenEmptyOrUnderutilized"]
        Budget["budgets.nodes: - 100%"]
        NoPDB["No PodDisruptionBudget"]
    end
    
    subgraph Incident["Incident Timeline"]
        Start["15:43:00 - Consolidation Starts"]
        Drain["15:43:15 - Multiple Nodes - Drain Simultaneously"]
        Pods["15:43:20 - 20+ Pods - Terminating"]
        Failure["15:43:30 - Service Failure"]
    end
    
    subgraph Impact["Impact"]
        API["API Gateway - 0/3 Healthy"]
        Order["Order Service - Down"]
        Payment["Payment Service - Down"]
    end
    
    Config -> Start
    Start -> Drain
    Drain -> Pods
    Pods -> Failure
    Failure -> API
    Failure -> Order
    Failure -> Payment
    
    style Policy fill:#ffebee
    style Budget fill:#ffebee
    style NoPDB fill:#ffebee
    style Drain fill:#ffebee
    style Pods fill:#ffebee
    style Failure fill:#ff5252
    style API fill:#ff5252
    style Order fill:#ff5252
    style Payment fill:#ff5252
```

## 1. 사건의 시작

### 1.1 타임라인

| 시간 | 이벤트 |
|------|--------|
| 15:43:00 | Karpenter가 노드 통합 시작 |
| 15:43:15 | Node `ip-10-0-1-234` 드레인 시작 |
| 15:43:20 | 20+ Pod 동시 Terminating |
| 15:43:30 | API Gateway health check 실패 알림 |
| 15:44:00 | 서비스 전체 장애 인지 |
| 15:45:00 | 긴급 대응 시작 |
| 15:50:00 | 수동 노드 추가 |
| 15:53:00 | 서비스 복구 완료 |
| 15:55:00 | 장애 공지 발송 |

### 1.2 최초 알림

```
[CRITICAL] API Gateway health-check failed
Time: 2025-10-02 15:43:30 KST
Service: api-gateway
Status: 0/3 healthy endpoints
Duration: ongoing
```

## 2. 근본 원인 분석

### 2.1 Karpenter 노드 통합이란?

Karpenter는 클러스터 비용 최적화를 위해 **노드 통합(Consolidation)** 기능을 제공합니다. 이는 여러 노드에 분산된 Pod를 더 적은 수의 노드로 모아 빈 노드를 삭제하는 기능입니다.

> **2025년 업데이트: Karpenter v1.0 GA 출시**
>
> 2025년에 Karpenter v1.0이 GA(General Availability)로 출시되었습니다. 주요 변경사항:
> - **API 안정성**: `karpenter.sh/v1` API가 stable로 전환되어 프로덕션 준비 완료
> - **개선된 Consolidation 알고리즘**: 더 스마트한 비용 최적화로 불필요한 노드 종료 감소
> - **Multi-architecture 지원 강화**: ARM64/AMD64 혼합 워크로드 지원 개선
> - **Disruption Budgets 개선**: 더 세밀한 disruption 제어 가능
>
> **v1.0에서 해결된 문제들:**
> - 이 장애에서 경험한 공격적인 consolidation 문제가 크게 개선됨
> - `consolidationPolicy: WhenEmptyOrUnderutilized` 사용 시에도 더 보수적으로 동작
> - PDB를 더 잘 존중하며, Pod readiness를 확인 후 다음 노드 종료 진행

<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
Before Consolidation:
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Node 1 │ │ Node 2 │ │ Node 3 │
│ [Pod][Pod] │ │ [Pod] │ │ [Pod] │
│ CPU: 30% │ │ CPU: 15% │ │ CPU: 20% │
└─────────────┘ └─────────────┘ └─────────────┘

After Consolidation:
┌─────────────┐ ┌─────────────┐
│ Node 1 │ │ (deleted) │
│ [Pod][Pod] │ │ │
│ [Pod][Pod] │ │ │
│ CPU: 65% │ │ │
└─────────────┘ └─────────────┘

```
-->

### 2.2 문제의 NodePool 설정

> **참고**: Karpenter NodePool 설정 관련 내용은 [Karpenter 공식 문서](https://karpenter.sh/) 및 [Karpenter GitHub 저장소](https://github.com/aws/karpenter)를 참조하세요.
> 
> ```yaml
> # 문제가 된 NodePool 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 문제가 된 NodePool 설정
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
 name: default
spec:
 template:
 spec:
 nodeClassRef:
 group: karpenter.k8s.aws
 kind: EC2NodeClass
 name: default
 disruption:
 consolidationPolicy: WhenEmptyOrUnderutilized # 너무 공격적
 consolidateAfter: 30s # 30초 후 바로 통합 시도
 budgets:
 - nodes: "100%" # 모든 노드 동시 삭제 가능!

```
-->

### 2.3 PDB 미설정 문제

> **참고**: PodDisruptionBudget 설정 관련 내용은 [Kubernetes PDB 문서](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) 및 [Karpenter 문서](https://karpenter.sh/)를 참조하세요.
> 
> ```yaml
> # PodDisruptionBudget이 없었음...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# PodDisruptionBudget이 없었음
# 결과: 모든 Pod가 동시에 종료될 수 있음

# 있어야 했던 설정:
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
 name: api-gateway-pdb
spec:
 minAvailable: 2 # 또는 maxUnavailable: 1
 selector:
 matchLabels:
 app: api-gateway

```
-->

## 3. 장애 발생 과정 상세

### 3.1 이벤트 로그 분석

> **참고**: Karpenter 로그 분석 관련 내용은 [Karpenter 문서](https://karpenter.sh/) 및 [Kubernetes 로깅 모범 사례](https://kubernetes.io/docs/concepts/cluster-administration/logging/)를 참조하세요.
> 
> ```bash
> # Karpenter 로그 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# Karpenter 로그 확인
kubectl logs -n karpenter deploy/karpenter -c controller --since=1h | grep -i consolidat

# 출력 (재구성)
15:43:00 INFO controller.disruption Computing consolidation candidates
15:43:05 INFO controller.disruption Found 3 consolidatable nodes
15:43:10 INFO controller.disruption Disrupting node ip-10-0-1-234 for consolidation
15:43:10 INFO controller.disruption Disrupting node ip-10-0-2-156 for consolidation
15:43:15 INFO controller.node Draining node ip-10-0-1-234
15:43:15 INFO controller.node Draining node ip-10-0-2-156

```
-->

### 3.2 Pod 이벤트

> **참고**: Kubernetes Pod 이벤트 분석 관련 내용은 [Kubernetes 이벤트 문서](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/event-v1/) 및 [Kubernetes 디버깅 가이드](https://kubernetes.io/docs/tasks/debug/)를 참조하세요.

```bash
kubectl get events --field-selector reason=Killing -A

NAMESPACE LAST SEEN TYPE REASON OBJECT MESSAGE
prod 10m Warning Killing pod/api-gateway-abc12 Stopping container...
prod 10m Warning Killing pod/api-gateway-def34 Stopping container...
prod 10m Warning Killing pod/order-service-xyz Stopping container...
# ... 20개 이상의 Pod가 동시에 종료됨
```

### 3.3 영향 범위

<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌────────────────────────────────────────────────────────────────────┐
│ Impact Analysis │
├────────────────────────────────────────────────────────────────────┤
│ │
│ Affected Services: │
│ ├── api-gateway (3/3 pods down) ──► 전체 API 불가 │
│ ├── order-service (2/2 pods down) ──► 주문 처리 불가 │
│ ├── payment-service (2/2 pods down) ──► 결제 실패 │
│ └── notification (1/1 pod down) ──► 알림 발송 지연 │
│ │
│ Business Impact: │
│ ├── Failed API calls: ~15,000 │
│ ├── Failed orders: ~200 │
│ ├── Estimated revenue loss: ~2,000,000 KRW │
│ └── Customer complaints: 50+ │
│ │
└────────────────────────────────────────────────────────────────────┘

```
-->

## 4. 긴급 대응

### 4.1 즉시 조치 사항

> **참고**: Karpenter 긴급 대응 관련 내용은 [Karpenter 공식 문서](https://karpenter.sh/) 및 [Karpenter GitHub 저장소](https://github.com/aws/karpenter)를 참조하세요.
> 
> ```bash
> # 1. Karpenter 비활성화 (긴급)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 1. Karpenter 비활성화 (긴급)
kubectl scale deployment karpenter -n karpenter --replicas=0

# 2. 수동으로 노드 추가
eksctl scale nodegroup --cluster=prod-cluster \
 --name=workers --nodes=5 --nodes-min=5

# 3. 서비스 상태 확인
kubectl get pods -n prod -o wide
kubectl get nodes

# 4. Pod 재시작 강제
kubectl rollout restart deployment -n prod

```
-->

### 4.2 서비스 복구 확인

> **참고**: Kubernetes Health Check 관련 내용은 [Kubernetes Liveness/Readiness Probes 문서](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)를 참조하세요.

```bash
# Health check 확인
for svc in api-gateway order-service payment-service; do
 echo "=== $svc ==="
 kubectl get pods -n prod -l app=$svc
 kubectl exec -n prod deploy/$svc -- curl -s localhost:8080/health
done
```

## 5. 영구적 해결책

### 해결 방안 개요

다음과 같은 다층 방어 전략을 통해 재발을 방지합니다:

```mermaid
graph TB
    subgraph Solution["Solution Layers"]
        Policy["1. Consolidation Policy - WhenEmpty Only"]
        Budget["2. Disruption Budget - Max 20% Nodes"]
        PDB["3. PodDisruptionBudget - minAvailable: 50%"]
        Schedule["4. Schedule Restriction - Business Hours Block"]
        Monitor["5. Monitoring & Alerts - Real-time Detection"]
    end
    
    subgraph Result["Result"]
        Stable["Stable Service - No Disruption"]
    end
    
    Policy -> Budget
    Budget -> PDB
    PDB -> Schedule
    Schedule -> Monitor
    Monitor -> Stable
    
    style Policy fill:#e8f5e9
    style Budget fill:#e8f5e9
    style PDB fill:#e8f5e9
    style Schedule fill:#e8f5e9
    style Monitor fill:#e8f5e9
    style Stable fill:#c8e6c9
```

### 5.1 NodePool 설정 수정

> **참고**: Karpenter NodePool 설정 관련 내용은 [Karpenter 공식 문서](https://karpenter.sh/) 및 [Karpenter GitHub 저장소](https://github.com/aws/karpenter)를 참조하세요.
> 
> ```yaml
> # 수정된 NodePool 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 수정된 NodePool 설정
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
 name: default
spec:
 template:
 spec:
 nodeClassRef:
 group: karpenter.k8s.aws
 kind: EC2NodeClass
 name: default
 requirements:
 - key: karpenter.sh/capacity-type
 operator: In
 values: ["on-demand", "spot"]
 - key: kubernetes.io/arch
 operator: In
 values: ["amd64"]
 disruption:
 consolidationPolicy: WhenEmpty # 빈 노드만 삭제
 consolidateAfter: 5m # 5분 대기
 budgets:
 - nodes: "20%" # 최대 20%의 노드만 동시 삭제
 - nodes: "0"
 schedule: "0 9-18 * * 1-5" # 업무 시간에는 삭제 금지
 duration: 9h

```
-->

### 5.2 PodDisruptionBudget 적용

PodDisruptionBudget을 적용하여 Pod 보호:

```mermaid
graph LR
    subgraph Before["Before PDB"]
        Pod1["Pod 1"]
        Pod2["Pod 2"]
        Pod3["Pod 3"]
        Drain1["Karpenter - Drain All"]
    end
    
    subgraph After["After PDB"]
        Pod1P["Pod 1 - Protected"]
        Pod2P["Pod 2 - Protected"]
        Pod3P["Pod 3 - Protected"]
        PDB["PDB - minAvailable: 2"]
        Drain2["Karpenter - Respects PDB"]
    end
    
    Before -> Drain1
    Drain1 ->|"All Pods Terminated"| Failure["Service Failure"]
    
    After -> PDB
    PDB -> Drain2
    Drain2 ->|"Sequential Drain"| Stable["Service Stable"]
    
    style Drain1 fill:#ffebee
    style Failure fill:#ff5252
    style PDB fill:#e8f5e9
    style Drain2 fill:#e8f5e9
    style Stable fill:#c8e6c9
```

> **참고**: PodDisruptionBudget 설정 관련 내용은 [Kubernetes PDB 문서](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) 및 [Karpenter 문서](https://karpenter.sh/)를 참조하세요.
> 
> ```yaml
> # Critical 서비스용 PDB...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Critical 서비스용 PDB
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
 name: api-gateway-pdb
 namespace: prod
spec:
 minAvailable: 2
 selector:
 matchLabels:
 app: api-gateway
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
 name: order-service-pdb
 namespace: prod
spec:
 maxUnavailable: 1
 selector:
 matchLabels:
 app: order-service
---
# 전체 critical 서비스에 PDB 일괄 적용 스크립트
# deploy-pdbs.sh
for app in api-gateway order-service payment-service notification; do
 cat <<EOF | kubectl apply -f -
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
 name: ${app}-pdb
 namespace: prod
spec:
 maxUnavailable: 1
 selector:
 matchLabels:
 app: ${app}
EOF
done

```
-->

### 5.3 Pod Anti-Affinity 설정

> **참고**: Pod Anti-Affinity 설정 관련 내용은 [Kubernetes Pod Affinity 문서](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)를 참조하세요.
> 
> ```yaml
> # 같은 서비스의 Pod를 다른 노드에 분산...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 같은 서비스의 Pod를 다른 노드에 분산
apiVersion: apps/v1
kind: Deployment
metadata:
 name: api-gateway
spec:
 replicas: 3
 template:
 spec:
 affinity:
 podAntiAffinity:
 requiredDuringSchedulingIgnoredDuringExecution:
 - labelSelector:
 matchLabels:
 app: api-gateway
 topologyKey: kubernetes.io/hostname
 topologySpreadConstraints:
 - maxSkew: 1
 topologyKey: topology.kubernetes.io/zone
 whenUnsatisfiable: DoNotSchedule
 labelSelector:
 matchLabels:
 app: api-gateway

```
-->

## 6. 모니터링 강화

### 6.1 Karpenter 알림 설정

{% raw %}
> **참고**: Prometheus Alert Rules 관련 내용은 [Prometheus 공식 문서](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/) 및 [Awesome Prometheus Alerts](https://github.com/samber/awesome-prometheus-alerts)를 참조하세요.
> 
> ```yaml
> # Prometheus Alert Rules...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Prometheus Alert Rules
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
 name: karpenter-alerts
spec:
 groups:
 - name: karpenter
 rules:
 - alert: KarpenterHighDisruptionRate
 expr: |
 sum(rate(karpenter_nodes_terminated_total[5m])) > 2
 for: 2m
 labels:
 severity: warning
 annotations:
 summary: "Karpenter is terminating nodes rapidly"
 description: "{{ $value }} nodes terminated in last 5 minutes"

 - alert: KarpenterConsolidationActive
 expr: |
 karpenter_disruption_actions_performed_total{action="consolidate"} > 0
 for: 0m
 labels:
 severity: info
 annotations:
 summary: "Karpenter consolidation in progress"

```
-->
{% endraw %}

### 6.2 Datadog 대시보드

> **참고**: Datadog 모니터링 관련 내용은 [Datadog 공식 문서](https://docs.datadoghq.com/) 및 [Datadog Kubernetes 통합](https://docs.datadoghq.com/agent/kubernetes/)을 참조하세요.
> 
> ```yaml
> # Datadog Monitor...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Datadog Monitor
{
 "name": "[Karpenter] Node Disruption Alert",
 "type": "metric alert",
 "query": "sum(last_5m):sum:karpenter.nodes.terminated{*} > 3",
 "message": "Karpenter가 5분 내 3개 이상의 노드를 종료했습니다.\n\n@slack-platform-alerts",
 "tags": ["karpenter", "kubernetes", "critical"],
 "priority": 2,
 "options": {
 "thresholds": {
 "critical": 3,
 "warning": 2
 }
 }
}

```
-->

## 7. 재발 방지 체크리스트

| 항목 | 상태 | 담당자 |
|------|------|--------|
| NodePool consolidation 정책 완화 | ✅ | Platform |
| 업무시간 disruption 금지 설정 | ✅ | Platform |
| 모든 Critical 서비스 PDB 적용 | ✅ | DevOps |
| Pod Anti-Affinity 설정 | ✅ | DevOps |
| Karpenter 모니터링 알림 추가 | ✅ | SRE |
| 런북 업데이트 | ✅ | SRE |
| 팀 공유 및 교육 | ✅ | All |

## 8. 교훈 (Lessons Learned)

### 8.1 기술적 교훈

1. **기본값을 신뢰하지 말 것**: Karpenter의 기본 consolidation 정책은 프로덕션에 너무 공격적
2. **PDB는 필수**: Critical 서비스는 반드시 PodDisruptionBudget 설정
3. **점진적 적용**: 새로운 도구는 스테이징에서 충분히 테스트 후 적용
4. **가시성 확보**: 인프라 변경 도구는 반드시 모니터링과 알림 설정

### 8.2 프로세스 교훈

1. **변경 관리 강화**: Karpenter 설정 변경 시 Change Advisory Board 검토 필수
2. **런북 사전 준비**: "Karpenter 긴급 비활성화" 런북 사전 작성
3. **정기적 DR 훈련**: 인프라 장애 시나리오 훈련 분기별 실시

## 9. 마무리

이번 장애를 통해 **Kubernetes 오토스케일러의 위험성**과 **PDB의 중요성**을 다시 한번 깨달았습니다. 비용 최적화도 중요하지만, 서비스 안정성이 항상 우선되어야 합니다.

> "Move fast and break things" 는 프로덕션에서는 금물입니다.

---

📚 **참고 자료:**
- [Karpenter Disruption 공식 문서](https://karpenter.sh/docs/concepts/disruption/)
- [Kubernetes PDB Best Practices](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
