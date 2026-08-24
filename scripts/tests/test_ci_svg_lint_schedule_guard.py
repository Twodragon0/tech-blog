#!/usr/bin/env python3
"""CI regression guard: svg-lint.yml must keep a schedule, because its producer bypasses PRs.

Why this guard exists
---------------------
``svg-lint.yml`` carries 15 corpus-wide (``--all``) gates: cover drift for four
generator families, the honesty scorer, title-ASCII, spec-slug consistency,
KST-midnight URLs, checklist headings, bare URLs, template-echo. They scan the whole
corpus, so a narrow trigger produces the same trigger-narrower-than-scan hazard that
hid a three-week regression in ``check-svg.yml`` (see that file's header and
``test_ci_svg_gate_no_conceal_guard.py``).

Until 2026-08-10 this workflow had ``push`` + ``pull_request`` and no ``schedule`` —
exactly the pre-#489 shape. Measured that day:

- ``git log --format='%an' -40 -- 'assets/images/*.svg'`` -> **35 github-actions[bot]**
  direct pushes to main, 5 human commits. The blogwatcher cron is the dominant
  producer of the covers these gates check.
- A GITHUB_TOKEN push triggers no workflow (GitHub's recursion prevention, the same
  mechanism ``deploy-pages.yml`` documents and works around with its own cron).
- Bot cover commit ``685ca468`` carried 12 workflow runs, **every one ``schedule``**
  and not a single ``push`` or ``pull_request`` event.

So the artifacts these 15 gates exist to check arrived through the one path neither
trigger could see. A ``schedule`` is the only trigger that observes bot pushes, which
makes it load-bearing here rather than a nice-to-have.

Direction: presence assertions. Dropping the schedule or shrinking the corpus-wide
gate set trips this; adding triggers or gates stays green. If svg-lint is ever
reworked so every gate is diff-scoped (no ``--all``), the mismatch disappears and
this guard should be updated in the same PR with the reasoning.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "svg-lint.yml"

# A representative slice of the corpus-wide gates. Not the full 15: this guard
# should fail when the *category* is gutted, not churn on every gate addition.
CORPUS_WIDE_GATES = (
    "score_cover_honesty.py",
    "check_svg_title_ascii.py",
    "check_template_echo.py",
    "check_digest_checklist_heading.py",
)


def _noncomment_lines(text: str) -> str:
    """Workflow text with comment-only lines dropped.

    The header prose above names ``schedule``, ``cron`` and several gate scripts.
    Matching that commentary would keep this guard green after the real YAML was
    deleted, so comment-only lines are removed. Inline trailing comments survive
    because those lines are not comment-only.
    """
    return "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))


def _body() -> str:
    return _noncomment_lines(WORKFLOW.read_text(encoding="utf-8"))


def _triggers() -> set[str]:
    import yaml

    parsed = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    # PyYAML resolves the bare key `on:` to the boolean True.
    section = parsed[True] if True in parsed else parsed["on"]
    return set(section)


def test_workflow_exists():
    assert WORKFLOW.is_file(), f"missing {WORKFLOW}"


def test_schedule_trigger_present():
    assert "schedule" in _triggers(), (
        "svg-lint.yml has no 'schedule' trigger. Its 15 corpus-wide gates would then "
        "never see a blogwatcher cron push (GITHUB_TOKEN pushes fire no workflow), so "
        "a cover or digest regression published by the bot could sit on main "
        "indefinitely — the pre-#489 check-svg failure mode."
    )


def test_schedule_has_a_cron_expression():
    body = _body()
    schedule_at = body.find("schedule:")
    assert schedule_at != -1, "schedule: key missing from the YAML body"
    assert "cron:" in body[schedule_at:], "schedule: present but carries no cron entry"


def test_schedule_does_not_collide_with_check_svg_sweep():
    """Two full-corpus sweeps in the same minute contend for the runner pool."""
    import yaml

    def crons(path: Path) -> list[str]:
        parsed = yaml.safe_load(path.read_text(encoding="utf-8"))
        section = parsed[True] if True in parsed else parsed["on"]
        entries = section.get("schedule") or []
        return [e["cron"] for e in entries if isinstance(e, dict) and "cron" in e]

    ours = crons(WORKFLOW)
    theirs = crons(REPO_ROOT / ".github" / "workflows" / "check-svg.yml")
    assert ours, "svg-lint.yml must declare at least one cron"
    overlap = sorted(set(ours) & set(theirs))
    assert not overlap, (
        f"svg-lint.yml and check-svg.yml share cron slot(s) {overlap}; stagger them so "
        "the two corpus sweeps do not run simultaneously."
    )


def test_manual_dispatch_available():
    """Without dispatch, verifying a schedule-only change means waiting a day."""
    assert "workflow_dispatch" in _triggers(), (
        "svg-lint.yml should keep workflow_dispatch so the sweep can be run on demand "
        "after changing it, instead of trusting it until the next cron."
    )


def test_corpus_wide_gates_still_present():
    """The schedule only matters while corpus-wide gates justify it."""
    body = _body()
    missing = [g for g in CORPUS_WIDE_GATES if g not in body]
    assert not missing, (
        f"corpus-wide gate(s) gone from svg-lint.yml: {missing}. If every gate here is "
        "now diff-scoped, the trigger/scan mismatch this guard protects against no "
        "longer exists — update the guard deliberately rather than leaving it stale."
    )


def test_diff_scoped_steps_have_a_non_pull_request_base():
    """On a schedule run there is no pull_request context; the fallback must exist.

    A diff-scoped step branches on ``github.event_name`` and falls back to
    ``HEAD~1``. Without that fallback, ``origin/`` + an empty base ref would make
    the scheduled run fail on every diff-scoped gate — turning the trigger into
    daily noise that gets muted.

    This asserted a hardcoded ``>= 4`` until 2026-08-24. That number is not the
    invariant: it drifts down every time a gate correctly *stops* being
    diff-scoped, which is what happened when the digest untranslated and
    proper-noun gates moved to ``--all``. The property worth pinning is the
    pairing — each PR-side base assignment has a scheduled-run fallback — plus
    the fact that at least one diff-scoped step still exists to protect.
    """
    body = _body()
    pr_branches = body.count('github.event_name }}" = "pull_request"')
    pr_bases = body.count('BASE="origin/')
    fallbacks = body.count('BASE="HEAD~1"')

    assert pr_branches >= 1, (
        "no diff-scoped step left in svg-lint.yml. If every gate is now --all "
        "that is an improvement, not a failure — delete this test and say so."
    )
    assert pr_bases == pr_branches, (
        f"{pr_branches} event_name branch(es) but {pr_bases} origin/ base "
        "assignment(s); one diff-scoped step is not computing a PR base."
    )
    assert fallbacks == pr_branches, (
        f"{pr_branches} event_name branch(es) but {fallbacks} HEAD~1 "
        "fallback(s); a diff-scoped step would fail on the scheduled sweep "
        "instead of checking the latest commit."
    )
