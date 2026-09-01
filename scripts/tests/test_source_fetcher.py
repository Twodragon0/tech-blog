import json
import os
import sys
import tempfile
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "news"))
import source_fetcher


def test_fetch_failure_returns_none(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network down")

    monkeypatch.setattr(source_fetcher, "_http_get", boom)
    assert (
        source_fetcher.fetch_article("https://example.com/a", cache_path=None) is None
    )


def test_short_body_treated_as_failure(monkeypatch):
    monkeypatch.setattr(
        source_fetcher,
        "_http_get",
        lambda url, timeout=10: "<html><body>x</body></html>",
    )
    assert (
        source_fetcher.fetch_article("https://example.com/a", cache_path=None) is None
    )


def test_cache_hit_skips_fetch(monkeypatch):
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    key = source_fetcher._key("https://example.com/a")
    with open(cache.name, "w", encoding="utf-8") as fh:
        json.dump(
            {
                key: {
                    "text": "CACHED ARTICLE TEXT " * 20,
                    "expires_at": (now + timedelta(days=3)).isoformat(),
                }
            },
            fh,
        )

    def fail(*a, **k):
        raise AssertionError("should not fetch on cache hit")

    monkeypatch.setattr(source_fetcher, "_http_get", fail)
    out = source_fetcher.fetch_article(
        "https://example.com/a", cache_path=cache.name, now=now
    )
    assert out and out.startswith("CACHED ARTICLE TEXT")


def test_expired_cache_refetches(monkeypatch):
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    key = source_fetcher._key("https://example.com/a")
    with open(cache.name, "w", encoding="utf-8") as fh:
        json.dump(
            {key: {"text": "OLD", "expires_at": (now - timedelta(days=1)).isoformat()}},
            fh,
        )
    monkeypatch.setattr(
        source_fetcher,
        "_http_get",
        lambda url, timeout=10: (
            "<html><body>" + ("fresh article body " * 40) + "</body></html>"
        ),
    )
    out = source_fetcher.fetch_article(
        "https://example.com/a", cache_path=cache.name, now=now
    )
    assert out and "fresh article body" in out


def test_malformed_cache_entry_does_not_raise(monkeypatch):
    # entry whose expires_at is None (non-string) → the isinstance guard in
    # fetch_article rejects it and the entry is treated as a miss
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    url_a = "https://example.com/malformed-a"
    key_a = source_fetcher._key(url_a)
    with open(cache.name, "w", encoding="utf-8") as fh:
        json.dump({key_a: {"text": "x", "expires_at": None}}, fh)
    monkeypatch.setattr(
        source_fetcher,
        "_http_get",
        lambda url, timeout=10: (
            "<html><body>" + ("fresh article body " * 40) + "</body></html>"
        ),
    )
    out = source_fetcher.fetch_article(url_a, cache_path=cache.name, now=now)
    # malformed entry falls through to a successful re-fetch (mock body is valid)
    assert out and "fresh article body" in out

    # entry value is a bare string instead of a dict → entry["expires_at"] raises TypeError
    cache2 = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    cache2.close()
    url_b = "https://example.com/malformed-b"
    key_b = source_fetcher._key(url_b)
    with open(cache2.name, "w", encoding="utf-8") as fh:
        json.dump({key_b: "not-a-dict"}, fh)
    out2 = source_fetcher.fetch_article(url_b, cache_path=cache2.name, now=now)
    assert out2 and "fresh article body" in out2


def test_successful_fetch_writes_back(monkeypatch):
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    ttl_days = 7
    url = "https://example.com/writeback"
    key = source_fetcher._key(url)
    monkeypatch.setattr(
        source_fetcher,
        "_http_get",
        lambda u, timeout=10: (
            "<html><body>" + ("brand new article body " * 40) + "</body></html>"
        ),
    )
    out = source_fetcher.fetch_article(
        url, cache_path=cache.name, ttl_days=ttl_days, now=now
    )
    assert out and "brand new article body" in out
    with open(cache.name, encoding="utf-8") as fh:
        data = json.load(fh)
    assert key in data
    entry = data[key]
    assert "text" in entry and "brand new article body" in entry["text"]
    assert datetime.fromisoformat(entry["expires_at"]) == now + timedelta(days=ttl_days)


@pytest.mark.parametrize(
    "entry",
    [
        pytest.param({"text": "STALE"}, id="expires_at-absent"),
        pytest.param({"text": "STALE", "expires_at": None}, id="expires_at-none"),
        pytest.param({"text": "STALE", "expires_at": 1763300000}, id="expires_at-int"),
        pytest.param(
            {"text": "STALE", "expires_at": ["2026-07-20"]}, id="expires_at-list"
        ),
        pytest.param(
            {"text": "STALE", "expires_at": "not-a-date"}, id="expires_at-junk"
        ),
    ],
)
def test_every_unusable_expires_at_falls_through_to_refetch(
    entry, monkeypatch, tmp_path
):
    """No shape of a bad expires_at may serve the stale text or raise.

    fetch_article narrows expires_at with isinstance(str) before parsing it;
    unparseable strings still fall through via the ValueError handler. Both
    routes must reach the same place: a re-fetch, never a raise, and never the
    cached text.
    """
    cache_path = tmp_path / "cache.json"
    now = datetime(2026, 7, 16, 12, 0, 0)
    url = "https://example.com/expires-shapes"
    cache_path.write_text(
        json.dumps({source_fetcher._key(url): entry}), encoding="utf-8"
    )
    monkeypatch.setattr(
        source_fetcher,
        "_http_get",
        lambda u, timeout=10: (
            "<html><body>" + ("fresh article body " * 40) + "</body></html>"
        ),
    )
    out = source_fetcher.fetch_article(url, cache_path=str(cache_path), now=now)
    assert out and "fresh article body" in out
    assert "STALE" not in out


def test_valid_expires_at_string_still_serves_the_cache(monkeypatch, tmp_path):
    """Control: a well-formed, unexpired expires_at is still a cache hit.

    Without this, a guard that rejected *every* expires_at would pass the
    test above and silently disable the cache.
    """
    cache_path = tmp_path / "cache.json"
    now = datetime(2026, 7, 16, 12, 0, 0)
    url = "https://example.com/expires-valid"
    cache_path.write_text(
        json.dumps(
            {
                source_fetcher._key(url): {
                    "text": "CACHED ARTICLE TEXT " * 20,
                    "expires_at": (now + timedelta(days=3)).isoformat(),
                }
            }
        ),
        encoding="utf-8",
    )

    def fail(*a, **k):
        raise AssertionError("cache hit must not fetch")

    monkeypatch.setattr(source_fetcher, "_http_get", fail)
    out = source_fetcher.fetch_article(url, cache_path=str(cache_path), now=now)
    assert out and out.startswith("CACHED ARTICLE TEXT")
