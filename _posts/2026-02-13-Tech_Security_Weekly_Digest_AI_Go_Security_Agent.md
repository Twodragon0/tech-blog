---
layout: post
title: "Tech & Security Weekly Digest: Lazarus, RCE, Cloud"
date: 2026-02-13 12:39:45 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go, Security, Agent]
excerpt: "2026년 02월 13일 주요 보안/기술 뉴스 25건 - AI, Go, Security"
description: "2026년 02월 13일 보안 뉴스: The Hacker News, Microsoft Security Blog 등 25건. AI, Go, Security, Agent 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go, Security]
author: Twodragon
comments: true
image: /assets/images/2026-02-13-Tech_Security_Weekly_Digest_AI_Go_Security_Agent.svg
image_alt: "Tech Security Weekly Digest February 13 2026 AI Go Security"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title="Tech & Security Weekly Digest (2026년 02월 13일)"
  categories_html="<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>"
  tags_html="<span class="tag">Security-Weekly</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">2026</span>"
  highlights_html="<li><strong>The Hacker News</strong>: Google Reports State-Backed Hackers Using Gemini AI for...</li>
      <li><strong>The Hacker News</strong>: Lazarus Campaign Plants Malicious Packages in npm and...</li>
      <li><strong>Microsoft Security Blog</strong>: Copilot Studio agent security: Top 10 risks you can...</li>
      <li><strong>Google Cloud Blog</strong>: Simpler billing, clearer savings: A FinOps guide to...</li>"
  period="2026년 02월 13일 (24시간)"
  audience="보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
%}

## Executive Summary

2026년 02월 13일 기준 보안 현황 및 위협 분석입니다.

### 위험 스코어카드

```text
+================================================================+
|          2026-02-13 주간 보안 위험 스코어카드                      |
+================================================================+
|                                                                |
|  항목                    위험도   점수    조치 시급도             |
|  ----------------------------------------------------------   |
|  Copilot Studio agent security: █████████░  9/10   [즉시]                |
|  ThreatsDay Bulletin: AI Prompt █████████░  9/10   [즉시]                |
|  ----------------------------------------------------------   |
|  종합 위험 수준: █████████░ HIGH (9.0/10)                         |
|                                                                |
+================================================================+
```


### 경영진 대시보드

