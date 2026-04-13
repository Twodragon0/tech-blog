"""Tests for stats block and trend analysis consistency fixes.

Verifies that:
- _format_stats_block always produces category lines that sum to total
- _generate_trend_analysis trend table rows sum to total (via '기타' fallback)
- _generate_tech_trend_analysis trend table rows sum to total (via '기타' fallback)
"""

import re

import pytest
from news.content_generator import (
    _format_stats_block,
    _generate_tech_trend_analysis,
    _generate_trend_analysis,
)

# ===========================================================================
# _format_stats_block
# ===========================================================================

_CATEGORY_COUNT_RE = re.compile(r"- \*\*[^*]+\*\*:\s*(\d+)개")


def _parse_stats_counts(block: str) -> tuple[int, list[int]]:
    """Parse the total and category counts from a stats block."""
    total_m = re.search(r"\*\*총 뉴스 수\*\*:\s*(\d+)개", block)
    total = int(total_m.group(1)) if total_m else 0
    counts = [int(m) for m in _CATEGORY_COUNT_RE.findall(block)]
    # Remove the total from counts (it's also matched by the regex)
    # Actually "총 뉴스 수" line is also matched, so we need to skip it
    # The total line is the first one
    return total, counts[1:]  # skip the total line


class TestFormatStatsBlock:
    """_format_stats_block must produce lines that sum to total."""

    def test_all_known_categories(self):
        stats = {"security": 5, "ai": 4, "cloud": 3, "devops": 2, "blockchain": 1}
        total = 15
        block = _format_stats_block(stats, total)
        parsed_total, counts = _parse_stats_counts(block)
        assert parsed_total == 15
        assert sum(counts) == 15

    def test_with_unknown_categories_grouped_as_etc(self):
        """Items in 'tech' and 'finops' should appear under '기타 뉴스'."""
        stats = {"security": 3, "ai": 2, "tech": 4, "finops": 1}
        total = 10
        block = _format_stats_block(stats, total)
        assert "기타 뉴스" in block
        parsed_total, counts = _parse_stats_counts(block)
        assert parsed_total == 10
        assert sum(counts) == 10

    def test_only_unknown_categories(self):
        """All items are 'tech' -> only '기타 뉴스' line shown."""
        stats = {"tech": 7}
        total = 7
        block = _format_stats_block(stats, total)
        assert "기타 뉴스" in block
        assert "보안 뉴스" not in block
        parsed_total, counts = _parse_stats_counts(block)
        assert sum(counts) == 7

    def test_empty_stats(self):
        stats = {}
        total = 0
        block = _format_stats_block(stats, total)
        assert "총 뉴스 수**: 0개" in block

    def test_zero_count_known_categories_omitted(self):
        """Categories with 0 items should not produce a line."""
        stats = {"security": 5, "ai": 0, "cloud": 3}
        total = 8
        block = _format_stats_block(stats, total)
        assert "AI/ML 뉴스" not in block
        parsed_total, counts = _parse_stats_counts(block)
        assert sum(counts) == 8

    def test_assertion_on_mismatch(self):
        """If stats don't sum to total, an AssertionError is raised."""
        stats = {"security": 3}
        with pytest.raises(AssertionError, match="Stats block category sum mismatch"):
            _format_stats_block(stats, 10)

    def test_apr12_regression_15_items(self):
        """Regression: 4/12 post had total=15 but only 10 in known categories.

        With the fix, 5 'tech' items should go to '기타 뉴스'.
        """
        stats = {
            "security": 4,
            "ai": 3,
            "cloud": 2,
            "devops": 1,
            "blockchain": 0,
            "tech": 5,
        }
        total = 15
        block = _format_stats_block(stats, total)
        assert "기타 뉴스**: 5개" in block
        parsed_total, counts = _parse_stats_counts(block)
        assert sum(counts) == 15


# ===========================================================================
# Trend analysis helpers
# ===========================================================================

_TREND_ROW_RE = re.compile(r"\|\s*\*\*([^|]+)\*\*\s*\|\s*(\d+)\s*건")


def _parse_trend_rows(content: str) -> list[tuple[str, int]]:
    """Extract (name, count) from trend table rows."""
    return [(m.group(1), int(m.group(2))) for m in _TREND_ROW_RE.finditer(content)]


# ===========================================================================
# _generate_trend_analysis (security mode)
# ===========================================================================


