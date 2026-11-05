"""The publisher and workflow must select the same KST calendar day."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def test_all_digest_date_lookups_use_kst():
    workflow = Path(".github/workflows/ai-blogwatcher.yml").read_text()
    lookups = [
        line.strip()
        for line in workflow.splitlines()
        if "TODAY=$(date" in line or "TODAY=$(TZ=" in line
    ]
    assert len(lookups) == 3
    assert all(line == "TODAY=$(TZ=Asia/Seoul date +%Y-%m-%d)" for line in lookups)


def test_kst_midnight_differs_from_utc_day():
    instant = datetime.fromisoformat("2026-11-05T15:40:00+00:00")
    assert instant.astimezone(ZoneInfo("Asia/Seoul")).date().isoformat() == "2026-11-06"
    assert instant.date().isoformat() == "2026-11-05"
