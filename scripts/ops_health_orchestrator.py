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

    lint_fix = run_command(["ruff", "check", "scripts/", "--fix"])
    ruff_format = run_command(["ruff", "format", "scripts/"])
    lint_verify = run_command(["ruff", "check", "scripts/"])

    if shutil.which("mypy") is None:
        mypy_result = CommandResult(
            ok=False, output="mypy is not installed", return_code=1
        )
    else:
        mypy_result = run_command(
            ["mypy", "scripts/", "--ignore-missing-imports"], timeout=300
        )

    ok = lint_verify.ok and mypy_result.ok
    details = [
        f"ruff --fix: {'OK' if lint_fix.ok else 'FAIL'}",
        f"ruff format: {'OK' if ruff_format.ok else 'FAIL'}",
        f"ruff verify: {'OK' if lint_verify.ok else 'FAIL'}",
        f"mypy: {'OK' if mypy_result.ok else 'FAIL'}",
        "lint output:",
        summarize_output(lint_verify.output or lint_fix.output),
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
            ok=False,
            priority="P1",
            summary="VERCEL_TOKEN is missing",
            recommendation="Set VERCEL_TOKEN in CI secrets.",
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
        and run.get("conclusion") not in {"success", "neutral", "skipped"}
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


def check_uiux() -> CheckResult:
    api_key = os.getenv("PAGESPEED_API_KEY", "")
    target_url = os.getenv("OPS_UIUX_TARGET_URL", "https://tech.2twodragon.com")
    if not api_key:
        return CheckResult(
            name="uiux-health",
            agent="UiUxAgent",
            ok=True,
            priority="P2",
            summary="Skipped (PAGESPEED_API_KEY not set)",
            recommendation="Set PAGESPEED_API_KEY to enforce UI/UX performance gates.",
        )

    query = urllib.parse.urlencode(
        {
            "url": target_url,
            "key": api_key,
            "strategy": "mobile",
            "category": "performance",
        }
    )
    request = urllib.request.Request(
        f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?{query}"
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as error:
        return CheckResult(
            name="uiux-health",
            agent="UiUxAgent",
            ok=False,
            priority="P1",
            summary=f"PageSpeed API request failed: {error}",
            recommendation="Check API key quota and site availability.",
        )

    lighthouse = payload.get("lighthouseResult", {})
    categories = lighthouse.get("categories", {})
    audits = lighthouse.get("audits", {})

    perf_score = categories.get("performance", {}).get("score", 0.0)
    lcp_ms = audits.get("largest-contentful-paint", {}).get("numericValue", 99999)
    cls = audits.get("cumulative-layout-shift", {}).get("numericValue", 999.0)

    ok = perf_score >= 0.75 and lcp_ms <= 2500 and cls <= 0.1
    summary = (
        f"performance score: {perf_score:.2f}\nLCP(ms): {lcp_ms:.0f}\nCLS: {cls:.3f}"
    )
    return CheckResult(
        name="uiux-health",
        agent="UiUxAgent",
        ok=ok,
        priority="P2" if ok else "P1",
        summary=summary,
        recommendation=(
            "No action needed."
            if ok
            else "Improve LCP/CLS with image optimization and layout stabilization."
        ),
    )


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

    lines.extend(["", "[UiUxAgent]"])
    for result in by_agent.get("UiUxAgent", []):
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
        description="Run lint/ops/security/uiux roundtable checks"
    )
    parser.add_argument("--auto-recover-gha", action="store_true")
    parser.add_argument("--gha-rerun-limit", type=int, default=2)
    parser.add_argument("--sentry-unresolved-threshold", type=int, default=0)
    parser.add_argument("--skip-lint", action="store_true")
    parser.add_argument("--skip-vercel", action="store_true")
    parser.add_argument("--skip-github-actions", action="store_true")
    parser.add_argument("--skip-sentry", action="store_true")
    parser.add_argument("--skip-uiux", action="store_true")
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
    run_uiux = env_enabled("RUN_UIUX_CHECKS", True) and not args.skip_uiux

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
    if run_uiux:
        results.append(check_uiux())

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

    if any(result.priority == "P0" and not result.ok for result in results):
        return 2
    if any(not result.ok for result in results):
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.TimeoutExpired as error:
        command = " ".join(shlex.quote(part) for part in error.cmd)
        print(f"Command timed out: {command}", file=sys.stderr)
        raise
