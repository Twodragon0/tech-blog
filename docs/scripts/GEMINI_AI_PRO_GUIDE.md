# Gemini AI Pro 활용 가이드

Gemini AI Pro를 적극 활용하여 고품질 오디오/영상 콘텐츠를 생성하는 가이드입니다.

## 🎯 Gemini AI Pro의 강점

### 1. 고품질 대본 생성
- **구조화된 출력**: 서론-본론-결론 구조 자동 생성
- **자연스러운 구어체**: 강의자 말투처럼 자연스러운 표현
- **맥락 이해**: 블로그 내용을 정확하게 이해하고 요약

### 2. 고급 기능
- **Safety Settings**: 안전한 콘텐츠 생성 보장
- **Temperature 조절**: 창의성과 일관성의 균형
- **구조화된 프롬프트**: 단계별 가이드에 따른 정확한 출력

### 3. 비용 효율성
- **1단계 처리**: 대본 생성과 개선을 한 번에 처리
- **고품질 출력**: 추가 개선 단계 불필요
- **캐싱 활용**: 동일한 포스트 재처리 시 비용 없음

## 🚀 권장 설정

### 기본 설정 (Gemini AI Pro 우선)

```bash
# 필수
export ELEVENLABS_API_KEY='your-key'
export ELEVENLABS_VOICE_ID='your-voice-id'
export GEMINI_API_KEY='your-key'

# Gemini AI Pro 우선 설정
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='false'  # Gemini만 사용
export USE_GEMINI_FOR_IMPROVEMENT='false'  # 이미 고품질이므로 개선 불필요
```

### 폴백 설정 (Gemini + DeepSeek)

```bash
# 필수
export ELEVENLABS_API_KEY='your-key'
export ELEVENLABS_VOICE_ID='your-voice-id'
export GEMINI_API_KEY='your-key'
export DEEPSEEK_API_KEY='sk-your-key'

# Gemini 우선, DeepSeek 폴백
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='true'  # 폴백 활성화
export USE_GEMINI_FOR_IMPROVEMENT='false'  # Gemini로 생성 시 개선 불필요
```

## 📊 사용 시나리오

### 시나리오 1: Gemini AI Pro만 사용 (권장) ⭐

**특징:**
- ✅ 최고 품질
- ✅ 구조화된 대본 (서론-본론-결론)
- ✅ 자연스러운 구어체
- ✅ 1단계 처리 (빠름)

**비용:** ~$0.001/포스트

**설정:**
```bash
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='false'
export USE_GEMINI_FOR_IMPROVEMENT='false'
```

### 시나리오 2: Gemini AI Pro + DeepSeek 폴백

**특징:**
- ✅ Gemini AI Pro 우선 (고품질)
- ✅ DeepSeek 폴백 (안정성)
- ✅ 비용 효율적 (대부분 Gemini 사용)

**비용:** ~$0.001/포스트 (Gemini 사용 시), ~$0.0002/포스트 (DeepSeek 폴백 시)

**설정:**
```bash
export GEMINI_API_KEY='your-key'
export DEEPSEEK_API_KEY='sk-your-key'
export PREFER_GEMINI='true'
export USE_GEMINI_FOR_SCRIPT='true'
export USE_DEEPSEEK_FOR_SCRIPT='true'
```

### 시나리오 3: DeepSeek + Gemini 개선

**특징:**
- ✅ 비용 효율적 (DeepSeek으로 생성)
- ✅ 높은 품질 (Gemini로 개선)
- ⚠️ 2단계 처리 (시간 소요)

**비용:** ~$0.0005/포스트

**설정:**
```bash
export DEEPSEEK_API_KEY='sk-your-key'
export GEMINI_API_KEY='your-key'
export PREFER_GEMINI='false'
export USE_DEEPSEEK_FOR_SCRIPT='true'
export USE_GEMINI_FOR_IMPROVEMENT='true'
```

## 🎨 Gemini AI Pro 프롬프트 구조

### 대본 생성 프롬프트

현재 사용 중인 고급 프롬프트 구조:

```
1. 서론 (10-15초)
   - 인사말과 주제 소개

2. 본론 (4-4.5분)
   - 핵심 내용 단계별 설명
   - 구어체 사용
   - 실무 예시/비유

3. 결론 (10-15초)
   - 핵심 내용 요약
   - 마무리 인사
```

