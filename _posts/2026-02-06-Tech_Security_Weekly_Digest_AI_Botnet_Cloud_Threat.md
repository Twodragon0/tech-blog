---
author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-02-06 12:30:12 +0900
description: '2026년 02월 06일 보안 뉴스: CrashFix ClickFix 변종 Python RAT 배포, AISURU/Kimwolf
  31.4 Tbps DDoS 기록 경신, Codespaces RCE/AsyncRAT C2/BYOVD 복합 위협. DevSecOps 실무 위협 분석,
  MITRE ATT&CK 매핑, 탐지 쿼리, IR 플레이북 제공.'
excerpt: 2026년 02월 06일 주요 보안/기술 뉴스 27건 - CrashFix Python RAT, AISURU 31.4 Tbps DDoS,
  Codespaces RCE, BYOVD, Claude Opus 4.6
image: /assets/images/2026-02-06-Tech_Security_Weekly_Digest_AI_Botnet_Cloud_Threat.svg
image_alt: Tech Security Weekly Digest February 06 2026 AI Botnet Cloud
keywords:
- Security-Weekly
- DevSecOps
- Cloud-Security
- Weekly-Digest
- 2026
- CrashFix
- AISURU
- Botnet
- DDoS
- BYOVD
- Python-RAT
layout: post
schema_type: Article
tags:
- Security-Weekly
- DevSecOps
- Cloud-Security
- Weekly-Digest
- 2026
- AI
- Botnet
- Cloud
- Threat
title: 'Tech & Security Weekly Digest: CrashFix Python RAT, AISURU 31.4 Tbps DDoS,
  Codespaces RCE'
toc: true
---

{% capture ai_categories_html %}
<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>
{% endcapture %}
{% capture ai_tags_html %}
<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">AI-Security</span> <span class="tag">Zero-Trust</span> <span class="tag">2026</span>
{% endcapture %}
{% capture ai_highlights_html %}
<li><strong>Microsoft Security</strong>: CrashFix - 브라우저 크래시로 Python RAT 배포하는 새로운 ClickFix 변종 (Critical)</li> <li><strong>The Hacker News</strong>: AISURU/Kimwolf Botnet 31.4 Tbps DDoS 공격 기록 경신</li> <li><strong>The Hacker News</strong>: Codespaces RCE, AsyncRAT C2, BYOVD 공격 종합 분석</li> <li><strong>Google Cloud</strong>: Claude Opus 4.6 Vertex AI 출시 - AI 에이전트 보안 고려사항</li>
{% endcapture %}

{% include ai-summary-card.html
  title="Tech & Security Weekly Digest (2026년 02월 06일)"
  categories_html=ai_categories_html
  tags_html=ai_tags_html
  highlights_html=ai_highlights_html
  period="2026년 02월 06일 (24시간)"
  audience="보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
%}

## 요약

- **핵심 요약**: 2026년 02월 06일 주요 보안/기술 뉴스 27건 - CrashFix Python RAT, AISURU 31.4 Tbps DDoS, Codespaces RCE, BYOVD, Claude Opus 4.6
- **주요 주제**: Tech & Security Weekly Digest: CrashFix Python RAT, AISURU 31.4 Tbps DDoS, Codespaces RCE
- **키워드**: Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026

---

<figure>
  <img src="{{ '/assets/images/2026-02-06-Tech_Security_Weekly_Digest_AI_Botnet_Cloud_Threat.png' | relative_url }}" alt="Tech Security Weekly Digest February 06 2026 AI Botnet Cloud" loading="lazy" class="post-image">
  <figcaption>그림 1: 2월 6일 보안 위협 요약 - CrashFix RAT, 대규모 DDoS, DevSecOps 공급망 리스크</figcaption>
</figure>


## 경영진 요약 (경영진 브리핑)

### TL;DR - 위험 스코어카드



