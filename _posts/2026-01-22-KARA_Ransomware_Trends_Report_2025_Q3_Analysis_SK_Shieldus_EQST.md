---
layout: post
title: "2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략"
date: 2026-01-22 14:30:00 +0900
categories: [security, incident]
tags: [Ransomware, KARA, SK-Shieldus, LockBit, Akira, INC-Ransomware, Threat-Intelligence, DevSecOps, Zero-Trust, "2025"]
excerpt: "2025년 3분기 랜섬웨어 1,517건 발생. LockBit 5.0 재등장, Akira 제조업 타겟, 제로 트러스트 대응 전략."
description: "SK쉴더스 EQST insight 기반 2025년 3분기 랜섬웨어 동향 분석. KARA 보고서의 주요 그룹(LockBit 5.0, Akira, INC Ransomware) 분석, 공격 통계, 최신 TTPs, YARA/Sigma 탐지 룰, 제로 트러스트 기반 기업 대응 전략."
keywords: "랜섬웨어, KARA, SK쉴더스, LockBit 5.0, Akira, INC Ransomware, 제로 트러스트, YARA, Sigma, 침해사고대응, SOC, CERT, 2025년 3분기"
author: Twodragon
comments: true
image: /assets/images/2026-01-22-KARA_Ransomware_Trends_2025_Q3.svg
image_alt: "KARA Ransomware Trends Report 2025 Q3 Analysis - Attack Statistics, Major Groups, Defense Strategies"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag incident">Incident</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Ransomware</span>
      <span class="tag">KARA</span>
      <span class="tag">SK-Shieldus</span>
      <span class="tag">LockBit</span>
      <span class="tag">Akira</span>
      <span class="tag">INC-Ransomware</span>
      <span class="tag">Threat-Intelligence</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">2025</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>공격 규모</strong>: 2025년 3분기 전 세계 1,517~1,733건 랜섬웨어 공격 발생 (전년 대비 36% 증가)</li>
      <li><strong>생태계 분절화</strong>: 77개 활동 그룹 (역대 최다), 상위 10개 그룹이 56%만 차지</li>
      <li><strong>주요 그룹</strong>: Qilin (+318%), Akira, INC Ransomware, LockBit 5.0 (9월 재등장)</li>
      <li><strong>타겟 산업</strong>: 제조업 1위 (+56%), 헬스케어, 금융권 지속적 표적</li>
      <li><strong>새로운 전술</strong>: 4중 협박(Quadruple Extortion), 규제 무기화, AI 기반 공격</li>
      <li><strong>대응 전략</strong>: 제로 트러스트, 3-2-1-1-0 백업, CISA KEV 패치, YARA/Sigma 탐지 룰</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">출처</span>
    <span class="summary-value">SK쉴더스 EQST insight, KARA, CISA, GuidePoint GRIT, Checkpoint, Mandiant</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, CISO, DevSecOps 엔지니어, SOC 분석가, 침해사고대응팀(CERT)</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다.

2025년 랜섬웨어 위협은 그 어느 때보다 복잡하고 교묘해지고 있습니다. SK쉴더스 EQST(Experts, Qualified Security Team)에서 발간하는 **KARA(Korea Anti-Ransomware Alliance) 랜섬웨어 동향 보고서**를 바탕으로 2025년 3분기 핵심 동향을 심층 분석합니다.

이번 포스팅에서는 다음 내용을 다룹니다:

- 2025년 3분기 글로벌 랜섬웨어 공격 통계 및 트렌드
- 주요 랜섬웨어 그룹별 특성 및 기술적 분석
- 최신 공격 기법(TTPs) 및 초기 침투 벡터
- YARA/Sigma 탐지 룰 및 IOC 기반 모니터링
- 실효성 있는 기업 대응 전략 및 체크리스트

> **참고**: 본 포스팅은 SK쉴더스 EQST insight의 KARA 보고서와 GuidePoint GRIT, Checkpoint, CISA, Mandiant 등의 글로벌 위협 인텔리전스를 종합하여 작성되었습니다.

## 📊 빠른 참조

### 2025년 3분기 랜섬웨어 핵심 지표

| 지표 | 수치 | 전년 대비 | 시사점 |
|------|------|----------|--------|
| **총 공격 건수** | 1,517~1,733건 | +36% | 분기별 기준선 상향 |
| **월평균 피해자** | 535건/월 | 역대 최고 수준 | 지속적 위협 증가 |
| **활동 그룹 수** | 77개 | +57% | 생태계 분절화 심화 |
| **랜섬 지불률** | 23% | 역대 최저 | 기업 대응력 향상 |
| **평균 랜섬 금액** | $376,941 | -66% QoQ | 지불 거부로 인한 가격 하락 |
| **데이터 유출 사이트** | 85개 | 역대 최다 | 추적 복잡도 증가 |

