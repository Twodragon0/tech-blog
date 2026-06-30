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
    _AI_COMPOUND_ADJECTIVES,
    _apply_real_content,
    _build_story,
    _content_descriptor,
    _content_format_word,
    _content_side_kpi,
    _DEFERRED_AI_ADJECTIVES,
    _DIGEST_CONTENT_HONEST,
    _digest_highlight_panels,
    _digest_panels,
    _digest_cadence,
    _digest_stats,
    _digest_table_counts,
    _digest_table_panels,
    _entity_tokens,
    _GENERIC_HEADLINE_WORDS,
    _honest_content_visual,
    _is_good_headline,
    _panel_from_source_title,
    _rescue_hero,
    _severity_from_marker,
    build_lead_headline,
    extract_three_stories,
    load_post_fields,
    resolve_digest_band_visuals,
    route_visual_id,
    theme_for_topics,
    _action_for,
    _HEADLINE_MAX_CHARS,
    _SUB_MAX_CHARS,
)
from scripts.lib.svg_l20_hero import render_l20_hero

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

    def test_builds_headline_and_content_subheadline(self):
        # The displayed subheadline is now a terse CONTENT summary built from the
        # title's secondary ASCII entity (here "Teams"), not a bare source name.
        # The source moves to route_hint, which drives visual routing so the
        # honest visual class is unchanged.
        hl = [self._hl("The Hacker News", "MuddyWater가 Microsoft Teams를 악용")]
        panels = _digest_highlight_panels(hl)
        assert panels[0]["headline"] == "MuddyWater Microsoft"
        assert panels[0]["subheadline"] == "Teams"
        assert panels[0]["route_hint"] == "The Hacker News"

    def test_cve_stays_out_of_headline_and_drives_routing(self):
        # CVE id is never the headline; it lives in route_hint (the routing /
        # attribution text) alongside the source. The DISPLAYED subheadline is a
        # content descriptor from the title's secondary entity ("RCE").
        hl = [self._hl("The Hacker News", "Ivanti EPMM CVE-2026-6973 RCE 공개")]
        panels = _digest_highlight_panels(hl)
        assert panels[0]["headline"] == "Ivanti EPMM"
        assert "CVE-2026-6973" not in panels[0]["headline"]
        assert "CVE-2026-6973" in panels[0]["route_hint"]
        assert "The Hacker News" in panels[0]["route_hint"]
        assert panels[0]["subheadline"] == "RCE"

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
        # Fix A: a lone short acronym ("APT", len 3) is no longer a good
        # headline, and with no ASCII source there is nothing to fall back to,
        # so the slot is skipped (None) rather than echoing a weak "APT / APT".
        hl = [self._hl("", "APT 그룹 활동 관측")]
        assert _digest_highlight_panels(hl) == []

    def test_neutral_descriptor_when_strong_headline_no_source(self):
        # A strong multi-word headline with no ASCII source gets the neutral
        # descriptor, never an echo of the headline.
        hl = [self._hl("", "SilentRoute Campaign 관측")]
        panels = _digest_highlight_panels(hl)
        assert panels[0]["headline"] == "SilentRoute Campaign"
        assert panels[0]["subheadline"] == "Security advisory"

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
        # "WP Maps Pro 취약점": headline consumes the only ASCII entities
        # (Maps, Pro; "WP" is a dropped 2-letter fragment), so no content
        # descriptor remains and the subheadline falls back to the source.
        p = _panel_from_source_title("BleepingComputer", "WP Maps Pro 취약점")
        assert p["headline"] == "Maps Pro"
        assert p["subheadline"] == "BleepingComputer"
        assert p["route_hint"] == "BleepingComputer"


# ---------------------------------------------------------------------------
# Content-descriptor subheadline: the displayed subheadline is a terse content
# summary (title's secondary ASCII entities), NOT a bare source name. The
# source/CVE text is preserved in route_hint, which drives visual routing so
# the honest visual class is byte-identical to the pre-descriptor behaviour.
# ---------------------------------------------------------------------------
class TestContentDescriptorSubheadline:
    def test_descriptor_surfaces_secondary_entities(self):
        # "Google Vertex" headline -> subheadline summarises the rest of the
        # title ("AI SDK Bucket"), not the publication.
        d = _content_descriptor(
            "Google Vertex AI SDK 결함으로 Bucket Squatting 통해 모델 업로드",
            "Google Vertex",
        )
        assert d == "AI SDK Bucket"

    def test_descriptor_excludes_headline_tokens(self):
        d = _content_descriptor("Rokarolla Android PIN SMS 코드 탈취", "Rokarolla")
        assert "Rokarolla" not in d
        assert d == "Android PIN SMS"

    def test_descriptor_empty_when_no_secondary_entity(self):
        # Only one ASCII entity (the headline itself) -> empty, so the caller
        # keeps the source attribution.
        assert _content_descriptor("ClickFix 캠페인 악성코드 확대", "ClickFix") == ""

    def test_descriptor_is_ascii_only(self):
        d = _content_descriptor("TCLBANKER 뱅킹 트로이목마 WhatsApp 악용", "TCLBANKER")
        assert _is_ascii(d)

    def test_display_subheadline_falls_back_to_source(self):
        p = _panel_from_source_title("The Hacker News", "ClickFix 캠페인 확대")
        assert p["subheadline"] == "The Hacker News"  # no secondary entity
        assert p["route_hint"] == "The Hacker News"

    def test_route_hint_keeps_routing_byte_identical(self):
        # The honest visual class must be derived from route_hint (source/CVE),
        # NOT the new content subheadline — otherwise a descriptor keyword could
        # flip the visual and the honesty class. resolve_digest_band_visuals
        # (the scorer's replay path) and _apply_real_content must agree.
        sc = {"highlights": [
            {"source": "The Hacker News",
             "title": "Google Vertex AI SDK 결함으로 Bucket Squatting 모델 업로드"},
        ]}
        panels = _digest_panels(sc, "")
        p = panels[0]
        routed_from_hint = _honest_content_visual(
            route_visual_id(f"{p['headline']} {p['route_hint']}")
        )
        # resolve_digest_band_visuals routes the SAME way (lockstep).
        visuals = resolve_digest_band_visuals(
            "주간 보안 다이제스트", "", "2026-06-17-Tech_Security_Weekly_Digest.md", "", sc
        )
        assert visuals[0] == routed_from_hint

    def test_decoupling_is_load_bearing(self):
        # Proves keying off route_hint actually matters: a title whose CONTENT
        # descriptor ("Botnet C2") routes to a DIFFERENT visual than its source
        # attribution. If routing ever regressed to the displayed subheadline,
        # the band would assert a C2/botnet motif the post evidence doesn't back.
        sc = {"highlights": [
            {"source": "The Hacker News", "title": "Acme Mirai Botnet C2 takedown"},
        ]}
        p = _digest_panels(sc, "")[0]
        from_display = route_visual_id(f"{p['headline']} {p['subheadline']}")
        from_hint = route_visual_id(f"{p['headline']} {p['route_hint']}")
        assert from_display != from_hint, "test input no longer diverges; pick another"
        # The cover routes from route_hint (honest), NOT the descriptor.
        visuals = resolve_digest_band_visuals(
            "주간 보안 다이제스트", "", "2026-06-18-Tech_Security_Weekly_Digest.md", "", sc
        )
        assert visuals[0] == _honest_content_visual(from_hint)
        assert visuals[0] != _honest_content_visual(from_display)


# ---------------------------------------------------------------------------
# Source-name echo demotion: a headline whose tokens are wholly contained in the
# row's source name carries no story info (it just echoes the publication) and
# is flagged _src_fallback so the side-card rescue demotes it. Whole-word match
# (not substring) so "Meta" vs source "Metaverse Daily" is NOT demoted.
# ---------------------------------------------------------------------------
class TestSourceEchoDemotion:
    def test_exact_source_echo_demoted(self):
        # 03-11 body-table case: source="Cloudflare Blog", title echoes it
        p = _panel_from_source_title("Cloudflare Blog", "클라우드 보안 동향 Cloudflare Blog")
        assert p is not None
        assert p.get("_src_fallback") is True

    def test_headline_subset_of_source_demoted(self):
        # 06-09 case: headline "AWS Security" ⊆ source "AWS Security Blog"
        p = _panel_from_source_title("AWS Security Blog", "5월 AWS Security 소식 정리")
        assert p is not None
        assert p["headline"] == "AWS Security"
        assert p.get("_src_fallback") is True

    def test_real_co_entity_not_demoted(self):
        # headline has a token ("Ivanti") NOT in the source -> real story, kept
        p = _panel_from_source_title("CISA", "CISA, Ivanti 취약점 긴급 권고 발표")
        assert p is not None
        assert "Ivanti" in p["headline"]
        assert not p.get("_src_fallback")

    def test_substring_not_whole_word_not_demoted(self):
        # "Meta" is a substring of "Metaverse" but NOT a whole token -> kept
        p = _panel_from_source_title("Metaverse Daily", "Meta 신규 정책 발표")
        assert p is not None
        assert p["headline"].startswith("Meta")
        assert not p.get("_src_fallback")

    def test_single_token_vendor_on_own_blog_not_demoted(self):
        # A lone vendor name may BE the story subject reported on its own blog,
        # so a single-token headline contained in the source is NOT demoted
        # (only >= 2-token publication echoes are).
        p = _panel_from_source_title("Google Cloud Blog", "Google 신규 클라우드 보안 기능")
        assert p is not None
        assert not p.get("_src_fallback")

    def test_placeholder_source_not_demoted_by_containment(self):
        # 02-27 class: source is the Korean placeholder, headline is a
        # publication name from the title prose. Containment does NOT catch this
        # (headline ⊄ "포인트 1") — it is a content-quality issue handled by the
        # placeholder-source fix, not this cover-side demotion. Documents scope.
        p = _panel_from_source_title("포인트 1", "보안 뉴스: The Hacker News, AWS Security Blog")
        assert p is not None
        assert not p.get("_src_fallback")  # NOT demoted here (deferred)

    def test_end_to_end_source_echo_demoted_below_real(self):
        sc = {"highlights": [
            {"source": "The Hacker News", "title": "Storm-2949 캠페인 분석"},
        ]}
        # body table: a real story + a source-echo row
        content = (
            "| 분야 | 소스 | 핵심 내용 | 영향도 |\n|------|------|----------|--------|\n"
            "| 🔒 **Security** | Cloudflare Blog | 클라우드 보안 동향 Cloudflare Blog | 🟡 Medium |\n"
            "| 🔒 **Security** | BleepingComputer | WP Maps Pro 취약점 악용 | 🟠 High |\n"
        )
        panels = _digest_panels(sc, content)
        heads = [p["headline"] for p in panels]
        # the source-echo "Cloudflare Blog" must not precede a real story
        assert "Cloudflare Blog" not in heads[:1]
        assert any("Maps Pro" in h or "Storm-2949" in h for h in heads)


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
# _digest_table_counts (KPI fallback for marker-less early digests)
# ---------------------------------------------------------------------------
# 5-column legacy highlights table (adds a 긴급도 / urgency column) — the format
# used by Jan–early-Feb digests that the 4-cell ``_digest_table_panels`` parser
# bails on. ``_digest_table_counts`` must read it.
_DIGEST_TABLE_5COL = (
    "| 분야 | 소스 | 핵심 내용 | 영향도 | 긴급도 |\n"
    "|------|------|----------|--------|--------|\n"
    "| 🔒 **Security** | The Hacker News | Microsoft AitM 피싱 | 🟠 High | 즉시 |\n"
    "| 🤖 **AI** | OpenAI | PostgreSQL 스케일링 | 🟡 Medium | 검토 |\n"
    "| 🔒 **보안** | BleepingComputer | VMware vCenter KEV | 🔴 Critical | 긴급 |\n"
)


