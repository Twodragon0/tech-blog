"""Unit tests for notify_webhook.py."""

from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

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
    assert "No transport configured" in out


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


# ---------------------------------------------------------------------------
# Slack Bot API transport (chat.postMessage)
# ---------------------------------------------------------------------------

BOT_ENV = {"SLACK_BOT_TOKEN": "xoxb-test-token-value", "SLACK_CHANNEL_ID": "C0123456789"}


def _resp(body: str):
    resp = MagicMock()
    resp.read.return_value = body.encode("utf-8")
    return resp


def test_bot_config_requires_both_halves():
    with patch.dict(os.environ, {"SLACK_BOT_TOKEN": "xoxb-x"}, clear=True):
        assert notifier.get_slack_bot_config() is None
    with patch.dict(os.environ, {"SLACK_CHANNEL_ID": "C1"}, clear=True):
        assert notifier.get_slack_bot_config() is None
    with patch.dict(os.environ, BOT_ENV, clear=True):
        assert notifier.get_slack_bot_config() == {
            "token": BOT_ENV["SLACK_BOT_TOKEN"],
            "channel": BOT_ENV["SLACK_CHANNEL_ID"],
        }


@patch("urllib.request.urlopen")
def test_bot_send_succeeds_only_when_body_says_ok(mock_urlopen):
    mock_urlopen.return_value.__enter__.return_value = _resp('{"ok": true}')
    assert notifier.send_slack_bot({"token": "t", "channel": "C1"}, "T", "M") is True


@patch("urllib.request.urlopen")
def test_http_200_with_ok_false_is_a_failure(mock_urlopen):
    """Slack answers 200 for channel_not_found / invalid_auth / not_in_channel.

    Checking only the status code would report every one of those as a
    successful send — the same false-success shape this module was already
    fixed for once.
    """
    mock_urlopen.return_value.__enter__.return_value = _resp(
        '{"ok": false, "error": "channel_not_found"}'
    )
    assert notifier.send_slack_bot({"token": "t", "channel": "C1"}, "T", "M") is False


@patch("urllib.request.urlopen")
def test_bot_payload_carries_channel_and_text_fallback(mock_urlopen):
    """Blocks alone give no push notification and nothing to a screen reader."""
    mock_urlopen.return_value.__enter__.return_value = _resp('{"ok": true}')
    notifier.send_slack_bot({"token": "t", "channel": "C777"}, "Title", "Body", "FAILED")

    req = mock_urlopen.call_args[0][0]
    sent = json.loads(req.data.decode("utf-8"))
    assert sent["channel"] == "C777"
    assert "Title" in sent["text"] and "FAILED" in sent["text"]
    assert sent["attachments"], "Block Kit attachments missing"
    assert req.get_header("Authorization") == "Bearer t"


@patch("urllib.request.urlopen")
@patch.dict(os.environ, BOT_ENV, clear=True)
def test_notify_prefers_the_bot_transport(mock_urlopen):
    mock_urlopen.return_value.__enter__.return_value = _resp('{"ok": true}')
    assert notifier.notify("T", "M") is True
    assert "chat.postMessage" in mock_urlopen.call_args[0][0].full_url


@patch.dict(os.environ, BOT_ENV, clear=True)
def test_require_delivery_passes_when_bot_is_configured():
    assert notifier.delivered_anywhere() is True


def test_require_delivery_exits_nonzero_with_no_transport():
    """Fail-closed. Safe precisely because the bot secrets exist in this repo."""
    import sys as _sys

    argv = _sys.argv
    _sys.argv = ["notify_webhook.py", "--message", "m", "--require-delivery"]
    try:
        with patch.dict(os.environ, {}, clear=True):
            assert notifier.delivered_anywhere() is False
            rc = notifier.main()
    finally:
        _sys.argv = argv
    assert rc == 1


def test_no_transport_without_require_delivery_still_exits_zero():
    """Proves the fail-closed case above is opt-in, not a behaviour change."""
    import sys as _sys

    argv = _sys.argv
    _sys.argv = ["notify_webhook.py", "--message", "m"]
    try:
        with patch.dict(os.environ, {}, clear=True):
            rc = notifier.main()
    finally:
        _sys.argv = argv
    assert rc == 0
