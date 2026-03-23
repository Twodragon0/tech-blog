---

layout: post
title: "Gemini 3.1 Pro 출시, AI 공급망 공격, Kubernetes 보안 강화"
date: 2026-02-20 09:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Gemini, AI, Supply-Chain, Kubernetes]
excerpt: "Gemini 3.1 Pro 출시, AI 공급망 공격 신규 벡터, Kubernetes Ingress NGINX 은퇴 이슈를 중심으로 기술 관점(공격 경로·영향 자산·탐지 포인트)과 경영진 관점(서비스 영향·우선순위·의사결정 체크리스트)을 함께 정리한 2026년 2월 20일 주간 보안 다이제스트입니다."
description: "2026년 02월 20일 보안 뉴스: The Hacker News, Google Cloud, Snyk 등 29건. Gemini 3.1 Pro, AI 공급망 공격, Kubernetes Ingress NGINX 은퇴 관련 DevSecOps 실무 위협 분석 및 대응 가이드."
author: Twodragon
comments: true
image: /assets/images/2026-02-20-Tech_Security_Weekly_Digest_Gemini_AI_Supply_Chain_Kubernetes.svg
image_alt: "기술 보안 주간 다이제스트 2026년 2월 20일 Gemini AI 공급망 Kubernetes"
toc: true
---
{% include ai-summary-card.html
  title='Gemini 3.1 Pro 출시, AI 공급망 공격, Kubernetes 보안 강화'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">Security-Weekly</span> <span class="tag">DevSecOps</span> <span class="tag">Cloud-Security</span> <span class="tag">Weekly-Digest</span> <span class="tag">2026</span> <span class="tag">Gemini</span> <span class="tag">AI</span> <span class="tag">Supply-Chain</span>'
  highlights_html='<li><strong>포인트 1</strong>: 2026년 02월 20일 보안 뉴스: The Hacker News, Google Cloud, Snyk 등 29건. Gemini 3.1 Pro, AI 공급망 공격, Kubernetes Ingress NGINX 은퇴 관</li> <li><strong>포인트 2</strong>: 실무 관점에서 영향 범위와 우선순위를 함께 점검해야 합니다</li> <li><strong>포인트 3</strong>: 운영 절차와 검증 기준을 문서화해 재현 가능한 적용 체계를 유지해야 합니다</li>'
  period='2026-02-20 (24시간)'
  audience='보안/클라우드/플랫폼 엔지니어 및 기술 의사결정자'
%}

## Executive Summary

> **경영진 브리핑**: 2026년 02월 20일 보안 뉴스: The Hacker News, Google Cloud, Snyk 등 29건. Gemini 3.1 Pro, AI 공급망 공격, Kubernetes Ingress NGINX 은퇴 관련 DevSecOps 실무 위협 분석 및 대응 가이드.

### 위험도 평가

| 항목 | 위험도 | 설명 |
|------|--------|------|
| 전체 위험도 | 🟡 중간 | 주요 보안 위협 모니터링 및 패치 적용 필요 |

---

## 서론

안녕하세요, Twodragon입니다.

2026년 02월 20일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

수집 통계:
- 총 뉴스 수: 30개
- 보안 뉴스: 7개
- AI/ML 뉴스: 4개
- 클라우드 뉴스: 5개
- DevOps 뉴스: 4개
- 블록체인 뉴스: 5개

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 Security | The Hacker News | PromptSpy 안드로이드 악성코드, Gemini AI 악용 최초 사례 | 🔴 Critical |
| 🔒 DevSecOps | Snyk | Clinejection - AI 봇을 공급망 공격 벡터로 전환 | 🔴 Critical |
| 🔒 Security | Datadog Security Labs | Kubernetes Ingress NGINX 은퇴 경고, 고위험 CVE 공개 | 🟠 High |
| 🔒 Security | The Hacker News | Microsoft CVE-2026-26119 Windows Admin Center 권한상승 | 🟠 High |
| ☁️ Cloud | Google Cloud | Gemini 3.1 Pro 출시, 이전 대비 2배 추론 성능 | 🟡 Medium |

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. 보안 뉴스

### 1.1 PromptSpy 안드로이드 악성코드, Gemini AI를 악용해 최근 앱 지속성 자동화

{%- include news-card.html
  title="[보안] PromptSpy 안드로이드 악성코드, Gemini AI를 악용해 최근 앱 지속성 자동화"
  url="https://thehackernews.com/2026/02/promptspy-android-malware-abuses-google.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEidDhkNjYF9Khe4u-ECtSVv3ezo7dUK80WV06lgCNtOdV51GuCKCMmxgdm10lbAhP7MRPVY7Pq5yMuiYPAJ0Opk2xPijnkjHOWfPqiD9oR6k56GqDX6l5IgjYa_9ZTnvxvN6KnazUB0LBZ3aZMOnVrtoodDr-Hx_JTTNjMyzm-u1alcCL6VXeqoeTl12jFE/s1700-e365/android-ai.jpg"
  summary="PromptSpy 안드로이드 악성코드, Gemini AI를 악용해 최근 앱 지속성 자동화 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="The Hacker News"
  severity="High"
-%}


Google Gemini AI를 런타임에 악용하는 최초의 안드로이드 악성코드가 발견됐습니다. VNC 원격 접근과 PIN 가로채기 기능을 탑재하고 Chase Bank 피싱 페이지로 위장 배포되어, AI 서비스가 새로운 공격 표면으로 전용되는 실제 사례를 보여줍니다.


