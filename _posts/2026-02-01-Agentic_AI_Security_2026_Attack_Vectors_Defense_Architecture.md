---
author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-02-01 19:00:00 +0900
description: AI Agent Tool Poisoning, Agentic Tool Chain Attack, Prompt Injection
  방어, Chrome Agentic Security, CrowdStrike Falcon Agentic Defense, LLM 취약점 진단, JWT
  서명키 유출 대응 등 2026년 에이전틱 AI 보안의 모든 것을 다루는 실무 가이드.
excerpt: 2026년 에이전틱 AI 시대의 새로운 공격 벡터(Tool Poisoning, Tool Chain Attack, Prompt Injection)와
  Google Chrome·CrowdStrike Falcon의 방어 아키텍처를 심층 분석합니다.
image: /assets/images/2026-02-01-Agentic_AI_Security_2026_Attack_Vectors_Defense_Architecture.svg
image_alt: Agentic AI Security 2026 - Attack Vectors and Defense Architecture Guide
keywords:
- Agentic AI Security
- AI Tool Poisoning
- Tool Chain Attack
- Prompt Injection Defense
- Chrome Agentic Security
- CrowdStrike Falcon
- LLM Vulnerability
- JWT Security
- LABYRINTH CHOLLIMA
- Linux Security 2026
layout: post
schema_type: Article
tags:
- Agentic-AI
- AI-Security
- Tool-Poisoning
- Prompt-Injection
- LLM-Security
- Supply-Chain
- Zero-Trust
- DevSecOps
- CrowdStrike
- Google-Security
- '2026'
title: '에이전틱 AI 보안 2026: AI Agent 공격 벡터와 방어 아키텍처 완전 가이드'
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">에이전틱 AI 보안 2026: 공격 벡터와 방어 아키텍처</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Agentic-AI</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Tool-Poisoning</span>
      <span class="tag">Prompt-Injection</span>
      <span class="tag">LLM-Security</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">2026</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>CrowdStrike</strong>: AI Tool Poisoning - 도구 설명에 숨겨진 악성 지시로 AI 에이전트 조작</li>
      <li><strong>CrowdStrike</strong>: Agentic Tool Chain Attack - AI 에이전트 공급망 공격의 새로운 벡터</li>
      <li><strong>Google</strong>: Chrome 에이전틱 보안 아키텍처 - 샌드박스 기반 에이전트 격리</li>
      <li><strong>Google</strong>: Prompt Injection 다층 방어 전략 - 입력 필터링부터 출력 검증까지</li>
      <li><strong>SK쉴더스</strong>: LLM Application 취약점 진단 가이드 - 실무 점검 체크리스트</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, AI/ML 엔지니어, 클라우드 아키텍트, CISO</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

2026년은 AI가 단순한 챗봇을 넘어 **자율적으로 도구를 호출하고 작업을 수행하는 에이전틱(Agentic) AI 시대**로 진입한 해입니다. CrowdStrike, Google, Microsoft, OWASP 등 주요 보안 기업과 기관들이 에이전틱 AI의 새로운 위협 벡터에 대한 연구 결과를 잇따라 발표하고 있습니다.

이 포스트에서는 2026년 1월 발표된 최신 연구를 기반으로, AI 에이전트에 대한 **공격 벡터(Attack Vector)**와 이에 대응하는 **방어 아키텍처(Defense Architecture)**를 실무 관점에서 심층 분석합니다.

### 경영진 요약 (Executive Summary)

**에이전틱 AI 보안 위험 스코어카드**

