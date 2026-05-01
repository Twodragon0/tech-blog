"""Smoke tests for the Noto woff2 build.sh integration.

Pure stdlib — no shell execution, no network calls.
Asserts structural invariants that must hold for the build hook to work correctly.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SH = REPO_ROOT / "build.sh"
GITIGNORE = REPO_ROOT / ".gitignore"


def _build_sh_text() -> str:
    return BUILD_SH.read_text(encoding="utf-8")


def _gitignore_text() -> str:
    return GITIGNORE.read_text(encoding="utf-8")


class TestBuildShNotoHook:
    """build.sh must reference the generator and the pinned URL."""

    def test_references_generator_script(self) -> None:
        assert "generate_noto_2tier_subset.py" in _build_sh_text(), (
            "build.sh must invoke generate_noto_2tier_subset.py"
        )

    def test_exports_noto_vf_url(self) -> None:
        text = _build_sh_text()
        assert "NOTO_VF_URL=" in text, "build.sh must set NOTO_VF_URL"

    def test_noto_vf_url_is_pinned_sha(self) -> None:
        """The URL must contain a 40-char commit SHA, not 'main' or a branch name."""
        text = _build_sh_text()
        match = re.search(r"NOTO_VF_URL='(https://raw\.githubusercontent\.com/[^']+)'", text)
        assert match, "build.sh must export NOTO_VF_URL as a single-quoted string"
        url = match.group(1)
        # Ensure the URL contains a 40-hex-char SHA (not the word 'main')
        sha_match = re.search(r"/([0-9a-f]{40})/", url)
        assert sha_match, f"NOTO_VF_URL must contain a pinned 40-char commit SHA; got: {url}"

    def test_references_syllable_list(self) -> None:
        assert "noto_subset_top1k.txt" in _build_sh_text(), (
            "build.sh must reference noto_subset_top1k.txt for the mtime check"
        )

    def test_stamp_file_variable_defined(self) -> None:
        assert ".noto-subset.stamp" in _build_sh_text(), (
            "build.sh must reference .noto-subset.stamp"
        )

    def test_graceful_failure_pattern(self) -> None:
        """The regen step must not hard-fail the build on generator error."""
        text = _build_sh_text()
        # The || { ... } or || true pattern after python3 call signals graceful failure
        assert re.search(r"generate_noto_2tier_subset\.py.*\|\|", text, re.DOTALL), (
            "build.sh must handle generator failure gracefully (|| pattern required)"
        )

    def test_pip_install_fonttools_graceful(self) -> None:
        """pip install for fonttools must also be graceful (|| true)."""
        text = _build_sh_text()
        assert re.search(r"fonttools.*\|\|.*true", text, re.DOTALL), (
            "pip install fonttools must have a graceful fallback (|| true)"
        )


class TestGitignoreStampFile:
    """The stamp file must be ignored by git."""

    def test_stamp_file_ignored(self) -> None:
        assert ".noto-subset.stamp" in _gitignore_text(), (
            ".noto-subset.stamp must be listed in .gitignore"
        )