#### 핵심 포인트

- Google Gemini AI를 런타임에 악용하는 최초의 안드로이드 악성코드
- VNC 모듈로 피해자 기기에 원격 접근 및 실시간 화면 제어 가능
- 잠금화면 PIN/비밀번호 가로채기, 패턴 잠금을 영상으로 캡처
- 특정 화면 영역에 투명 사각형 오버레이로 삭제 차단
- 아르헨티나 대상, Chase Bank를 사칭한 스페인어 피싱 페이지로 배포

#### 위협 분석

| 항목 | 내용 |
|------|------|
| CVE ID | 미공개 |
| 심각도 | Critical |
| C2 서버 | 54.67.2[.]84 (Amazon 호스팅, VNC/AES 암호화) |
| 배포 도메인 | mgardownload[.]com |
| MITRE ATT&CK | T1437 (Application Layer Protocol), T1516 (Input Injection) |

#### 권장 조치

- [ ] Google Play Protect 활성화 상태 확인 (알려진 샘플 자동 차단)
- [ ] 기업 MDM에서 사이드로딩 앱 설치 차단 정책 점검
- [ ] SIEM에 C2 IP(54.67.2[.]84) 및 배포 도메인 IOC 추가
- [ ] 안전 모드 재부팅을 통한 감염 기기 MorganArg 앱 삭제 절차 수립
- [ ] AI 서비스 API 호출 패턴의 비정상 사용 모니터링 검토

---

### 1.2 INTERPOL Operation Red Card 2.0, 아프리카 사이버범죄 단속으로 651명 체포

{%- include news-card.html
  title="[보안] INTERPOL Operation Red Card 2.0, 아프리카 사이버범죄 단속으로 651명 체포"
  url="https://thehackernews.com/2026/02/interpol-operation-red-card-20-arrests.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhltf-8sYx4UcRPT_qBv92hmitOenRSgB2OctxYx4hdCPglcMJzeHR8Dmffrt5xjjtp0Tz2ur0wPSbvig7cnEyrdtJrOx8V4Z2sTGeR6eBlFwOO4pgPUISeLWGuMbUO4bnruvRWx-O6zYRUy_xw1F1CohPk2fZDkpM1YGXusO-8h8rgwQhLvZSlfp4ho5RJ/s1700-e365/interpol.jpg"
  summary="INTERPOL Operation Red Card 2.0, 아프리카 사이버범죄 단속으로 651명 체포 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="The Hacker News"
  severity="Medium"
-%}


INTERPOL이 주도한 국제 공조 작전으로 아프리카 전역에서 사이버 범죄자 651명을 일제 검거하고 430만 달러 이상을 회수했습니다. 모바일 뱅킹 사기와 투자 사기가 주요 표적이었으며, 국경을 초월한 사이버 범죄 단속의 실효성을 보여주는 사례입니다.


#### 핵심 포인트

- INTERPOL 주도 Operation Red Card 2.0으로 651명 체포, 430만 달러 이상 회수
- 모바일 뱅킹 사기, 투자 사기, 메시징 앱 사기 대상 집중 단속
- 아프리카 전역 법 집행 기관 공조 작전

#### 권장 조치

- 아프리카 지역 거래 모니터링 강화 필요
- 모바일 뱅킹 사기 패턴에 대한 탐지 룰 업데이트
- 국제 공조 작전 동향 파악 및 보안 정책 반영

---

### 1.3 Microsoft, Windows Admin Center 권한 상승 취약점 CVE-2026-26119 패치 발표

{%- include news-card.html
  title="[보안] Microsoft, Windows Admin Center 권한 상승 취약점 CVE-2026-26119 패치 발표"
  url="https://thehackernews.com/2026/02/microsoft-patches-cve-2026-26119.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiTYrWKU78qUjsLRxRje4c7MEejHM-e4bg7D2mFbFEomGbCI39Um78JNkCJKcjrcH2FYinO-dVUiV0_rB60jmErrc4lyMkYOK-qIX3HnYCFJ8aWfFwcnaZOHe_38JSgbLPnVqWrQaXhvbXmMCAaJpb6qnANjxjsqB3S4NM89kemycwHA8kDGlwrS-306oP8/s1700-e365/windows-admin.jpg"
  summary="Microsoft, Windows Admin Center 권한 상승 취약점 CVE-2026-26119 패치 발표 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="The Hacker News"
  severity="High"
-%}


Microsoft가 Windows Admin Center의 권한 상승 취약점 CVE-2026-26119에 대한 패치를 발표했습니다. 관리 콘솔 접근 권한이 있는 공격자가 시스템 수준 권한을 획득할 수 있는 결함으로, 즉시 패치 적용이 필요합니다.


#### 핵심 포인트

- Windows Admin Center에서 권한 상승 취약점 발견 및 패치 완료
- 낮은 권한 사용자가 관리자 수준 접근 가능한 심각한 결함
- Microsoft의 정기 보안 업데이트를 통해 패치 배포

#### 위협 분석

| 항목 | 내용 |
|------|------|
| CVE ID | CVE-2026-26119 |
| 심각도 | High |
| 대응 우선순위 | P1 - 7일 이내 패치 적용 권장 |

#### 권장 조치

- [ ] Windows Admin Center 사용 현황 인벤토리 확인
- [ ] CVE-2026-26119 패치 즉시 적용
- [ ] Admin Center 접근 로그에서 비정상 권한 상승 시도 확인
- [ ] 네트워크 세그멘테이션을 통한 Admin Center 접근 제한 검토