### 2025년 3분기 주요 랜섬웨어 이슈

| 이슈 | 출처 | 영향도 | 권장 조치 |
|------|------|--------|----------|
| **LockBit 5.0 재등장** | Flashpoint | 높음 | EDR 우회 기법 탐지 룰 업데이트 |
| **제조업 공격 급증** | GRIT | 높음 | OT/IT 보안 통합 강화 |
| **INC Ransomware Rust 버전** | SK쉴더스 EQST | 높음 | Rust 기반 악성코드 탐지 강화 |
| **4중 협박 전술 확산** | Checkpoint | 높음 | DDoS 방어 및 고객 통신 보호 |
| **CVE-2024-40766 악용** | CISA | 긴급 | SonicWall 패치 즉시 적용 |

---

## 1. 2025년 3분기 랜섬웨어 동향 개요

### 1.1 공격 추이 분석

2025년 3분기 랜섬웨어 공격은 전년 대비 **36% 증가**하며 지속적인 상승세를 보였습니다:

| 월 | 공격 건수 | 전년 대비 | 주요 이벤트 |
|----|----------|----------|------------|
| **7월** | 96건 | +50% | Akira 활동 급증 |
| **8월** | 92건 | +37% | INC Ransomware Rust 버전 등장 |
| **9월** | 85건 | +27% | LockBit 5.0 런칭 |

### 1.2 생태계 분절화 현상

랜섬웨어 생태계는 점점 더 **분절화**되고 있습니다:

<div class="post-image-container">
  <img src="/assets/images/2026-01-22-ransomware-ecosystem-2025q3.svg" alt="Ransomware Ecosystem Fragmentation 2025 Q3 - 77 Active Groups" class="post-image">
  <p class="image-caption">2025년 3분기 랜섬웨어 생태계 분절화 - 활동 그룹 77개로 급증</p>
</div>

```
┌─────────────────────────────────────────────────────────────────┐
│              2025년 3분기 랜섬웨어 생태계 변화                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   2025 Q1                        2025 Q3                        │
│   ┌─────────────────┐            ┌─────────────────┐           │
│   │ 상위 10개 그룹   │            │ 상위 10개 그룹   │           │
│   │     71%         │            │     56%         │           │
│   └─────────────────┘            └─────────────────┘           │
│   ┌─────────────────┐            ┌─────────────────┐           │
│   │ 기타 그룹       │            │ 기타 그룹       │           │
│   │     29%         │            │     44%         │           │
│   └─────────────────┘            └─────────────────┘           │
│                                                                 │
│   활동 그룹: 49개                 활동 그룹: 77개 (+57%)        │
│   데이터 유출 사이트: 62개        데이터 유출 사이트: 85개      │
│                                                                 │
│   시사점: 소규모 그룹 급증으로 추적 및 대응 복잡도 증가         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 랜섬 지불률 하락 추세

기업들의 랜섬 지불 거부가 증가하고 있습니다:

| 연도 | 지불률 | 평균 지불 금액 | 비고 |
|------|--------|---------------|------|
| 2022 | 41% | $812,000 | 최고점 |
| 2023 | 34% | $568,000 | 하락 시작 |
| 2024 | 28% | $420,000 | 지속 하락 |
| 2025 Q3 | **23%** | **$376,941** | 역대 최저 |

> **시사점**: 지불률 하락에도 불구하고 공격 건수는 증가. 공격자들은 볼륨 전략으로 전환 중.

---

## 2. 주요 랜섬웨어 그룹 심층 분석

### 2.1 2025년 3분기 상위 랜섬웨어 그룹

| 순위 | 그룹명 | 피해자 수 | 전년 대비 | 주요 타겟 | 특징 |
|------|--------|----------|----------|----------|------|
| 1 | **Qilin** | ~250건 | +318% | 헬스케어, IT | Agenda 기반, 빠른 성장 |
| 2 | **Akira** | 150~155건 | +212% | 제조업, VPN | SonicWall 취약점 악용 |
| 3 | **INC Ransomware** | 90~114건 | +90% QoQ | 의료, 공공 | Rust 버전 신규 |
| 4 | **Play** | 102건 | -17.6% QoQ | 중소기업 | 900건+ 누적 피해 |
| 5 | **SafePay** | 90건 | 신규 | 다양 | 신규 그룹 |
| 6 | **Cl0p** | ~100건 | -12.95% QoQ | 파일 전송 SW | Cleo 취약점 악용 |

### 2.2 LockBit 5.0 기술적 분석

2025년 9월, LockBit 그룹이 **LockBit 5.0**으로 복귀했습니다:

#### LockBit 5.0 주요 특징

| 특징 | 설명 | 탐지 포인트 |
|------|------|------------|
| **멀티 플랫폼** | Windows, Linux, VMware ESXi | 각 플랫폼별 IOC 모니터링 |
| **향상된 EDR 우회** | 프로세스 홀로잉, ETW 패칭 | 메모리 스캔, 커널 모니터링 |
| **빠른 암호화** | 멀티스레드, 부분 암호화 | 대량 파일 변경 탐지 |
| **어필리에이트 장벽** | $500 비트코인 예치 | - |

#### LockBit 5.0 공격 체인

```yaml
# LockBit 5.0 공격 체인 분석
attack_chain:
  initial_access:
    - technique: T1566 (Phishing)
    - technique: T1133 (External Remote Services)
    - tools: [Cobalt Strike, SystemBC]
    
  execution:
    - technique: T1059.001 (PowerShell)
    - technique: T1047 (WMI)
    - evasion: DLL Reflection, Dynamic API Resolution
    
  persistence:
    - technique: T1547.001 (Registry Run Keys)
    - technique: T1053.005 (Scheduled Task)
    
  defense_evasion:
    - technique: T1562.001 (Disable Security Tools)
    - method: Process Hollowing
    - method: ETW Patching
    - method: Library Unhooking
    
  credential_access:
    - tools: [Mimikatz, LaZagne, Rubeus]
    
  lateral_movement:
    - technique: T1021.001 (RDP)
    - technique: T1021.002 (SMB/Windows Admin Shares)
    
  exfiltration:
    - tools: [Rclone, MEGASync, 7zip]
    - destinations: [MEGA, Dropbox, Private Servers]
    
  impact:
    - encryption: ChaCha20 + RSA-4096
    - deletion: Shadow Copy, Backup Catalogs
