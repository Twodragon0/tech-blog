"""CI regression guard: a failed newsletter send must turn buttondown-notify red.

Measured from run logs on 2026-11-21: Buttondown answered HTTP 401 on every
sampled run (2026-10-27, 2026-11-06, 2026-11-20), and every one of those runs
was green. The send step carried ``continue-on-error: true`` and wrapped each
call in ``|| echo "... (non-critical)"``, so a revoked key read as success for
weeks and no subscriber got an email.

The fix lets the exit status through: the batch script exits 1 on a rejected
key (401/403) or a refused request and only warns on 5xx/429/timeouts. Failing
here is safe because nothing waits on this workflow; the last test pins that.

Direction: reintroducing ``continue-on-error``, an ``||`` fallback on the send
command, or a workflow that depends on this one trips this guard.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
WORKFLOW = WORKFLOWS / "buttondown-notify.yml"
WORKFLOW_NAME = "Buttondown Email Notification"
SEND_STEP = "Send Buttondown Email"


def _doc(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _uncommented(shell: str) -> str:
    """Comment-only lines removed; the step's comments name the old masking."""
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


def _send_step() -> dict:
    for step in _doc(WORKFLOW)["jobs"]["notify"]["steps"]:
        if step.get("name") == SEND_STEP:
            return step
    pytest.fail(f"no step named {SEND_STEP!r} in {WORKFLOW.name}")


def test_nothing_on_the_send_path_is_continue_on_error():
    job = _doc(WORKFLOW)["jobs"]["notify"]
    assert not job.get("continue-on-error"), "continue-on-error on the notify job"
    for step in job["steps"]:
        assert not step.get("continue-on-error"), (
            f"continue-on-error on step {step.get('name')!r} turns a rejected "
            "BUTTONDOWN_API_KEY back into a green run"
        )


def test_send_commands_are_not_masked():
    body = _uncommented(_send_step()["run"])
    calls = [ln.strip() for ln in body.splitlines() if "buttondown_notify" in ln]
    assert calls, "the send step no longer runs a buttondown_notify script"
    for call in calls:
        assert "||" not in call, (
            f"{call!r} has an || fallback, which discards the exit status that "
            "reports a rejected key"
        )
    assert "non-critical" not in body


def test_both_triggers_go_through_the_guarded_batch_script():
    """Manual dispatch must get the same bulk/imported guards as a push."""
    body = _uncommented(_send_step()["run"])
    calls = [ln.strip() for ln in body.splitlines() if "python3 scripts/" in ln]
    assert calls == [
        # `--`: a post_path starting with "-" must not be read as an option.
        'python3 scripts/buttondown_notify_batch.py -- "$POST_PATH"',
        "python3 scripts/buttondown_notify_batch.py",
    ], calls


def test_missing_api_key_fails_with_an_error_annotation():
    body = _uncommented(_send_step()["run"])
    match = re.search(
        r'if \[ -z "\$BUTTONDOWN_API_KEY" \]; then\n(.*?)\n\s*fi', body, re.DOTALL
    )
    assert match, "the BUTTONDOWN_API_KEY presence check is gone"
    block = match.group(1)
    assert "::error::" in block and "exit 1" in block, block


def test_nothing_waits_on_this_workflow():
    """A red newsletter run must not hold up a deploy or any other workflow."""
    triggers = _doc(WORKFLOW).get(True) or _doc(WORKFLOW).get("on")
    assert not {"pull_request", "pull_request_target"} & set(triggers), (
        "buttondown-notify runs on PRs again; as a failing check it could block merges"
    )
    assert not any(job.get("needs") for job in _doc(WORKFLOW)["jobs"].values())
    for path in sorted(WORKFLOWS.glob("*.yml")):
        if path == WORKFLOW:
            continue
        on = _doc(path).get(True) or _doc(path).get("on") or {}
        upstream = (on.get("workflow_run") or {}) if isinstance(on, dict) else {}
        assert WORKFLOW_NAME not in (upstream.get("workflows") or []), (
            f"{path.name} now runs after {WORKFLOW_NAME}; a failed send would "
            "cascade into it"
        )
