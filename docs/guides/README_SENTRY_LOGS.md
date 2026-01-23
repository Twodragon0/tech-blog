# Sentry Logs 설정 가이드

이 문서는 Sentry Logs와 Vercel Log Drains 통합 설정 가이드를 제공합니다.

## 📋 목차

1. [Sentry Logs 개요](#sentry-logs-개요)
2. [브라우저 로그 설정](#브라우저-로그-설정)
3. [Vercel Log Drains 설정](#vercel-log-drains-설정)
4. [비용 최적화](#비용-최적화)
5. [보안 고려사항](#보안-고려사항)
6. [로그 검증](#로그-검증)

## Sentry Logs 개요

Sentry Logs는 구조화된 로깅을 제공하여 에러, 트레이스와 함께 로그를 분석할 수 있습니다.

### 주요 기능

- **실시간 로그 접근**: 실시간으로 로그를 확인하고 쿼리
- **에러 상관관계**: 로그와 에러를 연결하여 전체 컨텍스트 파악
- **알림 및 대시보드**: 로그 쿼리 기반 알림 및 대시보드 위젯 생성

## 브라우저 로그 설정

### 현재 설정

현재 프로젝트는 다음 설정으로 Sentry Logs가 활성화되어 있습니다:

```javascript
Sentry.init({
  enableLogs: true,
  // Loader Script 제한으로 consoleLoggingIntegration 사용 불가
  // 대신 console.warn/error를 수동으로 래핑하여 Sentry로 전송
  beforeSendLog(log, hint) {
    // Free 티어 최적화: 프로덕션만 수집
    if (window.location.hostname !== 'tech.2twodragon.com') {
      return null;
    }
    // info, debug, trace 레벨 제외
    if (log.level === 'info' || log.level === 'debug' || log.level === 'trace') {
      return null;
    }
    // 로그 컨텍스트 정보 추가
    log.data = {
      page: window.location.pathname,
      url: window.location.href,
      referrer: document.referrer || 'none',
      timestamp: new Date().toISOString()
    };
    // 민감 정보 필터링
    // ...
  },
  // Breadcrumbs 강화: 에러 발생 시 관련 로그 자동 연결
  maxBreadcrumbs: 100,
  beforeBreadcrumb(breadcrumb, hint) {
    // 프로덕션만 breadcrumb 수집
    // 민감 정보 필터링
    // ...
  }
});
```

### Console 메서드 자동 전송

Loader Script 제한으로 `consoleLoggingIntegration`을 사용할 수 없으므로, `console.warn`과 `console.error`를 수동으로 래핑하여 Sentry로 자동 전송합니다:

```javascript
// console.warn 래핑
console.warn = function(...args) {
  originalWarn.apply(console, args);
  Sentry.logger.warn(message, {
    console: true,
    args: extra,
    page: window.location.pathname,
    timestamp: new Date().toISOString()
  });
};

// console.error 래핑
console.error = function(...args) {
  originalError.apply(console, args);
  Sentry.logger.error(message, {
    console: true,
    error: errorData,
    page: window.location.pathname,
    timestamp: new Date().toISOString()
  });
};
```

**효과**:
- `console.warn`, `console.error`가 자동으로 Sentry로 전송
- 원본 console 메서드 기능 유지
- 추가 컨텍스트 정보 자동 포함

### 로그 레벨

현재 설정에서는 다음 로그 레벨만 전송됩니다:

- ✅ **warn**: 경고 로그
- ✅ **error**: 에러 로그
- ❌ **log**: 일반 로그 (제외 - Free 티어 최적화)
- ❌ **info**: 정보 로그 (제외)
- ❌ **debug**: 디버그 로그 (제외)
- ❌ **trace**: 추적 로그 (제외)

### 로그 전송 방법

#### 1. console 메서드 사용 (자동 전송)

```javascript
// console.warn, console.error가 자동으로 Sentry로 전송됨
console.warn('Warning message', { context: 'additional data' });
console.error('Error occurred', { errorCode: 500 });

// 에러 객체도 자동 처리
console.error('API 호출 실패', new Error('Network error'), { endpoint: '/api/users' });
```

**자동 추가되는 컨텍스트**:
- `page`: 현재 페이지 경로
- `url`: 전체 URL
- `referrer`: 리퍼러 정보
- `timestamp`: 타임스탬프
- `console: true`: console 메서드에서 전송된 로그임을 표시

#### 2. Sentry.logger API 사용 (권장)

```javascript
// 구조화된 로그 전송 (더 많은 컨텍스트 정보 포함 가능)
Sentry.logger.warn('Warning message', {
  userId: 'user123',
  action: 'login',
  timestamp: new Date().toISOString(),
  page: window.location.pathname
});

Sentry.logger.error('Error occurred', {
  errorCode: 500,
  endpoint: '/api/users',
  requestId: 'req-123',
  stack: error.stack
});
```

**Sentry.logger의 장점**:
- 더 구조화된 데이터 전송
- 자동 태깅 (logLevel, source 등)
- 에러 객체 자동 처리
- Breadcrumbs에 자동 추가

## Vercel Log Drains 설정

Vercel Log Drains를 통해 서버 로그를 Sentry로 전송할 수 있습니다.

### 설정 단계

#### 1. Vercel Marketplace에서 Sentry 통합 설치

1. [Vercel Marketplace](https://vercel.com/integrations) 접속
2. "Sentry" 검색
3. "Add Integration" 클릭
4. 팀 또는 프로젝트 선택하여 설치

#### 2. Log Drain 설정

1. Vercel 대시보드 접속
2. **Team Settings** > **Drains** 이동
3. **Add Drain** 클릭
4. 다음 설정 입력:
   - **Name**: `Sentry Logs` (원하는 이름)
   - **Data Type**: `Logs` 선택
   - **Projects**: 모니터링할 프로젝트 선택
   - **Sampling Rate**: `10%` (Free 티어 최적화 - 필요시 조정)
   - **Destination**: `Sentry` 선택 (설치한 통합)

#### 3. Sentry 프로젝트 연결

1. Log Drain 생성 시 Sentry 프로젝트 선택
2. DSN 확인 (자동으로 설정됨)
3. **Create Drain** 클릭

### 환경 변수 설정

Vercel 프로젝트에 다음 환경 변수가 설정되어 있는지 확인:

```bash
# Sentry DSN (실제 DSN으로 교체 필요)
SENTRY_DSN=https://YOUR_SENTRY_DSN@o4510686170710016.ingest.us.sentry.io/YOUR_PROJECT_ID

# 환경별 설정 (선택사항)
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=tech-blog@1.0.0
```

### Vercel 환경 변수 설정 방법

```bash
# Vercel CLI 사용
vercel env add SENTRY_DSN production
vercel env add SENTRY_ENVIRONMENT production

# 또는 Vercel 대시보드에서
# Settings → Environment Variables → Add
```

## 비용 최적화

### Free 티어 제한

- **월 5,000 이벤트** 제한
- **30일 데이터 보존**

### 적용된 최적화

1. **프로덕션만 수집**: 개발/프리뷰 환경 제외
2. **로그 레벨 필터링**: warn, error만 전송
3. **console.log 제외**: 일반 로그는 전송하지 않음
4. **샘플링**: Vercel Log Drains 샘플링 10%
5. **로그 길이 제한**: 1,000자 초과 시 잘라서 전송
6. **중복 로그 필터링**: Sentry 자동 그룹핑 활용
7. **동적 샘플링**: 동일한 로그가 1시간 내 20번 이상 발생 시 70% 샘플링
8. **민감 정보 필터링**: API 키, 토큰 등 자동 필터링
9. **Breadcrumbs 제한**: 최대 100개로 제한

### 예상 이벤트 수

- **브라우저 로그**: warn/error만 → 약 100-200개/일
- **Vercel 서버 로그**: 10% 샘플링 → 약 50-100개/일
- **에러 이벤트**: 프로덕션만 → 약 10-50개/일
- **트레이스**: 5% 샘플링 → 약 20-50개/일

**총 예상**: 약 200-400개/일 (월 6,000-12,000개)

⚠️ **주의**: 트래픽이 많으면 샘플링을 더 낮춰야 할 수 있습니다.

## 보안 고려사항

### 자동 필터링

다음 정보는 자동으로 필터링됩니다:

- **민감한 키워드**: password, token, secret, api_key 등
- **URL 파라미터**: access_token, refresh_token, auth 등
- **스택 트레이스**: 파일 경로, 사용자 디렉토리 경로
- **변수값**: 민감한 변수명의 값

### 필터링 패턴

```javascript
// 자동으로 필터링되는 패턴
/password/i
/token/i
/secret/i
/api[_-]?key/i
/apikey/i
/authorization/i
/bearer/i
/credential/i
/private[_-]?key/i
```

### 수동 필터링

민감한 정보가 포함된 로그는 수동으로 필터링해야 합니다:

```javascript
// ❌ 나쁜 예
console.error('API key:', apiKey);

// ✅ 좋은 예
console.error('API key validation failed', {
  hasKey: !!apiKey,
  keyLength: apiKey ? apiKey.length : 0
});
```

## 로그 검증

### 브라우저 로그 확인

1. **Sentry 대시보드** 접속
2. **Logs** 섹션 이동
3. **Filters** 설정:
   - Environment: `production`
   - Level: `warn`, `error`
   - Time range: 최근 1시간

### Vercel 로그 확인

1. **Vercel 대시보드** 접속
2. **Deployments** → 특정 배포 선택
3. **Logs** 탭에서 로그 확인
4. **Sentry 대시보드**에서 동일한 로그 확인

### 테스트 로그 전송

```javascript
// 브라우저 콘솔에서 실행
console.warn('Test log from browser', {
  test: true,
  timestamp: new Date().toISOString()
});

// Sentry.logger 사용
Sentry.logger.error('Test error log', {
  test: true,
  source: 'manual-test'
});
```

### 로그 검증 체크리스트

- [ ] Sentry 대시보드에서 로그 확인 가능
- [ ] 프로덕션 환경에서만 로그 수집
- [ ] warn, error 레벨만 전송됨
- [ ] 민감 정보가 필터링됨
- [ ] Vercel Log Drains가 작동함
- [ ] 이벤트 수가 Free 티어 제한 내에 있음

## 문제 해결

### 로그가 전송되지 않는 경우

1. **환경 확인**: 프로덕션 환경인지 확인
2. **레벨 확인**: warn, error 레벨만 전송됨
3. **필터링 확인**: 민감 정보가 포함되어 필터링되었는지 확인
4. **브라우저 콘솔**: 에러 메시지 확인

### 이벤트 수가 너무 많은 경우

1. **샘플링 조정**: Vercel Log Drains 샘플링 낮추기
2. **로그 레벨 제한**: 더 엄격한 필터링 적용
3. **트레이스 샘플링**: 5% → 3%로 낮추기

### Vercel Log Drains가 작동하지 않는 경우

1. **통합 확인**: Sentry 통합이 설치되어 있는지 확인
2. **Drain 상태**: Vercel 대시보드에서 Drain 상태 확인
3. **권한 확인**: 필요한 권한이 있는지 확인
4. **Sentry 프로젝트**: 올바른 프로젝트에 연결되어 있는지 확인

## 참고 자료

- [Sentry Logs 문서](https://docs.sentry.io/platforms/javascript/guides/browser/logs/)
- [Vercel Log Drains 문서](https://vercel.com/docs/log-drains/configure-log-drains)
- [Sentry Free 티어 제한](https://sentry.io/pricing/)

## 빠른 시작 가이드

### 1. Vercel Log Drains 설정

```bash
# 대화형 설정 스크립트 실행
./scripts/setup_vercel_log_drains.sh
```

또는 수동으로:
1. [Vercel Marketplace](https://vercel.com/integrations)에서 Sentry 통합 설치
2. Vercel 대시보드 > Team Settings > Drains > Add Drain
3. 설정: Name, Data Type (Logs), Projects, Sampling Rate (10%), Destination (Sentry)

### 2. 로그 검증

```bash
# 로그 검증 스크립트 실행
node scripts/verify_sentry_logs.js
```

브라우저 콘솔에서 테스트:
```javascript
console.warn('Test log from browser', { test: true });
console.error('Test error log', { test: true });
```

### 3. 할당량 모니터링

```bash
# 할당량 모니터링 스크립트 실행
./scripts/monitor_sentry_quota.sh
```

Sentry 대시보드에서 확인:
- [통계](https://sentry.io/organizations/twodragon/projects/tech-blog/stats/)
- [로그](https://sentry.io/organizations/twodragon/projects/tech-blog/logs/)

## 로그 모니터링 개선

### 로그 레벨별 통계

로그 레벨별 통계가 자동으로 추적됩니다:

```javascript
// 1시간마다 자동으로 Sentry 메트릭으로 전송
Sentry.metrics.distribution('logs.warn', warnCount, {
  unit: 'none',
  tags: {
    page: window.location.pathname,
    period: '1h'
  }
});

Sentry.metrics.distribution('logs.error', errorCount, {
  unit: 'none',
  tags: {
    page: window.location.pathname,
    period: '1h'
  }
});
```

**확인 방법**:
1. Sentry 대시보드 → **Performance** → **Metrics**
2. `logs.warn`, `logs.error` 메트릭 확인
3. 페이지별 필터링 가능

### Breadcrumbs 강화

에러 발생 시 관련 로그가 자동으로 Breadcrumbs에 추가됩니다:

```javascript
// 최대 100개의 breadcrumb 저장
maxBreadcrumbs: 100,

// Breadcrumb 필터링 및 컨텍스트 추가
beforeBreadcrumb(breadcrumb, hint) {
  // 프로덕션만 수집
  // 민감 정보 필터링
  // 페이지 정보 추가
  breadcrumb.data = {
    page: window.location.pathname,
    timestamp: new Date().toISOString()
  };
  return breadcrumb;
}
```

**효과**:
- 에러 발생 전후의 사용자 액션 추적
- 관련 로그 자동 연결
- 문제 진단 시간 단축

### 로그 컨텍스트 정보

모든 로그에 다음 컨텍스트 정보가 자동으로 추가됩니다:

- **page**: 현재 페이지 경로
- **url**: 전체 URL
- **referrer**: 리퍼러 정보
- **timestamp**: 타임스탬프
- **navigationType**: 네비게이션 타입 (가능한 경우)
- **tags**: 로그 레벨, 소스 등

## 업데이트 이력

- **2026-01-10**: 초기 문서 작성, Vercel Log Drains 설정 가이드 추가
- **2026-01-10**: 검증 및 모니터링 스크립트 추가
- **2026-01-11**: Console 메서드 자동 전송 추가, 로그 컨텍스트 정보 강화
- **2026-01-11**: Breadcrumbs 강화, 로그 레벨별 통계 추적 추가
