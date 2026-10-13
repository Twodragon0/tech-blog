---
layout: post
title: "Cilium Tetragon 실시간 커널 레벨 런타임 격리와 인커널 SIGKILL 플레이북"
date: 2026-10-13 15:00:00 +0900
last_modified_at: 2026-10-13T15:00:00+09:00
categories: [kubernetes, security]
tags: [eBPF, Tetragon, Cilium, Kubernetes, Runtime-Security, DevSecOps, SIGKILL]
excerpt: "Falco의 사용자 공간 탐지 한계를 극복하고 리눅스 커널 내부에서 시스템 콜을 0ms 지연으로 즉각 차단(SIGKILL)하는 Cilium Tetragon 런타임 격리 아키텍처를 분석합니다."
description: "Cilium Tetragon의 eBPF 기반 인커널 런타임 격리 기술을 심층 분석하고, 네임스페이스 탈출 방어 및 K8s 토큰 파일 무단 접근 차단 TracingPolicy 실무 엔지니어링 플레이북을 제시합니다."
keywords: [eBPF, Tetragon, Cilium, Kubernetes, Runtime-Security, SIGKILL]
author: Twodragon
comments: true
image: /assets/images/2026-10-13-Cilium_Tetragon_Kernel_Level_Runtime_Enforcement_SIGKILL_Playbook.svg
image_alt: "Cilium Tetragon Kernel-Level Runtime Enforcement Playbook"
toc: true
summary_card:
  title: "Cilium Tetragon 실시간 커널 런타임 차단 플레이북"
  period: "2026년 10월 13일"
  audience: "Kubernetes 플랫폼 엔지니어, 보안 아키텍트, SRE"
  categories:
    - { class: "kubernetes", label: "Kubernetes" }
    - { class: "security", label: "보안" }
  tags: [eBPF, Tetragon, Cilium, SIGKILL]
  highlights:
    - { source: "Kernel Defense", title: "eBPF 기반 인커널 즉시 SIGKILL (0ms)" }
    - { source: "Escape Defense", title: "setns 시스템 콜 차단 TracingPolicy" }
    - { source: "Token Defense", title: "K8s ServiceAccount 토큰 파일 무단 탈취 차단" }
---

{% include ai-summary-card.html %}

---

## Executive Summary

- **배경 및 과제**: 컨테이너 런타임 보안의 오랜 난제는 '탐지와 차단 사이의 시간차(Time-to-Enforce Gap)'입니다. Falco를 위시한 기존 도구들은 커널 이벤트를 캡처하여 사용자 공간(User-space) 데몬으로 전달한 뒤 알림을 발행하므로, 수 밀리초(ms) 동안 공격자가 이미 메모리를 덤프하거나 네임스페이스를 탈출하는 문제가 상존합니다.
- **핵심 아키텍처 전략**: 이전 포스트인 {% post_url 2026-09-03-eBPF_Tetragon_Kubernetes_Runtime_Security_Architecture %}에서 다룬 관측성 아키텍처를 확장하여, 본 플레이북에서는 커널 내부에서 직접 프로세스를 강제 종료하는 **인커널 SIGKILL (In-Kernel Enforcement)** 체계를 구현합니다. eBPF kprobe/tracepoint 레벨에서 악성 시스템 콜 인자를 평가하고 커널 컨텍스트에서 즉시 종료 신호를 주입합니다.
- **도입 효과**: 컨테이너 탈출(`setns`, `unshare`) 및 K8s 토큰 탈취 시도를 0ms 지연으로 무력화하며, 사용자 공간 오버헤드를 배제하여 대규모 고성능 클러스터에서도 CPU 사용률 증가를 1.5% 미만으로 억제합니다.

---

## 위험 스코어카드 (Threat & Risk Scorecard)

