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

# ANY reference to a secret in an expression. Used by the allowlist check below
# so that fallback forms like `${{ secrets.FOO || '' }}` (which SECRET_VALUE's
# exact-shape regex would miss) are still caught as a value leak.
SECRET_REF = re.compile(r"secrets\.[A-Z0-9_]+")
# A sanctioned MED-2 presence flag leaks existence only: every secret token on
# the line is compared with `!= ''` and no raw-value/`|| ''` form is present.
PRESENCE_FLAG = re.compile(r"secrets\.[A-Z0-9_]+\s*!=\s*''")

# Jobs that MUST stay contents:read only (reachable from the untrusted path or
# lightweight): their permissions must equal exactly {contents: read}.
READ_ONLY_JOBS = ("priority", "on_demand")


def _job_env_secret_leaks(env_block: str) -> list[str]:
    """Job-level env lines that expose a raw secret VALUE (allowlist approach).

    A line is a LEAK if it references any `secrets.X` but is NOT a pure presence
    flag (`secrets.X != ''`). This catches the exact `${{ secrets.X }}` form AND
    fallback forms like `${{ secrets.X || '' }}` that a denylist regex misses.
    """
    leaks: list[str] = []
    for ln in env_block.splitlines():
        if SECRET_REF.search(ln) and not PRESENCE_FLAG.search(ln):
            leaks.append(ln.strip())
    return leaks


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

    def test_read_only_jobs_have_exactly_contents_read(self):
        # Equality check (not just "no actions/issues"): catches ANY new elevated
        # key on the read-only jobs, e.g. id-token:write, pull-requests:write,
        # packages:write — which an actions/issues-only check would miss.
        jobs = _load()["jobs"]
        for name in READ_ONLY_JOBS:
            perms = jobs[name].get("permissions", {}) or {}
            assert perms == {"contents": "read"}, (
                f"job `{name}` permissions must equal exactly {{contents: read}}; "
                f"found {perms}. Any extra grant widens the attack surface on a job "
                "reachable from untrusted input (on_demand) or on the lightweight lane."
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

    def test_read_only_jobs_secrets_are_step_scoped(self):
        # MED-2 for BOTH untrusted (on_demand) and lightweight (priority) jobs:
        # no raw secret VALUE at job-level env — only non-secret toggles and
        # `secrets.X != ''` presence flags. Allowlist-based so fallback forms
        # like `${{ secrets.X || '' }}` are also caught (denylist regex misses).
        text = WORKFLOW.read_text(encoding="utf-8")
        for name in READ_ONLY_JOBS:
            env_block = _job_env_block(_job_block(text, name))
            leaks = _job_env_secret_leaks(env_block)
            assert not leaks, (
                f"{name} job-level env exposes raw secret VALUE(s) to every step "
                "(incl. checkout/install) — MED-2 regression, secrets must be "
                "step-scoped:\n  " + "\n  ".join(leaks)
            )

    def test_read_only_jobs_actually_use_step_scoped_secrets(self):
        # Positive check: step-scoped secrets still exist somewhere in each job
        # (guards against a "fix" that just deletes them, killing Slack/checks).
        text = WORKFLOW.read_text(encoding="utf-8")
        for name in READ_ONLY_JOBS:
            job_text = _job_block(text, name)
            assert SECRET_VALUE.search(job_text), (
                f"{name} no longer references any step-scoped secret; expected the "
                "AI_GATEWAY/SLACK (and, for on_demand, VERCEL/SENTRY/GITHUB) values "
                "on the steps that use them."
            )
