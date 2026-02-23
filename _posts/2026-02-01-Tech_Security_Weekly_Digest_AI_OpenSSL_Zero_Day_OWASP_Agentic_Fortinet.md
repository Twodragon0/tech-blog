---
layout: post
title: "기술 & 보안 주간 다이제스트: AI가 OpenSSL 제로데이 12건 발견, OWASP Agentic AI 프레임워크, Fortinet SSO 제로데이"
date: 2026-02-01 10:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, AI-Security, OpenSSL, Zero-Day, OWASP, Agentic-AI, Fortinet, Azure, Kyverno, Supply-Chain, eScan, NIST, "2026"]
excerpt: "AISLE AI가 OpenSSL 제로데이 12건 전량 발견(역사적 최초), OWASP Agentic AI Top 10 프레임워크 발표, CVE-2026-24858 Fortinet FortiCloud SSO 인증 우회 제로데이 심층 분석"
description: "2026년 2월 1일 보안 뉴스: AI 시스템이 OpenSSL 제로데이 12건을 모두 발견한 역사적 사건, OWASP Agentic AI 보안 프레임워크, Microsoft NIST 기반 AI 에이전트 거버넌스, Fortinet FortiCloud SSO 제로데이, Azure Resource Manager CVSS 9.9, Kyverno 인가 우회, eScan 공급망 공격"
keywords: [AISLE AI, OpenSSL Zero-Day, OWASP Agentic AI, Fortinet CVE-2026-24858, Azure CVE-2026-24304, Kyverno CVE-2026-22039, eScan Supply Chain, NIST AI RMF]
author: Twodragon
comments: true
image: /assets/images/2026-02-01-Tech_Security_Weekly_Digest_AI_OpenSSL_Zero_Day_OWASP_Agentic_Fortinet.svg
image_alt: "보안 다이제스트 - AI OpenSSL Zero-Day OWASP Agentic AI Fortinet 분석"
toc: true
schema_type: Article
---

## 📋 포스팅 요약

> **제목**: 기술 & 보안 주간 다이제스트: AI가 OpenSSL 제로데이 12건 발견, OWASP Agentic AI 프레임워크, Fortinet SSO 제로데이

> **카테고리**: security, devsecops

> **태그**: Security-Weekly, DevSecOps, AI-Security, OpenSSL, Zero-Day, OWASP, Agentic-AI, Fortinet, Azure, Kyverno, Supply-Chain, eScan, NIST, "2026"

> **핵심 내용**: 
> - AISLE AI가 OpenSSL 제로데이 12건 전량 발견(역사적 최초), OWASP Agentic AI Top 10 프레임워크 발표, CVE-2026-24858 Fortinet FortiCloud SSO 인증 우회 제로데이 심층 분석

> **주요 기술/도구**: Security, DevSecOps, Security, security, devsecops

> **대상 독자**: 기업 보안 담당자, 보안 엔지니어, CISO

> ---

> *이 포스팅은 AI(Cursor, Claude 등)가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.*


<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">기술 & 보안 주간 다이제스트 (2026년 02월 01일)</span>
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

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # AI 기반 보안 감사 파이프라인 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # AI 기반 보안 감사 파이프라인 예시...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# AI 기반 보안 감사 파이프라인 예시
security-audit:
  stage: test
  tools:
    - name: ai-code-review
      type: SAST
      config:
        model: security-specialized  # 범용 LLM이 아닌 보안 특화 모델
        scope: cryptographic-libraries
        depth: deep-analysis
    - name: traditional-sast
      type: SAST  # AI와 기존 도구 병행
  rules:
    - if: $CI_MERGE_REQUEST_ID
      when: always
    - if: $CI_COMMIT_BRANCH == "main"
      when: always


