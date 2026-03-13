---
layout: post
title: "기술·보안 주간 다이제스트: CVE-2026-20122, Cisco 보안, AWS 운영"
date: 2026-03-06 12:29:02 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Threat, AI, AWS]
excerpt: "Cisco Catalyst SD-WAN Manager CVE-2026-20122 활성 공격 확인, Europol의 Tycoon 2FA PhaaS 해체(64,000건 공격), APT28 우크라이나 표적 신규 악성코드 배포, GPT-5.4 출시 및 Google Cloud 보안 체크리스트 등 22건의 DevSecOps 실무 위협 분석."
description: "Cisco Catalyst SD-WAN Manager CVE-2026-20122 활성 공격 확인, Europol의 Tycoon 2FA PhaaS 해체(64,000건 공격), APT28 우크라이나 표적 신규 악성코드 배포, GPT-5.4 출시 및 Google Cloud 보안 체크리스트 등 22건의 DevSecOps 실무 위협 분석."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Threat, AI]
author: Twodragon
comments: true
image: /assets/images/2026-03-06-Tech_Security_Weekly_Digest_Security_Threat_AI_AWS.svg
image_alt: "Tech Security Weekly Digest March 06 2026 Security Threat AI AWS"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">기술·보안 주간 다이제스트 (2026년 03월 06일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags"><span class="tag">Security-Weekly</span>
      <span class="tag">Cisco-SD-WAN</span>
      <span class="tag">Tycoon-2FA</span>
      <span class="tag">GPT-5.4</span>
      <span class="tag">GKE</span>
      <span class="tag">2026</span></span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list"><li><strong>Cisco SD-WAN 제로데이 공격</strong>: CVE-2026-20122 활성 공격 확인, Catalyst SD-WAN Manager 임의 파일 덮어쓰기 취약점</li>
      <li><strong>Tycoon 2FA 피싱 플랫폼 해체</strong>: Europol 주도 국제공조로 64,000건 AitM 피싱 공격에 사용된 PhaaS 플랫폼 셧다운</li>
      <li><strong>GPT-5.4 출시</strong>: OpenAI 최신 프런티어 모델, 네이티브 컴퓨터 사용 기능과 100만 토큰 컨텍스트 지원</li>
      <li><strong>Google Cloud 보안 체크리스트</strong>: MVSP 기반 보안 설정 권장 체크리스트 공개, 에이전틱 AI 시대 대응</li></ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">수집 기간</span>
    <span class="summary-value">2026년 03월 06일 (24시간)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

---

## 경영진 브리핑

- 경계 장비 취약점 악용과 피싱 인프라 고도화가 동시에 진행되어 패치 속도와 탐지 정확도가 핵심 KPI가 되었습니다.
- 단기 대응은 인터넷 노출 장비 우선 패치, AitM/피싱 탐지 룰 보강, 클라우드 보안 기준 준수 점검입니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 경계 장비 취약점 | High | KEV 기반 우선 패치, 외부 노출면 점검 |
| 피싱/AitM 위협 | High | MFA 우회 탐지 룰 강화, 사용자 경보 체계 점검 |
| 클라우드 보안 운영 | Medium | Google/AWS 보안 체크리스트 갭 분석 및 보완 |

## 서론

안녕하세요, Twodragon입니다.

2026년 03월 06일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

> 관련 다이제스트: Coruna iOS 익스플로잇 킷, 핵티비스트 DDoS 급증, AI 거버넌스 RFP 등은 [3월 5일 다이제스트](/2026/03/05/Tech_Security_Weekly_Digest_iOS_Exploit_Hacktivist_DDoS/)에서 다루었습니다.

수집 통계:
- 총 뉴스 수: 22개 (큐레이션)
- 보안 뉴스: 8개
- AI/ML 뉴스: 4개
- 클라우드 뉴스: 4개
- DevOps 뉴스: 2개
- 블록체인 뉴스: 4개

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 보안 | The Hacker News | Cisco SD-WAN Manager CVE-2026-20122 활성 공격 — 임의 파일 덮어쓰기 | 🔴 Critical |
| 🔒 보안 | The Hacker News | Tycoon 2FA PhaaS 플랫폼 해체 — Europol 주도, 64,000건 공격 차단 | 🔴 Critical |
| 🔒 보안 | The Hacker News | APT28 우크라이나 표적 BadPaw/MeowMeow 신규 악성코드 | 🟠 High |
| 🔒 보안 | The Hacker News | Dust Specter — 이라크 정부 관료 표적 신규 멀웨어 캠페인 | 🟠 High |
| 🔒 보안 | Microsoft Security | 악성 AI 어시스턴트 확장 프로그램, LLM 채팅 기록 탈취 | 🟠 High |
| 🔒 보안 | The Hacker News | MFA 한계점과 자격 증명 남용 시작점 분석 | 🟡 Medium |
| 🤖 AI/ML | OpenAI Blog | GPT-5.4 출시 — 네이티브 컴퓨터 사용, 100만 토큰 컨텍스트 | 🟠 High |
| ☁️ 클라우드 | Google Cloud Blog | Google Cloud 보안 체크리스트 — MVSP 기반 권장 설정 | 🟠 High |
| ☁️ 클라우드 | Google Cloud Blog | 2025 제로데이 리뷰 — GTIG 분석, 90개 제로데이 추적 | 🟠 High |
| ☁️ 클라우드 | Google Cloud Blog | GKE 커스텀 메트릭 네이티브 지원 — 오토스케일링 고도화 | 🟡 Medium |

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. 보안 뉴스

### 1.1 Cisco Catalyst SD-WAN Manager 취약점 활성 공격 확인

