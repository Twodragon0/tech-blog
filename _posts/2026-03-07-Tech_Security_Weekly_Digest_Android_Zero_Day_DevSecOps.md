---

layout: post
title: "기술·보안 주간 다이제스트: Android 129개 취약점, DevSecOps 보안 부채, K8s 공격 급증"
date: 2026-03-07 12:00:00 +0900
categories: [security, devsecops]
tags: [Security-Weekly, DevSecOps, Cloud-Security, Weekly-Digest, 2026, Android, Zero-Day, Kubernetes, Supply-Chain]
excerpt: "기술·보안 주간 다이제스트: Android 129개 취약점, DevSecOps 보안 부채, K8s 공격 급증에서 확인된 주요 위협과 기술 변화를 운영 관점으로 요약하고, 보안팀·플랫폼팀이 바로 실행할 우선 대응 항목을 정리한 주간 다이제스트입니다."
description: "Google Android 129개 취약점 패치(Qualcomm 제로데이 CVE-2026-21385 활성 공격), VMware Aria Operations CVE-2026-22719 KEV 등재, Datadog DevSecOps 보고서(87% 조직 취약), VoidLink AI..."
author: Twodragon
comments: true
image: /assets/images/2026-03-07-Tech_Security_Weekly_Digest_Android_Zero_Day_DevSecOps.svg
image_alt: "Tech Security Weekly Digest March 07 2026 Android Zero Day DevSecOps"
toc: true
---
<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">기술·보안 주간 다이제스트 (2026년 03월 07일)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags"><span class="tag">Security-Weekly</span>
      <span class="tag">Android-Zero-Day</span>
      <span class="tag">DevSecOps-Report</span>
      <span class="tag">Kubernetes</span>
      <span class="tag">Supply-Chain</span>
      <span class="tag">2026</span></span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list"><li><strong>Android 129개 취약점 패치</strong>: Qualcomm 제로데이 CVE-2026-21385 활성 공격 확인, 234개 칩셋 영향</li>
      <li><strong>VMware Aria Operations 활성 공격</strong>: CVE-2026-22719 CISA KEV 등재, 인증 없이 임의 명령 실행</li>
      <li><strong>Datadog DevSecOps 보고서</strong>: 87% 조직이 운영 환경에 공격 가능한 취약점 보유, 의존성 평균 278일 지연</li>
      <li><strong>VoidLink K8s 악성코드</strong>: AI로 제작된 클라우드 네이티브 컨테이너 인식형 악성코드 프레임워크 확산</li></ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">수집 기간</span>
    <span class="summary-value">2026년 03월 07일 (24시간)</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

---

## 경영진 브리핑

- 모바일 제로데이, 가상화 인프라 취약점, 클라우드 네이티브 악성코드가 동시 관측되어 보안 운영 우선순위 재정렬이 필요합니다.
- 이번 주에는 패치 SLA 준수, 취약 자산 식별 자동화, 컨테이너 런타임 탐지 강화에 리소스를 집중해야 합니다.

## 위험 스코어카드

| 영역 | 현재 위험도 | 즉시 조치 |
|------|-------------|-----------|
| 모바일/엔드포인트 | High | Android 고위험 패치 강제, 취약 버전 정책 차단 |
| 인프라 취약점 | High | VMware/Cisco KEV 항목 우선 조치 및 검증 |
| 컨테이너/K8s 보안 | High | 런타임 탐지 정책 업데이트, 이미지 신뢰성 검증 |

## 실행 체크리스트

- [ ] Android/VMware/Cisco 고위험 자산 패치 상태 점검
- [ ] 인터넷 노출 자산 취약점 재스캔 및 결과 공유
- [ ] K8s 런타임 이상행위 탐지 룰 최신화
- [ ] CI/CD 의존성 보안 스캔 주기 단축
- [ ] 사고 대응 연락망 및 격리 절차 리허설

## 서론

안녕하세요, Twodragon입니다.

2026년 03월 07일 기준, 지난 24시간 동안 발표된 주요 기술 및 보안 뉴스를 심층 분석하여 정리했습니다.

> 관련 다이제스트: Cisco SD-WAN CVE-2026-20122, Tycoon 2FA 해체, GPT-5.4 출시 등은 [3월 6일 다이제스트](/2026/03/06/Tech_Security_Weekly_Digest_Security_Threat_AI_AWS/)에서 다루었습니다.

수집 통계:
- 총 뉴스 수: 20개 (큐레이션)
- 보안 뉴스: 8개
- DevSecOps 뉴스: 3개
- AI/ML 뉴스: 3개
- 클라우드/K8s 뉴스: 3개
- 블록체인 뉴스: 3개

---

