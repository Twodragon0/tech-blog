#!/usr/bin/env python3
"""Golden-snapshot regression tests for the L22 ultra weekly-digest SVG renderer.

Protects the two visually-verified covers (2026-04-29, 2026-04-30) against
silent renderer drift.  Any change to ``upgrade_digest_cover.render()``,
``svg_l22_generator``, or the YAML specs that alters the output will fail
these tests and surface the message:

    "renderer drift detected — visual review required"

Tests in this file never regenerate or commit images.  They are read-only
with respect to the ``assets/images/`` directory.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ── project path setup ──────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SPECS_DIR = REPO_ROOT / "_data" / "digest_covers"
ASSETS_DIR = REPO_ROOT / "assets" / "images"

# ── helpers ─────────────────────────────────────────────────────────────────


def _golden_path(date: str, slug: str) -> Path:
    return ASSETS_DIR / f"{date}-{slug}.svg"


def _load_and_render(spec_path: Path) -> str:
    """Load a YAML spec and return the re-rendered SVG string."""
    from scripts.upgrade_digest_cover import load_spec, render  # noqa: PLC0415
    return render(load_spec(spec_path))


# ── parametrize fixtures ─────────────────────────────────────────────────────

# (date, slug) pairs for the two visually-verified L22 ultra covers
_GOLDEN_SPECS = [
    pytest.param(
        "2026-04-29",
        "Tech_Security_Weekly_Digest_CVE_AI_Ransomware_Update",
        id="2026-04-29",
    ),
    pytest.param(
        "2026-04-30",
        "Tech_Security_Weekly_Digest_AI_Malware_Rust",
        id="2026-04-30",
    ),
]


# ── 1. Golden snapshot tests (byte-equality) ─────────────────────────────────


class TestGoldenSnapshots:
    """Re-render each spec and assert byte-exact equality with the on-disk SVG."""

    @pytest.mark.parametrize("date,slug", _GOLDEN_SPECS)
    def test_renderer_matches_golden_svg(self, date: str, slug: str) -> None:
        """Rendered output must be byte-identical to the on-disk golden SVG.

        Failure means a renderer change silently altered a cover that has
        already been visually approved.
        """
        spec_path = SPECS_DIR / f"{date}.yml"
        golden_path = _golden_path(date, slug)

        assert spec_path.exists(), f"spec not found: {spec_path}"
        assert golden_path.exists(), f"golden SVG not found: {golden_path}"

        rendered = _load_and_render(spec_path)
        golden = golden_path.read_text(encoding="utf-8")

        assert rendered == golden, (
            f"renderer drift detected — visual review required\n"
            f"  spec : {spec_path.relative_to(REPO_ROOT)}\n"
            f"  golden: {golden_path.relative_to(REPO_ROOT)}\n"
            f"  rendered bytes: {len(rendered.encode())}  "
            f"  golden bytes: {len(golden.encode())}"
        )


# ── 2. Structural invariants (L22 ultra contract) ────────────────────────────

# Theme accent colors map (from svg_l22_generator.THEMES).
# Keyed here as constants to avoid importing the full module in the
# invariant tests (they re-render from spec, not from THEMES dict).
_THEME_ACCENTS = {
    "red":    "#E63946",
    "amber":  "#FFB703",
    "green":  "#4ADE80",
    "blue":   "#60A5FA",
    "purple": "#A78BFA",
}

# Expected theme set per spec (derived from the band definitions in YAML).
_EXPECTED_THEMES: dict[str, set[str]] = {
    "2026-04-29": {"red", "amber", "green"},
    "2026-04-30": {"red", "amber", "blue"},
}


class TestStructuralInvariants:
    """L22 ultra contract: these invariants must hold for every canonical cover.

    These tests run against rendered output (not the on-disk golden files)
    so they catch regressions even before byte equality is checked.
    """

    @pytest.mark.parametrize("date,slug", _GOLDEN_SPECS)
    def test_qr_block_present(self, date: str, slug: str) -> None:
        """SVG must contain the QR-block translate marker ``translate(1080,504)``."""
        svg = _load_and_render(SPECS_DIR / f"{date}.yml")
        assert "translate(1080,504)" in svg, (
            f"{date}: QR block missing — translate(1080,504) not found in SVG"
        )

    @pytest.mark.parametrize("date,slug", _GOLDEN_SPECS)
    def test_file_size_indicates_ultra_tier(self, date: str, slug: str) -> None:
        """Rendered SVG must be at least 50,000 bytes (L22 ultra, not L20 fallback)."""
        svg = _load_and_render(SPECS_DIR / f"{date}.yml")
        byte_len = len(svg.encode("utf-8"))
        assert byte_len >= 50_000, (
            f"{date}: SVG too small ({byte_len} bytes < 50 000) — "
            "possible L20 fallback or truncation"
        )

    @pytest.mark.parametrize("date,slug", _GOLDEN_SPECS)
    def test_all_three_theme_accents_present(self, date: str, slug: str) -> None:
        """SVG must contain the accent colors for all three band themes."""
        svg = _load_and_render(SPECS_DIR / f"{date}.yml")
        expected_themes = _EXPECTED_THEMES[date]
        for theme_name in expected_themes:
            accent = _THEME_ACCENTS[theme_name]
            assert accent in svg, (
                f"{date}: accent color for theme '{theme_name}' ({accent}) "
                f"not found in SVG — expected themes: {expected_themes}"
            )

    @pytest.mark.parametrize("date,slug", _GOLDEN_SPECS)
    def test_title_element_non_empty(self, date: str, slug: str) -> None:
        """SVG must contain a non-empty ``<title>`` element."""
        svg = _load_and_render(SPECS_DIR / f"{date}.yml")
        match = re.search(r"<title>([^<]+)</title>", svg)
        assert match is not None and match.group(1).strip(), (
            f"{date}: <title> element is missing or empty"
        )
