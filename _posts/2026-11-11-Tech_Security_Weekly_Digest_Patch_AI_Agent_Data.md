---
layout: post
title: "2026년 11월 11일 주간 보안 다이제스트: 제로데이·패치·악성코드 (30건)"
date: 2026-11-11 12:51:11 +0900
last_modified_at: 2026-11-11T12:51:11+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Patch, AI, Agent, Data]
excerpt: "2026년 11월 11일 공개된 30건의 위협·취약점 가운데 Git, 재귀 복제 중 악성 저장소가 코드를 실행할 수 있는 취약점 · SGLang RCE 익스플로잇이 NEAR AI를 침해해 18개가 즉각 대응 우선순위에 올랐습니다. 사안별 소스와 영향도를 표로 정리해 우선순위 판단 근거를 남겼습니다."
description: "2026년 11월 11일 보안 뉴스 요약. The Hacker News, AWS Security Blog 등 30건을 분석하고 Git, 재귀 복제 중 악성, SGLang RCE 익스플로잇이 NEAR 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Patch, AI, Agent]
author: Twodragon
comments: true
image: /assets/images/2026-11-11-Tech_Security_Weekly_Digest_Patch_AI_Agent_Data.svg
image_alt: "Git, SGLang RCE NEAR, Xen Orchestra - security digest overview"
toc: true
summary_card:
  title: "2026년 11월 11일 주간 보안 다이제스트: 제로데이·패치·악성코드 (30건)"
  period: "2026년 11월 11일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Patch"
    - "AI"
    - "Agent"
    - "Data"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "Git, 재귀 복제 중 악성 저장소가 코드를 실행할 수 있는 취약점 패치" }
    - { source: "The Hacker News", title: "SGLang RCE 익스플로잇이 NEAR AI를 침해해 18개 에이전트와 약 100명의 사용자 데이터 탈취" }
    - { source: "The Hacker News", title: "해커들이 Xen Orchestra의 치명적 인증 우회 취약점을 악용해 관리자 접근 권한 획득" }
    - { source: "Google Cloud Blog", title: "Gemini 팩토리 내부: 파트너 솔루션 가속화" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 11월 11일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
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
| 🔒 **Security** | The Hacker News | Git, 재귀 복제 중 악성 저장소가 코드를 실행할 수 있는 취약점 패치 | 🟠 High |
| 🔒 **Security** | The Hacker News | SGLang RCE 익스플로잇이 NEAR AI를 침해해 18개 에이전트와 약 100명의 사용자 데이터 탈취 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | 해커들이 Xen Orchestra의 치명적 인증 우회 취약점을 악용해 관리자 접근 권한 획득 | 🔴 Critical |
| 🤖 **AI/ML** | OpenAI Blog | Gilbert + Tobin, AI로 법률 비즈니스를 재구상하다 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | AI가 재활용업체의 혼합 폐기물 재사용 소재 전환을 돕는 방법 | 🟡 Medium |
| 🤖 **AI/ML** | Google AI Blog | Gemini Intelligence: 더 많은 기기에서 만나는 새로운 기능 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Gemini 팩토리 내부: 파트너 솔루션 가속화 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 지적만 하지 말고 수정하세요: pull request에서 CodeMender를 실행하는 방법 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | BigQuery measures 정식 출시: AI 정확성을 위한 BI 지표와 지식 그래프 통합 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Enterprise Copilot 시트 관리를 위한 GitHub App 지원 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: SGLang RCE 익스플로잇이 NEAR AI를 침해해 18개 에이전트와 약 100명의 사용자 데이터 탈취, 해커들이 Xen Orchestra의 치명적 인증 우회 취약점을 악용해 관리자 접근 권한 획득 등 Critical 등급 위협 2건이 확인되었습니다.
- **주요 모니터링 대상**: Git, 재귀 복제 중 악성 저장소가 코드를 실행할 수 있는 취약점 패치, LNbits, 11월 8일 공격으로 자금 유출된 후 긴급 보안 업데이트 1.7.0 출시 등 High 등급 위협 2건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 Git, 재귀 복제 중 악성 저장소가 코드를 실행할 수 있는 취약점 패치

{% include news-card.html
  title="Git, 재귀 복제 중 악성 저장소가 코드를 실행할 수 있는 취약점 패치"
  url="https://thehackernews.com/2026/11/git-patches-flaw-that-lets-malicious.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEipoPlLYj_xfJ8bsfRTONwa3estE9I2un_9OBx2fVuxEp-zoiADgipn-gGOeU4TqqyjqjrCpoGXC4jmuF7o1e_PUMbr-QoHDdPZEDWavb4VbjtWbOxMfmz-E9fIPT2DHEXYCN53l2jtiJGVfEFjHsR8gaHeyF59Yii0oTnP73vaslLWPzuideEGxTy6S9U/s1600/gits.jpg"
  summary="Git에서 악성 저장소가 재귀적 클론 및 서브모듈과 함께 복제하는 컴퓨터에서 공격자 코드를 실행할 수 있는 취약점이 발견되어 Git 2.56.1 및 2.50~2.55 시리즈용 패치(2.50.2, 2.51.3, 2.52.1, 2.53.1, 2.54.1, 2.55.1)로 수정되었습니다."
  source="The Hacker News"
  severity="High"
%}

#### Git 재귀 클론 취약점 분석 (CVE-2026-111760)

#### 기술적 배경 및 위협 분석

Git의 인덱스 처리 과정에서 발생하는 정수 잘림(integer truncation) 결함으로, 악성 저장소를 재귀적으로 클론(`--recurse-submodules`)할 때 서브모듈을 통해 공격자 코드가 실행될 수 있다. 재귀 클론은 CI/CD 파이프라인에서 서브모듈 의존성을 자동으로 가져오는 표준 관행이므로, 신뢰할 수 없는 저장소나 손상된 서브모듈 참조가 곧 원격 코드 실행(RCE)으로 이어지는 경로가 된다. Git 2.56.1 및 2.50~2.55 계열 패치(2.50.2~2.55.1)에서 수정되었다.

#### 실무 영향 분석

DevSecOps 파이프라인에서 빌드 에이전트는 종종 높은 권한과 시크릿 접근 권한을 가진 채 재귀 클론을 수행한다. 따라서 악성 서브모듈이 실행되면 CI 러너 장악 → 시크릿 탈취 → 공급망 전파로 확대될 수 있다. 특히 외부 기여 PR, 포크 저장소, 서드파티 서브모듈을 참조하는 프로젝트는 즉시 영향권이다. 빌드 이미지에 구버전 Git이 포함된 경우 패치 적용이 지연될 수 있어 컨테이너 베이스 이미지 재빌드도 필요하다.



#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - T1190  # Exploit Public-Facing Application
```

---

### 1.2 SGLang RCE 익스플로잇이 NEAR AI를 침해해 18개 에이전트와 약 100명의 사용자 데이터 탈취

{% include news-card.html
  title="SGLang RCE 익스플로잇이 NEAR AI를 침해해 18개 에이전트와 약 100명의 사용자 데이터 탈취"
  url="https://thehackernews.com/2026/11/sglang-rce-exploit-breaches-near-ai.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEifQOwa1ngLZRATbbZyg_iud4SNx-9ugjo2iOG6crnJzatc_uS9FjGScBnNUy-uNIuOEE3Y6kJTpUVMVtOR1bW5sse_pRNJA1SQALCGjshDx6-CF1t8HXlUI2CCb6yp7Uepz6uk3ctMLUlSx4Q36Q7pZcx1nb9wPgbYAZqvd6CnSJ6WM6Kn_ZENtHpESoM/s1600/nearai.jpg"
  summary="SGLang의 원격 코드 실행 취약점을 악용한 공격자가 지난 일요일 NEAR AI의 추론 서버 중 하나에서 코드를 실행했으며, 그날 해당 서버에서 처리된 기밀 모드 요청을 포함한 요청들을 열람했을 가능성이 있다고 회사 측이 밝혔다. 기밀 모드는 TEE(신뢰 실행 환경) 내에서 요청을 처리하는 방식이다."
  source="The Hacker News"
  severity="Critical"
%}

#### SGLang RCE 사고 DevSecOps 분석

#### 기술적 배경 및 위협 분석
SGLang은 LLM 추론 엔진으로, 대규모 모델 서빙 시 높은 처리량을 위해 신뢰 경계 밖 입력(프롬프트, 토크나이저 설정, 요청 파라미터)을 다수 처리한다. RCE 취약점은 이런 입력 검증 미흡에서 비롯되며, 공격자는 추론 서버에서 임의 코드를 실행해 동일 서버에서 처리 중인 요청 스트림을 열람할 수 있었다. 핵심 위협은 **TEE(신뢰 실행 환경) 격리 우회 가능성**이다. TEE는 호스트/하이퍼바이저로부터 게스트 메모리를 보호하지만, 애플리케이션 계층 RCE가 발생하면 TEE 내부 프로세스 권한으로 비밀 모드 요청까지 노출된다. 즉 "기밀 컴퓨팅=안전"이라는 가정이 애플리케이션 취약점 앞에서 붕괴된 사례다.

#### 실무 영향 분석
- **공급망 리스크**: 오픈소스 추론 엔진을 프로덕션에 도입한 팀은 버전 고정·패치 SLA 재점검이 필요하다.
- **멀티테넌시 노출**: 단일 추론 서버가 여러 에이전트/사용자 요청을 혼재 처리하면 측면 이동 및 데이터 유출 범위가 확대된다.
- **TEE 신뢰 모델 재설계**: TEE 도입만으로 컴플라이언스를 충족했다고 판단한 조직은 애플리케이션 취약점 관리(CVE 대응, SBOM, 런타임 보호)를 병행해야 한다.
- **관측성 공백**: 추론 서버 내부 요청 로그·이상 행위 탐지가 없으면 침해 사실을 사후에도 인지하기 어렵다.



---

### 1.3 해커들이 Xen Orchestra의 치명적 인증 우회 취약점을 악용해 관리자 접근 권한 획득

{% include news-card.html
  title="해커들이 Xen Orchestra의 치명적 인증 우회 취약점을 악용해 관리자 접근 권한 획득"
  url="https://thehackernews.com/2026/11/hackers-exploit-critical-xen-orchestra.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgMH_u7t-U3KIejAItsfC_js20xJgxT2ITYLsR0DAxzfcwDvPrzBHkpZlDuALWPnACOoknX2IALwHIUxIzfhbA24M7e8cGWTZpBMWqpX-wn6xqe8_U3fAtnR-9RsRdFHMCjvNnBsMXrEUKhVYS5bbTGL3B50UMO0aydtHIomY89s2iDAQMq0jXJJ3vh4Nvi/s1600/XEN-attack.jpg"
  summary="Vates VMS는 Xen Orchestra에서 인증 우회 취약점(VSA-2026-062)이 실제로 악용되고 있다고 경고했습니다. 이 취약점은 REST cookie 파싱 시 authenticationToken=j:%7B%7D가 {}로 변환되어 인증이 우회되는 방식이며, 아직 CVE 식별자가 부여되지 않았습니다."
  source="The Hacker News"
  severity="Critical"
%}

#### 기술적 배경 및 위협 분석

Xen Orchestra(XO)는 XenServer/XCP-ng 기반 가상화 인프라를 웹에서 관리하는 오픈소스 콘솔로, Vates VMS가 유지보수한다. 이번 VSA-2026-062는 REST API의 쿠키 파싱 로직 결함에서 비롯된다. `authenticationToken=j:%7B%7D`(URL 인코딩된 `{}`)를 REST 인증 계층이 빈 객체 `{}`로 역직렬화한 뒤, 인증 검증 로직이 이를 유효한 토큰 컨텍스트로 오인하면서 인증을 우회한다. 즉, 조작된 쿠키 한 줄로 관리자 권한 획득이 가능한 전형적인 "파서 불일치(parser differential)" 유형이다. CVE 미부여 상태에서 실제 익스플로잇이 확인된 점이 가장 큰 위협이며, XO는 하이퍼바이저 제어 평면이므로 침해 시 전체 VM 라이프사이클(생성·삭제·스냅샷·마이그레이션)과 백업 스토리지 접근까지 노출된다. 관리 콘솔이 인터넷에 노출된 환경이라면 사실상 즉시 위험군이다.

#### 실무 영향 분석

DevSecOps 관점에서 이 취약점은 세 가지 지점을 건드린다. 첫째, **CI/CD 파이프라인 신뢰 경계**: XO API를 Terraform/Ansible 프로바이더로 자동화하는 조직은 자격증명·토큰이 파이프라인 시크릿에 저장되어 있어, 우회 취약점이 뚫리면 IaC 실행 권한 전체가 탈취될 수 있다. 둘째, **SBOM/취약점 게이팅**: CVE 미할당 상태이므로 Trivy/Grype 등 스캐너가 탐지하지 못한다. 버전 기반 수동 룰을 추가하지 않으면 게이트가 무력화된다. 셋째, **런타임 탐지 공백**: 정상 REST 인증과 형식이 동일해 WAF 시그니처로 걸러지기 어렵고, 쿠키 값의 인코딩 패턴(`%7B%7D`, `j:` 접두)에 대한 커스텀 룰이 필요하다. 또한 XO 관리 콘솔이 사내망에만 있다는 가정은 VPN·제로트러스트 프록시 경유 시에도 동일 취약점이 성립하므로 안전하지 않다.



---

## 2. AI/ML 뉴스

### 2.1 Gilbert + Tobin, AI로 법률 비즈니스를 재구상하다

{% include news-card.html
  title="Gilbert + Tobin, AI로 법률 비즈니스를 재구상하다"
  url="https://openai.com/index/gilbert-tobin-sam-nickless"
  summary="Gilbert + Tobin의 파트너 겸 CEO인 Sam Nickless와의 대화에서 AI를 활용한 법률 비즈니스 재구상을 논의했습니다. 이 대화는 법률 사무소가 AI를 통해 업무 방식을 어떻게 혁신할 수 있는지에 초점을 맞췄습니다."
  source="OpenAI Blog"
  severity="Medium"
%}


---

### 2.2 AI가 재활용업체의 혼합 폐기물 재사용 소재 전환을 돕는 방법

{% include news-card.html
  title="AI가 재활용업체의 혼합 폐기물 재사용 소재 전환을 돕는 방법"
  url="https://blogs.nvidia.com/blog/ai-recycling-startups/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/11/recycling-company-grid-1920x1080-1-842x450.png"
  summary="Vision AI와 로보틱스가 혼합 재활용품 컨베이어 벨트에서 회수 가치가 있는 품목을 선별해 수천 톤의 폐기물을 매립지에서 전환한다. 이를 통해 재활용업체는 혼합 폐기물을 재사용 가능한 소재로 바꿀 수 있다."
  source="NVIDIA AI Blog"
  severity="Medium"
%}


---

### 2.3 Gemini Intelligence: 더 많은 기기에서 만나는 새로운 기능

{% include news-card.html
  title="Gemini Intelligence: 더 많은 기기에서 만나는 새로운 기능"
  url="https://blog.google/products-and-platforms/platforms/android/gemini-intelligence-november-features-devices/"
  image="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Gemini_Intelligence_Signature27.max-600x600.format-webp.webp"
  summary="Google이 Gemini Intelligence의 새로운 기능을 더 많은 기기에서 제공한다. 사용자는 스마트폰을 통해 Gemini Intelligence를 음성으로 활용할 수 있다."
  source="Google AI Blog"
  severity="Medium"
%}


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Gemini 팩토리 내부: 파트너 솔루션 가속화

{% include news-card.html
  title="Gemini 팩토리 내부: 파트너 솔루션 가속화"
  url="https://cloud.google.com/blog/topics/partners/inside-the-gemini-factory-accelerating-partner-solutions/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/1_-_Accelerated_Partner_Development_Pipeli.max-1000x1000.png"
  summary="새로운 통합 Gemini 경험을 통해 기업은 표준화된 커넥터(MCP, A2A 런타임, REST API)를 통해 타사 파트너 기능을 Gemini에 직접 통합할 수 있습니다. 여기에는 새로운 선언적 스킬과 플러그인도 포함됩니다."
  source="Google Cloud Blog"
  severity="Medium"
%}


---

### 3.2 지적만 하지 말고 수정하세요: pull request에서 CodeMender를 실행하는 방법

{% include news-card.html
  title="지적만 하지 말고 수정하세요: pull request에서 CodeMender를 실행하는 방법"
  url="https://cloud.google.com/blog/products/identity-security/how-to-run-codemender-in-your-pull-requests/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/figure-1a.max-1000x1000.png"
  summary="Google은 개발자들이 agentic 도구로 더 빠르게 코드를 생성하면서 소프트웨어 결함을 찾고 수정하는 데 시간이 더 걸리는 문제를 해결하기 위해 CodeMender를 pull request에서 실행하는 방법을 제시했다. 이는 코드 복잡성 증가에 대응하기 위한 Google의 핵심 관심사다."
  source="Google Cloud Blog"
  severity="Medium"
%}


---

### 3.3 BigQuery measures 정식 출시: AI 정확성을 위한 BI 지표와 지식 그래프 통합

{% include news-card.html
  title="BigQuery measures 정식 출시: AI 정확성을 위한 BI 지표와 지식 그래프 통합"
  url="https://cloud.google.com/blog/products/data-analytics/bigquery-measures-ga-unifying-bi-metrics-and-knowledge-graphs/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/Figure_1_Unified_Model_BI_and_Graphs.max-1000x1000.png"
  summary="BigQuery measures가 GA되어 BI 지표와 knowledge graph를 통합함으로써 AI 에이전트가 비즈니스 질문에 답할 때 '무엇이 일어났는지'와 '왜 일어났는지'를 함께 이해할 수 있게 되었다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

BigQuery measures가 GA되어 BI 지표와 knowledge graph를 통합함으로써 AI 에이전트가 비즈니스 질문에 답할 때 '무엇이 일어났는지'와 '왜 일어났는지'를 함께 이해할 수 있게 되었다. 기존에는 지표 정의가 BI 플랫폼에, 관계 정보가 knowledge graph에 분리되어 있어 AI가 절반의 정보만으로 추측하다 오답을 낼 수 있었다.


---

## 4. DevOps & 개발 뉴스

### 4.1 Enterprise Copilot 시트 관리를 위한 GitHub App 지원

{% include news-card.html
  title="Enterprise Copilot 시트 관리를 위한 GitHub App 지원"
  url="https://github.blog/changelog/2026-11-10-github-app-support-for-enterprise-copilot-seat-management"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-improvements.jpg"
  summary="Enterprise GitHub Apps가 enterprise-level Copilot seat management API를 호출해 사용자와 enterprise team의 Copilot seat 할당을 제어할 수 있게 되었다. 해당 API는 GitHub App을 통해 접근 가능하다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

### 4.2 GitHub Copilot의 Gemini 4 Carbon

{% include news-card.html
  title="GitHub Copilot의 Gemini 4 Carbon"
  url="https://github.blog/changelog/2026-11-10-gemini-4-carbon-in-github-copilot"
  image="https://github.blog/wp-content/uploads/2026/11/700374691-69ca0c74-ac8e-4638-82f6-46417790e655.png"
  summary="Google의 최신 모델인 Gemini 4 Carbon이 GitHub Copilot에서 정식 출시되었습니다. 이 모델은 복잡한 코딩, 에이전트, 추론 작업을 위해 설계되었으며 안전한 코드 생성에 중점을 둡니다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

### 4.3 C++ 언어 서버, 이제 MSBuild 빌드 자동 구성 지원

{% include news-card.html
  title="C++ 언어 서버, 이제 MSBuild 빌드 자동 구성 지원"
  url="https://github.blog/changelog/2026-11-10-c-language-server-now-auto-configures-msbuild-builds"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-improvements.jpg"
  summary="Microsoft C++ Language Server for GitHub Copilot CLI가 이제 MSBuild compile commands extractor를 자체 번들로 포함하고 자동으로 실행한다. 이를 통해 agent가 별도로 이를 탐색하고 실행할 필요 없이 MSBuild 빌드를 자동 구성할 수 있다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

## 5. 블록체인 뉴스

### 5.1 Bitcoin으로 데워진 온수 욕조와 278개 워싱턴 Bitcoin 판매점: 이제 Bitcoin 받습니다

{% include news-card.html
  title="Bitcoin으로 데워진 온수 욕조와 278개 워싱턴 Bitcoin 판매점: 이제 Bitcoin 받습니다"
  url="https://bitcoinmagazine.com/news/washington-bitcoin-merchants-snorkel"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/Kake-Junkijarvi-Finland-6-diameter-3-tall.jpg"
  summary="Washington의 Bitcoin 가맹점이 Seattle 커피숍부터 bitcoin 채굴기로 데워지는 Snorkel 온수 욕조까지 278곳으로 늘어나 Bitcoin 결제를 받기 시작했다. 이 소식은 Bitcoin Magazine에 Vagabond가 작성한 글로 전해졌다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 5.2 LNbits, 11월 8일 공격으로 자금 유출된 후 긴급 보안 업데이트 1.7.0 출시

{% include news-card.html
  title="LNbits, 11월 8일 공격으로 자금 유출된 후 긴급 보안 업데이트 1.7.0 출시"
  url="https://bitcoinmagazine.com/news/lnbits-releases-1-7-0-urgent-security-update-after-november-8-attacks-drain-funds"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/tn-5.webp"
  summary="LNbits는 11월 8일부터 시작된 공격으로 자금이 탈취되자 11월 10일 긴급 보안 업데이트인 버전 1.7.0을 출시했습니다. 운영자는 서버를 재시작하기 전에 반드시 업그레이드해야 하며, 이전 버전은 자금 도난 위험에 노출되어 있습니다."
  source="Bitcoin Magazine"
  severity="High"
%}


---

### 5.3 Texas 하원의원, 도시들이 Bitcoin에 1천만 달러 투자할 수 있는 법안 발의

{% include news-card.html
  title="Texas 하원의원, 도시들이 Bitcoin에 1천만 달러 투자할 수 있는 법안 발의"
  url="https://bitcoinmagazine.com/news/texas-bill-invest-10-million-bitcoin"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/Texas-Rep.-Files-Bill-Letting-Cities-Invest-10-Million-in-Bitcoin.jpg"
  summary="Texas 주 하원의원 Ron Reynolds가 2027년 9월 1일부터 각 텍사스 도시나 카운티가 최대 1,000만 달러의 공적 자금을 bitcoin에 투자할 수 있도록 하는 House Bill 815를 발의했습니다. 해당 소식은 Bitcoin Magazine에 Micah Zimmerman이 작성한 기사로 처음 보도되었습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Socket.IO 서버를 여러 Pod에서 운영하기](https://d2.naver.com/helloworld/3517874) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ Socket.IO 서버를 여러 Pod에서 운영하기 NAVER D2 | Socket.IO 서버를 여러 Pod에서 운영하기 naver.me ​ 발표 내용 Socket.IO와 n3r 기반의 소켓 서버를 자체 구축하면서, 여러 Pod 사이의 등이 확인되었습니다. |
| [Airbnb의 임베디드 워크플로 엔진 Skipper, 오픈소스로 공개](https://medium.com/airbnb-engineering/skipper-airbnbs-embedded-workflow-engine-is-now-open-source-78dd354f472b?source=rss----53c7c27702d5---4) | Airbnb Engineering | Airbnb가 자사 전반의 팀에서 프로덕션으로 사용 중인 임베디드 workflow engine인 Skipper를 오픈소스로 공개했습니다. Skipper는 다단계 비즈니스 프로세스를 Java 또는 Kotlin 클래스로 표현하고 진행 상황을 영속화하며 크래시와 일시적 장애에서 복구할 수 있게 해줍니다. |
| [AI 스킬 만들기 10계명: Figma→Code 자동화 실전기](https://d2.naver.com/helloworld/8562180) | 네이버 D2 | 이 글에서 예로 든 스킬은 naver/design-to-ui 라는 이름의 오픈 소스로 공개되어 있습니다. 들어가며: 같은 모델, 다른 결과 AI 코딩 도구를 쓰다 보면 프롬프트에서 같은 설명을 매번 반복하게 됩니다 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 9건 | 기타 주제 |
| **AI/ML** | 5건 | The Hacker News 관련 동향, OpenAI Blog 관련 동향, NVIDIA AI Blog 관련 동향 |
| **취약점/CVE** | 1건 | The Hacker News 관련 동향 |
| **악성코드/피싱** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **AI/ML**(5건)입니다. The Hacker News 관련 동향, OpenAI Blog 관련 동향 등이 주요 이슈입니다. 

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **SGLang RCE 익스플로잇이 NEAR AI를 침해해 18개 에이전트와 약 100명의 사용자 데이터 탈취** 관련 긴급 패치 및 영향도 확인
- [ ] **해커들이 Xen Orchestra의 치명적 인증 우회 취약점을 악용해 관리자 접근 권한 획득** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **Git, 재귀 복제 중 악성 저장소가 코드를 실행할 수 있는 취약점 패치** (CVE-2026-111760) 관련 보안 검토 및 모니터링
- [ ] **Sparrow 악성코드 생태계로 연결된 세 가지 중국 연계 스파이 활동** 관련 보안 검토 및 모니터링
- [ ] **Amazon GuardDuty의 위협 탐지 기능을 사용자 지정하여 경고 피로 줄이기** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Gilbert + Tobin, AI로 법률 비즈니스를 재구상하다** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사

## 관련 포스트 및 참고 자료

- 2026년 11월 10일 주간 보안 다이제스트: {% post_url 2026-11-10-Tech_Security_Weekly_Digest_AWS_Data_Rust_Malware %}
- 2026년 11월 09일 주간 보안 다이제스트: {% post_url 2026-11-09-Tech_Security_Weekly_Digest_Cloud_Data_Security_Agent %}
- 2026년 11월 08일 주간 보안 다이제스트: {% post_url 2026-11-08-Tech_Security_Weekly_Digest_AI_Rust_Vulnerability_Patch %}

| 리소스 | 링크 | 용도 |
|--------|------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 실제 악용 확인된 취약점 목록 — 패치 우선순위 기준 |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) | 공격 전술·기법 매핑 — 탐지 룰 설계 |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) | 취약점 악용 확률 점수 — CVSS 보완 |
| The Hacker News | [thehackernews.com](https://thehackernews.com) | 본문 3건 인용 |
| OpenAI Blog | [openai.com](https://openai.com) | 본문 1건 인용 |
| NVIDIA AI Blog | [blogs.nvidia.com](https://blogs.nvidia.com) | 본문 1건 인용 |
| Google AI Blog | [blog.google](https://blog.google) | 본문 1건 인용 |
| Google Cloud Blog | [cloud.google.com](https://cloud.google.com) | 본문 3건 인용 |
| GitHub Changelog | [github.blog](https://github.blog) | 본문 3건 인용 |
| Bitcoin Magazine | [bitcoinmagazine.com](https://bitcoinmagazine.com) | 본문 3건 인용 |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [2026년 11월 10일 주간 보안 다이제스트: 클라우드·악성코드·AI 에이전트 (29건)](/posts/2026/11/10/Tech_Security_Weekly_Digest_AWS_Data_Rust_Malware/) — 2026-11-10
- [2026년 11월 08일 주간 보안 다이제스트: 제로데이·패치·Kubernetes (15건)](/posts/2026/11/08/Tech_Security_Weekly_Digest_AI_Rust_Vulnerability_Patch/) — 2026-11-08
- [2026년 11월 09일 주간 보안 다이제스트: 클라우드·BYOVD EDR·블록체인 (15건)](/posts/2026/11/09/Tech_Security_Weekly_Digest_Cloud_Data_Security_Agent/) — 2026-11-09

---

**작성자**: Twodragon
