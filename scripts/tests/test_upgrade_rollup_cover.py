#!/usr/bin/env python3
"""Tests for ``scripts/upgrade_rollup_cover.py`` and
``scripts/lib/svg_rollup_generator.py``.

Coverage scope:
- ``load_spec``: schema validation, kind/severity/count guards, source enum.
- ``render``: byte-stability, XML escaping (ampersand, lt, gt, quote).
- ``write`` / ``check``: no-drift and drift detection lifecycle.
- ``_gather_specs``: --since filter on real SPECS_DIR contents.
- Day-cell count assertions for weekly_rollup (7) and monthly_index (9).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pytest
import yaml

from scripts.upgrade_rollup_cover import (
    SPECS_DIR,
    Spec,
    _gather_specs,
    check,
    load_spec,
    main,
    render,
    write,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_weekly(n_days: int = 7, **overrides) -> dict:
    """Return a minimal but valid weekly_rollup spec dict."""
    days = [
        {"date": f"4/{i + 6}", "severity": "HIGH", "tag": f"Day {i}"}
        for i in range(n_days)
    ]
    spec = {
        "date": "2026-04-12",
        "slug": "Test_Weekly_Rollup",
        "kind": "weekly_rollup",
        "period_label": "April 6-12, 2026",
        "period_short": "W2 APR",
        "daily_count": n_days,
        "daily_count_source": "redirect_from",
        "sfx": "TST1",
        "title": "Test Weekly Title",
        "aria": "Test weekly rollup aria",
        "top_highlights": [
            {"severity": "HIGH",   "label": "APT",    "headline": "Headline A", "source": "SrcA"},
            {"severity": "HIGH",   "label": "BOT",    "headline": "Headline B", "source": "SrcB"},
            {"severity": "MEDIUM", "label": "SUPPLY", "headline": "Headline C", "source": "SrcC"},
        ],
        "days": days,
        "footer": {"daily_digests": n_days, "categories": ["security"]},
    }
    spec.update(overrides)
    return spec


def _minimal_monthly(n_days: int = 9, **overrides) -> dict:
    """Return a minimal but valid monthly_index spec dict."""
    days = [
        {"date": f"1/{i + 23}", "severity": "HIGH", "tag": f"Day {i}"}
        for i in range(n_days)
    ]
    spec = {
        "date": "2026-01-31",
        "slug": "January_2026_Monthly_Index",
        "kind": "monthly_index",
        "period_label": "January 2026",
        "period_short": "JAN 2026",
        "daily_count": n_days,
        "daily_count_source": "index_table",
        "sfx": "JN31",
        "title": "Test Monthly Title",
        "aria": "Test monthly index aria",
        "top_highlights": [
            {"severity": "HIGH",   "label": "SOC ENG", "headline": "Headline X", "source": "SrcX"},
            {"severity": "HIGH",   "label": "ZERO DAY","headline": "Headline Y", "source": "SrcY"},
            {"severity": "MEDIUM", "label": "AI INFRA","headline": "Headline Z", "source": "SrcZ"},
        ],
        "days": days,
        "footer": {"daily_digests": n_days, "categories": ["security"]},
    }
    spec.update(overrides)
    return spec


def _write_spec(tmp_path: Path, data: dict, name: str = "sample.yml") -> Path:
    p = tmp_path / name
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# 1. Load valid real specs
# ---------------------------------------------------------------------------

class TestLoadRealSpecs:
    def test_load_valid_weekly_rollup_spec(self):
        spec_path = SPECS_DIR / "2026-04-12.yml"
        spec = load_spec(spec_path)
        assert spec.kind == "weekly_rollup"
        assert spec.daily_count == 7
        assert len(spec.days) == 7
        assert len(spec.top_highlights) == 3

    def test_load_valid_monthly_index_spec(self):
        spec_path = SPECS_DIR / "2026-01-31.yml"
        spec = load_spec(spec_path)
        assert spec.kind == "monthly_index"
        assert spec.daily_count == 9
        assert spec.daily_count_source == "index_table"


# ---------------------------------------------------------------------------
# 2. Schema validation — negative tests (inline synth dicts)
# ---------------------------------------------------------------------------

class TestLoadSpecValidation:
    def test_load_rejects_unknown_kind(self, tmp_path):
        data = _minimal_weekly()
        data["kind"] = "invalid"
        with pytest.raises(ValueError, match="kind must be"):
            load_spec(_write_spec(tmp_path, data))

    def test_load_rejects_bad_severity(self, tmp_path):
        data = _minimal_weekly()
        data["top_highlights"][0]["severity"] = "SUPER_HIGH"
        with pytest.raises(ValueError, match="severity must be"):
            load_spec(_write_spec(tmp_path, data))

    def test_load_rejects_weekly_rollup_with_4_days(self, tmp_path):
        data = _minimal_weekly(n_days=4)
        with pytest.raises(ValueError, match="weekly_rollup requires 5"):
            load_spec(_write_spec(tmp_path, data))

    def test_load_rejects_monthly_index_with_2_days(self, tmp_path):
        data = _minimal_monthly(n_days=2)
        with pytest.raises(ValueError, match="monthly_index requires 4"):
            load_spec(_write_spec(tmp_path, data))

    def test_load_accepts_monthly_index_with_9_days(self, tmp_path):
        """Jan W4-only edge case (9 days) must be accepted without error."""
        data = _minimal_monthly(n_days=9)
        spec = load_spec(_write_spec(tmp_path, data))
        assert len(spec.days) == 9

    def test_load_rejects_unknown_daily_count_source(self, tmp_path):
        data = _minimal_weekly()
        data["daily_count_source"] = "magic"
        with pytest.raises(ValueError, match="daily_count_source must be"):
            load_spec(_write_spec(tmp_path, data))


# ---------------------------------------------------------------------------
# 3. render() — byte stability + XML escaping
# ---------------------------------------------------------------------------

class TestRender:
    def test_render_byte_stable(self, tmp_path):
        """Same spec rendered twice must produce byte-identical output."""
        spec = load_spec(_write_spec(tmp_path, _minimal_weekly()))
        svg_a = render(spec)
        svg_b = render(spec)
        assert svg_a == svg_b

    def test_render_xml_escapes_ampersand(self, tmp_path):
        """Critical regression: AT&T in headline must become AT&amp;T in SVG.

        This guards against the 2026-01-26 drift cycle where unescaped
        ampersands corrupted SVG output.
        """
        data = _minimal_weekly()
        data["top_highlights"][0]["headline"] = "AT&T breach"
        spec = load_spec(_write_spec(tmp_path, data))
        svg = render(spec)
        assert "AT&amp;T" in svg
        # Raw ampersand must NOT appear inside element text (only &amp; is valid).
        # The only raw & allowed is at the start of escape sequences.
        assert "AT&T" not in svg

    def test_render_xml_escapes_lt_gt_quote(self, tmp_path):
        """<, >, and \" in text fields must be XML-escaped in the SVG."""
        data = _minimal_weekly()
        data["top_highlights"][1]["headline"] = '<script>alert("xss")</script>'
        spec = load_spec(_write_spec(tmp_path, data))
        svg = render(spec)
        assert "&lt;script&gt;" in svg
        assert "<script>" not in svg

    def test_render_weekly_produces_well_formed_svg(self, tmp_path):
        spec = load_spec(_write_spec(tmp_path, _minimal_weekly()))
        svg = render(spec)
        assert svg.strip().startswith("<svg")
        assert 'viewBox="0 0 1200 630"' in svg
        assert "</svg>" in svg

    def test_render_weekly_rollup_produces_7_day_cells(self, tmp_path):
        """weekly_rollup with 7 days must render exactly 7 day cells.

        Day cells are ``<g transform="translate(x,350)">`` where 350 = strip_y + 30.
        """
        data = _minimal_weekly(n_days=7)
        spec = load_spec(_write_spec(tmp_path, data))
        svg = render(spec)
        cells = re.findall(r'translate\([\d.]+,350\)', svg)
        assert len(cells) == 7

    def test_render_monthly_index_january_produces_9_day_cells(self, tmp_path):
        """monthly_index with 9 days (Jan W4-only) must render exactly 9 day cells."""
        data = _minimal_monthly(n_days=9)
        spec = load_spec(_write_spec(tmp_path, data))
        svg = render(spec)
        cells = re.findall(r'translate\([\d.]+,350\)', svg)
        assert len(cells) == 9


