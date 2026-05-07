#!/usr/bin/env python3
"""Unit tests for scripts/check_workflow_action_pins.py."""

from __future__ import annotations

import os
import sys
import textwrap
from pathlib import Path

import pytest

# Ensure the scripts directory is on the path.
sys.path.insert(0, str(Path(__file__).parent.parent))

import check_workflow_action_pins as checker


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SHA_A = "de0fac2e4500dabe0009e67214ff5f5447ce83dd"  # checkout v6 canonical
SHA_B = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"  # fake minority SHA
SHA_C = "b309ff8b426b58ec0e2a45f0f869d46889d02405"  # setup-python v6 canonical


def _make_workflow(name: str, tmp_path: Path, content: str) -> Path:
    """Write a YAML file to tmp_path and return its path."""
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# test_extract_uses_directives — correct pattern extraction
# ---------------------------------------------------------------------------


class TestExtractUsesDirectives:
    def test_extracts_sha_pin(self, tmp_path):
        _make_workflow("w.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}  # v6
        """)
        pins = checker.collect_pins(tmp_path)
        assert len(pins) == 1
        assert pins[0].action == "actions/checkout"
        assert pins[0].ref == SHA_A
        assert pins[0].workflow == "w.yml"
        assert pins[0].line == 2

    def test_extracts_floating_tag(self, tmp_path):
        _make_workflow("w.yml", tmp_path, """\
            steps:
              - uses: actions/setup-python@v5
        """)
        pins = checker.collect_pins(tmp_path)
        assert len(pins) == 1
        assert pins[0].ref == "v5"

    def test_extracts_multiple_actions(self, tmp_path):
        _make_workflow("w.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
              - uses: actions/setup-python@{SHA_C}
        """)
        pins = checker.collect_pins(tmp_path)
        assert len(pins) == 2
        actions = {p.action for p in pins}
        assert "actions/checkout" in actions
        assert "actions/setup-python" in actions

    def test_skips_non_uses_lines(self, tmp_path):
        _make_workflow("w.yml", tmp_path, """\
            name: test
            on: push
            jobs:
              build:
                runs-on: ubuntu-latest
                steps:
                  - run: echo hello
        """)
        pins = checker.collect_pins(tmp_path)
        assert pins == []

    def test_extracts_from_multiple_workflows(self, tmp_path):
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        pins = checker.collect_pins(tmp_path)
        assert len(pins) == 2
        workflows = {p.workflow for p in pins}
        assert "a.yml" in workflows
        assert "b.yml" in workflows


# ---------------------------------------------------------------------------
# test_consistent_pins_pass — all same SHA → no consistency errors
# ---------------------------------------------------------------------------


