---
layout: post
title: "Tech & Security Weekly Digest: Notepad++ 국가 지원 공급망 공격, Bitcoin $80K 붕괴, AI Agent 스케일링 과학"
date: 2026-02-02 10:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, Supply-Chain, Notepad++, Bitcoin-Crash, AI-Agent, Amazon-Bedrock, Google-Research, HashiCorp, FOSDEM-2026, "2026"]
excerpt: "Notepad++ 국가 지원 해킹 그룹 공급망 공격 분석, Bitcoin $80K 이하 급락과 DeFi 청산 연쇄, Google Research AI Agent 스케일링 법칙, Amazon Bedrock AgentCore 멀티에이전트 아키텍처"
description: "2026년 2월 2일 보안/기술 뉴스: Notepad++ 공급망 공격(T1195), Bitcoin 주말 대폭락($19B 청산), Google AI Agent 스케일링 연구, Amazon Bedrock AgentCore, HashiCorp Boundary 0.21, FOSDEM 2026"
keywords: [Notepad++ Supply Chain Attack, Bitcoin Crash 2026, AI Agent Scaling, Amazon Bedrock AgentCore, Google Research Agents, HashiCorp Boundary, FOSDEM 2026, Ethereum Quantum Security]
author: Twodragon
comments: true
image: /assets/images/2026-02-02-Tech_Security_Weekly_Digest_Notepadpp_Hijack_Bitcoin_Crash_AI_Agents.svg
image_alt: "Tech Security Weekly Digest Feb 2 2026 Notepad++ Hijack Bitcoin Crash AI Agents"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Tech & Security Weekly Digest (2026년 02월 02일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Supply-Chain</span>
      <span class="tag">Notepad++</span>
      <span class="tag">Bitcoin-Crash</span>
      <span class="tag">AI-Agent</span>
      <span class="tag">Amazon-Bedrock</span>
      <span class="tag">Google-Research</span>
      <span class="tag">HashiCorp</span>
      <span class="tag">FOSDEM-2026</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>Notepad++ 국가 지원 공급망 공격</strong>: 국가 배후 해킹 그룹이 Notepad++ 배포 인프라를 침해, 수백만 개발자에게 영향 가능한 공급망 공격 발생</li>
      <li><strong>Bitcoin $80K 이하 급락</strong>: 주말 동안 $19B 규모 청산 연쇄, 단일 트레이더 $220M 손실, DeFi 프로토콜 연쇄 영향</li>
      <li><strong>Google Research AI Agent 스케일링</strong>: 에이전트 시스템의 확장 법칙과 실효성 조건을 규명한 연구 발표</li>
      <li><strong>Amazon Bedrock AgentCore</strong>: 항공사 시나리오 기반 멀티에이전트 오케스트레이션 및 접근 제어 아키텍처</li>
    </ul>
  </div>
</div>
</div>

## 개요

2026년 2월 첫 주말, 보안과 금융 양쪽에서 대형 사건이 동시에 터졌습니다. **국가 지원 해킹 그룹이 Notepad++의 배포 인프라를 침해**하여 전 세계 개발자와 시스템 관리자를 대상으로 공급망 공격을 감행한 사실이 확인되었습니다. Hacker News에서 304 포인트를 기록할 만큼 커뮤니티에 큰 충격을 준 이 사건은, 일상적으로 사용하는 텍스트 에디터마저 국가 수준의 위협으로부터 안전하지 않다는 현실을 보여줍니다.

암호화폐 시장에서는 **Bitcoin이 $80,000 아래로 급락**하며 주말 동안 약 $19B 규모의 청산이 발생했습니다. 단일 트레이더가 Ether 급락으로 $220M을 잃었고, DeFi 프로토콜 전반에 청산 연쇄가 확산되었습니다. Ethereum Foundation은 양자 컴퓨팅 위협에 대응하여 LeanVM과 Post-Quantum 서명 도입을 우선순위로 격상시켰습니다.

AI 에이전트 분야에서는 **Google Research가 에이전트 시스템의 스케일링 과학**을 발표하며 "언제, 왜 에이전트 시스템이 작동하는가"라는 근본적 질문에 답했고, **Amazon은 Bedrock AgentCore 기반 멀티에이전트 아키텍처**의 실전 운영 패턴을 공개했습니다. 인프라 측면에서는 HashiCorp이 Boundary 0.21의 패스워드리스 RDP와 VSO의 etcd-free 시크릿 관리를 발표했으며, FOSDEM 2026이 브뤼셀에서 개막하여 오픈소스 커뮤니티의 최신 동향을 공유하고 있습니다.

---

## 1. 보안 뉴스: Notepad++ 국가 지원 공급망 공격

### 1.1 사건 개요

| 항목 | 내용 |
|------|------|
| **대상** | Notepad++ - 전 세계에서 가장 많이 사용되는 오픈소스 텍스트 에디터 |
| **공격 유형** | 국가 지원(State-Sponsored) 공급망 침해 (Supply Chain Compromise) |
| **공격 벡터** | 배포 인프라 침해를 통한 악성 바이너리 배포 |
| **영향 범위** | 전 세계 개발자, 시스템 관리자, IT 전문가 (추정 수백만 사용자) |
| **심각도** | Critical - 국가 수준 위협 행위자 |
| **발표일** | 2026년 2월 1일 |
| **HN 반응** | 304 포인트 (커뮤니티 주요 관심사) |
| **출처** | [Notepad++ 공식 공지](https://notepad-plus-plus.org/news/hijacked-incident-info-update/) |

Notepad++는 단순한 텍스트 에디터를 넘어, **프로그래밍 언어 편집, 서버 설정 파일 수정, 로그 분석** 등 개발/운영 전반에서 사용되는 핵심 도구입니다. Windows 환경의 개발자와 시스템 관리자 중 상당수가 일상적으로 사용하고 있어, 이 도구가 침해되면 그 영향은 SolarWinds나 3CX 공급망 공격에 버금갈 수 있습니다.

### 1.2 공격 분석: MITRE ATT&CK 매핑

이번 공격은 MITRE ATT&CK 프레임워크의 **T1195 Supply Chain Compromise** 기법에 정확히 해당합니다. 하위 기법까지 분석하면 다음과 같습니다:

| MITRE ATT&CK ID | 기법명 | 적용 내용 |
|------------------|--------|-----------|
| **T1195** | Supply Chain Compromise | 전체 공격의 최상위 분류 |
| **T1195.002** | Compromise Software Supply Chain | 소프트웨어 배포 채널 침해 |
| **T1588.001** | Obtain Capabilities: Malware | 공격에 사용할 악성 페이로드 준비 |
| **T1036.005** | Masquerading: Match Legitimate Name | 정상 Notepad++ 바이너리로 위장 |
| **T1071.001** | Application Layer Protocol: Web | C2 통신에 HTTPS 사용 추정 |
| **T1059** | Command and Scripting Interpreter | 침해된 바이너리를 통한 코드 실행 |

**공격 체인 분석:**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" font-family="Segoe UI, Arial, sans-serif">
  <defs>
    <linearGradient id="phase1" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#dc2626"/><stop offset="100%" stop-color="#ef4444"/></linearGradient>
    <linearGradient id="phase2" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#ea580c"/><stop offset="100%" stop-color="#f97316"/></linearGradient>
    <linearGradient id="phase3" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#ca8a04"/><stop offset="100%" stop-color="#eab308"/></linearGradient>
    <linearGradient id="phase4" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>
    <filter id="shadow"><feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.15"/></filter>
  </defs>
  <rect width="900" height="520" rx="12" fill="#0f172a"/>
  <text x="450" y="36" text-anchor="middle" fill="#f8fafc" font-size="18" font-weight="700">Notepad++ Supply Chain Attack Chain Analysis</text>
  <!-- Phase 1 -->
  <rect x="30" y="55" width="200" height="36" rx="6" fill="url(#phase1)" filter="url(#shadow)"/>
  <text x="130" y="78" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 1: Initial Access</text>
  <rect x="240" y="55" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="78" r="5" fill="#f87171"/><text x="275" y="82" fill="#e2e8f0" font-size="12">Compromise distribution infrastructure server (state-level capability)</text>
  <circle cx="260" cy="103" r="5" fill="#f87171"/><text x="275" y="107" fill="#e2e8f0" font-size="12">Obtain code signing key or build pipeline access</text>
  <circle cx="260" cy="128" r="5" fill="#f87171"/><text x="275" y="132" fill="#e2e8f0" font-size="12">Inject malicious code into legitimate release process</text>
  <!-- Arrow -->
  <path d="M450 152 L450 168" stroke="#475569" stroke-width="2" marker-end="url(#arrowhead)"/>
  <defs><marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#475569"/></marker></defs>
  <!-- Phase 2 -->
  <rect x="30" y="170" width="200" height="36" rx="6" fill="url(#phase2)" filter="url(#shadow)"/>
  <text x="130" y="193" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 2: Execution</text>
  <rect x="240" y="170" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="193" r="5" fill="#fb923c"/><text x="275" y="197" fill="#e2e8f0" font-size="12">User downloads/updates Notepad++ from official channel</text>
  <circle cx="260" cy="218" r="5" fill="#fb923c"/><text x="275" y="222" fill="#e2e8f0" font-size="12">Execute legitimate-looking installer</text>
  <circle cx="260" cy="243" r="5" fill="#fb923c"/><text x="275" y="247" fill="#e2e8f0" font-size="12">Malicious payload activated in background</text>
  <!-- Arrow -->
  <path d="M450 267 L450 283" stroke="#475569" stroke-width="2" marker-end="url(#arrowhead)"/>
  <!-- Phase 3 -->
  <rect x="30" y="285" width="200" height="36" rx="6" fill="url(#phase3)" filter="url(#shadow)"/>
  <text x="130" y="308" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 3: Persistence &amp; C2</text>
  <rect x="240" y="285" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="308" r="5" fill="#facc15"/><text x="275" y="312" fill="#e2e8f0" font-size="12">Install persistent access mechanism on system</text>
  <circle cx="260" cy="333" r="5" fill="#facc15"/><text x="275" y="337" fill="#e2e8f0" font-size="12">Establish encrypted C2 channel</text>
  <circle cx="260" cy="358" r="5" fill="#facc15"/><text x="275" y="362" fill="#e2e8f0" font-size="12">Maintain capability for additional payload downloads</text>
  <!-- Arrow -->
  <path d="M450 382 L450 398" stroke="#475569" stroke-width="2" marker-end="url(#arrowhead)"/>
  <!-- Phase 4 -->
  <rect x="30" y="400" width="200" height="36" rx="6" fill="url(#phase4)" filter="url(#shadow)"/>
  <text x="130" y="423" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 4: Objectives</text>
  <rect x="240" y="400" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="423" r="5" fill="#a78bfa"/><text x="275" y="427" fill="#e2e8f0" font-size="12">Collect development environment information</text>
  <circle cx="260" cy="448" r="5" fill="#a78bfa"/><text x="275" y="452" fill="#e2e8f0" font-size="12">Exfiltrate source code / credentials</text>
  <circle cx="260" cy="473" r="5" fill="#a78bfa"/><text x="275" y="477" fill="#e2e8f0" font-size="12">Establish foothold for internal network lateral movement</text>
</svg>

### 1.3 왜 Notepad++가 표적이 되었나?

국가 지원 해킹 그룹이 Notepad++를 표적으로 선택한 전략적 이유가 있습니다:

| 공격 가치 요소 | 상세 설명 |
|---------------|-----------|
| **사용자 프로필** | 개발자, 시스템 관리자, DevOps 엔지니어 - 높은 권한을 가진 사용자층 |
| **사용 환경** | 서버 관리, 코드 편집, 설정 파일 수정 - 민감한 시스템에서 직접 사용 |
| **설치 규모** | 전 세계 수백만 다운로드, Windows 환경의 사실상 표준 에디터 |
| **신뢰도** | 20년 이상 유지된 오픈소스 프로젝트, 사용자들의 높은 신뢰 |
| **업데이트 빈도** | 활발한 개발/업데이트로 사용자들이 업데이트에 익숙 |
| **보안 인프라** | 대형 기업 소프트웨어 대비 상대적으로 작은 보안 인프라 |

이는 **"물 웅덩이 공격(Watering Hole)"**의 변형입니다. 고가치 표적(개발자/관리자)이 자주 찾는 소프트웨어를 침해하여, 광범위한 고권한 시스템에 접근하는 전략입니다.

### 1.4 과거 유사 공급망 공격 비교

| 사건 | 연도 | 규모 | 공격자 | 영향 |
|------|------|------|--------|------|
| **SolarWinds** | 2020 | 18,000+ 기관 | 러시아 SVR | 미국 정부 기관 다수 침해 |
| **3CX** | 2023 | 600,000+ 기업 | 북한 Lazarus | 암호화폐 탈취 목적 |
| **XZ Utils** | 2024 | 리눅스 전체 | 미상 (국가급) | SSH 백도어 (사전 차단) |
| **Notepad++** | 2026 | 수백만 사용자 | 국가 지원 그룹 | 개발자/관리자 환경 침해 |

### 1.5 탐지 및 대응: SIEM/EDR 쿼리

보안 관제 담당자는 다음 쿼리를 활용하여 Notepad++ 관련 침해 징후를 탐지할 수 있습니다:

```bash
# Splunk - Detect Notepad++ Anomalous Network Activity
index=endpoint sourcetype=sysmon EventCode=3
process_name="notepad++.exe"
NOT (dest_ip IN ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
| stats count by src_ip, dest_ip, dest_port, process_name
| where count > 5
| sort -count

# Splunk - Detect Notepad++ Anomalous Child Processes
index=endpoint sourcetype=sysmon EventCode=1
parent_process_name="notepad++.exe"
NOT (process_name IN ("notepad++.exe", "updater.exe"))
| stats count by process_name, parent_process_name, CommandLine
| sort -count

# Elastic/KQL - Detect Notepad++ Suspicious DLL Loading
process.name: "notepad++.exe" AND
event.category: "library" AND
NOT dll.path: ("C:\\Program Files\\Notepad++\\*" OR
               "C:\\Windows\\System32\\*" OR
               "C:\\Windows\\SysWOW64\\*")
```

```bash
# File Integrity Verification - Notepad++ Binary Hash Check
# Windows PowerShell
Get-FileHash "C:\Program Files\Notepad++\notepad++.exe" -Algorithm SHA256

# Compare with official hash (verify at Notepad++ official site)
# https://notepad-plus-plus.org/downloads/

# Verify downloaded file on Linux/Mac
sha256sum notepad++_installer.exe
# Verify official GPG signature
gpg --verify notepad++_installer.exe.sig notepad++_installer.exe
```

### 1.6 실무 대응 체크리스트

**즉시 조치 (P0):**

- [ ] 조직 내 Notepad++ 설치 현황 파악 (소프트웨어 자산 관리)
- [ ] 공식 공지에 따라 영향받는 버전 확인 및 해시 검증
- [ ] EDR/SIEM에 위 탐지 쿼리 적용
- [ ] Notepad++ 프로세스의 비정상 네트워크 연결 모니터링
- [ ] 의심스러운 설치분은 즉시 격리 및 포렌식 수행

**단기 조치 (P1):**

- [ ] 소프트웨어 화이트리스트 정책 검토 (AppLocker, WDAC)
- [ ] 코드 서명 검증 강제화 (서명되지 않은 바이너리 실행 차단)
- [ ] 배포 채널 SBOM(Software Bill of Materials) 검증 프로세스 도입
- [ ] 개발자 워크스테이션 보안 강화 (EDR 에이전트 설치 확인)

**장기 조치 (P2):**

- [ ] 소프트웨어 공급망 보안 정책 수립/갱신
- [ ] Zero Trust 모델에 소프트웨어 배포 채널 포함
- [ ] 개발 도구 보안 평가 주기적 수행 (연 2회 이상)
- [ ] 공급망 공격 시나리오 포함한 테이블탑 훈련(TTX) 실시

---

## 2. AI & 클라우드: 에이전트 시대의 도래

### 2.1 Amazon Bedrock AgentCore 멀티에이전트 운영

| 항목 | 내용 |
|------|------|
| **서비스** | Amazon Bedrock AgentCore |
| **시나리오** | 항공사 고객 서비스 멀티에이전트 운영 |
| **핵심** | 멀티에이전트 오케스트레이션 + 접근 제어 패턴 |
| **출처** | [AWS Korea Blog](https://aws.amazon.com/ko/blogs/tech/multi-agent-operations-for-airline-agentcore-service/) |

AWS Korea Blog에서 발표한 이 아키텍처는 **항공사 고객 서비스**를 예시로 하여, 여러 AI 에이전트가 협력하면서도 적절한 접근 제어를 유지하는 방법을 보여줍니다.

**멀티에이전트 아키텍처 핵심 구성:**

| 구성 요소 | 역할 | 접근 권한 |
|-----------|------|-----------|
| **Orchestrator Agent** | 사용자 요청 분석 및 적절한 에이전트로 라우팅 | 전체 에이전트 디스패치 |
| **Booking Agent** | 항공권 예약, 변경, 취소 처리 | 예약 시스템 읽기/쓰기 |
| **Status Agent** | 항공편 상태, 지연 정보 조회 | 운항 정보 읽기 전용 |
| **Loyalty Agent** | 마일리지 조회, 보상 처리 | 고객 포인트 시스템 |
| **Complaint Agent** | 불만 접수 및 보상 결정 | 고객 이력 + 보상 정책 |

**접근 제어 패턴 (Guardrails):**

Amazon Bedrock AgentCore의 접근 제어는 **최소 권한 원칙(Principle of Least Privilege)**을 에이전트 수준에서 구현합니다:

- **Agent-level IAM**: 각 에이전트별 독립적 IAM 역할 할당
- **Action Groups**: 에이전트가 호출 가능한 API를 명시적으로 제한
- **Knowledge Base Scoping**: 에이전트별 접근 가능한 지식 베이스 범위 제한
- **Session Isolation**: 에이전트 간 세션 데이터 격리
- **Human-in-the-Loop**: 고위험 작업(환불, 보상)에 대한 인간 승인 게이트

이 패턴은 지난주 발표된 **OWASP Agentic AI Top 10**의 "Excessive Agency" 위협에 대한 실전적 대응 방법이기도 합니다.

### 2.2 Google Research: AI Agent 스케일링의 과학

| 항목 | 내용 |
|------|------|
| **발표** | Google Research Blog |
| **주제** | Towards a Science of Scaling Agent Systems |
| **핵심 질문** | 언제, 왜 에이전트 시스템이 작동하는가? |
| **출처** | [Google Research Blog](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) |

Google Research가 발표한 이 연구는 AI 에이전트 시스템의 **스케일링 법칙(Scaling Laws)**을 규명하려는 시도입니다. LLM의 스케일링 법칙(파라미터, 데이터, 컴퓨팅이 많을수록 성능 향상)이 명확히 밝혀진 것과 달리, 에이전트 시스템에서는 "에이전트를 더 추가한다고 반드시 성능이 좋아지지 않는다"는 반직관적 결과가 있습니다.

**핵심 발견:**

| 발견 | 상세 | 실무 시사점 |
|------|------|------------|
| **스케일링 한계점 존재** | 에이전트 수가 일정 수준을 넘으면 성능 포화 또는 하락 | 무조건 에이전트 추가는 비효율 |
| **작업 분해 품질이 핵심** | 잘 분해된 작업에서만 멀티에이전트가 효과적 | 오케스트레이션 설계가 LLM 성능보다 중요 |
| **통신 오버헤드** | 에이전트 간 통신 비용이 기하급수적 증가 가능 | 에이전트 간 인터페이스 최소화 필요 |
| **검증 메커니즘 필수** | 자율 에이전트의 출력 품질 보장에 검증 루프 필수 | Critic/Verifier 에이전트 패턴 권장 |
| **전문화 > 범용** | 전문화된 소수 에이전트가 범용 다수보다 효과적 | 에이전트 역할을 명확히 정의 |

**실무 설계 원칙 (연구에서 도출):**

1. **"더 많이" 보다 "더 잘"**: 에이전트 수를 늘리기보다 개별 에이전트의 역할 정의와 도구 접근을 정교하게 설계
2. **계층적 오케스트레이션**: 플랫 구조보다 계층적(hierarchical) 에이전트 구조가 스케일링에 유리
3. **명시적 검증 루프**: 매 스텝마다 출력을 검증하는 에이전트를 포함 (self-correction)
4. **통신 프로토콜 표준화**: 에이전트 간 메시지 형식을 구조화하여 오해 최소화
5. **실패 격리**: 한 에이전트의 실패가 전체 시스템으로 전파되지 않도록 설계

이 연구 결과는 Amazon Bedrock AgentCore의 아키텍처 설계 원칙과도 일맥상통하며, 에이전트 시스템을 프로덕션에 배포하려는 팀에게 과학적 근거를 제공합니다.

---

## 3. 블록체인: Bitcoin $80K 대폭락과 시장 충격

### 3.1 주말 대폭락 타임라인

2026년 2월 1-2일 주말 동안, 암호화폐 시장에 대규모 폭락이 발생했습니다.

| 시간 (UTC) | 이벤트 | 영향 |
|------------|--------|------|
| **2/1 02:00** | Bitcoin $86K에서 급락 시작 | 레버리지 포지션 경고 발생 |
| **2/1 06:00** | $82K 지지선 붕괴 | 1차 대규모 청산 ($3.2B) |
| **2/1 10:00** | Ether 10%+ 급락 | 단일 트레이더 $220M 손실 확인 |
| **2/1 14:00** | DeFi 프로토콜 연쇄 청산 시작 | TVL 급감, DEX 거래량 폭증 |
| **2/1 18:00** | $80K 심리적 지지선 하회 | 패닉 매도 가속 |
| **2/2 00:00** | $78K 저점 형성 | 총 청산 규모 $19B 추정 |
| **2/2 06:00** | $79K 부근 횡보 | 약 반등 시도, 거래량 감소 |

**출처:** [CoinDesk - Bitcoin Holds Below $80K](https://www.coindesk.com/markets/2026/02/02/bitcoin-holds-below-usd80-000-as-january-prediction-contracts-miss-liquidation-driven-slide-asia-morning-briefing), [CoinDesk - Bitcoin Weekend Crash](https://www.coindesk.com/markets/2026/02/01/this-is-absolutely-insane-bitcoin-s-weekend-crash-exposes-the-cracks-beneath-crypto-s-latest-boom)

### 3.2 DeFi 청산 연쇄 분석

이번 폭락에서 특히 주목할 점은 **DeFi 프로토콜의 연쇄 청산(Cascading Liquidations)**입니다.

| 지표 | 수치 | 의미 |
|------|------|------|
| **총 청산 규모** | ~$19B | 2024년 이후 최대 규모 |
| **최대 단일 손실** | $220M (1인 트레이더) | Ether 레버리지 롱 포지션 |
| **주요 청산 프로토콜** | Aave, Compound, MakerDAO | 대형 DeFi 렌딩 프로토콜 전반 |
| **BTC 하락폭** | ~$86K -> ~$78K (-9.3%) | 주말 2일 동안 |
| **ETH 하락폭** | ~10%+ | BTC보다 더 큰 하락률 |

**청산 연쇄 메커니즘:**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 520" font-family="Segoe UI, Arial, sans-serif">
  <defs>
    <linearGradient id="liq-red" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#b91c1c"/><stop offset="100%" stop-color="#dc2626"/></linearGradient>
    <linearGradient id="liq-org" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#c2410c"/><stop offset="100%" stop-color="#ea580c"/></linearGradient>
    <linearGradient id="liq-yel" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#a16207"/><stop offset="100%" stop-color="#ca8a04"/></linearGradient>
    <linearGradient id="liq-pur" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#6d28d9"/><stop offset="100%" stop-color="#7c3aed"/></linearGradient>
    <marker id="arr2" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#64748b"/></marker>
    <filter id="sh2"><feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.18"/></filter>
  </defs>
  <rect width="740" height="520" rx="12" fill="#0f172a"/>
  <text x="370" y="32" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">DeFi Cascading Liquidation Mechanism</text>
  <!-- Step boxes -->
  <g filter="url(#sh2)">
    <rect x="195" y="46" width="350" height="36" rx="18" fill="url(#liq-red)"/><text x="370" y="69" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">1. Bitcoin Price Crash Begins</text>
    <path d="M370 82 L370 96" stroke="#64748b" stroke-width="2" marker-end="url(#arr2)"/>
    <rect x="195" y="100" width="350" height="36" rx="18" fill="url(#liq-red)"/><text x="370" y="123" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">2. Leveraged Long Positions Margin Called</text>
    <path d="M370 136 L370 150" stroke="#64748b" stroke-width="2" marker-end="url(#arr2)"/>
    <rect x="195" y="154" width="350" height="36" rx="18" fill="url(#liq-org)"/><text x="370" y="177" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">3. Forced Liquidation → Market Sell Flood</text>
    <path d="M370 190 L370 204" stroke="#64748b" stroke-width="2" marker-end="url(#arr2)"/>
    <rect x="195" y="208" width="350" height="36" rx="18" fill="url(#liq-org)"/><text x="370" y="231" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">4. Further Price Drop → More Liquidations</text>
    <path d="M370 244 L370 258" stroke="#64748b" stroke-width="2" marker-end="url(#arr2)"/>
    <rect x="165" y="262" width="410" height="36" rx="18" fill="url(#liq-yel)"/><text x="370" y="285" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">5. DeFi Collateral Ratio Falls Below Threshold</text>
    <path d="M370 298 L370 312" stroke="#64748b" stroke-width="2" marker-end="url(#arr2)"/>
    <rect x="165" y="316" width="410" height="36" rx="18" fill="url(#liq-yel)"/><text x="370" y="339" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">6. Aave/Compound Auto-Liquidation Triggered</text>
    <path d="M370 352 L370 366" stroke="#64748b" stroke-width="2" marker-end="url(#arr2)"/>
    <rect x="165" y="370" width="410" height="36" rx="18" fill="url(#liq-pur)"/><text x="370" y="393" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">7. Liquidation Assets Dumped on DEX → Downward Pressure</text>
    <path d="M370 406 L370 420" stroke="#64748b" stroke-width="2" marker-end="url(#arr2)"/>
    <rect x="195" y="424" width="350" height="36" rx="18" fill="url(#liq-pur)"/><text x="370" y="447" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">8. Stablecoin De-peg Fear → Panic Selloff</text>
  </g>
  <!-- Feedback loop arrow -->
  <path d="M545 447 C680 447, 700 280, 545 69" stroke="#f87171" stroke-width="2" fill="none" stroke-dasharray="6,4" marker-end="url(#arr2)"/>
  <text x="670" y="268" fill="#f87171" font-size="11" font-weight="600" transform="rotate(-90,670,268)">Feedback Loop</text>
</svg>

**출처:** [CoinDesk - Single Trader Lost $220M](https://www.coindesk.com/markets/2026/02/01/single-trader-just-lost-usd220-million-as-ether-plunged-10)

### 3.3 Ethereum 양자 위협 대응: LeanVM과 PQ Signatures

흥미롭게도 가격 폭락과 동시에, Ethereum Foundation은 양자 컴퓨팅 보안 위협에 대한 대응을 발표했습니다.

| 항목 | 내용 |
|------|------|
| **이니셔티브** | Ethereum Quantum Security Roadmap |
| **핵심 기술** | LeanVM + Post-Quantum (PQ) Signatures |
| **목표** | 양자 컴퓨터에 의한 기존 타원 곡선 암호 해독 대비 |
| **출처** | [CoinDesk - Quantum Threat Gets Real](https://www.coindesk.com/tech/2026/02/01/quantum-threat-gets-real-ethereum-foundation-prioritizes-security-with-leanvm-and-pq-signatures) |

**왜 중요한가?**

현재 Ethereum(및 Bitcoin)의 서명 알고리즘(ECDSA)은 양자 컴퓨터가 Shor 알고리즘을 실행할 수 있는 수준에 도달하면 이론적으로 해독 가능합니다. Ethereum Foundation의 대응은:

- **LeanVM**: 양자 안전 서명을 효율적으로 검증할 수 있는 경량 가상 머신
- **PQ Signatures**: NIST가 표준화한 Post-Quantum 서명 알고리즘(CRYSTALS-Dilithium 등) 도입
- **하위 호환성**: 기존 EOA(Externally Owned Account)와의 호환성 유지 전략

이번 가격 폭락과는 별개로, 양자 보안 대비는 블록체인의 장기적 생존과 직결되는 핵심 과제입니다.

---

## 4. DevOps: HashiCorp 보안 자동화

### 4.1 Boundary 0.21: 패스워드리스 RDP 접근

| 항목 | 내용 |
|------|------|
| **제품** | HashiCorp Boundary 0.21 |
| **핵심 기능** | Passwordless RDP Access |
| **대상** | Windows 원격 데스크톱 접근 관리 |
| **출처** | [HashiCorp Blog](https://www.hashicorp.com/blog/boundary-0-21-improves-remote-access-security-and-ux-for-rdp-connections) |

HashiCorp Boundary 0.21은 **RDP(Remote Desktop Protocol) 연결의 패스워드리스 접근**을 지원합니다. 이는 Windows 서버 관리에서 가장 큰 보안 위험 중 하나인 RDP 자격 증명 관리 문제를 해결합니다.

**기존 RDP의 보안 문제:**

| 문제 | 위험 | Boundary 0.21 해결 방식 |
|------|------|------------------------|
| 공유 비밀번호 | 자격 증명 유출 시 대규모 침해 | 패스워드리스 인증 (인증서 기반) |
| 비밀번호 재사용 | 한 서버 침해가 전체로 확산 | 세션별 임시 자격 증명 |
| 비밀번호 만료 관리 | 운영 부담, 만료 시 장애 | 자동 자격 증명 순환 |
| RDP 무차별 대입 | 인터넷 노출 시 상시 공격 | Boundary 프록시를 통한 간접 접근 |
| 세션 추적 불가 | 누가 언제 접근했는지 파악 어려움 | 전체 세션 감사 로그 |

**아키텍처 흐름:**

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 340" font-family="Segoe UI, Arial, sans-serif">
  <defs>
    <linearGradient id="b-blue" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#1d4ed8"/><stop offset="100%" stop-color="#3b82f6"/></linearGradient>
    <linearGradient id="b-green" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#059669"/><stop offset="100%" stop-color="#10b981"/></linearGradient>
    <linearGradient id="b-purple" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#7c3aed"/><stop offset="100%" stop-color="#8b5cf6"/></linearGradient>
    <linearGradient id="b-gray" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#475569"/><stop offset="100%" stop-color="#64748b"/></linearGradient>
    <marker id="arr3" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="#94a3b8"/></marker>
    <filter id="sh3"><feDropShadow dx="1" dy="2" stdDeviation="3" flood-opacity="0.2"/></filter>
  </defs>
  <rect width="820" height="340" rx="12" fill="#0f172a"/>
  <text x="410" y="30" text-anchor="middle" fill="#f8fafc" font-size="17" font-weight="700">HashiCorp Boundary 0.21 Passwordless RDP Architecture</text>
  <!-- User -->
  <rect x="30" y="65" width="120" height="55" rx="10" fill="url(#b-gray)" filter="url(#sh3)"/>
  <text x="90" y="90" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">User</text>
  <text x="90" y="106" text-anchor="middle" fill="#cbd5e1" font-size="10">SSO / MFA</text>
  <!-- Arrow 1 -->
  <line x1="150" y1="92" x2="195" y2="92" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <text x="172" y="85" text-anchor="middle" fill="#94a3b8" font-size="9">1</text>
  <!-- Boundary Client -->
  <rect x="200" y="65" width="140" height="55" rx="10" fill="url(#b-blue)" filter="url(#sh3)"/>
  <text x="270" y="90" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Boundary Client</text>
  <text x="270" y="106" text-anchor="middle" fill="#bfdbfe" font-size="10">Desktop App</text>
  <!-- Arrow 2 -->
  <line x1="340" y1="92" x2="395" y2="92" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <text x="367" y="85" text-anchor="middle" fill="#94a3b8" font-size="9">2</text>
  <!-- Boundary Controller -->
  <rect x="400" y="55" width="170" height="75" rx="10" fill="url(#b-purple)" filter="url(#sh3)"/>
  <text x="485" y="82" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Boundary Controller</text>
  <text x="485" y="100" text-anchor="middle" fill="#ddd6fe" font-size="10">AuthN / AuthZ</text>
  <text x="485" y="116" text-anchor="middle" fill="#ddd6fe" font-size="10">Ephemeral Cert Issue</text>
  <!-- Arrow 3 down -->
  <line x1="485" y1="130" x2="485" y2="175" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <text x="495" y="155" fill="#94a3b8" font-size="9">3</text>
  <!-- Boundary Worker -->
  <rect x="400" y="180" width="170" height="65" rx="10" fill="url(#b-green)" filter="url(#sh3)"/>
  <text x="485" y="207" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Boundary Worker</text>
  <text x="485" y="225" text-anchor="middle" fill="#a7f3d0" font-size="10">Cert-based RDP Proxy</text>
  <!-- Arrow 4 -->
  <line x1="570" y1="212" x2="625" y2="212" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <text x="597" y="205" text-anchor="middle" fill="#94a3b8" font-size="9">4</text>
  <!-- RDP Target -->
  <rect x="630" y="180" width="155" height="65" rx="10" fill="url(#b-gray)" filter="url(#sh3)"/>
  <text x="707" y="207" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">RDP Target Server</text>
  <text x="707" y="225" text-anchor="middle" fill="#cbd5e1" font-size="10">Windows Server</text>
  <!-- Steps -->
  <rect x="30" y="270" width="760" height="55" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="50" y="290" fill="#94a3b8" font-size="11" font-weight="600">Flow:</text>
  <text x="50" y="310" fill="#e2e8f0" font-size="11">1. User authenticates via SSO/MFA → 2. Ephemeral certificate issued per session → 3. Worker establishes RDP via cert → 4. Passwordless RDP session → 5. Cert auto-revoked on disconnect</text>
</svg>

### 4.2 VSO: etcd 없이 Kubernetes 시크릿 관리

| 항목 | 내용 |
|------|------|
| **제품** | Vault Secrets Operator (VSO) |
| **핵심** | Kubernetes Pod에 시크릿 전달 시 etcd 저장 없이 직접 주입 |
| **출처** | [HashiCorp Blog](https://www.hashicorp.com/blog/deliver-secrets-to-kubernetes-pods-without-storing-in-etcd-using-vso) |

Kubernetes의 기본 Secret 리소스는 **etcd에 base64 인코딩(암호화 아님!)으로 저장**됩니다. 이는 etcd 접근 권한이 있는 공격자가 모든 시크릿을 평문으로 읽을 수 있다는 심각한 보안 취약점입니다.

**기존 방식 vs VSO 방식 비교:**

| 비교 항목 | 기존 K8s Secret | VSO (etcd-free) |
|-----------|-----------------|-----------------|
| **저장 위치** | etcd (base64 인코딩) | Vault에만 저장, etcd 미저장 |
| **암호화** | etcd encryption-at-rest 별도 설정 필요 | Vault 자체 암호화 |
| **접근 제어** | K8s RBAC만 | Vault Policy + K8s RBAC 이중 제어 |
| **시크릿 순환** | 수동 업데이트 필요 | VSO가 자동 동기화 |
| **감사** | K8s audit log | Vault audit log (상세) |
| **유출 시 영향** | etcd 백업에서 평문 노출 | etcd에 시크릿 없음 |

이 접근 방식은 **CIS Kubernetes Benchmark**의 시크릿 관리 권장 사항을 충족하며, SOC 2 / ISO 27001 감사에서도 강점이 됩니다.

---

## 5. 기술 동향: FOSDEM 2026 & AI 개발 패러다임

### 5.1 FOSDEM 2026 Day 1 하이라이트

| 항목 | 내용 |
|------|------|
| **행사** | FOSDEM 2026 (Free and Open Source Developers' European Meeting) |
| **장소** | 벨기에 브뤼셀, ULB 캠퍼스 |
| **일정** | 2026년 2월 1-2일 |
| **출처** | [FOSDEM 2026 Blog](https://gyptazy.com/blog/fosdem-2026-opensource-conference-brussels/) |

FOSDEM은 매년 브뤼셀에서 열리는 **유럽 최대 오픈소스 개발자 컨퍼런스**로, 올해 26번째를 맞이했습니다. 10,000명 이상의 개발자가 참가하는 이 행사에서 주목할 트렌드:

| 트랙/주제 | 핵심 내용 | 시사점 |
|-----------|-----------|--------|
| **AI/ML DevRoom** | LLM 로컬 실행, 오픈소스 AI 도구 | AI 민주화 가속 |
| **Security DevRoom** | 공급망 보안(SBOM), Sigstore | Notepad++ 사건과 직결 |
| **Containers & Cloud** | eBPF, Wasm, 서버리스 | 클라우드 네이티브 진화 |
| **Legal DevRoom** | EU Cyber Resilience Act | 오픈소스 규제 영향 |

### 5.2 "코드는 싸다" - AI 시대의 개발자 역량 변화

GeekNews(Hada.io)에서 화제가 된 여러 기사들이 **AI 시대 개발 패러다임의 근본적 변화**를 조명하고 있습니다.

| 기사 제목 | 핵심 메시지 | 출처 |
|-----------|------------|------|
| **"코드는 싸다. 이제는 '말'을 보여줘라"** | AI가 코드를 생성하는 시대에 개발자의 가치는 명확한 요구사항 정의와 커뮤니케이션 능력에 있다 | [GeekNews](https://news.hada.io/topic?id=26333) |
| **"Claude Code 창시자가 공개한 실전 사용 팁"** | AI 코딩 도구의 효과적 활용법, 프롬프트 엔지니어링 실전 패턴 | [GeekNews](https://news.hada.io/topic?id=26330) |
| **"AI 창의성의 역설"** | AI가 창의적 작업을 수행할수록, 인간의 고유 창의성이 더 가치있어지는 역설 | [GeekNews](https://news.hada.io/topic?id=26332) |
| **"2026 기술 트렌드 보고서"** | AI Agent, 양자 컴퓨팅, 공급망 보안이 2026년 3대 기술 트렌드 | [GeekNews](https://news.hada.io/topic?id=26329) |

**"코드는 싸다"가 의미하는 변화:**

이 담론의 핵심은 AI 코드 생성 도구(Claude Code, GitHub Copilot, Cursor 등)의 발전으로 **코드 작성 자체의 비용이 급격히 낮아졌다**는 것입니다. 이에 따라 개발자에게 요구되는 역량의 무게 중심이 이동하고 있습니다:

| 역량 영역 | 과거 가치 | 현재/미래 가치 | 변화 방향 |
|-----------|----------|---------------|-----------|
| **코드 작성 속도** | 높음 | 낮음 | AI가 대체 |
| **아키텍처 설계** | 높음 | 매우 높음 | AI가 보조하나 인간 판단 필수 |
| **요구사항 정의** | 중간 | 매우 높음 | AI에게 "무엇을"을 명확히 전달하는 능력 |
| **코드 리뷰/검증** | 중간 | 높음 | AI 생성 코드의 품질 보증 |
| **도메인 지식** | 높음 | 매우 높음 | AI가 대체하기 어려운 영역 |
| **커뮤니케이션** | 중간 | 높음 | 기술적 의사결정의 근거 설명 능력 |

---

## 트렌드 분석

이번 주 뉴스에서 도출되는 주요 트렌드를 종합 분석합니다:

| 트렌드 | 관련 뉴스 | 영향도 | 대응 시급성 |
|--------|-----------|--------|------------|
| **공급망 공격 고도화** | Notepad++ 국가 지원 공급망 침해 | Critical | 즉시 |
| **DeFi 시스템 리스크** | Bitcoin 폭락 → 연쇄 청산 $19B | High | 단기 |
| **AI Agent 성숙** | Google 스케일링 연구 + Amazon AgentCore | High | 중기 |
| **양자 보안 대비** | Ethereum PQ Signatures | Medium | 장기 |
| **패스워드리스 확산** | HashiCorp Boundary 0.21 RDP | Medium | 중기 |
| **개발자 역할 재정의** | "코드는 싸다" + Claude Code 실전 팁 | Medium | 진행 중 |
| **오픈소스 보안 규제** | FOSDEM 2026 + EU CRA | Medium | 장기 |

**가장 주목할 교차점:** Notepad++ 공급망 공격과 FOSDEM의 공급망 보안 세션, Google의 에이전트 스케일링 연구와 Amazon의 AgentCore 실전 패턴이 같은 주에 발표된 것은, 이 분야들이 이론에서 실전으로 빠르게 이동하고 있음을 보여줍니다.

---

## 실무 체크리스트

이번 주 뉴스 기반으로 보안/DevOps 팀이 즉시 확인해야 할 항목들입니다:

### 보안팀 (P0 - 즉시)

- [ ] Notepad++ 설치 현황 파악 및 해시 검증 ([공식 공지](https://notepad-plus-plus.org/news/hijacked-incident-info-update/) 확인)
- [ ] EDR/SIEM에 Notepad++ 비정상 행위 탐지 쿼리 적용
- [ ] 소프트웨어 배포 채널 보안 현황 점검 (코드 서명, 이중 검증)
- [ ] 암호화폐 관련 서비스 운영 시 - DeFi 청산 이벤트 모니터링 강화

### DevOps팀 (P1 - 이번 주)

- [ ] Kubernetes 시크릿 관리 방식 점검 (etcd 암호화 또는 VSO 도입 검토)
- [ ] RDP 접근 관리 현황 점검 (Boundary 0.21 패스워드리스 평가)
- [ ] 개발 도구 SBOM(Software Bill of Materials) 생성/관리 시작

### AI/ML팀 (P1 - 이번 달)

- [ ] AI 에이전트 접근 제어 현황 점검 (Amazon AgentCore 패턴 참조)
- [ ] 멀티에이전트 아키텍처 설계 시 Google 스케일링 연구 반영
- [ ] 에이전트별 IAM 역할 분리 및 최소 권한 원칙 적용

### 전략/기획 (P2 - Q1 2026)

- [ ] 공급망 보안 정책 수립/갱신 (국가 수준 위협 대비)
- [ ] AI 시대 개발 역량 로드맵 수립 (아키텍처/커뮤니케이션 강화)
- [ ] Post-Quantum 암호화 전환 로드맵 검토 시작

---

## 참고 자료

### 보안 & 공급망

| 제목 | URL |
|------|-----|
| Notepad++ Hijacked Incident Info Update | [Notepad++ 공식](https://notepad-plus-plus.org/news/hijacked-incident-info-update/) |
| MITRE ATT&CK T1195 - Supply Chain Compromise | [MITRE ATT&CK](https://attack.mitre.org/techniques/T1195/) |

### AI & 에이전트

| 제목 | URL |
|------|-----|
| Amazon Bedrock AgentCore 멀티에이전트 운영 | [AWS Korea Blog](https://aws.amazon.com/ko/blogs/tech/multi-agent-operations-for-airline-agentcore-service/) |
| Google Research - Scaling Agent Systems | [Google Research](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) |

### 블록체인 & 암호화폐

| 제목 | URL |
|------|-----|
| Bitcoin Holds Below $80K | [CoinDesk](https://www.coindesk.com/markets/2026/02/02/bitcoin-holds-below-usd80-000-as-january-prediction-contracts-miss-liquidation-driven-slide-asia-morning-briefing) |
| Bitcoin Weekend Crash Analysis | [CoinDesk](https://www.coindesk.com/markets/2026/02/01/this-is-absolutely-insane-bitcoin-s-weekend-crash-exposes-the-cracks-beneath-crypto-s-latest-boom) |
| Single Trader Lost $220M | [CoinDesk](https://www.coindesk.com/markets/2026/02/01/single-trader-just-lost-usd220-million-as-ether-plunged-10) |
| Ethereum Quantum Threat - PQ Signatures | [CoinDesk](https://www.coindesk.com/tech/2026/02/01/quantum-threat-gets-real-ethereum-foundation-prioritizes-security-with-leanvm-and-pq-signatures) |

### DevOps & 인프라

| 제목 | URL |
|------|-----|
| HashiCorp Boundary 0.21 - Passwordless RDP | [HashiCorp Blog](https://www.hashicorp.com/blog/boundary-0-21-improves-remote-access-security-and-ux-for-rdp-connections) |
| VSO - Kubernetes Secrets without etcd | [HashiCorp Blog](https://www.hashicorp.com/blog/deliver-secrets-to-kubernetes-pods-without-storing-in-etcd-using-vso) |

### 기술 동향 & AI 개발

| 제목 | URL |
|------|-----|
| FOSDEM 2026 Day 1 | [gyptazy Blog](https://gyptazy.com/blog/fosdem-2026-opensource-conference-brussels/) |
| 코드는 싸다 - AI 시대의 개발 | [GeekNews](https://news.hada.io/topic?id=26333) |
| Claude Code 창시자 실전 팁 | [GeekNews](https://news.hada.io/topic?id=26330) |
| AI 창의성의 역설 | [GeekNews](https://news.hada.io/topic?id=26332) |
| 2026 기술 트렌드 보고서 | [GeekNews](https://news.hada.io/topic?id=26329) |

---

*이 글은 [Twodragon's Tech Blog](https://tech.2twodragon.com)에서 매주 발행하는 Tech & Security Weekly Digest입니다. 최신 보안 뉴스와 실무 가이드를 매주 받아보세요.*
