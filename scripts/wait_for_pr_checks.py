#!/usr/bin/env python3
"""Block until a PR's CI checks finish, ignoring the caller's own check run.

Why this exists
---------------
``gh pr checks --watch --fail-fast`` waits on *every* check attached to the PR
head SHA. When the waiter is itself a job in a ``pull_request`` workflow, its own
check run is in that set -- so it waits on itself and can never finish.

That is exactly what happened to ``.github/workflows/dependabot-auto-merge.yml``.
Measured 2026-09-10 on PRs #696-#701: every real check was green (slowest was
``build`` at 5m39s) yet the ``auto-merge`` job ran the full ``timeout-minutes:
30`` and was cancelled, which skipped the merge step. Six dependency PRs -- including
security patches -- sat open behind a red ``auto-merge`` check, each burning 30
minutes of runner time.

This helper polls the same ``gh pr checks`` data but drops any check whose link
points at the current workflow run, so the waiter never blocks on itself. It
keeps the fail-closed contract the original gate existed for: a red check, a
cancelled check, an unreadable response, or an elapsed deadline all exit
non-zero, which skips the merge step. Only an affirmative "every other check
reached a passing state" exits 0.

Usage:
    python3 scripts/wait_for_pr_checks.py --pr "$PR_URL" [--timeout-seconds 1500]

``--exclude-run-id`` defaults to ``$GITHUB_RUN_ID`` so callers inside Actions need
not pass it.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

# `gh pr checks --json bucket` normalises every check-run conclusion and commit
# status into one of these buckets.
PASSING_BUCKETS = frozenset({"pass", "skipping"})
# `cancel` is deliberately a failure: a cancelled check never proved anything, and
# the safe direction for a merge gate is to refuse.
FAILING_BUCKETS = frozenset({"fail", "cancel"})


def _belongs_to_run(link: str, run_id: str | None) -> bool:
    """True when ``link`` is a check run of workflow run ``run_id``.

    Matches on ``/runs/<id>/`` rather than a bare substring so run 222 does not
    also swallow run 2223 -- silently dropping somebody else's check would turn
    this gate into a rubber stamp.
    """
    if not run_id:
        return False
    return f"/runs/{run_id}/" in (link or "")


def partition(
    checks: list[dict], exclude_run_id: str | None
) -> tuple[list[dict], list[dict]]:
    """Split ``checks`` into (still-running, failed), dropping our own run's checks.

    Buckets we do not recognise count as still-running, not as passes: if gh's
    vocabulary grows, the gate should stall (and eventually time out) rather than
    wave an unknown state through.
    """
    pending: list[dict] = []
    failed: list[dict] = []
    for c in checks:
        if _belongs_to_run(c.get("link", ""), exclude_run_id):
            continue
        bucket = (c.get("bucket") or "").lower()
        if bucket in PASSING_BUCKETS:
            continue
        if bucket in FAILING_BUCKETS:
            failed.append(c)
        else:
            pending.append(c)
    return pending, failed


def _names(checks: list[dict]) -> str:
    return ", ".join(c.get("name", "?") for c in checks)


def wait(
    fetch,
    *,
    exclude_run_id: str | None,
    timeout_seconds: int,
    interval: int,
    sleep=time.sleep,
    now=time.monotonic,
) -> int:
    """Poll ``fetch`` until every foreign check is terminal. Returns an exit code."""
    deadline = now() + timeout_seconds
    reason = "no checks reported for this PR"
    while True:
        checks = fetch()
        if checks is None:
            reason = "could not read check status from gh"
        elif not checks:
            reason = "no checks reported for this PR yet"
        else:
            pending, failed = partition(checks, exclude_run_id)
            if failed:
                print(f"FAIL: {len(failed)} check(s) are not green: {_names(failed)}")
                return 1
            if not pending:
                print("OK: all checks on this PR reached a passing state.")
                return 0
            reason = f"{len(pending)} check(s) still running: {_names(pending)}"

        if now() >= deadline:
            print(f"FAIL: timed out after {timeout_seconds}s -- {reason}")
            return 1
        print(f"waiting ({reason})")
        sleep(interval)


def _gh_fetch(pr: str):
    """Return the PR's checks as a list, or None when gh's output is unusable.

    ``gh pr checks --json`` exits 0 regardless of check state (verified with gh
    2.100.0), so the exit code carries no signal -- the JSON body is the answer.
    """
    proc = subprocess.run(
        ["gh", "pr", "checks", pr, "--json", "name,bucket,state,link"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, list) else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pr", required=True, help="PR URL or number")
    ap.add_argument(
        "--exclude-run-id",
        default=os.environ.get("GITHUB_RUN_ID"),
        help="workflow run whose own checks to ignore (default: $GITHUB_RUN_ID)",
    )
    ap.add_argument("--timeout-seconds", type=int, default=1500)
    ap.add_argument("--interval", type=int, default=30)
    args = ap.parse_args(argv)

    if not args.exclude_run_id:
        print(
            "warning: no --exclude-run-id / $GITHUB_RUN_ID; may wait on own check run"
        )

    return wait(
        lambda: _gh_fetch(args.pr),
        exclude_run_id=args.exclude_run_id,
        timeout_seconds=args.timeout_seconds,
        interval=args.interval,
    )


if __name__ == "__main__":
    sys.exit(main())
