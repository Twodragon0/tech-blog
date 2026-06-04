#!/usr/bin/env python3
"""Tests for the L20 content-post cover variant.

Covers the additive content-cover support layered on top of the L20
Hero+2-Card digest generator:

- ``render_l20_hero`` default eyebrow/footer_label preserve the digest
  branding byte-for-byte ("WEEKLY DIGEST" / "Weekly Digest") so existing
  digest covers do not drift.
- ``render_l20_hero`` honours custom eyebrow/footer_label (content covers).
- ``generate_l20_content_svg`` end-to-end on a Korean-title / English-slug
  ``post_info``: honest category eyebrow, content CTA, no "WEEKLY DIGEST",
  no Hangul in any ``<text>``, and the L20 profile marker.
- ``_content_eyebrow_from_category`` mapping (str / list / comma forms).
- Redundant-subtitle guard: a single-keyword headline never yields a
  subheadline equal to the headline.

API disabling and ``sys.path`` setup are handled by ``conftest.py``.
"""

import re

import pytest

from scripts.news.l20_dispatch import (
    _build_story,
    _CONTENT_HONEST_VISUALS,
    _content_eyebrow_from_category,
    _meaningful_content_keywords,
    _pad_subheadline,
    extract_content_stories,
    extract_three_stories,
    generate_l20_content_svg,
    route_visual_id,
)
from scripts.lib.svg_l20_hero import render_l20_hero


# A minimal but complete story dict for direct render_l20_hero calls.
def _story(headline: str, action: str = None) -> dict:
    s = {
        "tag": "HIGH",
        "index": "01",
        "theme": "blue",
        "visual": "neutral",
        "headline": headline,
        "subheadline": f"{headline} overview and context",
        "kpi_value": "TBD",
        "kpi_label": "STATUS",
        "kpi_sub": "NEW",
    }
    if action is not None:
        s["action"] = action
    return s


_HANGUL_RE = re.compile(r"[가-힣ᄀ-ᇿ㄰-㆏]")
_TEXT_RE = re.compile(r"<text\b[^>]*>(.*?)</text>", re.DOTALL)


def _texts(svg: str):
    return _TEXT_RE.findall(svg)


# =====================================================================
# Default eyebrow/footer regression guard (byte-identical digest output)
# =====================================================================


class TestRenderDefaultsPreserveDigestBranding:
    def test_default_eyebrow_is_weekly_digest(self):
        svg = render_l20_hero(
            date_str="2026.01.11",
            hero=_story("Vulnerability", action="READ THE FULL DIGEST"),
            top_right=_story("Patch"),
            bottom_right=_story("Advisory"),
            url="https://tech.2twodragon.com/posts/2026/01/11/Sample/",
            post_title="Weekly Security Digest - 2026.01.11",
        )
        assert ">WEEKLY DIGEST</text>" in svg
        assert "Weekly Digest  /  2026.01.11" in svg


# =====================================================================
# Custom eyebrow/footer (content covers)
# =====================================================================


class TestRenderCustomEyebrowFooter:
    def test_content_eyebrow_and_footer_render(self):
        svg = render_l20_hero(
            date_str="2026.01.11",
            hero=_story("Container Hardening", action="READ THE FULL GUIDE"),
            top_right=_story("Policy"),
            bottom_right=_story("Runtime"),
            url="https://tech.2twodragon.com/posts/2026/01/11/Sample/",
            post_title="DevSecOps Guide - 2026.01.11",
            eyebrow="DEVSECOPS GUIDE",
            footer_label="DevSecOps Guide",
        )
        assert ">DEVSECOPS GUIDE</text>" in svg
        assert "DevSecOps Guide  /  2026.01.11" in svg
        assert "WEEKLY DIGEST" not in svg


# =====================================================================
# _content_eyebrow_from_category mapping
# =====================================================================


