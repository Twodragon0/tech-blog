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


def test_inline_diagram_filenames_are_exempt() -> None:
    """Small inline diagrams must not trigger std-min violations."""
    inline_diagrams = [
        "2026-01-22-Linux_Rootkit_Detection_Flow.svg",
        "2026-01-22-quadruple-extortion.svg",
        "2026-01-23-AitM_BEC_Attack_Flow.svg",
        "2026-01-24-bitlocker-key-flow.svg",
        "2026-01-29-n8n-sandbox-escape-attack-flow.svg",
        "2026-02-04-3cs-framework.svg",
        "2026-02-05-CVE-Timeline.svg",
    ]
    for name in inline_diagrams:
        svg = ASSETS / name
        if not svg.exists():
            pytest.skip(f"{name} not on disk")
        assert _gate.is_exempt(name), (
            f"{name} should be exempt but is_exempt() returned False. "
            "Update EXEMPT_PATTERNS in scripts/check_svg_size_gate.py."
        )


def test_baseline_silences_known_violations(tmp_path) -> None:
    """A baseline allow-list must keep strict-mode from failing on listed paths."""
    # Generate a fresh baseline from current state
    baseline = tmp_path / "baseline.txt"
    gen = subprocess.run(
        ["python3", str(PY_GATE), "--update-baseline", str(baseline)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert gen.returncode == 0
    assert baseline.exists()
    # With the baseline, --all --strict must exit 0 (legacy grandfathered).
    result = subprocess.run(
        ["python3", str(PY_GATE), "--all", "--strict", "--baseline", str(baseline)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        "strict mode with up-to-date baseline must pass.\n"
        f"stdout: {result.stdout}"
    )


def test_strict_blocks_new_violation(tmp_path) -> None:
    """A new out-of-band SVG NOT in baseline must trigger exit 1 under --strict."""
    # Create a fake std-profile SVG that overshoots the std max band.
    # Bigger than STD_MAX_BYTES (24576) so size check fires; lacks HQ/rollup
    # markers so it falls into the std bucket.
    fake = tmp_path / "2099-12-31-Synthetic_Regression_Test.svg"
    body = '<svg xmlns="http://www.w3.org/2000/svg" width="1" height="1">'
    body += '<!-- pad -->' * 4000  # ~50 KB of comment padding
    body += '</svg>'
    assert len(body) > 25000, "smoke test payload must exceed STD_MAX_BYTES"
    fake.write_text(body, encoding="utf-8")

    # Without baseline → strict exit 1
    result = subprocess.run(
        ["python3", str(PY_GATE), str(fake), "--strict"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 1, (
        f"strict mode must reject new oversize std SVG. "
        f"stdout: {result.stdout}"
    )
    assert "WARN" in result.stdout
    assert "FAIL" in result.stdout

    # With baseline including this path → strict exit 0
    baseline = tmp_path / "baseline.txt"
    # The gate stores paths repo-relative; for tmp paths that fall outside
    # the repo, repo_rel() falls back to the absolute path string. Match that.
    baseline.write_text(str(fake) + "\n", encoding="utf-8")

    result = subprocess.run(
        ["python3", str(PY_GATE), str(fake), "--strict", "--baseline", str(baseline)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, (
        f"baselined violation must pass strict mode.\n"
        f"stdout: {result.stdout}"
    )


def test_baseline_file_committed_and_current() -> None:
    """The committed baseline must be up-to-date with current repo state."""
    baseline = REPO / "scripts" / "svg_size_gate_baseline.txt"
    assert baseline.exists(), (
        "scripts/svg_size_gate_baseline.txt missing — regenerate with:\n"
        "  python3 scripts/check_svg_size_gate.py --update-baseline scripts/svg_size_gate_baseline.txt"
    )
    result = subprocess.run(
        ["python3", str(PY_GATE), "--all", "--strict", "--baseline", str(baseline)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        "Committed baseline is stale — new violations not yet baselined.\n"
        "Regenerate with:\n"
        "  python3 scripts/check_svg_size_gate.py --update-baseline scripts/svg_size_gate_baseline.txt\n"
        f"stdout: {result.stdout}"
    )