---

### 1.4 가짜 IPTV 앱, 모바일 뱅킹 사용자 대상 Massiv 안드로이드 악성코드 유포

{%- include news-card.html
  title="[보안] 가짜 IPTV 앱, 모바일 뱅킹 사용자 대상 Massiv 안드로이드 악성코드 유포"
  url="https://thehackernews.com/2026/02/fake-iptv-apps-spread-massiv-android.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj67LPvqhfl_NCfP1wUAUN8p7ISQ_x3wCwavSYjJJkMl9jkcDnk0gP2Om7d1O0UqaQnwqeU4GzTfpLxUok2ei5tiNhArCqldBzaS6yzNe_mudDAbzllZcD1BA0FOfbn1LQRSiK36eB69u4hfK_Pa0XA0eZti_KN8Q43d_k1xRmp_LQCW6gA9ZWNvdrBx_py/s1700-e365/android-banking.jpg"
  summary="가짜 IPTV 앱, 모바일 뱅킹 사용자 대상 Massiv 안드로이드 악성코드 유포 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="The Hacker News"
  severity="High"
-%}


합법적인 IPTV 앱으로 위장한 'Massiv' 트로이 목마가 모바일 뱅킹 사용자를 직접 표적으로 삼아 기기 탈취(Device Take Over) 공격을 수행하고 있습니다. 공식 마켓 외부의 IPTV 앱 설치가 주요 감염 경로로, MDM 정책 강화가 핵심 대응 수단입니다.


#### 핵심 포인트

- 'Massiv' 안드로이드 트로이 목마가 가짜 IPTV 앱으로 위장 배포
- 기기 탈취(Device Take Over) 공격으로 모바일 뱅킹 직접 표적
- 합법적인 IPTV 앱 마켓플레이스를 통한 배포 경로 활용

#### 권장 조치

- [ ] MDM을 통한 비공식 앱 스토어 접근 차단 정책 적용
- [ ] 모바일 뱅킹 앱의 기기 무결성 검증 기능 활성화
- [ ] IPTV 관련 사이드로드 앱 설치 현황 감사
- [ ] 모바일 위협 탐지(MTD) 솔루션 도입 검토

---

### 1.5 CRESCENTHARVEST 캠페인, RAT 악성코드로 이란 시위 지지자 표적 공격

{%- include news-card.html
  title="[보안] CRESCENTHARVEST 캠페인, RAT 악성코드로 이란 시위 지지자 표적 공격"
  url="https://thehackernews.com/2026/02/crescentharvest-campaign-targets-iran.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEiFD_PtNViVDHZuayLVtVYwd7N2scLLqDjTvVq8WGWrnvOCZ7tt92yiynt44EBuHUv2Y4b-sujz_BlBBx2Vl9af8ZzAXzTJH2UzFpsqC5KyxWWvB6FD-Ini78yxU9MsffuVeYsU2wQQCP5mTPs7xlI73PBSZ3RYj1RUMbjxfH06NhmoNjHkpapxBNwyEMrI/s1700-e365/protest.jpg"
  summary="CRESCENTHARVEST 캠페인, RAT 악성코드로 이란 시위 지지자 표적 공격 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="The Hacker News"
  severity="High"
-%}


국가 후원 위협 행위자로 추정되는 그룹이 이란 시위 지지자를 표적으로 RAT 악성코드를 배포하는 사이버 스파이 캠페인을 전개하고 있습니다. 정치적·지정학적 리스크가 높은 지역과 연관된 네트워크 트래픽에 대한 추가 모니터링이 필요합니다.


#### 핵심 포인트

- 이란 시위 지지자를 표적으로 한 새로운 사이버 스파이 캠페인
- RAT 악성코드를 통한 감시 및 데이터 수집
- 국가 후원 위협 행위자의 활동으로 추정

#### 권장 조치

- 지정학적 위험이 높은 지역 관련 네트워크 트래픽 모니터링
- RAT 악성코드 관련 IOC 업데이트 및 탐지 룰 적용

---

## 2. DevSecOps 뉴스

### 2.1 "Clinejection": AI 봇을 공급망 공격 벡터로 전환한 방법

{%- include news-card.html
  title="&quot;Clinejection&quot;: AI 봇을 공급망 공격 벡터로 전환한 방법"
  url="https://snyk.io/blog/cline-supply-chain-attack-prompt-injection-github-actions/"
  image="https://res.cloudinary.com/snyk/image/upload/v1646599410/wordpress-sync/blog-feature-security-alert-purple.jpg"
  summary="&quot;Clinejection&quot;: AI 봇을 공급망 공격 벡터로 전환한 방법 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Snyk Blog"
  severity="High"
-%}


Snyk 연구팀이 AI 코딩 에이전트 Cline을 프롬프트 인젝션으로 조작해 GitHub Actions 캐시 포이즈닝과 결합한 공급망 공격을 시연했습니다. AI 에이전트가 자동으로 코드를 실행하는 환경에서 기존 보안 모델로는 탐지하기 어려운 새로운 공격 표면이 열렸다는 점이 핵심입니다.


#### 핵심 포인트

- AI 코딩 에이전트(Cline)를 프롬프트 인젝션으로 공급망 공격 벡터로 전환
- GitHub Actions 캐시 포이즈닝과 결합한 복합 공격 체인
- npm 패키지 무결성을 우회하는 새로운 공격 경로 발견
- AI 에이전트의 자동화된 코드 실행이 공격 표면 확대

#### 위협 분석

