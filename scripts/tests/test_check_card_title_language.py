"""Tests for the news-card title language gate.

Context worth keeping: before this gate, 51 of 2312 card titles were English
(2.2 %). The convention is a faithful Korean translation of the source headline
with proper nouns left in English, so those 51 were drift. 48 were translated;
3 pure proper-noun strings are allow-listed.

The gate could not reuse `check_digest_untranslated.is_untranslated()` — that
heuristic deliberately exempts cited English titles and Title-Cased proper-noun
runs because it inspects prose summaries, and run over the 51 it flagged 1.
These tests pin the opposite shape: deny by default, allow by exact string.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts import check_card_title_language as gate

REPO_ROOT = Path(__file__).resolve().parents[2]
POSTS_DIR = REPO_ROOT / "_posts"


def test_korean_title_passes():
    assert gate.offending_titles('title="Android 악성코드 분석"') == []


def test_english_title_is_flagged():
    """Proof the gate is not vacuously green."""
    assert gate.offending_titles('title="Hackers exploit a new flaw"') == [
        "Hackers exploit a new flaw"
    ]


def test_korean_bracket_label_does_not_mask_an_english_title():
    """`[클라우드]` is Hangul and would satisfy a naive check on the raw value."""
    assert gate.offending_titles('title="[클라우드] Fully English Headline Here"') == [
        "[클라우드] Fully English Headline Here"
    ]


def test_allow_listed_title_passes():
    allowed = next(iter(gate.ENGLISH_TITLE_ALLOW))
    assert gate.offending_titles(f'title="{allowed}"') == []


def test_allow_list_matches_through_non_breaking_spaces():
    """RSS feeds deliver U+00A0 that renders identically to a space.

    Two of them in a 2026-02-05 title silently defeated exact matching during
    the translation pass, so the allow-list is keyed on the normalized form.
    """
    allowed = next(iter(gate.ENGLISH_TITLE_ALLOW))
    with_nbsp = allowed.replace(" ", " ")
    assert with_nbsp != allowed
    assert gate.offending_titles(f'title="{with_nbsp}"') == []


def test_every_allow_list_entry_states_a_reason():
    """A deny-by-default list without reasons becomes a deny-nothing list."""
    for title, reason in gate.ENGLISH_TITLE_ALLOW.items():
        assert reason and len(reason) > 15, f"{title!r} has no usable reason"


def test_allow_list_stays_small():
    """If this starts absorbing real headlines the gate means nothing.

    Three entries as of 2026-08-24. Raising the ceiling is a decision: say why
    in the PR rather than growing it quietly.
    """
    assert len(gate.ENGLISH_TITLE_ALLOW) <= 6, sorted(gate.ENGLISH_TITLE_ALLOW)


def test_every_allow_list_entry_is_still_used():
    """An entry whose title no longer exists is dead permission."""
    corpus = "\n".join(
        p.read_text(encoding="utf-8", errors="ignore") for p in POSTS_DIR.glob("*.md")
    )
    normalized = gate.normalize(corpus)
    orphans = [
        t for t in gate.ENGLISH_TITLE_ALLOW if gate.normalize(t) not in normalized
    ]
    assert orphans == [], f"allow-listed titles no longer in the corpus: {orphans}"


def test_live_corpus_has_no_unallowed_english_titles():
    violations, checked = gate.scan(sorted(POSTS_DIR.glob("*.md")))
    assert violations == [], violations
    assert checked > 2000, f"only {checked} titles scanned — did the regex break?"


def test_the_scan_is_actually_looking_at_titles():
    """Guards against the corpus assertion reducing to an empty scan."""
    _, checked = gate.scan(sorted(POSTS_DIR.glob("*.md")))
    raw = sum(
        len(
            re.findall(r'title="[^"]+"', p.read_text(encoding="utf-8", errors="ignore"))
        )
        for p in POSTS_DIR.glob("*.md")
    )
    assert checked == raw > 0
