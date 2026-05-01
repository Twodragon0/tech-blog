#!/usr/bin/env python3
"""Font drift gate helper.

Reads a comma-separated list of changed files and exits 1 if any
assets/fonts/*.woff2 file changed without a corresponding change to
the generator script or the syllable corpus.

Usage:
    python3 scripts/dev/check_font_drift.py \\
        --changed-files 'assets/fonts/noto-sans-kr-400-tier1.woff2'
    # exit 1 — fonts changed without generator/corpus update

    python3 scripts/dev/check_font_drift.py \\
        --changed-files 'assets/fonts/noto-sans-kr-400-tier1.woff2,scripts/build/generate_noto_2tier_subset.py'
    # exit 0

Override: when the CI label "font-drift-allowed" is present the caller
should skip running this script entirely (handled in the workflow).
"""

import argparse
import re
import sys


WOFF2_PATTERN = re.compile(r"^assets/fonts/.*\.woff2$")

# Source-of-truth files that must accompany any woff2 change
GENERATOR_FILES = frozenset(
    [
        "scripts/build/generate_noto_2tier_subset.py",
        "scripts/build/noto_subset_top1k.txt",
    ]
)

FAILURE_MESSAGE = """\
## Font Drift Gate Failed

`assets/fonts/*.woff2` changed without a corresponding update to the
generator or the syllable corpus.

**Allowed source-of-truth files (at least one must also change):**
- `scripts/build/generate_noto_2tier_subset.py`
- `scripts/build/noto_subset_top1k.txt`

**Why this gate exists:**
The woff2 files are committed binaries. Any accidental regeneration
(e.g. a stale stamp file or a local toolchain upgrade) would silently
bloat the git history without a meaningful change to the subsetting
logic. This gate ensures every woff2 commit is intentional and
traceable to a source change.

**If this change is intentional (e.g. upstream Noto bump):**
1. Also commit the updated generator/corpus file, OR
2. Ask a maintainer to apply the `font-drift-allowed` label to this PR.

See `docs/optimization/WOFF2_LFS_DECISION.md` for background and
`docs/optimization/NOTO_SANS_SELF_HOST_RUNBOOK.md` for regeneration
instructions.
"""


def check_font_drift(changed_files: list[str]) -> bool:
    """Return True if the diff is clean (gate passes), False if it fails."""
    woff2_changed = [f for f in changed_files if WOFF2_PATTERN.match(f)]
    if not woff2_changed:
        return True  # no woff2 in diff — nothing to enforce

    generator_changed = bool(GENERATOR_FILES & set(changed_files))
    return generator_changed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that woff2 changes are accompanied by generator/corpus changes."
    )
    parser.add_argument(
        "--changed-files",
        required=True,
        help="Comma-separated list of changed file paths.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    changed = [f.strip() for f in args.changed_files.split(",") if f.strip()]
    if check_font_drift(changed):
        return 0
    print(FAILURE_MESSAGE, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
