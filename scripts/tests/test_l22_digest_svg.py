#!/usr/bin/env python3
"""Tests for the L22 stacked-bands SVG generator integration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.generate_post_images import (
    _DIGEST_TITLE_PATTERN,
    _extract_digest_topics,
    _is_digest_post,
    generate_l22_digest_svg,
)
from scripts.lib import svg_l22_generator as l22


def test_digest_title_regex_matches_expected_patterns():
    cases = [
        "Weekly Digest 2026-03-19",
        "주간 다이제스트 03-19",
        "Tech_Security_Weekly_Digest_Zero-Day",
        "Daily_Tech_Digest_AI",
    ]
    for title in cases:
        assert _DIGEST_TITLE_PATTERN.search(title), f"missed: {title}"


def test_digest_title_regex_skips_non_digest():
    assert not _DIGEST_TITLE_PATTERN.search("AI Agent Security Architecture")
    assert not _DIGEST_TITLE_PATTERN.search("FinOps Cost Optimization Guide")


def test_is_digest_post_by_filename_pattern():
    info = {
        "title": "보안 다이제스트",
        "filename": "2026-03-20-Tech_Security_Weekly_Digest_Foo.md",
        "category": "security",
    }
    assert _is_digest_post(info) is True


def test_is_digest_post_rejects_regular_post():
    info = {
        "title": "Kubernetes Best Practices",
        "filename": "2026-03-20-Kubernetes_Guide.md",
        "category": "kubernetes",
    }
    assert _is_digest_post(info) is False


def test_extract_digest_topics_skips_boilerplate_h2():
    body = """## 서론
intro body

## 📊 빠른 참조
ref body

## 1. 보안 뉴스

### 1.1 Zero-day in Cisco FMC

content here

## 2. AI/ML 뉴스

### 2.1 LLM jailbreak study

more content

## 3. 클라우드 & 인프라 뉴스

### 3.1 Kubernetes Helm CVE-2026-2341
"""
    topics = _extract_digest_topics(body, max_topics=3)
    assert len(topics) == 3
    assert "Zero-day in Cisco FMC" in topics
    assert "LLM jailbreak study" in topics
    assert any("Helm" in t for t in topics)
    # Boilerplate H2 must not leak in.
    assert "서론" not in topics
    assert "📊 빠른 참조" not in topics


def test_generate_l22_digest_svg_writes_valid_svg(tmp_path):
    body = """## 서론
intro

## 1. 보안 뉴스

### 1.1 Ransomware campaign hits 320 victims

## 2. AI/ML 뉴스

### 2.1 LLM prompt injection defense

## 3. 클라우드 뉴스

### 3.1 Kubernetes RBAC privilege escalation
"""
    post_info = {
        "title": "Tech Security Weekly Digest 2026-03-19",
        "filename": "2026-03-19-Tech_Security_Weekly_Digest_Demo.md",
        "category": "security",
        "tags": ["security", "ransomware", "kubernetes"],
        "excerpt": "Weekly security digest",
        "content": body,
    }
    output_path = tmp_path / "demo.svg"
    assert generate_l22_digest_svg(post_info, output_path) is True

    svg_text = output_path.with_suffix(".svg").read_text(encoding="utf-8")
    # Sanity: real SVG with the expected viewport.
    assert svg_text.startswith("<svg")
    assert 'viewBox="0 0 1200 630"' in svg_text
    # All three bands rendered.
    assert "bandAL22" in svg_text
    assert "bandBL22" in svg_text
    assert "bandCL22" in svg_text
    # Line count in the documented operating range for the L22 layout.
    line_count = svg_text.count("\n") + 1
    assert 100 <= line_count <= 400, f"unexpected line count: {line_count}"


def test_l22_render_bands_svg_requires_three_bands():
    import pytest

    def _band(theme):
        return {
            "theme": theme,
            "label": "X",
            "headline": "Y",
            "metric": "M",
            "detail": "D",
            "badge_value": "1",
            "badge_label": "L",
            "badge_sub": "S",
            "visual": "",
        }

    # Two bands should raise; three bands should render.
    with pytest.raises(ValueError):
        l22.render_bands_svg(
            sfx="T",
            aria="t",
            title="t",
            url="https://example.test/",
            bands_cfg=[_band("red"), _band("amber")],
        )

    svg = l22.render_bands_svg(
        sfx="T",
        aria="t",
        title="t",
        url="https://example.test/",
        bands_cfg=[_band("red"), _band("amber"), _band("green")],
    )
    assert "<svg" in svg and "</svg>" in svg
