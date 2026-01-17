# TTS 비용 최적화 가이드

## 개요

Gemini TTS API와 오픈소스 대안(Coqui TTS)을 통합하여 비용 효율적인 TTS 솔루션을 제공합니다.

## 비용 비교

### 1. Gemini 2.5 TTS API (권장 ⭐)
- **가격**: 토큰 기반 과금
  - Flash: Input $0.50/1M tokens, Output $10/1M tokens
  - Pro: Input $1/1M tokens, Output $20/1M tokens
- **장점**: 
  - 사용한 만큼만 과금 (구독 불필요)
  - 2,000-2,500자 대본 기준 매우 저렴
  - 이미 사용 중인 Gemini API 키 활용 가능
- **단점**: Preview 모델 (안정성 제한 가능)

### 2. Coqui TTS (무료 오픈소스)
- **가격**: 완전 무료
- **장점**: 
  - 자체 호스팅 가능
  - 데이터 프라이버시 보장
  - 한국어 지원
- **단점**: 
  - 초기 설정 필요
  - 품질이 상용 서비스 대비 낮을 수 있음

## 설정 방법

### 환경 변수 설정

`.env` 파일에 다음 변수를 추가하세요:

```bash
# TTS 제공자 선택 (기본값: auto)
# 옵션: "chirp3", "gemini", "coqui", "auto"
TTS_PROVIDER=auto

# Gemini TTS 사용 (기본값: auto 모드에서 자동 선택)
GEMINI_API_KEY=your-gemini-api-key
# Gemini TTS Voice 설정 (IT/DevSecOps 전문가용 남자 목소리)
# 기본값: "Rasalgethi" (IT 전문가용 추천)
# 다른 voice 옵션: Charon, Iapetus, Orus, Sadaltager 등
GEMINI_TTS_VOICE_NAME=Rasalgethi

# Chirp 3: Instant Custom Voice (자신의 목소리 클로닝) - 선택적
# Google Cloud Text-to-Speech API에서 voice cloning key 생성 필요
# 자세한 내용은 CHIRP3_VOICE_SETUP_GUIDE.md 참조
USE_CHIRP3_CUSTOM_VOICE=true
CHIRP3_VOICE_CLONING_KEY=your-voice-cloning-key
GOOGLE_CLOUD_PROJECT=your-project-id
CHIRP3_LOCATION=global  # 또는 us, eu
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Voice 스타일 제어 (자연어 프롬프트) - 선택적
# 예: "professional and authoritative", "friendly and informative"
# GEMINI_TTS_VOICE_STYLE=professional and authoritative

# Voice 속도 제어 (0.25 ~ 4.0, 기본값: 1.0) - 선택적
# GEMINI_TTS_VOICE_PACE=1.0

# Coqui TTS 사용 (선택적, 무료)
USE_COQUI_TTS=false
```

### TTS 제공자 선택 전략

#### 1. `auto` (기본값, 권장)
자동으로 가장 적합한 옵션을 선택합니다:
1. **Chirp 3** 우선 (자신의 목소리, 설정된 경우)
2. **Gemini TTS** 폴백 (비용 효율적)
3. **Coqui TTS** 폴백 (모두 실패 시, 무료)

```bash
TTS_PROVIDER=auto
```

#### 2. `chirp3` (Chirp 3만 사용 - 자신의 목소리)
자신의 목소리로 클로닝된 음성을 사용합니다.

```bash
TTS_PROVIDER=chirp3
USE_CHIRP3_CUSTOM_VOICE=true
CHIRP3_VOICE_CLONING_KEY=your-voice-cloning-key
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

자세한 설정 방법은 [CHIRP3_VOICE_SETUP_GUIDE.md](./CHIRP3_VOICE_SETUP_GUIDE.md)를 참조하세요.

#### 3. `gemini` (Gemini만 사용)
Gemini TTS만 사용합니다. 가장 비용 효율적입니다.

```bash
TTS_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
```

#### 4. `coqui` (Coqui TTS만 사용)
완전 무료 오픈소스 TTS를 사용합니다.

```bash
TTS_PROVIDER=coqui
USE_COQUI_TTS=true
```

## Coqui TTS 설치 (선택적)

Coqui TTS를 사용하려면 다음을 설치하세요:

```bash
# 기본 설치
pip install TTS

# 한국어 지원 포함
pip install TTS[ko]
```

**주의**: Coqui TTS는 초기 모델 다운로드가 필요하며, 디스크 공간을 사용합니다.

## 사용 예시

### 기본 사용 (자동 선택)
```bash
python scripts/generate_enhanced_audio.py
```

### Gemini TTS만 사용
```bash
export TTS_PROVIDER=gemini
python scripts/generate_enhanced_audio.py
```

### Coqui TTS 사용
```bash
export TTS_PROVIDER=coqui
export USE_COQUI_TTS=true
python scripts/generate_enhanced_audio.py
```

## 테스트

### 테스트 스크립트 실행

모든 TTS 제공자를 테스트할 수 있는 스크립트가 포함되어 있습니다:

```bash
python scripts/test_tts_providers.py
```

이 스크립트는 다음을 테스트합니다:
1. **Gemini TTS**: Gemini 2.5 TTS API 테스트 (Chirp 3: Instant Custom Voice 포함)
2. **Coqui TTS**: Coqui TTS 오픈소스 테스트 (설치된 경우)
3. **자동 선택**: auto 모드에서 올바른 제공자 선택 확인

### 테스트 결과 예시

```
============================================================
📊 테스트 결과 요약
============================================================
  GEMINI: ✅ 성공
  COQUI: ❌ 실패 (설치되지 않음)
  AUTO: ✅ 성공

