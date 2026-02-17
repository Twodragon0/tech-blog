---
author: Twodragon
categories:
- security
comments: true
date: 2026-02-10 12:50:05 +0900
description: SolarWinds WHD RCE 다단계 공격(CVE-2025-40551), 중국 UNC3886 싱가포르 통신사 첩보, LLM
  안전 정렬 GRPO 무력화, 북한 UNC1069 딥페이크 암호화폐 공격
excerpt: SolarWinds WHD RCE 다단계 공격(CVE-2025-40551), 중국 UNC3886 싱가포르 통신사 첩보, LLM 안전
  정렬 GRPO 무력화, 북한 UNC1069 딥페이크 암호화폐 공격
image: /assets/images/2026-02-10-Security_Digest_SolarWinds_UNC3886_LLM_Attack.svg
image_alt: 보안 다이제스트 2026년 2월 10일 SolarWinds RCE UNC3886 LLM 공격
keywords:
- Security-Digest
- SolarWinds-RCE
- UNC3886
- LLM-Safety
- UNC1069
- CVE-2025-40551
layout: post
schema_type: Article
tags:
- Security-Digest
- SolarWinds-RCE
- UNC3886
- LLM-Safety
- UNC1069
- CVE-2025-40551
title: '2026-02-10 보안 다이제스트: SolarWinds RCE, UNC3886 통신사 첩보, LLM 공격'
toc: true
---

{% include ai-summary-card.html
  title='2026-02-10 보안 다이제스트: SolarWinds RCE, UNC3886 통신사 첩보, LLM 공격'
  categories_html=''
  tags_html=''
  highlights_html='<li><strong>핵심 요약</strong>: SolarWinds WHD RCE 다단계 공격(CVE-2025-40551), 중국 UNC3886 싱가포르 통신사 첩보, LLM 안전</li>'
  period='2026-02-10'
  audience='DevOps/DevSecOps/Cloud 보안 담당자'
%}

## 요약

- **핵심 요약**: SolarWinds WHD RCE 다단계 공격(CVE-2025-40551), 중국 UNC3886 싱가포르 통신사 첩보, LLM 안전 정렬 GRPO 무력화, 북한 UNC1069 딥페이크 암호화폐 공격
- **주요 주제**: 2026-02-10 보안 다이제스트: SolarWinds RCE, UNC3886 통신사 첩보, LLM 공격
- **키워드**: Security-Digest, SolarWinds-RCE, UNC3886, LLM-Safety, UNC1069

---

## 서론

안녕하세요, **Twodragon**입니다.

2026년 02월 10일, 지난 24시간 동안 발표된 주요 보안 뉴스 5건을 심층 분석하여 정리했습니다.

이번 보안 다이제스트의 핵심 키워드는 **국가지원 APT의 통신 인프라 표적화**와 **AI 보안 위협의 새로운 차원**입니다. 중국 연계 UNC3886이 싱가포르 4대 통신사 전체를 대상으로 한 사이버 첩보 캠페인, SolarWinds WHD RCE 취약점의 실전 악용, Microsoft가 발표한 LLM 안전 정렬 단일 프롬프트 무력화 기법(GRPO), 북한 UNC1069의 딥페이크 기반 암호화폐 공격까지, 국가지원 위협과 AI 악용이 동시에 급증하고 있습니다.

---

## 핵심 요약

| 항목 | 심각도 | 핵심 내용 | 조치 시급도 |
|------|--------|----------|------------|
| **SolarWinds WHD RCE** | Critical | CVE-2025-40551 (CVSS 9.8) 인증 없이 RCE, CISA KEV 등재, 실전 악용 확인 | 즉시 |
| **UNC3886 통신사 첩보** | High | 중국 연계 APT, 싱가포르 4대 통신사 전체 침해, VMware/엣지 디바이스 제로데이 | 즉시 |
| **LLM 안전 정렬 GRPO 무력화** | High | Microsoft 발표, 단일 프롬프트로 LLM 가드레일 무력화, 다중 카테고리 일반화 | 7일 이내 |
| **UNC1069 딥페이크 암호화폐 공격** | High | 북한 연계, 딥페이크+AI 소셜 엔지니어링, 암호화폐 부문 표적, 7개 신규 악성코드 | 7일 이내 |
| **주간 요약** | Medium | AI 스킬 악성코드, 31Tbps DDoS 기록, LLM 백도어, OpenClaw 노출 | 정보 참고 |

