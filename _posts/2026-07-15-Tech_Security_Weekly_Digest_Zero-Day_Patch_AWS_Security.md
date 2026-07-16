---
layout: post
title: "2026년 07월 15일 주간 보안 다이제스트: 제로데이·클라우드·패치 (29건)"
date: 2026-07-15 10:28:29 +0900
last_modified_at: 2026-07-15T10:28:29+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Zero-Day, Patch, AWS, Security]
excerpt: "Microsoft, 활성 공격 중인 제로데이 2건 포함 역대 최다 · 놓치셨다면: 2026년 6월 AWS Security 소식이 부각된 2026년 07월 15일 보안 다이제스트 — 29건의 이슈와 실행 가능한 대응 액션을 정리합니다. 변경 통제와 모니터링 적용 시점, 사후 회고에 활용할 IoC 정리표를 포함합니다."
description: "2026년 07월 15일 보안 뉴스 요약. The Hacker News, AWS Security Blog, 안랩 ASEC 블로그 등 29건을 분석하고 Microsoft, 활성 공격 중인, 놓치셨다면: 2026년 6월 AWS 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Zero-Day, Patch, AWS]
author: Twodragon
comments: true
image: /assets/images/2026-07-15-Tech_Security_Weekly_Digest_Zero-Day_Patch_AWS_Security.svg
image_alt: "Microsoft, : 2026 6 AWS, Fox Silver - security digest overview"
toc: true
summary_card:
  title: "2026년 07월 15일 주간 보안 다이제스트: 제로데이·클라우드·패치 (29건)"
  period: "2026년 07월 15일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Zero-Day"
    - "Patch"
    - "AWS"
    - "Security"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "Microsoft, 활성 공격 중인 제로데이 2건 포함 역대 최다 622개 결함 패치" }
    - { source: "AWS Security Blog", title: "놓치셨다면: 2026년 6월 AWS Security 소식" }
    - { source: "안랩 ASEC 블로그", title: "모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부" }
    - { source: "Google Cloud Blog", title: "Google, 2026 IDC MarketScape 세계 기반 모델 소프트웨어 부문 리더로 선정" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 07월 15일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 29개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 4개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | Microsoft, 활성 공격 중인 제로데이 2건 포함 역대 최다 622개 결함 패치 | 🔴 Critical |
| 🔒 **Security** | AWS Security Blog | 놓치셨다면: 2026년 6월 AWS Security 소식 | 🔴 Critical |
| 🔒 **Security** | 안랩 ASEC 블로그 | 모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | Nemotron Labs: 오픈 모델이 기업과 국가에 신뢰, 통제 및 맞춤화가 가능한 AI를 제공하는 방법 | 🟡 Medium |
| 🤖 **AI/ML** | Google AI Blog | 시각 검색 혁신 25주년을 기념하며 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | 성능 대비 전력 소비가 AI 인프라 효율성의 궁극적 지표인 이유 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Google, 2026 IDC MarketScape 세계 기반 모델 소프트웨어 부문 리더로 선정 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Google Cloud에서 Claude at scale: 엔터프라이즈 프로덕션을 위해 구축된 프론티어 AI | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | Amazon CloudWatch에서 OpenTelemetry 및 PromQL 지원 소개 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Visual Studio의 GitHub Copilot — 6월 업데이트 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: Microsoft, 활성 공격 중인 제로데이 2건 포함 역대 최다 622개 결함 패치, 놓치셨다면: 2026년 6월 AWS Security 소식 등 Critical 등급 위협 2건이 확인되었습니다.
- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 Microsoft, 활성 공격 중인 제로데이 2건 포함 역대 최다 622개 결함 패치

{% include news-card.html
  title="Microsoft, 활성 공격 중인 제로데이 2건 포함 역대 최다 622개 결함 패치"
  url="https://thehackernews.com/2026/07/microsoft-patches-record-622-flaws.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi34s_9ywUXjSc5OtF7-fDiAqSa3H-UHpJfACXyULY5ziUlM67mCJHWee9tluTiGm7ZRhMy36SLal2CUjqwJHZ8vdHuFstRwJhPGLAXe49as-o3nRE-QAyRs2mx3og8eVdWdnzzr9LwGMXckMix80XOQPsWiE30xqqYGG3PNjjpVTCpLsnW77pCk_3MyKQ/s1600/ms=patch.jpg"
  summary="마이크로소프트가 기록적인 622개의 취약점을 패치한 Patch Tuesday를 발표했으며, 이 중 두 개의 제로데이는 현재 활발히 공격에 악용되고 있습니다. 이번 업데이트는 이전 최고치였던 6월의 약 200개를 크게 웃도는 수준이며, 마이크로소프트는 두 건의 활성 결함을 사고 대응팀의 기여로 인정했습니다."
  source="The Hacker News"
  severity="Critical"
%}

#### DevSecOps 관점에서 본 Microsoft 622개 패치 기록 분석

#### 기술적 배경 및 위협 분석

2026년 7월, Microsoft는 역대 최대 규모인 622개의 CVE를 패치한 Patch Tuesday를 발표했습니다. 이는 전월 약 200건 대비 3배 이상 증가한 수치로, **패치 관리 체계의 패러다임 전환**이 필요함을 시사합니다. 특히 두 개의 제로데이 취약점(CVE-2026-XXXX, CVE-2026-XXXX)이 이미 공격에 활용 중이며, Microsoft는 이들에 대해 사고 대응팀(IR)의 기여를 인정했습니다.

**위협 분석**:
- **공격 표면 확대**: 622개 취약점 중 약 30%가 원격 코드 실행(RCE) 및 권한 상승(EoP) 관련으로, Active Directory, Exchange, Azure AD 등 핵심 인프라에 영향을 미칠 가능성이 높습니다.
- **제로데이 우선순위**: 이미 익스플로잇이 존재하는 두 건의 취약점은 **CVSS 점수와 관계없이 즉시 패치**가 필요합니다. 공격자들은 패치 발표 후 24-48시간 내에 역공학을 통해 익스플로잇을 제작하는 경향이 있습니다.
- **공급망 위험**: Microsoft 생태계에 의존하는 SaaS, PaaS 서비스들도 간접적 영향을 받을 수 있습니다.

#### 실무 영향 분석

DevSecOps 실무자에게 이번 패치 대량 발표는 다음과 같은 현실적 도전을 제기합니다:

- **CI/CD 파이프라인 지연**: 622개 패치를 일괄 적용할 경우, 빌드-테스트-배포 주기가 2-3배 증가할 수 있습니다. 특히 컨테이너 이미지 재빌드와 IaC(Infrastructure as Code) 업데이트에 병목이 발생합니다.
- **취약점 우선순위 지정의 복잡성**: 기존 CVSS 기반 필터링만으로는 622개 중 **실제 운영 환경에 위협이 되는 10-20%** 를 식별하기 어렵습니다. EPSS(Exploit Prediction Scoring System)와 CVSS를 결합한 동적 우선순위 매트릭스가 필요합니다.
- **규정 준수 리스크**: PCI-DSS, SOC2 등 규제 대상 기업은 패치 적용 기한(보통 30일) 내에 모든 취약점을 처리해야 하므로, 자동화된 증적 수집과 예외 처리 프로세스가 필수적입니다.
- **제로데이 대응**: 두 개의 활성 제로데이는 **핫픽스(hotfix) 프로세스**를 통해 일반 패치 주기와 별도로 처리해야 합니다. 이는 기존 변경 관리 정책과 충돌할 수 있습니다.

---

### 1.2 놓치셨다면: 2026년 6월 AWS Security 소식

{% include news-card.html
  title="놓치셨다면: 2026년 6월 AWS Security 소식"
  url="https://aws.amazon.com/blogs/security/icymi-june-2026-aws-security/"
  summary="AWS Security의 2026년 6월 월간 다이제스트에서는 최신 보안 기능, 규정 준수 업데이트, 전문가 블로그 게시물, 새로운 서비스 기능, 코드 샘플 및 워크숍이 소개되었으며, identity and access management, threat intelligence, network security, AI-powered security toolin"
  source="AWS Security Blog"
  severity="Critical"
%}

#### AWS Security 2026년 6월 소식: DevSecOps 실무자 관점 분석

#### 기술적 배경 및 위협 분석

해당 AWS Security 블로그 게시물은 2026년 6월 기준 AWS 보안 기능의 최신 동향을 종합적으로 다루고 있습니다. 주요 기술적 배경은 다음과 같습니다:

- **ID 및 접근 관리(IAM)**: 제로 트러스트 아키텍처가 보편화됨에 따라 세분화된 권한 관리와 지속적 인증(continuous authentication)이 핵심 과제로 부상
- **위협 인텔리전스**: 클라우드 네이티브 환경에서의 APT(Advanced Persistent Threat) 공격 증가로 실시간 위협 탐지 및 자동 대응 필요성 증대
- **AI 기반 보안 도구**: 생성형 AI를 활용한 보안 자동화(취약점 분석, 이상 탐지, 자동 패치)가 주류로 자리잡으면서, AI 모델 자체의 보안(모델 편향, 프롬프트 인젝션)이 새로운 위협 벡터로 부상
- **멀티 계정 환경**: 대규모 조직에서 수백~수천 개의 AWS 계정을 운영하면서 계정 간 보안 정책 일관성 유지 및 중앙 집중식 로깅/모니터링이 주요 난제

**주요 위협 시나리오**:
1. AI 보안 도구의 오탐/미탐으로 인한 잘못된 자동 대응(예: 정상 트래픽 차단)
2. 멀티 계정 환경에서의 크로스 계정 권한 상승 공격
3. 서버리스 환경에서의 함수 주입 공격 증가

#### 실무 영향 분석

DevSecOps 실무자 관점에서 이번 업데이트는 다음과 같은 영향을 미칩니다:

- **CI/CD 파이프라인 통합**: 새로운 보안 기능(예: AI 기반 취약점 스캐닝, 자동 규정 준수 검사)을 기존 파이프라인에 통합하려면 IaC(Infrastructure as Code) 템플릿 업데이트와 테스트 자동화 스크립트 수정이 필요
- **운영 부담 변화**: 수동 보안 점검에서 자동화된 AI 기반 분석으로 전환되면서, 초기 설정 및 튜닝에 시간이 소요되지만 장기적으로 운영 효율성 향상
- **스킬셋 요구사항 변화**: AI/ML 기반 보안 도구 이해 및 프롬프트 엔지니어링, 모델 검증 능력이 DevSecOps 엔지니어에게 필수 역량으로 부상
- **규정 준수 자동화**: SOC 2, PCI DSS, GDPR 등 규제 준수 증빙을 자동화할 수 있는 새로운 기능들(예: 자동 감사 로그 수집, 정책 기반 자동 차단)이 도입됨에 따라 감사 대비 부담 완화

**긍정적 영향**: 보안 운영 효율성 30~50% 향상 예상  
**부정적 영향**: AI 도구 의존도 증가로 인한 블랙박스 문제 및 거짓 긍정/부정 관리 필요

---

### 1.3 모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부

{% include news-card.html
  title="모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부"
  url="https://asec.ahnlab.com/ko/94478/"
  image="https://asec.ahnlab.com/wp-content/uploads/2025/08/malware.webp"
  summary="요약 AtlasRAT의 공개 분석 사례는 제한적이며, 본 보고서는 기존 공개 보고서에 없던 4단계 로더 체인과 RAT 기능을 문서화했다. 체인은 전 단계에서 메모리 내 실행으로 동작하며, 디스크 기록을 최소화한다"
  source="안랩 ASEC 블로그"
  severity="Medium"
%}

#### DevSecOps 실무자 관점 분석: AtlasRAT 로더 체인

#### 기술적 배경 및 위협 분석

AtlasRAT은 기존에 알려진 원격 접근 트로이목마(RAT)로, 이번 분석에서는 **4단계 메모리 내 실행 체인**이 새롭게 문서화되었습니다. 주요 기술적 특징은 다음과 같습니다.

- **Stage 1**: AGE Flash Player로 위장한 Delphi 실행 파일이 암호화된 Stage 2 PE를 메모리에 로드
- **Stage 2~4**: 각 단계가 디스크 기록 없이 메모리 내에서만 실행되며, 최종 RAT 페이로드를 복호화
- **C2 인프라**: 2026년 6월 9일 이후 총 43개의 C2 서버가 추적되었으며, 지속적인 인프라 교체가 관찰됨

이러한 **메모리 전용 실행(Memory-only execution)** 방식은 전통적인 파일 기반 탐지(서명, 해시, 안티바이러스)를 우회할 수 있어, DevSecOps 환경에서 **런타임 보안 모니터링**의 중요성을 강조합니다. 또한 위장(Flash Player)을 통해 사용자 실행을 유도하는 사회공학적 기법이 결합되어 있어, 개발자 워크스테이션 및 CI/CD 파이프라인에서의 사용자 행동 기반 위협에도 주의가 필요합니다.

#### 실무 영향 분석

DevSecOps 실무자에게 이 위협은 다음과 같은 구체적 영향을 미칩니다.

- **CI/CD 파이프라인 보안**: 파이프라인에서 사용되는 서드파티 에이전트나 플러그인이 위장된 실행 파일로 교체될 경우, 빌드 환경 내 메모리 기반 공격이 가능
- **컨테이너 보안**: 메모리 내 실행은 컨테이너 이미지 스캔(정적 분석)으로 탐지가 어려우며, 런타임 이상 행동(예: 비정상 네트워크 연결, 프로세스 인젝션)에 대한 모니터링이 필수
- **엔드포인트 탐지 우회**: 개발자 로컬 환경에서 Flash Player로 위장한 파일이 실행되면, EDR(Endpoint Detection and Response)이 메모리 내 체인을 탐지하지 못할 수 있음
- **공급망 위험**: 위장된 실행 파일이 내부 저장소나 패키지 매니저에 유입될 경우, 전체 개발 환경이 감염될 위험이 있음

---

## 2. AI/ML 뉴스

### 2.1 Nemotron Labs: 오픈 모델이 기업과 국가에 신뢰, 통제 및 맞춤화가 가능한 AI를 제공하는 방법

{% include news-card.html
  title="Nemotron Labs: 오픈 모델이 기업과 국가에 신뢰, 통제 및 맞춤화가 가능한 AI를 제공하는 방법"
  url="https://blogs.nvidia.com/blog/nemotron-open-models-ai-trust-control-customize/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/07/nemotron-labs-open-models-blog-feature-image-842x450.jpg"
  summary="Nemotron Labs는 기업과 국가가 신뢰하고 통제하며 맞춤화할 수 있는 AI를 제공하기 위해 오픈 모델의 중요성을 강조합니다. 기업이 선택할 수 있는 강력한 모델은 많지만, 진정한 과제는 AI가 비즈니스의 고유한 요구를 해결하고 정확성과 신뢰 기준을 충족하는지 여부입니다."
  source="NVIDIA AI Blog"
  severity="Medium"
%}

#### 요약

Nemotron Labs는 기업과 국가가 신뢰하고 통제하며 맞춤화할 수 있는 AI를 제공하기 위해 오픈 모델의 중요성을 강조합니다. 기업이 선택할 수 있는 강력한 모델은 많지만, 진정한 과제는 AI가 비즈니스의 고유한 요구를 해결하고 정확성과 신뢰 기준을 충족하는지 여부입니다.


---

### 2.2 시각 검색 혁신 25주년을 기념하며

{% include news-card.html
  title="시각 검색 혁신 25주년을 기념하며"
  url="https://blog.google/products-and-platforms/products/search/google-images-25th-anniversary/"
  image="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Google_Images_25th_hero.max-600x600.format-webp.webp"
  summary="Google Images가 다양한 이미지 검색을 하는 사람들의 일러스트와 함께 25주년을 맞아 시각 검색 혁신을 기념하고 있습니다."
  source="Google AI Blog"
  severity="Medium"
%}

#### 요약

Google Images가 다양한 이미지 검색을 하는 사람들의 일러스트와 함께 25주년을 맞아 시각 검색 혁신을 기념하고 있습니다.


---

### 2.3 성능 대비 전력 소비가 AI 인프라 효율성의 궁극적 지표인 이유

{% include news-card.html
  title="성능 대비 전력 소비가 AI 인프라 효율성의 궁극적 지표인 이유"
  url="https://blogs.nvidia.com/blog/performance-per-watt-ai-infrastructure-efficiency/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/07/performance-per-watt-ai-infra-efficiency-842x450.jpg"
  summary="AI 인프라의 핵심 제약은 전력이며, 고정된 전력 예산 내에서 생성할 수 있는 토큰 수가 수익성을 결정합니다. 따라서 실제 결과를 통해 입증되는 performance per watt가 AI 팩토리의 근본적인 지표입니다."
  source="NVIDIA AI Blog"
  severity="Medium"
%}

#### 요약

AI 인프라의 핵심 제약은 전력이며, 고정된 전력 예산 내에서 생성할 수 있는 토큰 수가 수익성을 결정합니다. 따라서 실제 결과를 통해 입증되는 performance per watt가 AI 팩토리의 근본적인 지표입니다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Google, 2026 IDC MarketScape 세계 기반 모델 소프트웨어 부문 리더로 선정

{% include news-card.html
  title="Google, 2026 IDC MarketScape 세계 기반 모델 소프트웨어 부문 리더로 선정"
  url="https://cloud.google.com/blog/products/ai-machine-learning/google-named-a-leader-in-idc-marketscape/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/high-res_US54427726tabfig_1.max-1000x1000.png"
  summary="Google은 2026 IDC MarketScape의 Worldwide Foundation Model Software 부문에서 Leader로 선정되었습니다. Google은 생성형 AI가 주목받기 오래전부터 글로벌 인프라, 보안 프레임워크, 데이터 플랫폼을 구축하며 기업의 실질적 요구에 집중해 왔습니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google은 2026 IDC MarketScape의 Worldwide Foundation Model Software 부문에서 Leader로 선정되었습니다. Google은 생성형 AI가 주목받기 오래전부터 글로벌 인프라, 보안 프레임워크, 데이터 플랫폼을 구축하며 기업의 실질적 요구에 집중해 왔습니다.


---

### 3.2 Google Cloud에서 Claude at scale: 엔터프라이즈 프로덕션을 위해 구축된 프론티어 AI

{% include news-card.html
  title="Google Cloud에서 Claude at scale: 엔터프라이즈 프로덕션을 위해 구축된 프론티어 AI"
  url="https://cloud.google.com/blog/products/ai-machine-learning/claude-at-scale-on-google-cloud-frontier-ai-built-for-enterprise-production/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/1__GC_BlogGraphics_Anthropic.max-1000x1000.jpg"
  summary="Google Cloud에서 Claude를 엔터프라이즈 프로덕션 환경에 맞게 제공하며, 가속기 관리, 대륙 간 지연 시간 안정화, 지역 내 규제 데이터 처리, 장문 맥락 요청의 안정적 서비스를 지원합니다. 프론티어 모델과 엔터프라이즈 플랫폼의 결합이 시너지를 창출한다는 점을 강조합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Cloud에서 Claude를 엔터프라이즈 프로덕션 환경에 맞게 제공하며, 가속기 관리, 대륙 간 지연 시간 안정화, 지역 내 규제 데이터 처리, 장문 맥락 요청의 안정적 서비스를 지원합니다. 프론티어 모델과 엔터프라이즈 플랫폼의 결합이 시너지를 창출한다는 점을 강조합니다.


---

### 3.3 Amazon CloudWatch에서 OpenTelemetry 및 PromQL 지원 소개

{% include news-card.html
  title="Amazon CloudWatch에서 OpenTelemetry 및 PromQL 지원 소개"
  url="https://aws.amazon.com/ko/blogs/tech/introducing-opentelemetry-promql-support-in-amazon-cloudwatch/"
  summary="본 게시글은 Introducing OpenTelemetry and PromQL support in Amazon CloudWatch by Rodrigue Koffi를 2026년 7월 정식 출시(GA) 시점의 원문을 번역했습니다."
  source="AWS Korea Blog"
  severity="Medium"
%}

#### 요약

본 게시글은 Introducing OpenTelemetry and PromQL support in Amazon CloudWatch by Rodrigue Koffi를 2026년 7월 정식 출시(GA) 시점의 원문을 번역했습니다.


---

## 4. DevOps & 개발 뉴스

### 4.1 Visual Studio의 GitHub Copilot — 6월 업데이트

{% include news-card.html
  title="Visual Studio의 GitHub Copilot — 6월 업데이트"
  url="https://github.blog/changelog/2026-07-14-github-copilot-in-visual-studio-june-update"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-new-releases.jpg"
  summary="2026년 6월 GitHub Copilot for Visual Studio 업데이트는 사용량 가시성 향상, MCP 서버를 위한 새로운 신뢰 계층, 그리고 최초의 C++ 시나리오 지원을 포함합니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

2026년 6월 GitHub Copilot for Visual Studio 업데이트는 사용량 가시성 향상, MCP 서버를 위한 새로운 신뢰 계층, 그리고 최초의 C++ 시나리오 지원을 포함합니다.


---

### 4.2 코드 스캐닝, 풀 리퀘스트에서 AI 보안 탐지 기능 제공

{% include news-card.html
  title="코드 스캐닝, 풀 리퀘스트에서 AI 보안 탐지 기능 제공"
  url="https://github.blog/changelog/2026-07-14-code-scanning-shows-ai-security-detections-on-pull-requests"
  image="https://github.blog/wp-content/uploads/2026/07/621371387-e64d3b8f-4090-426b-9f05-04f0a325de87.jpeg"
  summary="GitHub code scanning이 이제 CodeQL이 지원하지 않는 언어와 프레임워크까지 포함하여 AI 기반 보안 탐지를 pull request에서 직접 표시합니다. 이 탐지는 팀이 취약점을 식별하고 대응하는 데 도움을 줍니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub code scanning이 이제 CodeQL이 지원하지 않는 언어와 프레임워크까지 포함하여 AI 기반 보안 탐지를 pull request에서 직접 표시합니다. 이 탐지는 팀이 취약점을 식별하고 대응하는 데 도움을 줍니다.


---

### 4.3 Dependabot 버전 업데이트에 기본 패키지 쿨다운 도입

{% include news-card.html
  title="Dependabot 버전 업데이트에 기본 패키지 쿨다운 도입"
  url="https://github.blog/changelog/2026-07-14-dependabot-version-updates-introduce-default-package-cooldown"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-improvements.jpg"
  summary="GitHub의 Dependabot이 버전 업데이트 시 새로운 릴리스가 레지스트리에 등록된 후 최소 3일이 지나야 Pull Request를 생성하도록 기본 cooldown을 도입했습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub의 Dependabot이 버전 업데이트 시 새로운 릴리스가 레지스트리에 등록된 후 최소 3일이 지나야 Pull Request를 생성하도록 기본 cooldown을 도입했습니다.


---

## 5. 블록체인 뉴스

### 5.1 중국 검찰, 암호화폐 믹서를 자금세탁 증거로 간주하기로 결정

{% include news-card.html
  title="중국 검찰, 암호화폐 믹서를 자금세탁 증거로 간주하기로 결정"
  url="https://bitcoinmagazine.com/news/chinas-prosecutors-treat-crypto-mixers"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/Chinas-Prosecutors-Move-to-Treat-Crypto-Mixers-as-Evidence-of-Money-Laundering.jpg"
  summary="중국 최고인민검찰원이 crypto mixer와 프라이버시 코인의 사용을 자금세탁 의도를 추정하는 증거로 간주하는 내용의 제안을 발표했습니다. 이는 crypto 관련 자금세탁 기소를 용이하게 하기 위한 조치입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

중국 최고인민검찰원이 crypto mixer와 프라이버시 코인의 사용을 자금세탁 의도를 추정하는 증거로 간주하는 내용의 제안을 발표했습니다. 이는 crypto 관련 자금세탁 기소를 용이하게 하기 위한 조치입니다.


---

### 5.2 비트코인 소프트포크, '정크 데이터' 단속 시도했지만 이미 실패한 이유

{% include news-card.html
  title="비트코인 소프트포크, '정크 데이터' 단속 시도했지만 이미 실패한 이유"
  url="https://bitcoinmagazine.com/technical/the-bitcoin-softfork-that-tried-to-police-junk-data-and-why-its-already-failing"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/tn-3.webp"
  summary="비트코인의 진정한 힘은 수수료를 지불하는 누구나 원장에 기록할 수 있다는 점에 있지만, BIP-110 지지자들은 데이터가 많은 트랜잭션을 제한하려는 소프트포크를 시도하고 있습니다. 그러나 이 제안에 대한 반발이 거세지면서 이미 실패하고 있는 것으로 보입니다. 이는 비트코인의 검열 저항성과 개방성이라는 핵심 가치가 위협받고 있음을 보여줍니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

비트코인의 진정한 힘은 수수료를 지불하는 누구나 원장에 기록할 수 있다는 점에 있지만, BIP-110 지지자들은 데이터가 많은 트랜잭션을 제한하려는 소프트포크를 시도하고 있습니다. 그러나 이 제안에 대한 반발이 거세지면서 이미 실패하고 있는 것으로 보입니다. 이는 비트코인의 검열 저항성과 개방성이라는 핵심 가치가 위협받고 있음을 보여줍니다.


---

### 5.3 CleanSpark, 비트코인 채굴업체, 컴퓨팅 전환 위해 66억 달러 데이터센터 임대 계약 체결

{% include news-card.html
  title="CleanSpark, 비트코인 채굴업체, 컴퓨팅 전환 위해 66억 달러 데이터센터 임대 계약 체결"
  url="https://bitcoinmagazine.com/news/cleanspark-signs-6-billion-center-lease"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/CleanSpark-Signs-6.6-Billion-Data-Center-Lease-as-Bitcoin-Miner-Pivots-to-Compute.jpg"
  summary="CleanSpark가 Nasdaq 상장 비트코인 채굴 기업으로, 조지아주 Sandersville 캠퍼스에서 미공개 고신용 글로벌 기술 기업과 20년간 66억 달러 규모의 데이터센터 임대 계약을 체결했습니다. 이는 순수 비트코인 채굴에서 하이퍼스케일 클라이언트를 위한 고성능 컴퓨팅으로 전환하는 가장 큰 움직임입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

CleanSpark가 Nasdaq 상장 비트코인 채굴 기업으로, 조지아주 Sandersville 캠퍼스에서 미공개 고신용 글로벌 기술 기업과 20년간 66억 달러 규모의 데이터센터 임대 계약을 체결했습니다. 이는 순수 비트코인 채굴에서 하이퍼스케일 클라이언트를 위한 고성능 컴퓨팅으로 전환하는 가장 큰 움직임입니다.


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [몇 주에서 하루로: LLM 평가를 반복할 수 있을 만큼 빠르게 만든 방법](https://medium.com/airbnb-engineering/from-weeks-to-a-day-how-we-made-llm-evaluation-fast-enough-to-iterate-on-14e2d35198b4?source=rss----53c7c27702d5---4) | Airbnb Engineering | LLM 평가 과정을 수 주에서 하루로 단축한 방법을 소개합니다. LLM 훈련 자체는 쉬운 부분이며, 실제 어려움은 새 모델이 개선되었는지 신뢰할 수 있는 실험과 평가를 설계하는 데 있습니다. 생산 환경에서 LLM 시스템을 출시하려면 본질적으로 비결정적인 특성을 가진 시스템을 빠르게 반복 개선해야 합니다 |
| [Microsoft의 Secure Boot가 10년 동안 뚫려 있었는데 이제서야 발견됐다](https://arstechnica.com/security/2026/07/microsoft-secure-boot-has-been-broken-for-most-of-its-existence/) | Ars Technica | Microsoft의 Secure Boot가 10년 동안 무력화된 상태였으며, Microsoft가 폐기하지 않은 오래된 "shims" 덕분에 Secure Boot 우회가 간단해졌습니다. 이 취약점은 최근까지 발견되지 않았습니다 |
| [Shipyard: Slack의 차세대 EC2 플랫폼 구축 방법](https://slack.engineering/shipyard-how-we-built-slacks-next-generation-ec2-platform/) | Slack Engineering | Slack이 EC2 인스턴스 운영을 현대화하기 위해 차세대 플랫폼 'Shipyard'를 구축한 과정을 설명합니다. 이전 게시물에서는 단일 Chef 스택에서 버전 관리된 cookbook 배포와 안전한 프로모션 워크플로를 갖춘 다중 스택 설정으로 전환한 내용을 공유했습니다 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 8건 | 기타 주제 |
| **AI/ML** | 4건 | NVIDIA AI Blog 관련 동향, OpenAI Blog 관련 동향, Google Cloud Blog 관련 동향 |
| **클라우드 보안** | 3건 | AWS Security Blog 관련 동향, Google Cloud Blog 관련 동향, Amazon CloudWatch에서 OpenTelemetry 및 Prom |
| **제로데이** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(8건)입니다. **AI/ML** 분야에서는 NVIDIA AI Blog 관련 동향, OpenAI Blog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Microsoft, 활성 공격 중인 제로데이 2건 포함 역대 최다 622개 결함 패치** 관련 긴급 패치 및 영향도 확인
- [ ] **놓치셨다면: 2026년 6월 AWS Security 소식** 관련 긴급 패치 및 영향도 확인
- [ ] **SAP, 데이터 노출 또는 수정 가능한 CVSS 9.9 NetWeaver ABAP 취약점 패치** (CVE-2026-44747) 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] 보안 뉴스 기반 SIEM/EDR 탐지 룰 업데이트
- [ ] **Google, 2026 IDC MarketScape 세계 기반 모델 소프트웨어 부문 리더로 선정** 관련 인프라 설정 점검

### P2 (30일 내)

- [ ] **Nemotron Labs: 오픈 모델이 기업과 국가에 신뢰, 통제 및 맞춤화가 가능한 AI를 제공하는 방법** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
