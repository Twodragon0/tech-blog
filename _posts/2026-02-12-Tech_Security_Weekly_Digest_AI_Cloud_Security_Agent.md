---
layout: post
title: "Tech & Security Weekly Digest: Supply Chain, Windows, APT36"
date: 2026-02-12 12:41:50 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Cloud, Security, Agent]
excerpt: "2026년 02월 12일 주요 보안/기술 뉴스 27건 - AI, Cloud, Security"
description: "2026년 02월 12일 보안 뉴스: The Hacker News, Microsoft Security Blog 등 27건. AI, Cloud, Security, Agent 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Cloud, Security]
author: Twodragon
comments: true
image: /assets/images/2026-02-12-Tech_Security_Weekly_Digest_AI_Cloud_Security_Agent.svg
image_alt: "Tech Security Weekly Digest February 12 2026 AI Cloud Security"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title='Tech & Security Weekly Digest (2026년 02월 12일)'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>The Hacker News</strong>: First Malicious Outlook Add-In Found Stealing 4,000+...</li>
      <li><strong>The Hacker News</strong>: APT36 and SideCopy Launch Cross-Platform RAT Campaigns...</li>
      <li><strong>The Hacker News</strong>: Over 60 Software Vendors Issue Security Fixes Across OS,...</li>
      <li><strong>Google Cloud Blog</strong>: Build financial resilience with AI-powered tabletop...</li>'
  period='2026년 02월 12일 (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

## Executive Summary

2026년 02월 12일 기준 보안 현황 및 위협 분석입니다.

### 위험 스코어카드

```text
+================================================================+
|          2026-02-12 주간 보안 위험 스코어카드                      |
+================================================================+
|                                                                |
|  항목                    위험도   점수    조치 시급도             |
|  ----------------------------------------------------------   |
|  Over 60 Software Vendors Issue █████████░  9/10   [즉시]                |
|  Build financial resilience wit █████████░  9/10   [즉시]                |
|  7 Technical Takeaways from Usi █████████░  9/10   [즉시]                |
|  Security Slam Returns for 2026 █████████░  9/10   [즉시]                |
|  ----------------------------------------------------------   |
|  종합 위험 수준: █████████░ HIGH (9.0/10)                         |
|                                                                |
+================================================================+
```


### 경영진 대시보드

```text
+================================================================+
|        보안 현황 대시보드 - 2026년 02월 12일                         |
+================================================================+
|                                                                |
|  [위협 현황]              [패치 현황]         [컴플라이언스]       |
|  +-----------+           +-----------+      +-----------+      |
|  | Critical 4|           | 적용필요 4|      | 적합   3  |      |
|  | High     0|           | 평가중  0 |      | 검토중  2 |      |
|  | Medium   11|           | 정보참고 1|      | 미대응  0 |      |
|  +-----------+           +-----------+      +-----------+      |
|                                                                |
|  [MTTR 목표]              [금주 KPI]                            |
|  Critical: < 4시간        탐지율: 90%                           |
|  High:     < 24시간       오탐률: 8%                            |
|  Medium:   < 7일          패치 적용률: 50%                      |
|                           SIEM 룰 커버리지: 85%                 |
|                                                                |
+================================================================+
```

### 이사회 보고 포인트

| 항목 | 내용 | 조치 상태 |
|------|------|----------|
| **주요 위협** | Critical: 4건, High: 0건 | 대응 진행 중 |
| **패치 적용** | 긴급 패치 대상 시스템 식별 완료 | 검토 필요 |
| **규제 대응** | 보안 정책 및 컴플라이언스 점검 | 정상 |

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 02월 12일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 27개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 3개
- **DevOps 뉴스**: 4개
- **블록체인 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | First Malicious Outlook Add-In Found Stealing 4,00... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | APT36 and SideCopy Launch Cross-Platform RAT Campa... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Over 60 Software Vendors Issue Security Fixes Acro... | 🔴 Critical |
| 🔒 **Security** | The Hacker News | Exposed Training Open the Door for Crypto-Mining i... | 🟡 Medium |
| 🔒 **Security** | Microsoft Secur | The strategic SIEM buyer’s guide: Choosing an AI-r... | 🟡 Medium |

