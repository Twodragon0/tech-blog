# Vercel 보안 검문소 오류 해결 가이드

## 문제 상황

Vercel 보안 검문소에서 "브라우저를 확인하지 못했습니다" 오류(코드 705)가 발생하는 경우가 있습니다.

### 발생 경로
- `/certifications/aws-saa/` 등 certifications 페이지 접근 시 종종 발생
- `/posts/2025/12/...` 등 posts 페이지 접근 시 발생 (429, 705 에러)
- `/_vercel/speed-insights/vitals` 경로에서 429 (Too Many Requests) 에러 발생

### 오류 코드
- **705**: 브라우저 검증 실패
- **429**: Too Many Requests (Rate Limiting)

## 원인 분석

### 주요 원인
1. **X-Robots-Tag 헤더 충돌**: `X-Robots-Tag: noindex, nofollow` 헤더가 Vercel 보안 검문소의 브라우저 검증과 충돌
2. **엄격한 보안 헤더**: 일부 보안 헤더가 브라우저 검증 프로세스를 방해할 수 있음
3. **JavaScript 실행 환경**: 브라우저 검증을 위한 JavaScript 실행이 차단될 수 있음

## 해결 방법

### 1. vercel.json 설정 수정

#### `/certifications/` 경로 (완료)

`/certifications/` 경로에 대해서는 브라우저 검증에 방해가 되는 헤더를 제거했습니다:

```json
{
  "source": "/certifications/(.*)",
  "headers": [
    { "key": "X-Content-Type-Options", "value": "nosniff" },
    { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
    { "key": "X-XSS-Protection", "value": "1; mode=block" },
    { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
    { "key": "Permissions-Policy", "value": "geolocation=(), microphone=(), camera=()" },
    { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
    { "key": "X-DNS-Prefetch-Control", "value": "on" },
    { "key": "Cache-Control", "value": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400" }
  ]
}
```

**변경 사항**:
- ✅ `X-Robots-Tag` 헤더 제거 (브라우저 검증 충돌 방지)
- ✅ `X-Request-ID` 빈 값 제거
- ✅ 캐싱 헤더 추가 (성능 최적화)

#### `/posts/` 경로 (2026-01-11 추가)

`/posts/` 경로에서도 동일한 문제가 발생할 수 있으므로, 브라우저 검증에 방해가 되는 헤더를 최적화했습니다:

```json
{
  "source": "/posts/(.*)",
  "headers": [
    { "key": "X-Content-Type-Options", "value": "nosniff" },
    { "key": "X-Frame-Options", "value": "SAMEORIGIN" },
    { "key": "X-XSS-Protection", "value": "1; mode=block" },
    { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" },
    { "key": "Permissions-Policy", "value": "geolocation=(), microphone=(), camera=()" },
    { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
    { "key": "X-DNS-Prefetch-Control", "value": "on" },
    { "key": "Cache-Control", "value": "public, max-age=10800, s-maxage=10800, stale-while-revalidate=259200" }
  ]
}
```

**변경 사항**:
- ✅ 브라우저 검증에 필요한 헤더만 유지
- ✅ 캐싱 헤더 최적화 (3시간 캐시, stale-while-revalidate 적용)
- ✅ 보안 헤더는 유지하되 브라우저 검증을 방해하지 않도록 조정

### 2. Cloudflare 설정 확인 (Cloudflare 사용 시)

Cloudflare를 사용하는 경우, Rate Limiting 및 보안 설정을 확인하세요:

1. **Cloudflare 대시보드** 접속
2. **Security** → **WAF** 또는 **Rate Limiting** 이동
3. **Rate Limiting 규칙** 확인:
   - 임계값이 너무 낮게 설정되어 있는지 확인
   - 정상적인 사용자 트래픽이 차단되지 않도록 조정
4. **Security Level** 확인:
   - Medium 또는 Low로 설정 권장 (High는 너무 엄격할 수 있음)
5. **Bot Fight Mode** 확인:
   - 정상적인 크롤러가 차단되지 않도록 설정

### 3. Vercel 대시보드 확인

Vercel 대시보드에서 보안 검문소 설정을 확인하세요:

1. **Vercel 대시보드** 접속
2. **프로젝트** → **Settings** → **Security** 이동
3. **Firewall** 또는 **Security Checkpoint** 설정 확인
4. 필요시 보안 검문소 임계값 조정

### 4. 브라우저 측 해결 방법

사용자가 경험하는 경우 다음을 시도해보세요:

#### 방법 1: 쿠키 및 캐시 삭제
1. 브라우저 설정에서 쿠키 및 캐시 삭제
2. 사이트 재방문

#### 방법 2: 시크릿/프라이빗 모드 사용
1. 시크릿/프라이빗 모드로 사이트 접근
2. 브라우저 확장 프로그램 비활성화 후 재시도

#### 방법 3: JavaScript 활성화 확인
1. 브라우저에서 JavaScript가 활성화되어 있는지 확인
2. NoScript 등 JavaScript 차단 확장 프로그램 비활성화

#### 방법 4: VPN/프록시 비활성화
1. VPN 또는 프록시 사용 시 일시적으로 비활성화
2. 직접 연결로 재시도

## 추가 최적화 권장사항

### 1. 보안 헤더 최적화

공개 페이지에서는 `X-Robots-Tag` 헤더를 제거하는 것이 좋습니다:

```json
// ❌ 나쁜 예: 모든 페이지에 noindex 적용
{ "key": "X-Robots-Tag", "value": "noindex, nofollow" }

// ✅ 좋은 예: 특정 경로에만 적용 (예: /admin/)
{
  "source": "/admin/(.*)",
  "headers": [
    { "key": "X-Robots-Tag", "value": "noindex, nofollow" }
  ]
}
```

### 2. Vercel 보안 검문소 설정

Vercel Pro 플랜 이상에서는 보안 검문소 설정을 세밀하게 조정할 수 있습니다:

- **Bot Detection Sensitivity**: 봇 탐지 민감도 조정
- **Browser Verification**: 브라우저 검증 임계값 조정
- **Rate Limiting**: 요청 제한 설정

### 3. 모니터링

보안 검문소 오류를 모니터링하려면:

1. **Vercel Analytics**: 보안 검문소 차단 통계 확인
2. **Sentry**: 에러 로그 모니터링
3. **사용자 피드백**: 접근 문제 신고 수집

## 보안 고려사항

### 보안 헤더 제거 시 주의사항

`X-Robots-Tag` 헤더를 제거하면:
- ✅ 검색 엔진 크롤러가 페이지를 인덱싱할 수 있음
- ✅ SEO에 도움이 될 수 있음
- ⚠️ 민감한 페이지는 별도로 보호 필요

**권장 사항**:
- 공개 페이지: `X-Robots-Tag` 제거 (SEO 최적화)
- 관리자 페이지: `X-Robots-Tag: noindex, nofollow` 유지
- API 엔드포인트: 적절한 인증 및 권한 제어

## 문제 해결 체크리스트

### 배포 전 확인
- [ ] `vercel.json` 설정이 올바르게 적용되었는지 확인
- [ ] `/certifications/` 경로 헤더 설정 확인
- [ ] `/posts/` 경로 헤더 설정 확인
- [ ] Vercel 대시보드에서 보안 설정 확인
- [ ] Cloudflare 설정 확인 (사용 시)

### 배포 후 확인
- [ ] `/certifications/aws-saa/` 접근 테스트
- [ ] `/posts/2025/12/...` 경로 접근 테스트
- [ ] 브라우저 개발자 도구에서 응답 헤더 확인
- [ ] 429, 705 에러가 발생하지 않는지 확인
- [ ] 다양한 브라우저에서 테스트 (Chrome, Firefox, Safari, Edge)
- [ ] 모바일 브라우저에서도 테스트

### 지속적인 모니터링
- [ ] Vercel Analytics에서 보안 검문소 차단 통계 확인
- [ ] 사용자 피드백 수집
- [ ] 에러 로그 모니터링

## 참고 자료