class TestDigestTableCounts:
    def test_counts_4col_table_total_and_security(self):
        # _DIGEST_TABLE: 3 rows, 2 Security + 1 Blockchain.
        counts = _digest_table_counts(_DIGEST_TABLE)
        assert counts["total"] == 3
        assert counts["security"] == 2

    def test_counts_5col_legacy_table(self):
        # The 4-cell panel parser bails on this; the counter must NOT.
        counts = _digest_table_counts(_DIGEST_TABLE_5COL)
        assert counts["total"] == 3
        # English "Security" + Korean "보안" both count; "AI" does not.
        assert counts["security"] == 2

    def test_no_table_returns_none(self):
        counts = _digest_table_counts("본문에 하이라이트 테이블 없음")
        assert counts["total"] is None and counts["security"] is None

    def test_stops_at_first_non_table_line(self):
        body = _DIGEST_TABLE + "\n## 다음 섹션\n| 이슈 | 출처 | 영향도 | 권장 조치 |\n"
        # Only the highlights table rows are counted; the trailing reference
        # table after the blank line / heading is excluded.
        assert _digest_table_counts(body)["total"] == 3

    def test_panel_parser_untouched_by_counter(self):
        # The shared panel parser still bails on the 5-col table (count-only
        # helper must not have changed panel extraction / scorer routing).
        assert _digest_table_panels(_DIGEST_TABLE_5COL) == []


# ---------------------------------------------------------------------------
# _digest_cadence (count-free KPI descriptor source)
# ---------------------------------------------------------------------------
class TestDigestCadence:
    def test_weekly_daily_monthly_from_filename(self):
        assert _digest_cadence({"filename": "2026-01-26-Tech_Security_Weekly_Digest_X.md"}) == "WEEKLY"
        assert _digest_cadence({"filename": "2026-02-16-Daily_Tech_Digest_RSS.md"}) == "DAILY"
        assert _digest_cadence({"filename": "2026-03-30-March_2026_Monthly_Index.md"}) == "MONTH"

    def test_defaults_to_digest(self):
        assert _digest_cadence({"filename": "2026-01-01-Some_Roundup.md", "title": ""}) == "DIGEST"

    def test_ascii_only_and_within_cap(self):
        for fn in ("Weekly", "Daily", "Monthly", "Other"):
            v = _digest_cadence({"filename": fn})
            assert v.isascii() and len(v) <= 6


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
        assert stories[0]["visual"] == "security_advisory"   # single CVE -> advisory (hero keeps it)
        # Side band (index 2): advisory is demoted to a neutral motif so the
        # hero-scale shield never occludes the band headline / duplicates.
        assert stories[2]["visual"] == "neutral"             # botnet -> advisory -> sidecard demote
        # Hero action follows the RESOLVED visual, not "PATCH UPSTREAM NOW".
        assert stories[0]["action"] == "READ THE ADVISORY"

    def test_sidecard_advisory_demoted_to_neutral(self):
        """Side bands (index >= 1) never carry the hero-scale advisory shield;
        it is demoted to a diverse neutral motif (honesty-safe). The hero
        (index 0) keeps advisory where the panel fits."""
        stories = self._stories()
        post_info = {
            "summary_card": {"highlights": [
                # All three downgrade to advisory (single CVE / generic / botnet).
                {"source": "The Hacker News", "title": "Ivanti EPMM CVE-2026-6973 RCE"},
                {"source": "The Hacker News", "title": "Acme Security Advisory 발표"},
                {"source": "The Hacker News", "title": "Aeternum Botnet C2 발견"},
            ]},
            "content": "- **총 뉴스 수**: 12개\n- **보안 뉴스**: 2개\n",
        }
        _apply_real_content(stories, post_info)
        assert stories[0]["visual"] == "security_advisory"   # hero keeps advisory
        assert stories[1]["visual"] == "neutral"             # side -> demoted
        assert stories[2]["visual"] == "neutral"             # side -> demoted
        # Demoted side bands follow neutral theme + action (no stale amber/advisory).
        assert stories[1]["theme"] == "blue"
        assert "advisory" not in stories[1].get("action", "").lower() or "action" not in stories[1]

    def test_thin_post_keeps_keyword_fallback(self):
        stories = self._stories()
        original_hl = stories[1]["headline"]
        post_info = {"summary_card": {}, "content": "no stats here",
                     "filename": "2026-01-26-Tech_Security_Weekly_Digest_X.md"}
        _apply_real_content(stories, post_info)
        # No highlights, no table -> headlines unchanged; KPI shows a count-free
        # honest descriptor (cadence / curation), NOT the ``TBD`` placeholder.
        assert stories[1]["headline"] == original_hl
        assert stories[1]["kpi_value"] == "WEEKLY" and stories[1]["kpi_label"] == "DIGEST"
        assert stories[2]["kpi_value"] == "MULTI" and stories[2]["kpi_label"] == "SOURCES"
        assert "TBD" not in (stories[1]["kpi_value"], stories[2]["kpi_value"])

    def test_marker_takes_precedence_over_table(self):
        # When both a marker AND a highlights table exist, the marker (true feed
        # volume) wins; the table is only a fallback.
        stories = self._stories()
        post_info = {
            "summary_card": {},
            "content": "- **총 뉴스 수**: 28개\n- **보안 뉴스**: 9개\n" + _DIGEST_TABLE,
        }
        _apply_real_content(stories, post_info)
        assert stories[1]["kpi_value"] == "28"   # marker total, not table's 3
        assert stories[2]["kpi_value"] == "9"     # marker security, not table's 2

    def test_table_fallback_when_no_marker(self):
        # No markers -> the highlights-table row counts populate the KPIs.
        stories = self._stories()
        post_info = {"summary_card": {}, "content": _DIGEST_TABLE}
        _apply_real_content(stories, post_info)
        assert stories[1]["kpi_value"] == "3" and stories[1]["kpi_label"] == "ITEMS"
        assert stories[2]["kpi_value"] == "2" and stories[2]["kpi_label"] == "SECURITY"

    def test_table_fallback_reads_5col_legacy_table(self):
        # The early 5-column digest format (the original TBD source) is fixed.
        stories = self._stories()
        post_info = {"summary_card": {}, "content": _DIGEST_TABLE_5COL}
        _apply_real_content(stories, post_info)
        assert stories[1]["kpi_value"] == "3"
        assert stories[2]["kpi_value"] == "2"

    def test_marker_security_wins_table_total_fallback(self):
        # Mixed availability: security marker present but total marker absent ->
        # total falls back to the table, security keeps the marker.
        stories = self._stories()
        post_info = {"summary_card": {}, "content": "- **보안 뉴스**: 10개\n" + _DIGEST_TABLE}
        _apply_real_content(stories, post_info)
        assert stories[1]["kpi_value"] == "3"    # table total (no total marker)
        assert stories[2]["kpi_value"] == "10"    # security marker wins over table's 2

    def test_zero_total_marker_respected_over_table(self):
        # An authoritative ``총 뉴스 수: 0`` (empty feed) must NOT be overridden
        # by the table row count — total/security stay symmetric on the 0 case.
        stories = self._stories()
        post_info = {"summary_card": {},
                     "content": "- **총 뉴스 수**: 0개\n- **보안 뉴스**: 0개\n" + _DIGEST_TABLE}
        _apply_real_content(stories, post_info)
        assert stories[1]["kpi_value"] == "0" and stories[1]["kpi_label"] == "ITEMS"
        assert stories[2]["kpi_value"] == "0" and stories[2]["kpi_label"] == "SECURITY"

    def test_count_free_label_is_ascii(self):
        stories = self._stories()
        post_info = {"summary_card": {}, "content": "no stats",
                     "filename": "2026-02-16-Daily_Tech_Digest.md"}
        _apply_real_content(stories, post_info)
        for s in (stories[1], stories[2]):
            for key in ("kpi_value", "kpi_label", "kpi_sub"):
                assert s[key].isascii()
        assert stories[1]["kpi_value"] == "DAILY"

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


# ---------------------------------------------------------------------------
# Headline quality (Fix A): garbled / bare-acronym headlines are rejected
# ---------------------------------------------------------------------------
import pytest  # noqa: E402


class TestIsGoodHeadline:
    @pytest.mark.parametrize("tok", [
        "Showboat", "ChatGPhish", "Apache HTTP/2", "Ivanti", "Cisco",
        "Defender", "CVE-2026-1234",
    ])
    def test_good_tokens(self, tok):
        assert _is_good_headline(tok) is True

    @pytest.mark.parametrize("tok", [
        "Sorry", "AI", "VPN", "npm", "MENA", "Linux", "New", "",
        "안녕하세요",  # non-ASCII never good
    ])
    def test_bad_tokens(self, tok):
        assert _is_good_headline(tok) is False


class TestHeadlineQuality:
    """The known-bad raw digest titles must not produce garbage headlines.

    A ``None`` panel means the slot stays on the filename-keyword fallback —
    acceptable; what is NOT acceptable is a lone acronym / generic / weak word
    becoming the displayed headline.
    """
    _BAD_LONE = {"sorry", "ai", "vpn", "npm", "mena", "linux"}

    @pytest.mark.parametrize("ttl", [
        "Sorry", "AI", "VPN", "npm", "MENA",
    ])
    def test_lone_bad_word_never_a_headline(self, ttl):
        # With a Korean (non-ASCII) source the panel must be None (no garbage),
        # because the only ASCII token is a rejected lone word.
        p = _panel_from_source_title("한국소스", ttl)
        assert p is None

    @pytest.mark.parametrize("ttl,expected", [
        ("Showboat Linux", "Showboat"),
        ("ChatGPhish ChatGPT", "ChatGPhish"),
        ("Linux Defender", "Defender"),
    ])
    def test_garbled_titles_cleaned(self, ttl, expected):
        p = _panel_from_source_title("The Hacker News", ttl)
        assert p is not None
        assert p["headline"] == expected

    @pytest.mark.parametrize("ttl", [
        "Apache HTTP/2", "Ivanti EPMM", "Cisco Catalyst",
        "Mirai ADB", "Turla Kazuar", "Hugging Face",
    ])
    def test_good_titles_unchanged(self, ttl):
        p = _panel_from_source_title("The Hacker News", ttl)
        assert p is not None
        assert p["headline"] == ttl

    def test_no_panel_ever_emits_a_bad_lone_headline(self):
        for ttl in ("Sorry", "AI", "VPN", "npm", "MENA"):
            p = _panel_from_source_title("The Hacker News", ttl)
            # ASCII source -> falls back to source headline, never the bad word.
            assert p is not None
            assert p["headline"].lower() not in self._BAD_LONE


class TestPanelFallback:
    def test_korean_subject_non_ascii_source_returns_none(self):
        assert _panel_from_source_title("한국소스", "봇넷 해체 작전") is None

    def test_ascii_source_fallback_uses_source_and_advisory_sub(self):
        # The only ASCII token is a rejected lone word ("Sorry"), so no entity
        # passes; the ASCII source becomes the headline with a neutral sub.
        p = _panel_from_source_title("The Hacker News", "Sorry 사과문 발표")
        assert p is not None
        assert p["headline"] == "The Hacker News"
        assert p["subheadline"] == "Security advisory"

    def test_zero_token_title_returns_none(self):
        # An all-Korean title has no ASCII token at all -> skip the slot.
        assert _panel_from_source_title("The Hacker News", "보안 속보 분석") is None


# ---------------------------------------------------------------------------
# Severity (Fix B): real severity instead of "SEVERITY: TBD"
# ---------------------------------------------------------------------------
class TestSeverityFromMarker:
    @pytest.mark.parametrize("cell,expected", [
        ("🔴 Critical", "CRITICAL"),
        ("🟠 High", "HIGH"),
        ("🟡 Medium", "MEDIUM"),
        ("Low", ""),
        ("", ""),
        ("-", ""),
    ])
    def test_emoji_to_ascii(self, cell, expected):
        assert _severity_from_marker(cell) == expected


