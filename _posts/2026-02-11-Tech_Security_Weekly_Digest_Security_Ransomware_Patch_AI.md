---
layout: post
title: "기술 & 보안 주간 다이제스트: 랜섬웨어, CVE-2026-21643, Fortinet"
date: 2026-02-11 12:47:26 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Ransomware, Patch, AI]
excerpt: "2026년 02월 11일 주요 보안/기술 뉴스 26건 - Security, Ransomware, Patch"
description: "2026년 02월 11일 보안 뉴스: The Hacker News 등 26건. Security, Ransomware, Patch, AI 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Security, Ransomware, Patch]
author: Twodragon
comments: true
image: /assets/images/2026-02-11-Tech_Security_Weekly_Digest_Security_Ransomware_Patch_AI.svg
image_alt: "기술 보안 주간 다이제스트 2026년 2월 11일 랜섬웨어 패치"
toc: true
schema_type: Article
---

{% include ai-summary-card.html
  title='기술 &amp; 보안 주간 다이제스트: 랜섬웨어, CVE-2026-21643, Fortinet'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">Weekly-Digest</span> <span class="tag">2026</span> <span class="tag">Security</span> <span class="tag">Ransomware</span> <span class="tag">Patch</span>'
  highlights_html='<li><strong>포인트 1</strong>: 2026년 02월 11일 주요 보안/기술 뉴스 26건 - Security, Ransomware, Patch</li> <li><strong>포인트 2</strong>: 실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다</li> <li><strong>포인트 3</strong>: 운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다</li>'
  period='2026-02-11 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

## 주요 요약

2026년 02월 11일 기준 보안 현황 및 위협 분석입니다.

### 위험 스코어카드

```text
+================================================================+
|          2026-02-11 주간 보안 위험 스코어카드                      |
+================================================================+
|                                                                |
|  항목                    위험도   점수    조치 시급도             |
|  ----------------------------------------------------------   |
|  Fortinet Patches Critical SQLi █████████░  9/10   [즉시]                |
|  ZAST.AI Raises $6M Pre-A to Sc ███████░░░  7/10   [7일 이내]             |
|  Google Distributed Cloud bring ███████░░░  7/10   [7일 이내]             |
|  ----------------------------------------------------------   |
|  종합 위험 수준: ███████░░░ HIGH (7.7/10)                         |
|                                                                |
+================================================================+
```

### 경영진 대시보드

```text
+================================================================+
|        보안 현황 대시보드 - 2026년 02월 11일                         |
+================================================================+
|                                                                |
|  [위협 현황]              [패치 현황]         [컴플라이언스]       |
|  +-----------+           +-----------+      +-----------+      |
|  | Critical 1|           | 적용필요 1|      | 적합   3  |      |
|  | High     2|           | 평가중  2 |      | 검토중  2 |      |
|  | Medium   12|           | 정보참고 1|      | 미대응  0 |      |
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

### 이사회 보고 포인트

| 항목 | 내용 | 조치 상태 |
|------|------|----------|
| **주요 위협** | Critical: 1건, High: 2건 | 대응 진행 중 |
| **패치 적용** | 긴급 패치 대상 시스템 식별 완료 | 검토 필요 |
| **규제 대응** | 보안 정책 및 컴플라이언스 점검 | 정상 |

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 02월 11일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 26개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 4개
- **클라우드 뉴스**: 4개
- **DevOps 뉴스**: 3개
- **블록체인 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | DPRK 요원들이 LinkedIn에서 전문직을 사칭해 기업 침투 시도 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Reynolds 랜섬웨어, BYOVD 드라이버 내장으로 EDR 보안 도구 무력화 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 랜섬웨어에서 장기 잠복으로: 디지털 기생 공격의 부상 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Fortinet, 미인증 원격 코드 실행 가능한 Critical SQLi 취약점 패치 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | ZAST.AI, "제로 오탐" AI 보안 플랫폼 확장을 위해 600만 달러 Pre-A 투자 유치 | 🟠 High |

---

## 1. 보안 뉴스

### 1.1 DPRK 요원들의 LinkedIn 전문직 사칭 기업 침투 시도

DPRK 요원들의 LinkedIn 전문직 사칭 기업 침투 시도 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/dprk-operatives-impersonate.html)

#### 핵심 포인트

- 북한(DPRK) 연계 IT 인력들이 타인의 실제 LinkedIn 계정을 도용해 원격 직위에 지원하는 신종 사기 수법이 확인됨
- 인증된 직장 이메일과 신원 배지가 포함된 프로필로 채용 심사를 통과하려는 시도가 포착됨

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

### 1.2 Reynolds 랜섬웨어, BYOVD 드라이버 내장으로 EDR 보안 도구 무력화

Reynolds 랜섬웨어, BYOVD 드라이버 내장으로 EDR 보안 도구 무력화 이슈는 공격 성립 조건과 영향 범위를 함께 보여주며 우선 대응 대상을 빠르게 식별하게 합니다. 실무에서는 노출 자산 식별, 패치 우선순위, 탐지 룰 갱신을 동일 주기에 묶어 처리해야 합니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/reynolds-ransomware-embeds-byovd-driver.html)

#### 핵심 포인트

- 신종 랜섬웨어 'Reynolds'가 페이로드 내 BYOVD 컴포넌트를 내장해 방어 우회 목적으로 활용한다는 사실이 밝혀짐
- BYOVD는 취약한 정품 드라이버를 악용해 권한을 상승시키고 EDR(엔드포인트 탐지 및 대응) 도구를 비활성화하는 기술임

#### 실무 영향

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인

---

### 1.3 랜섬웨어에서 장기 잠복으로: 디지털 기생 공격의 부상

랜섬웨어에서 장기 잠복으로: 디지털 기생 공격의 부상 이슈는 공격 성립 조건과 영향 범위를 함께 보여주며 우선 대응 대상을 빠르게 식별하게 합니다. 실무에서는 노출 자산 식별, 패치 우선순위, 탐지 룰 갱신을 동일 주기에 묶어 처리해야 합니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/from-ransomware-to-residency-inside.html)

#### 핵심 포인트

- 랜섬웨어·암호화 중심의 공격 패러다임이 장기 잠복·은밀한 내부 정착 방식으로 전환되고 있다는 분석이 제기됨
- Picus Labs Red Report 2026은 110만+ 악성 파일 및 2025년 관측된 1,550만 건 공격 행위 분석 결과를 기반으로 이 추세를 확인함

#### 실무 영향

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인

---

## 2. AI/ML 뉴스

### 2.1 Google Photos에 물어볼 만한 재미있는 질문 9가지

Google Photos에 물어볼 만한 재미있는 질문 9가지 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Google AI Blog](https://blog.google/products-and-platforms/products/photos/ask-button-ask-photos-tips/)

#### 핵심 포인트

- Google Photos의 'Ask Photos' 기능을 통해 자연어로 사진을 검색하고 다양한 질문에 답을 얻을 수 있는 활용 사례 소개

#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검

---

### 2.2 Amazon Nova 모델로 신규 물류 센터 운영 준비 테스트 자동화하기

Amazon Nova 모델로 신규 물류 센터 운영 준비 테스트 자동화하기 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/how-amazon-uses-amazon-nova-models-to-automate-operational-readiness-testing-for-new-fulfillment-centers/)

#### 핵심 포인트

- Amazon Bedrock의 Amazon Nova 모델로 AI 기반 이미지 인식 솔루션을 구현해 물류 센터 모듈 구성 요소 감지·검증을 자동화함
- 수작업 검증 노력을 대폭 절감하고 정확도를 향상시킨 실제 사례 공유

#### AI/ML 보안 영향 분석

- **모델 보안**: AI 모델 무결성 및 적대적 공격 대응 현황 점검
- **데이터 보안**: 학습 데이터 및 추론 파이프라인 보안 검토 필요
- **거버넌스**: AI 모델 배포 전 보안 평가 체크리스트 확인

#### 실무 적용

- AI/ML 파이프라인 보안 점검 항목 검토
- 모델 입출력 검증 로직 추가 검토
- AI 거버넌스 프레임워크 대비 현황 점검

---

### 2.3 Iberdrola, Amazon Bedrock AgentCore로 IT 운영 고도화

Iberdrola, Amazon Bedrock AgentCore로 IT 운영 고도화 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/iberdrola-enhances-it-operations-using-amazon-bedrock-agentcore/)

#### 핵심 포인트

- Iberdrola가 Amazon Bedrock AgentCore 기반 에이전트 아키텍처를 ServiceNow IT 운영에 도입해 혁신을 추진함
- 변경 요청 검증 자동화, 인시던트 관리 지능화, 대화형 AI 기반 변경 모델 선택 간소화 등 세 가지 핵심 영역에서 성과를 달성함

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

### 3.1 Google Distributed Cloud, 에어갭 환경에 퍼블릭 클라우드급 네트워킹 제공

Google Distributed Cloud, 에어갭 환경에 퍼블릭 클라우드급 네트워킹 제공 업데이트는 인프라 변경이 안정성·비용·보안 통제에 어떤 영향을 주는지 확인할 수 있는 사례입니다. 적용 전에는 대상 서비스, 롤백 경로, 관측 지표를 사전에 고정해 운영 리스크를 낮춰야 합니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/networking/google-distributed-cloud-gdc-air-gapped-1-15-networking/)

#### 핵심 포인트

- 고규제 산업에서 에어갭 환경의 보안성과 클라우드의 유연성을 동시에 충족하기 위한 새로운 접근법이 제시됨
- GDC 에어갭 1.15에서 보안 태세를 유지하며 직접적인 제어·가시성을 높이는 네트워킹 기능(프리뷰)과 서브넷 관리 간소화를 위한 IPAM 기능(GA)이 추가됨

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

### 3.2 Gemini Enterprise Agent Ready (GEAR) 프로그램 전면 개방, 엔터프라이즈 AI 에이전트 구축의 새 길

Gemini Enterprise Agent Ready (GEAR) 프로그램 전면 개방, 엔터프라이즈 AI 에이전트 구축의 새 길 주제는 AI 기능 확장이 개발·운영 절차에 미치는 변화를 구체적으로 드러냅니다. 팀은 성능 지표와 함께 모델 거버넌스, 데이터 보호, 배포 검증 기준을 동시에 확정해야 합니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/gear-program-now-available/)

#### 핵심 포인트

- 에이전트 기반 소프트웨어(추론·계획·실행)가 현대 IT의 핵심으로 부상하고 있음
- GEAR 프로그램이 전면 개방되어 누구나 엔터프라이즈급 AI 에이전트 구축·배포 역량을 학습할 수 있게 됨
- Google Developer Program 내 전문 경로로 실험에서 프로덕션 아키텍처까지 단계적으로 지원함

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

### 3.3 전장을 넘어서: 방산 산업 기반을 노리는 위협

전장을 넘어서: 방산 산업 기반을 노리는 위협 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/threats-to-defense-industrial-base/)

#### 핵심 포인트

- 현대 전쟁의 전선이 물리적 전장에서 방산 기업의 서버와 공급망으로 확대됨
- 국가 지원 행위자 및 범죄 집단이 방산 산업 기반(DIB)을 집중 표적으로 삼고 있으며, GTIG가 주요 공격 패턴을 관측함

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

## 4. DevOps & 개발 뉴스

### 4.1 Docker Hardened Images 무료 제공 이후, 이제 어떻게 활용할까?

Docker Hardened Images 무료 제공 이후, 이제 어떻게 활용할까? 업데이트는 인프라 변경이 안정성·비용·보안 통제에 어떤 영향을 주는지 확인할 수 있는 사례입니다. 적용 전에는 대상 서비스, 롤백 경로, 관측 지표를 사전에 고정해 운영 리스크를 낮춰야 합니다.

> **출처**: [Docker Blog](https://www.docker.com/blog/hardened-images-free-now-what/)

#### 핵심 포인트

- Docker Hardened Images가 무료 제공으로 전환되어 Alpine, Debian 등 1,000개 이상의 이미지(DB, 런타임, 메시지 버스 포함)를 지원함
- 보안팀의 컨테이너 취약점 관리 비용 구조가 변화하며, Docker 보안팀의 수정 사항이 포함되어 보안 대응이 간소화됨
- 플랫폼 팀은 패치된 베이스 이미지를 가져와 빠르게 재배포 가능

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

### 4.2 .NET 11 Preview 1 출시

.NET 11 Preview 1 출시 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/dotnet-11-preview-1/)

#### 핵심 포인트

- .NET 11 Preview 1에서 .NET 런타임, SDK, 라이브러리, ASP.NET Core, Blazor, C#, .NET MAUI 등 주요 컴포넌트의 신규 기능 공개

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

### 4.3 .NET 및 .NET Framework 2026년 2월 서비스 업데이트

.NET 및 .NET Framework 2026년 2월 서비스 업데이트 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-february-2026-servicing-updates/)

#### 핵심 포인트

- .NET 및 .NET Framework의 2026년 2월 서비스 업데이트 요약 제공
- CVE-2026-21218 관련 보안 패치 포함

#### 실무 적용 포인트

- 기존 인프라/운영 환경과의 호환성 및 영향도 검토
- 테스트 환경에서 먼저 검증 후 프로덕션 적용 계획 수립
- 팀 내 기술 공유 및 도입 로드맵 논의

---

## 5. 블록체인 뉴스

### 5.1 Goldman Sachs, 비트코인 ETF에 11억 달러 포지션 보유 공시

Goldman Sachs, 비트코인 ETF에 11억 달러 포지션 보유 공시 이슈는 시장 신호와 제도 변화가 기술 생태계 의사결정에 연결되는 흐름을 보여줍니다. 단기 변동성보다 규제·유동성·채택 속도를 함께 추적해야 실무 판단의 정확도를 높일 수 있습니다.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/goldman-sachs-position-in-bitcoin)

#### 핵심 포인트

- Goldman Sachs가 비트코인 ETF에 약 11억 달러 규모 포지션 보유를 공식 공시함
- 글로벌 투자은행의 암호화폐 시장 진입 확대를 보여주는 사례로 주목됨

---

### 5.2 FTX Sam Bankman-Fried, 재심 신청 - 바이든 행정부의 정치적 피해자 주장

FTX Sam Bankman-Fried, 재심 신청 - 바이든 행정부의 정치적 피해자 주장 관련 변화는 기술 도입의 배경과 적용 포인트를 빠르게 파악하는 데 유효한 정보입니다. 실무 적용 전 기대 효과와 운영 리스크를 같은 기준으로 비교해 우선순위를 결정해야 합니다.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/ftx-sam-bankman-fried-wants-a-new-trial)

#### 핵심 포인트

- FTX 사기 혐의로 유죄 판결을 받은 Sam Bankman-Fried가 재심 신청서를 제출함
- 바이든 행정부의 정치적 피해자였다고 주장하며 재판 무효화를 요구함

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Trump can’t freeze NEVI funds, so he’s trying to s](https://electrek.co/2026/02/10/trump-cant-freeze-nevi-funds-so-hes-trying-to-stall-them-again/) | Electrek | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |
| [Tesla Semi specs and pricing, L4 haul trucks, and](https://electrek.co/2026/02/10/tesla-semi-specs-and-pricing-l4-haul-trucks-and-windrose-mobile-ai-concept/) | Electrek | 적용 효과와 운영 리스크를 함께 비교해 도입 우선순위를 판단해야 하는 기술 동향입니다. |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 12건 | ai |
| **Cloud Security** | 2건 | cloud, aws |
| **Ransomware** | 2건 | ransomware |
| **Supply Chain** | 1건 | supply chain |
| **Container/K8s** | 1건 | container |
| **Authentication** | 1건 | identity |

이번 주기에서 가장 많이 언급된 트렌드는 **AI/ML** (12건)입니다. 그 다음으로 **Cloud Security** (2건)이 주목받고 있습니다. 실무에서는 해당 트렌드와 관련된 보안 정책 및 모니터링 체계를 점검하시기 바랍니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Fortinet Patches Critical SQLi Flaw Enabling Unauthenticated** (CVE-2026-21643) 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **ZAST.AI Raises $6M Pre-A to Scale "Zero False Positive" AI-P** 관련 보안 검토 및 모니터링
- [ ] **Google Distributed Cloud brings public-cloud-like networking** 관련 보안 검토 및 모니터링

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
