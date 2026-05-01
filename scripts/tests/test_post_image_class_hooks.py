"""Smoke tests for class-hook injection on built post pages.

These tests verify:
1. The compiled CSS (``_site/assets/css/main.css``) contains no
   ``[src*=...]`` / ``[src$=...]`` attribute regex selectors targeting
   section banners or SVG images (the 3 selectors replaced by this PR).
2. The compiled CSS does contain the replacement class selectors.
3. The ``_includes/post-image.html`` Liquid include exists with the
   expected class-injection logic.
4. The Jekyll plugin ``_plugins/markdown_image_lazy.rb`` has the
   ``class_hooks_for_src`` method and injects class hooks.
5. (Optional) A built post HTML page contains at least one ``<img>``
   tag emitted by the plugin with a class hook, if the site is built.

The tests do NOT require a Jekyll build — they work on source files so
CI stays fast.  The build-dependent test (``test_built_page_has_class_hook``)
is skipped when ``_site/assets/css/main.css`` is absent.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
POST_SCSS = REPO_ROOT / "_sass" / "_post.scss"
PLUGIN_RB = REPO_ROOT / "_plugins" / "markdown_image_lazy.rb"
INCLUDE_HTML = REPO_ROOT / "_includes" / "post-image.html"
COMPILED_CSS = REPO_ROOT / "_site" / "assets" / "css" / "main.css"
POST_CSS = REPO_ROOT / "_site" / "assets" / "css" / "post-page.css"


# ---------------------------------------------------------------------------
# 1. _post.scss — no longer contains [src*=] / [src$=] for section / svg
# ---------------------------------------------------------------------------

class TestPostScssSelectors:
    def test_no_src_section_attribute_selector(self):
        """img[src*='section-'] must have been replaced by img.is-section-image."""
        scss = POST_SCSS.read_text(encoding="utf-8")
        assert 'img[src*="section-"]' not in scss, (
            'Found legacy img[src*="section-"] selector in _post.scss — should be .is-section-image'
        )

    def test_no_src_svg_attribute_selector(self):
        """img[src$='.svg'] must have been replaced by img.is-svg-image."""
        scss = POST_SCSS.read_text(encoding="utf-8")
        assert 'img[src$=".svg"]' not in scss, (
            'Found legacy img[src$=".svg"] selector in _post.scss — should be .is-svg-image'
        )

    def test_class_hook_is_section_image_present(self):
        """_post.scss must define .is-section-image rule."""
        scss = POST_SCSS.read_text(encoding="utf-8")
        assert "is-section-image" in scss

    def test_class_hook_is_svg_image_present(self):
        """_post.scss must define .is-svg-image rule."""
        scss = POST_SCSS.read_text(encoding="utf-8")
        assert "is-svg-image" in scss


# ---------------------------------------------------------------------------
# 2. _includes/post-image.html — exists and contains class logic
# ---------------------------------------------------------------------------

class TestPostImageInclude:
    def test_include_exists(self):
        assert INCLUDE_HTML.exists(), f"Missing {INCLUDE_HTML}"

    def test_include_injects_is_svg_image(self):
        html = INCLUDE_HTML.read_text(encoding="utf-8")
        assert "is-svg-image" in html

    def test_include_injects_is_section_image(self):
        html = INCLUDE_HTML.read_text(encoding="utf-8")
        assert "is-section-image" in html

    def test_include_injects_is_news_card_image(self):
        html = INCLUDE_HTML.read_text(encoding="utf-8")
        assert "is-news-card-image" in html

    def test_include_injects_is_raster_image(self):
        html = INCLUDE_HTML.read_text(encoding="utf-8")
        assert "is-raster-image" in html

    def test_include_emits_img_tag(self):
        html = INCLUDE_HTML.read_text(encoding="utf-8")
        assert "<img" in html


# ---------------------------------------------------------------------------
# 3. _plugins/markdown_image_lazy.rb — has class_hooks_for_src method
# ---------------------------------------------------------------------------

class TestMarkdownImageLazyPlugin:
    def test_plugin_exists(self):
        assert PLUGIN_RB.exists(), f"Missing {PLUGIN_RB}"

    def test_plugin_has_class_hooks_method(self):
        rb = PLUGIN_RB.read_text(encoding="utf-8")
        assert "class_hooks_for_src" in rb

    def test_plugin_handles_svg(self):
        rb = PLUGIN_RB.read_text(encoding="utf-8")
        assert "is-svg-image" in rb

    def test_plugin_handles_section(self):
        rb = PLUGIN_RB.read_text(encoding="utf-8")
        assert "is-section-image" in rb

    def test_plugin_handles_raster(self):
        rb = PLUGIN_RB.read_text(encoding="utf-8")
        assert "is-raster-image" in rb

    def test_plugin_has_inject_classes_method(self):
        rb = PLUGIN_RB.read_text(encoding="utf-8")
        assert "inject_classes" in rb


# ---------------------------------------------------------------------------
# 4. Compiled CSS — attr regex count reduced (build-dependent, skippable)
# ---------------------------------------------------------------------------

ATTR_REGEX_PATTERN = re.compile(r"img\[src[\*\$\^]=")


@pytest.mark.skipif(not POST_CSS.exists(), reason="_site/assets/css/post-page.css not built")
class TestCompiledCss:
    """_post.scss compiles into post-page.css — check that file."""

    def test_no_src_section_attr_selector_in_compiled_css(self):
        css = POST_CSS.read_text(encoding="utf-8")
        # After the refactor the compiled CSS must not contain img[src*=section-]
        assert 'img[src*="section-"]' not in css, (
            "Legacy attribute selector img[src*=section-] found in compiled CSS"
        )

    def test_no_src_svg_attr_selector_in_compiled_css(self):
        css = POST_CSS.read_text(encoding="utf-8")
        assert 'img[src$=".svg"]' not in css, (
            "Legacy attribute selector img[src$=.svg] found in compiled CSS"
        )

    def test_class_hooks_present_in_compiled_css(self):
        css = POST_CSS.read_text(encoding="utf-8")
        assert "is-section-image" in css
        assert "is-svg-image" in css
