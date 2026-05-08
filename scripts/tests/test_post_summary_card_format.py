"""Regression guard: every _posts/ file with an ai-summary-card include must
use the bare include form and carry a `summary_card:` block in frontmatter
(Option A, post-2026-05-08).

Prevents reintroducing the legacy include-with-attributes form (which split
between two render branches in _includes/ai-summary-card.html and forced the
migration cleanup).
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

POSTS_DIR = Path(__file__).resolve().parent.parent.parent / "_posts"

# Match any include reference, capturing the body between the include name and %}.
_INCLUDE_BLOCK_RE = re.compile(
    r"\{%-?\s*include\s+ai-summary-card\.html(?P<body>.*?)-?%\}",
    re.DOTALL,
)
_FRONTMATTER_RE = re.compile(r"^---\n(?P<fm>.*?\n)---\n", re.DOTALL)


def _all_posts() -> list[Path]:
    return sorted(POSTS_DIR.glob("*.md"))


def _parse_frontmatter(text: str) -> dict:
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}
    parsed = yaml.safe_load(m.group("fm"))
    return parsed if isinstance(parsed, dict) else {}


def test_all_summary_card_includes_use_bare_form():
    """Bodies must contain only `{% include ai-summary-card.html %}` (no attrs)."""
    violations: list[str] = []
    for path in _all_posts():
        text = path.read_text(encoding="utf-8")
        for m in _INCLUDE_BLOCK_RE.finditer(text):
            body = m.group("body").strip()
            if body:
                violations.append(f"{path.name}: include attrs leaked: {body[:80]!r}")
    assert not violations, "Legacy include attrs detected:\n" + "\n".join(violations)


def test_every_post_with_card_include_has_summary_card_frontmatter():
    """If a post uses the include, it must have summary_card: in frontmatter."""
    violations: list[str] = []
    for path in _all_posts():
        text = path.read_text(encoding="utf-8")
        if not _INCLUDE_BLOCK_RE.search(text):
            continue
        front = _parse_frontmatter(text)
        if "summary_card" not in front:
            violations.append(f"{path.name}: include present but no summary_card in FM")
    assert not violations, "Missing summary_card frontmatter:\n" + "\n".join(violations)


def test_summary_card_blocks_have_required_keys():
    """summary_card block must have title and either categories or tags or highlights."""
    violations: list[str] = []
    for path in _all_posts():
        text = path.read_text(encoding="utf-8")
        front = _parse_frontmatter(text)
        sc = front.get("summary_card")
        if not isinstance(sc, dict):
            continue
        if not sc.get("title"):
            violations.append(f"{path.name}: summary_card.title is empty")
        if not any(sc.get(k) for k in ("categories", "tags", "highlights")):
            violations.append(
                f"{path.name}: summary_card has neither categories/tags/highlights"
            )
    assert not violations, "summary_card schema violations:\n" + "\n".join(violations)


def test_post_count_invariant_at_least_one_card_post():
    """Sanity check: the corpus has many posts using the card."""
    counted = sum(
        1 for p in _all_posts()
        if _INCLUDE_BLOCK_RE.search(p.read_text(encoding="utf-8"))
    )
    assert counted > 100, f"Expected >100 posts with summary card, got {counted}"
