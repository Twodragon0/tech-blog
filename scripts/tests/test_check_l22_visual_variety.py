#!/usr/bin/env python3
"""Tests for scripts/check_l22_visual_variety.py — L22 visual-variety CI gate."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.check_l22_visual_variety import check_file, main


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_svg(markers: list[str], tmp_path: Path, name: str = "test.svg") -> Path:
    """Write a minimal SVG containing the given band-visual comment markers."""
    lines = ['<svg xmlns="http://www.w3.org/2000/svg">']
    for kind in markers:
        lines.append(f'<!-- band-visual: {kind} -->')
        lines.append(f'<g transform="translate(500,105)"><circle/></g>')
    lines.append('</svg>')
    p = tmp_path / name
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# check_file unit tests
# ---------------------------------------------------------------------------


class TestCheckFile:
    def test_three_distinct_markers_pass(self, tmp_path: Path) -> None:
        """Cover with 3 distinct primitives must return PASS."""
        path = _make_svg(["lock_cve", "network_nodes", "code_bars"], tmp_path)
        status, msg = check_file(path)
        assert status == "PASS"
        assert msg is None

    def test_all_same_primitive_fails(self, tmp_path: Path) -> None:
        """Cover with 3× the same primitive (all lock_cve) must FAIL."""
        path = _make_svg(["lock_cve", "lock_cve", "lock_cve"], tmp_path)
        status, msg = check_file(path)
        assert status == "FAIL"
        assert msg is not None
        assert "duplicate" in msg.lower() or "distinct" in msg.lower()

    def test_two_distinct_one_dup_fails(self, tmp_path: Path) -> None:
        """2 distinct + 1 duplicate must FAIL (exact 3-distinct required)."""
        path = _make_svg(["lock_cve", "network_nodes", "lock_cve"], tmp_path)
        status, msg = check_file(path)
        assert status == "FAIL"
        assert msg is not None
        assert "lock_cve" in msg

    def test_no_markers_warns(self, tmp_path: Path) -> None:
        """Legacy cover with no markers must WARN, not FAIL."""
        path = tmp_path / "legacy.svg"
        path.write_text('<svg><g transform="translate(500,105)"/></svg>', encoding="utf-8")
        status, msg = check_file(path)
        assert status == "WARN"
        assert "legacy" in (msg or "").lower() or "no band-visual" in (msg or "").lower()

    def test_wrong_marker_count_fails(self, tmp_path: Path) -> None:
        """Cover with only 2 markers (malformed) must FAIL."""
        path = _make_svg(["lock_cve", "network_nodes"], tmp_path)
        status, msg = check_file(path)
        assert status == "FAIL"
        assert "expected 3" in (msg or "")

    def test_four_markers_fails(self, tmp_path: Path) -> None:
        """Cover with 4 markers (unexpected) must FAIL."""
        path = _make_svg(["lock_cve", "network_nodes", "code_bars", "shield"], tmp_path)
        status, msg = check_file(path)
        assert status == "FAIL"
        assert "expected 3" in (msg or "")


# ---------------------------------------------------------------------------
# main() integration tests
# ---------------------------------------------------------------------------


class TestMain:
    def test_all_pass_exits_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Batch where every file passes → exit 0."""
        _make_svg(["lock_cve", "network_nodes", "code_bars"], tmp_path, "a.svg")
        _make_svg(["shield", "router_mesh", "cloud_k8s"], tmp_path, "b.svg")
        monkeypatch.chdir(tmp_path)
        # point REPO_ROOT to tmp_path via the glob arg
        rc = main(["--glob", "*.svg"])
        assert rc == 0

    def test_one_fail_exits_one(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Batch with one failing cover → exit 1."""
        _make_svg(["lock_cve", "network_nodes", "code_bars"], tmp_path, "good.svg")
        _make_svg(["lock_cve", "lock_cve", "lock_cve"], tmp_path, "bad.svg")
        monkeypatch.chdir(tmp_path)
        rc = main(["--glob", "*.svg"])
        assert rc == 1

    def test_legacy_only_exits_zero(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Batch of legacy covers (no markers) → WARN only, exit 0."""
        p = tmp_path / "legacy.svg"
        p.write_text("<svg/>", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--glob", "*.svg"])
        assert rc == 0

    def test_mixed_batch_reports_failures(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        """Mixed batch reports each failure file name in output."""
        _make_svg(["lock_cve", "network_nodes", "code_bars"], tmp_path, "pass.svg")
        _make_svg(["shield", "shield", "shield"], tmp_path, "fail.svg")
        p_legacy = tmp_path / "legacy.svg"
        p_legacy.write_text("<svg/>", encoding="utf-8")
        monkeypatch.chdir(tmp_path)
        rc = main(["--glob", "*.svg"])
        captured = capsys.readouterr()
        assert rc == 1
        assert "fail.svg" in captured.out
        assert "1 fail" in captured.out
        assert "1 warn" in captured.out
