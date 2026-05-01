#!/usr/bin/env python3
"""Tests for scripts/dev/compare_lighthouse_runs.py.

Tests the pure logic by writing synthetic LHR JSON fixtures into temp
directories and asserting on rows + exit codes + Markdown output.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

_RUN_PY = REPO_ROOT / "scripts" / "dev" / "compare_lighthouse_runs.py"
spec = importlib.util.spec_from_file_location("compare_lighthouse_runs", _RUN_PY)
clr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clr)


def _write_lhr(target_dir: Path, url: str, lcp_ms: float, cls: float = 0.05,
               tbt_ms: float = 100.0, fcp_ms: float = 800.0, run_id: int = 1) -> Path:
    """Write a synthetic Lighthouse-report JSON file into ``target_dir``."""
    target_dir.mkdir(parents=True, exist_ok=True)
    path = target_dir / f"lhr-{run_id}.json"
    payload = {
        "finalDisplayedUrl": url,
        "finalUrl": url,
        "audits": {
            "largest-contentful-paint": {"numericValue": lcp_ms},
            "cumulative-layout-shift": {"numericValue": cls},
            "total-blocking-time": {"numericValue": tbt_ms},
            "first-contentful-paint": {"numericValue": fcp_ms},
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_passes_when_within_threshold(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/", lcp_ms=1800)
    _write_lhr(head, "http://localhost:4000/", lcp_ms=1900)  # +100 ms, under 200 threshold

    rows, exit_code = clr.compare(base, head, threshold_ms=200.0)
    assert exit_code == 0
    assert len(rows) == 1
    assert rows[0]["delta_lcp"] == pytest.approx(100.0)
    assert rows[0]["verdict"] == "PASS"


def test_fails_when_threshold_exceeded(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/", lcp_ms=1800)
    _write_lhr(head, "http://localhost:4000/", lcp_ms=2100)  # +300 ms, over 200 threshold

    rows, exit_code = clr.compare(base, head, threshold_ms=200.0)
    assert exit_code == 1
    assert "FAIL" in rows[0]["verdict"]
    assert rows[0]["delta_lcp"] == pytest.approx(300.0)


def test_median_of_multiple_runs(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    for run_id, lcp in enumerate([1700, 1800, 1900], start=1):
        _write_lhr(base, "http://localhost:4000/", lcp_ms=lcp, run_id=run_id)
    for run_id, lcp in enumerate([2200, 2400, 2300], start=1):
        _write_lhr(head, "http://localhost:4000/", lcp_ms=lcp, run_id=run_id)

    rows, exit_code = clr.compare(base, head, threshold_ms=200.0)
    assert exit_code == 1  # 2300 - 1800 = 500 > 200
    assert rows[0]["base_lcp"] == pytest.approx(1800)
    assert rows[0]["head_lcp"] == pytest.approx(2300)


def test_url_normalisation_across_localhost_and_loopback(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/post/", lcp_ms=1800)
    _write_lhr(head, "http://127.0.0.1:4000/post/", lcp_ms=1850)

    rows, exit_code = clr.compare(base, head, threshold_ms=200.0)
    assert exit_code == 0
    assert len(rows) == 1
    assert rows[0]["url"] == "/post/"
    assert rows[0]["delta_lcp"] == pytest.approx(50.0)


def test_no_comparable_urls(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/page-a/", lcp_ms=1800)
    _write_lhr(head, "http://localhost:4000/page-b/", lcp_ms=1900)

    rows, exit_code = clr.compare(base, head, threshold_ms=200.0)
    assert exit_code == 0  # no failures, but also no rows
    assert rows == []


def test_markdown_output_structure(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/", lcp_ms=1800, cls=0.05, tbt_ms=120, fcp_ms=900)
    _write_lhr(head, "http://localhost:4000/", lcp_ms=2100, cls=0.06, tbt_ms=180, fcp_ms=950)

    rows, _ = clr.compare(base, head, threshold_ms=200.0)
    md = clr.render_markdown(rows, 200.0)
    assert "Lighthouse perf gate" in md
    assert "Base LCP" in md and "Head LCP" in md and "Δ LCP" in md
    assert "+300 ms" in md
    assert "FAIL" in md
    # CLS / TBT columns present
    assert "Δ CLS" in md
    assert "Δ TBT" in md


def test_main_writes_markdown_and_returns_exit_code(tmp_path, capsys, monkeypatch):
    base = tmp_path / "base"
    head = tmp_path / "head"
    out = tmp_path / "report.md"
    _write_lhr(base, "http://localhost:4000/", lcp_ms=1800)
    _write_lhr(head, "http://localhost:4000/", lcp_ms=2100)  # +300 ms

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_lighthouse_runs.py",
            "--base-dir", str(base),
            "--head-dir", str(head),
            "--threshold-lcp-ms", "200",
            "--output-md", str(out),
            "--quiet",
        ],
    )
    exit_code = clr.main()
    assert exit_code == 1
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "FAIL" in text
    assert "+300 ms" in text


def test_main_quiet_flag_silences_stdout(tmp_path, capsys, monkeypatch):
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/", lcp_ms=1800)
    _write_lhr(head, "http://localhost:4000/", lcp_ms=1850)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_lighthouse_runs.py",
            "--base-dir", str(base),
            "--head-dir", str(head),
            "--threshold-lcp-ms", "200",
            "--quiet",
        ],
    )
    clr.main()
    captured = capsys.readouterr()
    assert captured.out == ""


def test_missing_base_dir_returns_no_rows(tmp_path):
    head = tmp_path / "head"
    _write_lhr(head, "http://localhost:4000/", lcp_ms=1800)
    rows, exit_code = clr.compare(tmp_path / "nonexistent-base", head, threshold_ms=200.0)
    assert rows == []
    assert exit_code == 0


def test_threshold_zero_fails_any_regression(tmp_path):
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/", lcp_ms=1800)
    _write_lhr(head, "http://localhost:4000/", lcp_ms=1801)  # +1 ms

    rows, exit_code = clr.compare(base, head, threshold_ms=0.0)
    assert exit_code == 1
    assert "FAIL" in rows[0]["verdict"]


def test_negative_delta_passes(tmp_path):
    """Improvement (negative delta) must always pass."""
    base = tmp_path / "base"
    head = tmp_path / "head"
    _write_lhr(base, "http://localhost:4000/", lcp_ms=2000)
    _write_lhr(head, "http://localhost:4000/", lcp_ms=1500)  # 500 ms improvement

    rows, exit_code = clr.compare(base, head, threshold_ms=200.0)
    assert exit_code == 0
    assert rows[0]["delta_lcp"] == pytest.approx(-500.0)
    assert rows[0]["verdict"] == "PASS"
