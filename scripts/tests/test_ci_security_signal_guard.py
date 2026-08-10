#!/usr/bin/env python3
"""CI regression guard: the two gates whose only signal is a GitHub issue.

Both `security-audit.yml` and `digest-translate-backfill.yml` end in an issue rather
than a failing job. That is a defensible design — a dependency CVE should not block
an unrelated PR, and a blocked `gh pr create` should not strand translations — but it
puts the whole value of the gate in the notification path. The 2026-08-10 audit found
both notification paths broken:

security-audit
    The audit steps are `|| true`, so the job is green regardless of findings and the
    issue is the ONLY output. Issue creation was skipped whenever an open
    `security`-labelled issue mentioned "npm audit", and nothing ever closed one.
    Measured: #414 and #415 open since 2026-06-15 while `npm audit` reported 0
    high/critical, and #446 open since 2026-07-10 while `bundle audit check --update`
    reported "No vulnerabilities found". Net effect: the next real finding would have
    produced a green job and no notification. The two same-day duplicates also prove
    the `!existing` check raced.

digest-translate-backfill
    `gh pr create` is refused by this repo ("GitHub Actions is not permitted to create
    or approve pull requests"), and the step used to `exit 1`. Measured 2026-08-08..10:
    three consecutive daily failures, three stranded branches, and the same headline
    retranslated differently each day. Its first real execution was also its first
    failure — the step had been `skipped` on every prior run.

Direction: presence/absence assertions on the reconcile behaviour. Reintroducing
"create only when absent, never close", conditioning the reconcile step on findings,
or restoring the hard exit trips this guard.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SECURITY_AUDIT = REPO_ROOT / ".github" / "workflows" / "security-audit.yml"
BACKFILL = REPO_ROOT / ".github" / "workflows" / "digest-translate-backfill.yml"


def _yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _uncommented(shell: str) -> str:
    """Shell script text with comment-only lines dropped.

    The degraded-path block explains that it *used to* `exit 1`, so asserting on the
    raw text would fail on the very comment documenting the removal — and, worse,
    would keep passing later if the comment were deleted while the exit came back.
    """
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


def _step(path: Path, job: str, name_fragment: str) -> dict:
    steps = _yaml(path)["jobs"][job]["steps"]
    for step in steps:
        if name_fragment in (step.get("name") or ""):
            return step
    pytest.fail(f"no step matching {name_fragment!r} in {path.name}:{job}")


# ---------------------------------------------------------------------------
# security-audit: the issue must be reconciled, not just created-if-absent
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("job", "fragment"),
    [("npm-audit", "Reconcile npm audit issue"), ("bundle-audit", "Reconcile bundle audit issue")],
)
def test_reconcile_step_runs_regardless_of_findings(job: str, fragment: str):
    """Gating it on findings is what made "resolved" unobservable."""
    step = _step(SECURITY_AUDIT, job, fragment)
    assert "if" not in step, (
        f"{fragment} is conditioned on {step.get('if')!r}. It must run on every audit "
        "so a resolved finding closes its issue; otherwise a stale open issue keeps "
        "suppressing the next real one."
    )


@pytest.mark.parametrize(
    ("job", "fragment"),
    [("npm-audit", "Reconcile npm audit issue"), ("bundle-audit", "Reconcile bundle audit issue")],
)
def test_reconcile_closes_when_clean(job: str, fragment: str):
    script = _step(SECURITY_AUDIT, job, fragment)["with"]["script"]
    assert "state: 'closed'" in script, (
        f"{fragment} never closes an issue, so the signal cannot self-clear"
    )
    assert "state_reason: 'completed'" in script


@pytest.mark.parametrize(
    ("job", "fragment", "marker"),
    [
        ("npm-audit", "Reconcile npm audit issue", "<!-- security-audit: npm -->"),
        ("bundle-audit", "Reconcile bundle audit issue", "<!-- security-audit: bundle -->"),
    ],
)
def test_reconcile_matches_on_marker_not_only_title(job: str, fragment: str, marker: str):
    """Title matching forks the issue the moment someone retitles it."""
    script = _step(SECURITY_AUDIT, job, fragment)["with"]["script"]
    assert marker in script, f"{fragment} lost its hidden matching marker"
    assert "LEGACY" in script, (
        "the one-time legacy title fallback is gone; the pre-existing issues would be "
        "orphaned instead of adopted and closed"
    )


@pytest.mark.parametrize(
    ("job", "fragment"),
    [("npm-audit", "Reconcile npm audit issue"), ("bundle-audit", "Reconcile bundle audit issue")],
)
def test_reconcile_collapses_duplicates(job: str, fragment: str):
    """#414 and #415 were created the same day by two racing runs."""
    script = _step(SECURITY_AUDIT, job, fragment)["with"]["script"]
    assert "Duplicate of #" in script, f"{fragment} does not collapse duplicate issues"
    assert "mine.sort" in script, "expected a deterministic primary (lowest issue number)"


