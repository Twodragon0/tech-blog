---

author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-01-23 10:00:00 +0900
description: '2026년 1월 23일 주요 기술/보안 뉴스: Microsoft AitM 피싱 경고, HashiCorp Agentic AI Zero Trust NHI 관리, OpenAI PostgreSQL 8억 사용자 스케일링 아키텍처, vLLM 제작자 Inferact $150M 투자까지...'
excerpt: "기술·보안 주간 다이제스트: Microsoft AitM 피싱 경고, Agentic AI Zero Trust, - 2026년 1월 23일 주요 기술/보안 뉴스: Microsoft AitM 피싱 경고, HashiCorp Agentic AI"
image: /assets/images/2026-01-23-Tech_Security_Weekly_Digest.svg
image_alt: Tech and Security Weekly Digest January 2026 - AitM Phishing, Zero Trust,
  PostgreSQL Scaling
layout: post
tags:
- Security-Weekly
- AitM-Phishing
- BEC
- Zero-Trust
- Agentic-AI
- NHI
- PostgreSQL
- OpenAI
- Google-Cloud
- HashiCorp
- vLLM
- DevSecOps
- '2026'
title: '기술·보안 주간 다이제스트: Microsoft AitM 피싱 경고, Agentic AI Zero Trust,
  OpenAI PostgreSQL 8억 사용자 스케일링'
toc: true
---
{%- include ai-summary-card.html
  title='Tech & Security Weekly Digest (2026년 01월 23일)'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">AitM-Phishing</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">Agentic-AI</span>
      <span class="tag">PostgreSQL</span>
      <span class="tag">OpenAI</span>
      <span class="tag">HashiCorp</span>
      <span class="tag">vLLM</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>Microsoft</strong>: 에너지 기업 대상 다단계 AitM 피싱 & BEC 공격 경고 - SharePoint 악용</li>
      <li><strong>HashiCorp</strong>: Agentic AI 시스템의 Zero Trust NHI(비인간 ID) 관리 가이드 발표</li>
      <li><strong>OpenAI</strong>: PostgreSQL로 8억 ChatGPT 사용자 지원 - 스케일링 아키텍처 공개</li>
      <li><strong>Inferact</strong>: vLLM 제작자 설립, a16z/Lightspeed 주도 $150M 시드 투자 유치</li>
      <li><strong>Google SRE</strong>: Gemini CLI 활용 실제 장애 대응 사례 공개</li>'
  period='2026년 1월 22일 ~ 23일 (24시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트, CISO'
-%}

## 경영진 요약

### 위협 리스크 스코어카드

| 위협 유형 | 심각도 | 영향도 | 긴급도 | 한국 조직 노출도 | 권장 조치 기한 |
|----------|--------|--------|--------|-----------------|--------------|
| AitM 피싱 + BEC 공격 | 🔴 Critical | 높음 | 긴급 | 매우 높음 | 48시간 이내 |
| Agentic AI NHI 관리 부재 | 🟠 High | 중간 | 중간 | 중간 | 30일 이내 |
| 대규모 DB 스케일링 한계 | 🟡 Medium | 중간 | 낮음 | 낮음 | 90일 이내 |
| AI 콘텐츠 환각 (학술/기업) | 🟠 High | 중간 | 중간 | 높음 | 30일 이내 |

### 경영진 브리핑 (1분 요약)

보고 일자: 2026년 1월 23일
보고 대상: CISO, CTO, 경영진

핵심 위협 요약:
1. 즉시 대응 필요 (Critical): Microsoft가 에너지 기업 대상 고도화된 AitM 피싱 공격 경고. 기존 MFA로는 방어 불가능하며, 피싱 방지 MFA (FIDO2/Passkey) 도입 필수.

2. 전략적 대응 필요 (High): Agentic AI 시스템의 확산으로 비인간 ID(NHI) 관리가 새로운 보안 과제로 부상. HashiCorp Zero Trust 가이드 검토 및 동적 시크릿 관리 체계 수립 필요.

3. 기술 트렌드: OpenAI는 8억 사용자를 PostgreSQL로 지원 중. NoSQL 대신 검증된 RDBMS도 초대규모 스케일링 가능함을 입증.

즉시 필요한 예산: 피싱 방지 MFA 도입 (FIDO2 보안 키 구매 + Azure AD P2 라이선스)

---

## 서론

안녕하세요, Twodragon입니다.