{%- include news-card.html
  title="[보안] Cisco Catalyst SD-WAN Manager 취약점 활성 공격 확인"
  url="https://thehackernews.com/2026/03/cisco-confirms-active-exploitation-of.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgEr5vlbwHAPeevtBJ7iylInnh2ZQCxX10smm1srCFONJBSriIbAvvp5jAFpFYdeoyk9BKBhyFZx-U4xBhqtN2eT1r150GMLdRP3scA8PsHMYh0PGALAqnzwQnLS-3K_9yneL-7tRa3lD-TTOIebyc_alzp2kLKFdFRCiJcWMcmTiMnoqUAeO_Wxv6hd05D/s1700-e365/cisco-exploit.jpg"
  summary="Cisco가 Catalyst SD-WAN Manager(구 SD-WAN vManage)에 영향을 미치는 2개의 취약점이 실제 공격에 활용되고 있음을 공식 확인했습니다. 핵심 취약점인 CVE-2026-20122(CVSS 7.1)는 인증된 원격 공격자가 로컬 파일 시스템의 임의 파일을 덮어쓸 수 있는 취약점입니다."
  source="The Hacker News"
-%}


Cisco가 Catalyst SD-WAN Manager(구 SD-WAN vManage)에 영향을 미치는 2개의 취약점이 실제 공격에 활용되고 있음을 공식 확인했습니다. 핵심 취약점인 CVE-2026-20122(CVSS 7.1)는 인증된 원격 공격자가 로컬 파일 시스템의 임의 파일을 덮어쓸 수 있는 취약점입니다.

SD-WAN Manager는 대규모 WAN 인프라의 중앙 관리 플랫폼으로, 이 시스템이 침해될 경우 전체 SD-WAN 네트워크의 구성이 변조될 수 있습니다. 특히 인증된 사용자 권한만으로 공격이 가능하다는 점에서, 내부자 위협이나 초기 침투 후 횡적 이동 시나리오에서 심각한 위험을 초래합니다.

실무 대응:
- Cisco PSIRT 권고에 따른 긴급 패치 적용 (SD-WAN Manager 업데이트)
- SD-WAN Manager 접근 가능 계정의 권한 최소화 및 비정상 인증 시도 모니터링
- SD-WAN 구성 파일 무결성 검증 및 백업 확인

#### 위협 분석

| 항목 | 내용 |
|------|------|
| CVE ID | CVE-2026-20122 |
| CVSS | 7.1 |
| 공격 벡터 | 네트워크 (인증 필요) |
| 영향 | 임의 파일 덮어쓰기 |
| 대상 | Catalyst SD-WAN Manager |
| 심각도 | Critical |
| 대응 우선순위 | P0 - 즉시 대응 |

#### MITRE ATT&CK 매핑

- T1565.001 (Stored Data Manipulation) — 파일 시스템 직접 조작
- T1078 (Valid Accounts) — 인증된 계정 악용
- T1570 (Lateral Tool Transfer) — SD-WAN 네트워크 내 횡적 이동

#### SIEM 탐지 쿼리 (참고용)

```splunk
index=network sourcetype=cisco:sdwan
("file overwrite" OR "unauthorized write" OR "vManage" OR "SD-WAN Manager")
| stats count by src_ip, user, dest_path
| where count > 3
| lookup threat_intel src_ip OUTPUT threat_group
```


---

### 1.2 Europol 주도 Tycoon 2FA 피싱 플랫폼 해체

{%- include news-card.html
  title="[보안] Europol 주도 Tycoon 2FA 피싱 플랫폼 해체"
  url="https://thehackernews.com/2026/03/europol-led-operation-takes-down-tycoon.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgj8UTSWEMM2rFGJeOr4V1jcbj7LGdQOWonmvhfcbkNspvoCt-7wsBrnJoMuGgnyCZ-E4G5DqWRcPYrrTi3MF-nZWM3pke6JmFrnNlIrs99WF4ayKdghQxMVtvsxxkvv0FMHmKHWCA92klsfqy2fS4rD0_YcBTOapV-lsGCsZhnLHMCe3oMhEukpHaTgGQE/s1700-e365/takedown.jpg"
  summary="Europol이 주도한 국제 공조 작전으로 Tycoon 2FA 피싱-서비스(PhaaS) 플랫폼이 해체되었습니다. 이 플랫폼은 MFA를 우회하는 AitM(Adversary-in-the-Middle) 방식의 자격 증명 탈취 공격을 대규모로 가능하게 했으며, 총 64,000건 이상의 공격에 연루된 것으로 확인되었습니다."
  source="The Hacker News"
-%}


Europol이 주도한 국제 공조 작전으로 Tycoon 2FA 피싱-서비스(PhaaS) 플랫폼이 해체되었습니다. 이 플랫폼은 MFA를 우회하는 AitM(Adversary-in-the-Middle) 방식의 자격 증명 탈취 공격을 대규모로 가능하게 했으며, 총 64,000건 이상의 공격에 연루된 것으로 확인되었습니다.

Tycoon 2FA는 공격자가 피해자와 정상 인증 서버 사이에 프록시를 삽입하여, MFA 토큰까지 실시간으로 가로채는 방식을 사용했습니다. 이로 인해 SMS, TOTP 기반 MFA만으로는 보호가 불충분하다는 점이 다시 한번 증명되었습니다.

실무 대응:
- FIDO2/WebAuthn 기반 피싱 저항성 MFA로 전환 검토
- AitM 공격 탐지를 위한 세션 토큰 이상 행위 모니터링 강화
- Tycoon 2FA 관련 IoC(도메인, IP) 차단 목록 업데이트

#### 위협 분석

| 항목 | 내용 |
|------|------|
| 위협 유형 | PhaaS (Phishing-as-a-Service) |
| 공격 방식 | AitM (Adversary-in-the-Middle) |
| 피해 규모 | 64,000건+ 공격 |
| MFA 우회 | SMS/TOTP 기반 MFA 우회 가능 |
| 대응 | Europol 주도 국제공조 해체 |
| 대응 우선순위 | P0 - MFA 정책 즉시 검토 |

#### MITRE ATT&CK 매핑

- T1557 (Adversary-in-the-Middle) — 실시간 인증 토큰 가로채기
- T1556.006 (Multi-Factor Authentication Interception) — MFA 우회
- T1566.002 (Spearphishing Link) — 피싱 링크 배포


---

### 1.3 APT28 우크라이나 표적 BadPaw/MeowMeow 신규 악성코드

