---
author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-02-03 10:00:00 +0900
description: '2026년 2월 3일 보안/DevOps 다이제스트: AI(Clawdbot/Moltbot) CVE-2026-25253
  원클릭 RCE, ClawHavoc 캠페인 335개 Atomic Stealer 배포, Moltbook AI 소셜네트워크 자격증명 유출(Wiz),
  가짜 VS Code 확장 ScreenConnect RAT, Shodan 대규모 노출, Cisco 31K 스킬 26% 취약점, NanoClaw Apple
  컨테이너 격리 비교, Jamf Pro/Intune MDM 앱 제어, Microsoft NTLM 폐지, OWASP Agentic AI Top 10'
excerpt: AI(Moltbot) CVE-2026-25253 RCE, ClawHavoc 335개 Atomic Stealer 캠페인,
  Moltbook 자격증명 대량 유출, 가짜 VS Code 확장 RAT 배포 등 AI 에이전트 생태계 보안 위기 총정리와 Jamf/Intune MDM
  실무 대응 가이드
image: /assets/images/2026-02-03-Weekly_Security_DevOps_Digest.svg
image_alt: Weekly Security and DevOps Digest Feb 3 2026
keywords:
- AI Security
- Moltbot
- Moltbook
- CVE-2026-25253
- ClawHub Malicious Skills
- ClawHavoc
- Atomic Stealer
- NanoClaw
- AI Agent Sandbox
- Jamf Pro MDM
- Microsoft Intune
- App Disable
- OWASP Agentic AI
- MDM Zero Trust
- SIEM MDM Integration
- DevSecOps Weekly
- NTLM Phase Out
- Supply Chain Security
- ScreenConnect RAT
- Shodan Exposure
layout: post
schema_type: Article
tags:
- Security-Weekly
- AI
- Moltbot
- Moltbook
- NanoClaw
- AI-Agent-Security
- MDM
- Jamf
- Intune
- OWASP
- Kubernetes
- DevSecOps
- ClawHub
- ClawHavoc
- NTLM
- CVE-2026-25253
- Supply-Chain
- Zero-Trust
- Atomic-Stealer
- '2026'
title: 'Weekly Security & DevOps Digest: AI Agent 보안 취약점, MDM 앱 제어, 금주 뉴스'
toc: true
---

## 요약

- **핵심 요약**: AI(Moltbot) CVE-2026-25253 RCE, ClawHavoc 335개 Atomic Stealer 캠페인, Moltbook 자격증명 대량 유출, 가짜 VS Code 확장 RAT 배포 등 AI 에이전트 생태계 보안 위기 총정리와 Jamf/Intune MDM 실무 대응 가이드
- **주요 주제**: Weekly Security & DevOps Digest: AI Agent 보안 취약점, MDM 앱 제어, 금주 뉴스
- **키워드**: Security-Weekly, AI, Moltbot, Moltbook, NanoClaw

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">Weekly Security & DevOps Digest (2026년 02월 03일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">AI</span>
      <span class="tag">Moltbot</span>
      <span class="tag">Moltbook</span>
      <span class="tag">NanoClaw</span>
      <span class="tag">ClawHavoc</span>
      <span class="tag">AI-Agent-Security</span>
      <span class="tag">MDM</span>
      <span class="tag">Jamf</span>
      <span class="tag">Intune</span>
      <span class="tag">OWASP</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">NTLM</span>
      <span class="tag">Supply-Chain</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>AI(Moltbot) 연쇄 보안 사건</strong>: CVE-2026-25253 원클릭 RCE(CVSS 8.8), ClawHavoc 캠페인 335개 Atomic Stealer 배포, Moltbook 자격증명 대량 유출(Wiz), 가짜 VS Code 확장 ScreenConnect RAT, Shodan 대규모 인스턴스 노출</li>
      <li><strong>MDM 앱 비활성화 실무 가이드</strong>: Jamf Pro Configuration Profile 기반 앱 제한, Microsoft Intune App Protection Policy, MDM 선택 의사결정 플로차트 제공</li>
      <li><strong>금주 뉴스 하이라이트</strong>: Microsoft NTLM 3단계 폐지, Snowflake-OpenAI 2억달러 파트너십, Kubernetes 1.33 보안 강화, SBOM 컴플라이언스 동향</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, IT 관리자, MDM 운영자</span>
  </div>
</div>
</div>

> **함께 읽기**: 지난주 보안 위협 인텔리전스 다이제스트 [Weekly Security Threat Intelligence Digest](/2026-02-02-Weekly_Security_Threat_Intelligence_Digest)에서 Notepad++ 국가 지원 공급망 공격, SK쉴더스 보안 리포트 종합, HashiCorp 보안 자동화를 심층 분석합니다. 기술/AI/블록체인 소식은 [Weekly Tech & AI & Blockchain Digest](/2026-02-02-Weekly_Tech_AI_Blockchain_Digest)를 참고하세요.

## 개요

2026년 2월 첫째 주, AI 에이전트 생태계에 **연쇄 보안 위협**이 현실화되었습니다. AI(구 Clawdbot/Moltbot)를 둘러싼 보안 사건이 **여러 건 동시다발적으로 발생**하며, AI 코딩 에이전트의 보안이 중요해지고 있습니다:

