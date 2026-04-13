"""Unit tests for the pre-publish QA gate (scripts.news.qa_gate).

Covers:
- validate_sentence_completeness: incomplete / complete checklist items
- validate_stats_consistency: category sum vs stated total
- validate_trend_analysis: trend table sum vs stated total
- run_qa_gate: strict mode (env var) raises QAGateError
"""

import os

import pytest
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
    """Trend table counts should not be less than total news count."""

    TREND_OK = (
        "- **총 뉴스 수**: 10개\n"
        "\n"
        "## 5. 트렌드 분석\n\n"
        "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        "|--------|-------------|------------|\n"
        "| **AI/LLM** | 5건 | GPT, LLM |\n"
        "| **보안** | 4건 | CVE, 패치 |\n"
        "| **클라우드** | 3건 | AWS, GCP |\n"
    )

    TREND_UNDERCOUNT = (
        "- **총 뉴스 수**: 15개\n"
        "\n"
        "## 3. 트렌드 분석\n\n"
        "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
        "|--------|-------------|------------|\n"
        "| **AI/LLM** | 3건 | GPT |\n"
        "| **보안** | 2건 | CVE |\n"
    )

    def test_trend_ok(self):
        """Sum >= total is acceptable (overlap)."""
        assert validate_trend_analysis(self.TREND_OK) == []

    def test_trend_undercount(self):
        """Sum < total is flagged."""
        issues = validate_trend_analysis(self.TREND_UNDERCOUNT)
        assert len(issues) == 1
        assert "Trend analysis under-count" in issues[0]
        assert "trend sum=5" in issues[0]
        assert "total=15" in issues[0]

    def test_no_trend_section(self):
        """Content without trend section should pass."""
        content = "- **총 뉴스 수**: 10개\nSome content\n"
        assert validate_trend_analysis(content) == []

    def test_no_total(self):
        """Content without total should pass."""
        content = (
            "## 5. 트렌드 분석\n\n"
            "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
            "| **AI** | 3건 | GPT |\n"
        )
        assert validate_trend_analysis(content) == []

    def test_exact_match(self):
        """Sum == total should pass."""
        content = (
            "- **총 뉴스 수**: 8개\n"
            "\n## 4. 트렌드 분석\n\n"
            "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
            "|--------|-------------|------------|\n"
            "| **AI** | 5건 | GPT |\n"
            "| **보안** | 3건 | CVE |\n"
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

    def test_ci_mode_raises(self, monkeypatch):
        monkeypatch.setenv("CI", "1")
        monkeypatch.setenv("AUTO_PUBLISH_STRICT_QA", "")
        content = "- [ ] 시스템이 지속적으로 취약\n"
        with pytest.raises(QAGateError):
            run_qa_gate(content)

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

    def test_apr13_trend_mismatch(self):
        """4/13 post: trend sum didn't match total."""
        content = (
            "- **총 뉴스 수**: 12개\n\n"
            "## 5. 트렌드 분석\n\n"
            "| 트렌드 | 관련 뉴스 수 | 주요 키워드 |\n"
            "|--------|-------------|------------|\n"
            "| **공급망 보안** | 2건 | supply chain |\n"
            "| **제로데이** | 1건 | zero-day |\n"
        )
        issues = validate_trend_analysis(content)
        assert len(issues) == 1
        assert "trend sum=3" in issues[0]

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
