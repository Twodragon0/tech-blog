#!/usr/bin/env python3
"""CI regression guard: dependabot auto-merge must stay gated on green CI.

Why this guard exists
---------------------
main has NO required status checks configured (verified 2026-06-30), so
``gh pr merge --auto`` in ``.github/workflows/dependabot-auto-merge.yml`` would
merge a patch/minor dependency PR the instant it is mergeable -- even with red
CI. The fix is the ``Wait for CI checks to pass`` step that blocks on the
waiter BEFORE the merge step: a failing check fails that step, which skips
the merge step (fail-closed). That protection
disappears *silently* if someone:

* deletes the wait step, or
* stops invoking the blocking waiter (so it no longer blocks on red checks), or
* moves the wait step to run AFTER the merge step (no longer a gate), or
* neutralises it with ``continue-on-error`` / ``|| true``.

This guard makes any such weakening fail loudly and reviewably.

2026-09-10 -- the waiter changed shape, and the guard changed with it. The step
used to run ``gh pr checks --watch --fail-fast``, which deadlocked: ``--watch``
waits on every check attached to the PR head SHA, and the ``auto-merge`` job is
itself one of those checks, so it waited on itself until ``timeout-minutes: 30``
cancelled it. Measured on PRs #696-#701: all real checks green (slowest ``build``
5m39s) yet ``auto-merge`` ran 30m16s and was cancelled -- so the merge step never
ran and six dependency PRs, security patches among them, stayed open. The gate
is now ``scripts/wait_for_pr_checks.py``, which polls the same data with this
run's own check runs excluded. The guard therefore asserts on the *new* waiter
AND bans the old deadlocking invocation from coming back.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control). Direction: presence /
ordering assertions -- any removal/reorder trips. If the gate moves to a real
branch-protection required check instead, update this guard in the same PR and
say why (the workflow gate then becomes belt-and-suspenders, not load-bearing).
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "dependabot-auto-merge.yml"
WAITER_REL = "scripts/wait_for_pr_checks.py"
WAITER = REPO_ROOT / WAITER_REL

_WAIT_NAME_RE = re.compile(r"\s*-\s+name:\s*Wait for CI checks\b")
_MERGE_NAME_RE = re.compile(r"\s*-\s+name:\s*Enable auto-merge\b")


def _step_line_index(text: str, name_re: "re.Pattern[str]"):
    """Index of the line whose ``- name:`` matches ``name_re``, else ``None``."""
    for i, ln in enumerate(text.splitlines()):
        if name_re.match(ln):
            return i
    return None


def _step_block(text: str, name_re: "re.Pattern[str]") -> str:
    """Return the YAML lines of the step whose ``- name:`` matches ``name_re``.

    Spans from that ``- name:`` line to the next sibling ``- name:`` step at the
    same indent (or EOF). Returns ``""`` when the step is absent.
    """
    lines = text.splitlines()
    start = _step_line_index(text, name_re)
    if start is None:
        return ""
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        ln = lines[end]
        if re.match(r"\s*-\s+name:", ln) and (len(ln) - len(ln.lstrip())) == indent:
            break
        end += 1
    return "\n".join(lines[start:end])


def _command_text(block: str) -> str:
    """The step block with comment-only lines removed.

    The wait step's surrounding comments legitimately mention ``gh pr checks
    --watch`` while explaining why it was removed; asserting on the executable
    command (not comments) keeps the guard honest in both directions -- a stale
    comment must neither keep it green after the real gate is deleted, nor trip
    the "old invocation is back" assertion below. (Skill rule: never match
    commentary.)
    """
    return "\n".join(ln for ln in block.splitlines() if not ln.lstrip().startswith("#"))


class TestDependabotGateGuard:
    @classmethod
    def setup_class(cls):
        cls.text = WORKFLOW.read_text(encoding="utf-8") if WORKFLOW.is_file() else ""

    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_wait_step_present(self):
        assert _step_block(self.text, _WAIT_NAME_RE), (
            "The 'Wait for CI checks' step disappeared from dependabot-auto-merge.yml. "
            "That step is the fail-closed gate that stops a red dependency PR from "
            "auto-merging (main has no required status checks). If intentional, "
            "update this guard."
        )

    def test_gate_runs_blocking_waiter(self):
        cmd = _command_text(_step_block(self.text, _WAIT_NAME_RE))
        assert WAITER_REL in cmd, (
            f"the gate no longer invokes {WAITER_REL}; without a blocking waiter a "
            "still-pending or red dependency PR falls straight through to auto-merge."
        )
        assert "--pr" in cmd, (
            "the waiter is invoked without --pr, so it cannot gate anything"
        )

    def test_waiter_script_exists(self):
        assert WAITER.is_file(), (
            f"{WAITER_REL} is referenced by the workflow but missing from the repo; "
            "the gate step would fail open only in the sense of erroring every run."
        )

    def test_old_self_deadlocking_invocation_not_reintroduced(self):
        """`gh pr checks --watch` waits on this job's own check run -- never again.

        Reverting to it does not look like a regression (the step still 'waits for
        CI') but it can never succeed: the job times out and every Dependabot PR
        silently stops merging.
        """
        cmd = _command_text(_step_block(self.text, _WAIT_NAME_RE))
        assert not ("gh pr checks" in cmd and "--watch" in cmd), (
            "'gh pr checks --watch' is back in the wait step. It waits on the "
            "auto-merge job's own check run and can only end at the job timeout "
            f"(observed 30m16s, PRs #696-#701). Use {WAITER_REL}, which excludes "
            "$GITHUB_RUN_ID's own checks."
        )

    def test_wait_precedes_merge(self):
        wait_i = _step_line_index(self.text, _WAIT_NAME_RE)
        merge_i = _step_line_index(self.text, _MERGE_NAME_RE)
        assert wait_i is not None and merge_i is not None, (
            "could not locate both the wait step and the auto-merge step"
        )
        assert wait_i < merge_i, (
            "the 'Wait for CI checks' step no longer precedes 'Enable auto-merge'; "
            "a gate that runs after the merge does not block anything. Keep the "
            "wait step first."
        )

    def test_gate_not_neutralized(self):
        block = _step_block(self.text, _WAIT_NAME_RE)
        cmd = _command_text(block)
        assert "continue-on-error: true" not in block, (
            "the wait step is marked continue-on-error; its failure would no longer "
            "skip the merge step, reopening the red-merge hole."
        )
        assert "|| true" not in cmd, (
            "the wait gate is neutralised with '|| true'; a red check would be "
            "swallowed and the PR would still auto-merge."
        )
