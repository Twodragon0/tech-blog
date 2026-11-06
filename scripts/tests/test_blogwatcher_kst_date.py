"""Publisher KST calendar and the workflow must not scan a second clock."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.blogwatcher_manifest import KST, kst_publish_date

WORKFLOW = Path(".github/workflows/ai-blogwatcher.yml")
PUBLISHER = Path("scripts/auto_publish_news.py")


def _code(path: Path) -> str:
    return "\n".join(
        line
        for line in path.read_text(encoding="utf-8").splitlines()
        if not line.lstrip().startswith("#")
    )


def test_workflow_consumes_the_manifest_instead_of_a_clock():
    body = _code(WORKFLOW)
    assert "date +%Y-%m-%d" not in body
    assert "find _posts" not in body
    assert "find assets/images" not in body
    assert "_posts/${TODAY}" not in body
    assert "blogwatcher_manifest.py resolve" in body
    assert "blogwatcher_manifest.py preserve-on-failure" in body
    assert 'git add -- "${to_add[@]}"' in body
    assert "nothing was staged for commit" in body
    assert "if: steps.check_news.outputs.has_enough_news == 'true'" in body
    raw = WORKFLOW.read_text(encoding="utf-8")
    assert raw.index("Commit and publish") < raw.index("Preserve unpublished digest")
    assert raw.index("Preserve unpublished digest") < raw.index("Upload rejected draft")


def test_publisher_dates_filenames_with_kst_publish_date():
    body = _code(PUBLISHER)
    assert "kst_publish_date(" in body
    assert "datetime.now(timezone(timedelta(hours=9)))" not in body


def test_utc_late_evening_is_the_next_kst_morning():
    """Run 41770313270 wrote the digest at 2026-11-04 23:11 UTC."""
    source = datetime(2026, 11, 4, 23, 11, tzinfo=timezone.utc)
    instant, day = kst_publish_date(source)
    assert source.date().isoformat() == "2026-11-04"
    assert day == "2026-11-05"
    assert instant.hour == 8


def test_kst_0900_matches_the_utc_calendar_day():
    source = datetime(2026, 11, 5, 0, 0, tzinfo=timezone.utc)
    instant, day = kst_publish_date(source)
    assert source.date().isoformat() == "2026-11-05"
    assert day == "2026-11-05"
    assert instant.hour == 9


def test_forced_date_keeps_the_kst_hour():
    instant, day = kst_publish_date(
        datetime(2026, 11, 4, 23, 11, tzinfo=timezone.utc),
        forced="2026-11-01",
    )
    assert day == "2026-11-01"
    assert instant.astimezone(KST).hour == 8


def test_naive_datetime_is_already_kst():
    naive = datetime(2026, 11, 6, 8, 30)
    instant, day = kst_publish_date(naive)
    assert day == "2026-11-06"
    assert instant.tzinfo == timezone(timedelta(hours=9))
    assert instant.hour == 8
