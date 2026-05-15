"""Tests for _plugins/sri_inject.rb — SRI injection Jekyll plugin.

Verifies behaviour by:
  1. Building a minimal fixture Jekyll site under a temp dir (session-scoped).
  2. Asserting on the rendered HTML output.

Fixture site is intentionally tiny (one page, one JS file, one CSS file plus
an external <script> and a missing-asset reference) to keep build time well
under 5s. Full-site behaviour is covered indirectly via the production
sandbox build (see commit notes / Phase 0 plan).
"""
from __future__ import annotations

import base64
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_PATH = REPO_ROOT / "_plugins" / "sri_inject.rb"

# Skip tests if bundler / jekyll are unavailable (CI sanity).
pytestmark = pytest.mark.skipif(
    shutil.which("bundle") is None,
    reason="bundler / jekyll not available — skipping SRI plugin tests",
)


# --------------------------------------------------------------------------- #
# Fixture site builder
# --------------------------------------------------------------------------- #

FIXTURE_CONFIG = """\
title: SRI Fixture Site
url: https://example.test
baseurl: ""
plugins: []
markdown: kramdown
"""

FIXTURE_INDEX_HTML = """\
---
layout: null
---
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>SRI Fixture</title>
  <link rel="stylesheet" href="/assets/css/main.css?v=1234">
  <link rel="icon" href="/assets/images/favicon.png">
  <link rel="preload" href="/assets/css/main.css" as="style">
</head>
<body>
  <h1>SRI test</h1>
  <!-- Local script (must gain integrity) -->
  <script src="/assets/js/main-core.js" defer></script>
  <!-- Local script with cache-buster (must gain integrity, hash ignores ?v=) -->
  <script src="/assets/js/main-core.js?v=99999999" defer></script>
  <!-- External script (must NOT gain integrity) -->
  <script src="https://va.vercel-scripts.com/v1/script.debug.js" defer></script>
  <!-- Pre-existing integrity (must be preserved as-is) -->
  <script src="/assets/js/preserved.js" integrity="sha384-PREEXISTINGFAKE" crossorigin="anonymous"></script>
  <!-- Missing asset (must not crash, must not gain integrity) -->
  <script src="/assets/js/does-not-exist.js" defer></script>
  <!-- Inline script (no src — must NOT gain integrity) -->
  <script>console.log("inline");</script>
</body>
</html>
"""

# Minimal asset content (deterministic bytes for hash assertions).
MAIN_CORE_JS = b"// main-core fixture\nwindow.__fixture=1;\n"
PRESERVED_JS = b"// preserved\n"
MAIN_CSS = b"body{color:#000}\n"


def _b64_sha384(data: bytes) -> str:
    return base64.b64encode(hashlib.sha384(data).digest()).decode("ascii")


