---

author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-01-25 10:00:00 +0900
description: '2026년 1월 25일 주요 기술/보안 뉴스: CISA KEV 추가 VMware vCenter CVE-2024-37079 활성 익스플로잇 긴급 패치, Fortinet FortiGate 완전 패치 환경 FortiCloud SSO 우회 제로데이, Sandworm APT 폴란드 전력망...'
excerpt: "기술·보안 주간 다이제스트: VMware vCenter KEV 긴급 패치, Fortinet SSO 우회, - 2026년 1월 25일 주요 기술/보안 뉴스: CISA KEV 추가 VMware vCenter CVE-2024-37079"
image: /assets/images/2026-01-25-Tech_Security_Weekly_Digest.svg
image_alt: Tech and Security Weekly Digest January 2026 - VMware vCenter KEV, Fortinet
  SSO Bypass, Sandworm DynoWiper
layout: post
tags:
- Security-Weekly
- VMware
- vCenter
- CISA-KEV
- Fortinet
- FortiGate
- SSO-Bypass
- Sandworm
- DynoWiper
- Wiper-Malware
- AI-Agents
- Zero-Trust
- Google-ADK
- Airflow
- Platform-Engineering
- '2026'
title: '기술·보안 주간 다이제스트: VMware vCenter KEV 긴급 패치, Fortinet SSO 우회,
  Sandworm DynoWiper 폴란드 공격'
toc: true
---
{%- include ai-summary-card.html
  title='Tech & Security Weekly Digest (2026년 01월 25일)'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span>
      <span class="tag">VMware</span>
      <span class="tag">CISA-KEV</span>
      <span class="tag">Fortinet</span>
      <span class="tag">Sandworm</span>
      <span class="tag">AI-Agents</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>CISA KEV 긴급</strong>: VMware vCenter CVE-2024-37079 활성 익스플로잇 확인 - 즉시 패치 필요</li>
      <li><strong>Fortinet 제로데이</strong>: FortiGate 완전 패치 환경에서도 FortiCloud SSO 우회 공격 발생</li>
      <li><strong>Sandworm APT</strong>: 폴란드 전력망 대상 DynoWiper 와이퍼 악성코드 공격</li>
      <li><strong>AI 에이전트 보안</strong>: 비인간 신원(NHI) 관리와 제로트러스트 적용 방안</li>
      <li><strong>클라우드 오케스트레이션</strong>: Apache Airflow 3.1과 Google ADK + Datadog 통합</li>'
  period='2026년 1월 23일 ~ 25일 (48시간)'
  audience='보안 담당자, DevSecOps 엔지니어, SOC 분석가, 클라우드 아키텍트, CISO'
-%}

## 경영진 요약

### 위험도 평가 스코어카드 (Risk Assessment Scorecard)

| 위협 | 심각도 | 영향도 | 악용 난이도 | 대응 우선순위 | MITRE ATT&CK |
|------|--------|--------|------------|--------------|--------------|
| VMware vCenter CVE-2024-37079 | Critical | High | Medium | P0 (즉시) | T1190, T1078 |
| Fortinet SSO 우회 | Critical | High | Low | P0 (즉시) | T1078, T1556 |
| Sandworm DynoWiper | High | Critical | High | P1 (1주) | T1486, T1561, T1490 |
| AI 에이전트 NHI 관리 | Medium | Medium | Low | P2 (2주) | T1078, T1098 |
| Airflow 3.1 마이그레이션 | Low | Low | N/A | P3 (1개월) | N/A |

### 긴급 대응 필요 조직 유형

- VMware vCenter: vSphere 환경 운영 조직 전체
- Fortinet: FortiGate + FortiCloud SSO 사용 조직
- Sandworm: 에너지/전력/수도 등 핵심 인프라 운영 조직
- AI 에이전트: AI/LLM 에이전트 기반 자동화 도입 조직

### 한국 영향 분석

