#!/usr/bin/env python3
"""Pin the argmax selection in the four keyword-scoring detectors.

All four sites used to spell the selection ``max(scores, key=scores.get)``.
``dict.get`` is typed ``(K) -> V | None``, so mypy rejects it as a ``max`` key;
the sites now spell it ``max(scores, key=lambda k: scores[k])``.

The swap is only equivalent because every key handed to ``key`` comes from
iterating ``scores`` itself, so no absent key is ever looked up. These tests
pin BOTH halves of the observable behaviour so the swap cannot have moved it:

  1. the winner on a real table with a clear best score, and
  2. the tie-break — ``max`` returns the FIRST maximal element in iteration
     order, which for a dict is insertion order. ``.get`` and ``[]`` return
     the same value for present keys, so the tie-break is unchanged; a
     regression here would silently repick a different category.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.add_section_banners import detect_banner_type  # noqa: E402
from scripts.fix_code_blocks import detect_language  # noqa: E402
from scripts.generate_aws_diagram import detect_diagram_type  # noqa: E402
from scripts.upgrade_post_images import detect_theme  # noqa: E402

# ---------------------------------------------------------------------------
# add_section_banners.detect_banner_type
# ---------------------------------------------------------------------------


def test_detect_banner_type_picks_highest_scoring_category():
    # NOT "security": that is also the all-zero fallback, so asserting it
    # would pass even if the argmax were inverted to a min.
    assert detect_banner_type("Kubernetes Docker CI/CD 파이프라인") == "devops"
    assert detect_banner_type("AWS Cloud GCP 인프라 비용") == "cloud"
    assert detect_banner_type("LLM GPT Claude 모델 평가") == "ai-ml"


def test_detect_banner_type_tie_keeps_first_inserted(monkeypatch):
    import scripts.add_section_banners as mod

    monkeypatch.setattr(
        mod, "SECTION_KEYWORDS", {"alpha": ["AAA"], "beta": ["BBB"]}, raising=True
    )
    # Both categories score exactly 1 -> the first-inserted key wins.
    assert mod.detect_banner_type("AAA BBB") == "alpha"
    monkeypatch.setattr(
        mod, "SECTION_KEYWORDS", {"beta": ["BBB"], "alpha": ["AAA"]}, raising=True
    )
    assert mod.detect_banner_type("AAA BBB") == "beta"


def test_detect_banner_type_all_zero_falls_back_to_security():
    # Every category scores 0 -> the `scores[best] > 0` guard rejects the
    # argmax and the documented default is returned instead.
    assert detect_banner_type("qqqq wwww zzzz") == "security"


# ---------------------------------------------------------------------------
# upgrade_post_images.detect_theme
# ---------------------------------------------------------------------------


def test_detect_theme_picks_highest_scoring_theme():
    # Two themes score (security=1, finops=4) and the loser is the one that
    # comes FIRST in THEME_RULES, so neither a min nor a tie-break change
    # could produce this answer by accident.
    assert (
        detect_theme(
            tags=["security", "finops", "cost", "billing", "budget"],
            categories=[],
            title="cost optimization",
        )
        == "finops"
    )


def test_detect_theme_tie_keeps_first_rule_order(monkeypatch):
    import scripts.upgrade_post_images as mod

    monkeypatch.setattr(
        mod, "THEME_RULES", [("alpha", ["aaa"]), ("beta", ["bbb"])], raising=True
    )
    assert mod.detect_theme(tags=["aaa", "bbb"], categories=[], title="") == "alpha"
    monkeypatch.setattr(
        mod, "THEME_RULES", [("beta", ["bbb"]), ("alpha", ["aaa"])], raising=True
    )
    assert mod.detect_theme(tags=["aaa", "bbb"], categories=[], title="") == "beta"


def test_detect_theme_no_match_returns_general():
    assert detect_theme(tags=[], categories=[], title="qqqq wwww") == "general"


# ---------------------------------------------------------------------------
# generate_aws_diagram.detect_diagram_type
# ---------------------------------------------------------------------------


def test_detect_diagram_type_picks_highest_scoring_type():
    # NOT "vpc": that is both the all-zero fallback and the first-inserted
    # key, so it is exactly the answer a min or a tie-break bug would give.
    assert (
        detect_diagram_type("WAF Shield IAM 방화벽 Security 인증 VPC", tags=[])
        == "security"
    )


def test_detect_diagram_type_tie_keeps_first_inserted(monkeypatch):
    import scripts.generate_aws_diagram as mod

    monkeypatch.setattr(
        mod, "KEYWORD_TYPE_MAP", {"alpha": ["aaa"], "beta": ["bbb"]}, raising=True
    )
    assert mod.detect_diagram_type("aaa bbb", tags=[]) == "alpha"
    monkeypatch.setattr(
        mod, "KEYWORD_TYPE_MAP", {"beta": ["bbb"], "alpha": ["aaa"]}, raising=True
    )
    assert mod.detect_diagram_type("aaa bbb", tags=[]) == "beta"


def test_detect_diagram_type_no_match_returns_vpc():
    assert detect_diagram_type("qqqq wwww", tags=[]) == "vpc"


# ---------------------------------------------------------------------------
# fix_code_blocks.detect_language
# ---------------------------------------------------------------------------


def test_detect_language_picks_highest_scoring_language():
    # Mixed block: bash scores 3, yaml scores 1. A single-language sample
    # would pass under a min too, so it must be mixed to mean anything.
    mixed = "\n".join(
        [
            "docker run -d nginx",
            "kubectl apply -f pod.yaml",
            "helm upgrade api ./chart",
            "image: nginx:1.25",
        ]
    )
    assert detect_language(mixed) == "bash"


def test_detect_language_tie_keeps_first_inserted(monkeypatch):
    import scripts.fix_code_blocks as mod

    monkeypatch.setattr(
        mod, "LANG_PATTERNS", [(r"aaa", "alpha"), (r"bbb", "beta")], raising=True
    )
    monkeypatch.setattr(mod, "OUTPUT_PATTERNS", [], raising=True)
    assert mod.detect_language("aaa bbb") == "alpha"
    monkeypatch.setattr(
        mod, "LANG_PATTERNS", [(r"bbb", "beta"), (r"aaa", "alpha")], raising=True
    )
    assert mod.detect_language("aaa bbb") == "beta"