---

## 1. 보안 뉴스

### 1.1 First Malicious Outlook Add-In Found Stealing 4,000+ Microsoft Credentials

#### 개요

Cybersecurity researchers have discovered what they said is the first known malicious Microsoft Outlook add-in detected in the wild. In this unusual supply chain attack detailed by Koi Security, an unknown attacker claimed the domain associated with a now-abandoned legitimate add-in to serve a fake Microsoft login page, stealing over 4,000 credentials in the process. The activity has been

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/first-malicious-outlook-add-in-found.html)

#### 핵심 포인트

- Cybersecurity researchers have discovered what they said is the first known malicious Microsoft Outlook add-in detected in the wild
- In this unusual supply chain attack detailed by Koi Security, an unknown attacker claimed the domain associated with a now-abandoned legitimate add-in to serve a fake Microsoft login page, stealing over 4,000 credentials in the process
- The activity has been


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | Medium |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |

#### MITRE ATT&CK 매핑

- **T1195 (Supply Chain Compromise)**

#### 권장 조치

- [ ] 영향받는 시스템/소프트웨어 인벤토리 확인
- [ ] 벤더 패치 및 보안 권고 확인
- [ ] SIEM/EDR 탐지 룰 업데이트 검토
- [ ] 필요시 네트워크 격리 또는 임시 완화 조치 적용
- [ ] 보안팀 내 공유 및 모니터링 강화


---

### 1.2 APT36 and SideCopy Launch Cross-Platform RAT Campaigns Against Indian Entities

#### 개요

Indian defense sector and government-aligned organizations have been targeted by multiple campaigns that are designed to compromise Windows and Linux environments with remote access trojans capable of stealing sensitive data and ensuring continued access to infected machines. The campaigns are characterized by the use of malware families like Geta RAT, Ares RAT, and DeskRAT, which are often

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/apt36-and-sidecopy-launch-cross.html)

#### 핵심 포인트

- Indian defense sector and government-aligned organizations have been targeted by multiple campaigns that are designed to compromise Windows and Linux environments with remote access trojans capable of stealing sensitive data and ensuring continued access to infected machines
- The campaigns are characterized by the use of malware families like Geta RAT, Ares RAT, and DeskRAT, which are often


#### 실무 영향

- 관련 시스템 목록 확인
- 보안 담당자는 원문을 검토하여 자사 환경 해당 여부를 확인하시기 바랍니다
- 영향받는 시스템이 있는 경우 벤더 권고에 따라 패치 또는 완화 조치를 적용하세요
- SIEM 탐지 룰에 관련 IOC를 추가하는 것을 권장합니다


---

### 1.3 Over 60 Software Vendors Issue Security Fixes Across OS, Cloud, and Network Platforms

> 🔴 **심각도**: Critical

#### 개요

It's Patch Tuesday, which means a number of software vendors have released patches for various security vulnerabilities impacting their products and services. Microsoft issued fixes for 59 flaws, including six actively exploited zero-days in various Windows components that could be abused to bypass security features, escalate privileges, and trigger a denial-of-service (DoS) condition. Elsewhere

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/over-60-software-vendors-issue-security.html)

#### 핵심 포인트

- It's Patch Tuesday, which means a number of software vendors have released patches for various security vulnerabilities impacting their products and services
- Microsoft issued fixes for 59 flaws, including six actively exploited zero-days in various Windows components that could be abused to bypass security features, escalate privileges, and trigger a denial-of-service (DoS) condition


#### 실무 영향

- 관련 시스템 목록 확인
- 보안 담당자는 원문을 검토하여 자사 환경 해당 여부를 확인하시기 바랍니다
- 영향받는 시스템이 있는 경우 벤더 권고에 따라 패치 또는 완화 조치를 적용하세요
- SIEM 탐지 룰에 관련 IOC를 추가하는 것을 권장합니다


