#!/usr/bin/env python3
"""CI regression guard: the digest-translate-backfill workflow must stay trusted.

Why this guard exists
---------------------
`digest-translate-backfill.yml` runs the LLM re-translation pass (재발 방지 B단계)
WITH `GEMINI_API_KEY`/`DEEPSEEK_API_KEY` in scope. That is only safe because the
workflow is un-triggerable by external parties: it has NO `repository_dispatch`
trigger, and every key expression is additionally gated on the trusted path
(`github.event_name != 'repository_dispatch'`, belt-and-suspenders with the
job-level schedule/workflow_dispatch allowlist `if`).

Either protection can disappear *silently* — a future edit adding a
`repository_dispatch` trigger, or dropping the gate from a key line, would hand a
live LLM key to an attacker-controlled `client_payload` (the exact MED-1
secret-exposure failure mode the sibling blogwatcher guard was built to catch).
This guard makes that regression fail loudly.

Maps to OWASP CICD-SEC-1 / A02 (secret exposure to untrusted input). If the
partition is intentionally reworked, update this guard in the same PR.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "digest-translate-backfill.yml"

GATE = "github.event_name != 'repository_dispatch'"


def _triggers(text: str) -> list:
    """Return the workflow's `on:` trigger keys (YAML parses `on` as True)."""
    doc = yaml.safe_load(text)
    on = doc.get("on", doc.get(True))
    if isinstance(on, dict):
        return list(on.keys())
    if isinstance(on, list):
        return list(on)
    return [on]


def _key_lines(text: str) -> list:
    """Non-comment lines assigning a ``*_API_KEY:`` from ``secrets.*``."""
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            continue
        if re.match(r"[A-Z0-9_]*API_KEY:\s*", s) and "secrets." in s:
            out.append(ln)
    return out


class TestDigestTranslatePartitionGuard:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_no_repository_dispatch_trigger(self):
        triggers = _triggers(WORKFLOW.read_text(encoding="utf-8"))
        assert "repository_dispatch" not in triggers, (
            "digest-translate-backfill.yml must NOT be triggerable by "
            "repository_dispatch — that path is externally controllable and this "
            f"workflow runs with live LLM keys. Found triggers: {triggers}. "
            "Remove the trigger, or if reworking the trust model, update this guard."
        )

    def test_every_key_gated_on_trusted_path(self):
        lines = _key_lines(WORKFLOW.read_text(encoding="utf-8"))
        assert lines, (
            "no *_API_KEY secret assignments found — the workflow structure "
            "changed; review the secret partition and update this guard."
        )
        ungated = [ln.strip() for ln in lines if GATE not in ln]
        assert not ungated, (
            "these digest-translate API-key expressions are NOT gated on the "
            f"trusted path (missing `{GATE}`); a future repository_dispatch trigger "
            "would then hand over a live LLM key (MED-1 secret-exposure "
            "regression):\n  " + "\n  ".join(ungated)
        )
