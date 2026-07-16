import sys, os, json, tempfile
from datetime import datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "news"))
import source_fetcher


def test_fetch_failure_returns_none(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("network down")
    monkeypatch.setattr(source_fetcher, "_http_get", boom)
    assert source_fetcher.fetch_article("https://example.com/a", cache_path=None) is None


def test_short_body_treated_as_failure(monkeypatch):
    monkeypatch.setattr(source_fetcher, "_http_get", lambda url, timeout=10: "<html><body>x</body></html>")
    assert source_fetcher.fetch_article("https://example.com/a", cache_path=None) is None


def test_cache_hit_skips_fetch(monkeypatch):
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    key = source_fetcher._key("https://example.com/a")
    with open(cache.name, "w", encoding="utf-8") as fh:
        json.dump({key: {"text": "CACHED ARTICLE TEXT " * 20,
                         "expires_at": (now + timedelta(days=3)).isoformat()}}, fh)
    def fail(*a, **k):
        raise AssertionError("should not fetch on cache hit")
    monkeypatch.setattr(source_fetcher, "_http_get", fail)
    out = source_fetcher.fetch_article("https://example.com/a", cache_path=cache.name, now=now)
    assert out and out.startswith("CACHED ARTICLE TEXT")


def test_expired_cache_refetches(monkeypatch):
    cache = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); cache.close()
    now = datetime(2026, 7, 16, 12, 0, 0)
    key = source_fetcher._key("https://example.com/a")
    with open(cache.name, "w", encoding="utf-8") as fh:
        json.dump({key: {"text": "OLD", "expires_at": (now - timedelta(days=1)).isoformat()}}, fh)
    monkeypatch.setattr(source_fetcher, "_http_get",
                        lambda url, timeout=10: "<html><body>" + ("fresh article body " * 40) + "</body></html>")
    out = source_fetcher.fetch_article("https://example.com/a", cache_path=cache.name, now=now)
    assert out and "fresh article body" in out
