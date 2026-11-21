"""Guard: migrated WordPress slugs 301 to their apex post, not the legacy archive.

``data/wp_redirect_map.json`` lists the 52 WordPress security slugs from the
retired 2twodragon.com site. 50 carry a ``target``, the URL of the same
article on this blog; 2 are null (not migrated, so the archive keeps them).
The archive redirect map in vercel.json sent all 52 to
https://legacy.2twodragon.com/<slug>/, so every migrated article had a second
copy and the old URL's link equity went to the archive instead of the post.

Rules are matched the way Vercel does here: the first rule whose ``source``
equals the request path wins. Vercel compares the percent-encoded path
case-sensitively, so a slug with a non-ASCII character needs a rule for
WordPress's lowercase encoding and for the uppercase encoding browsers send.
The raw-character rule is defensive: clients that send raw UTF-8 bytes are
re-encoded upstream and land on the uppercase rule.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import frontmatter
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.lib.post_url import post_permalink  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
VERCEL_CONFIG = REPO_ROOT / "vercel.json"
WP_MAP = REPO_ROOT / "data" / "wp_redirect_map.json"
POSTS_DIR = REPO_ROOT / "_posts"
LEGACY_ORIGIN = "https://legacy.2twodragon.com"

ENTRIES = json.loads(WP_MAP.read_text(encoding="utf-8"))
MIGRATED = [e for e in ENTRIES if e["target"]]
UNMIGRATED = [e for e in ENTRIES if not e["target"]]
REDIRECTS = json.loads(VERCEL_CONFIG.read_text(encoding="utf-8"))["redirects"]
_PERCENT_ESCAPE = re.compile(r"%[0-9A-Fa-f]{2}")
_POST_FILENAME = re.compile(r"^\d{4}-\d{2}-\d{2}-(?P<title>.+)$")


def request_paths(entry: dict) -> list[str]:
    """Every form the old WordPress path can arrive in."""
    paths = [entry["wp_path"]]
    encoded = entry.get("wp_path_encoded")
    if encoded:
        for case in (str.lower, str.upper):
            paths.append(_PERCENT_ESCAPE.sub(lambda m: case(m.group(0)), encoded))
    return list(dict.fromkeys(paths))


def first_rule(path: str) -> dict | None:
    return next((rule for rule in REDIRECTS if rule["source"] == path), None)


def post_url(path: Path) -> str:
    """The URL Jekyll gives a post: ``/posts/:year/:month/:day/:title/``.

    ``_config.yml`` pins ``timezone: UTC``, so the date parts come from the
    front-matter ``date`` converted to UTC, and ``:title`` is the filename slug.
    Built by the same helper the newsletter and share scripts use.
    """
    return post_permalink(path, frontmatter.load(path).metadata["date"])


MIGRATED_PATHS = [(path, e["target"]) for e in MIGRATED for path in request_paths(e)]


@pytest.mark.parametrize(
    "path,target", MIGRATED_PATHS, ids=[path for path, _ in MIGRATED_PATHS]
)
def test_migrated_slug_redirects_to_apex_post(path, target):
    rule = first_rule(path)
    assert rule is not None, f"no redirect rule for {path}"
    assert (rule["destination"], rule.get("statusCode")) == (target, 301)


def test_no_rule_sends_a_migrated_slug_to_legacy():
    migrated = {path for path, _ in MIGRATED_PATHS}
    to_legacy = [
        rule["source"]
        for rule in REDIRECTS
        if rule["source"] in migrated and rule["destination"].startswith(LEGACY_ORIGIN)
    ]
    assert not to_legacy


@pytest.mark.parametrize("entry", UNMIGRATED, ids=[e["wp_slug"] for e in UNMIGRATED])
def test_unmigrated_slug_stays_on_legacy(entry):
    rule = first_rule(entry["wp_path"])
    assert rule is not None, f"no redirect rule for {entry['wp_path']}"
    assert rule["destination"] == LEGACY_ORIGIN + entry["wp_path"]


@pytest.mark.parametrize("entry", MIGRATED, ids=[e["wp_slug"] for e in MIGRATED])
def test_target_is_an_existing_post(entry):
    title = entry["target"].rstrip("/").rsplit("/", 1)[-1]
    candidates = [
        p
        for p in POSTS_DIR.glob("*.md")
        if (m := _POST_FILENAME.match(p.stem)) and m["title"] == title
    ]
    building = [p for p in candidates if post_url(p) == entry["target"]]
    assert building, f"{entry['wp_slug']}: no _posts file builds {entry['target']}"
    # post_url() derives the URL from date + filename only; an override would
    # move or hide the post while this test still passed.
    meta = frontmatter.load(building[0]).metadata
    assert not {"permalink", "slug"} & meta.keys(), building[0].name
    assert meta.get("published", True) is not False, building[0].name


def test_no_pattern_rule_precedes_a_migrated_rule():
    # first_rule() only knows exact sources. A pattern (":param", "(...)", "*")
    # above the WordPress block could capture an old URL before its own rule.
    migrated = {path for path, _ in MIGRATED_PATHS}
    last = max(i for i, rule in enumerate(REDIRECTS) if rule["source"] in migrated)
    patterns = [
        rule["source"]
        for rule in REDIRECTS[:last]
        if any(ch in rule["source"] for ch in ":(*")
    ]
    assert not patterns, patterns
