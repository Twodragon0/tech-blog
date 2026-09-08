"""Unit tests for the pre-publish QA gate (scripts.news.qa_gate).

Covers:
- validate_sentence_completeness: incomplete / complete checklist items
- validate_stats_consistency: category sum vs stated total
- validate_trend_analysis: trend table sum vs stated total
- run_qa_gate: strict mode (AUTO_PUBLISH_STRICT_QA only) raises QAGateError
"""

import os
import re
from pathlib import Path

import pytest
from news import qa_gate
from news.qa_gate import (
    QAGateError,
    run_qa_gate,
    validate_sentence_completeness,
    validate_stats_consistency,
    validate_trend_analysis,
)

# ===========================================================================
# validate_sentence_completeness
# ===========================================================================


class TestSentenceCompleteness:
    """Checklist items must end with complete sentences."""

    def test_complete_imperative(self):
        """Items ending with -하세요 are OK."""
        content = "- [ ] 영향받는 시스템 버전을 확인하고 패치 적용 일정을 수립하세요.\n"
        assert validate_sentence_completeness(content) == []

    def test_complete_declarative(self):
        """Items ending with -니다 are OK."""
        content = "- [ ] 보안 패치가 필요합니다.\n"
        assert validate_sentence_completeness(content) == []

    def test_complete_with_period(self):
        """Items ending with period are OK."""
        content = "- [ ] EDR/SIEM에서 IoC 기반 탐지 룰을 업데이트하세요.\n"
        assert validate_sentence_completeness(content) == []

    def test_complete_with_count(self):
        """Items ending with number + unit are OK."""
        content = "- [ ] 총 15개\n"
        assert validate_sentence_completeness(content) == []

    def test_complete_with_colon(self):
        """Items ending with colon are OK."""
        content = "- [ ] 확인 필요:\n"
        assert validate_sentence_completeness(content) == []

    def test_incomplete_dangling_adjective(self):
        """Real-world failure: sentence ending with bare adjective '취약'."""
        content = "- [ ] **CVE-2026-1234** 관련 시스템이 지속적으로 취약\n"
        issues = validate_sentence_completeness(content)
        assert len(issues) == 1
        assert "Incomplete checklist item" in issues[0]

    def test_incomplete_dangling_connector_gorena(self):
        """Sentence ending with connective -거나."""
        content = "- [ ] 패치를 적용하거나\n"
        issues = validate_sentence_completeness(content)
        assert len(issues) == 1

    def test_incomplete_dangling_connector_hago(self):
        """Sentence ending with connective -하고."""
        content = "- [ ] 보안 정책을 검토하고\n"
        issues = validate_sentence_completeness(content)
        assert len(issues) == 1

    def test_incomplete_dangling_modifier_haneun(self):
        """Sentence ending with modifier -하는."""
        content = "- [ ] 클라우드 인프라를 점검하는\n"
        issues = validate_sentence_completeness(content)
        assert len(issues) == 1

    def test_incomplete_dangling_wihan(self):
        """Sentence ending with relative stem -위한."""
        content = "- [ ] 보안 강화를 위한\n"
        issues = validate_sentence_completeness(content)
        assert len(issues) == 1

    def test_bold_title_with_complete_ending(self):
        """Bold-wrapped title followed by complete advice."""
        content = "- [ ] **북한 해커 그룹** 관련 보안 영향도 분석 및 모니터링 강화\n"
        # '강화' is a bare noun but NOT in our dangling list; it could be
        # a false positive.  We accept it because it's a common action noun.
        issues = validate_sentence_completeness(content)
        # This should NOT be flagged - '강화' is not in dangling list
        assert issues == []

    def test_multiple_items_mixed(self):
        """Mix of complete and incomplete items."""
        content = (
            "- [ ] 패치 적용 일정을 수립하세요.\n"
            "- [ ] 시스템이 지속적으로 취약\n"
            "- [x] 보안 점검 완료.\n"
            "- [ ] 인프라를 검토하는\n"
        )
        issues = validate_sentence_completeness(content)
        assert len(issues) == 2

    def test_non_checklist_lines_ignored(self):
        """Regular lines (not checklist) should be ignored."""
        content = "이것은 일반 문장이고 끝이 취약\n- 일반 목록 항목\n"
        assert validate_sentence_completeness(content) == []

    def test_empty_checklist_item(self):
        """Empty checklist item should be ignored."""
        content = "- [ ] \n"
        assert validate_sentence_completeness(content) == []


# ===========================================================================
# validate_stats_consistency
# ===========================================================================


