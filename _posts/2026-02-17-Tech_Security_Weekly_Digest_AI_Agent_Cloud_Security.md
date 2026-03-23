---

layout: post
title: "AI 에이전트 토큰 탈취, 패스워드 매니저 취약점, 서버리스 방어 전략"
date: 2026-02-17 12:35:29 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI-Agent, Password-Manager, Serverless]
excerpt: "Infostealer 악성코드의 AI 에이전트 설정·토큰 탈취 신규 벡터, Bitwarden/Dashlane/LastPass 25개 패스워드 복구 공격, AWS AI 기반 서버리스 방어 심층 아키텍처 등 18건을 DevSecOps 실무 관점으로 분석한 2026년 2월 17일 주간 보안 다이제스트입니다."
description: "Infostealer 악성코드의 AI 에이전트 설정/토큰 탈취 신규 벡터, Bitwarden/Dashlane/LastPass 25개 패스워드 복구 공격, AWS AI 기반 서버리스 방어 심층 아키텍처 등 18건 분석."
author: Twodragon
comments: true
image: /assets/images/2026-02-17-Tech_Security_Weekly_Digest_AI_Agent_Cloud_Security.svg
image_alt: "Tech Security Weekly Digest February 17 2026 AI Agent Cloud Security"
toc: true
---
{% include ai-summary-card.html
  title='기술·보안 주간 다이제스트: AI 에이전트 토큰 탈취, 패스워드 매니저 취약점, 서버리스 방어'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">Weekly-Digest</span> <span class="tag">2026</span> <span class="tag">AI-Agent</span> <span class="tag">Password-Manager</span> <span class="tag">Serverless</span>'
  highlights_html='<li><strong>포인트 1</strong>: Infostealer 악성코드의 AI 에이전트 설정/토큰 탈취 신규 벡터, Bitwarden/Dashlane/LastPass 25개 패스워드 복구 공격, AWS AI 기반 서버리스 방어 심층 아키텍처 등 18건 분석</li> <li><strong>포인트 2</strong>: 실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다</li> <li><strong>포인트 3</strong>: 운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다</li>'
  period='2026-02-17 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

## Executive Summary

> **경영진 브리핑**: Infostealer 악성코드의 AI 에이전트 설정/토큰 탈취 신규 벡터, Bitwarden/Dashlane/LastPass 25개 패스워드 복구 공격, AWS AI 기반 서버리스 방어 심층 아키텍처 등 18건 분석.

### 위험도 평가

| 항목 | 위험도 | 설명 |
|------|--------|------|
| 전체 위험도 | 🟡 중간 | 주요 보안 위협 모니터링 및 패치 적용 필요 |

---

## 소개

안녕하세요, Twodragon입니다.

2026년 2월 17일 기준 지난 24시간 동안의 주요 기술 및 보안 뉴스 심층 분석입니다.

> 이전 다이제스트: [SolarWinds RCE, UNC3886, LLM Attack (2026.02.10)]({{ site.baseurl }}/security/2026/02/10/Security_Digest_SolarWinds_UNC3886_LLM_Attack.html)

수집 통계:
- 전체: 18건
- 보안: 5건
- AI/ML: 10건
- 클라우드: 3건
- 블록체인: 5건

---

## 빠른 참조

| 카테고리 | 출처 | 주요 발견 | 영향도 |
|----------|--------|-------------|--------|
| 보안 | The Hacker News | Infostealer가 AI 에이전트 설정 파일 및 게이트웨이 토큰 탈취 | HIGH |
| 보안 | The Hacker News | Bitwarden/Dashlane/LastPass에서 25개 패스워드 복구 공격 발견 | HIGH |
| 보안 | AWS Security Blog | 서버리스 마이크로서비스를 위한 AI 기반 Defense-in-Depth | MEDIUM |
| 보안 | The Hacker News | 주간 요약: Outlook Add-In 하이재킹, 0-Day 패치 | HIGH |
| 보안 | The Hacker News | 리투아니아 e-사회 보안 프레임워크 분석 | LOW |
| 클라우드 | AWS Blog | 5세대 AMD EPYC 탑재 EC2 Hpc8a - 성능 40% 향상 | MEDIUM |
| 클라우드 | AWS Blog | 맞춤형 Amazon Nova 모델을 위한 SageMaker Inference | MEDIUM |

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. 보안 뉴스

### 1.1 Infostealer, AI 에이전트 설정 파일 및 게이트웨이 토큰 탈취

{%- include news-card.html
  title="[보안] Infostealer, AI 에이전트 설정 파일 및 게이트웨이 토큰 탈취"
  url="https://thehackernews.com/2026/02/infostealer-steals-ai-agent-configuration-files-and-gateway-tokens.html"
  summary="사이버보안 연구진이 AI 에이전트 설정 파일과 게이트웨이 토큰을 적극적으로 탈취하는 Infostealer 악성코드를 발견했습니다. 이는 브라우저 자격증명 탈취에서 AI 에이전트 신원 및 접근 설정 수집으로의 진화로, Infostealer 위협 지형에서 매우 중요한 변화를 의미합니다."
  source="The Hacker News"
  severity="High"
-%}


사이버보안 연구진이 AI 에이전트 설정 파일과 게이트웨이 토큰을 적극적으로 탈취하는 Infostealer 악성코드를 발견했습니다. 이는 브라우저 자격증명 탈취에서 AI 에이전트 신원 및 접근 설정 수집으로의 진화로, Infostealer 위협 지형에서 매우 중요한 변화를 의미합니다.

중요한 이유:

AI 에이전트 토큰 하나가 탈취되면 공격자는 해당 에이전트가 접속하는 모든 시스템에 접근할 수 있습니다. 기업들이 데이터베이스, API, 클라우드 서비스 등 광범위한 시스템 접근 권한을 가진 AI 에이전트를 배포하면서, 이러한 토큰은 고가치 공격 목표가 되고 있습니다.

공격 체인:

```text
1. Infostealer가 개발자/운영자 워크스테이션 감염
2. AI 에이전트 설정 파일 탐색 (예: .env, config.yaml, agent.json)
3. OAuth 토큰, API 키, 게이트웨이 자격증명 추출
4. C2 서버로 유출 - 공격자가 AI 에이전트로 위장
5. 에이전트가 권한을 가졌던 모든 시스템에 접근
```

MITRE ATT&CK 매핑:

| 기법 | ID | 설명 |
|-----------|------|-------------|
| Credentials from Files | T1552.001 | AI 에이전트 설정 파일 수집 |
| Steal Application Access Token | T1528 | 게이트웨이 토큰 추출 |
| Valid Accounts: Cloud | T1078.004 | 탈취한 토큰을 이용한 신원 위장 |

권장 조치:
- AI 에이전트 자격증명은 Secrets Manager / HashiCorp Vault에 저장하고, 로컬 설정 파일에는 절대 저장 금지
- AI 에이전트 인증에 단기 자동 갱신 토큰 적용
- AI 에이전트 설정 디렉토리 접근을 탐지하는 EDR 규칙 추가
- 에이전트 서비스 계정의 비정상적인 API 호출 모니터링 (비정상 시간대, IP, 요청 패턴)


---

### 1.2 주요 클라우드 패스워드 매니저에서 25개 패스워드 복구 공격 발견

{%- include news-card.html
  title="[보안] 주요 클라우드 패스워드 매니저에서 25개 패스워드 복구 공격 발견"
  url="https://thehackernews.com/2026/02/study-uncovers-25-password-recovery.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgBPbskdafjFepjzUnEOcPNFvk1UceqE9lVwhurVxvrqJ3_1VhbKg-XcZjTrVpt2aqk_uv6Sodg9NMcoTvkVEeoAhNUU9X_0ltI9oHpnTIA-a28iDGnudnxJklcADpfz5llcUEStKI7Nt7IjW3vhA_DyO7rKG03dgj8KTFfrpxamTqy7xEciFwLzeS-lXEb/s1700-e365/password-managers.jpg"
  summary="Scarlata, Torrisi, Backendal, Paterson으로 구성된 연구팀이 Bitwarden, Dashlane, LastPass를 포함한 주요 클라우드 패스워드 매니저에서 25개의 패스워드 복구 공격 벡터를 발견했습니다. 공격 심각도는 무결성 침해부터 조직 전체 볼트의 완전 탈취까지 다양합니다."
  source="The Hacker News"
  severity="High"
-%}


Scarlata, Torrisi, Backendal, Paterson으로 구성된 연구팀이 Bitwarden, Dashlane, LastPass를 포함한 주요 클라우드 패스워드 매니저에서 25개의 패스워드 복구 공격 벡터를 발견했습니다. 공격 심각도는 무결성 침해부터 조직 전체 볼트의 완전 탈취까지 다양합니다.

발견된 공격 유형:

| 유형 | 영향 제품 | 심각도 | 설명 |
|----------|----------|----------|-------------|
| 복구 키 가로채기 | 세 제품 모두 | Critical | 설정/재설정 흐름 중 복구 키 탈취 |
| 관리자 복구 남용 | Bitwarden, LastPass | High | 기업용 관리자 복구 메커니즘 악용 가능 |
| 이메일 기반 복구 우회 | Dashlane, LastPass | High | 복구 체인 내 이메일 검증 취약점 |
| 볼트 무결성 침해 | 세 제품 모두 | Medium | 감지 없이 암호화된 볼트 내용 변조 |

권장 조치:
- [ ] 조직의 패스워드 매니저 복구 설정 감사
- [ ] 가능한 경우 패스워드 복구 메커니즘 비활성화, MFA로 대체
- [ ] 비정상적인 볼트 접근 패턴 모니터링 (대량 내보내기, 비정상 지역)
- [ ] 관리자/특권 계정 마스터 패스워드 즉시 교체
- [ ] 볼트 접근에 하드웨어 키(FIDO2) 강제 적용 검토


---

### 1.3 AWS, 서버리스 마이크로서비스를 위한 AI 기반 Defense-in-Depth

{%- include news-card.html
  title="[보안] AWS, 서버리스 마이크로서비스를 위한 AI 기반 Defense-in-Depth"
  url="https://aws.amazon.com/blogs/security/building-an-ai-powered-defense-in-depth-security-architecture-for-serverless-microservices/"
  image="https://d2908q01vomqb2.cloudfront.net/827bfc458708f0b442009c9c9836f7e4b65557fb/2020/06/03/Blog-Post_thumbnail.png"
  summary="AWS Security Blog에서 서버리스 마이크로서비스를 위한 AI 기반 Defense-in-Depth 아키텍처 구축에 관한 포괄적인 가이드를 공개했습니다. 이 가이드는 기계 속도로 취약점을 찾아내고, 공격을 자동화하며, 탐지를 회피하는 AI 강화 위협에 대응하기 위한 것으로, 기존 경계 기반 보안의 한계를 극복하는 방안을 다룹니다."
  source="AWS Security Blog"
  severity="Medium"
-%}


AWS Security Blog에서 서버리스 마이크로서비스를 위한 AI 기반 Defense-in-Depth 아키텍처 구축에 관한 포괄적인 가이드를 공개했습니다. 이 가이드는 기계 속도로 취약점을 찾아내고, 공격을 자동화하며, 탐지를 회피하는 AI 강화 위협에 대응하기 위한 것으로, 기존 경계 기반 보안의 한계를 극복하는 방안을 다룹니다.

주요 아키텍처 레이어:

| 레이어 | AWS 서비스 | 목적 |
|-------|-------------|---------|
| 엣지 보호 | WAF + Shield Advanced | DDoS 완화, 봇 관리 |
| 런타임 보호 | GuardDuty + Lambda Insights | 함수 실행 이상 탐지 |
| 데이터 보호 | KMS + Macie | 암호화, 민감 데이터 탐지 |
| 신원 관리 | IAM + Cognito | 최소 권한, 세분화된 접근 제어 |
| 모니터링 | Security Hub + CloudTrail | 중앙화된 보안 발견사항, 감사 추적 |
| 대응 | EventBridge + Step Functions | 자동화된 보안 대응 워크플로우 |

권장 조치:
- [ ] Lambda 실행 역할 권한 감사 - 대부분 과도한 권한 부여 상태
- [ ] 런타임 위협 탐지를 위한 GuardDuty Lambda Protection 활성화
- [ ] 함수 단위 네트워크 정책 적용 (VPC 엔드포인트, 보안 그룹)
- [ ] 주요 보안 발견사항에 대한 EventBridge 자동 대응 추가


---

### 1.4 주간 요약: Outlook Add-In 하이재킹, 0-Day 패치

{%- include news-card.html
  title="[보안] 주간 요약: Outlook Add-In 하이재킹, 0-Day 패치"
  url="https://thehackernews.com/2026/02/weekly-recap.html"
  summary="The Hacker News 주간 보안 요약에서 즉각적인 조치가 필요한 주요 위협을 다룹니다:"
  source="The Hacker News"
  severity="Critical"
-%}


The Hacker News 주간 보안 요약에서 즉각적인 조치가 필요한 주요 위협을 다룹니다:

- Outlook Add-In 하이재킹: 공격자가 Outlook 애드인 사이드로딩을 악용해 정상 이메일 클라이언트를 통한 지속성 확보 및 데이터 유출 실행
- 다수의 0-Day 패치: 이번 주 주요 플랫폼에서 실제 악용되고 있는 여러 제로데이 취약점 패치 배포

권장 조치:
- [ ] Outlook 애드인 정책 검토 - IT 승인 애드인만 사이드로딩 허용
- [ ] 벤더 권고에 따라 0-Day 패치 즉시 배포
- [ ] 엔드포인트 텔레메트리를 통한 비인가 Outlook 애드인 설치 모니터링


---

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 2. 클라우드 & 인프라

### 2.1 Amazon EC2 Hpc8a: 5세대 AMD EPYC, 성능 40% 향상

{%- include news-card.html
  title="[클라우드] Amazon EC2 Hpc8a: 5세대 AMD EPYC, 성능 40% 향상"
  url="https://aws.amazon.com/blogs/aws/amazon-ec2-hpc8a-instances-powered-by-5th-gen-amd-epyc-processors-are-now-available/"
  image="https://d2908q01vomqb2.cloudfront.net/da4b9237bacccdf19c0760cab7aec4a8359010b0/2026/02/11/EC2_with_gradient-2.png"
  summary="AWS가 5세대 AMD EPYC 프로세서를 탑재한 EC2 Hpc8a 인스턴스를 출시했습니다. 컴퓨팅 집약적인 HPC 워크로드에서 최대 40% 높은 성능, 향상된 메모리 대역폭, 300Gbps Elastic Fabric Adapter(EFA) 네트워킹을 제공합니다."
  source="AWS Blog"
  severity="Medium"
-%}


AWS가 5세대 AMD EPYC 프로세서를 탑재한 EC2 Hpc8a 인스턴스를 출시했습니다. 컴퓨팅 집약적인 HPC 워크로드에서 최대 40% 높은 성능, 향상된 메모리 대역폭, 300Gbps Elastic Fabric Adapter(EFA) 네트워킹을 제공합니다.

실무 고려사항:
- 마이그레이션 전 현재 HPC 병목 지점(CFD, FEA, 분자 시뮬레이션) 프로파일링 필수
- EFA 300Gbps는 적절한 MPI 설정과 배치 그룹 구성 필요
- 운영 전환 전 기존 HPC 클러스터 스크립트 호환성 검증 필요


---

### 2.2 맞춤형 Amazon Nova 모델을 위한 SageMaker Inference

{%- include news-card.html
  title="[클라우드] 맞춤형 Amazon Nova 모델을 위한 SageMaker Inference"
  url="https://aws.amazon.com/blogs/aws/announcing-amazon-sagemaker-inference-for-custom-amazon-nova-models/"
  image="https://d2908q01vomqb2.cloudfront.net/da4b9237bacccdf19c0760cab7aec4a8359010b0/2025/11/25/Nova-4.png"
  summary="AWS가 인스턴스 유형, 자동 스케일링 정책, 동시성 설정을 구성할 수 있는 맞춤형 Amazon Nova 모델용 SageMaker Inference 지원을 발표했습니다."
  source="AWS Blog"
  severity="Medium"
-%}


AWS가 인스턴스 유형, 자동 스케일링 정책, 동시성 설정을 구성할 수 있는 맞춤형 Amazon Nova 모델용 SageMaker Inference 지원을 발표했습니다.

보안 고려사항:
- 최소 권한 원칙을 위해 엔드포인트별 IAM 역할 범위 제한
- VPC 엔드포인트를 통해 추론 트래픽 라우팅 (공개 인터넷 우회)
- 모델 아티팩트를 저장하는 S3 버킷에 SSE-KMS 암호화 적용


---

![Blockchain Web3 News Section Banner](/assets/images/section-blockchain.svg)

## 3. 블록체인 뉴스

### 3.1 비트코인 약세: $71,800 저항선 유지, 하방 리스크 지속

{%- include news-card.html
  title="[블록체인] 비트코인 약세: $71,800 저항선 유지, 하방 리스크 지속"
  url="https://bitcoinmagazine.com/markets/bitcoin-bears-dominate-failure-to-break-71800-keeps-downside-risk-alive"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/02/bullish-price-thumbnail-1.webp"
  summary="비트코인이 $71,800 저항선 돌파에 실패하며, 주요 지지선은 $65,650에 형성되어 있습니다. 이 지지선이 무너지면 $63,000, 이후 피보나치 레벨 $57,800까지 하락 가능성이 있습니다. 상방은 $71,800~$74,500 구간에서 막혀 있습니다."
  source="Bitcoin Magazine"
  severity="Medium"
-%}


비트코인이 $71,800 저항선 돌파에 실패하며, 주요 지지선은 $65,650에 형성되어 있습니다. 이 지지선이 무너지면 $63,000, 이후 피보나치 레벨 $57,800까지 하락 가능성이 있습니다. 상방은 $71,800~$74,500 구간에서 막혀 있습니다.

보안 시사점: 시장 불확실성이 높아지면 암호화폐 투자자를 대상으로 한 피싱/스캠 활동이 증가합니다. 가짜 거래소 사이트 및 투자 사기 캠페인을 지속 모니터링하세요.


---

### 3.2 Payjoin Foundation, 501(c)(3) 지위 획득

{%- include news-card.html
  title="[블록체인] Payjoin Foundation, 501(c)(3) 지위 획득"
  url="https://bitcoinmagazine.com/business/payjoin-foundation-gains-501c3-status-enabling-tax-deductible-donations-for-bitcoin-privacy-development"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/02/tn-3.webp"
  summary="Payjoin Dev Kit을 운영하는 비영리단체 Payjoin Foundation이 IRS로부터 501(c)(3) 면세 지위를 획득했습니다. 이를 통해 프라이버시를 강화하는 비트코인 프로토콜 개발에 세금 공제 기부가 가능해졌으며, 프라이버시와 수수료 효율성을 모두 개선하는 Payjoin 트랜잭션 도입이 가속화될 전망입니다."
  source="Bitcoin Magazine"
  severity="Medium"
-%}


Payjoin Dev Kit을 운영하는 비영리단체 Payjoin Foundation이 IRS로부터 501(c)(3) 면세 지위를 획득했습니다. 이를 통해 프라이버시를 강화하는 비트코인 프로토콜 개발에 세금 공제 기부가 가능해졌으며, 프라이버시와 수수료 효율성을 모두 개선하는 Payjoin 트랜잭션 도입이 가속화될 전망입니다.


---

## 4. 기타 주요 뉴스

| 제목 | 출처 | 요약 |
|-------|--------|---------|
| [AWS 주간 요약: EC2 M8azn, Bedrock 오픈 웨이트 모델](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-amazon-ec2-m8azn-instances-new-open-weights-models-in-amazon-bedrock-and-more-february-16-2026/) | AWS Blog | 네트워크 집약적 워크로드용 M8azn, Bedrock에 새로운 오픈 웨이트 모델 추가. 컴플라이언스를 위한 라이선스 조건 확인 필요 |
| [리투아니아의 안전하고 포용적인 e-사회](https://thehackernews.com/2026/02/safe-and-inclusive-e-society.html) | The Hacker News | 디지털 사회를 위한 리투아니아의 사이버보안 프레임워크 - 국가 수준 보안 정책의 참고 사례 |

---

## 5. 트렌드 분석

| 트렌드 | 기사 수 | 핵심 인사이트 |
|-------|----------|-------------|
| AI 에이전트 보안 | 3건 | AI 에이전트가 새로운 공격 표면을 형성 - 설정 파일, 토큰, 실행 환경이 고가치 공격 목표로 부상 |
| 인증 인프라 | 3건 | 패스워드 매니저 취약점 + 인증 시스템을 겨냥한 0-Day 익스플로잇은 신원이 새로운 경계임을 확인 |
| 서버리스 보안 | 2건 | 위협이 기계 속도로 자동화됨에 따라 AI 기반 Defense-in-Depth가 필수화 |
| 클라우드 인프라 | 3건 | AMD EPYC HPC + SageMaker Nova + Bedrock 오픈 웨이트가 클라우드 AI 역량 확대 |

이번 기간의 지배적인 트렌드는 AI 에이전트 보안이 핵심 과제로 부상하고 있다는 점입니다. 기업 환경에서 광범위한 시스템 접근 권한을 가진 AI 에이전트가 급증하면서, 공격 표면이 전통적인 자격증명에서 에이전트 설정 파일과 게이트웨이 토큰으로 이동하고 있습니다. 조직은 AI 에이전트 자격증명을 특권 서비스 계정과 동일한 수준으로 관리해야 합니다.

---

## 조치 체크리스트

### P0 (즉시 조치)

- [ ] Outlook Add-In 사이드로딩: IT 승인 애드인만 허용하도록 제한, 0-Day 패치 즉시 배포
- [ ] AI 에이전트 자격증명: 모든 AI 에이전트 토큰/설정 파일이 Secrets Manager/Vault에 저장되어 있는지 확인 (로컬 파일 또는 git 저장소 저장 금지)
- [ ] 패스워드 매니저 복구: Bitwarden/Dashlane/LastPass의 복구 메커니즘 설정 감사, 가능한 경우 비활성화

### P1 (7일 이내)

- [ ] AI 에이전트 설정 디렉토리 접근 탐지를 위한 EDR 규칙 구현
- [ ] 조직 전체 볼트에 대한 패스워드 매니저 MFA 적용 현황 검토
- [ ] 최소 권한 준수를 위한 Lambda 실행 역할 권한 감사

### P2 (30일 이내)

- [ ] 서버리스 환경을 위한 AI 기반 Defense-in-Depth 구현 (GuardDuty Lambda Protection)
- [ ] AI 에이전트 인증을 위한 단기 자동 갱신 토큰 전략 검토
- [ ] Hpc8a 인스턴스를 활용한 HPC 워크로드 마이그레이션 기회 검토

---


---

## 참고자료

| 리소스 | 링크 |
|----------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |
| AWS Security Blog | [aws.amazon.com/blogs/security](https://aws.amazon.com/blogs/security/) |

---

작성자: Twodragon
