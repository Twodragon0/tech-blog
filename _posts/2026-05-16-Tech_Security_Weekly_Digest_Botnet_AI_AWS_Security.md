---
layout: post
title: "2026년 05월 16일 주간 보안 다이제스트: BYOVD EDR·AI 에이전트·쿠버네티스 (13건)"
date: 2026-05-16 11:07:01 +0900
last_modified_at: 2026-05-21T18:36:46+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Botnet, AI, AWS, Security]
excerpt: "2026년 05월 16일 공개된 26건의 위협·취약점 가운데 Turla, Kazuar 백도어를 모듈형 P2P 봇넷으로 전환해 · AWS AI 보안 프레임워크: 적절한 통제, 적절한 계층이 즉각 대응 우선순위에 올랐습니다. 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다."
description: "2026년 05월 16일 보안 뉴스 요약. The Hacker News, AWS Security Blog, BleepingComputer 등 26건을 분석하고 Turla, Kazuar 백도어를 모듈형 P2P, AWS AI 보안 프레임워크 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Botnet, AI, AWS]
author: Twodragon
comments: true
image: /assets/images/2026-05-16-Tech_Security_Weekly_Digest_Botnet_AI_AWS_Security.svg
image_alt: "Turla, Kazuar P2P, AWS AI, 45 - security digest overview"
toc: true
summary_card:
  title: "2026년 05월 16일 주간 보안 다이제스트: BYOVD EDR·AI 에이전트·쿠버네티스 (13건)"
  period: "2026년 05월 16일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Botnet"
    - "AI"
    - "AWS"
    - "Security"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "Turla, Kazuar 백도어를 모듈형 P2P 봇넷으로 전환해 지속적 접근 확보" }
    - { source: "AWS Security Blog", title: "AWS AI 보안 프레임워크: 적절한 통제, 적절한 계층, 적절한 단계에서 AI 보안 확보" }
    - { source: "The Hacker News", title: "45일간의 자체 도구 모니터링이 실제 공격 표면에 대해 알려주는 것" }
    - { source: "Google Cloud Blog", title: "Gemini Live Agent Challenge: 수상자와 하이라이트 발표" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 05월 16일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 26개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 1개
- **클라우드 뉴스**: 5개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | Turla, Kazuar 백도어를 모듈형 P2P 봇넷으로 전환해 지속적 접근 확보 | 🟠 High |
| 🔒 **Security** | AWS Security Blog | AWS AI 보안 프레임워크: 적절한 통제, 적절한 계층, 적절한 단계에서 AI 보안 확보 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 45일간의 자체 도구 모니터링이 실제 공격 표면에 대해 알려주는 것 | 🟠 High |
| 🤖 **AI/ML** | AWS Machine Learning | Amazon S3용 Amazon Quick 지식 베이스에서 민감한 문서에 대한 액세스 제한 | 🟠 High |
| ☁️ **Cloud** | Google Cloud Blog | Gemini Live Agent Challenge: 수상자와 하이라이트 발표 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | BlackFile에 오신 것을 환영합니다: 비싱 갈취 작전 내부 | 🟡 Medium |
| ☁️ **Cloud** | AWS Korea Blog | AWS의 Claude Platform 소개: AWS 계정을 통한 Anthropic의 네이티브 Claude Platform 시작하기 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Grok Code Fast 1 지원 중단 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Copilot Memory가 Pro, Pro+ 사용자를 위한 사용자 선호도를 지원 | 🟡 Medium |
| ⚙️ **DevOps** | Docker Blog | 맞춤형 MCP 카탈로그 및 프로필: 엔터프라이즈 MCP 도입의 진전 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: Turla, Kazuar 백도어를 모듈형 P2P 봇넷으로 전환해 지속적 접근 확보, 45일간의 자체 도구 모니터링이 실제 공격 표면에 대해 알려주는 것, Amazon S3용 Amazon Quick 지식 베이스에서 민감한 문서에 대한 액세스 제한 등 High 등급 위협 3건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 Turla, Kazuar 백도어를 모듈형 P2P 봇넷으로 전환해 지속적 접근 확보

{% include news-card.html
  title="Turla, Kazuar 백도어를 모듈형 P2P 봇넷으로 전환해 지속적 접근 확보"
  url="https://thehackernews.com/2026/05/turla-turns-kazuar-backdoor-into.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg8BT1AOScncZQM_A-0WBdCzTDAHGHSey48_Mywhij-TJupCdzP3s3o-MIImRtMZcoV2OqX3RjRV4COpVqkB1mrH3d_zjwvSTwCEXOq_2m80HgDo-xwAZ1KpR1h8eN9dAHGcKN_PpcE0cBsnv67FcthDycHLBJMYs8NkPszWNiQqdbhyL0YIlwVJn4NtgaR/s1600/code.jpg"
  summary="러시아 정부 후원 해킹 그룹 Turla가 자체 백도어 Kazuar를 모듈식 P2P 봇넷으로 변환하여 은밀하고 지속적인 접근을 가능하게 했습니다. CISA에 따르면 Turla는 러시아 FSB의 Center 16과 연계된 것으로 평가됩니다."
  source="The Hacker News"
  severity="High"
%}

# DevSecOps 실무자 관점에서 본 Turla Kazuar P2P Botnet 분석

## 1. 기술적 배경 및 위협 분석

러시아 FSB 산하 해킹 그룹 Turla가 기존 Kazuar 백도어를 모듈형 P2P 봇넷으로 진화시켰다. 이는 중앙 C&C 서버에 의존하지 않고 감염 호스트 간 직접 통신(P2P)을 통해 명령을 전파하는 구조로, 탐지 및 차단이 극히 어렵다. 주요 기술적 특징은 다음과 같다:

- **모듈형 아키텍처**: 백도어가 단일 페이로드가 아닌, 필요에 따라 플러그인을 동적으로 로드할 수 있는 구조로 변경됨. 이는 공격자가 환경에 맞춰 기능을 선택적으로 활성화할 수 있음을 의미함
- **P2P 통신**: 중앙 서버 없이 감염 노드 간 암호화된 P2P 채널을 통해 명령 및 데이터 전송. 블록체인 유사 분산 구조로 단일 노드 차단만으로는 봇넷 전체를 무력화할 수 없음
- **지속성 강화**: 시스템 재부팅 후에도 유지되는 은닉 메커니즘과 정상 트래픽으로 위장한 통신 패턴 사용

DevSecOps 관점에서 이 위협은 **공급망 공격**, **CI/CD 파이프라인 침투**, **컨테이너 환경 내 지속성 확보** 등으로 발전할 가능성이 높다. 특히 모듈형 구조는 특정 DevOps 도구(예: Jenkins, GitLab Runner)를 대상으로 한 플러그인 형태로 변형될 수 있다.

## 2. 실무 영향 분석

- **CI/CD 파이프라인 보안 위협 증가**: Kazuar의 모듈형 특성은 CI/CD 파이프라인 내 빌드 에이전트나 테스트 환경에 백도어를 심는 데 악용될 수 있음. P2P 통신은 내부 네트워크를 통해 봇넷을 확산시키는 데 이상적
- **컨테이너 환경 취약점**: 쿠버네티스 클러스터 내 파드 간 P2P 통신은 정상적인 마이크로서비스 트래픽으로 위장하기 쉬움. 런타임 보안 탐지가 어려워짐
- **코드 서명 및 무결성 검증 우회**: 모듈형 구조는 코드 서명 검증을 우회하고 악성 플러그인을 동적으로 로드할 수 있어, 기존의 정적 분석 기반 보안 도구가 무력화됨
- **DevSecOps 파이프라인 내 탐지 지연**: 전통적인 시그니처 기반 탐지로는 P2P 기반 변종 탐지가 어려워, 보안 팀의 대응 시간이 지연됨

## 3. 대응 체크리스트

- [ ] CI/CD 파이프라인 내 모든 빌드 에이전트와 러너에 대해 **네트워크 기반 행동 분석(Network Behavior Anomaly Detection)** 도구를 도입하여 비정상적인 P2P 트래픽 패턴 탐지
- [ ] 컨테이너 이미지 및 런타임 환경에 대해 **무결성 검증(Integrity Monitoring)** 및 **허용 목록(Allowlist)** 기반의 모듈 로드 제어 정책 수립
- [ ] 모든 개발 및 운영 환경에서 **최소 권한 원칙(Least Privilege)** 을 적용하고, 서비스 계정의 네트워크 통신을 엄격히 제한하는 네트워크 정책(Istio, Calico 등) 구현
- [ ] 코드 저장소(Git) 및 아티팩트 저장소(Nexus, Artifactory)에 대해 **변조 탐지 시스템** 구축 및 정기적인 서명 검증 자동화 파이프라인 추가
- [ ] DevSecOps 파이프라인에 **동적 행동 기반 분석(Dynamic Behavioral Analysis)** 단계를 통합하여, 런타임 시 악성 모듈 로드 시도를 탐지하는 테스트 자동

---

### 1.2 AWS AI 보안 프레임워크: 적절한 통제, 적절한 계층, 적절한 단계에서 AI 보안 확보

{% include news-card.html
  title="AWS AI 보안 프레임워크: 적절한 통제, 적절한 계층, 적절한 단계에서 AI 보안 확보"
  url="https://aws.amazon.com/blogs/security/the-aws-ai-security-framework-securing-ai-with-the-right-controls-at-the-right-layers-at-the-right-phases/"
  summary="AWS AI Security Framework는 AI 워크로드가 프로토타입에서 프로덕션, 확장 단계로 진화함에 따라 보안을 처음부터 강화하도록 설계되었습니다. 보안 리더는 무료 SHIP engagement를 통해 현재 상태를 평가하고 우선순위 로드맵을 수립할 수 있습니다. 이 프레임워크는 적절한 통제를 적절한 계층과 단계에 적용하여 AI 보안을 신속하게 확"
  source="AWS Security Blog"
  severity="Medium"
%}

# AWS AI Security Framework 분석: DevSecOps 실무자 관점

## 1. 기술적 배경 및 위협 분석

AWS AI Security Framework는 AI 워크로드의 전 생애주기(프로토타입 → 프로덕션 → 확장)에 걸쳐 **계층별(Layer)**, **단계별(Phase)** 보안 통제를 적용하는 구조적 접근법이다. 이 프레임워크는 AI 시스템이 기존 소프트웨어와 달리 **데이터 파이프라인, 모델 학습, 추론 엔드포인트** 등 복잡한 공격 표면을 가진다는 점에 주목한다.

**주요 위협 요소:**
- **공급망 공격**: 학습 데이터 변조(Data Poisoning), 모델 가중치 탈취
- **추론 단계 공격**: 프롬프트 인젝션, 모델 도용(Model Stealing), 역공학
- **운영 단계 위협**: 모델 드리프트로 인한 편향/오류, 권한 상승을 통한 모델 조작
- **규제 리스크**: GDPR, AI Act 등 컴플라이언스 위반

AWS는 **SHIP(Security, Health, Identity, Protection)** 엔지니어링 접근법을 통해 보안을 Day 0부터 통합할 것을 강조하며, 이는 DevSecOps의 **Shift-Left** 원칙과 정확히 일치한다.

## 2. 실무 영향 분석

DevSecOps 실무자에게 이 프레임워크는 **CI/CD 파이프라인에 AI 특화 보안 게이트를 추가**해야 함을 시사한다.

**주요 실무 변화:**
- **파이프라인 확장**: 기존 SAST/DAST 외에 **모델 취약점 스캐닝**(예: ModelScan, Adversarial Robustness Toolbox)을 CI/CD에 통합
- **인프라스트럭처 코드(IaC) 보안**: Terraform/CDK로 배포되는 SageMaker, Bedrock 등 AI 서비스에 **IAM 조건 키, VPC 엔드포인트, 데이터 암호화** 설정 자동화
- **런타임 모니터링**: 모델 추론 로그를 실시간 분석하여 **이상 탐지**(비정상 입력 패턴, 과도한 API 호출)를 Security Information and Event Management(SIEM)에 연동
- **거버넌스 자동화**: AWS Config 규칙으로 모델 버전 관리, 데이터 레이블링 감사 추적, 출력 필터링 정책을 코드로 관리

**핵심 인사이트**: AI 보안은 단순히 "모델 보호"가 아니라 **데이터 → 모델 → 추론 → 피드백** 순환 구조 전체를 보호해야 하며, 이는 DevSecOps의 **Continuous Security** 개념의 자연스러운 확장이다.

## 3. 대응 체크리스트

- [ ] **AI 워크로드에 대한 위협 모델링 세션을 2주 내에 진행**하여 데이터 변조, 모델 탈취, 프롬프트 인젝션 등 시나리오별 대응 방안 수립
- [ ] **CI/CD 파이프라인에 모델 보안 스캐닝 단계 추가** (예: GitHub Actions에서 Snyk 또는 AWS Inspector로 모델 컨테이너 취약점 검사)
- [ ] **IaC 템플릿에 AI 서비스 보안 베이스라인 적용** (SageMaker 노트북에 VPC만 허용, Bedrock 엔드포인트에 AWS WAF 연결 등)
- [ ] **모델 추론 로그에 대한 실시간 이상 탐지 규칙 생성** (CloudWatch Logs → Lambda → Security Hub 연동)
- [ ] **분기별 AI 보안 거버넌스 리뷰 일정 수립** (모델 드리프트 모니터링, 데이터 접근 권한 감사, 규제 변경 사항 반영)

---

### 1.3 45일간의 자체 도구 모니터링이 실제 공격 표면에 대해 알려주는 것

{% include news-card.html
  title="45일간의 자체 도구 모니터링이 실제 공격 표면에 대해 알려주는 것"
  url="https://thehackernews.com/2026/05/what-45-days-of-watching-your-own-tools.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhVcSUDrpIZyFrHqIlIGnXfIShsEamRNviaM6TguPwmQI9KkhrIXOQbQ0WVKiOkcBGkFqKTKZmK16zPChmlcCbZHIkX3K_C0sjnyXYJjpZuJXO3OiIhUe7Ez8jCNiTxh0FGYS2-RR6HKsl9pWJVgc_uXAtHXj0hgU-mLSsOh-QHft6A92KtgWPQhk1OVPA/s1600/Attack-Surface.jpg"
  summary="Bitdefender의 분석에 따르면, 조직 내 가장 위험한 활동은 더 이상 명백한 공격이 아닌 일상적인 관리 작업처럼 보이며, PowerShell, WMIC, netsh, Certutil, MSBuild와 같은 신뢰되는 유틸리티가 현대 위협 행위자의 선호 도구로 사용되고 있습니다."
  source="The Hacker News"
  severity="High"
%}

# DevSecOps 실무자 관점 보안/기술 뉴스 분석

**제목:** What 45 Days of Watching Your Own Tools Will Tell You About Your Real Attack Surface

---

## 1. 기술적 배경 및 위협 분석

해당 기사는 조직 내에서 신뢰받는 시스템 도구(PowerShell, WMIC, netsh, Certutil, MSBuild 등)가 실제 공격 표면으로 활용되는 현상을 집중 조명한다. Bitdefender의 45일간 모니터링 분석에 따르면, 현대 위협 행위자들은 악성코드 배포보다 **신뢰 기반의 정상 도구 남용(Living-off-the-Land, LotL)** 을 선호한다. 이는 기존의 시그니처 기반 탐지를 우회하고, 보안 팀이 정상 관리 활동과 공격을 구분하기 어렵게 만든다.

특히 주목할 점은:
- **PowerShell**은 코드 실행, 메모리 내 악성 페이로드 로드, C2 통신에 활용
- **Certutil**은 인증서 다운로드 기능을 악용해 악성 파일 다운로드
- **MSBuild**는 코드 서명 우회 및 비정상 빌드 프로세스 실행에 사용

이러한 도구들은 **이미 신뢰된 프로세스**로 분류되어 EDR/AV 탐지를 우회할 수 있으며, 정상 관리 활동과의 경계가 모호해 실질적인 위협 탐지가 어렵다.

## 2. 실무 영향 분석

DevSecOps 환경에서 이는 **파이프라인 무결성**과 **운영 보안**에 직접적인 위협이 된다.

- **CI/CD 파이프라인 내 취약점**: 빌드 서버에서 PowerShell이나 MSBuild가 정상적으로 실행되므로, 공급망 공격 시 악성 스크립트가 탐지되지 않고 주입될 수 있다.
- **컨테이너 및 인프라 관리 도구 남용**: kubectl, docker, helm 등도 유사한 LotL 벡터가 될 수 있으며, 이는 쿠버네티스 환경에서의 권한 상승 및 데이터 유출로 이어진다.
- **모니터링 사각지대**: 기존 보안 솔루션은 "정상 도구"의 비정상적 사용 패턴을 식별하지 못하며, DevSecOps 팀은 로그 양의 폭증으로 실제 위협을 놓칠 위험이 있다.
- **규정 준수 위험**: 신뢰 도구 남용은 규정 감사에서 발견되지 않을 수 있으며, 사후 분석 시에도 정상 활동으로 오인될 가능성이 높다.

## 3. 대응 체크리스트

- [ ] **CI/CD 파이프라인 내 모든 스크립트 실행에 대한 행동 기반 모니터링 구축**: PowerShell, MSBuild 등의 실행 시 인자, 네트워크 연결, 파일 생성 패턴을 지속적으로 분석하고 이상 징후를 실시간 알림
- [ ] **신뢰 도구 사용에 대한 최소 권한 원칙 강화**: 각 도구가 필요한 최소한의 권한만 부여하고, 관리자 권한이 필요한 작업은 승인 절차와 감사 로그 기록 필수화
- [ ] **비정상적 도구 사용 패턴 탐지 규칙 수립**: 예: Certutil로 외부 URL에서 파일 다운로드, PowerShell의 -EncodedCommand 사용, MSBuild의 외부 프로젝트 파일 로드 등에 대한 경고 규칙 생성
- [ ] **컨테이너 이미지 빌드 시 불필요한 시스템 도구 제거**: 프로덕션 이미지에서 PowerShell, wmic 등 불필요한 도구를 제거하고, 최소 이미지(예: distroless) 사용 정책 수립
- [ ] **정기적인 LotL 시뮬레이션 및 레드팀 테스트 수행**: 분기별로 실제 공격자가 사용하는 신뢰 도구 기반 시나리오를 모의 훈련에 포함시켜 탐지 및 대응 능력 검증

---

## 2. AI/ML 뉴스

### 2.1 Amazon S3용 Amazon Quick 지식 베이스에서 민감한 문서에 대한 액세스 제한

{% include news-card.html
  title="Amazon S3용 Amazon Quick 지식 베이스에서 민감한 문서에 대한 액세스 제한"
  url="https://aws.amazon.com/blogs/machine-learning/restrict-access-to-sensitive-documents-in-your-amazon-quick-knowledge-bases-for-amazon-s3/"
  summary="Amazon Quick의 S3 knowledge base에서 문서 수준 ACL을 구성하여 민감한 문서에 대한 접근을 제한하는 방법을 설명합니다. 채팅 및 자동화 워크플로우에서 문서 수준 권한을 적용하는 ACL 설정 및 검증 과정을 다룹니다."
  source="AWS Machine Learning Blog"
  severity="High"
%}

#### 요약

Amazon Quick의 S3 knowledge base에서 문서 수준 ACL을 구성하여 민감한 문서에 대한 접근을 제한하는 방법을 설명합니다. 채팅 및 자동화 워크플로우에서 문서 수준 권한을 적용하는 ACL 설정 및 검증 과정을 다룹니다.

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Gemini Live Agent Challenge: 수상자와 하이라이트 발표

{% include news-card.html
  title="Gemini Live Agent Challenge: 수상자와 하이라이트 발표"
  url="https://cloud.google.com/blog/topics/developers-practitioners/winners-and-highlights-of-the-gemini-live-agent-challenge/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/bryen.max-1000x1000.jpg"
  summary="Google의 Gemini Live Agent Challenge가 종료되었으며, 전 세계 151개국에서 11,878명의 참가자와 1,536개의 제출 프로젝트를 기록했습니다. 이 대회는 개발자들이 전통적인 텍스트 박스 패러다임을 벗어난 차세대 AI 에이전트를 구축하도록 도전했습니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google의 Gemini Live Agent Challenge가 종료되었으며, 전 세계 151개국에서 11,878명의 참가자와 1,536개의 제출 프로젝트를 기록했습니다. 이 대회는 개발자들이 전통적인 텍스트 박스 패러다임을 벗어난 차세대 AI 에이전트를 구축하도록 도전했습니다.

---

### 3.2 BlackFile에 오신 것을 환영합니다: 비싱 갈취 작전 내부

{% include news-card.html
  title="BlackFile에 오신 것을 환영합니다: 비싱 갈취 작전 내부"
  url="https://cloud.google.com/blog/topics/threat-intelligence/blackfile-vishing-extortion-operation/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/blackfile-fig5.max-1000x1000.png"
  summary="Google Threat Intelligence Group(GTIG)이 추적 중인 위협 행위자 UNC6671은 ”BlackFile” 브랜드로 조직을 대상으로 정교한 voice phishing(vishing)과 single sign-on(SSO) 침해를 통한 광범위한 갈취 캠페인을 전개하고 있습니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Threat Intelligence Group(GTIG)이 추적 중인 위협 행위자 UNC6671은 "BlackFile" 브랜드로 조직을 대상으로 정교한 voice phishing(vishing)과 single sign-on(SSO) 침해를 통한 광범위한 갈취 캠페인을 전개하고 있습니다.

---

### 3.3 AWS의 Claude Platform 소개: AWS 계정을 통한 Anthropic의 네이티브 Claude Platform 시작하기

{% include news-card.html
  title="AWS의 Claude Platform 소개: AWS 계정을 통한 Anthropic의 네이티브 Claude Platform 시작하기"
  url="https://aws.amazon.com/ko/blogs/tech/introducing-claude-platform-on-aws-anthropics-native-platform-through-your-aws-account/"
  summary="이 글은 AWS Artificial Intelligence Blog에 게시된 Introducing Claude Platform on AWS: Anthropic's native platform, through your AWS account 를 한국어로 번역 및 편집하였습니다."
  source="AWS Korea Blog"
  severity="Medium"
%}

#### 요약

이 글은 AWS Artificial Intelligence Blog에 게시된 Introducing Claude Platform on AWS: Anthropic’s native platform, through your AWS account 를 한국어로 번역 및 편집하였습니다.

---

## 4. DevOps & 개발 뉴스

### 4.1 Grok Code Fast 1 지원 중단

{% include news-card.html
  title="Grok Code Fast 1 지원 중단"
  url="https://github.blog/changelog/2026-05-15-grok-code-fast-1-deprecated"
  summary="GitHub Copilot의 모든 기능에서 Grok Code Fast 1 모델이 2026년 5월 15일자로 지원 중단되었습니다. 이는 모델 폐기의 일환으로, 해당 모델은 더 이상 사용할 수 없게 되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot의 모든 기능에서 Grok Code Fast 1 모델이 2026년 5월 15일자로 지원 중단되었습니다. 이는 모델 폐기의 일환으로, 해당 모델은 더 이상 사용할 수 없게 되었습니다.

---

### 4.2 Copilot Memory가 Pro, Pro+ 사용자를 위한 사용자 선호도를 지원

{% include news-card.html
  title="Copilot Memory가 Pro, Pro+ 사용자를 위한 사용자 선호도를 지원"
  url="https://github.blog/changelog/2026-05-15-copilot-memory-supports-user-preferences-for-pro-pro-users"
  summary="GitHub이 Copilot Pro 및 Pro+ 사용자를 대상으로 Copilot Memory 기능의 얼리 액세스를 시작했습니다. 이 기능은 사용자가 명시하거나 유추된 개인 선호도를 저장하여 더 개인화된 경험을 제공합니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub이 Copilot Pro 및 Pro+ 사용자를 대상으로 Copilot Memory 기능의 얼리 액세스를 시작했습니다. 이 기능은 사용자가 명시하거나 유추된 개인 선호도를 저장하여 더 개인화된 경험을 제공합니다.

---

### 4.3 맞춤형 MCP 카탈로그 및 프로필: 엔터프라이즈 MCP 도입의 진전

{% include news-card.html
  title="맞춤형 MCP 카탈로그 및 프로필: 엔터프라이즈 MCP 도입의 진전"
  url="https://www.docker.com/blog/create-custom-mcp-catalogs-and-profiles/"
  image="https://www.docker.com/app/uploads/2025/03/image.png"
  summary="Docker가 MCP 서버 관리를 위한 Custom Catalogs와 Profiles 기능을 정식 출시했습니다. Custom Catalogs는 조직이 승인된 MCP 서버 모음을 선별 및 배포할 수 있게 하고, MCP Profiles는 개별 개발자가 쉽게 구축 및 실행할 수 있도록 지원합니다."
  source="Docker Blog"
  severity="Medium"
%}

#### 요약

Docker가 MCP 서버 관리를 위한 Custom Catalogs와 Profiles 기능을 정식 출시했습니다. Custom Catalogs는 조직이 승인된 MCP 서버 모음을 선별 및 배포할 수 있게 하고, MCP Profiles는 개별 개발자가 쉽게 구축 및 실행할 수 있도록 지원합니다.

---

## 5. 블록체인 뉴스

### 5.1 비트코인 오픈, 2026년 6월 8일 이벤트를 위해 상징적인 Glen Abbey Golf Club으로 향하다

{% include news-card.html
  title="비트코인 오픈, 2026년 6월 8일 이벤트를 위해 상징적인 Glen Abbey Golf Club으로 향하다"
  url="https://bitcoinmagazine.com/culture/bitcoin-open-heads-to-iconic-glen-abbey-golf-club-for-june-8-2026-event"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/05/tnpregrass.webp"
  summary="Bitcoin Open이 2026년 6월 8일, 온타리오주 오크빌의 상징적인 Glen Abbey Golf Club에서 개최된다고 발표했다. 이 행사는 팀 스크램블 골프 토너먼트와 저녁 Texas Hold'em 포커 토너먼트로 구성되며, Glen Abbey Golf Club의 개장 50주년이 되는 해에 열린다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Bitcoin Open이 2026년 6월 8일, 온타리오주 오크빌의 상징적인 Glen Abbey Golf Club에서 개최된다고 발표했다. 이 행사는 팀 스크램블 골프 토너먼트와 저녁 Texas Hold'em 포커 토너먼트로 구성되며, Glen Abbey Golf Club의 개장 50주년이 되는 해에 열린다.

---

### 5.2 아부다비 무바달라, 2026년 1분기 비트코인 ETF 지분 16% 늘려 5억6600만 달러로 확대

{% include news-card.html
  title="아부다비 무바달라, 2026년 1분기 비트코인 ETF 지분 16% 늘려 5억6600만 달러로 확대"
  url="https://bitcoinmagazine.com/news/abu-dhabis-mubadala-raises-bitcoin-stake"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/05/Abu-Dhabis-Mubadala-Raises-Bitcoin-ETF-Stake-16-to-566-Million-in-Q1-2026.jpg"
  summary="아부다비의 무바달라 투자회사가 2026년 1분기 블랙록의 iShares Bitcoin Trust 지분을 16% 늘려 5억 6600만 달러 규모로 확대했다. 이 소식은 비트코인 매거진이 보도했다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

아부다비의 무바달라 투자회사가 2026년 1분기 블랙록의 iShares Bitcoin Trust 지분을 16% 늘려 5억 6600만 달러 규모로 확대했다. 이 소식은 비트코인 매거진이 보도했다.

---

### 5.3 Gemini 주가, Winklevoss 쌍둥이가 회사 미래에 1억 달러 비트코인 베팅하며 급등

{% include news-card.html
  title="Gemini 주가, Winklevoss 쌍둥이가 회사 미래에 1억 달러 비트코인 베팅하며 급등"
  url="https://bitcoinmagazine.com/news/gemini-stock-jumps-after-winklevoss-twins"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/04/New-York-Sues-Coinbase-and-Gemini-Over-Alleged-Illegal-Prediction-Market-Gambling-Operations.jpg"
  summary="Winklevoss 쌍둥이가 Gemini에 1억 달러 규모의 Bitcoin 투자를 발표하고, Q1 실적에서 전년 대비 42%의 매출 성장을 보고하면서 Gemini 주가가 상승했습니다. 이 소식은 Bitcoin Magazine에 Micah Zimmerman이 기고한 내용입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Winklevoss 쌍둥이가 Gemini에 1억 달러 규모의 Bitcoin 투자를 발표하고, Q1 실적에서 전년 대비 42%의 매출 성장을 보고하면서 Gemini 주가가 상승했습니다. 이 소식은 Bitcoin Magazine에 Micah Zimmerman이 기고한 내용입니다.

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [Windows XP 데스크톱처럼 Wikipedia 탐색하기](https://news.hada.io/topic?id=29551) | GeekNews (긱뉴스) | Wikipedia File Explorer 는 Wikipedia 카테고리를 Windows XP 데스크톱의 폴더처럼 열어 탐색하는 웹 인터페이스임 Wikipedia의 카테고리 는 폴더처럼, 문서는 파일처럼 열리며 카테고리 없는 약 100개 안팎의 페이지를 제외하면 모든 항목에 접근 가능함 |
| [Mullvad exit IP는 놀라울 정도로 식별 가능함](https://news.hada.io/topic?id=29550) | GeekNews (긱뉴스) | Mullvad 는 서버 하나에 여러 exit IP를 두지만, WireGuard 키 기반으로 결정적으로 배정해 접속마다 무작위로 바뀌지 않음 9개 서버에서 pubkey를 반복 변경해 모은 3,650개 데이터 포인트 는 가능한 8.2조 개 조합 중 284개 조합에만 배정됨 각 서버의 ex |
| [지금 많은 기업이 AI 집단 광기에 빠져 있다고 믿는다](https://news.hada.io/topic?id=29549) | GeekNews (긱뉴스) | 미첼 하시모토: " 지금 많은 기업이 심각한 AI 집단 광기에 빠져 있으며, 그들과 이성적인 대화를 나누는 것은 불가능하다 " 클라우드 인프라 자동화 시대의 MTBF vs MTTR 논쟁 이 이제 소프트웨어 개발 산업 전체로 확산되고 있으며, AI 에이전트에 대한 맹 |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 10건 | 기타 주제 |
| **AI/ML** | 3건 | AWS AI 보안 프레임워크 Securing AI, GS SHOP의 영상 기반 AI 상품 추천 플랫폼 구축기, Agentic AI 기반 플랫폼 |
| **클라우드 보안** | 2건 | AWS AI 보안 프레임워크 Securing AI, AWS의 Claude Platform 소개 |
| **공급망 보안** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(10건)입니다. **AI/ML** 분야에서는 AWS AI 보안 프레임워크 Securing AI, GS SHOP의 영상 기반 AI 상품 추천 플랫폼 구축기 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **TanStack 공급망 공격, OpenAI 직원 기기 2대 감염시키며 macOS 업데이트 강제** 관련 긴급 패치 및 영향도 확인
- [ ] **Funnel Builder WordPress 플러그인 버그 악용되어 신용카드 정보 탈취** 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **Turla, Kazuar 백도어를 모듈형 P2P 봇넷으로 전환해 지속적 접근 확보** 관련 보안 검토 및 모니터링
- [ ] **45일간의 자체 도구 모니터링이 실제 공격 표면에 대해 알려주는 것** 관련 보안 검토 및 모니터링
- [ ] **Amazon S3용 Amazon Quick 지식 베이스에서 민감한 문서에 대한 액세스 제한** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Amazon S3용 Amazon Quick 지식 베이스에서 민감한 문서에 대한 액세스 제한** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [Cisco Catalyst SD-WAN, Stealer Backdoor가 개발자, ThreatsDay 게시판](/posts/2026/05/15/Tech_Security_Weekly_Digest_AI_Threat_AWS_Go/) — 2026-05-15
- [Funnel Builder Flaw, Microsoft, 중요한 Azure 취약점, 러시아 해커, Kazuar 백도어를 모듈형](/posts/2026/05/17/Tech_Security_Weekly_Digest_CVE_Vulnerability_Azure_Botnet/) — 2026-05-17
- [AI 기반 합성 공격 로그 생성을 통한 탐지, 새로운 Exim BDAT 취약점으로 GnuTLS, AI 속도의 방어](/posts/2026/05/13/Tech_Security_Weekly_Digest_AI_Vulnerability_Security_Agent/) — 2026-05-13

---

**작성자**: Twodragon
