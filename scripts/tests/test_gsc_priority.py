"""Tests for scripts/gsc_priority.py.

All tests use synthetic state and history dictionaries. No external API
calls, no real history snapshots required.
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import gsc_priority as gp  # noqa: E402


# ---------------------------------------------------------------------------
# recency_score
# ---------------------------------------------------------------------------


def test_recency_score_zero_days_old_returns_max():
    today = date(2026, 5, 15)
    assert gp.recency_score(today, today) == pytest.approx(gp.RECENCY_MAX_PTS)


def test_recency_score_full_horizon_returns_zero():
    today = date(2026, 5, 15)
    past = date(2025, 5, 15)  # 365 days exactly
    assert gp.recency_score(past, today) == 0.0


def test_recency_score_ninety_days_returns_about_thirty():
    today = date(2026, 5, 15)
    past = date(2026, 2, 14)  # 90 days back
    # 40 * (1 - 90/365) = ~30.14
    assert gp.recency_score(past, today) == pytest.approx(30.14, abs=1.0)


def test_recency_score_unknown_date_is_zero():
    assert gp.recency_score(None, date(2026, 5, 15)) == 0.0


def test_recency_score_future_publish_clamped_to_today():
    today = date(2026, 5, 15)
    future = date(2026, 6, 1)
    assert gp.recency_score(future, today) == pytest.approx(gp.RECENCY_MAX_PTS)


# ---------------------------------------------------------------------------
# sitemap_age_score
# ---------------------------------------------------------------------------


def test_sitemap_age_zero_days_returns_zero():
    now = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)
    just_crawled = now.isoformat().replace("+00:00", "Z")
    assert gp.sitemap_age_score(just_crawled, now) == pytest.approx(0.0, abs=0.5)


def test_sitemap_age_past_horizon_caps_at_max():
    now = datetime(2026, 5, 15, tzinfo=timezone.utc)
    long_ago = datetime(2025, 1, 1, tzinfo=timezone.utc)  # 499 days
    assert gp.sitemap_age_score(long_ago.isoformat(), now) == gp.SITEMAP_AGE_MAX_PTS


def test_sitemap_age_thirty_five_days_returns_five():
    now = datetime(2026, 5, 15, tzinfo=timezone.utc)
    crawled = datetime(2026, 4, 10, tzinfo=timezone.utc)  # 35 days
    # 20 * 35/140 = 5
    assert gp.sitemap_age_score(crawled.isoformat(), now) == pytest.approx(5.0, abs=1.0)


def test_sitemap_age_no_crawl_data_returns_max():
    now = datetime(2026, 5, 15, tzinfo=timezone.utc)
    # Discovered-not-indexed URLs typically have null lastCrawlTime.
    assert gp.sitemap_age_score(None, now) == gp.SITEMAP_AGE_MAX_PTS


# ---------------------------------------------------------------------------
# stuck_penalty_score
# ---------------------------------------------------------------------------


def test_stuck_penalty_zero_when_not_stuck_state():
    # Even with prior history, "Submitted and indexed" should not be penalised.
    assert gp.stuck_penalty_score("Submitted and indexed", 5) == 0.0


def test_stuck_penalty_zero_when_no_history():
    assert gp.stuck_penalty_score("Discovered - currently not indexed", 0) == 0.0


def test_stuck_penalty_first_stuck_run_is_16():
    # base 15 + min(15, 1*1) = 16
    score = gp.stuck_penalty_score("Discovered - currently not indexed", 1)
    assert score == pytest.approx(16.0)


def test_stuck_penalty_caps_at_thirty():
    # base 15 + min(15, 30*1) = 30
    score = gp.stuck_penalty_score("Crawled - currently not indexed", 30)
    assert score == pytest.approx(30.0)


def test_stuck_penalty_recognises_alternate_phrasing():
    score = gp.stuck_penalty_score("Crawled, not indexed", 3)
    assert score == pytest.approx(18.0)


# ---------------------------------------------------------------------------
# build_stuck_counts (history walking)
# ---------------------------------------------------------------------------


def _stub_snapshot(urls_to_state):
    return {"urls": [{"url": u, "coverage_state": s} for u, s in urls_to_state.items()]}


def test_build_stuck_counts_consecutive_runs():
    today_state = _stub_snapshot({
        "https://x/post-a/": "Discovered - currently not indexed",
        "https://x/post-b/": "Submitted and indexed",
    })
    history = [
        # oldest first
        _stub_snapshot({"https://x/post-a/": "Discovered - currently not indexed"}),
        _stub_snapshot({"https://x/post-a/": "Discovered - currently not indexed"}),
        _stub_snapshot({"https://x/post-a/": "Crawled - currently not indexed"}),
    ]
    counts = gp.build_stuck_counts(history, today_state)
    # 3 consecutive stuck snapshots before today
    assert counts == {"https://x/post-a/": 3}


def test_build_stuck_counts_breaks_streak_on_indexed():
    today_state = _stub_snapshot({
        "https://x/post-a/": "Discovered - currently not indexed",
    })
    history = [
        # Oldest: indexed (should NOT count)
        _stub_snapshot({"https://x/post-a/": "Submitted and indexed"}),
        # Newer: stuck (counts)
        _stub_snapshot({"https://x/post-a/": "Discovered - currently not indexed"}),
        _stub_snapshot({"https://x/post-a/": "Discovered - currently not indexed"}),
    ]
    counts = gp.build_stuck_counts(history, today_state)
    # Walking backward: 2 stuck consecutive, then indexed breaks the streak.
    assert counts == {"https://x/post-a/": 2}


# ---------------------------------------------------------------------------
# Integration: rank_entries + render_report
# ---------------------------------------------------------------------------


@pytest.fixture
def synthetic_state():
    return {
        "schema_version": 1,
        "generated_at": "2026-05-15T07:30:00Z",
        "site_url": "https://tech.2twodragon.com",
        "totals": {"inspected": 5, "indexed": 1, "discovered_not_indexed": 2,
                   "crawled_not_indexed": 1, "errors": 1},
        "urls": [
            {
                "url": "https://tech.2twodragon.com/security/2026-05-14-fresh-stuck/",
                "inspected_at": "2026-05-15T07:30:01Z",
                "verdict": "NEUTRAL",
                "coverage_state": "Discovered - currently not indexed",
                "indexing_state": "INDEXING_ALLOWED",
                "last_crawl_time": None,
            },
            {
                "url": "https://tech.2twodragon.com/cloud/2025-08-01-old-indexed/",
                "inspected_at": "2026-05-15T07:30:02Z",
                "verdict": "PASS",
                "coverage_state": "Submitted and indexed",
                "indexing_state": "INDEXING_ALLOWED",
                "last_crawl_time": "2026-05-14T12:00:00Z",
            },
            {
                "url": "https://tech.2twodragon.com/devops/2026-04-01-mid-stuck/",
                "inspected_at": "2026-05-15T07:30:03Z",
                "verdict": "NEUTRAL",
                "coverage_state": "Crawled - currently not indexed",
                "indexing_state": "INDEXING_ALLOWED",
                "last_crawl_time": "2026-01-01T00:00:00Z",
            },
            {
                "url": "https://tech.2twodragon.com/finops/2024-01-15-ancient/",
                "inspected_at": "2026-05-15T07:30:04Z",
                "verdict": "PASS",
                "coverage_state": "Submitted and indexed",
                "indexing_state": "INDEXING_ALLOWED",
                "last_crawl_time": "2025-12-01T00:00:00Z",
            },
            {
                "url": "https://tech.2twodragon.com/x/2026-05-10-errored/",
                "inspected_at": "2026-05-15T07:30:05Z",
                "error": "HttpError 429 Too Many Requests",
            },
        ],
    }


def test_rank_entries_top_url_is_fresh_stuck_with_history(synthetic_state):
    history = [
        _stub_snapshot({
            "https://tech.2twodragon.com/security/2026-05-14-fresh-stuck/":
                "Discovered - currently not indexed",
        }),
        _stub_snapshot({
            "https://tech.2twodragon.com/security/2026-05-14-fresh-stuck/":
                "Discovered - currently not indexed",
        }),
    ]
    today = date(2026, 5, 15)
    now = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)
    ranked = gp.rank_entries(synthetic_state, history, today=today, now=now)

    # 5 input rows in / 5 ranked rows out.
    assert len(ranked) == 5
    # Fresh + stuck + 2 prior runs = highest score.
    top_url = ranked[0]["url"]
    assert "2026-05-14-fresh-stuck" in top_url
    assert ranked[0]["stuck_count"] == 2
    # Indexed-old should NOT be #1
    assert "old-indexed" not in top_url


def test_rank_entries_no_history_still_works(synthetic_state):
    today = date(2026, 5, 15)
    now = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)
    ranked = gp.rank_entries(synthetic_state, history=[], today=today, now=now)
    assert all(row["stuck_count"] == 0 for row in ranked)
    # Without history, top-1 is whichever stuck URL has best recency.
    assert ranked[0]["coverage_state"].lower().startswith(("discovered", "crawled"))


def test_render_report_has_required_sections(synthetic_state):
    today = date(2026, 5, 15)
    now = datetime(2026, 5, 15, 12, 0, tzinfo=timezone.utc)
    ranked = gp.rank_entries(synthetic_state, history=[], today=today, now=now)
    report = gp.render_report(synthetic_state, ranked, today, top_n=3)

    assert "# GSC Daily Action Report — 2026-05-15" in report
    assert "## Coverage state distribution" in report
    assert "## Top 3 priority URLs" in report
    assert "## Suggested actions" in report
    assert "## Full ranked list" in report
    assert "## Priority-score formula" in report
    # Top-N respects argument
    assert report.count("| 1 |") >= 1  # at least one row #1 (top table + full)
    # All 5 URLs appear in the full ranked list
    for entry in synthetic_state["urls"]:
        assert entry["url"] in report


# ---------------------------------------------------------------------------
# Safety: missing state, missing history, edge inputs
# ---------------------------------------------------------------------------


def test_load_state_missing_returns_none(tmp_path, capsys):
    result = gp.load_state(tmp_path / "absent.json")
    assert result is None
    assert "state file not found" in capsys.readouterr().err


def test_load_history_missing_dir_returns_empty(tmp_path):
    assert gp.load_history(tmp_path / "absent-dir") == []


def test_load_history_skips_bad_file(tmp_path, capsys):
    (tmp_path / "good.json").write_text(json.dumps({"urls": []}), encoding="utf-8")
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    history = gp.load_history(tmp_path)
    assert len(history) == 1
    assert "skip history file" in capsys.readouterr().err


def test_main_dry_run_prints_report(tmp_path, capsys, synthetic_state):
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps(synthetic_state), encoding="utf-8")
    rc = gp.main([
        "--state", str(state_path),
        "--history-dir", str(tmp_path / "history"),  # missing, ok
        "--dry-run",
        "--top-n", "2",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "GSC Daily Action Report" in out
    assert "Top 2 priority URLs" in out


def test_main_missing_state_exits_zero_with_warning(tmp_path, capsys):
    rc = gp.main([
        "--state", str(tmp_path / "missing.json"),
        "--history-dir", str(tmp_path / "history"),
        "--dry-run",
    ])
    assert rc == 0
    assert "state file not found" in capsys.readouterr().err


def test_infer_publish_date_from_url():
    assert gp.infer_publish_date_from_url(
        "https://tech.2twodragon.com/security/2026-05-14-foo/"
    ) == date(2026, 5, 14)
    assert gp.infer_publish_date_from_url(None) is None
    assert gp.infer_publish_date_from_url(
        "https://tech.2twodragon.com/no-date-here/"
    ) is None
