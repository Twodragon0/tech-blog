#!/usr/bin/env python3
"""Tests for the L20 dispatch flag + KPI inference + ``generate_l20_digest_svg``.

Covers:

- ``USE_L20_HERO`` env flag toggle (set to "0" / unset / "1") and the
  resulting auto_publish_news ``L20_HERO_ENABLED`` constant.
- ``_infer_kpi`` regex coverage (CVE id, CVSS, USD, percent, count, default).
- ``generate_l20_digest_svg`` end-to-end (with a stubbed renderer so the
  unit tests stay fast and side-effect free).

API disabling and ``sys.path`` setup are handled by ``conftest.py``.
"""

import importlib
import os
import re
import sys
from pathlib import Path

import pytest

from scripts.news import l20_dispatch
from scripts.news.l20_dispatch import (
    _english_topics_from_filename,
    _has_hangul,
    _infer_kpi,
    extract_three_stories,
    generate_l20_digest_svg,
    route_visual_id,
)


# =====================================================================
# Honesty-driven routing (Option B): non-attack -> neutral, price -> market
# =====================================================================


class TestHonestyDrivenRouting:
    """The two flagged covers' tokens must route to honest, non-attack
    visuals. The Option A stopgap routed them to attack builders
    (data_exfil/container_escape/hub_spoke) which the re-audit flagged."""

    def test_bithumb_routes_neutral_not_breach(self):
        # Operational incident, NOT an intrusion: data_exfil would assert a
        # breach the post lacks.
        assert route_visual_id("Bithumb") == "neutral"

    def test_cncf_and_cluster_api_route_neutral_not_escape(self):
        # Ecosystem velocity / lifecycle, NOT a container escape.
        assert route_visual_id("CNCF") == "neutral"
        assert route_visual_id("Cluster API") == "neutral"

    def test_bitcoin_routes_market_not_attack(self):
        # Pure price / market story: any attack builder misrepresents it.
        assert route_visual_id("Bitcoin") == "market"
        assert route_visual_id("Bitcoin $71K") == "market"

    def test_chainalysis_routes_neutral(self):
        assert route_visual_id("Chainalysis report") == "neutral"

    def test_real_cve_still_routes_cve_chain(self):
        # The genuine CVE keyword route is UNCHANGED.
        assert route_visual_id("CVE-2026-1234 RCE in Redis") == "cve_chain"
        assert route_visual_id("Patch Tuesday 9.8 CVSS fix") == "cve_chain"

    def test_genuine_attack_routes_unchanged(self):
        # Ransomware / supply-chain / botnet still reach their attack builders.
        assert route_visual_id("LockBit ransomware hits banks") == "ransomware_lock"
        assert route_visual_id("Supply chain attack on npm") == "supply_chain_pipe"
        assert route_visual_id("SOHO router botnet C2") == "hub_spoke"

    def test_default_is_neutral(self):
        assert route_visual_id("") == "neutral"
        assert route_visual_id("an unrelated topic") == "neutral"


# =====================================================================
# English fallback for Korean titles (regression: 2026-05-08 check-svg)
# =====================================================================


