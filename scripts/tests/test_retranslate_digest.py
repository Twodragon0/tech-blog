"""Tests for scripts/retranslate_digest.py (재발 방지 B단계 correction pass).

The translation backends are fully MOCKED — no network. We monkeypatch the
Gemini entrypoint (`_gemini_call`) / `check_gemini_available` and the DeepSeek
helper on the retranslate_digest module namespace, so we exercise the real
detection -> translate -> write wiring without any API call.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import retranslate_digest as rt  # noqa: E402

# --- Fixtures -------------------------------------------------------------

# An English (untranslated) news-card + 요약 block, alongside a second card that
# is ALREADY Korean (must stay untouched). Includes a table and frontmatter to
# assert structure preservation.
_ENGLISH_TITLE = (
    "Attackers are exploiting a flaw in the Active Directory to escalate privileges"
)
_ENGLISH_SUMMARY = (
    "BlueNoroff, tracked as CVE-2026-1234, is operating an active phishing kit "
    "that impersonates the video platforms to deliver malware and to profile wallets."
)
_ENGLISH_BLOCK = (
    "BlueNoroff threat actors are running a phishing kit and are abusing "
    "CVE-2026-1234 to deliver malware to the victims in a social engineering campaign."
)
_KOREAN_TITLE = "AWS에서 Claude Opus 5 소개"
_KOREAN_SUMMARY = (
    "북한 위협 행위자들이 화상회의 플랫폼을 사칭하는 활성 피싱 키트를 운영하는 것으로 "
    "확인되었습니다."
)

_POST = f"""---
layout: post
title: "주간 다이제스트"
category: [security]
---
## 1. 보안 뉴스

### 1.1 English Item

{{% include news-card.html
  title="{_ENGLISH_TITLE}"
  url="https://thehackernews.com/example.html"
  summary="{_ENGLISH_SUMMARY}"
  source="The Hacker News"
  severity="High"
%}}

#### 요약

{_ENGLISH_BLOCK}


#### 위협 분석

| 항목 | 내용 |
|------|------|
| **CVE ID** | CVE-2026-1234 |
| **심각도** | High |

---

### 1.2 Korean Item

{{% include news-card.html
  title="{_KOREAN_TITLE}"
  url="https://aws.amazon.com/example"
  summary="{_KOREAN_SUMMARY}"
  source="AWS Security Blog"
  severity="Medium"
%}}

#### 요약

{_KOREAN_SUMMARY} 보안 영향도를 평가하고 필요 시 대응 조치를 수행하세요.

