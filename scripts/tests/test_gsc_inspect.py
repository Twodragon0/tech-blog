"""Tests for scripts/gsc_inspect.py.

All Google API calls are mocked. The google-api-python-client and google-auth
libraries are NOT required for these tests — `build_search_console_client` is
the only entry point that imports them, and we never invoke it directly.

Covered:
1. parse_sitemap_urls — handles namespaced sitemap correctly
2. parse_sitemap_urls — returns [] on parse error
3. _extract_index_status — pulls fields, tolerates missing keys
4. categorise — buckets coverage_state strings
5. inspect_url — retries on 429 then succeeds
6. inspect_url — gives up after MAX_RETRIES
7. run_inspection — aggregates totals correctly
8. run_inspection — per-URL exception logged, run continues
9. main() — exits non-zero with missing service-account env
10. load_service_account_info — raw JSON vs path handling
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import gsc_inspect as gsc  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://tech.2twodragon.com/post-a/</loc></url>
  <url><loc>https://tech.2twodragon.com/post-b/</loc></url>
  <url><loc>https://tech.2twodragon.com/post-c/</loc></url>
</urlset>
"""


def _make_inspection_response(coverage_state: str = "Submitted and indexed"):
    return {
        "inspectionResult": {
            "indexStatusResult": {
                "verdict": "PASS",
                "coverageState": coverage_state,
                "indexingState": "INDEXING_ALLOWED",
                "lastCrawlTime": "2026-05-15T10:00:00Z",
                "robotsTxtState": "ALLOWED",
                "pageFetchState": "SUCCESSFUL",
                "googleCanonical": "https://example.com/x/",
                "userCanonical": "https://example.com/x/",
            }
        }
    }


class _FakeStatus:
    def __init__(self, status: int) -> None:
        self.status = status


class _FakeHttpError(Exception):
    """Mimics googleapiclient.errors.HttpError just enough for retry tests."""

    def __init__(self, status: int) -> None:
        super().__init__(f"HTTP {status}")
        self.resp = _FakeStatus(status)


def _stub_client(responses):
    """Build a MagicMock that returns/raises from `responses` on each call.

    Each element of `responses` is either:
        - a dict → returned by .execute()
        - an exception → raised by .execute()
    """
    call_idx = {"n": 0}

    def execute_side_effect():
        idx = call_idx["n"]
        call_idx["n"] += 1
        value = responses[idx]
        if isinstance(value, Exception):
            raise value
        return value

    client = MagicMock()
    client.urlInspection.return_value.index.return_value.inspect.return_value.execute.side_effect = (  # noqa: E501
        execute_side_effect
    )
    return client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_parse_sitemap_urls_namespaced():
    urls = gsc.parse_sitemap_urls(SITEMAP_XML)
    assert urls == [
        "https://tech.2twodragon.com/post-a/",
        "https://tech.2twodragon.com/post-b/",
        "https://tech.2twodragon.com/post-c/",
    ]


def test_parse_sitemap_urls_returns_empty_on_bad_xml(capsys):
    result = gsc.parse_sitemap_urls("not xml at all <<<")
    assert result == []
    assert "sitemap parse failed" in capsys.readouterr().err


def test_extract_index_status_handles_missing_fields():
    extracted = gsc._extract_index_status({})
    assert extracted["verdict"] is None
    assert extracted["coverage_state"] is None
    assert "indexing_state" in extracted

    extracted = gsc._extract_index_status(
        {"indexStatusResult": {"verdict": "PASS", "coverageState": "Submitted and indexed"}}
    )
    assert extracted["verdict"] == "PASS"
    assert extracted["coverage_state"] == "Submitted and indexed"


@pytest.mark.parametrize(
    "state,expected",
    [
        ("Submitted and indexed", "indexed"),
        ("Indexed, not submitted in sitemap", "indexed"),
        ("Discovered - currently not indexed", "discovered"),
        ("Crawled - currently not indexed", "crawled"),
        ("Excluded by 'noindex' tag", "other"),
        (None, "other"),
        ("", "other"),
    ],
)
def test_categorise(state, expected):
    assert gsc.categorise(state) == expected


