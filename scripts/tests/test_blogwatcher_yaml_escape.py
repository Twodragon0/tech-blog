"""Regression tests for the YAML-escape fix in scripts.news.content_generator.

Auto-published digest titles can contain Korean post-quoted phrases like
\"Sorry\" — those inner double-quotes used to land directly inside the YAML
frontmatter's double-quoted scalars and break Jekyll's parser with

    YAML Exception ... did not find expected key while parsing a block
    mapping at line 2 column 1

(Real example: 2026-05-03-Tech_Security_Weekly_Digest_Ransomware_Azure_CVE_Vulnerability.md)

These tests pin the contract so the bug can't silently come back.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from news.content_generator import (  # noqa: E402
    _yaml_escape_dq,
    generate_post_content,
)


class TestYamlEscapeDq:
    """The helper itself — quote/backslash escaping in double-quoted scalars."""

    def test_escapes_inner_double_quote(self):
        assert _yaml_escape_dq('cPanel "Sorry" 취약점') == 'cPanel \\"Sorry\\" 취약점'

    def test_escapes_backslash_first(self):
        # Backslashes must be escaped before quotes so we don't double-escape
        # `\"` into `\\\"` and break parsing.
        assert _yaml_escape_dq('path\\with\\backslash') == 'path\\\\with\\\\backslash'

    def test_escapes_backslash_then_quote(self):
        # Mixed input — both pass through correctly in either order.
        assert _yaml_escape_dq(r'a\"b') == 'a\\\\\\"b'

    def test_passes_through_plain_string(self):
        assert _yaml_escape_dq("normal text without quotes") == "normal text without quotes"

    def test_passes_through_korean_no_quotes(self):
        # Korean post-quote characters (｜ 「 『 etc.) aren't ASCII " so they
        # don't need escaping — verify we don't over-escape.
        assert _yaml_escape_dq("한글 「인용」 텍스트") == "한글 「인용」 텍스트"


class TestFrontmatterYamlRoundTrip:
    """Integration: rendered post must yaml.safe_load cleanly even when the
    upstream news payload contains adversarial quote characters.

    The historical failure mode is that yaml.safe_load raises and Jekyll
    silently skips the post — these tests catch that the moment a generator
    change lets a bare `"` slip through.
    """

    @staticmethod
    def _extract_frontmatter(content: str) -> dict:
        # `---\n...\n---\n` envelope, take the inner block and load as YAML.
        assert content.startswith("---\n"), "post must start with frontmatter delimiter"
        end = content.index("\n---\n", 4)
        return yaml.safe_load(content[4:end])

    @pytest.fixture
    def quote_laden_payload(self):
        """News selection that mirrors the 2026-05-03 production failure —
        title fragments injected from the upstream feed contain inner
        double-quotes, which used to break the resulting frontmatter."""
        date = datetime(2026, 5, 3, 11, 1, 23, tzinfo=timezone.utc)
        selected = [
            {
                "title": 'Critical cPanel vulnerability "Sorry" exploit found',
                "summary": "RCE chain bypassing auth.",
                "url": "https://example.com/cpanel-sorry",
                "source": "BleepingComputer",
                "categories": ["security"],
                "published": date,
            },
            {
                "title": 'Trellix discovers "ConsentFix v3" attack',
                "summary": "Adversary-in-the-middle phishing with browser injection.",
                "url": "https://example.com/trellix",
                "source": "The Hacker News",
                "categories": ["security"],
                "published": date,
            },
        ] * 8  # pad to >=15 to satisfy any min-news guards
        return selected, date

    def test_security_digest_yaml_parses_with_inner_quotes(self, quote_laden_payload):
        selected, date = quote_laden_payload
        categorized = {"security": selected, "devsecops": [], "cloud": [], "tech": []}
        content = generate_post_content(
            selected, categorized, date, "Ransomware Azure CVE Vulnerability"
        )
        # The bug: yaml.safe_load raises on unescaped inner `"`.
        # The fix: round-trip succeeds and the parsed values still contain
        # the literal quote characters from the source headlines.
        fm = self._extract_frontmatter(content)
        assert fm["layout"] == "post"
        assert isinstance(fm["title"], str)
        assert isinstance(fm["excerpt"], str)
        assert isinstance(fm["description"], str)
        assert isinstance(fm["image_alt"], str)

    def test_no_bare_double_quote_inside_title_value(self, quote_laden_payload):
        """Defense-in-depth: even if some other parser besides PyYAML reads
        the file, the rendered `title:` line should never have an unescaped
        `"` between its outer quotes."""
        selected, date = quote_laden_payload
        categorized = {"security": selected, "devsecops": [], "cloud": [], "tech": []}
        content = generate_post_content(
            selected, categorized, date, "Ransomware Azure CVE Vulnerability"
        )
        # Pull the literal title line as bytes (not yaml-parsed) and check
        # quote balance: opening quote + escaped pairs + closing quote.
        for line_prefix in ("title:", "excerpt:", "description:", "image_alt:"):
            line = next(
                line for line in content.splitlines() if line.startswith(line_prefix)
            )
            # Strip leading "title: " then check the remaining is a balanced
            # double-quoted YAML scalar — count unescaped `"`.
            value = line[len(line_prefix):].strip()
            assert value.startswith('"') and value.endswith('"'), (
                f"{line_prefix} value not wrapped in double-quotes: {line!r}"
            )
            inner = value[1:-1]
            # An unescaped `"` is one preceded by zero or an even number of `\`
            # — find any and assert there are none.
            i = 0
            while i < len(inner):
                if inner[i] == '"':
                    # walk back across `\` to determine escape parity
                    bs_run = 0
                    j = i - 1
                    while j >= 0 and inner[j] == "\\":
                        bs_run += 1
                        j -= 1
                    assert bs_run % 2 == 1, (
                        f"unescaped `\"` at offset {i} in {line_prefix} value: {line!r}"
                    )
                i += 1
