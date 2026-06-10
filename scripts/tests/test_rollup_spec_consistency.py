#!/usr/bin/env python3
"""Tests for scripts/check_rollup_spec_consistency.py (rollup spec↔post gate).

Verifies the deterministic accuracy rules pass all 6 real specs (no false
positives) and catch genuine drift (out-of-period day, weekly daily_count >
redirect_from), while NOT applying the weekly daily_count rule to monthly_index
(whose daily_count is a month aggregate far exceeding its redirect_from).
"""

import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.check_rollup_spec_consistency import (  # noqa: E402
    ROLLUP_COVERS_DIR,
    _day_in_period,
    _period_bounds,
    _redirect_from_count,
    check_spec,
)


class TestPeriodParsing:
    def test_date_range_label(self):
        assert _period_bounds("April 13-19, 2026") == (4, 13, 4, 19)

    def test_whole_month_label(self):
        # January 2026 -> full month span (1..31)
        assert _period_bounds("January 2026") == (1, 1, 1, 31)

    def test_unparseable(self):
        assert _period_bounds("sometime soon") is None


class TestDayInPeriod:
    def test_in_range(self):
        assert _day_in_period("4/15", (4, 13, 4, 19)) is True

    def test_out_of_range(self):
        assert _day_in_period("4/20", (4, 13, 4, 19)) is False

    def test_non_date_cell_skipped(self):
        # "Week 1" is a monthly_index label, not a date -> None (skip).
        assert _day_in_period("Week 1", (4, 1, 4, 30)) is None


class TestRealSpecsPass:
    def test_all_six_specs_clean(self):
        """All shipped rollup specs must pass — guards against false positives."""
        specs = sorted(ROLLUP_COVERS_DIR.glob("*.yml"))
        assert len(specs) >= 6
        for spec in specs:
            assert check_spec(spec) == [], f"{spec.name} unexpectedly flagged"


class TestCatchesDrift:
    def _write(self, tmp_path, data):
        p = tmp_path / "2026-04-19-Week3_April_2026_Security_Digest.yml"
        p.write_text(yaml.safe_dump(data), encoding="utf-8")
        return p

    def _base(self):
        return yaml.safe_load(
            (ROLLUP_COVERS_DIR / "2026-04-19.yml").read_text(encoding="utf-8")
        )

    def test_catches_out_of_period_day(self, tmp_path):
        data = self._base()
        data["days"].append({"date": "5/02", "severity": "HIGH", "tag": "x"})
        # write to the real dir name so owning-post resolves; use real slug/date
        v = check_spec(self._write_realname(tmp_path, data))
        assert any("outside period" in x for x in v)

    def test_catches_weekly_daily_count_over_redirect(self, tmp_path):
        data = self._base()
        data["daily_count"] = 99
        v = check_spec(self._write_realname(tmp_path, data))
        assert any("daily_count 99 > redirect_from" in x for x in v)

    def test_monthly_index_not_subject_to_daily_count_rule(self, tmp_path):
        # monthly_index daily_count legitimately exceeds redirect_from.
        data = self._base()
        data["kind"] = "monthly_index"
        data["daily_count"] = 99
        v = check_spec(self._write_realname(tmp_path, data))
        assert not any("daily_count" in x for x in v)

    def _write_realname(self, tmp_path, data):
        # owning post is resolved from data['date']+data['slug'], so the temp
        # file name doesn't matter — only the YAML content does.
        p = tmp_path / "spec.yml"
        p.write_text(yaml.safe_dump(data), encoding="utf-8")
        return p


class TestRedirectCount:
    def test_counts_redirect_entries(self):
        post = Path(__file__).parent.parent.parent / "_posts" / "2026-04-19-Week3_April_2026_Security_Digest.md"
        # The 2026-04-19 owning post has 9 redirect_from entries (verified).
        assert _redirect_from_count(post) >= 7
