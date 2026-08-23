#!/usr/bin/env python3
"""CI regression guard: the CSP interaction gate must keep measuring the hard path.

Background (2026-08-12)
-----------------------
`vercel.json` ships a Report-Only policy that drops 'unsafe-inline' from script-src and
allows only the two first-party inline-script hashes — the preview of CSP Path B. A
headless page-load measurement on production found ZERO violations, which looked like a
green light for Path B. It was not: `head-runtime.js` defers GA / AdSense / Kakao /
Sentry behind the first user interaction, and `google-translate.js` only loads Google's
element.js from a click on `#lang-toggle`. Page load never reaches them.

Bisecting the interaction path produced the actual answer:

    no interaction                        -> 0 violations (GTM + Sentry already loaded)
    mouse move / scroll / synthetic events -> 0 violations
    click #lang-toggle alone              -> 1 violation (script-src-elem, blockedURI=inline)

Reproduced WITHOUT any Playwright injection (console-only observation), and a run with no
interaction produces zero, so it is the site's behaviour rather than an instrumentation
artifact. The click creates `about:blank` frames, which inherit the parent CSP — hence
`sourceFile="about"`.

So the Path B blocker is Google Translate, isolated locally in minutes without waiting
for Sentry data. That violation is grandfathered; new ones fail.

What these tests protect
------------------------
The gate is only worth anything while it still (a) drives the interactions, (b) refuses
to pass when it could not measure, and (c) keeps the known violation visible instead of
deleting it to go quiet. Each is easy to erode with a one-line edit.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "csp-interaction-check.yml"
SCRIPT = REPO_ROOT / "scripts" / "tests" / "check_csp_interaction_violations.mjs"
BASELINE = REPO_ROOT / "scripts" / "tests" / "csp_interaction_baseline.txt"
VERCEL_JSON = REPO_ROOT / "vercel.json"


def _yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _uncommented(text: str, marker: str) -> str:
    return "\n".join(
        ln for ln in text.splitlines() if not ln.lstrip().startswith(marker)
    )


def _script() -> str:
    return _uncommented(SCRIPT.read_text(encoding="utf-8"), "//")


def _workflow_body() -> str:
    return _uncommented(WORKFLOW.read_text(encoding="utf-8"), "#")


# ---------------------------------------------------------------------------
# The gate must exist and must not be soft
# ---------------------------------------------------------------------------


def test_workflow_and_script_exist():
    assert WORKFLOW.is_file(), f"{WORKFLOW.name} is gone"
    assert SCRIPT.is_file(), f"{SCRIPT.name} is gone"
    assert BASELINE.is_file(), f"{BASELINE.name} is gone"


def test_gate_is_not_soft():
    job = _yaml(WORKFLOW)["jobs"]["csp-interaction"]
    assert not job.get("continue-on-error"), (
        "the CSP interaction job is continue-on-error"
    )
    for step in job["steps"]:
        run = step.get("run") or ""
        if "check_csp_interaction_violations.mjs" in run:
            assert "|| true" not in run, "the gate invocation is wrapped in '|| true'"
            assert not step.get("continue-on-error"), (
                "the gate step is continue-on-error"
            )
            assert "--baseline" in run, (
                "the gate must run with --baseline, otherwise the known Translate "
                "violation fails every run and the gate gets muted"
            )
            return
    pytest.fail("no step invokes check_csp_interaction_violations.mjs")


# ---------------------------------------------------------------------------
# It must still drive the interactions that make it worth running
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fragment", "why"),
    [
        (
            "#lang-toggle",
            "the Translate click is the only interaction that found a violation",
        ),
        (
            ".adsbygoogle",
            "AdSense loads via IntersectionObserver on this slot, not on scroll",
        ),
        ("pointermove", "head-runtime.js binds this to its lazy loaders"),
        (
            "securitypolicyviolation",
            "structural violation capture, not console scraping",
        ),
    ],
)
def test_script_still_drives_the_interaction_path(fragment: str, why: str):
    assert fragment in _script(), (
        f"{SCRIPT.name} no longer references {fragment!r} — {why}"
    )


def test_script_reports_coverage_gaps():
    """A green result must say which integrations it did NOT exercise."""
    src = _script()
    assert "uncovered" in src, (
        "coverage tracking is gone; a green run would overstate what it covered"
    )
    assert "configured" in src, (
        "the script no longer distinguishes 'not configured' from 'configured but not "
        "triggered' — the second is a coverage gap, the first is not"
    )


def test_script_refuses_to_pass_when_it_cannot_measure():
    """ "Could not check" must not read as "nothing was wrong"."""
    src = _script()
    assert "sawReportOnly" in src, (
        "the script no longer verifies a Report-Only header is present; without one it "
        "would pass vacuously"
    )
    assert (
        "process.exit(2)" in src
        or "exitCode = 2" in src
        or "Math.max(exitCode, 2)" in src
    ), "the distinct 'could not measure' exit code is gone"


def test_extension_violations_are_excluded():
    """The console dump that started this work was mostly MetaMask."""
    src = _script()
    assert "chrome-extension:" in src, (
        "extension-origin violations are no longer filtered out. Adding 'unsafe-eval' or "
        "'unsafe-inline' to satisfy a browser extension would weaken the policy for every "
        "visitor."
    )


# ---------------------------------------------------------------------------
# The baseline is a record, not a mute button
# ---------------------------------------------------------------------------


def test_baseline_documents_the_known_blocker():
    text = BASELINE.read_text(encoding="utf-8")
    assert "script-src-elem|inline" in text, (
        "the grandfathered Translate violation is gone from the baseline. If Path B work "
        "actually fixed it, that is the definition of done — say so in the PR. If it was "
        "deleted to quiet the gate, restore it."
    )
    assert "lang-toggle" in text, (
        "the baseline no longer records HOW the violation was isolated"
    )


def test_baseline_stays_small():
    """A growing baseline means Path B is receding, and that should be visible."""
    entries = [
        ln.strip()
        for ln in BASELINE.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.lstrip().startswith("#")
    ]
    assert len(entries) <= 3, (
        f"the CSP interaction baseline has grown to {len(entries)} entries: {entries}. Each "
        "one is a first-party violation that blocks Path B — grandfathering more of them "
        "quietly converts the gate into a record of defeat."
    )


# ---------------------------------------------------------------------------
# Premise canary
# ---------------------------------------------------------------------------


def test_report_only_policy_still_exists_to_measure():
    """The gate has nothing to measure if the Report-Only policy is dropped."""
    import json

    config = json.loads(VERCEL_JSON.read_text(encoding="utf-8"))
    keys = {h["key"] for entry in config["headers"] for h in entry["headers"]}
    assert "Content-Security-Policy-Report-Only" in keys, (
        "vercel.json no longer sends a Report-Only policy, so this gate measures nothing. "
        "If Path B shipped and the preview is obsolete, retire the gate deliberately."
    )


def test_schedule_present_because_the_target_is_production():
    """A PR run tests the PREVIOUS deployment; the cron is what catches regressions."""
    parsed = _yaml(WORKFLOW)
    triggers = parsed[True] if True in parsed else parsed["on"]
    assert "schedule" in triggers, (
        "the schedule is gone. This gate measures production, so a pull_request run tests "
        "the deployment that is already live — the cron is the trigger that actually "
        "catches a regression after it ships."
    )
    assert "workflow_dispatch" in triggers, "no way to run the gate on demand"
