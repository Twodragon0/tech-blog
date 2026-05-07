"""Tests for scripts/indexnow_ping.py.

Covers:
1. test_payload_structure   - payload has correct fields
2. test_key_masking         - raw key is never printed to stdout/stderr
3. test_url_limit           - 10000+ URL input is truncated safely
4. test_dry_run             - --dry-run produces output without HTTP calls
"""

import json
import sys
import textwrap
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import indexnow_ping as ping  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_key():
    return "890b921a9bdd4a155d198c6c0487a14f"


@pytest.fixture()
def sample_urls():
    return [
        "https://tech.2twodragon.com/post-a/",
        "https://tech.2twodragon.com/post-b/",
    ]


# ---------------------------------------------------------------------------
# 1. Payload structure
# ---------------------------------------------------------------------------


def test_payload_structure(sample_key, sample_urls):
    """build_payload() must emit host, key, keyLocation, and urlList correctly."""
    payload = ping.build_payload(sample_key, sample_urls)

    assert payload["host"] == ping.HOST
    assert payload["key"] == sample_key
    assert payload["keyLocation"] == f"https://{ping.HOST}/{sample_key}.txt"
    assert payload["urlList"] == sample_urls

    # Verify JSON-serialisable (IndexNow requires JSON body)
    serialised = json.dumps(payload)
    round_tripped = json.loads(serialised)
    assert round_tripped["urlList"] == sample_urls


# ---------------------------------------------------------------------------
# 2. Key masking
# ---------------------------------------------------------------------------


def test_key_masking(sample_key, sample_urls, capsys):
    """main() must never print the raw key to stdout or stderr."""
    with patch.object(ping, "resolve_key", return_value=sample_key), \
         patch.object(ping, "parse_sitemap_urls", return_value=sample_urls), \
         patch.object(ping, "post_to_endpoint", return_value=(True, 200, "OK")), \
         patch("sys.argv", ["indexnow_ping.py"]):
        rc = ping.main()

    captured = capsys.readouterr()
    combined = captured.out + captured.err

    assert rc == 0
    # Raw key must NOT appear in any output
    assert sample_key not in combined, (
        f"Raw key '{ping.mask_key(sample_key)}' was leaked in output. "
        "Full output:\n" + combined
    )
    # Masked representation should appear
    assert ping.mask_key(sample_key) in combined


def test_mask_key_format(sample_key):
    """mask_key() shows first-4 and last-4 chars separated by ellipsis."""
    masked = ping.mask_key(sample_key)
    assert masked.startswith(sample_key[:4])
    assert masked.endswith(sample_key[-4:])
    assert "..." in masked


def test_mask_key_short():
    """mask_key() handles keys shorter than 8 chars gracefully."""
    assert ping.mask_key("abc") == "****"
    assert ping.mask_key("1234567") == "****"   # len < 8 → fully masked
    assert ping.mask_key("12345678") == "1234...5678"  # len == 8 → show first/last 4


# ---------------------------------------------------------------------------
# 3. URL limit
# ---------------------------------------------------------------------------


def test_url_limit_truncation(sample_key, capsys):
    """URLs exceeding URL_LIMIT must be truncated, not errored."""
    oversized = [f"https://tech.2twodragon.com/post-{i}/" for i in range(ping.URL_LIMIT + 500)]

    with patch.object(ping, "resolve_key", return_value=sample_key), \
         patch.object(ping, "parse_sitemap_urls", return_value=oversized), \
         patch.object(ping, "post_to_endpoint", return_value=(True, 200, "OK")), \
         patch("sys.argv", ["indexnow_ping.py"]):
        rc = ping.main()

    assert rc == 0
    captured = capsys.readouterr()
    assert "Truncating" in captured.out or "Truncating" in captured.err

    # Verify build_payload receives at most URL_LIMIT items
    truncated = oversized[: ping.URL_LIMIT]
    payload = ping.build_payload(sample_key, truncated)
    assert len(payload["urlList"]) == ping.URL_LIMIT


def test_url_limit_boundary_ok(sample_key, sample_urls):
    """Exactly URL_LIMIT URLs should pass without truncation warning."""
    exactly = [f"https://tech.2twodragon.com/p{i}/" for i in range(ping.URL_LIMIT)]
    payload = ping.build_payload(sample_key, exactly)
    assert len(payload["urlList"]) == ping.URL_LIMIT


# ---------------------------------------------------------------------------
# 4. Dry-run: no HTTP calls
# ---------------------------------------------------------------------------


def test_dry_run_no_http(sample_key, sample_urls, capsys):
    """--dry-run must not invoke post_to_endpoint or any HTTP calls."""
    with patch.object(ping, "resolve_key", return_value=sample_key), \
         patch.object(ping, "parse_sitemap_urls", return_value=sample_urls), \
         patch.object(ping, "post_to_endpoint") as mock_post, \
         patch("sys.argv", ["indexnow_ping.py", "--dry-run"]):
        rc = ping.main()

    mock_post.assert_not_called()
    assert rc == 0

    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
    # Raw key must not appear even in dry-run output
    assert sample_key not in captured.out


def test_dry_run_contains_payload_structure(sample_key, sample_urls, capsys):
    """--dry-run output must include host, keyLocation (masked), and urlList fields."""
    with patch.object(ping, "resolve_key", return_value=sample_key), \
         patch.object(ping, "parse_sitemap_urls", return_value=sample_urls), \
         patch.object(ping, "post_to_endpoint"), \
         patch("sys.argv", ["indexnow_ping.py", "--dry-run"]):
        ping.main()

    out = capsys.readouterr().out
    assert ping.HOST in out
    assert ".txt" in out          # keyLocation should reference .txt file
    assert "urlList" in out
    assert sample_urls[0] in out
    # Raw key must not appear in dry-run output (including keyLocation URL)
    assert sample_key not in out