```

#### LockBit 5.0 YARA 탐지 룰

```yara
rule LockBit_5_0_Ransomware
{
    meta:
        description = "Detects LockBit 5.0 ransomware"
        author = "Twodragon"
        reference = "SK Shieldus EQST / Flashpoint"
        date = "2025-09"
        severity = "critical"
        
    strings:
        // LockBit 5.0 특징적 문자열
        $lockbit_marker = "LockBit" ascii wide
        $ransom_note = "Restore-My-Files.txt" ascii wide
        $mutex_pattern = "Global\\LockBit" ascii wide
        
        // 암호화 관련
        $chacha20 = { 65 78 70 61 6E 64 20 33 32 2D 62 79 74 65 20 6B }
        $rsa_marker = { 30 82 ?? ?? 02 82 }
        
        // EDR 우회 기법
        $etw_patch = { 48 33 C0 C3 }  // xor rax, rax; ret
        $unhook_ntdll = "ntdll.dll" ascii
        
        // API 동적 해석
        $api_hash_1 = { 0F B6 ?? 33 ?? C1 ?? 05 }
        
    condition:
        uint16(0) == 0x5A4D and
        filesize < 10MB and
        (
            ($lockbit_marker and $ransom_note) or
            ($mutex_pattern and $chacha20) or
            (2 of ($etw_patch, $unhook_ntdll, $api_hash_1))
        )
}
```

### 2.3 INC Ransomware Rust 버전 분석

SK쉴더스 EQST의 "Keep up with Ransomware" 시리즈에서 집중 분석한 **INC Ransomware**:

#### INC Ransomware 특징

| 특징 | C++ 버전 | Rust 버전 |
|------|----------|----------|
| **언어** | C++ | Rust |
| **암호화** | AES-256 + RSA | ChaCha20 + Curve25519 |
| **플랫폼** | Windows | Windows, Linux |
| **탐지 회피** | 기본 | 메모리 안전성으로 분석 어려움 |
| **등장 시기** | 2024 Q1 | 2025 Q3 |

#### INC Ransomware Sigma 탐지 룰

```yaml
title: INC Ransomware Process Activity
id: 8a7b9c0d-1e2f-3g4h-5i6j-7k8l9m0n1o2p
status: experimental
description: Detects INC Ransomware process execution patterns
author: Twodragon
date: 2025/09/15
references:
    - https://www.skshieldus.com/kor/media/newsletter/insight.do
logsource:
    category: process_creation
    product: windows
