#!/usr/bin/env python3
"""Sanity tests for scripts/check_svg_precommit.sh.

Verifies the gate correctly classifies the three SVG profiles
(lane/digest, high-quality cover, weekly/monthly rollup) and does
not emit a false-positive WARN for any cover currently committed
under ``assets/images/``.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
GATE = REPO / "scripts" / "check_svg_precommit.sh"
ASSETS = REPO / "assets" / "images"


# Markers copied from check_svg_precommit.sh (must stay in sync).
HQ_RE = re.compile(
    r'sceneGlow1|sceneGlow2|@keyframes [^ ]*floatUp|clipPath id="[^"]*clip"'
    r'|profile: high-quality-cover|id="bgSpread[A-Z0-9]*"'
    r'|id="heroPanel[A-Z0-9]*"|id="bandA[A-Z0-9]+"'
)
ROLLUP_RE = re.compile(
    r'>WEEKLY ROLLUP<|>MONTHLY INDEX<|id="bgRoll[A-Z0-9]+"|id="hdrGrad[A-Z0-9]+"'
)


def classify(svg: Path) -> str:
    """Replicate the gate's profile detection in Python for testability."""
    text = svg.read_text(encoding="utf-8", errors="replace")
    # rollup check fires first in the gate
    if ROLLUP_RE.search(text):
        return "rollup"
    if HQ_RE.search(text):
        return "hq"
    return "std"


def size(svg: Path) -> int:
    return svg.stat().st_size


# Profile bands must match the values in check_svg_precommit.sh.
BANDS = {
    "std": (5000, 24576),
    "hq": (18000, 73728),
    "rollup": (38000, 83968),
}


def test_gate_script_exists_and_executable() -> None:
    """The gate fragment must exist and be a runnable shell script."""
    assert GATE.exists(), f"missing {GATE}"
    assert GATE.read_text().startswith("#!/bin/sh")


def test_rollup_band_covers_existing_rollups() -> None:
    """Every committed rollup SVG must fall inside the rollup band."""
    rollups = []
    for svg in sorted(ASSETS.glob("2026-*.svg")):
        if classify(svg) == "rollup":
            rollups.append(svg)
    assert rollups, "expected at least one rollup SVG under assets/images/"
    mn, mx = BANDS["rollup"]
    out_of_band = [(svg.name, size(svg)) for svg in rollups if not (mn <= size(svg) <= mx)]
    assert not out_of_band, (
        f"rollup band [{mn}, {mx}] excludes: {out_of_band}. "
        "Update ROLLUP_MIN_BYTES / ROLLUP_MAX_BYTES in check_svg_precommit.sh."
    )


def test_known_rollup_dates_classified_correctly() -> None:
    """Known rollup files must be classified as rollup, not hq or std."""
    known_rollup_stems = [
        "2026-04-12-Week2_April_2026_Security_Digest",
        "2026-04-19-Week3_April_2026_Security_Digest",
        "2026-01-31-January_2026_Security_Digest_Monthly_Index",
        "2026-02-28-February_2026_Security_Digest_Monthly_Index",
    ]
    for stem in known_rollup_stems:
        svg = ASSETS / f"{stem}.svg"
        if not svg.exists():
            pytest.skip(f"{svg.name} not on disk")
        assert classify(svg) == "rollup", (
            f"{svg.name} classified as {classify(svg)}; expected rollup. "
            "Rollup markers may have drifted in svg_rollup_generator."
        )


def test_l20_hero_covers_classify_as_hq() -> None:
    """L20 Hero+2-Card covers (profile string in comment) must classify as hq."""
    samples = [
        "2026-04-15-Tech_Security_Weekly_Digest_AI_AWS_Agent_Patch",
        "2026-05-19-Tech_Security_Weekly_Digest_Cloud_AI_Malware_Go",
    ]
    for stem in samples:
        svg = ASSETS / f"{stem}.svg"
        if not svg.exists():
            pytest.skip(f"{svg.name} not on disk")
        assert classify(svg) == "hq", (
            f"{svg.name} classified as {classify(svg)}; expected hq."
        )


def test_gate_runs_without_diff_returns_zero() -> None:
    """Running the gate with no staged diff must exit 0 silently."""
    result = subprocess.run(
        ["sh", str(GATE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
        env={"PATH": "/usr/bin:/bin"},
    )
    assert result.returncode == 0
    # No staged SVGs in test env → no output expected
    assert "WARN" not in result.stdout
