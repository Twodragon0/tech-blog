---
description: Continuous ops checks and prioritization loop with AI Gateway and Slack
agent: lead
---

Run an ultrawork reliability loop focused on prioritized remediation.

Run:
`python3 scripts/ops_health_orchestrator.py --auto-recover-gha`

Then:
1. Generate a priority summary.
2. Validate logs and prioritize actionable fixes.
3. Post summary to Slack via AI Gateway if configured.
4. Keep iterating until no P0/P1 items remain.

Output `<promise>ULTRAWORK_LOOP_COMPLETE</promise>` when complete.
