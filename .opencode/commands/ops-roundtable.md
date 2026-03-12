---
description: Multi-agent ops/security/uiux roundtable with auto-recovery
agent: lead
---

Run:
`python3 scripts/ops_health_orchestrator.py --auto-recover-gha`

Treat checks as three reviewers:
- OpsAgent (lint, Vercel, GitHub Actions)
- SecurityAgent (Sentry)
- UiUxAgent (performance)

Synthesize as Moderator with prioritized actions and continue until no unresolved P0/P1 items remain.
Post summary through AI Gateway Slack flow if configured.

Output `<promise>OPS_ROUNDTABLE_COMPLETE</promise>` when complete.