class TestContentEyebrowFromCategory:
    @pytest.mark.parametrize(
        "category,expected",
        [
            ("security", "SECURITY GUIDE"),
            ("devsecops", "DEVSECOPS GUIDE"),
            ("devops", "DEVOPS GUIDE"),
            ("cloud", "CLOUD GUIDE"),
            ("kubernetes", "KUBERNETES GUIDE"),
            ("finops", "FINOPS GUIDE"),
            ("blockchain", "BLOCKCHAIN GUIDE"),
            ("incident", "INCIDENT REPORT"),
            ("DevSecOps", "DEVSECOPS GUIDE"),  # case-insensitive
            ("unknown", "TECH GUIDE"),
            ("", "TECH GUIDE"),
        ],
    )
    def test_scalar_category(self, category, expected):
        assert _content_eyebrow_from_category(category) == expected

    def test_list_category_uses_first(self):
        assert _content_eyebrow_from_category(["cloud", "security"]) == "CLOUD GUIDE"

    def test_comma_string_uses_first(self):
        assert _content_eyebrow_from_category("kubernetes, devops") == "KUBERNETES GUIDE"


# =====================================================================
# generate_l20_content_svg end-to-end (real renderer, grep output)
# =====================================================================


class TestGenerateL20ContentSvg:
    def test_content_cover_is_honest_and_english_only(self, tmp_path):
        post_info = {
            "title": "쿠버네티스 컨테이너 보안 완벽 가이드",  # Korean -> filename fallback
            "excerpt": "런타임 보안과 정책 적용을 단계별로 설명합니다",
            "category": "devsecops",
            "filename": "2026-01-11-Kubernetes_Container_Security_Runtime_Policy_Guide.md",
        }
        out = tmp_path / "cover.svg"
        ok = generate_l20_content_svg(post_info, out)
        assert ok is True
        svg = out.read_text(encoding="utf-8")

        # Honest category eyebrow + content CTA, NO digest branding.
        assert ">DEVSECOPS GUIDE</text>" in svg
        assert "READ THE FULL GUIDE" in svg
        assert "WEEKLY DIGEST" not in svg
        assert "READ THE FULL DIGEST" not in svg

        # L20 profile marker present.
        assert "profile: high-quality-cover (L20 Hero+2-Card)" in svg

        # No Hangul anywhere in <text> (check-svg-quality gate requirement).
        for body in _texts(svg):
            assert not _HANGUL_RE.search(body), f"Hangul leaked into <text>: {body!r}"

    def test_incident_uses_report_cta_and_eyebrow(self, tmp_path):
        post_info = {
            "title": "Production Outage Postmortem",
            "excerpt": "Root cause, timeline, and remediation",
            "category": "incident",
            "filename": "2026-01-11-Production_Outage_Postmortem_Root_Cause.md",
        }
        out = tmp_path / "cover.svg"
        assert generate_l20_content_svg(post_info, out) is True
        svg = out.read_text(encoding="utf-8")
        assert ">INCIDENT REPORT</text>" in svg
        assert "READ THE FULL REPORT" in svg
        assert "WEEKLY DIGEST" not in svg


# =====================================================================
# Honest visual clamping (content_mode)
# =====================================================================

# Attack motif strings that render_l20_hero embeds when an attack visual
# is routed. None of these must appear in a content cover SVG.
_ATTACK_MOTIF_STRINGS = [
    "BYPASS AUTHZ",
    "DATA EXFILTRATION",
    "VICTIM",
    "RANSOM NOTE",
    "DARK APP",
    "PATCH UPSTREAM NOW",
    "GATE TOOL CALLS",
    "VERIFY SLSA",
    "ROTATE TOKENS",
    "BLOCK C2",
]


