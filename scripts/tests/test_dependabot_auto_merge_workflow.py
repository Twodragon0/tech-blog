#!/usr/bin/env python3
"""CI config regression guards for .github/workflows/dependabot-auto-merge.yml.

Concrete incident this protects against
----------------------------------------
The workflow once carried an ``Approve PR`` step running
``gh pr review --approve``. Because the repo setting "Allow GitHub Actions to
create and approve pull requests" is disabled by design, that step failed on
EVERY Dependabot PR with::

    failed to create review: GraphQL: GitHub Actions is not permitted to
    approve pull requests. (addPullRequestReview)

which blocked the entire auto-merge workflow (PRs #369/#368/#393/#370). The
step was removed; ``gh pr merge --auto`` does not need it. These guards make a
silent re-introduction of the self-approve anti-pattern — or an accidental
removal of the real auto-merge mechanism — fail loudly and reviewably.

Second incident (2026-09-14 batch)
----------------------------------
7 of 8 dependabot auto-merge runs failed with ``timed out after 1500s``. Two
causes, both invisible to the guards above:

1. The waiter's budget sat *inside* the observed spread of the slowest check.
   Vercel preview wall time, from the ``Vercel`` commit statuses: #726 427s,
   #696 725s, #699 1130s, #701 1540s, #727 1779s. #701 passed by ~8s; #727
   missed by 279s. The file said in prose that the step budget expires before
   ``timeout-minutes`` — nothing checked the two numbers against each other.
2. Dependabot's rebase left two runs alive on one PR. The older one polls by PR
   URL (current head) and therefore sees the *newer* run's ``auto-merge`` check,
   which ``--exclude-run-id`` does not drop. Exactly the 2 runs that were the
   older half of a force-pushed pair reported ``2 check(s) still running:
   auto-merge, Vercel``. A ``concurrency`` block keyed to the PR number cancels
   the superseded run.

Invariant directions
---------------------
* self-approve step : MUST be ABSENT  (presence => regression)
* ``gh pr merge --auto`` : MUST be PRESENT (absence => merge mechanism lost)
* fetch-metadata pin comment : the pinned SHA must be labelled with the tag it
  actually resolves to (consistency; stale labels break supply-chain audits)
* ``concurrency`` with ``cancel-in-progress`` keyed to the PR : MUST be PRESENT
* waiter budget < job ``timeout-minutes`` : the waiter must lose the race, so a
  slow check fails the step (skipping merge) rather than killing the job
* waiter budget : MUST clear the observed slowest check with headroom

Comments are stripped before scanning for the self-approve / auto-merge tokens,
because the workflow header legitimately *mentions* ``gh pr review --approve``
when explaining why it is not used. A naive substring scan would self-trip.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET = REPO_ROOT / ".github" / "workflows" / "dependabot-auto-merge.yml"

# fetch-metadata pin currently in use and the tag it resolves to. If you repin
# fetch-metadata, update BOTH and confirm the SHA resolves to the new tag via
#   gh api repos/dependabot/fetch-metadata/tags
_FETCH_METADATA_SHA = "25dd0e34f4fe68f24cc83900b1fe3fe149efef98"
_FETCH_METADATA_TAG = "v3.1.0"

# Slowest check wall time observed on a dependabot PR, in seconds: the Vercel
# preview deploy for #727 on 2026-09-14 (statuses 00:09:35 -> 00:39:14). The
# waiter's budget must clear this, otherwise a green PR fails the gate on
# queueing latency alone. Raise this ONLY with a fresh measurement:
#   gh api repos/<owner>/<repo>/commits/<sha>/statuses \
#     -q '.[] | select(.context=="Vercel") | [.state,.created_at] | @tsv'
_SLOWEST_OBSERVED_CHECK_SECONDS = 1779


def _strip_yaml_comments(text: str) -> str:
    """Remove YAML comments line-by-line.

    A ``#`` starts a comment when it is the first non-space character or is
    preceded by whitespace. ``run:`` shell lines in this workflow contain no
    ``#`` inside quotes, so this conservative rule is sufficient and avoids
    matching commentary that merely references a banned token.
    """
    out: list[str] = []
    for line in text.splitlines():
        cut = None
        for i, ch in enumerate(line):
            if ch == "#" and (i == 0 or line[i - 1] in " \t"):
                cut = i
                break
        out.append(line if cut is None else line[:cut])
    return "\n".join(out)


@pytest.fixture(scope="module")
def raw() -> str:
    # No existence skip here: `test_target_exists` is the canary for a
    # moved/renamed workflow, and a skip would additionally silence the ~15
    # tests below on the exact event this guard exists to catch. A missing
    # file raises FileNotFoundError, which errors the tests instead.
    return TARGET.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def code(raw: str) -> str:
    """Workflow text with YAML comments stripped (real steps only)."""
    return _strip_yaml_comments(raw)


def test_target_exists() -> None:
    """Canary: a moved/renamed workflow should fail clearly, not vacuously."""
    assert TARGET.is_file(), f"{TARGET} not found — update this guard if moved."


def test_no_self_approve_step(code: str) -> None:
    """`gh pr review --approve` must NOT be re-introduced (presence=regression).

    The self-approve step fails on every run ("GitHub Actions is not permitted
    to approve pull requests") and is a circular control with no independent
    review value. If you intentionally re-enable PR approval, do it via the
    repo setting + a non-GITHUB_TOKEN identity, and update this guard with the
    rationale.
    """
    assert "gh pr review --approve" not in code, (
        "Self-approve step re-introduced in dependabot-auto-merge.yml. This "
        "fails on every run because 'Allow GitHub Actions to approve PRs' is "
        "disabled by design. Remove it; 'gh pr merge --auto' does not need it."
    )


def test_auto_merge_mechanism_present(code: str) -> None:
    """The actual merge mechanism must remain (absence=broken automation)."""
    assert "gh pr merge --auto" in code, (
        "'gh pr merge --auto' is gone from dependabot-auto-merge.yml — the "
        "workflow no longer auto-merges anything. Restore the auto-merge step."
    )


def _waiter_budget_seconds(code: str) -> int:
    m = re.search(r"--timeout-seconds\s+(\d+)", code)
    assert m, (
        "No `--timeout-seconds N` on the wait_for_pr_checks.py invocation in "
        "dependabot-auto-merge.yml. Without an explicit budget the step "
        "inherits the helper default and this guard cannot check the ordering."
    )
    return int(m.group(1))


def _job_timeout_seconds(code: str) -> int:
    m = re.search(r"timeout-minutes:\s*(\d+)", code)
    assert m, "No `timeout-minutes:` on the auto-merge job."
    return int(m.group(1)) * 60


def test_concurrency_cancels_superseded_run(code: str) -> None:
    """A rebase must cancel the older run, not leave it waiting on the newer one.

    Dependabot force-pushes on rebase, which starts a second `pull_request` run
    while the first is still waiting. The waiter polls by PR URL — always the
    PR's *current* head — so the older run sees the newer run's `auto-merge`
    check. `--exclude-run-id` drops only the waiter's own run id, so the sibling
    is not excluded and the old run blocks until its deadline. Measured
    2026-09-15: both of the 2026-09-14 runs that were the older half of a
    force-pushed pair failed with `2 check(s) still running: auto-merge, Vercel`.
    """
    m = re.search(r"^concurrency:\s*$", code, re.MULTILINE)
    assert m, (
        "No top-level `concurrency:` block in dependabot-auto-merge.yml. "
        "Without it a dependabot rebase leaves two runs alive on one PR and "
        "the older one waits on the newer one's own auto-merge check until it "
        "times out."
    )
    block = code[m.end() :]
    assert "cancel-in-progress: true" in block.split("\njobs:")[0], (
        "`concurrency` present but not `cancel-in-progress: true` — the "
        "superseded run is queued rather than cancelled, which reproduces the "
        "deadlock instead of preventing it."
    )
    group = re.search(r"group:\s*(.+)", block.split("\njobs:")[0])
    assert group and "pull_request.number" in group.group(1), (
        "`concurrency.group` must be keyed to the PR number "
        "(github.event.pull_request.number); a coarser key would serialise "
        "unrelated dependabot PRs, and a per-SHA key would not match the "
        "pre- and post-rebase runs that need collapsing. Found: "
        f"{group.group(1) if group else '(no group:)'}"
    )


def test_waiter_budget_expires_before_job_timeout(code: str) -> None:
    """The waiter must lose the race against `timeout-minutes`.

    The distinction is not cosmetic. If the waiter expires first it exits
    non-zero, the merge step is skipped by `if:` and the PR stays open — the
    fail-safe the gate exists for. If the JOB times out first the run is
    cancelled, which is a coarser signal and leaves the failure mode the
    workflow header claims is impossible. The header asserted this ordering in
    prose from the day it was written and nothing compared the two numbers.
    """
    budget = _waiter_budget_seconds(code)
    job = _job_timeout_seconds(code)
    assert budget < job, (
        f"wait_for_pr_checks --timeout-seconds ({budget}s) must be strictly "
        f"less than the job's timeout-minutes ({job}s) so the step, not the "
        "job, is what expires. Raise timeout-minutes."
    )
    # The step also spends `sleep 30` plus checkout + fetch-metadata before the
    # waiter starts, so equality-adjacent values still let the job win.
    assert job - budget >= 120, (
        f"Only {job - budget}s of slack between the waiter budget ({budget}s) "
        f"and the job timeout ({job}s). The step burns a 30s sleep plus "
        "checkout and fetch-metadata first, so the job can still win the race. "
        "Keep at least 120s."
    )


def test_waiter_budget_clears_slowest_observed_check(code: str) -> None:
    """The budget must clear the slowest real check, with headroom.

    Measured 2026-09-15 across dependabot PRs, Vercel preview wall time: 427s,
    725s, 1130s, 1540s, 1779s. The budget was 1500s — inside that spread. The
    consequence was not a red CI signal but a *false* one: 7 of 8 runs on
    2026-09-14 failed on queueing latency while every substantive check was
    green, and the PRs sat open behind a red `auto-merge`.
    """
    budget = _waiter_budget_seconds(code)
    assert budget > _SLOWEST_OBSERVED_CHECK_SECONDS, (
        f"Waiter budget {budget}s does not clear the slowest observed check "
        f"({_SLOWEST_OBSERVED_CHECK_SECONDS}s). A green PR would fail this "
        "gate on latency alone."
    )
    headroom = budget - _SLOWEST_OBSERVED_CHECK_SECONDS
    assert headroom >= _SLOWEST_OBSERVED_CHECK_SECONDS * 0.25, (
        f"Only {headroom}s of headroom over the slowest observed check "
        f"({_SLOWEST_OBSERVED_CHECK_SECONDS}s). Vercel previews queue, so the "
        "observed max is a sample and not a ceiling — #701 passed by 8s under "
        "the old budget and that was not a safe margin. Keep >=25%."
    )


def test_fetch_metadata_pin_comment_accurate(raw: str) -> None:
    """The fetch-metadata SHA pin must be labelled with the tag it resolves to.

    Stale version comments (the pin said `# v2.4.0` while the SHA was v3.1.0)
    undermine supply-chain audits. If you repin, update _FETCH_METADATA_SHA /
    _FETCH_METADATA_TAG above after confirming the resolution via the API.
    """
    pin_lines = [
        ln
        for ln in raw.splitlines()
        if "dependabot/fetch-metadata@" in ln and "uses:" in ln
    ]
    assert pin_lines, "fetch-metadata `uses:` pin line not found."
    line = pin_lines[0]
    if _FETCH_METADATA_SHA in line:
        assert _FETCH_METADATA_TAG in line, (
            f"fetch-metadata pinned to {_FETCH_METADATA_SHA[:12]} but comment "
            f"does not say {_FETCH_METADATA_TAG}. The SHA resolves to "
            f"{_FETCH_METADATA_TAG}; fix the comment (or update this guard if "
            f"you repinned)."
        )
        # The previously-wrong label must not linger.
        assert "v2.4.0" not in line, (
            "Stale '# v2.4.0' comment on the fetch-metadata pin — the SHA is "
            f"{_FETCH_METADATA_TAG}."
        )
