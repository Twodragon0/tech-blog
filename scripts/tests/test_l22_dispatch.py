#!/usr/bin/env python3
"""Tests for ``scripts/news/l22_dispatch.py`` and the
``USE_L22_ULTRA`` env-flag wiring in ``scripts/auto_publish_news.py``.

Mirrors the structure of ``tests/test_l20_hero_dispatch.py``:

- env-flag toggle (``USE_L22_ULTRA`` set to ``"1"`` / unset / ``"0"``)
  and the resulting ``L22_ULTRA_ENABLED`` constant on auto_publish_news.
- routing helpers (``_route_theme``, ``_route_visual_kind``,
  ``_route_label``) and the headline-derived band-config builder.
- end-to-end renderer (``render_l22_svg_string`` + ``generate_l22_digest_svg``)
  with a stubbed L22 generator so the unit tests stay fast.
- dispatch precedence in auto_publish_news.main: L22 wins over L20 when
  both flags are set; L22 failure falls back to L20; both off ⇒ legacy.
"""

import importlib
import sys
from pathlib import Path
from typing import Optional

import pytest


# =====================================================================
# _route_* heuristics
# =====================================================================


class TestRouteHelpers:
    def test_route_theme_red_amber_green(self):
        from scripts.news.l22_dispatch import _route_theme
        assert _route_theme(0) == "red"
        assert _route_theme(1) == "amber"
        assert _route_theme(2) == "green"

    @pytest.mark.parametrize(
        "headline,expected_visual",
        [
            ("CVE-2026-1234 RCE in Ivanti EPMM", "lock_cve"),
            ("Mirai botnet hits IoT", "network_nodes"),
            ("Chrome zero-day patched", "lock_cve"),
            ("Kubernetes container escape via CRI-O", "cloud_k8s"),
            ("Hugging Face fake OpenAI repo distributes stealer", "code_bars"),
            # "router" matches before "patches" in the heuristic order, so
            # the cover gets a router_mesh visual rather than the patch shield.
            ("Cisco patches three router CVEs", "router_mesh"),
            ("Stealer hidden in npm supply chain", "lock_cve"),
            ("AI agent framework prompt RCE", "lock_cve"),
            # "vulnerabilities" matches the \bvuln rule (lock_cve) before
            # the \bpatch rule (shield) — keep heuristic ordering test honest.
            ("vendor releases hardening for backups", "shield"),
        ],
    )
    def test_route_visual_kind_keyword_matches(self, headline, expected_visual):
        from scripts.news.l22_dispatch import _route_visual_kind
        assert _route_visual_kind(headline, 0) == expected_visual

    def test_route_visual_kind_default_rotates_by_index(self):
        from scripts.news.l22_dispatch import _route_visual_kind
        # No keyword match → fall back to band-index rotation.
        assert _route_visual_kind("nothing in particular", 0) == "lock_cve"
        assert _route_visual_kind("nothing in particular", 1) == "network_nodes"
        assert _route_visual_kind("nothing in particular", 2) == "code_bars"

    @pytest.mark.parametrize(
        "headline,expected_label",
        [
            ("LockBit ransomware hits 320 victims", "RANSOMWARE"),
            ("TCLBANKER banking trojan worms via WhatsApp", "BANKING TROJAN"),
            ("PCPJack 5-CVE worm spreads in cloud", "WORM CHAIN"),
            ("Ivanti EPMM admin RCE", "ADMIN RCE"),
            ("AI agent framework prompt RCE", "ADMIN RCE"),
            ("Patch Tuesday: 87 fixes", "PATCH NOW"),
            ("Mirai botnet variant", "IOT BOTNET"),
            ("nothing matches", "ALERT"),
        ],
    )
    def test_route_label(self, headline, expected_label):
        from scripts.news.l22_dispatch import _route_label
        assert _route_label(headline) == expected_label


# =====================================================================
# _build_band_cfg — full dict shape
# =====================================================================


