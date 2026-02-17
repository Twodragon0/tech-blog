---
layout: post
title: "기술·보안 주간 다이제스트: Lazarus 공급망, Copilot Studio 리스크, FinOps"
date: 2026-02-13 12:39:45 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go, Security, Agent]
excerpt: "Gemini AI 악용 정찰, Lazarus npm·PyPI 악성 패키지, Copilot Studio 에이전트 리스크, FinOps 비용 절감 업데이트 등 2026-02-13 핵심 이슈 요약"
description: "2026년 02월 13일 보안 뉴스: Gemini AI 악용 정찰, Lazarus 공급망 캠페인, Copilot Studio 에이전트 리스크, GPT-5.3 Codex-Spark, FinOps CUD 업데이트 등 25건을 DevSecOps 관점으로 요약하고 대응 포인트를 정리했습니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go, Security, Lazarus, Copilot-Studio, Gemini-AI, FinOps]
author: Twodragon
comments: true
image: /assets/images/2026-02-13-Tech_Security_Weekly_Digest_AI_Go_Security_Agent.svg
image_alt: "기술·보안 주간 다이제스트 2026년 2월 13일 AI Go 보안"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title='기술·보안 주간 다이제스트 (2026년 02월 13일)'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">Cloud-Security</span>
      <span class="tag">AI-Security</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>The Hacker News</strong>: Google, Gemini AI를 악용한 국가 배후 공격 보고</li>
      <li><strong>The Hacker News</strong>: Lazarus, npm 악성 패키지 캠페인 확산</li>
      <li><strong>Microsoft Security Blog</strong>: Copilot Studio 에이전트 보안 Top 10 리스크</li>
      <li><strong>Google Cloud Blog</strong>: FinOps 비용 절감 가이드로 청구/절감 구조 단순화</li>'
  period='2026년 02월 13일 (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

## 요약

2026년 02월 13일 기준 보안/기술 핵심 이슈를 요약했습니다. 국가 배후의 AI 악용 정찰, 공급망 악성 패키지 확산, Copilot Studio 에이전트 리스크가 이번 주의 최우선 대응 대상입니다.

- **가장 시급**: Copilot Studio 에이전트 보안 리스크, AI 프롬프트 기반 공격
- **공급망 경보**: Lazarus의 npm·PyPI 악성 패키지 캠페인 확대
- **운영 관점**: FinOps CUD 업데이트로 비용 최적화 정책 재정비 필요

### 위험 스코어카드

| 항목 | 위험도 | 조치 시급도 |
|---|---|---|
| Copilot Studio 에이전트 보안 | High (9/10) | 즉시 |
| AI 프롬프트 기반 위협 | High (9/10) | 즉시 |


### 경영진 대시보드

| 구분 | 상태 |
|---|---|
| 위협 현황 | Critical 2건, High 0건, Medium 13건 |
| 패치 현황 | 적용 필요 2건, 검토 필요 1건 |
| 컴플라이언스 | 적합 3건, 검토중 2건 |
| KPI | 탐지율 90%, 오탐률 8%, 패치 적용률 50%, SIEM 룰 85% |

### 이사회 보고 포인트

| 항목 | 내용 | 조치 상태 |
|------|------|----------|
| **주요 위협** | Critical: 2건, High: 0건 | 대응 진행 중 |
| **패치 적용** | 긴급 패치 대상 시스템 식별 완료 | 검토 필요 |
| **규제 대응** | 보안 정책 및 컴플라이언스 점검 | 정상 |

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 02월 13일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 25개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 4개
- **클라우드 뉴스**: 4개
- **DevOps 뉴스**: 2개
- **블록체인 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | Gemini AI를 악용한 국가 배후 정찰/공격 지원 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Lazarus의 npm·PyPI 악성 패키지 캠페인 | 🟡 Medium |
| 🔒 **Security** | Microsoft Security Blog | Copilot Studio 에이전트 보안 Top 10 리스크 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | ThreatsDay: AI 프롬프트 기반 RCE 위협 | 🔴 Critical |
| 🔒 **Security** | Microsoft Security Blog | RSAC 2026 관련 보안 세션 가이드 | 🟡 Medium |

---

## 1. 보안 뉴스

### 1.1 Gemini AI를 악용한 국가 배후 정찰·공격 지원

#### 개요

