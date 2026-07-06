#!/usr/bin/env python3
"""CI regression guard: blogwatcher LLM secrets must stay off the untrusted path.

Why this guard exists
---------------------
`ai-blogwatcher.yml` publishes via two paths: the TRUSTED schedule/workflow_dispatch
path (direct push to main) and the UNTRUSTED `repository_dispatch` path (external
`client_payload`, quarantined to a PR). The PR quarantine protects `main` but NOT
the secrets: the 2026-07-06 audit (MED-1) found all four LLM API keys
(GEMINI/CLAUDE/OPENAI/DEEPSEEK) were live on the untrusted path — the job-level
`env:` set them unconditionally and the step-level re-declaration defaulted
`USE_AI=auto`, which un-gates every key. A poisoned feed could then reach a live
key.

The fix gates every key expression on `github.event_name != 'repository_dispatch'`
so the untrusted path always resolves them to `''`. That partition disappears
*silently* if someone drops the gate from any key line (job-level OR step-level).
This guard makes that removal fail loudly.

Maps to OWASP CICD-SEC-1 / A02 (secret exposure to untrusted input). Direction:
presence assertion — EVERY line assigning a `*_API_KEY:` from `secrets.*` must
carry the trusted-path gate. If the partition is intentionally reworked, update
this guard in the same PR.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "ai-blogwatcher.yml"

# The trusted-path gate every secret expression must contain (normalised on
# whitespace so single/double quotes and spacing don't cause false failures).
GATE = "github.event_name != 'repository_dispatch'"


def _key_lines(text: str) -> list[str]:
    """Non-comment lines that assign a ``*_API_KEY:`` from ``secrets.*``.

    Comment-only lines are skipped so prose mentioning the gate can't satisfy the
    guard, and so a commented-out key line isn't asserted on.
    """
    out = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("#"):
            continue
        if re.match(r"[A-Z0-9_]*API_KEY:\s*", s) and "secrets." in s:
            out.append(ln)
    return out


class TestBlogwatcherSecretPartitionGuard:
    def test_workflow_exists(self):
        assert WORKFLOW.is_file(), f"{WORKFLOW} not found (moved/renamed?)"

    def test_api_key_lines_present(self):
        lines = _key_lines(WORKFLOW.read_text(encoding="utf-8"))
        # Two blocks (job-level env + the 'Auto publish digest' step env), 4 keys
        # each = 8. If the count drops the structure changed — review, don't
        # silently pass.
        assert len(lines) >= 8, (
            f"expected >=8 *_API_KEY secret assignments (job + step level), found "
            f"{len(lines)}. The env structure changed; review the secret partition "
            "and update this guard."
        )

    def test_every_key_gated_on_trusted_path(self):
        lines = _key_lines(WORKFLOW.read_text(encoding="utf-8"))
        ungated = [ln.strip() for ln in lines if GATE not in ln]
        assert not ungated, (
            "these blogwatcher API-key expressions are NOT gated on the trusted "
            f"path (missing `{GATE}`), so the untrusted repository_dispatch payload "
            "would receive a live LLM key (MED-1 secret-exposure regression):\n  "
            + "\n  ".join(ungated)
            + "\nRe-add the gate; if the partition was intentionally reworked, "
            "update this guard."
        )
