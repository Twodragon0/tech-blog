#!/usr/bin/env python3
"""Tests for scripts/dev/resolve_lighthouse_urls.py.

The property that matters most here is the both-sides intersection. The perf
gate serves each build with ``serve --single``, which answers an unknown path
with the homepage at HTTP 200 and no redirect, so a URL that exists on head but
not on base would be compared against the homepage and produce a meaningless
delta. Several tests below pin that behaviour specifically.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "dev"))

from resolve_lighthouse_urls import post_slug, resolve, urls_for_slug  # noqa: E402

POST_HTML = "<!doctype html><html><head><title>x</title></head><body>post</body></html>"
REDIRECT_HTML = (
    '<!doctype html><html><head><meta http-equiv="refresh" '
    'content="0; url=/posts/2026/05/21/Foo/"></head></html>'
)


def _make_post(site_dir: Path, url_path: str, html: str = POST_HTML) -> None:
    target = site_dir / url_path.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")


class TestPostSlug:
    def test_strips_date_prefix_and_extension(self):
        assert (
            post_slug("_posts/2026-04-29-Tech_Security_Weekly.md")
            == "Tech_Security_Weekly"
        )

    def test_accepts_markdown_extension(self):
        assert post_slug("_posts/2026-01-02-Foo.markdown") == "Foo"

    @pytest.mark.parametrize(
        "path",
        [
            "assets/images/2026-04-29-Foo.svg",
            "_drafts/2026-04-29-Foo.md",
            "_posts/no-date-here.md",
            "_posts/2026-04-29-Foo.txt",
            "_posts/2026-04-29-.md",
            "scripts/dev/x.py",
            "",
        ],
    )
    def test_rejects_non_post_paths(self, path):
        assert post_slug(path) is None


class TestUrlsForSlug:
    def test_finds_built_post(self, tmp_path):
        _make_post(tmp_path, "/posts/2026/04/29/Foo/")
        assert urls_for_slug("Foo", tmp_path) == {"/posts/2026/04/29/Foo/"}

    def test_ignores_redirect_stubs(self, tmp_path):
        """A KST-midnight post ships a redirect_from stub at the filename date.

        Both directories match the glob. The stub is the *later* date (UTC
        pushes the canonical page back a day), so the newest-first tie-break
        would pick it — only the meta-refresh sniff prevents the gate from
        measuring a 769-byte redirect page instead of the post. That pairing is
        real: 12 slugs in the current build have both a canonical page and a
        3-level redirect stub.
        """
        _make_post(tmp_path, "/posts/2026/05/20/Foo/")
        _make_post(tmp_path, "/posts/2026/05/21/Foo/", REDIRECT_HTML)
        assert urls_for_slug("Foo", tmp_path) == {"/posts/2026/05/20/Foo/"}
        assert resolve(["_posts/2026-05-21-Foo.md"], [tmp_path]) == [
            "/",
            "/posts/2026/05/20/Foo/",
        ]

    def test_unknown_slug_yields_nothing(self, tmp_path):
        _make_post(tmp_path, "/posts/2026/04/29/Foo/")
        assert urls_for_slug("Bar", tmp_path) == set()

    def test_url_date_may_differ_from_filename_date(self, tmp_path):
        """timezone: UTC shifts KST 00:00-08:59 posts back a day.

        The resolver must read the date off the build, never recompute it from
        the filename.
        """
        _make_post(tmp_path, "/posts/2026/05/20/Foo/")
        resolved = resolve(["_posts/2026-05-21-Foo.md"], [tmp_path])
        assert resolved == ["/", "/posts/2026/05/20/Foo/"]


class TestResolve:
    def test_homepage_always_first(self, tmp_path):
        assert resolve([], [tmp_path])[0] == "/"

    def test_measures_the_edited_post(self, tmp_path):
        head, base = tmp_path / "head", tmp_path / "base"
        for site in (head, base):
            _make_post(site, "/posts/2026/04/29/Edited/")
            _make_post(site, "/posts/2026/03/01/Untouched/")
        assert resolve(["_posts/2026-04-29-Edited.md"], [head, base]) == [
            "/",
            "/posts/2026/04/29/Edited/",
        ]

    def test_new_post_absent_from_base_is_dropped(self, tmp_path):
        """The --single hazard: measuring it would compare post vs homepage."""
        head, base = tmp_path / "head", tmp_path / "base"
        _make_post(head, "/posts/2026/08/08/BrandNew/")
        base.mkdir(parents=True, exist_ok=True)
        assert resolve(["_posts/2026-08-08-BrandNew.md"], [head, base]) == ["/"]

    def test_deleted_post_absent_from_head_is_dropped(self, tmp_path):
        head, base = tmp_path / "head", tmp_path / "base"
        head.mkdir(parents=True, exist_ok=True)
        _make_post(base, "/posts/2026/04/29/Removed/")
        assert resolve(["_posts/2026-04-29-Removed.md"], [head, base]) == ["/"]

    def test_cap_bounds_run_time(self, tmp_path):
        """A 40-post corpus PR must not turn into 41 Lighthouse URL sweeps."""
        head, base = tmp_path / "head", tmp_path / "base"
        changed = []
        for day in range(1, 15):
            url = f"/posts/2026/04/{day:02d}/Post{day:02d}/"
            _make_post(head, url)
            _make_post(base, url)
            changed.append(f"_posts/2026-04-{day:02d}-Post{day:02d}.md")
        resolved = resolve(changed, [head, base], max_post_urls=1)
        assert len(resolved) == 2, resolved
        # Newest first, so a corpus PR measures the most recent page it touched.
        assert resolved[1] == "/posts/2026/04/14/Post14/"

    def test_cap_is_configurable(self, tmp_path):
        head, base = tmp_path / "head", tmp_path / "base"
        for url in ("/posts/2026/04/01/A/", "/posts/2026/04/02/B/"):
            _make_post(head, url)
            _make_post(base, url)
        resolved = resolve(
            ["_posts/2026-04-01-A.md", "_posts/2026-04-02-B.md"],
            [head, base],
            max_post_urls=2,
        )
        assert resolved == ["/", "/posts/2026/04/02/B/", "/posts/2026/04/01/A/"]

    def test_selection_is_deterministic(self, tmp_path):
        """Same inputs in a different order must pick the same URL.

        Otherwise a re-run of the same PR measures a different page and the
        comparison against the previous run's comment is meaningless.
        """
        head, base = tmp_path / "head", tmp_path / "base"
        for url in ("/posts/2026/04/01/A/", "/posts/2026/04/02/B/"):
            _make_post(head, url)
            _make_post(base, url)
        forward = resolve(
            ["_posts/2026-04-01-A.md", "_posts/2026-04-02-B.md"], [head, base]
        )
        reverse = resolve(
            ["_posts/2026-04-02-B.md", "_posts/2026-04-01-A.md"], [head, base]
        )
        assert forward == reverse

    def test_falls_back_to_default_when_no_post_touched(self, tmp_path):
        """An assets/** or _includes/** PR keeps the representative post."""
        head, base = tmp_path / "head", tmp_path / "base"
        for site in (head, base):
            _make_post(site, "/posts/2026/04/29/Representative/")
        assert resolve(
            ["_includes/head.html"],
            [head, base],
            default_post_url="/posts/2026/04/29/Representative/",
        ) == ["/", "/posts/2026/04/29/Representative/"]

    def test_default_dropped_when_it_stops_existing(self, tmp_path):
        """The hard-coded post can be renamed or unpublished at any time.

        Measuring it then would compare homepage-served-as-post on both sides:
        a permanently green, permanently vacuous row.
        """
        head, base = tmp_path / "head", tmp_path / "base"
        head.mkdir(parents=True, exist_ok=True)
        base.mkdir(parents=True, exist_ok=True)
        assert resolve(
            ["_includes/head.html"],
            [head, base],
            default_post_url="/posts/2026/04/29/Gone/",
        ) == ["/"]

    def test_no_site_dirs_uses_default_only(self, tmp_path):
        """GH Pages fallback: nothing local to inspect, so do not guess."""
        assert resolve(
            ["_posts/2026-04-29-Edited.md"],
            [],
            default_post_url="/posts/2026/04/29/Representative/",
        ) == ["/", "/posts/2026/04/29/Representative/"]

    def test_non_post_changes_do_not_leak_urls(self, tmp_path):
        head, base = tmp_path / "head", tmp_path / "base"
        for site in (head, base):
            _make_post(site, "/posts/2026/04/29/Foo/")
        assert resolve(["assets/js/main.js", "README.md"], [head, base]) == ["/"]
