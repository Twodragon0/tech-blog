---
description: Multi-agent ops/security roundtable with auto-recovery
agent: lead
---

Run:
`python3 scripts/ops_health_orchestrator.py --auto-recover-gha`

Treat checks as two reviewers:
- OpsAgent (lint, Vercel, GitHub Actions)
- SecurityAgent (Sentry)

UiUxAgent was removed 2026-09-18 with `check_uiux()`. Core Web Vitals are
measured by `lighthouse-ci.yml` and `lighthouse.yml`, not here — see the
PAGESPEED_API_KEY entry in `.github/docs/SECRETS_MANAGEMENT.md`.

Synthesize as Moderator with prioritized actions and continue until no unresolved P0/P1 items remain.
(The AI Gateway Slack steps were removed 2026-09-18 — never provisioned,
never executed. The report reaches humans via $GITHUB_STEP_SUMMARY, the
artifact, and the inlined failure-issue body.)

Output `<promise>OPS_ROUNDTABLE_COMPLETE</promise>` when complete.
