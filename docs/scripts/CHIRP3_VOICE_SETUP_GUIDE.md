# Chirp 3: Instant Custom Voice 설정 가이드

## 개요

Chirp 3: Instant Custom Voice를 사용하면 자신의 목소리로 오디오를 생성할 수 있습니다. 이 가이드는 자신의 목소리를 클로닝하여 사용하는 방법을 설명합니다.

## 사전 요구사항

1. **Google Cloud 프로젝트 생성**
   - [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
   - Text-to-Speech API 활성화

2. **Allowlist 등록**
   - ⚠️ **중요**: Chirp 3: Instant Custom Voice는 현재 allowlist에 등록된 사용자만 사용 가능합니다.
   - Google Cloud 팀에 연락하여 allowlist에 등록 요청

3. **OAuth 2.0 인증 설정**
   - 서비스 계정 생성 및 JSON 키 파일 다운로드
   - `GOOGLE_APPLICATION_CREDENTIALS` 환경 변수 설정

## 1단계: 참조 오디오 및 동의 오디오 준비

### 참조 오디오 (Reference Audio)
- **형식**: WAV 파일
- **샘플 레이트**: 24kHz
- **인코딩**: LINEAR16 (16-bit PCM)
- **길이**: 몇 초 분량의 명확한 음성
- **내용**: 일반적인 문장 (예: "안녕하세요. 오늘은 클라우드 보안에 대해 설명하겠습니다.")

### 동의 오디오 (Consent Audio)
- **형식**: WAV 파일
- **샘플 레이트**: 24kHz
- **인코딩**: LINEAR16 (16-bit PCM)
- **내용**: 다음 동의 스크립트를 읽은 오디오
  ```
  I am the owner of this voice and I consent to Google using this voice to create a synthetic voice model.
  ```
  또는 한국어:
  ```
  저는 이 목소리의 소유자이며, Google이 이 목소리를 사용하여 합성 음성 모델을 생성하는 것에 동의합니다.
  ```

### 오디오 파일 변환 (필요한 경우)

ffmpeg를 사용하여 오디오를 올바른 형식으로 변환:

```bash
# 참조 오디오 변환
ffmpeg -i reference_audio.mp3 -ar 24000 -ac 1 -sample_fmt s16 reference_audio.wav

# 동의 오디오 변환
ffmpeg -i consent_audio.mp3 -ar 24000 -ac 1 -sample_fmt s16 consent_audio.wav
```

## 2단계: Voice Cloning Key 생성

### 방법 1: Python 스크립트 사용

```python
from pathlib import Path
from scripts.generate_enhanced_audio import create_chirp3_voice_cloning_key

# 참조 오디오 및 동의 오디오 경로
reference_audio = Path("reference_audio.wav")
consent_audio = Path("consent_audio.wav")

# Voice Cloning Key 생성
voice_key = create_chirp3_voice_cloning_key(reference_audio, consent_audio)

if voice_key:
    print(f"Voice Cloning Key: {voice_key}")
    # .env 파일에 저장
    # CHIRP3_VOICE_CLONING_KEY=your-voice-key-here
else:
    print("Voice Cloning Key 생성 실패")
```

### 방법 2: Google Cloud 노트북 사용

[공식 노트북](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/audio/speech/getting-started/get_started_with_chirp3_instant_custom_voice.ipynb)을 사용하여 Voice Cloning Key 생성:

1. 노트북을 Colab 또는 Vertex AI Workbench에서 열기
2. 프로젝트 ID 설정
3. 참조 오디오 및 동의 오디오 업로드
4. Voice Cloning Key 생성

## 3단계: 환경 변수 설정

`.env` 파일에 다음 변수를 추가:

```bash
# Chirp 3: Instant Custom Voice 설정
USE_CHIRP3_CUSTOM_VOICE=true
CHIRP3_VOICE_CLONING_KEY=your-voice-cloning-key-here
GOOGLE_CLOUD_PROJECT=your-project-id
CHIRP3_LOCATION=global  # 또는 us, eu

# OAuth 2.0 인증 (서비스 계정 JSON 키 파일 경로)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# TTS 제공자 설정
TTS_PROVIDER=chirp3  # 또는 auto (자동 선택 시 Chirp 3 우선)
```

## 4단계: 오디오 생성

이제 자신의 목소리로 오디오를 생성할 수 있습니다:

```bash
python scripts/generate_enhanced_audio.py
```

## 리전 지원

Chirp 3: Instant Custom Voice는 다음 리전에서 지원됩니다:
- `global` (기본값)
- `us` (미국)
- `eu` (유럽)

리전은 `CHIRP3_LOCATION` 환경 변수로 설정할 수 있습니다.

## 다국어 지원

Voice Cloning Key는 한 언어로 생성했어도 다른 언어로 음성을 생성할 수 있습니다 (multilingual transfer).

예:
- 한국어로 생성한 Voice Cloning Key로 영어 음성 생성 가능
- 영어로 생성한 Voice Cloning Key로 한국어 음성 생성 가능

## 문제 해결

### 1. Allowlist 오류
```
Error: Access denied. This feature requires allowlist access.
```
**해결**: Google Cloud 팀에 연락하여 allowlist 등록 요청

### 2. OAuth 2.0 인증 오류
```
Error: OAuth 2.0 authentication failed
```
**해결**: 
- `GOOGLE_APPLICATION_CREDENTIALS` 환경 변수 확인
- 서비스 계정 JSON 키 파일 경로 확인
- 서비스 계정에 Text-to-Speech API 권한 확인

### 3. 오디오 형식 오류
```
Error: Invalid audio format
```
**해결**: 
- 오디오가 24kHz, LINEAR16, Mono 형식인지 확인
- ffmpeg로 올바른 형식으로 변환

### 4. Voice Cloning Key 생성 실패
```
Error: Failed to create voice cloning key
```
**해결**:
- 참조 오디오와 동의 오디오가 올바른 형식인지 확인
- Google Cloud 프로젝트에서 Text-to-Speech API 활성화 확인
- Allowlist 등록 확인

## 참고 자료

- [Chirp 3: Instant Custom Voice 공식 문서](https://docs.cloud.google.com/text-to-speech/docs/chirp3-instant-custom-voice)
- [Google Cloud 노트북](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/audio/speech/getting-started/get_started_with_chirp3_instant_custom_voice.ipynb)
- [Text-to-Speech API 문서](https://cloud.google.com/text-to-speech/docs)

## 보안 고려사항

1. **Voice Cloning Key 관리**
   - Voice Cloning Key는 민감 정보이므로 환경 변수로 관리
   - 공개 저장소에 커밋하지 않음
   - `.env` 파일을 `.gitignore`에 추가

2. **오디오 파일 보안**
   - 참조 오디오와 동의 오디오는 개인 정보이므로 안전하게 보관
   - 공개 저장소에 업로드하지 않음

3. **서비스 계정 키 관리**
   - 서비스 계정 JSON 키 파일은 절대 공개하지 않음
   - 최소 권한 원칙 적용
