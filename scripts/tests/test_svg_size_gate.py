#!/usr/bin/env python3
"""Sanity tests for the SVG size gate.

The gate has two entry points that must stay in sync:
  - scripts/check_svg_size_gate.py   (canonical Python implementation)
  - scripts/check_svg_precommit.sh   (shell thin delegator)
Both consume the SAME classifier defined in check_svg_size_gate.py,
so the pre-commit hook and the .github/workflows/svg-lint.yml CI step
catch the same regressions.

This file imports the Python gate directly and reuses its classify()
+ BANDS to verify (1) every committed rollup SVG falls inside the
rollup band, (2) known rollup/hq dates are classified correctly, and
(3) both entry points exit 0 with no staged diff.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
SHELL_GATE = REPO / "scripts" / "check_svg_precommit.sh"
PY_GATE = REPO / "scripts" / "check_svg_size_gate.py"
ASSETS = REPO / "assets" / "images"


# Load the Python gate as a module to reuse its classifier + BANDS.
_spec = importlib.util.spec_from_file_location("_svg_gate", PY_GATE)
_gate = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_gate)  # type: ignore[union-attr]

classify = _gate.classify
BANDS = _gate.BANDS


def size(svg: Path) -> int:
    return svg.stat().st_size


def test_gate_script_exists_and_executable() -> None:
    """Both gate entry points must exist."""
    assert SHELL_GATE.exists(), f"missing {SHELL_GATE}"
    assert SHELL_GATE.read_text().startswith("#!/bin/sh")
    assert PY_GATE.exists(), f"missing {PY_GATE}"
    assert PY_GATE.read_text().startswith("#!/usr/bin/env python3")


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


def test_shell_gate_runs_without_diff_returns_zero() -> None:
    """The shell wrapper must exit 0 (warn-only) regardless of state."""
    result = subprocess.run(
        ["sh", str(SHELL_GATE)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0


def test_python_gate_strict_mode_signals_violations() -> None:
    """--strict must exit non-zero when violations exist (smoke via --all)."""
    result = subprocess.run(
        ["python3", str(PY_GATE), "--all", "--strict"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # The repo contains pre-existing legacy SVGs outside their bands;
    # the gate's job is to surface them. We just verify --strict propagates
    # the warning count to the exit code so CI can fail on regressions.
    if "WARN" in result.stdout:
        assert result.returncode == 1, "--strict must exit 1 on any WARN"
    else:
        assert result.returncode == 0


def test_python_gate_warn_only_mode_returns_zero() -> None:
    """Without --strict the gate must return 0 even with violations."""
    result = subprocess.run(
        ["python3", str(PY_GATE), "--all"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, "warn-only mode must always exit 0"
