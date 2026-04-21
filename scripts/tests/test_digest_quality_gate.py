"""Unit tests for the digest quality gate in auto_publish_news.

Covers _run_digest_quality_gate() in isolation using tmp_path fixtures.
Does NOT invoke main(). Pattern follows test_auto_publish_qa.py.
"""

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is on sys.path so auto_publish_news and digest_quality_report
# are importable without a package prefix.
_SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from auto_publish_news import _run_digest_quality_gate  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_DIGEST_NAME = "2026-04-20-Tech_Security_Weekly_Digest_Test.md"
_NON_DIGEST_NAME = "2026-04-20-Tech_Security_Weekly_Test.md"

_CLEAN_CONTENT = """\
---
layout: post
title: Test Digest
---

| 영역 | 핵심 내용 | 주요 키워드 |
|------|-----------|-------------|
| AI/LLM | 공격자가 LLM 프롬프트 인젝션 취약점을 악용해 민감한 데이터를 탈취했습니다. | CVE-2026-0001 |
"""

_TRUNCATED_CONTENT = """\
---
layout: post
title: Test Digest
---

| 영역 | 핵심 내용 | 주요 키워드 |
|------|-----------|-------------|
| AI/LLM | 공격자가 LLM 프롬프트 인젝션을 통해 민감한 데이터를 탈취하기 위한 | CVE-2026-0001 |
"""

_ENGLISH_HEADER_CONTENT = """\
---
layout: post
title: Test Digest
---

| 영역 | 핵심 내용 | 주요 키워드 |
|------|-----------|-------------|
| **Random Header** | 관련 시스템에서 보안 패치가 배포되었습니다. | CVE-2026-0002 |
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestDigestQualityGate:
    def test_non_digest_post_skipped(self, tmp_path, capsys):
        """Files without 'Digest' in name are skipped entirely (always True)."""
        p = tmp_path / _NON_DIGEST_NAME
        p.write_text(_TRUNCATED_CONTENT, encoding="utf-8")
        result = _run_digest_quality_gate(p, strict=True)
        assert result is True
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_clean_digest_passes(self, tmp_path):
        """A well-formed Digest post returns True with no output."""
        p = tmp_path / _DIGEST_NAME
        p.write_text(_CLEAN_CONTENT, encoding="utf-8")
        result = _run_digest_quality_gate(p, strict=True)
        assert result is True

    def test_truncated_cell_strict_fails(self, tmp_path, capsys):
        """Truncated table cell causes strict gate to return False."""
        p = tmp_path / _DIGEST_NAME
        p.write_text(_TRUNCATED_CONTENT, encoding="utf-8")
        result = _run_digest_quality_gate(p, strict=True)
        assert result is False
        captured = capsys.readouterr()
        assert "FAILED" in captured.out
        assert "TRUNCATED" in captured.out

    def test_truncated_cell_force_warns(self, tmp_path, capsys):
        """With strict=False the gate warns but returns True (non-blocking)."""
        p = tmp_path / _DIGEST_NAME
        p.write_text(_TRUNCATED_CONTENT, encoding="utf-8")
        result = _run_digest_quality_gate(p, strict=False)
        assert result is True
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "TRUNCATED" in captured.out

    def test_english_only_header_fails(self, tmp_path, capsys):
        """An English-only header not in the allowed list causes strict failure."""
        p = tmp_path / _DIGEST_NAME
        p.write_text(_ENGLISH_HEADER_CONTENT, encoding="utf-8")
        result = _run_digest_quality_gate(p, strict=True)
        assert result is False
        captured = capsys.readouterr()
        assert "FAILED" in captured.out
        assert "ENGLISH HEADER" in captured.out
