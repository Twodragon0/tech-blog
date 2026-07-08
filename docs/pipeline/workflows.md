# GitHub Actions Workflows 상세

> 모든 워크플로우의 상세 설명 및 설정

## 워크플로우 목록

```
.github/workflows/
├── jekyll.yml              # 메인: Jekyll 빌드 및 GitHub Pages 배포
├── sns-share.yml           # SNS 자동 공유
├── buttondown-notify.yml   # 이메일 뉴스레터
├── daily-news.yml          # 일일 뉴스 수집 (deprecated, 수동 전용 — schedule는 ai-blogwatcher.yml)
├── ops-orchestrator.yml    # Ops 통합: multi_agent(6h)/priority(daily)/on_demand(dispatch) 잡
├── generate-images.yml     # AI 이미지 생성
├── sentry-release.yml      # Sentry 릴리스 관리
├── ai-video-gen.yml        # 비디오 생성
├── ci-optimization.yml     # CI 최적화
├── vercel-deploy.yml       # Vercel 배포 보조
└── test-sentry-release.yml # Sentry 테스트
```

---

## 1. Jekyll CI (jekyll.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | Jekyll 사이트 빌드 및 GitHub Pages 배포 |
| **트리거** | push (main), PR, workflow_dispatch |
| **타임아웃** | 10분 (빌드), 15분 (배포) |

### 트리거 조건
```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
```

### Jobs 구조
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ check-changes   │ ──▶ │     build       │ ──▶ │     deploy      │
│                 │     │                 │     │                 │
│ • paths-filter  │     │ • Ruby setup    │     │ • GitHub Pages  │
│ • should-build  │     │ • Jekyll build  │     │ • only on main  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 조건부 실행 경로
```yaml
# 다음 경로 변경 시에만 빌드
paths:
  - '**_posts/**'
  - '**_includes/**'
  - '**_layouts/**'
  - '**_sass/**'
  - '**assets/**'
  - '**_config.yml'
  - '**.github/workflows/**'
```

### 환경 변수
```yaml
env:
  JEKYLL_ENV: production
  LANG: C.UTF-8
  BUILD_ID: ${{ github.sha }}
```

---

