---
layout: post
title: "2026년 4월 4주차 보안 다이제스트 주간 롤업 (4/20~4/30)"
date: 2026-04-30 23:00:00 +0900
categories: [security, devsecops]
tags: [weekly-rollup, security-news, weekly-digest, 2026, April, supply-chain, npm, ransomware, quantum, FIRESTARTER]
excerpt: "2026년 4월 4주차(4/20~4/30) 발행된 보안 주간 다이제스트 11건 통합 롤업. Apple 피싱, SGLang CVE-2026-5760, SystemBC C2, KICS 악성 Docker 이미지, 자체 전파 npm 웜, FIRESTARTER 백도어, 스턱스넷 변종, Robinhood 피싱, LofyGang, VECT 2.0 랜섬웨어, SAP npm·북한 공급망 공격까지 4월 마지막 주 주요 위협을 종합 정리합니다."
description: "2026년 4월 4주차(4/20~4/30) 발행된 보안 주간 다이제스트 11건 통합 롤업. Apple 피싱, SGLang CVE-2026-5760, SystemBC C2, KICS 악성 Docker 이미지, 자체 전파 npm 웜, FIRESTARTER 백도어, 스턱스넷 변종, Robinhood 피싱, LofyGang, VECT 2.0 랜섬웨어, SAP npm·북한 공급망 공격까지 4월 마지막 주 주요 위협을 종합 정리합니다."
keywords: [weekly-rollup, security-news, weekly-digest, 2026, April, DevSecOps, Cloud-Security, supply-chain, npm, ransomware, quantum]
author: Twodragon
comments: true
image: /assets/images/2026-04-30-Week4_April_2026_Security_Digest.svg
toc: true
---

{% include ai-summary-card.html
  title='2026년 4월 4주차 보안 다이제스트 주간 롤업'
  categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
  tags_html='<span class="tag">weekly-rollup</span>
      <span class="tag">security-news</span>
      <span class="tag">weekly-digest</span>
      <span class="tag">2026</span>
      <span class="tag">April</span>'
  highlights_html='<li><strong>npm 공급망 위기</strong>: 자체 전파 npm 웜·악성 KICS Docker 이미지·SAP npm 패키지·LofyGang 등 npm 생태계 집중 공격</li>
      <li><strong>APT 및 랜섬웨어</strong>: FIRESTARTER 백도어(미 국방 표적), VECT 2.0 랜섬웨어, 라자루스 KelpDAO, 북한 새 공격 물결</li>
      <li><strong>인프라 위협</strong>: 스턱스넷 변종(엔지니어링 소프트웨어), SGLang CVE-2026-5760 SSRF, SystemBC C2 서버 분석</li>'
  period='2026년 4월 4주차 (4/20 ~ 4/30)'
  audience='보안 담당자, DevSecOps 엔지니어, SRE, 클라우드 아키텍트'
%}

---

## 개요

2026년 4월 4주차(4월 20일~30일) 동안 발행된 보안 주간 다이제스트 11건을 통합하여 정리합니다. 이번 주는 npm 패키지 생태계를 대상으로 한 공격이 여러 벡터에서 동시에 발생한 주였습니다. 자체 전파 npm 웜, 악성 KICS Docker 이미지, LofyGang의 지속적 활동, SAP npm 패키지를 통한 북한의 공급망 공격까지 오픈소스 생태계 전반이 위협에 노출됐습니다.

---

## 일별 다이제스트 인덱스

