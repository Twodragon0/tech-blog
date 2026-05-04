#!/usr/bin/env python3
"""Front-matter double-quote gate for _posts/*.md.

Detection rule
--------------
A ``title:`` or ``excerpt:`` line whose value is wrapped in outer double
quotes (``"..."``), but contains at least one inner ``"`` that is NOT
preceded by a backslash, is considered broken YAML and will cause Jekyll
to silently skip the post with::

    YAML Exception ... did not find expected key while parsing a block
    mapping at line 2 column 1

Valid forms (all accepted):
    title: "Foo \\\"Bar\\\" Baz"       # escaped inner DQ
    title: 'Foo "Bar" Baz'             # single-quoted outer
    title: Foo Bar Baz                  # unquoted

Invalid form (this script fails on):
    title: "Foo "Bar" Baz"             # unescaped inner DQ

Usage::

    python3 scripts/validators/check_frontmatter_quotes.py          # all posts
    python3 scripts/validators/check_frontmatter_quotes.py [file …]  # specific files

Exit code: 0 = no issues, 1 = at least one broken line found.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Match title: "..." or excerpt: "..." lines (only outer DQ-wrapped values)
_FIELD_RE = re.compile(r'^(title|excerpt):\s*"(.*)')

# Unescaped double-quote: a `"` NOT preceded by `\`
_UNESCAPED_DQ_RE = re.compile(r'(?<!\\)"')


def find_broken_lines(text: str) -> List[Tuple[int, str]]:
    """Return a list of (1-based line number, raw line) for front-matter lines
    in *text* whose ``title:`` or ``excerpt:`` value contains an unescaped
    inner double-quote.

    Only lines inside the opening front-matter block (between the first and
    second ``---`` delimiters) are inspected.
    """
    broken: List[Tuple[int, str]] = []

    lines = text.split("\n")
    if not lines or lines[0].rstrip() != "---":
        return broken

    in_fm = True
    for lineno, line in enumerate(lines[1:], start=2):
        if line.rstrip() == "---":
            break  # end of front matter
        if not in_fm:
            break

        m = _FIELD_RE.match(line)
        if not m:
            continue

        inner = m.group(2)
        # inner is everything after the opening `"`.
        # Count unescaped `"` characters.  The very last one is expected to be
        # the closing quote of the YAML scalar; any extra ones are broken inner
        # quotes.
        hits = _UNESCAPED_DQ_RE.findall(inner)
        if len(hits) > 1:
            broken.append((lineno, line))

    return broken


def check_file(path: Path) -> List[Tuple[int, str]]:
    """Read *path* and return broken (lineno, line) pairs."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return []
    return find_broken_lines(text)


def main(argv: List[str] | None = None) -> int:
    """Entry point.  Returns 0 on success, 1 if any violations found."""
    args = argv if argv is not None else sys.argv[1:]

    if args:
        files = [Path(f) for f in args]
    else:
        repo_root = Path(__file__).resolve().parent.parent.parent
        files = sorted((repo_root / "_posts").glob("*.md"))

    violations: List[Tuple[str, int, str]] = []

    for path in files:
        for lineno, line in check_file(path):
            violations.append((str(path), lineno, line))

    if violations:
        print(
            "FAIL: unescaped inner double-quotes found in front matter title/excerpt",
            file=sys.stderr,
        )
        print(
            "  Fix: use \\\" for inner quotes, or switch the outer wrapper to single quotes.",
            file=sys.stderr,
        )
        print(file=sys.stderr)
        for filepath, lineno, line in violations:
            print(f"  {filepath}:{lineno}: {line}", file=sys.stderr)
        print(
            f"\n{len(violations)} violation(s) found.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: checked {len(files)} file(s) — no front-matter quote violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
