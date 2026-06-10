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
    _digest_panels,
    _digest_stats,
    _digest_table_panels,
    _entity_tokens,
    _honest_content_visual,
    _is_good_headline,
    _panel_from_source_title,
    _rescue_hero,
    _severity_from_marker,
    resolve_digest_band_visuals,
    route_visual_id,
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
