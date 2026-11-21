"""scripts/lib/post_url.py: the URL Jekyll gives a post.

The site builds ``/posts/:year/:month/:day/:title/`` with ``timezone: UTC``, so
the date parts are the front-matter ``date`` converted to UTC. A KST post
written between 00:00 and 08:59 therefore lives under the previous UTC day.
The newsletter and share builders used to drop the day entirely and 404ed.
"""

from __future__ import annotations

import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.lib.post_url import _isoformat, _utc_day, post_permalink  # noqa: E402

KST = timezone(timedelta(hours=9))
NAME = "2026-05-21-Kubernetes_Security_Guide.md"
POSTS_DIR = Path(__file__).resolve().parents[2] / "_posts"


def _yaml_date(line: str) -> object:
    """The ``date`` value exactly as callers get it from PyYAML."""
    return yaml.safe_load(line)["date"]


@pytest.mark.parametrize(
    "front_matter_date, expected_day",
    [
        # This repo's format; PyYAML leaves "+0900" (no colon) as a str.
        ("2026-05-21 00:00:00 +0900", "2026/05/20"),
        ("2026-05-21 08:59:59 +0900", "2026/05/20"),
        ("2026-05-21 09:00:00 +0900", "2026/05/21"),
        ("2026-05-21 20:36:28 +0900", "2026/05/21"),
    ],
)
def test_kst_morning_posts_land_on_the_previous_utc_day(
    front_matter_date: str, expected_day: str
) -> None:
    value = _yaml_date(f"date: {front_matter_date}")
    assert isinstance(value, str)
    assert post_permalink(NAME, value) == (
        f"/posts/{expected_day}/Kubernetes_Security_Guide/"
    )


def test_normal_post_keeps_the_filename_day() -> None:
    url = post_permalink("2026-11-19-Tech_Digest.md", "2026-11-19 10:00:00 +0900")
    assert url == "/posts/2026/11/19/Tech_Digest/"


def test_url_always_carries_the_day() -> None:
    """The defect being fixed: /posts/YYYY/MM/<slug>/ without the day."""
    url = post_permalink(NAME, "2026-05-21 12:00:00 +0900")
    assert url.split("/")[2:5] == ["2026", "05", "21"]


def test_kst_midnight_on_new_year_rolls_back_month_and_year() -> None:
    url = post_permalink("2026-01-01-New_Year.md", "2026-01-01 00:30:00 +0900")
    assert url == "/posts/2025/12/31/New_Year/"


@pytest.mark.parametrize(
    "line, expected_day",
    [
        ("date: 2026-05-21 08:00:00 +09:00", "2026/05/20"),  # aware datetime
        ("date: 2026-05-20T23:00:00Z", "2026/05/20"),  # aware datetime, UTC
        ("date: 2026-05-21", "2026/05/21"),  # date
        ("date: 2026-05-21 03:00:00", "2026/05/21"),  # naive -> site tz (UTC)
    ],
)
def test_every_shape_pyyaml_returns(line: str, expected_day: str) -> None:
    assert post_permalink(NAME, _yaml_date(line)) == (
        f"/posts/{expected_day}/Kubernetes_Security_Guide/"
    )


def test_python_datetime_and_date_objects() -> None:
    aware = datetime(2026, 5, 21, 0, 0, tzinfo=KST)
    assert post_permalink(NAME, aware).startswith("/posts/2026/05/20/")
    assert post_permalink(NAME, date(2026, 5, 21)).startswith("/posts/2026/05/21/")


def test_negative_offset_can_move_the_url_a_day_later() -> None:
    url = post_permalink(NAME, "2026-05-21 22:00:00 -0500")
    assert url == "/posts/2026/05/22/Kubernetes_Security_Guide/"


@pytest.mark.parametrize("missing", [None, "", "not a date", 20260521, ["x"]])
def test_missing_or_unusable_date_falls_back_to_the_filename(missing: object) -> None:
    assert post_permalink(NAME, missing) == (
        "/posts/2026/05/21/Kubernetes_Security_Guide/"
    )


def test_accepts_paths_and_uses_only_the_basename() -> None:
    path = Path("/repo/_posts") / NAME
    assert post_permalink(path, "2026-05-21 08:00:00 +0900") == (
        "/posts/2026/05/20/Kubernetes_Security_Guide/"
    )
    assert post_permalink(f"_posts/{NAME}") == (
        "/posts/2026/05/21/Kubernetes_Security_Guide/"
    )


def test_slug_is_kept_verbatim() -> None:
    name = "2026-11-13-Tech_Security_Weekly_Digest_Threat_Zero-Day_Security_AI.md"
    assert post_permalink(name, "2026-11-13 10:00:00 +0900") == (
        "/posts/2026/11/13/Tech_Security_Weekly_Digest_Threat_Zero-Day_Security_AI/"
    )


def test_dateless_filename_keeps_the_old_fallback() -> None:
    assert post_permalink("about.md") == "/posts/about/"


@pytest.mark.parametrize(
    "front_matter_date, expected_day",
    [
        ("2026-05-21 8:59:59 +0900", "2026/05/20"),
        ("2026-05-21 9:00:00 +0900", "2026/05/21"),
    ],
)
def test_single_digit_hours_parse_as_jekyll_reads_them(
    front_matter_date: str, expected_day: str
) -> None:
    """Ruby's Time.parse takes "9:00:00"; fromisoformat() needs "09"."""
    value = _yaml_date(f"date: {front_matter_date}")
    assert post_permalink(NAME, value) == (
        f"/posts/{expected_day}/Kubernetes_Security_Guide/"
    )


@pytest.mark.parametrize(
    "text, iso",
    [
        ("2026-05-21 09:00:00 +0900", "2026-05-21 09:00:00+09:00"),
        ("2026-05-21 9:00:00 +0900", "2026-05-21 09:00:00+09:00"),
        ("2026-05-21T9:00:00+0900", "2026-05-21T09:00:00+09:00"),
        ("2026-05-21 22:00:00 -0500", "2026-05-21 22:00:00-05:00"),
        ("2026-05-21 08:00:00 +09:00", "2026-05-21 08:00:00+09:00"),
        ("2026-05-20T23:00:00Z", "2026-05-20T23:00:00+00:00"),
        ("2026-05-21 09:00:00.500 +0900", "2026-05-21 09:00:00.500+09:00"),
        ("2026-05-21 03:00:00", "2026-05-21 03:00:00"),
        ("2026-05-21", "2026-05-21"),
    ],
)
def test_dates_are_rewritten_into_a_form_python_3_7_to_3_10_reads(
    text: str, iso: str
) -> None:
    """fromisoformat() before 3.11 rejects "+0900", "Z" and a space before the
    offset, so a 3.10 run would have used the filename day for every post."""
    assert _isoformat(text) == iso


def test_every_post_date_parses_without_the_filename_fallback() -> None:
    """A date the parser rejects falls back to the filename day silently, and
    that is the wrong URL for any KST post written before 09:00."""
    posts = sorted(POSTS_DIR.glob("*.md"))
    assert posts, f"no posts found in {POSTS_DIR}"
    unparsed = []
    for path in posts:
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
        front = yaml.safe_load(match.group(1)) if match else None
        value = front.get("date") if isinstance(front, dict) else None
        if _utc_day(value) is None:
            unparsed.append(f"{path.name}: date {value!r}")
    assert not unparsed, "\n".join(unparsed)
