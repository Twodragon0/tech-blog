"""Regression tests for scripts.lib.svg_l22_generator._fit_band_text.

User feedback (2026-05-22 session, commit 322a054f): May 2026 L22 covers
were shipping with 100-char detail lines that flowed past the visual
element at x=420 and across the mini-card at x=820+, hiding both the
tail of the text and the KPI digits. Cap was added inside band() to
prevent that overflow regression.

These tests pin the cap so a future contributor cannot quietly raise
the per-font-size character budget back into overflow territory.

API disabling and path setup are handled by conftest.py.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_module():
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "lib" / "svg_l22_generator.py"
    spec = importlib.util.spec_from_file_location("svg_l22_generator", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


l22 = _load_module()


class TestFitBandTextBudget:
    """Per-font-size character budget never raises silently above safe value."""

    def test_short_string_unchanged(self):
        assert l22._fit_band_text("Short text", 50) == "Short text"

    def test_exact_length_unchanged(self):
        s = "x" * 50
        assert l22._fit_band_text(s, 50) == s

    def test_long_string_gets_ellipsis(self):
        s = "x" * 100
        result = l22._fit_band_text(s, 50)
        assert result.endswith("..."), (
            f"Expected ellipsis-truncation on 100-char input with cap 50, "
            f"got: {result!r}"
        )
        assert len(result) <= 50 + 3  # cap + ellipsis suffix

    def test_long_string_soft_break_on_space(self):
        # Sentence with words; cap at 30 should break at last space within budget,
        # not mid-word.
        s = "TeamPCP weaponizes Jenkins build chain to poison KICS supply"
        result = l22._fit_band_text(s, 30)
        assert result.endswith("...")
        # The cut should NOT land mid-word — last char before "..." must be
        # the end of a word (alpha/digit), not whitespace, and the preceding
        # word boundary should be near a space within the 30-char budget.
        body = result[:-3].rstrip()
        # Verify body fits within budget and doesn't end with whitespace
        assert len(body) <= 30
        assert not body.endswith(" ")

    def test_long_unbroken_string_hard_cut(self):
        # If there is no space inside the budget, fall back to hard cut.
        s = "a" * 100  # no spaces
        result = l22._fit_band_text(s, 24)
        assert result.endswith("...")
        # Body length = max_chars - 1 (the rfind fallback)
        body = result[:-3]
        assert len(body) == 23

    def test_none_input_returns_empty_string(self):
        assert l22._fit_band_text(None, 50) == ""

    def test_non_string_coerced_then_capped(self):
        # int input should be coerced via str(), then capped at a realistic
        # production cap (24-60 chars per font-size). Use 24 — the headline
        # budget — for a stable assertion.
        s = int("1" * 60)  # 60-digit integer
        result = l22._fit_band_text(s, 24)
        assert result.endswith("...")
        # Body length is exactly the hard-cut fallback (max_chars - 1) since
        # the string contains no spaces.
        assert len(result[:-3]) == 23


class TestBandTextCappedInRender:
    """band() must truncate long text fields so they do not overflow into
    the visual or mini-card areas in the rendered SVG."""

    def _make_theme(self):
        # Minimal theme dict matching what band() reads.
        return {
            "accent": "#E63946",
            "soft": "#FCA5A5",
            "label": "#F87171",
            "metric": "#FBB6BD",
            "detail": "#D9C9CE",
            "card": "#1A0814",
            "pattern": "dotGrid",
        }

    def test_detail_field_truncated_in_band_output(self):
        # 100-char detail input — should appear truncated in SVG.
        detail_input = (
            "Active in-wild exploit deploys web shell on shared hosting "
            "at scale plus reseed admin tokens audit"
        )
        assert len(detail_input) > 50, "Setup: input must exceed detail cap"

        svg = l22.band(
            idx=0,
            theme=self._make_theme(),
            label="TEST",
            headline="Test headline",
            metric="Test metric",
            detail=detail_input,
            badge_value="X",
            badge_label="L",
            badge_sub="s",
            visual_svg="",
            sfx="TST1",
        )
        # The full original detail must NOT appear verbatim.
        assert detail_input not in svg, (
            "band() must cap the detail field — full 100+ char string leaked "
            "into rendered SVG, will overflow into visual at x=420."
        )
        # The capped form must appear with the ASCII ellipsis suffix.
        assert "..." in svg

    def test_detail_b_field_truncated_in_ultra_tier(self):
        detail_b_input = (
            "Block JDownloader install plus force fresh re-download plus EDR sweep "
            "for python and rotate creds"
        )
        assert len(detail_b_input) > 60

        svg = l22.band(
            idx=1,
            theme=self._make_theme(),
            label="L",
            headline="H",
            metric="M",
            detail="D",
            badge_value="X",
            badge_label="L",
            badge_sub="s",
            visual_svg="",
            sfx="TST2",
            tier="ultra",
            metric_b="m2",
            detail_b=detail_b_input,
        )
        assert detail_b_input not in svg, (
            "band() must cap detail_b in ultra tier — long input leaked through."
        )
        assert "..." in svg

    def test_short_inputs_pass_through_unchanged(self):
        svg = l22.band(
            idx=0,
            theme=self._make_theme(),
            label="L",
            headline="Short headline",
            metric="Short metric",
            detail="Short detail line",
            badge_value="X",
            badge_label="L",
            badge_sub="s",
            visual_svg="",
            sfx="TST3",
        )
        # Each short string should be present verbatim — no ellipsis appended.
        assert "Short headline" in svg
        assert "Short metric" in svg
        assert "Short detail line" in svg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
