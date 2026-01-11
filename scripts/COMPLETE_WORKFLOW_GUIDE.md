# 완전한 강의 영상 생성 워크플로우 가이드

## 🎯 전체 워크플로우 구조

```
포스팅 완료
    ↓
[0] 이미지 생성 (Gemini Nano Banana / Cursor / Claude)
    ↓
[1] 강의 대본 생성 (Gemini 우선 → DeepSeek 폴백)
    ↓
[2] 오디오 생성 (ElevenLabs 우선 → Gemini 폴백)
    ↓
[3] 영상 제작 (Gemini Veo 우선 → Remotion 폴백)
```

## 💰 비용 최적화 전략

### API 선택 우선순위 (비용 효율성 고려)

1. **대본 생성**: Gemini 우선 → DeepSeek 폴백
   - Gemini: 고품질 대본 생성 (비용: $1.25/1M input, $5.00/1M output)
   - DeepSeek: 비용 효율적 폴백 (비용: $0.14/1M input, $0.28/1M output)
   - **전략**: Gemini로 고품질 대본 생성, 실패 시 DeepSeek 사용

2. **오디오 생성**: ElevenLabs 우선 → Gemini 폴백
   - ElevenLabs: 비용 효율적, 무료 티어 제공 (월 10,000자)
   - Gemini TTS: 향후 지원 예정
   - **전략**: ElevenLabs를 우선 사용하여 비용 절감

3. **이미지 생성**: Gemini Nano Banana / Cursor / Claude
   - Gemini Nano Banana: 비용 효율적 이미지 생성
   - Cursor/Claude: 수동 생성 안내
   - **전략**: Gemini Nano Banana 우선, 실패 시 수동 생성 안내

4. **영상 생성**: Gemini Veo 우선 → Remotion 폴백 → FFmpeg 폴백
   - Gemini Veo: 고품질 동적 영상 (향후 지원)
   - Remotion: 동적 영상 생성 (Node.js 필요)
   - FFmpeg: 빠른 정적 영상 (기본)
   - **전략**: Gemini Veo 우선, 실패 시 Remotion, 최종 폴백 FFmpeg

### 캐싱 전략

- **대본 캐싱**: 동일 포스트의 대본은 7일간 캐시 사용
- **API 호출 최소화**: 실패한 API는 즉시 폴백으로 전환
- **재시도 제한**: 최대 3회 재시도로 불필요한 비용 방지

## 🔒 보안 고려사항

1. **API 키 관리**
   - 모든 API 키는 환경 변수에서만 읽음
   - GitHub Secrets에 암호화 저장
   - 로그에 민감 정보 마스킹

2. **입력 검증**
   - 포스트 파일 존재 확인
   - API 키 형식 검증
   - 파일 경로 검증

3. **에러 핸들링**
   - 안전한 에러 메시지 (민감 정보 제외)
   - 상세한 로그 기록 (마스킹된 정보만)

## 🚀 사용 방법

### 기본 실행 (전체 워크플로우)

```bash
# 환경 변수 로드
set -a
source .env
set +a

# 최신 포스트로 전체 생성
python3 scripts/generate_complete_lecture.py

# 특정 포스트로 전체 생성
python3 scripts/generate_complete_lecture.py _posts/2026-01-08-example.md
```

### 옵션 사용

```bash
# 이미지 생성 방법 지정
python3 scripts/generate_complete_lecture.py --image-method cursor
python3 scripts/generate_complete_lecture.py --image-method claude

# 영상 생성 방법 지정
python3 scripts/generate_complete_lecture.py --video-method remotion
python3 scripts/generate_complete_lecture.py --video-method ffmpeg

# 특정 단계만 실행
python3 scripts/generate_complete_lecture.py --skip-image  # 이미지 제외
python3 scripts/generate_complete_lecture.py --skip-video  # 영상 제외
python3 scripts/generate_complete_lecture.py --skip-script --skip-audio  # 대본/오디오 제외
```

## 📋 단계별 상세 설명

### 0단계: 이미지 생성 (포스팅 완료 후)

**목적**: 강의용 썸네일 이미지 생성

**방법**:
1. **Gemini Nano Banana** (우선) ⭐
   - 자동 이미지 생성
   - 비용 효율적
2. **Cursor** (수동)
   - IDE에서 이미지 생성 프롬프트 제공
   - 사용자가 직접 생성
3. **Claude** (수동)
   - 이미지 생성 제한적
   - 텍스트 기반 안내

