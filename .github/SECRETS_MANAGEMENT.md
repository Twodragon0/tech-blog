# GitHub Secrets 관리 가이드

이 문서는 GitHub Actions와 Vercel에서 사용하는 Secrets를 안전하게 관리하는 방법을 제공합니다.

## 필수 Secrets

### Sentry 관련
- `SENTRY_AUTH_TOKEN`: Sentry 인증 토큰 (필수)
  - 생성 방법: Sentry 대시보드 → Settings → Account → Auth Tokens → Create New Token
  - Token 형식: `sntryu_` 또는 `sentry-release`로 시작
  - 권한: `project:releases` (필수), `project:read` (필수), `org:read` (권장)
  - 사용처: `.github/workflows/sentry-release.yml`, `.github/workflows/vercel-deploy.yml`
  - GitHub Secrets 설정:
    ```bash
    gh secret set SENTRY_AUTH_TOKEN --body "sentry-release************fe26"
    ```
  - 확인 방법: GitHub Repository → Settings → Secrets and variables → Actions → SENTRY_AUTH_TOKEN

- `SENTRY_ORG`: Sentry Organization 슬러그 (선택적, 기본값: `twodragon`)
  - 확인 방법: Sentry 대시보드 URL에서 확인 (예: `https://sentry.io/organizations/YOUR-ORG-SLUG/`)
  - GitHub Secrets 설정 (필요시):
    ```bash
    gh secret set SENTRY_ORG --body "your-org-slug"
    ```
  - 참고: Secret이 없으면 워크플로우에서 기본값 `twodragon` 사용

- `SENTRY_PROJECT`: Sentry Project 슬러그 (선택적, 기본값: `tech-blog`)
  - 확인 방법: Sentry 대시보드 → Projects → Project 선택 → Settings → General → Project Slug
  - GitHub Secrets 설정 (필요시):
    ```bash
    gh secret set SENTRY_PROJECT --body "your-project-slug"
    ```
  - 참고: Secret이 없으면 워크플로우에서 기본값 `tech-blog` 사용

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
  - 기본값 예시: `your-gemini-api-key` (선택적, Secret이 없을 때 사용, 실제 키로 교체 필요)

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
  - 기본값 예시: `your-project-id` (선택적, Secret이 없을 때 사용, 실제 프로젝트 ID로 교체 필요)

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

