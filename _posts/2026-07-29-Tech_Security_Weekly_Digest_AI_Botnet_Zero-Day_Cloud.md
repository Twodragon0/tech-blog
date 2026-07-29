---
layout: post
title: "2026년 07월 29일 주간 보안 다이제스트: Telnetd·제로데이·AI 에이전트 (29건)"
date: 2026-07-29 10:48:11 +0900
last_modified_at: 2026-07-29T10:48:11+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Botnet, Zero-Day, Cloud]
excerpt: "2026년 07월 29일 공개된 29건의 위협·취약점 가운데 Claude AI, 포스트퀀텀 테스트 체계를 돌파하고 더 빠른 · Tengu Botnet, 방어자가 프로세스를 종료하면 손상된이 즉각 대응 우선순위에 올랐습니다. 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다."
description: "2026년 07월 29일 보안 뉴스 요약. The Hacker News, AWS Security Blog 등 29건을 분석하고 Claude AI, 포스트퀀텀 테스트, Tengu Botnet 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Botnet, Zero-Day]
author: Twodragon
comments: true
image: /assets/images/2026-07-29-Tech_Security_Weekly_Digest_AI_Botnet_Zero-Day_Cloud.svg
image_alt: "Claude AI, Tengu Botnet, 24, 650 BMC - security digest overview"
toc: true
summary_card:
  title: "2026년 07월 29일 주간 보안 다이제스트: Telnetd·제로데이·AI 에이전트 (29건)"
  period: "2026년 07월 29일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Botnet"
    - "Zero-Day"
    - "Cloud"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "Claude AI, 포스트퀀텀 테스트 체계를 돌파하고 더 빠른 7라운드 AES 공격 발견" }
    - { source: "The Hacker News", title: "Tengu Botnet, 방어자가 프로세스를 종료하면 손상된 Linux 장치를 재부팅한다" }
    - { source: "The Hacker News", title: "인터넷에 노출된 24,650개의 BMC가 로그인 전 IPMI 비밀번호 해시를 노출" }
    - { source: "Google Cloud Blog", title: "전체 데이터 생태계에 대화형 분석 도입" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 07월 29일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

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
| 🔒 **Security** | The Hacker News | Claude AI, 포스트퀀텀 테스트 체계를 돌파하고 더 빠른 7라운드 AES 공격 발견 | 🟠 High |
| 🔒 **Security** | The Hacker News | Tengu Botnet, 방어자가 프로세스를 종료하면 손상된 Linux 장치를 재부팅한다 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | 인터넷에 노출된 24,650개의 BMC가 로그인 전 IPMI 비밀번호 해시를 노출 | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | 에이전틱 AI 시대의 과학 컴퓨팅 | 🟡 Medium |
| 🤖 **AI/ML** | Google AI Blog | Gemini API Managed Agents: 3.6 Flash, hooks 등 추가 기능 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | 강력한 컴퓨팅이 이렇게 작게, NVIDIA Jetson으로 어디서나 AI를 구축하세요 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 전체 데이터 생태계에 대화형 분석 도입 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 미래 데이터 무결성 보장: Cloud KMS의 양자내성 디지털 서명 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Best Buy, Workforce Identity Federation으로 AI 워크로드 확장 및 접근 보안 강화 | 🟠 High |
| ⚙️ **DevOps** | GitHub Changelog | GitHub Copilot 앱 사용량 지표가 이제 보고서 롤업 전반으로 확장됩니다 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: Tengu Botnet, 방어자가 프로세스를 종료하면 손상된 Linux 장치를 재부팅한다 등 Critical 등급 위협 1건이 확인되었습니다.
- **주요 모니터링 대상**: Claude AI, 포스트퀀텀 테스트 체계를 돌파하고 더 빠른 7라운드 AES 공격 발견, Best Buy, Workforce Identity Federation으로 AI 워크로드 확장 및 접근 보안 강화 등 High 등급 위협 2건에 대한 탐지 강화가 필요합니다.
- 공급망 보안 위협이 확인되었으며, 서드파티 의존성 검토와 SBOM 업데이트를 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 Claude AI, 포스트퀀텀 테스트 체계를 돌파하고 더 빠른 7라운드 AES 공격 발견

{% include news-card.html
  title="Claude AI, 포스트퀀텀 테스트 체계를 돌파하고 더 빠른 7라운드 AES 공격 발견"
  url="https://thehackernews.com/2026/07/claude-ai-just-cracked-post-quantum.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgPhJ6dzEL23Ak57nA_XsbXtGaxl5wNrcGBPMQBVz1jddDuX_oTndpQjl3omqMxhRnQ1P4cSF7Ut18tccLFT2BxngpYTqTP8Kg6f4clFWRQ2GvxetR-uAGjMS2SsZwsiPcq5vyxCmP_AN3rCPvO5WMQeLNEit0q14i0iY9wuIUDAHMXkyvO3KjIC6c6Ozg/s1600/Claude.jpg"
  summary="Anthropic의 Claude Mythos Preview가 HAWK-256에 대한 종단간 키 복구 공격을 유도했으며, 7라운드 AES-128에 대한 공격 속도를 200~800배 향상시켰습니다. HAWK 공격은 서명 체계의 격자에서 이전에 사용되지 않은 대칭성을 악용했으며, 96코어 서버에서 약 3시간 42분의 예상 실행 시간을 보입니다."
  source="The Hacker News"
  severity="High"
%}

#### Claude AI의 Post-Quantum 암호 체계 공격 분석 (DevSecOps 관점)

#### 기술적 배경 및 위협 분석

Anthropic의 Claude Mythos Preview가 **HAWK-256** 서명 체계에 대한 end-to-end 키 복구 공격과 **7-라운드 AES-128**에 대한 200~800배 속도 향상을 달성했습니다. 이는 AI가 수학적 취약점(격자 내 대칭성)을 자동으로 발견하고, 공격 구현까지 생성한 사례입니다.

- **HAWK-256 위협**: NIST 표준화 과정의 post-quantum 서명 체계로, 격자 기반 암호의 대칭성을 AI가 식별하여 96코어 서버에서 약 3시간 42분 만에 키 복구가 가능함. 이는 양자 컴퓨터 없이도 AI가 post-quantum 암호를 실용적으로 공격할 수 있음을 시사함.
- **AES-128 위협**: 7-라운드 축소 AES에 대한 공격 속도 향상은 기존의 차분/선형 공격보다 AI가 더 효율적인 경로를 찾았음을 의미. AES-128의 10라운드 전체 공격 가능성은 낮지만, 암호학적 마진이 줄어들고 있음.

**위협 시사점**: AI가 암호 분석을 자동화함에 따라, 기존에 "안전하다"고 여겨졌던 알고리즘에 대한 신뢰가 흔들릴 수 있음. 특히 DevSecOps 파이프라인에서 사용 중인 암호화 라이브러리들이 미래에 더 강력한 공격에 노출될 가능성이 있음.

#### 실무 영향 분석

#### DevSecOps 파이프라인 영향
- **CI/CD 보안**: 현재 사용 중인 AES 기반 암호화(예: Jenkins 비밀 저장, Terraform 상태 암호화)는 10라운드 전체를 사용하므로 즉각적 위협은 낮으나, AI 발전 속도를 고려할 때 **암호화 강도 주기적 재평가** 필요.
- **Post-Quantum 준비**: HAWK-256 공격은 post-quantum 전환 시 특정 알고리즘에 대한 의존도가 높은 위험을 보여줌. NIST 표준(CRYSTALS-Kyber/Dilithium) 외에도 **알고리즘 다양화** 전략 필요.
- **AI 기반 보안 테스트**: Claude 사례는 AI가 보안 취약점을 자동 발견하는 시대가 왔음을 의미. 기존 정적 분석 도구 외에 **AI 보조 취약점 스캐닝**을 파이프라인에 통합 고려.

#### 운영 영향
- **암호화 키 관리**: HAWK-256 공격은 96코어 서버에서 3시간 42분이면 키 복구 가능 → 장기 보관 데이터(로그, 백업)의 암호화 체계 재검토 필요.
- **서드파티 종속성**: 암호학 라이브러리(BoringSSL, OpenSSL, libsodium)의 최신 패치와 AI 취약점 대응 상태를 지속 모니터링해야 함.



---

### 1.2 Tengu Botnet, 방어자가 프로세스를 종료하면 손상된 Linux 장치를 재부팅한다

{% include news-card.html
  title="Tengu Botnet, 방어자가 프로세스를 종료하면 손상된 Linux 장치를 재부팅한다"
  url="https://thehackernews.com/2026/07/tengu-botnet-reboots-compromised-linux.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi0zv7PihU6xAba7-fb5OY-Xv5YIEPM1HhmCu2ET65l5TSKYrPh6q4pYVQRNJtHb9RkvO1oNsBBrsxs50Hm_GRnPKCu4XoG1hhtPOoeGILfRHN99ICGSO72NOGQ6AdUc_haCrQvHRUn4YiyFmCy99WgH1v4-4GRLirZzsV1b5MmCjfTX3a2yWmg1tWOr38/s1600/tengu-botnet.jpg"
  summary="Tengu라는 새로운 Mirai 기반 봇넷이 방어자가 주요 프로세스를 종료할 때 손상된 Linux 장치의 하드웨어 watchdog을 이용해 재부팅을 트리거하며, 이를 통해 다른 지속성 메커니즘이 다시 실행될 기회를 얻습니다. Nozomi Networks Labs는 Telnet 자격 증명 무차별 대입을 통해 드로퍼가 허니팟에 도달하는 것을 관찰했으며, Ten"
  source="The Hacker News"
  severity="Critical"
%}

#### Tengu Botnet 분석: DevSecOps 실무자 관점

#### 기술적 배경 및 위협 분석

Tengu 봇넷은 Mirai 계열 변종으로, Linux 기반 IoT/임베디드 장비를 표적으로 한다. 주요 특징은 **하드웨어 워치독(Hardware Watchdog) 타이머**를 악용해 방어자가 주요 프로세스를 종료할 경우 강제 재부팅을 유도한다는 점이다. 일반적인 프로세스 종료 시도는 효과가 없으며, 재부팅 후 다른 지속성 메커니즘(예: 크론잡, 시스템 서비스, 스크립트)이 활성화되어 봇넷이 재기동된다. 초기 침투는 Telnet 자격 증명 무차별 대입(Brute Force)을 통해 이루어지며, 25종의 DDoS 공격(HTTP 플러드, SYN 플러드, UDP 플러드 등)을 지원한다. 이는 단순한 프로세스 킬(kill) 대응이 무력화됨을 의미하며, DevSecOps 파이프라인에서 런타임 보안과 복원력(resilience) 설계의 중요성을 재확인시킨다.

#### 실무 영향 분석

- **CI/CD 파이프라인**: 컨테이너/VM 이미지 빌드 시 불필요한 Telnet 서비스, 기본 자격 증명, 하드웨어 워치독 비활성화 설정이 누락되면 감염 위험 증가.
- **운영 환경**: 프로세스 종료만으로 대응 불가능 → 재부팅 후 재감염 루프 발생. 기존 모니터링(프로세스 상태 체크)만으로는 탐지 어려움.
- **취약점 관리**: Telnet 대신 SSH 강제, 패스워드 정책 강화, 워치독 설정 검증이 DevSecOps 보안 게이트에 포함되어야 함.
- **포렌식 대응**: 재부팅 시 로그 증발 가능 → syslog 원격 전송, immutable 로그 저장소 필요.



---

### 1.3 인터넷에 노출된 24,650개의 BMC가 로그인 전 IPMI 비밀번호 해시를 노출

{% include news-card.html
  title="인터넷에 노출된 24,650개의 BMC가 로그인 전 IPMI 비밀번호 해시를 노출"
  url="https://thehackernews.com/2026/07/24650-internet-exposed-bmcs-disclose.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjIZDJmL5vHIaEgakZEwVC-O1KGBidMz7xrUS6MQmj0Nfqx4_WzGlwmz4amGxIwYa2PEJTKr5UsFwkh8lEOoFkjAVwTm38bgmbc_gDW2-__9MBpP5Z6cWQrIjFTe3tKTMEhD2lX3XyTrIe0T4mQDruecN3nCWqHUpkU5NpW5OIzZFy5la9RQnMCsmGkt-n8/s1600/bmcs.jpg"
  summary="사이버보안 연구진이 36,000개 이상의 Baseboard Management Controller(BMC) 관리 인터페이스가 Intelligent Platform Management Interface(IPMI) 프로토콜을 공용 인터넷에 노출하고 있다고 경고했습니다. 이 중 24,650개는 로그인 전에 IPMI 비밀번호 해시를 유출하는 것으로 확인되었습니다."
  source="The Hacker News"
  severity="Medium"
%}

#### 요약

사이버보안 연구진이 36,000개 이상의 Baseboard Management Controller(BMC) 관리 인터페이스가 Intelligent Platform Management Interface(IPMI) 프로토콜을 공용 인터넷에 노출하고 있다고 경고했습니다. 이 중 24,650개는 로그인 전에 IPMI 비밀번호 해시를 유출하는 것으로 확인되었습니다.


#### 권장 조치

- 관련 시스템의 인증 정보(Credential) 즉시 로테이션 검토
- MFA(다중 인증) 적용 현황 점검 및 미적용 시스템 식별
- SSO/IdP 로그에서 비정상 인증 시도 모니터링 강화
- 서비스 계정 및 API 키 사용 현황 감사


---

## 2. AI/ML 뉴스

### 2.1 에이전틱 AI 시대의 과학 컴퓨팅

{% include news-card.html
  title="에이전틱 AI 시대의 과학 컴퓨팅"
  url="https://openai.com/index/scientific-computing-agentic-ai"
  summary="과학자들이 AI 코딩 에이전트를 활용해 유전체학 등 과학 컴퓨팅 분야의 소프트웨어 개발과 발견을 가속화하고 있다는 새로운 현장 보고서가 발표되었다. 이는 에이전틱 AI(agentic AI) 시대에 과학 컴퓨팅을 현대화하는 방식을 보여준다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

과학자들이 AI 코딩 에이전트를 활용해 유전체학 등 과학 컴퓨팅 분야의 소프트웨어 개발과 발견을 가속화하고 있다는 새로운 현장 보고서가 발표되었다. 이는 에이전틱 AI(agentic AI) 시대에 과학 컴퓨팅을 현대화하는 방식을 보여준다.


---

### 2.2 Gemini API Managed Agents: 3.6 Flash, hooks 등 추가 기능

{% include news-card.html
  title="Gemini API Managed Agents: 3.6 Flash, hooks 등 추가 기능"
  url="https://blog.google/innovation-and-ai/technology/developers-tools/expanding-managed-agents-gemini-api-3-6-flash-hooks/"
  image="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/unnamed_2_vNnOv20.max-600x600.format-webp.webp"
  summary="Google의 Gemini API에서 Managed Agents 기능이 업데이트되어 Gemini 3.6 Flash 모델을 지원하고, Hooks 및 Triggers 기능이 추가되었습니다. 이를 통해 개발자는 에이전트의 동작을 더욱 세밀하게 제어하고 자동화할 수 있게 되었습니다."
  source="Google AI Blog"
  severity="Medium"
%}

#### 요약

Google의 Gemini API에서 Managed Agents 기능이 업데이트되어 Gemini 3.6 Flash 모델을 지원하고, Hooks 및 Triggers 기능이 추가되었습니다. 이를 통해 개발자는 에이전트의 동작을 더욱 세밀하게 제어하고 자동화할 수 있게 되었습니다.


---

### 2.3 강력한 컴퓨팅이 이렇게 작게, NVIDIA Jetson으로 어디서나 AI를 구축하세요

{% include news-card.html
  title="강력한 컴퓨팅이 이렇게 작게, NVIDIA Jetson으로 어디서나 AI를 구축하세요"
  url="https://blogs.nvidia.com/blog/build-ai-with-nvidia-jetson/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/07/SarahGuo_Jetson_FeaturedImage-842x450.png"
  summary="NVIDIA Jetson 플랫폼이 소형화된 강력한 컴퓨팅 성능으로 어디서나 AI를 구축할 수 있게 해준다고 강조하며, AI 투자자 Sarah Guo가 이 플랫폼을 최신 명품 가방보다 돋보이는 액세서리로 평가했다."
  source="NVIDIA AI Blog"
  severity="Medium"
%}

#### 요약

NVIDIA Jetson 플랫폼이 소형화된 강력한 컴퓨팅 성능으로 어디서나 AI를 구축할 수 있게 해준다고 강조하며, AI 투자자 Sarah Guo가 이 플랫폼을 최신 명품 가방보다 돋보이는 액세서리로 평가했다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 전체 데이터 생태계에 대화형 분석 도입

{% include news-card.html
  title="전체 데이터 생태계에 대화형 분석 도입"
  url="https://cloud.google.com/blog/products/data-analytics/conversational-analytics-in-google-data-cloud-in-q326/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/original_images/1_n7Jglje.gif"
  summary="Google Cloud의 Conversational Analytics(CA)가 기업 전반으로 확장되며, 제너레이티브 AI 도입을 위해 엔터프라이즈 의미 체계에 기반한 신뢰와 거버넌스가 중요해지고 있습니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Cloud의 Conversational Analytics(CA)가 기업 전반으로 확장되며, 제너레이티브 AI 도입을 위해 엔터프라이즈 의미 체계에 기반한 신뢰와 거버넌스가 중요해지고 있습니다.


---

### 3.2 미래 데이터 무결성 보장: Cloud KMS의 양자내성 디지털 서명

{% include news-card.html
  title="미래 데이터 무결성 보장: Cloud KMS의 양자내성 디지털 서명"
  url="https://cloud.google.com/blog/products/identity-security/future-proofing-data-integrity-quantum-safe-digital-signatures-in-cloud-kms/"
  summary="양자 컴퓨터(CRQC)의 등장에 대비해 장기적인 데이터 무결성과 신뢰성을 보호하기 위해 양자 안전 디지털 서명으로의 전환이 중요해지고 있습니다. 미국 정부는 기관들이 이 전환을 완료해야 하는 일정을 업데이트하며 이러한 시급성을 강조했습니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

양자 컴퓨터(CRQC)의 등장에 대비해 장기적인 데이터 무결성과 신뢰성을 보호하기 위해 양자 안전 디지털 서명으로의 전환이 중요해지고 있습니다. 미국 정부는 기관들이 이 전환을 완료해야 하는 일정을 업데이트하며 이러한 시급성을 강조했습니다.


---

### 3.3 Best Buy, Workforce Identity Federation으로 AI 워크로드 확장 및 접근 보안 강화

{% include news-card.html
  title="Best Buy, Workforce Identity Federation으로 AI 워크로드 확장 및 접근 보안 강화"
  url="https://cloud.google.com/blog/topics/retail/best-buy-scales-secure-ai-access-with-workforce-identity-federation/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/Best_Buy_architecture_diagram_no_MSFT_logo.max-1000x1000.jpg"
  summary="Best Buy는 Google Cloud에서 AI 워크로드를 확장하면서 Microsoft Entra ID 사용자 동기화의 관리 마찰과 위험을 해결하기 위해 Google Cloud의 Workforce Identity Federation을 도입했습니다. 이를 통해 대규모 클라우드 확장의 기반을 마련했습니다."
  source="Google Cloud Blog"
  severity="High"
%}

#### 요약

Best Buy는 Google Cloud에서 AI 워크로드를 확장하면서 Microsoft Entra ID 사용자 동기화의 관리 마찰과 위험을 해결하기 위해 Google Cloud의 Workforce Identity Federation을 도입했습니다. 이를 통해 대규모 클라우드 확장의 기반을 마련했습니다.


---

## 4. DevOps & 개발 뉴스

### 4.1 GitHub Copilot 앱 사용량 지표가 이제 보고서 롤업 전반으로 확장됩니다

{% include news-card.html
  title="GitHub Copilot 앱 사용량 지표가 이제 보고서 롤업 전반으로 확장됩니다"
  url="https://github.blog/changelog/2026-07-28-github-copilot-app-usage-metrics-now-expand-across-report-rollups"
  image="https://github.blog/wp-content/uploads/2026/07/628045684-214a7d76-25fe-403d-ba58-cd491fe67b2f.jpeg"
  summary="GitHub Copilot의 앱 사용량 메트릭이 Copilot usage metrics API 전반으로 확장되어 보고되며, 개별 Copilot 앱 활동이 enterprise-user 및 organization-user 보고서에서 사용자별로 귀속됩니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot의 앱 사용량 메트릭이 Copilot usage metrics API 전반으로 확장되어 보고되며, 개별 Copilot 앱 활동이 enterprise-user 및 organization-user 보고서에서 사용자별로 귀속됩니다.


---

### 4.2 Grok 4.5가 GitHub Copilot에서 사용 가능해졌습니다

{% include news-card.html
  title="Grok 4.5가 GitHub Copilot에서 사용 가능해졌습니다"
  url="https://github.blog/changelog/2026-07-28-grok-4-5-is-now-available-in-github-copilot"
  image="https://github.blog/wp-content/uploads/2026/07/621587455-15e748c5-a2d8-4e1c-ac1f-902495ad4259.png"
  summary="xAI의 최신 추론 모델인 Grok 4.5가 GitHub Copilot에서 사용 가능해졌으며, 빠른 에이전틱 코딩과 복잡한 다단계 워크플로우를 위해 설계되었습니다. 이 모델은 최대 컨텍스트 윈도우를 지원하여 개발 생산성을 높이는 데 초점을 맞추고 있습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

xAI의 최신 추론 모델인 Grok 4.5가 GitHub Copilot에서 사용 가능해졌으며, 빠른 에이전틱 코딩과 복잡한 다단계 워크플로우를 위해 설계되었습니다. 이 모델은 최대 컨텍스트 윈도우를 지원하여 개발 생산성을 높이는 데 초점을 맞추고 있습니다.


---

### 4.3 Coding Agent 공포 이야기: 2900만 달러의 비밀 문제

{% include news-card.html
  title="Coding Agent 공포 이야기: 2900만 달러의 비밀 문제"
  url="https://www.docker.com/blog/coding-agent-horror-stories-the-29-million-secret-problem/"
  summary="AI 코딩 에이전트가 공급망 공격에서 자격 증명을 노출할 수 있는 위험성을 다루며, Docker Sandbox를 통해 에이전트가 비밀 정보에 접근하지 못하도록 차단하는 방법을 설명합니다."
  source="Docker Blog"
  severity="Medium"
%}

#### 요약

AI 코딩 에이전트가 공급망 공격에서 자격 증명을 노출할 수 있는 위험성을 다루며, Docker Sandbox를 통해 에이전트가 비밀 정보에 접근하지 못하도록 차단하는 방법을 설명합니다.


---

## 5. 블록체인 뉴스

### 5.1 SEC 의장, 암호화폐 명확성 법안(Crypto Clarity Act) 지원에 '헌신' 표명

{% include news-card.html
  title="SEC 의장, 암호화폐 명확성 법안(Crypto Clarity Act) 지원에 '헌신' 표명"
  url="https://bitcoinmagazine.com/news/sec-chair-paul-atkins-supports-clarity-act"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/SEC-CHair-Paul-Atkins-Supports-Clairty.jpg"
  summary="SEC Chairman Paul Atkins가 Crypto Clarity Act를 지원하겠다고 밝혔으며, 이는 Bitcoin Magazine이 보도한 내용입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

SEC Chairman Paul Atkins가 Crypto Clarity Act를 지원하겠다고 밝혔으며, 이는 Bitcoin Magazine이 보도한 내용입니다.


---

### 5.2 두바이 기반 에미레이트 항공, Bitcoin 및 암호화폐 결제 도입

{% include news-card.html
  title="두바이 기반 에미레이트 항공, Bitcoin 및 암호화폐 결제 도입"
  url="https://bitcoinmagazine.com/news/dubai-based-emirates-adds-bitcoin-payments"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/Dubai-Based-Emirates-Airline-Adds-Bitcoin-and-Crypto-Payments.jpg"
  summary="두바이에 본사를 둔 항공사 Emirates Airline이 Bitcoin 및 암호화폐 결제를 도입했습니다. 이 항공사는 2022년에 처음 Bitcoin 결제 가능성을 시사한 바 있습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

두바이에 본사를 둔 항공사 Emirates Airline이 Bitcoin 및 암호화폐 결제를 도입했습니다. 이 항공사는 2022년에 처음 Bitcoin 결제 가능성을 시사한 바 있습니다.


---

### 5.3 Bitcoin 하락, Crypto Clarity Act 기대감 약화

{% include news-card.html
  title="Bitcoin 하락, Crypto Clarity Act 기대감 약화"
  url="https://bitcoinmagazine.com/bitcoin-mining/bitcoin-price-dips-clarity-act"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/Bitcoin-Price-Down-Clarity-Act.jpg"
  summary="Bitcoin이 Crypto Clarity Act에 대한 기대감이 줄어들면서 하락세를 보였다. 일부 의원들은 다음 주까지 이 법안에 대한 표결이 이루어지길 희망하고 있다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Bitcoin이 Crypto Clarity Act에 대한 기대감이 줄어들면서 하락세를 보였다. 일부 의원들은 다음 주까지 이 법안에 대한 표결이 이루어지길 희망하고 있다.


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Eval-driven development: 대규모 GenAI 평가에서 얻은 교훈](https://medium.com/airbnb-engineering/eval-driven-development-lessons-from-evaluating-genai-at-scale-e817e5ae5788?source=rss----53c7c27702d5---4) | Airbnb Engineering | Airbnb는 Generative AI 제품의 신뢰성을 확보하기 위해 평가를 사후 작업이 아닌 핵심 엔지니어링 분야로 다루는 Eval-driven development 방식을 채택했습니다. Generative AI는 기존 소프트웨어 테스트의 가정을 깨뜨리며, Airbnb 팀은 이를 대규모로 평가한 경험을 공유합니다 |
| [업그레이드된 Go-To-Market 플레이북](https://news.hada.io/topic?id=31934) | GeekNews (긱뉴스) | 혼잡하고 비싸진 SEO·PR 중심 성장 채널 대신, 빠르게 성장하는 기업들은 제품 전략과 시장 진출(GTM) 전략을 결합하고 있음 GTM은 온라인 정보로 사용자를 끌어오던 Pull에서 제품 내 바이럴·네트워크 효과를 활용한 Push, 외부 커뮤니티에서 사용자를 확보하는 Off-Platfo |
| [오픈 소스 c++라이브러리 목록](https://news.hada.io/topic?id=31933) | GeekNews (긱뉴스) | 1. 문서 목적 이 글은 C++ 개발자가 필요한 기능을 빠르게 찾을 수 있도록 오픈 소스 라이브러리를 분야별로 모은 목록이다 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 6건 | The Hacker News 관련 동향, OpenAI Blog 관련 동향, NVIDIA AI Blog 관련 동향 |
| **기타** | 6건 | 기타 주제 |
| **클라우드 보안** | 3건 | AWS Security Blog 관련 동향, Google Cloud Blog 관련 동향 |
| **제로데이** | 1건 | The Hacker News 관련 동향 |
| **인증 보안** | 1건 | Google Cloud Blog 관련 동향 |

이번 주기의 핵심 트렌드는 **AI/ML**(6건)입니다. The Hacker News 관련 동향, OpenAI Blog 관련 동향 등이 주요 이슈입니다. **기타**(6건)도 주목할 트렌드입니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Tengu Botnet, 방어자가 프로세스를 종료하면 손상된 Linux 장치를 재부팅한다** 관련 긴급 패치 및 영향도 확인
- [ ] **JFrog, Hugging Face 침해 전 OpenAI 모델이 Artifactory 제로데이에 악용된 사실 확인** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **Claude AI, 포스트퀀텀 테스트 체계를 돌파하고 더 빠른 7라운드 AES 공격 발견** 관련 보안 검토 및 모니터링
- [ ] **Best Buy, Workforce Identity Federation으로 AI 워크로드 확장 및 접근 보안 강화** 관련 보안 검토 및 모니터링
- [ ] **Google Cloud의 강화된 비용 통제로 AI 지출을 조기에 감지하고 확고히 관리하세요** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **에이전틱 AI 시대의 과학 컴퓨팅** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
