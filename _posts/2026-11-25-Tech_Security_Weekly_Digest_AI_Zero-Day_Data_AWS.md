---
layout: post
title: "2026년 11월 25일 주간 보안 다이제스트: 제로데이·패치·DNS 유출 (27건)"
date: 2026-11-25 02:46:20 +0900
last_modified_at: 2026-11-25T02:46:20+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Zero-Day, Data, Go]
excerpt: "‘이란 연계 Volant Manticore’ 소식 · ‘VMware vCenter, 제로데이 악용 이후 또 다른 치명적’ 소식이 부각된 2026년 11월 25일 보안 다이제스트 — 27건의 이슈와 실행 가능한 대응 액션을 정리합니다. 사안별 소스와 영향도를 표로 정리해 우선순위 판단 근거를 남겼습니다."
description: "2026년 11월 25일 보안 뉴스 요약. The Hacker News, AWS Security Blog 등 27건을 분석하고 이란 연계 Volant Manticore, VMware vCenter, Okta 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Zero-Day, Data]
author: Twodragon
comments: true
image: /assets/images/2026-11-25-Tech_Security_Weekly_Digest_AI_Zero-Day_Data_AWS.svg
image_alt: "Volant Manticore, VMware vCenter, Okta, ShinyHunters - security digest overview"
toc: true
summary_card:
  title: "2026년 11월 25일 주간 보안 다이제스트: 제로데이·패치·DNS 유출 (27건)"
  period: "2026년 11월 25일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Zero-Day"
    - "Data"
    - "Go"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "이란 연계 Volant Manticore, 첩보 캠페인에서 IPFS 기반 KuboShell 백도어 사용" }
    - { source: "The Hacker News", title: "VMware vCenter, 제로데이 악용 이후 또 다른 치명적 9.8 등급 인증 우회 취약점에 노출" }
    - { source: "The Hacker News", title: "Okta, ShinyHunters 연계 비싱 조직과 새로운 INCEPTION 데이터 유출 사이트 연결" }
    - { source: "Google Cloud Blog", title: "제로 트러스트 구현: ALLEN의 Chrome Enterprise Premium 전환" }
redirect_from:
- /posts/2026/11/25/Tech_Security_Weekly_Digest_AI_Zero-Day_Data_AWS/
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 11월 25일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 27개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 4개
- **클라우드 뉴스**: 5개
- **DevOps 뉴스**: 3개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | 이란 연계 Volant Manticore, 첩보 캠페인에서 IPFS 기반 KuboShell 백도어 사용 | 🟠 High |
| 🔒 **Security** | The Hacker News | VMware vCenter, 제로데이 악용 이후 또 다른 치명적 9.8 등급 인증 우회 취약점에 노출 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | Okta, ShinyHunters 연계 비싱 조직과 새로운 INCEPTION 데이터 유출 사이트 연결 | 🟠 High |
| 🤖 **AI/ML** | Google AI Blog | Gemini가 Golden State 조직과 팬들에게 판도를 어떻게 바꾸고 있는가 | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | OpenAI와 Cisco, Shirudo 공개 | 🟠 High |
| 🤖 **AI/ML** | AWS Machine Learning | Anthropic의 Enterprise Frontier Safeguards 및 Enterprise Data Controls와 함께하는 Amazon Bedrock Trusted Access API 소개 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 제로 트러스트 구현: ALLEN의 Chrome Enterprise Premium 전환 | 🟠 High |
| ☁️ **Cloud** | AWS Blog | AWS 주간 라운드업: 보고타 Local Zone, 30분 Lambda 타임아웃 등 (2026년 11월 24일) | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | AI 에이전트로 AWS 운영 질문에 답하기 – 1부: Amazon Bedrock AgentCore로 조회 도구 연결하기 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | GitHub.com에서 더 예측 가능한 알림 제공 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: VMware vCenter, 제로데이 악용 이후 또 다른 치명적 9.8 등급 인증 우회 취약점에 노출 등 Critical 등급 위협 1건이 확인되었습니다.
- **주요 모니터링 대상**: 이란 연계 Volant Manticore, 첩보 캠페인에서 IPFS 기반 KuboShell 백도어 사용, Okta, ShinyHunters 연계 비싱 조직과 새로운 INCEPTION 데이터 유출 사이트 연결, OpenAI와 Cisco, Shirudo 공개 등 High 등급 위협 4건에 대한 탐지 강화가 필요합니다.
- 제로데이 취약점이 보고되었으며, 임시 완화 조치 적용과 벤더 패치 일정 확인이 시급합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 분석가 시점