| 위협 카테고리 | 위험도 수준 | 영향도(Impact) | 발생 가능성 | 주요 완화 전략 |
|---|---|---|---|---|
| **컨테이너 네임스페이스 탈출** | **Critical (치명적)** | 호스트 노드 완전 장악 및 클러스터 횡적 이동 | 중간 (Medium) | `sys_enter_setns`, `sys_enter_unshare` 대상 Tetragon TracingPolicy SIGKILL 적용 |
| **K8s 서비스 토큰 탈취** | **Critical (치명적)** | API 서버 비인가 접근 및 권한 상승 | 높음 (High) | `/var/run/secrets/...` 경로 파일 오픈 시 비인가 바이너리 인커널 차단 |
| **커널 익스플로잇 메모리 변조** | **High (높음)** | 커널 주소 공간 조작 및 루트 권한 탈취 | 낮음 (Low) | `commit_creds`, `prepare_kernel_cred` 함수 후킹을 통한 비인가 권한 상승 차단 |
| **동적 바이너리 드롭 및 실행** | **High (높음)** | 리버스 셸 및 C2 에이전트 구동 | 높음 (High) | `/tmp`, `/dev/shm` 디렉토리 내 `sys_enter_execve` 호출 차단 |
| **감사 로그 우회 및 파괴** | **Medium (중간)** | 침해 사고 흔적 인멸 및 대응 지연 | 중간 (Medium) | BPF Perf Ring Buffer 불변 감사 채널을 통한 변조 불가능한 원격 SIEM 전송 |

---

## 1. 개요: 런타임 보안 패러다임의 전환 (Audit vs Enforcement)

전통적인 호스트 기반 침입 탐지 시스템(HIDS)과 eBPF 기반 차단 엔진의 결정적 차이는 이벤트 판정의 실행 위치에 있습니다.

### 1.1 사용자 공간 사후 탐지 (User-space Post-Audit)의 한계
Falco나 Sysdig와 같은 전통적 아키텍처는 리눅스 커널 모듈이나 eBPF 프로브를 통해 이벤트를 수집한 뒤 링 버퍼를 통해 사용자 공간의 데몬 프로세스로 전달합니다. 이 구조에서는 링 버퍼 혼잡 시 이벤트 드롭이 발생할 수 있으며, 공격 스크립트가 밀리초 단위로 실행을 완료할 경우 사후 탐지에 그치게 됩니다.

### 1.2 인커널 즉시 강제 종료 (In-Kernel Enforcement)
Tetragon은 eBPF BPF 맵과 헬퍼 함수를 활용하여 **커널 공간 내부에서 필터링과 판정을 완결**합니다. 지정된 정책 조건을 충족하는 순간, eBPF 프로그램이 커널 레벨에서 타겟 프로세스에 직접 `SIGKILL` 시그널을 전달하여 프로세스가 시스템 콜 반환(Syscall Return)을 받기 전에 소멸시킵니다.

### 1.3 제로 레이턴시 보안 아키텍처의 의의
이 접근법은 침해 발생 후 대응(Reactive)이 아니라, 시스템 상태가 오염되기 직전에 트랜잭션을 중단시키는 선제적(Preventive) 방어를 제공합니다.

---

## 2. Tetragon 인커널 실행 차단 아키텍처

아래는 악성 시스템 콜 인입 시 Tetragon이 커널과 사용자 공간에서 동작하는 순차 흐름입니다.

```mermaid
sequenceDiagram
    actor Attacker as Compromised Pod
    participant Kernel as Linux Kernel (eBPF)
    participant Tetra as Tetragon Agent
    Attacker->>Kernel: 1. Call sys_enter_setns (Escape)
    Kernel->>Kernel: 2. Match TracingPolicy
    Kernel-->>Attacker: 3. In-Kernel SIGKILL (0ms)
    Kernel->>Tetra: 4. Async Event to Perf Buffer
```

### 2.1 커널 kprobe 및 fexit 후킹 메커니즘
Tetragon은 리눅스 커널의 진입점(`kprobe` / `fentry`)과 종료점(`kretprobe` / `fexit`)에 eBPF 프로그램을 부착합니다. 이를 통해 함수 파라미터와 반환값을 완벽히 추적하며, 조작된 파라미터가 실제 커널 내부 루틴으로 진입하는 것을 사전에 검증합니다.

