#!/usr/bin/env python3
"""Tests for the L20 flag wiring inside generate_post_images.process_post().

Covers the four dispatch paths for a Weekly Digest post when Gemini is
unavailable (no API key), so the SVG generators are the only option:

1. L20 flag enabled + generator succeeds  → L20 called, L22 NOT called.
2. L20 flag enabled + generator returns False → falls back to L22.
3. L20 flag enabled + generator raises → warning logged, falls back to L22.
4. L20 flag disabled                    → L20 NOT called, L22 called.

The module-level ``L20_HERO_ENABLED`` and ``_generate_l20_digest_svg``
attributes are monkey-patched on the ``generate_post_images`` module so the
tests are fully isolated from the real l20_dispatch module.

``sys.path`` setup and API disabling are handled by ``conftest.py``.
"""

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Module under test -- imported once; we monkeypatch attributes per test.
# ---------------------------------------------------------------------------
import scripts.generate_post_images as _gpi


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DIGEST_POST_INFO: Dict[str, Any] = {
    "title": "Tech Security Weekly Digest",
    "date": "2026-04-30",
    "filename": "2026-04-30-Tech_Security_Weekly_Digest.md",
    "content": "## AI Agent Security\n\n## CVE Update\n\n## Cloud Breach",
    "tags": ["weekly-digest"],
    "categories": ["security"],
    "image": "/assets/images/2026-04-30-Tech_Security_Weekly_Digest.svg",
}


def _make_output_path(tmp_path: Path) -> Path:
    return tmp_path / "2026-04-30-Tech_Security_Weekly_Digest.svg"


# ---------------------------------------------------------------------------
# Test: L20 path used when flag enabled and generator succeeds
# ---------------------------------------------------------------------------


def test_l20_path_used_when_flag_enabled_and_generator_succeeds(
    monkeypatch, tmp_path
):
    l20_stub = MagicMock(return_value=True)
    l22_stub = MagicMock(return_value=True)

    monkeypatch.setattr(_gpi, "L20_HERO_ENABLED", True)
    monkeypatch.setattr(_gpi, "_generate_l20_digest_svg", l20_stub)
    monkeypatch.setattr(_gpi, "generate_l22_digest_svg", l22_stub)
    # Ensure Gemini is disabled so we reach SVG path.
    monkeypatch.setattr(_gpi, "GEMINI_API_KEY", "")
    # Make _is_digest_post return True.
    monkeypatch.setattr(_gpi, "_is_digest_post", lambda _: True)
    # Stub dependent helpers so no disk I/O.
    monkeypatch.setattr(_gpi, "generate_digest_svg", MagicMock(return_value=False))
    monkeypatch.setattr(_gpi, "generate_fallback_svg", MagicMock(return_value=True))
    monkeypatch.setattr(_gpi, "save_prompt_file", MagicMock())
    monkeypatch.setattr(_gpi, "generate_image_prompt", MagicMock(return_value="prompt"))
    monkeypatch.setattr(_gpi, "check_image_exists", MagicMock(return_value=(False, None)))
    monkeypatch.setattr(_gpi, "extract_post_info", MagicMock(return_value=_DIGEST_POST_INFO))
    monkeypatch.setattr(_gpi, "IMAGES_DIR", tmp_path)

    post_file = tmp_path / "2026-04-30-Tech_Security_Weekly_Digest.md"
    post_file.write_text("---\ntitle: Test\n---\ncontent")

    result = _gpi.process_post(post_file, force=True)

    assert result is True
    l20_stub.assert_called_once()
    l22_stub.assert_not_called()


# ---------------------------------------------------------------------------
# Test: Falls back to L22 when L20 returns False
# ---------------------------------------------------------------------------


def test_falls_back_to_l22_when_l20_returns_false(monkeypatch, tmp_path):
    l20_stub = MagicMock(return_value=False)
    l22_stub = MagicMock(return_value=True)

    monkeypatch.setattr(_gpi, "L20_HERO_ENABLED", True)
    monkeypatch.setattr(_gpi, "_generate_l20_digest_svg", l20_stub)
    monkeypatch.setattr(_gpi, "generate_l22_digest_svg", l22_stub)
    monkeypatch.setattr(_gpi, "GEMINI_API_KEY", "")
    monkeypatch.setattr(_gpi, "_is_digest_post", lambda _: True)
    monkeypatch.setattr(_gpi, "generate_digest_svg", MagicMock(return_value=False))
    monkeypatch.setattr(_gpi, "generate_fallback_svg", MagicMock(return_value=True))
    monkeypatch.setattr(_gpi, "save_prompt_file", MagicMock())
    monkeypatch.setattr(_gpi, "generate_image_prompt", MagicMock(return_value="prompt"))
    monkeypatch.setattr(_gpi, "check_image_exists", MagicMock(return_value=(False, None)))
    monkeypatch.setattr(_gpi, "extract_post_info", MagicMock(return_value=_DIGEST_POST_INFO))
    monkeypatch.setattr(_gpi, "IMAGES_DIR", tmp_path)

    post_file = tmp_path / "2026-04-30-Tech_Security_Weekly_Digest.md"
    post_file.write_text("---\ntitle: Test\n---\ncontent")

    result = _gpi.process_post(post_file, force=True)

    assert result is True
    l20_stub.assert_called_once()
    l22_stub.assert_called_once()


