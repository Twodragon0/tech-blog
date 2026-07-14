---
layout: post
title: "2026년 04월 08일 주간 보안 다이제스트: 제로데이·BYOVD EDR·DNS 유출 (15건)"
date: 2026-04-08 10:30:05 +0900
last_modified_at: 2026-05-06T15:26:06+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, CVE, Docker, Botnet]
excerpt: "러시아 국가 연계 APT28, 글로벌 DNS 하이재킹 캠페인에서 · [웨비나] AI가 기업 리스크를 악용하기 전에 2026년까지가 부각된 2026년 04월 08일 보안 다이제스트 — 18건의 이슈와 실행 가능한 대응 액션을 정리합니다. 보안 운영센터(SOC)와 DevSecOps 팀이 즉시 적용할 수 있는 차단·완화 조치를 요약합니다."
description: "러시아 국가 연계 APT28 글로벌 DNS 하이재킹 캠페인, Docker CVE-2026-34040 인증 우회 취약점, AI 스타트업 보안 리스크 노출 사례를 중심으로 2026년 04월 08일 주요 보안·기술 뉴스 18건과 DevSecOps 대응 우선순위를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, CVE, Docker]
author: Twodragon
comments: true
image: /assets/images/2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.svg
image_alt: "APT28 DNS hijacking, Docker CVE, AI enterprise security digest"
toc: true
redirect_from:
  - /posts/2026/04/Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet/
  - /posts/2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet/
