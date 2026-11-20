#!/usr/bin/env python3
"""Filter post paths down to the ones the 60-point quality floor applies to.

Posts carried over verbatim from the retired 2twodragon.com WordPress site
declare ``original_url: https://2twodragon.com/...`` in front matter. They keep
their original text, and the floor scores structure written for this blog
(summary sections, length) that those posts predate, so raising them would mean
rewriting them. Every other post is still gated.

Shared by ``.github/workflows/jekyll.yml`` and ``.githooks/pre-commit`` so the
two cannot drift. Only the front-matter block is read: a body line that happens
to start with ``original_url:`` does not exempt a post.

Usage:
    python3 scripts/quality_floor_posts.py _posts/a.md _posts/b.md
Prints gated paths on stdout (one per line), exempt paths on stderr.
Paths that do not exist (deleted in the diff) are dropped.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

IMPORTED_HOST_RE = re.compile(r"""^original_url:\s*["']?https://(www\.)?2twodragon\.com/""")


def front_matter_lines(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:i]
    return []


def is_imported_wp_post(text: str) -> bool:
    return any(IMPORTED_HOST_RE.match(line) for line in front_matter_lines(text))


def main(argv: list[str]) -> int:
    for arg in argv:
        path = Path(arg)
        if not path.is_file():
            continue
        if is_imported_wp_post(path.read_text(encoding="utf-8")):
            print(f"Skipping imported WordPress post: {arg}", file=sys.stderr)
        else:
            print(arg)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
