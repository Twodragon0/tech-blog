#!/usr/bin/env python3
"""Check that every post with an image: field has at least one usable
raster variant in the fallback chain.

Fallback chain (mirrors post-card.html Liquid logic and
_plugins/lazy_data_generator.rb#compute_image_flags):
  For a post whose image: field resolves to base stem <S>:
    Primary   : <S>_og.png  (required — blocks push if missing)
    Modern    : <S>_og.avif, <S>_og.webp  (warn if missing)
    Card      : <S>_card.avif, <S>_card.webp  (warn if missing)
    Fallback  : the literal image: value itself (.svg / .png)

Exit codes:
  0  all posts OK (primary variant present or image: is already a raster)
  1  one or more posts missing their primary variant

Usage::

    python3 scripts/check_post_image_variants.py
    python3 scripts/check_post_image_variants.py --posts-dir _posts --warn-only
    python3 scripts/check_post_image_variants.py --changed-only <sha1> <sha2>

Environment:
    SKIP_VARIANT_CHECK=1   bypass all checks (emergency push override)
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

try:
    import yaml
except ModuleNotFoundError:
    print(
        "Missing dependency: PyYAML. Run `pip install PyYAML` and retry.",
        file=sys.stderr,
    )
    raise SystemExit(2)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = PROJECT_ROOT / "_posts"
IMAGES_DIR = PROJECT_ROOT / "assets" / "images"

# Strip these suffixes to recover the base stem used for variant naming.
# Order matters: longest suffix first.
_STEM_STRIP_RE = re.compile(r"(_og\.png|\.png|\.svg)\Z", re.IGNORECASE)


class PostResult(NamedTuple):
    post: Path
    image_field: str
    missing_primary: list[str]   # blocks push
    missing_secondary: list[str]  # warns only


def _extract_image_field(post_path: Path) -> str | None:
    """Return the raw ``image:`` value from a post's front matter, or None."""
    try:
        content = post_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return None
    return str(fm["image"]).strip() if "image" in fm else None


def _strip_query(image_field: str) -> str:
    """Drop ``?query`` and ``#fragment`` from an image: URL so cache-bust
    suffixes like ``?v=20260518`` don't break filesystem lookups.
    """
    return image_field.split("?", 1)[0].split("#", 1)[0]


def _base_stem(image_field: str) -> str:
    """Strip /assets/images/ prefix and trailing suffix to get the bare stem.

    Example:
        "/assets/images/2026-05-06-Foo_og.png"          -> "2026-05-06-Foo"
        "/assets/images/2026-05-06-Foo.svg"             -> "2026-05-06-Foo"
        "/assets/images/2026-05-06-Foo.svg?v=20260518"  -> "2026-05-06-Foo"
    """
    name = Path(_strip_query(image_field).lstrip("/")).name
    return _STEM_STRIP_RE.sub("", name)


def check_post(post_path: Path) -> PostResult | None:
    """Return a PostResult if the post has an image: field, else None."""
    image_field = _extract_image_field(post_path)
    if not image_field:
        return None

    stem = _base_stem(image_field)

    # The literal image: value may itself exist (e.g. an SVG or a plain PNG).
    # If the literal file is present, the primary requirement is satisfied.
    literal_path = IMAGES_DIR / Path(_strip_query(image_field).lstrip("/")).name
    literal_exists = literal_path.exists()

    og_png = IMAGES_DIR / f"{stem}_og.png"
    og_avif = IMAGES_DIR / f"{stem}_og.avif"
    og_webp = IMAGES_DIR / f"{stem}_og.webp"
    card_avif = IMAGES_DIR / f"{stem}_card.avif"
    card_webp = IMAGES_DIR / f"{stem}_card.webp"

    # Primary check: _og.png must exist (or the literal image: file must exist).
    missing_primary: list[str] = []
    if not og_png.exists() and not literal_exists:
        missing_primary.append(str(og_png.relative_to(PROJECT_ROOT)))

    # Secondary (warn-only): modern/card variants.
    missing_secondary: list[str] = []
    for p, label in [
        (og_avif, "_og.avif"),
        (og_webp, "_og.webp"),
        (card_avif, "_card.avif"),
        (card_webp, "_card.webp"),
    ]:
        if not p.exists():
            missing_secondary.append(str(p.relative_to(PROJECT_ROOT)))

    return PostResult(
        post=post_path,
        image_field=image_field,
        missing_primary=missing_primary,
        missing_secondary=missing_secondary,
    )


