# 콘텐츠 생성 워크플로우 가이드

## 개요

포스팅부터 영상 제작까지의 전체 자동화 워크플로우입니다.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. 포스팅   │───▶│  2. 이미지   │───▶│  3. 대본    │───▶│  4. TTS     │───▶│  5. 영상    │
│    작성     │    │    생성     │    │    생성     │    │    생성     │    │    제작     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
      │                  │                  │                  │                  │
      ▼                  ▼                  ▼                  ▼                  ▼
  Markdown           Diagrams          Gemini CLI        ElevenLabs         FFmpeg
  + Front Matter     + Gemini          + DeepSeek        + Gemini TTS       + Remotion
```

---

## 비용 최적화 전략

### API 우선순위

| 우선순위 | 서비스 | 비용 | 용도 |
|----------|--------|------|------|
| 1순위 | **Gemini CLI** | 무료 (OAuth 2.0) | 대본 생성, 텍스트 처리 |
| 2순위 | **Python Diagrams** | 무료 (로컬) | AWS/보안 아키텍처 다이어그램 |
| 3순위 | **Edge-TTS** | 무료 | TTS (API 키 불필요) |
| 4순위 | **Coqui TTS** | 무료 (로컬) | TTS 폴백 (로컬 실행) |
| 5순위 | **DeepSeek API** | 저비용 | 대본 생성 폴백 |
| 6순위 | **Gemini API** | 유료 | 이미지 생성, TTS 폴백 |
| 7순위 | **ElevenLabs** | 유료 | 고품질 TTS (최후의 수단) |

### 캐싱 전략

```
캐시 디렉토리: .cache/
├── scripts/          # 생성된 대본 캐시
├── audio/            # 생성된 오디오 캐시
└── images/           # 생성된 이미지 캐시

캐시 키: SHA256(content + title + date)
```

---

## 1단계: 포스팅 작성

### 파일 구조

```yaml
---
layout: post
title: "제목"
date: 2026-01-12 10:00:00 +0900
category: [devsecops]
tags: [AWS, Security, Kubernetes]
excerpt: "요약 (150-200자)"
image: /assets/images/2026-01-12-Title.svg
---

## 📋 포스팅 요약
[AI 요약 카드]

## 서론
[배경 및 목적]

## 1. 개요
[주요 개념]

## 2. 핵심 내용
[상세 설명 + 코드 예제]

## 결론
[요약]
```

### 자동화 스크립트

```bash
# AI 기반 포스트 개선
python3 scripts/ai_improve_posts.py

# 포스트 요약 생성
python3 scripts/enhance_posts_summary.py
```

---

## 2단계: 이미지 생성

### 2.1 AWS 아키텍처 다이어그램 (Python Diagrams)

AWS 관련 포스트의 경우 Python `diagrams` 라이브러리 사용:

```bash
# AWS 아키텍처 다이어그램 생성
python3 scripts/generate_aws_diagram.py _posts/2026-01-12-AWS_Security.md
```

**지원 다이어그램 유형:**
- VPC 네트워크 아키텍처
- EC2/ECS/EKS 컴퓨팅 구조
- S3/RDS/DynamoDB 데이터 계층
- IAM/WAF/Shield 보안 아키텍처
- CloudWatch/X-Ray 모니터링

### 2.2 일반 이미지 (Gemini Nano Banana)

비 AWS 콘텐츠 또는 개념도:

```bash
# Gemini로 이미지 생성
python3 scripts/generate_post_images.py _posts/2026-01-12-DevSecOps.md
```

### 2.3 세그먼트 이미지 (영상용)

```bash
# 영상 세그먼트별 이미지 생성
python3 scripts/generate_segment_images.py _posts/2026-01-12-DevSecOps.md
```

### 이미지 생성 우선순위

| 콘텐츠 유형 | 생성 방법 | 비용 | 자동 감지 |
|------------|----------|------|----------|
| **AWS 아키텍처** | **Python Diagrams** | **무료** | ✅ 자동 감지 (AWS 키워드 2개 이상) |
| **보안 아키텍처** | **Python Diagrams** | **무료** | ✅ 자동 감지 (보안 키워드 2개 이상) |
| Kubernetes 구조 | Python Diagrams | 무료 | 수동 지정 |
| 개념도/흐름도 | Gemini API | 유료 | 기본값 |
| 썸네일 | Gemini Nano Banana | 유료 | 수동 지정 |

**자동 감지 로직:**
- AWS 키워드 2개 이상 감지 → Python Diagrams 사용
- 보안 키워드 2개 이상 감지 → Python Diagrams 사용
- 그 외 → Gemini API 사용

---

## 3단계: 대본 생성

### API 선택 전략

```python
# 1순위: Gemini CLI (무료 - OAuth 2.0)
if check_gemini_cli_available():
    script = generate_script_with_gemini_cli(text, title)