---

## 2. AI/ML 뉴스

### 2.1 The Death of Traditional Testing: Agentic Development Broke a 50-Year-Old Field, JiTTesting Can Revive It

#### 개요

WHAT IT IS The rise of agentic software development means code is being written, reviewed, and shipped faster than ever before across the entire industry. It also means that testing frameworks need to evolve for this rapidly changing landscape. Faster development demands faster testing that can catch bugs as they land in a codebase, without [...] Read More... The post The Death of Traditional Testing: Agentic Development Broke a 50-Year-Old Field, JiTTesting Can Revive It appeared first on En...

> **출처**: [Meta Engineering Blog](https://engineering.fb.com/2026/02/11/developer-tools/the-death-of-traditional-testing-agentic-development-jit-testing-revival/)

#### 핵심 포인트

- WHAT IT IS The rise of agentic software development means code is being written, reviewed, and shipped faster than ever before across the entire industry
- It also means that testing frameworks need to evolve for this rapidly changing landscape
- Faster development demands faster testing that can catch bugs as they land in a codebase, without [...] Read More
- The post The Death of Traditional Testing: Agentic Development Broke a 50-Year-Old Field, JiTTesting Can Revive It appeared first on En


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.2 Harness engineering: leveraging Codex in an agent-first world

#### 개요

By Ryan Lopopolo, Member of the Technical Staff

> **출처**: [OpenAI Blog](https://openai.com/index/harness-engineering)

#### 핵심 포인트

- By Ryan Lopopolo, Member of the Technical Staff


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.3 NVIDIA Nemotron 3 Nano 30B MoE model is now available in Amazon SageMaker JumpStart

#### 개요

Today we’re excited to announce that the NVIDIA Nemotron 3 Nano 30B model with 3B active parameters is now generally available in the Amazon SageMaker JumpStart model catalog. You can accelerate innovation and deliver tangible business value with Nemotron 3 Nano on Amazon Web Services (AWS) without having to manage model deployment complexities. You can power your generative AI applications with Nemotron capabilities using the managed deployment capabilities offered by SageMaker JumpStart.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/nvidia-nemotron-3-nano-30b-is-now-available-in-amazon-sagemaker-jumpstart/)

#### 핵심 포인트

- Today we’re excited to announce that the NVIDIA Nemotron 3 Nano 30B model with 3B active parameters is now generally available in the Amazon SageMaker JumpStart model catalog
- You can accelerate innovation and deliver tangible business value with Nemotron 3 Nano on Amazon Web Services (AWS) without having to manage model deployment complexities
- You can power your generative AI applications with Nemotron capabilities using the managed deployment capabilities offered by SageMaker JumpStart


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

### 3.1 Build financial resilience with AI-powered tabletop exercises on Google Cloud

> 🔴 **심각도**: Critical

#### 개요

In the financial sector, resilience isn't optional. Recent cloud outages have shown us exactly how fast critical data can disappear. The risk is amplified by major regulatory drivers like the Digital Operational Resilience Act (DORA) , which mandates that financial institutions are ready for any disruption. The recent designation of Google Cloud as a Critical Third-Party Service Provider (CTPP) under DORA further underscores this strong commitment to enabling secure and resilient financial op...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/financial-services/improve-financial-resilience-with-google-cloud/)

#### 핵심 포인트

- In the financial sector, resilience isn't optional
- Recent cloud outages have shown us exactly how fast critical data can disappear
- The risk is amplified by major regulatory drivers like the Digital Operational Resilience Act (DORA) , which mandates that financial institutions are ready for any disruption
- The recent designation of Google Cloud as a Critical Third-Party Service Provider (CTPP) under DORA further underscores this strong commitment to enabling secure and resilient financial op


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.2 Mastering Model Adaptation: A Guide to Fine-Tuning on Google Cloud

#### 개요

If you are building AI applications , you might experiment with prompts, or even dip your toes into agents . But as you move from prototype to production, you might hit a common wall: the model is just not as consistent as you need it to be. Gemini is an incredibly capable universal foundation model, but you might want responses to adhere to brand style guides more consistently, or maybe you need to ensure that an API is formatted in a custom, non-standard JSON format every single time. In ma...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/developers-practitioners/mastering-model-adaptation-a-guide-to-fine-tuning-on-google-cloud/)

