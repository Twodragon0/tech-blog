# Blog Video Generator with Remotion

Remotion을 사용하여 블로그 포스팅을 동적 영상으로 변환하는 프로젝트입니다.

## 빠른 시작

```bash
# 의존성 설치
npm install

# 개발 모드 (Remotion Studio)
npm run dev

# 영상 렌더링
npm run render
```

## 사용 방법

자세한 내용은 `../scripts/README_REMOTION.md`를 참조하세요.

## 프로젝트 구조

- `src/Root.tsx`: Remotion 루트 컴포넌트
- `src/BlogVideo.tsx`: 블로그 영상 컴포넌트
- `public/`: 정적 파일 (오디오, 이미지)

## 참고

이 프로젝트는 `scripts/generate_video_with_remotion.py`에서 자동으로 사용됩니다.
