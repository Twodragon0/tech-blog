---
layout: post
title: "2026년 4월 3주차 보안 다이제스트 주간 롤업 (4/13~4/19)"
date: 2026-04-19 23:00:00 +0900
categories: [security, devsecops]
tags: [weekly-rollup, security-news, weekly-digest, 2026, April, ransomware, botnet, CVE, nginx, AI]
excerpt: "2026년 4월 3주차(4/13~4/19) 발행된 보안 주간 다이제스트 7건 통합 롤업. CPUID 공급망 침해(CPU-Z 변조), JanelaRAT 신규 멀웨어, n8n Webhooks 피싱 악용, Nginx UI 인증 우회(CVE-2026-33032), PowMix 봇넷, Mirai 변종 Nexcorium 등 주요 위협과 DevSecOps 대응 포인트를 통합 정리합니다."
description: "2026년 4월 3주차(4/13~4/19) 발행된 보안 주간 다이제스트 7건 통합 롤업. CPUID 공급망 침해(CPU-Z 변조), JanelaRAT 신규 멀웨어, n8n Webhooks 피싱 악용, Nginx UI 인증 우회(CVE-2026-33032), PowMix 봇넷, Mirai 변종 Nexcorium 등 주요 위협과 DevSecOps 대응 포인트를 통합 정리합니다."
keywords: [weekly-rollup, security-news, weekly-digest, 2026, April, DevSecOps, Cloud-Security, ransomware, botnet, nginx]
author: Twodragon
comments: true
image: /assets/images/2026-04-19-Week3_April_2026_Security_Digest.svg
toc: true
---

