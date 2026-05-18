#!/usr/bin/env python3
"""GSC priority queue + daily action report (PR-2).

Consumes the read-only inspection state file produced by `gsc_inspect.py`
(PR-1) and emits two things:

1. A priority-ranked action list — scored per the plan §3.2 formula
2. A markdown action report at `.omc/reports/gsc-daily-action-YYYY-MM-DD.md`

The script is read-only with respect to external APIs. It only reads the
already-polled state file and, optionally, a directory of prior-day snapshots
to compute a "consecutive stuck" counter per URL.

Usage:
    python3 scripts/gsc_priority.py [--state PATH] [--history-dir PATH]
                                    [--output PATH] [--top-n N] [--dry-run]

See docs/seo/GSC_RECRAWL_SETUP.md (PR-2 section) for what the report
contains and how to use it with the GSC UI.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# Defaults

DEFAULT_STATE = Path(".omc/state/gsc-queue.json")
DEFAULT_HISTORY_DIR = Path(".omc/state/gsc-queue-history")
DEFAULT_REPORT_DIR = Path(".omc/reports")
DEFAULT_TOP_N = 10

# Priority-score coefficients (see plan §3.2 + executor decision in PR description).
RECENCY_MAX_PTS = 40.0
RECENCY_HORIZON_DAYS = 365
ENGAGEMENT_MAX_PTS = 0.0          # reserved, hook for PR-5
SITEMAP_AGE_MAX_PTS = 20.0
SITEMAP_AGE_FULL_DAYS = 140       # 20 weeks ≈ full credit
STUCK_BASE_PTS = 15.0
STUCK_PER_RUN_PTS = 1.0
STUCK_PER_RUN_CAP = 15.0

STUCK_COVERAGE_STATES = (
    "discovered - currently not indexed",
    "discovered, not indexed",
    "crawled - currently not indexed",
    "crawled, not indexed",
)

# Front-matter date pattern in post slugs (YYYY-MM-DD-Title)
SLUG_DATE_RE = re.compile(r"/(\d{4}-\d{2}-\d{2})[-_]")


# Helpers


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    """Best-effort ISO-8601 parser, tolerant of trailing 'Z' and offsets."""
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    # datetime.fromisoformat in 3.11+ accepts most forms but not 'Z'
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _days_between(later: datetime, earlier: datetime) -> float:
    return max(0.0, (later - earlier).total_seconds() / 86400.0)


def is_stuck_state(coverage_state: Optional[str]) -> bool:
    if not coverage_state:
        return False
    cs = coverage_state.strip().lower()
    return any(needle in cs for needle in STUCK_COVERAGE_STATES)


def infer_publish_date_from_url(url: Optional[str]) -> Optional[date]:
    """Extract YYYY-MM-DD from a Jekyll-style permalink slug.

    The blog uses `/{category}/YYYY-MM-DD-Title/` style URLs for posts. If the
    URL embeds a date we can use it as a publish-date proxy without reading
    the source markdown. Returns None if no date found.
    """
    if not url:
        return None
    m = SLUG_DATE_RE.search(url)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


# Score components (each returns float clamped to its max)


def recency_score(
    publish_date: Optional[date], today: date,
) -> float:
    """Fresh posts deserve faster indexing visibility.

    Linear decay from RECENCY_MAX_PTS at 0 days to 0 at RECENCY_HORIZON_DAYS.
    Returns 0 if no publish date is known (we cannot reward unknown freshness).
    """
    if publish_date is None:
        return 0.0
    days = (today - publish_date).days
    if days < 0:
        # Future-dated post — treat as 0 days old.
        days = 0
    if days >= RECENCY_HORIZON_DAYS:
        return 0.0
    return RECENCY_MAX_PTS * (1.0 - days / RECENCY_HORIZON_DAYS)


def sitemap_age_score(
    last_crawl_time: Optional[str], now: datetime,
) -> float:
    """Old `lastCrawlTime` → higher priority (Google may not have refetched).

    Linear ramp from 0 pts at 0 days to SITEMAP_AGE_MAX_PTS at
    SITEMAP_AGE_FULL_DAYS. Uses `lastCrawlTime` from GSC as a proxy for
    sitemap freshness — both signal "how long since Google last looked".
    """
    last_crawl = _parse_iso(last_crawl_time)
    if last_crawl is None:
        # No crawl data → URL has never been crawled. Treat as maximally stale
        # to surface it. This matches the "Discovered, not indexed" intent
        # where `lastCrawlTime` is typically null.
        return SITEMAP_AGE_MAX_PTS
    days = _days_between(now, last_crawl)
    if days >= SITEMAP_AGE_FULL_DAYS:
        return SITEMAP_AGE_MAX_PTS
    return SITEMAP_AGE_MAX_PTS * (days / SITEMAP_AGE_FULL_DAYS)


def stuck_penalty_score(
    coverage_state: Optional[str], consecutive_count: int,
) -> float:
    """Reward URLs that have been stuck across consecutive runs.

    Only applies when the URL is currently in a "stuck" coverage state
    (Discovered/Crawled, not indexed). First run with no history -> 0.

    Formula: STUCK_BASE_PTS + min(STUCK_PER_RUN_CAP, N * STUCK_PER_RUN_PTS)
    where N is the number of consecutive prior runs in a stuck state.
    """
    if not is_stuck_state(coverage_state):
        return 0.0
    if consecutive_count <= 0:
        return 0.0
    extra = min(STUCK_PER_RUN_CAP, float(consecutive_count) * STUCK_PER_RUN_PTS)
    return STUCK_BASE_PTS + extra


def engagement_score(_url: str) -> float:
    """Placeholder hook for future Plausible/GA4 integration (PR-5).

    Always returns 0 until an engagement source is wired in. Kept as a
    function so the formula composition stays the same shape and future
    PRs only need to fill in this function.
    """
    return ENGAGEMENT_MAX_PTS


# History / state loading


def load_state(state_path: Path) -> Optional[Dict[str, Any]]:
    """Load a queue state file. Returns None (with warning) if missing/bad."""
    if not state_path.exists():
        print(
            f"WARN: state file not found: {state_path}. "
            "Run scripts/gsc_inspect.py first (see "
            "docs/seo/GSC_RECRAWL_SETUP.md).",
            file=sys.stderr,
        )
        return None
    try:
        with open(state_path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"WARN: failed to load state {state_path}: {exc}", file=sys.stderr)
        return None


def load_history(history_dir: Path) -> List[Dict[str, Any]]:
    """Load all YYYY-MM-DD.json snapshots from history_dir, newest last.

    Missing or empty directory returns []. Files that don't parse are skipped
    with a warning — a single bad day shouldn't break today's report.
    """
    if not history_dir.exists() or not history_dir.is_dir():
        return []
    snapshots: List[Tuple[str, Dict[str, Any]]] = []
    for path in sorted(history_dir.glob("*.json")):
        try:
            with open(path, encoding="utf-8") as fh:
                snapshots.append((path.stem, json.load(fh)))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"WARN: skip history file {path}: {exc}", file=sys.stderr)
            continue
    return [snap for _, snap in snapshots]


def build_stuck_counts(
    history: List[Dict[str, Any]], today_state: Dict[str, Any],
) -> Dict[str, int]:
    """For each URL, count consecutive prior-day runs ending stuck.

    The count is the number of consecutive history snapshots (walking back
    from the most recent) in which the URL appeared with a "stuck" coverage
    state. The current day's state is NOT counted here (it is reflected in
    the live `coverage_state` passed to stuck_penalty_score).
    """
    counts: Dict[str, int] = {}
    urls_in_today = {entry.get("url") for entry in today_state.get("urls", [])}

    # Walk history newest -> oldest, breaking the streak on first non-stuck.
    by_url_streak: Dict[str, int] = {url: 0 for url in urls_in_today if url}
    streak_open: Dict[str, bool] = {url: True for url in by_url_streak}

    for snapshot in reversed(history):
        snapshot_index = {
            entry.get("url"): entry.get("coverage_state")
            for entry in snapshot.get("urls", [])
            if entry.get("url")
        }
        for url in list(by_url_streak.keys()):
            if not streak_open.get(url, False):
                continue
            cov = snapshot_index.get(url)
            if cov is None:
                # URL absent in this snapshot — streak broken.
                streak_open[url] = False
                continue
            if is_stuck_state(cov):
                by_url_streak[url] += 1
            else:
                streak_open[url] = False

    for url, n in by_url_streak.items():
        if n > 0:
            counts[url] = n
    return counts


# Scoring + ranking


def score_url(
    entry: Dict[str, Any],
    today: date,
    now: datetime,
    consecutive_stuck: int,
) -> Dict[str, Any]:
    """Compute the score breakdown for a single URL inspection entry."""
    url = entry.get("url", "")
    coverage = entry.get("coverage_state")
    publish_date = infer_publish_date_from_url(url)

    breakdown = {
        "recency": round(recency_score(publish_date, today), 2),
        "engagement": round(engagement_score(url), 2),
        "sitemap_age": round(
            sitemap_age_score(entry.get("last_crawl_time"), now), 2,
        ),
        "stuck_penalty": round(
            stuck_penalty_score(coverage, consecutive_stuck), 2,
        ),
    }
    total = round(sum(breakdown.values()), 2)

    days_since_publish = (today - publish_date).days if publish_date else None
    last_crawl = _parse_iso(entry.get("last_crawl_time"))
    days_since_lastmod = (
        round(_days_between(now, last_crawl), 1) if last_crawl else None
    )

    return {
        "url": url,
        "coverage_state": coverage or "(unknown)",
        "verdict": entry.get("verdict"),
        "indexing_state": entry.get("indexing_state"),
        "days_since_publish": days_since_publish,
        "days_since_lastmod": days_since_lastmod,
        "stuck_count": consecutive_stuck,
        "score_breakdown": breakdown,
        "total_score": total,
        "error": entry.get("error"),
    }


def rank_entries(
    state: Dict[str, Any],
    history: List[Dict[str, Any]],
    today: Optional[date] = None,
    now: Optional[datetime] = None,
) -> List[Dict[str, Any]]:
    """Compute ranked scoring rows from today's state + prior history."""
    today = today or utc_today()
    now = now or datetime.now(timezone.utc)
    stuck_counts = build_stuck_counts(history, state)

    rows = [
        score_url(entry, today, now, stuck_counts.get(entry.get("url", ""), 0))
        for entry in state.get("urls", [])
    ]
    rows.sort(key=lambda r: (-r["total_score"], r["url"]))
    return rows


