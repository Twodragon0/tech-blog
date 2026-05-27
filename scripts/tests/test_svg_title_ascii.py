"""Unit tests for scripts/check_svg_title_ascii.py.

Covers:
- Detection of the exact bug: U+00B7 middle-dot in <title>
- ASCII-only <title> passes
- Hangul in <title> detected as non-ASCII
- U+00B7 (middle-dot) between ASCII tokens is still non-ASCII (policy)
- <desc> element violations detected
- Exit-code contract via _violations()
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

# Import the module under test directly.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from check_svg_title_ascii import _violations  # noqa: E402


def _make_svg(title: str = "", desc: str = "") -> str:
    """Minimal valid SVG string with optional <title> and <desc> content."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">']
    if title:
        parts.append(f"<title>{title}</title>")
    if desc:
        parts.append(f"<desc>{desc}</desc>")
    parts.append("</svg>")
    return "\n".join(parts)


@pytest.fixture
def tmp_svg(tmp_path: Path):
    """Factory: write SVG content to a temp file and return its Path."""
    def _write(content: str) -> Path:
        p = tmp_path / "test.svg"
        p.write_text(content, encoding="utf-8")
        return p
    return _write


# ---------------------------------------------------------------------------
# <title> tests
# ---------------------------------------------------------------------------


class TestTitleViolations:
    def test_exact_bug_middle_dot_in_title(self, tmp_svg):
        """The original bug: U+00B7 middle-dot + U+2022 bullet in digest title."""
        svg = _make_svg(title="2026 05 27 : ·· (30)")
        path = tmp_svg(svg)
        hits = _violations(path)
        codepoints = {h[2] for h in hits}
        assert 0x00B7 in codepoints, "U+00B7 middle-dot must be detected"

    def test_bullet_u2022_in_title(self, tmp_svg):
        """U+2022 bullet point must be detected."""
        svg = _make_svg(title="Items • news")
        path = tmp_svg(svg)
        hits = _violations(path)
        codepoints = {h[2] for h in hits}
        assert 0x2022 in codepoints, "U+2022 bullet must be detected"

    def test_ascii_only_title_passes(self, tmp_svg):
        """A clean ASCII-only title produces zero violations."""
        svg = _make_svg(title="Weekly Digest 30 items")
        path = tmp_svg(svg)
        hits = _violations(path)
        assert hits == [], f"Expected no violations, got: {hits}"

    def test_hangul_in_title_detected(self, tmp_svg):
        """Hangul characters (U+AC00..U+D7AF range) must be detected as non-ASCII."""
        svg = _make_svg(title="보안 weekly digest")
        path = tmp_svg(svg)
        hits = _violations(path)
        assert len(hits) > 0, "Hangul in <title> must be flagged"
        codepoints = {h[2] for h in hits}
        assert all(cp >= 128 for cp in codepoints), "All violations must have cp >= 128"

    def test_middle_dot_between_ascii_fails(self, tmp_svg):
        """U+00B7 between ASCII tokens MUST fail — it is non-ASCII per policy.

        Even 'AWS·GCP·Azure security' should be rejected.
        The proper separator is an ASCII hyphen or space.
        """
        svg = _make_svg(title="AWS·GCP·Azure security")
        path = tmp_svg(svg)
        hits = _violations(path)
        codepoints = {h[2] for h in hits}
        assert 0x00B7 in codepoints, (
            "U+00B7 middle-dot between ASCII tokens must still fail "
            "(positive-rule: only codepoint < 128 is allowed)"
        )

    def test_em_dash_in_title_detected(self, tmp_svg):
        """U+2014 em-dash is non-ASCII and must be detected."""
        svg = _make_svg(title="DevSecOps—Best Practices")
        path = tmp_svg(svg)
        hits = _violations(path)
        codepoints = {h[2] for h in hits}
        assert 0x2014 in codepoints

    def test_multiple_violations_all_reported(self, tmp_svg):
        """Multiple non-ASCII chars in one title are all reported."""
        svg = _make_svg(title="·•안녕")  # middle-dot, bullet, Hangul
        path = tmp_svg(svg)
        hits = _violations(path)
        assert len(hits) >= 4, f"Expected >= 4 violations, got {len(hits)}: {hits}"


