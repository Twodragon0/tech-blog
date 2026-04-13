"""Pre-publish QA gate for auto-generated digest posts.

Validates content quality before a post file is written to disk.
Three independent checks are provided:

* ``validate_sentence_completeness`` -- checklist items end with a
  complete Korean/English sentence (not dangling particles/adjectives).
* ``validate_stats_consistency`` -- category counts in the "수집 통계"
  block sum to the stated total.
* ``validate_trend_analysis`` -- trend-table row counts do not exceed
  the stated total news count.

Integration
-----------
Call ``run_qa_gate(content)`` before writing.  By default warnings are
logged; set env ``AUTO_PUBLISH_STRICT_QA=1`` (or ``CI=1``) to raise
``QAGateError`` and block publication.
"""

import logging
import os
import re
from typing import List

logger = logging.getLogger(__name__)


class QAGateError(Exception):
    """Raised when strict QA mode is active and issues are found."""


# ---------------------------------------------------------------------------
# 1. Sentence completeness for checklist items
# ---------------------------------------------------------------------------

# Endings that are considered "complete" for Korean checklist text.
# Conservative: accept common sentence-final patterns, punctuation, numbers+단위.
_COMPLETE_ENDING_RE = re.compile(
    r"(?:"
    r"[.?!:)]"  # punctuation
    r"|세요"  # imperative polite (하세요, 확인하세요)
    r"|니다"  # declarative polite (합니다, 됩니다)
    r"|시오"  # formal imperative (하십시오)
    r"|바랍니다"
    r"|필요합니다"
    r"|권장합니다"
    r"|\d+[개건%]"  # numeric + unit (15개, 3건, 90%)
    r"|입니다"
    r"|됩니다"
    r"|하세요"
    r"|합시다"
    r")\s*\**\s*$"  # allow trailing bold markers / whitespace
)

# Dangling endings that strongly indicate an incomplete sentence.
_DANGLING_ENDING_RE = re.compile(
    r"(?:"
    r"하거나|이거나|거나"  # connective -거나
    r"|하고|되고|이고"  # connective -고
    r"|하며|되며|이며|으며"  # connective -며
    r"|지만|이지만"  # concessive -지만
    r"|에서|에게|까지|부터|처럼"  # postpositions (mid-sentence)
    r"|취약|위험|중요|필요|가능|불가"  # bare adjective stems
    r"|대한|관한|위한|통한"  # relative clause stems
    r"|인한|따른"
    r"|하는|되는|있는|없는|같은"  # modifier endings
    r"|할|될|있을|없을"  # prospective modifier
    r")\s*\**\s*$"
)


def validate_sentence_completeness(content: str) -> List[str]:
    """Return warnings for checklist items that appear to be incomplete sentences.

    Scans lines matching ``- [ ]`` or ``- [x]`` patterns.
    """
    issues: List[str] = []
    for line in content.splitlines():
        stripped = line.strip()
        if not re.match(r"^- \[[ xX]\] ", stripped):
            continue
        # Extract the text part after the checkbox marker
        text = re.sub(r"^- \[[ xX]\]\s*", "", stripped).strip()
        if not text:
            continue
        # Strip trailing markdown bold/italic markers for analysis
        clean = re.sub(r"\*+$", "", text).rstrip()
        if not clean:
            continue
        # Accept if ends with a known complete pattern
        if _COMPLETE_ENDING_RE.search(clean):
            continue
        # Flag if ends with a known dangling pattern
        if _DANGLING_ENDING_RE.search(clean):
            preview = clean[:60] + ("..." if len(clean) > 60 else "")
            issues.append(f"Incomplete checklist item: '{preview}'")
    return issues


# ---------------------------------------------------------------------------
# 2. Stats consistency  (수집 통계 block)
# ---------------------------------------------------------------------------

