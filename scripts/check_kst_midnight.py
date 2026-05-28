#!/usr/bin/env python3
"""KST-midnight URL-safety gate for Jekyll posts.

The site is pinned to ``timezone: UTC`` in ``_config.yml``.  Permalinks use
``/posts/:year/:month/:day/:title/``, where the day is derived from the post
``date:`` field **converted to UTC**.  A post with::

    date: 2025-05-30 00:30:00 +0900

stores KST 00:30 which is UTC 2025-05-29 15:30 — a **different calendar day**.
The built URL therefore becomes ``/2025/05/29/…`` while the source filename
starts with ``2025-05-30-``, so external links to
``/posts/2025/05/30/…`` return 404 unless a ``redirect_from:`` entry covers
that filename-date path.

This script flags any post where:

1. ``date:`` has a ``+0900`` (KST) offset, **and**
2. The hour component is between 00 and 08 (inclusive), **and**
3. The ``redirect_from:`` list does **not** include
   ``/posts/{YYYY}/{MM}/{DD}/{slug}/`` using the **filename** date
   (i.e., the date prefix of the ``.md`` basename).

Usage:
    python3 scripts/check_kst_midnight.py --staged   # only git-cached _posts/*.md
    python3 scripts/check_kst_midnight.py --all       # every _posts/*.md (default)
    python3 scripts/check_kst_midnight.py path/a.md path/b.md
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
        "[kst-midnight] ERROR: PyYAML not installed. Run: pip install PyYAML",
        file=sys.stderr,
    )
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO / "_posts"

# Matches front-matter block: lines between the first and second '---'
_FRONT_MATTER_RE = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)", re.DOTALL)

# Matches 'date: YYYY-MM-DD HH:MM:SS +ZZZZ' (strict ISO-8601 with offset).
# Groups: (year, month, day, hour, minute, second, sign, off_h, off_m)
_DATE_LINE_RE = re.compile(
    r"^date:\s*"
    r"(\d{4})-(\d{2})-(\d{2})"          # YYYY-MM-DD
    r"[ T]"
    r"(\d{2}):(\d{2}):(\d{2})"          # HH:MM:SS
    r"\s*([+-])(\d{2}):?(\d{2})"        # ±HH:MM offset
    r"\s*$",
    re.MULTILINE,
)

# Filename basename pattern: YYYY-MM-DD-slug.md
_FILENAME_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")


# ---------------------------------------------------------------------------
# Front-matter parsing helpers
# ---------------------------------------------------------------------------


def _parse_front_matter(text: str) -> Optional[dict]:
    """Return parsed YAML front matter dict, or None on failure."""
    m = _FRONT_MATTER_RE.match(text)
    if not m:
        return None
    try:
        data = yaml.safe_load(m.group(1))
        if isinstance(data, dict):
            return data
    except yaml.YAMLError:
        pass
    return None


def _extract_date_raw(text: str) -> Optional[re.Match]:
    """Return the first regex match for a 'date:' line in the front matter block."""
    fm_m = _FRONT_MATTER_RE.match(text)
    if not fm_m:
        return None
    return _DATE_LINE_RE.search(fm_m.group(1))


def _date_line_number(text: str, date_match_span: tuple[int, int]) -> int:
    """Return the 1-based line number for a character offset into *text*.

    ``date_match_span`` is the (start, end) span from a regex match on
    the full *text*.
    """
    return text[: date_match_span[0]].count("\n") + 1


# ---------------------------------------------------------------------------
# Core check per file
# ---------------------------------------------------------------------------


def _filename_parts(path: Path) -> Optional[tuple[str, str, str, str]]:
    """Return (YYYY, MM, DD, slug) from the post filename, or None."""
    m = _FILENAME_DATE_RE.match(path.stem)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3), m.group(4)


def _is_kst_at_risk(
    hour: int, sign: str, off_h: int, off_m: int
) -> bool:
    """Return True when the timestamp is KST (UTC+0900) and hour < 9.

    We only flag ``+0900`` offsets because those are explicitly KST and the
    site's author convention.  UTC (``+0000``) timestamps are already in UTC
    so no day shift occurs.  Other positive offsets are treated conservatively:
    if offset == +09:00 AND hour < 9, the UTC day is at most one day earlier
    than the KST day.
    """
    if sign != "+" or off_h != 9 or off_m != 0:
        return False
    return hour < 9


def _redirect_from_list(front_matter: dict) -> list[str]:
    """Extract redirect_from as a flat list of strings."""
    raw = front_matter.get("redirect_from")
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item).strip() for item in raw if item]
    if isinstance(raw, str):
        return [raw.strip()]
    return []


def _expected_redirect(yyyy: str, mm: str, dd: str, slug: str) -> str:
    """Return the redirect URL corresponding to the filename date.

    Example: ``/posts/2025/05/30/Kubernetes_Minikube_and_K9s_Practice_Guide/``
    """
    return f"/posts/{yyyy}/{mm}/{dd}/{slug}/"


def check_file(path: Path) -> list[tuple[int, str]]:
    """Return list of (line_number, message) violations for *path*.

    An empty list means the file is clean.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    parts = _filename_parts(path)
    if parts is None:
        # Not a dated post filename — skip.
        return []

    yyyy, mm, dd, slug = parts

    # Locate the date: line using regex (handles cases where PyYAML parses
    # datetime objects and loses the original offset string).
    date_re_match = _extract_date_raw(text)
    if date_re_match is None:
        return []

    hour = int(date_re_match.group(4))
    sign = date_re_match.group(7)
    off_h = int(date_re_match.group(8))
    off_m = int(date_re_match.group(9))

    if not _is_kst_at_risk(hour, sign, off_h, off_m):
        return []

    # At-risk: KST 00:00-08:59 → need redirect entry for filename-date URL.
    expected = _expected_redirect(yyyy, mm, dd, slug)

    front_matter = _parse_front_matter(text)
    if front_matter is None:
        # Can't parse front matter — report the date line as context.
        line_no = _date_line_number(text, date_re_match.span())
        return [
            (
                line_no,
                f"KST midnight post (HH={hour:02d}) — could not parse front matter "
                f"to check redirect_from; expected {expected}",
            )
        ]

    redirects = _redirect_from_list(front_matter)

    if expected in redirects:
        return []  # Already protected.

    line_no = _date_line_number(text, date_re_match.span())
    return [
        (
            line_no,
            f"missing redirect_from {expected}  "
            f"(KST {hour:02d}:{date_re_match.group(5)}:{date_re_match.group(6)} "
            f"→ UTC previous day; filename-date URL would 404)",
        )
    ]


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------