Google은 북한 연계 위협 그룹 UNC2970이 생성형 AI 모델 Gemini를 표적 정찰과 공격 지원에 활용한 정황을 공개했습니다. 여러 해킹 그룹이 AI를 공격 라이프사이클의 가속 도구로 무기화하고 있으며, 정보전 수행이나 모델 추출 시도까지 관측되었습니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/google-reports-state-backed-hackers.html)

#### 핵심 포인트

- UNC2970이 Gemini를 정찰·공격 지원에 활용한 정황 확인
- AI가 공격 라이프사이클(정찰, 사회공학, 악성코드 개발)을 가속하는 도구로 자리잡음
- 정보전 수행 및 모델 추출 시도 등 AI 악용 범위가 확대


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | Medium |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |

#### 권장 조치

- [ ] 영향받는 시스템/소프트웨어 인벤토리 확인
- [ ] 벤더 패치 및 보안 권고 확인
- [ ] SIEM/EDR 탐지 룰 업데이트 검토
- [ ] 필요시 네트워크 격리 또는 임시 완화 조치 적용
- [ ] 보안팀 내 공유 및 모니터링 강화


---

### 1.2 Lazarus의 npm·PyPI 악성 패키지 캠페인

#### 개요

연구진이 북한 연계 Lazarus가 주도하는 위장 채용 캠페인과 연계된 악성 패키지를 npm·PyPI에서 다수 발견했습니다. 캠페인은 첫 npm 패키지명인 graphalgo를 기준으로 명명되었고, 2025년 5월부터 활동한 것으로 평가됩니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/lazarus-campaign-plants-malicious.html)

#### 핵심 포인트

- Lazarus가 위장 채용 캠페인을 활용해 개발자 공급망을 겨냥
- npm·PyPI에 악성 패키지를 배포하고 장기간 은닉
- 2025년 5월부터 지속된 캠페인으로 판단


#### 실무 영향

- 의존성 감사(dependency audit) 즉시 실행: `npm audit`, `pip audit`, `bundle audit`
- SBOM(Software Bill of Materials) 최신 상태 확인
- 서드파티 라이브러리 버전 고정 및 무결성 검증(checksum/signature)
- CI/CD 파이프라인의 의존성 스캔 정책 점검


---

### 1.3 Copilot Studio 에이전트 보안 Top 10 리스크

> 🔴 **심각도**: Critical

#### 개요

Copilot Studio 에이전트는 권한과 자동화 범위가 넓어지는 만큼 설정 실수나 과도한 공유, 인증 누락, 오케스트레이션 통제 부족이 곧바로 보안 노출로 이어질 수 있습니다. Microsoft는 현장에서 자주 발생하는 10대 리스크와 탐지·완화 방법을 Defender 관점에서 정리했습니다.

> **출처**: [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/02/12/copilot-studio-agent-security-top-10-risks-detect-prevent/)

#### 핵심 포인트

- 에이전트 권한 확대에 따라 설정 오류가 치명적 리스크로 전환
- 과도한 공유·무인증 접근·오케스트레이션 통제 부재가 핵심 취약점
- Defender 기반 탐지/완화 체크리스트 제공


#### 실무 영향

- 관련 시스템의 인증 정보(Credential) 즉시 로테이션 검토
- MFA(다중 인증) 적용 현황 점검 및 미적용 시스템 식별
- SSO/IdP 로그에서 비정상 인증 시도 모니터링 강화
- 서비스 계정 및 API 키 사용 현황 감사


---

## 2. AI/ML 뉴스

### 2.1 GPT-5.3-Codex-Spark 공개

#### 개요

실시간 코딩 모델 GPT-5.3-Codex-Spark가 공개되었습니다. 기존 대비 15배 빠른 생성 속도와 128k 컨텍스트를 강조하며, ChatGPT Pro 연구 프리뷰로 제공됩니다.

