---
author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-02-11 12:47:26 +0900
description: '2026년 02월 11일 보안 뉴스: The Hacker News 등 26건. 보안, 랜섬웨어, 패치, AI 관련 DevSecOps
  실무 위협 분석 및 대응 가이드.'
excerpt: 2026년 02월 11일 주요 보안/기술 뉴스 26건 - 보안, 랜섬웨어, 패치
image: /assets/images/2026-02-11-Tech_Security_Weekly_Digest_Security_Ransomware_Patch_AI.svg
image_alt: 기술·보안 주간 다이제스트 2026년 2월 11일 보안 랜섬웨어 패치
keywords:
- Security-Weekly
- DevSecOps
- Cloud-Security
- Weekly-Digest
- 2026
- Security
- Ransomware
- Patch
layout: post
tags:
- Security-Weekly
- DevSecOps
- Cloud-Security
- Weekly-Digest
- 2026
- Security
- Ransomware
- Patch
- AI
title: '기술·보안 주간 다이제스트: 랜섬웨어, CVE-2026-21643, Fortinet'
toc: true
---

{% capture ai_categories_html %}
<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>
{% endcapture %}
{% capture ai_tags_html %}
<span class="tag">Security-Weekly</span>
<span class="tag">DevSecOps</span>
<span class="tag">Cloud-Security</span>
<span class="tag">AI-Security</span>
<span class="tag">Zero-Trust</span>
<span class="tag">2026</span>
{% endcapture %}
{% capture ai_highlights_html %}
<li><strong>The Hacker News</strong>: 북한 연계 요원이 LinkedIn에서 전문가 사칭 공격</li>
<li><strong>The Hacker News</strong>: Reynolds 랜섬웨어가 BYOVD 드라이버로 EDR 무력화</li>
<li><strong>The Hacker News</strong>: 랜섬웨어가 이주/거주권 사기로 확장되는 흐름</li>
<li><strong>Google Cloud Blog</strong>: 분산 클라우드로 퍼블릭 클라우드 수준 운영 경험 제공</li>
{% endcapture %}

{% include ai-summary-card.html
  title="기술·보안 주간 다이제스트 (2026년 02월 11일)"
  categories_html=ai_categories_html
  tags_html=ai_tags_html
  highlights_html=ai_highlights_html
  period="2026년 02월 11일 (24시간)"
  audience="보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
%}

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
| 🔒 **Security** | The Hacker News | 북한 연계 IT 요원, LinkedIn 전문가 사칭으로 기업 침투 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Reynolds 랜섬웨어, BYOVD 드라이버 내장으로 EDR 무력화 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 랜섬웨어에서 장기 잠복으로: 디지털 기생 공격의 부상 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | Fortinet, 미인증 접근 허용 Critical SQLi 취약점 패치 (CVE-2026-21643) | 🔴 Critical |
| 🔒 **Security** | The Hacker News | ZAST.AI, "제로 오탐" AI 보안 플랫폼으로 600만 달러 Pre-A 조달 | 🟠 High |

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. 보안 뉴스

### 1.1 북한 연계 IT 요원, LinkedIn에서 전문가 사칭으로 기업 침투

#### 개요

북한(DPRK) 연계 IT 요원들이 실제 인물의 LinkedIn 계정을 도용해 원격 채용 공고에 지원하는 새로운 사기 수법이 포착되었습니다. 이들은 인증된 직장 이메일과 신원 배지를 갖춘 프로필을 활용해 채용 담당자의 검증을 우회하는 방식으로 공격을 고도화하고 있습니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/dprk-operatives-impersonate.html)

#### 핵심 포인트

- 실존 인물의 LinkedIn 계정을 탈취·도용해 원격 근무 포지션에 직접 지원하는 방식으로 이전보다 탐지 회피가 어려워짐
- 인증된 이메일·신원 배지를 갖춘 프로필로 채용 심사를 통과 후 내부 시스템 접근권 확보 시도


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | Medium |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |

#### 권장 조치

- [ ] HR 및 채용팀에 LinkedIn 계정 도용 사칭 수법 공유 및 신원 검증 절차 강화
- [ ] 원격 채용 후보자에 대해 화상 면접 필수화 및 공식 이메일 도메인 외 연락처 이중 확인
- [ ] 신규 채용자 온보딩 시 최소 권한 원칙 적용 및 초기 접근 범위 제한
- [ ] 내부 시스템에 대한 신규 계정 활동 모니터링 룰 SIEM에 추가