{%- include news-card.html
  title="[보안] APT28 우크라이나 표적 BadPaw/MeowMeow 신규 악성코드"
  url="https://thehackernews.com/2026/03/apt28-linked-campaign-deploys-badpaw.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEihW1ns0JTT2vYUjdQEqTcDwytBGmTnID9xQkCxuT-WURhd71xeh9UD80hZiRL3WWBOg5dCVZKY2huOuElbB-QjczQquCirdpgVRjWNM426jLNF-U_s8RGs9CjNC1Qr2DJhQ532z6bz2hdMkzUjJ-vSKpJmBdvyy5qgkAuwB2armvVyx4HNsn4glFMWmupC/s1700-e365/Ukraine.jpg"
  summary="러시아 연계 위협 그룹 APT28(Fancy Bear)이 우크라이나 기관을 대상으로 BadPaw 로더와 MeowMeow 백도어라는 2개의 신규 악성코드를 배포한 것이 확인되었습니다."
  source="The Hacker News"
-%}


러시아 연계 위협 그룹 APT28(Fancy Bear)이 우크라이나 기관을 대상으로 BadPaw 로더와 MeowMeow 백도어라는 2개의 신규 악성코드를 배포한 것이 확인되었습니다.

APT28은 러시아 군 정보기관(GRU)과 연계된 것으로 알려진 APT 그룹으로, 우크라이나-러시아 분쟁 상황에서 지속적으로 사이버 작전을 수행하고 있습니다. 이번에 발견된 악성코드는 이전에 문서화되지 않은 새로운 패밀리로, 기존 탐지 시그니처를 회피할 수 있습니다.

실무 대응:
- APT28 관련 최신 IoC를 위협 인텔리전스 피드에 반영
- 동유럽/CIS 지역과 비즈니스 관계가 있는 조직은 네트워크 트래픽 모니터링 강화
- EDR 솔루션에 BadPaw/MeowMeow 탐지 룰 추가


---

### 1.4 Dust Specter — 이라크 정부 관료 표적 신규 멀웨어

{%- include news-card.html
  title="[보안] Dust Specter — 이라크 정부 관료 표적 신규 멀웨어"
  url="https://thehackernews.com/2026/03/dust-specter-targets-iraqi-officials.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjWg0441avqEutKSymEsuuVP_gKz7kiss4jZesCHLwD4731n135lf6jhJdT2X5CPIWISsByG0RsJoH7eXSyGVOI6RNmo1QkE8Z24lPdiFTLni79c2EoiLGlAurQsIHqn7j_-MDPlL9F98XAsRtrBD17V7YXRYikdcET0hnw897ButkFyI1T4JmzxpJdwM8y/s1700-e365/iran-attack.jpg"
  summary="이란 연계로 추정되는 위협 행위자가 이라크 외교부를 사칭하여 정부 관료를 대상으로 SPLITDROP과 GHOSTFORM이라는 신규 악성코드를 배포하는 캠페인이 포착되었습니다."
  source="The Hacker News"
-%}


이란 연계로 추정되는 위협 행위자가 이라크 외교부를 사칭하여 정부 관료를 대상으로 SPLITDROP과 GHOSTFORM이라는 신규 악성코드를 배포하는 캠페인이 포착되었습니다.

이 캠페인은 중동 지역 지정학적 긴장 속에서 국가 수준의 사이버 스파이 활동이 활발히 이루어지고 있음을 보여줍니다. 정부 기관 사칭은 소셜 엔지니어링의 효과를 극대화하는 전형적인 APT 전술입니다.

실무 대응:
- 외교/정부 관련 도메인에서 발송된 이메일의 발신자 인증(SPF/DKIM/DMARC) 검증 강화
- 중동 지역 관련 비즈니스를 운영하는 조직은 위협 인텔리전스 레벨 상향


---

### 1.5 악성 AI 어시스턴트 확장 프로그램, LLM 채팅 기록 대량 탈취

{%- include news-card.html
  title="[보안] 악성 AI 어시스턴트 확장 프로그램, LLM 채팅 기록 대량 탈취"
  url="https://www.microsoft.com/en-us/security/blog/2026/03/05/malicious-ai-assistant-extensions-harvest-llm-chat-histories/"
  image="https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/03/MS_Actional-Insights_Adversarial-AI.png"
  summary="Microsoft 보안팀이 ChatGPT, DeepSeek 등 LLM 플랫폼의 채팅 기록과 브라우징 데이터를 수집하는 악성 AI 브라우저 확장 프로그램을 발견했습니다. 총 약 90만 건 설치되었으며, 20,000개 이상의 기업 환경에서 활동이 확인되었습니다."
  source="Microsoft Security Blog"
-%}


Microsoft 보안팀이 ChatGPT, DeepSeek 등 LLM 플랫폼의 채팅 기록과 브라우징 데이터를 수집하는 악성 AI 브라우저 확장 프로그램을 발견했습니다. 총 약 90만 건 설치되었으며, 20,000개 이상의 기업 환경에서 활동이 확인되었습니다.

AI 도구의 업무 활용이 확산되면서, LLM 채팅 기록에는 코드 스니펫, 내부 문서, 비즈니스 전략 등 민감한 정보가 포함될 수 있어 새로운 데이터 유출 경로로 부상하고 있습니다.

실무 대응:
- 기업 브라우저 확장 프로그램 허용 목록(allowlist) 정책 시행
- AI 플랫폼 접근 시 기업 관리형 브라우저 프로필 사용 의무화
- Chrome/Edge 엔터프라이즈 정책으로 미승인 확장 프로그램 차단

#### 위협 분석

| 항목 | 내용 |
|------|------|
| 위협 유형 | 악성 브라우저 확장 프로그램 |
| 설치 수 | ~900,000건 |
| 영향 기업 | 20,000+ |
| 타겟 플랫폼 | ChatGPT, DeepSeek 등 |
| 탈취 데이터 | LLM 채팅 기록, 브라우징 데이터 |
| 대응 우선순위 | P1 - 7일 이내 정책 점검 |


---

### 1.6 MFA 한계점과 자격 증명 남용의 시작점

