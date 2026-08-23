"""Unit tests for notify_webhook.py."""

from __future__ import annotations

import os
from unittest.mock import patch, MagicMock
from scripts import notify_webhook as notifier


def test_build_slack_payload():
    payload = notifier.build_slack_payload(
        title="Weekly AI Tools Update",
        message="• agy updated\n• claude updated",
        status="SUCCESS",
    )
    assert "attachments" in payload
    assert payload["attachments"][0]["color"] == "#36a64f"
    assert "🟢" in payload["attachments"][0]["blocks"][0]["text"]["text"]
    assert "• agy updated" in payload["attachments"][0]["blocks"][1]["text"]["text"]


def test_build_discord_payload():
    payload = notifier.build_discord_payload(
        title="Daily Tech Blog Modernizer",
        message="5 posts modernized",
        status="WARNING",
    )
    assert "embeds" in payload
    assert payload["embeds"][0]["color"] == 0xECB22E
    assert "🟡" in payload["embeds"][0]["title"]
    assert "5 posts modernized" in payload["embeds"][0]["description"]


@patch.dict(os.environ, {}, clear=True)
def test_notify_skips_when_no_urls():
    # Should safely return True when no webhook URLs configured
    res = notifier.notify("Test Title", "Test Message")
    assert res is True


@patch("urllib.request.urlopen")
@patch.dict(os.environ, {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/T00/B00/X00"})
def test_notify_sends_slack(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    res = notifier.notify("Daily Run", "Run succeeded", status="SUCCESS")
    assert res is True
    assert mock_urlopen.called
