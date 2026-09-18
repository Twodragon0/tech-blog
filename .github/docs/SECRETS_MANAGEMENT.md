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

- `GEMINI_SERVICE_ACCOUNT_KEY`: Google Cloud 서비스 계정 키 — **설정하지 말 것**
  - 2026-09-17 실측: 등록돼 있지 않고, 이 저장소의 워크플로·코드 어디서도 읽지 않는다.
    유일한 사용처였던 `ai-video-gen.yml` / `generate_enhanced_audio.py` 는 `cfe0d82d`
    에서 online-course 레포로 이전했다. 오래 "⭐ 권장" 으로 적혀 있었으나 그 권장을
    따르면 소비자 없는 자격증명이 하나 생긴다.
  - Gemini 를 쓰는 현재 경로는 아래 `GEMINI_API_KEY` 하나다.
  - 되살릴 때: 소비자를 같은 PR 에서 함께 넣고
    `scripts/check_secret_contract.py` 의 예외에서 지울 것.

- `GOOGLE_CLOUD_PROJECT`: Google Cloud 프로젝트 ID
  - 생성 방법: Google Cloud Console에서 프로젝트 ID 확인
  - 형식: 프로젝트 ID 문자열
  - 사용처: 런타임 소비자 **없음**. `scripts/setup_gemini_oauth.sh` 와
    `scripts/gemini_oauth_setup.py` 가 로컬 설정 안내로 `export ...` 문자열을 **출력만**
    한다 — 읽는 코드는 없다. Actions 시크릿으로 둘 필요가 없다는 뜻이다.
  - 기본값 예시: `your-project-id`

