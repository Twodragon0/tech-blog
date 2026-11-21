"""The Slack post notifications link the live post URL.

build_slack_post_message.py and post_category_slack_digest.py built the link
from the filename day. The permalink uses the front-matter ``date`` in UTC, so
for a KST post written before 09:00 the live URL is a day earlier and those
links 404 (CLAUDE.md, "Date / Timezone Rule"). Both now use
scripts/lib/post_url.post_permalink, like the newsletter and share scripts.
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import build_slack_post_message
import post_category_slack_digest
import pytest

SITE = "https://2twodragon.com"
KST = timezone(timedelta(hours=9))


def _post(directory: Path, name: str, date: str) -> Path:
    path = directory / name
    path.write_text(
        f'---\ntitle: "T"\ndate: {date}\ncategories: [security]\n---\n\nbody\n',
        encoding="utf-8",
    )
    return path


def test_new_post_message_links_a_kst_morning_post_by_its_utc_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    (tmp_path / "_posts").mkdir()
    _post(tmp_path / "_posts", "2026-11-19-Morning.md", "2026-11-19 08:30:00 +0900")
    monkeypatch.setattr(build_slack_post_message, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(build_slack_post_message, "SITE_URL", SITE)
    monkeypatch.setattr(sys, "argv", ["x", "_posts/2026-11-19-Morning.md"])
    build_slack_post_message.main()
    assert f"<{SITE}/posts/2026/11/18/Morning/|T>" in capsys.readouterr().out


def test_category_digest_links_a_kst_morning_post_by_its_utc_day(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Dated this morning KST, so it is inside the digest's 24-hour window.
    today = datetime.now(KST).date()
    _post(tmp_path, f"{today}-Morning.md", f"{today} 08:30:00 +0900")
    monkeypatch.setattr(post_category_slack_digest, "POSTS_DIR", tmp_path)
    digest = post_category_slack_digest.build_digest(24, SITE, ["security"])
    utc_day = today - timedelta(days=1)
    assert digest == [("T", f"{SITE}/posts/{utc_day:%Y/%m/%d}/Morning/")]
