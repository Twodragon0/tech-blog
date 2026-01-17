# Coqui TTS 설치 가이드

## 개요

Coqui TTS는 완전 무료 오픈소스 텍스트-음성 변환 도구입니다. 한국어를 포함한 다양한 언어를 지원합니다.

## 설치 방법

### 기본 설치

```bash
pip install TTS
```

### 한국어 지원 포함 설치 (권장)

```bash
pip install TTS[ko]
```

### 시스템 요구사항

- Python 3.10 이상, 3.14 미만
- ffmpeg (오디오 변환용)
- 충분한 디스크 공간 (모델 다운로드용, 약 1-2GB)

### ffmpeg 설치

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
- [ffmpeg 다운로드](https://ffmpeg.org/download.html) 또는
- `choco install ffmpeg` (Chocolatey 사용 시)

## 설치 확인

```bash
python3 -c "from TTS.api import TTS; print('Coqui TTS 설치 완료!')"
```

## 사용 방법

설치 후 다음 스크립트를 실행하세요:

```bash
# 간단한 테스트
python scripts/generate_tts_simple.py

# 전체 대본 생성
python scripts/generate_tts_comparison.py [대본파일]
```

## 문제 해결

### 설치 오류

**Python 버전 문제:**
- Python 3.10 이상이 필요합니다
- `python3 --version`으로 버전 확인

**의존성 오류:**
```bash
pip install --upgrade pip
pip install TTS[ko] --no-cache-dir
```

### 모델 다운로드 오류

- 인터넷 연결 확인
- 디스크 공간 확인 (최소 2GB 여유 공간)
- 방화벽 설정 확인

### 메모리 부족

- GPU가 없는 경우 CPU 모드로 실행됩니다 (느릴 수 있음)
- `gpu=False` 옵션이 기본값입니다

## 참고 자료

- [Coqui TTS 공식 문서](https://docs.coqui.ai/)
- [GitHub 저장소](https://github.com/coqui-ai/TTS)
