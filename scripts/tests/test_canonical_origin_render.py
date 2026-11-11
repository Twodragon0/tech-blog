"""Render canonical SEO and backup RSS using production and Pages origins."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree

import pytest

ROOT = Path(__file__).resolve().parents[2]
PRODUCTION = "https://tech.2twodragon.com"
BACKUP = "https://twodragon0.github.io"
BASEURL = "/tech-blog"
POST_PATH = "/posts/2026/11/10/canonical-origin-fixture/"


@pytest.fixture(scope="module")
def rendered_sites(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    bundle = shutil.which("bundle")
    if not bundle:
        pytest.skip("Bundler not on PATH; required for Jekyll render")
    probe = subprocess.run(
        [bundle, "exec", "jekyll", "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if probe.returncode:
        pytest.skip(
            "Jekyll gems not available in this environment; render runs in the Jekyll build job"
        )

    temp = tmp_path_factory.mktemp("canonical-origin")
    source = temp / "source"
    (source / "_includes").mkdir(parents=True)
    (source / "_layouts").mkdir()
    (source / "_plugins").mkdir()
    (source / "_posts").mkdir()
    (source / "assets/images").mkdir(parents=True)
    shutil.copy(ROOT / "feed.xml", source / "feed.xml")
    for name in (
        "head.html",
        "font-face.html",
        "sentry.html",
        "performance-monitor.html",
    ):
        shutil.copy(ROOT / "_includes" / name, source / "_includes" / name)
    shutil.copy(
        ROOT / "_plugins/image_content_hash.rb",
        source / "_plugins/image_content_hash.rb",
    )
    (source / "_layouts/post.html").write_text(
        "<!doctype html>{% include head.html %}<body>{{ content }}</body>",
        encoding="utf-8",
    )
    (source / "_posts/2026-11-10-canonical-origin-fixture.md").write_text(
        "---\nlayout: post\ntitle: Canonical Origin Fixture\n"
        "date: 2026-11-10 09:00:00 +0900\ncategory: devops\n"
        "image: /assets/images/share-card.png\nexcerpt: Fixture excerpt\n---\nFixture body.\n",
        encoding="utf-8",
    )
    (source / "assets/images/share-card.png").write_bytes(b"fixture image bytes")

    backup_config = temp / "jekyll-pages.yml"
    backup_config.write_text(json.dumps({"url": BACKUP}), encoding="utf-8")
    fixture_config = temp / "jekyll-fixture.yml"
    fixture_config.write_text(json.dumps({"plugins": []}), encoding="utf-8")
    destinations: dict[str, Path] = {}
    configs = {
        "production": (f"{ROOT / '_config.yml'},{fixture_config}", ""),
        "backup": (f"{ROOT / '_config.yml'},{backup_config},{fixture_config}", BASEURL),
    }
    for name, (config, baseurl) in configs.items():
        destination = temp / name
        result = subprocess.run(
            [
                bundle,
                "exec",
                "jekyll",
                "build",
                "--source",
                str(source),
                "--destination",
                str(destination),
                "--config",
                config,
                "--baseurl",
                baseurl,
                "--quiet",
            ],
            cwd=ROOT,
            env=os.environ.copy(),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        destinations[name] = destination
    return destinations


@pytest.mark.parametrize("site_name", ["production", "backup"])
def test_rendered_canonical_and_share_metadata_use_production_origin(
    rendered_sites: dict[str, Path], site_name: str
) -> None:
    html = (
        rendered_sites[site_name] / POST_PATH.lstrip("/") / "index.html"
    ).read_text()
    expected_post = f"{PRODUCTION}{POST_PATH}"
    expected_image = f"{PRODUCTION}/assets/images/share-card.png"
    assert f'<link rel="canonical" href="{expected_post}">' in html
    assert f'<meta property="og:url" content="{expected_post}">' in html
    assert f'<meta name="twitter:url" content="{expected_post}">' in html
    assert f'<meta property="og:image" content="{expected_image}?v=' in html
    assert f'<meta name="twitter:image" content="{expected_image}?v=' in html
    assert '<meta name="twitter:domain" content="tech.2twodragon.com">' in html
    structured_data = [
        json.loads(block)
        for block in re.findall(
            r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
            html,
            flags=re.DOTALL,
        )
    ]
    article = next(item for item in structured_data if item["@type"] == "BlogPosting")
    assert article["url"] == expected_post
    assert article["mainEntityOfPage"]["@id"] == expected_post
    assert article["image"]["url"].startswith(f"{expected_image}?v=")


def test_backup_render_keeps_backup_feed_and_noindex(
    rendered_sites: dict[str, Path],
) -> None:
    html = (rendered_sites["backup"] / POST_PATH.lstrip("/") / "index.html").read_text()
    assert '<meta name="robots" content="noindex, follow">' in html
    assert f'href="{BACKUP}{BASEURL}/feed.xml"' in html

    feed = ElementTree.parse(rendered_sites["backup"] / "feed.xml").getroot()
    namespaces = {"atom": "http://www.w3.org/2005/Atom"}
    channel = feed.find("channel")
    assert channel is not None
    self_link = channel.find("atom:link[@rel='self']", namespaces)
    assert self_link is not None
    assert self_link.attrib["href"] == f"{BACKUP}{BASEURL}/feed.xml"
    assert channel.findtext("link") == f"{BACKUP}{BASEURL}/"
    item_link = channel.find("item/link")
    assert item_link is not None
    assert item_link.text == f"{BACKUP}{BASEURL}{POST_PATH}"
    assert channel.findtext("item/guid") == f"{BACKUP}{BASEURL}{POST_PATH}"
