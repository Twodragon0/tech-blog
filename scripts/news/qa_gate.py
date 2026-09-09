"""Pre-publish QA gate for auto-generated digest posts.

Validates content quality before a post file is written to disk.
Three independent checks are provided:

* ``validate_sentence_completeness`` -- checklist items end with a
  complete Korean/English sentence (not dangling particles/adjectives).
* ``validate_stats_consistency`` -- category counts in the "수집 통계"
  block sum to the stated total.
* ``validate_trend_analysis`` -- every trend the prose cites exists as a
  row in the trend table.

Integration
-----------
Call ``run_qa_gate(content)`` before writing.  By default warnings are
logged; set env ``AUTO_PUBLISH_STRICT_QA=1`` to raise ``QAGateError`` and
block publication.  That is the ONLY switch — a ``CI=1`` clause used to sit
beside it and never fired (Actions sets ``CI=true``), and enabling it would
have promoted two rules that were deliberately left advisory.  See
``run_qa_gate`` for the measurements.

Note that ``validate_stats_consistency`` blocks the publish on its own,
independently of this flag: ``auto_publish_news`` acts on its findings with a
self-heal in front (``heal_stats_total``).
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


def heal_stats_total(content: str) -> "str | None":
    """Rewrite ``총 뉴스 수`` to the sum of the category lines. None = refuse.

    The self-heal for the blocking stats gate, and deliberately narrow. The
    only repair that introduces no guess is to re-derive the total from the
    per-category counts the block already carries — the same direction the
    generator derives it (``total = sum(stats.values())``).

    IT REFUSES WHEN A CATEGORY SITS EXACTLY AT ``MAX_NEWS_PER_CATEGORY``.
    That is the fingerprint of the historical defect: the 23 grandfathered
    posts from 2026-02..04 reported CAPPED per-category counts against an
    uncapped total, which is why ``stated - sum`` is ``{+5: 22, -5: 1}``
    regardless of post size. Healing that shape would silently UNDERSTATE the
    collected count — a content regression dressed as a repair. Refusing means
    the caller blocks, which is the honest outcome when the right total is not
    recoverable.

    Returns the repaired content, or None when it declines. Never raises: the
    caller's bare re-verify decides the outcome either way.
    """
    from scripts.news.config import MAX_NEWS_PER_CATEGORY

    stats_match = re.search(r"\*\*수집 통계:\*\*\s*\n((?:- .+\n)+)", content)
    if not stats_match:
        return None
    block = stats_match.group(0)

    total_m = _TOTAL_NEWS_RE.search(block)
    if not total_m:
        return None
    category_counts = [int(m) for m in _CATEGORY_COUNT_RE.findall(block)]
    if not category_counts:
        return None
    if any(c == MAX_NEWS_PER_CATEGORY for c in category_counts):
        return None

    corrected = sum(category_counts)
    if corrected == int(total_m.group(1)):
        return None

    healed_block = block.replace(total_m.group(0), f"**총 뉴스 수**: {corrected}개", 1)
    return content.replace(block, healed_block, 1)


# ---------------------------------------------------------------------------
# 3. Trend analysis table consistency
# ---------------------------------------------------------------------------

_TREND_TABLE_ROW_RE = re.compile(r"\|\s*\*\*([^|*]+)\*\*\s*\|\s*(\d+)\s*건\s*\|")
_TREND_SECTION_RE = re.compile(
    r"##\s*\d+\.\s*트렌드 분석\s*\n([\s\S]*?)(?=\n## |\n---|\Z)"
)
# Every "**name**(N건)" the prose cites, not just the first: a post may headline
# two trends ("**A**(2건)와 **B**(4건)입니다").
_TREND_CITATION_RE = re.compile(r"\*\*([^*]+)\*\*\s*\((\d+)건\)")


def _trend_prose(block: str) -> str:
    """The prose after the table.

    Sliced at the last LINE that is a table row, not at the last ``|``
    CHARACTER. A markdown table row starts its line with ``|``, so this asks
    the grammar where the table ends instead of guessing from a character that
    also occurs in prose.

    Why it matters: an article title reaches this prose verbatim through
    ``content_generator._extract_trend_keyword``, and tech headlines routinely
    contain a pipe. Measured 2026-09-08 with ``랜섬웨어 | 이중 협박 재확산`` as a
    title, ``rfind("|")`` put the boundary INSIDE the prose and dropped the
    first citation:

        prose  '이중 협박 재확산 등이 주요 이슈입니다. **기타**(1건)도 …'
        cites  [('기타', 1)]          # **랜섬웨어**(1건) never seen

    The gate then reported 0 issues for a post it had only half-read — the
    vacuity failure mode, where nothing-found reads exactly like nothing-wrong.

    Zero effect on the corpus as it stands: 195 citations over 176 posts either
    way, 0 posts change. So this is a latent-vacuity fix, not a live-defect fix,
    and the ``MAX_VIOLATIONS = 0`` ratchet was not being fooled today.
    """
    lines = block.splitlines()
    last_row = -1
    for i, line in enumerate(lines):
        if line.lstrip().startswith("|"):
            last_row = i
    return "\n".join(lines[last_row + 1 :])


def extract_trend_rows_and_citations(
    content: str,
) -> "tuple[set[tuple[str, int]], list[tuple[str, int]]]":
    """The gate's own extractor, exposed so the generator can assert on it.

    Returned as ``(rows, citations)``. ``citations`` is a LIST, not a set: the
    generator needs the count to detect a citation that went missing from the
    prose slice, which a set would hide by deduplicating.

    Public so that ``content_generator`` asserts against the same code the gate
    runs. A parallel re-implementation there could agree with the generator
    while disagreeing with the gate, which is the drift this replaces.
    """
    section = _TREND_SECTION_RE.search(content)
    if not section:
        return set(), []
    block = section.group(1)

    rows = {
        (name.strip(), int(count)) for name, count in _TREND_TABLE_ROW_RE.findall(block)
    }
    if not rows:
        return set(), []

    # Only the prose AFTER the table. Scanning the whole block would match the
    # rows' own bold names and make every citation trivially present.
    citations = [
        (name.strip(), int(count))
        for name, count in _TREND_CITATION_RE.findall(_trend_prose(block))
    ]
    return rows, citations


def validate_trend_analysis(content: str) -> List[str]:
    """Every trend the prose cites must exist as a row in the trend table.

    The prose under the table headlines one or two trends by name and count
    ("이번 주기의 핵심 트렌드는 **공급망 공격 및 RCE 취약점**(3건)입니다"). If that
    citation does not match a row, the reader is told about a trend the table
    contradicts.

    WHAT THIS REPLACED, AND WHY
    ---------------------------
    Until 2026-09-08 this function flagged ``trend_sum < 총 뉴스 수``. That
    premise is not an invariant of this generator, and the rule fired on **140
    of 216** published digests. Two distortions make the two numbers
    incomparable by design: a trend count DOUBLE-COUNTS an article that matches
    several trends, while the trend analysis itself runs over a list capped by
    ``MAX_NEWS_PER_CATEGORY``. Measured three ways over the 179 posts that carry
    both numbers — ``== 총 뉴스 수`` held for 32, ``== 본문 항목 수`` for 26, and
    even the loosest ``>= 본문 항목 수`` for only 162. There was no threshold to
    fix, so the rule went rather than being tuned.

    The noise had teeth: ``run_qa_gate`` raises under ``AUTO_PUBLISH_STRICT_QA=1``
    or ``CI=1``, and this rule alone would have blocked the 2026-09-08 publish
    (``trend sum=20 < stated total=23``) had either been set.

    WHY NOT "the claim must be the table's TOP row"
    -----------------------------------------------
    That was the first replacement drafted, and the corpus rejected it: 168 of
    173 conformed, which looked strong, but the 5 exceptions were hand-edited
    posts making a BETTER editorial choice than the generator's ``max()``.
    2026-04-13 headlines ``공급망 공격 및 RCE 취약점``(3건) over the numerically
    larger ``Bitcoin 및 블록체인 동향``(5건) — correct for a security digest — and
    2026-04-12's numeric top is the catch-all ``기타``(5건), which should never
    be headlined. The 168/173 was measuring conformance to the generator, not
    the absence of a defect.

    Requiring only that the citation EXISTS as a row keeps that editorial
    freedom and still catches the real contradiction: 169/173 hold, and the 4
    that do not cite a trend the table does not contain (``블록체인 규제 리스크``
    against a ``블록체인/규제`` row, or ``북한 연계 대형 해킹``(1건) against no
    such row at all).

    Count-only ("some row has this count") is deliberately NOT the rule: it
    holds for 173/173, so it carries no signal.

    Verdict and measurements:
    .omc/plans/validate-trend-analysis-verdict-2026-09-08.md
    """
    issues: List[str] = []

    rows, citations = extract_trend_rows_and_citations(content)
    if not rows:
        return issues

    for cited in citations:
        if cited not in rows:
            issues.append(
                f"Trend citation not in the table: {cited[0]}({cited[1]}건) — "
                f"rows are {sorted(rows, key=lambda r: -r[1])}"
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

    # ONE explicit switch. There used to be a second clause,
    # `os.getenv("CI", "") == "1"`, and it never fired: GitHub Actions sets
    # `CI=true`, and the blogwatcher workflow sets neither variable. Proven by
    # outcome rather than by reading the docs — before the trend rule was
    # replaced, this function returned an issue for the 2026-09-08 content and
    # that publish SUCCEEDED, so `strict` was False in Actions.
    #
    # It was removed rather than "fixed" to truthy, because turning it on is not
    # an env-var correction — it is a silent double promotion. Measured: the
    # stats rule is ALREADY blocking on its own (with a self-heal that refuses
    # the capped shape), so strict would only re-raise it while skipping that
    # heal; and the two rules left, validate_trend_analysis and
    # validate_sentence_completeness, were deliberately NOT promoted and carry
    # no self-heal. `INLINE_PUBLISH_GATES` lists run_qa_gate as blocking=False,
    # so its `blocking => self_heal` invariant would not catch that bypass.
    #
    # Verdict: .omc/plans/run-qa-gate-ci-detection-2026-09-08.md
    strict = os.getenv("AUTO_PUBLISH_STRICT_QA", "") == "1"
    if strict and all_issues:
        msg = f"QA gate blocked publication of {label}:\n" + "\n".join(
            f"  - {i}" for i in all_issues
        )
        raise QAGateError(msg)

    return all_issues
