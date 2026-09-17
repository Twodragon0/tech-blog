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
        "PROVISIONED but unused since cfe0d82d moved ai-video-gen.yml and "
        "generate_enhanced_audio.py to the online-course repo. Pending an owner "
        "decision: revoke + `gh secret delete`, or move it to that repo. Remove "
        "from this list either way."
    ),
    "ELEVENLABS_VOICE_ID": "Same as ELEVENLABS_API_KEY — same commit, same decision.",
    "GEMINI_SERVICE_ACCOUNT_KEY": (
        "Not provisioned and not read. Documented so the guide can say 'do not "
        "set this' — following the old '⭐ 권장' text created a credential with "
        "no consumer. Remove when a consumer lands in the same PR."
    ),
    "GOOGLE_CLOUD_PROJECT": (
        "No runtime reader. setup_gemini_oauth.sh / gemini_oauth_setup.py only "
        "PRINT it as an `export ...` hint for local setup."
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


def code_consumers(name: str) -> List[str]:
    """Tracked files under CODE_DIRS that mention the name.

    Deliberately a plain substring scan rather than `os.environ` parsing: a
    dynamic read (``os.environ[k]`` over a parsed .env, or
    ``importlib``-style indirection) would be invisible to a stricter pattern,
    and calling a live credential unused is the expensive direction to be wrong
    in. `_archive/` is excluded — code kept for history is not a consumer.
    """
    proc = subprocess.run(
        ["git", "grep", "-l", "--", name, *CODE_DIRS],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    return [p for p in proc.stdout.split() if p and "_archive" not in p]


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
            f"{name} is documented in {DOC.name} but nothing reads it. Either "
            "wire a consumer, or add it to DOCUMENTED_WITHOUT_CONSUMER with the "
            "reason and what would remove it."
        )

    for name, files in sorted(in_workflows.items()):
        if name in documented or name in UNDOCUMENTED_ON_PURPOSE:
            continue
        problems.append(
            f"{name} is read by {files} but is missing from {DOC.name}. Someone "
            "setting this repo up from the guide would leave those jobs without "
            "it — which is how SLACK_BOT_TOKEN/SLACK_CHANNEL_ID went undocumented "
            "while five fail-closed workflows depended on them."
        )
    return problems


def check_provisioned_without_consumer() -> List[str]:
    """`gh secret list` names vs consumers. Names only — values are never read."""
    proc = subprocess.run(
        ["gh", "secret", "list"], cwd=REPO_ROOT, capture_output=True, text=True
    )
    if proc.returncode != 0:
        return [f"`gh secret list` failed: {proc.stderr.strip()[:200]}"]
    provisioned = [ln.split("\t")[0] for ln in proc.stdout.splitlines() if ln.strip()]
    in_workflows = workflow_secrets()
    dormant = [
        n for n in provisioned if n not in in_workflows and not code_consumers(n)
    ]
    return [
        f"{n} is provisioned but nothing consumes it — a live credential with no "
        f"reader. ({DOCUMENTED_WITHOUT_CONSUMER.get(n, 'no recorded reason')})"
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
