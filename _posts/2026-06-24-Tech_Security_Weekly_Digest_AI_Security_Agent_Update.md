---
layout: post
title: "2026년 06월 24일 주간 보안 다이제스트: AI 에이전트·패치·제로데이 (28건)"
date: 2026-06-24 09:31:18 +0900
last_modified_at: 2026-06-24T09:31:18+09:00
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Security, Agent, Update]
excerpt: "FortiBleed, 1억 1천만 개 자격 증명 수집 작전에서 · 가짜 AI 에이전트 스킬이 보안 검사를 통과해 26,000개가 부각된 2026년 06월 24일 보안 다이제스트 — 28건의 이슈와 실행 가능한 대응 액션을 정리합니다. 영향받는 자산 식별과 SBOM 기반 의존성 패치, EDR 룰 보강 가이드를 다룹니다."
description: "2026년 06월 24일 보안 뉴스 요약. The Hacker News, BleepingComputer 등 28건을 분석하고 FortiBleed, 1억 1천만 개 자격 증명, 가짜 AI 에이전트 스킬이 보안 검사를 통과해 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, AI, Security, Agent]
author: Twodragon
comments: true
image: /assets/images/2026-06-24-Tech_Security_Weekly_Digest_AI_Security_Agent_Update.svg
image_alt: "FortiBleed, 1 1, AI - security digest overview"
toc: true
summary_card:
  title: "2026년 06월 24일 주간 보안 다이제스트: AI 에이전트·패치·제로데이 (28건)"
  period: "2026년 06월 24일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "AI"
    - "Security"
    - "Agent"
    - "Update"
    - "2026"
  highlights:
    - { source: "The Hacker News", title: "FortiBleed, 1억 1천만 개 자격 증명 수집 작전에서 FortiGate 방화벽 표적" }
    - { source: "The Hacker News", title: "가짜 AI 에이전트 스킬이 보안 검사를 통과해 26,000개 에이전트에 도달한 것으로 알려져" }
    - { source: "The Hacker News", title: "트럼프 행정명령, 연방 양자내성암호 전환 시한 2030년으로 설정" }
    - { source: "Google Cloud Blog", title: "Log Analytics가 Observability Analytics로 변경: SQL로 로그와 트레이스 쿼리" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 06월 24일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 28개
- **보안 뉴스**: 5개
- **AI/ML 뉴스**: 5개
- **클라우드 뉴스**: 3개
- **DevOps 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | The Hacker News | FortiBleed, 1억 1천만 개 자격 증명 수집 작전에서 FortiGate 방화벽 표적 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 가짜 AI 에이전트 스킬이 보안 검사를 통과해 26,000개 에이전트에 도달한 것으로 알려져 | 🟡 Medium |
| 🔒 **Security** | The Hacker News | 트럼프 행정명령, 연방 양자내성암호 전환 시한 2030년으로 설정 | 🟡 Medium |
| 🤖 **AI/ML** | NVIDIA AI Blog | NVIDIA와 AWS, AI를 대규모로 프로덕션에 도입하기 위해 협력 | 🟡 Medium |
| 🤖 **AI/ML** | OpenAI Blog | GPT-5가 면역학자 Derya Unutmaz의 3년 된 미스터리 해결을 도왔다 | 🟡 Medium |
| 🤖 **AI/ML** | Meta Engineering Blo | Meta가 AI 글래스용 초박형 배터리를 설계한 방법 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | Log Analytics가 Observability Analytics로 변경: SQL로 로그와 트레이스 쿼리 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 검증 가능하고 프라이빗한 AI: Google Cloud, 기밀 컴퓨팅 영역 확장 | 🟡 Medium |
| ☁️ **Cloud** | Google Cloud Blog | 오픈 모델, 글로벌 네트워크: AT&T와 GSMA가 Gemma로 통신 혁신을 가속화하는 방법 | 🟡 Medium |
| ⚙️ **DevOps** | GitHub Changelog | Secret scanning이 Replicate 비밀에 대한 확장 메타데이터를 추가합니다 | 🟡 Medium |

---

## 경영진 브리핑

- **주요 모니터링 대상**: Craig Raw가 비트코인 최고의 지갑 중 하나를 무료로 만들었지만, Apple이 6월 30일까지 이를 막을 수도 있다 등 High 등급 위협 1건에 대한 탐지 강화가 필요합니다.
- 공급망 보안 위협이 확인되었으며, 서드파티 의존성 검토와 SBOM 업데이트를 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | Medium | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | High | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| 클라우드 보안 | Medium | 클라우드 자산 구성 드리프트 점검 및 권한 검토 |

## 1. 보안 뉴스

### 1.1 FortiBleed, 1억 1천만 개 자격 증명 수집 작전에서 FortiGate 방화벽 표적

{% include news-card.html
  title="FortiBleed, 1억 1천만 개 자격 증명 수집 작전에서 FortiGate 방화벽 표적"
  url="https://thehackernews.com/2026/06/fortibleed-targeted-fortigate-firewalls.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhJkhDD5qINhfAhBFXG2C13raQF6T6zAOmnHlArhnLUP5z0ifBzpyq6M_4n11cgynQfZW0mxJWnYU-TDYSpKQHYFHvXsZHCB7uoMFg0w02yZILY-JLMm2-uqm-CA_wIqZHhzl25FfO_lMd7dYm6VfprDP83bz_SoB3MWLEc059E4YCa554bba-qWHW5udHv/s1600/fortigate.jpg"
  summary="러시아어를 사용하는 금전적 동기의 초기 접근 중개자가 2026년 2월부터 전 세계 43만 대 이상의 FortiGate 방화벽을 대상으로 한 대규모 자격 증명 수집 작전 FortiBleed를 주도한 것으로 평가됩니다. 이 캠페인은 자격 증명 목록 수집, 노출된 서비스 검색, 접근 가능한 시스템에 대한 무차별 대입 공격, 맞춤형 도구 배포를 포함합니다."
  source="The Hacker News"
  severity="Medium"
%}

# FortiBleed 캠페인 분석: DevSecOps 실무자 관점

## 1. 기술적 배경 및 위협 분석

FortiBleed는 2026년 2월부터 활동한 러시아어 사용 IAB(Initial Access Broker) 그룹이 주도하는 대규모 자격증명 수집 캠페인입니다. 전 세계 43만 대 이상의 FortiGate 방화벽을 대상으로 하며, 약 1억 1천만 개의 자격증명을 수집한 것으로 추정됩니다. 공격 방식은 다음과 같습니다:

- **Credential harvesting**: 노출된 FortiGate 인터페이스에서 관리자 계정 정보 수집
- **Brute-force 공격**: 수집된 자격증명 리스트를 기반으로 무차별 대입 공격
- **맞춤형 악성코드 배포**: 시스템 접근 후 지속적인 제어를 위한 커스텀 툴 사용

특히 FortiGate는 네트워크 경계에 위치한 핵심 장비로, 침해 시 내부 네트워크 전체로의 측면 이동(lateral movement)이 가능해 위험도가 매우 높습니다. IAB는 획득한 접근 권한을 랜섬웨어 그룹 등에 재판매하는 비즈니스 모델을 갖고 있어, 이번 캠페인이 단순한 데이터 유출 이상의 연쇄 피해를 초래할 수 있습니다.

## 2. 실무 영향 분석

DevSecOps 실무자에게 이번 위협은 다음과 같은 직접적 영향을 미칩니다:

- **CI/CD 파이프라인 위험**: FortiGate가 인프라의 게이트웨이 역할을 하는 경우, 침해 시 파이프라인 접근 제어 우회 가능
- **자격증명 관리 체계 취약점 노출**: 하드코딩된 관리자 계정, 기본 비밀번호 사용 등이 주요 침해 경로로 활용됨
- **모니터링 체계 우회**: 방화벽 자체가 손상되면 로그 변조나 트래픽 필터링 우회가 가능해 탐지 회피
- **규제 준수 위험**: 금융, 의료 등 규제 산업에서 방화벽 침해는 GDPR, PCI DSS 위반으로 이어질 수 있음

특히 **2026년 2월부터 활동**한 점을 고려하면, 이미 침해된 환경이 존재할 가능성이 높아 신속한 대응이 필요합니다.

## 3. 대응 체크리스트

- [ ] **모든 FortiGate 장비의 펌웨어를 최신 버전으로 업데이트**하고, Fortinet 보안 권고사항(CVE 목록)을 즉시 확인
- [ ] **관리자 계정 자격증명 감사**: 기본 계정 비활성화, MFA(다중 인증) 강제 적용, 주기적 비밀번호 교체 정책 수립
- [ ] **노출된 인터페이스 차단**: 불필요한 HTTPS/SSH 관리 인터페이스를 외부에 노출하지 않도록 네트워크 ACL 재구성
- [ ] **비정상 로그인 시도 탐지 규칙 추가**: SIEM/SOAR에 FortiGate 로그 기반의 무차별 대입 공격 패턴 탐지 룰 배포
- [ ] **자격증명 순환 및 침해 지표(IoC) 검색**: FortiBleed 관련 IoC(IP, 해시, 도메인)를 기반으로 내부 환경 스캔 및 노출된 자격증명 즉시 변경

---

### 1.2 가짜 AI 에이전트 스킬이 보안 검사를 통과해 26,000개 에이전트에 도달한 것으로 알려져

{% include news-card.html
  title="가짜 AI 에이전트 스킬이 보안 검사를 통과해 26,000개 에이전트에 도달한 것으로 알려져"
  url="https://thehackernews.com/2026/06/fake-ai-agent-skill-passed-security.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgb14v3ddlfpybc15jRbk-cwHI-0S8BAzdp8Ix83L5ZCZ4AB8gCySG7J4tZr4od9q3Jbuic1a4J29VAvRcdSQag_-ju1o9ae9yCcL6XV_jRDVhgd31E5BljiThpXcfHu_gdsmSySY8o0WyjuUoSQ5CGOyKO3cKXVDYeGKa1b1up2VM5ZJE6_PjPNCVOD_M/s1600/skills.jpg"
  summary="보안 업체 AIR가 가짜 AI 에이전트 스킬을 제작해 유명 스킬 마켓플레이스와 Instagram 광고를 통해 유포한 결과, 일부 기업 계정을 포함해 약 26,000개의 에이전트에 도달했습니다. 이 스킬은 모든 보안 스캐너에서 안전하다고 판정받았으며, 실제로는 사용자 이메일 주소만 수집하는 무해한 페이로드였습니다. 이 실험은 현재 보안 검사 체계의 허점을 드"
  source="The Hacker News"
  severity="Medium"
%}

# DevSecOps 관점 분석: Fake AI Agent Skill 보안 스캔 우회 사건

## 1. 기술적 배경 및 위협 분석

본 사건은 AI 에이전트 스킬 마켓플레이스의 보안 검증 체계가 근본적으로 취약함을 드러낸다. AIR社가 제작한 악성 스킬은 기존 정적 분석 기반 스캐너를 모두 통과했으며, 실제로 26,000개 에이전트(기업 계정 포함)에 도달했다. 핵심 위협은 다음과 같다.

- **스캐너 우회 메커니즘**: 페이로드가 단순 이메일 수집 기능만 수행했지만, 실제 공격자는 난독화, 지연 실행, 조건부 트리거(예: 특정 시간/환경에서만 활성화)를 통해 탐지를 회피할 수 있다.
- **공급망 위험**: 마켓플레이스의 신뢰 모델이 깨졌다. 승인된 스킬이라도 실제 동작이 검증되지 않으면, 에이전트가 권한 상승, 데이터 유출, API 남용 등으로 이어질 수 있다.
- **기업 계정 노출**: 26,000개 에이전트 중 기업 계정이 포함된 점은 내부 데이터 유출, 크리덴셜 탈취, 랜섬웨어 전파 등으로 확장될 수 있는 심각한 시나리오를 시사한다.

## 2. 실무 영향 분석

DevSecOps 실무자에게 이 사건은 **AI 에이전트 보안을 기존 소프트웨어 공급망 보안(SBOM, 정적 분석)과 동일한 수준으로 취급해서는 안 된다**는 교훈을 준다.

- **CI/CD 파이프라인 변화 필요**: 기존 SAST/DAST 스캐너는 AI 스킬의 동적 행위(사용자 상호작용, 외부 API 호출 패턴)를 분석하지 못한다. 따라서 **런타임 모니터링**과 **행위 기반 분석**을 파이프라인에 통합해야 한다.
- **정책 기반 승인 체계**: 모든 스킬은 "최소 권한 원칙"에 따라 API 접근 범위, 데이터 수집 유형, 통신 대상이 명시되어야 하며, 이를 자동화된 정책 엔진으로 검증해야 한다.
- **사고 대응 시나리오 변경**: 기존 컨테이너/코드 취약점 대응과 달리, AI 에이전트는 자율적으로 행동할 수 있으므로 **에이전트 행위 로깅, 롤백 메커니즘, 격리 프로토콜**이 필요하다.

## 3. 대응 체크리스트

- [ ] **AI 에이전트 스킬 SBOM(소프트웨어 구성 명세서)에 행위 명세(Behavior Specification) 필수 포함**: 모든 API 호출, 데이터 수집 범위, 조건부 로직을 기계가 읽을 수 있는 형식(예: OPA 정책)으로 명시하고 CI 파이프라인에서 검증
- [ ] **샌드박스 기반 동적 분석 도입**: 스킬을 실제 환경과 격리된 샌드박스에서 실행하며, 네트워크 트래픽, 파일 시스템 접근, 사용자 데이터 수집 행위를 실시간 모니터링하고 이상 징후를 자동 차단
- [ ] **기업 계정용 AI 에이전트 스킬 사용 정책 강화**: 모든 서드파티 스킬은 승인 전 반드시 내부 보안팀의 수동 검토와 7일간의 행위 로그 분석 기간을 거쳐야 하며, 권한은 읽기 전용으로 제한
- [ ] **런타임 에이전트 행위 감사 및 자동 롤백 시스템 구축**: 에이전트가 승인되지 않은 API 호출, 예상치 못한 데이터 수집, 비정상적 통신 패턴을 보일 경우 즉시 격리하고 이전 버전으로 자동 롤백하는 메커니즘 구현

---

### 1.3 트럼프 행정명령, 연방 양자내성암호 전환 시한 2030년으로 설정

{% include news-card.html
  title="트럼프 행정명령, 연방 양자내성암호 전환 시한 2030년으로 설정"
  url="https://thehackernews.com/2026/06/trump-order-sets-2030-deadline-for.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhoC7KFWoDGkSi-UzAyKNUkw-Ogs4oy2tCOAYXiYAAkqEUC1WMotLAE1GUwoWApfXK3prWVctTP05aLGjru0hDBfJkZ1NzPiFeI1VObgSNCx4egTrYhKIUt4m1S14eQ6_GpdffFBL4Ak3Mgjw7UiiBethv1lmyd_OaPIfhk_b-zuMjxCHLZtih8Tk6MtRg/s1600/unitedstates.jpg"
  summary="트럼프 대통령이 6월 22일 행정명령에 서명하여 연방 기관들이 고가치 자산과 고영향 시스템을 post-quantum cryptography로 전환하도록 2030년 12월 31일(키 수립)과 2031년 12월 31일(디지털 서명)의 기한을 설정했습니다. EO 14409는 국가 안보 시스템을 별도 트랙으로 분리했으며, 이 기한은 아직 실현되지 않은 위협에 대비"
  source="The Hacker News"
  severity="Medium"
%}

# DevSecOps 실무자 관점에서 본 미국 연방 양자내성암호 전환 행정명령 분석

## 1. 기술적 배경 및 위협 분석

해당 행정명령(EO 14409)은 2030년까지 연방 기관의 고가치 자산과 고영향 시스템을 양자내성암호(PQC)로 전환하도록 강제합니다. 이는 **"지금 수집하고 나중에 해독(Store Now, Decrypt Later)"** 공격에 대응하기 위한 조치입니다. 양자 컴퓨터가 현재 RSA/ECC 기반 암호를 실용적으로 해독할 수 있는 능력을 갖추기 전에, 공격자들이 이미 암호화된 통신을 대량 수집하여 미래에 복호화할 수 있다는 위협이 현실화되고 있습니다. 특히 국가 안보 시스템은 별도 트랙으로 분리되어 더 엄격한 기준이 적용될 가능성이 높습니다.

## 2. 실무 영향 분석

DevSecOps 실무자에게 이번 행정명령은 다음과 같은 핵심 과제를 제기합니다:

- **CI/CD 파이프라인 전면 재설계**: 기존 TLS 인증서, 코드 서명, 패키지 서명에 사용된 RSA/ECC 알고리즘을 CRYSTALS-Kyber, Dilithium 등 NIST 표준 PQC 알고리즘으로 교체해야 합니다.
- **하이브리드 암호 체계 운영**: 전환 기간 동안 기존 시스템과 PQC를 병행 운영하는 하이브리드 모드가 필수적이며, 이는 인프라 복잡성을 크게 증가시킵니다.
- **소프트웨어 공급망 보안 강화**: SBOM(소프트웨어 자재 명세서)에 암호 알고리즘 정보를 포함하고, 모든 서드파티 라이브러리의 PQC 호환성을 검증해야 합니다.
- **성능 영향 평가**: PQC 알고리즘은 기존 대비 키 크기와 연산량이 크므로, API 게이트웨이, 로드밸런서 등 네트워크 장비의 처리량 변화를 사전 테스트해야 합니다.

## 3. 대응 체크리스트

- [ ] 현재 사용 중인 모든 암호 라이브러리와 TLS 구현체의 PQC 지원 여부를 인벤토리화하고, NIST SP 800-227(초안) 기준과의 갭 분석 수행
- [ ] CI/CD 파이프라인에 PQC 알고리즘 기반 테스트 환경을 구축하고, 기존 RSA/ECC와의 하이브리드 모드에서의 통합 테스트 자동화
- [ ] 코드 서명, 컨테이너 이미지 서명, Git 커밋 서명에 사용되는 키 관리 시스템을 PQC 호환 HSM/소프트웨어 모듈로 마이그레이션 계획 수립
- [ ] 외부 API 연동 파트너와의 PQC 전환 로드맵 협의 및 계약상 암호화 요구사항 업데이트
- [ ] 2028년까지 전체 시스템의 PQC 전환 현황을 모니터링할 수 있는 대시보드 구축 및 분기별 리스크 평가 프로세스 도입

---

## 2. AI/ML 뉴스

### 2.1 NVIDIA와 AWS, AI를 대규모로 프로덕션에 도입하기 위해 협력

{% include news-card.html
  title="NVIDIA와 AWS, AI를 대규모로 프로덕션에 도입하기 위해 협력"
  url="https://blogs.nvidia.com/blog/nvidia-aws-ai-production-scale/"
  image="https://blogs.nvidia.com/wp-content/uploads/2026/06/logo-lockup-tech-blog-aws-1920x1080-2-842x450.jpg"
  summary="NVIDIA와 AWS가 협력하여 AI 시스템의 대규모 프로덕션 배포를 위한 인프라를 제공합니다. 이 협력은 Amazon OpenSearch와 Amazon EC2 전반에서 NVIDIA AI 인프라를 활용하여 낮은 지연 시간의 추론, 빠른 벡터 검색, 강력한 GPU 가격 대비 성능을 지원합니다. 이를 통해 기업들은 운영 복잡성 증가 없이 확장 가능한 AI 배포"
  source="NVIDIA AI Blog"
  severity="Medium"
%}

#### 요약

NVIDIA와 AWS가 협력하여 AI 시스템의 대규모 프로덕션 배포를 위한 인프라를 제공합니다. 이 협력은 Amazon OpenSearch와 Amazon EC2 전반에서 NVIDIA AI 인프라를 활용하여 낮은 지연 시간의 추론, 빠른 벡터 검색, 강력한 GPU 가격 대비 성능을 지원합니다. 이를 통해 기업들은 운영 복잡성 증가 없이 확장 가능한 AI 배포 경로를 확보할 수 있습니다.

---

### 2.2 GPT-5가 면역학자 Derya Unutmaz의 3년 된 미스터리 해결을 도왔다

{% include news-card.html
  title="GPT-5가 면역학자 Derya Unutmaz의 3년 된 미스터리 해결을 도왔다"
  url="https://openai.com/index/gpt-5-immunology-mystery"
  summary="GPT-5 Pro가 면역학자 Derya Unutmaz의 3년간 미해결 과제를 해결하며 T cell 행동에 대한 통찰을 제공했다. 이 돌파구는 암 및 자가면역 연구를 지원할 가능성이 있다."
  source="OpenAI Blog"
  severity="Medium"
%}

#### 요약

GPT-5 Pro가 면역학자 Derya Unutmaz의 3년간 미해결 과제를 해결하며 T cell 행동에 대한 통찰을 제공했다. 이 돌파구는 암 및 자가면역 연구를 지원할 가능성이 있다.

---

### 2.3 Meta가 AI 글래스용 초박형 배터리를 설계한 방법

{% include news-card.html
  title="Meta가 AI 글래스용 초박형 배터리를 설계한 방법"
  url="https://engineering.fb.com/2026/06/23/production-engineering/how-meta-built-ultra-narrow-batteries-for-ai-glasses-meta-tech-podcast/"
  summary="Meta는 Ray-Ban Meta 및 Oakley Meta Vanguards 같은 AI 글래스의 얇은 안경다리에 카메라, 스피커, AI 작업 등을 구동할 충분한 에너지를 담기 위해 초소형 배터리를 엔지니어링했습니다."
  source="Meta Engineering Blog"
  severity="Medium"
%}

#### 요약

Meta는 Ray-Ban Meta 및 Oakley Meta Vanguards 같은 AI 글래스의 얇은 안경다리에 카메라, 스피커, AI 작업 등을 구동할 충분한 에너지를 담기 위해 초소형 배터리를 엔지니어링했습니다.

---

## 3. 클라우드 & 인프라 뉴스

### 3.1 Log Analytics가 Observability Analytics로 변경: SQL로 로그와 트레이스 쿼리

{% include news-card.html
  title="Log Analytics가 Observability Analytics로 변경: SQL로 로그와 트레이스 쿼리"
  url="https://cloud.google.com/blog/products/management-tools/query-logs-and-traces-with-sql-in-observability-analytics/"
  summary="Google Cloud Observability 제품군에서 Log Analytics가 Observability Analytics로 변경되었으며, 이제 SQL을 사용해 로그와 Trace 데이터를 쿼리할 수 있습니다. Trace 데이터는 일반 사용 가능(GA) 상태입니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Cloud Observability 제품군에서 Log Analytics가 Observability Analytics로 변경되었으며, 이제 SQL을 사용해 로그와 Trace 데이터를 쿼리할 수 있습니다. Trace 데이터는 일반 사용 가능(GA) 상태입니다.

---

### 3.2 검증 가능하고 프라이빗한 AI: Google Cloud, 기밀 컴퓨팅 영역 확장

{% include news-card.html
  title="검증 가능하고 프라이빗한 AI: Google Cloud, 기밀 컴퓨팅 영역 확장"
  url="https://cloud.google.com/blog/products/identity-security/verifiable-trust-in-the-ai-era-whats-new-in-confidential-computing/"
  image="https://storage.googleapis.com/gweb-cloudblog-publish/images/promt_encryption_diagram.max-1000x1000.png"
  summary="Google Cloud가 Confidential Computing 영역을 확장하며, AI 데이터 보호를 위해 하드웨어 기반 TEE(Trusted Execution Environment) 내에서 암호화된 데이터 무결성을 제공합니다. 이 혁신은 클라우드 AI 배포에서 검증 가능한 프라이버시를 강화합니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

Google Cloud가 Confidential Computing 영역을 확장하며, AI 데이터 보호를 위해 하드웨어 기반 TEE(Trusted Execution Environment) 내에서 암호화된 데이터 무결성을 제공합니다. 이 혁신은 클라우드 AI 배포에서 검증 가능한 프라이버시를 강화합니다.

---

### 3.3 오픈 모델, 글로벌 네트워크: AT&T와 GSMA가 Gemma로 통신 혁신을 가속화하는 방법

{% include news-card.html
  title="오픈 모델, 글로벌 네트워크: AT&T와 GSMA가 Gemma로 통신 혁신을 가속화하는 방법"
  url="https://cloud.google.com/blog/topics/telecommunications/open-models-global-networks-how-att-and-gsma-are-accelerating-innovation-with-gemma/"
  summary="AT&T와 GSMA는 Google의 Gemma 오픈 모델을 활용하여 통신 혁신을 가속화하고 있습니다. 통신 분야는 데이터 부족과 복잡한 멀티 벤더 환경이 AI 모델의 네트워크 이해에 큰 장애물이 되고 있습니다."
  source="Google Cloud Blog"
  severity="Medium"
%}

#### 요약

AT&T와 GSMA는 Google의 Gemma 오픈 모델을 활용하여 통신 혁신을 가속화하고 있습니다. 통신 분야는 데이터 부족과 복잡한 멀티 벤더 환경이 AI 모델의 네트워크 이해에 큰 장애물이 되고 있습니다.

---

## 4. DevOps & 개발 뉴스

### 4.1 Secret scanning이 Replicate 비밀에 대한 확장 메타데이터를 추가합니다

{% include news-card.html
  title="Secret scanning이 Replicate 비밀에 대한 확장 메타데이터를 추가합니다"
  url="https://github.blog/changelog/2026-06-23-secret-scanning-adds-extended-metadata-for-replicate-secrets"
  image="https://github.blog/wp-content/uploads/2026/06/571554102-6349f5b6-b0b7-4130-9300-6d5d87e0b6e9_70da3e.jpg"
  summary="GitHub의 Secret scanning이 Replicate secrets에 대한 확장 메타데이터를 추가하여 유출된 자격 증명에 대해 더 풍부한 컨텍스트를 제공합니다. 이제 이 패턴이 감지되면 확장 메타데이터가 포함되어 더 자세한 정보를 제공합니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub의 Secret scanning이 Replicate secrets에 대한 확장 메타데이터를 추가하여 유출된 자격 증명에 대해 더 풍부한 컨텍스트를 제공합니다. 이제 이 패턴이 감지되면 확장 메타데이터가 포함되어 더 자세한 정보를 제공합니다.

---

### 4.2 REST API를 통해 코드 품질 결과 가져오기

{% include news-card.html
  title="REST API를 통해 코드 품질 결과 가져오기"
  url="https://github.blog/changelog/2026-06-23-fetch-code-quality-findings-via-rest-api"
  image="https://github.blog/wp-content/uploads/2026/06/611418691-10e1f351-d85b-453b-bd17-3cf3ccec645f.jpg"
  summary="GitHub Blog에 따르면, 코드 품질 결과를 위한 Repository-level REST API가 공개 미리보기로 제공되며, GitHub UI에서 이미 사용 가능한 기능에 API 지원을 추가합니다. 두 개의 새로운 읽기 전용 엔드포인트가 포함됩니다."
  source="GitHub Changelog"
  severity="Medium"
%}

#### 요약

GitHub Blog에 따르면, 코드 품질 결과를 위한 Repository-level REST API가 공개 미리보기로 제공되며, GitHub UI에서 이미 사용 가능한 기능에 API 지원을 추가합니다. 두 개의 새로운 읽기 전용 엔드포인트가 포함됩니다.

---

### 4.3 SBOM이란 무엇이며, 왜 이것 없이는 배포할 수 없나요?

{% include news-card.html
  title="SBOM이란 무엇이며, 왜 이것 없이는 배포할 수 없나요?"
  url="https://www.docker.com/blog/what-is-an-sbom/"
  summary="Omdia의 2026년 소프트웨어 공급망 보안 보고서에 따르면 SBOM을 생성하는 조직의 73%가 취약점 완화 효율성 향상을 경험했지만, 86%는 여전히 생성 과정에 어려움을 겪고 있습니다. 이러한 인식된 가치와 운영상의 어려움 사이의 격차가 대부분의 팀이 직면한 문제입니다. 컨테이너화된 애플리케이션을 구축하고 보호하는 팀은 SBOM이 무엇인지 이해하는 것"
  source="Docker Blog"
  severity="Medium"
%}

#### 요약

Omdia의 2026년 소프트웨어 공급망 보안 보고서에 따르면 SBOM을 생성하는 조직의 73%가 취약점 완화 효율성 향상을 경험했지만, 86%는 여전히 생성 과정에 어려움을 겪고 있습니다. 이러한 인식된 가치와 운영상의 어려움 사이의 격차가 대부분의 팀이 직면한 문제입니다. 컨테이너화된 애플리케이션을 구축하고 보호하는 팀은 SBOM이 무엇인지 이해하는 것이 중요합니다.

---

## 5. 블록체인 뉴스

### 5.1 의회, 7월 17일 뉴욕에서 CLARITY Act 청문회 일정 확정

{% include news-card.html
  title="의회, 7월 17일 뉴욕에서 CLARITY Act 청문회 일정 확정"
  url="https://bitcoinmagazine.com/news/congress-schedules-clarity-act-hearing"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/Congress-Schedules-CLARITY-Act-Hearing-for-July-17-in-New-York.jpg"
  summary="미국 의회가 7월 17일 뉴욕에서 CLARITY Act 청문회를 개최할 예정이며, 암호화폐 시장 구조 법안에 대한 추진력이 커지고 있습니다. 이 소식은 Bitcoin Magazine을 통해 Micah Zimmerman이 보도했습니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

미국 의회가 7월 17일 뉴욕에서 CLARITY Act 청문회를 개최할 예정이며, 암호화폐 시장 구조 법안에 대한 추진력이 커지고 있습니다. 이 소식은 Bitcoin Magazine을 통해 Micah Zimmerman이 보도했습니다.

---

### 5.2 Craig Raw가 비트코인 최고의 지갑 중 하나를 무료로 만들었지만, Apple이 6월 30일까지 이를 막을 수도 있다

{% include news-card.html
  title="Craig Raw가 비트코인 최고의 지갑 중 하나를 무료로 만들었지만, Apple이 6월 30일까지 이를 막을 수도 있다"
  url="https://bitcoinmagazine.com/news/craig-raw-apple-might-kill-it-by-june-30"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/Craig-Raw-Built-One-of-Bitcoins-Best-Wallets-for-Free.-Apple-Might-Kill-It-by-June-30.jpg"
  summary="Craig Raw가 무료로 개발한 Bitcoin 지갑 Sparrow Wallet이 Apple의 개발자 계정 종료 위협에 직면했습니다. Apple은 가짜 Sparrow Wallet 사기 방지 앱을 제출한 Raw의 계정을 6월 30일자로 해지할 가능성이 있습니다. 이 소식은 Bitcoin Magazine을 통해 Micah Zimmerman이 보도했습니다."
  source="Bitcoin Magazine"
  severity="High"
%}

#### 요약

Craig Raw가 무료로 개발한 Bitcoin 지갑 Sparrow Wallet이 Apple의 개발자 계정 종료 위협에 직면했습니다. Apple은 가짜 Sparrow Wallet 사기 방지 앱을 제출한 Raw의 계정을 6월 30일자로 해지할 가능성이 있습니다. 이 소식은 Bitcoin Magazine을 통해 Micah Zimmerman이 보도했습니다.

---

### 5.3 Bull Bitcoin, 프랑스에서 MiCA 라이선스 획득, 완전한 자체 보관 및 프라이버시 기능 유지

{% include news-card.html
  title="Bull Bitcoin, 프랑스에서 MiCA 라이선스 획득, 완전한 자체 보관 및 프라이버시 기능 유지"
  url="https://bitcoinmagazine.com/business/bull-bitcoin-secures-mica-license-in-france-preserving-full-self-custody-and-privacy-features"
  image="https://bitcoinmagazine.com/wp-content/uploads/2026/06/thumbnail.webp"
  summary="Bull Bitcoin이 프랑스에서 MiCA 라이선스를 획득했으며, 창립자 Francis Pouliot는 자체 자금 조달로 3년 만에 이룬 성과라고 발표했습니다. 이 라이선스는 핵심 인프라를 아웃소싱하지 않고 PASSI 및 DORA 사이버 보안 감사를 통과하여 완전한 셀프 커스터디와 프라이버시 기능을 유지합니다."
  source="Bitcoin Magazine"
  severity="Medium"
%}

#### 요약

Bull Bitcoin이 프랑스에서 MiCA 라이선스를 획득했으며, 창립자 Francis Pouliot는 자체 자금 조달로 3년 만에 이룬 성과라고 발표했습니다. 이 라이선스는 핵심 인프라를 아웃소싱하지 않고 PASSI 및 DORA 사이버 보안 감사를 통과하여 완전한 셀프 커스터디와 프라이버시 기능을 유지합니다.

---

## 6. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [SNOW의 Automatic Sharding 도입기](https://d2.naver.com/helloworld/4394359) | 네이버 D2 | 네이버 사내 기술 교류 행사인 NAVER ENGINEERING DAY 2026(5월)에서 발표되었던 세션을 공개합니다. 발표 내용 수천 개의 서비스가 한정된 GPU 자원을 효율적으로 공유할 수 있도록 돕는 Automatic Sharding 기술을 소개하고, 모델 로딩 오버헤드를 제거하여 더 빠르고 안정적인 AI 모델 서빙 전략을 공유합니다 |
| [6. 도구를 넘어, 기준과 책임으로](https://toss.tech/article/technical-writing-6) | 토스 기술 블로그 | 도구와 자동화가 있어도, 무엇을 남기고 누가 책임지고 어떤 문서를 믿을지 정하는 기준과 책임이 없으면 문서화가 제대로 굴러가지 않아요. 그 빈자리를 메워간 과정을 담았습니다 |
| [5. Technical Writer, 사라질 결심](https://toss.tech/article/technical-writing-5) | 토스 기술 블로그 | TW의 암묵지를 AI에게 가르쳐서, 사람이 하던 글쓰기와 리뷰를 대신하게 만든 과정을 담았어요 |

---

## 7. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **AI/ML** | 7건 | The Hacker News 관련 동향, NVIDIA AI Blog 관련 동향, OpenAI Blog 관련 동향 |
| **기타** | 7건 | 기타 주제 |
| **클라우드 보안** | 2건 | NVIDIA AI Blog 관련 동향, Google Cloud Blog 관련 동향 |
| **인증 보안** | 1건 | The Hacker News 관련 동향 |

이번 주기의 핵심 트렌드는 **AI/ML**(7건)입니다. The Hacker News 관련 동향, NVIDIA AI Blog 관련 동향 등이 주요 이슈입니다. **기타**(7건)도 주목할 트렌드입니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **FortiBleed, 1억 1천만 개 자격 증명 수집 작전에서 FortiGate 방화벽 표적** 관련 보안 영향도 분석 및 모니터링 강화

### P1 (7일 내)

- [ ] **GitHub, actions/checkout 업데이트로 일반적인 Pwn Request 공격 패턴 차단** 관련 보안 검토 및 모니터링
- [ ] **Cisco Unified CM 취약점 CVE-2026-20230, 현재 공격에 악용 중** (CVE-2026-20230) 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] **NVIDIA와 AWS, AI를 대규모로 프로덕션에 도입하기 위해 협력** 관련 AI 보안 정책 검토
- [ ] 클라우드 인프라 보안 설정 정기 감사
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

**작성자**: Twodragon
