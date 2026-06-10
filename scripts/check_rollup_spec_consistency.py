#!/usr/bin/env python3
"""Rollup cover spec ↔ owning-post accuracy gate.

The 6 weekly-rollup / monthly-index cover specs (``_data/rollup_covers/*.yml``)
are HAND-AUTHORED and not covered by the visual-builder honesty scorer
(``score_cover_honesty.py`` classifies them ``unknown-system`` → SKIP, because
their highlight labels are free-text, not a fixed builder vocabulary). The
existing ``upgrade_rollup_cover.py --all --check`` only verifies spec ↔ on-disk
SVG drift — NOT whether the spec still agrees with its owning post. This gate
closes that gap with DETERMINISTIC, false-positive-free accuracy checks.

For each spec, against its owning post ``_posts/{date}-{slug}.md``:
  1. The owning post must exist.
  2. ``days[]`` cells that look like dates (``M/D``) must fall within the
     ``period_label`` date range (date-range labels only; whole-month labels
     like "January 2026" are checked at month granularity; non-date cells like
     "Week 1" are skipped — monthly_index summaries).
  3. For ``kind: weekly_rollup`` only: ``daily_count <= redirect_from count``
     (a week's rollup redirects each daily URL + KST-midnight variants, so it
     can never legitimately claim MORE dailies than it redirects). This rule is
     NOT applied to ``monthly_index`` (its daily_count is a month aggregate, far
     larger than the rollup's own 2 redirect entries).
  4. ``severity`` values are in {HIGH, MEDIUM, LOW}.

Design note (why not honesty-score rollups directly): see
``.omc/plans/rollup-cover-realcontent-consistency.md`` — rollup claims are
free-text spec fields, so a fixed claim-class taxonomy (the L20 model) is the
wrong fit and a naive label-token grounding check empirically false-FAILs
honest covers (the labels "SUPPLY CHAIN"/"AUTH BYPASS" are not literal post
tokens). Deterministic spec↔post ACCURACY is the honest, verifiable gate.

Usage:
    python3 scripts/check_rollup_spec_consistency.py            # all specs (default)
    python3 scripts/check_rollup_spec_consistency.py --strict   # exit 1 on violation

Exit codes:
    0  no violations (or warn-only default)
    1  --strict and >=1 violation
    2  usage / dependency error
"""

from __future__ import annotations

import argparse
import calendar
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

try:
    import yaml