class TestSeverityPanelPlumbing:
    def test_table_panel_carries_severity(self):
        table = (
            "| 분야 | 소스 | 핵심 내용 | 영향도 |\n"
            "|------|------|----------|--------|\n"
            "| Security | The Hacker News | Aeternum Botnet C2 | 🔴 Critical |\n"
        )
        panels = _digest_table_panels(table)
        assert panels and panels[0].get("severity") == "CRITICAL"

    def test_highlight_panel_carries_severity(self):
        hl = [{"source": "The Hacker News", "title": "Aeternum Botnet C2",
               "severity": "🟠 High"}]
        panels = _digest_highlight_panels(hl)
        assert panels and panels[0].get("severity") == "HIGH"

    def test_apply_real_content_sets_story_severity(self):
        stories = [
            _build_story(headline="x", subheadline="x", index=0,
                         severity_label="HIGH", action="READ"),
            _build_story(headline="x", subheadline="x", index=1,
                         severity_label="HIGH"),
            _build_story(headline="x", subheadline="x", index=2,
                         severity_label="MEDIUM"),
        ]
        post_info = {
            "summary_card": {"highlights": [
                {"source": "The Hacker News", "title": "Aeternum Botnet C2",
                 "severity": "🟠 High"},
            ]},
            "content": "- **총 뉴스 수**: 12개\n- **보안 뉴스**: 2개\n",
        }
        _apply_real_content(stories, post_info)
        assert stories[0].get("severity") == "HIGH"


class TestRenderedSeverity:
    def _stories_with_advisory(self):
        stories = [
            _build_story(headline="x", subheadline="x", index=0,
                         severity_label="HIGH", action="READ"),
            _build_story(headline="x", subheadline="x", index=1,
                         severity_label="HIGH"),
            _build_story(headline="x", subheadline="x", index=2,
                         severity_label="MEDIUM"),
        ]
        post_info = {
            "summary_card": {"highlights": [
                {"source": "The Hacker News", "title": "Aeternum Botnet C2 발견",
                 "severity": "🟠 High"},
            ]},
            "content": "- **총 뉴스 수**: 30개\n- **보안 뉴스**: 5개\n",
        }
        _apply_real_content(stories, post_info)
        return stories

    def test_no_tbd_or_under_review_in_svg(self):
        st = self._stories_with_advisory()
        svg = render_l20_hero("2026.05.30", st[0], st[1], st[2],
                              "https://x", "Digest")
        assert "SEVERITY: TBD" not in svg
        assert "unspecified - under review" not in svg

    def test_known_severity_line_present(self):
        st = self._stories_with_advisory()
        # Band 0 routes to security_advisory (botnet headline -> clamp) and has
        # a known severity, so the gauge shows the ASCII severity word.
        assert st[0]["visual"] == "security_advisory"
        svg = render_l20_hero("2026.05.30", st[0], st[1], st[2],
                              "https://x", "Digest")
        assert "SEVERITY: HIGH" in svg

    def test_anchors_and_ascii_preserved(self):
        st = self._stories_with_advisory()
        svg = render_l20_hero("2026.05.30", st[0], st[1], st[2],
                              "https://x", "Digest")
        # Scorer path-b anchors must survive (security_advisory + neutral).
        assert "SECURITY ADVISORY" in svg
        assert ">UPDATE<" in svg
        assert svg.isascii()

    def test_unknown_severity_omits_line(self):
        # A security_advisory band with no severity must omit the line entirely.
        st = [
            _build_story(headline="malware threat advisory", subheadline="x",
                         index=0, severity_label="HIGH", action="READ"),
            _build_story(headline="update", subheadline="x", index=1,
                         severity_label="HIGH"),
            _build_story(headline="update", subheadline="x", index=2,
                         severity_label="MEDIUM"),
        ]
        # No real content -> no severity set on the stories.
        svg = render_l20_hero("2026.05.30", st[0], st[1], st[2],
                              "https://x", "Digest")
        assert "SEVERITY: TBD" not in svg
        assert "unspecified - under review" not in svg


# ---------------------------------------------------------------------------
# Honesty lockstep: scorer path-a (routed) == path-b (rendered fingerprint)
# ---------------------------------------------------------------------------
class TestHonestyLockstep:
    def test_routed_equals_fingerprinted_no_stale_render(self):
        from scripts import score_cover_honesty as sch

        # Three DISTINCT band visuals (security_advisory / market / neutral) so
        # the per-builder anchor fingerprinter can recover all three in order
        # (it records the first occurrence per visual id).
        title = "주간 보안 다이제스트"
        excerpt = ""
        filename = "2026-05-30-Tech_Security_Weekly_Digest_Botnet.md"
        summary_card = {"highlights": [
            {"source": "The Hacker News", "title": "Aeternum Botnet C2 발견",
             "severity": "🟠 High"},
            {"source": "Cointelegraph", "title": "Bitcoin $71K 급등",
             "severity": "🟡 Medium"},
            {"source": "Microsoft", "title": "Teams 업데이트 배포",
             "severity": "-"},
        ]}
        content = "- **총 뉴스 수**: 30개\n- **보안 뉴스**: 5개\n"

        # path a: routing intent
        routed = resolve_digest_band_visuals(
            title, excerpt, filename, content=content, summary_card=summary_card)

        # Build the SAME stories the generator would and render them.
        stories = [
            _build_story(headline="x", subheadline="x", index=0,
                         severity_label="HIGH", action="READ"),
            _build_story(headline="x", subheadline="x", index=1,
                         severity_label="HIGH"),
            _build_story(headline="x", subheadline="x", index=2,
                         severity_label="MEDIUM"),
        ]
        _apply_real_content(stories, {"summary_card": summary_card,
                                      "content": content})
        svg = render_l20_hero("2026.05.30", stories[0], stories[1],
                              stories[2], "https://x", "Digest")

        # path b: fingerprint the rendered SVG
        fingerprinted = sch._fingerprint_visual_ids(svg, n_bands=3)
        assert routed == fingerprinted


# ---------------------------------------------------------------------------
# Vendor+product acronym join: "AWS KY3P" must survive intact
# ---------------------------------------------------------------------------
class TestAcronymProductJoin:
    """The lead_bad guard must NOT strip a known cloud/vendor acronym when it
    is paired with a real entity in a two-token join ("AWS KY3P", "GCP IAM").
    """

    def test_aws_ky3p_preserved(self):
        """'AWS KY3P' is a recognisable vendor+product phrase and must appear
        as the headline, NOT the bare product alone ("KY3P")."""
        p = _panel_from_source_title(
            "AWS Security Blog",
            "AWS KY3P 보고서, 서드파티 공급업체 실사에 활용 가능",
        )
        assert p is not None
        assert p["headline"] == "AWS KY3P"
        assert not p.get("_src_fallback")

    def test_npm_worm_preserved(self):
        """'npm' is an acronym lead; joined with a real entity it should stay."""
        p = _panel_from_source_title(
            "The Hacker News",
            "npm Worm, 주간 패키지 공급망 공격 최신 동향",
        )
        # npm + Worm → "npm Worm" (Worm passes _is_good_headline, not generic)
        assert p is not None
        assert p["headline"] == "npm Worm"
        assert not p.get("_src_fallback")

    def test_generic_trailing_still_stripped(self):
        """A cloud/platform generic trailing word is still dropped even when
        the lead is an acronym: 'npm Linux' → lone product scan, not 'npm Linux'."""
        p = _panel_from_source_title(
            "BleepingComputer",
            "npm Linux 패키지 업데이트 권고",
        )
        # "Linux" is in _GENERIC_TRAILING → join blocked even with acronym lead.
        # The fallback scan finds no good non-acronym cap → falls back to source.
        assert p is not None
        # headline must NOT be "npm Linux"
        assert p["headline"] != "npm Linux"

    def test_lone_acronym_lead_no_second_token_still_falls_back(self):
        """A lone acronym with no second token still falls back to source."""
        p = _panel_from_source_title(
            "The Hacker News",
            "VPN 해킹 사건 발생",
        )
        # "VPN" alone → lead_bad, no good second token → source fallback
        assert p is not None
        assert p.get("_src_fallback") is True
        assert p["headline"] == "The Hacker News"


# ---------------------------------------------------------------------------
# Hero rescue: source-name hero replaced by best real-entity side card
# ---------------------------------------------------------------------------
class TestHeroRescue:
    """When panels[0] is a source-name fallback and a real-entity story exists
    in the side cards, _rescue_hero() must swap the best real-entity story into
    slot 0 (the hero)."""

    @staticmethod
    def _make_panel(headline, src_fallback=False, severity=""):
        return {
            "headline": headline,
            "subheadline": "sub",
            "severity": severity,
            "_src_fallback": src_fallback,
        }

    def test_rescue_promotes_first_real_entity(self):
        panels = [
            self._make_panel("The Hacker News", src_fallback=True),
            self._make_panel("Storm-2949"),
            self._make_panel("Exchange npm"),
        ]
        result = _rescue_hero(panels)
        assert result[0]["headline"] == "Storm-2949"
        assert result[1]["headline"] == "The Hacker News"
        assert result[2]["headline"] == "Exchange npm"

    def test_rescue_prefers_higher_severity(self):
        panels = [
            self._make_panel("BleepingComputer", src_fallback=True),
            self._make_panel("Trellix", severity=""),
            self._make_panel("ConsentFix OAuth", severity="HIGH"),
        ]
        result = _rescue_hero(panels)
        # ConsentFix OAuth has higher severity → promoted over Trellix
        assert result[0]["headline"] == "ConsentFix OAuth"

    def test_no_rescue_when_hero_is_real_entity(self):
        panels = [
            self._make_panel("Ivanti EPMM"),  # NOT a source fallback
            self._make_panel("The Hacker News", src_fallback=True),
            self._make_panel("Storm-2949"),
        ]
        result = _rescue_hero(panels)
        # Hero already real — no change
        assert result[0]["headline"] == "Ivanti EPMM"

    def test_no_rescue_when_all_are_source_fallbacks(self):
        panels = [
            self._make_panel("The Hacker News", src_fallback=True),
            self._make_panel("BleepingComputer", src_fallback=True),
            self._make_panel("AWS Security Blog", src_fallback=True),
        ]
        result = _rescue_hero(panels)
        # Nothing to promote — order unchanged
        assert result[0]["headline"] == "The Hacker News"

    def test_no_rescue_with_empty_panels(self):
        assert _rescue_hero([]) == []

    def test_src_fallback_marker_set_for_source_name_panels(self):
        """_panel_from_source_title must set _src_fallback=True when falling
        back to the ASCII source name (no usable entity in the title)."""
        p = _panel_from_source_title(
            "The Hacker News",
            "인터폴 작전 람즈, MENA 사이버범죄 네트워크 교란하며 201명 체포",
        )
        assert p is not None
        assert p.get("_src_fallback") is True
        assert p["headline"] == "The Hacker News"

    def test_real_entity_panel_has_no_src_fallback_marker(self):
        """A panel with a real entity must NOT have _src_fallback=True."""
        p = _panel_from_source_title(
            "The Hacker News",
            "Ghostwriter, 우크라이나 정부 기관 대상 Prometheus 피싱 멀웨어 공격",
        )
        assert p is not None
        assert not p.get("_src_fallback")
        # Should produce "Ghostwriter" or "Ghostwriter Prometheus"
        assert "Ghostwriter" in p["headline"]


