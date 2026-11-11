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
  0 - report produced, or shared mode could not access issues (reported unmeasured)
  1 - missing or invalid configuration
  2 - API access or response error. Dedicated mode also fails on HTTP 401/403.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.lib import sentry_monitor  # noqa: E402


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
    try:
        config = sentry_monitor.load_config()
    except sentry_monitor.SentryMonitorError as error:
        print(f"::error::{error}; CSP unmeasured", file=sys.stderr)
        return 1

    period = os.getenv("STATS_PERIOD", "30d")
    shared = sentry_monitor.monitor_mode() == "shared"
    try:
        page = sentry_monitor.read_issues(
            config,
            query="event.type:csp",
            period=period,
            max_pages=1 if shared else sentry_monitor.MAX_PAGES,
        )
    except sentry_monitor.SentryMonitorError as error:
        if shared and error.http_status in {401, 403}:
            print(
                f"::warning::MEASURED NOTHING — {error}; verify event:read and project access."
            )
            return 0
        print(f"::error::{error}; CSP unmeasured", file=sys.stderr)
        return 2

    buckets: dict[str, int] = {"first-party": 0, "translate": 0, "extension": 0}
    for issue in page.issues:
        raw_count = issue.get("count")
        try:
            if not isinstance(raw_count, (str, int)) or isinstance(raw_count, bool):
                raise ValueError
            count = int(raw_count)
            if count < 0:
                raise ValueError
        except ValueError:
            print("::error::Invalid CSP issue count; CSP unmeasured", file=sys.stderr)
            return 2
        buckets[classify(issue)] += count

    total = sum(buckets.values())
    print("# CSP report volume")
    print(f"- CSP issue groups observed: **{len(page.issues)}**")
    print(f"- API-reported events in observed groups: **{total}**")
    print()
    print("| bucket | events | share |")
    print("|---|---:|---:|")
    for name in ("first-party", "translate", "extension"):
        share = f"{buckets[name] / total * 100:.1f}%" if total else "n/a"
        print(f"| {name} | {buckets[name]} | {share} |")
    print()

    if not page.complete:
        print("> Partial observation. The count is a floor for the returned groups.")
        return 0 if shared else 2
    if total == 0:
        print(
            "> Zero CSP events in this window. Either the report channel is not "
            "reaching Sentry, or it genuinely costs nothing — check the Sentry "
            "project's inbound filters before concluding the latter.\n"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