# ---------------------------------------------------------------------------
# Test: Falls back to L22 when L20 raises
# ---------------------------------------------------------------------------


def test_falls_back_to_l22_when_l20_raises(monkeypatch, tmp_path, capsys):
    def _l20_raise(*args, **kwargs):
        raise RuntimeError("L20 boom")

    l22_stub = MagicMock(return_value=True)
    warned: list = []

    # Capture log_message calls to verify warning is emitted.
    original_log = _gpi.log_message

    def _spy_log(msg, level="INFO"):
        if level == "WARNING":
            warned.append(msg)
        original_log(msg, level)

    monkeypatch.setattr(_gpi, "L20_HERO_ENABLED", True)
    monkeypatch.setattr(_gpi, "_generate_l20_digest_svg", _l20_raise)
    monkeypatch.setattr(_gpi, "generate_l22_digest_svg", l22_stub)
    monkeypatch.setattr(_gpi, "log_message", _spy_log)
    monkeypatch.setattr(_gpi, "GEMINI_API_KEY", "")
    monkeypatch.setattr(_gpi, "_is_digest_post", lambda _: True)
    monkeypatch.setattr(_gpi, "generate_digest_svg", MagicMock(return_value=False))
    monkeypatch.setattr(_gpi, "generate_fallback_svg", MagicMock(return_value=True))
    monkeypatch.setattr(_gpi, "save_prompt_file", MagicMock())
    monkeypatch.setattr(_gpi, "generate_image_prompt", MagicMock(return_value="prompt"))
    monkeypatch.setattr(_gpi, "check_image_exists", MagicMock(return_value=(False, None)))
    monkeypatch.setattr(_gpi, "extract_post_info", MagicMock(return_value=_DIGEST_POST_INFO))
    monkeypatch.setattr(_gpi, "IMAGES_DIR", tmp_path)

    post_file = tmp_path / "2026-04-30-Tech_Security_Weekly_Digest.md"
    post_file.write_text("---\ntitle: Test\n---\ncontent")

    result = _gpi.process_post(post_file, force=True)

    assert result is True
    l22_stub.assert_called_once()
    assert any("L20" in w or "폴백" in w for w in warned), (
        f"Expected a warning mentioning L20 fallback; got: {warned}"
    )


# ---------------------------------------------------------------------------
# Test: L22 used when flag disabled
# ---------------------------------------------------------------------------


def test_l22_used_when_flag_disabled(monkeypatch, tmp_path):
    l20_stub = MagicMock(return_value=True)
    l22_stub = MagicMock(return_value=True)

    monkeypatch.setattr(_gpi, "L20_HERO_ENABLED", False)
    monkeypatch.setattr(_gpi, "_generate_l20_digest_svg", l20_stub)
    monkeypatch.setattr(_gpi, "generate_l22_digest_svg", l22_stub)
    monkeypatch.setattr(_gpi, "GEMINI_API_KEY", "")
    monkeypatch.setattr(_gpi, "_is_digest_post", lambda _: True)
    monkeypatch.setattr(_gpi, "generate_digest_svg", MagicMock(return_value=False))
    monkeypatch.setattr(_gpi, "generate_fallback_svg", MagicMock(return_value=True))
    monkeypatch.setattr(_gpi, "save_prompt_file", MagicMock())
    monkeypatch.setattr(_gpi, "generate_image_prompt", MagicMock(return_value="prompt"))
    monkeypatch.setattr(_gpi, "check_image_exists", MagicMock(return_value=(False, None)))
    monkeypatch.setattr(_gpi, "extract_post_info", MagicMock(return_value=_DIGEST_POST_INFO))
    monkeypatch.setattr(_gpi, "IMAGES_DIR", tmp_path)

    post_file = tmp_path / "2026-04-30-Tech_Security_Weekly_Digest.md"
    post_file.write_text("---\ntitle: Test\n---\ncontent")

    result = _gpi.process_post(post_file, force=True)

    assert result is True
    l20_stub.assert_not_called()
    l22_stub.assert_called_once()