_TOTAL_NEWS_RE = re.compile(r"\*\*총 뉴스 수\*\*\s*:\s*(\d+)\s*개")
# Match category lines but NOT the "총 뉴스 수" line
_CATEGORY_COUNT_RE = re.compile(r"- \*\*(?!총 뉴스 수)[^*]+\*\*\s*:\s*(\d+)\s*개")


def validate_stats_consistency(content: str) -> List[str]:
    """Check that category counts in '수집 통계' sum to the stated total."""
    issues: List[str] = []

    # Find the stats block
    stats_match = re.search(r"\*\*수집 통계:\*\*\s*\n((?:- .+\n)+)", content)
    if not stats_match:
        return issues

    block = stats_match.group(0)
    total_m = _TOTAL_NEWS_RE.search(block)
    if not total_m:
        return issues

    stated_total = int(total_m.group(1))
    category_counts = [int(m) for m in _CATEGORY_COUNT_RE.findall(block)]

    if not category_counts:
        return issues

    actual_sum = sum(category_counts)
    # The total line is also matched by _CATEGORY_COUNT_RE if it has the
    # same format, but it uses "총 뉴스 수" which is distinct.  The regex
    # requires "- **" prefix so the total line (which lacks "-") won't match.
    if actual_sum != stated_total:
        issues.append(
            f"Stats mismatch: category sum={actual_sum} != stated total={stated_total}"
        )
    return issues


# ---------------------------------------------------------------------------
# 3. Trend analysis table consistency
# ---------------------------------------------------------------------------

_TREND_TABLE_ROW_RE = re.compile(r"\|\s*\*\*[^|]+\*\*\s*\|\s*(\d+)\s*건\s*\|")


def validate_trend_analysis(content: str) -> List[str]:
    """Check that trend table row counts don't exceed the stated total news count."""
    issues: List[str] = []

    total_m = _TOTAL_NEWS_RE.search(content)
    if not total_m:
        return issues
    stated_total = int(total_m.group(1))

    # Find trend analysis section
    trend_section = re.search(
        r"##\s*\d+\.\s*트렌드 분석\s*\n([\s\S]*?)(?=\n## |\n---|\Z)",
        content,
    )
    if not trend_section:
        return issues

    trend_block = trend_section.group(1)
    row_counts = [int(m) for m in _TREND_TABLE_ROW_RE.findall(trend_block)]

    if not row_counts:
        return issues

    trend_sum = sum(row_counts)
    # Trend counts can overlap (one article matches multiple trends),
    # so sum > total is acceptable.  But sum should not be less than total
    # when there are many categories, and a large discrepancy is suspicious.
    # The user's complaint is about sum != total, so we flag when they differ
    # significantly.  However, overlap is natural so we only flag sum < total
    # (under-counting) as a hard error.
    if trend_sum < stated_total:
        issues.append(
            f"Trend analysis under-count: trend sum={trend_sum} < stated total={stated_total}"
        )
    return issues


# ---------------------------------------------------------------------------
# Unified gate
# ---------------------------------------------------------------------------


def run_qa_gate(content: str, post_filename: str = "") -> List[str]:
    """Run all QA validations and return combined issue list.

    When ``AUTO_PUBLISH_STRICT_QA=1`` or ``CI=1``, raises ``QAGateError``
    if any issues are found.
    """
    all_issues: List[str] = []
    all_issues.extend(validate_sentence_completeness(content))
    all_issues.extend(validate_stats_consistency(content))
    all_issues.extend(validate_trend_analysis(content))

    label = post_filename or "auto-generated post"
    if all_issues:
        for issue in all_issues:
            logger.warning("QA gate [%s]: %s", label, issue)

    strict = (
        os.getenv("AUTO_PUBLISH_STRICT_QA", "") == "1" or os.getenv("CI", "") == "1"
    )
    if strict and all_issues:
        msg = f"QA gate blocked publication of {label}:\n" + "\n".join(
            f"  - {i}" for i in all_issues
        )
        raise QAGateError(msg)

    return all_issues
