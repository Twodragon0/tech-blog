"""Tests for genre-aware scoring of monthly-index pages in validate_post_quality.

Covers:
  - Index genre detection (is_index_post / index_signal_drift).
  - The dedicated index rubric (_score_index / validate_post dispatch).
  - A non-index golden-baseline regression that locks isolation: every
    non-index post's score must stay byte-identical to the pre-change HEAD
    snapshot committed at scripts/tests/fixtures/quality_baseline.json.
"""

import json
from pathlib import Path

import pytest
from validate_post_quality import (
    index_signal_drift,
    is_index_post,
    validate_index_coverage,
    validate_post,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POSTS_DIR = REPO_ROOT / "_posts"
BASELINE_PATH = Path(__file__).resolve().parent / "fixtures" / "quality_baseline.json"

INDEX_FILES = [
    "2026-01-31-January_2026_Security_Digest_Monthly_Index.md",
    "2026-02-28-February_2026_Security_Digest_Monthly_Index.md",
    "2026-03-30-March_2026_Security_Digest_Monthly_Index.md",
]


def _read(name: str) -> str:
    return (POSTS_DIR / name).read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# 5.1 Index detection
# --------------------------------------------------------------------------- #
class TestIndexDetection:
    @pytest.mark.parametrize("name", INDEX_FILES)
    def test_real_index_pages_are_index(self, name):
        assert is_index_post(_read(name), name) is True

    def test_digest_post_is_not_index(self):
        # A real weekly digest — has no monthly-index tag.
        digest = next(POSTS_DIR.glob("*Weekly_Digest*.md"))
        assert is_index_post(digest.read_text(encoding="utf-8"), digest.name) is False

    def test_guide_post_is_not_index(self):
        name = "2026-02-28-AI_Agent_Security_Architecture_Design_Guide.md"
        assert is_index_post(_read(name), name) is False

    def test_body_only_mention_is_not_index(self):
        # "monthly-index" appears only in the body, never in the tags: line.
        content = (
            "---\n"
            'title: "Regular post"\n'
            "tags: [security, devsecops]\n"
            "---\n\n"
            "This post discusses the monthly-index concept in prose only.\n"
        )
        assert is_index_post(content, "2026-01-01-Regular.md") is False

    def test_inline_tags_line_is_index(self):
        content = (
            "---\n"
            'title: "Index"\n'
            "tags: [monthly-index, security-news, 2026]\n"
            "---\n\n"
            "body\n"
        )
        assert is_index_post(content, "2026-01-31-Foo_Monthly_Index.md") is True

    def test_drift_tag_present_filename_missing(self):
        content = "---\ntags: [monthly-index]\n---\n"
        assert index_signal_drift(content, "2026-01-31-Not_An_Index.md") != ""

    def test_drift_filename_present_tag_missing(self):
        content = "---\ntags: [security]\n---\n"
        assert index_signal_drift(content, "2026-01-31-Foo_Monthly_Index.md") != ""

    @pytest.mark.parametrize("name", INDEX_FILES)
    def test_no_drift_for_real_index_pages(self, name):
        assert index_signal_drift(_read(name), name) == ""

    def test_filename_drift_cross_check_all_corpus(self):
        # Tag and filename must agree across the whole corpus (no silent drift).
        for post in sorted(POSTS_DIR.glob("*.md")):
            content = post.read_text(encoding="utf-8")
            assert index_signal_drift(content, post.name) == "", (
                f"drift on {post.name}"
            )


# --------------------------------------------------------------------------- #
# 5.2 Index rubric
# --------------------------------------------------------------------------- #
class TestIndexRubric:
    def test_january_scores_at_least_80(self):
        r = validate_post(POSTS_DIR / INDEX_FILES[0])
        assert r["total"] == 87
        assert r["total"] >= 80

    @pytest.mark.parametrize("name", INDEX_FILES[1:])
    def test_feb_mar_score_100(self, name):
        r = validate_post(POSTS_DIR / name)
        assert r["total"] == 100

    @pytest.mark.parametrize("name", INDEX_FILES)
    def test_per_dimension_shared(self, name):
        r = validate_post(POSTS_DIR / name)
        s = r["scores"]
        assert s["front_matter"] == 15
        assert s["ai_summary"] == 10
        assert s["digest_link_coverage"] == 35
        assert s["editorial_sections"] == 10
        assert s["excerpt_quality"] == 10

    def test_weekly_structure_values(self):
        jan = validate_post(POSTS_DIR / INDEX_FILES[0])
        assert jan["scores"]["weekly_structure"] == 7  # single month-end bucket
        for name in INDEX_FILES[1:]:
            r = validate_post(POSTS_DIR / name)
            assert r["scores"]["weekly_structure"] == 20

    def test_malformed_index_below_80(self):
        content = (
            "---\n"
            'title: "Stub index"\n'
            "tags: [monthly-index, 2026]\n"
            'excerpt: "short"\n'
            "---\n\n"
            "{% include ai-summary-card.html %}\n\n"
            "No links, no weekly sections, no editorial framing.\n"
        )
        tmp = POSTS_DIR / "___tmp_malformed_index_test.md"
        try:
            tmp.write_text(content, encoding="utf-8")
            r = validate_post(tmp)
            assert r["total"] < 80
        finally:
            tmp.unlink(missing_ok=True)

    def test_coverage_counts_both_link_styles(self):
        raw = "".join(
            f"| 1월 {d}일 | 주제 | [바로가기](/posts/2026/01/{d:02d}/Foo/) |\n"
            for d in range(1, 6)
        )
        raw_table = "| 날짜 | 주제 | 링크 |\n|---|---|---|\n" + raw
        assert validate_index_coverage(raw_table) == 35

        liquid = "\n".join(f"{{% post_url 2026-01-{d:02d}-Foo %}}" for d in range(1, 6))
        liquid_table = "| 날짜 | 주제 | 링크 |\n|---|---|---|\n" + liquid + "\n"
        assert validate_index_coverage(liquid_table) == 35

        # A single link (partial) plus a table.
        one = "| 날짜 | 주제 | 링크 |\n[x](/posts/2026/01/23/Foo/)\n"
        assert validate_index_coverage(one) == 15  # 1*5 + 10 table


# --------------------------------------------------------------------------- #
# 5.3 Non-index regression (isolation guarantee)
# --------------------------------------------------------------------------- #
def _load_baseline() -> dict:
    return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))


