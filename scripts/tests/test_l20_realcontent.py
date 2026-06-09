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
    _DIGEST_CONTENT_HONEST,
    _digest_highlight_panels,
    _digest_stats,
    _digest_table_panels,
    _entity_tokens,
    _honest_content_visual,
    _panel_from_source_title,
    resolve_digest_band_visuals,
    route_visual_id,
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
# Content-aware visual routing + honesty downgrade gate (Approach B)
# ---------------------------------------------------------------------------
class TestHonestContentVisual:
    def test_all_attack_classes_downgraded_to_advisory(self):
        # A content headline routes by keyword, but an attack-class builder
        # asserts an incident the honesty gate verifies against a body EVIDENCE
        # token — which a headline entity does not guarantee. So EVERY attack
        # class is downgraded to the always-honest security_advisory (no
        # overclaim, can never FAIL the gate on the unattended cron path).
        for v in ("cve_chain", "supply_chain_pipe", "hub_spoke", "ransomware_lock",
                  "data_exfil", "container_escape", "code_injection", "ai_agent_funnel"):
            assert _honest_content_visual(v) == "security_advisory"

    def test_always_honest_classes_kept(self):
        for v in ("neutral", "market", "security_advisory"):
            assert _honest_content_visual(v) == v


class TestResolveDigestBandVisuals:
    def test_single_cve_headline_does_not_assert_regression_chain(self):
        sc = {"highlights": [
            {"source": "The Hacker News", "title": "Ivanti EPMM CVE-2026-6973 RCE 공개"},
        ]}
        visuals = resolve_digest_band_visuals(
            "주간 보안 다이제스트", "", "2026-05-08-x.md",
            content="", summary_card=sc,
        )
        # Hero (band 0) carries the real CVE story but must NOT route cve_chain.
        assert "cve_chain" not in visuals
        assert visuals[0] == "security_advisory"

    def test_attack_routed_headline_downgraded_not_overclaimed(self):
        # A botnet/C2 headline routes to hub_spoke by keyword, but is clamped to
        # security_advisory — the gate can't confirm a body C2 evidence token.
        sc = {"highlights": [{"source": "The Hacker News", "title": "Aeternum Botnet C2 인프라 발견"}]}
        visuals = resolve_digest_band_visuals(
            "주간 보안 다이제스트", "", "2026-05-07-x.md",
            content="", summary_card=sc,
        )
        assert visuals[0] == "security_advisory"
        assert "hub_spoke" not in visuals and "cve_chain" not in visuals

    def test_band_without_panel_keeps_filename_routing(self):
        # Only one highlight -> bands 1,2 fall back to filename-keyword routing.
        sc = {"highlights": [{"source": "BleepingComputer", "title": "Maps Pro 취약점"}]}
        visuals = resolve_digest_band_visuals(
            "주간 보안 다이제스트", "", "2026-06-01-Tech_Security_Weekly_Digest_Botnet.md",
            content="", summary_card=sc,
        )
        assert len(visuals) == 3


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

    def test_visual_follows_content_and_never_overclaims(self):
        """Approach B: a band's visual re-routes to its real story, but is
        clamped to an honest class — never the overclaiming cve_chain /
        supply_chain_pipe, and the hero action follows the resolved visual."""
        stories = self._stories()
        post_info = {
            "summary_card": {"highlights": [
                # Single CVE story: must NOT assert a CVE regression chain.
                {"source": "The Hacker News", "title": "Ivanti EPMM CVE-2026-6973 RCE"},
                {"source": "The Hacker News", "title": "Packagist npm GitHub 패키지"},
                {"source": "The Hacker News", "title": "Aeternum Botnet C2 발견"},
            ]},
            "content": "- **총 뉴스 수**: 12개\n- **보안 뉴스**: 2개\n",
        }
        _apply_real_content(stories, post_info)
        visuals = [s["visual"] for s in stories]
        # No band asserts an attack class from a one-line headline.
        for attack in ("cve_chain", "supply_chain_pipe", "hub_spoke", "ransomware_lock"):
            assert attack not in visuals
        assert stories[0]["visual"] == "security_advisory"   # single CVE -> advisory
        assert stories[2]["visual"] == "security_advisory"   # botnet -> advisory
        # Hero action follows the RESOLVED visual, not "PATCH UPSTREAM NOW".
        assert stories[0]["action"] == "READ THE ADVISORY"

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


# ---------------------------------------------------------------------------
# Regression guard: content routing may NEVER assert an attack class
# ---------------------------------------------------------------------------
# This is the invariant that keeps cron-published digest covers honest. The
# honesty gate is BLOCKING and digests auto-publish unattended, so re-adding any
# attack class to the content-routing allowlist would silently re-open the
# overclaim hole (a single CVE token rendering "CVE REGRESSION CHAIN", an APT
# headline rendering a C2 graph with no body c2 token, etc.). "Honest" is
# derived from the scorer's OWN taxonomy so the guard can't drift out of lockstep.
class TestContentRoutingHonestyGuard:
    def _always_pass_classes(self):
        from scripts.score_cover_honesty import CLAIM_CLASSES
        return {vid for vid, spec in CLAIM_CLASSES.items() if spec[3]}

    def _attack_classes(self):
        from scripts.score_cover_honesty import CLAIM_CLASSES
        return {vid for vid, spec in CLAIM_CLASSES.items() if not spec[3]}

    def test_allowlist_is_subset_of_always_pass(self):
        # Every class a content headline may assert must be an always_pass
        # (non-fabricating) class in the honesty taxonomy.
        assert _DIGEST_CONTENT_HONEST <= self._always_pass_classes()

    def test_allowlist_contains_no_attack_class(self):
        assert not (_DIGEST_CONTENT_HONEST & self._attack_classes())

    def test_every_attack_class_downgrades_to_always_pass(self):
        # The gate must map EVERY attack class to an always_pass class, so a
        # content-routed band can never overclaim regardless of routing churn.
        always_pass = self._always_pass_classes()
        for vid in self._attack_classes():
            assert _honest_content_visual(vid) in always_pass

    def test_always_pass_classes_pass_through_unchanged(self):
        for vid in self._always_pass_classes():
            assert _honest_content_visual(vid) == vid
