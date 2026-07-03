#!/usr/bin/env python3
"""CI regression guards for two workflow-hardening invariants that no other test
protects (security-review 2026-07-01, gaps G2 and G3).

Why these guards exist
----------------------
G2 — token least-privilege. Every workflow currently declares a top-level
``permissions:`` block, and none uses ``write-all``. If someone deletes a
``permissions:`` block, the workflow silently reverts to the repository's
**default** ``GITHUB_TOKEN`` scope (often broad ``contents: write`` + more) — a
privilege escalation with no visible diff at the point of use. ``write-all`` is
the same failure stated explicitly. Branch protection / required checks do not
catch either. Direction: presence (``permissions:`` must exist) + absence
(``write-all`` must not).

  NOTE: top-level ``contents: write`` is intentionally allowed. Two single-purpose
  workflows legitimately need it at top level (``dependabot-auto-merge.yml``,
  ``visual-baseline-refresh.yml``); forcing job-scoping there is out of scope.
  This guard only blocks the two universally-clean regressions above.

G3 — no ``pull_request_target`` privilege-escalation shape. No workflow uses the
``pull_request_target`` trigger today. That trigger runs with a **read/write**
token and repo secrets in the context of a PR from a fork; combining it with a
checkout of the PR's untrusted head ref (``github.event.pull_request.head.*`` /
``github.head_ref``) is the canonical GitHub Actions RCE (an attacker's PR code
runs with the write token). This guard fails if that shape is introduced.

Maps to OWASP CICD-SEC-1 (Insufficient Flow Control) / CICD-SEC-4 (Poisoned
Pipeline Execution) and A05 (Security Misconfiguration). If a future workflow
must use ``pull_request_target``, it MUST NOT check out the untrusted head; keep
it to the base ref and update this guard in the same PR explaining why.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# Untrusted PR-head references that must never be checked out under
# pull_request_target.
_HEAD_REF_RE = re.compile(
    r"github\.event\.pull_request\.head\.(ref|sha)\b|github\.head_ref\b"
)

# G4: attacker-controlled free-text contexts that must not be interpolated into
# an action `with:` input value. Same untrusted set as the run:/github-script
# injection guard (kept in sync deliberately). These are DATA sinks (Slack
# payloads, comment bodies, ...), so this is defense-in-depth — not a
# proven-exploitable injection like the run:/script: cases — but interpolating
# an issue/PR title or comment body raw invites payload/markdown injection and
# secondary shell exposure if a downstream action forwards it. Step outputs,
# github.repository / run_id / sha / ref_name, and PR numbers are trusted and
# intentionally allowed.
_UNTRUSTED_CTX_RE = re.compile(
    r"github\.event\.inputs\."
    r"|github\.head_ref\b"
    r"|github\.event\.pull_request\.head\.ref\b"
    r"|github\.event\.pull_request\.(title|body)\b"
    r"|github\.event\.issue\.(title|body)\b"
    r"|github\.event\.comment\.body\b"
    r"|github\.event\.review\.body\b"
    r"|github\.event\.discussion\.(title|body)\b"
)
_EXPR_RE = re.compile(r"\$\{\{(.*?)\}\}", re.DOTALL)


def _flatten_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for v in value.values():
            yield from _flatten_strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _flatten_strings(v)


def _workflow_files():
    return sorted(WORKFLOW_DIR.glob("*.yml")) + sorted(WORKFLOW_DIR.glob("*.yaml"))


def _on_triggers(doc: dict):
    """Return the set of trigger names. PyYAML parses the bare ``on:`` key as the
    boolean ``True``, so check both keys."""
    on = doc.get("on", doc.get(True))
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    if isinstance(on, dict):
        return set(on.keys())
    return set()


def _steps(doc: dict):
    for job in (doc.get("jobs") or {}).values():
        if isinstance(job, dict):
            for step in job.get("steps") or []:
                if isinstance(step, dict):
                    yield step


def _load(wf: Path):
    try:
        return yaml.safe_load(wf.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise AssertionError(f"{wf.name} is not valid YAML: {exc}")


class TestWorkflowHardeningGuard:
    def test_workflow_dir_exists(self):
        assert WORKFLOW_DIR.is_dir(), f"{WORKFLOW_DIR} not found (moved/renamed?)"

    def test_workflow_files_present(self):
        assert _workflow_files(), "no workflow files found under .github/workflows"

    def test_every_workflow_has_top_level_permissions(self):
        missing = [
            wf.name
            for wf in _workflow_files()
            if isinstance(_load(wf), dict) and _load(wf).get("permissions") is None
        ]
        assert not missing, (
            "These workflows have no top-level `permissions:` block, so their "
            "GITHUB_TOKEN falls back to the repository default scope (often broad "
            "contents:write). Add an explicit least-privilege `permissions:` block "
            "(start from `contents: read`). Offending files:\n  - " + "\n  - ".join(missing)
        )

    def test_no_write_all_permissions(self):
        offenders = []
        for wf in _workflow_files():
            doc = _load(wf)
            if not isinstance(doc, dict):
                continue
            if doc.get("permissions") == "write-all":
                offenders.append(f"{wf.name} (top-level)")
            for job_name, job in (doc.get("jobs") or {}).items():
                if isinstance(job, dict) and job.get("permissions") == "write-all":
                    offenders.append(f"{wf.name} :: job '{job_name}'")
        assert not offenders, (
            "`permissions: write-all` grants every scope to GITHUB_TOKEN — the "
            "opposite of least privilege. Enumerate only the scopes actually "
            "needed. Offending sites:\n  - " + "\n  - ".join(offenders)
        )

    def test_no_pull_request_target_checking_out_untrusted_head(self):
        offenders = []
        for wf in _workflow_files():
            doc = _load(wf)
            if not isinstance(doc, dict):
                continue
            if "pull_request_target" not in _on_triggers(doc):
                continue
            for step in _steps(doc):
                if "checkout" not in str(step.get("uses", "")):
                    continue
                ref = str((step.get("with") or {}).get("ref", ""))
                if _HEAD_REF_RE.search(ref):
                    offenders.append(f"{wf.name} :: checkout ref={ref}")
        assert not offenders, (
            "A pull_request_target workflow checks out the PR's untrusted head ref "
            "— attacker-controlled code then runs with the read/write token and "
            "repo secrets (canonical GitHub Actions RCE). Do not check out the head "
            "ref under pull_request_target; use the base ref. Offending sites:\n  - "
            + "\n  - ".join(offenders)
        )

    def test_no_untrusted_context_in_action_with_inputs(self):
        # G4: defense-in-depth — untrusted free-text into a `with:` input value.
        # (github-script `script:` bodies are the run:-equivalent injection and
        # are covered by test_ci_no_run_input_interpolation_guard; skip them here.)
        offenders = []
        for wf in _workflow_files():
            doc = _load(wf)
            if not isinstance(doc, dict):
                continue
            for step in _steps(doc):
                with_block = step.get("with")
                if not isinstance(with_block, dict):
                    continue
                is_github_script = "github-script" in str(step.get("uses", ""))
                for input_name, value in with_block.items():
                    if is_github_script and input_name == "script":
                        continue
                    for s in _flatten_strings(value):
                        for m in _EXPR_RE.finditer(s):
                            if _UNTRUSTED_CTX_RE.search(m.group(1)):
                                offenders.append(
                                    f"{wf.name} :: input '{input_name}' :: {m.group(0).strip()}"
                                )
        assert not offenders, (
            "Attacker-controlled free-text context interpolated into an action "
            "`with:` input — route it through an env: var and have the step read "
            "$VAR (or use the action's structured/templated fields) so a payload "
            "cannot inject into the comment/Slack/webhook body. Offending sites:\n  - "
            + "\n  - ".join(offenders)
        )
