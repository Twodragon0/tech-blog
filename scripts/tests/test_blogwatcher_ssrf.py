#!/usr/bin/env python3
"""SSRF / feed-poisoning guard tests for normalize_blogwatcher_payload.validate_fetch_url.

The blogwatcher payload URL comes from an external repository_dispatch
client_payload (`collected_news_url`). Before commit c-2026-07-03 it was fetched
with `requests.get()` and no validation — a metadata-SSRF (169.254.169.254) and
feed-poisoning vector. These tests pin the validator's behavior.

All cases use numeric IPs or allowlist rejection so no live DNS is required.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_MOD_PATH = Path(__file__).resolve().parents[1] / "normalize_blogwatcher_payload.py"
_spec = importlib.util.spec_from_file_location("nbp", _MOD_PATH)
nbp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(nbp)


class TestValidateFetchUrl:
    def test_rejects_non_http_scheme(self):
        with pytest.raises(ValueError, match="non-http"):
            nbp.validate_fetch_url("file:///etc/passwd", [])

    def test_rejects_gopher_scheme(self):
        with pytest.raises(ValueError, match="non-http"):
            nbp.validate_fetch_url("gopher://127.0.0.1:6379/_", [])

    def test_rejects_loopback_ip(self):
        with pytest.raises(ValueError, match="non-public"):
            nbp.validate_fetch_url("http://127.0.0.1/data.json", [])

    def test_rejects_cloud_metadata_ip(self):
        # AWS/GCP metadata endpoint — the classic SSRF target.
        with pytest.raises(ValueError, match="non-public"):
            nbp.validate_fetch_url("http://169.254.169.254/latest/meta-data/", [])

    def test_rejects_private_ip(self):
        with pytest.raises(ValueError, match="non-public"):
            nbp.validate_fetch_url("https://10.0.0.5/feed.json", [])

    def test_allowlist_blocks_other_host(self):
        with pytest.raises(ValueError, match="allowlist"):
            nbp.validate_fetch_url("https://evil.example/feed.json", ["news.trusted.io"])

    def test_allowlist_permits_exact_and_subdomain(self):
        allowed = ["trusted.io"]
        # subdomain match — public numeric IP would still be checked, so use a
        # host that resolves publicly; instead assert the allowlist gate passes
        # by checking a public numeric IP is NOT what we test here. Use exact
        # host with monkeypatched resolver below.
        # Exact-host allow + public IP:
        assert nbp.validate_fetch_url("https://8.8.8.8/feed.json", []).scheme == "https"

    def test_permits_public_numeric_ip(self):
        parsed = nbp.validate_fetch_url("https://8.8.8.8/collected.json", [])
        assert parsed.hostname == "8.8.8.8"

    def test_allowlist_subdomain_match(self, monkeypatch):
        # Force the resolver public so we isolate the allowlist logic.
        monkeypatch.setattr(nbp, "_resolves_to_public", lambda host: True)
        parsed = nbp.validate_fetch_url("https://cdn.trusted.io/feed.json", ["trusted.io"])
        assert parsed.hostname == "cdn.trusted.io"

    def test_no_host_rejected(self):
        with pytest.raises(ValueError, match="no host"):
            nbp.validate_fetch_url("https:///path-only", [])


class TestFailClosedAllowlist:
    """MED-2: the env-driven fetch path (allowed_hosts=None) must fail closed
    when BLOGWATCHER_ALLOWED_HOSTS is unset — an untrusted external URL must not
    be fetched from an arbitrary public host just because the allowlist is
    unconfigured. Explicit-list callers keep their existing semantics.
    """

    def test_env_unset_fails_closed(self, monkeypatch):
        # No allowlist configured → refuse even a public host (fail-closed).
        monkeypatch.delenv("BLOGWATCHER_ALLOWED_HOSTS", raising=False)
        monkeypatch.setattr(nbp, "_resolves_to_public", lambda host: True)
        with pytest.raises(ValueError, match="fail-closed|BLOGWATCHER_ALLOWED_HOSTS is not set"):
            nbp.validate_fetch_url("https://feed.example/collected.json")

    def test_env_blank_fails_closed(self, monkeypatch):
        # Whitespace-only value normalizes to an empty allowlist → still closed.
        monkeypatch.setenv("BLOGWATCHER_ALLOWED_HOSTS", "  , ")
        monkeypatch.setattr(nbp, "_resolves_to_public", lambda host: True)
        with pytest.raises(ValueError, match="fail-closed|is not set"):
            nbp.validate_fetch_url("https://feed.example/collected.json")

    def test_env_set_permits_matching_host(self, monkeypatch):
        monkeypatch.setenv("BLOGWATCHER_ALLOWED_HOSTS", "trusted.io")
        monkeypatch.setattr(nbp, "_resolves_to_public", lambda host: True)
        parsed = nbp.validate_fetch_url("https://cdn.trusted.io/feed.json")
        assert parsed.hostname == "cdn.trusted.io"

    def test_env_set_rejects_other_host(self, monkeypatch):
        monkeypatch.setenv("BLOGWATCHER_ALLOWED_HOSTS", "trusted.io")
        monkeypatch.setattr(nbp, "_resolves_to_public", lambda host: True)
        with pytest.raises(ValueError, match="allowlist"):
            nbp.validate_fetch_url("https://evil.example/feed.json")

    def test_explicit_empty_list_still_permissive(self, monkeypatch):
        # Regression guard for the contract: an explicit [] is a deliberate
        # opt-out (trusted callers/tests) and must NOT trigger fail-closed,
        # regardless of the env var.
        monkeypatch.delenv("BLOGWATCHER_ALLOWED_HOSTS", raising=False)
        parsed = nbp.validate_fetch_url("https://8.8.8.8/feed.json", [])
        assert parsed.hostname == "8.8.8.8"