- **CVE-2026-25253 원클릭 RCE**(CVSS 8.8): depthfirst 연구원 Mav Levin이 발견한 인증 토큰 탈취 기반 원격 코드 실행
- **ClawHavoc 캠페인**: Koi Security가 ClawHub에서 발견한 341개 악성 스킬 중 **335개가 macOS Atomic Stealer(AMOS)** 배포
- **Moltbook 자격증명 유출**: Wiz Inc.가 AI 소셜네트워크 Moltbook에서 **수백만 건의 자격증명이 인증 없이 노출**된 것을 발견
- **가짜 VS Code 확장**: Clawdbot 이름을 사칭한 VS Code 확장이 **ScreenConnect RAT** 설치
- **Shodan 대규모 노출**: 2026년 1월 25일 자가 호스팅 AI 인스턴스의 대량 인덱싱 발견

**AI(구 Clawdbot/Moltbot)**는 원래 2025년 11월 Peter Steinberger가 Clawdbot이라는 이름으로 출시했으며, Anthropic의 상표 요청으로 Moltbot으로 개명한 뒤 다시 AI로 이름을 변경했습니다. GitHub 스타 145,000+, 포크 20,000+을 기록한 이 프로젝트는 52개 이상의 모듈이 단일 Node.js 프로세스에서 무제한 권한으로 실행되는 구조입니다. Cisco는 이를 **"치명적 삼중주(Lethal Trifecta)"** -- 개인 데이터 접근, 신뢰할 수 없는 콘텐츠 노출, 외부 통신 능력 -- 라고 경고했습니다. 대안으로 **NanoClaw**가 Apple 컨테이너 격리와 최소 권한 원칙을 적용한 ~500줄 핵심 코드로 주목받고 있으며, OWASP Agentic AI Top 10이 프레임워크로 자리잡고 있습니다.

엔터프라이즈 환경에서는 이러한 AI 에이전트의 무단 설치를 탐지하고 제어하기 위해 **MDM(Mobile Device Management)을 통한 앱 비활성화/제한**이 Zero Trust 전략의 핵심 구성요소로 부상했습니다. Jamf Pro의 Configuration Profile과 Microsoft Intune의 App Protection Policy를 비교하여, 환경별 최적화된 앱 제어 전략과 의사결정 가이드를 제시합니다.

아울러 **Microsoft의 NTLM 3단계 폐지 계획**, **Snowflake-OpenAI 2억달러 파트너십** 등 금주 주요 보안/기술 뉴스를 심층 분석합니다.

---

## 1. AI AI 에이전트 보안: 어떤 위협이 있는가?

### 1.1 배경: AI 코딩 에이전트의 보안 위협은 왜 심각한가?

AI 코딩 에이전트가 개발자의 터미널과 파일 시스템에 직접 접근하면서, **에이전트의 권한 범위와 격리 수준**이 새로운 보안 과제가 되었습니다. 2026년 2월 첫째 주에만 AI 관련 보안 사건이 5건 이상 동시다발적으로 발생하면서, 이 위협이 이론적 가능성이 아닌 **현실적인 공격 벡터**임이 확인되었습니다.

| 위협 요소 | 설명 | 심각도 |
|-----------|------|--------|
| **무제한 파일 시스템 접근** | 에이전트가 시스템 전체 파일을 읽고 쓸 수 있음 | Critical |
| **프로세스 실행 권한** | 임의의 셸 명령어 실행 가능 | Critical |
| **네트워크 접근** | 외부 API 호출, 데이터 유출 가능 | High |
| **단일 프로세스 모델** | 모든 모듈이 같은 권한으로 실행 | High |
| **프롬프트 인젝션** | 악성 코드 코멘트를 통한 에이전트 조작 | High |
| **공급망 공격** | 서드파티 스킬/플러그인을 통한 악성 코드 주입 | Critical |

### 1.2 AI(Clawdbot/Moltbot) 아키텍처와 최신 보안 사건 분석

#### 이름 변천사 및 프로젝트 규모

AI는 2025년 11월 **Peter Steinberger**가 **Clawdbot**이라는 이름으로 출시한 오픈소스 AI 개인 에이전트입니다. Anthropic의 Claude를 기반으로 만들어졌으며, 원래 이름은 Claude Code를 로딩할 때 나타나는 캐릭터에서 영감을 받았습니다.

