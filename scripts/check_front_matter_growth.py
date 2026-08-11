#!/usr/bin/env python3
"""Front-matter size gate — a growth ratchet, not an absolute limit.

Why this replaced the old check
-------------------------------
`jekyll.yml` used to run an inline Python snippet that warned when a post's front
matter exceeded 1,000 characters. Measured 2026-08-10: **261 of 261 posts exceed
it**, and the snippet could not exit non-zero anyway (the step was additionally
`continue-on-error: true`). A threshold every single file violates carries no
information — it prints a warning on every post-touching PR, which is how people
learn to scroll past warnings.

So the absolute number is replaced by two claims that are actually true today:

1. **Ratchet** — a post that already exists must not grow its front matter. The
   corpus is where it is; what matters is that it stops getting worse. This is the
   same shape as `check_digest_structure.py --ratchet` and the cover honesty
   baseline: legacy debt is grandfathered, new debt fails.
2. **Absolute cap** — nothing, new or old, may exceed `--max-chars` (default 3000).
   Measured maximum at the time of writing is 2,749, so the cap is a ceiling on
   unbounded growth rather than a retroactive judgement. New posts have no baseline
   to ratchet against, and this is what bounds them.

Usage
-----
    # PR mode: compare every changed post against its version in <base>
    python3 scripts/check_front_matter_growth.py --changed origin/main

    # Explicit files (still ratcheted against <base>)
    python3 scripts/check_front_matter_growth.py --changed origin/main _posts/a.md

    # Corpus-wide cap check only (no baseline available)
    python3 scripts/check_front_matter_growth.py --all

Exit codes: 0 clean, 1 violation, 2 usage/environment error.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = REPO_ROOT / "_posts"

# Measured max across 261 posts on 2026-08-10 was 2,749 chars. 3,000 is a ceiling on
# further growth, deliberately not a retroactive verdict on the corpus.
DEFAULT_MAX_CHARS = 3000

_FRONT_MATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def front_matter_len(text: str) -> int | None:
    """Length of the YAML front matter block, or None when there is none."""
    match = _FRONT_MATTER_RE.match(text)
    return len(match.group(1)) if match else None


def _git(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    return proc.returncode, proc.stdout


def changed_posts(base: str) -> list[str]:
    """Repo-relative paths of _posts/*.md that differ from `base`.

    Raises RuntimeError when the diff cannot be computed. An unresolvable base must
    not silently look like "nothing changed" — that is exactly how the old digest
    gate reported "No Digest posts changed, skipping" on a broken checkout.
    """
    code, out = _git(["diff", "--name-only", f"{base}...HEAD", "--", "_posts/*.md"])
    if code != 0:
        raise RuntimeError(
            f"git diff against {base!r} failed (exit {code}). Refusing to report "
            "'no changes' on an unresolvable base — deepen the checkout or fix the ref."
        )
    return [line.strip() for line in out.splitlines() if line.strip()]


def baseline_len(base: str, rel_path: str) -> int | None:
    """Front-matter length of `rel_path` at `base`, or None when it did not exist."""
    code, out = _git(["show", f"{base}:{rel_path}"])
    if code != 0:
        return None
    return front_matter_len(out)


def check(base: str | None, paths: list[str], max_chars: int) -> tuple[list[str], list[str]]:
    """Return (violations, notes)."""
    violations: list[str] = []
    notes: list[str] = []

    for rel in paths:
        path = REPO_ROOT / rel
        if not path.is_file():
            notes.append(f"{rel}: deleted or moved — skipped")
            continue
        current = front_matter_len(path.read_text(encoding="utf-8", errors="replace"))
        if current is None:
            violations.append(f"{rel}: no front matter block found")
            continue

        if current > max_chars:
            violations.append(
                f"{rel}: front matter {current} chars exceeds the {max_chars}-char cap"
            )
            continue

        if base is None:
            continue

        previous = baseline_len(base, rel)
        if previous is None:
            notes.append(f"{rel}: new post ({current} chars, under the {max_chars} cap)")
            continue
        if current > previous:
            violations.append(
                f"{rel}: front matter grew {previous} -> {current} chars "
                f"(+{current - previous}). Trim it, or move the content into the body."
            )
        elif current < previous:
            notes.append(f"{rel}: front matter shrank {previous} -> {current} chars")

    return violations, notes


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--changed", metavar="BASE", help="Ratchet changed posts against BASE")
    group.add_argument("--all", action="store_true", help="Cap check over every post (no ratchet)")
    parser.add_argument("files", nargs="*", help="Optional explicit post paths")
    parser.add_argument(
        "--max-chars",
        type=int,
        default=DEFAULT_MAX_CHARS,
        help=f"Absolute front-matter ceiling (default: {DEFAULT_MAX_CHARS})",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.all:
        base = None
        paths = sorted(str(p.relative_to(REPO_ROOT)) for p in POSTS_DIR.glob("*.md"))
    else:
        base = args.changed
        if args.files:
            paths = [str(Path(f)) for f in args.files]
        else:
            try:
                paths = changed_posts(base)
            except RuntimeError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 2

    if not paths:
        print("No posts to check.")
        return 0

    violations, notes = check(base, paths, args.max_chars)

    for note in notes:
        print(f"  note: {note}")
    if violations:
        print()
        for violation in violations:
            print(f"::error::front matter: {violation}")
        print(f"\n{len(violations)} front-matter violation(s) across {len(paths)} post(s).")
        return 1

    print(f"Front matter OK across {len(paths)} post(s) (cap {args.max_chars}, no growth).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
