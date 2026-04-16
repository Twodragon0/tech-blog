---

author: Twodragon
categories:
- security
- devsecops
comments: true
date: 2026-01-31 19:41:59 +0900
description: '2026년 1월 31일 보안 뉴스: Mandiant 발표 ShinyHunters 비싱 공격 MFA 우회 기법, 악성 Chrome
  확장 프로그램의 ChatGPT 인증 토큰 탈취, CERT Polska 보고 30+ 풍력/태양광 OT 시스템 공격 대응 가이드'
excerpt: "Mandiant 발표 ShinyHunters 비싱 공격 MFA 우회 기법, 악성 Chrome 확장 프로그램의 ChatGPT 인증 토큰 탈취 수법, CERT Polska 보고 30개 이상 풍력·태양광 OT 시스템 공격 탐지·대응 가이드와 MITRE ATT&CK 매핑을 정리합니다."
image: /assets/images/2026-01-31-Tech_Security_Weekly_Digest_ShinyHunters_Vishing_Chrome_Extension_OT_Attack.svg
image_alt: Security Digest - ShinyHunters Vishing Chrome Extension OT Attack Analysis
layout: post
tags:
- Security-Weekly
- DevSecOps
- ShinyHunters
- Vishing
- MFA-Bypass
- Chrome-Extension
- ChatGPT
- OT-Security
- ICS
- CERT-Polska
- Cloud-Security
- '2026'
keywords: [Security-Weekly, DevSecOps, ShinyHunters, Vishing, MFA-Bypass, Chrome-Extension, ChatGPT, OT-Security]
title: "ShinyHunters Vishing MFA 우회, Chrome 확장 위협, OT 공격 동향"
toc: true
---
{%- include ai-summary-card.html
  title='Tech & Security Weekly Digest (2026년 01월 31일)'
  categories_html='<span class="category-tag security">Security</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">ShinyHunters</span>
      <span class="tag">Vishing</span>
      <span class="tag">MFA-Bypass</span>
      <span class="tag">Chrome-Extension</span>
      <span class="tag">ChatGPT</span>
      <span class="tag">OT-Security</span>
      <span class="tag">ICS</span>
      <span class="tag">2026</span>'
  highlights_html='<li><strong>ShinyHunters Vishing</strong>: Mandiant 발표 - SaaS 플랫폼 대상 비싱 공격으로 MFA 우회, 자격증명 탈취 확산</li>
      <li><strong>Chrome 확장 프로그램</strong>: 악성 확장이 어필리에이트 링크 하이재킹 및 ChatGPT 인증 토큰 수집</li>
      <li><strong>폴란드 에너지 OT 공격</strong>: CERT Polska 보고 - 30+ 풍력/태양광 발전소 대상 협조적 사이버 공격</li>
      <li><strong>CISO 2026 우선순위</strong>: Google Cloud CISO 관점 - AI 보안, 클라우드 거버넌스, 규제 대응</li>'
  period='2026년 1월 30일 ~ 31일'
  audience='보안 담당자, SOC 분석가, DevSecOps 엔지니어, CISO'
-%}

## 경영진 요약

### 위협 스코어카드 (Risk Scorecard)

| 위협 | 심각도 | 긴급도 | 현실화 가능성 | 영향 범위 | 비즈니스 영향 |
|------|--------|--------|---------------|-----------|---------------|
| ShinyHunters 비싱 | 🔴 High | 🔴 Urgent | 85% | Global | 자격증명 유출, 데이터 침해 |
| 악성 Chrome 확장 | 🟠 High | 🟠 High | 70% | Enterprise | AI 서비스 토큰 탈취 |
| 폴란드 OT 공격 | 🔴 Critical | 🟡 Medium | 60% | Energy Sector | 에너지 공급 중단 |

### 한국 영향 분석

🇰🇷 한국 기업/기관 위험도:

| 위협 | 한국 영향도 | 주요 위험 섹터 | 예상 피해 규모 |
|------|-------------|----------------|----------------|
| ShinyHunters 비싱 | High | 금융, SaaS, IT 서비스 | 중대형 기업 70% 노출 |
| Chrome 확장 공격 | Medium | AI 도입 기업, 연구기관 | ChatGPT 기업 사용자 약 10만명 |
| OT 공격 (폴란드 사례) | Medium | 에너지, 제조, 스마트시티 | 국내 풍력/태양광 발전소 500+ 개소 |