## 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 보안 | Google/CISA | Android 129개 취약점 패치, Qualcomm 제로데이 CVE-2026-21385 활성 공격 | Critical |
| 보안 | CISA | VMware Aria Operations CVE-2026-22719 KEV 등재, 인증 없이 명령 실행 | Critical |
| 보안 | CISA/Tenable | Cisco SD-WAN CVE-2026-20127 인증 우회, Volt Typhoon 연계 의심 | Critical |
| 보안 | The Hacker News | APT28 MSHTML 제로데이 CVE-2026-21513, 우크라이나 표적 공격 | High |
| 보안 | Google TAG | 중국 사이버 첩보 GridTide 캠페인 차단, 42개국 53개 조직 표적 | High |
| 보안 | Microsoft | OAuth 스캠으로 정부 기관 표적, 악성 리디렉트 URL 활용 | High |
| DevSecOps | Datadog | DevSecOps 2026 보고서: 87% 조직 운영 환경에 공격 가능 취약점 보유 | High |
| DevSecOps | Help Net Security | CI/CD 파이프라인 자동 공격 캠페인, GitHub 토큰 유출 | High |
| AI/ML | SecurityWeek | AI 기반 공격 89% 증가, 에이전틱 AI 랜섬웨어 100배 빠른 유출 | High |
| 클라우드 | Cisco/Check Point | VoidLink: AI 제작 K8s 인식형 악성코드 프레임워크 | High |

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. 보안 뉴스

### 1.1 Google Android 3월 보안 업데이트: 129개 취약점 패치

{%- include news-card.html
  title="[보안] Google Android 3월 보안 업데이트: 129개 취약점 패치"
  url="https://thehackernews.com/2026/03/google-confirms-cve-2026-21385-in.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjR_pPCmiYZpBkIhumuW9B55rXBX7U9PZto5xPxHsLBbx5EstbqXgUI-XLZkQQV8OCsdaOi5RuSapl0V4LPKX9B_8MDBqSteyX83vXpj7G8-87BBhyphenhyphen75Os_0RhTFWBL_yxr7JVwXXtZ-qdbbugAlw9MoC5mFEx0hfQMncgnDRR8tLlEMXsLiPmim2sTjzNO/s1700-e365/android-exploit.jpg"
  summary="Google Android 3월 보안 업데이트: 129개 취약점 패치 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="The Hacker News"
  severity="Critical"
-%}


> 심각도: Critical | CVE: CVE-2026-21385, CVE-2026-0006

Google이 Android 역사상 최대 규모의 보안 업데이트를 배포했습니다. 총 129개 취약점이 수정되었으며, 이 중 10개는 Critical 등급입니다. 2018년 4월 이후 단일 월 기준 가장 많은 패치입니다.

핵심은 CVE-2026-21385(CVSS 7.8)로, Qualcomm 오픈소스 디스플레이 드라이버의 메모리 손상 취약점입니다. Google은 "제한적이고 표적화된 공격에 활용되고 있다"고 확인했으며, 234개 Qualcomm 칩셋이 영향을 받습니다. 보안 전문가들은 상업용 스파이웨어 업체가 언론인, 활동가, 정부 관료를 표적으로 이 취약점을 악용하고 있다고 분석합니다.

또한 CVE-2026-0006은 System 컴포넌트의 원격 코드 실행(RCE) 취약점으로, 추가 권한 없이 원격에서 악성 코드를 실행할 수 있습니다.

실무 대응:
- Android 보안 패치 레벨 `2026-03-05` 이상으로 즉시 업데이트
- MDM 정책으로 조직 내 Android 디바이스 패치 상태 모니터링
- Qualcomm 칩셋 기반 IoT/임베디드 장비도 펌웨어 업데이트 확인

#### 위협 분석

| 항목 | 내용 |
|------|------|
| CVE ID | CVE-2026-21385 |
| CVSS | 7.8 |
| 공격 벡터 | 로컬 (표적 공격) |
| 영향 | 메모리 손상, 권한 상승 |
| 대상 | 234개 Qualcomm 칩셋 |
| 심각도 | Critical |
| 대응 우선순위 | P0 - 즉시 업데이트 |

#### MITRE ATT&CK 매핑

- T1203 (Exploitation for Client Execution) -- 디스플레이 드라이버 취약점 악용
- T1068 (Exploitation for Privilege Escalation) -- 커널 레벨 권한 상승
- T1082 (System Information Discovery) -- 칩셋 정보 기반 표적 선별


---

### 1.2 VMware Aria Operations 명령 주입 취약점 활성 공격

