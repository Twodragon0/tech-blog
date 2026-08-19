---
layout: post
title: "2026년 08월 19일 주간 보안 다이제스트: DNS 유출·클라우드·랜섬웨어 (30건)"
date: 2026-08-19 09:43:25 +0900
last_modified_at: 2026-08-19T09:43:25+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AWS, Data, ML, Cloud]
excerpt: "Microsoft Copilot Personal의 결함으로 한 번의 · 공격자들이 MLflow SSRF 취약점을 악용해 클라우드 자격이 부각된 2026년 08월 19일 보안 다이제스트 — 30건의 이슈와 실행 가능한 대응 액션을 정리합니다. 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다."
description: "2026년 08월 19일 보안 뉴스 요약. The Hacker News, AWS Security Blog 등 30건을 분석하고 Microsoft Copilot, 공격자들이 MLflow SSRF 취약점을 악용해, Ransom Busters 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AWS, Data, ML]
author: Twodragon
comments: true
image: /assets/images/2026-08-19-Tech_Security_Weekly_Digest_AWS_Data_ML_Cloud.svg
image_alt: "Microsoft Copilot, MLflow SSRF, Ransom Busters - security digest overview"
toc: true
summary_card:
  title: "2026년 08월 19일 주간 보안 다이제스트: DNS 유출·클라우드·랜섬웨어 (30건)"
  period: "2026년 08월 19일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AWS"
    - "Data"
    - "ML"
    - "Cloud"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "Microsoft Copilot Personal의 결함으로 한 번의 클릭으로 연결된 앱에서 데이터 유출 가능" }
    - { source: "The Hacker News", title: "공격자들이 MLflow SSRF 취약점을 악용해 클라우드 자격 증명과 비밀 정보를 탈취하다" }
    - { source: "The Hacker News", title: "Ransom Busters, 랜섬웨어 서버를 해킹했다고 주장하며 피해자들에게 최대 6만 달러 요구" }
    - { source: "Google Cloud Blog", title: "자동 조종 모드의 거버넌스, 난기류 없이" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 08월 19일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

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
| 🔒 **Security** | The Hacker News | Microsoft Copilot Personal의 결함으로 한 번의 클릭으로 연결된 앱에서 데이터 유출 가능 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 공격자들이 MLflow SSRF 취약점을 악용해 클라우드 자격 증명과 비밀 정보를 탈취하다 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | Ransom Busters, 랜섬웨어 서버를 해킹했다고 주장하며 피해자들에게 최대 6만 달러 요구 | 🔴 Critical |
| 🤖 **AI/ML** | OpenAI Blog | 국가 안보 분야의 민주적 감독 강화 | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | CodeAI와 협력하여 첫 AI 세대를 준비하다 | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | 사이버 중요 역량 시대의 모델 개발 속도 조절 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 자동 조종 모드의 거버넌스, 난기류 없이 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Google Dataflow에서 비용 효율적이고 고처리량의 생성형 AI 워크플로 구축하기 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Box, Gemini Embeddings 2로 멀티모달 엔터프라이즈 에이전트를 구현하다 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | JetBrains용 GitHub Copilot의 엔터프라이즈 관리 설정 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: 공격자들이 MLflow SSRF 취약점을 악용해 클라우드 자격 증명과 비밀 정보를 탈취하다, Ransom Busters, 랜섬웨어 서버를 해킹했다고 주장하며 피해자들에게 최대 6만 달러 요구 등 Critical 등급 위협 2건이 확인되었습니다.
- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 Microsoft Copilot Personal의 결함으로 한 번의 클릭으로 연결된 앱에서 데이터 유출 가능

{% include news-card.html
  title="Microsoft Copilot Personal의 결함으로 한 번의 클릭으로 연결된 앱에서 데이터 유출 가능"
  url="https://thehackernews.com/2026/08/microsoft-copilot-personal-flaws-could.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjAc2Z6RvtNlJnjkfp-kCEhx8x8Q9XPLHY-oQb8NXu6cb-C5BTfa9HnmWq3G1GT3mPsHLV6Xf6tyBui-ljplsYEo9Qt8kBiNKXOwvTzACMisyS0NQ5U3bGg8O6yVEPStEPbYw4W-4ZasDNssDr2JTJD7GTo6QEpER1L-9Xci-mNSk3A5t_aLXGIHwo04FI/s1600/copilot.jpg"
  summary="Varonis Threat Labs가 Microsoft Copilot Personal에서 세 가지 취약점(CoSnitch)을 공개했으며, 이는 조작된 링크를 한 번 클릭하면 연결된 앱과 Copilot 세션의 데이터가 조용히 유출될 수 있습니다. 이 결함은 Copilot이 노출한 문서화되지 않은 URL 파라미터에 부분적으로 기인합니다."
  source="The Hacker News"
  severity="Medium"
%}

#### 요약

Varonis Threat Labs가 Microsoft Copilot Personal에서 세 가지 취약점(CoSnitch)을 공개했으며, 이는 조작된 링크를 한 번 클릭하면 연결된 앱과 Copilot 세션의 데이터가 조용히 유출될 수 있습니다. 이 결함은 Copilot이 노출한 문서화되지 않은 URL 파라미터에 부분적으로 기인합니다.


#### 권장 조치

- 관련 시스템 목록 확인 및 자사 환경 해당 여부 평가
- 벤더 보안 권고 확인 후 패치 또는 완화 조치 적용
- SIEM/EDR 탐지 룰에 관련 IoC 추가
- 보안팀 내 공유 및 모니터링 강화


---

### 1.2 공격자들이 MLflow SSRF 취약점을 악용해 클라우드 자격 증명과 비밀 정보를 탈취하다

{% include news-card.html
  title="공격자들이 MLflow SSRF 취약점을 악용해 클라우드 자격 증명과 비밀 정보를 탈취하다"
  url="https://thehackernews.com/2026/08/attackers-exploit-mlflow-ssrf-flaw-to.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiOzcJe940Ayk9JrnE-tmotZ-mEHZiA5Jc0A8Sw9IZIfYEnH61X8whAW6jJZTnzLIQYA37foce9X_fshoAVwjLyBKrjvHbkuhhtwZ2Mewxtf1Syn9FBOvZBqwcMWXOCKFNnASyrCOQ9XTF6f174Aa4O55O7tbU6evYcrrV0H_psoYYq3uQQ_GvZqsu0e0ik/s1600/mlflow.jpg"
  summary="공격자들이 오픈소스 AI 플랫폼 MLflow의 SSRF 취약점을 악용해 클라우드 자격 증명과 비밀 정보를 탈취하고 있으며, OT/산업 자동화용 SCADA/HMI 소프트웨어 FUXA의 취약점도 악성 스캐닝과 공격 대상이 되고 있습니다. watchTowr와 VulnCheck의 독립적 보고서에 따르면, 이 두 취약점은 각각 심각도가 높은 것으로 확인되었습니다."
  source="The Hacker News"
  severity="Critical"
%}

#### 기술적 배경 및 위협 분석

MLflow는 ML 수명주기 관리 플랫폼으로, 모델 레지스트리, 실험 추적, 배포 기능을 제공합니다. 이번에 악용된 SSRF(Server-Side Request Forgery) 취약점은 공격자가 MLflow 서버의 요청 기능을 악용해 내부 네트워크 리소스에 접근하거나, 클라우드 메타데이터 서비스(예: AWS IAM Credentials, GCP Metadata API)를 통해 임시 자격 증명을 탈취할 수 있는 취약점입니다. 특히 MLflow는 기본적으로 인증 없이 실행되는 경우가 많아, Kubernetes 클러스터나 클라우드 환경에 배포된 경우 공격 표면이 넓어집니다.

FUXA는 SCADA/HMI 웹 기반 시스템으로, OT 환경에서 산업 제어를 담당합니다. 이번 취약점은 원격 코드 실행 또는 인증 우회를 유발할 수 있으며, OT 네트워크에 침투한 공격자가 생산 공정을 교란하거나 랜섬웨어를 유포할 수 있는 심각한 위협입니다. 두 취약점 모두 이미 PoC(Proof-of-Concept)가 공개되었고, 스캐닝 활동이 관찰되고 있어 실질적인 악용이 진행 중입니다.

#### 실무 영향 분석

DevSecOps 관점에서 이번 사건은 **공급망 보안과 클라우드 자격 증명 관리의 취약점**을 동시에 드러냅니다. MLflow는 CI/CD 파이프라인에서 모델 학습·배포 단계에 통합되는 경우가 많아, 취약한 버전이 파이프라인 내부에 존재하면 **파이프라인 자체가 공격 경로**가 됩니다. 또한 SSRF를 통해 탈취한 클라우드 자격 증명은 **장기간 유효한 IAM 키**일 경우, 데이터 유출이나 추가 리소스 남용으로 이어질 수 있습니다.

FUXA의 경우 OT 환경에서의 패치 적용이 지연되는 특성(가동 중단 최소화, 승인 절차 등)으로 인해 **제로데이 기간이 길어질 위험**이 있습니다. DevSecOps 팀은 IT 보안 정책을 OT에 그대로 적용하기보다 **세그멘테이션, 네트워크 모니터링, 비상 대응 절차**를 별도로 수립해야 합니다.



---

### 1.3 Ransom Busters, 랜섬웨어 서버를 해킹했다고 주장하며 피해자들에게 최대 6만 달러 요구

{% include news-card.html
  title="Ransom Busters, 랜섬웨어 서버를 해킹했다고 주장하며 피해자들에게 최대 6만 달러 요구"
  url="https://thehackernews.com/2026/08/ransom-busters-claims-it-hacked.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjo_eOapavOiIGXF7klCQPyN0-Qg2nWk9KlUYzPHuLwAyMKM75P3E2jciQR3v9gt2UBmez3XRSC57e5Fe9Oowm2brtgRXz5nJMPN8iQnBYddnTI4DyffnBAh4iLQFSOhA-8RhbbwuXqbJQOkhiXo5asFku1kFfmQd-UsHT6ulzdvRvw7WXwFKYFBTU_Q9nB/s1600/ransom.jpg"
  summary="Ransom Busters라는 랜섬웨어 제휴 조직이 피해 기관에 이메일을 보내 랜섬웨어 그룹 서버에서 탈취된 데이터를 삭제해 주는 대가로 $20,000에서 $60,000를 요구하고 있습니다. GuidePoint Research는 이러한 제3자의 개입이 비정상적이라고 지적했습니다."
  source="The Hacker News"
  severity="Critical"
%}

#### 기술적 배경 및 위협 분석

이번에 등장한 **Ransom Busters**는 전형적인 **이중 착취(Fraud-on-Fraud)** 공격 패턴을 보여줍니다. 이들은 랜섬웨어 그룹의 C2 서버나 데이터 유출 사이트를 해킹했다고 주장하며, 피해 기업에게 **"탈취된 데이터를 삭제해 주겠다"**며 2만~6만 달러를 요구합니다. 

기술적으로 이는 **중간자(Man-in-the-Middle) 수준의 정보 비대칭**을 악용한 사기입니다. 실제로 랜섬웨어 그룹의 인프라를 침투했는지 여부는 확인되지 않았으며, 대부분의 경우 **피해자 정보를 랜섬웨어 협상 과정에서 유출된 이메일 스레드나 OSINT(공개 정보)로 수집**했을 가능성이 높습니다. 특히 GuidePoint Research가 지적한 "피해자에게 먼저 연락하는 비정상적 행동"은 기존 랜섬웨어 그룹의 운영 방식(침묵 유지 → 협상)과 전혀 다르며, **사기꾼이 단순히 피해자의 심리적 취약 상태를 노린 정황**으로 판단됩니다.

위협의 핵심은 **이중 사기**입니다. (1) 피해자가 돈을 지불해도 실제 데이터 삭제가 이뤄지지 않을 가능성이 높고, (2) 지불 정보(암호화폐 지갑, 이메일 등)를 확보한 이후 **추가 피싱이나 랜섬웨어 재감염**에 악용할 수 있습니다. 또한, 이들이 주장하는 "해킹"이 사실일 경우, 랜섬웨어 생태계의 내부 분열을 유발해 **공격자 간 정보 거래 시장**이 형성될 수 있다는 점도 간과할 수 없습니다.

#### 실무 영향 분석

DevSecOps 실무자 관점에서 이 사건은 **위협 대응 프로세스에 새로운 변수**를 추가합니다.

- **협상 단계 오염**: 기존에는 랜섬웨어 그룹과의 협상만 고려하면 됐지만, 이제 제3자 사기꾼이 개입하여 **협상 채널이 이원화**됩니다. 이는 법무·협상팀의 의사결정을 방해하고, 실제 랜섬웨어 그룹이 요구하는 금액보다 낮은 금액으로 유인하여 **피해자가 불필요한 비용을 지출**하게 만듭니다.
- **데이터 유출 범위 확대**: 만약 Ransom Busters가 실제로 랜섬웨어 서버를 침투했다면, 이는 **공급망 공격(Supply Chain Attack)** 과 유사한 파급 효과를 가집니다. 피해 기업의 데이터가 이중으로 유출될 위험이 있으며, **규제 당국(GDPR, KISA 등)에 대한 신고 의무**와 법적 책임이 복잡해집니다.
- **탐지 및 모니터링 우선순위**: 기존의 침해 지표(IOC) 기반 탐지로는 이 새로운 위협을 식별하기 어렵습니다. **비정상 발신 이메일(외부에서 "복구 제안"을 가장한 피싱)** 에 대한 게이트웨이 필터링과, 내부 직원 대상 **사회공학 공격 대비 교육**이 시급해집니다.



---

## 2. AI/ML 뉴스

### 2.1 국가 안보 분야의 민주적 감독 강화

{% include news-card.html
  title="국가 안보 분야의 민주적 감독 강화"
  url="https://openai.com/index/strengthening-democratic-oversight-in-national-security"
  summary="OpenAI는 국가 안보 분야에서 AI에 대한 민주적 감독을 강화하기 위한 이니셔티브를 시작했습니다. 이 이니셔티브는 정부 기관에 도구, 교육, 전문성을 제공하여 민주적 통제를 지원합니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

OpenAI는 국가 안보 분야에서 AI에 대한 민주적 감독을 강화하기 위한 이니셔티브를 시작했습니다. 이 이니셔티브는 정부 기관에 도구, 교육, 전문성을 제공하여 민주적 통제를 지원합니다.


---

### 2.2 CodeAI와 협력하여 첫 AI 세대를 준비하다

{% include news-card.html
  title="CodeAI와 협력하여 첫 AI 세대를 준비하다"
  url="https://openai.com/index/partnering-with-codeai"
  summary="OpenAI와 CodeAI가 협력하여 학생들이 AI 리터러시를 갖추고, AI에 대해 비판적으로 사고하며, 책임감 있게 활용하고 발전시킬 수 있는 기술을 개발하도록 돕습니다. 이 파트너십은 첫 AI 세대를 준비시키는 것을 목표로 합니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

OpenAI와 CodeAI가 협력하여 학생들이 AI 리터러시를 갖추고, AI에 대해 비판적으로 사고하며, 책임감 있게 활용하고 발전시킬 수 있는 기술을 개발하도록 돕습니다. 이 파트너십은 첫 AI 세대를 준비시키는 것을 목표로 합니다.


---

### 2.3 사이버 중요 역량 시대의 모델 개발 속도 조절

{% include news-card.html
  title="사이버 중요 역량 시대의 모델 개발 속도 조절"
  url="https://openai.com/index/pacing-model-development-cyber-capabilities"
  summary="OpenAI는 최첨단 AI 모델에 대한 모니터링, 정렬, 보안을 강화하고 있으며, 새로운 안전장치가 모델 개발 속도를 조율하는 데 중요한 역할을 하고 있습니다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

OpenAI는 최첨단 AI 모델에 대한 모니터링, 정렬, 보안을 강화하고 있으며, 새로운 안전장치가 모델 개발 속도를 조율하는 데 중요한 역할을 하고 있습니다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 자동 조종 모드의 거버넌스, 난기류 없이

{% include news-card.html
  title="자동 조종 모드의 거버넌스, 난기류 없이"
  url="https://cloud.google.com/blog/products/data-analytics/governance-on-autopilot-automate-data-governance-with-lineage/"
  summary="데이터 팀은 cust_seg_flg 같은 컬럼의 의미와 안전성을 확인하기 위해 매번 동료에게 물어봐야 하며, 이런 상황이 수천 개의 테이블에서 반복되면 거버넌스 부채(governance debt)가 단순한 규정 위반이 아닌 모든 구성원의 일상 업무에 부과되는 세금이 됩니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

데이터 팀은 cust_seg_flg 같은 컬럼의 의미와 안전성을 확인하기 위해 매번 동료에게 물어봐야 하며, 이런 상황이 수천 개의 테이블에서 반복되면 거버넌스 부채(governance debt)가 단순한 규정 위반이 아닌 모든 구성원의 일상 업무에 부과되는 세금이 됩니다.


---

### 3.2 Google Dataflow에서 비용 효율적이고 고처리량의 생성형 AI 워크플로 구축하기

{% include news-card.html
  title="Google Dataflow에서 비용 효율적이고 고처리량의 생성형 AI 워크플로 구축하기"
  url="https://cloud.google.com/blog/products/data-analytics/cost-effective-genai-workflows-in-google-dataflow/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/image1_XYX8VCT.max-1000x1000.jpg"
  summary="Google Dataflow에서 생성형 AI 에이전트를 통합해 기존의 정적 스트리밍 DAG를 넘어 적응형 실행이 가능한 비용 효율적이고 고처리량의 AI 워크플로우를 구축하는 방법을 다룹니다. 실시간 스트리밍 파이프라인은 기업 운영의 핵심이지만, 전통적으로 배포 후 로직이 고정되어 있었습니다. 이제 AI를 결합해 동적이고 유연한 처리를 실현합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Dataflow에서 생성형 AI 에이전트를 통합해 기존의 정적 스트리밍 DAG를 넘어 적응형 실행이 가능한 비용 효율적이고 고처리량의 AI 워크플로우를 구축하는 방법을 다룹니다. 실시간 스트리밍 파이프라인은 기업 운영의 핵심이지만, 전통적으로 배포 후 로직이 고정되어 있었습니다. 이제 AI를 결합해 동적이고 유연한 처리를 실현합니다.


---

### 3.3 Box, Gemini Embeddings 2로 멀티모달 엔터프라이즈 에이전트를 구현하다

{% include news-card.html
  title="Box, Gemini Embeddings 2로 멀티모달 엔터프라이즈 에이전트를 구현하다"
  url="https://cloud.google.com/blog/topics/partners/box-ai-agents-gemini-embeddings-multimodal-enterprise-ai/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/original_images/GIF_1_1AuFwiE.gif"
  summary="Box는 클라우드 마이그레이션 이후 최대의 아키텍처 변화를 맞아, Gemini Embeddings 2를 활용해 금융 모델, 임상 시험 프로토콜, M&A 실사 자료 등 기업 데이터를 처리하는 멀티모달 엔터프라이즈 에이전트를 구현하고 있습니다. 이는 Box에 저장된 수조 기가바이트의 핵심 데이터를 기반으로 한 새로운 전환점을 의미합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Box는 클라우드 마이그레이션 이후 최대의 아키텍처 변화를 맞아, Gemini Embeddings 2를 활용해 금융 모델, 임상 시험 프로토콜, M&A 실사 자료 등 기업 데이터를 처리하는 멀티모달 엔터프라이즈 에이전트를 구현하고 있습니다. 이는 Box에 저장된 수조 기가바이트의 핵심 데이터를 기반으로 한 새로운 전환점을 의미합니다.


---

## 4. DevOps & 개발 뉴스

### 4.1 JetBrains용 GitHub Copilot의 엔터프라이즈 관리 설정

{% include news-card.html
  title="JetBrains용 GitHub Copilot의 엔터프라이즈 관리 설정"
  url="https://github.blog/changelog/2026-08-18-enterprise-managed-settings-in-github-copilot-for-jetbrains"
  image="https://github.blog/wp-content/uploads/2026/08/637261473-31523768-888f-4cea-8123-8bc06cf6a51f.png"
  summary="GitHub Copilot for JetBrains가 이제 엔터프라이즈 관리 설정을 지원하여 플러그인 거버넌스, MCP 서버 접근, OpenTelemetry, 권한 모드를 관리자가 일관되게 제어할 수 있습니다. 이 기능은 기업 내 모든 사용자에게 동일한 정책을 적용할 수 있게 해줍니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot for JetBrains가 이제 엔터프라이즈 관리 설정을 지원하여 플러그인 거버넌스, MCP 서버 접근, OpenTelemetry, 권한 모드를 관리자가 일관되게 제어할 수 있습니다. 이 기능은 기업 내 모든 사용자에게 동일한 정책을 적용할 수 있게 해줍니다.


---

### 4.2 토큰 유형별 자격 증명 폐기 및 권한 해제

{% include news-card.html
  title="토큰 유형별 자격 증명 폐기 및 권한 해제"
  url="https://github.blog/changelog/2026-08-18-credential-revocation-and-deauthorization-by-token-type"
  image="https://github.blog/wp-content/uploads/2026/08/637196833-94e35c27-ab19-456c-9c74-b62e6b63454e.jpg"
  summary="GitHub Blog에서 발표한 내용으로, 보안 사고 대응 시 셀프서비스 자격 증명 철회 기능을 확장하여 이제 토큰 유형과 사용자별로 자격 증명을 비활성화하고 철회할 수 있습니다. 이를 통해 관리자는 보다 세밀하게 사용자 자격 증명을 제어할 수 있게 되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Blog에서 발표한 내용으로, 보안 사고 대응 시 셀프서비스 자격 증명 철회 기능을 확장하여 이제 토큰 유형과 사용자별로 자격 증명을 비활성화하고 철회할 수 있습니다. 이를 통해 관리자는 보다 세밀하게 사용자 자격 증명을 제어할 수 있게 되었습니다.


---

### 4.3 17,600 Actions: 에이전트 보안은 시스템 문제다

{% include news-card.html
  title="17,600 Actions: 에이전트 보안은 시스템 문제다"
  url="https://www.docker.com/blog/ai-agent-security-systems-problem/"
  summary="OpenAI와 Hugging Face의 보안 사고에서 17,600건의 공격자 행동이 드러나며, AI 에이전트 보안이 인간 검토에 의존할 수 없음을 입증했다. 에이전트를 신속하게 제약하고 관찰하며 통제하기 위한 시스템 차원의 보안 컨트롤이 필수적이다."
  source="Docker Blog"
  severity="Medium"
%}

#### 요약

OpenAI와 Hugging Face의 보안 사고에서 17,600건의 공격자 행동이 드러나며, AI 에이전트 보안이 인간 검토에 의존할 수 없음을 입증했다. 에이전트를 신속하게 제약하고 관찰하며 통제하기 위한 시스템 차원의 보안 컨트롤이 필수적이다.


---

## 5. 블록체인 뉴스

### 5.1 BitBox, 펌웨어에서 '심각한' 취약점 발견 후 Bitcoin 사용자에 경고

{% include news-card.html
  title="BitBox, 펌웨어에서 '심각한' 취약점 발견 후 Bitcoin 사용자에 경고"
  url="https://bitcoinmagazine.com/news/bitbox-warns-users-about-vulnerability"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/08/BitBox-Warns-Bitcoiners-After-Discovering-Severe-Vulnerability-In-Firmware.jpg"
  summary="BitBox가 자사 하드웨어 지갑 펌웨어에서 '심각한' 취약점을 발견해 수정했으며, 자금 도난은 없었다고 밝혔다. 그러나 사용자들에게 신중한 업그레이드를 강하게 권고했다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

BitBox가 자사 하드웨어 지갑 펌웨어에서 '심각한' 취약점을 발견해 수정했으며, 자금 도난은 없었다고 밝혔다. 그러나 사용자들에게 신중한 업그레이드를 강하게 권고했다.


---

### 5.2 SEC, Clarity Act 지연 속 암호화폐 규칙서 제안

{% include news-card.html
  title="SEC, Clarity Act 지연 속 암호화폐 규칙서 제안"
  url="https://bitcoinmagazine.com/news/sec-proposes-crypto-rules"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/05/SEC-Delaying-Plan-to-Allow-Crypto-Versions-of-US-Stocks-Report.jpg"
  summary="SEC가 Clarity Act가 지연된 상황에서도 규제를 추진하며 암호화폐 관련 규정집을 제안했다. 이 소식은 Bitcoin Magazine이 Mathew Di Salvo의 기사로 보도했다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

SEC가 Clarity Act가 지연된 상황에서도 규제를 추진하며 암호화폐 관련 규정집을 제안했다. 이 소식은 Bitcoin Magazine이 Mathew Di Salvo의 기사로 보도했다.


---

### 5.3 Bitcoin의 격렬한 변동성, 약세장의 집요한 압박 속에서도 잠잠해지다

{% include news-card.html
  title="Bitcoin의 격렬한 변동성, 약세장의 집요한 압박 속에서도 잠잠해지다"
  url="https://bitcoinmagazine.com/news/bitcoin-volatility-dampens-vaneck"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/08/Bitcoins-Wild-Swings-Go-Quiet-Even-as-the-Bears-Wont-Let-Go.jpg"
  summary="VanEck의 새로운 연구에 따르면 Bitcoin의 변동성이 크게 완화되었지만, 약세론자들은 여전히 매도 압력을 유지하고 있습니다. 이 소식은 Bitcoin Magazine에 Mathew Di Salvo가 작성한 기사에서 전해졌습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

VanEck의 새로운 연구에 따르면 Bitcoin의 변동성이 크게 완화되었지만, 약세론자들은 여전히 매도 압력을 유지하고 있습니다. 이 소식은 Bitcoin Magazine에 Mathew Di Salvo가 작성한 기사에서 전해졌습니다.


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [토스는 어떻게 광고 속에 게임을 넣었을까](https://toss.tech/article/games-in-ads) | 토스 기술 블로그 | 토스에서 게임 광고를 받기 위해 MRAID 기반 플레이어블 광고 SDK를 직접 만든 이야기를 소개해요 |
| [Microsoft Copilot, 비밀 입력 노출로 해킹 가능해져](https://arstechnica.com/security/2026/08/microsoft-copilot-reveals-secret-input-that-allowed-it-to-be-hacked/) | Ars Technica | Microsoft Copilot에서 발견된 비밀 매개변수(secret parameter)가 해커가 링크 클릭 시 비밀번호를 탈취할 수 있게 한 취약점으로 드러났습니다. 이번 보안 결함은 Copilot의 입력 처리 과정에서 노출된 것으로, 사용자 주의가 요구됩니다 |
| [AI 시대의 증가하는 수요에 대응하기 위한 인프라 효율성 개선](https://dropbox.tech/infrastructure/improving-infrastructure-efficiency-for-growing-demand-in-the-age-of-ai) | Dropbox Tech Blog | AI 수요 증가에 따라 이를 지원하는 인프라 효율성 개선의 중요성이 커지고 있다. 원문은 AI 시대의 성장하는 수요에 맞춰 인프라 효율성을 높여야 한다는 점을 강조한다 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 7건 | 기타 주제 |
| **AI/ML** | 5건 | The Hacker News 관련 동향, OpenAI Blog 관련 동향, Google Cloud Blog 관련 동향 |
| **인증 보안** | 2건 | Attackers 익스플로잇 MLflow SSRF 결함 탈취, AWS Security Blog 관련 동향 |
| **클라우드 보안** | 1건 | Attackers 익스플로잇 MLflow SSRF 결함 탈취 |
| **랜섬웨어** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(7건)입니다. **AI/ML** 분야에서는 The Hacker News 관련 동향, OpenAI Blog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **공격자들이 MLflow SSRF 취약점을 악용해 클라우드 자격 증명과 비밀 정보를 탈취하다** 관련 긴급 패치 및 영향도 확인
- [ ] **Ransom Busters, 랜섬웨어 서버를 해킹했다고 주장하며 피해자들에게 최대 6만 달러 요구** 관련 긴급 패치 및 영향도 확인
- [ ] **AgentCore Gateway에서 request Lambda 인터셉터를 사용해 도구 통합용 사용자 지정 인증 구현하기** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **에이전틱 소스 코드 리뷰를 통한 적대적 AI 대응 선도** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **국가 안보 분야의 민주적 감독 강화** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