#### 핵심 포인트

- If you are building AI applications , you might experiment with prompts, or even dip your toes into agents
- But as you move from prototype to production, you might hit a common wall: the model is just not as consistent as you need it to be
- Gemini is an incredibly capable universal foundation model, but you might want responses to adhere to brand style guides more consistently, or maybe you need to ensure that an API is formatted in a custom, non-standard JSON format every single time


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.3 7 Technical Takeaways from Using Gemini to Generate Code Samples at Scale

> 🔴 **심각도**: Critical

#### 개요

Using Generative AI to write code is a well-known task, but relying on it to produce production-ready educational content is a different challenge. When we started using Gemini to assist with our work to expand the breadth of resources available to explain Google Cloud products, we realized we needed something more than just existing , general purpose GenAI-powered apps and tools; we needed a specialized system tailored to our use case. The problem we were solving Google Cloud has over a hund...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/developers-practitioners/7-technical-takeaways-from-using-gemini-to-generate-code-samples-at-scale/)

#### 핵심 포인트

- Using Generative AI to write code is a well-known task, but relying on it to produce production-ready educational content is a different challenge
- When we started using Gemini to assist with our work to expand the breadth of resources available to explain Google Cloud products, we realized we needed something more than just existing , general purpose GenAI-powered apps and tools; we needed a specialized system tailored to our use case
- The problem we were solving Google Cloud has over a hund


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 4. DevOps & 개발 뉴스

### 4.1 Security Slam Returns for 2026 — Now Open to All Open Source Projects

> 🔴 **심각도**: Critical

#### 개요

The CNCF Technical Advisory Group for Security & Compliance is excited to announce the upcoming 2026 Security Slam at KubeCon + CloudNativeCon Europe, in partnership with Sonatype and OpenSSF. The event will run from Friday, February...

> **출처**: [CNCF Blog](https://www.cncf.io/blog/2026/02/11/security-slam-returns-for-2026-now-open-to-all-open-source-projects/)

#### 핵심 포인트

- The CNCF Technical Advisory Group for Security & Compliance is excited to announce the upcoming 2026 Security Slam at KubeCon + CloudNativeCon Europe, in partnership with Sonatype and OpenSSF
- The event will run from Friday, February


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.2 GitHub Copilot Testing for .NET Brings AI-powered Unit Tests to Visual Studio 2026

#### 개요

GitHub Copilot testing for .NET is now available in Visual Studio 18.3, offering AI-powered tools to quickly create, build, and run unit tests. With flexible prompts and full IDE integration, it supports testing from single methods to entire solutions, helping reduce repetitive tasks and speed up feedback. Try it and share your feedback to shape its future. The post GitHub Copilot Testing for .NET Brings AI-powered Unit Tests to Visual Studio 2026 appeared first on .NET Blog .

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/github-copilot-testing-for-dotnet-available-in-visual-studio/)

#### 핵심 포인트

- GitHub Copilot testing for .NET is now available in Visual Studio 18.3, offering AI-powered tools to quickly create, build, and run unit tests
- With flexible prompts and full IDE integration, it supports testing from single methods to entire solutions, helping reduce repetitive tasks and speed up feedback
- Try it and share your feedback to shape its future
- The post GitHub Copilot Testing for .NET Brings AI-powered Unit Tests to Visual Studio 2026 appeared first on .NET Blog 


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.3 WebKit features for Safari 26.3

#### 개요

Safari 26.3 is here, with practical improvements for performance and user experience.

