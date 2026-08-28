#!/usr/bin/env python3
"""Unified Slack / Discord notifier for cron and CI pipelines.

Three transports, tried in this order:

1. **Slack Bot API** (`chat.postMessage`) via `SLACK_BOT_TOKEN` +
   `SLACK_CHANNEL_ID`. This is the one that actually works here: both secrets
   are configured in this repo and two workflows already use them
   (`slack-post-notify.yml`, `slack-category-digest.yml`).
2. Slack incoming webhook via `SLACK_WEBHOOK_URL`.
3. Discord webhook via `DISCORD_WEBHOOK_URL`.

Neither webhook secret has ever been registered here (`gh secret list`,
2026-08-24), which is why every call to this script was a silent no-op until the
Bot API transport was added. It printed `[INFO]` and returned True — the same
value as a successful send. Requiring a *new* credential when a working one
exists is what PR #583 rejected for `monitoring.yml`; this follows that
decision.

Slack's Web API answers **HTTP 200 with `{"ok": false}`** on failure, so the
Bot transport parses the response body. Treating 200 as success is precisely the
false-success bug this module has already been fixed for once.

Pass `--require-delivery` to exit non-zero when nothing was configured or the
send failed. Use it wherever a lost notification is itself the regression worth
knowing about.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
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


def get_slack_bot_config() -> Optional[Dict[str, str]]:
    """Slack Bot API credentials, or None when either half is missing."""
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    channel = os.getenv("SLACK_CHANNEL_ID", "").strip()
    if token and channel:
        return {"token": token, "channel": channel}
    return None


def send_slack_bot(
    config: Dict[str, str],
    title: str,
    message: str,
    status: str = "SUCCESS",
    timeout: int = 5,
) -> bool:
    """POST to chat.postMessage, reading `ok` from the body.

    The Web API returns HTTP 200 with `{"ok": false, "error": "..."}` for
    channel_not_found, not_in_channel, invalid_auth and friends. Checking only
    the status code would report every one of those as a successful send.
    """
    payload: Dict[str, Any] = {
        "channel": config["channel"],
        # `text` is the notification/accessibility fallback. Without it Slack
        # delivers the blocks but push notifications and screen readers get
        # nothing.
        "text": f"{mask_sensitive_info(title)} — {status}",
        "unfurl_links": False,
        "unfurl_media": False,
        **build_slack_payload(title, message, status),
    }
    try:
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {config['token']}",
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "TechBlog-Notifier/1.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8") or "{}")
    except Exception as e:  # noqa: BLE001 — any transport failure is a failure
        print(
            f"[WARN] Slack Bot API request failed: {mask_sensitive_info(str(e))}",
            file=sys.stderr,
        )
        return False

    if body.get("ok") is True:
        return True
    # `error` is a Slack error code (channel_not_found, invalid_auth, ...), not
    # a secret, but mask anyway — this is the branch that runs when something
    # unexpected came back.
    print(
        "[WARN] Slack Bot API returned ok=false: "
        f"{mask_sensitive_info(str(body.get('error', 'unknown')))}",
        file=sys.stderr,
    )
    return False


def send_http_post(url: str, payload: Dict[str, Any], timeout: int = 5) -> bool:
    """Send JSON payload over HTTP POST with timeout.

    Incoming webhooks (Slack and Discord) genuinely signal failure with a
    non-2xx status, so a status check is correct here — unlike the Web API
    above.
    """
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
        # e.reason is a status phrase today, but this is the one error branch that
        # was not masked; a future urllib that includes the URL would leak the
        # webhook token. Mask unconditionally rather than relying on that.
        print(
            f"[WARN] Webhook HTTP Error: {e.code} - {mask_sensitive_info(str(e.reason))}",
            file=sys.stderr,
        )
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
    """Deliver to every configured transport. False means a send failed.

    "Nothing configured" returns True — it is not a delivery failure — but it
    prints a `::warning::` so the state is visible in the Actions run summary
    rather than buried in step output. Callers that need it to be an error pass
    `--require-delivery`, which consults `delivered_anywhere()`.
    """
    bot = get_slack_bot_config()
    urls = get_webhook_urls()
    slack_url = urls.get("slack")
    discord_url = urls.get("discord")

    if not bot and not slack_url and not discord_url:
        # Measured 2026-08-24 (`gh secret list`): SLACK_BOT_TOKEN and
        # SLACK_CHANNEL_ID are configured; SLACK_WEBHOOK_URL and
        # DISCORD_WEBHOOK_URL never were. Before the Bot transport existed,
        # every call landed here, printed [INFO] and returned True — the same
        # value as a successful send, which is why nobody noticed for a month.
        print(
            "::warning title=Notification not delivered::"
            "No transport configured (SLACK_BOT_TOKEN+SLACK_CHANNEL_ID, "
            "SLACK_WEBHOOK_URL, or DISCORD_WEBHOOK_URL), so this notification "
            "went nowhere."
        )
        print(
            "[WARN] No notification transport configured. Nothing was sent.",
            file=sys.stderr,
        )
        return True

    success = True
    if bot:
        if send_slack_bot(bot, title, message, status):
            print("[INFO] Slack notification sent via chat.postMessage.")
        else:
            success = False

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


def delivered_anywhere() -> bool:
    """Whether at least one transport is configured."""
    urls = get_webhook_urls()
    return bool(get_slack_bot_config() or urls.get("slack") or urls.get("discord"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", type=str, default="Tech Blog Cron Pipeline", help="Notification Title")
    parser.add_argument("--message", type=str, required=True, help="Notification Message Body")
    parser.add_argument("--status", choices=["SUCCESS", "WARNING", "FAILED"], default="SUCCESS", help="Execution Status")
    parser.add_argument(
        "--require-delivery",
        action="store_true",
        help=(
            "exit non-zero when no transport is configured. Use where a lost "
            "notification is itself the regression worth knowing about — "
            "SLACK_BOT_TOKEN and SLACK_CHANNEL_ID are configured in this repo, "
            "so their absence means a removal or lost secret access, not an "
            "optional integration."
        ),
    )
    args = parser.parse_args()

    if args.require_delivery and not delivered_anywhere():
        # Same reasoning as slack-post-notify.yml: fail-closed is safe precisely
        # BECAUSE the bot secrets exist. Contrast gsc-queue-refresh.yml, whose
        # secrets have never been configured — fail-closed there would only
        # produce a permanently red cron that gets muted.
        print(
            "::error title=Notification transport missing::"
            "--require-delivery was set but no transport is configured. "
            "SLACK_BOT_TOKEN and SLACK_CHANNEL_ID are configured in this repo, "
            "so this is a regression — check secret access for this workflow.",
        )
        return 1

    # Propagate delivery failure. Previously the return value was discarded and
    # main() always exited 0, so no caller could ever detect that a POST failed.
    delivered = notify(title=args.title, message=args.message, status=args.status)
    return 0 if delivered else 1


if __name__ == "__main__":
    sys.exit(main())
