# 블로그 포스트 → 오디오 → 영상 생성 워크플로우 요약

## 🎯 전체 워크플로우

```
블로그 포스트
    ↓
[1] 대본 생성 (Gemini 우선 → DeepSeek 폴백)
    ↓
[2] 오디오 생성 (Gemini TTS 우선 → ElevenLabs 폴백)
    ↓
[3] 이미지 생성 (Gemini Nano Banana, 선택적)
    ↓
[4] 영상 생성 (Gemini Veo / Remotion / FFmpeg)
```

## 📝 1단계: 대본 생성

### API 우선순위
1. **Gemini 2.5 Pro** (우선) ⭐
2. **DeepSeek API** (Gemini 실패 시 폴백)

### 대본 사양
- **길이**: 7-8분 분량 (약 2,000-2,500자)
- **재생 속도**: 1.5배속 고려 (1.5배속 재생 시 약 5분)
- **구성**:
  - 서론: 30-45초 (1.5배속 시 20-30초)
  - 본론: 6-7분 (1.5배속 시 4-4.5분)
  - 결론: 30-45초 (1.5배속 시 20-30초)

### 출력 파일
- `output/{포스트명}_script.txt` - 대본 파일 (사용된 API 정보 포함)

## 🎤 2단계: 오디오 생성

### API 우선순위
1. **Gemini TTS** (우선, 현재 제한적) ⭐
2. **ElevenLabs API** (Gemini 실패 시 폴백)

### 출력 파일
- `output/{포스트명}_audio.mp3` - 오디오 파일

## 🎨 3단계: 이미지 생성 (선택적)

### API
- **Gemini Nano Banana** (이미지 생성)

### 사용 방법
```bash
python3 scripts/generate_post_to_video.py --generate-image
```

### 출력 파일
- `output/{포스트명}_thumbnail.png` - 생성된 썸네일 이미지

## 📹 4단계: 영상 생성

### 방법 옵션
1. **Gemini Veo** (우선, 현재 제한적) ⭐
2. **Remotion** (동적 영상 생성)
3. **FFmpeg** (기본, 빠른 정적 영상)

> 영상/오디오 생성 스크립트는 `~/Desktop/online-course/` 프로젝트로 이전되었습니다.
> 상세 사용법: `~/Desktop/online-course/scripts/audio_video/`

## 🚀 통합 실행

### 기본 실행 (전체 워크플로우)
```bash
# 환경 변수 로드
set -a
source .env
set +a

# 최신 포스트로 전체 생성
python3 scripts/generate_post_to_video.py

# 특정 포스트로 전체 생성
python3 scripts/generate_post_to_video.py _posts/2026-01-08-example.md
```

### 옵션 조합
```bash
# 이미지 생성 포함
python3 scripts/generate_post_to_video.py --generate-image

# Gemini Veo로 영상 생성 + 이미지 생성
python3 scripts/generate_post_to_video.py --method gemini-veo --generate-image

# 오디오만 생성 (대본 + 오디오)
python3 scripts/generate_post_to_video.py --skip-video

# 영상만 생성 (오디오가 이미 있는 경우)
python3 scripts/generate_post_to_video.py --skip-audio
```

## ⚙️ 환경 변수 설정

### 필수
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

### 선택적 (전략 제어)
```bash
# API 선택 전략
PREFER_GEMINI=true              # Gemini 우선 (기본값)
USE_GEMINI_FOR_SCRIPT=true      # Gemini로 대본 생성 (기본값)
USE_DEEPSEEK_FOR_SCRIPT=true    # DeepSeek으로 대본 생성 (폴백)
USE_GEMINI_FOR_IMPROVEMENT=true # Gemini로 대본 개선
ENABLE_CACHING=true             # 캐싱 활성화
```

## 📊 생성된 파일

전체 워크플로우 실행 시 생성되는 파일:

```
output/
  ├── {포스트명}_script.txt      # 강의용 대본 (Gemini/DeepSeek)
  ├── {포스트명}_audio.mp3       # 오디오 파일 (Gemini TTS/ElevenLabs)
  ├── {포스트명}_thumbnail.png   # 썸네일 이미지 (Gemini Nano Banana, 선택적)
  └── {포스트명}_video.mp4       # 영상 파일 (Gemini Veo/Remotion/FFmpeg)
```

## 🔄 API 우선순위 요약

### 대본 생성
1. Gemini 2.5 Pro ⭐
2. DeepSeek API (폴백)

### 오디오 생성
1. Gemini TTS ⭐ (준비됨)
2. ElevenLabs API (폴백)

### 이미지 생성
1. Gemini Nano Banana ⭐ (준비됨)

### 영상 생성
1. Gemini Veo ⭐ (준비됨)
2. Remotion (동적 영상)
3. FFmpeg (정적 영상, 기본)

## 📝 참고 사항

- **1.5배속 재생**: 대본이 7-8분 분량으로 생성되어 1.5배속 재생 시 약 5분 분량이 됩니다.
- **Gemini 우선**: 모든 단계에서 Gemini를 우선적으로 사용하며, 실패 시 폴백 API로 전환합니다.
- **대본 파일**: 생성된 대본은 자동으로 파일로 저장되며, 사용된 API 정보가 포함됩니다.

---

**마지막 업데이트**: 2026-01-11
