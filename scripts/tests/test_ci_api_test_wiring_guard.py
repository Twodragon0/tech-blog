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
    assert script, "package.json lost the `test:api` script; the api/ suite has no runner"
    assert "node --test" in script, (
        "`test:api` must invoke `node --test` — these files import from 'node:test' "
        f"and Vitest cannot execute them. Got: {script!r}"
    )
    assert "api/__tests__" in script, f"`test:api` no longer targets api/__tests__: {script!r}"


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
