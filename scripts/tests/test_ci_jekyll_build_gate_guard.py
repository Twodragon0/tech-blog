#!/usr/bin/env python3
"""Regression guard: the jekyll-build fixture stays fail-closed in CI.

``test_image_content_hash.py`` runs its own ``bundle exec jekyll build`` and
asserts the ``?v={hash}`` cache-buster the `image_content_hash` plugin appends.
Until 2026-08-21 a build that *failed* skipped those 5 tests and left the step
green — a build defect reported as "not applicable". Two facts made that
invisible: a skip and a pass are both non-failures in a step's exit code, and
locally the build really does fail for an unrelated reason (mise ahead of rbenv
on PATH), so the skips looked normal.

The repair is the ``REQUIRE_COMPILED_CSS`` pattern from PR #578: an explicit
opt-in env var that turns "cannot build" into a failure, set only on CI.

Three parts have to hold together, and this guard pins each:

1. ``REQUIRE_JEKYLL_BUILD=1`` on the pytest step in ``jekyll.yml`` — without it
   the fixture is back to skipping and nothing turns red;
2. the armed branches in the fixture (`bundle` absent, and build rc != 0) —
   an env var no code reads is decoration;
3. ``Setup Ruby`` ordered *before* that step — arming a step that runs before
   bundler exists would make CI permanently red instead of honest.

Part 3 is the one static review misses, so it is a separate test.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"
HASH_TEST = REPO_ROOT / "scripts" / "tests" / "test_image_content_hash.py"

PYTEST_STEP_MARKER = "pytest scripts/tests/"
RUBY_SETUP_MARKER = "ruby/setup-ruby"
ENV_VAR = "REQUIRE_JEKYLL_BUILD"


def _build_job_steps() -> list[dict]:
    import yaml

    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return workflow["jobs"]["build"]["steps"]


def _index_of(predicate) -> int:
    for i, step in enumerate(_build_job_steps()):
        if predicate(step):
            return i
    return -1


def _armed_pytest_step() -> dict | None:
    for step in _build_job_steps():
        run = step.get("run") or ""
        if PYTEST_STEP_MARKER in run and "--cov-fail-under" in run:
            return step
    return None


# ---------------------------------------------------------------------------
# Non-vacuity: the fixture being armed has to still exist
# ---------------------------------------------------------------------------


def test_the_build_fixture_still_exists() -> None:
    """If the fixture is gone this guard protects nothing — delete it too."""
    source = HASH_TEST.read_text(encoding="utf-8")
    assert "def built_site_dir" in source, (
        f"{HASH_TEST.name} no longer defines the built_site_dir fixture; if the "
        f"jekyll-build integration was removed on purpose, delete "
        f"{Path(__file__).name} and the workflow env var with it"
    )


# ---------------------------------------------------------------------------
# 1. The workflow arms the gate
# ---------------------------------------------------------------------------


def test_pytest_step_is_armed() -> None:
    step = _armed_pytest_step()
    assert step is not None, (
        f"no `{PYTEST_STEP_MARKER}` step found in the build job of "
        f"{WORKFLOW.name}; the full-suite pytest step was renamed or removed"
    )
    assert str((step.get("env") or {}).get(ENV_VAR)) == "1", (
        f"{ENV_VAR} is not set to '1' on the pytest step. Without it a jekyll "
        f"build that fails inside test_image_content_hash.py skips its 5 tests "
        f"and the step still passes — the exact silence this gate removed."
    )


# ---------------------------------------------------------------------------
# 2. The fixture reads it and fails, rather than skipping
# ---------------------------------------------------------------------------


def test_fixture_fails_closed_when_armed() -> None:
    source = HASH_TEST.read_text(encoding="utf-8")
    assert f'os.environ.get("{ENV_VAR}")' in source, (
        f"{HASH_TEST.name} does not read {ENV_VAR}; the workflow env var is "
        f"then decoration and the fixture skips as before"
    )
    assert source.count("pytest.fail(") >= 2, (
        f"{HASH_TEST.name} must fail on BOTH armed conditions — `bundle` absent "
        f"and build rc != 0 — but has {source.count('pytest.fail(')} "
        f"pytest.fail() call(s). A missing toolchain and a broken build are "
        f"different regressions and both were silent."
    )


def test_unarmed_path_still_skips_for_local_shells() -> None:
    """Local dev keeps skipping; the arm is CI-only by design.

    Removing the unarmed skip would make every dev box whose Ruby is shadowed
    fail 5 tests it has no stake in, and the predictable response is to stop
    running the suite locally.
    """
    source = HASH_TEST.read_text(encoding="utf-8")
    assert "pytest.skip(" in source, (
        f"{HASH_TEST.name} no longer skips when unarmed. Local runs would fail "
        f"on toolchain issues unrelated to the change under test."
    )


# ---------------------------------------------------------------------------
# 3. Ordering — bundler must exist before the armed step runs
# ---------------------------------------------------------------------------


def test_ruby_is_set_up_before_the_armed_step() -> None:
    ruby_idx = _index_of(lambda s: RUBY_SETUP_MARKER in str(s.get("uses", "")))
    pytest_idx = _index_of(
        lambda s: PYTEST_STEP_MARKER in (s.get("run") or "")
        and "--cov-fail-under" in (s.get("run") or "")
    )
    assert ruby_idx >= 0, f"no {RUBY_SETUP_MARKER} step in the build job"
    assert pytest_idx >= 0, "no full-suite pytest step in the build job"
    assert ruby_idx < pytest_idx, (
        f"`{RUBY_SETUP_MARKER}` is at step {ruby_idx} but the armed pytest step "
        f"is at {pytest_idx}. Armed, the fixture requires `bundle` on PATH: run "
        f"it before Ruby is installed and CI goes permanently red on a "
        f"condition that is not a defect."
    )
