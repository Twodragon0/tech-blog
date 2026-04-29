#!/usr/bin/env python3
"""Regenerate 2025-* legacy cover SVGs to HQ tier using the L25 template
generator (no LLM API).

Pipeline (per post):
    1. Parse front matter and body via post_l25_router
    2. Derive an L25 config dict (3 bands, theme, stats)
    3. Render the SVG via svg_l25_generator
    4. Validate with the same rules as upgrade_2025_svgs.validate_svg
    5. Backup existing SVG to assets/images/.backup/
    6. Write new SVG, then run fix_svg_forbidden_chars.fix_svg_file
    7. Restore from backup on any verification failure

Usage:
    python3 scripts/regen_2025_svgs.py [options]

Options:
    --posts N             process first N posts only
    --dry-run             print derived config JSON, do not write
    --post-glob GLOB      override post pattern (default: 2025-*.md)
    --out-dir DIR         output directory (default: assets/images)
    --no-backup           skip creating .backup copies
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"
BACKUP_DIR = IMAGES_DIR / ".backup"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Make sibling and library imports work
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR.parent))

# Reuse the validate_svg function from the existing upgrade script
from upgrade_2025_svgs import (  # noqa: E402
    parse_front_matter,
    post_image_path,
    validate_svg,
)
import fix_svg_forbidden_chars  # noqa: E402

# L25 modules (use absolute imports because lib has __init__.py)
from lib.svg_l25_generator import render_l25_cover_svg  # noqa: E402
from lib.post_l25_router import derive_l25_config  # noqa: E402


def collect_posts(post_glob: str, limit: Optional[int]) -> list[Path]:
    posts = sorted(POSTS_DIR.glob(post_glob))
    if limit is not None:
        posts = posts[:limit]
    return posts


def regen_one(
    post_path: Path,
    out_dir: Path,
    do_backup: bool,
) -> tuple[str, str, dict]:
    """Process one post; returns (status, reason, info)."""
    info: dict = {"post": post_path.name}
    fm = parse_front_matter(post_path)
    if not fm:
        return "FAIL", "no front matter", info
    svg_path = post_image_path(fm, post_path)
    if svg_path is None:
        # Fall back to convention even if file does not exist yet
        svg_path = out_dir / f"{post_path.stem}.svg"
    info["file"] = svg_path.name

    backup_path = BACKUP_DIR / svg_path.name
    if do_backup and svg_path.exists():
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(svg_path, backup_path)
        except OSError as exc:
            return "FAIL", f"backup failed: {exc}", info

    try:
        config = derive_l25_config(post_path)
        svg_xml = render_l25_cover_svg(**config)
        v = validate_svg(svg_xml)
        if not v.ok:
            # Restore backup if we had one
            if do_backup and backup_path.exists():
                shutil.copy2(backup_path, svg_path)
            info["text_count"] = v.text_count
            return "FAIL", v.reason, info
        info["text_count"] = v.text_count

        # Write new SVG
        svg_path.parent.mkdir(parents=True, exist_ok=True)
        svg_path.write_text(svg_xml, encoding="utf-8")

        # Sanitize forbidden chars defensively
        try:
            fix_svg_forbidden_chars.fix_svg_file(svg_path)
        except Exception:
            pass  # non-fatal

        # Re-parse final XML to ensure file is still well-formed
        try:
            final = svg_path.read_text(encoding="utf-8")
            ET.fromstring(final)
        except (OSError, ET.ParseError) as exc:
            if do_backup and backup_path.exists():
                shutil.copy2(backup_path, svg_path)
            return "FAIL", f"final parse: {exc}", info

        return "OK", "", info
    except Exception as exc:  # noqa: BLE001
        if do_backup and backup_path.exists():
            try:
                shutil.copy2(backup_path, svg_path)
            except OSError:
                pass
        return "FAIL", f"unexpected: {exc}", info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--posts", type=int, default=None,
                    help="process first N posts only")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--post-glob", default="2025-*.md")
    ap.add_argument("--out-dir", default=str(IMAGES_DIR))
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()

    posts = collect_posts(args.post_glob, args.posts)
    if not posts:
        print("No posts to process.")
        return 0

    out_dir = Path(args.out_dir)
    do_backup = not args.no_backup

    print(f"Discovered {len(posts)} posts")
    print(f"Output dir: {out_dir}")
    print(f"Backup:     {'on' if do_backup else 'off'}")

    if args.dry_run:
        for i, post in enumerate(posts, start=1):
            cfg = derive_l25_config(post)
            print(f"\n[{i}/{len(posts)}] {post.name}")
            print(json.dumps(cfg, ensure_ascii=False, indent=2)[:1200])
        return 0

    results: list[tuple[str, str, str, dict]] = []
    started = time.time()
    for i, post in enumerate(posts, start=1):
        status, reason, info = regen_one(post, out_dir, do_backup)
        results.append((post.name, status, reason, info))
        suffix_parts: list[str] = []
        if "text_count" in info:
            suffix_parts.append(f"text={info['text_count']}")
        if reason:
            suffix_parts.append(f"reason={reason[:80]}")
        suffix = " ".join(suffix_parts)
        target = info.get("file", "?")
        print(f"[{i}/{len(posts)}] {status}: {target}  {suffix}")

    elapsed = time.time() - started
    ok = sum(1 for _, s, _, _ in results if s == "OK")
    fail = sum(1 for _, s, _, _ in results if s == "FAIL")
    print()
    print(f"Done in {elapsed:.1f}s")
    print(f"  OK:   {ok}")
    print(f"  FAIL: {fail}")

    if fail:
        log = SCRIPTS_DIR / "regen_2025_svgs.failures"
        with log.open("w", encoding="utf-8") as fh:
            fh.write(f"Run at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for name, status, reason, info in results:
                if status == "FAIL":
                    fh.write(f"{name}\t{reason}\t{json.dumps(info)}\n")
        print(f"  failures logged: {log.relative_to(PROJECT_ROOT)}")

    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
