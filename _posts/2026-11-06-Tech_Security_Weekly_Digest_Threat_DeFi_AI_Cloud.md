---
layout: post
title: "2026년 11월 06일 주간 보안 다이제스트: 패치·AI 에이전트·클라우드 (30건)"
date: 2026-11-06 00:53:32 +0900
last_modified_at: 2026-11-06T00:53:32+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Threat, DeFi, AI, Cloud]
excerpt: "Apache OFBiz 원격 코드 실행·노출 관리 플랫폼 등 2026년 11월 06일 확인한 후보 30건의 보안/기술 이슈 중 핵심 기사를 운영 관점에서 점검합니다. 본문 말미의 실무 체크리스트에 팀에서 바로 나눠 가질 점검 항목을 정리했습니다."
description: "2026년 11월 06일 보안 뉴스 요약. The Hacker News 등 후보 30건에서 핵심 기사를 선별하고 Apache OFBiz, 노출 관리, OpenAI 보안 연구 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Threat, DeFi, AI]
author: Twodragon
comments: true
image: /assets/images/2026-11-06-Tech_Security_Weekly_Digest_Threat_DeFi_AI_Cloud.svg
image_alt: "Apache OFBiz, 노출 관리, OpenAI 보안 연구 - security digest overview"
toc: true
summary_card:
  title: "2026년 11월 06일 주간 보안 다이제스트: 패치·AI 에이전트·클라우드 (30건)"
  period: "2026년 11월 06일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Threat"
    - "DeFi"
    - "AI"
    - "Cloud"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "ThreatsDay: Apache OFBiz 원격 코드 실행·DreamHost 침해 소식" }
    - { source: "The Hacker News", title: "노출 관리 플랫폼만으로 해소되지 않는 보안 위험" }
    - { source: "The Hacker News", title: "OpenAI, 30시간 실행으로 Linux 권한 상승 익스플로잇 948개 생성" }
    - { source: "Google Cloud Blog", title: "자율 에이전트를 위한 개방형 인프라" }
redirect_from:
- /posts/2026/11/06/Tech_Security_Weekly_Digest_Threat_DeFi_AI_Cloud/
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 11월 06일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

본문은 분류 후보 30개 중 핵심 기사 15개를 선별했다. 아래 수치는 후보 집합의 통계이며 본문 카드 수와 다르다. 표와 카드의 심각도는 편집상 검토 우선순위이며, 공식 CVSS나 독자 조직의 침해 사실을 의미하지 않는다.

**분류 후보 통계:**
- **총 뉴스 수**: 30개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 5개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | ThreatsDay: Apache OFBiz 원격 코드 실행·DreamHost 침해 소식 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | 노출 관리 플랫폼만으로 해소되지 않는 보안 위험 | 🟠 High |
| 🔒 **Security** | The Hacker News | OpenAI, 30시간 실행으로 Linux 권한 상승 익스플로잇 948개 생성 | 🟠 High |
| 🤖 **AI/ML** | NVIDIA AI Blog | 호그와트 레거시, GeForce NOW에서 NVIDIA DLSS 5 적용 | 🟠 High |
| 🤖 **AI/ML** | OpenAI Blog | OpenAI, 책임 있는 AI 인프라 개발 원칙 발표 | 🟠 High |
| 🤖 **AI/ML** | Bitcoin Magazine | Riot, 280억 달러 텍사스 임대 계약의 임차인으로 Anthropic 명시 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 자율 에이전트를 위한 개방형 인프라 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 에이전트 시대의 기계 속도 개발·방어 전략 | 🟠 High |
| ☁️ **Cloud** | Google Cloud Blog | Google Public Sector Summit 주요 내용과 시사점 | 🟡 Medium |
| ⚙️ **DevOps** | Docker Blog | Docker·ActiveState, 신뢰할 수 있는 콘텐츠 협력 확대 | 🟠 High |

---

## 경영진 브리핑

- **긴급 대응 필요**: ThreatsDay: Apache OFBiz 원격 코드 실행·DreamHost 침해 소식 등 Critical 검토 우선순위로 분류한 보도 1건을 확인했습니다.
- **주요 모니터링 대상**: 노출 관리 플랫폼만으로 해소되지 않는 보안 위험, OpenAI, 30시간 실행으로 Linux 권한 상승 익스플로잇 948개 생성, 호그와트 레거시, GeForce NOW에서 NVIDIA DLSS 5 적용 등 High 검토 우선순위로 분류한 보도 7건은 자사 관련성을 먼저 확인해야 합니다.
- 공급망 보안 위협이 확인되었으며, 서드파티 의존성 검토와 SBOM 업데이트를 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 ThreatsDay: Apache OFBiz 원격 코드 실행·DreamHost 침해 소식

