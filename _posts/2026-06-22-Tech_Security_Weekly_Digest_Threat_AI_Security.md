---
layout: post
title: "2026년 06월 22일 주간 보안 다이제스트: 블록체인·보안 위협·AI (10건)"
date: 2026-06-22 09:43:28 +0900
last_modified_at: 2026-06-22T09:43:28+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Threat, AI, Security]
excerpt: "악명 높은 ‘샌드위치 공격’ 봇 Jaredfromsubway.eth · 위협 브리프: 대규모 자격 증명 공격 완화 방안을 비롯한 2026년 06월 22일 보안/기술 동향 10건을 DevSecOps 시선으로 정리합니다. 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다."
description: "2026년 06월 22일 보안 뉴스 요약. Cointelegraph, Unit 42 (Palo Alto), CoinDesk 등 10건을 분석하고 악명 높은 '샌드위치 공격' 봇, 위협 브리프: 대규모 자격 증명 공격 완화 방안, Sonic token 5% 하락 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Threat, AI, Security]
author: Twodragon
comments: true
image: /assets/images/2026-06-22-Tech_Security_Weekly_Digest_Threat_AI_Security.svg
image_alt: "Sonic token 5% - security digest overview"
toc: true
summary_card:
  title: "2026년 06월 22일 주간 보안 다이제스트: 블록체인·보안 위협·AI (10건)"
  period: "2026년 06월 22일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Threat"
    - "AI"
    - "Security"
    - "2026"
  highlights:
    - { source: "Cointelegraph", title: "악명 높은 ‘샌드위치 공격’ 봇 Jaredfromsubway.eth, 750만 달러 규모 익스플로잇 피해" }
    - { source: "Unit 42 (Palo Alto)", title: "위협 브리프: 대규모 자격 증명 공격 완화 방안" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 06월 22일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 10개
- **보안 뉴스**: 2개
- **블록체인 뉴스**: 3개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | Cointelegraph | 악명 높은 ‘샌드위치 공격’ 봇 Jaredfromsubway.eth, 750만 달러 규모 익스플로잇 피해 | 🟠 High |
| 🔒 **Security** | Unit 42 (Palo Alto) | 위협 브리프: 대규모 자격 증명 공격 완화 방안 | 🟠 High |
| ⛓️ **Blockchain** | Cointelegraph | Sonic token 5% 하락, Sonic Labs 이사회에서 전직 임원 3명 사임 | 🟡 Medium |
| ⛓️ **Blockchain** | CoinDesk | AI가 암호화폐 보안을 더 저렴하고, 빠르고, 무시하기 어렵게 만들고 있다 | 🟡 Medium |
| ⛓️ **Blockchain** | CoinDesk | STRC가 액면가를 잃은 과정: Strategy 우선주 폭락의 타임라인 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | 머신러닝 연구의 선(Zen)과 예술 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | ClickHouse 오픈소스 10년 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | 미국인들, SpaceX가 은퇴 저축에 미치는 영향에 불안 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: 악명 높은 ‘샌드위치 공격’ 봇 Jaredfromsubway.eth, 750만 달러 규모 익스플로잇 피해, 위협 브리프: 대규모 자격 증명 공격 완화 방안 등 High 등급 위협 2건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | Medium | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 악명 높은 ‘샌드위치 공격’ 봇 Jaredfromsubway.eth, 750만 달러 규모 익스플로잇 피해

{% include news-card.html
  title="악명 높은 '샌드위치 공격' 봇 Jaredfromsubway.eth, 750만 달러 규모 익스플로잇 피해"
  url="https://cointelegraph.com/news/notorious-sandwich-attack-bot-jaredfromsubwayeth-exploited-for-75m?utm_source=rss&utm_medium=rss&utm_campaign=rss"
  image="https://s3-images.ctmedia.io/media/article-covers/hi-how-cybercriminals-are-exploiting-digital-twins-for-social-engineering.jpg"
  summary="Jaredfromsubway.eth 봇이 750만 달러 규모의 익스플로잇을 당했다. 이 봇은 2024년 11월부터 2025년 10월까지 이더리움에서 발생한 샌드위치 어택의 70%를 담당했던 악명 높은 존재였다."
  source="Cointelegraph"
  severity="High"
%}

# DevSecOps 관점 분석: Jaredfromsubway.eth 샌드위치 공격 봇 피해 사례

## 1. 기술적 배경 및 위협 분석

Jaredfromsubway.eth는 이더리움 네트워크에서 **MEV(Maximal Extractable Value) 기반 샌드위치 공격**을 자동화한 악성 봇으로, 2024년 11월~2025년 10월 기간 동안 이더리움 샌드위치 공격의 약 70%를 담당했습니다. 샌드위치 공격은 사용자의 트랜잭션 전후에 악의적인 트랜잭션을 끼워넣어 가격 슬리피지를 유발하고 차익을 취하는 방식입니다.

이번 사건은 해당 봇 자체가 **취약점(스마트 컨트랙트 로직 결함 또는 프라이빗 키 유출)** 을 통해 750만 달러 규모로 탈취당한 사례입니다. 공격자는 봇의 MEV 수익을 가로채거나 봇이 사용하는 유동성 풀을 조작했을 가능성이 높습니다. 이는 **공격 도구가 역으로 공격받는** 전형적인 **공급망 보안 위협** 사례입니다.

## 2. 실무 영향 분석

DevSecOps 실무자에게 이 사건은 다음과 같은 시사점을 제공합니다:

- **블록체인 기반 애플리케이션의 CI/CD 파이프라인 보안**: 스마트 컨트랙트 배포 시 취약점 스캐닝(Slither, Mythril 등)과 **비정상 트랜잭션 패턴 감지**를 자동화해야 합니다.
- **MEV 보호 메커니즘 부재 위험**: DApp 개발 시 샌드위치 공격을 방어하는 **스마트 컨트랙트 레벨의 슬리피지 보호 로직**이 필수적입니다.
- **프라이빗 키 관리**: 봇이나 자동화 시스템의 프라이빗 키가 하드코딩되거나 안전하지 않은 저장소에 노출될 경우 전체 시스템이 위험에 처할 수 있습니다.
- **모니터링의 중요성**: 온체인 데이터 분석 도구(Dune Analytics, The Graph)를 활용한 **실시간 이상 트랜잭션 탐지**가 필요합니다.

## 3. 대응 체크리스트

- [ ] **스마트 컨트랙트 보안 감사 자동화**: CI/CD 파이프라인에 Slither, Mythril, Echidna 등 정적/동적 분석 도구를 통합하여 모든 배포 전 취약점 스캔 수행
- [ ] **MEV 방어 로직 구현**: 사용자 트랜잭션에 대해 최대 슬리피지 제한, 타임스탬프 기반 보호, Commit-Reveal 스킴 등 샌드위치 공격 방어 메커니즘 적용
- [ ] **프라이빗 키 및 시크릿 관리 강화**: Vault, AWS Secrets Manager 등 중앙 집중식 시크릿 관리 도구 사용, 키 순환 정책 수립 및 감사 로그 활성화
- [ ] **블록체인 모니터링 및 알림 체계 구축**: 온체인 트랜잭션 패턴 이상 징후(동일 주소의 반복적 프론트러닝, 비정상 가스 가격 변동) 탐지 시 Slack/PagerDuty 알림 연동
- [ ] **취약점 대응 훈련 및 보안 정책 업데이트**: 정기적인 레드팀 모의훈련을 통해 MEV 공격 시나리오 테스트, 발견된 취약점에 대한 핫픽스 배포 프로세스 문서화

---

### 1.2 위협 브리프: 대규모 자격 증명 공격 완화 방안

{% include news-card.html
  title="위협 브리프: 대규모 자격 증명 공격 완화 방안"
  url="https://unit42.paloaltonetworks.com/large-scale-credential-attacks/"
  image="https://unit42.paloaltonetworks.com/wp-content/uploads/2026/06/07_Vulnerabilities_1920x900-1.jpg"
  summary="Unit 42의 최신 보고서는 보안 업체 장치를 대상으로 한 최근 캠페인에 초점을 맞춰 대규모 자격 증명 공격에 대비하고 완화하기 위한 지침을 제공합니다. 이 게시물은 대규모 자격 증명 공격 완화에 대한 위협 브리핑입니다."
  source="Unit 42 (Palo Alto)"
  severity="High"
%}

# DevSecOps 실무자 관점 분석: 대규모 크리덴셜 공격 완화

## 1. 기술적 배경 및 위협 분석

최근 Palo Alto Networks Unit 42가 보고한 대규모 크리덴셜 공격 캠페인은 보안 벤더 장비를 표적으로 삼아, 자격 증명 탈취 후 내부망 침투를 시도하는 정교한 공격 패턴을 보입니다. 주요 특징은 다음과 같습니다:

- **공격 벡터**: 무차별 대입(Brute-force) 및 크리덴셜 스터핑(Credential Stuffing)을 병행하며, 기존에 유출된 사용자 이름/비밀번호 조합을 재사용
- **타겟**: 방화벽, VPN 게이트웨이, 원격 접속 솔루션 등 보안 장비의 관리 인터페이스 (특히 기본 계정이나 패치되지 않은 장비 취약)
- **규모**: 분산된 봇넷을 활용하여 초당 수천 건의 로그인 시도, IP 기반 차단 우회 시도
- **위험**: 성공 시 공격자는 관리자 권한 탈취 → 네트워크 전반으로 측면 이동(Lateral Movement) → 랜섬웨어/데이터 유출로 이어짐

DevSecOps 환경에서 특히 취약한 점은 CI/CD 파이프라인에서 사용되는 서비스 계정(Service Account)이나 API 토큰이 유출될 경우, 코드 저장소와 배포 인프라 전체가 위험에 노출된다는 점입니다.

## 2. 실무 영향 분석

DevSecOps 실무자에게 이 위협은 다음과 같은 직접적 영향을 미칩니다:

- **CI/CD 파이프라인 보안**: Jenkins, GitLab Runner, ArgoCD 등에 사용되는 크리덴셜이 탈취되면 악성 코드 주입(Malicious Code Injection) 가능
- **인프라 접근 통제**: Kubernetes 클러스터, 클라우드 콘솔 접근용 서비스 계정이 공격 대상이 될 수 있음
- **Secrets 관리 체계**: 하드코딩된 비밀번호나 환경 변수에 의존하는 레거시 설정이 위험
- **운영 부담**: 대규모 로그인 실패 로그 처리와 IP 차단 정책 업데이트로 인한 운영 오버헤드 증가
- **규정 준수**: GDPR, PCI-DSS 등에서 요구하는 다중 인증(MFA) 미적용 시 규제 위반 가능성

특히 보안 장비(방화벽, WAF 등) 자체가 공격받으면 전체 보안 아키텍처가 무력화되므로, 이에 대한 사전 대비가 필수적입니다.

## 3. 대응 체크리스트

- [ ] **CI/CD 파이프라인 크리덴셜 회전 자동화**: 모든 서비스 계정과 API 토큰에 대해 최소 90일 주기 자동 교체 정책 적용 (Vault, AWS Secrets Manager 등 활용)
- [ ] **보안 장비 관리 인터페이스 접근 제한**: VPN 또는 점프 호스트(Jump Host)를 통해서만 관리 인터페이스 접근 허용, 기본 포트 변경 및 IP 화이트리스트 적용
- [ ] **다중 인증(MFA) 전면 적용**: 모든 관리자 계정(DevOps 도구 포함)에 대해 MFA 강제, 특히 CI/CD 트리거 계정에도 적용
- [ ] **실시간 로그인 모니터링 및 자동 차단**: 실패한 로그인 시도 임계치 초과 시 자동 IP 차단 + Slack/PagerDuty 알림 연동 (예: 5분 내 10회 실패 시 차단)
- [ ] **Secrets 스캔 파이프라인 통합**: 코드 커밋 시 GitLeaks, TruffleHog 등으로 하드코딩된 크리덴셜 탐지 → 빌드 실패 처리

---

## 2. 블록체인 뉴스

### 2.1 Sonic token 5% 하락, Sonic Labs 이사회에서 전직 임원 3명 사임

{% include news-card.html
  title="Sonic token 5% 하락, Sonic Labs 이사회에서 전직 임원 3명 사임"
  url="https://cointelegraph.com/news/s-token-drops-5-as-3-former-execs-resign-from-sonic-labs-board?utm_source=rss&utm_medium=rss&utm_campaign=rss"
  image="https://s3-images.ctmedia.io/media/article-covers/bank-building-hall-entrance-revolving-doorsthreepeople.jpg"
  summary="Sonic Labs 이사회에서 Andre Cronje, Michael Kong, David Richardson 등 전직 임원 3명이 사임하면서 Sonic 토큰이 5% 하락했습니다. Matt Visser가 2월에 사임한 Mitchell Demeter를 대신해 새로운 CEO로 임명되었습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

Sonic Labs 이사회에서 Andre Cronje, Michael Kong, David Richardson 등 전직 임원 3명이 사임하면서 Sonic 토큰이 5% 하락했습니다. Matt Visser가 2월에 사임한 Mitchell Demeter를 대신해 새로운 CEO로 임명되었습니다.

---

### 2.2 AI가 암호화폐 보안을 더 저렴하고, 빠르고, 무시하기 어렵게 만들고 있다

{% include news-card.html
  title="AI가 암호화폐 보안을 더 저렴하고, 빠르고, 무시하기 어렵게 만들고 있다"
  url="https://www.coindesk.com/tech/2026/06/20/ai-is-making-crypto-security-cheaper-faster-and-harder-to-ignore"
  image="https://cdn.sanity.io/images/s3y3vcno/production/6c28c3dcd5461d3803d6e6200f1da0686dde993f-1920x1082.jpg"
  summary="AI 기반 자동화 도구가 스마트 컨트랙트 감사와 위협 탐지를 더 저렴하고 빠르게 만들면서 암호화폐 보안이 더 이상 무시하기 어려운 과제가 되고 있다고 CoinDesk가 분석했습니다."
  source="CoinDesk"
  severity="Medium"
%}

#### 요약

AI 기반 자동화 도구가 스마트 컨트랙트 감사와 위협 탐지를 더 저렴하고 빠르게 만들면서 암호화폐 보안이 더 이상 무시하기 어려운 과제가 되고 있다고 CoinDesk가 분석했습니다.

---

### 2.3 STRC가 액면가를 잃은 과정: Strategy 우선주 폭락의 타임라인

{% include news-card.html
  title="STRC가 액면가를 잃은 과정: Strategy 우선주 폭락의 타임라인"
  url="https://www.coindesk.com/markets/2026/06/20/how-strc-lost-its-par-the-timeline-behind-strategy-s-preferred-stock-meltdown"
  image="https://cdn.sanity.io/images/s3y3vcno/production/3a6393eb4ae1f1db4ef1caec0023161c16707226-6000x3376.jpg"
  summary="Strategy의 우선주 STRC가 액면가를 잃고 폭락하기까지의 과정을 CoinDesk가 시간 순으로 정리했습니다."
  source="CoinDesk"
  severity="Medium"
%}

#### 요약

Strategy의 우선주 STRC가 액면가를 잃고 폭락하기까지의 과정을 CoinDesk가 시간 순으로 정리했습니다.
---

## 3. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [머신러닝 연구의 선(Zen)과 예술](https://news.hada.io/topic?id=30672) | GeekNews (긱뉴스) | 세계적 수준의 AI 연구 는 재능만으로 이어지지 않으며, 읽기와 만들기를 반복하면서 오래 버티는 기질 이 성과를 가름함 주제 선택은 6개월짜리 유행어보다 cross-entropy, SVD, policy gradients 같은 기초 개념 을 깊게 이해하는 데서 출발해야 함 |
| [ClickHouse 오픈소스 10년](https://news.hada.io/topic?id=30671) | GeekNews (긱뉴스) | ClickHouse는 2016년 6월 15일 공개된 뒤 10년 동안 2,000명 이상이 기여하며 오픈소스 분석 데이터베이스의 대표 프로젝트로 성장함 단순 코드 공개가 아니라 기여 가이드, 코드 리뷰, 로드맵, CI, 릴리스, 문서까지 공개하는 Level 3 오픈소스 를 지향함 |
| [미국인들, SpaceX가 은퇴 저축에 미치는 영향에 불안](https://news.hada.io/topic?id=30670) | GeekNews (긱뉴스) | SpaceX의 1.77조 달러 평가액 증시 데뷔 이후, 미국인의 401(k)와 인덱스펀드가 거대 기술기업에 간접 노출될 수 있다는 우려가 커짐 은퇴 자금 상당수가 S&P 500 같은 주요 지수 추종 펀드에 묶여 있어, 개인이 원치 않아도 신규 대형 기술주를 보유하게 될 수 |

---

## 4. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 7건 | 기타 주제 |
| **AI/ML** | 2건 | CoinDesk 관련 동향, GPT |
| **인증 보안** | 1건 | Unit 42 (Palo Alto) 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(7건)입니다. **AI/ML** 분야에서는 CoinDesk 관련 동향, GPT 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **악명 높은 ‘샌드위치 공격’ 봇 Jaredfromsubway.eth, 750만 달러 규모 익스플로잇 피해** 관련 보안 영향도 분석 및 모니터링 강화

### P1 (7일 내)

- [ ] **악명 높은 ‘샌드위치 공격’ 봇 Jaredfromsubway.eth, 750만 달러 규모 익스플로잇 피해** 관련 보안 검토 및 모니터링
- [ ] **위협 브리프: 대규모 자격 증명 공격 완화 방안** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
