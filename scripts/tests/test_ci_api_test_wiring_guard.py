#!/usr/bin/env python3
"""CI regression guard: the api/ suite must stay wired to a runner and to CI.

`api/__tests__/` has existed since March 2026 with 77 passing assertions covering
the rate limiter, the log sanitizer and `sanitizeInput`. Until 2026-08-18 it had
**never executed**, in CI or anywhere else, for two independent reasons:

1. Those files `import { test } from 'node:test'`, but the only configured runner
   was Vitest, whose `include` is `tests/js/**`. Adding `api/__tests__/**` to that
   include would not have helped — Vitest cannot run `node:test` files. They needed
   `node --test`, which nothing invoked.
2. `vitest.yml` did not list `api/**` in either path filter, so a change under
   `api/` triggered no JS gate at all.

A suite that never runs is worse than no suite: it reads as coverage in the tree
and reviewers count on it. This guard pins the wiring so it cannot be dropped
back to decorative.

It also pins that `sanitize.test.js` imports the real `sanitizeInput` from
`api/chat.js`. That file used to hold a hand-copied mirror of the function body,
which meant the assertions could stay green while the shipped sanitizer
regressed — verified: mutating `api/chat.js` to stop escaping `<` fails a test
today, and would have failed nothing before the import was wired.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "vitest.yml"
PACKAGE_JSON = REPO_ROOT / "package.json"
API_TESTS = REPO_ROOT / "api" / "__tests__"
SANITIZE_TEST = API_TESTS / "sanitize.test.js"
CHAT = REPO_ROOT / "api" / "chat.js"


def _workflow() -> dict:
    import yaml

    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _scripts() -> dict:
    return json.loads(PACKAGE_JSON.read_text(encoding="utf-8")).get("scripts", {})


def _steps() -> list[dict]:
    return _workflow()["jobs"]["vitest"]["steps"]


def test_api_test_files_still_exist() -> None:
    """If these are gone the rest of the guard is vacuous, so assert it first."""
    found = sorted(p.name for p in API_TESTS.glob("*.test.js"))
    assert found, f"no *.test.js under {API_TESTS}"


def test_npm_exposes_a_runner_for_the_api_suite() -> None:
    script = _scripts().get("test:api")
    assert script, (
        "package.json lost the `test:api` script; the api/ suite has no runner"
    )
    assert "node --test" in script, (
        "`test:api` must invoke `node --test` — these files import from 'node:test' "
        f"and Vitest cannot execute them. Got: {script!r}"
    )
    assert "api/__tests__" in script, (
        f"`test:api` no longer targets api/__tests__: {script!r}"
    )


def test_ci_actually_runs_the_api_suite() -> None:
    runs = [str(s.get("run", "")) for s in _steps()]
    assert any("test:api" in r for r in runs), (
        "vitest.yml no longer runs `npm run test:api`; the api/ suite is back to "
        f"never executing. Steps: {runs}"
    )


def test_api_suite_step_is_not_soft() -> None:
    """A step that cannot fail the job is the same as no step."""
    for step in _steps():
        if "test:api" in str(step.get("run", "")):
            assert not step.get("continue-on-error"), (
                "the api/ suite step is marked continue-on-error, so a failure "
                "would not block the PR"
            )
            assert "|| true" not in str(step["run"]), (
                "the api/ suite step swallows its exit code with `|| true`"
            )
            return
    pytest.fail("no step running test:api found")


def test_api_step_fails_when_zero_tests_are_collected() -> None:
    """`node --test <glob>` exits 0 on an empty match — measured 2026-08-21.

    A glob that matches nothing prints ``1..0 / # tests 0 / # pass 0`` and exits
    0, so renaming ``api/__tests__``, moving it, or changing the ``.test.js``
    suffix would leave the step green while running zero assertions. Vitest
    fails closed on an empty collection; node:test does not, so the floor has to
    live in the workflow step.
    """
    for step in _steps():
        run = str(step.get("run", ""))
        if "test:api" not in run:
            continue
        assert "# tests" in run, (
            "the api/ suite step no longer reads the collected-test count. "
            "Without it, a glob matching nothing exits 0 and this step passes "
            "having verified nothing (measured: `1..0`, `# tests 0`, exit 0)."
        )
        assert "exit 1" in run, (
            "the api/ suite step parses the test count but never fails on it; "
            "the check is decorative without a non-zero exit"
        )
        assert "set -o pipefail" in run, (
            "the api/ suite step pipes `npm run test:api` into tee without "
            "`set -o pipefail`, so a failing suite is masked by tee's exit code "
            "— the count check would then be the only thing that can fail"
        )
        return
    pytest.fail("no step running test:api found")


def test_api_test_files_are_not_empty_shells() -> None:
    """A file with zero `test()` calls counts as ONE passing test.

    Measured 2026-08-21: `node --test` on a file containing no `test()` call
    reports ``# tests 1 / # pass 1`` and exits 0 — it wraps the file itself as a
    single vacuous test. So the ``# tests >= 1`` floor in the workflow step
    cannot see this case: four emptied files would report ``# tests 4`` and pass.

    Only a static check distinguishes them, so the content assertion lives here
    rather than in the runner. `test_api_test_files_still_exist` above checks
    that the files are present; this checks they still contain tests.
    """
    empty = []
    for path in sorted(API_TESTS.glob("*.test.js")):
        source = path.read_text(encoding="utf-8")
        if "test(" not in source:
            empty.append(path.name)
    assert not empty, (
        f"api test file(s) with no `test(` call: {empty}. node --test reports "
        f"each such file as 1 passing test, so the suite would stay green while "
        f"asserting nothing. Restore the tests or delete the file."
    )


def test_vitest_ci_step_uses_the_coverage_gate() -> None:
    """The coverage flag is what makes a mass-skip fail — measured, not assumed.

    `vitest run` with every test filtered out reports ``698 skipped`` and exits
    **0**. The same run with ``--coverage`` exits **1**, because 0% trips the
    thresholds in vitest.config.js. CI therefore has to keep running the
    coverage script; switching the step to plain `npm test` would silently
    reopen the hole.
    """
    for step in _steps():
        run = str(step.get("run", ""))
        if "vitest" in run or "test:coverage" in run:
            assert "test:coverage" in run, (
                "the Vitest CI step no longer runs `npm run test:coverage`. Plain "
                "`vitest run` exits 0 when every test is skipped (measured: "
                "`698 skipped`, exit 0); only the coverage gate turns that red."
            )
            return
    pytest.fail("no step running vitest found in vitest.yml")


def test_vitest_coverage_thresholds_are_non_trivial() -> None:
    """Zeroed thresholds would neuter the gate the test above relies on."""
    config = (REPO_ROOT / "vitest.config.js").read_text(encoding="utf-8")
    found = dict(re.findall(r"(branches|functions|lines|statements):\s*(\d+)", config))
    missing = {"branches", "functions", "lines", "statements"} - set(found)
    assert not missing, (
        f"vitest.config.js lost coverage thresholds for: {sorted(missing)}"
    )
    zeroed = {k: v for k, v in found.items() if int(v) <= 0}
    assert not zeroed, (
        f"coverage threshold(s) set to zero: {zeroed}. A 0% floor cannot fail, "
        f"which is what a mass-skip regression produces — the gate would pass "
        f"with every test skipped."
    )


def test_vitest_still_fails_on_an_empty_collection() -> None:
    """`passWithNoTests` would give Vitest the same hole node:test has."""
    config = (REPO_ROOT / "vitest.config.js").read_text(encoding="utf-8")
    assert "passWithNoTests" not in config, (
        "vitest.config.js sets passWithNoTests; an empty `include` match would "
        "then exit 0 and the JS gate could report success with no tests run"
    )
    for name, script in _scripts().items():
        if "vitest" in script:
            assert "--passWithNoTests" not in script, (
                f"npm script {name!r} passes --passWithNoTests to vitest: {script!r}"
            )


@pytest.mark.parametrize("trigger", ["pull_request", "push"])
def test_api_changes_trigger_the_workflow(trigger: str) -> None:
    # PyYAML parses a bare `on:` key as the boolean True.
    on = _workflow().get("on") or _workflow()[True]
    paths = on[trigger]["paths"]
    assert "api/**" in paths, (
        f"`api/**` missing from the {trigger} path filter; a change under api/ "
        f"would trigger no JS gate. Current: {paths}"
    )


def test_sanitize_test_exercises_the_real_function() -> None:
    source = SANITIZE_TEST.read_text(encoding="utf-8")
    assert "from '../chat.js'" in source, (
        "sanitize.test.js no longer imports sanitizeInput from api/chat.js. If the "
        "function body was copied back into the test, the suite tests a mirror and "
        "can stay green while the shipped sanitizer regresses."
    )
    assert "function sanitizeInput(input)" not in source, (
        "sanitize.test.js defines its own sanitizeInput again — that is the mirror "
        "this guard exists to prevent."
    )


def test_chat_exports_sanitize_input() -> None:
    assert "export function sanitizeInput(input)" in CHAT.read_text(encoding="utf-8"), (
        "api/chat.js stopped exporting sanitizeInput, which breaks the import in "
        "sanitize.test.js"
    )