현장 운영 관점에서 보면 이번 주기 헤드라인 세 건은 결국 `신뢰 경계가 무너지는 지점`이 서로 다르다는 걸 보여준다. IPFS 기반 KuboShell 백도어는 아웃바운드 트래픽 허용 정책과 egress 필터링의 사각을 찌르고, vCenter의 9.8 인증 우회는 패치 창과 자산 인벤토리 지연이 곧 침해로 이어짐을 증명하며, Okta 연계 vishing은 사람을 통한 자격증명 탈취가 여전히 최전선임을 확인시킨다. DevSecOps 실무자가 이번 주기에 가장 먼저 봐야 할 신호는 **vCenter 같은 관리 평면 자산의 패치 SLA와 egress 정책을 동시에 점검하는 일**이다. GitHub Actions 파이프라인에서 관리 평면 취약점 스캔을 게이트로 걸고, AWS IAM 권한 최소화와 eBPF 기반 아웃바운드 가시성을 붙여야 다음 사이클을 버틴다.

## 1. 보안 뉴스

### 1.1 이란 연계 Volant Manticore, 첩보 캠페인에서 IPFS 기반 KuboShell 백도어 사용

{% include news-card.html
  title="이란 연계 Volant Manticore, 첩보 캠페인에서 IPFS 기반 KuboShell 백도어 사용"
  url="https://thehackernews.com/2026/11/iran-aligned-volant-manticore-uses-ipfs.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhqukTcR2pkDWiTqMzORa4j7zZRB0MDUGfBly50X7gPwPHqSeBmfReQWpMR9IdPOP_NbeuQSBdYPknSgxvutDll4VAZNSoGqcwmXzhZNEez-UoE-MwTnM9i9XxjoLYRdhY0iY6tD9BK9IDB0o8RUU7sNsOex5tVNtoNwRHCCAxM9ri66c4G2wPa9AqW9saA/s1600/iran-hackers.jpg"
  summary="이란 연계 사이버 첩보 그룹 Volant Manticore가 키프로스의 통신사, 항공사, 핵심 인프라를 대상으로 공격을 수행했다. 이 그룹은 IPFS를 C2 통신에 활용하는 KuboShell 백도어와 침투 후 프레임워크인 Homa를 배포하는 것으로 나타났다."
  source="The Hacker News"
  severity="High"
%}

#### Volant Manticore IPFS 백도어 분석 (DevSecOps 관점)

#### 기술적 배경 및 위협 분석

Volant Manticore는 키프로스의 통신·항공·핵심 인프라를 겨냥한 이란 연계 스파이 그룹으로, **KuboShell** 백도어의 C2 채널로 IPFS(InterPlanetary File System)를 악용한다. IPFS는 콘텐츠 해시 기반 분산 파일 시스템으로, Kubo 노드가 공용 게이트웨이와 P2P로 통신하기 때문에 전통적 도메인·IP 평판 기반 탐지가 무력화된다. C2 트래픽이 정상 IPFS 트래픽과 구분되지 않아 프록시·NGFW 로그에서도 저탐지율을 보이며, 콘텐츠 애드레싱(CID)으로 명령을 게시·회수하는 구조는 테이크다운도 어렵다. 침해 후에는 Homa 프레임워크(알려진 프레임워크 재구현)를 배포해 측면 이동·지속성을 확보한다. 즉 **"정상 서비스로 위장한 C2"** 라는 공급망·경계 우회형 위협 모델이다.

#### 실무 영향 분석

