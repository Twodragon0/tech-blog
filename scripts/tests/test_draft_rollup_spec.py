#!/usr/bin/env python3
"""Tests for scripts/draft_rollup_spec.py (piece A: rollup draft tool).

Per the plan (.omc/plans/rollup-autogen-and-grounding.md §A): "draft should
~reproduce the hand specs". We assert the deterministic, machine-extractable
parts of the draft match the hand-authored weekly spec — days[] dates + count,
daily_count, 3 top_highlights, every top_highlight's source matching a daily's
highlight source — while ALLOWING editorial differences (label left blank,
headline/detail phrasing).

Tested against the real existing weekly posts that own the hand specs:
  _data/rollup_covers/2026-04-05.yml, .../2026-04-12.yml, .../2026-04-19.yml

API disabling and sys.path setup are handled by conftest.py; we also insert
the repo root so ``scripts.draft_rollup_spec`` imports cleanly when run alone.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts.draft_rollup_spec import (  # noqa: E402
    _to_ascii,
    build_spec,
    daily_urls_from_redirects,
    lead_entity,
    parse_frontmatter,
    rank_top_highlights,
    render_yaml,
    resolve_owning_post,
)

POSTS_DIR = REPO / "_posts"
ROLLUP_DIR = REPO / "_data" / "rollup_covers"

# (date, owning post filename) for the three weekly rollups with hand specs.
WEEKLY_CASES = [
    ("2026-04-05", "2026-04-05-Week1_April_2026_Security_Digest.md"),
    ("2026-04-12", "2026-04-12-Week2_April_2026_Security_Digest.md"),
    ("2026-04-19", "2026-04-19-Week3_April_2026_Security_Digest.md"),
]


def _load_hand_spec(date: str) -> dict:
    return yaml.safe_load((ROLLUP_DIR / f"{date}.yml").read_text(encoding="utf-8"))


def _is_ascii(text: str) -> bool:
    return all(ord(ch) < 128 for ch in text)


# ---------------------------------------------------------------------------
# Unit tests: pure helpers (deterministic, no fixtures)
# ---------------------------------------------------------------------------


def test_to_ascii_strips_korean_and_leading_punctuation():
    assert _to_ascii(", CVE-2025-55182 점검") == "CVE-2025-55182"
    assert _to_ascii("Axios npm 해킹") == "Axios npm"
    assert _to_ascii("순수한글") == ""


def test_lead_entity_prefers_proper_noun_over_cve():
    # CVE present but a proper noun leads -> proper noun is the headline.
    assert lead_entity("TrueConf CVE-2026-3502 zero-day") == "TrueConf"
    # All-Korean title yields no ASCII entity.
    assert lead_entity("순수 한글 제목") == ""


def test_lead_entity_inherits_cover_grade_honesty_filtering():
    """Intentional decision: rollup day-cell tags share the L20 cover headline
    quality guards (generic-word reject, severity-join reject) via the shared
    ``build_lead_headline`` helper — no weak "Show Option"/"Critical High" tags
    leak onto rollup covers."""
    # A generic platform lead falls through to the real following entity.
    assert lead_entity("Linux Defender 우회") == "Defender"
    # An all-severity-word join is rejected -> empty tag (omit, don't fabricate).
    assert lead_entity("Critical High 경보") == ""
    # Both tokens generic filler ("Show Option") -> empty tag.
    assert lead_entity("Show Option 기능") == ""
    # Positive control: a real vendor+product bigram is preserved.
    assert lead_entity("Ivanti EPMM 취약점") == "Ivanti EPMM"


def test_daily_urls_from_redirects_picks_only_daily_paths():
    redirects = [
        "/posts/2026/04/01/Tech_Security_Weekly_Digest_Zero-Day/",
        "/posts/2026/04/Week1_April_2026_Security_Digest/",  # self-canonical, no day
        "/posts/2026-04-05-Week1_April_2026_Security_Digest/",  # self-canonical
    ]
    dailies = daily_urls_from_redirects(redirects)
    assert dailies == [("2026", "04", "01", "Tech_Security_Weekly_Digest_Zero-Day")]


def test_rank_top_highlights_orders_by_severity_then_recency():
    records = [
        {"headline": "A", "severity": "MEDIUM", "recency": 0, "detail": "", "source": ""},
        {"headline": "B", "severity": "HIGH", "recency": 1, "detail": "", "source": ""},
        {"headline": "C", "severity": "HIGH", "recency": 3, "detail": "", "source": ""},
        {"headline": "B", "severity": "LOW", "recency": 4, "detail": "", "source": ""},  # dup
    ]
    top = rank_top_highlights(records, limit=3)
    assert [r["headline"] for r in top] == ["C", "B", "A"]  # HIGH(recent), HIGH, MEDIUM
    assert len(top) == 3


def test_parse_frontmatter_returns_dict_and_body():
    fm, body = parse_frontmatter("---\nfoo: bar\n---\nhello body\n")
    assert fm == {"foo": "bar"}
    assert "hello body" in body


# ---------------------------------------------------------------------------
# Integration: draft ~reproduces each hand-authored weekly spec
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("date,post_name", WEEKLY_CASES)
def test_draft_reproduces_hand_spec_structure(date, post_name):
    post = POSTS_DIR / post_name
    if not post.exists():
        pytest.skip(f"owning post missing: {post_name}")
    hand = _load_hand_spec(date)

    spec = build_spec(post)

    # date + slug match the owning post / hand spec exactly.
    assert spec["date"] == hand["date"] == date
    assert spec["slug"] == hand["slug"]

    # days[] dates + count match the hand spec (deterministic from redirect_from).
    draft_dates = [d["date"] for d in spec["days"]]
    hand_dates = [d["date"] for d in hand["days"]]
    assert draft_dates == hand_dates

    # daily_count matches the hand spec and the days[] length.
    assert spec["daily_count"] == hand["daily_count"]
    assert len(spec["days"]) == spec["daily_count"]

    # footer mirrors the existing spec shape.
    assert spec["footer"]["daily_digests"] == spec["daily_count"]
    assert spec["footer"]["categories"]  # non-empty list

    # Exactly 3 top_highlights with the required keys; label left blank (editorial).
    assert len(spec["top_highlights"]) == 3
    for h in spec["top_highlights"]:
        assert set(h) == {"severity", "label", "headline", "detail", "source"}
        assert h["label"] == ""  # editorial — human fills it
        assert h["severity"] in {"HIGH", "MEDIUM", "LOW"}
        assert h["headline"]  # non-empty entity phrase


@pytest.mark.parametrize("date,post_name", WEEKLY_CASES)
def test_draft_top_highlight_sources_are_daily_derived(date, post_name):
    """Every drafted top_highlight source must come from a daily's highlights."""
    post = POSTS_DIR / post_name
    if not post.exists():
        pytest.skip(f"owning post missing: {post_name}")
    fm, _ = parse_frontmatter(post.read_text(encoding="utf-8"))
    daily_sources: set = set()
    for (_y, _m, _d, slug) in daily_urls_from_redirects(fm.get("redirect_from")):
        # find the daily file by date+slug
        for cand in POSTS_DIR.glob("*.md"):
            if cand.name.endswith(f"{slug}.md"):
                dfm, _ = parse_frontmatter(cand.read_text(encoding="utf-8"))
                for h in (dfm.get("summary_card") or {}).get("highlights") or []:
                    if isinstance(h, dict):
                        daily_sources.add(_to_ascii(str(h.get("source", ""))))

    spec = build_spec(post)
    for h in spec["top_highlights"]:
        assert h["source"] in daily_sources


