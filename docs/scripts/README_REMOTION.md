# Remotion 영상 생성 가이드

Remotion을 사용하여 더 동적이고 전문적인 영상을 생성할 수 있습니다.

## 🎯 Remotion vs FFmpeg

### FFmpeg (기본)
- ✅ 빠른 처리 속도
- ✅ 간단한 설정
- ❌ 정적 이미지 + 오디오만 가능
- ❌ 애니메이션 제한적

### Remotion (권장)
- ✅ React 기반 동적 영상 생성
- ✅ 애니메이션, 전환 효과 가능
- ✅ 코드 하이라이팅, 슬라이드쇼 등 고급 기능
- ✅ 향후 확장성 높음
- ❌ Node.js 및 npm 필요
- ❌ 초기 설정 필요

## 📋 사전 요구사항

### 1. Node.js 설치

```bash
# Node.js 버전 확인
node --version  # v20 이상 권장

# npm 버전 확인
npm --version
```

### 2. Remotion 프로젝트 설정

```bash
cd video-generator
npm install
```

## 🚀 사용 방법

### 로컬 테스트

#### 1단계: 오디오 생성

```bash
# 먼저 오디오 생성
python3 scripts/generate_enhanced_audio.py
```

#### 2단계: Remotion 영상 생성

```bash
# Remotion으로 영상 생성
python3 scripts/generate_video_with_remotion.py

# 또는 특정 포스트 지정
python3 scripts/generate_video_with_remotion.py 2026-01-10-2026년_DevSecOps_로드맵_완벽_가이드_roadmap.sh_분석.md
```

### GitHub Actions 사용

1. **Actions** 탭 → **Generate AI Video Lecture** 선택
2. **Run workflow** 클릭
3. **video_method** 선택: `remotion`
4. (선택사항) **post_file** 입력
5. **Run workflow** 실행

## 📁 프로젝트 구조

```
video-generator/
├── package.json          # Remotion 의존성
├── remotion.config.ts    # Remotion 설정
├── src/
│   ├── Root.tsx         # Remotion 루트 컴포넌트
│   ├── BlogVideo.tsx    # 블로그 영상 컴포넌트
│   ├── index.tsx        # 진입점
│   └── index.css        # 스타일
└── public/              # 정적 파일 (오디오, 이미지)
```

## 🎨 커스터마이징

### BlogVideo.tsx 수정

현재 구현:
- 배경 이미지 (썸네일)
- 제목 텍스트
- 진행 바
- 오디오 재생

추가 가능한 기능:
- 코드 하이라이팅 애니메이션
- 슬라이드 전환 효과
- 텍스트 애니메이션
- 로고/워터마크
- 자막

예시:

```tsx
// 코드 하이라이팅 추가
import {Code} from '@remotion/layout-utils';

<Code
  code={codeSnippet}
  language="typescript"
  fontSize={24}
/>
```

## 🔧 문제 해결

### Node.js가 설치되지 않음

```bash
# macOS (Homebrew)
brew install node

# Ubuntu
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### npm install 실패

```bash
cd video-generator
rm -rf node_modules package-lock.json
npm install
```

### Remotion 렌더링 실패

1. 오디오 파일 확인: `output/*_audio.mp3` 존재 여부
2. 썸네일 이미지 확인: `assets/images/` 디렉토리 확인
3. 로그 확인: `video_generation_log.txt`

### 오디오 길이 확인 실패

FFprobe가 설치되어 있지 않으면 기본값(10초)을 사용합니다.

```bash
# FFprobe 설치 (FFmpeg와 함께 설치됨)
sudo apt-get install -y ffmpeg
```

## 📊 성능 비교

| 방법 | 렌더링 시간 | 파일 크기 | 품질 |
|------|------------|----------|------|
| FFmpeg | ~5초 | 작음 | 보통 |
| Remotion | ~30-60초 | 보통 | 높음 |

## 💡 향후 개선 사항

1. **코드 하이라이팅**: 블로그의 코드 블록을 애니메이션으로 표시
2. **슬라이드쇼**: 여러 이미지를 순차적으로 표시
3. **자막**: 자동 생성된 자막 표시
4. **브랜딩**: 로고, 워터마크 추가
5. **템플릿**: 다양한 영상 스타일 템플릿

## 🔗 관련 링크

- [Remotion 공식 문서](https://remotion.dev/docs)
- [Remotion GitHub](https://github.com/remotion-dev/remotion)
- [Remotion 예제](https://remotion.dev/showcase)
