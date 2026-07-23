"""Tests for scripts/regen_quality_baseline.py.

Covers:
  - `--check` exits 0 when the committed baseline has no missing posts.
  - The writer produces deterministic, filename-sorted JSON.
  - Round-trip: scoring a sample post via score_all_posts() matches a direct
    validate_post() call on the same file.

Hermetic: all writes go to tmp_path / a monkeypatched BASELINE_PATH. The real
scripts/tests/fixtures/quality_baseline.json is never overwritten by these
tests.
"""

import json
import shutil
from pathlib import Path

import regen_quality_baseline as rqb
from validate_post_quality import validate_post

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
POSTS_DIR = REPO_ROOT / "_posts"


def test_check_passes_when_baseline_current(capsys):
    """--check is read-only and must exit 0 while no cron-added posts are
    missing from the committed baseline."""
    exit_code = rqb.main(["--check"])
    out = capsys.readouterr().out
    assert exit_code == 0
    assert "up to date" in out


def test_render_baseline_is_deterministic():
    scored = {
        "2026-02-01-Zeta.md": {"total": 42, "scores": {"b": 1, "a": 2}},
        "2026-01-01-Alpha.md": {"total": 99, "scores": {"a": 1}},
    }
    out1 = rqb.render_baseline(scored)
    out2 = rqb.render_baseline(scored)
    assert out1 == out2
    assert out1.endswith("\n")

    parsed = json.loads(out1)
    assert list(parsed.keys()) == ["2026-01-01-Alpha.md", "2026-02-01-Zeta.md"]
    # inner key order is preserved as given (not alphabetically re-sorted)
    assert list(parsed["2026-02-01-Zeta.md"]["scores"].keys()) == ["b", "a"]


def test_score_all_posts_round_trip(tmp_path):
    """Copy a handful of real posts into a tmp dir, score them via
    score_all_posts(), and confirm each entry matches a direct validate_post()
    call on the original file — no divergence introduced by the wrapper."""
    sample_posts = sorted(POSTS_DIR.glob("*.md"))[:3]
    assert sample_posts, "expected at least one real post fixture to sample"

    tmp_posts_dir = tmp_path / "_posts"
    tmp_posts_dir.mkdir()
    for post in sample_posts:
        shutil.copy(post, tmp_posts_dir / post.name)

    scored = rqb.score_all_posts(tmp_posts_dir)

    assert set(scored) == {p.name for p in sample_posts}
    for post in sample_posts:
        expected = validate_post(post)
        actual = scored[post.name]
        assert actual["total"] == expected["total"]
        assert actual["scores"] == expected["scores"]


def test_main_write_mode_is_hermetic(tmp_path, monkeypatch):
    """Default (write) mode must only touch the monkeypatched BASELINE_PATH
    and read from the monkeypatched POSTS_DIR — never the real fixture or
    the real _posts/ corpus."""
    real_fixture = rqb.BASELINE_PATH
    real_fixture_bytes_before = real_fixture.read_bytes()

    sample_posts = sorted(POSTS_DIR.glob("*.md"))[:2]
    tmp_posts_dir = tmp_path / "_posts"
    tmp_posts_dir.mkdir()
    for post in sample_posts:
        shutil.copy(post, tmp_posts_dir / post.name)

    tmp_baseline = tmp_path / "quality_baseline.json"
    monkeypatch.setattr(rqb, "POSTS_DIR", tmp_posts_dir)
    monkeypatch.setattr(rqb, "BASELINE_PATH", tmp_baseline)

    exit_code = rqb.main([])

    assert exit_code == 0
    assert tmp_baseline.exists()
    written = json.loads(tmp_baseline.read_text(encoding="utf-8"))
    assert set(written) == {p.name for p in sample_posts}

    # the real committed fixture must be untouched
    assert real_fixture.read_bytes() == real_fixture_bytes_before
