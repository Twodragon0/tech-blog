#!/usr/bin/env python3
"""CI regression guard: jekyll.yml's validation steps must stay hard.

`jekyll.yml` carries the `build` job, one of only two checks with real blocking
evidence in the last 30 PRs. The 2026-08-10 audit found four of its steps softened,
two of them doubly:

D8  "Validate post quality" had `continue-on-error: true` AND `|| true`, under a step
    that printed "warnings only, non-blocking". `validate_post_quality.py` defaults
    `--fail-below` to **60**, so a real floor existed and was disabled twice over — it
    survived only in the pre-commit hook, which `--no-verify` skips. Measured before
    enabling: 261 posts, minimum score 80, mean 90.6, zero below 60.

D9  "Check front matter size" warned above 1,000 chars via inline Python that could
    not exit non-zero. Measured: 261 of 261 posts exceed 1,000. A threshold every file
    violates is noise, so it became a growth ratchet plus a 3,000-char cap
    (`check_front_matter_growth.py`, measured max 2,749).

D10 The Digest gate and the front-matter quote gate both computed their changed-file
    list with `|| true`. An unresolvable `origin/main` therefore yielded an empty list
    and printed "skipping" — a broken checkout silently skipped the gate while the step
    reported success. The quote gate's version was worse: the `|| true` sat inside
    `<(...)` process substitution, where mapfile cannot see the exit code at all.

D7/D11 The two PR-comment steps keep `continue-on-error: true` — failing to post a
    comment must not fail CI — but their `gh` calls used bare `|| true`, so a failed
    comment left no trace. They now emit `::warning::`.

Direction: absence assertions on the soft shapes. Re-adding `continue-on-error` to a
validation step, or `|| true` around a validator, trips this guard.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "jekyll.yml"

# Steps that make a pass/fail judgement. These must never be soft.
VALIDATION_STEPS = (
    "Run script unit tests",
    "Digest quality gate",
    "Validate Jekyll Configuration",
    "Validate Liquid include syntax in posts",
    "Front-matter quote gate (unescaped inner DQ)",
    "Validate posts (severity, front matter, links)",
    "Validate post quality (PR only)",
    "Check front matter growth (PR only)",
)

# Steps whose only job is to post a PR comment. Soft is CORRECT here: a comment API
# failure must not fail the build. They must still announce the failure.
REPORTING_STEPS = (
    "Post coverage comment (PR only)",
    "Post quality dashboard comment (PR only)",
)


def _job() -> dict:
    import yaml

    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["build"]


def _steps() -> dict[str, dict]:
    return {s["name"]: s for s in _job()["steps"] if s.get("name")}


def _uncommented(shell: str) -> str:
    """Shell text minus comment-only lines.

    Each repaired step documents the `|| true` it removed, so asserting on raw text
    would match the very comment explaining the fix.
    """
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


@pytest.mark.parametrize("name", VALIDATION_STEPS)
def test_validation_steps_are_not_continue_on_error(name: str):
    steps = _steps()
    assert name in steps, f"step {name!r} is gone from jekyll.yml — renamed or removed?"
    assert not steps[name].get("continue-on-error"), (
        f"{name!r} is continue-on-error again. A validation step that cannot fail the "
        "job is a green tick over an unchecked claim."
    )


@pytest.mark.parametrize("name", VALIDATION_STEPS)
def test_validation_steps_do_not_swallow_exit_codes(name: str):
    steps = _steps()
    run = _uncommented(steps[name].get("run") or "")
    offenders = [
        ln.strip()
        for ln in run.splitlines()
        if "|| true" in ln and "gh api" not in ln  # comment-id lookups may legitimately be empty
    ]
    assert not offenders, (
        f"{name!r} swallows an exit code with '|| true': {offenders}. If the intent is "
        "advisory, say so in the step name — do not name it Validate and then disarm it."
    )


def test_post_quality_floor_is_enforced():
    run = _uncommented(_steps()["Validate post quality (PR only)"]["run"])
    assert "validate_post_quality.py" in run
    assert "|| true" not in run, (
        "the 60-point floor is disarmed again. validate_post_quality.py exits 1 below "
        "--fail-below (default 60); measured corpus minimum is 80."
    )


def test_front_matter_gate_uses_the_ratchet_script():
    steps = _steps()
    assert "Check front matter size (PR only)" not in steps, (
        "the old 1,000-char warning step is back. 261 of 261 posts exceed that "
        "threshold, so it can only ever print noise."
    )
    run = _uncommented(steps["Check front matter growth (PR only)"]["run"])
    assert "check_front_matter_growth.py" in run
    assert "--changed" in run, "the ratchet needs a diff base to compare against"


@pytest.mark.parametrize("step_name", ["Digest quality gate", "Front-matter quote gate (unescaped inner DQ)"])
def test_changed_file_diffs_fail_closed(step_name: str):
    """An unresolvable origin/main must not read as "nothing changed"."""
    run = _uncommented(_steps()[step_name]["run"])
    assert re.search(r"if !\s+\w+=\$\(git diff", run), (
        f"{step_name!r} no longer checks whether `git diff` succeeded. A shallow or "
        "broken checkout would yield an empty list and skip the gate while passing."
    )
    assert "refusing to skip" in run, "expected an explicit ::error:: on diff failure"


def test_quote_gate_diff_is_not_inside_process_substitution():
    """`mapfile < <(cmd || true)` hides the exit code from mapfile entirely."""
    run = _uncommented(_steps()["Front-matter quote gate (unescaped inner DQ)"]["run"])
    assert "mapfile -t CHANGED < <(" not in run, (
        "the changed-file list is computed inside <(...) again; a failure there is "
        "invisible to mapfile, which is how this gate silently skipped"
    )


@pytest.mark.parametrize("name", REPORTING_STEPS)
def test_reporting_steps_stay_soft_but_announce_failures(name: str):
    """Comment posting should not fail CI — but must not vanish silently either."""
    steps = _steps()
    assert name in steps, f"reporting step {name!r} disappeared"
    assert steps[name].get("continue-on-error") is True, (
        f"{name!r} is now hard-failing. A GitHub comment API hiccup would break "
        "unrelated PRs; keep it soft."
    )
    run = steps[name].get("run") or ""
    assert "::warning::" in run, (
        f"{name!r} swallows posting failures without a trace. Emit ::warning:: so a "
        "missing comment is visible, following indexnow-ping.yml."
    )


def test_coverage_floor_still_pinned():
    """Canary: the pytest coverage floor is the other half of this job's value."""
    body = _uncommented(WORKFLOW.read_text(encoding="utf-8"))
    assert "--cov-fail-under=40" in body, (
        "the coverage floor moved or vanished. Raising or removing it is a deliberate "
        "decision that belongs in a PR description, not a silent edit."
    )
