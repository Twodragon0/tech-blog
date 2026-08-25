#!/usr/bin/env python3
"""Resolve which URLs the Lighthouse perf gate should measure for a PR.

Why this exists
---------------
``.github/workflows/lighthouse-ci.yml`` used to measure a hard-coded pair:
the homepage and one representative post from 2026-04-29. That was fine while
the gate only fired on ``_includes/**`` / ``assets/**`` changes, because those
change every page equally. Once ``_posts/**`` triggers the gate, a fixed URL is
worse than useless: the PR edits post *X* and the gate measures post *Y*, which
is byte-identical on both sides, so it always reports +0 ms and blocks nothing.

So the URL list is derived from the PR diff instead: homepage + the post(s) the
PR actually touched.

The both-sides rule (this is a correctness requirement, not an optimisation)
---------------------------------------------------------------------------
If a URL exists on head but not on base (a newly added post), there is nothing
like-for-like to compare: base answers with a 404 page, and the delta between a
real post and an error page is garbage in whichever direction the two happen to
differ.

Hence: a post URL is measured only when it exists in **every** site directory
passed via ``--site-dir``. New posts drop out and the gate falls back to
comparing the homepage, which is honest.

This check is necessary but was never sufficient, and believing otherwise cost
the gate months of vacuous runs. The workflow used to serve each build with
``npx serve … --single`` on the theory that ``--single`` only substitutes the
homepage for *unknown* paths — which this rule would then cover. That theory is
wrong: ``--single`` rewrites every extensionless path to ``/index.html``
*before* the filesystem lookup, so it answered an **existing** post page with
the homepage at HTTP 200 as well. Every post URL this resolver correctly
admitted was still measured as the homepage. ``--single`` is gone and the
workflow now probes page identity over HTTP before measuring; see
``.github/workflows/lighthouse-ci.yml`` and PR #606.

Slug rule
---------
``_config.yml`` sets ``permalink: /posts/:year/:month/:day/:title/`` and Jekyll's
``:title`` for these posts is the filename with the ``YYYY-MM-DD-`` prefix and
the extension stripped, verbatim (underscores and case preserved). The date part
is deliberately *not* recomputed here: ``timezone: UTC`` means a post authored at
KST 00:00-08:59 lands on the previous UTC day, so the filename date and the URL
date can differ (see CLAUDE.md "Date / Timezone Rule"). Globbing the built site
for ``posts/*/*/*/<slug>/index.html`` reads the answer off the actual build
instead of re-deriving it, so the drift cannot bite.

``redirect_from`` stubs match that same glob, so candidates whose HTML carries a
``http-equiv="refresh"`` are discarded — they are 1 KB meta-refresh pages and
measuring one would report the redirect, not the post.

Usage::

    python3 scripts/dev/resolve_lighthouse_urls.py \\
        --changed-files changed.txt \\
        --site-dir _site_head --site-dir _site_base \\
        --default-post-url /posts/2026/04/29/Some_Post/ \\
        --max-post-urls 1 --output lh-urls.txt

Prints one URL path per line (``/`` first). Pure stdlib.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HOMEPAGE = "/"

# Enough of the document to cover <head>; redirect stubs put the refresh there.
_SNIFF_BYTES = 4096
_REFRESH_MARKERS = ('http-equiv="refresh"', "http-equiv='refresh'")

_POST_SUFFIXES = (".md", ".markdown")


def post_slug(changed_path: str) -> str | None:
    """``_posts/2026-04-29-Foo_Bar.md`` -> ``Foo_Bar``.

    Returns ``None`` for anything that is not a dated post source file.
    """
    path = Path(changed_path.strip())
    if not path.parts or path.parts[0] != "_posts":
        return None
    if path.suffix.lower() not in _POST_SUFFIXES:
        return None
    stem = path.stem
    # YYYY-MM-DD- prefix: 11 characters.
    if len(stem) <= 11 or stem[4] != "-" or stem[7] != "-" or stem[10] != "-":
        return None
    if not (stem[:4].isdigit() and stem[5:7].isdigit() and stem[8:10].isdigit()):
        return None
    slug = stem[11:]
    return slug or None


def _is_redirect_stub(index_html: Path) -> bool:
    try:
        head = index_html.read_bytes()[:_SNIFF_BYTES].decode("utf-8", "replace").lower()
    except OSError:
        return True
    return any(marker in head for marker in _REFRESH_MARKERS)


def urls_for_slug(slug: str, site_dir: Path) -> set[str]:
    """Every canonical ``/posts/YYYY/MM/DD/<slug>/`` URL built for ``slug``."""
    found: set[str] = set()
    for index_html in site_dir.glob(f"posts/*/*/*/{slug}/index.html"):
        if _is_redirect_stub(index_html):
            continue
        rel = index_html.parent.relative_to(site_dir).as_posix()
        found.add(f"/{rel}/")
    return found


def resolve(
    changed_files: list[str],
    site_dirs: list[Path],
    default_post_url: str | None = None,
    max_post_urls: int = 1,
) -> list[str]:
    """Homepage + up to ``max_post_urls`` post URLs present in every site dir.

    With no ``site_dirs`` (the GH Pages fallback path, where there is no local
    build to inspect) existence cannot be checked, so only the homepage and the
    default post URL are returned — guessing a URL there would hit the
    ``--single`` hazard described in the module docstring.
    """
    urls = [HOMEPAGE]

    if not site_dirs:
        if default_post_url:
            urls.append(default_post_url)
        return urls

    slugs = sorted({s for s in (post_slug(c) for c in changed_files) if s})

    candidates: set[str] = set()
    for slug in slugs:
        per_dir = [urls_for_slug(slug, site_dir) for site_dir in site_dirs]
        # Intersection: measurable only where every build serves it.
        common = set.intersection(*per_dir) if per_dir else set()
        candidates |= common

    if candidates:
        # Deterministic and stable across re-runs: newest URL date first (the
        # path sorts lexicographically by /YYYY/MM/DD/), then by slug.
        urls.extend(sorted(candidates, reverse=True)[:max_post_urls])
        return urls

    if default_post_url and all(
        (site_dir / default_post_url.strip("/") / "index.html").is_file()
        for site_dir in site_dirs
    ):
        urls.append(default_post_url)
    return urls


def _read_changed_files(path: Path | None) -> list[str]:
    if path is None:
        return []
    if str(path) == "-":
        return [ln for ln in sys.stdin.read().splitlines() if ln.strip()]
    if not path.is_file():
        return []
    return [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--changed-files",
        type=Path,
        default=None,
        help="File with one changed repo path per line ('-' for stdin)",
    )
    parser.add_argument(
        "--site-dir",
        type=Path,
        action="append",
        default=[],
        dest="site_dirs",
        help="Built site directory; a post URL must exist in every one (repeatable)",
    )
    parser.add_argument(
        "--default-post-url",
        default=None,
        help="Post URL to measure when the PR touched no resolvable post",
    )
    parser.add_argument(
        "--max-post-urls",
        type=int,
        default=1,
        help="Cap on post URLs measured, so run time stays flat (default: 1)",
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="Write the list here too"
    )
    args = parser.parse_args()

    urls = resolve(
        _read_changed_files(args.changed_files),
        args.site_dirs,
        args.default_post_url,
        args.max_post_urls,
    )
    text = "\n".join(urls) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