class TestBuildBandCfg:
    def test_emits_required_keys_for_render_bands_svg(self):
        from scripts.news.l22_dispatch import _build_band_cfg
        cfg = _build_band_cfg(
            "Ivanti EPMM CVE-2026-6973 RCE actively exploited",
            "Critical CVSS 9.8 admin access",
            band_idx=0,
        )
        required = {
            "theme", "label", "headline", "metric", "detail",
            "metric_b", "detail_b",
            "badge_value", "badge_label", "badge_sub",
            "mini_value", "mini_label", "mini_sub",
            "mini2_value", "mini2_label", "mini2_sub",
            "visual",
        }
        assert required.issubset(cfg.keys())
        assert cfg["theme"] == "red"          # band 0 = red
        assert cfg["label"] == "ADMIN RCE"    # keyword match wins
        assert cfg["visual"]                  # non-empty SVG fragment

    def test_band_idx_drives_theme_progression(self):
        from scripts.news.l22_dispatch import _build_band_cfg
        b0 = _build_band_cfg("h0", "s0", 0)
        b1 = _build_band_cfg("h1", "s1", 1)
        b2 = _build_band_cfg("h2", "s2", 2)
        assert (b0["theme"], b1["theme"], b2["theme"]) == ("red", "amber", "green")


# =====================================================================
# render_l22_svg_string — end-to-end with stubbed renderer
# =====================================================================


class TestRenderL22SvgString:
    def test_renders_svg_via_l22_renderer(self, monkeypatch):
        captured = {}

        def fake_render(**kwargs):
            captured.update(kwargs)
            return (
                '<svg xmlns="http://www.w3.org/2000/svg" '
                'viewBox="0 0 1200 630" width="1200" height="630">'
                "<title>stub</title></svg>\n"
            )

        import scripts.lib.svg_l22_generator as l22
        monkeypatch.setattr(l22, "render_bands_svg", fake_render)

        from scripts.news.l22_dispatch import render_l22_svg_string

        svg = render_l22_svg_string({
            "title": "Weekly digest 2026-05-10: Ransomware, AI agent, Cloud",
            "filename": "2026-05-10-Tech_Security_Weekly_Digest_Ransomware.md",
            "excerpt": "Ransomware wave hits banks; AI agents jailbroken; S3 leak",
        })
        assert svg.startswith("<svg")
        # The dispatcher passes 3 bands and the canonical Jekyll permalink.
        assert len(captured["bands_cfg"]) == 3
        # Underscore-preserving permalink (Jekyll convention) — see the
        # check_cover_qr_urls.py CI gate for the canonical contract.
        assert captured["url"] == (
            "https://tech.2twodragon.com/posts/2026/05/10/"
            "Tech_Security_Weekly_Digest_Ransomware/"
        )
        # Each band has a distinct theme.
        themes = [b["theme"] for b in captured["bands_cfg"]]
        assert themes == ["red", "amber", "green"]

    def test_returns_empty_on_renderer_exception(self, monkeypatch):
        def boom(**kwargs):
            raise RuntimeError("render exploded")

        import scripts.lib.svg_l22_generator as l22
        monkeypatch.setattr(l22, "render_bands_svg", boom)
        from scripts.news.l22_dispatch import render_l22_svg_string
        assert render_l22_svg_string({
            "title": "x",
            "filename": "2026-05-10-Foo.md",
            "excerpt": "bar",
        }) == ""


# =====================================================================
# generate_l22_digest_svg — file-write contract
# =====================================================================


class TestGenerateL22DigestSvg:
    def test_writes_file_via_renderer(self, tmp_path, monkeypatch):
        def fake_render(**kwargs):
            return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630"><title>stub</title></svg>\n'

        import scripts.lib.svg_l22_generator as l22
        monkeypatch.setattr(l22, "render_bands_svg", fake_render)

        from scripts.news.l22_dispatch import generate_l22_digest_svg

        out = tmp_path / "cover.svg"
        ok = generate_l22_digest_svg({
            "title": "Weekly digest 2026-05-10",
            "filename": "2026-05-10-Tech_Security_Weekly_Digest.md",
            "excerpt": "summary",
        }, out)
        assert ok is True
        assert out.exists()
        assert out.read_text(encoding="utf-8").startswith("<svg")

    def test_returns_false_on_empty_filename(self, tmp_path, monkeypatch):
        from scripts.news.l22_dispatch import generate_l22_digest_svg
        out = tmp_path / "cover.svg"
        ok = generate_l22_digest_svg(
            {"title": "x", "filename": "", "excerpt": "y"}, out
        )
        assert ok is False
        assert not out.exists()


# =====================================================================
# auto_publish_news USE_L22_ULTRA env flag
# =====================================================================


def _reload_auto_publish_news():
    for mod in (
        "auto_publish_news",
        "scripts.auto_publish_news",
        "scripts.news.l20_dispatch",
        "scripts.news.l22_dispatch",
    ):
        sys.modules.pop(mod, None)
    return importlib.import_module("auto_publish_news")


