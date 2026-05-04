---
layout: post
title: "2026년 4월 2주차 보안 다이제스트 주간 롤업 (4/6~4/12)"
date: 2026-04-12 23:00:00 +0900
categories: [security, devsecops]
tags: [weekly-rollup, security-news, weekly-digest, 2026, April, APT, ransomware, botnet, supply-chain]
excerpt: "2026년 4월 2주차(4/6~4/12) 발행된 보안 주간 다이제스트 7건 통합 롤업. Drift 해킹(2.85억 달러), 이란·북한 연계 한국 표적 APT, APT28 DNS 하이재킹, Masjesu IoT 봇넷, GlassWorm Zig 드로퍼, Citizen Lab 스파이웨어 공개 등 주요 위협과 DevSecOps 대응 포인트를 주차 단위로 통합 정리합니다."
description: "2026년 4월 2주차(4/6~4/12) 발행된 보안 주간 다이제스트 7건 통합 롤업. Drift 해킹(2.85억 달러), 이란·북한 연계 한국 표적 APT, APT28 DNS 하이재킹, Masjesu IoT 봇넷, GlassWorm Zig 드로퍼, Citizen Lab 스파이웨어 공개 등 주요 위협과 DevSecOps 대응 포인트를 주차 단위로 통합 정리합니다."
keywords: [weekly-rollup, security-news, weekly-digest, 2026, April, DevSecOps, Cloud-Security, APT, ransomware, botnet]
author: Twodragon
comments: true
image: /assets/images/2026-04-12-Week2_April_2026_Security_Digest.svg
toc: true
---

