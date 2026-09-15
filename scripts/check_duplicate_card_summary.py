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

Scope
-----
A block is a violation when it says the same thing as the card. The block
legitimately survives when it carries MORE: the card truncates at 200
characters, so a longer summary needs the block for its tail (152 such blocks
remain), and an item with no card summary needs it as its only prose. 71 more
differ outright. Neither is touched.

The escaping-aware pass (2026-09-11)
------------------------------------
The first version compared bytes and said so: "~32 residual blocks differ from
their card only by quote escaping … left for a separate change". This is that
change, and the estimate was low — the real count is **66 of the 289 remaining
adjacent pairs**, in three flavours:

    45  quote shape only        '이슈'      vs  "이슈"
    11  quote shape + backslash  \\”이슈\\”  vs  ”이슈”
     1  backslash only
     9  identical but for a trailing period (some also escaping-differing)

All 66 read as the same sentence twice. :func:`canonical` folds exactly those
four differences — Unicode form, backslashes, quote glyphs, whitespace runs and
a trailing sentence mark — and nothing else.

Why this is safe to fold rather than judgement-laden: the control is that
folding must not merge a pair whose *real* characters differ. Stripping only
quotes, backslashes, whitespace and periods from both sides and comparing
lengths gives a delta of **0 for all 66** — so no pair is being called
duplicate on the strength of content the reader would otherwise lose. Measured
2026-09-11 across 295 posts.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
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


_QUOTES_RE = re.compile(r"[\"“”‘’'`]")
# The same quote characters spelled as HTML entities. Folded by name rather
# than with ``html.unescape``: that also rewrites ``&amp;``/``&lt;`` and, for
# the entities Python matches without a trailing semicolon, stretches of
# ordinary prose — a far wider licence than the live cases need. All five in
# the corpus on 2026-09-13 were ``&quot;``; the sibling spellings are here
# because a generator that emits one can emit the others.
#
# Not covered: the NUMERIC spellings of the curly quotes (``&#8220;``,
# ``&#x201C;`` …), while their named forms are. By the same "can emit the
# others" argument they belong here too; they are left out because missing one
# is fail-OPEN — one duplicated sentence, never a failed publish — and no live
# case needs them.
_QUOTE_ENTITY_RE = re.compile(
    r"&(?:quot|apos|[lr]dquo|[lr]squo|#0*3[49]|#[xX]0*2[27]);", re.I
)
# Markdown emphasis, PAIRED only, with a non-space required just inside each
# marker — markdown's own rule, and what keeps `2 ** 8 + 3 ** 4` out of reach.
#
# KNOWN LIMIT, measured rather than assumed: "paired" can be satisfied by the
# closing `**` of a DIFFERENT expression, so two exponent runs in one string do
# fold — `2**32 개와 2**64 개` collapses to `232 개와 264 개`. The fold deletes
# only the markers (`m.group(1)`), never content, so the failure mode is token
# concatenation, not a dropped clause. Incidence across the 297 posts on
# 2026-09-13: 12,718 matches, **0** where the removal joins two ASCII
# alphanumerics — the `2`+`8` signature. (Re-measuring with a bare
# `str.isalnum()` gives 1,566 instead: Hangul is alphanumeric too, so
# `**강조**의` → `강조의` counts. That join is the fold working as intended —
# Korean has no word separator — and is not the hazard.)
# Tightening this to demand a non-alphanumeric outside each marker would close
# it, and is deliberately not done — it is a wider change than the evidence
# asks for, and on the producer side it cannot bite at all (the card derives
# from the block, so both sides fold identically).
_BOLD_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*", re.S)
_WS_RE = re.compile(r"\s+")
# Trailing sentence marks only. Not `.rstrip(".")` on arbitrary text: a summary
# genuinely ending in an ellipsis or an exclamation is the same sentence as the
# block whether or not the mark survived the Liquid attribute.
_TRAILING_MARKS = ".。!?… "


def canonical(text: str) -> str:
    """Fold the differences that do not change what a reader reads.

    Unicode form, backslash escapes, quote glyph — as a character or as its
    HTML entity — paired markdown emphasis, whitespace runs, and a trailing
    sentence mark. Deliberately nothing else: every additional fold is a chance
    to call two different sentences the same.

    The producer imports this function (``scripts/news/content_generator.py``)
    to decide whether to emit the block at all, so widening a fold here makes
    the generator suppress strictly more. That is the intent — one definition,
    both sides — but it means a new fold has to be judged on generated output,
    not only on the corpus.
    """
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\\", "")
    text = _QUOTE_ENTITY_RE.sub("", text)
    text = _QUOTES_RE.sub("", text)
    text = _BOLD_RE.sub(lambda m: m.group(1), text)
    return _WS_RE.sub(" ", text).strip().rstrip(_TRAILING_MARKS)


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
        if canonical(body) == canonical(summary):
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