**출력**: `assets/images/{포스트명}_thumbnail.png`

### 1단계: 강의 대본 생성

**목적**: 블로그 포스트를 강의용 대본으로 변환

**API 우선순위**:
1. **Gemini 2.5 Pro** (우선) ⭐
   - 고품질 대본 생성
   - 7-8분 분량 (1.5배속 재생 시 약 5분)
2. **DeepSeek API** (폴백)
   - 비용 효율적
   - Gemini 실패 시 사용

**출력**: `output/{포스트명}_script.txt`

### 2단계: 오디오 생성

**목적**: 대본을 음성으로 변환

**API 우선순위**:
1. **ElevenLabs API** (우선) ⭐
   - 비용 효율적 (무료 티어: 월 10,000자)
   - 고품질 한국어 음성
2. **Gemini TTS** (폴백)
   - 향후 지원 예정
   - ElevenLabs 실패 시 사용

**출력**: `output/{포스트명}_audio.mp3`

### 3단계: 영상 제작

**목적**: 오디오와 이미지를 결합하여 영상 생성

**API 우선순위**:
1. **Gemini Veo** (우선) ⭐
   - 고품질 동적 영상
   - 향후 지원 예정
2. **Remotion** (폴백)
   - 동적 영상 생성
   - Node.js 필요
3. **FFmpeg** (최종 폴백)
   - 빠른 정적 영상
   - 기본 방법

**출력**: `output/{포스트명}_video.mp4`

## 📊 생성된 파일 구조

```
output/
  ├── {포스트명}_script.txt      # 강의용 대본 (Gemini/DeepSeek)
  ├── {포스트명}_audio.mp3       # 오디오 파일 (ElevenLabs/Gemini)
  └── {포스트명}_video.mp4       # 영상 파일 (Gemini Veo/Remotion/FFmpeg)

assets/images/
  └── {포스트명}_thumbnail.png   # 썸네일 이미지 (Gemini Nano Banana/Cursor/Claude)
```

## ⚙️ 환경 변수 설정

### 필수 환경 변수

```bash
# Gemini API (대본 생성, 이미지 생성, 영상 생성)
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLOUD_PROJECT=your-project-id

# DeepSeek API (대본 생성 폴백)
DEEPSEEK_API_KEY=sk-your-deepseek-key

# ElevenLabs API (오디오 생성 우선)
ELEVENLABS_API_KEY=sk_your-elevenlabs-key
ELEVENLABS_VOICE_ID=your-voice-id
```

### 선택적 환경 변수 (전략 제어)

```bash
# API 선택 전략
PREFER_GEMINI=true              # Gemini 우선 (기본값)
USE_GEMINI_FOR_SCRIPT=true      # Gemini로 대본 생성 (기본값)
USE_DEEPSEEK_FOR_SCRIPT=true    # DeepSeek으로 대본 생성 (폴백)
ENABLE_CACHING=true             # 캐싱 활성화 (기본값)
```

## 💡 비용 최적화 팁

1. **캐싱 활용**: 동일 포스트는 캐시된 대본 사용
2. **API 선택**: 비용 효율적인 API 우선 사용 (ElevenLabs, DeepSeek)
3. **재시도 제한**: 최대 3회 재시도로 불필요한 비용 방지
4. **에러 처리**: 실패 시 즉시 폴백으로 전환하여 불필요한 재시도 방지

## 🔧 문제 해결

### 이미지 생성 실패
- Gemini Nano Banana가 제한적인 경우: Cursor나 Claude로 수동 생성
- 기본 썸네일 사용: `assets/images/` 디렉토리에 이미지 추가

### 대본 생성 실패
- Gemini API 키 확인
- DeepSeek API 키 확인 (폴백용)
- 네트워크 연결 확인

### 오디오 생성 실패
- ElevenLabs 크레딧 확인
- Voice ID 확인
- Gemini TTS는 향후 지원 예정

### 영상 생성 실패
- Gemini Veo는 향후 지원 예정
- Remotion: Node.js 및 npm 설치 확인
- FFmpeg: 설치 확인 (`brew install ffmpeg`)

## 📚 관련 문서

- [워크플로우 요약](./WORKFLOW_SUMMARY.md)
- [로컬 테스트 가이드](./TEST_VOICE_GENERATION.md)
- [Secrets 관리 가이드](../.github/SECRETS_MANAGEMENT.md)

---

**마지막 업데이트**: 2026-01-11
**버전**: 1.0.0