| 공격 벡터 | 심각도 | 탐지 난이도 | 비즈니스 영향 | 대응 긴급도 |
|-----------|--------|-------------|---------------|-------------|
| AI Tool Poisoning | 🔴 Critical (9.8) | 높음 | 데이터 유출, 시스템 조작 | P0 (즉시) |
| Agentic Tool Chain Attack | 🔴 Critical (9.5) | 매우 높음 | 공급망 전체 오염 | P0 (즉시) |
| Indirect Prompt Injection | 🟠 High (8.2) | 높음 | 권한 우회, 정보 유출 | P1 (7일 내) |
| Agent Identity Abuse | 🟠 High (7.9) | 중간 | 권한 탈취, 횡적 이동 | P1 (7일 내) |
| Model Data Exfiltration | 🟡 Medium (6.5) | 중간 | 지적 재산 유출 | P2 (30일 내) |
| Excessive Agent Autonomy | 🟡 Medium (5.8) | 낮음 | 의도하지 않은 작업 수행 | P2 (30일 내) |

**핵심 권고사항**:
- 모든 AI 에이전트 도구에 대한 **허용 목록(Allowlist) 기반 운영** 즉시 적용
- 고위험 작업에 대한 **Human-in-the-Loop 승인 프로세스** 의무화
- AI 에이전트 도구 호출 이력에 대한 **실시간 감사 로그 및 이상 탐지** 구축
- 에이전틱 AI 보안 성숙도 현황 평가 및 **30일 내 L2(관리) 수준 달성**

**다루는 핵심 주제:**

| 주제 | 출처 | 발표일 |
|------|------|--------|
| AI Tool Poisoning | CrowdStrike | 2026-01-09 |
| Agentic Tool Chain Attack | CrowdStrike | 2026-01-30 |
| Chrome Agentic Security Architecture | Google Security Blog | 2025-12-08 |
| Prompt Injection 다층 방어 | Google Security Blog | 2025-06 |
| Agentic Defense (Falcon Platform) | CrowdStrike | 2026-01-16 |
| LABYRINTH CHOLLIMA 분화 | CrowdStrike | 2026-01-29 |
| LLM Application 취약점 진단 | SK쉴더스 EQST | 2025 |
| JWT 서명키 유출 위협 | SK쉴더스 | 2026-01 |
| 2026 Linux Security Threat Landscape | HashiCorp | 2026-01 |
| Terraform MCP Server | HashiCorp | 2026-01 |

---

## 1. 한국 영향 분석 및 규제 대응 (Korean Impact Analysis)

### 1.1 국내 AI 규제 환경 개요

2026년 현재 한국의 AI 관련 규제는 **개인정보보호법, 정보통신망법, 신용정보법**을 중심으로 운영되고 있으며, 에이전틱 AI 보안과 직접적으로 관련된 주요 규제 포인트는 다음과 같습니다:

| 법규 | 주요 조항 | 에이전틱 AI 보안 연관성 |
|------|----------|----------------------|
| **개인정보보호법** 제29조 | 안전성 확보 조치 의무 | AI 에이전트의 개인정보 처리 시 Tool Poisoning 방어 필수 |
| **개인정보보호법** 제15조 | 개인정보 수집·이용 동의 | AI 에이전트의 자율적 데이터 수집 시 명시적 동의 필요 |
| **정보통신망법** 제28조 | 개인정보의 보호조치 | 에이전트 도구 체인 내 암호화 및 접근통제 의무 |
| **신용정보법** 제21조 | 신용정보의 안전성 확보 | 금융 AI 에이전트의 Tool Chain Attack 방어 필수 |
| **클라우드컴퓨팅법** 제23조 | 이용자 보호 | 클라우드 기반 AI 에이전트 서비스 제공자의 보안 책임 |

### 1.2 금융권 영향 분석

한국 금융권은 **금융보안원(FSI)** 주도로 AI 보안 가이드라인을 마련 중이며, 에이전틱 AI 도입 시 다음 사항이 강화되고 있습니다:

**금융 AI 에이전트 보안 요구사항 (2026년 신설)**


**개인정보 처리 단계별 준수 사항**

