"""Regression test: auto_publish_news content generators must emit
`last_modified_at:` in the YAML front matter.

Context: 14 weekly digest posts (2026-05-07 ~ 2026-05-21) were published
without `last_modified_at`, blocking the SEO LastModified signal that Bing/
Google use to schedule re-crawl. Root cause: the content generators emitted
`date:` but not `last_modified_at:`. Fix adds `last_modified_at:` immediately
after `date:` using the same publish timestamp.

This test pins that fix so the field never silently disappears again.

API disabling and path setup are handled by conftest.py.
"""

import datetime
import re

import pytest
import yaml

from auto_publish_news import generate_post_content, generate_tech_blog_content


def _make_items(titles, category="security"):
    return [
        {
            "title": t,
            "summary": "test summary",
            "url": f"https://example.com/{i}",
            "source_name": "TestSource",
            "source": "TestSource",
            "category": category,
            "published": "2026-05-22T01:00:00Z",
        }
        for i, t in enumerate(titles)
    ]


def _extract_frontmatter(content: str) -> dict:
    fm_block = content.split("---", 2)[1]
    return yaml.safe_load(fm_block) or {}


def _publish_date() -> datetime.datetime:
    # Match the production code path: KST-anchored datetime.
    return datetime.datetime(2026, 5, 22, 9, 30, 0, tzinfo=datetime.timezone.utc)


class TestLastModifiedAtEmission:
    """Both content generators must emit `last_modified_at:` in front matter."""

    def test_security_generator_emits_last_modified_at(self):
        items = _make_items(
            [
                "Critical CVE-2026-9999 in Kubernetes admission controller",
                "AWS S3 misconfiguration leaks 10M records",
                "OpenAI rolls out new agent security guardrails",
            ]
        )
        categorized = {
            "security": items,
            "ai": [],
            "cloud": [],
            "devops": [],
            "blockchain": [],
            "tech": [],
        }
        content = generate_post_content(items, categorized, _publish_date())

        front = _extract_frontmatter(content)
        assert "last_modified_at" in front, (
            "generate_post_content must emit `last_modified_at:` in front matter"
        )
        # yaml.safe_load returns aware datetime when timezone offset present.
        lm = front["last_modified_at"]
        assert lm is not None
        assert isinstance(lm, (datetime.datetime, str))

    def test_tech_generator_emits_last_modified_at(self):
        items = _make_items(
            [
                "Anthropic releases Claude Opus 4.7 with 1M context window",
                "Vercel introduces edge AI inference",
                "Rust 1.85 stabilizes async closures",
            ],
            category="tech",
        )
        categorized = {
            "tech": items,
            "ai": [],
            "cloud": [],
            "devops": [],
        }
        content = generate_tech_blog_content(items, categorized, _publish_date())

        front = _extract_frontmatter(content)
        assert "last_modified_at" in front, (
            "generate_tech_blog_content must emit `last_modified_at:` in front matter"
        )

    def test_last_modified_at_matches_publish_date(self):
        """`last_modified_at` must equal the publish `date:` at creation time."""
        items = _make_items(["Sample headline for date match"])
        categorized = {
            "security": items,
            "ai": [],
            "cloud": [],
            "devops": [],
            "blockchain": [],
            "tech": [],
        }
        date = _publish_date()
        content = generate_post_content(items, categorized, date)

        # Both fields must reference the same calendar timestamp. YAML may
        # parse the two fields with slightly different formats (`date:` uses
        # `YYYY-MM-DD HH:MM:SS +0900` whereas `last_modified_at:` uses
        # ISO-8601 with `T` separator). Normalize to UTC datetime and compare.
        front = _extract_frontmatter(content)
        d = front["date"]
        lm = front["last_modified_at"]

        def _as_utc(value):
            if isinstance(value, datetime.datetime):
                return value.astimezone(datetime.timezone.utc).replace(microsecond=0)
            # Fallback: parse string form.
            return datetime.datetime.fromisoformat(
                str(value).replace(" +0900", "+09:00")
            ).astimezone(datetime.timezone.utc).replace(microsecond=0)

        assert _as_utc(d) == _as_utc(lm), (
            f"date ({d}) and last_modified_at ({lm}) must match at publish time"
        )

    def test_last_modified_at_position_after_date(self):
        """For readability, `last_modified_at:` should appear immediately after `date:`."""
        items = _make_items(["Headline ordering"])
        categorized = {
            "security": items,
            "ai": [],
            "cloud": [],
            "devops": [],
            "blockchain": [],
            "tech": [],
        }
        content = generate_post_content(items, categorized, _publish_date())

        # Look at the raw front matter block (not parsed) to assert ordering.
        fm_block = content.split("---", 2)[1]
        m = re.search(
            r"^date:.*?\n^last_modified_at:.*?$",
            fm_block,
            re.MULTILINE | re.DOTALL,
        )
        assert m, (
            "Expected `last_modified_at:` to follow `date:` on the next line.\n"
            f"Front matter:\n{fm_block}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
