---
layout: post
title: "Tech & Security Weekly Digest: Iran-Linked RedKitten Cyber Campaign Targets, Mandiant Finds ShinyHunters-Style Vishi..."
date: 2026-02-02 12:58:04 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Ransomware]
excerpt: "2026년 02월 02일 주요 보안/기술 뉴스 23건 - AI, Ransomware"
description: "2026년 02월 02일 보안 뉴스: The Hacker News, SK쉴더스 보안 리포트 등 23건. AI, Ransomware 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Ransomware]
author: Twodragon
comments: true
image: /assets/images/2026-02-02-Tech_Security_Weekly_Digest_AI_Ransomware.svg
image_alt: "Tech Security Weekly Digest February 02 2026 AI Ransomware"
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
      <span class="tag">Security-Weekly</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>The Hacker News</strong>: Iran-Linked RedKitten Cyber Campaign Targets Human...</li>
      <li><strong>The Hacker News</strong>: Mandiant Finds ShinyHunters-Style Vishing Attacks...</li>
      <li><strong>The Hacker News</strong>: CERT Polska Details Coordinated Cyber Attacks on 30+...</li>
      <li><strong>AWS Korea Blog</strong>: Amazon Bedrock AgentCore를 활용한 멀티에이전트 운영과 접근제어</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">수집 기간</span>
    <span class="summary-value">2026년 02월 02일 (24시간)</span>
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

## 서론

안녕하세요, **Twodragon**입니다.

2026년 02월 02일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 23개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 2개
- **클라우드 뉴스**: 1개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | Iran-Linked RedKitten Cyber Campaign Targets Human... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Mandiant Finds ShinyHunters-Style Vishing Attacks ... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | CERT Polska Details Coordinated Cyber Attacks on 3... | 🟡 Medium |
| 🔒 **Security** | SK쉴더스 보안 리포트 | HeadLine 11월호 사이버보안 특화 Vertical AI 구축 방안... | 🟡 Medium |
| 🔒 **Security** | SK쉴더스 보안 리포트 | Keep up with Ransomware 11월호 기존 랜섬웨어 코드를 재활용한 Blac... | 🟡 Medium |

---

## 1. 보안 뉴스

### 1.1 Iran-Linked RedKitten Cyber Campaign Targets Human Rights NGOs and Activists

#### 개요

A Farsi-speaking threat actor aligned with Iranian state interests is suspected to be behind a new campaign targeting non-governmental organizations and individuals involved in documenting recent human rights abuses. The activity, observed by HarfangLab in January 2026, has been codenamed RedKitten. It's said to coincide with the nationwide unrest in Iran that began towards the end of 2025,

