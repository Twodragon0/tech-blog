"""Guard: the monthly report's notification must report the real outcome.

`.github/workflows/monthly-quality-report.yml` used to run its notification step
under `if: always()` with a hardcoded `--status "SUCCESS"` and the literal claim
"published to GitHub Issues", neither derived from whether `gh issue create`
actually ran. `always()` defeats the default skip-on-failure, so a failed issue
creation still announced success, and a manual dispatch with `create_issue=false`
announced a publication that never happened.

This is the third instance of the same bug class in this repo:
  1. `run-blog-autonomous-cron.sh` sent "Zero-Regression Gate: 100% Passed" as a
     constant regardless of the gate result (removed 2026-08-24).
  2. `monitoring.yml`'s Slack step was wired to a secret that was never
     configured, so a real failure alert went nowhere (fixed in PR #583).
  3. This one.

The pattern to block: a notification whose status is a literal rather than a
function of the thing it reports on.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "monthly-quality-report.yml"


def _text() -> str:
    assert WORKFLOW.exists(), f"{WORKFLOW} is missing"
    return WORKFLOW.read_text(encoding="utf-8")


def _uncommented(text: str) -> str:
    """Drop full-line comments.

    The repo has been bitten before by grep-style checks that matched the
    explanatory comment instead of the code — see notes/ci-gate-audit-2026-08.md.
    """
    return "\n".join(
        line for line in text.split("\n") if not line.lstrip().startswith("#")
    )


def test_create_issue_step_is_addressable():
    """Without an `id:` the step's outcome cannot be read by any later step."""
    body = _uncommented(_text())
    m = re.search(
        r"- name: Create or update issue\n(.*?)\n      - name: ", body, re.DOTALL
    )
    assert m, "the 'Create or update issue' step is gone or was renamed"
    assert re.search(r"^\s+id:\s*issue\s*$", m.group(1), re.MULTILINE), (
        "add `id: issue` back — the notification step derives its status from "
        "steps.issue.outcome, and without the id that expression is empty, which "
        "silently falls through to the FAILED branch."
    )


def test_notification_status_is_derived_not_hardcoded():
    body = _uncommented(_text())
    assert "steps.issue.outcome" in body, (
        "the notification status must come from the create-issue step's outcome"
    )
    assert not re.search(r'--status\s+"SUCCESS"', body), (
        'a literal --status "SUCCESS" is the bug this guard exists for; derive it '
        "from steps.issue.outcome instead"
    )


@pytest.mark.parametrize("state", ["SUCCESS", "WARNING", "FAILED"])
def test_all_three_outcome_states_are_distinguishable(state: str):
    """success / skipped / failed must not collapse into one message."""
    body = _uncommented(_text())
    assert f'STATUS="{state}"' in body, (
        f"the {state} branch is gone — success, skipped and failed have to stay "
        "tellable apart or the notification is back to asserting one state always"
    )


def test_no_step_output_is_interpolated_directly_into_a_run_block():
    """`${{ }}` inside `run:` is the Actions script-injection shape.

    These particular values are integer counts today, but routing them through
    `env:` costs nothing and removes the class. Mirrors
    test_ci_no_run_input_interpolation_guard.py.
    """
    body = _uncommented(_text())
    m = re.search(r"- name: Send Webhook Notification\n(.*)", body, re.DOTALL)
    assert m, "the notification step is gone or was renamed"
    step = m.group(1)
    run_idx = step.find("run: |")
    assert run_idx != -1, "notification step has no run: block"
    run_block = step[run_idx:]
    # Built outside the f-string: CI runs Python 3.11, where a backslash inside
    # an f-string expression is a SyntaxError (PEP 701 lifted that in 3.12, and
    # the local .venv is 3.14 — so this parses locally and breaks in CI).
    leaked = re.findall(r"\$\{\{[^}]*\}\}", run_block)
    assert "${{" not in run_block, (
        "pass step outputs through env: instead of interpolating them into the "
        f"shell: {leaked}"
    )


def test_report_template_no_longer_prescribes_boilerplate_injection():
    """The monthly report told the reader to keep injecting fixed diagrams.

    `generate_quality_report.py` shipped the action item "Mermaid 다이어그램
    미적용 포스트 지속적 주입" — which is the instruction that produced 43
    byte-identical fabricated diagrams. An action item that recreates the
    incident is worse than no action item.
    """
    src = (REPO_ROOT / "scripts" / "generate_quality_report.py").read_text(
        encoding="utf-8"
    )
    for banned in (
        "다이어그램 미적용 포스트 지속적 주입",
        "자율 현대화 크론 파이프라인",
    ):
        assert banned not in src, (
            f"{banned!r} refers to a removed pipeline or prescribes boilerplate "
            "injection; see notes/autonomous-modernizer-retro.md"
        )
