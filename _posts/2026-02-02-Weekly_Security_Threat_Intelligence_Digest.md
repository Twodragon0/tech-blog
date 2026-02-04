---
layout: post
title: "Weekly Security Threat Intelligence Digest: Notepad++ 공급망 공격, SK쉴더스 보안 리포트 종합, HashiCorp 보안 자동화"
date: 2026-02-02 10:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, Supply-Chain, Notepad++, Ransomware, Zero-Trust, JWT, Vertical-AI, SK-Shieldus, HashiCorp, Red-Team, "2026"]
excerpt: "Notepad++ 국가 지원 공급망 공격, SK쉴더스 11-1월 보안 리포트 종합 (Vertical AI, BlackField/Sinobi/Gentlemen 랜섬웨어, 제로트러스트, JWT 보안), HashiCorp 패스워드리스 RDP"
description: "2026년 2월 2일 보안 위협 인텔리전스: Notepad++ 공급망 공격(T1195), SK쉴더스 EQST 보안 리포트 11-1월호 종합 분석, 랜섬웨어 생태계 변화, 제로트러스트 데이터 보안, JWT 인증 위협, HashiCorp Boundary 0.21"
keywords: [Notepad++ Supply Chain Attack, SK Shieldus EQST, BlackField Ransomware, Sinobi Ransomware, Zero Trust Data Security, JWT Security, Vertical AI SOC, HashiCorp Boundary, Red Team Cyber Immunity]
author: Twodragon
comments: true
image: /assets/images/2026-02-02-Weekly_Security_Threat_Intelligence_Digest.svg
image_alt: "Weekly Security Threat Intelligence Digest Feb 2 2026"
toc: true
schema_type: Article
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Weekly Security Threat Intelligence Digest (2026년 02월 02일)</span>
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
      <span class="tag">Ransomware</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">JWT</span>
      <span class="tag">Vertical-AI</span>
      <span class="tag">SK-Shieldus</span>
      <span class="tag">HashiCorp</span>
      <span class="tag">Red-Team</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>Notepad++ 국가 지원 공급망 공격</strong>: 배포 인프라 침해를 통한 수백만 개발자 대상 공급망 공격 (HN 304pts)</li>
      <li><strong>SK쉴더스 보안 리포트 종합</strong>: Vertical AI SOC 자동화, BlackField/Sinobi/Gentlemen 랜섬웨어, 제로트러스트 데이터 보안, JWT 인증 위협, 레드팀 사이버 면역 체계</li>
      <li><strong>HashiCorp 보안 자동화</strong>: Boundary 0.21 패스워드리스 RDP, VSO etcd-free Kubernetes 시크릿 관리</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, SOC 분석가, CISO</span>
  </div>
</div>
</div>

> **함께 읽기**: 같은 날짜의 기술/AI/블록체인 다이제스트 [Weekly Tech & AI & Blockchain Digest](/2026-02-02-Weekly_Tech_AI_Blockchain_Digest)에서 Apple MLX 버그, Bitcoin $74K 대폭락, AI 창의성 역설, DeFi 보안, FOSDEM 2026을 심층 분석합니다.

## 개요

2026년 2월 첫째 주, 보안 분야에서 국가 수준의 공급망 공격부터 랜섬웨어 생태계의 구조적 변화까지 중대한 이벤트가 잇따랐습니다.

**국가 지원 해킹 그룹이 Notepad++의 배포 인프라를 침해**하여 전 세계 수백만 개발자를 대상으로 공급망 공격을 감행한 사실이 확인되었습니다 (HN 304 포인트). 일상적으로 사용하는 텍스트 에디터가 국가 수준의 위협으로부터 안전하지 않다는 현실을 보여주는 사건입니다.

SK쉴더스 EQST는 **11월~1월호 보안 리포트 10건**을 발행하며, Vertical AI 기반 SOC 자동화, BlackField/Sinobi/Gentlemen 랜섬웨어 위협, 데이터 중심 제로트러스트, JWT 서명키 유출 위협, 레드팀 기반 사이버 면역 체계 구축 전략을 심층 분석했습니다.

인프라 보안에서는 HashiCorp이 **Boundary 0.21 패스워드리스 RDP**와 **VSO etcd-free 시크릿 관리**를 발표하여, Zero Trust 접근 제어와 Kubernetes 시크릿 보안의 새로운 기준을 제시했습니다.

