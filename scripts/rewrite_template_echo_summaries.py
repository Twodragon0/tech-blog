"""Repair template-echo card summaries: rewrite from the post's prose, or drop.

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

So spotlight items cannot be rewritten this way. In the REPLACE mode below they
are not special-cased: the prose window simply finds nothing for them and they
are skipped, the same as the five ``news-card`` items whose follow-up is a table
or a bullet list.

DROP mode then handles those 45. There is no article-specific text to put there,
and a sentence claiming a security analysis nobody performed is worse than no
sentence, so the ``summary=`` attribute is deleted outright.
``_includes/news-spotlight-item.html:9`` wraps the summary in
``{% if include.summary %}``, so the ``<p class="news-spotlight-summary">`` is
simply omitted while the title link and the source/tag meta still render.
Re-summarising from the source article was rejected: it needs a network call and
invents text, both of which this script refuses to do.

Both modes edit inside a Liquid include, the exact place a context-blind rewrite
corrupted three cover images in PR #509. Each therefore carries its OWN runtime
contract, enforced separately so that neither can launder a change through the
other's allowance, and either aborts the whole run:

    REPLACE: a file may differ ONLY in the VALUE of ``summary=`` inside a card.
    DROP:    a file may differ ONLY by whole ``summary="…"`` LINES deleted from
             ``news-spotlight-item`` includes; card count and attribute order
             stay put.

Usage:
    python3 scripts/rewrite_template_echo_summaries.py --posts-glob '_posts/*Weekly_Digest*.md' --dry-run
    python3 scripts/rewrite_template_echo_summaries.py _posts/2026-03-11-*.md
    python3 scripts/rewrite_template_echo_summaries.py --mode drop _posts/2026-03-06-*.md
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

# Same reason, for the card patterns themselves (C8 + C11). ``\s`` does not match
# ``-``, so a re-declared ``\{%\s*include`` silently skips every ``{%- include``
# card; that miss produced no diff and no red test in PR #512/#513.
from scripts.news_card_patterns import (  # noqa: E402
    CARD_RE,
    SPOTLIGHT_RE,
    SUMMARY_RE,
)

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

# Drop mode deletes whole lines, so the attribute must OWN its line. Measured:
# 45/45 spotlight defects match this; a value that ever wrapped would be skipped
# rather than half-deleted. Local to this script — it is a line-ownership test
# for the drop mechanic, not a card pattern.
SUMMARY_LINE_RE = re.compile(r'^[ \t]*summary="[^"\n]*"[ \t]*$')

# Independent of the shared patterns ON PURPOSE (contract C5): the drop contract
# audits card count and attribute order, so its detector must not be the same
# regex the rule uses, or both regress together.
_ATTR_NAME_RE = re.compile(r'(?m)^[ \t]*([\w-]+)="')
_INCLUDE_NAME_RE = re.compile(r"\{%-?\s*include\s+([\w.-]+)")

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


def _line_of(offsets, pos: int) -> int:
    lo, hi = 0, len(offsets) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if offsets[mid] <= pos:
            lo = mid
        else:
            hi = mid - 1
    return lo


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


def _quote(candidate: str):
    """One candidate quotation, validated, or None.

    Every rule that decides whether text may be lifted lives here, so the
    narrowing loop in ``summarise`` cannot weaken a check by retrying: a shorter
    candidate faces exactly the same bar as the longer one it replaces.
    """
    # Applied to the CANDIDATE, not to the whole paragraph. A paragraph often
    # trails into something that is not a sentence — a byline "(작성: …)", a
    # colon lead-in for the bullet list below it, or, in 2026-03-16, a
    # generator truncation that stops mid-word. None of those are quoted, and
    # none of them are evidence against the finished sentences above them.
    if not candidate.endswith(("다.", "요.", ".")):
        return None

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


def summarise(prose: str, max_sentences: int = 2):
    """First one or two sentences of ``prose``, or None if it is not a summary.

    Two sentences are preferred; when they cannot be quoted the first alone is
    tried before giving up. Narrowing the quote never loosens a rule — it only
    stops one unusable trailing sentence from discarding a usable leading one,
    which is the whole difference between 6 and 1 unrepairable cards.
    """
    text = _clean_markdown(prose)
    if len(text) < MIN_PROSE_LEN:
        return None
    if "{%" in text or "{{" in text:
        return None

    sentences = [s for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]
    if not sentences:
        return None
    for count in range(max_sentences, 0, -1):
        value = _quote(" ".join(sentences[:count]).strip())
        if value is not None:
            return value
    return None


# --- transform: replace ------------------------------------------------------


def replace_echo_summaries(text: str) -> str:
    """Lift the following prose paragraph into every template-echo summary.

    In practice this only ever reaches ``news-card``: spotlight items have no
    prose after them, so they fall out of ``_prose_after`` on their own.
    """
    lines = text.split("\n")
    body_start = _front_matter_end(lines)
    fence = _fence_flags(lines, body_start)
    offsets = _line_starts(text)

    edits = []
    for card in CARD_RE.finditer(text):
        first = _line_of(offsets, card.start())
        last = _line_of(offsets, card.end() - 1)
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


# --- transform: drop ---------------------------------------------------------


def _spotlight_summary_lines(text: str):
    """Line indices holding a droppable spotlight ``summary=`` echo."""
    lines = text.split("\n")
    body_start = _front_matter_end(lines)
    fence = _fence_flags(lines, body_start)
    offsets = _line_starts(text)

    found_lines = set()
    for card in SPOTLIGHT_RE.finditer(text):
        first = _line_of(offsets, card.start())
        if first < body_start or fence[first]:
            continue
        found = SUMMARY_RE.search(card.group(0))
        if not found or not _is_template_echo(found.group(2)):
            continue
        index = _line_of(offsets, card.start() + found.start(1))
        if not SUMMARY_LINE_RE.match(lines[index]):
            continue
        found_lines.add(index)
    return found_lines


def drop_spotlight_echo_summaries(text: str) -> str:
    """Delete the ``summary=`` line from spotlight items that only echo the title."""
    doomed = _spotlight_summary_lines(text)
    if not doomed:
        return text
    lines = text.split("\n")
    return "\n".join(line for i, line in enumerate(lines) if i not in doomed)


def transform(text: str) -> str:
    """Both modes, in the order ``main`` applies them."""
    return drop_spotlight_echo_summaries(replace_echo_summaries(text))


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
    """REPLACE mode may change nothing but a card ``summary=`` VALUE.

    Deliberately stronger than a token or length check: it compares the two files
    byte for byte with every card summary masked out, so any edit that leaks into
    a URL, an image attribute, the front matter or the prose aborts the run.

    Note this contract also forbids DELETING a summary — drop mode is checked by
    ``violates_spotlight_line_drop_only`` instead, so neither mode inherits the
    other's allowance.
    """
    return _mask_summaries(old) != _mask_summaries(new)


def _card_attribute_shapes(text: str):
    """``[(include name, [attr names]), …]`` for every card.

    Computed straight from the text without touching the drop rule's line
    bookkeeping, so the contract's detector cannot regress in lockstep with the
    rule it is supposed to police (contract C5).
    """
    shapes = []
    for card in CARD_RE.finditer(text):
        name = _INCLUDE_NAME_RE.match(card.group(0))
        shapes.append(
            (name.group(1) if name else "", _ATTR_NAME_RE.findall(card.group(0)))
        )
    return shapes


def _violates_card_shape(old: str, new: str) -> bool:
    """Card count and attribute order must survive; at most one ``summary`` may go."""
    old_shapes = _card_attribute_shapes(old)
    new_shapes = _card_attribute_shapes(new)
    if len(old_shapes) != len(new_shapes):
        return True
    for (old_name, old_attrs), (new_name, new_attrs) in zip(old_shapes, new_shapes):
        if old_name != new_name:
            return True
        if new_attrs == old_attrs:
            continue
        if new_name != "news-spotlight-item.html":
            return True
        if old_attrs.count("summary") != 1:
            return True
        if [a for a in old_attrs if a != "summary"] != new_attrs:
            return True
    return False


def violates_spotlight_line_drop_only(old: str, new: str) -> bool:
    """DROP mode may only DELETE whole spotlight ``summary="…"`` lines.

    Nothing may be added, reordered or rewritten; every deleted line must be a
    self-contained ``summary=`` attribute that lived inside a
    ``news-spotlight-item`` include and carried a template echo. Verified twice
    over: a strict line-by-line walk, plus an independently computed check that
    card count and attribute order did not move.
    """
    old_lines = old.split("\n")
    new_lines = new.split("\n")
    if len(new_lines) > len(old_lines):
        return True

    deletable = _spotlight_summary_lines(old)
    i = j = 0
    while i < len(old_lines) and j < len(new_lines):
        if old_lines[i] == new_lines[j]:
            i += 1
            j += 1
            continue
        if i not in deletable:
            return True
        i += 1
    if j != len(new_lines):
        return True
    while i < len(old_lines):
        if i not in deletable:
            return True
        i += 1

    return _violates_card_shape(old, new)


# Each mode is (name, rule, its own contract). Nothing shared, by design.
MODES = {
    "replace": (replace_echo_summaries, violates_summary_only),
    "drop": (drop_spotlight_echo_summaries, violates_spotlight_line_drop_only),
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Repair template-echo card summaries from the post's own prose."
    )
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--posts-glob")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--mode",
        choices=("both", "replace", "drop"),
        default="both",
        help="replace = news-card from prose; drop = spotlight summary attribute",
    )
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

    stages = ["replace", "drop"] if args.mode == "both" else [args.mode]

    changed = 0
    totals = {"replace": 0, "drop": 0}
    for path in files:
        original = path.read_text(encoding="utf-8")
        current = original
        counts = {}
        for stage in stages:
            rule, contract = MODES[stage]
            stepped = rule(current)
            # Each stage is judged against ITS OWN input, so a legal replace
            # cannot cover for an illegal drop or the other way round.
            if stepped != current and contract(current, stepped):
                print(
                    f"ABORT {path}: {stage} mode broke its runtime contract",
                    file=sys.stderr,
                )
                return 1
            counts[stage] = count_defects(current) - count_defects(stepped)
            totals[stage] += counts[stage]
            current = stepped
        if current == original:
            continue
        changed += 1
        detail = ", ".join(f"{stage} {counts[stage]}" for stage in stages)
        if args.dry_run:
            print(f"DRY   {path}  ({detail})")
        else:
            path.write_text(current, encoding="utf-8")
            print(f"FIXED {path}  ({detail})")
    verb = "would fix" if args.dry_run else "fixed"
    summary = ", ".join(f"{stage} {totals[stage]}" for stage in stages)
    print(f"[template-echo] {verb} {summary} in {changed}/{len(files)} post(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
