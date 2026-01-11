# ElevenLabs + DeepSeek + Gemini 통합 가이드

ElevenLabs, DeepSeek, Gemini API를 통합하여 비용 효율적이고 고품질의 오디오/영상 생성 시스템을 구축하는 가이드입니다.

## 🎯 시스템 개요

```
블로그 포스팅
    ↓
[1] 텍스트 정제 (마크다운 → 순수 텍스트)
    ↓
[2] 대본 생성 (DeepSeek API - 비용 효율적)
    ↓
[3] 대본 개선 (Gemini API - 선택적, 품질 향상)
    ↓
[4] 음성 생성 (ElevenLabs API)
    ↓
[5] 영상 생성 (Remotion 또는 FFmpeg)
    ↓
최종 영상 파일
```

## 📋 전체 워크플로우

### 1단계: 환경 설정

```bash
# 필수 API 키
export ELEVENLABS_API_KEY='your-key'
export ELEVENLABS_VOICE_ID='your-voice-id'

# 선택적 API 키 (최소 하나 필요)
export DEEPSEEK_API_KEY='sk-your-key'  # 권장
export GEMINI_API_KEY='your-key'  # 선택적

# 고급 설정
export USE_DEEPSEEK_FOR_SCRIPT='true'
export USE_GEMINI_FOR_IMPROVEMENT='true'
export ENABLE_CACHING='true'
```

### 2단계: 오디오 생성

```bash
# 개선된 스크립트 사용 (권장)
python3 scripts/generate_enhanced_audio.py

# 또는 특정 포스트 지정
python3 scripts/generate_enhanced_audio.py 2026-01-10-example.md
```

### 3단계: 영상 생성 (선택적)

```bash
# Remotion 사용 (권장)
python3 scripts/generate_video_with_remotion.py

# 또는 FFmpeg 사용
ffmpeg -loop 1 -i thumbnail.jpg -i audio.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest output.mp4
```

## 🔄 API 선택 전략

### 전략 1: Gemini AI Pro 우선 (권장) ⭐

**설정:**
```bash
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='false'
```

**특징:**
- ✅ 최고 품질 (구조화된 대본)
- ✅ 자연스러운 구어체
- ✅ 1단계 처리 (빠름)
- ✅ 자동 개선 불필요

**비용:** ~$0.001/포스트

### 전략 2: Gemini AI Pro + DeepSeek 폴백 (권장)

**설정:**
```bash
export GEMINI_API_KEY='your-key'
export DEEPSEEK_API_KEY='sk-your-key'
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='true'
```

**특징:**
- ✅ Gemini AI Pro 우선 (고품질)
- ✅ DeepSeek 폴백 (안정성)
- ✅ 최적의 균형

**비용:** ~$0.001/포스트 (Gemini), ~$0.0002/포스트 (DeepSeek 폴백)

### 전략 3: DeepSeek + Gemini 개선 (비용 효율)

**설정:**
```bash
export DEEPSEEK_API_KEY='sk-your-key'
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='false'
export USE_DEEPSEEK_FOR_SCRIPT='true'
export USE_GEMINI_FOR_IMPROVEMENT='true'
```

**특징:**
- ✅ 비용 효율적
- ✅ 높은 품질 (2단계 처리)
- ⚠️ 처리 시간 증가

**비용:** ~$0.0005/포스트

## 💰 비용 관리

### 캐싱 활용

동일한 포스트를 다시 처리하면 캐시에서 즉시 로드:

```bash
# 첫 실행: API 호출 (비용 발생)
python3 scripts/generate_enhanced_audio.py post.md

# 재실행: 캐시에서 로드 (비용 없음)
python3 scripts/generate_enhanced_audio.py post.md
```

### 사용량 모니터링

스크립트 실행 후 자동으로 통계 출력:

```
📊 API 사용량 통계
============================================================

DEEPSEEK:
  요청 수: 1
  총 토큰: 1,500
  예상 비용: $0.000210

GEMINI:
  요청 수: 1
  총 토큰: 800
  예상 비용: $0.002125

💰 총 예상 비용: $0.002335
```

자세한 내용은 [비용 최적화 가이드](./COST_OPTIMIZATION_GUIDE.md)를 참조하세요.

## 🔒 보안 고려사항

### API 키 관리

1. **환경 변수 사용**: 절대 코드에 하드코딩하지 않음
2. **로그 마스킹**: 모든 로그에 API 키 자동 마스킹
3. **Git 제외**: `.gitignore`에 API 키 파일 포함

### 입력 검증

- 텍스트 길이 제한 (50,000자)
- 대본 길이 제한 (3,000자)
- 파일 존재 여부 확인

### 에러 핸들링

- 모든 API 호출에 타임아웃 설정
- 자동 재시도 (최대 3회, 지수 백오프)
- 상세한 에러 로깅

## 📊 성능 비교

| 방법 | 대본 생성 시간 | 비용/포스트 | 품질 |
|------|---------------|-----------|------|
| DeepSeek만 | ~2-3초 | $0.0002 | 보통 |
| DeepSeek + Gemini | ~5-7초 | $0.0005 | 높음 |
| Gemini만 | ~3-5초 | $0.001 | 매우 높음 |

## 🚀 고급 사용법

### 배치 처리

여러 포스트를 한 번에 처리:

```bash
for post in _posts/*.md; do
    python3 scripts/generate_enhanced_audio.py "$post"
    sleep 2  # Rate Limit 방지
done
```

### Off-Peak 시간대 활용

DeepSeek API는 Off-Peak 시간대(한국 시간 01:30-09:30)에 할인:

```bash
# 새벽에 배치 작업 실행
0 2 * * * cd /path/to/blog && python3 scripts/generate_enhanced_audio.py
```

### 캐시 관리

캐시 초기화:

```bash
rm -rf .cache/audio_generation/*
```

캐시 비활성화:

```bash
export ENABLE_CACHING='false'
```

## 🔗 관련 문서

- [Gemini AI Pro 활용 가이드](./GEMINI_AI_PRO_GUIDE.md) ⭐ **권장**
- [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md)
- [비용 최적화 가이드](./COST_OPTIMIZATION_GUIDE.md)
- [ElevenLabs 플랫폼 가이드](./ELEVENLABS_PLATFORM_GUIDE.md)
- [내 목소리 설정 가이드](./MY_VOICE_SETUP_GUIDE.md)
- [DeepSeek API 최적화 가이드](../DEEPSEEK_API_OPTIMIZATION.md)
- [Gemini 이미지 생성 가이드](../GEMINI_IMAGE_GUIDE.md)
- [Remotion 영상 생성 가이드](./README_REMOTION.md)

## ⚠️ 주의사항

1. **비용 관리**: API 사용량을 모니터링하고 필요시 제한 설정
2. **Rate Limit**: API Rate Limit 준수
3. **캐시 관리**: 오래된 캐시는 정기적으로 정리
4. **API 키 보안**: 절대 Git에 커밋하지 않음

## 💡 팁

1. **처음에는 짧은 포스트로 테스트**: 비용과 시간 절약
2. **캐싱 활용**: 동일한 포스트 재처리 시 즉시 응답
3. **Off-Peak 시간대 활용**: DeepSeek API 할인 혜택
4. **사용량 모니터링**: 정기적으로 통계 확인

---

**마지막 업데이트**: 2026-01-08