{% include ai-summary-card.html
  title='2026년 4월 3주차 보안 다이제스트 주간 롤업'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">weekly-rollup</span>
      <span class="tag">security-news</span>
      <span class="tag">weekly-digest</span>
      <span class="tag">2026</span>
      <span class="tag">April</span>'
  highlights_html='<li><strong>공급망 침해</strong>: CPUID 공급망 침해로 CPU-Z 변조 배포, n8n Webhooks를 통한 피싱 이메일 악성코드 유포</li>
      <li><strong>신규 취약점</strong>: Nginx UI CVE-2026-33032 인증 우회, Marimo 사전 인증 RCE 치명적 취약점 발견</li>
      <li><strong>봇넷 확산</strong>: PowMix 봇넷, Mirai 변종 Nexcorium, Operation PowerOFF 국제 공조 단속</li>'
  period='2026년 4월 3주차 (4/13 ~ 4/19)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

---

## 개요

2026년 4월 3주차(4월 13일~19일) 동안 발행된 보안 주간 다이제스트 7건을 통합하여 정리합니다. 이번 주는 공급망 침해와 신규 취약점 발견이 집중된 한 주였습니다. 개발 도구와 웹 서버 관리 도구의 취약점이 실제 공격에 활용되는 사례가 다수 확인됐습니다.

---

## 일별 다이제스트 인덱스

| 날짜 | 주요 이슈 | 링크 |
|------|-----------|------|
| 4월 13일 | CPUID 공급망 침해(CPU-Z 변조), Marimo RCE 취약점, Adobe Acrobat 제로데이 악용 | [바로가기](/posts/2026/04/13/Tech_Security_Weekly_Digest_CVE_Patch_Zero-Day_Rust/) |
| 4월 14일 | 2026년 3월 랜섬웨어 동향 보고서, JanelaRAT 신규 변종, FBI·인도네시아 2천만 달러 사기 단속 | [바로가기](/posts/2026/04/14/Tech_Security_Weekly_Digest_Malware_Vulnerability_AI_Data/) |
| 4월 15일 | AWS Model Context Protocol AI 에이전트, PHP Composer 명령어 실행 취약점, Google Pixel 10 Rust DNS 파서 | [바로가기](/posts/2026/04/15/Tech_Security_Weekly_Digest_AI_AWS_Agent_Patch/) |
| 4월 16일 | n8n Webhooks 피싱 악용, Nginx UI CVE-2026-33032 인증 우회, Cloud CISO 회복력 Q&A | [바로가기](/posts/2026/04/16/Tech_Security_Weekly_Digest_AI_Malware_CVE_Patch/) |
| 4월 17일 | PowMix 봇넷 신규 발견, ThreatsDay Bulletin, Operation PowerOFF | [바로가기](/posts/2026/04/17/Tech_Security_Weekly_Digest_Botnet_Threat_AI_Malware/) |
| 4월 18일 | Microsoft Defender ETL 구성 보안, Google 2025년 정책 위반 광고 분석 | [바로가기](/posts/2026/04/18/Tech_Security_Weekly_Digest_Zero-Day_Patch_Security_Go/) |
| 4월 19일 | Grinex 거래소 제재, 크로스 테넌트 헬프데스크 사칭 데이터 탈취, Mirai 변종 Nexcorium | [바로가기](/posts/2026/04/19/Tech_Security_Weekly_Digest_AI_Data_CVE_Botnet/) |

---

## 4월 13일: CPUID 공급망 침해와 Adobe 제로데이

### 핵심 이슈: CPUID 공급망 침해로 CPU-Z 변조 배포

CPUID의 공급망이 침해되어 변조된 CPU-Z 유틸리티가 배포된 사실이 확인됐습니다. 정상 배포 채널을 통해 악성 코드가 삽입된 소프트웨어가 배포되는 전형적인 소프트웨어 공급망 공격입니다. CPU-Z 사용 환경에서는 즉시 해시 검증을 수행하고, 알려진 악성 버전을 제거해야 합니다.

**대응 포인트:**
- CPU-Z 설치 인스턴스 전수 확인 및 파일 해시 검증
- 소프트웨어 배포 채널에 대한 코드 서명 검증 프로세스 강화
- SBOM(Software Bill of Materials) 기반 소프트웨어 인벤토리 관리 강화

### Marimo 사전 인증 RCE 치명적 취약점

오픈소스 노트북 환경 Marimo에서 사전 인증 원격 코드 실행(RCE) 취약점이 발견됐습니다. 인증 없이 임의 코드를 실행할 수 있어 데이터 과학·ML 팀의 개발 환경이 주요 표적이 될 수 있습니다.

### Adobe Acrobat 제로데이 악용

Adobe Acrobat의 취약점이 실제 공격에 활용되고 있음이 확인됐습니다. Adobe 제품 사용 환경에서 즉각적인 패치 적용이 필요합니다.

---

## 4월 14일: 랜섬웨어 동향과 JanelaRAT 신규 변종

### 2026년 3월 랜섬웨어 동향 보고서

3월 랜섬웨어 동향 보고서에 따르면 의료·금융·제조 부문이 주요 표적으로 지속됩니다. RaaS(Ransomware-as-a-Service) 모델의 고도화로 진입 장벽이 낮아지면서 공격 빈도가 증가 추세입니다.

**주요 트렌드:**
- 이중 갈취(Double Extortion): 데이터 암호화 + 유출 협박 병행
- 초기 접근 브로커(IAB)를 통한 침투 전문화
- 클라우드 스토리지 및 백업 시스템을 우선 표적으로 삼는 전술 진화

### JanelaRAT 신규 변종

JanelaRAT 원격 접근 트로이목마의 신규 변종이 발견됐습니다. 브라질 등 남미 지역을 중심으로 확산 중이나 글로벌 인프라를 대상으로 하는 캠페인도 확인됩니다. 지속성 메커니즘과 탐지 우회 기법이 이전 버전 대비 강화됐습니다.

### FBI·인도네시아 경찰 합동 2천만 달러 암호화폐 사기 단속

국제 공조를 통해 2천만 달러 규모의 암호화폐 사기 네트워크가 적발됐습니다. 소셜 엔지니어링과 가짜 투자 플랫폼을 결합한 수법이 계속해서 진화하고 있어 임직원 대상 보안 교육 강화가 필요합니다.

---

## 4월 15일: AWS MCP 에이전트와 Rust 기반 보안

### AWS Model Context Protocol 기반 AI 에이전트 보안

AWS가 Model Context Protocol(MCP)을 기반으로 한 AI 에이전트 접근 패턴을 공개했습니다. LLM 에이전트가 AWS 서비스와 상호작용할 때 필요한 최소 권한 원칙 적용과 API 호출 감사 방법이 포함됩니다.

**실무 적용:**
- AI 에이전트에 부여하는 IAM 역할을 최소 권한 원칙으로 설계
- 에이전트의 API 호출을 CloudTrail로 전량 감사
- 프롬프트 인젝션 방어 레이어를 에이전트 실행 환경에 추가

### PHP Composer 임의 명령어 실행 취약점

PHP 패키지 관리자 Composer에서 임의 명령어 실행 취약점이 발견되어 패치가 배포됐습니다. PHP 기반 애플리케이션 빌드 파이프라인에서 Composer를 사용하는 환경은 즉각 업데이트가 필요합니다.

### Google Pixel 10: Rust 기반 DNS 파서 적용

Google이 Pixel 10 모뎀에 Rust로 작성된 DNS 파서를 적용했습니다. 메모리 안전성 언어를 시스템 소프트웨어에 적용하는 업계 트렌드의 중요한 사례로, C/C++ 기반 레거시 컴포넌트의 Rust 재작성 계획을 검토할 시점입니다.

---

## 4월 16일: n8n Webhooks 악용과 Nginx UI 인증 우회

### n8n Webhooks를 통한 피싱 이메일 악성코드 유포

워크플로우 자동화 도구 n8n의 Webhooks 기능이 2025년 10월부터 피싱 이메일 악성코드 유포에 악용되고 있습니다. 합법적인 자동화 플랫폼을 경유하여 보안 필터를 우회하는 기법으로, n8n 인스턴스를 운영하는 조직은 Webhook 엔드포인트에 대한 접근 제어와 요청 검증을 강화해야 합니다.

**즉각 조치:**
- n8n Webhook 엔드포인트 인증 및 요청 출처 검증 강화
- 발신 이메일 보안 필터에 자동화 플랫폼 경유 패턴 추가
- n8n 워크플로우 실행 로그 감사 강화

### Nginx UI CVE-2026-33032 인증 우회 - 활발한 악용 중

Nginx 웹 서버 관리 UI의 인증 우회 취약점(CVE-2026-33032)이 실제 공격에 활발히 이용되고 있습니다. 인증 없이 서버 설정을 변경하거나 임의 파일을 읽을 수 있는 치명적 취약점입니다.

**즉각 조치:**
- Nginx UI 버전 확인 및 긴급 패치 적용
- Nginx UI 접근을 내부 네트워크 또는 VPN으로 제한
- 인터넷에 노출된 Nginx UI 인스턴스 즉시 격리

---

## 4월 17일: PowMix 봇넷과 Operation PowerOFF

### PowMix 봇넷 신규 발견

신규 PowMix 봇넷이 발견됐습니다. 취약한 서버와 IoT 장치를 감염시켜 DDoS 공격 인프라로 활용하는 봇넷으로, C2 서버 통신에 암호화를 적용하여 탐지를 어렵게 만듭니다.

### Operation PowerOFF: DDoS 서비스형 범죄 국제 공조 단속

국제 공조 작전 Operation PowerOFF를 통해 DDoS-as-a-Service 플랫폼 다수가 차단됐습니다. 합법적 사업체로 위장하여 DDoS 공격 서비스를 판매하던 범죄 인프라가 제거됐으나, 후속 플랫폼의 등장에 대한 지속적 모니터링이 필요합니다.

---

## 4월 18일: Microsoft Defender 구성 보안

### Microsoft Defender ETL 기반 구성 보안

Microsoft Defender가 ETL(Event Tracing for Windows) 기반 구성 보안 기능을 강화했습니다. 악의적인 구성 변경을 실시간으로 감지하고 차단하는 기능으로, Defender를 사용하는 환경에서 ETL 로그 기반 보안 이벤트 모니터링을 활성화하는 것이 권장됩니다.

---

## 4월 19일: 크로스 테넌트 공격과 Nexcorium 봇넷

### 크로스 테넌트 헬프데스크 사칭 데이터 탈취

멀티테넌트 환경에서 헬프데스크 직원을 사칭한 크로스 테넌트 공격으로 데이터가 탈취되는 사례가 확인됐습니다. SaaS 플랫폼의 테넌트 격리 설정과 내부 헬프데스크 인증 절차를 즉시 점검해야 합니다.

### Mirai 변종 Nexcorium

Mirai 봇넷의 새로운 변종 Nexcorium이 발견됐습니다. 취약한 IoT 장치와 라우터를 표적으로 하며, 기존 Mirai 변종 대비 감염 속도가 빠른 것이 특징입니다.

### Grinex 거래소 제재

정보 기관의 주장 이후 Grinex 암호화폐 거래소가 제재 대상이 됐습니다. 제재된 플랫폼과의 거래가 자사 컴플라이언스에 미치는 영향을 법무팀과 즉시 검토해야 합니다.

---

## 3주차 트렌드 분석

### 이번 주 핵심 트렌드

**합법적 도구의 악성 활용 심화**: n8n Webhooks를 통한 악성코드 유포는 정상적인 워크플로우 자동화 도구가 공격 인프라로 전용되는 트렌드를 명확히 보여줍니다. 자동화 플랫폼의 Webhook 보안 설정을 전수 점검해야 합니다.

**웹 서버 관리 도구 취약점 악용**: Nginx UI CVE-2026-33032의 활발한 악용은 관리 인터페이스가 최우선 공격 표적임을 재확인합니다. 모든 관리 UI를 인터넷에서 격리하는 것이 기본 원칙입니다.

**공급망 침해의 지속**: CPUID·CPU-Z 사건은 3주 연속으로 공급망 공격이 주요 위협으로 부상하고 있음을 보여줍니다. 소프트웨어 설치 전 해시 검증을 운영 정책으로 수립해야 합니다.

**메모리 안전성 언어로의 전환 가속**: Google Pixel 10의 Rust DNS 파서 적용은 시스템 소프트웨어 수준의 메모리 안전성 확보 추세를 보여줍니다. 레거시 C/C++ 컴포넌트의 현대화 계획을 수립할 시점입니다.

---

## 주요 CVE 요약

| CVE | 대상 | 심각도 | 상태 |
|-----|------|--------|------|
| CVE-2026-33032 | Nginx UI | 치명적 | 활발한 악용 중 — 즉시 패치 |

---

## 실무 우선순위 체크리스트

### P0 (즉시)
- [ ] Nginx UI CVE-2026-33032 패치 및 인터넷 노출 인스턴스 즉시 격리
- [ ] CPU-Z 설치 환경 해시 검증 (CPUID 공급망 침해 대응)
- [ ] Adobe Acrobat 긴급 패치 적용

### P1 (7일 내)
- [ ] n8n Webhook 엔드포인트 인증 강화 및 접근 제어 설정
- [ ] PHP Composer 최신 버전 업데이트
- [ ] 헬프데스크 인증 절차 검토 (크로스 테넌트 공격 대응)

### P2 (30일 내)
- [ ] AI 에이전트 IAM 역할 최소 권한 원칙 적용 검토
- [ ] IoT 장치 기본 자격증명 변경 및 Nexcorium 탐지 규칙 추가
- [ ] 레거시 C/C++ 컴포넌트 Rust 전환 로드맵 검토

---

**작성자**: Twodragon
