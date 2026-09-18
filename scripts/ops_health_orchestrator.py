#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@dataclass
class CommandResult:
    ok: bool
    output: str
    return_code: int


@dataclass
class CheckResult:
    name: str
    agent: str
    ok: bool
    priority: str
    summary: str
    recommendation: str


def run_command(command: list[str], timeout: int = 180) -> CommandResult:
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    combined = (completed.stdout + completed.stderr).strip()
    return CommandResult(
        ok=completed.returncode == 0,
        output=combined,
        return_code=completed.returncode,
    )


def summarize_output(output: str, max_lines: int = 6) -> str:
    lines = [line for line in output.splitlines() if line.strip()]
    if not lines:
        return "no output"
    if len(lines) <= max_lines:
        return "\n".join(lines)
    return "\n".join(lines[:max_lines]) + "\n..."


def check_lint_and_types() -> CheckResult:
    if shutil.which("ruff") is None:
        return CheckResult(
            name="lint-and-types",
            agent="OpsAgent",
            ok=False,
            priority="P1",
            summary="ruff is not installed",
            recommendation="Install ruff and rerun lint checks.",
        )

    # Verify only. Until 2026-08-28 this ran `ruff check --fix` and `ruff format`
    # (both mutating) BEFORE the verification pass, so every auto-fixable rule —
    # which is most of them, including the whole `I` isort family — was repaired
    # in the ephemeral runner and then verified as clean. `ok` could not become
    # False for anything ruff knows how to fix, and nothing here commits, so the
    # repair was discarded and main quietly accumulated violations: 9 of them by
    # the time this was measured, one landed by PR #629 an hour earlier.
    #
    # A check that fixes the thing it is about to look at reports on the fix, not
    # on the repository.
    lint_verify = run_command(["ruff", "check", "scripts/"])
    # Gating as of 2026-08-28. It was advisory for exactly one reason — 25 files
    # under scripts/ were already drifted and failing on that backlog would have
    # made the ops loop permanently red, which is how an alert gets muted. The
    # 25 were reformatted in the commit that promoted this, so the reason is
    # gone. mypy below stays advisory because its 94 legacy errors have NOT been
    # cleared; the two are not the same situation and should not share a verdict.
    format_check = run_command(["ruff", "format", "--check", "scripts/"])

    if shutil.which("mypy") is None:
        mypy_result = CommandResult(
            ok=False, output="mypy is not installed", return_code=1
        )
    else:
        mypy_result = run_command(
            ["mypy", "scripts/", "--ignore-missing-imports"], timeout=300
        )

    # mypy is advisory only (94 legacy errors need gradual fixing)
    ok = lint_verify.ok and format_check.ok
    details = [
        f"ruff check: {'OK' if lint_verify.ok else 'FAIL'}",
        f"ruff format --check: {'OK' if format_check.ok else 'FAIL'}",
        f"mypy: {'OK' if mypy_result.ok else 'WARN (advisory)'}",
        "lint output:",
        summarize_output(lint_verify.output),
        "format output:",
        summarize_output(format_check.output),
        "mypy output:",
        summarize_output(mypy_result.output),
    ]

    return CheckResult(
        name="lint-and-types",
        agent="OpsAgent",
        ok=ok,
        priority="P2" if ok else "P1",
        summary="\n".join(details),
        recommendation=(
            "No action needed."
            if ok
            else "Resolve remaining Ruff/Mypy errors before deploy."
        ),
    )


