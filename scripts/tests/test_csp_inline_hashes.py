"""Tests for scripts/dev/check_csp_inline_hashes.py.

Covers:
- The real _includes/head.html passes the gate against the checked-in
  manifest, and its two known-good hashes match the browser-validated
  ground-truth values from the security review.
- A mutated inline-script body is detected as a MISMATCH.
- --update rewrites the manifest to match the current head.html.

Uses tmp_path fixtures throughout; never mutates the real head.html.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts/ and scripts/dev/ to path so we can import the helper directly
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "dev"))

from check_csp_inline_hashes import (  # noqa: E402
    compute_current_hashes,
    compute_hash,
    diff_hashes,
    extract_inline_scripts,
    load_manifest,
    main,
    save_manifest,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = Path(__file__).parent.parent / "dev" / "check_csp_inline_hashes.py"
REAL_HEAD_HTML = REPO_ROOT / "_includes" / "head.html"
REAL_MANIFEST = REPO_ROOT / "scripts" / "dev" / "csp_inline_hashes.json"

# Ground-truth hashes validated against the browser's CSP hashing behavior
# (see the security review referenced in scripts/dev/check_csp_inline_hashes.py).
KNOWN_GOOD_THEME_INIT = "sha256-FiF+gbNVa7+4pSSr/iRRyau5vRAaG7O6j/jhduKyItE="
KNOWN_GOOD_CSS_LOADER = "sha256-bJASvghY1rpfB3ScKAFDDJoFiYeDK3Cu+aVj0ferf98="


SAMPLE_HEAD = """<!DOCTYPE html>
<head>
  <!-- comment mentioning a fake <script src="not-real.js"> tag as prose -->
  <script id="theme-init">(function(){console.log('theme');})();</script>
  <script src="{{ '/assets/js/console-filter.js' | relative_url }}" defer></script>
  <script type="application/ld+json">{"@type": "Article"}</script>
  <script>
    (function () {
      console.log('deferred css loader');
    })();
  </script>
