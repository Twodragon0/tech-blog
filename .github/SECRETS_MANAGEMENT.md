# GitHub Secrets 관리 가이드

이 문서는 GitHub Actions와 Vercel에서 사용하는 Secrets를 안전하게 관리하는 방법을 제공합니다.

## 필수 Secrets

### Sentry 관련
- `SENTRY_AUTH_TOKEN`: Sentry 인증 토큰
  - 생성 방법: Sentry 대시보드 → Settings → Account → Auth Tokens
  - 권한: `project:releases` (최소 권한)
  - 사용처: `.github/workflows/sentry-release.yml`, `.github/workflows/vercel-deploy.yml`

### DeepSeek API 관련 (채팅)
- `DEEPSEEK_API_KEY`: DeepSeek AI API 키
  - 생성 방법: [DeepSeek Platform](https://platform.deepseek.com)에서 발급
  - 형식: `sk-`로 시작하는 문자열
  - 사용처: `api/chat.js` (Vercel Serverless Function)
  - 참고: Vercel 환경 변수에도 동일하게 설정 필요 (Development, Preview, Production)
  - 참고: 보이스 생성에도 사용 가능 (중복 설정 불필요)

### Gemini API 관련 (보이스 생성)
- `GEMINI_API_KEY`: Google Gemini API 키 (선택적, API Key 방식)
  - 생성 방법: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급
  - 형식: 일반 문자열
  - 사용처: `.github/workflows/ai-video-gen.yml`, `scripts/generate_enhanced_audio.py`
  - 비용: 토큰 기반 과금 (Gemini 1.5 Pro)
  - 참고: DeepSeek 또는 Gemini 중 하나는 필수
  - 기본값 예시: `AIxxxg` (선택적, Secret이 없을 때 사용)

- `GEMINI_SERVICE_ACCOUNT_KEY`: Google Cloud 서비스 계정 키 (선택적, OAuth 2.0 방식) ⭐ 권장
  - 생성 방법: 
    1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
    2. 서비스 계정 생성 및 Gemini API 활성화
    3. 서비스 계정 키 다운로드 (JSON 파일)
    4. JSON 파일 전체 내용을 Secret으로 저장
  - 형식: JSON 파일 전체 내용
  - 사용처: `.github/workflows/ai-video-gen.yml`, `scripts/generate_enhanced_audio.py`
  - 장점: API Key보다 안전, 토큰 자동 갱신, 비용 절감 가능
  - 참고: `GOOGLE_CLOUD_PROJECT` Secret도 함께 설정 필요

- `GOOGLE_CLOUD_PROJECT`: Google Cloud 프로젝트 ID (OAuth 2.0 사용 시)
  - 생성 방법: Google Cloud Console에서 프로젝트 ID 확인
  - 형식: 프로젝트 ID 문자열
  - 사용처: `.github/workflows/ai-video-gen.yml` (OAuth 2.0 인증)
  - 참고: `GEMINI_SERVICE_ACCOUNT_KEY`와 함께 사용
  - 기본값 예시: `oxxx-cxxx` (선택적, Secret이 없을 때 사용)

### DeepSeek API 관련 (보이스 생성)
- `DEEPSEEK_API_KEY`: DeepSeek AI API 키 (선택적)
  - 생성 방법: [DeepSeek Platform](https://platform.deepseek.com)에서 발급
  - 형식: `sk-`로 시작하는 문자열
  - 사용처: `.github/workflows/ai-video-gen.yml`, `scripts/generate_enhanced_audio.py`
  - 비용: 토큰 기반 과금 (비용 효율적)
  - 참고: DeepSeek 또는 Gemini 중 하나는 필수

### ElevenLabs API 관련
- `ELEVENLABS_API_KEY`: ElevenLabs Text-to-Speech API 키
  - 생성 방법: [ElevenLabs Creative Platform](https://elevenlabs.io/app) → Developers → API Keys
  - 형식: `sk_`로 시작하는 문자열
  - 권한: Text to Speech (Access)만 활성화 (최소 권한 원칙)
  - 사용처: `.github/workflows/ai-video-gen.yml`, `scripts/generate_enhanced_audio.py`
  - 비용 관리: 월간 크레딧 제한 설정 권장 (ElevenLabs 대시보드에서 설정)
  - 참고: 무료 티어는 월 10,000자 제한

- `ELEVENLABS_VOICE_ID`: ElevenLabs Voice ID
  - 생성 방법: ElevenLabs Creative Platform → Voices → Voice 선택 → Voice ID 복사
  - 또는 Voice Cloning으로 본인 목소리 생성 후 Voice ID 확인
  - 형식: UUID 문자열
  - 사용처: `.github/workflows/ai-video-gen.yml`, `scripts/generate_enhanced_audio.py`

### Vercel 관련
- Vercel 대시보드에서 직접 관리 (GitHub Integration 사용 시 자동 동기화)
  - 환경 변수는 Vercel 대시보드에서 설정
  - `DEEPSEEK_API_KEY`: Vercel 환경 변수로도 설정 필요

### SNS 공유 관련
- `TWITTER_API_KEY`: Twitter/X API Key
- `TWITTER_API_SECRET`: Twitter/X API Secret
- `TWITTER_ACCESS_TOKEN`: Twitter/X Access Token
- `TWITTER_ACCESS_SECRET`: Twitter/X Access Secret
- `FACEBOOK_PAGE_ID`: Facebook Page ID
- `FACEBOOK_ACCESS_TOKEN`: Facebook Access Token
- `LINKEDIN_ACCESS_TOKEN`: LinkedIn Access Token
- `LINKEDIN_PERSON_ID`: LinkedIn Person ID

## 기본값 설정 (선택적)

다음 값들은 Secret이 설정되지 않은 경우 기본값으로 사용됩니다:

- `GEMINI_API_KEY`: `AIzaSyDkFfVGpaP6kaJKENUItnB2u0tSCD8xQ_g`
- `GOOGLE_CLOUD_PROJECT`: `online-course-447813`

**주의**: 기본값 사용 시 보안 및 비용 관리에 주의하세요. 가능하면 GitHub Secrets에 개별 키를 설정하는 것을 권장합니다.

## Secrets 설정 방법

### 방법 1: CLI 스크립트 사용 (권장) ⭐

```bash
# 스크립트 실행
cd scripts
./setup_gemini_api_key.sh --api-key YOUR_KEY --both
```

자세한 내용은 [Gemini API Key 설정 가이드](../scripts/SETUP_GEMINI_API_KEY.md)를 참조하세요.

### 방법 2: GitHub 웹 인터페이스 사용

1. GitHub 저장소 접속
2. **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** 클릭
4. Name과 Value 입력 후 저장
5. Secret이 설정되면 기본값보다 우선 사용됩니다

### Vercel 환경 변수 설정
1. Vercel 대시보드 접속
2. 프로젝트 선택 → **Settings** → **Environment Variables**
3. 환경별 변수 추가:
   - **Production**: 프로덕션 전용
   - **Preview**: 프리뷰 배포용
   - **Development**: 로컬 개발용

## 보안 모범 사례

### 1. 최소 권한 원칙
- 각 Secret은 필요한 최소 권한만 부여
- Sentry Auth Token: `project:releases` 권한만
- ElevenLabs API Key: Text to Speech (Access)만 활성화
- GitHub Actions: 필요한 권한만 부여

### 2. 환경별 분리
- 프로덕션과 개발 환경의 Secrets 분리
- 테스트용 토큰과 프로덕션 토큰 분리

### 3. 정기적 로테이션
- 90일마다 Secrets 로테이션 권장
- 유출 의심 시 즉시 재생성
- ElevenLabs API Key: 사용량 모니터링 후 필요시 로테이션

### 4. 접근 제어
- Secrets 접근 권한을 최소한의 인원에게만 부여
- 감사 로그 정기 확인

### 5. 비용 관리 (ElevenLabs)
- API Key 생성 시 월간 크레딧 제한 설정
- ElevenLabs 대시보드에서 사용량 모니터링
- 워크플로우는 수동 실행만 허용 (workflow_dispatch)
- 긴 포스트는 요약 후 사용하여 비용 절감

## Secrets 검증

### GitHub Actions에서 Secrets 확인
```yaml
- name: Verify Secrets
  run: |
    if [ -z "${{ secrets.SENTRY_AUTH_TOKEN }}" ]; then
      echo "❌ SENTRY_AUTH_TOKEN is not set"
      exit 1
    fi
    echo "✅ Secrets verified"
```

### Vercel 환경 변수 확인
```bash
# Vercel CLI 사용
vercel env ls
```

## 문제 해결

### Secret이 설정되지 않은 경우
1. GitHub Secrets 확인: Settings → Secrets and variables → Actions
2. 워크플로우에서 Secret 참조 확인
3. Secret 이름 오타 확인

### 권한 오류
1. Sentry Auth Token 권한 확인
2. GitHub Actions 권한 설정 확인
3. Vercel 프로젝트 권한 확인

## 참고 자료

- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Sentry Auth Tokens](https://docs.sentry.io/api/auth/)