def check_vercel() -> CheckResult:
    if shutil.which("vercel") is None:
        return CheckResult(
            name="vercel-health",
            agent="OpsAgent",
            ok=False,
            priority="P1",
            summary="vercel CLI is not installed",
            recommendation="Install Vercel CLI with npm i -g vercel.",
        )

    token = os.getenv("VERCEL_TOKEN", "")
    if not token:
        return CheckResult(
            name="vercel-health",
            agent="OpsAgent",
            ok=True,
            priority="P2",
            summary="Skipped (VERCEL_TOKEN not set)",
            recommendation="Set VERCEL_TOKEN in CI secrets to enable Vercel monitoring.",
        )

    auth = run_command(["vercel", "whoami", "--token", token])
    if not auth.ok:
        return CheckResult(
            name="vercel-health",
            agent="OpsAgent",
            ok=False,
            priority="P1",
            summary=f"Authentication failed\n{summarize_output(auth.output)}",
            recommendation="Refresh VERCEL_TOKEN and verify project scope.",
        )

    monitor = run_command(["bash", "scripts/monitor_vercel_builds.sh", "--alert-only"])
    ok = monitor.ok
    return CheckResult(
        name="vercel-health",
        agent="OpsAgent",
        ok=ok,
        priority="P2" if ok else "P1",
        summary=summarize_output(monitor.output),
        recommendation=(
            "No action needed."
            if ok
            else "Inspect failing deployment and rerun build/deploy pipeline."
        ),
    )


# Workflows that may invoke this orchestrator with --auto-recover-gha, and so
# must never be auto-rerun BY it. Rerunning one re-runs auto-recover inside it:
# an autonomous rerun chain holding actions:write with no human gate.
# (Security fix A-H3, 2026-06-30 workflow audit.)
#
# This was a literal set of four names — "Ops Multi Agent Loop", "Ops Priority
# Loop", "Ultrawork Loop", "AI Ops On Demand" — and on 2026-09-18 NONE of the
# four matched a live workflow. The four had been consolidated into one file
# whose `name:` is "Ops Orchestrator", and the set was never updated, so the
# control had been inert since that consolidation. Nothing went wrong only
# because Ops Orchestrator did not fail in the last 50 runs; the 21 stale ops
# issues from 2026-03/04/06 show it does fail. A gate keyed to an exact string
# is blind to the variant, and a renamed workflow is the variant.
#
# Two layers now, so a rename cannot silently disarm it again:
#   1. GITHUB_WORKFLOW — set by Actions to the RUNNING workflow's name. Always
#      correct, needs no maintenance, and covers the self-rerun case exactly.
#   2. SELF_RERUN_WORKFLOWS — declared siblings, for the case where a future
#      second loop workflow can also pass --auto-recover-gha. Every entry is
#      asserted against the live `.github/workflows/*.yml` `name:` fields by
#      test_ops_health_orchestrator.py, so a rename fails CI instead of
#      quietly removing the protection.
SELF_RERUN_WORKFLOWS = frozenset({"Ops Orchestrator"})


def self_rerun_excluded() -> frozenset[str]:
    """Workflow names this orchestrator must not auto-rerun."""
    running = os.getenv("GITHUB_WORKFLOW", "").strip()
    return SELF_RERUN_WORKFLOWS | ({running} if running else frozenset())