detection:
    selection_parent:
        ParentImage|endswith:
            - '\cmd.exe'
            - '\powershell.exe'
            - '\wscript.exe'
    selection_process:
        Image|endswith:
            - '\inc.exe'
            - '\inc_ransomware.exe'
        CommandLine|contains:
            - '--encrypt'
            - '--path'
            - '--key'
    selection_vssadmin:
        Image|endswith: '\vssadmin.exe'
        CommandLine|contains: 'delete shadows'
    selection_wmic:
        Image|endswith: '\wmic.exe'
        CommandLine|contains: 'shadowcopy delete'
    condition: selection_parent and (selection_process or selection_vssadmin or selection_wmic)
level: critical
tags:
    - attack.impact
    - attack.t1486
    - attack.t1490
falsepositives:
    - Legitimate backup software
```

### 2.4 Akira 랜섬웨어 - SonicWall 취약점 악용

| 항목 | 내용 |
|------|------|
| **주요 취약점** | CVE-2024-40766 (SonicWall SSLVPN) |
| **타겟 산업** | 제조업, 헬스케어, 금융 |
| **침투 방식** | VPN 취약점 → 내부망 횡적 이동 |
| **암호화 방식** | ChaCha20 + RSA-4096 |
| **특이사항** | Nutanix AHV 최초 암호화 성공 (2025년 6월) |

```bash
# SonicWall 취약점 확인 명령어
# CVE-2024-40766 영향받는 버전 확인

# SonicOS 버전 확인
show version

# 영향받는 버전:
# - SonicOS 7.0.x (7.0.1-5161 이전)
# - SonicOS 6.5.x (6.5.4.15-117n 이전)

# 즉시 패치 적용:
# 1. SonicWall 지원 포털에서 최신 펌웨어 다운로드
# 2. SSLVPN Default Users Group 비활성화
# 3. MFA 강제 적용
```

---

## 3. 최신 공격 기법(TTPs) 심층 분석

### 3.1 4중 협박(Quadruple Extortion)

2025년 새롭게 부각된 **4중 협박** 전술:

<div class="post-image-container">
  <img src="/assets/images/2026-01-22-quadruple-extortion.svg" alt="Quadruple Extortion Tactics - 4-Layer Ransomware Pressure Strategy" class="post-image">
  <p class="image-caption">4중 협박(Quadruple Extortion) 전술 - 단계별 압박 전략</p>
</div>

```
┌─────────────────────────────────────────────────────────────────┐
│              4중 협박(Quadruple Extortion) 전술                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1단계: 데이터 암호화 + 랜섬 요구                          │   │
│  │        └─ "파일 복호화에 $500,000 지불하라"               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓ 거부 시                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2단계: 데이터 유출 협박                                   │   │
│  │        └─ "72시간 내 지불하지 않으면 Dark Web 공개"       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓ 거부 시                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3단계: DDoS 공격                                          │   │
│  │        └─ "서비스를 마비시켜 추가 압박"                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          ↓ 거부 시                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4단계: 고객/파트너/언론 직접 연락                         │   │
│  │        └─ "귀사의 데이터 유출 사실을 알립니다"            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 규제 무기화(Regulatory Weaponization)

공격자들이 새롭게 사용하는 전술:

| 규제 | 악용 방식 | 대상 기업 |
|------|----------|----------|
| **GDPR** | EU 규제 당국에 데이터 유출 신고 협박 | EU 사업 기업 |
| **SEC** | 미국 증권거래위원회에 신고 협박 | 미국 상장 기업 |
| **HIPAA** | 의료 정보 유출로 규제 위반 협박 | 헬스케어 |
| **PCI-DSS** | 카드 정보 유출로 인증 박탈 협박 | 금융/소매 |

### 3.3 초기 침투 벡터 (2025년 3분기)

| 벡터 | 비중 | 주요 기법 | 탐지 방법 |
|------|------|----------|----------|
| **유효 계정/탈취 크리덴셜** | 1위 | 피싱, 헬프데스크 사칭, Teams 사칭 | 이상 로그인 탐지 |
| **취약점 익스플로잇** | 2위 | CVE-2024-40766, CVE-2025-61882 | 취약점 스캔, 패치 관리 |
| **VPN 취약점** | 3위 | SonicWall, Fortinet, Ivanti | VPN 접근 로그 모니터링 |
| **드라이브바이 다운로드** | 신규 | 정상 웹사이트 변조 | 웹 트래픽 분석 |
| **ClickFix 소셜엔지니어링** | 신규 | 가짜 CAPTCHA → PowerShell | PowerShell 로깅 |

### 3.4 EDR 우회 기법 상세