```
-->
-->

> **핵심 교훈**: AI 보안 도구는 "보안 특화 AI"와 "범용 LLM의 무분별한 사용"을 명확히 구분해야 합니다. AISLE의 성공은 목적에 맞게 설계된 AI 시스템의 가치를 증명합니다.

---

## 2. OWASP Agentic AI Top 10 프레임워크 (2026)

### 2.1 핵심 요약

| 항목 | 내용 |
|------|------|
| **발표** | OWASP GenAI Security Project |
| **대상** | 자율 AI 에이전트 애플리케이션 |
| **구성** | Top 10 보안 위험 + 거버넌스 체크리스트 + 레드팀 가이드 |
| **출처** | [OWASP Agentic AI](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) |

### 2.2 Agentic AI가 기존 LLM과 다른 이유

기존 LLM은 **질문에 답변**하는 수동적 도구였지만, Agentic AI는:

| 특성 | 기존 LLM | Agentic AI |
|------|----------|------------|
| **동작 방식** | 프롬프트 → 응답 | 목표 설정 → 자율 실행 |
| **시스템 접근** | 없음 (텍스트만) | API, DB, 파일시스템, 네트워크 |
| **의사결정** | 인간이 판단 | 에이전트가 자율 판단 |
| **지속성** | 단일 세션 | 다중 세션, 메모리 유지 |
| **공격 표면** | 프롬프트 인젝션 | 프롬프트 인젝션 + 시스템 접근 + 자율 실행 |

### 2.3 OWASP Agentic AI Top 10 주요 위협

1. **Excessive Agency** - 에이전트에게 과도한 권한 부여
2. **Indirect Prompt Injection** - 이메일, 문서, 웹페이지를 통한 간접 프롬프트 주입
3. **Insecure Tool Use** - 안전하지 않은 외부 도구 호출
4. **Uncontrolled Autonomous Actions** - 통제 불가능한 자율 행동
5. **Memory Poisoning** - 에이전트 메모리/컨텍스트 오염
6. **Inadequate Sandboxing** - 불충분한 격리 환경
7. **Trust Boundary Violations** - 신뢰 경계 위반
8. **Data Exfiltration via Agent** - 에이전트를 통한 데이터 유출
9. **Supply Chain Compromise** - 에이전트 도구/플러그인 공급망 공격
10. **Insufficient Monitoring** - 에이전트 행동 모니터링 부재

### 2.4 실무 적용 체크리스트

- [ ] AI 에이전트에 **최소 권한 원칙** 적용 (Excessive Agency 방지)
- [ ] 외부 입력(이메일, 문서)에 대한 **간접 프롬프트 인젝션 필터링** 구현
- [ ] 에이전트가 호출하는 **모든 도구/API에 입력 검증** 적용
- [ ] **Human-in-the-Loop**: 고위험 작업에 인간 승인 프로세스 필수
- [ ] 에이전트 실행 **샌드박스 환경** 구성 (네트워크, 파일시스템 격리)
- [ ] **에이전트 행동 로그** 전량 기록 및 이상 탐지 설정
- [ ] 에이전트 메모리/컨텍스트 **무결성 검증** 메커니즘 구현
- [ ] 도구/플러그인 **공급망 보안** 검증 프로세스 수립

---

## 3. Microsoft NIST 기반 AI 에이전트 보안 거버넌스

### 3.1 핵심 요약

| 항목 | 내용 |
|------|------|
| **발표** | Microsoft Defender for Cloud Blog |
| **프레임워크** | NIST AI Risk Management Framework (AI RMF) 기반 |
| **대상** | AI 에이전트를 배포하는 기업 |
| **발표일** | 2026년 1월 30일 |
| **출처** | [Microsoft Tech Community](https://techcommunity.microsoft.com/blog/microsoftdefendercloudblog/architecting-trust-a-nist-based-security-governance-framework-for-ai-agents/4490556) |

### 3.2 핵심 거버넌스 영역

Microsoft가 제시하는 AI 에이전트 보안 거버넌스는 **4개 핵심 기능**으로 구성됩니다:

| NIST 기능 | AI 에이전트 적용 | 실무 활동 |
|-----------|-----------------|-----------|
| **GOVERN** | AI 거버넌스 정책 | 에이전트 배포 승인 프로세스, 위험 평가 기준 |
| **MAP** | 위험 식별 | 에이전트 접근 범위, 데이터 흐름, 의사결정 경로 매핑 |
| **MEASURE** | 위험 측정 | 에이전트 행동 모니터링, 성능 메트릭, 편향성 평가 |
| **MANAGE** | 위험 대응 | 에이전트 차단/롤백, 인시던트 대응, 지속 개선 |

### 3.3 WEF 통계와의 연계

World Economic Forum의 **Global Cybersecurity Outlook 2026**에 따르면:

- **87%** 의 사이버보안 리더가 AI 취약점을 **가장 빠르게 증가하는 위험**으로 인식
- 비인간 에이전트 ID는 2026년 말까지 **450억 개 초과** 예상 (인간 노동력의 12배)
- 전략적 AI 에이전트 거버넌스를 갖춘 기업은 **10%에 불과**

---

## 4. CVE-2026-24858: Fortinet FortiCloud SSO 제로데이

### 4.1 취약점 요약

| 항목 | 내용 |
|------|------|
| **CVE** | CVE-2026-24858 |
| **영향 제품** | FortiOS - FortiCloud SSO 기능 |
| **심각도** | Critical |
| **공격 유형** | 인증 우회 (Authentication Bypass) |
| **상태** | 실제 공격 확인 (Actively Exploited) |
| **패치일** | 2026년 1월 28일 |
| **출처** | [eSentire Security Advisory](https://www.esentire.com/security-advisories/confirmed-zero-day-vulnerability-in-fortinet-products-cve-2026-24858) |

### 4.2 MITRE ATT&CK 매핑

| MITRE 기법 | 설명 | 적용 단계 |
|-----------|------|----------|
| **T1190** - Exploit Public-Facing Application | FortiCloud SSO 인증 우회 익스플로잇 | 초기 침투 |
| **T1078.004** - Cloud Accounts | SSO 우회를 통한 클라우드 계정 탈취 | 지속성 확보 |
| **T1098** - Account Manipulation | FortiGate 관리자 계정 생성/권한 상승 | 권한 상승 |
| **T1562.004** - Disable or Modify System Firewall | 방화벽 규칙 수정/무력화 | 방어 회피 |
| **T1021.004** - SSH | VPN/SSH를 통한 내부 네트워크 접근 | 횡적 이동 |
| **T1018** - Remote System Discovery | 내부 네트워크 정찰 및 자산 발견 | 정찰 |

### 4.3 공격 흐름도 (Attack Flow)

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```text
┌──────────────────────────────────────────────────────────────┐
│                    CVE-2026-24858 공격 체인                   │
└──────────────────────────────────────────────────────────────┘

[1] 초기 접근 (Initial Access)
    │
    ├─> 공격자가 FortiCloud SSO 엔드포인트 탐지
    │   URL: https://[target].forticloud.com/sso
    │
    └─> T1190: 공개 웹 애플리케이션 익스플로잇
        │
        ▼
[2] 인증 우회 (Authentication Bypass)
    │
    ├─> 인증 토큰 검증 로직 우회
    │   (세부 기술적 내용은 Fortinet 비공개)
    │
    └─> FortiGate 관리 세션 획득
        │
        ▼
[3] 권한 상승 (Privilege Escalation)
    │
    ├─> T1098: 새로운 관리자 계정 생성
    │   또는 기존 계정 권한 상승
    │
    └─> 완전한 방화벽 제어권 획득
        │
        ▼
[4] 방어 무력화 (Defense Evasion)
    │
    ├─> T1562.004: 방화벽 규칙 수정
    │   - 악성 IP 허용 규칙 추가
    │   - 로깅 비활성화
    │   - IPS/IDS 우회 규칙 생성
    │
    └─> VPN 접근 권한 설정
        │
        ▼
[5] 횡적 이동 (Lateral Movement)
    │
    ├─> T1021.004: VPN/SSH로 내부 네트워크 침투
    │
    └─> T1018: 내부 시스템 스캐닝 및 정찰
        │
        ▼
[6] 목표 달성 (Impact)
    │
    ├─> 민감 데이터 유출 (C2 서버로 전송)
    ├─> 랜섬웨어 배포
    └─> 지속 공격 인프라 구축


