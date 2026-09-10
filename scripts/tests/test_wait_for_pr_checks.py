#!/usr/bin/env python3
"""Tests for scripts/wait_for_pr_checks.py.

The helper replaces ``gh pr checks --watch --fail-fast`` in the Dependabot
auto-merge workflow. ``--watch`` waits on *every* check attached to the PR head
SHA -- including the check run of the job doing the waiting -- so the waiter
waited on itself and always died at the job timeout. These tests pin the two
properties that fix must keep:

1. the waiter never counts its own workflow run as pending (no self-deadlock);
2. it stays fail-closed -- red checks, cancelled checks, an elapsed deadline,
   and "no checks reported at all" must each exit non-zero.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "scripts" / "wait_for_pr_checks.py"

_spec = importlib.util.spec_from_file_location("wait_for_pr_checks", MODULE_PATH)
assert _spec and _spec.loader
wfpc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wfpc)


def check(name, bucket, run_id=None):
    """Build one `gh pr checks --json name,bucket,state,link` record."""
    link = (
        f"https://github.com/o/r/actions/runs/{run_id}/job/999"
        if run_id is not None
        else "https://vercel.com/github"
    )
    return {"name": name, "bucket": bucket, "state": bucket.upper(), "link": link}


class TestPartition:
    def test_own_run_is_excluded_even_while_pending(self):
        """The self-deadlock case: our own job is pending and must not count."""
        checks = [check("build", "pass", 111), check("auto-merge", "pending", 222)]
        pending, failed = wfpc.partition(checks, exclude_run_id="222")
        assert pending == [] and failed == []

    def test_own_run_excluded_even_when_failed(self):
        """Our own job's red state must not make the gate fail against itself."""
        checks = [check("build", "pass", 111), check("auto-merge", "fail", 222)]
        pending, failed = wfpc.partition(checks, exclude_run_id="222")
        assert pending == [] and failed == []

    def test_other_runs_still_counted(self):
        checks = [check("build", "pending", 111), check("auto-merge", "pending", 222)]
        pending, failed = wfpc.partition(checks, exclude_run_id="222")
        assert [c["name"] for c in pending] == ["build"]

    def test_run_id_matched_on_boundary_not_substring(self):
        """`/runs/222/` must not swallow run 2223 -- that would hide a real check."""
        checks = [check("other", "pending", 2223)]
        pending, _ = wfpc.partition(checks, exclude_run_id="222")
        assert [c["name"] for c in pending] == ["other"]

    def test_no_exclude_id_keeps_everything(self):
        checks = [check("build", "pending", 111)]
        pending, _ = wfpc.partition(checks, exclude_run_id=None)
        assert len(pending) == 1

    @pytest.mark.parametrize("bucket", ["fail", "cancel"])
    def test_failing_buckets_are_failures(self, bucket):
        """`cancel` counts as failure: a cancelled check is not a green check."""
        pending, failed = wfpc.partition([check("x", bucket, 1)], exclude_run_id=None)
        assert [c["name"] for c in failed] == ["x"] and pending == []

    @pytest.mark.parametrize("bucket", ["pass", "skipping"])
    def test_passing_buckets_block_nothing(self, bucket):
        pending, failed = wfpc.partition([check("x", bucket, 1)], exclude_run_id=None)
        assert pending == [] and failed == []

    def test_unknown_bucket_is_treated_as_pending(self):
        """Fail-closed on vocabulary drift: a bucket we do not know is not a pass."""
        pending, failed = wfpc.partition([check("x", "weird", 1)], exclude_run_id=None)
        assert [c["name"] for c in pending] == ["x"] and failed == []

    def test_status_without_link_is_kept(self):
        """Commit statuses (Vercel, GitGuardian) have no run link -- keep them."""
        pending, _ = wfpc.partition([check("Vercel", "pending")], exclude_run_id="222")
        assert [c["name"] for c in pending] == ["Vercel"]


class TestWait:
    def _wait(self, responses, **kw):
        """Drive wait() off a scripted list of fetch results, without sleeping."""
        calls = {"n": 0}

        def fetch():
            i = min(calls["n"], len(responses) - 1)
            calls["n"] += 1
            return responses[i]

        kw.setdefault("exclude_run_id", "222")
        kw.setdefault("timeout_seconds", 300)
        kw.setdefault("interval", 30)
        # Deterministic clock: each sleep advances time by the poll interval.
        clock = {"t": 0.0}
        kw.setdefault("sleep", lambda s: clock.__setitem__("t", clock["t"] + s))
        kw.setdefault("now", lambda: clock["t"])
        return wfpc.wait(fetch, **kw), calls["n"]

    def test_returns_zero_when_all_green(self):
        rc, _ = self._wait([[check("build", "pass", 111)]])
        assert rc == 0

    def test_self_only_checks_do_not_hang(self):
        """Regression: only our own job present -> must not spin to the deadline."""
        rc, n = self._wait([[check("auto-merge", "pending", 222)]])
        assert rc == 0 and n == 1

    def test_polls_until_pending_clears(self):
        rc, n = self._wait(
            [
                [check("build", "pending", 111)],
                [check("build", "pending", 111)],
                [check("build", "pass", 111)],
            ]
        )
        assert rc == 0 and n == 3

    def test_fails_fast_on_red_check(self):
        rc, n = self._wait([[check("build", "fail", 111), check("x", "pending", 333)]])
        assert rc != 0 and n == 1, (
            "a red check must fail immediately, not after polling"
        )

    def test_fails_closed_on_timeout(self):
        rc, _ = self._wait([[check("build", "pending", 111)]], timeout_seconds=90)
        assert rc != 0

    def test_fails_closed_when_no_checks_ever_appear(self):
        """`gh pr checks` reporting nothing must not read as 'everything passed'."""
        rc, _ = self._wait([[]], timeout_seconds=90)
        assert rc != 0

    def test_late_appearing_checks_are_awaited(self):
        """Checks registering after the job starts must still gate the merge."""
        rc, n = self._wait(
            [[], [check("build", "pending", 111)], [check("build", "pass", 111)]]
        )
        assert rc == 0 and n == 3

    def test_fetch_error_is_retried_then_fails_closed(self):
        rc, _ = self._wait([None], timeout_seconds=90)
        assert rc != 0, "an unreadable gh response must not fall through to merge"