```yaml
# 2025년 3분기 주요 EDR 우회 기법
edr_evasion_techniques:
  
  process_hollowing:
    description: "정상 프로세스에 악성 코드 주입"
    used_by: [LockBit5.0, BlackCat]
    detection:
      - "프로세스 메모리 영역 변경 모니터링"
      - "CreateProcess + WriteProcessMemory 조합 탐지"
    sigma_rule: |
      detection:
        selection:
          - EventID: 10  # Process Access
          - TargetImage|endswith: '\svchost.exe'
          - GrantedAccess|contains: '0x1F0FFF'
  
  library_unhooking:
    description: "보안 솔루션의 API 후킹 해제"
    used_by: [LockBit5.0, Akira]
    detection:
      - "ntdll.dll 직접 로드 탐지"
      - "syscall 직접 호출 모니터링"
  
  etw_patching:
    description: "Event Tracing for Windows 비활성화"
    used_by: [LockBit5.0]
    detection:
      - "EtwEventWrite 함수 패치 탐지"
      - "커널 수준 ETW 모니터링"
    ioc_pattern: "48 33 C0 C3"  # xor rax, rax; ret
  
  edr_killer:
    description: "EDR 프로세스 강제 종료"
    used_by: [RansomHub]
    tool: "EDRKillShifter"
    detection:
      - "BYOVD(Bring Your Own Vulnerable Driver) 탐지"
      - "서명된 드라이버 악용 모니터링"
  
  byovd:
    description: "취약한 드라이버를 통한 커널 접근"
    used_by: [Multiple Groups]
    vulnerable_drivers:
      - "Process Explorer driver (dbutil_2_3.sys)"
      - "Intel driver (iqvw64e.sys)"
      - "RentDrv2 driver (rentdrv2.sys)"
    detection:
      - "알려진 취약 드라이버 로드 탐지"
      - "드라이버 로드 이벤트 모니터링 (Sysmon ID 6)"
```

---

## 4. 산업별 표적 분석

### 4.1 2025년 산업별 공격 현황

| 순위 | 산업 | 공격 비중 | 전년 대비 | 주요 공격 그룹 | 취약점 |
|------|------|----------|----------|---------------|--------|
| 1 | **제조업** | 26% | +56% | Akira, Play, INC | OT/IT 통합 |
| 2 | **헬스케어** | 8% | 정체 | INC, BlackCat | HIPAA 데이터 |
| 3 | **금융 서비스** | - | +65% | Cl0p, LockBit | 파일 전송 SW |
| 4 | **비즈니스 서비스** | 10% | - | Qilin | 원격 접속 |
| 5 | **법률** | - | +54% | - | 기밀 문서 |
| 6 | **소매** | - | +37% | - | POS 시스템 |

### 4.2 제조업 공격 급증 원인 분석

<div class="post-image-container">
  <img src="/assets/images/2026-01-22-manufacturing-targeting.svg" alt="Why Manufacturing is Ransomware Target Number 1 - 4 Key Reasons" class="post-image">
  <p class="image-caption">제조업이 랜섬웨어 #1 타겟인 4가지 이유</p>
</div>

