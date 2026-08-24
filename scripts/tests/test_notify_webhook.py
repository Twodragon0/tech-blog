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


def test_no_configured_target_emits_a_ci_visible_warning(capsys):
    """Silence here is what hid the dead channel.

    Neither SLACK_WEBHOOK_URL nor DISCORD_WEBHOOK_URL is registered in this repo
    (measured 2026-08-24 via `gh secret list`), so every call has been a no-op.
    It used to print [INFO] and return True — indistinguishable from a
    successful send. The ::warning:: annotation puts it in the run summary.
    """
    with patch.dict(os.environ, {}, clear=True):
        notifier.notify("Title", "Message")
    out = capsys.readouterr().out
    assert "::warning" in out
    assert "not delivered anywhere" in out


@patch("urllib.request.urlopen", side_effect=OSError("connection refused"))
@patch.dict(
    os.environ,
    {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/T00/B00/X00"},
    clear=True,
)
def test_main_exits_nonzero_when_delivery_fails(_mock_urlopen):
    """main() used to discard notify()'s result and always return 0.

    A caller checking the exit code could therefore never detect that a POST
    failed, which makes the notifier unusable as a monitored step.
    """
    import sys as _sys

    argv = _sys.argv
    _sys.argv = ["notify_webhook.py", "--message", "m", "--status", "FAILED"]
    try:
        rc = notifier.main()
    finally:
        _sys.argv = argv
    assert rc == 1


@patch("urllib.request.urlopen")
@patch.dict(
    os.environ,
    {"SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/T00/B00/X00"},
    clear=True,
)
def test_main_exits_zero_when_delivery_succeeds(mock_urlopen):
    """The counterpart — proves the nonzero case above is not vacuous."""
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_urlopen.return_value.__enter__.return_value = mock_resp

    import sys as _sys

    argv = _sys.argv
    _sys.argv = ["notify_webhook.py", "--message", "m"]
    try:
        rc = notifier.main()
    finally:
        _sys.argv = argv
    assert rc == 0