class TestConsistentPinsPass:
    def test_same_sha_across_two_workflows(self, tmp_path):
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        pins = checker.collect_pins(tmp_path)
        errors = checker.check_consistency(pins)
        assert errors == []

    def test_different_actions_no_conflict(self, tmp_path):
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
              - uses: actions/setup-python@{SHA_C}
        """)
        pins = checker.collect_pins(tmp_path)
        errors = checker.check_consistency(pins)
        assert errors == []


# ---------------------------------------------------------------------------
# test_inconsistent_pins_fail — different SHAs → errors
# ---------------------------------------------------------------------------


class TestInconsistentPinsFail:
    def test_two_different_shas_detected(self, tmp_path):
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_B}
        """)
        pins = checker.collect_pins(tmp_path)
        errors = checker.check_consistency(pins)
        assert len(errors) > 0
        combined = "\n".join(errors)
        assert "actions/checkout" in combined

    def test_error_mentions_both_workflows(self, tmp_path):
        _make_workflow("alpha.yml", tmp_path, f"""\
            steps:
              - uses: actions/setup-python@{SHA_C}
        """)
        _make_workflow("beta.yml", tmp_path, f"""\
            steps:
              - uses: actions/setup-python@{SHA_B}
        """)
        pins = checker.collect_pins(tmp_path)
        errors = checker.check_consistency(pins)
        combined = "\n".join(errors)
        assert "alpha.yml" in combined
        assert "beta.yml" in combined

    def test_main_exits_one_on_inconsistency(self, tmp_path):
        _make_workflow("x.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("y.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_B}
        """)
        rc = checker.main(["--workflows-dir", str(tmp_path)])
        assert rc == 1

    def test_single_workflow_always_consistent(self, tmp_path):
        """One workflow can't disagree with itself — no cross-file conflict."""
        _make_workflow("solo.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
              - uses: actions/checkout@{SHA_A}
        """)
        pins = checker.collect_pins(tmp_path)
        errors = checker.check_consistency(pins)
        assert errors == []


# ---------------------------------------------------------------------------
# test_floating_tag_warning — @v5 etc. produce warnings
# ---------------------------------------------------------------------------


class TestFloatingTagWarning:
    def test_floating_v_tag_warned(self, tmp_path):
        _make_workflow("w.yml", tmp_path, """\
            steps:
              - uses: actions/setup-python@v5
        """)
        pins = checker.collect_pins(tmp_path)
        warnings = checker.check_sha_format(pins)
        assert len(warnings) == 1
        assert "FLOATING TAG" in warnings[0]
        assert "v5" in warnings[0]

    def test_floating_tag_in_different_workflows(self, tmp_path):
        _make_workflow("a.yml", tmp_path, """\
            steps:
              - uses: actions/checkout@v4
        """)
        _make_workflow("b.yml", tmp_path, """\
            steps:
              - uses: actions/setup-python@v5
        """)
        pins = checker.collect_pins(tmp_path)
        warnings = checker.check_sha_format(pins)
        assert len(warnings) == 2

    def test_sha_pin_produces_no_format_warning(self, tmp_path):
        _make_workflow("w.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        pins = checker.collect_pins(tmp_path)
        warnings = checker.check_sha_format(pins)
        assert warnings == []

    def test_warn_only_exits_zero_even_with_floating_tags(self, tmp_path):
        """--warn-only suppresses non-zero exit for format warnings."""
        _make_workflow("w.yml", tmp_path, """\
            steps:
              - uses: actions/checkout@v4
        """)
        rc = checker.main(["--warn-only", "--workflows-dir", str(tmp_path)])
        assert rc == 0


# ---------------------------------------------------------------------------
# test_skip_env_bypass — SKIP_PIN_CHECK=1 → exit 0 immediately
# ---------------------------------------------------------------------------


class TestSkipEnvBypass:
    def test_skip_pin_check_env_exits_zero(self, tmp_path, monkeypatch):
        # Even with a real inconsistency, SKIP_PIN_CHECK=1 exits 0.
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_B}
        """)
        monkeypatch.setenv("SKIP_PIN_CHECK", "1")
        rc = checker.main(["--workflows-dir", str(tmp_path)])
        assert rc == 0

    def test_skip_pin_check_zero_by_default(self, tmp_path, monkeypatch):
        monkeypatch.delenv("SKIP_PIN_CHECK", raising=False)
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_B}
        """)
        rc = checker.main(["--workflows-dir", str(tmp_path)])
        assert rc == 1  # No bypass → should fail


# ---------------------------------------------------------------------------
# test_warn_only_returns_zero — --warn-only always exits 0
# ---------------------------------------------------------------------------


class TestWarnOnlyReturnsZero:
    def test_warn_only_exits_zero_with_consistency_error(self, tmp_path):
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_B}
        """)
        rc = checker.main(["--warn-only", "--workflows-dir", str(tmp_path)])
        assert rc == 0

    def test_warn_only_exits_zero_with_no_violations(self, tmp_path):
        _make_workflow("w.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        rc = checker.main(["--warn-only", "--workflows-dir", str(tmp_path)])
        assert rc == 0


# ---------------------------------------------------------------------------
# test_fix — --fix unifies minority SHA to majority
# ---------------------------------------------------------------------------


class TestFix:
    def test_fix_rewrites_minority_sha(self, tmp_path):
        # SHA_A appears twice, SHA_B once → SHA_B should be replaced with SHA_A.
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("c.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_B}
        """)
        pins = checker.collect_pins(tmp_path)
        n = checker.fix_inconsistencies(pins, workflows_dir=tmp_path, dry_run=False)
        assert n >= 1
        # Verify c.yml was rewritten.
        content = (tmp_path / "c.yml").read_text()
        assert SHA_B not in content
        assert SHA_A in content

    def test_fix_dry_run_does_not_modify_files(self, tmp_path):
        _make_workflow("a.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        _make_workflow("b.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_B}
        """)
        original = (tmp_path / "b.yml").read_text()
        pins = checker.collect_pins(tmp_path)
        checker.fix_inconsistencies(pins, workflows_dir=tmp_path, dry_run=True)
        # File should be untouched.
        assert (tmp_path / "b.yml").read_text() == original

    def test_fix_no_changes_when_already_consistent(self, tmp_path):
        _make_workflow("w.yml", tmp_path, f"""\
            steps:
              - uses: actions/checkout@{SHA_A}
        """)
        pins = checker.collect_pins(tmp_path)
        n = checker.fix_inconsistencies(pins, workflows_dir=tmp_path, dry_run=False)
        assert n == 0
