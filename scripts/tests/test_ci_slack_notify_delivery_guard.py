#!/usr/bin/env python3
"""CI regression guard: a Slack delivery failure must reach the exit code.

This repo has shipped "the notification reports a constant, not the result"
three times:

- ``run-blog-autonomous-cron.sh`` put a fixed ``Zero-Regression Gate: 100%
  Passed`` in the webhook body, so a failing gate still announced success.
- ``monitoring.yml``'s Slack step hung off ``SLACK_WEBHOOK``, a secret that was
  never registered, so it never fired for a real outage (fixed in #583).
- ``monthly-quality-report.yml`` combined ``if: always()`` with a hardcoded
  ``--status "SUCCESS"``, announcing a published issue even when ``gh issue
  create`` failed or was skipped (fixed in #599).

``slack-post-notify.yml`` was the fourth, in a subtler shape: the status was
correctly derived, but both **delivery**-failure branches printed
``::warning::`` and fell through to exit 0. ``channel_not_found``,
``not_in_channel``, ``invalid_auth``, a revoked scope and HTTP 429 all produced
a green job with nothing delivered.

That was survivable while the workflow only ran on human pushes — someone had
just merged and was watching the run. It stopped being survivable when
ai-blogwatcher.yml began calling it (#616): that path fires at 00:00 UTC, nobody
reads cron logs, and a silent delivery failure looks exactly like the bug #616
fixed. An alert is only worth anything at the moment it fails.

Direction: the failure branches must stay hard. Softening one back to a warning,
adding ``continue-on-error``, or introducing ``always()`` trips this.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "slack-post-notify.yml"
CALLER = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"

POST_STEP = "Post to Slack via Bot API"

# (branch marker, what makes it a failure) — both must end in a hard exit.
FAILURE_BRANCHES = (
    ("ok=false", 'reported ok=false'),
    ("non-2xx", 'Slack HTTP error'),
)


def _doc(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _step(name: str) -> dict:
    for s in _doc(WORKFLOW)["jobs"]["notify"]["steps"]:
        if s.get("name") == name:
            return s
    pytest.fail(f"no step named {name!r} in slack-post-notify.yml")


def _uncommented(shell: str) -> str:
    """Comment-only lines removed.

    The step explains the anti-pattern it avoids and names ``::warning::`` in
    prose. Matching raw text would hit the explanation and stay green after the
    real ``exit 1`` was deleted.
    """
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


def test_workflow_exists():
    assert WORKFLOW.is_file(), f"{WORKFLOW} not found"


def _block_after(lines: list[str], at: int) -> list[str]:
    """Lines belonging to the same shell block as ``lines[at]``.

    Scoped by indentation: scanning stops at the first line indented LESS than
    the anchor, which is the `fi`/`else` that closes the branch.

    An earlier version of this guard used a flat ``lines[at+1:at+6]`` window.
    That window ran past the closing `fi` and the `else`, and found the OTHER
    branch's ``exit 1`` — so deleting the ok=false branch's exit left the guard
    green. The mutation was verified to have landed before this was diagnosed;
    the window, not the mutation, was the defect.
    """
    indent = len(lines[at]) - len(lines[at].lstrip())
    out = []
    for ln in lines[at + 1 :]:
        if not ln.strip():
            continue
        if len(ln) - len(ln.lstrip()) < indent:
            break
        out.append(ln.strip())
    return out


@pytest.mark.parametrize(("label", "marker"), FAILURE_BRANCHES)
def test_delivery_failure_exits_nonzero(label: str, marker: str):
    body = _uncommented(_step(POST_STEP)["run"])
    lines = body.splitlines()
    at = next((i for i, ln in enumerate(lines) if marker in ln), None)
    assert at is not None, (
        f"the {label} failure branch is gone (looked for {marker!r}); re-read the "
        "step before trusting this guard"
    )
    assert "::error::" in lines[at], (
        f"the {label} branch no longer raises ::error:: — it reads {lines[at]!r}"
    )
    block = _block_after(lines, at)
    assert "exit 1" in block, (
        f"the {label} branch does not `exit 1` before its block closes (saw "
        f"{block}). Without it the job stays green and a digest publishes with no "
        "announcement — indistinguishable from the pre-#616 bug."
    )


def test_step_never_softens_a_failure():
    """No ``::warning::`` anywhere in this step, at all.

    Asserted over the whole step body rather than per-branch on purpose. The
    per-branch version keyed on the branch's own message text, so a mutation
    that REPLACED that text with a `::warning::` removed the very string the
    loop searched for and the test passed having examined nothing. An assertion
    must not depend on a string its target mutation can delete.

    There is no legitimate warning in this step: every path here is either a
    successful delivery or something a human needs to act on.
    """
    body = _uncommented(_step(POST_STEP)["run"])
    assert "::warning::" not in body, (
        "a failure path in the Slack post step was softened to ::warning::. A "
        "warning leaves the job green, and nobody reads a green cron run — which "
        "is how this exact step announced nothing for four straight digests."
    )


def test_error_paths_and_exits_stay_balanced():
    """Canary: 4 error paths, 4 exits — two secret checks, two delivery branches.

    Coarse on purpose. If the step is restructured, this fails and forces a
    re-read rather than letting the per-branch assertions drift into vacuity.
    """
    body = _uncommented(_step(POST_STEP)["run"])
    errors = body.count("::error::")
    exits = sum(1 for ln in body.splitlines() if ln.strip() == "exit 1")
    assert errors == exits == 4, (
        f"expected 4 ::error:: paths each ending in `exit 1`, found "
        f"{errors} errors / {exits} exits. If the step was intentionally "
        "restructured, re-derive the per-branch assertions above and update this "
        "count in the same change."
    )


def test_missing_secret_still_fails_closed():
    body = _uncommented(_step(POST_STEP)["run"])
    for secret in ("SLACK_BOT_TOKEN", "SLACK_CHANNEL_ID"):
        # the emptiness test, then an exit within the same block
        at = next(
            (
                i
                for i, ln in enumerate(body.splitlines())
                if f'-z "${{{secret}:-}}"' in ln
            ),
            None,
        )
        assert at is not None, f"the {secret} presence check is gone"
        window = [ln.strip() for ln in body.splitlines()[at : at + 4]]
        assert any(ln == "exit 1" for ln in window), (
            f"{secret} absence no longer fails the step. It IS registered in this "
            "repo, so absence means removal, rotation or lost access — the one "
            "regression worth knowing about."
        )


def test_no_always_on_the_notification_path():
    """`always()` without derived status is how #599 announced a non-event."""
    text = WORKFLOW.read_text(encoding="utf-8")
    body = "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith("#")
    )
    assert "always()" not in body, (
        "always() appeared in slack-post-notify.yml. It defeats the default "
        "skip-on-failure, so without a derived status it guarantees a false "
        "report — monthly-quality-report.yml's exact defect."
    )