summary_card:
  title: "2026년 04월 08일 주간 보안 다이제스트: 제로데이·BYOVD EDR·DNS 유출 (15건)"
  period: "2026년 04월 08일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "CVE"
    - "Docker"
    - "Botnet"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "러시아 국가 연계 APT28, 글로벌 DNS 하이재킹 캠페인에서 SOHO 라우터 악용" }
    - { source: "The Hacker News", title: "[웨비나] AI가 기업 리스크를 악용하기 전에 2026년까지 아이덴티티 격차를 해소하는 방법" }
    - { source: "The Hacker News", title: "Docker CVE-2026-34040으로 공격자 인증 우회 및 호스트 접근 권한 획득 가능" }
    - { source: "Google Cloud Blog", title: "Claude Mythos 프리뷰: Vertex AI에서 프라이빗 프리뷰로 이용 가능" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 04월 08일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 18개
- **보안 뉴스**: 3개
- **AI/ML 뉴스**: 3개
- **클라우드 뉴스**: 3개
- **DevOps 뉴스**: 3개
- **블록체인 뉴스**: 3개
- **기타 뉴스**: 3개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | 러시아 국가 연계 APT28, 글로벌 DNS 하이재킹 캠페인에서 SOHO 라우터 악용 | 🟠 High |
| 🔒 **Security** | The Hacker News | [웨비나] AI가 기업 리스크를 악용하기 전에 2026년까지 아이덴티티 격차를 해소하는 방법 | 🟠 High |
| 🔒 **Security** | The Hacker News | Docker CVE-2026-34040으로 공격자 인증 우회 및 호스트 접근 권한 획득 가능 | 🟠 High |
| 🤖 **AI/ML** | Palantir Blog | Palantir의 프론트엔드 엔지니어링: Three.js의 플롯라인 | 🟡 Medium |
| 🤖 **AI/ML** | AWS Machine Learning | Amazon Bedrock Projects로 AI 비용 관리하기 | 🟡 Medium |
| 🤖 **AI/ML** | AWS Machine Learning | Amazon Nova 2 Sonic으로 실시간 대화형 팟캐스트 구축하기 | 🟠 High |
| ☁️ **Cloud** | Google Cloud Blog | Claude Mythos 프리뷰: Vertex AI에서 프라이빗 프리뷰로 이용 가능 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Google Cloud NGFW로 IP와 보안 URL 이상을 확인하세요 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Lyria 3 모델을 위한 최고의 프롬프팅 가이드 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Dynatrace의 런타임 컨텍스트로 보안 경고에 우선순위 지정하기 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: Docker CVE-2026-34040 인증 우회 취약점이 확인되었으며, 컨테이너 환경의 즉시 패치가 필요합니다.
- **주요 모니터링 대상**: 러시아 국가 연계 APT28의 DNS 하이재킹, AI 아이덴티티 격차 대응 웨비나, Docker CVE-2026-34040 인증 우회, Amazon Nova 2 Sonic 실시간 대화 워크로드 등 High 등급 위협 4건에 대한 탐지 강화가 필요합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 러시아 국가 연계 APT28, 글로벌 DNS 하이재킹 캠페인에서 SOHO 라우터 악용

{% include news-card.html
  title="러시아 국가 연계 APT28, 글로벌 DNS 하이재킹 캠페인에서 SOHO 라우터 악용"
  url="https://thehackernews.com/2026/04/russian-state-linked-apt28-exploits.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj6xcrxyaKNQYXfVN-AHFfiSrJ_8SwW3v7MgKlJNBi-E5WIwT3ZNrNm4fcT0JZKHHLH9fbtMKdYhG_2DBHxkIy7-EydaWvEeeo4LDRPgAJ1K8i-YFeD9a0gPnw92xfN4FU3k7rQUhizsFLL8fiAo2YOw-ql-Ru07KtBUoA__B_fGYW4I6jnnn-OPwxoXnCx/s1600/router.jpg"
  summary="러시아 국가 연계 해킹 그룹 APT28(별칭 Forest Blizzard)이 2025년 5월부터 MikroTik 및 TP-Link SOHO 라우터를 탈취해 DNS 하이재킹 인프라로 악용한 사이버 스파이 캠페인을 진행해 왔습니다. 이 대규모 공격 작전은 불안전한 라우터를 악성 인프라로 전환하여 장악한 것이 특징입니다."
  source="The Hacker News"
  severity="High"
%}

# APT28의 SOHO 라우터 DNS 하이재킹 캠페인 분석

## 1. 기술적 배경 및 위협 분석
이번 공격은 국가 지원 해킹 그룹 APT28이 보안이 취약한 SOHO(소규모 사무실/가정용) 라우터, 특히 MikroTik 및 TP-Link 제품을 대규모로 악용한 DNS 하이재킹 캠페인입니다. 공격자는 2025년 5월부터 최소한 9개월 이상 지속적으로 약점을 악용하여 라우터 설정을 변조, 이를 악성 인프라로 전환했습니다. 기술적 핵심은 **기본/약한 자격증명, 알려진 취약점 미패치, 원격 관리 인터페이스 노출** 등을 통해 라우터에 침투한 후, DNS 설정을 변경하여 합법적인 도메인 요청을 악성 서버로 리다이렉트하는 것입니다. 이를 통해 표적 조직의 이메일, 클라우드 서비스, 내부 시스템에 대한 인증 정보 탈취 및 지능형 지속 공격(APT)을 수행한 것으로 분석됩니다. SOHO 장비는 전통적인 엔터프라이즈 보안 모니터링 범위에서 벗어나기 때문에 탐지가 어렵고, 공격자가 저비용으로 글로벌 악성 인프라를 구축할 수 있다는 점이 위협적입니다.

## 2. 실무 영향 분석
DevSecOps 관점에서 이 공격은 **소프트웨어 공급망과 하이브리드 근무 환경의 취약점**을 정확히 타격했습니다. 많은 조직이 원격 근무자를 위해 SOHO 라우터를 사용하며, 이러한 장비는 자동화된 패치 관리 체계 밖에 존재합니다. 결과적으로, 개발자의 원격 접속, CI/CD 파이프라인 통신, 클라우드 서비스 인증 트래픽이 조작될 수 있으며, 이는 **소스 코드 유출, 빌드 환경 오염, 프로덕션 시스템 침해**로 직접 이어질 수 있습니다. 또한, 공격자가 하이재킹한 라우터를 악성 C2 서버나 피싱 사이트 호스팅에 사용함으로써, 조직의 외부에서 발신되는 공격에도 간접적으로 연루될 수 있는 리스크가 있습니다. 이는 기존의 엔드포인트 및 클라우드 중심 보안 모델만으로는 방어가 불충분함을 보여줍니다.

## 3. 대응 체크리스트
- [ ] **원격 근무 인프라 가시화 및 강화**: 조직 네트워크에 접속하는 모든 SOHO/가정용 라우터를 인벤토리화하고, 최소한 기본 비밀번호 변경, 펌웨어 최신 버전 유지, 불필요한 원격 관리 기능 비활성화를 의무화하라.
- [ ] **DNS 보안 조치 적용**: 모든 개발 및 운영 환경에서 DNS-over-HTTPS(DoH) 또는 DNS-over-TLS(DoT)와 같은 암호화된 DNS 프로토콜을 채택하고, DNSSEC 검증을 활성화하여 DNS 응답 조작을 탐지하라.
- [ ] **아웃바운드 트래픽 모니터링 강화**: CI/CD 툴, 패키지 저장소, 클라우드 관리 콘솔로 향하는 아웃바운드 연결을 특히 주시하고, 예상치 못한 지리적 위치나 알려진 악성 IP로의 연결 시도를 탐지하는 규칙을 SIEM/SOAR에 추가하라.
- [ ] **공급망 공격 시나리오 테스트**: 레드 팀/퍼플 팀 연습에 '손상된 개발자 장비' 또는 '조작된 네트워크 인프라' 시나리오를 포함시켜, DNS 하이재킹을 통한 인증 정보 탈취 및 후속 공격에 대한 탐지 및 대응 능력을 평가하라.

---

### 1.2 [웨비나] AI가 기업 리스크를 악용하기 전에 2026년까지 아이덴티티 격차를 해소하는 방법

{% include news-card.html
  title="[웨비나] AI가 기업 리스크를 악용하기 전에 2026년까지 아이덴티티 격차를 해소하는 방법"
  url="https://thehackernews.com/2026/04/webinar-how-to-close-identity-gaps-in.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgRHgJL0SczODx5PAnF85b8b0mRpiOOkIQdOWvhivyXu6H8UeZKH9ZUdaeW5IuU59q2hjMNioQWQ5vk1Km8yinGGc8GA079qvhTtFsp9PV76Kmp-3lpKh2zi3vgd_-6dFcOI6i1YHs7VkJ-p-HvOEuOwkjooBVSvYFOrVqXqNhZShZy3IUeD6BVHVvUIj50/s1600/webinar-cerby.jpg"
  summary="Ponemon Institute 연구에 따르면 기업 내 수많은 애플리케이션이 중앙 집중식 Identity 시스템에서 분리된 '다크' 상태로 남아 있어 Identity 프로그램이 성숙함에도 위험이 증가하는 역설이 발생하고 있습니다. 2026년 위협 환경에서 AI가 이러한 취약점을 악용하기 전에 Identity 격차를 해소하는 방법이 주요 과제입니다."
  source="The Hacker News"
  severity="High"
%}

# 보안 웨비나 분석: 2026년 AI가 악용하기 전, 기업의 아이덴티티 격차 해결 방법

## 1. 기술적 배경 및 위협 분석
2026년 위협 환경에서 아이덴티티 관리 프로그램이 성숙해짐에도 불구하고 오히려 위험이 증가하는 역설이 발생하고 있습니다. Ponemon 연구소의 새로운 연구에 따르면, 일반적인 기업 내 수백 개의 애플리케이션이 중앙 집중식 아이덴티티 시스템(예: IAM, CIEM)과 연결되지 않은 "다크 애플리케이션"으로 남아 있습니다. 이러한 격차는 AI 기반 공격에 특히 취약한데, AI는 이러한 연결되지 않은 시스템을 자동으로 탐지하고, 취약점을 분석하며, 대규모로 권한 상승 또는 데이터 유출 공격을 수행할 수 있습니다. 클라우드 네이티브 환경과 하이브리드 워크의 확산으로 인해 관리되지 않는 아이덴티티(사용자, 서비스, 머신)가 기하급수적으로 증가하며, 이는 AI 공격자에게 이상적인 표적이 되고 있습니다.

## 2. 실무 영향 분석
DevSecOps 실무자에게 이 문제는 직접적인 운영 위험과 책임으로 이어집니다. 첫째, 개발팀이 빠르게 도입하는 새로운 클라우드 서비스, 컨테이너, 마이크로서비스는 종종 중앙 IAM 정책 검토를 거치지 않아 "섀도 아이덴티티"를 생성합니다. 둘째, CI/CD 파이프라인 내 서비스 계정과 DevOps 도구 체인의 접근 권한이 제대로 관리되지 않을 경우, 공격자가 파이프라인 자체를 침해하여 전사적인 위협으로 확대될 수 있습니다. 셋째, AI가 악용될 경우, 기존의 정적 접근 제어와 수동 감사로는 대응이 불가능해지므로, 실시간 위험 기반 접근 제어와 자동화된 대응이 필수적입니다. 이는 단순한 정책 문제를 넘어 시스템 설계와 지속적인 모니터링 방식의 근본적 변화를 요구합니다.

## 3. 대응 체크리스트
- [ ] **자산 및 아이덴티티 인벤토리 정기 점검**: 모든 클라우드 계정, 애플리케이션, 서비스/머신 아이덴티티를 매핑하여 중앙 IAM 시스템과의 연결 상태를 주기적으로(분기별) 검증하고, "다크" 자산을 식별하는 자동화 스크립트를 운영 환경에 통합합니다.
- [ ] **DevSecOps 파이프라인 내 IAM 통합 강화**: CI/CD 도구 체인(예: Jenkins, GitLab)의 모든 서비스 계정과 배포 권한을 중앙 IdP(예: Azure AD, Okta)와 연동하고, 인프라 as 코드(IaC) 템플릿에 최소 권한 IAM 정책을 기본으로 포함시킵니다.
- [ ] **AI 기반 이상 행위 탐지 도구 검토 및 도입**: 사용자 및 엔터티 행동 분석(UEBA)을 넘어, 서비스 간 통패턴과 DevOps 활동을 학습하여 비정상적인 접근 시도를 실시간으로 탐지하고 대응할 수 있는 AI 기반 솔루션 도입을 평가합니다.
- [ ] **권한 상승 및 세션 관리 강화**: JIT(Just-In-Time) 접근과 시간 기반 권한을 적용하여 상시 권한을 최소화하고, 특히 관리자 세션에 대해 세부 로깅과 행위 기록을 필수화합니다.

---

### 1.3 Docker CVE-2026-34040으로 공격자 인증 우회 및 호스트 접근 권한 획득 가능

{% include news-card.html
  title="Docker CVE-2026-34040으로 공격자 인증 우회 및 호스트 접근 권한 획득 가능"
  url="https://thehackernews.com/2026/04/docker-cve-2026-34040-lets-attackers.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi1fiR51KBq7hNIR1D2V9e0jituEJTVutYd8b9v6KR0YdA30xWCSKJo3nfIykSdYSjZNe7gvNj3Wf3HidhZ24n-piDo8LhrE6ctyZrcLYNcJwCSP0KEe7G0Fl_xJm676Dv-4bFEh63Vv_xZ1zb9qOKhfeWFN5IexOHligHBCTHyVLAMDl0aeL2olDxnjfch/s1600/ai-chat.jpg"
  summary="Docker Engine에서 인가 플러그인(AuthZ)을 우회할 수 있는 고위험 취약점 CVE-2026-34040이 공개되었습니다. 이 취약점은 2024년 7월에 발견된 최고 위험 등급 취약점 CVE-2024-41110에 대한 수정이 불완전해 발생한 것으로, 공격자가 특정 조건에서 호스트 접근 권한을 획득할 수 있습니다."
  source="The Hacker News"
  severity="High"
%}

# Docker CVE-2026-34040 인증 우회 취약점 분석

## 1. 기술적 배경 및 위협 분석
이 취약점은 Docker Engine의 인증 플러그인(AuthZ) 시스템에서 발생합니다. AuthZ 플러그인은 Docker 데몬(dockerd)에 대한 API 요청을 가로채어 사용자 권한을 검증하는 핵심 보안 메커니즘입니다. CVE-2026-34040는 2024년 7월에 공개된 최대 위험 등급 취약점(CVE-2024-41110)에 대한 수정이 불완전하여 파생된 문제입니다. 공격자는 특정 조건에서 이 취약점을 악용하여 AuthZ 검증을 우회하고, 결국 호스트 시스템에 대한 무단 접근 및 권한 상승을 달성할 수 있습니다. CVSS 8.8의 높은 위험도는 네트워크를 통한 원격 공격 가능성과 성공 시 호스트 제어권을 완전히 탈취할 수 있는 심각한 영향을 반영합니다.

## 2. 실무 영향 분석
DevSecOps 환경에서 이 취약점은 특히 다중 테넌트 환경이나 개발자에게 Docker 데몬 접근 권한이 부여된 경우 치명적입니다. CI/CD 파이프라인에서 Docker를 사용하는 모든 단계(이미지 빌드, 컨테이너 실행, 레지스트리 연동)가 공격 경로가 될 수 있습니다. 취약한 Docker Engine을 실행하는 모든 호스트(개발자 워크스테이션, 빌드 서버, 프로덕션 노드)가 위협에 노출됩니다. 컨테이너 보안의 기본 전제인 격리와 최소 권한 원칙이 무너져, 단일 컨테이너의 침해가 전체 호스트 및 호스트 내 다른 컨테이너로 확장될 수 있습니다. 이는 기업의 애플리케이션 보안과 데이터 무결성에 직접적인 위협이 됩니다.

## 3. 대응 체크리스트
- [ ] **취약 버전 식별 및 패치**: 모든 Docker 호스트(개발, 스테이징, 프로덕션)의 Docker Engine 버전을 점검하고, 취약한 버전(공식 패치 노트 기준)을 즉시 최신 안정판으로 업데이트하세요.
- [ ] **AuthZ 플러그인 구성 검증**: 사용 중인 AuthZ 플러그인(예: Twistlock, Aqua Security 등)의 구성과 로그를 검토하여 비정상적인 우회 시도 흔적이 있는지 모니터링하세요.
- [ ] **네트워크 격리 및 접근 제어 강화**: Docker 데몬 API(기본값: TCP 2375/2376)에 대한 불필요한 네트워크 접근을 차단하고, TLS 인증서를 통한 상호 인증을 필수로 적용하세요.
- [ ] **런타임 보안 모니터링 강화**: 호스트 및 컨테이너 런타임에서의 비정상적인 프로세스 실행, 권한 상승 시도, 호스트 리소스 접근을 탐지하도록 보안 모니터링 도구(Falco, Wazuh 등) 규칙을 업데이트하고 검증하세요.
- [ ] **CI/CD 파이프라인 보안 점검**: CI/CD 도구(Jenkins, GitLab Runner 등)가 사용하는 Docker 소켓 또는 API 접근 권한을 재평가하고, 가능한 경우 더 제한된 권한을 가진 별도의 Docker 인스턴스를 사용하도록 파이프라인을 재구성하세요.

#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - T1078  # Valid Accounts
```

---

## 2. AI/ML 뉴스

### 2.1 Palantir의 프론트엔드 엔지니어링: Three.js의 플롯라인

{% include news-card.html
  title="Palantir의 프론트엔드 엔지니어링: Three.js의 플롯라인"
  url="https://blog.palantir.com/frontend-engineering-at-palantir-plotlines-in-three-js-c0c47f310715?source=rss----3c87dc14372f---4"
  image="https://cdn-images-1.medium.com/max/1024/1*D_5LhinYPvt9spEjX8t_AA.png"
  summary="Palantir의 프론트엔드 엔지니어링은 표준 웹 앱을 넘어 네트워크가 불안정하고 오류 허용 범위가 없는 상황에서도 사용자 요구를 충족하는 미션 크리티컬 인터페이스를 설계합니다. 이들은 대규모 데이터셋을 처리하며 통찰력을 실행으로 전환하는 운영 애플리케이션을 Three.js와 같은 기술로 구축합니다."
  source="Palantir Blog"
  severity="Medium"
%}

#### 요약

Palantir의 프론트엔드 엔지니어링은 표준 웹 앱을 넘어 네트워크가 불안정하고 오류 허용 범위가 없는 상황에서도 사용자 요구를 충족하는 미션 크리티컬 인터페이스를 설계합니다. 이들은 대규모 데이터셋을 처리하며 통찰력을 실행으로 전환하는 운영 애플리케이션을 Three.js와 같은 기술로 구축합니다.

---

### 2.2 Amazon Bedrock Projects로 AI 비용 관리하기

{% include news-card.html
  title="Amazon Bedrock Projects로 AI 비용 관리하기"
  url="https://aws.amazon.com/blogs/machine-learning/manage-ai-costs-with-amazon-bedrock-projects/"
  summary="Amazon Bedrock Projects를 사용하면 추론 비용을 특정 워크로드에 귀속시키고 AWS Cost Explorer 및 AWS Data Exports에서 분석할 수 있습니다. 이 게시물에서는 태깅 전략 설계부터 비용 분석에 이르는 Projects의 종단 간 설정 방법을 소개합니다."
  source="AWS Machine Learning Blog"
  severity="Medium"
%}

#### 요약

Amazon Bedrock Projects를 사용하면 추론 비용을 특정 워크로드에 귀속시키고 AWS Cost Explorer 및 AWS Data Exports에서 분석할 수 있습니다. 이 게시물에서는 태깅 전략 설계부터 비용 분석에 이르는 Projects의 종단 간 설정 방법을 소개합니다.

---

### 2.3 Amazon Nova 2 Sonic으로 실시간 대화형 팟캐스트 구축하기

{% include news-card.html
  title="Amazon Nova 2 Sonic으로 실시간 대화형 팟캐스트 구축하기"
  url="https://aws.amazon.com/blogs/machine-learning/building-real-time-conversational-podcasts-with-amazon-nova-2-sonic/"
  summary="Amazon Nova 2 Sonic의 스트리밍 기능을 활용해 주제에 따라 두 AI 호스트 간의 대화를 생성하는 자동화된 팟캐스트 제작 방법이 소개됐습니다. 이는 스테이지 인식 콘텐츠 필터링과 실시간 오디오 생성 기술을 보여줍니다."
  source="AWS Machine Learning Blog"
  severity="High"
%}

#### 요약

Amazon Nova 2 Sonic의 스트리밍 기능을 활용해 주제에 따라 두 AI 호스트 간의 대화를 생성하는 자동화된 팟캐스트 제작 방법이 소개됐습니다. 이는 스테이지 인식 콘텐츠 필터링과 실시간 오디오 생성 기술을 보여줍니다.

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Claude Mythos 프리뷰: Vertex AI에서 프라이빗 프리뷰로 이용 가능

{% include news-card.html
  title="Claude Mythos 프리뷰: Vertex AI에서 프라이빗 프리뷰로 이용 가능"
  url="https://cloud.google.com/blog/products/ai-machine-learning/claude-mythos-preview-on-vertex-ai/"
  summary="Anthropic의 최신 최강 모델인 Claude Mythos Preview가 Project Glasswing의 일환으로 선별된 Google Cloud 고객을 대상으로 Vertex AI에서 Private Preview로 제공됩니다. Vertex AI를 통한 Claude Mythos Preview 제공은 Google Cloud가 선도적인 AI 연구소의 모델에"
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Anthropic의 최신 최강 모델인 Claude Mythos Preview가 Project Glasswing의 일환으로 선별된 Google Cloud 고객을 대상으로 Vertex AI에서 Private Preview로 제공됩니다. Vertex AI를 통한 Claude Mythos Preview 제공은 Google Cloud가 선도적인 AI 연구소의 모델에 대한 고객 접근을 제공하겠다는 약속을 강조합니다.

---

### 3.2 Google Cloud NGFW로 IP와 보안 URL 이상을 확인하세요

{% include news-card.html
  title="Google Cloud NGFW로 IP와 보안 URL 이상을 확인하세요"
  url="https://cloud.google.com/blog/products/identity-security/see-beyond-the-ip-and-secure-urls-with-google-cloud-ngfw/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/image1_zzP0Xt6.max-1000x1000.png"
  summary="클라우드 환경에서 기존 IP 기반 방어는 더 이상 충분하지 않습니다. Google Cloud NGFW Enterprise는 와일드카드 기능을 갖춘 도메인 필터링을 도입하여 동적 IP와 FQDN의 한계를 해결합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

클라우드 환경에서 기존 IP 기반 방어는 더 이상 충분하지 않습니다. Google Cloud NGFW Enterprise는 와일드카드 기능을 갖춘 도메인 필터링을 도입하여 동적 IP와 FQDN의 한계를 해결합니다.

---

### 3.3 Lyria 3 모델을 위한 최고의 프롬프팅 가이드

{% include news-card.html
  title="Lyria 3 모델을 위한 최고의 프롬프팅 가이드"
  url="https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-lyria-3-pro/"
  summary="Google의 음악 생성 모델군 Lyria 3는 보컬, 악기 구성, 편곡에 대한 세밀한 제어를 제공하도록 설계되었습니다. 이 가이드는 다양한 음악 장르와 사용 사례를 테스트한 결과를 바탕으로 최상의 결과를 얻는 방법을 공유합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google의 음악 생성 모델군 Lyria 3는 보컬, 악기 구성, 편곡에 대한 세밀한 제어를 제공하도록 설계되었습니다. 이 가이드는 다양한 음악 장르와 사용 사례를 테스트한 결과를 바탕으로 최상의 결과를 얻는 방법을 공유합니다.

---

## 4. DevOps & 개발 뉴스

### 4.1 Dynatrace의 런타임 컨텍스트로 보안 경고에 우선순위 지정하기

{% include news-card.html
  title="Dynatrace의 런타임 컨텍스트로 보안 경고에 우선순위 지정하기"
  url="https://github.blog/changelog/2026-04-07-prioritize-security-alerts-with-runtime-context-from-dynatrace"
  image="https://github.blog/wp-content/uploads/2026/04/573334750-bed39ef7-f411-4705-9821-0df16c6af6ad.jpg"
  summary="Dynatrace의 런타임 컨텍스트를 활용해 Kubernetes 환경에서 배포된 아티팩트와 런타임 리스크를 기반으로 GitHub Advanced Security 알림의 우선순위를 지정할 수 있게 되었습니다. 이 기능은 GitHub 블로그를 통해 소개되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

Dynatrace의 런타임 컨텍스트를 활용해 Kubernetes 환경에서 배포된 아티팩트와 런타임 리스크를 기반으로 GitHub Advanced Security 알림의 우선순위를 지정할 수 있게 되었습니다. 이 기능은 GitHub 블로그를 통해 소개되었습니다.

---

### 4.2 Copilot CLI가 BYOK 및 로컬 모델 지원을 추가

{% include news-card.html
  title="Copilot CLI가 BYOK 및 로컬 모델 지원을 추가"
  url="https://github.blog/changelog/2026-04-07-copilot-cli-now-supports-byok-and-local-models"
  image="https://github.blog/wp-content/themes/github-2021-child/dist/img/social-v3-new-releases.jpg"
  summary="GitHub Copilot CLI가 이제 BYOK와 로컬 모델을 지원합니다. 사용자는 GitHub 호스팅 모델 대신 자체 모델 제공자를 연결하거나 완전히 로컬 모델을 실행할 수 있게 되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Copilot CLI가 이제 BYOK와 로컬 모델을 지원합니다. 사용자는 GitHub 호스팅 모델 대신 자체 모델 제공자를 연결하거나 완전히 로컬 모델을 실행할 수 있게 되었습니다.

---

### 4.3 Dependabot 경고를 이제 AI 에이전트에 할당해 수정할 수 있습니다

{% include news-card.html
  title="Dependabot 경고를 이제 AI 에이전트에 할당해 수정할 수 있습니다"
  url="https://github.blog/changelog/2026-04-07-dependabot-alerts-are-now-assignable-to-ai-agents-for-remediation"
  image="https://github.blog/wp-content/uploads/2026/04/571584033-8e16bab8-d6d1-45a4-87ee-90b52828b81b.jpg"
  summary="GitHub의 Dependabot 알림을 이제 Copilot, Claude, Codex와 같은 AI 코딩 에이전트에 할당하여 수정할 수 있습니다. 이를 통해 단순한 버전 업데이트 이상의 코드 변경이 필요한 취약점을 AI가 해결할 수 있게 되었습니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub의 Dependabot 알림을 이제 Copilot, Claude, Codex와 같은 AI 코딩 에이전트에 할당하여 수정할 수 있습니다. 이를 통해 단순한 버전 업데이트 이상의 코드 변경이 필요한 취약점을 AI가 해결할 수 있게 되었습니다.

---

## 5. 블록체인 뉴스

### 5.1 FDIC, GENIUS Act에 따른 스테이블코인 감독 체계를 새 건전성 규칙 제안으로 추진

{% include news-card.html
  title="FDIC, GENIUS Act에 따른 스테이블코인 감독 체계를 새 건전성 규칙 제안으로 추진"
  url="https://bitcoinmagazine.com/news/fdic-advances-stablecoin-oversight"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/04/FDIC-Advances-Stablecoin-Oversight-Framework-Under-GENIUS-Act-With-New-Prudential-Rule-Proposal.jpg"
  summary="FDIC가 GENIUS Act 하에 은행의 스테이블코인 발행 및 관리를 규정하는 새로운 건전성 규칙 제안을 발표했습니다. 이는 달러에 연동된 디지털 자산에 대한 연방 차원의 감독이 확대될 것을 시사합니다. 해당 소식은 Bitcoin Magazine를 통해 보도되었습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

FDIC가 GENIUS Act 하에 은행의 스테이블코인 발행 및 관리를 규정하는 새로운 건전성 규칙 제안을 발표했습니다. 이는 달러에 연동된 디지털 자산에 대한 연방 차원의 감독이 확대될 것을 시사합니다. 해당 소식은 Bitcoin Magazine를 통해 보도되었습니다.

---

### 5.2 Paolo Ardoino, Bitcoin 2026 연사로 확정

{% include news-card.html
  title="Paolo Ardoino, Bitcoin 2026 연사로 확정"
  url="https://bitcoinmagazine.com/conference/paolo-ardoino-confirmed-as-a-bitcoin-2026-speaker"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/04/Paolo-Ardoino.jpg"
  summary="Paolo Ardoino가 Bitcoin 2026 컨퍼런스의 스피커로 공식 확정되었습니다. Bitcoin Magazine가 이 소식을 발표했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Paolo Ardoino가 Bitcoin 2026 컨퍼런스의 스피커로 공식 확정되었습니다. Bitcoin Magazine가 이 소식을 발표했습니다.

---

### 5.3 FBI "2025년 미국 암호화폐 사기 규모 110억 달러 돌파, 기록 경신

{% include news-card.html
  title="FBI \”2025년 미국 암호화폐 사기 규모 110억 달러 돌파, 기록 경신"
  url="https://bitcoinmagazine.com/news/american-crypto-fraud-topped-11-billion"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/04/American-Crypto-Fraud-Topped-11-Billion-in-2025-Shattering-Records-FBI.jpg"
  summary="FBI에 따르면 2025년 미국에서 발생한 암호화폐 사기 피해액이 110억 달러를 넘어 기록을 경신했으며, 대부분은 투자 사기에서 비롯됐습니다. 이 소식은 Micah Zimmerman이 작성해 Bitcoin Magazine에 처음 게재되었습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

FBI에 따르면 2025년 미국에서 발생한 암호화폐 사기 피해액이 110억 달러를 넘어 기록을 경신했으며, 대부분은 투자 사기에서 비롯됐습니다. 이 소식은 Micah Zimmerman이 작성해 Bitcoin Magazine에 처음 게재되었습니다.

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [OpenTelemetry와 vmagent로 고용량 메트릭 파이프라인 구축하기](https://medium.com/airbnb-engineering/building-a-high-volume-metrics-pipeline-with-opentelemetry-and-vmagent-c714d6910b45?source=rss----53c7c27702d5---4) | Airbnb Engineering | StatsD 기반 대규모 메트릭 파이프라인을 OpenTelemetry와 Prometheus로 이전하는 프로덕션 검증 접근법을 소개합니다. 전체 쓰기 규모에서 병목 현상을 조기에 발견하고 대시보드 및 알림 검증을 위한 실제 데이터 기반 마이그레이션을 가능하게 합니다 |
| [Layers of your time : 토스와 함께한 시간을 기념하기](https://toss.tech/article/layers-of-your-time) | 토스 기술 블로그 | 팀원의 시간을 진심으로 축하하는 방법을 찾고 싶었어요. 8개월 동안 사내 굿즈를 다시 만들며 고민했던 과정과, 그 안에서 발견한 기준을 들려드려요 |
| [Pinterest 홈 피드에서의 다중 목표 최적화 진화](https://medium.com/pinterest-engineering/evolution-of-multi-objective-optimization-at-pinterest-home-feed-06657e33cd10?source=rss----4c5a5f6279b6---4) | Pinterest Engineering | Pinterest Home feed의 다중 목표 최적화 발전 과정을 소개하며, 피드 추천과 사용자-아이템 쌍의 확률 예측을 다루는 랭킹 모델이 일반적으로 별도로 처리된다고 설명합니다 |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **국가 배후 사이버 공격** | 1건 | APT28 DNS 하이재킹, SOHO 라우터 악용 |
| **컨테이너 보안** | 1건 | Docker CVE-2026-34040, AuthZ 우회 |
| **AI 플랫폼 & 비용** | 3건 | Claude Mythos, Bedrock Projects, Nova 2 Sonic |
| **DevOps 자동화** | 3건 | Copilot BYOK, Dependabot AI, Dynatrace 런타임 |
| **암호화폐 규제** | 2건 | FDIC 스테이블코인, FBI 사기 $11B |

이번 주기의 핵심 트렌드는 **AI 플랫폼 확장**(3건)과 **DevOps 자동화**(3건)입니다. Claude Mythos의 Vertex AI 출시, Bedrock Projects 비용 관리, Nova 2 Sonic 실시간 오디오 등 AI 플랫폼이 빠르게 확장되고 있으며, Copilot CLI의 BYOK 지원과 Dependabot의 AI 에이전트 할당 기능은 DevSecOps 워크플로우의 자동화를 가속화하고 있습니다. **보안** 측면에서는 APT28의 DNS 하이재킹과 Docker 인증 우회 취약점이 즉각적인 대응을 요구합니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **Docker CVE-2026-34040 인증 우회 취약점** 관련 Docker Engine 긴급 패치 및 AuthZ 플러그인 구성 점검

### P1 (7일 내)

- [ ] **러시아 국가 연계 APT28, 글로벌 DNS 하이재킹 캠페인에서 SOHO 라우터 악용** 관련 보안 검토 및 모니터링
- [ ] **[웨비나] AI가 기업 리스크를 악용하기 전에 2026년까지 아이덴티티 격차를 해소하는 방법** 관련 보안 검토 및 모니터링
- [ ] **Docker CVE-2026-34040으로 공격자 인증 우회 및 호스트 접근 권한 획득 가능** (CVE-2026-34040, CVE-2024-41110) 관련 보안 검토 및 모니터링
- [ ] **1,000개 이상의 노출된 ComfyUI 인스턴스가 크립토마이닝 봇넷 캠페인 표적됐다** 관련 보안 검토 및 모니터링
- [ ] **Amazon Nova 2 Sonic으로 실시간 대화형 팟캐스트 구축하기** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **Palantir의 프론트엔드 엔지니어링: Three.js의 플롯라인** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사

## DevSecOps 관점: 이번 주의 실무 시사점

오늘의 핵심은 Docker CVE-2026-34040 — `--authorization-plugin` 설정에서 특정 헤더 조합으로 AuthZ 결정을 우회하는 패턴이다. Docker Engine을 사용하는 조직 중 Twistlock·OPA·자체 AuthZ 플러그인을 신뢰 경계로 삼아 root 권한 컨테이너 실행을 통제하던 곳은, 이번 패치 적용 전까지 그 게이트가 **신뢰할 수 없는 상태**라고 간주해야 한다. 같은 날 보고된 ComfyUI 1,000+ 인스턴스 크립토마이너 봇넷 캠페인도 결국 동일한 실패 — 개발자 도구가 인증 없이 인터넷에 노출된 상태 — 의 다른 얼굴이다.

이번 주 작업할 일은 두 가지다. 첫째, `docker version --format '{{.Server.Version}}'` 으로 Engine 버전을 인벤토리하고, AuthZ 플러그인 사용 호스트에 한해 28.x 패치 적용을 P0로 올린다. 둘째, ComfyUI·Jupyter·MLflow 같은 ML 개발 UI 노출 여부를 `aws ec2 describe-security-groups --filters "Name=ip-permission.cidr,Values=0.0.0.0/0" --query 'SecurityGroups[*].[GroupId,IpPermissions[?FromPort==`8188`||FromPort==`5000`||FromPort==`8888`]]'` 로 즉시 스캔하라. APT28의 SOHO 라우터 캠페인이 가르치는 교훈도 같다 — 관리 인터페이스가 공용 인터넷에 노출된 상태로 방치되면 패치 적용 속도와 무관하게 자산은 적의 인프라가 된다.

이번 사건은 본 블로그의 [클라우드 보안 8기 7주차 — Docker·Kubernetes 보안 실습](https://tech.2twodragon.com/posts/2026/01/15/Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_Security_Practical_Guide/) 에서 다룬 컨테이너 권한 최소화·런타임 격리 원칙이 왜 게이트가 무너졌을 때의 마지막 방어선인지를 다시 보여준다. AuthZ 게이트가 우회된다 해도, `--cap-drop=ALL` 과 read-only rootfs·user namespace remapping이 적용된 컨테이너라면 호스트 takeover 의 폭은 현저히 줄어든다. 이번 주의 패치 작업과 별도로, "AuthZ를 통과해 들어온 컨테이너가 root 권한을 받을 수 있는가" 라는 질문을 다시 던질 가치가 있다.

## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [이란·북한 연계 해커, 한국 표적 다단계 공격·REvil: 주간 보안 다이제스트](/posts/2026/04/07/Tech_Security_Weekly_Digest_AI_Ransomware_Go_Palantir/) — 2026-04-07
- [Chaos 클라우드 변종·Masjesu IoT 봇넷·APT28 PRISMEX: 2026-04-09 보안 위클리 다이제스트](/posts/2026/04/09/Tech_Security_Weekly_Digest_Cloud_Botnet_AI_Malware/) — 2026-04-09
- [AWS LZA 컴플라이언스·npm 해킹·디바이스 코드 피싱: 주간 보안 다이제스트](/posts/2026/04/05/Tech_Security_Weekly_Digest_AWS_AI_Security_Malware/) — 2026-04-05

---

**작성자**: Twodragon
