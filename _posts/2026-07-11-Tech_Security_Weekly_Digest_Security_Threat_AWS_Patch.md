---
layout: post
title: "2026년 07월 11일 주간 보안 다이제스트: DNS 유출·클라우드·패치 (29건)"
date: 2026-07-11 10:51:23 +0900
last_modified_at: 2026-07-11T10:51:23+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Threat, AWS, Patch]
excerpt: "긴급 - Progress, ShareFile 고객에게 보안 위협으로 · Injective Labs GitHub 침해로 지갑 키를 탈취하는이 부각된 2026년 07월 11일 보안 다이제스트 — 29건의 이슈와 실행 가능한 대응 액션을 정리합니다. 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다."
description: "2026년 07월 11일 보안 뉴스 요약. The Hacker News 등 29건을 분석하고 긴급 - Progress, ShareFile, Injective Labs GitHub 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Threat, AWS]
author: Twodragon
comments: true
image: /assets/images/2026-07-11-Tech_Security_Weekly_Digest_Security_Threat_AWS_Patch.svg
image_alt: "Progress, ShareFile, Injective Labs GitHub, 6 U-Boot - security digest overview"
toc: true
summary_card:
  title: "2026년 07월 11일 주간 보안 다이제스트: DNS 유출·클라우드·패치 (29건)"
  period: "2026년 07월 11일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Security"
    - "Threat"
    - "AWS"
    - "Patch"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "긴급 - Progress, ShareFile 고객에게 보안 위협으로 Storage Zone" }
    - { source: "The Hacker News", title: "Injective Labs GitHub 침해로 지갑 키를 탈취하는 npm 패키지 유포" }
    - { source: "The Hacker News", title: "6가지 새로운 U-Boot 취약점으로 악성 이미지가 부팅 시 장치를 충돌시키거나 코드를 실행할 수 있어" }
    - { source: "Google Cloud Blog", title: "영국 금융 부문의 핵심 제3자로서 복원력에 기여" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 07월 11일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

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

#### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | 긴급 - Progress, ShareFile 고객에게 보안 위협으로 Storage Zone Controller 종료 지시 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Injective Labs GitHub 침해로 지갑 키를 탈취하는 npm 패키지 유포 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 6가지 새로운 U-Boot 취약점으로 악성 이미지가 부팅 시 장치를 충돌시키거나 코드를 실행할 수 있어 | 🟠 High |
| 🤖 **AI/ML** | OpenAI Blog | Deutsche Telekom, AI로 통신을 재설계하는 방법 | 🟡 Medium |
| 🤖 **AI/ML** | Cointelegraph | TeraWulf, Anthropic 연계 데이터센터 위해 35억 달러 부채 조달 검토: 보고서 | 🟡 Medium |
| 🤖 **AI/ML** | AWS Machine Learning | Amazon SageMaker AI 서버리스 모델 커스터마이징으로 NVIDIA Nemotron 3 모델 미세 조정하기 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 영국 금융 부문의 핵심 제3자로서 복원력에 기여 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 프런티어와 센터: 평가를 평가하는 사람은 누구인가? | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Google Cloud의 새로운 소식 | 🟠 High |
| ⚙️ **DevOps** | GitHub Changelog | CodeQL 2.26.0, Kotlin 2.4.0 지원 및 AI 프롬프트 인젝션 탐지 기능 추가 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: 6가지 새로운 U-Boot 취약점으로 악성 이미지가 부팅 시 장치를 충돌시키거나 코드를 실행할 수 있어, Google Cloud의 새로운 소식 등 High 등급 위협 2건에 대한 탐지 강화가 필요합니다.
- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | Medium | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 긴급 - Progress, ShareFile 고객에게 보안 위협으로 Storage Zone Controller 종료 지시

{% include news-card.html
  title="긴급 - Progress, ShareFile 고객에게 보안 위협으로 Storage Zone Controller 종료 지시"
  url="https://thehackernews.com/2026/07/urgent-progress-tells-sharefile.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgULXOG2_Ph1198nw2lOea2pYE9u1GkPHaaMlzhpO48pOmejpWKFuHbchUac5JIRQHGiIMMTefXq-LktA8AjsqqMIsBS54bLaludxIJbq7chYfo_Vsoqf9Xi7YomnSUL9wHAYa5InCST76k1aP10VMmNKK_MDLD3o5zNXyB4ODMRMl0DbLkz9f2mg2k2S8/s1600/progress.jpg"
  summary="Progress Software가 ShareFile 고객에게 Storage Zone Controller를 실행 중인 Windows 서버를 종료하라고 지시했으며, 이는 ”신뢰할 수 있는 외부 보안 위협”에 대응하기 위한 조치라고 The Hacker News에 확인했습니다. 회사는 과도한 주의 차원에서 해당 계정에 대한 접근을 일시적으로 차단했습니다."
  source="The Hacker News"
  severity="Medium"
%}

#### DevSecOps 관점 분석: Progress ShareFile Storage Zone Controller 보안 위협

#### 기술적 배경 및 위협 분석

Progress ShareFile은 기업용 파일 공유 및 협업 플랫폼으로, Storage Zone Controller(SZC)는 고객이 자체 인프라에서 파일 저장소를 운영할 수 있게 해주는 Windows 기반 구성 요소입니다. 이번 경고는 SZC가 실행 중인 Windows 서버를 즉시 종료하라는 긴급 조치로, "신뢰할 수 있는 외부 보안 위협"에 대응하기 위한 것입니다.

**핵심 위협 분석:**
- **공격 표면**: SZC는 Windows 서버에서 실행되며, 일반적으로 네트워크에 노출되는 엔드포인트입니다. 공격자는 인증 우회, 원격 코드 실행(RCE) 또는 권한 상승 취약점을 통해 SZC를 장악할 가능성이 있습니다.
- **데이터 유출 위험**: SZC는 고객 파일 저장소를 제어하므로, 침해 시 기업 데이터(비즈니스 문서, 개인정보, 지적재산권)가 유출될 수 있습니다.
- **공급망 위험**: ShareFile이 SaaS 형태로 제공되지만, SZC는 고객 관리형 인프라이므로 패치 지연이나 설정 오류가 위협을 증폭시킵니다.
- **제로데이 가능성**: Progress가 "과도한 주의"로 계정 접근을 차단한 점은 아직 패치가 없는 제로데이 취약점일 가능성을 시사합니다.

#### 실무 영향 분석

**DevSecOps 파이프라인 및 운영 영향:**
- **CI/CD 중단**: SZC 종료로 인해 파일 공유 기반의 빌드 아티팩트 전달, 로그 수집, 배포 스크립트 접근이 차단됩니다.
- **규정 준수 위험**: 금융, 의료 등 규제 산업에서 파일 저장소 중단은 데이터 보존 및 접근 감사 요건 위반을 초래할 수 있습니다.
- **백업 및 재해 복구 마비**: SZC가 백업 저장소로 사용된 경우, 복구 프로세스 전체가 중단됩니다.
- **공급망 연쇄 영향**: ShareFile을 통해 외부 협업(고객, 파트너)하던 프로세스가 마비되어 비즈니스 연속성에 타격이 발생합니다.

**우선 대응 방향:**
- 즉시 SZC 서버 종료 후, 대체 파일 전송 수단(예: 임시 SFTP 서버, 암호화된 클라우드 스토리지)으로 전환
- SZC와 연동된 모든 시스템(AD, SIEM, 백업 솔루션)의 연결 차단 및 로그 보존
- Progress의 공식 패치 및 복구 지침 발표까지 대기

---

### 1.2 Injective Labs GitHub 침해로 지갑 키를 탈취하는 npm 패키지 유포

{% include news-card.html
  title="Injective Labs GitHub 침해로 지갑 키를 탈취하는 npm 패키지 유포"
  url="https://thehackernews.com/2026/07/injective-labs-github-compromise-pushes.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhTNxzPo9jxkW3GuuZLBgtPOrG3vZ3va6E710jDJu_JF0jCpyQ1JTpymdVwdSH2VHL6-Ib6YLInvKsuNwgFJxna1nvDhwKMZ_hycTik5OgQniZei2FQ59-F3s80lsnPmhQ1aJsr7qIWWrf63V0AtHQxd_1Nlk6LkVEheoN5lRYH8aTeBoJ-kM1-bOjUgAwa/s1600/npm-malware-2.jpg"
  summary="Injective Labs의 GitHub 저장소가 침해되어 npm 레지스트리에 악성 패키지 @injectivelabs/sdk-ts@1.20.21이 게시되었으며, 이 패키지는 가짜 텔레메트리 기능을 통해 암호화폐 지갑의 개인 키와 니모닉 시드 구문을 탈취하도록 설계되었습니다."
  source="The Hacker News"
  severity="Medium"
%}

#### DevSecOps 관점 Injective Labs GitHub 침해 사고 분석

#### 기술적 배경 및 위협 분석

이번 사고는 **공급망 공급망 공격(Supply Chain Attack)** 의 전형적인 사례로, 공격자가 Injective Labs의 GitHub 저장소에 접근 권한을 획득한 후 정상 SDK 프로젝트에 악성 코드를 주입했습니다. 특히 `@injectivelabs/sdk-ts@1.20.21` 버전에 가짜 원격 측정(Telemetry) 기능으로 위장한 **지갑 개인키 및 시드 구문 탈취 코드**를 포함시켰습니다.

**핵심 위협 요소:**
- **GitHub 저장소 권한 탈취**: 공격자는 CI/CD 파이프라인에 사용되는 토큰이나 개발자 계정을 탈취한 것으로 추정
- **npm 패키지 변조**: 정상 패키지에 악성 코드를 삽입한 후 npm 레지스트리에 배포
- **데이터 유출 채널**: 가짜 텔레메트리 기능을 통해 암호화폐 지갑 데이터를 외부 서버로 전송
- **타겟팅**: 블록체인/DeFi 개발자 및 사용자들의 개인키 탈취에 특화

이러한 공격은 **소프트웨어 공급망의 신뢰성**을 근본적으로 훼손하며, 특히 암호화폐 관련 프로젝트는 금전적 가치가 높아 공격자에게 매력적인 표적이 됩니다.

#### 실무 영향 분석

DevSecOps 실무자 관점에서 이 사고가 시사하는 바는 다음과 같습니다.

**즉각적 영향:**
- 해당 버전(1.20.21)을 사용한 모든 프로젝트의 암호화폐 지갑 개인키 노출 가능성
- 의존성 트리를 통해 간접적으로 영향을 받은 프로젝트들
- Injective Labs의 브랜드 신뢰도 하락 및 커뮤니티 혼란

**장기적 영향:**
- **CI/CD 파이프라인 보안 강화 필요성**: GitHub Actions, npm publish 권한 등 자동화된 배포 과정의 보안 취약점 노출
- **npm 패키지 서명(Package Signing) 미적용 문제**: 현재 npm은 패키지 서명이 선택사항이어서 변조 탐지가 어려움
- **의존성 검증 프로세스 재고**: lock 파일과 checksum 검증만으로는 부족함을 입증

**DevSecOps 실무 시사점:**
- 패키지 관리자와 CI/CD 도구의 권한을 최소 권한 원칙으로 운영해야 함
- 오픈소스 패키지의 변조 여부를 실시간으로 탐지하는 메커니즘 필요
- 암호화폐 관련 프로젝트는 특히 중요 패키지에 대한 추가 검증 레이어 도입 필요

---

### 1.3 6가지 새로운 U-Boot 취약점으로 악성 이미지가 부팅 시 장치를 충돌시키거나 코드를 실행할 수 있어

{% include news-card.html
  title="6가지 새로운 U-Boot 취약점으로 악성 이미지가 부팅 시 장치를 충돌시키거나 코드를 실행할 수 있어"
  url="https://thehackernews.com/2026/07/six-new-u-boot-flaws-could-let.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEihuE5rUYRadx5Q2auJjv9dVeFNIP8XSwSTaH0PDwGLUA54MXlPy3AyI532a8OnhXadtWnCCH30qvUKW9C3rCOu1LPld1or5_lXwNhRVqbohHNInDzNd1f9E77Sox5yB-ir7H69LmlYRKnoqnFASOMFa2TIK2RfTThJvu_oofIXHCpiRbXGXWy-bquBWsw/s1600/bootloader.gif"
  summary="Binarly의 연구원들이 U-Boot에서 6개의 새로운 취약점을 발견했으며, 이 중 4개는 기기를 충돌시키고 2개는 공격자가 부트로더에 악성 이미지를 주입해 자체 코드를 실행할 수 있게 합니다."
  source="The Hacker News"
  severity="High"
%}

#### DevSecOps 관점 U-Boot 취약점 분석

#### 기술적 배경 및 위협 분석

U-Boot는 임베디드 시스템 및 데이터센터 서버의 BMC(Baseboard Management Controller) 등에서 사용되는 오픈소스 부트로더로, 하드웨어 초기화와 운영체제 로딩을 담당한다. Binarly 연구진이 발견한 6개의 취약점 중 4개는 서비스 거부(DoS)를 유발하며, 나머지 2개는 악의적인 이미지 삽입을 통해 부트로더 단계에서 임의 코드 실행(RCE)을 가능하게 한다.

**핵심 위협**: 
- 부트로더는 OS 보안 메커니즘이 활성화되기 전에 실행되므로, 이 단계에서의 RCE는 전체 시스템의 신뢰 루트(Root of Trust)를 붕괴시킨다.
- 공격자는 네트워크 부트(PXE), USB, SD카드 등을 통해 조작된 부트 이미지를 주입할 수 있으며, IoT 기기(라우터, IP 카메라)와 서버 BMC 모두 취약하다.
- 특히 데이터센터 환경에서는 BMC를 통해 서버 전원 제어, 펌웨어 업데이트 등이 가능하므로, 단일 취약점으로 대규모 인프라 장애로 이어질 수 있다.

#### 실무 영향 분석

DevSecOps 파이프라인에서 부트로더 취약점은 일반적으로 간과되기 쉬운 영역이다. 다음과 같은 실무적 영향을 고려해야 한다:

- **CI/CD 파이프라인 위험**: 컨테이너 이미지나 VM 이미지 빌드 시 사용되는 베이스 이미지가 취약한 U-Boot 버전을 포함할 경우, 최종 배포 환경 전체가 위험에 노출된다.
- **펌웨어 업데이트 체계**: 대부분의 IoT/엣지 디바이스는 OTA 업데이트를 지원하지만, 부트로더 패치는 제조사 지원 종료나 낮은 우선순위로 인해 지연되거나 누락된다.
- **공급망 보안**: 장비 제조사가 사용하는 U-Boot 버전과 패치 현황을 추적하지 않으면, 취약한 펌웨어가 그대로 배포된다.
- **SBOM(Software Bill of Materials) 관리**: 부트로더 수준의 컴포넌트가 SBOM에 포함되지 않는 경우가 많아, 취약점 스캐닝에서 누락된다.

---

## 2. AI/ML 뉴스

### 2.1 Deutsche Telekom, AI로 통신을 재설계하는 방법

{% include news-card.html
  title="Deutsche Telekom, AI로 통신을 재설계하는 방법"
  url="https://openai.com/index/deutsche-telekom"
  summary="Deutsche Telekom은 OpenAI를 활용해 AI 기반 통신사로 전환 중이며, 고객 서비스, 직원 워크플로우, 네트워크 운영 및 음성 기술의 미래를 혁신하고 있습니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

Deutsche Telekom은 OpenAI를 활용해 AI 기반 통신사로 전환 중이며, 고객 서비스, 직원 워크플로우, 네트워크 운영 및 음성 기술의 미래를 혁신하고 있습니다.

---

### 2.2 TeraWulf, Anthropic 연계 데이터센터 위해 35억 달러 부채 조달 검토: 보고서

{% include news-card.html
  title="TeraWulf, Anthropic 연계 데이터센터 위해 35억 달러 부채 조달 검토: 보고서"
  url="https://cointelegraph.com/news/terawulf-3-5-billion-debt-raise-anthropic-data-center?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/hi-what-is-decentralized-web-hosting-and-how-does-it-work22.jpg"
  summary="비트코인 채굴 기업 TeraWulf가 Morgan Stanley 주도로 35억 달러의 부채 조달을 추진 중이며, 이 자금은 AI 기업 Anthropic에 임대된 켄터키 데이터 센터 캠퍼스에 사용될 예정이다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

비트코인 채굴 기업 TeraWulf가 Morgan Stanley 주도로 35억 달러의 부채 조달을 추진 중이며, 이 자금은 AI 기업 Anthropic에 임대된 켄터키 데이터 센터 캠퍼스에 사용될 예정이다.

---

### 2.3 Amazon SageMaker AI 서버리스 모델 커스터마이징으로 NVIDIA Nemotron 3 모델 미세 조정하기

{% include news-card.html
  title="Amazon SageMaker AI 서버리스 모델 커스터마이징으로 NVIDIA Nemotron 3 모델 미세 조정하기"
  url="https://aws.amazon.com/blogs/machine-learning/fine-tune-nvidia-nemotron-3-models-with-amazon-sagemaker-ai-serverless-model-customization/"
  summary="이 게시글은 NVIDIA Nemotron 3 아키텍처의 특징과 미세 조정 기법을 설명하며, Amazon SageMaker AI의 serverless model customization을 통해 SageMaker Studio에서 모델을 커스터마이징하는 방법을 단계별로 안내합니다."
  source="AWS Machine Learning Blog"
  severity="Medium"
%}

#### 요약

이 게시글은 NVIDIA Nemotron 3 아키텍처의 특징과 미세 조정 기법을 설명하며, Amazon SageMaker AI의 serverless model customization을 통해 SageMaker Studio에서 모델을 커스터마이징하는 방법을 단계별로 안내합니다.

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 영국 금융 부문의 핵심 제3자로서 복원력에 기여

{% include news-card.html
  title="영국 금융 부문의 핵심 제3자로서 복원력에 기여"
  url="https://cloud.google.com/blog/products/identity-security/contributing-to-uk-financial-sector-resilience-as-a-critical-third-party/"
  summary="Google Cloud EMEA가 영국 재무부로부터 금융 부문의 critical third party(CTP)로 지정되었으며, 이는 운영 탄력성과 책임 있는 혁신에 대한 Google Cloud의 지속적인 약속의 일환입니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Cloud EMEA가 영국 재무부로부터 금융 부문의 critical third party(CTP)로 지정되었으며, 이는 운영 탄력성과 책임 있는 혁신에 대한 Google Cloud의 지속적인 약속의 일환입니다.

---

### 3.2 프런티어와 센터: 평가를 평가하는 사람은 누구인가?

{% include news-card.html
  title="프런티어와 센터: 평가를 평가하는 사람은 누구인가?"
  url="https://cloud.google.com/blog/products/data-analytics/evaluate-agent-performance/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/Who_Evaluates_the_Evaluations__-_FP_blog.max-1000x1000.jpg"
  summary="Google Cloud이 AI 에이전트 평가의 신뢰성을 높이기 위해 정보 이론의 surprisal(놀라움) 지표와 반복적 난이도 조절(iSQR)을 적용한 Discovery Bench 메타벤치마크를 소개했습니다. 단일 표현 방식의 벤치마크가 성능 급락(capability cliff)을 감추고 정답 데이터셋 자체에 오류가 있을 수 있음을 지적하며, 평가자를 평가하는 문제를 다룹니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Cloud이 AI 에이전트 평가의 신뢰성을 높이기 위해 정보 이론의 surprisal(놀라움) 지표와 반복적 난이도 조절(iSQR)을 적용한 Discovery Bench 메타벤치마크를 소개했습니다. 단일 표현 방식의 벤치마크가 성능 급락(capability cliff)을 감추고 정답 데이터셋 자체에 오류가 있을 수 있음을 지적하며, 평가자를 평가하는 문제를 다룹니다.

---

### 3.3 Google Cloud의 새로운 소식

{% include news-card.html
  title="Google Cloud의 새로운 소식"
  url="https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud/"
  summary="Google Cloud의 최신 업데이트, 공지사항, 리소스, 이벤트 및 학습 기회를 한곳에서 확인할 수 있습니다. Google Cloud 블로그에서 원하는 정보를 찾는 방법에 대한 팁도 제공됩니다."
  source="Google Cloud Blog"
  severity="High"
%}

#### 요약

Google Cloud의 최신 업데이트, 공지사항, 리소스, 이벤트 및 학습 기회를 한곳에서 확인할 수 있습니다. Google Cloud 블로그에서 원하는 정보를 찾는 방법에 대한 팁도 제공됩니다.

---

## 4. DevOps & 개발 뉴스

### 4.1 CodeQL 2.26.0, Kotlin 2.4.0 지원 및 AI 프롬프트 인젝션 탐지 기능 추가

{% include news-card.html
  title="CodeQL 2.26.0, Kotlin 2.4.0 지원 및 AI 프롬프트 인젝션 탐지 기능 추가"
  url="https://github.blog/changelog/2026-07-10-codeql-2-26-0-adds-kotlin-2-4-0-support-and-ai-prompt-injection-detection"
  image="https://github.blog/wp-content/uploads/2026/07/620083714-db8cf0d2-f457-4e23-b01d-acb6c26d9599.jpeg"
  summary="CodeQL 2.26.0이 Kotlin 2.4.0을 지원하고 AI prompt injection 탐지 기능을 추가했습니다. 이는 GitHub code scanning의 정적 분석 엔진인 CodeQL의 최신 릴리스입니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

CodeQL 2.26.0이 Kotlin 2.4.0을 지원하고 AI prompt injection 탐지 기능을 추가했습니다. 이는 GitHub code scanning의 정적 분석 엔진인 CodeQL의 최신 릴리스입니다.

---

### 4.2 비밀 스캐닝 탐지기 유형의 명칭을 명확히 함

{% include news-card.html
  title="비밀 스캐닝 탐지기 유형의 명칭을 명확히 함"
  url="https://github.blog/changelog/2026-07-10-clearer-names-for-secret-scanning-detector-types"
  image="https://github.blog/wp-content/uploads/2026/07/571554102-6349f5b6-b0b7-4130-9300-6d5d87e0b6e9_e29286.jpg"
  summary="GitHub이 secret scanning에서 사용하는 detector type의 이름을 각각이 비밀을 찾는 방식을 더 잘 반영하도록 변경했습니다. 이는 명칭 변경에 해당하며, 사용자가 secret scanning을 더 쉽게 이해할 수 있도록 하기 위한 조치입니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub이 secret scanning에서 사용하는 detector type의 이름을 각각이 비밀을 찾는 방식을 더 잘 반영하도록 변경했습니다. 이는 명칭 변경에 해당하며, 사용자가 secret scanning을 더 쉽게 이해할 수 있도록 하기 위한 조치입니다.

---

### 4.3 더 나은 도구가 Copilot 코드 리뷰를 오히려 악화시켰다. 실제로 개선한 방법은 이렇다.

{% include news-card.html
  title="더 나은 도구가 Copilot 코드 리뷰를 오히려 악화시켰다. 실제로 개선한 방법은 이렇다."
  url="https://github.blog/ai-and-ml/github-copilot/better-tools-made-copilot-code-review-worse-heres-how-we-actually-improved-it/"
  image="https://github.blog/wp-content/uploads/2026/01/generic-github-copilot-commit-logo.png"
  summary="GitHub 블로그에 따르면, Copilot 코드 리뷰에 더 나은 도구를 도입했지만 오히려 성능이 저하되었고, 이후 공유 Unix 스타일 코드 탐색 도구로 마이그레이션하여 에이전트 워크플로를 pull request 증거 중심으로 재구성함으로써 리뷰 비용을 절감했습니다."
  source="GitHub Engineering Blog"
  severity="Medium"
%}

#### 요약

GitHub 블로그에 따르면, Copilot 코드 리뷰에 더 나은 도구를 도입했지만 오히려 성능이 저하되었고, 이후 공유 Unix 스타일 코드 탐색 도구로 마이그레이션하여 에이전트 워크플로를 pull request 증거 중심으로 재구성함으로써 리뷰 비용을 절감했습니다.

---

## 5. 블록체인 뉴스

### 5.1 미국 하원의원들, 7월 CLARITY Act 표결 및 윤리 문제 해결 촉구

{% include news-card.html
  title="미국 하원의원들, 7월 CLARITY Act 표결 및 윤리 문제 해결 촉구"
  url="https://bitcoinmagazine.com/news/u-s-house-urge-senate-vote-clarity-act"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/U.S.-Representatives-Urge-Senate-to-Vote-on-CLARITY-Act-in-July-Address-Ethics-Concerns.jpg"
  summary="미국 하원의원 French Hill이 8월 휴회 전에 상원이 CLARITY Act에 대한 표결을 진행할 것을 촉구했습니다. 이 법안은 투명한 암호화폐 시장 프레임워크를 구축하고 트럼프 대통령의 디지털 자산 벤처와 관련된 윤리적 우려를 해결할 것이라고 주장했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

미국 하원의원 French Hill이 8월 휴회 전에 상원이 CLARITY Act에 대한 표결을 진행할 것을 촉구했습니다. 이 법안은 투명한 암호화폐 시장 프레임워크를 구축하고 트럼프 대통령의 디지털 자산 벤처와 관련된 윤리적 우려를 해결할 것이라고 주장했습니다.

---

### 5.2 Circle (CRCL), OCC의 국가 신탁 은행 최종 승인 획득

{% include news-card.html
  title="Circle (CRCL), OCC의 국가 신탁 은행 최종 승인 획득"
  url="https://bitcoinmagazine.com/news/circle-crcl-wins-final-occ-approval"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/Circle-CRCL-Wins-Final-OCC-Approval-for-National-Trust-Bank.jpg"
  summary="Circle(CRCL)이 OCC의 최종 승인을 받아 전국 신탁은행을 설립하게 되었으며, 이를 통해 USDC 준비금을 연방 감독 하에 두고 규제된 디지털 자산 수탁 사업을 확장할 수 있게 되었습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Circle(CRCL)이 OCC의 최종 승인을 받아 전국 신탁은행을 설립하게 되었으며, 이를 통해 USDC 준비금을 연방 감독 하에 두고 규제된 디지털 자산 수탁 사업을 확장할 수 있게 되었습니다.

---

### 5.3 Metaplanet, 비트코인 담보 디지털 신용을 일본에 도입하기 위한 공동 연구 발표

{% include news-card.html
  title="Metaplanet, 비트코인 담보 디지털 신용을 일본에 도입하기 위한 공동 연구 발표"
  url="https://bitcoinmagazine.com/news/metaplanet-announces-joint-study-bitcoin"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/Metaplanet-Acquires-Siiibo-Securities-in-Push-to-Build-Bitcoin-Financial-Ecosystem.jpg"
  summary="Metaplanet이 비트코인 전략을 재무부 축적을 넘어 확장하며, 일본 부채 시장을 재편할 수 있는 토큰화된 비트코인 담보 신용 상품을 탐구하기 위한 공동 연구를 발표했습니다. 이 연구는 비트코인 기반 디지털 신용을 일본에 도입하는 것을 목표로 합니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Metaplanet이 비트코인 전략을 재무부 축적을 넘어 확장하며, 일본 부채 시장을 재편할 수 있는 토큰화된 비트코인 담보 신용 상품을 탐구하기 위한 공동 연구를 발표했습니다. 이 연구는 비트코인 기반 디지털 신용을 일본에 도입하는 것을 목표로 합니다.

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [초당 100만 건, LINE 앱에 Apache Kafka 종단 간 암호화 적용기](https://techblog.lycorp.co.jp/ko/applying-e2ee-to-apache-kafka-in-line-app) | LINE Engineering | 들어가며: 왜 Kafka 종단 간 암호화인가?LINE 메신저에서는 매일 수십억 건의 메시지가 오갑니다. 이 방대한 데이터는 다양한 시스템으로 전달되며, 그중에는 개인 정보와 같이 |
| [Apple, OpenAI를 상대로 소송 제기하며 전 직원들이 영업비밀을 훔쳤다고 주장](https://news.hada.io/topic?id=31318) | GeekNews (긱뉴스) | 애플은 전 직원 2명과 OpenAI 및 Jony Ive의 io Products를 상대로 영업비밀 부정취득 과 계약 위반 소송을 제기하며, OpenAI의 하드웨어 진출이 Apple 기밀에 기대고 있다고 주장 소장에 따르면 OpenAI는 io Products 인수와 전 Apple 임원·엔지니어 채용을 통해 소비자 하드웨어 시 |
| [뉴욕시, 기만적 구독 관행 금지 예정](https://news.hada.io/topic?id=31317) | GeekNews (긱뉴스) | 뉴욕시는 헬스장 멤버십·스트리밍 같은 반복 과금에서 소비자가 빠져나오기 어렵게 만드는 기만적 구독 관행 을 금지하며, 미국 도시 중 첫 사례가 됨 10월 1일 부터 간단한 해지 방법을 제공하지 않는 기업은 사용자 구독 1건당 525달러 와 환급 수 |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 7건 | 기타 주제 |
| **AI/ML** | 5건 | OpenAI Blog 관련 동향, AWS Machine Learning Blog 관련 동향, GitHub Changelog 관련 동향 |
| **클라우드 보안** | 3건 | AWS Machine Learning Blog 관련 동향, Google Cloud Blog 관련 동향, Oracle Database@AWS 네트워크 구성 가이드 |
| **공급망 보안** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(7건)입니다. **AI/ML** 분야에서는 OpenAI Blog 관련 동향, AWS Machine Learning Blog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **긴급 - Progress, ShareFile 고객에게 보안 위협으로 Storage Zone Controller 종료 지시** 관련 보안 영향도 분석 및 모니터링 강화

### P1 (7일 내)

- [ ] **6가지 새로운 U-Boot 취약점으로 악성 이미지가 부팅 시 장치를 충돌시키거나 코드를 실행할 수 있어** 관련 보안 검토 및 모니터링
- [ ] **Laser Attack, 패치 불가능한 카드에서 Tangem Wallet 비밀번호 초기화** 관련 보안 검토 및 모니터링
- [ ] **새로운 MODBEACON RAT, 암호화된 C2 트래픽에 gRPC 스트리밍 사용** 관련 보안 검토 및 모니터링
- [ ] **Henry Schein One의 Amazon SageMaker AI 기반 실시간 치과 이미지 검증** 관련 보안 검토 및 모니터링
- [ ] **AWS에서 Stardog와 Amazon Bedrock AgentCore로 에이전틱 AI를 위한 시맨틱 레이어 구축하기** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Deutsche Telekom, AI로 통신을 재설계하는 방법** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