---

### 1.2 Reynolds 랜섬웨어, BYOVD 드라이버 내장으로 EDR 무력화

#### 개요

새로운 랜섬웨어 패밀리 "Reynolds"가 페이로드 자체에 BYOVD(Bring Your Own Vulnerable Driver) 컴포넌트를 내장해 배포 단계부터 EDR을 무력화하는 방식을 채택한 것으로 밝혀졌습니다. 취약한 정상 드라이버를 악용해 권한을 상승시키고 엔드포인트 탐지를 비활성화한 뒤 랜섬웨어를 실행합니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/reynolds-ransomware-embeds-byovd-driver.html)

#### 핵심 포인트

- BYOVD 컴포넌트가 랜섬웨어 페이로드에 통합되어 있어, EDR이 동작 중인 환경에서도 실행 초기에 보안 솔루션을 우회할 수 있음
- 정상 드라이버 서명을 악용하므로 커널 수준의 드라이버 허용 목록(Block List) 관리와 취약 드라이버 차단 정책이 핵심 방어 수단


#### 권장 조치

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인


---

### 1.3 랜섬웨어에서 장기 잠복으로: 디지털 기생 공격의 부상

#### 개요

Picus Labs의 Red Report 2026에 따르면, 2025년 한 해 동안 110만 개 이상의 악성 파일과 1,550만 건의 적대적 행동을 분석한 결과, 공격자들이 랜섬웨어와 암호화 방식에서 탈피해 탐지 없이 장기간 시스템에 잠복하는 "거주(residency)" 전략으로 전환하고 있는 추세가 확인되었습니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/from-ransomware-to-residency-inside.html)

#### 핵심 포인트

- 공격자들이 즉각적인 수익화(랜섬웨어)보다 장기 잠복·데이터 수집에 집중하는 방향으로 전략 변화 중
- Picus Labs Red Report 2026: 1.1M 악성 파일·15.5M 행동 분석 기반으로 "디지털 기생" 패턴이 주요 위협으로 부상


#### 권장 조치

- 백업 시스템 정상 동작 여부 즉시 검증 (오프라인 백업 포함)
- 인시던트 대응 플레이북 점검 및 랜섬웨어 시나리오 확인
- 네트워크 세그멘테이션 상태 확인 및 횡적 이동 차단 검토
- EDR/XDR 솔루션의 랜섬웨어 탐지 정책 최신 상태 확인


---

![AI ML News Section Banner](/assets/images/section-ai-ml.svg)

## 2. AI/ML 뉴스

### 2.1 Google Photos "Ask Photos" 기능 활용 가이드

#### 개요

Google Photos의 AI 기반 질의 기능 "Ask Photos"를 활용해 사진 컬렉션에서 정보를 검색하고 인사이트를 얻는 9가지 실용적인 질문 유형을 소개합니다.

> **출처**: [Google AI Blog](https://blog.google/products-and-platforms/products/photos/ask-button-ask-photos-tips/)

#### 핵심 포인트

- 자연어로 사진 라이브러리를 검색·분석할 수 있는 생성형 AI 기능으로, 위치·날짜·인물 등 복합 조건 질의 지원
- 개인 사진 데이터에 AI가 접근하는 방식이므로, 프라이버시 설정 및 데이터 처리 범위 확인 필요


---

### 2.2 Amazon Nova로 물류 센터 운영 준비 자동 검증

#### 개요

Amazon이 신규 물류 센터 개소 시 Amazon Bedrock의 Nova 모델을 활용해 모듈 컴포넌트 탐지·검증을 자동화한 사례를 소개합니다. AI 기반 이미지 인식으로 수동 검증 작업 부담을 크게 줄이고 정확도를 향상시켰습니다.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/how-amazon-uses-amazon-nova-models-to-automate-operational-readiness-testing-for-new-fulfillment-centers/)

#### 핵심 포인트

- Amazon Bedrock 기반 이미지 인식 AI로 물류 모듈 상태 자동 검증, 수동 점검 시간 대폭 단축
- 운영 환경의 AI 검증 자동화는 검증 데이터 무결성 보장과 모델 드리프트 모니터링이 병행되어야 실효성 확보 가능


