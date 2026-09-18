#!/usr/bin/env python3
"""Keep the secrets guide, the workflows, and the provisioned secrets in sync.

Why this exists
---------------
Three guards already cover credentials, and all three read the SAME direction —
from a *reference* outward:

* ``test_ci_secret_absence_guard.py`` walks ``.github/workflows/`` and asserts
  each referenced secret either fails closed or is listed as never-configured.
* ``check_runtime_env_contract.py`` walks ``api/`` for ``process.env.*``.
* ``test_retired_social_secrets_…`` asserts the retired SNS names are *not*
  referenced.

Nothing read the other direction: a secret that is **documented or provisioned
while nothing consumes it**. Measured 2026-09-17, that blind spot held three
entries, and one of them was live:

* ``ELEVENLABS_API_KEY`` / ``ELEVENLABS_VOICE_ID`` — provisioned 2026-01-11,
  zero workflow references, zero code references. Their only consumers,
  ``ai-video-gen.yml`` and ``generate_enhanced_audio.py``, both left the repo in
  commit ``cfe0d82d``. A paid third-party credential sat in repo settings for
  eight months with nothing able to use it.
* ``GEMINI_SERVICE_ACCOUNT_KEY`` — documented as "⭐ 권장" with setup steps, never
  provisioned, no consumer. Following the guide would have created a fourth.

And the reverse gap was worse for a newcomer: ``SLACK_BOT_TOKEN`` /
``SLACK_CHANNEL_ID`` are read by six workflows — five of them fail-closed — and
were **absent from the guide entirely**. Setting the repo up by following the
document produced failing notification jobs.

What it checks
--------------
Two directions, and only the first needs no credentials:

1. **Doc ↔ consumer sync (always, runs in pytest).**
   - Every secret documented in ``SECRETS_MANAGEMENT.md`` must have a consumer
     (a workflow or a tracked script), or be listed in
     ``DOCUMENTED_WITHOUT_CONSUMER`` with the reason.
   - Every secret a workflow reads must be documented. This is the direction
     that would have caught the missing Slack section.
2. **Provisioning (``--gh``, opt-in).** Runs ``gh secret list`` and reports
   provisioned names that nothing consumes. Needs an authenticated ``gh``, so it
   is an owner command, not a CI gate. Only *names* are read; values are never
   fetched or printed.

Usage::

    python3 scripts/check_secret_contract.py          # doc <-> consumer
    python3 scripts/check_secret_contract.py --gh     # + dormant-credential scan
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set

REPO_ROOT = Path(__file__).resolve().parent.parent
DOC = REPO_ROOT / ".github" / "docs" / "SECRETS_MANAGEMENT.md"
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
CODE_DIRS = ("scripts", "api")

# Two documented forms, both deliberate:
#   `- `NAME`: description`  — a full entry with setup steps
#   `| `NAME` | … |`         — a table row, used for the referenced-but-unprovisioned
#                              list where inventing setup steps would be a lie
# A bare prose mention does NOT count: the guide names secrets in explanations
# ("SLACK_BOT_TOKEN/SLACK_CHANNEL_ID went undocumented while…"), and counting
# those would let a secret be "documented" by being complained about.
_DOC_ENTRY_RE = re.compile(
    r"^- `([A-Z][A-Z0-9_]{2,})`\s*:|^\|\s*`([A-Z][A-Z0-9_]{2,})`\s*\|", re.M
)
# `secrets.NAME` / `secrets['NAME']` in workflow YAML.
_WORKFLOW_SECRET_RE = re.compile(r"secrets\.([A-Z][A-Z0-9_]{2,})")

# Documented on purpose while nothing consumes them. Each entry states what has
# to happen for it to leave this list — an exemption without an exit condition
# is just a permanent hole.
DOCUMENTED_WITHOUT_CONSUMER: Dict[str, str] = {
    "ELEVENLABS_API_KEY": (
        "RESOLVED 2026-09-17: deleted from this repo's Actions secrets. It had "
        "been provisioned since 2026-01-11 with no consumer, because cfe0d82d "
        "moved ai-video-gen.yml and generate_enhanced_audio.py to online-course. "
        "Documented only so the guide can say 'do not set this here' — the "
        "scripts that use it live in online-course and read it from the local "
        "environment, and Actions secrets are repo-scoped, so a secret here "
        "could never have served them. Remove when a consumer lands here."
    ),
    "ELEVENLABS_VOICE_ID": (
        "RESOLVED 2026-09-17 — deleted alongside ELEVENLABS_API_KEY, same reason."
    ),
    "GEMINI_SERVICE_ACCOUNT_KEY": (
        "Not provisioned and not read. Documented so the guide can say 'do not "
        "set this' — following the old '⭐ 권장' text created a credential with "
        "no consumer. Remove when a consumer lands in the same PR."
    ),
    "GOOGLE_CLOUD_PROJECT": (
        "No runtime reader. setup_gemini_oauth.sh / gemini_oauth_setup.py only "
        "PRINT it as an `export ...` hint for local setup."
    ),
    # The AI-Gateway Slack trio. Listed explicitly even though `code_consumers`
    # currently finds them, because what it finds is a COMMENT in
    # test_ci_ops_orchestrator_partition_guard.py explaining the removal — the
    # substring scan cannot tell prose from a read. That looseness is deliberate
    # (a missed dynamic read is the expensive direction to be wrong in), so the
    # accurate record has to live here rather than rely on the grep.
    "AI_GATEWAY_TOKEN": (
        "RESOLVED 2026-09-18: the three ops-orchestrator steps that used it were "
        "removed. Never provisioned, so every one of those steps was skipped on "
        "every run since 2026-08-07. Re-adding needs the gateway service AND the "
        "secret in the same change."
    ),
    "AI_GATEWAY_URL": (
        "RESOLVED 2026-09-18 — removed with AI_GATEWAY_TOKEN, same three steps."
    ),
    "SLACK_CHANNEL_ID_OPS": (
        "RESOLVED 2026-09-18 — removed with the AI-Gateway steps. A dedicated ops "
        "Slack channel was never provisioned; the repo's working Slack path is "
        "SLACK_BOT_TOKEN + SLACK_CHANNEL_ID via scripts/notify_webhook.py."
    ),
    "PAGESPEED_API_KEY": (
        "RESOLVED 2026-09-18: DO NOT PROVISION. check_uiux() and the CWV block in "
        "monitor_vercel_builds.sh were removed because the measurement already "
        "exists twice — lighthouse-ci.yml (head-vs-base LCP over 5 runs, PRs) and "
        "lighthouse.yml (CLS budget 0.05, push + PR) — and check_uiux gated on "
        "exactly what lighthouse.yml discarded after 60 runs: performance score "
        "(0.55-0.86 on unchanged content, 'produced random red') and LCP <= 2500ms "
        "(bimodal 4218-4373 / 6921-9695, both modes above the threshold). Setting "
        "this key would have aimed a noisy P1 source at the 6-hourly cron, and P1 "
        "is what opens an ops issue. Documented so the guide can say 'do not set "
        "this here'. To remove this entry: land a PSI-side measurement showing the "
        "numbers are stable on Google's infrastructure, with thresholds derived "
        "from that distribution, and wire a real consumer in the same change."
    ),
    # The retired SNS eight. scripts/share_sns.py and linkedin_oauth.py read
    # them from the local environment for manual runs, so they are documented —
    # but as "do not put these in Actions secrets".
    # test_ci_secret_absence_guard.py keeps workflows from referencing them.
    "TWITTER_API_KEY": "Retired sns-share.yml; manual use only via local .env.",
    "TWITTER_API_SECRET": "Retired sns-share.yml; manual use only via local .env.",
    "TWITTER_ACCESS_TOKEN": "Retired sns-share.yml; manual use only via local .env.",
    "TWITTER_ACCESS_SECRET": "Retired sns-share.yml; manual use only via local .env.",
    "FACEBOOK_PAGE_ID": "Retired sns-share.yml; manual use only via local .env.",
    "FACEBOOK_ACCESS_TOKEN": "Retired sns-share.yml; manual use only via local .env.",
    "LINKEDIN_ACCESS_TOKEN": "Retired sns-share.yml; manual use only via local .env.",
    "LINKEDIN_PERSON_ID": "Retired sns-share.yml; manual use only via local .env.",
}

# Read by workflows but deliberately not in the guide.
UNDOCUMENTED_ON_PURPOSE: Dict[str, str] = {
    "GITHUB_TOKEN": "injected by Actions; nothing to provision",
}

# A GitHub secret NAME. Every token this tool prints must match it.
#
# The tool only ever handles names — `gh secret list` does not return values and
# the regexes above match identifiers — but on a PUBLIC repo "only names" must be
# a checked property, not a comment. CodeQL agreed: alert 290
# (py/clear-text-logging-sensitive-data, high) fired on the print in main()
# because names parsed out of workflow `secrets.X` are a sensitive-data source to
# its taint analysis. Routing every emitted token through `_safe_name` makes the
# guarantee structural: anything that is not a bare SCREAMING_SNAKE identifier —
# which is what a leaked value would look like — cannot reach stdout/stderr.
_SECRET_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{2,}$")
_REDACTED = "<redacted: not a secret name>"

# This tool and its test name the secrets they reason about — DOCUMENTED_WITHOUT_
# CONSUMER spells out ELEVENLABS_API_KEY, and the test asserts on it. Counting
# those as consumers made the `--gh` scan report zero dormant credentials on the
# very run that was supposed to find two: the checker had become its own
# consumer. A scanner that reads the file describing the rule always finds the
# rule's own example.
_SELF_REFERENCES = frozenset(
    {
        "scripts/check_secret_contract.py",
        "scripts/tests/test_secret_contract.py",
    }
)


def _safe_name(raw: str) -> str:
    """Return `raw` only if it is a bare secret NAME; otherwise redact it."""
    return raw if _SECRET_NAME_RE.fullmatch(raw or "") else _REDACTED


def documented_secrets() -> Set[str]:
    # findall returns a tuple per match (one group per alternative); exactly one
    # is non-empty. Flattening with a plain set() over tuples would silently
    # produce tuples instead of names — the kind of extractor bug that makes a
    # gate read 0 and look green.
    return {
        name
        for pair in _DOC_ENTRY_RE.findall(DOC.read_text(encoding="utf-8"))
        for name in pair
        if name
    }


def workflow_secrets() -> Dict[str, List[str]]:
    """secret name -> workflow files that read it via `secrets.NAME`."""
    out: Dict[str, List[str]] = {}
    for path in sorted(WORKFLOWS.glob("*.yml")):
        for name in set(_WORKFLOW_SECRET_RE.findall(path.read_text(encoding="utf-8"))):
            out.setdefault(name, []).append(path.name)
    return out


_COMMENT_PREFIXES = ("#", "//", "*", "/*")


def code_consumers(name: str) -> List[str]:
    """Tracked files under CODE_DIRS that mention the name OUTSIDE a comment.

    Deliberately a substring scan rather than `os.environ` parsing: a dynamic
    read (``os.environ[k]`` over a parsed .env, or ``importlib``-style
    indirection) would be invisible to a stricter pattern, and calling a live
    credential unused is the expensive direction to be wrong in. `_archive/` is
    excluded — code kept for history is not a consumer.

    Whole-line comments are dropped, because a substring scan otherwise cannot
    tell a read from prose ABOUT a read, and this tool's entire question is
    "does anything actually read this". Measured cost of not doing it: on
    2026-09-18 the removal notes explaining why `PAGESPEED_API_KEY` was deleted
    counted as three consumers, so the contract check reported 0 violations for
    a secret that by then had none. The same day, three AI-Gateway names
    survived only in a guard's comments and passed for the same reason.

    Limit, stated rather than papered over: this drops whole-line comments, not
    docstrings or block-comment bodies whose lines happen not to start with a
    marker. A name mentioned mid-prose inside a ``\"\"\"...\"\"\"`` still reads as a
    consumer — the safe direction, since the failure mode is "keeps a live
    secret documented", not "declares a used secret dead".
    """
    proc = subprocess.run(
        ["git", "grep", "-n", "--", name, *CODE_DIRS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    hits: dict[str, None] = {}
    for line in proc.stdout.splitlines():
        # `path:lineno:text` — the text itself may contain colons.
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        path, _, text = parts
        if "_archive" in path or path in _SELF_REFERENCES:
            continue
        if text.lstrip().startswith(_COMMENT_PREFIXES):
            continue
        hits[path] = None
    return list(hits)


def check_doc_consumer_sync() -> List[str]:
    problems: List[str] = []
    documented = documented_secrets()
    in_workflows = workflow_secrets()

    for name in sorted(documented):
        if name in in_workflows or code_consumers(name):
            continue
        if name in DOCUMENTED_WITHOUT_CONSUMER:
            continue
        problems.append(
            f"{_safe_name(name)} is documented in {DOC.name} but nothing reads "
            "it. Either wire a consumer, or add it to "
            "DOCUMENTED_WITHOUT_CONSUMER with the reason and what would remove it."
        )

    for name, files in sorted(in_workflows.items()):
        if name in documented or name in UNDOCUMENTED_ON_PURPOSE:
            continue
        problems.append(
            f"{_safe_name(name)} is read by {files} but is missing from "
            f"{DOC.name}. Someone setting this repo up from the guide would "
            "leave those jobs without it — which is how SLACK_BOT_TOKEN/"
            "SLACK_CHANNEL_ID went undocumented while five fail-closed "
            "workflows depended on them."
        )
    return problems


def check_provisioned_without_consumer() -> List[str]:
    """`gh secret list` names vs consumers. Names only — values are never read."""
    proc = subprocess.run(
        ["gh", "secret", "list"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if proc.returncode != 0:
        # Deliberately not echoing proc.stderr: `gh` error text is attacker- and
        # environment-controlled, and this tool's whole contract is that only
        # secret NAMES leave it. The exit code is enough to tell you to re-auth.
        return [
            f"`gh secret list` failed (exit {proc.returncode}); run `gh auth status`"
        ]
    # Keep only the name column, and only tokens that ARE names. `gh secret list`
    # does not emit values, so a non-matching token means the output format
    # changed — drop it rather than print something unexamined.
    provisioned = [
        ln.split("\t")[0]
        for ln in proc.stdout.splitlines()
        if ln.strip() and _SECRET_NAME_RE.fullmatch(ln.split("\t")[0])
    ]
    in_workflows = workflow_secrets()
    dormant = [
        n for n in provisioned if n not in in_workflows and not code_consumers(n)
    ]
    return [
        f"{_safe_name(n)} is provisioned but nothing consumes it — a live "
        "credential with no reader. "
        f"({DOCUMENTED_WITHOUT_CONSUMER.get(n, 'no recorded reason')})"
        for n in dormant
    ]


def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--gh",
        action="store_true",
        help="also run `gh secret list` and report provisioned-but-unused names",
    )
    args = ap.parse_args(argv)

    problems = check_doc_consumer_sync()
    for p in problems:
        print(f"[secret-contract] {p}", file=sys.stderr)

    if args.gh:
        dormant = check_provisioned_without_consumer()
        for d in dormant:
            print(f"[secret-contract] DORMANT {d}", file=sys.stderr)
        if dormant:
            print(
                f"[secret-contract] {len(dormant)} dormant credential(s). Deleting "
                "or rotating a secret is an owner decision — this only reports.",
                file=sys.stderr,
            )

    if problems:
        print(f"[secret-contract] {len(problems)} contract violation(s).")
        return 1
    print(
        f"[secret-contract] OK — {len(documented_secrets())} documented, "
        f"{len(workflow_secrets())} read by workflows, 0 violations."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