def _non_index_posts() -> list[Path]:
    out = []
    for post in sorted(POSTS_DIR.glob("*.md")):
        if not is_index_post(post.read_text(encoding="utf-8"), post.name):
            out.append(post)
    return out


def test_index_detection_stable():
    """Detection must (a) find all known index files and (b) never fire on a
    post whose filename lacks 'Monthly_Index'. Written to tolerate a future
    monthly-index publication while still catching over-matching regressions.
    """
    idx = [
        p.name
        for p in sorted(POSTS_DIR.glob("*.md"))
        if is_index_post(p.read_text(encoding="utf-8"), p.name)
    ]
    # (a) every known index is detected (subset — future indexes allowed)
    for known in INDEX_FILES:
        assert known in idx, f"{known} no longer detected as index"
    # (b) no false positive: every detected index is a *Monthly_Index* file
    for name in idx:
        assert "Monthly_Index" in name, f"unexpected index detection: {name}"


@pytest.mark.parametrize(
    "post", _non_index_posts(), ids=lambda p: p.name
)
def test_non_index_scores_byte_identical(post):
    baseline = _load_baseline()
    if post.name not in baseline:
        # A post published after the golden snapshot (e.g. by the daily
        # blogwatcher cron) is not part of the frozen isolation corpus.
        pytest.skip(f"{post.name} not in golden baseline (added after snapshot)")
    r = validate_post(post)
    expected = baseline[post.name]
    assert r["total"] == expected["total"]
    assert r["scores"] == expected["scores"]
