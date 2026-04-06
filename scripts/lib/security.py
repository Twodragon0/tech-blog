"""Centralized sensitive data masking and validation.

Consolidates mask_sensitive_info() and _validate_masked_text() previously
duplicated across 6+ scripts. All scripts should import from here.
"""

import os
import re


def mask_sensitive_info(text: str) -> str:
    """Mask API keys, tokens, and passwords from text before logging."""
    if not text:
        return text

    # API key patterns (sk-, sk-ant-, AIza, etc.)
    masked = re.sub(r"sk-ant-[a-zA-Z0-9_-]{20,}", "sk-ant-***MASKED***", text)
    masked = re.sub(r"sk-[a-zA-Z0-9_-]{20,}", "sk-***MASKED***", masked)
    masked = re.sub(r"AIza[0-9A-Za-z_-]{35}", "AIza***MASKED***", masked)

    # Mask actual API key values from environment
    for env_var in [
        "GEMINI_API_KEY",
        "CLAUDE_API_KEY",
        "DEEPSEEK_API_KEY",
        "OPENAI_API_KEY",
        "BUTTONDOWN_API_KEY",
    ]:
        key_val = os.getenv(env_var, "")
        if key_val and len(key_val) > 10:
            masked = masked.replace(key_val, f"***{env_var}_MASKED***")

    # URL key parameters
    masked = re.sub(r"[?&]key=[a-zA-Z0-9_-]+", "?key=***MASKED***", masked)

    # Generic long token patterns (40+ chars)
    masked = re.sub(
        r"[a-zA-Z0-9_-]{40,}",
        lambda m: m.group()[:8] + "***MASKED***" if len(m.group()) > 40 else m.group(),
        masked,
    )

    return masked


def validate_masked_text(text: str) -> bool:
    """Verify no sensitive data remains in text. Returns True if safe."""
    if not text:
        return True

    api_key_patterns = [
        r"sk-[a-zA-Z0-9_-]{20,}",
        r"sk-ant-[a-zA-Z0-9_-]{20,}",
        r"AIza[0-9A-Za-z_-]{35,}",
    ]

    for pattern in api_key_patterns:
        if re.search(pattern, text):
            return False

    # Check actual env var values
    for env_var in ["GEMINI_API_KEY", "CLAUDE_API_KEY", "DEEPSEEK_API_KEY"]:
        key_val = os.getenv(env_var, "")
        if key_val and len(key_val) > 10 and key_val in text:
            return False

    return True