2026년 1월 23일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다. 이번 주는 Agentic AI 시대의 보안 패러다임 변화가 핵심 화두였습니다.

이번 주 핵심 테마:
- AitM 피싱 고도화: Microsoft의 에너지 섹터 공격 경고
- Agentic AI 보안: 자율 AI 시스템의 Zero Trust 전략
- PostgreSQL 스케일링: OpenAI의 8억 사용자 지원 아키텍처
- AI 인프라 투자: vLLM 기반 Inferact $150M 유치

수집 소스: 39개 RSS 피드에서 91개 뉴스 수집
분석 기준: DevSecOps 실무 영향도, 기술적 깊이, 즉시 적용 가능성

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 | 긴급도 |
|------|------|----------|--------|--------|
| 피싱/BEC | Microsoft | 에너지 기업 AitM 공격 | 높음 | 긴급 |
| AI 보안 | HashiCorp | Agentic AI Zero Trust NHI | 높음 | 중간 |
| DB 스케일링 | OpenAI | PostgreSQL 8억 사용자 | 중간 | 낮음 |
| AI 투자 | Inferact | vLLM 기반 $150M 시드 | 중간 | 낮음 |
| SRE 자동화 | Google | Gemini CLI 장애 대응 | 중간 | 낮음 |

### 카테고리별 뉴스 분포

```text
보안 (Security)     : ████████████ 35%
클라우드 (Cloud)    : ██████████ 28%
AI/ML              : ████████ 22%
DevOps             : █████ 15%
```

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. 보안 뉴스 심층 분석

### 1.1 Microsoft, 에너지 기업 대상 다단계 AitM 피싱 및 BEC 공격 경고

{%- include news-card.html
  title="[보안] Microsoft, 에너지 기업 대상 다단계 AitM 피싱 및 BEC 공격 경고"
  url="https://thehackernews.com/2026/01/microsoft-flags-multi-stage-aitm.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgBbSlIXcDChwJf0Cmq4j01QoZOUqnaRGaciqD9J0XKMk-2_Fnzge5_qv44fs_4xzO3OORbk0kiYFOHlocsuJBdVDxC86k-GMG-21LAJ-62F15I6XyUVobMKwVVh6h8PxP6rsJSPaSFUh50yCflaAxLI-UpGwbCLAaCtKqoti67rT6jChpeTei6TUjjYCE4/s1700-e365/1000049930.png"
  summary="Microsoft Defender Security Research Team이 에너지 섹터를 타겟으로 한 정교한 다단계 공격 캠페인을 경고했습니다. 이 공격은 기존 피싱과 달리 Adversary-in-the-Middle (AitM) 기법과 Business Email Compromise (BEC)를 결합한 고도화된 형태입니다."
  source="The Hacker News - Microsoft AitM Phishing Warning"
-%}


Microsoft Defender Security Research Team이 에너지 섹터를 타겟으로 한 정교한 다단계 공격 캠페인을 경고했습니다. 이 공격은 기존 피싱과 달리 Adversary-in-the-Middle (AitM) 기법과 Business Email Compromise (BEC)를 결합한 고도화된 형태입니다.

#### 공격 메커니즘 상세 분석

![AitM + BEC 공격 흐름도](/assets/images/2026-01-23-AitM_BEC_Attack_Flow.svg)

#### 공격 흐름 다이어그램


---

### 1.2 Agentic AI 시스템을 위한 Zero Trust 보안 전략

{%- include news-card.html
  title="[보안] Agentic AI 시스템을 위한 Zero Trust 보안 전략"
  url="https://www.hashicorp.com/blog/zero-trust-for-agentic-systems-managing-non-human-identities-at-scale"
  image="https://www.datocms-assets.com/2885/1764106190-theattackphase0and1.jpg?w=1200&h=630&fit=crop&auto=format"
  summary="HashiCorp에서 자율 AI 시스템(Agentic AI)의 보안을 위한 포괄적인 Zero Trust 가이드를 발표했습니다. 이는 단순히 AI 모델 보안이 아닌, AI가 사용하는 모든 비인간 ID(NHI: Non-Human Identities)의 관리에 초점을 맞추고 있습니다."
  source="HashiCorp - Zero Trust for Agentic Systems"
-%}


HashiCorp에서 자율 AI 시스템(Agentic AI)의 보안을 위한 포괄적인 Zero Trust 가이드를 발표했습니다. 이는 단순히 AI 모델 보안이 아닌, AI가 사용하는 모든 비인간 ID(NHI: Non-Human Identities)의 관리에 초점을 맞추고 있습니다.

