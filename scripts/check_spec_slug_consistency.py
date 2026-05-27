#!/usr/bin/env python3
"""Digest cover spec slug ↔ post image: field consistency gate.

For each _data/digest_covers/*.yml (excluding _archive_l20_superseded/):
  - Parse YAML → extract date and slug
  - Find matching post in _posts/{date}-*.md
  - Extract image: field from post front matter
  - Verify image: == /assets/images/{date}-{slug}.svg (case-sensitive)

Reports violations and exits non-zero if any found.

Usage:
    python3 scripts/check_spec_slug_consistency.py --staged    # only specs in git diff --cached
    python3 scripts/check_spec_slug_consistency.py --all       # all specs (default)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print(
        "[spec-slug] ERROR: PyYAML not installed. Run: pip install PyYAML",
        file=sys.stderr,
    )
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
DIGEST_COVERS_DIR = REPO / "_data" / "digest_covers"
POSTS_DIR = REPO / "_posts"
ARCHIVE_DIR = DIGEST_COVERS_DIR / "_archive_l20_superseded"

# Front-matter image field extractor (handles YAML front matter block).
_FRONT_MATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_IMAGE_RE = re.compile(r"^image:\s*(.+)$", re.MULTILINE)


# ---------------------------------------------------------------------------
# YAML spec parsing
# ---------------------------------------------------------------------------


def _parse_spec(spec_path: Path) -> tuple[Optional[str], Optional[str]]:
    """Return (date_str, slug) from a digest cover YAML spec.

    Returns (None, None) on parse failure or missing fields.
    """
    try:
        text = spec_path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
    except Exception as exc:
        print(
            f"[spec-slug] WARNING: could not parse {spec_path.name}: {exc}",
            file=sys.stderr,
        )
        return None, None

    if not isinstance(data, dict):
        return None, None

    date_val = data.get("date")
    slug_val = data.get("slug")

    if date_val is None or slug_val is None:
        return None, None

    # date may be a datetime.date object when parsed by PyYAML.
    date_str = str(date_val).strip()
    slug_str = str(slug_val).strip()

    return date_str, slug_str


# ---------------------------------------------------------------------------
# Post lookup
# ---------------------------------------------------------------------------


def _find_post(date_str: str, slug: str) -> Optional[Path]:
    """Find the post that matches this spec.

    Strategy:
    1. Look for exact case-sensitive match: _posts/{date}-{slug}.md
    2. If not found, look for any _posts/{date}-*.md (any case variant).
       Return the first match (there should only be one post per date/topic).
    3. Return None if no post found for this date at all.
    """
    exact = POSTS_DIR / f"{date_str}-{slug}.md"
    if exact.exists():
        return exact

    # Fallback: any post with this date prefix (macOS case-insensitive match)
    candidates = list(POSTS_DIR.glob(f"{date_str}-*.md"))
    if not candidates:
        return None

    # Try to find a candidate whose basename (without .md) ends with slug
    # in a case-insensitive manner — this identifies the "same" post.
    slug_lower = slug.lower()
    for candidate in candidates:
        stem = candidate.stem  # e.g. "2025-05-24-Amazon_Q_DeveloperAnd_..."
        # The part after the date prefix
        after_date = stem[len(date_str) + 1:]  # strip "YYYY-MM-DD-"
        if after_date.lower() == slug_lower:
            return candidate

    # If only one post exists for that date, return it as best-effort.
    if len(candidates) == 1:
        return candidates[0]

    return None


# ---------------------------------------------------------------------------
# Image field extraction
# ---------------------------------------------------------------------------


def _extract_image(post_path: Path) -> Optional[str]:
    """Extract the image: field value from a post's YAML front matter."""
    try:
        text = post_path.read_text(encoding="utf-8")
    except OSError:
        return None

    m = _FRONT_MATTER_RE.match(text)
    if not m:
        # Try multi-line front matter without strict newline after second ---
        # Some posts may have CRLF or extra whitespace.
        alt = re.match(r"^---\s*\n(.*?)---\s*", text, re.DOTALL)
        if not alt:
            return None
        front = alt.group(1)
    else:
        front = m.group(1)

    img_m = _IMAGE_RE.search(front)
    if not img_m:
        return None

    return img_m.group(1).strip()


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------


def _all_spec_paths() -> list[Path]:
    """Return all *.yml files under _data/digest_covers/, excluding archive subdir."""
    if not DIGEST_COVERS_DIR.exists():
        return []
    paths = []
    for p in sorted(DIGEST_COVERS_DIR.glob("*.yml")):
        # Exclude anything inside the archive directory (top-level only).
        if p.parent != DIGEST_COVERS_DIR:
            continue
        paths.append(p)
    return paths


def _staged_spec_paths() -> list[Path]:
    """Return staged _data/digest_covers/*.yml paths from the git index."""
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            cwd=str(REPO),
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths = []
    for line in out.splitlines():
        p = line.strip()
        # Match _data/digest_covers/*.yml (not in archive subdir)
        if re.match(r"^_data/digest_covers/[^/]+\.yml$", p):
            full = REPO / p
            if full.exists():
                paths.append(full)
    return sorted(paths)


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------


def _check_spec(spec_path: Path) -> list[str]:
    """Check one spec file. Return list of violation strings (empty = clean)."""
    violations = []

    date_str, slug = _parse_spec(spec_path)
    if date_str is None or slug is None:
        # Missing date or slug — can't check, skip with warning
        print(
            f"[spec-slug] WARNING: {spec_path.name} missing date or slug field, skipping.",
            file=sys.stderr,
        )
        return violations

    expected_image = f"/assets/images/{date_str}-{slug}.svg"
    post = _find_post(date_str, slug)

    if post is None:
        rel_spec = spec_path.relative_to(REPO) if spec_path.is_relative_to(REPO) else spec_path
        violations.append(
            f"orphan-spec  spec={rel_spec}  no matching post found for date={date_str}"
        )
        return violations

    actual_image = _extract_image(post)
    rel_post = post.relative_to(REPO) if post.is_relative_to(REPO) else post

    if actual_image is None:
        rel_spec = spec_path.relative_to(REPO) if spec_path.is_relative_to(REPO) else spec_path
        violations.append(
            f"missing-image  spec={rel_spec.name}  post={rel_post}  no image: field in front matter"
        )
        return violations

    if actual_image != expected_image:
        rel_spec = spec_path.relative_to(REPO) if spec_path.is_relative_to(REPO) else spec_path
        violations.append(
            f"slug-vs-image-mismatch  spec={rel_spec.name}"
            f"  expects={expected_image}"
            f"  actual={actual_image}"
        )

    return violations


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that each digest cover spec slug matches the post's image: field "
            "(case-sensitive). Exits 1 on any violation."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Only check specs in git staging area (_data/digest_covers/*.yml).",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Check all specs under _data/digest_covers/ (default).",
    )
    args = parser.parse_args()

    if args.staged:
        specs = _staged_spec_paths()
    else:
        # Default: --all
        specs = _all_spec_paths()

    if not specs:
        print("[spec-slug] No spec files to check.")
        sys.exit(0)

    all_violations: list[str] = []
    for spec in specs:
        all_violations.extend(_check_spec(spec))

    if all_violations:
        for v in all_violations:
            print(f"[spec-slug] VIOLATION: {v}", file=sys.stderr)
        print(
            f"\n[spec-slug] FAIL — {len(all_violations)} violation(s) found. "
            f"Spec slug and post image: field must match case-sensitively.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[spec-slug] OK — {len(specs)} spec(s) checked, 0 violations.")
    sys.exit(0)


if __name__ == "__main__":
    main()