# ---------------------------------------------------------------------------
# Integration: no May hero should be a bare source name when a real entity
# exists in the day's side cards.
# ---------------------------------------------------------------------------
class TestNoSourceNameHero:
    """End-to-end guard: for all 30 May 2026 digest posts, if the final hero
    headline is a known source-name string, at least one of the side-card
    panels must also be a source-name fallback (meaning no real entity was
    available that day — the cover is genuinely unavoidable)."""

    # Known news-source names that appear as source-fallback headlines.
    _KNOWN_SOURCES = frozenset({
        "BleepingComputer", "The Hacker News", "AWS Security Blog",
        "Microsoft Security Blog", "SecurityWeek", "Krebs on Security",
        "Dark Reading", "Threatpost", "CISA", "NIST", "Google Cloud Blog",
        "Google Security Blog", "GitHub Security Blog", "The Record",
        "Ars Technica", "Wired", "ZDNet", "TechCrunch", "Help Net Security",
        "Risky Business", "SC Magazine", "Security Boulevard", "SecurityWeek",
    })

    def _load_may_posts(self):
        import glob, re, yaml
        posts = []
        for fn in sorted(glob.glob("_posts/2026-05-*.md")):
            with open(fn) as f:
                raw = f.read()
            m = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
            if not m:
                continue
            fm = yaml.safe_load(m.group(1))
            content = raw[m.end():]
            posts.append((fn.split("/")[-1][:10], fm.get("summary_card"), content))
        return posts

    def test_no_avoidable_source_name_hero(self):
        """When the hero headline is a known source name, ALL side-card panels
        must also be source-name fallbacks (meaning there was no real entity
        available for any slot that day).  If a real-entity side card exists,
        the hero rescue should have promoted it."""
        failures = []
        for datestr, summary_card, content in self._load_may_posts():
            panels = _digest_panels(summary_card, content)
            if not panels:
                continue
            hero = panels[0]
            if hero["headline"] not in self._KNOWN_SOURCES:
                continue  # hero is a real entity — OK
            # Hero is a source name.  Check that all side cards are also src fallbacks.
            side_real = [
                p["headline"] for p in panels[1:]
                if not p.get("_src_fallback")
                and p["headline"] not in self._KNOWN_SOURCES
            ]
            if side_real:
                failures.append(
                    f"{datestr}: hero={hero['headline']!r} "
                    f"but real-entity side cards={side_real}"
                )
        assert not failures, "Avoidable source-name heroes detected:\n" + "\n".join(failures)


# ---------------------------------------------------------------------------
# Side-card rescue: generalises hero rescue to EVERY visible slot.
# A source-name fallback must not occupy a visible slot when a real-entity
# story is available anywhere in the day's candidate pool (highlights + body
# table backfill).  _rescue_hero only swaps slot 0; _digest_panels must also
# keep source-name fallbacks out of the side cards.
# ---------------------------------------------------------------------------
class TestSideCardRescue:
    def _content(self, *rows):
        head = (
            "| 분야 | 소스 | 핵심 내용 | 영향도 |\n"
            "|------|------|----------|--------|\n"
        )
        return head + "".join(f"| 🔒 Security | {s} | {t} | {sev} |\n" for s, t, sev in rows)

    def test_side_card_src_fallback_replaced_by_real_table_story(self):
        # highlight #2 has only a region word ("MENA") -> source-name fallback.
        # The body table carries additional real-entity stories, so when 3 real
        # entities exist the visible side cards must NOT show the bare source
        # name — the fallback is dropped entirely.
        summary_card = {"highlights": [
            {"source": "The Hacker News", "title": "Ivanti EPMM CVE-2026-6973 RCE 공개"},
            {"source": "The Hacker News", "title": "MENA 지역 사이버범죄 네트워크 교란 201명 체포"},
        ]}
        content = self._content(
            ("The Hacker News", "Ivanti EPMM CVE-2026-6973 RCE 공개", "🟠 High"),
            ("BleepingComputer", "WP Maps Pro 취약점 악용", "🟠 High"),
            ("The Hacker News", "CISA SolarWinds Serv-U KEV 추가", "🟡 Medium"),
        )
        panels = _digest_panels(summary_card, content)
        heads = [p["headline"] for p in panels]
        assert "The Hacker News" not in heads, heads
        # Real-entity backfill stories fill the slots instead.
        assert "Ivanti EPMM" in heads
        assert any("Maps Pro" in h or "SolarWinds" in h for h in heads)
        # No visible panel is a source-name fallback when reals are available.
        assert not any(p.get("_src_fallback") for p in panels), heads

    def test_side_card_fallback_pushed_last_when_only_two_reals(self):
        # 2 real entities + 1 source-name fallback, no extra table stories: the
        # fallback fills the trailing slot, never the middle (ahead of a real).
        summary_card = {"highlights": [
            {"source": "The Hacker News", "title": "Storm-2949 캠페인 분석"},
            {"source": "The Hacker News", "title": "MENA 지역 공격 급증"},          # src fallback
            {"source": "The Hacker News", "title": "Exchange npm 패키지 악용"},
        ]}
        panels = _digest_panels(summary_card, "")
        heads = [p["headline"] for p in panels]
        assert heads[:2] == ["Storm-2949", "Exchange npm"], heads
        assert panels[2].get("_src_fallback") is True, heads

    def test_fallback_kept_when_no_real_entity_available(self):
        # Every story has ASCII tokens that all fail _is_good_headline (a region
        # word / bare acronym) -> only source-name fallbacks exist. The cover
        # must still fill its slots (never go blank) with the fallbacks.
        summary_card = {"highlights": [
            {"source": "The Hacker News", "title": "MENA 지역 사이버범죄 네트워크 교란 201명 체포"},
            {"source": "BleepingComputer", "title": "AI 도구 악용 사례 증가"},
        ]}
        panels = _digest_panels(summary_card, "")
        assert panels, "must not be empty"
        assert all(p.get("_src_fallback") for p in panels)

    def test_real_entities_keep_editorial_order_fallback_last(self):
        # real-entity panels keep their editorial order; a source-name fallback
        # is pushed to the LAST slot, never ahead of a real story.
        summary_card = {"highlights": [
            {"source": "The Hacker News", "title": "Cisco Unified CM 취약점"},
            {"source": "The Hacker News", "title": "VPN 장비 취약점 패치 권고"},   # src fallback (VPN acronym)
            {"source": "AWS Security Blog", "title": "Amazon Cognito 설정 강화"},
        ]}
        panels = _digest_panels(summary_card, "")
        # find the first fallback index — everything before it must be real
        fb_idxs = [i for i, p in enumerate(panels) if p.get("_src_fallback")]
        if fb_idxs:
            first_fb = fb_idxs[0]
            assert all(not p.get("_src_fallback") for p in panels[:first_fb])
        heads = [p["headline"] for p in panels]
        assert heads[0] == "Cisco Unified"  # editorial lead preserved


# ---------------------------------------------------------------------------
# End-to-end guard (May + June): a source-name fallback must never appear in a
# visible slot ahead of a real-entity story for any real digest post.
# ---------------------------------------------------------------------------
class TestNoAvoidableSourceNameSideCard:
    _KNOWN_SOURCES = TestNoSourceNameHero._KNOWN_SOURCES

    def _load_posts(self, *globs):
        import glob
        import re
        import yaml
        posts = []
        for g in globs:
            for fn in sorted(glob.glob(g)):
                with open(fn) as f:
                    raw = f.read()
                m = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
                if not m:
                    continue
                fm = yaml.safe_load(m.group(1))
                posts.append((fn.split("/")[-1][:10], fm.get("summary_card"), raw[m.end():]))
        return posts

    def _is_fallback(self, p):
        return bool(p.get("_src_fallback")) or p["headline"] in self._KNOWN_SOURCES

    def test_real_entity_never_follows_a_source_name_fallback(self):
        # Reals fill the visible slots first; a source-name fallback only fills a
        # trailing slot once reals are exhausted. So a real story must NEVER
        # appear after a fallback in the rendered order.
        posts = self._load_posts("_posts/2026-05-*.md", "_posts/2026-06-*.md")
        # Sanity: the load helper must actually find posts, else the guard below
        # passes vacuously and masks a future regression.
        assert len(posts) >= 30, f"expected the May+June digest corpus, got {len(posts)}"
        failures = []
        for datestr, summary_card, content in posts:
            panels = _digest_panels(summary_card, content)
            seen_fallback = False
            for p in panels:
                if self._is_fallback(p):
                    seen_fallback = True
                elif seen_fallback:
                    failures.append(
                        f"{datestr}: real card {p['headline']!r} after a "
                        f"source-name fallback in {[q['headline'] for q in panels]}"
                    )
                    break
        assert not failures, "Avoidable source-name side cards:\n" + "\n".join(failures)


# ---------------------------------------------------------------------------
# Backfill quality (plan .omc/plans/l20-digest-backfill-quality.md): W1 table
# allowlist, W2 security-signal table ranking, W3 weak-token reject, W4
# severity-join defense.
# ---------------------------------------------------------------------------
def _table(*rows):
    """rows are (category_col1, source, title, severity_col4) tuples."""
    head = "| 분야 | 소스 | 핵심 내용 | 영향도 |\n|------|------|----------|--------|\n"
    return head + "".join(f"| {c} | {s} | {t} | {sev} |\n" for c, s, t, sev in rows)


class TestW1TableAllowlist:
    def test_admits_decorated_category_labels(self):
        content = _table(
            ("🔒 **Security**", "The Hacker News", "Ivanti EPMM RCE 취약점", "🟠 High"),
            ("⛓️ **Blockchain**", "Cointelegraph", "Arthur Hayes BTC 발언", "🟡 Medium"),
            ("💻 **Tech**", "GeekNews", "OpenAI Oracle 협력 철회", "🟡 Medium"),
            ("🔒 **Security** (7)", "BleepingComputer", "WP Maps Pro 취약점 악용", "🟠 High"),
        )
        heads = [p["headline"] for p in _digest_table_panels(content, limit=6)]
        assert "Ivanti EPMM" in heads          # Security admitted
        assert any("Arthur" in h for h in heads)  # Blockchain admitted
        assert any("OpenAI" in h for h in heads)  # Tech admitted
        assert "Maps Pro" in heads             # decorated "(7)" Security admitted

    def test_excludes_secondary_body_tables(self):
        # The highlights table is followed (after a blank line) by a SEPARATE
        # risk-summary table ("대응 긴급도"). W1 anchors parsing to the highlights
        # table only, so the secondary table's rows (incl. a "Critical Medium"
        # severity-join leak) are never parsed.
        content = _table(
            ("🔒 **Security**", "The Hacker News", "Ivanti EPMM RCE 취약점", "🟠 High"),
        ) + (
            "\n| 영역 | 현재 위험도 | 즉시 조치 |\n"
            "|------|-------------|-----------|\n"
            "| 대응 긴급도 | Critical 다수 | Critical 1건 Medium 다수 |\n"
        )
        heads = [p["headline"] for p in _digest_table_panels(content, limit=6)]
        assert heads == ["Ivanti EPMM"], heads
        assert not any("Critical" in h or "Medium" in h for h in heads)

    def test_admits_diverse_categories_incl_korean(self):
        # The highlights table legitimately uses many categories incl. Korean
        # labels — none may be dropped (the bug a 3-stem allowlist caused).
        content = _table(
            ("☁️ **Cloud**", "AWS Security Blog", "Amazon GuardDuty 업데이트", "🟡 Medium"),
            ("⚙️ **DevOps**", "The Hacker News", "Argo CD 취약점 공개", "🟠 High"),
            ("🤖 **AI/ML**", "The Hacker News", "PromptArmor LLM 가드레일", "🟡 Medium"),
            ("🔒 **보안**", "BleepingComputer", "Akira Ransomware 캠페인", "🔴 Critical"),
        )
        heads = [p["headline"] for p in _digest_table_panels(content, limit=6)]
        assert len(heads) == 4, heads  # all categories admitted, none dropped

    def test_loud_fail_corpus_has_nonempty_highlights_table(self):
        # If a future generator renames the highlights-table header, the W1
        # anchor silently empties the table and covers regress to source-name
        # fallbacks. This guard fails LOUDLY in CI instead: every real digest
        # post that contains the (category|source) header MUST yield >= 1 table
        # panel.
        import glob
        import re
        checked = 0
        failures = []
        for fn in sorted(glob.glob("_posts/2026-*.md")):
            raw = open(fn, encoding="utf-8").read()
            m = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
            if not m:
                continue
            content = raw[m.end():]
            if not re.search(r"^\|\s*(?:분야|카테고리)\s*\|\s*(?:소스|출처)\s*\|", content, re.M):
                continue  # no highlights table -> nothing to assert
            checked += 1
            if not _digest_table_panels(content, limit=6):
                failures.append(fn.split("/")[-1][:10])
        assert checked >= 100, f"expected the digest corpus, only checked {checked}"
        # A header RENAME would zero out essentially ALL header-posts at once.
        # A handful of legitimate empties (a 5-column "…|영향도|긴급도|" table
        # variant the 4-column parser skips, covered by summary_card.highlights;
        # or an all-Korean table) is expected — so the guard trips only on a
        # mass regression, not these known edge cases.
        assert len(failures) <= 5, (
            f"{len(failures)}/{checked} header-posts yielded NO table panels "
            f"(header rename / parser regression?): {failures}"
        )


