---

author: Twodragon
categories:
- incident
comments: true
date: 2025-09-17 16:20:06 +0900
description: "NPM 생태계 최초 자가 복제 웜 형태 공급망 공격 Shai-Hulud 완전 분석. 180개 이상 패키지를 침해한 공격 메커니즘과 전파 경로, 감염 여부 확인 방법, SBOM 생성과 2FA 필수 설정, 오픈소스 공급망 보안 강화를 위한 실무 대응 방안을 상세히 다룹니다."
excerpt: "NPM 생태계 최초 자가 복제 웜 형태 공급망 공격 Shai-Hulud 완전 분석. 180개 이상 패키지를 침해한 공격 메커니즘과 전파 경로, 감염 여부 확인 방법, SBOM 생성과 2FA 필수 설정, 오픈소스 공급망 보안 강화를 위한 실무 대응 방안을 상세히 다룹니다."
image: /assets/images/2025-09-17-NPM_Shai-Hulud_180_Large-scale_Analysis.svg
image_alt: 'NPM Shai-Hulud Self-Replicating Worm Attack: Complete Analysis of Large-Scale'
layout: post
original_url: https://twodragon.tistory.com/694
tags:
- npm
- Supply-Chain-Attack
- Worm
- Security-Incident
keywords: [npm, Supply-Chain-Attack, Worm, Security-Incident]
title: 'NPM "Shai-Hulud" 웜: 180개 패키지 침해, 대규모 공급망 공격 분석'
toc: true
---
{%- include ai-summary-card.html
  title="NPM &quot;Shai-Hulud&quot; 자가 복제 웜 공격: 180개 이상 패키지 침해된 대규모 공급망 공격 완전 분석"
  categories_html='<span class="category-tag security">Incident</span>'
  tags_html='<span class="tag">npm</span>
      <span class="tag">Supply-Chain-Attack</span>
      <span class="tag">Worm</span>
      <span class="tag">Security-Incident</span>'
  highlights_html='<li>NPM 생태계 최초 자가 복제 웜 형태 공급망 공격 분석</li>
      <li>Shai-Hulud 공격으로 180개 이상 패키지 감염</li>
      <li>개발자 인증 정보 탈취 및 자동 전파 메커니즘 분석</li>'
  audience='SRE, 인시던트 대응 담당자, 운영 엔지니어'
-%}

### 보안 강화 체크리스트

- 관련 보안 설정 검토 및 적용
- 취약점 스캔 및 점검 수행
- 접근 제어 정책 확인
- 로깅 및 모니터링 설정 점검
- 보안 문서 업데이트

## Executive Summary

> **경영진 브리핑**: NPM 생태계 최초 자가 복제 웜 형태 공급망 공격인 Shai-Hulud 분석과 대응 방안을 다룹니다. SBOM 생성 및 2FA

![Security News Section Banner](/assets/images/section-security.svg)

## 경영진 요약

### 인시던트 개요

2025년 9월, NPM 생태계는 역사상 최초의 자가 복제 웜(Self-Replicating Worm) 형태 공급망 공격인 Shai-Hulud의 출현으로 심각한 보안 위기에 직면했습니다. 초기 180개 패키지 침해에서 시작된 이 공격은 2025년 10월 796개 이상의 패키지로 확산되었으며, 11월에는 Dead Man's Switch 기능을 탑재한 2.0 버전이 등장하여 제거 시도 시 더욱 악의적인 행동을 수행하게 되었습니다.

### 비즈니스 영향도

| 영향 범위 | 수치 | 비즈니스 리스크 |
|----------|------|----------------|
| 침해 패키지 | 796+ | 공급망 전체 오염 위험 |
| 주간 다운로드 | 수백만 회 | 광범위한 노출 |
| 감염 벡터 | 자가 복제 | 제어 불능 확산 |
| 탈취 대상 | NPM 토큰, GitHub Secrets, AWS Credentials | 전사 시스템 침투 |
| 평균 탐지 시간 | 수 주 | 지속적 데이터 유출 |

### 위험 점수 카드 (Risk Scorecard)

