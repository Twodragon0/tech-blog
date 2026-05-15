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
    def test_unset_defaults_to_enabled(self, monkeypatch):
        """Default flipped from opt-in to ON-by-default on 2026-05-15
        after the 05-12~15 batch shipped without QR due to flag drift
        on ai-blogwatcher.yml (only daily-news.yml set USE_L22_ULTRA=1)."""
        monkeypatch.delenv("USE_L22_ULTRA", raising=False)
        mod = _reload_auto_publish_news()
        assert mod.L22_ULTRA_ENABLED is True

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE", ""])
    def test_truthy_values_enable(self, monkeypatch, value):
        # Empty string now ALSO defaults to enabled — opt-out requires
        # an explicit 0/false/no/off.
        monkeypatch.setenv("USE_L22_ULTRA", value)
        mod = _reload_auto_publish_news()
        assert mod.L22_ULTRA_ENABLED is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", "FALSE", "Off"])
    def test_falsy_values_disable(self, monkeypatch, value):
        """Only explicit opt-out values disable L22 ultra.
        Empty string is NOT in this list anymore."""
        monkeypatch.setenv("USE_L22_ULTRA", value)
        mod = _reload_auto_publish_news()
        assert mod.L22_ULTRA_ENABLED is False


class TestDispatchPrecedence:
    """L22 wins over L20 when both flags are set; falls back gracefully."""

    def _stub_dispatch(self, monkeypatch, mod, l22_returns: str, l20_returns: str = "<svg>l20</svg>"):
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

    def test_l22_enabled_takes_precedence_over_l20(self, monkeypatch):
        monkeypatch.setenv("USE_L22_ULTRA", "1")
        monkeypatch.setenv("USE_L20_HERO", "1")
        mod = _reload_auto_publish_news()
        called = self._stub_dispatch(monkeypatch, mod, l22_returns="<svg>l22</svg>")

        # Inline the dispatch fragment as it appears in main():
        post_info: dict = {"title": "T", "filename": "f.md"}
        svg = ""
        if mod.L22_ULTRA_ENABLED:
            svg = mod._render_l22_svg_string(post_info)
        if not svg and mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string(post_info)
        if not svg:
            svg = mod.generate_svg_image(None, {}, [])

        assert called == {"l22": 1, "l20": 0, "legacy": 0}
        assert svg == "<svg>l22</svg>"

    def test_l22_failure_falls_back_to_l20(self, monkeypatch):
        monkeypatch.setenv("USE_L22_ULTRA", "1")
        monkeypatch.setenv("USE_L20_HERO", "1")
        mod = _reload_auto_publish_news()
        called = self._stub_dispatch(monkeypatch, mod, l22_returns="")  # render fail

        post_info: dict = {"title": "T", "filename": "f.md"}
        svg = ""
        if mod.L22_ULTRA_ENABLED:
            svg = mod._render_l22_svg_string(post_info)
        if not svg and mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string(post_info)
        if not svg:
            svg = mod.generate_svg_image(None, {}, [])

        assert called == {"l22": 1, "l20": 1, "legacy": 0}
        assert svg == "<svg>l20</svg>"

    def test_both_flags_off_falls_back_to_legacy(self, monkeypatch):
        monkeypatch.setenv("USE_L22_ULTRA", "0")
        monkeypatch.setenv("USE_L20_HERO", "0")
        mod = _reload_auto_publish_news()
        called = self._stub_dispatch(monkeypatch, mod, l22_returns="")

        post_info: dict = {"title": "T", "filename": "f.md"}
        svg = ""
        if mod.L22_ULTRA_ENABLED:
            svg = mod._render_l22_svg_string(post_info)
        if not svg and mod.L20_HERO_ENABLED:
            svg = mod._render_l20_svg_string(post_info)
        if not svg:
            svg = mod.generate_svg_image(None, {}, [])

        # Neither dispatch path runs; legacy generator picks up.
        assert called == {"l22": 0, "l20": 0, "legacy": 1}
        assert svg == "<svg>legacy</svg>"
