#!/usr/bin/env python3
"""CI regression guard: the SVG quality gate must not be able to conceal a red main.

Why this guard exists
---------------------
``check-svg.yml`` scans the WHOLE corpus (``check_svg_quality.py --fix --ci
assets/images/``) but is trigger-filtered by ``paths``. That asymmetry hid a real
regression for three weeks:

- 2026-07-13, commit ``6bbe71af`` restored 4 README architecture SVGs from
  ``_unused_archive`` without a ``<title>`` element -> the gate's full-corpus scan
  returned ``292 PASS / 4 FAIL`` and main was red.
- No path in the filter changed afterwards, so the workflow never ran again. The
  last main run stayed the 07-13 failure, invisible.
- 2026-08-04, PR #481 touched ``scripts/check_posts.py`` (a filtered path), tripped
  the trigger, and inherited 4 FAILs it did not cause — reading as "this PR broke
  CI". Fixed in #489, trigger hardened here.

Two invariants keep that from recurring:

1. A ``schedule:`` cron runs the gate on main regardless of ``paths``, so a corpus
   regression surfaces within 24h instead of waiting for an unrelated change.
2. ``paths`` covers every script the steps actually invoke (self-consistency). A
   step added for a new script whose path is not filtered re-opens the same hole,
   just for a different file.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control) and NIST SSDF PO.3.
Direction: presence / superset assertions — narrowing the trigger or dropping the
schedule trips this; widening it stays green. If the gate is intentionally reworked
(e.g. the scan becomes diff-scoped so the narrow trigger is no longer a mismatch),
update this guard in the same PR and say why.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "check-svg.yml"

# Scripts whose changes must run the gate even though the guard derives the rest
# dynamically: check_svg_quality.py owns the corpus-wide PASS/FAIL verdict, so a
# change to it silently redefines what the gate means.
CORE_SCRIPT = "scripts/check_svg_quality.py"


def _noncomment_lines(text: str) -> str:
    """Workflow text with comment-only lines dropped.

    The rationale prose at the top of check-svg.yml names the very scripts and
    triggers this guard asserts on. Matching that commentary would keep the guard
    green after the real YAML was deleted, so comment-only lines are removed.
    Inline trailing comments survive because those lines are not comment-only.
    """
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _body() -> str:
    return _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))


def _invoked_scripts(body: str) -> set:
    """Repo-relative script paths the workflow's run: steps execute."""
    return set(re.findall(r"python3\s+(scripts/[\w./-]+\.py)", body))


def _filtered_paths(body: str) -> set:
    """Every quoted entry under a `paths:` list in the trigger block."""
    return set(re.findall(r"^\s*-\s*['\"]([^'\"]+)['\"]\s*$", body, re.MULTILINE))


def test_workflow_exists():
    assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"


def test_schedule_trigger_present():
    assert re.search(r"^\s*schedule:\s*$", _body(), re.MULTILINE), (
        "check-svg.yml lost its 'schedule:' trigger. The gate scans the whole "
        "corpus but is path-filtered, so without a scheduled run a regression on "
        "main stays invisible until some unrelated change touches a filtered path "
        "(observed 2026-07-13 -> 08-04, three weeks red). Re-add the cron, or make "
        "the scan diff-scoped and update this guard."
    )


def test_schedule_has_cron():
    crons = re.findall(r"-\s*cron:\s*[\"']([^\"']+)[\"']", _body())
    assert crons, (
        "the schedule: trigger has no 'cron:' entry, so the gate never runs on a "
        "timer and a corpus regression can sit undetected. Re-add a cron (e.g. "
        "'15 3 * * *'). If intentional, update this guard."
    )


def test_manual_dispatch_still_available():
    """workflow_dispatch is the escape hatch used to confirm a fix without a push."""
    assert re.search(r"^\s*workflow_dispatch:", _body(), re.MULTILINE), (
        "check-svg.yml lost workflow_dispatch; there is no way to re-run the gate "
        "on demand after fixing a corpus regression. If intentional, update this guard."
    )


def test_corpus_scan_still_covers_whole_directory():
    """The gate's value is the full-corpus verdict; narrowing it hides regressions."""
    body = _body()
    # Anchored at end-of-line: 'assets/images/one.svg' must NOT satisfy this, or the
    # assertion would pass while the scan had been narrowed to a single file.
    assert re.search(
        rf"{re.escape(CORE_SCRIPT)}\s+--fix\s+--ci\s+assets/images/\s*$",
        body,
        re.MULTILINE,
    ), (
        f"check-svg.yml no longer runs '{CORE_SCRIPT} --fix --ci assets/images/'. "
        "If the scan was narrowed to changed files only, that is a legitimate "
        "alternative fix for the trigger/scan mismatch — but then say so and update "
        "this guard (and test_schedule_trigger_present) in the same PR."
    )


def test_every_invoked_script_is_in_the_trigger_paths():
    """Self-consistency: a step's script must also be a filtered path.

    This is the general form of the 2026-07-13 hole. A new step added for a script
    outside `paths` means edits to that script never run the gate that depends on it.
    """
    body = _body()
    invoked = _invoked_scripts(body)
    assert invoked, "no 'python3 scripts/*.py' step found — did the steps move?"
    filtered = _filtered_paths(body)
    missing = sorted(s for s in invoked if s not in filtered)
    assert not missing, (
        "check-svg.yml runs these scripts but does not list them under 'paths', so "
        f"changing them never runs the gate that depends on them: {missing}. Add each "
        "to BOTH the push: and pull_request: paths lists."
    )


def test_workflow_file_itself_is_a_filtered_path():
    """Editing the gate must run the gate, or a weakening ships unverified."""
    filtered = _filtered_paths(_body())
    assert ".github/workflows/check-svg.yml" in filtered, (
        "check-svg.yml does not list itself under 'paths'. A change to the gate "
        "(including one that breaks it) would then merge without the gate ever "
        "running on the PR."
    )


def test_scripts_referenced_by_paths_exist():
    """Canary: a renamed script leaves a dead path filter that silently matches nothing."""
    filtered = _filtered_paths(_body())
    dead = sorted(
        p
        for p in filtered
        if p.startswith("scripts/") and not (REPO_ROOT / p).is_file()
    )
    assert not dead, (
        f"these trigger paths point at files that no longer exist: {dead}. A dead "
        "path filter matches nothing, so the gate stops running for that dependency."
    )