class TestEnglishFallbackForKoreanTitle:
    """check-svg blocked when SVG <text> contained Hangul. extract_three_stories
    must pull English keywords from the filename slug whenever a candidate
    segment contains Hangul."""

    def test_filename_keyword_extraction(self):
        kws = _english_topics_from_filename(
            "2026-05-01-Tech_Security_Weekly_Digest_AI_AWS_Threat_Cloud.md"
        )
        assert kws == ["AI", "AWS", "Threat", "Cloud"]

    def test_filename_keyword_extraction_alt_stem(self):
        kws = _english_topics_from_filename(
            "2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin.md"
        )
        assert kws == ["Bithumb", "Bitcoin"]

    def test_korean_title_replaced_by_filename_keywords(self):
        """A purely-Korean title yields three ASCII-only headlines."""
        title = "Apache HTTP/2의 치명적, DAEMON Tools 공급망 공격으로 공식, 중국과 연계된 UAT-8302"
        excerpt = "Apache HTTP/2의 치명적 취약점을 발표했습니다."
        filename = "2026-05-06-Tech_Security_Weekly_Digest_CVE_AI_Malware_Go.md"
        h, tr, br = extract_three_stories(title, excerpt, filename)
        for story in (h, tr, br):
            assert not _has_hangul(story["headline"]), (
                f"Hangul leaked into headline: {story['headline']!r}"
            )
            assert not _has_hangul(story["subheadline"]), (
                f"Hangul leaked into subheadline: {story['subheadline']!r}"
            )

    def test_mixed_title_keeps_english_segments(self):
        """Mixed Korean+English title preserves English segments verbatim."""
        title = "AWS Re:Invent 2026, 한국어 세그먼트, Kubernetes Update"
        h, tr, br = extract_three_stories(
            title, "", "2026-05-01-Tech_Security_Weekly_Digest_AI_AWS_Threat_Cloud.md"
        )
        # First and third segments are pure-English so they survive.
        assert "AWS" in h["headline"] or "Re:Invent" in h["headline"]
        # Middle segment should be replaced with a filename keyword.
        assert not _has_hangul(tr["headline"])
        assert "Kubernetes" in br["headline"] or "Update" in br["headline"]

    def test_empty_filename_falls_back_to_generic(self):
        """No filename → generic English placeholders, never Korean."""
        title = "한국어 제목입니다"
        h, tr, br = extract_three_stories(title, "", "")
        for story in (h, tr, br):
            assert not _has_hangul(story["headline"])

    def test_has_hangul_detection(self):
        assert _has_hangul("Apache HTTP/2의")
        assert _has_hangul("ㄱ")
        assert not _has_hangul("Apache HTTP/2 critical")
        assert not _has_hangul("")


# =====================================================================
# Env flag toggle - L20_HERO_ENABLED on auto_publish_news
# =====================================================================


def _reload_auto_publish_news():
    """Reload auto_publish_news so module-level env reads re-evaluate.

    The conftest.py already imports auto_publish_news; we drop and re-import
    so the test sees a freshly-read USE_L20_HERO value.
    """
    # auto_publish_news installs a _ConfigProxy into sys.modules.  Drop the
    # proxy + its real backing module so the next import re-runs top-level.
    for mod in ("auto_publish_news", "scripts.news.l20_dispatch"):
        sys.modules.pop(mod, None)
    return importlib.import_module("auto_publish_news")


class TestUseL20HeroEnvFlag:
    def test_unset_defaults_to_enabled(self, monkeypatch):
        monkeypatch.delenv("USE_L20_HERO", raising=False)
        mod = _reload_auto_publish_news()
        assert mod.L20_HERO_ENABLED is True

    def test_explicit_one_enables(self, monkeypatch):
        monkeypatch.setenv("USE_L20_HERO", "1")
        mod = _reload_auto_publish_news()
        assert mod.L20_HERO_ENABLED is True

    def test_zero_disables(self, monkeypatch):
        monkeypatch.setenv("USE_L20_HERO", "0")
        mod = _reload_auto_publish_news()
        assert mod.L20_HERO_ENABLED is False

    def test_false_disables(self, monkeypatch):
        monkeypatch.setenv("USE_L20_HERO", "false")
        mod = _reload_auto_publish_news()
        assert mod.L20_HERO_ENABLED is False

    def test_empty_disables(self, monkeypatch):
        monkeypatch.setenv("USE_L20_HERO", "")
        mod = _reload_auto_publish_news()
        assert mod.L20_HERO_ENABLED is False


# =====================================================================
# _infer_kpi - regex heuristics
# =====================================================================


class TestInferKpi:
    @pytest.mark.parametrize(
        "headline,expected_label,expected_sub_contains",
        [
            ("LockBit ransomware hits 320 victims", "COUNT", ""),
            ("Patch Tuesday CVE-2026-1234 RCE", "ID", "CVE-2026-1234"),
            ("Critical CVSS 9.8 in Redis", "CVSS", "severity"),
            ("Heist drains $87M from bridge", "IMPACT", "estimated"),
            ("Phishing kits cover 63% of incidents", "RATIO", "share"),
            ("nothing to extract here", "STATUS", "NEW"),
        ],
    )
    def test_kpi_label_and_sub(self, headline, expected_label, expected_sub_contains):
        value, label, sub = _infer_kpi(headline)
        assert label == expected_label
        if expected_sub_contains:
            assert expected_sub_contains.lower() in sub.lower()
        # Value must be non-empty and bounded for layout safety.
        assert value
        assert len(value) <= 18

    def test_default_when_empty(self):
        assert _infer_kpi("") == ("TBD", "STATUS", "NEW")
        assert _infer_kpi(None) == ("TBD", "STATUS", "NEW")


