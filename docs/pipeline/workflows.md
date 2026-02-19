# GitHub Actions Workflows 상세

> 모든 워크플로우의 상세 설명 및 설정

## 워크플로우 목록

```
.github/workflows/
├── jekyll.yml              # 메인: Jekyll 빌드 및 GitHub Pages 배포
├── sns-share.yml           # SNS 자동 공유
├── buttondown-notify.yml   # 이메일 뉴스레터
├── daily-news.yml          # 일일 뉴스 수집
├── ops-priority-loop.yml   # Ops 우선순위 점검
├── ultrawork-loop.yml      # Ultrawork 지속 루프
├── ai-ops-on-demand.yml    # AI 온디맨드 운영 점검
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

## 4. Ops Priority Loop (ops-priority-loop.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 자동 점검 + 우선순위 산정 + Slack 알림 |
| **트리거** | schedule, workflow_dispatch |
| **게이트** | `OPS_PRIORITY_LOOP_SCHEDULE=true` |
| **타임아웃** | 15분 |

### 실행 내용
- `scripts/priority_ops_check.py` 실행
- 기본 체크: `check_posts.py`, `verify_images_unified.py --missing`
- Vercel 체크는 기본 비활성 (`RUN_VERCEL_CHECKS=false`)

### Slack 연동
- OpenClaw Gateway 사용
- Secrets: `OPENCLAW_GATEWAY_URL`, `OPENCLAW_GATEWAY_TOKEN`, `SLACK_CHANNEL_ID_OPS`

---

## 5. Ultrawork Loop (ultrawork-loop.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 지속 점검 + 우선순위 산정 + Slack 알림 |
| **트리거** | schedule, workflow_dispatch |
| **게이트** | `ULTRAWORK_LOOP_SCHEDULE=true` |
| **타임아웃** | 20분 |

### 실행 내용
- `scripts/ultrawork_loop.py` 실행
- 기본 체크: `check_posts.py`, `fix_links_unified.py --check`, `verify_images_unified.py --missing`
- Vercel 체크는 기본 비활성 (`RUN_VERCEL_CHECKS=false`)

### Slack 연동
- OpenClaw Gateway 사용
- Secrets: `OPENCLAW_GATEWAY_URL`, `OPENCLAW_GATEWAY_TOKEN`, `SLACK_CHANNEL_ID_OPS`

---

## 6. AI Ops On Demand (ai-ops-on-demand.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 온디맨드 점검 수행 후 Slack 보고 |
| **트리거** | `repository_dispatch` (`ai_ops_task`), workflow_dispatch |
| **타임아웃** | 15분 |

### repository_dispatch payload 예시

```json
{
  "event_type": "ai_ops_task",
  "client_payload": {
    "run_post_checks": "true",
    "run_image_checks": "true",
    "run_vercel_checks": "false"
  }
}
```

### 필요 Secrets
```yaml
BUTTONDOWN_API_KEY: ${{ secrets.BUTTONDOWN_API_KEY }}
SITE_URL: "https://tech.2twodragon.com"
```

---

## 7. Daily News (daily-news.yml)

### 개요
| 항목 | 값 |
|------|-----|
| **목적** | 기술/보안 뉴스 자동 수집 및 초안 생성 |
| **트리거** | schedule (daily KST 09:00), workflow_dispatch |
| **출력** | PR with draft posts |

### 스케줄
```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00 = KST 09:00
```

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

## 8. Generate Images (generate-images.yml)

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

## 9. Sentry Release (sentry-release.yml)

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

## 10. AI Video Gen (ai-video-gen.yml)

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
| GEMINI_API_KEY | AI 이미지/요약 | generate-images, daily-news |
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