- [Vercel Security Checkpoint 문서](https://vercel.com/docs/security/security-checkpoint)
- [Vercel Firewall 설정](https://vercel.com/docs/security/firewall)
- [HTTP 보안 헤더 가이드](https://owasp.org/www-project-secure-headers/)
- [프로젝트 보안 정책](./SECURITY.md)

## Vercel Speed Insights 429 에러 해결

### 문제
`/_vercel/speed-insights/vitals` 경로에서 429 (Too Many Requests) 에러가 발생합니다.

### 원인
- Vercel Speed Insights의 Rate Limiting
- 너무 많은 페이지뷰로 인한 요청 제한 초과
- 동시 요청 수 제한

### 해결 방법

#### 1. 에러 핸들링 추가 (완료)

`_includes/footer.html`에 에러 핸들링을 추가했습니다:

```javascript
// Speed Insights 스크립트 로드 (에러 핸들링 포함)
var speedInsightsScript = document.createElement('script');
speedInsightsScript.defer = true;
speedInsightsScript.src = 'https://va.vercel-scripts.com/v1/speed-insights/script.js';
speedInsightsScript.onerror = function() {
  // Speed Insights 로드 실패는 조용히 처리 (429 Rate Limiting 등)
};
```

**효과**:
- 429 에러 발생 시 콘솔 에러 방지
- 사용자 경험 개선
- Speed Insights는 선택적 기능이므로 실패해도 사이트 기능에 영향 없음

#### 2. 프로덕션에서만 활성화

개발 환경에서는 Speed Insights를 로드하지 않도록 설정:

```javascript
// 프로덕션 환경에서만 로드
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
  return; // 개발 환경에서는 로드하지 않음
}
```

#### 3. Vercel 대시보드 확인

Vercel 대시보드에서 Speed Insights 설정 확인:

1. **Vercel 대시보드** 접속
2. **프로젝트** → **Analytics** → **Speed Insights** 이동
3. Rate Limiting 설정 확인
4. 필요시 Vercel Pro 플랜 업그레이드 고려

### 참고사항

- Speed Insights는 선택적 기능입니다
- 429 에러가 발생해도 사이트 기능에는 영향이 없습니다
- 에러 핸들링으로 콘솔 에러를 방지할 수 있습니다
- Vercel Pro 플랜에서는 더 높은 Rate Limit이 제공됩니다

## Vercel Attack Challenge Mode (429 에러) 해결

### 문제

사이트 전체에서 429 에러와 함께 `x-vercel-mitigated: challenge` 헤더가 반환됩니다.

### 원인

Vercel의 Attack Challenge Mode가 활성화되어 모든 요청에 브라우저 검증이 적용됩니다.

### 즉시 해결 방법 (Vercel Dashboard)

1. **Vercel 대시보드** 접속: https://vercel.com/dashboard
2. **프로젝트 선택** → **Settings** 이동
3. **Security** 탭 클릭
4. **Attack Challenge Mode** 확인:
   - 현재 상태가 `Enabled`인 경우 `Disabled`로 변경
   - 또는 **IP 기반 예외** 설정
5. **Firewall Rules** 확인:
   - 너무 엄격한 규칙이 있는지 확인
   - 필요시 규칙 완화 또는 제거

### 대안 해결 방법

Attack Challenge가 필요한 경우:

1. **특정 경로만 Challenge 적용**:
   ```
   Path: /api/*
   Action: Challenge
   ```

2. **특정 국가/IP 예외 설정**:
   - 한국(KR) IP 예외 처리
   - 관리자 IP 화이트리스트 추가

3. **Rate Limiting 대신 사용**:
   - Challenge를 비활성화하고 Rate Limiting만 적용

### 확인 방법

```bash
# HTTP 상태 코드 확인
curl -s -o /dev/null -w "%{http_code}" https://tech.2twodragon.com

# 응답 헤더 확인
curl -s -I https://tech.2twodragon.com | head -20
```

정상인 경우: `200`
문제인 경우: `429` + `x-vercel-mitigated: challenge`

## 업데이트 이력

- **2026-01-11**: 초기 문서 작성, `/certifications/` 경로 헤더 최적화 적용
- **2026-01-11**: `X-Robots-Tag` 헤더 제거로 브라우저 검증 충돌 해결
- **2026-01-11**: `/posts/` 경로 헤더 최적화 추가, Cloudflare 설정 가이드 추가
- **2026-01-11**: Vercel Speed Insights 429 에러 해결 방법 추가
- **2026-01-26**: Vercel Attack Challenge Mode 해결 방법 추가 (705 에러)
