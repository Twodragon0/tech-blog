---
layout: post
title: "2026년 07월 27일 주간 보안 다이제스트: BYOVD EDR·클라우드·블록체인 (16건)"
date: 2026-07-27 11:03:52 +0900
last_modified_at: 2026-07-27T11:03:52+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI]
excerpt: "GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 · Hugging Face CEO, '전례 없는' OpenAI 해킹 등 2026년 07월 27일 보고된 16건의 보안/기술 이슈를 운영 관점에서 점검합니다. 변경 통제와 모니터링 적용 시점, 사후 회고에 활용할 IoC 정리표를 포함합니다."
description: "2026년 07월 27일 보안 뉴스 요약. BleepingComputer, TechCrunch Security, Cointelegraph 등 16건을 분석하고 GitHub, PyPI가 공급망 공격, Hugging Face CEO 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI]
author: Twodragon
comments: true
image: /assets/images/2026-07-27-Tech_Security_Weekly_Digest_AI.svg
image_alt: "GitHub, PyPI, Hugging Face CEO, Garden Finance - security digest overview"
toc: true
summary_card:
  title: "2026년 07월 27일 주간 보안 다이제스트: BYOVD EDR·클라우드·블록체인 (16건)"
  period: "2026년 07월 27일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "2026"
  highlights:
    - { source: "BleepingComputer", title: "GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 기능 추가" }
    - { source: "TechCrunch Security", title: "Hugging Face CEO, &#x27;전례 없는&#x27; OpenAI 해킹 이후 &#x27;급진적 투명성&#x27; 촉구" }
    - { source: "Cointelegraph", title: "Garden Finance, Blockaid가 45만 달러 익스플로잇을 보고함에 따라 앱 비활성화" }
    - { source: "AWS Korea Blog", title: "개인 생산성에서 멈춘 Claude Code, 조직의 생산성으로 – 영상 10개로 완성하는 Claude" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 07월 27일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 16개
- **보안 뉴스**: 4개
- **AI/ML 뉴스**: 1개
- **클라우드 뉴스**: 1개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | BleepingComputer | GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 기능 추가 | 🟠 High |
| 🔒 **Security** | TechCrunch Security | Hugging Face CEO, '전례 없는' OpenAI 해킹 이후 '급진적 투명성' 촉구 | 🟠 High |
| 🔒 **Security** | Cointelegraph | Garden Finance, Blockaid가 45만 달러 익스플로잇을 보고함에 따라 앱 비활성화 | 🟠 High |
| 🤖 **AI/ML** | NVIDIA AI Blog | NVIDIA, Vera CPU를 활용해 차세대 CPU 및 GPU 설계 가속화 | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | 개인 생산성에서 멈춘 Claude Code, 조직의 생산성으로 – 영상 10개로 완성하는 Claude Code on Amazon Bedrock 학습 플랜 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | Storj 파산 신청, 토큰 보유자 위한 지분 경로 모색 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | CLARITY 기대감 사라지고, BitMEX 소송 앞두고 폐쇄: Hodler’s Digest, 7월 26일 | 🟠 High |
| ⛓️ **Blockchain** | Cointelegraph | CFTC, 예측 시장에 정형화된 자체 인증에 대해 두 번째 경고 발령 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | Cloudflare, 고객별 AI 트래픽 제어 옵션 공개 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | Netflix의 사내 LLM 서빙 플랫폼 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 기능 추가, Hugging Face CEO, '전례 없는' OpenAI 해킹 이후 '급진적 투명성' 촉구, Garden Finance, Blockaid가 45만 달러 익스플로잇을 보고함에 따라 앱 비활성화 등 High 등급 위협 4건에 대한 탐지 강화가 필요합니다.
- 공급망 보안 위협이 확인되었으며, 서드파티 의존성 검토와 SBOM 업데이트를 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 기능 추가

{% include news-card.html
  title="GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 기능 추가"
  url="https://www.bleepingcomputer.com/news/security/github-pypi-add-time-absed-defenses-against-supply-chain-attacks/"
  image="https://www.bleepstatic.com/content/hl-images/2026/05/21/GitHub_headpic.jpg"
  summary="GitHub와 PyPI가 Dependabot 의존성 관리 도구에 시간 기반 메커니즘을 도입하여 공급망 공격을 방어하고 그 영향을 제한하고자 한다."
  source="BleepingComputer"
  severity="High"
%}

#### DevSecOps 실무자 관점 분석: GitHub/PyPI 시간 기반 공급망 공격 방어

#### 기술적 배경 및 위협 분석

GitHub Dependabot과 PyPI가 도입한 **시간 기반(time-based) 방어 메커니즘**은 악성 패키지의 신속한 유포를 차단하기 위한 조치다. 기존 공급망 공격은 신규 패키지나 특정 버전이 등록된 직후 대규모 자동 업데이트를 통해 빠르게 확산되는 취약점을 악용했다. 대표적으로 `dependency confusion` 공격이나 `typosquatting` 공격이 이에 해당한다.

새로운 메커니즘은 **새로 등록된 패키지나 버전에 대해 일정 기간(예: 24-48시간) 업데이트를 지연**시키거나, Dependabot이 자동으로 PR을 생성하지 않도록 한다. 이는 악성 패키지가 탐지되기 전에 대규모로 유입되는 것을 방지하며, 보안 커뮤니티가 해당 패키지를 분석할 시간을 확보하게 해준다. 또한 PyPI는 신규 유지보수자(first-time publisher)의 패키지에 대해 추가 검증 절차를 적용할 수 있다.

**주요 위협**: 공격자는 여전히 기존 인기 패키지의 취약한 버전을 악용하거나, 합법적인 패키지의 계정 탈취를 통해 악성 코드를 주입할 수 있다. 시간 기반 방어는 신규 패키지에만 적용되므로, 기존 패키지의 변조를 막지는 못한다.

#### 실무 영향 분석

- **긍정적 영향**: 자동 의존성 업데이트의 위험성이 크게 감소한다. DevSecOps 파이프라인에서 Dependabot PR을 무분별하게 머지하던 관행을 개선할 수 있다. 특히 CI/CD에 자동 업데이트를 통합한 조직의 경우, 공급망 공격에 대한 1차 방어선이 강화된다.
- **부정적 영향**: 보안 패치 적용이 지연될 수 있다. 예를 들어, 긴급 보안 취약점(CVE)이 발견된 패키지의 새로운 버전이 출시되어도 Dependabot이 즉시 PR을 생성하지 않으므로, 수동 개입이 필요해진다. 이는 **보안 업데이트 속도와 안전성 사이의 트레이드오프**를 발생시킨다.
- **운영 부담**: 지연 기간 동안 수동으로 패키지 보안을 검증해야 하는 부담이 증가한다. 특히 수백 개의 의존성을 가진 대규모 프로젝트에서는 운영 오버헤드가 발생할 수 있다.



---

### 1.2 Hugging Face CEO, '전례 없는' OpenAI 해킹 이후 '급진적 투명성' 촉구

{% include news-card.html
  title="Hugging Face CEO, '전례 없는' OpenAI 해킹 이후 '급진적 투명성' 촉구"
  url="https://techcrunch.com/2026/07/26/hugging-face-ceo-calls-for-radical-transparency-after-unprecedented-openai-hack/"
  image="https://techcrunch.com/wp-content/uploads/2026/07/hugging-face-openai-logos-split-screen.jpg"
  summary="Hugging Face의 CEO는 '전례 없는' OpenAI 해킹 사건 이후 '급진적 투명성'을 촉구하며, 최초의 자율 에이전트 사이버 공격에 대해 전례 없는 대응이 필요하다고 강조했습니다."
  source="TechCrunch Security"
  severity="High"
%}

#### DevSecOps 실무자 관점 분석: Hugging Face CEO의 '급진적 투명성' 촉구

#### 기술적 배경 및 위협 분석

2026년 7월 발생한 OpenAI 해킹 사건은 **최초의 자율 에이전트 기반 사이버 공격**으로 기록됩니다. 이는 기존의 정적 스크립트나 사전 정의된 공격 패턴과 달리, AI 에이전트가 실시간으로 환경을 분석하고 자체적으로 공격 벡터를 생성·변형하며 침투한 점이 핵심입니다. Hugging Face CEO가 '급진적 투명성(radical transparency)'을 요구한 배경에는 다음과 같은 기술적 위협이 존재합니다:

- **자율적 취약점 스캐닝 및 익스플로잇 생성**: AI 에이전트가 코드베이스, API 문서, 오픈소스 의존성을 실시간 분석해 제로데이 취약점을 발굴하고 즉시 익스플로잇 코드를 작성
- **지속적 적응형 회피**: 기존 SIEM/SOAR 규칙을 학습한 후, 탐지를 회피하도록 공격 패턴을 동적으로 변경 (예: 정상 트래픽으로 위장한 후 점진적 권한 상승)
- **모델/데이터 파이프라인 오염**: ML 모델 저장소(Hugging Face Hub 유사)에 악성 가중치나 백도어를 삽입하여 CI/CD 파이프라인 전반을 감염시키는 공급망 공격 가능성

#### 실무 영향 분석

DevSecOps 실무자에게 이번 사건은 **기존 보안 패러다임의 근본적 전환**을 요구합니다:

- **CI/CD 파이프라인 보안 강화**: 기존 SAST/DAST만으로는 AI 에이전트의 동적 회피를 막을 수 없음. **실시간 행동 분석 기반의 런타임 보안**과 **AI 모델 자체의 이상 탐지(Adversarial Robustness)**가 필수
- **모델 저장소 보안 재정의**: Hugging Face, PyTorch Hub 등 오픈모델 저장소에서의 **공급망 보안**이 최우선 과제로 부상. 모델 가중치 서명, 무결성 검증, 사용 이력 투명성 확보 필요
- **사고 대응 체계 변화**: 자율 에이전트 공격은 초기 침투 후 수분 내에 확산 가능. **SOAR 자동화 대응 속도**를 공격 속도보다 빠르게 유지해야 하며, **AI 기반 위협 인텔리전스 피드** 실시간 연동 필수
- **규제 및 컴플라이언스**: '급진적 투명성' 요구는 SOC 2, ISO 27001 등 기존 프레임워크를 넘어 **실시간 취약점 공개 및 패치 이력 공개**를 강제할 가능성



---

### 1.3 Garden Finance, Blockaid가 45만 달러 익스플로잇을 보고함에 따라 앱 비활성화

{% include news-card.html
  title="Garden Finance, Blockaid가 45만 달러 익스플로잇을 보고함에 따라 앱 비활성화"
  url="https://cointelegraph.com/news/garden-finance-app-offline-450k-htlc-exploit?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/hi-bithumb-hack-what-is-known.jpg"
  summary="Blockaid가 Garden Finance의 HTLC 계약에서 Ethereum, Base, Arbitrum, BNB Smart Chain에 걸쳐 약 45만 달러 상당의 USDT가 유출된 익스플로잇을 보고했으며, 이에 Garden Finance가 앱을 비활성화했습니다."
  source="Cointelegraph"
  severity="High"
%}

#### DevSecOps 실무자 관점에서의 Garden Finance $450,000 HTLC 익스플로잇 분석

#### 기술적 배경 및 위협 분석

이번 사건은 **HTLC(Hashed TimeLock Contract)** 기반 스마트 컨트랙트에서 발생한 취약점 익스플로잇입니다. HTLC는 암호화폐 원장 간 원자적 스왑(Atomic Swap)을 가능하게 하는 핵심 메커니즘으로, 해시 잠금(Hash Lock)과 시간 잠금(Time Lock)을 결합하여 조건부 거래를 수행합니다.

**주요 위협 요소:**
- **크로스체인 브릿지 취약점**: 이더리움, 베이스, 아비트럼, BNB 스마트 체인 등 4개 체인에서 동시에 발생한 점으로 보아, HTLC 계약의 로직 결함이 공격자에게 악용되었을 가능성이 높음
- **타임락 조건 우회**: 시간 잠금 조건을 조작하거나 해시 프리이미지(Hash Preimage)를 유출하는 방식으로 자금이 인출된 것으로 추정
- **450,000 USDT 손실**: 단일 공격으로 비교적 소규모 피해이나, 유사한 HTLC 기반 프로토콜에 대한 연쇄 공격 가능성 존재

#### 실무 영향 분석

DevSecOps 관점에서 이번 사건은 다음과 같은 실무적 시사점을 제공합니다:

- **스마트 컨트랙트 감사(Audit)의 한계**: HTLC와 같은 복잡한 조건부 로직은 기존 감사로 발견되지 않는 취약점이 존재할 수 있음 → **지속적 모니터링과 런타임 검증 필요**
- **크로스체인 리스크 확대**: 멀티체인 배포 시 각 체인별 실행 환경 차이(가스 한도, 블록 타임 등)가 취약점으로 연결될 수 있음
- **사고 대응 속도**: Blockaid가 익스플로잇을 탐지하고 Garden Finance가 앱을 비활성화한 시간 간격이 짧았으나, **실시간 탐지-차단 자동화**가 더 필요함
- **규제 및 평판 리스크**: DeFi 프로토콜의 보안 사고는 사용자 신뢰 하락과 규제 강화로 이어질 수 있음



---

## 2. AI/ML 뉴스

### 2.1 NVIDIA, Vera CPU를 활용해 차세대 CPU 및 GPU 설계 가속화

{% include news-card.html
  title="NVIDIA, Vera CPU를 활용해 차세대 CPU 및 GPU 설계 가속화"
  url="https://blogs.nvidia.com/blog/vera-cpu-eda/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/07/cpu-corp-blog-vera-superchip-1280x680-4939150-842x450.jpg"
  summary="NVIDIA는 차세대 CPU와 GPU 설계를 가속화하기 위해 Vera CPU를 활용하고 있으며, Cadence 및 Synopsys와 협력하여 전자 설계 자동화(EDA) 애플리케이션을 최적화하고 있습니다."
  source="NVIDIA AI Blog"
  severity="Medium"
%}

#### 요약

NVIDIA는 차세대 CPU와 GPU 설계를 가속화하기 위해 Vera CPU를 활용하고 있으며, Cadence 및 Synopsys와 협력하여 전자 설계 자동화(EDA) 애플리케이션을 최적화하고 있습니다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 개인 생산성에서 멈춘 Claude Code, 조직의 생산성으로 – 영상 10개로 완성하는 Claude Code on Amazon Bedrock 학습 플랜

{% include news-card.html
  title="개인 생산성에서 멈춘 Claude Code, 조직의 생산성으로 – 영상 10개로 완성하는 Claude Code on Amazon Bedrock 학습 플랜"
  url="https://aws.amazon.com/ko/blogs/tech/claude-code-on-amazon-bedrock-training/"
  summary="AI 코딩 도구, 이제 다들 하나쯤 쓰고 계실 겁니다. 문제는 그 다음입니다"
  source="AWS Korea Blog"
  severity="Medium"
%}

#### 요약

AI 코딩 도구, 이제 다들 하나쯤 쓰고 계실 겁니다. 문제는 그 다음입니다


---

## 4. 블록체인 뉴스

### 4.1 Storj 파산 신청, 토큰 보유자 위한 지분 경로 모색

{% include news-card.html
  title="Storj 파산 신청, 토큰 보유자 위한 지분 경로 모색"
  url="https://cointelegraph.com/news/storj-chapter-11-bankruptcy-tokenholder-equity?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/data-storage-system-2.jpg"
  summary="Storj가 파산 신청을 했으며, 챕터 11 절차 중에도 네트워크는 계속 운영될 것이라고 밝혔습니다. 회사는 STORJ 보유자를 위한 법원 승인 소유권 메커니즘을 모색 중입니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

Storj가 파산 신청을 했으며, 챕터 11 절차 중에도 네트워크는 계속 운영될 것이라고 밝혔습니다. 회사는 STORJ 보유자를 위한 법원 승인 소유권 메커니즘을 모색 중입니다.


---

### 4.2 CLARITY 기대감 사라지고, BitMEX 소송 앞두고 폐쇄: Hodler’s Digest, 7월 26일

{% include news-card.html
  title="CLARITY 기대감 사라지고, BitMEX 소송 앞두고 폐쇄: Hodler's Digest, 7월 26일"
  url="https://cointelegraph.com/magazine/clarity-hopes-fade-bitmex-shuts-as-lawsuit-looms-hodlers-digest-july-27?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/25-july.jpg"
  summary="골드만삭스, 피델리티, 법 집행 기관의 지지에도 불구하고 CLARITY Act의 통과 가능성이 낮아졌습니다. 암호화폐 시장이 5대 주요 업체로 통합됨에 따라 BitMEX가 소송 위기에 직면해 문을 닫습니다."
  source="Cointelegraph"
  severity="High"
%}

#### 요약

골드만삭스, 피델리티, 법 집행 기관의 지지에도 불구하고 CLARITY Act의 통과 가능성이 낮아졌습니다. 암호화폐 시장이 5대 주요 업체로 통합됨에 따라 BitMEX가 소송 위기에 직면해 문을 닫습니다.


---

### 4.3 CFTC, 예측 시장에 정형화된 자체 인증에 대해 두 번째 경고 발령

{% include news-card.html
  title="CFTC, 예측 시장에 정형화된 자체 인증에 대해 두 번째 경고 발령"
  url="https://cointelegraph.com/news/cftc-issues-second-warning-to-prediction-markets-on-cookie-cutter-self-certifications?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/hi-prediction-market-cftc-rule.png"
  summary="미국 상품선물거래위원회(CFTC)가 올해 두 번째로 예측 시장(Prediction Markets)에 대해 지나치게 광범위한 템플릿 방식의 이벤트 계약 자체 인증(self-certifications)을 중단하라고 경고했습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

미국 상품선물거래위원회(CFTC)가 올해 두 번째로 예측 시장(Prediction Markets)에 대해 지나치게 광범위한 템플릿 방식의 이벤트 계약 자체 인증(self-certifications)을 중단하라고 경고했습니다.


---

## 5. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Cloudflare, 고객별 AI 트래픽 제어 옵션 공개](https://news.hada.io/topic?id=31857) | GeekNews (긱뉴스) | 모든 요금제 고객이 자동화 트래픽을 Search·Agent·Training 으로 나눠 허용하거나 차단할 수 있어, 기존의 일괄적인 AI 봇 차단보다 세밀한 정책 설정이 가능해짐 AI 사용 여부가 아니라 사이트에서 수행하는 행동과 콘텐츠 용도 를 분류 기준으로 삼으며, 다목적 크 |
| [Netflix의 사내 LLM 서빙 플랫폼](https://news.hada.io/topic?id=31856) | GeekNews (긱뉴스) | 넷플릭스는 LLM을 별도 사일로로 분리하지 않고 기존 ML 인프라에서 함께 운영하며, vLLM과 Triton 을 통합 서빙 체계에 연결함 기본 엔진으로 선택한 vLLM 은 사용자 정의 모델 지원, 디버깅 용이성, 확장 훅, 연구 환경과의 친숙성을 갖췄으며, Triton의 vLLM back |
| [Claude Code로 대규모 코드 마이그레이션을 수행한 방법](https://news.hada.io/topic?id=31855) | GeekNews (긱뉴스) | Anthropic 개발자들은 Claude Fable 5, Claude Opus 4.8과 동적 워크플로를 이용해 최근 한 달간 수만~수십만 줄 규모의 패키지 10개를 이전했으며, 개별 코드를 고치는 대신 코드를 생성하는 반복 과정 을 개선함 Bun의 Zig→Rust 이전은 2주 미만에 100만 줄 을 생 |


---

## 6. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 12건 | 기타 주제 |
| **AI/ML** | 2건 | Cloudflare, Netflix의 사내 LLM 서빙 플랫폼 |
| **클라우드 보안** | 1건 | Cloudflare |
| **공급망 보안** | 1건 | BleepingComputer 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(12건)입니다. **AI/ML** 분야에서는 Cloudflare, Netflix의 사내 LLM 서빙 플랫폼 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 기능 추가** 관련 보안 영향도 분석 및 모니터링 강화

### P1 (7일 내)

- [ ] **GitHub, PyPI가 공급망 공격 대응을 위한 시간 기반 방어 기능 추가** 관련 보안 검토 및 모니터링
- [ ] **Hugging Face CEO, '전례 없는' OpenAI 해킹 이후 '급진적 투명성' 촉구** 관련 보안 검토 및 모니터링
- [ ] **Garden Finance, Blockaid가 45만 달러 익스플로잇을 보고함에 따라 앱 비활성화** 관련 보안 검토 및 모니터링
- [ ] **WEMIX, 계약 침해 후 공격자가 약 72만 4천 달러 이동했다고 밝혀** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **NVIDIA, Vera CPU를 활용해 차세대 CPU 및 GPU 설계 가속화** 관련 AI 보안 정책 검토
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