---
"""


def _fake_gemini(prompt, timeout=20):
    """A canned 'translator': returns Korean-dominant text that PRESERVES the
    CVE ID and the BlueNoroff proper noun found in the source, so we can assert
    preservation while keeping the output Korean (idempotent on re-run)."""
    m = re.search(r"원문:\s*(.*?)\n번역:", prompt, re.S)
    src = m.group(1) if m else prompt
    parts = ["이것은 한국어로 번역된 문장입니다."]
    cve = re.search(r"CVE-\d{4}-\d+", src)
    if cve:
        parts.append(f"이 취약점은 {cve.group(0)}로 추적되고 있습니다.")
    if "BlueNoroff" in src:
        parts.append("BlueNoroff 위협 행위자가 관련되어 있습니다.")
    return " ".join(parts)


def _mock_gemini(monkeypatch, call=_fake_gemini):
    monkeypatch.setattr(rt, "check_gemini_available", lambda: True)
    monkeypatch.setattr(rt, "_gemini_call", call)


# --- Detection -> translation wiring --------------------------------------

def test_translates_english_spans_and_preserves_structure(monkeypatch):
    _mock_gemini(monkeypatch)
    out, stats = rt.retranslate_text(_POST)

    # English title + summary field replaced; the English 요약 block replaced.
    assert stats == {"fields": 2, "blocks": 1}
    assert _ENGLISH_TITLE not in out
    assert _ENGLISH_SUMMARY not in out
    assert _ENGLISH_BLOCK not in out
    assert "이것은 한국어로 번역된 문장입니다." in out

    # Proper noun + CVE ID preserved through translation.
    assert "BlueNoroff" in out
    assert out.count("CVE-2026-1234") >= 2  # summary field + 요약 block (+ table)

    # Structure intact: both include blocks, frontmatter, table pipes.
    assert out.count("{% include news-card.html") == 2
    assert out.startswith("---\nlayout: post\n")
    assert "| **CVE ID** | CVE-2026-1234 |" in out

    # The already-Korean card is untouched.
    assert f'title="{_KOREAN_TITLE}"' in out
    assert f'summary="{_KOREAN_SUMMARY}"' in out


def test_summary_field_stays_single_line_without_inner_quotes(monkeypatch):
    _mock_gemini(monkeypatch)
    out, _ = rt.retranslate_text(_POST)
    for line in out.split("\n"):
        stripped = line.strip()
        if stripped.startswith("summary=") or stripped.startswith("title="):
            # opens and closes on one physical line, no raw inner double-quote.
            assert stripped.endswith('"')
            assert stripped[stripped.index('"') + 1: -1].count('"') == 0


def test_idempotent_second_run_is_noop(monkeypatch):
    _mock_gemini(monkeypatch)
    once, _ = rt.retranslate_text(_POST)
    twice, stats2 = rt.retranslate_text(once)
    assert twice == once
    assert stats2 == {"fields": 0, "blocks": 0}


# --- Output validation (security) -----------------------------------------

def test_output_validation_rejects_non_korean_and_keeps_original(monkeypatch):
    # Model returns English (no Hangul) -> validation fails -> original kept.
    _mock_gemini(monkeypatch, call=lambda prompt, timeout=20: "This is still English output")
    monkeypatch.setattr(rt, "_allow_deepseek", lambda: False)
    out, stats = rt.retranslate_text(_POST)
    assert out == _POST
    assert stats == {"fields": 0, "blocks": 0}


def test_output_validation_rejects_runaway_length(monkeypatch):
    # Korean but absurdly long (> MAX_LEN_RATIO x source) -> rejected.
    _mock_gemini(monkeypatch, call=lambda prompt, timeout=20: "가" * 5000)
    monkeypatch.setattr(rt, "_allow_deepseek", lambda: False)
    out, stats = rt.retranslate_text(_POST)
    assert out == _POST
    assert stats == {"fields": 0, "blocks": 0}


def test_output_validation_rejects_html_liquid_injection(monkeypatch):
    # M-01: a prompt-injected model response that keeps Hangul but smuggles
    # active HTML/Liquid must be rejected (fail-safe: original English kept),
    # so it can never land in a kramdown+Liquid-rendered post body.
    for payload in (
        "<script>steal()</script> 공격자가 코드를 실행합니다.",
        "{% raw %} 공격자가 코드를 실행합니다.",
        "{{ site.secret }} 공격자가 코드를 실행합니다.",
    ):
        _mock_gemini(monkeypatch, call=lambda prompt, timeout=20, p=payload: p)
        monkeypatch.setattr(rt, "_allow_deepseek", lambda: False)
        out, stats = rt.retranslate_text(_POST)
        assert out == _POST, f"payload leaked into output: {payload!r}"
        assert stats == {"fields": 0, "blocks": 0}


# --- DeepSeek fallback path ------------------------------------------------

def test_falls_back_to_deepseek_when_gemini_unavailable(monkeypatch):
    monkeypatch.setattr(rt, "check_gemini_available", lambda: False)
    monkeypatch.setattr(rt, "_allow_deepseek", lambda: True)
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key-not-real")

    def _fake_deepseek(text, context="기술 뉴스", mode="summary"):
        return "딥시크로 번역된 한국어 요약 문장입니다."

    monkeypatch.setattr(rt, "_translate_to_korean_deepseek", _fake_deepseek)
    out, stats = rt.retranslate_text(_POST)
    assert "딥시크로 번역된 한국어 요약 문장입니다." in out
    assert stats["fields"] == 2 and stats["blocks"] == 1


# --- Graceful no-op without keys ------------------------------------------

def test_no_backend_is_clean_noop(monkeypatch, tmp_path):
    monkeypatch.setattr(rt, "check_gemini_available", lambda: False)
    monkeypatch.setattr(rt, "_allow_deepseek", lambda: False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    assert rt.backend_available() is False

    post = tmp_path / "2026-07-25-Sample_Weekly_Digest_Test.md"
    post.write_text(_POST, encoding="utf-8")
    rc = rt.main([str(post)])
    assert rc == 0
    assert post.read_text(encoding="utf-8") == _POST  # unchanged


def test_main_writes_translation_to_file(monkeypatch, tmp_path):
    _mock_gemini(monkeypatch)
    post = tmp_path / "2026-07-25-Sample_Weekly_Digest_Test.md"
    post.write_text(_POST, encoding="utf-8")

    rc = rt.main([str(post)])
    assert rc == 0
    written = post.read_text(encoding="utf-8")
    assert _ENGLISH_TITLE not in written
    assert "이것은 한국어로 번역된 문장입니다." in written


def test_main_dry_run_does_not_write(monkeypatch, tmp_path):
    _mock_gemini(monkeypatch)
    post = tmp_path / "2026-07-25-Sample_Weekly_Digest_Test.md"
    post.write_text(_POST, encoding="utf-8")

    rc = rt.main([str(post), "--dry-run"])
    assert rc == 0
    assert post.read_text(encoding="utf-8") == _POST  # unchanged on dry-run
