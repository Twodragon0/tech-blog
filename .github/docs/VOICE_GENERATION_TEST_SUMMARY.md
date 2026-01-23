# 목소리 생성 테스트 완료 요약

## ✅ 설정 완료 상태

### GitHub Secrets 설정
모든 필수 Secrets가 GitHub에 설정되었습니다:

- ✅ `GEMINI_API_KEY` (2026-01-11 설정)
- ✅ `GOOGLE_CLOUD_PROJECT` (your-project-id)
- ✅ `DEEPSEEK_API_KEY` (2026-01-11 설정)
- ✅ `ELEVENLABS_API_KEY` (2026-01-11 설정)
- ✅ `ELEVENLABS_VOICE_ID` (2026-01-11 설정)

### 워크플로우 설정
- ✅ `.github/workflows/ai-video-gen.yml` 존재 및 설정 완료
- ✅ 수동 실행만 허용 (workflow_dispatch) - 비용 관리
- ✅ API 키 검증 단계 포함
- ✅ ElevenLabs 크레딧 확인 단계 포함

## 🎯 API 우선순위 전략

워크플로우는 다음 순서로 API를 사용합니다:

1. **Gemini OAuth 2.0** (서비스 계정 키가 있는 경우) ⭐ 최우선
2. **Gemini API Key** (OAuth 실패 시)
3. **DeepSeek API** (Gemini 실패 시)
4. **ElevenLabs API** (음성 생성 - 항상 사용)

## 📋 로컬 테스트 방법

### 1. 환경 변수 설정

`.env` 파일에 다음을 추가하세요:

```bash
# GitHub Secrets에서 확인하거나 직접 설정
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_CLOUD_PROJECT=your-project-id
DEEPSEEK_API_KEY=sk-your-deepseek-key
ELEVENLABS_API_KEY=sk_your-elevenlabs-key
ELEVENLABS_VOICE_ID=your-voice-id
```

### 2. 의존성 설치

```bash
pip3 install --user -r scripts/requirements.txt
```

### 3. 테스트 실행

```bash
# 환경 변수 로드
set -a
source .env
set +a

# 최신 포스트로 테스트
python3 scripts/generate_enhanced_audio.py
```

자세한 내용: [로컬 테스트 가이드](../scripts/TEST_VOICE_GENERATION.md)

## 🚀 GitHub Actions 워크플로우 실행

### 실행 방법

1. GitHub 저장소 접속
2. **Actions** 탭 클릭
3. **Generate AI Video Lecture** 워크플로우 선택
4. **Run workflow** 버튼 클릭
5. 옵션 설정:
   - **post_file**: 특정 포스트 파일명 (선택사항, 비워두면 최신 포스트 사용)
   - **video_method**: `ffmpeg` 또는 `remotion` (기본값: `ffmpeg`)
6. **Run workflow** 클릭

### 실행 결과 확인

- **Artifacts**: 생성된 오디오/비디오 파일 다운로드 가능
- **Logs**: 각 단계별 실행 로그 확인
- **Summary**: API 사용량 및 비용 정보

## 📊 예상 비용

### Gemini API
- Gemini 1.5 Pro: $1.25 / 1M input tokens, $5.00 / 1M output tokens
- 대본 생성 1회: 약 $0.01-0.05 (텍스트 길이에 따라)

### DeepSeek API
- DeepSeek Chat: $0.14 / 1M input tokens, $0.28 / 1M output tokens
- 대본 생성 1회: 약 $0.001-0.005

### ElevenLabs API
- 무료 티어: 월 10,000자
- 유료 플랜: 문자 수 기반 과금
- 대본 1회 (약 1000자): 약 1000자 사용

## 🔒 보안 고려사항

1. ✅ 모든 API 키는 GitHub Secrets에 암호화 저장
2. ✅ 로그에 민감 정보 마스킹
3. ✅ 최소 권한 원칙 적용
4. ✅ 환경 변수는 `.gitignore`에 포함
5. ✅ 워크플로우는 수동 실행만 허용 (비용 관리)

## 📝 다음 단계

1. **로컬 테스트**: `.env` 파일에 ElevenLabs 키 추가 후 로컬 테스트
2. **워크플로우 테스트**: GitHub Actions에서 수동 실행
3. **결과 확인**: 생성된 오디오 파일 품질 확인
4. **비용 모니터링**: API 사용량 및 비용 추적

## 🔗 관련 문서

- [로컬 테스트 가이드](../scripts/TEST_VOICE_GENERATION.md)
- [Secrets 관리 가이드](./SECRETS_MANAGEMENT.md)
- [Gemini API 설정](./../scripts/QUICK_START_GEMINI.md)
- [워크플로우 파일](./workflows/ai-video-gen.yml)

## ✅ 검증 완료 항목

- [x] GitHub Secrets 설정 완료
- [x] 워크플로우 파일 확인
- [x] API 키 검증 로직 확인
- [x] 로컬 테스트 가이드 작성
- [x] 의존성 설치 확인
- [x] 보안 설정 확인

---

**마지막 업데이트**: 2026-01-11
**상태**: ✅ 설정 완료, 테스트 준비 완료