| 위험 요소 | 점수 | 평가 기준 |
|----------|------|----------|
| 공격 빈도 | 9/10 | 자동화된 자가 복제 메커니즘 |
| 탐지 난이도 | 8/10 | 정상 패키지로 위장, 코드 난독화 |
| 영향 범위 | 10/10 | 전체 공급망 오염 가능 |
| 복구 비용 | 9/10 | 전체 의존성 재검증 필요 |
| 법적/컴플라이언스 | 8/10 | GDPR, SOC2, ISO27001 위반 가능 |
| 종합 위험도 | CRITICAL | 즉각적 대응 필수 |

### 경영진 요약

상황: NPM 생태계 최초의 웜 형태 공급망 공격으로, 자동화된 확산 메커니즘을 통해 796개 이상의 패키지를 침해했습니다.

영향:
- 개발자 인증 정보(NPM 토큰, GitHub Secrets, AWS Credentials) 대량 탈취
- CI/CD 파이프라인 침투로 프로덕션 환경 노출
- 공급망 전체의 무결성 손상

권장 조치:
1. 즉시: 전체 NPM 의존성 감사 및 침해 패키지 제거
2. 24시간 내: 모든 개발자 계정 2FA 활성화 (하드웨어 키 권장)
3. 1주 내: SBOM(Software Bill of Materials) 생성 및 관리 체계 구축
4. 지속적: 공급망 보안 모니터링 도구 도입 (Socket.dev, Snyk 등)

예상 비용:
- 인시던트 대응: 약 200-500만원 (인력 투입 기준)
- 도구 도입: 월 100-300만원 (팀 규모별 상이)
- 미대응 시 예상 손실: 수억원 이상 (데이터 유출, 서비스 중단, 법적 비용)

## 서론

### 배경

2025년 9월, 보안 연구진은 NPM 생태계에서 전례 없는 형태의 공격을 발견했습니다. Shai-Hulud(프랭크 허버트의 소설 "듄"에 등장하는 거대 모래벌레에서 이름을 따옴)로 명명된 이 공격은 기존 공급망 공격과 근본적으로 다른 특징을 가지고 있었습니다:

1. 자가 복제(Self-Replication): 감염된 패키지가 스스로 다른 패키지를 감염시킴
2. 자동화된 전파: 인간의 개입 없이 자동으로 확산
3. 다층 지속성: 제거 시도를 탐지하고 더욱 악의적인 행동 수행

### 공격의 역사적 중요성

Shai-Hulud는 단순한 보안 사고가 아니라, 소프트웨어 공급망 공격의 패러다임 전환을 의미합니다:

| 기존 공급망 공격 | Shai-Hulud |
|----------------|------------|
| 수동 침투 (Maintainer 계정 탈취) | 자동 복제 |
| 단일 패키지 침해 | 796+ 패키지 동시 침해 |
| 정적 악성 코드 | 동적 진화 (2.0 버전) |
| 선형 확산 | 지수적 확산 |

이 글에서는 Shai-Hulud 공격의 기술적 메커니즘, MITRE ATT&CK 매핑, 탐지 방법, 대응 전략을 실무 중심으로 상세히 다룹니다.

![NPM Supply Chain Worm Attack](/assets/images/mermaid/npm_supply_chain_worm.svg)

## 1. 공격 기술 분석

### 1.1 Shai-Hulud 웜 아키텍처

Shai-Hulud 웜은 다음과 같은 모듈형 아키텍처로 구성되어 있습니다:

주요 단계 분석:

| 단계 | 기술 | 목적 | 탐지 난이도 |
|------|------|------|------------|
| 1. 인증 정보 수집 | 환경 변수 읽기, 파일 스캔 | 권한 확보 | 중간 |
| 2. 대상 선정 | 의존성 트리 분석 | 확산 경로 파악 | 낮음 |
| 3. 악성 코드 주입 | 소스 코드 변조 | 정상 패키지로 위장 | 높음 |
| 4. 자동 배포 | NPM API 호출 | 확산 자동화 | 낮음 |
| 5. 지속성 확보 | 훅, 환경 변수 | 재감염 방지 | 중간 |

### 1.2 Shai-Hulud 2.0: Dead Man's Switch

2025년 11월 등장한 2.0 버전은 제거 방어 메커니즘을 추가했습니다:

난독화 기법 레이어:
1. 변수명 암호화: 의미 있는 이름을 16진수 문자열로 변환
2. 제어 흐름 평탄화: if-else를 switch-case로 변환하여 정적 분석 방해
3. 문자열 암호화: 중요 문자열을 Base64 또는 XOR로 암호화
4. Dead Code 삽입: 실행되지 않는 코드 삽입으로 분석 도구 혼란
5. 동적 eval: 런타임에 코드 생성 및 실행

