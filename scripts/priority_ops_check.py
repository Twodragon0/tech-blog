#!/usr/bin/env python3
"""Run prioritized ops checks and emit a Slack-ready summary."""

import argparse
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

PROJECT_ROOT = Path(__file__).parent.parent


@dataclass
class CheckResult:
    name: str
    success: bool
    priority: str
    summary: str


def _run_command(command: List[str]) -> Tuple[bool, str]:
    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = (result.stdout + result.stderr).strip()
    return result.returncode == 0, output


def _summarize_output(name: str, output: str) -> str:
    lines = [line for line in output.splitlines() if line.strip()]
    if not lines:
        return f"{name}: no output"
    if len(lines) <= 6:
        return "\n".join(lines)
    return "\n".join(lines[:6]) + "\n..."


def run_post_checks(enabled: bool) -> CheckResult:
    if not enabled:
        return CheckResult("post-checks", True, "P2", "Skipped")
    ok, output = _run_command(["python3", "scripts/check_posts.py"])
    summary = _summarize_output("check_posts.py", output)
    priority = "P0" if not ok else "P2"
    return CheckResult("post-checks", ok, priority, summary)


def run_image_checks(enabled: bool) -> CheckResult:
    if not enabled:
        return CheckResult("image-checks", True, "P2", "Skipped")
    ok, output = _run_command(
        ["python3", "scripts/verify_images_unified.py", "--missing"]
    )
    summary = _summarize_output("verify_images_unified.py", output)
    priority = "P0" if not ok else "P2"
    return CheckResult("image-checks", ok, priority, summary)


def run_vercel_checks(enabled: bool) -> CheckResult:
    if not enabled:
        return CheckResult("vercel-checks", True, "P2", "Skipped")
    ok, output = _run_command(
        ["bash", "scripts/monitor_vercel_builds.sh", "--alert-only"]
    )
    summary = _summarize_output("monitor_vercel_builds.sh", output)
    priority = "P1" if not ok else "P2"
    return CheckResult("vercel-checks", ok, priority, summary)


def format_summary(results: List[CheckResult]) -> str:
    failures = [r for r in results if not r.success]
    priority = "P2"
    if any(r.priority == "P0" for r in failures):
        priority = "P0"
    elif any(r.priority == "P1" for r in failures):
        priority = "P1"

    header = f"Priority Ops Check: {priority}"
    lines = [header, "", "Results:"]
    for result in results:
        status = "OK" if result.success else "FAIL"
        lines.append(f"- {result.name}: {status} ({result.priority})")
    lines.append("")
    for result in results:
        lines.append(f"[{result.name}] {result.summary}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run prioritized ops checks")
    parser.add_argument("--post-checks", action="store_true")
    parser.add_argument("--image-checks", action="store_true")
    parser.add_argument("--vercel-checks", action="store_true")
    args = parser.parse_args()

    post_checks = args.post_checks or os.getenv("RUN_POST_CHECKS", "true") == "true"
    image_checks = args.image_checks or os.getenv("RUN_IMAGE_CHECKS", "true") == "true"
    vercel_checks = (
        args.vercel_checks or os.getenv("RUN_VERCEL_CHECKS", "false") == "true"
    )

    results = [
        run_post_checks(post_checks),
        run_image_checks(image_checks),
        run_vercel_checks(vercel_checks),
    ]

    print(format_summary(results))
    return 0 if all(r.success for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
