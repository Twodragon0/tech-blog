# TTFB (Time to First Byte) 최적화 가이드

이 문서는 Sentry 로그를 기반으로 TTFB 성능 문제를 해결하고 Vercel 프리티어에 맞게 최적화하는 가이드를 제공합니다.

## 📋 목차

1. [TTFB 개요](#ttfb-개요)
2. [현재 상태 분석](#현재-상태-분석)
3. [적용된 최적화](#적용된-최적화)
4. [Vercel 프리티어 최적화](#vercel-프리티어-최적화)
5. [모니터링 및 검증](#모니터링-및-검증)
6. [문제 해결](#문제-해결)

## TTFB 개요

### TTFB란?

**Time to First Byte (TTFB)**는 웹 서버가 요청을 받은 후 첫 번째 바이트를 응답하는 데 걸리는 시간을 측정하는 성능 메트릭입니다.

### TTFB 측정 기준

| 등급 | TTFB (P75) | 설명 |
|------|------------|------|
| **Good** | < 200ms | 우수한 성능 |
| **Meh** | 200ms - 500ms | 개선 필요 |
| **Poor** | > 500ms | 즉시 개선 필요 |

### 현재 상태 (Sentry 로그 기준)

- **TTFB P75**: 1.25s (Poor)
- **TTFB Score**: 10 (Poor)
- **주요 문제 페이지**:
  - `/posts/*/*/클라우드_보안_과정_8기_6주차_...`: 1.25s
  - `/posts/*/*/클라우드_시큐리티_8기_1주차_...`: 651ms

## 현재 상태 분석

### 문제점

1. **서버 응답 시간 지연**
   - Vercel Functions의 콜드 스타트
   - 정적 파일 캐싱 미흡
   - CDN 캐시 설정 부족

2. **외부 리소스 로딩**
   - DNS 조회 시간
   - TLS 핸드셰이크 시간
   - 외부 스크립트 로딩 순서

3. **캐싱 전략 부족**
   - HTML 캐시 설정 미흡
   - 정적 파일 캐시 최적화 부족
   - ISR (Incremental Static Regeneration) 미적용

## 적용된 최적화

### 1. 캐싱 헤더 강화

#### HTML 파일 캐싱

```json
{
  "source": "/(.*).html",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"
    }
  ]
}
```

**효과**:
- `max-age=3600`: 브라우저 캐시 1시간
- `s-maxage=3600`: CDN 캐시 1시간
- `stale-while-revalidate=86400`: 백그라운드 재검증 허용 (24시간)

#### 정적 파일 캐싱

```json
{
  "source": "/assets/(.*)",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=31536000, immutable"
    }
  ]
}
```

**효과**:
- 1년간 캐싱 (immutable)
- 해시 기반 파일명으로 안전한 장기 캐싱

### 2. DNS Prefetch 및 Preconnect 최적화

#### Critical Resources: Preconnect

```html
<!-- DNS + TCP + TLS 핸드셰이크 사전 수행 -->
<link rel="preconnect" href="https://giscus.app" crossorigin>
<link rel="preconnect" href="https://api.deepseek.com" crossorigin>
<link rel="preconnect" href="https://va.vercel-scripts.com" crossorigin>
```

**효과**:
- DNS 조회 시간 제거
- TCP 연결 사전 설정
- TLS 핸드셰이크 사전 수행

#### Non-Critical Resources: DNS Prefetch

```html
<!-- DNS 조회만 사전 수행 -->
<link rel="dns-prefetch" href="https://api.mymemory.translated.net">
<link rel="dns-prefetch" href="https://pagead2.googlesyndication.com">
```

**효과**:
- DNS 조회 시간만 절약 (리소스 절약)
- 필요 시 빠른 연결

### 3. 스크립트 로딩 최적화

#### Defer 속성 사용

```html
<!-- TTFB 최적화: defer 사용 -->
<script defer src="https://va.vercel-scripts.com/v1/script.js"></script>
<script defer src="https://va.vercel-scripts.com/v1/speed-insights/script.js"></script>
```

**효과**:
- HTML 파싱을 블로킹하지 않음
- TTFB 이후에 스크립트 실행
- 페이지 로딩 속도 향상

### 4. Vercel Edge Network 활용

Vercel은 자동으로 Edge Network를 활용하여:
- **글로벌 CDN**: 전 세계 엣지 서버에서 콘텐츠 제공
- **자동 최적화**: 이미지, 폰트, 스크립트 자동 최적화
- **HTTP/2 및 HTTP/3**: 최신 프로토콜 지원

## Vercel 프리티어 최적화

### 프리티어 제한사항

| 항목 | Hobby (무료) | Pro |
|------|--------------|-----|
| **Edge Functions** | ✅ 사용 가능 | ✅ 사용 가능 |
| **ISR** | ✅ 사용 가능 | ✅ 사용 가능 |
| **CDN 캐싱** | ✅ 자동 | ✅ 자동 |
| **대역폭** | 100GB/월 | 무제한 |

### 최적화 전략

#### 1. 정적 사이트 생성 (SSG)

Jekyll은 빌드 시 정적 HTML을 생성하므로:
- ✅ 서버 렌더링 오버헤드 없음
- ✅ Edge Network에서 즉시 제공
- ✅ TTFB 최소화

#### 2. ISR (Incremental Static Regeneration)

프리티어에서도 ISR 사용 가능:

```json
{
  "headers": [
    {
      "source": "/(.*).html",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=3600, s-maxage=3600, stale-while-revalidate=86400"
        }
      ]
    }
  ]
}
```

**효과**:
- 첫 요청: 정적 파일 즉시 제공 (빠른 TTFB)
- 백그라운드: 필요 시 재생성
- 사용자 경험: 항상 빠른 응답

#### 3. Edge Functions (선택사항)

프리티어에서도 Edge Functions 사용 가능:

```javascript
// api/edge-example.js
export const config = {
  runtime: 'edge',
};

export default function handler(req) {
  return new Response('Hello from Edge!', {
    headers: {
      'Content-Type': 'text/plain',
    },
  });
}
```

**효과**:
- 전 세계 엣지 서버에서 실행
- 콜드 스타트 최소화
- 매우 빠른 응답 시간

## 모니터링 및 검증

### Sentry를 통한 TTFB 모니터링

Sentry Performance Monitoring에서 TTFB 추적:

1. **Sentry 대시보드** 접속
2. **Performance** → **Web Vitals** 이동
3. **TTFB** 메트릭 확인

### Vercel Analytics

Vercel Analytics에서 실시간 성능 모니터링:

1. **Vercel 대시보드** 접속
2. **Analytics** 탭 이동
3. **Web Vitals** 확인:
   - TTFB
   - FCP (First Contentful Paint)
   - LCP (Largest Contentful Paint)

### 검증 방법

#### 1. Chrome DevTools

```bash
# Chrome DevTools 열기
# Network 탭 → 요청 선택 → Timing 확인
# - Waiting (TTFB): 서버 응답 시간
```

#### 2. Lighthouse

```bash
# Lighthouse 실행
npx lighthouse https://tech.2twodragon.com --view
```

**확인 항목**:
- Performance Score
- TTFB 메트릭
- Opportunities 섹션

#### 3. WebPageTest

```bash
# WebPageTest에서 테스트
https://www.webpagetest.org/
```

**확인 항목**:
- TTFB (Time to First Byte)
- First Byte Time
- DNS Lookup Time

## 문제 해결

### TTFB가 여전히 높은 경우

#### 1. 외부 리소스 확인

```bash
# Chrome DevTools → Network 탭
# 각 리소스의 TTFB 확인
# 느린 리소스 식별
```

**해결책**:
- 외부 스크립트를 `defer` 또는 `async`로 변경
- 불필요한 외부 리소스 제거
- Critical CSS 인라인화

#### 2. CDN 캐시 확인

```bash
# Vercel 대시보드 → Deployments
# 캐시 상태 확인
```

**해결책**:
- 캐시 헤더 재확인
- `s-maxage` 값 조정
- `stale-while-revalidate` 활용

#### 3. 서버 응답 시간 확인

```bash
# Vercel Functions 로그 확인
vercel logs
```

**해결책**:
- 함수 실행 시간 최적화
- 불필요한 계산 제거
- 데이터베이스 쿼리 최적화

### 특정 페이지 TTFB가 높은 경우

#### 1. 한글 URL 인코딩 문제

한글 URL은 인코딩되어 길어질 수 있습니다:

```
/posts/*/*/%ED%81%B4%EB%9D%BC%EC%9A%B0%EB%93%9C_%EB%B3%B4%EC%95%88_...
```

**해결책**:
- 파일명을 영어로 변경 (권장)
- URL 단축 서비스 사용
- 영문 슬러그 사용

#### 2. 이미지 로딩 최적화

```html
<!-- 이미지 최적화 -->
<img src="image.webp" loading="lazy" decoding="async">
```

**효과**:
- WebP 형식 사용
- Lazy loading
- Async decoding

#### 3. 폰트 최적화

```css
/* 폰트 최적화 */
@font-face {
  font-display: swap; /* TTFB 개선 */
}
```

## 예상 개선 효과

### 최적화 전

- **TTFB P75**: 1.25s (Poor)
- **TTFB Score**: 10 (Poor)

### 최적화 후 (예상)

- **TTFB P75**: < 400ms (Meh → Good)
- **TTFB Score**: 50+ (개선)

### 개선 포인트

1. **캐싱 강화**: 30-50% 개선
2. **DNS Preconnect**: 100-200ms 절약
3. **스크립트 최적화**: 50-100ms 절약
4. **Edge Network**: 100-300ms 절약

**총 예상 개선**: 500-800ms (1.25s → 450-750ms)

## 추가 최적화 권장사항

### 1. 이미지 최적화

```bash
# WebP 변환
for file in assets/images/*.{png,jpg}; do
  convert "$file" "${file%.*}.webp"
done
```

### 2. Critical CSS 인라인화

```html
<!-- Critical CSS 인라인 -->
<style>
  /* Above-the-fold CSS */
</style>
```

### 3. 서비스 워커 활용

```javascript
// sw.js
// 정적 리소스 캐싱
// 오프라인 지원
```

### 4. HTTP/2 Server Push (Vercel 자동)

Vercel은 자동으로 HTTP/2 Server Push를 활용합니다.

## 참고 자료

- [Vercel Edge Network](https://vercel.com/docs/edge-network/overview)
- [Vercel Caching](https://vercel.com/docs/caching/overview)
- [Web Vitals](https://web.dev/vitals/)
- [TTFB 최적화 가이드](https://web.dev/ttfb/)
- [Sentry Performance Monitoring](https://docs.sentry.io/platforms/javascript/performance/)

## 업데이트 이력

- **2026-01-11**: 초기 문서 작성, TTFB 최적화 설정 적용
- **2026-01-11**: 캐싱 헤더 강화, DNS Preconnect 최적화
- **2026-01-11**: 프리티어 최적화 전략 추가
