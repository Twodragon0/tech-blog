#!/usr/bin/env python3
"""CI regression guard: the cron must announce the digest it just published.

`slack-post-notify.yml` was written to announce new posts and, for the entire
life of the bot-push arrangement, announced none of them. Its only trigger was
`push: _posts/**` on main; the blogwatcher pushes with GITHUB_TOKEN, and GitHub
does not let a GITHUB_TOKEN push start further workflow runs (recursion
prevention). Measured 2026-08-26: the last four bot commits (da730a40,
98a4170d, 233943cf, a4843c8e) appear in that workflow's run history zero times
— every run on record is on a human SHA. A human merge the same day
(6e00b1be) drew eight push-triggered runs, so the trigger works; it just
cannot see the producer.

Fixed by calling it from ai-blogwatcher.yml via `workflow_call` with the exact
post path and the exact post-push SHA.

Two invariants are load-bearing and both are easy to lose in a refactor:

1. The announcement is gated on `published_to_main`. The untrusted
   `repository_dispatch` path quarantines the digest on a branch behind a
   review PR — that post is NOT live, and announcing it would link readers to a
   404 and leak an unreviewed external-payload digest into Slack.
2. The called workflow checks out `inputs.ref`. On a `workflow_call` the default
   checkout ref is the CALLER's triggering SHA, which for the nightly cron is
   main as it stood *before* the digest was pushed. Lose the ref and the job
   checks out a tree without the post — where the git-diff branch it would fall
   back to reports "no new posts" and exits 0. Green, silent, wrong.

Direction: presence + gating. Deleting the job, widening its condition, or
dropping the ref plumbing trips this.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOGWATCHER = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"
SLACK = REPO_ROOT / ".github" / "workflows" / "slack-post-notify.yml"

PUBLISH_STEP = "Commit and publish"
NOTIFY_JOB = "notify-slack"
PUBLISH_JOB = "auto-publish"


def _wf(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _triggers(doc: dict) -> dict:
    # `on:` is the YAML 1.1 boolean True once parsed, not the string "on".
    return doc.get(True, doc.get("on")) or {}


def _steps(doc: dict, job: str) -> dict[str, dict]:
    return {s["name"]: s for s in doc["jobs"][job]["steps"] if s.get("name")}


def test_both_workflows_exist():
    assert BLOGWATCHER.is_file(), f"{BLOGWATCHER} not found"
    assert SLACK.is_file(), f"{SLACK} not found"


def test_notify_job_exists_and_calls_the_slack_workflow():
    job = _wf(BLOGWATCHER)["jobs"].get(NOTIFY_JOB)
    assert job is not None, (
        f"the {NOTIFY_JOB!r} job is gone. Without it no cron digest is ever "
        "announced — slack-post-notify.yml's push trigger cannot fire for a "
        "GITHUB_TOKEN push."
    )
    assert job.get("uses") == "./.github/workflows/slack-post-notify.yml", (
        f"{NOTIFY_JOB} no longer calls slack-post-notify.yml: {job.get('uses')!r}"
    )
    assert job.get("needs") == PUBLISH_JOB, (
        f"{NOTIFY_JOB} must `needs: {PUBLISH_JOB}` so it runs after the push"
    )


def test_notify_is_gated_on_an_actual_push_to_main():
    """The untrusted dispatch path must never announce."""
    job = _wf(BLOGWATCHER)["jobs"][NOTIFY_JOB]
    condition = job.get("if", "")
    assert f"needs.{PUBLISH_JOB}.outputs.published_to_main == 'true'" in condition, (
        f"unexpected condition on {NOTIFY_JOB}: {condition!r}. It must require "
        "published_to_main, which is set only on the trusted push-to-main branch. "
        "A repository_dispatch digest lives on a quarantine branch behind a review "
        "PR — announcing it links Slack to a post that is not live."
    )


def test_notify_receives_the_exact_post_and_commit():
    job = _wf(BLOGWATCHER)["jobs"][NOTIFY_JOB]
    passed = job.get("with") or {}
    assert f"needs.{PUBLISH_JOB}.outputs.post_file" in str(
        passed.get("post_path", "")
    ), "post_path is no longer the publish job's resolved post_file"
    assert f"needs.{PUBLISH_JOB}.outputs.published_sha" in str(passed.get("ref", "")), (
        "ref is no longer the post-push SHA. Without it the called workflow "
        "checks out the caller's triggering SHA — main BEFORE the digest landed — "
        "and finds no post to announce."
    )
    assert job.get("secrets") == "inherit", (
        "secrets: inherit dropped; SLACK_BOT_TOKEN/SLACK_CHANNEL_ID will be empty "
        "and the called workflow fails closed on purpose"
    )


def test_notify_job_grants_itself_the_permission_the_callee_needs():
    """ai-blogwatcher.yml is deny-by-default; a caller cannot under-grant a callee.

    The workflow sets `permissions: {}` at the top and each job re-grants what it
    needs. A reusable workflow can never hold more than its caller, so a
    notify-slack job with no permissions block silently cuts the callee's
    `contents: read` to nothing and actions/checkout fails — after the digest is
    already live on main.
    """
    doc = _wf(BLOGWATCHER)
    assert doc.get("permissions") == {}, (
        "the workflow-level deny-by-default changed; re-derive what notify-slack "
        "actually inherits before trusting this guard"
    )
    perms = doc["jobs"][NOTIFY_JOB].get("permissions")
    assert perms and perms.get("contents") == "read", (
        f"notify-slack permissions are {perms!r}. It inherits `{{}}` from the "
        "workflow level, so it must grant contents: read or the called workflow "
        "cannot check out the repo."
    )


def test_publish_job_exports_the_outputs_the_notify_job_reads():
    outputs = _wf(BLOGWATCHER)["jobs"][PUBLISH_JOB].get("outputs") or {}
    for key in ("post_file", "published_to_main", "published_sha"):
        assert key in outputs, f"{PUBLISH_JOB} no longer exports {key!r}"
    assert "steps.publish.outputs" in outputs["published_to_main"], (
        "published_to_main must come from the publish step, not be hardcoded"
    )


def test_published_to_main_is_set_only_after_a_successful_trusted_push():
    """Not in the dispatch branch, and not before `git push` succeeds.

    The literal must sit inside the `if git push; then` success arm. Hoisting it
    to the top of the step — or into the repository_dispatch arm — would make a
    quarantined or failed publish announce itself.
    """
    run = _steps(_wf(BLOGWATCHER), PUBLISH_JOB)[PUBLISH_STEP]["run"]
    body = "\n".join(ln for ln in run.splitlines() if not ln.lstrip().startswith("#"))
    assert "published_to_main=true" in body, (
        "the publish step no longer signals published_to_main; the notify job "
        "will never fire"
    )
    quarantine_at = body.find('BRANCH="blogwatcher/digest-')
    signal_at = body.find("published_to_main=true")
    push_at = body.find("if git push; then")
    assert quarantine_at != -1 and push_at != -1, (
        "the publish step's shape changed; re-read it before trusting this guard"
    )
    assert signal_at > push_at, (
        "published_to_main is set before `git push` succeeds, so a push that "
        "fails all three attempts would still announce"
    )
    assert signal_at > quarantine_at, (
        "published_to_main is set in (or above) the repository_dispatch quarantine "
        "branch — an unreviewed external-payload digest would be announced"
    )


def test_slack_workflow_is_callable_with_a_path_and_a_ref():
    call = _triggers(_wf(SLACK)).get("workflow_call")
    assert call is not None, (
        "slack-post-notify.yml lost its workflow_call trigger; ai-blogwatcher.yml "
        "cannot call it and cron digests go unannounced again"
    )
    inputs = call.get("inputs") or {}
    for key in ("post_path", "ref"):
        assert key in inputs, f"workflow_call input {key!r} removed"


def test_slack_workflow_still_fires_on_human_pushes():
    """The call path is an addition, not a replacement."""
    push = _triggers(_wf(SLACK)).get("push") or {}
    assert "_posts/**" in (push.get("paths") or []), (
        "the push trigger was dropped; human-authored posts would stop being "
        "announced, trading one blind spot for another"
    )


def test_checkout_honours_the_caller_supplied_ref():
    checkout = next(
        s
        for s in _wf(SLACK)["jobs"]["notify"]["steps"]
        if "actions/checkout" in str(s.get("uses", ""))
    )
    assert "inputs.ref" in str((checkout.get("with") or {}).get("ref", "")), (
        "the checkout no longer honours inputs.ref. On a workflow_call the default "
        "ref is the caller's triggering SHA (main before the digest push), so the "
        "post would be absent and the job would exit 0 having announced nothing."
    )


def test_missing_post_path_is_an_error_not_a_silent_diff_fallback():
    """A bad path must fail loudly, not announce whatever git-diff finds."""
    step = next(
        s for s in _wf(SLACK)["jobs"]["notify"]["steps"] if s.get("id") == "posts"
    )
    body = "\n".join(
        ln for ln in step["run"].splitlines() if not ln.lstrip().startswith("#")
    )
    assert 'if [ ! -f "$POST_PATH" ]' in body and "::error::" in body, (
        "the caller-supplied path is no longer validated. If it is wrong, the "
        "git-diff branch would run instead and announce an unrelated post."
    )
    assert "POST_PATH" in str(step.get("env") or {}), (
        "post_path must reach the shell through env, not inlined via ${{ }} — "
        "same injection rule buttondown-notify.yml adopted (B-H1, 2026-06-30)"
    )
