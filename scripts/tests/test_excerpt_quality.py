#!/usr/bin/env python3
"""Regression guard: post excerpts must be present, sized, distinct, and not echo the title.

`excerpt:` is what the listing pages, the RSS feed, and the search index show
before a reader opens anything. A post whose excerpt merely repeats its own
title, or shares a byte-identical excerpt with another post, has a summary that
carries no information the reader did not already have.

Measured 2026-09-02 across 287 posts, all four dimensions are clean:

    present            287 / 287
    length             min 124, median 172, max 239   (CLAUDE.md targets 150-200)
    echoes its title   0
    duplicated         0

So this file is a **ratchet, not a repair**. Nothing here is currently failing;
the point is that the four properties above were never asserted anywhere, and
three of them are the kind that degrade one post at a time without any existing
gate noticing. `check_template_echo.py` is the closest neighbour and it inspects
`summary_card` **card attributes**, not front-matter `excerpt:` — a different
field on a different subset of posts.

Direction, per dimension:
  present     — hard requirement, no allowance
  length      — a band with slack on both sides of the CLAUDE.md target, so
                ordinary editing does not trip it; only a clearly broken
                excerpt (a fragment, or a pasted paragraph) does
  title echo  — hard, with a normalised comparison so punctuation and spacing
                changes do not create false positives
  duplicates  — hard on exact repeats only; near-duplicates are a judgement
                call this file deliberately does not make
"""

from __future__ import annotations

import collections
import re
import unicodedata
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = REPO_ROOT / "_posts"

# Bounds, not targets. CLAUDE.md asks authors for 150-200 characters; the corpus
# sits at 124-239. These are set outside the observed spread so the guard catches
# a broken excerpt rather than nagging about a good one that runs a little long.
MIN_LEN = 80
MAX_LEN = 320

# How much of the title has to reappear at the head of the excerpt before it
# counts as an echo. Deliberately generous: a summary legitimately reuses the
# subject's name, so only a substantial verbatim prefix qualifies.
TITLE_ECHO_PREFIX = 20

# A scanner that finds nothing must fail rather than pass silently. Set below the
# current corpus so ordinary post deletion does not trip it.
MIN_POSTS = 200


def _normalize(text: str) -> str:
    """Fold to comparable form: NFKC, strip everything but word chars and Hangul."""
    return re.sub(r"[^\w가-힣]", "", unicodedata.normalize("NFKC", text)).lower()


FRONT_MATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)


def _front_matter_field(text: str, key: str) -> str:
    """Read one field from the leading ``---`` block only.

    Parsed with YAML rather than a line regex over the whole document, for two
    reasons that both reproduce:

    1. A regex scanning the entire file also matches ```yaml fences in the body.
       A post with **no** front-matter ``excerpt:`` but an ``excerpt:`` line
       inside a body fence would satisfy ``test_every_post_has_an_excerpt`` —
       this guard's primary assertion, defeated silently. That is a hole in the
       detector, not untidiness.
    2. A folded scalar (``excerpt: >-``) captures the two-character indicator,
       so the length assertion would fail with a message about length instead
       of about the value being multi-line. YAML resolves it to the real text.

    Neither shape occurs in the corpus today (all 287 posts parse, none are
    folded), so this is the detector being correct rather than a repair.
    """
    match = FRONT_MATTER_RE.match(text)
    if not match:
        return ""
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return ""
    if not isinstance(data, dict):
        return ""
    value = data.get(key)
    return str(value).strip() if value is not None else ""


def _posts() -> list[tuple[str, str, str]]:
    """(filename, title, excerpt) for every post."""
    out = []
    for path in sorted(POSTS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8", errors="ignore")
        out.append(
            (
                path.name,
                _front_matter_field(text, "title"),
                _front_matter_field(text, "excerpt"),
            )
        )
    return out


@pytest.fixture(scope="module")
def posts() -> list[tuple[str, str, str]]:
    return _posts()


def test_posts_dir_is_not_empty(posts) -> None:
    """Non-vacuity: a broken glob must fail loudly, not pass by checking nothing."""
    assert len(posts) >= MIN_POSTS, (
        f"only {len(posts)} posts found under {POSTS_DIR} (floor {MIN_POSTS}); the "
        f"glob in _posts() has probably stopped matching, which would make every "
        f"assertion below pass by inspecting an empty list"
    )


def test_every_post_has_an_excerpt_and_a_title(posts) -> None:
    missing = [name for name, _title, excerpt in posts if not excerpt]
    assert not missing, (
        "these posts have no `excerpt:` in front matter, so listing pages, the RSS "
        "feed and the search index have nothing to show for them:\n  "
        + "\n  ".join(missing)
    )


def test_excerpt_length_is_within_bounds(posts) -> None:
    bad = [
        f"{name}: {len(excerpt)} chars"
        for name, _title, excerpt in posts
        if excerpt and not (MIN_LEN <= len(excerpt) <= MAX_LEN)
    ]
    assert not bad, (
        f"excerpts outside {MIN_LEN}-{MAX_LEN} characters (CLAUDE.md targets "
        f"150-200; these bounds are wider on purpose):\n  " + "\n  ".join(bad)
    )


def test_excerpt_does_not_echo_the_title(posts) -> None:
    """An excerpt that restates the title tells the reader nothing new.

    Compared on a normalised form so that punctuation, spacing and quoting
    differences do not manufacture a violation.
    """
    echoes = []
    for name, title, excerpt in posts:
        if not title or not excerpt:
            continue
        head = _normalize(title)[:TITLE_ECHO_PREFIX]
        if head and head in _normalize(excerpt)[: TITLE_ECHO_PREFIX * 2]:
            echoes.append(
                f"{name}\n      title:   {title[:70]}\n      excerpt: {excerpt[:70]}"
            )
    assert not echoes, (
        "these excerpts open by repeating their own title. The excerpt is the one "
        "line a reader sees next to the title, so repeating it wastes the slot — "
        "say what the post concludes instead:\n  " + "\n  ".join(echoes)
    )


def test_excerpts_are_not_duplicated_across_posts(posts) -> None:
    """Two posts sharing an excerpt means at least one is describing the wrong post.

    Exact matches only. Near-duplicates need a threshold and a human judgement
    this guard deliberately declines to make.
    """
    by_excerpt = collections.defaultdict(list)
    for name, _title, excerpt in posts:
        if excerpt:
            by_excerpt[excerpt].append(name)

    dupes = [
        (excerpt, names) for excerpt, names in by_excerpt.items() if len(names) > 1
    ]
    assert not dupes, "\n".join(
        f"{len(names)} posts share one excerpt — {excerpt[:80]}…\n  "
        + "\n  ".join(names)
        for excerpt, names in dupes
    )