| 단계 | 법적 근거 | 에이전틱 AI 적용 방안 |
|------|----------|----------------------|
| **수집** | 개인정보보호법 제15조 (동의) | AI 에이전트 작업 시작 전 명시적 동의 획득 |
| **이용** | 개인정보보호법 제18조 (목적 외 이용 제한) | 에이전트 시스템 프롬프트에 목적 명시 및 제약 |
| **제공** | 개인정보보호법 제17조 (제3자 제공 제한) | 외부 API/도구 호출 시 사전 동의 필수 |
| **보관** | 개인정보보호법 제21조 (파기 의무) | 에이전트 세션 종료 시 개인정보 자동 삭제 |
| **안전 조치** | 개인정보보호법 제29조 | Tool Poisoning 방어, 접근통제, 암호화 |

### 1.5 경영진 보고 형식 (Board Reporting Format)

**에이전틱 AI 보안 위험 경영진 보고서 (2026년 2월 기준)**

---

**제목**: 에이전틱 AI 도입에 따른 보안 위험 및 대응 현황 보고

**보고일**: 2026년 2월 8일
**보고자**: CISO (Chief Information Security Officer)
**수신**: 이사회, CEO, CTO

---

#### 1. 요약 (Executive Summary)

2026년 1분기, 당사는 AI 에이전트 기반 고객 응대 시스템을 도입하였으며, 이에 따른 신규 보안 위험을 식별하고 대응 계획을 수립하였습니다. 주요 위험은 **AI Tool Poisoning**(도구 오염)과 **Tool Chain Attack**(도구 체인 공격)이며, 현재 대응 수준은 **Level 2 (관리)**입니다.

**주요 지표**:
- **보안 위험 수준**: 🟠 High (8.5/10)
- **대응 성숙도**: Level 2 (관리 단계)
- **목표 성숙도**: Level 3 (고도화 단계, 2026년 3분기 달성)
- **투자 필요 예산**: 3억 원 (보안 솔루션 + 인력)

---

#### 2. 핵심 위험 (Key Risks)

| 위험 | 현재 상태 | 비즈니스 영향 | 발생 가능성 | 대응 우선순위 |
|------|----------|---------------|-------------|--------------|
| **AI Tool Poisoning** | 🔴 미흡 | 고객 데이터 유출 → 과징금 최대 3% | 높음 (30%) | P0 (즉시) |
| **Tool Chain Attack** | 🟡 보통 | 서비스 중단, 공급망 오염 | 중간 (15%) | P1 (7일 내) |
| **Prompt Injection** | 🟢 양호 | 권한 우회, 부정 거래 | 낮음 (5%) | P2 (30일 내) |
| **과도한 자율성** | 🟡 보통 | 의도하지 않은 고객 정보 노출 | 중간 (20%) | P1 (7일 내) |

**재무 영향 추정**:
- **최악 시나리오**: 개인정보 10만 건 유출 시 과징금 약 50억 원 + 브랜드 손실
- **예상 손실 (연간 기대값)**: 약 5억 원 (발생 가능성 × 영향도)

---

#### 3. 현재 대응 현황

**적용 완료된 조치** ✅:
- AI 에이전트 도구 허용 목록 운영 (30개 검증된 도구)
- 고위험 작업에 Human-in-the-Loop 승인 프로세스 적용
- AI 에이전트 감사 로그 Splunk SIEM 연동 (실시간 모니터링)

**미완료 조치** ⚠️:
- MCP 서버 도구 설명 자동 스캔 파이프라인 (구축 중, 3월 완료 예정)
- 에이전트 행위 기반 이상 탐지 (UEBA) 시스템 (예산 승인 대기)
- 정기 AI Red Team 테스트 (분기별 → 월별로 강화 필요)

---

#### 4. 권고 사항 (Recommendations)

| 권고 | 예산 | 기대 효과 | 우선순위 |
|------|------|----------|----------|
| **AI 보안 전담 조직 신설** | 인건비 2억/년 | 위험 탐지 시간 80% 단축 | 🔴 긴급 |
| **UEBA 솔루션 도입** | 라이선스 1억/년 | Tool Poisoning 탐지율 90% | 🔴 긴급 |
| **Red Team 강화** | 외주 용역 5천만/년 | 취약점 사전 발견 | 🟠 중요 |
| **임직원 AI 보안 교육** | 교육비 2천만/년 | 인적 오류 50% 감소 | 🟡 권장 |

