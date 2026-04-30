#!/usr/bin/env python3
"""Tests for the --strict / --threshold gate in reports/l20-visual-regression/run.py.

These tests do NOT call rsvg-convert, render SVGs, or write any files.
They test only the pure gate logic (check_strict_gate) and argument parsing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Path setup — add repo root so we can import the run module directly
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import importlib.util

_RUN_PY = REPO_ROOT / "reports" / "l20-visual-regression" / "run.py"
spec = importlib.util.spec_from_file_location("l20_run", _RUN_PY)
l20_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l20_run)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row(name: str, hamming: int, is_ref: bool = False) -> dict:
    return {
        "name": name,
        "size_kb": 150.0,
        "phash": "83c3307403a3f700",
        "hamming": hamming,
        "category": l20_run.categorize(hamming),
        "is_ref": is_ref,
        "error": None,
        "avg_color": "#211c26",
    }


# ---------------------------------------------------------------------------
# Tests: check_strict_gate (pure function)
# ---------------------------------------------------------------------------

class TestCheckStrictGate:
    """check_strict_gate(rows, threshold) returns outlier rows."""

    def test_no_outliers_returns_empty(self):
        rows = [
            _row("ref.svg", 0, is_ref=True),
            _row("a.svg", 10),
            _row("b.svg", 25),  # exactly at boundary — NOT an outlier
        ]
        result = l20_run.check_strict_gate(rows, threshold=25)
        assert result == []

    def test_outlier_above_threshold_returned(self):
        rows = [
            _row("ref.svg", 0, is_ref=True),
            _row("ok.svg", 20),
            _row("bad.svg", 26),  # 26 > 25 → outlier
        ]
        result = l20_run.check_strict_gate(rows, threshold=25)
        assert len(result) == 1
        assert result[0]["name"] == "bad.svg"

    def test_reference_row_excluded_even_if_hamming_exceeds(self):
        """Reference row is never flagged (is_ref=True guard)."""
        rows = [
            _row("ref.svg", 99, is_ref=True),  # artificially high but is_ref
            _row("a.svg", 5),
        ]
        result = l20_run.check_strict_gate(rows, threshold=25)
        assert result == []

    def test_multiple_outliers_all_returned(self):
        rows = [
            _row("ref.svg", 0, is_ref=True),
            _row("a.svg", 30),
            _row("b.svg", 40),
            _row("c.svg", 10),
        ]
        result = l20_run.check_strict_gate(rows, threshold=25)
        names = {r["name"] for r in result}
        assert names == {"a.svg", "b.svg"}

    def test_custom_threshold_tighter(self):
        """threshold=10: Hamming=15 is an outlier."""
        rows = [
            _row("ref.svg", 0, is_ref=True),
            _row("edge.svg", 15),
        ]
        result = l20_run.check_strict_gate(rows, threshold=10)
        assert len(result) == 1
        assert result[0]["name"] == "edge.svg"

    def test_custom_threshold_looser(self):
        """threshold=50: Hamming=35 is within bounds."""
        rows = [
            _row("ref.svg", 0, is_ref=True),
            _row("a.svg", 35),
        ]
        result = l20_run.check_strict_gate(rows, threshold=50)
        assert result == []

    def test_boundary_at_threshold_is_not_outlier(self):
        """Hamming == threshold must NOT be flagged (> not >=)."""
        rows = [
            _row("ref.svg", 0, is_ref=True),
            _row("a.svg", 15),
        ]
        result = l20_run.check_strict_gate(rows, threshold=15)
        assert result == []


# ---------------------------------------------------------------------------
# Tests: argument parsing
# ---------------------------------------------------------------------------

class TestParseArgs:
    """parse_args() accepts --strict and --threshold."""

    def _parse(self, argv: list[str]):
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(sys, "argv", ["run.py"] + argv)
            return l20_run.parse_args()

    def test_defaults(self):
        args = self._parse([])
        assert args.strict is False
        assert args.threshold == 25

    def test_strict_flag(self):
        args = self._parse(["--strict"])
        assert args.strict is True

    def test_threshold_flag(self):
        args = self._parse(["--threshold", "10"])
        assert args.threshold == 10

    def test_strict_and_threshold_together(self):
        args = self._parse(["--strict", "--threshold", "30"])
        assert args.strict is True
        assert args.threshold == 30