## 빠른 참조

### 공격 요약

| 항목 | 내용 |
|------|------|
| 공격 유형 | 자가 복제 웜 형태 공급망 공격 |
| 감염 패키지 수 | 180개 이상 |
| 공격 특징 | NPM 생태계 최초 자가 복제 웜 |
| 주요 목표 | 개발자 인증 정보 탈취 및 자동 전파 |

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
| SBOM 생성 | 소프트웨어 구성 요소 목록 관리 | 높음 |
| 의존성 스캔 | 정기적인 취약점 스캔 | 높음 |
| 2FA 활성화 | 2단계 인증 필수 | 매우 높음 |
| 패키지 검증 | 신뢰할 수 있는 소스 확인 | 높음 |
| 모니터링 | 이상 패키지 활동 탐지 | 중간 |

### 보안 체크리스트

| 항목 | 상태 | 설명 |
|------|------|------|
| 2FA 활성화 | ✅ 필수 | NPM 계정 2단계 인증 |
| 의존성 검토 | ✅ 필수 | 정기적인 의존성 검토 |
| 패키지 검증 | ✅ 필수 | 신뢰할 수 있는 패키지만 사용 |
| SBOM 생성 | ✅ 권장 | 소프트웨어 구성 요소 추적 |
| 자동 스캔 | ✅ 권장 | CI/CD 파이프라인 통합 |

<img src="{{ '/assets/images/2025-09-17-NPM_Shai-Hulud_180_Large-scale_Analysis.svg' | relative_url }}" alt="NPM Shai-Hulud Self-Replicating Worm Attack: Complete Analysis of Large-Scale Supply Chain Attack with 180+ Compromised Packages" loading="lazy" class="post-image">

## 2. 2025년 최신 동향 및 후속 사건

### 2.1 Shai-Hulud 공격 확산 타임라인

초기 180개 패키지 침해 이후 공격은 급속히 확산되었습니다:

| 시기 | 침해 패키지 수 | 주요 사건 |
|------|---------------|----------|
| 2025년 9월 초 | 180+ | 최초 Shai-Hulud 웜 발견 |
| 2025년 9월 중순 | 500+ | 급속 확산, GitLab 팀 분석 발표 |
| 2025년 10월 | 796+ | 최대 확산 규모 기록 |
| 2025년 11월 | - | Shai-Hulud 2.0 변종 등장 |

### 2.2 Shai-Hulud 2.0: Dead Man's Switch

2025년 11월, 더욱 진화된 Shai-Hulud 2.0 변종이 발견되었습니다. 가장 위험한 새 기능은 Dead Man's Switch입니다.

Dead Man's Switch는 패키지가 NPM 레지스트리에서 제거되거나 특정 조건이 감지될 때 자동으로 더 악의적인 페이로드를 실행하는 메커니즘입니다:

- 제거 감지: 패키지 설치 후 주기적으로 NPM 레지스트리에 자신의 존재를 확인
- 트리거 조건: 패키지가 unpublish되거나 인터넷 접근이 차단되면 로컬에 캐시된 페이로드 실행
- 페이로드: 환경 변수 전체 덤프, SSH 키 탈취, `.npmrc` 파일 외부 전송
- 지속성: `~/.bashrc`, `~/.zshrc`에 훅을 삽입하여 셸 재시작 시에도 유지

### 2.3 연관 사건: 9월 대규모 npm 침해

Shai-Hulud와 시기적으로 연관된 2025년 9월 대규모 npm 침해 사건의 상세 내용:

| 항목 | 세부 내용 |
|------|----------|
| 피해 규모 | 18개 핵심 패키지 (debug, chalk 등) |
| 주간 다운로드 | 2.6B+ (26억 회 이상) |
| 공격 방식 | Maintainer 계정 피싱 |
| 피싱 도메인 | `npmjs.help` (공식 사이트 위장) |
| 2FA 우회 | 실시간 MITM으로 2FA 토큰 탈취 |
| 발견자 | GitLab Vulnerability Research Team |

### 2.4 Nx / s1ngularity 공격

Shai-Hulud와 별개로 발생한 또 다른 심각한 공급망 공격:

참고: s1ngularity 공격 상세 분석은 [Nx 공식 포스트모템](https://nx.dev/blog/s1ngularity-postmortem) 및 [Nx GitHub 저장소](https://github.com/nrwl/nx)를 참조하세요.

s1ngularity 공격은 Nx 모노레포 툴체인을 대상으로 한 공급망 침해로, 악성 패키지가 Nx 생태계의 의존성을 통해 배포되었습니다:

```yaml
# s1ngularity 공격 개요
attack:
  target: "Nx monorepo toolchain"
  vector: "compromised npm package maintainer account"
  payload: "credential harvester + persistence script"
  affected_packages:
    - "@nrwl/workspace"
    - "@nx/workspace"
  mitigation: "Nx 팀이 즉각 패키지 제거 및 계정 보안 강화"
```

### 2.5 침해 대응 절차

감염이 확인된 경우 다음 절차를 즉시 수행합니다.

#### 2.5.1 Docker 런타임 보안 설정

컨테이너 환경에서 최소 권한 원칙을 적용하여 공격 영향 범위를 제한합니다:

```dockerfile
# Dockerfile - 최소 권한 및 보안 강화
FROM node:20-alpine AS base

# 비루트 사용자 생성
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

WORKDIR /app

# 의존성 설치 (루트로 수행 후 권한 변경)
COPY package*.json ./
RUN npm ci --only=production && \
    npm cache clean --force

# 애플리케이션 파일 복사
COPY --chown=appuser:appgroup . .

# 비루트 사용자로 전환
USER appuser

# 읽기 전용 파일시스템 권장 (docker run --read-only)
EXPOSE 3000
CMD ["node", "index.js"]
```

1. 감염된 워크스테이션 격리:

```bash
# 감염된 개발자 워크스테이션 네트워크 차단
sudo iptables -A OUTPUT -j DROP
# 또는 VPN 연결 강제 종료
sudo systemctl stop openvpn
```

2. CI/CD 파이프라인 중단:

```bash
# GitHub Actions 비활성화
gh api -X PATCH /repos/OWNER/REPO/actions/permissions \
  -f enabled=false

# Jenkins job 비활성화
java -jar jenkins-cli.jar -s http://jenkins:8080/ \
  disable-job "affected-pipeline"
```

3. Private NPM Registry 읽기 전용으로 전환:

```yaml
# verdaccio.yaml
packages:
  '**':
    access: $authenticated
    publish: $admin  # 일반 사용자 publish 차단
    proxy: npmjs
```

4. NPM 토큰 즉시 재생성:

```bash
# 기존 토큰 전체 목록 확인 및 폐기
npm token list
npm token revoke <token-id>

# 새 토큰 생성 (읽기 전용 CI 토큰)
npm token create --read-only --cidr=10.0.0.0/8
```

## 3. 참고 자료 (References)

### 3.1 공식 보안 권고사항

1. CISA (Cybersecurity & Infrastructure Security Agency)
   - NPM Supply Chain Attack Advisory (2025-11)
   - URL: https://www.cisa.gov/news-events/alerts/2025/11/15/npm-supply-chain-attack

2. NIST (National Institute of Standards and Technology)
   - NIST SP 800-161 Rev. 1: Cybersecurity Supply Chain Risk Management
   - URL: https://csrc.nist.gov/publications/detail/sp/800-161/rev-1/final

3. NPM Security Team
   - NPM Security Best Practices
   - URL: https://docs.npmjs.com/security

4. MITRE ATT&CK Framework
   - T1195: Supply Chain Compromise
   - URL: https://attack.mitre.org/techniques/T1195/

### 3.2 기술 분석 리포트

5. GitLab Vulnerability Research Team
   - Shai-Hulud Technical Analysis (2025-09)
   - URL: https://about.gitlab.com/blog/2025/09/17/npm-shai-hulud-analysis/

6. Socket.dev Research
   - NPM 자가 복제 웜의 부상 (The Rise of Self-Replicating Worms in NPM)
   - URL: https://socket.dev/blog/shai-hulud-worm-analysis

7. Snyk Research
   - NPM 생태계 보안 리포트 2025 (NPM Ecosystem Security Report 2025)
   - URL: https://snyk.io/reports/npm-ecosystem-security-2025/

8. Aqua Security
   - 공급망 공격의 Dead Man's Switch (Dead Man's Switch in Supply Chain Attacks)
   - URL: https://blog.aquasec.com/dead-mans-switch-supply-chain

