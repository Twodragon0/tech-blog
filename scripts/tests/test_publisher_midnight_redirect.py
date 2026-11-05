"""KST midnight publication keeps its actual date and filename URL reachable."""
from datetime import datetime, timedelta, timezone

import pytest
import yaml
from auto_publish_news import _ensure_midnight_redirect

from scripts.check_kst_midnight import check_file


@pytest.mark.parametrize("hour", [0, 8, 9])
@pytest.mark.parametrize("existing", ["", "redirect_from: /old/\n", "redirect_from:\n- /old/\n"])
def test_redirect_covers_resolved_filename_without_changing_date(tmp_path, hour, existing):
    now = datetime(2026, 11, 6, hour, 12, tzinfo=timezone(timedelta(hours=9)))
    date = now.strftime("%Y-%m-%d %H:%M:%S %z")
    content = f'---\ntitle: "Keep quoted title"\ndate: {date}\n{existing}tags: [ai]\n---\nBody\n'
    # The explicit filename can differ from the requested publication date.
    filename = "2026-11-05-Override_Slug.md"
    result = _ensure_midnight_redirect(content, filename, now)
    assert f"date: {date}" in result
    assert 'title: "Keep quoted title"' in result
    assert result.endswith("\nBody\n")
    if hour >= 9:
        assert result == content
    else:
        fm = yaml.safe_load(result.split("---", 2)[1])
        assert "/posts/2026/11/05/Override_Slug/" in fm["redirect_from"]
        if existing:
            assert "/old/" in fm["redirect_from"]
        assert _ensure_midnight_redirect(result, filename, now) == result
    post = tmp_path / filename
    post.write_text(result)
    assert check_file(post) == []
