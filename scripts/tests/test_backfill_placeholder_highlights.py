#!/usr/bin/env python3
"""Tests for scripts/backfill_placeholder_highlights.py — the one-off legacy
digest highlights backfill (replace 포인트 N placeholders with the real
(source, title) rows from the body highlights table)."""

import yaml

from backfill_placeholder_highlights import (
    backfill_text,
    extract_real_highlights,
    has_placeholder,
    render_highlights_block,
)

_BODY_TABLE = (
    "## 본문\n\n"
    "| 항목 | 위험도 | 설명 |\n"          # a DIFFERENT (secondary) table first
    "|------|--------|------|\n"
    "| 전체 위험도 | 🟡 중간 | 패치 필요 |\n\n"
    "| 분야 | 소스 | 핵심 내용 | 영향도 |\n"   # the highlights table
    "|------|------|----------|--------|\n"
    "| 🔒 Security | The Hacker News | Aeternum C2 Botnet 분석 | 🔴 Critical |\n"
    "| 🤖 AI/ML | Google AI Blog | Google x Massachusetts AI Hub | 🟡 Medium |\n"
    "| ☁️ Cloud | AWS Security Blog | AWS ISO 42001 감사 통과 | 🟠 High |\n"
    "| 🔒 Security | The Hacker News | extra row beyond top 3 | 🟡 Medium |\n"
)

_PLACEHOLDER_POST = (
    "---\n"
    "layout: post\n"
    "title: \"x\"\n"
    "summary_card:\n"
    "  title: \"y\"\n"
    "  categories:\n"
    "    - { class: \"security\", label: \"보안\" }\n"
    "  highlights:\n"
    "    - { source: \"포인트 1\", title: \"2026년 보안 뉴스: The Hacker News 등 30건\" }\n"
    "    - { source: \"포인트 2\", title: \"실무 관점에서 점검\" }\n"
    "    - { source: \"포인트 3\", title: \"문서화\" }\n"
    "---\n"
    + _BODY_TABLE
)


class TestHasPlaceholder:
    def test_detects_placeholder(self):
        assert has_placeholder('  - { source: "포인트 1", title: "x" }')

    def test_real_source_not_flagged(self):
        assert not has_placeholder('  - { source: "The Hacker News", title: "x" }')


class TestExtractRealHighlights:
    def test_extracts_from_highlights_table_only(self):
        hl = extract_real_highlights(_BODY_TABLE)
        assert len(hl) == 3  # capped at top 3
        assert hl[0] == ("The Hacker News", "Aeternum C2 Botnet 분석")
        assert hl[1][0] == "Google AI Blog"
        assert hl[2][0] == "AWS Security Blog"
        # the secondary "항목 | 위험도 | 설명" table must NOT leak
        assert all("위험도" not in s and "전체 위험도" not in s for s, _ in hl)

    def test_no_table_returns_empty(self):
        assert extract_real_highlights("본문에 표 없음") == []


class TestRenderHighlightsBlock:
    def test_flow_style_and_quote_escaping(self):
        block = render_highlights_block([("AWS Blog", 'a "quoted" title')])
        assert block.startswith("  highlights:\n")
        assert '    - { source: "AWS Blog", title: "a \\"quoted\\" title" }' in block


class TestBackfillText:
    def test_replaces_placeholder_with_real_highlights(self):
        out = backfill_text(_PLACEHOLDER_POST)
        assert out is not None
        assert "포인트" not in out.split("\n---\n")[0]  # gone from front matter
        # the result parses as YAML and carries the real source
        fm = out.split("---\n", 2)[1]
        data = yaml.safe_load(fm)
        srcs = [h["source"] for h in data["summary_card"]["highlights"]]
        assert srcs == ["The Hacker News", "Google AI Blog", "AWS Security Blog"]
        # other front-matter keys preserved
        assert data["summary_card"]["title"] == "y"
        assert data["layout"] == "post"

    def test_idempotent_no_placeholder_returns_none(self):
        already_real = _PLACEHOLDER_POST.replace("포인트 1", "The Hacker News").replace(
            "포인트 2", "BleepingComputer"
        ).replace("포인트 3", "AWS Security Blog")
        assert backfill_text(already_real) is None

    def test_body_only_placeholder_string_not_rewritten(self):
        # A 포인트-like string in the BODY prose (real FM highlights) must NOT
        # trigger a front-matter rewrite — the guard is front-matter scoped.
        already_real = _PLACEHOLDER_POST.replace("포인트 1", "The Hacker News").replace(
            "포인트 2", "BleepingComputer"
        ).replace("포인트 3", "AWS Security Blog")
        # inject a placeholder-looking string into the body only
        poisoned = already_real + '\n예시 코드: source: "포인트 1"\n'
        assert backfill_text(poisoned) is None

    def test_no_body_table_returns_none(self):
        no_table = _PLACEHOLDER_POST.split("\n---\n")[0] + "\n---\n\n본문 표 없음\n"
        assert backfill_text(no_table) is None  # do not fabricate

    def test_body_preserved_byte_for_byte(self):
        out = backfill_text(_PLACEHOLDER_POST)
        assert out is not None
        assert out.split("\n---\n", 1)[1] == _PLACEHOLDER_POST.split("\n---\n", 1)[1]
