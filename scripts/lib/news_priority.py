"""Shared, narrow exclusions for digest priority surfaces."""

import re

_PROMOTIONAL_PREFIX = re.compile(
    r"^\s*(?:\[(?:webinar|webcast|웨비나)\]|(?:webinar|webcast|웨비나)(?=$|[\s:：—–-]))",
    re.IGNORECASE,
)


def is_promotional_news_title(title: str) -> bool:
    """Identify explicit event promotions without matching product names."""
    return bool(_PROMOTIONAL_PREFIX.match(title))