# =====================================================================
# Nit 1 - market-routed USD KPI relabels IMPACT -> PRICE in _build_story
# =====================================================================


class TestMarketKpiPriceLabel:
    """A USD figure on a market-routed band is a PRICE, not an attack
    IMPACT. ``_build_story`` relabels only market-routed bands; non-market
    USD KPIs keep the generic IMPACT label from ``_infer_kpi``."""

    def test_market_usd_relabels_to_price(self):
        from scripts.news.l20_dispatch import _build_story

        story = _build_story(
            headline="Bitcoin $71K",
            subheadline="market trend overview",
            index=2,
            severity_label="MEDIUM",
        )
        assert story["visual"] == "market"
        assert story["kpi_label"] == "PRICE"
        assert story["kpi_sub"] == "spot"
        assert story["kpi_value"] == "$71K"

    def test_non_market_usd_keeps_impact(self):
        from scripts.news.l20_dispatch import _build_story

        # A breach-cost figure on an attack-routed (ransomware) band must keep
        # the IMPACT label — the relabel is market-only.
        story = _build_story(
            headline="Ransomware heist drains $87M",
            subheadline="incident impact estimate",
            index=0,
            severity_label="HIGH",
        )
        assert story["visual"] == "ransomware_lock"
        assert story["kpi_label"] == "IMPACT"
        assert story["kpi_sub"] == "estimated"


# =====================================================================
# Subheadline de-duplication (designer re-audit bug fix)
# =====================================================================


