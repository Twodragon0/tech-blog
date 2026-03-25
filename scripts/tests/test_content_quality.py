"""Unit tests for content quality helper functions in content_generator.py.

Tests _build_clean_excerpt, _build_clean_description, _build_clean_image_alt,
and _has_batchim functions.
"""

import pytest
from news.content_generator import (
    _build_clean_excerpt,
    _build_clean_description,
    _build_clean_image_alt,
    _has_batchim,
)


class TestHasBatchim:
    """Korean batchim (final consonant) detection."""

    def test_with_batchim(self):
        assert _has_batchim("한") is True  # ㄴ batchim
        assert _has_batchim("일") is True  # ㄹ batchim
        assert _has_batchim("것") is True  # ㅅ batchim

    def test_without_batchim(self):
        assert _has_batchim("해") is False
        assert _has_batchim("주") is False
        assert _has_batchim("가") is False

    def test_non_korean(self):
        assert _has_batchim("A") is False
        assert _has_batchim("1") is False
        assert _has_batchim("") is False


class TestBuildCleanExcerpt:
    """Excerpt generation with correct Korean particles."""

    def test_particle_eul_with_batchim(self):
        # "형" has batchim -> "을"
        result = _build_clean_excerpt("IAM 정책 유형", "2026년 03월 24일", 29, "security")
        assert "유형을 중심으로" in result

    def test_particle_reul_without_batchim(self):
        # "해" has no batchim -> "를"
        result = _build_clean_excerpt("보안 위협 분석, 취약점 대응 요약", "2026년 03월 20일", 24, "security")
        assert "요약를" not in result

    def test_security_mode(self):
        result = _build_clean_excerpt("test", "2026년 03월 24일", 10, "security")
        assert "보안/기술 뉴스" in result
        assert "10건" in result

    def test_tech_mode(self):
        result = _build_clean_excerpt("test", "2026년 03월 24일", 15, "tech")
        assert "기술 블로그 뉴스" in result
        assert "15건" in result


class TestBuildCleanDescription:
    """Description generation with natural sentence structure."""

    def test_multi_keyword_description(self):
        result = _build_clean_description(
            "북한 해커, VS Code 악용, IAM 정책",
            "The Hacker News, AWS Security Blog",
            "2026년 03월 24일", 29, "security"
        )
        assert "북한 해커" in result
        assert "VS Code 악용" in result
        assert "IAM 정책" in result
        assert "등 DevSecOps" in result

    def test_single_keyword(self):
        result = _build_clean_description(
            "Ransomware 위협 분석",
            "SK쉴더스", "2026년 03월 23일", 15, "security"
        )
        assert "Ransomware 위협 분석" in result

    def test_tech_mode_description(self):
        result = _build_clean_description(
            "Kubernetes, Docker, CI/CD",
            "CNCF Blog", "2026년 03월 21일", 22, "tech"
        )
        assert "개발자 트렌드" in result

    def test_source_list_included(self):
        result = _build_clean_description(
            "test", "The Hacker News", "2026년 03월 24일", 10, "security"
        )
        assert "The Hacker News" in result

    def test_no_orphaned_commas(self):
        result = _build_clean_description(
            "A, , B, , C",
            "Source", "2026년 03월 24일", 5, "security"
        )
        assert ",," not in result
        assert ", ," not in result


class TestBuildCleanImageAlt:
    """Image alt text generation - English only, no truncation artifacts."""

    def test_basic_security_alt(self):
        result = _build_clean_image_alt("VS Code exploit, IAM policy", "security")
        assert "VS Code" in result
        assert "security digest" in result

    def test_korean_stripped(self):
        result = _build_clean_image_alt("북한 해커, VS Code 악용, IAM 정책", "security")
        assert "VS Code" in result
        # No Korean characters in output
        import re
        assert not re.search(r"[가-힣]", result)

    def test_tech_mode_suffix(self):
        result = _build_clean_image_alt("Kubernetes, Docker", "tech")
        assert "tech digest" in result

    def test_fallback_on_empty(self):
        result = _build_clean_image_alt("한국어만 있는 제목", "security")
        assert "Weekly security digest" in result or "security" in result.lower()

    def test_no_double_spaces(self):
        result = _build_clean_image_alt("A,  , B,  , C", "security")
        assert "  " not in result

    def test_no_leading_trailing_punctuation(self):
        result = _build_clean_image_alt(", test, ", "security")
        assert not result.startswith(",")
        assert not result.startswith(" ")


class TestCheckTableCellTruncation:
    """Table cell truncation detection in check_posts.py."""

    @pytest.fixture
    def check_fn(self):
        from check_posts import check_table_cell_truncation
        return check_table_cell_truncation

    def test_trailing_comma_detected(self, check_fn):
        content = "| cell1 | this is truncated, |\n"
        result = check_fn(content)
        assert any("잘림" in w for w in result)

    def test_dangling_preposition_detected(self, check_fn):
        content = "| cell1 | connected to the |\n"
        result = check_fn(content)
        assert any("잘림" in w for w in result)

    def test_normal_cell_no_warning(self, check_fn):
        content = "| 항목 | 인터넷 노출 자산 점검 및 고위험 항목 우선 패치 |\n"
        result = check_fn(content)
        assert len(result) == 0

    def test_code_identifier_no_warning(self, check_fn):
        content = "| tool | restricted-ssh |\n"
        result = check_fn(content)
        assert len(result) == 0

    def test_tech_terms_no_warning(self, check_fn):
        content = "| OS | iOS, Android |\n"
        result = check_fn(content)
        assert len(result) == 0

    def test_qa_no_warning(self, check_fn):
        content = "| 내용 | 보안 이슈 공유 및 Q&A |\n"
        result = check_fn(content)
        assert len(result) == 0

    def test_separator_row_skipped(self, check_fn):
        content = "|---|---|\n"
        result = check_fn(content)
        assert len(result) == 0

    def test_camelcase_no_warning(self, check_fn):
        content = "| setting | runAsNonRoot: true |\n"
        result = check_fn(content)
        assert len(result) == 0
