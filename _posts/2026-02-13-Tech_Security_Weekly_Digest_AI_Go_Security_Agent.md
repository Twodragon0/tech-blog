---
layout: post
title: "기술 & 보안 주간 다이제스트: Lazarus, RCE, 클라우드"
date: 2026-02-13 12:39:45 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go, Security, Agent]
excerpt: "2026년 02월 13일 주요 보안/기술 뉴스 25건 - AI, Go, Security"
description: "2026년 02월 13일 보안 뉴스: The Hacker News, Microsoft Security Blog 등 25건. AI, Go, Security, Agent 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Go, Security]
author: Twodragon
comments: true
image: /assets/images/2026-02-13-Tech_Security_Weekly_Digest_AI_Go_Security_Agent.svg
image_alt: "기술 보안 주간 다이제스트 2026년 2월 13일 AI Go 보안"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title='기술 &amp; 보안 주간 다이제스트: Lazarus, RCE, 클라우드'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">Weekly-Digest</span> <span class="tag">2026</span> <span class="tag">AI</span> <span class="tag">Go</span> <span class="tag">Security</span>'
  highlights_html='<li><strong>포인트 1</strong>: 2026년 02월 13일 주요 보안/기술 뉴스 25건 - AI, Go, Security</li> <li><strong>포인트 2</strong>: 실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다</li> <li><strong>포인트 3</strong>: 운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다</li>'
  period='2026-02-13 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

## 주요 요약

2026년 02월 13일 기준 보안 현황 및 위협 분석입니다.

### 위험 스코어카드

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```text
+================================================================+
|          2026-02-13 주간 보안 위험 스코어카드                      |
+================================================================+
|                                                                |
|  항목                    위험도   점수    조치 시급도             |
|  ----------------------------------------------------------   |
|  Copilot Studio agent security: █████████░  9/10   [즉시]                |
|  ThreatsDay Bulletin: AI Prompt █████████░  9/10   [즉시]                |
|  ----------------------------------------------------------   |
|  종합 위험 수준: █████████░ HIGH (9.0/10)                         |
|                                                                |
+================================================================+

```
-->
-->

### 경영진 대시보드

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상)
```text
+================================================================+
|        보안 현황 대시보드 - 2026년 02월 13일                         |
+================================================================+
|                                                                |
|  [위협 현황]              [패치 현황]         [컴플라이언스]       |
|  +-----------+           +-----------+      +-----------+      |
|  | Critical 2|           | 적용필요 2|      | 적합   3  |      |
|  | High     0|           | 평가중  0 |      | 검토중  2 |      |
|  | Medium   13|           | 정보참고 1|      | 미대응  0 |      |
|  +-----------+           +-----------+      +-----------+      |
|                                                                |
|  [MTTR 목표]              [금주 KPI]                            |
|  Critical: < 4시간        탐지율: 90%                           |
|  High:     < 24시간       오탐률: 8%                            |
|  Medium:   < 7일          패치 적용률: 50%                      |
|                           SIEM 룰 커버리지: 85%                 |
|                                                                |
+================================================================+

```
-->
-->

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
| 🔒 **Security** | The Hacker News | 구글, 국가 지원 해커들이 Gemini AI를 정찰 및 공격 지원에 활용 중 보고 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Lazarus 캠페인, npm 및 PyPI 생태계에 악성 패키지 삽입 | 🟡 Medium |
| 🔒 **Security** | Microsoft Secur | Copilot Studio 에이전트 보안: 탐지 및 예방 가능한 10대 위험 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | ThreatsDay 불레틴: AI 프롬프트 RCE, Claude 0-클릭 취약점 | 🔴 Critical |
| 🔒 **Security** | Microsoft Secur | RSA에서 만나는 Microsoft 경험 완벽 가이드 | 🟡 Medium |

---

## 1. 보안 뉴스

### 1.1 구글, 국가 지원 해커들이 Gemini AI를 정찰 및 공격 지원에 활용 중 보고

구글, 국가 지원 해커들이 Gemini AI를 정찰 및 공격 지원에 활용 중 보고 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/google-reports-state-backed-hackers.html)

#### 핵심 포인트

- 북한 연계 위협 행위자 UNC2970이 Gemini AI를 정찰 목적으로 활용 중임이 구글에 의해 확인됨
- 다수의 해킹 그룹이 사이버 공격 전 주기(정찰, 사회공학, 악성코드 개발)에 AI를 무기화하는 추세
- 정보 작전 지원 및 모델 추출 공격에도 AI가 활용되고 있어 AI 거버넌스 강화 필요

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

### 1.2 Lazarus 캠페인, npm 및 PyPI 생태계에 악성 패키지 삽입

Lazarus 캠페인, npm 및 PyPI 생태계에 악성 패키지 삽입 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/lazarus-campaign-plants-malicious.html)

