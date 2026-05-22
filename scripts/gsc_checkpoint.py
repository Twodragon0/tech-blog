#!/usr/bin/env python3
"""Generate a dated GSC indexing-recovery checkpoint markdown.

Wraps ``scripts/gsc_inspect.py`` so a single command produces both the
``.omc/state/gsc-queue.json`` snapshot and a human-readable markdown
checkpoint comparing the current totals against a baseline measurement.

Intended use: schedule once on the target follow-up date (e.g., 2026-05-29
to evaluate the 2026-05-19 / 2026-05-22 SEO patch stack). The output path
is deterministic so re-runs are idempotent — same day → same file.

Usage::

    python3 scripts/gsc_checkpoint.py \\
        --checkpoint-date 2026-05-29 \\
        --baseline-date 2026-05-22 \\
        --baseline-crawled 109 \\
        --baseline-discovered 162

Env (forwarded to gsc_inspect.py):
    GSC_SERVICE_ACCOUNT_JSON  Required for the live inspection. If unset,
                              ``--skip-inspect`` lets the script render the
                              markdown from an existing state file.
    GSC_SITE_URL              Optional; default matches gsc_inspect.py.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date as _date_cls, datetime, timezone
from pathlib import Path
from typing import Dict, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_FILE = REPO_ROOT / ".omc" / "state" / "gsc-queue.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / ".omc" / "research"


def _iso(value: Optional[str]) -> str:
    return value or "n/a"


def _delta(current: Optional[int], baseline: Optional[int]) -> str:
    if current is None or baseline is None:
        return "n/a"
    diff = current - baseline
    arrow = "→"
    if diff < 0:
        arrow = "▼"
    elif diff > 0:
        arrow = "▲"
    return f"{baseline} → {current} ({arrow}{diff:+d})"


def _load_state(state_file: Path) -> Dict:
    if not state_file.exists():
        raise FileNotFoundError(
            f"State file missing: {state_file}. Run gsc_inspect.py first or "
            f"omit --skip-inspect."
        )
    with open(state_file, encoding="utf-8") as fh:
        return json.load(fh)


def _run_inspect(state_file: Path, limit: int, daily_budget: int) -> None:
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "gsc_inspect.py"),
        "--state-file",
        str(state_file),
        "--daily-budget",
        str(daily_budget),
    ]
    if limit:
        cmd.extend(["--limit", str(limit)])
    print(f"→ Running: {' '.join(cmd)}", file=sys.stderr)
    subprocess.run(cmd, check=True, cwd=REPO_ROOT)


def _render(
    *,
    checkpoint_date: str,
    baseline_date: str,
    baseline_crawled: Optional[int],
    baseline_discovered: Optional[int],
    state: Dict,
) -> str:
    totals = state.get("totals", {})
    current_crawled = totals.get("crawled_not_indexed")
    current_discovered = totals.get("discovered_not_indexed")
    current_indexed = totals.get("indexed")
    current_inspected = totals.get("inspected")
    generated_at = _iso(state.get("generated_at"))
    site_url = _iso(state.get("site_url"))

    return f"""---
name: GSC indexing recovery checkpoint — {checkpoint_date}
description: 7-day GSC recheck after the {baseline_date} SEO patch stack. Comparison against baseline {baseline_date}.
type: project
---
GSC indexing recheck for **{checkpoint_date}** (7-day window after {baseline_date}).

**Site:** `{site_url}`
**Inspection generated:** `{generated_at}`
**URLs inspected this run:** {current_inspected if current_inspected is not None else "n/a"}

## Indexing totals vs baseline ({baseline_date})

| Bucket | Baseline | Current | Δ |
|---|---|---|---|
| Crawled, currently not indexed | {baseline_crawled if baseline_crawled is not None else "n/a"} | {current_crawled if current_crawled is not None else "n/a"} | {_delta(current_crawled, baseline_crawled)} |
| Discovered, currently not indexed | {baseline_discovered if baseline_discovered is not None else "n/a"} | {current_discovered if current_discovered is not None else "n/a"} | {_delta(current_discovered, baseline_discovered)} |
| Indexed | n/a | {current_indexed if current_indexed is not None else "n/a"} | n/a |

## Interpretation
- Down-arrow (▼) on Crawled-not-indexed = excerpt diversification + JSON-LD
  image + related-posts injection are landing in the index.
- Down-arrow on Discovered-not-indexed = sitemap recrawl + IndexNow are
  draining the backlog.
- If either delta is flat or up: see "If stuck" in
  `[[checkpoint_gsc_2026_05_26]]` (deeper-level interventions list).

## Source state
- `state_file`: `.omc/state/gsc-queue.json`
- Regenerate: `python3 scripts/gsc_inspect.py`
- Regenerate checkpoint markdown: `python3 scripts/gsc_checkpoint.py --checkpoint-date {checkpoint_date} --baseline-date {baseline_date} --baseline-crawled {baseline_crawled} --baseline-discovered {baseline_discovered}`
"""


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--checkpoint-date",
        default=_date_cls.today().isoformat(),
        help="Checkpoint date in YYYY-MM-DD (default: today UTC)",
    )
    parser.add_argument(
        "--baseline-date",
        required=True,
        help="Baseline measurement date in YYYY-MM-DD",
    )
    parser.add_argument(
        "--baseline-crawled",
        type=int,
        help="Baseline `Crawled, currently not indexed` count",
    )
    parser.add_argument(
        "--baseline-discovered",
        type=int,
        help="Baseline `Discovered, currently not indexed` count",
    )
    parser.add_argument(
        "--state-file",
        default=DEFAULT_STATE_FILE,
        type=Path,
        help="Path to gsc_inspect state JSON (default: .omc/state/gsc-queue.json)",
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        type=Path,
        help="Directory for checkpoint markdown (default: .omc/research/)",
    )
    parser.add_argument(
        "--skip-inspect",
        action="store_true",
        help="Skip live GSC inspection; render markdown from existing state file",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Limit URLs to inspect (forwarded to gsc_inspect.py)",
    )
    parser.add_argument(
        "--daily-budget", type=int, default=500,
        help="Daily QPD cap (forwarded to gsc_inspect.py)",
    )

    args = parser.parse_args(argv)

    if not args.skip_inspect:
        if not os.environ.get("GSC_SERVICE_ACCOUNT_JSON"):
            print(
                "ERROR: GSC_SERVICE_ACCOUNT_JSON is unset. Either set it "
                "(see docs/seo/GSC_RECRAWL_SETUP.md) or pass --skip-inspect "
                "to render from an existing state file.",
                file=sys.stderr,
            )
            return 2
        _run_inspect(args.state_file, args.limit, args.daily_budget)

    state = _load_state(args.state_file)
    markdown = _render(
        checkpoint_date=args.checkpoint_date,
        baseline_date=args.baseline_date,
        baseline_crawled=args.baseline_crawled,
        baseline_discovered=args.baseline_discovered,
        state=state,
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.output_dir / f"checkpoint_gsc_{args.checkpoint_date.replace('-', '_')}.md"
    out_path.write_text(markdown, encoding="utf-8")
    print(f"✅ Wrote checkpoint: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
