#!/usr/bin/env python3
"""CI regression guard: the info/style ratchet stays wired, unsoftened and complete.

The blocking actionlint gate and this ratchet are designed as exact complements:
the gate enforces native rules plus SC `warning`/`error`, the ratchet holds the
line on SC `info`/`style`. Together they cover everything actionlint emits.

That complement is an invariant nothing else checks, and it can be broken from
either side without touching the other file:

- add `-ignore 'SC[0-9]+:warning:'` to the gate and warnings become ungated,
  because the ratchet does not cover them either;
- drop `"style"` from `RATCHETED_SEVERITIES` and style findings become free to
  grow, while the gate still ignores them.

`test_gate_exclusions_and_ratchet_coverage_are_complements` is the assertion
that makes either move fail loudly. It is the reason this file exists.

The trigger assertion matters for a subtler reason. The workflow's `paths:`
filter used to list only `.github/workflows/**`. With the baseline living under
`scripts/`, a PR could raise the baseline without waking this job at all, merge
green, and a second PR would then land the extra findings against the
already-widened number. Neither PR would ever see a red check.

Direction: pins are `==`, the severity split is an exact partition, softeners
are forbidden, trigger coverage is `>=`.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "action-pin-check.yml"
CHECKER = REPO_ROOT / "scripts" / "check_actionlint_ratchet.py"
BASELINE_REL = "scripts/actionlint_ratchet_baseline.txt"
CHECKER_REL = "scripts/check_actionlint_ratchet.py"

JOB = "check-pins"
RATCHET_STEP = "actionlint info/style ratchet"
GATE_STEP = "actionlint (blocking"
SHELLCHECK_STEP = "Install shellcheck"


def _doc(path: Path | None = None) -> dict:
    return yaml.safe_load((path or WORKFLOW).read_text(encoding="utf-8"))


def _step(fragment: str, path: Path | None = None) -> dict:
    steps = _doc(path)["jobs"][JOB]["steps"]
    matches = [s for s in steps if fragment in (s.get("name") or "")]
    if not matches:
        pytest.fail(f"no step whose name contains {fragment!r}")
    if len(matches) > 1:
        pytest.fail(
            f"{fragment!r} matches {len(matches)} steps: {[s.get('name') for s in matches]}"
        )
    return matches[0]


def _uncommented(shell: str) -> str:
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


def _ratcheted_severities() -> tuple[str, ...]:
    spec = importlib.util.spec_from_file_location("_ratchet", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return tuple(module.RATCHETED_SEVERITIES)


def _on(doc: dict) -> dict:
    # PyYAML resolves a bare `on:` key to the boolean True.
    return doc.get(True, doc.get("on")) or {}


def test_checker_and_baseline_exist():
    assert CHECKER.is_file(), f"{CHECKER} not found"
    assert (REPO_ROOT / BASELINE_REL).is_file(), f"{BASELINE_REL} not found"


def test_ratchet_step_invokes_the_checker():
    body = _uncommented(_step(RATCHET_STEP)["run"])
    assert CHECKER_REL in body, (
        f"the ratchet step no longer runs {CHECKER_REL}; the baseline would then "
        "be a file nothing reads"
    )


def test_ratchet_step_is_not_softened():
    step = _step(RATCHET_STEP)
    assert not step.get("continue-on-error"), "the ratchet step is continue-on-error"
    assert not step.get("if"), (
        f"the ratchet carries a condition ({step.get('if')!r}); it must run on every "
        "trigger of this workflow"
    )
    body = _uncommented(step["run"])
    for softener in ("|| true", "|| echo", "|| :", "--warn-only", "continue-on-error"):
        assert softener not in body, (
            f"the ratchet invocation is softened with {softener!r}. A ratchet that "
            "cannot fail is a counter."
        )
    assert not _doc()["jobs"][JOB].get("continue-on-error"), (
        "the whole job is continue-on-error, which defeats every gate in it"
    )


def test_gate_exclusions_and_ratchet_coverage_are_complements():
    """Every tier the blocking gate ignores must be one the ratchet holds.

    This is the invariant that makes "we exclude info/style" safe. Break it in
    either direction and a severity tier becomes enforced by nothing at all.
    """
    gate_body = _uncommented(_step(GATE_STEP)["run"])
    ignored = set(re.findall(r"-ignore\s+'SC\[0-9\]\+:([a-z]+):'", gate_body))
    assert ignored, (
        "no SC severity exclusions found in the blocking gate. Either the gate "
        "changed shape or this regex went stale — check before assuming the "
        "former; a guard that finds nothing reads exactly like a guard that passes."
    )
    ratcheted = set(_ratcheted_severities())
    assert ignored == ratcheted, (
        f"the gate ignores {sorted(ignored)} but the ratchet covers "
        f"{sorted(ratcheted)}. The difference is enforced by nothing: a tier the "
        "gate skips and the ratchet does not count is free to grow without limit. "
        "Change both files together, or argue in the diff for leaving a tier "
        "uncovered."
    )


def test_shellcheck_is_pinned_and_checksum_verified():
    """An unpinned analyzer makes the committed count unreproducible.

    The runners ship 0.9.0 (ubuntu-24.04) / 0.8.0 (ubuntu-22.04); the baseline is
    generated against 0.11.0. Without the pin the job is born red, and the
    obvious "fix" is to regenerate the baseline on whatever the runner happened
    to have that week.
    """
    step = _step(SHELLCHECK_STEP)
    env = step.get("env") or {}
    version = str(env.get("SHELLCHECK_VERSION", ""))
    digest = str(env.get("SHELLCHECK_SHA256", ""))
    assert re.fullmatch(r"\d+\.\d+(\.\d+)?", version), (
        f"SHELLCHECK_VERSION is {version!r}; it must be an exact release"
    )
    assert re.fullmatch(r"[0-9a-f]{64}", digest), (
        f"SHELLCHECK_SHA256 is {digest!r}; a 64-hex sha256 of the release tarball "
        "is required. If bumping, download the artifact and compute the checksum — "
        "do not copy a value you have not verified — then regenerate the baseline, "
        "because a version bump can change which findings appear."
    )
    body = _uncommented(step["run"])
    assert "sha256sum -c" in body, "the checksum is declared but never verified"
    url = next(ln for ln in body.splitlines() if "releases/download" in ln)
    assert "${SHELLCHECK_VERSION}" in url, (
        f"the download URL does not interpolate SHELLCHECK_VERSION: {url.strip()!r}"
    )
    assert not re.search(r"curl[^|\n]*\|\s*(ba)?sh", body), (
        "the install step pipes a remote script into a shell"
    )


def test_shellcheck_is_installed_before_actionlint_runs():
    names = [s.get("name") or "" for s in _doc()["jobs"][JOB]["steps"]]
    install = next(i for i, n in enumerate(names) if SHELLCHECK_STEP in n)
    ratchet = next(i for i, n in enumerate(names) if RATCHET_STEP in n)
    gate = next(i for i, n in enumerate(names) if GATE_STEP in n)
    assert install < gate and install < ratchet, (
        "shellcheck is installed after actionlint runs, so the pinned version is "
        "not the one that produced the findings"
    )


@pytest.mark.parametrize("event", ["push", "pull_request"])
@pytest.mark.parametrize("needed", [BASELINE_REL, CHECKER_REL, ".github/workflows/**"])
def test_trigger_covers_the_baseline_and_the_checker(event, needed):
    paths = (_on(_doc()).get(event) or {}).get("paths") or []
    assert needed in paths, (
        f"the {event} trigger does not cover {needed!r} (currently {paths}). "
        "Editing it would then not run this job, so the baseline could be widened "
        "in one PR and filled in another, both green."
    )