class TestStatsConsistency:
    """Category counts must sum to the stated total."""

    STATS_OK = (
        "**수집 통계:**\n"
        "- **총 뉴스 수**: 15개\n"
        "- **보안 뉴스**: 5개\n"
        "- **AI/ML 뉴스**: 4개\n"
        "- **클라우드 뉴스**: 3개\n"
        "- **DevOps 뉴스**: 2개\n"
        "- **블록체인 뉴스**: 1개\n"
    )

    STATS_MISMATCH = (
        "**수집 통계:**\n"
        "- **총 뉴스 수**: 15개\n"
        "- **보안 뉴스**: 3개\n"
        "- **AI/ML 뉴스**: 4개\n"
        "- **클라우드 뉴스**: 2개\n"
        "- **DevOps 뉴스**: 1개\n"
        "- **블록체인 뉴스**: 0개\n"
    )

    def test_consistent_stats(self):
        assert validate_stats_consistency(self.STATS_OK) == []

    def test_inconsistent_stats(self):
        issues = validate_stats_consistency(self.STATS_MISMATCH)
        assert len(issues) == 1
        assert "Stats mismatch" in issues[0]
        assert "sum=10" in issues[0]
        assert "total=15" in issues[0]

    def test_no_stats_block(self):
        """Content without stats block should pass."""
        assert validate_stats_consistency("No stats here\n") == []

    def test_tech_blog_stats(self):
        """Tech-blog style stats with different category names."""
        content = (
            "**수집 통계:**\n"
            "- **총 뉴스 수**: 12개\n"
            "- **AI/ML**: 5개\n"
            "- **DevOps/Cloud**: 4개\n"
            "- **Open Source**: 2개\n"
            "- **General**: 1개\n"
        )
        assert validate_stats_consistency(content) == []

    def test_tech_blog_stats_mismatch(self):
        content = (
            "**수집 통계:**\n"
            "- **총 뉴스 수**: 20개\n"
            "- **AI/ML**: 5개\n"
            "- **DevOps/Cloud**: 4개\n"
            "- **Open Source**: 2개\n"
            "- **General**: 1개\n"
        )
        issues = validate_stats_consistency(content)
        assert len(issues) == 1
        assert "sum=12" in issues[0]
        assert "total=20" in issues[0]


# ===========================================================================
# validate_trend_analysis
# ===========================================================================


class TestTrendAnalysis:
    """Every trend the prose cites must exist as a row in the trend table.

    Replaced the old ``trend_sum < 총 뉴스 수`` rule on 2026-09-08: that premise
    fired on 140 of 216 published digests because a trend count double-counts an
    article matching several trends while the analysis runs over a capped
    subset — the two numbers are incomparable by design. See
    ``validate_trend_analysis``'s docstring for the three measurements that
    ruled out tuning it, and for why "must be the table's TOP row" was rejected
    too (it flagged hand-edited posts that headline a better trend than
    ``max()`` picks).
    """

    _TABLE = (
        "## 5. 트렌드 분석\n\n"
        "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        "|--------|-------------|------------|\n"
        "| **공급망 공격** | 3건 | RCE, CVE |\n"
        "| **블록체인 동향** | 5건 | Bitcoin |\n"
        "| **기타** | 2건 | 기타 주제 |\n"
    )

    def test_a_non_top_row_is_allowed(self):
        """The editorial choice this rule exists to preserve.

        2026-04-13 headlines 공급망 공격(3건) over the larger 블록체인 동향(5건),
        which is right for a security digest. A "must be the top row" rule
        flagged that and four other correct posts.
        """
        content = self._TABLE + "\n핵심 트렌드는 **공급망 공격**(3건)입니다.\n"
        assert validate_trend_analysis(content) == []

    def test_two_cited_trends_both_checked(self):
        content = (
            self._TABLE
            + "\n핵심 트렌드는 **공급망 공격**(3건)와 **블록체인 동향**(5건)입니다.\n"
        )
        assert validate_trend_analysis(content) == []

    def test_a_name_the_table_does_not_carry_is_flagged(self):
        """The real corpus defect: 블록체인 규제 리스크 against a 블록체인/규제 row."""
        content = self._TABLE + "\n핵심 트렌드는 **공급망 침해**(3건)입니다.\n"
        issues = validate_trend_analysis(content)
        assert len(issues) == 1, issues
        assert "Trend citation not in the table" in issues[0]
        assert "공급망 침해(3건)" in issues[0]

    def test_a_count_that_does_not_match_its_row_is_flagged(self):
        content = self._TABLE + "\n핵심 트렌드는 **공급망 공격**(9건)입니다.\n"
        issues = validate_trend_analysis(content)
        assert len(issues) == 1, issues
        assert "공급망 공격(9건)" in issues[0]

    def test_only_the_prose_after_the_table_is_scanned(self):
        """Control against a vacuous rule.

        Scanning the whole section would match the rows' own bold names, so
        every citation would be trivially present and the check would never
        fire. This fixture puts a bogus citation only in the prose.
        """
        content = self._TABLE + "\n**존재하지 않는 트렌드**(1건)이 주목됩니다.\n"
        assert validate_trend_analysis(content) != []

    def test_no_trend_section_passes(self):
        assert validate_trend_analysis("- **총 뉴스 수**: 10개\n본문\n") == []

    def test_a_table_with_no_prose_citation_passes(self):
        """Nothing to contradict."""
        assert validate_trend_analysis(self._TABLE) == []

    def test_the_old_undercount_rule_is_gone(self):
        """A post whose trend sum is under the stated total must now pass.

        Pinned because reinstating that comparison would re-block roughly two
        thirds of the corpus, and under strict mode it would have blocked the
        2026-09-08 publish on its own.
        """
        content = (
            "- **총 뉴스 수**: 30개\n\n"
            + self._TABLE
            + "\n핵심 트렌드는 **블록체인 동향**(5건)입니다.\n"
        )
        assert validate_trend_analysis(content) == []


