# Vercel Monitoring & Performance Tracking

Comprehensive monitoring for Vercel deployments, build performance, and Core Web Vitals.

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
| `PAGESPEED_API_KEY` | Google PageSpeed Insights | No (optional) |

**Obtaining Keys:**

- **Sentry**: Visit Settings → Integrations → Tokens
- **PageSpeed Insights**: [Google Cloud Console](https://console.cloud.google.com)

## Metrics Tracked

### 1. Vercel Deployment Status
- Latest deployment URL and state
- Recent deployment history (last 5)
- Success/failure indicators

### 2. Core Web Vitals (CWV)
Measured via Google PageSpeed Insights API (requires `PAGESPEED_API_KEY`):

| Metric | Abbreviation | Good | Needs Improvement | Poor |
|--------|--------------|------|-------------------|------|
| **Largest Contentful Paint** | LCP | < 2.5s | 2.5-4.0s | > 4.0s |
| **First Input Delay** | FID | < 100ms | 100-300ms | > 300ms |
| **Cumulative Layout Shift** | CLS | < 0.1 | 0.1-0.25 | > 0.25 |

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
LCP_THRESHOLD=2500      # ms
FID_THRESHOLD=100       # ms
CLS_THRESHOLD=0.1       # unitless
BUILD_TIME_THRESHOLD=120 # seconds
```

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

### "PAGESPEED_API_KEY not configured"
1. Create API key in [Google Cloud Console](https://console.cloud.google.com)
2. Set environment variable:
   ```bash
   export PAGESPEED_API_KEY="your-api-key"
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
          PAGESPEED_API_KEY: ${{ secrets.PAGESPEED_API_KEY }}

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
- **LCP**: < 2.5 seconds
- **FID**: < 100 milliseconds
- **CLS**: < 0.1

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
