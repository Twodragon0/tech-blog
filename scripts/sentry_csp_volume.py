#!/usr/bin/env python3
"""Report how many Sentry events the CSP report channel actually consumes.

Why this exists
---------------
`vercel.json` ships two CSP policies and both carry `report-uri` + `report-to`
(the live `reporting-endpoints` header points at Sentry). Those reports travel
browser -> Sentry ingest directly. They never pass through the Sentry SDK, so
none of the SDK's filtering applies to them — and `assets/js/sentry-init.js`
explicitly drops exactly this class of event:

    var ignorePatterns = [
      /content security policy/i, /csp/i,
      /chrome-extension/i, /moz-extension/i,
      ...

So the noise the SDK is configured to discard is being ingested through a
different door, unsampled. The SDK's monthly guard does not see it either:
`getMonthlyCount()` counts in `localStorage`, i.e. per browser, not globally.

Whether that matters is an empirical question — how many events, and how many
of them are ours rather than a visitor's browser extension. This script answers
it. It does NOT decide anything: removing the Report-Only header or adding
Sentry inbound filters is a call for the repo owner, made on these numbers.

Credentials come from the environment so the run can happen in CI, where the
secrets already live, rather than passing a token around in plaintext.

Exit codes
  0 - report produced, OR the token is not authorized to read issues (see below)
  1 - a required secret is missing. SENTRY_* ARE configured in this repo, so
      their absence is a regression (rotation, lost access), not an optional
      integration. Same rule as scripts/tests/test_ci_secret_absence_guard.py.
  2 - the Sentry API call failed for any other reason. "Could not measure" must
      never read as "nothing was wrong".

Why 401/403 is not fail-closed
------------------------------
The Sentry token in this repo can read the project endpoint but NOT issues.
Verified from the scheduled run on 2026-08-12T04:21Z — i.e. BEFORE this script
existed — where the pre-existing healthcheck step logged:

    ⚠️ Sentry issues API check returned HTTP 403
    - Issues API accessible: false

So the missing scope (`event:read`) is a standing condition, not a regression
this script discovered. Exiting non-zero on it would turn a daily cron
permanently red, which this repo has repeatedly established gets muted and is
therefore worse than the gap itself (see notes/ci-gate-audit-2026-08.md and
scripts/tests/test_ci_secret_absence_guard.py). Instead the run stays green and
says, unmissably, that it measured nothing — the same treatment the neighbouring
step already gives the same 403.

Direction: once the token gains `event:read`, delete the 401/403 branch so any
authorization failure is fail-closed again, and update
scripts/tests/test_sentry_csp_volume.py in the same PR.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_ROOT = "https://sentry.io/api/0"
TIMEOUT_S = 30

# assets/js/sentry-init.js:30 — the free-tier budget the SDK throttles against.
SDK_MONTHLY_LIMIT = 5000

REQUIRED = ("SENTRY_AUTH_TOKEN", "SENTRY_ORG", "SENTRY_PROJECT")


def _fetch(url: str, token: str) -> list | dict:
    req = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:  # noqa: S310 - fixed https host
        return json.loads(resp.read().decode("utf-8"))


def classify(issue: dict) -> str:
    """Bucket an issue by who would have to fix it.

    'extension'  - a visitor's browser extension tripped our policy. Not ours,
                   and not fixable by us: satisfying it (e.g. adding
                   'unsafe-eval' for MetaMask's WebAssembly) would weaken the
                   policy for every visitor.
    'translate'  - the known Google Translate about:blank inline bootstrap,
                   grandfathered in scripts/tests/csp_interaction_baseline.txt.
    'first-party'- anything else. These are the ones worth reading.
    """
    haystack = " ".join(
        str(issue.get(k, "")) for k in ("title", "culprit", "metadata")
    ).lower()
    if "chrome-extension" in haystack or "moz-extension" in haystack:
        return "extension"
    if "about" in haystack and "inline" in haystack:
        return "translate"
    return "first-party"


def main() -> int:
    missing = [k for k in REQUIRED if not os.getenv(k)]
    if missing:
        # Names only — never the values.
        print(f"::error::missing required secret(s): {', '.join(missing)}", file=sys.stderr)
        return 1

    token = os.environ["SENTRY_AUTH_TOKEN"]
    org = os.environ["SENTRY_ORG"]
    project = os.environ["SENTRY_PROJECT"]
    period = os.getenv("STATS_PERIOD", "30d")

    query = urllib.parse.urlencode(
        {
            "query": "event.type:csp",
            "statsPeriod": period,
            "limit": "100",
            "sort": "freq",
        }
    )
    url = f"{API_ROOT}/projects/{org}/{project}/issues/?{query}"

    try:
        issues = _fetch(url, token)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            # Standing scope gap, not a regression — see the module docstring.
            # Loud in the summary, green in the check.
            print(f"# CSP report volume ({period})\n")
            print(
                f"> **MEASURED NOTHING** — Sentry returned HTTP {exc.code} for the issues "
                f"query. The token can read the project but not its events, so this "
                f"report is empty for a permissions reason, **not** because the CSP "
                f"report channel is quiet.\n"
            )
            print(
                "> To make it measure: grant the Sentry auth token `event:read` "
                "(Sentry → Settings → Auth Tokens), then re-run this workflow.\n"
            )
            print(
                f"::warning::CSP volume not measured: Sentry issues API HTTP {exc.code} "
                f"(token lacks event:read). Pre-existing since at least 2026-08-12."
            )
            return 0
        print(f"::error::Sentry API HTTP {exc.code} for issues query", file=sys.stderr)
        return 2
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"::error::Sentry API call failed: {type(exc).__name__}", file=sys.stderr)
        return 2

    if not isinstance(issues, list):
        print("::error::unexpected Sentry response shape (expected a list)", file=sys.stderr)
        return 2

    buckets: dict[str, int] = {"first-party": 0, "translate": 0, "extension": 0}
    rows = []
    for issue in issues:
        try:
            count = int(issue.get("count", 0))
        except (TypeError, ValueError):
            count = 0
        bucket = classify(issue)
        buckets[bucket] += count
        rows.append((count, bucket, str(issue.get("title", ""))[:90]))

    total = sum(buckets.values())
    rows.sort(reverse=True)

    print(f"# CSP report volume ({period})\n")
    print(f"- CSP issue groups returned: **{len(issues)}** (API page cap 100)")
    print(f"- Total CSP events: **{total}**")
    if total:
        pct = total / SDK_MONTHLY_LIMIT * 100
        print(
            f"- Against the {SDK_MONTHLY_LIMIT}/mo budget `sentry-init.js` throttles "
            f"against: **{pct:.1f}%**"
        )
    print()
    print("| bucket | events | share |")
    print("|---|---:|---:|")
    for name in ("first-party", "translate", "extension"):
        share = f"{buckets[name] / total * 100:.1f}%" if total else "n/a"
        print(f"| {name} | {buckets[name]} | {share} |")
    print()

    if rows:
        print("## Top groups\n")
        print("| events | bucket | title |")
        print("|---:|---|---|")
        for count, bucket, title in rows[:15]:
            print(f"| {count} | {bucket} | `{title}` |")
        print()

    if len(issues) == 100:
        # No silent caps: say when the page limit was hit.
        print(
            "> The API returned a full page (100 groups), so **totals are a floor, "
            "not the complete count**.\n"
        )
    if total == 0:
        print(
            "> Zero CSP events in this window. Either the report channel is not "
            "reaching Sentry, or it genuinely costs nothing — check the Sentry "
            "project's inbound filters before concluding the latter.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
