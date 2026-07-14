"""Tests for news content-generation action-point diversity and the removal of
'실무 포인트' / '실무 적용 포인트' filler blocks.

`_pick_variant` selects deterministically from a list of phrasings keyed on the
article identity, so different articles in the same keyword branch yield
different tips — but the same article always yields the same tip across
regenerations. `_generate_contextual_action_point` (used for the weekly
briefing and Korean-summary text) exercises that rotation.

Editorial decision 2026-07-14: the standalone practical-point filler blocks
('**실무 포인트**:' inline line and '#### 실무 적용 포인트' heading sections)
are no longer emitted by `generate_news_section`. ``TestNoPracticalPointEmission``
guards against regression (re-emission).
"""

from typing import Dict, List

import pytest
from news.content_generator import (
    _generate_contextual_action_point,
    _pick_variant,
    _reset_variant_dedup,
    generate_news_section,
)


@pytest.fixture(autouse=True)
def _reset_variant_state():
    """The per-post variant-dedup registry is module-global; reset before each
    test so accumulated state never leaks across tests."""
    _reset_variant_dedup()
    yield
    _reset_variant_dedup()


def _item(title: str, category: str = "security", url: str = "") -> Dict:
    return {
        "title": title,
        "summary": title,
        "content": "",
        "category": category,
        "url": url or f"https://example.test/{title.replace(' ', '-')}",
    }


class TestPickVariantDeterminism:
    def test_same_item_yields_same_variant(self):
        variants = ["A", "B", "C", "D", "E"]
        item = _item("stable article")
        first = _pick_variant(item, variants)
        for _ in range(10):
            assert _pick_variant(item, variants) == first


class TestPickVariantDedup:
    """Regression: two DIFFERENT articles hitting the same branch must not
    render the IDENTICAL variant block within one post (the '실무 포인트
    블록 중복' warning from check_posts.py)."""

    def test_distinct_items_avoid_same_variant(self):
        variants = ["A", "B", "C"]
        # Build enough distinct items to fill all variants; none should repeat
        # until the pool is exhausted.
        chosen = [_pick_variant(_item(f"article {i}"), variants) for i in range(3)]
        assert sorted(chosen) == ["A", "B", "C"], f"expected all 3 variants, got {chosen}"

    def test_overflow_falls_back_without_crash(self):
        variants = ["A", "B"]
        # More colliding items than variants: first 2 distinct, rest reuse.
        chosen = [_pick_variant(_item(f"article {i}"), variants) for i in range(4)]
        assert set(chosen[:2]) == {"A", "B"}
        assert all(c in {"A", "B"} for c in chosen)

    def test_reset_clears_dedup_state(self):
        variants = ["A", "B", "C"]
        first_post = [_pick_variant(_item(f"a{i}"), variants) for i in range(3)]
        _reset_variant_dedup()
        second_post = [_pick_variant(_item(f"a{i}"), variants) for i in range(3)]
        # After reset, the same items reproduce the same assignment.
        assert first_post == second_post

    def test_same_item_idempotent_across_calls_within_post(self):
        variants = ["A", "B", "C"]
        item = _item("repeat me")
        first = _pick_variant(item, variants)
        # Re-asking the same item+branch returns the cached choice, even after
        # other items have consumed variants.
        _pick_variant(_item("other"), variants)
        assert _pick_variant(item, variants) == first

    def test_empty_variants_returns_empty_string(self):
        assert _pick_variant(_item("x"), []) == ""

    def test_single_variant_always_returned(self):
        assert _pick_variant(_item("x"), ["only"]) == "only"


