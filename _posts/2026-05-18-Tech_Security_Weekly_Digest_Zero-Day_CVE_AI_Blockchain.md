---
layout: post
title: "2026년 05월 18일 주간 보안 다이제스트: 제로데이·랜섬웨어·악성코드 (6건)"
date: 2026-05-18 11:32:14 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Zero-Day, CVE, AI, Blockchain]
excerpt: "새로운 Windows 'MiniPlasma' 제로데이 익스플로잇 · NGINX CVE-2026-42945 실제 공격 발생이 부각된 2026년 05월 18일 보안 다이제스트 — 15건의 이슈와 실행 가능한 대응 액션을 정리합니다. 본문에서는 공격 경로·영향 평가·운영 환경 검증 절차까지 단계별로 다룹니다."
description: "2026년 05월 18일 보안 뉴스 요약. BleepingComputer, The Hacker News, 안랩 ASEC 블로그 등 15건을 분석하고 새로운 Windows 'MiniPlasma', NGINX CVE-2026-42945 실제 공격, 2026년 4월 APT 그룹 동향 보고서 등 DevSecOps 대응 포인트를 정리합니다."
keywords: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Zero-Day, CVE, AI]
author: Twodragon
comments: true
image: /assets/images/2026-05-18-Tech_Security_Weekly_Digest_Zero-Day_CVE_AI_Blockchain.svg
image_alt: "Windows 'MiniPlasma', NGINX CVE-2026-42945, 2026 4 APT - security digest overview"
toc: true
summary_card:
  title: "2026년 05월 18일 주간 보안 다이제스트: 제로데이·랜섬웨어·악성코드 (6건)"
  period: "2026년 05월 18일 (24시간)"
  audience: "보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트"
  categories:
    - { class: "security", label: "보안" }
    - { class: "devsecops", label: "DevSecOps" }
  tags:
    - "Security-Weekly"
    - "Zero-Day"
    - "CVE"
    - "AI"
    - "Blockchain"
    - "2026"
  highlights:
    - { source: "BleepingComputer", title: "새로운 Windows &#x27;MiniPlasma&#x27; 제로데이 익스플로잇, SYSTEM 권한 획득 및 PoC 공개" }
    - { source: "The Hacker News", title: "NGINX CVE-2026-42945 실제 공격 발생, 워커 크래시 및 잠재적 RCE 유발" }
    - { source: "안랩 ASEC 블로그", title: "2026년 4월 APT 그룹 동향 보고서" }
---

{% include ai-summary-card.html %}

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 05월 18일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

**수집 통계:**
- **총 뉴스 수**: 15개
- **보안 뉴스**: 5개
- **블록체인 뉴스**: 5개
- **기타 뉴스**: 5개

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | BleepingComputer | 새로운 Windows 'MiniPlasma' 제로데이 익스플로잇, SYSTEM 권한 획득 및 PoC 공개 | 🔴 Critical |
| 🔒 **Security** | The Hacker News | NGINX CVE-2026-42945 실제 공격 발생, 워커 크래시 및 잠재적 RCE 유발 | 🔴 Critical |
| 🔒 **Security** | 안랩 ASEC 블로그 | 2026년 4월 APT 그룹 동향 보고서 | 🟠 High |
| ⛓️ **Blockchain** | Cointelegraph | Bernstein, Figure의 1분기 실적이 블록체인 마켓플레이스의 독창성을 보여준다고 밝혀 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | Saylor가 BTC 매수 신호를 보내는 가운데, 소매 보유자들은 STRC 배당 투표 압박을 받다 | 🟡 Medium |
| ⛓️ **Blockchain** | Cointelegraph | SBI, Rakuten, Nomura, 암호화폐 투자 신탁 출시 준비 중: 보도 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | whichllm - 내 하드웨어에서 실제로 돌아가고 최고 성능을 내는 로컬 LLM 찾기 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | AI 구독은 엔터프라이즈의 시한폭탄 | 🟡 Medium |
| 💻 **Tech** | GeekNews (긱뉴스) | 2025년 4월 이후 5개 주에서 Flock 카메라 최소 25대가 파괴됨 | 🟡 Medium |

---

## 경영진 브리핑

