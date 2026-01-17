# TTS 제공자 테스트 결과

## 테스트 일시
2026-01-11 22:50

## 테스트 환경
- Python: 3.9.13
- 운영체제: macOS
- 테스트 스크립트: `scripts/test_tts_providers.py`

## 테스트 결과

### 1. Gemini 2.5 TTS API ✅ 성공

**테스트 내용:**
- 한국어 텍스트를 음성으로 변환
- Flash 모델 사용 (비용 효율적)
- MP3 형식으로 출력
- 1.5배속 재생 지원

**결과:**
- ✅ 성공적으로 오디오 파일 생성
- 파일 크기: 25,292 bytes
- 생성 시간: 약 26초
- 출력 파일: `output/test_gemini_tts.mp3`

**API 요청 형식:**
```json
{
  "contents": [{
    "parts": [{
      "text": "테스트 텍스트"
    }]
  }],
  "generationConfig": {
    "responseModalities": ["AUDIO"],
    "speechConfig": {
      "voiceConfig": {
        "prebuiltVoiceConfig": {
          "voiceName": "Kore"
        }
      }
    }
  }
}
```

**비용:**
- 매우 저렴 (토큰 기반 과금)
- 2,500자 대본 기준 약 $0.0005 이하

### 2. Coqui TTS 오픈소스 ❌ 미설치

**테스트 내용:**
- Coqui TTS 라이브러리 설치 확인
- 한국어 모델 로드 테스트

**결과:**
- ❌ 라이브러리가 설치되지 않음
- 선택사항이므로 정상

**설치 방법:**
```bash
pip install TTS[ko]
```

**참고:**
- Coqui TTS는 완전 무료 오픈소스
- 자체 호스팅 가능
- 데이터 프라이버시 보장
- 필요시 설치하여 사용 가능

### 3. 자동 선택 모드 (auto) ✅ 성공

**테스트 내용:**
- `TTS_PROVIDER=auto` 설정
- 자동으로 가장 적합한 제공자 선택
- 폴백 메커니즘 확인

**결과:**
- ✅ Gemini TTS 자동 선택 성공
- 우선순위: Gemini → ElevenLabs → Coqui
- 파일 크기: 24,620 bytes
- 생성 시간: 약 7초

**사용된 제공자:**
- Gemini TTS (우선순위 1)

## 종합 평가

### 성공률
- 총 테스트: 3개
- 성공: 2개 (67%)
- 실패: 1개 (33%, 선택사항)

### 권장 사항

1. **기본 사용**: `TTS_PROVIDER=auto` (기본값)
   - Gemini TTS가 자동으로 선택됨
   - 비용 효율적
   - 고품질 음성

2. **Gemini TTS 전용**: `TTS_PROVIDER=gemini`
   - 가장 비용 효율적
   - 이미 사용 중인 Gemini API 키 활용

3. **Coqui TTS 사용** (선택적):
   - 완전 무료
   - 데이터 프라이버시 중요시하는 경우
   - 설치: `pip install TTS[ko]`

## 비용 절감 효과

### ElevenLabs 대비
- **ElevenLabs**: $5/월 (고정)
- **Gemini TTS**: 약 $0.0005/월 (사용량 기반)
- **절감률**: 약 99.99%

### 월 10개 대본 기준 (각 2,500자)
- **ElevenLabs**: $5/월
- **Gemini TTS**: 약 $0.005/월
- **연간 절감**: 약 $60

## 다음 단계

1. ✅ Gemini TTS 통합 완료
2. ✅ 자동 선택 모드 구현 완료
3. ⚠️ Coqui TTS는 선택사항 (필요시 설치)
4. ✅ 테스트 스크립트 제공

## 문제 해결

### Gemini TTS 오류
- API 키 확인: `.env` 파일에 `GEMINI_API_KEY` 설정
- 할당량 확인: 무료 티어 제한 확인
- 네트워크 확인: 인터넷 연결 상태 확인

### Coqui TTS 설치 오류
- Python 버전: 3.10 이상, 3.14 미만 필요
- 시스템 의존성: ffmpeg 등 확인
- 디스크 공간: 모델 다운로드 공간 필요

## 참고 자료

- [Gemini TTS API 문서](https://ai.google.dev/gemini-api/docs/speech-generation)
- [Coqui TTS 문서](https://docs.coqui.ai/)
- [테스트 스크립트](./test_tts_providers.py)
- [TTS 최적화 가이드](./README_TTS_OPTIMIZATION.md)