```
-->
-->

### 4.4 공격 시나리오

```text
1. 공격자 → FortiCloud SSO 엔드포인트 접근
2. 인증 우회 취약점 악용 → FortiGate 관리 세션 획득
3. 방화벽 설정 변경/VPN 접근/네트워크 정찰
4. 내부 네트워크 횡이동 → 추가 공격
```

<!-- SIEM Detection Queries (Security Operations Reference)

### Splunk SPL - Fortinet FortiCloud SSO 이상 인증 탐지

```spl
index=fortigate sourcetype=fortigate_log
(action=authfailure OR action=authsuccess)
| eval auth_method=if(like(msg, "%SSO%"), "SSO", "Local")
| where auth_method="SSO"
| stats count by src_ip, user, auth_method, action
| where count > 5
| table _time, src_ip, user, auth_method, action, count
| sort -count
```

### Azure Sentinel KQL - FortiCloud SSO 이상 접근 패턴

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
CommonSecurityLog
| where DeviceVendor == "Fortinet"
| where DeviceProduct startswith "FortiGate"
| where Activity contains "sso" or Activity contains "authentication"
| where DeviceAction in ("authfailure", "authsuccess")
| extend SourceIP = coalesce(SourceIP, SourceAddress)
| summarize
    FailedAttempts = countif(DeviceAction == "authfailure"),
    SuccessfulLogins = countif(DeviceAction == "authsuccess"),
    UniqueUsers = dcount(DestinationUserName)
    by SourceIP, bin(TimeGenerated, 5m)
| where FailedAttempts > 5 or (FailedAttempts > 3 and SuccessfulLogins > 0)
| project TimeGenerated, SourceIP, FailedAttempts, SuccessfulLogins, UniqueUsers
| order by FailedAttempts desc


```
-->
-->

