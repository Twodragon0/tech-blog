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

### 설정 방법
1. [Sentry](https://sentry.io) 계정 생성
2. 프로젝트 생성 후 DSN 복사
3. Vercel 환경 변수에 `SENTRY_DSN` 추가
4. `_includes/sentry.html`에서 DSN 설정

### 보안
- DSN은 환경 변수로 관리
- 민감 정보 자동 필터링
- 10% 샘플링으로 비용 최적화

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