@pytest.mark.parametrize("date,post_name", WEEKLY_CASES)
def test_draft_severity_matches_enum(date, post_name):
    post = POSTS_DIR / post_name
    if not post.exists():
        pytest.skip(f"owning post missing: {post_name}")
    spec = build_spec(post)
    for d in spec["days"]:
        assert d["severity"] in {"HIGH", "MEDIUM", "LOW"}


@pytest.mark.parametrize("date,post_name", WEEKLY_CASES)
def test_rendered_draft_is_ascii_only_and_valid_yaml(date, post_name):
    post = POSTS_DIR / post_name
    if not post.exists():
        pytest.skip(f"owning post missing: {post_name}")
    spec = build_spec(post)
    text = render_yaml(spec)

    # ASCII-only across the entire rendered draft (covers require ASCII <text>).
    assert _is_ascii(text), "rendered draft contains non-ASCII characters"

    # Header marks it as an auto-generated DRAFT for review.
    assert "AUTO-GENERATED DRAFT" in text
    assert "label" in text  # editor guidance present

    # The YAML body round-trips and preserves the structural fields.
    loaded = yaml.safe_load(text)
    assert loaded["daily_count"] == spec["daily_count"]
    assert len(loaded["top_highlights"]) == 3
    assert len(loaded["days"]) == spec["daily_count"]


def test_resolve_owning_post_by_date_prefers_rollup_over_daily():
    """A date shared by a daily + a weekly rollup resolves to the rollup post."""
    week2 = POSTS_DIR / "2026-04-12-Week2_April_2026_Security_Digest.md"
    if not week2.exists():
        pytest.skip("Week2 rollup post missing")
    resolved = resolve_owning_post("2026-04-12")
    # The rollup (with daily redirect_from URLs) wins over the same-date daily.
    assert resolved.name.startswith("2026-04-12-Week")
