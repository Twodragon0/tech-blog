# 블로그 포스트 → 오디오 → 영상 자동 생성 가이드

이 가이드는 블로그 포스트를 오디오로 변환한 후 영상까지 자동으로 생성하는 통합 워크플로우를 설명합니다.

## 📋 개요

`generate_post_to_video.py` 스크립트는 다음 작업을 자동으로 수행합니다:

1. **오디오 생성**: 블로그 포스트를 강의용 대본으로 변환 후 ElevenLabs로 음성 생성
2. **영상 생성**: 생성된 오디오와 썸네일 이미지를 결합하여 영상 생성

## 🚀 빠른 시작

### 기본 사용법

```bash
# 최신 포스트로 오디오 + 영상 생성 (FFmpeg)
python3 scripts/generate_post_to_video.py

# 특정 포스트로 오디오 + 영상 생성
python3 scripts/generate_post_to_video.py _posts/2025-01-10-example.md
```

### 옵션

```bash
# Remotion으로 영상 생성
python3 scripts/generate_post_to_video.py --method remotion

# 오디오만 생성 (영상 생성 건너뛰기)
python3 scripts/generate_post_to_video.py --skip-video

# 영상만 생성 (오디오 생성 건너뛰기, 이미 오디오가 있는 경우)
python3 scripts/generate_post_to_video.py --skip-audio
```

## 📦 사전 요구사항

### 1. 환경 변수 설정

`.env` 파일에 다음 환경 변수를 설정하세요:

```bash
# Gemini API
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLOUD_PROJECT=your-project-id

# DeepSeek API
DEEPSEEK_API_KEY=sk-your-deepseek-key

# ElevenLabs API
ELEVENLABS_API_KEY=sk_your-elevenlabs-key
ELEVENLABS_VOICE_ID=your-voice-id
```

### 2. Python 의존성

```bash
pip3 install --user -r scripts/requirements.txt
```

필요한 패키지:
- `requests`
- `python-frontmatter`
- `google-generativeai`
- `google-auth`

### 3. FFmpeg 설치 (FFmpeg 방법 사용 시)

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 4. Node.js 및 Remotion (Remotion 방법 사용 시)

```bash
# Node.js 설치 확인
node --version

# video-generator 디렉토리에서 의존성 설치
cd video-generator
npm install
```

## 🎬 영상 생성 방법

### FFmpeg 방법 (기본, 권장)

- **장점**: 빠르고 가볍고, 추가 설정 불필요
- **단점**: 정적 이미지만 사용 (썸네일 이미지 + 오디오)
- **사용 시나리오**: 빠른 영상 생성이 필요한 경우

```bash
python3 scripts/generate_post_to_video.py --method ffmpeg
```

### Remotion 방법

- **장점**: 동적 영상 생성 가능, 커스터마이징 가능
- **단점**: Node.js 및 npm 의존성 필요, 설정 복잡
- **사용 시나리오**: 고품질 동적 영상이 필요한 경우

```bash
python3 scripts/generate_post_to_video.py --method remotion
```

## 📁 출력 파일

생성된 파일은 `output/` 디렉토리에 저장됩니다:

- **대본**: `{포스트명}_script.txt` - Gemini/DeepSeek으로 생성된 강의용 대본
- **오디오**: `{포스트명}_audio.mp3` - ElevenLabs로 생성된 음성 파일
- **영상**: `{포스트명}_video.mp4` - 오디오와 썸네일을 결합한 영상 파일

예시:
```
output/
  ├── 2025-05-30-Kubernetes_Minikube_ampamp_K9s_실습_가이드_문제_해결부터_실전_테스트까지_script.txt
  ├── 2025-05-30-Kubernetes_Minikube_ampamp_K9s_실습_가이드_문제_해결부터_실전_테스트까지_audio.mp3
  └── 2025-05-30-Kubernetes_Minikube_ampamp_K9s_실습_가이드_문제_해결부터_실전_테스트까지_video.mp4
```

### 대본 파일 형식

대본 파일(`_script.txt`)에는 다음 정보가 포함됩니다:

```
# 포스트 제목

생성일: 2026-01-11 19:00:00
대본 길이: 1782자
원본 포스트: 2025-05-30-example.md
사용된 API: Gemini API Key → DeepSeek API
API 전략: Gemini 우선

============================================================
강의용 대본
============================================================

[대본 본문...]
```

- **제목**: 포스트 제목
- **생성일**: 대본 생성 시각
- **대본 길이**: 생성된 대본의 문자 수
- **원본 포스트**: 원본 블로그 포스트 파일명
- **사용된 API**: 대본 생성에 사용된 API 목록 (Gemini OAuth 2.0, Gemini API Key, DeepSeek API)
- **API 전략**: 사용된 API 선택 전략 (OAuth 2.0 우선, Gemini 우선, DeepSeek 우선)
- **대본 본문**: Gemini/DeepSeek으로 생성된 강의용 대본

