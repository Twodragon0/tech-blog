# Vercel Firewall 보안 최적화 가이드

이 문서는 Vercel 프리티어에 맞춘 보안 최적화 및 비용 효율적인 방어 전략을 제공합니다.

## 📋 목차

1. [Vercel Firewall 개요](#vercel-firewall-개요)
2. [프리티어 보안 기능](#프리티어-보안-기능)
3. [적용된 보안 최적화](#적용된-보안-최적화)
4. [비용 효율적인 보안 전략](#비용-효율적인-보안-전략)
5. [모니터링 및 대응](#모니터링-및-대응)

## Vercel Firewall 개요

### 프리티어 제공 기능

Vercel 프리티어(Hobby 플랜)에서 제공하는 보안 기능:

- ✅ **DDoS 보호**: 자동 DDoS 완화 (모든 플랜)
- ✅ **IP 차단**: 커스텀 규칙을 통한 IP 차단
- ✅ **기본 보안 헤더**: 자동 보안 헤더 적용
- ✅ **HTTPS**: 자동 SSL/TLS 인증서
- ❌ **Rate Limiting**: Pro/Enterprise 플랜만 가능 (서버 측 구현 필요)

### Pro/Enterprise 전용 기능

- Rate Limiting (WAF)
- 고급 위협 탐지
- 커스텀 규칙 세트
- 실시간 보안 대시보드

## 프리티어 보안 기능

### 1. DDoS 보호

Vercel은 자동으로 DDoS 공격을 완화합니다:

- **Edge Network**: 전 세계 엣지 서버에서 공격 분산
- **자동 스케일링**: 트래픽 급증 시 자동 확장
- **Rate Limiting**: 기본적인 Rate Limiting 제공

**비용**: 무료 (프리티어 포함)

### 2. IP 차단

Vercel 대시보드에서 IP 차단 규칙 설정:

1. **Vercel 대시보드** 접속
2. **Security** → **Firewall** 이동
3. **Block IP** 규칙 추가

**제한사항**:
- 프리티어: 수동 IP 차단만 가능
- Pro/Enterprise: 자동 위협 탐지 및 차단

### 3. 보안 헤더

`vercel.json`을 통해 보안 헤더 설정:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" }
      ]
    }
  ]
}
```

## 적용된 보안 최적화

### 1. API 엔드포인트 보안 강화

#### Rate Limiting (서버 측 구현)

프리티어에서는 WAF Rate Limiting이 없으므로 서버 측에서 구현:

```javascript
// api/chat.js
const CONFIG = {
  RATE_LIMIT: {
    MAX_REQUESTS: 15, // 세션당 최대 요청 수
    WINDOW_MS: 60000, // 1분 윈도우
  }
};
```

**효과**:
- 비용 보호: API 호출 수 제한
- DDoS 완화: 과도한 요청 차단
- 프리티어 제한 내에서 작동

#### Bot 보호

User-Agent 검증을 통한 봇 차단:

```javascript
function isBotUserAgent(userAgent) {
  const botPatterns = [
    /bot/i, /crawler/i, /spider/i, /scraper/i,
    /curl/i, /wget/i, /python-requests/i
  ];
  // 허용된 브라우저 패턴 확인
  // ...
}
```

**효과**:
- 크롤러/봇 차단으로 비용 절감
- 불필요한 API 호출 방지
- 프리티어 제한 보호

#### 요청 크기 제한

```javascript
const contentLength = req.headers['content-length'];
if (contentLength && parseInt(contentLength) > 100000) { // 100KB
  return res.status(413).json({ error: '요청 크기가 너무 큽니다.' });
}
```

**효과**:
- 메모리 사용량 제한
- 비용 최적화
- DoS 공격 완화

### 2. CORS 정책 강화

```javascript
const allowedOrigins = [
  'https://tech.2twodragon.com',
  'https://www.tech.2twodragon.com'
];

// 프로덕션에서만 엄격한 Origin 검증
if (req.method === 'POST' && !isAllowedOrigin && process.env.NODE_ENV === 'production') {
  return res.status(403).json({ error: 'Forbidden: Invalid origin' });
}
```

**효과**:
- CSRF 공격 방지
- 무단 도메인 접근 차단
- 데이터 유출 방지

### 3. 입력 검증 강화

#### XSS 방지

```javascript
const dangerousPatterns = [
  /<script[^>]*>/i,
  /javascript:/i,
  /on\w+\s*=/i,
  /data:text\/html/i,
  /<iframe[^>]*>/i
];

for (const pattern of dangerousPatterns) {
  if (pattern.test(message)) {
    return res.status(400).json({ error: '유효하지 않은 메시지 형식입니다.' });
  }
}
```

**효과**:
- XSS 공격 방지
- 코드 인젝션 차단
- 사용자 데이터 보호

### 4. Rate Limit 헤더 추가

```javascript
res.setHeader('X-RateLimit-Limit', CONFIG.RATE_LIMIT.MAX_REQUESTS.toString());
res.setHeader('X-RateLimit-Remaining', remainingRequests.toString());
res.setHeader('X-RateLimit-Reset', resetTime.toString());
res.setHeader('Retry-After', '60');
```

**효과**:
- 클라이언트가 Rate Limit 상태를 알 수 있음
- 적절한 재시도 전략 수립 가능
- 사용자 경험 개선

### 5. Request ID 추적

```javascript
const requestId = generateRequestId();
res.setHeader('X-Request-ID', requestId);
```

**효과**:
- 보안 사고 추적
- 디버깅 용이
- 로그 분석 개선

## 비용 효율적인 보안 전략

### 1. 메모리 기반 Rate Limiter

프리티어에서는 Redis/KV 없이 메모리 기반 Rate Limiter 사용:

```javascript
const rateLimitStore = new Map();

// 메모리 정리: 오래된 레코드 자동 삭제
if (rateLimitStore.size > 1000) {
  for (const [k, v] of rateLimitStore.entries()) {
    if (v.resetAt < now) {
      rateLimitStore.delete(k);
    }
  }
}
```

**장점**:
- 추가 비용 없음
- 프리티어 제한 내에서 작동
- 간단한 구현

**단점**:
- 서버 재시작 시 초기화
- 다중 인스턴스 간 공유 불가

**프로덕션 권장**: Vercel KV 또는 Redis 사용

### 2. Bot 차단으로 비용 절감

```javascript
// 봇 차단으로 불필요한 API 호출 방지
if (isBotUserAgent(userAgent)) {
  return res.status(403).json({ error: 'Forbidden' });
}
```

**비용 절감 효과**:
- 크롤러 요청 차단: API 호출 수 감소
- 함수 실행 시간 절약: 비용 절감
- 대역폭 절약: 데이터 전송 비용 감소

### 3. 요청 크기 제한

```javascript
// 100KB 제한으로 메모리 사용량 제한
if (contentLength && parseInt(contentLength) > 100000) {
  return res.status(413).json({ error: '요청 크기가 너무 큽니다.' });
}
```

**비용 절감 효과**:
- 메모리 사용량 제한: 함수 비용 절감
- 처리 시간 단축: 실행 시간 비용 절감

### 4. 캐싱 전략

```json
{
  "source": "/posts/(.*)",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=10800, s-maxage=10800, stale-while-revalidate=259200"
    }
  ]
}
```

**비용 절감 효과**:
- 함수 호출 감소: 캐시된 응답 제공
- 대역폭 절약: CDN 캐시 활용
- 응답 시간 개선: 사용자 경험 향상

## 모니터링 및 대응

### 1. Vercel Analytics

Vercel 대시보드에서 모니터링:

1. **Analytics** → **Functions** 이동
2. 함수 실행 시간 및 호출 수 확인
3. 에러율 모니터링

### 2. Sentry 보안 모니터링

```javascript
// 보안 이벤트를 Sentry로 전송
if (pattern.test(message)) {
  Sentry.captureMessage('XSS attempt detected', {
    level: 'warning',
    tags: { security: 'xss_attempt' },
    extra: { requestId, userAgent }
  });
}
```

### 3. 로그 분석

```javascript
// 보안 관련 로그만 기록 (비용 최적화)
if (process.env.NODE_ENV === 'production') {
  // 프로덕션에서는 최소한의 로그만
  console.warn('[Security] Rate limit exceeded:', sessionKey);
}
```

### 4. 알림 설정

Vercel 대시보드에서 알림 설정:

1. **Settings** → **Notifications** 이동
2. **Function Errors** 알림 활성화
3. **Rate Limit Exceeded** 이벤트 모니터링

## 보안 체크리스트

### 배포 전 확인

- [ ] Rate Limiting 설정 확인
- [ ] CORS 정책 검증
- [ ] 입력 검증 로직 확인
- [ ] 보안 헤더 설정 확인
- [ ] Bot 보호 활성화 확인
- [ ] 요청 크기 제한 확인

### 정기 점검

- [ ] 주간: Rate Limit 통계 확인
- [ ] 월간: 보안 로그 분석
- [ ] 분기: 보안 헤더 업데이트
- [ ] 연간: 보안 정책 재검토

## 프리티어 제한 및 대응

### 제한사항

| 항목 | 프리티어 제한 | 대응 방안 |
|------|--------------|----------|
| **Rate Limiting** | WAF Rate Limiting 없음 | 서버 측 Rate Limiter 구현 |
| **IP 차단** | 수동만 가능 | vercel.json + 서버 측 검증 |
| **고급 위협 탐지** | 없음 | 기본 보안 헤더 + 입력 검증 |
| **실시간 대시보드** | 제한적 | Sentry + Vercel Analytics |

### 업그레이드 고려사항

Pro 플랜($20/월) 업그레이드 시:

- ✅ WAF Rate Limiting
- ✅ 고급 위협 탐지
- ✅ 커스텀 규칙 세트
- ✅ 실시간 보안 대시보드

**비용 대비 효과**:
- 트래픽이 많을 경우: Pro 플랜 권장
- 트래픽이 적을 경우: 프리티어 + 서버 측 구현으로 충분

## 참고 자료

- [Vercel Firewall 문서](https://vercel.com/docs/vercel-firewall)
- [Vercel 보안 가이드](https://vercel.com/docs/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [프로젝트 보안 정책](./SECURITY.md)

## 업데이트 이력

- **2026-01-11**: 초기 문서 작성, 프리티어 보안 최적화 적용
- **2026-01-11**: Rate Limiting, Bot 보호, 요청 크기 제한 추가
- **2026-01-11**: 비용 효율적인 보안 전략 문서화