{% include news-card.html
  title="ThreatsDay: Apache OFBiz 원격 코드 실행·DreamHost 침해 소식"
  url="https://thehackernews.com/2026/11/threatsday-apache-ofbiz-rce-dreamhost.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj37A8QMI4tUKrluDLCSgawVjQQeZ6c6NrfWLMLUjrI6vRhpt8Tlw4PNnfF49ZlOTtW28Cfb035jo-j22auCrWauuE-JpHfKMFSVfIQtUZjn1eETLFhQEev0FFafFlGz8W6r-96FPmTWlFGTR3RhV869PbcYkO4YPi5nD-zQVGHSZ8d39OmhecF693dj4-x/s1600/tds.jpg"
  summary="The Hacker News는 Apache OFBiz 원격 코드 실행과 DreamHost 침해 등을 묶어 소개했습니다. 단일 사고로 간주하지 말고 원문의 개별 항목과 자사 자산의 연관성을 확인해야 합니다."
  source="The Hacker News"
  severity="Critical"
%}


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | Critical |
| **대응 우선순위** | P0 - 즉시 대응 |

#### SIEM 탐지 쿼리 (참고용)

```splunk
index=security sourcetype=syslog ("exploit" OR "remote code execution" OR "shell")
| stats count by src_ip, dest_ip, action
| where count > 3
```

#### MITRE ATT&CK 매핑

- **T1203 (Exploitation for Client Execution)**


---

### 1.2 노출 관리 플랫폼만으로 해소되지 않는 보안 위험

{% include news-card.html
  title="노출 관리 플랫폼만으로 해소되지 않는 보안 위험"
  url="https://thehackernews.com/2026/11/is-your-exposure-management-platform.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiTqhUSejDKMWiBuqakycpFyce33qmRAlEPU4FbfKnzSRZmIlOQia8YXyU8bdvYFN6ldGMqz2vxPZn-s9524oTPZithSzMiO5ejngh_UMdp8jEbSG8znPLj-0husv1pxRF0dW2qES9dz4oR56dk67YJ8zePlgnVFSbHSIKHAU_7VqK0-pwSVeYEsOYM7u8/s1600/exposure.png"
  summary="The Hacker News는 심각도와 티켓만으로는 노출을 해소하기 어렵다고 설명합니다. 시스템 소유자와 공격자 접근 가능성 등 대응에 필요한 맥락을 함께 확인하는 것이 핵심입니다."
  source="The Hacker News"
  severity="High"
%}


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | High |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |


---

### 1.3 OpenAI, 30시간 실행으로 Linux 권한 상승 익스플로잇 948개 생성

{% include news-card.html
  title="OpenAI, 30시간 실행으로 Linux 권한 상승 익스플로잇 948개 생성"
  url="https://thehackernews.com/2026/11/openai-ai-pipeline-generates-948-linux.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEje4ZiJMrWCzkoOXuOcWQkB02TmQLM81NWPvzQ8yw9iComqPyLIP0_TAzy8AHMkNfzyXw2Fw-8kBhWIohuXc_dGl39AI4Kw_n4Tll0DImNrRfcPrk1eZNQCP9QtOich_dhNW-ly5DIuZSzmWspWsWXU9QiGwnS5W7qzVDiIBVc4oggC__f6tsL1AOIP8opc/s1600/linux-lpe.jpg"
  summary="The Hacker News 보도에 따르면 OpenAI는 사이버 보안용 AI 모델을 사용한 파이프라인을 공개했습니다. 기사 제목은 30시간 실행과 권한 상승 익스플로잇 948개를 언급하며, 요약은 API 비용 120만 달러를 제시합니다. 연구 결과를 자사 환경의 실제 침해 증거로 해석하지 말고 원문의 검증 조건을 확인해야 합니다."
  source="The Hacker News"
  severity="High"
%}


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | 미공개 또는 해당 없음 |
| **심각도** | High |
| **대응 우선순위** | P1 - 7일 이내 검토 권장 |

#### MITRE ATT&CK 매핑

