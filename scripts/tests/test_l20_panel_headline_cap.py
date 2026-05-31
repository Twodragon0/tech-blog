#!/usr/bin/env python3
"""Unit tests for _fit_panel_headline() in scripts/lib/svg_l20_hero.py.

Guards against headline bleed past x=1024 in the L20 hero SVG panel.
Bug fixed in commit 14d51115.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from scripts.lib.svg_l20_hero import _fit_panel_headline


# ---------------------------------------------------------------------------
# 1. None input
# ---------------------------------------------------------------------------

def test_none_returns_empty_string():
    assert _fit_panel_headline(None) == ""


# ---------------------------------------------------------------------------
# 2. Short text unchanged
# ---------------------------------------------------------------------------

def test_short_text_unchanged():
    text = "Short headline"
    assert _fit_panel_headline(text) == text


# ---------------------------------------------------------------------------
# 3. Exact 27-char boundary passes verbatim
# ---------------------------------------------------------------------------

def test_exactly_27_chars_unchanged():
    text = "A" * 27
    assert len(text) == 27
    result = _fit_panel_headline(text)
    assert result == text


# ---------------------------------------------------------------------------
# 4. 28 chars -> ellipsis appears
# ---------------------------------------------------------------------------

def test_28_chars_truncates_with_ellipsis():
    text = "A" * 28
    result = _fit_panel_headline(text)
    assert result.endswith("...")
    assert len(result) <= 27


# ---------------------------------------------------------------------------
# 5. Property: result length <= max_chars for various long inputs
# ---------------------------------------------------------------------------

def test_result_never_exceeds_max_chars():
    inputs = [
        "X" * 28,
        "Hello World This Is A Very Long Headline That Goes On",
        "AWS Lambda function timeout configuration guide 2026",
        "Zero Day Exploit Disclosed in OpenSSL Library",
        "Kubernetes RBAC Misconfiguration Leads to Cluster Takeover",
    ]
    for text in inputs:
        result = _fit_panel_headline(text)
        assert len(result) <= 27, f"Overflowed for: {text!r} -> {result!r}"


# ---------------------------------------------------------------------------
# 6. Word boundary preferred
# ---------------------------------------------------------------------------

def test_word_boundary_preferred():
    # 31 chars; last space within budget is after "42001"
    text = "AWS Achieves ISO 42001 AI Audit"
    assert len(text) == 31
    result = _fit_panel_headline(text)
    assert result.endswith("...")
    assert len(result) <= 27
    # Must not hard-cut mid-word (result prefix must end cleanly)
    body = result[:-3]
    assert not body.endswith(" "), "No trailing space before ellipsis"
    # Word-boundary cut: body should be one of the space-delimited prefixes
    words = text.split()
    prefix_options = [" ".join(words[:i]) for i in range(1, len(words))]
    assert body in prefix_options, f"Expected word-boundary cut, got: {body!r}"


# ---------------------------------------------------------------------------
# 7. Hard cut when no late space
# ---------------------------------------------------------------------------

def test_hard_cut_when_no_late_space():
    # Space only at index 1 ("A BBBBB..."); budget=24, threshold=14; 1 < 14 -> hard cut at 24
    text = "A " + "B" * 30   # space at index 1, rest B's, total 32 chars
    assert len(text) > 27
    result = _fit_panel_headline(text)
    assert result.endswith("...")
    assert len(result) <= 27
    # Hard cut: body must be exactly s[:24] stripped (no trailing space here)
    body = result[:-3]
    assert body == text[:24].rstrip(), (
        f"Expected hard cut at budget=24, got: {body!r}"
    )


# ---------------------------------------------------------------------------
# 8. Custom max_chars honored
# ---------------------------------------------------------------------------

def test_custom_max_chars():
    text = "AWS Lambda Timeout Guide"  # 24 chars, fits at default=27
    result = _fit_panel_headline(text, max_chars=15)
    assert len(result) <= 15
    assert result.endswith("...")


# ---------------------------------------------------------------------------
# 9. Non-string input coerced via str()
# ---------------------------------------------------------------------------

def test_non_string_input_coerced():
    assert _fit_panel_headline(42) == "42"
    # Float within 27 chars -> returned as-is string
    result_float = _fit_panel_headline(3.14)
    assert isinstance(result_float, str)
    assert len(result_float) <= 27


# ---------------------------------------------------------------------------
# 10. Parametrized real-world overflow cases from commit 14d51115
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text,expected_prefix", [
    ("FortiCloud SSO Bypass Returns", "FortiCloud SSO Bypass"),
    ("AWS Serverless AI Defense Architecture", "AWS Serverless AI"),
    ("Voice Phishing Surge Targets Staff", "Voice Phishing Surge"),
    ("Go Crypto Package Backdoor Found", "Go Crypto Package"),
    ("25 Password Manager Recovery Attacks", "25 Password Manager"),
])
def test_real_overflow_cases_from_commit_14d51115(text, expected_prefix):
    result = _fit_panel_headline(text)
    assert len(result) <= 27, f"Overflow: {text!r} -> {result!r} ({len(result)} chars)"
    assert result.endswith("..."), f"Expected ellipsis: {result!r}"
    assert result.startswith(expected_prefix), (
        f"Expected prefix {expected_prefix!r}, got {result!r}"
    )
