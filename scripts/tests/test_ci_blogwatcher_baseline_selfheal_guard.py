#!/usr/bin/env python3
"""CI regression guard: the BlogWatcher publish step must self-heal the quality baseline.

Why this guard exists
---------------------
The AI BlogWatcher publishes the daily digest by committing a new
``_posts/YYYY-MM-DD-*.md`` (``ai-blogwatcher.yml``, "Commit and publish" step).
That post is NOT scored into ``scripts/tests/fixtures/quality_baseline.json`` by
the publish path, so ``test_regen_quality_baseline`` (which asserts
``regen_quality_baseline.py --check`` exits 0) goes red on ``main`` the moment
the digest lands — and that red ``build`` propagates to every branch rebased on
top. Observed 2026-07-28: the 07-28 digest broke ``main``'s build and blocked
PR #470 until the baseline was refreshed by hand.

The fix is a self-healing step: the publish job runs
``regen_quality_baseline.py`` and stages the refreshed baseline into the SAME
digest commit, so both the trusted push-to-main and the untrusted
``repository_dispatch`` PR path stay green. That property disappears *silently*
if someone drops the regen call or the ``git add`` of the baseline. This guard
makes that removal fail loudly.

Direction: presence assertion — any removal of the regen-and-stage pair trips
this. If the self-heal is intentionally reworked (e.g. moved to a post-publish
job or a reusable workflow), update this guard in the same PR and say why.

See also memory: regen-quality-baseline-stale-cron.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"
BASELINE_JSON = "scripts/tests/fixtures/quality_baseline.json"
REGEN_SCRIPT = "scripts/regen_quality_baseline.py"


def _noncomment_lines(text: str) -> str:
    """The workflow text with comment-only lines removed.

    Asserting on real YAML (not surrounding ``#`` prose that also names the
    baseline/regen script) keeps the guard honest: a stale comment must not keep
    it green after the real step is deleted. Inline trailing comments on a real
    key line are preserved because that line is not comment-only.
    """
    return "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
    )


class TestBlogwatcherBaselineSelfHealGuard:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_regen_baseline_invoked(self):
        body = _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))
        assert re.search(rf"python3?\s+{re.escape(REGEN_SCRIPT)}", body), (
            "ai-blogwatcher.yml no longer runs regen_quality_baseline.py in the "
            "publish step. A cron-added digest that is missing from the committed "
            "quality baseline turns test_regen_quality_baseline red on main and "
            "on every rebased PR. Re-add the regen call before the commit, or if "
            "moved to another job update this guard."
        )

    def test_baseline_staged_into_commit(self):
        body = _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))
        assert re.search(rf"git add\s+[\"']?{re.escape(BASELINE_JSON)}", body), (
            "ai-blogwatcher.yml runs the baseline regen but no longer stages "
            f"{BASELINE_JSON} into the digest commit, so the self-heal never "
            "reaches main/PR. Re-add the 'git add' of the baseline JSON."
        )

    def test_regen_precedes_commit(self):
        """The regen + stage must run before 'git commit' so the refreshed
        baseline is part of the digest commit, not a dangling working-tree edit.
        """
        body = _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))
        regen = re.search(rf"python3?\s+{re.escape(REGEN_SCRIPT)}", body)
        commit = re.search(r"git commit\b", body)
        assert regen and commit, "expected both the regen call and a 'git commit'"
        assert regen.start() < commit.start(), (
            "regen_quality_baseline.py must run BEFORE 'git commit' so the "
            "refreshed baseline is staged into the same digest commit. It is "
            "currently ordered after the commit, which leaves the baseline "
            "change uncommitted (main stays red)."
        )
