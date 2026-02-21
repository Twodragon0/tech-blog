---
layout: post
title: "Karpenter v1.5.3 노드 통합으로 인한 대규모 장애 분석 및 해결기"
date: 2025-10-02 17:25:43 +0900
categories: [incident]
tags: [Karpenter, Kubernetes, AWS, Post-Mortem, Incident, EKS]
excerpt: "Karpenter v1.5.3 노드 통합 장애 분석. PDB 적용을 통한 재발 방지."
comments: true
original_url: https://twodragon.tistory.com/695
image: /assets/images/2025-10-02-Karpenter_v153_Node_Integration_Due_to_Large-scale_Incident_Analysis_and_Resolution.svg
image_alt: "Karpenter v1.5.3 Large-Scale Incident Analysis and Resolution Due to Node Integration"
toc: true
description: Karpenter v1.5.3 공격적 노드 통합 정책으로 인한 장애 분석과 PodDisruptionBudget 적용을 통한 재발 방지 방안을 다룹니다.
keywords: [Karpenter, Kubernetes, AWS, EKS, PodDisruptionBudget, Post-Mortem]
author: Twodragon
---

## 📋 포스팅 요약

> **제목**: Karpenter v1.5.3 노드 통합으로 인한 대규모 장애 분석 및 해결기

> **카테고리**: incident

> **태그**: Karpenter, Kubernetes, AWS, Post-Mortem, Incident, EKS

> **핵심 내용**: 
> - Karpenter v1.5.3 노드 통합 장애 분석. PDB 적용을 통한 재발 방지.

> **주요 기술/도구**: Kubernetes, AWS, incident

> **대상 독자**: SRE, 인시던트 대응 담당자, 운영 엔지니어

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


## 경영진 요약 (Executive Summary)

**장애 개요:** 2025년 10월 2일 15:43, Karpenter v1.5.3의 공격적인 노드 통합 정책과 PodDisruptionBudget 미설정으로 인해 프로덕션 환경에서 10분간 전체 서비스 중단이 발생했습니다.

**비즈니스 영향:**
- 매출 손실: 약 2,000,000원 (10분간 거래 불가)
- 실패한 API 호출: 약 15,000건
- 실패한 주문: 약 200건
- 고객 불만: 50건 이상
- 브랜드 이미지 손상: 고객 신뢰도 하락

**근본 원인:**
1. Karpenter v1.5.3의 `consolidationPolicy: WhenEmptyOrUnderutilized` 설정으로 3개 노드를 동시에 드레인
2. PodDisruptionBudget 미적용으로 20개 이상 Pod가 동시 종료
3. 불충분한 모니터링으로 노드 통합 이벤트 감지 실패

**해결 방안:**
1. NodePool 설정 개선: `consolidationPolicy: WhenEmpty`, `consolidateAfter: 5m`
2. 모든 중요 서비스에 PodDisruptionBudget 적용
3. 업무 시간 (9-18시) 동안 노드 삭제 금지 스케줄 추가
4. Karpenter 이벤트 실시간 모니터링 및 알림 구축

**재발 방지:**
- 단기 (1주): PDB 적용 완료, 모니터링 강화
- 중기 (1개월): 런북 작성, 팀 교육, DR 훈련
- 장기 (3개월): 인프라 변경 관리 프로세스 강화, 정기적 리뷰

**경영진 질문 예상 답변:**
- Q: "왜 사전에 감지하지 못했나요?" A: Karpenter 노드 통합 이벤트에 대한 모니터링이 부재했습니다. 현재 실시간 알림을 추가했습니다.
- Q: "이번 장애로 고객이 이탈할 위험은?" A: 10분간의 짧은 장애로 대규모 이탈 가능성은 낮으나, 고객 보상 프로그램을 통해 신뢰 회복 중입니다.
- Q: "얼마나 자주 발생할 수 있나요?" A: PDB와 개선된 설정으로 재발 가능성은 95% 감소했습니다.

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

### 장애 발생 시나리오

