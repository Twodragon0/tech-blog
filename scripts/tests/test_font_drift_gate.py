"""Tests for scripts/dev/check_font_drift.py.

Each test exercises the gate logic either via the public API
(check_font_drift) or via subprocess to validate the CLI exit codes.
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts/ to path so we can import the helper directly
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "dev"))

from check_font_drift import check_font_drift  # noqa: E402

SCRIPT = Path(__file__).parent.parent / "dev" / "check_font_drift.py"

WOFF2_A = "assets/fonts/noto-sans-kr-400-tier1.woff2"
WOFF2_B = "assets/fonts/noto-sans-kr-700-tier2.woff2"
GENERATOR = "scripts/build/generate_noto_2tier_subset.py"
CORPUS = "scripts/build/noto_subset_top1k.txt"
UNRELATED = "README.md"


# ---------------------------------------------------------------------------
# Unit tests via check_font_drift()
# ---------------------------------------------------------------------------


def test_empty_diff_passes():
    """Empty diff should pass — no woff2 changed."""
    assert check_font_drift([]) is True


def test_only_generator_changed_passes():
    """Only the generator script changed, no woff2 — no enforcement needed."""
    assert check_font_drift([GENERATOR]) is True


def test_only_corpus_changed_passes():
    """Only the corpus file changed, no woff2 — no enforcement needed."""
    assert check_font_drift([CORPUS]) is True


def test_woff2_plus_generator_passes():
    """woff2 and generator both changed — gate passes."""
    assert check_font_drift([WOFF2_A, GENERATOR]) is True


def test_woff2_plus_corpus_passes():
    """woff2 and corpus both changed — gate passes."""
    assert check_font_drift([WOFF2_A, CORPUS]) is True


def test_only_woff2_fails():
    """Single woff2 changed with no source file — gate fails."""
    assert check_font_drift([WOFF2_A]) is False


def test_multiple_woff2_no_source_fails():
    """Multiple woff2 files changed with no source file — gate fails."""
    assert check_font_drift([WOFF2_A, WOFF2_B]) is False


def test_woff2_plus_unrelated_file_fails():
    """woff2 + unrelated file (e.g. README) — gate must still fail."""
    assert check_font_drift([WOFF2_A, UNRELATED]) is False


# ---------------------------------------------------------------------------
# CLI smoke tests via subprocess (validates argparse + exit codes)
# ---------------------------------------------------------------------------


def _run(changed_files: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--changed-files", changed_files],
        capture_output=True,
        text=True,
    )


def test_cli_passes_with_generator():
    result = _run(f"{WOFF2_A},{GENERATOR}")
    assert result.returncode == 0


def test_cli_fails_woff2_only():
    result = _run(WOFF2_A)
    assert result.returncode == 1
    # Failure message should reference the decision doc
    assert "WOFF2_LFS_DECISION.md" in result.stderr