- **긴급 대응 필요**: 새로운 Windows 'MiniPlasma' 제로데이 익스플로잇, SYSTEM 권한 획득 및 PoC 공개, NGINX CVE-2026-42945 실제 공격 발생, 워커 크래시 및 잠재적 RCE 유발 등 Critical 등급 위협 2건이 확인되었습니다.
- **주요 모니터링 대상**: 2026년 4월 APT 그룹 동향 보고서 등 High 등급 위협 1건에 대한 탐지 강화가 필요합니다.
- 랜섬웨어 관련 위협이 확인되었으며, 백업 무결성 검증과 복구 절차 리허설을 권고합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 위협 대응 | High | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |
| 탐지/모니터링 | High | SIEM/EDR 경보 우선순위 및 룰 업데이트 |
| 취약점 관리 | Critical | CVE 기반 패치 우선순위 선정 및 SLA 내 적용 |
| AI/ML 보안 | Medium | AI 서비스 접근 제어 및 프롬프트 인젝션 방어 점검 |

## 1. 보안 뉴스

### 1.1 새로운 Windows 'MiniPlasma' 제로데이 익스플로잇, SYSTEM 권한 획득 및 PoC 공개

{% include news-card.html
  title="새로운 Windows 'MiniPlasma' 제로데이 익스플로잇, SYSTEM 권한 획득 및 PoC 공개"
  url="https://www.bleepingcomputer.com/news/microsoft/new-windows-miniplasma-zero-day-exploit-gives-system-access-poc-released/"
  image="https://www.bleepstatic.com/content/hl-images/2021/09/20/Windows.jpg"
  summary="Windows에서 ”MiniPlasma”로 명명된 새로운 제로데이 권한 상승 취약점의 PoC(Proof-of-Concept) 익스플로잇이 공개되었습니다. 이 취약점은 완전히 패치된 Windows 시스템에서도 공격자에게 SYSTEM 권한을 부여할 수 있습니다."
  source="BleepingComputer"
  severity="Critical"
%}

# DevSecOps 관점: Windows 'MiniPlasma' 제로데이 취약점 분석

## 1. 기술적 배경 및 위협 분석

MiniPlasma는 Windows 커널 수준의 권한 상승 제로데이 취약점으로, 완전히 패치된 Windows 시스템에서도 공격자가 **SYSTEM 권한**을 획득할 수 있게 합니다. 이 취약점은 Windows 커널의 특정 객체 관리 메커니즘(예: GDI/GDI+ 또는 커널 풀 할당)에서 발생하는 것으로 추정되며, PoC(Proof-of-Concept) 코드가 공개되어 실질적인 위협이 임박했습니다.

주요 위협 요소:
- **로컬 권한 상승(LPE)**: 공격자가 이미 제한된 사용자 권한을 보유한 상태에서 SYSTEM 권한으로 전환 가능
- **전파 가능성**: PoC 공개로 인해 악성코드 및 랜섬웨어 제작자들이 빠르게 활용할 가능성 높음
- **영향 범위**: Windows 10, 11 및 Windows Server 계열(특정 빌드)에 영향

DevSecOps 관점에서는 **빌드 파이프라인**, **CI/CD 에이전트**, **컨테이너 호스트** 등 Windows 기반 인프라가 공격 표면이 될 수 있습니다.

## 2. 실무 영향 분석

- **CI/CD 환경 위험**: Jenkins, Azure DevOps 등 Windows 에이전트에서 빌드 실행 시, 공격자가 파이프라인을 통해 SYSTEM 권한을 획득하면 전체 인프라가 손상될 수 있음
- **컨테이너 보안**: Windows 컨테이너 호스트에서 이 취약점을 악용하면 호스트 시스템 제어권 상실
- **개발자 워크스테이션**: 로컬 개발 환경에서 PoC 실행 시 개발 머신이 랜섬웨어 등에 감염될 위험
- **모니터링 사각지대**: SYSTEM 권한 획득 후 공격자는 로그 삭제 및 EDR 우회 가능

## 3. 대응 체크리스트

