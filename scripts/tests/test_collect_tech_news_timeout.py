#!/usr/bin/env python3
"""Tests for timeout optimization and worker concurrency in collect_tech_news.py."""

from unittest.mock import MagicMock, patch

import requests

from scripts.collect_tech_news import (
    DEFAULT_FEED_TIMEOUT,
    fetch_all_news,
    fetch_rss_feed,
    fetch_skshieldus_insight,
    fetch_worldmonitor_tech,
)


def test_default_feed_timeout_is_ten():
    assert DEFAULT_FEED_TIMEOUT == 10


@patch("scripts.collect_tech_news.requests.get")
def test_fetch_rss_feed_timeout_handled_fast(mock_get):
    mock_get.side_effect = requests.Timeout("Connection timed out")
    source_config = {
        "name": "Slow Source",
        "feed_url": "https://slow-source.example.com/rss",
        "category": "tech",
        "language": "en",
    }
    items = fetch_rss_feed("slow_source", source_config, hours=24, timeout=5)
    assert items == []
    mock_get.assert_called_once()


@patch("scripts.collect_tech_news.requests.get")
def test_fetch_skshieldus_insight_timeout_handled(mock_get):
    mock_get.side_effect = requests.Timeout("Timeout")
    source_config = {
        "name": "SK Shieldus Test",
        "scraper": "skshieldus_eqst",
    }
    items = fetch_skshieldus_insight("skshieldus", source_config, hours=24, timeout=5)
    assert items == []


@patch("scripts.collect_tech_news.requests.get")
def test_fetch_worldmonitor_tech_timeout_handled(mock_get):
    mock_get.side_effect = requests.Timeout("Timeout")
    source_config = {
        "name": "World Monitor Test",
        "url": "https://tech.worldmonitor.app/?layers=cloudRegions",
    }
    items = fetch_worldmonitor_tech("worldmonitor", source_config, hours=24, timeout=5)
    assert items == []


@patch("scripts.collect_tech_news.fetch_rss_feed")
def test_fetch_all_news_with_workers(mock_fetch_rss):
    mock_fetch_rss.return_value = []
    test_sources = ["geeknews", "kakao_tech"]
    items = fetch_all_news(sources=test_sources, hours=24, feed_timeout=10, workers=2)
    assert items == []
    assert mock_fetch_rss.call_count == 2
