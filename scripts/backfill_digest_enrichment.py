#!/usr/bin/env python3
"""Backfill source-grounded per-item expansion into existing digest posts
(Sub-project A, Task 11).

For each item region that CURRENTLY HAS a deep-analysis block (detected by
the marker line '#### 기술적 배경' inside the region), replace that item's
deep-analysis with a source-grounded expansion built from the article the
item links to (content_generator._maybe_source_expansion, Task 10). The
item's URL is parsed straight out of the existing
'{% include news-card.html ... url="..." %}' block already in the body — no
re-fetch of *current* news, so this is safe to run days after publication
(mirrors backfill_digest_structure.py / backfill_digest_commentary.py).

Fail-closed per item: if _maybe_source_expansion returns None (expansion
flag off, fetch failed, LLM failed, or the honesty gate rejected the
output), that item's text is left completely unchanged.

Usage:
    python3 scripts/backfill_digest_enrichment.py --dry-run --stats \
        --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
    DIGEST_SOURCE_EXPANSION=1 python3 scripts/backfill_digest_enrichment.py \
        --stats --posts-glob '_posts/2026-07-1[12345]-*Weekly_Digest*.md'
"""
import argparse
import glob
import re
import sys
from pathlib import Path

# --- Path setup so we can import scripts.news.* (mirrors
# backfill_digest_structure.py's established pattern). ---
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from scripts.news import content_generator  # noqa: E402

_ITEM_HEADING_RE = re.compile(r"^### (\d+\.\d+) (.*)$")
_TOP_SECTION_RE = re.compile(r"^## ")
_DEEP_ANALYSIS_MARKER_RE = re.compile(r"^#### 기술적 배경")
_HEADING4_RE = re.compile(r"^#### ")
_NEWSCARD_START_RE = re.compile(r"^\{%\s*include news-card\.html\s*$")
_NEWSCARD_END_RE = re.compile(r"^%\}\s*$")
_URL_RE = re.compile(r'url="([^"]*)"')


def _split_front_matter(text: str):
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.DOTALL)
    return (m.group(1), m.group(2)) if m else ("", text)


def _find_item_regions(lines):
    """Return [(start, end, num, title), ...] — end is exclusive, the next
    '### N.M' item heading or next '## ' top-level section heading (or EOF)."""
    regions = []
    current = None
    for i, line in enumerate(lines):
        m = _ITEM_HEADING_RE.match(line)
        if m:
            if current:
                current["end"] = i
                regions.append(current)
            current = {"start": i, "num": m.group(1), "title": m.group(2)}
        elif _TOP_SECTION_RE.match(line) and current:
            current["end"] = i
            regions.append(current)
            current = None
    if current:
        current["end"] = len(lines)
        regions.append(current)
    return regions


def _find_newscard_end(region_lines):
    """Index (relative to region_lines) of the '%}' line closing the
    news-card include, or None if no news-card block is present."""
    start = None
    for i, line in enumerate(region_lines):
        if start is None and _NEWSCARD_START_RE.match(line):
            start = i
            continue
        if start is not None and _NEWSCARD_END_RE.match(line):
            return i
    return None


def _extract_url(region_lines, newscard_end):
    """Search the news-card include block (start..newscard_end inclusive)
    for url="...". Falls back to scanning the whole region if the include
    start line wasn't matched for some reason."""
    block = "\n".join(region_lines[: newscard_end + 1]) if newscard_end is not None \
        else "\n".join(region_lines)
    m = _URL_RE.search(block)
    return m.group(1) if m else ""


def _find_deep_analysis_span(region_lines, newscard_end):
    """Return (da_start, da_end) relative indices for the replaceable
    deep-analysis block, or None if no marker present.

    da_start = first '#### ' heading line after the news-card '%}' line.
    da_end   = the item's trailing '---' separator (exclusive), or region end.
    """
    if not any(_DEEP_ANALYSIS_MARKER_RE.match(ln) for ln in region_lines):
        return None
    search_from = (newscard_end + 1) if newscard_end is not None else 0
    da_start = None
    for i in range(search_from, len(region_lines)):
        if _HEADING4_RE.match(region_lines[i]):
            da_start = i
            break
    if da_start is None:
        return None
    da_end = len(region_lines)
    for i in range(da_start, len(region_lines)):
        if region_lines[i].strip() == "---":
            da_end = i
            break
    return (da_start, da_end)