```
┌─────────────────────────────────────────────────────────────────┐
│              제조업이 랜섬웨어 #1 타겟인 이유                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 가동 중단 비용이 극히 높음                                   │
│     ├─ 분당 수십만 달러 손실 가능                               │
│     ├─ 생산 라인 중단 시 납기 지연                              │
│     └─ 공급망 전체에 영향 파급                                  │
│                                                                 │
│  2. OT/IT 통합으로 공격 표면 확대                                │
│     ├─ 레거시 SCADA/ICS 시스템 취약점                           │
│     ├─ IT 네트워크에서 OT 네트워크로 피벗 가능                  │
│     └─ 패치 주기가 길거나 불가능한 시스템                       │
│                                                                 │
│  3. 랜섬 지불 압박 극대화                                        │
│     ├─ JIT(Just-In-Time) 생산 방식의 취약성                     │
│     ├─ 계약 위약금 발생 압박                                    │
│     └─ 고객사 신뢰 손상 우려                                    │
│                                                                 │
│  4. 상대적으로 낮은 보안 성숙도                                  │
│     ├─ IT 보안 투자 대비 OT 보안 미흡                           │
│     ├─ 보안 인력 부족                                           │
│     └─ 인식 교육 부재                                           │
│                                                                 │
│  대응 전략:                                                      │
│  - OT/IT 네트워크 분리 (Air Gap 또는 단방향 게이트웨이)         │
│  - 산업용 방화벽 및 IDS/IPS 도입                                │
│  - OT 전용 EDR 솔루션 검토                                      │
│  - 정기적인 OT 보안 평가 및 모의 훈련                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 주요 악용 취약점 (CISA KEV 기준)

| CVE | 제품 | CVSS | 악용 그룹 | 패치 상태 |
|-----|------|------|----------|----------|
| **CVE-2024-40766** | SonicWall SSLVPN | 9.8 | Akira | 긴급 패치 필요 |
| **CVE-2025-61882** | Oracle E-Business Suite | 9.1 | Cl0p | 패치 가용 |
| **CVE-2024-21887** | Ivanti Connect Secure | 9.1 | Multiple | 패치 가용 |
| **CVE-2024-1709** | ConnectWise ScreenConnect | 10.0 | Multiple | 패치 가용 |
| **CVE-2024-3400** | Palo Alto PAN-OS | 10.0 | Multiple | 패치 가용 |

---

## 5. 기업 대응 전략

### 5.1 제로 트러스트 아키텍처 구현

```yaml
# 제로 트러스트 구현 체크리스트
zero_trust_implementation:
  
  identity_verification:
    - name: "MFA 전면 적용"
      priority: critical
      implementation:
        - "모든 VPN 접근에 MFA 필수"
        - "클라우드 서비스 MFA 필수"
        - "하드웨어 키(YubiKey) 권장"
      tools: [Okta, Azure AD, Duo]
      
    - name: "SSO 통합"
      priority: high
      implementation:
        - "SAML/OIDC 기반 SSO"
        - "세션 타임아웃 강화"
      
  device_trust:
    - name: "디바이스 상태 검증"
      priority: high
      implementation:
        - "EDR 에이전트 설치 필수"
        - "OS 패치 수준 검증"
        - "디스크 암호화 필수"
      tools: [CrowdStrike, SentinelOne, MS Defender]
      
  network_segmentation:
    - name: "마이크로 세그멘테이션"
      priority: high
      implementation:
        - "워크로드 단위 격리"
        - "East-West 트래픽 제어"
        - "OT/IT 네트워크 분리"
      tools: [Illumio, Guardicore, VMware NSX]
      
  least_privilege:
    - name: "최소 권한 원칙"
      priority: critical
      implementation:
        - "JIT(Just-In-Time) 접근 권한"
        - "PAM(Privileged Access Management)"
        - "정기적 권한 검토 (분기별)"
      tools: [CyberArk, BeyondTrust, HashiCorp Vault]
      
  continuous_monitoring:
    - name: "지속적 모니터링"
      priority: critical
      implementation:
        - "SIEM/SOAR 통합"
        - "UEBA(User Entity Behavior Analytics)"
        - "24x7 SOC 운영"
      tools: [Splunk, Microsoft Sentinel, Elastic SIEM]
```

### 5.2 3-2-1-1-0 백업 전략

<div class="post-image-container">
  <img src="/assets/images/2026-01-22-backup-strategy-321-10.svg" alt="3-2-1-1-0 Backup Strategy for Ransomware Defense" class="post-image">
  <p class="image-caption">3-2-1-1-0 백업 전략 - 랜섬웨어 방어를 위한 강화된 백업 규칙</p>
</div>

```
┌─────────────────────────────────────────────────────────────────┐
│              3-2-1-1-0 백업 전략                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   3 - 데이터의 3개 복사본 유지                                   │
│       ├─ 프로덕션 데이터                                        │
│       ├─ 로컬 백업                                              │
│       └─ 원격 백업                                              │
│                                                                 │
│   2 - 2가지 다른 미디어 타입 사용                               │
│       ├─ 디스크 기반 백업                                       │
│       └─ 테이프/클라우드 백업                                   │
│                                                                 │
│   1 - 1개는 오프사이트(원격지) 저장                             │
│       └─ 지리적으로 분리된 위치                                 │
│                                                                 │
│   1 - 1개는 불변(Immutable) 백업                                │
│       ├─ WORM(Write Once Read Many)                            │
│       ├─ Object Lock (AWS S3)                                  │
│       └─ 에어갭(Air-gapped) 백업                                │
│                                                                 │
│   0 - 복구 테스트에서 0개 에러                                   │
│       ├─ 정기적 복구 테스트 (월 1회 이상)                       │
│       ├─ 전체 복구 시뮬레이션 (분기 1회)                        │
│       └─ RTO/RPO 충족 검증                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### AWS S3 Immutable 백업 설정

```json
{
    "Rules": [
        {
            "ID": "ransomware-protection-rule",
            "Status": "Enabled",
            "Filter": {
                "Prefix": "backups/"
            },
            "DefaultRetention": {
                "Mode": "COMPLIANCE",
                "Days": 365
            }
        }
    ]
}
```

```bash
# AWS CLI로 Object Lock 설정
aws s3api put-object-lock-configuration \
    --bucket backup-bucket \
    --object-lock-configuration '{
        "ObjectLockEnabled": "Enabled",
        "Rule": {
            "DefaultRetention": {
                "Mode": "COMPLIANCE",
                "Days": 365
            }
        }
    }'
```

