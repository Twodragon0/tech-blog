#!/usr/bin/env python3
"""Regression tests for ``scripts.news.content_generator.generate_news_section``
quote-safety contract.

Background — incident 2026-05-09:
The auto-publish blogwatcher emitted an `news-card` include where the
``summary`` attribute contained backslash-escaped ASCII double-quotes
(``\\"…\\"``). Liquid does NOT honor backslash escapes inside include
attributes, so it sees a literal ASCII ``"`` that terminates the value
early. ``scripts/fix_malformed_liquid_includes.py --check`` correctly
flagged this and blocked the build CI on every open PR.

Root cause: ``_sanitize_liquid_param`` (nested helper in
``generate_news_section``) was doing ``text.replace('"', '\\"')``. Fixed
to mirror ``fix_malformed_liquid_includes.py``'s convention: replace
inner ASCII ``"`` with U+201D RIGHT DOUBLE QUOTATION MARK.

These tests assert the contract holds at the *generation* boundary so
the bug can't slip through again.
"""

from __future__ import annotations

import re

from scripts.news.content_generator import generate_news_section


def _build_item(*, title: str = "x", summary: str = "y", **overrides):
    """Minimal news item dict matching what the news collector emits."""
    item = {
        "title_ko": title,  # _korean_display_title prefers title_ko if present
        "title": title,
        "summary_ko": summary,
        "summary": summary,
        "url": "https://example.com/post",
        "source_name": "Example",
        "category": "tech",
        "image": "https://example.com/post.jpg",
        "content": "x" * 800,  # avoid short-content sanitization paths
    }
    item.update(overrides)
    return item


def _extract_news_card(section: str) -> str:
    """Return the ``{% include news-card.html ... %}`` block from a section."""
    m = re.search(r"\{%\s*include\s+news-card\.html[\s\S]*?%\}", section)
    assert m, f"news-card include not emitted; section was:\n{section[:500]}"
    return m.group(0)


# ---------------------------------------------------------------------------
# Quote-safety: emitted news-card must never contain backslash-escaped ASCII "
# ---------------------------------------------------------------------------


def test_summary_with_inner_ascii_quotes_emits_curly_not_backslash():
    """Reproducer for the 2026-05-09 build break."""
    item = _build_item(
        title="암호화폐 거래소 의원에 압력",
        summary='이들은 "조작에 쉽게 취약하지 않은" 토큰 거래를 의무화하는 문구를 빼도록 요청했습니다.',
    )
    section = generate_news_section(item, "5.1")
    card = _extract_news_card(section)

    # Negative: no backslash-escaped ASCII " (the legacy buggy output).
    assert '\\"' not in card, (
        "include block must not contain backslash-escaped ASCII double-quotes; "
        "Liquid does not honor backslash escapes inside attribute values. "
        "Expected U+201D substitution per scripts/fix_malformed_liquid_includes.py."
    )
    # Positive: the curly close-quote replacement landed.
    assert "\u201d" in card, (
        "expected at least one U+201D RIGHT DOUBLE QUOTATION MARK to replace "
        "the ASCII double-quotes from the source summary"
    )


def test_summary_with_curly_quotes_normalized_then_replaced():
    """Even when the LLM emits already-curly quotes, output must still be safe."""
    item = _build_item(
        summary="이들은 \u201c조작에 취약하지 않은\u201d 토큰 거래를 요청했습니다.",
    )
    card = _extract_news_card(generate_news_section(item, "1.1"))
    assert '\\"' not in card
    # Curly was normalized to ASCII then re-mapped to U+201D — net result
    # should be U+201D in the final card (and no ASCII " inside the value).
    assert "\u201d" in card


def test_emitted_news_card_passes_fix_malformed_liquid_includes_check():
    """End-to-end: the emitted block must satisfy the gate that blocked the
    earlier deploy. Run the project's own validator on the rendered section."""
    from scripts.fix_malformed_liquid_includes import check_content

    item = _build_item(
        summary='이들은 "조작에 쉽게 취약하지 않은" 토큰 거래를 의무화하는 문구를 빼도록 요청했습니다.',
    )
    section = generate_news_section(item, "5.1")
    violations = check_content(section)
    assert violations == [], f"validator reported violations: {violations}"


def test_title_with_inner_ascii_quotes_also_safe():
    """The bug applies to every Liquid attribute, not just summary."""
    item = _build_item(
        title='Critical cPanel "Sorry" page bypass disclosed',
        summary="A short safe summary.",
    )
    card = _extract_news_card(generate_news_section(item, "1.1"))
    assert '\\"' not in card
    # title attribute must contain the curly replacement.
    title_match = re.search(r'title="([^"]*)"', card)
    assert title_match, f"title attribute missing in {card!r}"
    assert "\u201d" in title_match.group(1)


def test_no_ascii_double_quote_inside_any_attribute_value():
    """Stronger invariant: every attribute value in the include block must be
    free of ASCII " (the outer delimiter).  Even one slip terminates Liquid's
    parse early."""
    item = _build_item(
        title='Sample with "stray" quote',
        summary='Two "inner" quotes.',
    )
    card = _extract_news_card(generate_news_section(item, "2.1"))

    # Walk each `attr="value"` pair and ensure no ASCII " survives inside.
    for attr_match in re.finditer(r'(\w[\w-]*)="([^"]*)"', card):
        name, value = attr_match.group(1), attr_match.group(2)
        assert '"' not in value, (
            f'attribute {name!r} contains an inner ASCII double-quote in '
            f'value: {value!r}; Liquid would terminate the attribute early.'
        )
