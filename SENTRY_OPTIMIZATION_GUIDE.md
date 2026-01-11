# Sentry 로그 및 트레이싱 최적화 가이드

이 문서는 Sentry 로그, 트레이싱, 성능 모니터링을 전체적으로 개선하는 가이드를 제공합니다.

## 📋 목차

1. [적용된 개선사항](#적용된-개선사항)
2. [Performance Monitoring 강화](#performance-monitoring-강화)
3. [에러 그룹핑 개선](#에러-그룹핑-개선)
4. [Release 정보 자동화](#release-정보-자동화)
5. [비용 최적화](#비용-최적화)
6. [모니터링 및 검증](#모니터링-및-검증)

## 적용된 개선사항

### 1. Performance Monitoring 강화

#### Web Vitals 자동 추적

Sentry Performance Monitoring에 다음 메트릭이 자동으로 전송됩니다:

- **TTFB (Time to First Byte)**: 서버 응답 시간
- **LCP (Largest Contentful Paint)**: 가장 큰 콘텐츠 렌더링 시간
- **FID (First Input Delay)**: 첫 사용자 입력 지연 시간
- **CLS (Cumulative Layout Shift)**: 누적 레이아웃 시프트

#### 구현 방법

```javascript
// TTFB 추적
if (window.performance && window.performance.timing) {
  const timing = window.performance.timing;
  const ttfb = timing.responseStart - timing.requestStart;
  
  if (ttfb > 0) {
    Sentry.metrics.distribution('ttfb', ttfb, {
      unit: 'millisecond',
      tags: {
        page: window.location.pathname
      }
    });
  }
}

// LCP, FID, CLS는 Performance Observer를 통해 자동 수집
```

### 2. 에러 그룹핑 개선

#### Fingerprinting 강화

동일한 에러를 더 정확하게 그룹핑하여 중복 제거:

```javascript
// 에러 타입과 메시지 기반 그룹핑
const fingerprint = [
  errorType,
  errorMessage.substring(0, 100).replace(/\s+/g, ' ').trim()
];

// URL 패턴이 포함된 경우 URL도 fingerprint에 추가
if (event.request && event.request.url) {
  const url = new URL(event.request.url);
  fingerprint.push(url.pathname); // 경로만 포함 (쿼리 파라미터 제외)
}

event.fingerprint = fingerprint;
```

**효과**:
- 동일한 에러의 중복 제거
- 더 정확한 에러 그룹핑
- 에러 분석 효율성 향상

### 3. Release 정보 자동화

#### Vercel 환경 변수 활용

```javascript
release: (function() {
  // Vercel 환경 변수 우선 사용
  if (typeof window !== 'undefined' && window.VERCEL_GIT_COMMIT_SHA) {
    return 'tech-blog@' + window.VERCEL_GIT_COMMIT_SHA.substring(0, 7);
  }
  // GitHub Pages 환경 변수
  if (typeof window !== 'undefined' && window.BUILD_ID) {
    return 'tech-blog@' + window.BUILD_ID.substring(0, 7);
  }
  // 기본값: 날짜 기반 (프로덕션만)
  if (window.location.hostname === 'tech.2twodragon.com') {
    const date = new Date();
    return 'tech-blog@' + date.getFullYear() + 
           String(date.getMonth() + 1).padStart(2, '0') + 
           String(date.getDate()).padStart(2, '0');
  }
  return undefined;
})(),
```

#### GitHub Actions 통합

`.github/workflows/sentry-release.yml`에서 자동으로 Release 생성:

```yaml
- name: Create Sentry Release
  uses: getsentry/action-release@v1
  with:
    environment: production
    version: ${{ github.sha }}
    set_commits: auto
    finalize: true
```

### 4. 비용 최적화

#### 동적 샘플링

월간 이벤트 수에 따라 자동으로 샘플링 조정:

```javascript
sampleRate: (function() {
  // 개발/프리뷰 환경은 수집하지 않음
  if (window.location.hostname !== 'tech.2twodragon.com') {
    return 0.0;
  }
  
  // 동적 샘플링: 월간 이벤트 수에 따라 자동 조정
  const freeTierLimit = 5000;
  const monthlyEvents = parseInt(localStorage.getItem('sentry_monthly_events') || '0');
  
  // 80% 이상 사용 시 샘플링 50%
  if (monthlyEvents > freeTierLimit * 0.8) {
    return 0.5;
  }
  // 60% 이상 사용 시 샘플링 75%
  else if (monthlyEvents > freeTierLimit * 0.6) {
    return 0.75;
  }
  
  // 정상 범위: 100% 수집
  return 1.0;
})(),
```

#### 트레이스 샘플링

```javascript
tracesSampleRate: window.location.hostname === 'tech.2twodragon.com' 
  ? 0.05  // 프로덕션: 5% (Free 티어 최적화)
  : 0.0,  // 개발/프리뷰: 0%
```

#### 로그 필터링

```javascript
beforeSendLog(log, hint) {
  // 프로덕션만 수집
  if (window.location.hostname !== 'tech.2twodragon.com') {
    return null;
  }
  
  // warn, error만 전송 (info, debug 제외)
  if (log.level === 'info' || log.level === 'debug' || log.level === 'trace') {
    return null;
  }
  
  return log;
}
```

## Performance Monitoring 강화

### Web Vitals 추적

#### TTFB (Time to First Byte)

```javascript
// Performance Timing API 사용
const timing = window.performance.timing;
const ttfb = timing.responseStart - timing.requestStart;

Sentry.metrics.distribution('ttfb', ttfb, {
  unit: 'millisecond',
  tags: {
    page: window.location.pathname
  }
});
```

#### LCP (Largest Contentful Paint)

```javascript
const lcpObserver = new PerformanceObserver(function(list) {
  const entries = list.getEntries();
  const lastEntry = entries[entries.length - 1];
  if (lastEntry && lastEntry.renderTime) {
    Sentry.metrics.distribution('lcp', lastEntry.renderTime, {
      unit: 'millisecond',
      tags: {
        page: window.location.pathname
      }
    });
  }
});
lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
```

#### FID (First Input Delay)

```javascript
const fidObserver = new PerformanceObserver(function(list) {
  for (const entry of list.getEntries()) {
    const fid = entry.processingStart - entry.startTime;
    Sentry.metrics.distribution('fid', fid, {
      unit: 'millisecond',
      tags: {
        page: window.location.pathname
      }
    });
  }
});
fidObserver.observe({ entryTypes: ['first-input'] });
```

#### CLS (Cumulative Layout Shift)

```javascript
let clsValue = 0;
const clsObserver = new PerformanceObserver(function(list) {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) {
      clsValue += entry.value;
    }
  }
});
clsObserver.observe({ entryTypes: ['layout-shift'] });

// 페이지 언로드 시 최종 CLS 전송
window.addEventListener('beforeunload', function() {
  if (clsValue > 0) {
    Sentry.metrics.distribution('cls', clsValue, {
      unit: 'none',
      tags: {
        page: window.location.pathname
      }
    });
  }
});
```

### Sentry 대시보드에서 확인

1. **Performance** → **Web Vitals** 이동
2. **Metrics** 섹션에서 TTFB, LCP, FID, CLS 확인
3. **페이지별 필터링**: `page` 태그로 특정 페이지 성능 확인

## 에러 그룹핑 개선

### Fingerprinting 전략

#### 기본 Fingerprinting

```javascript
// 에러 타입과 메시지 기반
const fingerprint = [
  errorType,  // 예: "TypeError", "ReferenceError"
  errorMessage.substring(0, 100).replace(/\s+/g, ' ').trim()
];
```

#### URL 기반 Fingerprinting

```javascript
// 동적 URL 값 제외하고 경로만 포함
if (event.request && event.request.url) {
  try {
    const url = new URL(event.request.url);
    fingerprint.push(url.pathname); // 쿼리 파라미터 제외
  } catch (e) {
    // URL 파싱 실패 시 무시
  }
}
```

### 효과

- **중복 제거**: 동일한 에러가 여러 번 발생해도 하나로 그룹핑
- **정확한 분석**: 에러 타입과 위치를 정확히 파악
- **비용 절감**: 중복 이벤트 제거로 Free 티어 제한 내 운영

## Release 정보 자동화

### Vercel 환경 변수

Vercel은 자동으로 다음 환경 변수를 주입합니다:

- `VERCEL_GIT_COMMIT_SHA`: Git 커밋 SHA
- `VERCEL_URL`: 배포 URL
- `VERCEL_ENV`: 환경 (production, preview, development)

### GitHub Actions 통합

`.github/workflows/sentry-release.yml`에서 자동 Release 생성:

```yaml
- name: Create Sentry Release
  uses: getsentry/action-release@v1
  env:
    SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
    SENTRY_ORG: ${{ secrets.SENTRY_ORG || 'twodragon' }}
    SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT || 'tech-blog' }}
  with:
    environment: production
    version: ${{ github.sha }}
    set_commits: auto
    finalize: true
```

### Release 확인

1. **Sentry 대시보드** → **Releases** 이동
2. Release 목록에서 최신 Release 확인
3. Release 상세 페이지에서:
   - 커밋 정보 확인
   - 에러 통계 확인
   - 성능 메트릭 확인

## 비용 최적화

### Free 티어 제한

- **월 5,000 이벤트** 제한
- **30일 데이터 보존**
- **트레이스 샘플링**: 5% (프로덕션)

### 최적화 전략

#### 1. 환경별 필터링

```javascript
// 프로덕션만 수집
if (window.location.hostname !== 'tech.2twodragon.com') {
  return null;
}
```

#### 2. 동적 샘플링

```javascript
// 월간 이벤트 수에 따라 자동 조정
if (monthlyEvents > freeTierLimit * 0.8) {
  return 0.5; // 50% 샘플링
}
```

#### 3. 로그 레벨 필터링

```javascript
// warn, error만 전송
if (log.level === 'info' || log.level === 'debug' || log.level === 'trace') {
  return null;
}
```

#### 4. 중복 에러 샘플링

```javascript
// 1시간 이내에 동일한 에러가 10번 이상 발생하면 50% 샘플링
if (errorCount > 10 && (now - lastErrorTime) < oneHour) {
  if (Math.random() > 0.5) {
    return null; // 50% 샘플링
  }
}
```

#### 5. 이벤트 크기 제한

```javascript
// 8KB 제한
const maxEventSize = 8000;
if (eventSize > maxEventSize) {
  // 이벤트 크기 축소
  event.extra = { message: 'Extra data truncated' };
  event.breadcrumbs = event.breadcrumbs.slice(-10);
}
```

### 예상 이벤트 수

| 항목 | 예상 수 | 샘플링 |
|------|---------|--------|
| **에러 이벤트** | 100-200개/일 | 100% (프로덕션만) |
| **트레이스** | 20-50개/일 | 5% |
| **로그 (warn/error)** | 50-100개/일 | 100% |
| **Web Vitals** | 100-200개/일 | 100% (메트릭) |
| **총 예상** | 270-550개/일 | - |
| **월간 예상** | 8,100-16,500개 | ⚠️ 초과 가능 |

**주의**: Web Vitals 메트릭은 이벤트로 카운트되지 않지만, 트레이스와 함께 사용량이 증가할 수 있습니다.

## 모니터링 및 검증

### Sentry 대시보드 확인

#### 1. Performance 메트릭

1. **Performance** → **Web Vitals** 이동
2. **Metrics** 섹션에서 확인:
   - TTFB (Time to First Byte)
   - LCP (Largest Contentful Paint)
   - FID (First Input Delay)
   - CLS (Cumulative Layout Shift)

#### 2. 에러 그룹핑

1. **Issues** → 특정 에러 선택
2. **Fingerprint** 확인
3. **Similar Issues** 확인

#### 3. Release 정보

1. **Releases** → 최신 Release 선택
2. **Commits** 확인
3. **Issues** 확인

### 할당량 모니터링

#### 브라우저 콘솔 확인

```javascript
// localStorage에서 월간 이벤트 수 확인
const monthlyEvents = parseInt(localStorage.getItem('sentry_monthly_events') || '0');
console.log('Monthly events:', monthlyEvents, '/ 5000');
```

#### Sentry 대시보드

1. **Settings** → **Usage** 이동
2. **Monthly Events** 확인
3. **Quota** 확인

### 검증 체크리스트

- [ ] Web Vitals 메트릭이 Sentry에 전송되는지 확인
- [ ] 에러 그룹핑이 올바르게 작동하는지 확인
- [ ] Release 정보가 자동으로 생성되는지 확인
- [ ] 동적 샘플링이 작동하는지 확인
- [ ] 월간 이벤트 수가 Free 티어 제한 내에 있는지 확인

## 문제 해결

### Web Vitals가 전송되지 않는 경우

1. **브라우저 콘솔 확인**: 에러 메시지 확인
2. **Performance Observer 지원 확인**: 브라우저 호환성 확인
3. **Sentry SDK 버전 확인**: 최신 버전 사용 확인

### 에러 그룹핑이 작동하지 않는 경우

1. **Fingerprint 확인**: Sentry 대시보드에서 Fingerprint 확인
2. **에러 메시지 확인**: 동일한 메시지인지 확인
3. **URL 패턴 확인**: 동적 값이 포함되어 있는지 확인

### Release가 생성되지 않는 경우

1. **GitHub Actions 로그 확인**: 워크플로우 실행 로그 확인
2. **Sentry Auth Token 확인**: 권한 확인
3. **환경 변수 확인**: SENTRY_ORG, SENTRY_PROJECT 확인

## 참고 자료

- [Sentry Performance Monitoring](https://docs.sentry.io/platforms/javascript/performance/)
- [Sentry Web Vitals](https://docs.sentry.io/platforms/javascript/performance/web-vitals/)
- [Sentry Fingerprinting](https://docs.sentry.io/platforms/javascript/data-management/event-grouping/)
- [Sentry Release Management](https://docs.sentry.io/product/releases/)
- [Sentry Free Tier Limits](https://sentry.io/pricing/)

## 업데이트 이력

- **2026-01-11**: 초기 문서 작성, Performance Monitoring 강화
- **2026-01-11**: 에러 그룹핑 개선, Release 정보 자동화
- **2026-01-11**: 비용 최적화 전략 추가
