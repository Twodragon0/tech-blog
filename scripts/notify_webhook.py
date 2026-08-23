#!/usr/bin/env python3
"""Unified Slack & Discord Webhook Notifier for Autonomous Tech Blog & Cron Pipelines.

Sends formatted status cards to Slack/Discord webhooks with security masking,
timeouts, and graceful fallbacks.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.lib.security import mask_sensitive_info


def get_webhook_urls() -> Dict[str, Optional[str]]:
    """Retrieve Slack and Discord webhook URLs from environment or local dot-env."""
    slack_url = os.getenv("SLACK_WEBHOOK_URL") or os.getenv("SLACK_WEBHOOK")
    discord_url = os.getenv("DISCORD_WEBHOOK_URL") or os.getenv("DISCORD_WEBHOOK")

    # Check local .env if not found in current process env
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SLACK_WEBHOOK_URL=") and not slack_url:
                slack_url = line.split("=", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("DISCORD_WEBHOOK_URL=") and not discord_url:
                discord_url = line.split("=", 1)[1].strip().strip('"').strip("'")

    return {
        "slack": slack_url if slack_url and "hooks.slack.com" in slack_url else None,
        "discord": discord_url if discord_url and "discord.com/api/webhooks" in discord_url else None,
    }


def send_http_post(url: str, payload: Dict[str, Any], timeout: int = 5) -> bool:
    """Send JSON payload over HTTP POST with timeout."""
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "TechBlog-Notifier/1.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status in (200, 204)
    except urllib.error.HTTPError as e:
        print(f"[WARN] Webhook HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"[WARN] Webhook request failed: {mask_sensitive_info(str(e))}", file=sys.stderr)
        return False


def build_slack_payload(title: str, message: str, status: str = "SUCCESS") -> Dict[str, Any]:
    """Build Slack Block Kit message payload."""
    color = "#36a64f" if status == "SUCCESS" else ("#ECB22E" if status == "WARNING" else "#E01E5A")
    icon = "🟢" if status == "SUCCESS" else ("🟡" if status == "WARNING" else "🔴")

    safe_title = mask_sensitive_info(title)
    safe_msg = mask_sensitive_info(message)

    return {
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": f"{icon} {safe_title}", "emoji": True},
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": safe_msg},
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Mac mini 24/7 Automation | *Status: {status}* | <https://tech.2twodragon.com|Tech Blog>",
                            }
                        ],
                    },
                ],
            }
        ]
    }


def build_discord_payload(title: str, message: str, status: str = "SUCCESS") -> Dict[str, Any]:
    """Build Discord Embed payload."""
    color = 0x36A64F if status == "SUCCESS" else (0xECB22E if status == "WARNING" else 0xE01E5A)
    icon = "🟢" if status == "SUCCESS" else ("🟡" if status == "WARNING" else "🔴")

    safe_title = mask_sensitive_info(title)
    safe_msg = mask_sensitive_info(message)

    return {
        "embeds": [
            {
                "title": f"{icon} {safe_title}",
                "description": safe_msg,
                "color": color,
                "footer": {
                    "text": f"Mac mini 24/7 Automation • Status: {status} • tech.2twodragon.com"
                },
            }
        ]
    }


def notify(title: str, message: str, status: str = "SUCCESS") -> bool:
    """Send notification to all configured webhooks."""
    urls = get_webhook_urls()
    slack_url = urls.get("slack")
    discord_url = urls.get("discord")

    if not slack_url and not discord_url:
        print("[INFO] No Webhook URLs configured (SLACK_WEBHOOK_URL or DISCORD_WEBHOOK_URL). Skipping notification.")
        return True

    success = True
    if slack_url:
        payload = build_slack_payload(title, message, status)
        res = send_http_post(slack_url, payload)
        if res:
            print("[INFO] ✅ Slack notification sent successfully.")
        else:
            success = False

    if discord_url:
        payload = build_discord_payload(title, message, status)
        res = send_http_post(discord_url, payload)
        if res:
            print("[INFO] ✅ Discord notification sent successfully.")
        else:
            success = False

    return success


def main() -> int:
    parser = argparse.ArgumentParser(description="Send Webhook Notification for Cron / Pipelines")
    parser.add_argument("--title", type=str, default="Tech Blog Cron Pipeline", help="Notification Title")
    parser.add_argument("--message", type=str, required=True, help="Notification Message Body")
    parser.add_argument("--status", choices=["SUCCESS", "WARNING", "FAILED"], default="SUCCESS", help="Execution Status")
    args = parser.parse_args()

    notify(title=args.title, message=args.message, status=args.status)
    return 0


if __name__ == "__main__":
    sys.exit(main())