#### 핵심 포인트

- 북한 연계 Lazarus 그룹이 가짜 채용 캠페인을 통해 npm 및 PyPI에 악성 패키지를 유포
- 캠페인 코드명 'graphalgo', 2025년 5월부터 활성화된 것으로 분석
- 오픈소스 패키지 생태계를 통한 공급망 공격으로 개발자 환경이 주요 표적

#### 실무 영향

- 의존성 감사(dependency audit) 즉시 실행: `npm audit`, `pip audit`, `bundle audit`
- SBOM(Software Bill of Materials) 최신 상태 확인
- 서드파티 라이브러리 버전 고정 및 무결성 검증(checksum/signature)
- CI/CD 파이프라인의 의존성 스캔 정책 점검

---

### 1.3 Copilot Studio 에이전트 보안: 탐지 및 예방 가능한 10대 위험

Copilot Studio 에이전트 보안: 탐지 및 예방 가능한 10대 위험 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/02/12/copilot-studio-agent-security-top-10-risks-detect-prevent/)

#### 핵심 포인트

- Copilot Studio 에이전트의 강력해진 기능과 함께 보안 위험도 증가
- 잘못된 구성, 과도한 공유, 미인증 접근, 취약한 오케스트레이션 제어가 주요 위험 요인
- Microsoft Defender를 활용한 10대 위험의 실무적 탐지·완화 방법 제시

#### 실무 영향

- 관련 시스템의 인증 정보(Credential) 즉시 로테이션 검토
- MFA(다중 인증) 적용 현황 점검 및 미적용 시스템 식별
- SSO/IdP 로그에서 비정상 인증 시도 모니터링 강화
- 서비스 계정 및 API 키 사용 현황 감사

---

## 2. AI/ML 뉴스

### 2.1 GPT-5.3-Codex-Spark 소개

GPT-5.3-Codex-Spark 소개 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [OpenAI Blog](https://openai.com/index/introducing-gpt-5-3-codex-spark)

#### 핵심 포인트

- OpenAI 최초의 실시간 코딩 특화 모델 GPT-5.3-Codex-Spark 발표
- 기존 모델 대비 15배 빠른 생성 속도, 128k 컨텍스트 지원
- ChatGPT Pro 사용자 대상 리서치 프리뷰로 우선 출시

#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검

---

### 2.2 PFCS Forward 소개

PFCS Forward 소개 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Palantir Blog](https://blog.palantir.com/introducing-pfcs-forward-d8755d34c429?source=rss----3c87dc14372f---4)

#### 핵심 포인트

- PFCS Forward: IL5/IL6 인증을 클라우드에서 전술 엣지까지 확장
- DISA의 DoD 사이버 방어 사령부 요구사항을 충족하는 하드웨어 비종속 인증 방식
- 전술 엣지 환경에서의 보안 인증 부담을 줄이는 실용적 접근 제시

#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검

---

### 2.3 AI와 HR의 만남: Amazon Bedrock으로 채용 방식 혁신

AI와 HR의 만남: Amazon Bedrock으로 채용 방식 혁신 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/ai-meets-hr-transforming-talent-acquisition-with-amazon-bedrock/)

#### 핵심 포인트

- Amazon Bedrock과 AWS Lambda를 활용한 AI 기반 채용 시스템 구축 방법 소개
- 직무 기술서 생성, 지원자 소통, 면접 준비 과정을 AI로 자동화
- 인간 감독(Human Oversight)을 유지하면서 채용 효율성 향상

#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 간소화된 청구와 명확한 절감: 지출 기반 CUD 개선을 위한 FinOps 가이드

간소화된 청구와 명확한 절감: 지출 기반 CUD 개선을 위한 FinOps 가이드 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/cost-management/a-finops-professionals-guide-to-updated-spend-based-cuds/)

#### 핵심 포인트

- 클라우드 비용 절감을 위한 약정 사용 할인(CUD) 모델 업데이트 발표
- Cloud Run, H3/M-series VM 등 신규 SKU로 CUD 적용 범위 확대
- 비용 가시성 개선 및 유연성 향상으로 FinOps 실무 간소화

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

### 3.2 GTIG AI 위협 추적기: 적대적 목적 AI 활용의 정제, 실험, 지속적 통합

GTIG AI 위협 추적기: 적대적 목적 AI 활용의 정제, 실험, 지속적 통합 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/distillation-experimentation-integration-ai-adversarial-use/)

#### 핵심 포인트

- GTIG, 2025년 4분기 위협 행위자의 AI 기반 공격 생명주기 가속화 사례 다수 관찰
- 정찰·사회공학·악성코드 개발 분야에서 AI 활용으로 인한 생산성 향상 확인
- 초기 징후 및 공격적 개념 증명(PoC)을 조기 식별하여 방어 역량 강화 목표

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

