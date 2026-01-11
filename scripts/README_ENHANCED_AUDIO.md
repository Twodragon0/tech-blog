# 개선된 오디오/영상 생성 가이드

DeepSeek API와 Gemini API를 적절히 활용하여 비용 효율화, 최적화, 보안을 모두 고려한 통합 시스템입니다.

## 🎯 주요 개선 사항

### 1. API 선택적 활용
- **Gemini AI Pro**: 대본 생성 및 개선 (고품질, 우선 사용) ⭐
- **DeepSeek API**: 대본 생성 (비용 효율적, 폴백 옵션)
- **ElevenLabs API**: 음성 생성

### 2. 비용 최적화
- **캐싱 시스템**: 동일한 포스트는 캐시에서 재사용 (7일 유효)
- **API 선택 전략**: 작업 유형에 따라 적절한 API 선택
- **사용량 모니터링**: 실시간 토큰 사용량 및 비용 추적
- **배치 처리**: 여러 포스트를 효율적으로 처리

### 3. 보안 강화
- **API 키 관리**: 환경 변수만 사용, 절대 코드에 하드코딩하지 않음
- **민감 정보 마스킹**: 로그에 API 키 자동 마스킹
- **입력 검증**: 모든 입력 데이터 검증
- **에러 핸들링**: 상세한 에러 로깅 및 안전한 실패 처리

### 4. 품질 향상
- **Gemini AI Pro 우선**: 고품질 대본 생성 (구조화된 서론-본론-결론)
- **2단계 대본 생성**: DeepSeek으로 생성 → Gemini로 개선 (선택적)
- **고급 프롬프트**: Gemini AI Pro의 고급 기능 활용
- **자동 재시도**: 네트워크 오류 시 자동 재시도 (지수 백오프)
- **캐시 활용**: 동일한 작업 반복 시 즉시 응답

## 📋 사전 요구사항

### 1. API 키 준비

다음 API 키 중 필요한 것만 설정하면 됩니다:

