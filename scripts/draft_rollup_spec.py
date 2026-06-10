#!/usr/bin/env python3
"""Auto-draft a weekly-rollup cover spec from the week's daily digests.

Implements piece A of ``.omc/plans/rollup-autogen-and-grounding.md``.

Each ``_data/rollup_covers/*.yml`` is normally HAND-AUTHORED: an editor reads
the week's 5-7 daily digests and types the 3 ``top_highlights`` + per-day
``days[]`` tags. The daily digests already expose structured
``summary_card.highlights`` (and the L20 generator extracts ASCII entities
from them via ``_entity_tokens`` / ``_digest_panels`` in
``scripts/news/l20_dispatch.py``), so most of that authoring can be DRAFTED.

This tool emits a DRAFT spec for the editor to review + tweak, NOT an
auto-commit. The ``label`` (threat category) and the 3-story selection are
editorial judgments, so the draft leaves ``label`` blank and the human keeps
editorial control. Severity / peak parsing from daily bodies is heuristic;
the reviewed-draft altitude means a misparse is caught by the human.

The owning rollup post lists each daily's URL in ``redirect_from`` as
``/posts/{YYYY}/{MM}/{DD}/{slug}/`` (plus 2 self-canonical variants). We
resolve those daily URLs to ``_posts/{YYYY}-{MM}-{DD}-{slug}.md`` and read each
daily's front-matter ``summary_card.highlights`` + body severity table.

Scope / limitations:
  * WEEKLY rollups (``kind: weekly_rollup``) are fully supported — dailies come
    from ``redirect_from``.
  * MONTHLY index specs (``daily_count_source: index_table``) draw their
    dailies from an index table in the post BODY, not ``redirect_from``. This
    tool does NOT parse the monthly index table; pass ``--dailies`` to supply
    the daily post paths explicitly for a monthly draft.

Usage:
    python3 scripts/draft_rollup_spec.py <owning-post-path-or-date>
    python3 scripts/draft_rollup_spec.py 2026-04-05 --write
    python3 scripts/draft_rollup_spec.py <post> --dailies <p1.md> <p2.md> ...

Exit codes:
    0  draft emitted
    2  usage / resolution error
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    print("[draft-rollup] ERROR: PyYAML not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent

# Reuse the L20 ASCII entity extractor — do NOT reimplement (the cover SVG
# quality gate forbids Hangul in <text>, so all rendered text must be ASCII).
# scripts/news/__init__.py imports via the ``scripts.`` package, so the repo
# root (parent of scripts/) must be on sys.path.
sys.path.insert(0, str(REPO))
from scripts.news.l20_dispatch import _CVE_RE, _entity_tokens  # noqa: E402

ROLLUP_COVERS_DIR = REPO / "_data" / "rollup_covers"
POSTS_DIR = REPO / "_posts"

# A daily URL inside redirect_from: /posts/2026/04/01/<slug>/
_DAILY_URL_RE = re.compile(r"^/posts/(\d{4})/(\d{2})/(\d{2})/([^/]+)/?$")
# Severity-table impact cell markers (daily body "빠른 참조" table).
_SEV_MARKERS: Tuple[Tuple[str, str], ...] = (
    ("🔴", "HIGH"),
    ("🟡", "MEDIUM"),
    ("🟢", "LOW"),
)
_HEADLINE_MAX_CHARS = 30
_DETAIL_MAX_CHARS = 60
# Rank severities for ordering top_highlights (peak first).
_SEV_RANK = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "": 0}


def _to_ascii(text: str) -> str:
    """Drop non-ASCII chars and collapse whitespace (cover text is ASCII-only).

    Trims leading/trailing punctuation left behind when Korean is stripped from
    a mixed-script title (e.g. ", CVE-2025-55182" -> "CVE-2025-55182").
    """
    ascii_only = "".join(ch for ch in (text or "") if ord(ch) < 128)
    collapsed = re.sub(r"\s+", " ", ascii_only).strip()
    return collapsed.strip(" ,.;:-/|").strip()


def _shorten(text: str, limit: int) -> str:
    """Trim to <= limit chars on a word boundary, no ellipsis."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip()
    return cut or text[:limit].rstrip()


def parse_frontmatter(text: str) -> Tuple[dict, str]:
    """Return (front_matter_dict, body). Mirrors the repo's other parsers."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}, text
    if not isinstance(fm, dict):
        return {}, text
    return fm, parts[2]


def _has_daily_redirects(post: Path) -> bool:
    """True if a post's front matter lists daily-digest URLs in redirect_from."""
    try:
        fm, _ = parse_frontmatter(post.read_text(encoding="utf-8"))
    except OSError:
        return False
    return bool(daily_urls_from_redirects(fm.get("redirect_from")))