### 개선 프롬프트

대본 개선 시 사용하는 프롬프트:

```
1. 자연스러운 구어체 유지
2. 핵심 내용 보존
3. 표현 개선
4. 흐름 개선
5. 몰입도 향상
6. 길이 유지
```

## 💡 최적화 팁

### 1. 캐싱 활용

Gemini AI Pro로 생성한 대본은 캐시에 저장됩니다:

```bash
# 첫 실행: Gemini AI Pro 호출
python3 scripts/generate_enhanced_audio.py post.md

# 재실행: 캐시에서 로드 (비용 없음)
python3 scripts/generate_enhanced_audio.py post.md
```

### 2. 배치 처리

여러 포스트를 한 번에 처리:

```bash
for post in _posts/*.md; do
    python3 scripts/generate_enhanced_audio.py "$post"
    sleep 2  # Rate Limit 방지
done
```

### 3. Rate Limit 관리

Gemini API는 월 15 RPM 제한이 있습니다:
- 배치 처리 시 적절한 대기 시간 설정
- 중요 포스트만 우선 처리

## 📈 성능 비교

| 방법 | 품질 | 비용/포스트 | 처리 시간 | 권장도 |
|------|------|-----------|----------|--------|
| Gemini AI Pro만 | ⭐⭐⭐⭐⭐ | $0.001 | ~3-5초 | ⭐⭐⭐⭐⭐ |
| Gemini + DeepSeek 폴백 | ⭐⭐⭐⭐⭐ | $0.001 | ~3-5초 | ⭐⭐⭐⭐ |
| DeepSeek + Gemini 개선 | ⭐⭐⭐⭐ | $0.0005 | ~5-7초 | ⭐⭐⭐ |
| DeepSeek만 | ⭐⭐⭐ | $0.0002 | ~2-3초 | ⭐⭐ |

## 🔒 보안 고려사항

### Safety Settings

Gemini AI Pro는 자동으로 안전 설정을 적용합니다:

- **HARASSMENT**: 중간 이상 차단
- **HATE_SPEECH**: 중간 이상 차단
- **SEXUALLY_EXPLICIT**: 중간 이상 차단
- **DANGEROUS_CONTENT**: 중간 이상 차단

### API 키 보안

- ✅ 환경 변수만 사용
- ✅ 로그에 자동 마스킹
- ✅ Git에 커밋하지 않음

## 🐛 문제 해결

### Gemini API 오류

```
❌ Gemini API 오류: HTTP 429
```

**해결 방법:**
1. Rate Limit 확인: 월 15 RPM 제한
2. 대기 시간 추가: `sleep 2` 추가
3. 중요 포스트만 우선 처리

### 대본 품질 문제

```
생성된 대본이 너무 짧거나 길다
```

**해결 방법:**
1. 프롬프트에 길이 명시: "약 800-1000자"
2. `MAX_SCRIPT_LENGTH` 조정: 스크립트에서 설정 변경
3. Gemini AI Pro의 구조화된 프롬프트 활용

## 🔗 관련 문서

- [개선된 오디오 생성 가이드](./README_ENHANCED_AUDIO.md)
- [비용 최적화 가이드](./COST_OPTIMIZATION_GUIDE.md)
- [통합 가이드](./INTEGRATION_GUIDE.md)
- [Gemini 이미지 생성 가이드](../GEMINI_IMAGE_GUIDE.md)

## ⚠️ 주의사항

1. **Rate Limit**: Gemini API는 월 15 RPM 제한이 있습니다.
2. **비용 관리**: Gemini AI Pro는 DeepSeek보다 비용이 높지만 품질이 우수합니다.
3. **캐싱 활용**: 동일한 포스트 재처리 시 캐시를 활용하여 비용 절감

## 💡 권장 사항

1. **Gemini AI Pro 우선 사용**: 최고 품질을 위해 Gemini AI Pro를 우선 사용
2. **DeepSeek 폴백**: 안정성을 위해 DeepSeek을 폴백으로 설정
3. **캐싱 활성화**: 비용 절감을 위해 캐싱 활성화
4. **배치 처리**: 여러 포스트를 한 번에 처리하여 효율성 향상

---

**마지막 업데이트**: 2026-01-08
