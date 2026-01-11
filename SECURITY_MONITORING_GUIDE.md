# 보안 모니터링 가이드

이 문서는 Vercel Firewall 보안 기능의 테스트, 모니터링, 로그 분석 가이드를 제공합니다.

## 📋 목차

1. [배포 후 테스트](#배포-후-테스트)
2. [Vercel Analytics 모니터링](#vercel-analytics-모니터링)
3. [Sentry 보안 이벤트 모니터링](#sentry-보안-이벤트-모니터링)
4. [정기 모니터링 체크리스트](#정기-모니터링-체크리스트)

## 배포 후 테스트

### 자동 테스트 스크립트

보안 기능을 자동으로 테스트하는 스크립트를 실행합니다:

```bash
# 테스트 스크립트 실행
chmod +x scripts/test-security.sh
./scripts/test-security.sh
```

또는 API URL 지정:

```bash
API_URL=https://tech.2twodragon.com/api/chat ./scripts/test-security.sh
```

### 테스트 항목

스크립트는 다음 항목을 자동으로 테스트합니다:

1. **정상 요청 테스트**
   - 정상적인 POST 요청이 200 응답을 반환하는지 확인

2. **Rate Limiting 테스트**
   - 15개의 연속 요청 후 16번째 요청이 429 (Too Many Requests)를 반환하는지 확인
   - Rate Limit 헤더 (`X-RateLimit-Limit`, `X-RateLimit-Remaining`) 확인

3. **Bot 보호 테스트**
   - Bot User-Agent (curl, wget 등)로 요청 시 403 (Forbidden) 반환 확인
   - 빈 User-Agent로 요청 시 차단 확인

4. **CORS 정책 테스트**
   - 허용되지 않은 Origin으로 요청 시 403 반환 확인

5. **입력 검증 테스트**
   - XSS 패턴 (`<script>`, `javascript:`) 차단 확인
   - 빈 메시지 거부 확인
   - 메시지 길이 초과 거부 확인

6. **요청 크기 제한 테스트**
   - 100KB 초과 요청 시 413 (Payload Too Large) 반환 확인

7. **보안 헤더 확인**
   - Rate Limit 헤더 존재 확인
   - Request ID 헤더 존재 확인

### 수동 테스트

#### Rate Limiting 테스트

```bash
# 15개의 연속 요청 전송
for i in {1..16}; do
  curl -X POST https://tech.2twodragon.com/api/chat \
    -H "Content-Type: application/json" \
    -H "Origin: https://tech.2twodragon.com" \
    -H "User-Agent: Mozilla/5.0" \
    -d "{\"message\":\"테스트 $i\",\"sessionId\":\"test-session\"}"
  echo ""
  sleep 0.1
done
```

**예상 결과**:
- 1-15번째 요청: HTTP 200
- 16번째 요청: HTTP 429 (Rate Limit 초과)

#### Bot 보호 테스트

```bash
# Bot User-Agent로 요청
curl -X POST https://tech.2twodragon.com/api/chat \
  -H "Content-Type: application/json" \
  -H "Origin: https://tech.2twodragon.com" \
  -H "User-Agent: curl/7.68.0" \
  -d '{"message":"테스트","sessionId":"bot-test"}'
```

**예상 결과**: HTTP 403 (Forbidden)

#### XSS 차단 테스트

```bash
# XSS 패턴 포함 메시지
curl -X POST https://tech.2twodragon.com/api/chat \
  -H "Content-Type: application/json" \
  -H "Origin: https://tech.2twodragon.com" \
  -H "User-Agent: Mozilla/5.0" \
  -d '{"message":"<script>alert(1)</script>","sessionId":"xss-test"}'
```

**예상 결과**: HTTP 400 (Bad Request)

## Vercel Analytics 모니터링

### 대시보드 접근

1. **Vercel 대시보드** 접속: https://vercel.com/dashboard
2. 프로젝트 선택
3. **Analytics** 탭 이동

### 주요 메트릭

#### 1. Functions 메트릭

**확인 항목**:
- **호출 수**: `/api/chat` 엔드포인트 호출 수
- **평균 실행 시간**: 함수 실행 시간 추이
- **에러율**: 4xx, 5xx 에러 비율
- **비용**: 함수 실행 비용 (Pro 플랜 이상)

**정상 범위**:
- 호출 수: 일일 100-1000회 (트래픽에 따라 다름)
- 평균 실행 시간: 2-5초 (DeepSeek API 응답 시간에 따라 다름)
- 에러율: < 5%

#### 2. Web Vitals

**확인 항목**:
- **TTFB** (Time to First Byte): < 200ms (Good)
- **FCP** (First Contentful Paint): < 1.8s (Good)
- **LCP** (Largest Contentful Paint): < 2.5s (Good)
- **CLS** (Cumulative Layout Shift): < 0.1 (Good)

#### 3. 실시간 로그

**명령어**:
```bash
# 실시간 로그 확인
vercel logs --follow

# 특정 기간 로그 확인
vercel logs --since 1h

# Rate Limit 이벤트 필터링
vercel logs | grep -i "rate limit"

# Bot 차단 이벤트 필터링
vercel logs | grep -i "bot blocked"
```

**확인 항목**:
- Rate Limit 초과 이벤트
- Bot 차단 이벤트
- 보안 관련 경고 로그
- 에러 로그

### 알림 설정

1. **Vercel 대시보드** → **Settings** → **Notifications**
2. 다음 알림 활성화:
   - ✅ **Function Errors**: 함수 에러 발생 시 알림
   - ✅ **Deployment Failures**: 배포 실패 시 알림
   - ✅ **Build Failures**: 빌드 실패 시 알림

## Sentry 보안 이벤트 모니터링

### 대시보드 접근

1. **Sentry 대시보드** 접속: https://sentry.io
2. 프로젝트 선택: `tech-blog`
3. **Issues** 탭 이동

### 보안 이벤트 필터링

#### 1. 보안 태그로 필터링

**필터 조건**:
```
tags.security = true
```

**또는**:
```
tags.errorType = rate_limit_exceeded
tags.errorType = bot_blocked
tags.errorType = xss_attempt
```

#### 2. 보안 이벤트 유형

| 이벤트 유형 | 태그 | 설명 |
|------------|------|------|
| **Rate Limit 초과** | `errorType: rate_limit_exceeded` | Rate Limit 초과 시도 |
| **Bot 차단** | `errorType: bot_blocked` | Bot User-Agent 차단 |
| **XSS 시도** | `errorType: xss_attempt` | XSS 패턴 감지 |
| **CORS 위반** | `errorType: cors_violation` | 허용되지 않은 Origin |

#### 3. Performance 모니터링

**경로**: **Performance** → **Transactions**

**확인 항목**:
- `/api/chat` 엔드포인트 성능
- 평균 응답 시간
- 에러율
- P95, P99 응답 시간

**필터**:
```
transaction:/api/chat
```

#### 4. Logs 모니터링

**경로**: **Logs** → **Filters**

**필터 조건**:
- `level = warning`: 보안 경고 로그
- `level = error`: 보안 에러 로그
- `message contains "Security"`: 보안 관련 로그

### 알림 설정

1. **Sentry 대시보드** → **Settings** → **Alerts**
2. **New Alert Rule** 생성:

**조건 예시**:
```
When an issue matches:
  - tags.security = true
  - level = warning or error
Then send a notification to:
  - Email
  - Slack (선택사항)
```

**알림 빈도**:
- 즉시 알림: Critical 보안 이벤트
- 일일 요약: 일반 보안 이벤트

## 정기 모니터링 체크리스트

### 일일 모니터링

- [ ] **Vercel Analytics**: 함수 호출 수 확인
  - 정상 범위 내인지 확인
  - 급증한 경우 원인 분석

- [ ] **Rate Limit 이벤트**: 초과 이벤트 확인
  - `vercel logs | grep -i "rate limit"`
  - 비정상적인 패턴 확인

- [ ] **에러율**: 4xx, 5xx 에러 비율 확인
  - 정상 범위: < 5%
  - 높은 경우 원인 분석

### 주간 모니터링

- [ ] **Bot 차단 통계**: 차단된 봇 수 및 유형
  - `vercel logs | grep -i "bot blocked"`
  - 새로운 봇 패턴 확인

- [ ] **보안 이벤트 로그 분석**: Sentry에서 보안 이벤트 확인
  - XSS 시도 횟수
  - CORS 위반 횟수
  - Rate Limit 초과 패턴

- [ ] **API 비용 분석**: Vercel Analytics에서 비용 확인
  - 예상 비용 범위 내인지 확인
  - 비용 급증 시 원인 분석

### 월간 모니터링

- [ ] **보안 트렌드 분석**: 월간 보안 이벤트 통계
  - 공격 패턴 변화 확인
  - 새로운 위협 탐지

- [ ] **성능 개선**: API 응답 시간 및 에러율 개선
  - 목표: 평균 응답 시간 < 3초
  - 목표: 에러율 < 3%

- [ ] **비용 최적화**: API 호출 수 및 비용 최적화
  - 불필요한 호출 제거
  - 캐싱 전략 개선

## 문제 해결

### Rate Limiting이 작동하지 않는 경우

1. **로그 확인**:
   ```bash
   vercel logs | grep -i "rate limit"
   ```

2. **코드 확인**: `api/chat.js`의 `checkRateLimit` 함수 확인

3. **세션 ID 확인**: 동일한 세션 ID로 요청하는지 확인

### Bot 보호가 작동하지 않는 경우

1. **User-Agent 확인**: 요청 헤더에 User-Agent가 있는지 확인

2. **프로덕션 환경 확인**: `NODE_ENV === 'production'`인지 확인

3. **로그 확인**:
   ```bash
   vercel logs | grep -i "bot blocked"
   ```

### 보안 이벤트가 Sentry에 나타나지 않는 경우

1. **Sentry 설정 확인**: `_includes/sentry.html` 확인

2. **태그 확인**: 보안 이벤트에 올바른 태그가 있는지 확인

3. **필터 확인**: Sentry 대시보드 필터 설정 확인

## 참고 자료

- [Vercel Analytics 문서](https://vercel.com/docs/analytics)
- [Sentry 보안 모니터링](https://docs.sentry.io/product/security/)
- [프로젝트 보안 정책](./SECURITY.md)
- [Vercel Firewall 보안 가이드](./VERCEL_FIREWALL_SECURITY.md)

## 업데이트 이력

- **2026-01-11**: 초기 문서 작성, 테스트 및 모니터링 가이드 추가
- **2026-01-11**: 자동 테스트 스크립트 추가
- **2026-01-11**: Sentry 보안 이벤트 추적 설정
