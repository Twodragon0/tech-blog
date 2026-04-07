#!/usr/bin/env python3
"""Targeted tests for SVG cover/banner generation helpers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.generate_post_images import (
    _detect_digest_nodes,
    _compose_cover_headline,
    _extract_visual_tokens,
    generate_fallback_svg,
    generate_section_banner_svg,
)


def test_extract_visual_tokens_prefers_english_security_terms():
    post_info = {
        "title": "AI Agent 보안 아키텍처",
        "excerpt": "Prompt injection and MCP runtime hardening",
        "category": "security",
        "tags": ["AI", "MCP", "Prompt-Injection"],
    }

    tokens = _extract_visual_tokens(post_info, limit=5)

    assert "AI AGENT" in tokens
    assert "PROMPT INJECTION" in tokens
    assert "MCP" in tokens


def test_compose_cover_headline_falls_back_to_ascii_tokens():
    post_info = {
        "title": "보안 아키텍처 실무 가이드",
        "category": "security",
        "tags": ["AI", "Security", "MCP"],
    }
    tokens = _extract_visual_tokens(post_info, limit=4)

    lines = _compose_cover_headline(post_info, tokens)

    assert len(lines) == 2
    assert all(line == line.encode("ascii", "ignore").decode("ascii") for line in lines)
    assert any(line for line in lines)


def test_compose_cover_headline_adds_second_line_for_single_english_phrase():
    post_info = {
        "title": "Prompt Injection Defense",
        "category": "security",
        "tags": ["MCP"],
    }
    tokens = _extract_visual_tokens(post_info, limit=4)

    lines = _compose_cover_headline(post_info, tokens)

    assert len(lines) == 2
    assert all(lines)


def test_detect_digest_nodes_handles_non_string_tags():
    nodes = _detect_digest_nodes(
        {"title": "AI Agent 보안", "tags": ["MCP", 2026, "Cloud"]}
    )

    assert "ai" in nodes or "cloud" in nodes


def test_generate_section_banner_svg_contains_expected_label():
    svg = generate_section_banner_svg("section-cloud.svg")

    assert "<svg" in svg
    assert "CLOUD" in svg
    assert "SECTION BANNER" in svg
    assert "POST NAVIGATION" in svg


def test_generate_fallback_svg_writes_modernized_cover(tmp_path):
    output_path = tmp_path / "sample.svg"
    post_info = {
        "title": "AI Agent 보안 아키텍처",
        "category": "security",
        "tags": ["AI", "MCP", "Runtime"],
        "excerpt": "Prompt injection and runtime isolation",
        "filename": "2026-02-28-AI_Agent_Security_Architecture_Design_Guide.md",
    }

    assert generate_fallback_svg(post_info, output_path) is True

    svg = output_path.with_suffix(".svg").read_text(encoding="utf-8")
    assert 'width="1200" height="630"' in svg
    assert 'width="None" height="None"' not in svg
    assert "VISUAL SYSTEM" in svg
    assert "CATEGORY" in svg