| 항목 | 내용 |
|------|------|
| 공격 유형 | Supply Chain Attack via AI Agent |
| MITRE ATT&CK | T1195.002 (Supply Chain Compromise: Software Supply Chain) |
| 영향 범위 | AI 코딩 에이전트 사용 조직 전체 |

#### 권장 조치

- [ ] AI 코딩 에이전트의 실행 권한 최소화 및 샌드박스 적용
- [ ] GitHub Actions 캐시 무결성 검증 메커니즘 도입
- [ ] npm/yarn lock 파일 변경에 대한 코드 리뷰 강화
- [ ] AI 에이전트가 실행하는 코드에 대한 정적 분석 파이프라인 구축
- [ ] 프롬프트 인젝션 방어를 위한 입력 검증 레이어 추가

---

### 2.2 Kubernetes 프로젝트, Ingress NGINX 은퇴 경고 발표

{%- include news-card.html
  title="Kubernetes 프로젝트, Ingress NGINX 은퇴 경고 발표"
  url="https://securitylabs.datadoghq.com/articles/kubernetes-ingress-nginx-retirement-warning/"
  summary="Kubernetes 프로젝트, Ingress NGINX 은퇴 경고 발표 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Datadog Security Labs"
  severity="High"
-%}


Kubernetes 커뮤니티가 2026년 3월 이후 Ingress NGINX 공식 지원을 종료한다고 공식 발표했습니다. 클라우드 네이티브 환경의 약 50%에서 사용 중인 만큼 영향 범위가 크고, 최근 고위험 CVE 4건도 함께 공개되어 지금 당장 마이그레이션 계획을 수립해야 합니다.


#### 핵심 포인트

- 2026년 3월 이후 Ingress NGINX 공식 지원 완전 종료
- 클라우드 네이티브 환경의 약 50%가 Ingress NGINX 사용 중
- 최근 4개 고위험 CVE 공개 (CVE-2026-1580, 24512, 24513, 24514)
- Gateway API 기반 컨트롤러로의 마이그레이션 권장

#### 마이그레이션 체크리스트

| 단계 | 작업 | 우선순위 |
|------|------|---------|
| 1 | 영향받는 배포 식별: `kubectl get pods --all-namespaces --selector app.kubernetes.io/name=ingress-nginx` | 즉시 |
| 2 | Gateway API 호환 컨트롤러 평가 (Envoy Gateway, Istio 등) | 1주 내 |
| 3 | 마이그레이션 계획 수립 및 테스트 환경 검증 | 2주 내 |
| 4 | 프로덕션 마이그레이션 실행 | 3월 전 |

#### 권장 조치

- [ ] Ingress NGINX 사용 현황 전수 조사 실행
- [ ] 최신 고위험 CVE 4종 패치 즉시 적용
- [ ] Gateway API 기반 대안 컨트롤러 PoC 시작
- [ ] 마이그레이션 타임라인 수립 (3월 은퇴 전 완료 목표)

---

![AI ML News Section Banner](/assets/images/section-ai-ml.svg)

## 3. AI/ML 뉴스

### 3.1 Google Cloud에서 Gemini 3.1 Pro 출시

{%- include news-card.html
  title="[AI/ML] Google Cloud에서 Gemini 3.1 Pro 출시"
  url="https://cloud.google.com/blog/products/ai-machine-learning/gemini-3-1-pro-on-gemini-cli-gemini-enterprise-and-vertex-ai/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/gemini-3.1_pro_meta_dark.max-2000x2000.png"
  summary="Google Cloud에서 Gemini 3.1 Pro 출시 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Google Cloud Blog"
  severity="Medium"
-%}


Google Cloud가 ARC-AGI-2 벤치마크에서 77.1%를 기록한 Gemini 3.1 Pro를 공식 출시했습니다. 이전 세대 대비 2배 이상의 추론 성능을 제공하며, Gemini CLI와 Vertex AI에서 즉시 사용 가능해 기업 AI 워크플로우에 바로 적용할 수 있습니다.


#### 핵심 포인트

- ARC-AGI-2 벤치마크에서 77.1% 달성, 이전 대비 2배 이상 추론 성능 향상
- 데이터 통합, 복잡한 분석, 멀티모달 처리 능력 강화
- Gemini CLI, Gemini Enterprise, Vertex AI에서 즉시 사용 가능
- 기업 AI 애플리케이션의 핵심 추론 엔진으로 포지셔닝

#### 실무 적용

- 기존 Gemini 기반 워크플로우의 성능 벤치마크 비교 검토
- Vertex AI Provisioned Throughput를 통한 안정적 성능 확보 계획
- 멀티모달 입력 처리가 필요한 유스케이스 파일럿 프로젝트 시작

---

### 3.2 AI 정렬 독립 연구 지원 확대

{%- include news-card.html
  title="[AI/ML] AI 정렬 독립 연구 지원 확대"
  url="https://openai.com/index/advancing-independent-research-ai-alignment"
  summary="AI 정렬 독립 연구 지원 확대 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="OpenAI Blog"
  severity="Medium"
-%}


OpenAI가 독립적인 AI 정렬 연구 기관인 The Alignment Project에 750만 달러를 투자하겠다고 발표했습니다. AGI 안전성 확보를 위해 외부 연구 생태계를 직접 지원하는 움직임으로, 기업 AI 거버넌스 정책에도 정렬 검증 단계를 포함하는 흐름이 가속화될 전망입니다.


#### 핵심 포인트