def process_item(region_lines, stats):
    """Mutates nothing; returns the (possibly) updated region_lines list.

    stats is a dict of counters this call increments in place:
    items_with_deep_analysis, fetched_ok, expanded_ok, replaced.
    """
    newscard_end = _find_newscard_end(region_lines)
    span = _find_deep_analysis_span(region_lines, newscard_end)
    if span is None:
        return region_lines  # no deep-analysis block in this item at all

    stats["items_with_deep_analysis"] += 1
    m = _ITEM_HEADING_RE.match(region_lines[0])
    title = m.group(2) if m else ""
    url = _extract_url(region_lines, newscard_end)
    item = {"title": title, "url": url, "category": "security"}

    # Instrument the two calls _maybe_source_expansion makes internally so
    # we get fetch/expand granularity from the SAME call (no duplicate
    # network/LLM calls) — this literally calls _maybe_source_expansion(item)
    # once, per the spec.
    orig_fetch = content_generator._fetch_article_for
    orig_expand = content_generator._expand_summary_for
    outcome = {}

    def _counting_fetch(u):
        text = orig_fetch(u)
        outcome["fetched_ok"] = bool(text)
        return text

    def _counting_expand(it, article):
        text = orig_expand(it, article)
        outcome["expanded_ok"] = bool(text)
        return text

    content_generator._fetch_article_for = _counting_fetch
    content_generator._expand_summary_for = _counting_expand
    try:
        expanded = content_generator._maybe_source_expansion(item)
    finally:
        content_generator._fetch_article_for = orig_fetch
        content_generator._expand_summary_for = orig_expand

    if outcome.get("fetched_ok"):
        stats["fetched_ok"] += 1
    if outcome.get("expanded_ok"):
        stats["expanded_ok"] += 1

    if not expanded:
        return region_lines  # fail-closed: keep current text unchanged

    da_start, da_end = span
    new_region = (
        region_lines[:da_start]
        + expanded.split("\n")
        + region_lines[da_end:]
    )
    stats["replaced"] += 1
    return new_region


def transform_body(text: str, stats: dict) -> str:
    front, body = _split_front_matter(text)
    lines = body.split("\n")
    regions = _find_item_regions(lines)

    out = []
    cursor = 0
    for region in regions:
        out.extend(lines[cursor:region["start"]])
        region_lines = lines[region["start"]:region["end"]]
        out.extend(process_item(region_lines, stats))
        cursor = region["end"]
    out.extend(lines[cursor:])
    return front + "\n".join(out)


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--posts-glob", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--stats", action="store_true")
    args = ap.parse_args(argv)
    files = sorted(glob.glob(args.posts_glob))
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("no files matched", file=sys.stderr)
        return 1

    changed = 0
    totals = {"items_with_deep_analysis": 0, "fetched_ok": 0, "expanded_ok": 0, "replaced": 0}
    for path in files:
        with open(path, encoding="utf-8") as fh:
            original = fh.read()
        stats = {"items_with_deep_analysis": 0, "fetched_ok": 0, "expanded_ok": 0, "replaced": 0}
        new = transform_body(original, stats)
        for k in totals:
            totals[k] += stats[k]
        if args.stats:
            print(
                f"{path}: items-with-deep-analysis={stats['items_with_deep_analysis']} "
                f"fetched-ok={stats['fetched_ok']} expanded-ok={stats['expanded_ok']} "
                f"replaced={stats['replaced']}"
            )
        if new != original:
            changed += 1
            if args.dry_run:
                print(f"WOULD CHANGE {path}")
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                print(f"CHANGED {path}")
        else:
            print(f"unchanged {path}")
    print(f"{changed}/{len(files)} changed")
    if args.stats:
        print(
            f"TOTAL: items-with-deep-analysis={totals['items_with_deep_analysis']} "
            f"fetched-ok={totals['fetched_ok']} expanded-ok={totals['expanded_ok']} "
            f"replaced={totals['replaced']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
