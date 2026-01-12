# TTS 오픈소스 가이드

## 개요

비용 최적화를 위한 오픈소스 TTS (Text-to-Speech) 옵션 가이드입니다.

## 추천 순위

### 1순위: Edge-TTS (Microsoft Edge TTS)

**장점:**
- ✅ 완전 무료
- ✅ API 키 불필요
- ✅ 한국어 지원 우수
- ✅ 설치 간단
- ✅ 품질 우수

**단점:**
- 인터넷 연결 필요 (온라인 서비스)

**설치:**
```bash
pip install edge-tts
```

**사용법:**
```python
import edge_tts

# 한국어 음성 선택
voice = "ko-KR-SunHiNeural"  # 여성 음성
# 또는 "ko-KR-InJoonNeural"  # 남성 음성

# 음성 생성
communicate = edge_tts.Communicate("안녕하세요, 테스트입니다.", voice)
communicate.save("output.mp3")
```

**사용 가능한 한국어 음성 확인:**
```bash
edge-tts --list-voices | grep ko-KR
```

**출력:**
```
ko-KR-SunHiNeural    Female    한국어 (대한민국)
ko-KR-InJoonNeural   Male      한국어 (대한민국)
ko-KR-BongJinNeural  Male      한국어 (대한민국)
```

---

### 2순위: Coqui TTS

**장점:**
- ✅ 완전 무료 (로컬 실행)
- ✅ 오프라인 작동 가능
- ✅ 한국어 지원
- ✅ 고품질 음성

**단점:**
- 모델 다운로드 필요 (첫 실행 시)
- 메모리 사용량 높음

**설치:**
```bash
pip install TTS
```

**사용법:**
```python
from TTS.api import TTS

# 한국어 모델 초기화 (첫 실행 시 자동 다운로드)
tts = TTS(model_name="tts_models/ko/common-glow_tts", progress_bar=False)

# 음성 생성
tts.tts_to_file(text="안녕하세요, 테스트입니다.", file_path="output.mp3")
```

**지원 모델:**
- `tts_models/ko/common-glow_tts`: 기본 한국어 모델
- `tts_models/multilingual/multi-dataset/your_tts`: 다국어 모델

---

### 3순위: ElevenLabs (유료)

**장점:**
- ✅ 최고 품질
- ✅ 다양한 음성 선택
- ✅ 감정 표현 가능

**단점:**
- 유료 (월 10,000자 무료)
- API 키 필요

**사용법:**
```python
import requests

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json"
}
data = {
    "text": "안녕하세요, 테스트입니다.",
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75
    }
}

response = requests.post(url, json=data, headers=headers)
with open("output.mp3", "wb") as f:
    f.write(response.content)
```

---

## 통합 사용 예제

`generate_enhanced_audio.py` 스크립트는 자동으로 다음 순서로 TTS를 시도합니다:

1. **Edge-TTS** (무료, API 키 불필요)
2. **Coqui TTS** (로컬, 완전 무료)
3. **ElevenLabs** (유료, 최고 품질)
4. **Gemini TTS** (유료, 폴백)

```bash
# Edge-TTS 사용 (권장)
python3 scripts/generate_enhanced_audio.py _posts/2026-01-12-Post.md

# 특정 TTS 방법 강제 사용 (환경 변수)
export PREFER_EDGE_TTS="true"
python3 scripts/generate_enhanced_audio.py _posts/2026-01-12-Post.md
```

---

## 성능 비교

| TTS | 품질 | 속도 | 비용 | 오프라인 | 한국어 |
|-----|------|------|------|----------|--------|
| Edge-TTS | ⭐⭐⭐⭐ | 빠름 | 무료 | ❌ | ✅ |
| Coqui TTS | ⭐⭐⭐⭐ | 보통 | 무료 | ✅ | ✅ |
| ElevenLabs | ⭐⭐⭐⭐⭐ | 빠름 | 유료 | ❌ | ✅ |
| Gemini TTS | ⭐⭐⭐ | 보통 | 유료 | ❌ | ✅ |

---

## 권장 설정

### 개발 환경
```bash
# Edge-TTS 설치 (가장 간단)
pip install edge-tts

# 테스트
edge-tts --text "안녕하세요" --write-media test.mp3
```

### 프로덕션 환경
```bash
# Edge-TTS + Coqui TTS 모두 설치 (폴백 옵션)
pip install edge-tts TTS

# Coqui TTS 모델 사전 다운로드
python3 -c "from TTS.api import TTS; TTS(model_name='tts_models/ko/common-glow_tts')"
```

---

## 문제 해결

### Edge-TTS 오류
```bash
# 재설치
pip uninstall edge-tts
pip install edge-tts

# 음성 목록 확인
edge-tts --list-voices
```

### Coqui TTS 메모리 부족
```bash
# 모델 크기 확인
du -sh ~/.local/share/tts/

# 더 작은 모델 사용
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")
```

---

## 참고 자료

- [Edge-TTS GitHub](https://github.com/rany2/edge-tts)
- [Coqui TTS 문서](https://github.com/coqui-ai/TTS)
- [ElevenLabs API 문서](https://elevenlabs.io/docs/api-reference/text-to-speech)
