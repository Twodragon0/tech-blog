#!/usr/bin/env python3
"""Rewind digest table cells that end mid-word, to a word boundary.

Why this exists
---------------
``digest_quality_report.check_file`` runs INSIDE ``auto_publish_news.py``, and a
failure there **deletes the draft** and ends the cron run. That is the largest
blast radius of any publish gate in this repo, and it was the only one with no
self-heal: the six self-heal-then-block steps in ``ai-blogwatcher.yml`` all run
*after* the post exists, so they never get a turn. Two publish days were lost
this way (2026-08-27, 2026-09-06).

The gate is also deny-by-default over an 18-word allow-list, so a false positive
is not hypothetical. Measured 2026-09-07: 10 live feed titles end in a complete
word the allow-list does not carry (``7개 주요 Bitcoin 채굴 풀``, ``2026년 초``,
``Coruna iOS 익스플로잇 킷``). Any of those landing in a trend cell costs a day.

This module makes that cost two characters instead. It does not widen the
allow-list, which would silently un-flag a whole class of real cuts.

What it does, and does not
--------------------------
It removes the dangling partial token and nothing else — no refetch, no model,
no invented text. The result is always a prefix of the input. Proven on the
whole historical corpus: 42 cells across 35 published posts, 42/42 cleared,
removing min 2 / median 2 / max 16 characters (PR #688).

It heals only ``TRUNCATED`` and ``MID-WORD``. ``ENGLISH_HEADER``,
``INCOMPLETE_HIGHLIGHT`` and ``SUMMARY_QUALITY`` have no deterministic fixer, so
they must keep blocking — healing what you cannot fix just hides it.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Run as a script, sys.path[0] is scripts/, so `scripts.news.*` does not resolve
# and the CLI half of this module dies on import. auto_publish_news.py solves it
# the same way. Measured: without this, `rewind_midword_cells.py --check --all`
# raises ModuleNotFoundError while pytest passes, because the test run already
# has the repo root on the path.
_PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from digest_quality_report import (  # noqa: E402
    analyze_post,
    find_digest_posts,
    load_midword_baseline,
    unbaselined_midword,
)

from scripts.news.content_generator import (  # noqa: E402
    _drop_dangling_lone_syllable,
    _trim_dangling_particles,
)


def rewind_cell(cell: str) -> str:
    """Drop trailing dangling tokens until the cell reaches a fixed point.

    Both helpers are needed and neither is sufficient. The gate's
    ``_TRUNCATION_PARTICLES`` and the generator's ``_DANGLING_SUFFIXES_RE`` are
    different lists: the gate carries ``할``/``인`` (single syllables, which
    ``_drop_dangling_lone_syllable`` catches) while the generator carries the
    multi-syllable ``위한``/``하기``/``대한``/``으로``/``에서`` that a lone-syllable
    rule cannot see. Iterating both to a fixed point covers the union, and
    ``test_rewind_clears_every_gate_particle`` pins that per particle rather
    than trusting this paragraph.
    """
    previous = None
    text = cell
    while text != previous:
        previous = text
        text = _drop_dangling_lone_syllable(text)
        text = _trim_dangling_particles(text)
    return text


def _flagged_suffixes(path: Path) -> dict[int, set[str]]:
    """Line number -> cell suffixes the gate would BLOCK on.

    Mirrors ``check_file``: every ``truncated_cells`` entry, and only the
    ``midword_cells`` the grandfather baseline does not already exempt. Healing
    a baselined cell would make its baseline entry stale, which
    ``test_no_baseline_entry_is_stale`` correctly treats as a defect.
    """
    issues = analyze_post(path)
    targets: dict[int, set[str]] = {}
    for cell in issues.get("truncated_cells", []):
        targets.setdefault(cell["line"], set()).add(cell["text"])
    for cell in unbaselined_midword(path.name, issues, load_midword_baseline()):
        targets.setdefault(cell["line"], set()).add(cell["text"])
    return targets


def rewind_post(path: Path, *, write: bool = True) -> list[str]:
    """Rewind every blocking cell in `path`. Returns one line per edit."""
    targets = _flagged_suffixes(path)
    if not targets:
        return []

    lines = path.read_text(encoding="utf-8").split("\n")
    edits: list[str] = []
    for lineno, suffixes in sorted(targets.items()):
        if not 1 <= lineno <= len(lines):
            continue
        line = lines[lineno - 1]
        # Segment-level replacement, not a rebuilt row: rejoining every cell
        # would reformat the padding of cells this fixer never touched.
        parts = line.split("|")
        for idx in range(1, max(len(parts) - 1, 1)):
            inner = parts[idx]
            cell = inner.strip()
            if not any(cell.endswith(suffix) for suffix in suffixes):
                continue
            healed = rewind_cell(cell)
            if healed == cell:
                continue
            assert cell.startswith(healed), (
                f"rewind must only remove a suffix, but produced new text: {healed!r}"
            )
            parts[idx] = inner.replace(cell, healed, 1)
            edits.append(
                f"L{lineno}: -{len(cell) - len(healed)} chars "
                f"{cell[-24:]!r} -> {healed[-24:]!r}"
            )
        lines[lineno - 1] = "|".join(parts)

    if edits and write:
        path.write_text("\n".join(lines), encoding="utf-8")
    return edits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("files", nargs="*", help="Digest posts to rewind")
    parser.add_argument("--all", action="store_true", help="Every digest post")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report what would change and exit 1 if anything would; write nothing",
    )
    args = parser.parse_args()

    if args.all:
        posts = find_digest_posts(None)
    elif args.files:
        posts = [Path(f) for f in args.files]
    else:
        parser.error("pass file paths or --all")

    total = 0
    for post in posts:
        if not post.is_file():
            print(f"MISSING {post}", file=sys.stderr)
            return 2
        edits = rewind_post(post, write=not args.check)
        for edit in edits:
            print(f"{'WOULD FIX' if args.check else 'FIXED'} {post.name} {edit}")
        total += len(edits)

    verb = "would be rewound" if args.check else "rewound"
    print(f"[rewind-midword] {len(posts)} post(s), {total} cell(s) {verb}.")
    return 1 if (args.check and total) else 0


if __name__ == "__main__":
    raise SystemExit(main())