**총 소요 예산**: 약 3.7억 원/년

---

#### 5. 액션 플랜 (Action Plan)

| 일정 | 조치 | 담당 부서 | 완료 기준 |
|------|------|----------|----------|
| **2월 15일** | AI 도구 자동 스캔 파이프라인 구축 | 보안팀 | 도구 등록 시 자동 검증 |
| **2월 28일** | UEBA 솔루션 벤더 선정 | 보안팀, IT팀 | POC 완료 |
| **3월 15일** | Red Team 테스트 (1차) | 외부 전문 업체 | 취약점 리포트 제출 |
| **3월 31일** | Level 3 (고도화) 달성 | 보안팀 | 실시간 자동 대응 가능 |

---

#### 6. 결론 (Conclusion)

에이전틱 AI 도입은 고객 만족도 향상과 운영 효율성 증대에 기여하고 있으나, 신규 보안 위험에 대한 체계적 관리가 필수적입니다. 현재 위험 수준(High)을 고려할 때, **2026년 1분기 내 Level 3 보안 성숙도 달성**을 목표로 투자 승인을 요청드립니다.

---

## 2. AI Agent 공격 벡터: 새로운 위협 지형도

### 1.1 AI Tool Poisoning: 도구에 숨겨진 악성 지시

> **출처**: [CrowdStrike - AI Tool Poisoning: How Hidden Instructions Threaten AI Agents](https://www.crowdstrike.com/en-us/blog/ai-tool-poisoning/)

#### 공격 원리

AI Tool Poisoning은 **MCP(Model Context Protocol) 서버나 API 도구의 설명(description)에 숨겨진 악성 지시**를 삽입하는 공격입니다. AI 에이전트가 도구를 선택할 때 도구 설명을 참조하는 특성을 악용합니다.

#### 5.2.6 데이터 유출 공격 흐름도 (종합)

**탐지 및 대응 타임라인**

| 시간 | 공격 단계 | 탐지 시그널 | 대응 조치 | 예상 영향 |
|------|----------|-------------|----------|----------|
| T+0 | 도구 오염 | GitHub commit (비정상 패턴) | 소스 코드 리뷰, Git 감사 | 없음 (예방) |
| T+1 (10분) | 자격증명 수집 | SIEM 경고: 민감 파일 접근 | 세션 즉시 종료, 계정 잠금 | 최소 (조기 탐지) |
| T+1 (11분) | 데이터 유출 시도 | 방화벽: 의심스러운 외부 연결 | 네트워크 차단, 포렌식 시작 | 낮음 (차단 성공 시) |
| T+2 | 권한 상승 | CloudTrail: 비정상 IAM 활동 | AWS 자격증명 무효화, IR 팀 소집 | 중간 (일부 접근) |
| T+3~7 | 대량 유출 | DLP: 대량 데이터 전송 | 법적 대응, 고객 통지 준비 | 높음 (규제 위반) |

### 5.3 에이전틱 AI 보안 성숙도 모델

| 레벨 | 이름 | 특징 | 핵심 활동 |
|------|------|------|----------|
| **L0** | 미인식 | AI 에이전트 보안 미고려 | - |
| **L1** | 기본 | 도구 허용 목록, 기본 로깅 | 인벤토리 관리 |
| **L2** | 관리 | 도구 무결성 검증, 권한 분리 | 정책 기반 제어 |
| **L3** | 고도화 | 실시간 행위 모니터링, 자동 대응 | UEBA, Agentic SOAR |
| **L4** | 최적화 | AI 기반 방어, 지속적 개선 | Red Team, 위협 인텔 연동 |

---

## 6. 실무 체크리스트

### P0: 즉시 적용 (이번 주)

- [ ] AI 에이전트가 사용하는 **도구 인벤토리** 작성
- [ ] 도구 설명(description) 내 **숨겨진 지시 스캔**
- [ ] 고위험 작업에 대한 **Human-in-the-Loop** 확인
- [ ] JWT 서명키 저장 방식 점검 (하드코딩 여부)

### P1: 7일 내

- [ ] MCP 서버/도구에 대한 **허용 목록(allowlist)** 구축
- [ ] 에이전트 도구 호출 **감사 로그** 활성화
- [ ] SIEM 탐지 룰에 에이전틱 공격 패턴 추가
- [ ] LLM Application 취약점 진단 (OWASP LLM Top 10 기반)

### P2: 30일 내

- [ ] 에이전틱 보안 성숙도 자가 평가 (L0~L4)
- [ ] AI 에이전트 보안 정책 문서화
- [ ] Red Team 시나리오에 Tool Poisoning/Chain Attack 추가
- [ ] 보안 교육에 에이전틱 AI 위협 모듈 추가

---

## 7. 기타 주목할 보안 동향

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [CrowdStrike, Seraphic 인수](https://www.crowdstrike.com/en-us/blog/crowdstrike-to-acquire-seraphic/) | CrowdStrike | 브라우저 보안 강화를 위한 인수 — 에이전틱 브라우징 보안 |
| [USB 드라이브 보안 위협](https://www.crowdstrike.com/en-us/blog/usb-drives-threaten-enterprise-security/) | CrowdStrike | 물리적 매체를 통한 기업 보안 침해 사례 증가 |
| [January 2026 Patch Tuesday](https://www.crowdstrike.com/en-us/blog/january-2026-patch-tuesday-114-cves/) | CrowdStrike | 114개 CVE 패치, 3개 Zero-Day 포함 |
| [GCP 보안 공지 2026-001~006](https://cloud.google.com/support/bulletins) | Google Cloud | GKE, Compute Engine 등 다수 취약점 패치 |
| [Rust in Android](https://security.googleblog.com/2025/11/rust-in-android-move-fast-fix-things.html) | Google | 메모리 안전 취약점 20% 이하로 감소 — Rust 도입 성과 |
| [Terraform MCP Server 0.4](https://www.hashicorp.com/blog/terraform-mcp-server-updates-stacks-support-new-tools-and-tips) | HashiCorp | Stacks 지원, 새로운 AI 도구, 사용 팁 |
| [선제적 보안과 레드팀 전략](https://www.skshieldus.com/) | SK쉴더스 | 사이버 면역 체계 구축을 위한 레드팀 기반 전략 |

---

## 참고 자료

### 주요 보안 프레임워크 및 가이드라인

| 리소스 | URL | 설명 |
|--------|-----|------|
| **OWASP LLM Top 10 (2025)** | [https://owasp.org/www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/) | LLM 애플리케이션 취약점 Top 10 |
| **OWASP Agentic AI Top 10** | [https://genai.owasp.org/](https://genai.owasp.org/) | 에이전틱 AI 전용 보안 위협 분류 |
| **MITRE ATT&CK Framework** | [https://attack.mitre.org/](https://attack.mitre.org/) | 사이버 공격 전술 및 기법 매트릭스 |
| **MITRE ATLAS (AI 전용)** | [https://atlas.mitre.org/](https://atlas.mitre.org/) | AI/ML 시스템 공격 기법 데이터베이스 |
| **NIST AI Risk Management Framework** | [https://www.nist.gov/itl/ai-risk-management-framework](https://www.nist.gov/itl/ai-risk-management-framework) | AI 시스템 위험 관리 프레임워크 |
| **ISO/IEC 42001 (AI Management)** | [https://www.iso.org/standard/81230.html](https://www.iso.org/standard/81230.html) | AI 관리 시스템 국제 표준 |

### CrowdStrike 에이전틱 AI 보안 연구

| 제목 | URL | 발표일 |
|------|-----|--------|
| **AI Tool Poisoning** | [https://www.crowdstrike.com/en-us/blog/ai-tool-poisoning/](https://www.crowdstrike.com/en-us/blog/ai-tool-poisoning/) | 2026-01-09 |
| **Agentic Tool Chain Attack** | [https://www.crowdstrike.com/en-us/blog/how-agentic-tool-chain-attacks-threaten-ai-agent-security/](https://www.crowdstrike.com/en-us/blog/how-agentic-tool-chain-attacks-threaten-ai-agent-security/) | 2026-01-30 |
| **Architecture of Agentic Defense** | [https://www.crowdstrike.com/en-us/blog/architecture-of-agentic-defense-inside-the-falcon-platform/](https://www.crowdstrike.com/en-us/blog/architecture-of-agentic-defense-inside-the-falcon-platform/) | 2026-01-16 |
| **SGNL Acquisition (ID Security)** | [https://www.crowdstrike.com/en-us/blog/crowdstrike-to-acquire-sgnl/](https://www.crowdstrike.com/en-us/blog/crowdstrike-to-acquire-sgnl/) | 2026-01 |
| **LABYRINTH CHOLLIMA Evolution** | [https://www.crowdstrike.com/en-us/blog/labyrinth-chollima-evolves-into-three-adversaries/](https://www.crowdstrike.com/en-us/blog/labyrinth-chollima-evolves-into-three-adversaries/) | 2026-01-29 |
| **Seraphic Acquisition (Browser)** | [https://www.crowdstrike.com/en-us/blog/crowdstrike-to-acquire-seraphic/](https://www.crowdstrike.com/en-us/blog/crowdstrike-to-acquire-seraphic/) | 2026-01 |
| **USB Drive Security Threats** | [https://www.crowdstrike.com/en-us/blog/usb-drives-threaten-enterprise-security/](https://www.crowdstrike.com/en-us/blog/usb-drives-threaten-enterprise-security/) | 2026-01 |
| **January 2026 Patch Tuesday** | [https://www.crowdstrike.com/en-us/blog/january-2026-patch-tuesday-114-cves/](https://www.crowdstrike.com/en-us/blog/january-2026-patch-tuesday-114-cves/) | 2026-01-15 |

### Google 보안 연구

| 제목 | URL | 발표일 |
|------|-----|--------|
| **Chrome Agentic Security Architecture** | [https://security.googleblog.com/2025/12/architecting-security-for-agentic.html](https://security.googleblog.com/2025/12/architecting-security-for-agentic.html) | 2025-12-08 |
| **Mitigating Prompt Injection** | [https://security.googleblog.com/2025/06/mitigating-prompt-injection-attacks.html](https://security.googleblog.com/2025/06/mitigating-prompt-injection-attacks.html) | 2025-06 |
| **Rust in Android (Memory Safety)** | [https://security.googleblog.com/2025/11/rust-in-android-move-fast-fix-things.html](https://security.googleblog.com/2025/11/rust-in-android-move-fast-fix-things.html) | 2025-11 |
| **GCP Security Bulletins** | [https://cloud.google.com/support/bulletins](https://cloud.google.com/support/bulletins) | 2026-01 |

### HashiCorp 보안 및 인프라

| 제목 | URL | 발표일 |
|------|-----|--------|
| **2026 Linux Security Threat Landscape** | [https://www.hashicorp.com/blog/the-linux-security-threat-landscape-and-strategic-defense-pillars](https://www.hashicorp.com/blog/the-linux-security-threat-landscape-and-strategic-defense-pillars) | 2026-01 |
| **Terraform MCP Server 0.4** | [https://www.hashicorp.com/blog/terraform-mcp-server-updates-stacks-support-new-tools-and-tips](https://www.hashicorp.com/blog/terraform-mcp-server-updates-stacks-support-new-tools-and-tips) | 2026-01 |
| **Vault (Secrets Management)** | [https://www.vaultproject.io/](https://www.vaultproject.io/) | - |

### 국내 보안 기관 및 규제

| 리소스 | URL | 설명 |
|--------|-----|------|
| **개인정보보호위원회** | [https://www.pipc.go.kr/](https://www.pipc.go.kr/) | 개인정보보호법 및 AI 가이드라인 |
| **금융보안원 (FSI)** | [https://www.fsec.or.kr/](https://www.fsec.or.kr/) | 금융권 AI 보안 가이드라인 |
| **한국인터넷진흥원 (KISA)** | [https://www.kisa.or.kr/](https://www.kisa.or.kr/) | 사이버 보안 및 개인정보보호 |
| **국가정보원 국가사이버안전센터** | [https://www.ncsc.go.kr/](https://www.ncsc.go.kr/) | 국가·공공기관 보안 지침 |
| **과학기술정보통신부** | [https://www.msit.go.kr/](https://www.msit.go.kr/) | 정보통신망법, 클라우드 보안 인증 |

### SK쉴더스 보안 연구

| 제목 | URL | 발표일 |
|------|-----|--------|
| **LLM Application 취약점 진단 가이드** | [https://www.skshieldus.com/download/files/download.do?o_fname=LLM%20Application%20취약점%20진단%20가이드.pdf](https://www.skshieldus.com/download/files/download.do?o_fname=LLM%20Application%20취약점%20진단%20가이드.pdf) | 2025 |
| **JWT 서명키 유출 위협과 대응** | [https://www.skshieldus.com/](https://www.skshieldus.com/) | 2026-01 |
| **선제적 보안과 레드팀 전략** | [https://www.skshieldus.com/](https://www.skshieldus.com/) | 2026 |

### 위협 인텔리전스

| 리소스 | URL | 설명 |
|--------|-----|------|
| **CISA KEV (Known Exploited Vulnerabilities)** | [https://www.cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 실제 악용된 취약점 카탈로그 |
| **CrowdStrike Adversary Intelligence** | [https://www.crowdstrike.com/adversaries/](https://www.crowdstrike.com/adversaries/) | 위협 그룹 프로필 및 IOC |
| **The Hacker News** | [https://thehackernews.com/](https://thehackernews.com/) | 최신 사이버 보안 뉴스 |
| **MISP (Threat Intelligence Sharing)** | [https://www.misp-project.org/](https://www.misp-project.org/) | 위협 인텔리전스 공유 플랫폼 |

### 관련 기술 문서

| 리소스 | URL | 설명 |
|--------|-----|------|
| **Model Context Protocol (MCP)** | [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/) | AI 에이전트 도구 연결 프로토콜 |
| **LangChain Security Best Practices** | [https://python.langchain.com/docs/security](https://python.langchain.com/docs/security) | LangChain 보안 모범 사례 |
| **OpenAI Safety Best Practices** | [https://platform.openai.com/docs/guides/safety-best-practices](https://platform.openai.com/docs/guides/safety-best-practices) | OpenAI API 보안 가이드 |
| **Anthropic Claude Safety** | [https://www.anthropic.com/safety](https://www.anthropic.com/safety) | Claude AI 안전성 연구 |

### SIEM/보안 도구

| 도구 | URL | 용도 |
|------|-----|------|
| **Splunk Enterprise Security** | [https://www.splunk.com/en_us/products/enterprise-security.html](https://www.splunk.com/en_us/products/enterprise-security.html) | SIEM 플랫폼 |
| **Microsoft Sentinel** | [https://azure.microsoft.com/en-us/products/microsoft-sentinel](https://azure.microsoft.com/en-us/products/microsoft-sentinel) | 클라우드 네이티브 SIEM |
| **Wazuh** | [https://wazuh.com/](https://wazuh.com/) | 오픈소스 보안 플랫폼 |
| **GitLeaks** | [https://github.com/gitleaks/gitleaks) | Git 저장소 비밀정보 스캔 |
| **TruffleHog** | [https://github.com/trufflesecurity/trufflehog) | 비밀정보 유출 탐지 |

---

**작성자**: Twodragon
**작성일**: 2026년 2월 1일
**카테고리**: Security, DevSecOps
