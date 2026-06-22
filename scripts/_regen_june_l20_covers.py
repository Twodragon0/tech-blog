#!/usr/bin/env python3
"""Faithfully regenerate June 2026 L20 digest covers via the cron render path.

Mirrors ``auto_publish_news`` exactly: builds ``post_info`` with the SAME
fields the cron passes to :func:`_render_l20_svg_string` (title / excerpt /
filename / full post content — NO summary_card, NO category), so the on-disk
cover matches what the unattended publisher would produce. Rasters are rebuilt
with :func:`scripts._rebuild_all_l20_rasters.build_one` (the documented L20
post-render rasterizer). One-shot helper for the content-descriptor subheadline
change; not wired into automation.
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
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--glob", default="2026-06-*.md", help="post glob under _posts/")
    ap.add_argument("--only", default="", help="substring filter on post filename")
    ap.add_argument("--exclude", default="", help="comma-separated substrings; skip posts matching any")
    ap.add_argument("--skip-raster", action="store_true")
    args = ap.parse_args()

    posts = sorted(POSTS.glob(args.glob))
    if args.only:
        posts = [p for p in posts if args.only in p.name]
    if args.exclude:
        bad = [s for s in args.exclude.split(",") if s]
        posts = [p for p in posts if not any(s in p.name for s in bad)]
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
