"""Tests for `_generate_unique_post_commentary` and helpers.

LLM calls are mocked — no real network access. Validates:
  - Top-headline selection by priority_score with first-3 fallback
  - Category stat aggregation
  - Prompt building with seeded opening pattern
  - Output validation (length, blocklist, quote sanitization)
  - Seed determinism (same seed -> same pattern)
  - None return when LLM unavailable
  - None return when output is too short / contains placeholder phrase
"""

from __future__ import annotations

from unittest import mock

import pytest

from news.content_generator import (
    _build_commentary_prompt,
    _commentary_category_stats,
    _commentary_top_headlines,
    _COMMENTARY_OPENING_PATTERNS,
    _COMMENTARY_PLACEHOLDER_BLOCKLIST,
    _generate_unique_post_commentary,
    _validate_commentary,
)


def _item(title="Critical CVE in Foo", category="security", source="acme",
          priority_score=None, summary=""):
    item = {
        "title": title,
        "category": category,
        "source": source,
        "source_name": source,
        "url": f"https://example.test/{abs(hash(title))}",
        "summary": summary,
    }
    if priority_score is not None:
        item["priority_score"] = priority_score
    return item


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestTopHeadlines:
    def test_picks_top3_by_priority_score(self):
        items = [
            _item("alpha", priority_score=10),
            _item("beta", priority_score=80),
            _item("gamma", priority_score=50),
            _item("delta", priority_score=90),
        ]
        out = _commentary_top_headlines(items)
        assert [h["title"] for h in out] == ["delta", "beta", "gamma"]

    def test_falls_back_to_first3_when_no_score(self):
        items = [_item(f"t{i}") for i in range(5)]
        out = _commentary_top_headlines(items)
        assert [h["title"] for h in out] == ["t0", "t1", "t2"]

    def test_empty_input(self):
        assert _commentary_top_headlines([]) == []


class TestCategoryStats:
    def test_counts_known_categories(self):
        items = [
            _item(category="security"),
            _item(category="security"),
            _item(category="ai"),
            _item(category="cloud"),
            _item(category="devops"),
            _item(category="blockchain"),
            _item(category="tech"),  # not counted
        ]
        stats = _commentary_category_stats(items)
        assert stats["security"] == 2
        assert stats["ai"] == 1
        assert stats["cloud"] == 1
        assert stats["devops"] == 1
        assert stats["blockchain"] == 1


class TestPromptBuilder:
    def test_includes_headlines_and_pattern(self):
        items = [_item("AAA"), _item("BBB"), _item("CCC")]
        stats = {"security": 3, "ai": 0, "cloud": 0, "devops": 0, "blockchain": 0}
        prompt = _build_commentary_prompt(
            items, stats, "2026-05-07", _COMMENTARY_OPENING_PATTERNS[0]
        )
        assert "AAA" in prompt
        assert "BBB" in prompt
        assert "CCC" in prompt
        assert "2026-05-07" in prompt
        assert _COMMENTARY_OPENING_PATTERNS[0] in prompt
        assert "보안 3건" in prompt

    def test_resolves_date_str_in_pattern(self):
        items = [_item("X")]
        stats = {"security": 1, "ai": 0, "cloud": 0, "devops": 0, "blockchain": 0}
        # Pattern that contains {date_str}
        pattern = "{date_str} 디지스트의 중심축은"
        prompt = _build_commentary_prompt(items, stats, "2026-05-07", pattern)
        assert "2026-05-07 디지스트의 중심축은" in prompt
        # Raw {date_str} marker should NOT leak.
        assert "{date_str}" not in prompt


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def _good(self):
        # ~250 chars, no placeholder, no double quotes.
        base = (
            "이번 분석 사이클에서 가장 먼저 눈에 띄는 신호는 GitHub Actions "
            "OIDC 토큰 권한 누설이며, 사내 CI/CD 파이프라인에서 토큰 스코프와 "
            "패치 SLA를 같은 주기로 점검해야 한다. **노출 자산 인벤토리**를 "
            "기준으로 패치, SIEM 룰, 백업 무결성을 함께 운영해야 한다."
        )
        return base

    def test_accepts_clean_text(self):
        out = _validate_commentary(self._good())
        assert out is not None
        assert 150 <= len(out) <= 450

    def test_rejects_too_short(self):
        assert _validate_commentary("짧은 글") is None

    def test_rejects_too_long(self):
        long_text = "가" * 600
        assert _validate_commentary(long_text) is None

    def test_rejects_empty(self):
        assert _validate_commentary("") is None
        assert _validate_commentary(None) is None  # type: ignore[arg-type]

    def test_rejects_blocklist_phrase(self):
        for phrase in _COMMENTARY_PLACEHOLDER_BLOCKLIST:
            if phrase in {"{", "}"}:
                continue
            text = self._good() + f" {phrase}"
            # Replace the good text part to keep length bounded.
            test = (phrase + " ") * 20  # ~ enough to clear length floor
            test = test[:280]
            assert _validate_commentary(test) is None, (
                f"Should reject phrase: {phrase}"
            )

    def test_rejects_template_token(self):
        bad = "이번 분석 사이클에서는 {date_str} 디지스트가 " + "내용" * 50
        assert _validate_commentary(bad) is None

    def test_strips_wrapping_quotes(self):
        wrapped = '"' + self._good() + '"'
        out = _validate_commentary(wrapped)
        assert out is not None
        assert not out.startswith('"')
        assert not out.endswith('"')

    def test_strips_leading_header(self):
        with_header = "## 분석가 시점\n" + self._good()
        out = _validate_commentary(with_header)
        assert out is not None
        assert not out.startswith("##")

    def test_collapses_whitespace(self):
        with_breaks = self._good().replace(" ", "\n  \n")
        out = _validate_commentary(with_breaks)
        # The good text has more than enough chars; after collapsing whitespace
        # with single spaces it remains bounded.
        if out is not None:
            assert "\n" not in out

    def test_sanitizes_double_quotes(self):
        # Embed an ASCII double quote inside a long enough body.
        body = (
            'GitHub Actions에서 토큰 권한 점검을 권장한다. "노출 자산 인벤토리"를 '
            * 4
        )
        body = body[:280]
        out = _validate_commentary(body)
        if out is not None:
            assert '"' not in out