except ImportError:
    print("[rollup-spec] ERROR: PyYAML not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
ROLLUP_COVERS_DIR = REPO / "_data" / "rollup_covers"
POSTS_DIR = REPO / "_posts"

_MONTHS = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
_SEVERITIES = {"HIGH", "MEDIUM", "LOW"}
_DATE_CELL_RE = re.compile(r"^\s*(\d{1,2})/(\d{1,2})\s*$")  # "4/13"
# "April 13-19, 2026" / "April 1-5, 2026"
_RANGE_RE = re.compile(r"^([A-Za-z]+)\s+(\d{1,2})\s*[-–]\s*(\d{1,2}),\s*(\d{4})$")
# "January 2026"
_MONTH_RE = re.compile(r"^([A-Za-z]+)\s+(\d{4})$")
_REDIRECT_BLOCK_RE = re.compile(
    r"^redirect_from:\s*\n((?:\s*-\s*.+\n?)+)", re.MULTILINE
)


def _redirect_from_count(post_path: Path) -> int:
    """Count ``redirect_from:`` list entries in a post's front matter."""
    try:
        text = post_path.read_text(encoding="utf-8")
    except OSError:
        return 0
    m = _REDIRECT_BLOCK_RE.search(text)
    if not m:
        return 0
    return len([ln for ln in m.group(1).splitlines() if ln.strip().startswith("-")])


def _period_bounds(period_label: str) -> Optional[Tuple[int, int, int, int]]:
    """Parse a period label into (start_month, start_day, end_month, end_day).

    Returns ``None`` for an unparseable label. A whole-month label
    ("January 2026") yields the full month span so all in-month days pass.
    """
    rng = _RANGE_RE.match(period_label.strip())
    if rng:
        month = _MONTHS.get(rng.group(1).lower())
        if not month:
            return None
        return (month, int(rng.group(2)), month, int(rng.group(3)))
    mo = _MONTH_RE.match(period_label.strip())
    if mo:
        month = _MONTHS.get(mo.group(1).lower())
        if not month:
            return None
        last = calendar.monthrange(int(mo.group(2)), month)[1]
        return (month, 1, month, last)
    return None


def _day_in_period(cell: str, bounds: Tuple[int, int, int, int]) -> Optional[bool]:
    """True/False if a ``M/D`` day cell falls in bounds; None if not a date cell."""
    m = _DATE_CELL_RE.match(cell)
    if not m:
        return None  # "Week 1" etc. — not a date cell, skip
    mon, day = int(m.group(1)), int(m.group(2))
    sm, sd, em, ed = bounds
    return (sm, sd) <= (mon, day) <= (em, ed)


def check_spec(spec_path: Path) -> List[str]:
    """Return a list of violation strings for one rollup spec ([] = clean)."""
    violations: List[str] = []
    try:
        data = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{spec_path.name}: YAML parse error: {exc}"]
    if not isinstance(data, dict):
        return [f"{spec_path.name}: spec is not a mapping"]

    name = spec_path.name
    date = str(data.get("date", ""))
    slug = str(data.get("slug", ""))
    kind = str(data.get("kind", "weekly_rollup"))

    # 1. Owning post must exist.
    post = POSTS_DIR / f"{date}-{slug}.md"
    if not post.exists():
        violations.append(f"{name}: owning post not found: {post.name}")
        return violations  # downstream checks need the post

    # 2. days[] date cells within period_label.
    bounds = _period_bounds(str(data.get("period_label", "")))
    days = data.get("days") or []
    if bounds is None and any(_DATE_CELL_RE.match(str(d.get("date", ""))) for d in days):
        violations.append(
            f"{name}: unparseable period_label {data.get('period_label')!r} but days[] has date cells"
        )
    elif bounds is not None:
        for d in days:
            cell = str(d.get("date", ""))
            inside = _day_in_period(cell, bounds)
            if inside is False:
                violations.append(
                    f"{name}: day {cell!r} outside period {data.get('period_label')!r}"
                )

    # 3. weekly_rollup: daily_count <= redirect_from count.
    daily_count = data.get("daily_count")
    if kind == "weekly_rollup" and isinstance(daily_count, int):
        rc = _redirect_from_count(post)
        if rc and daily_count > rc:
            violations.append(
                f"{name}: daily_count {daily_count} > redirect_from {rc} "
                f"(weekly rollup cannot claim more dailies than it redirects)"
            )

    # 4. severity enum on highlights + days.
    for item in (data.get("top_highlights") or []):
        sev = str(item.get("severity", "")).upper()
        if sev and sev not in _SEVERITIES:
            violations.append(f"{name}: top_highlight severity {sev!r} not in {sorted(_SEVERITIES)}")
    for d in days:
        sev = str(d.get("severity", "")).upper()
        if sev and sev not in _SEVERITIES:
            violations.append(f"{name}: day severity {sev!r} not in {sorted(_SEVERITIES)}")

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Rollup spec ↔ owning-post accuracy gate")
    parser.add_argument("--all", action="store_true", default=True, help="check all specs (default)")
    parser.add_argument("--strict", action="store_true", help="exit 1 on any violation")
    args = parser.parse_args()

    if not ROLLUP_COVERS_DIR.is_dir():
        print(f"[rollup-spec] no rollup_covers dir at {ROLLUP_COVERS_DIR}")
        return 0

    specs = sorted(ROLLUP_COVERS_DIR.glob("*.yml"))
    all_violations: List[str] = []
    for spec in specs:
        all_violations.extend(check_spec(spec))

    if all_violations:
        for v in all_violations:
            print(f"[rollup-spec] VIOLATION: {v}")
        print(f"\n[rollup-spec] {len(all_violations)} violation(s) across {len(specs)} spec(s).")
        return 1 if args.strict else 0
    print(f"[rollup-spec] OK — {len(specs)} spec(s) checked, 0 violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
