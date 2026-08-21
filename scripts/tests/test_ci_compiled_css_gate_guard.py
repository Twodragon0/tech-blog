#!/usr/bin/env python3
"""CI regression guard: the compiled-CSS class-hook gate must run after the build.

`TestCompiledCss` in test_post_image_class_hooks.py asserts that the *compiled*
`_site/assets/css/post-page.css` carries the `.is-section-image` / `.is-svg-image`
class hooks and no longer carries the legacy `img[src*=…]` attribute selectors.
Section 1 of that file greps `_sass/_post.scss` for the same thing, but a source
grep only clears the one partial it reads — the compiled check is what covers
every stylesheet that actually lands in post-page.css.

Until 2026-08-18 it covered nothing. `jekyll.yml` runs `pytest` near the top of
the build job and `build.sh` as its last step, so `_site/` did not exist when
those three tests were collected and they skipped on every run — visible in the
CI summary as `4204 passed, 7 skipped`, three of which were these.

The fix has two halves and this guard pins both:

1. a post-build pytest step that re-runs `TestCompiledCss`, placed *after* the
   build.sh step (order is the whole point — before it, the artifact is absent);
2. `REQUIRE_COMPILED_CSS=1` on that step, which makes a missing artifact fail
   instead of skip. Without the env var the step would "pass" by skipping all
   three tests, which is exactly the silence being fixed.

Drop either half and the gate is decorative again with nothing turning red.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"
HOOKS_TEST = REPO_ROOT / "scripts" / "tests" / "test_post_image_class_hooks.py"

BUILD_STEP_MARKER = "build.sh"
GATE_MARKER = "test_post_image_class_hooks.py::TestCompiledCss"
ENV_VAR = "REQUIRE_COMPILED_CSS"


def _build_job_steps() -> list[dict]:
    import yaml

    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return workflow["jobs"]["build"]["steps"]


def _index_of(predicate) -> int:
    for i, step in enumerate(_build_job_steps()):
        if predicate(step):
            return i
    return -1


# ---------------------------------------------------------------------------
# Non-vacuity: the tests being gated have to still exist
# ---------------------------------------------------------------------------


def test_compiled_css_tests_still_exist() -> None:
    """If TestCompiledCss is gone this guard protects nothing — delete it too."""
    source = HOOKS_TEST.read_text(encoding="utf-8")
    assert "class TestCompiledCss:" in source, (
        f"{HOOKS_TEST.name} no longer defines TestCompiledCss; if it was removed "
        f"on purpose, delete {Path(__file__).name} and the workflow step with it"
    )


def test_missing_artifact_fails_when_the_gate_is_armed() -> None:
    """The fail-closed branch is what distinguishes this from the old skipif.

    A step that runs the tests but lets them skip is indistinguishable from no
    step at all in the CI summary, so the `pytest.fail` branch is load-bearing.
    """
    source = HOOKS_TEST.read_text(encoding="utf-8")
    assert f'os.environ.get("{ENV_VAR}")' in source, (
        f"{HOOKS_TEST.name} no longer reads {ENV_VAR}; the gate would skip "
        f"silently when _site/ is absent"
    )
    assert "pytest.fail(" in source, (
        f"{HOOKS_TEST.name} no longer fails on a missing artifact; a skip here "
        f"reads as success in the CI summary"
    )


# ---------------------------------------------------------------------------
# The workflow wiring
# ---------------------------------------------------------------------------


def test_gate_step_exists_and_is_armed() -> None:
    idx = _index_of(lambda s: GATE_MARKER in s.get("run", ""))
    assert idx >= 0, (
        f"{WORKFLOW.name} build job has no step running {GATE_MARKER}; the "
        f"compiled-CSS assertions would only ever be collected by the pre-build "
        f"pytest step, where they skip"
    )

    step = _build_job_steps()[idx]
    env = step.get("env") or {}
    assert str(env.get(ENV_VAR)) == "1", (
        f"the compiled-CSS gate step does not set {ENV_VAR}=1 (env={env!r}); "
        f"without it a missing _site/ skips all three tests and the step passes"
    )


def test_gate_step_runs_after_the_build() -> None:
    """Order is the entire fix — before build.sh the artifact does not exist."""
    build_idx = _index_of(lambda s: BUILD_STEP_MARKER in s.get("run", ""))
    gate_idx = _index_of(lambda s: GATE_MARKER in s.get("run", ""))

    assert build_idx >= 0, f"{WORKFLOW.name} build job no longer runs build.sh"
    assert gate_idx >= 0, f"{WORKFLOW.name} build job no longer runs the gate"
    assert build_idx < gate_idx, (
        f"the compiled-CSS gate (step {gate_idx}) runs before build.sh "
        f"(step {build_idx}); _site/assets/css/post-page.css is not written yet, "
        f"so with {ENV_VAR}=1 every run fails and without it every run skips"
    )
