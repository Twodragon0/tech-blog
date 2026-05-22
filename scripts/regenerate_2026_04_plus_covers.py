#!/usr/bin/env python3
"""One-shot: regenerate every 2026-04+ digest cover as L22 ultra.

Pulls ``title`` + ``excerpt`` from each post's YAML front matter, runs the
L22 ultra dispatch (``scripts.news.l22_dispatch.generate_l22_digest_svg``)
which yields a deterministic 65-70 KB three-band cover with QR encoding
the canonical post URL, then re-renders the raster variants
(_og.png / _og.avif / _og.webp / _card.avif / _card.webp).

Idempotent — running twice produces the same SVG byte-for-byte (the L22
generator is deterministic for the same title/excerpt/filename trio).

Usage::

    python3 scripts/regenerate_2026_04_plus_covers.py --dry-run     # report only
    python3 scripts/regenerate_2026_04_plus_covers.py --commit      # rewrite SVGs + variants

Filters: only acts on posts whose filename starts with ``2026-04-`` or
``2026-05-`` and whose ``image:`` front matter points to an SVG in
``assets/images/``. Non-digest posts whose excerpt does not parse into
three story headlines still get a valid L22 cover — the dispatcher falls
back to title-derived headlines.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.news.l22_dispatch import generate_l22_digest_svg  # noqa: E402

POSTS_DIR = ROOT / "_posts"
IMAGES_DIR = ROOT / "assets" / "images"

# Reference posts whose covers are pinned baselines for visual regression
# tests. Excluded from bulk regen to keep test fixtures stable.
#
# - test_l20_hero_visual.py: pins 2026-04-08 (L20 hero reference).
# - test_l22_golden_snapshots.py: byte-equality against twelve hand-curated
#   L22 ultra covers rendered by scripts/upgrade_digest_cover.py.
#
# Touching these would break golden-snapshot CI. Add new entries here if a
# golden fixture is added or moved.
PINNED_REFERENCES = {
    "2026-04-08-Tech_Security_Weekly_Digest_AI_CVE_Docker_Botnet.md",
    "2026-04-29-Tech_Security_Weekly_Digest_CVE_AI_Ransomware_Update.md",
    "2026-04-30-Tech_Security_Weekly_Digest_AI_Malware_Rust.md",
    "2026-05-01-Tech_Security_Weekly_Digest_AI_AWS_Threat_Cloud.md",
    "2026-05-02-Tech_Security_Weekly_Digest_AI_Go_Security_AWS.md",
    "2026-05-03-Tech_Security_Weekly_Digest_Ransomware_Azure_CVE_Vulnerability.md",
    "2026-05-04-Tech_Security_Weekly_Digest_AI_Data_CVE_Malware.md",
    "2026-05-05-Tech_Security_Weekly_Digest_AI_Patch_AWS.md",
    "2026-05-06-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.md",
    "2026-05-07-Tech_Security_Weekly_Digest_AI_Botnet_AWS_Ransomware.md",
    "2026-05-08-Tech_Security_Weekly_Digest_CVE_Cloud_AI_Agent.md",
    "2026-05-09-Tech_Security_Weekly_Digest_Vulnerability_AI_Threat.md",
    "2026-05-10-Tech_Security_Weekly_Digest_Malware_Patch_AI_Agent.md",
}


def collect_targets(month_glob: str = "2026-04-*.md") -> List[Tuple[Path, Path]]:
    """Return [(post_md_path, svg_output_path), ...] for posts in scope.

    Defaults to April 2026 only (the user-confirmed scope). Pass a different
    glob (e.g. "2026-0[45]-*.md") to widen later.
    """
    targets: List[Tuple[Path, Path]] = []
    for post in sorted(POSTS_DIR.glob(month_glob)):
        if post.name in PINNED_REFERENCES:
            continue
        text = post.read_text(encoding="utf-8")
        try:
            fm_block = text.split("---", 2)[1]
            fm = yaml.safe_load(fm_block) or {}
        except Exception:
            continue
        img = fm.get("image") or ""
        if not img.endswith(".svg"):
            continue
        svg_name = Path(img).name
        svg_path = IMAGES_DIR / svg_name
        targets.append((post, svg_path))
    return targets


def regenerate_one(post: Path, svg_path: Path) -> bool:
    text = post.read_text(encoding="utf-8")
    fm = yaml.safe_load(text.split("---", 2)[1]) or {}
    post_info = {
        "title": fm.get("title", "") or "",
        "excerpt": fm.get("excerpt", "") or "",
        "filename": post.stem + ".md",
        "content": text,
    }
    return generate_l22_digest_svg(post_info, svg_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate 2026-04+ digest covers as L22 ultra.")
    parser.add_argument("--dry-run", action="store_true", help="Report targets without writing")
    parser.add_argument("--commit", action="store_true", help="Write new SVGs")
    args = parser.parse_args()

    targets = collect_targets()
    print(f"Targets: {len(targets)} posts")

    if args.dry_run or not args.commit:
        for post, svg in targets[:5]:
            print(f"  [dry-run] {post.name} → {svg.name}")
        if len(targets) > 5:
            print(f"  ... and {len(targets) - 5} more")
        print("\nUse --commit to apply.")
        return 0

    ok = 0
    fail = 0
    for post, svg in targets:
        if regenerate_one(post, svg):
            ok += 1
            print(f"  ok   {svg.name}")
        else:
            fail += 1
            print(f"  FAIL {svg.name}")

    print(f"\nDone: {ok} ok, {fail} failed (out of {len(targets)})")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
