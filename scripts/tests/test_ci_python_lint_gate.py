#!/usr/bin/env python3
"""CI regression guard: ruff must actually run, on pull requests, without --fix.

Two independent defects let PR #629 land an ``I001`` violation on main unremarked
on 2026-08-27, and either one alone is enough to make the lint gate decorative:

1. **Wrong trigger.** ruff existed only inside ``ops-orchestrator.yml``, whose
   ``on:`` is schedule / workflow_dispatch / repository_dispatch. No pull request
   has ever been linted by it.
2. **Self-repairing check.** ``check_lint_and_types`` ran ``ruff check --fix``
   and ``ruff format`` — both mutating — *before* its verification pass, and
   ``ok`` was derived from that verification. Every auto-fixable rule, which is
   most of them and all of the ``I`` isort family, was repaired in the ephemeral
   runner and then found clean. The workflow commits nothing, so the repair was
   discarded and the violation stayed on main. Nine had accumulated by the time
   anyone looked.

A check that fixes the thing it is about to inspect reports on the fix, not on
the repository. That is the invariant this guard pins.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control). Direction: presence for the
trigger and the blocking invocation, absence for the mutating flags. If any of it
is reworked intentionally, update this guard in the same PR and say why.

Note on matching: the assertions below target *invocations*, not prose. The
docstrings and comments in ops_health_orchestrator.py legitimately mention
``--fix`` while describing why it was removed, and a guard that greps the file
for the bare string would fail on its own explanation.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "python-lint.yml"
ORCHESTRATOR = REPO_ROOT / "scripts" / "ops_health_orchestrator.py"


def _code_lines(text: str) -> str:
    """Drop whole-line comments so prose about a flag is not read as using it."""
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


class TestPullRequestLintWorkflow:
    @classmethod
    def _doc(cls) -> dict:
        return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))

    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), (
            f"{WORKFLOW} is gone. Nothing else in this repo runs ruff on a pull "
            "request, so removing it restores the 2026-08-27 gap wholesale."
        )

    def test_runs_on_pull_request(self):
        doc = self._doc()
        on = doc.get(True) if doc.get(True) is not None else doc.get("on")
        assert isinstance(on, dict) and "pull_request" in on, (
            f"python-lint.yml triggers are {sorted(on) if isinstance(on, dict) else on}. "
            "Without pull_request this is ops-orchestrator's problem again: a lint "
            "job that never sees the change it is supposed to gate."
        )

    def test_pull_request_has_no_paths_filter(self):
        """A path-filtered required check reports as skipped, never as passed.

        Deliberate choice, not an oversight — the job is ~30s and this repo has
        already been bitten by a path filter concealing a red state.
        """
        doc = self._doc()
        on = doc.get(True) if doc.get(True) is not None else doc.get("on")
        pr = on["pull_request"]
        if isinstance(pr, dict):
            assert "paths" not in pr and "paths-ignore" not in pr, (
                "python-lint.yml's pull_request trigger grew a path filter. If "
                "that is intentional, confirm the check is not required by branch "
                "protection first — a skipped required check blocks merges."
            )

    def test_ruff_check_runs_and_is_not_self_repairing(self):
        steps = self._doc()["jobs"]["ruff"]["steps"]
        blocking = [
            s
            for s in steps
            if "ruff check" in str(s.get("run", ""))
            and not s.get("continue-on-error", False)
        ]
        assert blocking, (
            "no blocking `ruff check` step remains in python-lint.yml. A lint "
            "workflow whose only ruff step is continue-on-error cannot fail."
        )
        for step in blocking:
            assert "--fix" not in str(step["run"]), (
                "the blocking ruff step passes --fix. It would then repair the "
                "violation and report on the repair — exactly the defect this "
                "workflow was created to replace."
            )

    def test_format_check_is_blocking(self):
        """Promoted from advisory on 2026-08-28, once the backlog was cleared.

        It shipped with ``continue-on-error: true`` for one stated reason: 25
        files under scripts/ were already drifted. Those were reformatted in the
        promoting commit, so the exemption has no remaining justification — and
        an advisory check kept past its reason is a slower way of not checking.
        Re-adding the flag here silently restores that state, so it fails.
        """
        steps = self._doc()["jobs"]["ruff"]["steps"]
        fmt = [s for s in steps if "ruff format" in str(s.get("run", ""))]
        assert fmt, "python-lint.yml no longer runs `ruff format --check` at all."
        for step in fmt:
            assert not step.get("continue-on-error", False), (
                "the ruff format step is continue-on-error again. If the backlog "
                "genuinely came back, say so and record the count — do not "
                "reinstate a permanent exemption for a temporary condition."
            )
            assert "--check" in str(step["run"]), (
                "the ruff format step dropped --check, so it now rewrites files "
                "in the runner instead of reporting on them. Nothing commits "
                "here, so the rewrite is discarded and the step always passes."
            )

    def test_ruff_is_version_pinned(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        assert re.search(r"ruff==\d+\.\d+\.\d+", text), (
            "ruff is no longer version-pinned in python-lint.yml. An unpinned "
            "ruff adds rules between releases and fails a PR for code its author "
            "did not write."
        )


class TestOrchestratorDoesNotRepairBeforeVerifying:
    @classmethod
    def _code(cls) -> str:
        return _code_lines(ORCHESTRATOR.read_text(encoding="utf-8"))

    def test_orchestrator_exists(self):
        assert ORCHESTRATOR.is_file(), f"{ORCHESTRATOR} not found"

    def test_no_autofix_invocation(self):
        hits = re.findall(r"run_command\(\[[^\]]*--fix[^\]]*\]", self._code())
        assert not hits, (
            f"ops_health_orchestrator invokes ruff with --fix again: {hits}. "
            "The verification that follows then measures the fixed tree, `ok` "
            "cannot go False for any auto-fixable rule, and since nothing here "
            "commits, the repair is discarded and main keeps the violation."
        )

    def test_format_is_check_only(self):
        """`ruff format scripts/` rewrites files; `--check` only reports."""
        # The lookahead sits *before* the whitespace on purpose. With
        # `\s*(?!"--check")` the star backtracks to zero width, the lookahead
        # then inspects the space rather than the flag, and the pattern matches
        # the compliant line — a guard that fails on correct code, which is how
        # this was caught.
        mutating = re.findall(
            r'run_command\(\[\s*"ruff",\s*"format",(?!\s*"--check")', self._code()
        )
        assert not mutating, (
            "ops_health_orchestrator runs `ruff format` without --check. That "
            "rewrites scripts/ inside the runner, and because the workflow does "
            "not commit, the only lasting effect is that the following check "
            "sees a tree that does not exist anywhere else."
        )

    def test_lint_verdict_still_derives_from_the_verification(self):
        code = self._code()
        assert "ok = lint_verify.ok and format_check.ok" in code, (
            "check_lint_and_types no longer derives `ok` from both the ruff "
            "check and the format check. Dropping `format_check.ok` returns "
            "format drift to advisory in the ops loop while the PR gate still "
            "blocks it — two gates disagreeing about the same rule is how a "
            "violation ends up on main with a green tick somewhere to point at."
        )