class TestW34GoodHeadline:
    def test_w3_weak_trailing_single_token_rejected(self):
        for bad in ("Factories", "Critical", "Medium", "High", "Low"):
            assert _is_good_headline(bad) is False, bad

    def test_w4_severity_join_rejected(self):
        for bad in ("Critical Medium", "High Low", "Critical High Medium"):
            assert _is_good_headline(bad) is False, bad

    def test_single_severity_word_in_real_phrase_kept(self):
        # only a phrase made ENTIRELY of severity words is rejected
        assert _is_good_headline("Critical Infrastructure") is True

    def test_false_positive_guard_real_entities_kept(self):
        for good in ("Ivanti", "Veeam", "Cloudflare", "Cisco Talos",
                     "Hugging Face", "Palo Alto", "Recorded Future"):
            assert _is_good_headline(good) is True, good


class TestW2TableCategoryRanking:
    def test_security_table_row_floats_above_blockchain_tech_filler(self):
        # Thin highlights (1 real) so the side cards backfill from the table.
        # A Blockchain filler row precedes a Security row in document order;
        # the Security row must rank ahead among the table backfill (both carry
        # the same severity marker, so only the category distinguishes them).
        sc = {"highlights": [
            {"source": "The Hacker News", "title": "Storm-2949 캠페인 분석"},
        ]}
        content = _table(
            ("⛓️ **Blockchain**", "Cointelegraph", "Arthur Hayes BTC 발언", "🟡 Medium"),
            ("🔒 **Security**", "The Hacker News", "Veeam Backup RCE 취약점", "🟡 Medium"),
        )
        panels = _digest_panels(sc, content)
        heads = [p["headline"] for p in panels]
        assert heads[0] == "Storm-2949"  # editorial highlight stays the hero
        veeam = next(i for i, h in enumerate(heads) if "Veeam" in h)
        arthur = next((i for i, h in enumerate(heads) if "Arthur" in h), 99)
        assert veeam < arthur, heads  # Security floats above Blockchain filler

    def test_filler_rank_is_letter_boundary_anchored(self):
        # "FinTech"/"Biotech" CONTAIN "tech" but are on-topic — must NOT be
        # demoted as filler; bare Blockchain/Tech (any decoration) must be.
        from scripts.news.l20_dispatch import _category_rank
        assert _category_rank("💻 **FinTech**") == 0
        assert _category_rank("🧬 **Biotech**") == 0
        assert _category_rank("🔒 **Security**") == 0
        assert _category_rank("⛓️ **Blockchain**") == 1
        assert _category_rank("💻 **Tech**") == 1
        assert _category_rank("⛓️ **블록체인**") == 1

    def test_editorial_highlight_not_demoted_by_table_category(self):
        # A no-signal editorial highlight must NOT be pushed below a Security
        # table-backfill row — editorial highlights dominate the table backfill.
        sc = {"highlights": [
            {"source": "The Hacker News", "title": "JDownloader Python 패키지 악용"},
        ]}
        content = _table(
            ("🔒 **Security**", "The Hacker News", "Veeam Backup RCE 취약점", "🟡 Medium"),
        )
        panels = _digest_panels(sc, content)
        assert panels[0]["headline"].startswith("JDownloader"), [p["headline"] for p in panels]


# ---------------------------------------------------------------------------
# Weak two-token headline quality (plan
# .omc/plans/weak-two-token-headline-quality.md): FM1 clause-crossing join,
# FM2 generic-word bigram, Hangul-glue safety, and the shared-helper clause
# guard. DISPLAYED text only — visual routing + honesty scorer untouched.
# ---------------------------------------------------------------------------
class TestWeakBigramAndClause:
    def test_generic_word_rejected_as_lone_headline(self):
        # FM2 root: a lone generic capitalized English word reads as filler.
        assert _is_good_headline("Show") is False
        assert _is_good_headline("Option") is False

    def test_real_subjects_still_pass(self):
        # "Strategy" is the MSTR-rebrand entity and "Michael" is a real actor —
        # neither is generic, so both remain valid headline tokens.
        assert _is_good_headline("Strategy") is True
        assert _is_good_headline("Michael") is True

    def test_fm2_generic_bigram_not_emitted(self):
        # "Show Option" (both generic) must never surface as the headline, nor
        # may either lone generic word.
        panel = _panel_from_source_title("Cointelegraph", "Show Option 기능 노출", "")
        assert panel["headline"] not in {"Show Option", "Show", "Option"}

    def test_legit_bigram_preserved(self):
        # "Michael Saylor가 발언": the Hangul "가" abuts "Saylor"; the legit
        # person bigram must survive (no false split on the glued particle).
        panel = _panel_from_source_title("Src", "Michael Saylor가 발언", "")
        assert panel["headline"] == "Michael Saylor"

    def test_possessive_bigram_preserved_not_overfiltered(self):
        # "X의 Y" possessive joins are usually real entity bigrams and MUST be
        # kept (the generic-word reject must not over-filter these).
        assert build_lead_headline("Anthropic의 Claude Mythos 제로데이") == "Anthropic Claude"
        assert build_lead_headline("Broadcom의 VMware 인수 이후") == "Broadcom VMware"


class TestGenericHeadlineWordVetting:
    """Per-word vetting contract for ``_GENERIC_HEADLINE_WORDS``.

    Each admitted member must (a) be rejected as a LONE headline, yet (b) never
    over-filter a real story subject when it appears mid-phrase. New filler words
    are admitted only when they pass these checks against the live corpus
    (see ``TestCorpusNoGenericHero`` for the corpus-level guard).
    """

    def test_command_rejected_as_lone_headline(self):
        # "Command" joins "show"/"option" from the same GeekNews macOS
        # keyboard-key line ("Show GN: 오른쪽 Option / Command 키...").
        assert "command" in _GENERIC_HEADLINE_WORDS
        assert _is_good_headline("Command") is False

    def test_command_bigram_with_real_token_preserved(self):
        # The lone reject must NOT kill a real "Command <Noun>" story phrase:
        # only the bare filler word is generic, not the bigram.
        assert build_lead_headline("Command Injection 취약점 공개") == "Command Injection"
        assert build_lead_headline("Command Center 운영 사례") == "Command Center"

    def test_geeknews_keyboard_line_yields_no_filler(self):
        # The real source line that produced show/option/command must resolve to
        # NONE of the three filler words (it has no real ASCII story subject).
        title = "Show GN: 오른쪽 Option / Command 키로 한/영 전환"
        assert build_lead_headline(title) not in {
            "Show",
            "Option",
            "Command",
            "Show Option",
            "Show Command",
            "Option Command",
        }

    def test_adjective_of_ai_words_deferred_not_admitted(self):
        # "agentic"/"vertical" are the deferred adjective+"AI" case (FM2), NOT
        # clean filler — they are intentionally NOT in the generic set. Guard
        # against a well-meaning future edit folding them in here, which would
        # degrade real "Agentic AI" (HashiCorp/AWS/NVIDIA) covers to empty
        # fallthrough instead of fixing them properly.
        assert "agentic" not in _GENERIC_HEADLINE_WORDS
        assert "vertical" not in _GENERIC_HEADLINE_WORDS


class TestCvssLeadReject:
    """``cvss`` is the severity-SCALE label, never a story subject.

    A highlight title that leads with a severity metric ("CVSS 9.9 - ...")
    carries its real subject in the source/body. Admission criteria mirror
    ``TestGenericHeadlineWordVetting``: (a) rejected as a LONE headline, (b)
    never the lead of a bigram, (c) the panel falls through to the source
    entity instead of rendering a bare "CVSS" / "CVSS JavaScript" hero.
    """

    def test_cvss_rejected_as_lone_headline(self):
        assert _is_good_headline("CVSS") is False

    def test_cvss_led_bigram_does_not_lead(self):
        # "CVSS 9.9 - JavaScript ..." must not yield "CVSS" or "CVSS JavaScript";
        # the next real token wins (2026-01-29).
        h = build_lead_headline(
            "CVSS 9.9 - JavaScript AST sandbox escape, Function constructor bypass"
        )
        assert h not in {"CVSS", "CVSS JavaScript"}
        assert "CVSS" not in h
        assert h == "JavaScript"

    def test_cvss_only_ascii_title_yields_empty(self):
        # Korean body after the metric → no ASCII entity → empty, so the panel
        # builder falls through to the source (2026-01-27).
        assert build_lead_headline("CVSS 7.8 긴급 패치 - 보안 기능 우회 취약점 실제 악용 중") == ""

    def test_cve_bearing_source_supplies_real_hero_not_demoted(self):
        # The lead highlight of 2026-01-27: title is a bare metric, but the
        # CVE-bearing source is the real advisory subject. The panel must carry
        # a real entity headline, NOT "CVSS", and must NOT be flagged
        # _src_fallback (which would demote the lead off the hero slot).
        p = _panel_from_source_title(
            "MS Office Zero-Day (CVE-2026-21509)",
            "CVSS 7.8 긴급 패치 - 보안 기능 우회 취약점 실제 악용 중",
        )
        assert p is not None
        assert "CVSS" not in p["headline"]
        assert p["headline"]  # non-empty real entity
        assert not p.get("_src_fallback"), "CVE-bearing source subject must not be demoted"
        # CVE surfaces in the subheadline; route stays the honest advisory class.
        assert "CVE-2026-21509" in p["subheadline"]
        assert p["route_hint"] == "Security advisory"


class TestUrlBigramReject:
    """Per-word vetting contract for adding ``url`` to ``_GENERIC_TRAILING``.

    'url' is a generic format noun, never a story subject — same role as the
    pre-existing 'api'/'web'. Admission criteria mirror
    ``TestGenericHeadlineWordVetting``: (a) rejected as a LONE headline, (b)
    dropped as a trailing bigram token so a junk "<Acronym> URL" never renders,
    yet (c) it must not over-filter any real story subject.
    """

    def test_url_in_generic_trailing(self):
        from scripts.news.l20_dispatch import _GENERIC_TRAILING
        assert "url" in _GENERIC_TRAILING

    def test_url_rejected_as_lone_headline(self):
        assert _is_good_headline("URL") is False

    def test_fbi_url_junk_bigram_dropped(self):
        # 06-15 real title. "FBI" (3 chars) is too short to be a lone headline
        # and "URL" is now generic-trailing, so the junk bigram "FBI URL" no
        # longer renders — build_lead_headline yields "" and the caller falls
        # back to the source (demoted to a side card), surfacing real stories.
        title = "FBI, 백만 개 URL 사용한 대규모 AI 기반 피싱 서비스 무력화"
        h = build_lead_headline(title)
        assert h != "FBI URL"
        assert "URL" not in h

    def test_fbi_url_highlight_demoted_to_source_fallback(self):
        p = _panel_from_source_title(
            "BleepingComputer", "FBI, 백만 개 URL 사용한 대규모 AI 기반 피싱 서비스 무력화"
        )
        assert p is not None
        assert p.get("_src_fallback") is True

    def test_url_does_not_over_filter_real_bigrams(self):
        # The reject must only touch the generic 'url' token; real product /
        # vendor bigrams are unaffected (regression guard).
        assert build_lead_headline("Cisco Unified Communications 취약점") == "Cisco Unified"
        assert build_lead_headline("Oracle WebLogic KEV 등재") == "Oracle WebLogic"
        assert build_lead_headline("Google Vertex AI SDK 결함") == "Google Vertex"


