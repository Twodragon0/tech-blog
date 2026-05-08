#!/usr/bin/env python3
"""Tests for scripts/migrate_summary_cards_to_frontmatter.py.

Covers attribute extraction, HTML parsing into structured types, YAML
serialization, idempotency, and reverse migration.

API disabling and path setup are handled by conftest.py.
"""

from __future__ import annotations

import textwrap

import pytest

from migrate_summary_cards_to_frontmatter import (
    INCLUDE_BLOCK_RE,
    SummaryCard,
    build_summary_card,
    emit_summary_card_yaml,
    extract_attributes,
    migrate_post,
    parse_categories_html,
    parse_highlights_html,
    parse_tags_html,
    reverse_post,
)


# ---------------------------------------------------------------------------
# Sample posts
# ---------------------------------------------------------------------------


def _post_with_attrs() -> str:
    """A representative legacy post with `{% include ... %}` attribute form."""
    return textwrap.dedent(
        """\
        ---
        layout: post
        title: "Sample Post"
        date: 2026-05-04 11:02:00 +0900
        categories: [security, devsecops]
        tags: [Security-Weekly]
        ---

        {% include ai-summary-card.html
          title="Test title"
          categories_html='<span class="category-tag security">보안</span> <span class="category-tag devsecops">DevSecOps</span>'
          tags_html='<span class="tag">Security-Weekly</span>
              <span class="tag">CVE</span>'
          highlights_html='<li><strong>The Hacker News</strong>: Apache HTTP/2 vulnerability</li>
              <li><strong>BleepingComputer</strong>: ransomware attack</li>'
          period='2026년 05월 04일 (24시간)'
          audience='보안 담당자, DevSecOps 엔지니어'
        %}

        Body content here.
        """
    )


def _post_with_dash_include() -> str:
    """Legacy post using `{%- include ... -%}` whitespace-control variant."""
    return textwrap.dedent(
        """\
        ---
        layout: post
        title: "Whitespace Variant"
        ---

        {%- include ai-summary-card.html
          title='Title here'
          categories_html='<span class="category-tag security">Security</span>'
          tags_html='<span class="tag">A</span>
              <span class="tag">B</span>'
          highlights_html='<li><strong>Source</strong>: highlight one</li>'
          audience='engineers'
        -%}

        Body.
        """
    )


def _already_migrated_post() -> str:
    return textwrap.dedent(
        """\
        ---
        layout: post
        title: "Migrated"
        summary_card:
          title: "Pre-migrated"
          categories: []
          tags: []
          highlights: []
        ---

        {% include ai-summary-card.html %}

        Body.
        """
    )


