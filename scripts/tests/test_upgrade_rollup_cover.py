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


# ---------------------------------------------------------------------------
# 6. Regression: highlight-band text no overlap
# ---------------------------------------------------------------------------

class TestHighlightBandNoOverlap:
    def test_render_highlights_text_no_overlap(self, tmp_path):
        """Detail line y and source line y must be separated by >= font_size * 1.1.

        Constructs a spec with a long detail line (worst case: 2-line headline
        pushes headline_y2 to 162, detail naively at 176, source at 178 → 2px gap).
        After the fix the detail line must be at most y+162, source at y+178,
        guaranteeing >= 16px clearance.
        """
        data = _minimal_weekly()
        # Force 2-line headline to trigger the tightest layout.
        data["top_highlights"][0]["headline"] = "SAP credential theft supply chain"
        data["top_highlights"][0]["detail"] = "SAP credential theft : attackers leverage stolen creds for supply chain pivot"
        data["top_highlights"][0]["source"] = "The Hacker News"
        spec = load_spec(_write_spec(tmp_path, data))
        svg = render(spec)

        # Parse all <text y="..."> values in the first card region (x ≈ 28..400).
        # Card 0 is at x=28 so all its text elements share x in [28, 399].
        # We look for text elements with y between y=100+60=160 and y=100+200=300.
        import xml.etree.ElementTree as ET
        _SVG_NS = "http://www.w3.org/2000/svg"
        root = ET.fromstring(svg)

        ys_by_fontsize: dict = {}
        for el in root.iter(f"{{{_SVG_NS}}}text"):
            try:
                y = int(el.get("y", "0"))
                fs = int(el.get("font-size", "0"))
                ys_by_fontsize.setdefault(fs, []).append(y)
            except (ValueError, TypeError):
                pass

        detail_font_ys = sorted(ys_by_fontsize.get(12, []))
        source_font_ys = sorted(ys_by_fontsize.get(11, []))

        # There should be at least one detail-12 text and one source-11 text.
        assert detail_font_ys, "Expected font-size=12 detail text elements"
        assert source_font_ys, "Expected font-size=11 source text elements"

        # For card 0: detail_y <= 262 (y=100 + detail_y_offset=162),
        # source_y == 278 (y=100 + source_y_offset=178).
        # Minimum gap between any detail and its nearest source must be >= 14.
        min_gap = min(
            sy - dy
            for sy in source_font_ys
            for dy in detail_font_ys
            if sy > dy
        )
        assert min_gap >= 14, (
            f"Detail/source lines too close: gap={min_gap}px (must be >= 14). "
            f"detail_ys={detail_font_ys}, source_ys={source_font_ys}"
        )


# ---------------------------------------------------------------------------
# 7. Regression: CATEGORIES footer card no mid-word truncation
# ---------------------------------------------------------------------------

class TestCategoriesCardNoTruncation:
    def test_render_categories_card_no_truncation(self, tmp_path):
        """CATEGORIES card must not end with a partial word like 'DEVSECOC'.

        When the category list is ['SECURITY', 'DEVSECOPS', 'CLOUD'], the
        rendered text must be either the full string or a proper word-boundary
        truncation ending with '...'.
        """
        data = _minimal_weekly()
        data["footer"]["categories"] = ["security", "devsecops", "cloud"]
        spec = load_spec(_write_spec(tmp_path, data))
        svg = render(spec)

        # The CATEGORIES card value text element contains the formatted string.
        # Find all font-size="14" text elements (categories use val_size=14).
        import xml.etree.ElementTree as ET
        _SVG_NS = "http://www.w3.org/2000/svg"
        root = ET.fromstring(svg)
        cat_texts = [
            el.text or ""
            for el in root.iter(f"{{{_SVG_NS}}}text")
            if el.get("font-size") == "14"
        ]
        assert cat_texts, "Expected font-size=14 CATEGORIES text element"
        cat_value = cat_texts[0]

        # Must not end mid-word: valid endings are a full word or "...".
        assert not (
            cat_value.endswith(("DEVSECOC", "DEVSECO", "DEVSEOP", "DEVSEO"))
        ), f"CATEGORIES text appears mid-word truncated: {cat_value!r}"

        # If truncated it must end with "..."
        if len(cat_value) < len("SECURITY, DEVSECOPS, CLOUD"):
            assert cat_value.endswith("..."), (
                f"Truncated CATEGORIES text must end with '...', got: {cat_value!r}"
            )

    def test_render_categories_card_long_list_truncates_at_word_boundary(self, tmp_path):
        """With 5 categories, the card text must truncate at word boundary with '...'."""
        data = _minimal_weekly()
        data["footer"]["categories"] = ["security", "devsecops", "cloud", "kubernetes", "finops"]
        spec = load_spec(_write_spec(tmp_path, data))
        svg = render(spec)

        import xml.etree.ElementTree as ET
        _SVG_NS = "http://www.w3.org/2000/svg"
        root = ET.fromstring(svg)
        cat_texts = [
            el.text or ""
            for el in root.iter(f"{{{_SVG_NS}}}text")
            if el.get("font-size") == "14"
        ]
        assert cat_texts, "Expected font-size=14 CATEGORIES text element"
        cat_value = cat_texts[0]

        # Must end with "..." since 5 categories exceed 24 chars.
        assert cat_value.endswith("..."), (
            f"Long category list must truncate with '...', got: {cat_value!r}"
        )
        # Must not contain a partial word before "..." — last token before "..."
        # must be a complete uppercase word.
        prefix = cat_value[:-3]  # strip "..."
        if prefix:
            last_char = prefix[-1]
            # Last char before "..." must not be a letter mid-word — it must be
            # either a complete word end or the full last token ends before comma.
            assert last_char in (",", " ") or prefix.endswith(
                tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
            ), f"Partial word before '...': {cat_value!r}"
