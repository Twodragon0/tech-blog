"""Pin the jekyll.yml step that dry-runs `pip install -r scripts/requirements.txt`.

Nothing installs scripts/requirements.txt in CI except generate-images.yml, which
runs only after merge. Dependabot proposed five mutually conflicting pins for it
(#488, #562, #572, #791, #792); #792 reached main and broke Generate Post Images
for four weeks with ResolutionImpossible. The resolver dry-run in the build job
moves that failure to the PR. With the dependabot ignore rules for Pillow gone,
it is the only defence, so a cleanup must not drop or disarm it silently.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
JEKYLL = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"
GENERATE_IMAGES = REPO_ROOT / ".github" / "workflows" / "generate-images.yml"

STEP_NAME = "Check scripts/requirements.txt resolves"


def _steps(workflow: Path, job: str | None = None) -> list[dict]:
    jobs = yaml.safe_load(workflow.read_text(encoding="utf-8"))["jobs"]
    if job is not None:
        return jobs[job]["steps"]
    return [step for spec in jobs.values() for step in spec.get("steps", [])]


def _python_version(steps: list[dict]) -> str:
    versions = {
        str(step["with"]["python-version"])
        for step in steps
        if "actions/setup-python" in str(step.get("uses", ""))
    }
    assert len(versions) == 1, versions
    return versions.pop()


def test_dry_run_step_is_present_and_armed():
    steps = _steps(JEKYLL, "build")
    names = [step.get("name") for step in steps]
    assert STEP_NAME in names, "the requirements.txt resolver dry-run step is gone"
    step = steps[names.index(STEP_NAME)]
    run = step.get("run", "")
    assert "--dry-run" in run and "-r scripts/requirements.txt" in run, run
    assert not step.get("continue-on-error"), "the dry-run must fail the job"
    assert "|| true" not in run and "|| echo" not in run, run
    assert "if" not in step, "the dry-run must run on every build"


def test_dry_run_runs_after_python_setup_and_before_pytest():
    steps = _steps(JEKYLL, "build")
    names = [step.get("name") for step in steps]
    at = names.index(STEP_NAME)
    setup = next(
        i
        for i, step in enumerate(steps)
        if "actions/setup-python" in str(step.get("uses", ""))
    )
    pytest_at = next(
        i
        for i, step in enumerate(steps)
        if "pytest scripts/tests" in str(step.get("run", ""))
    )
    assert setup < at < pytest_at, (setup, at, pytest_at)


def test_dry_run_uses_the_image_workflows_python():
    # A resolution on one Python minor says little about another: wheels and
    # markers differ, so the dry-run must match the job that really installs it.
    assert _python_version(_steps(JEKYLL, "build")) == _python_version(
        _steps(GENERATE_IMAGES)
    )