## 2. SNS Share (sns-share.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 새 포스트 SNS 자동 공유 |
| **트리거** | push (main, _posts/**) |
| **타임아웃** | 10분 |

### 지원 플랫폼
| 플랫폼 | API | 필요 Secrets |
|--------|-----|-------------|
| Twitter/X | Tweepy v2 | TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET |
| Facebook | Graph API | FACEBOOK_PAGE_ID, FACEBOOK_ACCESS_TOKEN |
| LinkedIn | UGC Posts | LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSON_ID |

### 실행 흐름
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Check Posts    │ ──▶ │  Setup Python   │ ──▶ │   Share SNS     │
│                 │     │                 │     │                 │
│ • git diff      │     │ • Python 3.11   │     │ • share_sns.py  │
│ • has_new_posts │     │ • requirements  │     │ • latest_post   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 3. Buttondown Notify (buttondown-notify.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 새 포스트 이메일 뉴스레터 발송 |
| **트리거** | push (main, _posts/**) |
| **타임아웃** | 10분 |

### 특징
- **새 포스트만**: `--diff-filter=A` (Added only)
- **수정 포스트 제외**: 업데이트된 포스트는 발송하지 않음
- **배치 처리**: 여러 포스트 동시 처리

### 실행 흐름
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Check Posts    │ ──▶ │  Setup Python   │ ──▶ │  Send Email     │
│                 │     │                 │     │                 │
│ • git diff -A   │     │ • Python 3.11   │     │ • buttondown_   │
│ • new posts only│     │ • pyyaml        │     │   notify_batch  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 4. Ops Orchestrator (ops-orchestrator.yml)

> 이전의 `ops-multi-agent-loop.yml` / `ops-priority-loop.yml` / `ultrawork-loop.yml` /
> `ai-ops-on-demand.yml` 4개를 단일 파일로 통합했다. 하나의 `on:`(두 cron +
> `workflow_dispatch` profile + `repository_dispatch`)과 상호 배타적인 3개의
> `if:`-게이트 잡으로 구성되며, 각 잡은 자신의 최소 권한과 시크릿 스코프를 그대로 유지한다
> (동작 보존형 통합). 모든 잡은 `scripts/ops_health_orchestrator.py`를 호출한다.

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 운영 헬스 점검(lint/types, Vercel, GitHub Actions, Sentry, UI/UX) + Slack 알림 |
| **트리거** | schedule(`0 */6`, `0 4`), `workflow_dispatch`(profile), `repository_dispatch`(`ai_ops_task`) |
| **동시성** | `ops-orchestrator-${{ github.event_name }}-...` (잡별 독립 레인) |

### 잡 구성 (3개, 상호 배타)
| 잡 | 트리거 | 게이트 | 권한 | 시크릿 | 비고 |
|----|--------|--------|------|--------|------|
| `multi_agent` | 6h cron 또는 dispatch profile `full`/`multi-agent` | `OPS_MULTI_AGENT_SCHEDULE != 'false'` (기본 ON) | `contents:read`+`actions:write`+`issues:write` | job-level | 전체 roundtable + 아티팩트 + 실패 시 이슈 생성 |
| `priority` | daily cron(`0 4`) 또는 dispatch profile `priority` | `OPS_PRIORITY_LOOP_SCHEDULE == 'true'` (기본 OFF) | `contents:read` | Slack만 | `--skip-sentry --skip-uiux`, ruff+mypy 설치, rc 캡처 후 non-zero면 RED |
| `on_demand` | `repository_dispatch`(`ai_ops_task`) 또는 dispatch profile `full` | — | `contents:read` | **step-scoped** | 신뢰할 수 없는 경로에서 도달 가능한 유일한 잡. RUN_* = inputs → client_payload → 'true' |

### 보안 불변식 (회귀 금지)
- `actions:write` / `issues:write`는 **오직 `multi_agent`** 잡에만 존재하며,
  신뢰할 수 없는 `repository_dispatch` 경로에서 **도달 불가**하다.
- `on_demand`의 시크릿은 **step-scoped**(MED-2 하드닝)로, job-level env에는 비-시크릿
  토글과 boolean has-secret 플래그(`secrets.X != ''`)만 둔다. 실제 시크릿 값은
  이를 사용하는 step에만 부여한다.
- 회귀 가드: `scripts/tests/test_ci_ops_orchestrator_partition_guard.py`.

### Slack 연동
- AI Gateway 사용
- Secrets: `AI_GATEWAY_URL`, `AI_GATEWAY_TOKEN`, `SLACK_CHANNEL_ID_OPS`

### repository_dispatch payload 예시 (on_demand)
```json
{
  "event_type": "ai_ops_task",
  "client_payload": {
    "run_lint_checks": "true",
    "run_vercel_checks": "false",
    "auto_recover_gha": "true"
  }
}
```

---

## 5. Daily News (daily-news.yml)

> **Deprecated:** GitHub `schedule` 트리거가 주석 처리되어 수동 `workflow_dispatch`
> 전용입니다. 스케줄 자동 발행은 `ai-blogwatcher.yml`(schedule `0 0 * * *`, 09:00 KST)이
> 담당합니다. 30일+ 미사용 시 제거 후보(2026-07-07 기준 마지막 실행 2026-03-02).

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 기술/보안 뉴스 자동 수집 및 초안 생성 (수동 전용, deprecated) |
| **트리거** | workflow_dispatch |
| **출력** | PR with draft posts |

### 스케줄 운영

- 서버 상시 가동 환경에서는 GitHub schedule 대신 로컬 크론을 사용합니다.
- 로컬 09:00 자동 포스팅/품질 점검 실행: `bash scripts/install_morning_cron.sh`
- 실행 스크립트: `scripts/morning_autopost_cron.sh`
- 하이브리드 동작: 크론이 로컬에서 포스팅/품질검증/커밋·푸시를 수행하고, 푸시 후 `slack-post-notify.yml`, `buttondown-notify.yml`, `monitoring.yml`를 GitHub Actions로 트리거합니다.
- 크론 실행 시 malformed Liquid include 자동 정리(`scripts/fix_malformed_liquid_includes.py`)와 Ops roundtable(`scripts/ops_health_orchestrator.py`)를 함께 수행합니다.
- AI 강화 모드는 `USE_AI=auto|claude|gemini|gpt-5.4|codex-medium|deepseek|none`로 제어하며, 기본값은 `auto`입니다.
- `auto` 모드는 Claude 우선, Gemini 차선, OpenAI Codex/DeepSeek 폴백 순서로 동작합니다.

### 수동 실행 옵션
```yaml
workflow_dispatch:
  inputs:
    hours: '24'        # 뉴스 수집 기간
    sources: ''        # 특정 소스만 (비워두면 전체)
    use_ai: 'true'     # AI 요약 사용 여부
    max_posts: '10'    # 최대 초안 수
```

### 실행 흐름
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Collect News   │ ──▶ │ Generate Draft  │ ──▶ │   Create PR     │
│                 │     │                 │     │                 │
│ • RSS feeds     │     │ • Gemini API    │     │ • Auto PR       │
│ • 15+ sources   │     │ • AI summary    │     │ • Review labels │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 출력
- `_data/collected_news.json`: 수집된 뉴스 데이터
- `_drafts/*.md`: 생성된 초안
- PR: `drafts/daily-news-{run_number}` 브랜치

---

## 6. Generate Images (generate-images.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | AI 기반 포스트 이미지 생성 |
| **트리거** | workflow_dispatch만 (비용 관리) |
| **AI 서비스** | Gemini API |

### 수동 실행 옵션
```yaml
workflow_dispatch:
  inputs:
    post_file: ''      # 특정 포스트 파일명
    image_type: 'post' # post, segment, both
    force: false       # 기존 이미지 덮어쓰기
```

### 실행 흐름
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ Verify API Key  │ ──▶ │ Generate Image  │ ──▶ │ Upload Artifact │
│                 │     │                 │     │                 │
│ • GEMINI_API_KEY│     │ • generate_     │     │ • 7일 보관      │
│ • format check  │     │   post_images   │     │ • PNG/JPG       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 비용 관리
- `workflow_dispatch`만 사용 (자동 트리거 없음)
- 아티팩트 7일 보관 후 자동 삭제
- API 사용량 모니터링 권장

---

## 7. Sentry Release (sentry-release.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 배포 시 Sentry 릴리스 생성 |
| **트리거** | 배포 성공 시 |
| **도구** | sentry-cli |

### 필요 Secrets
```yaml
SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}
```

### 기능
- 새 릴리스 생성
- 커밋 연결 (--auto)
- 릴리스 완료 처리

---

## 8. AI Video Gen (ai-video-gen.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 포스트 기반 비디오 생성 |
| **트리거** | workflow_dispatch |
| **출력** | 비디오 파일 |

### 특징
- 실험적 기능
- 높은 리소스 사용
- 수동 실행만 지원

---

## Secrets 관리 요약

### 필수 Secrets
| Secret | 용도 | 워크플로우 |
|--------|------|-----------|
| GEMINI_API_KEY | AI 이미지/요약 | generate-images, daily-news (deprecated) |
| SENTRY_* | 에러 추적 | sentry-release |
| BUTTONDOWN_API_KEY | 이메일 | buttondown-notify |

### SNS Secrets
| Secret | 용도 | 워크플로우 |
|--------|------|-----------|
| TWITTER_* | Twitter/X | sns-share |
| FACEBOOK_* | Facebook | sns-share |
| LINKEDIN_* | LinkedIn | sns-share |

### Secrets 설정 방법
```bash
# GitHub CLI
gh secret set SECRET_NAME --body 'value'

# 또는 GitHub UI
# Settings → Secrets and variables → Actions → New repository secret
```

---

## 워크플로우 실행

### CLI로 수동 실행
```bash
# Jekyll 빌드
gh workflow run jekyll.yml

# 이미지 생성
gh workflow run generate-images.yml -f post_file="2026-01-22-Example.md" -f image_type="post"

# 뉴스 수집
gh workflow run daily-news.yml -f hours="48" -f use_ai="true"
```

### 실행 상태 확인
```bash
# 최근 실행 목록
gh run list --limit 10

# 특정 실행 로그
gh run view [run-id] --log

# 실행 중인 워크플로우 확인
gh run list --status in_progress
```

---

## 관련 문서

- [Architecture](architecture.md)
- [Operations](operations.md)
- [PDCA 기능별 문서](../pdca/README.md)