- OpenAI, The Alignment Project에 750만 달러 투자 약속
- 독립적 AI 정렬 연구 기금 조성으로 AGI 안전성 강화
- 글로벌 AI 안전 연구 생태계 확대 목표

#### AI/ML 보안 영향 분석

- 모델 보안: AI 정렬 연구의 실무적 보안 시사점 검토 필요
- 거버넌스: AI 모델 배포 전 정렬 평가 체크리스트 확인
- 정책: 기업 AI 거버넌스 프레임워크에 정렬 검증 단계 포함 검토

---

### 3.3 Union.ai와 Flyte로 Amazon EKS에서 AI 워크플로우 구축

{%- include news-card.html
  title="[AI/ML] Union.ai와 Flyte로 Amazon EKS에서 AI 워크플로우 구축"
  url="https://aws.amazon.com/blogs/machine-learning/build-ai-workflows-on-amazon-eks-with-union-ai-and-flyte/"
  image="https://d2908q01vomqb2.cloudfront.net/f1f836cb4ea6efb2a0b1b99f41ad8b103eff4b59/2026/02/19/ML-19776-1120x630.png"
  summary="Union.ai와 Flyte로 Amazon EKS에서 AI 워크플로우 구축 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="AWS Machine Learning Blog"
  severity="Medium"
-%}


AWS가 Union.ai 2.0과 Flyte Python SDK를 활용해 Amazon EKS 위에서 AI/ML 워크플로우를 구축하는 실전 가이드를 공개했습니다. 컨테이너 네이티브 ML 파이프라인의 보안 설정(RBAC, 시크릿 관리)까지 다루고 있어 프로덕션 배포 시 참고할 만한 내용입니다.


#### 핵심 포인트

- Flyte Python SDK로 AI/ML 워크플로우 오케스트레이션 및 확장
- Amazon EKS 위에서 Union.ai 2.0 기반 AI 워크플로우 관리
- 컨테이너 네이티브 ML 파이프라인 구축 가이드 제공

#### 실무 적용 포인트

- EKS 기반 AI 워크플로우 구축 시 보안 컨텍스트 및 RBAC 설정 검토
- Flyte 워크플로우의 비밀 관리(Secrets Management) 모범 사례 적용
- ML 파이프라인 보안을 위한 네트워크 정책 구성

---

![Cloud Infrastructure News Section Banner](/assets/images/section-cloud.svg)

## 4. 클라우드 & 인프라 뉴스

### 4.1 Conversational Analytics API로 BigQuery에서 대화형 에이전트 구축

{%- include news-card.html
  title="[클라우드] Conversational Analytics API로 BigQuery에서 대화형 에이전트 구축"
  url="https://cloud.google.com/blog/products/data-analytics/build-data-agents-with-conversational-analytics-api/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/09_-_Data_Analytics_tFH57V6.max-2600x2600.jpg"
  summary="Conversational Analytics API로 BigQuery에서 대화형 에이전트 구축 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Google Cloud Blog"
  severity="Medium"
-%}


Google Cloud의 Conversational Analytics API를 이용하면 BigQuery 데이터에 자연어로 질의하는 대화형 에이전트를 별도 ML 인프라 없이 구축할 수 있습니다. 데이터 민주화와 셀프서비스 분석 환경을 강화하려는 팀에게 주목할 만한 업데이트입니다.


#### 핵심 포인트

- BigQuery 데이터에 대한 자연어 기반 대화형 접근 지원
- Conversational Analytics API로 데이터 에이전트 구축 간소화
- 기술적 장벽 해소를 통한 데이터 민주화 가속

---

### 4.2 BigQuery 자율 임베딩 생성으로 AI 워크플로우 간소화

{%- include news-card.html
  title="[클라우드] BigQuery 자율 임베딩 생성으로 AI 워크플로우 간소화"
  url="https://cloud.google.com/blog/products/data-analytics/introducing-bigquery-autonomous-embedding-generation/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/09_-_Data_Analytics_tFH57V6.max-2600x2600.jpg"
  summary="BigQuery 자율 임베딩 생성으로 AI 워크플로우 간소화 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Google Cloud Blog"
  severity="Medium"
-%}


Google이 BigQuery 내부에서 임베딩을 자동 생성·관리하는 기능을 도입했습니다. RAG 파이프라인 구축 시 별도 임베딩 서버 없이 BigQuery 단일 환경에서 완결되는 AI 워크플로우가 가능해져 운영 복잡도를 크게 줄일 수 있습니다.


#### 핵심 포인트

- BigQuery 내 자율 임베딩 생성으로 RAG 파이프라인 간소화
- AI 에이전트가 데이터를 이해하는 핵심 기술인 임베딩의 자동 관리
- 별도 인프라 없이 BigQuery 내에서 완결되는 AI 워크플로우 구현

---

### 4.3 Amazon Bedrock 사용량 관리 및 최적화 하기

{%- include news-card.html
  title="[클라우드] Amazon Bedrock 사용량 관리 및 최적화 하기"
  url="https://aws.amazon.com/ko/blogs/tech/optimzie-and-manage-amazon-bedrock-usage/"
  image="https://d2908q01vomqb2.cloudfront.net/2a459380709e2fe4ac2dae5733c73225ff6cfee1/2026/02/19/Screenshot-2026-02-19-at-11.53.05 AM-1117x630.png"
  summary="Amazon Bedrock 사용량 관리 및 최적화 하기 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="AWS Korea Blog"
  severity="Medium"
-%}


