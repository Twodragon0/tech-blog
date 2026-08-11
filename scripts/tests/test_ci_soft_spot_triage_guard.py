#!/usr/bin/env python3
"""CI regression guard: which soft spots are legitimate, and which must stay hard.

The 2026-08-10/11 gate audit ended with 12 flagged soft spots in two reporting
workflows. Reviewing them one at a time (2026-08-11) split them three ways, and the
split is the thing worth pinning — a future sweep that "aligns" all of them in either
direction makes the repo worse.

LEGITIMATE — `|| true` is correct here, do not remove:
  monthly-quality-report.yml
    * `grep -c` x2 — exits 1 when the count is 0, which is a valid count, not an error.
      A `|| echo 0` chain instead writes two lines and breaks $GITHUB_OUTPUT parsing.
    * `gh issue list` — an empty list is the normal case.
    * `gh issue close` — an already-closed or missing issue is not a failure.
    * `gh label create` x2 — idempotent create; it fails precisely when the label
      already exists, which is the steady state.

WAS WRONG, NOW HARD:
  monthly-quality-report.yml
    * `gh issue create` — this issue IS the workflow's deliverable. Actions can create
      issues in this repo (the security-audit reconcile step does it), so a failure is a
      real anomaly. With `|| true` the monthly report silently never existed while the
      job reported success.

WAS WRONG, NOW OBSERVABLE (still non-blocking by design):
  monthly-quality-report.yml
    * The two corpus scans wrote `image_issues` / `post_issues` to $GITHUB_OUTPUT from
      steps with NO `id:`, and nothing referenced them anyway. Two full-corpus scans ran
      monthly and their results were discarded — `generate_quality_report.py` builds the
      report from post SCORES and trend coverage, so image verification and check_posts
      warnings were genuinely missing rather than duplicated. Now they have ids, feed
      the issue body, and a scan that CRASHES reports "unknown" instead of "0" — because
      "0 issues" from a crashed scan is a lie, not a clean result.
  sentry-release.yml
    * Two step-level `continue-on-error: true` on top of a job that already carries it.
      The job-level one is a documented free-tier decision and stays; the step-level
      duplicates only rendered the steps green. Removing them lets a failed step show
      red inside a still-passing job, which is the difference between "Sentry release
      tracking stopped" being visible and invisible.

Direction: this asserts the CLASSIFICATION. Removing a legitimate `|| true`, restoring a
removed one, or re-adding step-level continue-on-error all trip it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
MONTHLY = WORKFLOWS / "monthly-quality-report.yml"
SENTRY = WORKFLOWS / "sentry-release.yml"


def _code(path: Path) -> str:
    """Workflow text minus comment-only lines.

    Both files now explain, in prose, which `|| true` calls they keep and why. Matching
    raw text would hit that explanation instead of the code it describes.
    """
    return "\n".join(
        ln for ln in path.read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("#")
    )


def _soft_lines(path: Path) -> list[str]:
    return [ln.strip() for ln in _code(path).splitlines() if "|| true" in ln]


# ---------------------------------------------------------------------------
# monthly-quality-report: the legitimate set
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "fragment",
    [
        "grep -c '❌",
        "grep -c '⚠️",
        "gh issue list",
        "gh issue close",
        'gh label create "quality-report"',
        'gh label create "automated"',
    ],
)
def test_legitimate_soft_calls_stay_soft(fragment: str):
    """These six fail in their normal, expected state. Hardening them breaks the job."""
    matching = [ln for ln in _soft_lines(MONTHLY) if fragment in ln]
    assert matching, (
        f"the `|| true` on {fragment!r} is gone. It fails in its steady state "
        "(zero grep matches / empty issue list / already-closed issue / existing label), "
        "so removing it turns a normal condition into a failed monthly report. See this "
        "file's docstring before changing it."
    )


def test_only_the_reviewed_soft_calls_remain():
    """A NEW `|| true` should be justified, not inherited by proximity."""
    lines = _soft_lines(MONTHLY)
    allowed = ("grep -c", "gh issue list", "gh issue close", "gh label create")
    unreviewed = [ln for ln in lines if not any(a in ln for a in allowed)]
    assert not unreviewed, (
        f"unreviewed `|| true` in monthly-quality-report.yml: {unreviewed}. Each soft "
        "call in this file was classified individually on 2026-08-11 — add the new one "
        "to the docstring with its reason, or make it hard."
    )


# ---------------------------------------------------------------------------
# monthly-quality-report: what must stay hard
# ---------------------------------------------------------------------------


def test_issue_creation_is_hard():
    """The issue IS the deliverable; a swallowed failure means no report at all."""
    code = _code(MONTHLY)
    match = re.search(r"gh issue create[^\n]*(?:\n[^\n]*)*?--label \"quality-report,automated\"[^\n]*", code)
    assert match, "the gh issue create call is gone from monthly-quality-report.yml"
    assert "|| true" not in match.group(0), (
        "gh issue create is soft again. Actions can create issues in this repo, so a "
        "failure is a real anomaly — and swallowing it means the monthly report silently "
        "never existed while the job reported success."
    )


def test_scan_steps_have_ids_and_are_consumed():
    """Outputs from a step with no `id:` are unreferenceable — that was the bug."""
    import yaml

    job = yaml.safe_load(MONTHLY.read_text(encoding="utf-8"))["jobs"]["quality-report"]
    steps = {s.get("name"): s for s in job["steps"] if s.get("name")}
    for name, expected_id in (("Verify images", "images"), ("Check posts", "posts")):
        assert steps[name].get("id") == expected_id, (
            f"step {name!r} lost its `id: {expected_id}`. It writes to $GITHUB_OUTPUT, "
            "and without an id nothing can read the value — two full-corpus scans ran "
            "monthly and threw their results away."
        )

    code = _code(MONTHLY)
    assert "steps.images.outputs.image_issues" in code, "image_issues is not consumed anywhere"
    assert "steps.posts.outputs.post_issues" in code, "post_issues is not consumed anywhere"


def test_crashed_scan_is_not_reported_as_zero():
    """"0 issues" from a scan that died is a lie, not a clean result."""
    code = _code(MONTHLY)
    assert code.count("PIPESTATUS[0]") >= 2, (
        "the scan exit status is no longer captured; a crashed scan would report 0 issues"
    )
    assert code.count("unknown (scan exited") >= 2, (
        "the crashed-scan branch no longer distinguishes 'unknown' from a real zero"
    )


# ---------------------------------------------------------------------------
# sentry-release: one soft layer, not three
# ---------------------------------------------------------------------------


def test_sentry_job_stays_soft():
    """Documented free-tier decision: a Sentry release failure must not break CI."""
    import yaml

    job = yaml.safe_load(SENTRY.read_text(encoding="utf-8"))["jobs"]["create-sentry-release"]
    assert job.get("continue-on-error") is True, (
        "create-sentry-release is now hard-failing. Release tracking is a nicety on the "
        "free tier; failing it would break unrelated pushes to main."
    )


def test_sentry_has_no_redundant_step_level_soft():
    """A second soft layer inside a soft job only hides which step failed."""
    import yaml

    job = yaml.safe_load(SENTRY.read_text(encoding="utf-8"))["jobs"]["create-sentry-release"]
    soft_steps = [s.get("name") for s in job["steps"] if s.get("continue-on-error")]
    assert not soft_steps, (
        f"step-level continue-on-error is back on {soft_steps}. The job is already "
        "continue-on-error, so this only renders the step green — the failure becomes "
        "invisible instead of a red step inside a passing job."
    )


def test_sentry_verify_step_still_runs_after_a_failure():
    """It is the step that reports the outcome, so it needs `if: always()`."""
    import yaml

    job = yaml.safe_load(SENTRY.read_text(encoding="utf-8"))["jobs"]["create-sentry-release"]
    verify = next(s for s in job["steps"] if s.get("name") == "Verify Release & Summary")
    assert "always()" in verify["if"], (
        "Verify Release & Summary no longer runs unconditionally. With the release step "
        "no longer soft, a failure there would skip the very step that reports it."
    )