{%- include news-card.html
  title="[보안] VMware Aria Operations 명령 주입 취약점 활성 공격"
  url="https://thehackernews.com/2026/03/cisa-adds-actively-exploited-vmware.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjwSnIflppBRH5X_FxN5pZcibA3-KyhW9iDiNGlD76L9B8dFwzLtP5i7FHFzf73XpTAhCLtmQn0JD_fUqgXceUlrCwPgJqbmlkPXi2e_IDggrIHDyJ5HoDzr191LxAbe08arokXZ4FXH5k9NxErepVgiaEkGVfWDWQ2ZWJ8h3mGjySQ-QqTzo02oBdh01Up/s1700-e365/vmware.jpg"
  summary="VMware Aria Operations 명령 주입 취약점 활성 공격 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="The Hacker News"
  severity="Critical"
-%}


> 심각도: Critical | CVE: CVE-2026-22719

CISA가 VMware Aria Operations의 명령 주입 취약점 CVE-2026-22719(CVSS 8.1)를 KEV(Known Exploited Vulnerabilities) 카탈로그에 등재했습니다. 이 취약점은 인증되지 않은 공격자가 임의의 운영 체제 명령을 실행할 수 있게 합니다.

Aria Operations는 VMware 가상화 인프라의 성능 및 용량 관리 핵심 도구이므로, 침해 시 전체 vSphere 환경의 가시성과 제어권이 위험에 노출됩니다.

실무 대응:
- FCEB 기관: 2026년 3월 24일까지 패치 의무 적용
- VMware Aria Operations 긴급 업데이트 적용
- Aria Operations 인스턴스의 네트워크 접근 제한 (관리 네트워크로 격리)

#### MITRE ATT&CK 매핑

- T1059 (Command and Scripting Interpreter) -- 임의 명령 실행
- T1190 (Exploit Public-Facing Application) -- 인증 없이 외부 노출 서비스 공격


---

### 1.3 Cisco SD-WAN 인증 우회 제로데이 (CVE-2026-20127)

{%- include news-card.html
  title="[보안] Cisco SD-WAN 인증 우회 제로데이 (CVE-2026-20127)"
  url="https://www.tenable.com/blog/cve-2026-20127-cisco-catalyst-sd-wan-controllermanager-zero-day-authentication-bypass"
  image="https://www.tenable.com/sites/default/files/styles/640x360/public/images/articles/FAQ-advisory-zero-day_2.png?itok=xDtxGvoM"
  summary="Cisco SD-WAN 인증 우회 제로데이 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Tenable"
  severity="Critical"
-%}


> 심각도: Critical | CVE: CVE-2026-20127

Cisco Catalyst SD-WAN Controller/Manager에서 인증 우회 취약점이 발견되어 실제 공격에 활용되고 있습니다. 원격의 인증되지 않은 공격자가 조작된 요청을 보내 고권한 사용자로 로그인할 수 있습니다.

CISA는 긴급 지시문 ED 26-03을 발령하여 Cisco SD-WAN 시스템의 즉각적인 조치를 명령했습니다. Volt Typhoon 그룹이 과거 Cisco 장비를 악용한 이력이 있어, 이번 취약점과의 연관성에 주의가 필요합니다.

실무 대응:
- CISA ED 26-03에 따른 즉시 패치 적용
- SD-WAN Controller/Manager 접근 로그 긴급 검토
- 비인가 관리자 계정 생성 여부 확인

#### 위협 분석

| 항목 | 내용 |
|------|------|
| CVE ID | CVE-2026-20127 |
| 공격 벡터 | 네트워크 (인증 불필요) |
| 영향 | 고권한 인증 우회 |
| 연관 위협 | Volt Typhoon (중국 APT) |
| CISA 지시 | ED 26-03 긴급 지시문 |
| 대응 우선순위 | P0 - 즉시 대응 |


---

### 1.4 APT28 MSHTML 제로데이 악용 확인 (CVE-2026-21513)

{%- include news-card.html
  title="[보안] APT28 MSHTML 제로데이 악용 확인 (CVE-2026-21513)"
  url="https://thehackernews.com/2026/03/apt28-tied-to-cve-2026-21513-mshtml-0.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEgGmBYExYY-MdqirvtI7-k2gWDf2rCE5AX4J246DywytJU0hWklJfAxRUKUa6AhU-VFWf2jazsAR1DkpPBHUqv2LsGckfxhVUebrMsnAccaYYmp2L9VJDz4rHaRLxKRgXaYM-UPcFS_ZoyveJxkLu1RunwaIuCBckILFDzMo1mCZtg9zaOmXrOSEEWU7RSg/s1700-e365/windows.jpg"
  summary="APT28 MSHTML 제로데이 악용 확인 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="The Hacker News"
  severity="Critical"
-%}


> 심각도: High | CVE: CVE-2026-21513

러시아 연계 APT28(Fancy Bear)이 Microsoft MSHTML 프레임워크의 보안 기능 우회 취약점 CVE-2026-21513(CVSS 8.8)을 2월 패치 전부터 제로데이로 악용한 것이 확인되었습니다.

