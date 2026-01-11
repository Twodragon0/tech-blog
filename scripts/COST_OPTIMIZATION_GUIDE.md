# 비용 최적화 가이드

ElevenLabs, DeepSeek, Gemini API를 사용할 때 비용을 최적화하는 방법을 안내합니다.

## 💰 API별 가격 정보

### DeepSeek API
- **deepseek-chat**: $0.14 / 1M input tokens, $0.28 / 1M output tokens
- **Context Caching**: 캐시 히트 시 최대 90% 할인
- **Off-Peak 할인**: UTC 16:30-00:30 (한국 시간 01:30-09:30)
  - DeepSeek-R1: 75% 할인
  - DeepSeek-V3: 50% 할인

### Gemini API (Gemini AI Pro)
- **gemini-1.5-pro**: $1.25 / 1M input tokens, $5.00 / 1M output tokens
- **무료 티어**: 월 15 RPM (Requests Per Minute)
- **고급 기능**: 구조화된 출력, 안전 설정, 고품질 생성

### ElevenLabs API
- **무료 티어**: 월 10,000자
- **Starter ($5/월)**: 월 30,000자
- **Creator ($22/월)**: 월 100,000자

## 🎯 비용 최적화 전략

### 1. API 선택 전략

#### 시나리오별 권장 설정

**Gemini AI Pro 우선 (권장) ⭐**
```bash
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
```
- Gemini AI Pro만 사용 (고품질, 구조화된 대본)
- 대본 생성: ~$0.001/포스트 (평균 1000 토큰 기준)
- 개선 단계 생략으로 총 비용 절감

**Gemini AI Pro + DeepSeek 폴백 (균형)**
```bash
export GEMINI_API_KEY='your-key'
export DEEPSEEK_API_KEY='sk-your-key'
export PREFER_GEMINI='true'
```
- Gemini AI Pro 우선, 실패 시 DeepSeek 사용
- 대부분 Gemini 사용: ~$0.001/포스트
- 폴백 시: ~$0.0002/포스트

**DeepSeek + Gemini 개선 (비용 효율)**
```bash
export DEEPSEEK_API_KEY='sk-your-key'
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='false'
export USE_GEMINI_FOR_IMPROVEMENT='true'
```
- DeepSeek으로 생성 + Gemini로 개선
- 대본 생성: ~$0.0005/포스트 (DeepSeek $0.0002 + Gemini $0.0003)

### 2. 캐싱 활용

동일한 포스트를 다시 처리하면 캐시에서 즉시 로드됩니다:

```bash
# 첫 실행: API 호출 (비용 발생)
python3 scripts/generate_enhanced_audio.py post.md

# 두 번째 실행: 캐시에서 로드 (비용 없음)
python3 scripts/generate_enhanced_audio.py post.md
```

**캐시 설정:**
- 기본값: 7일 유효
- 저장 위치: `.cache/audio_generation/`
- 비활성화: `export ENABLE_CACHING='false'`

### 3. 텍스트 길이 제한

긴 포스트는 자동으로 잘립니다:

```python
MAX_TEXT_LENGTH = 50000  # 최대 텍스트 길이
MAX_SCRIPT_LENGTH = 3000  # 최대 대본 길이
```

필요시 스크립트에서 조정 가능합니다.

### 4. Off-Peak 시간대 활용

DeepSeek API는 Off-Peak 시간대에 할인됩니다:

- **할인 시간대**: UTC 16:30-00:30 (한국 시간 01:30-09:30)
- **할인율**: 
  - DeepSeek-R1: 75% 할인
  - DeepSeek-V3: 50% 할인

**권장 작업 시간:**
- 새벽 1시 30분 ~ 오전 9시 30분 (한국 시간)
- 배치 작업을 이 시간대에 실행

### 5. 배치 처리

여러 포스트를 한 번에 처리하면 효율적입니다:

```bash
# 모든 포스트 처리
for post in _posts/*.md; do
    python3 scripts/generate_enhanced_audio.py "$post"
    sleep 2  # API Rate Limit 방지
done
```

### 6. 사용량 모니터링