class TestGenerateTrendAnalysis:
    """Security-mode trend analysis must account for all items."""

    def _make_items(self, titles: list[str]) -> list[dict]:
        return [{"title": t, "summary": "", "source_name": "Test"} for t in titles]

    def test_all_items_matched(self):
        """All items match known trends -> no '기타' row, sum >= total."""
        items = self._make_items(
            [
                "New AI model released",
                "Zero-day vulnerability found",
                "Cloud security breach",
            ]
        )
        content = _generate_trend_analysis(items, 1)
        rows = _parse_trend_rows(content)
        # Overlap possible, sum >= total
        assert sum(c for _, c in rows) >= 3
        # No '기타' row since all items matched
        etc_rows = [r for r in rows if r[0] == "기타"]
        assert len(etc_rows) == 0

    def test_unmatched_items_go_to_etc(self):
        """Items not matching any trend keyword -> '기타' row."""
        items = self._make_items(
            [
                "New AI model released",
                "Company quarterly earnings report",
                "Local sports team wins championship",
            ]
        )
        content = _generate_trend_analysis(items, 1)
        rows = _parse_trend_rows(content)
        total_trend = sum(c for _, c in rows)
        assert total_trend == 3
        # Check '기타' exists
        etc_rows = [r for r in rows if r[0] == "기타"]
        assert len(etc_rows) == 1
        assert etc_rows[0][1] == 2

    def test_all_unmatched(self):
        """No items match any trend -> single '기타' row."""
        items = self._make_items(
            [
                "Company quarterly earnings report",
                "Local sports update",
            ]
        )
        content = _generate_trend_analysis(items, 1)
        rows = _parse_trend_rows(content)
        assert len(rows) == 1
        assert rows[0][0] == "기타"
        assert rows[0][1] == 2

    def test_empty_items(self):
        """No items -> no trend table."""
        content = _generate_trend_analysis([], 1)
        rows = _parse_trend_rows(content)
        assert len(rows) == 0

    def test_apr12_regression_15_items(self):
        """Regression: with 15 items, trend sum must equal 15."""
        items = self._make_items(
            [
                "AI vulnerability scanner released",
                "Zero-day exploit in Chrome",
                "AWS cloud security update",
                "Supply chain attack detected",
                "Ransomware targets hospitals",
                "Kubernetes container escape",
                "Authentication bypass CVE",
                "New machine learning framework",
                "GCP infrastructure change",
                "Docker security patch",
                "Company blog post about culture",
                "Open source project launch",
                "Developer conference recap",
                "Budget planning for Q3",
                "Team building event highlights",
            ]
        )
        content = _generate_trend_analysis(items, 1)
        rows = _parse_trend_rows(content)
        total_trend = sum(c for _, c in rows)
        assert total_trend == 15


# ===========================================================================
# _generate_tech_trend_analysis
# ===========================================================================


class TestGenerateTechTrendAnalysis:
    """Tech-blog trend analysis must account for all items."""

    def _make_items(self, titles: list[str]) -> list[dict]:
        return [{"title": t, "summary": "", "source_name": "Test"} for t in titles]

    def test_all_items_matched(self):
        """All items match known trends -> sum >= total (overlap possible), no '기타'."""
        items = self._make_items(
            [
                "New AI model from OpenAI",
                "Kubernetes best practices",
                "Rust programming guide",
            ]
        )
        content = _generate_tech_trend_analysis(items, 1)
        rows = _parse_trend_rows(content)
        # Overlap is possible (item matches multiple trends), so sum >= total
        assert sum(c for _, c in rows) >= 3
        # No '기타' row since all items matched at least one trend
        etc_rows = [r for r in rows if r[0] == "기타"]
        assert len(etc_rows) == 0

    def test_unmatched_items_go_to_etc(self):
        items = self._make_items(
            [
                "New AI model from OpenAI",
                "Company quarterly earnings",
                "Local news update",
            ]
        )
        content = _generate_tech_trend_analysis(items, 1)
        rows = _parse_trend_rows(content)
        total_trend = sum(c for _, c in rows)
        assert total_trend == 3
        etc_rows = [r for r in rows if r[0] == "기타"]
        assert len(etc_rows) == 1
        assert etc_rows[0][1] == 2

    def test_empty_items(self):
        content = _generate_tech_trend_analysis([], 1)
        rows = _parse_trend_rows(content)
        assert len(rows) == 0
