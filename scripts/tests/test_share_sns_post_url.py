"""share_sns.py shares the live post URL, day included.

It used to build ``/posts/YYYY/MM/<slug>/`` from the filename, which 404s: the
permalink is ``/posts/:year/:month/:day/:title/`` with the date in UTC.
"""

from __future__ import annotations

from pathlib import Path

import share_sns

SITE = "https://2twodragon.com"


def _post(directory: Path, name: str, date: str) -> str:
    path = directory / name
    path.write_text(f'---\ntitle: "T"\ndate: {date}\n---\n\nbody\n', encoding="utf-8")
    return str(path)


def test_share_url_carries_the_day(tmp_path: Path) -> None:
    post = _post(tmp_path, "2026-11-19-Tech_Digest.md", "2026-11-19 10:00:00 +0900")
    assert share_sns.generate_post_url(post, SITE) == (
        f"{SITE}/posts/2026/11/19/Tech_Digest/"
    )


def test_share_url_of_a_kst_midnight_post_is_the_previous_utc_day(
    tmp_path: Path,
) -> None:
    post = _post(tmp_path, "2026-11-19-Night_Post.md", "2026-11-19 00:00:00 +0900")
    assert share_sns.generate_post_url(post, SITE) == (
        f"{SITE}/posts/2026/11/18/Night_Post/"
    )