---

## 1. Notepad++ 국가 지원 공급망 공격

### 1.1 사건 개요

| 항목 | 내용 |
|------|------|
| **대상** | Notepad++ - 전 세계에서 가장 많이 사용되는 오픈소스 텍스트 에디터 |
| **공격 유형** | 국가 지원(State-Sponsored) 공급망 침해 (Supply Chain Compromise) |
| **공격 벡터** | 배포 인프라 침해를 통한 악성 바이너리 배포 |
| **영향 범위** | 전 세계 개발자, 시스템 관리자, IT 전문가 (추정 수백만 사용자) |
| **심각도** | Critical - 국가 수준 위협 행위자 |
| **HN 반응** | 304 포인트 (커뮤니티 주요 관심사) |
| **출처** | [Notepad++ 공식 공지](https://notepad-plus-plus.org/news/hijacked-incident-info-update/) |

### 1.2 MITRE ATT&CK 매핑

| MITRE ATT&CK ID | 기법명 | 적용 내용 |
|------------------|--------|-----------|
| **T1195** | Supply Chain Compromise | 전체 공격의 최상위 분류 |
| **T1195.002** | Compromise Software Supply Chain | 소프트웨어 배포 채널 침해 |
| **T1588.001** | Obtain Capabilities: Malware | 공격에 사용할 악성 페이로드 준비 |
| **T1036.005** | Masquerading: Match Legitimate Name | 정상 Notepad++ 바이너리로 위장 |
| **T1071.001** | Application Layer Protocol: Web | C2 통신에 HTTPS 사용 추정 |
| **T1059** | Command and Scripting Interpreter | 침해된 바이너리를 통한 코드 실행 |

### 1.3 공격 체인 분석

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
  <rect x="30" y="55" width="200" height="36" rx="6" fill="url(#phase1)" filter="url(#shadow)"/>
  <text x="130" y="78" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 1: Initial Access</text>
  <rect x="240" y="55" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="78" r="5" fill="#f87171"/><text x="275" y="82" fill="#e2e8f0" font-size="12">Compromise distribution infrastructure server (state-level capability)</text>
  <circle cx="260" cy="103" r="5" fill="#f87171"/><text x="275" y="107" fill="#e2e8f0" font-size="12">Obtain code signing key or build pipeline access</text>
  <circle cx="260" cy="128" r="5" fill="#f87171"/><text x="275" y="132" fill="#e2e8f0" font-size="12">Inject malicious code into legitimate release process</text>
  <path d="M450 152 L450 168" stroke="#475569" stroke-width="2" marker-end="url(#arrowhead)"/>
  <defs><marker id="arrowhead" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#475569"/></marker></defs>
  <rect x="30" y="170" width="200" height="36" rx="6" fill="url(#phase2)" filter="url(#shadow)"/>
  <text x="130" y="193" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 2: Execution</text>
  <rect x="240" y="170" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="193" r="5" fill="#fb923c"/><text x="275" y="197" fill="#e2e8f0" font-size="12">User downloads/updates Notepad++ from official channel</text>
  <circle cx="260" cy="218" r="5" fill="#fb923c"/><text x="275" y="222" fill="#e2e8f0" font-size="12">Execute legitimate-looking installer</text>
  <circle cx="260" cy="243" r="5" fill="#fb923c"/><text x="275" y="247" fill="#e2e8f0" font-size="12">Malicious payload activated in background</text>
  <path d="M450 267 L450 283" stroke="#475569" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="30" y="285" width="200" height="36" rx="6" fill="url(#phase3)" filter="url(#shadow)"/>
  <text x="130" y="308" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 3: Persistence &amp; C2</text>
  <rect x="240" y="285" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="308" r="5" fill="#facc15"/><text x="275" y="312" fill="#e2e8f0" font-size="12">Install persistent access mechanism on system</text>
  <circle cx="260" cy="333" r="5" fill="#facc15"/><text x="275" y="337" fill="#e2e8f0" font-size="12">Establish encrypted C2 channel</text>
  <circle cx="260" cy="358" r="5" fill="#facc15"/><text x="275" y="362" fill="#e2e8f0" font-size="12">Maintain capability for additional payload downloads</text>
  <path d="M450 382 L450 398" stroke="#475569" stroke-width="2" marker-end="url(#arrowhead)"/>
  <rect x="30" y="400" width="200" height="36" rx="6" fill="url(#phase4)" filter="url(#shadow)"/>
  <text x="130" y="423" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Phase 4: Objectives</text>
  <rect x="240" y="400" width="630" height="95" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <circle cx="260" cy="423" r="5" fill="#a78bfa"/><text x="275" y="427" fill="#e2e8f0" font-size="12">Collect development environment information</text>
  <circle cx="260" cy="448" r="5" fill="#a78bfa"/><text x="275" y="452" fill="#e2e8f0" font-size="12">Exfiltrate source code / credentials</text>
  <circle cx="260" cy="473" r="5" fill="#a78bfa"/><text x="275" y="477" fill="#e2e8f0" font-size="12">Establish foothold for internal network lateral movement</text>
</svg>

### 1.4 과거 유사 공급망 공격 비교

| 사건 | 연도 | 규모 | 공격자 | 영향 |
|------|------|------|--------|------|
| **SolarWinds** | 2020 | 18,000+ 기관 | 러시아 SVR | 미국 정부 기관 다수 침해 |
| **3CX** | 2023 | 600,000+ 기업 | 북한 Lazarus | 암호화폐 탈취 목적 |
| **XZ Utils** | 2024 | 리눅스 전체 | 미상 (국가급) | SSH 백도어 (사전 차단) |
| **Notepad++** | 2026 | 수백만 사용자 | 국가 지원 그룹 | 개발자/관리자 환경 침해 |

### 1.5 탐지: SIEM/EDR 쿼리

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

---

## 2. SK쉴더스 보안 리포트 종합 (11월~1월)

SK쉴더스 EQST가 2025년 11월부터 2026년 1월까지 발행한 보안 리포트를 **랜섬웨어, 제로트러스트, AI 보안, 인증 보안, 선제적 보안** 5개 축으로 재구성하여 분석합니다.

### 2.1 랜섬웨어 위협: BlackField, Sinobi, Gentlemen

#### BlackField 랜섬웨어 - 코드 재활용 생태계 경고 (11월호)

BlackField의 핵심 위험은 **LockBit, Babuk, Conti 등 유출된 소스코드를 복합 재활용**하여 만들어졌다는 점입니다.

| 시기 | 유출 소스코드 | 파생 그룹 |
|------|-------------|-----------|
| 2021년 | **Babuk** 소스코드 유출 | Rook, Pandora, AstraLocker 등 |
| 2022년 | **Conti** 내부 채팅/소스 유출 | Royal, Black Basta, Akira 등 |
| 2022년 | **LockBit 3.0** 빌더 유출 | BrainCipher, DragonForce 등 수십 개 파생 |
| 2025년 | 코드 재활용 가속 | **BlackField** (복합 재활용) |

> **출처**: [SK쉴더스 Keep up with Ransomware 11월호](https://www.skshieldus.com/download/files/download.do?o_fname=Keep%20up%20with%20Ransomware%2011%EC%9B%94%ED%98%B8%20%EA%B8%B0%EC%A1%B4%20%EB%9E%9C%EC%84%AC%EC%9B%A8%EC%96%B4%20%EC%BD%94%EB%93%9C%EB%A5%BC%20%EC%9E%AC%ED%99%9C%EC%9A%A9%ED%95%9C%20BlackField%20%EB%9E%9C%EC%84%AC%EC%9B%A8%EC%96%B4.pdf&r_fname=20251127174343776.pdf)

#### Sinobi 랜섬웨어 - Lynx 그룹 연계 (1월호)

SK쉴더스 KARA 분석에 따르면, **Sinobi는 Lynx 위협 그룹과 코드/인프라/TTP 수준에서 연계**가 확인되었습니다.

| 연계 유형 | 증거 |
|-----------|------|
| **코드 유사성** | 암호화 루틴, 파일 탐색 로직의 코드 패턴 일치 |
| **인프라 공유** | C2 서버 IP 대역, 도메인 등록 패턴 유사 |
| **TTP 일치** | 초기 접근, 횡이동, 암호화 실행 절차 유사 |
| **랜섬노트 유사성** | 협상 페이지 디자인, 지불 안내 문구 유사 |

> **출처**: [SK쉴더스 Keep up with Ransomware 1월호](https://www.skshieldus.com)

#### Gentlemen 랜섬웨어 위협 확산 (12월호)

SK쉴더스 12월호에서는 확산 중인 **Gentlemen 랜섬웨어** 위협을 분석했습니다.

> **출처**: [SK쉴더스 Keep up with Ransomware 12월호](https://www.skshieldus.com)

#### 공통 MITRE ATT&CK 매핑 (BlackField + Sinobi)

| MITRE ATT&CK ID | 기법명 | 적용 내용 |
|------------------|--------|-----------|
| **T1190** | Exploit Public-Facing Application | 공개 서비스 취약점 악용 |
| **T1566.001** | Spearphishing Attachment | 표적형 피싱 메일 |
| **T1059.001** | PowerShell | 악성 스크립트 실행 |
| **T1078** | Valid Accounts | 탈취 자격 증명으로 내부 이동 |
| **T1021.002** | SMB/Windows Admin Shares | 네트워크 횡이동 |
| **T1562.001** | Disable or Modify Tools | EDR/AV 비활성화 |
| **T1490** | Inhibit System Recovery | VSS 삭제, 백업 파괴 |
| **T1567** | Exfiltration Over Web Service | 이중 갈취 - 데이터 유출 |
| **T1486** | Data Encrypted for Impact | 파일 암호화 (핵심 목적) |

#### 랜섬웨어 탐지: SIEM 쿼리

```bash
# Splunk - Detect Ransomware Indicators (VSS Deletion + Backup Destruction)
index=endpoint sourcetype=sysmon EventCode=1
(CommandLine="*vssadmin*delete*shadows*" OR
 CommandLine="*wmic*shadowcopy*delete*" OR
 CommandLine="*bcdedit*/set*recoveryenabled*no*" OR
 CommandLine="*wbadmin*delete*catalog*")
| stats count by Computer, User, CommandLine, ParentProcessName
| sort -count

# Splunk - Detect Ransomware File Encryption Activity
index=endpoint sourcetype=sysmon EventCode=11
(TargetFilename="*.encrypted" OR TargetFilename="*.locked" OR
 TargetFilename="*.sinobi" OR TargetFilename="*README*ransom*")
| stats count by Computer, Image, TargetFilename
| where count > 50

# Elastic/KQL - Detect EDR/AV Tampering (T1562.001)
process.name: ("net.exe" OR "sc.exe" OR "taskkill.exe") AND
process.command_line: (*defender* OR *sentinel* OR *crowdstrike* OR *carbon* OR *symantec*)
```

---

### 2.2 제로트러스트 보안 전략

#### 데이터 중심 제로트러스트 (11월호)

공격자가 최종적으로 원하는 것은 네트워크가 아니라 **데이터**입니다. SK쉴더스 11월호는 데이터가 어디에 있든, 누가 접근하든 일관된 보호를 제공하는 전략을 제시합니다.

| 계층 | 내용 | 핵심 기술 |
|------|------|-----------|
| **Layer 1: 발견/분류** | 민감 데이터 자동 식별 및 분류 | DLP + AI 기반 자동 태깅 |
| **Layer 2: 보호** | 저장/전송/사용 중 전 구간 암호화 | AES-256, TLS 1.3, Confidential Computing |
| **Layer 3: 접근 제어** | 속성 기반 동적 접근 제어 | ABAC, Just-in-Time, 필드/행 단위 RBAC |
| **Layer 4: 모니터링** | 이상 접근 실시간 탐지 | 전수 로깅, DLP 차단, 컴플라이언스 자동 감사 |

> **출처**: [SK쉴더스 Special Report 11월호](https://www.skshieldus.com/download/files/download.do?o_fname=Special%20Report_11%EC%9B%94%ED%98%B8_%EC%A0%9C%EB%A1%9C%ED%8A%B8%EB%9F%AC%EC%8A%A4%ED%8A%B8%20%EB%B3%B4%EC%95%88%EC%A0%84%EB%9E%B5%20%EB%8D%B0%EC%9D%B4%ED%84%B0(Data).pdf&r_fname=20251127174412898.pdf)

#### 가시성 및 분석 (12월호)

12월호에서는 제로트러스트의 **Visibility & Analytics** 영역을 다루며, 네트워크/사용자/데이터 전반의 가시성 확보 전략을 제시합니다.

> **출처**: [SK쉴더스 Special Report 12월호](https://www.skshieldus.com)

---

### 2.3 Vertical AI: 보안 특화 AI (11월호)

범용 AI의 한계를 넘어 **사이버보안 도메인에 특화된 Vertical AI** 구축 전략입니다.

| 비교 항목 | General AI (범용) | Vertical AI (보안 특화) |
|-----------|------------------|------------------------|
| **학습 데이터** | 인터넷 전반 | 위협 인텔리전스, IOC, MITRE ATT&CK, 보안 로그 |
| **위협 탐지 정확도** | 기본적 패턴 인식 | SIEM/EDR 기반 정밀 탐지, 낮은 오탐률 |
| **IOC 분석** | 해시/IP/도메인 기본 분류 | 위협 컨텍스트 연관 분석, 자동 TTP 매핑 |
| **대응 판단** | 일반적 권고 | 조직 환경 맞춤 대응 시나리오 자동 생성 |
| **환각(Hallucination)** | 보안 맥락에서 위험 높음 | 도메인 파인튜닝으로 최소화 |

**3대 적용 영역**: SOC Tier 1 알림 분류 자동화, TTP 기반 위협 탐지 AI, 보안 특화 LLM 파인튜닝

> **출처**: [SK쉴더스 HeadLine 11월호](https://www.skshieldus.com/download/files/download.do?o_fname=HeadLine_11%EC%9B%94%ED%98%B8_%EC%82%AC%EC%9D%B4%EB%B2%84%EB%B3%B4%EC%95%88%20%ED%8A%B9%ED%99%94%20Vertical%20AI%20%EA%B5%AC%EC%B6%95%20%EB%B0%A9%EC%95%88.pdf&r_fname=20251127174323358.pdf)

---

### 2.4 레드팀 기반 사이버 면역 체계 (1월호)

**사후 대응에서 사전 예방으로의 패러다임 전환**을 다룹니다.

| 비교 항목 | 사후 대응(Reactive) | 선제적 보안(Proactive) |
|-----------|---------------------|----------------------|
| **시점** | 침해 발생 후 | 침해 발생 전 |
| **초점** | 피해 최소화, 복구 | 취약점 선제 제거, 방어력 강화 |
| **핵심 활동** | 사고 대응(IR), 포렌식 | 레드팀, 위협 헌팅, 공격 시뮬레이션 |
| **비용 효율** | 사고당 평균 $4.88M (IBM 2025) | 사전 투자로 사고 비용 절감 |

**사이버 면역 체계 4단계**: 위협 모델링 -> 공격 시뮬레이션 -> 방어 검증 -> 면역 강화 (지속 반복)

```bash
# Splunk - Detect Active Scanning (T1595)
index=firewall sourcetype=firewall_logs action=blocked
| stats dc(dest_port) as unique_ports, count by src_ip
| where unique_ports > 50 AND count > 200
| sort -unique_ports

# Splunk - Detect Brute Force Attempts (T1110)
index=auth sourcetype=windows_security EventCode=4625
| stats count as failed_attempts by src_ip, TargetUserName
| where failed_attempts > 10
| sort -failed_attempts
```

> **출처**: [SK쉴더스 HeadLine 1월호](https://www.skshieldus.com)

---

### 2.5 JWT 서명키 유출 인증 위협 (1월호)

JWT 서명키가 유출되면 **토큰 위조, 세션 하이재킹, 권한 상승** 공격 체인이 형성됩니다.

**JWT 서명 알고리즘별 위험도:**

| 알고리즘 | 유형 | 키 유출 시 위험 | 권장 |
|----------|------|----------------|------|
| **HS256** | 대칭키 (HMAC) | 유출 시 즉시 토큰 위조 가능 | 제한적 |
| **RS256** | 비대칭키 (RSA) | 개인키 유출 시만 위조 가능 | 권장 |
| **ES256** | 비대칭키 (ECDSA) | 개인키 유출 시만 위조, 짧은 키로 동등 보안 | 강력 권장 |
| **EdDSA** | 비대칭키 (Ed25519) | 최신, 높은 보안성과 성능 | 강력 권장 |

**주요 유출 경로**: 소스코드 하드코딩(매우 높음), 환경 변수 미설정(높음), 설정 파일(.env) 웹 노출(중간), 로그 기록(중간)

**대응 전략**: HS256 -> RS256/ES256 전환, 30-90일 키 순환 자동화, 15-30분 Access Token 만료, JWKS 엔드포인트 도입, AWS KMS/HashiCorp Vault 키 관리

```bash
# Splunk - Detect JWT Token Anomalies
index=web sourcetype=access_combined
| rex field=_raw "Bearer (?<jwt_token>[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)"
| eval jwt_header=base64decode(replace(mvindex(split(jwt_token,"."),0),"-_","+/"))
| where jwt_header LIKE "%none%" OR jwt_header LIKE "%HS256%"
| stats count by src_ip, uri_path, jwt_header
| where count > 100
```

> **출처**: [SK쉴더스 Research Technique 1월호](https://www.skshieldus.com)

---

### 2.6 OT 보안 및 EQST Insight

| 리포트 | 주제 | 핵심 |
|--------|------|------|
| **HeadLine 12월호** | 비즈니스를 위한 제조사 OT 보안 동향 | IT-OT 컨버전스 보안, ICS/SCADA 보호 |
| **EQST insight 11월호** | 분기별 위협 동향 종합 | 실제 침해 대응 경험 기반 인사이트 |
| **EQST insight 12월호** | 2025년 4분기 위협 종합, 2026년 전망 | AI 기반 공격 증가, 공급망 공격 고도화 |
| **EQST insight 1월호** | 1월 보안 인사이트 (목차) | HeadLine/Ransomware/Research Technique 요약 |

> **출처**: [SK쉴더스](https://www.skshieldus.com)

---

## 3. HashiCorp 보안 자동화

### 3.1 Boundary 0.21: 패스워드리스 RDP

RDP 자격 증명 관리의 보안 문제를 **인증서 기반 패스워드리스 접근**으로 해결합니다.

| 문제 | Boundary 0.21 해결 |
|------|-------------------|
| 공유 비밀번호 | 패스워드리스 인증 (인증서 기반) |
| 비밀번호 재사용 | 세션별 임시 자격 증명 |
| RDP 무차별 대입 | Boundary 프록시 간접 접근 |
| 세션 추적 불가 | 전체 세션 감사 로그 |

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
  <rect x="30" y="65" width="120" height="55" rx="10" fill="url(#b-gray)" filter="url(#sh3)"/>
  <text x="90" y="90" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">User</text>
  <text x="90" y="106" text-anchor="middle" fill="#cbd5e1" font-size="10">SSO / MFA</text>
  <line x1="150" y1="92" x2="195" y2="92" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <rect x="200" y="65" width="140" height="55" rx="10" fill="url(#b-blue)" filter="url(#sh3)"/>
  <text x="270" y="90" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Boundary Client</text>
  <line x1="340" y1="92" x2="395" y2="92" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <rect x="400" y="55" width="170" height="75" rx="10" fill="url(#b-purple)" filter="url(#sh3)"/>
  <text x="485" y="82" text-anchor="middle" fill="#fff" font-size="13" font-weight="700">Boundary Controller</text>
  <text x="485" y="100" text-anchor="middle" fill="#ddd6fe" font-size="10">AuthN / AuthZ</text>
  <text x="485" y="116" text-anchor="middle" fill="#ddd6fe" font-size="10">Ephemeral Cert Issue</text>
  <line x1="485" y1="130" x2="485" y2="175" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <rect x="400" y="180" width="170" height="65" rx="10" fill="url(#b-green)" filter="url(#sh3)"/>
  <text x="485" y="207" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">Boundary Worker</text>
  <text x="485" y="225" text-anchor="middle" fill="#a7f3d0" font-size="10">Cert-based RDP Proxy</text>
  <line x1="570" y1="212" x2="625" y2="212" stroke="#94a3b8" stroke-width="2" marker-end="url(#arr3)"/>
  <rect x="630" y="180" width="155" height="65" rx="10" fill="url(#b-gray)" filter="url(#sh3)"/>
  <text x="707" y="207" text-anchor="middle" fill="#fff" font-size="13" font-weight="600">RDP Target Server</text>
  <text x="707" y="225" text-anchor="middle" fill="#cbd5e1" font-size="10">Windows Server</text>
  <rect x="30" y="270" width="760" height="55" rx="8" fill="#1e293b" stroke="#334155" stroke-width="1"/>
  <text x="50" y="290" fill="#94a3b8" font-size="11" font-weight="600">Flow:</text>
  <text x="50" y="310" fill="#e2e8f0" font-size="11">1. User authenticates via SSO/MFA → 2. Ephemeral certificate issued per session → 3. Worker establishes RDP via cert → 4. Passwordless RDP session → 5. Cert auto-revoked on disconnect</text>
</svg>

> **출처**: [HashiCorp Blog](https://www.hashicorp.com/blog/boundary-0-21-improves-remote-access-security-and-ux-for-rdp-connections)

### 3.2 VSO: etcd 없이 Kubernetes 시크릿 관리

Kubernetes 기본 Secret은 **etcd에 base64 인코딩(암호화 아님!)으로 저장**됩니다. VSO는 시크릿을 etcd에 저장하지 않고 Vault에서 직접 Pod에 주입합니다.

| 비교 항목 | 기존 K8s Secret | VSO (etcd-free) |
|-----------|-----------------|-----------------|
| **저장 위치** | etcd (base64) | Vault에만 저장 |
| **암호화** | 별도 설정 필요 | Vault 자체 암호화 |
| **접근 제어** | K8s RBAC만 | Vault Policy + K8s RBAC 이중 |
| **시크릿 순환** | 수동 | VSO 자동 동기화 |
| **유출 시 영향** | etcd 백업에서 평문 노출 | etcd에 시크릿 없음 |

> **출처**: [HashiCorp Blog](https://www.hashicorp.com/blog/deliver-secrets-to-kubernetes-pods-without-storing-in-etcd-using-vso)

---

## 4. AI 에이전트 보안

### 4.1 Amazon Bedrock AgentCore 접근 제어

멀티에이전트 환경에서 **최소 권한 원칙**을 에이전트 수준에서 구현합니다.

| 원칙 | 구현 방식 | 보안 효과 |
|------|----------|-----------|
| **최소 권한** | 에이전트별 독립 IAM 역할 | 침해 시 피해 범위 한정 |
| **권한 분리** | 읽기 전용 / 쓰기 가능 에이전트 분리 | 데이터 무결성 보호 |
| **세션 격리** | 에이전트 간 세션 데이터 격리 | 크로스 에이전트 데이터 유출 방지 |
| **인간 승인 게이트** | 고위험 작업은 인간 승인 필수 | 자율 에이전트 오작동 제어 |

이 패턴은 OWASP Agentic AI Top 10의 **"Excessive Agency"** 위협에 대한 실전적 대응입니다.

> **출처**: [AWS Korea Blog](https://aws.amazon.com/ko/blogs/tech/multi-agent-operations-for-airline-agentcore-service/)

---

## 트렌드 분석

| 트렌드 | 관련 내용 | 영향도 | 대응 시급성 |
|--------|-----------|--------|------------|
| **공급망 공격 고도화** | Notepad++ 국가 지원 공급망 침해 | Critical | 즉시 |
| **랜섬웨어 생태계 변화** | BlackField 코드 재활용, Sinobi-Lynx 연계, Gentlemen 확산 | Critical | 즉시 |
| **인증 체계 근본 위협** | JWT 서명키 유출 공격 체인 | High | 단기 |
| **데이터 중심 보안** | 제로트러스트 데이터/가시성 전략 | High | 중기 |
| **보안 AI 전문화** | Vertical AI SOC 자동화 | High | 중기 |
| **레드팀 주류화** | 사이버 면역 체계 구축 | High | 중기 |
| **패스워드리스 확산** | HashiCorp Boundary 0.21 RDP | Medium | 중기 |
| **AI 에이전트 거버넌스** | Bedrock AgentCore 접근 제어 | Medium | 중기 |

**핵심 교차점**: JWT 서명키 유출 -> 유효한 자격 증명 탈취(T1078) -> 랜섬웨어 초기 접근. JWT 보안 강화는 랜섬웨어 초기 접근 차단과도 직결됩니다. 레드팀이 Sinobi TTP를 시뮬레이션하여 방어 능력을 검증하고, Vertical AI가 탐지 자동화를 지원하는 **통합 면역 체계**가 완성됩니다.

---

## 실무 체크리스트

### P0 - 즉시

- [ ] Notepad++ 설치 현황 파악 및 해시 검증 ([공식 공지](https://notepad-plus-plus.org/news/hijacked-incident-info-update/))
- [ ] EDR/SIEM에 Notepad++ 비정상 행위 및 랜섬웨어 탐지 쿼리 적용
- [ ] Sinobi/Lynx IOC 반영 (SK쉴더스 KARA 리포트 참조)
- [ ] 백업 무결성 검증 및 복구 테스트 수행
- [ ] JWT 시크릿 긴급 점검: 소스코드/설정 파일 하드코딩 스캔 (trufflehog, gitleaks)

### P1 - 이번 주

- [ ] JWT 서명 알고리즘 감사: HS256 사용 서비스 -> RS256/ES256 전환 계획
- [ ] Kubernetes 시크릿 관리 점검 (etcd 암호화 또는 VSO 도입)
- [ ] RDP 접근 관리 현황 점검 (Boundary 0.21 패스워드리스 평가)
- [ ] MITRE ATT&CK 커버리지 측정: 현재 탐지 룰의 매트릭스 커버리지율
- [ ] 위협 인텔리전스 피드: Lynx/BlackField/Sinobi IOC 구독/갱신

### P2 - 이번 달

- [ ] 레드팀 프로그램 기획: Sinobi TTP 기반 시나리오 포함
- [ ] 데이터 중심 제로트러스트 로드맵: 데이터 분류 -> 보호 -> 모니터링
- [ ] Vertical AI 파일럿: SOC Tier 1 알림 분류 자동화 PoC
- [ ] 공급망 보안 정책 수립: SBOM 관리, 코드 서명 검증 프로세스
- [ ] OT 보안 점검: IT-OT 경계 보안 상태 확인

---

## 참고 자료

### 공급망 보안

| 제목 | URL |
|------|-----|
| Notepad++ Hijacked Incident Info Update | [Notepad++](https://notepad-plus-plus.org/news/hijacked-incident-info-update/) |
| MITRE ATT&CK T1195 - Supply Chain Compromise | [MITRE](https://attack.mitre.org/techniques/T1195/) |

### SK쉴더스 보안 리포트

| 리포트 | URL |
|--------|-----|
| HeadLine 11월호 - Vertical AI 구축 방안 | [SK쉴더스](https://www.skshieldus.com) |
| HeadLine 12월호 - 제조사 OT 보안 동향 | [SK쉴더스](https://www.skshieldus.com) |
| HeadLine 1월호 - 레드팀 사이버 면역 체계 | [SK쉴더스](https://www.skshieldus.com) |
| Ransomware 11월호 - BlackField 코드 재활용 | [SK쉴더스](https://www.skshieldus.com) |
| Ransomware 12월호 - Gentlemen 랜섬웨어 | [SK쉴더스](https://www.skshieldus.com) |
| Ransomware 1월호 - Sinobi + Lynx 연계 | [SK쉴더스](https://www.skshieldus.com) |
| Special Report 11월호 - 제로트러스트 데이터 | [SK쉴더스](https://www.skshieldus.com) |
| Special Report 12월호 - 가시성 및 분석 | [SK쉴더스](https://www.skshieldus.com) |
| Research Technique 1월호 - JWT 인증 위협 | [SK쉴더스](https://www.skshieldus.com) |

### DevOps 보안

| 제목 | URL |
|------|-----|
| HashiCorp Boundary 0.21 - Passwordless RDP | [HashiCorp](https://www.hashicorp.com/blog/boundary-0-21-improves-remote-access-security-and-ux-for-rdp-connections) |
| VSO - K8s Secrets without etcd | [HashiCorp](https://www.hashicorp.com/blog/deliver-secrets-to-kubernetes-pods-without-storing-in-etcd-using-vso) |

### AI 에이전트 보안

| 제목 | URL |
|------|-----|
| Amazon Bedrock AgentCore 멀티에이전트 운영 | [AWS Korea](https://aws.amazon.com/ko/blogs/tech/multi-agent-operations-for-airline-agentcore-service/) |
| OWASP Agentic AI Top 10 | [OWASP](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |

### 보안 프레임워크

| 리소스 | URL |
|--------|-----|
| MITRE ATT&CK Framework | [attack.mitre.org](https://attack.mitre.org/) |
| MITRE ATT&CK T1486 - Data Encrypted for Impact | [MITRE](https://attack.mitre.org/techniques/T1486/) |
| NIST Zero Trust Architecture (SP 800-207) | [NIST](https://csrc.nist.gov/publications/detail/sp/800-207/final) |
| CISA KEV | [CISA](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |

---

*이 글은 [Twodragon's Tech Blog](https://tech.2twodragon.com)에서 매주 발행하는 Security Threat Intelligence Digest입니다. 최신 보안 뉴스와 실무 가이드를 매주 받아보세요.*

**작성자**: Twodragon
