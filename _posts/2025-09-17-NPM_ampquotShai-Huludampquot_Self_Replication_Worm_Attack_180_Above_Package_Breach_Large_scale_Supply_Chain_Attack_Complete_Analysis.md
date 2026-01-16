---
layout: post
title: "NPM \"Shai-Hulud\" 자가 복제 웜 공격: 180개 이상 패키지 침해된 대규모 공급망 공격 완전 분석"
date: 2025-09-17 16:20:06 +0900
categories: [incident]
tags: [npm, Supply-Chain-Attack, Worm, Security-Incident]
excerpt: "NPM Shai-Hulud 자가 복제 웜 공격 완전 분석: NPM 생태계 최초 자가 복제 웜 형태 공급망 공격, 180개 이상 패키지 감염, 개발자 인증 정보 탈취 및 자동 전파 메커니즘, 공격 체인 분석(패키지 하이재킹->인증 정보 탈취->자동 전파), 대응 방안(SBOM 생성, 의존성 스캔, 2FA 활성화)까지 실무 중심 정리."
comments: true
original_url: https://twodragon.tistory.com/694
image: /assets/images/2025-09-17-NPM_ampquotShai-Huludampquot_180_Large-scale_Analysis.svg
image_alt: "NPM Shai-Hulud Self-Replicating Worm Attack: Complete Analysis of Large-Scale Supply Chain Attack with 180+ Compromised Packages"
toc: true
---

<div class="ai-summary-card">
<div class="ai-summary-header">
  <span class="ai-badge">AI 요약</span>
</div>
<div class="ai-summary-content">
  <div class="summary-row">
    <span class="summary-label">제목</span>
    <span class="summary-value">NPM "Shai-Hulud" 자가 복제 웜 공격: 180개 이상 패키지 침해된 대규모 공급망 공격 완전 분석</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">카테고리</span>
    <span class="summary-value"><span class="category-tag security">Incident</span></span>
  </div>
  <div class="summary-row">
    <span class="summary-label">태그</span>
    <span class="summary-value tags">
      <span class="tag">npm</span>
      <span class="tag">Supply-Chain-Attack</span>
      <span class="tag">Worm</span>
      <span class="tag">Security-Incident</span>
    </span>
  </div>
  <div class="summary-row highlights">
    <span class="summary-label">핵심 내용</span>
    <ul class="summary-list">
      <li>NPM 생태계 최초 자가 복제 웜 형태 공급망 공격 분석</li>
      <li>Shai-Hulud 공격으로 180개 이상 패키지 감염</li>
      <li>개발자 인증 정보 탈취 및 자동 전파 메커니즘 분석</li>
    </ul>
  </div>
  <div class="summary-row">
    <span class="summary-label">기술/도구</span>
    <span class="summary-value">npm, Supply Chain Security, Worm Analysis</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">대상 독자</span>
    <span class="summary-value">SRE, 인시던트 대응 담당자, 운영 엔지니어</span>
  </div>
</div>
<div class="ai-summary-footer">
  이 포스팅은 AI가 쉽게 이해하고 활용할 수 있도록 구조화된 요약을 포함합니다.
</div>
</div>

## 서론

NPM 생태계 역사상 최초의 자가 복제 웜 형태 공급망 공격 분석입니다. Shai-Hulud 공격으로 180개 이상의 패키지가 감염되었으며, 개발자 인증 정보 탈취 및 자동 전파 메커니즘을 분석합니다.

이 글에서는 NPM "Shai-Hulud" 자가 복제 웜 공격: 180개 이상 패키지 침해된 대규모 공급망 공격 완전 분석에 대해 실무 중심으로 상세히 다룹니다.

### Shai-Hulud 공격 체인

Shai-Hulud 웜 공격의 자가 복제 메커니즘:

```mermaid
graph TB
    subgraph Attack["Attack Chain"]
        Step1["1. Package Hijacking - 기존 패키지 탈취 - 또는 유사 이름 생성"]
        Step2["2. Credential Theft - 개발자 인증 정보 탈취 - npm token, password"]
        Step3["3. Auto Propagation - 탈취한 인증 정보로 - 새 패키지 생성/업데이트"]
        Step4["4. Persistence - 백도어 설치 - 추가 공격 벡터 구축"]
    end
    
    Step1 -> Step2
    Step2 -> Step3
    Step3 -> Step4
    Step4 -> Step1
    
    style Step1 fill:#ffebee
    style Step2 fill:#ff5252
    style Step3 fill:#ff9800
    style Step4 fill:#ffebee
```

### 공급망 공격 확산 과정

감염된 패키지가 어떻게 확산되는지:

```mermaid
graph LR
    subgraph Initial["Initial Infection"]
        Pkg1["Compromised - Package 1"]
        Dev1["Developer 1 - Installs Package"]
    end
    
    subgraph Spread["Worm Spread"]
        Token1["Token Stolen - from Developer 1"]
        Pkg2["New Package - Created"]
        Dev2["Developer 2 - Installs Package"]
        Token2["Token Stolen - from Developer 2"]
    end
    
    subgraph Scale["Large Scale"]
        PkgN["180+ Packages - Compromised"]
        Impact["Massive Impact - Supply Chain"]
    end
    
    Pkg1 -> Dev1
    Dev1 -> Token1
    Token1 -> Pkg2
    Pkg2 -> Dev2
    Dev2 -> Token2
    Token2 -> PkgN
    PkgN -> Impact
    
    style Pkg1 fill:#ffebee
    style Token1 fill:#ff5252
    style Token2 fill:#ff5252
    style PkgN fill:#ff9800
    style Impact fill:#d32f2f
```

## 📊 빠른 참조

### 공격 요약

| 항목 | 내용 |
|------|------|
| **공격 유형** | 자가 복제 웜 형태 공급망 공격 |
| **감염 패키지 수** | 180개 이상 |
| **공격 특징** | NPM 생태계 최초 자가 복제 웜 |
| **주요 목표** | 개발자 인증 정보 탈취 및 자동 전파 |

### 공격 체인 분석

| 단계 | 설명 | 목적 |
|------|------|------|
| 1. 패키지 하이재킹 | 기존 패키지 탈취 또는 유사 이름 패키지 생성 | 초기 침투 |
| 2. 인증 정보 탈취 | 개발자 인증 정보 (토큰, 비밀번호) 수집 | 권한 확보 |
| 3. 자동 전파 | 탈취한 인증 정보로 새 패키지 생성 및 업데이트 | 확산 |
| 4. 지속성 확보 | 백도어 설치 및 추가 공격 벡터 구축 | 장기 침투 |

### 대응 방안

| 대응 항목 | 설명 | 우선순위 |
|----------|------|----------|
| **SBOM 생성** | 소프트웨어 구성 요소 목록 관리 | 높음 |
| **의존성 스캔** | 정기적인 취약점 스캔 | 높음 |
| **2FA 활성화** | 2단계 인증 필수 | 매우 높음 |
| **패키지 검증** | 신뢰할 수 있는 소스 확인 | 높음 |
| **모니터링** | 이상 패키지 활동 탐지 | 중간 |

### 보안 체크리스트

| 항목 | 상태 | 설명 |
|------|------|------|
| **2FA 활성화** | ✅ 필수 | NPM 계정 2단계 인증 |
| **의존성 검토** | ✅ 필수 | 정기적인 의존성 검토 |
| **패키지 검증** | ✅ 필수 | 신뢰할 수 있는 패키지만 사용 |
| **SBOM 생성** | ✅ 권장 | 소프트웨어 구성 요소 추적 |
| **자동 스캔** | ✅ 권장 | CI/CD 파이프라인 통합 |

<img src="{{ '/assets/images/2025-09-17-NPM_ampquotShai-Huludampquot_180_Large-scale_Analysis_image.webp' | relative_url }}" alt="NPM Shai-Hulud Self-Replicating Worm Attack: Complete Analysis of Large-Scale Supply Chain Attack with 180+ Compromised Packages" loading="lazy" class="post-image">

## 1. 개요

### 1.1 배경 및 필요성

NPM 생태계 역사상 최초의 자가 복제 웜 형태 공급망 공격 분석입니다. Shai-Hulud 공격으로 180개 이상의 패키지가 감염되었으며, 개발자 인증 정보 탈취 및 자동 전파 메커니즘을 분석합니다....

### 1.2 주요 개념

이 가이드에서 다루는 주요 개념:

- **보안**: 안전한 구성 및 접근 제어
- **효율성**: 최적화된 설정 및 운영
- **모범 사례**: 검증된 방법론 적용

## 2. 핵심 내용

### 2.1 기본 설정

기본 설정을 시작하기 전에 다음 사항을 확인해야 합니다:

1. **요구사항 분석**: 필요한 기능 및 성능 요구사항 파악
2. **환경 준비**: 필요한 도구 및 리소스 준비
3. **보안 정책**: 보안 정책 및 규정 준수 사항 확인

### 2.2 단계별 구현

#### 단계 1: 초기 설정

초기 설정 단계에서는 기본 구성을 수행합니다.

```bash
# 예시 명령어
# 실제 설정에 맞게 수정 필요
```

#### 단계 2: 보안 구성

보안 설정을 구성합니다:

- 접근 제어 설정
- 암호화 구성
- 모니터링 활성화

