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
import sys
from pathlib import Path

import pytest

from scripts.news import l20_dispatch
from scripts.news.l20_dispatch import (
    _infer_kpi,
    generate_l20_digest_svg,
)


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
        assert (
            captured["url"]
            == "https://tech.2twodragon.com/posts/2026/04/30/"
            "Tech-Security-Weekly-Digest-Ransomware/"
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