| 날짜 | 주요 이슈 | 링크 |
|------|-----------|------|
| 4월 20일 | Apple 계정 피싱, NIST 취약점 비우선순위 정책 변경, Palantir 논란 | [바로가기](/posts/2026/04/20/Tech_Security_Weekly_Digest_AI_Apple_AWS_Palantir/) |
| 4월 21일 | SGLang CVE-2026-5760(CVSS 치명적), 라자루스 KelpDAO, 주간 보안 요약 | [바로가기](/posts/2026/04/21/Tech_Security_Weekly_Digest_CVE_Apple_AI_Agent/) |
| 4월 22일 | AWS Winter 2025 SOC 1 보고서, SystemBC C2 서버 분석, 22 BRIDGE 캠페인 | [바로가기](/posts/2026/04/22/Tech_Security_Weekly_Digest_AI_Ransomware_AWS_Go/) |
| 4월 23일 | 악성 KICS Docker 이미지·VS Code 확장, 자체 전파 npm 웜, Harvester·Microsoft Graph 악용 | [바로가기](/posts/2026/04/23/Tech_Security_Weekly_Digest_AI_Docker_Go_API/) |
| 4월 24일 | UNC6692 위협 행위자, Microsoft 보안 업데이트, Bitwarden CLI 취약점, Checkmarx 공격 | [바로가기](/posts/2026/04/24/Tech_Security_Weekly_Digest_Malware_AI_Go_Threat/) |
| 4월 25일 | FIRESTARTER 백도어(미 국방 소프트웨어 표적), NASA 직원 대상 공격, 양자 위협 대응 | [바로가기](/posts/2026/04/25/Tech_Security_Weekly_Digest_Patch_Security_Threat_Data/) |
| 4월 26일 | 스턱스넷 변종(엔지니어링 소프트웨어), Microsoft Windows 개편, 위협 행위자의 Microsoft 도구 악용 | [바로가기](/posts/2026/04/26/Tech_Security_Weekly_Digest_Malware_Threat_AWS_Go/) |
| 4월 27일 | 미국 유틸리티 기업 Itron 한국 파트너십, AI 에이전트 원칙 공개 | [바로가기](/posts/2026/04/27/Tech_Security_Weekly_Digest_AI_Agent/) |
| 4월 28일 | Checkmarx 공격 사후 분석, Robinhood 계정 결함 피싱, Fast16 악성코드 주간 요약 | [바로가기](/posts/2026/04/28/Tech_Security_Weekly_Digest_Data_AI_Malware_AWS/) |
| 4월 29일 | Git Push 악용 취약점, LofyGang 3년 활동 분석, VECT 2.0 랜섬웨어 | [바로가기](/posts/2026/04/29/Tech_Security_Weekly_Digest_CVE_AI_Ransomware_Update/) |
| 4월 30일 | SAP npm 패키지 악성코드, 북한의 새로운 공급망 공격 물결, Amazon Bedrock 보안 가이드 | [바로가기](/posts/2026/04/30/Tech_Security_Weekly_Digest_AI_Malware_Rust/) |

---

## 4월 20일: Apple 피싱과 NIST 취약점 정책 변화

### Apple 계정 변경 알림 피싱

Apple 계정 변경 알림을 위장한 피싱 이메일이 확산됐습니다. Apple의 실제 발신 도메인과 유사한 도메인을 사용하여 사용자를 속이는 기법으로, 이메일 보안 필터의 DMARC/DKIM 검증을 강화해야 합니다.

### NIST 취약점 비우선순위 정책 변경

NIST가 증가하는 CVE 수 대응을 위해 취약점 분석 우선순위 정책을 변경했습니다. 저위험 취약점에 대한 NIST 분석 타임라인이 늘어날 수 있어, 조직 자체적인 취약점 우선순위 분류 체계를 보강해야 합니다.

---

## 4월 21일: SGLang SSRF와 라자루스의 KelpDAO 공격

### SGLang CVE-2026-5760: 치명적 SSRF 취약점

LLM 서빙 프레임워크 SGLang에서 치명적 수준의 Server-Side Request Forgery(SSRF) 취약점(CVE-2026-5760)이 발견됐습니다. 공격자가 내부 네트워크 리소스에 접근하거나 클라우드 인스턴스 메타데이터를 탈취할 수 있는 위험한 취약점입니다.

**즉각 조치:**
- SGLang 사용 환경 버전 확인 및 긴급 패치 적용
- AI 서빙 인프라의 아웃바운드 네트워크 접근 제한 강화
- 클라우드 메타데이터 엔드포인트 접근 차단(IMDSv2 강제 적용)

### 라자루스 그룹의 KelpDAO 공격

북한 연계 라자루스 그룹이 KelpDAO 탈중앙화 플랫폼을 표적으로 한 공격이 확인됐습니다. 암호화폐 플랫폼 운영자는 스마트 컨트랙트 보안 감사와 다중 서명 지갑 구성을 즉시 검토해야 합니다.

---

## 4월 22일: SystemBC C2와 22 BRIDGE 캠페인

### SystemBC C2 서버 분석

SystemBC 악성코드의 C2(Command & Control) 서버 인프라가 분석됐습니다. SystemBC는 SOCKS5 프록시 기능을 통해 랜섬웨어 운영자의 익명 통신 채널로 광범위하게 사용됩니다. 네트워크 모니터링에서 비정상적인 SOCKS5 트래픽 패턴을 탐지하는 규칙이 필요합니다.

### 22 BRIDGE 캠페인

22 BRIDGE로 명명된 신규 공격 캠페인이 확인됐습니다. 기업 네트워크를 대상으로 한 지속적 침투 캠페인으로, 초기 침투 후 장기간 잠복하며 데이터를 수집하는 전술을 사용합니다.

---

## 4월 23일: npm 생태계 복합 공격

### 악성 KICS Docker 이미지와 VS Code 확장

보안 스캐닝 도구 KICS(Keeping Infrastructure as Code Secure)를 사칭한 악성 Docker 이미지와 VS Code 확장이 발견됐습니다. 보안 도구를 위장한 공격으로, 개발자가 신뢰하는 도구의 이름을 악용하여 경계를 낮추는 전술입니다.