- [ ] **Windows 업데이트 모니터링**: Microsoft의 긴급 보안 패치 발표 여부를 매일 확인하고, 패치 출시 시 24시간 내 테스트 환경에 적용 후 프로덕션 배포 일정 수립
- [ ] **최소 권한 원칙 강화**: CI/CD 에이전트 계정 및 서비스 계정에 불필요한 로컬 관리자 권한 제거, SYSTEM 권한이 필요한 작업을 최소화
- [ ] **엔드포인트 탐지 강화**: EDR/XDR 솔루션에서 MiniPlasma 관련 행위(특정 커널 호출 패턴, 비정상적인 토큰 조작)를 탐지하는 사용자 정의 규칙 추가
- [ ] **취약점 스캐닝 자동화**: 보안 스캐너(예: Nessus, Qualys)를 CI/CD 파이프라인에 통합하여 Windows 이미지 및 빌드 에이전트의 취약점을 주기적으로 점검
- [ ] **비상 대응 계획 수립**: PoC 악용 징후(예: SYSTEM 권한 획득 후 비정상 프로세스 실행) 발견 시 컨테이너/호스트 격리 절차 문서화 및 훈련


---

### 1.2 NGINX CVE-2026-42945 실제 공격 발생, 워커 크래시 및 잠재적 RCE 유발

{% include news-card.html
  title="NGINX CVE-2026-42945 실제 공격 발생, 워커 크래시 및 잠재적 RCE 유발"
  url="https://thehackernews.com/2026/05/nginx-cve-2026-42945-exploited-in-wild.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgdFtAiSRukEdQXVvEzXdQKy0O9SY7RCuqFLuAEIBe4rECuQuUS76qEXnxPuEcKIIFUysRNOGdBW2Mf2n1sh1W35aU0nCksWiW7v-20p1K7RhdPPDnxKh7kt_OmQaPrmtYPJ3larEwWr9iHeQMoRtlW767YpsXBFP5-5CQ2jTJUB_jWaMmt_29uLJvaGZE_/s1600/nginx.jpg"
  summary="NGINX Plus와 NGINX Open Source에서 발견된 CVE-2026-42945 (CVSS 9.2) 취약점이 공개 후 며칠 만에 실제 환경에서 악용되고 있으며, 이는 ngx_http_rewrite_module의 heap buffer overflow로 인해 worker crash 및 원격 코드 실행(RCE) 가능성이 있습니다."
  source="The Hacker News"
  severity="Critical"
%}

# DevSecOps 관점 NGINX CVE-2026-42945 분석

## 1. 기술적 배경 및 위협 분석

CVE-2026-42945는 NGINX의 `ngx_http_rewrite_module`에서 발생하는 힙 버퍼 오버플로우 취약점으로, CVSS 9.2의 치명적 등급을 받았다. 영향받는 버전은 0.6.27부터 1.30.0까지로, 거의 모든 현대 NGINX 배포판이 포함된다. 공격자는 특수하게 조작된 HTTP 요청을 전송하여 워커 프로세스를 크래시시키거나 원격 코드 실행(RCE)까지 유발할 수 있다. 특히 `rewrite` 지시어가 활성화된 환경에서 공격 표면이 넓어지며, 이미 야생에서 익스플로잇이 확인되어 패치 적용이 시급하다.

## 2. 실무 영향 분석

DevSecOps 관점에서 이 취약점은 **CI/CD 파이프라인 전반에 걸친 즉각적 대응**을 요구한다. NGINX는 로드밸런서, 리버스 프록시, API 게이트웨이로 광범위하게 사용되므로, 단일 인스턴스 장애가 서비스 전체 중단으로 이어질 수 있다. RCE 가능성은 내부망 측면 이동(Lateral Movement)의 위협도 내포한다. 컨테이너 환경(Kubernetes Ingress Controller, Docker)에서 NGINX를 사용하는 경우, 파드 재시작만으로는 근본 해결이 되지 않으며, 이미지 업데이트와 재배포가 필요하다. 또한, rewrite 모듈을 사용하지 않더라도 기본 모듈 로딩으로 인해 취약점에 노출될 수 있으므로, 모듈 비활성화보다는 패치 적용이 우선되어야 한다.

## 3. 대응 체크리스트

- [ ] 영향받는 NGINX 버전(0.6.27 ~ 1.30.0) 사용 여부를 모든 환경(프로덕션, 스테이징, 개발)에서 즉시 스캔 및 식별
- [ ] NGINX 최신 패치 버전(1.30.1 이상)으로 업데이트 또는 공식 보안 패치 적용 후, CI/CD 파이프라인을 통해 무중단 배포(Blue-Green, Rolling Update) 계획 수립
- [ ] `ngx_http_rewrite_module` 사용 여부 확인 및 불필요 시 모듈 비활성화 (`--without-http_rewrite_module`), 단 rewrite 규칙이 필요한 서비스는 패치 우선 적용
- [ ] WAF(Web Application Firewall) 규칙 업데이트 및 침입 탐지 시스템(IDS) 시그니처 추가로 익스플로잇 시도 차단 및 모니터링 강화
- [ ] 컨테이너 이미지(예: nginxinc/nginx-unprivileged, 공식 nginx 이미지) 베이스라인 업데이트 후, Kubernetes Ingress Controller 재배포 및 Helm 차트 버전 고정


