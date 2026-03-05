---
layout: post
title: "기술·보안 주간 다이제스트: AWS, iOS, Authentication"
date: 2026-03-05 12:31:09 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go]
excerpt: "2026년 03월 05일 주요 보안/기술 뉴스 27건 - AI, Go"
description: "2026년 03월 05일 보안 뉴스: AWS Security Blog, The Hacker News 등 27건. AI, Go 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go]
author: Twodragon
comments: true
image: /assets/images/2026-03-05-Tech_Security_Weekly_Digest_AI_Go.svg
image_alt: "Tech Security Weekly Digest March 05 2026 AI Go"
toc: true
---

{% include ai-summary-card.html
  title='기술·보안 주간 다이제스트 (2026년 03월 05일)'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">AI</span>
      <span class="tag">Go</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>AWS Security Blog</strong>: [보안] 2025 ISO and CSA STAR certificates are now available</li>
      <li><strong>The Hacker News</strong>: [보안] 149 Hacktivist DDoS Attacks Hit 110 Organizations in</li>
      <li><strong>The Hacker News</strong>: [보안] Coruna iOS Exploit Kit Uses 23 Exploits Across Five</li>
      <li><strong>Google Cloud Blog</strong>: [클라우드] Small models, high quality: Inside BMW Group’s</li>'
  period='2026년 03월 05일 (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 03월 05일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 27개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 5개
- **DevOps 뉴스**: 2개
- **블록체인 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | AWS Security Blog | [보안] 2025 ISO and CSA STAR certificates are now available with one | 🟡 Medium |
| 🔒 **Security** | The Hacker News | [보안] 149 Hacktivist DDoS Attacks Hit 110 Organizations in 16 Countries After | 🟡 Medium |
| 🔒 **Security** | The Hacker News | [보안] Coruna iOS Exploit Kit Uses 23 Exploits Across Five Chains Targeting | 🟠 High |
| 🤖 **AI/ML** | Google AI Blog | [AI] Use Canvas in AI Mode to get things done and bring your | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | [AI] Extending single-minus amplitudes to gravitons | 🟡 Medium |
| 🤖 **AI/ML** | AWS Machine Learning | [AI] Embed Amazon Quick Suite chat agents in enterprise | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | [클라우드] Small models, high quality: Inside BMW Group’s experiments evaluating | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | [클라우드] H4D VMs, now GA, deliver exceptional performance and | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | [클라우드] The AI-native core: Highly resilient telco architecture | 🟡 Medium |
| ⚙️ **DevOps** | CNCF Blog | [DevOps] Scaling organizational structure with Meshery’s expanding | 🟡 Medium |

---

## 1. 보안 뉴스

### 1.1 [보안] 2025 ISO and CSA STAR certificates are now available with one

#### 개요

Amazon Web Services (AWS) successfully completed the annual recertification audit with no findings for ISO 9001:2015, 27001:2022, 27017:2015, 27018:2019, 27701:2019, 20000-1:2018, 22301:2019, and Cloud Security Alliance (CSA) STAR Cloud Controls Matrix (CCM) v4.0.

**실무 포인트**: 보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요.

> **출처**: [AWS Security Blog](https://aws.amazon.com/blogs/security/2025-iso-and-csa-star-certificates-are-now-available-with-one-additional-service-and-one-new-region/)


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

### 1.2 [보안] 149 Hacktivist DDoS Attacks Hit 110 Organizations in 16 Countries After

#### 개요

Cybersecurity researchers have warned of a surge in retaliatory hacktivist activity following the U.S.-Israel coordinated military campaign against Iran, codenamed Epic Fury and Roaring Lion.

**실무 포인트**: 보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요.

> **출처**: [The Hacker News](https://thehackernews.com/2026/03/149-hacktivist-ddos-attacks-hit-110.html)


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

### 1.3 [보안] Coruna iOS Exploit Kit Uses 23 Exploits Across Five Chains Targeting

#### 개요

Google said it identified a "new and powerful" exploit kit dubbed Coruna (aka CryptoWaters) targeting Apple iPhone models running iOS versions between 13.0 and 17.2.1. The exploit kit featured five full iOS exploit chains and a total of 23 exploits, Google Threat Intelligence Group (GTIG) said. It's not effective against the latest version of iOS. The findings were first reported by WIRED.

**실무 포인트**: 보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요.

> **출처**: [The Hacker News](https://thehackernews.com/2026/03/coruna-ios-exploit-kit-uses-23-exploits.html)


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | High |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |

#### 권장 조치

- [ ] 영향받는 시스템/소프트웨어 인벤토리 확인
- [ ] 벤더 패치 및 보안 권고 확인
- [ ] SIEM/EDR 탐지 룰 업데이트 검토
- [ ] 필요시 네트워크 격리 또는 임시 완화 조치 적용
- [ ] 보안팀 내 공유 및 모니터링 강화


---

## 2. AI/ML 뉴스

### 2.1 [AI] Use Canvas in AI Mode to get things done and bring your

#### 개요

Canvas in AI Mode is now available for everyone in the U.S. Plus, it can now help you draft documents or build interactive tools.

**실무 포인트**: AI/ML 파이프라인 및 서비스에 미치는 영향을 검토하세요.

> **출처**: [Google AI Blog](https://blog.google/products-and-platforms/products/search/ai-mode-canvas-writing-coding/)


#### 실무 적용 포인트

- 관련 AI/ML 기술의 자사 적용 가능성 및 보안 영향 평가
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 동향 공유 및 도입 로드맵 논의


---

### 2.2 [AI] Extending single-minus amplitudes to gravitons

#### 개요

A new preprint extends single-minus amplitudes to gravitons, with GPT-5.2 Pro helping derive and verify nonzero graviton tree amplitudes in quantum gravity.

**실무 포인트**: AI/ML 파이프라인 및 서비스에 미치는 영향을 검토하세요.

> **출처**: [OpenAI Blog](https://openai.com/index/extending-single-minus-amplitudes-to-gravitons)


#### 실무 적용 포인트

- LLM 입출력 데이터 보안 및 프라이버시 검토
- 모델 서빙 환경의 접근 제어 및 네트워크 격리 확인
- 프롬프트 인젝션 등 적대적 공격 대응 방안 점검


---

### 2.3 [AI] Embed Amazon Quick Suite chat agents in enterprise

#### 개요

Organizations find it challenging to implement a secure embedded chat in their applications and can require weeks of development to build authentication, token validation, domain security, and global distribution infrastructure. In this post, we show you how to solve this with a one-click deployment solution to embed the chat agents using the Quick Suite Embedding SDK in enterprise portals.

**실무 포인트**: AI Agent 도입 시 권한 범위 설정과 출력 검증 체계를 사전에 수립하세요.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/embed-amazon-quick-suite-chat-agents-in-enterprise-applications/)


#### 실무 적용 포인트

- AI 에이전트 도구 호출 권한 및 접근 범위 최소화 설계
- 에이전트 행동 로깅 및 감사 파이프라인 구축 검토
- 에이전트 출력에 대한 검증 및 사람 감독(Human-in-the-Loop) 설계


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 [클라우드] Small models, high quality: Inside BMW Group’s experiments evaluating

#### 개요

A car you can talk to has been a longstanding dream, whether as the basis for television shows or more recent smartphone integrations. One way of achieving better, more natural voice commands is by incorporating AI foundation models into vehicle systems, which offer more intelligence than traditional voice commands.

**실무 포인트**: 인프라 및 운영 환경 영향을 검토하세요.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/manufacturing/how-bmw-is-testing-slms-not-llms-for-in-vehicle-voice-commands/)


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.2 [클라우드] H4D VMs, now GA, deliver exceptional performance and

#### 개요

Today, we’re announcing the general availability of H4D VMs , our latest high performance computing (HPC)-optimized VM, powered by the 5th Generation AMD EPYC ™ processors . H4D VMs deliver exceptional performance, scalability, and value for industries like manufacturing, health care and life sciences, weather forecasting, and electronic design automation (EDA).

**실무 포인트**: 클러스터 버전 호환성과 워크로드 영향을 확인하세요.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/compute/h4d-vms-now-ga/)


#### 실무 적용 포인트

- Kubernetes 클러스터 보안 정책(PSP/PSA) 점검
- 네트워크 폴리시 및 RBAC 설정 최신화 확인
- 커뮤니티 행사 참가를 통한 최신 보안 동향 파악


---

### 3.3 [클라우드] The AI-native core: Highly resilient telco architecture

#### 개요

The telecommunications industry has reached a critical tipping point. Traditional, on-premises-heavy data center models are struggling under the weight of escalating infrastructure costs and an under utilization due to availability and compliance requirements. But the AI era demands exponential scale and beyond-nines reliability.

**실무 포인트**: 클러스터 버전 호환성과 워크로드 영향을 확인하세요.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/networking/gke-for-telco-building-a-highly-resilient-ai-native-core/)


#### 실무 적용 포인트

- Kubernetes 클러스터 보안 정책(PSP/PSA) 점검
- 네트워크 폴리시 및 RBAC 설정 최신화 확인
- 커뮤니티 행사 참가를 통한 최신 보안 동향 파악


---

## 4. DevOps & 개발 뉴스

### 4.1 [DevOps] Scaling organizational structure with Meshery’s expanding

#### 개요

As a high velocity project and one of the fastest-growing projects in the CNCF ecosystem, Meshery’s increasing scale and community contributions necessitates this recognition, which requires a revision to its governance and organizational structure that better.

**실무 포인트**: 인프라 및 운영 환경 영향을 검토하세요.

> **출처**: [CNCF Blog](https://www.cncf.io/blog/2026/03/04/scaling-organizational-structure-with-mesherys-expanding-ecosystem/)


#### 실무 적용 포인트

- Kubernetes 클러스터 보안 정책(PSP/PSA) 점검
- 네트워크 폴리시 및 RBAC 설정 최신화 확인
- 커뮤니티 행사 참가를 통한 최신 보안 동향 파악


---

### 4.2 [DevOps] OSPOlogy Day Cloud Native at KubeCon + CloudNativeCon Europe

#### 개요

Peer mentoring and group discussions on cloud strategy management Cloud native management has matured quickly. Platform engineering is now a cross-organization product, supply chain security expectations continue to rise, and regulation has moved from a future.

**실무 포인트**: 인프라 및 운영 환경 영향을 검토하세요.

> **출처**: [CNCF Blog](https://www.cncf.io/blog/2026/03/04/ospology-day-cloud-native-at-kubecon-cloudnativecon-europe/)


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 5. 블록체인 뉴스

### 5.1 [블록체인] Crypto Firm Zerohash is Seeking US National Trust Bank Charter

#### 개요

Bitcoin Magazine Crypto Firm Zerohash is Seeking US National Trust Bank Charter Digital asset infrastructure firm Zerohash has applied for a U.S. national trust bank charter to offer custody, staking, and payment services. This post Crypto Firm Zerohash is Seeking US National Trust Bank Charter first appeared on Bitcoin Magazine and is written by Micah Zimmerman.

**실무 포인트**: 가격 변동에 따른 보안 위협(피싱/스캠) 증가에 대비하세요.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/crypto-firm-zerohash-bank-charter)


---

### 5.2 [블록체인] Satlantis Emerges as Bitcoin-Native Alternative to Luma for Real-World

#### 개요

Bitcoin Magazine Satlantis Emerges as Bitcoin-Native Alternative to Luma for Real-World Events Satlantis positions itself as the direct Bitcoin-native alternative to Luma, embedding Lightning wallets for instant BTC payments, Nostr integration for portable data, and just 2% fees—outpacing Luma's rumored Solana ties and higher costs.

**실무 포인트**: 가격 변동에 따른 보안 위협(피싱/스캠) 증가에 대비하세요.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/business/satlantis-emerges-as-bitcoin-native-alternative-to-luma-for-real-world-events)


---

### 5.3 [블록체인] Bitwise to Donate $233,000 to Bitcoin Open-Source Developers

#### 개요

Bitcoin Magazine Bitwise to Donate $233,000 to Bitcoin Open-Source Developers Bitwise said it will be contributing $233,000 to support the programmers who maintain and secure the Bitcoin network. This post Bitwise to Donate $233,000 to Bitcoin Open-Source Developers first appeared on Bitcoin Magazine and is written by Micah Zimmerman.

**실무 포인트**: 가격 변동에 따른 보안 위협(피싱/스캠) 증가에 대비하세요.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/bitwise-to-donate-233000-to-bitcoin-comm)


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [새로운 Flash를 구축하기](https://news.hada.io/topic?id=27210) | GeekNews (긱뉴스) | C# , Avalonia , SkiaSharp 로 개발된 차세대 2D 애니메이션 저작 도구 로, Flash의 기능을 현대적으로 재구현 Linux, Mac, PC 에서 모두 동작하며, 타임라인·벡터 |
| [Google Workspace CLI — Drive, Gmail, Calendar, Sheets, Docs, Chat, Admin 등을 위한 통합 명령줄 도구](https://news.hada.io/topic?id=27209) | GeekNews (긱뉴스) | Google Workspace API 전체를 단일 CLI로 제어 할 수 있는 도구로, Drive·Gmail·Calendar·Sheets·Docs·Chat·Admin 등을 지원 Google Discovery |
| [Qwen의 땅에서 무언가 일어나고 있다](https://news.hada.io/topic?id=27207) | GeekNews (긱뉴스) | Alibaba의 Qwen 팀 핵심 연구진이 대거 사임 하면서, 최근 공개된 Qwen 3.5 모델 시리즈 의 향후가 불투명해짐 팀 리더 Lin Junyang 이 사임을 발표했고, 이어 여러 핵심 인력들이 동반 퇴사 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 13건 | 2025 ISO and CSA STAR, 149 Hacktivist DDoS Attacks Hit, Coruna iOS Exploit Kit Uses |
| **Cloud Security** | 4건 | 2025 ISO and CSA STAR, How Ricoh built a scalable, The rise of the autonomous |
| **Container/K8s** | 2건 | H4D VMs, now GA, deliver, The AI-native core: Highly resilient |
| **Authentication** | 2건 | Embed Amazon Quick Suite chat, H4D VMs, now GA, deliver |

이번 주기의 핵심 트렌드는 **AI/ML**(13건)입니다. 2025 ISO and CSA STAR, 149 Hacktivist DDoS Attacks Hit 등이 주요 이슈입니다. **Cloud Security** 분야에서는 2025 ISO and CSA STAR, How Ricoh built a scalable 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **[보안] Enhanced access denied error messages with policy** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **[보안] Coruna iOS Exploit Kit Uses 23 Exploits Across Five Chains Targeting** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **[AI] Use Canvas in AI Mode to get things done and bring your** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사

---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
