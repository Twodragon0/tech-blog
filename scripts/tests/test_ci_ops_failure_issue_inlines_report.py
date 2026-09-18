#!/usr/bin/env python3
"""Guard: the ops failure issue must carry the report, not just a link to it.

Concrete incident
-----------------
`ops-orchestrator.yml`'s `Create issue on failure` step used to write a body
whose only evidence was::

    - Workflow run: <url>
    - Artifact: ops-roundtable-report

GitHub deletes workflow artifacts after 90 days. So every one of these issues
became unactionable on a timer — not because nobody read it, but because the
thing it pointed at stopped existing.

Measured 2026-09-18 across the 21 then-open issues (26 total, 5 closed):

    #191 (2026-03-23)  surviving artifacts: 0
    #394 (2026-06-08)  surviving artifacts: 0
    #400 (2026-06-09)  surviving artifacts: 0
    #643 (2026-08-31)  surviving              (expires 2026-11-29)

20 of 21 had already lost their only evidence. Month distribution was
2026-03 ×9, 2026-04 ×3, 2026-06 ×8, 2026-08 ×1 — against just 3 failures in the
last 200 runs, so this was never a volume problem.

Why inlining is safe
--------------------
The same text is already written to `$GITHUB_STEP_SUMMARY`, which is public on
this repo, so the issue body does not widen exposure. The report names
credentials by presence only — `Skipped (VERCEL_TOKEN not set)` — never values;
`scripts/ops_health_orchestrator.py` emits statuses, lint/mypy output and check
results.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ops-orchestrator.yml"


def _issue_step(text: str) -> str:
    """The `Create issue on failure` step block."""
    m = re.search(
        r"\n      - name: Create issue on failure\n((?:(?!\n      - name: ).)*)",
        text,
        re.S,
    )
    assert m, "`Create issue on failure` step not found — was it renamed or removed?"
    return m.group(1)


def _code(text: str) -> str:
    """The step with comment lines removed.

    A substring scan cannot tell a read from prose about a read. The first
    draft of `test_dedup_does_not_match_on_the_dated_title` failed against the
    correct workflow because the comment explaining the old bug quotes it
    verbatim — the same confusion that made the secret-contract check pass for
    the wrong reason on 2026-09-18, when three gateway names survived only in
    the partition guard's comments.

    Whole-line comments only (`#` for YAML, `//` for the embedded JS); a `//`
    appearing mid-expression is left alone.
    """
    return "\n".join(
        ln
        for ln in text.splitlines()
        if not ln.lstrip().startswith("#") and not ln.lstrip().startswith("//")
    )


def test_workflow_exists() -> None:
    assert WORKFLOW.is_file(), f"{WORKFLOW} not found — update this guard if moved."


def test_failure_issue_inlines_the_report() -> None:
    """The body must embed the report text, not only reference the artifact."""
    step = _code(_issue_step(WORKFLOW.read_text(encoding="utf-8")))
    assert "steps.report.outputs.message" in step, (
        "The failure issue no longer receives the roundtable report. Its body "
        "would be a link to an artifact that GitHub deletes after 90 days — "
        "which is how 20 of 21 open ops issues lost their only evidence."
    )
    assert "process.env.REPORT" in step, (
        "REPORT is passed to the step but never read in the script; the body "
        "would still contain no report."
    )


def test_truncation_is_explicit() -> None:
    """A silently cut report is the same defect as an expired artifact.

    GitHub caps an issue body at 65536 characters. The step must budget under
    that AND say so when it truncates, so a reader can tell "this is all of it"
    from "the rest is elsewhere".
    """
    step = _code(_issue_step(WORKFLOW.read_text(encoding="utf-8")))
    m = re.search(r"const LIMIT = (\d+);", step)
    assert m, "No explicit LIMIT — the body can exceed GitHub's 65536-char cap."
    limit = int(m.group(1))
    assert limit < 65536, (
        f"LIMIT is {limit}, at or above GitHub's 65536-char issue body cap. The "
        "surrounding prose also has to fit."
    )
    assert "truncated" in step, (
        "Truncation happens without saying so. Mark it, or a partial report "
        "reads as a complete one."
    )


def test_dedup_does_not_match_on_the_dated_title() -> None:
    """The duplicate check must not compare the title that carries the date.

    The original was `issues.find((issue) => issue.title === title)` where
    `title` ends in `(YYYY-MM-DD)`. A new date every day means the equality
    never held, so the dedup could not fire even once. Two streaks each opened
    one issue per day — 2026-03-23…04-03 (12 consecutive) and 2026-06-02…06-09
    (8) — which is 20 of the 21 issues it existed to prevent.
    """
    step = _code(_issue_step(WORKFLOW.read_text(encoding="utf-8")))
    assert "issue.title === title" not in step, (
        "Dedup compares the full dated title again. It can never match; use a "
        "date-free prefix."
    )
    assert "TITLE_PREFIX" in step and "startsWith(TITLE_PREFIX)" in step, (
        "Expected the duplicate check to match a date-free prefix so a repeat "
        "failure lands on the existing issue."
    )


def test_dedup_paginates() -> None:
    """One unpaginated page can hide the issue the dedup is looking for.

    `listForRepo` returns 30 per page by default and this repo held 21 open
    ops/automation issues at once — near enough that a second streak would push
    the match off page one and silently resume opening a new issue a day.
    """
    step = _code(_issue_step(WORKFLOW.read_text(encoding="utf-8")))
    assert "github.paginate" in step, (
        "The dedup reads a single page of issues. Use github.paginate so the "
        "match cannot fall off the end of page one."
    )


def test_duplicate_path_still_records_the_report() -> None:
    """On a match, append the report — do not drop it.

    The old branch was `if (!duplicate) { create }` with no else, so every
    repeat failure discarded its report entirely. That is the same evidence
    loss the inlining above exists to stop, just on a different path.
    """
    step = _code(_issue_step(WORKFLOW.read_text(encoding="utf-8")))
    assert "createComment" in step, (
        "The duplicate branch does nothing with the report. Comment it onto "
        "the existing issue so the evidence survives."
    )


def test_artifact_link_says_it_expires() -> None:
    """Keep the artifact link, but stop presenting it as durable evidence.

    It is still the fastest path to the full output inside the retention
    window; it just must not be the ONLY thing the issue offers.
    """
    step = _code(_issue_step(WORKFLOW.read_text(encoding="utf-8")))
    assert "ops-roundtable-report" in step, "Artifact reference dropped entirely."
    assert "expires" in step, (
        "The artifact is linked without noting that it expires. That framing is "
        "exactly what made the older issues look actionable when they were not."
    )