class TestRoundupAndSuffixReject:
    """FM3: two narrow, corpus-vetted join rejects (each blast-radius 1 cover).

    (a) Korean roundup-list headline ("<Lead> ... 외 N건"): the entity tokens
        after the lead are UNRELATED list items, so the join glues a nonsense
        bigram. Keep only the lead entity.
    (b) Redundant suffix restatement (token2 is the tail of token1, e.g.
        "GreatXML" + "XML"): the prefix near-dup guard misses it. Drop token2.

    Both titles below are REAL 2026-06 corpus highlight titles. Regression
    guards prove neither rule over-filters a normal two-entity story.
    """

    def test_roundup_list_keeps_lead_only(self):
        # 06-19 real title. "ThreatsDay 게시판: Claude ..., NastyC2 ... 외 25건"
        # — Claude/NastyC2 are separate list items, not a phrase with ThreatsDay.
        title = "ThreatsDay 게시판: Claude 채팅 악용, NastyC2 npm 패키지, 디바이스 코드 피싱 외 25건"
        assert build_lead_headline(title) == "ThreatsDay"

    def test_suffix_redundant_join_dropped(self):
        # 06-12 real title. "GreatXML" + "XML" is a redundant suffix restatement.
        title = "새로운 GreatXML 익스플로잇, 복구 파티션 XML 파일을 통해 Windows BitLocker 우회"
        assert build_lead_headline(title) == "GreatXML"

    def test_roundup_does_not_over_filter_normal_story(self):
        # No "외 N건" tail -> normal two-entity join is untouched.
        assert build_lead_headline("Cisco, Unified CM의 CVE-2026-20230 패치") == "Cisco Unified"

    def test_suffix_reject_does_not_touch_acronym_led_event(self):
        # "SAP SAPPHIRE": the SHORT token leads (prefix relation), so the
        # suffix-only guard must NOT fire — the real event name is preserved.
        assert (
            build_lead_headline("SAP SAPPHIRE 2026: Google Cloud 에이전틱 비전 공개")
            == "SAP SAPPHIRE"
        )


class TestMultiWordVendorPromote:
    """FM4: a resolved lead that TRUNCATES a curated multi-word vendor entity is
    promoted to the full entity when that entity is literally present in the
    title ("Miasma Red" -> "Red Hat", "AWS Amazon"/lone "Amazon" -> "Amazon
    Bedrock"). Curated allowlist (_MW_VENDOR_ENTITIES), NOT a positional
    heuristic — a "<token> <Capitalized>" rule flags ~134 covers (~132 real
    two-entity stories). All firing titles below are REAL corpus highlight
    titles. Display-text only: routing (route_hint) and honesty class unchanged.
    """

    def test_aws_amazon_bigram_promoted(self):
        # 2026-04-21 real highlight: "AWS Amazon" truncates "Amazon Bedrock".
        assert (
            build_lead_headline(
                "AWS 위클리 라운드업: Amazon Bedrock의 Claude Opus 4.7, AWS Internal 업데이트"
            )
            == "Amazon Bedrock"
        )

    def test_miasma_red_bigram_promoted(self):
        # 2026-06-02 real highlight: "Miasma Red" truncates "Red Hat".
        assert (
            build_lead_headline(
                "Miasma 공급망 공격, 자격증명 탈취 웜으로 Red Hat npm 패키지 손상"
            )
            == "Red Hat"
        )

    def test_lone_amazon_promoted(self):
        # 2026-04-27 real highlight: lone "Amazon" (no bigram) also promotes when
        # "Amazon Bedrock" is literally in the title.
        assert (
            build_lead_headline(
                "에이전틱 AI와 Amazon Bedrock AgentCore를 활용한 전문가 팀 시뮬레이션"
            )
            == "Amazon Bedrock"
        )

    def test_arch_linux_promoted(self):
        # FM5: 06-13/06-15 real highlights. "linux" in _GENERIC_TRAILING strips
        # to a lone "Arch"; "Arch Linux" is a real distro entity in the title.
        assert (
            build_lead_headline(
                "400개 이상의 Arch Linux AUR 패키지가 하이재킹되어 정보 탈취 악성코드 유포"
            )
            == "Arch Linux"
        )
        assert (
            build_lead_headline(
                "Arch Linux, 이제 악성코드 사고가 통제됐다고 판단: 1,500개 이상 패키지 영향"
            )
            == "Arch Linux"
        )

    def test_malware_plus_linux_not_promoted(self):
        # CRITICAL: NOT a blanket "<X> Linux" promote. "Showboat"/"CIFSwitch" are
        # the malware/vuln (the real subject); "Linux" is just the platform, so
        # the lone lead is CORRECT and must NOT promote to a fabricated entity.
        assert (
            build_lead_headline(
                "Showboat Linux 악성코드, SOCKS5 프록시 백도어로 중동 통신사 공격"
            )
            == "Showboat"
        )
        assert (
            build_lead_headline(
                "새로운 CIFSwitch Linux 취약점으로 여러 배포판에서 루트 권한 획득 가능"
            )
            == "CIFSwitch"
        )

    def test_full_entity_lead_is_idempotent(self):
        # Promoting an already-full entity is a no-op (no double-promote).
        assert build_lead_headline("Amazon Bedrock AgentCore가 출시") == "Amazon Bedrock"

    def test_no_promote_without_literal_full_entity(self):
        # "Amazon" with NO "Amazon Bedrock" in the title must NOT fabricate it.
        assert build_lead_headline("Amazon, 새로운 클라우드 보안 기능 발표") != "Amazon Bedrock"

    def test_unseeded_vendor_untouched(self):
        # "Palo Alto" is not seeded this PR → normal lead-join, unchanged.
        assert build_lead_headline("Palo Alto GlobalProtect VPN 취약점 공개") == "Palo Alto"

    def test_normal_two_entity_untouched(self):
        assert build_lead_headline("Cisco, Unified CM의 CVE-2026-20230 패치") == "Cisco Unified"

    def test_sap_sapphire_untouched(self):
        # FM3 regression guard still holds under FM4.
        assert (
            build_lead_headline("SAP SAPPHIRE 2026: Google Cloud 에이전틱 비전 공개")
            == "SAP SAPPHIRE"
        )

    def test_promoted_headlines_route_neutral(self):
        # Both promoted full entities carry no attack-class claim — honesty-safe.
        assert route_visual_id("Amazon Bedrock") == "neutral"
        assert route_visual_id("Red Hat") == "neutral"


class TestMultiWordVendorVetting:
    """Self-healing corpus guard for FM4 (mirrors TestCorpusNoLoneAdjectiveAi).

    Seed is EXACTLY the two live-firing pairs this PR (no forward-looking
    entries). The corpus invariant is PROPERTY-based, not a fixed count: daily
    auto-published digests must not break it — only an ILLEGITIMATE promote
    (full entity not literally in the title, or a non-seeded result) fails. This
    converts allowlist-rot from silent to CI-blocking without coupling the test
    to the (growing) corpus size.
    """

    def test_seed_is_exactly_the_curated_pairs(self):
        from scripts.news.l20_dispatch import _MW_VENDOR_ENTITIES

        # FM4: red hat, amazon bedrock; FM5: arch linux — each a real entity with
        # a live exercising cover, no unexercised forward-looking entries.
        assert _MW_VENDOR_ENTITIES == frozenset(
            {("red", "hat"), ("amazon", "bedrock"), ("arch", "linux")}
        )

    def test_heads_disjoint_from_generic_trailing(self):
        from scripts.news.l20_dispatch import _GENERIC_TRAILING, _MW_VENDOR_ENTITIES

        for head, _tail in _MW_VENDOR_ENTITIES:
            assert head not in _GENERIC_TRAILING

    def test_every_corpus_promote_is_legitimate(self):
        # Walk every summary_card highlight title; for each, compute the lead WITH
        # and WITHOUT the promote rule. Every delta MUST be a legitimate promote:
        # the full entity is literally in the title AND the new lead is a seeded
        # full entity. Also a positive control: the two named live defects fire.
        import glob
        import re as _re

        import yaml as _yaml

        from scripts.news import l20_dispatch as _L

        seeded_full = {f"{h.title()} {t.title()}" for h, t in _L._MW_VENDOR_ENTITIES}
        illegitimate = []
        fired_dates = set()
        orig = _L._promote_mw_vendor
        try:
            for fn in sorted(glob.glob("_posts/*.md")):
                raw = open(fn).read()
                m = _re.match(r"^---\n(.*?)\n---\n", raw, _re.DOTALL)
                if not m:
                    continue
                sc = (_yaml.safe_load(m.group(1)) or {}).get("summary_card")
                if not isinstance(sc, dict):
                    continue
                for hl in sc.get("highlights", []) or []:
                    title = hl.get("title", "") or ""
                    new = _L.build_lead_headline(title)
                    _L._promote_mw_vendor = lambda c, t: ""
                    try:
                        old = _L.build_lead_headline(title)
                    finally:
                        _L._promote_mw_vendor = orig
                    if new == old:
                        continue
                    fired_dates.add(fn.split("/")[-1][:10])
                    if new not in seeded_full or new.lower() not in title.lower():
                        illegitimate.append(f"{fn.split('/')[-1][:10]}: {old!r}->{new!r} <- {title[:50]!r}")
        finally:
            _L._promote_mw_vendor = orig
        assert not illegitimate, "Illegitimate FM4 promote(s):\n" + "\n".join(illegitimate)
        # positive control: the two named live defects are actually fixed
        assert {"2026-06-02", "2026-04-21"}.issubset(fired_dates), fired_dates


class TestAiCompoundHeadline:
    """FM2: '<CompoundAdjective> AI' (Agentic AI / Vertical AI) must survive as an
    honest bigram instead of collapsing to a lone weak adjective. 'ai' is in
    _GENERIC_TRAILING (so '<Foo> AI' -> 'Foo'); _AI_COMPOUND_ADJECTIVES is the
    narrow, corpus-vetted override. All titles below are REAL corpus highlight
    titles (see .omc/plans/fm2-ai-compound-adjective.md)."""

    def test_agentic_ai_real_titles_kept_as_bigram(self):
        for title in (
            "Agentic AI 시스템의 Zero Trust NHI(비인간 ID) 관리 가이드 발표",
            "Agentic AI 기반 통신 자율 네트워크 + AI-RAN 상용화 실증",
            "Agentic AI 플랫폼: MCP Registry로 에이전트 도구 통합 관리",
        ):
            assert build_lead_headline(title) == "Agentic AI", title

    def test_vertical_ai_real_titles_kept_as_bigram(self):
        for title in (
            "사이버보안 특화 Vertical AI 구축 방안 분석",
            "Vertical AI 구축 — 보안 특화 AI로 위협 탐지 오탐률 감소, SOC 자동화 가속",
        ):
            assert build_lead_headline(title) == "Vertical AI", title

    def test_double_ai_does_not_triple(self):
        # tokens=[Vertical, AI, AI, SOC] — the join takes only [0]+[1], never "Vertical AI AI".
        assert (
            build_lead_headline(
                "Vertical AI 구축 — 보안 특화 AI로 위협 탐지 오탐률 감소, SOC 자동화 가속"
            )
            == "Vertical AI"
        )

    def test_branch_does_not_fire_when_adjective_not_lead(self):
        # Real negative: a stronger entity precedes the adjective -> the AI-compound
        # branch must NOT fire; the strong lead wins (proves the branch is gated on
        # non_cve[0], not on the mere presence of '<adj> AI').
        assert build_lead_headline("OWASP Agentic AI 프레임워크, Kubernetes 보안 확인") == "OWASP Agentic"

    def test_arbitrary_adjective_ai_still_strips(self):
        # A >=4-char, non-allowlisted lead adjective + "AI" must NOT join into a
        # bigram (only curated qualifiers do). It falls back to the lone token.
        assert build_lead_headline("Responsible AI 거버넌스 프레임워크") == "Responsible"

    def test_generalized_join_would_wreck_proper_noun_fragments(self):
        # Why an allowlist, not a generalized "<Cap> AI" rule: these real titles
        # must keep their proper-noun lead, never become "Gordon AI"/"Mythos AI".
        assert build_lead_headline("Ask Gordon AI 비서의 이미지 메타데이터 기반 코드 실행 취약점") == "Ask Gordon"
        assert build_lead_headline("Claude Mythos AI, 10,000개의 높은 심각도 결함 발견") == "Claude Mythos"