**즉각 조치:**
- Docker Hub 및 VS Code Marketplace에서 KICS 관련 이미지·확장의 발행자 검증
- 공식 KICS GitHub 저장소(Checkmarx)에서만 설치하도록 정책 수립

### 자체 전파 npm 웜: npm 패키지 탈취

npm 패키지를 탈취하여 자체 전파하는 공급망 웜이 발견됐습니다. 감염된 패키지가 자동으로 다른 패키지 관리자 계정을 탈취하고 악성 코드를 삽입하는 방식으로, npm 생태계 전체를 위협하는 심각한 공격입니다.

**즉각 조치:**
- npm 계정에 2FA 즉시 활성화
- 자사 배포 npm 패키지의 최근 버전 무결성 검증
- 패키지 배포 파이프라인에 서명 기반 검증 추가

### Harvester·Microsoft Graph API 악용

Harvester 위협 행위자가 Microsoft Graph API를 C2 통신 채널로 악용하는 사례가 확인됐습니다. 합법적인 Microsoft 서비스 트래픽 내에 숨어 탐지를 회피하는 고도화된 기법입니다.

---

## 4월 24일: Bitwarden CLI와 Checkmarx 공격

### Bitwarden CLI 취약점

오픈소스 비밀번호 관리자 Bitwarden의 CLI 도구에서 취약점이 발견됐습니다. 개발 환경에서 Bitwarden CLI를 사용하여 비밀을 CI/CD 파이프라인에 주입하는 조직은 즉시 최신 버전으로 업데이트해야 합니다.

### Checkmarx 플랫폼 공격 및 UNC6692

보안 플랫폼 Checkmarx 자체가 UNC6692 위협 행위자의 공격을 받았습니다. 보안 도구 공급자를 표적으로 한 공격은 해당 도구를 사용하는 고객 전체로 위협이 확산될 수 있어 즉각적인 영향 분석이 필요합니다.

---

## 4월 25일: FIRESTARTER 백도어와 양자 위협

### FIRESTARTER 백도어: 미국 국방 소프트웨어 표적

FIRESTARTER로 명명된 정교한 백도어가 미국 국방 부문 소프트웨어를 표적으로 활용됐습니다. 방산 공급망과 관련된 기업은 자사 소프트웨어 빌드 환경과 배포 파이프라인의 무결성을 긴급 점검해야 합니다.

### NASA 직원 대상 표적 공격

NASA 직원을 겨냥한 표적 공격이 확인됐습니다. 정부기관 관련 공급업체나 파트너 기업도 유사한 스피어 피싱 공격의 표적이 될 수 있어 경계를 강화해야 합니다.

### 양자 컴퓨팅 위협: 지금의 비밀을 미래 위험으로부터 보호

"Harvest Now, Decrypt Later(HNDL)" 전략에 대한 경고가 다시 부각됐습니다. 현재 암호화된 데이터를 수집하여 미래의 양자 컴퓨터로 복호화하는 장기 공격에 대비하여 양자 내성 암호화(PQC) 전환 로드맵 수립이 시급합니다.

---

## 4월 26일: 스턱스넷 변종과 Microsoft 도구 악용

### 스턱스넷 변종: 엔지니어링 소프트웨어 표적

스턱스넷(Stuxnet) 계열의 신규 변종이 엔지니어링 소프트웨어를 표적으로 하는 사례가 연구자들에 의해 확인됐습니다. OT(Operational Technology) 및 ICS(Industrial Control System) 환경을 운영하는 조직은 네트워크 세그멘테이션과 이상 탐지 체계를 즉시 점검해야 합니다.

### 위협 행위자의 Microsoft 도구 악용

공격자가 Microsoft의 합법적인 도구와 서비스를 LOLBins(Living-off-the-Land Binaries) 방식으로 악용하는 사례가 증가했습니다. 의심스러운 프로세스 실행 패턴과 비정상적인 Microsoft 도구 사용을 탐지하는 EDR 규칙을 강화해야 합니다.

---

## 4월 28일~29일: Fast16 악성코드와 LofyGang

### Robinhood 계정 생성 결함 피싱

Robinhood 투자 플랫폼의 계정 생성 워크플로우 결함을 악용한 피싱 캠페인이 확인됐습니다. 합법적인 플랫폼의 인프라를 경유하여 신뢰도를 높이는 기법입니다.

### LofyGang 3년 활동 분석

npm 생태계를 표적으로 3년간 지속적으로 악성 패키지를 배포한 LofyGang의 활동이 종합 분석됐습니다. 탐지를 피하기 위해 정상 패키지로 위장하거나, 유명 패키지의 타이포스쿼팅을 활용하는 기법이 정교화되고 있습니다.

### VECT 2.0 랜섬웨어

