---
layout: post
title: "2026년 07월 18일 주간 보안 다이제스트: 패치·쿠버네티스·AI 에이전트 (28건)"
date: 2026-07-18 10:43:05 +0900
last_modified_at: 2026-07-18T10:43:05+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Blockchain, Cloud, Kubernetes]
excerpt: "2026년 07월 18일 공개된 28건의 위협·취약점 가운데 새로운 wp2shell WordPress 핵심 결함으로 인증되지 · OpenSSL HollowByte 결함이 즉각 대응 우선순위에 올랐습니다. 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다."
description: "2026년 07월 18일 보안 뉴스 요약. The Hacker News 등 28건을 분석하고 새로운 wp2shell WordPress 핵심, OpenSSL HollowByte 결함, 7개의 악성 Vite npm 패키지 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Blockchain, Cloud]
author: Twodragon
comments: true
image: /assets/images/2026-07-18-Tech_Security_Weekly_Digest_AI_Blockchain_Cloud_Kubernetes.svg
image_alt: "wp2shell WordPress, OpenSSL HollowByte, 7 Vite npm - security digest overview"
toc: true
summary_card:
  title: "2026년 07월 18일 주간 보안 다이제스트: 패치·쿠버네티스·AI 에이전트 (28건)"
  period: "2026년 07월 18일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Blockchain"
    - "Cloud"
    - "Kubernetes"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "새로운 wp2shell WordPress 핵심 결함으로 인증되지 않은 공격자가 코드 실행 가능" }
    - { source: "The Hacker News", title: "OpenSSL HollowByte 결함, 11바이트 TLS 요청으로 서버 메모리 정지 가능" }
    - { source: "The Hacker News", title: "7개의 악성 Vite npm 패키지, 블록체인 C2를 이용해 RAT 유포" }
    - { source: "Google Cloud Blog", title: "BigQuery에서 IAM 데이터 거버넌스 태그로 컬럼 수준 보안을 강화하세요" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 07월 18일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 28개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 3개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | 새로운 wp2shell WordPress 핵심 결함으로 인증되지 않은 공격자가 코드 실행 가능 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | OpenSSL HollowByte 결함, 11바이트 TLS 요청으로 서버 메모리 정지 가능 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 7개의 악성 Vite npm 패키지, 블록체인 C2를 이용해 RAT 유포 | 🟠 High |
| 🤖 **AI/ML** | NVIDIA AI Blog | NVIDIA Vera Rubin, 포스트 트레이닝 워크로드에서 달러당 지능을 극대화 — 에이전틱 AI의 핵심 지표 | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | AI 시대를 위한 성과표 | 🟡 Medium |
| 🤖 **AI/ML** | Netflix Tech Blog | Netflix의 사내 LLM 서빙 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | BigQuery에서 IAM 데이터 거버넌스 태그로 컬럼 수준 보안을 강화하세요 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Gemini Enterprise Agent Platform에서 구축할 수 있는 13가지 실습 데모 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | AI 토크노믹스 가이드: 토큰 효율적 소프트웨어 엔지니어링을 위한 11가지 원칙 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | GitHub Copilot의 저장소 수준 사용 메트릭이 일반 공개되었습니다 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: 새로운 wp2shell WordPress 핵심 결함으로 인증되지 않은 공격자가 코드 실행 가능 등 Critical 등급 위협 1건이 확인되었습니다.
- **주요 모니터링 대상**: 7개의 악성 Vite npm 패키지, 블록체인 C2를 이용해 RAT 유포 등 High 등급 위협 1건에 대한 탐지 강화가 필요합니다.
- 공급망 보안 위협이 확인되었으며, 서드파티 의존성 검토와 SBOM 업데이트를 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 새로운 wp2shell WordPress 핵심 결함으로 인증되지 않은 공격자가 코드 실행 가능

{% include news-card.html
  title="새로운 wp2shell WordPress 핵심 결함으로 인증되지 않은 공격자가 코드 실행 가능"
  url="https://thehackernews.com/2026/07/new-wp2shell-wordpress-core-flaw-lets.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiRULLT1q8L6AtUB7jgKywi_KSF8VGKkOF9yC3Snt81K1aD2XSEV1jgfIe331rXUWGqhmAyFgr1USssr4_CQmuE7HLAn0ShaQ0pHY_yvNYMjQdHtpV8i-vlk2ickhJSJDSN3amGox_DMR5hemMlrgXIk8kHoHlYKZncjpiV3ibF77ax1Yn0fEjxtgxy7tY/s1600/wordpress-core.jpg"
  summary="WordPress 핵심에서 발견된 wp2shell 취약점으로 인증되지 않은 공격자가 익명의 HTTP 요청을 통해 코드를 실행할 수 있으며, 플러그인이 없는 기본 설치도 영향을 받습니다. 이 결함은 Assetnote의 Adam Kues가 발견하여 보고했으며, WordPress는 6.9.5 및 7.0.2 버전을 출시하고 강제 업데이트를 활성화하여 대응했습니다."
  source="The Hacker News"
  severity="Critical"
%}

#### DevSecOps 관점에서 wp2shell WordPress 핵심 취약점 분석

#### 기술적 배경 및 위협 분석

해당 취약점(CVE 미할당)은 WordPress 코어 자체에 존재하는 원격 코드 실행(RCE) 취약점으로, **플러그인이나 테마 없이 기본 설치 상태에서도 익스플로잇이 가능**합니다. 익명의 HTTP 요청만으로 서버 측 코드 실행이 가능하다는 점에서 심각도가 극히 높습니다.

영향받는 버전은 WordPress 6.9 및 7.0 전체이며, 패치는 6.9.5와 7.0.2로 배포되었습니다. WordPress는 이번에 **강제 자동 업데이트(forced auto-update)** 메커니즘을 활성화하여, 패치 적용을 서버 측에서 강제로 밀어넣은 점이 주목할 만합니다. 이는 일반적인 자동 업데이트와 달리 사용자 동의 없이 업데이트가 진행될 수 있음을 의미하며, DevSecOps 관점에서 **변경 관리 프로세스의 우회**라는 리스크를 수반합니다.

Assetnote(Searchlight Cyber)의 Adam Kues가 발견했으며, 공격 벡터는 WordPress의 URL 처리 로직 내 파라미터 인젝션으로 추정됩니다. 구체적인 익스플로잇 코드는 아직 공개되지 않았으나, PoC가 조만간 등장할 가능성이 높습니다.

#### 실무 영향 분석

- **공격 표면 확대**: WordPress는 전 세계 웹사이트의 43% 이상을 점유하므로, 이 취약점 하나로 수백만 사이트가 즉각적인 위험에 노출됩니다. 인증이 필요 없는 RCE는 공격자에게 **완전한 서버 장악**을 허용합니다.
- **CI/CD 파이프라인 혼란**: 강제 자동 업데이트로 인해 운영 중인 사이트가 예고 없이 업데이트되면서, 사전 테스트를 거친 CI/CD 파이프라인이 무력화될 수 있습니다. 특히 커스텀 테마나 플러그인과의 호환성 문제가 발생할 위험이 큽니다.
- **모니터링 및 탐지 어려움**: 정상적인 HTTP 요청으로 위장한 공격이므로, 기존 WAF나 IDS/IPS만으로는 탐지가 까다롭습니다. 로그 기반 이상 징후 탐지(SIEM)가 필수적입니다.
- **규정 준수 위험**: GDPR, PCI DSS 등 규제 대상 사이트의 경우, 패치 적용 지연 시 법적 책임이 발생할 수 있습니다.



---

### 1.2 OpenSSL HollowByte 결함, 11바이트 TLS 요청으로 서버 메모리 정지 가능

{% include news-card.html
  title="OpenSSL HollowByte 결함, 11바이트 TLS 요청으로 서버 메모리 정지 가능"
  url="https://thehackernews.com/2026/07/openssl-hollowbyte-flaw-could-freeze.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhk66eU1Srifu4Rdpf7MZDjg3GdNMtQK6ZW-F283kxhZ7Z0W_8nWNJynZiQ7n0ov9OLNm315P4942h3-unMI0WZ1-LH8tdQ6sv2o6q0TxKT-bVKewzkQULKKXSJOee_oANuI3YquoDgSPHsPeXEdQcFRoy8czRQimH_f0sNHJ55-5LA153sQgUPkpBBEVE/s1600/openssl.jpg"
  summary="OpenSSL의 HollowByte 취약점은 11바이트의 TLS 요청으로 서버 메모리를 최대 131KB까지 고갈시킬 수 있으며, glibc 시스템에서는 프로세스가 재시작될 때까지 메모리가 회수되지 않습니다. Okta Red Team이 발견하고 명명한 이 서비스 거부 버그는 OpenSSL이 6월에 CVE, 권고, 변경 로그 없이 패치를 배포했습니다."
  source="The Hacker News"
  severity="Medium"
%}

#### 요약

OpenSSL의 HollowByte 취약점은 11바이트의 TLS 요청으로 서버 메모리를 최대 131KB까지 고갈시킬 수 있으며, glibc 시스템에서는 프로세스가 재시작될 때까지 메모리가 회수되지 않습니다. Okta Red Team이 발견하고 명명한 이 서비스 거부 버그는 OpenSSL이 6월에 CVE, 권고, 변경 로그 없이 패치를 배포했습니다.


#### 권장 조치

- 관련 시스템 목록 확인 및 자사 환경 해당 여부 평가
- 벤더 보안 권고 확인 후 패치 또는 완화 조치 적용
- SIEM/EDR 탐지 룰에 관련 IoC 추가
- 보안팀 내 공유 및 모니터링 강화


---

### 1.3 7개의 악성 Vite npm 패키지, 블록체인 C2를 이용해 RAT 유포

{% include news-card.html
  title="7개의 악성 Vite npm 패키지, 블록체인 C2를 이용해 RAT 유포"
  url="https://thehackernews.com/2026/07/seven-malicious-vite-npm-packages-use.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgA07xA1INXGKM7Z2LQ6zk2IFE_Hb_aDQNHmSfPtJkZY5Gzo2U2_cyflorBsU76hbXK8SwKXR5AmkK5dAAd9uw0wRh6gYaC-5ZPjT6kEdvE7rO-5G0TxXm8a-eytoygZOMuSG-aOnYkC_zTVbnxSq7zxaIFYyLcegbQ59WVztRO-y3MHmce7XuDz2SdVsKA/s1600/vite-npm.jpg"
  summary="사이버 보안 연구진이 Vite 프론트엔드 도구 생태계를 노리는 7개의 악성 npm 패키지를 발견했습니다. Checkmarx가 ViteVenom으로 명명한 이 캠페인은 Tron 블록체인을 활용한 4계층 C2 인프라를 사용하는 ChainVeil의 확장으로, 원격 접근 트로이목마(RAT)를 유포합니다."
  source="The Hacker News"
  severity="High"
%}

#### DevSecOps 관점 분석: ViteVenom 공급망 공격

#### 기술적 배경 및 위협 분석

ViteVenom 캠페인은 **Vite 프론트엔드 빌드 도구 생태계**를 표적으로 한 7개의 악성 npm 패키지로 구성된 공급망 공격입니다. 주요 특징은 **블록체인 기반 C2(Command & Control) 인프라**를 4계층으로 구성하여 탐지를 회피한 점입니다.

- **C2 구조**: Tron 블록체인 스마트 컨트랙트를 활용한 C2 통신으로, 기존 IP/도메인 기반 탐지 우회
- **페이로드**: 원격 접근 트로이목마(RAT)를 배포하여 개발자 환경 내 정보 탈취 및 지속적 접근 확보
- **공급망 공격**: Vite 플러그인/도구로 위장한 패키지를 npm 레지스트리에 업로드, `npm install` 시 자동 실행

기존 ChainVeil 캠페인의 확장판으로, 블록체인 트랜잭션을 통해 C2 명령을 전달하므로 전통적인 네트워크 기반 탐지가 무력화됩니다.

#### 실무 영향 분석

**DevSecOps 파이프라인**에 미치는 직접적 영향:
- **CI/CD 환경**: 빌드 과정에서 악성 패키지가 자동 설치될 경우, RAT이 CI/CD 에이전트에 상주하여 자격증명, 소스코드, 시크릿 탈취
- **개발자 워크스테이션**: `npm install` 시 로컬 환경 감염 → 개발자 PC를 경유한 내부망 침투
- **의존성 트리**: Vite 기반 프로젝트의 `package.json`에 악성 패키지가 포함되면 팀 전체로 전파

**탐지 난이도**: 블록체인 트랜잭션은 합법적인 트래픽과 구분이 어렵고, C2 주소가 동적으로 변경되어 정적 탐지룰 무력화



---

## 2. AI/ML 뉴스

### 2.1 NVIDIA Vera Rubin, 포스트 트레이닝 워크로드에서 달러당 지능을 극대화 — 에이전틱 AI의 핵심 지표

{% include news-card.html
  title="NVIDIA Vera Rubin, 포스트 트레이닝 워크로드에서 달러당 지능을 극대화 — 에이전틱 AI의 핵심 지표"
  url="https://blogs.nvidia.com/blog/nvidia-vera-rubin-post-training-intelligence-per-dollar/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/07/inline-1784235912807-842x450.png"
  summary="NVIDIA Vera Rubin은 에이전틱 AI 시대의 포스트 트레이닝 워크로드에서 극한의 코드사인을 통해 토큰당 최저 비용을 달성, 달러당 지능을 극대화합니다."
  source="NVIDIA AI Blog"
  severity="Medium"
%}

#### 요약

NVIDIA Vera Rubin은 에이전틱 AI 시대의 포스트 트레이닝 워크로드에서 극한의 코드사인을 통해 토큰당 최저 비용을 달성, 달러당 지능을 극대화합니다.


---

### 2.2 AI 시대를 위한 성과표

{% include news-card.html
  title="AI 시대를 위한 성과표"
  url="https://openai.com/index/a-scorecard-for-the-ai-age"
  summary="OpenAI의 CFO Sarah Friar가 AI 투자 수익률을 측정하기 위해 유용한 작업, 성공적 작업당 비용, 신뢰성, 컴퓨팅 대비 수익이라는 네 가지 기준을 포함한 실용적인 AI scorecard를 소개했습니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

OpenAI의 CFO Sarah Friar가 AI 투자 수익률을 측정하기 위해 유용한 작업, 성공적 작업당 비용, 신뢰성, 컴퓨팅 대비 수익이라는 네 가지 기준을 포함한 실용적인 AI scorecard를 소개했습니다.


---

### 2.3 Netflix의 사내 LLM 서빙

{% include news-card.html
  title="Netflix의 사내 LLM 서빙"
  url="https://netflixtechblog.com/in-house-llm-serving-at-netflix-a5a8e799ea2c?source=rss----2615bd06b42e---4"
  image="https://cdn-images-1.medium.com/max/1024/1*GKGOrp0xddZwHomMhiSeCA.png"
  summary="Netflix의 AI Platform 팀은 자체 프로덕션 환경에서 LLM을 호스팅 API 대신 전체 스택을 직접 운영하며, 모델 배포부터 추론까지 내부에서 처리합니다. 이러한 결정 중 일부는 명확하지 않았으며, 일부는 프로덕션 부하 하에서야 트레이드오프가 드러났습니다."
  source="Netflix Tech Blog"
  severity="Medium"
%}

#### 요약

Netflix의 AI Platform 팀은 자체 프로덕션 환경에서 LLM을 호스팅 API 대신 전체 스택을 직접 운영하며, 모델 배포부터 추론까지 내부에서 처리합니다. 이러한 결정 중 일부는 명확하지 않았으며, 일부는 프로덕션 부하 하에서야 트레이드오프가 드러났습니다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 BigQuery에서 IAM 데이터 거버넌스 태그로 컬럼 수준 보안을 강화하세요

{% include news-card.html
  title="BigQuery에서 IAM 데이터 거버넌스 태그로 컬럼 수준 보안을 강화하세요"
  url="https://cloud.google.com/blog/products/data-analytics/level-up-your-column-level-security-using-iam-data-governance-tags-in-bigquery/"
  summary="BigQuery의 정책 태그는 민감한 컬럼 접근 제어에 효과적이었지만, 데이터 환경의 복잡성 증가에 따라 IAM Data Governance Tags를 사용한 컬럼 수준 보안 강화가 필요합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

BigQuery의 정책 태그는 민감한 컬럼 접근 제어에 효과적이었지만, 데이터 환경의 복잡성 증가에 따라 IAM Data Governance Tags를 사용한 컬럼 수준 보안 강화가 필요합니다.


---

### 3.2 Gemini Enterprise Agent Platform에서 구축할 수 있는 13가지 실습 데모

{% include news-card.html
  title="Gemini Enterprise Agent Platform에서 구축할 수 있는 13가지 실습 데모"
  url="https://cloud.google.com/blog/products/ai-machine-learning/13-demos-on-gemini-enterprise-agent-platform/"
  summary="올해 초 소개된 Gemini Enterprise Agent Platform에서 에이전트를 구축, 확장, 관리, 최적화할 수 있으며, 이 플랫폼의 기능을 보여주는 13개의 데모가 공개되었다. 각 데모는 즉시 활용 가능한 개념, 패턴, 아키텍처를 다루며, 반드시 순서대로 따라 할 필요는 없다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

올해 초 소개된 Gemini Enterprise Agent Platform에서 에이전트를 구축, 확장, 관리, 최적화할 수 있으며, 이 플랫폼의 기능을 보여주는 13개의 데모가 공개되었다. 각 데모는 즉시 활용 가능한 개념, 패턴, 아키텍처를 다루며, 반드시 순서대로 따라 할 필요는 없다.


---

### 3.3 AI 토크노믹스 가이드: 토큰 효율적 소프트웨어 엔지니어링을 위한 11가지 원칙

{% include news-card.html
  title="AI 토크노믹스 가이드: 토큰 효율적 소프트웨어 엔지니어링을 위한 11가지 원칙"
  url="https://cloud.google.com/blog/topics/developers-practitioners/guide-to-ai-tokenomics-eleven-principles-for-token-efficient-software-engineering/"
  summary="AI 코딩 어시스턴트의 효율성을 높이기 위해 token 소비 최적화가 중요하며, context bloat는 지연 시간 증가와 모델의 명령 망각 및 환각을 유발합니다. 개발자는 각 token을 최대한 활용하도록 어시스턴트를 지시하는 책임을 지게 됩니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

AI 코딩 어시스턴트의 효율성을 높이기 위해 token 소비 최적화가 중요하며, context bloat는 지연 시간 증가와 모델의 명령 망각 및 환각을 유발합니다. 개발자는 각 token을 최대한 활용하도록 어시스턴트를 지시하는 책임을 지게 됩니다.


---

## 4. DevOps & 개발 뉴스

### 4.1 GitHub Copilot의 저장소 수준 사용 메트릭이 일반 공개되었습니다

{% include news-card.html
  title="GitHub Copilot의 저장소 수준 사용 메트릭이 일반 공개되었습니다"
  url="https://github.blog/changelog/2026-07-17-repository-level-github-copilot-usage-metrics-generally-available"
  image="https://github.blog/wp-content/uploads/2026/07/623445116-e279ca7d-2e24-46bd-ab94-897188edb536.jpeg"
  summary="GitHub Copilot usage metrics REST API가 이제 저장소 수준의 활동을 보고하며, 두 개의 새로운 엔드포인트가 Copilot coding agent와 Copilot code review에 대한 일별 풀 리퀘스트 활동을 제공합니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot usage metrics REST API가 이제 저장소 수준의 활동을 보고하며, 두 개의 새로운 엔드포인트가 Copilot coding agent와 Copilot code review에 대한 일별 풀 리퀘스트 활동을 제공합니다.


---

### 4.2 GitHub Copilot 앱이 이제 사용량 메트릭 API에서 제공됩니다

{% include news-card.html
  title="GitHub Copilot 앱이 이제 사용량 메트릭 API에서 제공됩니다"
  url="https://github.blog/changelog/2026-07-17-github-copilot-app-now-available-in-the-usage-metrics-api"
  image="https://github.blog/wp-content/uploads/2026/07/622915765-3eae91f4-3887-4da9-a456-537508756b81.jpeg"
  summary="GitHub Copilot 앱 사용량이 이제 usage metrics API의 enterprise 및 organization 1일 및 28일 보고서에 포함되어, 관리자들이 해당 데이터를 확인할 수 있게 되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot 앱 사용량이 이제 usage metrics API의 enterprise 및 organization 1일 및 28일 보고서에 포함되어, 관리자들이 해당 데이터를 확인할 수 있게 되었습니다.


---

### 4.3 Copilot 코드 리뷰: 사용자 정의 및 구성 가능성 개선

{% include news-card.html
  title="Copilot 코드 리뷰: 사용자 정의 및 구성 가능성 개선"
  url="https://github.blog/changelog/2026-07-17-copilot-code-review-customization-and-configurability-improvements"
  image="https://github.blog/wp-content/uploads/2026/07/623369388-f6be276d-7e45-4ba4-9ec6-e60565bffad4.jpg"
  summary="GitHub의 Copilot code review가 방화벽, 커스텀 설정 단계, 독립적인 runner 구성을 도입했으며, head branch에서 커스텀 명령어를 읽어 테스트와 검증을 용이하게 하는 맞춤화 및 구성 가능성 개선이 이루어졌습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub의 Copilot code review가 방화벽, 커스텀 설정 단계, 독립적인 runner 구성을 도입했으며, head branch에서 커스텀 명령어를 읽어 테스트와 검증을 용이하게 하는 맞춤화 및 구성 가능성 개선이 이루어졌습니다.


---

## 5. 블록체인 뉴스

### 5.1 Ocean Mining 부사장 Jason Hughes: BIP-110, 채굴자 시그널링 1% 미만 유지로 실패할 전망

{% include news-card.html
  title="Ocean Mining 부사장 Jason Hughes: BIP-110, 채굴자 시그널링 1% 미만 유지로 실패할 전망"
  url="https://bitcoinmagazine.com/bitcoin-mining/ocean-mining-vp-jason-hughes-bip-110-on-track-to-fail-as-miner-signaling-stays-below-1"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/tn-5.webp"
  summary="Ocean Mining의 개발 및 엔지니어링 부사장 Jason Hughes는 BIP-110이 측정 가능한 합의를 확보하지 못했으며, 중요 블록 961632 윈도우를 앞두고 노드 시그널링은 7-15%, 해시레이트 지원은 1% 미만에 머물러 있어 실패할 것으로 예상된다고 주장했다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Ocean Mining의 개발 및 엔지니어링 부사장 Jason Hughes는 BIP-110이 측정 가능한 합의를 확보하지 못했으며, 중요 블록 961632 윈도우를 앞두고 노드 시그널링은 7-15%, 해시레이트 지원은 1% 미만에 머물러 있어 실패할 것으로 예상된다고 주장했다.


---

### 5.2 SBI Holdings, MAS 승인 후 싱가포르 Coinhako 지분 과반수 확보

{% include news-card.html
  title="SBI Holdings, MAS 승인 후 싱가포르 Coinhako 지분 과반수 확보"
  url="https://bitcoinmagazine.com/news/sbi-holdings-takes-majority-stake-coinhako"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/SBI-Holdings-Takes-Majority-Stake-in-Singapores-Coinhako-After-MAS-Approval-.jpg"
  summary="SBI Holdings가 싱가포르 통화청(MAS)의 승인을 받아 싱가포르의 Coinhako 지분을 과반수 인수했습니다. 이번 인수는 일본과 동남아시아를 연결하는跨境 디지털 자산 네트워크 구축을 강화하기 위한 전략적 움직임입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

SBI Holdings가 싱가포르 통화청(MAS)의 승인을 받아 싱가포르의 Coinhako 지분을 과반수 인수했습니다. 이번 인수는 일본과 동남아시아를 연결하는跨境 디지털 자산 네트워크 구축을 강화하기 위한 전략적 움직임입니다.


---

### 5.3 비트코인 채굴 대기업 Foundry, BIP-110 소프트 포크 투표 요청

{% include news-card.html
  title="비트코인 채굴 대기업 Foundry, BIP-110 소프트 포크 투표 요청"
  url="https://bitcoinmagazine.com/news/foundry-asks-bitcoin-miners-vote-bip-110"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/Bitcoin-Mining-Giant-Foundry-Asks-Miners-To-Vote-on-BIP-110-Soft-Fork.jpg"
  summary="비트코인 채굴 대기업 Foundry Digital이 자사의 채굴 풀을 이용하는 고객들에게 BIP-110 소프트 포크에 대한 투표를 요청했습니다. 이는 Bitcoin Magazine이 Mathew Di Salvo와 Micah Zimmerman의 기사를 통해 보도한 내용입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

비트코인 채굴 대기업 Foundry Digital이 자사의 채굴 풀을 이용하는 고객들에게 BIP-110 소프트 포크에 대한 투표를 요청했습니다. 이는 Bitcoin Magazine이 Mathew Di Salvo와 Micah Zimmerman의 기사를 통해 보도한 내용입니다.


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [먼 별의 생명체 거주 가능 영역에 있는 지구형 행성에서 최초로 대기 발견](https://news.hada.io/topic?id=31539) | GeekNews (긱뉴스) | 지구에서 48광년 떨어진 암석 행성 LHS 1140 b 에서 대기가 확인돼, 태양계 밖 생명체 거주 가능 영역의 지구형 행성으로는 첫 사례가 됨 지금까지 검출된 기체는 상층 대기에 있을 것으로 추정되는 헬륨 뿐이지만, 더 낮은 대기층에 다른 기체가 존재할 가능성은 남 |
| [2026년 7월 오픈소스 AI 현황](https://news.hada.io/topic?id=31538) | GeekNews (긱뉴스) | 오픈 웨이트 모델은 코딩·지시 이행·일반 지식에서 폐쇄형과 비슷한 수준에 도달했고, 추론 비용도 36개월간 50배 하락 하면서 경쟁의 중심이 모델 자체에서 에이전트 하네스 로 이동함 2026년 중반 OpenRouter에서 오픈 웨이트가 토큰 처리량의 과반을 차지하고 상위 |
| [Apple, 법적 서한으로 OpenAI 직원 수십 명 겨냥](https://news.hada.io/topic?id=31537) | GeekNews (긱뉴스) | Apple, 법적 서한으로 OpenAI 직원 수십 명 겨냥 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 8건 | 기타 주제 |
| **AI/ML** | 6건 | The Hacker News 관련 동향, NVIDIA AI Blog 관련 동향, OpenAI Blog 관련 동향 |
| **클라우드 보안** | 1건 | The Hacker News 관련 동향 |
| **공급망 보안** | 1건 | The Hacker News 관련 동향 |
| **컨테이너/K8s** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(8건)입니다. **AI/ML** 분야에서는 The Hacker News 관련 동향, NVIDIA AI Blog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **새로운 wp2shell WordPress 핵심 결함으로 인증되지 않은 공격자가 코드 실행 가능** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **7개의 악성 Vite npm 패키지, 블록체인 C2를 이용해 RAT 유포** 관련 보안 검토 및 모니터링
- [ ] **새로운 NadMesh 봇넷, 노출된 AI 서비스에서 클라우드 키와 Kubernetes 토큰 수집** 관련 보안 검토 및 모니터링
- [ ] **GoldenEyeDog 서브그룹, DigiCert 침해 및 코드 서명 인증서 도난과 연계** 관련 보안 검토 및 모니터링
- [ ] **Amazon Quick으로 영업 조직을 혁신하세요: 새로운 에이전틱 AI 팀메이트** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **NVIDIA Vera Rubin, 포스트 트레이닝 워크로드에서 달러당 지능을 극대화 — 에이전틱 AI의 핵심 지표** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