{%- include news-card.html
  title="[보안] MFA 한계점과 자격 증명 남용의 시작점"
  url="https://thehackernews.com/2026/03/where-multi-factor-authentication-stops.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh573fCRL7EMT-Piz1QEJizjMNdQH5G4eMHpLbuCGvm-PNF6-osRuSQF09DHGIuYS1EXDgZXUmWzVf1p3kHDH0_jE7_XDKuG0J7R9Yc3kP4XbaW3UoF3gLYCQ6ba63S0iYQf3Ftf7s0UkDD9QBbnzUcBPRDQXI401TzAVjET05OjgS38tiYgfWA79kS-8g/s1700-e365/outpost.jpg"
  summary="MFA를 도입하면 탈취된 비밀번호만으로 시스템에 접근할 수 없다고 가정하지만, Windows 환경에서는 이 가정이 종종 틀립니다. 공격자들은 NTLM 해시, Kerberos 티켓, 캐시된 자격 증명 등 MFA가 적용되지 않는 인증 경로를 통해 시스템에 접근합니다."
  source="The Hacker News"
-%}


MFA를 도입하면 탈취된 비밀번호만으로 시스템에 접근할 수 없다고 가정하지만, Windows 환경에서는 이 가정이 종종 틀립니다. 공격자들은 NTLM 해시, Kerberos 티켓, 캐시된 자격 증명 등 MFA가 적용되지 않는 인증 경로를 통해 시스템에 접근합니다.

이는 MFA가 "만능 해결책"이 아님을 보여주는 중요한 분석입니다. Pass-the-Hash, Pass-the-Ticket 등의 공격 기법은 MFA를 완전히 우회할 수 있으며, 특히 Active Directory 환경에서 심각한 위험을 초래합니다.

실무 대응:
- Windows 환경에서 NTLM 사용 현황 감사 및 단계적 제거 계획 수립
- Credential Guard 활성화로 자격 증명 덤프 방지
- 특권 접근 관리(PAM) 솔루션을 통한 관리자 자격 증명 보호


---

### 1.7 양자 시대 대비 — 포스트 양자 암호화 웨비나

{%- include news-card.html
  title="[보안] 양자 시대 대비 — 포스트 양자 암호화 웨비나"
  url="https://thehackernews.com/2026/03/preparing-for-quantum-era-post-quantum.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiX1kV8IdraKTyGmXfKTap-DKE7krpM6SchfXQZlvruEBaaJyCbG0HQuJD3B08AkkIZF6Ej7oQ2Nr3AfzVD5klERt782T3IuCPT8tSYm49B6j6se-IH7d0XC4kBcTPl-yp3tsA_YmhrZsB0On2ukhH1rhlSaG3fpRXNrSzpbMEoVu_EBoiMGcbFVg9AcWTC/s1700-e365/webinar.jpg"
  summary="양자 컴퓨터가 현재 암호화를 깨뜨릴 수 있는 미래에 대비하여, 많은 공격자들이 이미 &quot;지금 수집, 나중에 복호화&quot;(Harvest Now, Decrypt Later) 전략을 실행하고 있습니다. 현재의 암호화된 데이터가 안전하다는 가정은 양자 컴퓨팅 시대에 더 이상 유효하지 않을 수 있습니다."
  source="The Hacker News"
-%}


양자 컴퓨터가 현재 암호화를 깨뜨릴 수 있는 미래에 대비하여, 많은 공격자들이 이미 "지금 수집, 나중에 복호화"(Harvest Now, Decrypt Later) 전략을 실행하고 있습니다. 현재의 암호화된 데이터가 안전하다는 가정은 양자 컴퓨팅 시대에 더 이상 유효하지 않을 수 있습니다.

실무 포인트: 암호화 자산 인벤토리를 수행하고, NIST가 표준화한 포스트 양자 암호화 알고리즘(CRYSTALS-Kyber, CRYSTALS-Dilithium)으로의 마이그레이션 로드맵을 수립하세요. 특히 장기 보존이 필요한 민감 데이터부터 우선 검토해야 합니다.


---

### 1.8 주간 위협 동향 요약 — DDR5 봇 스캘핑, 삼성 TV 추적, Reddit 개인정보 과징금

{%- include news-card.html
  title="[보안] 주간 위협 동향 요약 — DDR5 봇 스캘핑, 삼성 TV 추적, Reddit 개인정보 과징금"
  url="https://thehackernews.com/2026/03/threatsday-bulletin-redis-rce-ddr5-bot.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgmX71oTh0PhBoeXrV6BUD7_jQe9VWPqHc60ijUxf4iv8wPE8UeWY8dlDrfbx3-Ut5aNoNQZJ8DH_ADNQGgFL4NbMMcw-IayIe9HXKG3l5EN3-og9LuNqBP452mXpm1HTn3ooWlJ-q4QRqvPJC4gmR0lstJ8KWdQYa2knQ5J69nneIwIRTKKG43fXtcWRXm/s1700-e365/threatsday.jpg"
  summary="이번 주 사이버보안 분야에서 다수의 새로운 동향이 포착되었습니다. DDR5 메모리 구매를 자동화하는 봇 스캘핑 활동, 삼성 TV의 사용자 시청 데이터 추적 문제, Reddit의 개인정보 보호법 위반 과징금 등 다양한 분야에서 보안 이슈가 발생했습니다."
  source="The Hacker News"
-%}


이번 주 사이버보안 분야에서 다수의 새로운 동향이 포착되었습니다. DDR5 메모리 구매를 자동화하는 봇 스캘핑 활동, 삼성 TV의 사용자 시청 데이터 추적 문제, Reddit의 개인정보 보호법 위반 과징금 등 다양한 분야에서 보안 이슈가 발생했습니다.

실무 포인트: 보안팀은 이러한 다양한 위협 트렌드를 주간 브리핑에 포함하고, IoT 기기(스마트 TV 등)의 네트워크 격리 정책을 검토하세요. 개인정보 보호 규정 준수 현황도 함께 점검이 필요합니다.


---

