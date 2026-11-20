"""Domain decision guard: tech.2twodragon.com is canonical, the apex only redirects.

Decided 2026-11-20 (docs/seo/apex-domain-cutover.md, AGENTS.md). The same day a
parallel change switched `url` to the apex before the apex served this site: every
tech page then declared a WordPress URL as its canonical and pointed og:image,
favicon and RSS at it. These checks make that state fail CI instead of shipping.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VERCEL_JSON = REPO_ROOT / "vercel.json"
CONFIG = REPO_ROOT / "_config.yml"

CANONICAL = "https://tech.2twodragon.com"
APEX_HOSTS = {"2twodragon.com", "www.2twodragon.com"}
OFF_SITE = (
    "https://2twodragon.com",
    "https://www.2twodragon.com",
    "https://legacy.2twodragon.com",
)


def _redirects() -> list[dict]:
    return json.loads(VERCEL_JSON.read_text(encoding="utf-8"))["redirects"]


def _apex_scoped(rule: dict) -> bool:
    for cond in rule.get("has", []):
        value = cond.get("value")
        if cond.get("type") == "host" and isinstance(value, dict):
            hosts = set(value.get("inc", []))
            if hosts and hosts <= APEX_HOSTS:
                return True
    return False


def test_site_url_is_the_tech_host():
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert config["url"] == CANONICAL


def test_off_site_redirects_only_fire_on_the_apex():
    # An unscoped rule sending a path to the apex or the archive would also fire
    # on tech.2twodragon.com and take readers off the canonical site.
    leaking = [
        r["source"]
        for r in _redirects()
        if r["destination"].startswith(OFF_SITE) and not _apex_scoped(r)
    ]
    assert not leaking, leaking


def test_apex_rules_never_target_the_apex_itself():
    looping = [
        r["source"]
        for r in _redirects()
        if _apex_scoped(r) and r["destination"].startswith(OFF_SITE[:2])
    ]
    assert not looping, looping


def _catch_all() -> dict:
    rules = [
        r for r in _redirects() if _apex_scoped(r) and r["source"].startswith("/:path(")
    ]
    assert len(rules) == 1, [r["source"] for r in rules]
    return rules[0]


def _matches(source: str, path: str) -> bool:
    # vercel.json `/:path(<re>)` → the custom group is matched against the rest of the path.
    inner = source[len("/:path(") : -1]
    return re.fullmatch("/" + inner, path) is not None


def test_apex_catch_all_serves_ads_txt_and_robots_txt():
    # tech.2twodragon.com/ads.txt 301s to the apex, and AdSense reads the
    # root-domain ads.txt for tech.* inventory, so the apex must serve the file.
    source = _catch_all()["source"]
    for path in ("/ads.txt", "/app-ads.txt", "/robots.txt"):
        assert not _matches(source, path), path
    for path in ("/", "/economic-bitcoin/", "/wp-login.php", "/x/ads.txt"):
        assert _matches(source, path), path
    assert _catch_all()["destination"] == CANONICAL + "/"


def test_ads_txt_is_built():
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    assert (REPO_ROOT / "ads.txt").is_file()
    assert "ads.txt" not in (config.get("exclude") or [])