## 🖼️ 썸네일 이미지

영상 생성을 위해 썸네일 이미지가 필요합니다:

1. **포스트 Front matter의 `image` 필드** (우선)
   ```yaml
   image: /assets/images/thumbnail.png
   ```

2. **assets/images 디렉토리의 기본 이미지** (폴백)
   - `assets/images/*.png` 또는 `*.jpg` 파일

## 🔄 워크플로우 단계

### 1단계: 오디오 생성

1. 블로그 포스트 마크다운 읽기
2. 텍스트 정제 (코드 블록, 이미지 제거 등)
3. AI로 강의용 대본 생성 (Gemini 또는 DeepSeek)
4. **대본 파일 저장**: `output/{포스트명}_script.txt` (사용된 API 정보 포함)
5. ElevenLabs로 음성 생성
6. `output/{포스트명}_audio.mp3` 저장

### 2단계: 영상 생성

1. 생성된 오디오 파일 확인
2. 썸네일 이미지 찾기
3. FFmpeg 또는 Remotion으로 영상 생성
4. `output/{포스트명}_video.mp4` 저장

## 💡 사용 예시

### 예시 1: 전체 워크플로우 실행

```bash
# 환경 변수 로드
set -a
source .env
set +a

# 최신 포스트로 오디오 + 영상 생성
python3 scripts/generate_post_to_video.py
```

### 예시 2: 특정 포스트 처리

```bash
python3 scripts/generate_post_to_video.py _posts/2025-01-10-example.md
```

### 예시 3: 오디오만 생성

```bash
python3 scripts/generate_post_to_video.py --skip-video
```

### 예시 4: 이미 생성된 오디오로 영상만 생성

```bash
python3 scripts/generate_post_to_video.py --skip-audio
```

## 📊 로그 확인

모든 작업 로그는 `video_generation_log.txt`에 저장됩니다:

```bash
# 최근 로그 확인
tail -n 50 video_generation_log.txt

# 오류만 확인
grep ERROR video_generation_log.txt
```

## ⚙️ 환경 변수 옵션

오디오 생성 시 다음 환경 변수로 동작을 제어할 수 있습니다:

```bash
# API 선택 전략
PREFER_GEMINI=true              # Gemini 우선 사용
USE_GEMINI_FOR_SCRIPT=true      # Gemini로 대본 생성
USE_DEEPSEEK_FOR_SCRIPT=true    # DeepSeek으로 대본 생성
USE_GEMINI_FOR_IMPROVEMENT=true # Gemini로 대본 개선
ENABLE_CACHING=true             # 캐싱 활성화
```

## 🔧 문제 해결

### 오디오 생성 실패

1. 환경 변수 확인:
   ```bash
   echo $ELEVENLABS_API_KEY
   echo $ELEVENLABS_VOICE_ID
   ```

2. API 키 유효성 확인:
   - [ElevenLabs 대시보드](https://elevenlabs.io/app)에서 크레딧 확인
   - [Gemini API](https://makersuite.google.com/app/apikey)에서 키 확인

### 영상 생성 실패 (FFmpeg)

1. FFmpeg 설치 확인:
   ```bash
   ffmpeg -version
   ```

2. 썸네일 이미지 확인:
   ```bash
   ls -la assets/images/*.png
   ```

### 영상 생성 실패 (Remotion)

1. Node.js 설치 확인:
   ```bash
   node --version
   npm --version
   ```

2. 의존성 설치 확인:
   ```bash
   cd video-generator
   npm install
   ```

## 📚 관련 문서

- [로컬 테스트 가이드](./TEST_VOICE_GENERATION.md)
- [오디오 생성 상세 가이드](./README_ENHANCED_AUDIO.md)
- [Remotion 영상 생성 가이드](./README_REMOTION.md)
- [GitHub Actions 워크플로우](../.github/workflows/ai-video-gen.yml)

## 🎯 GitHub Actions 사용

로컬 테스트가 완료되면 GitHub Actions에서도 실행할 수 있습니다:

1. GitHub 저장소 → Actions 탭
2. "Generate AI Video Lecture" 워크플로우 선택
3. "Run workflow" 클릭
4. 옵션 설정:
   - `post_file`: 포스트 파일명 (선택사항)
   - `video_method`: `ffmpeg` 또는 `remotion`

## ✅ 체크리스트

오디오 + 영상 생성 전 확인사항:

- [ ] `.env` 파일에 모든 API 키 설정
- [ ] Python 의존성 설치 완료
- [ ] FFmpeg 설치 (FFmpeg 방법 사용 시)
- [ ] Node.js 및 npm 설치 (Remotion 방법 사용 시)
- [ ] `assets/images/` 디렉토리에 썸네일 이미지 존재
- [ ] 포스트 Front matter에 `image` 필드 설정 (선택사항)

---

**마지막 업데이트**: 2026-01-11