---

### 2.3 Iberdrola, Amazon Bedrock AgentCore로 IT 운영 고도화

#### 개요

세계 최대 전력 기업 중 하나인 Iberdrola가 AWS와의 협력으로 ServiceNow IT 운영에 Amazon Bedrock AgentCore 기반 에이전틱 아키텍처를 도입했습니다. 변경 요청 검증, 인시던트 관리 지능화, 변경 모델 선택 자동화 3개 영역에서 효율을 크게 높였습니다.

> **출처**: [AWS Machine Learning Blog](https://aws.amazon.com/blogs/machine-learning/iberdrola-enhances-it-operations-using-amazon-bedrock-agentcore/)

#### 핵심 포인트

- 변경 요청 초안 단계 검증 자동화, 인시던트에 맥락 정보 자동 보강, 대화형 AI로 변경 모델 선택 지원 등 3가지 에이전틱 워크플로우 구현
- 에너지 인프라 운영에 AI 에이전트 도입 시 장애 전파 방지를 위한 롤백 기준과 에이전트 행동 감사 로그 설계가 필수


---

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 3. 클라우드 & 인프라 뉴스

### 3.1 Google Distributed Cloud, air-gapped 환경에 퍼블릭 클라우드급 네트워킹 제공

#### 개요

Organizations in highly regulated industries often struggle to balance the rigid security of air-gapped environments with the need for the agility and flexibility that the cloud provides. To address this, Google Distributed Cloud (GDC) air-gapped 1.15 introduces new networking features in preview that give you more direct control and visibility without compromising your security posture, as well as a new IPAM feature in general availability that simplifies subnet management . These preview fe...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/networking/google-distributed-cloud-gdc-air-gapped-1-15-networking/)

#### 핵심 포인트

- Organizations in highly regulated industries often struggle to balance the rigid security of air-gapped environments with the need for the agility and flexibility that the cloud provides
- To address this, Google Distributed Cloud (GDC) air-gapped 1.15 introduces new networking features in preview that give you more direct control and visibility without compromising your security posture, as well as a new IPAM feature in general availability that simplifies subnet management
- These preview fe


#### 실무 적용 포인트

- GDC air-gapped 환경에서 신규 IPAM 기능 적용 시 기존 서브넷 할당 체계와 충돌 여부를 사전에 점검하고 IP 플랜 재정비
- air-gapped 네트워크의 외부 연결 경로(관리 인터페이스, 업데이트 채널)를 재검토해 의도치 않은 망 개방 여부 확인


---

### 3.2 Gemini Enterprise Agent Ready(GEAR) 프로그램 공개 — 대규모 AI 에이전트 구축 경로 제시

#### 개요

Today’s reality is agentic – software that can reason, plan, and act on your behalf to execute complex workflows. To meet this moment, we are excited to open the Gemini Enterprise Agent Ready (GEAR) learning program to everyone. As a new specialized pathway within the Google Developer Program , GEAR empowers developers and pros to build and deploy enterprise-grade agents with Google AI. Here is how GEAR helps you build what’s next. Move from experimentation to production-ready architecture Bu...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/gear-program-now-available/)

#### 핵심 포인트

- Today’s reality is agentic – software that can reason, plan, and act on your behalf to execute complex workflows
- To meet this moment, we are excited to open the Gemini Enterprise Agent Ready (GEAR) learning program to everyone
- As a new specialized pathway within the Google Developer Program , GEAR empowers developers and pros to build and deploy enterprise-grade agents with Google AI
- Here is how GEAR helps you build what’s next


#### 실무 적용 포인트

- 엔터프라이즈 에이전트 도입 전 권한 범위(scope)와 데이터 접근 경계를 명시적으로 정의하고 최소 권한 원칙 적용
- GEAR 기반 에이전트가 처리하는 민감 데이터의 로깅·감사 정책을 수립하고, 프롬프트 인젝션 대응 테스트 시나리오 마련


---

### 3.3 전장을 넘어: 방위산업 기반(DIB)을 겨냥한 사이버 위협

#### 개요