### Elasticsearch (ELK) - FortiCloud SSO 공격 탐지

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "query": {
    "bool": {
      "must": [
        {"match": {"vendor": "Fortinet"}},
        {"match": {"event.action": "authentication"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "aggs": {
    "suspicious_ips": {
      "terms": {
        "field": "source.ip",
        "size": 100
      },
      "aggs": {
        "failed_auth": {
          "filter": {"term": {"event.outcome": "failure"}},
          "aggs": {
            "count": {"value_count": {"field": "event.action"}}
          }
        },
        "success_after_failure": {
          "bucket_selector": {
            "buckets_path": {"failed": "failed_auth>count"},
            "script": "params.failed > 5"
          }
        }
      }
    }
  }
}


```
-->
-->

-->

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

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```text
┌──────────────────────────────────────────────────────────────┐
│              CVE-2026-24304 Azure RM 권한 상승 체인            │
└──────────────────────────────────────────────────────────────┘

[1] 초기 접근 (Initial Access)
    │
    ├─> 공격자가 낮은 권한 Azure 계정 확보
    │   (예: Reader 권한만 가진 계정)
    │
    └─> T1078.004: 정상 클라우드 계정 사용
        │
        ▼
[2] 취약점 탐색 (Discovery)
    │
    ├─> Azure Resource Manager API 엔드포인트 호출
    │   https://management.azure.com/...
    │
    └─> 권한 상승 가능한 API 경로 식별
        │
        ▼
[3] 권한 상승 (Privilege Escalation) - T1068
    │
    ├─> CVE-2026-24304 익스플로잇 실행
    │   - ARM API 검증 로직 우회
    │   - 낮은 권한으로 고권한 작업 수행
    │
    └─> Owner/Contributor 역할 획득
        │
        ▼
[4] 지속성 확보 (Persistence)
    │
    ├─> T1098.001: 추가 관리자 계정 생성
    │   - Service Principal 생성
    │   - Managed Identity 권한 부여
    │
    └─> 백도어 계정으로 지속 접근 확보
        │
        ▼
[5] 리소스 탈취/조작 (Collection & Impact)
    │
    ├─> T1530: Azure Storage Account 데이터 다운로드
    ├─> T1496: VM 크립토마이닝 배포
    ├─> T1485: 중요 리소스 삭제 (랜섬 협박)
    └─> 네트워크 설정 변경 (방화벽 규칙, NSG)
        │
        ▼
[6] 탐지 회피 (Defense Evasion)
    │
    ├─> Activity Log 비활성화
    ├─> Defender for Cloud 비활성화
    └─> 감사 로그 삭제/변조


```
-->
-->

<!-- SIEM Detection Queries - Azure Resource Manager 권한 상승 탐지

### Azure Sentinel KQL - 의심스러운 권한 상승 활동

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
AzureActivity
| where OperationNameValue in (
    "Microsoft.Authorization/roleAssignments/write",
    "Microsoft.Authorization/permissions/write"
)
| where ActivityStatusValue == "Success"
| extend Caller = Caller, Resource = ResourceId
| join kind=leftouter (
    AzureActivity
    | where TimeGenerated > ago(7d)
    | summarize PreviousRoleCount = count() by Caller
) on Caller
| where PreviousRoleCount < 5 or isempty(PreviousRoleCount)
| project TimeGenerated, Caller, OperationNameValue, Resource, ActivityStatusValue
| order by TimeGenerated desc


```
-->
-->
{% endraw %}

### Splunk SPL - Azure 비정상 역할 할당 탐지

{% raw %}
```spl
index=azure sourcetype=azure:activity
operationName="Microsoft.Authorization/roleAssignments/write"
| eval role_definition=spath(_raw, "properties.roleDefinitionId")
| eval principal_id=spath(_raw, "properties.principalId")
| eval caller=spath(_raw, "caller")
| where like(role_definition, "%Owner%") OR like(role_definition, "%Contributor%")
| stats count by _time, caller, principal_id, role_definition
| where count > 3
| table _time, caller, principal_id, role_definition, count
```
{% endraw %}

### Azure Log Analytics - 높은 권한 작업 이상 패턴

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
AzureActivity
| where CategoryValue == "Administrative"
| where OperationNameValue has_any (
    "delete", "write", "action"
)
| summarize
    Operations = count(),
    UniqueResources = dcount(ResourceId),
    OperationTypes = make_set(OperationNameValue)
    by Caller, bin(TimeGenerated, 5m)
| where Operations > 20 or UniqueResources > 10
| project TimeGenerated, Caller, Operations, UniqueResources, OperationTypes
| order by Operations desc


```
-->
-->
{% endraw %}

-->

### 5.4 CVSS 벡터 분석

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```text
CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H

AV:N  → 네트워크를 통한 원격 공격 가능
AC:L  → 공격 복잡도 낮음
PR:L  → 낮은 권한만 필요 (일반 사용자)
UI:N  → 사용자 상호작용 불필요
S:C   → 범위 변경 (다른 리소스에 영향)
C:H   → 기밀성 완전 침해
I:H   → 무결성 완전 침해
A:H   → 가용성 완전 침해


```
-->
-->

### 5.5 Azure 사용자 즉시 조치

- [ ] Microsoft 2026년 1월 보안 패치 즉시 적용
- [ ] **최소 권한 IAM 정책** 재검토 및 강화
- [ ] Azure AD **Conditional Access** 활성화
- [ ] **Azure Activity Log** 에서 비정상 권한 상승 탐지 규칙 설정
- [ ] **Privileged Identity Management (PIM)** 으로 Just-In-Time 접근 구현

---

## 6. CVE-2026-22039: Kyverno 인가 우회 (Kubernetes)

### 6.1 취약점 요약

| 항목 | 내용 |
|------|------|
| **CVE** | CVE-2026-22039 |
| **심각도** | Critical |
| **영향 버전** | Kyverno < 1.16.3, < 1.15.3 |
| **공격 유형** | Authorization Boundary Bypass |

### 6.2 공격 원리

Kyverno의 `isAccessAllowed()` 함수에서 네임스페이스 격리가 제대로 적용되지 않아, **네임스페이스 간 데이터 접근과 권한 상승**이 가능합니다.

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 취약한 시나리오: 네임스페이스 격리 우회...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 취약한 시나리오: 네임스페이스 격리 우회...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```yaml
# 취약한 시나리오: 네임스페이스 격리 우회
# dev 네임스페이스의 사용자가 prod 네임스페이스 API 호출 가능

apiVersion: kyverno.io/v1
kind: Policy  # 네임스페이스 정책 (ClusterPolicy가 아님)
metadata:
  name: malicious-policy
  namespace: dev  # dev 네임스페이스에 생성
spec:
  rules:
    - name: cross-namespace-access
      match:
        any:
          - resources:
              kinds: ["*"]
      context:
        - name: secrets
          apiCall:
            urlPath: "/api/v1/namespaces/prod/secrets"
            # dev 사용자가 prod 시크릿에 접근!


```
-->
-->

### 6.3 즉시 조치

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # Kyverno 버전 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```bash
> # Kyverno 버전 확인...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```bash
# Kyverno 버전 확인
kubectl get pods -n kyverno -o jsonpath='{.items[*].spec.containers[*].image}'

# 패치 버전으로 업그레이드
helm upgrade kyverno kyverno/kyverno \
  --namespace kyverno \
  --set image.tag=v1.16.3

# Kyverno ServiceAccount RBAC 제한
kubectl get clusterrolebinding | grep kyverno


```
-->
-->

---

## 7. eScan 안티바이러스 공급망 공격

### 7.1 사건 요약

| 항목 | 내용 |
|------|------|
| **피해 기업** | MicroWorld Technologies (eScan 개발사) |
| **공격 기간** | 2026년 1월 20-22일 |
| **공격 유형** | 업데이트 서버 침해 → 악성 서명 업데이트 배포 |
| **영향 범위** | 글로벌 기업 고객 |
| **출처** | [BleepingComputer](https://www.bleepingcomputer.com/news/security/escan-confirms-update-server-breached-to-push-malicious-update/) |

### 7.2 공격 체인

```text
eScan 업데이트 서버 침해
    ↓
정상 서명된 악성 업데이트 생성
    ↓
자동 업데이트 채널을 통해 글로벌 배포
    ↓
기업 엔드포인트에 다단계 멀웨어 설치
    ↓
정보 수집 + 추가 페이로드 다운로드
```

### 7.3 공급망 공격 방어 체크리스트

- [ ] 소프트웨어 업데이트 **이중 서명 검증** (코드 서명 + 해시 검증)
- [ ] 업데이트 서버 **무결성 모니터링** (FIM) 구성
- [ ] **SBOM(Software Bill of Materials)** 생성 및 관리
- [ ] 업데이트 배포 전 **스테이징 환경 테스트** 필수화
- [ ] 엔드포인트 **행동 기반 탐지** (EDR) 활성화
- [ ] 업데이트 **롤백 메커니즘** 사전 구축

---

## 8. 추가 주요 CVE 요약

| CVE | 대상 | CVSS | 유형 | 상태 |
|-----|------|------|------|------|
| CVE-2026-24835 | Podman Desktop | Critical | 인증 우회 | v1.25.1 패치 |
| CVE-2026-24905 | Inspektor Gadget | High | 명령 주입 | v0.48.1 패치 |
| CVE-2026-24740 | Dozzle | High | 컨테이너 접근 우회 | 패치 가용 |
| CVE-2026-20045 | Cisco Unified CM | Critical | 제로데이 | 실제 공격 중 |
| CVE-2025-31133 | runc | High | 컨테이너 탈출 | v1.1.14 패치 |

### Podman Desktop CVE-2026-24835 상세

`isAccessAllowed()` 함수가 무조건 `true`를 반환하여, **악성 확장이 모든 인증 세션을 탈취**할 수 있습니다.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

> **참고**: 관련 예제는 [공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.

```bash
# Podman Desktop 버전 확인 및 업그레이드
podman desktop version
# 1.25.1 이상으로 업그레이드 필수
```

---

## 9. 2026년 2월 보안 대응 종합 로드맵

### 즉시 대응 (이번 주)

| 우선순위 | 항목 | 담당 |
|----------|------|------|
| **P0** | Fortinet FortiOS 긴급 패치 (CVE-2026-24858) | 네트워크 보안팀 |
| **P0** | Azure 보안 업데이트 적용 (CVE-2026-24304) | 클라우드팀 |
| **P0** | Kyverno 1.16.3+ 업그레이드 (CVE-2026-22039) | K8s 운영팀 |
| **P1** | eScan 관련 IoC 점검 | SOC/보안관제 |
| **P1** | OpenSSL 최신 버전 확인 | 인프라팀 |

### 단기 대응 (이번 달)

| 우선순위 | 항목 | 담당 |
|----------|------|------|
| **P1** | OWASP Agentic AI Top 10 기반 AI 에이전트 보안 평가 | 보안 아키텍처팀 |
| **P1** | AI 에이전트 거버넌스 정책 수립 (NIST AI RMF 기반) | CISO/보안기획 |
| **P2** | 컨테이너 런타임(runc) 패치 확인 | DevOps팀 |
| **P2** | 공급망 보안 SBOM 도입 검토 | DevSecOps팀 |

### 장기 대응 (Q1 2026)

| 항목 | 상세 |
|------|------|
| **AI 보안 감사 도구 도입** | AISLE 같은 전문 AI 보안 분석 파이프라인 구축 |
| **EU AI Act 준비** | 2026년 8월 2일 시행 대비 AI 시스템 매핑 및 위험 평가 |
| **Zero Trust for AI Agents** | AI 에이전트에 대한 제로 트러스트 아키텍처 설계 |

---

## 10. 한국 조직 영향 분석 (Korean Impact Analysis)

### 10.1 Fortinet FortiGate (CVE-2026-24858) 한국 영향도

**영향 받는 한국 조직**
- 전국 지자체 및 공공기관 (행정안전부 보안 지침에 따라 Fortinet 방화벽 다수 사용)
- 금융권 (은행, 증권사 대부분이 Fortinet 엔터프라이즈 방화벽 운영)
- 대기업 및 중견기업 IDC (FortiGate를 경계 방화벽으로 사용)
- 클라우드 서비스 제공자 (네이버 클라우드, KT Cloud 등 내부 보안 장비)

**한국 특화 위험 요소**
1. **정부 통합보안관제센터(G-SOC) 연계 기관** - FortiGate 로그가 중앙 관제센터로 전송되므로 침해 시 관제 우회 가능
2. **전자금융거래법 준수 필수** - 금융권은 침해 사고 시 금융감독원 보고 의무 (24시간 내)
3. **K-ISMS 인증 기관** - 연간 재심사 시 제로데이 패치 미적용이 발견되면 인증 취소 위험

**즉시 조치 사항 (한국 기준)**
- [ ] **행안부/KISA 보안 공지 확인** - 한국인터넷진흥원(KISA)이 발표하는 긴급 보안 업데이트 확인
- [ ] **금융보안원(FSI) 긴급 통보** 확인 (금융권 해당)
- [ ] **FortiGate 관리 인터페이스 IP 제한** - VPN 또는 전용선에서만 접근 가능하도록 설정
- [ ] **G-SOC 연계 로그 재검증** - FortiCloud SSO 관련 인증 로그 전수 점검

### 10.2 Azure Resource Manager (CVE-2026-24304) 한국 영향도

**영향 받는 한국 조직**
- Azure Korea Central/Korea South 리전 사용 기업 (삼성, LG, 현대, SK 등 대기업)
- 금융권 클라우드 전환 프로젝트 (카카오뱅크, 토스뱅크 등 디지털뱅크)
- 공공기관 클라우드 우선 정책 대상 (행안부 지침에 따라 Azure 사용 증가)
- 스타트업 및 SaaS 기업 (Azure 기반 서비스 운영)

**한국 특화 위험 요소**
1. **클라우드 컴퓨팅 보안인증(CSAP)** - Azure 사용 공공기관은 CSAP 인증 유지 필수
2. **전자정부법 클라우드 보안 가이드** - 공공기관은 클라우드 보안 사고 시 과기정통부 보고 의무
3. **개인정보보호법(PIPA)** - Azure에 개인정보 저장 시 침해 사고는 개인정보보호위원회 신고 대상

**즉시 조치 사항 (한국 기준)**
- [ ] **한국 리전(Korea Central/South) 우선 패치** - Microsoft는 한국 리전에 대한 패치 롤아웃 시차 확인
- [ ] **CSAP 인증 기관 재심사 대비** - 패치 적용 이력 문서화 (스크린샷, 로그)
- [ ] **개인정보보호 영향평가(PIA) 재검토** - Azure에 저장된 개인정보 유형 및 암호화 상태 확인
- [ ] **Azure AD Conditional Access 한국 IP 제한** - 한국 IP 대역에서만 Azure Portal 접근 허용

### 10.3 Kyverno (CVE-2026-22039) 한국 영향도

**영향 받는 한국 조직**
- 네이버, 카카오, 라인, 배달의민족 등 대형 IT 기업 (Kubernetes 대규모 클러스터 운영)
- 핀테크 및 게임 기업 (쿠팡, 넥슨, 엔씨소프트 등)
- MSP(Managed Service Provider) 사업자 (메가존클라우드, 베스핀글로벌 등)

**한국 특화 위험 요소**
1. **금융권 컨테이너 보안 가이드** - 금융보안원(FSI)이 요구하는 컨테이너 격리 정책 위반 가능
2. **K-ISMS-P 인증 요구사항** - 개인정보 처리 시스템의 네임스페이스 격리 실패는 인증 요구사항 위반
3. **전자상거래법** - 결제 정보를 다루는 K8s 클러스터는 침해 시 공정거래위원회 신고 대상

**즉시 조치 사항 (한국 기준)**
- [ ] **금융보안원 컨테이너 보안 가이드 재검토** - Kyverno 정책이 FSI 요구사항 충족하는지 확인
- [ ] **K-ISMS-P 심사 대비 문서화** - Kyverno 버전 업그레이드 이력 및 RBAC 정책 문서화
- [ ] **한국 클라우드 제공사 지원 요청** - 네이버 클라우드, KT Cloud 등에서 관리형 Kubernetes 사용 시 벤더 패치 일정 확인

### 10.4 eScan 공급망 공격 한국 영향도

**영향 받는 한국 조직**
- 중소기업 (eScan은 한국에서 비용 효율적인 안티바이러스로 일부 사용)
- 공공기관 엔드포인트 보안 (일부 지자체 및 교육기관)

**한국 특화 위험 요소**
1. **정보보호제품 평가인증(CC 인증)** - eScan이 CC 인증 제품인지 확인 필요 (공공기관 사용 시 필수)
2. **중소기업 정보보호 지원사업** - KISA 지원으로 eScan 도입한 기업은 대체 제품 검토 필요

**즉시 조치 사항 (한국 기준)**
- [ ] **KISA 보안공지 확인** - eScan 공급망 공격 관련 한국 CERT 공지 확인
- [ ] **CC 인증 제품으로 대체** - 공공기관은 KISA CC 인증 목록에서 대체 안티바이러스 선택
- [ ] **중소기업 보안 컨설팅** - KISA 중소기업 정보보호 지원센터에 대체 제품 문의

### 10.5 AI 보안 (AISLE AI, OWASP Agentic AI) 한국 준비도

**한국 조직 현황**
- **AI 에이전트 도입 초기 단계** - 금융권 및 대기업 중심으로 LangChain, AutoGPT 기반 에이전트 실험 중
- **AI 규제 부재** - EU AI Act와 달리 한국은 AI 보안 규제가 미흡 (과기정통부 가이드라인만 존재)
- **KISA AI 보안 가이드** - 2025년 발표된 AI 보안 가이드가 있으나 구속력 없음

**한국 조직 대응 방향**
1. **금융권 AI 보안 가이드 적용** - 금융보안원(FSI)이 발표할 AI 에이전트 보안 가이드 선제 준비
2. **K-ISMS-P AI 확장 대비** - 개인정보 처리 AI 시스템은 향후 K-ISMS-P 인증 대상 가능성 높음
3. **EU AI Act 준수 (수출 기업)** - EU 시장 진출 기업은 2026년 8월 시행 EU AI Act 준비 필수

---

## 11. 경영진 보고 형식 (Board Reporting Format)

### 보고 제목: 2026년 2월 1주차 사이버보안 긴급 브리핑

**보고일**: 2026년 2월 1일
**보고자**: CISO (Chief Information Security Officer)
**수신**: CEO, CTO, CFO, 이사회

---

### A. 긴급 조치 필요 사항 (Executive Action Required)

| 위협 | 비즈니스 영향 | 재무 리스크 | 조치 기한 | 담당 |
|------|-------------|-----------|----------|------|
| **Fortinet 제로데이** | 방화벽 우회 → 전사 네트워크 침투 | 침해 시 평균 $500만 손실 | **즉시** | 네트워크팀 |
| **Azure 권한 상승** | 클라우드 리소스 완전 탈취 | 침해 시 클라우드 비용 폭증 + 데이터 유출 | **24시간 내** | 클라우드팀 |
| **Kyverno 격리 우회** | K8s 프로덕션 환경 침투 | 서비스 다운타임 → 매출 손실 | **48시간 내** | DevOps팀 |

**CFO 참고**: 침해 사고 발생 시 예상 비용
- 직접 손실: 시스템 복구, 데이터 유출 대응 ($300만~$1,000만)
- 간접 손실: 브랜드 이미지 훼손, 고객 이탈 (매출의 5~15%)
- 규제 벌금: GDPR/개인정보보호법 위반 시 최대 $2,000만 또는 매출의 4%

---

### B. 전략적 의사결정 필요 사항 (Strategic Decisions Needed)

#### 1. AI 보안 투자 의사결정

**배경**: AI가 OpenSSL 제로데이 12건을 전량 발견한 역사적 사건 발생. AI 보안 도구의 실효성이 입증됨.

**의사결정 옵션**:

| 옵션 | 투자 규모 | 기대 효과 | 리스크 |
|------|----------|----------|--------|
| **A. AI 보안 도구 도입** | $50만~$150만/년 | 제로데이 조기 발견, 코드 감사 자동화 | 초기 학습 비용, 오탐 가능성 |
| **B. 기존 SAST 도구 유지** | $10만/년 | 비용 절감 | AI 시대 뒤처짐, 제로데이 대응 지연 |
| **C. 하이브리드 (AI + 기존)** | $30만/년 | AI 장점 + 기존 도구 안정성 | 도구 통합 복잡도 |

**CISO 권고**: 옵션 C (하이브리드) - AI 도구를 실험적으로 도입하되 기존 SAST와 병행하여 위험 최소화

#### 2. AI 에이전트 거버넌스 정책 수립

**배경**: OWASP Agentic AI Top 10 발표. 자율 AI 에이전트의 보안 위험이 공식화됨.

**의사결정 필요**:
- AI 에이전트 사용 승인 프로세스 수립
- AI 에이전트 접근 권한 정책 (최소 권한 원칙)
- AI 에이전트 행동 모니터링 및 감사 체계

**타임라인**: Q1 2026 (3개월) 내 정책 수립 완료

**예산**: $20만 (컨설팅 + 정책 수립 + 교육)

---

### C. 운영 현황 (Operational Status)

| 지표 | 현재 상태 | 목표 | 평가 |
|------|----------|------|------|
| **패치 적용률** | 85% (Fortinet, Azure 미적용 포함) | 95% | 🔴 미달 |
| **제로데이 대응 시간** | 평균 48시간 | 24시간 | 🟡 개선 필요 |
| **보안 예산 집행률** | 60% (Q1 기준) | 75% | 🟢 양호 |
| **보안 인력 충원** | 10명 (목표 15명) | 15명 | 🔴 미달 |

**인력 이슈**: 보안 엔지니어 5명 부족. 채용 시장 경쟁 심화로 연봉 인상 검토 필요.

---

### D. 이사회 질의응답 (Q&A for Board)

**Q1. 이번 Fortinet 제로데이가 우리 조직에 영향을 미칠 가능성은?**
A1. 현재 전사 방화벽 30대 중 20대가 Fortinet FortiGate입니다. 패치 미적용 시 외부 공격자가 방화벽을 우회하여 내부 네트워크에 침투할 수 있습니다. **즉시 패치 적용 중**이며, 패치 전까지 FortiCloud SSO 기능을 비활성화했습니다.

**Q2. AI 보안 도구 도입 시 투자 대비 효과는?**
A2. AISLE AI가 OpenSSL 제로데이 12건을 발견한 사례는 AI 보안 도구의 실효성을 입증합니다. 우리 조직에서는 연간 약 2,000건의 코드 변경이 발생하며, AI 도구 도입 시 **제로데이 발견 시간을 90% 단축**할 수 있습니다. 투자 회수 기간은 약 18개월로 예상됩니다.

**Q3. Azure 권한 상승 취약점이 클라우드 비용에 미치는 영향은?**
A3. 공격자가 Azure 관리자 권한을 탈취하면 **VM을 무제한으로 생성**하여 크립토마이닝에 악용할 수 있습니다. 2025년 유사 사례에서 한 기업이 72시간 만에 $30만의 Azure 비용이 청구된 사례가 있습니다. **즉시 패치 적용 및 비용 알람 설정** 완료했습니다.

**Q4. 공급망 공격(eScan) 같은 사건을 어떻게 방지하나?**
A4. 현재 우리 조직은 eScan을 사용하지 않지만, 유사한 공급망 공격을 방지하기 위해 다음 조치를 시행 중입니다:
- 모든 소프트웨어 업데이트를 **스테이징 환경에서 48시간 테스트** 후 프로덕션 적용
- **SBOM(Software Bill of Materials)** 생성 및 관리
- 업데이트 서버 **무결성 모니터링(FIM)** 구성

---

### E. 이사회 의결 사항 (Board Approval Needed)

1. **AI 보안 도구 도입 예산 승인** - $30만/년 (하이브리드 옵션)
2. **보안 인력 5명 추가 채용 승인** - 연간 $75만 (연봉 인상 포함)
3. **AI 에이전트 거버넌스 정책 수립 프로젝트 승인** - $20만

**총 예산**: $125만/년

---

## 12. 위협 헌팅 쿼리 (Threat Hunting Queries)

### 12.1 Fortinet FortiCloud SSO 제로데이 헌팅

**헌팅 목표**: FortiCloud SSO 인증 우회 시도 또는 성공 탐지

#### Azure Sentinel KQL

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
// 단기간 내 다수의 SSO 인증 실패 후 성공 패턴 탐지
CommonSecurityLog
| where DeviceVendor == "Fortinet"
| where DeviceProduct startswith "FortiGate"
| where TimeGenerated > ago(7d)
| where Activity contains "sso" or Activity contains "authentication"
| extend AuthResult = case(
    DeviceAction == "authsuccess", "Success",
    DeviceAction == "authfailure", "Failure",
    "Unknown"
)
| summarize
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated),
    TotalAttempts = count(),
    Failures = countif(AuthResult == "Failure"),
    Successes = countif(AuthResult == "Success"),
    UniqueUsers = dcount(DestinationUserName)
    by SourceIP
| where Failures > 5 and Successes > 0
| extend SuspicionScore = (Failures * 1.0) + (Successes * 5.0)
| where SuspicionScore > 10
| project FirstSeen, LastSeen, SourceIP, TotalAttempts, Failures, Successes, UniqueUsers, SuspicionScore
| order by SuspicionScore desc


```
-->
-->
{% endraw %}

#### Splunk SPL

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```spl
index=fortigate sourcetype=fortigate_log earliest=-7d
(action=authfailure OR action=authsuccess)
| eval auth_result=if(action=="authsuccess", "Success", "Failure")
| eval is_sso=if(like(msg, "%SSO%") OR like(msg, "%sso%"), 1, 0)
| where is_sso=1
| stats
    min(_time) as first_seen,
    max(_time) as last_seen,
    count as total_attempts,
    sum(eval(if(auth_result=="Failure",1,0))) as failures,
    sum(eval(if(auth_result=="Success",1,0))) as successes,
    dc(user) as unique_users
    by src_ip
| where failures > 5 AND successes > 0
| eval suspicion_score = (failures * 1) + (successes * 5)
| where suspicion_score > 10
| eval first_seen=strftime(first_seen, "%Y-%m-%d %H:%M:%S")
| eval last_seen=strftime(last_seen, "%Y-%m-%d %H:%M:%S")
| table first_seen, last_seen, src_ip, total_attempts, failures, successes, unique_users, suspicion_score
| sort -suspicion_score


```
-->
-->
{% endraw %}

### 12.2 Azure Resource Manager 권한 상승 헌팅

**헌팅 목표**: Azure RM API를 통한 비정상 권한 상승 활동 탐지

#### Azure Sentinel KQL

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
// 낮은 권한 사용자가 높은 권한 역할을 할당받는 패턴
let HighPrivilegeRoles = dynamic([
    "Owner", "Contributor", "User Access Administrator",
    "Security Admin", "Global Administrator"
]);
AzureActivity
| where OperationNameValue == "Microsoft.Authorization/roleAssignments/write"
| where ActivityStatusValue == "Success"
| extend RoleDefinition = tostring(parse_json(Properties).roleDefinitionId)
| extend PrincipalId = tostring(parse_json(Properties).principalId)
| where RoleDefinition has_any (HighPrivilegeRoles)
| join kind=leftouter (
    AzureActivity
    | where TimeGenerated > ago(30d)
    | where OperationNameValue == "Microsoft.Authorization/roleAssignments/write"
    | summarize HistoricalRoleAssignments = count() by Caller
) on Caller
| where HistoricalRoleAssignments < 3 or isempty(HistoricalRoleAssignments)
| project
    TimeGenerated,
    Caller,
    PrincipalId,
    RoleDefinition,
    ResourceId,
    HistoricalRoleAssignments,
    CorrelationId
| order by TimeGenerated desc


```
-->
-->
{% endraw %}

#### Splunk SPL

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```spl
index=azure sourcetype=azure:activity earliest=-7d
operationName="Microsoft.Authorization/roleAssignments/write"
status=Succeeded
| spath input=_raw path=properties.roleDefinitionId output=role_definition
| spath input=_raw path=properties.principalId output=principal_id
| spath input=_raw path=caller output=caller
| where like(role_definition, "%Owner%") OR like(role_definition, "%Contributor%") OR like(role_definition, "%Administrator%")
| join type=left caller [
    search index=azure sourcetype=azure:activity earliest=-30d
    operationName="Microsoft.Authorization/roleAssignments/write"
    | spath input=_raw path=caller output=caller
    | stats count as historical_count by caller
]
| where historical_count < 3 OR isnull(historical_count)
| table _time, caller, principal_id, role_definition, historical_count
| sort -_time


```
-->
-->
{% endraw %}

### 12.3 Kyverno 네임스페이스 격리 우회 헌팅

**헌팅 목표**: Kyverno Policy를 통한 크로스 네임스페이스 접근 시도 탐지

#### Kubernetes Audit Log (Splunk)

{% raw %}
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```spl
> index=k8s sourcetype=kube:apiserver:audit earliest=-7d...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```spl
> index=k8s sourcetype=kube:apiserver:audit earliest=-7d...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```spl
index=k8s sourcetype=kube:apiserver:audit earliest=-7d
objectRef.resource="policies" OR objectRef.resource="clusterpolicies"
verb IN ("create", "update", "patch")
| spath input=requestObject path=spec.rules{}.context{}.apiCall.urlPath output=api_call_path
| where like(api_call_path, "%/namespaces/%")
| rex field=api_call_path "/namespaces/(?<target_namespace>[^/]+)/"
| rex field=objectRef.namespace "(?<policy_namespace>.*)"
| where policy_namespace != target_namespace AND isnotnull(target_namespace)
| table _time, user.username, objectRef.name, policy_namespace, target_namespace, api_call_path
| sort -_time


```
-->
-->
{% endraw %}

#### Elasticsearch (ELK)

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조
```json
{
  "query": {
    "bool": {
      "must": [
        {"term": {"objectRef.resource": "policies"}},
        {"terms": {"verb": ["create", "update", "patch"]}},
        {"wildcard": {"requestObject.spec.rules.context.apiCall.urlPath": "*/namespaces/*"}}
      ],
      "filter": [
        {"range": {"@timestamp": {"gte": "now-7d"}}}
      ]
    }
  },
  "aggs": {
    "cross_namespace_policies": {
      "terms": {"field": "objectRef.name.keyword", "size": 50},
      "aggs": {
        "users": {"terms": {"field": "user.username.keyword"}},
        "namespaces": {"terms": {"field": "objectRef.namespace.keyword"}}
      }
    }
  }
}


```
-->
-->

### 12.4 eScan 공급망 공격 헌팅

**헌팅 목표**: eScan 업데이트 서버에서 다운로드된 악성 파일 실행 탐지

#### Windows Security Event Log (Splunk)

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```spl
index=windows sourcetype=WinEventLog:Security EventCode=4688 earliest=-14d
| eval process_name=lower(New_Process_Name)
| where like(process_name, "%escan%") OR like(process_name, "%mwav.exe%") OR like(process_name, "%ecls.exe%")
| eval parent_process=lower(Creator_Process_Name)
| where like(parent_process, "%svchost.exe%") OR like(parent_process, "%services.exe%")
| stats
    count,
    values(New_Process_Name) as processes,
    values(Command_Line) as command_lines,
    dc(Computer_Name) as affected_hosts
    by Account_Name
| where affected_hosts > 5
| table _time, Account_Name, processes, command_lines, affected_hosts, count
| sort -count


```
-->
-->
{% endraw %}

#### Azure Sentinel KQL (Windows Events)

{% raw %}
<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```kql
SecurityEvent
| where TimeGenerated > ago(14d)
| where EventID == 4688 // Process creation
| where tolower(NewProcessName) contains "escan"
    or tolower(NewProcessName) contains "mwav.exe"
    or tolower(NewProcessName) contains "ecls.exe"
| where tolower(ParentProcessName) contains "svchost.exe"
    or tolower(ParentProcessName) contains "services.exe"
| summarize
    FirstSeen = min(TimeGenerated),
    LastSeen = max(TimeGenerated),
    ExecutionCount = count(),
    AffectedHosts = dcount(Computer),
    Processes = make_set(NewProcessName),
    CommandLines = make_set(CommandLine)
    by Account
| where AffectedHosts > 5
| project FirstSeen, LastSeen, Account, ExecutionCount, AffectedHosts, Processes, CommandLines
| order by ExecutionCount desc


```
-->
-->
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
| CVE-2026-22039 | Kyverno < 1.16.3 | Critical | 2026-01 | [GitHub Security Advisory](https://github.com/kyverno/kyverno/security/advisories) |
| CVE-2026-24835 | Podman Desktop < 1.25.1 | Critical | 2026-01 | [Podman Desktop GitHub](https://github.com/podman-desktop/podman-desktop/security/advisories) |
| CVE-2026-24905 | Inspektor Gadget < 0.48.1 | High | 2026-01 | [Inspektor Gadget Advisory](https://github.com/inspektor-gadget/inspektor-gadget/security/advisories) |
| CVE-2026-24740 | Dozzle | High | 2026-01 | [Dozzle GitHub](https://github.com/amir20/dozzle/security/advisories) |
| CVE-2026-20045 | Cisco Unified Communications Manager | Critical | 2026-01 | [Cisco Security Advisory](https://sec.cloudapps.cisco.com/security/center/publicationListing.x) |
| CVE-2025-31133 | runc < 1.1.14 | High | 2025-12 | [runc GitHub](https://github.com/opencontainers/runc/security/advisories) |

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
