"""Unit tests for check_cron_status.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import check_cron_status as checker


def test_get_lock_status_nonexistent(tmp_path):
    lock_dir = tmp_path / "test.lock"
    active, pid = checker.get_lock_status(lock_dir)
    assert active is False
    assert pid is None


def test_parse_ai_tools_log(tmp_path):
    log_file = tmp_path / "ai-tools-update.log"
    log_content = (
        "[2026-08-23 18:07:45 KST] [INFO] Starting Weekly AI Tools & Engine Auto-Update...\n"
        "[2026-08-23 18:07:45 KST] [INFO] [1/5] Updating Antigravity CLI (agy)...\n"
        "[2026-08-23 18:07:46 KST] [INFO] ✅ agy updated successfully: 1.1.19 -> 1.1.19\n"
        "[2026-08-23 18:07:46 KST] [INFO] [2/5] Updating Claude Code CLI (claude)...\n"
        "[2026-08-23 18:07:48 KST] [INFO] ✅ claude updated successfully: 2.1.228 -> 2.1.228\n"
        "[2026-08-23 18:07:48 KST] [INFO] [3/5] Updating Global NPM packages (OMC, OpenClaw, Codex)...\n"
        "[2026-08-23 18:08:31 KST] [INFO] ✅ Global NPM packages updated (oh-my-claude-sisyphus, oh-my-opencode, openclaw, @openai/codex).\n"
        "[2026-08-23 18:08:31 KST] [INFO] [4/5] Upgrading OpenCode via Homebrew...\n"
        "[2026-08-23 18:08:37 KST] [INFO] ✅ opencode version: 1.14.30\n"
        "[2026-08-23 18:08:37 KST] [INFO] 🎉 Weekly AI Tools Update Completed Successfully.\n"
    )
    log_file.write_text(log_content, encoding="utf-8")

    res = checker.parse_ai_tools_log(log_file)
    assert res["status"] == "SUCCESS"
    assert res["tools"]["agy"] == "updated"
    assert res["tools"]["claude"] == "updated"
    assert res["tools"]["npm"] == "updated"
    assert "1.14.30" in res["tools"]["opencode"]
    assert res["start_time"] == "2026-08-23 18:07:45 KST"
    assert res["finish_time"] == "2026-08-23 18:08:37 KST"


def test_monitor_does_not_report_on_the_removed_modernizer_pipeline():
    """The blog-autonomous pipeline was removed on 2026-08-24.

    A monitor that keeps a section for a pipeline nobody runs reports a
    permanent ❌ that carries no information — the dead-channel alert failure
    mode. If the pipeline is ever revived, revive this section deliberately.
    """
    assert not hasattr(checker, "parse_blog_autonomous_log")
    assert "daily_autonomous" not in checker.check_crontab_entries()


def test_format_status_badge():
    assert "HEALTHY" in checker.format_status_badge("SUCCESS")
    assert "WARNING" in checker.format_status_badge("WARNING")
    assert "FAILED" in checker.format_status_badge("FAILED")