</head>
"""


# ---------------------------------------------------------------------------
# Extraction unit tests
# ---------------------------------------------------------------------------


def test_extract_inline_scripts_excludes_src_and_ldjson():
    scripts = extract_inline_scripts(SAMPLE_HEAD)
    labels = [s.label for s in scripts]
    assert labels == ["theme-init", "inline-script-2"]


def test_extract_inline_scripts_ignores_comment_prose():
    """A comment mentioning a fake <script src=...> tag must not be parsed
    as a real script boundary (would misalign subsequent tag matching)."""
    scripts = extract_inline_scripts(SAMPLE_HEAD)
    # Only the two real inline scripts are found; the comment's fake tag
    # text does not produce a spurious third entry or corrupt content.
    assert len(scripts) == 2
    assert "console.log('theme')" in scripts[0].content
    assert "deferred css loader" in scripts[1].content


def test_compute_hash_is_stable_sha256_token():
    h = compute_hash("abc")
    assert h.startswith("sha256-")
    # Recomputing the same content yields the same token.
    assert compute_hash("abc") == h
    assert compute_hash("abcd") != h


# ---------------------------------------------------------------------------
# (a) Real head.html passes the gate + matches known-good ground truth
# ---------------------------------------------------------------------------


def test_real_head_html_matches_known_good_hashes():
    html = REAL_HEAD_HTML.read_text(encoding="utf-8")
    hashes = compute_current_hashes(html)
    assert hashes.get("theme-init") == KNOWN_GOOD_THEME_INIT
    assert hashes.get("inline-script-2") == KNOWN_GOOD_CSS_LOADER


def test_real_head_html_passes_gate_against_checked_in_manifest():
    exit_code = main(["--head", str(REAL_HEAD_HTML), "--manifest", str(REAL_MANIFEST)])
    assert exit_code == 0


def test_real_head_html_passes_gate_via_subprocess():
    result = subprocess.run(
        [sys.executable, str(SCRIPT)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "OK" in result.stdout


# ---------------------------------------------------------------------------
# (b) Mutated inline-script body fails the gate
# ---------------------------------------------------------------------------


def test_mutated_inline_script_body_fails(tmp_path: Path):
    head = tmp_path / "head.html"
    manifest = tmp_path / "csp_inline_hashes.json"

    head.write_text(SAMPLE_HEAD, encoding="utf-8")
    save_manifest(manifest, compute_current_hashes(SAMPLE_HEAD))

    # Sanity: unmutated tree passes.
    assert main(["--head", str(head), "--manifest", str(manifest)]) == 0

    # Mutate the theme-init script body (even whitespace-only change would
    # change the hash).
    mutated = SAMPLE_HEAD.replace(
        "console.log('theme');",
        "console.log('theme-mutated');",
    )
    head.write_text(mutated, encoding="utf-8")

    exit_code = main(["--head", str(head), "--manifest", str(manifest)])
    assert exit_code == 1


def test_diff_hashes_reports_mismatch_with_old_and_new():
    manifest = {"theme-init": "sha256-OLD"}
    current = {"theme-init": "sha256-NEW"}
    problems = diff_hashes(current, manifest)
    assert len(problems) == 1
    assert "sha256-OLD" in problems[0]
    assert "sha256-NEW" in problems[0]
    assert "MISMATCH" in problems[0]


def test_diff_hashes_reports_new_script():
    problems = diff_hashes({"new-label": "sha256-X"}, {})
    assert len(problems) == 1
    assert "NEW inline script" in problems[0]


def test_diff_hashes_reports_removed_script():
    problems = diff_hashes({}, {"gone-label": "sha256-X"})
    assert len(problems) == 1
    assert "REMOVED" in problems[0]


def test_diff_hashes_clean_when_matching():
    current = {"theme-init": "sha256-A"}
    manifest = {"theme-init": "sha256-A"}
    assert diff_hashes(current, manifest) == []


def test_missing_manifest_fails_with_guidance(tmp_path: Path):
    head = tmp_path / "head.html"
    head.write_text(SAMPLE_HEAD, encoding="utf-8")
    missing_manifest = tmp_path / "does_not_exist.json"

    exit_code = main(["--head", str(head), "--manifest", str(missing_manifest)])
    assert exit_code == 1


def test_missing_head_html_fails(tmp_path: Path):
    missing_head = tmp_path / "nope.html"
    manifest = tmp_path / "manifest.json"
    exit_code = main(["--head", str(missing_head), "--manifest", str(manifest)])
    assert exit_code == 2


# ---------------------------------------------------------------------------
# (c) --update rewrites the manifest
# ---------------------------------------------------------------------------


def test_update_rewrites_manifest(tmp_path: Path):
    head = tmp_path / "head.html"
    manifest = tmp_path / "csp_inline_hashes.json"
    head.write_text(SAMPLE_HEAD, encoding="utf-8")

    # Seed a stale manifest.
    save_manifest(manifest, {"theme-init": "sha256-STALE"})

    exit_code = main(["--head", str(head), "--manifest", str(manifest), "--update"])
    assert exit_code == 0

    updated = load_manifest(manifest)
    expected = compute_current_hashes(SAMPLE_HEAD)
    assert updated == expected
    assert updated["theme-init"] != "sha256-STALE"


def test_update_then_check_passes(tmp_path: Path):
    head = tmp_path / "head.html"
    manifest = tmp_path / "csp_inline_hashes.json"
    head.write_text(SAMPLE_HEAD, encoding="utf-8")

    assert main(["--head", str(head), "--manifest", str(manifest), "--update"]) == 0
    assert main(["--head", str(head), "--manifest", str(manifest)]) == 0


def test_save_manifest_output_is_valid_json(tmp_path: Path):
    manifest = tmp_path / "csp_inline_hashes.json"
    save_manifest(manifest, {"b": "sha256-2", "a": "sha256-1"})
    with manifest.open(encoding="utf-8") as f:
        data = json.load(f)
    assert data == {"a": "sha256-1", "b": "sha256-2"}
