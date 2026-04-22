#!/usr/bin/env python3
"""check_filename_entities.py - Pre-commit guard against HTML entity residues in filenames.

Detects double-encoded HTML entity artifacts in:
  - Filenames under _posts/ and assets/images/
  - frontmatter `image:` field values in markdown posts

Patterns detected:
  - amp[a-z]+   e.g. ampamp, amplsquo, amprsquo, ampquot, ampldquo, amprdquo,
                     amphellip, ampndash, ampmdash, ampapos, ampgt, amplt
  - &amp;        literal double-encoded ampersand
  - &#NNN;       numeric character references
  - &name;       named character references

Usage:
    python3 scripts/check_filename_entities.py --staged   # check git-staged files (default)
    python3 scripts/check_filename_entities.py --all      # check all _posts/ + assets/images/

Exit codes:
    0  no violations
    1  violations found (or argument error)
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

# Detect HTML entity residues in filenames.
#
# Strategy: match "amp" followed by a known entity suffix.
# English words like "example", "campaign", "champion", "dampness" don't
# contain entity suffixes (lsquo, rsquo, quot, hellip, ndash, mdash, amp…).
# The short suffixes "lt", "gt", "apos" could appear mid-word so we guard
# those with a negative lookbehind (?<![a-zA-Z]) applied only to the short
# variants. Long unique suffixes need no lookbehind.
#
# Positive examples:  ampamp  amplsquo  amprsquo  ampquot  amphellip
#                     titleampampmore  fileamplsquoname  range-ampndash-value
# Negative examples:  example  campaign  dampness  champion  itsampaposfile

# Long suffixes — unique enough to not appear after mid-word "amp" in English
_LONG_SUFFIXES = (
    "amp|quot"
    "|lsquo|rsquo|ldquo|rdquo"
    "|hellip|ndash|mdash|laquo|raquo"
    "|copy|reg|trade|deg|plusmn|times|divide"
    "|nbsp|ensp|emsp|thinsp"
)
# Short/common suffixes that could appear after letters in English words
# (apos: "its" → "itsamp" + "apos"; lt/gt: rare but possible)
# Guard these with a negative lookbehind (?<![a-zA-Z])
_SHORT_SUFFIXES = "lt|gt|apos"

_RE_AMP_WORD = re.compile(
    rf"amp(?:{_LONG_SUFFIXES})|(?<![a-zA-Z])amp(?:{_SHORT_SUFFIXES})",
    re.IGNORECASE,
)

# Matches literal HTML entities in a filename/path string
_RE_LITERAL_ENTITY = re.compile(
    r"&amp;"          # double-encoded &
    r"|&#\d+;?"       # numeric entity (semicolon optional due to stripping)
    r"|&[a-zA-Z]+;",  # named entity
    re.IGNORECASE,
)

# Combined check for a single string
_RE_ANY_ENTITY = re.compile(
    rf"amp(?:{_LONG_SUFFIXES})"           # long entity suffix — no lookbehind needed
    rf"|(?<![a-zA-Z])amp(?:{_SHORT_SUFFIXES})"  # short suffix — guard with lookbehind
    r"|&amp;"                              # literal &amp;
    r"|&#\d+;?"                            # numeric entity
    r"|&[a-zA-Z]+;",                      # named entity
    re.IGNORECASE,
)

# Directories scanned in --all mode
_ALL_ROOTS = ("_posts", "assets/images")

# Frontmatter image field pattern
_RE_FRONTMATTER_IMAGE = re.compile(r"^image:\s*(.+)$", re.MULTILINE)

# ---------------------------------------------------------------------------
# Whitelist
# ---------------------------------------------------------------------------

_WHITELIST_FILE = Path(__file__).parent / ".filename_entity_whitelist"


def _load_whitelist() -> frozenset[str]:
    """Load whitelisted filenames (basenames or full paths, one per line)."""
    if not _WHITELIST_FILE.exists():
        return frozenset()
    lines = _WHITELIST_FILE.read_text(encoding="utf-8").splitlines()
    return frozenset(
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    )


# ---------------------------------------------------------------------------
# Detection helpers
# ---------------------------------------------------------------------------

def has_entity_residue(name: str) -> bool:
    """Return True if *name* contains any HTML entity residue pattern."""
    return bool(_RE_ANY_ENTITY.search(name))


def suggest_clean_name(name: str) -> str:
    """Return a suggested clean version of *name* with entity residues removed.

    This is a best-effort suggestion only — operators should verify manually.
    """
    clean = _RE_AMP_WORD.sub("", name)
    clean = _RE_LITERAL_ENTITY.sub("", clean)
    # Collapse double hyphens/underscores that may result from removal
    clean = re.sub(r"-{2,}", "-", clean)
    clean = re.sub(r"_{2,}", "_", clean)
    clean = clean.strip("-_")
    return clean


# ---------------------------------------------------------------------------
# Frontmatter image field scanner
# ---------------------------------------------------------------------------

def check_frontmatter_image(path: Path) -> str | None:
    """Return the image field value if it contains entity residues, else None."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None

    # Only scan the frontmatter block (between first pair of ---)
    lines = text.splitlines()
    in_fm = False
    fm_lines: list[str] = []
    for line in lines:
        if line.strip() == "---":
            if not in_fm:
                in_fm = True
                continue
            else:
                break  # end of frontmatter
        if in_fm:
            fm_lines.append(line)

    fm_text = "\n".join(fm_lines)
    m = _RE_FRONTMATTER_IMAGE.search(fm_text)
    if m:
        value = m.group(1).strip().strip('"').strip("'")
        if has_entity_residue(value):
            return value
    return None