### 5.3 침해 지표(IOC) 모니터링 자동화

```yaml
# Sigma 룰 - 랜섬웨어 초기 침투 징후 탐지
title: Ransomware Initial Access Indicators
id: 3f4e5d6c-7b8a-9c0d-1e2f-3g4h5i6j7k8l
status: production
description: Detects common ransomware initial access indicators
author: Twodragon
date: 2025/09/20
references:
    - https://attack.mitre.org/techniques/T1566/
    - https://www.cisa.gov/known-exploited-vulnerabilities-catalog
logsource:
    category: process_creation
    product: windows
detection:
    # PowerShell 다운로드 크래들
    selection_powershell_download:
        Image|endswith: '\powershell.exe'
        CommandLine|contains:
            - 'IEX'
            - 'Invoke-Expression'
            - 'DownloadString'
            - 'Net.WebClient'
            - 'Start-BitsTransfer'
    
    # 의심스러운 스크립트 실행
    selection_suspicious_script:
        ParentImage|endswith:
            - '\outlook.exe'
            - '\winword.exe'
            - '\excel.exe'
        Image|endswith:
            - '\cmd.exe'
            - '\powershell.exe'
            - '\wscript.exe'
    
    # Shadow Copy 삭제 시도
    selection_vss_deletion:
        Image|endswith:
            - '\vssadmin.exe'
            - '\wmic.exe'
        CommandLine|contains:
            - 'delete'
            - 'shadowcopy'
            - 'shadows'
    
    # 백업 카탈로그 삭제
    selection_backup_deletion:
        Image|endswith: '\wbadmin.exe'
        CommandLine|contains: 'delete'
    
    # 방화벽 비활성화
    selection_firewall_disable:
        Image|endswith: '\netsh.exe'
        CommandLine|contains:
            - 'firewall'
            - 'advfirewall'
            - 'set'
            - 'off'
    
    condition: 1 of selection_*
level: high
tags:
    - attack.initial_access
    - attack.execution
    - attack.defense_evasion
    - attack.impact
falsepositives:
    - Legitimate admin activities
    - Software deployment tools
```

### 5.4 침해사고 대응 플레이북

```yaml
# 랜섬웨어 침해사고 대응 플레이북
ransomware_incident_response:
  
  phase_1_detection:
    name: "탐지 및 분석"
    duration: "0-2시간"
    actions:
      - "SIEM 알람 확인 및 분류"
      - "영향 범위 초기 평가"
      - "IOC 수집 시작"
      - "침해사고대응팀(CERT) 소집"
    checklist:
      - "[ ] 알람 트리거 조건 확인"
      - "[ ] 영향받은 시스템 목록 작성"
      - "[ ] 네트워크 로그 보존"
      - "[ ] 메모리 덤프 수집 (가능 시)"
      
  phase_2_containment:
    name: "격리 및 봉쇄"
    duration: "2-4시간"
    actions:
      - "감염 시스템 네트워크 격리"
      - "추가 확산 차단"
      - "백업 시스템 보호"
    checklist:
      - "[ ] 감염 시스템 VLAN 격리"
      - "[ ] 관리자 계정 패스워드 변경"
      - "[ ] 백업 서버 네트워크 분리"
      - "[ ] VPN 접근 일시 차단"
      
  phase_3_eradication:
    name: "제거"
    duration: "4-24시간"
    actions:
      - "악성코드 완전 제거"
      - "취약점 패치"
      - "침투 경로 차단"
    checklist:
      - "[ ] AV/EDR 전체 스캔"
      - "[ ] 악용된 취약점 패치"
      - "[ ] 탈취된 계정 비활성화"
      - "[ ] 백도어 확인 및 제거"
      
  phase_4_recovery:
    name: "복구"
    duration: "24-72시간"
    actions:
      - "백업에서 데이터 복구"
      - "시스템 재구축 (필요 시)"
      - "서비스 단계적 재개"
    checklist:
      - "[ ] 백업 무결성 검증"
      - "[ ] 깨끗한 환경에서 복구"
      - "[ ] 복구된 시스템 스캔"
      - "[ ] 서비스 정상 동작 확인"
      
  phase_5_lessons_learned:
    name: "사후 분석"
    duration: "복구 후 1-2주"
    actions:
      - "상세 보고서 작성"
      - "개선 사항 도출"
      - "정책/절차 업데이트"
    checklist:
      - "[ ] 타임라인 문서화"
      - "[ ] 근본 원인 분석(RCA)"
      - "[ ] 탐지 룰 개선"
      - "[ ] 훈련 프로그램 업데이트"
```

---

## 6. 실무 체크리스트

