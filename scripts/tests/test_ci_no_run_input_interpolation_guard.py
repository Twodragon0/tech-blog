#!/usr/bin/env python3
"""CI regression guard: no untrusted ``${{ ... }}`` context interpolated into a
``run:`` shell body.

Why this guard exists
---------------------
Commit ``80dc060f`` fixed 6 shell-injection sites where ``workflow_dispatch``
inputs and git-diff-derived filenames were interpolated **straight into a
``run:`` script** via ``${{ ... }}``. GitHub expands ``${{ }}`` into the script
text *before* the shell executes it, so a value such as ``$(id)``, backticks, or
``; rm -rf`` in an operator-supplied (``github.event.inputs.*``) or
attacker-supplied (``github.head_ref``, PR/issue/comment title & body) field runs
as code. The fix routes every such value through an ``env:`` var and references
it as a quoted ``"$VAR"`` — GitHub writes the value to the environment literally
and the shell never re-parses it as syntax.

That protection regresses **silently** the moment someone re-adds a raw
``${{ github.event.inputs.X }}`` (or ``github.head_ref`` / a PR-title-style
field) inside a ``run:`` block. This guard scans every workflow and fails loudly.

Scope / direction
-----------------
- Presence assertion: **any** forbidden context inside a ``run:`` body trips it.
- Only ``run:`` script bodies are scanned. Passing a value via ``env:``
  (``env: FOO: ${{ github.event.inputs.x }}``) is the CORRECT remediation and is
  intentionally NOT flagged. ``if:``/``with:``/other keys are GitHub-expression
  contexts (not a shell) and are out of scope.
- Forbidden contexts are the injectable ones only. GitHub-controlled scalars that
  are NOT attacker-influenced shell metacharacter carriers — ``pull_request.number``
  (int), ``*.sha`` (hex), ``github.run_id``, ``github.event_name``,
  ``steps.*.outputs.*`` — are deliberately allowed so the guard stays focused and
  false-positive-free. If you must interpolate a genuinely new safe context,
  extend ``_SAFE_ALLOW`` with a one-line justification.

Maps to OWASP CICD-SEC-4 (Poisoned Pipeline Execution) and CWE-94/78 (code /
command injection). If a future workflow legitimately needs one of these values,
route it through ``env:`` and quote it — do not weaken this guard.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# ``${{ <expr> }}`` occurrences (non-greedy so multiple per line are captured).
_EXPR_RE = re.compile(r"\$\{\{(.*?)\}\}", re.DOTALL)

# Untrusted contexts that must never be interpolated raw into a shell body.
# Operator-supplied (workflow_dispatch) + attacker-supplied (fork branch name,
# PR / issue / comment / review free-text) — all can carry shell metacharacters.
_FORBIDDEN_RE = re.compile(
    r"github\.event\.inputs\."
    r"|github\.head_ref\b"
    r"|github\.event\.pull_request\.head\.ref\b"
    r"|github\.event\.pull_request\.(title|body)\b"
    r"|github\.event\.issue\.(title|body)\b"
    r"|github\.event\.comment\.body\b"
    r"|github\.event\.review\.body\b"
    r"|github\.event\.discussion\.(title|body)\b"
)


def _run_bodies(workflow: object):
    """Yield ``(job_name, step_name, run_text)`` for every step-level ``run:``."""
    if not isinstance(workflow, dict):
        return
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict):
        return
    for job_name, job in jobs.items():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and isinstance(step.get("run"), str):
                yield job_name, step.get("name", "<unnamed>"), step["run"]


def _scan(text: str):
    """Return the list of forbidden ``${{ }}`` expressions found in *text*."""
    return [
        m.group(0).strip()
        for m in _EXPR_RE.finditer(text)
        if _FORBIDDEN_RE.search(m.group(1))
    ]


def _workflow_files():
    return sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))


class TestNoRunInputInterpolationGuard:
    def test_workflow_dir_exists(self):
        assert WORKFLOW_DIR.is_dir(), f"{WORKFLOW_DIR} not found (moved/renamed?)"

    def test_workflow_files_present(self):
        # Canary: a vacuous pass (zero files scanned) must fail clearly.
        assert _workflow_files(), "no workflow files found under .github/workflows"

    def test_no_untrusted_context_in_run_bodies(self):
        offenders = []
        for wf in _workflow_files():
            try:
                doc = yaml.safe_load(wf.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:  # malformed YAML is its own failure
                raise AssertionError(f"{wf.name} is not valid YAML: {exc}")
            for job_name, step_name, run_text in _run_bodies(doc):
                for expr in _scan(run_text):
                    offenders.append(f"{wf.name} :: job '{job_name}' :: step '{step_name}' :: {expr}")

        assert not offenders, (
            "Untrusted ${{ }} context interpolated directly into a run: shell body "
            "— this is a shell-injection vector (see commit 80dc060f). Route the "
            "value through an env: var on the step and reference it as a quoted "
            '"$VAR" instead. Offending sites:\n  - ' + "\n  - ".join(offenders)
        )
