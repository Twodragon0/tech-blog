#!/usr/bin/env python3
"""Gate: a `#### 요약` block must not reprint the news card above it.

``_includes/news-card.html:54`` renders the card's ``summary=`` attribute in a
``<p class="news-card__summary">``. The generator's fallback path then emitted a
``#### 요약`` heading with the same text, so the reader saw one sentence twice,
about one line apart. Confirmed in built HTML: the sentence appears in
``<p class="news-card__summary">`` and again under ``<h4 id="요약">``.

Measured over the corpus on 2026-09-10, before the fix: **1,583 of 2,043**
blocks adjacent to a card (77%) were byte-identical to that card's summary,
across 193 of 217 digests — 215,858 characters of second printing.
``scripts/news/content_generator.py`` now suppresses the block in exactly that
case; this gate is what keeps it suppressed.

Scope, deliberately narrow
--------------------------
Only **byte-identical** bodies are violations. The block legitimately survives
when it carries more than the card: the card truncates at 200 characters, so a
longer summary needs the block for its tail (213 such blocks remain), and an
item with no card summary needs it as its only prose.

Known non-goal: ~32 residual blocks differ from their card only by quote
escaping (``\\”`` in the Liquid attribute vs ``”`` in prose) or are a strict
prefix of it. Those are duplicates to a reader but not byte-identical, and
catching them needs an escaping-aware normaliser. Flagging them with a
hand-rolled one risks the false positives that a normaliser always brings, so
they are left for a separate change rather than smuggled in here. This gate is
therefore a floor, not a ceiling.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
POSTS_DIR = REPO_ROOT / "_posts"

# Both include spellings the corpus uses, plus the `{%-` whitespace-control
# variant. Missing one of these is how a card-scanning gate ends up reporting a
# reassuring zero.
CARD_RE = re.compile(r"\{%-?\s*include\s+news-card\.html\s.*?-?%\}", re.S)
SUMMARY_ATTR_RE = re.compile(r"summary=([\"'])(.*?)\1", re.S)
# Heading plus prose up to a blank-line gap, the next heading, or a rule.
BLOCK_RE = re.compile(
    r"\n####[ \t]*요약[ \t]*\n\n(.+?)(?=\n[ \t]*\n|\n####|\n###|\n##|\n---)", re.S
)


def _fence_spans(text: str) -> list[tuple[int, int]]:
    """Character ranges inside ``` fences, which no rule here may inspect."""
    spans: list[tuple[int, int]] = []
    start: int | None = None
    for m in re.finditer(r"^```.*$", text, re.M):
        if start is None:
            start = m.start()
        else:
            spans.append((start, m.end()))
            start = None
    if start is not None:
        spans.append((start, len(text)))
    return spans


def find_violations(text: str) -> list[str]:
    """``["<first 60 chars of the duplicated body>", ...]`` for one post."""
    spans = _fence_spans(text)

    def fenced(pos: int) -> bool:
        return any(a <= pos < b for a, b in spans)

    out: list[str] = []
    for card in CARD_RE.finditer(text):
        if fenced(card.start()):
            continue
        attr = SUMMARY_ATTR_RE.search(card.group(0))
        if not attr:
            continue
        summary = attr.group(2).strip()
        if not summary:
            continue
        block = BLOCK_RE.search(text, card.end(), card.end() + 2600)
        if not block or fenced(block.start()):
            continue
        # Adjacent only: anything but whitespace between them means this block
        # belongs to a different item.
        if text[card.end() : block.start()].strip():
            continue
        body = block.group(1).strip()
        if body == summary:
            out.append(body[:60])
    return out


def check_post(path: Path) -> list[str]:
    return find_violations(path.read_text(encoding="utf-8"))


def _paths(argv: argparse.Namespace) -> list[Path]:
    if argv.paths:
        return [Path(p) for p in argv.paths]
    return sorted(POSTS_DIR.glob("*.md"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", help="post paths (default: whole corpus)")
    ap.add_argument("--all", action="store_true", help="scan the whole corpus")
    args = ap.parse_args(argv)

    paths = _paths(args)
    scanned = 0
    failures: list[tuple[Path, list[str]]] = []
    for p in paths:
        if not p.is_file():
            print(f"::error::{p} not found")
            return 1
        scanned += 1
        v = check_post(p)
        if v:
            failures.append((p, v))

    if failures:
        total = sum(len(v) for v in (f[1] for f in failures))
        print(
            f"[duplicate-card-summary] FAIL — {total} '#### 요약' block(s) reprint "
            f"the news card above them, in {len(failures)} of {scanned} post(s)."
        )
        for p, v in failures:
            print(f"FAIL {p}")
            for body in v:
                print(f"  - {body}…")
        print(
            "\nThe card already renders summary= (news-card.html:54). Drop the "
            "block, or make it carry what the card does not."
        )
        return 1

    print(f"[duplicate-card-summary] OK — {scanned} post(s) checked, 0 violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
