---
layout: post
title: "2026년 07월 03일 주간 보안 다이제스트: 제로데이·랜섬웨어·BYOVD EDR (26건)"
date: 2026-07-03 11:04:43 +0900
last_modified_at: 2026-07-03T11:04:43+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Go, AI, Ransomware, Threat]
excerpt: "2026년 07월 03일 공개된 26건의 위협·취약점 가운데 Google, 200만 가정용 기기에 걸친 NetNut 리지덴셜 · 랜섬웨어 그룹, Citrix Bleed 2, BYOVD가 즉각 대응 우선순위에 올랐습니다. 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다."
description: "2026년 07월 03일 보안 뉴스 요약. The Hacker News, BleepingComputer 등 26건을 분석하고 Google, 200만 가정용 기기에 걸친, 랜섬웨어 그룹 등 DevSecOps 대응 포인트를 정리합니다. 주간 보안 위협 동향과 실무 대응 방안을 한곳에서 확인하세요."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Go, AI, Ransomware]
author: Twodragon
comments: true
image: /assets/images/2026-07-03-Tech_Security_Weekly_Digest_Go_AI_Ransomware_Threat.svg
image_alt: "Google, 200, Citrix Bleed 2, Anthropic, Claude Fable - security digest overview"
toc: true
summary_card:
  title: "2026년 07월 03일 주간 보안 다이제스트: 제로데이·랜섬웨어·BYOVD EDR (26건)"
  period: "2026년 07월 03일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Go"
    - "AI"
    - "Ransomware"
    - "Threat"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "Google, 200만 가정용 기기에 걸친 NetNut 리지덴셜 프록시 네트워크를 교란" }
    - { source: "The Hacker News", title: "랜섬웨어 그룹, Citrix Bleed 2, BYOVD, 공급망 자격증명으로 전환" }
    - { source: "BleepingComputer", title: "Anthropic, Claude Fable 5가 구독에서 영구적으로 사라지는 것은 아니라고 밝혀" }
    - { source: "Google Cloud Blog", title: "Google의 악성 가정용 프록시 네트워크에 대한 지속적인 방해" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 07월 03일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 26개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 1개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | Google, 200만 가정용 기기에 걸친 NetNut 리지덴셜 프록시 네트워크를 교란 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 랜섬웨어 그룹, Citrix Bleed 2, BYOVD, 공급망 자격증명으로 전환 | 🟠 High |
| 🔒 **Security** | BleepingComputer | Anthropic, Claude Fable 5가 구독에서 영구적으로 사라지는 것은 아니라고 밝혀 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | GeForce NOW에 12개의 게임이 추가되는 7월, 즐거운 질주를 시작하세요 | 🟠 High |
| 🤖 **AI/ML** | NVIDIA AI Blog | NVIDIA, AI 컴퓨팅을 대규모로 개방하며 파트너 초청해 AI 인프라 구축 지원 | 🟡 Medium |
| 🤖 **AI/ML** | Cointelegraph | OpenAI, 트럼프 협상 속 미국 정부 지분 5% 검토 중: FT | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Google의 악성 가정용 프록시 네트워크에 대한 지속적인 방해 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Copilot 사용 메트릭 보고서의 정확성과 적용 범위 개선 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | 예정된 Gemini 2.5 Pro 및 Gemini 3 Flash 지원 중단 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | GitHub Actions에서 Copilot CLI에 더 이상 개인 액세스 토큰이 필요하지 않습니다 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: 랜섬웨어 그룹, Citrix Bleed 2, BYOVD, 공급망 자격증명으로 전환, GeForce NOW에 12개의 게임이 추가되는 7월, 즐거운 질주를 시작하세요 등 High 등급 위협 2건에 대한 탐지 강화가 필요합니다.
- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | Medium | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | High | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 분석가 시점

이번 분석 사이클에서 가장 먼저 눈에 띄는 신호는 **Citrix Bleed 2 취약점을 랜섬웨어 그룹이 BYOVD와 공급망 크리덴셜 탈취로 연계**하는 정형화된 공격 체인이 등장했다는 점입니다. NetNut과 같은 200만 가정용 디바이스 기반 리버스 프록시 네트워크가 정찰·우회 인프라로 활용되는 상황에서, Claude Fable 5 구독 정책 혼란이 시사하는 AI 서비스의 신뢰성 문제는 보조적 관찰에 불과합니다. DevSecOps 실무자가 이번 주기에 가장 먼저 봐야 할 신호는 **공격자들이 더 이상 단일 CVE 패치로 방어할 수 없는 다층적 진입 경로를 표준화**하고 있다는 점이며, 이는 GitHub Actions 시크릿 스캐닝과 AWS IAM 조건 키 기반의 리소스 제한 정책을 즉시 재점검해야 함을 의미합니다.

## 1. 보안 뉴스

### 1.1 Google, 200만 가정용 기기에 걸친 NetNut 리지덴셜 프록시 네트워크를 교란

{% include news-card.html
  title="Google, 200만 가정용 기기에 걸친 NetNut 리지덴셜 프록시 네트워크를 교란"
  url="https://thehackernews.com/2026/07/google-disrupts-netnut-residential.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjAH6tBAe18U0FqA-i5kNNNQYeXjY_LBflzBqVD5rq81OAC6q9c8UsDBsQb5K2F7IAfof5_JZCBpS51DNp63jsXfk4qqwLkckDh4nq-z-Gj0zoRwQu5IZYiNHiBlpp3C-6OR84JeDfPmIr4VLTp2NN6uHRYl0qT273wrbpcnUmd5SbIJH07cPHQxMo6VgI/s1600/proxy.jpg"
  summary="Google이 FBI, Lumen 등과 협력하여 자택 기기를 타인의 트래픽 중계기로 전환하는 대규모 네트워크 NetNut(Popa)의 가용 장치 풀을 수백만 개 감소시켰습니다. 이 네트워크는 200만 대의 가정용 기기에 걸쳐 운영되며, Google Threat Intelligence Group(GTIG)이 이번 조치를 주도했습니다."
  source="The Hacker News"
  severity="Medium"
%}

# DevSecOps 관점에서 NetNut Residential Proxy Network 분석

## 1. 기술적 배경 및 위협 분석

NetNut(Popa)은 가정용 IoT 기기 200만 대를 무단으로 프록시 노드로 전환한 레지덴셜 프록시 네트워크입니다. 이는 **합법적인 ISP IP를 가진 정상 기기**를 경유해 트래픽을 우회시키는 구조로, 기존 데이터센터 IP 기반 차단 정책을 무력화합니다. Google의 Threat Intelligence Group(GTIG)은 FBI, Lumen과 협력해 NetNut의 가용 디바이스 풀을 대폭 축소시켰습니다.

**위협 포인트:**
- **악성 트래픽 출처 위장**: 봇넷, 크리덴셜 스터핑, 스캘핑 등 공격이 정상 가정용 IP에서 발생한 것처럼 위장
- **레이트 리밋 우회**: 분산된 IP 풀을 통해 WAF/API Gateway의 속도 제한 회피
- **인증 우회**: Geo-fencing, IP 기반 접근 제어 무력화 (예: 한국 IP만 허용하는 서비스에 해외 공격자가 국내 가정용 IP로 접근)

## 2. 실무 영향 분석

DevSecOps 관점에서 NetNut 중단은 **일시적 완화**일 뿐, 근본적인 위협은 지속됩니다.

| 영향 영역 | 구체적 내용 |
|-----------|------------|
| **CI/CD 파이프라인** | IP 기반 차단에 의존한 보안 정책이 무력화될 수 있음 |
| **API 보안** | 정상 사용자 트래픽과 악성 트래픽의 구분이 더욱 어려워짐 |
| **모니터링** | 기존 IP 평판 기반 탐지 로직의 신뢰도 하락 |

**핵심 교훈**: IP 기반 보안은 단기적 완화책일 뿐, 행동 기반 분석과 다층 보안 전략이 필수적입니다.

## 3. 대응 체크리스트

- [ ] **행동 기반 탐지 도입**: IP 신뢰도 외에도 요청 패턴(헤더, 타이밍, User-Agent 일관성)을 분석하는 WAF/API Gateway 규칙 추가
- [ ] **레이트 리밋 고도화**: 단순 IP 기반 속도 제한에서 사용자 세션, 디바이스 핑거프린트, 행동 시퀀스 기반 제한으로 전환
- [ ] **CI/CD 환경 보안 강화**: 파이프라인 내 IP 화이트리스트 의존도 낮추고, mTLS, OAuth2.0 등 인증 기반 접근 제어 적용
- [ ] **모니터링 대시보드 업데이트**: 비정상적인 IP 분포(예: 단일 세션에서 다양한 가정용 IP로 전환)를 탐지하는 이상 징후 알람 추가
- [ ] **레지덴셜 프록시 탐지 로직 주기적 리뷰**: GTIG의 분석 결과를 참고해 자체 탐지 규칙 업데이트 (분기별 1회 이상)

---

### 1.2 랜섬웨어 그룹, Citrix Bleed 2, BYOVD, 공급망 자격증명으로 전환

{% include news-card.html
  title="랜섬웨어 그룹, Citrix Bleed 2, BYOVD, 공급망 자격증명으로 전환"
  url="https://thehackernews.com/2026/07/ransomware-groups-turn-to-citrix-bleed.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh5gkjf1FwB4__nC6-pLZYnDv2rJA29UAL9mxfCv4BNSl1FxNpat9jD-OiMRLewjXJXyiSGvqiLYcewN_b1lLFHh0FhzKkrHFzu82jziSuOodYX87FkwjuCcXaqwzWRsiFdsBcd9mzDnak1rJpDu46F8TV206IEcD1pE7njojB8TcQEZ4Wa70KnK2vyeVKI/s1600/ransomwares.jpg"
  summary="Anubis 랜섬웨어 운영과 연계된 위협 행위자들이 초기 접근을 위해 Citrix Bleed 2 (CVE-2025-5777) 취약점을 악용하는 것이 관찰되었습니다. 이들은 정당한 RMM 도구와 자격 증명 접근을 사용하는 등 공통된 패턴을 보이며 측면 이동을 수행합니다."
  source="The Hacker News"
  severity="High"
%}

# DevSecOps 실무자 관점에서의 랜섬웨어 위협 분석

## 1. 기술적 배경 및 위협 분석

Anubis 랜섬웨어 운영 그룹이 **Citrix Bleed 2(CVE-2025-5777)** 취약점을 악용하여 초기 침투를 시도하고 있습니다. 이는 2023년에 유행했던 Citrix Bleed(CVE-2023-4966)의 변종으로, Citrix ADC/Gateway의 세션 쿠키 정보 유출 취약점을 통해 인증 우회 및 세션 하이재킹이 가능합니다.

주요 위협 벡터는 세 가지입니다:
- **Citrix Bleed 2**: 패치되지 않은 Citrix 장비를 통해 초기 접근권한 획득
- **BYOVD(Bring Your Own Vulnerable Driver)**: 합법적이지만 취약한 드라이버를 로드하여 커널 수준 권한 상승 및 EDR 우회
- **공급망 자격증명 탈취**: RMM(Remote Monitoring and Management) 도구의 자격증명을 탈취하여 정당한 관리 도구로 위장한 측면 이동

특히 **합법적 RMM 도구**를 악용하는 점이 위협적입니다. AnyDesk, TeamViewer, ScreenConnect 등이 악용되며, 이는 보안 솔루션에서 정상 트래픽으로 오인될 가능성이 높습니다.

## 2. 실무 영향 분석

DevSecOps 환경에서 이 위협은 다음과 같은 실무적 영향을 미칩니다:

- **CI/CD 파이프라인 위험**: Citrix ADC/Gateway가 인프라 게이트웨이로 사용될 경우, 파이프라인 인증 정보 유출 가능성
- **컨테이너 및 오케스트레이션 위험**: RMM 도구를 통한 측면 이동 시 Kubernetes 클러스터 접근 권한 탈취 가능
- **취약점 스캔 우회**: BYOVD 공격은 기존 취약점 스캐너로 탐지가 어려움
- **공급망 리스크**: 서드파티 RMM 도구와 자격증명 관리 방식에 대한 재검토 필요

## 3. 대응 체크리스트

- [ ] Citrix ADC/Gateway 대상 **긴급 패치 적용(CVE-2025-5777)** 및 모든 세션 쿠키 무효화 후 재인증 강제
- [ ] **RMM 도구 사용 현황 감사** 실시: 비승인 도구 차단, 허용된 도구에 대한 MFA 강제 및 네트워크 세그먼트 제한
- [ ] **Windows 드라이버 서명 정책 강화**: WDAC(Windows Defender Application Control) 또는 AppLocker를 통해 서명되지 않은 드라이버 로드 차단
- [ ] **공급망 자격증명 모니터링**: GitHub, Jenkins, Azure DevOps 등에 저장된 자격증명에 대한 시크릿 스캐닝 도구 도입 및 주기적 회전 정책 수립
- [ ] **이상 행동 탐지 규칙 업데이트**: RMM 도구를 통한 비정상적 원격 접속(야간 시간대, 비정상 IP 대역) 탐지 로직 추가

#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - T1203  # Exploitation for Client Execution
    - T1078  # Valid Accounts
```

---

### 1.3 Anthropic, Claude Fable 5가 구독에서 영구적으로 사라지는 것은 아니라고 밝혀

{% include news-card.html
  title="Anthropic, Claude Fable 5가 구독에서 영구적으로 사라지는 것은 아니라고 밝혀"
  url="https://www.bleepingcomputer.com/news/artificial-intelligence/claude-fable-5-isnt-permanently-leaving-subscriptions-anthropic-says/"
  image="https://www.bleepstatic.com/content/hl-images/2026/05/07/Claude_AI.png"
  summary="Anthropic은 Claude Fable 5가 7월 7일 이후 Claude 구독을 통해 접근할 수 없게 되지만, 이는 영구적인 변경이 아니며 사용량 기반 요금제 외부로 모델이 곧 돌아올 것이라고 밝혔습니다."
  source="BleepingComputer"
  severity="Medium"
%}

# DevSecOps 관점에서 본 Anthropic Claude Fable 5 구독 변경 분석

## 1. 기술적 배경 및 위협 분석

Anthropic이 Claude Fable 5 모델을 7월 7일 이후 구독형 요금제에서 제외한다는 발표는 AI 모델 접근성의 불안정성을 시사합니다. 이는 단순한 요금제 변경이 아니라, **모델 제공 방식의 전환**으로 해석됩니다. DevSecOps 실무자 입장에서 주목할 점은:

- **API 기반 접근으로의 이동**: 구독 제외는 사용량 기반(usage-based) API 모델로 전환을 암시하며, 이는 CI/CD 파이프라인 내 AI 모델 통합 방식에 직접적 영향을 미칩니다. 기존 구독 기반 자동화 스크립트는 갑작스러운 중단 위험에 노출됩니다.
- **보안 위협**: 모델 접근 방식 변경 시, API 키 재발급, 엔드포인트 변경, 레이트 리밋 조정 등으로 인해 **인증 체계 혼란**이 발생할 수 있습니다. 특히 기존 자동화된 보안 분석(코드 리뷰, 취약점 탐지) 파이프라인이 중단되면, 배포 주기 내 보안 검증 공백이 생깁니다.
- **공급망 위험**: Anthropic의 모델 제공 정책 변경은 AI 서비스 의존도가 높은 DevSecOps 환경에서 **서드파티 의존성 위험**을 재확인시킵니다. 모델이 일시적으로 제공되지 않을 경우, 대체 모델(예: Claude 3.5 Sonnet, GPT-4)로 전환해야 하는데, 이는 출력 일관성과 보안 검증 기준 차이를 초래합니다.

## 2. 실무 영향 분석

- **CI/CD 파이프라인 중단 위험**: Fable 5를 기반으로 한 자동화된 코드 리뷰, SAST/DAST 결과 분석, 보안 정책 검증 작업이 7월 7일 이후 중단될 수 있습니다. 특히 **릴리스 게이트**에 AI 검증 단계가 포함된 조직은 배포 지연 위험에 직면합니다.
- **규정 준수 이슈**: Fable 5의 출력을 보안 감사 증적으로 사용하는 경우, 모델 변경으로 인해 **감사 추적의 일관성**이 깨질 수 있습니다. 예: 변경 전후 모델의 취약점 분류 기준 차이.
- **비용 구조 변화**: 사용량 기반 API로 전환 시, 대규모 CI/CD 실행(예: 야간 빌드)에서 예상치 못한 **비용 급증**이 발생할 수 있습니다. 기존 구독 고정 비용에서 변동 비용으로 전환되므로 예산 계획 재수립이 필요합니다.

## 3. 대응 체크리스트

- [ ] **API 전환 계획 수립**: 7월 7일 이전에 Fable 5 구독 기반 자동화 스크립트를 Anthropic API v2 엔드포인트로 마이그레이션하고, API 키 재발급 및 레이트 리밋 테스트 완료
- [ ] **대체 모델 페일오버 구성**: Claude 3.5 Sonnet 또는 GPT-4o로 자동 전환되는 페일오버 로직을 CI/CD 파이프라인에 구현하고, 출력 결과의 보안 정책 일치율(예: CWE 매핑 정확도)을 사전 검증
- [ ] **비용 모니터링 및 알림 설정**: 사용량 기반 API로 전환 후, 실행 건수당 비용 임계치(예: 월 $500) 초과 시 Slack/PagerDuty 알림 발송 및 자동 중단 트리거 설정
- [ ] **감사 로그 호환성 검증**: Fable 5 이전/이후 모델의 보안 분석 결과를 비교하여, 감사 증적으로 사용할 때 차이점(예: false positive 비율 변화)을 문서화하고 규정 준수 담당자와 공유

---

## 2. AI/ML 뉴스

### 2.1 GeForce NOW에 12개의 게임이 추가되는 7월, 즐거운 질주를 시작하세요

{% include news-card.html
  title="GeForce NOW에 12개의 게임이 추가되는 7월, 즐거운 질주를 시작하세요"
  url="https://blogs.nvidia.com/blog/geforce-now-thursday-july-2026-games-list/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/07/gfn-thursday-7-2-blog-2048x1024-no-copy-logo-842x450.jpg"
  summary="GeForce NOW가 7월에 12개의 신규 게임을 클라우드에 추가하며, Monopoly: Star Wars Heroes vs. Villains로 여름 시즌을 시작한다. 이번 업데이트로 인기 보드게임 프랜차이즈에 스타워즈 세계관이 결합된다. 또한 가장 큰 GeForce 관련 소식을 놓치지 말아야 한다."
  source="NVIDIA AI Blog"
  severity="High"
%}

#### 요약

GeForce NOW가 7월에 12개의 신규 게임을 클라우드에 추가하며, Monopoly: Star Wars Heroes vs. Villains로 여름 시즌을 시작한다. 이번 업데이트로 인기 보드게임 프랜차이즈에 스타워즈 세계관이 결합된다. 또한 가장 큰 GeForce 관련 소식을 놓치지 말아야 한다.

---

### 2.2 NVIDIA, AI 컴퓨팅을 대규모로 개방하며 파트너 초청해 AI 인프라 구축 지원

{% include news-card.html
  title="NVIDIA, AI 컴퓨팅을 대규모로 개방하며 파트너 초청해 AI 인프라 구축 지원"
  url="https://blogs.nvidia.com/blog/nvidia-unlocks-ai-compute-at-scale-capital-partners-to-power-ai-infrastructure-buildout/"
  image="https://blogs.nvidia.com/wp-content/uploads/2025/03/nvendeavor-1-842x450.jpg"
  summary="NVIDIA는 AI 모델 개발에서 프로덕션 추론으로의 전환에 따라 확장 가능한 AI 컴퓨팅을 제공하며, 대규모 멀티테넌트 가속 컴퓨팅 인프라 구축을 위해 파트너를 초대하고 있습니다. 이는 지속적으로 운영되는 AI 팩토리에서 토큰을 대규모로 생성하는 수요를 충족하기 위한 것입니다."
  source="NVIDIA AI Blog"
  severity="Medium"
%}

#### 요약

NVIDIA는 AI 모델 개발에서 프로덕션 추론으로의 전환에 따라 확장 가능한 AI 컴퓨팅을 제공하며, 대규모 멀티테넌트 가속 컴퓨팅 인프라 구축을 위해 파트너를 초대하고 있습니다. 이는 지속적으로 운영되는 AI 팩토리에서 토큰을 대규모로 생성하는 수요를 충족하기 위한 것입니다.

---

### 2.3 OpenAI, 트럼프 협상 속 미국 정부 지분 5% 검토 중: FT

{% include news-card.html
  title="OpenAI, 트럼프 협상 속 미국 정부 지분 5% 검토 중: FT"
  url="https://cointelegraph.com/news/openai-5-percent-stake-us-government-trump-talks?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://s3-images.ctmedia.io/media/article-covers/video-altman.jpg"
  summary="OpenAI가 트럼프 행정부 초기 회담에서 미국 정부에 5%의 지분을 제공하는 방안을 논의한 것으로 알려졌으며, 이는 워싱턴이 AI 모델 감독을 강화하는 가운데 나온 것이다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

OpenAI가 트럼프 행정부 초기 회담에서 미국 정부에 5%의 지분을 제공하는 방안을 논의한 것으로 알려졌으며, 이는 워싱턴이 AI 모델 감독을 강화하는 가운데 나온 것이다.

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Google의 악성 가정용 프록시 네트워크에 대한 지속적인 방해

{% include news-card.html
  title="Google의 악성 가정용 프록시 네트워크에 대한 지속적인 방해"
  url="https://cloud.google.com/blog/topics/threat-intelligence/google-continued-disruption-residential-proxy-networks/"
  summary="Google은 FBI, Lumen 등과 협력하여 NetNut(Popa) residential proxy network에 대한 조치를 취했으며, 이는 2026년 1월의 IPIDEA proxy network 방해 공작에 이어 악성 residential proxy network를 해체하려는 Google의 지속적인 노력의 일환입니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google은 FBI, Lumen 등과 협력하여 NetNut(Popa) residential proxy network에 대한 조치를 취했으며, 이는 2026년 1월의 IPIDEA proxy network 방해 공작에 이어 악성 residential proxy network를 해체하려는 Google의 지속적인 노력의 일환입니다.

---

## 4. DevOps & 개발 뉴스

### 4.1 Copilot 사용 메트릭 보고서의 정확성과 적용 범위 개선

{% include news-card.html
  title="Copilot 사용 메트릭 보고서의 정확성과 적용 범위 개선"
  url="https://github.blog/changelog/2026-07-02-improved-accuracy-and-coverage-in-copilot-usage-metrics-reports"
  summary="GitHub이 Copilot 사용량 메트릭 API에 세 가지 개선 사항을 적용하여 보고서의 완전성과 정확성을 높였으며, 이제 GitHub Copilot CLI가 제안된 코드 라인을 보고하고 이전에 누락되던 사용자 데이터도 포함됩니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub이 Copilot 사용량 메트릭 API에 세 가지 개선 사항을 적용하여 보고서의 완전성과 정확성을 높였으며, 이제 GitHub Copilot CLI가 제안된 코드 라인을 보고하고 이전에 누락되던 사용자 데이터도 포함됩니다.

---

### 4.2 예정된 Gemini 2.5 Pro 및 Gemini 3 Flash 지원 중단

{% include news-card.html
  title="예정된 Gemini 2.5 Pro 및 Gemini 3 Flash 지원 중단"
  url="https://github.blog/changelog/2026-07-02-upcoming-deprecation-of-gemini-2-5-pro-and-gemini-3-flash"
  image="https://github.blog/wp-content/uploads/2026/07/Gemini-models-deprecation-social.jpg"
  summary="GitHub Copilot에서 사용 중이던 Gemini 2.5 Pro와 Gemini 3 Flash 모델이 7월 31일자로 모든 기능에서 지원이 중단됩니다. 이는 Copilot Chat, 인라인 편집, ask 및 agent 모드, 코드 완성 등 모든 환경에 적용됩니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot에서 사용 중이던 Gemini 2.5 Pro와 Gemini 3 Flash 모델이 7월 31일자로 모든 기능에서 지원이 중단됩니다. 이는 Copilot Chat, 인라인 편집, ask 및 agent 모드, 코드 완성 등 모든 환경에 적용됩니다.

---

### 4.3 GitHub Actions에서 Copilot CLI에 더 이상 개인 액세스 토큰이 필요하지 않습니다

{% include news-card.html
  title="GitHub Actions에서 Copilot CLI에 더 이상 개인 액세스 토큰이 필요하지 않습니다"
  url="https://github.blog/changelog/2026-07-02-copilot-cli-no-longer-needs-a-personal-access-token-in-github-actions"
  summary="GitHub Actions에서 Copilot CLI를 사용할 때 더 이상 개인 액세스 토큰(PAT)이 필요하지 않으며, 내장된 GITHUB_TOKEN을 활용할 수 있게 되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Actions에서 Copilot CLI를 사용할 때 더 이상 개인 액세스 토큰(PAT)이 필요하지 않으며, 내장된 GITHUB_TOKEN을 활용할 수 있게 되었습니다.

---

## 5. 블록체인 뉴스

### 5.1 Wavespace, Lightning 및 NWC 기반 MiCA 규정 준수 자체 보관 비트코인 직불카드 출시

{% include news-card.html
  title="Wavespace, Lightning 및 NWC 기반 MiCA 규정 준수 자체 보관 비트코인 직불카드 출시"
  url="https://bitcoinmagazine.com/business/wavespace-launches-mica-compliant-self-custodial-bitcoin-debit-card-powered-by-lightning-and-nwc"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/tn.webp"
  summary="Wavespace가 MiCA 규정을 준수하는 비트코인 전용 네오뱅크로, 자체 보관형 wavecard®를 출시했습니다. 이 카드는 Nostr Wallet Connect를 통해 사용자의 Lightning 노드에서 자동으로 잔액을 충전하여, 보관형 선불 충전의 위험을 제거합니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Wavespace가 MiCA 규정을 준수하는 비트코인 전용 네오뱅크로, 자체 보관형 wavecard®를 출시했습니다. 이 카드는 Nostr Wallet Connect를 통해 사용자의 Lightning 노드에서 자동으로 잔액을 충전하여, 보관형 선불 충전의 위험을 제거합니다.

---

### 5.2 Bitget, U.S. Stock Options Trading으로 Stock+ 플랫폼 강화

{% include news-card.html
  title="Bitget, U.S. Stock Options Trading으로 Stock+ 플랫폼 강화"
  url="https://bitcoinmagazine.com/news/bitget-bolsters-stock-options-trading"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/Bitget-Bolsters-Stock-Platform-With-U.S.-Stock-Options-Trading.jpg"
  summary="Bitget이 Stock+ 플랫폼에 미국 주식 옵션 거래를 추가하며 long call과 put 옵션을 도입했습니다. 이는 암호화폐와 전통 금융 시장을 하나의 거래 플랫폼에 결합하려는 전략의 일환입니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Bitget이 Stock+ 플랫폼에 미국 주식 옵션 거래를 추가하며 long call과 put 옵션을 도입했습니다. 이는 암호화폐와 전통 금융 시장을 하나의 거래 플랫폼에 결합하려는 전략의 일환입니다.

---

### 5.3 FBI 국장 Kash Patel, 6자리 규모의 Strategy(MSTR) 지분 공시하지 않아: 보도

{% include news-card.html
  title="FBI 국장 Kash Patel, 6자리 규모의 Strategy(MSTR) 지분 공시하지 않아: 보도"
  url="https://bitcoinmagazine.com/news/fbi-director-kash-patel-did-not-disclose"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/07/FBI-Director-Kash-Patel-Did-Not-Disclose-Six-Figure-Strategy-MSTR-Stake-Report.jpg"
  summary="FBI 국장 Kash Patel이 Strategy(MSTR)에 대한 6자리 규모의 지분 투자를 적시에 공개하지 않았다는 보도가 나왔으며, 이는 윤리 규정 준수에 대한 논란을 다시 불러일으켰습니다. 해당 소식은 Bitcoin Magazine이 Micah Zimmerman의 기사를 인용해 처음 보도했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

FBI 국장 Kash Patel이 Strategy(MSTR)에 대한 6자리 규모의 지분 투자를 적시에 공개하지 않았다는 보도가 나왔으며, 이는 윤리 규정 준수에 대한 논란을 다시 불러일으켰습니다. 해당 소식은 Bitcoin Magazine이 Micah Zimmerman의 기사를 인용해 처음 보도했습니다.

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [World Monitor - 실시간 글로벌 인텔리전스 대시보드](https://tech.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.00&view=global&timeRange=7d&layers=cables%2Cweather%2Ceconomic%2Coutages%2Cdatacenters%2Cnatural%2CstartupHubs%2CcloudRegions%2CtechHQs%2CtechEvents) | Tech World Monitor | Tech World Monitor 글로벌 대시보드 기반 기술 동향 요약입니다. Real-time global intelligence dashboard with live news, markets, military tracking, infrastructure monitoring, and geopolitical data |
| [AI로 웹 엔지니어 없이 LINE 앱 안에서 그룹 영상 통화 서비스 만들기](https://techblog.lycorp.co.jp/ko/building-group-video-calls-inside-line-app-with-ai-and-line-planet) | LINE Engineering | 들어가며LINE Developers를 통해 이용할 수 있는 LIFF(LINE Front-end Framework)를 활용하면, LINE 앱 사용자를 대상으로 나만의 서비스 공간을 |
| [버지니아주, 위치정보 데이터 판매 금지](https://news.hada.io/topic?id=31077) | GeekNews (긱뉴스) | 버지니아주는 VCDPA 개정 으로 위치정보 데이터 판매를 금지해, 주 단위 개인정보보호법에서 위치 데이터 거래 제한을 강화함 이번 개정은 S.B. 388 서명으로 확정됐으며, 금지는 2026년 7월 1일부터 적용됨 VCDPA의 판매(sale) 정의는 개 |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 10건 | 기타 주제 |
| **AI/ML** | 4건 | The Hacker News 관련 동향, NVIDIA AI Blog 관련 동향, AWS Machine Learning Blog 관련 동향 |
| **랜섬웨어** | 2건 | The Hacker News 관련 동향 |
| **공급망 보안** | 1건 | The Hacker News 관련 동향 |
| **인증 보안** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(10건)입니다. **AI/ML** 분야에서는 The Hacker News 관련 동향, NVIDIA AI Blog 관련 동향 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Google, 200만 가정용 기기에 걸친 NetNut 리지덴셜 프록시 네트워크를 교란** 관련 보안 영향도 분석 및 모니터링 강화

### P1 (7일 내)

- [ ] **랜섬웨어 그룹, Citrix Bleed 2, BYOVD, 공급망 자격증명으로 전환** (CVE-2025-5777) 관련 보안 검토 및 모니터링
- [ ] **GeForce NOW에 12개의 게임이 추가되는 7월, 즐거운 질주를 시작하세요** 관련 보안 검토 및 모니터링
- [ ] **Amazon Bedrock이 AI 생성 피싱을 탐지하는 방법** 관련 보안 검토 및 모니터링
- [ ] **Amazon SageMaker AI에서 멀티턴 강화 학습을 위한 모범 사례** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **GeForce NOW에 12개의 게임이 추가되는 7월, 즐거운 질주를 시작하세요** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