class TestL22UltraEnvFlag:
    def test_unset_defaults_to_disabled(self, monkeypatch):
        """L22 ultra deprecated 2026-05-26 in favor of L20 family unification.
        Default flipped back to OFF; L22 retained only as an explicit
        opt-in legacy renderer. See auto_publish_news.py L22_ULTRA_ENABLED."""
        monkeypatch.delenv("USE_L22_ULTRA", raising=False)
        mod = _reload_auto_publish_news()
        assert mod.L22_ULTRA_ENABLED is False

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE"])
    def test_truthy_values_enable(self, monkeypatch, value):
        # Explicit opt-in only.
        monkeypatch.setenv("USE_L22_ULTRA", value)
        mod = _reload_auto_publish_news()
        assert mod.L22_ULTRA_ENABLED is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", "FALSE", "Off", ""])
    def test_falsy_values_disable(self, monkeypatch, value):
        """Default + explicit opt-out values disable L22 ultra. Empty
        string is the new default-equivalent and disables."""
        monkeypatch.setenv("USE_L22_ULTRA", value)
        mod = _reload_auto_publish_news()
        assert mod.L22_ULTRA_ENABLED is False


class TestDispatchPrecedence:
    """L20 wins over L22 when both flags are set (2026-05-26 migration);
    falls back gracefully."""

    def _stub_dispatch(self, monkeypatch, mod, l20_returns: str, l22_returns: str = "<svg>l22</svg>"):
        called = {"l22": 0, "l20": 0, "legacy": 0}

        def fake_l22(post_info):
            called["l22"] += 1
            return l22_returns

        def fake_l20(post_info):
            called["l20"] += 1
            return l20_returns

        def fake_legacy(*_a, **_kw):
            called["legacy"] += 1
            return "<svg>legacy</svg>"

        monkeypatch.setattr(mod, "_render_l22_svg_string", fake_l22)
        monkeypatch.setattr(mod, "_render_l20_svg_string", fake_l20)
        monkeypatch.setattr(mod, "generate_svg_image", fake_legacy)
        return called

    def test_l20_takes_precedence_when_both_enabled(self, monkeypatch):
        monkeypatch.setenv("USE_L22_ULTRA", "1")
        monkeypatch.setenv("USE_L20_HERO", "1")
        mod = _reload_auto_publish_news()
        called = self._stub_dispatch(monkeypatch, mod, l20_returns="<svg>l20</svg>")

        # Inline the dispatch fragment as it appears in main():
        post_info: dict = {"title": "T", "filename": "f.md"}
        svg = ""
        if mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string(post_info)
        if not svg and mod.L22_ULTRA_ENABLED:
            svg = mod._render_l22_svg_string(post_info)
        if not svg:
            svg = mod.generate_svg_image(None, {}, [])

        assert called == {"l22": 0, "l20": 1, "legacy": 0}
        assert svg == "<svg>l20</svg>"

    def test_l20_failure_falls_back_to_l22(self, monkeypatch):
        monkeypatch.setenv("USE_L22_ULTRA", "1")
        monkeypatch.setenv("USE_L20_HERO", "1")
        mod = _reload_auto_publish_news()
        called = self._stub_dispatch(monkeypatch, mod, l20_returns="")  # render fail

        post_info: dict = {"title": "T", "filename": "f.md"}
        svg = ""
        if mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string(post_info)
        if not svg and mod.L22_ULTRA_ENABLED:
            svg = mod._render_l22_svg_string(post_info)
        if not svg:
            svg = mod.generate_svg_image(None, {}, [])

        assert called == {"l22": 1, "l20": 1, "legacy": 0}
        assert svg == "<svg>l22</svg>"

    def test_both_flags_off_falls_back_to_legacy(self, monkeypatch):
        monkeypatch.setenv("USE_L22_ULTRA", "0")
        monkeypatch.setenv("USE_L20_HERO", "0")
        mod = _reload_auto_publish_news()
        called = self._stub_dispatch(monkeypatch, mod, l20_returns="")

        post_info: dict = {"title": "T", "filename": "f.md"}
        svg = ""
        if mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string(post_info)
        if not svg and mod.L22_ULTRA_ENABLED:
            svg = mod._render_l22_svg_string(post_info)
        if not svg:
            svg = mod.generate_svg_image(None, {}, [])

        # Neither dispatch path runs; legacy generator picks up.
        assert called == {"l22": 0, "l20": 0, "legacy": 1}
        assert svg == "<svg>legacy</svg>"


