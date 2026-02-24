# Ops Roundtable

Multi-agent operations loop focused on reliable remediation across lint, deployment, CI, security, and UI/UX.

## Goal
- Keep operational priority at P2 by continuously removing P0/P1 items.
- Auto-recover common GitHub Actions failures.
- Gate production quality with Vercel, Sentry, and PageSpeed signals.

## Agent Roles
- OpsAgent: lint/type checks, Vercel health, GitHub Actions workflow health.
- SecurityAgent: unresolved Sentry issue review and risk prioritization.
- UiUxAgent: Core Web Vitals and performance score review.
- Moderator: merge recommendations into a single action plan.

## Run
```bash
python3 scripts/ops_health_orchestrator.py --auto-recover-gha
```

## Optional Outputs
```bash
python3 scripts/ops_health_orchestrator.py \
  --auto-recover-gha \
  --output reports/ops-roundtable.md \
  --json-output reports/ops-roundtable.json
```

## Required Secrets
- VERCEL_TOKEN
- GITHUB_TOKEN (or GH_TOKEN)
- SENTRY_AUTH_TOKEN
- SENTRY_ORG
- SENTRY_PROJECT
- PAGESPEED_API_KEY

## Exit Policy
- Exit 0: no unresolved failures.
- Exit 1: unresolved P1 failures remain.
- Exit 2: unresolved P0 failure detected.
