#!/usr/bin/env python3
"""Tests for the L20 digest real-content extractors.

The digest covers used to render filename keywords ("AI", "AWS") + a hard
``TBD / STATUS / NEW`` KPI placeholder on every band, so they all looked
identical. ``_entity_tokens`` / ``_digest_highlight_panels`` / ``_digest_stats``
/ ``_apply_real_content`` surface the post's REAL reported content instead.

Invariants under test:

* ASCII-only output (the SVG ``<text>`` quality gate forbids Hangul).
* Real story entities / source / CVE / collection counts are surfaced.
* The visual / theme / action keys (band routing + honesty class) are NEVER
  mutated by the override — only displayed text + KPI counts change.
* A thin post (no usable highlight) keeps the existing filename-keyword path.

``sys.path`` setup + API disabling handled by ``conftest.py``.
"""

import re


from scripts.news.l20_dispatch import (
    _apply_real_content,
    _build_story,
    _digest_highlight_panels,
    _digest_stats,
    _digest_table_panels,
    _entity_tokens,
    _panel_from_source_title,
    _HEADLINE_MAX_CHARS,
    _SUB_MAX_CHARS,
)

_DIGEST_TABLE = (
    "| 분야 | 소스 | 핵심 내용 | 영향도 |\n"
    "|------|------|----------|--------|\n"
    "| 🔒 **Security** | The Hacker News | 네덜란드 당국 봇넷 해체 | 🟠 High |\n"
    "| 🔒 **Security** | BleepingComputer | WP Maps Pro 취약점 악용 | 🟠 High |\n"
    "| ⛓️ **Blockchain** | Cointelegraph | Michael Saylor BTC 매수 암시 | 🟡 Medium |\n"
)

_HANGUL = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")


def _is_ascii(text: str) -> bool:
    return all(ord(c) < 128 for c in text) and not _HANGUL.search(text)


# ---------------------------------------------------------------------------
# _entity_tokens
# ---------------------------------------------------------------------------
class TestEntityTokens:
    def test_extracts_proper_nouns_in_order(self):
        toks = _entity_tokens("Ivanti EPMM CVE-2026-6973 RCE 취약점 공개")
        assert toks[:2] == ["Ivanti", "EPMM"]
        assert "CVE-2026-6973" in toks

    def test_unescapes_html_entities_no_x27_leak(self):
        # &#x27; must not become a bogus "x27" token.
        toks = _entity_tokens("Breuninger&#x27;s be your own model AI 전략")
        assert "x27" not in toks
        assert "AI" in toks

    def test_drops_two_letter_allcaps_fragments(self):
        # "FA" is a 2-letter all-caps fragment -> dropped; "AI" is a known acronym.
        toks = _entity_tokens("AI FA 평가")
        assert "AI" in toks
        assert "FA" not in toks

    def test_drops_generic_stopwords_and_dash_artifacts(self):
        toks = _entity_tokens("the new Microsoft &mdash; Teams")
        assert "Microsoft" in toks and "Teams" in toks
        assert "the" not in [t.lower() for t in toks]
        assert "mdash" not in [t.lower() for t in toks]

    def test_all_korean_returns_empty(self):
        assert _entity_tokens("취약점 공개 및 패치 권고") == []