Introduction In modern warfare, the front lines are no longer confined to the battlefield; they extend directly into the servers and supply chains of the industry that safeguards the nation. Today, the defense sector faces a relentless barrage of cyber operations conducted by state-sponsored actors and criminal groups alike. In recent years, Google Threat Intelligence Group (GTIG) has observed several distinct areas of focus in adversarial targeting of the defense industrial base (DIB). While...

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/threats-to-defense-industrial-base/)

#### 핵심 포인트

- Introduction In modern warfare, the front lines are no longer confined to the battlefield; they extend directly into the servers and supply chains of the industry that safeguards the nation
- Today, the defense sector faces a relentless barrage of cyber operations conducted by state-sponsored actors and criminal groups alike
- In recent years, Google Threat Intelligence Group (GTIG) has observed several distinct areas of focus in adversarial targeting of the defense industrial base (DIB)


#### 실무 적용 포인트

- 방산·공공 분야 공급망에 포함된 3rd-party 벤더와 협력사의 보안 수준을 평가하고, 고위험 벤더에는 추가 접근 제어 및 감사 요건 부과
- MITRE ATT&CK for ICS 프레임워크를 참조해 OT/IT 경계에서 국가 배후 위협 그룹의 TTP에 대응하는 탐지 룰을 SIEM에 추가
- 내부 직원 대상 스피어피싱·사회공학 시뮬레이션 훈련 주기를 단축하고, 방산 관련 자격증·접근 권한 보유자를 우선 대상으로 실시


---

![DevOps Platform News Section Banner](/assets/images/section-devops.svg)

## 4. DevOps & 개발 뉴스

### 4.1 Docker Hardened Images 무료 제공 — 이제 무엇을 해야 하나?

#### 개요

Docker Hardened Images are now free, covering Alpine, Debian, and over 1,000 images including databases, runtimes, and message buses. For security teams, this changes the economics of container vulnerability management. DHI includes security fixes from Docker’s security team, which simplifies security response. Platform teams can pull the patched base image and redeploy quickly. But free...

> **출처**: [Docker Blog](https://www.docker.com/blog/hardened-images-free-now-what/)

#### 핵심 포인트

- Docker Hardened Images are now free, covering Alpine, Debian, and over 1,000 images including databases, runtimes, and message buses
- For security teams, this changes the economics of container vulnerability management
- DHI includes security fixes from Docker’s security team, which simplifies security response
- Platform teams can pull the patched base image and redeploy quickly


#### 실무 적용 포인트

- 현재 운영 중인 컨테이너 이미지 레지스트리를 전수 조사해 일반 베이스 이미지를 Docker Hardened Images(DHI)로 교체하는 마이그레이션 계획 수립
- CI/CD 파이프라인에 `docker scout cves` 또는 Trivy 스캔 단계를 추가해 DHI 전환 후에도 신규 취약점이 빌드 시점에 탐지되도록 설정
- Dockerfile의 `FROM` 태그를 고정 다이제스트(`@sha256:...`) 방식으로 변경해 공급망 공격(이미지 교체)에 대한 무결성 보장


---

### 4.2 .NET 11 Preview 1 출시

#### 개요

.NET 11 Preview 1이 공개되었습니다. .NET 런타임, SDK, 라이브러리, ASP.NET Core, Blazor, C#, .NET MAUI 전반에 걸친 신규 기능이 포함되었으며, 정식 출시 전 얼리 어답터 피드백 수집 단계입니다.

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/dotnet-11-preview-1/)

#### 핵심 포인트

- .NET 11 Preview 1: 런타임 성능 개선, ASP.NET Core 인증 미들웨어 변경, C# 신규 언어 기능 포함
- Preview 단계이므로 프로덕션 적용 전 Breaking Changes 목록을 공식 문서에서 확인하고 호환성 테스트 선행 필요


#### 실무 적용 포인트

- .NET 11 Preview는 프로덕션 투입 전 단계이므로 현재 .NET 9/10 기반 서비스의 호환성 매트릭스를 작성하고, Breaking Changes 항목을 미리 추적
- ASP.NET Core 신규 보안 API(예: 인증 미들웨어 변경, 암호화 기본값 업데이트) 항목을 식별해 기존 코드베이스에 미치는 영향도 평가


---

### 4.3 .NET / .NET Framework 2026년 2월 서비스 업데이트

> 🟡 **심각도**: Medium | **CVE**: CVE-2026-21218

#### 개요