# 2순위: DeepSeek API (저비용)
if not script and DEEPSEEK_API_KEY:
    script = generate_script_with_deepseek(text, title)

# 3순위: Gemini API (비용 발생)
if not script and GEMINI_API_KEY:
    script = generate_script_with_gemini(text, title)
```

### 대본 구조

```markdown
# [제목] 강의

안녕하세요, 오늘은 [주제]에 대해 알아보겠습니다.

## 서론
[배경 설명]

## 1. [첫 번째 주제]
[상세 설명]

## 2. [두 번째 주제]
[상세 설명]

## 결론
[요약 및 마무리]

감사합니다.
```

### 실행 방법

```bash
# 대본 생성
python3 scripts/generate_enhanced_audio.py --script-only _posts/2026-01-12-Post.md
```

---

## 4단계: TTS (Text-to-Speech)

### API 선택 전략 (비용 최적화)

| 우선순위 | 서비스 | 품질 | 비용 | 특징 |
|----------|--------|------|------|------|
| **1순위** | **Edge-TTS** | 우수 | **무료** | Microsoft Edge TTS, API 키 불필요, 한국어 지원 |
| **2순위** | **Coqui TTS** | 우수 | **무료** | 로컬 실행, 완전 무료, 한국어 지원 |
| 3순위 | ElevenLabs | 최고 | 유료 (월 10,000자 무료) | 최고 품질, 유료 |
| 4순위 | Gemini TTS | 우수 | 유료 | 폴백 옵션 |

### TTS 설치 및 설정

#### Edge-TTS (권장 - 무료)
```bash
# 설치
pip install edge-tts

# 사용 가능한 한국어 음성 확인
edge-tts --list-voices | grep ko-KR
```

#### Coqui TTS (로컬 실행)
```bash
# 설치
pip install TTS

# 한국어 모델 자동 다운로드 (첫 실행 시)
python3 -c "from TTS.api import TTS; tts = TTS(model_name='tts_models/ko/common-glow_tts')"
```

#### ElevenLabs 설정 (선택사항)
```python
# ElevenLabs 설정 (유료)
VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam
VOICE_SETTINGS = {
    "stability": 0.5,
    "similarity_boost": 0.75,
    "style": 0.5,
    "use_speaker_boost": True
}
```

### 오디오 설정

```python
# 오디오 설정
AUDIO_SPEED_MULTIPLIER = 1.5  # 1.5배속
AUDIO_OUTPUT_FORMAT = "mp3"
MAX_SCRIPT_LENGTH = 4500  # 약 7-8분 분량
```

### 실행 방법

```bash
# TTS 생성 (대본 포함)
python3 scripts/generate_enhanced_audio.py _posts/2026-01-12-Post.md

# 오디오만 생성 (기존 대본 사용)
python3 scripts/generate_enhanced_audio.py --audio-only _posts/2026-01-12-Post.md
```

---

## 5단계: 영상 제작

### 영상 생성 방법

| 방법 | 장점 | 단점 | 비용 |
|------|------|------|------|
| **FFmpeg** | 빠름, 안정적 | 기본 기능만 | 무료 |
| **Remotion** | 고품질, 애니메이션 | 설정 복잡 | 무료 |
| **Gemini Veo** | AI 생성 | 실험적 | 유료 |

### 영상 구조

```
0:00 - 0:30  인트로 (제목 + 썸네일)
0:30 - 1:00  목차 소개
1:00 - 끝    본문 (세그먼트별 이미지 + TTS)
마지막 30초  아웃트로 (구독 유도)
```

### 실행 방법

```bash
# 전체 워크플로우 (대본 + TTS + 영상)
python3 scripts/generate_post_to_video.py _posts/2026-01-12-Post.md