![AI ML News Section Banner](/assets/images/section-ai-ml.svg)

## 2. AI/ML 뉴스

### 2.1 OpenAI GPT-5.4 출시 — 네이티브 컴퓨터 사용과 100만 토큰 컨텍스트

{%- include news-card.html
  title="[AI/ML] OpenAI GPT-5.4 출시 — 네이티브 컴퓨터 사용과 100만 토큰 컨텍스트"
  url="https://openai.com/index/introducing-gpt-5-4"
  image="https://images.ctfassets.net/kftzwdyauwt9/261kYlzPT8cBKoynLi35ct/14e3cae5d20ab9349af93f6b034c2947/5.4_Thinking_Hero___SEO.png?w=1600&h=900&fit=fill"
  summary="OpenAI가 최신 프런티어 모델 GPT-5.4를 공개했습니다. ChatGPT, API, Codex 전반에 적용되는 이 모델은 추론, 코딩, 에이전트 워크플로우 성능을 통합하며, 특히 네이티브 컴퓨터 사용(computer-use) 기능을 내장하여 에이전트가 웹사이트와 소프트웨어를 직접 조작할 수 있습니다."
  source="OpenAI Blog"
-%}


OpenAI가 최신 프런티어 모델 GPT-5.4를 공개했습니다. ChatGPT, API, Codex 전반에 적용되는 이 모델은 추론, 코딩, 에이전트 워크플로우 성능을 통합하며, 특히 네이티브 컴퓨터 사용(computer-use) 기능을 내장하여 에이전트가 웹사이트와 소프트웨어를 직접 조작할 수 있습니다. 최대 100만 토큰 컨텍스트를 지원합니다.

AI 모델이 단순한 텍스트 생성을 넘어 실제 컴퓨터 환경을 조작하는 "에이전틱 AI" 시대가 본격화되고 있습니다. 이는 자동화 역량을 획기적으로 높이는 동시에, AI 에이전트의 권한 관리와 보안 통제에 대한 새로운 과제를 제기합니다.

실무 대응:
- AI 에이전트가 시스템에 접근할 때의 권한 범위(최소 권한 원칙) 정의
- 컴퓨터 사용 기능이 포함된 AI 도구의 샌드박싱 환경 구성 검토
- 100만 토큰 컨텍스트 활용 시 민감 데이터 노출 방지 정책 수립


---

### 2.2 Palantir Maven Smart System — NATO 동맹국 AI 전투 시스템

{%- include news-card.html
  title="[AI/ML] Palantir Maven Smart System — NATO 동맹국 AI 전투 시스템"
  url="https://blog.palantir.com/maven-smart-system-innovating-for-the-alliance-5ebc31709eea?source=rss----3c87dc14372f---4"
  image="https://miro.medium.com/v2/resize:fit:1200/1*rDDZDcEQP011rQj5uPCuwA.png"
  summary="Palantir이 NATO의 Task Force Maven과 협력하여 Maven Smart System을 공개했습니다. 2025년 11월 NATO Warfighting Innovation Week에서 시연된 이 시스템은 동맹국 전투원에게 즉각적인 AI 역량을 제공하는 것을 목표로 합니다."
  source="Palantir Blog"
-%}


Palantir이 NATO의 Task Force Maven과 협력하여 Maven Smart System을 공개했습니다. 2025년 11월 NATO Warfighting Innovation Week에서 시연된 이 시스템은 동맹국 전투원에게 즉각적인 AI 역량을 제공하는 것을 목표로 합니다.

군사 AI 시스템의 발전은 민간 분야에도 영향을 미칩니다. 대규모 데이터 통합, 실시간 의사결정 지원, 다국적 협업 플랫폼 등의 기술은 기업의 보안 운영 센터(SOC)나 위협 인텔리전스 플랫폼에도 적용 가능한 패턴입니다.

실무 포인트: 대규모 데이터 통합 기반 의사결정 지원 시스템 도입 시, Palantir과 같은 플랫폼의 아키텍처 패턴(데이터 온톨로지, 실시간 분석)을 참고할 수 있습니다.


---

### 2.3 Google AI 시각 검색 기술 심층 분석

{%- include news-card.html
  title="[AI/ML] Google AI 시각 검색 기술 심층 분석"
  url="https://blog.google/company-news/inside-google/googlers/how-google-ai-visual-search-works/"
  image="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Fan_out_query_ss.width-1300.png"
  summary="Google이 AI가 사용자의 시각적 검색을 이해하는 방식을 상세히 설명했습니다. 카메라로 촬영한 이미지에서 객체를 인식하고, 텍스트와 이미지를 결합한 멀티모달 이해를 통해 검색 의도를 파악하는 기술입니다."
  source="Google AI Blog"
-%}


Google이 AI가 사용자의 시각적 검색을 이해하는 방식을 상세히 설명했습니다. 카메라로 촬영한 이미지에서 객체를 인식하고, 텍스트와 이미지를 결합한 멀티모달 이해를 통해 검색 의도를 파악하는 기술입니다.

실무 포인트: 멀티모달 AI 검색 기술은 보안 분야에서 영상 감시 분석, 피싱 이미지 탐지, 위조 문서 식별 등에 활용 가능성이 있습니다. 자사 서비스에 시각적 검색이 포함된 경우, AI 모델의 편향성과 프라이버시 영향을 평가하세요.


---

### 2.4 Google 2월 AI 업데이트 종합 — Gemini 3.1 Pro, Nano Banana 2

{%- include news-card.html
  title="[AI/ML] Google 2월 AI 업데이트 종합 — Gemini 3.1 Pro, Nano Banana 2"
  url="https://blog.google/innovation-and-ai/products/google-ai-updates-february-2026/"
  image="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Thumbnail_mPCqgRv.width-1300.png"
  summary="Google이 2026년 2월에 발표한 AI 관련 업데이트를 종합 정리했습니다. Gemini 3.1 Pro와 이미지 생성 모델 Nano Banana 2 등이 포함되며, Google의 AI 제품 라인업 전반에 걸친 개선사항을 다루고 있습니다."
  source="Google AI Blog"
-%}