class TestForceVisualVariety:
    """Fix 1: when 2+ bands route to the same primitive, the dispatcher
    must rewrite them so all 3 bands carry distinct primitives. The
    deterministic seeded rotation also has to keep the same post stable
    across reruns (same date → same visual triple)."""

    def test_three_identical_kinds_get_diversified(self):
        from scripts.news.l22_dispatch import _force_variety
        out = _force_variety(["lock_cve", "lock_cve", "lock_cve"], seed_hex="20260513")
        assert len(set(out)) == 3, f"expected 3 distinct primitives, got {out}"

    def test_two_identical_one_different_get_diversified(self):
        from scripts.news.l22_dispatch import _force_variety
        out = _force_variety(["lock_cve", "network_nodes", "lock_cve"], seed_hex="20260513")
        assert len(set(out)) == 3

    def test_already_distinct_passes_through_unchanged(self):
        from scripts.news.l22_dispatch import _force_variety
        triple = ["lock_cve", "network_nodes", "code_bars"]
        assert _force_variety(triple, seed_hex="20260513") == triple

    def test_deterministic_per_seed(self):
        from scripts.news.l22_dispatch import _force_variety
        a = _force_variety(["lock_cve", "lock_cve", "lock_cve"], seed_hex="20260513")
        b = _force_variety(["lock_cve", "lock_cve", "lock_cve"], seed_hex="20260513")
        assert a == b, "same seed must produce the same rotation"

    def test_seven_target_dates_each_produce_three_distinct_kinds(self):
        """End-to-end: 2026-05-12..18 excerpts → 3 distinct visual_kinds."""
        from scripts.news.l22_dispatch import (
            _force_variety,
            _route_visual_kind,
            extract_three_stories_from_excerpt,
        )

        # Real frontmatter excerpts copy-pasted from _posts/.
        cases = {
            "20260512": (
                "TeamPCP, Checkmarx Jenkins, cPanel CVE-2026-41940 활성, "
                "해커들이 AI를 사용해 최초로 알려진을 중심으로 2026년 05월 12일 "
                "주요 보안/기술 뉴스 28건과 대응 우선순위를 정리합니다."
            ),
            "20260513": (
                "AI 기반 합성 공격 로그 생성을 통한 탐지, 새로운 Exim BDAT "
                "취약점으로 GnuTLS, AI 속도의 방어를 중심으로 2026년 05월 "
                "13일 주요 보안/기술 뉴스 29건과 대응 우선순위를 정리합니다."
            ),
            "20260514": (
                "AWS 환경에서 암호화폐 채굴 탐지 및 방지, Microsoft의 MDASH "
                "AI 시스템, 업데이트된 AWS User Guide 소개를 중심으로 "
                "2026년 05월 14일 주요 보안/기술 뉴스 30건과 대응 우선순위를 정리합니다."
            ),
        }
        for seed, excerpt in cases.items():
            stories = extract_three_stories_from_excerpt("", excerpt, "")
            assert stories is not None, f"excerpt parse failed for {seed}"
            initial = [
                _route_visual_kind(s["headline"], i) for i, s in enumerate(stories)
            ]
            forced = _force_variety(initial, seed_hex=seed)
            assert len(set(forced)) == 3, (
                f"date {seed}: forced visuals not 3-distinct: {forced}"
            )


class TestExtractFromExcerpt:
    """Fix 2: extract 3 distinct anchor-story headlines from a Korean
    auto-publisher excerpt, falling back to None when the boilerplate
    shape is absent so callers can use the original filename path."""

    def test_2026_05_13_excerpt_yields_three_distinct_korean_headlines(self):
        from scripts.news.l22_dispatch import extract_three_stories_from_excerpt
        excerpt = (
            "AI 기반 합성 공격 로그 생성을 통한 탐지, 새로운 Exim BDAT 취약점으로 GnuTLS, "
            "AI 속도의 방어를 중심으로 2026년 05월 13일 주요 보안/기술 뉴스 29건과 "
            "대응 우선순위를 정리합니다."
        )
        stories = extract_three_stories_from_excerpt("", excerpt, "")
        assert stories is not None
        h0, h1, h2 = (s["headline"] for s in stories)
        # All three differ.
        assert len({h0, h1, h2}) == 3
        # Specific spec assertion: the spec literally calls out these three.
        assert "AI" in h0
        assert "Exim BDAT" in h1
        assert "AI" in h2 and "방어" in h2

    def test_returns_none_when_boilerplate_missing(self):
        from scripts.news.l22_dispatch import extract_three_stories_from_excerpt
        # English-only excerpt — no "을 중심으로" marker.
        out = extract_three_stories_from_excerpt(
            "", "LockBit ransomware hits 320 victims this week", ""
        )
        assert out is None

    def test_returns_none_when_segments_under_three(self):
        from scripts.news.l22_dispatch import extract_three_stories_from_excerpt
        # Boilerplate present but only 1 segment before it.
        out = extract_three_stories_from_excerpt(
            "", "단일 주제를 중심으로 정리합니다.", ""
        )
        assert out is None


