"""Digest covers must not turn promotional copy or position into threat severity."""

import pytest

from scripts.news.l20_dispatch import (
    _apply_real_content,
    _build_story,
    _digest_panels,
    _panel_from_source_title,
)


@pytest.mark.parametrize(
    "title",
    [
        "Webinar: Identity Blind Spots",
        "웨비나: Identity Blind Spots",
        "[Webinar] Identity Blind Spots",
    ],
)
def test_promotional_title_is_not_a_cover_story(title):
    assert _panel_from_source_title("The Hacker News", title) is None


def test_promotion_filter_applies_to_highlights_and_table_backfill():
    card = {"highlights": [{"source": "THN", "title": "Webinar: Identity Blind Spots"}]}
    content = (
        "| 분야 | 소스 | 핵심 내용 | 영향도 |\n"
        "|---|---|---|---|\n"
        "| Security | THN | Webinar: Identity Blind Spots | 🟠 High |\n"
        "| Security | ASEC | Xloader phishing campaign | 🟠 High |\n"
        "| Security | THN | ThreatsDay Linux bug roundup | 🟠 High |\n"
        "| Cloud | Google | Chrome Enterprise protection | 🟡 Medium |\n"
    )
    panels = _digest_panels(card, content)
    assert len(panels) == 3
    assert all("Identity" not in p["headline"] for p in panels)
    assert panels[0]["headline"] == "Xloader"


def test_real_incident_with_webinar_product_name_is_retained():
    assert (
        _panel_from_source_title("Vendor", "WebinarKit vulnerability patched")
        is not None
    )


@pytest.mark.parametrize("with_panel", [False, True])
def test_unknown_severity_uses_neutral_editorial_badge(with_panel):
    stories = [
        _build_story(
            headline="Xloader", subheadline="Security", index=i, severity_label=tag
        )
        for i, tag in enumerate(("HIGH", "HIGH", "MEDIUM"))
    ]
    info = {"content": ""}
    if with_panel:
        info["summary_card"] = {
            "highlights": [{"source": "ASEC", "title": "Xloader phishing"}]
        }
    _apply_real_content(stories, info)
    assert [story["tag"] for story in stories] == ["FOCUS"] * 3


def test_reported_story_severity_drives_badge():
    stories = [
        _build_story(
            headline="Xloader", subheadline="Security", index=0, severity_label="MEDIUM"
        )
    ]
    info = {
        "summary_card": {
            "highlights": [
                {"source": "ASEC", "title": "Xloader phishing", "severity": "🟠 High"}
            ]
        },
        "content": "",
    }
    _apply_real_content(stories, info)
    assert stories[0]["severity"] == "HIGH"
    assert stories[0]["tag"] == "HIGH"
