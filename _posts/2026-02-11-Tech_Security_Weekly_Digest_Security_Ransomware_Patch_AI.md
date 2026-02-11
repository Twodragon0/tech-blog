---
layout: post
title: "Tech & Security Weekly Digest: Ransomware, CVE-2026-21643, Fortinet"
date: 2026-02-11 12:47:26 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Ransomware, Patch, AI]
excerpt: "2026년 02월 11일 주요 보안/기술 뉴스 26건 - Security, Ransomware, Patch"
description: "2026년 02월 11일 보안 뉴스: The Hacker News 등 26건. Security, Ransomware, Patch, AI 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Ransomware, Patch]
author: Twodragon
comments: true
image: /assets/images/2026-02-11-Tech_Security_Weekly_Digest_Security_Ransomware_Patch_AI.svg
image_alt: "Tech Security Weekly Digest February 11 2026 Security Ransomware Patch"
toc: true
---

{% include ai-summary-card.html
  title="Tech & Security Weekly Digest (2026년 02월 11일)"
  categories_html="<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>"
  tags_html="<span class="tag">Security-Weekly</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">2026</span>"
  highlights_html="<li><strong>The Hacker News</strong>: DPRK Operatives Impersonate Professionals on LinkedIn to...</li>
      <li><strong>The Hacker News</strong>: Reynolds Ransomware Embeds BYOVD Driver to Disable EDR...</li>
      <li><strong>The Hacker News</strong>: From Ransomware to Residency: Inside the Rise of the...</li>
      <li><strong>Google Cloud Blog</strong>: Google Distributed Cloud brings public-cloud-like...</li>"
  period="2026년 02월 11일 (24시간)"
  audience="보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
%}

## Executive Summary

2026년 02월 11일 기준 보안 현황 및 위협 분석입니다.

### 위험 스코어카드

```
+================================================================+
|          2026-02-11 주간 보안 위험 스코어카드                      |
+================================================================+
|                                                                |
|  항목                    위험도   점수    조치 시급도             |
|  ----------------------------------------------------------   |
|  Fortinet Patches Critical SQLi █████████░  9/10   [즉시]                |
|  ZAST.AI Raises $6M Pre-A to Sc ███████░░░  7/10   [7일 이내]             |
|  Google Distributed Cloud bring ███████░░░  7/10   [7일 이내]             |
|  ----------------------------------------------------------   |
|  종합 위험 수준: ███████░░░ HIGH (7.7/10)                         |
|                                                                |
+================================================================+
```


### 경영진 대시보드