#### Agentic AI의 보안 패러다임 변화

![Traditional AI vs Agentic AI - Comparison of reactive vs autonomous AI with security complexity ratings](/assets/images/diagrams/2026-01-23-traditional-vs-agentic-ai.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

| | Traditional AI (Reactive) | Agentic AI (Autonomous) |
|---|---|---|
| Processing | Input → Output | Goal → Plan → Execute |
| API | Single API call | Multi-tool orchestration |
| Decision | Human approval required | Independent decisions |
| Permissions | Static | Dynamic requirements |
| Security | ★★☆☆☆ LOW | ★★★★★ HIGH |

</details>

#### Agentic AI NHI 공격 시나리오


---

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 2. 클라우드 & 인프라 뉴스

### 2.1 OpenAI, PostgreSQL로 8억 ChatGPT 사용자 지원

{%- include news-card.html
  title="[클라우드] OpenAI, PostgreSQL로 8억 ChatGPT 사용자 지원"
  url="https://eieio.games/blog/ssh-sends-100-packets-per-keystroke/"
  image="https://eieio.games/images/ssh-sends-100-packets-per-keystroke/og_image.png"
  summary="OpenAI가 PostgreSQL을 활용한 대규모 스케일링 전략을 공개했습니다. 이는 NoSQL이나 NewSQL 솔루션 대신 검증된 RDBMS로도 초대규모 서비스가 가능함을 증명합니다."
  source="eieio.games - SSH Packets Analysis"
-%}


OpenAI가 PostgreSQL을 활용한 대규모 스케일링 전략을 공개했습니다. 이는 NoSQL이나 NewSQL 솔루션 대신 검증된 RDBMS로도 초대규모 서비스가 가능함을 증명합니다.

#### 스케일링 아키텍처 핵심 요소

![OpenAI PostgreSQL 스케일링 아키텍처](/assets/images/2026-01-23-PostgreSQL_Scaling_Architecture.svg)

#### DevSecOps 관점 인사이트

| 영역 | 인사이트 | 적용 포인트 |
|------|----------|------------|
| Connection Management | PgBouncer로 연결 풀링 필수 | 서버리스 환경에서 특히 중요 |
| Read/Write Split | 읽기 트래픽 리플리카 분산 | 80% 이상이 읽기 작업인 경우 효과적 |
| Horizontal Scaling | Citus로 분산 처리 | 단일 노드 한계 극복 |
| 모니터링 | 쿼리 성능 지속 추적 | pg_stat_statements 활용 |

#### 한국 조직의 PostgreSQL 스케일링 현황

국내 기업의 일반적 DB 스케일링 한계:

| 사용자 규모 | 일반적 선택 | 문제점 | OpenAI 접근법과 차이 |
|------------|------------|--------|---------------------|
| ~100만 | 단일 PostgreSQL | Connection 고갈 | PgBouncer 미사용 |
| 100만~500만 | MongoDB로 전환 | 트랜잭션 복잡도 증가 | Read Replica 활용으로 RDBMS 유지 |
| 500만~1000만 | DynamoDB/Cosmos DB | 높은 비용 | Citus 샤딩으로 비용 절감 |
| 1000만 이상 | 포기 또는 대규모 재설계 | 기술 부채 누적 | 점진적 확장 전략 |

OpenAI 방식을 한국 조직에 적용 시 이점:


---

## 4. 기타 주목할 뉴스

### 4.1 HashiCorp, AWS Kiro Powers 런치 파트너

AWS의 새로운 AI 코딩 환경 Kiro의 확장 기능 Kiro powers가 발표되었으며, HashiCorp이 Terraform power로 런치 파트너가 되었습니다.

### 4.2 Capital One, Brex $5.15B 인수

Capital One이 핀테크 기업 Brex를 $5.15B에 인수한다고 발표. 기업 지출 관리 시장의 대형 M&A.

### 4.3 Claude Code 사용 중 계정 차단 사례

개인 프로젝트에서 Claude Code CLI로 CLAUDE.md 파일 생성 자동화 중 계정이 예고 없이 비활성화된 사례가 보고됨. AI 도구 사용 시 이용약관 주의 필요.

---

## 5. DevSecOps 실무 체크리스트

이번 주 뉴스를 바탕으로 한 즉시 점검 가능한 항목들:

### 긴급 (이번 주 내 조치)

- [ ] 피싱 방지 MFA 도입 상태 점검: FIDO2/Passkey 지원 여부 확인
- [ ] SharePoint 외부 공유 설정 감사: Anyone 링크 비활성화
- [ ] 받은편지함 규칙 모니터링 설정: 의심스러운 규칙 자동 알림

### 중요 (이번 달 내 계획)

- [ ] Agentic AI 보안 정책 수립: NHI 관리 체계 검토
- [ ] 동적 시크릿 관리 도입: Vault 또는 유사 솔루션 검토
- [ ] PostgreSQL 스케일링 아키텍처 검토: Connection pooling, Read replica 구성

### 권장 (분기 내 검토)

- [ ] AI 도구 활용 SRE 자동화: Gemini CLI 또는 유사 도구 파일럿
- [ ] LLM 추론 인프라 최적화: vLLM 도입 검토
- [ ] AI 생성 콘텐츠 검증 체계: 내부 문서/코드 리뷰 프로세스

---

## 6. Threat Hunting 가이드

이번 주 주요 위협에 대한 능동적 위협 헌팅(Threat Hunting) 쿼리 및 절차를 제공합니다.

### 6.1 AitM 피싱 공격 헌팅

#### Hunting Hypothesis (가설)
"우리 조직 내에 이미 AitM 피싱으로 계정이 탈취되었으나 아직 탐지되지 않은 사용자가 있을 수 있다."

#### Hunting Procedure (절차)

Step 1: 의심스러운 받은편지함 규칙 탐지


Step 2: 동일 API 키의 비정상 지리적 사용 패턴

<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

Step 3: AI 에이전트의 권한 상승 시도

<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

Step 4: Vault Audit Log 이상 패턴

```json
{
  "vault_hunting_query": {
    "description": "Vault에서 동일 토큰의 과다한 시크릿 접근 탐지",
    "query": "cat /var/log/vault/audit.log | jq 'select(.type==\"response\" and .auth.client_token != null) | {time: .time, token: .auth.client_token, path: .request.path}' | jq -s 'group_by(.token) | map({token: .[0].token, access_count: length, paths: [.[].path] | unique}) | .[] | select(.access_count > 100)'"
  }
}
```

### 6.3 Threat Hunting 보고서 템플릿

<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

---

## 결론

이번 주는 Agentic AI 시대의 보안 패러다임 전환이 가장 큰 화두였습니다.

핵심 메시지:

1. 피싱 공격 고도화: AitM + BEC 결합 공격에 기존 MFA만으로는 부족 → 피싱 방지 MFA 필수

2. AI 시스템 보안: 자율 AI의 확산으로 NHI(비인간 ID) 관리가 새로운 보안 과제 → Zero Trust 원칙 적용

3. 검증된 기술의 힘: OpenAI도 PostgreSQL 사용 → 기본에 충실한 아키텍처가 스케일링의 핵심

4. AI 인프라 투자 급증: vLLM 기반 Inferact $150M 유치 → AI 추론 인프라 시장 급성장

다음 주에도 DevSecOps 실무에 도움이 되는 핵심 뉴스를 선별하여 분석해 드리겠습니다.

---


## 관련 포스트

- ['AWS/GCP 2026년 1월 주요 업데이트: EC2 G7e/X8i 인스턴스, Bangkok 리전, European Sovereign]({% post_url 2026-01-22-AWS_GCP_Cloud_Updates_January_2026_EC2_G7e_X8i_Bangkok_Region_European_Sovereign_Cloud %})
- ["\U0001F680 클라우드 보안 과정 8기 8주차: CI/CD와 Kubernetes 보안 실전 가이드 - DevSecOps 파이프라인부터]({% post_url 2026-01-22-Cloud_Security_Course_8Batch_8Week_CI_CD_Kubernetes_Security_Practical_Guide %})
- ['2026년 1월 클라우드 보안 동향: Kubernetes 82% 프로덕션 도입, VS Code 악용 위협 증가, CNCF 연례 조사]({% post_url 2026-01-22-Cloud_Security_Trends_January_2026_Kubernetes_82_Percent_Production_VS_Code_Threats_CNCF_Survey %})
- [2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략]({% post_url 2026-01-22-KARA_Ransomware_Trends_Report_2025_Q3_Analysis_SK_Shieldus_EQST %})
- [KISA 보안 공지 분석: 랜섬웨어 예방 가이드와 리눅스 커널 루트킷 점검 방법]({% post_url 2026-01-22-KISA_Security_Advisory_Ransomware_Prevention_Linux_Rootkit_Detection_Guide_Analysis %})
- [보안 벤더 블로그 주간 리뷰 (2026년 01월 22일)]({% post_url 2026-01-22-Security_Vendor_Blog_Weekly_Review %})
- ['기술·보안 주간 다이제스트: Microsoft BitLocker FBI 키 제공, Cloudflare Route]({% post_url 2026-01-24-Tech_Security_Weekly_Digest_BitLocker_FBI_Cloudflare_Route_Leak_Agentic_Enterprise_Docker %})
- ['기술·보안 주간 다이제스트: VMware vCenter KEV 긴급 패치, Fortinet SSO 우회,]({% post_url 2026-01-25-Tech_Security_Weekly_Digest_VMware_vCenter_Fortinet_SSO_Sandworm_DynoWiper_AI_Agents %})
- ['기술·보안 주간 다이제스트: Zero Trust for AI Agents, Chrome 기술지원 사기 방지,]({% post_url 2026-01-26-Tech_Security_Weekly_Digest_Zero_Trust_Agentic_AI_Chrome_Tech_Support_Scam_Terraform_Stacks %})

## 참고 자료

### 보안 위협 관련

AitM 피싱 & BEC 공격:
- [Microsoft Defender - Multi-Stage AitM Phishing Warning](https://thehackernews.com/2026/01/microsoft-flags-multi-stage-aitm.html) - 에너지 섹터 AitM 공격 경고 (원문)
- [Microsoft Security Blog](https://www.microsoft.com/en-us/security/blog/) - Microsoft 보안 연구팀 공식 블로그
- [MITRE ATT&CK - T1557: Adversary-in-the-Middle](https://attack.mitre.org/techniques/T1557/) - AitM 공격 기법 상세 설명
- [MITRE ATT&CK - T1566.002: Spearphishing Link](https://attack.mitre.org/techniques/T1566/002/) - 스피어피싱 링크 기법
- [CISA - Phishing-Resistant MFA Guidance](https://www.cisa.gov/mfa) - 미국 CISA 피싱 방지 MFA 가이드
- [NIST SP 800-63B - Digital Identity Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html) - 인증 수준별 권장사항

Agentic AI & NHI 보안:
- [HashiCorp - Zero Trust for Agentic Systems](https://www.hashicorp.com/blog/zero-trust-for-agentic-systems-managing-non-human-identities-at-scale) - Agentic AI NHI 관리 가이드 (원문)
- [OWASP - Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) - LLM 애플리케이션 보안 위협 Top 10
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) - AI 리스크 관리 프레임워크
- [MITRE ATLAS - Adversarial Threat Landscape for AI Systems](https://atlas.mitre.org/) - AI 시스템 위협 매트릭스
- [CIS Controls v8 - Non-Human Identity Management](https://www.cisecurity.org/controls/v8) - NHI 관리 모범 사례

### 인프라 & 스케일링

PostgreSQL 대규모 스케일링:
- [OpenAI - Scaling PostgreSQL](https://openai.com/index/scaling-postgresql/) - OpenAI의 PostgreSQL 스케일링 전략 (원문)
- [Citus Data Documentation](https://docs.citusdata.com/) - Citus 분산 PostgreSQL 공식 문서
- [PgBouncer Official Documentation](https://www.pgbouncer.org/) - PgBouncer 연결 풀링 가이드
- [PostgreSQL High Availability](https://www.postgresql.org/docs/current/high-availability.html) - PostgreSQL HA 구성 공식 문서
- [AWS RDS Best Practices](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html) - AWS RDS 운영 모범 사례

SRE & 장애 대응:
- [Google Cloud - SRE with Gemini CLI](https://cloud.google.com/blog/topics/developers-practitioners/how-google-sres-use-gemini-cli-to-solve-real-world-outages/) - Google SRE의 Gemini CLI 활용 (원문)
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/) - Google SRE 원칙 및 사례
- [Site Reliability Engineering Workbook](https://sre.google/workbook/table-of-contents/) - SRE 실무 워크북

### AI/ML 인프라

vLLM & 추론 최적화:
- [vLLM GitHub Repository](https://github.com/vllm-project/vllm) - vLLM 오픈소스 프로젝트
- [vLLM Documentation](https://docs.vllm.ai/) - vLLM 공식 문서 (PagedAttention, Continuous Batching)
- [Inferact Funding News - GeekNews](https://news.hada.io/topic?id=26066) - Inferact $150M 투자 유치 뉴스
- [a16z Portfolio - Inferact](https://a16z.com/portfolio/) - Andreessen Horowitz 투자 포트폴리오
- [HuggingFace - LLM Inference Optimization](https://huggingface.co/docs/transformers/llm_tutorial_optimization) - LLM 추론 최적화 가이드

AI 환각 & 콘텐츠 무결성:
- [GPTZero - NeurIPS Analysis](https://gptzero.me/news/neurips/) - NeurIPS 2025 논문 환각 분석 (원문)
- [Stanford - AI Hallucination Research](https://hai.stanford.edu/) - Stanford HAI 환각 연구
- [OpenAI - Model Behavior FAQs](https://platform.openai.com/docs/guides/safety-best-practices) - OpenAI 모델 안전 가이드

### 보안 도구 & 프레임워크

SIEM & 탐지:
- [Splunk SPL Reference](https://docs.splunk.com/Documentation/SplunkCloud/latest/SearchReference/WhatsInThisManual) - Splunk 검색 언어 레퍼런스
- [Azure Sentinel KQL Reference](https://learn.microsoft.com/en-us/azure/data-explorer/kusto/query/) - KQL 쿼리 언어 가이드
- [Sigma Rules Repository](https://github.com/SigmaHQ/sigma) - 범용 SIEM 탐지 룰 저장소
- [Elastic Security Rules](https://www.elastic.co/guide/en/security/current/prebuilt-rules.html) - Elastic 사전 구축 탐지 룰

시크릿 스캐닝 & 관리:
- [TruffleHog GitHub](https://github.com/trufflesecurity/trufflehog) - 시크릿 스캐닝 도구
- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs) - Vault 공식 문서
- [AWS Secrets Manager](https://docs.aws.amazon.com/secretsmanager/) - AWS 시크릿 관리 서비스
- [GitHub Secret Scanning](https://docs.github.com/en/code-security) - GitHub 시크릿 스캐닝

### 규제 & 컴플라이언스 (한국)

- [개인정보보호위원회 - 개인정보보호법 개정안 (2026)](https://www.pipc.go.kr/) - 계정 탈취 시 기업 책임 강화
- [금융보안원 - 금융권 클라우드 보안 가이드](https://www.fsec.or.kr/) - 금융권 MFA 권고사항
- [한국인터넷진흥원(KISA) - 보안 공지](https://www.kisa.or.kr/public/notice/notice_List.jsp) - 국내 보안 위협 동향
- [정보통신망법 시행령](https://www.law.go.kr/) - MFA 관련 규정

### 커뮤니티 & 뉴스 소스

- [The Hacker News](https://thehackernews.com/) - 사이버 보안 뉴스
- [GeekNews](https://news.hada.io/) - 국내 기술 뉴스 큐레이션
- [Hacker News](https://news.ycombinator.com/) - 기술 커뮤니티
- [Reddit /r/netsec](https://www.reddit.com/r/netsec/) - 네트워크 보안 커뮤니티
- [SANS Internet Storm Center](https://isc.sans.edu/) - 실시간 위협 인텔리전스

### 추가 학습 자료

무료 교육 과정:
- [Microsoft Learn - Azure Security](https://learn.microsoft.com/en-us/training/browse/?products=azure&subjects=security) - Azure 보안 무료 교육
- [Google Cloud Skills Boost - Security](https://www.cloudskillsboost.google/paths) - GCP 보안 실습
- [SANS Cyber Aces](https://www.cyberaces.org/) - 무료 사이버 보안 튜토리얼
- [Cybrary - Free Courses](https://www.cybrary.it/) - 보안 전문가 과정

실습 환경:
- [TryHackMe - Red Teaming Path](https://tryhackme.com/paths) - 실전 해킹 시뮬레이션
- [HackTheBox - Enterprise Labs](https://www.hackthebox.com/) - 기업 환경 모의 침투 테스트
- [AWS Skill Builder - Security Learning Plan](https://explore.skillbuilder.aws/learn/public/learning_plan/view/91/security-learning-plan) - AWS 보안 실습

---

면책 조항: 이 포스트의 모든 기술적 내용은 교육 및 방어 목적으로만 제공됩니다. 무단 접근, 시스템 침해, 또는 불법적 활동에 사용해서는 안 됩니다. SIEM 쿼리 및 Threat Hunting 스크립트는 자신이 관리하는 시스템에서만 실행하시기 바랍니다.
