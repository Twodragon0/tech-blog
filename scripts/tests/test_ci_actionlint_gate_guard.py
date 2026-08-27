#!/usr/bin/env python3
"""CI regression guard: the actionlint gate stays pinned, verified and unsoftened.

Nothing linted `.github/workflows/` until 2026-08-26 — no CI job and no
pre-commit hook ran actionlint or shellcheck over them. That gap mattered
because the plumbing added in #616 (a `workflow_call` job, `needs:` outputs,
`secrets: inherit`) is exactly the class actionlint validates and no other gate
in this repo touches: a typo in `needs.auto-publish.outputs.post_file` is
invisible to YAML parsing, to pytest, and to the pin checker.

Measured before wiring, at the scope being enforced, per the rule that a gate
nobody has run has never been right:

    actionlint native rules ...  0
    SC info .................... 65   (59x SC2086)
    SC style ....................  5   (SC2129)
    SC warning ..................  1   (SC2034, fixed in the same change)

So the gate starts at zero rather than being born red, and the excluded info +
style tiers are printed to the run summary instead of hidden.

Three things here are load-bearing:

1. The binary is version-pinned AND checksum-verified. The upstream install
   path is `curl | bash` off the mutable `main` ref, which would make a
   workflow whose whole purpose is pin hygiene depend on an unpinned script.
2. The ignore patterns are anchored to `SC<digits>:`. A bare `':info:'` can
   match a native actionlint message, silently widening the exclusion from
   "cosmetic shell findings" to "anything whose text happens to contain
   ':info:'".
3. Neither the gate step nor the job is softened.

Direction: pins are `==` (a bump must be deliberate and re-checksummed),
exclusions are an exact set, softeners are forbidden.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "action-pin-check.yml"

JOB = "check-pins"
INSTALL_STEP = "Install actionlint"
GATE_STEP = "actionlint (blocking"
INFO_STEP = "actionlint informational"

# Exactly the two tiers excluded from gating. Widening this set is a policy
# change and must be argued for in the diff, not slipped in.
EXPECTED_IGNORES = {"SC[0-9]+:info:", "SC[0-9]+:style:"}


def _doc() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _steps() -> list[dict]:
    return _doc()["jobs"][JOB]["steps"]


def _step(fragment: str) -> dict:
    for s in _steps():
        if fragment in (s.get("name") or ""):
            return s
    pytest.fail(f"no step whose name contains {fragment!r} in {WORKFLOW.name}")


def _uncommented(shell: str) -> str:
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


def _logical_lines(shell: str) -> list[str]:
    """Shell lines with trailing-backslash continuations joined.

    The actionlint invocation spans four physical lines. Checking physical lines
    let a `|| true` appended to the last continuation escape entirely: that line
    does not contain the word "actionlint", so a loop keyed on it never looked.
    The mutation was confirmed to have landed before this was diagnosed.
    """
    out: list[str] = []
    buf = ""
    for raw in shell.splitlines():
        ln = raw.strip()
        if not ln:
            continue
        if ln.endswith("\\"):
            buf += ln[:-1].rstrip() + " "
            continue
        out.append((buf + ln).strip())
        buf = ""
    if buf:
        out.append(buf.strip())
    return out


def test_workflow_exists():
    assert WORKFLOW.is_file(), f"{WORKFLOW} not found"


def test_actionlint_is_version_pinned_and_checksum_verified():
    step = _step(INSTALL_STEP)
    env = step.get("env") or {}
    version = str(env.get("ACTIONLINT_VERSION", ""))
    digest = str(env.get("ACTIONLINT_SHA256", ""))
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), (
        f"ACTIONLINT_VERSION is {version!r}; it must be an exact release, not a "
        "range or a tag like 'latest'"
    )
    assert re.fullmatch(r"[0-9a-f]{64}", digest), (
        f"ACTIONLINT_SHA256 is {digest!r}; a 64-hex sha256 of the release tarball "
        "is required. If bumping the version, fetch the new checksum from the "
        "release's checksums.txt and verify it against the downloaded artifact — "
        "do not copy a value you have not checked."
    )
    body = _uncommented(step["run"])
    assert "sha256sum -c" in body, (
        "the checksum is declared but never verified. An unverified pin is "
        "documentation, not a control."
    )
    # The URL must interpolate the env var rather than repeat the literal, so a
    # version bump cannot leave the download pointing at the old release while
    # the pin claims the new one. (An earlier draft of this test asserted the
    # literal appeared in the body and failed on correct code.)
    url = next(ln for ln in body.splitlines() if "releases/download" in ln)
    assert "${ACTIONLINT_VERSION}" in url, (
        f"the download URL does not interpolate ACTIONLINT_VERSION: {url.strip()!r}. "
        "A hardcoded version there can silently disagree with the pin above."
    )
    assert "${ACTIONLINT_SHA256}" in body, (
        "the checksum comparison does not use ACTIONLINT_SHA256"
    )


def test_install_does_not_pipe_a_remote_script_to_a_shell():
    """The upstream one-liner curls from the mutable `main` ref."""
    body = _uncommented(_step(INSTALL_STEP)["run"])
    assert not re.search(r"curl[^|\n]*\|\s*(ba)?sh", body), (
        "the install step pipes a remote script into a shell. This workflow "
        "exists to enforce pin hygiene; it must not depend on an unpinned script."
    )
    assert "download-actionlint.bash" not in body, (
        "download-actionlint.bash is fetched from refs/heads/main — unpinned"
    )


def test_gate_excludes_exactly_the_documented_tiers():
    body = _uncommented(_step(GATE_STEP)["run"])
    found = set(re.findall(r"-ignore\s+'([^']+)'", body))
    assert found == EXPECTED_IGNORES, (
        f"actionlint exclusions are {sorted(found)}, expected "
        f"{sorted(EXPECTED_IGNORES)}. Adding one hides a tier that currently "
        "gates; removing one makes the job red on 70 pre-existing cosmetic "
        "findings. Either way it is a policy change — say so in the diff."
    )


def test_ignore_patterns_cannot_swallow_native_actionlint_findings():
    """Anchored to `SC<digits>:`, so only shellcheck output can match."""
    body = _uncommented(_step(GATE_STEP)["run"])
    for pattern in re.findall(r"-ignore\s+'([^']+)'", body):
        assert pattern.startswith("SC[0-9]+"), (
            f"the exclusion {pattern!r} is not anchored to a shellcheck code. A "
            "bare severity like ':info:' also matches native actionlint "
            "messages, turning a narrow cosmetic exclusion into a general one."
        )


def test_gate_is_not_softened():
    gate = _step(GATE_STEP)
    assert not gate.get("continue-on-error"), "the actionlint gate is continue-on-error"
    assert not gate.get("if"), (
        f"the gate carries a condition ({gate.get('if')!r}); it must run on every "
        "trigger of this workflow"
    )
    lines = _logical_lines(_uncommented(gate["run"]))
    invocations = [ln for ln in lines if ln.startswith("actionlint")]
    assert invocations, "the gate no longer invokes actionlint"
    for ln in invocations:
        for softener in ("|| true", "|| echo", "continue-on-error", "|| :"):
            assert softener not in ln, (
                f"the actionlint invocation is softened with {softener!r}: {ln!r}"
            )
    assert not _doc()["jobs"][JOB].get("continue-on-error"), (
        "the whole job is continue-on-error, which defeats both gates in it"
    )


def test_informational_step_is_reporting_only_and_derives_its_counts():
    """The excluded tiers must stay visible, and the numbers must be measured."""
    step = _step(INFO_STEP)
    assert step.get("if") == "always()", (
        "the informational step should run even when the gate fails; that is when "
        "its counts are most useful"
    )
    body = _uncommented(step["run"])
    assert "GITHUB_STEP_SUMMARY" in body, "the counts are not surfaced anywhere"
    assert "$(actionlint" in body or "actionlint 2>&1" in body, (
        "the counts are no longer derived from an actual run. A hardcoded number "
        "here is the same defect as a hardcoded --status: it reports a constant, "
        "not a result."
    )
    assert not re.search(r"info=\s*\d+", body), (
        "an info count is hardcoded rather than computed"
    )


def test_gate_runs_whenever_any_workflow_changes():
    on = _doc().get(True, _doc().get("on")) or {}
    for event in ("push", "pull_request"):
        block = on.get(event) or {}
        paths = block.get("paths") or []
        assert ".github/workflows/**" in paths, (
            f"the {event} trigger no longer covers .github/workflows/**, so "
            "editing a workflow would not lint it"
        )