> 출처: [CNBC](https://www.cnbc.com/2026/02/02/ai-open-source-ai-agent-rise-controversy-clawdbot-moltbot-moltbook.html), [Scientific American](https://www.scientificamerican.com/article/moltbot-is-an-open-source-ai-agent-that-runs-your-computer/)

| 시점 | 이름 | 사유 |
|------|------|------|
| **2025년 11월** | Clawdbot | 최초 출시 (Peter Steinberger) |
| **2026년 1월 초** | Moltbot | Anthropic 상표 요청으로 개명 |
| **2026년 1월 중순** | AI | 최종 이름 변경 |

| 지표 | 수치 |
|------|------|
| **GitHub Stars** | 145,000+ |
| **GitHub Forks** | 20,000+ |
| **출시 후 기간** | 약 2개월 만에 100K 스타 달성 |
| **모듈 수** | 52+ 모듈 (도구, 플러그인, 확장) |
| **런타임** | 단일 Node.js 프로세스 |
| **권한 모델** | 사용자와 동일한 권한으로 실행 |
| **격리** | 프로세스 수준 격리 없음 |
| **파일 접근** | 전체 파일 시스템 읽기/쓰기 |
| **네트워크** | 제한 없는 아웃바운드 연결 |

Cisco는 AI를 **"치명적 삼중주(Lethal Trifecta)"**라고 표현했습니다 -- 개인 데이터 접근, 신뢰할 수 없는 콘텐츠 노출, 외부 통신 능력이 결합되어, 보안 경계를 의도적으로 무너뜨리는 구조입니다. 보안 비평가 Gary Marcus는 **"디바이스 보안이나 데이터 프라이버시를 중시한다면 AI를 사용하지 마라"**라고 경고했습니다.

> 출처: [Cisco Blogs](https://blogs.cisco.com/ai/personal-ai-agents-like-ai-are-a-security-nightmare), [VentureBeat](https://venturebeat.com/security/ai-agentic-ai-security-risk-ciso-guide)

**보안 위험 요인:**

![AI Architecture - Single process model with 52+ modules running with full user privileges and no isolation](/assets/images/diagrams/2026-02-03-ai-architecture.svg)

#### CVE-2026-25253: AI 원클릭 RCE 취약점

> 출처: [The Hacker News](https://thehackernews.com/2026/02/ai-bug-enables-one-click-remote.html)

AI(구 Clawdbot/Moltbot)에서 **악성 링크 클릭만으로 원격 코드 실행(RCE)이 가능한 고위험도 취약점**이 공개되었습니다.

| 항목 | 내용 |
|------|------|
| **CVE ID** | CVE-2026-25253 |
| **CVSS 점수** | 8.8 (High) |
| **CWE** | CWE-669 (Incorrect Resource Transfer Between Spheres) |
| **취약점 유형** | 토큰 유출(Token Exfiltration) -> RCE |
| **공격 벡터** | 악성 링크 원클릭 (localhost 사용자도 취약) |
| **발견자** | Mav Levin (depthfirst 보안 연구원) |
| **취약 버전** | v2026.1.24-1 이하 전 버전 |
| **패치 버전** | 2026.1.29 (2026년 1월 30일 릴리스) |
| **패치 내용** | Gateway URL 확인 모달 추가 (자동 연결 제거) |

> 출처: [depthfirst](https://depthfirst.com/post/1-click-rce-to-steal-your-moltbot-data-and-keys), [SOCRadar](https://socradar.io/blog/cve-2026-25253-rce-ai-auth-token/)

**공격 메커니즘 상세:**

취약점의 핵심은 URL 파라미터 처리 로직에 있습니다. 패치 전 AI는 쿼리 스트링의 `gatewayUrl` 파라미터를 받아 **사용자 확인 없이 자동으로 WebSocket 연결**을 수립하고, 이 과정에서 인증 토큰을 전송했습니다. 공격자가 조작한 링크를 클릭하면 토큰이 밀리초 단위로 탈취되며, 이후 피해자의 로컬 게이트웨이에 연결하여 샌드박스/도구 정책을 변경하고 권한 있는 작업을 실행할 수 있습니다. **localhost에서 실행 중인 인스턴스도 피해자의 브라우저를 통해 로컬 네트워크로 피벗**할 수 있어 인터넷 노출 여부와 관계없이 취약합니다.

**실무 대응 체크리스트:**

- [ ] AI 버전 2026.1.29 이상으로 즉시 업데이트
- [ ] 조직 내 AI 설치 현황 인벤토리 확인 (섹션 1.8의 Jamf EA 스크립트 활용)
- [ ] 의심스러운 링크 클릭 이력이 있는 경우 토큰 교체
- [ ] SIEM에 CVE-2026-25253 관련 IOC 탐지 룰 추가

#### ClawHub 341개 악성 스킬 공급망 공격

> 출처: [The Hacker News](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html)

Koi Security 연구팀이 ClawHub 마켓플레이스에 대한 보안 감사를 수행한 결과, **2,857개 스킬 중 341개(약 12%)가 악성**임을 확인했습니다. ClawHub는 AI 사용자가 서드파티 스킬을 검색하고 설치할 수 있는 마켓플레이스입니다.

| 항목 | 내용 |
|------|------|
| **감사 대상** | ClawHub 마켓플레이스 2,857개 스킬 |
| **악성 스킬 수** | 341개 (약 12%) |
| **캠페인 코드명** | **ClawHavoc** (Koi Security 명명) |
| **핵심 악성코드** | **Atomic Stealer (AMOS)** - macOS 인포스틸러 |
| **단일 공격자** | "hightower6eu" 계정 - 314개 악성 스킬 게시 |
| **공격 타임라인** | 1차: 28개 (1/27-29), 2차: 386개 (1/31-2/2) |
| **발견 주체** | Koi Security, VirusTotal, Cisco |
| **MITRE ATT&CK** | T1195 (Supply Chain Compromise) |

> 출처: [Koi Security](https://www.koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting), [VirusTotal](https://blog.virustotal.com/2026/02/from-automation-to-infection-how.html), [CyberInsider](https://cyberinsider.com/341-ai-skills-distribute-macos-malware-via-clickfix-instructions/)

**ClawHavoc 캠페인 상세 분석:**

341개 악성 스킬 중 **335개는 단일 캠페인(ClawHavoc)**에서 발생했으며, 가짜 사전 설치 요구사항을 통해 macOS 인포스틸러 **Atomic Stealer(AMOS)**를 설치합니다. 악성 스킬은 고수요 카테고리를 사칭했습니다:

| 사칭 카테고리 | 악성 스킬 수 | 비율 |
|--------------|-------------|------|
| **Crypto 유틸리티** | 111개 | 33% |
| **YouTube 도구** | 57개 | 17% |
| **금융/소셜 트렌드** | 51개 | 15% |
| **예측 시장 봇** | 34개 | 10% |
| **자동 업데이터** | 28개 | 8% |
| **Google Workspace** | 17개 | 5% |

**타이포스쿼팅(Typosquatting)** 기법도 사용되었습니다 -- 공식 ClawHub CLI 이름을 `clawhub`, `clawhub1`, `clawhubb`, `clawhubcli` 등으로 변형하여 오타 입력 시 악성 패키지로 유도했습니다.

Cisco가 별도로 수행한 대규모 분석에서는 **31,000개 에이전트 스킬 중 26%(약 8,060개)가 최소 1개 이상의 취약점**을 포함하고 있음을 확인했습니다. 특히 한 취약한 스킬은 `curl` 명령을 통해 사용자 모르게 외부 서버로 데이터를 탈취하는 코드가 포함되어 있었습니다.

**플랫폼 대응의 한계:** ClawHub 관리자는 통보를 받은 후에도 **"레지스트리를 보안할 수 없다"**고 인정했으며, 대부분의 악성 스킬이 여전히 온라인 상태입니다. 이는 NPM, PyPI 등 기존 패키지 레지스트리의 보안 모델과 유사한 근본적 한계를 드러냅니다.

**공급망 공격 위험 분석:**

이 사건은 AI의 아키텍처적 취약점과 결합될 때 특히 위험합니다. 단일 프로세스 모델에서 악성 스킬이 사용자와 동일한 권한으로 실행되므로, `~/.ssh/`, `~/.aws/`, `~/.env` 등 민감한 자격 증명에 무제한 접근이 가능합니다.

![ClawHub Supply Chain Attack Flow - From malicious skill upload to data exfiltration via AI single process](/assets/images/diagrams/2026-02-03-clawhub-supply-chain-attack.svg)

**MITRE ATT&CK 관련 기법:**

| MITRE ATT&CK ID | 기법명 | AI 에이전트 적용 |
|------------------|--------|------------------|
| **T1059.007** | Command and Scripting Interpreter: JavaScript | Node.js 런타임에서 임의 코드 실행 |
| **T1005** | Data from Local System | 로컬 파일 시스템에서 민감 정보 수집 |
| **T1041** | Exfiltration Over C2 Channel | API 호출을 통한 데이터 유출 |
| **T1078** | Valid Accounts | 사용자 권한을 그대로 상속 |
| **T1195** | Supply Chain Compromise | ClawHub 악성 스킬을 통한 침투 |
| **T1547** | Boot or Logon Autostart Execution | 에이전트 자동 시작 설정 |

#### Moltbook AI 소셜네트워크 자격증명 대량 유출

> 출처: [SiliconANGLE](https://siliconangle.com/2026/02/02/ai-agent-social-network-moltbook-left-millions-credentials-publicly-exposed/), [Fortune](https://fortune.com/2026/01/31/ai-agent-moltbot-clawdbot-ai-data-privacy-security-nightmare-moltbook-social-network/)

**Moltbook**은 기업가 Matt Schlicht가 2026년 1월 런칭한 **AI 에이전트 전용 소셜네트워크**로, 사람은 읽기만 가능하고 AI 에이전트만 읽기/쓰기가 가능한 독특한 플랫폼입니다. 출시 한 달 만에 **77만 이상의 활성 에이전트**를 확보했으나, Wiz Inc.가 심각한 보안 결함을 발견했습니다.

| 항목 | 내용 |
|------|------|
| **플랫폼** | Moltbook (AI 에이전트 전용 소셜네트워크) |
| **활성 에이전트** | 770,000+ |
| **발견 주체** | Wiz Inc. (클라우드 보안 기업) |
| **결함** | 데이터베이스 인증 제어 부재 - 누구나 접근 가능 |
| **유출 데이터** | 수백만 건의 민감 자격증명 |
| **보안 위협** | 간접 프롬프트 인젝션 벡터 (악성 포스트가 에이전트 지시 덮어쓰기) |

Moltbook의 구조적 문제는 **간접 프롬프트 인젝션(Indirect Prompt Injection)**에 취약하다는 점입니다. 에이전트가 다른 에이전트의 비신뢰 데이터를 수집/처리해야 하므로, 악성 포스트가 에이전트의 핵심 지시를 덮어쓸 수 있습니다.

#### 추가 보안 사건: 가짜 VS Code 확장 및 Shodan 노출

> 출처: [The Register](https://www.theregister.com/2026/02/02/ai_security_issues/), [SOCPrime](https://socprime.com/active-threats/the-moltbot-clawdbots-epidemic/)

| 사건 | 상세 | 위험도 |
|------|------|--------|
| **가짜 VS Code 확장** | Clawdbot 이름을 사칭한 VS Code 확장이 **ScreenConnect RAT**(원격 접근 트로이목마) 설치. 개발자의 브랜드 신뢰를 악용 | Critical |
| **Shodan 대규모 노출** | 2026년 1월 25일, 자가 호스팅 AI 인스턴스가 Shodan에 대량 인덱싱. 관리 포트가 인터넷에 노출된 채 운영 | Critical |
| **SecurityAffairs 400+ 악성 패키지** | Moltbot 스킬을 악용해 수일 만에 400개 이상의 악성 패키지 유포 | High |

![AI Moltbot Security Incident Timeline Jan-Feb 2026 - From Shodan exposure to ClawHavoc campaign and CVE patch](/assets/images/diagrams/2026-02-03-security-incident-timeline.svg)

### 1.3 NanoClaw는 어떻게 보안 문제를 해결하는가?

NanoClaw는 보안을 아키텍처 수준에서 해결합니다. AI의 CVE-2026-25253이나 ClawHub 공급망 공격과 같은 위협에 대해 구조적인 방어력을 갖추고 있습니다.

| 항목 | NanoClaw |
|------|----------|
| **핵심 코드** | ~500줄 (감사 가능한 규모) |
| **격리 방식** | Apple 컨테이너 (App Sandbox) |
| **권한 모델** | 최소 권한 원칙 (Principle of Least Privilege) |
| **파일 접근** | 프로젝트 디렉토리만 허용 |
| **네트워크** | 허용 목록 기반 아웃바운드만 |
| **프로세스** | 격리된 샌드박스 프로세스 |
| **서드파티 확장** | 제한적 (공격 표면 최소화) |

**NanoClaw 보안 아키텍처:**

![NanoClaw Architecture - Apple container sandbox with isolated file access and filtered network](/assets/images/diagrams/2026-02-03-nanoclaw-architecture.svg)

### 1.4 AI vs NanoClaw: 어떤 AI 에이전트가 더 안전한가?

| 비교 항목 | AI | NanoClaw |
|-----------|----------|----------|
| **코드 규모** | 52+ 모듈, 수만 줄 | ~500줄 핵심 코드 |
| **감사 용이성** | 어려움 (방대한 코드베이스) | 용이함 (사람이 읽을 수 있는 규모) |
| **격리 수준** | 없음 (사용자 프로세스) | Apple 컨테이너 샌드박스 |
| **파일 접근** | 전체 파일 시스템 | 프로젝트 디렉토리 한정 |
| **네트워크** | 무제한 | 허용 목록 기반 |
| **권한 모델** | 사용자 전체 권한 | 최소 권한 원칙 |
| **공급망 리스크** | 높음 (ClawHub 341개 악성 스킬) | 낮음 (제한된 확장 모델) |
| **프롬프트 인젝션 내성** | 낮음 (넓은 공격 표면) | 높음 (제한된 기능) |
| **기능 범위** | 광범위 (IDE 수준) | 핵심 코딩 지원 |
| **적합 환경** | 개인 개발, 빠른 프로토타이핑 | 엔터프라이즈, 보안 민감 환경 |

### 1.5 OWASP Agentic AI Top 10이란 무엇인가?

AI 에이전트 보안의 표준 프레임워크로 부상한 OWASP Agentic AI Top 10은 이번 주 AI 사건들과 직접 연관됩니다:

| 순위 | 취약점 | AI 해당 여부 | 이번 주 사건 연관성 | 대응 방안 |
|------|--------|-------------------|-------------------|-----------|
| 1 | **Excessive Agency** | Yes - 무제한 권한 | CVE-2026-25253 RCE | 최소 권한 원칙 적용 |
| 2 | **Prompt Injection** | Yes - 넓은 공격 표면 | 악성 스킬 프롬프트 조작 | 입력 검증, 샌드박싱 |
| 3 | **Supply Chain Vulnerabilities** | Yes - 52+ 의존성 | ClawHub 341개 악성 스킬 | SBOM 관리, 의존성 감사 |
| 4 | **Insecure Output Handling** | Partial | - | 출력 검증, 실행 전 확인 |
| 5 | **Data Leakage** | Yes - 전체 FS 접근 | 자격 증명 탈취 | 데이터 접근 범위 제한 |
| 6 | **Lack of Oversight** | Partial | - | 실행 로깅, 승인 워크플로 |
| 7 | **Privilege Escalation** | Yes - 사용자 권한 상속 | 토큰 유출 -> RCE | 권한 분리, 컨테이너화 |
| 8 | **Insufficient Monitoring** | Partial | - | SIEM 연동, 행위 분석 |
| 9 | **Over-Reliance** | Context-dependent | - | 코드 리뷰 프로세스 유지 |
| 10 | **Model Denial of Service** | Low | - | Rate limiting |

### 1.6 AI 에이전트 보안 체크리스트: 어떻게 대비해야 하는가?

> **코드 예시**: 전체 코드는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.
> 
> ```yaml
> # AI Agent Security Checklist...
> ```



### 1.8 Jamf Extension Attribute: AI/Moltbot 설치를 어떻게 탐지하는가?

엔터프라이즈 환경에서 Jamf Pro를 통해 관리 대상 Mac에 AI(Clawdbot) 또는 Moltbot이 무단 설치되어 있는지 자동으로 탐지할 수 있습니다. 이번 주 ClawHub 악성 스킬 사건(341개 탐지)과 CVE-2026-25253 취약점을 고려하면, 조직 내 AI 설치 현황 파악이 **즉시 필요한 조치**입니다. 아래 스크립트를 **Jamf Pro > Settings > Extension Attributes**에 등록하면, 인벤토리 수집 시 각 디바이스의 설치 여부가 자동으로 보고됩니다.

#### Extension Attribute 스크립트

> **코드 예시**: 전체 코드는 [Bash 공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> #!/bin/bash...
> ```



#### Jamf Pro 등록 방법

| 단계 | 설정 |
|------|------|
| **1. EA 생성** | Jamf Pro > Settings > Extension Attributes > New |
| **2. 기본 정보** | Display Name: `AI Detection`, Data Type: `String` |
| **3. Input Type** | `Script` 선택, 위 스크립트 붙여넣기 |
| **4. Inventory Scope** | `Computer` |
| **5. 저장** | Save 후 인벤토리 수집 시 자동 실행 |

#### Smart Group 연동: 설치 탐지 디바이스 자동 그룹화

![Jamf Pro Smart Group - AI installed devices detection with automated alert and restriction actions](/assets/images/diagrams/2026-02-03-jamf-smart-group.svg)

탐지 시 자동으로 다음 조치를 취할 수 있습니다:

| 자동 대응 | 방법 |
|-----------|------|
| **알림** | Smart Group 변경 시 Slack/Teams 웹훅 발송 |
| **제한** | Restriction Profile 자동 배포 (네트워크 접근 차단) |
| **제거** | Self Service에서 제거 스크립트 제공 또는 정책 자동 실행 |
| **로깅** | SIEM 연동으로 설치 이력 추적 |

#### 확장: 추가 AI 에이전트 탐지

동일 패턴으로 다른 AI 코딩 에이전트도 탐지할 수 있습니다:

> **코드 예시**: 전체 코드는 [Bash 공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # Additional AI agent binary paths to monitor...
> ```



#### 탐지 결과 SIEM 연동

> **코드 예시**: 전체 코드는 [Bash 공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # Splunk - Jamf EA 기반 AI 설치 탐지 알림...
> ```



### 1.9 AI 에이전트 보안 FAQ

**Q1: AI를 사용 중인데 당장 무엇을 해야 하나요?**

즉시 버전 2026.1.29 이상으로 업데이트하여 CVE-2026-25253을 패치하세요. 설치된 ClawHub 스킬 목록을 점검하고, 출처가 불분명한 스킬은 제거하세요. `~/.ssh/`, `~/.aws/` 등 민감 디렉토리의 접근 로그를 확인하여 이상 징후가 없는지 점검하는 것이 권장됩니다.

**Q2: ClawHub 스킬의 악성 여부를 어떻게 판별하나요?**

Koi Security 연구팀의 보고서에 따르면, 악성 스킬은 주로 자격 증명 수집과 데이터 탈취를 시도합니다. 스킬의 소스 코드에서 `~/.ssh`, `~/.aws`, `~/.env`, `process.env` 등의 문자열 접근 패턴을 확인하세요. 스킬 설치 전 코드 리뷰를 의무화하고, 검증된 퍼블리셔의 스킬만 사용하는 정책을 수립하는 것이 좋습니다.

**Q3: NanoClaw로 전환하면 기존 워크플로에 영향이 있나요?**

NanoClaw는 핵심 코딩 지원에 집중하므로 AI의 52개 이상 모듈 중 상당수는 지원하지 않습니다. IDE 수준의 광범위한 기능이 필요하면 AI를 보안 설정과 함께 사용하되, 보안 민감 환경(금융, 의료, 정부)에서는 NanoClaw의 샌드박스 모델이 더 적합합니다.

**Q4: OWASP Agentic AI Top 10을 조직에 어떻게 적용하나요?**

먼저 현재 사용 중인 AI 에이전트의 권한과 접근 범위를 매핑하세요. Top 10 항목별로 해당 여부를 평가하고, 우선순위가 높은 항목(Excessive Agency, Supply Chain Vulnerabilities)부터 대응하세요. 분기별 AI 에이전트 보안 감사를 도입하고, 결과를 경영진에게 보고하는 체계를 수립하는 것을 권장합니다.

---

## 2. MDM 앱 비활성화: 어떤 MDM을 선택해야 하는가?

### 2.1 AI 에이전트 시대에 MDM 앱 제어가 왜 중요한가?

섹션 1에서 살펴본 바와 같이, AI의 CVE-2026-25253 취약점과 ClawHub 악성 스킬 사건은 **AI 에이전트의 무단 설치가 곧 보안 사고의 시작점**이 될 수 있음을 보여줍니다. 엔터프라이즈 환경에서 MDM을 통한 앱 제어는 더 이상 선택이 아닌 Zero Trust 전략의 핵심 필수 요소입니다.

특히 AI 코딩 에이전트는 기존의 일반 앱과 달리 **파일 시스템, 네트워크, 셸 실행 권한**을 모두 요구하므로, 무단 설치 시 공격자에게 개발 환경 전체의 접근 권한을 제공하는 것과 같습니다. MDM의 앱 제한 프로파일과 컴플라이언스 정책을 통해 승인된 도구만 사용할 수 있도록 제어해야 합니다.

| 시나리오 | MDM 앱 제어 대응 |
|----------|-----------------|
| **AI 에이전트 무단 설치 방지** | 비인가 AI 도구 차단 목록 (AI, 미검증 스킬) |
| 퇴사 예정자 데이터 유출 방지 | 클라우드 스토리지 앱 비활성화 |
| 규정 미준수 디바이스 격리 | 업무 앱 접근 차단 |
| 보안 사고 시 긴급 대응 | 원격 앱 잠금/삭제 |
| BYOD 업무/개인 앱 분리 | 관리 컨테이너 내 앱만 허용 |
| 임시직원 앱 제한 | 시간 기반 앱 정책 배포 |

### 2.2 어떤 MDM을 선택해야 하는가? 의사결정 가이드

조직의 환경에 따라 최적의 MDM 솔루션이 달라집니다. 아래 플로차트를 참고하세요:

![MDM Selection Decision Flowchart - Choose between Jamf Pro, Intune, or Hybrid based on device mix and platform needs](/assets/images/diagrams/2026-02-03-mdm-selection-flowchart.svg)

### 2.3 Jamf Pro: Apple 기기 MDM은 어떻게 설정하는가?

Jamf Pro는 Apple 생태계에 최적화된 MDM으로, Configuration Profile을 통해 세밀한 앱 제어가 가능합니다.

#### Configuration Profile로 앱 제한



### 2.4 Microsoft Intune: 크로스 플랫폼 MDM은 어떻게 구성하는가?

Intune은 Windows, macOS, iOS, Android를 통합 관리합니다.

#### App Protection Policies

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



#### Conditional Access로 앱 접근 제어

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



#### Intune Compliance Policy

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



### 2.5 Jamf Pro vs Microsoft Intune: 주요 기능은 어떻게 다른가?

| 비교 항목 | Jamf Pro | Microsoft Intune |
|-----------|----------|------------------|
| **지원 플랫폼** | Apple 전용 (macOS, iOS, iPadOS, tvOS) | Windows, macOS, iOS, Android, Linux |
| **앱 차단 방식** | Configuration Profile (blacklist/whitelist) | App Protection Policy + Compliance |
| **앱 제거** | MDM 명령어로 관리형 앱 즉시 제거 | Selective Wipe / App Uninstall |
| **Conditional Access** | Jamf Connect + Azure AD 연동 | 네이티브 Azure AD Conditional Access |
| **BYOD 지원** | User Enrollment (제한적 관리) | MAM without enrollment (앱 수준 관리) |
| **자동화** | Jamf API + Smart Groups | Graph API + Power Automate |
| **가격** | 디바이스당 과금 | Microsoft 365 E3/E5 포함 |
| **설정 복잡도** | 낮음 (Apple 친화적 UI) | 중간 (다중 플랫폼 고려) |
| **Apple DEP/ABM** | 네이티브 지원 (최적) | 지원 (Jamf 대비 제한적) |
| **Windows 관리** | 미지원 | 네이티브 (GPO 대체) |
| **AI 에이전트 제어** | EA 스크립트 + 프로파일 (섹션 1.8) | Compliance Policy + App Block |
| **적합 환경** | Apple 중심 기업, 크리에이티브 | 혼합 플랫폼, Microsoft 365 환경 |

### 2.6 SIEM 연동 MDM 모니터링은 어떻게 설정하는가?

> **코드 예시**: 전체 코드는 [Bash 공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # Splunk - Jamf Pro MDM Compliance Events...
> ```



### 2.7 MDM Zero Trust 구현 체크리스트

> **코드 예시**: 전체 코드는 [공식 문서](https://kubernetes.io/docs/home/)를 참조하세요.
> 
> ```yaml
> # MDM Zero Trust Checklist...
> ```



### 이번 주 핵심 질문: 보안 팀이 스스로 물어야 할 것

조직의 보안 상태를 점검하기 위해 이번 주 다음 질문에 답할 수 있어야 합니다:

1. **우리 조직에 AI가 설치된 디바이스가 몇 대인가?** CVE-2026-25253 패치가 적용되었는가?
2. **승인되지 않은 AI 코딩 에이전트의 설치를 탐지하는 메커니즘이 있는가?** (Jamf EA, EDR 룰 등)
3. **서드파티 AI 스킬/플러그인의 설치 승인 프로세스가 있는가?** ClawHub와 같은 마켓플레이스에서 설치된 스킬을 추적하고 있는가?
4. **NTLM 인증을 사용하는 시스템 목록이 있는가?** Microsoft 폐지 계획에 따른 마이그레이션 일정이 수립되어 있는가?
5. **소프트웨어 공급망의 무결성을 어떻게 검증하고 있는가?** SBOM이 생성/관리되고 있으며 SLSA 레벨은 어느 단계인가?

---

## 참고 자료

### AI 에이전트 보안

| 제목 | URL |
|------|-----|
| OWASP Agentic AI Top 10 | [OWASP](https://owasp.org/www-project-top-10-for-large-language-model-applications/) |
| NanoClaw - Minimal AI Agent | [GitHub](https://github.com/anthropics/anthropic-cookbook) |
| Claude Code Security Model | [Anthropic Docs](https://docs.anthropic.com/en/docs/claude-code/security) |
| ClawHub 341 Malicious Skills (The Hacker News) | [The Hacker News](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html) |
| AI CVE-2026-25253 RCE Bug (The Hacker News) | [The Hacker News](https://thehackernews.com/2026/02/ai-bug-enables-one-click-remote.html) |
| Microsoft NTLM Phase-Out Plan (The Hacker News) | [The Hacker News](https://thehackernews.com/2026/02/microsoft-begins-ntlm-phase-out-with.html) |
| CVE-2026-25253 1-Click RCE (depthfirst) | [depthfirst](https://depthfirst.com/post/1-click-rce-to-steal-your-moltbot-data-and-keys) |
| CVE-2026-25253 상세 분석 (SOCRadar) | [SOCRadar](https://socradar.io/blog/cve-2026-25253-rce-ai-auth-token/) |
| ClawHavoc: 341 Malicious Skills (Koi Security) | [Koi Security](https://www.koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting) |
| AI Skills Weaponized (VirusTotal) | [VirusTotal Blog](https://blog.virustotal.com/2026/02/from-automation-to-infection-how.html) |
| AI Security Nightmare (Cisco) | [Cisco Blogs](https://blogs.cisco.com/ai/personal-ai-agents-like-ai-are-a-security-nightmare) |
| AI Agentic AI CISO Guide (VentureBeat) | [VentureBeat](https://venturebeat.com/security/ai-agentic-ai-security-risk-ciso-guide) |
| AI Security Issues (The Register) | [The Register](https://www.theregister.com/2026/02/02/ai_security_issues/) |
| Clawdbot to AI (Vectra AI) | [Vectra AI](https://www.vectra.ai/blog/clawdbot-to-moltbot-to-ai-when-automation-becomes-a-digital-backdoor) |
| AI Sovereign Security Manifest (Penligent) | [Penligent AI](https://www.penligent.ai/hackinglabs/ai-sovereign-ai-security-manifest-a-comprehensive-post-mortem-and-architectural-hardening-guide-for-ai-ai-2026/) |
| Clawdbot to AI (CNBC) | [CNBC](https://www.cnbc.com/2026/02/02/ai-open-source-ai-agent-rise-controversy-clawdbot-moltbot-moltbook.html) |
| Moltbook Credential Exposure (SiliconANGLE) | [SiliconANGLE](https://siliconangle.com/2026/02/02/ai-agent-social-network-moltbook-left-millions-credentials-publicly-exposed/) |
| Moltbook AI Social Network (Fortune) | [Fortune](https://fortune.com/2026/01/31/ai-agent-moltbot-clawdbot-ai-data-privacy-security-nightmare-moltbook-social-network/) |
| Moltbot Skills 400+ Malware (SecurityAffairs) | [SecurityAffairs](https://securityaffairs.com/187562/malware/moltbot-skills-exploited-to-distribute-400-malware-packages-in-days.html) |
| AI Use Cases & Security (AIMultiple) | [AIMultiple](https://research.aimultiple.com/moltbot/) |

### AI 및 클라우드

| 제목 | URL |
|------|-----|
| Snowflake-OpenAI Partnership ($200M) | [OpenAI Blog](https://openai.com/index/snowflake-partnership) |
| Google AI: Preserving Endangered Species | [Google AI Blog](https://blog.google/innovation-and-ai/technology/ai/ai-to-preserve-endangered-species/) |
| Clarus Care Amazon Bedrock Clinical AI | [AWS ML Blog](https://aws.amazon.com/blogs/machine-learning/how-clarus-care-uses-amazon-bedrock-to-deliver-conversational-contact-center-interactions/) |
| Gemini Enterprise Employee Onboarding | [Google Cloud Blog](https://cloud.google.com/blog/topics/developers-practitioners/how-to-build-onboarding-agents-with-gemini-enterprise/) |

### MDM 관리

| 제목 | URL |
|------|-----|
| Jamf Pro Administrator Guide | [Jamf](https://learn.jamf.com/en-US/bundle/jamf-pro-documentation-current/page/About_Jamf_Pro.html) |
| Microsoft Intune App Protection Policies | [Microsoft](https://learn.microsoft.com/en-us/mem/intune/apps/app-protection-policy) |
| Intune Conditional Access | [Microsoft](https://learn.microsoft.com/en-us/mem/intune/protect/conditional-access) |
| Apple MDM Protocol Reference | [Apple](https://developer.apple.com/documentation/devicemanagement) |

### 보안 프레임워크

| 리소스 | URL |
|--------|-----|
| MITRE ATT&CK Framework | [attack.mitre.org](https://attack.mitre.org/) |
| NIST Zero Trust Architecture (SP 800-207) | [NIST](https://csrc.nist.gov/publications/detail/sp/800-207/final) |
| SLSA Framework | [slsa.dev](https://slsa.dev/) |
| CIS Benchmarks | [CIS](https://www.cisecurity.org/cis-benchmarks) |

### 지난주 다이제스트

| 제목 | URL |
|------|-----|
| Weekly Security Threat Intelligence Digest (Feb 2) | [Twodragon Blog](/2026-02-02-Weekly_Security_Threat_Intelligence_Digest) |
| Weekly Tech & AI & Blockchain Digest (Feb 2) | [Twodragon Blog](/2026-02-02-Weekly_Tech_AI_Blockchain_Digest) |

---

*이 글은 [Twodragon's Tech Blog](https://tech.2twodragon.com)에서 매주 발행하는 Security & DevOps Digest입니다. 최신 보안 뉴스와 실무 가이드를 매주 받아보세요.*

<!-- quality-upgrade:v1 -->
## 경영진 요약 (Executive Summary)
이 문서는 운영자가 즉시 실행할 수 있는 보안 우선 실행 항목과 검증 포인트를 중심으로 재정리했습니다.

### 위험 스코어카드
| 영역 | 현재 위험도 | 영향도 | 우선순위 |
|---|---|---|---|
| 공급망/의존성 | 중간 | 높음 | P1 |
| 구성 오류/권한 | 중간 | 높음 | P1 |
| 탐지/가시성 공백 | 낮음 | 중간 | P2 |

### 운영 개선 지표
| 지표 | 현재 기준 | 목표 | 검증 방법 |
|---|---|---|---|
| 탐지 리드타임 | 주 단위 | 일 단위 | SIEM 알림 추적 |
| 패치 적용 주기 | 월 단위 | 주 단위 | 변경 티켓 감사 |
| 재발 방지율 | 부분 대응 | 표준화 | 회고 액션 추적 |

### 실행 체크리스트
- [ ] 핵심 경고 룰을 P1/P2로 구분하고 온콜 라우팅을 검증한다.
- [ ] 취약점 조치 SLA를 서비스 등급별로 재정의한다.
- [ ] IAM/시크릿/네트워크 변경 이력을 주간 기준으로 리뷰한다.
- [ ] 탐지 공백 시나리오(로그 누락, 파이프라인 실패)를 월 1회 리허설한다.
- [ ] 경영진 보고용 핵심 지표(위험도, 비용, MTTR)를 월간 대시보드로 고정한다.

### 시각 자료
![포스트 시각 자료](/assets/images/2026-02-03-Weekly_Security_DevOps_Digest.svg)

<!-- priority-quality-korean:v1 -->
## 우선순위 기반 고도화 메모
| 구분 | 현재 상태 | 목표 상태 | 우선순위 |
|---|---|---|---|
| 콘텐츠 밀도 | 점수 82 수준 | 실무 의사결정 중심 문장 강화 | P2 (단기 보강) |
| 표/시각 자료 | 핵심 표 중심 | 비교/의사결정 표 추가 | P2 |
| 실행 항목 | 체크리스트 중심 | 역할/기한/증적 기준 명시 | P1 |

### 이번 라운드 개선 포인트
- 핵심 위협과 비즈니스 영향의 연결 문장을 강화해 의사결정 맥락을 명확히 했습니다.
- 운영팀이 바로 실행할 수 있도록 우선순위(P0/P1/P2)와 검증 포인트를 정리했습니다.
- 후속 업데이트 시에는 실제 지표(MTTR, 패치 리드타임, 재발률)를 반영해 정량성을 높입니다.