{% include ai-summary-card.html
  title='2026년 4월 2주차 보안 다이제스트 주간 롤업'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">weekly-rollup</span>
      <span class="tag">security-news</span>
      <span class="tag">weekly-digest</span>
      <span class="tag">2026</span>
      <span class="tag">April</span>'
  highlights_html='<li><strong>APT 집중</strong>: 이란·북한 연계 한국 표적 다단계 공격, APT28 DNS 하이재킹·PRISMEX 캠페인 동시 확인</li>
      <li><strong>봇넷·클라우드 위협</strong>: Masjesu IoT DDoS 봇넷, Chaos 클라우드 변종, Docker CVE-2026-34040 인증 우회</li>
      <li><strong>공급망·멀웨어</strong>: GlassWorm Zig 드로퍼 IDE 감염, EngageLab SDK 결함으로 5천만 Android 사용자 노출</li>'
  period='2026년 4월 2주차 (4/6 ~ 4/12)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

---

## 개요

2026년 4월 2주차(4월 6일~12일) 동안 발행된 보안 주간 다이제스트 7건을 통합하여 정리합니다. 이번 주는 국가 연계 APT 공격이 다층적으로 확인된 주였습니다. 이란·북한 연계 그룹의 한국 표적 공격, 러시아 APT28의 글로벌 DNS 하이재킹, 그리고 Drift 프로토콜 2.85억 달러 해킹까지 위협 행위자들의 활동이 매우 활발했습니다.

---

## 일별 다이제스트 인덱스

| 날짜 | 주요 이슈 | 링크 |
|------|-----------|------|
| 4월 6일 | Drift 해킹(2.85억 달러), QR 코드 피싱, FortiClient EMS 취약점 | [바로가기](/posts/2026/04/06/Tech_Security_Weekly_Digest_Patch_AI/) |
| 4월 7일 | 이란·북한 연계 한국 표적 공격, REvil·GangCrab 기소 | [바로가기](/posts/2026/04/07/Tech_Security_Weekly_Digest_AI_Ransomware_Go_Palantir/) |
| 4월 8일 | APT28 DNS 하이재킹, Docker CVE-2026-34040, AI 스타트업 보안 리스크 | [바로가기](/posts/2026/04/08/Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet/) |
| 4월 9일 | Chaos 클라우드 변종, Masjesu IoT 봇넷, APT28 PRISMEX 캠페인 | [바로가기](/posts/2026/04/09/Tech_Security_Weekly_Digest_Cloud_Botnet_AI_Malware/) |
| 4월 10일 | EngageLab SDK 취약점(5천만 Android 노출), LucidRook 스피어 피싱, Microsoft 에이전트 SOC | [바로가기](/posts/2026/04/10/Tech_Security_Weekly_Digest_AI_Malware_Go_Agent/) |
| 4월 11일 | GlassWorm Zig 드로퍼 IDE 감염, Chrome 146 DBSC 쿠키 탈취 차단 | [바로가기](/posts/2026/04/11/Tech_Security_Weekly_Digest_AI_Go_CVE_Update/) |
| 4월 12일 | Citizen Lab 스파이웨어 공개, 국제 암호화폐 사기 단속(2만 명+), ChatGPT·Claude 안전성 논란 | [바로가기](/posts/2026/04/12/Tech_Security_Weekly_Digest_Data_GPT_Cloud_AI/) |

---

## 4월 6일: Drift 해킹과 신종 피싱 기법

### 핵심 이슈: Drift 프로토콜 2.85억 달러 해킹

탈중앙화 프로토콜 Drift가 2.85억 달러 규모의 해킹 피해를 입었습니다. 스마트 컨트랙트 취약점과 오라클 조작이 결합된 복합 공격으로 분석됩니다. DeFi 프로토콜 운영 환경에서는 온체인 모니터링과 비정상 거래 패턴 실시간 감지 체계가 필수입니다.

### QR 코드 활용 교통위반 피싱

교통위반 고지서를 가장한 QR 코드 스미싱 기법이 확산됐습니다. 피해자가 QR 코드를 스캔하면 피싱 페이지로 유도되어 개인정보와 카드 정보를 탈취합니다. 직원 대상 보안 인식 교육에 QR 코드 피싱 시나리오를 즉시 추가해야 합니다.

### FortiClient EMS 신규 취약점

FortiClient EMS에 대한 신규 취약점 패치가 배포됐습니다. Fortinet 제품을 사용하는 환경은 즉각 패치 적용 여부를 확인해야 합니다.

---

## 4월 7일: 이란·북한 연계 APT와 랜섬웨어 기소

### 이란 연계 패스워드 스프레이링과 북한의 한국 표적 공격

이란 연계 위협 행위자의 패스워드 스프레이링 공격이 확인됐습니다. 동시에 북한 연계 해커가 한국 표적을 대상으로 다단계 공격 캠페인을 전개하고 있음이 드러났습니다. 초기 침투부터 측면 이동, 데이터 유출까지 체계적으로 설계된 공격 체인이 특징입니다.

**대응 포인트:**
- 계정 잠금 임계값 검토 및 이상 로그인 패턴 모니터링 강화
- 한국 관련 인프라에 대한 접근 제어 정책 긴급 점검
- 다단계 인증(MFA) 전 계정 적용 여부 확인

### REvil·GangCrab 랜섬웨어 운영자 기소

독일 당국이 REvil과 GangCrab 랜섬웨어 운영자를 기소했습니다. 국제 공조 법집행의 성과이며, 동시에 이들 그룹의 잔존 인프라나 후속 그룹의 활동에 대한 모니터링도 필요합니다.

---

## 4월 8일: APT28 DNS 하이재킹과 Docker 인증 우회

### APT28 글로벌 DNS 하이재킹 캠페인

러시아 국가 연계 APT28이 글로벌 규모의 DNS 하이재킹 캠페인을 전개했습니다. DNS 응답을 조작하여 정상 도메인 트래픽을 공격자 인프라로 우회시키는 기법입니다.

**즉각 조치:**
- DNS 쿼리 응답의 이상 패턴 모니터링 설정
- DNSSEC 구현 여부 및 DNS-over-HTTPS 사용 검토
- 내부 DNS 서버 설정 변경 이력 감사

### Docker CVE-2026-34040 인증 우회

Docker API 엔드포인트의 인증 우회 취약점(CVE-2026-34040)이 공개됐습니다. 컨테이너 오케스트레이션 환경에서 권한 없는 컨테이너 실행으로 이어질 수 있는 위험한 취약점입니다.

**즉각 조치:**
- Docker Engine 버전 확인 및 긴급 패치 적용
- Docker API 노출 범위를 최소화하고 mTLS 인증 강제 적용

---

## 4월 9일: Chaos 봇넷과 Masjesu IoT 위협

### Chaos 클라우드 변종과 Masjesu DDoS 봇넷

잘못 구성된 클라우드 환경을 노리는 Chaos 봇넷 신변종이 SOCKS 프록시 기능을 추가하여 탐지를 어렵게 만들고 있습니다. 동시에 글로벌 IoT 장치를 대상으로 한 Masjesu DDoS 봇넷이 급속히 확산됐습니다.

**대응 포인트:**
- 클라우드 인프라 보안 구성(Security Posture Management) 전수 점검
- IoT 장치 기본 자격증명 변경 및 펌웨어 업데이트 체계 구축
- 비정상적 아웃바운드 트래픽 및 DDoS 트래픽 탐지 룰 업데이트

### APT28 PRISMEX 캠페인

우크라이나와 NATO 동맹국을 겨냥한 APT28의 PRISMEX 캠페인이 추가로 확인됐습니다. 스피어 피싱과 제로데이 취약점을 결합한 고도화된 공격입니다.

---

## 4월 10일: EngageLab SDK와 에이전트 기반 SOC

### EngageLab SDK 결함: 5천만 Android 사용자·3천만 암호화폐 지갑 노출

EngageLab SDK의 보안 결함으로 5천만 Android 사용자와 3천만 암호화폐 지갑이 위험에 노출됐습니다. SDK를 통합한 앱이 사용자의 세션 토큰과 지갑 키를 외부로 노출할 수 있는 심각한 취약점입니다.

**즉각 조치:**
- 자사 앱에서 EngageLab SDK 사용 여부 확인
- 영향을 받는 버전 식별 및 SDK 업데이트 또는 제거
- 사용자 알림 및 자격증명 재발급 프로세스 준비

### UAT-10362 LucidRook 스피어 피싱

대만 NGO를 표적으로 한 UAT-10362의 LucidRook 악성코드 스피어 피싱 캠페인이 확인됐습니다. Microsoft의 에이전트 기반 SOC 비전과 함께, AI가 보안 운영에서 위협 탐지와 대응 자동화를 가속화하는 방향도 이번 주 주목받았습니다.

---

## 4월 11일: GlassWorm의 IDE 감염 경로

### GlassWorm Zig 드로퍼를 통한 IDE 감염

GlassWorm 악성코드가 Zig 언어로 작성된 드로퍼를 통해 개발자 IDE를 감염 경로로 활용하는 새로운 기법이 분석됐습니다. 개발 환경이 직접 공격 대상이 됨에 따라 CI/CD 파이프라인 전체의 무결성 검증이 더욱 중요해졌습니다.

**대응 포인트:**
- IDE 플러그인 및 확장 프로그램의 출처 검증 강화
- 개발 환경 격리 및 빌드 서버 접근 제어 강화
- 코드 서명 및 빌드 아티팩트 무결성 검증 자동화

### Chrome 146 DBSC: 세션 쿠키 탈취 차단

Chrome 146에 도입된 Device Bound Session Credentials(DBSC)가 Windows 환경에서 세션 쿠키 탈취 공격을 효과적으로 차단합니다. 기업 브라우저 정책에 DBSC 활성화를 포함시키는 것이 권장됩니다.

---

## 4월 12일: Citizen Lab 스파이웨어 공개

### Citizen Lab 스파이웨어 연구 공개

Citizen Lab이 상업용 스파이웨어의 새로운 인프라와 피해자 분석 결과를 공개했습니다. 언론인, 활동가, 반체제 인사를 주요 표적으로 하는 국가 지원 스파이웨어의 동작 방식과 탐지 방법이 포함됐습니다.

### 국제 암호화폐 사기 단속

국제 공조 단속으로 2만 명 이상이 연루된 암호화폐 사기 네트워크가 적발됐습니다. 소셜 엔지니어링과 가짜 투자 플랫폼을 결합한 '피그 도살(Pig Butchering)' 사기 수법이 계속해서 진화하고 있습니다.

---

## 2주차 트렌드 분석

### 이번 주 핵심 트렌드

**국가 연계 위협 행위자의 동시다발 활동**: 이란, 북한, 러시아 연계 APT 그룹이 동시에 활발한 공격을 전개한 주였습니다. 특히 한국 인프라를 표적으로 한 북한 연계 공격은 국내 보안 팀의 즉각적인 경계 강화를 요구했습니다.

**개발 환경이 공격 표면으로**: GlassWorm의 IDE 감염 경로와 EngageLab SDK 결함은 개발 도구와 서드파티 SDK 자체가 공격 벡터로 활용되는 트렌드를 보여줍니다. 개발 환경의 공급망 보안이 핵심 과제입니다.

**봇넷의 클라우드 표적화 심화**: Chaos 봇넷 변종이 클라우드 설정 오류를 자동 탐지하고 악용하는 기능을 추가했습니다. 클라우드 Security Posture Management(CSPM) 도구의 지속적 운영이 필수입니다.

---

## 주요 CVE 요약

| CVE | 대상 | CVSS | 상태 |
|-----|------|------|------|
| CVE-2026-34040 | Docker Engine | 높음 | 긴급 패치 배포 |

---

## 실무 우선순위 체크리스트

### P0 (즉시)
- [ ] Docker CVE-2026-34040 패치 즉시 적용
- [ ] EngageLab SDK 사용 앱 식별 및 긴급 업데이트

### P1 (7일 내)
- [ ] DNS 쿼리 이상 패턴 모니터링 설정 (APT28 DNS 하이재킹 대비)
- [ ] 한국 대상 인프라 접근 제어 정책 점검 (북한 APT 대비)
- [ ] IoT 장치 기본 자격증명 변경 및 펌웨어 업데이트 검토

### P2 (30일 내)
- [ ] IDE 및 개발 도구 플러그인 출처 검증 정책 수립
- [ ] Chrome DBSC 활성화 기업 브라우저 정책 검토
- [ ] 클라우드 Security Posture Management 자동화 강화

---

**작성자**: Twodragon
