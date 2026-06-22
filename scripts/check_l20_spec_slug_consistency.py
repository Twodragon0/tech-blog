#!/usr/bin/env python3
"""Gate: L20 cover spec slug must match its owning post's image slug EXACTLY (case-sensitive).

`upgrade_l20_cover.py` derives the output filename from the spec's ``date`` +
``slug`` fields (``{date}-{slug}.svg``). If that slug differs only by CASE from
the post's ``image:`` slug, the spec renders to a wrong-cased filename — harmless
on case-insensitive macOS but a 404 on Linux / Vercel (the post points at the
other casing). The existing ``check_spec_slug_consistency.py`` covers only
``_data/digest_covers/`` and compares case-INSENSITIVELY, so it cannot catch this.

This gate, for each ``_data/l20_covers/*.yml`` spec whose slug matches a post
``image:`` slug case-insensitively, requires an EXACT (case-sensitive) match.
Specs with no matching post (orphan/renamed) are reported as a separate WARNING
(not a hard fail — orphan-spec cleanup is a distinct concern).

Usage:
    python3 scripts/check_l20_spec_slug_consistency.py
Exit 0 = clean, 1 = case mismatch(es) found.
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
SPECS_DIR = REPO / "_data" / "l20_covers"
POSTS = REPO / "_posts"

_IMG_RE = re.compile(r'^image:\s*"?(/assets/images/[^"\n]+\.svg)', re.MULTILINE)
_DATE_RE = re.compile(r'^date:\s*[\'"]?([0-9]{4}-[0-9]{2}-[0-9]{2})', re.MULTILINE)
_SLUG_RE = re.compile(r'^slug:\s*(.+?)\s*$', re.MULTILINE)


def _post_image_slugs() -> Dict[str, str]:
    """lower(slug) -> exact-case slug, from every post's image: field."""
    out: Dict[str, str] = {}
    for p in POSTS.glob("*.md"):
        m = _IMG_RE.search(p.read_text(encoding="utf-8", errors="ignore"))
        if m:
            slug = Path(m.group(1)).stem
            out[slug.lower()] = slug
    return out


def _spec_output_slug(spec_path: Path) -> str | None:
    """Reproduce upgrade_l20_cover's output stem = {date}-{slug}."""
    txt = spec_path.read_text(encoding="utf-8", errors="ignore")
    d = _DATE_RE.search(txt)
    s = _SLUG_RE.search(txt)
    if not (d and s):
        return None
    return f"{d.group(1)}-{s.group(1)}"


def check() -> tuple[List[str], List[str]]:
    posts = _post_image_slugs()
    mismatches: List[str] = []
    orphans: List[str] = []
    for sp in sorted(glob.glob(str(SPECS_DIR / "*.yml"))):
        stem = _spec_output_slug(Path(sp))
        if stem is None:
            continue
        exact = posts.get(stem.lower())
        if exact is None:
            orphans.append(stem)
        elif exact != stem:
            mismatches.append(f"{stem}  != post {exact}")
    return mismatches, orphans


def main() -> int:
    mismatches, orphans = check()
    for o in orphans:
        print(f"[l20-spec-slug] WARN orphan spec (no matching post image): {o}")
    if mismatches:
        print(f"[l20-spec-slug] FAIL — {len(mismatches)} spec slug(s) differ only by CASE from the post (Linux 404 risk):")
        for m in mismatches:
            print(f"  ✗ {m}")
        print("  Fix: edit the spec's `slug:` field to match the post image slug EXACTLY.")
        return 1
    print(f"[l20-spec-slug] OK — all l20 spec slugs case-match their post ({len(orphans)} orphan spec(s) warned).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