# ---------------------------------------------------------------------------
# File collection
# ---------------------------------------------------------------------------

def _staged_files() -> list[Path]:
    """Return list of staged files (added/copied/modified/renamed)."""
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [Path(p) for p in result.stdout.splitlines() if p.strip()]


def _all_files(repo_root: Path) -> list[Path]:
    """Return all files under _posts/ and assets/images/."""
    files: list[Path] = []
    for root_name in _ALL_ROOTS:
        root = repo_root / root_name
        if root.exists():
            files.extend(f for f in root.rglob("*") if f.is_file())
    return files


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------

def check_files(
    files: list[Path],
    repo_root: Path,
    whitelist: frozenset[str],
) -> list[tuple[str, str, str | None]]:
    """Check *files* for entity residues.

    Returns list of (rel_path, violation_description, suggested_clean) tuples.
    """
    violations: list[tuple[str, str, str | None]] = []

    for fpath in files:
        rel = fpath.as_posix()
        basename = fpath.name

        # Skip whitelisted entries
        if basename in whitelist or rel in whitelist:
            continue

        # Check filename itself
        if has_entity_residue(basename):
            clean = suggest_clean_name(basename)
            violations.append((rel, f"filename contains entity residue: '{basename}'", clean))

        # Check frontmatter image: field (only for markdown files in _posts)
        if (
            fpath.suffix == ".md"
            and ("_posts" in rel or rel.startswith("_posts"))
        ):
            abs_path = repo_root / fpath if not fpath.is_absolute() else fpath
            bad_image = check_frontmatter_image(abs_path)
            if bad_image is not None:
                # Avoid duplicate if the file itself already flagged
                existing_rels = {v[0] for v in violations}
                key = f"{rel}::image"
                if key not in existing_rels:
                    clean = suggest_clean_name(Path(bad_image).name)
                    violations.append((
                        rel,
                        f"frontmatter image: field contains entity residue: '{bad_image}'",
                        clean,
                    ))

    return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect HTML entity residues in filenames and frontmatter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--staged",
        action="store_true",
        default=True,
        help="Check only git-staged files (default)",
    )
    mode.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="Check all files under _posts/ and assets/images/",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    whitelist = _load_whitelist()

    if args.all:
        files = _all_files(repo_root)
        mode_label = "--all"
    else:
        files = _staged_files()
        mode_label = "--staged"

    if not files:
        return 0

    violations = check_files(files, repo_root, whitelist)

    if not violations:
        return 0

    print(
        f"[check_filename_entities] FAILED ({mode_label}) — "
        f"{len(violations)} violation(s) found:\n",
        file=sys.stderr,
    )
    for rel, description, suggested in violations:
        print(f"  FAIL  {rel}", file=sys.stderr)
        print(f"        {description}", file=sys.stderr)
        if suggested:
            print(f"        Suggested clean name: {suggested}", file=sys.stderr)
        print(file=sys.stderr)

    print(
        "Fix: rename the file(s) above, update any references, then re-stage.\n"
        "Temporary exception: add the filename/path to scripts/.filename_entity_whitelist",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