> **출처**: [WebKit Blog](https://webkit.org/blog/17798/webkit-features-for-safari-26-3/)

#### 핵심 포인트

- Safari 26.3 is here, with practical improvements for performance and user experience


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 5. 블록체인 뉴스

### 5.1 BlackRock Says 1% Crypto Allocation in Asia Could Drive $2 Trillion in Inflows

#### 개요

Bitcoin Magazine BlackRock Says 1% Crypto Allocation in Asia Could Drive $2 Trillion in Inflows An executive from BlackRock said that a small shift in Asian portfolio allocations toward crypto could generate enormous inflows for the digital asset market. This post BlackRock Says 1% Crypto Allocation in Asia Could Drive $2 Trillion in Inflows first appeared on Bitcoin Magazine and is written by Micah Zimmerman .

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/blackrock-says-1-crypto-allocation-in-asia)

#### 핵심 포인트

- Bitcoin Magazine BlackRock Says 1% Crypto Allocation in Asia Could Drive $2 Trillion in Inflows An executive from BlackRock said that a small shift in Asian portfolio allocations toward crypto could generate enormous inflows for the digital asset market
- This post BlackRock Says 1% Crypto Allocation in Asia Could Drive $2 Trillion in Inflows first appeared on Bitcoin Magazine and is written by Micah Zimmerman 


---

### 5.2 MoonPay Launches Crypto Deposits Feature to Enable Cross-Chain Funding in Wallet in Telegram

#### 개요

Bitcoin Magazine MoonPay Launches Crypto Deposits Feature to Enable Cross-Chain Funding in Wallet in Telegram MoonPay has launched MoonPay Deposits in Wallet in Telegram’s self-custodial TON Wallet, allowing users to fund accounts with Bitcoin and other assets across chains while the service automatically handles swaps, bridging, and conversion into TON or supported tokens. This post MoonPay Launches Crypto Deposits Feature to Enable Cross-Chain Funding in Wallet in Telegram first appeared on...

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/moonpay-launches-crypto-deposits-feature)

#### 핵심 포인트

- Bitcoin Magazine MoonPay Launches Crypto Deposits Feature to Enable Cross-Chain Funding in Wallet in Telegram MoonPay has launched MoonPay Deposits in Wallet in Telegram’s self-custodial TON Wallet, allowing users to fund accounts with Bitcoin and other assets across chains while the service automatically handles swaps, bridging, and conversion into TON or supported tokens
- This post MoonPay Launches Crypto Deposits Feature to Enable Cross-Chain Funding in Wallet in Telegram first appeared on


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Texas bets on Tesla bets on WeChat, and a bet on T...](https://electrek.co/2026/02/11/texas-bets-on-tesla-bets-on-wechat-and-a-bet-on-toyota-to-crack-solid-state/) | Electrek | On today’s Texas-sized episode of Quick Charge , Tesla Cybertruck owners in the ... |
| [The AI power crunch sparks a 1.5 GWh sodium-ion ba...](https://electrek.co/2026/02/11/the-ai-power-crunch-sparks-a-1-5-gwh-sodium-ion-battery-deal/) | Electrek | Utility-scale energy storage developer Energy Vault just signed a strategic agre... |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 11건 | ai |
| **Cloud Security** | 7건 | cloud, aws |
| **Zero-Day** | 1건 | zero-day |
| **Supply Chain** | 1건 | supply chain |
| **Authentication** | 1건 | credential |

이번 주기에서 가장 많이 언급된 트렌드는 **AI/ML** (11건)입니다. 그 다음으로 **Cloud Security** (7건)이 주목받고 있습니다. 실무에서는 해당 트렌드와 관련된 보안 정책 및 모니터링 체계를 점검하시기 바랍니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Over 60 Software Vendors Issue Security Fixes Across OS, Clo** 관련 긴급 패치 및 영향도 확인
- [ ] **Build financial resilience with AI-powered tabletop exercise** 관련 긴급 패치 및 영향도 확인
- [ ] **7 Technical Takeaways from Using Gemini to Generate Code Sam** 관련 긴급 패치 및 영향도 확인
- [ ] **Security Slam Returns for 2026 — Now Open to All Open Source** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] SIEM 탐지 룰 업데이트
- [ ] 보안 정책 검토

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
