#!/usr/bin/env python3
"""The URL Jekyll actually gives a post, built in one place.

Why this exists
---------------
``_config.yml`` sets ``permalink: /posts/:year/:month/:day/:title/`` and
``timezone: UTC``. Jekyll converts the front-matter ``date`` to UTC before it
fills in the date parts, so the URL date is not always the filename date::

    date: 2026-05-21 09:00:00 +0900   ->  /posts/2026/05/21/<slug>/
    date: 2026-05-21 08:59:59 +0900   ->  /posts/2026/05/20/<slug>/

(CLAUDE.md, "Date / Timezone Rule".) ``buttondown_notify.py`` and
``share_sns.py`` each rebuilt the URL from the filename and dropped the day
entirely (``/posts/YYYY/MM/<slug>/``), so every newsletter and share link they
produced was a 404.

``:title`` is the filename slug after the ``YYYY-MM-DD-`` prefix. Filenames are
ASCII (``[A-Za-z0-9_.+-]``), which Jekyll's slugify leaves unchanged, and no post
overrides the URL with ``slug:`` or ``permalink:``.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timezone
from pathlib import Path

__all__ = ["post_permalink"]

_FILENAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-(.+)$")

# "2026-05-21 09:00:00 +0900": fromisoformat() accepts "+0900" but not the space
# in front of it.
_SPACE_BEFORE_OFFSET_RE = re.compile(r"\s+(?=(?:Z|[+-]\d{2}:?\d{2})$)")


def _utc_day(value: object) -> date | None:
    """The UTC calendar day of a front-matter ``date``, or None if unusable.

    PyYAML returns three shapes. This repo's ``YYYY-MM-DD HH:MM:SS +0900`` comes
    back as a ``str`` (an offset without a colon is not a YAML timestamp),
    ``+09:00`` and ``Z`` forms come back as an aware ``datetime``, and a bare day
    as a ``date``. A naive time is treated as UTC, the site timezone.
    """
    if isinstance(value, datetime):
        when = value
    elif isinstance(value, date):
        return value
    elif isinstance(value, str):
        text = _SPACE_BEFORE_OFFSET_RE.sub("", value.strip())
        try:
            when = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    if when.tzinfo is not None:
        when = when.astimezone(timezone.utc)
    return when.date()


def post_permalink(filename: str | Path, front_matter_date: object = None) -> str:
    """Return ``/posts/YYYY/MM/DD/<slug>/`` for a ``_posts`` file.

    ``front_matter_date`` is the post's ``date`` value as YAML parsed it. If it
    is missing or unparsable, the filename date is used, which is what Jekyll
    does for a post without ``date:``. Jekyll does not publish a file without
    the date prefix at all; for one of those this returns ``/posts/<stem>/``,
    the fallback the old builders had, so callers do not crash.
    """
    stem = Path(filename).stem
    match = _FILENAME_RE.match(stem)
    if not match:
        return f"/posts/{stem}/"
    year, month, day, slug = match.groups()
    utc_day = _utc_day(front_matter_date) or date(int(year), int(month), int(day))
    return f"/posts/{utc_day:%Y/%m/%d}/{slug}/"