AWS Korea가 Amazon Bedrock 기반 AI 서비스의 토큰 사용량 관리와 비용 최적화 방법을 상세히 정리한 가이드를 공개했습니다. PoC를 넘어 프로덕션 운영 단계에 진입한 팀이라면 모델별 비용-성능 트레이드오프와 프롬프트 최적화 전략을 지금 검토할 시점입니다.


#### 핵심 포인트

- LLM 토큰 사용량 관리와 최적화는 운영 서비스 런칭 후 핵심 과제
- Amazon Bedrock 기반 AI 서비스의 비용 효율적 운영 가이드
- PoC에서 프로덕션까지의 안정적 AI 서비스 구축 로드맵 제공

#### 실무 적용 포인트

- Bedrock 토큰 사용량 모니터링 대시보드 구축
- 프롬프트 최적화를 통한 토큰 비용 절감 전략 수립
- 모델별 비용-성능 트레이드오프 분석 및 적정 모델 선정

---

### 4.4 주권과 유럽 경쟁력: 파트너십 기반 AI 성장 접근 방식

{%- include news-card.html
  title="[클라우드] 주권과 유럽 경쟁력: 파트너십 기반 AI 성장 접근 방식"
  url="https://cloud.google.com/blog/products/identity-security/sovereignty-and-european-competitiveness-a-partnership-led-approach-to-ai-growth/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/17_-_Security__Identity_NrORvDT.max-2600x2600.jpg"
  summary="주권과 유럽 경쟁력: 파트너십 기반 AI 성장 접근 방식 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Google Cloud Blog"
  severity="Medium"
-%}


Google Cloud가 유럽 데이터 주권 요구사항을 반영한 파트너십 기반 AI 인프라 전략을 발표했습니다. 현지 규제 준수와 기술 혁신을 동시에 달성하는 접근법으로, GDPR 및 EU AI Act 대응을 고려하는 클라우드 아키텍처 설계에 참고할 만한 내용입니다.


#### 핵심 포인트

- 유럽 데이터 주권 요구사항을 반영한 AI 인프라 전략
- 파트너십 기반 접근으로 현지 규제 준수와 기술 혁신 병행
- 클라우드 보안과 주권의 균형점 제시

---

![DevOps Platform News Section Banner](/assets/images/section-devops.svg)

## 5. DevOps & 개발 뉴스

### 5.1 클라우드 네이티브 현황 2026: CNCF CTO의 인사이트와 전망

{%- include news-card.html
  title="[DevOps] 클라우드 네이티브 현황 2026: CNCF CTO의 인사이트와 전망"
  url="https://www.cncf.io/blog/2026/02/19/state-of-cloud-native-2026-cncf-ctos-insights-and-predictions/"
  image="https://www.cncf.io/wp-content/uploads/2026/02/Akamia-Cloud-Credits-35.png"
  summary="클라우드 네이티브 현황 2026: CNCF CTO의 인사이트와 전망 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="CNCF Blog"
  severity="Medium"
-%}


CNCF 10주년을 맞아 CTO가 클라우드 네이티브 생태계의 현재와 향후 방향을 정리한 인사이트를 공개했습니다. AI 워크로드와 Kubernetes의 통합 가속화, 보안 표준 강화가 2026년 핵심 화두로 제시되어 클라우드 네이티브 전략 수립 시 기준점으로 활용할 수 있습니다.


#### 핵심 포인트

- CNCF 10주년 기념 클라우드 네이티브 생태계 현황 분석
- AI 워크로드와 Kubernetes 통합의 가속화 전망
- 클라우드 네이티브 보안 표준의 지속적 강화

---

### 5.2 Medplum, Docker Hardened Images(DHI)로 헬스케어 플랫폼 보안 강화 사례

{%- include news-card.html
  title="[DevOps] Medplum, Docker Hardened Images(DHI)로 헬스케어 플랫폼 보안 강화 사례"
  url="https://www.docker.com/blog/medplum-healthcare-docker-hardened-images/"
  image="https://www.docker.com/app/uploads/2025/03/image.png"
  summary="Medplum, Docker Hardened Images로 헬스케어 플랫폼 보안 강화 사례 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Docker Blog"
  severity="Medium"
-%}


오픈소스 의료 플랫폼 Medplum이 Docker Hardened Images 도입을 통해 HIPAA 규제 준수 수준의 컨테이너 보안을 달성한 과정을 공유했습니다. 헬스케어처럼 규제가 엄격한 환경에서 컨테이너 이미지 보안을 강화하려는 팀에게 실전 참고 사례가 됩니다.


#### 핵심 포인트

- 의료 플랫폼에서 Docker Hardened Images로 컨테이너 보안 강화
- 헬스케어 규제(HIPAA 등) 준수를 위한 컨테이너 보안 모범 사례
- 오픈소스 프로젝트의 보안 이미지 마이그레이션 경험 공유

---

### 5.3 Rust, Google Summer of Code 2026 참여 발표

{%- include news-card.html
  title="[DevOps] Rust, Google Summer of Code 2026 참여 발표"
  url="https://blog.rust-lang.org/2026/02/19/Rust-participates-in-GSoC-2026/"
  image="https://www.rust-lang.org/static/images/rust-social-wide.jpg"
  summary="Rust, Google Summer of Code 2026 참여 발표 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Rust Blog"
  severity="Medium"
-%}


Rust 프로젝트가 3년 연속 Google Summer of Code에 참여한다고 발표했습니다. 메모리 안전성으로 주목받는 Rust의 오픈소스 기여자 저변 확대는 보안 중심 시스템 소프트웨어 생태계 성장에 긍정적인 신호입니다.