class TestContextualActionDiversity:
    """Different articles in the same keyword branch should not all share one tip."""

    @staticmethod
    def _collect_variants(items: List[Dict]) -> set:
        return {_generate_contextual_action_point(it) for it in items}

    def test_bitcoin_branch_diversifies(self):
        items = [
            _item("Bitcoin surges past 80k mark", category="blockchain"),
            _item("Bitcoin Magazine keynote recap", category="blockchain"),
            _item("비트코인 시세 업데이트 요약", category="blockchain"),
            _item("BTC on-chain analytics roundup", category="blockchain"),
            _item("Bitcoin ETF inflow trend", category="blockchain"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2, (
            f"Bitcoin branch collapsed to single variant across 5 articles: {variants}"
        )

    def test_ransomware_branch_diversifies(self):
        items = [
            _item("Ransomware attack on hospital"),
            _item("LockBit ransomware resurgence in 2026"),
            _item("랜섬웨어 방어 모범 사례"),
            _item("New ransomware variant observed"),
            _item("Ransomware-as-a-Service operator profile"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2, (
            f"Ransomware branch collapsed to one variant: {variants}"
        )

    def test_phishing_branch_diversifies(self):
        items = [
            _item("Phishing campaign targets SaaS users"),
            _item("피싱 공격 탐지 기법"),
            _item("Credential phishing via cloned portals"),
            _item("자격증명 탈취 피싱 증가"),
            _item("Spear phishing against finance teams"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2

    def test_llm_branch_diversifies(self):
        items = [
            _item("GPT-5 architecture preview", category="ai"),
            _item("Claude Haiku 4.5 released", category="ai"),
            _item("Gemini 3 multimodal benchmarks", category="ai"),
            _item("LLM prompt injection survey", category="ai"),
            _item("GPT-4o performance update", category="ai"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2

    def test_supply_chain_branch_diversifies(self):
        items = [
            _item("Supply chain attack via npm package"),
            _item("공급망 공격 SBOM 대응"),
            _item("Dependency confusion campaign"),
            _item("Trivy supply chain breach response"),
            _item("Sonatype supply chain malware report"),
        ]
        variants = self._collect_variants(items)
        assert len(variants) >= 2

    @pytest.mark.parametrize(
        "title,category,required_substrings",
        [
            ("Bitcoin keynote", "blockchain", ["피싱", "지갑", "화이트리스트"]),
            ("Ransomware on MSP", "security", ["백업", "복구", "SMB"]),
            ("Phishing surge report", "security", ["MFA", "FIDO2", "조건부"]),
            ("LLM update from vendor", "ai", ["LLM", "모델", "프롬프트", "리덕션"]),
        ],
    )
    def test_branch_variants_contain_relevant_terminology(
        self, title, category, required_substrings
    ):
        """Every variant in a branch must include at least one expected keyword."""
        # Generate tips for 10 slightly different titles — must cover >=2 unique variants
        items = [_item(f"{title} {i}", category=category) for i in range(10)]
        unique = {_generate_contextual_action_point(it) for it in items}
        assert len(unique) >= 2, f"Branch produced single variant for {title}"
        for tip in unique:
            assert any(
                sub in tip for sub in required_substrings
            ), f"Variant missing expected terminology ({required_substrings}): {tip}"

class TestContextualActionFallbackDiversity:
    """The bare category-fallback returns (no keyword branch matched) must
    rotate via `_pick_variant` instead of returning one hardcoded string —
    regression for the '실무 포인트' repeating ~323x across digests."""

    @staticmethod
    def _collect_variants(items: List[Dict]) -> set:
        return {_generate_contextual_action_point(it) for it in items}

    @staticmethod
    def _fallback_items(category: str) -> List[Dict]:
        # Titles deliberately avoid every keyword checked by all branches
        # (including substring matches like "act", "sec", "eth") so each
        # branch's final bare-return fallback fires.
        suffixes = ["alpha", "beta", "gamma", "delta", "epsilon"]
        return [
            _item(f"Quarterly research roundup {s}", category=category)
            for s in suffixes
        ]

    def test_security_fallback_diversifies(self):
        variants = self._collect_variants(self._fallback_items("security"))
        assert len(variants) >= 2, (
            f"security fallback collapsed to single variant: {variants}"
        )

    def test_ai_fallback_diversifies(self):
        variants = self._collect_variants(self._fallback_items("ai"))
        assert len(variants) >= 2, (
            f"ai fallback collapsed to single variant: {variants}"
        )

    def test_cloud_fallback_diversifies(self):
        variants = self._collect_variants(self._fallback_items("cloud"))
        assert len(variants) >= 2, (
            f"cloud fallback collapsed to single variant: {variants}"
        )

    def test_blockchain_fallback_diversifies(self):
        variants = self._collect_variants(self._fallback_items("blockchain"))
        assert len(variants) >= 2, (
            f"blockchain fallback collapsed to single variant: {variants}"
        )

    def test_default_fallback_diversifies(self):
        variants = self._collect_variants(self._fallback_items("tech"))
        assert len(variants) >= 2, (
            f"default fallback collapsed to single variant: {variants}"
        )

    def test_fallback_same_item_is_deterministic(self):
        """The same article re-asking the same fallback branch must always
        return the same tip (idempotent across regenerations)."""
        item = _item("Quarterly research roundup alpha", category="cloud")
        first = _generate_contextual_action_point(item)
        for _ in range(10):
            assert _generate_contextual_action_point(item) == first

    def test_blockchain_fallback_variants_preserve_required_substring(self):
        """Every blockchain fallback variant must retain '프로토콜' or
        '스마트 컨트랙트' (asserted separately by
        test_news_templates.py::test_blockchain_fallback)."""
        variants = self._collect_variants(self._fallback_items("blockchain"))
        assert len(variants) >= 2
        for tip in variants:
            assert "프로토콜" in tip or "스마트 컨트랙트" in tip, (
                f"blockchain fallback variant missing required substring: {tip}"
            )


class TestNoPracticalPointEmission:
    """Regression: generate_news_section must NOT emit practical-point filler
    blocks for any category (editorial decision 2026-07-14).

    Both the inline '**실무 포인트**:' line and the '#### 실무 적용 포인트'
    heading sections were removed. Security-category templates (권장 조치 etc.)
    are unaffected and do not use these markers.
    """

    @staticmethod
    def _item(title: str, category: str) -> Dict:
        return {
            "title": title,
            "summary": f"{title} 관련 상세 요약 문장입니다.",
            "content": "",
            "category": category,
            "url": f"https://example.test/{title.replace(' ', '-')}",
        }

    @pytest.mark.parametrize(
        "category,title",
        [
            ("ai", "New AI agent framework release"),
            ("cloud", "Kubernetes RBAC hardening guide"),
            ("devops", "Docker image scanning automation"),
            ("kubernetes", "k8s cluster security audit"),
            ("blockchain", "Ethereum DeFi smart contract audit"),
            ("security", "Phishing campaign targets SaaS users"),
            ("devsecops", "Supply chain attack via npm package"),
            ("tech", "Quarterly research roundup"),
        ],
    )
    def test_no_practical_point_markers(self, category, title):
        section = generate_news_section(self._item(title, category), "1")
        assert "#### 실무 적용 포인트" not in section, (
            f"'#### 실무 적용 포인트' re-emitted for category={category}"
        )
        assert "**실무 포인트**" not in section, (
            f"'**실무 포인트**:' re-emitted for category={category}"
        )

    def test_no_markers_for_critical_security(self):
        # Critical security items take the enhanced-content branch; verify the
        # markers are absent there too.
        item = self._item("Critical RCE in widely-used library", "security")
        section = generate_news_section(item, "1", is_critical=True)
        assert "#### 실무 적용 포인트" not in section
        assert "**실무 포인트**" not in section