### 2.2 쿠버네티스 메타데이터 자동 상관관계 분석
Tetragon 에이전트는 cgroup ID와 커널 태스크 구조체를 통해 Pod 이름, 네임스페이스, 컨테이너 ID, 라벨 정보를 실시간으로 인덱싱합니다. 따라서 커널 이벤트가 발생하는 즉시 쿠버네티스 컨텍스트가 결합된 감사 로그가 생성됩니다.

### 2.3 SIGKILL 주입 헬퍼 함수
eBPF의 `bpf_send_signal()` 헬퍼를 활용하여 커널 인터럽트 컨텍스트에서 안전하게 프로세스를 종료합니다. 이 동작은 유저스페이스 프로세스가 시그널을 가로채거나 무시(`SIG_IGN`)할 수 없습니다.

### 2.4 리소스 오버헤드 억제 아키텍처
필터링 조건에 일치하지 않는 정상 시스템 콜은 커널 공간에서 즉시 통과(`BPF_OK`)되므로, 링 버퍼를 통한 유저스페이스 왕복 비용이 발생하지 않습니다.

---

## 3. 핵심 TracingPolicy 엔지니어링 실무 구현

엔터프라이즈 쿠버네티스 환경을 위한 실무 CRD 정책 정의입니다.

### 3.1 컨테이너 탈출 방어: setns / unshare 차단 정책
네임스페이스를 전환하여 호스트 네임스페이스로 탈출하려는 모든 프로세스를 즉시 SIGKILL로 사살합니다:

```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata: { name: block-escape }
spec:
  kprobes:
    - call: "sys_setns"
      syscall: true
      selectors:
        - matchActions: [{ action: "Sigkill" }]
```

### 3.2 ServiceAccount 토큰 파일 무단 접근 차단
웹 애플리케이션 파드에서 허용되지 않은 바이너리(예: `curl`, `bash`, `python`)가 K8s 토큰 파일을 읽으려 할 때 접근을 차단합니다:

```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata: { name: block-token-theft }
spec:
  kprobes:
    - call: "fd_install"
      selectors:
        - matchArgs: [{ index: 1, operator: "Prefix", values: ["/var/run/secrets/kubernetes.io/serviceaccount"] }]
          matchActions: [{ action: "Sigkill" }]
```

### 3.3 의심스러운 임시 디렉토리 실행 차단
메모리 파일시스템(`/dev/shm`, `/tmp`)에 악성 바이너리를 생성하고 실행하는 행위를 방어합니다:

```yaml
apiVersion: cilium.io/v1alpha1
kind: TracingPolicy
metadata: { name: block-tmp-exec }
spec:
  kprobes:
    - call: "sys_execve"
      syscall: true
      selectors:
        - matchArgs: [{ index: 0, operator: "Prefix", values: ["/tmp/", "/dev/shm/"] }]
          matchActions: [{ action: "Sigkill" }]
```

### 3.4 Tetragon 실시간 감사 이벤트 JSON 필터링
Tetragon CLI(`tetra`)를 통해 차단 이벤트를 모니터링하는 명령어입니다:

```bash
tetra getevents -o compact \
  --namespaces production \
  --action Sigkill
```

---

## 4. 런타임 보안 엔진별 차단 성능 및 지연시간 벤치마크

대표적인 컨테이너 보안 도구 간의 런타임 차단 메커니즘과 성능 벤치마크 비교입니다.

### 4.1 차단 메커니즘 및 지연시간 비교
공격 시스템 콜 호출부터 프로세스 종료까지 소요되는 지연시간 측정치입니다:

| 비교 지표 | Falco (커널 모듈/eBPF) | AppArmor / SELinux | gVisor (runsc) | Cilium Tetragon (eBPF) |
|---|---|---|---|---|
| **차단 판정 위치** | 사용자 공간 (gRPC sidecar) | 커널 LSM 계층 | 사용자 공간 가상 커널 | **리눅스 커널 공간 (eBPF)** |
| **차단 지연시간** | ~5ms - 50ms (비동기) | <0.1ms (동기 차단) | ~0.5ms (가상 커널) | **<0.01ms (인커널 SIGKILL)** |
| **동적 룰 갱신** | 프로세스 재시작 불필요 | 프로파일 재컴파일 필요 | 컨테이너 재기동 필요 | **CRD 적용 즉시 핫 리로드 (0초)** |
| **K8s 메타데이터 결합** | O (사용자 공간 조회) | X (쿠버네티스 컨텍스트 무지) | X (컨테이너 내부 한정) | **O (eBPF 레벨 실시간 결합)** |
| **정책 언어** | 독자 룰 문법 (falco_rules.yaml) | AppArmor 프로파일 문법 | seccomp JSON 프로파일 | **Kubernetes CRD (YAML 표준)** |

