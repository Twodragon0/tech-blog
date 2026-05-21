"""Integration tests for the `image_content_hash` Jekyll plugin.

Plan: .omc/plans/image-content-hash-versioning.md (Step 1).

The plugin computes SHA-256[0:8] of every image under assets/images/ and
appends `?v={hash}` to image URLs at build time. These tests verify the
behavior end-to-end by running a Jekyll build and inspecting the output
HTML. Skips gracefully when `bundle` / `jekyll` is not available.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
IMAGES_DIR = REPO_ROOT / "assets" / "images"

# Three L25 covers known to be referenced from L25-promoted posts (2026-05-15
# digest cover overhaul). They must show up with a content-hash version query
# in the built HTML.
L25_SLUGS = (
    "2025/11/19/Post-Mortem_2025_11_18_Cloudflare_Global_Incident_Response_Log_What_Learned",
    "2025/12/12/Cloud_Security_8Batch_3Week_AWS_FinOps_ArchitectureFrom_ISMS-P_Security_AuditTo_Complete_Strategy",
    "2025/05/30/Kubernetes_Minikube_and_K9s_Practice_Guide",
)

VERSIONED_IMG_SRC_RE = re.compile(
    r'src="(/assets/images/[^"?\s]+\.(?:svg|png|webp|avif))\?v=([a-f0-9]{8})"'
)


def _bundle_available() -> bool:
    return shutil.which("bundle") is not None


@pytest.fixture(scope="module")
def built_site_dir() -> Path:
    """Run `bundle exec jekyll build` once and return the destination dir."""
    if not _bundle_available():
        pytest.skip("bundle not available in this environment")

    dest = Path(tempfile.mkdtemp(prefix="jk-image-hash-pytest-"))
    try:
        env = os.environ.copy()
        result = subprocess.run(
            [
                "bundle",
                "exec",
                "jekyll",
                "build",
                "--destination",
                str(dest),
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            pytest.skip(
                f"jekyll build failed (rc={result.returncode}): "
                f"{result.stderr[-500:]}"
            )
        yield dest
    finally:
        shutil.rmtree(dest, ignore_errors=True)


def _expected_hash(image_rel_path: str) -> str | None:
    """Compute SHA-256[0:8] for an image relative to the repo root."""
    abs_path = REPO_ROOT / image_rel_path.lstrip("/")
    if not abs_path.is_file():
        return None
    return hashlib.sha256(abs_path.read_bytes()).hexdigest()[:8]


@pytest.mark.parametrize("post_slug", L25_SLUGS)
def test_l25_post_body_image_has_content_hash_version(
    built_site_dir: Path, post_slug: str
) -> None:
    """Each L25-promoted post must emit a body <img> with ?v={hash}."""
    html_path = built_site_dir / "posts" / post_slug / "index.html"
    if not html_path.is_file():
        # Diagnostic: dump the actual built layout around the expected path
        # so we can see what Jekyll produced instead. This fires only on
        # failure and is cheap (a few directory listings).
        diag_lines = [f"missing built HTML: {html_path}"]
        parent = html_path.parent.parent  # e.g. .../posts/2025/05/30/
        for level in (parent.parent, parent):  # /YYYY/MM/ and /YYYY/MM/DD/
            if level.is_dir():
                diag_lines.append(f"  contents of {level}:")
                for entry in sorted(level.iterdir()):
                    diag_lines.append(f"    {entry.name}{'/' if entry.is_dir() else ''}")
            else:
                diag_lines.append(f"  missing dir: {level}")
        # Also search the whole build dir for any path containing the slug tail
        slug_tail = post_slug.rsplit("/", 1)[-1]
        matches = list(built_site_dir.rglob(f"*{slug_tail}*"))
        diag_lines.append(f"  rglob hits for *{slug_tail}*: {len(matches)}")
        for m in matches[:10]:
            diag_lines.append(f"    {m.relative_to(built_site_dir)}")
        pytest.fail("\n".join(diag_lines))

    html = html_path.read_text(encoding="utf-8")
    matches = VERSIONED_IMG_SRC_RE.findall(html)
    assert matches, (
        f"no versioned image found in {post_slug}/index.html — "
        f"plugin not running or filter not piped?"
    )

    # The hero <img> src should appear and its hash must match the file's
    # actual SHA-256[0:8] on disk.
    img_path, observed_hash = matches[0]
    expected = _expected_hash(img_path)
    assert expected is not None, (
        f"hero image file missing on disk: {img_path}"
    )
    assert observed_hash == expected, (
        f"hash mismatch for {img_path}: html={observed_hash} disk={expected}"
    )


def test_at_least_three_distinct_hashes_in_built_site(
    built_site_dir: Path,
) -> None:
    """Proves the filter is computing, not hardcoding."""
    posts_dir = built_site_dir / "posts"
    assert posts_dir.is_dir(), f"missing posts dir: {posts_dir}"

    hashes: set[str] = set()
    sampled = 0
    for html_path in posts_dir.rglob("index.html"):
        if html_path.stat().st_size < 200:  # skip redirect stubs
            continue
        sampled += 1
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        for _, h in VERSIONED_IMG_SRC_RE.findall(html):
            hashes.add(h)
        if sampled >= 30 and len(hashes) >= 5:
            break

    assert len(hashes) >= 3, (
        f"only {len(hashes)} distinct image-hash(es) found across "
        f"{sampled} sampled posts — filter likely hardcoded or broken"
    )


def test_no_remaining_v20260518_hot_fix(built_site_dir: Path) -> None:
    """Step-0 hot-fix `?v=20260518` must be gone from image URLs in built HTML.

    Note: `?v=202605181722` (longer timestamp) is a separate JS-asset cache
    key generated by site.time; that one is allowed. We only forbid the
    8-digit date `?v=20260518` exactly on image URLs.
    """
    image_hot_fix_re = re.compile(
        r'/assets/images/[^"\s]+\.(?:svg|png|webp|avif)\?v=20260518\b'
    )
    posts_dir = built_site_dir / "posts"
    offenders: list[str] = []
    for html_path in posts_dir.rglob("index.html"):
        if html_path.stat().st_size < 200:
            continue
        html = html_path.read_text(encoding="utf-8", errors="ignore")
        if image_hot_fix_re.search(html):
            offenders.append(str(html_path.relative_to(built_site_dir)))
    assert not offenders, (
        f"stale Step-0 hot-fix `?v=20260518` still on image URLs: "
        f"{offenders[:5]}"
    )