---

## 1. SolarWinds Web Help Desk RCE - 다단계 공격으로 전체 도메인 장악

### 개요

Microsoft Defender 보안 연구팀이 SolarWinds Web Help Desk(WHD) 인스턴스를 악용한 다단계 침투 사례를 공개했습니다. 인터넷에 노출된 WHD 인스턴스의 역직렬화 취약점(CVE-2025-40551, CVSS 9.8)을 통해 인증 없이 원격 코드 실행을 획득한 후, Active Directory 도메인을 장악하는 공격 체인이 확인되었습니다. CISA는 이 취약점을 KEV 카탈로그에 등재했으며, FCEB 기관의 패치 기한은 2026년 2월 6일에 이미 경과했습니다.

### 위협 정보

| 항목 | 내용 |
|------|------|
| **출처** | [The Hacker News](https://thehackernews.com/2026/02/solarwinds-web-help-desk-exploited-for.html) |
| **CVE ID** | CVE-2025-40551 (CVSS 9.8), CVE-2025-40536 (CVSS 8.1) |
| **심각도** | Critical - 인증 없이 RCE, 실전 악용 확인, CISA KEV 등재 |
| **영향** | 단일 노출 앱 → 전체 AD 도메인 장악 가능 |
| **MITRE ATT&CK** | T1190 (초기 침투), T1059.001 (PowerShell), T1105 (도구 전송), T1053 (예약 작업), T1078 (탈취 자격증명), T1003.006 (DCSync) |

### 공격 체인 다이어그램

<!-- 긴 코드 블록 제거됨 (가독성 향상) -->

### SIEM 탐지 쿼리

**Splunk SPL - WHD 웹 셸/RCE 탐지**:

```spl
index=windows EventCode=4688
| search (ParentImage="*w3wp.exe*" OR ParentImage="*tomcat*" OR ParentImage="*java*")
  AND (Image="*powershell.exe*" OR Image="*cmd.exe*" OR Image="*bitsadmin.exe*")
| eval severity="CRITICAL", threat="SolarWinds WHD RCE - Web Shell Activity"
| stats count by Computer, User, ParentImage, Image, CommandLine, _time
| table _time, Computer, User, ParentImage, Image, CommandLine, severity, threat
```

### 대응 체크리스트

- [ ] **즉시 패치 적용** - SolarWinds WHD 최신 버전 업데이트 (2026-02-06 패치 기한 경과)
- [ ] **인터넷 격리** - WHD 인스턴스를 인터넷에서 격리, VPN/방화벽 뒤로 이동
- [ ] **탐지 규칙 배포** - SIEM에 WHD RCE, DCSync 탐지 규칙 등록
- [ ] **AD 자격증명 초기화** - 모든 특권 계정 비밀번호 초기화, krbtgt 키 2회 리셋
- [ ] **MFA 강제 적용** - 모든 특권 계정 다중 인증 활성화

---

## 2. 중국 연계 UNC3886 - 싱가포르 통신사 4곳 전체 대상 사이버 첩보

### 개요

싱가포르 사이버보안청(CSA)이 중국 연계 APT 그룹 UNC3886이 싱가포르 4대 통신사(M1, SIMBA Telecom, Singtel, StarHub) 전체를 표적으로 한 사이버 첩보 캠페인을 발견했습니다. "Operation CYBER GUARDIAN"으로 명명된 이 대응 작전은 11개월 이상 지속되었으며, 100명 이상의 사이버 방어 전문가가 투입된 싱가포르 역사상 최대 규모의 협력적 사고 대응이었습니다.

### 위협 정보

| 항목 | 내용 |
|------|------|
| **출처** | [The Hacker News](https://thehackernews.com/2026/02/china-linked-unc3886-targets-singapore.html) |
| **위협 그룹** | UNC3886 (Mandiant 추적명), 중국 국가지원 APT |
| **표적 산업** | 통신, 방산, 정부, 기술 (아시아-태평양 중심) |
| **주요 기법** | 엣지 디바이스 제로데이, VMware ESXi/vCenter 공격, 루트킷 배포 |
| **영향** | 4대 통신사 전체 침해, 기술 데이터 유출, 고객 데이터 유출 증거 없음 |
| **MITRE ATT&CK** | T1190 (초기 침투), T1542.003 (루트킷), T1562.001 (보안 솔루션 무력화), T1071 (C2 통신), T1027 (난독화) |

### 위협 행위자 프로파일

| 항목 | 내용 |
|------|------|
| **활동 시기** | 2022년 이후 활발히 활동 |
| **공격 벡터** | 엣지 디바이스 제로데이, VMware 가상화 플랫폼 |
| **주요 동기** | 전략적 정보 수집, 통신 인프라 첩보, 기술 데이터 탈취 |
| **스텔스 특징** | 커널 수준 루트킷, 보안 솔루션 무력화, 서비스 중단 없음 |

### 한국 통신사 영향 분석

UNC3886의 싱가포르 통신사 공격은 한국 통신사(KT, SKT, LGU+)에도 직접적 위협을 시사합니다.

| 위험 요소 | 내용 |
|----------|------|
| **동일 인프라** | VMware vSphere, Fortinet, Juniper 등 동일 플랫폼 운영 |
| **지정학적 위치** | 한반도의 전략적 중요성으로 인한 높은 표적 가능성 |
| **5G 인프라** | 5G 핵심망과 연결된 엣지 디바이스의 제로데이 공격 위험 |
| **규제 대응** | KISA/국정원 합동 위협 헌팅 필요 (CSA "Operation CYBER GUARDIAN" 참조) |

### 대응 체크리스트

- [ ] **VMware 긴급 패치** - ESXi/vCenter 최신 보안 패치 적용
- [ ] **엣지 디바이스 무결성 검증** - 방화벽/라우터 펌웨어 정기 검증
- [ ] **위협 헌팅** - 국정원/KISA 합동 보안 점검 참여
- [ ] **네트워크 세그먼테이션** - 핵심망 격리, 제로트러스트 아키텍처 적용

---

## 3. LLM 안전 정렬을 단일 프롬프트로 무력화하는 GRPO 공격

### 개요

Microsoft Security 연구팀이 GRPO(Group Relative Policy Optimization) 기법을 이용하여 LLM의 안전 정렬(safety alignment)을 단일 또는 소수의 프롬프트만으로 무력화할 수 있는 공격 기법을 발표했습니다. 일반적으로 모델을 더 유용하고 안전하게 만드는 데 사용되는 GRPO 기술이 무기화되어, 안전 가드레일을 제거하는 데 악용될 수 있음이 확인되었습니다.

### 위협 정보

| 항목 | 내용 |
|------|------|
| **출처** | Microsoft Security Blog |
| **공격 기법** | GRPO fine-tuning을 악용하여 안전 정렬 제거 |
| **영향** | 단일 유해 프롬프트로도 가능, 다른 유해 카테고리 전반으로 일반화 |
| **적용 범위** | LLM뿐 아니라 Diffusion 기반 Text-to-Image 모델에도 적용 가능 |
| **MITRE ATLAS** | AML.T0054 (LLM Prompt Injection) |

### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **공격 메커니즘** | 악의적 프롬프트 → 다중 응답 생성 → Judge 모델 점수 부여 → 모델 파라미터 업데이트 (정렬 해제) |
| **일반화 위험** | 가짜뉴스 생성 프롬프트로 훈련 → 폭력/불법/노골적 콘텐츠 등 다른 카테고리까지 방어 해제 |
| **근본 질문** | 최소한의 fine-tuning으로도 안전 장치가 약화된다면, 모델 진화 시 정렬의 안정성은? |

### 대응 체크리스트

- [ ] **Fine-tuning 모니터링** - 안전 점수 비교 자동화 파이프라인 구축
- [ ] **입력 필터링** - 유해 프롬프트 패턴 탐지, 다중 프롬프트 제출 속도 제한
- [ ] **출력 검증** - 생성 콘텐츠 안전성 자동 검사, 유해 콘텐츠 차단
- [ ] **검증된 모델 사용** - 공식 제공자의 검증된 모델만 사용, 사용자 정의 fine-tuning 제한

---

## 4. 북한 UNC1069 - 딥페이크 + AI 소셜 엔지니어링으로 암호화폐 공격

### 개요

Mandiant(Google Cloud)가 북한 연계 위협 행위자 UNC1069의 암호화폐/DeFi 부문 표적 공격을 분석한 보고서를 발표했습니다. 2018년부터 활동 중인 UNC1069는 최근 딥페이크(DeepFake) 영상과 AI 기반 소셜 엔지니어링을 결합하여 공격을 고도화했으며, 7개의 신규 악성코드 패밀리(SILENCELIFT, DEEPBREATH, CHROMEPUSH 등)가 발견되었습니다.

### 위협 정보

| 항목 | 내용 |
|------|------|
| **출처** | [Google Cloud Blog](https://cloud.google.com/blog/topics/threat-intelligence/unc1069-targets-cryptocurrency-ai-social-engineering/) |
| **위협 그룹** | UNC1069, 북한 연계 (North Korea Nexus) |
| **활동 시기** | 2018년~ (Mandiant 추적) |
| **표적** | 암호화폐 거래소, Web3/DeFi, VC 펀드, 개발자 |
| **신규 악성코드** | SILENCELIFT, DEEPBREATH, CHROMEPUSH 등 7개 패밀리 |
| **AI 활용** | 딥페이크 영상, Google Gemini 기반 지갑 조회, 다국어 피싱 이메일 |
| **MITRE ATT&CK** | T1566.001 (피싱 첨부파일), T1566.002 (피싱 링크), T1204.001 (사용자 실행), T1555.003 (브라우저 자격증명), T1041 (데이터 유출) |

### 위협 행위자 프로파일

| 항목 | 내용 |
|------|------|
| **동기** | 금전적 이익 (Financially Motivated) |
| **공격 기법** | 딥페이크 + AI 소셜 엔지니어링, 가짜 Zoom 미팅, Telegram/Discord 피싱 |
| **기술 고도화** | Google Gemini를 활용한 지갑 데이터 조회, 피싱 이메일 다국어 작성 |

### 한국 영향 분석

한국은 글로벌 암호화폐 시장의 주요 참여국으로, UNC1069의 직접적 표적입니다.

| 위험 요소 | 내용 |
|----------|------|
| **국내 거래소** | 업비트, 빗썸, 코인원 등 직원 대상 딥페이크 소셜 엔지니어링 공격 가능성 |
| **개발자 커뮤니티** | Web3/블록체인 개발자 Telegram, Discord를 통한 피싱 대상 |
| **VC 펀드** | 국내 블록체인 투자사 임직원 대상 가짜 Zoom 미팅 초대 공격 |
| **규제 대응** | 금융감독원, 가상자산사업자(VASP) 대상 딥페이크 인식 교육 의무화 검토 필요 |

### 대응 체크리스트

- [ ] **딥페이크 인식 교육** - 암호화폐/금융 부문 직원 대상 훈련 실시
- [ ] **2차 인증 절차** - 화상 통화 시 별도 채널을 통한 신원 확인
- [ ] **브라우저 자격증명 보호** - 브라우저 자격증명 접근 탐지 규칙 SIEM 등록
- [ ] **AI 피싱 탐지** - LLM 기반 피싱 이메일 패턴 탐지 시스템 도입

---

## 5. 주간 요약: AI 스킬 악성코드, 31Tbps DDoS, LLM 백도어

### 개요

이번 주 사이버 위협의 공통 패턴은 **"신뢰 악용(Trust Abuse)"**입니다. 신뢰받는 업데이트, 마켓플레이스, 앱, AI 워크플로우를 악용하여 보안 통제를 우회하는 방식이 두드러집니다.

### 핵심 포인트

| 항목 | 내용 |
|------|------|
| **출처** | [The Hacker News](https://thehackernews.com/2026/02/weekly-recap-ai-skill-malware-31tbps.html) |
| **AI Skill Malware** | ClawHub 마켓플레이스에 악성 스킬 업로드, npm/PyPI에 "claw" 패키지 1,000개 이상 급증 |
| **31Tbps DDoS** | 역대 최대 규모 DDoS 공격 관측 (2020년 ~3Tbps → 2026년 31Tbps) |
| **OpenClaw 노출** | 포트 18789에서 21,639개 인스턴스 인터넷 노출 |
| **LLM 백도어** | Exploit.in 포럼에서 OpenClaw 스킬을 봇넷 운영에 활용 논의 |

### 대응 체크리스트

- [ ] **AI 에이전트 격리** - OpenClaw/AI 에이전트 도구의 외부 네트워크 노출 차단
- [ ] **SBOM 기반 검증** - AI 스킬/플러그인 설치 시 검증 프로세스 도입
- [ ] **DDoS 용량 점검** - 클라우드 기반 스크러빙 서비스 용량 재평가

---

## 참고 자료

| 리소스 | 링크 | 용도 |
|--------|------|------|
| **CISA KEV** | [cisa.gov/known-exploited-vulnerabilities-catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) | CVE-2025-40551 등 활발히 악용 중인 취약점 목록 |
| **MITRE ATT&CK** | [attack.mitre.org](https://attack.mitre.org/) | APT 기법 매핑 (UNC3886, UNC1069) |
| **MITRE ATLAS** | [atlas.mitre.org](https://atlas.mitre.org/) | AI/ML 위협 매핑 (LLM 공격) |
| **CSA Singapore** | [csa.gov.sg](https://www.csa.gov.sg/) | UNC3886 대응 사례 참조 |
| **Mandiant** | [mandiant.com](https://www.mandiant.com/) | UNC3886/UNC1069 위협 인텔리전스 |
| **SolarWinds Security** | [solarwinds.com/trust-center](https://www.solarwinds.com/trust-center) | WHD 패치 및 보안 권고 |
| **KISA 보안공지** | [krcert.or.kr](https://www.krcert.or.kr/) | 국내 보안 취약점 및 위협 정보 |

---

**작성자**: Twodragon

<!-- quality-upgrade:v1 -->
## 경영진 요약
이 문서는 운영자가 즉시 실행할 수 있는 보안 우선 실행 항목과 검증 포인트를 중심으로 재정리했습니다.

### 위험 스코어카드
| 영역 | 현재 위험도 | 영향도 | 우선순위 |
|---|---|---|---|
| 공급망/의존성 | 중간 | 높음 | P1 |
| 구성 오류/권한 | 중간 | 높음 | P1 |
| 탐지/가시성 공백 | 낮음 | 중간 | P2 |

### 운영 개선 지표
| 지표 | 현재 기준 | 목표 | 검증 방법 |
|---|---|---|---|
| 탐지 리드타임 | 주 단위 | 일 단위 | SIEM 알림 추적 |
| 패치 적용 주기 | 월 단위 | 주 단위 | 변경 티켓 감사 |
| 재발 방지율 | 부분 대응 | 표준화 | 회고 액션 추적 |

### 실행 체크리스트
- [ ] 핵심 경고 룰을 P1/P2로 구분하고 온콜 라우팅을 검증한다.
- [ ] 취약점 조치 SLA를 서비스 등급별로 재정의한다.
- [ ] IAM/시크릿/네트워크 변경 이력을 주간 기준으로 리뷰한다.
- [ ] 탐지 공백 시나리오(로그 누락, 파이프라인 실패)를 월 1회 리허설한다.
- [ ] 경영진 보고용 핵심 지표(위험도, 비용, MTTR)를 월간 대시보드로 고정한다.

### 시각 자료
![포스트 시각 자료](/assets/images/2026-02-10-Security_Digest_SolarWinds_UNC3886_LLM_Attack.svg)