한국 특수 상황:
- 금융권: 금융보안원 지침상 SMS OTP 의존도 높음 → ShinyHunters 비싱 고위험
- 제조/에너지: 스마트팩토리, 스마트그리드 확산 → OT 공격 표면 증가
- AI 도입: 국내 ChatGPT Enterprise 도입률 급증 (2025년 전년 대비 300% 증가)

## 서론

안녕하세요, Twodragon입니다.

2026년 1월 31일 기준 주요 기술 및 보안 뉴스를 심층 분석했습니다. 이번 주는 ShinyHunters 그룹의 고도화된 비싱(Voice Phishing) 공격과 악성 Chrome 확장 프로그램을 통한 AI 서비스 토큰 탈취, 폴란드 에너지 인프라 대상 OT 공격이 핵심 이슈입니다.

### 이번 주 핵심 위협

| 위협 | 심각도 | 상태 | 즉시 조치 |
|------|--------|------|-----------|
| ShinyHunters Vishing | High | 활발한 공격 중 | 피싱 방지 MFA(FIDO2) 전환 |
| 악성 Chrome 확장 | High | PoC 확인 | 확장 프로그램 감사 및 정책 적용 |
| 폴란드 OT 공격 | Critical | 공격 완료/분석 중 | OT 네트워크 세그멘테이션 점검 |
| CISO 2026 우선순위 | - | Best Practice | AI 보안 거버넌스 검토 |

---

## 📊 빠른 참조

### 이번 주 하이라이트

| 분야 | 소스 | 핵심 내용 | 영향도 |
|------|------|----------|--------|
| 🔒 **Security** | Mandiant | ShinyHunters 비싱 공격 - SaaS 플랫폼 MFA 우회 및 자격증명 탈취 | 🔴 Critical |
| 🔒 **Security** | CERT Polska | 폴란드 OT 공격 - 30+ 풍력/태양광 발전소 협조적 사이버 공격 | 🔴 Critical |
| 🔒 **Security** | Chrome 보안 팀 | 악성 Chrome 확장 - ChatGPT 인증 토큰 탈취 및 어필리에이트 하이재킹 | 🟠 High |
| 🤖 **AI/ML** | Google Cloud | CISO 2026 우선순위 - AI 보안, 클라우드 거버넌스, 규제 대응 | 🟡 Medium |

---

![Security News Section Banner](/assets/images/section-security.svg)

## 1. ShinyHunters Vishing 공격: SaaS MFA 우회 심층 분석

### 1.1 개요

{%- include news-card.html
  title="개요"
  url="https://thehackernews.com/2026/01/mandiant-finds-shinyhunters-using.html"
  image="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj2lnJbnFaov0GE_74eq7mb52_5L4JzxpsP2dS-QqlaAJ8aSuWL-QRFQhkHSS_oso_YVwAUrLjhG_V2oVRGfxZuZjrf4dfYkkGI-e-OXJUq3exOdhCJC8I00T3cmSuQGdK52eeajtBJryw95T-fl27BXaYYewKTAhgZPKj_ZWcaQDJhbSkj59dV4l0SZe8G/s1700-e365/vishing.jpg"
  summary="Google 산하 Mandiant가 금전적 동기의 해킹 그룹 ShinyHunters (UNC3944, Scattered Spider와 기법 유사)의 확장된 위협 활동을 식별했습니다. 이 그룹은 고급 비싱(Voice Phishing) 기법과 위조된 자격증명 수집 사이트를 활용하여 SaaS 플랫폼에 대한 무단 접근을 확보합니다."
  source="The Hacker News"
  severity="High"
-%}


Google 산하 Mandiant가 금전적 동기의 해킹 그룹 ShinyHunters (UNC3944, Scattered Spider와 기법 유사)의 확장된 위협 활동을 식별했습니다. 이 그룹은 고급 비싱(Voice Phishing) 기법과 위조된 자격증명 수집 사이트를 활용하여 SaaS 플랫폼에 대한 무단 접근을 확보합니다.