#### MITRE ATT&CK 매핑

```yaml
mitre_attack:
  tactics:
    - T1203  # Exploitation for Client Execution
```

---

### 1.3 2026년 4월 APT 그룹 동향 보고서

{% include news-card.html
  title="2026년 4월 APT 그룹 동향 보고서"
  url="https://asec.ahnlab.com/ko/93743/"
  summary="목적 및 범위 본 보고서는 국가 지원을 받는 것으로 추정되는 국가 주도 위협 그룹의 사이버 간첩(Cyber Espionage)과 비밀 파괴공작(Sabotage) 활동을 다룬다. 금전적 이득 목적의 사이버 범죄 그룹은 제외했다"
  source="안랩 ASEC 블로그"
  severity="High"
%}

# DevSecOps 실무자 관점 APT 그룹 동향 분석 (2026년 4월)

## 1. 기술적 배경 및 위협 분석

해당 보고서는 국가 주도 APT 그룹의 사이버 간첩 및 파괴공작 활동을 다루며, 특히 북한 연계 그룹이 **개발자와 암호화폐 환경**을 집중 표적으로 삼고 있음을 시사한다. 이는 DevSecOps 환경에서 다음과 같은 기술적 위협으로 구체화된다:

- **공급망 공격 확대**: 개발자 워크스테이션, 패키지 레지스트리(npm, PyPI, Maven), CI/CD 파이프라인을 통한 악성코드 삽입 가능성 증가
- **암호화폐 인프라 표적화**: 스마트 계약 배포 파이프라인, 지갑 키 관리 시스템, 거래소 API 연동 구간에 대한 APT의 정밀 타격
- **개발자 신원 도용**: SSH 키, GPG 서명 키, 클라우드 액세스 토큰 탈취를 통한 인증 우회 및 지속적 침투

## 2. 실무 영향 분석

DevSecOps 실무자에게 이번 동향은 **파이프라인 보안 강화와 개발자 자산 보호**가 단순 컴플라이언스가 아닌 생존 문제임을 의미한다:

- **CI/CD 파이프라인 무결성 위협**: 빌드 단계에서의 코드 변조, 테스트 환경 오염, 배포 아티팩트 변조로 인한 프로덕션 침투 가능성
- **개발자 생태계 취약점**: IDE 플러그인, 오픈소스 라이브러리, 컨테이너 이미지 베이스 레이어 등 신뢰 체인 전반에 대한 검증 필요
- **암호화폐 관련 조직 특별 주의**: 키 관리 솔루션, 하드웨어 지갑 연동 파이프라인, 거래소 API 통합 구간의 보안 감사 필수

## 3. 대응 체크리스트

- [ ] CI/CD 파이프라인에 **서명 검증(Signature Verification)** 단계를 추가하고, 빌드 아티팩트 무결성 해시를 별도 저장소에 기록
- [ ] 개발자 워크스테이션에 **행위 기반 탐지(EDR)** 에이전트 설치 및 SSH 키/토큰 로테이션 정책을 90일 주기로 자동화
- [ ] 오픈소스 의존성 스캐닝 도구(SBOM 생성)를 모든 빌드에 포함하고, **취약점 데이터베이스와 APT 연계 IOC**를 교차 분석
- [ ] 암호화폐 관련 키 관리 시스템에 대해 **멀티 시그(Multi-sig)** 및 **하드웨어 보안 모듈(HSM)** 적용 여부를 분기별 감사
- [ ] 개발자 계정에 **지문 인증(FIDO2)** 또는 **하드웨어 보안 키** 기반 MFA를 강제하고, 비정상 로그인 시도 알림을 실시간 수신


---

## 2. 블록체인 뉴스

### 2.1 Bernstein, Figure의 1분기 실적이 블록체인 마켓플레이스의 독창성을 보여준다고 밝혀