# 영상만 생성 (기존 오디오 사용)
python3 scripts/generate_post_to_video.py --skip-audio _posts/2026-01-12-Post.md

# Remotion으로 영상 생성
python3 scripts/generate_post_to_video.py --method remotion _posts/2026-01-12-Post.md
```

---

## 통합 워크플로우

### 전체 파이프라인 실행

```bash
# 전체 워크플로우 (1-5단계 모두)
python3 scripts/generate_complete_content.py _posts/2026-01-12-Post.md

# 옵션
python3 scripts/generate_complete_content.py \
    --skip-post-improve \     # 포스트 개선 건너뛰기
    --image-method diagrams \ # AWS 다이어그램 사용
    --tts-method elevenlabs \ # ElevenLabs TTS
    --video-method ffmpeg \   # FFmpeg 영상
    _posts/2026-01-12-Post.md
```

### GitHub Actions 워크플로우

```yaml
name: Generate Content
on:
  push:
    paths:
      - '_posts/*.md'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r scripts/requirements.txt

      - name: Generate content
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
          ELEVENLABS_API_KEY: ${{ secrets.ELEVENLABS_API_KEY }}
        run: |
          python3 scripts/generate_complete_content.py \
            --auto-detect-new
```

---

## 환경 변수

```bash
# 필수
export GEMINI_API_KEY="your-gemini-api-key"

# 선택 (비용 최적화)
export USE_GEMINI_CLI="true"              # Gemini CLI 우선 사용
export USE_DEEPSEEK_FOR_SCRIPT="true"     # DeepSeek 대본 생성
export PREFER_GEMINI="true"               # Gemini 우선

# TTS
export ELEVENLABS_API_KEY="your-key"      # ElevenLabs API
export ELEVENLABS_VOICE_ID="voice-id"     # 음성 ID

# 캐싱
export ENABLE_CACHING="true"              # 캐싱 활성화
```

---

## 출력 파일 구조

```
output/
├── 2026-01-12-Post_script.md       # 생성된 대본
├── 2026-01-12-Post_audio.mp3       # 생성된 오디오
├── 2026-01-12-Post_video.mp4       # 생성된 영상
└── 2026-01-12-Post_segments/       # 세그먼트 이미지
    ├── segment_001.png
    ├── segment_002.png
    └── ...

assets/images/
├── 2026-01-12-Post.svg             # 메인 이미지
└── 2026-01-12-Post_diagram.png     # AWS 다이어그램
```

---

## 트러블슈팅

### Gemini CLI 인증 오류

```bash
# OAuth 재인증
gemini auth login

# 인증 상태 확인
gemini auth status
```

### TTS 라이브러리 설치 오류

```bash
# Edge-TTS 재설치
pip install --upgrade edge-tts

# Coqui TTS 재설치
pip install --upgrade TTS

# 사용 가능한 한국어 음성 확인 (Edge-TTS)
edge-tts --list-voices | grep ko-KR
```

### ElevenLabs 할당량 초과

```bash
# 할당량 확인
curl -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/user/subscription

# Edge-TTS로 자동 폴백 (기본 동작)
# 또는 Coqui TTS 사용
```

### 이미지 생성 실패

```bash
# Python Diagrams 재설치
pip install --upgrade diagrams graphviz

# Graphviz 설치 (macOS)
brew install graphviz
```

---

## 참고 문서

- [Gemini CLI 설정](GEMINI_OAUTH_SETUP.md)
- [TTS 오픈소스 가이드](TTS_OPENSOURCE_GUIDE.md) ⭐ **추천**
- [ElevenLabs 설정](ELEVENLABS_SETUP.md)
- [비디오 생성 가이드](README_VIDEO_GENERATION.md)
- [비용 최적화 가이드](COST_OPTIMIZATION_GUIDE.md)
