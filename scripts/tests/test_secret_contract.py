#!/usr/bin/env python3
"""Runs the credentials-free half of scripts/check_secret_contract.py.

The provisioning half (`--gh`) is deliberately NOT here: it needs an
authenticated `gh`, and a suite that fails without credentials is a suite people
learn to ignore. Same split as check_runtime_env_contract.py / its test.

What this protects, measured 2026-09-17:

* `ELEVENLABS_API_KEY` / `ELEVENLABS_VOICE_ID` — provisioned since 2026-01-11
  with zero consumers, because `cfe0d82d` moved `ai-video-gen.yml` and
  `generate_enhanced_audio.py` to the online-course repo and left the secrets.
* 12 secrets read by workflows that `SECRETS_MANAGEMENT.md` never mentioned,
  including `SLACK_BOT_TOKEN` / `SLACK_CHANNEL_ID`, which five fail-closed
  workflows depend on. Setting the repo up from the guide produced failing jobs.

Neither direction was checked by anything. The three existing credential guards
all read outward from a reference (`.github/workflows/` → secret, `api/` →
`process.env`), so "documented or provisioned but consumed by nothing" was a
structural blind spot.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from check_secret_contract import (  # noqa: E402
    DOCUMENTED_WITHOUT_CONSUMER,
    check_doc_consumer_sync,
    documented_secrets,
    workflow_secrets,
)


def test_secret_doc_and_consumers_agree() -> None:
    """Every documented secret has a consumer, every consumed secret is documented."""
    problems = check_doc_consumer_sync()
    assert problems == [], "\n".join(problems)


def test_scanners_are_not_vacuous() -> None:
    """A regex that stops matching would make the check above pass trivially.

    Both numbers are floors, not exact counts — they should only ever grow, and a
    collapse means the extractor broke rather than the repo shrinking. Measured
    2026-09-17: 24 documented, 21 read by workflows.
    """
    documented = documented_secrets()
    consumed = workflow_secrets()
    assert len(documented) >= 20, (
        f"Only {len(documented)} secret(s) parsed out of SECRETS_MANAGEMENT.md "
        "(24 on 2026-09-17). The doc format probably changed — fix _DOC_ENTRY_RE "
        "rather than letting the contract check pass on an empty set."
    )
    assert len(consumed) >= 18, (
        f"Only {len(consumed)} secret(s) found in .github/workflows/ (21 on "
        "2026-09-17). Check _WORKFLOW_SECRET_RE."
    )


def test_every_exemption_states_what_would_remove_it() -> None:
    """An exemption without an exit condition is a permanent hole.

    This is the failure mode the repo has already paid for: an allow-list entry
    outlives its reason, nobody can tell whether it is still true, and removing
    it silently drops its carriers out of coverage.
    """
    vague = [
        name for name, reason in DOCUMENTED_WITHOUT_CONSUMER.items() if len(reason) < 40
    ]
    assert vague == [], (
        f"{vague} are exempted with a reason too short to act on. Say what the "
        "secret is for, why nothing reads it, and what would take it off the list."
    )


def test_elevenlabs_exemption_is_still_flagged_as_pending() -> None:
    """The dormant credential must not quietly become 'normal'.

    ELEVENLABS_* is exempted only because deleting or rotating a secret is an
    owner decision, not because the situation is fine. If someone resolves it,
    the entry should leave DOCUMENTED_WITHOUT_CONSUMER — not have its wording
    softened until the exemption reads like a design choice.
    """
    reason = DOCUMENTED_WITHOUT_CONSUMER.get("ELEVENLABS_API_KEY", "")
    assert "PROVISIONED" in reason and "decision" in reason, (
        "The ELEVENLABS_API_KEY exemption no longer records that it is a live, "
        "provisioned credential awaiting an owner decision. Either resolve it "
        "(revoke + `gh secret delete`, or move it to the online-course repo) and "
        "drop the entry, or keep the wording explicit."
    )


def test_check_script_is_wired_to_this_test() -> None:
    """Canary: the script must stay importable from the suite.

    `check_broken_links.py` sat inert for months because nothing invoked it. A
    contract checker nobody runs is the same shape of defect.
    """
    assert (REPO_ROOT / "scripts" / "check_secret_contract.py").is_file()
    assert os.environ.get("PYTEST_CURRENT_TEST"), "expected to run under pytest"
