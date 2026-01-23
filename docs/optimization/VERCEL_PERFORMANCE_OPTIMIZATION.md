# Vercel 성능 최적화 가이드

이 문서는 Vercel 로그를 기반으로 한 성능 개선 가이드입니다.

## 📊 현재 성능 상태

### Needs Improvement (50-90 점수 범위) 페이지

| 경로 | 응답 시간 | 성능 점수 | 상태 |
|------|----------|----------|------|
| `/posts/2026/01/클라우드_보안_과정_8기_6주차_...` | 114ms | 74점 | 개선 필요 |
| `/posts/2026/01/DevSecOps가_바라보는_자동차_보안_...` | 74ms | 75점 | 개선 필요 |
| `/posts/2026/01/2026년_DevSecOps_로드맵_...` | 37ms | 89점 | 양호 |
| `/categories` | 19ms | 88점 | 양호 |
| `/posts/2026/01/Tesla_FSD_2026_...` | 15ms | 60점 | 개선 필요 |
| `/posts/2025/05/Kubernetes_Minikube_...` | 11ms | 88점 | 양호 |

### 주요 문제점

1. **긴 한글 URL**: URL 인코딩으로 인한 긴 경로 (114ms 응답)
2. **이미지 로딩**: 포스트 이미지 최적화 부족
3. **스크립트 로딩**: Analytics 스크립트가 head에 위치하여 TTFB 지연
4. **캐싱 전략**: 포스트 페이지 캐싱 시간 부족

## 적용된 최적화

### 1. 캐싱 전략 강화

#### vercel.json 캐싱 헤더 개선

```json
{
  "source": "/(.*).html",
  "headers": [
    {
      "key": "Cache-Control",
      "value": "public, max-age=7200, s-maxage=7200, stale-while-revalidate=172800"
    }
  ]
},
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

**개선 효과**:
- HTML 캐시: 1시간 → 2시간
- 포스트 페이지: 3시간 캐싱
- `stale-while-revalidate`: 백그라운드 재검증으로 사용자 경험 향상

### 2. 리소스 로딩 최적화

#### DNS Preconnect 추가

```html
<!-- Critical resources: preconnect (DNS + TCP + TLS) -->
<link rel="preconnect" href="https://js.sentry-cdn.com" crossorigin>
```

**효과**:
- Sentry 스크립트 로딩 시간 단축
- DNS 조회 + TCP 연결 + TLS 핸드셰이크 사전 수행

#### Analytics 스크립트 위치 변경

**Before**: `<head>` 내부
```html
<!-- head.html -->
<script defer src="https://va.vercel-scripts.com/v1/script.js"></script>
```

**After**: `<footer>` 내부
```html
<!-- footer.html -->
<script defer src="https://va.vercel-scripts.com/v1/script.js"></script>
```

**효과**:
- TTFB 개선: Analytics 스크립트가 초기 로딩을 블로킹하지 않음
- 페이지 렌더링 우선순위 향상

### 3. 이미지 최적화

#### 이미지 에러 핸들링

```html
<img 
  src="{{ image_path }}" 
  alt="{{ image_alt_text }}" 
  loading="eager" 
  decoding="async" 
  fetchpriority="high"
  onerror="this.style.display='none';"
>
```

**효과**:
- 이미지 로드 실패 시 레이아웃 깨짐 방지
- CLS (Cumulative Layout Shift) 개선

### 4. Critical CSS 인라인화

```html
{% if page.layout == 'post' %}
<style>
  /* Critical above-the-fold styles inline for faster rendering */
  .post-header { opacity: 0; animation: fadeIn 0.3s ease-in forwards; }
  @keyframes fadeIn { to { opacity: 1; } }
</style>
{% endif %}
```

**효과**:
- FCP (First Contentful Paint) 개선
- 초기 렌더링 블로킹 최소화

## 성능 개선 목표

### 현재 상태
- **평균 응답 시간**: 50-114ms
- **성능 점수**: 60-89점
- **목표 점수**: 90점 이상

### 개선 목표
- **응답 시간**: < 50ms (목표)
- **성능 점수**: 90점 이상
- **TTFB**: < 200ms
- **LCP**: < 2.5s
- **CLS**: < 0.1

## 모니터링

### Vercel Analytics

1. **Vercel 대시보드** 접속
2. **Analytics** 탭 이동
3. **Performance** 메트릭 확인:
   - TTFB (Time to First Byte)
   - FCP (First Contentful Paint)
   - LCP (Largest Contentful Paint)
   - CLS (Cumulative Layout Shift)

### Sentry Performance Monitoring

1. **Sentry 대시보드** 접속
2. **Performance** → **Web Vitals** 이동
3. 페이지별 성능 메트릭 확인

### 주요 모니터링 항목

- **응답 시간**: 각 페이지별 평균 응답 시간
- **성능 점수**: Lighthouse 성능 점수
- **에러율**: 페이지 로드 실패율
- **캐시 히트율**: CDN 캐시 효율성

## 추가 최적화 권장사항

### 1. 이미지 포맷 최적화

```bash
# WebP 변환 스크립트
for file in assets/images/*.{png,jpg}; do
  convert "$file" "${file%.*}.webp"
done
```

**효과**:
- 이미지 크기 30-50% 감소
- 로딩 시간 단축

### 2. 한글 URL 최적화

**문제**: 한글 URL 인코딩으로 인한 긴 경로

**해결책**:
- 파일명을 영어로 변경 (권장)
- 영문 슬러그 사용
- URL 단축 서비스 활용

### 3. 서비스 워커 활용

```javascript
// sw.js
// 정적 리소스 캐싱
// 오프라인 지원
```

**효과**:
- 재방문 시 즉시 로딩
- 오프라인 지원

### 4. 리소스 우선순위 조정

```html
<!-- Critical resources -->
<link rel="preload" href="..." as="style" fetchpriority="high">

<!-- Non-critical resources -->
<link rel="prefetch" href="..." as="script">
```

## 문제 해결

### 성능 점수가 여전히 낮은 경우

1. **캐시 확인**: Vercel 대시보드에서 캐시 상태 확인
2. **리소스 크기**: 이미지 및 스크립트 크기 확인
3. **외부 리소스**: 외부 스크립트 로딩 시간 확인
4. **서버 응답**: Vercel Functions 응답 시간 확인

### 특정 페이지가 느린 경우

1. **이미지 최적화**: WebP 변환 및 lazy loading
2. **스크립트 최적화**: defer/async 속성 확인
3. **캐싱 확인**: 해당 페이지 캐시 설정 확인
4. **외부 리소스**: Giscus, Analytics 등 로딩 시간 확인

## 참고 자료

- [Vercel Performance Optimization](https://vercel.com/docs/analytics)
- [Web Vitals](https://web.dev/vitals/)
- [TTFB 최적화 가이드](https://web.dev/ttfb/)
- [Image Optimization](https://web.dev/fast/#optimize-your-images)

## 업데이트 이력

- **2026-01-11**: 초기 문서 작성, Vercel 로그 기반 성능 분석
- **2026-01-11**: 캐싱 전략 강화, Analytics 스크립트 위치 변경
- **2026-01-11**: 이미지 최적화, Critical CSS 인라인화 추가
