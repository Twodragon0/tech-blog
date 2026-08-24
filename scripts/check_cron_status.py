#!/usr/bin/env python3
"""Mac mini 24/7 Cron & Tooling Healthcheck Monitor.

Parses `logs/ai-tools-update.log`, verifies active concurrency locks and
crontab registration, and reports status with security masking.

The daily blog-autonomous half of this monitor was removed on 2026-08-24
together with the pipeline it watched (`run-blog-autonomous-cron.sh` +
`autonomous_post_modernizer.py`); see notes/autonomous-modernizer-retro.md.
Reporting on a pipeline that no longer exists produces a permanent red ❌
that means nothing, which is the failure mode this repo has already paid for
twice with dead-channel Slack alerts.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = REPO_ROOT / "logs"

sys.path.insert(0, str(REPO_ROOT))
from scripts.lib.security import mask_sensitive_info


def get_lock_status(lock_dir: Path) -> Tuple[bool, Optional[int]]:
    """Check if lock directory exists and if process is alive."""
    if not lock_dir.exists():
        return False, None
    pid_file = lock_dir / "pid"
    if not pid_file.exists():
        return True, None
    try:
        pid = int(pid_file.read_text().strip())
        # Check if process is still running
        os.kill(pid, 0)
        return True, pid
    except (ValueError, OSError):
        return False, None


def check_crontab_entries() -> Dict[str, bool]:
    """Verify if the AI tools update job exists in crontab."""
    try:
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if res.returncode != 0:
            return {"weekly_update": False}
        return {"weekly_update": "weekly-ai-tools-update.sh" in res.stdout}
    except Exception:
        return {"weekly_update": False}


def parse_ai_tools_log(log_path: Path) -> Dict[str, Any]:
    """Parse latest execution run from ai-tools-update.log."""
    if not log_path.exists():
        return {"status": "NOT_FOUND", "message": "Log file not found"}

    content = log_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()

    start_time = None
    finish_time = None
    status = "SUCCESS"
    tool_statuses: Dict[str, str] = {}
    warnings: List[str] = []
    errors: List[str] = []

    # Find the latest session
    session_start_indices = [
        i for i, line in enumerate(lines) if "Starting Weekly AI Tools" in line
    ]
    if session_start_indices:
        session_lines = lines[session_start_indices[-1] :]
    else:
        session_lines = lines[-100:]

    for line in session_lines:
        ts_match = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Z]+)\]", line)
        if ts_match:
            current_ts = ts_match.group(1)
            if start_time is None:
                start_time = current_ts
            finish_time = current_ts

        if "Updating Antigravity CLI" in line:
            tool_statuses["agy"] = "in_progress"
        elif "agy updated successfully" in line:
            tool_statuses["agy"] = "updated"
        elif "Updating Claude Code CLI" in line:
            tool_statuses["claude"] = "in_progress"
        elif "claude updated successfully" in line:
            tool_statuses["claude"] = "updated"
        elif "Global NPM packages updated" in line:
            tool_statuses["npm"] = "updated"
        elif "opencode version:" in line:
            tool_statuses["opencode"] = line.split("version:")[-1].strip()

        if "[WARN]" in line:
            warnings.append(mask_sensitive_info(line.strip()))
        if "[ERROR]" in line or "Error:" in line:
            errors.append(mask_sensitive_info(line.strip()))

    if errors:
        status = "FAILED"
    elif warnings:
        status = "WARNING"

    return {
        "start_time": start_time,
        "finish_time": finish_time,
        "status": status,
        "tools": tool_statuses,
        "warnings_count": len(warnings),
        "errors_count": len(errors),
        "recent_warnings": warnings[-3:],
        "recent_errors": errors[-3:],
    }


def format_status_badge(status: str) -> str:
    """Return colored status string."""
    if status == "SUCCESS":
        return "🟢 [HEALTHY / SUCCESS]"
    elif status == "WARNING":
        return "🟡 [WARNING]"
    elif status == "FAILED":
        return "🔴 [FAILED / ERROR]"
    return f"⚪ [{status}]"


def print_cli_report(data: Dict[str, Any]) -> None:
    """Print clean human-readable CLI report."""
    print("=" * 70)
    print(" 🖥️  Mac mini AI Tools Update Health Report")
    print("=" * 70)

    # Crontab check
    cron = data["crontab"]
    w_icon = "✅" if cron["weekly_update"] else "❌"
    print(f"\n⏰ Crontab Registration Status:")
    print(f"  • Weekly AI Tools Update (Sun 04:00 KST): {w_icon} {'Active' if cron['weekly_update'] else 'Missing'}")

    # Active Locks
    print(f"\n🔒 Concurrency Lock Status:")
    for lock_name, lock_info in data["locks"].items():
        state = "🔒 Active (Running)" if lock_info["active"] else "🔓 Idle / Released"
        pid_str = f" [PID: {lock_info['pid']}]" if lock_info["pid"] else ""
        print(f"  • {lock_name}: {state}{pid_str}")

    # Weekly Update Report
    ai_up = data["ai_tools_update"]
    print(f"\n🔄 [1] Weekly AI Tools Auto-Update ({ai_up.get('finish_time', 'N/A')}):")
    print(f"  Status: {format_status_badge(ai_up.get('status', 'UNKNOWN'))}")
    tools = ai_up.get("tools", {})
    if tools:
        print(f"  Tools: AGY ({tools.get('agy', 'ok')}), Claude ({tools.get('claude', 'ok')}), NPM ({tools.get('npm', 'ok')}), OpenCode ({tools.get('opencode', 'ok')})")
    if ai_up.get("recent_errors"):
        print("  Recent Errors:")
        for err in ai_up["recent_errors"]:
            print(f"    ❌ {err}")

    print("\n" + "=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check 24/7 cron and update pipeline status")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    ai_tools_log = LOGS_DIR / "ai-tools-update.log"

    ai_lock, ai_pid = get_lock_status(Path("/tmp/ai-tools-update.lock"))

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "crontab": check_crontab_entries(),
        "locks": {
            "ai_tools_update": {"active": ai_lock, "pid": ai_pid},
        },
        "ai_tools_update": parse_ai_tools_log(ai_tools_log),
    }

    if args.json:
        print(json.dumps(report_data, indent=2, ensure_ascii=False))
    else:
        print_cli_report(report_data)

    if report_data["ai_tools_update"].get("status") == "FAILED":
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
