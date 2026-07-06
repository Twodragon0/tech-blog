#!/usr/bin/env python3
"""CI regression guard: the GH Pages backup must have a self-healing scheduled deploy.

Why this guard exists
---------------------
The AI BlogWatcher publishes the daily digest with a ``github-actions[bot]``
``git push`` on its 00:00 UTC schedule (``ai-blogwatcher.yml`` trusted path). A
push authenticated with the ``GITHUB_TOKEN`` does NOT trigger other workflows
(GitHub's recursion-prevention rule), so that push never fires the ``push:``
trigger in ``deploy-pages.yml`` — and the GH Pages backup
(twodragon0.github.io/tech-blog) goes stale until the next human/PAT content
push. Observed 2026-07-06: the 07-06 digest was live on Vercel but missing from
the backup for hours.

The fix (Option C) is a ``schedule:`` cron in ``deploy-pages.yml`` (30 min after
the digest publish) that rebuilds the backup regardless of who pushed. That
self-healing property disappears *silently* if someone drops the ``schedule:``
trigger or its ``cron`` entry. This guard makes that removal fail loudly.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control). Direction: presence
assertion — any removal of the scheduled trigger trips this. If the schedule is
intentionally reworked (e.g. moved into a reusable ``workflow_call`` invoked by
blogwatcher, Option A), update this guard in the same PR and say why.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "deploy-pages.yml"


def _noncomment_lines(text: str) -> str:
    """The workflow text with comment-only lines removed.

    Asserting on real YAML (not surrounding ``#`` prose that also mentions
    "schedule"/"cron") keeps the guard honest: a stale comment must not keep it
    green after the real trigger is deleted. (Skill rule: never match commentary.)
    Inline trailing comments on a real key line are preserved because that line
    is not comment-only.
    """
    return "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
    )


class TestPagesBackupScheduleGuard:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_schedule_trigger_present(self):
        body = _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))
        assert re.search(r"^\s*schedule:\s*$", body, re.MULTILINE), (
            "deploy-pages.yml lost its 'schedule:' trigger. The GH Pages backup "
            "self-heals via a scheduled deploy because a github-actions[bot] "
            "push (blogwatcher digest) cannot trigger the push: workflow. Without "
            "the schedule the backup goes stale after every bot-published digest. "
            "If moved to a reusable workflow (Option A), update this guard."
        )

    def test_schedule_has_cron(self):
        body = _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))
        crons = re.findall(r"-\s*cron:\s*[\"']([^\"']+)[\"']", body)
        assert crons, (
            "the schedule: trigger has no 'cron:' entry; the backup would never "
            "auto-deploy. Re-add a cron (e.g. '30 0 * * *', 30 min after the "
            "blogwatcher 00:00 UTC digest). If intentional, update this guard."
        )

    def test_manual_dispatch_still_available(self):
        """workflow_dispatch must remain so the backup can be force-deployed.

        The 2026-07-06 recovery used ``gh workflow run deploy-pages.yml``; keep
        that manual escape hatch alongside the scheduled trigger.
        """
        body = _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))
        assert re.search(r"^\s*workflow_dispatch:\s*$", body, re.MULTILINE), (
            "deploy-pages.yml lost workflow_dispatch; the manual backup-deploy "
            "escape hatch is gone. If intentional, update this guard."
        )