스크립트 실행 후 자동으로 사용량 통계가 출력됩니다:

```
📊 API 사용량 통계
============================================================

DEEPSEEK:
  요청 수: 10
  총 토큰: 15,000
  Prompt 토큰: 10,000
  Completion 토큰: 5,000
  캐시 히트 토큰: 2,000
  캐시 히트율: 20.0%
  에러 수: 0

예상 비용: $0.0021
```

## 📊 비용 계산 예시

### 시나리오 1: DeepSeek만 사용

**가정:**
- 포스트당 평균 1000 토큰 (input: 700, output: 300)
- 10개 포스트 처리

**비용 계산:**
- Input: 7,000 tokens × $0.14 / 1M = $0.00098
- Output: 3,000 tokens × $0.28 / 1M = $0.00084
- **총 비용: $0.00182**

### 시나리오 2: DeepSeek + Gemini

**가정:**
- DeepSeek: 1000 토큰 (input: 700, output: 300)
- Gemini 개선: 800 토큰 (input: 500, output: 300)
- 10개 포스트 처리

**비용 계산:**
- DeepSeek: $0.00182
- Gemini: (500 × $1.25 / 1M) + (300 × $5.00 / 1M) = $0.000625 + $0.0015 = $0.002125
- **총 비용: $0.003945**

### 시나리오 3: 캐싱 활용

**가정:**
- 10개 포스트 처리 (첫 실행)
- 동일한 10개 포스트 재처리 (캐시 히트)

**비용 계산:**
- 첫 실행: $0.00182
- 재실행: $0 (캐시에서 로드)
- **총 비용: $0.00182 (50% 절감)**

## 💡 비용 절감 팁

### 1. 포스트 요약 후 사용

긴 포스트는 요약 후 사용:

```python
# 원본: 50,000자 → 비용 높음
# 요약: 5,000자 → 비용 낮음
```

### 2. Gemini 개선 선택적 사용

품질이 중요하지 않은 경우 Gemini 개선 비활성화:

```bash
export USE_GEMINI_FOR_IMPROVEMENT='false'
```

### 3. ElevenLabs 할당량 관리

무료 티어는 월 10,000자 제한:
- 짧은 대본 사용 (800-1000자)
- 중요한 포스트만 처리

### 4. 에러 재시도 최소화

에러 발생 시 자동 재시도가 발생하므로:
- 안정적인 네트워크 환경 사용
- API 키 유효성 확인

## 📈 비용 예측

월간 사용량에 따른 예상 비용:

| 포스트 수 | DeepSeek만 | DeepSeek+Gemini | Gemini만 |
|----------|-----------|----------------|----------|
| 10개 | $0.02 | $0.04 | $0.10 |
| 50개 | $0.10 | $0.20 | $0.50 |
| 100개 | $0.20 | $0.40 | $1.00 |

**참고:**
- 포스트당 평균 1000 토큰 기준
- 캐싱 미적용
- Off-Peak 할인 미적용

## 🔍 비용 모니터링

### 1. 로그 파일 확인

```bash
tail -f video_generation_log.txt | grep "토큰"
```

### 2. 사용량 통계 확인

스크립트 실행 후 자동 출력되는 통계 확인

### 3. API 대시보드 확인

- **DeepSeek**: [Platform Dashboard](https://platform.deepseek.com)
- **Gemini**: [Google AI Studio](https://makersuite.google.com)
- **ElevenLabs**: [Usage Page](https://elevenlabs.io/app/usage)

## ⚠️ 주의사항

1. **무료 티어 제한**: 각 API의 무료 티어 제한 확인
2. **Rate Limit**: API Rate Limit 준수
3. **캐시 관리**: 오래된 캐시는 정기적으로 정리
4. **비용 알림**: API 대시보드에서 비용 알림 설정 권장

## 🔗 관련 문서

- [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md)
- [DeepSeek API 최적화 가이드](../DEEPSEEK_API_OPTIMIZATION.md)
- [ElevenLabs 플랫폼 가이드](./ELEVENLABS_PLATFORM_GUIDE.md)

---

**마지막 업데이트**: 2026-01-08