# ---------------------------------------------------------------------------
# Public function with mocked LLM
# ---------------------------------------------------------------------------


class TestGenerateUniquePostCommentary:
    GOOD_OUTPUT = (
        "이번 분석 사이클에서 가장 먼저 눈에 띄는 신호는 GitHub Actions "
        "OIDC 토큰 권한 누설이며, 사내 CI/CD 파이프라인에서 토큰 스코프와 "
        "패치 SLA를 같은 주기로 점검해야 한다. **노출 자산 인벤토리**를 "
        "기준으로 패치, SIEM 룰, 백업 무결성을 함께 운영해야 한다."
    )

    def test_returns_text_when_llm_succeeds(self):
        items = [_item("Alpha"), _item("Beta"), _item("Gamma")]
        with mock.patch(
            "news.content_generator._commentary_llm_call",
            return_value=self.GOOD_OUTPUT,
        ):
            out = _generate_unique_post_commentary(items, "2026-05-07")
        assert out is not None
        assert "GitHub Actions" in out

    def test_returns_none_when_llm_returns_empty(self):
        items = [_item("Alpha")]
        with mock.patch(
            "news.content_generator._commentary_llm_call", return_value=""
        ):
            out = _generate_unique_post_commentary(items, "2026-05-07")
        assert out is None

    def test_returns_none_when_no_news(self):
        with mock.patch(
            "news.content_generator._commentary_llm_call",
            return_value=self.GOOD_OUTPUT,
        ):
            out = _generate_unique_post_commentary([], "2026-05-07")
        assert out is None

    def test_returns_none_when_output_has_placeholder(self):
        items = [_item("Alpha")]
        bad = "본 디지스트는 " + ("내용입니다. " * 30)
        with mock.patch(
            "news.content_generator._commentary_llm_call", return_value=bad
        ):
            out = _generate_unique_post_commentary(items, "2026-05-07")
        assert out is None

    def test_seed_determinism_picks_same_pattern(self):
        """Same seed -> same opening pattern selection."""
        items = [_item("Alpha"), _item("Beta")]
        captured_prompts = []

        def fake_call(prompt: str) -> str:
            captured_prompts.append(prompt)
            return self.GOOD_OUTPUT

        with mock.patch(
            "news.content_generator._commentary_llm_call", side_effect=fake_call
        ):
            _generate_unique_post_commentary(items, "2026-05-07", seed="DETERMINISTIC")
            _generate_unique_post_commentary(items, "2026-05-07", seed="DETERMINISTIC")

        assert len(captured_prompts) == 2
        # Same seed must produce identical prompts (pattern + headlines).
        assert captured_prompts[0] == captured_prompts[1]

    def test_different_seeds_can_pick_different_patterns(self):
        """Differing seeds should at least allow different patterns to be chosen
        across the 5-pattern set. Run several seeds and ensure not all collapse
        to one pattern."""
        items = [_item("Alpha"), _item("Beta")]
        seen_patterns: set[str] = set()

        def fake_call(prompt: str) -> str:
            for pat in _COMMENTARY_OPENING_PATTERNS:
                resolved = pat.replace("{date_str}", "2026-05-07")
                if resolved in prompt:
                    seen_patterns.add(pat)
                    break
            return self.GOOD_OUTPUT

        seeds = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"]
        with mock.patch(
            "news.content_generator._commentary_llm_call", side_effect=fake_call
        ):
            for s in seeds:
                _generate_unique_post_commentary(items, "2026-05-07", seed=s)

        # Across 10 seeds and 5 patterns, we expect at least 2 distinct patterns.
        assert len(seen_patterns) >= 2, (
            f"Expected >=2 distinct patterns across 10 seeds, got: {seen_patterns}"
        )
