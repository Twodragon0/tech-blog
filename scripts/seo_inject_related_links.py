#!/usr/bin/env python3
"""Inject "관련 포스트" internal-link sections into Weekly-Digest posts.

Why this exists
---------------
GSC audit (2026-05-19) found 105 daily Weekly-Digest posts have **zero**
outbound internal links to other digests. That makes every digest a graph
orphan — Google's crawl prioritization and PageRank diffusion both penalise
orphans, which compounds the "Crawled, currently not indexed" backlog.

This script appends a "🔗 관련 포스트" section to each digest with 3 links
to nearby-date digests (preferring ±1d, ±3d, ±7d offsets so each post
sits on a chain rather than an island).

Scope & safety
--------------
- Only touches files matching ``_posts/YYYY-MM-DD-Tech_Security_Weekly_Digest_*.md``
- Skips monthly roll-ups (Week3/Week4/MonthN/...)
- Inserts a ``<!-- related-posts:v1 -->`` HTML marker so re-runs are no-ops
- Injects before the trailing ``---`` + ``**작성자**`` block when present,
  otherwise at end-of-file

Usage
-----
::

    python3 scripts/seo_inject_related_links.py            # dry-run
    python3 scripts/seo_inject_related_links.py --apply    # write changes
    python3 scripts/seo_inject_related_links.py --apply --month 2026-05
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date as Date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = ROOT / "_posts"

DIGEST_GLOB = "20*-Tech_Security_Weekly_Digest_*.md"
MARKER = "<!-- related-posts:v1 -->"

# Preferred temporal offsets (days). 0 is skipped to avoid self-references.
PREFERRED_OFFSETS: tuple[int, ...] = (
    -1,
    1,
    -3,
    3,
    -7,
    7,
    -2,
    2,
    -5,
    5,
    -14,
    14,
    -30,
    30,
)

_FILENAME_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>Tech_Security_Weekly_Digest_.+)\.md$"
)
_TITLE_RE = re.compile(r'^title:\s*"(.+?)"\s*$', re.MULTILINE)
# A post carrying this key has its URL 301'd elsewhere by vercel.json (the 30
# April 2026 dailies consolidated into 4 weekly rollups). Such a post must
# neither be offered as a link target nor receive a block of its own: the link
# text names the daily and the click lands on a different article. Matched on
# the front matter only — the body of a rollup legitimately discusses it.
_SUPERSEDED_RE = re.compile(r"^superseded_by:\s*\S+", re.MULTILINE)


def _is_superseded(text: str) -> bool:
    if not text.startswith("---"):
        return False
    parts = text.split("---", 2)
    return len(parts) >= 3 and bool(_SUPERSEDED_RE.search(parts[1]))


def _is_monthly_rollup(name: str) -> bool:
    stem = name.lower()
    return any(
        token in stem for token in ("week3_", "week4_", "week5_", "month", "monthly")
    )


def _parse_date(s: str) -> Date | None:
    try:
        y, m, d = s.split("-")
        return Date(int(y), int(m), int(d))
    except (ValueError, AttributeError):
        return None


def _post_url(date_str: str, slug: str) -> str:
    y, m, d = date_str.split("-")
    return f"/posts/{y}/{m}/{d}/{slug}/"


def _extract_title(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    if not text.startswith("---"):
        return ""
    fm = text.split("---", 2)[1]
    m = _TITLE_RE.search(fm)
    return m.group(1).strip() if m else ""


def _gather_digests(posts_dir: Path) -> dict[Date, tuple[Path, str, str]]:
    """Return ``{date: (path, slug, title)}`` for every eligible digest."""
    out: dict[Date, tuple[Path, str, str]] = {}
    for path in sorted(posts_dir.glob(DIGEST_GLOB)):
        if _is_monthly_rollup(path.name):
            continue
        m = _FILENAME_RE.match(path.name)
        if not m:
            continue
        d = _parse_date(m.group("date"))
        if d is None:
            continue
        try:
            if _is_superseded(path.read_text(encoding="utf-8")):
                continue
        except OSError:
            continue
        title = _extract_title(path)
        if not title:
            continue
        # Same date already seen → keep the first (alphabetically-earlier name)
        if d in out:
            continue
        out[d] = (path, m.group("slug"), title)
    return out


def _pick_neighbors(
    target: Date,
    catalog: dict[Date, tuple[Path, str, str]],
    n: int = 3,
) -> list[tuple[Date, str, str]]:
    """Pick up to ``n`` neighbors using the preferred-offset ordering."""
    chosen: list[tuple[Date, str, str]] = []
    seen: set[Date] = {target}
    from datetime import timedelta

    for delta in PREFERRED_OFFSETS:
        candidate_date = target + timedelta(days=delta)
        if candidate_date in seen:
            continue
        if candidate_date in catalog:
            _path, slug, title = catalog[candidate_date]
            chosen.append((candidate_date, slug, title))
            seen.add(candidate_date)
            if len(chosen) >= n:
                break
    # Fall back: scan all catalog dates by absolute distance if we are short
    if len(chosen) < n:
        remaining = sorted(
            (d for d in catalog if d not in seen),
            key=lambda d: abs((d - target).days),
        )
        for d in remaining:
            if len(chosen) >= n:
                break
            _path, slug, title = catalog[d]
            chosen.append((d, slug, title))
            seen.add(d)
    return chosen


def _build_section(
    neighbors: list[tuple[Date, str, str]],
) -> str:
    if not neighbors:
        return ""
    lines = ["", "---", "", "## 🔗 관련 포스트", "", MARKER, ""]
    for d, slug, title in neighbors:
        url = _post_url(d.isoformat(), slug)
        lines.append(f"- [{title}]({url}) — {d.isoformat()}")
    lines.append("")
    return "\n".join(lines)


_AUTHOR_RE = re.compile(
    r"\n---\s*\n+\*\*작성자\*\*\s*:\s*[^\n]+\s*\n*$",
    re.MULTILINE,
)


def _inject(body: str, section: str) -> str:
    """Insert ``section`` before the trailing ``---\\n**작성자**`` block, or
    at the end of the body if that footer is absent."""
    m = _AUTHOR_RE.search(body)
    if m:
        head = body[: m.start()].rstrip()
        tail = body[m.start() :]
        return head + "\n" + section + tail
    return body.rstrip() + "\n" + section + "\n"


# The whole generated block, marker included, so an existing one can be
# REPLACED rather than skipped. `_process_file` used to bail on sight of the
# marker, which made every block permanent: one generated against a stale
# catalog could never be corrected, and the 7 links to superseded April dailies
# found on 2026-09-10 would have survived every future run. Anchored on the
# marker and consuming only the list items that follow it, so it cannot swallow
# the trailing footer.
_SECTION_RE = re.compile(
    r"\n---\s*\n+##\s*🔗\s*관련 포스트\s*\n+" + re.escape(MARKER) + r"\s*\n+"
    r"(?:-\s*\[[^\n]*\n)*",
)


def _process_file(path: Path, catalog: dict, apply: bool) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    if _is_superseded(text):
        return False, "superseded"
    if not text.startswith("---"):
        return False, "no-front-matter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, "malformed"
    fm = parts[1]
    body = parts[2]

    m = _FILENAME_RE.match(path.name)
    if not m:
        return False, "name-mismatch"
    d = _parse_date(m.group("date"))
    if d is None:
        return False, "bad-date"

    neighbors = _pick_neighbors(d, catalog, n=3)
    if len(neighbors) < 2:
        return False, "no-neighbors"

    section = _build_section(neighbors)
    # Strip any existing block first, then inject the freshly computed one. The
    # equality check below turns this into a no-op when nothing changed, so the
    # script stays idempotent while becoming self-correcting.
    body = _SECTION_RE.sub("\n", body, count=1)
    new_body = _inject(body, section)
    new_text = "---" + fm + "---" + new_body

    if new_text == text:
        return False, "no-change"

    if apply:
        path.write_text(new_text, encoding="utf-8")
    return True, "rewritten" if apply else "would-rewrite"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="Write changes (default: dry-run)"
    )
    parser.add_argument(
        "--month", default=None, help="Optional YYYY-MM filter (e.g. 2026-05)"
    )
    args = parser.parse_args()

    catalog = _gather_digests(POSTS_DIR)
    if not catalog:
        print(f"No digests found under {POSTS_DIR}", file=sys.stderr)
        return 1

    candidates = sorted(POSTS_DIR.glob(DIGEST_GLOB))
    if args.month:
        candidates = [p for p in candidates if p.name.startswith(args.month)]
    candidates = [p for p in candidates if not _is_monthly_rollup(p.name)]

    # `already-v1` is gone: the marker no longer short-circuits the run, so
    # "nothing to do" is now `no-change` — an answer the script computed rather
    # than one it assumed. `superseded` counts posts skipped because their URL
    # 301s elsewhere.
    stats = {
        "rewritten": 0,
        "no-change": 0,
        "superseded": 0,
        "no-neighbors": 0,
        "skipped": 0,
    }
    for path in candidates:
        changed, reason = _process_file(path, catalog, apply=args.apply)
        if changed:
            stats["rewritten"] += 1
            print(f"[REWRITE] {path.relative_to(ROOT)}")
        elif reason in ("no-change", "superseded"):
            stats[reason] += 1
        elif reason == "no-neighbors":
            stats["no-neighbors"] += 1
            print(f"[SKIP   ] {path.name} (no-neighbors)")
        else:
            stats["skipped"] += 1
            print(f"[SKIP   ] {path.name} ({reason})")

    print()
    print(f"Total candidates  : {len(candidates)}")
    print(f"  Rewritten       : {stats['rewritten']}")
    print(f"  Unchanged       : {stats['no-change']}")
    print(f"  Superseded      : {stats['superseded']}")
    print(f"  No neighbors    : {stats['no-neighbors']}")
    print(f"  Other skipped   : {stats['skipped']}")
    if not args.apply:
        print()
        print("Dry-run only. Re-run with --apply to write changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
