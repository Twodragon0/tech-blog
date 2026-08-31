#!/usr/bin/env python3
"""Unit tests for the actionlint info/style ratchet.

The property that matters most here is **position insensitivity**. actionlint
embeds two line:col pairs in every shellcheck finding — one for the `run:` block
in the workflow, one for the offending line inside the script. A ratchet keyed
on the message text therefore fails whenever anything above a finding is edited,
which is the false block `check_digest_structure.py` already had to be rescued
from in PR #492 (there the message embedded body *text* rather than positions).

So `test_position_shift_does_not_change_counts` is not a nicety: it is the
regression test for the design decision, and it uses two real actionlint lines
that differ only in position.

Fixtures are captured actionlint output, never a live invocation — the binary is
not present in every environment that runs pytest, and a test that silently
skips is a test nobody notices has stopped running.
"""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_actionlint_ratchet.py"
REAL_BASELINE = REPO_ROOT / "scripts" / "actionlint_ratchet_baseline.txt"


def _load():
    spec = importlib.util.spec_from_file_location("check_actionlint_ratchet", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


mod = _load()


def _finding(path: str, wf_line: int, code: str, severity: str, sc_line: int) -> str:
    """One actionlint finding line, in the real output format."""
    return (
        f"{path}:{wf_line}:9: shellcheck reported issue in this script: "
        f"{code}:{severity}:{sc_line}:25: Double quote to prevent globbing and "
        f"word splitting [shellcheck]"
    )


# Captured verbatim from actionlint 1.7.12 + shellcheck 0.11.0 on 2026-08-27,
# including the indented source-snippet lines it interleaves between findings.
REAL_OUTPUT = """\
.github/workflows/lighthouse.yml:58:9: shellcheck reported issue in this script: SC2086:info:2:25: Double quote to prevent globbing and word splitting [shellcheck]
   |
58 |         run: |
   |         ^~~~
.github/workflows/security-audit.yml:120:9: shellcheck reported issue in this script: SC2129:style:4:1: Consider using { cmd1; cmd2; } >> file instead of individual redirects [shellcheck]
   |
120 |         run: |
   |         ^~~~
"""


class TestParsing:
    def test_extracts_file_code_and_severity(self):
        counts = mod.parse_findings(REAL_OUTPUT)
        assert counts == Counter(
            {
                (".github/workflows/lighthouse.yml", "SC2086", "info"): 1,
                (".github/workflows/security-audit.yml", "SC2129", "style"): 1,
            }
        )

    def test_source_snippet_lines_are_not_counted(self):
        """`58 |         run: |` and `   |         ^~~~` must not match."""
        snippets = "\n".join(
            ln for ln in REAL_OUTPUT.splitlines() if "shellcheck reported" not in ln
        )
        assert mod.parse_findings(snippets) == Counter()

    def test_gated_severities_are_excluded(self):
        """warning/error belong to the blocking gate, not to this ratchet."""
        out = "\n".join(
            [
                _finding(".github/workflows/a.yml", 10, "SC2034", "warning", 3),
                _finding(".github/workflows/a.yml", 20, "SC1090", "error", 4),
                _finding(".github/workflows/a.yml", 30, "SC2086", "info", 5),
            ]
        )
        assert mod.parse_findings(out) == Counter(
            {(".github/workflows/a.yml", "SC2086", "info"): 1}
        )

    def test_native_actionlint_findings_are_not_counted(self):
        """Only shellcheck output is ratcheted; native rules already gate."""
        native = (
            '.github/workflows/a.yml:12:5: property "post_file" is not defined in '
            "object type {} [expression]"
        )
        assert mod.parse_findings(native) == Counter()

    def test_repeated_findings_accumulate(self):
        out = "\n".join(
            _finding(".github/workflows/a.yml", 10, "SC2086", "info", n)
            for n in (1, 2, 3)
        )
        assert (
            mod.parse_findings(out)[(".github/workflows/a.yml", "SC2086", "info")] == 3
        )


class TestPositionInsensitivity:
    def test_position_shift_does_not_change_counts(self):
        """The whole reason the key is not the message string.

        Measured on the real corpus: prepending one irrelevant comment line to
        lighthouse.yml moved its finding from 58:9 to 59:9 while the shell
        script stayed byte-identical.
        """
        before = _finding(".github/workflows/lighthouse.yml", 58, "SC2086", "info", 2)
        after = _finding(".github/workflows/lighthouse.yml", 59, "SC2086", "info", 2)

        assert before != after, (
            "the fixture must actually differ, or this proves nothing"
        )
        assert mod.parse_findings(before) == mod.parse_findings(after)
        assert mod.compare(mod.parse_findings(after), mod.parse_findings(before)) == (
            [],
            [],
        )

    def test_shifting_the_script_relative_position_also_does_not_matter(self):
        a = _finding(".github/workflows/a.yml", 10, "SC2086", "info", 2)
        b = _finding(".github/workflows/a.yml", 10, "SC2086", "info", 40)
        assert mod.parse_findings(a) == mod.parse_findings(b)


class TestCompare:
    KEY = (".github/workflows/a.yml", "SC2086", "info")

    def test_equal_counts_are_clean(self):
        assert mod.compare(Counter({self.KEY: 5}), Counter({self.KEY: 5})) == ([], [])

    def test_more_findings_is_a_regression(self):
        regressions, stale = mod.compare(Counter({self.KEY: 6}), Counter({self.KEY: 5}))
        assert stale == []
        assert len(regressions) == 1 and "5 -> 6" in regressions[0]

    def test_fewer_findings_is_a_stale_baseline(self):
        regressions, stale = mod.compare(Counter({self.KEY: 3}), Counter({self.KEY: 5}))
        assert regressions == []
        assert len(stale) == 1 and "5 -> 3" in stale[0]

    def test_a_wholly_new_key_is_a_regression(self):
        regressions, _ = mod.compare(Counter({self.KEY: 1}), Counter())
        assert len(regressions) == 1 and "0 -> 1" in regressions[0]

    def test_a_vanished_key_is_stale_not_silent(self):
        """Deleting a workflow must force the baseline to be regenerated."""
        _, stale = mod.compare(Counter(), Counter({self.KEY: 2}))
        assert len(stale) == 1 and "2 -> 0" in stale[0]

    def test_same_code_in_a_different_file_is_not_offset(self):
        """Fixing one file and breaking another must not net to zero."""
        other = (".github/workflows/b.yml", "SC2086", "info")
        regressions, stale = mod.compare(Counter({other: 1}), Counter({self.KEY: 1}))
        assert len(regressions) == 1 and len(stale) == 1


class TestBaselineFile:
    def test_round_trip(self, tmp_path):
        counts = Counter(
            {
                (".github/workflows/a.yml", "SC2086", "info"): 18,
                (".github/workflows/b.yml", "SC2129", "style"): 1,
            }
        )
        path = tmp_path / "baseline.txt"
        path.write_text(mod.render_baseline(counts), encoding="utf-8")
        assert mod.load_baseline(path) == counts

    def test_comments_and_blank_lines_are_ignored(self, tmp_path):
        path = tmp_path / "baseline.txt"
        path.write_text(
            "# a comment\n\n.github/workflows/a.yml SC2086 info 2\n\n", encoding="utf-8"
        )
        assert mod.load_baseline(path) == Counter(
            {(".github/workflows/a.yml", "SC2086", "info"): 2}
        )

    def test_malformed_entry_is_fatal_not_skipped(self, tmp_path):
        """A silently dropped line would lower the effective baseline."""
        path = tmp_path / "baseline.txt"
        path.write_text(".github/workflows/a.yml SC2086 info\n", encoding="utf-8")
        with pytest.raises(EnvironmentError, match="malformed"):
            mod.load_baseline(path)

    def test_missing_baseline_is_fatal(self, tmp_path):
        with pytest.raises(EnvironmentError, match="not found"):
            mod.load_baseline(tmp_path / "nope.txt")

    def test_the_committed_baseline_parses(self):
        counts = mod.load_baseline(REAL_BASELINE)
        assert counts, (
            "the committed baseline is empty — the ratchet would enforce nothing"
        )
        for _path, code, severity in counts:
            assert code.startswith("SC")
            assert severity in mod.RATCHETED_SEVERITIES, (
                f"{severity!r} is in the baseline but not in RATCHETED_SEVERITIES, so "
                "parse_findings can never produce it and the entry is dead weight "
                "that permanently reads as stale"
            )

    def test_committed_baseline_references_existing_workflows(self):
        for path, _code, _sev in mod.load_baseline(REAL_BASELINE):
            assert (REPO_ROOT / path).is_file(), (
                f"{path} is in the baseline but not in the repo. Regenerate with "
                "--update; a baseline citing a deleted file is permanently stale."
            )


class TestMainExitCodes:
    def _write(self, tmp_path, text: str) -> Path:
        p = tmp_path / "out.txt"
        p.write_text(text, encoding="utf-8")
        return p

    def test_clean_run_exits_zero(self, tmp_path):
        out = self._write(
            tmp_path, _finding(".github/workflows/a.yml", 1, "SC2086", "info", 1)
        )
        base = tmp_path / "b.txt"
        base.write_text(".github/workflows/a.yml SC2086 info 1\n", encoding="utf-8")
        assert mod.main(["--from-file", str(out), "--baseline", str(base)]) == 0

    def test_regression_exits_one(self, tmp_path):
        out = self._write(
            tmp_path,
            "\n".join(
                _finding(".github/workflows/a.yml", 1, "SC2086", "info", n)
                for n in (1, 2)
            ),
        )
        base = tmp_path / "b.txt"
        base.write_text(".github/workflows/a.yml SC2086 info 1\n", encoding="utf-8")
        assert mod.main(["--from-file", str(out), "--baseline", str(base)]) == 1

    def test_missing_baseline_exits_two(self, tmp_path):
        out = self._write(tmp_path, "")
        assert (
            mod.main(
                ["--from-file", str(out), "--baseline", str(tmp_path / "nope.txt")]
            )
            == 2
        )

    def test_update_writes_a_baseline_that_then_passes(self, tmp_path):
        out = self._write(
            tmp_path, _finding(".github/workflows/a.yml", 1, "SC2086", "info", 1)
        )
        base = tmp_path / "b.txt"
        assert (
            mod.main(["--from-file", str(out), "--baseline", str(base), "--update"])
            == 0
        )
        assert mod.main(["--from-file", str(out), "--baseline", str(base)]) == 0


class TestEnvironmentIsFailClosed:
    """A missing analyzer must never be reported as "zero findings"."""

    def test_missing_shellcheck_raises(self, monkeypatch):
        monkeypatch.setattr(
            mod.shutil,
            "which",
            lambda name: None if name == "shellcheck" else "/usr/bin/actionlint",
        )
        with pytest.raises(EnvironmentError, match="shellcheck"):
            mod.run_actionlint()

    def test_missing_actionlint_raises(self, monkeypatch):
        monkeypatch.setattr(mod.shutil, "which", lambda name: None)
        with pytest.raises(EnvironmentError, match="actionlint"):
            mod.run_actionlint()

    @pytest.mark.parametrize("rc", [2, 3])
    def test_non_result_exit_codes_raise(self, monkeypatch, rc):
        """rc=3 is "no project was found" — it parses to zero findings.

        This is not hypothetical: a probe harness for this very script hit rc=3
        by running actionlint outside a git repository, and the empty output
        read as "baseline stale" rather than "the tool did not run".
        """
        monkeypatch.setattr(mod.shutil, "which", lambda name: f"/usr/bin/{name}")

        class _Proc:
            returncode = rc
            stdout = ""
            stderr = "no project was found in any parent directories"

        monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _Proc())
        with pytest.raises(EnvironmentError, match=f"exited {rc}"):
            mod.run_actionlint()

    @pytest.mark.parametrize("rc", [0, 1])
    def test_result_exit_codes_are_accepted(self, monkeypatch, rc):
        monkeypatch.setattr(mod.shutil, "which", lambda name: f"/usr/bin/{name}")

        class _Proc:
            returncode = rc
            stdout = _finding(".github/workflows/a.yml", 1, "SC2086", "info", 1)
            stderr = ""

        monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _Proc())
        assert mod.parse_findings(mod.run_actionlint())
