"""Promotions stay available as articles but do not lead priority summaries."""

import pytest

from scripts.lib.news_priority import is_promotional_news_title


@pytest.mark.parametrize(
    "title",
    [
        "Webinar: Identity blind spots",
        "webcast - Security operations",
        "  웨비나: SOC 운영 개선",
        "[Webinar] Identity security",
        "[웨비나] 보안 운영",
        "WEBINAR Identity security",
    ],
)
def test_explicit_event_prefixes_are_promotional(title: str) -> None:
    assert is_promotional_news_title(title)


@pytest.mark.parametrize(
    "title",
    [
        "WebinarKit vulnerability patched",
        "Webcasting server RCE fixed",
        "Researchers uncover attack on a webinar platform",
        "Xloader phishing campaign",
        "",
    ],
)
def test_product_and_incident_titles_are_not_promotional(title: str) -> None:
    assert not is_promotional_news_title(title)
