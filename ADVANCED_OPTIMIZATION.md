# 고급 최적화 가이드

## 1. 이미지 최적화 (WebP)

### 구현 내용
- 자동 WebP 형식 감지 및 변환
- Fallback 지원 (WebP 미지원 브라우저)
- Lazy loading 이미지와 통합

### 사용 방법
1. 이미지 파일을 WebP 형식으로 변환하여 같은 디렉토리에 저장
2. 예: `image.png` → `image.webp` 생성
3. JavaScript가 자동으로 WebP를 우선 사용

### WebP 변환 스크립트 예시
```bash
# ImageMagick 사용
for file in assets/images/*.{png,jpg,jpeg}; do
  convert "$file" "${file%.*}.webp"
done
```

## 2. 폰트 최적화

### 현재 상태
- 시스템 폰트 사용 (preload 불필요)
- 향후 커스텀 폰트 추가 시 최적화 구조 준비됨

### 커스텀 폰트 추가 시
1. `font-optimizer.html`에서 주석 해제
2. `font-display: swap` 사용
3. `unicode-range`로 subset 지정
4. WOFF2 형식 우선 사용

## 3. Sentry 통합

### 플랫폼 선택
- **플랫폼**: JavaScript (Browser)
- **프레임워크**: Vanilla JavaScript (Jekyll 정적 사이트)

### 설정 방법

#### 1. Sentry 계정 및 프로젝트 생성
1. [Sentry.io](https://sentry.io) 접속 및 계정 생성
2. **Create Project** 클릭
3. **Platform 선택**: `JavaScript` → `Browser` 선택
4. 프로젝트 이름 입력 (예: `tech-blog`)
5. DSN (Data Source Name) 복사

#### 2. Vercel 환경 변수 설정
```bash
# Vercel CLI 사용
vercel env add SENTRY_DSN production
vercel env add SENTRY_DSN preview
vercel env add SENTRY_DSN development

# 또는 Vercel 대시보드에서:
# Settings → Environment Variables → SENTRY_DSN 추가
```

#### 3. Sentry SDK 추가
`_includes/sentry.html` 파일에서 Sentry SDK를 로드합니다:

```html
<!-- Sentry SDK (최신 버전) -->
<script src="https://browser.sentry-cdn.com/7.xx.x/bundle.min.js" 
        integrity="sha384-..." 
        crossorigin="anonymous"></script>
```

#### 4. DSN 설정
`_includes/sentry.html`에서 환경 변수 또는 직접 DSN 설정:

```javascript
const SENTRY_DSN = 'https://xxxxx@xxxxx.ingest.sentry.io/xxxxx';
```

### 보안
- DSN은 환경 변수로 관리 (프로덕션)
- 민감 정보 자동 필터링 (쿠키, 토큰, 키 등)
- CSP 위반 등 정상적인 보안 에러는 무시
- URL에서 민감한 쿼리 파라미터 자동 제거

### 비용 최적화
- 성능 모니터링: 10% 샘플링
- 에러 수집: 100% (필요시 조정)
- 세션 리플레이: 비활성화 (0%)
- 에러 리플레이: 비활성화 (0%)

### Sentry 프로젝트 설정 예시
```
Platform: JavaScript
Framework: Browser
Project Name: tech-blog
Organization: your-org
DSN: https://xxxxx@xxxxx.ingest.sentry.io/xxxxx
```

### 통합 확인
1. 브라우저 콘솔에서 `window.Sentry` 확인
2. 의도적으로 에러 발생시켜 Sentry로 전송되는지 확인
3. Sentry 대시보드에서 이벤트 수신 확인

## 4. 서비스 워커 (오프라인 지원)

### 기능
- 정적 리소스 캐싱
- 오프라인 지원
- 네트워크 우선, 캐시 fallback 전략

### 캐시 전략
- **정적 리소스**: 설치 시 캐시
- **동적 콘텐츠**: 네트워크 우선, 실패 시 캐시
- **API**: 캐싱 없음

### 업데이트
- 새 버전 배포 시 자동 업데이트
- 오래된 캐시 자동 삭제

## 배포 체크리스트

- [ ] WebP 이미지 변환 및 업로드
- [ ] Sentry DSN 설정 (선택사항)
- [ ] 서비스 워커 테스트
- [ ] 오프라인 모드 테스트
- [ ] 성능 측정 (Lighthouse)