### 3.3 오픈소스 도구

9. Socket.dev CLI
   - GitHub: https://socket.dev/
   - 실시간 공급망 위협 탐지 도구

10. Snyk
    - GitHub: https://github.com/snyk/snyk
    - 종합 취약점 스캔 도구

11. OSV Scanner (Google)
    - GitHub: https://github.com/google/osv-scanner
    - OSV 데이터베이스 기반 취약점 스캔 도구

12. Syft (Anchore)
    - GitHub: https://github.com/anchore/syft
    - SBOM 생성 도구

13. Grype (Anchore)
    - GitHub: https://github.com/anchore/grype
    - 취약점 스캔 도구

14. lockfile-lint
    - GitHub: https://github.com/lirantal/lockfile-lint
    - lockfile 무결성 검증 도구

### 3.4 법규 및 컴플라이언스

15. 개인정보보호법 (한국)
    - 법제처: https://www.law.go.kr/법령/개인정보보호법

16. 정보통신망법 (한국)
    - 법제처: https://www.law.go.kr/법령/정보통신망이용촉진및정보보호등에관한법률

17. 전자금융거래법 (한국)
    - 법제처: https://www.law.go.kr/법령/전자금융거래법

18. GDPR (EU)
    - Official Text: https://gdpr.eu/

### 3.5 사고 사례 연구

19. Nx / s1ngularity 공격 포스트모템
    - URL: https://nx.dev/blog/s1ngularity-postmortem

20. SolarWinds 공급망 공격 (참고 사례)
    - CISA 분석: https://www.cisa.gov/solarwinds

21. Log4j 취약점 (참고 사례)
    - NIST: https://nvd.nist.gov/vuln/detail/CVE-2021-44228

### 3.6 학술 논문 및 연구

22. "소프트웨어 공급망 공격: 체계적 문헌 검토" (Software Supply Chain Attacks: A Systematic Literature Review)
    - 저자: Torres-Arias 외
    - DOI: 10.1145/3412841.3442028

23. "배신자의 칼 컬렉션: 오픈소스 소프트웨어 공급망 공격 리뷰" (Backstabber's Knife Collection: A Review of Open Source Software Supply Chain Attacks)
    - 저자: Ohm 외
    - DOI: 10.1007/978-3-030-52683-2_1

24. "의존성 혼동: Apple, Microsoft 등 수십 개 기업을 해킹한 방법" (Dependency Confusion: How I Hacked Into Apple, Microsoft and Dozens of Other Companies)
    - 저자: Alex Birsan
    - URL: https://medium.com/@alex.birsan/dependency-confusion-4a5d60fec610

### 3.7 추가 학습 자료

25. OWASP CI/CD 보안 위험 Top 10 (OWASP Top 10 CI/CD Security Risks)
    - URL: https://owasp.org/www-project-top-10-ci-cd-security-risks/

26. SLSA 프레임워크 - 소프트웨어 아티팩트 공급망 레벨 (Supply-chain Levels for Software Artifacts)
    - URL: https://slsa.dev/

27. Sigstore (코드 서명)
    - URL: https://www.sigstore.dev/

28. CycloneDX (SBOM 표준)
    - URL: https://cyclonedx.org/

---

관련 태그: #NPM #Supply-Chain-Attack #Worm #Security-Incident #SBOM #2FA #Shai-Hulud #DevSecOps #MITRE-ATT&CK #Incident-Response

## 결론

NPM "Shai-Hulud" 자가 복제 웜 공격은 초기 180개 패키지에서 796개 이상으로 확산되었으며, 2025년 11월에는 Dead Man's Switch 기능이 추가된 2.0 버전이 등장했습니다.

동시에 발생한 9월 대규모 npm 침해(26억+ 다운로드 패키지 감염)와 Nx/s1ngularity 공격까지 고려하면, 2025년은 npm 생태계 역사상 가장 심각한 공급망 보안 위기의 해로 기록될 것입니다.

CISA 경고에 따라 모든 조직은 즉시 의존성 감사를 실시하고, GitLab Vulnerability Research Team이 권장하는 보안 도구를 적극 활용해야 합니다. 올바른 설정과 지속적인 모니터링을 통해 안전하고 효율적인 환경을 구축할 수 있습니다.

---

마지막 업데이트: 2025-11-15 (Shai-Hulud 2.0, CISA 경고, Nx 공격 등 추가)