#### 핵심 포인트

- Rust 프로젝트 3년 연속 GSoC 참여
- 오픈소스 기여자의 Rust 생태계 개발 참여 기회 확대

---

![Blockchain Web3 News Section Banner](/assets/images/section-blockchain.svg)

## 6. 블록체인 뉴스

### 6.1 비트코인 라이트닝 네트워크, 월간 거래량 10억 달러 돌파

{%- include news-card.html
  title="[블록체인] 비트코인 라이트닝 네트워크, 월간 거래량 10억 달러 돌파"
  url="https://cointelegraph.com/news/bitcoin-lightning-network-1b-monthly-volume"
  image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,onerror=redirect,w=1200/https://s3.cointelegraph.com/uploads/2026-02/019c77b1-52d4-779a-9396-2139521238f7.jpg"
  summary="비트코인 라이트닝 네트워크, 월간 거래량 10억 달러 돌파 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Cointelegraph"
  severity="Medium"
-%}


비트코인 라이트닝 네트워크의 월간 거래량이 11.7억 달러를 돌파하며 처음으로 10억 달러 벽을 넘었습니다. AI 에이전트 결제 실험 확산이 새로운 수요를 창출하고 있으며, 소액 결제 인프라로서의 입지가 빠르게 강화되고 있습니다.


#### 핵심 포인트

- 비트코인 라이트닝 네트워크 월간 거래량 11.7억 달러 돌파
- AI 에이전트 결제 실험 확산에 따른 거래량 증가 전망
- 개인과 기업의 라이트닝 네트워크 채택 가속화

---

### 6.2 CME, 5월 암호화폐 파생상품 24/7 거래 출시 목표

{%- include news-card.html
  title="[블록체인] CME, 5월 암호화폐 파생상품 24/7 거래 출시 목표"
  url="https://cointelegraph.com/news/cme-may-24-7-crypto-derivative-trading"
  image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,onerror=redirect,w=1200/https://s3.cointelegraph.com/uploads/2026-02/019c76b7-6035-78bb-a892-da0e8b8ce4fb.jpg"
  summary="CME, 5월 암호화폐 파생상품 24/7 거래 출시 목표 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Cointelegraph"
  severity="Medium"
-%}


CME Group이 5월 29일부터 암호화폐 선물의 24시간 365일 거래를 시작할 예정입니다. SEC와 CFTC의 거래 시간 확대 검토와 맞물려 전통 금융과 암호화폐 시장의 경계가 빠르게 허물어지고 있는 흐름을 보여줍니다.


#### 핵심 포인트

- CME Group, 5월 29일부터 24/7 암호화폐 선물 거래 시작 예정
- SEC, CFTC의 24/7 거래 시간 확대 검토와 맞물린 움직임
- 전통 금융과 암호화폐 시장의 거래 시간 통합 가속화

---

### 6.3 SEC 리더십, 토큰화 증권과 기존 규제의 상호작용 명확화 추진

{%- include news-card.html
  title="[블록체인] SEC 리더십, 토큰화 증권과 기존 규제의 상호작용 명확화 추진"
  url="https://cointelegraph.com/news/sec-leadership-future-securities-ethdenver"
  image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,onerror=redirect,w=1200/https://s3.cointelegraph.com/uploads/2026-02/019c76c0-5e44-7e39-90ed-b285dc9cde3b.jpg"
  summary="SEC 리더십, 토큰화 증권과 기존 규제의 상호작용 명확화 추진 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Cointelegraph"
  severity="Medium"
-%}


SEC 리더십이 ETHDenver에서 토큰화 증권과 기존 증권법의 상호작용을 공식적으로 명확화하겠다는 방향을 제시했습니다. 규제 불확실성 해소 움직임으로 블록체인 기반 금융 상품을 준비하는 기업에게 중요한 정책 신호입니다.


#### 핵심 포인트

- SEC 리더십이 ETHDenver에서 토큰화 증권 규제 방향 발표
- 기존 증권법과 토큰화 자산의 상호작용 명확화 추진
- 암호화폐 시장 변동성에 대한 규제 기관 대응 방향 제시

---

### 6.4 비트코인 ETF, 최근 유출에도 530억 달러 순유입 유지

{%- include news-card.html
  title="[블록체인] 비트코인 ETF, 최근 유출에도 530억 달러 순유입 유지"
  url="https://cointelegraph.com/news/bitcoin-etfs-53b-net-inflows-after-selloff"
  image="https://images.cointelegraph.com/cdn-cgi/image/f=auto,onerror=redirect,w=1200/https://s3.cointelegraph.com/uploads/2026-01/019b92cc-d609-7af6-b3a8-9b3f85736edf.jpg"
  summary="비트코인 ETF, 최근 유출에도 530억 달러 순유입 유지 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Cointelegraph"
  severity="Medium"
-%}


비트코인 ETF가 최근 유출에도 불구하고 530억 달러의 순유입을 유지하고 있습니다. 기관 투자자의 지속적인 관심이 단기 가격 변동과 별개로 유지되는 흐름입니다.


#### 핵심 포인트

- 현물 비트코인 ETF, 최근 유출에도 530억 달러 순유입 유지
- 기관 투자자의 장기적 비트코인 ETF 신뢰 확인
- 단기 매도 압력에도 누적 유입 규모는 견고

---

### 6.5 UAE, 조용히 4억 5300만 달러 규모의 비트코인 준비금 축적