@pytest.mark.parametrize(
    ("job", "fragment"),
    [("npm-audit", "Reconcile npm audit issue"), ("bundle-audit", "Reconcile bundle audit issue")],
)
def test_reconcile_refuses_to_act_on_missing_evidence(job: str, fragment: str):
    """Number('') is 0 — an absent count must not auto-close a live issue."""
    script = _step(SECURITY_AUDIT, job, fragment)["with"]["script"]
    assert "leaving issue state untouched" in script, (
        f"{fragment} no longer bails out when the audit produced no verdict. An empty "
        "env value would then read as 'no findings' and close a real issue."
    )


def test_audit_jobs_can_write_issues():
    parsed = _yaml(SECURITY_AUDIT)
    perms = parsed.get("permissions") or {}
    assert perms.get("issues") == "write", (
        "the workflow needs issues: write — without it the reconcile steps fail and the "
        "gate has no output channel at all"
    )


def test_old_create_if_absent_shape_is_gone():
    body = SECURITY_AUDIT.read_text(encoding="utf-8")
    assert not re.search(r"const existing = issues\.data\.find", body), (
        "the create-only-if-absent lookup is back; it is what let a stale open issue "
        "silence every later finding"
    )


# ---------------------------------------------------------------------------
# digest-translate-backfill: a blocked PR must not strand work behind a red cron
# ---------------------------------------------------------------------------


def test_blocked_pr_creation_does_not_hard_fail():
    step = _step(BACKFILL, "translate-backfill", "Open review PR with translations")
    run = _uncommented(step["run"])
    assert "exit 1" not in run, (
        "the degraded path exits non-zero again. It produced three consecutive daily "
        "failures with three stranded branches and no one acting; the durable signal "
        "belongs in an issue, not in a red cron run."
    )
    assert "::warning::" in run, "the degraded path must still announce itself"
    assert "stranded=true" in run, "the tracking step needs an output to trigger on"


def test_stranded_branch_is_tracked_in_an_issue():
    step = _step(BACKFILL, "translate-backfill", "Track stranded translations")
    assert step.get("if") == "steps.open_pr.outputs.stranded == 'true'", (
        "the tracking step must fire exactly on the degraded path"
    )
    script = step["with"]["script"]
    assert "digest-retranslate-stranded" in script, "lost the hidden matching marker"
    assert "issues.create" in script and "issues.update" in script, (
        "expected create-or-append so repeated failures collapse into one issue "
        "instead of one issue per day"
    )


def test_backfill_job_can_write_issues():
    job = _yaml(BACKFILL)["jobs"]["translate-backfill"]
    assert job["permissions"].get("issues") == "write", (
        "issues: write is required for the fallback signal channel"
    )


def test_backfill_still_pushes_the_branch():
    """Work must survive the degraded path; only the notification changes."""
    run = _uncommented(_step(BACKFILL, "translate-backfill", "Open review PR with translations")["run"])
    assert 'git push origin "$BRANCH"' in run, (
        "the branch push is gone — the translations would be lost, not merely unmerged"
    )
