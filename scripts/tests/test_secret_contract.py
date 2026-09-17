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

import pytest  # noqa: E402
from check_secret_contract import (  # noqa: E402
    _REDACTED,
    DOCUMENTED_WITHOUT_CONSUMER,
    _safe_name,
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


@pytest.mark.parametrize(
    "value",
    [
        "xoxb-1234567890-abcdefghijkl",  # Slack bot token shape
        "sk_abcdef0123456789abcdef0123456789",  # ElevenLabs / OpenAI shape
        "ghp_AbCdEf0123456789AbCdEf0123456789AbCd",  # GitHub PAT shape
        '{"type": "service_account", "private_key": "-----BEGIN"}',  # GCP JSON
        "AbCdEf123+/=",  # mixed case / base64 padding
        "lowercase_name",
        "",
    ],
)
def test_value_shaped_strings_are_redacted(value: str) -> None:
    """Only bare SCREAMING_SNAKE names may leave this tool.

    Not hypothetical: CodeQL alert 290 (py/clear-text-logging-sensitive-data,
    high) fired on this script's own `print` because names parsed out of
    workflow `secrets.X` are a sensitive-data source to its taint analysis. The
    tool never handled values — `gh secret list` does not return them — but on a
    PUBLIC repo that has to be a checked property rather than a comment. Every
    real credential shape above must come back redacted.
    """
    assert _safe_name(value) == _REDACTED


@pytest.mark.parametrize(
    "name", ["SLACK_BOT_TOKEN", "GEMINI_API_KEY", "A1B", "ELEVENLABS_VOICE_ID"]
)
def test_real_names_survive_the_sanitizer(name: str) -> None:
    """The sanitizer must not be vacuous — a redact-everything version would
    pass the test above while making every message useless."""
    assert _safe_name(name) == name


def test_this_module_does_not_count_as_a_consumer() -> None:
    """The checker must not be its own consumer.

    First draft was. `DOCUMENTED_WITHOUT_CONSUMER` spells out
    ELEVENLABS_API_KEY and the tests above assert on it, so `git grep` found
    those two files and `--gh` reported **zero** dormant credentials on the run
    that was supposed to find two. A scanner that reads the file describing the
    rule always finds the rule's own example.
    """
    import check_secret_contract as mod

    assert "scripts/check_secret_contract.py" in mod._SELF_REFERENCES
    assert "scripts/tests/test_secret_contract.py" in mod._SELF_REFERENCES
    # And the exclusion must actually bite: this file names ELEVENLABS_API_KEY.
    assert mod.code_consumers("ELEVENLABS_API_KEY") == [], (
        "ELEVENLABS_API_KEY looks consumed. If a real consumer landed, drop it "
        "from DOCUMENTED_WITHOUT_CONSUMER; if it is this file again, extend "
        "_SELF_REFERENCES."
    )


def test_check_script_is_wired_to_this_test() -> None:
    """Canary: the script must stay importable from the suite.

    `check_broken_links.py` sat inert for months because nothing invoked it. A
    contract checker nobody runs is the same shape of defect.
    """
    assert (REPO_ROOT / "scripts" / "check_secret_contract.py").is_file()
    assert os.environ.get("PYTEST_CURRENT_TEST"), "expected to run under pytest"