Microsoft가 2026년 2월 .NET 및 .NET Framework 최신 서비스 업데이트를 발표했습니다. CVE-2026-21218을 포함한 보안 패치와 안정성 수정 사항이 포함되어 있으며, 지원 중인 모든 .NET 버전에 대한 업데이트가 제공됩니다.

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/dotnet-and-dotnet-framework-february-2026-servicing-updates/)

#### 핵심 포인트

- CVE-2026-21218 보안 패치 포함: .NET 및 .NET Framework 지원 버전 전체에 해당하므로 즉시 적용 검토 필요
- .NET Framework 4.x 레거시 환경은 WSUS/SCCM 경로로 KB 번호를 확인해 배포 정책에 반영


#### 실무 적용 포인트

- CVE-2026-21218 영향을 받는 .NET/.NET Framework 버전을 인벤토리에서 식별하고, 30일 내 패치 적용 일정을 확정
- .NET Framework 레거시 버전(4.x)을 운영 중인 경우 Microsoft Update Catalog에서 해당 KB 번호를 확인해 WSUS/SCCM 배포 정책에 즉시 포함


---

![Blockchain Web3 News Section Banner](/assets/images/section-blockchain.svg)

## 5. 블록체인 뉴스

### 5.1 Goldman Sachs, 비트코인 ETF 11억 달러 보유 공시

#### 개요

Goldman Sachs가 SEC 공시를 통해 비트코인 ETF에 11억 달러 규모의 포지션을 보유하고 있음을 밝혔습니다. 전통 금융 대형 기관의 암호화폐 노출이 확대되는 추세를 보여주는 사례입니다.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/goldman-sachs-position-in-bitcoin)

#### 핵심 포인트

- Goldman Sachs가 비트코인 현물 ETF에 11억 달러 투자 공시, 기관 자금 유입 가속화 신호
- 대형 기관의 ETF 보유는 암호화폐 시장 안정성에 긍정적 영향을 줄 수 있으나, 규제 변화에 따른 동반 매도 리스크도 동시에 증가


---

### 5.2 FTX 샘 뱅크먼-프리드, 재심 신청 — "바이든 행정부의 정치적 피해자" 주장

#### 개요

FTX 사기 혐의로 유죄 판결을 받은 샘 뱅크먼-프리드가 재심을 신청했습니다. 그는 자신의 기소가 바이든 행정부의 정치적 동기에 의한 것이라고 주장하며 판결 취소를 시도하고 있습니다.

> **출처**: [Bitcoin Magazine](https://bitcoinmagazine.com/news/ftx-sam-bankman-fried-wants-a-new-trial)

#### 핵심 포인트

- 뱅크먼-프리드의 재심 신청은 암호화폐 업계의 규제 집행 투명성과 정치적 독립성 문제를 다시 수면 위로 올림
- FTX 사태는 중앙화 거래소의 자산 분리 의무와 감사 체계 부재가 핵심 원인이었으며, 업계 전반의 규제 강화 논의에 영향 지속


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Trump can’t freeze NEVI funds, so he’s trying to s...](https://electrek.co/2026/02/10/trump-cant-freeze-nevi-funds-so-hes-trying-to-stall-them-again/) | Electrek | The Federal Highway Administration (FHWA) just issued a new notice today that ai... |
| [Tesla Semi specs and pricing, L4 haul trucks, and ...](https://electrek.co/2026/02/10/tesla-semi-specs-and-pricing-l4-haul-trucks-and-windrose-mobile-ai-concept/) | Electrek | On today’s long overdue episode of Quick Charge , we’ve finally got production s... |


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

- [ ] **Fortinet CVE-2026-21643** (Critical SQLi — 미인증 접근 허용): 영향받는 FortiOS/FortiProxy 버전 인벤토리 확인 후 긴급 패치 적용 또는 임시 완화 조치(WAF 룰, 관리 인터페이스 접근 제한) 시행

### P1 (7일 내)

- [ ] **ZAST.AI "Zero False Positive" AI 보안 플랫폼**: 기존 SAST/DAST 도구와의 중복·연동 가능성 검토 및 POC 계획 수립
- [ ] **Google Distributed Cloud GDC air-gapped 1.15 신규 네트워킹 기능**: 적용 예정 환경의 IPAM 충돌 여부 사전 점검 및 air-gapped 경계 재검토

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
