"""scripts/lib/post_url.py: the URL Jekyll gives a post.

The site builds ``/posts/:year/:month/:day/:title/`` with ``timezone: UTC``, so
the date parts are the front-matter ``date`` converted to UTC. A KST post
written between 00:00 and 08:59 therefore lives under the previous UTC day.
The newsletter and share builders used to drop the day entirely and 404ed.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.lib.post_url import post_permalink  # noqa: E402

KST = timezone(timedelta(hours=9))
NAME = "2026-05-21-Kubernetes_Security_Guide.md"


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