class TestAiCompoundAdjectiveVetting:
    """Per-word vetting + structural invariants for _AI_COMPOUND_ADJECTIVES
    (mirrors TestGenericHeadlineWordVetting)."""

    def test_seed_membership(self):
        assert _AI_COMPOUND_ADJECTIVES == frozenset({"agentic", "vertical"})

    def test_each_member_produces_good_bigram(self):
        # Every allowlist member must yield an _is_good_headline bigram when joined
        # to "AI" (keeps the list honest: no member that would render as junk).
        for adj in _AI_COMPOUND_ADJECTIVES:
            bigram = f"{adj.title()} AI"
            assert _is_good_headline(bigram), bigram

    def test_disjoint_from_generic_headline_words(self):
        # A word must never be in both sets (contradictory routing).
        assert _AI_COMPOUND_ADJECTIVES.isdisjoint(_GENERIC_HEADLINE_WORDS)

    def test_disjoint_from_deferred(self):
        # Shadow et al. are deferred (structurally distinct), never silently
        # promoted into the join allowlist (that would be a no-op guard-silencer).
        assert _AI_COMPOUND_ADJECTIVES.isdisjoint(_DEFERRED_AI_ADJECTIVES)


class TestCorpusNoLoneAdjectiveAi:
    """Self-healing guard: no committed digest panel may emit a lone adjective
    immediately followed by a standalone 'AI' in its source title unless that
    adjective is in _AI_COMPOUND_ADJECTIVES (would be a join bug) or explicitly
    deferred in _DEFERRED_AI_ADJECTIVES (a structurally-distinct known case).
    Converts allowlist-rot from silent to CI-blocking. Scope: the L20
    summary_card highlight corpus; the rollup path shares build_lead_headline and
    is covered separately by TestRollupLeadParity."""

    def test_no_unvetted_lone_adjective_ai_panel(self):
        import glob
        import html as _html_mod
        import re as _re
        import yaml as _yaml

        offenders = []
        for fn in sorted(glob.glob("_posts/*.md")):
            with open(fn) as f:
                raw = f.read()
            m = _re.match(r"^---\n(.*?)\n---\n", raw, _re.DOTALL)
            if not m:
                continue
            fm = _yaml.safe_load(m.group(1))
            sc = fm.get("summary_card")
            if not isinstance(sc, dict):
                continue
            for hl in sc.get("highlights", []) or []:
                title = hl.get("title", "") or ""
                lead = build_lead_headline(title)
                if not lead or " " in lead:
                    continue
                # literal title adjacency "<lead> AI" (AI standalone, not "OpenAI")
                if _re.search(rf"\b{_re.escape(lead)}\s+AI\b", _html_mod.unescape(title)):
                    low = lead.lower()
                    if low in _AI_COMPOUND_ADJECTIVES or low in _DEFERRED_AI_ADJECTIVES:
                        continue
                    offenders.append(f"{fn.split('/')[-1][:10]}: lone {lead!r} <- {title[:60]!r}")
        assert not offenders, (
            "Unvetted lone-adjective+AI panel(s) — add the adjective to "
            "_AI_COMPOUND_ADJECTIVES (if the join fixes the cover) or "
            "_DEFERRED_AI_ADJECTIVES (if structurally distinct):\n"
            + "\n".join(offenders)
        )


class TestRollupLeadParity:
    """draft_rollup_spec.lead_entity must produce the same headline as the L20
    panel path for the same title (one shared join helper, no drift)."""

    PARITY_TITLES = [
        "Strategy의 Michael Saylor, BTC 매수",
        "Show Option 기능 노출",
        "Michael Saylor가 발언",
        "Arthur Hayes 발언",
        "Ivanti EPMM 취약점",
        "Cisco Catalyst 결함",
        "Mirai ADB 봇넷",
        "Hugging Face 모델",
        "AWS KY3P 발표",
        "npm Worm 공격",
        "Maps Pro 출시",
        "Cisco Unified 패치",
        # FM2: the AI-compound join is in the shared helper, so the rollup tag
        # inherits it — these must produce "Agentic AI" / "Vertical AI" on BOTH paths.
        "Agentic AI 시스템의 Zero Trust NHI 관리 가이드 발표",
        "사이버보안 특화 Vertical AI 구축 방안 분석",
    ]

    def test_lead_entity_matches_shared_helper(self):
        # Both the L20 panel join and the rollup tag delegate to the SHARED
        # build_lead_headline, so they agree on the non-CVE path by design.
        from scripts.draft_rollup_spec import lead_entity

        for title in self.PARITY_TITLES:
            shared = build_lead_headline(title)
            assert lead_entity(title) == shared, title

    def test_fm2_ai_compound_inherited_by_rollup(self):
        # Explicit: the rollup path yields the FM2 bigram, not a lone adjective.
        from scripts.draft_rollup_spec import lead_entity

        assert lead_entity("사이버보안 특화 Vertical AI 구축 방안 분석") == "Vertical AI"
        assert lead_entity("Agentic AI 플랫폼: MCP Registry로 도구 통합") == "Agentic AI"

    def test_cve_only_title_diverges_as_designed(self):
        # The one intentional divergence: a CVE-only title has no non-CVE entity,
        # so the shared helper returns "" and each caller applies its own CVE
        # fallback — the rollup tag uses the CVE id (toks[0]).
        from scripts.draft_rollup_spec import lead_entity

        cve_only = "CVE-2026-1234 단독 권고"
        assert build_lead_headline(cve_only) == ""
        assert lead_entity(cve_only) == "CVE-2026-1234"


class TestCorpusNoGenericHero:
    """Output-level corpus guard: no live digest hero/side-card headline is a
    lone _GENERIC_HEADLINE_WORDS member. Asserts on dict outputs, NOT SVG."""

    def _load_posts(self, *globs):
        import glob
        import re
        import yaml

        posts = []
        for g in globs:
            for fn in sorted(glob.glob(g)):
                with open(fn) as f:
                    raw = f.read()
                m = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
                if not m:
                    continue
                fm = yaml.safe_load(m.group(1))
                posts.append(
                    (fn.split("/")[-1][:10], fm.get("summary_card"), raw[m.end():])
                )
        return posts

    def test_no_generic_word_hero_or_side_card(self):
        posts = self._load_posts("_posts/2026-05-*.md", "_posts/2026-06-*.md")
        assert len(posts) >= 30, f"expected the May+June digest corpus, got {len(posts)}"
        failures = []
        for datestr, summary_card, content in posts:
            for p in _digest_panels(summary_card, content):
                if p["headline"].lower() in _GENERIC_HEADLINE_WORDS:
                    failures.append(
                        f"{datestr}: generic-word headline {p['headline']!r}"
                    )
        assert not failures, "Generic-word covers:\n" + "\n".join(failures)


class TestTopicCoverTheme:
    """The digest gallery was uniformly blue because the neutral hero band
    hard-mapped to ``blue``. ``theme_for_topics`` now keys a per-cover identity
    color to the post's content, and ``_apply_real_content`` recolors the
    neutral hero to it. Palette only -> honesty class unchanged."""

    def test_theme_for_topics_specific_first(self):
        from scripts.news.l20_dispatch import theme_for_topics

        # A threat topic wins over the ubiquitous "AI" generic token.
        assert theme_for_topics(
            "2026-04-02-Tech_Security_Weekly_Digest_AI_Malware.md"
        ) == "red"
        # CVE / patch -> amber.
        assert theme_for_topics(
            "2026-04-03-Tech_Security_Weekly_Digest_CVE_Patch_AWS_AI.md"
        ) == "amber"
        # Crypto / blockchain -> green.
        assert theme_for_topics(
            "2026-05-25-Tech_Security_Weekly_Digest_AI_Ethereum_Blockchain.md"
        ) == "green"
        # Named infra/vendor -> blue.
        assert theme_for_topics(
            "2026-04-20-Tech_Security_Weekly_Digest_AI_Apple_AWS_Palantir.md"
        ) == "blue"

    def test_theme_for_topics_generic_fallback(self):
        from scripts.news.l20_dispatch import theme_for_topics

        # Only generic tokens present -> generic tier decides (aws -> blue).
        assert theme_for_topics(
            "2026-01-01-Tech_Security_Weekly_Digest_AWS_Cloud.md"
        ) == "blue"
        # No mappable token at all -> blue default.
        assert theme_for_topics("2026-01-01-Tech_Security_Weekly_Digest.md") == "blue"

    def test_title_fallback_word_boundary_no_misfire(self):
        from scripts.news.l20_dispatch import theme_for_topics

        # Empty filename -> no slug tokens -> title fallback path. Short specific
        # keys must NOT match inside unrelated words ("rat" in integration,
        # "go" in Google, "rce" in source).
        assert theme_for_topics("", "Cloud Migration Integration Guide") == "blue"
        assert theme_for_topics("", "Google adapter rollout") == "blue"
        # A real whole-word specific token in the title still maps.
        assert theme_for_topics("", "Ransomware roundup") == "red"

    def test_neutral_hero_adopts_cover_theme(self):
        # A neutral hero band must take the supplied cover_theme, not blue.
        hero = _build_story(
            headline="Ecosystem Update", subheadline="x", index=0,
            severity_label="HIGH", action="READ THE FULL DIGEST",
        )
        side1 = _build_story(headline="update", subheadline="x", index=1,
                             severity_label="HIGH")
        side2 = _build_story(headline="update", subheadline="x", index=2,
                             severity_label="MEDIUM")
        stories = [hero, side1, side2]
        _apply_real_content(stories, {"content": ""}, cover_theme="red")
        # Hero is neutral (no post content) -> recolored red.
        assert stories[0]["visual"] == "neutral"
        assert stories[0]["theme"] == "red"
        # Side cards keep their semantic (blue) theme -> intra-cover contrast.
        assert stories[1]["theme"] == "blue"

    def test_cover_theme_does_not_change_claim_class(self):
        # Recoloring is palette-only: the hero stays the neutral claim class
        # regardless of the cover_theme passed.
        for theme in ("red", "amber", "green", "purple", "blue"):
            hero = _build_story(headline="Ecosystem Update", subheadline="x",
                                index=0, severity_label="HIGH", action="GO")
            _apply_real_content([hero], {"content": ""}, cover_theme=theme)
            assert hero["visual"] == "neutral"
            assert hero["theme"] == theme

    def test_security_advisory_hero_adopts_cover_theme(self):
        # An advisory-shield hero (security_advisory) must adopt the topic theme
        # so the gallery is not a wall of identical amber shields. The class is
        # unchanged (palette only) -> honesty gate unaffected.
        hero = _build_story(headline="Security Advisory", subheadline="x",
                            index=0, severity_label="HIGH", action="READ")
        assert hero["visual"] == "security_advisory"  # routed before recolor
        _apply_real_content([hero], {"content": ""}, cover_theme="red")
        assert hero["visual"] == "security_advisory"  # class preserved
        assert hero["theme"] == "red"                 # palette recolored

    def test_build_story_advisory_hero_recolor(self):
        # _build_story path (pre-real-content) also recolors an advisory hero.
        hero = _build_story(headline="Security Advisory", subheadline="x",
                            index=0, severity_label="HIGH", action="READ",
                            cover_theme="green")
        assert hero["visual"] == "security_advisory"
        assert hero["theme"] == "green"
        # A side advisory band (index>=1) is NOT recolored by cover_theme.
        side = _build_story(headline="Security Advisory", subheadline="x",
                            index=1, severity_label="HIGH", cover_theme="green")
        assert side["theme"] != "green" or side["visual"] != "security_advisory"


