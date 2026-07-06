#!/usr/bin/env python3
"""CI regression guard: the pytest gate that enforces the digest-KPI fallback must stay live.

Why this guard exists
---------------------
Early digests (Jan–early-Feb) carry a 5-column highlights table (the legacy
``분야|소스|핵심내용|영향도|긴급도`` form). The shared 4-cell panel parser
``_digest_table_panels`` *silently* bails on that form (returns ``[]``), which is
exactly what left those digests' KPI cards showing ``TBD``. The fix
(``scripts/news/l20_dispatch.py`` :func:`_digest_table_counts`) is column-flexible
(``>= 3`` cells) so it reads both the 4- and 5-column tables, and its behaviour is
locked by the unit tests in ``test_l20_realcontent.py`` —
``TestDigestTableCounts::test_counts_5col_legacy_table`` (the counter must read the
5-col form) and ``::test_panel_parser_untouched_by_counter`` (the count-only helper
must not perturb panel/visual routing, keeping the honesty scorer invariant).

Those unit tests only protect against regression *while they actually run in CI*.
The CORPUS-LEVEL enforcement is the ``Run script unit tests`` step in
``.github/workflows/jekyll.yml``: it runs ``pytest scripts/tests/`` under a
``--cov-fail-under`` floor. That protection disappears *silently* if someone drops
the pytest step, stops pointing it at ``scripts/tests/``, lowers/removes the
coverage floor, marks the step ``continue-on-error``, or neutralises it with
``|| true`` — and the 5-column silent-break could then re-enter undetected. This
guard makes any such weakening fail loudly and reviewably. A behavioural canary
also trips if the specific 5-col regression test is renamed/deleted.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control). Direction: the coverage
floor is a ratchet (``>=`` 40 — raising it stays green); the pytest invocation and
the regression test are presence assertions — any removal trips. If a change here
is intentional, update this guard in the same PR and say why.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"
REGRESSION_TEST = REPO_ROOT / "scripts" / "tests" / "test_l20_realcontent.py"

# The coverage floor that gates ``scripts/tests/`` today. The guard asserts the
# floor is never LOWERED below this; raising it (and bumping this constant in the
# same PR) is the intended ratchet direction.
MIN_COV_FLOOR = 40


def _unit_test_step_block(text: str) -> str:
    """Return the YAML lines of the ``Run script unit tests`` step block.

    Spans from that ``- name:`` line to the next sibling ``- name:`` step at the
    same indent (or EOF). Returns ``""`` when the step is absent.
    """
    lines = text.splitlines()
    start = next(
        (
            i
            for i, ln in enumerate(lines)
            if re.match(r"\s*-\s+name:\s*Run script unit tests\b", ln)
        ),
        None,
    )
    if start is None:
        return ""
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        ln = lines[end]
        if re.match(r"\s*-\s+name:", ln) and (len(ln) - len(ln.lstrip())) == indent:
            break
        end += 1
    return "\n".join(lines[start:end])


def _should_build_paths_block(text: str) -> str:
    """Return the YAML lines of the ``should-build:`` paths-filter list.

    Spans from the ``should-build:`` key to the next line at the same-or-shallower
    indent (or EOF). Returns ``""`` when the key is absent. This is the
    dorny/paths-filter list that decides whether the build job (and thus the
    pytest step) runs on a ``push``.
    """
    lines = text.splitlines()
    start = next(
        (i for i, ln in enumerate(lines) if re.match(r"\s*should-build:\s*$", ln)),
        None,
    )
    if start is None:
        return ""
    indent = len(lines[start]) - len(lines[start].lstrip())
    end = start + 1
    while end < len(lines):
        ln = lines[end]
        if ln.strip() and (len(ln) - len(ln.lstrip())) <= indent:
            break
        end += 1
    return "\n".join(lines[start:end])


def _command_text(block: str) -> str:
    """The step block with comment-only lines removed.

    Asserting on the executable command (not surrounding comments) keeps the
    guard honest: a stale comment mentioning ``--cov-fail-under`` must not keep it
    green after the real flag is deleted. (Skill rule: never match commentary.)
    """
    return "\n".join(
        ln for ln in block.splitlines() if not ln.lstrip().startswith("#")
    )


class TestDigestKpiGateGuard:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_regression_test_file_exists(self):
        assert REGRESSION_TEST.is_file(), (
            f"{REGRESSION_TEST} not found — the 5-column table KPI-fallback "
            "regression tests must exist; if relocated, update this guard."
        )

    def test_unit_test_step_present(self):
        block = _unit_test_step_block(WORKFLOW.read_text(encoding="utf-8"))
        assert block, (
            "The 'Run script unit tests' step disappeared from jekyll.yml. That "
            "step is what runs the digest-KPI 5-column regression tests in CI; "
            "without it the silent-break could re-enter undetected. If "
            "intentional, update this guard."
        )

    def test_step_runs_pytest_over_scripts_tests(self):
        cmd = _command_text(
            _unit_test_step_block(WORKFLOW.read_text(encoding="utf-8"))
        )
        assert "pytest" in cmd, "pytest no longer invoked in the unit-test step"
        assert "scripts/tests/" in cmd, (
            "the pytest invocation no longer targets scripts/tests/; the "
            "digest-KPI regression tests would stop running in CI."
        )

    def test_coverage_floor_not_lowered(self):
        cmd = _command_text(
            _unit_test_step_block(WORKFLOW.read_text(encoding="utf-8"))
        )
        floors = re.findall(r"--cov-fail-under=(\d+)", cmd)
        assert floors, (
            "--cov-fail-under was removed from the unit-test step; the coverage "
            "floor gating scripts/tests/ is gone. If intentional, update this guard."
        )
        assert min(int(f) for f in floors) >= MIN_COV_FLOOR, (
            f"the coverage floor was lowered below {MIN_COV_FLOOR}; raising it is "
            "fine (bump MIN_COV_FLOOR in the same PR), lowering it weakens the gate."
        )

    def test_step_not_neutralized(self):
        block = _unit_test_step_block(WORKFLOW.read_text(encoding="utf-8"))
        cmd = _command_text(block)
        assert "continue-on-error: true" not in block, (
            "the unit-test step is marked continue-on-error; a test FAIL would no "
            "longer block the build."
        )
        assert "|| true" not in cmd, (
            "the pytest run is neutralised with '|| true'; a FAIL would be swallowed."
        )

    def test_pytest_triggered_on_python_only_push(self):
        """The build job's paths-filter must trigger on Python-only pushes.

        The 'Run script unit tests' step existing is necessary but not
        sufficient: on ``push`` the build job runs only when
        ``check-changes.should-build`` is true, which is decided by the
        dorny/paths-filter ``should-build:`` list. If that list omits a
        Python-covering glob, a push that touches ONLY ``scripts/**`` skips the
        build job entirely and pytest never runs — the cover dedup/lone-word,
        digest-KPI and honesty-replay regressions could then merge green
        (GAP-5, 2026-07-06 cover-invariant guard audit). PRs are unaffected
        (the build job runs unconditionally on pull_request), so this closes the
        direct-push hole specifically.

        Presence assertion: any glob that matches ``.py`` files satisfies it
        (``**/*.py`` today; ``scripts/**`` would also qualify). If the trigger is
        intentionally reworked, update this guard in the same PR.
        """
        block = _should_build_paths_block(WORKFLOW.read_text(encoding="utf-8"))
        assert block, (
            "the should-build paths-filter list disappeared from jekyll.yml; the "
            "build job trigger can no longer be reasoned about. If intentional, "
            "update this guard."
        )
        entries = [
            ln.strip().lstrip("-").strip().strip("'\"")
            for ln in block.splitlines()
            if ln.lstrip().startswith("-")
        ]
        covers_python = any(
            e.endswith("*.py") or e in ("scripts/**", "**scripts/**", "**/scripts/**")
            for e in entries
        )
        assert covers_python, (
            "the should-build paths-filter no longer matches Python changes "
            f"(entries: {entries}). A push touching only scripts/** would skip the "
            "build job, so the script unit tests would not run in CI on direct "
            "pushes. Re-add a Python glob (e.g. '**/*.py' or 'scripts/**'); if "
            "intentional, update this guard."
        )

    def test_five_column_regression_test_named(self):
        """Behavioural canary: the specific 5-col regression test must still exist.

        Locks the named tests so a rename/delete trips here loudly instead of the
        invariant silently going unprotected. (See module docstring.)
        """
        src = REGRESSION_TEST.read_text(encoding="utf-8")
        assert "def test_counts_5col_legacy_table" in src, (
            "test_counts_5col_legacy_table was removed/renamed — the 5-column "
            "table read invariant is no longer guarded. If intentional, update "
            "this guard."
        )
        assert "def test_panel_parser_untouched_by_counter" in src, (
            "test_panel_parser_untouched_by_counter was removed/renamed — the "
            "count-only helper's honesty-safety (no panel/routing perturbation) "
            "is no longer guarded. If intentional, update this guard."
        )