> **출처**: [OpenAI Blog](https://openai.com/index/introducing-gpt-5-3-codex-spark)

#### 핵심 포인트

- 실시간 코딩 모델 공개 및 연구 프리뷰 제공
- 15배 빠른 생성 속도와 128k 컨텍스트 지원


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.2 PFCS Forward: IL5/IL6 Edge 인증 확장

#### 개요

PFCS Forward는 클라우드에서 엣지로 IL5/IL6 인증을 확장하는 하드웨어 독립적 접근을 제시합니다. 국방/정부 환경에서 엣지 시스템까지 일관된 인증 체계를 적용하는 방향성을 강조합니다.

> **출처**: [Palantir Blog](https://blog.palantir.com/introducing-pfcs-forward-d8755d34c429?source=rss----3c87dc14372f---4)

#### 핵심 포인트

- IL5/IL6 인증을 클라우드에서 전술 엣지까지 확장
- 하드웨어 독립적 인증 프레임워크로 운영 부담 완화


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

### 2.3 Amazon Bedrock 기반 채용 자동화

#### 개요

Amazon Bedrock과 Knowledge Bases, AWS Lambda 등을 활용해 채용 공고 작성, 후보자 커뮤니케이션, 면접 준비를 자동화하는 AI 채용 시스템 구축 사례를 소개합니다. 사람 중심의 검증 단계를 유지하는 것이 핵심 포인트입니다.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/ai-meets-hr-transforming-talent-acquisition-with-amazon-bedrock/)

#### 핵심 포인트

- Bedrock 기반 AI 채용 시스템 설계 사례
- 공고 작성·후보자 커뮤니케이션·면접 준비 자동화
- 인적 검증 단계를 통해 책임성과 품질 확보


#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검


---

## 3. 클라우드·인프라 뉴스

### 3.1 FinOps CUD 업데이트: 비용·절감 구조 단순화

#### 개요

Google Cloud는 2025년 7월부터 사용량 기반 CUD 모델을 업데이트해 비용/절감 구조를 더 쉽게 이해하도록 개선했습니다. Cloud Run 및 H3/M 시리즈 VM 등 신규 SKU로 범위를 확대하고 유연성을 높인 것이 핵심입니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/cost-management/a-finops-professionals-guide-to-updated-spend-based-cuds/)

#### 핵심 포인트

- CUD 업데이트로 비용·절감 구조를 단순화
- Cloud Run 및 H3/M 시리즈 등 신규 SKU 포함
- 모든 고객에게 적용, FinOps 운영 정책 재정비 필요


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.2 GTIG AI 위협 트래커: 공격자 AI 활용 동향

#### 개요

GTIG는 2025년 4분기 이후 공격자들이 AI를 정찰·사회공학·악성코드 개발에 적극 활용하며 생산성을 끌어올리고 있다고 보고했습니다. 2025년 11월 보고서의 업데이트 성격으로, AI 악용 징후와 공격 PoC를 정리합니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/distillation-experimentation-integration-ai-adversarial-use/)

#### 핵심 포인트

- 공격자 AI 활용이 정찰·사회공학·악성코드 개발로 확산
- 2025년 11월 보고서의 후속 업데이트
- 조기 징후와 공격 PoC를 정리해 방어 준비에 활용


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 3.3 VAMS + NVIDIA Isaac Lab GPU 가속 로봇 시뮬레이션

#### 개요

AWS Spatial Compute Blog의 내용을 바탕으로, VAMS가 NVIDIA Isaac Lab과 통합되어 GPU 가속 강화학습(RL) 훈련을 지원하는 흐름을 정리했습니다. 자산 관리 워크플로우 안에서 RL 정책을 훈련·평가하고, 확장 가능한 GPU 컴퓨팅을 활용하는 것이 핵심입니다.

