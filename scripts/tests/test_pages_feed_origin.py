"""Pages RSS must use its deployment origin and preserve production defaults."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_pages_provides_origin_override_and_build_supports_config():
    workflow = yaml.safe_load((ROOT / ".github/workflows/deploy-pages.yml").read_text())
    steps = workflow["jobs"]["build"]["steps"]
    setup = next(s for s in steps if s.get("name") == "Write Pages origin override")
    build = next(s for s in steps if "via build.sh" in s.get("name", ""))
    assert setup["env"]["PAGES_ORIGIN"] == "${{ steps.pages.outputs.origin }}"
    assert (
        build["env"]["JEKYLL_CONFIG"]
        == "_config.yml,${{ runner.temp }}/jekyll-pages.yml"
    )
    assert '--config "${JEKYLL_CONFIG:-_config.yml}"' in (ROOT / "build.sh").read_text()


@pytest.fixture(scope="module")
def jekyll_available():
    # News-only runners install Python dependencies, not Ruby/Jekyll. The
    # Jekyll build job supplies Bundler and executes this rendered regression.
    if not shutil.which("bundle"):
        pytest.skip("Bundler not on PATH; required for Jekyll render")
    check = subprocess.run(
        ["bundle", "exec", "jekyll", "--version"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if check.returncode:
        pytest.skip(
            "Jekyll gems not available in this environment; render runs in the Jekyll build job"
        )


@pytest.mark.parametrize(
    "origin,baseurl",
    [
        ("http://twodragon0.github.io", "/tech-blog"),
        ("https://twodragon0.github.io", "/tech-blog"),
        ("https://tech.2twodragon.com", ""),
    ],
)
def test_rendered_feed_uses_selected_deployment(
    tmp_path, origin, baseurl, jekyll_available
):
    source = tmp_path / "source"
    source.mkdir()
    (source / "feed.xml").write_text(
        "---\nlayout: null\n---\n<link>{{ site.url }}{{ site.baseurl }}/posts/item/</link>\n"
    )
    base = tmp_path / "base.yml"
    base.write_text(json.dumps({"url": "https://tech.2twodragon.com", "baseurl": ""}))
    prepared = run_pages_config(tmp_path, origin)
    assert prepared.returncode == 0, prepared.stderr
    override = tmp_path / "jekyll-pages.yml"
    result = subprocess.run(
        [
            "bundle",
            "exec",
            "jekyll",
            "build",
            "--source",
            str(source),
            "--destination",
            str(tmp_path / "out"),
            "--config",
            f"{base},{override}",
            "--baseurl",
            baseurl,
            "--quiet",
        ],
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    expected_origin = origin.replace("http:", "https:", 1)
    assert (
        f"{expected_origin}{baseurl}/posts/item/"
        in (tmp_path / "out/feed.xml").read_text()
    )


@pytest.fixture(scope="module")
def ruby_available():
    if not shutil.which("ruby"):
        pytest.skip("Ruby not on PATH; required for Pages configuration")


def run_pages_config(tmp_path, origin):
    workflow = yaml.safe_load((ROOT / ".github/workflows/deploy-pages.yml").read_text())
    setup = next(
        s
        for s in workflow["jobs"]["build"]["steps"]
        if s.get("name") == "Write Pages origin override"
    )
    env = os.environ.copy()
    env.update(PAGES_ORIGIN=origin, RUNNER_TEMP=str(tmp_path))
    return subprocess.run(
        ["bash", "-e", "-c", setup["run"]],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize(
    "origin",
    [
        "http://twodragon0.github.io",
        "https://twodragon0.github.io",
        "http://twodragon0.github.io/",
    ],
)
def test_actual_pages_step_always_writes_https(tmp_path, origin, ruby_available):
    result = run_pages_config(tmp_path, origin)
    assert result.returncode == 0, result.stderr
    assert json.loads((tmp_path / "jekyll-pages.yml").read_text()) == {
        "url": "https://twodragon0.github.io"
    }


@pytest.mark.parametrize(
    "origin",
    [
        "",
        "ftp://twodragon0.github.io",
        "https://user:password@host.test",
        "https://host.test/path",
        "https://host.test?token=private",
        "https://host.test#section",
        "http://host.test:8080",
    ],
)
def test_pages_step_rejects_invalid_origin_without_writing(
    tmp_path, origin, ruby_available
):
    result = run_pages_config(tmp_path, origin)
    assert result.returncode != 0
    assert not (tmp_path / "jekyll-pages.yml").exists()
    assert "password" not in result.stderr
    assert "private" not in result.stderr