### Buttondown 이메일 관련
- `BUTTONDOWN_API_KEY`: Buttondown 이메일 서비스 API 키
  - 생성 방법: [Buttondown Dashboard](https://buttondown.com/settings/api) → API Keys → Create API Key
  - 형식: UUID 문자열 (예: `xxxx`)
  - 사용처: `.github/workflows/buttondown-notify.yml`
  - 용도: 새 포스트 발행 시 구독자에게 이메일 발송
  - GitHub Secrets 설정:
    ```bash
    gh secret set BUTTONDOWN_API_KEY --body "your-buttondown-api-key"
    ```
  - API 엔드포인트: `https://api.buttondown.com/v1/subscribers`
  - 인증 방식: `Authorization: Token $BUTTONDOWN_API_KEY` 헤더 사용

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

- `GEMINI_API_KEY`: `your-gemini-api-key` (예시, 실제 키로 교체 필요)
- `GOOGLE_CLOUD_PROJECT`: `your-project-id` (예시, 실제 프로젝트 ID로 교체 필요)

**주의**: 기본값 사용 시 보안 및 비용 관리에 주의하세요. 가능하면 GitHub Secrets에 개별 키를 설정하는 것을 권장합니다. **절대 실제 API 키를 코드나 문서에 하드코딩하지 마세요.**

## Secrets 설정 방법

### 방법 1: GitHub CLI 사용 (권장) ⭐

GitHub CLI (`gh`)를 사용하여 Secrets를 설정할 수 있습니다:

```bash
# GitHub CLI 로그인 확인
gh auth status

# 필수 Secrets 설정
gh secret set ELEVENLABS_API_KEY --body "your-elevenlabs-api-key"
gh secret set ELEVENLABS_VOICE_ID --body "your-voice-id"
gh secret set DEEPSEEK_API_KEY --body "your-deepseek-api-key"

# Gemini API (선택: API Key 방식)
gh secret set GEMINI_API_KEY --body "your-gemini-api-key"

# Gemini OAuth 2.0 (선택: 권장, 비용 절감)
gh secret set GEMINI_SERVICE_ACCOUNT_KEY --body "$(cat path/to/service-account-key.json)"
gh secret set GOOGLE_CLOUD_PROJECT --body "your-project-id"

# Sentry (선택)
gh secret set SENTRY_AUTH_TOKEN --body "your-sentry-auth-token"

# Buttondown 이메일 (선택)
gh secret set BUTTONDOWN_API_KEY --body "your-buttondown-api-key"

# SNS 공유 (선택)
gh secret set TWITTER_API_KEY --body "your-twitter-api-key"
gh secret set TWITTER_API_SECRET --body "your-twitter-api-secret"
gh secret set TWITTER_ACCESS_TOKEN --body "your-twitter-access-token"
gh secret set TWITTER_ACCESS_SECRET --body "your-twitter-access-secret"
gh secret set FACEBOOK_PAGE_ID --body "your-facebook-page-id"
gh secret set FACEBOOK_ACCESS_TOKEN --body "your-facebook-access-token"
gh secret set LINKEDIN_ACCESS_TOKEN --body "your-linkedin-access-token"
gh secret set LINKEDIN_PERSON_ID --body "your-linkedin-person-id"

# Secrets 확인
gh secret list
```

**주의사항:**
- `GEMINI_SERVICE_ACCOUNT_KEY`는 JSON 파일 전체 내용을 설정해야 합니다
- 파일 내용을 설정할 때: `gh secret set GEMINI_SERVICE_ACCOUNT_KEY < path/to/service-account-key.json`
- 또는: `gh secret set GEMINI_SERVICE_ACCOUNT_KEY --body "$(cat path/to/service-account-key.json)"`

### 방법 2: CLI 스크립트 사용

```bash
# 스크립트 실행
cd scripts
./setup_gemini_api_key.sh --api-key YOUR_KEY --both
```

자세한 내용은 [Gemini API Key 설정 가이드](../scripts/SETUP_GEMINI_API_KEY.md)를 참조하세요.

### 방법 3: GitHub 웹 인터페이스 사용

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

### Cursor Claude 설정 (Claude Code CLI 사용자)

#### 문제 시나리오

**시나리오 1: 비활성화된 API 키로 인한 오류**
- Claude Pro/Max 구독이 있는데도 API 키 오류 발생
- **원인**: 이전에 사용하던 조직(organization)의 비활성화된 API 키가 환경 변수에 남아있어 충돌

**시나리오 2: 이중 인증 충돌 (맞춤형 에이전트 개발자)**
- Claude Max Pro 구독자이면서 동시에 맞춤형 에이전트 개발자
- SDK 직접 호출을 위해 `ANTHROPIC_API_KEY` 환경 변수 필요
- 두 도구가 같은 컴퓨터에서 실행 중
- **원인**: 두 인증 방식 모두 유효하지만 지속적인 인증 충돌 경고 발생

**참고**: 이 문제는 [GitHub Issue #9880](https://github.com/getcursor/cursor/issues/9880)에서 논의되었으며, `--use-subscription` 플래그나 설정 파일 옵션 개선이 제안되었습니다.

**해결 방법 1: 환경 변수 제거 (권장)**

**Windows:**
```bash
# 명령 프롬프트에서 실행
set ANTHROPIC_API_KEY=

# 또는 시스템 환경 변수 설정에서 해당 변수를 삭제
# 제어판 → 시스템 → 고급 시스템 설정 → 환경 변수
```

**macOS/Linux:**
```bash
# 현재 세션에서만 제거
unset ANTHROPIC_API_KEY

# 영구적으로 제거 (셸 설정 파일에서 삭제)
# ~/.zshrc 또는 ~/.bashrc 파일을 열어서 다음 라인 삭제:
# export ANTHROPIC_API_KEY="..."

# 셸 설정 파일 편집 후
source ~/.zshrc  # 또는 source ~/.bashrc
```

**해결 방법 2: Cursor 설정 파일 수정**

Cursor 설정 파일에 다음 설정을 추가하여 환경 변수 API 키를 무시하고 구독을 우선 사용하도록 설정:

**설정 파일 위치:**
- **macOS**: `~/Library/Application Support/Cursor/User/settings.json`
- **Windows**: `%APPDATA%\Cursor\User\settings.json`
- **Linux**: `~/.config/Cursor/User/settings.json`

**설정 추가:**

```json
{
  "claude": {
    "authPrecedence": "subscription",
    "ignoreEnvApiKey": true
  }
}
```

**설정 옵션 설명:**
- `authPrecedence`: 인증 우선순위 설정
  - `"subscription"`: Claude 구독을 우선 사용 (구독 사용자 권장)
  - `"api-key"`: API 키를 우선 사용 (에이전트 개발자용)
  - `"auto"`: 자동 선택 (기본값)
- `ignoreEnvApiKey`: 환경 변수의 API 키 무시 여부
  - `true`: 환경 변수 `ANTHROPIC_API_KEY` 무시 (구독 사용자 권장, 이중 인증 충돌 해결)
  - `false`: 환경 변수 API 키 사용 (에이전트 개발자용)

**사용 사례별 권장 설정:**

| 사용 사례 | `authPrecedence` | `ignoreEnvApiKey` | 설명 |
|----------|----------------|------------------|------|
| **구독 전용 사용자** | `"subscription"` | `true` | 환경 변수 API 키 무시, 구독만 사용 |
| **에이전트 개발자 (이중 인증)** | `"subscription"` | `true` | Cursor는 구독 사용, SDK는 환경 변수 API 키 사용 |
| **API 키 전용 사용자** | `"api-key"` | `false` | 환경 변수 API 키 우선 사용 |
| **자동 선택** | `"auto"` | `false` | 시스템이 자동으로 선택 (기본값) |

**이중 인증 워크플로우 (맞춤형 에이전트 개발자):**
- Cursor/Claude Code: 구독 인증 사용 (`ignoreEnvApiKey: true`)
- SDK/에이전트: 환경 변수 `ANTHROPIC_API_KEY` 사용
- 두 인증 방식이 각각의 목적에 맞게 작동하며 충돌 없음

**설정 적용 방법:**

1. **Cursor 완전 종료**
   ```bash
   # macOS
   killall Cursor
   
   # Windows
   taskkill /F /IM Cursor.exe
   
   # Linux
   pkill -f cursor
   ```

2. **설정 파일 편집**
   ```bash
   # macOS
   nano ~/Library/Application\ Support/Cursor/User/settings.json
   
   # Windows (PowerShell)
   notepad $env:APPDATA\Cursor\User\settings.json
   
   # Linux
   nano ~/.config/Cursor/User/settings.json
   ```

3. **설정 추가 후 Cursor 재시작**

**확인 방법:**

1. Cursor 재시작 후 Claude API 호출 테스트
2. Cursor 개발자 도구 열기: `Help → Toggle Developer Tools`
3. Console 탭에서 오류 메시지 확인
4. Settings에서 Claude 구독 상태 확인

**추가 참고사항:**

- **명령줄 플래그 (향후 지원 예정)**: 
  - `claude --use-subscription`: 환경 변수 API 키 무시
  - `claude --ignore-env-api-key`: 대체 명령어
- **환경 변수 방식 (향후 지원 예정)**:
  - `CLAUDE_CODE_AUTH_METHOD=subscription claude`
- **현재 권장 방법**: 설정 파일 방식 (위의 방법 2)

**관련 이슈:**
- [GitHub Issue #9880](https://github.com/getcursor/cursor/issues/9880): 인증 방법 명시적 선택을 위한 플래그 개선 제안

## 참고 자료

- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
- [Sentry Auth Tokens](https://docs.sentry.io/api/auth/)
