# Ultrawork Loop

Continuous ops loop that uses OpenCode + OpenClaw + Slack for prioritization and fast fixes.

## Goals
- Maintain a tight priority queue (P0/P1/P2)
- Keep checks running on a cadence
- Post actionable summaries to Slack
- Iterate until no P0/P1 issues remain

## Loop Steps
1. Run the ultrawork checks:
   ```bash
   python3 scripts/ultrawork_loop.py
   ```
2. Parse failures and group by priority.
3. For P0/P1 items, either:
   - Fix immediately in the repo, or
   - Open a targeted task/issue with clear owners.
4. Re-run checks until the priority drops to P2.
5. Post the summary to Slack (via OpenClaw gateway) when available.

## Slack Posting (OpenClaw Gateway)
Required secrets:
- OPENCLAW_GATEWAY_URL
- OPENCLAW_GATEWAY_TOKEN
- SLACK_CHANNEL_ID_OPS

The GitHub workflow `ultrawork-loop.yml` posts the summary automatically when secrets are set.

## Notes
- Keep iterations small and targeted.
- Prefer local scripts (no paid API cost) when possible.
- Mask any sensitive data in logs.