{%- include news-card.html
  title="[블록체인] UAE, 조용히 4억 5300만 달러 규모의 비트코인 준비금 축적"
  url="https://bitcoinmagazine.com/news/the-uae-453-million-bitcoin-reserve"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/02/The-UAE-Has-Quietly-Built-Up-a-453-Million-Bitcoin-Reserve-Arkham-.jpg"
  summary="UAE, 조용히 4억 5300만 달러 규모의 비트코인 준비금 축적 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
-%}


UAE 왕실 연계 채굴 업체가 6,782 BTC(약 4억 5,300만 달러)를 보유하고 있음이 확인되며 국가 차원의 비트코인 준비금 전략이 드러났습니다. 중동 지역 기관 투자자의 암호화폐 채택이 조용하지만 의미 있는 속도로 진행되고 있음을 보여주는 사례입니다.


#### 핵심 포인트

- UAE 왕실 연계 채굴 업체, 6,782 BTC(4.53억 달러) 보유 확인
- 국가 차원의 비트코인 준비금 축적 전략 드러남
- 중동 지역의 암호화폐 기관 투자 확대 추세

---

## 7. 기타 주목할 뉴스

이 섹션은 즉시 대응이 필요한 보안 이슈 외에도 제품 전략, 운영 모델, 정책 변화까지 함께 읽어야 하는 후속 신호를 정리한 것입니다.

{% capture spotlight_items %}
{% include news-spotlight-item.html
  title="Spotify Multi-Agent Architecture for Advertising"
  url="https://engineering.atspotify.com/2026/2/our-multi-agent-architecture-for-smarter-advertising/"
  source="Spotify Engineering"
  tag="Operator Signal"
  summary="Spotify Multi-Agent Architecture for Advertising 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
%}
{% include news-spotlight-item.html
  title="Discord Osprey: Open Sourcing our Rule Engine"
  url="https://discord.com/blog/osprey-open-sourcing-our-rule-engine"
  source="Discord Blog"
  tag="Operator Signal"
  summary="Discord Osprey: Open Sourcing our Rule Engine 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
%}
{% include news-spotlight-item.html
  title="Chrome CSS Zero-Day CVE-2026-2441"
  url="https://news.hada.io/topic?id=26823"
  source="GeekNews"
  tag="Tech Signals"
  summary="Chrome CSS Zero-Day CVE-2026-2441 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
%}
{% include news-spotlight-item.html
  title="ThreatsDay Bulletin: OpenSSL RCE, Foxit 0-Days"
  url="https://thehackernews.com/2026/02/threatsday-bulletin-openssl-rce-foxit-0.html"
  source="The Hacker News"
  tag="Operator Signal"
  summary="ThreatsDay Bulletin: OpenSSL RCE, Foxit 0-Days 이슈를 기준으로 기술적으로는 공격 경로·영향 자산·탐지 포인트를 정리하고, 경영진 관점에서는 서비스 영향·우선순위·의사결정 체크포인트를 함께 제시했습니다."
%}
{% endcapture %}
{% include news-spotlight-section.html
  aria_label="기타 주목할 뉴스"
  intro="이 섹션은 즉시 대응이 필요한 보안 이슈 외에도 제품 전략, 운영 모델, 정책 변화까지 함께 읽어야 하는 후속 신호를 정리한 것입니다."
  body=spotlight_items
%}
---

## 8. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| AI/ML | 12건 | gemini, ai agent, alignment |
| Supply Chain | 3건 | clinejection, npm, github actions |
| Cloud Security | 5건 | bigquery, bedrock, sovereignty |
| Kubernetes | 3건 | ingress nginx, gateway api |
| Blockchain | 5건 | lightning network, etf, tokenization |

이번 주기에서 가장 많이 언급된 트렌드는 AI/ML (12건)입니다. 특히 AI 에이전트 보안이 새로운 위협 벡터로 부상하고 있으며(PromptSpy, Clinejection), Kubernetes의 Ingress NGINX 은퇴는 클라우드 네이티브 환경의 약 50%에 영향을 미칠 수 있어 즉각적인 대응이 필요합니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] PromptSpy 관련 모바일 보안 정책 점검 및 MDM 사이드로딩 차단
- [ ] Clinejection 관련 AI 코딩 에이전트 실행 권한 및 GitHub Actions 캐시 보안 검토
- [ ] Massiv 안드로이드 트로이목마 관련 모바일 뱅킹 보안 강화
- [ ] Chrome CVE-2026-2441 CSS 제로데이 패치 즉시 적용

### P1 (7일 내)

- [ ] CVE-2026-26119 Windows Admin Center 패치 적용
- [ ] Kubernetes Ingress NGINX 사용 현황 전수 조사 및 마이그레이션 계획 수립
- [ ] Ingress NGINX 최신 고위험 CVE 4종 패치 적용
- [ ] SIEM 탐지 룰 업데이트 (PromptSpy IOC, Massiv IOC 등)

### P2 (30일 내)

- [ ] AI 에이전트 보안 가이드라인 수립 (PromptSpy, Clinejection 사례 반영)
- [ ] Gateway API 기반 Ingress 컨트롤러 마이그레이션 실행
- [ ] 공격 표면 인벤토리 갱신 (AI 에이전트 포함)
- [ ] 접근 제어 감사

---


---

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |
| Kubernetes Gateway API | [gateway-api.sigs.k8s.io](https://gateway-api.sigs.k8s.io/) |

---

작성자: Twodragon
