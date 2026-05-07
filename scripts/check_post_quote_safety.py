#!/usr/bin/env python3
"""Pre-commit guard: block posts whose JSON-LD front-matter fields contain ASCII
double-quotes.

Scans `_posts/*.md` files (given as CLI arguments or auto-discovered from
staged files) for raw ASCII double-quotes inside the decoded value of the
four YAML fields that jekyll-seo-tag injects into JSON-LD structured data:

    title, excerpt, description, image_alt

Both raw ``"`` in the YAML source and YAML-escaped ``\"`` are detected because
jekyll-seo-tag emits both as a raw ``"`` in the JSON-LD block, causing
JSON.parse failures and "crawled — currently not indexed" outcomes in Google
Search Console.

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
    """Check a single post file for ASCII double-quotes in the target fields.

    Returns a list of ``(field_name, snippet)`` tuples for each violation.
    An empty list means the file is clean.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return []

    raw_fm = _extract_frontmatter(text)
    if raw_fm is None:
        return []

    fields = _parse_frontmatter_fields(raw_fm)
    violations: List[Tuple[str, str]] = []
    for field, value in fields.items():
        if '"' in value:
            snippet = value[:_SNIPPET_LEN]
            violations.append((field, snippet))
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
            for field, snippet in violations:
                print(
                    f"  field '{field}' contains ASCII double-quote (\"):\n"
                    f"    {snippet!r}",
                    flush=True,
                )
            print(
                "  Fix: replace inner \" with ' in the above field(s).\n"
                "  Bypass (emergency only): SKIP_QUOTE_CHECK=1 git commit ...",
                flush=True,
            )

    return 1 if found_any else 0


if __name__ == "__main__":
    sys.exit(main())
