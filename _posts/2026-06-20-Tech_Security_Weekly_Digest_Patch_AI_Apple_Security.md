---
layout: post
title: "2026년 06월 20일 주간 보안 다이제스트: 패치·랜섬웨어·BYOVD EDR (19건)"
date: 2026-06-20 09:41:00 +0900
last_modified_at: 2026-06-20T09:41:00+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Patch, AI, Apple, Security]
excerpt: "2026년 06월 20일 공개된 19건의 위협·취약점 가운데 패치 불가능한 'usbliter8' 익스플로잇 · Gentlemen RaaS, GentleKiller EDR가 즉각 대응 우선순위에 올랐습니다. 변경 통제와 모니터링 적용 시점, 사후 회고에 활용할 IoC 정리표를 포함합니다."
description: "2026년 06월 20일 보안 뉴스 요약. The Hacker News 등 19건을 분석하고 패치 불가능한 'usbliter8' 익스플로잇, Gentlemen RaaS, AutoJack 공격으로 한 웹 페이지가 AI 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Patch, AI, Apple]
author: Twodragon
comments: true
image: /assets/images/2026-06-20-Tech_Security_Weekly_Digest_Patch_AI_Apple_Security.svg
image_alt: "'usbliter8', Gentlemen RaaS, AutoJack AI - security digest overview"
toc: true
summary_card:
  title: "2026년 06월 20일 주간 보안 다이제스트: 패치·랜섬웨어·BYOVD EDR (19건)"
  period: "2026년 06월 20일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Patch"
    - "AI"
    - "Apple"
    - "Security"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "패치 불가능한 &#x27;usbliter8&#x27; 익스플로잇, Apple A12 및 A13 SecureROM 부트 체인" }
    - { source: "The Hacker News", title: "Gentlemen RaaS, GentleKiller EDR 프레임워크로 400개 보안 프로세스 표적" }
    - { source: "The Hacker News", title: "AutoJack 공격으로 한 웹 페이지가 AI 에이전트를 하이재킹해 호스트 코드 실행 가능" }
    - { source: "Google Cloud Blog", title: "Google Cloud의 새로운 기능" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 06월 20일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 19개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 2개
- **클라우드 뉴스**: 1개
- **DevOps 뉴스**: 1개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | 패치 불가능한 'usbliter8' 익스플로잇, Apple A12 및 A13 SecureROM 부트 체인 해제 | 🟠 High |
| 🔒 **Security** | The Hacker News | Gentlemen RaaS, GentleKiller EDR 프레임워크로 400개 보안 프로세스 표적 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | AutoJack 공격으로 한 웹 페이지가 AI 에이전트를 하이재킹해 호스트 코드 실행 가능 | 🔴 Critical |
| 🤖 **AI/ML** | AWS Machine Learning | Amazon Bedrock AgentCore에 웹 검색 기능 도입 | 🟡 Medium |
| 🤖 **AI/ML** | AWS Machine Learning | Adobe Marketing Agent for Amazon Quick의 인사이트로 캠페인 워크플로우 가속화 | 🟠 High |
| ☁️ **Cloud** | Google Cloud Blog | Google Cloud의 새로운 기능 | 🟠 High |
| ⚙️ **DevOps** | GitHub Changelog | Copilot 사용량 메트릭 API에 사용자별 AI 크레딧 소비량 추가 | 🟡 Medium |
| ⛓️ **Blockchain** | Bitcoin Magazine | JPMorgan: 비트코인 채굴 비용이 '악화'됐으며 BTC가 생산 비용 아래에서 거래 중 | 🟡 Medium |
| ⛓️ **Blockchain** | Bitcoin Magazine | 예측 시장 Kalshi, 수익 20억 달러 돌파하며 IPO 추진 | 🟠 High |
| ⛓️ **Blockchain** | Bitcoin Magazine | Kevin Warsh는 여전히 달러를 관리해야 하지만, Bitcoin은 자동으로 작동한다 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: AutoJack 공격으로 한 웹 페이지가 AI 에이전트를 하이재킹해 호스트 코드 실행 가능 등 Critical 등급 위협 1건이 확인되었습니다.
- **주요 모니터링 대상**: 패치 불가능한 'usbliter8' 익스플로잇, Apple A12 및 A13 SecureROM 부트 체인 해제, Adobe Marketing Agent for Amazon Quick의 인사이트로 캠페인 워크플로우 가속화, Google Cloud의 새로운 기능 등 High 등급 위협 4건에 대한 탐지 강화가 필요합니다.
- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 패치 불가능한 'usbliter8' 익스플로잇, Apple A12 및 A13 SecureROM 부트 체인 해제

{% include news-card.html
  title="패치 불가능한 'usbliter8' 익스플로잇, Apple A12 및 A13 SecureROM 부트 체인 해제"
  url="https://thehackernews.com/2026/06/unpatchable-usbliter8-exploit-breaks.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgIM725Ni41-PBwM_6zXNdsydP1eZO7oSsWIlAqpwdOu9dOcZM6ZI1iaqwSsL3yZKT4lbFRM-eZVq3ARKDbLRnid1pJ0Us3XX135nD0tV71gb1lnADzig_vE9c6CAiJdlJ-Wco11InBKUyGX9V5nRFn9qZxuxeJKCzsCV4tQTfFIgU3F05Wnp2VfsxyTPs/s1600/apple-chip.jpg"
  summary="보안 연구팀 Paradigm Shift가 Apple A12 및 A13 칩의 SecureROM 내에서 임의 코드 실행을 가능하게 하는 'usbliter8' 익스플로잇을 공개했습니다. 이 취약점은 제조 시 실리콘에 각인되어 소프트웨어 업데이트로는 패치가 불가능하며, 해당 기기는 사용 기간 내내 이 결함을 안고 가게 됩니다. 원격 공격은 아니며 물리적 접근이 필"
  source="The Hacker News"
  severity="High"
%}

# DevSecOps 관점에서 본 usbliter8 SecureROM Exploit 분석

## 1. 기술적 배경 및 위협 분석

usbliter8은 Apple A12/A13 칩셋의 SecureROM(부트롬)에서 임의 코드 실행을 가능케 하는 하드웨어 수준 익스플로잇입니다. SecureROM은 실리콘에 물리적으로 각인(burned-in)되어 있어 **소프트웨어 패치가 불가능**하며, 해당 칩을 사용하는 모든 기기(iPhone XS~11 시리즈, 일부 iPad)가 영구적 취약점을 보유하게 됩니다.

**핵심 위협 요소:**
- **비가역성**: 펌웨어 업데이트, OTA 패치, OS 업데이트로도 해결 불가
- **부트 체인 완전 붕괴**: SecureROM 무결성이 깨지면 이후 모든 보안 계층(LLB, iBoot, 커널)이 무력화됨
- **물리적 접근 필요**: USB 연결을 통한 공격으로, 원격 공격은 불가능하나 기기 분실/도난 시 심각한 데이터 노출 위험
- **영구적 지속성**: 기기 수명이 다할 때까지 취약점이 존재하며, 재부팅 후에도 제거 불가

## 2. 실무 영향 분석

DevSecOps 관점에서 이 취약점은 **공급망 보안(SBOM)**과 **디바이스 수명주기 관리**에 직접적인 영향을 미칩니다.

**CI/CD 파이프라인 영향:**
- 애플리케이션 수준의 보안 테스트(SAST/DAST)로는 탐지 불가능
- 하드웨어 보안 계층에 대한 신뢰 모델 재정립 필요
- 모바일 앱 배포 시 SecureROM 신뢰성을 가정한 보안 로직(예: Secure Enclave 기반 키 관리)이 무력화될 수 있음

**운영 환경 영향:**
- BYOD 정책 재검토 필요 (A12/A13 기기 사용자 대상)
- 취약 기기에서의 민감 데이터 처리 금지 가이드라인 수립
- 기기 교체 주기 단축에 따른 비용 증가 가능성

## 3. 대응 체크리스트

- [ ] **자산 인벤토리 업데이트**: 조직 내 A12/A13 칩셋 사용 기기 목록을 즉시 파악하고, 해당 기기의 보안 등급을 'High Risk'로 재분류
- [ ] **물리적 보안 강화**: 취약 기기에 대해 USB 접근 제한 정책 시행(USB 포트 물리적 봉인, USB 디버깅 비활성화 강제)
- [ ] **데이터 보호 계층 추가**: Secure Enclave에만 의존하지 않고, 애플리케이션 수준의 엔드투엔드 암호화 및 추가 인증 요소 도입 (예: FIDO2 하드웨어 키)
- [ ] **모니터링 및 탐지 규칙 생성**: USB 연결 기반의 비정상 부트 시퀀스 감지 로그를 수집하고, SIEM에 알림 규칙 추가
- [ ] **공급망 위험 평가 갱신**: Apple 디바이스에 대한 SBOM 평가 시 SecureROM 취약점을 명시적으로 포함하고, 차세대 칩셋(A14 이상)으로의 마이그레이션 로드맵 수립


---

### 1.2 Gentlemen RaaS, GentleKiller EDR 프레임워크로 400개 보안 프로세스 표적

{% include news-card.html
  title="Gentlemen RaaS, GentleKiller EDR 프레임워크로 400개 보안 프로세스 표적"
  url="https://thehackernews.com/2026/06/the-gentlemen-raas-uses-gentlekiller.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgjNWtaK_WkFnKnaLTIwg043i_I6YVi5XuZGVzh30SGeK-iutwr6t2Ed3S6Qk0V9uykYueDD5WETtQ4sW1QwG4jldPXW_IM2woF1Dk1PXcNxbwv6sgoprJ6m8pmogRc0vblucj3nf6Tox_ptxOX9bib6iO4bV4SXVVFoVzUGw0C8cSiJEvq3nDgUZ36G9xp/s1600/edr-killer.jpg"
  summary="Gentlemen RaaS는 GentleKiller라는 EDR 프레임워크를 기반으로 400개 이상의 보안 프로세스를 무력화하는 도구 제품군을 운영 중이며, 이를 제휴사에 제공해 암호화기 배포 전 시스템 방어를 저하시킵니다."
  source="The Hacker News"
  severity="Medium"
%}

# DevSecOps 관점에서 "The Gentlemen RaaS & GentleKiller EDR Framework" 분석

## 1. 기술적 배경 및 위협 분석

Gentlemen RaaS는 **GentleKiller**라는 전용 EDR 우회 프레임워크를 운영하며, 400개 이상의 보안 프로세스를 타겟팅합니다. 이는 단순한 악성코드가 아니라 **모듈형 EDR 킬러**로, 다음과 같은 위협을 내포합니다:

- **다계층 우회 전략**: EDR의 실시간 모니터링(ETW, AMSI, 커널 콜백), 프로세스 보호, 메모리 스캐닝을 무력화하는 API 후킹 및 드라이버 로드 차단 기법 사용
- **서드파티 툴 통합**: 공개된 EDR 우회 도구(예: Terminator, AuKill)와 자체 개발한 커널 드라이버를 결합해 다중 방어 계층을 순차적으로 제거
- **RaaS 비즈니스 모델**: 제휴사에게 GentleKiller를 제공해 랜섬웨어 배포 전 방어 체계를 무력화하는 표준 운영 절차를 구축

이는 기존의 단일 취약점 공격과 달리, **보안 제품 자체를 무력화하는 체계적인 공격 프레임워크**로 전환되었음을 의미합니다.

## 2. 실무 영향 분석

DevSecOps 실무자에게 이 위협은 **CI/CD 파이프라인과 프로덕션 환경 모두에 영향을 미칩니다**:

- **파이프라인 보안 약화**: EDR이 비활성화되면 빌드 서버, 컨테이너 레지스트리, 배포 자동화 도구에서 랜섬웨어가 탐지되지 않고 실행될 수 있음
- **Immutable 인프라 한계**: EDR 킬러가 OS 레벨에서 동작하므로, 컨테이너 기반 환경이라도 호스트 OS가 손상되면 전체 워크로드가 위험에 노출됨
- **공급망 리스크 증가**: 제휴사 기반 RaaS 특성상 다양한 변종이 빠르게 확산되어, 시그니처 기반 탐지만으로는 대응이 어려움

**핵심 문제**: EDR 단일 의존도가 높은 보안 아키텍처는 GentleKiller에 의해 완전히 우회될 수 있습니다.

## 3. 대응 체크리스트

- [ ] **EDR 이중화 및 행위 기반 탐지 도입**: 단일 EDR 대신, 커널 레벨과 사용자 레벨 탐지를 조합하고 비정상 프로세스 종료(예: `taskkill /f /im` 패턴)를 모니터링하는 SIEM 규칙 추가
- [ ] **CI/CD 파이프라인에 런타임 보안 게이트 적용**: 컨테이너 이미지 스캔(취약점 + 악성코드)과 더불어, 배포 전 EDR 상태 확인 스크립트를 파이프라인에 포함
- [ ] **호스트 기반 방어 강화**: Windows Defender Application Control(WDAC) 또는 Linux eBPF 기반 보안 모듈을 통해 알 수 없는 드라이버 로드 차단, LSA 보호 및 PPL(Protected Process Light) 설정 검증
- [ ] **사고 대응 자동화 플레이북 구축**: EDR 알림이 갑자기 중단되거나 보안 프로세스가 종료되는 이벤트 발생 시, 자동으로 해당 호스트를 네트워크 격리하고 포렌식 스냅샷을 수집하는 워크플로우 구현
- [ ] **최소 권한 원칙 재검토**: EDR 에이전트가 SYSTEM 권한으로 실행되지 않도록 서비스 계정 권한을 제한하고, 컨테이너 워크로드는 readOnlyRootFilesystem 및 seccomp 프로필 적용


---

### 1.3 AutoJack 공격으로 한 웹 페이지가 AI 에이전트를 하이재킹해 호스트 코드 실행 가능

{% include news-card.html
  title="AutoJack 공격으로 한 웹 페이지가 AI 에이전트를 하이재킹해 호스트 코드 실행 가능"
  url="https://thehackernews.com/2026/06/autojack-attack-lets-one-web-page.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg3wJOg5Y5vAn_dM0DcIB6SwV2B34iO0H-moeyuWLJ_DF1KgEEZMBGtKPDXYk0pL4wclWbnSmOB74sqReSZoGI2_SwUSzKSscUxEdvuJFx_sCIfU7UplU2k5s4UA0cOVAZT_s80PDTek6OGfrsnE8f6QxrQU58rBqPiuk_J__Yja3YNzZLzd-6s8Ji1PBhc/s1600/agent.jpg"
  summary="Microsoft 연구진이 AutoJack이라는 익스플로잇 체인을 공개했으며, 이는 AI 브라우징 에이전트를 피해자 시스템에서 원격 코드 실행을 수행하는 도구로 전환시킵니다. 공격자의 웹 페이지를 로드하도록 에이전트를 유도하면 해당 페이지의 JavaScript가 동일 머신의 권한 있는 로컬 서비스에 접근해 호스트에서 프로세스를 생성할 수 있으며, 추가 사용"
  source="The Hacker News"
  severity="Critical"
%}

# AutoJack 공격: DevSecOps 실무자 분석

## 1. 기술적 배경 및 위협 분석

AutoJack 공격은 **AI 브라우징 에이전트**가 웹 페이지를 로드할 때, 해당 페이지의 JavaScript가 **로컬 시스템의 권한 있는 서비스**에 접근하여 호스트 코드 실행(RCE)을 유도하는 공격 체인입니다. 핵심은 AI 에이전트가 사용자 대신 웹을 탐색하면서 **브라우저와 OS 간의 신뢰 경계**를 우회한다는 점입니다.

- **공격 벡터**: 악성 웹 페이지에 접속하도록 AI 에이전트를 유도 (예: 검색 결과, 이메일 링크, 광고)
- **취약점 유형**: 교차 출처 통신 우회 + 로컬 서비스 권한 상승
- **특징**: 자격 증명 불필요, 사용자 상호작용 없이 RCE 달성 가능, AI 에이전트를 '무기화'

이 공격은 **AI 에이전트의 자동화 특성**을 역이용합니다. 사용자가 직접 브라우징할 때는 Same-Origin Policy(SOP)가 보호하지만, AI 에이전트가 로컬 서비스와 통신할 때는 이러한 제약이 약화될 수 있습니다.

## 2. 실무 영향 분석

- **CI/CD 파이프라인 위험**: AI 기반 코드 리뷰, 테스트 자동화 도구가 에이전트로 동작할 경우, 악성 페이지를 통해 빌드 서버나 개발 환경이 감염될 수 있습니다.
- **DevSecOps 도구 체인**: AI 에이전트가 포함된 브라우저 기반 테스트 도구(예: Playwright, Puppeteer)를 사용하는 환경에서 특히 취약
- **공급망 공격**: AI 에이전트가 신뢰하는 웹 페이지(예: npm, PyPI) 내 악성 콘텐츠를 통해 간접 공격 가능
- **권한 분리 실패**: 로컬 서비스가 브라우저 컨텍스트에서 접근 가능하도록 설계된 경우, AI 에이전트의 행동을 신뢰하는 것이 위험

## 3. 대응 체크리스트

- [ ] AI 에이전트가 실행되는 브라우저 환경에서 **로컬 서비스 접근 제한** (예: `--disable-web-security` 플래그 금지, 격리된 프로필 사용)
- [ ] AI 에이전트가 접근하는 URL에 대해 **화이트리스트 기반 필터링** 적용 및 외부 페이지 로드 시 샌드박스 실행
- [ ] 로컬 서비스(예: 로컬 HTTP 서버, IPC)가 **브라우저 출처 검증**을 수행하도록 강화 (Origin 헤더, CORS 정책 엄격 적용)
- [ ] CI/CD 환경에서 AI 에이전트 사용 시 **네트워크 격리** (컨테이너 내 실행, 호스트 네트워크 차단) 및 최소 권한 계정 사용
- [ ] AI 에이전트의 JavaScript 실행을 **제한된 컨텍스트**에서만 허용하고, `dangerouslyEvaluate` 등의 API 사용을 금지하는 정책 수립


---

## 2. AI/ML 뉴스

### 2.1 Amazon Bedrock AgentCore에 웹 검색 기능 도입

{% include news-card.html
  title="Amazon Bedrock AgentCore에 웹 검색 기능 도입"
  url="https://aws.amazon.com/blogs/machine-learning/introducing-web-search-on-amazon-bedrock-agentcore/"
  summary="Amazon Bedrock AgentCore의 Web Search 기능이 정식 출시되었습니다. 이 기능은 기존 검색 방식과 차별화된 특징을 가지며, 몇 줄의 코드로 쉽게 통합할 수 있습니다."
  source="AWS Machine Learning Blog"
  severity="Medium"
%}

#### 요약

Amazon Bedrock AgentCore의 Web Search 기능이 정식 출시되었습니다. 이 기능은 기존 검색 방식과 차별화된 특징을 가지며, 몇 줄의 코드로 쉽게 통합할 수 있습니다.

**실무 포인트**: AI Agent 도입 시 권한 범위 설정과 출력 검증 체계를 사전에 수립하세요.


#### 실무 적용 포인트

- [Amazon Bedrock] AI 에이전트 도구 호출 권한 및 접근 범위 최소화 설계
- 에이전트 행동 로깅 및 감사 파이프라인 구축 검토
- 에이전트 출력에 대한 검증 및 사람 감독(Human-in-the-Loop) 설계
- Amazon Bedrock 이슈의 공개 IoC·지표를 SIEM/보안 이벤트 룰에 반영하고 탐지 검증

---

### 2.2 Adobe Marketing Agent for Amazon Quick의 인사이트로 캠페인 워크플로우 가속화

{% include news-card.html
  title="Adobe Marketing Agent for Amazon Quick의 인사이트로 캠페인 워크플로우 가속화"
  url="https://aws.amazon.com/blogs/machine-learning/accelerate-campaign-workflow-with-insights-from-adobe-marketing-agent-for-amazon-quick/"
  summary="이 게시물은 Model Context Protocol (MCP)을 사용하여 Adobe Marketing Agent for Amazon Quick를 활성화하는 방법을 보여줍니다. 통합 구성, Adobe 자격 증명 인증, Amazon Quick에서 최신 인사이트를 얻는 과정을 안내하며, 샘플 워크플로는 audience rankings, loyalty segme"
  source="AWS Machine Learning Blog"
  severity="High"
%}

#### 요약

이 게시물은 Model Context Protocol (MCP)을 사용하여 Adobe Marketing Agent for Amazon Quick를 활성화하는 방법을 보여줍니다. 통합 구성, Adobe 자격 증명 인증, Amazon Quick에서 최신 인사이트를 얻는 과정을 안내하며, 샘플 워크플로는 audience rankings, loyalty segment summaries, journey usage, conflict recommendations를 반환합니다.

**실무 포인트**: AI Agent 도입 시 권한 범위 설정과 출력 검증 체계를 사전에 수립하세요.


#### 실무 적용 포인트

- [Adobe Marketing] AI 에이전트 도구 호출 권한 및 접근 범위 최소화 설계
- 에이전트 행동 로깅 및 감사 파이프라인 구축 검토
- 에이전트 출력에 대한 검증 및 사람 감독(Human-in-the-Loop) 설계
- Adobe Marketing Agent 관련 테스트 케이스를 스테이징 환경에서 재현해 패치·완화 조치 검증

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Google Cloud의 새로운 기능

{% include news-card.html
  title="Google Cloud의 새로운 기능"
  url="https://cloud.google.com/blog/topics/inside-google-cloud/whats-new-google-cloud/"
  summary="Google Cloud의 최신 업데이트, 공지사항, 리소스, 이벤트 및 학습 기회를 한곳에서 확인할 수 있습니다. Google Cloud 블로그에서 원하는 정보를 찾는 방법에 대한 팁도 제공됩니다."
  source="Google Cloud Blog"
  severity="High"
%}

#### 요약

Google Cloud의 최신 업데이트, 공지사항, 리소스, 이벤트 및 학습 기회를 한곳에서 확인할 수 있습니다. Google Cloud 블로그에서 원하는 정보를 찾는 방법에 대한 팁도 제공됩니다.

**실무 포인트**: 인프라 및 운영 환경 영향을 검토하세요.


#### 실무 적용 포인트

- [Google Cloud의 새로운] 서비스 의존성 그래프 기반으로 변경 파급 범위(blast radius)를 사전 가시화
- 운영 지표(SLO·error budget)가 변경 이전 수준으로 수렴하는지 release gate 자동화
- 주요 서드파티 서비스의 Status 페이지를 내부 알림 파이프라인에 연동
- Google Cloud의 새로운 기능 이슈의 공개 IoC·지표를 SIEM/보안 이벤트 룰에 반영하고 탐지 검증

---

## 4. DevOps & 개발 뉴스

### 4.1 Copilot 사용량 메트릭 API에 사용자별 AI 크레딧 소비량 추가

{% include news-card.html
  title="Copilot 사용량 메트릭 API에 사용자별 AI 크레딧 소비량 추가"
  url="https://github.blog/changelog/2026-06-19-ai-credits-consumed-per-user-now-in-the-copilot-usage-metrics-api"
  summary="GitHub의 Copilot usage metrics API가 이제 사용자별 일일 AI credits 소비량을 보고하며, 이 데이터는 usage-based billing API에서 사용되는 것과 동일한 AI credits 소비 데이터에서 파생됩니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub의 Copilot usage metrics API가 이제 사용자별 일일 AI credits 소비량을 보고하며, 이 데이터는 usage-based billing API에서 사용되는 것과 동일한 AI credits 소비 데이터에서 파생됩니다.

**실무 포인트**: 인프라 및 운영 환경 영향을 검토하세요.


#### 실무 적용 포인트

- [Copilot 사용량 메트릭] GitHub Actions 워크플로우 권한을 최소화하고 제3자 Action은 SHA 고정 버전으로 참조
- Copilot 제안 코드에 SAST 게이트를 의무화해 시크릿 하드코딩·인젝션 취약점 자동 차단
- 변경 로그(changelog) 릴리스 노트에서 보안 관련 항목을 파싱해 내부 패치 SLA에 반영
- Copilot 사용량 메트릭 관련 테스트 케이스를 스테이징 환경에서 재현해 패치·완화 조치 검증

---

## 5. 블록체인 뉴스

### 5.1 JPMorgan: 비트코인 채굴 비용이 '악화'됐으며 BTC가 생산 비용 아래에서 거래 중

{% include news-card.html
  title="JPMorgan: 비트코인 채굴 비용이 '악화'됐으며 BTC가 생산 비용 아래에서 거래 중"
  url="https://bitcoinmagazine.com/news/jpmorgan-bitcoin-mining-costs-worsened"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/JPMorgan-Bitcoin-Mining-Costs-Have-Worsened-as-BTC-Trades-Below-Production-Cost.jpg"
  summary="JPMorgan은 BTC가 예상 생산 비용인 78,000달러보다 약 19% 낮은 가격에 거래되면서 비트코인 채굴 경제성이 악화되었다고 밝혔습니다. 이로 인해 상장 채굴 기업들은 사상 최대 규모의 코인 매도에 나섰으며, 업계의 약 20%가 수익성을 잃은 상황입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

JPMorgan은 BTC가 예상 생산 비용인 78,000달러보다 약 19% 낮은 가격에 거래되면서 비트코인 채굴 경제성이 악화되었다고 밝혔습니다. 이로 인해 상장 채굴 기업들은 사상 최대 규모의 코인 매도에 나섰으며, 업계의 약 20%가 수익성을 잃은 상황입니다.

**실무 포인트**: 시장 변동성 확대 시기에 피싱 도메인 모니터링을 강화하고 고액 출금 인증 절차를 점검하세요.


#### 실무 적용 포인트

- 블록체인 시장·정책 변화가 자사 자산 운용·리스크에 미치는 영향 분석
- 사용하는 프로토콜·체인의 거버넌스 변경·업그레이드 일정 추적
- 온체인 데이터를 위협 인텔에 연계해 악성 주소·믹서 사용 패턴 모니터링

---

### 5.2 예측 시장 Kalshi, 수익 20억 달러 돌파하며 IPO 추진

{% include news-card.html
  title="예측 시장 Kalshi, 수익 20억 달러 돌파하며 IPO 추진"
  url="https://bitcoinmagazine.com/news/prediction-market-kalshi-eyes-ipo"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/Prediction-Market-Kalshi-Eyes-IPO-as-Revenue-Hits-2-Billion-.jpg"
  summary="예측 시장 플랫폼 Kalshi가 연간 매출 20억 달러를 돌파하며 2027년 또는 2028년 IPO를 추진 중이다. 이 소식은 Bitcoin Magazine이 보도했다."
  source="Bitcoin Magazine"
  severity="High"
%}

#### 요약

예측 시장 플랫폼 Kalshi가 연간 매출 20억 달러를 돌파하며 2027년 또는 2028년 IPO를 추진 중이다. 이 소식은 Bitcoin Magazine이 보도했다.

**실무 포인트**: 거래소 API 키 권한을 읽기 전용 기준으로 최소화하고 출금 화이트리스트를 의무화하세요.


#### 실무 적용 포인트

- 블록체인 시장·정책 변화가 자사 자산 운용·리스크에 미치는 영향 분석
- 사용하는 프로토콜·체인의 거버넌스 변경·업그레이드 일정 추적
- 온체인 데이터를 위협 인텔에 연계해 악성 주소·믹서 사용 패턴 모니터링

---

### 5.3 Kevin Warsh는 여전히 달러를 관리해야 하지만, Bitcoin은 자동으로 작동한다

{% include news-card.html
  title="Kevin Warsh는 여전히 달러를 관리해야 하지만, Bitcoin은 자동으로 작동한다"
  url="https://bitcoinmagazine.com/news/warsh-fed-exposes-bitcoin"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/DALL·E-2026-04-14-17.45.18-A-surreal-corporate-office-environment-inspired-by-early-20th-century-surrealism_-business-professionals-in-formal-suits-stand-in-a-sleek-modern-board.webp"
  summary="Kevin Warsh의 첫 FOMC 회의에서 매파적 기조가 드러나며 달러가 지속적인 관리가 필요함을 보여준 반면, Bitcoin은 고정된 공급량으로 자동 운영되도록 설계되었다는 점을 Bitcoin Magazine의 Nick Ward가 지적했다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Kevin Warsh의 첫 FOMC 회의에서 매파적 기조가 드러나며 달러가 지속적인 관리가 필요함을 보여준 반면, Bitcoin은 고정된 공급량으로 자동 운영되도록 설계되었다는 점을 Bitcoin Magazine의 Nick Ward가 지적했다.

**실무 포인트**: 거래소 API 키 권한을 읽기 전용 기준으로 최소화하고 출금 화이트리스트를 의무화하세요.


#### 실무 적용 포인트

- 블록체인 시장·정책 변화가 자사 자산 운용·리스크에 미치는 영향 분석
- 사용하는 프로토콜·체인의 거버넌스 변경·업그레이드 일정 추적
- 온체인 데이터를 위협 인텔에 연계해 악성 주소·믹서 사용 패턴 모니터링

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [디자이너에게 AI로 뭐든 만들어보라고 한다면](https://toss.tech/article/ai_contest) | 토스 기술 블로그 | 토스 디자인챕터에서 AI Contest를 열었어요. 그중 인상적이었던 네 가지 사례를 소개합니다 |
| [Spark Connect on Kubernetes #1: 견고한 Spark Connect 만들기](https://toss.tech/article/spark-connect-on-kubernetes-1) | 토스 기술 블로그 | Spark Connect 서버에 세션이 몰리면, 무거운 작업이 다른 사용자까지 느리게 만들고 그 서버가 죽는 순간 모두가 실패합니다. 이 문제들을 어떻게 풀었는지 공유합니다 |
| [2. 전문성 밖으로 나아가기](https://toss.tech/article/technical-writing-2) | 토스 기술 블로그 | Technical Writer의 고민과 전문성을 '토독'이라는 제품으로 만들면서, 기존의 전문성을 더 확장하는 과정을 담았습니다 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 12건 | 기타 주제 |
| **AI/ML** | 2건 | The Hacker News 관련 동향, GitHub Changelog 관련 동향 |
| **클라우드 보안** | 1건 | Google Cloud Blog 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(12건)입니다. **AI/ML** 분야에서는 The Hacker News 관련 동향, GitHub Changelog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **AutoJack 공격으로 한 웹 페이지가 AI 에이전트를 하이재킹해 호스트 코드 실행 가능** 관련 긴급 패치 및 영향도 확인
- [ ] **Operation Endgame, SocGholish 서버 교란 및 14,971개 WordPress 사이트 정리** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **패치 불가능한 'usbliter8' 익스플로잇, Apple A12 및 A13 SecureROM 부트 체인 해제** 관련 보안 검토 및 모니터링
- [ ] **Adobe Marketing Agent for Amazon Quick의 인사이트로 캠페인 워크플로우 가속화** 관련 보안 검토 및 모니터링
- [ ] **Google Cloud의 새로운 기능** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Amazon Bedrock AgentCore에 웹 검색 기능 도입** 관련 AI 보안 정책 검토
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