# Report generation


def summarise_coverage_buckets(
    state: Dict[str, Any],
) -> List[Tuple[str, int]]:
    counts: Dict[str, int] = {}
    for entry in state.get("urls", []):
        bucket = entry.get("coverage_state") or "(unknown)"
        counts[bucket] = counts.get(bucket, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def _md_table(headers: Iterable[str], rows: Iterable[Iterable[Any]]) -> str:
    headers = list(headers)
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        cells = ["" if c is None else str(c) for c in row]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def render_report(
    state: Dict[str, Any],
    ranked: List[Dict[str, Any]],
    today: date,
    top_n: int,
) -> str:
    """Render the daily action report as markdown."""
    totals = state.get("totals", {}) or {}
    generated_at = state.get("generated_at", "(unknown)")
    site_url = state.get("site_url", "(unknown)")

    coverage_rows = [(label, count) for label, count in summarise_coverage_buckets(state)]

    top = ranked[: max(0, top_n)]
    top_rows = []
    for idx, row in enumerate(top, start=1):
        top_rows.append([
            idx,
            row["url"],
            row["total_score"],
            row["coverage_state"],
            row["days_since_publish"] if row["days_since_publish"] is not None else "n/a",
            row["days_since_lastmod"] if row["days_since_lastmod"] is not None else "n/a",
            row["stuck_count"],
        ])

    suggested = [
        "1. Open Google Search Console for "
        f"`{site_url}` (or the matching property).",
        "2. For each URL in the top-10 table above, paste it into the URL "
        "Inspection tool and click **Request Indexing**.",
        "3. GSC enforces an undocumented ~10-12 manual submissions per day per "
        "property cap — work top-down and stop when GSC starts rate-limiting.",
        "4. Repeat the next day. The daily report ranks fresh stale URLs first.",
        "5. URLs stuck > 45 days in `Discovered/Crawled - currently not indexed` "
        "should be flagged for content review per "
        "`.omc/plans/gsc-recrawl-automation.md` §10 (Decision Gate D).",
    ]

    full_rows = []
    for idx, row in enumerate(ranked, start=1):
        full_rows.append([
            idx,
            row["url"],
            row["total_score"],
            row["coverage_state"],
            row["stuck_count"],
            row["verdict"] or "",
            row["error"] or "",
        ])

    parts: List[str] = []
    parts.append(f"# GSC Daily Action Report — {today.isoformat()}")
    parts.append("")
    parts.append(f"- Generated at (state): `{generated_at}`")
    parts.append(f"- Report generated at: `{datetime.now(timezone.utc).isoformat()}`")
    parts.append(f"- Site: `{site_url}`")
    parts.append(
        f"- Totals: inspected={totals.get('inspected', '?')} "
        f"indexed={totals.get('indexed', '?')} "
        f"discovered_not_indexed={totals.get('discovered_not_indexed', '?')} "
        f"crawled_not_indexed={totals.get('crawled_not_indexed', '?')} "
        f"errors={totals.get('errors', '?')}"
    )
    parts.append("")

    parts.append("## Coverage state distribution")
    parts.append("")
    parts.append(_md_table(["Coverage state", "Count"], coverage_rows))
    parts.append("")

    parts.append(f"## Top {len(top)} priority URLs")
    parts.append("")
    if top:
        parts.append(_md_table(
            ["#", "URL", "Score", "Coverage", "Days since publish",
             "Days since last crawl", "Stuck N"],
            top_rows,
        ))
    else:
        parts.append("_No URLs ranked — empty state or all-error run._")
    parts.append("")

    parts.append("## Suggested actions")
    parts.append("")
    parts.extend(suggested)
    parts.append("")

    parts.append("## Full ranked list")
    parts.append("")
    parts.append("<details><summary>Show all ranked URLs</summary>")
    parts.append("")
    parts.append(_md_table(
        ["#", "URL", "Score", "Coverage", "Stuck N", "Verdict", "Error"],
        full_rows,
    ))
    parts.append("")
    parts.append("</details>")
    parts.append("")

    parts.append("## Priority-score formula")
    parts.append("")
    parts.append(
        f"`total = recency({RECENCY_MAX_PTS:.0f}) + "
        f"engagement({ENGAGEMENT_MAX_PTS:.0f}, reserved) + "
        f"sitemap_age({SITEMAP_AGE_MAX_PTS:.0f}) + "
        f"stuck_penalty({STUCK_BASE_PTS:.0f}+min({STUCK_PER_RUN_CAP:.0f}, N))`"
    )
    parts.append("")

    return "\n".join(parts) + "\n"


# CLI


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--state", default=str(DEFAULT_STATE), type=Path,
                        help=f"state file path (default: {DEFAULT_STATE})")
    parser.add_argument("--history-dir", default=str(DEFAULT_HISTORY_DIR),
                        type=Path,
                        help=f"history dir (default: {DEFAULT_HISTORY_DIR})")
    parser.add_argument("--output", default=None, type=Path,
                        help="output report path "
                             "(default: .omc/reports/gsc-daily-action-{today}.md)")
    parser.add_argument("--top-n", type=int, default=DEFAULT_TOP_N,
                        help=f"top-N table size (default: {DEFAULT_TOP_N})")
    parser.add_argument("--dry-run", action="store_true",
                        help="print report to stdout, do not write file")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)

    state = load_state(args.state)
    if state is None:
        # Treat missing/bad state as a soft warning, not a failure — PR-1 may
        # not have run yet on first installation.
        return 0

    history = load_history(args.history_dir)
    today = utc_today()
    ranked = rank_entries(state, history, today=today)
    report = render_report(state, ranked, today, args.top_n)

    if args.dry_run:
        print(report)
        return 0

    output_path = args.output or (
        DEFAULT_REPORT_DIR / f"gsc-daily-action-{today.isoformat()}.md"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
