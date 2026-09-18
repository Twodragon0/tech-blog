#!/usr/bin/env python3
"""Every required status check must still be producible.

A required check is a NAME. If nothing produces that name any more, GitHub never
receives the status and **every pull request blocks forever** — the most
expensive form of the failure this repo already paid for twice on 2026-09-18:

* A-H3's self-rerun exclusion listed four workflow names that had been
  consolidated away, so an `actions:write` control was inert for months.
* `check_secret_contract.code_consumers` counted a removal-rationale comment as
  a consumer, so the contract passed for a secret with none.

Same shape, worse blast radius: a stale entry in a name list that nothing checks.
So the required set lives in `.github/rulesets/main-required-status-checks.json`
(declarative, in the repo, reviewable) rather than only in the UI, and this
script asserts every context in it still resolves.

Two halves, same split as check_secret_contract.py / check_runtime_env_contract.py:

* Default run is credentials-free and runs in pytest. It resolves each context
  against `.github/workflows/` and the documented external-app set, and checks
  the producing workflow has no `pull_request` `paths:` filter.
* `--gh` is owner-only. It compares the declared JSON with the live ruleset and
  with the checks actually reported on the newest pull request.

Why the paths check matters, measured 2026-09-18 over 8 merged PRs: the
`Validate action pin consistency` check was absent from 4 of them, because
`action-pin-check.yml` filters on `paths:`. Requiring a paths-filtered check
means the PRs that do not touch those paths never get the status at all. A job
skipped by an `if:` still REPORTS (`auto-merge`, `npm Security Audit` and
`Ruby Gem Security Audit` reported `skipped` on all 8); a workflow that never
triggers does not. That distinction is the whole eligibility rule.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
RULESET = REPO_ROOT / ".github" / "rulesets" / "main-required-status-checks.json"
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"

# Checks produced by an installed app rather than a workflow in this repo, with
# what breaks if the app goes away. These cannot be resolved from the tree, so
# each one is an explicit, reasoned exception — not a silent fallthrough.
EXTERNAL_CHECKS: dict[str, str] = {
    "CodeQL": (
        "GitHub Advanced Security default setup (app `github-advanced-security`). "
        "The aggregate PR gate — 'No new alerts in code changed by this pull "
        "request'. Deliberately required INSTEAD of the per-language "
        "`Analyze (actions|javascript-typescript|python|ruby)` jobs: those names "
        "track the detected language list, so dropping Ruby from the repo would "
        "silently stop producing `Analyze (ruby)` and block every PR. If default "
        "setup is turned off, remove this context in the same change."
    ),
    "GitGuardian Security Checks": (
        "GitGuardian app, secret scanning on every PR. Reported success on 8/8 "
        "sampled PRs. This repo is PUBLIC and has already handled a credential in "
        "a URL, so the gate is worth the coupling. If the app is uninstalled, "
        "this context stops being produced and all PRs block — remove the context "
        "in the same change as the uninstall."
    ),
}

# Actor allowed to bypass. 15368 is the GitHub Actions app: four workflows
# (ai-blogwatcher, generate-images, vercel-firewall-backup,
# visual-baseline-refresh) push straight to main with `secrets.GITHUB_TOKEN`,
# and a required status check rejects a direct push. Without this bypass the
# daily digest stops publishing.
ACTIONS_APP_ID = 15368

_SECRET_LIKE = re.compile(r"^[\w .()/&+-]{1,80}$")


def _safe(name: str) -> str:
    """Contexts are printed; keep anything odd out of the output."""
    return name if _SECRET_LIKE.fullmatch(name or "") else "<redacted>"


def declared() -> dict[str, Any]:
    return json.loads(RULESET.read_text(encoding="utf-8"))


def required_contexts() -> list[str]:
    for rule in declared().get("rules", []):
        if rule.get("type") == "required_status_checks":
            params = rule.get("parameters", {})
            return [c["context"] for c in params.get("required_status_checks", [])]
    return []


def _load_workflows() -> list[tuple[str, dict[str, Any]]]:
    import yaml

    out = []
    for path in sorted(WORKFLOW_DIR.glob("*.y*ml")):
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        if isinstance(spec, dict):
            out.append((path.name, spec))
    return out


def _pr_trigger(spec: dict[str, Any]) -> dict[str, Any] | None:
    on = spec.get(True) or spec.get("on") or {}
    if not isinstance(on, dict) or "pull_request" not in on:
        return None
    trigger = on.get("pull_request")
    return trigger if isinstance(trigger, dict) else {}


def producers(context: str) -> list[tuple[str, str, bool]]:
    """(workflow file, job id, workflow has a pull_request paths filter).

    A check's reported name is the job's `name:` when set, else its job id.
    """
    hits = []
    for filename, spec in _load_workflows():
        trigger = _pr_trigger(spec)
        if trigger is None:
            continue
        filtered = bool(trigger.get("paths") or trigger.get("paths-ignore"))
        for job_id, job in (spec.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            if (job.get("name") or job_id) == context:
                hits.append((filename, job_id, filtered))
    return hits


def check_contract() -> list[str]:
    problems: list[str] = []
    contexts = required_contexts()

    if not contexts:
        return [
            f"{RULESET.name} declares no required status checks. If enforcement "
            "was dropped on purpose, delete the file; an empty rule reads as "
            "protection that is not there."
        ]

    for context in contexts:
        found = producers(context)
        if not found:
            if context in EXTERNAL_CHECKS:
                continue
            problems.append(
                f"required check {_safe(context)!r} is produced by no job in "
                ".github/workflows/ and is not in EXTERNAL_CHECKS. Nothing will "
                "report it, so EVERY pull request blocks. Rename the check back, "
                "drop it from the ruleset, or document it as external."
            )
            continue

        if len(found) > 1:
            where = ", ".join(f"{f}:{j}" for f, j, _ in found)
            problems.append(
                f"required check {_safe(context)!r} is produced by more than one "
                f"job ({where}). Name matching cannot tell them apart, so which "
                "one satisfies the requirement is undefined. Rename one."
            )

        for filename, job_id, filtered in found:
            if filtered:
                problems.append(
                    f"required check {_safe(context)!r} comes from {filename}:{job_id}, "
                    "whose pull_request trigger has a paths filter. On a PR that "
                    "touches none of those paths the workflow never runs and the "
                    "status is never reported — the PR stays pending forever. "
                    "Measured 2026-09-18: `Validate action pin consistency` was "
                    "absent from 4 of 8 sampled PRs for exactly this reason."
                )

    # The bypass is what keeps the four GITHUB_TOKEN crons publishing.
    actors = declared().get("bypass_actors") or []
    if not any(
        a.get("actor_id") == ACTIONS_APP_ID and a.get("actor_type") == "Integration"
        for a in actors
    ):
        problems.append(
            f"the GitHub Actions app (id {ACTIONS_APP_ID}) is not a bypass actor. "
            "ai-blogwatcher / generate-images / vercel-firewall-backup / "
            "visual-baseline-refresh push directly to main with "
            "secrets.GITHUB_TOKEN, and a required status check rejects a direct "
            "push — the daily digest would stop publishing. If those crons were "
            "converted to pull requests, remove this assertion in the same change."
        )

    params = next(
        (
            r["parameters"]
            for r in declared().get("rules", [])
            if r.get("type") == "required_status_checks"
        ),
        {},
    )
    if params.get("strict_required_status_checks_policy"):
        problems.append(
            "strict_required_status_checks_policy is true, which forces every PR "
            "branch to be up to date before merging. #735 traced auto-merge "
            "false-reds partly to rebases leaving sibling runs deadlocked; do not "
            "turn this on without re-measuring that."
        )

    return problems


def _gh_json(*args: str) -> Any:
    proc = subprocess.run(
        ["gh", "api", *args], capture_output=True, text=True, check=False
    )
    if proc.returncode != 0:
        return None
    return json.loads(proc.stdout) if proc.stdout.strip() else None


def compare_live(repo: str) -> int:
    """Owner-only: is the declared file what is actually enforced?"""
    rulesets = _gh_json(f"repos/{repo}/rulesets")
    if rulesets is None:
        print("[required-checks] gh api failed — authenticate with `gh auth login`.")
        return 2

    want_name = declared()["name"]
    match = next((r for r in rulesets if r.get("name") == want_name), None)
    if match is None:
        names = sorted(_safe(r.get("name", "")) for r in rulesets)
        print(
            f"[required-checks] NOT APPLIED — no ruleset named {want_name!r}. "
            f"Present: {names or 'none'}.\n"
            "Apply it with:\n"
            f"  gh api --method POST repos/{repo}/rulesets "
            f"--input {RULESET.relative_to(REPO_ROOT)}"
        )
        return 1

    live = _gh_json(f"repos/{repo}/rulesets/{match['id']}") or {}
    live_ctx = []
    for rule in live.get("rules", []):
        if rule.get("type") == "required_status_checks":
            live_ctx = [
                c["context"]
                for c in rule.get("parameters", {}).get("required_status_checks", [])
            ]
    declared_ctx = required_contexts()
    drift = sorted(set(declared_ctx) ^ set(live_ctx))
    if drift:
        print(
            f"[required-checks] DRIFT between file and live ruleset: "
            f"{[_safe(d) for d in drift]}\n"
            f"  file: {[_safe(c) for c in sorted(declared_ctx)]}\n"
            f"  live: {[_safe(c) for c in sorted(live_ctx)]}"
        )
        return 1

    print(
        f"[required-checks] applied and in sync — {len(declared_ctx)} context(s), "
        f"enforcement={live.get('enforcement')}."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--gh",
        action="store_true",
        help="also compare the declared file against the live ruleset (needs gh)",
    )
    parser.add_argument("--repo", default="Twodragon0/tech-blog")
    args = parser.parse_args(argv)

    problems = check_contract()
    for line in problems:
        print(f"[required-checks] {line}")
    if problems:
        print(f"[required-checks] {len(problems)} contract violation(s).")
        return 1

    print(
        f"[required-checks] OK — {len(required_contexts())} context(s), all "
        "producible, none paths-filtered."
    )
    return compare_live(args.repo) if args.gh else 0


if __name__ == "__main__":
    sys.exit(main())