Google이 2026년 2월에 발표한 AI 관련 업데이트를 종합 정리했습니다. Gemini 3.1 Pro와 이미지 생성 모델 Nano Banana 2 등이 포함되며, Google의 AI 제품 라인업 전반에 걸친 개선사항을 다루고 있습니다.

실무 포인트: 멀티모달 AI 모델의 빠른 발전에 맞춰, 자사에서 사용 중인 AI 모델의 버전과 성능을 정기적으로 벤치마크하세요. Gemini 3.1 Pro의 개선된 추론 능력은 코드 리뷰 자동화나 로그 분석에 활용 가능합니다.


---

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 3. 클라우드 & 인프라 뉴스

### 3.1 Google Cloud 보안 체크리스트 공개 — MVSP 기반 권장 설정

{%- include news-card.html
  title="[클라우드] Google Cloud 보안 체크리스트 공개 — MVSP 기반 권장 설정"
  url="https://cloud.google.com/blog/products/identity-security/introducing-the-google-cloud-recommended-security-checklist/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/Google_Cloud_recommended_security_checklis.max-2000x2000_mUiFTOZ.jpg"
  summary="Google Cloud가 Minimum Viable Secure Product(MVSP) 원칙에 기반한 보안 체크리스트를 공개했습니다. 에이전틱 AI 도입이 가속화되는 가운데, 클라우드 보안과 리스크 관리를 지속적으로 우선시해야 한다는 메시지와 함께, 조직이 보안 요구사항을 관리하고 설정을 검증할 수 있는 체계적인 가이드를 제공합니다."
  source="Google Cloud Blog"
-%}


Google Cloud가 Minimum Viable Secure Product(MVSP) 원칙에 기반한 보안 체크리스트를 공개했습니다. 에이전틱 AI 도입이 가속화되는 가운데, 클라우드 보안과 리스크 관리를 지속적으로 우선시해야 한다는 메시지와 함께, 조직이 보안 요구사항을 관리하고 설정을 검증할 수 있는 체계적인 가이드를 제공합니다.

MVSP는 B2B 소프트웨어의 최소 보안 요구사항을 정의하는 업계 표준으로, Google Cloud가 이를 기반으로 자체 플랫폼 보안 체크리스트를 만든 것은 실무에서 즉시 활용 가능한 가치를 제공합니다.

실무 대응:
- Google Cloud 보안 체크리스트를 다운로드하여 현재 GCP 환경 설정과 대조 감사
- 에이전틱 AI 워크로드에 대한 추가 보안 통제 항목 식별
- 자사 MVSP 기준을 수립하고, 서드파티 벤더 평가에도 적용


---

### 3.2 2025 제로데이 리뷰 — GTIG 분석, 90개 제로데이 추적

{%- include news-card.html
  title="[클라우드] 2025 제로데이 리뷰 — GTIG 분석, 90개 제로데이 추적"
  url="https://cloud.google.com/blog/topics/threat-intelligence/2025-zero-day-review/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/03_ThreatIntelligenceWebsiteBannerIdeas_BA.max-2600x2600.png"
  summary="Google Threat Intelligence Group(GTIG)이 2025년 한 해 동안 추적한 90개 제로데이 취약점에 대한 종합 리뷰를 발표했습니다. 제로데이 공격 트렌드, 주요 타겟 플랫폼, 공격자 유형별 분석 등을 포함합니다."
  source="Google Cloud Blog"
-%}


Google Threat Intelligence Group(GTIG)이 2025년 한 해 동안 추적한 90개 제로데이 취약점에 대한 종합 리뷰를 발표했습니다. 제로데이 공격 트렌드, 주요 타겟 플랫폼, 공격자 유형별 분석 등을 포함합니다.

실무 대응:
- GTIG 보고서의 제로데이 트렌드를 기반으로 자사 취약점 관리 우선순위 재조정
- 빈번하게 공격받는 소프트웨어(브라우저, OS, 엔터프라이즈 앱)의 패치 주기 단축
- 제로데이 대응을 위한 가상 패칭 및 WAF 룰 업데이트 프로세스 점검


---

### 3.3 GKE 커스텀 메트릭 네이티브 지원 — 오토스케일링 고도화

{%- include news-card.html
  title="[클라우드] GKE 커스텀 메트릭 네이티브 지원 — 오토스케일링 고도화"
  url="https://cloud.google.com/blog/products/containers-kubernetes/gke-now-supports-custom-metrics-natively/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/07_-_Containers__Kubernetes_iY4YTLa.max-2600x2600.jpg"
  summary="Google Kubernetes Engine(GKE)이 커스텀 메트릭을 네이티브로 지원하기 시작했습니다. 기존에 CPU와 메모리 기반 오토스케일링은 간단했지만, 큐 깊이(queue depth)나 활성 요청 수(active requests) 같은 애플리케이션 시그널 기반 스케일링은 복잡했습니다."
  source="Google Cloud Blog"
-%}


Google Kubernetes Engine(GKE)이 커스텀 메트릭을 네이티브로 지원하기 시작했습니다. 기존에 CPU와 메모리 기반 오토스케일링은 간단했지만, 큐 깊이(queue depth)나 활성 요청 수(active requests) 같은 애플리케이션 시그널 기반 스케일링은 복잡했습니다. 이번 업데이트로 외부 메트릭 어댑터 없이도 커스텀 메트릭 기반 HPA를 설정할 수 있게 되었습니다.

실무 대응:
- 기존 Prometheus Adapter나 Stackdriver Custom Metrics Adapter를 네이티브 지원으로 마이그레이션 검토
- AI 추론 워크로드의 GPU 활용률, 큐 깊이 등 커스텀 메트릭 기반 오토스케일링 설정
- HPA 설정 시 메트릭 안정화 윈도우(stabilization window) 최적화


---

### 3.4 메리츠증권 AWS 클라우드 기반 차세대 증권 플랫폼