def resolve_owning_post(arg: str) -> Path:
    """Resolve a post path OR a YYYY-MM-DD date to an owning rollup post file.

    A date can match multiple posts (a daily digest AND a weekly rollup share a
    date). Disambiguate deterministically: prefer the post whose redirect_from
    lists daily-digest URLs (the rollup), else the first match alphabetically.
    """
    p = Path(arg)
    if p.suffix == ".md":
        return p if p.is_absolute() else (REPO / p)
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", arg):
        matches = sorted(POSTS_DIR.glob(f"{arg}-*.md"))
        if not matches:
            raise FileNotFoundError(f"no post found for date {arg} in {POSTS_DIR}")
        for m in matches:
            if _has_daily_redirects(m):
                return m
        return matches[0]
    raise ValueError(f"expected a .md post path or a YYYY-MM-DD date, got {arg!r}")


def daily_urls_from_redirects(redirect_from) -> List[Tuple[str, str, str, str]]:
    """Extract (year, month, day, slug) tuples for each daily URL in redirect_from."""
    out: List[Tuple[str, str, str, str]] = []
    for entry in redirect_from or []:
        m = _DAILY_URL_RE.match(str(entry).strip())
        if m:
            out.append((m.group(1), m.group(2), m.group(3), m.group(4)))
    return out


def daily_path_for(year: str, month: str, day: str, slug: str) -> Optional[Path]:
    """Map a daily URL tuple to its _posts file (YYYY-MM-DD-slug.md)."""
    candidate = POSTS_DIR / f"{year}-{month}-{day}-{slug}.md"
    return candidate if candidate.exists() else None


def peak_severity_from_body(body: str) -> str:
    """Return the daily's peak severity from its body table (HIGH > MED > LOW).

    Heuristic: scan the "빠른 참조" / highlight table impact cells for the
    🔴/🟡/🟢 markers and take the highest. Returns "" when no marker is found.
    """
    best = ""
    for marker, sev in _SEV_MARKERS:
        if marker in (body or ""):
            if _SEV_RANK[sev] > _SEV_RANK[best]:
                best = sev
    return best


def severity_for_title(body: str, title: str) -> str:
    """Severity of a specific highlight from its row in the body table.

    Match the highlight's title to its table row (the title text is shared
    between front matter and the table), then read the row's 🔴/🟡/🟢 marker.
    Falls back to the body peak when no row matches.
    """
    needle = (title or "").strip()
    if needle:
        for line in (body or "").splitlines():
            if "|" not in line or needle not in line:
                continue
            for marker, sev in _SEV_MARKERS:
                if marker in line:
                    return sev
    return peak_severity_from_body(body)


def lead_entity(title: str) -> str:
    """Lead entity phrase (1-2 tokens) from a highlight title, ASCII-only.

    Reuses ``_entity_tokens``; prefers a non-CVE proper noun as the lead and
    appends a second token when it fits, mirroring the L20 panel headline rule.
    Returns "" when the title carries no usable ASCII entity.
    """
    toks = _entity_tokens(title)
    if not toks:
        return ""
    non_cve = [t for t in toks if not _CVE_RE.match(t)]
    if non_cve:
        lead = non_cve[0]
        if len(non_cve) > 1 and len(f"{non_cve[0]} {non_cve[1]}") <= _HEADLINE_MAX_CHARS:
            lead = f"{non_cve[0]} {non_cve[1]}"
    else:
        lead = toks[0]
    return _shorten(lead, _HEADLINE_MAX_CHARS)


def build_day_cell(year: str, month: str, day: str, daily_post: Optional[Path]) -> Dict:
    """Build one days[] cell: date (M/D), severity (body peak), tag (lead entity)."""
    date_cell = f"{int(month)}/{int(day)}"
    severity = ""
    tag = ""
    if daily_post is not None:
        fm, body = parse_frontmatter(daily_post.read_text(encoding="utf-8"))
        severity = peak_severity_from_body(body)
        highlights = (fm.get("summary_card") or {}).get("highlights") or []
        for h in highlights:
            if isinstance(h, dict):
                tag = lead_entity(str(h.get("title", "")))
                if tag:
                    break
    return {"date": date_cell, "severity": severity or "MEDIUM", "tag": tag or "Security update"}


def collect_week_highlights(dailies: List[Tuple[str, str, str, Optional[Path]]]) -> List[Dict]:
    """Flatten every daily's highlights into rank-able records.

    Each record: {headline, detail, source, severity, recency} where recency is
    the daily index (later daily = more recent). Highlights with no ASCII entity
    are skipped (they cannot produce a cover-safe headline).
    """
    records: List[Dict] = []
    for recency, (_y, _m, _d, post) in enumerate(dailies):
        if post is None:
            continue
        fm, body = parse_frontmatter(post.read_text(encoding="utf-8"))
        highlights = (fm.get("summary_card") or {}).get("highlights") or []
        for h in highlights:
            if not isinstance(h, dict):
                continue
            title = str(h.get("title", ""))
            headline = lead_entity(title)
            if not headline:
                continue
            records.append(
                {
                    "headline": headline,
                    "detail": _shorten(_to_ascii(title), _DETAIL_MAX_CHARS),
                    "source": _to_ascii(str(h.get("source", ""))),
                    "severity": severity_for_title(body, title) or "MEDIUM",
                    "recency": recency,
                }
            )
    return records


