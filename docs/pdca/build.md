# PDCA: 빌드 기능

> Jekyll 사이트 빌드 및 아티팩트 생성

## 현황

| 항목 | 값 |
|------|-----|
| **워크플로우** | `.github/workflows/jekyll.yml` |
| **트리거** | push (main), PR, workflow_dispatch |
| **실행 환경** | ubuntu-latest |
| **타임아웃** | 10분 (빌드), 15분 (배포) |
| **상태** | Active |

---

## Plan (계획)

### 목표
- Jekyll 사이트를 안정적으로 빌드
- 빌드 시간 최소화
- 비용 효율적 CI 운영

### KPI
| 지표 | 목표 | 현재 |
|------|------|------|
| 빌드 성공률 | 99%+ | - |
| 평균 빌드 시간 | < 3분 | - |
| 월간 빌드 실행 | 최소화 | - |

### 비용 계획
- GitHub Actions Free Tier: 2,000분/월
- 조건부 실행으로 불필요한 빌드 방지

---

## Do (실행)

### 구현된 기능

#### 1. 조건부 빌드 (paths-filter)
```yaml
# 관련 파일 변경 시에만 빌드 실행
uses: dorny/paths-filter@v2
filters: |
  should-build:
    - '**_posts/**'
    - '**_includes/**'
    - '**_layouts/**'
    - '**_config.yml'
```

#### 2. 캐싱 전략
```yaml
# Ruby 번들러 캐싱
uses: ruby/setup-ruby@v1
with:
  bundler-cache: true

# Node.js 캐싱
uses: actions/setup-node@v4
with:
  cache: 'npm'

# Python 캐싱
uses: actions/setup-python@v5
with:
  cache: 'pip'
```

#### 3. 빌드 스크립트 (build.sh)
```bash
# Vercel과 동일한 빌드 프로세스
./build.sh
```

### 의존성
- Ruby 3.3
- Node.js 20
- Python 3.11
- Jekyll, Bundler

---

## Check (점검)

### 모니터링 항목

#### 빌드 성공/실패
- [ ] GitHub Actions 대시보드 확인
- [ ] 실패 알림 설정

#### 빌드 시간 추이
```bash
# GitHub CLI로 최근 워크플로우 실행 확인
gh run list --workflow=jekyll.yml --limit=10
```

#### 비용 모니터링
- [ ] GitHub Actions 사용량 확인: Settings → Billing

### 점검 체크리스트
- [ ] 빌드 성공률 99% 이상 유지
- [ ] 평균 빌드 시간 3분 이하
- [ ] 불필요한 빌드 실행 없음
- [ ] 캐시 히트율 높음

---

## Act (개선)

### 식별된 개선점
1. **캐시 최적화**: 번들러 캐시 히트율 모니터링
2. **병렬화**: 독립적 작업 병렬 실행 검토
3. **증분 빌드**: Jekyll 증분 빌드 옵션 검토

### 개선 이력
| 날짜 | 개선 내용 | 결과 |
|------|----------|------|
| - | - | - |

### 다음 사이클 계획
- [ ] 빌드 시간 분석 및 병목 구간 식별
- [ ] 캐시 히트율 개선
- [ ] 불필요한 의존성 정리

---

## 관련 문서

- [배포 PDCA](deploy.md)
- [Pipeline 전체 흐름](../pipeline/README.md)
- [Jekyll 워크플로우](.github/workflows/jekyll.yml)