- **탐지 체계 재설계 필요**: 기존 IOC(도메인/IP) 중심 룰셋으로는 IPFS C2를 잡기 어렵다. Kubo 노드 프로세스, IPFS 게이트웨이 아웃바운드, CID 형태 문자열 등 행위 기반 시그널로 전환해야 한다.
- **이그레스 통제 강화**: 개발·운영 환경에서 IPFS 데몬(5001/8080 포트)이나 공용 게이트웨이로의 아웃바운드가 허용되어 있다면 즉시 정책 재검토 대상이다.
- **CI/CD 및 개발자 워크스테이션 리스크**: Kubo 바이너리나 IPFS 라이브러리가 의존성으로 유입될 경우 빌드 파이프라인이 C2 경유지가 될 수 있어 SCA·SBOM 검증이 중요하다.
- **텔레콤·항공 등 OT/레거시 환경**: 패치 주기가 긴 환경이 표적이므로 네트워크 분할과 아웃바운드 화이트리스트가 1차 방어선이다.



---

### 1.2 VMware vCenter, 제로데이 악용 이후 또 다른 치명적 9.8 등급 인증 우회 취약점에 노출

{% include news-card.html
  title="VMware vCenter, 제로데이 악용 이후 또 다른 치명적 9.8 등급 인증 우회 취약점에 노출"
  url="https://thehackernews.com/2026/11/vmware-vcenter-hit-by-another-critical.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi0zpQTclLnhVQHphFdBZZ_hrxhsZvA5G50sGBz5qq1iOg2B1YLu8rE5e_HM1GZOE24SNpwexwst80NTKP7_Wwexq7EzIl-I7ykIXCtTGQjeZhBGVVuAgzxac5JwaquTQuMNRstBFo8JzMDyqgsNbM_KtxGF3wHPBIM9GfaclNu0OTPlpF5YhNvqoKKytAY/s1600/vmware-exploit.jpg"
  summary="Broadcom이 VMware ESX, vCenter, Workstation, Fusion, Avi Load Balancer에 영향을 주는 23개 취약점 패치를 배포했으며, 여기에는 인증 우회가 가능한 CVSS 9.8점의 critical 결함 CVE-2026-123903이 포함됩니다."
  source="The Hacker News"
  severity="Critical"
%}

#### 기술적 배경 및 위협 분석

CVE-2026-123903은 VMware Directory Service(vmdir)에서 발생한 인증 우회 취약점으로 CVSS 9.8을 기록했다. vmdir은 vCenter SSO(Single Sign-On)의 핵심 구성요소로, LDAP 기반 디렉터리 서비스와 인증 토큰 발급을 담당한다. 즉 이 취약점이 악용되면 공격자는 별도 자격증명 없이 vCenter 관리 평면에 접근해 SSO 관리자 권한 획득으로 이어질 수 있다. 특히 요약문에 "Zero-Day Exploitation"이 명시된 점이 핵심이다. 패치 이전에 실제 공격에 사용됐다는 의미로, PoC 공개 전 익스플로이트가 이미 유통되고 있다는 뜻이다. ESX, Workstation, Fusion, Avi Load Balancer까지 23개 취약점이 함께 패치된 점을 볼 때, 하이퍼바이저 계층 전반의 공격 표면이 넓어진 상황이다. vCenter는 가상 인프라의 단일 통제점(single point of control)이므로, 여기서의 인증 우회는 곧 전체 VM·ESXi 호스트·스토리지 정책에 대한 장악으로 직결된다.

#### 실무 영향 분석

DevSecOps 관점에서 가장 큰 리스크는 **CI/CD 파이프라인의 빌드 인프라가 vCenter 위에 올라가 있는 경우**다. Jenkins, GitLab Runner, Tekton 등이 VM 기반으로 운영된다면 vCenter 장악이 곧 파이프라인 장악이며, 시크릿 탈취·이미지 변조·아티팩트 오염으로 확장된다. 또한 IaC(Terraform vSphere provider 등) 자동화 계정이 SSO에 묶여 있어 인증 우회 시 권한 상승 경로가 된다. 컴플라이언스 측면에서는 CIS Benchmark·PCI-DSS의 인증 통제 요건 위반 소지가 있고, SBOM/취약점 관리 파이프라인에 vCenter가 자산으로 등록되지 않아 스캔 사각지대에 있는 조직이 많다는 점도 문제다. 패치 주기가 인프라팀 소관이라 DevSecOps 팀이 가시성을 갖지 못하는 조직 구조적 이슈도 드러난다.