## 3. 모범 사례

### 3.1 보안 모범 사례

- **최소 권한 원칙**: 필요한 최소한의 권한만 부여
- **정기적인 보안 점검**: 취약점 스캔 및 보안 감사
- **자동화된 보안 스캔**: CI/CD 파이프라인에 보안 스캔 통합

### 3.2 운영 모범 사례

- **자동화된 배포 파이프라인**: 일관성 있는 배포
- **정기적인 백업**: 데이터 보호
- **모니터링**: 지속적인 상태 모니터링

## 4. 문제 해결

### 4.1 일반적인 문제

자주 발생하는 문제와 해결 방법:

**문제 1**: 설정 오류
- **원인**: 잘못된 구성
- **해결**: 설정 파일 재확인 및 수정

**문제 2**: 성능 저하
- **원인**: 리소스 부족
- **해결**: 리소스 확장 또는 최적화

## 5. 2025년 최신 동향 및 후속 사건

### 5.1 Shai-Hulud 공격 확산 타임라인

초기 180개 패키지 침해 이후 공격은 급속히 확산되었습니다:

| 시기 | 침해 패키지 수 | 주요 사건 |
|------|---------------|----------|
| 2025년 9월 초 | 180+ | 최초 Shai-Hulud 웜 발견 |
| 2025년 9월 중순 | 500+ | 급속 확산, GitLab 팀 분석 발표 |
| 2025년 10월 | **796+** | 최대 확산 규모 기록 |
| 2025년 11월 | - | **Shai-Hulud 2.0** 변종 등장 |

### 5.2 Shai-Hulud 2.0: Dead Man's Switch

2025년 11월, 더욱 진화된 **Shai-Hulud 2.0** 변종이 발견되었습니다. 가장 위험한 새 기능은 **Dead Man's Switch**입니다.

<!-- 긴 코드 블록 제거됨 (가독성 향상)
```
┌─────────────────────────────────────────────────────────────┐
│           Shai-Hulud 2.0 - Dead Man's Switch                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   [정상 상태]                                                │
│       웜 코드가 패키지 내 존재                               │
│              │                                               │
│              ▼                                               │
│   [트리거 조건 감지]                                         │
│       - 악성 코드 삭제 시도                                  │
│       - 패키지 강제 업데이트                                 │
│       - npm audit fix 실행                                   │
│              │                                               │
│              ▼                                               │
│   [Dead Man's Switch 활성화]                                 │
│       1. 로컬 npm 캐시 전체 삭제                             │
│       2. package-lock.json 변조                              │
│       3. 추가 악성 의존성 자동 주입                          │
│       4. CI/CD 환경변수 유출 시도                            │
│       5. GitHub/GitLab secrets 탈취                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘

```
-->

#### Dead Man's Switch 대응 방법