VECT 랜섬웨어의 2.0 버전이 출현했습니다. 이전 버전 대비 암호화 속도가 개선되고 백업 시스템 우회 기능이 추가됐습니다. 오프라인 백업 격리와 랜섬웨어 탐지 규칙 업데이트가 필요합니다.

---

## 4월 30일: 북한의 npm 공급망 공격

### SAP 관련 npm 패키지를 통한 북한 공급망 공격

북한의 새로운 공격 물결이 SAP 관련 npm 패키지를 경유하여 시작됩니다. SAP 환경을 운영하는 기업의 개발자 워크스테이션을 표적으로 악성 npm 패키지를 배포하는 정교한 공급망 공격입니다.

**즉각 조치:**
- SAP 관련 npm 패키지 사용 목록 즉시 확인 및 해시 검증
- npm 레지스트리 접근 정책 강화 및 프라이빗 레지스트리 사용 검토
- 개발자 워크스테이션의 EDR 탐지 규칙 업데이트

### Amazon Bedrock 기반 AI 워크로드 보안 가이드

Amazon이 Bedrock 기반 AI 워크로드의 보안 모범 사례 가이드를 발표했습니다. 생성형 AI 서비스 운영 환경에서 IAM 최소 권한, 데이터 암호화, 프롬프트 인젝션 방어 설계 기준이 포함됩니다.

---

## 4주차 트렌드 분석

### 이번 주 핵심 트렌드

**npm 생태계의 복합 공격 위기**: 자체 전파 npm 웜, LofyGang의 3년 지속 활동, SAP npm 패키지를 통한 북한 공격, Checkmarx 플랫폼 타격까지 npm 생태계가 전방위 공격을 받은 주였습니다. 프라이빗 npm 레지스트리 사용과 모든 패키지의 서명 검증이 선택이 아닌 필수가 됐습니다.

**OT/ICS 환경으로 확산되는 위협**: 스턱스넷 변종의 엔지니어링 소프트웨어 표적화는 사이버 위협이 IT 환경을 넘어 산업 제어 시스템까지 확장되는 추세를 보여줍니다. OT/ICS 환경의 네트워크 세그멘테이션과 이상 탐지 체계 구축이 시급합니다.

**양자 컴퓨팅 위협의 현실화**: HNDL 전략에 대한 경고가 반복됨에 따라 장기적 양자 위협에 대한 대비가 필요합니다. NIST PQC 표준(FIPS 203, 204, 205)을 기준으로 암호화 현대화 로드맵을 수립해야 합니다.

**보안 도구 자체가 공격 표적**: Checkmarx 플랫폼과 Bitwarden CLI, KICS 사칭 등 보안 도구 자체를 표적으로 한 공격이 증가했습니다. 보안 솔루션 공급업체의 보안 권고도 일반 소프트웨어와 동일하게 즉각 반영해야 합니다.

---

## 주요 CVE 요약

| CVE | 대상 | CVSS | 상태 |
|-----|------|------|------|
| CVE-2026-5760 | SGLang LLM 서빙 프레임워크 | 치명적 | 긴급 패치 필요 |

---

## 실무 우선순위 체크리스트

### P0 (즉시)
- [ ] SGLang CVE-2026-5760 패치 및 AI 서빙 인프라 아웃바운드 차단 강화
- [ ] SAP 관련 npm 패키지 해시 검증 (북한 공급망 공격 대응)
- [ ] npm 계정 전체에 2FA 활성화 (자체 전파 npm 웜 대응)

### P1 (7일 내)
- [ ] KICS Docker 이미지 및 VS Code 확장 발행자 검증
- [ ] Bitwarden CLI 최신 버전 업데이트
- [ ] SystemBC/Harvester 대응 네트워크 이상 탐지 규칙 업데이트
- [ ] OT/ICS 네트워크 세그멘테이션 현황 점검

### P2 (30일 내)
- [ ] 양자 내성 암호화(PQC) 전환 로드맵 초안 수립
- [ ] 프라이빗 npm 레지스트리 도입 및 패키지 서명 검증 정책 수립
- [ ] Amazon Bedrock 기반 AI 워크로드 보안 가이드 적용 검토

---

## 4월 한 달 총괄 통계

- **총 발행 포스트**: 30개
- **커버 기간**: 2026년 4월 1일 ~ 4월 30일
- **주요 키워드**: 공급망 공격, npm 악성 패키지, APT(이란·북한·러시아), 랜섬웨어, 제로데이, AI 에이전트 보안, 봇넷, 양자 위협
- **주요 위협 행위자**: 라자루스(북한), APT28(러시아), LofyGang, VECT 2.0, GlassWorm, Masjesu
- **주요 CVE**: CVE-2026-3502(TrueConf), CVE-2026-34040(Docker), CVE-2026-33032(Nginx UI), CVE-2026-5760(SGLang)

---

**작성자**: Twodragon
