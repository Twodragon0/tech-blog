#!/usr/bin/env python3
"""Keep every runtime env var that `api/` reads declared, so absence is loud.

Why this exists
---------------
`notes/ci-skip-campaign-2026-08.md` closed with the observation that every
credential guard in this repo is keyed to **CI secrets** — it walks
`.github/workflows/` and asserts each referenced secret either fails closed or
is listed as never-configured. Runtime credentials live somewhere that axis
cannot see: the Vercel project's environment variables. So half of the same
defect class was a structural blind spot, and it cost us one:

`GA4_API_SECRET` was never provisioned. `api/vitals.js` drops every report when
it is absent (`api/vitals.js:205-210`), and because the endpoint is
fire-and-forget it answers 204 either way. Two PRs of first-party beacon work
(#558, #586) shipped into a pipeline that collected nothing, and the only signal
was a `console.warn` in a Vercel function log that nobody reads. Verified absent
via `vercel env ls production` on 2026-08-24.

What it checks
--------------
Two things, and only the first needs credentials-free CI:

1. **Declaration sync (always).** Every ``process.env.NAME`` in ``api/`` must
   appear in the manifest below, and every manifest entry must still be read by
   ``api/``. A new runtime dependency therefore cannot land without someone
   writing down what breaks when it is missing and where it gets provisioned.
   This is the part that runs in CI.
2. **Provisioning (``--vercel``, opt-in).** Runs ``vercel env ls`` and reports
   REQUIRED names that are absent from the Vercel project. Needs an
   authenticated Vercel CLI, so it is a one-command owner check, not a CI gate.
   Only variable *names* are read; values are never fetched or printed.

Manifest categories
-------------------
``PLATFORM``  Vercel injects it. Nothing to provision.
``REQUIRED``  Absence silently disables a shipped feature. Must exist in Vercel.
``OPTIONAL``  Has a working default, or is an explicit opt-in flag that is
              deliberately off. Absence is a documented state, not a defect.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Set

REPO_ROOT = Path(__file__).resolve().parent.parent
API_DIR = REPO_ROOT / "api"

_ENV_RE = re.compile(r"process\.env\.([A-Z][A-Z0-9_]*)")

PLATFORM: Dict[str, str] = {
    "NODE_ENV": "injected by the runtime; 'production' on Vercel",
    "VERCEL_ENV": "injected by Vercel; production | preview | development",
}

REQUIRED: Dict[str, str] = {
    "GA4_API_SECRET": (
        "api/vitals.js — GA4 Measurement Protocol secret. Absent: every "
        "web_vitals beacon is dropped and the endpoint still answers 204, so "
        "collection reads as working. Provision: Vercel project env "
        "(Production). Create the value in GA4 Admin > Data Streams > the web "
        "stream > Measurement Protocol API secrets."
    ),
    "DEEPSEEK_API_KEY": (
        "api/chat.js — chatbot upstream key. Absent: the chat widget errors. "
        "Provision: Vercel project env (Production). Present as of 2026-08-24."
    ),
}

OPTIONAL: Dict[str, str] = {
    "SENTRY_DSN": (
        "api/chat.js — error reporting. Absent: no server-side reporting, "
        "feature still works. Present as of 2026-08-24."
    ),
    "GA4_MEASUREMENT_ID": "api/vitals.js — defaults to the hardcoded G-B29150XJ73.",
    "SITE_ORIGIN": "api/vitals.js — defaults to https://tech.2twodragon.com.",
    "DEEPSEEK_MODEL": "api/chat.js — model override; code carries a default.",
    "DEBUG": "api/chat.js — verbose logging switch.",
    "SEARCH_CACHE_TTL": "api/search.js — cache TTL override; code carries a default.",
    "SEARCH_RATE_LIMIT_RPM": "api/search.js — rate override; code carries a default.",
    "RATELIMIT_ANONYMOUS_RPM": "api/lib/ratelimit.js — override; code carries a default.",
    "RATELIMIT_AUTHENTICATED_RPM": "api/lib/ratelimit.js — override; code carries a default.",
    "USE_UPSTASH_RATELIMIT": (
        "api/lib/ratelimit.js — explicit opt-in ('true') for the Redis-backed "
        "limiter. Deliberately unset: the in-memory limiter is per-instance on "
        "serverless, which the code warns about at startup. This is a chosen "
        "trade-off, not a missing credential."
    ),
    "UPSTASH_REDIS_REST_URL": (
        "api/search.js, api/lib/ratelimit.js — only read when "
        "USE_UPSTASH_RATELIMIT is 'true'. Unset, consistent with that flag "
        "being off. Note the Vercel project has REDIS_URL from a storage "
        "integration, which no code in api/ reads."
    ),
    "UPSTASH_REDIS_REST_TOKEN": "api/lib/ratelimit.js — pairs with the URL above.",
}


def declared() -> Dict[str, str]:
    return {**PLATFORM, **REQUIRED, **OPTIONAL}


def referenced() -> Dict[str, Set[str]]:
    """env name -> set of api/ files reading it, excluding tests."""
    found: Dict[str, Set[str]] = {}
    for path in sorted(API_DIR.rglob("*.js")):
        if "__tests__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for name in _ENV_RE.findall(text):
            found.setdefault(name, set()).add(str(path.relative_to(REPO_ROOT)))
    return found


def vercel_env_names(environment: str) -> Set[str]:
    """Variable NAMES configured in the Vercel project. Values never fetched."""
    res = subprocess.run(
        ["vercel", "env", "ls", environment],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(
            "`vercel env ls` failed — is the CLI installed and logged in?\n"
            + res.stderr.strip()
        )
    names = set()
    for line in res.stdout.splitlines():
        parts = line.split()
        # Rows look like: NAME  Encrypted  Production, Preview  210d ago
        if len(parts) >= 2 and re.fullmatch(r"[A-Z][A-Z0-9_]*", parts[0]):
            names.add(parts[0])
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vercel",
        action="store_true",
        help="also check REQUIRED names against the Vercel project (needs CLI login)",
    )
    parser.add_argument("--environment", default="production")
    parser.add_argument("--json", action="store_true", help="machine-readable output")
    args = parser.parse_args()

    refs = referenced()
    dec = declared()

    undeclared = sorted(set(refs) - set(dec))
    orphaned = sorted(set(dec) - set(refs))

    report = {
        "referenced": {k: sorted(v) for k, v in sorted(refs.items())},
        "undeclared": undeclared,
        "orphaned": orphaned,
        "missing_in_vercel": [],
    }
    failures = []

    if undeclared:
        failures.append(
            "undeclared runtime env var(s) read by api/ — add each to REQUIRED or "
            "OPTIONAL in this script, saying what breaks when it is absent:\n"
            + "\n".join(f"    {n}  (read by {', '.join(sorted(refs[n]))})" for n in undeclared)
        )
    if orphaned:
        failures.append(
            "declared but no longer read by api/ — delete the entry:\n"
            + "\n".join(f"    {n}" for n in orphaned)
        )

    if args.vercel:
        try:
            configured = vercel_env_names(args.environment)
        except RuntimeError as exc:
            print(f"[runtime-env] {exc}", file=sys.stderr)
            return 2
        missing = sorted(n for n in REQUIRED if n not in configured)
        report["missing_in_vercel"] = missing
        if missing:
            failures.append(
                f"REQUIRED runtime env var(s) absent from Vercel "
                f"({args.environment}) — the feature is silently off:\n"
                + "\n".join(f"    {n}\n      {REQUIRED[n]}" for n in missing)
            )

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif failures:
        print("[runtime-env] FAIL\n", file=sys.stderr)
        for f in failures:
            print(f"  {f}\n", file=sys.stderr)
    else:
        scope = f", all {len(REQUIRED)} REQUIRED present in Vercel" if args.vercel else ""
        print(
            f"[runtime-env] OK — {len(refs)} env var(s) read by api/, all declared"
            f"{scope}."
        )

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
