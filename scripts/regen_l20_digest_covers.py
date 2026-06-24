#!/usr/bin/env python3
"""Faithfully regenerate L20 Hero+2-Card digest covers via the cron render path.

Mirrors ``auto_publish_news`` exactly: builds ``post_info`` with the SAME
fields the cron passes to :func:`_render_l20_svg_string` (title / excerpt /
filename / full post content — NO summary_card, NO category), so the on-disk
cover matches what the unattended publisher would produce. Rasters are rebuilt
with :func:`scripts._rebuild_all_l20_rasters.build_one` (the documented L20
post-render rasterizer). Not wired into automation — a deliberate, gated
regeneration tool.

SAFETY (see CLAUDE.md "Cover Generation System" + memory ``cover-system``):
This renders an L20 **digest** cover for every post it processes. It must NOT
run over spec-driven (``_data/{digest,rollup,l25}_covers/*.yml``), rollup, or
non-digest *content* posts — doing so converts them to L20 and breaks the
drift/size/honesty gates. Two guards:
  * ``--targets-file`` — an explicit allowlist of post stems (the safe path for
    heterogeneous months that mix digests, guides, rollups and specs).
  * default ``--digest-only`` name filter — skips posts whose filename is not a
    digest (disable with ``--no-digest-only`` only when you know every match is
    a digest). Always run the full cover-verify gate suite afterwards.

Examples::

    # Whole month, digest-name-filtered:
    python3 scripts/regen_l20_digest_covers.py --glob "2026-06-*.md"
    # Heterogeneous month via an explicit allowlist (safest):
    python3 scripts/regen_l20_digest_covers.py --targets-file /tmp/targets.txt
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
POSTS = REPO / "_posts"
ASSETS = REPO / "assets" / "images"
if str(REPO / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO / "scripts"))

from auto_publish_news import _render_l20_svg_string  # noqa: E402
from _rebuild_all_l20_rasters import build_one  # noqa: E402

_TITLE_RE = re.compile(r'^title:\s*"?([^\n"]+)"?\s*$', re.MULTILINE)
_EXCERPT_RE = re.compile(r'^excerpt:\s*"?([^\n"]+)"?\s*$', re.MULTILINE)
_IMAGE_RE = re.compile(r'^image:\s*"?(/assets/images/[^\n"]+\.svg)"?\s*$', re.MULTILINE)
# Digest-name guard: only filenames carrying a digest stem are L20-digest posts.
# Guides/postmortems/courses use the content-cover path and must be skipped.
_DIGEST_NAME_RE = re.compile(
    r"(Weekly_Digest|Daily_Tech_Digest|Security_Digest|AI_Cloud_Digest|"
    r"Blockchain_Tech_Digest|Security_Cloud_Digest)",
    re.IGNORECASE,
)


def _is_digest_post(name: str) -> bool:
    """True for a daily/weekly digest post (NOT a rollup/monthly or guide)."""
    if "Monthly_Index" in name or re.search(r"Week[1-4]_", name):
        return False
    return bool(_DIGEST_NAME_RE.search(name))


def _post_info(post_path: Path) -> dict:
    """Mirror the inline ``post_info_for_l20`` dict built in auto_publish_news.

    Same field-construction logic the cron uses (title/excerpt via the same
    regexes + .strip(), filename, full content, no summary_card / category),
    reading the already-published ``.md`` from disk instead of the cron's
    in-memory ``post_content`` (identical for published posts).
    """
    content = post_path.read_text(encoding="utf-8")
    info = {"title": "", "filename": post_path.name, "excerpt": "", "content": content}
    m_title = _TITLE_RE.search(content)
    m_excerpt = _EXCERPT_RE.search(content)
    if m_title:
        info["title"] = m_title.group(1).strip()
    if m_excerpt:
        info["excerpt"] = m_excerpt.group(1).strip()
    return info


def _svg_name(post_path: Path) -> str | None:
    content = post_path.read_text(encoding="utf-8")
    m = _IMAGE_RE.search(content)
    return Path(m.group(1)).name if m else None


def regen(post_path: Path, raster: bool) -> str:
    info = _post_info(post_path)
    svg_name = _svg_name(post_path)
    if not svg_name:
        return f"SKIP no-image {post_path.name}"
    svg = _render_l20_svg_string(info)
    if not svg:
        return f"FAIL empty-render {post_path.name}"
    out = ASSETS / svg_name
    out.write_text(svg, encoding="utf-8")
    note = "SVG"
    if raster:
        _name, ok, err = build_one(svg_name)
        note = "SVG+raster" if ok else f"SVG (raster FAIL: {err})"
    return f"OK [{note}] {svg_name}"


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--glob", default="2026-06-*.md", help="post glob under _posts/ (pathlib ranges OK, e.g. '2026-0[123]-*.md')")
    ap.add_argument("--only", default="", help="substring filter on post filename")
    ap.add_argument("--exclude", default="", help="comma-separated substrings; skip posts matching any")
    ap.add_argument("--targets-file", default="", help="path to a newline-delimited allowlist of post stems (no .md); overrides --glob")
    ap.add_argument("--no-digest-only", dest="digest_only", action="store_false",
                    help="disable the digest-name safety filter (DANGER: only when every match is a digest)")
    ap.add_argument("--skip-raster", action="store_true")
    ap.set_defaults(digest_only=True)
    args = ap.parse_args()

    if args.targets_file:
        stems = [s.strip() for s in Path(args.targets_file).read_text().splitlines() if s.strip()]
        posts = [POSTS / f"{s}.md" for s in stems]
        missing = [p.name for p in posts if not p.exists()]
        if missing:
            print(f"ERROR: {len(missing)} target(s) not found, e.g. {missing[:3]}")
            return 1
    else:
        posts = sorted(POSTS.glob(args.glob))
        if args.only:
            posts = [p for p in posts if args.only in p.name]
        if args.exclude:
            bad = [s for s in args.exclude.split(",") if s]
            posts = [p for p in posts if not any(s in p.name for s in bad)]

    skipped = []
    if args.digest_only:
        kept = [p for p in posts if _is_digest_post(p.name)]
        skipped = [p for p in posts if p not in kept]
        posts = kept
    for p in skipped:
        print(f"SKIP non-digest {p.name}")
    if not posts:
        print("no posts matched")
        return 1
    for p in posts:
        try:
            print(regen(p, raster=not args.skip_raster))
        except Exception as exc:  # one bad post must not abort the batch
            print(f"FAIL {p.name}: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