def _all_post_paths() -> list[Path]:
    """Return all *.md files under _posts/."""
    return sorted(POSTS_DIR.glob("*.md"))


def _staged_post_paths() -> list[Path]:
    """Return staged _posts/*.md paths from the git index."""
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
        if re.match(r"^_posts/[^/]+\.md$", p):
            full = REPO / p
            if full.exists():
                paths.append(full)
    return sorted(paths)


def _explicit_paths(args_paths: list[str]) -> list[Path]:
    """Resolve explicit file paths (absolute or relative to cwd / repo)."""
    paths = []
    for a in args_paths:
        p = Path(a)
        if not p.is_absolute():
            cwd_p = Path.cwd() / p
            p = cwd_p if cwd_p.exists() else REPO / a
        if p.exists():
            paths.append(p)
        else:
            print(f"[kst-midnight] WARNING: file not found: {a}", file=sys.stderr)
    return paths


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Flag _posts/*.md with KST 00:00-08:59 (+0900) timestamps that lack "
            "a redirect_from entry for the filename-date URL. "
            "Exits 1 if any violations found."
        )
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        help="Only check files in git staging area (_posts/*.md).",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        help="Check every _posts/*.md (default when no paths given).",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Explicit post file paths to check.",
    )
    args = parser.parse_args()

    if args.staged:
        files = _staged_post_paths()
    elif args.paths:
        files = _explicit_paths(args.paths)
    else:
        # Default: behave like --all.
        files = _all_post_paths()

    if not files:
        print("[kst-midnight] No post files to check.")
        sys.exit(0)

    total_violations = 0
    checked = 0
    for path in files:
        violations = check_file(path)
        if violations:
            rel = path.relative_to(REPO) if path.is_relative_to(REPO) else path
            for line_no, msg in violations:
                print(f"{rel}:{line_no}: {msg}", file=sys.stderr)
            total_violations += len(violations)
        checked += 1

    if total_violations:
        print(
            f"\n[kst-midnight] FAIL — {total_violations} post(s) with KST-midnight "
            f"timestamp missing filename-date redirect_from entry.\n"
            f"  Add to front matter:\n"
            f"    redirect_from:\n"
            f"      - /posts/{{YYYY}}/{{MM}}/{{DD}}/{{slug}}/   # filename date\n"
            f"  Or change 'date:' to HH >= 09:00:00 +0900 so the UTC day matches.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"[kst-midnight] OK — {checked} post(s) checked, 0 violations.")
    sys.exit(0)


if __name__ == "__main__":
    main()