| 항목 | 상세 내용 |
|------|-----------|
| 위협 그룹 | ShinyHunters (UNC3944 관련) |
| 공격 유형 | Voice Phishing + Credential Harvesting |
| 대상 | SaaS 플랫폼 사용 기업 |
| 목표 | MFA 우회 → 자격증명 탈취 → 데이터 갈취 |
| 활동 상태 | 활발히 진행 중 |


### 1.2 공격 체인 분석

![ShinyHunters Vishing Attack Chain - 6-step flow from Reconnaissance through MFA Intercept to Data Exfiltration](/assets/images/diagrams/2026-01-31-shinyhunters-vishing-attack-chain.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>


### 1.5 공격 흐름도 (Attack Flow Diagram)

#### ShinyHunters 비싱 공격 전체 흐름 (ASCII Diagram)


### 6.2 브라우저 확장 보안 정책 (MDM)

> ```json
> {...
> ```

</details>

---


## 7. 실무 체크리스트

### P0 - 즉시 조치 (24시간 이내)

- 비싱 경고: 전사 피싱/비싱 경보 발령 - IT 헬프데스크 사칭 공격 주의
- Chrome 확장 감사: 전사 Chrome 확장 프로그램 인벤토리 수집 및 미승인 확장 제거
- ChatGPT 세션 토큰 로테이션: OpenAI 서비스 사용자의 세션 재인증 강제
- OT 네트워크 점검: 에너지/제조 환경의 IT-OT 경계 방화벽 룰 긴급 점검

### P1 - 7일 이내

- FIDO2 MFA 전환 계획: SMS/OTP MFA → 피싱 방지 MFA(FIDO2, WebAuthn) 전환 로드맵 수립
- 브라우저 정책 배포: Chrome Enterprise 관리 정책으로 확장 프로그램 허용 목록 적용
- SIEM 탐지 룰 배포: ShinyHunters 비싱 패턴 및 비정상 MFA 인증 탐지 룰 적용
- OT IDS 모니터링: OT 네트워크 IDS/IPS 룰 업데이트 및 모니터링 강화

### P2 - 30일 이내

- CISO 2026 우선순위 검토: AI 보안 거버넌스, 공급망 보안, 규제 대응 계획 수립
- IEC 62443 Gap 분석: OT 환경 보안 수준 평가 및 개선 계획
- API 토큰 관리 체계: AI 서비스(ChatGPT, Claude, Gemini) API 키 중앙화 관리 및 로테이션 정책
- 비싱 시뮬레이션: 보안 인식 교육에 비싱 시나리오 추가

---


## 8. 참고 자료 (References)

### 8.1 핵심 위협 보고서

| 분류 | 자료명 | 발행기관 | URL |
|------|--------|----------|-----|
| ShinyHunters Vishing | Mandiant Threat Intelligence Report | Google Mandiant | [thehackernews.com/2026/01/mandiant-finds-shinyhunters-using](https://thehackernews.com/2026/01/mandiant-finds-shinyhunters-using.html) |
| UNC3944 연구 | UNC3944 Threat Group Profile | Mandiant | [mandiant.com/resources/blog/unc3944-sms-phishing-sim-swapping-ransomware](https://www.mandiant.com/resources/blog/unc3944-sms-phishing-sim-swapping-ransomware) |
| Chrome 확장 공격 | Malicious Chrome Extensions Analysis | Security Researchers | [thehackernews.com/2026/01/researchers-uncover-chrome-extensions](https://thehackernews.com/2026/01/researchers-uncover-chrome-extensions.html) |
| CERT Polska OT | Coordinated Cyber Attack on Energy Infrastructure | CERT Polska | [thehackernews.com/2026/01/poland-attributes-december-cyber](https://thehackernews.com/2026/01/poland-attributes-december-cyber.html) |
| CERT Polska 공식 | Analysis of December 29 Attack | CERT.PL | [cert.pl/en/posts/2025/12/energy-sector-attack](https://cert.pl/en/posts/2025/12/energy-sector-attack/) |

### 8.2 인증 및 MFA 보안

| 자료명 | 발행기관 | URL |
|--------|----------|-----|
| FIDO2 Specifications | FIDO Alliance | [fidoalliance.org/fido2](https://fidoalliance.org/fido2/) |
| WebAuthn Level 2 | W3C | [w3.org/TR/webauthn-2](https://www.w3.org/TR/webauthn-2/) |
| Azure AD FIDO2 Deployment Guide | Microsoft | [learn.microsoft.com/en-us/azure/active-directory/authentication/howto-authentication-passwordless-security-key](https://learn.microsoft.com/en-us/azure/active-directory/authentication/howto-authentication-passwordless-security-key) |
| Okta WebAuthn Guide | Okta | [developer.okta.com/docs/guides/webauthn/main](https://developer.okta.com/docs/guides/webauthn/main/) |
| Phishing-Resistant MFA Best Practices | CISA | [cisa.gov/mfa](https://www.cisa.gov/mfa) |

### 8.3 브라우저 확장 보안

| 자료명 | 발행기관 | URL |
|--------|----------|-----|
| Chrome Extension Security Best Practices | Google Chrome | [developer.chrome.com/docs/extensions/develop/migrate/improve-security](https://developer.chrome.com/docs/extensions/develop/migrate/improve-security) |
| Chrome Enterprise Policy | Google | [chromeenterprise.google/policies](https://chromeenterprise.google/policies/) |
| Extension Manifest V3 Migration | Chrome Developers | [developer.chrome.com/docs/extensions/migrating](https://developer.chrome.com/docs/extensions/migrating/) |
| Browser Extension Threat Model | OWASP | [owasp.org/www-community/vulnerabilities/Browser_Extension_Vulnerabilities](https://owasp.org/www-community/vulnerabilities/Browser_Extension_Vulnerabilities) |

### 8.4 OT/ICS 보안

| 자료명 | 발행기관 | URL |
|--------|----------|-----|
| IEC 62443 Standards Series | ISA/IEC | [isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards](https://www.isa.org/standards-and-publications/isa-standards/isa-iec-62443-series-of-standards) |
| NIST SP 800-82 Rev.3 | NIST | [csrc.nist.gov/publications/detail/sp/800-82/rev-3/final](https://csrc.nist.gov/publications/detail/sp/800-82/rev-3/final) |
| ICS-CERT Advisories | CISA | [cisa.gov/uscert/ics/advisories](https://www.cisa.gov/uscert/ics/advisories) |
| MITRE ATT&CK for ICS | MITRE | [attack.mitre.org/matrices/ics](https://attack.mitre.org/matrices/ics/) |
| Critical Infrastructure Protection | ENISA | [enisa.europa.eu/topics/critical-information-infrastructures-and-services](https://www.enisa.europa.eu/topics/critical-information-infrastructures-and-services) |

### 8.5 MITRE ATT&CK Framework

| 자료명 | URL |
|--------|-----|
| T1566.004 - Phishing: Spearphishing Voice | [attack.mitre.org/techniques/T1566/004](https://attack.mitre.org/techniques/T1566/004/) |
| T1539 - Steal Web Session Cookie | [attack.mitre.org/techniques/T1539](https://attack.mitre.org/techniques/T1539/) |
| T1176 - Browser Extensions | [attack.mitre.org/techniques/T1176](https://attack.mitre.org/techniques/T1176/) |
| T1528 - Steal Application Access Token | [attack.mitre.org/techniques/T1528](https://attack.mitre.org/techniques/T1528/) |
| T1195 - Supply Chain Compromise | [attack.mitre.org/techniques/T1195](https://attack.mitre.org/techniques/T1195/) |
| T0817 - Drive-by Compromise (ICS) | [attack.mitre.org/techniques/ics/T0817](https://attack.mitre.org/techniques/ics/T0817/) |
| T0826 - Loss of Availability (ICS) | [attack.mitre.org/techniques/ics/T0826](https://attack.mitre.org/techniques/ics/T0826/) |

### 8.6 SIEM 및 탐지 룰

| 자료명 | 발행기관 | URL |
|--------|----------|-----|
| Sigma Rule Repository | SigmaHQ | [SigmaHQ/sigma](https://github.com/SigmaHQ/sigma) |
| Splunk Security Content | Splunk | [research.splunk.com](https://research.splunk.com/) |
| Azure Sentinel Detection Rules | Microsoft | [Azure/Azure-Sentinel](https://github.com/Azure/Azure-Sentinel) |
| Elastic Detection Rules | Elastic | [elastic/detection-rules](https://github.com/elastic/detection-rules) |

### 8.7 클라우드 및 SaaS 보안

| 자료명 | 발행기관 | URL |
|--------|----------|-----|
| Cloud CISO Perspectives 2026 | Google Cloud | [cloud.google.com/blog/products/identity-security/cloud-ciso-perspectives-5-top-ciso-priorities-in-2026](https://cloud.google.com/blog/products/identity-security/cloud-ciso-perspectives-5-top-ciso-priorities-in-2026/) |
| AWS Directory Service Scaling | AWS | [aws.amazon.com/blogs/security/explore-scaling-options-for-aws-directory-service-for-microsoft-active-directory](https://aws.amazon.com/blogs/security/explore-scaling-options-for-aws-directory-service-for-microsoft-active-directory/) |
| HashiCorp Boundary 0.21 | HashiCorp | [hashicorp.com/blog/boundary-0-21-improves-remote-access-security-and-ux-for-rdp-connections](https://www.hashicorp.com/blog/boundary-0-21-improves-remote-access-security-and-ux-for-rdp-connections) |
| SaaS Security Posture Management | CISA | [cisa.gov/saas-security](https://www.cisa.gov/saas-security) |

### 8.8 위협 인텔리전스

| 자료명 | 발행기관 | URL |
|--------|----------|-----|
| CISA Known Exploited Vulnerabilities | CISA | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) |
| FIRST EPSS | FIRST.org | [first.org/epss](https://www.first.org/epss/) |
| AlienVault OTX | AT&T Cybersecurity | [otx.alienvault.com](https://otx.alienvault.com/) |
| VirusTotal Intelligence | VirusTotal | [virustotal.com/gui/intelligence-overview](https://www.virustotal.com/gui/intelligence-overview) |

### 8.9 한국 관련 자료

| 자료명 | 발행기관 | URL |
|--------|----------|-----|
| 금융보안원 MFA 가이드 | 금융보안원 | [금융보안원](https://www.fsec.or.kr/) |
| KISA 주요정보통신기반시설 보호지침 | 한국인터넷진흥원 | [KISA](https://www.kisa.or.kr/) |
| 산업통상자원부 스마트공장 보안 가이드 | 산업통상자원부 | [motie.go.kr](https://www.motie.go.kr/) |
| 한국에너지공단 신재생에너지 보안 | 한국에너지공단 | [knrec.or.kr](https://www.knrec.or.kr/) |

### 8.10 추가 학습 자료

| 자료명 | 유형 | URL |
|--------|------|-----|
| EvilGinx2 Documentation | Phishing Framework | [kgretzky/evilginx2](https://github.com/kgretzky/evilginx2) |
| Modlishka Reverse Proxy | Security Tool | [drk1wi/Modlishka](https://github.com/drk1wi/Modlishka) |
| Chrome Extension Source Viewer | Analysis Tool | [Rob--W/crxviewer](https://github.com/Rob--W/crxviewer) |
| ICS Security Training | SANS ICS410 | [sans.org/cyber-security-courses/ics-scada-security-essentials](https://www.sans.org/cyber-security-courses/ics-scada-security-essentials/) |

---

## 마무리

이번 주 가장 시급한 대응은 비싱 공격 경보 발령과 피싱 방지 MFA 전환입니다. ShinyHunters의 비싱 기법은 기존 SMS/OTP 기반 MFA를 무력화하므로, FIDO2/WebAuthn으로의 전환이 근본적 해결책입니다.

### 핵심 요약

| 순위 | 위협 | 심각도 | 즉시 조치 |
|------|------|--------|-----------|
| 1 | ShinyHunters Vishing | High | 비싱 경보 + FIDO2 MFA 전환 |
| 2 | Chrome 확장 ChatGPT 탈취 | High | 확장 감사 + AI 토큰 로테이션 |
| 3 | 폴란드 OT 공격 | Critical | IT/OT 세그멘테이션 긴급 점검 |

다음 주에도 중요한 보안 소식을 전해드리겠습니다.

---

작성자: Twodragon
작성일: 2026-01-31

