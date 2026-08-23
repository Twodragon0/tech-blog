"""Canonical patterns for the news-card includes a digest post renders.

This exists because of C11 ("대상 재현율") in
``notes/corpus-transformer-contract.md``: C1-C10 all constrain *where a
transformer must not write*, and nothing constrained *whether it found every
target*. A missed card produces no diff, so no protected-region test can see it.

``\\s`` does not match ``-``. A pattern written ``\\{%\\s*include`` therefore
skips every ``{%- include`` card — 282 of 2117 on 2026-08-07 — which is how
PR #512 (period backfill) and PR #513 (rewind) came to be *under*-fixes rather
than wrong fixes. Two more scripts (``check_posts``, ``cleanup_news_cards``)
already spelled it ``\\{%-?\\s*include``, so the corpus disagreed with itself.

Both include kinds carry a ``summary=`` attribute (see
``_includes/news-card.html`` and ``_includes/news-spotlight-item.html``), so a
transformer that rewrites summaries must cover both.

Importing these rather than re-declaring them is C8: one source of truth, so the
scripts cannot drift apart again. ``scripts/tests/test_news_card_patterns.py``
pins the match count against the corpus itself.
"""

import re

# Every include kind that renders a news item with a ``summary=`` attribute.
CARD_INCLUDES = ("news-card", "news-spotlight-item")

_NAMES = "|".join(re.escape(name) for name in CARD_INCLUDES)

# Opening tag only — for counting how many news items a post renders.
CARD_OPEN_RE = re.compile(rf"\{{%-?\s*include\s+(?:{_NAMES})\.html")

# The whole include block, in either whitespace-control form (``{% … %}`` and
# ``{%- … -%}``). Non-greedy, so it stops at the first closing tag.
CARD_RE = re.compile(
    rf"\{{%-?\s*include\s+(?:{_NAMES})\.html.*?-?%\}}",
    re.DOTALL,
)

# The ``summary="…"`` attribute inside a card. The lookahead ends the value at
# the next attribute, the closing tag, or end of input — never at an escaped
# quote inside the prose (``&quot;`` is what the corpus uses).
#
# The attribute name in that lookahead is ``[\w-]+``, not ``\w+``, because that
# is what Jekyll itself accepts: ``Jekyll::Tags::IncludeTag::VALID_SYNTAX`` is
# ``([\w-]+)\s*=\s*(?:"…"|'…'|[\w.-]+)`` (jekyll-4.4.1). Verified 2026-08-07:
# ``FULL_VALID_SYNTAX.match?('title="a" aria-label="x" summary="s"')`` is true.
# The corpus has no hyphenated include parameter yet, so widening the class is
# behaviour-preserving today (proved over all 2117 card blocks) and stops a
# ``summary`` value from swallowing the next attribute the day one appears.
SUMMARY_RE = re.compile(
    r'(\bsummary=")(.*?)("(?=\s+[\w-]+="|\s*-?%\}|\s*$))', re.DOTALL
)


def block_re(include_name: str) -> "re.Pattern[str]":
    """Block pattern for ONE include kind, built exactly like ``CARD_RE``.

    Transformers that must treat the kinds differently need this: dropping the
    ``summary=`` attribute is right for a spotlight item (no prose exists to
    rewrite it from) and wrong for a ``news-card``. Deny-by-default on the name
    so a typo cannot silently match nothing.
    """
    if include_name not in CARD_INCLUDES:
        raise ValueError(f"unknown card include: {include_name!r}")
    return re.compile(
        rf"\{{%-?\s*include\s+{re.escape(include_name)}\.html.*?-?%\}}",
        re.DOTALL,
    )


BLOCK_RE_BY_KIND = {name: block_re(name) for name in CARD_INCLUDES}

# Convenience aliases for the two kinds that exist today.
NEWS_CARD_RE = BLOCK_RE_BY_KIND["news-card"]
SPOTLIGHT_RE = BLOCK_RE_BY_KIND["news-spotlight-item"]


def count_cards(text: str) -> int:
    """Number of news-item includes in ``text`` (both kinds, both forms)."""
    return len(CARD_OPEN_RE.findall(text))
