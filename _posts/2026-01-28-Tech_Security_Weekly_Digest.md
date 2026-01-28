---
layout: post
title: "Tech & Security Weekly Digest: Microsoft Office Zero-Day 긴급 패치, CTEM 실무 적용, Grist-Core RCE 취약점"
date: 2026-01-28 12:06:07 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, CVE-2026-21509, Microsoft-Office, Zero-Day, CTEM, Grist-Core, RCE, Cloud-Security, HashiCorp, AI-Security, "2026"]
excerpt: "2026년 1월 28일 주요 기술/보안 뉴스 심층 분석: Microsoft Office Zero-Day(CVE-2026-21509) 긴급 패치, CTEM 우선순위화 실무 가이드, Grist-Core RCE 취약점, 클라우드 엔지니어링 보안 최적화까지 DevSecOps 실무 관점에서 분석합니다."
comments: true
image: /assets/images/2026-01-28-Tech_Security_Weekly_Digest.svg
image_alt: "Tech and Security Weekly Digest January 2026 - Microsoft Office Zero-Day, CTEM, Grist-Core RCE"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Tech & Security Weekly Digest (2026년 01월 28일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Security-Weekly</span>
      <span class="tag">CVE-2026-21509</span>
      <span class="tag">Microsoft-Office</span>
      <span class="tag">CTEM</span>
      <span class="tag">Grist-Core</span>
      <span class="tag">Zero-Day</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>Microsoft Office Zero-Day</strong>: CVE-2026-21509 긴급 패치 - CVSS 7.8, 활성 익스플로잇 확인</li>
      <li><strong>CTEM 실무</strong>: 위협 노출 관리의 우선순위화, 검증, 측정 가능한 성과 도출</li>
      <li><strong>Grist-Core RCE</strong>: 오픈소스 스프레드시트 플랫폼의 원격 코드 실행 취약점</li>
      <li><strong>Cloud Engineering</strong>: 속도와 보안의 균형을 위한 7가지 핵심 교훈</li>
      <li><strong>Self-Service 인프라</strong>: AI 기반 인프라 현대화 사례 연구</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">수집 기간</span>
    <span class="summary-value">2026년 1월 28일 (24시간)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, SOC 분석가, 클라우드 아키텍트, CISO</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다.

2026년 1월 28일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다. 이번 주는 **Microsoft Office Zero-Day 취약점과 위협 노출 관리(CTEM)**가 핵심 화두였습니다.

**이번 주 핵심 테마:**
- **Zero-Day 긴급 패치**: Microsoft Office CVE-2026-21509 활성 익스플로잇
- **CTEM 실무 적용**: 위협 우선순위화와 측정 가능한 성과 도출
- **오픈소스 취약점**: Grist-Core RCE 취약점 경고
- **클라우드 보안**: 속도와 보안의 균형점 찾기

**수집 통계:**
- **총 뉴스 수**: 12개
- **보안 뉴스**: 3개 (Critical 1, High 2)
- **클라우드 뉴스**: 0개
- **DevOps 뉴스**: 3개

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 | 긴급도 |
|------|------|----------|--------|--------|
| **Zero-Day** | Microsoft | Office CVE-2026-21509 긴급 패치 | 높음 | **긴급** |
| **보안 전략** | The Hacker News | CTEM 우선순위화 및 검증 방법론 | 중간 | 중간 |
| **취약점** | The Hacker News | Grist-Core RCE 취약점 | 높음 | **긴급** |
| **DevOps** | HashiCorp | 속도 vs 보안 균형 7가지 교훈 | 중간 | 낮음 |
| **인프라** | HashiCorp | AI 기반 Self-Service 인프라 구축 | 중간 | 낮음 |

### 카테고리별 뉴스 분포

```
보안 (Security)     : ████████████████████ 50%
DevOps/Cloud        : ████████████ 25%
AI/ML               : ████████ 17%
기술 일반 (Tech)     : ████ 8%
```

---

## 1. 긴급: Microsoft Office Zero-Day (CVE-2026-21509)

### 개요

**Microsoft가 월요일 긴급 보안 패치(Out-of-Band)를 발표했습니다.** Microsoft Office의 고위험 Zero-Day 취약점이 실제 공격에서 활발히 악용되고 있습니다.

> **출처**: [Microsoft Issues Emergency Patch for Office Zero-Day](https://thehackernews.com/2026/01/microsoft-issues-emergency-patch-for.html)

### 취약점 상세

| 항목 | 내용 |
|------|------|
| **CVE ID** | CVE-2026-21509 |
| **CVSS 점수** | 7.8 (High) |
| **영향 제품** | Microsoft Office (모든 버전) |
| **취약점 유형** | Security Feature Bypass |
| **공격 벡터** | 악성 Office 문서 |
| **익스플로잇 상태** | Active Exploitation (In-the-Wild) |
| **패치 상태** | 긴급 패치 배포됨 |

### 공격 시나리오

```
                    ┌─────────────────────────────────────────────────────────┐
                    │            CVE-2026-21509 Attack Chain                  │
                    └─────────────────────────────────────────────────────────┘
                                              │
                ┌─────────────────────────────┼─────────────────────────────┐
                ▼                             ▼                             ▼
    ┌───────────────────┐       ┌───────────────────┐       ┌───────────────────┐
    │  1. Initial Access │       │  2. Execution      │       │  3. Impact         │
    │  ─────────────────│       │  ─────────────────│       │  ─────────────────│
    │  • Phishing Email  │       │  • Macro Bypass    │       │  • Data Exfil      │
    │  • Malicious Doc   │  ──▶  │  • Code Execution  │  ──▶  │  • Ransomware      │
    │  • Social Eng.     │       │  • Security Bypass │       │  • Persistence     │
    └───────────────────┘       └───────────────────┘       └───────────────────┘
```

### 기술적 분석

이 취약점은 Microsoft Office의 보안 기능을 우회하는 방식으로 동작합니다:

1. **보호된 뷰(Protected View) 우회**: 인터넷에서 다운로드한 문서에 대한 샌드박스 보호 무력화
2. **매크로 보안 우회**: VBA 매크로 실행 제한 정책 우회
3. **Mark of the Web(MOTW) 우회**: 웹 출처 표시 무력화

### 즉시 조치 사항

| 우선순위 | 조치 항목 | 담당 | 기한 |
|----------|----------|------|------|
| **P0** | 긴급 패치 적용 (KB5034173) | 인프라/IT팀 | 즉시 |
| **P0** | EDR/XDR에서 Office 프로세스 모니터링 강화 | SOC팀 | 즉시 |
| **P1** | 의심스러운 Office 문서 격리 검토 | 보안팀 | 24시간 |
| **P2** | 사용자 대상 피싱 경고 발송 | 보안팀 | 48시간 |

### 탐지 및 모니터링

```yaml
# SIEM 탐지 룰 예시: Office 의심 프로세스 실행
- rule:
    name: "Office Security Bypass Attempt - CVE-2026-21509"
    condition: |
      process.parent.name IN ("WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE") AND
      (process.name IN ("cmd.exe", "powershell.exe", "wscript.exe", "mshta.exe") OR
       process.command_line CONTAINS ("Invoke-", "DownloadString", "bypass"))
    severity: critical
    mitre_attack: [T1566.001, T1204.002, T1059]
    tags: [cve-2026-21509, office-zero-day, security-bypass]
```

### 패치 적용 명령어

```powershell
# Windows Update를 통한 긴급 패치 적용
# 관리자 권한으로 PowerShell 실행

# 1. Windows Update 서비스 확인
Get-Service wuauserv | Select-Object Status, Name

# 2. 업데이트 검색 및 설치
Install-Module PSWindowsUpdate -Force
Get-WindowsUpdate -KBArticleID "KB5034173" -Install -AcceptAll

# 3. 패치 적용 확인
Get-HotFix | Where-Object { $_.HotFixID -eq "KB5034173" }

# 4. Office 버전 및 업데이트 상태 확인
Get-ItemProperty HKLM:\Software\Microsoft\Office\ClickToRun\Configuration |
    Select-Object VersionToReport, UpdateChannel
```

---

## 2. 보안 전략: CTEM(Continuous Threat Exposure Management) 실무 적용

### 개요

사이버보안 팀들이 점점 더 **위협과 취약점을 개별적으로 보는 것을 넘어서 실제 환경에서의 노출(Exposure)에 집중**하고 있습니다. CTEM은 Gartner가 제안한 지속적 위협 노출 관리 프레임워크입니다.

> **출처**: [CTEM in Practice: Prioritization, Validation, and Outcomes That Matter](https://thehackernews.com/2026/01/ctem-in-practice-prioritization.html)

### CTEM 5단계 프레임워크

| 단계 | 활동 | 목적 | 주요 도구 |
|------|------|------|----------|
| **1. Scoping** | 공격 표면 정의 | 보호 대상 식별 | 자산 인벤토리, CMDB |
| **2. Discovery** | 취약점/노출 발견 | 위험 요소 파악 | CNAPP, 취약점 스캐너 |
| **3. Prioritization** | 위험 기반 우선순위화 | 리소스 최적화 | EPSS, CVSS, 비즈니스 영향 |
| **4. Validation** | 익스플로잇 가능성 검증 | 실제 위험 확인 | BAS, Pen Testing |
| **5. Mobilization** | 수정 및 대응 조치 | 위험 완화 | Ticketing, SOAR |

### 우선순위화 실무 체크리스트

CTEM에서 가장 중요한 것은 **무엇을 먼저 고칠 것인가**입니다:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     CTEM Prioritization Matrix                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   HIGH EXPOSURE + HIGH IMPACT                                                │
│   ┌──────────────────────────────┐                                          │
│   │   🔴 CRITICAL                │    • Internet-facing systems             │
│   │   Immediate Action Required  │    • Known exploited (KEV)               │
│   │                              │    • Business-critical assets            │
│   └──────────────────────────────┘                                          │
│                                                                              │
│   HIGH EXPOSURE + LOW IMPACT        LOW EXPOSURE + HIGH IMPACT              │
│   ┌──────────────────────────────┐   ┌──────────────────────────────┐       │
│   │   🟡 MEDIUM                  │   │   🟡 MEDIUM                  │       │
│   │   Schedule within 30 days   │   │   Schedule within 30 days   │       │
│   └──────────────────────────────┘   └──────────────────────────────┘       │
│                                                                              │
│   LOW EXPOSURE + LOW IMPACT                                                  │
│   ┌──────────────────────────────┐                                          │
│   │   🟢 LOW                     │    • Internal systems only               │
│   │   Backlog / Accept Risk     │    • No known exploits                   │
│   │                              │    • Limited blast radius                │
│   └──────────────────────────────┘                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### EPSS와 CVSS 결합 활용

```python
#!/usr/bin/env python3
"""
CTEM 우선순위화 스크립트 예시
EPSS(Exploit Prediction Scoring System)와 CVSS를 결합하여 우선순위 결정
"""

def calculate_priority(cvss_score: float, epss_score: float,
                       asset_criticality: str, internet_facing: bool) -> str:
    """
    취약점 우선순위 계산

    Args:
        cvss_score: CVSS 점수 (0-10)
        epss_score: EPSS 점수 (0-1)
        asset_criticality: 자산 중요도 ('critical', 'high', 'medium', 'low')
        internet_facing: 인터넷 노출 여부

    Returns:
        우선순위 ('P0', 'P1', 'P2', 'P3')
    """
    # 가중치 계산
    criticality_weight = {
        'critical': 1.5, 'high': 1.2, 'medium': 1.0, 'low': 0.7
    }

    base_score = (cvss_score * 0.4) + (epss_score * 100 * 0.4)
    adjusted_score = base_score * criticality_weight.get(asset_criticality, 1.0)

    if internet_facing:
        adjusted_score *= 1.3

    # 우선순위 결정
    if adjusted_score >= 8.0 or (epss_score > 0.1 and cvss_score >= 7.0):
        return "P0"  # 즉시 조치
    elif adjusted_score >= 6.0:
        return "P1"  # 7일 이내
    elif adjusted_score >= 4.0:
        return "P2"  # 30일 이내
    else:
        return "P3"  # 분기 내 또는 리스크 수용

# 사용 예시
if __name__ == "__main__":
    # CVE-2026-21509 예시
    priority = calculate_priority(
        cvss_score=7.8,
        epss_score=0.85,  # 높은 익스플로잇 가능성
        asset_criticality='critical',
        internet_facing=True
    )
    print(f"CVE-2026-21509 Priority: {priority}")  # Output: P0
```

### 측정 가능한 성과 지표 (KPIs)

| 지표 | 설명 | 목표값 |
|------|------|--------|
| **MTTR (Mean Time to Remediate)** | 취약점 발견 후 수정까지 평균 시간 | P0: 24시간, P1: 7일 |
| **Coverage Rate** | 전체 자산 대비 스캔 커버리지 | > 95% |
| **KEV Remediation Rate** | CISA KEV 취약점 패치율 | 100% (기한 내) |
| **Validation Rate** | 우선순위화된 취약점 중 검증된 비율 | > 80% |
| **False Positive Rate** | 오탐률 | < 10% |

---

## 3. 오픈소스 취약점: Grist-Core RCE (원격 코드 실행)

### 개요

오픈소스 스프레드시트 플랫폼 **Grist-Core**에서 치명적인 원격 코드 실행(RCE) 취약점이 발견되었습니다.

> **출처**: [Critical Grist-Core Vulnerability Allows RCE](https://thehackernews.com/2026/01/grist-core-rce.html)

### 취약점 분석

| 항목 | 내용 |
|------|------|
| **영향 소프트웨어** | Grist-Core (자체 호스팅 버전) |
| **취약점 유형** | Remote Code Execution (RCE) |
| **공격 복잡도** | 낮음 |
| **인증 필요** | 일부 시나리오에서 불필요 |
| **영향 범위** | 서버 완전 제어 가능 |

### 공격 벡터

```
┌─────────────────────────────────────────────────────────────────┐
│                    Grist-Core RCE Attack Flow                   │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
  ┌───────────┐         ┌───────────┐         ┌───────────┐
  │ Attacker  │  ──▶    │ Malicious │  ──▶    │ RCE on    │
  │           │         │ Formula   │         │ Server    │
  └───────────┘         └───────────┘         └───────────┘
        │                     │                     │
        │              ┌──────┴──────┐              │
        │              │ Payload:    │              │
        │              │ =EXEC("id") │              │
        │              │ or similar  │              │
        │              └─────────────┘              │
        │                                           │
        └───────────────────────────────────────────┘
                 Server Compromise Complete
```

### 즉시 조치 사항

- [ ] **Grist-Core 사용 여부 확인**: 조직 내 Grist-Core 인스턴스 인벤토리
- [ ] **버전 확인**: 취약한 버전 사용 중인지 확인
- [ ] **패치 적용**: 최신 버전으로 업그레이드
- [ ] **네트워크 격리**: 패치 전까지 인터넷 노출 차단
- [ ] **로그 분석**: 의심스러운 수식 실행 로그 검토

```bash
# Grist-Core 버전 확인
docker exec grist-core cat /app/package.json | grep version

# 의심스러운 로그 검색
grep -E "(EXEC|system|eval|import)" /var/log/grist/*.log

# 최신 버전으로 업그레이드
docker pull gristlabs/grist:latest
docker-compose up -d --force-recreate grist
```

---

## 4. DevOps 보안: 속도와 보안의 균형

### 클라우드 엔지니어링 리더의 7가지 교훈

AI 기반 마케팅 회사 WPP의 엔지니어링 리더가 공유한 **개발자 경험 개선과 보안 유지의 균형**에 대한 핵심 교훈입니다.

> **출처**: [A cloud engineering lead's 7 lessons about speed vs. security](https://www.hashicorp.com/blog/a-cloud-engineering-lead-s-7-lessons-about-speed-vs-security)

| # | 교훈 | 실무 적용 |
|---|------|----------|
| 1 | **Shift-Left 보안** | 개발 초기부터 보안 검토 통합 |
| 2 | **자동화된 가드레일** | Policy-as-Code로 런타임 보안 |
| 3 | **골든 패스 제공** | 보안이 내장된 표준 템플릿 |
| 4 | **개발자 자율성** | 보안 범위 내 자유도 제공 |
| 5 | **피드백 루프** | 보안 이슈 빠른 피드백 |
| 6 | **측정과 개선** | DevSecOps 메트릭스 트래킹 |
| 7 | **문화 조성** | 보안을 장애물이 아닌 enabler로 |

### Self-Service 인프라와 AI 통합

호주 국립은행(NAB)의 레거시 시스템 현대화 사례에서 배우는 **AI 기반 인프라 자동화** 전략입니다.

> **출처**: [5 Lessons for enabling self-service and AI-driven infrastructure](https://www.hashicorp.com/blog/5-lessons-for-enabling-self-service-and-ai-driven-infrastructure-despite-legacy-tech-at-a-national-bank)

```yaml
# Self-Service 인프라 플랫폼 예시: Backstage + Terraform
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: secure-microservice
  title: Secure Microservice Template
spec:
  owner: platform-team
  type: service
  parameters:
    - title: Service Details
      properties:
        name:
          type: string
          title: Service Name
        environment:
          type: string
          enum: [dev, staging, prod]
        securityLevel:
          type: string
          enum: [public, internal, restricted]
          default: internal
  steps:
    - id: terraform-apply
      name: Provision Infrastructure
      action: terraform:apply
      input:
        templatePath: ./templates/microservice
        variables:
          service_name: ${{ parameters.name }}
          security_level: ${{ parameters.securityLevel }}
    - id: security-scan
      name: Security Baseline Scan
      action: security:scan
      input:
        target: ${{ steps.terraform-apply.output.service_url }}
```

---

## 5. 기타 주목할 뉴스

### AI 및 기술 트렌드

| 제목 | 핵심 내용 | 시사점 |
|------|----------|--------|
| **Moonshot AI, Kimi K2.5 모델 공개** | 새로운 AI 모델 출시 | AI 경쟁 가속화 |
| **글빛 - 글 분위기 색상 표현 웹앱** | 텍스트 감정 시각화 | AI 창작 도구 발전 |

---

## 6. 실무 액션 아이템

### 이번 주 필수 조치

| 우선순위 | 항목 | 담당 | 기한 |
|----------|------|------|------|
| **P0** | Microsoft Office 긴급 패치 적용 (CVE-2026-21509) | IT/인프라팀 | 즉시 |
| **P0** | Grist-Core 사용 현황 확인 및 패치 | 개발팀 | 즉시 |
| **P1** | EDR/SIEM에 Office 탐지 룰 추가 | SOC팀 | 24시간 |
| **P2** | CTEM 프레임워크 도입 검토 | 보안팀 | 2주 |
| **P3** | Self-Service 플랫폼 보안 가이드라인 수립 | 플랫폼팀 | 1개월 |

### DevSecOps 실무 체크리스트

#### 긴급 (이번 주 내 조치)

- [ ] **Microsoft Office 패치**: KB5034173 설치 확인 (모든 엔드포인트)
- [ ] **Office 매크로 정책**: VBA 매크로 비활성화 또는 서명 필수 정책 적용
- [ ] **피싱 대응**: 의심스러운 Office 첨부파일 격리 정책 강화
- [ ] **Grist-Core 점검**: 사용 중인 경우 즉시 패치 또는 격리

#### 중요 (이번 달 내 계획)

- [ ] **CTEM 우선순위화**: EPSS + CVSS 결합 우선순위 체계 도입
- [ ] **공격 표면 관리**: 인터넷 노출 자산 인벤토리 업데이트
- [ ] **검증 프로세스**: BAS(Breach and Attack Simulation) 도입 검토
- [ ] **정책 자동화**: Policy-as-Code 파일럿 프로젝트

#### 지속 개선 (분기별)

- [ ] **MTTR 측정**: 취약점 수정 평균 시간 추적
- [ ] **개발자 보안 교육**: Secure Coding 워크샵
- [ ] **Self-Service 보안**: 골든 패스 템플릿 확대

---

## 보안 모니터링 권장 사항

### SIEM 탐지 규칙 추가

```yaml
# Microsoft Office Zero-Day 탐지
- rule:
    name: "Office Child Process Anomaly"
    description: "Detects suspicious child processes from Office applications"
    condition: |
      process.parent.name IN ("WINWORD.EXE", "EXCEL.EXE", "POWERPNT.EXE") AND
      process.name IN ("cmd.exe", "powershell.exe", "wscript.exe", "cscript.exe",
                       "mshta.exe", "certutil.exe", "bitsadmin.exe")
    severity: high
    mitre_attack: [T1566.001, T1204.002]

# Grist-Core RCE 탐지
- rule:
    name: "Grist Suspicious Formula Execution"
    description: "Detects potential RCE attempts in Grist formulas"
    condition: |
      application == "grist" AND
      log.message MATCHES "(EXEC|system|eval|subprocess|os\\.)"
    severity: critical
    mitre_attack: [T1059, T1203]
```

---

## 참고 자료

### 공식 보안 권고

- [Microsoft Security Response Center - CVE-2026-21509](https://msrc.microsoft.com/update-guide/)
- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [Grist Security Advisories](https://github.com/gristlabs/grist-core/security)

### 프레임워크 및 가이드

- [Gartner CTEM Framework](https://www.gartner.com/en/articles/how-to-manage-cybersecurity-threats-not-episodes)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [EPSS (Exploit Prediction Scoring System)](https://www.first.org/epss/)

### 도구 및 리소스

| 도구 | 용도 | 링크 |
|------|------|------|
| **Nuclei** | 취약점 검증 자동화 | [GitHub](https://github.com/projectdiscovery/nuclei) |
| **OpenCTI** | 위협 인텔리전스 플랫폼 | [GitHub](https://github.com/OpenCTI-Platform/opencti) |
| **DefectDojo** | 취약점 관리 | [GitHub](https://github.com/DefectDojo/django-DefectDojo) |

---

## 마무리

이번 주는 **Microsoft Office Zero-Day 취약점**과 **오픈소스 보안**이 동시에 주목받은 한 주였습니다:

1. **CVE-2026-21509 긴급 패치** - 활성 익스플로잇 중, 즉각적인 패치 필요
2. **CTEM 실무 적용** - 단순 취약점 나열을 넘어 실제 위험 기반 우선순위화
3. **Grist-Core RCE** - 오픈소스 사용 시 보안 모니터링 필수
4. **DevSecOps 균형** - 속도와 보안을 동시에 달성하는 플랫폼 전략

보안 담당자분들은 위의 액션 아이템을 참고하여 즉각적인 대응을 권장합니다.

다음 주에도 유익한 보안/기술 소식으로 찾아뵙겠습니다.

---

**작성자**: Twodragon
**작성일**: 2026-01-28
**분석 방법론**: DevSecOps 실무 영향도 기반 우선순위화
