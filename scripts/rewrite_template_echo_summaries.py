"""Replace template-echo card summaries with the post's own prose.

271 card summaries across 24 digests (2026-02-20 … 2026-03-17) say nothing about
the article they sit on. They repeat the headline verbatim and bolt on one of
three fixed clauses:

    "<제목>를 기준으로 기술적으로는 공격 벡터·영향 범위·탐지 지표를 요약하고, …"
    "<제목> 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, …"
    "… 공격 경로·영향 자산·탐지 포인트를 정리하고, …"

The article-specific facts are already in the post: every affected ``news-card``
is followed by a prose paragraph that summarises the article. This lifts the
first one or two sentences of that paragraph into ``summary=``. Nothing is
fetched, nothing is invented, no LLM is called — the replacement text is copied
from the same post, a few lines below.

Measured on the corpus 2026-08-07, and this corrects the working assumption the
task started from:

===========================  =======  ==========================================
include                      defects  usable per-item prose within 20 lines
===========================  =======  ==========================================
``news-card``                    226  221 (5 have a heading/list/lead-in instead)
``news-spotlight-item``           45  **0** — they are packed back to back inside
                                      a ``{% capture %}`` block with no prose at
                                      all between them
===========================  =======  ==========================================

So spotlight items cannot be repaired this way. They are not special-cased: the
prose window simply finds nothing for them and they are skipped, the same as the
five ``news-card`` items whose follow-up is a table or a bullet list.

This edits inside a Liquid include, the exact place a context-blind rewrite
corrupted three cover images in PR #509. The runtime contract is therefore the
narrowest one that admits the change at all, and it aborts the whole run:

    a file may differ ONLY in the value of ``summary=`` inside a news card.

Usage:
    python3 scripts/rewrite_template_echo_summaries.py --posts-glob '_posts/*Weekly_Digest*.md' --dry-run
    python3 scripts/rewrite_template_echo_summaries.py _posts/2026-03-11-*.md
"""

import argparse
import glob
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Imported, not re-implemented: the corpus and the generator must not drift on
# where a Korean sentence may be cut (contract C8, PR #512).
from scripts.news.content_generator import _truncate_korean_sentence  # noqa: E402

# The three fixed clauses. A summary containing any of them describes no article.
TEMPLATE_MARKERS = (
    "공격 경로·영향 자산·탐지 포인트를 정리하고",
    "공격 벡터·영향 범위·탐지 지표를 요약하고",
    "공격 벡터와 영향 범위를 점검하고",
)

# Card summaries are capped at 200 by the generator (``_truncate_korean_sentence``
# in ``content_generator._generate_news_section``); stay inside the same budget.
MAX_SUMMARY_LEN = 200

# Below this the paragraph is a lead-in ("이번 기간 SK쉴더스 추가 발간물:"), not a
# summary. 60 rejects one real one-sentence summary in 2026-03-10, 40 does not.
MIN_PROSE_LEN = 40

# How far past the include to look. The corpus never exceeds 3 lines (blank,
# optional ``#### 요약``, blank); 20 is slack, not a licence to wander.
PROSE_WINDOW = 20

# Both card includes. ``{%-`` whitespace-control variants are the majority in
# 2026-03-06; matching only ``{%`` undercounts the corpus by 54 cards.
CARD_RE = re.compile(
    r"\{%-?\s*include\s+(?:news-card|news-spotlight-item)\.html.*?-?%\}",
    re.DOTALL,
)
SUMMARY_RE = re.compile(
    r'(\bsummary=")(.*?)("(?=\s+[\w-]+="|\s*-?%\}|\s*$))',
    re.DOTALL,
)

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_BOLD_RE = re.compile(r"\*{1,2}([^*]+)\*{1,2}")
_CODE_RE = re.compile(r"`([^`]*)`")

# Characters that either terminate the Liquid attribute or break its tokeniser.
_UNSAFE_IN_ATTR = ('"', "“", "”", "{", "}", "\n")

# Lines that end the prose search: another Liquid tag, a rule, any heading that
# is not the ``#### 요약`` lead, a table, a list, an image, a quote, a fence.
_BLOCK_PREFIXES = ("{%", "{{", "---", "***", "___", "|", "```", "!", ">", "#")
_LIST_ITEM_RE = re.compile(r"[-*+]\s")


def _is_block_start(stripped: str) -> bool:
    """True when the line opens a non-prose block.

    ``*`` and ``-`` need a following space to count as list markers: a paragraph
    may legitimately open on ``**개발자 도구**가 …``.
    """
    if stripped.startswith(_BLOCK_PREFIXES):
        return True
    return bool(_LIST_ITEM_RE.match(stripped))


def _is_template_echo(value: str) -> bool:
    return any(marker in value for marker in TEMPLATE_MARKERS)


def _is_digest_post(path: Path) -> bool:
    return "Weekly_Digest" in path.name


# --- protected regions -------------------------------------------------------


def _front_matter_end(lines) -> int:
    """Index of the first body line. 0 when the file has no front matter."""
    if not lines or lines[0].strip() != "---":
        return 0
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1
    return 0


def _fence_flags(lines, start: int):
    """True for every line inside a fenced code block.

    The toggle reads the STRIPPED line: 2026-02-08 closes its blocks with an
    indented fence, and a raw ``startswith`` flips the rest of the file
    (contract T3).
    """
    flags = [False] * len(lines)
    inside = False
    for i in range(start, len(lines)):
        if lines[i].strip().startswith("```"):
            flags[i] = True
            inside = not inside
            continue
        flags[i] = inside
    return flags


def _line_starts(text: str):
    offsets = []
    pos = 0
    for line in text.split("\n"):
        offsets.append(pos)
        pos += len(line) + 1
    return offsets