# ---------------------------------------------------------------------------
# _digest_highlight_panels
# ---------------------------------------------------------------------------
class TestDigestHighlightPanels:
    def _hl(self, source, title):
        return {"source": source, "title": title}

    def test_builds_headline_and_source_subheadline(self):
        hl = [self._hl("The Hacker News", "MuddyWater가 Microsoft Teams를 악용")]
        panels = _digest_highlight_panels(hl)
        assert panels[0]["headline"] == "MuddyWater Microsoft"
        assert panels[0]["subheadline"] == "The Hacker News"

    def test_cve_goes_to_subheadline_not_headline(self):
        hl = [self._hl("The Hacker News", "Ivanti EPMM CVE-2026-6973 RCE 공개")]
        panels = _digest_highlight_panels(hl)
        assert panels[0]["headline"] == "Ivanti EPMM"
        assert "CVE-2026-6973" in panels[0]["subheadline"]
        assert "The Hacker News" in panels[0]["subheadline"]

    def test_ascii_only_and_length_caps(self):
        hl = [
            self._hl("Google Cloud Blog", "Gemini Flash-Lite 에이전트 플랫폼 출시"),
            self._hl("The Hacker News", "TCLBANKER 뱅킹 트로이목마 WhatsApp 악용"),
        ]
        for p in _digest_highlight_panels(hl):
            assert _is_ascii(p["headline"]) and _is_ascii(p["subheadline"])
            assert len(p["headline"]) <= _HEADLINE_MAX_CHARS
            assert len(p["subheadline"]) <= _SUB_MAX_CHARS

    def test_skips_highlight_without_ascii_entity(self):
        hl = [
            self._hl("", "취약점 공개 권고"),                 # no ASCII -> skipped
            self._hl("BleepingComputer", "JDownloader RAT 유포"),
        ]
        panels = _digest_highlight_panels(hl)
        assert len(panels) == 1
        assert panels[0]["headline"].startswith("JDownloader")
        assert panels[0]["subheadline"] == "BleepingComputer"

    def test_no_redundant_subheadline_when_no_source(self):
        hl = [self._hl("", "APT 그룹 활동 관측")]
        panels = _digest_highlight_panels(hl)
        assert panels[0]["headline"] == "APT"
        assert panels[0]["subheadline"] != "APT"  # neutral descriptor, not echo

    def test_empty_highlights_returns_empty_list(self):
        assert _digest_highlight_panels(None) == []
        assert _digest_highlight_panels([]) == []


# ---------------------------------------------------------------------------
# _digest_table_panels (body highlights table backfill)
# ---------------------------------------------------------------------------
class TestDigestTablePanels:
    def test_parses_table_rows_skipping_header(self):
        panels = _digest_table_panels(_DIGEST_TABLE)
        # Row 1 has no ASCII entity (all-Korean title) -> skipped.
        heads = [p["headline"] for p in panels]
        assert "Maps Pro" in heads
        assert any("Michael" in h or "Saylor" in h for h in heads)
        # Header/source labels must never become panels.
        assert "소스" not in heads and "분야" not in heads

    def test_ascii_only(self):
        for p in _digest_table_panels(_DIGEST_TABLE):
            assert _is_ascii(p["headline"]) and _is_ascii(p["subheadline"])

    def test_no_table_returns_empty(self):
        assert _digest_table_panels("본문에 표 없음") == []


class TestPanelFromSourceTitle:
    def test_returns_none_without_ascii_entity(self):
        assert _panel_from_source_title("The Hacker News", "봇넷 해체 작전") is None

    def test_builds_panel(self):
        p = _panel_from_source_title("BleepingComputer", "WP Maps Pro 취약점")
        assert p["headline"] == "Maps Pro"
        assert p["subheadline"] == "BleepingComputer"


# ---------------------------------------------------------------------------
# _digest_stats
# ---------------------------------------------------------------------------
class TestDigestStats:
    def test_parses_bulleted_counts(self):
        body = "**수집 통계:**\n- **총 뉴스 수**: 30개\n- **보안 뉴스**: 5개\n"
        stats = _digest_stats(body)
        assert stats["total"] == 30
        assert stats["security"] == 5

    def test_security_not_confused_with_prose(self):
        # Intro prose mentions "보안 뉴스" with no colon; must NOT grab the total.
        body = (
            "지난 24시간 동안 주요 보안 뉴스를 분석했습니다.\n\n"
            "- **총 뉴스 수**: 24개\n- **보안 뉴스**: 5개\n"
        )
        assert _digest_stats(body)["security"] == 5

    def test_missing_markers_return_none(self):
        stats = _digest_stats("본문에 통계 없음")
        assert stats["total"] is None and stats["security"] is None


