#!/usr/bin/env python3
"""Mac mini 24/7 Autonomous Cron & Tooling Healthcheck Monitor.

Parses logs from `logs/blog-autonomous.log` and `logs/ai-tools-update.log`,
verifies active concurrency locks, crontab registration, and reports
comprehensive status with security masking.
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
    """Verify if blog autonomous and AI tools update jobs exist in crontab."""
    try:
        res = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if res.returncode != 0:
            return {"weekly_update": False, "daily_autonomous": False}
        content = res.stdout
        return {
            "weekly_update": "weekly-ai-tools-update.sh" in content,
            "daily_autonomous": "run-blog-autonomous-cron.sh" in content,
        }
    except Exception:
        return {"weekly_update": False, "daily_autonomous": False}


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


def parse_blog_autonomous_log(log_path: Path) -> Dict[str, Any]:
    """Parse latest execution run from blog-autonomous.log."""
    if not log_path.exists():
        return {"status": "NOT_FOUND", "message": "Log file not found"}

    content = log_path.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()

    start_time = None
    finish_time = None
    status = "SUCCESS"
    news_collected = 0
    new_posts_created: List[str] = []
    modernized_posts: List[str] = []
    warnings: List[str] = []
    errors: List[str] = []

    session_start_indices = [
        i
        for i, line in enumerate(lines)
        if "Starting Daily Tech Blog Autonomous" in line
    ]
    if session_start_indices:
        session_lines = lines[session_start_indices[-1] :]
    else:
        session_lines = lines[-150:]

    for line in session_lines:
        ts_match = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [A-Z]+)\]", line)
        if ts_match:
            current_ts = ts_match.group(1)
            if start_time is None:
                start_time = current_ts
            finish_time = current_ts

        if "Enhanced post:" in line:
            post_name = line.split("Enhanced post:")[-1].strip()
            modernized_posts.append(mask_sensitive_info(post_name))
        elif "Created post:" in line:
            post_name = line.split("Created post:")[-1].strip()
            new_posts_created.append(mask_sensitive_info(post_name))
        elif "Loaded" in line and "news items" in line:
            m = re.search(r"Loaded (\d+) news items", line)
            if m:
                news_collected = int(m.group(1))

        if "[WARN]" in line or "WARNING" in line:
            warnings.append(mask_sensitive_info(line.strip()))
        if "[ERROR]" in line or "Error:" in line or "Traceback" in line:
            errors.append(mask_sensitive_info(line.strip()))

    if errors:
        status = "FAILED"
    elif warnings:
        status = "WARNING" if not new_posts_created and not modernized_posts else "SUCCESS"

    return {
        "start_time": start_time,
        "finish_time": finish_time,
        "status": status,
        "news_items_collected": news_collected,
        "new_posts_published": new_posts_created,
        "modernized_posts_count": len(modernized_posts),
        "modernized_posts": modernized_posts,
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
    print(" 🖥️  Mac mini 24/7 Autonomous Pipeline & AI Tools Health Report")
    print("=" * 70)

    # Crontab check
    cron = data["crontab"]
    w_icon = "✅" if cron["weekly_update"] else "❌"
    d_icon = "✅" if cron["daily_autonomous"] else "❌"
    print(f"\n⏰ Crontab Registration Status:")
    print(f"  • Weekly AI Tools Update (Sun 04:00 KST): {w_icon} {'Active' if cron['weekly_update'] else 'Missing'}")
    print(f"  • Daily Autonomous Modernizer (05:00 KST): {d_icon} {'Active' if cron['daily_autonomous'] else 'Missing'}")

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

    # Daily Blog Autonomous Report
    blog_auto = data["blog_autonomous"]
    print(f"\n🤖 [2] Daily Tech Blog Autonomous Modernizer ({blog_auto.get('finish_time', 'N/A')}):")
    print(f"  Status: {format_status_badge(blog_auto.get('status', 'UNKNOWN'))}")
    print(f"  News Ingested: {blog_auto.get('news_items_collected', 0)} items")
    print(f"  Modernized Posts: {blog_auto.get('modernized_posts_count', 0)} posts")
    if blog_auto.get("new_posts_published"):
        print(f"  Auto-Published Posts:")
        for p in blog_auto["new_posts_published"]:
            print(f"    📰 {p}")
    if blog_auto.get("recent_errors"):
        print("  Recent Errors:")
        for err in blog_auto["recent_errors"]:
            print(f"    ❌ {err}")

    print("\n" + "=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check 24/7 cron and update pipeline status")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    ai_tools_log = LOGS_DIR / "ai-tools-update.log"
    blog_auto_log = LOGS_DIR / "blog-autonomous.log"

    ai_lock, ai_pid = get_lock_status(Path("/tmp/ai-tools-update.lock"))
    blog_lock, blog_pid = get_lock_status(Path("/tmp/blog-autonomous-modernizer.lock"))

    report_data = {
        "timestamp": datetime.now().isoformat(),
        "crontab": check_crontab_entries(),
        "locks": {
            "ai_tools_update": {"active": ai_lock, "pid": ai_pid},
            "blog_autonomous": {"active": blog_lock, "pid": blog_pid},
        },
        "ai_tools_update": parse_ai_tools_log(ai_tools_log),
        "blog_autonomous": parse_blog_autonomous_log(blog_auto_log),
    }

    if args.json:
        print(json.dumps(report_data, indent=2, ensure_ascii=False))
    else:
        print_cli_report(report_data)

    # Return non-zero if either failed
    if (
        report_data["ai_tools_update"].get("status") == "FAILED"
        or report_data["blog_autonomous"].get("status") == "FAILED"
    ):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