- **T1068 (Exploitation for Privilege Escalation)**


---

## 2. AI/ML 뉴스

### 2.1 호그와트 레거시, GeForce NOW에서 NVIDIA DLSS 5 적용

{% include news-card.html
  title="호그와트 레거시, GeForce NOW에서 NVIDIA DLSS 5 적용"
  url="https://blogs.nvidia.com/blog/geforce-now-thursday-hogwarts-legacy-dlss-5/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/11/gfn-thursday-11-5-blog-1920x1080-no-copy-842x450.jpg"
  summary="NVIDIA는 GeForce NOW의 호그와트 레거시에 3D-Guided Neural Rendering을 포함한 DLSS 5가 적용된다고 발표했습니다. 이는 그래픽 기능 업데이트이며 그 자체로 보안 취약점 발표는 아닙니다."
  source="NVIDIA AI Blog"
  severity="High"
%}


---

### 2.2 OpenAI, 책임 있는 AI 인프라 개발 원칙 발표

{% include news-card.html
  title="OpenAI, 책임 있는 AI 인프라 개발 원칙 발표"
  url="https://openai.com/index/setting-new-standard-responsible-ai-infrastructure"
  summary="OpenAI는 지역 자원 보호와 일자리 창출, 책임 있는 AI 인프라 개발을 위한 National Community Compact와 Compute Campus Policy Blueprint를 소개했습니다. 구체적인 의무와 적용 범위는 원문 정책 문서를 확인해야 합니다."
  source="OpenAI Blog"
  severity="High"
%}


---

### 2.3 Riot, 280억 달러 텍사스 임대 계약의 임차인으로 Anthropic 명시

