"""The RSS feed must stay small and readable outside the site.

On 2026-11-21 /feed.xml was 2.2 MB: 50 items, each carrying the full post body
(digests run about 40 KB each). Many readers cap the size they fetch. The same
bodies held 135 root-relative links (href="/posts/..."), which a feed reader
resolves against its own host. This renders the real feed.xml template with
Jekyll and checks the item limit and link rewriting.
"""

import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = "https://example.test"
CONTENT = "{http://purl.org/rss/1.0/modules/content/}encoded"


@pytest.fixture(scope="module")
def rendered_feed(tmp_path_factory):
    if not shutil.which("bundle"):
        pytest.skip("Bundler not on PATH; required for Jekyll render")
    tmp = tmp_path_factory.mktemp("feed")
    source = tmp / "source"
    (source / "_posts").mkdir(parents=True)
    shutil.copy(ROOT / "feed.xml", source / "feed.xml")
    (source / "_config.yml").write_text(f'url: "{ORIGIN}"\nbaseurl: ""\ntitle: t\n')
    for day in range(1, 23):
        (source / "_posts" / f"2026-01-{day:02d}-post-{day}.md").write_text(
            "---\ntitle: p\n---\n"
            '<a href="/posts/other/">rel</a> <img src="/assets/a.png">'
            ' <img src="//cdn.test/b.png"> <a href="https://x.test/">abs</a>\n'
        )
    result = subprocess.run(
        [
            "bundle",
            "exec",
            "jekyll",
            "build",
            "--source",
            str(source),
            "--destination",
            str(tmp / "out"),
            "--quiet",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode and "Could not find" in result.stderr:
        pytest.skip(
            "Jekyll gems not available in this environment; render runs in the Jekyll build job"
        )
    assert result.returncode == 0, result.stdout + result.stderr
    return ET.parse(tmp / "out" / "feed.xml").getroot().find("channel")


def test_feed_carries_the_latest_20_items(rendered_feed):
    assert len(rendered_feed.findall("item")) == 20


def test_root_relative_links_in_bodies_become_absolute(rendered_feed):
    body = rendered_feed.find("item").findtext(CONTENT)
    assert f'href="{ORIGIN}/posts/other/"' in body
    assert f'src="{ORIGIN}/assets/a.png"' in body
    assert 'src="//cdn.test/b.png"' in body
    assert 'href="https://x.test/"' in body
    assert 'href="/' not in body and 'src="/a' not in body