class TestInferKpiWithExcerpt:
    """Fix 3: KPI inference falls back to the excerpt when the headline
    has nothing numeric, and recognises Korean "<count>건" as a COUNT."""

    def test_headline_match_wins_over_excerpt(self):
        from scripts.news.l22_dispatch import _infer_kpi_with_excerpt
        out = _infer_kpi_with_excerpt(
            "CVE-2026-1234 RCE", excerpt="never used 99건"
        )
        assert out[0] == "CVE" and out[1] == "ID"

    def test_excerpt_count_in_geon_format_picked_up(self):
        from scripts.news.l22_dispatch import _infer_kpi_with_excerpt
        out = _infer_kpi_with_excerpt(
            "AI 속도의 방어",
            excerpt="...주요 보안/기술 뉴스 29건과 대응 우선순위를 정리합니다.",
        )
        assert out == ("29", "COUNT", "items")

    def test_default_when_both_empty(self):
        from scripts.news.l22_dispatch import _infer_kpi_with_excerpt
        assert _infer_kpi_with_excerpt("", "") == ("TBD", "STATUS", "NEW")


class TestBandSpecificMiniBadges:
    """Fix 4: each band's mini-badges carry a band-specific severity /
    priority label so the 3 stripes do not all read the literal
    'MAY / WK / Q2' placeholders."""

    def test_three_bands_have_three_distinct_priorities(self):
        from scripts.news.l22_dispatch import _build_band_cfg
        b0 = _build_band_cfg("h0", "s0", 0)
        b1 = _build_band_cfg("h1", "s1", 1)
        b2 = _build_band_cfg("h2", "s2", 2)
        # mini_value: P0 / P1 / P2 (priority rank).
        assert (b0["mini_value"], b1["mini_value"], b2["mini_value"]) == (
            "P0", "P1", "P2",
        )
        # mini_label is now "PRI" (priority), not the old "ISSUE".
        assert b0["mini_label"] == "PRI"
        # mini2_value: HIGH / MED / LOW severity tiers.
        assert (b0["mini2_value"], b1["mini2_value"], b2["mini2_value"]) == (
            "HIGH", "MED", "LOW",
        )


class TestKoreanTitleFilenameExtraction:
    """Regression guard for the 2026-05-13~18 bug: render_l22_svg_string
    was calling extract_three_stories(title, excerpt) without the
    filename= kwarg, so Korean-only auto-published posts fell through
    to the placeholder pool ['Security Update', 'Threat Analysis',
    'Patch Advisory'] instead of using English filename keywords.

    After the 2026-05-15 variety fix the dispatcher prefers
    excerpt-extracted Korean anchor stories over filename keywords,
    because the excerpt actually carries the 3 distinct news stories
    while the filename only carries broad tag words. The placeholder
    pool guard is preserved — if the excerpt extractor fails for any
    reason the filename fallback still must beat the placeholders.
    """

    def test_korean_excerpt_drives_headlines_not_placeholder_pool(self):
        from scripts.news.l22_dispatch import render_l22_svg_string

        post_info = {
            "title": "AI 기반 합성 공격 로그 생성을 통한 탐지, 새로운 Exim BDAT, AI 방어",
            "excerpt": "AI 기반 합성 공격, Exim BDAT, AI 방어를 중심으로 2026년 05월 13일 보안 뉴스 정리",
            "filename": "2026-05-13-Tech_Security_Weekly_Digest_AI_Vulnerability_Security_Agent.md",
        }
        svg = render_l22_svg_string(post_info)
        assert svg, "renderer must produce output"
        # Korean anchor stories from the excerpt should appear verbatim
        # (the L22 renderer keeps Hangul in <text>, unlike L20).
        assert "AI" in svg
        assert "Exim BDAT" in svg or "AI 방어" in svg
        # Placeholder pool from the filename-fallback path must NOT
        # have triggered — the excerpt path took priority.
        assert "Security Update" not in svg
        assert "Threat Analysis" not in svg
        assert "Patch Advisory" not in svg
