#!/usr/bin/env python3
"""CI regression guard: ops-orchestrator.yml privilege + secret partition.

Why this guard exists
---------------------
`ops-orchestrator.yml` consolidates four former ops workflows into ONE file with
three mutually-exclusive, ``if:``-gated jobs. Consolidation created a security
trap the multi-job design exists to avoid:

  * ``multi_agent`` needs elevated ``actions:write`` + ``issues:write`` (rerun
    failed workflows, open alert issues). If those permissions leaked onto a job
    reachable from the UNTRUSTED ``repository_dispatch`` path, an external
    ``client_payload`` could rerun arbitrary workflows / open issues
    (privilege escalation).
  * ``on_demand`` is the ONLY job reachable from ``repository_dispatch``. It must
    stay ``contents:read`` and keep secrets STEP-SCOPED (MED-2 hardening,
    dd0fc74e): job-level env may carry non-secret toggles and boolean
    has-secret presence flags (``secrets.X != ''``) but NEVER a raw secret VALUE
    (``${{ secrets.X }}``), which would expose it to every step incl. checkout.

Both invariants disappear *silently* under a careless edit. This guard makes
that regression fail loudly. Maps to OWASP CICD-SEC-1 / A02 (privilege + secret
exposure to untrusted input). If the partition is intentionally reworked, update
this guard in the same PR.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ops-orchestrator.yml"

# A raw secret VALUE assignment: `NAME: ${{ secrets.FOO }}`. Presence checks like
# `${{ secrets.FOO != '' }}` are deliberately NOT matched (they leak existence,
# not the value, and are the sanctioned MED-2 boolean flags).
SECRET_VALUE = re.compile(r":\s*\$\{\{\s*secrets\.[A-Z0-9_]+\s*\}\}")


def _load() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _job_block(text: str, job: str) -> str:
    """Return the raw text of one top-level job block (up to the next job)."""
    lines = text.splitlines()
    out: list[str] = []
    inside = False
    for ln in lines:
        if re.match(rf"^  {re.escape(job)}:\s*$", ln):
            inside = True
            continue
        if inside and re.match(r"^  [A-Za-z_][A-Za-z0-9_]*:\s*$", ln):
            break  # next top-level job
        if inside:
            out.append(ln)
    return "\n".join(out)


def _job_env_block(job_text: str) -> str:
    """The job-level ``env:`` block only (stops at the first ``steps:``)."""
    lines = job_text.splitlines()
    out: list[str] = []
    for ln in lines:
        if re.match(r"^    steps:\s*$", ln):
            break
        out.append(ln)
    return "\n".join(out)


class TestOpsOrchestratorPartitionGuard:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_three_jobs_present(self):
        jobs = _load()["jobs"]
        assert set(jobs) == {"multi_agent", "priority", "on_demand"}, (
            f"expected exactly the 3 partitioned jobs, found {sorted(jobs)}. "
            "The job topology changed; review the privilege/secret partition."
        )

    def test_elevated_perms_only_in_multi_agent(self):
        jobs = _load()["jobs"]
        for name, spec in jobs.items():
            perms = spec.get("permissions", {}) or {}
            elevated = {k for k, v in perms.items() if k in ("actions", "issues") and v == "write"}
            if name == "multi_agent":
                assert elevated == {"actions", "issues"}, (
                    "multi_agent must keep actions:write + issues:write; found "
                    f"{sorted(elevated)}."
                )
            else:
                assert not elevated, (
                    f"job `{name}` has elevated permissions {sorted(elevated)} but only "
                    "multi_agent may. This risks privilege escalation on a job "
                    "reachable from untrusted input."
                )

    def test_repository_dispatch_reaches_only_on_demand(self):
        jobs = _load()["jobs"]
        for name, spec in jobs.items():
            gate = str(spec.get("if", ""))
            mentions = "repository_dispatch" in gate
            if name == "on_demand":
                assert mentions, "on_demand `if:` must handle repository_dispatch."
            else:
                assert not mentions, (
                    f"job `{name}` references repository_dispatch in its `if:` gate. "
                    "Only on_demand (contents:read) may run on the untrusted path."
                )

    def test_multi_agent_unreachable_from_repository_dispatch(self):
        gate = str(_load()["jobs"]["multi_agent"].get("if", ""))
        # multi_agent must fire only on schedule or workflow_dispatch.
        assert "repository_dispatch" not in gate
        assert "schedule" in gate and "workflow_dispatch" in gate, (
            "multi_agent gate must be limited to schedule / workflow_dispatch so its "
            f"actions:write+issues:write stay off the untrusted path. Gate: {gate!r}"
        )

    def test_on_demand_secrets_are_step_scoped(self):
        text = WORKFLOW.read_text(encoding="utf-8")
        env_block = _job_env_block(_job_block(text, "on_demand"))
        leaked = [ln.strip() for ln in env_block.splitlines() if SECRET_VALUE.search(ln)]
        assert not leaked, (
            "on_demand job-level env exposes raw secret VALUE(s) to every step "
            "(MED-2 regression — secrets must be step-scoped):\n  "
            + "\n  ".join(leaked)
        )

    def test_on_demand_actually_uses_step_scoped_secrets(self):
        # Positive check: the step-scoped secrets still exist somewhere in the job
        # (guards against a "fix" that just deletes them).
        job_text = _job_block(WORKFLOW.read_text(encoding="utf-8"), "on_demand")
        assert SECRET_VALUE.search(job_text), (
            "on_demand no longer references any step-scoped secret; expected "
            "VERCEL/SENTRY/GITHUB + AI_GATEWAY/SLACK values on the steps that use them."
        )
