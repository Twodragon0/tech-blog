---
author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-02-01 10:00:00 +0900
description: '2026년 2월 1일 보안 뉴스: AI 시스템이 OpenSSL 제로데이 12건을 모두 발견한 역사적 사건, OWASP Agentic
  AI 보안 프레임워크, Microsoft NIST 기반 AI 에이전트 거버넌스, Fortinet FortiCloud SSO 제로데이, Azure
  Resource Manager CVSS 9.9, Kyverno 인가 우회, eScan 공급망 공격'
excerpt: AISLE AI가 OpenSSL 제로데이 12건 전량 발견(역사적 최초), OWASP Agentic AI Top 10 프레임워크 발표,
  CVE-2026-24858 Fortinet FortiCloud SSO 인증 우회 제로데이 심층 분석
image: /assets/images/2026-02-01-Tech_Security_Weekly_Digest_AI_OpenSSL_Zero_Day_OWASP_Agentic_Fortinet.svg
image_alt: Security Digest - AI OpenSSL Zero-Day OWASP Agentic AI Fortinet Analysis
keywords:
- AISLE AI
- OpenSSL Zero-Day
- OWASP Agentic AI
- Fortinet CVE-2026-24858
- Azure CVE-2026-24304
- Kyverno CVE-2026-22039
- eScan Supply Chain
- NIST AI RMF
layout: post
schema_type: Article
tags:
- Security-Weekly
- DevSecOps
- AI-Security
- OpenSSL
- Zero-Day
- OWASP
- Agentic-AI
- Fortinet
- Azure
- Kyverno
- Supply-Chain
- eScan
- NIST
- '2026'
title: 'Tech & Security Weekly Digest: AI가 OpenSSL 제로데이 12건 발견, OWASP Agentic AI 프레임워크,
  Fortinet SSO 제로데이'
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Tech & Security Weekly Digest (2026년 02월 01일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AI-Security</span>
      <span class="tag">OpenSSL</span>
      <span class="tag">OWASP</span>
      <span class="tag">Agentic-AI</span>
      <span class="tag">Fortinet</span>
      <span class="tag">Azure</span>
      <span class="tag">Kyverno</span>
      <span class="tag">Supply-Chain</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AISLE AI OpenSSL 제로데이 12건 전량 발견</strong>: 역사상 최초로 AI 시스템이 인터넷 암호화 핵심 라이브러리의 모든 신규 취약점 발견</li>
      <li><strong>OWASP Agentic AI Top 10</strong>: 자율 AI 에이전트 애플리케이션 보안을 위한 공식 프레임워크 발표</li>
      <li><strong>CVE-2026-24858 Fortinet 제로데이</strong>: FortiCloud SSO 인증 우회로 FortiGate 방화벽 무단 접근, 실제 공격 확인</li>
      <li><strong>CVE-2026-24304 Azure RM CVSS 9.9</strong>: Azure Resource Manager 권한 상승, 전체 리소스 제어권 탈취 가능</li>
    </ul>
  </div>
</div>
</div>

## 경영진 요약 (Executive Summary)

### 위험도 스코어카드

| 위협 | 심각도 | 긴급도 | 비즈니스 영향 | 즉시 조치 필요 |
|------|--------|--------|--------------|--------------|
| **CVE-2026-24858 Fortinet SSO 제로데이** | Critical | 🔴 Urgent | 방화벽 완전 우회 → 네트워크 침투 | ✅ 즉시 패치 |
| **CVE-2026-24304 Azure RM (9.9)** | Critical | 🔴 Urgent | Azure 전체 리소스 탈취 가능 | ✅ 즉시 패치 |
| **CVE-2026-22039 Kyverno** | Critical | 🔴 Urgent | K8s 네임스페이스 격리 무력화 | ✅ 즉시 업그레이드 |
| **eScan 공급망 공격** | High | 🟡 Moderate | 안티바이러스 배포 채널 악용 | ✅ IoC 점검 |
| **AISLE AI 제로데이 발견** | Informational | 🟢 Strategic | AI 보안 연구 패러다임 전환 | 장기 대응 계획 |
| **OWASP Agentic AI Top 10** | High | 🟡 Moderate | AI 에이전트 공격 표면 확대 | 정책 수립 (1개월) |

### 3줄 요약

1. **긴급 패치 3건**: Fortinet, Azure, Kyverno 제로데이/중요 취약점이 실제 공격에 악용 중이거나 가능성이 높음
2. **AI 보안 원년**: AI가 OpenSSL 제로데이 12건을 전량 발견한 역사적 사건과 OWASP Agentic AI 프레임워크 발표로 AI 보안 시대 본격 개막
3. **공급망 위협 지속**: eScan 안티바이러스 업데이트 서버 침해 사례로 소프트웨어 공급망 보안의 중요성 재확인

---

## 개요

2026년 2월 첫째 주, 보안 업계에 역사적인 전환점이 찍혔습니다. **AI 보안 연구 시스템 AISLE이 OpenSSL에서 12건의 제로데이 취약점을 발견**한 것입니다. 인터넷 암호화의 근간인 OpenSSL에서 인간이 아닌 AI가 신규 취약점을 찾아낸 것은 사이버보안 분야에서 중요한 사건입니다.

동시에 **OWASP는 Agentic AI Top 10 프레임워크**를, **Microsoft는 NIST 기반 AI 에이전트 보안 거버넌스**를 발표하며 AI 에이전트 보안의 체계적 대응이 본격화되고 있습니다. 인프라 측면에서는 **Fortinet FortiCloud SSO 제로데이**(CVE-2026-24858), **Azure Resource Manager CVSS 9.9**(CVE-2026-24304), **Kyverno 인가 우회**(CVE-2026-22039) 등 긴급 패치가 필요한 취약점들이 잇따라 공개되었습니다.

---

## 1. AISLE AI, OpenSSL 제로데이 12건 전량 발견 (역사적 최초)

### 1.1 핵심 요약

| 항목 | 내용 |
|------|------|
| **발견 주체** | AISLE (AI Security Lab & Engineering) |
| **대상** | OpenSSL - 인터넷 암호화 핵심 라이브러리 |
| **발견 건수** | 12건 제로데이 (신규 취약점 전량) |
| **의미** | AI가 역사상 가장 많이 감사된 오픈소스 라이브러리에서 모든 신규 취약점 발견 |
| **발표일** | 2026년 1월 27일 |
| **출처** | [LessWrong - AISLE Research](https://www.lesswrong.com/posts/7aJwgbMEiKq5egQbd/ai-found-12-of-12-openssl-zero-days-while-curl-cancelled-its) |

### 1.2 왜 역사적인가?

OpenSSL은 **지구상에서 가장 많이 검토되고 감사된 암호화 라이브러리** 중 하나입니다. 전 세계 웹 트래픽의 대부분이 OpenSSL에 의존하고 있으며, 2014년 Heartbleed 이후 수천 명의 보안 연구원이 지속적으로 코드를 검토해왔습니다.

이런 라이브러리에서 AI가 **12건의 제로데이를 100% 발견**했다는 것은:

- **인간 보안 연구원이 놓친 취약점**을 AI가 체계적으로 찾아냄
- **코드 감사의 패러다임 전환**: 가장 많이 검토된 코드에서도 AI가 우위
- **방어적 AI 활용의 실질적 증명**: 이론이 아닌 실전에서 입증

### 1.3 curl 버그 바운티 취소와의 대조

흥미롭게도, 같은 시기에 **curl 프로젝트는 버그 바운티 프로그램을 취소**했습니다. 이유는 AI가 생성한 저품질 보안 보고서의 폭주(spam)로 인해 운영이 불가능해졌기 때문입니다.

| 비교 항목 | AISLE (OpenSSL) | AI Spam (curl) |
|-----------|-----------------|----------------|
| **AI 활용 방식** | 전문 보안 AI 시스템 | 범용 LLM의 무분별한 사용 |
| **결과** | 12건 실제 제로데이 발견 | 대량의 저품질 허위 보고서 |
| **영향** | 보안 강화 | 버그 바운티 프로그램 중단 |
| **교훈** | AI 보안 연구의 가능성 | AI 남용의 위험성 |

### 1.4 DevSecOps 관점 시사점

### 4.5 즉시 조치 사항

| 우선순위 | 조치 | 상세 |
|----------|------|------|
| **P0** | 패치 적용 | FortiOS 최신 버전으로 즉시 업데이트 |
| **P0** | SSO 로그 점검 | 비정상 인증 시도 확인 |
| **P1** | FortiCloud SSO 비활성화 | 패치 전까지 임시 비활성화 검토 |
| **P1** | 관리 접근 제한 | FortiGate 관리 인터페이스 IP 화이트리스트 |
| **P2** | IoC 점검 | Fortinet 발표 침해 지표 확인 |

---

---

## 5. CVE-2026-24304: Azure Resource Manager CVSS 9.9

### 5.1 MITRE ATT&CK 매핑

| MITRE 기법 | 설명 | 적용 단계 |
|-----------|------|----------|
| **T1078.004** - Cloud Accounts | 낮은 권한 Azure 계정을 통한 초기 접근 | 초기 접근 |
| **T1068** - Exploitation for Privilege Escalation | Azure RM 취약점 익스플로잇으로 권한 상승 | 권한 상승 |
| **T1098.001** - Additional Cloud Credentials | 추가 관리자 계정 생성 및 권한 부여 | 지속성 확보 |
| **T1530** - Data from Cloud Storage Object | Azure Storage Account 데이터 탈취 | 데이터 수집 |
| **T1485** - Data Destruction | Azure 리소스 삭제/변조 | 영향 |
| **T1496** - Resource Hijacking | 크립토마이닝 위한 VM 리소스 탈취 | 영향 |

### 5.2 취약점 요약

| 항목 | 내용 |
|------|------|
| **CVE** | CVE-2026-24304 |
| **CVSS** | 9.9/10 (Critical) |
| **영향** | Azure Resource Manager |
| **공격 벡터** | 네트워크 (인증된 낮은 권한 사용자) |
| **영향 범위** | 기밀성, 무결성, 가용성 전체 |

### 5.3 공격 흐름도


### 6.3 즉시 조치

#### Elasticsearch (ELK)

> ```json
> {...
> ```


### 12.4 eScan 공급망 공격 헌팅

**헌팅 목표**: eScan 업데이트 서버에서 다운로드된 악성 파일 실행 탐지

#### Windows Security Event Log (Splunk)

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상) -->
{% endraw %}

#### Azure Sentinel KQL (Windows Events)

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상) -->
{% endraw %}

