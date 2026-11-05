"""Regression coverage for publisher proxy patch cleanup and brand leads."""

import types

import auto_publish_news
import pytest

from scripts.news.l20_dispatch import (
    _AI_COMPOUND_ADJECTIVES,
    _DEFERRED_AI_ADJECTIVES,
    build_lead_headline,
)


def test_proxy_deletes_attributes_on_backing_module():
    real = types.ModuleType("publisher_regression")
    def original_renderer():
        return "real-svg"
    real._render_l20_svg_string = original_renderer
    proxy = auto_publish_news._ConfigProxy(real)
    with pytest.MonkeyPatch.context() as patch:
        # Undo visits the absent legacy generator first. It must not abort
        # before restoring the real renderer (the CI empty-SVG cascade).
        patch.setattr(proxy, "_render_l20_svg_string", lambda: "")
        patch.setattr(proxy, "generate_svg_image", lambda: "patched", raising=False)
        assert real.generate_svg_image() == "patched"
    assert not hasattr(real, "generate_svg_image")
    assert proxy._render_l20_svg_string is original_renderer


def test_openai_ai_lead_is_vetted_brand_not_compound_adjective():
    title = "OpenAI AI 파이프라인, 30시간 실행으로 948개의 Linux 권한 상승 익스플로잇 생성"
    assert build_lead_headline(title) == "OpenAI"
    assert "openai" in _DEFERRED_AI_ADJECTIVES
    assert "openai" not in _AI_COMPOUND_ADJECTIVES