> **출처**: [The Hacker News](https://thehackernews.com/2026/01/iran-linked-redkitten-cyber-campaign.html)

#### 핵심 포인트

- A Farsi-speaking threat actor aligned with Iranian state interests is suspected to be behind a new campaign targeting non-governmental organizations and individuals involved in documenting recent human rights abuses
- The activity, observed by HarfangLab in January 2026, has been codenamed RedKitten
- It's said to coincide with the nationwide unrest in Iran that began towards the end of 2025,


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | Medium |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |

#### 권장 조치

- [ ] 영향받는 시스템/소프트웨어 인벤토리 확인
- [ ] 벤더 패치 및 보안 권고 확인
- [ ] SIEM/EDR 탐지 룰 업데이트 검토
- [ ] 필요시 네트워크 격리 또는 임시 완화 조치 적용
- [ ] 보안팀 내 공유 및 모니터링 강화


---

### 1.2 Mandiant Finds ShinyHunters-Style Vishing Attacks Stealing MFA to Breach SaaS Platforms

#### 개요

Google-owned Mandiant on Friday said it identified an "expansion in threat activity" that uses tradecraft consistent with extortion-themed attacks orchestrated by a financially motivated hacking group known as ShinyHunters. The attacks leverage advanced voice phishing (aka vishing) and bogus credential harvesting sites mimicking targeted companies to gain unauthorized access to victim

> **출처**: [The Hacker News](https://thehackernews.com/2026/01/mandiant-finds-shinyhunters-using.html)

#### 핵심 포인트

- Google-owned Mandiant on Friday said it identified an "expansion in threat activity" that uses tradecraft consistent with extortion-themed attacks orchestrated by a financially motivated hacking group known as ShinyHunters
- The attacks leverage advanced voice phishing (aka vishing) and bogus credential harvesting sites mimicking targeted companies to gain unauthorized access to victim


#### 실무 영향

- 보안 담당자는 원문을 검토하여 자사 환경 해당 여부를 확인하시기 바랍니다
- 영향받는 시스템이 있는 경우 벤더 권고에 따라 패치 또는 완화 조치를 적용하세요
- SIEM 탐지 룰에 관련 IOC를 추가하는 것을 권장합니다


---

### 1.3 CERT Polska Details Coordinated Cyber Attacks on 30+ Wind and Solar Farms

#### 개요

CERT Polska, the Polish computer emergency response team, revealed that coordinated cyber attacks targeted more than 30 wind and photovoltaic farms, a private company from the manufacturing sector, and a large combined heat and power plant (CHP) supplying heat to almost half a million customers in the country. The incident took place on December 29, 2025. The agency has attributed the attacks to

> **출처**: [The Hacker News](https://thehackernews.com/2026/01/poland-attributes-december-cyber.html)

#### 핵심 포인트

- CERT Polska, the Polish computer emergency response team, revealed that coordinated cyber attacks targeted more than 30 wind and photovoltaic farms, a private company from the manufacturing sector, and a large combined heat and power plant (CHP) supplying heat to almost half a million customers in the country
- The incident took place on December 29, 2025
- The agency has attributed the attacks to


#### 실무 영향

- 보안 담당자는 원문을 검토하여 자사 환경 해당 여부를 확인하시기 바랍니다
- 영향받는 시스템이 있는 경우 벤더 권고에 따라 패치 또는 완화 조치를 적용하세요
- SIEM 탐지 룰에 관련 IOC를 추가하는 것을 권장합니다


---

## 2. AI/ML 뉴스

### 2.1 What's new in TensorFlow 2.19

#### 개요

Posted by the TensorFlow team TensorFlow 2.19 has been released! Highlights of this release include changes to the C++ API in LiteRT, bfloat16 support for tflite casting, discontinue of releasing libtensorflow packages. Learn more by reading the full release notes . Note: Release updates on the new multi-backend Keras will be published on keras.io , starting with Keras 3.0. For more information, please see https://keras.io/keras_3/ . TensorFlow Core LiteRT The public constants tflite::Interpr...

> **출처**: [TensorFlow Blog](https://blog.tensorflow.org/2025/03/whats-new-in-tensorflow-2-19.html)

#### 핵심 포인트

- Posted by the TensorFlow team TensorFlow 2.19 has been released
- Highlights of this release include changes to the C++ API in LiteRT, bfloat16 support for tflite casting, discontinue of releasing libtensorflow packages
- Learn more by reading the full release notes
- Note: Release updates on the new multi-backend Keras will be published on keras.io , starting with Keras 3.0


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.2 What's new in TensorFlow 2.20

#### 개요

Posted by the TensorFlow team TensorFlow 2.20 has been released! For ongoing updates related to the multi-backend Keras, please note that all news and releases, starting with Keras 3.0, are now published directly on keras.io . You can find a complete list of all changes in the full release notes on GitHub . tf.lite is being replaced by LiteRT The tf.lite module will be deprecated with development for on-device inference moving to a new, independent repository: LiteRT . The new APIs are availa...

> **출처**: [TensorFlow Blog](https://blog.tensorflow.org/2025/08/whats-new-in-tensorflow-2-20.html)

#### 핵심 포인트

- Posted by the TensorFlow team TensorFlow 2.20 has been released
- For ongoing updates related to the multi-backend Keras, please note that all news and releases, starting with Keras 3.0, are now published directly on keras.io
- You can find a complete list of all changes in the full release notes on GitHub
- tf.lite is being replaced by LiteRT The tf.lite module will be deprecated with development for on-device inference moving to a new, independent repository: LiteRT


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Amazon Bedrock AgentCore를 활용한 멀티에이전트 운영과 접근제어

#### 개요

AI 에이전트를 처음 구축할 때 가장 단순한 접근 방식은 하나의 에이전트가 외부 서비스(API, MCP)를 직접 호출하도록 구성하는 것 입니다. 이러한 구조는 초기 PoC 단계에서는 구현이 간단하고, 빠르게 아이디어를 검증하는 데 효과적입니다. 그러나 에이전트 기반 시스템을 엔터프라이즈 환경으로 확장하기 시작하면, 이러한 접근 방식은 곧 한계에 부딪히게 됩니다. 에이전트의 수가 증가하고 외부 API, MCP, 내부 서비스가 지속적으로 […]

> **출처**: [AWS Korea Blog](https://aws.amazon.com/ko/blogs/tech/multi-agent-operations-for-airline-agentcore-service/)

#### 핵심 포인트

- AI 에이전트를 처음 구축할 때 가장 단순한 접근 방식은 하나의 에이전트가 외부 서비스(API, MCP)를 직접 호출하도록 구성하는 것 입니다
- 이러한 구조는 초기 PoC 단계에서는 구현이 간단하고, 빠르게 아이디어를 검증하는 데 효과적입니다
- 그러나 에이전트 기반 시스템을 엔터프라이즈 환경으로 확장하기 시작하면, 이러한 접근 방식은 곧 한계에 부딪히게 됩니다
- 에이전트의 수가 증가하고 외부 API, MCP, 내부 서비스가 지속적으로 […]


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 4. DevOps & 개발 뉴스

### 4.1 5 Lessons for enabling self-service and AI-driven infrastructure despite legacy tech at a national bank

#### 개요

Learn how the National Bank of Australia modernized its engineering stack to drive faster innovation.

> **출처**: [HashiCorp Blog](https://www.hashicorp.com/blog/5-lessons-for-enabling-self-service-and-ai-driven-infrastructure-despite-legacy-tech-at-a-national-bank)

#### 핵심 포인트

- Learn how the National Bank of Australia modernized its engineering stack to drive faster innovation


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.2 Boundary 0.21 improves remote access security and UX for RDP connections

#### 개요

Passwordless access and improved UX for RDP connections are now available in Boundary 0.21.

> **출처**: [HashiCorp Blog](https://www.hashicorp.com/blog/boundary-0-21-improves-remote-access-security-and-ux-for-rdp-connections)

#### 핵심 포인트

- Passwordless access and improved UX for RDP connections are now available in Boundary 0.21


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.3 HashiCorp year in review 2025: Lessons in simplifying the cloud

#### 개요

As part of the IBM family, HashiCorp is accelerating its enablement of hybrid cloud and AI-driven automation.

> **출처**: [HashiCorp Blog](https://www.hashicorp.com/blog/hashicorp-year-in-review-2025-lessons-in-simplifying-the-cloud)

#### 핵심 포인트

- As part of the IBM family, HashiCorp is accelerating its enablement of hybrid cloud and AI-driven automation


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 5. 블록체인 뉴스

### 5.1 Bitcoin's 'hopium' for bulls may be over and this weekend's slide could be just the beginning

#### 개요

> **출처**: [CoinDesk](https://www.coindesk.com/markets/2026/02/01/bitcoin-s-hopium-for-bulls-may-be-over-and-this-weekend-s-slide-could-be-just-the-beginning)


---

### 5.2 Hong Kong is positioning itself as crypto’s global connector, says lawmaker Johnny Ng

#### 개요

> **출처**: [CoinDesk](https://www.coindesk.com/policy/2026/02/01/hong-kong-is-positioning-itself-as-crypto-s-global-connector-says-lawmaker-johnny-ng)


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [NetBird – 오픈소스 제로 트러스트 네트워킹...](https://news.hada.io/topic?id=26322) | GeekNews (긱뉴스) | WireGuard® 기반 오버레이 네트워크 와 제로 트러스트 네트워크 액세스(ZTNA) 를 결합해 안전하고 신뢰성 있는 연결을 제공하는 오픈소스... |
| [Apple 플랫폼 보안 (2026년 1월) [PDF]...](https://news.hada.io/topic?id=26321) | GeekNews (긱뉴스) | Apple 플랫폼 보안 가이드 는 iPhone, iPad, Mac, Apple Watch 등 모든 기기에서 하드웨어·소프트웨어·서비스가 통합된 ... |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 9건 | ai |
| **Authentication** | 3건 | credential, sso |
| **Cloud Security** | 1건 | cloud |
| **Supply Chain** | 1건 | package |
| **Ransomware** | 1건 | ransomware |
| **Container/K8s** | 1건 | kubernetes |

이번 주기에서 가장 많이 언급된 트렌드는 **AI/ML** (9건)입니다. 그 다음으로 **Authentication** (3건)이 주목받고 있습니다. 실무에서는 해당 트렌드와 관련된 보안 정책 및 모니터링 체계를 점검하시기 바랍니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] 긴급 보안 패치 적용
- [ ] 취약 시스템 모니터링 강화

### P1 (7일 내)

- [ ] **What's new in TensorFlow 2.19** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] 공격 표면 인벤토리 갱신
- [ ] 접근 제어 감사

---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