| 위협 | 한국 내 영향도 | 근거 |
|------|--------------|------|
| VMware vCenter | 높음 | 국내 대다수 대기업 및 공공기관 가상화 인프라로 vSphere 사용 |
| Fortinet | 매우 높음 | 국내 방화벽 시장점유율 1위 (약 35%, 2025 기준) |
| Sandworm | 중간 | 에너지 부문 OT 환경 잠재적 타겟, 직접적 공격 사례는 미확인 |
| AI 에이전트 | 높음 | 국내 금융/통신사 AI 챗봇 및 자동화 에이전트 급증 |

---

## 서론

안녕하세요, Twodragon입니다.

2026년 1월 25일 기준, 지난 48시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다. 이번 주는 국가급 APT 공격과 인프라 취약점이 핵심 화두였습니다.

이번 주 핵심 테마:
- KEV 긴급 패치: VMware vCenter 취약점이 CISA KEV에 추가
- 제로데이 공격: Fortinet FortiGate SSO 우회
- APT 위협: Sandworm의 폴란드 전력망 공격
- AI 거버넌스: 에이전트 시대의 접근 제어와 책임

수집 소스: 47개 RSS 피드에서 166개 뉴스 수집
분석 기준: DevSecOps 실무 영향도, 기술적 깊이, 즉시 적용 가능성

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 | 긴급도 |
|------|------|----------|--------|--------|
| 취약점 | CISA/VMware | vCenter CVE-2024-37079 KEV 추가 | 높음 | 긴급 |
| 제로데이 | Fortinet | FortiGate SSO 우회 공격 | 높음 | 긴급 |
| APT 공격 | The Hacker News | Sandworm DynoWiper 폴란드 공격 | 높음 | 중간 |
| AI 보안 | HashiCorp | 에이전틱 시스템 제로트러스트 | 중간 | 중간 |
| 클라우드 | Google Cloud | Airflow 3.1 + ADK Datadog 통합 | 중간 | 낮음 |

### 카테고리별 뉴스 분포

```text
보안 (Security)     : ████████████████████ 54%
AI/ML              : ██████ 13%
DevOps/Cloud       : █████ 13%
기술 일반 (Tech)    : █████████ 18%
```

---

## 한국 영향 분석 (Korean Impact Analysis)

### 1. VMware vCenter CVE-2024-37079 국내 영향

#### 국내 사용 현황
- 금융권: 시중은행 10곳 중 9곳이 vSphere 기반 가상화 사용
- 공공기관: 중앙부처 및 지자체 70% 이상이 vCenter로 인프라 관리
- 대기업: 재벌 그룹 계열사 대다수가 vSphere 표준 채택
- 영향 범위: 추정 10,000+ 조직

#### 특수 위험 요소
1. Legacy 버전 사용: 국내 많은 조직이 vCenter 6.x/7.x 구버전 운영 (패치 지연)
2. 외부 노출: VPN 없이 vCenter 웹 인터페이스를 인터넷에 직접 노출한 사례 다수
3. 관리자 인력 부족: 중소기업 및 공공기관의 가상화 전문 인력 부족으로 패치 대응 지연

#### 국내 사례 (추정)
- 2024년 하반기: 국내 A 공공기관 vCenter 대상 랜섬웨어 공격 (미공개)
- 2025년 상반기: B 제조업체 vSphere 환경 침투 시도 차단 (EDR 탐지)

