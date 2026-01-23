# Sentry + Vercel + GitHub Actions 통합 가이드

이 문서는 Sentry, Vercel, GitHub Actions를 조화롭게 통합하여 비용 최적화, 효율적인 운영, 보안을 달성하는 방법을 제공합니다.

## 📋 목차

1. [통합 아키텍처](#통합-아키텍처)
2. [비용 최적화](#비용-최적화)
3. [효율적인 운영](#효율적인-운영)
4. [보안 강화](#보안-강화)
5. [워크플로우 최적화](#워크플로우-최적화)
6. [모니터링 및 알림](#모니터링-및-알림)

## 통합 아키텍처

### 배포 플로우

```
GitHub Push
    ↓
GitHub Actions (빌드/배포)
    ├─→ GitHub Pages 배포
    ├─→ Sentry Release 생성
    └─→ Vercel 배포 (자동)
         └─→ Sentry Release 생성 (Vercel)
```

### 주요 구성 요소

1. **GitHub Actions**: CI/CD 파이프라인
   - Jekyll 빌드 및 GitHub Pages 배포
   - Sentry Release 생성
   - SNS 공유

2. **Vercel**: 호스팅 및 서버리스 함수
   - 정적 사이트 호스팅
   - Serverless Functions (API)
   - 자동 배포

3. **Sentry**: 에러 추적 및 모니터링
   - 에러 수집 및 분석
   - Release 추적
   - 성능 모니터링

## 비용 최적화

### 1. Sentry Free 티어 최적화

#### 이벤트 수 제한 (월 5,000개)
- ✅ 동적 샘플링: 50-100% 자동 조정
- ✅ 중복 에러 그룹핑: 로컬 스토리지 기반
- ✅ 이벤트 크기 제한: 8KB 자동 축소
- ✅ 프로덕션만 수집: 개발/프리뷰 제외

#### Release 추적 최적화
- ✅ 소스맵 업로드 제외 (Jekyll 정적 사이트)
- ✅ 커밋 정보만 추적
- ✅ 프로덕션 배포 시에만 Release 생성

### 2. GitHub Actions 최적화

#### 실행 최적화
- ✅ 조건부 실행: 파일 변경 감지
- ✅ 타임아웃 설정: 무한 실행 방지
- ✅ 캐싱 활용: Ruby gems, Node modules
- ✅ 병렬 실행: 독립적인 작업 병렬화

#### 워크플로우 최적화
```yaml
# 불필요한 워크플로우 실행 방지
on:
  push:
    paths:
      - '_posts/**'  # 포스트 변경 시에만
      - '_includes/**'  # 포함 파일 변경 시에만
```

### 3. Vercel 최적화

#### 빌드 최적화
- ✅ 병렬 빌드: `BUNDLE_JOBS: 4`
- ✅ 불필요한 의존성 제외: `BUNDLE_WITHOUT: development:test`
- ✅ 캐싱: Vercel 자동 캐싱 활용

#### 배포 최적화
- ✅ Preview 배포: PR별 자동 배포
- ✅ 프로덕션 배포: main 브랜치만
- ✅ 개발 환경 비활성화: 비용 절감

## 효율적인 운영

### 1. 자동화된 Release 추적

#### GitHub Actions에서 Release 생성
```yaml
# .github/workflows/sentry-release.yml
- name: Create Sentry Release
  uses: getsentry/action-release@v1
  with:
    environment: production
    version: ${{ github.sha }}
    sourcemaps: false  # Free 티어 최적화
```

#### Vercel 배포 시 Release 생성
```yaml
# .github/workflows/vercel-deploy.yml
- name: Create Sentry Release (Vercel)
  uses: getsentry/action-release@v1
  with:
    environment: production
    version: ${{ github.sha }}
```

### 2. 환경 변수 통합

#### Vercel 환경 변수
```json
{
  "build": {
    "env": {
      "BUILD_ID": "$VERCEL_GIT_COMMIT_SHA",
      "BUILD_TIME": "$VERCEL_BUILD_TIME",
      "DEPLOYMENT_URL": "$VERCEL_URL"
    }
  }
}
```

#### Sentry Release 정보 자동 주입
```javascript
// _includes/sentry.html
release: (function() {
  // Vercel 환경 변수 우선 사용
  if (window.VERCEL_GIT_COMMIT_SHA) {
    return 'tech-blog@' + window.VERCEL_GIT_COMMIT_SHA.substring(0, 7);
  }
  // GitHub Pages 빌드 ID
  if (window.BUILD_ID) {
    return 'tech-blog@' + window.BUILD_ID.substring(0, 7);
  }
  return undefined;
})()
```

### 3. 조건부 워크플로우 실행

#### 파일 변경 감지
```yaml
# .github/workflows/ci-optimization.yml
- name: Check changed files
  uses: dorny/paths-filter@v2
  with:
    filters: |
      should-build:
        - '**_posts/**'
        - '**_includes/**'
      should-deploy:
        - '**_posts/**'
        - '**_includes/**'
```

## 보안 강화

### 1. Secrets 관리

#### GitHub Secrets
- ✅ 최소 권한 원칙: 필요한 권한만 부여
- ✅ 환경별 분리: 프로덕션/개발 분리
- ✅ 정기적 로테이션: 90일마다 권장

#### Vercel 환경 변수
- ✅ 프로덕션/프리뷰/개발 환경 분리
- ✅ 민감 정보는 Secrets에 저장
- ✅ 공개 정보는 환경 변수로 관리

### 2. 권한 최소화

#### GitHub Actions 권한
```yaml
permissions:
  contents: read      # 읽기만
  pages: write        # 배포에만 필요
  id-token: write     # OIDC 인증
```

#### Sentry Auth Token
- ✅ `project:releases` 권한만 부여
- ✅ 조직 전체 권한 제한

### 3. 보안 헤더

#### Vercel 보안 헤더
```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000" }
      ]
    }
  ]
}
```

## 워크플로우 최적화

### 1. 병렬 실행

#### 독립적인 작업 병렬화
```yaml
jobs:
  build:
    # 빌드 작업
  deploy:
    needs: build  # 빌드 완료 후 실행
  sentry-release:
    needs: deploy  # 배포 완료 후 실행
```

### 2. 캐싱

#### Ruby gems 캐싱
```yaml
- name: Setup Ruby
  uses: ruby/setup-ruby@v1
  with:
    bundler-cache: true  # 자동 캐싱
```

### 3. 타임아웃 설정

#### 무한 실행 방지
```yaml
jobs:
  build:
    timeout-minutes: 10
  deploy:
    timeout-minutes: 5
```

## 모니터링 및 알림

### 1. Sentry 대시보드

#### 주요 메트릭
- 이벤트 수: 월 5,000개 제한 내 유지
- 에러율: 목표 < 1%
- Release 추적: 배포별 에러 추적

### 2. GitHub Actions 모니터링

#### 워크플로우 실행 시간
- 빌드: 목표 < 5분
- 배포: 목표 < 2분
- Release 생성: 목표 < 1분

### 3. Vercel 대시보드

#### 배포 메트릭
- 빌드 시간: 목표 < 2분
- 배포 성공률: 목표 > 99%
- 동시 빌드 수: Hobby 플랜 1개, Pro 플랜 최대 12개

## 체크리스트

### 초기 설정
- [ ] GitHub Secrets 설정 (SENTRY_AUTH_TOKEN)
- [ ] Vercel 환경 변수 설정
- [ ] Sentry 프로젝트 설정
- [ ] GitHub Actions 워크플로우 활성화

### 보안
- [ ] Secrets 최소 권한 설정
- [ ] 환경별 Secrets 분리
- [ ] 보안 헤더 설정 확인
- [ ] 민감 정보 필터링 확인

### 최적화
- [ ] 동적 샘플링 활성화
- [ ] 조건부 워크플로우 실행
- [ ] 캐싱 활용
- [ ] 타임아웃 설정

### 모니터링
- [ ] Sentry 이벤트 수 모니터링
- [ ] GitHub Actions 실행 시간 추적
- [ ] Vercel 빌드 성능 모니터링
- [ ] 알림 설정

## 참고 자료

- [Sentry GitHub Integration](https://docs.sentry.io/product/integrations/source-code-mgmt/github/)
- [Vercel GitHub Integration](https://vercel.com/docs/concepts/git)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/learn-github-actions/best-practices)
- [SENTRY_GITHUB_FREE_TIER_OPTIMIZATION.md](./SENTRY_GITHUB_FREE_TIER_OPTIMIZATION.md)
- [VERCEL_DEPLOYMENT_OPTIMIZATION.md](./VERCEL_DEPLOYMENT_OPTIMIZATION.md)

## 업데이트 이력

- **2026-01-10**: 초기 통합 가이드 작성
- **2026-01-10**: 비용 최적화, 효율성, 보안 강화 섹션 추가
- **2026-01-10**: 워크플로우 최적화 및 모니터링 가이드 추가
