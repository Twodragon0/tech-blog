#!/usr/bin/env python3
"""Tests for automated cross-reference emission in content_generator.py."""

from datetime import datetime, timezone

from scripts.news.content_generator import (
    _get_recent_digest_links,
    generate_post_content,
    generate_tech_blog_content,
)


def _make_sample_items():
    return [
        {
            "title": "Sample Security Advisory",
            "summary": "Sample summary for security testing.",
            "url": "https://example.com/sec1",
            "source_name": "SecurityWeek",
            "source": "SecurityWeek",
            "category": "security",
            "published": "2026-09-20T01:00:00Z",
        }
    ]


def _make_categorized(items):
    return {
        "security": items,
        "ai": [],
        "cloud": [],
        "devops": [],
        "blockchain": [],
        "tech": [],
    }


def test_get_recent_digest_links_finds_posts():
    target_date = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
    links = _get_recent_digest_links(target_date, count=3)
    assert "{% post_url" in links
    assert "2026-09-19" in links
    assert "2026-09-18" in links
    assert "2026-09-17" in links


def test_generate_post_content_includes_cross_refs():
    target_date = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
    items = _make_sample_items()
    categorized = _make_categorized(items)
    content = generate_post_content(items, categorized, target_date, "Test_Topic")

    assert "## 관련 포스트 및 참고 자료" in content
    assert "{% post_url" in content


def test_generate_tech_blog_content_includes_cross_refs():
    target_date = datetime(2026, 9, 20, 10, 0, 0, tzinfo=timezone.utc)
    items = _make_sample_items()
    categorized = _make_categorized(items)
    content = generate_tech_blog_content(items, categorized, target_date, "Test_Tech")

    assert "## 관련 포스트 및 참고 자료" in content
    assert "{% post_url" in content
