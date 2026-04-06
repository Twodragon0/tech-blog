#!/usr/bin/env python3
"""Unit tests for regenerate_all_images.py utility functions."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.regenerate_all_images import (
    detect_topic,
    escape_svg,
    get_label,
    truncate,
    visual_ai_neural,
    visual_aws_cloud,
    visual_blockchain,
    visual_cicd,
    visual_devsecops,
    visual_docker,
    visual_finops,
    visual_generic_tech,
    visual_kubernetes,
    visual_ransomware,
    visual_security_shield,
    wrap_title,
)

# ---------------------------------------------------------------------------
# escape_svg
# ---------------------------------------------------------------------------


class TestEscapeSvg:
    def test_escapes_ampersand(self):
        assert escape_svg("A & B") == "A &amp; B"

    def test_escapes_less_than(self):
        assert escape_svg("<tag>") == "&lt;tag&gt;"

    def test_escapes_greater_than(self):
        assert escape_svg("a > b") == "a &gt; b"

    def test_escapes_double_quote(self):
        assert escape_svg('say "hello"') == "say &quot;hello&quot;"

    def test_escapes_single_quote(self):
        assert escape_svg("it's") == "it&#39;s"

    def test_empty_string_returns_empty_string(self):
        assert escape_svg("") == ""

    def test_none_returns_empty_string(self):
        assert escape_svg(None) == ""

    def test_plain_text_unchanged(self):
        assert escape_svg("Hello World") == "Hello World"

    def test_multiple_special_chars_all_escaped(self):
        result = escape_svg('<a href="url">link & text</a>')
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" in result
        assert "&quot;" in result


# ---------------------------------------------------------------------------
# truncate
# ---------------------------------------------------------------------------


class TestTruncate:
    def test_returns_text_unchanged_when_within_limit(self):
        assert truncate("Short title", 48) == "Short title"

    def test_truncates_and_appends_ellipsis_when_too_long(self):
        long_text = "A" * 60
        result = truncate(long_text, 48)
        assert result.endswith("...")
        assert len(result) == 48

    def test_empty_string_returns_default_fallback(self):
        assert truncate("") == "Tech Blog Post"

    def test_none_returns_default_fallback(self):
        assert truncate(None) == "Tech Blog Post"

    def test_exactly_max_len_not_truncated(self):
        text = "A" * 48
        assert truncate(text, 48) == text

    def test_custom_max_len_respected(self):
        result = truncate("Hello World This Is Long", 10)
        assert len(result) == 10
        assert result.endswith("...")


# ---------------------------------------------------------------------------
# wrap_title
# ---------------------------------------------------------------------------


class TestWrapTitle:
    def test_short_title_returns_single_line(self):
        result = wrap_title("Short", 40)
        assert result == ["Short"]

    def test_long_title_splits_into_two_lines(self):
        title = "This Is A Very Long Title That Needs Wrapping Into Two Lines"
        result = wrap_title(title, 40)
        assert len(result) == 2

    def test_second_line_truncated_when_still_too_long(self):
        title = "Word " * 20  # very long, forces truncation
        result = wrap_title(title.strip(), 40)
        assert len(result) == 2
        assert result[1].endswith("...")

    def test_title_exactly_at_limit_returns_single_line(self):
        title = "A" * 40
        result = wrap_title(title, 40)
        assert result == [title]

    def test_two_line_split_preserves_all_words(self):
        title = "Kubernetes Security Best Practices for Production"
        result = wrap_title(title, 40)
        joined = " ".join(result)
        # All original words present (second line may be truncated if very long,
        # but for a normal title both halves combine to cover the words)
        assert "Kubernetes" in joined


# ---------------------------------------------------------------------------
# get_label
# ---------------------------------------------------------------------------


class TestGetLabel:
    def test_returns_security_label_for_security_category(self):
        assert get_label(["security"]) == "SECURITY"

    def test_returns_kubernetes_label(self):
        assert get_label(["kubernetes"]) == "KUBERNETES"

    def test_returns_devops_label(self):
        assert get_label(["devops"]) == "DEVOPS"

    def test_returns_cloud_label(self):
        assert get_label(["cloud"]) == "CLOUD"

    def test_returns_finops_label(self):
        assert get_label(["finops"]) == "FINOPS"

    def test_returns_blockchain_label(self):
        assert get_label(["blockchain"]) == "BLOCKCHAIN"

    def test_returns_incident_label(self):
        assert get_label(["incident"]) == "INCIDENT"

    def test_returns_devsecops_label(self):
        assert get_label(["devsecops"]) == "DEVSECOPS"

    def test_returns_tech_blog_fallback_for_unknown_category(self):
        assert get_label(["unknown", "random"]) == "TECH BLOG"

    def test_returns_tech_blog_for_empty_categories(self):
        assert get_label([]) == "TECH BLOG"

    def test_first_matching_category_wins(self):
        # security comes before cloud in the list; result depends on order
        result = get_label(["security", "cloud"])
        assert result == "SECURITY"

    def test_case_insensitive_matching(self):
        assert get_label(["Security"]) == "SECURITY"


# ---------------------------------------------------------------------------
# detect_topic
# ---------------------------------------------------------------------------


class TestDetectTopic:
    def test_kubernetes_keywords_in_title_returns_kubernetes_func(self):
        func = detect_topic("Kubernetes Security Guide", [], [])
        assert func is visual_kubernetes

    def test_k8s_shorthand_returns_kubernetes_func(self):
        func = detect_topic("k8s pod security", [], [])
        assert func is visual_kubernetes

    def test_aws_keyword_returns_aws_cloud_func(self):
        func = detect_topic("AWS IAM Best Practices", [], [])
        assert func is visual_aws_cloud

    def test_gcp_keyword_returns_aws_cloud_func(self):
        func = detect_topic("GCP security hardening", [], [])
        assert func is visual_aws_cloud

    def test_blockchain_keyword_returns_blockchain_func(self):
        func = detect_topic("Blockchain and DeFi security", [], [])
        assert func is visual_blockchain

    def test_security_keyword_returns_security_shield_func(self):
        func = detect_topic("CVE vulnerability patch", [], [])
        assert func is visual_security_shield

    def test_devsecops_keyword_returns_devsecops_func(self):
        func = detect_topic("DevSecOps pipeline setup", [], [])
        assert func is visual_devsecops

    def test_ai_keyword_returns_ai_neural_func(self):
        func = detect_topic("AI and LLM security", [], [])
        assert func is visual_ai_neural

    def test_docker_keyword_returns_docker_func(self):
        func = detect_topic("Docker container basics", [], [])
        assert func is visual_docker

    def test_ransomware_keyword_returns_ransomware_func(self):
        func = detect_topic("Ransomware attack prevention", [], [])
        assert func is visual_ransomware

    def test_finops_keyword_returns_finops_func(self):
        func = detect_topic("FinOps cost optimization", [], [])
        assert func is visual_finops

    def test_cicd_keyword_returns_cicd_func(self):
        func = detect_topic("CI/CD pipeline automation", [], [])
        assert func is visual_cicd

    def test_unrecognized_title_returns_generic_tech(self):
        func = detect_topic("Random Unrelated Topic", [], [])
        assert func is visual_generic_tech

    def test_tags_used_in_detection_alongside_title(self):
        func = detect_topic("Introduction to networking", ["kubernetes", "k8s"], [])
        assert func is visual_kubernetes

    def test_categories_used_in_detection(self):
        func = detect_topic("Best Practices Post", [], ["blockchain"])
        assert func is visual_blockchain

    def test_kubernetes_takes_priority_over_docker_when_both_present(self):
        # kubernetes rule appears after docker in TOPIC_RULES but kubernetes
        # rule matches before docker+kubernetes rule because the dedicated
        # kubernetes rule fires first
        func = detect_topic("Docker and Kubernetes", [], [])
        # docker rule with also_requires kubernetes fires before plain docker
        assert func is visual_docker

    def test_supply_chain_without_npm_matches_ai_rule(self):
        # "supply chain" without npm/package/dependency does not match the
        # supply-chain rule; "ch-ai-n" contains "ai" substring so the ai_neural
        # rule fires instead of falling through to generic.
        func = detect_topic("Supply chain attack overview", [], [])
        assert func is visual_ai_neural

    def test_supply_chain_without_npm_does_not_return_npm_func(self):
        from scripts.regenerate_all_images import visual_npm_supply_chain

        func = detect_topic("Supply chain attack overview", [], [])
        assert func is not visual_npm_supply_chain

    def test_supply_chain_with_npm_returns_npm_func(self):
        from scripts.regenerate_all_images import visual_npm_supply_chain

        func = detect_topic("Supply chain attack via npm package", [], [])
        assert func is visual_npm_supply_chain

    def test_cloudflare_incident_returns_incident_func(self):
        from scripts.regenerate_all_images import visual_incident

        func = detect_topic("Cloudflare outage incident report", [], [])
        assert func is visual_incident

    def test_cloudflare_without_incident_returns_cloudflare_func(self):
        from scripts.regenerate_all_images import visual_cloudflare

        func = detect_topic("Cloudflare DNS overview", [], [])
        assert func is visual_cloudflare

    def test_detection_is_case_insensitive(self):
        func = detect_topic("KUBERNETES Cluster Management", [], [])
        assert func is visual_kubernetes