# ===========================================================================
# run_qa_gate (integration + strict mode)
# ===========================================================================


class TestRunQAGate:
    """Integration tests for the unified QA gate."""

    def test_clean_content_returns_empty(self):
        content = (
            "**수집 통계:**\n"
            "- **총 뉴스 수**: 5개\n"
            "- **보안 뉴스**: 3개\n"
            "- **AI/ML 뉴스**: 2개\n"
            "\n"
            "## 3. 트렌드 분석\n\n"
            "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
            "|--------|-------------|------------|\n"
            "| **보안** | 3건 | CVE |\n"
            "| **AI** | 2건 | GPT |\n"
            "\n"
            "- [ ] 보안 패치를 확인하세요.\n"
        )
        assert run_qa_gate(content) == []

    def test_multiple_issues_collected(self):
        content = (
            "**수집 통계:**\n"
            "- **총 뉴스 수**: 15개\n"
            "- **보안 뉴스**: 3개\n"
            "- **AI/ML 뉴스**: 2개\n"
            "\n"
            "- [ ] 시스템이 지속적으로 취약\n"
        )
        issues = run_qa_gate(content, "test-post.md")
        assert len(issues) >= 2  # stats mismatch + incomplete sentence

    def test_strict_mode_raises(self, monkeypatch):
        monkeypatch.setenv("AUTO_PUBLISH_STRICT_QA", "1")
        monkeypatch.setenv("CI", "")
        content = (
            "**수집 통계:**\n"
            "- **총 뉴스 수**: 15개\n"
            "- **보안 뉴스**: 3개\n"
            "- **AI/ML 뉴스**: 2개\n"
        )
        with pytest.raises(QAGateError, match="QA gate blocked"):
            run_qa_gate(content, "strict-test.md")

    def test_ci_alone_no_longer_raises(self, monkeypatch):
        """Retargeted, not deleted, on 2026-09-08.

        This used to assert that ``CI=1`` raises. That clause was removed: it
        never fired in Actions (which sets ``CI=true``), and switching it to a
        truthy check would have promoted ``validate_trend_analysis`` and
        ``validate_sentence_completeness`` — both deliberately left advisory,
        both without a self-heal — as a side effect.

        Deleting the case would have retired the coverage silently, so it now
        pins the new contract: CI alone does NOT block. Both spellings are
        checked because ``true`` is what the platform actually sets and ``1``
        is what this repo's own docs suggest.
        """
        monkeypatch.setenv("AUTO_PUBLISH_STRICT_QA", "")
        content = "- [ ] 시스템이 지속적으로 취약\n"
        for ci_value in ("1", "true"):
            monkeypatch.setenv("CI", ci_value)
            issues = run_qa_gate(content)
            assert issues, f"fixture stopped being a violation (CI={ci_value})"

    def test_strict_env_still_raises_on_the_same_content(self, monkeypatch):
        """Control for the test above.

        Without it, "CI does not raise" would pass just as well for a strict
        path that raises for nothing at all.
        """
        monkeypatch.setenv("CI", "1")
        monkeypatch.setenv("AUTO_PUBLISH_STRICT_QA", "1")
        with pytest.raises(QAGateError):
            run_qa_gate("- [ ] 시스템이 지속적으로 취약\n")

    def test_the_strict_switch_stays_single_and_ci_free(self):
        """The point of the removal, guarded at the source.

        The runtime tests above only prove that CI does not raise TODAY. The
        failure mode is someone reading ``== "1"`` as a bug, switching it to a
        truthy check, and thereby promoting two advisory rules that have no
        self-heal. This makes that edit fail instead of shipping.

        Anchored on the assignment rather than the whole file so an unrelated
        mention of CI in a comment does not trip it.
        """
        source = Path(qa_gate.__file__).read_text(encoding="utf-8")
        match = re.search(r"^\s*strict = (.+)$", source, re.M)
        assert match, "the strict switch was renamed or removed"
        expression = match.group(1)
        assert expression == 'os.getenv("AUTO_PUBLISH_STRICT_QA", "") == "1"', (
            f"the strict switch changed to {expression!r}. If a CI clause is "
            "being re-added, that is a promotion of validate_trend_analysis and "
            "validate_sentence_completeness — decide it explicitly and give "
            "them self-heals first (see INLINE_PUBLISH_GATES)."
        )

    def test_warn_mode_does_not_raise(self, monkeypatch):
        monkeypatch.setenv("AUTO_PUBLISH_STRICT_QA", "")
        monkeypatch.setenv("CI", "")
        content = "- [ ] 시스템이 지속적으로 취약\n"
        issues = run_qa_gate(content)
        assert len(issues) == 1  # warning only, no exception