이 취약점은 Microsoft의 2026년 2월 Patch Tuesday에서 수정되었지만, 패치 전 우크라이나를 표적으로 한 실제 공격에 사용되었습니다.

실무 대응:
- 2026년 2월 Windows 보안 업데이트 미적용 시 즉시 패치
- MSHTML 관련 탐지 규칙 추가 (특히 Mark-of-the-Web 우회 시도)
- 우크라이나 관련 조직은 APT28 IoC 긴급 점검


---

### 1.5 Google, 중국 사이버 첩보 캠페인 GridTide 차단

{%- include news-card.html
  title="[보안] Google, 중국 사이버 첩보 캠페인 GridTide 차단"
  url="https://www.cybersecurity-review.com/news-march-2026/"
  summary="Google, 중국 사이버 첩보 캠페인 GridTide 차단 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Cybersecurity News"
  severity="High"
-%}


> 심각도: High

Google이 42개국 53개 조직을 표적으로 한 대규모 중국 사이버 첩보 캠페인을 차단했습니다. GridTide 악성코드를 사용한 이 캠페인은 정부, 국방, 기술 분야를 주로 공격했습니다.

실무 대응:
- Google TAG가 공개한 GridTide IoC 기반 네트워크 스캔
- 외부 노출 서비스의 비정상 트래픽 패턴 점검
- APT 수준의 위협에 대비한 EDR/NDR 탐지 규칙 업데이트


---

### 1.6 악성 PHP 패키지: 크로스 플랫폼 RAT 배포

{%- include news-card.html
  title="[보안] 악성 PHP 패키지: 크로스 플랫폼 RAT 배포"
  url="https://thehackernews.com/"
  image="https://thehackernews.com/images/-AaptImXE5Y4/WzjvqBS8HtI/AAAAAAAAxSs/BcCIwpWJszILkuEbDfKZhxQJwOAD7qV6ACLcBGAs/s728-e365/the-hacker-news.jpg"
  summary="악성 PHP 패키지: 크로스 플랫폼 RAT 배포 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="The Hacker News"
  severity="High"
-%}


> 심각도: High

Packagist PHP 패키지 레지스트리에서 Laravel 유틸리티로 위장한 악성 패키지가 발견되었습니다. Windows, macOS, Linux 모두에서 작동하는 크로스 플랫폼 RAT(원격 접근 트로이목마)를 배포하며, 발견 시점에도 여전히 다운로드 가능했습니다.

실무 대응:
- 프로젝트의 Composer 의존성 감사 (`composer audit`)
- 최근 추가된 Laravel 관련 패키지의 출처와 다운로드 수 확인
- CI/CD 파이프라인에 패키지 출처 검증 단계 추가


---

### 1.7 Microsoft OAuth 스캠: 정부 기관 표적 공격

{%- include news-card.html
  title="[보안] Microsoft OAuth 스캠: 정부 기관 표적 공격"
  url="https://www.microsoft.com/en-us/security/blog/"
  image="https://www.microsoft.com/en-us/security/blog/wp-content/uploads/2018/08/cropped-microsoft_logo_element.png"
  summary="Microsoft OAuth 스캠: 정부 기관 표적 공격 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Microsoft Security"
  severity="High"
-%}


> 심각도: High

Microsoft가 OAuth 남용 스캠에 대해 경고했습니다. 피싱 이메일과 URL 리디렉트를 활용하여 피해자의 시스템에 악성코드를 설치하며, 주로 정부 및 공공 부문 조직을 표적으로 합니다.

실무 대응:
- Azure AD/Entra ID의 OAuth 앱 동의 정책 강화
- 관리자 동의 워크플로우 활성화
- 비정상 OAuth 앱 등록/권한 부여 모니터링


---

### 1.8 보복성 핵티비스트 공격 급증: Epic Fury 이후

{%- include news-card.html
  title="[보안] 보복성 핵티비스트 공격 급증: Epic Fury 이후"
  url="https://thehackernews.com/"
  image="https://thehackernews.com/images/-AaptImXE5Y4/WzjvqBS8HtI/AAAAAAAAxSs/BcCIwpWJszILkuEbDfKZhxQJwOAD7qV6ACLcBGAs/s728-e365/the-hacker-news.jpg"
  summary="보복성 핵티비스트 공격 급증: Epic Fury 이후 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="The Hacker News"
  severity="High"
-%}


> 심각도: Medium

미국-이스라엘 합동 군사 작전(Epic Fury/Roaring Lion) 이후 보복성 핵티비스트 활동이 급증했습니다. Radware에 따르면, Keymous+와 DieNet 두 그룹이 2월 28일-3월 2일 사이 전체 공격의 약 70%를 수행했습니다.