# --- extraction --------------------------------------------------------------


def _prose_after(lines, start: int, fence):
    """The article paragraph following a card, or None.

    Skips blank lines and a single ``#### 요약``-style lead heading, then returns
    the next contiguous block of plain prose. Anything else — a Liquid tag (the
    next spotlight item), a table, a list, a fence — means this card has no prose
    of its own and must be left alone.
    """
    i = start
    limit = min(len(lines), start + PROSE_WINDOW)
    while i < limit:
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("####"):
            i += 1
            continue
        break
    if i >= limit or fence[i]:
        return None
    if _is_block_start(lines[i].strip()):
        return None

    buf = []
    while i < len(lines) and lines[i].strip() and not fence[i]:
        buf.append(lines[i].strip())
        i += 1
    return " ".join(buf)


def _clean_markdown(text: str) -> str:
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _BOLD_RE.sub(r"\1", text)
    text = _CODE_RE.sub(r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def _to_liquid_safe(text: str) -> str:
    """ASCII/curly double quotes become ``'``.

    A double quote closes the attribute; a curly one is blocked outright by
    ``check_post_quote_safety.py``. A single quote is neither.
    """
    for quote in ('"', "“", "”"):
        text = text.replace(quote, "'")
    return text.replace("‘", "'").replace("’", "'")


def summarise(prose: str, max_sentences: int = 2):
    """First one or two sentences of ``prose``, or None if it is not a summary."""
    text = _clean_markdown(prose)
    if len(text) < MIN_PROSE_LEN:
        return None
    if not text.endswith(("다.", "요.", ".")):
        return None
    if "{%" in text or "{{" in text:
        return None

    sentences = [s for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]
    if not sentences:
        return None
    candidate = " ".join(sentences[:max_sentences]).strip()
    clipped = _truncate_korean_sentence(candidate, MAX_SUMMARY_LEN)
    # The helper's word-boundary fallback can APPEND "… 등이 확인되었습니다." That is
    # fine for a generator writing new text and wrong here: every character of a
    # replacement must come from the post. Requiring a prefix rejects the
    # invented tail and enforces the length cap in one check.
    if not candidate.startswith(clipped) or len(clipped) > MAX_SUMMARY_LEN:
        return None

    value = _to_liquid_safe(clipped).strip()
    if len(value) < MIN_PROSE_LEN:
        return None
    if any(ch in value for ch in _UNSAFE_IN_ATTR):
        return None
    if _is_template_echo(value):
        return None
    return value


# --- transform ---------------------------------------------------------------


def transform(text: str) -> str:
    lines = text.split("\n")
    body_start = _front_matter_end(lines)
    fence = _fence_flags(lines, body_start)
    offsets = _line_starts(text)

    def line_of(pos: int) -> int:
        lo, hi = 0, len(offsets) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offsets[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo

    edits = []
    for card in CARD_RE.finditer(text):
        first = line_of(card.start())
        last = line_of(card.end() - 1)
        if first < body_start or fence[first]:
            continue
        found = SUMMARY_RE.search(card.group(0))
        if not found or not _is_template_echo(found.group(2)):
            continue
        prose = _prose_after(lines, last + 1, fence)
        if prose is None:
            continue
        replacement = summarise(prose)
        if replacement is None:
            continue
        edits.append(
            (card.start() + found.start(2), card.start() + found.end(2), replacement)
        )

    for start, end, value in reversed(edits):
        text = text[:start] + value + text[end:]
    return text


def count_defects(text: str) -> int:
    total = 0
    for card in CARD_RE.finditer(text):
        found = SUMMARY_RE.search(card.group(0))
        if found and _is_template_echo(found.group(2)):
            total += 1
    return total


# --- runtime contract --------------------------------------------------------

_MASK = "\x00SUMMARY\x00"


def _mask_summaries(text: str) -> str:
    def _mask_card(card):
        return SUMMARY_RE.sub(
            lambda m: m.group(1) + _MASK + m.group(3), card.group(0)
        )

    return CARD_RE.sub(_mask_card, text)


def violates_summary_only(old: str, new: str) -> bool:
    """This transform may change nothing but a card ``summary=`` VALUE.

    Deliberately stronger than a token or length check: it compares the two files
    byte for byte with every card summary masked out, so any edit that leaks into
    a URL, an image attribute, the front matter or the prose aborts the run.
    """
    return _mask_summaries(old) != _mask_summaries(new)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Replace template-echo card summaries with the post's own prose."
    )
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--posts-glob")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="process at most N files")
    args = ap.parse_args(argv)

    files = [Path(p) for p in (args.paths or [])]
    if args.posts_glob:
        files += [Path(p) for p in sorted(glob.glob(args.posts_glob))]
    files = [f for f in files if _is_digest_post(f)]
    if args.limit:
        files = files[: args.limit]
    if not files:
        print("[template-echo] no digest post files to process.")
        return 0

    changed = 0
    rewritten = 0
    for path in files:
        original = path.read_text(encoding="utf-8")
        new = transform(original)
        if new == original:
            continue
        if violates_summary_only(original, new):
            print(f"ABORT {path}: change escaped the summary attribute", file=sys.stderr)
            return 1
        fixed = count_defects(original) - count_defects(new)
        changed += 1
        rewritten += fixed
        if args.dry_run:
            print(f"DRY   {path}  ({fixed} summaries)")
        else:
            path.write_text(new, encoding="utf-8")
            print(f"FIXED {path}  ({fixed} summaries)")
    verb = "would rewrite" if args.dry_run else "rewrote"
    print(
        f"[template-echo] {verb} {rewritten} summaries in "
        f"{changed}/{len(files)} post(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