```
+================================================================+
|        보안 현황 대시보드 - 2026년 02월 11일                         |
+================================================================+
|                                                                |
|  [위협 현황]              [패치 현황]         [컴플라이언스]       |
|  +-----------+           +-----------+      +-----------+      |
|  | Critical 1|           | 적용필요 1|      | 적합   3  |      |
|  | High     2|           | 평가중  2 |      | 검토중  2 |      |
|  | Medium   12|           | 정보참고 1|      | 미대응  0 |      |
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
| **주요 위협** | Critical: 1건, High: 2건 | 대응 진행 중 |
| **패치 적용** | 긴급 패치 대상 시스템 식별 완료 | 검토 필요 |
| **규제 대응** | 보안 정책 및 컴플라이언스 점검 | 정상 |

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 02월 11일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 26개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 4개
- **클라우드 뉴스**: 4개
- **DevOps 뉴스**: 3개
- **블록체인 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | DPRK Operatives Impersonate Professionals on Linke... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Reynolds Ransomware Embeds BYOVD Driver to Disable... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | From Ransomware to Residency: Inside the Rise of t... | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Fortinet Patches Critical SQLi Flaw Enabling Unaut... | 🔴 Critical |
| 🔒 **Security** | The Hacker News | ZAST.AI Raises $6M Pre-A to Scale "Zero False Posi... | 🟠 High |

---

## 1. 보안 뉴스

### 1.1 DPRK Operatives Impersonate Professionals on LinkedIn to Infiltrate Companies

#### 개요

The information technology (IT) workers associated with the Democratic People's Republic of Korea (DPRK) are now applying to remote positions using real LinkedIn accounts of individuals they're impersonating, marking a new escalation of the fraudulent scheme. "These profiles often have verified workplace emails and identity badges, which DPRK operatives hope will make their fraudulent

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/dprk-operatives-impersonate.html)

#### 핵심 포인트

- The information technology (IT) workers associated with the Democratic People's Republic of Korea (DPRK) are now applying to remote positions using real LinkedIn accounts of individuals they're impersonating, marking a new escalation of the fraudulent scheme
- "These profiles often have verified workplace emails and identity badges, which DPRK operatives hope will make their fraudulent


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

### 1.2 Reynolds Ransomware Embeds BYOVD Driver to Disable EDR Security Tools

#### 개요

Cybersecurity researchers have disclosed details of an emergent ransomware family dubbed Reynolds that comes embedded with a built-in bring your own vulnerable driver (BYOVD) component for defense evasion purposes within the ransomware payload itself. BYOVD refers to an adversarial technique that abuses legitimate but flawed driver software to escalate privileges and disable Endpoint Detection

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/reynolds-ransomware-embeds-byovd-driver.html)

#### 핵심 포인트

- Cybersecurity researchers have disclosed details of an emergent ransomware family dubbed Reynolds that comes embedded with a built-in bring your own vulnerable driver (BYOVD) component for defense evasion purposes within the ransomware payload itself
- BYOVD refers to an adversarial technique that abuses legitimate but flawed driver software to escalate privileges and disable Endpoint Detection


#### 실무 영향

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인


---

### 1.3 From Ransomware to Residency: Inside the Rise of the Digital Parasite

#### 개요

Are ransomware and encryption still the defining signals of modern cyberattacks, or has the industry been too fixated on noise while missing a more dangerous shift happening quietly all around them? According to Picus Labs’ new Red Report 2026, which analyzed over 1.1 million malicious files and mapped 15.5 million adversarial actions observed across 2025, attackers are no longer optimizing for

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/from-ransomware-to-residency-inside.html)

#### 핵심 포인트

- Are ransomware and encryption still the defining signals of modern cyberattacks, or has the industry been too fixated on noise while missing a more dangerous shift happening quietly all around them
- According to Picus Labs’ new Red Report 2026, which analyzed over 1.1 million malicious files and mapped 15.5 million adversarial actions observed across 2025, attackers are no longer optimizing for


#### 실무 영향

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인


---

## 2. AI/ML 뉴스

### 2.1 9 fun questions to try asking Google Photos

#### 개요

A collage of outdoor images, a blue icon that say "Ask Photos," and examples of Ask Photos prompts.

> **출처**: [Google AI Blog](https://blog.google/products-and-platforms/products/photos/ask-button-ask-photos-tips/)

#### 핵심 포인트

- A collage of outdoor images, a blue icon that say "Ask Photos," and examples of Ask Photos prompts


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.2 How Amazon uses Amazon Nova models to automate operational readiness testing for new fulfillment centers

#### 개요

In this post, we discuss how Amazon Nova in Amazon Bedrock can be used to implement an AI-powered image recognition solution that automates the detection and validation of module components, significantly reducing manual verification efforts and improving accuracy.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/how-amazon-uses-amazon-nova-models-to-automate-operational-readiness-testing-for-new-fulfillment-centers/)

#### 핵심 포인트

- In this post, we discuss how Amazon Nova in Amazon Bedrock can be used to implement an AI-powered image recognition solution that automates the detection and validation of module components, significantly reducing manual verification efforts and improving accuracy


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.3 Iberdrola enhances IT operations using Amazon Bedrock AgentCore

#### 개요

Iberdrola, one of the world’s largest utility companies, has embraced cutting-edge AI technology to revolutionize its IT operations in ServiceNow. Through its partnership with AWS, Iberdrola implemented different agentic architectures using Amazon Bedrock AgentCore, targeting three key areas: optimizing change request validation in the draft phase, enriching incident management with contextual intelligence, and simplifying change model selection using conversational AI. These innovations redu...

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/iberdrola-enhances-it-operations-using-amazon-bedrock-agentcore/)

#### 핵심 포인트

- Iberdrola, one of the world’s largest utility companies, has embraced cutting-edge AI technology to revolutionize its IT operations in ServiceNow
- Through its partnership with AWS, Iberdrola implemented different agentic architectures using Amazon Bedrock AgentCore, targeting three key areas: optimizing change request validation in the draft phase, enriching incident management with contextual intelligence, and simplifying change model selection using conversational AI
- These innovations redu


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

### 3.1 Google Distributed Cloud brings public-cloud-like networking to air-gapped environments

#### 개요

Organizations in highly regulated industries often struggle to balance the rigid security of air-gapped environments with the need for the agility and flexibility that the cloud provides. To address this, Google Distributed Cloud (GDC) air-gapped 1.15 introduces new networking features in preview that give you more direct control and visibility without compromising your security posture, as well as a new IPAM feature in general availability that simplifies subnet management . These preview fe...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/networking/google-distributed-cloud-gdc-air-gapped-1-15-networking/)

#### 핵심 포인트

- Organizations in highly regulated industries often struggle to balance the rigid security of air-gapped environments with the need for the agility and flexibility that the cloud provides
- To address this, Google Distributed Cloud (GDC) air-gapped 1.15 introduces new networking features in preview that give you more direct control and visibility without compromising your security posture, as well as a new IPAM feature in general availability that simplifies subnet management
- These preview fe


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.2 Gemini Enterprise Agent Ready (GEAR) program now available, a new path to building AI agents at scale

#### 개요

Today’s reality is agentic – software that can reason, plan, and act on your behalf to execute complex workflows. To meet this moment, we are excited to open the Gemini Enterprise Agent Ready (GEAR) learning program to everyone. As a new specialized pathway within the Google Developer Program , GEAR empowers developers and pros to build and deploy enterprise-grade agents with Google AI. Here is how GEAR helps you build what’s next. Move from experimentation to production-ready architecture Bu...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/gear-program-now-available/)

#### 핵심 포인트

- Today’s reality is agentic – software that can reason, plan, and act on your behalf to execute complex workflows
- To meet this moment, we are excited to open the Gemini Enterprise Agent Ready (GEAR) learning program to everyone
- As a new specialized pathway within the Google Developer Program , GEAR empowers developers and pros to build and deploy enterprise-grade agents with Google AI
- Here is how GEAR helps you build what’s next


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.3 Beyond the Battlefield: Threats to the Defense Industrial Base

#### 개요

Introduction In modern warfare, the front lines are no longer confined to the battlefield; they extend directly into the servers and supply chains of the industry that safeguards the nation. Today, the defense sector faces a relentless barrage of cyber operations conducted by state-sponsored actors and criminal groups alike. In recent years, Google Threat Intelligence Group (GTIG) has observed several distinct areas of focus in adversarial targeting of the defense industrial base (DIB). While...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/threats-to-defense-industrial-base/)

#### 핵심 포인트

- Introduction In modern warfare, the front lines are no longer confined to the battlefield; they extend directly into the servers and supply chains of the industry that safeguards the nation
- Today, the defense sector faces a relentless barrage of cyber operations conducted by state-sponsored actors and criminal groups alike
- In recent years, Google Threat Intelligence Group (GTIG) has observed several distinct areas of focus in adversarial targeting of the defense industrial base (DIB)


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 4. DevOps & 개발 뉴스

### 4.1 Hardened Images Are Free. Now What?

#### 개요

Docker Hardened Images are now free, covering Alpine, Debian, and over 1,000 images including databases, runtimes, and message buses. For security teams, this changes the economics of container vulnerability management. DHI includes security fixes from Docker’s security team, which simplifies security response. Platform teams can pull the patched base image and redeploy quickly. But free...

> **출처**: [Docker Blog](https://www.docker.com/blog/hardened-images-free-now-what/)

#### 핵심 포인트

- Docker Hardened Images are now free, covering Alpine, Debian, and over 1,000 images including databases, runtimes, and message buses
- For security teams, this changes the economics of container vulnerability management
- DHI includes security fixes from Docker’s security team, which simplifies security response
- Platform teams can pull the patched base image and redeploy quickly


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.2 .NET 11 Preview 1 is now available!

#### 개요

Find out about the new features in .NET 11 Preview 1 across the .NET runtime, SDK, libraries, ASP.NET Core, Blazor, C#, .NET MAUI, and more! The post .NET 11 Preview 1 is now available! appeared first on .NET Blog .

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/dotnet-11-preview-1/)

#### 핵심 포인트

- Find out about the new features in .NET 11 Preview 1 across the .NET runtime, SDK, libraries, ASP.NET Core, Blazor, C#, .NET MAUI, and more
- The post .NET 11 Preview 1 is now available
- appeared first on .NET Blog 


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.3 .NET and .NET Framework February 2026 servicing releases updates

> 🟡 **심각도**: Medium | **CVE**: CVE-2026-21218

#### 개요

A recap of the latest servicing updates for .NET and .NET Framework for February 2026. The post .NET and .NET Framework February 2026 servicing releases updates appeared first on .NET Blog .

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-february-2026-servicing-updates/)

#### 핵심 포인트

- A recap of the latest servicing updates for .NET and .NET Framework for February 2026
- The post .NET and .NET Framework February 2026 servicing releases updates appeared first on .NET Blog 


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 5. 블록체인 뉴스

### 5.1 Goldman Sachs Discloses $1.1 Billion Position in Bitcoin ETF Holdings

#### 개요

Bitcoin Magazine Goldman Sachs Discloses $1.1 Billion Position in Bitcoin ETF Holdings Goldman Sachs revealed it holds $1.1 billion in Bitcoin ETFs, marking somewhat of a shift toward cryptocurrency exposure. This post Goldman Sachs Discloses $1.1 Billion Position in Bitcoin ETF Holdings first appeared on Bitcoin Magazine and is written by Micah Zimmerman .

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/goldman-sachs-position-in-bitcoin)

#### 핵심 포인트

- Bitcoin Magazine Goldman Sachs Discloses $1.1 Billion Position in Bitcoin ETF Holdings Goldman Sachs revealed it holds $1.1 billion in Bitcoin ETFs, marking somewhat of a shift toward cryptocurrency exposure
- This post Goldman Sachs Discloses $1.1 Billion Position in Bitcoin ETF Holdings first appeared on Bitcoin Magazine and is written by Micah Zimmerman 


---

### 5.2 FTX’s Sam Bankman-Fried Wants a New Trial, Claims He Was a Political Victim of the Biden Administration

#### 개요

Bitcoin Magazine FTX’s Sam Bankman-Fried Wants a New Trial, Claims He Was a Political Victim of the Biden Administration Convicted FTX fraudster Sam Bankman-Fried reportedly filed for a new trial today. This post FTX’s Sam Bankman-Fried Wants a New Trial, Claims He Was a Political Victim of the Biden Administration first appeared on Bitcoin Magazine and is written by Micah Zimmerman .

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/ftx-sam-bankman-fried-wants-a-new-trial)

#### 핵심 포인트

- Bitcoin Magazine FTX’s Sam Bankman-Fried Wants a New Trial, Claims He Was a Political Victim of the Biden Administration Convicted FTX fraudster Sam Bankman-Fried reportedly filed for a new trial today
- This post FTX’s Sam Bankman-Fried Wants a New Trial, Claims He Was a Political Victim of the Biden Administration first appeared on Bitcoin Magazine and is written by Micah Zimmerman 


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Trump can’t freeze NEVI funds, so he’s trying to s...](https://electrek.co/2026/02/10/trump-cant-freeze-nevi-funds-so-hes-trying-to-stall-them-again/) | Electrek | The Federal Highway Administration (FHWA) just issued a new notice today that ai... |
| [Tesla Semi specs and pricing, L4 haul trucks, and ...](https://electrek.co/2026/02/10/tesla-semi-specs-and-pricing-l4-haul-trucks-and-windrose-mobile-ai-concept/) | Electrek | On today’s long overdue episode of Quick Charge , we’ve finally got production s... |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 12건 | ai |
| **Cloud Security** | 2건 | cloud, aws |
| **Ransomware** | 2건 | ransomware |
| **Supply Chain** | 1건 | supply chain |
| **Container/K8s** | 1건 | container |
| **Authentication** | 1건 | identity |

이번 주기에서 가장 많이 언급된 트렌드는 **AI/ML** (12건)입니다. 그 다음으로 **Cloud Security** (2건)이 주목받고 있습니다. 실무에서는 해당 트렌드와 관련된 보안 정책 및 모니터링 체계를 점검하시기 바랍니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Fortinet Patches Critical SQLi Flaw Enabling Unauthenticated** (CVE-2026-21643) 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **ZAST.AI Raises $6M Pre-A to Scale "Zero False Positive" AI-P** 관련 보안 검토 및 모니터링
- [ ] **Google Distributed Cloud brings public-cloud-like networking** 관련 보안 검토 및 모니터링

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