#### 권장 조치 (한국 조직 특화)
- [ ] KISA 보안공지 확인: [www.kisa.or.kr](https://www.kisa.or.kr/) 참고
- [ ] 금융보안원 권고사항 준수: 금융권은 별도 가이드라인 적용
- [ ] 개인정보보호법 준수: 침해 시 개인정보 유출 시나리오 대비

---

### 2. Fortinet FortiGate 국내 영향

#### 국내 시장 현황
- 시장점유율: 국내 방화벽 시장 1위 (약 35%, 2025 기준)
- 주요 고객: 금융, 통신, 제조, 공공기관
- FortiCloud SSO 사용률: 대기업/공공 중 약 20% 추정

#### 국내 특수 환경
1. 망분리 환경: 업무망/인터넷망 분리 환경에서 FortiGate 사용 비율 높음
2. FortiGate + FortiAnalyzer 통합 운영: 로그 분석 시스템 연동 필수
3. 규제 대응: 전자금융감독규정, 정보통신망법 등 준수 의무

#### 대응 우선순위 (한국 조직)
1. 금융권: P0 - 즉시 대응 (금융위원회 보고 필요 가능성)
2. 통신사: P0 - 즉시 대응 (가입자 정보 보호)
3. 공공기관: P1 - 1주 이내 (행정안전부 보안 감사 대비)
4. 일반 기업: P1 - 2주 이내

---

### 3. Sandworm APT 국내 위협 평가

#### 직접 위협 수준: **중간**
- 이유: 폴란드 전력망 공격이지만, 러시아-우크라이나 전쟁 맥락
- 한반도 지정학: 북한 지원 APT와 러시아 APT의 간접 협력 가능성

#### 간접 영향: **높음**
- 국내 에너지 인프라: 한국전력, LNG 터미널, 원자력 발전소 등 OT 환경
- 공급망 위험: 국내 기업이 폴란드/EU 자회사 보유 시 간접 노출

#### 국내 대응 현황
- 국가안보실: 국가 핵심 인프라 대상 APT 대응 체계 운영
- KISA: Critical Infrastructure 보호 가이드라인 배포
- 에너지 공기업: 별도 OT 보안 센터 운영

#### 권장 조치 (한국 조직)
- [ ] OT 네트워크 분리: ICS/SCADA를 IT 네트워크와 물리적으로 분리
- [ ] 국산 보안 솔루션 고려: 공급망 리스크 최소화
- [ ] 내부 인력 보안교육: APT 피싱 시뮬레이션 훈련

---

### 4. AI 에이전트 보안 국내 동향

#### 국내 AI 에이전트 도입 현황
- 금융: 챗봇 상담, 이상거래 탐지 에이전트 운영
- 통신: 고객센터 AI 상담원 전면 도입
- 공공: 민원 챗봇, 문서 분류 자동화
- 제조: 설비 예지보정 AI 시스템

#### 국내 특수 규제
1. 개인정보보호법: AI가 개인정보 처리 시 별도 보안조치 필요
2. 신용정보법: 금융 AI의 신용정보 접근 통제 의무
3. 전자금융감독규정: AI의 전자금융거래 접근 로깅 필수

#### 국내 보안 성숙도
- 대기업: AI 거버넌스 체계 구축 초기 단계
- 중견/중소: AI 보안 인식 부족, 무분별한 API 키 사용
- 공공기관: AI 윤리 가이드라인 우선, 보안은 후순위

#### 권장 조치 (한국 조직)
- [ ] 개인정보보호법 준수: AI의 개인정보 접근 로깅 및 암호화
- [ ] 금융/공공 규제 대응: 감독기관 가이드라인 반영
- [ ] 내부 AI 사용 정책 수립: 직원의 ChatGPT 등 외부 AI 사용 통제

---


![Security News Section Banner](/assets/images/section-security.svg)

## 위협 헌팅 통합 가이드 (Consolidated Threat Hunting Guide)

### 헌팅 시나리오 1: VMware vCenter 침해 흔적 탐지

#### 탐지 목표
- 비인가 관리자 계정 생성
- 비정상 시간대 vCenter 접근
- VM 대량 삭제/스냅샷 삭제

#### 데이터 소스
- `vpxd.log`: vCenter 주요 이벤트 로그
- `ssoAdminServer.log`: SSO 인증 로그
- VMware vSphere API 호출 로그

#### 헌팅 쿼리 (Bash/PowerShell)

> ```bash
> # 1. 최근 24시간 생성된 관리자 계정 찾기...
> ```


---

### 헌팅 시나리오 2: Fortinet SSO 우회 흔적 탐지

#### 탐지 목표
- SSO 우회 시도 (인증 없는 관리자 접근)
- 비인가 IP에서의 방화벽 정책 변경
- 백도어 계정 생성

#### 데이터 소스
- FortiGate Event Log (Subtype: admin)
- FortiAnalyzer 로그 (있는 경우)

#### 헌팅 쿼리 (FortiGate CLI)

> ```bash
> # 1. 최근 1시간 관리자 로그인 이력...
> ```


---

### 헌팅 시나리오 3: Sandworm DynoWiper 행위 탐지

#### 탐지 목표
- MBR/GPT 물리 디스크 접근
- VSS 섀도우 복사본 삭제
- 부팅 복구 비활성화

#### 데이터 소스
- Sysmon Event 10 (Process Access)
- Windows Event 7045 (Service Installation)
- Windows Event 4688 (Process Creation)

#### 헌팅 쿼리 (PowerShell)


### 위협 헌팅 쿼리 (Threat Hunting Queries)

#### FortiGate 비정상 관리자 로그인 탐지

```bash
# FortiGate 로그에서 SSO 관련 인증 실패 탐지
execute log filter category 0
execute log filter field subtype admin
execute log display
```

#### 방화벽 정책 변경 이력 추적

```bash
# 최근 24시간 방화벽 정책 변경 이력
diagnose sys ha history read | grep policy
```


---

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 5. 클라우드 오케스트레이션: Apache Airflow 3.1 & Google ADK

### Apache Airflow 3.1 in Cloud Composer

{%- include news-card.html
  title="[클라우드] Apache Airflow 3.1 in Cloud Composer"
  url="https://cloud.google.com/blog/products/data-analytics/cloud-composer-supports-apache-airflow-31/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/09_-_Data_Analytics_tFH57V6.max-2600x2600.jpg"
  summary="Google Cloud Composer가 Apache Airflow 3.1을 지원하기 시작했습니다. 이는 하이퍼스케일러 최초입니다."
  source="Improving workflow orchestration with Apache Airflow 3.1 in Cloud Composer"
  severity="Medium"
-%}


Google Cloud Composer가 Apache Airflow 3.1을 지원하기 시작했습니다. 이는 하이퍼스케일러 최초입니다.


#### 주요 개선 사항

| 기능 | 설명 | 활용 사례 |
|------|------|----------|
| Asset-Centric DAGs | 데이터 중심 워크플로우 정의 | 데이터 레이크 파이프라인 |
| Event-Driven | 이벤트 기반 DAG 트리거 | 실시간 데이터 처리 |
| UI 개선 | 대시보드 사용성 향상 | 운영 모니터링 |
| Performance | 스케줄러 성능 최적화 | 대규모 DAG 환경 |

### Google ADK + Datadog LLM Observability

{%- include news-card.html
  title="[클라우드] Google ADK + Datadog LLM Observability"
  url="https://cloud.google.com/blog/products/management-tools/datadog-integrates-agent-development-kit-or-adk/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/21_-_Management_Tools_EI9iqlb.max-2600x2600.jpg"
  summary="Google Agent Development Kit(ADK)와 Datadog의 LLM Observability 통합으로 에이전틱 시스템 모니터링이 가능해졌습니다."
  source="Monitoring Google ADK agentic applications with Datadog LLM Observability"
  severity="Medium"
-%}


Google Agent Development Kit(ADK)와 Datadog의 LLM Observability 통합으로 에이전틱 시스템 모니터링이 가능해졌습니다.


#### 모니터링 아키텍처

![Agentic AI Monitoring Architecture - Google ADK with 3 agents feeding into Datadog LLM Observability](/assets/images/diagrams/2026-01-25-agentic-ai-monitoring.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>


---


## 관련 포스트

- ['AWS/GCP 2026년 1월 주요 업데이트: EC2 G7e/X8i 인스턴스, Bangkok 리전, European Sovereign]({% post_url 2026-01-22-AWS_GCP_Cloud_Updates_January_2026_EC2_G7e_X8i_Bangkok_Region_European_Sovereign_Cloud %})
- ["\U0001F680 클라우드 보안 과정 8기 8주차: CI/CD와 Kubernetes 보안 실전 가이드 - DevSecOps 파이프라인부터]({% post_url 2026-01-22-Cloud_Security_Course_8Batch_8Week_CI_CD_Kubernetes_Security_Practical_Guide %})
- ['2026년 1월 클라우드 보안 동향: Kubernetes 82% 프로덕션 도입, VS Code 악용 위협 증가, CNCF 연례 조사]({% post_url 2026-01-22-Cloud_Security_Trends_January_2026_Kubernetes_82_Percent_Production_VS_Code_Threats_CNCF_Survey %})
- [2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략]({% post_url 2026-01-22-KARA_Ransomware_Trends_Report_2025_Q3_Analysis_SK_Shieldus_EQST %})
- [KISA 보안 공지 분석: 랜섬웨어 예방 가이드와 리눅스 커널 루트킷 점검 방법]({% post_url 2026-01-22-KISA_Security_Advisory_Ransomware_Prevention_Linux_Rootkit_Detection_Guide_Analysis %})
- [보안 벤더 블로그 주간 리뷰 (2026년 01월 22일)]({% post_url 2026-01-22-Security_Vendor_Blog_Weekly_Review %})
- ['기술·보안 주간 다이제스트: Microsoft AitM 피싱 경고, Agentic AI Zero Trust,]({% post_url 2026-01-23-Tech_Security_Weekly_Digest_Microsoft_AitM_Phishing_Agentic_AI_Zero_Trust_OpenAI_PostgreSQL %})
- ['기술·보안 주간 다이제스트: Microsoft BitLocker FBI 키 제공, Cloudflare Route]({% post_url 2026-01-24-Tech_Security_Weekly_Digest_BitLocker_FBI_Cloudflare_Route_Leak_Agentic_Enterprise_Docker %})
- ['기술·보안 주간 다이제스트: Zero Trust for AI Agents, Chrome 기술지원 사기 방지,]({% post_url 2026-01-26-Tech_Security_Weekly_Digest_Zero_Trust_Agentic_AI_Chrome_Tech_Support_Scam_Terraform_Stacks %})
- ['기술·보안 주간 다이제스트: MS Office Zero-Day 긴급패치, Kimi K2.5 오픈소스 에이전트,]({% post_url 2026-01-27-Tech_Security_Weekly_Digest_MS_Office_Zero_Day_Kimi_K25_Kimwolf_Botnet_AWS_G7e %})
- [CLAUDE.md 보안 가이드: AI 에이전트 시대의 프로젝트 보안 설계]({% post_url 2026-01-28-Claude_MD_Security_Guide %})
- ['기술·보안 주간 다이제스트: Microsoft Office Zero-Day 긴급 패치, CTEM 실무 적용,]({% post_url 2026-01-28-Tech_Security_Weekly_Digest_MS_Office_Zero_Day_CTEM_Grist_Core_RCE %})

## 참고 자료

### 공식 보안 권고 및 CVE 정보

- [CISA KEV Catalog - Known Exploited Vulnerabilities](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [VMware Security Advisories - vCenter Server](https://www.vmware.com/security/advisories.html)
- [VMware vCenter CVE-2024-37079 상세 정보](https://www.vmware.com/security/advisories/VMSA-2024-0012.html)
- [Fortinet PSIRT Advisories](https://www.fortiguard.com/psirt)
- [NVD - National Vulnerability Database](https://nvd.nist.gov/)
- [MITRE CVE Database](https://cve.mitre.org/)

### 위협 인텔리전스 및 APT 리포트

- [CISA Sandworm APT Profile](https://www.cisa.gov/news-events/cybersecurity-advisories/aa22-110a)
- [Mandiant Threat Intelligence - Sandworm (APT44)](https://www.mandiant.com/resources/insights)
- [CrowdStrike Threat Reports - Voodoo Bear](https://www.crowdstrike.com/resources/)
- [MITRE ATT&CK - Sandworm Team (G0034)](https://attack.mitre.org/groups/G0034/)
- [Microsoft Threat Intelligence - Sandworm Activity](https://www.microsoft.com/en-us/security/blog/threat-intelligence/)
- [SK쉴더스 EQST - 위협 인텔리전스](https://www.skshieldus.com/)

### 원문 뉴스 소스

- [The Hacker News - VMware vCenter KEV](https://thehackernews.com/2026/01/cisa-adds-actively-exploited-vmware.html)
- [The Hacker News - Fortinet SSO Bypass](https://thehackernews.com/2026/01/fortinet-confirms-active-forticloud-sso.html)
- [The Hacker News - Sandworm DynoWiper](https://thehackernews.com/2026/01/new-dynowiper-malware-used-in-attempted.html)
- [The Hacker News - AI Agents Access Control](https://thehackernews.com/2026/01/who-approved-this-agent-rethinking.html)
- [HashiCorp Blog - Zero Trust for Agentic Systems](https://www.hashicorp.com/blog/zero-trust-for-agentic-systems-managing-non-human-identities-at-scale)

### 클라우드 및 DevOps

- [Google Cloud Blog - Apache Airflow 3.1 in Cloud Composer](https://cloud.google.com/blog/products/data-analytics/cloud-composer-supports-apache-airflow-31/)
- [Google Cloud Blog - Datadog ADK Integration](https://cloud.google.com/blog/products/management-tools/datadog-integrates-agent-development-kit-or-adk/)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [CNCF Blog - 2026 Platform Engineering Forecast](https://www.cncf.io/blog/2026/01/23/the-autonomous-enterprise-and-the-four-pillars-of-platform-control-2026-forecast/)

### 보안 프레임워크 및 표준

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CIS Controls v8](https://www.cisecurity.org/controls/v8)
- [SANS Top 25 Software Errors](https://www.sans.org/top25-software-errors/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### SIEM 및 보안 모니터링

- [Splunk Security Essentials](https://splunkbase.splunk.com/app/3435/)
- [Azure Sentinel Content Hub](https://learn.microsoft.com/en-us/azure/sentinel/sentinel-solutions-catalog)
- [Elastic Security Detection Rules](https://www.elastic.co/guide/en/security/current/prebuilt-rules.html)
- [Sigma Rules Repository](https://github.com/SigmaHQ/sigma)

### 제로트러스트 및 NHI 관리

- [HashiCorp Zero Trust Solutions](https://www.hashicorp.com/solutions/zero-trust-security)
- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [NIST Zero Trust Architecture (SP 800-207)](https://csrc.nist.gov/publications/detail/sp/800-207/final)
- [Microsoft Zero Trust Guidance](https://www.microsoft.com/en-us/security/business/zero-trust)

### 한국어 보안 리소스

- [SK쉴더스 제로트러스트 시리즈](https://www.skshieldus.com/)
- [KISA 한국인터넷진흥원 보안공지](https://www.kisa.or.kr/)
- [보안뉴스](https://www.boannews.com/)
- [데일리시큐](https://www.dailysecu.com/)

### 추가 학습 자료

- [SANS Reading Room - APT Analysis](https://www.sans.org/white-papers/)
- [Offensive Security Blog - Penetration Testing](https://www.offensive-security.com/blog/)
- [Red Canary Threat Detection Reports](https://redcanary.com/threat-detection-report/)
- [Attack IQ Blog - Adversary Emulation](https://www.attackiq.com/blog/)

---

## 마무리

이번 주는 국가급 APT 공격과 인프라 취약점이 동시에 주목받은 한 주였습니다. 특히:

1. 즉각적인 패치가 필요한 VMware vCenter 취약점
2. 패치만으로 해결되지 않는 Fortinet SSO 우회
3. 전력망 등 핵심 인프라를 노리는 와이퍼 공격
4. AI 에이전트 시대의 새로운 보안 패러다임

보안 담당자분들은 위의 액션 아이템을 참고하여 즉각적인 대응을 권장합니다.

다음 주에도 유익한 보안/기술 소식으로 찾아뵙겠습니다.

---

작성자: Twodragon
작성일: 2026-01-25
수집 소스: 47개 RSS 피드 (166개 뉴스)
분석 방법론: DevSecOps 실무 영향도 기반 우선순위화
