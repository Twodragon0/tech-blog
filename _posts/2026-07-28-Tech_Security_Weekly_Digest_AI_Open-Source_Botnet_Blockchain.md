---
layout: post
title: "2026년 07월 28일 주간 보안 다이제스트: Cisco FMC·클라우드·악성코드 (29건)"
date: 2026-07-28 10:45:58 +0900
last_modified_at: 2026-07-28T10:45:58+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Open-Source, Botnet, Blockchain]
excerpt: "2026년 07월 28일 수집한 29건의 보안 이슈 중 NVIDIA, 37개 회원으로 구성된 Open Secure AI · 모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부를 중심으로 영향 범위와 패치 우선순위를 분석합니다. 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다."
description: "2026년 07월 28일 보안 뉴스 요약. The Hacker News, 안랩 ASEC 블로그, BleepingComputer 등 29건을 분석하고 NVIDIA, 37개 회원으로 구성된 Open, 모든 Fox가 Silver는 아니다 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Open-Source, Botnet]
author: Twodragon
comments: true
image: /assets/images/2026-07-28-Tech_Security_Weekly_Digest_AI_Open-Source_Botnet_Blockchain.svg
image_alt: "NVIDIA, 37 Open, Fox Silver, Dysphoria IoT Botnet - security digest overview"
toc: true
summary_card:
  title: "2026년 07월 28일 주간 보안 다이제스트: Cisco FMC·클라우드·악성코드 (29건)"
  period: "2026년 07월 28일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Open-Source"
    - "Botnet"
    - "Blockchain"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "NVIDIA, 37개 회원으로 구성된 Open Secure AI Alliance 결성 및 NOOA" }
    - { source: "안랩 ASEC 블로그", title: "모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부" }
    - { source: "The Hacker News", title: "Dysphoria IoT Botnet, JackSkid 중단 후 블록체인 C2 및 피해자 릴레이 추가" }
    - { source: "Google Cloud Blog", title: "SAP Business Data Cloud Connect for BigQuery 정식 출시 발표" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 07월 28일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

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
| 🔒 **Security** | The Hacker News | NVIDIA, 37개 회원으로 구성된 Open Secure AI Alliance 결성 및 NOOA 프레임워크 오픈소스화 | 🔴 Critical |
| 🔒 **Security** | 안랩 ASEC 블로그 | 모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부 | 🟠 High |
| 🔒 **Security** | The Hacker News | Dysphoria IoT Botnet, JackSkid 중단 후 블록체인 C2 및 피해자 릴레이 추가 | 🔴 Critical |
| 🤖 **AI/ML** | Palantir Blog | AI 주권이 당신의 알파다: 호스팅 모델 제공자에게 알파를 이전하지 않는 방법 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | 업계 리더들, AI 안전과 보안을 위한 Open Secure AI Alliance에 모이다 | 🟠 High |
| 🤖 **AI/ML** | OpenAI Blog | AI가 업무에서 사람들의 역할을 확장하는 방식 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | SAP Business Data Cloud Connect for BigQuery 정식 출시 발표 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Cyber Snapshot Report: Go beyond the toolchain and build | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 현대화하는 하늘: NOAA와 Google Cloud, 일기 예보 발전을 위해 협력 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | 전용 정책으로 GitHub Copilot 앱 접근 관리하기 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: NVIDIA, 37개 회원으로 구성된 Open Secure AI Alliance 결성 및 NOOA 프레임워크 오픈소스화, Dysphoria IoT Botnet, JackSkid 중단 후 블록체인 C2 및 피해자 릴레이 추가 등 Critical 등급 위협 2건이 확인되었습니다.
- **주요 모니터링 대상**: 모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부, 업계 리더들, AI 안전과 보안을 위한 Open Secure AI Alliance에 모이다, GitHub Copilot 앱 및 Copilot 클라우드 에이전트의 엔터프라이즈 관리 설정 등 High 등급 위협 3건에 대한 탐지 강화가 필요합니다.
- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 NVIDIA, 37개 회원으로 구성된 Open Secure AI Alliance 결성 및 NOOA 프레임워크 오픈소스화

{% include news-card.html
  title="NVIDIA, 37개 회원으로 구성된 Open Secure AI Alliance 결성 및 NOOA 프레임워크 오픈소스화"
  url="https://thehackernews.com/2026/07/nvidia-forms-37-member-open-secure-ai.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEij-O7sLARD9c2QGCheTeoamew1jlKiNe2KRKqw4_8f6VTxZo0MHNIQdizHhyphenhyphen-Bchq9tTzlYBJrJcJDhhhzNB17wPMHDT00pAikN61fAgOh7AdibxKPt5fQ_1KwMvkUXx1J7IzZBbtONSSIAOjRV74KSkmlsKYB7hFWy17AaQu02BqwngqCzlubslSbKvg/s1600/nvidia.jpg"
  summary="NVIDIA가 36개 조직과 함께 Open Secure AI Alliance를 결성하고 NOOA 프레임워크를 오픈소스로 공개했습니다. 이 연합은 Microsoft, Cisco, Cloudflare, CrowdStrike, Hugging Face, IBM, Palo Alto Networks, Red Hat, Linux 재단 등 클라우드, 보안, 엔터프라이즈 "
  source="The Hacker News"
  severity="Critical"
%}

#### DevSecOps 관점 분석: NVIDIA Open Secure AI Alliance 및 NOOA Framework

#### 기술적 배경 및 위협 분석

AI 에이전트와 LLM 기반 애플리케이션이 프로덕션 환경에 빠르게 확산되면서, 기존 보안 프레임워크로는 대응이 어려운 새로운 위협 표면이 등장하고 있습니다. 주요 위협으로는 **프롬프트 인젝션**, **모델 탈취**, **훈련 데이터 중독**, **AI 에이전트 간의 신뢰 체인 붕괴** 등이 있습니다. 특히, AI 에이전트가 자율적으로 코드를 생성하거나 시스템 명령을 실행하는 환경에서는 **공급망 공격(Supply Chain Attack)** 과 **권한 상승** 위험이 더욱 커집니다.

NVIDIA가 주도하는 Open Secure AI Alliance는 이러한 위협에 대응하기 위해 **오픈소스 기반의 표준화된 보안 도구와 방법론**을 제공하려는 시도입니다. NOOA(NVIDIA Open Secure AI) Framework는 AI 파이프라인의 **빌드 → 배포 → 런타임** 전 단계에 걸쳐 보안을 내장(Shift Left)할 수 있도록 설계되었습니다. 이는 기존 DevSecOps 파이프라인에 AI 특화 보안 검증 레이어를 추가하는 것과 같습니다.

#### 실무 영향 분석

DevSecOps 실무자에게 이 소식은 **CI/CD 파이프라인에 AI 보안 게이트를 통합할 수 있는 기반**이 마련되었음을 의미합니다.

- **긍정적 영향**: NOOA Framework를 통해 AI 모델의 취약점 스캔, SBOM(Software Bill of Materials) 생성, 런타임 모니터링을 자동화할 수 있습니다. 특히, Hugging Face, Red Hat 등 주요 파트너사와의 협력으로 **컨테이너 이미지 및 모델 레지스트리**에 대한 보안 정책을 표준화할 가능성이 높습니다.
- **부정적 영향**: 37개 회원사 간의 이해관계 조율이 지연될 수 있으며, 초기 버전의 Framework가 특정 클라우드(AWS, Azure, GCP)에 종속될 위험이 있습니다. 또한, 기존 **SBOM 및 취약점 관리 도구(Snyk, Trivy 등)** 와의 통합이 추가 작업을 요구할 수 있습니다.

**핵심 과제**: DevSecOps 팀은 NOOA의 정책을 기존 **OPA(Open Policy Agent)** 또는 **Kyverno** 같은 정책 엔진과 어떻게 매핑할지, 그리고 AI 에이전트의 행동을 감사(Audit)할 수 있는 **런타임 보안 로그**를 어떻게 수집할지 고민해야 합니다.



---

### 1.2 모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부

{% include news-card.html
  title="모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부"
  url="https://asec.ahnlab.com/ko/94648/"
  image="https://asec.ahnlab.com/wp-content/uploads/2025/08/malware.webp"
  summary="요약 AtlasRAT은 Windows 기반 원격 접근 악성코드다. 보고서는 AGE Flash Player로 위장한 Delphi 실행 파일에서 시작되는 4단계 인메모리 로더 체인과 최종 RAT 기능을 분석했다"
  source="안랩 ASEC 블로그"
  severity="High"
%}

#### DevSecOps 관점 AtlasRAT 로더 체인 분석

#### 기술적 배경 및 위협 분석

해당 공격은 **4단계 인메모리 로더 체인**을 통해 최종 RAT 페이로드를 은닉 및 실행하는 정교한 공급망 위협이다. 주요 기술적 특징은 다음과 같다:

- **진입점**: Flash Player로 위장한 Delphi 실행 파일 → 사용자 신뢰를 악용한 사회공학적 초기 침투
- **로더 체인**: 4단계에 걸친 **파일리스(fileless) 인메모리 실행** → 전통적인 파일 기반 탐지 우회
- **C2 통신**: TLS 기반 ChaCha20 암호화 → 트래픽 분석 및 복호화 난이도 상승
- **모듈형 플러그인**: 실행 후 추가 기능을 동적 로드 → 공격 유연성 및 탐지 회피
- **오프라인 키로깅** 및 **WeChat 프로세스 DLL 인젝션** → 특정 지역(아시아) 타겟팅 및 데이터 유출

이러한 다단계 인메모리 체인은 **엔드포인트 탐지(EDR) 우회**와 **네트워크 트래픽 암호화**로 인해 기존 시그니처 기반 탐지가 무력화된다. 특히 WeChat 타겟팅은 업무 환경에서 흔히 사용되는 메신저를 통한 정보 탈취를 노린 전략이다.

#### 실무 영향 분석

DevSecOps 실무자 관점에서 이 위협은 CI/CD 파이프라인, 배포 환경, 그리고 개발자 워크스테이션에 다음과 같은 직접적 영향을 미친다:

- **개발 환경 감염 위험**: Flash Player 위장 파일이 개발자 이메일/메신저로 유입될 경우, 개발 환경 내 민감한 소스코드, API 키, 인증서 탈취 가능
- **빌드 체인 오염**: 인메모리 기반 실행으로 빌드 서버나 CI/CD 에이전트에서 탐지되지 않고 장기간 잠복 가능
- **암호화된 C2 트래픽**: TLS+ChaCha20 조합으로 기존 네트워크 기반 탐지(SNORT, Zeek 등) 회피 → 아웃바운드 트래픽 분석 필요성 증대
- **모듈형 플러그인**: 최종 페이로드가 추가 악성 모듈을 동적 로드하므로, 초기 탐지 시점 이후에도 새로운 위협 기능이 지속적으로 추가될 수 있음

특히 **개발자 워크스테이션**은 권한이 높고 다양한 네트워크 접근이 가능하므로, 단일 감염만으로도 전체 인프라로 확산될 수 있는 **공급망 위협의 핵심 진입점**이다.



---

### 1.3 Dysphoria IoT Botnet, JackSkid 중단 후 블록체인 C2 및 피해자 릴레이 추가

{% include news-card.html
  title="Dysphoria IoT Botnet, JackSkid 중단 후 블록체인 C2 및 피해자 릴레이 추가"
  url="https://thehackernews.com/2026/07/dysphoria-iot-botnet-adds-blockchain-c2.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhIg3DnKkxpBnQZhAB8v4Wb9FDnDuh3ifKpBMF3kFhNr7_lYOk3S4CgvBoOxFD65FlCjRpoaoBNyH8zo8NtOhjTtTWriXHawlL9mndT3fd_7zlhUBU4mhjU4AvvYNzgV-PGsd52Ng0wnaDRAJMkRQtW4kUuMKlcrP0B71xxywX6cTICeHmMAjswmKhQJKo/s1600/blockchain-botnet.jpg"
  summary="Dysphoria IoT botnet은 CNCERT와 XLab이 추적 중인 사물인터넷 봇넷으로, JackSkid 인프라에 대한 3월 법 집행 작전 이후 블록체인 기반 이름 서비스와 감염 장치 릴레이를 채택했습니다. 연구원들은 이러한 설계가 봇넷을 더욱 교란하기 어렵게 만든다고 밝혔습니다."
  source="The Hacker News"
  severity="Critical"
%}

#### DevSecOps 관점에서 Dysphoria IoT Botnet 분석

#### 기술적 배경 및 위협 분석

Dysphoria IoT Botnet은 CNCERT와 XLab이 추적 중인 IoT 기반 봇넷으로, JackSkid 운영 중단 이후 진화된 형태를 보인다. 주요 기술적 특징은 다음과 같다.

- **Blockchain 기반 C2 (Command & Control) 채택**: 기존 중앙집중식 C2 서버 대신 블록체인 네임 서비스를 사용하여 명령 전달 경로를 분산·난독화함. 이는 DNS 기반 차단이나 IP 블랙리스트 대응을 무력화한다.
- **감염 장치 간 릴레이(Relay) 기능**: 피해 IoT 장비들이 서로 명령을 중계하는 P2P 구조를 형성하여 단일 장비 차단만으로는 봇넷을 해체할 수 없게 설계됨.
- **지속성 강화**: 법적·기술적 대응(JackSkid 운영 차단)을 경험한 공격자가 보안 대응 사이클을 회피하도록 아키텍처를 재설계함.

**위협 수준**: IoT 장비(라우터, IP 카메라, 스마트 허브 등)의 취약점을 악용하며, 대규모 DDoS, 크립토마이닝, 데이터 유출 가능성 존재. 블록체인 기반 C2는 트래픽 분석과 침해 지표(IoC) 추적을 어렵게 만든다.

#### 실무 영향 분석

DevSecOps 실무자에게 다음 측면에서 직접적 영향을 미친다.

- **CI/CD 파이프라인 위험 증가**: IoT 펌웨어 빌드 파이프라인에서 취약점 스캐닝이 강화되어야 함. 공급망 공격(예: 악성 라이브러리 주입)에 취약한 오픈소스 컴포넌트 사용 시 봇넷 감염 경로가 될 수 있음.
- **모니터링 및 탐지 난이도 상승**: 기존 SIEM/SOAR 규칙(특정 IP/도메인 기반)만으로는 블록체인 C2 트래픽을 탐지하기 어려움. 행동 기반 이상 탐지(Behavioral Anomaly Detection)와 네트워크 트래픽 패턴 분석 필요.
- **인프라 복원력 요구사항 증가**: 내부 IoT 장비가 봇넷 릴레이로 전환될 경우, 사내 네트워크 세그멘테이션과 제로 트러스트 정책이 더욱 중요해짐.
- **사고 대응(IR) 플레이북 업데이트 필요**: 기존 C2 차단 절차(IP 차단, 도메인 싱크홀)가 무력화되므로, 블록체인 트랜잭션 분석과 장비 격리 절차를 포함한 새로운 대응 체계가 요구됨.



---

## 2. AI/ML 뉴스

### 2.1 AI 주권이 당신의 알파다: 호스팅 모델 제공자에게 알파를 이전하지 않는 방법

{% include news-card.html
  title="AI 주권이 당신의 알파다: 호스팅 모델 제공자에게 알파를 이전하지 않는 방법"
  url="https://blog.palantir.com/ai-sovereignty-is-your-alpha-how-to-avoid-transferring-your-alpha-to-a-hosted-model-provider-774a1b35bf98?source=rss----3c87dc14372f---4"
  image="https://cdn-images-1.medium.com/max/1024/1*QvGMQmMAaP1sU3OId8uWDg.png"
  summary="타사 AI 모델 서비스 사용은 고유한 기관 지식과 트레이드크래프트인 알파(alpha)가 호스티드 모델 프로바이더(Hosted Model Provider)에게 추출되어 시장에 재판매될 위험이 있습니다. 따라서 알파의 유출을 방지하려면 데이터 처리에 대한 주권적 통제권을 확보하는 것이 중요합니다."
  source="Palantir Blog"
  severity="Medium"
%}

#### 요약

타사 AI 모델 서비스 사용은 고유한 기관 지식과 트레이드크래프트인 알파(alpha)가 호스티드 모델 프로바이더(Hosted Model Provider)에게 추출되어 시장에 재판매될 위험이 있습니다. 따라서 알파의 유출을 방지하려면 데이터 처리에 대한 주권적 통제권을 확보하는 것이 중요합니다.


---

### 2.2 업계 리더들, AI 안전과 보안을 위한 Open Secure AI Alliance에 모이다

{% include news-card.html
  title="업계 리더들, AI 안전과 보안을 위한 Open Secure AI Alliance에 모이다"
  url="https://blogs.nvidia.com/blog/open-secure-ai-alliance/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/07/osaia-logo-garden_press-kit_1920x1080_V4-842x450.png"
  summary="오픈소스 소프트웨어는 글로벌 경제의 핵심 기반이며, 사이버보안은 그 주요 수혜 분야 중 하나입니다. 이러한 배경에서 AI 안전과 보안을 위해 Open Secure AI Alliance가 출범했습니다."
  source="NVIDIA AI Blog"
  severity="High"
%}

#### 요약

오픈소스 소프트웨어는 글로벌 경제의 핵심 기반이며, 사이버보안은 그 주요 수혜 분야 중 하나입니다. 이러한 배경에서 AI 안전과 보안을 위해 Open Secure AI Alliance가 출범했습니다.


---

### 2.3 AI가 업무에서 사람들의 역할을 확장하는 방식

{% include news-card.html
  title="AI가 업무에서 사람들의 역할을 확장하는 방식"
  url="https://openai.com/index/how-ai-is-expanding-what-people-do-at-work"
  summary="OpenAI의 새로운 연구는 AI가 직무 경계를 재편하며 ChatGPT 사용자들이 다양한 역할의 작업을 수행하도록 확장하고 있음을 보여줍니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

OpenAI의 새로운 연구는 AI가 직무 경계를 재편하며 ChatGPT 사용자들이 다양한 역할의 작업을 수행하도록 확장하고 있음을 보여줍니다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 SAP Business Data Cloud Connect for BigQuery 정식 출시 발표

{% include news-card.html
  title="SAP Business Data Cloud Connect for BigQuery 정식 출시 발표"
  url="https://cloud.google.com/blog/products/sap-google-cloud/sap-and-google-cloud-launch-bdc-connect-for-bigquery/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/google_cloud_wrapped.max-1000x1000.jpg"
  summary="SAP와 Google Cloud가 SAP Business Data Cloud Connect for BigQuery의 일반 공급을 발표했습니다. 이 솔루션은 기존 데이터 복제 기술의 한계를 극복하고 최신 워크플로우에 필요한 데이터 신선도를 제공합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

SAP와 Google Cloud가 SAP Business Data Cloud Connect for BigQuery의 일반 공급을 발표했습니다. 이 솔루션은 기존 데이터 복제 기술의 한계를 극복하고 최신 워크플로우에 필요한 데이터 신선도를 제공합니다.


---

### 3.2 Cyber Snapshot Report: Go beyond the toolchain and build

{% include news-card.html
  title="Cyber Snapshot Report: Go beyond the toolchain and build"
  url="https://cloud.google.com/blog/products/identity-security/cyber-snapshot-report-enterprise-resilience-key-to-toolchain-success/"
  summary="Mandiant의 M-Trends 2026 보고서에 따르면, 기계 속도의 공격이 주목받지만 대부분의 성공적인 침입은 여전히 근본적인 인간 및 시스템 결함에서 비롯됩니다. 이는 toolchain을 넘어선 기업 복원력 구축의 필요성을 강조합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Mandiant의 M-Trends 2026 보고서에 따르면, 기계 속도의 공격이 주목받지만 대부분의 성공적인 침입은 여전히 근본적인 인간 및 시스템 결함에서 비롯됩니다. 이는 toolchain을 넘어선 기업 복원력 구축의 필요성을 강조합니다.


---

### 3.3 현대화하는 하늘: NOAA와 Google Cloud, 일기 예보 발전을 위해 협력

{% include news-card.html
  title="현대화하는 하늘: NOAA와 Google Cloud, 일기 예보 발전을 위해 협력"
  url="https://cloud.google.com/blog/topics/public-sector/modernizing-the-skies-noaa-google-cloud-collaborate-advance-weather-forecasting/"
  summary="미국 해양대기청(NOAA)이 Google Cloud를 기상 및 기후 운영 슈퍼컴퓨팅 시스템(WCOSS)의 고성능 컴퓨팅(HPC) 인프라 주요 제공자로 선정했습니다. 이 협력을 통해 NOAA는 지구 대기 패턴을 이해하고 예측하는 방식을 혁신적으로 개선할 계획입니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

미국 해양대기청(NOAA)이 Google Cloud를 기상 및 기후 운영 슈퍼컴퓨팅 시스템(WCOSS)의 고성능 컴퓨팅(HPC) 인프라 주요 제공자로 선정했습니다. 이 협력을 통해 NOAA는 지구 대기 패턴을 이해하고 예측하는 방식을 혁신적으로 개선할 계획입니다.


---

## 4. DevOps & 개발 뉴스

### 4.1 전용 정책으로 GitHub Copilot 앱 접근 관리하기

{% include news-card.html
  title="전용 정책으로 GitHub Copilot 앱 접근 관리하기"
  url="https://github.blog/changelog/2026-07-27-manage-github-copilot-app-access-with-a-dedicated-policy"
  summary="GitHub Copilot 앱이 이제 전용 정책을 가지게 되어 엔터프라이즈 및 조직 수준에서 접근 권한을 제어할 수 있습니다. 기존에는 Copilot 접근 관리가 제한적이었으나, 이번 업데이트로 더 세밀한 통제가 가능해졌습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot 앱이 이제 전용 정책을 가지게 되어 엔터프라이즈 및 조직 수준에서 접근 권한을 제어할 수 있습니다. 기존에는 Copilot 접근 관리가 제한적이었으나, 이번 업데이트로 더 세밀한 통제가 가능해졌습니다.


---

### 4.2 GitHub Copilot 앱 및 Copilot 클라우드 에이전트의 엔터프라이즈 관리 설정

{% include news-card.html
  title="GitHub Copilot 앱 및 Copilot 클라우드 에이전트의 엔터프라이즈 관리 설정"
  url="https://github.blog/changelog/2026-07-27-enterprise-managed-settings-now-apply-to-the-github-copilot-app"
  image="https://github.blog/wp-content/uploads/2026/07/624642571-540f26c1-9d86-4100-8515-7f856f5c3812.jpg"
  summary="GitHub Copilot 앱과 Copilot cloud agent에 대해 엔터프라이즈 관리 설정을 적용할 수 있게 되었으며, 이는 기업 전반에서 Copilot을 제어하는 데 사용하는 중앙 관리 정책과 동일합니다."
  source="GitHub Changelog"
  severity="High"
%}

#### 요약

GitHub Copilot 앱과 Copilot cloud agent에 대해 엔터프라이즈 관리 설정을 적용할 수 있게 되었으며, 이는 기업 전반에서 Copilot을 제어하는 데 사용하는 중앙 관리 정책과 동일합니다.


---

### 4.3 Safari 26.6을 위한 WebKit 기능

{% include news-card.html
  title="Safari 26.6을 위한 WebKit 기능"
  url="https://webkit.org/blog/18178/webkit-features-for-safari-26-6/"
  summary="Safari 26.6이 출시되었으며, WebKit 기능이 업데이트되었습니다."
  source="WebKit Blog"
  severity="Medium"
%}

#### 요약

Safari 26.6이 출시되었으며, WebKit 기능이 업데이트되었습니다.


---

## 5. 블록체인 뉴스

### 5.1 Coinbase 최고 정책 책임자, 암호화폐 명확성 법안을 "매우 초당적"이라고 칭찬

{% include news-card.html
  title="Coinbase 최고 정책 책임자, 암호화폐 명확성 법안을 ”매우 초당적”이라고 칭찬"
  url="https://bitcoinmagazine.com/news/coinbase-policy-officer-praises-clarity"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/04/Coinbase-Receives-Conditional-OCC-Approval-to-Form-National-Trust-Company.jpg"
  summary="Coinbase의 최고 정책 책임자 Faryar Shirzad는 Crypto Clarity Act를 ”매우 초당적”이라고 칭찬하며 민주당과 공화당이 이 법안에 대해 투표할 때라고 밝혔습니다. 이 소식은 Bitcoin Magazine이 Mathew Di Salvo의 기사를 통해 처음 보도했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Coinbase의 최고 정책 책임자 Faryar Shirzad는 Crypto Clarity Act를 "매우 초당적"이라고 칭찬하며 민주당과 공화당이 이 법안에 대해 투표할 때라고 밝혔습니다. 이 소식은 Bitcoin Magazine이 Mathew Di Salvo의 기사를 통해 처음 보도했습니다.


---

### 5.2 공화당, Crypto Clarity Act에 민주당 지지 기대

{% include news-card.html
  title="공화당, Crypto Clarity Act에 민주당 지지 기대"
  url="https://bitcoinmagazine.com/news/republicans-want-democrats-clarity-support"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/U.S.-Senator-Clarity-Act-is-Almost-There-Treasury-Secretary-Puts-It-at-the-1-Yard-Line.jpg"
  summary="공화당 의원들은 암호화폐 시장 구조 법안인 Crypto Clarity Act에 대해 민주당의 지지를 기대하고 있지만, 데이브 매코믹 상원의원에 따르면 민주당이 이를 저지하고 있습니다. 그는 Fox Business와의 인터뷰에서 이번 주에 표결이 이루어져야 한다고 강조했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

공화당 의원들은 암호화폐 시장 구조 법안인 Crypto Clarity Act에 대해 민주당의 지지를 기대하고 있지만, 데이브 매코믹 상원의원에 따르면 민주당이 이를 저지하고 있습니다. 그는 Fox Business와의 인터뷰에서 이번 주에 표결이 이루어져야 한다고 강조했습니다.


---

### 5.3 Bitcoin ETF, 지난주 말 약 5억 달러 유출로 시장 심리 역전

{% include news-card.html
  title="Bitcoin ETF, 지난주 말 약 5억 달러 유출로 시장 심리 역전"
  url="https://bitcoinmagazine.com/markets/bitcoin-etfs-see-investor-reversal"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/Bitcoin-ETFs-See-Outflows.jpg"
  summary="지난주 말 미국 Bitcoin ETF에서 약 4억 7500만 달러가 유출되며 7일 연속 순유입 행진이 마감됐고, 블랙록의 iShares Bitcoin Trust가 대부분의 거래를 처리한 것으로 나타났다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

지난주 말 미국 Bitcoin ETF에서 약 4억 7500만 달러가 유출되며 7일 연속 순유입 행진이 마감됐고, 블랙록의 iShares Bitcoin Trust가 대부분의 거래를 처리한 것으로 나타났다.


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [더 작고 강해진 Kanana SLM 개발](https://tech.kakao.com/posts/826) | 카카오 기술 블로그 | 안녕하세요. 카카오의 AI 모델 개발을 담당하는 카나나 LLM 조직에서 언어모델을 개발하고 있는 Kaya, Ryan, Wavy 입니다 |
| [Microsoft, 경쟁 플랫폼보다 뛰어난 AI 보안 도구 공개](https://arstechnica.com/security/2026/07/microsoft-unveils-ai-security-tools-it-says-outperform-competing-platforms/) | Ars Technica | Microsoft가 경쟁 플랫폼보다 성능이 뛰어나다고 주장하는 새로운 AI 보안 도구를 공개했습니다. 이 도구들은 경쟁사 제품보다 비용이 적게 들면서도 더 나은 성능을 제공한다고 회사 측은 밝혔습니다 |
| [온라인 포인트 쿼리를 위한 데이터 레이크 인덱싱](https://engineering.atspotify.com/2026/7/indexing-the-data-lake-for-online-point-queries/) | Spotify Engineering | Spotify는 온라인 서비스를 위해 대규모 데이터를 저지연으로 접근할 필요가 있으며, 이를 위해 Data Lake를 대상으로 한 Online Point Queries를 위한 인덱싱 방법을 개발했다. 이 접근법은 데이터 레이크 내에서 특정 데이터 포인트를 빠르게 조회할 수 있도록 설계되었다. |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 6건 | The Hacker News 관련 동향, Palantir Blog 관련 동향, NVIDIA AI Blog 관련 동향 |
| **클라우드 보안** | 5건 | AWS Machine Learning Blog 관련 동향, Google Cloud Blog 관련 동향, AWS Blog 관련 동향 |
| **기타** | 5건 | 기타 주제 |
| **제로데이** | 1건 | 해커 표적 US firms FastJson RCE 제로데이 공격 |

이번 주기의 핵심 트렌드는 **AI/ML**(6건)입니다. The Hacker News 관련 동향, Palantir Blog 관련 동향 등이 주요 이슈입니다. **클라우드 보안** 분야에서는 AWS Machine Learning Blog 관련 동향, Google Cloud Blog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **NVIDIA, 37개 회원으로 구성된 Open Secure AI Alliance 결성 및 NOOA 프레임워크 오픈소스화** 관련 긴급 패치 및 영향도 확인
- [ ] **Dysphoria IoT Botnet, JackSkid 중단 후 블록체인 C2 및 피해자 릴레이 추가** 관련 긴급 패치 및 영향도 확인
- [ ] **패치된 vBulletin의 사전 인증 코드 실행 취약점에 대한 공개 익스플로잇 공개** 관련 긴급 패치 및 영향도 확인
- [ ] **해커들이 FastJson RCE 제로데이 공격으로 미국 기업들을 표적으로 삼다** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **모든 Fox가 Silver는 아니다: AtlasRAT 로더 체인 내부** 관련 보안 검토 및 모니터링
- [ ] **업계 리더들, AI 안전과 보안을 위한 Open Secure AI Alliance에 모이다** 관련 보안 검토 및 모니터링
- [ ] **RAG를 넘어서: AWS 기업용 AI를 위한 태스크 인지 지식 압축** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **AI 주권이 당신의 알파다: 호스팅 모델 제공자에게 알파를 이전하지 않는 방법** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
