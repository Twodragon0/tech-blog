"""Guard the apex cutover against obsolete WordPress host redirects."""

import json
from pathlib import Path

VERCEL_CONFIG = Path(__file__).resolve().parents[2] / "vercel.json"


def test_apex_routes_do_not_redirect_to_old_tech_host():
    redirects = json.loads(VERCEL_CONFIG.read_text())["redirects"]
    assert not [
        rule
        for rule in redirects
        if rule.get("destination", "").startswith("https://tech.2twodragon.com")
    ]
    assert not [rule for rule in redirects if rule["source"] == "/:path*"]


def test_wordpress_slug_and_uploads_reach_archive():
    redirects = json.loads(VERCEL_CONFIG.read_text())["redirects"]
    destinations = {rule["source"]: rule["destination"] for rule in redirects}
    assert destinations["/2024-f1/"] == "https://legacy.2twodragon.com/2024-f1/"
    assert destinations["/wp-content/uploads/:path*"] == (
        "https://legacy.2twodragon.com/wp-content/uploads/:path*"
    )


LEGACY_HOME = "https://legacy.2twodragon.com/"
# WordPress categories with no apex counterpart; /category/security/ is a live apex page.
WP_ONLY_CATEGORIES = ("economic", "music", "online-class", "certification", "knowledge")


def test_wordpress_taxonomy_urls_reach_archive_without_shadowing_apex():
    redirects = json.loads(VERCEL_CONFIG.read_text())["redirects"]
    destinations = {rule["source"]: rule["destination"] for rule in redirects}
    assert destinations["/tag/:path*"] == LEGACY_HOME
    for slug in WP_ONLY_CATEGORIES:
        assert destinations[f"/category/{slug}/"] == LEGACY_HOME
    assert not [
        rule for rule in redirects if rule["source"].startswith("/category/security")
    ]
    assert not [rule for rule in redirects if rule["source"] == "/category/:path*"]


def test_wordpress_feed_and_sitemap_urls_reach_apex_equivalents():
    redirects = json.loads(VERCEL_CONFIG.read_text())["redirects"]
    destinations = {rule["source"]: rule["destination"] for rule in redirects}
    assert destinations["/feed/"] == "/feed.xml"
    assert destinations["/comments/feed/"] == "/feed.xml"
    assert destinations["/wp-sitemap.xml"] == "/sitemap.xml"


def test_no_redirect_shadows_an_apex_category_page():
    redirects = json.loads(VERCEL_CONFIG.read_text())["redirects"]
    sources = {rule["source"] for rule in redirects}
    pages_dir = VERCEL_CONFIG.parent / "_category_pages"
    permalinks = {
        line.split(":", 1)[1].strip()
        for page in pages_dir.glob("*.md")
        for line in page.read_text().splitlines()
        if line.startswith("permalink:")
    }
    assert "/category/security/" in permalinks
    assert not permalinks & sources
