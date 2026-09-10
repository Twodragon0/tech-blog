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

# Keys exempt from the GROWTH ratchet — never from the absolute cap.
#
# The ratchet's message is "Trim it, or move the content into the body", which is
# the right advice for prose and impossible advice for a structural key: Jekyll
# exposes per-post metadata only through front matter, so there is no body to
# move it to. Adding `superseded_by` to the 30 consolidated April 2026 posts
# tripped this gate 30 times at +67 chars each on 2026-09-10 — a change the gate
# was never aimed at.
#
# Each entry must name what reads it, so the list cannot quietly become a
# dumping ground. Growth is measured with these lines removed; `front_matter_len`
# (and therefore --max-chars) still counts every character, so the exemption
# narrows the ratchet without opening a hole in the ceiling.
#
#   superseded_by — the rollup URL a vercel.json 301 sends this post to. Read by
#     sitemap.xml, llms.txt, llms-full.txt and _plugins/lazy_data_generator.rb.
RATCHET_EXEMPT_KEYS = ("superseded_by",)

# Scalar keys only. Line-based removal, so a multi-line YAML value under an
# exempt key would leak its continuation lines into the measurement — keep this
# list to one-line values (a URL, a flag), which is all it is for.
_EXEMPT_KEY_RE = re.compile(
    r"^(?:%s):" % "|".join(re.escape(k) for k in RATCHET_EXEMPT_KEYS)
)


def front_matter_len(text: str) -> int | None:
    """Length of the YAML front matter block, or None when there is none.

    Counts everything. This is what the absolute cap is measured against.
    """
    match = _FRONT_MATTER_RE.match(text)
    return len(match.group(1)) if match else None


def ratchet_len(text: str) -> int | None:
    """Front-matter length with :data:`RATCHET_EXEMPT_KEYS` lines removed.

    This is what the growth comparison uses, so adding a structural key is not
    growth while adding prose still is.
    """
    match = _FRONT_MATTER_RE.match(text)
    if match is None:
        return None
    # Dropped line-wise, not by regex substitution: removing the line must also
    # remove its separator, or the exempt key still costs one character and the
    # ratchet trips by +1.
    kept = [ln for ln in match.group(1).split("\n") if not _EXEMPT_KEY_RE.match(ln)]
    return len("\n".join(kept))


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
    """Ratchet-measured front-matter length of `rel_path` at `base`.

    None when the file did not exist there. Uses :func:`ratchet_len`, not
    :func:`front_matter_len`, so both sides of the comparison exclude the same
    exempt keys — otherwise REMOVING one would read as shrinkage and adding one
    as growth.
    """
    code, out = _git(["show", f"{base}:{rel_path}"])
    if code != 0:
        return None
    return ratchet_len(out)


def check(
    base: str | None, paths: list[str], max_chars: int
) -> tuple[list[str], list[str]]:
    """Return (violations, notes)."""
    violations: list[str] = []
    notes: list[str] = []

    for rel in paths:
        path = REPO_ROOT / rel
        if not path.is_file():
            notes.append(f"{rel}: deleted or moved — skipped")
            continue
        raw = path.read_text(encoding="utf-8", errors="replace")
        current = front_matter_len(raw)
        if current is None:
            violations.append(f"{rel}: no front matter block found")
            continue

        # The cap counts every character, exempt keys included.
        if current > max_chars:
            violations.append(
                f"{rel}: front matter {current} chars exceeds the {max_chars}-char cap"
            )
            continue

        if base is None:
            continue

        # The ratchet does not. See RATCHET_EXEMPT_KEYS.
        current = ratchet_len(raw)
        previous = baseline_len(base, rel)
        if previous is None:
            notes.append(
                f"{rel}: new post ({current} chars, under the {max_chars} cap)"
            )
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
    group.add_argument(
        "--changed", metavar="BASE", help="Ratchet changed posts against BASE"
    )
    group.add_argument(
        "--all", action="store_true", help="Cap check over every post (no ratchet)"
    )
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
        print(
            f"\n{len(violations)} front-matter violation(s) across {len(paths)} post(s)."
        )
        return 1

    print(
        f"Front matter OK across {len(paths)} post(s) (cap {args.max_chars}, no growth)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