def rank_top_highlights(records: List[Dict], limit: int = 3) -> List[Dict]:
    """Rank by severity then recency, take top ``limit`` distinct stories."""
    ordered = sorted(
        records,
        key=lambda r: (_SEV_RANK.get(r["severity"], 0), r["recency"]),
        reverse=True,
    )
    out: List[Dict] = []
    seen_headlines: set = set()
    for r in ordered:
        key = r["headline"].lower()
        if key in seen_headlines:
            continue
        seen_headlines.add(key)
        out.append(r)
        if len(out) >= limit:
            break
    return out


def build_spec(
    owning_post: Path,
    dailies_override: Optional[List[Path]] = None,
) -> Dict:
    """Build the draft spec dict for ``owning_post``."""
    fm, _body = parse_frontmatter(owning_post.read_text(encoding="utf-8"))
    name = owning_post.name  # YYYY-MM-DD-slug.md
    m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$", name)
    if not m:
        raise ValueError(f"owning post name is not YYYY-MM-DD-slug.md: {name}")
    date, slug = m.group(1), m.group(2)
    categories = fm.get("categories") or ["security", "devsecops"]

    # Resolve dailies: explicit override (monthly) or redirect_from (weekly).
    dailies: List[Tuple[str, str, str, Optional[Path]]] = []
    if dailies_override:
        for p in dailies_override:
            path = p if p.is_absolute() else (REPO / p)
            dm = re.match(r"^(\d{4})-(\d{2})-(\d{2})-", path.name)
            y, mo, d = (dm.group(1), dm.group(2), dm.group(3)) if dm else ("", "", "")
            dailies.append((y, mo, d, path if path.exists() else None))
    else:
        for (y, mo, d, dslug) in daily_urls_from_redirects(fm.get("redirect_from")):
            dailies.append((y, mo, d, daily_path_for(y, mo, d, dslug)))

    if not dailies:
        raise ValueError(
            f"no dailies resolved for {name}. For a monthly index, pass --dailies "
            "with the daily post paths (the monthly index table is not parsed)."
        )

    days = [build_day_cell(y, mo, d, post) for (y, mo, d, post) in dailies]
    records = collect_week_highlights(dailies)
    top = rank_top_highlights(records, limit=3)
    top_highlights = [
        {
            "severity": r["severity"],
            "label": "",  # EDITORIAL — human fills the threat category.
            "headline": r["headline"],
            "detail": r["detail"],
            "source": r["source"],
        }
        for r in top
    ]
    daily_count = sum(1 for (_y, _m, _d, post) in dailies if post is not None)

    return {
        "date": date,
        "slug": slug,
        "daily_count": daily_count,
        "top_highlights": top_highlights,
        "days": days,
        "footer": {"daily_digests": daily_count, "categories": list(categories)},
    }


_HEADER = (
    "# AUTO-GENERATED DRAFT - review before committing.\n"
    "# Source: scripts/draft_rollup_spec.py (piece A of "
    "rollup-autogen-and-grounding.md).\n"
    "# Editorial fields the human must fill/verify:\n"
    "#   - top_highlights[].label : threat category (e.g. SUPPLY CHAIN) - LEFT BLANK.\n"
    "#   - period_label / period_short / sfx / title / aria : add per existing specs.\n"
    "#   - kind : defaults to weekly_rollup; set monthly_index when applicable.\n"
    "# Severity is heuristic (daily body table peak); verify against the dailies.\n"
)


def render_yaml(spec: Dict) -> str:
    """Render the draft spec to a review-friendly, ASCII-only YAML string."""
    body = yaml.safe_dump(
        spec,
        sort_keys=False,
        allow_unicode=False,
        default_flow_style=False,
        width=100,
    )
    return _HEADER + body


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Draft a weekly-rollup cover spec from the week's daily digests.",
        epilog=(
            "MONTHLY index specs (daily_count_source: index_table) are not fully "
            "supported: their dailies live in a body index table, not redirect_from. "
            "Pass --dailies with the daily post paths to draft a monthly spec."
        ),
    )
    parser.add_argument("owning_post", help="owning rollup post path (.md) or YYYY-MM-DD date")
    parser.add_argument(
        "--write",
        action="store_true",
        help="write to _data/rollup_covers/<date>.yml instead of stdout",
    )
    parser.add_argument(
        "--dailies",
        nargs="+",
        metavar="POST",
        help="explicit daily post paths (required for monthly_index drafts)",
    )
    args = parser.parse_args(argv)

    try:
        owning = resolve_owning_post(args.owning_post)
        if not owning.exists():
            print(f"[draft-rollup] ERROR: owning post not found: {owning}", file=sys.stderr)
            return 2
        dailies_override = [Path(p) for p in args.dailies] if args.dailies else None
        spec = build_spec(owning, dailies_override=dailies_override)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[draft-rollup] ERROR: {exc}", file=sys.stderr)
        return 2

    out_text = render_yaml(spec)
    if args.write:
        dest = ROLLUP_COVERS_DIR / f"{spec['date']}.yml"
        dest.write_text(out_text, encoding="utf-8")
        print(f"[draft-rollup] wrote draft to {dest}")
    else:
        sys.stdout.write(out_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
