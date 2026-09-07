---
layout: post
title: "2026년 09월 07일 주간 보안 다이제스트: 패치·악성코드·AI 에이전트 (20건)"
date: 2026-09-07 17:20:24 +0900
last_modified_at: 2026-09-07T17:20:24+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Patch, Go, GPT, Update]
excerpt: "N-able, 지속되는 공격 속 N-central 최대 심각도 · 리눅스 환경의 루트킷 Syslogk 탐지 및 치료를 비롯한 2026년 09월 07일 보안/기술 동향 20건을 DevSecOps 시선으로 정리합니다. 보안 운영센터(SOC)와 DevSecOps 팀이 즉시 적용할 수 있는 차단·완화 조치를 요약합니다."
description: "2026년 09월 07일 보안 뉴스 요약. BleepingComputer, 안랩 ASEC 블로그, The Hacker News 등 20건을 분석하고 N-able, 지속되는 공격 속, 리눅스 환경의 루트킷 Syslogk 탐지 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Patch, Go, GPT]
author: Twodragon
comments: true
image: /assets/images/2026-09-07-Tech_Security_Weekly_Digest_Patch_Go_GPT_Update.svg
image_alt: "N-able, Syslogk, ChatGPT Astra 20 Plus - security digest overview"
toc: true
summary_card:
  title: "2026년 09월 07일 주간 보안 다이제스트: 패치·악성코드·AI 에이전트 (20건)"
  period: "2026년 09월 07일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Patch"
    - "Go"
    - "GPT"
    - "Update"
    - "2026"
  highlights:
    - { source: "BleepingComputer", title: "N-able, 지속되는 공격 속 N-central 최대 심각도 취약점 패치" }
    - { source: "안랩 ASEC 블로그", title: "리눅스 환경의 루트킷 Syslogk 탐지 및 치료" }
    - { source: "BleepingComputer", title: "ChatGPT Astra가 20달러 Plus 구독에 제공됩니다." }
    - { source: "AWS Korea Blog", title: "AI Agent를 위한 OpenSearch 검색 품질 개선하기 (Part 2)" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 09월 07일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 20개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 2개
- **클라우드 뉴스**: 3개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | BleepingComputer | N-able, 지속되는 공격 속 N-central 최대 심각도 취약점 패치 | 🔴 Critical |
| 🔒 **Security** | 안랩 ASEC 블로그 | Linux 환경의 루트킷 Syslogk 탐지 및 치료 | 🟠 High |
| 🔒 **Security** | BleepingComputer | ChatGPT Astra가 20달러 Plus 구독에 제공됩니다. | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | 우크라이나의 독립 저널리즘 지원 | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | 외계인의 마음 | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | AI Agent를 위한 OpenSearch 검색 품질 개선하기 (Part 2) | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | 채널코퍼레이션의 Amazon DynamoDB와 함께한 아키텍처 현대화 여정 – 3부 | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | 가격 예측부터 입찰 전략까지, LG에너지솔루션의 Amazon Bedrock AgentCore 기반 ERCOT 분석 에이전트 구축기 | 🟡 Medium |
| ⛓️ **Blockchain** | Bitcoin Magazine | 추정 화이트햇 해커들, Blockstream의 Liquid Network Federation 준비금에서 4,000 Bitcoin 인출 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | Fomo, Solana에서 Pump.fun의 일일 수익 추월 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: N-able, 지속되는 공격 속 N-central 최대 심각도 취약점 패치 등 Critical 등급 위협 1건이 확인되었습니다.
- **주요 모니터링 대상**: Linux 환경의 루트킷 Syslogk 탐지 및 치료 등 High 등급 위협 1건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 분석가 시점

현장 운영 관점에서 보면, 이번 주기는 **공급망 관리와 Linux 커널 심층 방어**의 중요성을 뼈저리게 상기시킵니다. N-able의 치명적인 취약점은 핵심 IT 운영 관리 도구의 신뢰 붕괴 시 파급력을, Syslogk 루트킷은 운영체제 코어 레벨 위협의 상시 존재를 강력히 경고합니다. DevSecOps 실무자는 단순히 긴급 패치를 적용하는 수동적 대응을 넘어, eBPF 기반의 실시간 무결성 감시 및 강화된 접근 제어 등 능동적인 심층 방어 체계 구축에 집중해야 합니다. ChatGPT Astra 같은 AI 모델 확산은 새로운 효율과 동시에 데이터 유출 및 악용 시나리오에 대한 선제적 보안 검토를 요구합니다. 따라서 이번 주기에 가장 먼저 봐야 할 신호는 **핵심 인프라에 대한 종합적인 심층 방어 체계 구축 및 지속적인 위협 탐지 역량 강화**입니다.

## 1. 보안 뉴스

### 1.1 N-able, 지속되는 공격 속 N-central 최대 심각도 취약점 패치

{% include news-card.html
  title="N-able, 지속되는 공격 속 N-central 최대 심각도 취약점 패치"
  url="https://www.bleepingcomputer.com/news/security/n-able-patches-max-severity-n-central-flaw-amid-ongoing-attacks/"
  image="https://www.bleepstatic.com/content/hl-images/2026/09/07/N-able-headpic.jpg"
  summary="N-able이 자사 N-central 원격 모니터링 및 관리(RMM) 플랫폼에 영향을 미치는 최대 심각도의 원격 코드 실행(RCE) 취약점에 대한 긴급 핫픽스를 공개했습니다. 이는 현재 진행 중인 공격 속에서 해당 취약점에 대응하기 위한 조치입니다."
  source="BleepingComputer"
  severity="Critical"
%}

#### N-able N-central RCE 취약점 패치: DevSecOps 분석

1.  **기술 배경**
    N-able N-central RMM 플랫폼에서 원격 코드 실행(RCE) 취약점(최고 심각도)이 발견되어 긴급 패치가 배포되었습니다. 공격자가 이를 악용하면 시스템을 완전히 장악할 수 있습니다. 이는 제로데이 또는 활발한 악용 가능성을 시사합니다.

2.  **실무 영향**
    N-central을 사용하는 MSP(Managed Service Provider)의 고객 시스템들이 연쇄적으로 위험에 노출될 수 있습니다. RMM 도구를 통한 광범위한 제어권 상실 우려가 있으며, 이는 심각한 데이터 유출 및 서비스 중단으로 이어집니다.

3.  **체크리스트**
    - N-able N-central 긴급 패치 즉시 적용 및 배포 검증
    - RMM 공급망 보안(Software Supply Chain Security) 위협 모델링 및 대응 계획 수립
    - EDR/SIEM 통한 N-central 관련 비정상 행위 및 공격 흔적 모니터링 강화
    - 주기적인 서드파티 SW 취약점 관리(SCA) 정책 운영

4.  **MITRE ATT&CK**
    *   **초기 접근 (Initial Access):** T1190 (Exploitation of Public-Facing Application)
    *   **실행 (Execution):** T1059 (Command and Scripting Interpreter)


---

### 1.2 Linux 환경의 루트킷 Syslogk 탐지 및 치료

{% include news-card.html
  title="Linux 환경의 루트킷 Syslogk 탐지 및 치료"
  url="https://asec.ahnlab.com/ko/95253/"
  image="https://asec.ahnlab.com/wp-content/uploads/2026/09/6z3bwo8UMloeOd71apEs8uuztb4QqdR6erZJdFQm.webp"
  summary="Syslogk는 악성코드와 침해 흔적을 숨기기 위해 Linux 커널을 변조하는 방식으로 동작하는 루트킷입니다. AhnLab Security intelligence Center(ASEC)은 이 루트킷의 기능과 동작 방식을 분석하고 이를 바탕으로 탐지 및 치료 방안을 마련했습니다."
  source="안랩 ASEC 블로그"
  severity="High"
%}

#### Syslogk 루트킷 DevSecOps 분석
1.  **기술 배경**
    Syslogk는 Linux 커널을 변조, 악성코드 및 침해 흔적을 은폐하는 루트킷입니다. 이는 기존 보안 솔루션 탐지를 회피하며 시스템 무결성을 심각하게 훼손합니다.
2.  **실무 영향**
    CI/CD 빌드/배포 서버, 컨테이너 런타임 환경, 클라우드 워크로드에 영향을 줍니다. EDR/XDR, SIEM, 컨테이너 보안 솔루션의 탐지 능력 강화가 필수입니다.
3.  **체크리스트**
    - 커널 무결성 모니터링 및 실시간 위협 탐지 강화.
    - CI/CD 내 OS/커널 취약점 스캐닝 자동화.
    - 컨테이너/워크로드별 최소 권한 원칙 적용.
    - 행위 기반 이상 징후 분석 솔루션 도입.
4.  **MITRE ATT&CK**
    TA0005 (Defense Evasion): T1014 (Rootkit), T1070 (Indicator Removal). TA0003 (Persistence).


---

### 1.3 ChatGPT Astra가 20달러 Plus 구독에 제공됩니다.

{% include news-card.html
  title="ChatGPT Astra가 20달러 Plus 구독에 제공됩니다."
  url="https://www.bleepingcomputer.com/news/artificial-intelligence/chatgpt-astra-is-now-rolling-out-to-20-plus-subscription/"
  image="https://www.bleepstatic.com/content/hl-images/2023/03/24/ChatGPT-logo.jpg"
  summary="OpenAI가 자사의 가장 강력한 모델인 ChatGPT Astra를 월 20달러의 Plus 구독자들에게 배포하기 시작했습니다. 하지만 무료 사용자들의 접근 시기에 대해서는 아직 알려진 바가 없습니다."
  source="BleepingComputer"
  severity="Medium"
%}

#### 요약

OpenAI가 자사의 가장 강력한 모델인 ChatGPT Astra를 월 20달러의 Plus 구독자들에게 배포하기 시작했습니다. 하지만 무료 사용자들의 접근 시기에 대해서는 아직 알려진 바가 없습니다.


#### 권장 조치

- 관련 시스템 목록 확인 및 자사 환경 해당 여부 평가
- 벤더 보안 권고 확인 후 패치 또는 완화 조치 적용
- SIEM/EDR 탐지 룰에 관련 IoC 추가
- 보안팀 내 공유 및 모니터링 강화


---

## 2. AI/ML 뉴스

### 2.1 우크라이나의 독립 저널리즘 지원

{% include news-card.html
  title="우크라이나의 독립 저널리즘 지원"
  url="https://openai.com/index/supporting-independent-journalism-in-ukraine"
  summary="OpenAI, AIRPPU, WAN-IFRA는 우크라이나 뉴스 기관을 지원하기 위한 AI 프로그램을 시작했습니다. 이 프로그램은 이들의 혁신, 회복력, 독립 저널리즘을 강화하는 데 기여할 것입니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

OpenAI, AIRPPU, WAN-IFRA는 우크라이나 뉴스 기관을 지원하기 위한 AI 프로그램을 시작했습니다. 이 프로그램은 이들의 혁신, 회복력, 독립 저널리즘을 강화하는 데 기여할 것입니다.


---

### 2.2 외계인의 마음

{% include news-card.html
  title="외계인의 마음"
  url="https://openai.com/index/an-alien-mind"
  summary="야쿠프 파초키는 점점 더 강력해지는 인공지능과 이를 인간의 가치에 부합하도록 유지하는 것의 어려움에 대해 성찰합니다. 그는 더 강력한 안전장치 마련과 국제적 공조를 촉구했습니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

야쿠프 파초키는 점점 더 강력해지는 인공지능과 이를 인간의 가치에 부합하도록 유지하는 것의 어려움에 대해 성찰합니다. 그는 더 강력한 안전장치 마련과 국제적 공조를 촉구했습니다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 AI Agent를 위한 OpenSearch 검색 품질 개선하기 (Part 2)

{% include news-card.html
  title="AI Agent를 위한 OpenSearch 검색 품질 개선하기 (Part 2)"
  url="https://aws.amazon.com/ko/blogs/tech/evaluate-ai-agent-search-quality-with-amazon-opensearch-service-2/"
  summary="이 글은 AI 에이전트를 위한 OpenSearch 검색 품질을 개선하는 방법을 다룬다. 이전 측정 결과를 바탕으로 Rerank와 Weight 튜닝 등 실제 품질을 높이는 구체적인 방안을 제시한다."
  source="AWS Korea Blog"
  severity="Medium"
%}

#### 요약

이 글은 AI 에이전트를 위한 OpenSearch 검색 품질을 개선하는 방법을 다룬다. 이전 측정 결과를 바탕으로 Rerank와 Weight 튜닝 등 실제 품질을 높이는 구체적인 방안을 제시한다.


---

### 3.2 채널코퍼레이션의 Amazon DynamoDB와 함께한 아키텍처 현대화 여정 – 3부

{% include news-card.html
  title="채널코퍼레이션의 Amazon DynamoDB와 함께한 아키텍처 현대화 여정 – 3부"
  url="https://aws.amazon.com/ko/blogs/tech/how-channel-corporation-modernized-their-architecture-with-amazon-dynamodb-part-3-user-and-badge/"
  summary="채널코퍼레이션은 올인원 AI 메신저 '채널톡'을 운영하는 B2B SaaS 스타트업으로, 빠르게 성장하는 비즈니스를 위해 Amazon DynamoDB를 활용하고 있습니다. 이 블로그 시리즈는 채널코퍼레이션이 Amazon DynamoDB의 수평 확장성과 ACID 트랜잭션 등 강력한 기능을 활용하여 아키텍처를 현대화하는 과정을 상세히 다룹니다"
  source="AWS Korea Blog"
  severity="Medium"
%}

#### 요약

채널코퍼레이션은 올인원 AI 메신저 ‘채널톡’을 운영하는 B2B SaaS 스타트업으로, 빠르게 성장하는 비즈니스를 위해 Amazon DynamoDB를 활용하고 있습니다. 이 블로그 시리즈는 채널코퍼레이션이 Amazon DynamoDB의 수평 확장성과 ACID 트랜잭션 등 강력한 기능을 활용하여 아키텍처를 현대화하는 과정을 상세히 다룹니다


---

### 3.3 가격 예측부터 입찰 전략까지, LG에너지솔루션의 Amazon Bedrock AgentCore 기반 ERCOT 분석 에이전트 구축기

{% include news-card.html
  title="가격 예측부터 입찰 전략까지, LG에너지솔루션의 Amazon Bedrock AgentCore 기반 ERCOT 분석 에이전트 구축기"
  url="https://aws.amazon.com/ko/blogs/tech/lg-energy-solution-price-prediction-agent/"
  summary="LG에너지솔루션은 Amazon Bedrock AgentCore를 기반으로 ERCOT 분석 에이전트를 구축하여 실시간으로 변동하는 전력시장에서 가격 예측과 입찰 전략 분석을 가능하게 했습니다. 이 에이전트는 전력거래 솔루션의 핵심 기능으로, 급변하는 시장에서 ESS를 활용해 최대 수익을 창출하는 데 기여할 예정입니다."
  source="AWS Korea Blog"
  severity="Medium"
%}

#### 요약

LG에너지솔루션은 Amazon Bedrock AgentCore를 기반으로 ERCOT 분석 에이전트를 구축하여 실시간으로 변동하는 전력시장에서 가격 예측과 입찰 전략 분석을 가능하게 했습니다. 이 에이전트는 전력거래 솔루션의 핵심 기능으로, 급변하는 시장에서 ESS를 활용해 최대 수익을 창출하는 데 기여할 예정입니다.


---

## 4. 블록체인 뉴스

### 4.1 추정 화이트햇 해커들, Blockstream의 Liquid Network Federation 준비금에서 4,000 Bitcoin 인출

{% include news-card.html
  title="추정 화이트햇 해커들, Blockstream의 Liquid Network Federation 준비금에서 4,000 Bitcoin 인출"
  url="https://bitcoinmagazine.com/news/alleged-white-hat-hackers-withdraw-4000-bitcoin-from-blockstreams-liquid-network-federation-reserves"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/09/tn.webp"
  summary="리퀴드 네트워크는 자칭 화이트햇 해커들이 L-BTC를 지원하는 연합 지갑에서 약 4,000 Bitcoin을 인출했다고 밝혔습니다. 이에 따라 브리지 노드가 비활성화되고 사이드체인이 일시 중지된 상태입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

리퀴드 네트워크는 자칭 화이트햇 해커들이 L-BTC를 지원하는 연합 지갑에서 약 4,000 Bitcoin을 인출했다고 밝혔습니다. 이에 따라 브리지 노드가 비활성화되고 사이드체인이 일시 중지된 상태입니다.


---

### 4.2 Fomo, Solana에서 Pump.fun의 일일 수익 추월

{% include news-card.html
  title="Fomo, Solana에서 Pump.fun의 일일 수익 추월"
  url="https://cointelegraph.com/news/fomo-pumpfun-revenue-app-solana?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/09/01M1XA5XHGVP1S4E8DGH0JJ4XZ/sponsor-screen-traid2.jpg"
  summary="솔라나 기반의 Fomo가 금요일 일일 수익에서 Pump.fun을 앞질렀습니다. Fomo는 이날 176만 달러를 벌어들여 110만 달러를 기록한 Pump.fun을 제쳤지만, 30일 누적 수익에서는 Pump.fun이 여전히 우위를 지키고 있습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

솔라나 기반의 Fomo가 금요일 일일 수익에서 Pump.fun을 앞질렀습니다. Fomo는 이날 176만 달러를 벌어들여 110만 달러를 기록한 Pump.fun을 제쳤지만, 30일 누적 수익에서는 Pump.fun이 여전히 우위를 지키고 있습니다.


---

### 4.3 소위 화이트햇의 BTC 3.2억 달러 인출로 Bitcoin 사이드체인 Liquid 중단

{% include news-card.html
  title="소위 화이트햇의 BTC 3.2억 달러 인출로 Bitcoin 사이드체인 Liquid 중단"
  url="https://cointelegraph.com/news/liquid-network-pauses-320m-bitcoin-withdrawal?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/09/01M1X62TPQZQS0CSZKDBXWAKDQ/btc.png"
  summary="Bitcoin 사이드체인 리퀴드가 '화이트햇'으로 알려진 행위자들이 3억 2천만 달러(4,000 BTC)를 인출한 후 일시 중단되었습니다. 이들은 엘리먼츠 취약점이 네트워크 전반에 걸쳐 패치되면 인출한 4,000 BTC의 대부분을 블록스트림에 반환하겠다고 밝혔습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

Bitcoin 사이드체인 리퀴드가 ‘화이트햇’으로 알려진 행위자들이 3억 2천만 달러(4,000 BTC)를 인출한 후 일시 중단되었습니다. 이들은 엘리먼츠 취약점이 네트워크 전반에 걸쳐 패치되면 인출한 4,000 BTC의 대부분을 블록스트림에 반환하겠다고 밝혔습니다.


---

## 5. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [카카오, if(kakao)26 컨퍼런스 개최... 모든 연결에 지능을](https://tech.kakao.com/posts/834) | 카카오 기술 블로그 | 카카오가 오는 10월 13일부터 14일까지 이틀간 용인 카카오 AI 캠퍼스에서 'if(kakao)26' 컨퍼런스를 온·오프라인으로 개최한다. 이 행사는 '모든 연결에 지능을'이라는 슬로건 아래, AI가 확장할 연결 경험과 신뢰할 수 있는 기술 기준을 논하며 50여 개 기술 세션에서 AI 적용 성과와 개발 경험을 공유할 예정이다 |
| [Show GN: yukari-rubi : 일본어 사이트 한자 히라가나 브라우저 확장기능](https://news.hada.io/topic?id=33315) | GeekNews (긱뉴스) | 이번에 Chrome 또한 지원하게 되어 글을 올립니다. Firefox 확장기능으로 소개했던, yukari-rubi입니다 |
| [Show GN: VIBE-GAME ( AI 에게 일 시키고 기다리면서 하기에 좋은 게임 )](https://news.hada.io/topic?id=33311) | GeekNews (긱뉴스) | 요즘 AI 로 개발을 진행하다 보니 작업 시켜두고 기다리기에 지루한 시간들이 자주 생기더라구요. 앱을 다운로드 해서 하자니 뭔가 번거롭기도 하고 광고에 시달리기도 귀찮고 구형 폰이라서 최신 게임도 잘 안 돌아가고 해서 심심풀이로 Codex Sol Max 로 그냥 개발해보라고 했는데 퀄리티가 나름 등이 확인되었습니다 |


---

## 6. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 13건 | 기타 주제 |
| **AI/ML** | 1건 | AI Agent를 위한 OpenSearch 검색 품질 개선하기 (Part |
| **인증 보안** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(13건)입니다. **AI/ML** 분야에서는 AI Agent를 위한 OpenSearch 검색 품질 개선하기 (Part 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **N-able, 지속되는 공격 속 N-central 최대 심각도 취약점 패치** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **Linux 환경의 루트킷 Syslogk 탐지 및 치료** 관련 보안 검토 및 모니터링
- [ ] **공격자들, 인증 없이 인터넷 노출 SSH 통해 MikroTik 라우터 장악** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **우크라이나의 독립 저널리즘 지원** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