총 테스트: 3
성공: 2
실패: 1
```

**참고**: Coqui TTS는 선택사항이므로 설치되지 않아도 정상입니다. Gemini TTS만으로도 충분히 사용 가능합니다.

## 비용 절감 효과

### 시나리오: 월 10개 대본 생성 (각 2,500자)

**Gemini TTS (Flash 모델)**
- 대본당 약 2,500 토큰 (추정)
- Input: 2,500 × 10 = 25,000 tokens ≈ $0.0000125
- Output: 약간의 오디오 토큰 (추정 50,000 tokens) ≈ $0.0005
- 총 비용: 약 $0.0005/월 (거의 무료)

**결론**: Gemini TTS는 토큰 기반 과금으로 매우 저렴하며, 사용한 만큼만 과금됩니다!

## 보안 고려사항

1. **API 키 관리**: 환경 변수나 시크릿 관리 도구 사용
2. **데이터 프라이버시**: Coqui TTS는 자체 호스팅으로 데이터가 외부로 전송되지 않음
3. **비용 모니터링**: Gemini API 사용량을 정기적으로 확인

## 문제 해결

### Gemini TTS가 작동하지 않는 경우
- Gemini API 키가 올바르게 설정되었는지 확인
- API 할당량 확인 (무료 티어 제한)
- Preview 모델이므로 API 응답 형식이 변경될 수 있음

### Coqui TTS 설치 오류
- Python 3.10 이상, 3.14 미만 필요
- 시스템 의존성 확인 (ffmpeg 등)

## Voice 설정 (IT/DevSecOps 전문가용)

### Gemini TTS Voice 설정

IT, DevSecOps, 클라우드 보안 전문가용 강의 콘텐츠를 위한 목소리 설정:

#### 1. 기본 제공 Voice 사용

```bash
# .env 파일
GEMINI_TTS_VOICE_NAME=Rasalgethi  # 기본값: IT 전문가용 추천
# 다른 옵션: Charon, Iapetus, Orus, Sadaltager 등
```

**권장 Voice:**
- `Rasalgethi`: Informative and professional (기본값, IT 전문가용 추천)
- `Sadaltager`: Knowledgeable and authoritative
- `Charon`, `Iapetus`, `Orus`: 기타 옵션

#### 2. Chirp 3: Instant Custom Voice (자신의 목소리 클로닝)

자신의 목소리를 클로닝하여 사용할 수 있습니다:

```bash
# .env 파일
GEMINI_TTS_VOICE_CLONING_KEY=your-voice-cloning-key
```

**Voice Cloning Key 생성 방법:**
1. Google Cloud Text-to-Speech API 활성화
2. [Chirp 3: Instant Custom Voice 문서](https://docs.cloud.google.com/text-to-speech/docs/chirp3-instant-custom-voice) 참조
3. Voice cloning key 생성 (eu 또는 us 리전 지원)

#### 3. Voice 스타일 및 속도 제어

```bash
# 자연어 프롬프트로 스타일 제어
GEMINI_TTS_VOICE_STYLE=professional and authoritative

# 속도 제어 (0.25 ~ 4.0)
GEMINI_TTS_VOICE_PACE=1.0
```

**Best Practice:**
- 여러 voice 옵션을 테스트하여 가장 적합한 목소리 선택
- 기술 용어 발음 확인 (Kubernetes, DevSecOps 등)
- 1.5배속 재생 시 명확도 확인
- Chirp 3를 사용하면 자신의 목소리로 자연스러운 강의 제작 가능

자세한 내용은 [TTS_VOICE_BEST_PRACTICES.md](./TTS_VOICE_BEST_PRACTICES.md)를 참조하세요.

## 참고 자료

- [Chirp 3: Instant Custom Voice 설정 가이드](./CHIRP3_VOICE_SETUP_GUIDE.md) - 자신의 목소리 클로닝 가이드
- [Gemini TTS API 문서](https://ai.google.dev/gemini-api/docs/speech-generation)
- [Chirp 3: Instant Custom Voice 문서](https://docs.cloud.google.com/text-to-speech/docs/chirp3-instant-custom-voice)
- [Coqui TTS 문서](https://docs.coqui.ai/)
- [TTS_VOICE_BEST_PRACTICES.md](./TTS_VOICE_BEST_PRACTICES.md) - 목소리 생성 Best Practices
