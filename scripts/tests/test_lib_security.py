#!/usr/bin/env python3
"""Unit tests for scripts/lib/security.py masking and validation functions."""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.lib.security import mask_sensitive_info, validate_masked_text


# ---------------------------------------------------------------------------
# mask_sensitive_info
# ---------------------------------------------------------------------------

class TestMaskSensitiveInfo:
    def test_masks_sk_ant_api_key(self):
        text = "Key is sk-ant-api03-abcdefghijklmnopqrstuvwxyz"
        result = mask_sensitive_info(text)
        assert "sk-ant-***MASKED***" in result
        assert "abcdefghijklmnopqrstuvwxyz" not in result

    def test_masks_sk_prefix_api_key(self):
        text = "Token: sk-abcdefghijklmnopqrstuvwxyz1234"
        result = mask_sensitive_info(text)
        assert "sk-***MASKED***" in result

    def test_masks_aiza_google_api_key(self):
        text = "key=AIzaSyAbcdefghijklmnopqrstuvwxyz1234567"
        result = mask_sensitive_info(text)
        assert "AIza***MASKED***" in result

    def test_masks_url_key_parameter(self):
        text = "https://api.example.com/data?key=supersecretapikey123"
        result = mask_sensitive_info(text)
        assert "?key=***MASKED***" in result
        assert "supersecretapikey123" not in result

    def test_masks_url_key_with_ampersand(self):
        text = "https://api.example.com/data?foo=bar&key=anothersecretkey"
        result = mask_sensitive_info(text)
        assert "***MASKED***" in result

    def test_masks_generic_long_token_over_40_chars(self):
        long_token = "a" * 45
        result = mask_sensitive_info(long_token)
        assert "***MASKED***" in result
        assert long_token not in result

    def test_does_not_mask_short_strings(self):
        short = "hello"
        result = mask_sensitive_info(short)
        assert result == "hello"

    def test_empty_string_returned_unchanged(self):
        assert mask_sensitive_info("") == ""

    def test_none_like_falsy_returned_unchanged(self):
        # The function guards with `if not text: return text`
        assert mask_sensitive_info("") == ""

    def test_plain_text_without_secrets_unchanged(self):
        text = "This is a normal log message with no secrets."
        result = mask_sensitive_info(text)
        assert result == text

    def test_masks_env_var_value_when_set(self, monkeypatch):
        secret = "my-very-secret-api-key-value-12345"
        monkeypatch.setenv("GEMINI_API_KEY", secret)
        text = f"Using key: {secret}"
        result = mask_sensitive_info(text)
        assert secret not in result
        assert "GEMINI_API_KEY_MASKED" in result

    def test_sk_ant_masked_before_sk_to_preserve_specificity(self):
        # sk-ant- keys must be masked with sk-ant-***MASKED***, not sk-***MASKED***
        text = "sk-ant-api03-" + "x" * 25
        result = mask_sensitive_info(text)
        assert "sk-ant-***MASKED***" in result


# ---------------------------------------------------------------------------
# validate_masked_text
# ---------------------------------------------------------------------------

class TestValidateMaskedText:
    def test_returns_true_for_clean_text(self):
        assert validate_masked_text("No secrets here.") is True

    def test_returns_true_for_empty_string(self):
        assert validate_masked_text("") is True

    def test_returns_false_when_sk_key_present(self):
        text = "Token sk-abcdefghijklmnopqrstuvwxyz1234 found"
        assert validate_masked_text(text) is False

    def test_returns_false_when_sk_ant_key_present(self):
        text = "sk-ant-api03-abcdefghijklmnopqrstuvwxyz"
        assert validate_masked_text(text) is False

    def test_returns_false_when_aiza_key_present(self):
        text = "AIzaSyAbcdefghijklmnopqrstuvwxyz1234567"
        assert validate_masked_text(text) is False

    def test_returns_true_after_masking_applied(self):
        raw = "sk-ant-api03-" + "z" * 30
        masked = mask_sensitive_info(raw)
        assert validate_masked_text(masked) is True

    def test_returns_false_when_env_var_value_present(self, monkeypatch):
        secret = "my-detectable-secret-value-xyz999"
        monkeypatch.setenv("GEMINI_API_KEY", secret)
        assert validate_masked_text(f"key={secret}") is False

    def test_returns_true_when_env_var_not_set(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        assert validate_masked_text("clean text") is True

    def test_masked_placeholder_text_passes_validation(self):
        text = "sk-ant-***MASKED*** is safe to log"
        assert validate_masked_text(text) is True
