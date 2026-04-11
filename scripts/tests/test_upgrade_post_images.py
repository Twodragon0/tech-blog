#!/usr/bin/env python3
"""Tests for upgrade_post_images.py helper logic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.upgrade_post_images import (
    build_focus_lines,
    build_visual_concepts,
    generate_svg,
    select_visual_variant,
)


def test_build_visual_concepts_prefers_specific_phrases_and_tags():
    concepts = build_visual_concepts(
        title="Zero Trust runtime guide for AWS",
        excerpt="Prompt injection controls for agentic AI on Kubernetes clusters.",
        tags=["aws", "zero-trust", "prompt-injection"],
        filepath="assets/images/2026-03-27-Tech_Security_Weekly_Digest_Zero_Trust_Cloud_FinOps.svg",
        theme="cloud",
    )

    assert "Zero Trust" in concepts
    assert any(label in concepts for label in ("AWS", "Cloud", "Prompt Injection"))
    assert len(concepts) == 4


def test_select_visual_variant_is_deterministic():
    variant_a = select_visual_variant(
        "security",
        "Threat landscape update",
        "assets/images/example.svg",
    )
    variant_b = select_visual_variant(
        "security",
        "Threat landscape update",
        "assets/images/example.svg",
    )

    assert variant_a == variant_b
    assert variant_a in {"orbit", "beacon", "editorial", "bands"}


def test_build_focus_lines_groups_concepts_into_two_lines():
    lines = build_focus_lines(["Zero Trust", "Cloud Fabric", "Patch Flow", "Runtime Guard"])

    assert len(lines) == 2
    assert "Zero Trust" in lines[0]
    assert "Patch Flow" in lines[1]


def test_generate_svg_embeds_variant_marker_and_focus_panel():
    svg = generate_svg(
        title="AWS Zero Trust Runtime Security",
        excerpt="Prompt injection and runtime guardrails for AI agents.",
        date_str="2026-03-27 09:00:00 +0900",
        tags=["aws", "zero-trust", "ai-agent"],
        categories=["security", "cloud"],
        theme="security",
        filepath="assets/images/test-upgrade-post.svg",
    )

    assert "profile: high-quality-cover; variant:" in svg
    assert ">FOCUS<" in svg
    assert "Zero Trust" in svg or "AWS" in svg
