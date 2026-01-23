# Sentry 프리티어 최적화 가이드

이 문서는 Sentry Free 티어 제한 내에서 보안, 효율성, 비용을 최적화하는 가이드를 제공합니다.

## 📋 목차

1. [프리티어 제한사항](#프리티어-제한사항)
2. [적용된 최적화](#적용된-최적화)
3. [보안 강화](#보안-강화)
4. [효율성 개선](#효율성-개선)
5. [비용 최적화](#비용-최적화)
6. [모니터링 및 검증](#모니터링-및-검증)

## 프리티어 제한사항

### Sentry Free 티어 제한

| 항목 | 제한 | 최적화 전략 |
|------|------|------------|
| **월간 이벤트** | 5,000개 | 동적 샘플링, 필터링 강화 |
| **데이터 보존** | 30일 | 중요 이벤트만 수집 |
| **트레이스** | 제한 없음 (이벤트로 카운트) | 5% 샘플링 |
| **로그** | 이벤트로 카운트 | warn, error만, 샘플링 |
| **Breadcrumbs** | 제한 없음 (이벤트 크기에 영향) | 50개로 제한 |

## 적용된 최적화

### 1. localStorage 사용 최적화

#### 캐싱 메커니즘

```javascript
// localStorage 캐시 및 헬퍼 함수
const storageCache = {};
const storageHelper = {
  get: function(key) {
    if (storageCache[key] !== undefined) {
      return storageCache[key]; // 캐시에서 반환
    }
    try {
      const value = localStorage.getItem(key);
      storageCache[key] = value; // 캐시에 저장
      return value;
    } catch (e) {
      return null;
    }
  },
  set: function(key, value) {
    try {
      localStorage.setItem(key, value);
      storageCache[key] = value;
      // 캐시 크기 제한 (메모리 최적화)
      const keys = Object.keys(storageCache);
      if (keys.length > 20) {
        delete storageCache[keys[0]]; // 오래된 항목 제거
      }
    } catch (e) {
      // localStorage 접근 실패 시 무시
    }
  }
};
```

**효과**:
- localStorage 접근 횟수 감소 (성능 향상)
- 메모리 사용량 최적화 (캐시 크기 제한)
- 에러 처리 강화

#### 키 이름 단축

```javascript
// 최적화 전
const logCountKey = 'sentry_log_count_' + logKeyHash;

// 최적화 후
const logCountKey = 'sl_' + logKeyHash; // 키 이름 단축 (메모리 절약)
```

**효과**:
- localStorage 저장 공간 절약
- 메모리 사용량 감소

### 2. 중복 코드 제거

#### 월간 이벤트 추적 통합

```javascript
// 통합 헬퍼 함수
const monthlyEventTracker = {
  get: function() {
    // 월간 이벤트 추적 로직 통합
    return {
      count: monthlyEvents,
      increment: function() { /* ... */ },
      getDailyLimit: function() { /* ... */ },
      getExpectedDailyAverage: function() { /* ... */ }
    };
  }
};
```

**효과**:
- 코드 중복 제거 (유지보수성 향상)
- 일관된 로직 적용
- 버그 가능성 감소

### 3. 보안 강화

#### User-Agent 해시 처리

```javascript
// 개인정보 보호: User-Agent 해시 처리
const hashUserAgent = function(ua) {
  if (!ua || ua.length < 10) return 'unknown';
  let hash = 0;
  for (let i = 0; i < Math.min(ua.length, 50); i++) {
    const char = ua.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return 'ua_' + Math.abs(hash).toString(36).substring(0, 8);
};
```

**효과**:
- 개인정보 보호 (User-Agent 전체 전송 방지)
- GDPR 준수
- 프라이버시 강화

#### 민감 정보 필터링 강화

```javascript
const sensitivePatterns = [
  /password/i,
  /token/i,
  /secret/i,
  /api[_-]?key/i,
  /apikey/i,
  /authorization/i,
  /bearer/i,
  /credential/i,
  /private[_-]?key/i,
  /sk-[a-zA-Z0-9]+/i, // API 키 패턴 (예: sk-xxx)
  /sntryu_[a-zA-Z0-9]+/i // Sentry 토큰 패턴
];
```

**효과**:
- API 키 자동 필터링
- 토큰 패턴 감지
- 보안 강화

### 4. 비용 최적화

#### 동적 샘플링 강화

```javascript
// 90% 이상 사용 시 샘플링 30% (더 공격적)
if (tracker.count > freeTierLimit * 0.9) {
  return 0.3; // 50% → 30%로 감소
}
// 80% 이상 사용 시 샘플링 50%
else if (tracker.count > freeTierLimit * 0.8) {
  return 0.5;
}
```

**효과**:
- 월간 이벤트 수 제한 준수
- 비용 절감
- 중요 이벤트 우선 수집

#### Breadcrumbs 감소

```javascript
// 최대 50개의 breadcrumb 저장 (100 → 50으로 감소)
maxBreadcrumbs: 50,
```

**효과**:
- 이벤트 크기 감소
- 비용 절감
- 성능 향상

#### 이벤트 크기 제한 강화

```javascript
// 6KB 제한 (8KB → 6KB로 감소)
const maxEventSize = 6000;

// Breadcrumbs 제한 (10 → 8로 감소)
if (filteredEvent.breadcrumbs && filteredEvent.breadcrumbs.length > 8) {
  filteredEvent.breadcrumbs = filteredEvent.breadcrumbs.slice(-8);
}
```

**효과**:
- 이벤트 크기 감소
- 전송 비용 절감
- 성능 향상

#### 로그 샘플링 강화

```javascript
// 1시간 이내에 동일한 로그가 15번 이상 발생하면 샘플링 20% (더 공격적)
if (logCount > 15 && (now - lastLogTime) < oneHour) {
  if (Math.random() > 0.2) {
    return null; // 80% 샘플링 (70% → 80%로 증가)
  }
}
```

**효과**:
- 중복 로그 제거
- 비용 절감
- 중요 로그 우선 수집

#### 에러 샘플링 강화

```javascript
// 1시간 이내에 동일한 에러가 8번 이상 발생하면 샘플링 30% (더 공격적)
if (errorCount > 8 && (now - lastErrorTime) < oneHour) {
  if (Math.random() > 0.3) {
    return null; // 70% 샘플링 (50% → 70%로 증가)
  }
}
```

**효과**:
- 중복 에러 제거
- 비용 절감
- 중요 에러 우선 수집

### 5. 효율성 개선

#### 데이터 길이 제한

```javascript
// 페이지 정보 길이 제한
log.data.page = window.location.pathname.substring(0, 100);
log.data.url = window.location.href.substring(0, 200);
log.data.referrer = (document.referrer || 'none').substring(0, 200);
```

**효과**:
- 이벤트 크기 감소
- 전송 비용 절감
- 성능 향상

#### 키 이름 단축

```javascript
// timestamp → ts (키 이름 단축)
log.data.ts = new Date().toISOString();

// navigationType → navType (키 이름 단축)
log.data.navType = window.performance.navigation.type;
```

**효과**:
- JSON 크기 감소
- 전송 비용 절감
- 메모리 사용량 감소

#### 로그 통계 선택적 전송

```javascript
// 중요 통계만 전송 (비용 절감)
shouldSend: function() {
  // warn 또는 error가 10개 이상일 때만 전송
  return this.warn >= 10 || this.error >= 5;
}
```

**효과**:
- 불필요한 메트릭 전송 방지
- 비용 절감
- 중요 통계만 수집

## 보안 강화

### 1. 개인정보 보호

#### User-Agent 해시 처리

- 전체 User-Agent 전송 방지
- 해시 기반 식별자 사용
- GDPR 준수

#### 민감 정보 필터링

- API 키 패턴 자동 감지
- 토큰 패턴 자동 감지
- log.data에서도 민감 정보 제거

### 2. 데이터 최소화

#### 길이 제한

- URL: 200자
- Referrer: 200자
- 페이지 경로: 100자
- 에러 메시지: 200자
- 스택 트레이스: 1,000자

#### 불필요한 데이터 제거

- console.log breadcrumb 제외
- 개발 환경 데이터 제외
- 중복 컨텍스트 정보 제거

## 효율성 개선

### 1. 메모리 최적화

#### localStorage 캐싱

- 최대 20개 항목 캐시
- 오래된 항목 자동 제거
- 메모리 사용량 최적화

#### 키 이름 단축

- `sentry_log_count_` → `sl_`
- `sentry_error_count_` → `se_`
- `timestamp` → `ts`

### 2. 성능 최적화

#### 배치 처리

- localStorage 접근 최소화
- 캐시 활용
- 에러 처리 강화

#### 코드 최적화

- 중복 코드 제거
- 헬퍼 함수 통합
- 일관된 로직 적용

## 비용 최적화

### 최적화 전후 비교

| 항목 | 최적화 전 | 최적화 후 | 개선율 |
|------|-----------|-----------|--------|
| **Breadcrumbs** | 100개 | 50개 | 50% 감소 |
| **이벤트 크기** | 8KB | 6KB | 25% 감소 |
| **로그 샘플링** | 70% | 80% | 10%p 증가 |
| **에러 샘플링** | 50% | 70% | 20%p 증가 |
| **동적 샘플링** | 50% (80% 사용 시) | 30% (90% 사용 시) | 더 공격적 |
| **localStorage 키** | 긴 이름 | 짧은 이름 | 메모리 절약 |

### 예상 비용 절감

- **월간 이벤트 수**: 약 20-30% 감소 예상
- **이벤트 크기**: 약 25% 감소
- **전송 비용**: 약 30-40% 절감 예상

## 모니터링 및 검증

### 1. 이벤트 수 모니터링

```javascript
// localStorage에서 월간 이벤트 수 확인
const tracker = monthlyEventTracker.get();
console.log('Monthly events:', tracker.count, '/ 5000');
```

### 2. Sentry 대시보드 확인

1. **Settings** → **Usage** 이동
2. **Monthly Events** 확인
3. **Quota** 확인

### 3. 검증 체크리스트

- [ ] 월간 이벤트 수가 5,000개 이하인지 확인
- [ ] 이벤트 크기가 6KB 이하인지 확인
- [ ] Breadcrumbs가 50개 이하인지 확인
- [ ] 민감 정보가 필터링되는지 확인
- [ ] User-Agent가 해시 처리되는지 확인
- [ ] localStorage 사용량이 최적화되었는지 확인

## 문제 해결

### 이벤트 수가 여전히 많은 경우

1. **샘플링 비율 조정**: 더 공격적인 샘플링 적용
2. **필터링 강화**: 불필요한 로그 제거
3. **Breadcrumbs 감소**: 50개 → 30개로 감소

### 메모리 사용량이 높은 경우

1. **캐시 크기 조정**: 20개 → 10개로 감소
2. **키 이름 단축**: 더 짧은 키 이름 사용
3. **불필요한 데이터 제거**: 컨텍스트 정보 최소화

### 보안 문제가 발생한 경우

1. **민감 정보 필터링 확인**: 패턴 추가
2. **User-Agent 해시 확인**: 해시 함수 검증
3. **로그 검토**: 민감 정보 포함 여부 확인

## 참고 자료

- [Sentry Free 티어 제한](https://sentry.io/pricing/)
- [Sentry 데이터 최소화](https://docs.sentry.io/platforms/javascript/data-management/)
- [Sentry 샘플링](https://docs.sentry.io/platforms/javascript/configuration/sampling/)
- [GDPR 준수](https://docs.sentry.io/product/security/data-security/)

## 업데이트 이력

- **2026-01-11**: 초기 문서 작성, 프리티어 최적화 적용
- **2026-01-11**: localStorage 최적화, 보안 강화
- **2026-01-11**: 비용 최적화 강화, 효율성 개선
