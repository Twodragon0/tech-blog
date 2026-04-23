---
layout: post
title: "정보 기관 주장 이후 제재 대상 Grinex, 크로스 테넌트 헬프데스크 사칭에서 데이터, Mirai 변종 Nexcorium"
date: 2026-04-19 10:52:41 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Data, CVE, Botnet]
excerpt: "정보 기관 주장 이후 제재 대상 Grinex, 크로스 테넌트 헬프데스크 사칭에서 데이터, Mirai 변종 Nexcorium를 중심으로 2026년 04월 19일 주요 보안/기술 뉴스 15건과 대응 우선순위를 정리합니다. AI, Data, CVE 등 최신 위협 동향과 DevSecOps 실무 대응 방안을 함께 다룹니다."
description: "2026년 04월 19일 보안 뉴스 요약. The Hacker News, Microsoft Security Blog, BleepingComputer 등 15건을 분석하고 정보 기관 주장 이후 제재 대상 Grinex, 크로스 테넌트 헬프데스크 사칭에서 데이터, Mirai 변종 Nexcorium 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Data, CVE]
author: Twodragon
comments: true
image: /assets/images/2026-04-19-Tech_Security_Weekly_Digest_AI_Data_CVE_Botnet.svg
image_alt: "Grinex, Mirai Nexcorium - security digest overview"
toc: true
---