실무 대응:
- DDoS 완화 서비스 확인 및 임계값 조정
- 중동 관련 서비스 운영 조직은 WAF 규칙 강화
- 핵티비스트 그룹 IoC 모니터링


---

![DevSecOps Section Banner](/assets/images/section-devsecops.svg)

## 2. DevSecOps 뉴스

### 2.1 Datadog DevSecOps 2026 보고서: 87% 조직이 공격 가능 취약점 보유

{%- include news-card.html
  title="Datadog DevSecOps 2026 보고서: 87% 조직이 공격 가능 취약점 보유"
  url="https://www.helpnetsecurity.com/2026/03/02/devsecops-supply-chain-risk-security-debt/"
  image="https://img.helpnetsecurity.com/wp-content/uploads/2024/01/19155548/devsecops-1400.jpg"
  summary="Datadog DevSecOps 2026 보고서: 87% 조직이 공격 가능 취약점 보유 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Help Net Security"
  severity="High"
-%}


> 심각도: High

Datadog의 State of DevSecOps 2026 보고서가 발표되었습니다. 조사 대상 조직의 87%가 운영 환경에서 하나 이상의 공격 가능한 취약점을 실행하고 있으며, 서비스의 40%가 영향을 받습니다.

핵심 수치:
- Java 서비스의 59%에 공격 가능한 취약점 존재 (.NET 47%, Rust 40%)
- 의존성은 최신 버전 대비 평균 278일 지연 (작년 215일에서 악화)
- Java는 492일 지연으로 가장 심각
- EOL(지원 종료) 런타임 사용: 서비스의 10% (Go 23%, PHP 13%)
- 월 1회 미만 배포 조직은 매일 배포 조직보다 70% 더 많은 오래된 라이브러리 보유

실무 대응:
- SCA(Software Composition Analysis) 도구로 운영 환경 의존성 감사
- 배포 빈도 증가가 보안 부채 감소에 직접적 연관 -- CI/CD 자동화 강화
- EOL 런타임 사용 현황 파악 및 업그레이드 계획 수립


---

### 2.2 CI/CD 파이프라인 자동 공격 캠페인

{%- include news-card.html
  title="CI/CD 파이프라인 자동 공격 캠페인"
  url="https://www.helpnetsecurity.com/2026/03/02/devsecops-supply-chain-risk-security-debt/"
  image="https://img.helpnetsecurity.com/wp-content/uploads/2024/01/19155548/devsecops-1400.jpg"
  summary="CI/CD 파이프라인 자동 공격 캠페인 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Help Net Security"
  severity="High"
-%}


> 심각도: High

주요 오픈소스 리포지토리를 대상으로 한 1주일간의 자동화된 CI/CD 파이프라인 공격이 보고되었습니다. hackerbot-claw라는 자율 봇이 5가지 익스플로잇 기법을 사용하여 GitHub에서 가장 인기 있는 리포지토리 중 하나에서 쓰기 권한이 있는 GitHub 토큰을 유출하는 데 성공했습니다.

실무 대응:
- GitHub Actions 워크플로우에서 `permissions` 블록으로 최소 권한 적용
- `GITHUB_TOKEN` 권한을 `read-only`로 기본 설정
- 서드파티 Actions의 커밋 SHA 고정 (태그 대신)
- 워크플로우 실행 로그에서 비정상 토큰 사용 모니터링


---

### 2.3 코드 서명 인증서 유효기간 460일로 제한

{%- include news-card.html
  title="코드 서명 인증서 유효기간 460일로 제한"
  url="https://devops.com/three-encryption-resolutions-for-devsecops-in-2026/"
  image="https://devops.com/wp-content/uploads/2020/08/Overheard-at-CloudBees-Connect-The-Reality-of-Delivering-Modern-Software.jpg"
  summary="코드 서명 인증서 유효기간 460일로 제한 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="DevOps.com"
  severity="Medium"
-%}


> 심각도: Medium

2026년 3월 1일부터 CA/B Forum 규정에 따라 코드 서명 인증서의 최대 유효기간이 460일로 제한됩니다. 공급망 공격이 증가하고 AI 기반 위협이 확대되면서, DevSecOps 팀은 CI/CD 보안을 강화하고 인증서 갱신 자동화가 필수가 되었습니다.

실무 대응:
- 코드 서명 인증서 만료일 확인 및 자동 갱신 파이프라인 구축
- cert-manager 또는 HashiCorp Vault PKI로 자동화
- 인증서 만료 30일 전 알림 설정


---

![AI Section Banner](/assets/images/section-ai.svg)

## 3. AI/ML 뉴스

### 3.1 AI 기반 사이버 공격 89% 증가