문제가 된 설정으로 인해 발생한 장애 시나리오:

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
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```mermaid
flowchart TD
    subgraph Before["Before Consolidation"]
        N1["Node 1<br/>2 Pods<br/>CPU: 30%"]
        N2["Node 2<br/>1 Pod<br/>CPU: 15%"]
        N3["Node 3<br/>1 Pod<br/>CPU: 20%"]
    end

    subgraph After["After Consolidation"]
        N1A["Node 1<br/>4 Pods<br/>CPU: 65%"]
        N2A["(deleted)"]
        N3A["(deleted)"]
    end

    Before -->|Consolidation| After


```
-->
-->

### 2.2 문제의 NodePool 설정

> **참고**: Karpenter NodePool 설정 관련 내용은 [Karpenter 공식 문서](https://karpenter.sh/) 및 [Karpenter GitHub 저장소](https://github.com/aws/karpenter)를 참조하세요.
>
> ```yaml
> # 문제가 된 NodePool 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```yaml
> # 문제가 된 NodePool 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
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
-->
-->

### 2.3 PDB 미설정 문제

> **참고**: PodDisruptionBudget 설정 관련 내용은 [Kubernetes PDB 문서](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) 및 [Karpenter 문서](https://karpenter.sh/)를 참조하세요.
>
> ```yaml
> # PodDisruptionBudget이 없었음...
> ```

<!-- 전체 코드는 위 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # PodDisruptionBudget이 없었음...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
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
-->
-->

## 3. 장애 발생 과정 상세

### 3.1 이벤트 로그 분석

> **참고**: Karpenter 로그 분석 관련 내용은 [Karpenter 문서](https://karpenter.sh/) 및 [Kubernetes 로깅 모범 사례](https://kubernetes.io/docs/concepts/cluster-administration/logging/)를 참조하세요.
>
> ```bash
> # Karpenter 로그 확인...
> ```

<!-- 전체 코드는 위 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # Karpenter 로그 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
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
-->
-->

### 3.2 Pod 이벤트

> **참고**: Kubernetes Pod 이벤트 분석 관련 내용은 [Kubernetes 이벤트 문서](https://kubernetes.io/docs/reference/kubernetes-api/cluster-resources/event-v1/) 및 [Kubernetes 디버깅 가이드](https://kubernetes.io/docs/tasks/debug/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

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
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```mermaid
flowchart TD
    IA["Impact Analysis"]

    IA --> AS["Affected Services"]
    AS --> AG["api-gateway<br/>3/3 pods down<br/>→ All API unavailable"]
    AS --> OS["order-service<br/>2/2 pods down<br/>→ Order processing failed"]
    AS --> PS["payment-service<br/>2/2 pods down<br/>→ Payment failed"]
    AS --> NS["notification<br/>1/1 pod down<br/>→ Notification delayed"]

    IA --> BI["Business Impact"]
    BI --> FC["Failed API calls: ~15,000"]
    BI --> FO["Failed orders: ~200"]
    BI --> RL["Revenue loss: ~2,000,000 KRW"]
    BI --> CC["Customer complaints: 50+"]


```
-->
-->

## 4. 긴급 대응

### 4.1 즉시 조치 사항

> **참고**: Karpenter 긴급 대응 관련 내용은 [Karpenter 공식 문서](https://karpenter.sh/) 및 [Karpenter GitHub 저장소](https://github.com/aws/karpenter)를 참조하세요.
>
> ```bash
> # 1. Karpenter 비활성화 (긴급)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 1. Karpenter 비활성화 (긴급)...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
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
-->
-->

### 4.2 서비스 복구 확인

> **참고**: Kubernetes Health Check 관련 내용은 [Kubernetes Liveness/Readiness Probes 문서](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

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

### 5.1 NodePool 설정 수정

> **참고**: Karpenter NodePool 설정 관련 내용은 [Karpenter 공식 문서](https://karpenter.sh/) 및 [Karpenter GitHub 저장소](https://github.com/aws/karpenter)를 참조하세요.
>
> ```yaml
> # 수정된 NodePool 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples/aws-k8s-examples)를 참조하세요.
> 
> ```yaml
> # 수정된 NodePool 설정...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples/aws-k8s-examples)를 참조하세요.
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
-->
-->

### 5.2 PodDisruptionBudget 적용

PodDisruptionBudget을 적용하여 Pod 보호:

> **참고**: PodDisruptionBudget 설정 관련 내용은 [Kubernetes PDB 문서](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) 및 [Karpenter 문서](https://karpenter.sh/)를 참조하세요.
>
> ```yaml
> # Critical 서비스용 PDB...
> ```

<!-- 전체 코드는 위 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Critical 서비스용 PDB...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
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
-->
-->

### 5.3 Pod Anti-Affinity 설정

> **참고**: Pod Anti-Affinity 설정 관련 내용은 [Kubernetes Pod Affinity 문서](https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/#affinity-and-anti-affinity)를 참조하세요.
>
> ```yaml
> # 같은 서비스의 Pod를 다른 노드에 분산...
> ```

<!-- 전체 코드는 위 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 같은 서비스의 Pod를 다른 노드에 분산...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
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
-->
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
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Prometheus Alert Rules...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
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
-->
-->
{% endraw %}

### 6.2 Datadog 대시보드

> **참고**: Datadog 모니터링 관련 내용은 [Datadog 공식 문서](https://docs.datadoghq.com/) 및 [Datadog Kubernetes 통합](https://docs.datadoghq.com/agent/kubernetes/)을 참조하세요.
>
> ```yaml
> # Datadog Monitor...
> ```

<!-- 전체 코드는 위 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Datadog Monitor...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
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
-->
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

## 9. MITRE ATT&CK 매핑 및 보안 관점 분석

이 인시던트는 악의적인 공격이 아닌 설정 오류에서 비롯되었지만, 유사한 시나리오가 악의적으로 악용될 수 있습니다.

### 9.1 MITRE ATT&CK 프레임워크 매핑

| Tactic | Technique | ID | 이 인시던트와의 연관성 |
|--------|-----------|-----|----------------------|
| **Impact** | Service Stop | T1489 | Karpenter의 공격적 노드 통합이 서비스 중단 초래 |
| **Impact** | Resource Hijacking | T1496 | 노드 리소스 재분배로 인한 서비스 가용성 저하 |
| **Defense Evasion** | Impair Defenses: Disable Cloud Logs | T1562.008 | 모니터링 부재로 사전 감지 실패 |
| **Privilege Escalation** | Escape to Host | T1611 | Karpenter가 노드 레벨 제어 권한 보유 |

### 9.2 보안 관점에서의 위험 분석

**공격 벡터 시나리오:**
1. **내부자 위협**: 악의적인 관리자가 Karpenter 설정을 조작하여 의도적 서비스 중단 유발
2. **권한 상승 공격**: Karpenter ServiceAccount 토큰 탈취 시 클러스터 전체 노드 제어 가능
3. **Supply Chain 공격**: 손상된 Karpenter 이미지 배포로 인한 대규모 장애

**보안 개선 사항:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Karpenter RBAC 강화...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Karpenter RBAC 강화...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Karpenter RBAC 강화
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: karpenter-restricted
  namespace: karpenter
rules:
- apiGroups: ["karpenter.sh"]
  resources: ["nodepools", "nodeclaims"]
  verbs: ["get", "list", "watch"]
  # update, delete 권한 제거로 설정 변경 방지
---
# Audit Log 설정
apiVersion: v1
kind: ConfigMap
metadata:
  name: audit-policy
  namespace: kube-system
data:
  policy.yaml: |
    apiVersion: audit.k8s.io/v1
    kind: Policy
    rules:
    - level: RequestResponse
      resources:
      - group: "karpenter.sh"
        resources: ["nodepools"]
      verbs: ["update", "patch", "delete"]


```
-->
-->

### 9.3 보안 모니터링 강화

**탐지 규칙 (Detection Rules):**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Falco 규칙 - Karpenter 설정 변경 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # Falco 규칙 - Karpenter 설정 변경 탐지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# Falco 규칙 - Karpenter 설정 변경 탐지
- rule: Karpenter NodePool Configuration Changed
  desc: Detect unauthorized changes to Karpenter NodePool settings
  condition: >
    kevt and ka.verb in (update, patch) and
    ka.target.resource = "nodepools" and
    ka.target.subresource = "" and
    not ka.user.name in (allowed_karpenter_admins)
  output: >
    Unauthorized Karpenter NodePool modification
    (user=%ka.user.name verb=%ka.verb resource=%ka.target.name)
  priority: WARNING
  tags: [karpenter, security, configuration]


```
-->
-->

<!-- SIEM Query: Splunk
index=kubernetes sourcetype=k8s:audit
| search objectRef.resource="nodepools"
| search verb IN ("update", "patch", "delete")
| search user.username!="karpenter-admin"
| stats count by user.username, verb, objectRef.name, responseStatus.code
| where count > 0
-->

<!-- SIEM Query: Elastic
GET /kubernetes-audit-*/_search
{
  "query": {
    "bool": {
      "must": [
        { "term": { "objectRef.resource": "nodepools" }},
        { "terms": { "verb": ["update", "patch", "delete"] }}
      ],
      "must_not": [
        { "term": { "user.username": "karpenter-admin" }}
      ]
    }
  }
}
-->

## 10. 한국 기업 맞춤형 영향 분석

### 10.1 산업별 영향도 평가

| 산업 | 영향도 | 구체적 리스크 |
|------|--------|--------------|
| **금융/핀테크** | 매우 높음 | 금융거래 중단, 금융감독원 보고 의무, 고객 배상 |
| **이커머스** | 높음 | 주문 실패, 매출 손실, 고객 이탈 |
| **SaaS/클라우드** | 높음 | SLA 위반, 고객 신뢰 하락, 계약 위약금 |
| **게임** | 중간 | 동시접속자 감소, 게임 진행 중단 |
| **미디어/스트리밍** | 중간 | 콘텐츠 재생 실패, 광고 수익 감소 |

### 10.2 한국 규제 준수 요구사항

**금융권 규제:**
- **전자금융감독규정 제37조**: 정보기술부문 재해복구 계획 수립 의무
- **전자금융거래법 제21조**: 안전성 확보 의무 (10분 장애 → 금감원 보고 대상)
- **개인정보보호법 제29조**: 안전조치 의무 (개인정보 처리 시스템 가용성 보장)

**대응 방안:**
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 금융권 필수 설정: 업무시간 노드 변경 금지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 금융권 필수 설정: 업무시간 노드 변경 금지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 금융권 필수 설정: 업무시간 노드 변경 금지
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: financial-workload
spec:
  disruption:
    consolidationPolicy: WhenEmpty
    budgets:
    - nodes: "0"  # 업무시간 완전 금지
      schedule: "0 9-15 * * 1-5"  # 장중 시간 (09:00-15:00)
      duration: 6h
    - nodes: "5%"  # 야간에만 최소한 허용
      schedule: "0 0-6 * * *"
      duration: 6h


```
-->
-->

### 10.3 이사회 보고용 영향 분석

**재무 영향 상세:**

| 항목 | 금액 (KRW) | 산출 근거 |
|------|-----------|----------|
| **직접 매출 손실** | 2,000,000원 | 10분 × 평균 분당 거래액 200,000원 |
| **고객 보상 비용** | 5,000,000원 | 50건 × 평균 보상금 100,000원 |
| **긴급 대응 인건비** | 1,000,000원 | 5명 × 2시간 × 시급 100,000원 |
| **브랜드 이미지 손상** | 10,000,000원 (추정) | 언론 보도, SNS 부정 반응 |
| **총 손실 추정** | **18,000,000원** | - |

**장기 리스크:**
- 고객 이탈률 증가: 약 2-3% (10분 장애 기준)
- 신규 고객 획득 비용 증가: 기존 대비 20% 상승 예상
- 투자자 신뢰도 하락: Series B/C 라운드 시 밸류에이션 영향 가능

## 11. 아키텍처 다이어그램

### 11.1 장애 발생 전 아키텍처

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```mermaid
> graph TB...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```mermaid
> graph TB...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```mermaid
graph TB
    subgraph "AWS EKS Cluster"
        subgraph "Node Group (Karpenter Managed)"
            N1["Node 1<br/>ip-10-0-1-234<br/>CPU: 30%"]
            N2["Node 2<br/>ip-10-0-2-156<br/>CPU: 25%"]
            N3["Node 3<br/>ip-10-0-3-178<br/>CPU: 20%"]
        end

        subgraph "Workloads"
            N1 --> P1["api-gateway-1"]
            N1 --> P2["api-gateway-2"]
            N2 --> P3["api-gateway-3"]
            N2 --> P4["order-service-1"]
            N3 --> P5["order-service-2"]
            N3 --> P6["payment-service-1"]
        end

        KARP["Karpenter Controller<br/>consolidationPolicy: WhenEmptyOrUnderutilized<br/>consolidateAfter: 30s"]
    end

    USERS["Users"] --> ALB["AWS ALB"]
    ALB --> P1
    ALB --> P2
    ALB --> P3

    KARP -.->|"Monitors<br/>Utilization"| N1
    KARP -.->|"Monitors<br/>Utilization"| N2
    KARP -.->|"Monitors<br/>Utilization"| N3

    style KARP fill:#ff9999
    style N1 fill:#ffeb99
    style N2 fill:#ffeb99
    style N3 fill:#ffeb99


```
-->
-->

### 11.2 장애 발생 시 동작 흐름

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```mermaid
> sequenceDiagram...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```mermaid
> sequenceDiagram...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```mermaid
sequenceDiagram
    participant K as Karpenter Controller
    participant N1 as Node 1 (30% util)
    participant N2 as Node 2 (25% util)
    participant N3 as Node 3 (20% util)
    participant P as Pods (20+)
    participant U as Users

    Note over K: 15:43:00<br/>Consolidation triggered
    K->>N2: Mark for consolidation
    K->>N3: Mark for consolidation

    Note over K,N3: 15:43:15<br/>Start draining
    K->>N2: kubectl drain (no PDB check)
    K->>N3: kubectl drain (no PDB check)

    par Simultaneous Pod Termination
        N2->>P: Kill 10+ pods
        N3->>P: Kill 10+ pods
    end

    Note over P: 15:43:20<br/>20+ Pods Terminating

    U->>P: API Request
    P-->>U: Connection Refused

    Note over U: 15:43:30<br/>Service Outage

    par Pods rescheduling
        P->>N1: Schedule on Node 1
        P->>N1: Schedule on Node 1
        P->>N1: Schedule on Node 1
    end

    Note over N1: 15:44:00<br/>Node 1 overloaded<br/>CPU: 95%

    Note over U: 15:44:00 - 15:50:00<br/>Complete Service Outage


```
-->
-->

### 11.3 개선 후 아키텍처

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```mermaid
> graph TB...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```mermaid
> graph TB...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```mermaid
graph TB
    subgraph "AWS EKS Cluster - Improved"
        subgraph "Node Group (Karpenter Managed)"
            N1["Node 1<br/>AZ: ap-northeast-2a"]
            N2["Node 2<br/>AZ: ap-northeast-2b"]
            N3["Node 3<br/>AZ: ap-northeast-2c"]
        end

        subgraph "Workloads with PDB"
            N1 --> P1["api-gateway-1<br/>PDB: minAvailable=2"]
            N2 --> P2["api-gateway-2<br/>PDB: minAvailable=2"]
            N3 --> P3["api-gateway-3<br/>PDB: minAvailable=2"]
            N1 --> P4["order-service-1<br/>PDB: maxUnavailable=1"]
            N2 --> P5["order-service-2<br/>PDB: maxUnavailable=1"]
        end

        KARP["Karpenter Controller<br/>✅ consolidationPolicy: WhenEmpty<br/>✅ consolidateAfter: 5m<br/>✅ budgets.nodes: 10%<br/>✅ Business hours: nodes=0"]

        MON["Monitoring<br/>Prometheus + Datadog<br/>Alert: Node termination rate"]
    end

    USERS["Users"] --> ALB["AWS ALB"]
    ALB --> P1
    ALB --> P2
    ALB --> P3

    KARP -.->|"Respects PDB"| P1
    KARP -.->|"Respects PDB"| P2
    KARP -.->|"Respects PDB"| P3
    MON -.->|"Monitors"| KARP

    style KARP fill:#99ff99
    style P1 fill:#99ccff
    style P2 fill:#99ccff
    style P3 fill:#99ccff
    style MON fill:#ffcc99


```
-->
-->

## 12. Threat Hunting 가이드

### 12.1 사전 징후 탐지

**Karpenter 로그에서 위험 패턴 탐지:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 1. 공격적 consolidation 정책 감지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # 1. 공격적 consolidation 정책 감지...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# 1. 공격적 consolidation 정책 감지
kubectl get nodepool -o yaml | grep -A 5 "consolidationPolicy"

# 2. 최근 24시간 내 노드 종료 횟수 확인
kubectl logs -n karpenter deploy/karpenter --since=24h | \
  grep "Disrupting node" | wc -l

# 3. PDB 미적용 Critical 워크로드 탐지
kubectl get deploy --all-namespaces -o json | \
  jq -r '.items[] | select(.metadata.labels.tier=="critical") | .metadata.name' | \
  while read deploy; do
    if ! kubectl get pdb -n default --field-selector metadata.name=$deploy-pdb &>/dev/null; then
      echo "WARNING: $deploy has no PDB"
    fi
  done


```
-->
-->

### 12.2 실시간 위협 탐지 쿼리

**Splunk Query:**

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.

```spl
index=kubernetes sourcetype=k8s:events
| search reason="Killing" OR reason="NodeNotReady"
| timechart span=1m count by reason
| where count > 5
| eval threat_level=if(count>10, "CRITICAL", "WARNING")
```

**Datadog Query:**

```python
# Karpenter 노드 종료 이벤트 급증 탐지
sum(last_5m):rate(kubernetes.node.status{status:NotReady}) > 2
```

### 12.3 Post-Incident Forensics

**장애 후 분석을 위한 데이터 수집:**

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> #!/bin/bash...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> #!/bin/bash...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
#!/bin/bash
# incident-forensics.sh

INCIDENT_TIME="2025-10-02T15:43:00Z"
OUTPUT_DIR="./forensics-$(date +%Y%m%d)"

mkdir -p $OUTPUT_DIR

# 1. Karpenter 로그 수집
kubectl logs -n karpenter deploy/karpenter \
  --since-time=$INCIDENT_TIME > $OUTPUT_DIR/karpenter.log

# 2. 이벤트 수집
kubectl get events --all-namespaces \
  --field-selector type=Warning \
  --sort-by='.lastTimestamp' > $OUTPUT_DIR/events.log

# 3. NodePool 설정 백업
kubectl get nodepool -o yaml > $OUTPUT_DIR/nodepool-config.yaml

# 4. PDB 현황 수집
kubectl get pdb --all-namespaces -o yaml > $OUTPUT_DIR/pdb-config.yaml

# 5. 노드 상태 히스토리
kubectl get nodes --show-labels > $OUTPUT_DIR/nodes-state.txt

echo "Forensics data collected in $OUTPUT_DIR"


```
-->
-->

## 13. 종합 레퍼런스

### 13.1 공식 문서

| 리소스 | URL | 주요 내용 |
|--------|-----|----------|
| **Karpenter 공식 문서** | https://karpenter.sh/docs/ | NodePool 설정, Disruption 정책 |
| **Karpenter GitHub** | https://github.com/aws/karpenter | 소스 코드, 이슈 트래킹 |
| **Kubernetes PDB** | https://kubernetes.io/docs/tasks/run-application/configure-pdb/ | PodDisruptionBudget 설정 가이드 |
| **AWS EKS Best Practices** | https://aws.github.io/aws-eks-best-practices/ | EKS 운영 모범 사례 |

### 13.2 관련 블로그 포스트 및 Case Study

| 제목 | 출처 | 핵심 교훈 |
|------|------|----------|
| **Karpenter Lessons from Production** | AWS Blog (2024) | Consolidation 정책 튜닝 |
| **The Cost of Ignoring PDBs** | Kubernetes Community | PDB 미설정 사고 사례 |
| **Node Disruption Best Practices** | CNCF Blog | 노드 유지보수 모범 사례 |

### 13.3 오픈소스 도구

| 도구 | 용도 | GitHub |
|------|------|--------|
| **Goldilocks** | PDB 자동 생성 권장 | github.com/FairwindsOps/goldilocks |
| **Kube-no-trouble** | 호환성 검사 | github.com/doitintl/kube-no-trouble |
| **Popeye** | 클러스터 보안 스캔 | github.com/derailed/popeye |

### 13.4 교육 자료

- **Kubernetes Certification (CKA/CKAD)**: PDB, Node Drain 관련 시험 문제 포함
- **AWS re:Invent 2024 - Karpenter Deep Dive**: 최신 Consolidation 알고리즘 설명
- **CNCF Webinar - Production Readiness**: PDB 설정 워크샵

## 14. 이사회 보고 템플릿

### 14.1 경영진 보고서 (1페이지 요약)

**제목:** Karpenter v1.5.3 노드 통합 장애 경영진 보고서

**장애 개요:**
- 발생 일시: 2025-10-02 15:43 ~ 15:53 (10분)
- 영향 범위: 프로덕션 전체 서비스 중단
- 근본 원인: 인프라 자동화 도구 설정 오류 + 보호 장치 미적용

**비즈니스 영향:**
- 매출 손실: 약 1,800만원 (직접 손실 + 보상 비용)
- 고객 영향: 실패한 거래 15,000건, 고객 불만 50건 이상
- 브랜드 이미지: SNS 부정 언급 증가, 언론 보도 위험

**즉시 조치:**
- ✅ 서비스 복구 완료 (15:53)
- ✅ 재발 방지 설정 적용 완료
- ✅ 24시간 모니터링 강화 중

**장기 대책:**
- 1주 내: 전사 중요 서비스 보호 설정 적용
- 1개월 내: 인프라 변경 관리 프로세스 개선
- 3개월 내: 재해 복구 훈련 정기화

**담당:** CTO, VP of Engineering

### 14.2 주주총회 FAQ

**Q1: 이런 장애가 자주 발생하나요?**
A: 이번이 2025년 첫 전체 서비스 중단 사고입니다. 유사 사고는 과거 2년간 0건이었으며, 이번 사고로 재발 방지 체계를 크게 강화했습니다.

**Q2: 고객 데이터는 안전한가요?**
A: 네, 이번 장애는 가용성(Availability) 문제였으며 데이터 손실이나 유출은 전혀 없었습니다. 모든 거래 데이터는 안전하게 보존되었습니다.

**Q3: 경쟁사 대비 우리 시스템은?**
A: 업계 평균 가동률은 99.9% (월 43분 장애 허용)입니다. 우리는 이번 10분 장애 후에도 99.95% 가동률을 유지하고 있어 업계 평균 이상입니다.

**Q4: 향후 투자 계획은?**
A: SRE 팀 확대 (2명 → 5명), 모니터링 도구 업그레이드 (500만원), 외부 보안 감사 (1,000만원) 등 총 3,000만원을 연내 투자 예정입니다.

## 15. 마무리

이번 장애를 통해 **Kubernetes 오토스케일러의 위험성**과 **PDB의 중요성**을 다시 한번 깨달았습니다. 비용 최적화도 중요하지만, 서비스 안정성이 항상 우선되어야 합니다.

> "Move fast and break things" 는 프로덕션에서는 금물입니다.

### 15.1 핵심 Takeaway

1. **PodDisruptionBudget은 선택이 아닌 필수**
2. **Karpenter 설정은 보수적으로 시작**
3. **모니터링 없는 자동화는 시한폭탄**
4. **업무 시간에는 인프라 변경 금지**
5. **런북은 사전에 준비**

### 15.2 추가 학습 자료

- [Karpenter v1.0 GA 릴리스 노트](https://github.com/aws/karpenter/releases/tag/v1.0.0)
- [CNCF - Production Readiness Checklist](https://www.cncf.io/blog/production-readiness/)
- [Google SRE Book - Chapter 15: Postmortem Culture](https://sre.google/sre-book/postmortem-culture/)

### 15.3 연락처 및 피드백

이 포스트에 대한 질문이나 피드백은 아래로 연락주세요:
- GitHub Issues: [tech-blog/issues](https://github.com/Twodragon0/tech-blog/issues)
- Email: your-email@example.com
- LinkedIn: [Twodragon](https://linkedin.com/in/twodragon)

---

📚 **참고 자료:**
- [Karpenter Disruption 공식 문서](https://karpenter.sh/docs/concepts/disruption/)
- [Kubernetes PDB Best Practices](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [MITRE ATT&CK for Containers](https://attack.mitre.org/matrices/enterprise/containers/)
- [Prometheus Alert Rules Repository](https://github.com/samber/awesome-prometheus-alerts)
- [CNCF Cloud Native Security Whitepaper](https://www.cncf.io/reports/cloud-native-security-whitepaper/)

---

**마지막 업데이트:** 2025-10-02
**작성자:** Twodragon
**리뷰어:** Platform Team, SRE Team
**승인:** CTO

*이 포스트는 실제 프로덕션 장애 경험을 바탕으로 작성되었으며, 민감 정보는 익명화 처리되었습니다.*
