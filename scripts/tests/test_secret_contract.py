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

    These are floors against the EXTRACTOR breaking, not a claim that the counts
    never fall. A deliberate removal legitimately lowers the second one, and the
    floor gets lowered with it — in the same change, with the reason:

        2026-09-17  24 documented / 21 read by workflows   (initial measurement)
        2026-09-17  …            / 20   USE_GEMINI_PRO_IMAGE moved to `vars.`
        2026-09-18  …            / 17   AI_GATEWAY_URL + AI_GATEWAY_TOKEN +
                                        SLACK_CHANNEL_ID_OPS references removed
                                        with the three never-executed
                                        ops-orchestrator Slack steps
        2026-09-18  …            / 16   PAGESPEED_API_KEY removed with
                                        check_uiux() — the measurement already
                                        existed in lighthouse-ci.yml and
                                        lighthouse.yml

    A collapse to single digits means `_DOC_ENTRY_RE` / `_WORKFLOW_SECRET_RE`
    stopped matching — fix the regex, do not lower the floor to meet it.
    """
    documented = documented_secrets()
    consumed = workflow_secrets()
    assert len(documented) >= 20, (
        f"Only {len(documented)} secret(s) parsed out of SECRETS_MANAGEMENT.md "
        "(24 on 2026-09-18). The doc format probably changed — fix _DOC_ENTRY_RE "
        "rather than letting the contract check pass on an empty set."
    )
    assert len(consumed) >= 15, (
        f"Only {len(consumed)} secret(s) found in .github/workflows/ (16 on "
        "2026-09-18). Check _WORKFLOW_SECRET_RE before assuming secrets were "
        "removed on purpose."
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


def test_elevenlabs_exemption_records_the_resolution() -> None:
    """The entry must say the credential is gone, not that a decision is pending.

    It was provisioned 2026-01-11 with no consumer and deleted 2026-09-17 after
    measuring that "move it to online-course" was not even a real option:
    Actions secrets are repo-scoped, online-course has zero Actions secrets, and
    its copies of the scripts read `os.getenv("ELEVENLABS_API_KEY")` from the
    local environment. The name stays documented so the guide can say "do not
    set this here" — an undocumented name invites someone to re-add it.

    If a consumer ever lands in THIS repo, drop the entry entirely rather than
    editing this reason.
    """
    reason = DOCUMENTED_WITHOUT_CONSUMER.get("ELEVENLABS_API_KEY", "")
    assert "RESOLVED" in reason, (
        "The ELEVENLABS_API_KEY exemption no longer records that the secret was "
        "deleted. If it was re-provisioned, say why and what consumes it; if a "
        "consumer landed, drop the entry."
    )
    assert "pending" not in reason.lower(), (
        "The exemption still reads as awaiting a decision. It was decided on "
        "2026-09-17 — the secret is deleted."
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


def test_config_flags_are_variables_not_secrets() -> None:
    """A switch with a documented default is configuration, not a credential.

    `USE_GEMINI_PRO_IMAGE` was read as `${{ secrets.USE_GEMINI_PRO_IMAGE ||
    'false' }}` — a boolean with a default, stored where its value is masked. The
    cost is not theoretical: nobody can answer "is Pro on right now?" from an
    audit of secrets, and a credential-contract check like this one counts it as
    a key. Moved to `vars.` on 2026-09-17, alongside the five switches already
    using that context (AI_BLOGWATCHER_SCHEDULE, GSC_SITE_URL, …).

    Add a name here when you introduce another flag; do not relax the assertion.
    """
    flags = ("USE_GEMINI_PRO_IMAGE",)
    offenders = []
    for path in sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        for flag in flags:
            if f"secrets.{flag}" in text:
                offenders.append(f"{path.name} reads secrets.{flag}")
    assert offenders == [], (
        "\n".join(offenders) + "\n\nThese are configuration flags with defaults, "
        "not credentials. Use `vars.<NAME>` so the value stays visible."
    )


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


def test_comments_do_not_count_as_consumers() -> None:
    """Prose about a secret is not a read of it.

    Two instances on 2026-09-18, hours apart, in opposite directions:

    * The AI-Gateway trio survived only in `test_ci_ops_orchestrator_partition_
      guard.py`'s COMMENTS after their steps were deleted, so the contract check
      passed for the wrong reason.
    * Removing `PAGESPEED_API_KEY` left three files explaining WHY it was
      removed. `git grep -l` counted all three as consumers and the check again
      reported 0 violations — for a secret that by then had none.

    A checker whose only question is "does anything actually read this" cannot
    answer it with a scan that reads its own removal notes as usage.
    """
    import check_secret_contract as mod

    assert mod.code_consumers("PAGESPEED_API_KEY") == [], (
        "PAGESPEED_API_KEY looks consumed. If the hits are the removal-rationale "
        "comments again, the comment filter regressed; if a real consumer landed, "
        "drop it from DOCUMENTED_WITHOUT_CONSUMER and see the entry there first — "
        "the decision was DO NOT PROVISION."
    )
    # Not vacuous: live credentials must still resolve to real consumers.
    for name in ("VERCEL_TOKEN", "SENTRY_AUTH_TOKEN", "SLACK_BOT_TOKEN"):
        assert mod.code_consumers(name), (
            f"{name} now looks unused. The comment filter is over-stripping — it "
            "must drop whole-line comments only, never code."
        )


def test_pagespeed_decision_says_do_not_provision() -> None:
    """The entry must carry the decision, not just the absence.

    "Nothing reads it" invites someone to wire it back up. The measured reason
    is the opposite: `check_uiux` gated on a performance score the repo recorded
    at 0.55-0.86 on unchanged content and an LCP threshold below BOTH modes of a
    bimodal distribution, and its failures are P1 — the priority that opens an
    ops issue on a 6-hourly cron.
    """
    reason = DOCUMENTED_WITHOUT_CONSUMER.get("PAGESPEED_API_KEY", "")
    assert "DO NOT PROVISION" in reason, (
        "The PAGESPEED_API_KEY entry no longer records that provisioning it is "
        "the wrong move. If that changed, say what measurement changed it."
    )
    assert "lighthouse" in reason.lower(), (
        "The entry should name where the measurement actually lives, or the next "
        "reader will think CWV monitoring was simply dropped."
    )


def test_docstrings_do_not_count_as_consumers(tmp_path, monkeypatch) -> None:
    """A name inside a `\"\"\"...\"\"\"` is prose, not a read.

    Found the hard way on 2026-09-19: adding `scripts/dev/probe_guard_vacuity.py`,
    whose module docstring *describes* the PAGESPEED_API_KEY incident, made that
    secret look consumed again — breaking the very guard written to catch this.
    The earlier version called leaving docstrings in "the safe direction"; it was
    just the unbuilt one.

    It also only failed after `git add`, because `code_consumers` walks
    `git grep` and that reads the index. A bare `pytest` on an untracked file
    passed while the pre-commit hook failed.
    """
    import check_secret_contract as mod

    assert mod.code_consumers("PAGESPEED_API_KEY") == [], (
        "PAGESPEED_API_KEY looks consumed again. If the hits are prose — a "
        "docstring or a comment describing the removal — the filter regressed."
    )


def test_docstring_filter_is_not_over_broad(tmp_path) -> None:
    """Only a bare string STATEMENT is a docstring.

    A string that is assigned, passed or returned is data — `os.getenv("X")`,
    a lookup table, an f-string command — and must keep counting. Stripping
    those would declare live credentials dead, which is the expensive direction.
    """
    import check_secret_contract as mod

    src = tmp_path / "sample.py"
    src.write_text(
        '''"""Module prose mentioning DOCSTRING_ONLY_NAME."""

import os

VALUE = os.getenv("REAL_CODE_NAME", "")


def f():
    """Function prose mentioning DOCSTRING_ONLY_NAME again."""
    return VALUE
''',
        encoding="utf-8",
    )
    doc_lines = mod._docstring_lines(src)
    text = src.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(text, 1):
        if "DOCSTRING_ONLY_NAME" in line:
            assert i in doc_lines, f"line {i} is a docstring but was not detected"
        if "REAL_CODE_NAME" in line:
            assert i not in doc_lines, (
                f"line {i} is an os.getenv call, not a docstring — the filter is "
                "over-broad and would declare live secrets unused."
            )
