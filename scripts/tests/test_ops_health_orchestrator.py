#!/usr/bin/env python3
"""Behavioural tests for scripts/ops_health_orchestrator.py.

This module runs on a 6-hourly cron with `actions:write` + `issues:write`, and
until 2026-09-18 nothing imported or executed it. The one existing test
(`test_ci_python_lint_gate.py`) reads it as TEXT, to assert it does not call
`ruff --fix` — valuable, but it cannot see behaviour.

The first thing writing these tests found was that the A-H3 self-rerun control
had been inert for months (see `test_self_rerun_exclusions_match_live_workflows`).
That is the shape of defect this file exists to catch: things that still read as
enforcing.

Scope note — the checks that shell out (`check_lint_and_types`, `check_vercel`,
`check_github_actions`) are exercised through injected fakes rather than real
`ruff`/`vercel`/`gh` calls. A test that needs a live credential is a test people
learn to skip, and the ops loop's own failure modes are in the DECISION logic,
not in whether subprocess works.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import ops_health_orchestrator as ops  # noqa: E402

WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"


def _result(name="c", agent="OpsAgent", ok=True, priority="P2") -> ops.CheckResult:
    return ops.CheckResult(
        name=name,
        agent=agent,
        ok=ok,
        priority=priority,
        summary="s",
        recommendation="r",
    )


# ---------------------------------------------------------------------------
# A-H3: the autonomous rerun chain
# ---------------------------------------------------------------------------


def test_self_rerun_exclusions_match_live_workflows() -> None:
    """Every declared name must be a real workflow's `name:`.

    THE incident this file was written for. The set used to be a literal four —
    "Ops Multi Agent Loop", "Ops Priority Loop", "Ultrawork Loop", "AI Ops On
    Demand" — and on 2026-09-18 not one of them matched a live workflow. They
    had been consolidated into `ops-orchestrator.yml`, whose `name:` is "Ops
    Orchestrator", and the set was never updated.

    So the control that stops this orchestrator from rerunning a workflow that
    itself runs `--auto-recover-gha` had been disarmed, while still reading as
    a security fix. Nothing went wrong only because Ops Orchestrator had not
    failed in the last 50 runs — the 21 stale ops issues from 2026-03/04/06 are
    proof that it does.

    A name that matches nothing excludes nothing. Keep this assertion strict.
    """
    live = set()
    for path in sorted(WORKFLOW_DIR.glob("*.y*ml")):
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(spec, dict) and spec.get("name"):
            live.add(spec["name"])

    stale = sorted(ops.SELF_RERUN_WORKFLOWS - live)
    assert stale == [], (
        f"{stale} appear in SELF_RERUN_WORKFLOWS but match no workflow `name:`. "
        "They exclude nothing. If a workflow was renamed or consolidated, update "
        "the set in the same change — this is exactly how the original four went "
        "inert."
    )


def test_running_workflow_is_always_excluded(monkeypatch) -> None:
    """`GITHUB_WORKFLOW` covers the self-rerun case without maintenance."""
    monkeypatch.setenv("GITHUB_WORKFLOW", "Some Future Ops Loop")
    assert "Some Future Ops Loop" in ops.self_rerun_excluded()
    # …and the declared siblings survive alongside it.
    assert ops.SELF_RERUN_WORKFLOWS <= ops.self_rerun_excluded()


def test_exclusion_is_not_vacuous(monkeypatch) -> None:
    """An empty/blank GITHUB_WORKFLOW must not widen or empty the set."""
    monkeypatch.setenv("GITHUB_WORKFLOW", "   ")
    assert ops.self_rerun_excluded() == ops.SELF_RERUN_WORKFLOWS
    monkeypatch.delenv("GITHUB_WORKFLOW", raising=False)
    assert ops.self_rerun_excluded() == ops.SELF_RERUN_WORKFLOWS
    assert ops.SELF_RERUN_WORKFLOWS, "The set is empty — nothing is protected."


def _gha(monkeypatch, runs, rerun_calls):
    """Drive check_github_actions with a fake `gh`."""
    monkeypatch.setattr(ops.shutil, "which", lambda _: "/usr/bin/gh")
    monkeypatch.setenv("GITHUB_TOKEN", "dummy-token-not-a-real-credential")

    class Done:
        def __init__(self, rc=0, out="", err=""):
            self.returncode, self.stdout, self.stderr = rc, out, err

    def fake_run(cmd, **_kw):
        if cmd[:3] == ["gh", "run", "list"]:
            return Done(out=json.dumps(runs))
        if cmd[:3] == ["gh", "run", "rerun"]:
            rerun_calls.append(cmd[3])
            return Done()
        raise AssertionError(f"unexpected command {cmd}")

    monkeypatch.setattr(ops.subprocess, "run", fake_run)


def test_self_workflow_failure_is_never_rerun(monkeypatch) -> None:
    """The chain A-H3 forbids: a failed ops loop rerun by the next ops loop.

    Rerunning it re-runs `--auto-recover-gha` inside it, with actions:write and
    no human gate.
    """
    calls: list[str] = []
    _gha(
        monkeypatch,
        [
            {
                "databaseId": 1,
                "name": "Ops Orchestrator",
                "status": "completed",
                "conclusion": "failure",
                "url": "u",
            }
        ],
        calls,
    )
    result = ops.check_github_actions(auto_recover=True, rerun_limit=5)
    assert calls == [], f"rerun issued for a self workflow: {calls}"
    assert result.ok, "a self-workflow failure must not red the check either"


def test_other_workflow_failure_is_rerun(monkeypatch) -> None:
    """Not vacuous: the feature still works for everything else.

    Without this, 'never rerun anything' would pass the test above while
    silently removing auto-recovery.
    """
    calls: list[str] = []
    _gha(
        monkeypatch,
        [
            {
                "databaseId": 42,
                "name": "SVG Compliance Lint",
                "status": "completed",
                "conclusion": "failure",
                "url": "u",
            }
        ],
        calls,
    )
    result = ops.check_github_actions(auto_recover=True, rerun_limit=5)
    assert calls == ["42"]
    assert not result.ok and result.priority == "P1"


def test_rerun_limit_bounds_the_blast_radius(monkeypatch) -> None:
    """`rerun_limit` caps how many reruns one pass may trigger.

    This is the only bound on an `actions:write` loop acting without review.
    """
    calls: list[str] = []
    _gha(
        monkeypatch,
        [
            {
                "databaseId": i,
                "name": f"W{i}",
                "status": "completed",
                "conclusion": "failure",
                "url": "u",
            }
            for i in range(10)
        ],
        calls,
    )
    ops.check_github_actions(auto_recover=True, rerun_limit=2)
    assert len(calls) == 2, f"rerun_limit=2 issued {len(calls)} reruns: {calls}"


def test_auto_recover_off_issues_no_reruns(monkeypatch) -> None:
    calls: list[str] = []
    _gha(
        monkeypatch,
        [
            {
                "databaseId": 7,
                "name": "W",
                "status": "completed",
                "conclusion": "failure",
                "url": "u",
            }
        ],
        calls,
    )
    ops.check_github_actions(auto_recover=False, rerun_limit=5)
    assert calls == []


@pytest.mark.parametrize("conclusion", ["success", "neutral", "skipped", "cancelled"])
def test_non_failures_are_not_reruns(monkeypatch, conclusion: str) -> None:
    """`cancelled` and `skipped` are not failures.

    `skipped` matters concretely: the `priority` lane is cron-gated OFF, so it
    reports `skipped` on a schedule. Treating that as a failure would rerun a
    deliberately disabled job four times a day.
    """
    calls: list[str] = []
    _gha(
        monkeypatch,
        [
            {
                "databaseId": 1,
                "name": "W",
                "status": "completed",
                "conclusion": conclusion,
                "url": "u",
            }
        ],
        calls,
    )
    result = ops.check_github_actions(auto_recover=True, rerun_limit=5)
    assert calls == []
    assert result.ok


def test_in_progress_runs_are_not_failures(monkeypatch) -> None:
    """A run still going has no conclusion; it must not be rerun."""
    calls: list[str] = []
    _gha(
        monkeypatch,
        [
            {
                "databaseId": 1,
                "name": "W",
                "status": "in_progress",
                "conclusion": None,
                "url": "u",
            }
        ],
        calls,
    )
    assert ops.check_github_actions(auto_recover=True, rerun_limit=5).ok
    assert calls == []


# ---------------------------------------------------------------------------
# Priority derivation — decides whether an ops issue opens
# ---------------------------------------------------------------------------


def test_passing_check_does_not_raise_global_priority() -> None:
    """Only FAILED results contribute.

    Every check carries a `priority` even when it passes (`"P2" if ok else
    "P1"`), so reading priority without checking `ok` would make a healthy run
    look like P1 and open an issue on a green repo.
    """
    assert ops.derive_global_priority([_result(ok=True, priority="P1")]) == "P2"
    assert ops.derive_global_priority([_result(ok=True, priority="P0")]) == "P2"


def test_failures_escalate_in_order() -> None:
    assert ops.derive_global_priority([_result(ok=False, priority="P1")]) == "P1"
    assert (
        ops.derive_global_priority(
            [_result(ok=False, priority="P1"), _result(ok=False, priority="P0")]
        )
        == "P0"
    ), "P0 must win over P1 regardless of order"
    assert ops.derive_global_priority([]) == "P2"


# ---------------------------------------------------------------------------
# main() exit contract — what actually reds the cron
# ---------------------------------------------------------------------------


def _run_main(monkeypatch, tmp_path, *, lint, sentry=None, argv=None):
    monkeypatch.setattr(ops, "check_lint_and_types", lambda: lint)
    monkeypatch.setattr(ops, "check_vercel", lambda: _result(name="vercel-health"))
    monkeypatch.setattr(
        ops,
        "check_github_actions",
        lambda **_k: _result(name="github-actions-health"),
    )
    monkeypatch.setattr(
        ops,
        "check_sentry",
        lambda **_k: sentry or _result(name="sentry-health"),
    )
    monkeypatch.setattr(sys, "argv", ["ops_health_orchestrator.py", *(argv or [])])
    for var in (
        "RUN_LINT_CHECKS",
        "RUN_VERCEL_CHECKS",
        "RUN_GITHUB_ACTIONS_CHECKS",
        "RUN_SENTRY_CHECKS",
    ):
        monkeypatch.delenv(var, raising=False)
    return ops.main()


def test_only_lint_is_blocking(monkeypatch, tmp_path) -> None:
    """A failing external service must NOT red the run.

    Deliberate: Sentry/Vercel/PageSpeed outages are not this repo's defects, and
    a permanently red ops loop is an alert people learn to mute. The 21 stale
    ops issues are what muting looks like. If this ever flips, the cron starts
    opening issues for other people's downtime.
    """
    code = _run_main(
        monkeypatch,
        tmp_path,
        lint=_result(name="lint-and-types", ok=True),
        sentry=_result(name="sentry-health", ok=False, priority="P1"),
    )
    assert code == 0, "an advisory service failure reddened the run"


def test_lint_failure_is_blocking(monkeypatch, tmp_path) -> None:
    """Not vacuous: the one blocking check must still block.

    `check_lint_and_types` is the only thing here that measures THIS repo.
    """
    code = _run_main(
        monkeypatch,
        tmp_path,
        lint=_result(name="lint-and-types", ok=False, priority="P1"),
    )
    assert code == 1


def test_p0_lint_failure_exits_2(monkeypatch, tmp_path) -> None:
    code = _run_main(
        monkeypatch,
        tmp_path,
        lint=_result(name="lint-and-types", ok=False, priority="P0"),
    )
    assert code == 2


def test_no_checks_enabled_is_not_a_pass_in_disguise(monkeypatch, tmp_path, capsys):
    """Zero checks exits 0 — but must say so, not print an all-clear.

    A silent 0 here is indistinguishable from a healthy run.
    """
    monkeypatch.setenv("RUN_LINT_CHECKS", "false")
    monkeypatch.setenv("RUN_VERCEL_CHECKS", "false")
    monkeypatch.setenv("RUN_GITHUB_ACTIONS_CHECKS", "false")
    monkeypatch.setenv("RUN_SENTRY_CHECKS", "false")
    monkeypatch.setattr(sys, "argv", ["ops_health_orchestrator.py"])
    assert ops.main() == 0
    assert "No checks enabled" in capsys.readouterr().out


def test_report_files_are_written(monkeypatch, tmp_path) -> None:
    """`--output` / `--json-output` feed the artifact AND, since #746, the
    inlined body of the public failure issue."""
    md, js = tmp_path / "r.md", tmp_path / "r.json"
    _run_main(
        monkeypatch,
        tmp_path,
        lint=_result(name="lint-and-types", ok=True),
        argv=["--output", str(md), "--json-output", str(js)],
    )
    assert md.is_file() and js.is_file()
    payload = json.loads(js.read_text(encoding="utf-8"))
    assert payload["priority"] == "P2"
    assert {r["name"] for r in payload["results"]} == {
        "lint-and-types",
        "vercel-health",
        "github-actions-health",
        "sentry-health",
    }


# ---------------------------------------------------------------------------
# Report shaping
# ---------------------------------------------------------------------------


def test_report_bounds_each_summary() -> None:
    """`summarize_output` caps what reaches a PUBLIC issue body.

    Since #746 this text is inlined into the failure issue. The issue step has
    its own 50000-char budget, but the per-check cap is what keeps one noisy
    mypy run from crowding out the other checks.
    """
    assert ops.summarize_output("") == "no output"
    assert ops.summarize_output("a\n\n\nb") == "a\nb", "blank lines are dropped"
    long = "\n".join(str(i) for i in range(50))
    out = ops.summarize_output(long, max_lines=6)
    assert out.endswith("\n...") and len(out.splitlines()) == 7


def test_failed_checks_lead_the_recommendations() -> None:
    """A green run must not print a recommendation list, and a red one must."""
    green = ops.format_roundtable([_result(ok=True)])
    assert "All checks passed" in green
    red = ops.format_roundtable([_result(name="x", ok=False, priority="P1")])
    assert "Ops Roundtable Priority: P1" in red
    assert "- x: r" in red


def test_report_has_no_empty_agent_section_left_behind() -> None:
    """Sections are emitted per agent that the report knows about.

    `check_uiux`/`UiUxAgent` was removed on 2026-09-18 together with its
    section. If a check is deleted but its section header survives, the report
    grows a permanent empty heading that reads as "this was checked".
    """
    report = ops.format_roundtable([_result(agent="OpsAgent")])
    assert "[UiUxAgent]" not in report
    for header in ("[OpsAgent]", "[SecurityAgent]", "[Moderator]"):
        assert header in report


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("1", True),
        ("true", True),
        ("TRUE", True),
        ("  yes  ", True),
        ("on", True),
        ("0", False),
        ("false", False),
        ("", False),
        ("maybe", False),
    ],
)
def test_env_enabled_parsing(monkeypatch, raw: str, expected: bool) -> None:
    monkeypatch.setenv("OPS_TEST_FLAG", raw)
    assert ops.env_enabled("OPS_TEST_FLAG", True) is expected


def test_env_enabled_default_applies_only_when_unset(monkeypatch) -> None:
    """An explicitly empty value is a value, not "unset".

    `${{ vars.X }}` renders to an empty string when the variable does not
    exist, so a workflow can hand this function "" and mean "off". Falling back
    to the default there would silently enable a check someone turned off.
    """
    monkeypatch.delenv("OPS_TEST_FLAG", raising=False)
    assert ops.env_enabled("OPS_TEST_FLAG", True) is True
    assert ops.env_enabled("OPS_TEST_FLAG", False) is False
    monkeypatch.setenv("OPS_TEST_FLAG", "")
    assert ops.env_enabled("OPS_TEST_FLAG", True) is False


# ---------------------------------------------------------------------------
# Credential handling — the report is public
# ---------------------------------------------------------------------------


def test_missing_credentials_skip_rather_than_fail() -> None:
    """Absent optional secrets are P2 skips, not P1 failures.

    Otherwise a repo without Vercel/Sentry credentials opens an ops issue every
    6 hours forever. Measured on 2026-09-18: VERCEL_TOKEN, SENTRY_* are all
    unset in this repo's Actions secrets, so this is the live path, not an edge
    case.
    """
    import os

    for var in ("VERCEL_TOKEN", "SENTRY_AUTH_TOKEN", "SENTRY_ORG", "SENTRY_PROJECT"):
        os.environ.pop(var, None)
    sentry = ops.check_sentry(unresolved_threshold=0)
    assert sentry.ok and sentry.priority == "P2"
    assert "Skipped" in sentry.summary


def test_no_credential_value_reaches_a_summary(monkeypatch) -> None:
    """The report is inlined into a PUBLIC issue body since #746.

    Verified by hand on 2026-09-18 for all three f-string error paths; pinned
    here so it stays true. The token is passed to `gh` via env and to `vercel`
    as an argv element — neither of which `run_command` captures, since it reads
    only stdout+stderr.
    """
    secret = "ghp_NotARealTokenJustAShapeForThisTest123456"
    monkeypatch.setattr(ops.shutil, "which", lambda _: "/usr/bin/gh")
    monkeypatch.setenv("GITHUB_TOKEN", secret)

    class Done:
        returncode, stdout, stderr = 1, "", "HTTP 401: Bad credentials"

    monkeypatch.setattr(ops.subprocess, "run", lambda *_a, **_k: Done())
    result = ops.check_github_actions(auto_recover=False, rerun_limit=1)
    blob = f"{result.summary}\n{result.recommendation}"
    assert secret not in blob, "a credential value reached the report"
    assert "401" in blob, "…but the diagnostic itself must survive"