{%- include news-card.html
  title="[AI/ML] AI 기반 사이버 공격 89% 증가"
  url="https://www.securityweek.com/cyber-insights-2026-malware-and-cyberattacks-in-the-age-of-ai/"
  image="https://www.securityweek.com/wp-content/uploads/2026/02/malware-cyber-insights-2026.jpg"
  summary="AI 기반 사이버 공격 89% 증가 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="SecurityWeek"
  severity="High"
-%}


> 심각도: High

2026년 3월 기준, AI 기반 사이버 공격이 89% 증가했습니다. 피싱, 딥페이크 캠페인, 자격 증명 탈취에 AI가 적극적으로 활용되고 있으며, 아이덴티티 위협(API 자격 증명 남용, 내부자 위협)이 대부분의 데이터 유출 원인을 차지합니다.

특히 위험한 것은 에이전틱 AI의 등장입니다. 기존 도구와 달리, 에이전틱 AI는 네트워크 방어에 적응하고, 공격 중 페이로드를 변경하며, 탐지 응답으로부터 학습할 수 있습니다. 통제된 테스트에서 AI 기반 랜섬웨어가 인간 공격자보다 100배 빠른 데이터 유출을 달성했습니다.

실무 대응:
- AI 기반 피싱 탐지 도구 도입 (기존 패턴 매칭만으로 부족)
- 딥페이크 기반 소셜 엔지니어링에 대비한 다단계 인증 절차 강화
- 아이덴티티 및 횡적 이동 가시성 확보가 핵심 방어선


---

### 3.2 AI가 DevSecOps를 재편: PR 병합 98% 증가

{%- include news-card.html
  title="[AI/ML] AI가 DevSecOps를 재편: PR 병합 98% 증가"
  url="https://www.computerweekly.com/news/366639364/How-AI-code-generation-is-pushing-DevSecOps-to-machine-speed"
  image="https://www.computerweekly.com/visuals/ComputerWeekly/HeroImages/security-code-encryption-gonin-adobe.jpg"
  summary="AI가 DevSecOps를 재편: PR 병합 98% 증가 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Computer Weekly"
  severity="Medium"
-%}


> 심각도: Medium

AI를 활용하는 개발자는 98% 더 많은 PR을 병합하고 있습니다. 보안 팀에게 이 속도는 복합적인 문제를 만듭니다. 코드가 더 많고, 더 빠르게 생산되며, 리뷰할 시간은 줄어듭니다.

JFrog은 AI 모델을 소프트웨어 아티팩트와 동일한 수준으로 관리하는 플랫폼 확장을 발표하여, DevSecOps, MLOps, 거버넌스를 하나의 플랫폼으로 통합합니다.

실무 대응:
- AI 생성 코드에 대한 자동 보안 스캔 파이프라인 필수
- SAST/SCA 도구를 PR 수준에서 게이트로 설정
- AI 모델 아티팩트도 SBOM에 포함


---

### 3.3 랜섬웨어 생태계의 구조적 변화

{%- include news-card.html
  title="[AI/ML] 랜섬웨어 생태계의 구조적 변화"
  url="https://www.recordedfuture.com/blog/ransomware-tactics-2026"
  image="https://www.recordedfuture.com/blog/media_13d33e30a4d6ff2bf805413e36ff4532517bc417e.png?width=1200&format=pjpg&optimize=medium"
  summary="랜섬웨어 생태계의 구조적 변화 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Recorded Future"
  severity="High"
-%}


> 심각도: High

랜섬웨어 공격은 2025년 7,200건으로 전년 대비 47% 증가했지만, 수익은 감소했습니다. LockBit과 RansomHub가 사라진 후 Akira(16%), Qilin(16%), DragonForce(5%)가 부상했습니다.

Recorded Future는 2026년을 러시아 외 지역 랜섬웨어 조직이 러시아 내 조직 수를 처음으로 초과하는 해로 예측합니다. 전술도 변화하여, 암호화 대신 데이터 탈취와 AI 딥페이크를 결합한 "심리적 랜섬웨어" 방식이 확산되고 있습니다.

실무 대응:
- 암호화보다 데이터 유출 방지(DLP)에 초점
- 백업만으로 부족 -- 데이터 유출 탐지 및 차단 역량 강화
- 공격자의 표준화된 플레이북을 역이용하여 허니팟/디코이 배치


---

![Cloud Section Banner](/assets/images/section-cloud.svg)

## 4. 클라우드/K8s 뉴스

### 4.1 VoidLink: AI로 제작된 K8s 인식형 악성코드

