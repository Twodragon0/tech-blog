#!/usr/bin/env python3
"""Unit tests for scripts/check_filename_entities.py.

Tests cover:
  - amp* pattern detection (7+ entity types)
  - &amp; literal detection
  - &#NNN; numeric entity detection
  - &name; named entity detection
  - Clean filenames produce no false positives
  - Frontmatter image: field scanning
  - Whitelist suppression
  - --staged vs --all mode branching
  - suggest_clean_name correctness
  - check_files returns correct violation structure
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure scripts/ is on the path (conftest already adds parent, but be explicit)
sys.path.insert(0, str(Path(__file__).parent.parent))

import check_filename_entities as cfe


# ===========================================================================
# Pattern detection — has_entity_residue
# ===========================================================================

class TestHasEntityResidueAmpWord:
    """amp[a-z]+ pattern — 7 entity type variants."""

    def test_ampamp_detected(self):
        assert cfe.has_entity_residue("2025-05-30-titleampampmore.md") is True

    def test_amplsquo_detected(self):
        assert cfe.has_entity_residue("fileamplsquoname.svg") is True

    def test_amprsquo_detected(self):
        assert cfe.has_entity_residue("postamprsquotitle.md") is True

    def test_ampquot_detected(self):
        assert cfe.has_entity_residue("imageampquotfoo.svg") is True

    def test_amphellip_detected(self):
        assert cfe.has_entity_residue("titleamphellipend.md") is True

    def test_ampndash_detected(self):
        assert cfe.has_entity_residue("range-ampndash-value.svg") is True

    def test_ampmdash_detected(self):
        assert cfe.has_entity_residue("title-ampmdash-suffix.md") is True

    def test_ampldquo_detected(self):
        assert cfe.has_entity_residue("ampldquofile.md") is True

    def test_amprdquo_detected(self):
        assert cfe.has_entity_residue("amprdquofile.md") is True

    def test_ampapos_detected(self):
        # ampapos at start of filename segment — not preceded by a letter
        assert cfe.has_entity_residue("ampaposfile.md") is True

    def test_ampgt_detected(self):
        assert cfe.has_entity_residue("ampgtvalue.svg") is True

    def test_amplt_detected(self):
        assert cfe.has_entity_residue("ampltvalue.svg") is True

    def test_amp_uppercase_detected(self):
        """Pattern is case-insensitive."""
        assert cfe.has_entity_residue("fileAMPAMPrest.md") is True


class TestHasEntityResidueLiteralEntities:
    """Literal HTML entity patterns."""

    def test_amp_literal_detected(self):
        assert cfe.has_entity_residue("file&amp;name.md") is True

    def test_numeric_entity_with_semicolon(self):
        assert cfe.has_entity_residue("file&#39;name.md") is True

    def test_numeric_entity_without_semicolon(self):
        # Semicolon stripped by URL encoding leaves bare &#NNN
        assert cfe.has_entity_residue("file&#39name.md") is True

    def test_named_entity_detected(self):
        assert cfe.has_entity_residue("file&rsquo;name.md") is True

    def test_named_entity_amp_detected(self):
        assert cfe.has_entity_residue("file&amp;rest.svg") is True


class TestHasEntityResidueCleanNames:
    """Clean filenames must not produce false positives."""

    def test_normal_markdown_post(self):
        assert cfe.has_entity_residue("2025-04-21-Kubernetes-Security.md") is False

    def test_normal_svg_image(self):
        assert cfe.has_entity_residue("2025-04-21-Cloud-Architecture.svg") is False

    def test_normal_jpg_image(self):
        assert cfe.has_entity_residue("architecture-diagram.jpg") is False

    def test_name_with_amp_mid_word_no_boundary(self):
        """'example' contains 'amp' mid-word without a separator boundary — not an entity residue."""
        assert cfe.has_entity_residue("example.md") is False

    def test_name_with_amp_after_letter_no_boundary(self):
        """'campaign' has 'amp' after letters, not after a separator — not an entity residue."""
        assert cfe.has_entity_residue("campaign-2025.md") is False

    def test_dampness_not_flagged(self):
        """'dampness' contains 'amp' mid-word — not an entity residue."""
        assert cfe.has_entity_residue("dampness-study.md") is False

    def test_champion_not_flagged(self):
        """'champion' contains 'amp' after 'ch' — not an entity residue."""
        assert cfe.has_entity_residue("champion.svg") is False

    def test_empty_string(self):
        assert cfe.has_entity_residue("") is False

    def test_normal_hyphenated_post(self):
        assert cfe.has_entity_residue("2025-04-21-DevSecOps-Best-Practices.md") is False

    def test_path_with_clean_segments(self):
        assert cfe.has_entity_residue("assets/images/2025-04-21-banner.svg") is False


# ===========================================================================
# suggest_clean_name
# ===========================================================================

class TestSuggestCleanName:
    def test_removes_ampamp(self):
        result = cfe.suggest_clean_name("titleampampsuffix.md")
        assert "ampamp" not in result

    def test_removes_literal_amp(self):
        result = cfe.suggest_clean_name("file&amp;name.svg")
        assert "&amp;" not in result

    def test_removes_numeric_entity(self):
        result = cfe.suggest_clean_name("file&#39;name.md")
        assert "&#39;" not in result

    def test_no_double_hyphens_remain(self):
        result = cfe.suggest_clean_name("title-ampamp-rest.md")
        assert "--" not in result

    def test_clean_name_unchanged(self):
        original = "2025-04-21-Clean-Title.md"
        assert cfe.suggest_clean_name(original) == original


# ===========================================================================
# Frontmatter image field scanning
# ===========================================================================

class TestCheckFrontmatterImage:
    def _make_post(self, tmp_path: Path, image_value: str) -> Path:
        content = textwrap.dedent(f"""\
            ---
            layout: post
            title: "Test"
            image: {image_value}
            ---
            Body content.
        """)
        post = tmp_path / "2025-04-21-test.md"
        post.write_text(content, encoding="utf-8")
        return post

    def test_clean_image_field_returns_none(self, tmp_path):
        post = self._make_post(tmp_path, "/assets/images/2025-04-21-clean.svg")
        assert cfe.check_frontmatter_image(post) is None

    def test_amplsquo_in_image_field_detected(self, tmp_path):
        post = self._make_post(tmp_path, "/assets/images/2025-04-21-titleamplsquo.svg")
        result = cfe.check_frontmatter_image(post)
        assert result is not None
        assert "amplsquo" in result

    def test_ampquot_in_image_field_detected(self, tmp_path):
        post = self._make_post(tmp_path, "/assets/images/2025-04-21-ampquotfile.svg")
        result = cfe.check_frontmatter_image(post)
        assert result is not None

    def test_amp_literal_in_image_field_detected(self, tmp_path):
        post = self._make_post(tmp_path, "/assets/images/file&amp;name.svg")
        result = cfe.check_frontmatter_image(post)
        assert result is not None

    def test_no_frontmatter_returns_none(self, tmp_path):
        post = tmp_path / "no-fm.md"
        post.write_text("Just body, no frontmatter.\n", encoding="utf-8")
        assert cfe.check_frontmatter_image(post) is None

    def test_frontmatter_without_image_field_returns_none(self, tmp_path):
        content = textwrap.dedent("""\
            ---
            layout: post
            title: "No image field"
            ---
            Body.
        """)
        post = tmp_path / "no-image.md"
        post.write_text(content, encoding="utf-8")
        assert cfe.check_frontmatter_image(post) is None

    def test_nonexistent_file_returns_none(self, tmp_path):
        missing = tmp_path / "nonexistent.md"
        assert cfe.check_frontmatter_image(missing) is None


# ===========================================================================
# Whitelist suppression
# ===========================================================================

class TestWhitelistSuppression:
    def test_whitelisted_basename_skipped(self, tmp_path):
        whitelist = frozenset({"badampampfile.md"})
        fpath = Path("_posts/badampampfile.md")
        violations = cfe.check_files([fpath], tmp_path, whitelist)
        assert violations == []

    def test_whitelisted_rel_path_skipped(self, tmp_path):
        whitelist = frozenset({"_posts/badampampfile.md"})
        fpath = Path("_posts/badampampfile.md")
        violations = cfe.check_files([fpath], tmp_path, whitelist)
        assert violations == []

    def test_non_whitelisted_still_detected(self, tmp_path):
        whitelist = frozenset({"_posts/other-ampfile.md"})
        fpath = Path("_posts/badampampfile.md")
        violations = cfe.check_files([fpath], tmp_path, whitelist)
        assert len(violations) == 1

    def test_empty_whitelist_detects_all(self, tmp_path):
        whitelist = frozenset()
        fpath = Path("assets/images/imageamplsquo.svg")
        violations = cfe.check_files([fpath], tmp_path, whitelist)
        assert len(violations) == 1


# ===========================================================================
# check_files — violation structure
# ===========================================================================

class TestCheckFiles:
    def test_clean_file_no_violation(self, tmp_path):
        fpath = Path("_posts/2025-04-21-Clean-Post.md")
        violations = cfe.check_files([fpath], tmp_path, frozenset())
        assert violations == []

    def test_contaminated_filename_returns_violation(self, tmp_path):
        fpath = Path("assets/images/2025-05-30-titleamprsquo.svg")
        violations = cfe.check_files([fpath], tmp_path, frozenset())
        assert len(violations) == 1
        rel, description, suggested = violations[0]
        assert rel == "assets/images/2025-05-30-titleamprsquo.svg"
        assert "amprsquo" in description
        assert suggested is not None

    def test_multiple_violations_all_returned(self, tmp_path):
        files = [
            Path("_posts/ampamppost.md"),
            Path("assets/images/imageamphellip.svg"),
        ]
        violations = cfe.check_files(files, tmp_path, frozenset())
        assert len(violations) == 2

    def test_violation_tuple_has_three_elements(self, tmp_path):
        fpath = Path("_posts/ampquotfile.md")
        violations = cfe.check_files([fpath], tmp_path, frozenset())
        assert len(violations) == 1
        assert len(violations[0]) == 3

    def test_mix_clean_and_dirty(self, tmp_path):
        files = [
            Path("_posts/2025-04-21-Clean.md"),
            Path("_posts/ampampbad.md"),
        ]
        violations = cfe.check_files(files, tmp_path, frozenset())
        assert len(violations) == 1
        assert "ampampbad" in violations[0][0]


# ===========================================================================
# --staged vs --all mode branching
# ===========================================================================

class TestModeStaged:
    """--staged mode reads from git diff --cached."""

    def test_staged_calls_git_diff_cached(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "_posts/staged-clean.md\n"
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            files = cfe._staged_files()
        call_args = mock_run.call_args[0][0]
        assert "--cached" in call_args
        assert "--name-only" in call_args

    def test_staged_returns_paths(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "_posts/file1.md\nassets/images/file2.svg\n"
        with patch("subprocess.run", return_value=mock_result):
            files = cfe._staged_files()
        assert len(files) == 2
        assert all(isinstance(f, Path) for f in files)

    def test_staged_returns_empty_on_git_error(self):
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            files = cfe._staged_files()
        assert files == []

    def test_staged_skips_empty_lines(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "_posts/file.md\n\n\n"
        with patch("subprocess.run", return_value=mock_result):
            files = cfe._staged_files()
        assert len(files) == 1


class TestModeAll:
    """--all mode scans _posts/ and assets/images/ directories."""

    def test_all_scans_posts_directory(self, tmp_path):
        posts = tmp_path / "_posts"
        posts.mkdir()
        (posts / "2025-04-21-test.md").write_text("---\n---\n", encoding="utf-8")
        files = cfe._all_files(tmp_path)
        assert any("_posts" in str(f) for f in files)

    def test_all_scans_images_directory(self, tmp_path):
        images = tmp_path / "assets" / "images"
        images.mkdir(parents=True)
        (images / "test.svg").write_text("<svg/>", encoding="utf-8")
        files = cfe._all_files(tmp_path)
        assert any("images" in str(f) for f in files)

    def test_all_returns_empty_when_dirs_missing(self, tmp_path):
        files = cfe._all_files(tmp_path)
        assert files == []

    def test_all_finds_contaminated_file(self, tmp_path):
        posts = tmp_path / "_posts"
        posts.mkdir()
        bad = posts / "2025-09-17-titleamprsquo.md"
        bad.write_text("---\n---\n", encoding="utf-8")
        files = cfe._all_files(tmp_path)
        violations = cfe.check_files(files, tmp_path, frozenset())
        assert any("amprsquo" in v[1] for v in violations)


# ===========================================================================
# main() exit codes
# ===========================================================================

class TestMainExitCodes:
    def test_main_returns_0_when_no_staged_files(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        with patch("subprocess.run", return_value=mock_result):
            code = cfe.main(["--staged"])
        assert code == 0

    def test_main_returns_0_for_clean_all(self, tmp_path):
        git_result = MagicMock()
        git_result.returncode = 0
        git_result.stdout = str(tmp_path)

        def fake_run(cmd, **kwargs):
            if "rev-parse" in cmd:
                return git_result
            return git_result

        with patch("subprocess.run", side_effect=fake_run):
            code = cfe.main(["--all"])
        assert code == 0

    def test_main_returns_1_for_contaminated_staged(self, tmp_path, capsys):
        git_root = MagicMock()
        git_root.returncode = 0
        git_root.stdout = str(tmp_path) + "\n"

        staged = MagicMock()
        staged.returncode = 0
        staged.stdout = "_posts/badampampfile.md\n"

        call_count = [0]

        def fake_run(cmd, **kwargs):
            call_count[0] += 1
            if "rev-parse" in cmd:
                return git_root
            return staged

        with patch("subprocess.run", side_effect=fake_run):
            code = cfe.main(["--staged"])
        assert code == 1
