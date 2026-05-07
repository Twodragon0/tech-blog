#!/usr/bin/env python3
"""Pre-commit guard: block posts whose JSON-LD front-matter fields contain
problematic quote characters, or whose Liquid include attributes contain
typographic (curly) quotes that break the Liquid tokeniser.

Scans `_posts/*.md` files (given as CLI arguments or auto-discovered from
staged files) and performs two checks:

Check 1 — Front-matter field quote safety
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Detects both ASCII double-quotes AND typographic (curly) quote characters
inside the decoded value of the four YAML fields that jekyll-seo-tag injects
into JSON-LD structured data:

    title, excerpt, description, image_alt

Characters that trigger a violation:

    - U+0022  ``"``    ASCII double-quote
    - U+201C  ``\u201c``  LEFT DOUBLE QUOTATION MARK
    - U+201D  ``\u201d``  RIGHT DOUBLE QUOTATION MARK
    - U+2018  ``\u2018``  LEFT SINGLE QUOTATION MARK
    - U+2019  ``\u2019``  RIGHT SINGLE QUOTATION MARK

Korean body text is intentionally excluded from this check — curly quotes
are natural there and do not appear inside Liquid attribute strings.

Check 2 — Liquid include attribute line scan
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Scans every line of the post body for lines that contain a ``{% include %}``
tag and also contain any typographic quote character.  Even a single curly
quote inside a Liquid attribute value causes a token-break that aborts the
Jekyll build (regression: 2026-05-06 build failure, fixed in f86ad2d3).

Usage
-----
    python3 scripts/check_post_quote_safety.py [file1.md file2.md ...]

Environment variables
---------------------
    SKIP_QUOTE_CHECK=1   Bypass all checks and exit 0 (for emergency commits).

Exit codes
----------
    0  No violations found.
    1  One or more violations found (commit blocked).
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CHECKED_FIELDS = frozenset({"title", "excerpt", "description", "image_alt"})

# Max characters of the offending value to show in the error message.
_SNIPPET_LEN = 80

# Typographic (curly) quote characters that must not appear in front-matter
# fields or inside Liquid include attributes.
_CURLY_QUOTES = "\u201c\u201d\u2018\u2019"

# Regex to detect a Liquid include tag anywhere on a line.
import re as _re
_LIQUID_INCLUDE_RE = _re.compile(r"\{%-?\s*include\s")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_frontmatter(text: str) -> str | None:
    """Return the raw front-matter block (between the first two ``---`` fences).

    Returns ``None`` if no valid front-matter is found.
    """
    if not text.startswith("---"):
        return None
    # Find the closing ---
    end = text.find("\n---", 3)
    if end == -1:
        return None
    return text[3:end]


def _parse_frontmatter_fields(raw: str) -> dict[str, str]:
    """Parse the four target fields from raw YAML front-matter text.

    Uses ``yaml.safe_load`` so both raw ``"`` and YAML-escaped ``\"`` are
    decoded to their actual string values — exactly what jekyll-seo-tag will
    see and emit into JSON-LD.
    """
    import yaml  # type: ignore

    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError:
        # Malformed YAML: return empty so callers don't crash.
        return {}

    result: dict[str, str] = {}
    for field in CHECKED_FIELDS:
        value = data.get(field)
        if value is not None:
            result[field] = str(value)
    return result


def check_file(path: Path) -> List[Tuple[str, str]]:
    """Check a single post file for quote violations.

    Two checks are performed:

    1. Front-matter fields (title/excerpt/description/image_alt):
       - ASCII double-quote (U+0022) — breaks JSON-LD
       - Typographic double-quotes (U+201C / U+201D) — break Liquid attributes
       - Typographic single-quotes (U+2018 / U+2019) — break Liquid attributes

    2. Body lines containing ``{% include %}`` tags:
       - Any typographic (curly) quote on the same line triggers a violation.
       Korean body text that does NOT contain include tags is excluded.

    Returns a list of ``(label, snippet)`` tuples for each violation.
    An empty list means the file is clean.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []

    violations: List[Tuple[str, str]] = []

    # ------------------------------------------------------------------
    # Check 1: front-matter fields
    # ------------------------------------------------------------------
    raw_fm = _extract_frontmatter(text)
    if raw_fm is not None:
        fields = _parse_frontmatter_fields(raw_fm)
        for field, value in fields.items():
            bad_chars = [c for c in ('"',) + tuple(_CURLY_QUOTES) if c in value]
            if bad_chars:
                snippet = value[:_SNIPPET_LEN]
                violations.append((field, snippet))

    # ------------------------------------------------------------------
    # Check 2: Liquid include lines with curly quotes in body
    # ------------------------------------------------------------------
    # Find where the body starts (after the closing --- of front-matter).
    body_start = 0
    if text.startswith("---"):
        end_fm = text.find("\n---", 3)
        if end_fm != -1:
            body_start = end_fm + 4  # skip past the closing \n---

    body = text[body_start:]
    for lineno, line in enumerate(body.splitlines(), start=1):
        if _LIQUID_INCLUDE_RE.search(line):
            curly_found = [c for c in _CURLY_QUOTES if c in line]
            if curly_found:
                snippet = line.strip()[:_SNIPPET_LEN]
                violations.append(
                    (f"include_line:{lineno}", snippet)
                )

    return violations


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """Entry point.  Returns exit code (0 = clean, 1 = violations found)."""
    if os.environ.get("SKIP_QUOTE_CHECK", "").strip() == "1":
        print("[check_post_quote_safety] SKIP_QUOTE_CHECK=1 — skipping.", flush=True)
        return 0

    args = argv if argv is not None else sys.argv[1:]

    if args:
        paths = [Path(a) for a in args if Path(a).suffix == ".md"]
    else:
        # Auto-discover staged _posts/*.md files.
        import subprocess

        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
        )
        staged = result.stdout.splitlines()
        paths = [
            Path(p)
            for p in staged
            if re.match(r"^_posts/.*\.md$", p)
        ]

    if not paths:
        return 0

    found_any = False
    for path in paths:
        violations = check_file(path)
        if violations:
            found_any = True
            print(
                f"\n[check_post_quote_safety] FAIL: {path}",
                flush=True,
            )
            for label, snippet in violations:
                if label.startswith("include_line:"):
                    print(
                        f"  Liquid include line ({label}) contains curly/typographic quote:\n"
                        f"    {snippet!r}",
                        flush=True,
                    )
                else:
                    print(
                        f"  field '{label}' contains problematic quote character:\n"
                        f"    {snippet!r}",
                        flush=True,
                    )
            print(
                "  Fix: python3 scripts/fix_malformed_liquid_includes.py\n"
                "       또는 sanitize_quotes_for_yaml() 통과시킬 것\n"
                "  (front-matter fields: replace curly/ASCII quotes with ASCII apostrophe ')\n"
                "  Bypass (emergency only): SKIP_QUOTE_CHECK=1 git commit ...",
                flush=True,
            )

    return 1 if found_any else 0


if __name__ == "__main__":
    sys.exit(main())
