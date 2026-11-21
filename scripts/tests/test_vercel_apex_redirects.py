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
    assert (
        destinations["/12mon-devsecops/"]
        == "https://legacy.2twodragon.com/12mon-devsecops/"
    )
    assert destinations["/wp-content/uploads/:path*"] == (
        "https://legacy.2twodragon.com/wp-content/uploads/:path*"
    )
