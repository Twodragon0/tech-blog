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
assertion — any removal of the scheduled trigger trips this.

2026-08-27: Option A was added **alongside** the cron rather than replacing it.
The cron alone turned out to be a single point of failure in a way this guard's
original text did not anticipate: GitHub's Actions scheduler emitted no schedule
events repo-wide between 08-26T19:43Z and 08-27T05:50Z, and **missed cycles are
not backfilled**. So on the day the bot published at 07:11Z, the `push:` trigger
was suppressed (bot token) *and* the 00:30Z cron never ran — the backup served
404 for that digest while production served 200.

Two independent paths now, and this guard pins both:

- event-driven: ``ai-blogwatcher.yml`` calls ``deploy-pages.yml`` via
  ``workflow_call`` the moment it publishes;
- backstop: the existing cron, for anything the publish job cannot see.

The subtle part is ``ref``. blogwatcher's publish job runs on the PRE-publish
SHA, so a ``workflow_call`` without ``ref`` rebuilds the corpus *without* the
post that triggered it — and reports success. That failure is invisible in the
Actions tab, which is why it gets its own assertions below.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

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
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


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


class TestPagesBackupEventDrivenPath:
    """The workflow_call path added 2026-08-27, and the `ref` that makes it real."""

    CALLER = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"
    CALLEE_REL = "./.github/workflows/deploy-pages.yml"

    @classmethod
    def _callee(cls) -> dict:
        return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    @classmethod
    def _caller_job(cls) -> dict:
        doc = yaml.safe_load(cls.CALLER.read_text(encoding="utf-8"))
        jobs = {
            n: j
            for n, j in doc["jobs"].items()
            if str(j.get("uses", "")).strip() == cls.CALLEE_REL
        }
        assert jobs, (
            f"no job in ai-blogwatcher.yml calls {cls.CALLEE_REL}. The GH Pages "
            "backup is then back to depending on the cron alone — the exact "
            "single point of failure that produced a 404 backup on 2026-08-27."
        )
        assert len(jobs) == 1, f"expected one caller job, found {sorted(jobs)}"
        return next(iter(jobs.values()))

    def test_callee_exposes_workflow_call_with_ref(self):
        on = self._callee().get(True) or self._callee().get("on") or {}
        call = on.get("workflow_call")
        assert call is not None, (
            "deploy-pages.yml no longer accepts workflow_call, so blogwatcher "
            "cannot deploy the backup at publish time."
        )
        assert "ref" in (call.get("inputs") or {}), (
            "the workflow_call interface lost its `ref` input. The caller runs on "
            "the pre-publish SHA, so without it the backup rebuilds WITHOUT the "
            "new post and the job still goes green."
        )

    def test_checkout_honours_the_ref_input(self):
        """The one line that decides whether the deploy is real or theatre."""
        doc = self._callee()
        steps = doc["jobs"]["build"]["steps"]
        checkout = next(
            (s for s in steps if "checkout" in str(s.get("uses", "")).lower()), None
        )
        assert checkout is not None, "the build job no longer checks out the repo"
        ref = str((checkout.get("with") or {}).get("ref", ""))
        assert "inputs.ref" in ref, (
            f"the checkout ref is {ref!r}. It must consult `inputs.ref`, or the "
            "workflow_call path silently deploys the caller's pre-publish commit "
            "— a green run that leaves the backup exactly as stale as before."
        )

    def test_caller_passes_the_published_sha(self):
        job = self._caller_job()
        ref = str((job.get("with") or {}).get("ref", ""))
        assert "published_sha" in ref, (
            f"the caller passes ref={ref!r}. It must be the publish job's "
            "`published_sha` output; anything else points at a commit that "
            "predates the post being deployed."
        )

    def test_caller_runs_only_after_a_real_publish(self):
        job = self._caller_job()
        cond = str(job.get("if", ""))
        assert "published_to_main" in cond, (
            f"the deploy job's condition is {cond!r}. Without the "
            "published_to_main gate it would redeploy on runs that published "
            "nothing, including dry runs."
        )
        assert job.get("needs") == "auto-publish" or "auto-publish" in (
            job.get("needs") or []
        ), "the deploy job does not depend on auto-publish"

    def test_caller_grants_the_permissions_the_callee_needs(self):
        """ai-blogwatcher.yml is `permissions: {}` deny-by-default at the top.

        A called workflow cannot hold more than its caller grants, so an
        under-granted job fails at deploy time — after the digest is already
        live, which is the worst place to find out.
        """
        perms = self._caller_job().get("permissions") or {}
        for scope, level in (
            ("pages", "write"),
            ("id-token", "write"),
            ("contents", "read"),
        ):
            assert perms.get(scope) == level, (
                f"the deploy job grants {scope}={perms.get(scope)!r}, needs {level!r}. "
                "GitHub Pages deployment requires pages:write + id-token:write."
            )

    def test_both_paths_coexist(self):
        """Neither path may quietly replace the other.

        They failed together once because there was only one. The cron covers
        what the publish job cannot see; the call covers the ~10-hour scheduler
        outages the cron cannot survive.
        """
        body = _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))
        assert re.search(r"^\s*schedule:\s*$", body, re.MULTILINE), "cron backstop gone"
        assert re.search(r"^\s*workflow_call:\s*$", body, re.MULTILINE), (
            "event-driven path gone"
        )
