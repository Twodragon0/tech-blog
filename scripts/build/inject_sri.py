#!/usr/bin/env python3
"""Inject SRI integrity hashes into <script> and <link> tags in built HTML.

Runs as a post-build step (called from build.sh AFTER terser minification),
so the hashes are computed against the FINAL bytes that the browser will
receive — which is critical because terser changes file bytes after Jekyll
build, breaking any SRI computed by a Jekyll `:post_write` plugin.

Walks `_site/**/*.html`. For each tag matching one of:
    <script src="/assets/{js,css}/foo.js[?v=...]" ...>
    <link  rel="stylesheet" href="/assets/{js,css}/foo.css[?v=...]" ...>
that does NOT already carry an integrity= attribute, and whose src/href
points to a same-origin local file, the script:
  1. Strips ?query and #fragment for filesystem lookup.
  2. Strips a leading `site.baseurl` if the path starts with it
     (handles GH Pages backup `--baseurl /tech-blog`).
  3. Computes SHA-384 of the file at `_site/{path}`.
  4. Rewrites the tag to add `integrity="sha384-..." crossorigin="anonymous"`.
Missing or unreadable assets log a warning but do not abort the build —
mirrors the degrade-don't-crash policy of `_plugins/markdown_image_lazy.rb`.

Exit codes:
  0  Always (warnings only; never fails the build).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Match <script ... src="..."> and <link ... rel="stylesheet" ... href="..."> tags.
# Capture the entire tag so we can rewrite while preserving attribute order.
TAG_RE = re.compile(
    r'<(?P<elem>script|link)(?P<attrs>\s[^>]*?)\s*/?>',
    re.IGNORECASE,
)


def compute_sri(path: Path, cache: dict[tuple[str, int, float], str]) -> str | None:
    """Return `sha384-<base64>` for the file, cached by (path, size, mtime)."""
    try:
        stat = path.stat()
    except OSError:
        return None
    key = (str(path), stat.st_size, stat.st_mtime)
    if key in cache:
        return cache[key]
    digest = hashlib.sha384(path.read_bytes()).digest()
    sri = "sha384-" + base64.b64encode(digest).decode("ascii")
    cache[key] = sri
    return sri


def extract_attr(attrs: str, name: str) -> str | None:
    """Pull a single attribute value out of a tag's attribute blob."""
    m = re.search(
        rf'\b{name}\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))',
        attrs,
        re.IGNORECASE,
    )
    if not m:
        return None
    return m.group(1) or m.group(2) or m.group(3)


def rewrite_tag(
    match: re.Match[str],
    site_dest: Path,
    baseurl: str,
    cache: dict,
    stats: dict,
) -> str:
    elem = match.group("elem").lower()
    attrs = match.group("attrs")
    full_tag = match.group(0)

    # Skip if already has integrity (idempotent).
    if re.search(r'\bintegrity\s*=', attrs, re.IGNORECASE):
        return full_tag

    # For <link>: only rel="stylesheet" gets SRI.
    if elem == "link":
        rel = (extract_attr(attrs, "rel") or "").lower()
        if "stylesheet" not in rel.split():
            return full_tag
        url = extract_attr(attrs, "href")
    else:  # script
        url = extract_attr(attrs, "src")

    if not url:
        return full_tag

    # Skip external + protocol-relative URLs.
    if url.startswith(("http://", "https://", "//", "data:", "blob:")):
        return full_tag

    # Strip ?query / #fragment.
    clean = url.split("?", 1)[0].split("#", 1)[0]
    # Strip leading baseurl if present.
    if baseurl and clean.startswith(baseurl + "/"):
        clean = clean[len(baseurl):]
    # Resolve to filesystem path under _site/.
    rel_path = clean.lstrip("/")
    if not rel_path.startswith("assets/"):
        return full_tag

    abs_path = site_dest / rel_path
    sri = compute_sri(abs_path, cache)
    if sri is None:
        stats["missing"].append(rel_path)
        return full_tag

    # Inject integrity + crossorigin. Insert after the elem name.
    new_attrs = (
        f'{attrs.rstrip()} integrity="{sri}" crossorigin="anonymous"'
    )
    stats["injected"] += 1
    return f'<{match.group("elem")}{new_attrs}>'


def process_file(
    html_path: Path,
    site_dest: Path,
    baseurl: str,
    cache: dict,
    stats: dict,
) -> bool:
    """Rewrite one HTML file in place. Returns True if changed."""
    try:
        text = html_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    new_text = TAG_RE.sub(
        lambda m: rewrite_tag(m, site_dest, baseurl, cache, stats),
        text,
    )
    if new_text == text:
        return False
    html_path.write_text(new_text, encoding="utf-8")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inject SRI hashes into built HTML (post-minify build step)."
    )
    parser.add_argument(
        "--site",
        default=str(REPO_ROOT / "_site"),
        help="Path to the built site root (default: ./_site)",
    )
    parser.add_argument(
        "--baseurl",
        default="",
        help="Jekyll site.baseurl to strip from URLs (e.g. /tech-blog for GH Pages backup)",
    )
    args = parser.parse_args(argv)

    site_dest = Path(args.site)
    if not site_dest.is_dir():
        print(f"SRI: no _site at {site_dest}, skipping", file=sys.stderr)
        return 0

    cache: dict = {}
    stats = {"injected": 0, "missing": []}
    html_files = list(site_dest.rglob("*.html"))
    changed = 0
    for p in html_files:
        if process_file(p, site_dest, args.baseurl, cache, stats):
            changed += 1

    print(
        f"SRI: scanned {len(html_files)} HTML files, "
        f"rewrote {changed}, injected {stats['injected']} integrity attributes "
        f"({len(cache)} unique asset hashes)"
    )
    if stats["missing"]:
        unique_missing = sorted(set(stats["missing"]))
        print(
            f"SRI: {len(unique_missing)} asset paths could not be resolved "
            f"(skipped, no integrity injected). First 5:",
            file=sys.stderr,
        )
        for m in unique_missing[:5]:
            print(f"  - {m}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