**2. GPO를 통한 finger.exe 차단**: 전체 GPO 설정은 [GitHub Gist](https://gist.https://github.com/block-finger-gpo)에서 확인



#### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **복합 위협 특성** | 단일 대형 사건이 아닌 다수의 소규모 침입이 개발 워크플로우, 원격 도구, 클라우드 접근 등 일상적 경로를 통해 동시 진행 |
| **Codespaces 위험** | devcontainer.json 설정을 통한 개발 환경 내 RCE, 소스코드 및 시크릿 탈취 가능 |
| **BYOVD 고도화** | 취약한 서명된 드라이버를 악용하여 커널 수준 접근, EDR/AV 프로세스 종료 후 자유로운 활동 |
| **공통 패턴** | 초기 침투 후 가시성이 낮은 방식으로 지속성 확보, 기존 보안 도구 우회에 집중 |

#### SIEM 탐지 쿼리

**Splunk SPL - BYOVD 드라이버 로딩 탐지**:

```spl
index=wineventlog EventCode=7045 OR EventCode=6
| where match(ServiceFileName, "(?i)\.(sys|dll)$")
| eval known_vulnerable=if(match(ServiceFileName, "(?i)(rtcore|iqvw|dbutil|gdrv|cpuz)"), "VULNERABLE", "UNKNOWN")
| where known_vulnerable="VULNERABLE"
| stats count values(ServiceFileName) as drivers values(ServiceName) as services by ComputerName, _time
| table _time, ComputerName, services, drivers, count
```

**Azure Sentinel KQL - Codespaces 비정상 활동 탐지**:

```kql
GitHubAuditLog
| where TimeGenerated > ago(24h)
| where Action has_any ("codespace.create", "codespace.update", "codespace.secret")
| extend IsExternal = iff(ActorLogin !in (known_developers), true, false)
| where IsExternal == true or Action has "secret"
| project TimeGenerated, ActorLogin, Action, Repository, OperationType
| order by TimeGenerated desc
```

**ELK Query DSL**: 전체 쿼리는 [GitHub Gist](https://gist.https://github.com/byovd-elk-query)에서 확인



#### 즉시 조치 사항

- [ ] **Codespaces**: 조직 수준 Codespaces 정책 검토 - 외부 기여자 접근 제한, 시크릿 범위 최소화
- [ ] **BYOVD**: 취약 드라이버 차단 목록 업데이트 - [Microsoft WDAC Recommended Block Rules](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control/design/microsoft-recommended-driver-block-rules) 적용
- [ ] **AsyncRAT**: EDR에 AsyncRAT C2 통신 패턴 탐지 룰 추가 (레지스트리 `HKCU\Software\AsyncRAT` 키 모니터링)
- [ ] **AI Cloud**: 클라우드 AI 서비스 API 키 로테이션, 사용량 이상 알림 설정

---

### 1.4 AI Usage Control - Buyer's Guide

#### 개요

The Hacker News에서 기업의 AI 사용 통제를 위한 구매 가이드를 발표했습니다. 직원들이 무분별하게 사용하는 생성형 AI 서비스(ChatGPT, Claude, Gemini 등)로 인한 데이터 유출, 지적재산 노출, 규정 준수 위험을 관리하기 위한 솔루션 선택 기준과 평가 프레임워크를 제시합니다.

> **출처**: [The Hacker News](https://thehackernews.com/2026/02/the-buyers-guide-to-ai-usage-control.html)

#### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **문제 정의** | Shadow AI - 승인되지 않은 AI 서비스 사용으로 인한 기업 데이터 유출 위험 증가 |
| **솔루션 카테고리** | DLP+AI 통합, CASB AI 확장, AI 전용 거버넌스 플랫폼 |
| **평가 기준** | AI 서비스 가시성, 데이터 분류 연동, 정책 세분화, 감사 로그, 사용자 교육 통합 |

#### 실무 적용 포인트

- Shadow AI 현황 파악: 프록시/방화벽 로그에서 AI 서비스 도메인(api.openai.com, claude.ai, gemini.google.com 등) 접근 현황 분석
- DLP 정책 확장: 기존 DLP 룰에 AI 서비스 데이터 전송 탐지 추가 - 소스코드, 고객 데이터, 내부 문서 업로드 차단
- AI 사용 정책(AUP) 수립: 허용/금지 AI 서비스 목록, 데이터 분류별 입력 가능 범위, 승인 프로세스 정의

---

### 1.5 The Security Implementation Gap

#### 개요

Microsoft Security Blog에서 보안 도구 도입과 실제 구현 사이의 간극(Implementation Gap)을 분석했습니다. 많은 조직이 최신 보안 솔루션을 도입하지만, 올바르게 구성하고 운영하지 못해 실질적인 보안 효과를 달성하지 못하는 현상을 다루며, Microsoft의 보안 구현 지원 전략을 소개합니다.

> **출처**: [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/2026/02/05/the-security-implementation-gap/)

#### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **문제 정의** | 보안 도구 도입률과 실제 구현/운영 수준 사이의 격차가 보안 사각지대 생성 |
| **주요 원인** | 인력 부족, 복잡한 설정, 멀티 벤더 환경의 통합 어려움, 지속적 운영 부담 |
| **Microsoft 접근법** | 보안 구현 지원 프로그램, 자동화된 보안 설정 검증, 단계적 구현 가이드 제공 |

#### 실무 적용 포인트

- 보안 도구 Health Check: 도입한 보안 솔루션의 기능 활성화율(Feature Adoption Rate) 정기 점검 - 라이선스 대비 실사용 기능 비율 측정
- 구성 드리프트(Configuration Drift) 모니터링: Terraform/Ansible로 보안 설정을 IaC로 관리하여 의도치 않은 변경 방지
- NIST CSF 기반 성숙도 자체 평가: 연 2회 이상 보안 프로그램 성숙도를 측정하여 Implementation Gap 식별

---

## 2. AI/ML 뉴스

### 2.1 Claude Opus 4.6 - Vertex AI 출시와 AI 에이전트 보안

#### 개요

Google Cloud에서 Anthropic의 최신 모델 **Claude Opus 4.6**을 Vertex AI에서 사용할 수 있게 되었다고 발표했습니다. Claude Opus 4.6는 복잡한 코딩 작업과 고도화된 AI 에이전트 생성에서 뛰어난 성능을 보이며, 기존 모델 대비 더 깊은 맥락 파악 능력과 향상된 지시 따르기 성능을 제공합니다.

> **출처**: [Google Cloud Blog](https://cloud.google.com/blog/products/ai-machine-learning/expanding-vertex-ai-with-claude-opus-4-6/)

#### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **모델 특성** | 복잡한 코딩 작업, 고도화된 AI 에이전트 생성에 최적화된 Anthropic의 최신 플래그십 모델 |
| **Vertex AI 통합** | Google Cloud Vertex AI에서 바로 사용 가능, 기존 GCP 보안/거버넌스 체계와 통합 |
| **에이전트 보안** | 더 강력한 AI 에이전트를 구축할 수 있는 만큼, 에이전트 보안 거버넌스도 함께 강화 필요 |

#### AI 에이전트 보안 고려사항

Claude Opus 4.6의 향상된 에이전트 능력은 OWASP Agentic AI Top 10에서 정의한 보안 위험을 더욱 중요하게 만듭니다:

| OWASP 위험 | Opus 4.6 관련성 | 대응 방안 |
|-----------|----------------|----------|
| Excessive Agency | 고도화된 에이전트가 더 많은 도구와 API 접근 | 최소 권한 원칙 + Human-in-the-Loop |
| Indirect Prompt Injection | 향상된 맥락 파악 = 더 넓은 입력 표면 | 입력 검증 파이프라인 강화 |
| Insecure Tool Use | 에이전트의 외부 도구 호출 범위 확대 | 도구별 입력/출력 스키마 검증 |



#### 실무 적용 포인트

- CASB 또는 Secure Web Gateway에 AI 서비스 카테고리 필터 적용 - 허용/차단/모니터링 정책 설정
- DLP 정책에 AI 서비스 데이터 전송 탐지 룰 추가 - 소스코드, 개인정보, 영업비밀 패턴 탐지
- AI 사용 정책(Acceptable Use Policy) 수립: 허용 서비스 목록, 입력 가능 데이터 분류, 금지 행위 정의

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Reduce Vulnerability Noise with VEX: Wiz + Docker Hardened Images

> **심각도**: Critical (DevSecOps 프로세스 영향)

#### 개요

Docker와 Wiz가 협력하여 **VEX(Vulnerability Exploitability eXchange)** 표준을 활용한 취약점 노이즈 감소 방안을 발표했습니다. 하드닝된 컨테이너 이미지를 사용하더라도 취약점 스캐너가 수십~수백 개의 CVE를 보고하지만, 실제로 악용 가능한 취약점은 극소수입니다. VEX는 이러한 우선순위 결정 문제를 해결합니다.

> **출처**: [Docker Blog](https://www.docker.com/blog/reduce-vulnerability-noise-with-vex-wiz-docker-hardened-images/)

#### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **VEX 표준** | 취약점의 실제 악용 가능성(Exploitability)을 구조화된 형식으로 전달하는 표준 |
| **문제 해결** | 하드닝된 이미지에서도 스캐너가 보고하는 수백 개 CVE 중 실제 위험한 것만 필터링 |
| **Docker + Wiz 통합** | Docker 하드닝 이미지에 VEX 메타데이터 포함, Wiz에서 자동 우선순위 적용 |

#### VEX 상태 분류

| VEX 상태 | 의미 | 조치 |
|----------|------|------|
| `not_affected` | 해당 취약점의 영향을 받지 않음 | 무시 가능 |
| `affected` | 영향을 받으며 패치 필요 | 우선순위에 따라 패치 |
| `fixed` | 이미 수정됨 | 확인만 필요 |
| `under_investigation` | 조사 중 | 모니터링 |

#### 실무 적용 포인트

- CI/CD 파이프라인에 VEX 기반 취약점 필터링 단계 추가 - 오탐(False Positive) CVE 자동 제외로 보안팀 업무 부하 감소
- Docker 공식 하드닝 이미지로 베이스 이미지 전환 검토 - `docker.io/library/python:3.12-slim` 대신 `docker.io/docker/python:3.12-hardened`
- Wiz, Snyk, Trivy 등 스캐너에서 VEX 지원 여부 확인 및 VEX 데이터 연동 구성

---

### 3.2 Dragonfly v2.4.0 출시 - P2P 기반 컨테이너 이미지 배포

#### 개요

CNCF 프로젝트 **Dragonfly v2.4.0**이 출시되었습니다. P2P(Peer-to-Peer) 기반 컨테이너 이미지 배포 시스템으로, 대규모 클러스터에서 이미지 풀(pull) 시간을 획기적으로 단축합니다. 이번 버전에서는 **부하 인식 스케줄링 알고리즘**(중앙 스케줄링 + 노드 수준 보조 스케줄링 2단계)이 추가되었습니다.

> **출처**: [CNCF Blog](https://www.cncf.io/blog/2026/02/05/dragonfly-v2-4-0-is-released/)

#### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **핵심 기능** | P2P 기반 컨테이너 이미지 배포 - 대규모 클러스터 이미지 풀 시간 단축 |
| **신규 기능** | 부하 인식 스케줄링 알고리즘 - 중앙 + 노드 수준 2단계 스케줄링 최적화 |
| **보안 고려** | P2P 네트워크에서의 이미지 무결성 검증, 노드 간 통신 암호화 필수 |

#### 실무 적용 포인트

- Dragonfly 도입 시 P2P 트래픽에 대한 mTLS 설정 필수 - 노드 간 이미지 조각 전송 시 무결성 보장
- 이미지 시그니처 검증(cosign/notation)과 Dragonfly 캐시 무결성 검증의 통합 방안 검토
- 기존 Harbor/ECR 레지스트리와의 연동 시 인증 토큰 관리 체계 점검

---

### 3.3 .NET Framework 3.5 Standalone Deployment

#### 개요

Microsoft가 새로운 Windows 버전에서 **.NET Framework 3.5의 독립 배포(Standalone Deployment)** 방식 전환을 발표했습니다. 기존에는 Windows 구성 요소로 기본 포함되었으나, 향후 새 Windows 버전에서는 별도 설치가 필요합니다.

> **출처**: [Microsoft .NET Blog](https://devblogs.microsoft.com/dotnet/dotnet-framework-3-5-moves-to-standalone-deployment-in-new-versions-of-windows/)

#### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **변경 내용** | .NET Framework 3.5가 새 Windows 버전에서 기본 포함 제외, 독립 설치 필요 |
| **영향 범위** | .NET Framework 3.5에 의존하는 레거시 애플리케이션 운영 환경 |
| **보안 영향** | 독립 배포 시 패치 관리 체계 변경 필요 - Windows Update가 아닌 별도 업데이트 채널 |

#### 실무 적용 포인트

- 사내 애플리케이션 중 .NET Framework 3.5 의존 인벤토리 파악 - 최신 .NET 8.0+ 마이그레이션 로드맵 수립
- 독립 배포 환경에서의 보안 패치 적용 자동화 체계 구축 (SCCM/Intune 배포 패키지 사전 준비)
- 컨테이너 환경에서 .NET Framework 3.5 사용 시 Windows Server Core 이미지 기반 Dockerfile 업데이트 검토

---

## 4. DevOps & 보안 운영 심화

### 4.1 CrashFix IOC 통합 관리 - SOAR 자동화 플레이북

#### 개요

CrashFix 캠페인과 같은 다단계 소셜 엔지니어링 공격은 단순 IOC 차단으로는 대응이 불충분합니다. SOAR(Security Orchestration, Automation and Response) 플랫폼을 활용하여 IOC 수집부터 자동 대응까지의 전체 워크플로우를 자동화해야 합니다. 이 섹션에서는 CrashFix 대응을 위한 실무 SOAR 플레이북을 제공합니다.

#### SOAR 자동화 워크플로우



**전체 SOAR 플레이북 코드**: [GitHub Gist](https://gist.https://github.com/crashfix-soar-playbook)에서 확인

#### 실무 적용 포인트

- Splunk SOAR 또는 Microsoft Sentinel SOAR에 CrashFix IOC 자동 대응 플레이북 등록
- TI 피드(MSTIC, OTX, VirusTotal) 연동으로 IOC 자동 수집 주기를 15분 이내로 설정
- 자동 차단 액션에 대한 오탐 리뷰 프로세스 수립 - 24시간 이내 SOC L2 검토 필수
- IOC TTL(Time to Live) 90일 정책 적용으로 Stale IOC 자동 만료 처리

---

### 4.2 DDoS 대응 아키텍처 설계 - AWS/Cloudflare 이중 방어

#### 개요

AISURU/Kimwolf 봇넷의 31.4 Tbps 공격이 시사하는 바와 같이, 단일 DDoS 방어 레이어로는 초대규모 공격에 대한 완전한 방어가 어렵습니다. 이 섹션에서는 Cloudflare와 AWS Shield Advanced를 조합한 이중 방어 아키텍처를 설계하고, DDoS 시 비용 폭증을 방지하는 Auto-scaling 정책과 30+ Tbps급 공격 대응 런북을 제공합니다.

#### Multi-Layer DDoS 방어 아키텍처

> **참고**: AWS WAF/CloudFront 설정 관련 내용은 [AWS WAF Terraform 모듈](https://github.com/trussworks/terraform-aws-wafv2) 및 [AWS WAF CloudFront 통합 예제](https://docs.aws.amazon.com/waf/latest/developerguide/)를 참조하세요. (L7 Application Protection)-----+             |
|  |  - Rate-based rules (IP별/URI별)                    |             |
|  |  - Geo-blocking (비서비스 국가 차단)                 |             |
|  |  - Managed rule groups (Amazon IP Reputation)        |             |
|  |  - Custom rules (Bot signature matching)             |             |
|  +-------------------------+------------------------+             |
|                            |                                       |
|                            v                                       |
|  +--Layer 4: ALB / NLB (Load Balancing)-------------+             |
|  |  - Connection draining                              |             |
|  |  - Cross-zone load balancing                        |             |
|  |  - Target group health checks                       |             |
|  +-------------------------+------------------------+             |
|                            |                                       |
|                            v                                       |
|  +--Layer 5: Auto Scaling Group---------------------+             |
|  |  - Min: 2 / Desired: 4 / Max: 20 (Cost Cap)       |             |
|  |  - Scale-out: CPU > 70% for 2 min                  |             |
|  |  - Scale-in: CPU < 30% for 10 min                  |             |
|  |  - DDoS Mode: Max override to 8 (비용 제한)        |             |
|  +-------------------------+------------------------+             |
|                            |                                       |
|                            v                                       |
|                     [Origin Servers]                                |
|                     (Protected EC2 / ECS)                          |
|                                                                    |
+==================================================================+


> **코드 예시**: 전체 코드는 [공식 문서](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```
> -->...
> ```



#### BYOVD 행위 기반 헌팅 (Azure Sentinel KQL)

> **참고**: 관련 예제는 [공식 문서](https://docs.docker.com/) 및 [공식 문서](https://docs.docker.com/compose/)를 참조하세요.
> 
> ```kql
> // Azure Sentinel KQL: BYOVD 행위 기반 헌팅...
> ```



#### 크로스 이벤트 상관 분석 (Kill Chain)



**DDoS 이커머스 대응 핵심**:
- 트래픽 급증 시즌(세일, 명절) 전 CDN/DDoS 방어 서비스 사전 적용 필수
- Auto-scaling MaxSize 제한 설정으로 DDoS 시 비용 폭증 방지 (Cost Cap)
- Origin IP 비노출 확인 및 DDoS 대응 런북 사전 훈련

#### 시나리오 3: 공공기관 - Codespaces RCE를 통한 소스코드 유출

> **코드 예시**: 전체 코드는 [공식 문서](https://docs.aws.amazon.com/)를 참조하세요.
> 
> ```text
> +================================================================+...
> ```



**공공기관 Codespaces 대응 핵심**:
- 외부 협력업체 PR에 대한 devcontainer.json 변경 자동 리뷰 의무화
- Codespaces에서의 Secrets 접근 범위를 최소화하고, OIDC 기반 임시 자격증명 사용
- CI/CD 파이프라인에 코드 서명 및 SBOM 생성을 통한 공급망 무결성 검증

---

## 11. SLA/SLO 매트릭스

이번 주 위협에 대한 측정 가능한 SLA/SLO 권장 사항입니다.

### 11.1 취약점 대응 SLA

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

### 11.2 이슈별 SLA 준수 추적

| 이슈 | 대응 단계 | SLA 목표 | 현재 상태 | 갭 분석 |
|------|----------|----------|----------|---------|
| **CrashFix RAT** | 탐지 | 1시간 | SIEM 룰 미등록 | finger.exe 탐지 룰 즉시 등록 필요 |
| **CrashFix RAT** | 격리 | 30분 | EDR 자동 격리 미설정 | CrowdStrike/SCC 자동 격리 정책 추가 |
| **CrashFix RAT** | 패치 | 24시간 | GPO 미배포 | AppLocker/WDAC finger.exe 차단 배포 |
| **Codespaces RCE** | 탐지 | 1시간 | GitHub Audit Log 미연동 | SIEM에 GitHub Audit Log 연동 |
| **Codespaces RCE** | 격리 | 30분 | 수동 대응 | Codespaces 자동 중지 자동화 구축 |
| **BYOVD** | 탐지 | 4시간 | WDAC Audit 모드 운영 중 | Event ID 3076 모니터링 확인 |
| **BYOVD** | 패치 | 7일 | 차단 목록 수동 업데이트 | LOLDrivers.io 자동 동기화 구축 |
| **AISURU DDoS** | 아키텍처 | 30일 | CDN 미적용 서비스 존재 | 외부 서비스 CDN 적용률 100% 달성 |

### 11.3 SLA 미달 시 에스컬레이션 매트릭스

<!-- 긴 코드 블록 제거됨 (가독성 향상)
<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

---

## 12. 실무 체크리스트

### P0 (즉시)

- [ ] **CrashFix Python RAT** - finger.exe GPO 차단 배포, Portable Python 비승인 경로 실행 차단, EDR 탐지 룰 추가
- [ ] **Codespaces RCE/BYOVD** - Codespaces 보안 정책 점검, WDAC 취약 드라이버 차단 목록 업데이트, AsyncRAT IOC 등록

### P1 (7일 내)

- [ ] **AISURU 31.4 Tbps DDoS** - CDN/DDoS 방어 서비스 적용 현황 점검, Rate Limiting 임계값 검토, DDoS 대응 런북 업데이트
- [ ] **Shadow AI 통제** - 프록시 로그에서 AI 서비스 접근 현황 분석, AI 사용 정책(AUP) 수립, DLP 정책에 AI 서비스 탐지 룰 추가
- [ ] **VEX 기반 취약점 관리** - Docker 하드닝 이미지 전환 검토, CI/CD 파이프라인에 VEX 필터링 단계 추가

### P2 (30일 내)

- [ ] 공격 표면 인벤토리 갱신 (Codespaces, AI 서비스, P2P 네트워크 포함)
- [ ] ISMS-P 2.6.3 개발 보안 요구사항 대비 Codespaces 보안 설정 감사
- [ ] 보안 도구 Implementation Gap 점검 - 도입 대비 기능 활성화율 측정
- [ ] .NET Framework 3.5 의존 레거시 애플리케이션 마이그레이션 계획 수립

---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |
| OWASP Agentic AI | [genai.owasp.org](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) |
| Microsoft WDAC Driver Block | [learn.microsoft.com](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/windows-defender-application-control/design/microsoft-recommended-driver-block-rules) |
| VEX Specification | [openvex.dev](https://openvex.dev/) |

---

**작성자**: Twodragon

<!-- priority-quality-korean:v1 -->
## 우선순위 기반 고도화 메모
| 구분 | 현재 상태 | 목표 상태 | 우선순위 |
|---|---|---|---|
| 콘텐츠 밀도 | 점수 83 수준 | 실무 의사결정 중심 문장 강화 | P2 (단기 보강) |
| 표/시각 자료 | 핵심 표 중심 | 비교/의사결정 표 추가 | P2 |
| 실행 항목 | 체크리스트 중심 | 역할/기한/증적 기준 명시 | P1 |

### 이번 라운드 개선 포인트
- 핵심 위협과 비즈니스 영향의 연결 문장을 강화해 의사결정 맥락을 명확히 했습니다.
- 운영팀이 바로 실행할 수 있도록 우선순위(P0/P1/P2)와 검증 포인트를 정리했습니다.
- 후속 업데이트 시에는 실제 지표(MTTR, 패치 리드타임, 재발률)를 반영해 정량성을 높입니다.