def _posts_in_push_range(remote_ref: str, local_ref: str) -> list[Path]:
    """Return the subset of _posts/*.md files touched in the push range."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", remote_ref, local_ref],
            capture_output=True,
            text=True,
            check=True,
            cwd=str(PROJECT_ROOT),
        )
        touched = {Path(p.strip()) for p in result.stdout.splitlines() if p.strip()}
        return [
            PROJECT_ROOT / p
            for p in touched
            if p.parts[0] == "_posts" and p.suffix == ".md"
        ]
    except subprocess.CalledProcessError:
        return []


def run_check(
    posts: list[Path],
    warn_only: bool = False,
) -> int:
    """Check all given posts. Return 0 (pass) or 1 (fail)."""
    errors: list[PostResult] = []
    warnings: list[PostResult] = []

    for post in posts:
        result = check_post(post)
        if result is None:
            continue
        if result.missing_primary:
            errors.append(result)
        elif result.missing_secondary:
            warnings.append(result)

    if warnings:
        print(
            f"\n[variant-check] WARNING: {len(warnings)} post(s) missing optional variants:"
        )
        for r in warnings:
            print(f"  {r.post.name}  (image: {r.image_field})")
            for p in r.missing_secondary:
                print(f"    missing: {p}")

    if errors:
        print(
            f"\n[variant-check] FAIL: {len(errors)} post(s) missing required raster variant:",
            file=sys.stderr,
        )
        for r in errors:
            print(
                f"  {r.post.name}  (image: {r.image_field})",
                file=sys.stderr,
            )
            for p in r.missing_primary:
                print(f"    missing PRIMARY: {p}", file=sys.stderr)
        print(
            "\n  Fix: run `python3 scripts/build/rasterize_svg_covers.py` to generate _og.png,\n"
            "       then `python3 scripts/build/backfill_og_modern_variants.py` for avif/webp.\n"
            "  Emergency bypass: set SKIP_VARIANT_CHECK=1",
            file=sys.stderr,
        )
        if warn_only:
            print("[variant-check] --warn-only: continuing despite failures.", file=sys.stderr)
            return 0
        return 1

    total = len([p for p in posts if _extract_image_field(p)])
    print(f"[variant-check] OK: {total} post(s) checked, all have a primary raster variant.")
    return 0


def main(argv: list[str] | None = None) -> int:
    if os.environ.get("SKIP_VARIANT_CHECK", "").strip() in {"1", "true", "yes"}:
        print("[variant-check] SKIP_VARIANT_CHECK=1 — bypassing check.")
        return 0

    parser = argparse.ArgumentParser(
        description="Verify raster variant fallback chain for all posts with image: fields.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--posts-dir",
        type=Path,
        default=POSTS_DIR,
        help="Path to _posts/ directory (default: auto-detected from repo root)",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Emit warnings but always exit 0 (useful in CI where push guard is informational)",
    )
    parser.add_argument(
        "--changed-only",
        nargs=2,
        metavar=("REMOTE_REF", "LOCAL_REF"),
        help="Only check posts touched in git diff REMOTE_REF..LOCAL_REF (pre-push mode)",
    )
    args = parser.parse_args(argv)

    posts_dir: Path = args.posts_dir
    if not posts_dir.is_dir():
        print(f"ERROR: posts dir not found: {posts_dir}", file=sys.stderr)
        return 1

    if args.changed_only:
        remote_ref, local_ref = args.changed_only
        posts = _posts_in_push_range(remote_ref, local_ref)
        if not posts:
            print("[variant-check] No _posts/*.md in push range — skipping.")
            return 0
        print(f"[variant-check] Checking {len(posts)} post(s) in push range...")
    else:
        posts = sorted(posts_dir.glob("*.md"))
        print(f"[variant-check] Checking {len(posts)} post(s) in {posts_dir}...")

    return run_check(posts, warn_only=args.warn_only)


if __name__ == "__main__":
    raise SystemExit(main())
