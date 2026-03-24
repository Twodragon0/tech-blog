#!/usr/bin/env python3
"""Unit tests for fix_links_unified.py.

Tests cover:
- is_github_link: URL pattern detection
- check_dummy_links: dummy/placeholder pattern detection with line numbers
- fix_reference_links: URL and text replacement rules (LINK_FIXES, TEXT_FIXES)
- fix_code_blocks: short code block restoration, link text normalisation
- fix_contextual_links: keyword-triggered link replacements
- process_post_file: integration path (check mode vs fix mode, error handling)
- Edge cases: empty strings, malformed URLs, relative paths, no-op inputs
"""

import sys
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from fix_links_unified import (
    check_dummy_links,
    fix_code_blocks,
    fix_contextual_links,
    fix_reference_links,
    is_github_link,
    process_post_file,
)


# ---------------------------------------------------------------------------
# is_github_link
# ---------------------------------------------------------------------------


def test_is_github_link_returns_true_for_github_url():
    assert is_github_link("https://github.com/falcosecurity/falco") is True


def test_is_github_link_returns_true_for_www_prefix():
    assert is_github_link("https://www.github.com/user/repo") is True


def test_is_github_link_returns_true_for_http():
    assert is_github_link("http://github.com/user/repo") is True


def test_is_github_link_returns_false_for_non_github_url():
    assert is_github_link("https://docs.docker.com/engine/") is False


def test_is_github_link_returns_false_for_empty_string():
    assert is_github_link("") is False


def test_is_github_link_returns_false_for_partial_domain():
    # Contains "github" but not github.com/
    assert is_github_link("https://notgithub.com/user/repo") is False


# ---------------------------------------------------------------------------
# check_dummy_links
# ---------------------------------------------------------------------------


def test_check_dummy_links_detects_example_github_url():
    content = "See [example](https://github.com/example/repo) for details."
    issues = check_dummy_links(content)
    assert len(issues) >= 1
    line_nums = [line for line, _ in issues]
    assert 1 in line_nums


def test_check_dummy_links_detects_dummy_keyword():
    content = "This is a dummy link for testing."
    issues = check_dummy_links(content)
    assert any("dummy" in text.lower() for _, text in issues)


def test_check_dummy_links_detects_placeholder_keyword():
    content = "Replace this placeholder with a real URL."
    issues = check_dummy_links(content)
    assert any("placeholder" in text.lower() for _, text in issues)


def test_check_dummy_links_returns_empty_list_for_clean_content():
    content = "See [Falco](https://github.com/falcosecurity/falco) for runtime security."
    issues = check_dummy_links(content)
    assert issues == []


def test_check_dummy_links_reports_correct_line_number():
    content = "line one\nline two\nhttps://github.com/example/test\nline four"
    issues = check_dummy_links(content)
    assert any(line == 3 for line, _ in issues)


def test_check_dummy_links_is_case_insensitive_for_dummy():
    content = "This is a DUMMY link."
    issues = check_dummy_links(content)
    assert len(issues) >= 1


# ---------------------------------------------------------------------------
# fix_reference_links
# ---------------------------------------------------------------------------


def test_fix_reference_links_replaces_kubernetes_best_practices_url():
    content = "See https://kubernetes.io/docs/concepts/security/best-practices/ for more."
    result = fix_reference_links(content)
    assert "best-practices" not in result
    assert "security-checklist" in result


def test_fix_reference_links_replaces_versioned_trivy_download_url():
    content = (
        "wget https://github.com/aquasecurity/trivy/releases/latest/download/"
        "trivy_0.50.1_Linux-64bit.tar.gz"
    )
    result = fix_reference_links(content)
    assert "trivy_0.50.1_Linux-64bit.tar.gz" not in result
    assert "https://github.com/aquasecurity/trivy/releases" in result


def test_fix_reference_links_replaces_docker_library_text():
    content = (
        "> **코드 예시**: 전체 코드는 "
        "[GitHub 예제 저장소](https://github.com/docker-library)를 참조하세요."
    )
    result = fix_reference_links(content)
    assert "docker-library" not in result
    assert "docs.docker.com" in result


def test_fix_reference_links_is_no_op_for_unrelated_content():
    content = "Nothing to replace here. Just plain text."
    result = fix_reference_links(content)
    assert result == content


# ---------------------------------------------------------------------------
# fix_code_blocks
# ---------------------------------------------------------------------------


