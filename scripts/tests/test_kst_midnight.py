#!/usr/bin/env python3
"""Tests for scripts/check_kst_midnight.py.

Covers:
- Post with date HH=09:00 +0900 → safe (URL day matches filename day)
- Post with date HH=00:30 +0900 without redirect_from → violation
- Post with date HH=00:30 +0900 WITH correct redirect_from → clean
- Post with date HH=00:30 +0000 (UTC directly) → safe (no KST shift)
- Post with date HH=15:00 +0900 (KST afternoon) → safe
- Edge case: HH=08:59:59 +0900 → at risk (UTC = 23:59 prev day)
- Non-dated filename → skipped
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure scripts/ is importable.
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.check_kst_midnight import check_file, _expected_redirect


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_post(
    tmp_path: Path,
    filename: str,
    date_line: str,
    redirect_from: list[str] | None = None,
) -> Path:
    """Write a minimal Jekyll post to *tmp_path/_posts/<filename>*.

    ``date_line`` is the raw ``date:`` value string (without the key prefix),
    e.g. ``"2025-05-30 00:30:00 +0900"``.

    ``redirect_from`` is a list of strings that will be rendered as a YAML
    list under the ``redirect_from:`` key.
    """
    posts_dir = tmp_path / "_posts"
    posts_dir.mkdir(parents=True, exist_ok=True)

    redirect_block = ""
    if redirect_from is not None:
        entries = "\n".join(f"  - {url}" for url in redirect_from)
        redirect_block = f"redirect_from:\n{entries}\n"

    content = (
        "---\n"
        "layout: post\n"
        f'title: "Test Post"\n'
        f"date: {date_line}\n"
        f"{redirect_block}"
        "---\n"
        "Body text.\n"
    )

    post_path = posts_dir / filename
    post_path.write_text(content, encoding="utf-8")
    return post_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestKstMidnightGate:
    def test_safe_kst_09h_no_redirect_needed(self, tmp_path: Path):
        """HH=09:00 +0900 → UTC same day; no redirect required."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 09:00:00 +0900",
        )
        assert check_file(path) == []

    def test_violation_kst_midnight_no_redirect(self, tmp_path: Path):
        """HH=00:30 +0900 without redirect_from → violation reported."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 00:30:00 +0900",
        )
        violations = check_file(path)
        assert len(violations) == 1
        line_no, msg = violations[0]
        assert "/posts/2025/05/30/My_Post/" in msg
        assert "missing redirect_from" in msg

    def test_clean_kst_midnight_with_correct_redirect(self, tmp_path: Path):
        """HH=00:30 +0900 WITH the filename-date redirect_from → no violation."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 00:30:00 +0900",
            redirect_from=["/posts/2025/05/30/My_Post/"],
        )
        assert check_file(path) == []

    def test_safe_utc_direct(self, tmp_path: Path):
        """HH=00:30 +0000 (UTC offset directly) → no KST shift; safe."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 00:30:00 +0000",
        )
        assert check_file(path) == []

    def test_safe_kst_afternoon(self, tmp_path: Path):
        """HH=15:00 +0900 → UTC same day; no redirect required."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 15:00:00 +0900",
        )
        assert check_file(path) == []

    def test_violation_edge_08_59_59(self, tmp_path: Path):
        """HH=08:59:59 +0900 → UTC = 23:59 previous day; at risk → violation."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 08:59:59 +0900",
        )
        violations = check_file(path)
        assert len(violations) == 1
        _, msg = violations[0]
        assert "/posts/2025/05/30/My_Post/" in msg

    def test_edge_08_59_59_with_redirect_clean(self, tmp_path: Path):
        """HH=08:59:59 +0900 WITH correct redirect → clean."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 08:59:59 +0900",
            redirect_from=["/posts/2025/05/30/My_Post/"],
        )
        assert check_file(path) == []

    def test_non_dated_filename_skipped(self, tmp_path: Path):
        """File without YYYY-MM-DD prefix is silently skipped."""
        posts_dir = tmp_path / "_posts"
        posts_dir.mkdir(parents=True, exist_ok=True)
        path = posts_dir / "about.md"
        path.write_text(
            "---\nlayout: page\ntitle: About\n---\nContent.\n",
            encoding="utf-8",
        )
        assert check_file(path) == []

    def test_redirect_wrong_url_still_violation(self, tmp_path: Path):
        """Having a redirect_from entry but not the filename-date one → still violation."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 01:00:00 +0900",
            redirect_from=["/posts/2025/05/29/My_Post/"],  # UTC day, not filename day
        )
        violations = check_file(path)
        assert len(violations) == 1
        _, msg = violations[0]
        assert "/posts/2025/05/30/My_Post/" in msg

    def test_line_number_reported(self, tmp_path: Path):
        """Violation includes a sensible (non-zero) line number."""
        path = _make_post(
            tmp_path,
            "2026-01-01-New_Year.md",
            "2026-01-01 03:00:00 +0900",
        )
        violations = check_file(path)
        assert violations
        line_no, _ = violations[0]
        assert line_no > 0

    def test_kst_plus_0900_colon_variant(self, tmp_path: Path):
        """Offset written as +09:00 (with colon) is also detected."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 05:00:00 +09:00",
        )
        violations = check_file(path)
        assert len(violations) == 1

    def test_multiple_redirects_one_correct(self, tmp_path: Path):
        """Multiple redirect_from entries — correct one present → clean."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 00:30:00 +0900",
            redirect_from=[
                "/posts/2025/05/My_Post/",
                "/posts/2025-05-30-My_Post/",
                "/posts/2025/05/30/My_Post/",   # the required one
            ],
        )
        assert check_file(path) == []

    def test_safe_kst_09_00_01(self, tmp_path: Path):
        """One second past the risk window — safe (HH=09, minute > 0 is still ok)."""
        path = _make_post(
            tmp_path,
            "2025-05-30-My_Post.md",
            "2025-05-30 09:00:01 +0900",
        )
        assert check_file(path) == []


# ---------------------------------------------------------------------------
# _expected_redirect helper
# ---------------------------------------------------------------------------


class TestExpectedRedirect:
    def test_formats_correctly(self):
        result = _expected_redirect("2025", "05", "30", "My_Slug")
        assert result == "/posts/2025/05/30/My_Slug/"

    def test_zero_padded_month_day(self):
        result = _expected_redirect("2025", "01", "03", "Post")
        assert result == "/posts/2025/01/03/Post/"