{%- include news-card.html
  title="[클라우드] 메리츠증권 AWS 클라우드 기반 차세대 증권 플랫폼"
  url="https://aws.amazon.com/ko/blogs/tech/meritz-securities-wts-with-gen-ai/"
  image="https://d2908q01vomqb2.cloudfront.net/827bfc458708f0b442009c9c9836f7e4b65557fb/2020/06/03/Blog-Post_thumbnail.png"
  summary="메리츠증권이 AWS 클라우드를 활용하여 차세대 증권 플랫폼을 설계하고 구축한 사례가 공개되었습니다. 리테일 비즈니스 경쟁력 강화를 목표로, 단순 트레이딩 시스템을 넘어 투자자 간 상호작용과 정보 교류가 이루어지는 커뮤니티 중심 서비스를 구축했습니다."
  source="AWS Korea Blog"
-%}


메리츠증권이 AWS 클라우드를 활용하여 차세대 증권 플랫폼을 설계하고 구축한 사례가 공개되었습니다. 리테일 비즈니스 경쟁력 강화를 목표로, 단순 트레이딩 시스템을 넘어 투자자 간 상호작용과 정보 교류가 이루어지는 커뮤니티 중심 서비스를 구축했습니다.

실무 포인트: 금융 분야 클라우드 마이그레이션 시, 규제 요구사항(금융위원회 가이드라인)과 데이터 레지던시 요건을 충족하면서도 Gen AI를 활용한 고객 서비스 혁신이 가능함을 보여주는 국내 사례입니다.


---

![DevOps Platform News Section Banner](/assets/images/section-devops.svg)

## 4. DevOps & 개발 뉴스

### 4.1 MCP C# SDK v1.0 정식 출시

{%- include news-card.html
  title="[DevOps] MCP C# SDK v1.0 정식 출시"
  url="https://devblogs.microsoft.com/dotnet/release-v10-of-the-official-mcp-csharp-sdk/"
  image="https://devblogs.microsoft.com/dotnet/wp-content/uploads/sites/10/2026/03/image.webp"
  summary="Microsoft가 Model Context Protocol(MCP) C# SDK v1.0을 정식 출시했습니다. MCP는 AI 에이전트가 외부 도구와 상호작용하기 위한 표준 프로토콜로, 이번 v1.0에는 향상된 인증(authorization), 풍부한 메타데이터, 도구 호출 및 장시간 실행 요청을 위한 패턴이 포함되었습니다."
  source="Microsoft .NET Blog"
-%}


Microsoft가 Model Context Protocol(MCP) C# SDK v1.0을 정식 출시했습니다. MCP는 AI 에이전트가 외부 도구와 상호작용하기 위한 표준 프로토콜로, 이번 v1.0에는 향상된 인증(authorization), 풍부한 메타데이터, 도구 호출 및 장시간 실행 요청을 위한 패턴이 포함되었습니다.

실무 대응:
- .NET 기반 AI 에이전트 개발 시 MCP C# SDK를 표준 통합 레이어로 채택 검토
- 기존 자체 구현한 도구 호출 인터페이스를 MCP 표준으로 마이그레이션하여 상호운용성 확보
- MCP SDK의 인증 기능을 활용하여 AI 에이전트의 도구 접근 권한 통제


---

### 4.2 모든 AI 플랫폼이 Kubernetes로 수렴하는 이유

{%- include news-card.html
  title="[DevOps] 모든 AI 플랫폼이 Kubernetes로 수렴하는 이유"
  url="https://www.cncf.io/blog/2026/03/05/the-great-migration-why-every-ai-platform-is-converging-on-kubernetes/"
  image="https://www.cncf.io/wp-content/uploads/2026/02/Akamia-Cloud-Credits-2.png"
  summary="CNCF에서 발표한 분석에 따르면, 10년 전 마이크로서비스 배포를 위해 탄생한 Kubernetes가 2026년에는 AI 플랫폼의 사실상 표준 인프라로 자리 잡았습니다. 더 이상 &quot;상태 없는 웹 서비스&quot; 전용이 아니라, GPU 스케줄링, 분산 학습, 모델 서빙 등 AI 워크로드의 전체 라이프사이클을 관리하는 플랫폼으로 진화했습니다."
  source="CNCF Blog"
-%}


CNCF에서 발표한 분석에 따르면, 10년 전 마이크로서비스 배포를 위해 탄생한 Kubernetes가 2026년에는 AI 플랫폼의 사실상 표준 인프라로 자리 잡았습니다. 더 이상 "상태 없는 웹 서비스" 전용이 아니라, GPU 스케줄링, 분산 학습, 모델 서빙 등 AI 워크로드의 전체 라이프사이클을 관리하는 플랫폼으로 진화했습니다.

실무 대응:
- AI/ML 워크로드를 위한 Kubernetes 클러스터 설계 시 GPU 노드풀, 스케줄러 확장(volcano, yunikorn) 검토
- AI 모델 서빙의 카나리 배포, A/B 테스트를 위한 서비스 메시(Istio, Linkerd) 구성
- AI 워크로드 특화 보안 정책(GPU 리소스 격리, 모델 아티팩트 무결성) 수립


---

![Blockchain Web3 News Section Banner](/assets/images/section-blockchain.svg)

## 5. 블록체인 뉴스

### 5.1 비트코인 컨센서스 클린업 — BIP 54 소프트포크 제안

{%- include news-card.html
  title="[블록체인] 비트코인 컨센서스 클린업 — BIP 54 소프트포크 제안"
  url="https://bitcoinmagazine.com/print/the-core-issue-consensus-cleanup"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/03/Core-Issue-Article-Header-2400x1256-Poinsot-1-fotor-20260305161511.webp"
  summary="Bitcoin Magazine가 BIP 54 소프트포크 제안을 심층 분석했습니다. 이 제안은 비트코인 핵심 합의 프로토콜에 존재하는 4가지 미해결 버그를 수정하기 위한 것으로, 네트워크의 장기적 안정성과 보안 강화를 목표로 합니다."
  source="Bitcoin Magazine"
-%}


