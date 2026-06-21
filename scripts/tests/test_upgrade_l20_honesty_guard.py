#!/usr/bin/env python3
"""Tests for the cover-honesty guard in scripts/upgrade_l20_cover.py.

Most ``_data/l20_covers/*.yml`` specs have drifted from the honest on-disk
corpus, so a blind ``upgrade_l20_cover.py --all`` re-render reintroduces
dishonest covers (the regression caught during PR #387). The guard renders
off-disk, scores each cover for honesty, and aborts the write run if any spec
would produce a NON-baselined honesty FAIL.

``sys.path`` setup is handled by conftest.py.
"""

from __future__ import annotations

import types
from pathlib import Path

import scripts.score_cover_honesty as sch
import scripts.upgrade_l20_cover as up


class _FakeSpec:
    """Minimal stand-in for upgrade_l20_cover.Spec (only what the guard /
    write loop touch)."""

    def __init__(self, filename: str, output_path: Path):
        self._filename = filename
        self.output_path = output_path

    @property
    def filename(self) -> str:
        return self._filename


# ---------------------------------------------------------------------------
# _honesty_regressions: baseline + verdict filtering
# ---------------------------------------------------------------------------


def test_honesty_regressions_filters_by_baseline_and_verdict(monkeypatch, tmp_path):
    rendered = [
        (_FakeSpec("fail_new.svg", tmp_path / "fail_new.svg"), "<svg/>"),
        (_FakeSpec("fail_baselined.svg", tmp_path / "fail_baselined.svg"), "<svg/>"),
        (_FakeSpec("clean.svg", tmp_path / "clean.svg"), "<svg/>"),
    ]
    verdicts = {
        "fail_new.svg": "FAIL",
        "fail_baselined.svg": "FAIL",
        "clean.svg": "PASS",
    }

    def fake_score_file(path):
        return {
            "verdict": verdicts[Path(path).name],
            "honesty": {
                "violations": [
                    {
                        "band": "hero",
                        "visual_id": "cve_chain",
                        "claim_class": "cve",
                        "reason": "no cve token",
                    }
                ]
            },
        }

    # fail_baselined.svg is grandfathered → must NOT be reported.
    monkeypatch.setattr(sch, "score_file", fake_score_file)
    monkeypatch.setattr(sch, "load_baseline", lambda p: {"assets/images/fail_baselined.svg"})
    baseline_file = tmp_path / "baseline.txt"
    baseline_file.write_text("assets/images/fail_baselined.svg\n", encoding="utf-8")
    monkeypatch.setattr(up, "_HONESTY_BASELINE", baseline_file)

    regs = up._honesty_regressions(rendered)

    assert len(regs) == 1, regs
    assert regs[0].startswith("fail_new.svg")
    assert "hero:cve_chain" in regs[0]


def test_honesty_regressions_empty_when_all_pass(monkeypatch, tmp_path):
    rendered = [(_FakeSpec("a.svg", tmp_path / "a.svg"), "<svg/>")]
    monkeypatch.setattr(sch, "score_file", lambda p: {"verdict": "PASS", "honesty": {"violations": []}})
    monkeypatch.setattr(sch, "load_baseline", lambda p: set())
    monkeypatch.setattr(up, "_HONESTY_BASELINE", tmp_path / "nope.txt")
    assert up._honesty_regressions(rendered) == []


# ---------------------------------------------------------------------------
# main(): write run aborts on regression; --force / --dry-run skip the guard
# ---------------------------------------------------------------------------


def _stub_render_path(monkeypatch, tmp_path):
    """Stub spec gathering / loading / rendering so main() runs without real
    specs. Returns the output path the write loop would touch."""
    out = tmp_path / "stub-cover.svg"
    spec = _FakeSpec("stub-cover.svg", out)
    monkeypatch.setattr(up, "_gather_specs", lambda args: [Path("stub.yml")])
    monkeypatch.setattr(up, "load_spec", lambda p: spec)
    monkeypatch.setattr(up, "render", lambda s: "<svg>stub</svg>")
    return out


def test_main_write_aborts_on_regression(monkeypatch, tmp_path):
    out = _stub_render_path(monkeypatch, tmp_path)
    monkeypatch.setattr(up, "_honesty_regressions", lambda rendered: ["stub-cover.svg  [hero:cve_chain]"])

    rc = up.main(["--all"])

    assert rc == 1
    assert not out.exists(), "guard must block the write — no file should be created"


def test_main_force_bypasses_guard(monkeypatch, tmp_path):
    out = _stub_render_path(monkeypatch, tmp_path)

    def _must_not_run(rendered):
        raise AssertionError("honesty guard must not run under --force")

    monkeypatch.setattr(up, "_honesty_regressions", _must_not_run)

    rc = up.main(["--all", "--force"])

    assert rc == 0
    assert out.read_text(encoding="utf-8") == "<svg>stub</svg>"


def test_main_dry_run_skips_guard_and_writes_nothing(monkeypatch, tmp_path):
    out = _stub_render_path(monkeypatch, tmp_path)

    def _must_not_run(rendered):
        raise AssertionError("honesty guard must not run under --dry-run")

    monkeypatch.setattr(up, "_honesty_regressions", _must_not_run)

    rc = up.main(["--all", "--dry-run"])

    assert rc == 0
    assert not out.exists(), "--dry-run must not write"