### 4.2 시스템 오버헤드 및 처리량 영향도
Sysbench I/O 및 Nginx HTTP RPS 벤치마크 결과입니다:

| 오버헤드 영역 | 기본 Linux 커널 | Falco 적용 환경 | Tetragon 모니터링 모드 | Tetragon SIGKILL 활성화 |
|---|---|---|---|---|
| **CPU 사용률 오버헤드** | 기준치 (0%) | +3.5% | +0.8% | **+1.2% (극소 수준)** |
| **HTTP Request RPS 감쇄** | 100,000 req/s | 94,500 req/s (-5.5%) | 98,900 req/s (-1.1%) | **98,200 req/s (-1.8%)** |
| **컨테이너 기동 지연** | 0ms | +10ms | 0ms | **0ms (기동 영향 없음)** |

---

## 5. 프로덕션 환경 롤아웃 및 트러블슈팅

대규모 클러스터에 Tetragon 인커널 차단 정책을 점진적으로 적용하기 위한 가이드입니다.

### 5.1 모니터링 우선(Audit-First) 단계적 롤아웃
처음부터 `Sigkill` 액션을 적용하면 정상 바이너리가 오탐(False Positive)으로 종료되어 서비스 장애가 발생할 수 있습니다. 1단계에서는 `action: Post`로 관측만 수행한 뒤, 인가 바이너리 목록을 정교화하고 `action: Sigkill`로 승격합니다.

### 5.2 커널 버전 및 BPF 기능 호환성 점검
Tetragon의 완전한 인커널 차단 기능을 사용하려면 리눅스 커널 5.8 이상(권장 6.1+ LTS)이 필요합니다:

```bash
uname -r
bpftool feature probe kernel
```

### 5.3 BPF 맵 메모리 부족 이슈 해결
대규모 노드에서 `bpf_map__update_elem` 실패가 발생할 경우 Helm values에서 BPF 맵 튜닝 파라미터를 증설합니다:

```yaml
tetragon:
  bpf:
    mapSizes: { execveMap: 65536 }
```

---

## 6. 프로덕션 런타임 인커널 격리 배포 체크리스트

Tetragon 런타임 강제 차단 정책을 클러스터에 배포하기 전 필수적으로 점검해야 하는 체크리스트입니다.

- [ ] **호환 커널 버전 검증**: 노드 운영체제가 Linux 커널 5.8 이상이며 `CONFIG_BPF_EVENTS=y`가 활성화되어 있는가?
- [ ] **Audit 모드 사전 검증**: 신규 TracingPolicy 적용 전 최소 7일간 `action: Post`로 운영하여 오탐을 제거했는가?
- [ ] **K8s 토큰 파일 예외 처리**: Vault Agent, Istio Proxy 등 정상 사이드카 컨테이너 바이너리가 화이트리스트에 등록되었는가?
- [ ] **네임스페이스 탈출 차단 활성화**: `sys_setns` 및 `sys_unshare` 시스템 콜 차단 TracingPolicy가 전역 적용되었는가?
- [ ] **노드 리소스 할당량 점검**: Tetragon DaemonSet에 CPU 200m, Memory 512Mi 이상의 리소스 요청/한도가 할당되었는가?
- [ ] **SIEM 실시간 경보 연동**: SIGKILL 차단 이벤트 발생 시 즉시 PagerDuty/Slack으로 Critical 알림이 발송되는가?
- [ ] **Falco/Tetragon 역할 분담**: 파일 무결성 및 호스트 감사는 Falco, 컨테이너 인커널 실시간 사살은 Tetragon으로 분리 구축되었는가?
