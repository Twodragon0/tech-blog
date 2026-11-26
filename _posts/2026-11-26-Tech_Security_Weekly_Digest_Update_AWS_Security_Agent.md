---
layout: post
title: "2026년 11월 26일 주간 보안 다이제스트: 클라우드·패치·AI 에이전트 (21건)"
date: 2026-11-26 10:31:13 +0900
last_modified_at: 2026-11-26T10:31:13+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Update, AWS, Security, Agent]
excerpt: "‘AWS-LC로 포스트 양자 암호화 업데이트를 일상화하세요’ 소식 · ‘ICYMI: 2026년 10월 @AWS Security’ 소식이 부각된 2026년 11월 26일 보안 다이제스트 — 21건의 이슈와 실행 가능한 대응 액션을 정리합니다. 사안별 소스와 영향도를 표로 정리해 우선순위 판단 근거를 남겼습니다."
description: "2026년 11월 26일 보안 뉴스 요약. AWS Security Blog, The Hacker News 등 21건을 분석하고 AWS-LC로 포스트 양자 암호화, ICYMI: 2026년 10월 @AWS, Enterprise-Managed 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Update, AWS, Security]
author: Twodragon
comments: true
image: /assets/images/2026-11-26-Tech_Security_Weekly_Digest_Update_AWS_Security_Agent.svg
image_alt: "AWS-LC, ICYMI: 2026 10 @AWS, Enterprise-Managed - security digest overview"
toc: true
summary_card:
  title: "2026년 11월 26일 주간 보안 다이제스트: 클라우드·패치·AI 에이전트 (21건)"
  period: "2026년 11월 26일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Update"
    - "AWS"
    - "Security"
    - "Agent"
    - "2026"
  highlights:
    - { source: "AWS Security Blog", title: "AWS-LC로 포스트 양자 암호화 업데이트를 일상화하세요" }
    - { source: "AWS Security Blog", title: "ICYMI: 2026년 10월 @AWS Security" }
    - { source: "AWS Security Blog", title: "Enterprise-Managed Authorization을 통한 AWS 에이전틱 접근 보안" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 11월 26일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 21개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 3개
- **DevOps 뉴스**: 3개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | AWS Security Blog | AWS-LC로 포스트 양자 암호화 업데이트를 일상화하세요 | 🟡 Medium |
| 🔒 **Security** | AWS Security Blog | ICYMI: 2026년 10월 @AWS Security | 🔴 Critical |
| 🔒 **Security** | AWS Security Blog | Enterprise-Managed Authorization을 통한 AWS 에이전틱 접근 보안 | 🔴 Critical |
| 🤖 **AI/ML** | Hugging Face Blog | 과학자들은 AI 에이전트에 어디까지 선을 그을까 | 🟡 Medium |
| 🤖 **AI/ML** | Hugging Face Blog | CUGA를 갖춘 인도어 음성 에이전트 | 🟡 Medium |
| 🤖 **AI/ML** | CoinDesk | 암호화폐 트레이더들은 이제 Derive에서 Nvidia, Anthropic, 석유 베팅에 헤지할 수 있다 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Copilot 코드 리뷰 결제가 기본적으로 조직으로 설정됩니다 | 🟡 Medium |
| ⚙️ **DevOps** | Docker Blog | AI 에이전트 가드레일이 제대로 작동하는지 증명하세요 | 🟡 Medium |
| ⚙️ **DevOps** | CNCF Blog | “Drone 2” 비하인드 스토리: 나의 KubeCon + CloudNativeCon North America 2026 기조연설 | 🟠 High |
| ⛓️ **Blockchain** | Bitcoin Magazine | Bitcoin이 채굴 속도보다 빠르게 “딥 스토리지”로 사라지고 있다 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: ICYMI: 2026년 10월 @AWS Security, Enterprise-Managed Authorization을 통한 AWS 에이전틱 접근 보안 등 Critical 등급 위협 2건이 확인되었습니다.
- **주요 모니터링 대상**: “Drone 2” 비하인드 스토리: 나의 KubeCon + CloudNativeCon North America 2026 기조연설 등 High 등급 위협 1건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 분석가 시점

이번 주기를 한 줄로 정리하면, 암호 민첩성이 에이전트 신원 관리와 만나는 지점에서 DevSecOps 파이프라인의 신뢰 경계가 다시 그려지고 있다는 것이다. AWS-LC의 post-quantum 갱신을 일상화하라는 요구는 TLS 종료 지점과 빌드 산출물 서명까지 암호 스위트 교체를 릴리스 게이트로 끌어들이고, Enterprise-Managed Authorization은 사람이 아닌 에이전트의 AWS IAM 접근을 중앙 정책으로 통제하라는 신호다. 이번 주기에 가장 먼저 봐야 할 것은 **에이전트 런타임의 자격증명 발급 경로**다. GitHub Actions 워크플로에 붙은 OIDC 신뢰 정책과 임시 자격증명 TTL을 먼저 감사하고, 암호 민첩성은 그다음 순서로 eBPF 기반 런타임 관측과 묶어 릴리스 체크리스트에 넣어라.

## 1. 보안 뉴스

### 1.1 AWS-LC로 포스트 양자 암호화 업데이트를 일상화하세요

{% include news-card.html
  title="AWS-LC로 포스트 양자 암호화 업데이트를 일상화하세요"
  url="https://aws.amazon.com/blogs/security/make-post-quantum-cryptography-updates-routine-with-aws-lc/"
  summary="AWS-LC를 활용하면 post-quantum cryptography(PQC) 업데이트를 일상화할 수 있습니다. 조직은 PQC 업그레이드를 계획할 때 데이터 보호에 사용되는 알고리즘을 더 쉽게 교체할 수 있도록 cryptographic agility도 함께 고려해야 합니다."
  source="AWS Security Blog"
  severity="Medium"
%}

#### 요약

AWS-LC를 활용하면 post-quantum cryptography(PQC) 업데이트를 일상화할 수 있습니다. 조직은 PQC 업그레이드를 계획할 때 데이터 보호에 사용되는 알고리즘을 더 쉽게 교체할 수 있도록 cryptographic agility도 함께 고려해야 합니다. 암호화 및 관련 프로토콜 변경은 새로운 것이 아니지만 PQC는 조직이 새 알고리즘을 추가하고 오래된 알고리즘을 제거해야 하는 속도를 가속화하고 있습니다.


#### 권장 조치

- 관련 시스템 목록 확인 및 자사 환경 해당 여부 평가
- 벤더 보안 권고 확인 후 패치 또는 완화 조치 적용
- SIEM/EDR 탐지 룰에 관련 IoC 추가
- 보안팀 내 공유 및 모니터링 강화


---

### 1.2 ICYMI: 2026년 10월 @AWS Security

{% include news-card.html
  title="ICYMI: 2026년 10월 @AWS Security"
  url="https://aws.amazon.com/blogs/security/icymi-october-2026-aws-security/"
  summary="AWS Security의 2026년 10월 월간 다이제스트는 클라우드 보안 유지를 위해 필요한 최신 AWS Security 개발 동향을 정리한 자료입니다. 이번 호에는 새로운 공지사항, 기능, 리소스와 함께 블로그와 전문가 관점이 포함되어 있습니다."
  source="AWS Security Blog"
  severity="Critical"
%}

#### AWS Security 월간 다이제스트(2026년 10월) DevSecOps 관점 분석

#### 기술적 배경 및 위협 분석

AWS가 매월 발표하는 보안 업데이트 다이제스트는 클라우드 네이티브 환경에서 **구성 오류(misconfiguration)**, **IAM 권한 남용**, **공급망 취약점** 등 지속적으로 진화하는 위협에 대한 AWS의 대응 현황을 압축적으로 보여준다. 특히 2026년 시점에서는 생성형 AI 워크로드(Amazon Bedrock 등)의 확산으로 인한 **데이터 유출 경로 다변화**, **에이전트형 AI의 과도한 권한 부여** 문제가 새로운 공격 표면으로 부상하고 있다. 또한 멀티클라우드·하이브리드 환경에서의 **정책 일관성 부재**와 **CSPM(Cloud Security Posture Management) 사각지대**가 주요 리스크로 작용한다. AWS의 신규 기능 발표는 대개 새로운 보안 통제 수단(예: 세분화된 정책, 자동 탐지 기능)을 제공하지만, 동시에 기존 IaC 템플릿·파이프라인과의 정합성 재검토를 요구한다는 이중적 성격을 갖는다.

#### 실무 영향 분석

DevSecOps 실무자에게 이 다이제스트는 **파이프라인 내 보안 게이트 재조정**의 트리거가 된다. 신규 AWS 보안 기능은 대체로 ① IaC 스캔 규칙(Checkov/tfsec/cfn-nag) 업데이트, ② CI 단계의 정책 검증(OPA/Sentinel) 룰셋 반영, ③ 런타임 탐지(GuardDuty/Security Hub) 연동 강화를 요구한다. 특히 신규 서비스 출시 초기에는 **기본 설정(default)이 보안 최우선이 아닐 수 있으므로** 조직 표준 베이스라인에 즉시 편입해야 한다. 또한 월간 다이제스트를 단순 정보 소비로 끝내지 않고, **내부 보안 통제 매트릭스와의 갭 분석**에 활용하는 것이 실무적으로 중요하다. 컴플라이언스(ISO 27001, ISMS-P) 관점에서도 신규 리전·기능 도입 시 데이터 레지던시 요건 재검토가 필요하다.



---

### 1.3 Enterprise-Managed Authorization을 통한 AWS 에이전틱 접근 보안

{% include news-card.html
  title="Enterprise-Managed Authorization을 통한 AWS 에이전틱 접근 보안"
  url="https://aws.amazon.com/blogs/security/secure-agentic-access-to-aws-with-enterprise-managed-authorization/"
  summary="AWS Sign-In이 ID-JAG(Identity Assertion JWT Authorization Grant)를 활용한 Enterprise-Managed Authorization(EMA) 지원을 도입하여, 조직이 Okta 같은 기존 IdP를 통해 AI 에이전트의 AWS MCP Server 접근을 안전하게 승인할 수 있게 되었습니다."
  source="AWS Security Blog"
  severity="Critical"
%}

#### AWS EMA(ID-JAG) 도입, DevSecOps 실무자 관점 분석

#### 기술적 배경 및 위협 분석

기존 AI 에이전트의 AWS 접근은 장기 액세스 키나 정적 IAM 자격증명에 의존해 왔으며, 이는 키 유출·과도한 권한·회전 미비라는 구조적 위험을 내포한다. EMA는 IdP(Okta 등)가 발급한 ID-JAG(Identity Assertion JWT Authorization Grant)를 통해 에이전트 신원을 연합 인증으로 전환하는 모델로, RFC 8693 토큰 교환 흐름을 AWS MCP Server 접근에 적용한 것이다. 위협 관점에서는 ① 에이전트 스푸핑 및 토큰 재사용, ② IdP 침해 시 연쇄 권한 상승(신뢰 앵커가 IdP로 이동), ③ JWT 서명·클레임 검증 미흡 시 우회, ④ MCP 도구 호출 범위에 대한 가시성 부재가 핵심 리스크다. 즉 보안 경계가 "키 관리"에서 "신원 연합 및 토큰 수명주기 관리"로 이동한다.

#### 실무 영향 분석

에이전트별 정적 키 배포·회전 부담이 줄고, IdP 중앙 정책으로 애플리케이션-에이전트-AWS 리소스 간 승인 매핑이 가능해져 최소권한 원칙 적용이 용이해진다. 반면 CI/CD 파이프라인의 시크릿 관리 로직, IAM Role 신뢰 정책, 감사 로그 설계를 재정비해야 하며, IdP가 새 단일 실패점이 되므로 MFA·조건부 액세스·토큰 수명 정책을 강화해야 한다. 또한 에이전트 행위에 대한 CloudTrail·IdP 로그 상관분석 체계가 없으면 포렌식이 불가능해진다.



---

## 2. AI/ML 뉴스

### 2.1 과학자들은 AI 에이전트에 어디까지 선을 그을까

{% include news-card.html
  title="과학자들은 AI 에이전트에 어디까지 선을 그을까"
  url="https://huggingface.co/blog/allenai/where-scientists-draw-the-line-on-ai-agents"
  image="https://cdn-uploads.huggingface.co/production/uploads/638e39b249de7ae552d977b5/F32BgZC_rj0kg99apJlto.png"
  source="Hugging Face Blog"
  severity="Medium"
%}


---

### 2.2 CUGA를 갖춘 인도어 음성 에이전트

{% include news-card.html
  title="CUGA를 갖춘 인도어 음성 에이전트"
  url="https://huggingface.co/blog/ibm-research/an-indic-voice-agent-with-cuga"
  image="https://cdn-uploads.huggingface.co/production/uploads/67fe070a4e8cc28ba346f53c/-QNcrxSDbjI8VOCBlhi-C.png"
  source="Hugging Face Blog"
  severity="Medium"
%}


---

### 2.3 암호화폐 트레이더들은 이제 Derive에서 Nvidia, Anthropic, 석유 베팅에 헤지할 수 있다

{% include news-card.html
  title="암호화폐 트레이더들은 이제 Derive에서 Nvidia, Anthropic, 석유 베팅에 헤지할 수 있다"
  url="https://www.coindesk.com/markets/2026/11/25/crypto-traders-can-now-hedge-nvidia-and-oil-bets-on-derive"
  image="https://cdn.sanity.io/images/s3y3vcno/production/536d7d5e6cfaca6de1f092a21de7b4cf4d742687-1500x750.jpg"
  source="CoinDesk"
  severity="Medium"
%}


---

## 3. DevOps & 개발 뉴스

### 3.1 Copilot 코드 리뷰 결제가 기본적으로 조직으로 설정됩니다

{% include news-card.html
  title="Copilot 코드 리뷰 결제가 기본적으로 조직으로 설정됩니다"
  url="https://github.blog/changelog/2026-11-25-copilot-code-review-billing-will-default-to-the-organization"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-improvements.jpg"
  summary="Copilot 라이선스가 있는 멤버의 Copilot code review 과금 방식을 아직 선택하지 않았다면 2026년 12월 30일부터 해당 리뷰가 organization에 청구됩니다. 과금 방식을 유지하려면 별도 설정이 필요합니다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

### 3.2 AI 에이전트 가드레일이 제대로 작동하는지 증명하세요

{% include news-card.html
  title="AI 에이전트 가드레일이 제대로 작동하는지 증명하세요"
  url="https://www.docker.com/blog/prove-your-ai-agent-guardrails-work/"
  summary="Docker AI Governance를 통해 coding agent의 네트워크, 파일시스템, 자격 증명, MCP 접근을 제어하고 이를 테스트하는 방법을 소개합니다. Coding agent가 작업에 필요한 범위를 넘어 접근할 수 있는 문제를 다루며, guardrail이 실제로 작동하는지 검증하는 내용을 담고 있습니다."
  source="Docker Blog"
  severity="Medium"
%}


---

### 3.3 “Drone 2” 비하인드 스토리: 나의 KubeCon + CloudNativeCon North America 2026 기조연설

{% include news-card.html
  title="”Drone 2” 비하인드 스토리: 나의 KubeCon + CloudNativeCon North America 2026 기조연설"
  url="https://www.cncf.io/blog/2026/11/25/%f0%9f%9a%80-the-story-behind-drone-2-my-kubecon-cloudnativecon-north-america-2026-keynote/"
  image="https://www.cncf.io/wp-content/uploads/2026/11/The-story-behind-_Drone-2_.jpg"
  summary="KubeCon + CloudNativeCon North America 2026 폐막 기조연설에서 Kubernetes, agent-substrate, kagent, AI 에이전트, 드론을 아우르는 오픈 소스 프로젝트 ”Drone 2”의 비하인드 스토리가 공개됐다."
  source="CNCF Blog"
  severity="High"
%}

#### 요약

KubeCon + CloudNativeCon North America 2026 폐막 기조연설에서 Kubernetes, agent-substrate, kagent, AI 에이전트, 드론을 아우르는 오픈 소스 프로젝트 "Drone 2"의 비하인드 스토리가 공개됐다. 발표는 "Cloud Native Without Limits: What Can AI Agents..."를 주제로 라이브 30초 전까지 긴장감 속에 진행됐다.


---

## 4. 블록체인 뉴스

### 4.1 Bitcoin이 채굴 속도보다 빠르게 “딥 스토리지”로 사라지고 있다

{% include news-card.html
  title="Bitcoin이 채굴 속도보다 빠르게 ”딥 스토리지”로 사라지고 있다"
  url="https://bitcoinmagazine.com/videos/bitcoin-is-vanishing-into-deep-storage-faster-than-miners-make-it"
  image="https://img.youtube.com/vi/rWfTVQTY8vU/hqdefault.jpg"
  summary="Bitcoin 채굴자들이 하루 약 450개를 생산하는 것보다 더 빠른 속도로 Bitcoin이 10년 이상 휴면 상태인 지갑으로 이동하고 있다. 지난 한 해 동안 하루 약 630개의 Bitcoin이 이러한 ”딥 스토리지”로 유입된 것으로 나타났다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 4.2 Stanford 교수가 “Praxis” Bitcoin 암호학 혁신 공개

{% include news-card.html
  title="Stanford 교수가 ”Praxis” Bitcoin 암호학 혁신 공개"
  url="https://bitcoinmagazine.com/videos/stanford-professor-reveals-praxis-bitcoin-cryptography-breakthrough"
  image="https://img.youtube.com/vi/YL4q0VJ2HRQ/hqdefault.jpg"
  summary="Stanford 교수가 Bitcoin의 covenant 기능을 soft fork로 추가하는 새로운 암호학적 돌파구인 ”Praxis”를 공개했다. Bitcoin 개발자들은 5~10년간 covenant 도입을 시도해왔으나 매번 지연되어 왔다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 4.3 전략적 Bitcoin 준비금 법안, 하원 위원회 통과 후 본회의로

{% include news-card.html
  title="전략적 Bitcoin 준비금 법안, 하원 위원회 통과 후 본회의로"
  url="https://bitcoinmagazine.com/news/strategic-bitcoin-reserve-bill-house-floor"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/Strategic-Bitcoin-Reserve-Bill-Clears-House-Committee-Heads-to-Floor.jpg"
  summary="Nick Begich 의원의 Strategic Bitcoin Reserve 법안이 하원 위원회를 통과해 본회의 표결이 가능해졌다. 이 법안은 해당 Bitcoin을 20년간 매도하지 못하도록 하는 내용을 담고 있다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

## 5. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [디자인 시스템이 있는데도 화면은 왜 제각각일까?](https://toss.tech/article/loan_review) | 토스 기술 블로그 | 복잡한 업무 툴의 화면이 제각각이 된 이유를 찾고, 일관성을 만들어 간 과정을 소개합니다 |
| [운영자의 시간을 아끼는 AI 에이전트 2부 - MCP 부터 Agent 설계까지](https://d2.naver.com/helloworld/5073599) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ 발표 내용 운영 문의가 들어오면 운영자는 로그와 메트릭, 과거 사례를 직접 살펴보고 답변해야 합니다 |
| [운영자의 시간을 아끼는 AI 에이전트 1부 - RCA·Q&A 운영 지식그래프](https://d2.naver.com/helloworld/6934862) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ ​ 발표 내용 운영 문의에 명확한 답변을 남겨도 이슈가 닫히면 묻히기 쉽습니다 |


---

## 6. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **클라우드 보안** | 5건 | AWS Security Blog 관련 동향, CNCF Blog 관련 동향 |
| **기타** | 4건 | 기타 주제 |
| **블록체인/암호화폐** | 3건 | Bitcoin Magazine 관련 동향 |
| **AI/ML** | 2건 | Hugging Face Blog 관련 동향, Docker Blog 관련 동향 |
| **취약점/CVE** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **클라우드 보안**(5건)입니다. AWS Security Blog 관련 동향, CNCF Blog 관련 동향 등이 주요 이슈입니다. **블록체인/암호화폐** 분야에서는 Bitcoin Magazine 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **ICYMI: 2026년 10월 @AWS Security** 관련 긴급 패치 및 영향도 확인
- [ ] **Enterprise-Managed Authorization을 통한 AWS 에이전틱 접근 보안** 관련 긴급 패치 및 영향도 확인
- [ ] **해커들이 두 가지 GeoServer 취약점을 악용, 연구진은 인증 없는 RCE 체인 경고** (CVE-2026-120705, CVE-2026-129243) 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **“Drone 2” 비하인드 스토리: 나의 KubeCon + CloudNativeCon North America 2026 기조연설** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **과학자들은 AI 에이전트에 어디까지 선을 그을까** 관련 AI 보안 정책 검토
- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검

## 관련 포스트 및 참고 자료

- 2026년 11월 25일 주간 보안 다이제스트: {% post_url 2026-11-25-Tech_Security_Weekly_Digest_AI_Zero-Day_Data_AWS %}
- 2026년 11월 24일 주간 보안 다이제스트: {% post_url 2026-11-24-Tech_Security_Weekly_Digest_DeFi_Vulnerability_AI %}
- 2026년 11월 23일 주간 보안 다이제스트: {% post_url 2026-11-23-Tech_Security_Weekly_Digest_AI_Cloud_Data_Agent %}

| 리소스 | 링크 | 용도 |
|--------|------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 실제 악용 확인된 취약점 목록 — 패치 우선순위 기준 |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) | 공격 전술·기법 매핑 — 탐지 룰 설계 |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) | 취약점 악용 확률 점수 — CVSS 보완 |
| AWS Security Blog | [aws.amazon.com](https://aws.amazon.com) | 본문 3건 인용 |
| Hugging Face Blog | [huggingface.co](https://huggingface.co) | 본문 2건 인용 |
| CoinDesk | [coindesk.com](https://www.coindesk.com) | 본문 1건 인용 |
| GitHub Changelog | [github.blog](https://github.blog) | 본문 1건 인용 |
| Docker Blog | [docker.com](https://www.docker.com) | 본문 1건 인용 |
| CNCF Blog | [cncf.io](https://www.cncf.io) | 본문 1건 인용 |
| Bitcoin Magazine | [bitcoinmagazine.com](https://bitcoinmagazine.com) | 본문 3건 인용 |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [2026년 11월 25일 주간 보안 다이제스트: 제로데이·패치·DNS 유출 (27건)](/posts/2026/11/25/Tech_Security_Weekly_Digest_AI_Zero-Day_Data_AWS/) — 2026-11-25
- [2026년 11월 23일 주간 보안 다이제스트: 악성코드·BYOVD EDR·Cisco FMC (17건)](/posts/2026/11/23/Tech_Security_Weekly_Digest_AI_Cloud_Data_Agent/) — 2026-11-23
- [2026년 11월 19일 주간 보안 다이제스트: 클라우드·제로데이·AI 에이전트 (30건)](/posts/2026/11/19/Tech_Security_Weekly_Digest_AWS_Security_AI/) — 2026-11-19

---

**작성자**: Twodragon