class TestContentHonestVisuals:
    """content_mode=True in _build_story must clamp attack visuals to neutral."""

    _ATTACK_HEADLINES = [
        "Kubernetes",    # routes container_escape without clamping
        "Docker",        # routes container_escape
        "Credential",    # routes data_exfil
        "Router",        # routes hub_spoke
        "Agentic",       # routes ai_agent_funnel
        "npm",           # routes supply_chain_pipe
    ]

    def test_honest_set_constant_defined(self):
        assert "neutral" in _CONTENT_HONEST_VISUALS
        assert "security_advisory" in _CONTENT_HONEST_VISUALS
        assert "market" in _CONTENT_HONEST_VISUALS
        # Attack visuals must NOT be in the honest set.
        for attack in ("container_escape", "data_exfil", "hub_spoke",
                       "ai_agent_funnel", "supply_chain_pipe",
                       "cve_chain", "ransomware_lock", "code_injection"):
            assert attack not in _CONTENT_HONEST_VISUALS, (
                f"attack visual {attack!r} should not be in honest set"
            )

    @pytest.mark.parametrize("headline", _ATTACK_HEADLINES)
    def test_content_mode_clamps_attack_visual(self, headline):
        raw_visual = route_visual_id(headline)
        assert raw_visual not in _CONTENT_HONEST_VISUALS, (
            f"precondition: {headline!r} must route to an attack visual, got {raw_visual!r}"
        )
        story = _build_story(
            headline=headline, subheadline="x", index=0,
            severity_label="HIGH", content_mode=True,
        )
        assert story["visual"] in _CONTENT_HONEST_VISUALS, (
            f"content_mode did not clamp {raw_visual!r} for headline {headline!r}"
        )
        assert story["visual"] == "neutral"

    @pytest.mark.parametrize("headline", _ATTACK_HEADLINES)
    def test_digest_mode_keeps_attack_visual(self, headline):
        """content_mode=False (digest default) must NOT clamp routing."""
        raw_visual = route_visual_id(headline)
        story = _build_story(
            headline=headline, subheadline="x", index=0,
            severity_label="HIGH", content_mode=False,
        )
        assert story["visual"] == raw_visual

    def test_content_cover_svg_no_attack_motifs(self, tmp_path):
        """End-to-end: a 'Kubernetes / Docker / Container' content post must
        not render any attack-motif string in the SVG output."""
        post_info = {
            "title": "Kubernetes Docker Container Security Guide",
            "excerpt": "",
            "category": "devsecops",
            "filename": "2026-01-11-Kubernetes_Docker_Container_Security_Guide.md",
        }
        out = tmp_path / "cover.svg"
        assert generate_l20_content_svg(post_info, out) is True
        svg = out.read_text(encoding="utf-8")
        for motif in _ATTACK_MOTIF_STRINGS:
            assert motif not in svg, (
                f"attack motif {motif!r} present in content cover SVG"
            )

    def test_honest_visuals_pass_through_unchanged(self):
        """neutral / security_advisory / market must not be clamped."""
        for headline, expected_visual in [
            ("Bitcoin $71K",   "market"),
            ("Chainalysis",    "neutral"),
        ]:
            story = _build_story(
                headline=headline, subheadline="x", index=0,
                severity_label="HIGH", content_mode=True,
            )
            assert story["visual"] == expected_visual, (
                f"honest visual {expected_visual!r} was changed for {headline!r}"
            )


# =====================================================================
# Redundant-subtitle guard
# =====================================================================


class TestRedundantSubtitleGuard:
    def test_single_keyword_sub_not_equal_headline(self):
        # A title yielding a single repeated keyword used to render
        # sub == headline ("Vulnerability" / "Vulnerability").
        hero, tr, br = extract_three_stories(
            "Vulnerability",
            "",
            "2026-01-11-Vulnerability.md",
        )
        for story in (hero, tr, br):
            assert (
                story["subheadline"].strip().lower()
                != story["headline"].strip().lower()
            ), f"redundant subtitle: {story!r}"

    def test_pad_subheadline_borrows_sibling_when_redundant(self):
        sub = _pad_subheadline("Vulnerability", "", other_headlines=["Patch Advisory"])
        assert sub.lower() != "vulnerability"
        assert sub.lower().startswith("vulnerability -")

    def test_pad_subheadline_neutral_when_no_sibling(self):
        sub = _pad_subheadline("Vulnerability", "", other_headlines=[])
        assert sub.lower() != "vulnerability"
        assert "security topic overview" in sub.lower()

    def test_pad_subheadline_keeps_distinct_sub(self):
        # When the segment already carries enough material, behavior is
        # unchanged (no spurious descriptor appended).
        seg = "Cloud cost optimization with FinOps tagging"
        sub = _pad_subheadline(seg, "", other_headlines=["Other"])
        assert sub.lower().startswith("cloud cost optimization")


# =====================================================================
# extract_content_stories + _meaningful_content_keywords (filler filter)
# =====================================================================


_FILLER_WORDS = {"latest", "update", "complete", "guide", "analysis",
                 "perspective", "view", "overview", "intro", "summary",
                 "2025", "2026", "top"}