{% include news-card.html
  title="Riot, 280억 달러 텍사스 임대 계약의 임차인으로 Anthropic 명시"
  url="https://bitcoinmagazine.com/news/riot-names-anthropic-texas-lease"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/Riot-Anthropic-Texas-Lease.jpg"
  summary="Bitcoin Magazine은 Riot의 10-Q에 910MW 코르시카나 임대 계약 상대가 Anthropic으로 기재됐다고 보도했습니다. 기사에 따르면 최대 36억 달러의 건설 비용에 12% 이자가 발생할 수 있습니다. 계약 규모와 조건은 해당 공시와 대조해야 합니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 자율 에이전트를 위한 개방형 인프라

{% include news-card.html
  title="자율 에이전트를 위한 개방형 인프라"
  url="https://cloud.google.com/blog/products/containers-kubernetes/open-infrastructure-for-autonomous-agents-comes-to-cncf/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/1_s5MbWZe.max-1000x1000.png"
  summary="Google Cloud는 지속적으로 상태를 유지하고 하위 에이전트를 실행하는 작업이 기존 요청 중심 워크로드와 다른 인프라 요구를 만든다고 설명합니다. 에이전트 실행 상태와 자원 관리 경계를 점검할 때 참고할 자료입니다."
  source="Google Cloud Blog"
  severity="Medium"
%}


---

### 3.2 에이전트 시대의 기계 속도 개발·방어 전략

{% include news-card.html
  title="에이전트 시대의 기계 속도 개발·방어 전략"
  url="https://cloud.google.com/blog/products/identity-security/helping-you-build-and-defend-at-machine-speed-in-the-agentic-era/"
  summary="Google Cloud는 대규모 언어 모델의 개발과 실제 위협 동향을 연결하며 에이전트 시대의 개발·방어 접근을 소개합니다. 자사 환경에 적용할 통제는 제품 제공 범위와 운영 권한을 확인한 뒤 선정해야 합니다."
  source="Google Cloud Blog"
  severity="High"
%}


---

### 3.3 Google Public Sector Summit 주요 내용과 시사점

{% include news-card.html
  title="Google Public Sector Summit 주요 내용과 시사점"
  url="https://cloud.google.com/blog/topics/public-sector/highlights-and-reflections-from-google-public-sector-summit-where-mission-meets-moonshot/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/GPS2026_1020_090400-1207_ALIVE.max-1000x1000.jpg"
  summary="Google은 워싱턴 D.C.에서 이틀간 열린 Public Sector Summit에 정부 관계자·혁신가·산업 파트너 2,700명 이상이 참여했다고 소개했습니다. 공공 부문 AI 활용 사례와 발표 내용을 정리한 자료입니다."
  source="Google Cloud Blog"
  severity="Medium"
%}


---

## 4. DevOps & 개발 뉴스

### 4.1 Docker·ActiveState, 신뢰할 수 있는 콘텐츠 협력 확대

{% include news-card.html
  title="Docker·ActiveState, 신뢰할 수 있는 콘텐츠 협력 확대"
  url="https://www.docker.com/blog/docker-activestate-trusted-content/"
  summary="Docker는 ActiveState와의 협력을 통해 개발팀이 사용하는 신뢰할 수 있는 콘텐츠의 기준을 확장한다고 발표했습니다. 도입 시 지원 대상과 기존 이미지 검증 절차의 관계를 확인해야 합니다."
  source="Docker Blog"
  severity="High"
%}


---

### 4.2 CNCF Score, Docker 오픈소스 지원 프로그램으로 보안 개선

{% include news-card.html
  title="CNCF Score, Docker 오픈소스 지원 프로그램으로 보안 개선"
  url="https://www.docker.com/blog/cncf-score-project-improved-its-security-posture-by-joining-the-docker-sponsored-open-source-program/"
  summary="Docker는 CNCF Score 프로젝트가 Docker Scout, Hardened Images, Docker-Sponsored Open Source Program을 활용해 컨테이너 보안을 개선한 사례를 소개했습니다. 사례의 적용 조건을 자사 빌드 경로와 비교할 수 있습니다."
  source="Docker Blog"
  severity="High"
%}


---

### 4.3 CodeQL 2.27.4, 쿼리 정확도·메타데이터 개선

{% include news-card.html
  title="CodeQL 2.27.4, 쿼리 정확도·메타데이터 개선"
  url="https://github.blog/changelog/2026-11-04-codeql-2-27-4-improves-accuracy-and-query-metadata"
  image="https://github.blog/wp-content/uploads/2026/11/693764162-ed6ea6bf-2eea-41ac-82c2-27cd6ca10346.jpg"
  summary="GitHub는 CodeQL 2.27.4에서 여러 언어의 쿼리 정확도와 메타데이터를 개선했다고 발표했습니다. 분석 결과의 증감을 평가할 때 엔진·쿼리 버전 변경을 함께 기록해야 합니다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

## 5. 블록체인 뉴스

### 5.1 바이낸스 63억 달러 해킹 보도 후 Fed·OCC의 은행 점검

{% include news-card.html
  title="바이낸스 63억 달러 해킹 보도 후 Fed·OCC의 은행 점검"
  url="https://bitcoinmagazine.com/news/fed-occ-quiz-banks-binance-hack"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/Fed-OCC-Banks-Binance-Hack.jpg"
  summary="Bitcoin Magazine 보도에 따르면 Fed와 OCC 감독 당국은 바이낸스 해킹 이후 미국 은행의 취약성을 점검하기 위해 연락했습니다. 제목은 피해 규모를 63억 달러로 제시하며, 구체적인 영향 범위는 원문과 당국 발표를 대조해야 합니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 5.2 Tether·Tron, 바이낸스 해킹 두 달 전 T3 범죄 대응 조직 종료 보도

{% include news-card.html
  title="Tether·Tron, 바이낸스 해킹 두 달 전 T3 범죄 대응 조직 종료 보도"
  url="https://bitcoinmagazine.com/news/tether-tron-scrap-t3-crime-unit"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/BlackRock-Coinbase-Strategy-Among-Nine-Firms-Launching-the-Bitcoin-Security-Consortium-Pledging-15-Million-To-BTC-Security-Development.jpg"
  summary="Bitcoin Magazine은 T3 Financial Crime Unit이 8월 말 활동을 종료했다고 보도했습니다. 이 조직은 23개 관할 당국과 협력해 불법 USDT 4억 5,000만 달러 이상을 동결했다고 밝혔습니다. 활동 종료와 이후 사고 사이의 인과관계는 이 사실만으로 입증되지 않습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 5.3 American Bitcoin, 보유 자산 평가이익과 함께 분기 순이익 1억 2,600만 달러 기록

{% include news-card.html
  title="American Bitcoin, 보유 자산 평가이익과 함께 분기 순이익 1억 2,600만 달러 기록"
  url="https://bitcoinmagazine.com/news/american-bitcoin-126m-q3-profit"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/American-Bitcoin-ABTC-Q3-Mining-Rig.jpg"
  summary="Bitcoin Magazine은 American Bitcoin이 보유 Bitcoin에서 1억 9,730만 달러의 이익을 반영해 3분기 약 1억 2,600만 달러 순이익을 기록했다고 보도했습니다. 직전 분기 5,720만 달러 손실과 대비되며, 현금흐름과 평가손익은 구분해 읽어야 합니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [worklog-system 주간보고 자동화 구축 경험기](https://d2.naver.com/helloworld/5037598) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ worklog-system 주간보고 자동화 구축 경험기 NAVER D2 | worklog-system 주간보고 자동화 구축 경험기 naver.me 발표 내용 대 AI 시대에 본인의 업무 기록을 수집하고 TODO 및 회의록을 기록하는 등이 확인되었습니다. |
| [2026년과 이후 JavaScript의 동향 - 브라우저 밖의 JavaScript](https://d2.naver.com/helloworld/1443473) | 네이버 D2 | 브라우저 밖의 JavaScript 동향을 마지막으로 다루었던 2019년 시점( 1부 , 2부 )에서는 Node.js 12와 막 1년을 넘긴 Deno를 소개하며 "Node.js와 같은 성공을 거둘 수 있을지는 아직 미지수"라고 썼습니다 |
| [2026년과 이후 JavaScript의 동향 - JavaScript(ECMAScript)](https://d2.naver.com/helloworld/2675915) | 네이버 D2 | 2016년부터 매년 이어 오던 "JavaScript의 동향" 연재는 2020년을 마지막으로 한동안 쉬었습니다. 그사이 6년이 지났고, 그 6년 동안 ECMAScript 명세는 여섯 번 개정되었습니다 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 11건 | 기타 주제 |
| **AI/ML** | 2건 | The Hacker News 관련 동향, OpenAI Blog 관련 동향 |
| **클라우드 보안** | 1건 | The Hacker News 관련 동향 |
| **블록체인/암호화폐** | 1건 | The Hacker News 관련 동향 |
| **취약점/CVE** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **AI/ML**(2건)입니다. The Hacker News 관련 동향, OpenAI Blog 관련 동향 등이 주요 이슈입니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **ThreatsDay: Apache OFBiz 원격 코드 실행·DreamHost 침해 소식** 관련 긴급 패치 및 영향도 확인
- [ ] **5 Active Cyber Threats That Put US Enterprises at** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **노출 관리 플랫폼만으로 해소되지 않는 보안 위험** 관련 보안 검토 및 모니터링
- [ ] **OpenAI, 30시간 실행으로 Linux 권한 상승 익스플로잇 948개 생성** 관련 보안 검토 및 모니터링
- [ ] **호그와트 레거시, GeForce NOW에서 NVIDIA DLSS 5 적용** 관련 보안 검토 및 모니터링
- [ ] **OpenAI, 책임 있는 AI 인프라 개발 원칙 발표** 관련 보안 검토 및 모니터링
- [ ] **에이전트 시대의 기계 속도 개발·방어 전략** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **호그와트 레거시, GeForce NOW에서 NVIDIA DLSS 5 적용** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사

## 관련 포스트 및 참고 자료

- 2026년 10월 27일 주간 보안 다이제스트: {% post_url 2026-10-27-Tech_Security_Weekly_Digest_Agent_Update_Security_Malware %}
- 2026년 10월 26일 주간 보안 다이제스트: {% post_url 2026-10-26-Tech_Security_Weekly_Digest_AI_Malware_Agent %}
- 2026년 10월 25일 주간 보안 다이제스트: {% post_url 2026-10-25-Tech_Security_Weekly_Digest_AI_Bitcoin %}

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [2026년 10월 07일 주간 보안 다이제스트: 클라우드·AI 에이전트·클라우드 보안 (30건)](/posts/2026/10/07/Tech_Security_Weekly_Digest_GPT_AI_Security_AWS/) — 2026-10-07
- [2026년 10월 27일 주간 보안 다이제스트: 제로데이·패치·랜섬웨어 (25건)](/posts/2026/10/27/Tech_Security_Weekly_Digest_Agent_Update_Security_Malware/) — 2026-10-27
- [2026년 10월 26일 주간 보안 다이제스트: 클라우드·악성코드·BYOVD EDR (21건)](/posts/2026/10/26/Tech_Security_Weekly_Digest_AI_Malware_Agent/) — 2026-10-26

---

**작성자**: Twodragon
