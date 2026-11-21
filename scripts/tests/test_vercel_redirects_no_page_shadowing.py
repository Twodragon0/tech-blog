"""Guard: no vercel.json redirect may shadow a page this Jekyll site builds.

Vercel applies ``redirects`` before it serves a file, so a redirect whose
``source`` is the URL of a built page makes that page unreachable. That is how
the blog's own /privacy-policy/ (listed in sitemap.xml, and required for
AdSense) came to 301 to the retired WordPress policy on legacy.2twodragon.com:
the WordPress archive map (docs/seo/wordpress-archive-redirects.csv) carried an
unscoped ``/privacy-policy/`` rule, and both sites use that slug.

The page list is derived from front matter rather than kept by hand: every
published file with front matter contributes its ``permalink:``, and an HTML or
Markdown page without one contributes the pretty URL Jekyll gives it (the site
permalink ends in ``/``). Collection documents with ``output: true`` count too.
``CORE_PAGES`` only checks that the derivation still finds the pages it must,
so a walk that silently finds nothing cannot pass.
"""

from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path

import frontmatter
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
VERCEL_CONFIG = REPO_ROOT / "vercel.json"

CORE_PAGES = {
    "/privacy-policy/",
    "/about/",
    "/archive/",
    "/categories/",
    "/tags/",
    "/support/",
    "/discussion/",
    "/certifications/",
}
# Jekyll's EntryFilter skips names with these leading characters or a trailing "~".
SKIPPED_LEADING = (".", "_", "#", "~")
HTML_LIKE = {".html", ".htm", ".md", ".markdown"}


def _skipped(name: str) -> bool:
    return name.startswith(SKIPPED_LEADING) or name.endswith("~")


def _excluded(rel: str, is_dir: bool, patterns: list[str]) -> bool:
    """Jekyll's ``exclude:`` test: fnmatch, path prefix, or ``dir/`` equality."""
    return any(
        fnmatch.fnmatchcase(rel, pattern)
        or rel.startswith(pattern)
        or (is_dir and f"{rel}/" == pattern)
        for pattern in patterns
    )


def _has_front_matter(path: Path) -> bool:
    with path.open("rb") as fh:
        return fh.readline().rstrip() == b"---"


def _page_url(path: Path, rel_dir: str) -> str | None:
    permalink = frontmatter.load(path).metadata.get("permalink")
    if permalink:
        return str(permalink)
    if path.suffix not in HTML_LIKE:
        return None
    prefix = f"/{rel_dir}/" if rel_dir else "/"
    return prefix if path.stem == "index" else f"{prefix}{path.stem}/"


def built_page_urls() -> set[str]:
    config = yaml.safe_load((REPO_ROOT / "_config.yml").read_text(encoding="utf-8"))
    exclude = config.get("exclude") or []
    urls: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        rel_dir = Path(dirpath).relative_to(REPO_ROOT).as_posix()
        rel_dir = "" if rel_dir == "." else rel_dir
        prefix = f"{rel_dir}/" if rel_dir else ""
        dirnames[:] = [
            d
            for d in dirnames
            if not _skipped(d) and not _excluded(prefix + d, True, exclude)
        ]
        for name in filenames:
            path = Path(dirpath) / name
            if _skipped(name) or _excluded(prefix + name, False, exclude):
                continue
            if _has_front_matter(path):
                url = _page_url(path, rel_dir)
                if url:
                    urls.add(url)

    for label, opts in (config.get("collections") or {}).items():
        if not (opts or {}).get("output"):
            continue
        template = opts.get("permalink", f"/{label}/:name/")
        for path in sorted((REPO_ROOT / f"_{label}").rglob("*")):
            if path.is_file() and _has_front_matter(path):
                meta = frontmatter.load(path).metadata
                urls.add(
                    str(meta.get("permalink") or template.replace(":name", path.stem))
                )
    return urls


def _normalize(url: str) -> str:
    return url.rstrip("/") or "/"


def test_derivation_finds_core_pages():
    missing = sorted(CORE_PAGES - built_page_urls())
    assert not missing, f"page derivation no longer finds: {missing}"


def test_no_redirect_shadows_a_built_page():
    pages = {_normalize(url) for url in built_page_urls()}
    redirects = json.loads(VERCEL_CONFIG.read_text(encoding="utf-8"))["redirects"]
    shadowing = [
        (rule["source"], rule["destination"])
        for rule in redirects
        if _normalize(rule["source"]) in pages
    ]
    assert not shadowing, (
        "these vercel.json redirects make a page the blog builds unreachable; "
        f"drop the rule or scope it with `has`: {shadowing}"
    )