Bitcoin Magazine가 BIP 54 소프트포크 제안을 심층 분석했습니다. 이 제안은 비트코인 핵심 합의 프로토콜에 존재하는 4가지 미해결 버그를 수정하기 위한 것으로, 네트워크의 장기적 안정성과 보안 강화를 목표로 합니다.

실무 포인트: 비트코인 노드를 운영하는 기관은 BIP 54의 활성화 일정을 추적하고, 소프트포크 적용 시 노드 업데이트 계획을 수립하세요.


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Nano Banana 프롬프팅 가이드](https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-nano-banana/) | Google Cloud Blog | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [LeakBase 포럼 압수](https://thehackernews.com/2026/03/fbi-and-europol-seize-leakbase-forum.html) | The Hacker News | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [Cloudflare Dynamic Path MTU Discovery](https://blog.cloudflare.com/client-dynamic-path-mtu-discovery/) | Cloudflare Blog | 인프라 변경이 안정성·비용·보안 통제에 직접 연결되므로 배포 전 검증 체계가 핵심인 소식입니다. |
| [Cloudflare QUIC 기반 SASE Proxy Mode](https://blog.cloudflare.com/faster-sase-proxy-mode-quic/) | Cloudflare Blog | 인프라 변경이 안정성·비용·보안 통제에 직접 연결되므로 배포 전 검증 체계가 핵심인 소식입니다. |
| [GPT-5.4 공개](https://news.hada.io/topic?id=27230) | GeekNews | AI 기능 확대에 따른 운영 방식 변화와 거버넌스 점검 포인트를 함께 확인해야 하는 업데이트입니다. |
| [Grep은 죽었다: Claude Code 메모리 시스템](https://news.hada.io/topic?id=27239) | GeekNews | AI 기능 확대에 따른 운영 방식 변화와 거버넌스 점검 포인트를 함께 확인해야 하는 업데이트입니다. |
| [Google Chrome, 2주 출시 주기 전환](https://news.hada.io/topic?id=27238) | GeekNews | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [위키백과 관리자 계정 대량 유출](https://news.hada.io/topic?id=27233) | GeekNews | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [온디바이스 이미지 모델 (1편)](https://techblog.lycorp.co.jp/ko/on-device-image-model-trainer-for-messenger-1) | LINE Engineering | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [온디바이스 이미지 모델 (2편)](https://techblog.lycorp.co.jp/ko/on-device-image-model-trainer-for-messenger-2) | LINE Engineering | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [FE News 26년 3월호](https://d2.naver.com/news/0407747) | 네이버 D2 | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| 국제공조 사이버 범죄 소탕 | 3건 | Tycoon 2FA 해체, LeakBase 압수, Europol/FBI |
| 국가 배후 APT 활동 활발 | 2건 | APT28 BadPaw/MeowMeow, Dust Specter SPLITDROP |
| AI 에이전트 시대 보안 | 4건 | GPT-5.4 컴퓨터 사용, MCP SDK, 악성 AI 확장 프로그램, AI 거버넌스 |
| 클라우드 보안 표준화 | 3건 | Google Cloud 보안 체크리스트, GTIG 제로데이 리뷰, MVSP |
| Kubernetes AI 수렴 | 2건 | GKE 커스텀 메트릭, AI 플랫폼 K8s 수렴 |

이번 주기의 핵심 트렌드는 국제 사이버 범죄 소탕과 AI 에이전트 보안입니다.

Europol이 주도한 Tycoon 2FA 해체와 FBI/Europol의 LeakBase 압수는 법 집행기관의 사이버 범죄 대응이 더욱 체계화되고 있음을 보여줍니다. 동시에 APT28과 Dust Specter의 활동은 국가 배후 위협이 여전히 활발하다는 것을 상기시킵니다.

AI 분야에서는 GPT-5.4의 네이티브 컴퓨터 사용 기능 출시가 가장 주목할 만합니다. AI 에이전트가 실제 시스템을 조작할 수 있게 되면서, 에이전트 권한 관리, 도구 접근 통제, 행위 감사 등 새로운 보안 과제가 부상하고 있습니다. MCP C# SDK v1.0 정식 출시와 함께, AI 에이전트 표준 프로토콜 생태계도 빠르게 성숙하고 있습니다.

한편, 악성 AI 브라우저 확장 프로그램이 90만 건 설치되어 LLM 채팅 기록을 탈취한 사건은 AI 도구 자체가 새로운 공격 표면(attack surface)이 되고 있음을 경고합니다. Google Cloud의 MVSP 기반 보안 체크리스트 공개는 이러한 환경에서 기본적인 보안 기준선을 재정립하려는 움직임으로 해석됩니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] Cisco SD-WAN Manager 패치: CVE-2026-20122 영향받는 Catalyst SD-WAN Manager 버전 확인 및 긴급 패치 적용
- [ ] MFA 정책 검토: Tycoon 2FA 해체에 따른 IoC 차단 및 FIDO2/WebAuthn 전환 계획 수립
- [ ] AI 브라우저 확장 프로그램 감사: 기업 환경에서 미승인 AI 관련 브라우저 확장 프로그램 식별 및 차단

### P1 (7일 내)

- [ ] APT28(BadPaw/MeowMeow) 및 Dust Specter(SPLITDROP/GHOSTFORM) IoC를 SIEM/EDR에 반영
- [ ] Google Cloud 보안 체크리스트 다운로드 및 GCP 환경 설정 대조 감사
- [ ] GTIG 2025 제로데이 리뷰 기반 자사 취약점 관리 우선순위 재검토
- [ ] Windows 환경 NTLM 사용 현황 감사 및 Credential Guard 활성화 검토

### P2 (30일 내)

- [ ] 포스트 양자 암호화 마이그레이션 로드맵 초안 수립 (장기 보존 데이터 우선)
- [ ] GKE 커스텀 메트릭 네이티브 지원 활용한 AI 워크로드 오토스케일링 최적화
- [ ] AI 에이전트 보안 정책 수립: GPT-5.4 컴퓨터 사용 기능 등 에이전틱 AI 도구의 권한 범위 정의
- [ ] MCP 프로토콜 기반 AI 도구 통합 표준화 검토

---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

작성자: Twodragon
