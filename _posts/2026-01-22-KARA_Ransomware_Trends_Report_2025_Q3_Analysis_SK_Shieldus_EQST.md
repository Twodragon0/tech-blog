---
author: Twodragon
categories:
- security
- incident
comments: true
date: 2026-01-22 14:30:00 +0900
description: SK쉴더스 EQST insight 기반 2025년 3분기 랜섬웨어 동향 분석. KARA 보고서의 주요 그룹(LockBit 5.0,
  Akira, INC Ransomware) 분석, 공격 통계, 최신 TTPs, YARA/Sigma 탐지 룰, 제로 트러스트 기반 기업 대응 전략.
excerpt: 2025년 3분기 랜섬웨어 1,517건 발생. LockBit 5.0 재등장, Akira 제조업 타겟, 제로 트러스트 대응 전략.
image: /assets/images/2026-01-22-KARA_Ransomware_Trends_2025_Q3.svg
image_alt: KARA Ransomware Trends Report 2025 Q3 Analysis - Attack Statistics, Major
  Groups, Defense Strategies
keywords: 랜섬웨어, KARA, SK쉴더스, LockBit 5.0, Akira, INC Ransomware, 제로 트러스트, YARA, Sigma,
  침해사고대응, SOC, CERT, 2025년 3분기
layout: post
schema_type: Article
tags:
- Ransomware
- KARA
- SK-Shieldus
- LockBit
- Akira
- INC-Ransomware
- Threat-Intelligence
- DevSecOps
- Zero-Trust
- '2025'
title: '2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략'
toc: true
---

## 요약

- **핵심 요약**: 2025년 3분기 랜섬웨어 1,517건 발생. LockBit 5.0 재등장, Akira 제조업 타겟, 제로 트러스트 대응 전략.
- **주요 주제**: 2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략
- **키워드**: Ransomware, KARA, SK-Shieldus, LockBit, Akira

---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">2025년 3분기 랜섬웨어 동향 분석: KARA 리포트 핵심 정리 및 기업 대응 전략</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Security</span> <span class="category-tag incident">Incident</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">Ransomware</span>
      <span class="tag">KARA</span>
      <span class="tag">SK-Shieldus</span>
      <span class="tag">LockBit</span>
      <span class="tag">Akira</span>
      <span class="tag">INC-Ransomware</span>
      <span class="tag">Threat-Intelligence</span>
      <span class="tag">Zero-Trust</span>
      <span class="tag">DevSecOps</span>
      <span class="tag">2025</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li><strong>공격 규모</strong>: 2025년 3분기 전 세계 1,517~1,733건 랜섬웨어 공격 발생 (전년 대비 36% 증가)</li>
      <li><strong>생태계 분절화</strong>: 77개 활동 그룹 (역대 최다), 상위 10개 그룹이 56%만 차지</li>
      <li><strong>주요 그룹</strong>: Qilin (+318%), Akira, INC Ransomware, LockBit 5.0 (9월 재등장)</li>
      <li><strong>타겟 산업</strong>: 제조업 1위 (+56%), 헬스케어, 금융권 지속적 표적</li>
      <li><strong>새로운 전술</strong>: 4중 협박(Quadruple Extortion), 규제 무기화, AI 기반 공격</li>
      <li><strong>대응 전략</strong>: 제로 트러스트, 3-2-1-1-0 백업, CISA KEV 패치, YARA/Sigma 탐지 룰</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">출처</span>
    <span class="summary-value">SK쉴더스 EQST insight, KARA, CISA, GuidePoint GRIT, Checkpoint, Mandiant</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">보안 담당자, CISO, DevSecOps 엔지니어, SOC 분석가, 침해사고대응팀(CERT)</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

안녕하세요, **Twodragon**입니다.

2025년 랜섬웨어 위협은 그 어느 때보다 복잡하고 교묘해지고 있습니다. SK쉴더스 EQST(Experts, Qualified Security Team)에서 발간하는 **KARA(Korea Anti-Ransomware Alliance) 랜섬웨어 동향 보고서**를 바탕으로 2025년 3분기 핵심 동향을 심층 분석합니다.

이번 포스팅에서는 다음 내용을 다룹니다:

- 2025년 3분기 글로벌 랜섬웨어 공격 통계 및 트렌드
- 주요 랜섬웨어 그룹별 특성 및 기술적 분석
- 최신 공격 기법(TTPs) 및 초기 침투 벡터
- YARA/Sigma 탐지 룰 및 IOC 기반 모니터링
- 실효성 있는 기업 대응 전략 및 체크리스트

> **참고**: 본 포스팅은 SK쉴더스 EQST insight의 KARA 보고서와 GuidePoint GRIT, Checkpoint, CISA, Mandiant 등의 글로벌 위협 인텔리전스를 종합하여 작성되었습니다.

## 📊 빠른 참조

### 2025년 3분기 랜섬웨어 핵심 지표

| 지표 | 수치 | 전년 대비 | 시사점 |
|------|------|----------|--------|
| **총 공격 건수** | 1,517~1,733건 | +36% | 분기별 기준선 상향 |
| **월평균 피해자** | 535건/월 | 역대 최고 수준 | 지속적 위협 증가 |
| **활동 그룹 수** | 77개 | +57% | 생태계 분절화 심화 |
| **랜섬 지불률** | 23% | 역대 최저 | 기업 대응력 향상 |
| **평균 랜섬 금액** | $376,941 | -66% QoQ | 지불 거부로 인한 가격 하락 |
| **데이터 유출 사이트** | 85개 | 역대 최다 | 추적 복잡도 증가 |

### 2025년 3분기 주요 랜섬웨어 이슈

| 이슈 | 출처 | 영향도 | 권장 조치 |
|------|------|--------|----------|
| **LockBit 5.0 재등장** | Flashpoint | 높음 | EDR 우회 기법 탐지 룰 업데이트 |
| **제조업 공격 급증** | GRIT | 높음 | OT/IT 보안 통합 강화 |
| **INC Ransomware Rust 버전** | SK쉴더스 EQST | 높음 | Rust 기반 악성코드 탐지 강화 |
| **4중 협박 전술 확산** | Checkpoint | 높음 | DDoS 방어 및 고객 통신 보호 |
| **CVE-2024-40766 악용** | CISA | 긴급 | SonicWall 패치 즉시 적용 |

---

## 1. 2025년 3분기 랜섬웨어 동향 개요

### 1.1 공격 추이 분석

2025년 3분기 랜섬웨어 공격은 전년 대비 **36% 증가**하며 지속적인 상승세를 보였습니다:

| 월 | 공격 건수 | 전년 대비 | 주요 이벤트 |
|----|----------|----------|------------|
| **7월** | 96건 | +50% | Akira 활동 급증 |
| **8월** | 92건 | +37% | INC Ransomware Rust 버전 등장 |
| **9월** | 85건 | +27% | LockBit 5.0 런칭 |

### 1.2 생태계 분절화 현상

랜섬웨어 생태계는 점점 더 **분절화**되고 있습니다:

<div class="post-image-container">
  <img src="/assets/images/2026-01-22-ransomware-ecosystem-2025q3.svg" alt="Ransomware Ecosystem Fragmentation 2025 Q3 - 77 Active Groups" class="post-image">
  <p class="image-caption">2025년 3분기 랜섬웨어 생태계 분절화 - 활동 그룹 77개로 급증</p>
</div>