{% include news-card.html
  title="Bernstein, Figure의 1분기 실적이 블록체인 마켓플레이스의 독창성을 보여준다고 밝혀"
  url="https://cointelegraph.com/news/bernstein-say-figures-q1-shows-uniqueness-of-blockchain-marketplaces?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy1pbWFnZXMuY3RtZWRpYS5pby9tZWRpYS9hcnRpY2xlLWNvdmVycy9waG9uZS1zY3JlZW4tZ2FsYXh5LXZpcnR1YWwtcmVhbGl0eTIyMjIyMS5qcGc=.jpg"
  summary="Bernstein 분석가들은 Figure Technology Solutions의 1분기 실적이 대부분의 대차대조표 기반 핀테크 대출 플랫폼과 차별화되는 blockchain 마켓플레이스의 독특함을 입증했다고 평가했습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

Bernstein 분석가들은 Figure Technology Solutions의 1분기 실적이 대부분의 대차대조표 기반 핀테크 대출 플랫폼과 차별화되는 blockchain 마켓플레이스의 독특함을 입증했다고 평가했습니다.

**실무 포인트**: 관련 DeFi 프로토콜의 스마트 컨트랙트 감사 현황과 비상 정지 메커니즘을 확인하세요.


---

### 2.2 Saylor가 BTC 매수 신호를 보내는 가운데, 소매 보유자들은 STRC 배당 투표 압박을 받다

{% include news-card.html
  title="Saylor가 BTC 매수 신호를 보내는 가운데, 소매 보유자들은 STRC 배당 투표 압박을 받다"
  url="https://cointelegraph.com/news/saylor-signals-btc-buy-as-retail-holders-get-push-on-strc-dividend-vote?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy1pbWFnZXMuY3RtZWRpYS5pby9tZWRpYS9hcnRpY2xlLWNvdmVycy9taWNoYWVsLXNheWxvcnMtYmlnLWJldC1pbnN0aXR1dGlvbmFsLWludmVzdG1lbnRzLXJvbGUtaW4tYml0Y29pbnMtcHJpY2UtMi5qcGc=.jpg"
  summary="Michael Saylor가 추가 비트코인 매수 의사를 밝히며, 소매 투자자들에게 STRC 배당금 지급을 위한 대리 투표 참여를 촉구했습니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

Michael Saylor가 추가 비트코인 매수 의사를 밝히며, 소매 투자자들에게 STRC 배당금 지급을 위한 대리 투표 참여를 촉구했습니다.

**실무 포인트**: 하드웨어 지갑 키 관리와 출금 서명 흐름을 재점검해 조작된 트랜잭션 승인 리스크를 차단하세요.


---

### 2.3 SBI, Rakuten, Nomura, 암호화폐 투자 신탁 출시 준비 중: 보도

{% include news-card.html
  title="SBI, Rakuten, Nomura, 암호화폐 투자 신탁 출시 준비 중: 보도"
  url="https://cointelegraph.com/news/sbi-rakuten-nomura-line-up-to-launch-crypto-investment-trusts-report?utm_source=rss_feed&utm_medium=rss&utm_campaign=rss_partner_inbound"
  image="https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy1pbWFnZXMuY3RtZWRpYS5pby9tZWRpYS9hcnRpY2xlLWNvdmVycy9oaS1ob3ctdG8tbGF1bmNoLWEtY3J5cHRvLXRva2VuLW9uLWEtZGVjZW50cmFsaXplZC1leGNoYW5nZS5qcGc=.jpg"
  summary="일본의 주요 증권사 SBI, Rakuten, Nomura가 2028년까지 암호화폐 보유 펀드를 공식 허용하는 규제 움직임에 맞춰 개인 투자자 대상 crypto investment trust 출시를 준비 중입니다."
  source="Cointelegraph"
  severity="Medium"
%}

#### 요약

일본의 주요 증권사 SBI, Rakuten, Nomura가 2028년까지 암호화폐 보유 펀드를 공식 허용하는 규제 움직임에 맞춰 개인 투자자 대상 crypto investment trust 출시를 준비 중입니다.

**실무 포인트**: 관련 프로토콜 및 스마트 컨트랙트 영향을 확인하세요.


---

## 3. 기타 주목할 뉴스

| 제목 | 출처 | 핵심 내용 |
|------|------|----------|
| [whichllm - 내 하드웨어에서 실제로 돌아가고 최고 성능을 내는 로컬 LLM 찾기](https://news.hada.io/topic?id=29613) | GeekNews (긱뉴스) | 파라미터 수가 아닌 실측 벤치마크 기반 으로 사용자 하드웨어에 맞는 로컬 LLM을 자동 추천하는 CLI 도구 GPU/CPU/RAM을 자동 감지하고 HuggingFace 모델 중 시스템에 맞는 상위 모델을 랭킹 으로 제시 NVIDIA, AMD, Apple Silicon, CPU-only 모두 지원 |
| [AI 구독은 엔터프라이즈의 시한폭탄](https://news.hada.io/topic?id=29612) | GeekNews (긱뉴스) | OpenAI, Anthropic, Google 등은 기업에 실제 제공 비용보다 낮은 구독 가격 을 제시해, 가격 조정 때 큰 비용 충격을 만들 수 있음 Claude Pro·ChatGPT Plus의 월 20달러 정액제는 고사용자의 실제 API 환산 비용이 좌석당 월 200~400달러까지 커질 수 있음 |
| [2025년 4월 이후 5개 주에서 Flock 카메라 최소 25대가 파괴됨](https://news.hada.io/topic?id=29611) | GeekNews (긱뉴스) | 미국 전역에서 Flock Safety 감시 카메라 절단·파손·해체가 이어지며, 2025년 4월 이후 5개 주에서 최소 25대가 파괴됨 La Mesa, Eugene·Springfield, Suffolk, Greenview, Lisbon에서 파손이 발생했고, 도시·교외와 민주당·공화당 성향 주를 모두 가로지름 Virginia Suffo |


---

## 4. 트렌드 분석

| 트렌드 | 관련 뉴스 수 | 주요 키워드 |
|--------|-------------|------------|
| **기타** | 12건 | 기타 주제 |
| **AI/ML** | 2건 | whichllm, AI 구독은 엔터프라이즈의 시한폭탄 |
| **제로데이** | 1건 | BleepingComputer 관련 동향 |

이번 주기의 핵심 트렌드는 **기타**(12건)입니다. **AI/ML** 분야에서는 whichllm, AI 구독은 엔터프라이즈의 시한폭탄 관련 동향에 주목할 필요가 있습니다.

---

## 실무 체크리스트

### P0 (즉시)

- [ ] **새로운 Windows 'MiniPlasma' 제로데이 익스플로잇, SYSTEM 권한 획득 및 PoC 공개** 관련 긴급 패치 및 영향도 확인
- [ ] **NGINX CVE-2026-42945 실제 공격 발생, 워커 크래시 및 잠재적 RCE 유발** (CVE-2026-42945) 관련 긴급 패치 및 영향도 확인

### P1 (7일 내)

- [ ] **2026년 4월 APT 그룹 동향 보고서** 관련 보안 검토 및 모니터링
- [ ] **Tycoon2FA, 디바이스 코드 피싱으로 Microsoft 365 계정 탈취** 관련 보안 검토 및 모니터링

### P2 (30일 내)

- [ ] 암호화폐/블록체인 관련 컴플라이언스 점검
## 참고 자료

| 리소스 | 링크 |
|--------|------|
| CISA KEV | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| MITRE ATT&CK | [attack.mitre.org](https://attack.mitre.org/) |
| FIRST EPSS | [first.org/epss](https://www.first.org/epss/) |

---

## 🔗 관련 포스트

<!-- related-posts:v1 -->

- [Funnel Builder Flaw, Microsoft, 중요한 Azure 취약점, 러시아 해커, Kazuar 백도어를 모듈형](/posts/2026/05/17/Tech_Security_Weekly_Digest_CVE_Vulnerability_Azure_Botnet/) — 2026-05-17
- [Cisco Catalyst SD-WAN, Stealer Backdoor가 개발자, ThreatsDay 게시판](/posts/2026/05/15/Tech_Security_Weekly_Digest_AI_Threat_AWS_Go/) — 2026-05-15
- [Turla, Kazuar 백도어를 모듈형 P2P, AWS AI 보안 프레임워크, 45일간의 자체 도구 모니터링이 실제 공격](/posts/2026/05/16/Tech_Security_Weekly_Digest_Botnet_AI_AWS_Security/) — 2026-05-16

---

**작성자**: Twodragon