{%- include news-card.html
  title="[클라우드] VoidLink: AI로 제작된 K8s 인식형 악성코드"
  url="https://blogs.cisco.com/security/voidlink-ai-built-malware-and-the-future-of-workload-security"
  summary="VoidLink: AI로 제작된 K8s 인식형 악성코드 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Cisco Security Blog"
  severity="High"
-%}


> 심각도: High

Check Point Research가 공개한 VoidLink는 클라우드 네이티브 환경에 특화된 악성코드 프레임워크입니다. AWS, GCP, Azure, Alibaba, Tencent 환경을 탐지하고, Docker 컨테이너와 Kubernetes 포드 내부에서 동작하는지 판별하여 행위를 자동으로 조정합니다.

이는 공격자가 클라우드 네이티브, 컨테이너 인식형, AI 가속 공격 프레임워크를 구축하는 새로운 단계에 진입했음을 의미합니다.

실무 대응:
- 런타임 컨테이너 보안 도구 배포 (Falco, Sysdig Secure)
- Pod Security Standards 적용 (`restricted` 프로필)
- K8s RBAC 최소 권한 원칙 검토 및 서비스 어카운트 감사

#### MITRE ATT&CK 매핑 (Containers)

- T1610 (Deploy Container) -- 악성 컨테이너 배포
- T1613 (Container and Resource Discovery) -- 클라우드/K8s 환경 탐지
- T1611 (Escape to Host) -- 컨테이너 탈출 시도


---

### 4.2 Kubernetes 공격 도구 급증

{%- include news-card.html
  title="[클라우드] Kubernetes 공격 도구 급증"
  url="https://dev.to/deepseax/kubernetes-cluster-attacks-surge-in-2026-how-to-harden-your-k8s-foo"
  image="https://media2.dev.to/dynamic/image/width=1200,height=627,fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads.s3.amazonaws.com%2Fuploads%2Farticles%2Fh0yfzebupy5doeul7v02.png"
  summary="Kubernetes 공격 도구 급증 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="DEV Community"
  severity="High"
-%}


> 심각도: High

CSO Online은 2026년 3월 Kubernetes 전용 공격 도구의 급격한 증가를 보고했습니다. 노출된 API 서버를 통한 권한 상승, 탈취된 Pod를 이용한 크립토마이너 배포 등 점점 정교한 공격이 이루어지고 있습니다.

Kubernetes는 전 세계 컨테이너화된 워크로드의 60% 이상을 관리하며, API 서버, etcd, kubelet, 서비스 어카운트, 컨테이너 런타임 모두가 공격 표면입니다.

실무 대응:
- K8s API 서버 외부 노출 차단 (VPN/Bastion 경유)
- etcd 암호화 및 접근 제어 강화
- Network Policy로 Pod 간 통신 최소화
- `kube-bench`로 CIS Kubernetes 벤치마크 준수 점검


---

### 4.3 서비스 메시 복귀: 제로 트러스트 보안 강화

{%- include news-card.html
  title="[클라우드] 서비스 메시 복귀: 제로 트러스트 보안 강화"
  url="https://cloudnativenow.com/contributed-content/why-service-mesh-is-poised-for-a-dramatic-comeback-in-2026/"
  image="https://cloudnativenow.com/wp-content/uploads/2019/06/Service-Mesh-Pattern.jpg"
  summary="서비스 메시 복귀: 제로 트러스트 보안 강화 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Cloud Native Now"
  severity="Medium"
-%}


> 심각도: Medium

2026년 서비스 메시가 제로 트러스트 보안의 핵심 인프라로 재부상하고 있습니다. 기존 사이드카 기반 메시의 채택은 50%에서 42%로 감소했지만, Ambient Mode(사이드카리스) 아키텍처가 새로운 관심을 끌고 있습니다.

AI 기반 워크로드의 증가로 보안 연결, 워크로드 아이덴티티, 관측성 문제가 더욱 시급해졌습니다.

실무 대응:
- Istio Ambient Mode 또는 Cilium Service Mesh 평가
- mTLS 기반 서비스 간 통신 암호화 적용
- 서비스 메시 기반 트래픽 관측 및 이상 탐지


---

![Blockchain Section Banner](/assets/images/section-blockchain.svg)

## 5. 블록체인 뉴스

### 5.1 GENIUS Act: 미국 스테이블코인 규제 프레임워크 구체화

{%- include news-card.html
  title="[블록체인] GENIUS Act: 미국 스테이블코인 규제 프레임워크 구체화"
  url="https://www.clearygottlieb.com/news-and-insights/publication-listing/2026-digital-assets-regulatory-update-a-landmark-2025-but-more-developments-on-the-horizon"
  summary="GENIUS Act: 미국 스테이블코인 규제 프레임워크 구체화 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Cleary Gottlieb"
  severity="Medium"
-%}


> 심각도: Medium