# ===========================================================================
# Real-world regression samples from 4/12, 4/13 posts
# ===========================================================================


class TestRealWorldRegressions:
    """Samples based on actual issues found in April 2026 auto-published posts."""

    def test_apr12_incomplete_checklist(self):
        """4/12 post had checklist item ending with '취약'."""
        content = "- [ ] **CVE-2026-XXXX** 관련 시스템이 지속적으로 취약\n"
        issues = validate_sentence_completeness(content)
        assert len(issues) == 1

    def test_apr12_stats_mismatch(self):
        """4/12 post: total=15 but categories summed to 10."""
        content = (
            "**수집 통계:**\n"
            "- **총 뉴스 수**: 15개\n"
            "- **보안 뉴스**: 4개\n"
            "- **AI/ML 뉴스**: 3개\n"
            "- **클라우드 뉴스**: 2개\n"
            "- **DevOps 뉴스**: 1개\n"
            "- **블록체인 뉴스**: 0개\n"
        )
        issues = validate_stats_consistency(content)
        assert len(issues) == 1
        assert "sum=10" in issues[0]

    def test_apr13_trend_citation_now_governs_that_post(self):
        """4/13 used to be pinned against the retired trend-sum rule.

        That post's real shape is a prose citation of 공급망 공격 및 RCE
        취약점(3건) while the numerically largest row is Bitcoin 및 블록체인
        동향(5건) — an editorial choice, not a defect, and the live post passes
        (TestAprilDigestRegression asserts zero issues on it). What IS a defect
        for that shape is a citation the table does not carry, so the fixture is
        retargeted rather than deleted: deleting it would retire the regression
        silently.
        """
        table = (
            "## 5. 트렌드 분석\n\n"
            "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
            "|--------|-------------|------------|\n"
            "| **공급망 공격 및 RCE 취약점** | 3건 | supply chain |\n"
            "| **Bitcoin 및 블록체인 동향** | 5건 | Bitcoin |\n"
        )
        headline_non_top = (
            table + "\n핵심 트렌드는 **공급망 공격 및 RCE 취약점**(3건)입니다.\n"
        )
        assert validate_trend_analysis(headline_non_top) == []

        phantom = table + "\n핵심 트렌드는 **북한 연계 대형 해킹**(1건)입니다.\n"
        issues = validate_trend_analysis(phantom)
        assert len(issues) == 1, issues
        assert "북한 연계 대형 해킹(1건)" in issues[0]

    def test_normal_post_no_false_positive(self):
        """A well-formed post should produce zero issues."""
        content = (
            "**수집 통계:**\n"
            "- **총 뉴스 수**: 10개\n"
            "- **보안 뉴스**: 5개\n"
            "- **AI/ML 뉴스**: 3개\n"
            "- **클라우드 뉴스**: 2개\n"
            "\n---\n\n"
            "## 5. 트렌드 분석\n\n"
            "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
            "|--------|-------------|------------|\n"
            "| **AI/LLM** | 5건 | GPT, Claude |\n"
            "| **보안** | 4건 | CVE, 패치 |\n"
            "| **클라우드** | 3건 | AWS |\n"
            "\n---\n\n"
            "## 실무 체크리스트\n\n"
            "- [ ] 보안 패치를 즉시 적용하세요.\n"
            "- [ ] EDR/SIEM 탐지 룰을 업데이트하세요.\n"
            "- [ ] 클라우드 인프라 보안 설정 정기 감사\n"
        )
        issues = run_qa_gate(content)
        assert issues == []