#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - T1203  # Exploitation for Client Execution
    - T1078  # Valid Accounts
```

---

### 1.3 Okta, ShinyHunters 연계 비싱 조직과 새로운 INCEPTION 데이터 유출 사이트 연결

{% include news-card.html
  title="Okta, ShinyHunters 연계 비싱 조직과 새로운 INCEPTION 데이터 유출 사이트 연결"
  url="https://thehackernews.com/2026/11/okta-links-shinyhunters-associated.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjete6dy8Fmd7sbjqKI5GKSySXkcnz4NF__irfVMBHzgRIDUnpGHtvRIbCywZYYsoKsnMdPhvanoXcnXbYvZpMjL2lL6d_F9a4ErEaI5rH_boPedH_ru2Ush9wonb8tYhGNVM6M_01DTue1THY7uGMbuKBJKNgMbrACkxHCGJiJylHWoxkkpCXNr2Z_CIdf/s1600/leaks.jpg"
  summary="Okta의 Threat Intelligence 팀에 따르면 ShinyHunters 갈취 조직과 연관된 것으로 평가된 위협 클러스터가 INCEPTION이라는 새 이름으로 리브랜딩하여 활동을 이어갈 가능성이 있다."
  source="The Hacker News"
  severity="High"
%}

#### 기술적 배경 및 위협 분석

Okta 위협 인텔리전스 팀이 ShinyHunters 갈취 조직과 연관된 것으로 평가되던 위협 클러스터(O-UNC-053)가 **INCEPTION**이라는 새 이름으로 리브랜딩하여 활동을 지속하고 있다고 밝혔다. 핵심 위협 벡터는 **보이스 피싱(vishing)** 으로, 공격자는 전화로 대상자를 기만해 피싱 페이지에 자격증명을 입력하게 하고 MFA 승인까지 유도한다. 이는 기술적 취약점이 아닌 **인간 신뢰를 악용하는 사회공학 공격**으로, 전통적 경계 방어·EDR로는 탐지가 어렵다. Okta는 ID 공급자(IdP)로서 이 클러스터의 MFA 우회·세션 탈취 정황을 관찰할 수 있는 위치에 있다. 조직 리브랜딩은 탐지 규칙·위협 인텔리전스 매핑의 재조정이 필요함을 의미하며, 동일 TTP를 유지한 채 명칭만 바꾼 점이 특징이다.

#### 실무 영향 분석

DevSecOps 관점에서 이 사건은 **CI/CD 파이프라인과 클라우드 콘솔 접근 권한의 신뢰 경계**가 vishing으로 뚫릴 수 있음을 시사한다. 특히:

- **MFA 피로·푸시 승인 의존 구조**가 취약점으로 작용 — Okta/SSO 계정 탈취 시 파이프라인 시크릿, 배포 권한까지 연쇄 노출
- **헬프데스크/온콜 채널**을 통한 사칭 전화가 내부자 접근으로 이어질 수 있음
- 위협 인텔리전스 피드(IoC, TTP)의 명칭 변경 반영 지연 시 **탐지 공백** 발생
- 공급망(IdP 의존) 리스크 — Okta 테넌트 설정·로그 모니터링 강화 필요



---

## 2. AI/ML 뉴스

### 2.1 Gemini가 Golden State 조직과 팬들에게 판도를 어떻게 바꾸고 있는가

{% include news-card.html
  title="Gemini가 Golden State 조직과 팬들에게 판도를 어떻게 바꾸고 있는가"
  url="https://blog.google/products-and-platforms/products/gemini/gemini-golden-state/"
  image="https://storage.googleapis.com/gweb-uniblog-publish-prod/images/Google_Gemini_1.max-600x600.format-webp.webp"
  summary="Google Gemini가 Golden State와 파트너십을 맺고 Warriors, Valkyries, Chase Center의 팬 경험과 비즈니스 운영을 지원한다. 이번 협업을 통해 Gemini가 조직과 팬들에게 새로운 경험을 제공하는 방식이 주목된다."
  source="Google AI Blog"
  severity="Medium"
%}


---

### 2.2 OpenAI와 Cisco, Shirudo 공개

{% include news-card.html
  title="OpenAI와 Cisco, Shirudo 공개"
  url="https://openai.com/index/introducing-shirudo"
  summary="OpenAI와 Cisco가 Linux용 오픈소스 런타임 Shirudo를 공개했다. Shirudo는 팀이 패치를 배포하는 동안 실행 중인 시스템을 보호할 수 있도록 돕는다."
  source="OpenAI Blog"
  severity="High"
%}


---

### 2.3 Anthropic의 Enterprise Frontier Safeguards 및 Enterprise Data Controls와 함께하는 Amazon Bedrock Trusted Access API 소개

{% include news-card.html
  title="Anthropic의 Enterprise Frontier Safeguards 및 Enterprise Data Controls와 함께하는 Amazon Bedrock Trusted Access API 소개"
  url="https://aws.amazon.com/blogs/machine-learning/introducing-the-amazon-bedrock-trusted-access-api-with-anthropics-enterprise-frontier-safeguards-and-enterprise-data-controls/"
  summary="Amazon Bedrock이 모델 제공자 프로그램을 한곳에서 탐색·요청·등록할 수 있는 trusted access program API를 출시했습니다."
  source="AWS Machine Learning Blog"
  severity="Medium"
%}

#### 요약

Amazon Bedrock이 모델 제공자 프로그램을 한곳에서 탐색·요청·등록할 수 있는 trusted access program API를 출시했습니다. 첫 공개 프리뷰로 Anthropic의 Enterprise Frontier Safeguards(EFS)와 Enterprise Data Controls(EDC)가 제공되며, 이를 통해 Claude Fable 모델 사용 시 데이터를 제어할 수 있습니다.


---

## 3. 클라우드 & 인프라 뉴스

### 3.1 제로 트러스트 구현: ALLEN의 Chrome Enterprise Premium 전환

{% include news-card.html
  title="제로 트러스트 구현: ALLEN의 Chrome Enterprise Premium 전환"
  url="https://cloud.google.com/blog/products/chrome-enterprise/enabling-zero-trust-allens-move-to-chrome-enterprise-premium/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/Untitled_Design_26.max-1000x1000.png"
  summary="ALLEN은 1988년 라자스탄 코타에서 설립된 인도 주요 코칭 기관으로, 78개 도시 350개 이상 캠퍼스에서 40만 명 이상의 학생에게 서비스를 제공한다."
  source="Google Cloud Blog"
  severity="High"
%}

#### 요약

ALLEN은 1988년 라자스탄 코타에서 설립된 인도 주요 코칭 기관으로, 78개 도시 350개 이상 캠퍼스에서 40만 명 이상의 학생에게 서비스를 제공한다. IT 및 사이버보안 리더십 팀은 5,000명 이상의 사용자를 대상으로 민감한 데이터를 보호하고 zero trust를 구현하기 위해 Chrome Enterprise Premium으로 표준화한 과정을 공유했다. SaaS 및 멀티클라우드 환경 전반에서 브라우저 기반으로 업무를 수행하는 인력에게 디지털 환경 보안은 무엇보다 중요하다.


---

### 3.2 AWS 주간 라운드업: 보고타 Local Zone, 30분 Lambda 타임아웃 등 (2026년 11월 24일)

{% include news-card.html
  title="AWS 주간 라운드업: 보고타 Local Zone, 30분 Lambda 타임아웃 등 (2026년 11월 24일)"
  url="https://aws.amazon.com/blogs/aws/aws-weekly-roundup-local-zone-in-bogota-30-minute-lambda-timeout-and-more-november-24-2026/"
  summary="AWS가 2026년 11월 넷째 주에 Bogotá Local Zone을 출시하고 Lambda의 최대 실행 시간을 기존 15분에서 30분으로 두 배 늘렸다. 같은 주에 Lambda는 GPU 지원을 추가했으며, 이는 2014년 60초에서 시작해 2018년 15분에 이르기까지 단계적으로 확장되어 온 타임아웃 한도의 연장이다."
  source="AWS Blog"
  severity="Medium"
%}


---

### 3.3 AI 에이전트로 AWS 운영 질문에 답하기 – 1부: Amazon Bedrock AgentCore로 조회 도구 연결하기

{% include news-card.html
  title="AI 에이전트로 AWS 운영 질문에 답하기 – 1부: Amazon Bedrock AgentCore로 조회 도구 연결하기"
  url="https://aws.amazon.com/ko/blogs/tech/connecting-operational-queries-to-amazon-bedrock-agentcore-1/"
  summary="서비스를 처음 만들었을 때는 리소스의 용도와 연결 관계를 설명하기 쉽습니다. 기능과 서비스가 늘어나고 담당자가 바뀌면 상황이 달라집니다"
  source="AWS Korea Blog"
  severity="Medium"
%}


---

## 4. DevOps & 개발 뉴스

### 4.1 GitHub.com에서 더 예측 가능한 알림 제공

{% include news-card.html
  title="GitHub.com에서 더 예측 가능한 알림 제공"
  url="https://github.blog/changelog/2026-11-24-more-predictable-notifications-on-github-com"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-improvements.jpg"
  summary="GitHub는 2026년 12월 1일부터 일주일에 걸쳐 GitHub.com의 notifications을 마이그레이션하여 subscriptions을 더 예측 가능하게 만들고 예상치 못한 동작을 수정하며 증가하는 활동 규모를 지원할 예정입니다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

### 4.2 이슈 상태와 리포지토리 보드가 공개 미리보기로 제공됩니다

{% include news-card.html
  title="이슈 상태와 리포지토리 보드가 공개 미리보기로 제공됩니다"
  url="https://github.blog/changelog/2026-11-23-issue-statuses-and-repository-boards-are-in-public-preview"
  image="https://github.blog/wp-content/uploads/2026/11/716292665-b61bd263-dd28-430c-a147-fa22594ac67f.png"
  summary="GitHub에서 issue의 진행 상황을 더 구체적으로 표시할 수 있는 issue statuses와 repository boards가 public preview로 공개되었다. 기존의 open/closed만으로는 파악하기 어려웠던 작업 상태를 팀과 에이전트가 공유할 수 있게 된다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

### 4.3 Secret scanning, Slack에 대한 오탐 감소

{% include news-card.html
  title="Secret scanning, Slack에 대한 오탐 감소"
  url="https://github.blog/changelog/2026-11-23-secret-scanning-reduces-false-positives-for-slack"
  image="https://github.blog/wp-content/uploads/2026/11/571554102-6349f5b6-b0b7-4130-9300-6d5d87e0b6e9_0ff548.jpg"
  summary="GitHub의 secret scanning이 Slack secret에 대한 오탐(false positive) 검출을 줄이는 개선을 적용했습니다. slack_incoming_webhook_url 등 지원되는 secret 유형에서 특정 URL을 제외하는 방식으로 탐지 정확도를 높였습니다."
  source="GitHub Changelog"
  severity="Medium"
%}


---

## 5. 블록체인 뉴스

### 5.1 Coldcard 사후 분석, 해킹된 기기가 아닌 취약한 시드가 Bitcoin 탈취 초래했다 밝혀

{% include news-card.html
  title="Coldcard 사후 분석, 해킹된 기기가 아닌 취약한 시드가 Bitcoin 탈취 초래했다 밝혀"
  url="https://bitcoinmagazine.com/news/coldcard-postmortem-seed-flaw"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/Coldcard-Postmortem-Says-Weak-Seeds-Not-Hacked-Devices-Drove-Bitcoin-Thefts.jpg"
  summary="Coinkite는 Coldcard 포스트모템 전문을 공개하며 5년간 존재한 펌웨어 결함이 지갑 시드를 약화시켰고 약 242개 고객 계정이 손실을 신고했다고 밝혔다. 이번 사태는 기기 해킹이 아닌 취약한 시드가 Bitcoin 탈취의 원인이었다고 설명했다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 5.2 Stacks, 1,050 BTC 규모의 Bitcoin 스테이킹 용량으로 Bond 4 개시

{% include news-card.html
  title="Stacks, 1,050 BTC 규모의 Bitcoin 스테이킹 용량으로 Bond 4 개시"
  url="https://bitcoinmagazine.com/press-releases/stacks-opens-bond-4-with-1050-btc-of-bitcoin-staking-capacity"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/11/stacks-press-release.jpeg"
  summary="Stacks가 1,050 BTC 규모의 Bitcoin 스테이킹 용량으로 Bond 4를 개시했으며, 등록은 12월 5일경 시작된다. 앞서 Bond 3는 21shares와 Bullish 참여로 1,005 BTC에서 매진된 바 있다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

### 5.3 글로벌 부채가 Bitcoin을 세계에서 가장 성과 좋은 자산으로 만들 것이다

{% include news-card.html
  title="글로벌 부채가 Bitcoin을 세계에서 가장 성과 좋은 자산으로 만들 것이다"
  url="https://bitcoinmagazine.com/videos/global-debt-will-make-bitcoin-the-best-performing-asset-in-the-world"
  image="https://img.youtube.com/vi/6qNFLQyppLs/hqdefault.jpg"
  summary="Peoples Reserve의 창업자 겸 CEO인 CJ Konstantinos는 미국의 부채 문제가 Bitcoin의 가장 큰 순풍이 될 것이라고 주장하며, 글로벌 부채가 Bitcoin을 세계에서 가장 성과가 좋은 자산으로 만들 것이라고 전망했습니다. 해당 글은 Patrick Green이 작성해 Bitcoin Magazine에 처음 게재되었습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}


---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Jetpack Compose 기반 커스텀 3D 캐러셀 개발기 (영상)](https://d2.naver.com/helloworld/2957037) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER Engineering Day 10th 에서 발표되었던 세션을 공개합니다. ​ ​ 발표 내용 가로로 넘기는 목록을 만들 때 대부분 LazyRow부터 떠올립니다 |
| [내 Running Pod에 왜 접근할 수 없을까? kube-proxy nftables 모드로의 여정](https://medium.com/daangn/why-cant-my-running-pods-be-reached-our-journey-to-kube-proxy-nftables-mode-6fceb1d2a5f7?source=rss----4505f82a2dbd---4) | 당근 기술 블로그 | Karrot SRE의 Cluster 팀이 Kubernetes 플랫폼에서 kube-proxy를 iptables 모드에서 nftables 모드로 마이그레이션한 과정을 공유했습니다. 이 글에서는 클러스터의 관측 가능성과 안정성을 유지하기 위한 팀의 역할과 함께 마이그레이션 여정을 다룹니다 |
| [파드는 떴는데 왜 통신이 안 될까? kube-proxy nftables 전환 여정](https://medium.com/daangn/%ED%8C%8C%EB%93%9C%EB%8A%94-%EB%96%B4%EB%8A%94%EB%8D%B0-%EC%99%9C-%ED%86%B5%EC%8B%A0%EC%9D%B4-%EC%95%88-%EB%90%A0%EA%B9%8C-kube-proxy-nftables-%EC%A0%84%ED%99%98-%EC%97%AC%EC%A0%95-545dfd2cfc4f?source=rss----4505f82a2dbd---4) | 당근 기술 블로그 | 안녕하세요, 당근 SRE팀 클러스터 파트에서 일하고 있는 Karin(카린)이에요. 클러스터 파트는 당근 내부의 모든 서비스가 운영되는 Kubernetes 환경을 설계하고 관리해요 |


---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 9건 | 기타 주제 |
| **클라우드 보안** | 4건 | AWS Security Blog 관련 동향, AWS Blog 관련 동향, AI 에이전트로 AWS 운영 질문에 답하기 |
| **AI/ML** | 1건 | AI 에이전트로 AWS 운영 질문에 답하기 |
| **제로데이** | 1건 | The Hacker News 관련 동향 |
| **데이터 유출** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **클라우드 보안**(4건)입니다. AWS Security Blog 관련 동향, AWS Blog 관련 동향 등이 주요 이슈입니다. 

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **VMware vCenter, 제로데이 악용 이후 또 다른 치명적 9.8 등급 인증 우회 취약점에 노출** (CVE-2026-123903) 관련 긴급 패치 및 영향도 확인
- [ ] **해커들이 GitHub SHA 피닝을 우회하는 방법을 찾아냈다. 이 웨비나에서 격차를 해소하는 방법을 설명한다** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **이란 연계 Volant Manticore, 첩보 캠페인에서 IPFS 기반 KuboShell 백도어 사용** 관련 보안 검토 및 모니터링
- [ ] **Okta, ShinyHunters 연계 비싱 조직과 새로운 INCEPTION 데이터 유출 사이트 연결** 관련 보안 검토 및 모니터링
- [ ] **OpenAI와 Cisco, Shirudo 공개** 관련 보안 검토 및 모니터링
- [ ] **제로 트러스트 구현: ALLEN의 Chrome Enterprise Premium 전환** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Gemini가 Golden State 조직과 팬들에게 판도를 어떻게 바꾸고 있는가** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사

## 관련 포스트 및 참고 자료

- 2026년 11월 24일 주간 보안 다이제스트: {% post_url 2026-11-24-Tech_Security_Weekly_Digest_DeFi_Vulnerability_AI %}
- 2026년 11월 23일 주간 보안 다이제스트: {% post_url 2026-11-23-Tech_Security_Weekly_Digest_AI_Cloud_Data_Agent %}
- 2026년 11월 22일 주간 보안 다이제스트: {% post_url 2026-11-22-Tech_Security_Weekly_Digest_AI_Kubernetes_Data_AWS %}

| 리소스 | 링크 | 용도 |
|--------|------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | 실제 악용 확인된 취약점 목록 — 패치 우선순위 기준 |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) | 공격 전술·기법 매핑 — 탐지 룰 설계 |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) | 취약점 악용 확률 점수 — CVSS 보완 |
| The Hacker News | [thehackernews.com](https://thehackernews.com) | 본문 3건 인용 |
| Google AI Blog | [blog.google](https://blog.google) | 본문 1건 인용 |
| OpenAI Blog | [openai.com](https://openai.com) | 본문 1건 인용 |
| AWS Machine Learning Blog | [aws.amazon.com](https://aws.amazon.com) | 본문 1건 인용 |
| Google Cloud Blog | [cloud.google.com](https://cloud.google.com) | 본문 1건 인용 |
| AWS Blog | [aws.amazon.com](https://aws.amazon.com) | 본문 1건 인용 |
| AWS Korea Blog | [aws.amazon.com](https://aws.amazon.com) | 본문 1건 인용 |
| GitHub Changelog | [github.blog](https://github.blog) | 본문 3건 인용 |
| Bitcoin Magazine | [bitcoinmagazine.com](https://bitcoinmagazine.com) | 본문 3건 인용 |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [2026년 11월 24일 주간 보안 다이제스트: 제로데이·패치·AI 에이전트 (25건)](/posts/2026/11/24/Tech_Security_Weekly_Digest_DeFi_Vulnerability_AI/) — 2026-11-24
- [2026년 11월 22일 주간 보안 다이제스트: 패치·Kubernetes·클라우드 (16건)](/posts/2026/11/22/Tech_Security_Weekly_Digest_AI_Kubernetes_Data_AWS/) — 2026-11-22
- [2026년 11월 18일 주간 보안 다이제스트: 클라우드·제로데이·패치 (30건)](/posts/2026/11/18/Tech_Security_Weekly_Digest_AI_AWS_CVE_Patch/) — 2026-11-18

---

**작성자**: Twodragon
