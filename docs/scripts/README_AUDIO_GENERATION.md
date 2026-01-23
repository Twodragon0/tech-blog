# 개선된 대본 기반 오디오 생성 가이드

## 개요

개선된 대본 파일(`*_improved.txt`)을 기반으로 IT 전문가용 남자 목소리(Rasalgethi)로 오디오를 생성합니다.

## 생성된 파일

### 개선된 대본 파일
- `*_improved.txt`: 오디오 품질 및 Remotion 동기화를 위해 개선된 대본
- `*_segments.json`: Remotion 동기화를 위한 구간 정보

### 생성된 오디오 파일
- `*_audio_improved.mp3`: 개선된 대본 기반 오디오 (IT 전문가용 남자 목소리)

## 사용 방법

### 1. 특정 대본으로 오디오 생성

```bash
# 분할 생성 (긴 대본 권장)
python scripts/generate_audio_from_improved_split.py output/2025-05-23-클라우드_시큐리티_과정_7기_-_6주차_Cloudflare_및_github_보안_script_improved.txt

# 직접 생성 (짧은 대본)
python scripts/generate_audio_from_improved_scripts.py output/2025-04-29-SKT_보안_이슈_완벽_대응_가이드_IMEI_확인_USIMeSIM_교체_그리고_MFA의_중요성_script_improved.txt
```

### 2. 모든 개선된 대본으로 오디오 생성

```bash
# 분할 생성 (권장 - 긴 대본 처리 가능)
python scripts/generate_audio_from_improved_split.py

# 직접 생성 (짧은 대본만)
python scripts/generate_audio_from_improved_scripts.py
```

## Voice 설정

### IT 전문가용 남자 목소리 (기본값)

- **Rasalgethi**: Informative and professional (기본값)
- **Sadaltager**: Knowledgeable and authoritative
- **Charon**: Informative and clear
- **Iapetus**: Clear and articulate
- **Orus**: Firm and decisive

### Voice 변경

`.env` 파일에 추가:

```bash
GEMINI_TTS_VOICE_NAME=Sadaltager
```

## 생성 상태 확인

### 생성된 오디오 파일 확인

```bash
ls -lh output/*audio_improved.mp3
```

### 아직 생성되지 않은 대본 확인

```bash
for file in output/*_improved.txt; do
    base=$(basename "$file" _improved.txt)
    if [ ! -f "output/${base}_audio_improved.mp3" ]; then
        echo "$file"
    fi
done
```

## 특징

### 오디오 품질 개선
- ✅ 자연스러운 호흡과 속도
- ✅ 적절한 강조와 구어체
- ✅ 기술 용어 명확한 발음
- ✅ 1.5배속 재생 지원

### Remotion 동기화
- ✅ 구간별 타이밍 정보 제공
- ✅ 시각적 요소와 매칭 가능
- ✅ JSON 형식으로 구간 정보 저장

## 문제 해결

### 타임아웃 오류
- 긴 대본은 분할 생성 스크립트 사용
- `generate_audio_from_improved_split.py` 권장

### API 키 오류
- `.env` 파일에 `GEMINI_API_KEY` 설정 확인
- API 할당량 확인

### 오디오 합치기 실패
- `ffmpeg` 설치 확인: `brew install ffmpeg` (macOS)
- 임시 파일 정리 후 재시도

## 참고 자료

- [TTS 최적화 가이드](./README_TTS_OPTIMIZATION.md)
- [Voice 가이드](./GEMINI_TTS_VOICE_GUIDE.md)
- [대본 개선 가이드](./improve_scripts_for_audio_video.py)