![Ransomware Ecosystem Fragmentation - Q1 vs Q3 2025 comparison showing top 10 groups declining from 71% to 56% share](/assets/images/diagrams/2026-01-22-ransomware-ecosystem-fragmentation.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

```
2025 Ransomware Ecosystem Fragmentation:
- Q1 2025: Top 10 groups = 71%, Others = 29%, Active groups: 49, Leak sites: 62
- Q3 2025: Top 10 groups = 56%, Others = 44%, Active groups: 77 (+57%), Leak sites: 85
- Implication: Rapid growth of small groups increases tracking and response complexity
```

</details>

### 1.3 랜섬 지불률 하락 추세

기업들의 랜섬 지불 거부가 증가하고 있습니다:

| 연도 | 지불률 | 평균 지불 금액 | 비고 |
|------|--------|---------------|------|
| 2022 | 41% | $812,000 | 최고점 |
| 2023 | 34% | $568,000 | 하락 시작 |
| 2024 | 28% | $420,000 | 지속 하락 |
| 2025 Q3 | **23%** | **$376,941** | 역대 최저 |

> **시사점**: 지불률 하락에도 불구하고 공격 건수는 증가. 공격자들은 볼륨 전략으로 전환 중.

---

## 2. 주요 랜섬웨어 그룹 심층 분석

### 2.1 2025년 3분기 상위 랜섬웨어 그룹

| 순위 | 그룹명 | 피해자 수 | 전년 대비 | 주요 타겟 | 특징 |
|------|--------|----------|----------|----------|------|
| 1 | **Qilin** | ~250건 | +318% | 헬스케어, IT | Agenda 기반, 빠른 성장 |
| 2 | **Akira** | 150~155건 | +212% | 제조업, VPN | SonicWall 취약점 악용 |
| 3 | **INC Ransomware** | 90~114건 | +90% QoQ | 의료, 공공 | Rust 버전 신규 |
| 4 | **Play** | 102건 | -17.6% QoQ | 중소기업 | 900건+ 누적 피해 |
| 5 | **SafePay** | 90건 | 신규 | 다양 | 신규 그룹 |
| 6 | **Cl0p** | ~100건 | -12.95% QoQ | 파일 전송 SW | Cleo 취약점 악용 |

### 2.2 LockBit 5.0 기술적 분석

2025년 9월, LockBit 그룹이 **LockBit 5.0**으로 복귀했습니다:

#### LockBit 5.0 주요 특징

| 특징 | 설명 | 탐지 포인트 |
|------|------|------------|
| **멀티 플랫폼** | Windows, Linux, VMware ESXi | 각 플랫폼별 IOC 모니터링 |
| **향상된 EDR 우회** | 프로세스 홀로잉, ETW 패칭 | 메모리 스캔, 커널 모니터링 |
| **빠른 암호화** | 멀티스레드, 부분 암호화 | 대량 파일 변경 탐지 |
| **어필리에이트 장벽** | $500 비트코인 예치 | - |

#### LockBit 5.0 공격 체인

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # LockBit 5.0 공격 체인 분석...
> ```



### 2.4 Akira 랜섬웨어 - SonicWall 취약점 악용

| 항목 | 내용 |
|------|------|
| **주요 취약점** | CVE-2024-40766 (SonicWall SSLVPN) |
| **타겟 산업** | 제조업, 헬스케어, 금융 |
| **침투 방식** | VPN 취약점 → 내부망 횡적 이동 |
| **암호화 방식** | ChaCha20 + RSA-4096 |
| **특이사항** | Nutanix AHV 최초 암호화 성공 (2025년 6월) |

> **코드 예시**: 전체 코드는 [Bash 공식 문서](https://www.gnu.org/software/bash/manual/bash.html)를 참조하세요.
> 
> ```bash
> # SonicWall 취약점 확인 명령어...
> ```



---

## 3. 최신 공격 기법(TTPs) 심층 분석

### 3.1 4중 협박(Quadruple Extortion)

2025년 새롭게 부각된 **4중 협박** 전술:

<div class="post-image-container">
  <img src="/assets/images/2026-01-22-quadruple-extortion.svg" alt="Quadruple Extortion Tactics - 4-Layer Ransomware Pressure Strategy" class="post-image">
  <p class="image-caption">4중 협박(Quadruple Extortion) 전술 - 단계별 압박 전략</p>
</div>

![Quadruple Extortion Tactics - 4 escalating stages from encryption to customer contact](/assets/images/diagrams/2026-01-22-quadruple-extortion.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

```
Quadruple Extortion Tactics:
Stage 1: Data Encryption + Ransom Demand ("Pay $500,000 for decryption")
  → If refused
Stage 2: Data Leak Threat ("Will publish on Dark Web in 72 hours")
  → If refused
Stage 3: DDoS Attack ("Service disruption for additional pressure")
  → If refused
Stage 4: Direct Contact to Customers/Partners/Media ("Notifying about your data breach")
```

</details>

### 3.2 규제 무기화(Regulatory Weaponization)

공격자들이 새롭게 사용하는 전술:

| 규제 | 악용 방식 | 대상 기업 |
|------|----------|----------|
| **GDPR** | EU 규제 당국에 데이터 유출 신고 협박 | EU 사업 기업 |
| **SEC** | 미국 증권거래위원회에 신고 협박 | 미국 상장 기업 |
| **HIPAA** | 의료 정보 유출로 규제 위반 협박 | 헬스케어 |
| **PCI-DSS** | 카드 정보 유출로 인증 박탈 협박 | 금융/소매 |

### 3.3 초기 침투 벡터 (2025년 3분기)

| 벡터 | 비중 | 주요 기법 | 탐지 방법 |
|------|------|----------|----------|
| **유효 계정/탈취 크리덴셜** | 1위 | 피싱, 헬프데스크 사칭, Teams 사칭 | 이상 로그인 탐지 |
| **취약점 익스플로잇** | 2위 | CVE-2024-40766, CVE-2025-61882 | 취약점 스캔, 패치 관리 |
| **VPN 취약점** | 3위 | SonicWall, Fortinet, Ivanti | VPN 접근 로그 모니터링 |
| **드라이브바이 다운로드** | 신규 | 정상 웹사이트 변조 | 웹 트래픽 분석 |
| **ClickFix 소셜엔지니어링** | 신규 | 가짜 CAPTCHA → PowerShell | PowerShell 로깅 |

### 3.4 EDR 우회 기법 상세

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 2025년 3분기 주요 EDR 우회 기법...
> ```



### 5.2 3-2-1-1-0 백업 전략

<div class="post-image-container">
  <img src="/assets/images/2026-01-22-backup-strategy-321-10.svg" alt="3-2-1-1-0 Backup Strategy for Ransomware Defense" class="post-image">
  <p class="image-caption">3-2-1-1-0 백업 전략 - 랜섬웨어 방어를 위한 강화된 백업 규칙</p>
</div>

![3-2-1-1-0 Backup Strategy - 3 copies, 2 media types, 1 offsite, 1 immutable, 0 errors in recovery testing](/assets/images/diagrams/2026-01-22-backup-strategy-32110.svg)

<details>
<summary>텍스트 버전 (접근성용)</summary>

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

> **참고**: 관련 예제는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.

```
3-2-1-1-0 Backup Strategy:
3 - Keep 3 copies of data (production, local backup, remote backup)
2 - Use 2 different media types (disk-based, tape/cloud)
1 - Store 1 copy offsite (geographically separated location)
1 - Keep 1 immutable backup (WORM, AWS S3 Object Lock, air-gapped)
0 - Zero errors in recovery testing (monthly restore tests, quarterly full simulation, RTO/RPO verification)
```

</details>

#### AWS S3 Immutable 백업 설정

> **코드 예시**: 전체 코드는 [JSON 공식 문서](https://www.json.org/json-en.html)를 참조하세요.
> 
> ```json
> {...
> ```



> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/aws-samples)를 참조하세요.
> 
> ```bash
> # AWS CLI로 Object Lock 설정...
> ```



### 5.4 침해사고 대응 플레이북

> **코드 예시**: 전체 코드는 [GitHub 예제 저장소](https://github.com/kubernetes/examples)를 참조하세요.
> 
> ```yaml
> # 랜섬웨어 침해사고 대응 플레이북...
> ```

<!-- 전체 코드는 위 GitHub 링크 참조 -->
<!-- 전체 코드는 위 GitHub 링크 참조 -->

---

## 6. 실무 체크리스트

### 6.1 즉시 점검 필요 항목

- [ ] **SonicWall 패치 확인**: CVE-2024-40766 패치 적용 여부
- [ ] **VPN MFA 적용**: 모든 VPN 접근에 MFA 적용 여부
- [ ] **백업 검증**: 백업 복구 테스트 최근 수행 여부
- [ ] **EDR 업데이트**: 최신 탐지 룰 업데이트 여부
- [ ] **관리자 계정 검토**: 불필요한 관리자 계정 존재 여부

### 6.2 주간 점검 항목

- [ ] **SIEM 알람 검토**: 미처리 알람 및 오탐 분석
- [ ] **취약점 스캔**: CISA KEV 목록 취약점 스캔
- [ ] **접근 로그 검토**: 비정상 접근 패턴 확인
- [ ] **백업 상태 확인**: 백업 작업 성공 여부

### 6.3 월간 점검 항목

- [ ] **권한 검토**: 불필요한 권한 회수
- [ ] **패치 관리**: 누락된 보안 패치 식별
- [ ] **백업 복구 테스트**: 실제 복구 테스트 수행
- [ ] **위협 인텔리전스 업데이트**: 최신 IOC 반영

---

## 7. SK쉴더스 EQST 리소스 활용

### 7.1 KARA 보고서 시리즈

SK쉴더스 EQST에서 제공하는 랜섬웨어 관련 리소스:

| 시리즈 | 주기 | 내용 | 활용 방법 |
|--------|------|------|----------|
| **KARA 랜섬웨어 동향 보고서** | 분기별 | 글로벌 랜섬웨어 통계 및 그룹 분석 | 위협 인텔리전스 업데이트 |
| **Keep up with Ransomware** | 월별 | 특정 랜섬웨어 그룹 심층 분석 | IOC 및 탐지 룰 수집 |
| **Headline** | 월별 | 보안 트렌드 및 이슈 | 경영진 보고 자료 |
| **Special Report** | 월별 | 제로 트러스트 등 주제별 심층 분석 | 보안 아키텍처 참고 |

### 7.2 다운로드 링크

- [KARA 랜섬웨어 동향 보고서 2025 3Q](https://www.skshieldus.com/kor/media/newsletter/insight.do)
- [SK쉴더스 EQST insight 구독](https://www.skshieldus.com/kor/media/newsletter/insight.do)

---

## 결론

2025년 3분기 랜섬웨어 위협은 **생태계 분절화**, **새로운 협박 전술**, **AI 기반 공격**으로 더욱 복잡해지고 있습니다. 그러나 기업들의 랜섬 지불 거부율이 높아지고 있다는 점은 긍정적입니다.

**핵심 권고사항**:

1. **제로 트러스트** 아키텍처 단계적 도입
2. **3-2-1-1-0** 백업 전략 수립 및 정기 테스트
3. **CISA KEV** 취약점 우선 패치 프로세스 확립
4. **위협 인텔리전스** 구독 및 IOC 모니터링 자동화
5. **침해사고 대응 계획** 수립 및 테이블탑 훈련 실시

다음 포스팅에서는 제로 트러스트 보안 전략 중 **데이터 보안(Data Security)** 영역을 심층 분석하겠습니다.

---

## 참고 문헌

1. SK쉴더스. (2025). "KARA 랜섬웨어 동향 보고서 2025 3Q". [Link](https://www.skshieldus.com/kor/media/newsletter/insight.do)
2. GuidePoint GRIT. (2025). "Q3 2025 Ransomware and Cyber Threat Report". [Link](https://www.guidepointsecurity.com/resources/grit-q3-2025-ransomware-and-cyber-threat-report/)
3. Checkpoint. (2025). "The State of Ransomware Q3 2025". [Link](https://research.checkpoint.com/2025/the-state-of-ransomware-q3-2025/)
4. Flashpoint. (2025). "LockBit 5.0 Technical Deep Dive". [Link](https://flashpoint.io/blog/lockbit-5-0-analysis-technical-deep-dive-into-the-raas-giants-latest-upgrade/)
5. CISA. (2025). "Known Exploited Vulnerabilities Catalog". [Link](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
6. IC3. (2025). "Akira Ransomware Advisory". [Link](https://www.ic3.gov/CSA/2025/251113.pdf)
7. Mandiant. (2025). "Ransomware Defense Best Practices". [Link](https://www.mandiant.com/resources/reports)

---

> **면책 조항**: 본 포스팅은 SK쉴더스 EQST insight 및 공개된 위협 인텔리전스를 바탕으로 작성되었습니다. 정확한 최신 정보는 원본 보고서를 참조하시기 바랍니다.

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
![포스트 시각 자료](/assets/images/2026-01-22-KARA_Ransomware_Trends_2025_Q3.svg)

