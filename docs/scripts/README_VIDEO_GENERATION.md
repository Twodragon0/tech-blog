# 블로그 포스팅 → 영상 강의 자동 변환 가이드

이 스크립트는 블로그 포스팅을 자동으로 영상 강의용 오디오로 변환하는 시스템입니다.

## 🎯 기능

1. **대본 추출 및 요약**: DeepSeek API 또는 Gemini API를 사용하여 블로그 내용을 강의용 대본으로 변환
2. **대본 개선**: Gemini API를 활용한 품질 향상 (선택적)
3. **음성 생성**: ElevenLabs API를 사용하여 본인의 목소리로 음성 생성
4. **영상 생성**: FFmpeg 또는 Remotion을 사용하여 썸네일 이미지와 오디오를 합쳐 MP4 영상 생성

## 🆕 개선된 버전

**권장**: `generate_enhanced_audio.py` 사용
- ✅ DeepSeek과 Gemini API 선택적 활용
- ✅ 비용 최적화 (캐싱, 사용량 모니터링)
- ✅ 보안 강화
- ✅ 품질 향상 (2단계 대본 생성)

자세한 내용은 [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md)를 참조하세요.

## 📋 사전 요구사항

### 1. API 키 준비

다음 API 키가 필요합니다:

#### 필수
- **ElevenLabs API Key**: [ElevenLabs Platform](https://elevenlabs.io)에서 발급
- **ElevenLabs Voice ID**: ElevenLabs에서 본인의 목소리를 클로닝한 Voice ID

#### 선택 (최소 하나 필요)
- **DeepSeek API Key**: [DeepSeek Platform](https://platform.deepseek.com)에서 발급 (권장, 비용 효율적)
- **Gemini API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급 (품질 향상용)

### 2. 환경 변수 설정

로컬 테스트 시:

```bash
# 필수
export ELEVENLABS_API_KEY='your-elevenlabs-api-key'
export ELEVENLABS_VOICE_ID='your-voice-id'

# 선택 (최소 하나)
export DEEPSEEK_API_KEY='sk-your-deepseek-api-key'  # 권장
export GEMINI_API_KEY='your-gemini-api-key'  # 선택적
```

GitHub Actions 사용 시:

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. 다음 Secrets 추가:
   - `ELEVENLABS_API_KEY`
   - `ELEVENLABS_VOICE_ID`
   - `DEEPSEEK_API_KEY`

## 🚀 사용 방법

### 로컬 테스트

#### 1. 최신 포스트 자동 선택

```bash
cd scripts
python3 scripts/generate_enhanced_audio.py
```

#### 2. 특정 포스트 지정

```bash
python3 scripts/generate_enhanced_audio.py 2026-01-10-2026년_DevSecOps_로드맵_완벽_가이드_roadmap.sh_분석.md
```

#### 3. 결과 확인

생성된 파일은 `output/` 디렉토리에 저장됩니다:
- `{포스트명}_audio.mp3`: 생성된 오디오 파일

### GitHub Actions 사용

1. GitHub 저장소에서 **Actions** 탭으로 이동
2. **Generate AI Video Lecture** 워크플로우 선택
3. **Run workflow** 클릭
4. (선택사항) 특정 포스트 파일명 입력
5. **Run workflow** 실행

생성된 영상과 오디오는 **Artifacts**에서 다운로드할 수 있습니다.

## 📁 출력 파일

- `output/{포스트명}_audio.mp3`: 생성된 오디오 파일
- `output/{포스트명}_audio.mp4`: 생성된 영상 파일 (GitHub Actions에서만)
- `video_generation_log.txt`: 생성 로그

## ⚙️ 설정

### 스크립트 설정 (`generate_enhanced_audio.py`)

```python
MAX_TEXT_LENGTH = 50000  # 최대 텍스트 길이 (비용 관리)
MAX_SCRIPT_LENGTH = 3000  # 최대 대본 길이 (약 5분 분량)
AUDIO_OUTPUT_FORMAT = "mp3"
```

### ElevenLabs 모델 설정

현재 사용 모델: `eleven_multilingual_v2` (한국어 지원)

다른 모델 사용 시 `text_to_speech()` 함수의 `model_id` 수정:

```python
data = {
    "text": script,
    "model_id": "eleven_multilingual_v2",  # 또는 "eleven_turbo_v2_5"
    ...
}
```

## 🔒 보안 고려사항

### 1. API 키 보호

- ✅ 모든 API 키는 환경 변수에서만 읽음
- ✅ 로그에 민감 정보 자동 마스킹
- ✅ Git에 API 키 커밋 금지

### 2. 비용 관리

- ✅ 텍스트 길이 제한 (50,000자)
- ✅ 대본 길이 제한 (약 5분 분량)
- ✅ GitHub Actions는 수동 실행만 허용 (workflow_dispatch)

### 3. 에러 핸들링

- ✅ 모든 API 호출에 타임아웃 설정
- ✅ 상세한 에러 로깅
- ✅ 실패 시 즉시 중단

## 🐛 문제 해결

### API 키 오류

```
❌ 필수 환경 변수가 설정되지 않았습니다: ELEVENLABS_API_KEY
```

**해결 방법:**
1. 환경 변수 확인: `echo $ELEVENLABS_API_KEY`
2. GitHub Secrets 확인: Settings → Secrets and variables → Actions

### DeepSeek API 오류

```
❌ DeepSeek API 요청 실패: 401 Unauthorized
```

**해결 방법:**
1. API 키 형식 확인: `sk-`로 시작해야 함
2. API 키 유효성 확인: [DeepSeek Platform](https://platform.deepseek.com)에서 확인

### ElevenLabs API 오류

```
❌ ElevenLabs API 요청 실패: 401 Unauthorized
```

**해결 방법:**
1. API 키 확인: [ElevenLabs Platform](https://elevenlabs.io)에서 확인
2. Voice ID 확인: ElevenLabs 대시보드에서 본인의 Voice ID 확인

### 오디오 생성 실패

```
❌ 음성 생성 실패
```

**해결 방법:**
1. 대본 길이 확인: 너무 길면 자동으로 잘림
2. ElevenLabs 할당량 확인: 무료 티어는 제한이 있을 수 있음
3. 로그 확인: `video_generation_log.txt` 파일 확인

## 💡 팁

### 1. 비용 최적화

- 처음에는 짧은 포스트(1-2분 분량)로 테스트
- ElevenLabs 무료 티어는 월 10,000자 제한
- DeepSeek은 토큰 기반 과금

### 2. 품질 향상

- ElevenLabs Voice Cloning으로 본인의 목소리 사용
- 대본 프롬프트를 수정하여 더 자연스러운 말투 생성
- FFmpeg 옵션 조정으로 영상 품질 향상

### 3. 자동화

- GitHub Actions를 사용하여 새 포스트 자동 처리 (비용 주의)
- 워크플로우는 수동 실행만 허용하여 비용 관리

## 📊 로그 확인

모든 작업은 `video_generation_log.txt`에 기록됩니다:

```bash
tail -f video_generation_log.txt
```

## 🔗 관련 문서

- [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md) ⭐ **권장**
- [비용 최적화 가이드](./COST_OPTIMIZATION_GUIDE.md)
- [GitHub Secrets 관리 가이드](../.github/SECRETS_MANAGEMENT.md)
- [DeepSeek API 최적화 가이드](../DEEPSEEK_API_OPTIMIZATION.md)
- [ElevenLabs 공식 문서](https://elevenlabs.io/docs)

## ⚠️ 주의사항

1. **비용 관리**: ElevenLabs와 DeepSeek API는 사용량에 따라 과금됩니다. 처음에는 짧은 포스트로 테스트하세요.

2. **API 키 보안**: 절대 Git에 API 키를 커밋하지 마세요. 환경 변수나 GitHub Secrets만 사용하세요.

3. **할당량 제한**: 무료 티어는 제한이 있을 수 있습니다. 사용량을 모니터링하세요.

4. **음성 품질**: ElevenLabs Voice Cloning을 사용하면 더 자연스러운 음성을 얻을 수 있습니다.