def test_nothing_on_the_path_is_continue_on_error():
    doc = _doc(WORKFLOW)
    job = doc["jobs"]["notify"]
    assert not job.get("continue-on-error"), "continue-on-error on the notify job"
    for step in job["steps"]:
        assert not step.get("continue-on-error"), (
            f"continue-on-error on step {step.get('name')!r} defeats the exit code "
            "this guard exists to protect"
        )


def test_message_is_derived_not_literal():
    """Step 1 of the checklist: the announcement must be a function of the post."""
    step = _step(POST_STEP)
    message = str((step.get("env") or {}).get("MESSAGE", ""))
    assert "steps.posts.outputs.message" in message, (
        f"MESSAGE is {message!r}, not derived from the detection step. A literal "
        "announcement is the run-blog-autonomous-cron.sh defect."
    )
    builder = _uncommented(_step("Detect new posts and build message")["run"])
    assert "build_slack_post_message.py" in builder, (
        "the message is no longer built from the post file"
    )


def test_caller_still_gates_on_a_real_publish():
    """A red notify job must not be reachable for an unpublished digest."""
    job = _doc(CALLER)["jobs"]["notify-slack"]
    assert "published_to_main == 'true'" in job.get("if", ""), (
        "ai-blogwatcher.yml's notify-slack lost its published_to_main gate. Now "
        "that delivery failure is a hard error, an ungated call would turn the "
        "quarantined repository_dispatch path red as well as announcing it."
    )