def _post_without_include() -> str:
    return textwrap.dedent(
        """\
        ---
        layout: post
        title: "Plain post"
        ---

        Just body content with no summary card.
        """
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_extract_attributes_from_simple_include():
    body = """
      title="My Title"
      categories_html='<span class="category-tag a">A</span>'
      tags_html='<span class="tag">x</span>'
      highlights_html='<li>one</li>'
      period='now'
      audience='everyone'
    """
    attrs = extract_attributes(body)
    assert attrs["title"] == "My Title"
    assert attrs["period"] == "now"
    assert attrs["audience"] == "everyone"
    assert "category-tag" in attrs["categories_html"]
    assert "tag" in attrs["tags_html"]
    assert "<li>one</li>" in attrs["highlights_html"]


def test_extract_with_multiline_attributes():
    body = """
      tags_html='<span class="tag">A</span>
          <span class="tag">B</span>
          <span class="tag">C</span>'
    """
    attrs = extract_attributes(body)
    assert attrs["tags_html"].count("<span") == 3


def test_extract_with_quotes_in_html():
    """An include using `'` to wrap HTML containing `"` in attributes."""
    post = _post_with_attrs()
    m = INCLUDE_BLOCK_RE.search(post)
    assert m is not None
    body = m.group("body")
    attrs = extract_attributes(body)
    assert "보안" in attrs["categories_html"]
    assert 'category-tag security' in attrs["categories_html"]
    assert "DevSecOps" in attrs["categories_html"]
    assert attrs["title"] == "Test title"


def test_categories_html_parsed_to_list():
    html = (
        '<span class="category-tag security">보안</span> '
        '<span class="category-tag devsecops">DevSecOps</span>'
    )
    cats = parse_categories_html(html)
    assert cats == [
        {"class": "security", "label": "보안"},
        {"class": "devsecops", "label": "DevSecOps"},
    ]


def test_tags_html_parsed_to_list():
    html = (
        '<span class="tag">Security-Weekly</span>\n'
        '      <span class="tag">CVE</span>'
    )
    tags = parse_tags_html(html)
    assert tags == ["Security-Weekly", "CVE"]


def test_highlights_html_parsed_to_list():
    html = (
        "<li><strong>The Hacker News</strong>: Apache HTTP/2 vulnerability</li>\n"
        "      <li><strong>BleepingComputer</strong>: ransomware attack</li>"
    )
    hl = parse_highlights_html(html)
    assert hl == [
        {"source": "The Hacker News", "title": "Apache HTTP/2 vulnerability"},
        {"source": "BleepingComputer", "title": "ransomware attack"},
    ]


def test_highlights_without_strong_tag():
    html = "<li>Plain item</li>"
    hl = parse_highlights_html(html)
    assert hl == [{"source": "", "title": "Plain item"}]


def test_yaml_serialization_roundtrip():
    sc = SummaryCard(
        title="My Title",
        period="2026-05-04",
        audience="engineers",
        categories=[
            {"class": "security", "label": "보안"},
            {"class": "devsecops", "label": "DevSecOps"},
        ],
        tags=["Security-Weekly", "CVE"],
        highlights=[
            {"source": "Hacker News", "title": "vuln"},
        ],
    )
    yaml_str = emit_summary_card_yaml(sc)
    # Parse it back via PyYAML
    import yaml as _y

    data = _y.safe_load(yaml_str)
    assert data["summary_card"]["title"] == "My Title"
    assert data["summary_card"]["period"] == "2026-05-04"
    assert data["summary_card"]["audience"] == "engineers"
    assert data["summary_card"]["categories"][0]["class"] == "security"
    assert data["summary_card"]["categories"][1]["label"] == "DevSecOps"
    assert data["summary_card"]["tags"] == ["Security-Weekly", "CVE"]
    assert data["summary_card"]["highlights"][0]["source"] == "Hacker News"


def test_yaml_omits_optional_keys_when_empty():
    sc = SummaryCard(
        title="Only title",
        categories=[{"class": "a", "label": "A"}],
        tags=["t"],
        highlights=[{"source": "s", "title": "t"}],
    )
    yaml_str = emit_summary_card_yaml(sc)
    assert "period" not in yaml_str
    assert "audience" not in yaml_str
    assert "title" in yaml_str


def test_yaml_handles_empty_arrays():
    sc = SummaryCard(title="t")
    yaml_str = emit_summary_card_yaml(sc)
    assert "categories: []" in yaml_str
    assert "tags: []" in yaml_str
    assert "highlights: []" in yaml_str


def test_yaml_escapes_double_quotes_in_values():
    sc = SummaryCard(title='Title with "quotes"')
    yaml_str = emit_summary_card_yaml(sc)
    # Round-trip must give back the original
    import yaml as _y

    data = _y.safe_load(yaml_str)
    assert data["summary_card"]["title"] == 'Title with "quotes"'


def test_dry_run_no_changes(tmp_path, monkeypatch):
    p = tmp_path / "post.md"
    original = _post_with_attrs()
    p.write_text(original, encoding="utf-8")

    monkeypatch.chdir(tmp_path)
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir()
    (posts_dir / "post.md").write_text(original, encoding="utf-8")

    from migrate_summary_cards_to_frontmatter import main as mig_main

    rc = mig_main(["--dry-run", "--posts-glob", "_posts/*.md"])
    assert rc == 0
    # File on disk unchanged
    after = (posts_dir / "post.md").read_text(encoding="utf-8")
    assert after == original


def test_post_without_include_skipped():
    result = migrate_post(_post_without_include(), "test.md")
    assert result.status == "skipped"
    assert "no ai-summary-card include" in result.reason


def test_already_migrated_post_skipped_idempotent():
    result = migrate_post(_already_migrated_post(), "test.md")
    assert result.status == "skipped"
    assert "already migrated" in result.reason


def test_post_without_frontmatter_skipped():
    result = migrate_post("Just plain text\n", "test.md")
    assert result.status == "skipped"
    assert "no frontmatter" in result.reason


def test_full_migration_produces_summary_card_block():
    result = migrate_post(_post_with_attrs(), "test.md")
    assert result.status == "migrated"
    assert result.new_content is not None
    out = result.new_content
    assert "summary_card:" in out
    assert "Test title" in out
    # Body include is now the bare form
    assert "{% include ai-summary-card.html %}" in out
    # Old attribute lines should be gone from the body
    assert "categories_html=" not in out
    assert "tags_html=" not in out


def test_migration_handles_dash_include_variant():
    result = migrate_post(_post_with_dash_include(), "test.md")
    assert result.status == "migrated"
    assert "summary_card:" in result.new_content
    # Original `-` whitespace-control include is replaced with bare form
    assert "{% include ai-summary-card.html %}" in result.new_content
    assert "{%- include ai-summary-card.html" not in result.new_content


def test_migration_failed_when_required_attrs_missing():
    bad = textwrap.dedent(
        """\
        ---
        layout: post
        title: "Bad"
        ---

        {% include ai-summary-card.html
          title="just title"
        %}
        """
    )
    result = migrate_post(bad, "test.md")
    assert result.status == "failed"
    assert "missing attributes" in result.reason


def test_reverse_migration_idempotent():
    """Forward then reverse must return a working post that still has
    the include-with-attrs form, and a second reverse is a no-op."""
    forward = migrate_post(_post_with_attrs(), "test.md")
    assert forward.status == "migrated"

    reverse_once = reverse_post(forward.new_content, "test.md")
    assert reverse_once.status == "reversed"
    assert "summary_card:" not in reverse_once.new_content
    assert "{% include ai-summary-card.html" in reverse_once.new_content
    assert "categories_html=" in reverse_once.new_content

    # Second reverse is a no-op (no summary_card in frontmatter anymore)
    reverse_twice = reverse_post(reverse_once.new_content, "test.md")
    assert reverse_twice.status == "skipped"


def test_double_migration_is_idempotent():
    forward = migrate_post(_post_with_attrs(), "test.md")
    assert forward.status == "migrated"
    second = migrate_post(forward.new_content, "test.md")
    assert second.status == "skipped"
    assert "already migrated" in second.reason


@pytest.mark.parametrize(
    "raw,expected_label",
    [
        ('<span class="category-tag security">Security</span>', "Security"),
        ('<span class="category-tag devsecops">보안</span>', "보안"),
    ],
)
def test_categories_label_unicode_preserved(raw, expected_label):
    cats = parse_categories_html(raw)
    assert cats[0]["label"] == expected_label


def test_capture_variable_form_resolved_via_captures():
    """Posts that use `{% capture ai_categories_html %}...{% endcapture %}`
    plus `categories_html=ai_categories_html` (bare variable, no quotes)
    should be migrated correctly and the capture blocks stripped.

    To pass the byte-identical separator gate, the captured HTML must use
    the same separators the new include emits (space between categories,
    `\\n      ` between tags / highlights).
    """
    src = textwrap.dedent(
        """\
        ---
        layout: post
        title: "Capture form"
        ---

        {% capture ai_categories_html %}<span class="category-tag security">Security</span>{% endcapture %}

        {% capture ai_tags_html %}<span class="tag">A</span>
              <span class="tag">B</span>{% endcapture %}

        {% capture ai_highlights_html %}<li><strong>S</strong>: hl one</li>{% endcapture %}

        {% include ai-summary-card.html
          title="cap"
          categories_html=ai_categories_html
          tags_html=ai_tags_html
          highlights_html=ai_highlights_html
          period="2026-01-01"
          audience="readers"
        %}

        Body.
        """
    )
    result = migrate_post(src, "test.md")
    assert result.status == "migrated", result.reason
    out = result.new_content
    # summary_card frontmatter populated from captures
    assert 'class: "security"' in out
    assert "Security" in out
    assert "A" in out and "B" in out
    assert "hl one" in out
    # Original capture blocks have been removed (no stray HTML in body)
    assert "{% capture ai_categories_html" not in out
    assert "{% capture ai_tags_html" not in out
    assert "{% capture ai_highlights_html" not in out
    assert "{% include ai-summary-card.html %}" in out


def test_html_entities_preserved_in_highlights():
    """Original HTML escape sequences like &#x27; (added by the
    fix-malformed-liquid-includes lint) must survive parsing into
    frontmatter so re-rendered output matches baseline byte-for-byte."""
    html = (
        "<li><strong>Source</strong>: RSAC &#x27;26 highlight</li>"
        "<li><strong>S2</strong>: AT&amp;T outage</li>"
    )
    hl = parse_highlights_html(html)
    assert hl == [
        {"source": "Source", "title": "RSAC &#x27;26 highlight"},
        {"source": "S2", "title": "AT&amp;T outage"},
    ]


def test_separator_incompatible_post_skipped():
    """Posts whose tags_html uses a separator other than `\\n      ` must
    be skipped to preserve byte-identical rendering."""
    src = textwrap.dedent(
        """\
        ---
        layout: post
        title: "incompat"
        ---

        {% include ai-summary-card.html
          title="t"
          categories_html='<span class="category-tag a">A</span>'
          tags_html='<span class="tag">x</span>
        <span class="tag">y</span>'
          highlights_html='<li><strong>s</strong>: t</li>'
        %}
        """
    )
    result = migrate_post(src, "test.md")
    assert result.status == "skipped"
    assert "separator-incompatible" in result.reason
    assert "tags separator" in result.reason


def test_build_summary_card_full_pipeline():
    attrs = {
        "title": "Full",
        "categories_html": '<span class="category-tag a">A</span>',
        "tags_html": '<span class="tag">x</span>',
        "highlights_html": "<li><strong>S</strong>: t</li>",
        "period": "p",
        "audience": "a",
    }
    sc = build_summary_card(attrs)
    assert sc.title == "Full"
    assert sc.categories == [{"class": "a", "label": "A"}]
    assert sc.tags == ["x"]
    assert sc.highlights == [{"source": "S", "title": "t"}]
    assert sc.period == "p"
    assert sc.audience == "a"