#### 필수
- **ElevenLabs API Key**: [ElevenLabs Platform](https://elevenlabs.io)에서 발급
- **ElevenLabs Voice ID**: ElevenLabs에서 Voice ID 확인

#### 선택 (최소 하나 필요)
- **Gemini API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급 (권장, Gemini AI Pro 사용) ⭐
- **DeepSeek API Key**: [DeepSeek Platform](https://platform.deepseek.com)에서 발급 (비용 효율적, 폴백 옵션)

### 2. 환경 변수 설정

로컬 테스트 시:

```bash
# 필수
export ELEVENLABS_API_KEY='your-elevenlabs-api-key'
export ELEVENLABS_VOICE_ID='your-voice-id'

# 선택 (최소 하나)
export DEEPSEEK_API_KEY='sk-your-deepseek-api-key'  # 권장
export GEMINI_API_KEY='your-gemini-api-key'  # 선택적

# 고급 설정 (선택)
export PREFER_GEMINI='true'  # Gemini AI Pro 우선 사용 (기본값: true) ⭐
export USE_GEMINI_CLI='false'  # Gemini CLI 사용 (기본값: false, OAuth 2.0 지원) ⭐
export USE_DEEPSEEK_FOR_SCRIPT='true'  # DeepSeek으로 대본 생성 (기본값: true)
export USE_GEMINI_FOR_SCRIPT='true'  # Gemini AI Pro로 대본 생성 (기본값: true) ⭐
export USE_GEMINI_FOR_IMPROVEMENT='true'  # Gemini로 대본 개선 (기본값: true)
export ENABLE_CACHING='true'  # 캐싱 활성화 (기본값: true)

# OAuth 2.0 설정 (선택, 서비스 계정 사용)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GOOGLE_CLOUD_PROJECT="your-project-id"
export USE_GEMINI_OAUTH='true'  # OAuth 2.0 사용 (기본값: false)
```

GitHub Actions 사용 시:

1. GitHub 저장소 → **Settings** → **Secrets and variables** → **Actions**
2. 다음 Secrets 추가:
   - `ELEVENLABS_API_KEY` (필수)
   - `ELEVENLABS_VOICE_ID` (필수)
   - `DEEPSEEK_API_KEY` (권장)
   - `GEMINI_API_KEY` (선택적)

## 🚀 사용 방법

### 기본 사용 (최신 포스트)

```bash
python3 scripts/generate_enhanced_audio.py
```

### 특정 포스트 지정

```bash
python3 scripts/generate_enhanced_audio.py 2026-01-10-example.md
```

### 결과 확인

생성된 파일은 `output/` 디렉토리에 저장됩니다:
- `{포스트명}_audio.mp3`: 생성된 오디오 파일

## ⚙️ API 선택 전략

### 시나리오 1: Gemini AI Pro만 사용 (권장) ⭐

```bash
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='false'
```

- ✅ 최고 품질 (Gemini AI Pro의 고급 기능 활용)
- ✅ 구조화된 대본 생성 (서론-본론-결론)
- ✅ 자연스러운 구어체
- ✅ 자동 개선 단계 생략 (이미 고품질)

### 시나리오 2: Gemini AI Pro + DeepSeek 폴백 (균형)

```bash
export GEMINI_API_KEY='your-key'
export DEEPSEEK_API_KEY='sk-your-key'
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='true'
```

- ✅ Gemini AI Pro 우선 사용 (고품질)
- ✅ DeepSeek 폴백 (Gemini 실패 시)
- ✅ 최적의 균형

### 시나리오 3: DeepSeek + Gemini 개선 (비용 효율)

```bash
export DEEPSEEK_API_KEY='sk-your-key'
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='false'
export USE_DEEPSEEK_FOR_SCRIPT='true'
export USE_GEMINI_FOR_IMPROVEMENT='true'
```

- ✅ 비용 효율적 (DeepSeek으로 생성)
- ✅ 높은 품질 (Gemini로 개선)
- ⚠️ 2단계 처리로 시간 소요

## 💰 비용 최적화 팁

### 1. 캐싱 활용

동일한 포스트를 다시 처리하면 캐시에서 즉시 로드됩니다:

```bash
# 첫 실행: API 호출
python3 scripts/generate_enhanced_audio.py post.md

# 두 번째 실행: 캐시에서 로드 (API 호출 없음)
python3 scripts/generate_enhanced_audio.py post.md
```

캐시는 7일간 유효하며, `.cache/audio_generation/` 디렉토리에 저장됩니다.

### 2. 사용량 모니터링

스크립트 실행 후 자동으로 사용량 통계가 출력됩니다:

```
📊 API 사용량 통계
============================================================

DEEPSEEK:
  요청 수: 1
  총 토큰: 1500
  Prompt 토큰: 1000
  Completion 토큰: 500
  캐시 히트 토큰: 0
  캐시 히트율: 0.0%
  에러 수: 0

GEMINI:
  요청 수: 1
  총 토큰: 800
  Prompt 토큰: 500
  Completion 토큰: 300
  에러 수: 0
```

### 3. 배치 처리

여러 포스트를 한 번에 처리하려면 스크립트를 수정하거나 루프로 실행:

```bash
for post in _posts/*.md; do
    python3 scripts/generate_enhanced_audio.py "$post"
done
```

### 4. Off-Peak 시간대 활용

DeepSeek API는 Off-Peak 시간대(UTC 16:30-00:30)에 할인됩니다:
- DeepSeek-R1: 75% 할인
- DeepSeek-V3: 50% 할인

가능한 경우 Off-Peak 시간대에 배치 작업을 실행하세요.

## 🔒 보안 고려사항

### 1. API 키 보호

- ✅ 모든 API 키는 환경 변수에서만 읽음
- ✅ 로그에 자동 마스킹
- ✅ Git에 커밋하지 않음 (`.gitignore`에 포함)

### 2. 입력 검증

- ✅ 텍스트 길이 제한 (50,000자)
- ✅ 대본 길이 제한 (3,000자)
- ✅ 파일 존재 여부 확인

### 3. 에러 핸들링

- ✅ 모든 API 호출에 타임아웃 설정
- ✅ 자동 재시도 (최대 3회, 지수 백오프)
- ✅ 상세한 에러 로깅

## 📊 성능 비교

| 방법 | 대본 생성 시간 | 비용 | 품질 |
|------|---------------|------|------|
| DeepSeek만 | ~2-3초 | 낮음 | 보통 |
| DeepSeek + Gemini | ~5-7초 | 중간 | 높음 |
| Gemini만 | ~3-5초 | 높음 | 매우 높음 |

## 🐛 문제 해결

### API 키 오류

```
❌ 필수 환경 변수가 설정되지 않았습니다: DEEPSEEK_API_KEY
```

**해결 방법:**
1. 환경 변수 확인: `echo $DEEPSEEK_API_KEY`
2. GitHub Secrets 확인: Settings → Secrets and variables → Actions

### 캐시 문제

캐시를 초기화하려면:

```bash
rm -rf .cache/audio_generation/*
```

### 사용량 모니터링

사용량 통계는 스크립트 실행 후 자동으로 출력됩니다. 더 자세한 정보는 로그 파일을 확인하세요:

```bash
tail -f video_generation_log.txt
```

## 📝 설정 파일

환경 변수 대신 설정 파일을 사용하려면 `.env` 파일을 생성:

```bash
# .env 파일
ELEVENLABS_API_KEY=your-key
ELEVENLABS_VOICE_ID=your-voice-id
DEEPSEEK_API_KEY=sk-your-key
GEMINI_API_KEY=your-key
USE_DEEPSEEK_FOR_SCRIPT=true
USE_GEMINI_FOR_IMPROVEMENT=true
ENABLE_CACHING=true
```

그리고 스크립트 실행 전에 로드:

```bash
export $(cat .env | xargs)
python3 scripts/generate_enhanced_audio.py
```

## 🔗 관련 문서

- [ElevenLabs 플랫폼 가이드](./ELEVENLABS_PLATFORM_GUIDE.md)
- [내 목소리 설정 가이드](./MY_VOICE_SETUP_GUIDE.md)
- [DeepSeek API 최적화 가이드](../DEEPSEEK_API_OPTIMIZATION.md)
- [Gemini 이미지 생성 가이드](../GEMINI_IMAGE_GUIDE.md)
- [비디오 생성 가이드](./README_VIDEO_GENERATION.md)

## ⚠️ 주의사항

1. **비용 관리**: API 사용량을 모니터링하고 필요시 제한을 설정하세요.
2. **캐시 관리**: 캐시 디렉토리는 정기적으로 정리하세요 (7일 이상 된 캐시는 자동으로 무효화).
3. **API 키 보안**: 절대 Git에 API 키를 커밋하지 마세요.
4. **할당량 제한**: 무료 티어는 제한이 있을 수 있습니다. 사용량을 확인하세요.

## 💡 향후 개선 계획

- [ ] Gemini를 활용한 이미지 자동 생성
- [ ] 배치 처리 최적화
- [ ] 더 정교한 캐싱 전략
- [ ] 비용 예측 기능
- [ ] 자동 품질 평가

---

**마지막 업데이트**: 2026-01-08