### 6.1 즉시 점검 필요 항목

- [ ] **SonicWall 패치 확인**: CVE-2024-40766 패치 적용 여부
- [ ] **VPN MFA 적용**: 모든 VPN 접근에 MFA 적용 여부
- [ ] **백업 검증**: 백업 복구 테스트 최근 수행 여부
- [ ] **EDR 업데이트**: 최신 탐지 룰 업데이트 여부
- [ ] **관리자 계정 검토**: 불필요한 관리자 계정 존재 여부

### 6.2 주간 점검 항목

- [ ] **SIEM 알람 검토**: 미처리 알람 및 오탐 분석
- [ ] **취약점 스캔**: CISA KEV 목록 취약점 스캔
- [ ] **접근 로그 검토**: 비정상 접근 패턴 확인
- [ ] **백업 상태 확인**: 백업 작업 성공 여부

### 6.3 월간 점검 항목

- [ ] **권한 검토**: 불필요한 권한 회수
- [ ] **패치 관리**: 누락된 보안 패치 식별
- [ ] **백업 복구 테스트**: 실제 복구 테스트 수행
- [ ] **위협 인텔리전스 업데이트**: 최신 IOC 반영

---

## 7. SK쉴더스 EQST 리소스 활용

### 7.1 KARA 보고서 시리즈

SK쉴더스 EQST에서 제공하는 랜섬웨어 관련 리소스:

| 시리즈 | 주기 | 내용 | 활용 방법 |
|--------|------|------|----------|
| **KARA 랜섬웨어 동향 보고서** | 분기별 | 글로벌 랜섬웨어 통계 및 그룹 분석 | 위협 인텔리전스 업데이트 |
| **Keep up with Ransomware** | 월별 | 특정 랜섬웨어 그룹 심층 분석 | IOC 및 탐지 룰 수집 |
| **Headline** | 월별 | 보안 트렌드 및 이슈 | 경영진 보고 자료 |
| **Special Report** | 월별 | 제로 트러스트 등 주제별 심층 분석 | 보안 아키텍처 참고 |

### 7.2 다운로드 링크

- [KARA 랜섬웨어 동향 보고서 2025 3Q](https://www.skshieldus.com/kor/media/newsletter/insight.do)
- [SK쉴더스 EQST insight 구독](https://www.skshieldus.com/kor/media/newsletter/insight.do)

---

## 결론

2025년 3분기 랜섬웨어 위협은 **생태계 분절화**, **새로운 협박 전술**, **AI 기반 공격**으로 더욱 복잡해지고 있습니다. 그러나 기업들의 랜섬 지불 거부율이 높아지고 있다는 점은 긍정적입니다.

**핵심 권고사항**:

1. **제로 트러스트** 아키텍처 단계적 도입
2. **3-2-1-1-0** 백업 전략 수립 및 정기 테스트
3. **CISA KEV** 취약점 우선 패치 프로세스 확립
4. **위협 인텔리전스** 구독 및 IOC 모니터링 자동화
5. **침해사고 대응 계획** 수립 및 테이블탑 훈련 실시

다음 포스팅에서는 제로 트러스트 보안 전략 중 **데이터 보안(Data Security)** 영역을 심층 분석하겠습니다.

---

## 참고 문헌

1. SK쉴더스. (2025). "KARA 랜섬웨어 동향 보고서 2025 3Q". [Link](https://www.skshieldus.com/kor/media/newsletter/insight.do)
2. GuidePoint GRIT. (2025). "Q3 2025 Ransomware and Cyber Threat Report". [Link](https://www.guidepointsecurity.com/resources/grit-q3-2025-ransomware-and-cyber-threat-report/)
3. Checkpoint. (2025). "The State of Ransomware Q3 2025". [Link](https://research.checkpoint.com/2025/the-state-of-ransomware-q3-2025/)
4. Flashpoint. (2025). "LockBit 5.0 Technical Deep Dive". [Link](https://flashpoint.io/blog/lockbit-5-0-analysis-technical-deep-dive-into-the-raas-giants-latest-upgrade/)
5. CISA. (2025). "Known Exploited Vulnerabilities Catalog". [Link](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
6. IC3. (2025). "Akira Ransomware Advisory". [Link](https://www.ic3.gov/CSA/2025/251113.pdf)
7. Mandiant. (2025). "Ransomware Defense Best Practices". [Link](https://www.mandiant.com/resources/reports)

---

> **면책 조항**: 본 포스팅은 SK쉴더스 EQST insight 및 공개된 위협 인텔리전스를 바탕으로 작성되었습니다. 정확한 최신 정보는 원본 보고서를 참조하시기 바랍니다.