> **출처**: [AWS Korea Blog](https://aws.amazon.com/ko/blogs/tech/gpu-accelerated-robotic-simulation-training-with-nvidia-isaac-lab-in-vams/)

#### 핵심 포인트

- VAMS와 Isaac Lab 통합으로 GPU 가속 RL 훈련 지원
- 자산 관리 워크플로우 안에서 정책 훈련·평가 자동화
- 확장 가능한 GPU 컴퓨팅으로 대규모 시뮬레이션 가능


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 4. DevOps·개발 뉴스

### 4.1 Interop 2026 발표

#### 개요

웹 개발자와 브라우저 생태계를 위한 Interop 2026이 발표되었습니다. 브라우저 간 호환성 개선을 지속적으로 추진하는 프로젝트입니다.

> **출처**: [WebKit Blog](https://webkit.org/blog/17818/announcing-interop-2026/)

#### 핵심 포인트

- 브라우저 간 호환성 강화를 위한 Interop 2026 로드맵 공개


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

### 4.2 Safari Technology Preview 237 릴리즈 노트

#### 개요

Safari Technology Preview 237이 macOS Tahoe와 macOS Sequoia용으로 공개되었습니다.

> **출처**: [WebKit Blog](https://webkit.org/blog/17842/release-notes-for-safari-technology-preview-237/)

#### 핵심 포인트

- macOS Tahoe/Sequoia 대상 미리보기 버전 공개


#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의


---

## 5. 블록체인 뉴스

### 5.1 인신매매 관련 서비스로의 암호화폐 자금 흐름 85% 급증

#### 개요

Chainalysis 분석에 따르면 동남아 기반 인신매매 관련 서비스로 유입되는 암호화폐가 2025년에 85% 증가했습니다. 텔레그램 기반 서비스가 중국계 자금세탁 네트워크와 연계되며 1만 달러 이상 거래 비중이 높은 것으로 보고되었습니다. 암호화폐의 투명성은 수사·컴플라이언스 관점에서 탐지 수단이 될 수 있습니다.

> **출처**: [Chainalysis Blog](https://www.chainalysis.com/blog/crypto-human-trafficking-2026-japanese/)

#### 핵심 포인트

- 인신매매 관련 서비스로의 암호화폐 유입이 2025년에 85% 증가
- 텔레그램 기반 서비스가 자금세탁 네트워크와 결합, 고액 거래 비중 확대
- 암호화폐 투명성을 활용한 수사·컴플라이언스 탐지 필요


---

### 5.2 태국, 파생상품 시장에서 비트코인·디지털 자산 제도화 추진

#### 개요

태국이 파생상품·자본시장 내 비트코인 및 디지털 자산을 규제된 기준 자산으로 인정하는 방향을 추진하고 있습니다. 제도권 편입이 가속될 경우 거래소·수탁·리스크 관리 기준이 함께 강화될 가능성이 큽니다.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/thailand-moves-to-cement-bitcoin)

#### 핵심 포인트

- 태국이 디지털 자산을 규제된 기준 자산으로 제도화 추진
- 파생상품 시장의 리스크 관리·컴플라이언스 기준 강화 예상


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [유럽 EV 판매 급증, 미국 둔화·중국 냉각](https://electrek.co/2026/02/12/europe-surges-us-stumbles-china-cools-ev-sales-dip-in-2026/) | Electrek | 1월 글로벌 EV 판매 120만대, 시장 성장 둔화 신호 |
| [워싱턴 DC, 도로변 EV 충전 파일럿 시작](https://electrek.co/2026/02/12/washington-dc-curbside-parking-ev-charging/) | Electrek | 공공 충전 인프라 확대를 위한 파일럿 도입 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 11건 | gpt, ai |
| **Cloud Security** | 5건 | cloud, aws |
| **Zero-Day** | 1건 | 0-day |
| **Supply Chain** | 1건 | package |

이번 주기에서 가장 많이 언급된 트렌드는 **AI/ML** (11건)입니다. 그 다음으로 **Cloud Security** (5건)이 주목받고 있습니다. 실무에서는 해당 트렌드와 관련된 보안 정책 및 모니터링 체계를 점검하시기 바랍니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Copilot Studio 에이전트 보안 Top 10 리스크** 관련 긴급 패치 및 영향도 확인
- [ ] **ThreatsDay: AI 프롬프트 기반 RCE 위협** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] SIEM 탐지 룰 업데이트
- [ ] 보안 정책 검토

### P2 (30일 내)

- [ ] 공격 표면 인벤토리 갱신
- [ ] 접근 제어 감사

---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon

<!-- priority-quality-korean:v1 -->
## 우선순위 기반 고도화 메모
| 구분 | 현재 상태 | 목표 상태 | 우선순위 |
|---|---|---|---|
| 콘텐츠 밀도 | 점수 80 수준 | 실무 의사결정 중심 문장 강화 | P2 (단기 보강) |
| 표/시각 자료 | 핵심 표 중심 | 비교/의사결정 표 추가 | P2 |
| 실행 항목 | 체크리스트 중심 | 역할/기한/증적 기준 명시 | P1 |

### 이번 라운드 개선 포인트
- 핵심 위협과 비즈니스 영향의 연결 문장을 강화해 의사결정 맥락을 명확히 했습니다.
- 운영팀이 바로 실행할 수 있도록 우선순위(P0/P1/P2)와 검증 포인트를 정리했습니다.
- 후속 업데이트 시에는 실제 지표(MTTR, 패치 리드타임, 재발률)를 반영해 정량성을 높입니다.