class TestSubheadlineDeduplication:
    """Bug: side bands rendered ``"Bithumb - Bithumb Bitcoin"`` /
    ``"CNCF - CNCF Chainalysis Bitcoin"`` — the headline echoed into the
    subheadline because the only ASCII context for a Korean-excerpt digest
    is the filename-keyword pool, which contains the headline token. The
    subheadline must no longer repeat the headline back."""

    def test_bithumb_subheadline_does_not_echo_headline(self):
        title = "2026-02-09 블록체인 & 테크 다이제스트: Bithumb 운영 사고, Bitcoin $71K"
        excerpt = "빗썸 운영 사고 비트코인 오인출금 이슈"
        fn = "2026-02-09-Blockchain_Tech_Digest_Bithumb_Bitcoin.md"
        h, tr, br = extract_three_stories(title, excerpt, fn)
        # The exact corrupted strings must be gone.
        assert h["subheadline"] != "Bithumb - Bithumb Bitcoin"
        # No headline token is immediately repeated as the first sub word.
        for story in (h, tr, br):
            head = story["headline"].split()[0].lower()
            sub_words = [w.lower() for w in story["subheadline"].replace("-", " ").split()]
            # The headline's lead token must not appear twice in the sub.
            assert sub_words.count(head) <= 1, (
                f"headline token {head!r} repeated in subheadline "
                f"{story['subheadline']!r}"
            )

    def test_cncf_subheadline_does_not_echo_headline(self):
        title = "DevOps & 블록체인 다이제스트: CNCF Velocity, Cluster API, Bitcoin"
        excerpt = "CNCF 속도 보고서 클러스터 API 업데이트"
        fn = "2026-02-10-DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin.md"
        h, _, _ = extract_three_stories(title, excerpt, fn)
        assert h["subheadline"] != "CNCF - CNCF Chainalysis Bitcoin"
        assert not h["subheadline"].lower().startswith("cncf - cncf")

    def test_dedupe_helper_drops_repeated_words(self):
        from scripts.news.l20_dispatch import _dedupe_subheadline_extra

        assert _dedupe_subheadline_extra("Bithumb", "Bithumb Bitcoin") == "Bitcoin"
        assert _dedupe_subheadline_extra("CNCF", "CNCF Chainalysis Bitcoin") == (
            "Chainalysis Bitcoin"
        )
        # No overlap -> extra preserved verbatim (still within the 2-token cap).
        assert _dedupe_subheadline_extra("Bithumb", "Market update") == "Market update"

    def test_dedupe_caps_at_two_tokens(self):
        """Nit 2: the kept remainder is capped to <=2 keyword tokens so the
        subheadline cannot accrete a long keyword echo."""
        from scripts.news.l20_dispatch import _dedupe_subheadline_extra

        out = _dedupe_subheadline_extra("Topic", "Alpha Beta Gamma Delta")
        assert out.split() == ["Alpha", "Beta"]

    def test_dedupe_removes_repeated_tokens(self):
        """Nit 2: a token repeated within ``extra`` is kept only once."""
        from scripts.news.l20_dispatch import _dedupe_subheadline_extra

        assert _dedupe_subheadline_extra("Topic", "Bitcoin Bitcoin") == "Bitcoin"

    def test_dedupe_drops_other_band_headline_token(self):
        """Nit 2: the exact prior offender — band 1 "Cluster API" kept a
        trailing "Bitcoin" that is band 3's headline. With cross-band context
        that trailing token is dropped."""
        from scripts.news.l20_dispatch import _dedupe_subheadline_extra

        out = _dedupe_subheadline_extra(
            "Cluster API",
            "CNCF Chainalysis Bitcoin",
            other_headlines=["CNCF Velocity", "Bitcoin"],
        )
        words = out.lower().split()
        assert "bitcoin" not in words, f"trailing cross-band token kept: {out!r}"
        # The honest, non-overlapping remainder survives (not blanked).
        assert "chainalysis" in words

    def test_extract_three_stories_no_trailing_cross_band_dup(self):
        """End-to-end: no band's subheadline ends with another band's
        headline lead-token (the prior trailing-duplicate symptom)."""
        title = "DevOps & 블록체인 다이제스트: CNCF Velocity, Cluster API, Bitcoin"
        excerpt = "CNCF 속도 보고서 클러스터 API 업데이트"
        fn = "2026-02-10-DevOps_Blockchain_Digest_CNCF_Chainalysis_Bitcoin.md"
        h, tr, br = extract_three_stories(title, excerpt, fn)
        stories = [h, tr, br]
        for i, story in enumerate(stories):
            sub_words = [
                w.lower() for w in story["subheadline"].replace("-", " ").split()
            ]
            for j, other in enumerate(stories):
                if i == j:
                    continue
                other_lead = other["headline"].split()[0].lower()
                assert sub_words.count(other_lead) == 0 or other_lead in [
                    w.lower() for w in story["headline"].split()
                ], (
                    f"band {i} sub {story['subheadline']!r} echoes band {j} "
                    f"headline token {other_lead!r}"
                )


# =====================================================================
# generate_l20_digest_svg - dispatch with stubbed renderer
# =====================================================================


class TestGenerateL20DigestSvg:
    def test_writes_file_via_renderer(self, tmp_path, monkeypatch):
        """Confirm the dispatcher calls render_l20_hero and writes its
        output to the expected SVG path. Avoid pulling in the heavy
        sanitizer module by stubbing the renderer to return a minimal
        but well-formed SVG string.
        """
        captured = {}

        def fake_render_l20_hero(**kwargs):
            captured.update(kwargs)
            return (
                '<svg xmlns="http://www.w3.org/2000/svg" '
                'viewBox="0 0 1200 630" width="1200" height="630">'
                "<title>stub</title></svg>\n"
            )

        # Patch on the lazily-imported symbol path. l20_dispatch imports
        # render_l20_hero inside the function body, so we patch the source
        # module directly.
        import scripts.lib.svg_l20_hero as l20_lib

        monkeypatch.setattr(l20_lib, "render_l20_hero", fake_render_l20_hero)

        post_info = {
            "title": "Weekly digest 2026-04-30: Ransomware, AI agent, Cloud",
            "filename": "2026-04-30-Tech_Security_Weekly_Digest_Ransomware.md",
            "excerpt": "Ransomware wave hits banks; AI agents jailbroken; S3 leak",
            "content": "",
        }
        out = tmp_path / "cover.svg"
        ok = generate_l20_digest_svg(post_info, out)
        assert ok is True
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert content.startswith("<svg")
        assert 'viewBox="0 0 1200 630"' in content
        # The dispatcher must hand the renderer the canonical post URL.
        # Underscores are preserved per Jekyll's permalink config — earlier
        # ``slug.replace("_", "-")`` produced 404 URLs in every QR.
        assert (
            captured["url"]
            == "https://tech.2twodragon.com/posts/2026/04/30/"
            "Tech_Security_Weekly_Digest_Ransomware/"
        )
        # date_str follows the L20 dotted format.
        assert captured["date_str"] == "2026.04.30"
        # Hero gets an action tag, the right-side cards do not.
        assert "action" in captured["hero"]
        assert "action" not in captured["top_right"]
        assert "action" not in captured["bottom_right"]