class TestMeaningfulContentKeywords:
    def test_owasp_drops_filler_tokens(self):
        # Korean title -> filename fallback path; filler stripped from slug.
        kws = _meaningful_content_keywords(
            "2026-01-03-OWASP_2025_Latest_Update_Complete_Guide_Top_10_Agentic_AI_Security.md",
            "OWASP 2025 최신 업데이트 완벽 가이드",  # Korean title
        )
        for kw in kws:
            assert kw.lower() not in _FILLER_WORDS, f"filler keyword kept: {kw!r}"
        assert "OWASP" in kws

    def test_cloud_keywords_all_meaningful(self):
        kws = _meaningful_content_keywords(
            "2026-01-05-Cloud_Security_AWS_WAF_CloudFront_Kubernetes.md",
            "클라우드 보안",  # Korean
        )
        for kw in kws:
            assert kw.lower() not in _FILLER_WORDS, f"filler kept: {kw!r}"
        assert "Cloud" in kws
        assert "AWS" in kws

    def test_english_title_compound_phrase(self):
        # "AI Security" is extracted as a compound phrase before word-level
        # scan; the subsequent word scan deduplicates "AI" and "Security"
        # as individual tokens via seen_lower.
        kws = _meaningful_content_keywords(
            "2026-01-11-AI_Security.md",
            "AI Security Best Practices Guide",
        )
        assert "AI Security" in kws
        # Dedup: "AI" and "Security" as bare tokens must not also appear.
        kws_lower = [k.lower() for k in kws]
        assert kws_lower.count("ai") == 0
        assert kws_lower.count("security") == 0

    def test_digit_led_tokens_dropped(self):
        # "8Batch", "6Week" must not appear — they are course ordinals, not topics.
        kws = _meaningful_content_keywords(
            "2026-01-08-Cloud_Security_Course_8Batch_6Week_AWS_WAF_CloudFront_"
            "Security_Architecture_And_GitHub_DevSecOps_Practical.md",
            "",
        )
        for kw in kws:
            assert not kw[0].isdigit(), f"digit-led token survived: {kw!r}"
        assert "AWS" in kws

    def test_dedup_case_insensitive(self):
        # "Security" appears in both filename slug and title: only one copy kept.
        kws = _meaningful_content_keywords(
            "2026-01-11-Security_Guide.md",
            "Security Hardening Practices",
        )
        lowers = [k.lower() for k in kws]
        assert lowers.count("security") <= 1


class TestExtractContentStories:
    def test_owasp_no_filler_headlines(self):
        """Real OWASP scenario: Korean title + filler-laden filename slug."""
        h, t, b = extract_content_stories(
            "OWASP 2025 최신 업데이트 완벽 가이드: Top 10과 에이전틱 AI 보안",
            "",
            "2026-01-03-OWASP_2025_Latest_Update_Complete_Guide_Top_10_Agentic_AI_Security.md",
            eyebrow="SECURITY GUIDE",
        )
        all_headlines = [h["headline"], t["headline"], b["headline"]]
        for hl in all_headlines:
            assert hl.lower() not in _FILLER_WORDS, f"filler headline: {hl!r}"
        # OWASP must survive as a headline (it's the primary topic).
        assert "OWASP" in all_headlines

    def test_subheadlines_not_equal_to_headline(self):
        """Content stories must never yield sub == headline."""
        h, t, b = extract_content_stories(
            "OWASP 2025 최신 업데이트 완벽 가이드: Top 10과 에이전틱 AI 보안",
            "",
            "2026-01-03-OWASP_2025_Latest_Update_Complete_Guide_Top_10_Agentic_AI_Security.md",
            eyebrow="SECURITY GUIDE",
        )
        for story in (h, t, b):
            assert story["subheadline"].strip().lower() != story["headline"].strip().lower(), (
                f"redundant subtitle: {story!r}"
            )

    def test_blockchain_all_topics_meaningful(self):
        h, t, b = extract_content_stories(
            "블록체인 기술 완벽 가이드",
            "",
            "2026-01-04-Blockchain_Cryptocurrency_Security_Complete_Guide.md",
            eyebrow="BLOCKCHAIN GUIDE",
        )
        for story in (h, t, b):
            assert story["headline"].lower() not in _FILLER_WORDS

    def test_digest_extract_three_stories_unchanged(self):
        """extract_three_stories (digest path) behavior must not change."""
        # A digest title with comma separators still splits correctly.
        h, t, b = extract_three_stories(
            "Weekly digest 2026-04-30: Ransomware, AI agent, Cloud",
            "Ransomware wave hits banks; AI agents jailbroken; S3 leak",
            "2026-04-30-Tech_Security_Weekly_Digest_Ransomware.md",
        )
        assert h["headline"] == "Ransomware"
        assert t["headline"] == "AI agent"