---

## 13. 참고 자료 (References)

### 13.1 AI 보안 및 연구

| 제목 | 발행처 | URL | 발행일 |
|------|--------|-----|--------|
| AI Found 12 of 12 OpenSSL Zero-Days | AISLE Research (LessWrong) | [LessWrong Post](https://www.lesswrong.com/posts/7aJwgbMEiKq5egQbd/ai-found-12-of-12-openssl-zero-days-while-curl-cancelled-its) | 2026-01-27 |
| OWASP Top 10 for Agentic AI Applications 2026 | OWASP GenAI Security Project | [OWASP GenAI](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) | 2026-01 |
| Architecting Trust: NIST-Based AI Agent Security Framework | Microsoft Defender for Cloud | [Microsoft Tech Community](https://techcommunity.microsoft.com/blog/microsoftdefendercloudblog/architecting-trust-a-nist-based-security-governance-framework-for-ai-agents/4490556) | 2026-01-30 |
| 2026 Agentic AI Attack Surface Poster Child | Dark Reading | [Dark Reading](https://www.darkreading.com/threat-intelligence/2026-agentic-ai-attack-surface-poster-child) | 2026-01 |
| NIST AI Risk Management Framework (AI RMF) | NIST | [NIST AI RMF](https://www.nist.gov/itl/ai-risk-management-framework) | 2023 |
| World Economic Forum Global Cybersecurity Outlook 2026 | WEF | [Forbes Coverage](https://www.forbes.com/sites/guneyyildiz/2026/01/22/the-ai-security-wake-up-call-ceos-didnt-budget-for--what-davos-2026-data-reveals/) | 2026-01 |

### 13.2 CVE 및 취약점 공개

| CVE ID | 영향 제품 | 심각도 | 공개일 | 출처 |
|--------|----------|--------|--------|------|
| CVE-2026-24858 | Fortinet FortiOS (FortiCloud SSO) | Critical | 2026-01-28 | [eSentire Advisory](https://www.esentire.com/security-advisories/confirmed-zero-day-vulnerability-in-fortinet-products-cve-2026-24858) |
| CVE-2026-24304 | Azure Resource Manager | 9.9 Critical | 2026-01 | [Microsoft Security Response Center](https://msrc.microsoft.com/update-guide/) |
| CVE-2026-22039 | Kyverno < 1.16.3 | Critical | 2026-01 | [GitHub Security Advisory](https://github.com/kyverno/kyverno) |
| CVE-2026-24835 | Podman Desktop < 1.25.1 | Critical | 2026-01 | [Podman Desktop GitHub](https://github.com/podman-desktop/podman-desktop) |
| CVE-2026-24905 | Inspektor Gadget < 0.48.1 | High | 2026-01 | [Inspektor Gadget Advisory](https://github.com/inspektor-gadget/inspektor-gadget) |
| CVE-2026-24740 | Dozzle | High | 2026-01 | [Dozzle GitHub](https://github.com/amir20/dozzle) |
| CVE-2026-20045 | Cisco Unified Communications Manager | Critical | 2026-01 | [Cisco Security Advisory](https://sec.cloudapps.cisco.com/security/center/publicationListing.x) |
| CVE-2025-31133 | runc < 1.1.14 | High | 2025-12 | [runc GitHub](https://github.com/opencontainers/runc) |

### 13.3 공급망 보안 사건

| 사건 | 피해 기업 | 공격 유형 | 발견일 | 출처 |
|------|----------|----------|--------|------|
| eScan 업데이트 서버 침해 | MicroWorld Technologies | 악성 서명 업데이트 배포 | 2026-01-22 | [BleepingComputer](https://www.bleepingcomputer.com/news/security/escan-confirms-update-server-breached-to-push-malicious-update/) |
| curl 버그 바운티 프로그램 중단 | curl Project | AI 생성 허위 보고서 스팸 | 2026-01 | [curl Announcement](https://daniel.haxx.se/blog/) |

### 13.4 규제 및 컴플라이언스

| 규제/가이드 | 발행 기관 | 시행일 | 출처 |
|------------|----------|--------|------|
| EU AI Act (Artificial Intelligence Act) | European Union | 2026-08-02 | [Orrick Law Firm Guide](https://www.orrick.com/en/Insights/2025/11/The-EU-AI-Act-6-Steps-to-Take-Before-2-August-2026) |
| NIST Cybersecurity Framework (CSF) 2.0 | NIST | 2024-02 | [NIST CSF](https://www.nist.gov/cyberframework) |
| OWASP Top 10 for LLM Applications | OWASP | 2023 | [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |
| CISA Known Exploited Vulnerabilities Catalog | CISA | 지속 업데이트 | [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |

### 13.5 한국 보안 기관 및 가이드

| 기관/가이드 | 발행처 | 관련 주제 | 출처 |
|-----------|--------|----------|------|
| 한국인터넷진흥원(KISA) 보안공지 | KISA | 긴급 보안 업데이트 | [KISA 보안공지](https://www.kisa.or.kr/2060204) |
| 금융보안원(FSI) 보안 가이드 | 금융보안원 | 금융권 보안 기준 | [FSI](https://www.fsec.or.kr/) |
| 행정안전부 정보보호 지침 | 행정안전부 | 공공기관 보안 | [행안부](https://www.mois.go.kr/) |
| K-ISMS-P 인증 기준 | KISA | 정보보호 인증 | [K-ISMS](https://isms.kisa.or.kr/) |
| 개인정보보호위원회 가이드 | 개인정보보호위원회 | 개인정보 보호법 | [개인정보위](https://www.pipc.go.kr/) |
| 클라우드 컴퓨팅 보안인증(CSAP) | KISA | 클라우드 보안 | [CSAP](https://www.kisa.or.kr/1051) |

### 13.6 MITRE ATT&CK 프레임워크

| MITRE 기법 | 설명 | 적용 CVE | URL |
|-----------|------|---------|-----|
| T1190 | Exploit Public-Facing Application | CVE-2026-24858 (Fortinet) | [MITRE T1190](https://attack.mitre.org/techniques/T1190/) |
| T1078.004 | Valid Accounts: Cloud Accounts | CVE-2026-24304 (Azure) | [MITRE T1078.004](https://attack.mitre.org/techniques/T1078/004/) |
| T1068 | Exploitation for Privilege Escalation | CVE-2026-24304, CVE-2026-22039 | [MITRE T1068](https://attack.mitre.org/techniques/T1068/) |
| T1098 | Account Manipulation | CVE-2026-24858 | [MITRE T1098](https://attack.mitre.org/techniques/T1098/) |
| T1098.001 | Additional Cloud Credentials | CVE-2026-24304 | [MITRE T1098.001](https://attack.mitre.org/techniques/T1098/001/) |
| T1530 | Data from Cloud Storage Object | CVE-2026-24304 | [MITRE T1530](https://attack.mitre.org/techniques/T1530/) |
| T1562.004 | Disable or Modify System Firewall | CVE-2026-24858 | [MITRE T1562.004](https://attack.mitre.org/techniques/T1562/004/) |
| T1021.004 | Remote Services: SSH | CVE-2026-24858 | [MITRE T1021.004](https://attack.mitre.org/techniques/T1021/004/) |
| T1018 | Remote System Discovery | CVE-2026-24858 | [MITRE T1018](https://attack.mitre.org/techniques/T1018/) |
| T1485 | Data Destruction | CVE-2026-24304 | [MITRE T1485](https://attack.mitre.org/techniques/T1485/) |
| T1496 | Resource Hijacking | CVE-2026-24304 | [MITRE T1496](https://attack.mitre.org/techniques/T1496/) |

### 13.7 추가 보안 리소스

| 리소스 | 제공처 | 용도 | URL |
|--------|--------|------|-----|
| Splunk Security Content | Splunk | SIEM 탐지 규칙 | [Splunk Security Content](https://research.splunk.com/) |
| Azure Sentinel Content Hub | Microsoft | Azure 탐지 규칙 | [Sentinel Content Hub](https://learn.microsoft.com/en-us/azure/sentinel/) |
| Sigma Rules | Sigma HQ | 플랫폼 독립적 탐지 규칙 | [Sigma Rules](https://github.com/SigmaHQ/sigma) |
| Atomic Red Team | Red Canary | 공격 시뮬레이션 테스트 | [Atomic Red Team](https://atomicredteam.io/) |
| CIS Benchmarks | Center for Internet Security | 보안 설정 기준 | [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) |

---

*이 글은 [Twodragon's Tech Blog](https://tech.2twodragon.com)에서 매주 발행하는 Tech & Security Weekly Digest입니다. 최신 보안 뉴스와 실무 가이드를 매주 받아보세요.*
