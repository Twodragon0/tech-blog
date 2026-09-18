# Vercel Monitoring & Performance Tracking

Comprehensive monitoring for Vercel deployments, build performance, and error tracking.
(Core Web Vitals live in the Lighthouse workflows — see "2. Core Web Vitals" below.)

## Quick Start

```bash
# Basic monitoring
./scripts/monitor_vercel_builds.sh

# Monitoring with specific deployment
./scripts/monitor_vercel_builds.sh https://tech.2twodragon.com

# Alert-only mode (only show issues)
./scripts/monitor_vercel_builds.sh --alert-only

# Detailed analysis
./scripts/monitor_vercel_builds.sh --detailed
```

## Prerequisites

### Required Tools
- `curl` - HTTP client (usually pre-installed)
- Vercel CLI: `npm i -g vercel`
- `jq` - JSON processor: `brew install jq` (macOS) or `apt-get install jq` (Linux)

### Authentication

**Vercel Login:**
```bash
vercel login
```

## Environment Variables

Set these in your `.env` or CI/CD platform for full monitoring capabilities:

| Variable | Purpose | Required |
|----------|---------|----------|
| `VERCEL_TOKEN` | Vercel API authentication | No (uses Vercel CLI auth) |
| `SENTRY_AUTH_TOKEN` | Sentry error tracking | No (optional) |
| `SENTRY_ORG` | Sentry organization | No (optional) |
| `SENTRY_PROJECT` | Sentry project ID | No (optional) |

**Obtaining Keys:**

- **Sentry**: Visit Settings → Integrations → Tokens

## Metrics Tracked

### 1. Vercel Deployment Status
- Latest deployment URL and state
- Recent deployment history (last 5)
- Success/failure indicators

### 2. Core Web Vitals (CWV) — 이 스크립트가 아니라 Lighthouse 워크플로가 잰다

`monitor_vercel_builds.sh` 의 PageSpeed Insights 블록과 `PAGESPEED_API_KEY` 는
2026-09-18 에 제거됐다. 키가 등록된 적이 없어 늘 건너뛰었고, 등록했다면 이 저장소가
이미 60회 실측으로 폐기한 절대값 임계값(performance 0.55~0.86 변동, LCP 이봉분포의
두 봉우리가 모두 2500ms 초과)을 P1 로 판정해 6시간 주기로 ops 이슈를 열었을 것이다.
근거와 되돌리는 조건: `.github/docs/SECRETS_MANAGEMENT.md` 의 PAGESPEED_API_KEY 항목.

CWV 는 다음 두 워크플로가 잰다:

| 워크플로 | 트리거 | 무엇을 |
|---|---|---|
| `lighthouse-ci.yml` | PR | LCP 를 head 대 base 로 5회 비교, 회귀 200ms 초과 시 실패 |
| `lighthouse.yml` | push + PR | CLS 절대 예산 0.05, accessibility/best-practices/SEO 카테고리 게이트 |

절대 LCP 와 performance 점수는 **의도적으로** 게이트가 아니다. 러너 성능 추첨에
좌우돼 무작위 red 를 만들기 때문이며, 대신 로그로 계속 누적된다.

### 3. Sentry Error Tracking
Monitor unresolved errors in production (requires Sentry credentials):

- Count of unresolved issues
- Top 5 issues by event frequency
- Issue titles and event counts

### 4. Build Performance
- Build time (target < 120 seconds)
- Deployment success rate (target > 99%)
- Function execution metrics

### 5. Environment Configuration
Checks for required API keys and Vercel authentication

## Alert Thresholds

Configurable in `scripts/monitor_vercel_builds.sh`:

```bash
BUILD_TIME_THRESHOLD=120 # seconds
```

LCP/FID/CLS 임계값은 2026-09-18 에 제거됐다 — 이 스크립트가 재지 않는 목표를 출력하고
있었다. CWV 임계값은 `lighthouse-ci.yml`(LCP 회귀 200ms) 과 `lighthouse.yml`(CLS 0.05)
에 있다.

## Output Modes

### Standard Output (Default)
Shows detailed monitoring report with all checks:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Environment Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Environment checks passed
```

### Alert-Only Mode (`--alert-only`)
Shows only failures and issues:
```bash
./scripts/monitor_vercel_builds.sh --alert-only
# Output only includes ❌ ALERT and ⚠️  WARNING messages
```

### Detailed Mode (`--detailed`)
Extended analysis with additional metrics and recommendations.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed |
| 1 | One or more issues found |

## Common Issues & Troubleshooting

### "Vercel CLI not installed"
```bash
npm i -g vercel
```

### "Not logged in to Vercel"
```bash
vercel login
```

### "jq: command not found"
```bash
# macOS
brew install jq

# Linux
apt-get install jq

# Windows (via Chocolatey)
choco install jq
```

### "Sentry connection failed"
Verify credentials:
```bash
curl -s -H "Authorization: Bearer $SENTRY_AUTH_TOKEN" \
  "https://sentry.io/api/0/organizations/$SENTRY_ORG/" | jq .
```

## CI/CD Integration

### GitHub Actions

Monitor deployments automatically on every production deployment:

```yaml
# .github/workflows/monitoring.yml
name: Production Monitoring

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Vercel monitoring
        run: bash scripts/monitor_vercel_builds.sh --alert-only
        env:
          VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}

      - name: Create issue on failure
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Production Monitoring Alert',
              body: 'Deployment or performance checks failed. See workflow run for details.',
              labels: ['monitoring', 'alert']
            })
```

### Local Development

Add to your shell profile for quick access:

```bash
alias monitor='./scripts/monitor_vercel_builds.sh'
alias monitor-alert='./scripts/monitor_vercel_builds.sh --alert-only'
```

## Performance Targets

### Build Metrics
- **Build Time**: < 2 minutes
- **Deployment Success**: > 99%
- **Simultaneous Builds**: Up to 12 (Pro plan)

### User Experience (Core Web Vitals)
`lighthouse-ci.yml` / `lighthouse.yml` 가 강제한다 (위 "2. Core Web Vitals" 참조).
- **LCP**: 절대값이 아니라 head 대 base 회귀 200ms 로 게이트
- **CLS**: < 0.05 (절대 예산)
- **INP**: 미측정 — FID 는 2024 년에 은퇴했고 Lighthouse 감사 항목이 아니다

### Error Tracking
- **Unresolved Issues**: Keep < 10 at any time
- **Error Rate**: < 0.1% of requests

## Manual Vercel Commands

```bash
# View real-time logs
vercel logs --follow

# Get deployment details
vercel inspect https://tech.2twodragon.com

# List environment variables
vercel env ls

# View recent deployments
vercel ls --limit 10

# Trigger rebuild
vercel --prod

# Check account
vercel whoami
```

## Related Documentation

- [Vercel Official Docs](https://vercel.com/docs)
- [Google PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started)
- [Sentry Documentation](https://docs.sentry.io/)
- [Core Web Vitals Guide](https://web.dev/vitals/)

## Future Enhancements

- [ ] Export metrics to monitoring dashboard (DataDog, New Relic)
- [ ] Slack/email alerts on threshold violations
- [ ] Historical trend analysis
- [ ] Performance regression detection
- [ ] Automated performance reports

## Notes

- Monitoring script runs locally or in CI/CD
- No persistent state or database required
- All API calls are read-only (safe to run frequently)
- Sensitive information is masked in output
