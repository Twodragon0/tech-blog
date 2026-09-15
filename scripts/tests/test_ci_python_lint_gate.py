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
OPS_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ops-orchestrator.yml"


def _ruff_pins(text: str) -> set[str]:
    """Every pinned ruff version in a workflow, ignoring whole-line comments.

    The comments in both workflows name the pinned version while explaining why
    it is pinned, and a matcher that reads those would call an unpinned install
    compliant — the exact direction of failure this guard exists to catch.
    """
    return set(re.findall(r"ruff==(\d+\.\d+\.\d+)", _code_lines(text)))


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


class TestBothRuffGatesRunTheSameVersion:
    """The PR gate and the ops loop share a verdict, so they must share a ruff.

    Since 2026-08-28 ``check_lint_and_types`` derives ``ok`` from
    ``ruff format --check scripts/`` and python-lint.yml runs the same command
    blocking. Two gates enforcing one rule with two rulesets do not agree, and
    the disagreement surfaces on whichever one happens to run first.

    Pinning python-lint.yml alone was not enough, which is how this was found:
    ops-orchestrator.yml installed ruff unpinned, resolved to 0.16 — which
    formats Python inside Markdown, a thing 0.15.8 does not do — and failed on
    scripts/AGENTS.md, untouched since 2026-04-08, while the PR gate reported
    389 files clean.

    Direction: equality. A deliberate bump must move BOTH files in one PR.
    """

    def test_ops_workflow_exists(self):
        assert OPS_WORKFLOW.is_file(), f"{OPS_WORKFLOW} not found"

    def test_ops_orchestrator_pins_ruff(self):
        pins = _ruff_pins(OPS_WORKFLOW.read_text(encoding="utf-8"))
        assert pins, (
            "ops-orchestrator.yml installs ruff unpinned. Its lint-and-types "
            "check is the only check that can fail that run, so an upstream "
            "ruff release turns main red for code nobody wrote — and it did, "
            "on 2026-08-31."
        )

    def test_every_ruff_install_in_ops_is_pinned(self):
        """One unpinned install among three is still an unpinned gate."""
        code = _code_lines(OPS_WORKFLOW.read_text(encoding="utf-8"))
        installs = re.findall(r"pip install[^\n]*\bruff\b[^\n]*", code)
        assert installs, "ops-orchestrator.yml no longer installs ruff at all."
        unpinned = [line for line in installs if "ruff==" not in line]
        assert not unpinned, (
            f"ops-orchestrator.yml still installs ruff unpinned: {unpinned}. "
            "The workflow has three jobs that install it; pinning only the one "
            "that happens to be red leaves the next one to find the same skew."
        )

    def test_the_two_gates_agree_on_the_version(self):
        pr_gate = _ruff_pins(WORKFLOW.read_text(encoding="utf-8"))
        ops = _ruff_pins(OPS_WORKFLOW.read_text(encoding="utf-8"))
        assert pr_gate == ops, (
            f"ruff version skew: python-lint.yml pins {sorted(pr_gate)}, "
            f"ops-orchestrator.yml pins {sorted(ops)}. They enforce the same "
            "`ruff format --check scripts/` rule, so one of them is now failing "
            "on a rule the other does not have. Bump both in the same PR, and "
            "run `ruff format scripts/` with the new version before doing so."
        )

    def test_a_single_version_is_pinned_within_each_file(self):
        """Two pins in one file is the same skew, one directory deeper."""
        for path in (WORKFLOW, OPS_WORKFLOW):
            pins = _ruff_pins(path.read_text(encoding="utf-8"))
            assert len(pins) <= 1, (
                f"{path.name} pins more than one ruff version: {sorted(pins)}. "
                "Its jobs would lint the same tree against different rulesets."
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


REQUIREMENTS = (
    REPO_ROOT / "scripts" / "requirements-ci.txt",
    REPO_ROOT / "requirements-blogwatcher.txt",
)

_RUFF_DECL_RE = re.compile(r"^\s*ruff\s*(==|>=|>)\s*(\d+\.\d+\.\d+)\s*$", re.M)


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


def _ruff_declarations() -> dict[Path, tuple[str, str]]:
    """``{path: (operator, version)}`` for every file that declares ruff."""
    out: dict[Path, tuple[str, str]] = {}
    for path in REQUIREMENTS:
        m = _RUFF_DECL_RE.search(path.read_text(encoding="utf-8"))
        if m:
            out[path] = (m.group(1), m.group(2))
    return out


class TestThePinSatisfiesTheDeclaration:
    """There is a THIRD ruff, and for 18 days nothing compared it to the others.

    ``TestBothRuffGatesRunTheSameVersion`` above pins python-lint.yml against
    ops-orchestrator.yml. Neither is the only ruff in CI:
    ``scripts/requirements-ci.txt`` declares one too, and jekyll.yml and
    svg-lint.yml install it into the jobs that run pytest — where
    ``test_ci_python_syntax_floor_guard.py`` shells out to ``ruff`` by name.
    ``requirements-blogwatcher.txt`` declares the same for the publish path.

    Measured 2026-09-15: both files said ``ruff>=0.16.6`` while all four
    workflow sites pinned ``ruff==0.15.8`` — **a version that does not satisfy
    the declaration they sit next to**. Nothing objected, because the existing
    class compares the two workflows to each other and stops there. The cost was
    real and was paid in this repo: a local ``ruff format --check`` run using the
    declared version reported a file clean that the pinned version in CI wanted
    reformatted, so a PR went red for a file its author had already formatted.

    Direction: containment, not equality. The declarations are ``>=`` and
    dependabot maintains them; the workflows pin an exact version. The invariant
    is that the pin lies inside the declared range — so bumping the declaration
    without moving the pin fails here, loudly, with the four line numbers to fix.
    """

    def test_both_requirements_files_declare_ruff(self):
        """Canary: if a declaration is dropped, this class must not go quiet."""
        found = _ruff_declarations()
        missing = [p.name for p in REQUIREMENTS if p not in found]
        assert not missing, (
            f"no parseable `ruff` declaration in {missing}. Either the pin is no "
            "longer compared against anything, or the declaration uses a "
            "specifier this guard cannot read — add it to _RUFF_DECL_RE rather "
            "than letting the check pass vacuously."
        )

    def test_the_workflow_pin_satisfies_every_declaration(self):
        pins = _ruff_pins(WORKFLOW.read_text(encoding="utf-8")) | _ruff_pins(
            OPS_WORKFLOW.read_text(encoding="utf-8")
        )
        assert pins, "no pinned ruff to compare — see test_ruff_is_version_pinned."

        for path, (op, declared) in _ruff_declarations().items():
            for pin in sorted(pins):
                ok = {
                    "==": _version(pin) == _version(declared),
                    ">=": _version(pin) >= _version(declared),
                    ">": _version(pin) > _version(declared),
                }[op]
                assert ok, (
                    f"{path.name} declares `ruff{op}{declared}` but the workflows "
                    f"pin `ruff=={pin}`, which does not satisfy it. CI then runs "
                    "two different ruffs: the pinned one in the lint gate, the "
                    "declared one in the pytest jobs that shell out to `ruff`. "
                    "Move all four `ruff==` sites in python-lint.yml and "
                    "ops-orchestrator.yml to a version inside the declared range, "
                    "and run `ruff format scripts/` with it before doing so."
                )

    def test_the_declarations_agree_with_each_other(self):
        decls = _ruff_declarations()
        distinct = {spec for spec in decls.values()}
        assert len(distinct) <= 1, (
            f"the two requirements files declare different ruffs: "
            f"{ {p.name: s for p, s in decls.items()} }. The publish path and the "
            "test path would then lint with different rulesets."
        )
