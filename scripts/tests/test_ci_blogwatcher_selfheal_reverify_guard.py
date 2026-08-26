#!/usr/bin/env python3
"""CI regression guard: every cron self-heal must re-verify its own work.

`ai-blogwatcher.yml` publishes digests by pushing straight to main, so the pre-commit
hooks never see the post — the Actions commit runs with no local hooks. The workflow
compensates with self-heal pre-flight steps, and the shape that makes them trustworthy
is always the same three moves:

    if ! <check>; then warn; <fixer> || true; fi
    <check>          # re-verify, and BLOCK on a survivor

The `|| true` on the fixer is correct: a fixer crash must not be the thing that decides
whether the site publishes. The re-verify is what makes that safe — it converts "we
tried to fix it" into "it is actually fixed".

Audit finding (2026-08-10): three of the four self-heals had the re-verify. The
proper-noun one did not. It ran inside "Commit and publish" as
`check_digest_proper_nouns.py --fix … || true` with nothing after it, so a failed fix
shipped silently. Two things kept that from being caught elsewhere:

- pre-commit cannot see the post (no local hooks on the Actions commit), and
- the svg-lint proper-noun gate is diff-scoped (`--changed BASE`, BASE=HEAD~1 on
  non-PR events), so it only catches the bot's digest when that digest happens to be
  HEAD~1 when the sweep runs at 03:45 UTC. Any other commit landing in between and the
  violation ships uncaught.

Fixed 2026-08-11 by promoting it to its own pre-flight step with the standard shape.

Direction: this asserts the SHAPE, per gate. Adding a new self-heal without a re-verify
trips it; so does deleting a re-verify from an existing one.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"

# (step-name fragment, checker script, fixer script)
SELF_HEALS = (
    (
        "Canonical checklist heading pre-flight",
        "scripts/check_digest_checklist_heading.py",
        "scripts/restore_digest_structure.py",
    ),
    (
        "Template-echo summary pre-flight",
        "scripts/check_template_echo.py",
        "scripts/rewrite_template_echo_summaries.py",
    ),
    (
        "Proper-noun pre-flight",
        "scripts/check_digest_proper_nouns.py",
        "scripts/check_digest_proper_nouns.py --fix",
    ),
    (
        "Untranslated-summary pre-flight",
        "scripts/check_digest_untranslated.py",
        "scripts/retranslate_digest.py",
    ),
    (
        "Digest structure pre-flight",
        "scripts/check_digest_structure.py",
        "scripts/restore_digest_structure.py",
    ),
)


def _steps() -> dict[str, dict]:
    import yaml

    job = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["auto-publish"]
    return {s["name"]: s for s in job["steps"] if s.get("name")}


def _find_step(fragment: str) -> dict:
    for name, step in _steps().items():
        if fragment in name:
            return step
    pytest.fail(f"no step whose name contains {fragment!r} in ai-blogwatcher.yml")


def _uncommented(shell: str) -> str:
    """Shell text minus comment-only lines.

    Each of these steps explains the anti-pattern it avoids, naming the fixer and
    `|| true` in prose. Matching raw text would hit the explanation, and worse, would
    keep passing if the comment were deleted while the re-verify was too.
    """
    return "\n".join(ln for ln in shell.splitlines() if not ln.lstrip().startswith("#"))


@pytest.mark.parametrize(("fragment", "checker", "fixer"), SELF_HEALS)
def test_self_heal_reverifies_after_fixing(fragment: str, checker: str, fixer: str):
    run = _uncommented(_find_step(fragment)["run"])

    fixer_at = run.find(fixer)
    assert fixer_at != -1, f"{fragment}: fixer {fixer!r} is gone"

    # The checker must appear again AFTER the fixer, outside any `if !` condition.
    tail = run[fixer_at + len(fixer) :]
    reverify = [
        ln.strip()
        for ln in tail.splitlines()
        if checker in ln and not ln.strip().startswith("if ")
    ]
    assert reverify, (
        f"{fragment}: {checker} is never re-run after {fixer}. Without the re-verify "
        "the `|| true` on the fixer means a failed self-heal publishes silently — the "
        "exact hole the proper-noun step had until 2026-08-11."
    )


@pytest.mark.parametrize(("fragment", "checker", "fixer"), SELF_HEALS)
def test_reverify_is_not_itself_softened(fragment: str, checker: str, fixer: str):
    """A re-verify wrapped in `|| true` is decoration, not a gate."""
    run = _uncommented(_find_step(fragment)["run"])
    tail = run[run.find(fixer) + len(fixer) :]
    for line in tail.splitlines():
        if checker in line and not line.strip().startswith("if "):
            assert "|| true" not in line, (
                f"{fragment}: the re-verify is wrapped in '|| true', so a survivor "
                "still publishes"
            )
            return


def test_proper_nouns_no_longer_runs_inside_the_commit_step():
    """It has to be a pre-flight; inside the commit step there is nothing to block."""
    commit = _uncommented(_steps()["Commit and publish"]["run"])
    assert "check_digest_proper_nouns.py" not in commit, (
        "proper-noun --fix is back inside 'Commit and publish'. There it runs after the "
        "point where blocking is possible, which is how it went un-re-verified."
    )


def test_proper_noun_preflight_runs_under_the_same_partition():
    """Must share the trusted-event + post-created condition of its neighbours."""
    step = _find_step("Proper-noun pre-flight")
    assert step.get("if") == (
        "env.RUN_CHECKS == 'true' && steps.check_post.outputs.post_created == 'true'"
    ), (
        f"unexpected condition on the proper-noun pre-flight: {step.get('if')!r}. It "
        "should match the checklist-heading and template-echo steps exactly, so the "
        "untrusted-dispatch partition and the no-post case behave identically."
    )


def test_preflight_order_puts_all_gates_before_publish():
    """A gate after the commit cannot stop the commit."""
    names = list(_steps())
    publish_at = names.index("Commit and publish")
    for fragment, _checker, _fixer in SELF_HEALS:
        at = next(i for i, n in enumerate(names) if fragment in n)
        assert at < publish_at, f"{fragment} runs after 'Commit and publish'"


@pytest.mark.parametrize(("fragment", "checker", "fixer"), SELF_HEALS)
def test_last_executable_line_is_the_blocking_reverify(
    fragment: str, checker: str, fixer: str
):
    """The re-verify must be the step's *final* word, bare and unguarded.

    ``test_self_heal_reverifies_after_fixing`` only asks that the checker appear
    again somewhere after the fixer on a line not starting with ``if``. That is
    satisfiable without gating anything: the untranslated step runs the checker
    a second time inside its ``repository_dispatch`` branch, piped into
    ``|| echo ::warning::`` and followed by ``exit 0``. With only the weaker
    assertion in place, deleting that step's real blocking line — or softening
    it to ``|| true`` — left the suite green. Both mutations were run; both
    passed. So pin the position too, not just the presence.

    Under ``bash -e`` a bare non-zero command ends the step, which is what
    turns "we re-checked" into "we refused to publish".
    """
    run = _uncommented(_find_step(fragment)["run"])
    lines = [ln.rstrip() for ln in run.splitlines() if ln.strip()]
    assert lines, f"{fragment}: step body is empty"
    last = lines[-1].strip()
    assert checker in last, (
        f"{fragment}: the step's last executable line is {last!r}, not a bare "
        f"{checker} re-verify. Anything after the re-verify can swallow its exit "
        "code, and a re-verify that cannot end the step is decoration."
    )
    for softener in ("|| true", "|| echo", "continue-on-error"):
        assert softener not in last, (
            f"{fragment}: the final re-verify is softened with {softener!r}, so a "
            "surviving violation publishes anyway."
        )
    assert not last.startswith(("if ", "elif ", "#")), (
        f"{fragment}: the final re-verify is a condition, not a gate: {last!r}"
    )


def test_lone_adjective_stays_a_warning():
    """Deliberate contrast: that one IS a judgement call and must not block.

    Recorded so a future sweep does not "align" it with the blocking three. It fires on
    a cover headline reading like "Claude AI" — sometimes correct, sometimes not — and
    blocking there would stop publishing over a style opinion.
    """
    body = "\n".join(
        ln
        for ln in WORKFLOW.read_text(encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#")
    )
    assert re.search(r"check_digest_lone_adjective\.py", body), (
        "the lone-adjective check vanished"
    )
    assert "::warning::" in body
