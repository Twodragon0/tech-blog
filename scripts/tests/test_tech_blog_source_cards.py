"""Tech digest groups share source cards and the existing Liquid escaping path."""

import copy
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

import pytest
import requests

from scripts.check_duplicate_card_summary import CARD_RE
from scripts.news import config
from scripts.news.content_generator import generate_tech_blog_content
from scripts.news.qa_gate import validate_stats_consistency
from scripts.tests.test_pages_feed_origin import jekyll_available


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(config, "_AI_MODE", "none")

    def blocked(*args, **kwargs):
        raise AssertionError("Source-card rendering must not call an API")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked)


def _tech_rows():
    rows = []
    for index, (category, name, source) in enumerate(
        [
            ("ai", "Acme AI", "Vendor"),
            ("devops", "Acme DevOps", "Vendor"),
            ("cloud", "Acme cloud", "Vendor"),
            ("tech", "Rust", "Vendor"),
            ("tech", "Acme 제품", "Vendor"),
            ("tech", "Acme 제품", "geeknews"),
        ]
    ):
        rows.append(
            {
                "id": f"card-regression-{index}",
                "title": f'{name} "업데이트" 공개',
                "summary": 'v2.4의 CVE-2026-12345 수정 내용과 $30 비용을 "확인"해야 한다.',
                "url": f"https://vendor.test/article-{index}?view=full&format=html",
                "source": source,
                "source_name": 'Vendor "Studio"',
                "category": category,
            }
        )
    return rows


def test_all_groups_keep_source_urls_facts_and_quote_safe_fields():
    rows = _tech_rows()
    before = copy.deepcopy(rows)
    content = generate_tech_blog_content(
        rows, {"tech": rows}, datetime(2026, 11, 8, tzinfo=timezone.utc), "Acme_Rust"
    )
    cards = list(CARD_RE.finditer(content))
    assert cards
    found = {}
    for card in cards:
        attrs = dict(re.findall(r'([a-z]+)="([^"]*)"', card.group()))
        found[attrs["url"]] = attrs
        assert attrs["severity"]
        assert attrs["source"] == "Vendor ”Studio”"
        assert "v2.4" in attrs["summary"] and "CVE-2026-12345" in attrs["summary"]
        assert "$30" in attrs["summary"] and "”확인”" in attrs["summary"]
    assert set(found) == {row["url"] for row in rows}
    for heading in (
        "GeekNews 하이라이트",
        "AI/ML 트렌드",
        "DevOps & Cloud",
        "Open Source",
        "기타 주목할 뉴스",
    ):
        assert heading in content
    assert validate_stats_consistency(content) == []
    assert rows == before


def test_title_only_tech_item_still_has_a_canonical_source_card():
    row = {
        "id": "title-only",
        "title": "Acme 제품 소식",
        "summary": "",
        "category": "tech",
        "source": "Vendor",
        "url": "https://vendor.test/title-only",
    }
    content = generate_tech_blog_content(
        [row], {"tech": [row]}, datetime(2026, 11, 8, tzinfo=timezone.utc)
    )
    cards = list(CARD_RE.finditer(content))
    assert len(cards) == 1
    assert 'url="https://vendor.test/title-only"' in cards[0].group()


@pytest.mark.usefixtures("jekyll_available")
def test_rendered_tech_cards_keep_source_links_and_quoted_facts(tmp_path):
    root = Path(__file__).resolve().parents[2]
    rows = _tech_rows()
    content = generate_tech_blog_content(
        rows, {"tech": rows}, datetime(2026, 11, 8, tzinfo=timezone.utc), "Acme_Rust"
    )
    source = tmp_path / "source"
    (source / "_includes").mkdir(parents=True)
    for include in ("news-card.html", "ai-summary-card.html"):
        shutil.copy(root / "_includes" / include, source / "_includes" / include)
    (source / "index.md").write_text(content)
    # The generator includes real related-post references from the repo. Keep
    # those Liquid tags intact and supply tiny target posts in this isolated site.
    references = re.findall(r"\{%\s*post_url\s+([A-Za-z0-9_-]+)\s*%\}", content)
    if references:
        (source / "_posts").mkdir()
        for reference in references:
            (source / "_posts" / f"{reference}.md").write_text(
                "---\nlayout: null\ntitle: Related reference\n---\nReference fixture.\n"
            )
    base = tmp_path / "config.yml"
    base.write_text('url: "https://tech.2twodragon.com"\nbaseurl: ""\nplugins: []\n')
    result = subprocess.run(
        [
            "bundle",
            "exec",
            "jekyll",
            "build",
            "--source",
            str(source),
            "--destination",
            str(tmp_path / "out"),
            "--config",
            str(base),
            "--quiet",
        ],
        cwd=root,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    class Rendered(HTMLParser):
        def __init__(self):
            super().__init__()
            self.links = []
            self.text = []

        def handle_starttag(self, tag, attrs):
            if tag == "a":
                self.links.append(dict(attrs).get("href", ""))

        def handle_data(self, data):
            self.text.append(data)

    parsed = Rendered()
    parsed.feed((tmp_path / "out" / "index.html").read_text())
    assert {row["url"] for row in rows} <= set(parsed.links)
    text = " ".join(parsed.text)
    assert "Vendor ”Studio”" in text
    assert "v2.4" in text and "CVE-2026-12345" in text and "$30" in text
    assert "”확인”" in text
