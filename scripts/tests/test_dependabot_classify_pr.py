#!/usr/bin/env python3
"""Tests for ``scripts/dependabot_classify_pr.py``.

Covers:
- Real-world Dependabot PR title formats (``>=X.Y`` range, pinned, group
  bumps without a version, mixed ``from/to`` orderings).
- Major/minor/patch classification correctness.
- Pre-release suffix handling (``2.5.0rc1``).
- Negative paths: empty title, no ``from/to`` clause, downgrade,
  unparseable versions.
"""

import pytest

from scripts.dependabot_classify_pr import _parse_version, classify_pr_title


# =====================================================================
# classify_pr_title - real-world Dependabot title coverage
# =====================================================================


class TestClassifyPrTitle:
    @pytest.mark.parametrize(
        "title,expected",
        [
            # Patch bumps.
            (
                "deps(py)(deps): update foo requirement from >=1.2.3 to >=1.2.4 in /scripts",
                "version-update:semver-patch",
            ),
            ("Bump foo from 1.2.3 to 1.2.4", "version-update:semver-patch"),
            # Minor bumps - this is the gtts case from PR #363.
            (
                "deps(py)(deps): update gtts requirement from >=2.3.0 to >=2.5.4 in /scripts",
                "version-update:semver-minor",
            ),
            # Major bumps - pytest #362, pillow #364.
            (
                "deps(py)(deps): update pytest requirement from >=7.0 to >=8.4.2 in /scripts",
                "version-update:semver-major",
            ),
            (
                "deps(py)(deps): update pillow requirement from >=9.0.0 to >=11.3.0 in /scripts",
                "version-update:semver-major",
            ),
            # Pinned (==) prefix.
            (
                "deps: bump black from ==23.1.0 to ==23.3.1",
                "version-update:semver-minor",
            ),
        ],
    )
    def test_classifies_real_dependabot_titles(self, title, expected):
        assert classify_pr_title(title) == expected

    @pytest.mark.parametrize(
        "title",
        [
            "",
            None,
            "deps(actions)(deps): bump the github-actions group with 5 updates",
            "Random PR title with no version transition",
            "Bump foo from invalid to alsoinvalid",
        ],
    )
    def test_returns_empty_when_unclassifiable(self, title):
        assert classify_pr_title(title or "") == ""

    def test_downgrade_returns_empty(self):
        # We don't auto-classify downgrades; safer to require manual review.
        assert (
            classify_pr_title("Bump foo from 2.0.0 to 1.9.5") == ""
        ), "downgrade must not classify"

    def test_same_version_returns_empty(self):
        # No effective change.
        assert classify_pr_title("Bump foo from 1.2.3 to 1.2.3") == ""

    def test_pre_release_suffix_stripped(self):
        # 2.5.0rc1 -> (2, 5, 0); we treat suffix as no-op for classification.
        assert (
            classify_pr_title("Bump foo from 2.4.9 to 2.5.0rc1")
            == "version-update:semver-minor"
        )


# =====================================================================
# _parse_version - operator stripping + numeric parsing
# =====================================================================


class TestParseVersion:
    @pytest.mark.parametrize(
        "raw,expected",
        [
            (">=11.3.0", (11, 3, 0)),
            ("==2.5.4", (2, 5, 4)),
            ("~=1.2.3", (1, 2, 3)),
            ("^1.2", (1, 2)),
            ("v1.2.3", (1, 2, 3)),
            ("8.4.2", (8, 4, 2)),
            ("8.4", (8, 4)),
            ("2.5.0rc1", (2, 5, 0)),
            (">=8.0.0a1", (8, 0, 0)),
        ],
    )
    def test_parses_common_formats(self, raw, expected):
        assert _parse_version(raw) == expected

    @pytest.mark.parametrize("raw", ["", "abc", "v.1.2", ">=,"])
    def test_returns_empty_on_garbage(self, raw):
        assert _parse_version(raw) == ()