# ---------------------------------------------------------------------------
# Generic-pool hero regression: a digest whose real lead story lives ONLY in
# summary_card.highlights (NO body | 분야 | 소스 | table) used to render the
# generic-pool placeholder ("Security Update") as the hero, because the cron
# path passed only the raw content and never parsed summary_card. The shared
# parser (load_post_fields) now surfaces the editorial lead story on the cron
# and regen paths. See .omc/plans/l20-digest-hero-generic-pool-fix.md.
# ---------------------------------------------------------------------------
_GENERIC_POOL = {"Security Update", "Threat Analysis", "Patch Advisory"}

# Hero headline <text> in render_l20_hero: x=54 y=146, the 31px/800 title.
_HERO_TEXT_RE = re.compile(
    r'<text x="54" y="146"[^>]*font-size="31"[^>]*>([^<]*)</text>'
)


def _render_cron(post_info: dict) -> str:
    """Render an L20 digest cover the way the cron path does, in-process.

    Mirrors auto_publish_news._render_l20_svg_string: build 3 bands, parse the
    in-memory front matter's summary_card via the SHARED parser, then override
    displayed content. Kept here (not importing the app module) so the test
    asserts the l20_dispatch builders + shared parser directly.
    """
    title = str(post_info.get("title", "") or "")
    excerpt = str(post_info.get("excerpt", "") or "")
    filename = str(post_info.get("filename", "") or "")
    cover_theme = theme_for_topics(filename, title)
    h, tr, br = extract_three_stories(title, excerpt)
    hero = _build_story(headline=h["headline"], subheadline=h["subheadline"],
                        index=0, severity_label="HIGH",
                        action=_action_for(h["headline"]), cover_theme=cover_theme)
    tr_s = _build_story(headline=tr["headline"], subheadline=tr["subheadline"],
                        index=1, severity_label="HIGH")
    br_s = _build_story(headline=br["headline"], subheadline=br["subheadline"],
                        index=2, severity_label="MEDIUM")
    post_info["summary_card"] = (
        load_post_fields(text=post_info.get("content", "")) or (None, None)
    )[1]
    _apply_real_content([hero, tr_s, br_s], post_info, cover_theme=cover_theme)
    return render_l20_hero(
        date_str="2026.02.04", hero=hero, top_right=tr_s, bottom_right=br_s,
        url="https://tech.2twodragon.com/", post_title="Weekly Digest",
    )


# A digest with summary_card.highlights and NO body | 분야 | 소스 | table —
# the table-less class that exposed the bug (5 of the 8 affected covers).
_TABLELESS_DIGEST = (
    "---\n"
    "layout: post\n"
    "title: '주간 보안 다이제스트: 제로데이 DNS 유출 AI 에이전트'\n"
    "summary_card:\n"
    "  highlights:\n"
    "    - { source: \"Docker DockerDash\", title: \"Ask Gordon AI 비서 코드 실행 취약점 패치\" }\n"
    "    - { source: \"CVE-2025-11953\", title: \"React Native CLI Metro4Shell RCE - CVSS 9.8\" }\n"
    "    - { source: \"AWS IAM Identity Center\", title: \"멀티리전 복제 지원 보안 아키텍처 영향\" }\n"
    "---\n"
    "본문에 분야/소스 하이라이트 표가 없는 초기 다이제스트 형식입니다.\n"
)


class TestGenericPoolHeroFix:
    def _info(self):
        return {
            "title": "주간 보안 다이제스트: 제로데이 DNS 유출 AI 에이전트",
            "excerpt": "이번 주 보안 소식 정리",
            "filename": "2026-02-04-Tech_Security_Weekly_Digest_AI_Docker_Data_Go.md",
            "content": _TABLELESS_DIGEST,
        }

    def test_tableless_summary_card_hero_is_real_not_generic(self):
        # (a) The rendered hero <text> must NOT be a generic-pool placeholder,
        # and must equal the editorial lead highlight's resolved entity.
        sc = load_post_fields(text=_TABLELESS_DIGEST)[1]
        assert isinstance(sc, dict) and sc.get("highlights")
        lead = _digest_panels(sc, "")[0]["headline"]
        assert lead not in _GENERIC_POOL  # sanity: the panel resolves a real entity

        svg = _render_cron(self._info())
        m = _HERO_TEXT_RE.search(svg)
        assert m is not None, "hero <text> not found in rendered SVG"
        hero_text = m.group(1)
        assert hero_text not in _GENERIC_POOL, (
            f"hero rendered a generic-pool placeholder: {hero_text!r}"
        )
        assert hero_text == lead, (
            f"hero {hero_text!r} != editorial lead entity {lead!r}"
        )
        assert _is_ascii(hero_text)

    def test_honesty_lockstep_after_override(self):
        # (b) The scorer's replay (resolve_digest_band_visuals) must return the
        # SAME band visuals the generator sets on the stories via
        # _apply_real_content — no spurious STALE_RENDER on the regenerated cover.
        info = self._info()
        sc = load_post_fields(text=info["content"])[1]
        title, excerpt, filename = info["title"], info["excerpt"], info["filename"]

        cover_theme = theme_for_topics(filename, title)
        h, tr, br = extract_three_stories(title, excerpt)
        stories = [
            _build_story(headline=h["headline"], subheadline=h["subheadline"],
                         index=0, severity_label="HIGH",
                         action=_action_for(h["headline"]), cover_theme=cover_theme),
            _build_story(headline=tr["headline"], subheadline=tr["subheadline"],
                         index=1, severity_label="HIGH"),
            _build_story(headline=br["headline"], subheadline=br["subheadline"],
                         index=2, severity_label="MEDIUM"),
        ]
        post_info = dict(info)
        post_info["summary_card"] = sc
        _apply_real_content(stories, post_info, cover_theme=cover_theme)

        replay = resolve_digest_band_visuals(title, excerpt, filename, "", sc)
        assert [s["visual"] for s in stories] == replay

    def test_parser_parity_path_vs_text_real_post(self):
        # (c) load_post_fields(path=P) and load_post_fields(text=P.read_text())
        # must agree for a real post, so cron (text) and regen (path) parse the
        # summary_card identically (no generator/scorer divergence).
        import glob
        sample = None
        for fn in sorted(glob.glob("_posts/2026-02-*.md")):
            fields = load_post_fields(path=__import__("pathlib").Path(fn))
            if fields and isinstance(fields[1], dict) and fields[1].get("highlights"):
                sample = fn
                break
        assert sample is not None, "no real digest post with highlights found"
        from pathlib import Path as _P
        by_path = load_post_fields(path=_P(sample))
        by_text = load_post_fields(text=_P(sample).read_text(encoding="utf-8"))
        assert by_path is not None and by_text is not None
        assert by_path[1] == by_text[1]  # identical summary_card


# ---------------------------------------------------------------------------
# Content-cover honest KPI fallback (_content_format_word / _content_side_kpi)
# ---------------------------------------------------------------------------
# L20 CONTENT covers (guides/courses/research) have no incident metric, so a
# side KPI card whose headline yields no real figure used to render the
# "TBD / STATUS / NEW" placeholder. _content_side_kpi supplies an honest,
# post-derived descriptor (content FORMAT + publish YEAR) instead.
class TestContentFormatWord:
    def test_format_keywords(self):
        assert _content_format_word("Cloud Security Course 8Batch 6Week", "x.svg") == "COURSE"
        assert _content_format_word("AI Coding Assistants Comparison Research Analysis", "x") == "STUDY"
        assert _content_format_word("Cloud Security Trends January 2026", "x") == "TRENDS"
        assert _content_format_word("AWS GCP Cloud Updates January 2026", "x") == "UPDATE"
        assert _content_format_word("KISA Security Advisory Ransomware", "x") == "REPORT"

    def test_default_is_guide(self):
        # Plain guides + roadmaps (no specific format keyword) -> GUIDE.
        assert _content_format_word("AWS Cloud Security Complete Guide", "x") == "GUIDE"
        assert _content_format_word("2026 DevSecOps Roadmap Complete Guide", "x") == "GUIDE"

    def test_value_is_ascii_and_within_kpi_cap(self):
        # _kpi_card hard-caps the value at 6 chars; every word must fit + be ASCII.
        for title in ("Course", "Comparison", "Trends", "Updates", "Advisory", "Anything"):
            w = _content_format_word(title, "")
            assert w.isascii() and len(w) <= 6


class TestContentSideKpi:
    def test_hero_has_no_kpi(self):
        # index 0 (hero) has no KPI card -> None so the caller never overrides it.
        assert _content_side_kpi(0, "AWS Guide", "2026-01-14-AWS_Guide.svg") is None

    def test_card1_is_format(self):
        v = _content_side_kpi(1, "AWS Cloud Security Complete Guide", "2026-01-14-AWS.svg")
        assert v == ("GUIDE", "FORMAT", "reference")

    def test_card2_is_publish_year(self):
        v = _content_side_kpi(2, "AWS Cloud Security Complete Guide", "2026-01-14-AWS.svg")
        assert v == ("2026", "YEAR", "published")

    def test_card2_none_when_no_dated_filename(self):
        # Year not derivable -> None so the caller keeps whatever _infer_kpi gave.
        assert _content_side_kpi(2, "AWS Guide", "no-date-here.svg") is None


class TestBuildStoryContentKpi:
    def _kpi(self, story):
        return (story["kpi_value"], story["kpi_label"], story["kpi_sub"])

    def test_placeholder_replaced_by_content_kpi(self):
        # A content band whose headline yields no figure: the TBD placeholder is
        # replaced by the supplied honest descriptor.
        story = _build_story(
            headline="AWS Cloud Security",  # no CVE/CVSS/$/%/count
            subheadline="x",
            index=1,
            severity_label="HIGH",
            content_mode=True,
            content_kpi=("GUIDE", "FORMAT", "reference"),
        )
        assert self._kpi(story) == ("GUIDE", "FORMAT", "reference")

    def test_real_inferred_kpi_preserved_over_content_kpi(self):
        # A REAL figure in the headline (here a CVE) must win over the content
        # fallback -- only the TBD placeholder is overridden.
        story = _build_story(
            headline="Cisco FMC CVE-2026-20122 patch",
            subheadline="x",
            index=1,
            severity_label="HIGH",
            content_mode=True,
            content_kpi=("GUIDE", "FORMAT", "reference"),
        )
        assert story["kpi_value"] == "CVE" and story["kpi_label"] == "ID"

    def test_digest_path_unaffected_without_content_kpi(self):
        # content_mode False (digest path) + no content_kpi: behaviour unchanged,
        # placeholder kept for _apply_real_content to fill later.
        story = _build_story(
            headline="some headline",
            subheadline="x",
            index=1,
            severity_label="HIGH",
        )
        assert self._kpi(story) == ("TBD", "STATUS", "NEW")

    def test_content_kpi_ignored_when_none(self):
        # content_mode True but no content_kpi supplied (e.g. hero idx 0) ->
        # placeholder kept (no crash, no override).
        story = _build_story(
            headline="no figures here",
            subheadline="x",
            index=0,
            severity_label="HIGH",
            content_mode=True,
            content_kpi=None,
        )
        assert self._kpi(story) == ("TBD", "STATUS", "NEW")
