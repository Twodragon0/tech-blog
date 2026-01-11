# 목소리 생성 로컬 테스트 가이드

이 가이드는 Gemini, ElevenLabs, DeepSeek을 활용한 목소리 생성 기능을 로컬에서 테스트하는 방법을 안내합니다.

## 사전 준비

### 1. 환경 변수 설정

`.env` 파일에 다음 환경 변수를 설정하세요:

```bash
# Gemini API
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLOUD_PROJECT=your-project-id

# DeepSeek API
DEEPSEEK_API_KEY=sk-your-deepseek-key

# ElevenLabs API (필수)
ELEVENLABS_API_KEY=sk_your-elevenlabs-key
ELEVENLABS_VOICE_ID=your-voice-id

# API 선택 전략
PREFER_GEMINI=true
USE_GEMINI_FOR_SCRIPT=true
USE_DEEPSEEK_FOR_SCRIPT=true
USE_GEMINI_FOR_IMPROVEMENT=true
```

**보안 주의**: `.env` 파일은 Git에 커밋하지 마세요. `.gitignore`에 이미 포함되어 있습니다.

### 2. Python 의존성 설치

```bash
cd scripts
pip3 install --user -r requirements.txt
```

필요한 패키지:
- `requests`
- `python-frontmatter`
- `google-generativeai`
- `google-auth`

## 로컬 테스트 실행

### 방법 1: 직접 실행

```bash
# 환경 변수 로드
set -a
source .env
set +a

# 최신 포스트로 테스트
python3 scripts/generate_enhanced_audio.py

# 특정 포스트로 테스트
python3 scripts/generate_enhanced_audio.py _posts/2025-01-10-example.md
```

### 방법 2: 테스트 스크립트 사용

```bash
# 테스트 스크립트 실행
bash /tmp/test_voice_gen.sh
```

## API 우선순위

스크립트는 다음 순서로 API를 사용합니다:

1. **Gemini OAuth 2.0** (서비스 계정 키가 있는 경우) ⭐ 최우선
2. **Gemini API Key** (OAuth 실패 시)
3. **DeepSeek API** (Gemini 실패 시)

## 출력 파일

생성된 오디오 파일은 `output/` 디렉토리에 저장됩니다:
- 파일명 형식: `{포스트명}_audio.mp3`
- 로그 파일: `video_generation_log.txt`

## 문제 해결

### 환경 변수가 로드되지 않는 경우

```bash
# .env 파일 확인
cat .env | grep -E "GEMINI|DEEPSEEK|ELEVENLABS"

# 수동으로 export
export GEMINI_API_KEY="your-key"
export ELEVENLABS_API_KEY="your-key"
export ELEVENLABS_VOICE_ID="your-voice-id"
```

### API 키 오류

- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 확인
- **DeepSeek API**: [DeepSeek Platform](https://platform.deepseek.com)에서 확인
- **ElevenLabs API**: [ElevenLabs Dashboard](https://elevenlabs.io/app)에서 확인

### 의존성 오류

```bash
# 패키지 재설치
pip3 install --user --upgrade -r scripts/requirements.txt
```

## GitHub Secrets 확인

로컬 테스트 전에 GitHub Secrets가 올바르게 설정되어 있는지 확인:

```bash
gh secret list | grep -E "GEMINI|DEEPSEEK|ELEVENLABS"
```

설정된 Secrets:
- `GEMINI_API_KEY` ✅
- `GOOGLE_CLOUD_PROJECT` ✅
- `DEEPSEEK_API_KEY` ✅
- `ELEVENLABS_API_KEY` ✅
- `ELEVENLABS_VOICE_ID` ✅

## 워크플로우 테스트

로컬 테스트가 성공하면 GitHub Actions 워크플로우를 테스트할 수 있습니다:

1. GitHub 저장소 → Actions 탭
2. "Generate AI Video Lecture" 워크플로우 선택
3. "Run workflow" 클릭
4. 포스트 파일명 입력 (선택사항)
5. 실행 확인

## 참고 자료

- [Gemini API 설정 가이드](./QUICK_START_GEMINI.md)
- [Secrets 관리 가이드](../.github/SECRETS_MANAGEMENT.md)
- [워크플로우 설정](../.github/workflows/ai-video-gen.yml)