def check_github_actions(auto_recover: bool, rerun_limit: int) -> CheckResult:
    if shutil.which("gh") is None:
        return CheckResult(
            name="github-actions-health",
            agent="OpsAgent",
            ok=False,
            priority="P1",
            summary="gh CLI is not installed",
            recommendation="Install GitHub CLI and rerun checks.",
        )

    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        return CheckResult(
            name="github-actions-health",
            agent="OpsAgent",
            ok=False,
            priority="P1",
            summary="GITHUB_TOKEN/GH_TOKEN is missing",
            recommendation="Set GITHUB_TOKEN in CI secrets.",
        )

    env = os.environ.copy()
    env["GH_TOKEN"] = token
    query = [
        "gh",
        "run",
        "list",
        "--limit",
        "15",
        "--branch",
        "main",
        "--json",
        "databaseId,name,status,conclusion,url",
    ]
    response = subprocess.run(
        query,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if response.returncode != 0:
        return CheckResult(
            name="github-actions-health",
            agent="OpsAgent",
            ok=False,
            priority="P1",
            summary=summarize_output(response.stderr or response.stdout),
            recommendation="Verify repository permissions for GITHUB_TOKEN.",
        )

    try:
        runs: list[dict[str, Any]] = json.loads(response.stdout)
    except json.JSONDecodeError:
        return CheckResult(
            name="github-actions-health",
            agent="OpsAgent",
            ok=False,
            priority="P1",
            summary="Failed to parse gh run list output",
            recommendation="Check gh CLI version and token scope.",
        )

    failed_runs = [
        run
        for run in runs
        if run.get("status") == "completed"
        and run.get("conclusion") not in {"success", "neutral", "skipped", "cancelled"}
        and run.get("name") not in self_rerun_excluded()
    ]

    rerun_attempts: list[str] = []
    if auto_recover and failed_runs:
        for run in failed_runs[:rerun_limit]:
            run_id = str(run.get("databaseId", ""))
            if not run_id:
                continue
            rerun = subprocess.run(
                ["gh", "run", "rerun", run_id],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env=env,
            )
            status = "OK" if rerun.returncode == 0 else "FAIL"
            rerun_attempts.append(f"rerun {run_id}: {status}")

    ok = len(failed_runs) == 0
    summary_lines = [
        f"recent failed runs: {len(failed_runs)}",
    ]
    for run in failed_runs[:5]:
        summary_lines.append(
            f"- {run.get('name', 'unknown')} ({run.get('conclusion')}) {run.get('url', '')}"
        )
    if rerun_attempts:
        summary_lines.extend(rerun_attempts)

    return CheckResult(
        name="github-actions-health",
        agent="OpsAgent",
        ok=ok,
        priority="P2" if ok else "P1",
        summary="\n".join(summary_lines),
        recommendation=(
            "No action needed."
            if ok
            else "Review failed workflows and confirm rerun results."
        ),
    )


def check_sentry(unresolved_threshold: int) -> CheckResult:
    token = os.getenv("SENTRY_AUTH_TOKEN", "")
    org = os.getenv("SENTRY_ORG", "")
    project = os.getenv("SENTRY_PROJECT", "")
    if not token or not org or not project:
        return CheckResult(
            name="sentry-health",
            agent="SecurityAgent",
            ok=True,
            priority="P2",
            summary="Skipped (SENTRY_AUTH_TOKEN/SENTRY_ORG/SENTRY_PROJECT not fully set)",
            recommendation="Set Sentry secrets to enable automatic monitoring.",
        )

    params = urllib.parse.urlencode({"project": project, "status": "unresolved"})
    url = f"https://sentry.io/api/0/organizations/{org}/issues/?{params}"
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as error:
        return CheckResult(
            name="sentry-health",
            agent="SecurityAgent",
            ok=False,
            priority="P1",
            summary=f"Sentry API request failed: {error}",
            recommendation="Verify Sentry token scope and organization/project values.",
        )

    unresolved = len(payload)
    ok = unresolved <= unresolved_threshold
    top_issue = payload[0].get("title", "n/a") if payload else "n/a"
    summary = f"unresolved issues: {unresolved}\ntop issue: {top_issue}"
    return CheckResult(
        name="sentry-health",
        agent="SecurityAgent",
        ok=ok,
        priority="P2" if ok else "P1",
        summary=summary,
        recommendation=(
            "No action needed."
            if ok
            else "Triage unresolved Sentry issues and close repeating noisy errors."
        ),
    )


# check_uiux() / PAGESPEED_API_KEY was removed 2026-09-18.
#
# It called PageSpeed Insights and failed P1 when
# `perf_score >= 0.75 and lcp_ms <= 2500 and cls <= 0.1` did not hold. Every
# part of that was already settled elsewhere in this repo, the wrong way round:
#
#   * `perf_score >= 0.75` — lighthouse.yml deliberately dropped `performance`
#     as a gate after measuring 0.55-0.86 on UNCHANGED content over 60 runs:
#     "Gating on it produced random red."
#   * `lcp_ms <= 2500` — LCP is bimodal here, 4218-4373ms (55 runs) and
#     6921-9695ms (5 runs). BOTH modes exceed 2500, so this term was close to
#     constant-false.
#   * `cls <= 0.1` — lighthouse.yml already budgets CLS at a stricter 0.05.
#
# The capability is not lost: lighthouse-ci.yml compares head-vs-base LCP over
# 5 runs on PRs, and lighthouse.yml gates CLS on push and PR. Both are live.
#
# The secret was never provisioned, so this check only ever returned
# "Skipped (PAGESPEED_API_KEY not set)". Provisioning it would have pointed a
# noisy P1 source at the 6-hourly cron — and P1 is what opens an ops issue.
#
# What would bring it back: a PSI-side measurement showing the numbers are
# stable on Google's infrastructure (the 60 runs above are GitHub-runner
# Lighthouse/Lantern and do not transfer directly), plus thresholds derived
# from that distribution rather than round numbers.


def derive_global_priority(results: list[CheckResult]) -> str:
    failures = [result for result in results if not result.ok]
    if any(result.priority == "P0" for result in failures):
        return "P0"
    if any(result.priority == "P1" for result in failures):
        return "P1"
    return "P2"


def format_roundtable(results: list[CheckResult]) -> str:
    priority = derive_global_priority(results)
    by_agent: dict[str, list[CheckResult]] = {}
    for result in results:
        by_agent.setdefault(result.agent, []).append(result)

    lines: list[str] = [
        f"Ops Roundtable Priority: {priority}",
        "",
        "[OpsAgent]",
    ]
    for result in by_agent.get("OpsAgent", []):
        status = "OK" if result.ok else "FAIL"
        lines.append(f"- {result.name}: {status} ({result.priority})")
        lines.append(f"  {result.summary}")

    lines.extend(["", "[SecurityAgent]"])
    for result in by_agent.get("SecurityAgent", []):
        status = "OK" if result.ok else "FAIL"
        lines.append(f"- {result.name}: {status} ({result.priority})")
        lines.append(f"  {result.summary}")

    lines.extend(["", "[Moderator]", "Recommended next actions:"])
    failed = [result for result in results if not result.ok]
    if not failed:
        lines.append("- All checks passed. Keep current automation cadence.")
    else:
        ordered = sorted(failed, key=lambda item: item.priority)
        for result in ordered:
            lines.append(f"- {result.name}: {result.recommendation}")

    return "\n".join(lines).strip() + "\n"


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run lint/ops/security roundtable checks"
    )
    parser.add_argument("--auto-recover-gha", action="store_true")
    parser.add_argument("--gha-rerun-limit", type=int, default=2)
    parser.add_argument("--sentry-unresolved-threshold", type=int, default=0)
    parser.add_argument("--skip-lint", action="store_true")
    parser.add_argument("--skip-vercel", action="store_true")
    parser.add_argument("--skip-github-actions", action="store_true")
    parser.add_argument("--skip-sentry", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--json-output", type=Path)
    return parser.parse_args()


def env_enabled(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def main() -> int:
    args = parse_args()
    run_lint = env_enabled("RUN_LINT_CHECKS", True) and not args.skip_lint
    run_vercel = env_enabled("RUN_VERCEL_CHECKS", True) and not args.skip_vercel
    run_gha = (
        env_enabled("RUN_GITHUB_ACTIONS_CHECKS", True) and not args.skip_github_actions
    )
    run_sentry = env_enabled("RUN_SENTRY_CHECKS", True) and not args.skip_sentry

    results: list[CheckResult] = []
    if run_lint:
        results.append(check_lint_and_types())
    if run_vercel:
        results.append(check_vercel())
    if run_gha:
        results.append(
            check_github_actions(
                auto_recover=args.auto_recover_gha,
                rerun_limit=max(1, args.gha_rerun_limit),
            )
        )
    if run_sentry:
        results.append(
            check_sentry(unresolved_threshold=max(0, args.sentry_unresolved_threshold))
        )

    if not results:
        print("Ops Roundtable Priority: P2\n\n[Moderator]\n- No checks enabled.\n")
        return 0

    report = format_roundtable(results)
    print(report)

    if args.output:
        write_report(args.output, report)

    if args.json_output:
        payload = {
            "priority": derive_global_priority(results),
            "results": [result.__dict__ for result in results],
        }
        write_report(
            args.json_output, json.dumps(payload, indent=2, ensure_ascii=False)
        )

    # Only lint-and-types is blocking; external service checks are advisory
    blocking = [r for r in results if r.name == "lint-and-types"]
    if any(r.priority == "P0" and not r.ok for r in blocking):
        return 2
    if any(not r.ok for r in blocking):
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as error:
        command = " ".join(shlex.quote(part) for part in error.cmd)
        print(f"Command timed out: {command}", file=sys.stderr)
        raise