{% include ai-summary-card.html
  title='정보 기관 주장 이후 제재 대상 Grinex, 크로스 테넌트 헬프데스크 사칭에서 데이터, Mirai 변종 Nexcorium'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">AI</span>
      <span class="tag">Data</span>
      <span class="tag">CVE</span>
      <span class="tag">Botnet</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>The Hacker News</strong>: 정보 기관 주장 이후 제재 대상 Grinex 거래소가 1,374만 달러 해킹으로 폐쇄</li>
      <li><strong>Microsoft Security Blog</strong>: 크로스 테넌트 헬프데스크 사칭에서 데이터 유출까지: 인간 운영 침입 플레이북</li>
      <li><strong>The Hacker News</strong>: Mirai 변종 Nexcorium, CVE-2024-3721 취약점으로 TBK DVR 장악해 DDoS 봇넷</li>'
  period='2026년 04월 19일 (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 04월 19일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 15개
- **보안 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | 정보 기관 주장 이후 제재 대상 Grinex 거래소가 1,374만 달러 해킹으로 폐쇄 | 🟠 High |
| 🔒 **Security** | Microsoft Security B | 크로스 테넌트 헬프데스크 사칭에서 데이터 유출까지: 인간 운영 침입 플레이북 | 🟠 High |
| 🔒 **Security** | The Hacker News | Mirai 변종 Nexcorium, CVE-2024-3721 취약점으로 TBK DVR 장악해 DDoS 봇넷 구축 | 🟠 High |
| ⛓️ **Blockchain** | Cointelegraph | 워런, SEC의 앳킨스가 집행 데이터로 의회를 오도했을 가능성 주장 | 🟠 High |
| ⛓️ **Blockchain** | Cointelegraph | Solana 선물 미결제약정이 이번 주 20% 증가: SOL 100달러 다음 목표일까? | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | 이란, BTC를 전략적 자산으로 간주하지만 USDt가 여전히 유류 통행료 지배: BPI | 🟡 Medium |
| 💻 **Tech** | Tech World Monitor | World Monitor - 실시간 글로벌 인텔리전스 대시보드 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | Show GN: Paperclip + Gastown에서 영감을 받은, “영구기관” 컨셉의 오픈소스 AI 에이전트 프레임워크 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | 분리된 구간 집합 위에서 계산하는 계산기 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: 정보 기관 주장 이후 제재 대상 Grinex 거래소가 1,374만 달러 해킹으로 폐쇄, 크로스 테넌트 헬프데스크 사칭에서 데이터 유출까지: 인간 운영 침입 플레이북, Mirai 변종 Nexcorium, CVE-2024-3721 취약점으로 TBK DVR 장악해 DDoS 봇넷 구축 등 High 등급 위협 4건에 대한 탐지 강화가 필요합니다.
- 이번 주기에는 즉시 대응이 필요한 Critical 등급 위협은 확인되지 않았으며, 식별된 High 등급 이슈에 대한 지속적인 모니터링을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 정보 기관 주장 이후 제재 대상 Grinex 거래소가 1,374만 달러 해킹으로 폐쇄

{% include news-card.html
  title="정보 기관 주장 이후 제재 대상 Grinex 거래소가 1,374만 달러 해킹으로 폐쇄"
  url="https://thehackernews.com/2026/04/1374m-hack-shuts-down-sanctioned-grinex.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhPcUvJCFRqDmEr1ZDSaUJCAymmKwZOeXdmfPY6Eekp7tLOpqjXLKHilHOHlNyuxmennQE8H5oxuRTaCncC8hsoGYEloD8OrDlR1wpbxGivBBB7KdVX8kiv_pOzC6GQ7LNPKoJGkFklpW0XutuLRPjl3I5cPta1n-BqVyAdO1luW3EUR8jyiZEtVjVTGWUK/s1600/grinex.jpg"
  summary="영국과 미국의 제재를 받은 가상자산 거래소 Grinex가 서방 정보기관의 관여를 주장하는 1,374만 달러 규모의 해킹 피해를 입고 운영을 중단했습니다. 거래소는 외국 정보기관의 특징을 보이는 대규모 사이버 공격으로 인해 자금이 유출되었다고 밝혔습니다."
  source="The Hacker News"
  severity="High"
%}

#### 요약

영국과 미국의 제재를 받은 가상자산 거래소 Grinex가 서방 정보기관의 관여를 주장하는 1,374만 달러 규모의 해킹 피해를 입고 운영을 중단했습니다. 거래소는 외국 정보기관의 특징을 보이는 대규모 사이버 공격으로 인해 자금이 유출되었다고 밝혔습니다.

**실무 포인트**: 보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요.

#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | High |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |

#### 권장 조치

- [ ] 영향받는 시스템/소프트웨어 인벤토리 확인
- [ ] 벤더 패치 및 보안 권고 확인
- [ ] SIEM/EDR 탐지 룰 업데이트 검토
- [ ] 필요시 네트워크 격리 또는 임시 완화 조치 적용
- [ ] 보안팀 내 공유 및 모니터링 강화

---

### 1.2 크로스 테넌트 헬프데스크 사칭에서 데이터 유출까지: 인간 운영 침입 플레이북

{% include news-card.html
  title="크로스 테넌트 헬프데스크 사칭에서 데이터 유출까지: 인간 운영 침입 플레이북"
  url="https://www.microsoft.com/en-us/security/blog/2026/04/18/crosstenant-helpdesk-impersonation-data-exfiltration-human-operated-intrusion-playbook/"
  image="https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2026/04/MS_Actional-Insights_Rapid-response.jpg"
  summary="위협 행위자들이 Microsoft Teams 외부 협업 기능을 악용해 IT helpdesk 직원을 사칭하고 사용자들을 속여 원격 접근 권한을 얻고 있습니다. 침입 후 공격자들은 합법적 도구와 표준 관리 프로토콜을 남용해 측면 이동과 데이터 유출을 수행하며, Microsoft Defender는 Teams, 엔드포인트, ID 원격 분석을 통해 이러한 활동을 탐"
  source="Microsoft Security Blog"
  severity="High"
%}

# Cross‑tenant helpdesk impersonation 공격 분석: DevSecOps 관점

## 1. 기술적 배경 및 위협 분석
이 공격은 Microsoft Teams의 외부 협업 기능을 악용한 다단계 위협입니다. 공격자는 외부 테넌트에서 IT 헬프데스크를 사칭하여 피싱 메시지를 전송하고, 사용자를 속여 원격 접속 권한을 획득합니다. 내부 진입 후에는 **Living off the Land(LotL)** 전술을 활용하여 RDP, PsExec, PowerShell 같은 합법적인 관리 도구와 프로토콜을 남용하여 측면 이동과 데이터 유출을 수행합니다. 이는 정상적인 IT 지원 활동으로 위장하기 때문에 전통적인 시그니처 기반 탐지로는 발견하기 어렵습니다. Microsoft Defender는 Teams, 엔드포인트, ID 원격 분석을 연계하여 이러한 비정상적인 행위 패턴을 탐지합니다.

## 2. 실무 영향 분석
DevSecOps 관점에서 이 공격은 **CI/CD 파이프라인과 운영 환경 모두에 대한 위협**으로 확대될 수 있습니다. 공격자가 획득한 권한으로 개발자 워크스테이션, 빌드 서버, 구성 관리 저장소에 접근하여 소스 코드, 인프라 키, 배포 자격증명을 탈취하거나 악성 코드를 주입할 위험이 있습니다. 특히, 클라우드 네이티브 환경에서는 하나의 침해된 계정이 광범위한 테넌트 내 리소스로의 접근으로 이어질 수 있습니다. 이는 "신뢰할 수 있는" 내부 도구를 이용한 공격이므로, DevSecOps 팀은 도구 사용의 정상 기준선을 정의하고 행위 기반 이상 탐지에 집중해야 함을 시사합니다.

## 3. 대응 체크리스트
- [ ] **외부 협업 정책 검토 및 강화**: Microsoft Teams 및 다른 협업 도구의 외부 접근 정책을 검토하여, 필요한 경우에만 허용하고 신원 확인 절차를 강화합니다.
- [ ] **관리 도구 사용 모니터링 기준선 설정**: RDP, PsExec, PowerShell 등 내부 관리 도구의 정상적인 사용 패턴(시간, 사용자, 소스) 기준선을 수립하고, 이를 벗어나는 행위를 탐지하도록 행위 분석 규칙을 구성합니다.
- [ ] **최소 권한 원칙 적용 및 세션 격리**: IT 지원을 위한 원격 접속 시에는 **Just-In-Time(JIT)** 권한 상승과 세션 격리 솔루션을 도입하여, 공격자가 획득한 세션으로 중요한 시스템에 직접 접근하거나 이동하는 것을 제한합니다.
- [ ] **엔드포인트 및 ID 원격 분석 통합 모니터링**: Microsoft Defender for Endpoint, Identity, Cloud Apps 등의 원격 분석을 연계하여, Teams의 비정상적인 외부 메시지, 의심스러운 로그인, 파일 대량 접근 등 다단계 공격의 연쇄를 탐지할 수 있는 통합 위협 헌팅 쿼리를 정기적으로 실행합니다.
- [ ] **사용자 인식 교육 시뮬레이션 강화**: IT 헬프데스크를 사칭한 피싱 공격 시나리오를 정기적인 보안 인식 교육 및 모의 훈련에 포함시켜, 사용자가 비정상적인 원격 지원 요청을 식별하고 보고할 수 있도록 합니다.

---

### 1.3 Mirai 변종 Nexcorium, CVE-2024-3721 취약점으로 TBK DVR 장악해 DDoS 봇넷 구축

{% include news-card.html
  title="Mirai 변종 Nexcorium, CVE-2024-3721 취약점으로 TBK DVR 장악해 DDoS 봇넷 구축"
  url="https://thehackernews.com/2026/04/mirai-variant-nexcorium-exploits-cve.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh6cxZZMfiWctk3Me9QO6UlzVRFab0SPGMTzThjpcPHCXm49bQ0rRvtG2W6gicJw4Mi1QUuv-yTDMK5GKJju3QicyjYJwdbA86Ok8w2oU5Vg28l4s0HAVv7_c03dStaM7OPd4Yq0khmm9MeQVUYnCYThMx4JvkCnZZ5PEtCXAA90vKfsAumsMAIw085JIsz/s1600/botnet-ddos.jpg"
  summary="Fortinet FortiGuard Labs와 Palo Alto Networks Unit 42에 따르면 위협 행위자들이 TBK DVR과 EoL TP-Link Wi-Fi 라우터의 보안 결함을 악용해 Mirai 봇넷 변종을 배포하고 있습니다. TBK DVR을 대상으로 한 공격은 중간 심각도 명령어 삽입 취약점인 CVE-2024-3721을 악용하는 것으로 확인되"
  source="The Hacker News"
  severity="High"
%}

# Mirai 변종 Nexcorium의 TBK DVR 취약점(CVE-2024-3721) 악용 분석

## 1. 기술적 배경 및 위협 분석
이 공격은 **Mirai 봇넷의 변종인 Nexcorium**이 중간 심각도(CVSS 6.3)의 **명령어 삽입 취약점(CVE-2024-3721)**을 통해 TBK DVR 장치를 탈취하는 사례입니다. 취약점 자체는 인증이 필요하지만, 공격자는 약한 기본 자격증명이나 다른 경로를 통해 인증을 우회한 후, 시스템 명령을 삽입하여 봇넷 에이전트를 배포합니다. 특히 주목할 점은 **EoL(수명 주기 종료) TP-Link 라우터**도 함께 표적으로 삼고 있다는 것입니다. 이는 공격자가 보안 패치가 중단된 취약한 IoT 장치를 체계적으로 탐색 및 악용하여 대규모 DDoS 공격 인프라를 구축하고 있음을 보여줍니다. Mirai 변종은 지속적으로 새로운 취약점을 탐색하며, 기존 시그니처 기반 탐지 회피 기법을 진화시키고 있습니다.

## 2. 실무 영향 분석
DevSecOps 관점에서 이 사건은 **소프트웨어 구성 요소 관리(SBOM)와 자산 가시화의 중요성**을 다시 한번 강조합니다. TBK DVR과 같은 타사 하드웨어/펌웨어가 조직 네트워크에 연결되어 있을 경우, 예상치 못한 공격 경로가 될 수 있습니다. 또한, EoL 장치는 보안 정책상 관리 범위에서 쉽게 누락되기 때문에, 지속적인 자산 인벤토리 관리와 위험 평가에서 반드시 고려되어야 합니다. 이 공격은 중간 심각도 취약점이라도 실제로는 봇넷 가입을 통한 대규모 DDoS 공격으로 이어질 수 있어, **CVSS 점수에만 의존한 위험도 평가의 한계**를 보여줍니다. 내부 개발 장비뿐 아니라, 운영 환경의 모든 IoT/임베디드 장치에 대한 보안 태세 강화가 필요합니다.

## 3. 대응 체크리스트
- [ ] **네트워크 연결된 모든 IoT/임베디드 장치에 대한 즉각적인 인벤토리 점검**을 수행하고, TBK DVR, EoL TP-Link 라우터 등 영향을 받는 제품이 내부 네트워크에 존재하는지 확인하세요.
- [ ] **CVE-2024-3721 패치 적용 가능 여부를 확인**하고, 펌웨어 업데이트가 불가능한 장치는 네트워크 세분화(예: VLAN 분리, 아웃바운드 트래픽 제한)를 통해 위험을 격리하세요.
- [ ] **기본/약한 자격증명 사용을 전사적으로 점검**하고, 특히 IoT 장치에 대해 강력한 고유 비밀번호 적용을 의무화하세요.
- [ ] **네트워크 트래픽 모니터링에서 알려진 Mirai C&C 서버 도메인/IP와의 통신, 비정상적인 아웃바운드 트래픽 패턴(예: 대량 UDP 패킷)을 탐지할 수 있는 규칙을 검토 및 업데이트**하세요.
- [ ] **취약점 관리 프로세스를 재평가**하여, 공식 패치가 없는 EoL 장치에 대한 위험 처리 절차(교체, 격리, 보완 통제 적용)를 명확히 정의하고 실행하세요.

#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - T1203  # Exploitation for Client Execution
    - T1190  # Exploit Public-Facing Application
```

---

## 2. 블록체인 뉴스

### 2.1 워런, SEC의 앳킨스가 집행 데이터로 의회를 오도했을 가능성 주장

{% include news-card.html
  title="워런, SEC의 앳킨스가 집행 데이터로 의회를 오도했을 가능성 주장"
  url="https://cointelegraph.com/news/warren-claims-sec-atkins-likely-misled-congress-over-enforcement-data?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjYtMDQvMDE5ZGEyY2UtODU5MS03YmU4LTllYjItODliNmY1MTIwZDA4LmpwZw==.jpg"
  summary="SEC 의장 Paul Atkins가 기관의 집행 활동에 대해 의회를 오도하려 했다는 의원 Elizabeth Warren의 주장으로 비판을 받고 있습니다. Warren 의원은 Atkins 의장이 관련 데이터를 의도적으로 왜곡했을 가능성을 제기했습니다."
  source="Cointelegraph"
  severity="High"
%}

#### 요약

SEC 의장 Paul Atkins가 기관의 집행 활동에 대해 의회를 오도하려 했다는 의원 Elizabeth Warren의 주장으로 비판을 받고 있습니다. Warren 의원은 Atkins 의장이 관련 데이터를 의도적으로 왜곡했을 가능성을 제기했습니다.

**실무 포인트**: 규제 변화에 따른 컴플라이언스 영향을 법무팀과 사전 검토하세요.

---

### 2.2 Solana 선물 미결제약정이 이번 주 20% 증가: SOL 100달러 다음 목표일까?

{% include news-card.html
  title="Solana 선물 미결제약정이 이번 주 20% 증가: SOL 100달러 다음 목표일까?"
  url="https://cointelegraph.com/news/solana-futures-open-interest-rose-by-20-this-week-is-100-sol-next?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjYtMDQvMDE5ZGExZWQtZmRlYS03NDM4LWExNjQtMWI4OGY3MWQzODJjLmpwZw==.jpg"
  summary="Solana의 선물 미결제약정이 이번 주 20% 증가하며 SOL의 회복세가 이어지고 있습니다. 암호화폐 시장의 전반적인 상승과 함께 트레이더들은 SOL이 100달러를 돌파할지 관심을 가지고 지켜보고 있습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

Solana의 선물 미결제약정이 이번 주 20% 증가하며 SOL의 회복세가 이어지고 있습니다. 암호화폐 시장의 전반적인 상승과 함께 트레이더들은 SOL이 100달러를 돌파할지 관심을 가지고 지켜보고 있습니다.

**실무 포인트**: 스마트 컨트랙트 기반 서비스의 접근 제어와 트랜잭션 모니터링을 점검하세요.

---

### 2.3 이란, BTC를 전략적 자산으로 간주하지만 USDt가 여전히 유류 통행료 지배: BPI

{% include news-card.html
  title="이란, BTC를 전략적 자산으로 간주하지만 USDt가 여전히 유류 통행료 지배: BPI"
  url="https://cointelegraph.com/news/iran-btc-strategic-usdt-dominate-oil-tolls?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBoLmNvbS91cGxvYWRzLzIwMjYtMDQvMDE5ZGEyYWQtMGVlNS03YjMzLTkzYzAtMGM1YWI3ZDYwYjNmLmpwZw==.jpg"
  summary="이란 정부는 몰수 저항성 때문에 Bitcoin을 원유 관세 지불 수단으로 채택했지만, 실제로는 USDt 같은 달러 스테이블코인만 사용되고 있습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

이란 정부는 몰수 저항성 때문에 Bitcoin을 원유 관세 지불 수단으로 채택했지만, 실제로는 USDt 같은 달러 스테이블코인만 사용되고 있습니다.

**실무 포인트**: 시장 변동성 확대 시기에 피싱 도메인 모니터링을 강화하고 고액 출금 인증 절차를 점검하세요.

---

## 3. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [World Monitor - 실시간 글로벌 인텔리전스 대시보드](https://tech.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.00&view=global&timeRange=7d&layers=cables%2Cweather%2Ceconomic%2Coutages%2Cdatacenters%2Cnatural%2CstartupHubs%2CcloudRegions%2CtechHQs%2CtechEvents) | Tech World Monitor | Tech World Monitor 글로벌 대시보드 기반 기술 동향 요약입니다. Real-time global intelligence dashboard with live news, markets, military tracking, infrastructure monitoring, and geopolitical data |
| [Show GN: Paperclip + Gastown에서 영감을 받은, “영구기관” 컨셉의 오픈소스 AI 에이전트 프레임워크](https://news.hada.io/topic?id=28676) | GeekNews (긱뉴스) | 안녕하세요, Paperclip과 Gastown에서 영감을 받아, 토큰만 있으면 AI가 스스로 일을 이어가며 제품을 키워나가는 “영구기관(perpetual engine)” 컨셉의 오픈소스 에이전트 프레임워크를 만들었습니다. 핵심 아이디어는 단순합니다: AI를 단발성 호출이 아니라, 지속적으로 작동하는 시스템으로 |
| [분리된 구간 집합 위에서 계산하는 계산기](https://news.hada.io/topic?id=28675) | GeekNews (긱뉴스) | 분리된 구간들의 합집합 을 입력으로 받아 사칙연산, 함수 호출, 거듭제곱까지 수행하며, interval union arithmetic 를 브라우저에서 직접 계산 가능 결과 구간은 입력 합집합에서 고른 값들로 같은 식을 실수 위에서 계산했을 때의 값을 반드시 포함 |

---

## 4. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 14건 | 기타 주제 |
| **AI/ML** | 1건 | Show GN |

이번 주기의 핵심 트렌드는 **기타**(14건)입니다. **AI/ML** 분야에서는 Show GN 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Protobuf 라이브러리의 치명적 결함으로 JavaScript 코드 실행이 가능해져** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **정보 기관 주장 이후 제재 대상 Grinex 거래소가 1,374만 달러 해킹으로 폐쇄** 관련 보안 검토 및 모니터링
- [ ] **크로스 테넌트 헬프데스크 사칭에서 데이터 유출까지: 인간 운영 침입 플레이북** 관련 보안 검토 및 모니터링
- [ ] **Mirai 변종 Nexcorium, CVE-2024-3721 취약점으로 TBK DVR 장악해 DDoS 봇넷 구축** (CVE-2024-3721) 관련 보안 검토 및 모니터링

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
