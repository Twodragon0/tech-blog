"""C11 target-recall tests for scripts/news_card_patterns.py.

C1-C10 of ``notes/corpus-transformer-contract.md`` all pin *where a transformer
must not write*. None of them can catch a transformer that never found a target:
a skipped card produces no diff, so every protected-region test passes while the
defect survives. C11 closes that hole by pinning the other direction —

    number of cards the pattern matches == number of cards in the corpus

The concrete failure this backstops: ``\\s`` does not match ``-``, so
``\\{%\\s*include`` skipped all 282 ``{%- include news-card`` instances and all
64 ``news-spotlight-item`` instances. PR #512 and PR #513 both shipped with that
pattern and therefore under-fixed the corpus without any test going red.

These tests derive ground truth by scanning ``_posts/`` with an independently
written scanner (C5: the audit detector must not call the detector it audits),
so they keep working as the corpus grows — they assert agreement, not a frozen
count.
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts import news_card_patterns as ncp  # noqa: E402

POSTS = sorted((REPO / "_posts").glob("*.md"))

# --- ground truth ------------------------------------------------------------
# Deliberately NOT built from ncp's own regexes (C5). One explicit literal per
# include kind per whitespace-control form, so a bug in ncp cannot hide here.
_GROUND_TRUTH_OPENERS = (
    "{% include news-card.html",
    "{%- include news-card.html",
    "{% include news-spotlight-item.html",
    "{%- include news-spotlight-item.html",
)


def _ground_truth_count(text: str) -> int:
    return sum(text.count(opener) for opener in _GROUND_TRUTH_OPENERS)


@pytest.fixture(scope="module")
def corpus():
    return [(p, p.read_text(encoding="utf-8")) for p in POSTS]


# --- the recall contract -----------------------------------------------------


def test_corpus_is_not_empty(corpus):
    """Guard against a vacuous pass if _posts/ ever moves."""
    assert len(corpus) > 100
    assert sum(_ground_truth_count(t) for _, t in corpus) > 2000


def test_card_open_re_matches_every_card_in_the_corpus(corpus):
    """C11: matched == actual, file by file so a failure names the file."""
    mismatches = [
        (p.name, ncp.count_cards(t), _ground_truth_count(t))
        for p, t in corpus
        if ncp.count_cards(t) != _ground_truth_count(t)
    ]
    assert mismatches == []


def test_card_re_finds_a_block_for_every_opening_tag(corpus):
    """A block regex that swallows two cards at once is also a recall failure."""
    mismatches = [
        (p.name, len(ncp.CARD_RE.findall(t)), _ground_truth_count(t))
        for p, t in corpus
        if len(ncp.CARD_RE.findall(t)) != _ground_truth_count(t)
    ]
    assert mismatches == []


def test_every_corpus_card_block_exposes_its_summary(corpus):
    """SUMMARY_RE must reach the value in every card that carries one."""
    misses = []
    for p, text in corpus:
        for block in ncp.CARD_RE.findall(text):
            if "summary=" in block and not ncp.SUMMARY_RE.search(block):
                misses.append((p.name, block[:80]))
    assert misses == []


def test_both_include_kinds_are_actually_present_in_the_corpus(corpus):
    """Non-vacuity: the two kinds and both forms must each be exercised."""
    joined = "\n".join(t for _, t in corpus)
    for opener in _GROUND_TRUTH_OPENERS[:3]:
        assert opener in joined, f"{opener} vanished — retune this test"


# --- regression cases per variant --------------------------------------------

_VARIANTS = {
    "card_plain": '{% include news-card.html\n  summary="가나다."\n%}',
    "card_dash": '{%- include news-card.html\n  summary="가나다."\n-%}',
    "card_dash_open_only": '{%- include news-card.html\n  summary="가나다."\n%}',
    "card_plain_dash_close": '{% include news-card.html\n  summary="가나다."\n-%}',
    "spotlight_plain": '{% include news-spotlight-item.html\n  summary="가나다."\n%}',
    "spotlight_dash": '{%- include news-spotlight-item.html\n  summary="가나다."\n-%}',
    "no_space_after_dash": '{%-include news-card.html\n  summary="가나다."\n%}',
}


@pytest.mark.parametrize("name,snippet", sorted(_VARIANTS.items()))
def test_every_whitespace_control_variant_is_matched(name, snippet):
    assert ncp.count_cards(snippet) == 1, name
    assert len(ncp.CARD_RE.findall(snippet)) == 1, name
    assert ncp.SUMMARY_RE.search(snippet).group(2) == "가나다.", name


@pytest.mark.parametrize(
    "snippet",
    [
        '{% include ai-summary-card.html summary="x" %}',
        '{% include news-spotlight-section.html body=items %}',
        '{% include news-card-legacy.html summary="x" %}',
    ],
)
def test_unrelated_includes_are_not_matched(snippet):
    """Deny-by-default: only the two enumerated kinds count."""
    assert ncp.count_cards(snippet) == 0


def test_adjacent_cards_are_matched_separately():
    """Non-greedy close: two cards must not collapse into one block."""
    two = _VARIANTS["card_dash"] + "\n\n" + _VARIANTS["card_plain"]
    assert ncp.count_cards(two) == 2
    assert len(ncp.CARD_RE.findall(two)) == 2


def test_summary_as_the_last_attribute_before_a_dash_close():
    """``-%}`` must not swallow the closing quote of the last attribute."""
    snippet = '{%- include news-card.html\n  summary="가나다."\n-%}'
    assert ncp.SUMMARY_RE.search(snippet).group(2) == "가나다."


# --- consumers stay wired to this module (C8 drift guard) --------------------


CONSUMERS = [
    "rewind_truncated_summaries.py",
    "backfill_card_summary_period.py",
    "backfill_digest_titles.py",
    "rewrite_template_echo_summaries.py",
]


@pytest.mark.parametrize("script", CONSUMERS)
def test_consumers_import_the_shared_pattern_instead_of_redeclaring(script):
    """A re-declared `\\{%\\s*include` in any consumer reopens the C11 hole."""
    src = (REPO / "scripts" / script).read_text(encoding="utf-8")
    assert "news_card_patterns import" in src, f"{script} must import the shared pattern"
    assert not re.search(r'r"\\\{%\\s\*include', src), (
        f"{script} re-declares a `-`-blind include pattern"
    )


@pytest.mark.parametrize("script", CONSUMERS)
def test_consumers_do_not_redeclare_a_card_or_summary_pattern(script):
    """Even a CORRECT copy is a C8 violation — two definitions can drift apart.

    ``rewrite_template_echo_summaries`` shipped its own ``\\{%-?\\s*include``
    trio: right pattern, wrong place. The import-presence assertion above cannot
    see that, so pin the assignment forms too.
    """
    src = (REPO / "scripts" / script).read_text(encoding="utf-8")
    offenders = re.findall(
        r"(?m)^(CARD_RE|CARD_OPEN_RE|SUMMARY_RE|SPOTLIGHT_RE|NEWS_CARD_RE)\s*=\s*re\.compile",
        src,
    )
    assert offenders == [], f"{script} re-declares {offenders}"


# --- per-kind block patterns --------------------------------------------------


def test_block_re_rejects_an_unknown_include_kind():
    with pytest.raises(ValueError):
        ncp.block_re("news-spotlight-section")


@pytest.mark.parametrize("kind", ncp.CARD_INCLUDES)
def test_every_kind_has_a_block_pattern(kind):
    assert kind in ncp.BLOCK_RE_BY_KIND


def test_per_kind_blocks_partition_the_corpus(corpus):
    """C11 for the single-kind patterns: the parts must sum to the whole."""
    mismatches = []
    for path, text in corpus:
        whole = len(ncp.CARD_RE.findall(text))
        parts = sum(len(rx.findall(text)) for rx in ncp.BLOCK_RE_BY_KIND.values())
        if whole != parts:
            mismatches.append((path.name, whole, parts))
    assert mismatches == []


def test_spotlight_re_never_matches_a_news_card():
    card = '{%- include news-card.html\n  summary="가나다."\n-%}'
    assert ncp.SPOTLIGHT_RE.findall(card) == []
    assert len(ncp.NEWS_CARD_RE.findall(card)) == 1


@pytest.mark.parametrize("dash", ["", "-"])
def test_spotlight_re_matches_both_whitespace_control_forms(dash):
    snippet = f'{{%{dash} include news-spotlight-item.html\n  summary="가나다."\n{dash}%}}'
    assert len(ncp.SPOTLIGHT_RE.findall(snippet)) == 1


# --- hyphenated attribute names (Jekyll's own grammar) -----------------------


def test_summary_value_stops_at_a_hyphenated_attribute_name():
    """``Jekyll::Tags::IncludeTag::VALID_SYNTAX`` is ``([\\w-]+)\\s*=\\s*…``, so a
    hyphenated parameter name is legal Jekyll. With ``\\w+`` in the lookahead the
    summary value would swallow it."""
    snippet = (
        "{% include news-card.html\n"
        '  summary="가나다."\n'
        '  aria-label="x"\n'
        "%}"
    )
    assert ncp.SUMMARY_RE.search(snippet).group(2) == "가나다."


def test_summary_value_still_stops_at_an_underscored_attribute_name():
    snippet = (
        "{% include news-card.html\n"
        '  summary="가나다."\n'
        '  aria_label="x"\n'
        "%}"
    )
    assert ncp.SUMMARY_RE.search(snippet).group(2) == "가나다."