# =====================================================================
# Auto publish dispatch branch: L20 path vs L22/legacy fallback
# =====================================================================


class TestAutoPublishDispatchBranch:
    """Verify that USE_L20_HERO controls which generator is invoked when
    auto_publish_news.main runs in security mode. We don't run main()
    end-to-end (it touches disk + network); instead we exercise the
    branch logic directly.
    """

    def test_l20_branch_calls_l20_renderer(self, monkeypatch):
        monkeypatch.setenv("USE_L20_HERO", "1")
        mod = _reload_auto_publish_news()
        assert mod.L20_HERO_ENABLED is True

        called = {"l20": 0, "legacy": 0}

        def fake_l20(post_info):
            called["l20"] += 1
            return "<svg>l20</svg>"

        def fake_legacy(*_args, **_kwargs):
            called["legacy"] += 1
            return "<svg>legacy</svg>"

        monkeypatch.setattr(mod, "_render_l20_svg_string", fake_l20)
        monkeypatch.setattr(mod, "generate_svg_image", fake_legacy)

        # Inline the small dispatch fragment from main():
        if mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string({"title": "T", "filename": "f.md"})
            if not svg:
                svg = mod.generate_svg_image(None, {}, [])
        else:
            svg = mod.generate_svg_image(None, {}, [])

        assert called["l20"] == 1
        assert called["legacy"] == 0
        assert svg == "<svg>l20</svg>"

    def test_disabled_falls_back_to_legacy(self, monkeypatch):
        monkeypatch.setenv("USE_L20_HERO", "0")
        mod = _reload_auto_publish_news()
        assert mod.L20_HERO_ENABLED is False

        called = {"l20": 0, "legacy": 0}

        def fake_l20(post_info):
            called["l20"] += 1
            return "<svg>l20</svg>"

        def fake_legacy(*_args, **_kwargs):
            called["legacy"] += 1
            return "<svg>legacy</svg>"

        monkeypatch.setattr(mod, "_render_l20_svg_string", fake_l20)
        monkeypatch.setattr(mod, "generate_svg_image", fake_legacy)

        if mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string({"title": "T", "filename": "f.md"})
            if not svg:
                svg = mod.generate_svg_image(None, {}, [])
        else:
            svg = mod.generate_svg_image(None, {}, [])

        assert called["l20"] == 0
        assert called["legacy"] == 1
        assert svg == "<svg>legacy</svg>"

    def test_l20_failure_falls_back_to_legacy(self, monkeypatch):
        """If render returns empty (failure path), legacy generator runs."""
        monkeypatch.setenv("USE_L20_HERO", "1")
        mod = _reload_auto_publish_news()

        called = {"legacy": 0}

        def fake_l20(post_info):
            return ""  # Simulate render failure.

        def fake_legacy(*_args, **_kwargs):
            called["legacy"] += 1
            return "<svg>legacy</svg>"

        monkeypatch.setattr(mod, "_render_l20_svg_string", fake_l20)
        monkeypatch.setattr(mod, "generate_svg_image", fake_legacy)

        if mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string({"title": "T", "filename": "f.md"})
            if not svg:
                svg = mod.generate_svg_image(None, {}, [])
        else:
            svg = mod.generate_svg_image(None, {}, [])

        assert called["legacy"] == 1
        assert svg == "<svg>legacy</svg>"


