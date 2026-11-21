"""CI regression guard: a failed newsletter send must turn buttondown-notify red.

Measured from run logs on 2026-11-21: Buttondown answered HTTP 401 on every
sampled run (2026-10-27, 2026-11-06, 2026-11-20), and every one of those runs
was green. The send step carried ``continue-on-error: true`` and wrapped each
call in ``|| echo "... (non-critical)"``, so a revoked key read as success for
weeks and no subscriber got an email.

The fix lets the exit status through: the batch script exits 1 whenever a post
was not confirmed sent, whether the key was rejected (401/403), the request was
refused, or Buttondown failed temporarily (429, 5xx, timeout). Failing here is
safe because nothing waits on this workflow; a test below pins that.

Direction: reintroducing ``continue-on-error``, an ``||`` fallback on the send
command, or a workflow that depends on this one trips this guard.

Two ways a post's email went missing without any failure are pinned here too:
a later push cancelling the run that was mailing it (concurrency), and a push
of several commits being diffed as HEAD~1..HEAD, which only sees the last
commit's posts. The tests run the workflow's own "Check for new posts" script
against throwaway git repositories.
"""

from __future__ import annotations

import base64
import json
import os
import re
import subprocess
from pathlib import Path

import buttondown_notify_batch as batch
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
WORKFLOW = WORKFLOWS / "buttondown-notify.yml"
WORKFLOW_NAME = "Buttondown Email Notification"
SEND_STEP = "Send Buttondown Email"
CHECK_STEP = "Check for new posts"
ZERO_SHA = "0" * 40


def _doc(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _uncommented(shell: str) -> str:
    """Comment-only lines removed; the step's comments name the old masking."""
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


def _step(name: str) -> dict:
    for step in _doc(WORKFLOW)["jobs"]["notify"]["steps"]:
        if step.get("name") == name:
            return step
    pytest.fail(f"no step named {name!r} in {WORKFLOW.name}")


def test_nothing_on_the_send_path_is_continue_on_error():
    job = _doc(WORKFLOW)["jobs"]["notify"]
    assert not job.get("continue-on-error"), "continue-on-error on the notify job"
    for step in job["steps"]:
        assert not step.get("continue-on-error"), (
            f"continue-on-error on step {step.get('name')!r} turns a rejected "
            "BUTTONDOWN_API_KEY back into a green run"
        )


def test_send_commands_are_not_masked():
    body = _uncommented(_step(SEND_STEP)["run"])
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
    body = _uncommented(_step(SEND_STEP)["run"])
    calls = [ln.strip() for ln in body.splitlines() if "python3 scripts/" in ln]
    assert calls == [
        # `--`: a post_path starting with "-" must not be read as an option.
        'python3 scripts/buttondown_notify_batch.py -- "$POST_PATH"',
        "python3 scripts/buttondown_notify_batch.py",
    ], calls


def test_missing_api_key_fails_with_an_error_annotation():
    body = _uncommented(_step(SEND_STEP)["run"])
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


# ---------------------------------------------------------------------------
# No run is cancelled, and every post of a push is found
# ---------------------------------------------------------------------------


def test_a_later_push_never_cancels_or_replaces_a_pending_send():
    """One concurrency group per commit (and per dispatched post), never cancelled.

    A group per branch with cancel-in-progress cancelled the run that was
    mailing the first of two quick pushes, and that post's email was lost.
    Turning cancel-in-progress off is not enough on its own: GitHub keeps one
    pending run per group, so a third push would replace the second.
    """
    concurrency = _doc(WORKFLOW)["concurrency"]
    assert concurrency["cancel-in-progress"] is False
    group = concurrency["group"]
    assert "github.sha" in group and "inputs.post_path" in group, group
    assert "github.ref" not in group, group
    assert "concurrency" not in _doc(WORKFLOW)["jobs"]["notify"]


def test_the_checkout_has_the_commit_before_the_push():
    """github.event.before can be many commits back; a depth-2 clone lacks it."""
    checkout = next(
        step
        for step in _doc(WORKFLOW)["jobs"]["notify"]["steps"]
        if str(step.get("uses", "")).startswith("actions/checkout@")
    )
    assert checkout["with"]["fetch-depth"] == 0


def test_the_send_step_mails_the_list_the_check_step_found():
    """Diffing a second time in the send step could disagree with the check."""
    env = _step(SEND_STEP)["env"]
    assert env["POSTS_JSON"] == "${{ steps.check_posts.outputs.posts_json }}"
    assert _step(CHECK_STEP)["id"] == "check_posts"


def _git(repo: Path, *args: str) -> str:
    # The developer's global config stays out (it can change diff output);
    # identity and signing are set per command, so nothing is written to it.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=fixture",
            "-c",
            "user.email=fixture@invalid.local",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            *args,
        ],
        cwd=repo,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def _commit(repo: Path, *names: str) -> str:
    """Write each file (new or edited), commit, and return the commit SHA."""
    for name in names:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        old = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(old + "line\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", "fixture")
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    path = tmp_path / "repo"
    path.mkdir()
    _git(path, "init", "-q")
    _commit(path, "_posts/2026-11-01-Old_Post.md", "README.md")
    return path