### 3.3 VAMS에서 NVIDIA Isaac Lab을 활용한 GPU 가속 로봇 시뮬레이션 훈련

VAMS에서 NVIDIA Isaac Lab을 활용한 GPU 가속 로봇 시뮬레이션 훈련 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [AWS Korea Blog](https://aws.amazon.com/ko/blogs/tech/gpu-accelerated-robotic-simulation-training-with-nvidia-isaac-lab-in-vams/)

#### 핵심 포인트

- 본 게시글은 AWS Spatial Compute Blog에 작성된 “GPU-Accelerated Robotic Simulation Training with NVIDIA Isaac Lab in VAMS” 블로그를 번역했습니다
- 오픈소스 Visual Asset Management System(VAMS)이 이제 NVIDIA Isaac Lab과의 통합을 통해 로봇 자산에 대한 GPU 가속 강화학습(RL)을 지원합니다
- 이 파이프라인을 통해 팀은 자산 관리 워크플로우에서 직접 RL 정책을 훈련하고 평가할 수 있으며, 확장 가능한 GPU 컴퓨팅을 [ ]

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

## 4. DevOps & 개발 뉴스

### 4.1 Interop 2026 발표

Interop 2026 발표 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [WebKit Blog](https://webkit.org/blog/17818/announcing-interop-2026/)

#### 핵심 포인트

- 크로스 브라우저 상호운용성 개선을 목표로 하는 Interop 2026 공식 출범

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

### 4.2 Safari Technology Preview 237 릴리스 노트

Safari Technology Preview 237 릴리스 노트 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [WebKit Blog](https://webkit.org/blog/17842/release-notes-for-safari-technology-preview-237/)

#### 핵심 포인트

- Safari Technology Preview 237, macOS Tahoe 및 macOS Sequoia 대상 릴리스

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

## 5. 블록체인 뉴스

### 5.1 人身売買関連サービスへの暗号資産の資金フローが前年比85%急増

人身売買関連サービスへの暗号資産の資金フローが前年比85%急増 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Chainalysis Blog](https://www.chainalysis.com/blog/crypto-human-trafficking-2026-japanese/)

#### 핵심 포인트

- ※この記事は自動翻訳されています。正確な内容につきましては原文をご参照ください。 要約 主に東南アジアを拠点とする人身売買の疑いがあるサービスへの暗号資産の資金フローは、2025年に85%増加し、特定されたサービス全体で数億ドル規模に達しました。 Telegramベースの「インターナショナルエスコート」サービスは、中国語圏のマネーロンダリングネットワーク（CMLN）や担保プラットフォームと高度に統合されており、トランザクションの約半数が10,000ドルを超えています。 分析により、東南アジアの人身売買組織のグローバルな展開が明らかになり、南北アメリカ、ヨーロッパ、オーストラリアなど各地から多額の暗号資産が流入しています。 児童性的虐待コンテンツ（CSAM）ネットワークはサブスクリプション型モデルへと進化し、サディスティックなオンライン過激主義（SOE）コミュニティとの重複が増加しています。また、米国のインフラを戦略的に利用している点は、高度な運営計画を示唆しています。 現金取引とは異なり、暗号資産が本質的に持つ透明性は、法執行機関やコンプライアンスチームが人身売買の活動を検知、追

---

### 5.2 태국, 규제 파생상품 시장에서 Bitcoin 및 디지털 자산 제도화 추진

태국, 규제 파생상품 시장에서 Bitcoin 및 디지털 자산 제도화 추진 이슈는 시장 신호와 제도 변화가 기술 생태계 의사결정에 연결되는 흐름을 보여줍니다. 단기 변동성보다 규제·유동성·채택 속도를 함께 추적해야 실무 판단의 정확도를 높일 수 있습니다.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/thailand-moves-to-cement-bitcoin)

#### 핵심 포인트

- 태국, 비트코인 및 디지털 자산을 파생상품·자본 시장의 규제 기준 자산으로 공식화 추진
- 아시아 신흥 시장에서의 디지털 자산 제도화 흐름 강화

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [유럽 급증, 미국 부진, 중국 냉각: 2026년 EV 판매 감소](https://electrek.co/2026/02/12/europe-surges-us-stumbles-china-cools-ev-sales-dip-in-2026/) | Electrek | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [워싱턴 DC, 노변 주차 공간이 EV 충전 구역으로](https://electrek.co/2026/02/12/washington-dc-curbside-parking-ev-charging/) | Electrek | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |

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

- [ ] **Copilot Studio agent security: Top 10 risks you can detect a** 관련 긴급 패치 및 영향도 확인
- [ ] **ThreatsDay Bulletin: AI Prompt RCE, Claude 0-Click, RenEngin** 관련 긴급 패치 및 영향도 확인

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
