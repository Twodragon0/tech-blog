---
layout: post
title: "2026년 06월 26일 주간 보안 다이제스트: 클라우드·보안 위협·AI (26건)"
date: 2026-06-26 09:36:30 +0900
last_modified_at: 2026-06-26T09:36:30+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Threat]
excerpt: "2026년 06월 26일 수집한 26건의 보안 이슈 중 Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 · Chrome Ad Blocker, 1000만 회 이상 설치를 중심으로 영향 범위와 패치 우선순위를 분석합니다. 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다."
description: "2026년 06월 26일 보안 뉴스 요약. Microsoft Security Blog, The Hacker News, BleepingComputer 등 26건을 분석하고 Photo ZIP 캠페인이 호스피탈리티, Chrome Ad Blocker, Anthropic 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Threat]
author: Twodragon
comments: true
image: /assets/images/2026-06-26-Tech_Security_Weekly_Digest_AI_Threat.svg
image_alt: "Photo ZIP, Chrome Ad Blocker, Anthropic - security digest overview"
toc: true
summary_card:
  title: "2026년 06월 26일 주간 보안 다이제스트: 클라우드·보안 위협·AI (26건)"
  period: "2026년 06월 26일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Threat"
    - "2026"
  highlights:
    - { source: "Microsoft Security Blog", title: "Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 위한 Node.js 임플란트 유포" }
    - { source: "The Hacker News", title: "Chrome Ad Blocker, 1000만 회 이상 설치, 유휴 스크립트 주입 기능 발견돼" }
    - { source: "BleepingComputer", title: "Anthropic, 모바일용 데스크톱 스타일 Claude Cowork 테스트 중" }
    - { source: "Google Cloud Blog", title: "STOCKSTAY Another Day: Turla 정보 수집 체계의 최신 추가 사항" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 06월 26일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 26개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 1개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | Microsoft Security B | Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 위한 Node.js 임플란트 유포 | 🟠 High |
| 🔒 **Security** | The Hacker News | Chrome Ad Blocker, 1000만 회 이상 설치, 유휴 스크립트 주입 기능 발견돼 | 🟡 Medium |
| 🔒 **Security** | BleepingComputer | Anthropic, 모바일용 데스크톱 스타일 Claude Cowork 테스트 중 | 🟡 Medium |
| 🤖 **AI/ML** | Meta Engineering Blo | AI 네이티브 시대의 프라이버시 인식 인프라: 자산 분류 사례 연구 | 🟠 High |
| 🤖 **AI/ML** | Google AI Blog | Google Finance의 최신 업그레이드, 새로운 앱 포함 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | 궁극의 여름 세일 조합: Steam 세일과 GeForce NOW 할인 만남 | 🟠 High |
| ☁️ **Cloud** | Google Cloud Blog | STOCKSTAY Another Day: Turla 정보 수집 체계의 최신 추가 사항 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Copilot 코드 리뷰: 분석 깊이 및 효율성 업데이트 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Enterprise-managed settings에서 VS Code 및 GitHub Copilot CLI의 strictKnownMarketplaces를 지원합니다 | 🟡 Medium |
| ⚙️ **DevOps** | Docker Blog | 컨테이너 워크플로우를 위한 SBOM 생성 방법 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 위한 Node.js 임플란트 유포, AI 네이티브 시대의 프라이버시 인식 인프라: 자산 분류 사례 연구, 궁극의 여름 세일 조합: Steam 세일과 GeForce NOW 할인 만남 등 High 등급 위협 4건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 위한 Node.js 임플란트 유포

{% include news-card.html
  title="Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 위한 Node.js 임플란트 유포"
  url="https://www.microsoft.com/en-us/security/blog/2026/06/25/photo-zip-campaign-targeting-hospitality-industry-delivers-node-js-implant-persistent-access/"
  image="https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/03/MS_Actional-Insights_Phishing-social-engineering.jpg"
  summary="Microsoft Threat Intelligence가 유럽과 아시아의 숙박업계를 대상으로 한 다단계 침투 캠페인을 발견했습니다. 이 캠페인은 사진 테마의 ZIP 아카이브와 가짜 이미지 바로가기 파일을 사용하여 지속적인 Node.js 임플란트를 유포하고 탐지를 회피합니다."
  source="Microsoft Security Blog"
  severity="High"
%}

# DevSecOps 실무자 관점에서 본 Photo ZIP 캠페인 분석

## 1. 기술적 배경 및 위협 분석

Microsoft Threat Intelligence가 식별한 이 캠페인은 호텔, 리조트 등 환대 산업을 대상으로 한 **다단계 침투 공격**입니다. 공격자는 사진 테마의 ZIP 아카이브와 가짜 이미지 바로가기(.lnk) 파일을 활용하여 **Node.js 기반 임플란트**를 설치합니다. Node.js는 크로스플랫폼 특성과 낮은 탐지율로 인해 APT 그룹에서 지속적으로 악용되는 런타임 환경입니다.

주요 기술적 특징:
- **ZIP 파일 내 LNK 파일**을 통해 사용자가 이미지를 열도록 유인
- **Node.js 스크립트**를 메모리에서 실행하여 파일리스(fileless) 기법과 유사한 탐지 회피
- **지속성 확보**를 위한 레지스트리 또는 스케줄러 등록
- 유럽 및 아시아 지역 환대 산업 특화 타겟팅

## 2. 실무 영향 분석

DevSecOps 관점에서 이 캠페인은 다음과 같은 실무적 영향을 미칩니다:

- **CI/CD 파이프라인 보안**: Node.js 패키지(npm) 의존성 검증 필요. 악성 패키지 삽입 가능성 증가
- **컨테이너 보안**: Node.js 기반 임플란트가 도커 이미지 빌드 과정에 삽입될 위험
- **엔드포인트 탐지 한계**: LNK 파일과 ZIP 아카이브는 일반적인 EDR에서 간과되기 쉬움
- **클라우드 환경 위험**: Node.js 임플란트가 클라우드 인스턴스에서 실행될 경우 데이터 유출 가능성
- **공급망 위협**: 환대 산업의 POS 시스템, 예약 시스템 등과 연결된 API 취약점 활용 가능

## 3. 대응 체크리스트

- [ ] **CI/CD 파이프라인에 npm 패키지 취약점 스캐너**(예: Snyk, npm audit)를 필수 게이트로 적용하고, 의존성 트리에서 의심스러운 패키지 자동 차단
- [ ] **엔드포인트에서 LNK 파일 및 ZIP 아카이브 실행 제어**를 위한 AppLocker/Windows Defender Application Control 정책 강화
- [ ] **Node.js 런타임 환경에서 비정상적인 네트워크 연결 모니터링** (예: outbound 트래픽 분석, 비인가 프로세스 감지)
- [ ] **컨테이너 이미지 빌드 시 Node.js 베이스 이미지 서명 검증** 및 취약점 스캐닝(Trivy, Clair)을 파이프라인에 통합
- [ ] **환대 산업 특화 위협 인텔리전스 피드 구독** 및 사고 대응 시나리오에 Photo ZIP 캠페인 IOC(침해지표) 포함

---

### 1.2 Chrome Ad Blocker, 1000만 회 이상 설치, 유휴 스크립트 주입 기능 발견돼

{% include news-card.html
  title="Chrome Ad Blocker, 1000만 회 이상 설치, 유휴 스크립트 주입 기능 발견돼"
  url="https://thehackernews.com/2026/06/chrome-ad-blocker-with-10m-installs.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhqtdBDQ0Y38i0JZmDwU6XKiZ1R6HJ0KHe59012E0krnPubG5pJgiTg6IUg4fHEzoW5jm7QyEk8fXOL9swj7FlpXdMcjyn0ltziMhQJD2pYPtzjXimsntV8DFg-c1erOgWkLl8du8eBvJYlukTCDDycp5jSmWNfwmv5WwGKlJRJvZt1GvUZZl24dP2HVDkn/s1600/adblocker.jpg"
  summary="Chrome 웹 스토어에서 1,000만 회 이상 설치된 YouTube 광고 차단 확장 프로그램 'Adblock for YouTube'에서 임의의 JavaScript 코드를 실행할 수 있는 기능이 발견되었습니다. Island의 분석에 따르면, 이 확장 프로그램은 현재 비활성화된 스크립트 주입 기능을 보유하고 있었습니다."
  source="The Hacker News"
  severity="Medium"
%}

# Chrome 광고 차단 확장 프로그램의 지연된 스크립트 삽입 취약점 분석

## 1. 기술적 배경 및 위협 분석

이번 사례는 Chrome Web Store에서 1,000만 회 이상 설치되고 'Featured' 배지를 획득한 **Adblock for YouTube** 확장 프로그램에서 발견된 **지연된 스크립트 삽입(Dormant Script Injection)** 취약점이다. Island의 분석에 따르면, 이 확장 프로그램은 정상적인 광고 차단 기능을 제공하면서도 백그라운드에서 임의의 JavaScript 코드를 실행할 수 있는 숨겨진 기능을 내장하고 있었다.

**핵심 위협 요소:**
- **지연된 실행**: 악성 코드가 즉시 활성화되지 않고 특정 조건(업데이트, 시간, 원격 서버 명령 등)에서 실행되도록 설계됨
- **신뢰 경로 악용**: Chrome Web Store의 'Featured' 배지와 높은 설치 수를 이용한 사용자 신뢰 확보
- **권한 남용**: 광고 차단 기능을 위해 요청한 권한(웹사이트 콘텐츠 접근, 데이터 수정 등)을 악의적 목적으로 활용 가능
- **공급망 위험**: 확장 프로그램 업데이트를 통해 악성 코드가 유포될 수 있는 구조

이러한 취약점은 단순한 광고 차단기를 넘어 **사용자 브라우징 데이터 탈취, 자격 증명 도용, 피싱 페이지 삽입, 심지어 랜섬웨어 유포**까지 가능하게 할 수 있다.

## 2. 실무 영향 분석

DevSecOps 실무자 관점에서 이 사례는 다음과 같은 중대한 영향을 미친다:

- **CI/CD 파이프라인 보안 위험**: 개발자 워크스테이션에 설치된 확장 프로그램이 악성 코드를 실행할 경우, 로컬 환경에서 실행되는 CI/CD 도구, API 키, 소스 코드 저장소 접근 권한 등이 노출될 수 있다.
- **서드파티 의존성 관리의 한계**: Chrome Web Store의 공식 검증 절차를 통과했음에도 악성 코드가 포함될 수 있음을 보여줌 → 기존의 '공식 채널'에 대한 맹목적 신뢰 위험
- **Zero Trust 원칙 위반**: 확장 프로그램이 '설치 후에도 신뢰할 수 없는 행위자'로 간주되어야 한다는 교훈
- **규정 준수 위험**: 금융, 의료 등 규제 산업에서 브라우저 확장 프로그램을 통한 데이터 유출 시 GDPR, HIPAA 등 위반 가능성

## 3. 대응 체크리스트

- [ ] **조직 내 브라우저 확장 프로그램 관리 정책 수립**: 승인된 확장 프로그램 목록(Allowlist)을 구축하고, Chrome Web Store의 Featured 배지에 관계없이 모든 확장 프로그램에 대해 보안 검토 프로세스 적용
- [ ] **개발자 워크스테이션 주기적 감사**: 설치된 확장 프로그램 목록을 정기적으로 수집하고, 권한 분석 및 네트워크 트래픽 모니터링을 통해 비정상 행위 탐지 (예: 예상치 못한 원격 서버 통신)
- [ ] **CI/CD 환경 분리 및 최소 권한 원칙 적용**: 중요한 CI/CD 파이프라인에 사용되는 워크스테이션은 불필요한 브라우저 확장 프로그램 설치를 제한하고, 필요 시 전용 샌드박스 환경에서 실행
- [ ] **확장 프로그램 업데이트 자동화 제한**: 중요한 업무용 브라우저에서는 확장 프로그램 자동 업데이트를 비활성화하고, 보안 팀의 검토 후 수동 업데이트 정책 도입
- [ ] **사용자 보안 인식 교육 강화**: 'Featured' 배지나 높은 설치 수만으로 신뢰하지 말고, 확장 프로그램이 요청하는 권한과 실제 기능 간의 일치 여부를 확인하는 습관 교육

---

### 1.3 Anthropic, 모바일용 데스크톱 스타일 Claude Cowork 테스트 중

{% include news-card.html
  title="Anthropic, 모바일용 데스크톱 스타일 Claude Cowork 테스트 중"
  url="https://www.bleepingcomputer.com/news/artificial-intelligence/anthropic-is-testing-desktop-like-claude-cowork-for-mobile/"
  image="https://www.bleepstatic.com/content/hl-images/2026/02/13/Claude_chats.jpg"
  summary="Anthropic이 모바일에서 Claude Cowork를 테스트 중이며, 사용자가 휴대폰에서 장기 실행되는 Claude 작업을 관리할 수 있게 될 것으로 보입니다."
  source="BleepingComputer"
  severity="Medium"
%}

다음은 DevSecOps 실무자 관점에서 분석한 내용입니다.

---

## 1. 기술적 배경 및 위협 분석

Anthropic이 테스트 중인 **Claude Cowork for Mobile**은 데스크톱 환경의 협업 기능(장기 실행 태스크, 파일 접근, 코드 편집 등)을 모바일로 확장하는 기능입니다. 이는 AI 에이전트가 사용자 기기에서 직접 명령을 실행하고, 파일 시스템에 접근하며, 백그라운드 작업을 지속적으로 수행할 수 있음을 의미합니다.

**주요 위협 요소:**
- **모바일 샌드박스 우회 가능성**: AI 에이전트가 모바일 OS의 권한 모델을 넘어 장기 실행 프로세스로 동작할 경우, 기존 모바일 보안 정책(앱 격리, 백그라운드 제한)이 무력화될 수 있습니다.
- **데이터 유출 경로 확대**: 모바일에서 처리되는 장기 태스크는 클라우드 API 호출, 로컬 파일 읽기/쓰기, 클립보드 접근 등 다양한 데이터 흐름을 생성합니다. AI 에이전트가 중간에 가로채거나 의도치 않게 민감 정보(API 키, 인증 토큰)를 외부로 전송할 위험이 있습니다.
- **지속적 인증 문제**: 모바일 환경에서 장기 실행 태스크는 사용자 세션 만료, 생체 인증 재요청 등의 상황에서 인증 상태를 유지해야 합니다. 이는 세션 하이재킹이나 권한 상승 공격으로 이어질 수 있습니다.

## 2. 실무 영향 분석

DevSecOps 파이프라인에서 모바일 AI 에이전트 도입 시 다음과 같은 실무적 영향이 예상됩니다.

- **CI/CD 보안 게이트 변경**: 기존에는 모바일 빌드/배포 파이프라인에서 AI 에이전트가 개입하지 않았으나, 이제 모바일에서 직접 코드 리뷰, 환경 변수 관리, 배포 명령을 수행할 수 있게 됩니다. 이는 **파이프라인 무결성 검증**을 더욱 복잡하게 만듭니다.
- **모니터링 및 감사 로그 확장**: AI 에이전트가 생성하는 모든 파일 접근, API 호출, 네트워크 요청을 추적 가능한 감사 로그로 남겨야 합니다. 특히 모바일 디바이스의 로컬 로그는 휘발성이 강하므로 **중앙 로그 수집 정책**이 필요합니다.
- **취약점 스캔 대상 증가**: AI 에이전트가 사용하는 모바일 런타임, 의존성 라이브러리, 네트워크 통신 프로토콜이 새로운 공격 표면이 됩니다. 기존 SAST/DAST 스캔 범위를 모바일 AI 에이전트 레이어까지 확장해야 합니다.

## 3. 대응 체크리스트

- [ ] 모바일 AI 에이전트가 접근 가능한 파일 시스템 범위를 최소화하고, 민감 데이터(SSH 키, .env 파일)는 별도 암호화 저장소로 분리
- [ ] AI 에이전트의 모든 API 호출 및 파일 접근에 대해 감사 로깅을 활성화하고, SIEM 시스템과 연동하여 이상 징후 탐지
- [ ] 모바일 디바이스에서 장기 실행 태스크의 세션 만료 정책을 15분 이내로 설정하고, 민감 작업(배포, 권한 변경) 시 반드시 생체 인증 재요구
- [ ] CI/CD 파이프라인에 모바일 AI 에이전트 행위를 검증하는 정적 분석 스테이지 추가 (예: 예상치 못한 파일 접근 패턴 탐지)
- [ ] AI 에이전트가 생성하는 모든 네트워크 트래픽을 기업 VPN/프록시를 통해서만 라우팅하도록 모바일 MDM 정책 적용

---

## 2. AI/ML 뉴스

### 2.1 AI 네이티브 시대의 프라이버시 인식 인프라: 자산 분류 사례 연구

{% include news-card.html
  title="AI 네이티브 시대의 프라이버시 인식 인프라: 자산 분류 사례 연구"
  url="https://engineering.fb.com/2026/06/25/security/privacy-aware-infrastructure-in-the-ai-native-era-an-asset-classification-case-study/"
  summary="프라이버시 통제 시스템이 효과적으로 작동하려면 데이터에 대한 정확한 이해가 필수적이며, 이는 ”age” 필드처럼 맥락에 따라 의미가 달라질 수 있어 복잡성을 야기합니다. AI-Native 시대의 Privacy-Aware Infrastructure 구축을 위해서는 이러한 데이터 분류(Asset Classification)가 선행되어야 함을 사례 연구를 통해 "
  source="Meta Engineering Blog"
  severity="High"
%}

#### 요약

프라이버시 통제 시스템이 효과적으로 작동하려면 데이터에 대한 정확한 이해가 필수적이며, 이는 "age" 필드처럼 맥락에 따라 의미가 달라질 수 있어 복잡성을 야기합니다. AI-Native 시대의 Privacy-Aware Infrastructure 구축을 위해서는 이러한 데이터 분류(Asset Classification)가 선행되어야 함을 사례 연구를 통해 보여줍니다.

---

### 2.2 Google Finance의 최신 업그레이드, 새로운 앱 포함

{% include news-card.html
  title="Google Finance의 최신 업그레이드, 새로운 앱 포함"
  url="https://blog.google/products-and-platforms/products/search/google-finance-updates-june-2026/"
  image="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Google_Finance_blog_image_June_.max-600x600.format-webp.webp"
  summary="Google Finance가 새로운 앱을 포함한 최신 업그레이드를 발표했습니다. 이번 업데이트는 사용자 인터페이스 요소와 함께 Google Finance 로고를 중심으로 개선되었습니다."
  source="Google AI Blog"
  severity="Medium"
%}

#### 요약

Google Finance가 새로운 앱을 포함한 최신 업그레이드를 발표했습니다. 이번 업데이트는 사용자 인터페이스 요소와 함께 Google Finance 로고를 중심으로 개선되었습니다.

---

### 2.3 궁극의 여름 세일 조합: Steam 세일과 GeForce NOW 할인 만남

{% include news-card.html
  title="궁극의 여름 세일 조합: Steam 세일과 GeForce NOW 할인 만남"
  url="https://blogs.nvidia.com/blog/geforce-now-thursday-steam-summer-sale-2026/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/06/gfn-thursday-6-25-no-copy-kv-1536x920-1-842x450.jpg"
  summary="이번 GFN Thursday에서는 Steam Summer Sale과 GeForce NOW 멤버십 할인이 결합된 이중 혜택이 제공됩니다. 또한 Devolver 라인업에 Dark Scrolls가 합류하고, Square Enix의 The Adventures of Elliot: The Millennium Tales도 추가됩니다. 클라우드 게이밍의 가치를 극대화할 "
  source="NVIDIA AI Blog"
  severity="High"
%}

#### 요약

이번 GFN Thursday에서는 Steam Summer Sale과 GeForce NOW 멤버십 할인이 결합된 이중 혜택이 제공됩니다. 또한 Devolver 라인업에 Dark Scrolls가 합류하고, Square Enix의 The Adventures of Elliot: The Millennium Tales도 추가됩니다. 클라우드 게이밍의 가치를 극대화할 수 있는 다양한 할인 기회가 마련되었습니다.

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 STOCKSTAY Another Day: Turla 정보 수집 체계의 최신 추가 사항

{% include news-card.html
  title="STOCKSTAY Another Day: Turla 정보 수집 체계의 최신 추가 사항"
  url="https://cloud.google.com/blog/topics/threat-intelligence/stockstay-turla-intelligence-gathering/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/stockstay-fig1.max-1000x1000.png"
  summary="Google Threat Intelligence Group(GTIG)은 러시아 연계 위협 행위자 Turla가 2022년 12월부터 지속적으로 개발 및 배포해 온 .NET 백도어 STOCKSTAY를 분석했습니다. Turla는 이 STOCKSTAY를 우크라이나의 정부 및 군사 조직과 이탈리아 외교 정책에 관심이 있는 단체를 대상으로 사용했습니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Threat Intelligence Group(GTIG)은 러시아 연계 위협 행위자 Turla가 2022년 12월부터 지속적으로 개발 및 배포해 온 .NET 백도어 STOCKSTAY를 분석했습니다. Turla는 이 STOCKSTAY를 우크라이나의 정부 및 군사 조직과 이탈리아 외교 정책에 관심이 있는 단체를 대상으로 사용했습니다.

---

## 4. DevOps & 개발 뉴스

### 4.1 Copilot 코드 리뷰: 분석 깊이 및 효율성 업데이트

{% include news-card.html
  title="Copilot 코드 리뷰: 분석 깊이 및 효율성 업데이트"
  url="https://github.blog/changelog/2026-06-25-copilot-code-review-analysis-depth-and-efficiency-updates"
  image="https://github.blog/wp-content/uploads/2026/06/612815754-d8355674-4d06-4b8a-8464-8dd875f4a0c7.jpeg"
  summary="GitHub의 Copilot code review가 Copilot CLI와 SDK의 파일 탐색 도구를 활용하도록 업데이트되어, 기존 워크플로우 변경 없이 리뷰 비용 효율성이 크게 개선되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub의 Copilot code review가 Copilot CLI와 SDK의 파일 탐색 도구를 활용하도록 업데이트되어, 기존 워크플로우 변경 없이 리뷰 비용 효율성이 크게 개선되었습니다.

---

### 4.2 Enterprise-managed settings에서 VS Code 및 GitHub Copilot CLI의 strictKnownMarketplaces를 지원합니다

{% include news-card.html
  title="Enterprise-managed settings에서 VS Code 및 GitHub Copilot CLI의 strictKnownMarketplaces를 지원합니다"
  url="https://github.blog/changelog/2026-06-25-enterprise-managed-settings-now-support-strictknownmarketplaces-in-vs-code-and-the-cli"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-improvements.jpg"
  summary="GitHub이 VS Code와 GitHub Copilot CLI에서 기업이 사용자 플러그인 설치를 제어할 수 있는 strictKnownMarketplaces 설정을 퍼블릭 프리뷰로 제공한다. 이 설정은 엔터프라이즈 관리형 환경에 추가할 수 있다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub이 VS Code와 GitHub Copilot CLI에서 기업이 사용자 플러그인 설치를 제어할 수 있는 strictKnownMarketplaces 설정을 퍼블릭 프리뷰로 제공한다. 이 설정은 엔터프라이즈 관리형 환경에 추가할 수 있다.

---

### 4.3 컨테이너 워크플로우를 위한 SBOM 생성 방법

{% include news-card.html
  title="컨테이너 워크플로우를 위한 SBOM 생성 방법"
  url="https://www.docker.com/blog/sbom-generation-for-container-workflows/"
  summary="이 글은 컨테이너 이미지의 SBOM(Software Bill of Materials) 생성 시점과 방법을 다루며, 빌드 타임과 포스트 빌드 접근법, 품질 기준, CI/CD 통합 방안을 설명합니다."
  source="Docker Blog"
  severity="Medium"
%}

#### 요약

이 글은 컨테이너 이미지의 SBOM(Software Bill of Materials) 생성 시점과 방법을 다루며, 빌드 타임과 포스트 빌드 접근법, 품질 기준, CI/CD 통합 방안을 설명합니다.

---

## 5. 블록체인 뉴스

### 5.1 Trezor Academy, 아프리카 비트코인 경제 다큐멘터리 공개 및 교육 기부금 접수

{% include news-card.html
  title="Trezor Academy, 아프리카 비트코인 경제 다큐멘터리 공개 및 교육 기부금 접수"
  url="https://bitcoinmagazine.com/news/trezor-academy-releases-documentary"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/Screenshot-2026-06-25-at-3.27.16-PM.png"
  summary="Trezor Academy가 아프리카 전역의 Bitcoin 도입을 조명한 다큐멘터리를 공개하고, 글로벌 사우스의 Bitcoin 교육 이니셔티브를 지원하기 위한 기부 프로그램을 시작했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Trezor Academy가 아프리카 전역의 Bitcoin 도입을 조명한 다큐멘터리를 공개하고, 글로벌 사우스의 Bitcoin 교육 이니셔티브를 지원하기 위한 기부 프로그램을 시작했습니다.

---

### 5.2 Matt Corallo, Rust Lightning 금지 이후 GitHub 탈퇴 촉구

{% include news-card.html
  title="Matt Corallo, Rust Lightning 금지 이후 GitHub 탈퇴 촉구"
  url="https://bitcoinmagazine.com/business/matt-corallo-urges-bitcoin-projects-to-exit-github-after-rust-lightning-ban"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/tn-6.webp"
  summary="Matt Corallo가 Rust Lightning 금지 이후 Bitcoin 프로젝트들이 GitHub를 떠나야 한다고 촉구했습니다. Andrew Poelstra 등 선임 개발자들은 깨진 병합 스크립트, 숨겨진 diff, 신뢰할 수 없는 추적을 지적하며 자체 호스팅 Forgejo 솔루션으로 전환을 권장했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Matt Corallo가 Rust Lightning 금지 이후 Bitcoin 프로젝트들이 GitHub를 떠나야 한다고 촉구했습니다. Andrew Poelstra 등 선임 개발자들은 깨진 병합 스크립트, 숨겨진 diff, 신뢰할 수 없는 추적을 지적하며 자체 호스팅 Forgejo 솔루션으로 전환을 권장했습니다.

---

### 5.3 Perception, 4가지 디지털 자산 통합으로 베타 종료

{% include news-card.html
  title="Perception, 4가지 디지털 자산 통합으로 베타 종료"
  url="https://bitcoinmagazine.com/news/perception-exits-beta-with-digital-asset"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/Perception-Exits-Beta-With-Four-Digital-Asset-Integrations.jpg"
  summary="Perception이 베타 버전을 종료하고 디지털 자산 내러티브 인텔리전스 플랫폼을 출시했으며, BitGo, Swan, Relai, Bitcoin Well과의 통합을 통해 1,000개 이상의 업계 소스에서 AI 기반 시장 인사이트를 제공합니다."
  source="Bitcoin Magazine"
  severity="High"
%}

#### 요약

Perception이 베타 버전을 종료하고 디지털 자산 내러티브 인텔리전스 플랫폼을 출시했으며, BitGo, Swan, Relai, Bitcoin Well과의 통합을 통해 1,000개 이상의 업계 소스에서 AI 기반 시장 인사이트를 제공합니다.

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Notion, Skiff 영향을 받은 이메일 앱 종료, 대부분의 사용자가 AI 에이전트 사용](https://arstechnica.com/gadgets/2026/06/notion-killing-skiff-influenced-email-app-since-most-users-use-ai-agents-instead/) | Ars Technica | Notion이 AI 에이전트를 통해 이메일을 관리하는 방식에 집중하면서, Skiff의 영향을 받은 기존 이메일 앱을 중단하기로 결정했다. 이는 대부분의 사용자가 AI 에이전트를 선호하기 때문이다 |
| [Pinterest의 Foundation 모델을 위한 거의 선형적인 학습 확장성 달성](https://medium.com/pinterest-engineering/achieving-near-linear-training-scalability-for-pinterests-foundation-models-14d4f59fe6f6?source=rss----4c5a5f6279b6---4) | Pinterest Engineering | Pinterest의 AI 플랫폼 팀은 6억 명 이상의 월간 활성 사용자를 위한 추천을 지원하는 foundation 모델의 훈련 확장성을 거의 선형 수준으로 달성했습니다. |
| [Dash chat에서 AI 평가를 더 나은 응답으로 전환하기 위해 DSPy를 사용한 방법](https://dropbox.tech/machine-learning/how-we-turned-ai-evaluations-into-better-responses-in-dash-chat) | Dropbox Tech Blog | Dash chat에서 DSPy를 활용해 LLM 평가자를 개선하고 평가 기반 피드백 루프를 구축하여 더 나은 응답을 생성하는 최적화된 채팅 경험을 구현했습니다 |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 12건 | 기타 주제 |
| **AI/ML** | 2건 | The Hacker News 관련 동향, Meta Engineering Blog 관련 동향 |
| **컨테이너/K8s** | 1건 | Docker Blog 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(12건)입니다. **AI/ML** 분야에서는 The Hacker News 관련 동향, Meta Engineering Blog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 위한 Node.js 임플란트 유포** 관련 보안 영향도 분석 및 모니터링 강화

### P1 (7일 내)

- [ ] **Photo ZIP 캠페인이 호스피탈리티 업계를 노려 지속적 접근을 위한 Node.js 임플란트 유포** 관련 보안 검토 및 모니터링
- [ ] **폴란드, 수백만 달러 규모 암호화폐 도난 관련 SIM 스와핑 갱단 적발** 관련 보안 검토 및 모니터링
- [ ] **ThreatsDay 게시판: Smart TV Proxyware, 24년 된 curl 버그, AI 범죄 포럼 외 13건** 관련 보안 검토 및 모니터링
- [ ] **AI 네이티브 시대의 프라이버시 인식 인프라: 자산 분류 사례 연구** 관련 보안 검토 및 모니터링
- [ ] **궁극의 여름 세일 조합: Steam 세일과 GeForce NOW 할인 만남** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **AI 네이티브 시대의 프라이버시 인식 인프라: 자산 분류 사례 연구** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
