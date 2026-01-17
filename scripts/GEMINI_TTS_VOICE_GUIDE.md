# Gemini TTS Voice 가이드

## IT 전문가용 남자 목소리 설정

Gemini 2.5 TTS API는 다양한 한국어 남자 목소리를 제공합니다. IT/DevSecOps 전문가용 강의 콘텐츠에 적합한 목소리를 선택하세요.

## 권장 Voice 옵션

### 1. Rasalgethi (기본값, 추천 ⭐)
- **특징**: Informative and professional
- **용도**: IT/DevSecOps 전문가용 강의, 기술 설명
- **장점**: 전문적이고 정보 전달에 적합
- **추천 대상**: 기술 블로그 강의, 온라인 코스

### 2. Sadaltager
- **특징**: Knowledgeable and authoritative
- **용도**: 권위적인 기술 강의, 고급 콘텐츠
- **장점**: 지식이 풍부하고 권위적인 느낌
- **추천 대상**: 고급 기술 세미나, 전문가 강의

### 3. Charon
- **특징**: Informative and clear
- **용도**: 명확한 정보 전달이 중요한 콘텐츠
- **장점**: 명확하고 이해하기 쉬운 발음
- **추천 대상**: 초보자 대상 강의, 튜토리얼

### 4. Iapetus
- **특징**: Clear and articulate
- **용도**: 표현력이 중요한 콘텐츠
- **장점**: 명확하고 표현력 있는 발음
- **추천 대상**: 프레젠테이션, 데모 영상

### 5. Orus
- **특징**: Firm and decisive
- **용도**: 단호하고 결단력 있는 메시지 전달
- **장점**: 확신에 찬 느낌
- **추천 대상**: 보안 강의, 의사결정 관련 콘텐츠

## 설정 방법

### 환경 변수로 설정 (권장)

`.env` 파일에 추가:

```bash
# IT 전문가용 남자 목소리 (기본값: Rasalgethi)
GEMINI_TTS_VOICE_NAME=Rasalgethi
```

### 다른 Voice로 변경

```bash
# 권위적인 목소리
GEMINI_TTS_VOICE_NAME=Sadaltager

# 명확한 목소리
GEMINI_TTS_VOICE_NAME=Charon

# 표현력 있는 목소리
GEMINI_TTS_VOICE_NAME=Iapetus

# 단호한 목소리
GEMINI_TTS_VOICE_NAME=Orus
```

## 사용 예시

### 기본 사용 (Rasalgethi)

```bash
# .env 파일에 설정하지 않으면 기본값(Rasalgethi) 사용
python scripts/generate_enhanced_audio.py
```

### 특정 Voice 지정

```bash
export GEMINI_TTS_VOICE_NAME=Sadaltager
python scripts/generate_enhanced_audio.py
```

### Voice 테스트

```bash
# 여러 Voice로 테스트 생성
python scripts/generate_tts_with_voice.py [대본파일]
```

## Voice 비교

각 Voice의 특징을 비교하여 가장 적합한 목소리를 선택하세요:

| Voice | 특징 | 추천 용도 |
|-------|------|-----------|
| **Rasalgethi** | 전문적이고 정보 전달에 적합 | IT 강의, 기술 블로그 |
| **Sadaltager** | 권위적이고 지식이 풍부한 | 고급 세미나, 전문가 강의 |
| **Charon** | 명확하고 이해하기 쉬운 | 초보자 튜토리얼 |
| **Iapetus** | 표현력 있고 명확한 | 프레젠테이션, 데모 |
| **Orus** | 단호하고 결단력 있는 | 보안 강의, 의사결정 |

## Best Practices

1. **기술 용어 발음 확인**: Kubernetes, DevSecOps 등 전문 용어 발음 테스트
2. **1.5배속 재생 테스트**: 속도 조절 후 명확도 확인
3. **여러 Voice 비교**: 짧은 샘플로 여러 Voice 테스트 후 선택
4. **콘텐츠 유형 고려**: 강의, 튜토리얼, 프레젠테이션 등에 맞는 Voice 선택

## 참고 자료

- [Gemini TTS Voice Library](https://gemini-tts.com/voices) - 모든 Voice 샘플 듣기
- [Gemini TTS API 문서](https://ai.google.dev/gemini-api/docs/speech-generation)