# ---------------------------------------------------------------------------
# 4. write() / check() lifecycle
# ---------------------------------------------------------------------------

class TestWriteAndCheck:
    def test_check_no_drift(self, tmp_path, monkeypatch):
        """After writing a spec, check() must return None (no drift)."""
        from scripts import upgrade_rollup_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)

        spec = load_spec(_write_spec(tmp_path, _minimal_weekly()))
        size = write(spec)
        assert size > 0
        assert spec.output_path.exists()
        assert check(spec) is None

    def test_check_detects_drift(self, tmp_path, monkeypatch):
        """Mutating the on-disk SVG after writing must be detected by check()."""
        from scripts import upgrade_rollup_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)

        spec = load_spec(_write_spec(tmp_path, _minimal_weekly()))
        write(spec)
        spec.output_path.write_text("<svg>tampered</svg>", encoding="utf-8")
        result = check(spec)
        assert result is not None
        assert "DRIFT" in result

    def test_check_reports_missing_file(self, tmp_path, monkeypatch):
        """check() on a spec with no on-disk file must report a DRIFT."""
        from scripts import upgrade_rollup_cover as mod
        monkeypatch.setattr(mod, "ASSETS", tmp_path)

        spec = load_spec(_write_spec(tmp_path, _minimal_weekly()))
        result = check(spec)
        assert result is not None
        assert "does not exist" in result


# ---------------------------------------------------------------------------
# 5. _gather_specs — --since filter
# ---------------------------------------------------------------------------

class TestGatherSpecs:
    def test_gather_specs_since_filter(self):
        """--since 2026-04-12 on the real SPECS_DIR must return exactly
        2026-04-12 and 2026-04-19 (stems >= '2026-04-12').
        """
        args = argparse.Namespace(spec=None, all=True, since="2026-04-12")
        paths = _gather_specs(args)
        stems = [p.stem for p in paths]
        assert "2026-04-12" in stems
        assert "2026-04-19" in stems
        # Older files must be excluded.
        assert "2026-01-31" not in stems
        assert "2026-02-28" not in stems
        assert "2026-04-05" not in stems
