# Ralph Loop - Continuous Post Improvement System

**Last Updated**: 2026-01-23

Sisyphus 모드에서 Ralph Loop를 사용하여 블로그 포스트를 지속적으로 수집하고 개선하는 시스템입니다.

## Overview

Ralph Loop는 다음과 같은 자동화 워크플로우를 제공합니다:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RALPH LOOP WORKFLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                 │
│   │  RSS Feeds   │    │   Collect    │    │   Generate   │                 │
│   │  (50+ src)   │───▶│    News      │───▶│    Drafts    │                 │
│   └──────────────┘    └──────────────┘    └──────────────┘                 │
│                              │                   │                          │
│                              ▼                   ▼                          │
│                    ┌──────────────────────────────────┐                     │
│                    │     _data/collected_news.json    │                     │
│                    │     _drafts/prompts/*.md         │                     │
│                    └──────────────┬───────────────────┘                     │
│                                   │                                         │
│   ┌───────────────────────────────┼───────────────────────────────────┐    │
│   │                               ▼         RALPH LOOP                │    │
│   │  ┌────────────┐    ┌────────────┐    ┌────────────┐              │    │
│   │  │  AI Write  │───▶│  Validate  │───▶│  Quality   │              │    │
│   │  │   Post     │    │   Post     │    │   Score    │              │    │
│   │  └────────────┘    └────────────┘    └─────┬──────┘              │    │
│   │        ▲                                   │                      │    │
│   │        │                                   ▼                      │    │
│   │        │           ┌─────────────────────────────┐               │    │
│   │        │           │  Score >= 80?               │               │    │
│   │        │           │  ┌───────┐    ┌───────┐    │               │    │
│   │        └───────────│  │  NO   │    │  YES  │    │               │    │
│   │      (Improve)     │  └───┬───┘    └───┬───┘    │               │    │
│   │                    │      │            │         │               │    │
│   │                    └──────┼────────────┼─────────┘               │    │
│   │                           │            │                         │    │
│   └───────────────────────────┼────────────┼─────────────────────────┘    │
│                               │            │                              │
│                               ▼            ▼                              │
│                    ┌────────────┐    ┌────────────┐                       │
│                    │  Retry or  │    │  Publish   │                       │
│                    │  Flag for  │    │  to _posts │                       │
│                    │  Manual    │    └────────────┘                       │
│                    └────────────┘                                         │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install feedparser requests beautifulsoup4 frontmatter
```

### 2. Run the Ralph Loop

```bash
# OpenCode CLI에서 실행
/improve-posts

# 또는 직접 스크립트 실행
python3 scripts/collect_tech_news.py --hours 24
python3 scripts/generate_news_draft.py --prepare --max-posts 5
python3 scripts/validate_post_quality.py --drafts
```

## Configuration

### OpenCode Configuration

설정 파일: `.opencode/opencode.json`

```json
{
  "agent": {
    "mode": "sisyphus",
    "model": "claude-sonnet-4-20250514"
  },
  "ralphLoop": {
    "enabled": true,
    "defaultMaxIterations": 50,
    "defaultCompletionPromise": "DONE"
  },
  "qualityGates": {
    "scoreThreshold": 80,
    "maxRetries": 3
  }
}
```

### Quality Criteria

| Criterion | Weight | Threshold | Description |
|-----------|--------|-----------|-------------|
| Content Length | 20% | >= 3000 chars | 본문 길이 (마크다운 문법 제외) |
| Tables | 15% | >= 2 tables | 마크다운 테이블 개수 |
| Code Blocks | 15% | >= 1 block | 코드 블록 개수 |
| Checklist | 10% | >= 1 item | 체크리스트 항목 |
| Front Matter | 20% | All required | title, date, category, tags, excerpt |
| English Images | 10% | No Korean | 이미지 파일명에 한글 없음 |
| Valid Links | 10% | No broken | 깨진 링크 없음 |

## Commands

### /improve-posts

RSS 뉴스를 수집하고 고품질 블로그 포스트를 생성합니다.

```bash
/improve-posts                           # 기본 설정 (24시간, 5개 포스트)
/improve-posts --hours=48                # 48시간 뉴스 수집
/improve-posts --max-posts=10            # 최대 10개 포스트
/improve-posts --quality-threshold=90    # 90점 이상만 통과
```

### /collect-news

뉴스만 수집합니다 (포스트 생성 없음).

```bash
/collect-news                    # 24시간 뉴스
/collect-news --hours=168        # 1주일 뉴스
/collect-news --sources=aws,gcp  # 특정 소스만
```

### /validate-posts

기존 포스트의 품질을 검증합니다.

```bash
/validate-posts                  # 모든 포스트
/validate-posts --drafts         # 초안만
/validate-posts --threshold=90   # 90점 기준
```

## Workflow Details

### Phase 1: News Collection

```bash
python3 scripts/collect_tech_news.py --hours 24
```

**Output**: `_data/collected_news.json`

```json
{
  "collected_at": "2026-01-23T10:00:00+00:00",
  "total_items": 24,
  "items": [
    {
      "id": "abc123",
      "title": "AWS Security Best Practices",
      "url": "https://...",
      "source": "aws_security",
      "category": "security",
      "priority": 1
    }
  ]
}
```

### Phase 2: Draft Generation

```bash
python3 scripts/generate_news_draft.py --prepare --max-posts 5
```

**Output**: `_drafts/prompts/{date}-{title}_prompt.md`

프롬프트에는 다음이 포함됩니다:
- 뉴스 메타데이터
- 원문 콘텐츠 (최대 8000자)
- 관련 기존 포스트
- 카테고리별 분석 가이드
- 포스트 구조 템플릿
- AI 요약 카드 HTML
- 품질 체크리스트

### Phase 3: AI Writing & Improvement

Ralph Loop가 각 프롬프트에 대해:

1. AI가 포스트 생성
2. 품질 검증 실행
3. 점수 < 80이면 개선 후 재검증
4. 최대 3회 시도 후 수동 검토로 전환

### Phase 4: Publication

품질 검증 통과 후:
1. `_drafts/` → `_posts/` 이동
2. SVG 이미지 생성
3. 링크 검증
4. 처리된 뉴스 ID 기록

## Quality Validation

### Running Validation

```bash
# 모든 포스트 검증
python3 scripts/validate_post_quality.py

# 초안만 검증
python3 scripts/validate_post_quality.py --drafts

# JSON 출력
python3 scripts/validate_post_quality.py --json

# 실패한 것만 표시
python3 scripts/validate_post_quality.py --failed-only
```

### Sample Output

```
Validating 10 posts (threshold: 80)
============================================================
[PASS]  85/100 - 2026-01-23-AWS_Security_Best_Practices.md
[FAIL]  65/100 - 2026-01-23-Cloud_Migration_Guide.md
       -> Add 1200+ more characters of content (currently 1800)
       -> Add 1+ more markdown table(s) for data organization
[PASS]  92/100 - 2026-01-22-Kubernetes_Security.md
============================================================

Summary:
  Total:   10
  Passed:  8 (80.0%)
  Failed:  2
  Average: 78.5/100
```

### Improvement Suggestions

검증 실패 시 자동으로 개선 제안을 생성합니다:

| Issue | Suggestion |
|-------|------------|
| 짧은 콘텐츠 | "Add 1200+ more characters of content" |
| 테이블 부족 | "Add 1+ more markdown table(s)" |
| 코드 없음 | "Add at least 1 code block with practical examples" |
| 체크리스트 없음 | "Add a checklist section (- [ ] item)" |
| 누락된 메타데이터 | "Add missing front matter: excerpt, tags" |
| 한글 이미지 | "Rename Korean image files to English" |
| 깨진 링크 | "Fix broken/placeholder links" |

## Cost Optimization

Ralph Loop는 비용 최적화를 위해 다음 우선순위로 AI를 사용합니다:

1. **Gemini CLI** (OAuth 2.0) - 무료 ⭐ 최우선
2. **Local Templates** - 비용 없음
3. **Cursor/Claude Console** - 무료 할당량
4. **API Calls** - 마지막 수단

### Configuration

```json
{
  "costOptimization": {
    "priority": ["gemini-cli", "local-templates", "cursor-console", "api-calls"],
    "geminiCli": {
      "enabled": true,
      "timeout": 120
    },
    "apiRateLimiting": {
      "claude": { "maxRequestsPerMinute": 10 },
      "gemini": { "maxRequestsPerMinute": 15 }
    }
  }
}
```

## Monitoring

### Log Files

- `improvement_log.txt` - 상세 작업 로그
- `ai_improvement_log.txt` - AI 개선 작업 로그

### Processed News Tracking

`_data/processed_news_ids.json`에 처리된 뉴스 ID가 저장됩니다.

```json
["abc123", "def456", "ghi789"]
```

이미 처리된 뉴스는 다음 수집에서 제외됩니다.

### Todo Tracking

Ralph Loop 실행 중 TODO 리스트가 실시간으로 업데이트됩니다:

```
[x] Collect news from RSS feeds
[x] Generate draft prompts
[ ] Write post: AWS Security Best Practices
[ ] Validate post quality
[ ] Generate SVG image
[ ] Publish to _posts
```

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| RSS 수집 실패 | 캐시된 데이터 사용 (7일 이내) |
| AI 생성 실패 | 대체 프롬프트로 재시도 |
| 품질 검증 3회 실패 | 수동 검토로 전환 |
| 이미지 생성 실패 | 플레이스홀더 사용, 나중에 생성 |

### Debug Mode

```bash
# 상세 로그 출력
DEBUG=1 python3 scripts/collect_tech_news.py

# Dry run (실제 저장 없음)
python3 scripts/generate_news_draft.py --dry-run
python3 scripts/auto_publish_news.py --dry-run
```

## Integration with Sisyphus

Sisyphus 모드에서 Ralph Loop는:

1. **Intent Recognition**: `/improve-posts` 명령을 연속 작업으로 인식
2. **Background Execution**: explore 에이전트로 코드베이스 분석
3. **Parallel Processing**: 여러 포스트 동시 개선
4. **Quality Gates**: 각 포스트가 검증 통과해야 완료
5. **Progress Tracking**: TODO 리스트 실시간 업데이트
6. **Completion Signal**: 완료 시 `<promise>POSTS_IMPROVED</promise>` 출력

## Related Scripts

| Script | Purpose |
|--------|---------|
| `collect_tech_news.py` | RSS 뉴스 수집 |
| `generate_news_draft.py` | 초안 프롬프트 생성 |
| `auto_publish_news.py` | 자동 발행 (주간 다이제스트) |
| `validate_post_quality.py` | 품질 검증 |
| `ai_improve_posts.py` | AI 기반 포스트 개선 |
| `smart_improve_posts.py` | 템플릿 기반 개선 |
| `generate_post_images.py` | SVG 이미지 생성 |

## News Sources

현재 50개 이상의 RSS 소스에서 뉴스를 수집합니다:

### Security
- AWS Security Blog
- Microsoft Security Blog
- Google Security Blog
- CISA Advisories
- The Hacker News
- Krebs on Security
- OWASP Blog

### Cloud
- AWS Blog
- GCP Blog
- Azure Blog
- AWS Korea Blog

### DevOps
- Kubernetes Blog
- CNCF Blog
- HashiCorp Blog

### Security Vendors
- CrowdStrike
- Palo Alto Networks / Unit 42
- Cloudflare
- Okta
- Zscaler
- Snyk
- Aqua Security
- Sysdig
- Datadog Security Labs
- And more...

### Korean Sources
- GeekNews (긱뉴스)
- SK쉴더스 EQST insight
- KISA 보안 공지

전체 소스 목록은 `python3 scripts/collect_tech_news.py --list-sources`로 확인할 수 있습니다.

## Best Practices

### 1. Daily Workflow

```bash
# 매일 아침 (권장)
/improve-posts --hours=24 --max-posts=3
```

### 2. Weekly Digest

```bash
# 매주 일요일
python3 scripts/collect_tech_news.py --hours=168
python3 scripts/auto_publish_news.py --max-news=15
```

### 3. Quality Focus

```bash
# 고품질 포스트만 발행
/improve-posts --quality-threshold=90
```

### 4. Manual Review

품질 점수가 낮은 포스트는 수동 검토 후 개선합니다:

1. `_drafts/` 폴더에서 해당 포스트 확인
2. 개선 제안 사항 확인
3. 수동으로 콘텐츠 추가/수정
4. `python3 scripts/validate_post_quality.py _drafts/the-post.md` 로 재검증
5. 통과 시 `_posts/`로 이동