> **참고**: Shai-Hulud 2.0 탐지 및 대응 도구는 [Shai-Hulud-2.0-Detector](https://github.com/gensecaihq/Shai-Hulud-2.0-Detector) 및 [OreNPMGuard](https://github.com/rapticore/OreNPMGuard)를 참조하세요.
> 
> ```bash
> # 안전한 제거 절차 (Dead Man's Switch 우회)...
> ```

<!-- 전체 코드는 위 링크 참조
```bash
# 안전한 제거 절차 (Dead Man's Switch 우회)

# 1. 네트워크 격리 상태에서 작업
# (컨테이너 또는 VM 사용 권장)

# 2. 환경변수 백업 후 제거
env > /tmp/env_backup.txt
unset $(env | grep -E '^(NPM_TOKEN|GITHUB_TOKEN|AWS_)' | cut -d= -f1)

# 3. node_modules 삭제 전 프로세스 종료
pkill -f node
rm -rf node_modules

# 4. 캐시 정리 (오프라인 상태에서)
npm cache clean --force

# 5. 새로운 환경에서 클린 설치
npm ci --ignore-scripts

```
-->

### 5.3 연관 사건: 9월 대규모 npm 침해

Shai-Hulud와 시기적으로 연관된 2025년 9월 대규모 npm 침해 사건의 상세 내용:

| 항목 | 세부 내용 |
|------|----------|
| **피해 규모** | 18개 핵심 패키지 (debug, chalk 등) |
| **주간 다운로드** | **2.6B+** (26억 회 이상) |
| **공격 방식** | Maintainer 계정 피싱 |
| **피싱 도메인** | `npmjs.help` (공식 사이트 위장) |
| **2FA 우회** | 실시간 MITM으로 2FA 토큰 탈취 |
| **발견자** | **GitLab Vulnerability Research Team** |

### 5.4 Nx / s1ngularity 공격

Shai-Hulud와 별개로 발생한 또 다른 심각한 공급망 공격:

> **참고**: s1ngularity 공격 상세 분석은 [Nx 공식 포스트모템](https://nx.dev/blog/s1ngularity-postmortem) 및 [Nx GitHub 저장소](https://github.com/nrwl/nx)를 참조하세요.
> 
> ```yaml
> # s1ngularity 공격 개요...
> ```

<!-- 전체 코드는 위 링크 참조
```yaml
# s1ngularity 공격 개요
attack_name: "s1ngularity"
target: "Nx (Nrwl) 모노레포 빌드 도구"
impact:
  - Nx 패키지 악성 버전 배포
  - GitHub repository secrets 유출
  - CI/CD 파이프라인 침투
affected_packages:
  - "@nrwl/workspace"
  - "@nx/workspace"
  - "@nx/devkit"

```
-->

#### Nx 패키지 영향 확인

> **참고**: Nx 보안 관련 자세한 내용은 [Nx 공식 포스트모템](https://nx.dev/blog/s1ngularity-postmortem) 및 [npm 보안 권고사항](https://github.com/npm/security-advisories)을 참조하세요.

```bash
# Nx 의존성 확인
npm ls @nrwl/workspace @nx/workspace @nx/devkit 2>/dev/null

# package-lock.json에서 Nx 관련 패키지 해시 확인
grep -A5 '"@nrwl\|"@nx/' package-lock.json | grep integrity
```

### 5.5 CISA 공식 경고

**CISA (미국 사이버보안 및 인프라 보안국)**에서 npm 공급망 공격에 대한 공식 경고를 발령했습니다:

> **CISA Alert**: npm 생태계 대규모 공급망 공격 경고
>
> 모든 조직은 즉시 다음 조치를 취할 것을 권고합니다:
> 1. npm 의존성 전수 감사
> 2. 영향받은 패키지 즉시 업데이트
> 3. 모든 자격증명 교체
> 4. 하드웨어 보안 키 기반 2FA 도입

### 5.6 종합 대응 체크리스트 (2025년 11월 기준)

| 우선순위 | 조치 항목 | 대상 |
|---------|----------|------|
| Critical | Shai-Hulud 감염 여부 확인 | 모든 npm 프로젝트 |
| Critical | 796+ 침해 패키지 목록 대조 | DevOps |
| High | Dead Man's Switch 안전 제거 절차 적용 | 감염 확인 시스템 |
| High | npm 계정 2FA를 하드웨어 키로 전환 | Maintainers |
| Medium | Nx 패키지 버전 감사 | Nx 사용 프로젝트 |
| Medium | SBOM 생성 및 관리 체계 구축 | 전체 조직 |

### 5.7 GitLab Vulnerability Research Team 권장 도구

> **참고**: 공급망 보안 도구 관련 자세한 내용은 [Socket.dev](https://github.com/socketsecurity/socket), [Snyk](https://github.com/snyk/snyk), [OSV Scanner](https://github.com/google/osv-scanner)를 참조하세요.
> 
> ```bash
> # 공급망 보안 강화 도구 모음...
> ```

<!-- 전체 코드는 위 링크 참조
```bash
# 공급망 보안 강화 도구 모음

# 1. Socket.dev - 실시간 공급망 위협 탐지
npm install -g @socketsecurity/cli
socket scan .

# 2. npm audit signatures - 패키지 서명 검증 (npm 8.18+)
npm audit signatures

# 3. lockfile-lint - lockfile 무결성 검증
npx lockfile-lint --path package-lock.json --type npm \
  --allowed-hosts npm --validate-https

# 4. Snyk - 종합 취약점 스캔
npx snyk test

# 5. osv-scanner - Google OSV 데이터베이스 기반 스캔
# (Go 설치 필요)
osv-scanner --lockfile package-lock.json

```
-->

## 결론

NPM "Shai-Hulud" 자가 복제 웜 공격은 초기 180개 패키지에서 **796개 이상**으로 확산되었으며, 2025년 11월에는 **Dead Man's Switch** 기능이 추가된 2.0 버전이 등장했습니다.

동시에 발생한 9월 대규모 npm 침해(26억+ 다운로드 패키지 감염)와 Nx/s1ngularity 공격까지 고려하면, 2025년은 npm 생태계 역사상 가장 심각한 공급망 보안 위기의 해로 기록될 것입니다.

CISA 경고에 따라 모든 조직은 즉시 의존성 감사를 실시하고, GitLab Vulnerability Research Team이 권장하는 보안 도구를 적극 활용해야 합니다. 올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 환경을 구축할 수 있습니다.

---

**마지막 업데이트**: 2025-11-15 (Shai-Hulud 2.0, CISA 경고, Nx 공격 등 추가)