# ---------------------------------------------------------------------------
# <desc> tests
# ---------------------------------------------------------------------------


class TestDescViolations:
    def test_non_ascii_in_desc_detected(self, tmp_svg):
        """Non-ASCII in <desc> must be flagged."""
        svg = _make_svg(desc="Security·Coverage")
        path = tmp_svg(svg)
        hits = _violations(path)
        codepoints = {h[2] for h in hits}
        assert 0x00B7 in codepoints, "U+00B7 in <desc> must be detected"

    def test_ascii_only_desc_passes(self, tmp_svg):
        """ASCII-only <desc> produces no violations."""
        svg = _make_svg(desc="Clean ASCII description text only.")
        path = tmp_svg(svg)
        assert _violations(path) == []

    def test_hangul_in_desc_detected(self, tmp_svg):
        """Hangul in <desc> must be detected."""
        svg = _make_svg(desc="주간 보안 요약")
        path = tmp_svg(svg)
        hits = _violations(path)
        assert len(hits) > 0, "Hangul in <desc> must be flagged"

    def test_both_elements_violations_combined(self, tmp_svg):
        """Violations in both <title> and <desc> are both reported."""
        svg = _make_svg(title="Bad·title", desc="Bad•desc")
        path = tmp_svg(svg)
        hits = _violations(path)
        codepoints = {h[2] for h in hits}
        assert 0x00B7 in codepoints
        assert 0x2022 in codepoints


# ---------------------------------------------------------------------------
# Line/column attribution
# ---------------------------------------------------------------------------


class TestViolationLocation:
    def test_violation_reports_correct_line(self, tmp_svg):
        """The reported line number must point to the <title> line."""
        content = textwrap.dedent("""\
            <svg xmlns="http://www.w3.org/2000/svg">
            <title>Clean line one</title>
            <desc>Bad · char here</desc>
            </svg>
        """)
        path = tmp_svg(content)
        hits = _violations(path)
        # desc is on line 3
        lines = {h[0] for h in hits}
        assert 3 in lines, f"Violation should be on line 3, got lines: {lines}"

    def test_violation_context_contains_surrounding_text(self, tmp_svg):
        """Context string in violation output contains text around the bad char."""
        svg = _make_svg(title="prefix·suffix")
        path = tmp_svg(svg)
        hits = _violations(path)
        assert hits, "Expected at least one violation"
        context = hits[0][4]
        assert "prefix" in context or "suffix" in context or "·" in context, (
            f"Context should contain surrounding text, got: {context}"
        )


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_empty_title_passes(self, tmp_svg):
        """An empty <title></title> is fine."""
        svg = _make_svg(title="")
        path = tmp_svg(svg)
        assert _violations(path) == []

    def test_no_title_or_desc_passes(self, tmp_svg):
        """SVG with neither <title> nor <desc> has no violations."""
        content = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'
        path = tmp_svg(content)
        assert _violations(path) == []

    def test_nonexistent_file_returns_empty(self, tmp_path):
        """Missing file returns empty violations (no crash)."""
        fake = tmp_path / "nonexistent.svg"
        assert _violations(fake) == []

    def test_ascii_high_boundary_char_127_passes(self, tmp_svg):
        """DEL (codepoint 127) is technically ASCII and must pass.

        In practice it would never appear in SVG text, but the boundary
        check is ord(c) >= 128 so 127 must not be flagged.
        """
        svg = _make_svg(title="test\x7f")
        path = tmp_svg(svg)
        assert _violations(path) == []

    def test_codepoint_128_fails(self, tmp_svg):
        """First non-ASCII codepoint (128 / U+0080) must be detected."""
        svg = _make_svg(title="test\x80")
        path = tmp_svg(svg)
        hits = _violations(path)
        assert len(hits) == 1
        assert hits[0][2] == 0x80