def test_inspect_url_retries_on_429_then_succeeds():
    client = _stub_client(
        [
            _FakeHttpError(429),
            _FakeHttpError(429),
            _make_inspection_response("Submitted and indexed"),
        ]
    )
    with patch.object(gsc.time, "sleep") as sleep_mock:
        result = gsc.inspect_url(client, "https://example.com/a/", "https://example.com")
    assert result["indexStatusResult"]["verdict"] == "PASS"
    # 2 retries → 2 sleep calls
    assert sleep_mock.call_count == 2


def test_inspect_url_gives_up_after_max_retries():
    client = _stub_client([_FakeHttpError(429)] * gsc.MAX_RETRIES)
    with patch.object(gsc.time, "sleep"):
        with pytest.raises(_FakeHttpError):
            gsc.inspect_url(client, "https://example.com/b/", "https://example.com")


def test_run_inspection_aggregates_totals():
    responses = [
        _make_inspection_response("Submitted and indexed"),
        _make_inspection_response("Discovered - currently not indexed"),
        _make_inspection_response("Crawled - currently not indexed"),
    ]
    client = _stub_client(responses)
    urls = [f"https://example.com/{i}/" for i in range(3)]

    state = gsc.run_inspection(
        urls=urls, client=client, site_url="https://example.com",
        daily_budget=100, per_request_sleep=0,
    )

    assert state["schema_version"] == 1
    assert state["totals"] == {
        "inspected": 3, "indexed": 1, "discovered_not_indexed": 1,
        "crawled_not_indexed": 1, "errors": 0,
    }
    assert len(state["urls"]) == 3
    assert all("inspected_at" in entry for entry in state["urls"])


def test_run_inspection_per_url_failure_continues(capsys):
    responses = [
        _make_inspection_response("Submitted and indexed"),
        RuntimeError("transient inspector failure"),
        _make_inspection_response("Submitted and indexed"),
    ]
    client = _stub_client(responses)
    urls = [f"https://example.com/{i}/" for i in range(3)]

    state = gsc.run_inspection(
        urls=urls, client=client, site_url="https://example.com",
        daily_budget=100, per_request_sleep=0,
    )

    assert state["totals"]["inspected"] == 2
    assert state["totals"]["indexed"] == 2
    assert state["totals"]["errors"] == 1
    assert state["urls"][1].get("error", "").startswith("transient inspector failure")
    assert "ERROR inspecting" in capsys.readouterr().err


def test_main_missing_service_account_exits_nonzero(monkeypatch, capsys):
    monkeypatch.delenv("GSC_SERVICE_ACCOUNT_JSON", raising=False)
    rc = gsc.main(["--limit", "1"])
    assert rc == 1
    err = capsys.readouterr().err
    assert "GSC_SERVICE_ACCOUNT_JSON" in err
    assert "docs/seo/GSC_RECRAWL_SETUP.md" in err


def test_load_service_account_info_raw_json_and_path(tmp_path):
    sa_dict = {"type": "service_account", "client_email": "x@y.iam"}
    raw = json.dumps(sa_dict)
    assert gsc.load_service_account_info(raw) == sa_dict

    key_file = tmp_path / "key.json"
    key_file.write_text(raw, encoding="utf-8")
    assert gsc.load_service_account_info(str(key_file)) == sa_dict

    with pytest.raises(ValueError):
        gsc.load_service_account_info("   ")

    with pytest.raises(FileNotFoundError):
        gsc.load_service_account_info(str(tmp_path / "missing.json"))


def test_write_state_creates_parent_and_round_trips(tmp_path):
    target = tmp_path / "nested" / "state.json"
    payload = {"schema_version": 1, "totals": {"inspected": 5}}
    gsc.write_state(target, payload)
    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == payload