2025년 7월 초당적으로 통과된 GENIUS Act의 구현 타임라인이 구체화되고 있습니다. 감독 기관은 2026년 7월 18일까지 미국 달러 기반 스테이블코인 발행사에 대한 시행 규칙을 발표해야 하며, 규정은 2027년 1월 18일까지 발효됩니다.

SEC와 CFTC도 Project Crypto 공동 프로젝트를 발표하며 디지털 자산 규제 협력을 강화하고 있습니다.

실무 대응:
- 스테이블코인 관련 서비스 운영 조직은 GENIUS Act 준수 타임라인 확인
- AML/KYC 체계를 새 규정에 맞게 업데이트 계획 수립


---

### 5.2 일본 암호화폐 세율 55%에서 20%로 인하 예정

{%- include news-card.html
  title="[블록체인] 일본 암호화폐 세율 55%에서 20%로 인하 예정"
  url="https://sumsub.com/blog/global-crypto-regulations/"
  image="https://sumsub.com/wp/wp-content/uploads/2025/12/opengraph_crypto-regulation-around-the-world-2026_-what-changed-and-whats-ahead.png"
  summary="일본 암호화폐 세율 55%에서 20%로 인하 예정 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Sumsub"
  severity="Medium"
-%}


> 심각도: Medium

일본이 2026년 암호화폐 세율을 55%에서 20%로 인하할 예정입니다. 기존 잡소득으로 분류되던 암호화폐 수익을 전통적인 자본 이득세율과 동일하게 적용하여, 암호화폐 투자 환경을 크게 개선합니다.


---

### 5.3 EU MiCA 전면 시행: 세계 최초 포괄적 암호화폐 규제

{%- include news-card.html
  title="[블록체인] EU MiCA 전면 시행: 세계 최초 포괄적 암호화폐 규제"
  url="https://www.elliptic.co/blog/regulatory-and-policy-crypto-trends-to-except-in-2026"
  image="https://www.elliptic.co/hubfs/2026-Regulatory-outlook-blog_R%26A-Image.png"
  summary="EU MiCA 전면 시행: 세계 최초 포괄적 암호화폐 규제 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, 탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
  source="Elliptic"
  severity="Medium"
-%}


> 심각도: Medium

EU의 MiCA(Markets in Crypto-Assets Regulation)가 전면 시행에 들어갔습니다. 세계 최초의 포괄적 암호화폐 규제 프레임워크로, 엄격한 요구사항으로 인해 일부 시장 참여자에게는 상당한 혼란이 발생하고 있습니다.


---

## 마무리

### 이번 주 핵심 Action Items

| 우선순위 | 조치 항목 | 관련 뉴스 |
|---------|----------|----------|
| P0 | Android 보안 패치 `2026-03-05` 즉시 적용 | 1.1 Android 129개 취약점 |
| P0 | VMware Aria Operations 긴급 패치 | 1.2 CVE-2026-22719 |
| P0 | Cisco SD-WAN Controller CISA ED 26-03 대응 | 1.3 CVE-2026-20127 |
| P1 | Windows 2월 보안 업데이트 미적용 시 즉시 패치 | 1.4 APT28 MSHTML |
| P1 | 운영 환경 SCA 감사 및 EOL 런타임 교체 | 2.1 Datadog 보고서 |
| P1 | GitHub Actions 토큰 권한 최소화 | 2.2 CI/CD 공격 |
| P1 | K8s API 서버 외부 노출 차단 및 RBAC 감사 | 4.1-4.2 K8s 위협 |
| P2 | AI 생성 코드 자동 보안 스캔 게이트 설정 | 3.2 AI DevSecOps |
| P2 | DLP 역량 강화 (랜섬웨어 전술 변화 대비) | 3.3 랜섬웨어 생태계 |

---

> 다음 다이제스트는 2026년 3월 8일에 업데이트됩니다.
> 질문이나 추가 분석이 필요한 항목이 있으면 댓글로 남겨주세요.

---

## 관련 포스트

- [기술·보안 주간 다이제스트 (3월 6일)]({% post_url 2026-03-06-Tech_Security_Weekly_Digest_Security_Threat_AI_AWS %}) - 보안 위협 동향, AI, AWS
- [기술·보안 주간 다이제스트 (3월 8일)]({% post_url 2026-03-08-Tech_Security_Weekly_Digest_AI_Security %}) - AI 보안 동향
- [LLM 보안 실무 가이드]({% post_url 2026-03-07-LLM_Security_Practical_Guide_Prompt_Injection_RAG_MCP %}) - 프롬프트 인젝션, RAG, MCP 보안

---

*이 포스트가 유용했다면, [tech.2twodragon.com](https://tech.2twodragon.com)을 방문하여 더 많은 DevSecOps 인사이트를 확인하세요.*