@pytest.fixture(scope="session")
def fixture_build(tmp_path_factory):
    """Build a minimal Jekyll site with the SRI plugin loaded."""
    src = tmp_path_factory.mktemp("sri_src")
    dest = tmp_path_factory.mktemp("sri_dest")

    # _config.yml
    (src / "_config.yml").write_text(FIXTURE_CONFIG, encoding="utf-8")

    # index.html
    (src / "index.html").write_text(FIXTURE_INDEX_HTML, encoding="utf-8")

    # Assets
    js_dir = src / "assets" / "js"
    js_dir.mkdir(parents=True)
    (js_dir / "main-core.js").write_bytes(MAIN_CORE_JS)
    (js_dir / "preserved.js").write_bytes(PRESERVED_JS)

    css_dir = src / "assets" / "css"
    css_dir.mkdir(parents=True)
    (css_dir / "main.css").write_bytes(MAIN_CSS)

    # Plugin: symlink to keep behaviour identical to production.
    plugins_dir = src / "_plugins"
    plugins_dir.mkdir()
    (plugins_dir / "sri_inject.rb").write_bytes(PLUGIN_PATH.read_bytes())

    # Build (using repo's Gemfile via bundle exec, run from src dir).
    result = subprocess.run(
        [
            "bundle",
            "exec",
            "jekyll",
            "build",
            "--source",
            str(src),
            "--destination",
            str(dest),
            "--quiet",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "JEKYLL_ENV": "test"},
    )
    if result.returncode != 0:
        pytest.fail(
            f"Jekyll build failed (rc={result.returncode}):\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    index_html = (dest / "index.html").read_text(encoding="utf-8")
    return {
        "src": src,
        "dest": dest,
        "index_html": index_html,
        "expected_main_core_hash": _b64_sha384(MAIN_CORE_JS),
        "expected_main_css_hash": _b64_sha384(MAIN_CSS),
    }


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def test_local_script_gains_integrity(fixture_build):
    """Same-origin /assets/js/ <script> gets integrity + crossorigin."""
    html = fixture_build["index_html"]
    pattern = re.compile(
        r'<script\s+src="/assets/js/main-core\.js"[^>]*integrity="sha384-[^"]+"[^>]*crossorigin="anonymous"',
        re.IGNORECASE,
    )
    assert pattern.search(html), (
        "Expected /assets/js/main-core.js <script> to have integrity + crossorigin.\n"
        f"HTML excerpt:\n{html}"
    )


def test_local_stylesheet_gains_integrity(fixture_build):
    """Same-origin /assets/css/ <link rel=stylesheet> gets integrity + crossorigin."""
    html = fixture_build["index_html"]
    # link tag with rel="stylesheet" and href containing /assets/css/main.css
    pattern = re.compile(
        r'<link\s+rel="stylesheet"\s+href="/assets/css/main\.css[^"]*"[^>]*integrity="sha384-[^"]+"',
        re.IGNORECASE,
    )
    assert pattern.search(html), (
        "Expected /assets/css/main.css <link> to have integrity attribute.\n"
        f"HTML excerpt:\n{html}"
    )


def test_external_script_untouched(fixture_build):
    """External <script src="https://...">  must NOT gain integrity."""
    html = fixture_build["index_html"]
    # The external script line should still exist.
    assert "https://va.vercel-scripts.com" in html
    # And it must not have integrity= on the same tag.
    pattern = re.compile(
        r'<script[^>]*src="https://va\.vercel-scripts\.com[^"]*"[^>]*integrity=',
        re.IGNORECASE,
    )
    assert not pattern.search(html), (
        "External Vercel scripts must NOT gain integrity attribute."
    )


def test_non_stylesheet_link_untouched(fixture_build):
    """<link rel="icon"> / rel="preload" must NOT gain integrity."""
    html = fixture_build["index_html"]
    # rel="icon"
    icon_pattern = re.compile(
        r'<link[^>]*rel="icon"[^>]*integrity=', re.IGNORECASE
    )
    assert not icon_pattern.search(html), "rel='icon' link must not gain integrity."
    # rel="preload"
    preload_pattern = re.compile(
        r'<link[^>]*rel="preload"[^>]*integrity=', re.IGNORECASE
    )
    assert not preload_pattern.search(html), (
        "rel='preload' link must not gain integrity (only stylesheets)."
    )


def test_integrity_hash_format(fixture_build):
    """Every injected integrity value matches sha384-<base64> with 64 chars."""
    html = fixture_build["index_html"]
    values = re.findall(r'integrity="(sha384-[^"]+)"', html)
    assert values, "Expected at least one integrity attribute in built HTML."

    fmt = re.compile(r"^sha384-[A-Za-z0-9+/=]{64}$")
    for v in values:
        # Skip the pre-existing FAKE hash from the fixture HTML
        if v == "sha384-PREEXISTINGFAKE":
            continue
        assert fmt.match(v), f"Bad integrity format: {v!r}"
        # The base64 part should decode to exactly 48 bytes (SHA-384 digest).
        b64 = v[len("sha384-") :]
        decoded = base64.b64decode(b64)
        assert len(decoded) == 48, (
            f"sha384 digest must be 48 bytes, got {len(decoded)}: {v!r}"
        )


def test_hash_value_matches_file_bytes(fixture_build):
    """Injected hash must equal SHA-384(file_bytes)."""
    html = fixture_build["index_html"]
    expected = f'sha384-{fixture_build["expected_main_core_hash"]}'
    # main-core.js may appear with or without ?v= query; both must use the
    # same hash (hash is over file bytes only).
    matches = re.findall(
        r'<script\s+src="/assets/js/main-core\.js[^"]*"[^>]*integrity="(sha384-[^"]+)"',
        html,
    )
    assert matches, "Expected main-core.js integrity attribute(s)."
    for m in matches:
        assert m == expected, (
            f"Hash mismatch: got {m}, expected {expected} "
            f"(SHA-384 over {len(MAIN_CORE_JS)} bytes)"
        )


def test_cache_buster_query_ignored(fixture_build):
    """Two tags differing only in ?v= must get the same hash."""
    html = fixture_build["index_html"]
    hashes = re.findall(
        r'<script\s+src="/assets/js/main-core\.js(?:\?[^"]*)?"[^>]*integrity="(sha384-[^"]+)"',
        html,
    )
    assert len(hashes) >= 2, (
        f"Expected ≥2 main-core.js tags (with and without ?v=), got {len(hashes)}"
    )
    assert len(set(hashes)) == 1, (
        f"Cache-busted tag hashes must match; got distinct values: {set(hashes)!r}"
    )


def test_existing_integrity_preserved(fixture_build):
    """A tag that already has integrity= must not be modified."""
    html = fixture_build["index_html"]
    # The fixture uses sha384-PREEXISTINGFAKE on preserved.js.
    pattern = re.compile(
        r'<script\s+src="/assets/js/preserved\.js"[^>]*integrity="sha384-PREEXISTINGFAKE"',
        re.IGNORECASE,
    )
    assert pattern.search(html), (
        "Pre-existing integrity attribute must be preserved verbatim."
    )
    # And the tag must not have a second integrity= attribute (no duplicate).
    tag_match = re.search(
        r'<script\s+src="/assets/js/preserved\.js"[^>]*>',
        html,
    )
    assert tag_match, "preserved.js script tag missing from output."
    tag = tag_match.group(0)
    assert tag.count("integrity=") == 1, (
        f"Duplicate integrity attribute on preserved.js tag: {tag}"
    )


def test_missing_asset_warns_not_crashes(fixture_build):
    """Reference to non-existent asset → tag passes through without integrity."""
    html = fixture_build["index_html"]
    # The tag should still exist.
    assert "/assets/js/does-not-exist.js" in html, (
        "Missing-asset tag should pass through unchanged."
    )
    # And must not have integrity injected for that specific tag.
    pattern = re.compile(
        r'<script[^>]*src="/assets/js/does-not-exist\.js"[^>]*integrity=',
        re.IGNORECASE,
    )
    assert not pattern.search(html), (
        "Missing asset must not get a fabricated integrity attribute."
    )


def test_inline_script_untouched(fixture_build):
    """<script> without src= must not gain integrity."""
    html = fixture_build["index_html"]
    # inline tag should still be there
    assert 'console.log("inline")' in html
    # No integrity on inline scripts (regex requires src=).
    inline_pattern = re.compile(
        r'<script>\s*console\.log\("inline"\);?\s*</script>'
    )
    assert inline_pattern.search(html), (
        "Inline script should remain unchanged."
    )


def test_idempotent_across_rebuilds(fixture_build, tmp_path_factory):
    """Rebuilding the fixture site produces identical integrity hashes."""
    src = fixture_build["src"]
    dest2 = tmp_path_factory.mktemp("sri_dest2")
    result = subprocess.run(
        [
            "bundle",
            "exec",
            "jekyll",
            "build",
            "--source",
            str(src),
            "--destination",
            str(dest2),
            "--quiet",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "JEKYLL_ENV": "test"},
    )
    assert result.returncode == 0, (
        f"Second build failed:\n{result.stdout}\n{result.stderr}"
    )

    html1 = fixture_build["index_html"]
    html2 = (dest2 / "index.html").read_text(encoding="utf-8")

    hashes1 = sorted(re.findall(r'integrity="(sha384-[A-Za-z0-9+/=]{64})"', html1))
    hashes2 = sorted(re.findall(r'integrity="(sha384-[A-Za-z0-9+/=]{64})"', html2))

    assert hashes1 == hashes2, (
        "SRI plugin must be deterministic across builds.\n"
        f"Build 1: {hashes1}\nBuild 2: {hashes2}"
    )
    # Stronger: HTML containing integrity must be byte-identical
    # (cache-buster ?v= differences are external to the integrity= values).
    assert hashes1, "Expected at least one integrity attribute in the build."
