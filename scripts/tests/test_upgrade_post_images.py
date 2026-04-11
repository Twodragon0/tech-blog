#!/usr/bin/env python3
"""Tests for upgrade_post_images.py helper logic."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.upgrade_post_images import (
    build_cover_title_lines,
    build_excerpt_lines,
    build_focus_lines,
    build_visual_concepts,
    english_tags,
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


def test_english_tags_preserves_common_acronyms():
    labels = english_tags(["aws", "llm", "cloud-security", "mfa"])

    assert "AWS" in labels
    assert "LLM" in labels
    assert "Cloud Security" in labels
    assert "Mfa" not in labels


def test_build_excerpt_lines_returns_two_short_lines():
    lines = build_excerpt_lines(
        "Prompt injection controls and identity hardening for multi-cloud workloads "
        "with budget guardrails and audit telemetry."
    )

    assert len(lines) == 2
    assert all(len(line) <= 34 for line in lines)
    assert "controls" in lines[0].lower() or "hardening" in lines[1].lower()


def test_build_excerpt_lines_falls_back_for_korean_heavy_excerpt():
    lines = build_excerpt_lines(
        "SK텔레콤 USIM 정보 유출 사태 완벽 대응 가이드. USIM/eSIM 즉시 교체 방법과 MFA 활성화.",
        fallback=["SKT", "MFA", "USIM"],
    )

    assert lines == ["SKT focus", "MFA priority"]


def test_build_cover_title_lines_falls_back_to_concepts_for_korean_titles():
    lines = build_cover_title_lines(
        "랜섬웨어 진화, LLM 탈옥 공격, K8s 공급망 위협 분석",
        ["Supply Chain", "Ransomware", "LLM", "Kubernetes"],
    )

    assert lines[:3] == ["Supply Chain", "Ransomware", "LLM"]


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
    assert ">PRIMARY<" in svg
    assert "Zero Trust" in svg or "AWS" in svg