def test_fix_code_blocks_restores_short_spf_comment():
    content = (
        "<!-- 긴 코드 블록 제거됨\n"
        "```dns\n"
        "v=spf1 include:_spf.google.com ~all\n"
        "```\n"
        "-->"
    )
    result = fix_code_blocks(content)
    assert "```dns" in result
    assert "v=spf1" in result
    # The HTML comment wrapper should be gone
    assert "<!--" not in result


def test_fix_code_blocks_keeps_long_code_in_comment():
    long_code = "\n".join([f"line {i}" for i in range(20)])
    content = (
        "<!-- 긴 코드 블록 제거됨\n"
        f"```python\n{long_code}\n```\n"
        "-->"
    )
    result = fix_code_blocks(content)
    # Long code (>5 lines) should remain commented out
    assert "<!--" in result


def test_fix_code_blocks_normalises_github_example_link_in_json_block():
    content = (
        "> **코드 예시**: 전체 코드는 "
        "[GitHub 예제 저장소](https://github.com/some/repo)를 참조하세요.\n"
        "> \n"
        "> ```json\n"
    )
    result = fix_code_blocks(content)
    assert "json.org" in result


def test_fix_code_blocks_is_no_op_for_plain_text():
    content = "No code blocks here."
    result = fix_code_blocks(content)
    assert result == content


# ---------------------------------------------------------------------------
# fix_contextual_links
# ---------------------------------------------------------------------------


def test_fix_contextual_links_targets_dependabot_context():
    content = (
        "We use dependabot for dependency updates.\n"
        "> **코드 예시**: 전체 코드는 "
        "[GitHub 예제 저장소](https://github.com/kubernetes/examples)와 dependabot"
    )
    result = fix_contextual_links(content)
    assert "docs.github.com/en/code-security/dependabot" in result


def test_fix_contextual_links_is_no_op_without_matching_context():
    content = "This post is about FinOps cost optimisation strategies."
    result = fix_contextual_links(content)
    assert result == content


def test_fix_contextual_links_targets_waf_cloudfront_context():
    content = (
        "AWS WAF protects our CloudFront distribution.\n"
        "> **코드 예시**: 전체 코드는 "
        "[GitHub 예제 저장소](https://github.com/aws-samples)와 waf"
    )
    result = fix_contextual_links(content)
    assert "trussworks/terraform-aws-wafv2" in result


# ---------------------------------------------------------------------------
# process_post_file
# ---------------------------------------------------------------------------


def test_process_post_file_returns_error_for_missing_file(tmp_path):
    missing = tmp_path / "nonexistent.md"
    result = process_post_file(missing, fix_mode=False)
    assert any("Error" in issue for issue in result["issues"])


def test_process_post_file_detects_dummy_link_in_check_mode(tmp_path):
    post = tmp_path / "2025-01-01-test.md"
    post.write_text(
        "---\ntitle: Test\n---\n\nSee [link](https://github.com/example/repo).\n",
        encoding="utf-8",
    )
    result = process_post_file(post, fix_mode=False)
    assert result["fixed"] is False
    assert len(result["issues"]) >= 1


def test_process_post_file_fixes_trivy_url_in_fix_mode(tmp_path):
    post = tmp_path / "2025-01-01-trivy.md"
    original = (
        "---\ntitle: Trivy\n---\n\n"
        "wget https://github.com/aquasecurity/trivy/releases/latest/download/"
        "trivy_0.50.1_Linux-64bit.tar.gz\n"
    )
    post.write_text(original, encoding="utf-8")
    result = process_post_file(post, fix_mode=True, dry_run=False)
    assert result["fixed"] is True
    updated = post.read_text(encoding="utf-8")
    assert "trivy_0.50.1_Linux-64bit.tar.gz" not in updated


def test_process_post_file_dry_run_does_not_write_file(tmp_path):
    post = tmp_path / "2025-01-01-dry.md"
    original = (
        "---\ntitle: Test\n---\n\n"
        "https://kubernetes.io/docs/concepts/security/best-practices/\n"
    )
    post.write_text(original, encoding="utf-8")
    result = process_post_file(post, fix_mode=True, dry_run=True)
    assert result["fixed"] is True
    # File on disk must be unchanged
    assert post.read_text(encoding="utf-8") == original


def test_process_post_file_returns_no_issues_for_clean_post(tmp_path):
    post = tmp_path / "2025-01-01-clean.md"
    post.write_text(
        "---\ntitle: Clean\n---\n\nThis post has no suspicious links at all.\n",
        encoding="utf-8",
    )
    result = process_post_file(post, fix_mode=False)
    assert result["issues"] == []
    assert result["fixed"] is False
