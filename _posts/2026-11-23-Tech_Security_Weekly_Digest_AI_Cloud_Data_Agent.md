---
layout: post
title: "2026년 11월 23일 주간 보안 다이제스트: 악성코드·BYOVD EDR·Cisco FMC (17건)"
date: 2026-11-23 16:49:51 +0900
last_modified_at: 2026-11-23T16:49:51+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Cloud, Agent, AWS]
excerpt: "2026년 11월 23일 공개된 17건의 위협·취약점 가운데 ‘BYOVD를 통한 국내 보안 제품 무력화 시도: 정상 AI 도구로’ 소식 · ‘CISA, 심각한 Cisco RCE 취약점이 공격에 적극 악용되고’ 소식이 즉각 대응 우선순위에 올랐습니다. 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다."
description: "2026년 11월 23일 보안 뉴스 요약. 안랩 ASEC 블로그, BleepingComputer 등 17건을 분석하고 BYOVD를 통한 국내 보안 제품 무력화 시도, CISA, 심각한 Cisco RCE 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Cloud, Agent]
author: Twodragon
comments: true
image: /assets/images/2026-11-23-Tech_Security_Weekly_Digest_AI_Cloud_Data_Agent.svg
image_alt: "BYOVD, CISA, Cisco RCE, GL.iNet - security digest overview"
toc: true
summary_card:
  title: "2026년 11월 23일 주간 보안 다이제스트: 악성코드·BYOVD EDR·Cisco FMC (17건)"
  period: "2026년 11월 23일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Cloud"
    - "Agent"
    - "AWS"
    - "2026"
  highlights:
    - { source: "안랩 ASEC 블로그", title: "BYOVD를 통한 국내 보안 제품 무력화 시도: 정상 AI 도구로 위장한 악성코드 유포 주의" }
    - { source: "BleepingComputer", title: "CISA, 심각한 Cisco RCE 취약점이 공격에 적극 악용되고 있다고 경고" }
    - { source: "BleepingComputer", title: "해커들이 GL.iNet 클라우드 취약점을 악용해 라우터와 KVM 기기를 감염시켜" }
    - { source: "AWS Korea Blog", title: "Amazon Neptune과 Amazon Bedrock AgentCore로 만든 뉴스룸 이슈 그래프:" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 11월 23일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 17개
- **보안 뉴스**: 5개
- **클라우드 뉴스**: 2개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | 안랩 ASEC 블로그 | BYOVD를 통한 국내 보안 제품 무력화 시도: 정상 AI 도구로 위장한 악성코드 유포 주의 | 🟠 High |
| 🔒 **Security** | BleepingComputer | CISA, 심각한 Cisco RCE 취약점이 공격에 적극 악용되고 있다고 경고 | 🔴 Critical |
| 🔒 **Security** | BleepingComputer | 해커들이 GL.iNet 클라우드 취약점을 악용해 라우터와 KVM 기기를 감염시켜 | 🟠 High |
| ☁️ **Cloud** | AWS Korea Blog | Amazon Neptune과 Amazon Bedrock AgentCore로 만든 뉴스룸 이슈 그래프: 한국일보 N.C.I 구축 사례 | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | 금융 규제 환경에서 AWS Glue로 Google Analytics 4 데이터를 API 직접 호출로 수집하기 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | 트럼프, Nvidia의 Jensen Huang CEO 복귀 촉구 재차 강조 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | 억만장자 Bill Ackman, Fed가 12월에 금리 ‘실수’를 저지를 것이라고 경고 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | 트럼프 만찬 명단 지갑 절반이 비미국 거래소에서 토큰 받아 | 🟡 Medium |
| 💻 **Tech** | 네이버 D2 | 새벽 3시 54분, Agent가 먼저 분석하고 처리했습니다 | 🟡 Medium |
| 💻 **Tech** | 네이버 D2 | 뇌를 닮은 세컨드 브레인: 토큰 낭비 없는 RAG | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: CISA, 심각한 Cisco RCE 취약점이 공격에 적극 악용되고 있다고 경고 등 Critical 등급 위협 1건이 확인되었습니다.
- **주요 모니터링 대상**: BYOVD를 통한 국내 보안 제품 무력화 시도: 정상 AI 도구로 위장한 악성코드 유포 주의, 해커들이 GL.iNet 클라우드 취약점을 악용해 라우터와 KVM 기기를 감염시켜 등 High 등급 위협 2건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 분석가 시점

이번 주기를 한 줄로 정리하면, 정상 도구의 얼굴을 한 공격면이 커널과 엣지 펌웨어까지 내려왔다는 것이다. BYOVD로 국내 엔드포인트 방어를 무력화하려는 시도, CISA가 실제 악용으로 지정한 Cisco RCE, GL.iNet 클라우드를 통한 라우터·KVM 감염은 모두 `신뢰된 구성요소`를 공격 발판으로 삼는다. DevSecOps 실무자가 이번 주기에 가장 먼저 봐야 할 신호는 **서명된 드라이버와 펌웨어의 취약 버전을 자산 인벤토리에서 즉시 식별하는 것**이다. 파이프라인 게이트는 애플리케이션 CVE에서 멈추지 말고, 노드 커널 모듈과 엣지 장비 이미지의 해시·서명 검증까지 eBPF 기반 런타임 관측과 묶어야 한다.

## 1. 보안 뉴스

### 1.1 BYOVD를 통한 국내 보안 제품 무력화 시도: 정상 AI 도구로 위장한 악성코드 유포 주의

{% include news-card.html
  title="BYOVD를 통한 국내 보안 제품 무력화 시도: 정상 AI 도구로 위장한 악성코드 유포 주의"
  url="https://asec.ahnlab.com/ko/96707/"
  image="https://asec.ahnlab.com/wp-content/uploads/2026/11/qtW0tYjimeDsngtNucjviF6pb6gBqURRoWKTL9ZF.webp"
  summary="개요 최근 AhnLab SEcurity intelligence Center(ASEC)는 정상 AI 도구로 위장한 악성코드에서 BYOVD(Bring Your Own Vulnerable Driver)를 통한 국내 보안 솔루션 무력화 시도를 확인했다. 악성코드는 정상 AI 도구 배포 페이지로 위장한 사이트를 통해 유포된다."
  source="안랩 ASEC 블로그"
  severity="High"
%}

#### 기술적 배경 및 위협 분석

BYOVD(Bring Your Own Vulnerable Driver)는 공격자가 서명된 취약 드라이버를 악용해 커널 레벨 권한을 획득하는 기법이다. 이번 사례의 핵심은 **정상 AI 도구 배포 페이지로 위장한 한국어 사이트**를 통해 악성코드를 유포하고, 취약 드라이버로 국내 백신·보안 솔루션의 커널 콜백 및 프로세스 보호 기능을 무력화한다는 점이다. 드라이버가 정식 서명을 갖고 있어 코드 서명 정책을 우회하며, 사용자 모드 EDR 우회보다 탐지가 어렵다. 특히 무력화 대상이 모두 국내 제품으로 한정된 점은 한국 사용자를 표적으로 한 공급망 사칭형 공격으로, AI 도구 수요 증가를 사회공학적으로 악용한 전형적 사례다.

#### 실무 영향 분석

DevSecOps 파이프라인 관점에서 ① 개발자 단말이 AI 도구 설치를 빙자한 드라이버 로드 경로에 노출되고, ② CI/CD 러너나 빌드 서버에 BYOVD가 침투할 경우 시크릿 탈취·아티팩트 변조로 이어질 수 있다. 또한 커널 드라이버 로드 이벤트는 기존 애플리케이션 로그 기반 모니터링에서 사각지대가 되기 쉬워, SBOM·드라이버 인벤토리 관리와 커널 텔레메트리(예: Sysmon Event ID 6, WDAC/AppLocker 정책) 연계가 필수다. 서드파티 소프트웨어 허용목록 정책 부재 시 동일 위협에 반복 노출된다.



---

### 1.2 CISA, 심각한 Cisco RCE 취약점이 공격에 적극 악용되고 있다고 경고

{% include news-card.html
  title="CISA, 심각한 Cisco RCE 취약점이 공격에 적극 악용되고 있다고 경고"
  url="https://www.bleepingcomputer.com/news/security/cisa-flags-critical-cisco-expressway-rce-flaw-as-actively-exploited/"
  image="https://www.bleepstatic.com/content/hl-images/2026/11/23/Cisco.jpg"
  summary="CISA는 최근 패치된 Cisco Expressway의 치명적인 RCE 취약점이 실제 공격에서 적극적으로 악용되고 있다고 연방 기관에 경고했습니다. 해당 취약점은 원격 코드 실행이 가능한 심각한 결함으로, 공격자들이 이를 통해 시스템을 장악할 수 있습니다."
  source="BleepingComputer"
  severity="Critical"
%}

#### CISA, Cisco Expressway 치명적 RCE 취약점 실제 공격 악용 확인

#### 기술적 배경 및 위협 분석

Cisco Expressway는 기업 원격 통신 및 협업 인프라(화상회의, VoIP, MRA 프록시)의 핵심 게이트웨이로, 외부 노출이 빈번한 경계 장비라는 점에서 공격자에게 매력적인 표적이다. 이번 취약점은 인증 없이 원격에서 코드 실행(RCE)이 가능한 치명적 결함으로, 패치 직후 PoC가 공개되며 실제 악용으로 이어졌다. CISA가 KEV(알려진 악용 취약점) 목록에 등재하고 연방기관에 패치를 강제한 것은 단순 취약점 공지가 아닌 **활성 익스플로잇 신호**로 해석해야 한다. 특히 경계 장비의 RCE는 초기 침투 벡터로 활용되어 내부 측면 이동, 자격증명 탈취, 랜섬웨어 전개로 이어지는 킬체인의 시작점이 된다는 점이 위협의 본질이다.

#### 실무 영향 분석

DevSecOps 관점에서 이 사안은 세 가지 리스크를 드러낸다. 첫째, **SBOM/자산 인벤토리 사각지대** — Expressway처럼 네트워크 팀이 관리하는 어플라이언스는 코드 저장소 스캔(SCA) 범위 밖에 있어 CI/CD 파이프라인이 탐지하지 못한다. 둘째, **패치 SLA와 배포 자동화 격차** — 어플라이언스는 컨테이너처럼 재배포가 불가능해 수동 패치에 의존하며, 이는 "패치 후 검증" 자동화가 취약한 영역이다. 셋째, **런타임 탐지 부재** — 경계 장비의 익스플로잇 시도를 SIEM/EDR이 커버하지 못하면 침해 후 탐지까지 공백이 발생한다. 결과적으로 취약점 관리(VM)와 자산 관리(CMDB), 탐지(Detection-as-Code)의 통합이 파이프라인 밖에서 요구된다.



---

### 1.3 해커들이 GL.iNet 클라우드 취약점을 악용해 라우터와 KVM 기기를 감염시켜

{% include news-card.html
  title="해커들이 GL.iNet 클라우드 취약점을 악용해 라우터와 KVM 기기를 감염시켜"
  url="https://www.bleepingcomputer.com/news/security/hackers-exploit-glinet-cloud-flaw-to-infect-routers-kvm-devices/"
  image="https://www.bleepstatic.com/content/hl-images/2026/11/22/routers-kvms.jpg"
  summary="GL.iNet은 자사 클라우드 원격 관리 서비스의 취약점이 해커에 의해 악용되어 고객의 라우터와 KVM 기기에 커스텀 멀웨어가 설치되었다고 확인했습니다. 일부 피해 사용자들은 감염된 기기에 대한 원격 접근을 가능하게 하는 백도어와 리버스 셸이 보고되었습니다."
  source="BleepingComputer"
  severity="High"
%}

#### GL.iNet 클라우드 취약점 악용 사건 분석

#### 기술적 배경 및 위협 분석

GL.iNet은 라우터 및 KVM over IP 디바이스에 클라우드 기반 원격 관리 서비스(GLI.Net/GoodCloud)를 제공하는데, 이 클라우드 관리 평면(control plane)의 취약점이 공격자에 의해 악용되었다. 핵심 위협은 **관리 인터페이스가 단일 실패점(Single Point of Failure)으로 작용**한다는 점이다. 공격자는 클라우드 서비스를 경유해 다수의 디바이스에 커스텀 멀웨어를 푸시했고, 감염된 기기에서 백도어와 리버스 셸이 발견되어 원격 명령 실행이 가능한 상태가 되었다. 이는 공급망 신뢰 경계(클라우드→엣지 디바이스)가 무너진 전형적 사례로, IoT/엣지 계층이 곧 내부 네트워크 진입점으로 전락할 수 있음을 보여준다. 특히 KVM 디바이스는 물리 서버 콘솔 접근 권한을 가지므로, 감염 시 데이터센터 수준의 횡적 이동(lateral movement) 위험이 존재한다.

#### 실무 영향 분석

DevSecOps 관점에서 이 사건은 **관리 평면 의존성 리스크**와 **엣지 자산 가시성 부재**를 동시에 드러낸다. 첫째, 클라우드 관리 기능이 기본 활성화된 채 배포되면 CI/CD 파이프라인 외부에서 구성 드리프트가 발생하고, IaC(Infrastructure as Code)로 관리되지 않는 그림자 자산이 된다. 둘째, 리버스 셸·백도어 탐지는 기존 SAST/DAST로 커버되지 않으며, 런타임 무결성 검증(예: 파일 해시, 프로세스 화이트리스트)이 없으면 침해를 인지하기 어렵다. 셋째, 펌웨어/클라우드 에이전트의 SBOM 및 서명 검증 체계가 없을 경우 공급망 침해를 사후에야 인지하게 된다. 운영팀은 클라우드 관리 기능의 필요성 재검토, 네트워크 분리(관리망/데이터망), 아웃바운드 트래픽 모니터링 강화를 즉시 검토해야 한다.



---

## 2. 클라우드 & 인프라 뉴스

### 2.1 Amazon Neptune과 Amazon Bedrock AgentCore로 만든 뉴스룸 이슈 그래프: 한국일보 N.C.I 구축 사례

{% include news-card.html
  title="Amazon Neptune과 Amazon Bedrock AgentCore로 만든 뉴스룸 이슈 그래프: 한국일보 N.C.I 구축 사례"
  url="https://aws.amazon.com/ko/blogs/tech/hankookilbo-journal-ontology-nci/"
  summary="Overview 한국일보는 AWS를 기반으로 N.C.I(New Context Insights)를 구축했습니다. N.C.I는 편집회의를 준비하는 부장과 국장이 기사를 이슈 단위로 살펴볼 수 있도록 지원하는 서비스입니다."
  source="AWS Korea Blog"
  severity="Medium"
%}


---

### 2.2 금융 규제 환경에서 AWS Glue로 Google Analytics 4 데이터를 API 직접 호출로 수집하기

{% include news-card.html
  title="금융 규제 환경에서 AWS Glue로 Google Analytics 4 데이터를 API 직접 호출로 수집하기"
  url="https://aws.amazon.com/ko/blogs/tech/ingest-ga4-data-in-regulated-environments-using-aws-glue/"
  summary="AWS에서 운영하는 웹 서비스나 모바일 앱은 화면 조회, 버튼 클릭, 구매 같은 사용자 행동 로그를 Amazon Data Firehose 같은 서비스로 Amazon S3에 적재해 분석할 수 있습니다. 행동 로그는 사용자가 서비스를 어떻게 쓰는지 보여주므로 화면 구성을 개선하거나 마케팅 성과를 측정하는 데 쓰입니다."
  source="AWS Korea Blog"
  severity="Medium"
%}


---

## 3. 블록체인 뉴스

### 3.1 트럼프, Nvidia의 Jensen Huang CEO 복귀 촉구 재차 강조

{% include news-card.html
  title="트럼프, Nvidia의 Jensen Huang CEO 복귀 촉구 재차 강조"
  url="https://cointelegraph.com/news/trump-renews-call-for-nvidia-to-rehire-jensen-huang-as-ceo?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/11/01M837EB2PSB0DCZVVC436715D/trump-1.jpg"
  summary="트럼프 전 대통령이 Truth Social 게시물에서 Nvidia가 Jensen Huang을 CEO로 다시 선임해야 한다고 주장하며, 이것이 Nvidia와 미국 모두에 이익이 될 것이라고 밝혔다."
  source="Cointelegraph"
  severity="Medium"
%}


---

### 3.2 억만장자 Bill Ackman, Fed가 12월에 금리 ‘실수’를 저지를 것이라고 경고

{% include news-card.html
  title="억만장자 Bill Ackman, Fed가 12월에 금리 '실수'를 저지를 것이라고 경고"
  url="https://cointelegraph.com/markets/billionaire-bill-ackman-warns-fed-rate-hikes-could-trigger-recession?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/11/01M8341FZ3Y20X594GP00EB6TG/hi-what-the-feds-rate-cut-means-for-crypto-markets-2.jpg"
  summary="억만장자 Bill Ackman은 Fed가 12월 회의에서 25bp 금리 인상을 단행할 것이라는 시장의 광범위한 예상과 달리 금리 '실수'를 저지를 수 있다고 경고했습니다."
  source="Cointelegraph"
  severity="Medium"
%}


---

### 3.3 트럼프 만찬 명단 지갑 절반이 비미국 거래소에서 토큰 받아

{% include news-card.html
  title="트럼프 만찬 명단 지갑 절반이 비미국 거래소에서 토큰 받아"
  url="https://cointelegraph.com/news/half-wallets-trumps-dinner-list-got-tokens-from-non-us-exchanges?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/2026/11/01M82Y4PMA2YN6DTA00JY4GVH4/hi-crypto-charts-101-how-to-read-cryptocurrency-charts-trump.jpg"
  summary="Trump의 밈코인 디너 초청 명단에 오른 130개 지갑 중 66개가 미국 사용자를 제한하는 해외 거래소에서 토큰을 받은 것으로 Public Citizen이 추적했다. 이는 일요일 열리는 디너에 누가 참석하는지에 대한 의문을 제기한다."
  source="Cointelegraph"
  severity="Medium"
%}


---

## 4. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [새벽 3시 54분, Agent가 먼저 분석하고 처리했습니다](https://d2.naver.com/helloworld/1126768) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ 발표 내용 개발과 운영 당번을 함께 맡으며 새벽 알림에 깨는 일, 언제까지 사람이 해야 할까요? |
| [뇌를 닮은 세컨드 브레인: 토큰 낭비 없는 RAG](https://d2.naver.com/helloworld/5087915) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ 발표 내용 기존 RAG의 텍스트 덤프 및 토큰 낭비 한계를 극복하고, 최신 인지 메모리 논문 기법을 결합해 지식 자율 진화와 99% 재현율을 달성하는 차세대 AI 메모리 아키텍처를 소개합니다 |
| [GPU 노드 검증 자동화: 상시 점검부터 부하 검증까지](https://d2.naver.com/helloworld/7131556) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ GPU 노드 검증 자동화: 상시 점검부터 부하 검증까지 (네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다 |


---

## 5. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 9건 | 기타 주제 |
| **AI/ML** | 2건 | BYOVD를 통한 국내 보안 제품 무력화 시도, BleepingComputer 관련 동향 |
| **클라우드 보안** | 2건 | 해커 익스플로잇 GL.iNet cloud 결함 infect, 금융 규제 환경에서 AWS Glue로 Google Analytics 4 |
| **블록체인/암호화폐** | 1건 | Cointelegraph 관련 동향 |
| **취약점/CVE** | 1건 | BleepingComputer 관련 동향 |
| **악성코드/피싱** | 1건 | BYOVD를 통한 국내 보안 제품 무력화 시도 |

이번 주기의 핵심 트렌드는 **AI/ML**(2건)입니다. BYOVD를 통한 국내 보안 제품 무력화 시도, BleepingComputer 관련 동향 등이 주요 이슈입니다. **클라우드 보안** 분야에서는 해커 익스플로잇 GL.iNet cloud 결함 infect, 금융 규제 환경에서 AWS Glue로 Google Analytics 4 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **CISA, 심각한 Cisco RCE 취약점이 공격에 적극 악용되고 있다고 경고** 관련 긴급 패치 및 영향도 확인
- [ ] **Cleverbridge, 데이터 유출로 해커가 신용카드 번호와 CVV 탈취했다고 경고** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **BYOVD를 통한 국내 보안 제품 무력화 시도: 정상 AI 도구로 위장한 악성코드 유포 주의** 관련 보안 검토 및 모니터링
- [ ] **해커들이 GL.iNet 클라우드 취약점을 악용해 라우터와 KVM 기기를 감염시켜** 관련 보안 검토 및 모니터링
- [ ] **Signal, iOS와 Android에서 Siri 및 Gemini AI의 채팅 캡처 차단** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] 클라우드 인프라 보안 설정 정기 감사
- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검

## 관련 포스트 및 참고 자료

- 2026년 11월 22일 주간 보안 다이제스트: {% post_url 2026-11-22-Tech_Security_Weekly_Digest_AI_Kubernetes_Data_AWS %}
- 2026년 11월 21일 주간 보안 다이제스트: {% post_url 2026-11-21-Tech_Security_Weekly_Digest_Patch_AWS_Security_Malware %}
- 2026년 11월 19일 주간 보안 다이제스트: {% post_url 2026-11-19-Tech_Security_Weekly_Digest_AWS_Security_AI %}

| 리소스 | 링크 | 용도 |
|--------|------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 실제 악용 확인된 취약점 목록 — 패치 우선순위 기준 |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) | 공격 전술·기법 매핑 — 탐지 룰 설계 |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) | 취약점 악용 확률 점수 — CVSS 보완 |
| 안랩 ASEC 블로그 | [asec.ahnlab.com](https://asec.ahnlab.com) | 본문 1건 인용 |
| BleepingComputer | [bleepingcomputer.com](https://www.bleepingcomputer.com) | 본문 2건 인용 |
| AWS Korea Blog | [aws.amazon.com](https://aws.amazon.com) | 본문 2건 인용 |
| Cointelegraph | [cointelegraph.com](https://cointelegraph.com) | 본문 3건 인용 |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [2026년 11월 22일 주간 보안 다이제스트: 패치·Kubernetes·클라우드 (16건)](/posts/2026/11/22/Tech_Security_Weekly_Digest_AI_Kubernetes_Data_AWS/) — 2026-11-22
- [2026년 11월 16일 주간 보안 다이제스트: 패치·AI 에이전트·클라우드 (19건)](/posts/2026/11/16/Tech_Security_Weekly_Digest_AI_Cloud_Data_Go/) — 2026-11-16
- [2026년 11월 21일 주간 보안 다이제스트: 제로데이·클라우드·패치 (30건)](/posts/2026/11/21/Tech_Security_Weekly_Digest_Patch_AWS_Security_Malware/) — 2026-11-21

---

**작성자**: Twodragon