def _check_step(
    repo: Path, event: str, before: str
) -> subprocess.CompletedProcess[str]:
    """Run the workflow's check script as Actions runs a ``shell: bash`` step."""
    step = _step(CHECK_STEP)
    assert step["shell"] == "bash", "without -o pipefail a failed git diff is lost"
    assert step["env"] == {
        "EVENT_NAME": "${{ github.event_name }}",
        "BEFORE": "${{ github.event.before }}",
    }
    script = repo.parent / "check_step.sh"
    script.write_text(step["run"], encoding="utf-8")
    output = repo.parent / "github_output"
    output.write_text("", encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        EVENT_NAME=event,
        BEFORE=before,
        GITHUB_OUTPUT=str(output),
    )
    return subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", str(script)],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )


def _new_posts(repo: Path, event: str, before: str) -> list[str]:
    """What the send step would mail, decoded by the batch script itself."""
    run = _check_step(repo, event, before)
    assert run.returncode == 0, run.stdout + run.stderr
    outputs = dict(
        line.split("=", 1)
        for line in (repo.parent / "github_output").read_text().splitlines()
    )
    posts = batch.decode_posts_json(outputs["posts_json"])
    assert outputs["post_count"] == str(len(posts))
    assert outputs["has_new_posts"] == ("true" if posts else "false")
    return posts


def test_a_push_of_several_commits_mails_the_posts_of_all_of_them(repo: Path):
    before = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "_posts/2026-11-19-First.md")
    _commit(repo, "_posts/2026-11-20-Second.md")
    _commit(repo, "_posts/2026-11-01-Old_Post.md", "notes.txt")  # an edit only
    assert _new_posts(repo, "push", before) == [
        "_posts/2026-11-19-First.md",
        "_posts/2026-11-20-Second.md",
    ]


@pytest.mark.parametrize(
    "case", ["new branch", "unknown commit", "force push", "manual run"]
)
def test_without_a_usable_before_only_the_last_commit_counts(repo: Path, case: str):
    _git(repo, "checkout", "-q", "-b", "rewritten")
    rewritten = _commit(repo, "elsewhere.txt")  # not in HEAD's history below
    _git(repo, "checkout", "-q", "-")
    before = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "_posts/2026-11-19-First.md")
    _commit(repo, "_posts/2026-11-20-Second.md")
    event, before = {
        "new branch": ("push", ZERO_SHA),
        "unknown commit": ("push", "1" * 40),
        "force push": ("push", rewritten),
        "manual run": ("workflow_dispatch", before),
    }[case]
    assert _new_posts(repo, event, before) == ["_posts/2026-11-20-Second.md"]


def test_edited_and_renamed_posts_are_not_new(repo: Path):
    _commit(repo, "_posts/2026-11-02-To_Rename.md")
    before = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "_posts/2026-11-01-Old_Post.md")  # an edit
    _git(repo, "mv", "_posts/2026-11-02-To_Rename.md", "_posts/2026-11-02-Renamed.md")
    _git(repo, "commit", "-q", "-m", "rename")
    assert _new_posts(repo, "push", before) == []


def test_non_ascii_post_names_come_through_verbatim(repo: Path):
    """Without -z, git prints such a name quoted and octal-escaped."""
    before = _git(repo, "rev-parse", "HEAD")
    _commit(repo, "_posts/2026-11-19-보안_점검.md")
    assert _new_posts(repo, "push", before) == ["_posts/2026-11-19-보안_점검.md"]


def test_a_failing_git_diff_fails_the_step(repo: Path):
    """It used to read as "no new posts", and the run went green."""
    run = _check_step(repo, "push", ZERO_SHA)  # HEAD~1 of a root commit
    assert run.returncode != 0, run.stdout