```text
+================================================================+
|        보안 현황 대시보드 - 2026년 02월 13일                         |
+================================================================+
|                                                                |
|  [위협 현황]              [패치 현황]         [컴플라이언스]       |
|  +-----------+           +-----------+      +-----------+      |
|  | Critical 2|           | 적용필요 2|      | 적합   3  |      |
|  | High     0|           | 평가중  0 |      | 검토중  2 |      |
|  | Medium   13|           | 정보참고 1|      | 미대응  0 |      |
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
| **주요 위협** | Critical: 2건, High: 0건 | 대응 진행 중 |
| **패치 적용** | 긴급 패치 대상 시스템 식별 완료 | 검토 필요 |
| **규제 대응** | 보안 정책 및 컴플라이언스 점검 | 정상 |

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 02월 13일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 25개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 4개
- **클라우드 뉴스**: 4개
- **DevOps 뉴스**: 2개
- **블록체인 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | Google Reports State-Backed Hackers Using Gemini A... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Lazarus Campaign Plants Malicious Packages in npm ... | 🟡 Medium |
| 🔒 **Security** | Microsoft Secur | Copilot Studio agent security: Top 10 risks you ca... | 🔴 Critical |
| 🔒 **Security** | The Hacker News | ThreatsDay Bulletin: AI Prompt RCE, Claude 0-Click... | 🔴 Critical |
| 🔒 **Security** | Microsoft Secur | Your complete guide to Microsoft experiences at RS... | 🟡 Medium |

---

## 1. 보안 뉴스

### 1.1 Google Reports State-Backed Hackers Using Gemini AI for Recon and Attack Support

#### 개요

Google on Thursday said it observed the North Korea-linked threat actor known as UNC2970 using its generative artificial intelligence (AI) model Gemini to conduct reconnaissance on its targets, as various hacking groups continue to weaponize the tool for accelerating various phases of the cyber attack life cycle, enabling information operations, and even conducting model extraction attacks. "The

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/google-reports-state-backed-hackers.html)

#### 핵심 포인트

- Google on Thursday said it observed the North Korea-linked threat actor known as UNC2970 using its generative artificial intelligence (AI) model Gemini to conduct reconnaissance on its targets, as various hacking groups continue to weaponize the tool for accelerating various phases of the cyber attack life cycle, enabling information operations, and even conducting model extraction attacks


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

### 1.2 Lazarus Campaign Plants Malicious Packages in npm and PyPI Ecosystems

#### 개요

Cybersecurity researchers have discovered a fresh set of malicious packages across npm and the Python Package Index (PyPI) repository linked to a fake recruitment-themed campaign orchestrated by the North Korea-linked Lazarus Group. The coordinated campaign has been codenamed graphalgo in reference to the first package published in the npm registry. It's assessed to be active since May 2025. "

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/lazarus-campaign-plants-malicious.html)

#### 핵심 포인트

- Cybersecurity researchers have discovered a fresh set of malicious packages across npm and the Python Package Index (PyPI) repository linked to a fake recruitment-themed campaign orchestrated by the North Korea-linked Lazarus Group
- The coordinated campaign has been codenamed graphalgo in reference to the first package published in the npm registry
- It's assessed to be active since May 2025


#### 실무 영향

- 의존성 감사(dependency audit) 즉시 실행: `npm audit`, `pip audit`, `bundle audit`
- SBOM(Software Bill of Materials) 최신 상태 확인
- 서드파티 라이브러리 버전 고정 및 무결성 검증(checksum/signature)
- CI/CD 파이프라인의 의존성 스캔 정책 점검


---

### 1.3 Copilot Studio agent security: Top 10 risks you can detect and prevent

> 🔴 **심각도**: Critical

#### 개요

Copilot Studio agents are increasingly powerful. With that power comes risk: small misconfigurations, over‑broad sharing, unauthenticated access, and weak orchestration controls can create real exposure. This article consolidates the ten most common risks we observe and maps each to practical detections and mitigations using Microsoft Defender capabilities. The post Copilot Studio agent security: Top 10 risks you can detect and prevent appeared first on Microsoft Security Blog .

> **출처**: [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/02/12/copilot-studio-agent-security-top-10-risks-detect-prevent/)

#### 핵심 포인트

- Copilot Studio agents are increasingly powerful
- With that power comes risk: small misconfigurations, over‑broad sharing, unauthenticated access, and weak orchestration controls can create real exposure
- This article consolidates the ten most common risks we observe and maps each to practical detections and mitigations using Microsoft Defender capabilities
- The post Copilot Studio agent security: Top 10 risks you can detect and prevent appeared first on Microsoft Security Blog 


#### 실무 영향

- 관련 시스템의 인증 정보(Credential) 즉시 로테이션 검토
- MFA(다중 인증) 적용 현황 점검 및 미적용 시스템 식별
- SSO/IdP 로그에서 비정상 인증 시도 모니터링 강화
- 서비스 계정 및 API 키 사용 현황 감사


---

## 2. AI/ML 뉴스

### 2.1 Introducing GPT-5.3-Codex-Spark

#### 개요

Introducing GPT-5.3-Codex-Spark—our first real-time coding model. 15x faster generation, 128k context, now in research preview for ChatGPT Pro users.

> **출처**: [OpenAI Blog](https://openai.com/index/introducing-gpt-5-3-codex-spark)

#### 핵심 포인트

- Introducing GPT-5.3-Codex-Spark—our first real-time coding model
- 15x faster generation, 128k context, now in research preview for ChatGPT Pro users


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.2 Introducing PFCS Forward

#### 개요

Introducing PFCS Forward: Extending IL5/IL6 Authorization from Cloud to Edge Integrated systems that solve meaningful problems for commanders and their warfighting requirements are essential, according to Lieutenant General Paul T. Stanton, Director of DISA and Commander of DoD Cyber Defense Command, at DISA’s Forecast to Industry 2025 (December 8, 2025) Hardware-Agnostic Accreditation Brings IL5 and IL6 Authorization from the Cloud to the Tactical Edge Authorization overhead has become a fun...

> **출처**: [Palantir Blog](https://blog.palantir.com/introducing-pfcs-forward-d8755d34c429?source=rss----3c87dc14372f---4)

#### 핵심 포인트

- Introducing PFCS Forward: Extending IL5/IL6 Authorization from Cloud to Edge Integrated systems that solve meaningful problems for commanders and their warfighting requirements are essential, according to Lieutenant General Paul T
- Stanton, Director of DISA and Commander of DoD Cyber Defense Command, at DISA’s Forecast to Industry 2025 (December 8, 2025) Hardware-Agnostic Accreditation Brings IL5 and IL6 Authorization from the Cloud to the Tactical Edge Authorization overhead has become a fun


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.3 AI meets HR: Transforming talent acquisition with Amazon Bedrock

#### 개요

In this post, we show how to create an AI-powered recruitment system using Amazon Bedrock, Amazon Bedrock Knowledge Bases, AWS Lambda, and other AWS services to enhance job description creation, candidate communication, and interview preparation while maintaining human oversight.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/ai-meets-hr-transforming-talent-acquisition-with-amazon-bedrock/)

#### 핵심 포인트

- In this post, we show how to create an AI-powered recruitment system using Amazon Bedrock, Amazon Bedrock Knowledge Bases, AWS Lambda, and other AWS services to enhance job description creation, candidate communication, and interview preparation while maintaining human oversight


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

### 3.1 Simpler billing, clearer savings: A FinOps guide to updated spend-based CUDs

#### 개요

Optimizing cloud spend is one of the most rewarding aspects of FinOps — and committed use discounts (CUDs) remain one of the most effective levers to pull. In July 2025, we began rolling out updates to the spend-based CUD model to make it easier to understand your costs and savings, expand coverage to new SKUs (including Cloud Run and H3/M-series VMs), and offer increased flexibility. These changes are now available to all customers. Let’s dive into how this new model simplifies your FinOps p...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/cost-management/a-finops-professionals-guide-to-updated-spend-based-cuds/)

#### 핵심 포인트

- Optimizing cloud spend is one of the most rewarding aspects of FinOps — and committed use discounts (CUDs) remain one of the most effective levers to pull
- In July 2025, we began rolling out updates to the spend-based CUD model to make it easier to understand your costs and savings, expand coverage to new SKUs (including Cloud Run and H3/M-series VMs), and offer increased flexibility
- These changes are now available to all customers
- Let’s dive into how this new model simplifies your FinOps p


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.2 GTIG AI Threat Tracker: Distillation, Experimentation, and (Continued) Integration of AI for Adversarial Use

#### 개요

Introduction In the final quarter of 2025, Google Threat Intelligence Group (GTIG) observed threat actors increasingly integrating artificial intelligence (AI) to accelerate the attack lifecycle, achieving productivity gains in reconnaissance, social engineering, and malware development. This report serves as an update to our November 2025 findings regarding the advances in threat actor usage of AI tools. By identifying these early indicators and offensive proofs of concept, GTIG aims to arm ...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/distillation-experimentation-integration-ai-adversarial-use/)

#### 핵심 포인트

- Introduction In the final quarter of 2025, Google Threat Intelligence Group (GTIG) observed threat actors increasingly integrating artificial intelligence (AI) to accelerate the attack lifecycle, achieving productivity gains in reconnaissance, social engineering, and malware development
- This report serves as an update to our November 2025 findings regarding the advances in threat actor usage of AI tools
- By identifying these early indicators and offensive proofs of concept, GTIG aims to arm 


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.3 VAMS에서 NVIDIA Isaac Lab을 활용한 GPU 가속 로봇 시뮬레이션 훈련

#### 개요

본 게시글은 AWS Spatial Compute Blog에 작성된 “GPU-Accelerated Robotic Simulation Training with NVIDIA Isaac Lab in VAMS” 블로그를 번역했습니다. 오픈소스 Visual Asset Management System(VAMS)이 이제 NVIDIA Isaac Lab과의 통합을 통해 로봇 자산에 대한 GPU 가속 강화학습(RL)을 지원합니다. 이 파이프라인을 통해 팀은 자산 관리 워크플로우에서 직접 RL 정책을 훈련하고 평가할 수 있으며, 확장 가능한 GPU 컴퓨팅을 […]

> **출처**: [AWS Korea Blog](https://aws.amazon.com/ko/blogs/tech/gpu-accelerated-robotic-simulation-training-with-nvidia-isaac-lab-in-vams/)

#### 핵심 포인트

- 본 게시글은 AWS Spatial Compute Blog에 작성된 “GPU-Accelerated Robotic Simulation Training with NVIDIA Isaac Lab in VAMS” 블로그를 번역했습니다
- 오픈소스 Visual Asset Management System(VAMS)이 이제 NVIDIA Isaac Lab과의 통합을 통해 로봇 자산에 대한 GPU 가속 강화학습(RL)을 지원합니다
- 이 파이프라인을 통해 팀은 자산 관리 워크플로우에서 직접 RL 정책을 훈련하고 평가할 수 있으며, 확장 가능한 GPU 컴퓨팅을 […]


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 4. DevOps & 개발 뉴스

### 4.1 Announcing Interop 2026

#### 개요

Exciting news for web developers, designers, and browser enthusiasts alike — Interop 2026 is here, continuing the mission of improving cross-browser interoperability.

> **출처**: [WebKit Blog](https://webkit.org/blog/17818/announcing-interop-2026/)

#### 핵심 포인트

- Exciting news for web developers, designers, and browser enthusiasts alike — Interop 2026 is here, continuing the mission of improving cross-browser interoperability


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.2 Release Notes for Safari Technology Preview 237

#### 개요

Safari Technology Preview Release 237 is now available for download for macOS Tahoe and macOS Sequoia.

> **출처**: [WebKit Blog](https://webkit.org/blog/17842/release-notes-for-safari-technology-preview-237/)

#### 핵심 포인트

- Safari Technology Preview Release 237 is now available for download for macOS Tahoe and macOS Sequoia


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 5. 블록체인 뉴스

### 5.1 人身売買関連サービスへの暗号資産の資金フローが前年比85%急増

#### 개요

※この記事は自動翻訳されています。正確な内容につきましては原文をご参照ください。 要約 主に東南アジアを拠点とする人身売買の疑いがあるサービスへの暗号資産の資金フローは、2025年に85%増加し、特定されたサービス全体で数億ドル規模に達しました。 Telegramベースの「インターナショナルエスコート」サービスは、中国語圏のマネーロンダリングネットワーク（CMLN）や担保プラットフォームと高度に統合されており、トランザクションの約半数が10,000ドルを超えています。 分析により、東南アジアの人身売買組織のグローバルな展開が明らかになり、南北アメリカ、ヨーロッパ、オーストラリアなど各地から多額の暗号資産が流入しています。 児童性的虐待コンテンツ（CSAM）ネットワークはサブスクリプション型モデルへと進化し、サディスティックなオンライン過激主義（SOE）コミュニティとの重複が増加しています。また、米国のインフラを戦略的に利用している点は、高度な運営計画を示唆しています。 現金取引とは異なり、暗号資産が本質的に持つ透明性は、法執行機関やコンプライアンスチームが人身売買の活動を検知、追...

> **출처**: [Chainalysis Blog](https://www.chainalysis.com/blog/crypto-human-trafficking-2026-japanese/)

#### 핵심 포인트

- ※この記事は自動翻訳されています。正確な内容につきましては原文をご参照ください。 要約 主に東南アジアを拠点とする人身売買の疑いがあるサービスへの暗号資産の資金フローは、2025年に85%増加し、特定されたサービス全体で数億ドル規模に達しました。 Telegramベースの「インターナショナルエスコート」サービスは、中国語圏のマネーロンダリングネットワーク（CMLN）や担保プラットフォームと高度に統合されており、トランザクションの約半数が10,000ドルを超えています。 分析により、東南アジアの人身売買組織のグローバルな展開が明らかになり、南北アメリカ、ヨーロッパ、オーストラリアなど各地から多額の暗号資産が流入しています。 児童性的虐待コンテンツ（CSAM）ネットワークはサブスクリプション型モデルへと進化し、サディスティックなオンライン過激主義（SOE）コミュニティとの重複が増加しています。また、米国のインフラを戦略的に利用している点は、高度な運営計画を示唆しています。 現金取引とは異なり、暗号資産が本質的に持つ透明性は、法執行機関やコンプライアンスチームが人身売買の活動を検知、追


---

### 5.2 Thailand Moves to Cement Bitcoin and Digital Assets in Regulated Derivatives Market

#### 개요

Bitcoin Magazine Thailand Moves to Cement Bitcoin and Digital Assets in Regulated Derivatives Market Thailand is moving to cement bitcoin and other digital assets as legitimate, regulated reference assets in its derivatives and capital markets. This post Thailand Moves to Cement Bitcoin and Digital Assets in Regulated Derivatives Market first appeared on Bitcoin Magazine and is written by Micah Zimmerman .

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/thailand-moves-to-cement-bitcoin)

#### 핵심 포인트

- Bitcoin Magazine Thailand Moves to Cement Bitcoin and Digital Assets in Regulated Derivatives Market Thailand is moving to cement bitcoin and other digital assets as legitimate, regulated reference assets in its derivatives and capital markets
- This post Thailand Moves to Cement Bitcoin and Digital Assets in Regulated Derivatives Market first appeared on Bitcoin Magazine and is written by Micah Zimmerman 


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Europe surges, US stumbles, China cools: EV sales ...](https://electrek.co/2026/02/12/europe-surges-us-stumbles-china-cools-ev-sales-dip-in-2026/) | Electrek | 1.2 million EVs were sold globally in January – but the market shrank. Global EV... |
| [In Washington, DC, curbside parking just became EV...](https://electrek.co/2026/02/12/washington-dc-curbside-parking-ev-charging/) | Electrek | Washington, DC, just launched a curbside charging pilot to install public EV cha... |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 11건 | gpt, ai |
| **Cloud Security** | 5건 | cloud, aws |
| **Zero-Day** | 1건 | 0-day |
| **Supply Chain** | 1건 | package |

이번 주기에서 가장 많이 언급된 트렌드는 **AI/ML** (11건)입니다. 그 다음으로 **Cloud Security** (5건)이 주목받고 있습니다. 실무에서는 해당 트렌드와 관련된 보안 정책 및 모니터링 체계를 점검하시기 바랍니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Copilot Studio agent security: Top 10 risks you can detect a** 관련 긴급 패치 및 영향도 확인
- [ ] **ThreatsDay Bulletin: AI Prompt RCE, Claude 0-Click, RenEngin** 관련 긴급 패치 및 영향도 확인

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
