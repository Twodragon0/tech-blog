# Sentry + GitHub 통합 Free 티어 최적화 가이드

이 문서는 Sentry와 GitHub를 결합하여 사용할 때 Free 티어 제한 내에서 보안, 효율성, 비용을 최적화하는 방법을 제공합니다.

## 📋 목차

1. [Sentry Free 티어 제한](#sentry-free-티어-제한)
2. [GitHub 통합 기능](#github-통합-기능)
3. [보안 최적화](#보안-최적화)
4. [효율성 최적화](#효율성-최적화)
5. [비용 최적화](#비용-최적화)
6. [모니터링 및 알림](#모니터링-및-알림)
7. [실전 체크리스트](#실전-체크리스트)

## Sentry Free 티어 제한

### 핵심 제한사항

- **월 5,000 이벤트** 제한
- **30일 데이터 보존**
- **1개 프로젝트** (조직당)
- **기본 알림** (이메일, Slack)
- **GitHub 통합** 지원 (Issues, Releases, Commits)

### 제한 내에서 운영하기

Free 티어는 소규모 프로젝트나 개인 블로그에 적합합니다. 다음 최적화를 통해 제한 내에서 효과적으로 운영할 수 있습니다.

### 현재 프로젝트 정보

- **프로젝트**: tech-blog
- **조직**: twodragon
- **프로덕션 도메인**: tech.2twodragon.com
- **DSN**: `https://61fd23528aff138753e071de26c5b306@o4510686170710016.ingest.us.sentry.io/4510686177984512`
- **Loader Script**: `https://js.sentry-cdn.com/61fd23528aff138753e071de26c5b306.min.js`
- **구현 방식**: Loader Script + `Sentry.onLoad()` (권장 방식)

## GitHub 통합 기능

### Loader Script 방식 주의사항

현재 프로젝트는 **Sentry Loader Script** 방식을 사용하고 있습니다. 이 방식의 특징:

- ✅ **장점**: 
  - CDN을 통한 빠른 로드
  - 자동 업데이트 (Sentry가 최신 SDK 버전 제공)
  - CSP 위반 최소화
- ⚠️ **제한사항**:
  - `consoleLoggingIntegration` 사용 불가
  - 대신 `beforeSendLog`에서 로그 필터링 필요
  - `BrowserTracing`은 자동 설정됨

### 1. GitHub Issues 연동

Sentry에서 에러를 GitHub Issues로 자동 생성할 수 있습니다.

#### 설정 방법

1. **Sentry 대시보드** 접속
2. **Settings** → **Integrations** → **GitHub** 선택
3. **Configure** 클릭하여 GitHub OAuth 인증
4. **Repository** 선택 (예: `twodragon/tech-blog`)
5. **Issue Rules** 설정:
   - **New Issue**: 에러 발생 시 자동으로 GitHub Issue 생성
   - **Issue Assignment**: 특정 사용자에게 자동 할당
   - **Issue Labels**: 자동 라벨링 (예: `bug`, `sentry`)

#### Free 티어 최적화

```yaml
# .github/ISSUE_TEMPLATE/sentry-bug.yml
name: Sentry Bug Report
description: Sentry에서 자동 생성된 버그 리포트
labels: ["bug", "sentry", "auto-generated"]
body:
  - type: markdown
    attributes:
      value: |
        이 이슈는 Sentry에서 자동으로 생성되었습니다.
        원본 이벤트: [Sentry 이벤트 링크]
  - type: textarea
    id: sentry-event
    attributes:
      label: Sentry 이벤트 정보
      description: 원본 Sentry 이벤트 링크
    validations:
      required: true
```

**최적화 팁**:
- **중요한 에러만** GitHub Issue로 생성 (샘플링 10% 이하)
- **중복 이슈 방지**: 동일한 에러는 하나의 Issue로 그룹핑
- **자동 해결**: Sentry에서 해결된 이슈는 GitHub Issue도 자동으로 닫기

### 2. GitHub Releases 추적

GitHub Releases를 Sentry에 연결하여 배포 추적 및 릴리스 정보를 관리합니다.

#### 설정 방법

1. **Sentry 프로젝트** → **Settings** → **Releases**
2. **Create Release** 클릭
3. **GitHub Integration** 선택
4. **Repository** 및 **Release** 선택

#### GitHub Actions 통합

```yaml
# .github/workflows/release.yml
name: Create Sentry Release

on:
  release:
    types: [published]

jobs:
  create-sentry-release:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Create Sentry Release
        uses: getsentry/action-release@v1
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: twodragon
          SENTRY_PROJECT: tech-blog
        with:
          environment: production
          version: ${{ github.event.release.tag_name }}
          # Free 티어 최적화: 소스맵 업로드 제외 (비용 절감)
          # sourcemaps: false
```

**최적화 팁**:
- **소스맵 업로드 제외**: Free 티어에서는 소스맵 업로드 비용이 발생할 수 있으므로 제외
- **프로덕션만 추적**: Preview/Development 환경은 제외
- **태그 기반 릴리스**: GitHub Release 태그만 추적

### 3. GitHub Commits 연결

커밋 정보를 Sentry 이벤트에 연결하여 에러 발생 시 관련 커밋을 추적합니다.

#### 설정 방법

1. **Sentry 프로젝트** → **Settings** → **Source Maps**
2. **GitHub Integration** 활성화
3. **Repository** 선택
4. **Commits** 섹션에서 커밋 추적 활성화

#### 자동 커밋 추적

현재 프로젝트는 Jekyll 기반 정적 사이트이므로, GitHub Actions에서 릴리스 정보를 주입하는 방식이 적합합니다.

```javascript
// _includes/sentry.html (현재 설정)
Sentry.init({
  // 환경 설정 (현재 구현)
  environment: window.location.hostname === 'tech.2twodragon.com' 
    ? 'production' 
    : window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'development'
    : 'preview',
  
  // Release 정보 (GitHub Actions에서 주입 가능)
  // release: 'tech-blog@1.0.0', // 주석 처리됨 (필요 시 활성화)
  
  // Source Maps 설정 (현재 구현)
  _experiments: {
    // 프로덕션에서는 비활성화, 개발 환경에서만 활성화
    enableSourceMaps: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  }
});
```

**GitHub Actions에서 릴리스 정보 주입** (선택사항):

```yaml
# .github/workflows/jekyll.yml에 추가 가능
- name: Build with Jekyll
  run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
  env:
    JEKYLL_ENV: production
    GITHUB_SHA: ${{ github.sha }}
    GITHUB_REF: ${{ github.ref }}
```

그리고 Jekyll 빌드 시 환경 변수를 Sentry 설정에 주입:

```liquid
<!-- _includes/sentry.html -->
<script>
Sentry.init({
  release: '{{ site.github.build_revision | default: "unknown" }}',
  // 또는 Jekyll 플러그인을 통해 주입
});
</script>
```

**최적화 팁**:
- **커밋 정보만 추적**: 소스맵은 업로드하지 않음 (Free 티어 제한)
- **프로덕션만 추적**: 개발 환경 커밋은 제외
- **현재는 릴리스 정보 주석 처리**: 필요 시 활성화 가능

### 4. GitHub Pull Requests 연동

Sentry 이슈를 GitHub PR과 연결하여 코드 리뷰 시 관련 에러를 확인할 수 있습니다.

#### 설정 방법

1. **Sentry 프로젝트** → **Settings** → **Integrations** → **GitHub**
2. **Pull Request Comments** 활성화
3. **Comment Template** 설정 (선택사항)

**최적화 팁**:
- **중요한 에러만** PR에 코멘트 (샘플링 5% 이하)
- **자동 해결**: PR 머지 시 관련 Sentry 이슈 자동 해결

## 보안 최적화

### 1. 민감 정보 필터링

#### 자동 필터링 (현재 구현)

```javascript
// _includes/sentry.html의 beforeSend 함수 (실제 구현)
beforeSend(event, hint) {
  // Free 티어 최적화: 개발 환경 에러는 전송하지 않음
  if (window.location.hostname !== 'tech.2twodragon.com') {
    return null; // 프로덕션만 에러 수집
  }
  
  // 민감 정보 제거 및 보안 강화
  if (event.request) {
    // 쿠키 제거
    delete event.request.cookies;
    
    // URL에서 민감한 쿼리 파라미터 제거
    if (event.request.url) {
      try {
        const url = new URL(event.request.url);
        const sensitiveParams = [
          'token', 'key', 'password', 'secret', 'api_key', 'apikey',
          'access_token', 'refresh_token', 'auth', 'authorization',
          'credential', 'private_key', 'session', 'sessionid'
        ];
        sensitiveParams.forEach(param => {
          url.searchParams.delete(param);
        });
        event.request.url = url.toString();
      } catch (e) {
        // URL 파싱 실패 시 그대로 유지
      }
    }
  }
  
  // 스택 트레이스에서 민감 정보 제거
  if (event.exception && event.exception.values) {
    event.exception.values.forEach(exception => {
      if (exception.stacktrace && exception.stacktrace.frames) {
        exception.stacktrace.frames.forEach(frame => {
          // 파일 경로에서 민감 정보 제거
          if (frame.filename) {
            frame.filename = frame.filename.replace(/\/home\/[^\/]+/g, '/home/***');
            frame.filename = frame.filename.replace(/\/Users\/[^\/]+/g, '/Users/***');
          }
          // 코드 컨텍스트에서 민감 정보 제거
          if (frame.vars) {
            Object.keys(frame.vars).forEach(key => {
              const lowerKey = key.toLowerCase();
              if (lowerKey.includes('password') || 
                  lowerKey.includes('token') || 
                  lowerKey.includes('secret') ||
                  lowerKey.includes('key') ||
                  lowerKey.includes('auth')) {
                frame.vars[key] = '***REDACTED***';
              }
            });
          }
        });
      }
    });
  }
  
  // 특정 에러 무시 (정상적인 보안 에러 및 이미지 로드 실패)
  if (event.exception) {
    const error = hint.originalException;
    if (error && error.message) {
      const errorMessage = error.message.toLowerCase();
      if (errorMessage.includes('content security policy') ||
          errorMessage.includes('csp') ||
          errorMessage.includes('extension') ||
          errorMessage.includes('chrome-extension') ||
          errorMessage.includes('moz-extension') ||
          errorMessage.includes('failed to load') ||
          errorMessage.includes('load link') ||
          errorMessage.includes('long task detected') ||
          errorMessage.includes('layout shift detected') ||
          (errorMessage.includes('image') && (errorMessage.includes('404') || errorMessage.includes('not found')))) {
        return null; // 이벤트 무시
      }
    }
  }
  
  // 이미지 로드 실패 에러 필터링 (한글 파일명 포함)
  if (event.request && event.request.url) {
    const url = event.request.url.toLowerCase();
    if (url.includes('_og.png') || 
        url.includes('og.png') || 
        url.includes('og.jpg') || 
        url.includes('og.webp') ||
        url.includes('favicon') ||
        url.includes('robots.txt') ||
        /[\uAC00-\uD7A3]/.test(event.request.url)) { // 한글 포함된 URL
      return null; // 이벤트 무시
    }
  }
  
  // Free 티어 최적화: 이벤트 크기 제한
  if (event.extra && JSON.stringify(event.extra).length > 5000) {
    event.extra = { message: 'Extra data too large, truncated for Free tier optimization' };
  }
  
  return event;
}
```

#### GitHub Secrets 관리

```yaml
# .github/workflows/sentry-release.yml
env:
  # GitHub Secrets에 저장
  SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
  SENTRY_DSN: ${{ secrets.SENTRY_DSN }}
  
  # 공개 정보는 환경 변수로
  SENTRY_ORG: twodragon
  SENTRY_PROJECT: tech-blog
```

**보안 체크리스트**:
- [ ] DSN은 공개 저장소에 커밋하지 않음
- [ ] Auth Token은 GitHub Secrets에 저장
- [ ] 민감한 환경 변수는 `.env.example`에만 예시 포함
- [ ] Sentry 이벤트에서 민감 정보 자동 필터링 확인

### 2. CSP (Content Security Policy) 설정

```html
<!-- _includes/head.html (현재 구현) -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-inline' ... https://js.sentry-cdn.com https://browser.sentry-cdn.com;
  connect-src 'self' ... https://o4510686170710016.ingest.us.sentry.io https://*.ingest.sentry.io https://browser.sentry-cdn.com;
  ...
">
```

**현재 CSP 설정**:
- **Sentry 스크립트**: `https://js.sentry-cdn.com`, `https://browser.sentry-cdn.com` 허용
- **Sentry 수집 엔드포인트**: `https://o4510686170710016.ingest.us.sentry.io`, `https://*.ingest.sentry.io` 허용
- **특정 도메인만 허용**: 와일드카드 패턴 `*.ingest.sentry.io` 사용
- **Loader Script 방식**: CDN을 통한 스크립트 로드로 CSP 위반 최소화

**보안 최적화**:
- **특정 도메인만 허용**: `*.ingest.sentry.io` 패턴 사용
- **스크립트 로드**: Sentry Loader Script만 허용
- **인라인 스크립트 최소화**: `'unsafe-inline'`은 다른 서비스(Giscus 등)를 위해 필요

### 3. GitHub Actions 보안

```yaml
# .github/workflows/sentry-release.yml
permissions:
  contents: read  # 최소 권한만 부여
  issues: write   # Issues 연동 시에만 필요

jobs:
  create-release:
    runs-on: ubuntu-latest
    steps:
      - name: Create Sentry Release
        uses: getsentry/action-release@v1
        env:
          # Secrets 사용 (절대 하드코딩하지 않음)
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
```

**보안 체크리스트**:
- [ ] 최소 권한 원칙 적용
- [ ] Secrets는 절대 로그에 출력하지 않음
- [ ] Actions는 신뢰할 수 있는 소스에서만 사용
- [ ] Dependabot으로 의존성 보안 업데이트

## 효율성 최적화

### 1. 이벤트 샘플링

#### 현재 설정 (최적화됨)

```javascript
// _includes/sentry.html (실제 구현)
Sentry.onLoad(function() {
  Sentry.init({
    // 환경 설정
    environment: window.location.hostname === 'tech.2twodragon.com' 
      ? 'production' 
      : window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
      ? 'development'
      : 'preview',
    
    // 트레이스 샘플링: 5% (Free 티어 최적화)
    tracesSampleRate: window.location.hostname === 'tech.2twodragon.com' 
      ? 0.05  // 프로덕션: 5%
      : 0.0,  // 개발/프리뷰: 0%
    
    // Session Replay: 비활성화 (비용 절감)
    replaysSessionSampleRate: 0.0,
    replaysOnErrorSampleRate: 0.0,
    
    // Logs: 구조화된 로깅 활성화
    enableLogs: true,
    
    // Source Maps: 프로덕션에서는 비활성화
    _experiments: {
      enableSourceMaps: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    },
    
    // 에러 샘플링: 프로덕션만 100% 수집
    sampleRate: window.location.hostname === 'tech.2twodragon.com' 
      ? 1.0   // 프로덕션: 100% (중요한 에러는 모두 수집)
      : 0.0,  // 개발/프리뷰: 0%
    
    // 통합 설정
    // 참고: Loader Script를 사용할 때는 consoleLoggingIntegration을 사용할 수 없음
    // 대신 beforeSendLog에서 필터링하여 warn, error만 전송
    integrations: [
      // BrowserTracing은 Loader Script에서 자동 설정됨
      // Console 로깅은 beforeSendLog에서 처리
    ],
  });
});
```

**주요 특징**:
- **Loader Script 방식**: `Sentry.onLoad()` 사용 (권장 방식)
- **프로덕션 도메인**: `tech.2twodragon.com`만 수집
- **에러 샘플링**: 프로덕션 100%, 개발/프리뷰 0%
- **트레이스 샘플링**: 프로덕션 5%, 개발/프리뷰 0%
- **Session Replay**: 완전 비활성화
- **Source Maps**: 개발 환경에서만 활성화

#### 동적 샘플링 (고급)

```javascript
// 이벤트 수에 따라 동적으로 샘플링 조정
Sentry.init({
  beforeSend(event, hint) {
    // 월간 이벤트 수 확인 (로컬 스토리지 기반)
    const monthlyEvents = parseInt(localStorage.getItem('sentry_monthly_events') || '0');
    
    // 4,000개 이상이면 샘플링 50%
    if (monthlyEvents > 4000) {
      if (Math.random() > 0.5) {
        return null; // 50% 샘플링
      }
    }
    
    // 이벤트 수 증가
    localStorage.setItem('sentry_monthly_events', (monthlyEvents + 1).toString());
    
    return event;
  }
});
```

### 2. 로그 레벨 필터링

```javascript
// _includes/sentry.html (실제 구현)
beforeSendLog(log, hint) {
  // Free 티어 최적화: 개발 환경 로그는 전송하지 않음
  if (window.location.hostname !== 'tech.2twodragon.com') {
    return null; // 프로덕션만 로그 수집
  }
  
  // Free 티어 최적화: info, debug 레벨은 전송하지 않음 (warn, error만)
  // 단, 초기화 확인 로그는 예외 (환경 정보 포함)
  const isInitializationLog = log.message && 
    (log.message.includes('Sentry initialized') || 
     log.message.includes('Logs enabled'));
  
  if ((log.level === 'info' || log.level === 'debug' || log.level === 'trace') && !isInitializationLog) {
    return null; // info, debug, trace는 제외 (Free 티어 최적화)
  }
  
  // 초기화 로그는 info를 warn으로 변환 (beforeSendLog에서 필터링 방지)
  if (isInitializationLog && log.level === 'info') {
    log.level = 'warn';
  }
  
  // 민감 정보 제거
  if (log.message) {
    const sensitivePatterns = [
      /password/i,
      /token/i,
      /secret/i,
      /api[_-]?key/i,
      /apikey/i,
      /authorization/i,
      /bearer/i,
      /credential/i,
      /private[_-]?key/i
    ];
    
    if (sensitivePatterns.some(pattern => pattern.test(log.message))) {
      return null; // 민감한 로그는 전송하지 않음
    }
  }
  
  // 로그 길이 제한 (1,000자)
  if (log.message && log.message.length > 1000) {
    log.message = log.message.substring(0, 1000) + '... [truncated]';
  }
  
  return log;
}
```

**주요 특징**:
- **프로덕션만 수집**: `tech.2twodragon.com` 도메인만
- **로그 레벨**: warn, error만 전송 (info, debug, trace 제외)
- **초기화 로그 예외**: Sentry 초기화 확인 로그는 warn으로 변환하여 전송
- **민감 정보 필터링**: 패턴 매칭으로 자동 제거
- **로그 길이 제한**: 1,000자 초과 시 잘라서 전송

### 3. 에러 필터링

```javascript
// _includes/sentry.html (실제 구현)
beforeSend(event, hint) {
  // Free 티어 최적화: 개발 환경 에러는 전송하지 않음
  if (window.location.hostname !== 'tech.2twodragon.com') {
    return null; // 프로덕션만 에러 수집
  }
  
  // 특정 에러 무시 (정상적인 보안 에러 및 이미지 로드 실패)
  if (event.exception) {
    const error = hint.originalException;
    if (error && error.message) {
      const errorMessage = error.message.toLowerCase();
      // CSP 위반, 확장 프로그램 관련 에러는 무시
      // 이미지 로드 실패 (404, 한글 파일명 인코딩 문제 등)는 무시
      // Long task는 성능 경고이지 에러가 아니므로 무시
      if (errorMessage.includes('content security policy') ||
          errorMessage.includes('csp') ||
          errorMessage.includes('extension') ||
          errorMessage.includes('chrome-extension') ||
          errorMessage.includes('moz-extension') ||
          errorMessage.includes('failed to load') ||
          errorMessage.includes('load link') ||
          errorMessage.includes('long task detected') ||
          errorMessage.includes('layout shift detected') ||
          (errorMessage.includes('image') && (errorMessage.includes('404') || errorMessage.includes('not found')))) {
        return null; // 이벤트 무시
      }
    }
  }
  
  // Long task 및 성능 관련 에러 필터링 (커스텀 컨텍스트 기반)
  if (event.contexts && event.contexts.custom) {
    const customContext = event.contexts.custom;
    if (customContext.type === 'performance' && 
        (customContext.duration !== undefined || customContext.metric === 'CLS')) {
      return null; // 성능 메트릭은 에러로 보고하지 않음
    }
  }
  
  // 에러 메시지에서 Long task 패턴 확인 (추가 안전장치)
  if (event.message) {
    const message = event.message.toLowerCase();
    if (message.includes('long task') || message.includes('layout shift')) {
      return null; // 성능 경고는 에러로 보고하지 않음
    }
  }
  
  // 이미지 로드 실패 에러 필터링 (request URL 기반)
  if (event.request && event.request.url) {
    const url = event.request.url.toLowerCase();
    // OG 이미지, 한글 파일명 포함 URL은 무시
    if (url.includes('_og.png') || 
        url.includes('og.png') || 
        url.includes('og.jpg') || 
        url.includes('og.webp') ||
        url.includes('favicon') ||
        url.includes('robots.txt') ||
        /[\uAC00-\uD7A3]/.test(event.request.url)) { // 한글 포함된 URL
      return null; // 이벤트 무시
    }
  }
  
  // Free 티어 최적화: 이벤트 크기 제한
  if (event.extra && JSON.stringify(event.extra).length > 5000) {
    event.extra = { message: 'Extra data too large, truncated for Free tier optimization' };
  }
  
  return event;
}
```

**필터링되는 에러 유형**:
- **CSP 위반**: Content Security Policy 관련 에러
- **브라우저 확장 프로그램**: Chrome/Firefox 확장 프로그램 관련 에러
- **이미지 로드 실패**: 404, 한글 파일명 인코딩 문제
- **성능 경고**: Long task, Layout shift (에러가 아님)
- **OG 이미지**: Open Graph 이미지 로드 실패
- **Favicon, robots.txt**: 정적 파일 로드 실패

### 4. GitHub Actions 최적화

현재 프로젝트는 Jekyll 기반 정적 사이트로 GitHub Pages에 배포됩니다. Sentry Release 추적을 추가하려면 다음 워크플로우를 사용할 수 있습니다:

```yaml
# .github/workflows/jekyll.yml (현재 구조에 추가 가능)
name: Jekyll site CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.3'
          bundler-cache: true

      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v4

      # Sentry Release 생성 (프로덕션 배포 시에만, 선택사항)
      - name: Create Sentry Release
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        uses: getsentry/action-release@v1
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: twodragon
          SENTRY_PROJECT: tech-blog
        with:
          environment: production
          version: ${{ github.sha }}
          # Free 티어 최적화: 소스맵 제외 (Jekyll 정적 사이트이므로 소스맵 불필요)
          sourcemaps: false

      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
          LANG: en_US.UTF-8
          LC_ALL: en_US.UTF-8

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    permissions:
      pages: write
      id-token: write
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**참고사항**:
- **현재는 Sentry Release 추적 미구현**: 필요 시 위 워크플로우 추가 가능
- **Jekyll 정적 사이트**: 소스맵이 필요 없으므로 `sourcemaps: false` 권장
- **프로덕션만 추적**: `main` 브랜치 푸시 시에만 실행
- **GitHub Secrets 필요**: `SENTRY_AUTH_TOKEN` 설정 필요

**효율성 체크리스트**:
- [ ] 프로덕션만 이벤트 수집
- [ ] 트레이스 샘플링 5% 이하
- [ ] Session Replay 비활성화
- [ ] 로그 레벨 필터링 (warn, error만)
- [ ] 불필요한 에러 필터링
- [ ] GitHub Actions는 프로덕션 배포 시에만 실행

## 비용 최적화

### 1. 이벤트 수 예측 및 관리

#### 예상 이벤트 수 계산

```javascript
// scripts/estimate_sentry_events.js
/**
 * Sentry Free 티어 이벤트 수 예측
 * 
 * 일일 예상:
 * - 브라우저 에러: 10-50개 (프로덕션만)
 * - 브라우저 로그 (warn/error): 100-200개
 * - 트레이스 (5% 샘플링): 20-50개
 * - Vercel 서버 로그 (10% 샘플링): 50-100개
 * 
 * 총 일일: 약 180-400개
 * 총 월간: 약 5,400-12,000개
 * 
 * ⚠️ Free 티어 제한: 월 5,000개
 * → 샘플링을 더 낮춰야 할 수 있음
 */

const DAILY_ESTIMATE = {
  errors: { min: 10, max: 50 },
  logs: { min: 100, max: 200 },
  traces: { min: 20, max: 50 },
  serverLogs: { min: 50, max: 100 }
};

const monthlyEstimate = {
  min: Object.values(DAILY_ESTIMATE).reduce((sum, val) => sum + val.min, 0) * 30,
  max: Object.values(DAILY_ESTIMATE).reduce((sum, val) => sum + val.max, 0) * 30
};

console.log(`월간 예상 이벤트: ${monthlyEstimate.min} - ${monthlyEstimate.max}개`);
console.log(`Free 티어 제한: 5,000개`);
console.log(`권장 샘플링: ${Math.floor((5000 / monthlyEstimate.max) * 100)}%`);
```

#### 실제 사용량 모니터링

```bash
# scripts/monitor_sentry_quota.sh 실행
./scripts/monitor_sentry_quota.sh

# 또는 Sentry API 사용 (Auth Token 필요)
curl -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/projects/twodragon/tech-blog/stats/"
```

### 2. 샘플링 조정 전략

#### 단계별 샘플링 조정

```javascript
// 이벤트 수에 따라 자동으로 샘플링 조정
function getDynamicSampleRate() {
  // 로컬 스토리지에서 월간 이벤트 수 확인
  const monthlyEvents = parseInt(
    localStorage.getItem('sentry_monthly_events') || '0'
  );
  
  // Free 티어 제한: 5,000개
  const limit = 5000;
  const daysInMonth = 30;
  const dailyLimit = limit / daysInMonth; // 약 166개/일
  
  // 현재 일일 평균
  const dailyAverage = monthlyEvents / (new Date().getDate());
  
  if (dailyAverage > dailyLimit * 0.9) {
    // 90% 이상이면 샘플링 50%
    return 0.5;
  } else if (dailyAverage > dailyLimit * 0.7) {
    // 70% 이상이면 샘플링 75%
    return 0.75;
  } else {
    // 그 외는 100%
    return 1.0;
  }
}

Sentry.init({
  sampleRate: getDynamicSampleRate(),
  tracesSampleRate: 0.05, // 트레이스는 항상 5%
});
```

### 3. 불필요한 기능 비활성화

```javascript
// _includes/sentry.html (실제 구현)
Sentry.onLoad(function() {
  Sentry.init({
    // Session Replay: 비활성화 (Free 티어에서 비용 발생)
    replaysSessionSampleRate: 0.0, // 0% (비활성화 - 비용 절감)
    replaysOnErrorSampleRate: 0.0, // 0% (비활성화 - 비용 절감)
    
    // Source Maps: 프로덕션에서는 비활성화 (CSP 위반 방지 및 보안)
    // 개발 환경에서만 source map 로드
    _experiments: {
      enableSourceMaps: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    },
    
    // Profiling: 비활성화 (Free 티어 미지원)
    // 프로파일링은 Team 플랜 이상에서만 사용 가능
    
    // Loader Script 방식 사용
    // BrowserTracing은 Loader Script에서 자동 설정됨
    // consoleLoggingIntegration은 Loader Script 제한으로 사용 불가
    // 대신 beforeSendLog에서 필터링하여 warn, error만 전송
  });
});
```

**비활성화된 기능**:
- **Session Replay**: 완전 비활성화 (0%)
- **Source Maps**: 프로덕션에서 비활성화, 개발 환경에서만 활성화
- **Profiling**: Free 티어 미지원
- **consoleLoggingIntegration**: Loader Script 제한으로 사용 불가 (beforeSendLog로 대체)

### 4. GitHub Actions 비용 최적화

```yaml
# .github/workflows/sentry-release.yml
name: Sentry Release

on:
  # 프로덕션 배포 시에만 실행 (비용 절감)
  push:
    branches:
      - main
    # 특정 파일 변경 시에만 실행
    paths:
      - '_includes/sentry.html'
      - '_config.yml'
      - 'package.json'

jobs:
  create-release:
    runs-on: ubuntu-latest
    # 타임아웃 설정 (무한 실행 방지)
    timeout-minutes: 5
    steps:
      - name: Create Sentry Release
        uses: getsentry/action-release@v1
        # 소스맵 업로드 제외 (비용 절감)
        with:
          sourcemaps: false
```

**비용 최적화 체크리스트**:
- [ ] 이벤트 수 예측 및 모니터링
- [ ] 샘플링 조정 (트레이스 5%, 로그 warn/error만)
- [ ] Session Replay 비활성화
- [ ] Source Maps 비활성화
- [ ] GitHub Actions는 필요한 경우에만 실행
- [ ] 프로덕션만 이벤트 수집

## 모니터링 및 알림

### 1. 할당량 모니터링

#### 스크립트 사용

```bash
# scripts/monitor_sentry_quota.sh
./scripts/monitor_sentry_quota.sh

# 환경 변수 설정 (선택사항)
export SENTRY_AUTH_TOKEN=your_token
export SENTRY_ORG=twodragon
export SENTRY_PROJECT=tech-blog
./scripts/monitor_sentry_quota.sh
```

#### Sentry 대시보드 확인

1. **Sentry 대시보드** 접속
2. **Projects** → **tech-blog** → **Stats** 이동
3. **이벤트 수** 확인:
   - 일일 이벤트 수
   - 월간 이벤트 수
   - Free 티어 제한 대비 사용률

### 2. 알림 설정

#### 이메일 알림

1. **Sentry 대시보드** → **Settings** → **Alerts**
2. **Create Alert Rule** 클릭
3. **조건 설정**:
   - **이벤트 수가 4,000개 이상** (Free 티어 제한의 80%)
   - **중요한 에러 발생** (새로운 에러 그룹)
4. **알림 채널**: 이메일 선택

#### GitHub Issues 자동 생성

1. **Sentry 대시보드** → **Settings** → **Integrations** → **GitHub**
2. **Issue Rules** 설정:
   - **New Issue**: 중요한 에러만 GitHub Issue로 생성
   - **샘플링**: 10% 이하 (Free 티어 최적화)

### 3. 주간 리포트

```bash
# scripts/weekly_sentry_report.sh (새로 생성 필요)
#!/bin/bash

echo "📊 Sentry 주간 리포트"
echo "===================="
echo ""
echo "이벤트 수: Sentry 대시보드에서 확인"
echo "  - https://sentry.io/organizations/twodragon/projects/tech-blog/stats/"
echo ""
echo "주요 에러:"
echo "  - Sentry 대시보드에서 확인"
echo "  - https://sentry.io/organizations/twodragon/projects/tech-blog/issues/"
echo ""
echo "할당량 사용률:"
echo "  - Free 티어 제한: 5,000개/월"
echo "  - 현재 사용량: Sentry 대시보드에서 확인"
```

## 실전 체크리스트

### 초기 설정

- [x] Sentry 계정 생성 및 프로젝트 설정
- [ ] GitHub 통합 설정 (Issues, Releases, Commits) - 선택사항
- [x] DSN 설정 (Loader Script에 포함됨)
- [x] Sentry Loader Script 추가 (`_includes/sentry.html`)
- [x] CSP 설정 (Sentry 도메인 허용) - `_includes/head.html`에 설정됨
- [x] 샘플링 설정 (트레이스 5%, 프로덕션만) - `tech.2twodragon.com`만 수집
- [x] Loader Script 방식 사용 (`Sentry.onLoad()`)
- [x] 프로덕션 도메인 확인: `tech.2twodragon.com`

### 보안

- [x] 민감 정보 필터링 (`beforeSend`, `beforeSendLog`) - 구현됨
- [x] DSN은 Loader Script에 포함 (공개 가능, 읽기 전용)
- [ ] Auth Token은 GitHub Secrets에 저장 (Release 추적 시 필요)
- [x] CSP 설정 확인 - `_includes/head.html`에 설정됨
- [x] GitHub Actions 최소 권한 원칙 - `jekyll.yml`에 적용됨
- [x] 쿠키 자동 제거 - `beforeSend`에서 구현됨
- [x] URL 파라미터 필터링 - 민감한 쿼리 파라미터 자동 제거
- [x] 스택 트레이스 필터링 - 파일 경로 및 변수값에서 민감 정보 제거

### 효율성

- [x] 프로덕션만 이벤트 수집 - `tech.2twodragon.com`만 수집
- [x] 로그 레벨 필터링 (warn, error만) - `beforeSendLog`에서 구현
- [x] 불필요한 에러 필터링 - CSP, 확장 프로그램, 이미지 로드 실패 등 필터링
- [x] 트레이스 샘플링 5% - 프로덕션만 5% 샘플링
- [x] Session Replay 비활성화 - 0%로 설정됨
- [x] Source Maps 비활성화 - 프로덕션에서 비활성화
- [x] 이벤트 크기 제한 - 5,000자 초과 시 잘라서 전송
- [x] 로그 길이 제한 - 1,000자 초과 시 잘라서 전송

### 비용

- [ ] 이벤트 수 예측 및 모니터링 - `scripts/monitor_sentry_quota.sh` 사용
- [x] 샘플링 조정 (월 5,000개 제한 내) - 트레이스 5%, 에러 100% (프로덕션만)
- [x] Source Maps 비활성화 - 프로덕션에서 비활성화됨
- [x] GitHub Actions 최적화 - 현재는 Release 추적 미구현 (선택사항)
- [ ] 주간 리포트 확인 - 수동 확인 또는 스크립트 작성 필요
- [x] Session Replay 비활성화 - 비용 절감
- [x] 개발/프리뷰 환경 제외 - 프로덕션만 수집

### 모니터링

- [ ] 할당량 모니터링 스크립트 실행
- [ ] 알림 설정 (이벤트 수 4,000개 이상)
- [ ] GitHub Issues 자동 생성 설정
- [ ] 주간 리포트 확인

## 참고 자료

- [Sentry Free 티어 제한](https://sentry.io/pricing/)
- [Sentry GitHub 통합](https://docs.sentry.io/product/integrations/source-code-mgmt/github/)
- [Sentry 샘플링 가이드](https://docs.sentry.io/product/data-management-settings/filtering/)
- [GitHub Actions Sentry 통합](https://github.com/getsentry/action-release)
- [README_SENTRY_LOGS.md](./README_SENTRY_LOGS.md): Sentry 로그 설정 가이드

## 현재 프로젝트 설정 요약

### 구현된 최적화

1. **Loader Script 방식**: `Sentry.onLoad()` 사용 (권장 방식)
2. **프로덕션만 수집**: `tech.2twodragon.com` 도메인만 이벤트 수집
3. **샘플링**:
   - 에러: 프로덕션 100%, 개발/프리뷰 0%
   - 트레이스: 프로덕션 5%, 개발/프리뷰 0%
4. **로그 필터링**: warn, error만 전송 (info, debug, trace 제외)
5. **에러 필터링**: CSP, 확장 프로그램, 이미지 로드 실패 등 무시
6. **보안**: 민감 정보 자동 필터링 (쿠키, URL 파라미터, 스택 트레이스)
7. **비용 절감**: Session Replay 비활성화, Source Maps 프로덕션에서 비활성화

### 선택적 구현 사항

1. **GitHub Releases 추적**: GitHub Actions 워크플로우에 추가 가능
2. **GitHub Issues 연동**: Sentry 대시보드에서 설정 가능
3. **GitHub Commits 연결**: Sentry 프로젝트 설정에서 활성화 가능

### 모니터링 도구

- `scripts/monitor_sentry_quota.sh`: 할당량 모니터링
- `scripts/verify_sentry_logs.js`: 로그 검증
- Sentry 대시보드: https://sentry.io/organizations/twodragon/projects/tech-blog/

## 업데이트 이력

- **2026-01-10**: 초기 문서 작성, Sentry + GitHub 통합 Free 티어 최적화 가이드
- **2026-01-10**: 보안, 효율성, 비용 최적화 섹션 추가
- **2026-01-10**: 실전 체크리스트 및 모니터링 가이드 추가
- **2026-01-10**: 실제 프로젝트 설정 반영 (`_includes/sentry.html` 기반)