### DeepSeek API 관련 (보이스 생성)
- `DEEPSEEK_API_KEY`: DeepSeek AI API 키 (선택적)
  - 생성 방법: [DeepSeek Platform](https://platform.deepseek.com)에서 발급
  - 형식: `sk-`로 시작하는 문자열
  - 사용처: `.github/workflows/ai-video-gen.yml`, `scripts/generate_enhanced_audio.py`
  - 비용: 토큰 기반 과금 (비용 효율적)
  - 참고: DeepSeek 또는 Gemini 중 하나는 필수

### ElevenLabs API 관련 — 여기에 설정하지 말 것 (2026-09-17 삭제 완료)

> **두 시크릿은 2026-09-17 에 이 저장소의 Actions 시크릿에서 삭제됐다.**
> 2026-01-11 부터 등록돼 있었지만 워크플로 0건·코드 0건이었다 — 아래 "사용처"로 적혀
> 있던 `ai-video-gen.yml` 과 `generate_enhanced_audio.py` 가 커밋 `cfe0d82d` 에서
> online-course 로 이전하면서 시크릿만 남았기 때문이다.
>
> **"online-course 로 이관" 은 애초에 선택지가 아니었다.** Actions 시크릿은 저장소
> 범위라 이 저장소의 시크릿을 저쪽이 쓴 적이 없다. 게다가 online-course 도 CI 에서
> 이 키를 쓰지 않는다 — 워크플로 6개 중 참조 0건, Actions 시크릿 0개이고, 스크립트
> (`generate_elevenlabs_audio.py`, `scripts/video/audio_video/generate_enhanced_audio.py`)
> 가 `os.getenv("ELEVENLABS_API_KEY")` 로 **로컬 환경변수**를 읽는다.
>
> 그래서 삭제로 깨지는 것이 없다. ElevenLabs 대시보드의 키 자체는 **revoke 하지
> 않았다** — 로컬 오디오 생성이 계속 그 키를 쓴다. 이름을 문서에 남겨 두는 이유는,
> 지우면 누군가 다시 등록하기 때문이다.

- `ELEVENLABS_API_KEY`: ElevenLabs Text-to-Speech API 키
  - 생성 방법: [ElevenLabs Creative Platform](https://elevenlabs.io/app) → Developers → API Keys
  - 형식: `sk_`로 시작하는 문자열
  - 권한: Text to Speech (Access)만 활성화 (최소 권한 원칙)
  - 사용처: **없음** (이전: `ai-video-gen.yml`, `generate_enhanced_audio.py` — `cfe0d82d` 에서 이전)
  - 비용 관리: 월간 크레딧 제한 설정 권장 (ElevenLabs 대시보드에서 설정)
  - 참고: 무료 티어는 월 10,000자 제한

- `ELEVENLABS_VOICE_ID`: ElevenLabs Voice ID
  - 생성 방법: ElevenLabs Creative Platform → Voices → Voice 선택 → Voice ID 복사
  - 또는 Voice Cloning으로 본인 목소리 생성 후 Voice ID 확인
  - 형식: UUID 문자열
  - 사용처: **없음** (위와 같다)

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

### Slack 알림 관련
6개 워크플로(`slack-post-notify`, `slack-category-digest`, `monitoring`,
`googlebot-access-monitor`, `monthly-quality-report`, `ai-blogwatcher`)가 쓴다.
그중 다섯은 `test_ci_secret_absence_guard.py` 의 `FAIL_CLOSED` 라서, 이 둘이 없으면
**잡이 실패한다** — 조용히 건너뛰지 않는다.

- `SLACK_BOT_TOKEN`: Slack Bot User OAuth Token
  - 생성 방법: Slack App → OAuth & Permissions → Bot User OAuth Token
  - 형식: `xoxb-` 로 시작
  - 권한: `chat:write` (채널에 초대 필요)
- `SLACK_CHANNEL_ID`: 알림을 보낼 채널 ID
  - 형식: `C` 로 시작하는 ID (채널명 아님)

### 워크플로가 읽지만 프로비저닝되지 않은 것 (2026-09-17 실측)

아래 12개는 `secrets.<NAME>` 으로 **참조되지만 등록돼 있지 않다.** 그래서 해당 경로는
건너뛰거나 실패한다 — 어느 쪽인지는 워크플로마다 다르고, 그 비대칭을
`scripts/tests/test_ci_secret_absence_guard.py` 가 붙들고 있다. 여기서는 목록과 상태만
기록한다. **설정 절차를 추측해서 적지 않는다** — 그게 이 문서가 처음 어긋난 방식이다.

| Secret | 읽는 워크플로 | 기존 가드가 판단했나 |
|---|---|---|
| `GSC_SERVICE_ACCOUNT_JSON` | `gsc-queue-refresh` | ✅ `NEVER_CONFIGURED` |
| `VERCEL_TOKEN` | `vercel-firewall-backup`, `monitoring`, `ops-orchestrator` | ✅ `NEVER_CONFIGURED` |
| `VERCEL_PROJECT_ID` | `vercel-firewall-backup` | ✅ 가드 주석 |
| `VERCEL_TEAM_ID` | `vercel-firewall-backup` | ✅ 가드 주석 |
| `SLACK_WEBHOOK` | `monitoring` | ✅ 가드 주석 (한 번도 발화한 적 없음) |
| `AI_GATEWAY_TOKEN` | ~~`ops-orchestrator`~~ | ✅ **2026-09-18 참조 제거** |
| `AI_GATEWAY_URL` | ~~`ops-orchestrator`~~ | ✅ **2026-09-18 참조 제거** |
| `SLACK_CHANNEL_ID_OPS` | ~~`ops-orchestrator`~~ | ✅ **2026-09-18 참조 제거** |
| `CLAUDE_API_KEY` | `ai-blogwatcher` | ✅ 2026-09-17 — 선택적 프로바이더 |
| `OPENAI_API_KEY` | `ai-blogwatcher` | ✅ 2026-09-17 — 선택적 프로바이더 |
| `PAGESPEED_API_KEY` | `monitoring`, `ops-orchestrator` | ❌ 미판단 |

**AI_GATEWAY_* + SLACK_CHANNEL_ID_OPS — 2026-09-18 에 참조를 제거했다.**

`ops-orchestrator.yml` 에 AI Gateway 로 Slack 에 보내는 단계가 **세 개**(잡마다 하나)
있었고, `if: env.HAS_AI_GATEWAY == 'true' && env.HAS_SLACK_OPS == 'true'` 로 묶여 있었다.
셋 다 미등록이라 **존재한 이래 한 번도 실행되지 않았다** — 워크플로는 2026-08-07 부터
가동했고, 성공 실행 10건을 표본으로 뽑아 전부 `skipped` 임을 확인했다.

제거한 이유는 "안 돌아서" 가 아니라 **중복이어서**다. 같은 일을 하는 경로가 이미 있다:
`SLACK_BOT_TOKEN` + `SLACK_CHANNEL_ID` + `scripts/notify_webhook.py` (등록돼 있고
워크플로 6개가 쓰며 `--require-delivery` 로 테스트된다). AI Gateway 경로는 같은 결과를
위해 미등록 시크릿 3개와 **외부 자체호스팅 서비스**를 추가로 요구했다. 실패 알림은
바로 다음 `Create issue on failure` 단계가 `GITHUB_TOKEN` 만으로 이미 수행한다.

`test_ci_secret_absence_guard.py` 의 `NEVER_CONFIGURED` 로 옮기지 **않았다.** 그 목록의
계약은 "시크릿이 없으면 **워크플로 전체**가 아무 일도 안 한다" 이고, 짝이 되는 테스트가
cron 제거까지 요구한다. 여기는 워크플로가 실제 작업을 하고 알림 단계만 막히는 경우이며
ops-orchestrator 에는 6시간 cron 이 있다. 비슷해 보이는 옆 목록을 재사용하면 안 되는
사례였다.

⚠️ **다시 넣는다면 게이트웨이 서비스와 시크릿 3개를 같은 PR 에서 함께** 넣어야 한다.
`priority` 잡은 이제 시크릿이 하나도 없고,
`test_ci_ops_orchestrator_partition_guard.py::test_priority_job_has_no_secrets_at_all`
이 그 상태를 고정한다.

**선택적 프로바이더 (`CLAUDE_API_KEY`, `OPENAI_API_KEY`).** `USE_AI` 기본값 `auto` 는
네 프로바이더 키를 모두 넘기고, `GEMINI_API_KEY` 와 `DEEPSEEK_API_KEY` 는 등록돼 있다.
부재는 실패가 아니라 **선택지 축소**다 — 다이제스트는 매일 정상 발행된다.

`USE_GEMINI_PRO_IMAGE` 는 2026-09-17 에 이 목록에서 빠졌다. 시크릿이 아니라 기본값을
가진 불리언 플래그였고, `vars.USE_GEMINI_PRO_IMAGE` 로 옮겼다. 저장소 변수 문서는
아래 "저장소 변수" 절을 볼 것.

### 저장소 변수 (`vars.`) — 시크릿이 아닌 설정

값이 비밀이 아니고 감사에서 보이는 편이 나은 스위치는 시크릿이 아니라 변수다.
시크릿에 넣으면 값이 가려져 "지금 무엇이 켜져 있나" 를 아무도 못 본다.

- `USE_GEMINI_PRO_IMAGE`: 이미지 생성에 Gemini Pro 를 쓸지 (미설정 시 `false` → Flash)
  - 소비자: `scripts/generate_post_images.py`, `scripts/generate_missing_diagrams.py`
  - ⚠️ 두 소비자의 **로컬 기본값이 서로 다르다** — `generate_post_images.py:146` 은
    `"true"`, `generate_missing_diagrams.py:42` 는 `"false"`. CI 는 워크플로가 항상
    `'false'` 를 넘기므로 일치하지만, 환경변수 없이 로컬 실행하면 두 스크립트가 다른
    모델을 쓴다. 어느 쪽으로 맞출지는 비용·품질 결정이라 미정.
- `AI_BLOGWATCHER_SCHEDULE`, `ULTRAWORK_LOOP_SCHEDULE`, `GSC_SITE_URL`,
  `AUTO_PUBLISH_GEMINI_MODEL`, `SLACK_CATEGORY_DIGEST_SCHEDULE` 도 같은 범주다.

### SNS 공유 관련 — Actions 시크릿으로 설정하지 말 것

`sns-share.yml` 은 2026-08-11 에 폐기됐다. 여덟 개 모두 미설정 상태였고, 매 push 마다
약 3분을 의존성 설치에 쓴 뒤 "아무 데도 공유하지 않고" 성공을 보고했다. X/Twitter API v2
게시는 유료 티어를, Facebook/LinkedIn 은 앱 심사를 요구해서 CLAUDE.md 의 free-tier-first
원칙과 충돌한다.

`scripts/share_sns.py` 와 `scripts/linkedin_oauth.py` 는 **수동 실행용으로 남아 있고**
(`test_ci_secret_absence_guard.py::test_share_sns_script_is_kept_for_manual_use`),
값은 로컬 `.env` / 셸 환경변수로 준다. Actions 시크릿으로 넣으면 소비자 없는 자격증명이
된다 — `test_retired_social_secrets_are_not_referenced_by_any_workflow` 가 워크플로에서
다시 참조하는 것을 막는다.

- `TWITTER_API_KEY` / `TWITTER_API_SECRET` / `TWITTER_ACCESS_TOKEN` / `TWITTER_ACCESS_SECRET`
- `FACEBOOK_PAGE_ID` / `FACEBOOK_ACCESS_TOKEN`
- `LINKEDIN_ACCESS_TOKEN` / `LINKEDIN_PERSON_ID`

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

# Slack 알림 (6개 워크플로가 사용 — 사실상 필수)
gh secret set SLACK_BOT_TOKEN --body "your-slack-bot-token"
gh secret set SLACK_CHANNEL_ID --body "your-slack-channel-id"

# SNS 공유는 Actions 시크릿으로 설정하지 않는다 — 아래 "SNS 공유 관련" 절 참조

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