# ---------------------------------------------------------------------------
# _apply_real_content (the override)
# ---------------------------------------------------------------------------
class TestApplyRealContent:
    def _stories(self):
        hero = _build_story(headline="Botnet", subheadline="Botnet - AWS",
                            index=0, severity_label="HIGH", action="READ")
        tr = _build_story(headline="AWS", subheadline="AWS - AI",
                          index=1, severity_label="HIGH")
        br = _build_story(headline="Ransomware", subheadline="Ransomware - Go",
                          index=2, severity_label="MEDIUM")
        return [hero, tr, br]

    def test_overrides_text_and_kpis(self):
        stories = self._stories()
        post_info = {
            "summary_card": {"highlights": [
                {"source": "The Hacker News", "title": "Mirai 봇넷 ADB 악용"},
                {"source": "AWS Security Blog", "title": "AWS ISO/IEC 42001 인증"},
                {"source": "Microsoft Security Blog", "title": "MuddyWater 공격"},
            ]},
            "content": "- **총 뉴스 수**: 30개\n- **보안 뉴스**: 5개\n",
        }
        _apply_real_content(stories, post_info)
        assert stories[0]["headline"] == "Mirai ADB"
        assert stories[1]["kpi_value"] == "30" and stories[1]["kpi_label"] == "ITEMS"
        assert stories[2]["kpi_value"] == "5" and stories[2]["kpi_label"] == "SECURITY"

    def test_does_not_mutate_visual_theme_action(self):
        """Honesty invariant: routing/claim keys are never touched."""
        stories = self._stories()
        before = [(s["visual"], s["theme"], s.get("action")) for s in stories]
        post_info = {
            "summary_card": {"highlights": [
                {"source": "The Hacker News", "title": "Mirai 봇넷"},
            ]},
            "content": "- **총 뉴스 수**: 12개\n- **보안 뉴스**: 2개\n",
        }
        _apply_real_content(stories, post_info)
        after = [(s["visual"], s["theme"], s.get("action")) for s in stories]
        assert before == after

    def test_thin_post_keeps_keyword_fallback(self):
        stories = self._stories()
        original_hl = stories[1]["headline"]
        post_info = {"summary_card": {}, "content": "no stats here"}
        _apply_real_content(stories, post_info)
        # No highlights, no table -> headlines unchanged; KPI placeholder kept.
        assert stories[1]["headline"] == original_hl

    def test_backfills_thin_summary_card_from_body_table(self):
        """1 summary_card highlight + body table -> all 3 panels real, deduped."""
        stories = self._stories()
        post_info = {
            "summary_card": {"highlights": [
                {"source": "BleepingComputer", "title": "WP Maps Pro 취약점"},
            ]},
            "content": _DIGEST_TABLE,
        }
        _apply_real_content(stories, post_info)
        assert stories[0]["headline"] == "Maps Pro"            # from summary_card
        # Body-table backfill fills the next slot with a non-duplicate entity.
        assert "Maps Pro" not in stories[1]["headline"]        # deduped
        assert any("Michael" in s["headline"] or "Saylor" in s["headline"]
                   for s in stories[1:])

    def test_cron_path_content_only_no_summary_card_dict(self):
        """Cron post_info has full body content but no parsed summary_card."""
        stories = self._stories()
        post_info = {
            "content": _DIGEST_TABLE + "\n- **총 뉴스 수**: 12개\n- **보안 뉴스**: 2개\n",
        }
        _apply_real_content(stories, post_info)
        assert stories[0]["headline"] == "Maps Pro"            # from body table
        assert stories[1]["kpi_value"] == "12"                 # stats from content
        assert stories[2]["kpi_value"] == "2"