# =====================================================================
# Regression: cron cover <title> must be ASCII (build_cover_title wiring)
# =====================================================================
class TestRenderL20SvgStringCleanTitle:
    """The blogwatcher cron path ``auto_publish_news._render_l20_svg_string``
    must build the SVG ``<title>`` via ``build_cover_title`` (clean ASCII
    template), not pass the raw — often Korean — post title straight through.

    Regression for the 2026-06-05 auto-published cover that shipped
    ``<title>2026 06 05 Cisco FMC· (29 )</title>`` (U+00B7 middle dot +
    Hangul-strip residue), which only failed the title-ASCII gate after the
    PR merge because the cron itself had no ASCII gate.
    """

    def test_korean_post_title_yields_ascii_clean_title(self):
        ap = importlib.import_module("auto_publish_news")
        post_info = {
            "title": "2026년 06월 05일 주간 보안 다이제스트: 제로데이·Cisco FMC·패치 (29건)",
            "excerpt": "Cisco FMC 제로데이 패치 및 주간 보안 동향 요약입니다.",
            "filename": "2026-06-05-Tech_Security_Weekly_Digest_CVE_Patch_Go_AI.md",
            "category": "security",
        }
        svg = ap._render_l20_svg_string(post_info)
        assert svg, "_render_l20_svg_string returned empty (L20 import failed)"
        m = re.search(r"<title>([^<]*)</title>", svg)
        assert m, "no <title> element in rendered SVG"
        title = m.group(1)
        # Core regression: <title> is ASCII-only (no U+00B7, no Hangul).
        non_ascii = [c for c in title if ord(c) >= 128]
        assert not non_ascii, f"non-ASCII codepoint(s) {non_ascii!r} in <title>: {title!r}"
        # Clean fixed template, topic derived from the filename slug.
        assert title == "Weekly Security Digest - 2026.06.05", title


class TestRenderL20SvgStringRealContent:
    """The cron path must surface REAL content (lead entities + source +
    collection counts) from ``post_info["content"]`` (full body), not generic
    filename keywords + a TBD KPI. ``post_info`` has no parsed summary_card
    dict on the cron path, so the body-table backfill is the source.
    """

    _BODY = (
        "**수집 통계:**\n- **총 뉴스 수**: 29개\n- **보안 뉴스**: 5개\n\n"
        "| 분야 | 소스 | 핵심 내용 | 영향도 |\n"
        "|------|------|----------|--------|\n"
        "| 🔒 **Security** | The Hacker News | Ivanti EPMM CVE-2026-6973 RCE 공개 | 🟠 High |\n"
        "| 🔒 **Security** | BleepingComputer | WP Maps Pro 취약점 악용 | 🟠 High |\n"
        "| ⛓️ **Blockchain** | Cointelegraph | Michael Saylor BTC 매수 | 🟡 Medium |\n"
    )

    def test_cron_cover_carries_real_entities_and_counts(self):
        ap = importlib.import_module("auto_publish_news")
        post_info = {
            "title": "2026년 06월 05일 주간 보안 다이제스트 (29건)",
            "excerpt": "주간 보안 동향 요약입니다.",
            "filename": "2026-06-05-Tech_Security_Weekly_Digest_CVE_Patch_Go_AI.md",
            "category": "security",
            "content": self._BODY,
        }
        svg = ap._render_l20_svg_string(post_info)
        assert svg, "_render_l20_svg_string returned empty"
        texts = re.findall(r"<text[^>]*>([^<]+)</text>", svg)
        joined = "|".join(texts)
        # Real lead entity from the body table (not "CVE"/"Patch"/"Go").
        assert "Ivanti EPMM" in joined
        # The subheadline now surfaces a CONTENT descriptor from the title's
        # secondary entity ("RCE"), not the bare source name (which moved to
        # route_hint and drives visual routing only).
        assert "RCE" in joined
        # Real collection count replaces the TBD KPI placeholder.
        assert "ITEMS" in joined and "29" in texts
        # ASCII-only invariant holds end-to-end (no Hangul leaked into <text>).
        assert not any(ord(c) >= 128 for c in joined), "non-ASCII in <text>"
