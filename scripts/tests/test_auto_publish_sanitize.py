#!/usr/bin/env python3
"""Tests for sanitize_quotes_for_yaml in scripts/news/content_generator.py.

Covers:
1. raw `"` → `'`
2. already-sanitized text is idempotent
3. Korean curly quotes (U+201C / U+201D) are preserved
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.news.content_generator import sanitize_quotes_for_yaml


class TestSanitizeQuotesForYaml:
    # ------------------------------------------------------------------
    # 1. Raw ASCII double-quote is replaced with single quote
    # ------------------------------------------------------------------

    def test_raw_dq_replaced(self):
        result = sanitize_quotes_for_yaml('Title with "quoted" word')
        assert '"' not in result
        assert "'" in result

    def test_raw_dq_at_start(self):
        result = sanitize_quotes_for_yaml('"Leading quote')
        assert result.startswith("'")

    def test_raw_dq_at_end(self):
        result = sanitize_quotes_for_yaml('Trailing quote"')
        assert result.endswith("'")

    def test_multiple_raw_dqs(self):
        result = sanitize_quotes_for_yaml('a "b" and "c"')
        assert '"' not in result
        assert result == "a 'b' and 'c'"

    # ------------------------------------------------------------------
    # 2. Already-sanitized text is idempotent
    # ------------------------------------------------------------------

    def test_idempotent_no_dq(self):
        text = "No double quotes here"
        assert sanitize_quotes_for_yaml(text) == text

    def test_idempotent_single_quotes(self):
        text = "Title with 'inner' single quotes"
        assert sanitize_quotes_for_yaml(text) == text

    def test_idempotent_korean_no_dq(self):
        text = "중요한 CVE 취약점 'Sorry' 공격"
        assert sanitize_quotes_for_yaml(text) == text

    # ------------------------------------------------------------------
    # 3. Curly quotes normalised; fullwidth (U+FF02) preserved
    # ------------------------------------------------------------------

    def test_left_double_quotation_mark_normalised(self):
        """U+201C LEFT DOUBLE QUOTATION MARK is now normalised to ASCII apostrophe."""
        text = "\u201cSmart quote\u201d"
        result = sanitize_quotes_for_yaml(text)
        # Curly quotes are removed (normalised), NOT preserved
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "'" in result

    def test_fullwidth_quotation_preserved(self):
        """Fullwidth double-quote (U+FF02) is kept as-is."""
        text = "\uff02fullwidth\uff02"
        result = sanitize_quotes_for_yaml(text)
        assert "\uff02" in result

    def test_mixed_curly_and_ascii_all_normalised(self):
        """Both ASCII \" (U+0022) and curly quotes are replaced with apostrophe."""
        text = '\u201cSmart\u201d and "ascii" here'
        result = sanitize_quotes_for_yaml(text)
        assert '"' not in result  # ASCII dq gone
        assert "\u201c" not in result  # curly left quote normalised
        assert "\u201d" not in result  # curly right quote normalised
        assert "'" in result  # replaced with apostrophe

    # ------------------------------------------------------------------
    # 4. HTML entity &quot; and literal \u0022 decoded then sanitized
    # ------------------------------------------------------------------

    def test_html_entity_quot_decoded(self):
        """&quot; from upstream feed is decoded to ' (not left as &quot;)."""
        result = sanitize_quotes_for_yaml("Title &quot;Sorry&quot; attack")
        assert "&quot;" not in result
        assert '"' not in result
        assert "'" in result

    def test_literal_u0022_sequence(self):
        r"""Literal \\u0022 sequence in text → replaced with single quote."""
        result = sanitize_quotes_for_yaml("Title \\u0022word\\u0022 end")
        assert "\\u0022" not in result
        assert '"' not in result

    # ------------------------------------------------------------------
    # 5. Empty / None guard
    # ------------------------------------------------------------------

    def test_empty_string(self):
        assert sanitize_quotes_for_yaml("") == ""

    def test_none_like_empty(self):
        # The function signature accepts str; passing empty is the safe test
        assert sanitize_quotes_for_yaml("") == ""

    # ------------------------------------------------------------------
    # 6. Curly / typographic quote normalisation (new behaviour)
    # ------------------------------------------------------------------

    def test_curly_double_quote_left_normalized(self):
        """U+201C LEFT DOUBLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("Next \u201c26\u201d release")
        assert "\u201c" not in result
        assert "'" in result

    def test_curly_double_quote_right_normalized(self):
        """U+201D RIGHT DOUBLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("version \u201d1.0\u201d end")
        assert "\u201d" not in result
        assert "'" in result

    def test_curly_single_quote_left_normalized(self):
        """U+2018 LEFT SINGLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("Next \u201826\u2019 release")
        assert "\u2018" not in result
        assert "'" in result

    def test_curly_single_quote_right_normalized(self):
        """U+2019 RIGHT SINGLE QUOTATION MARK is normalised to ASCII apostrophe."""
        result = sanitize_quotes_for_yaml("it\u2019s fine")
        assert "\u2019" not in result
        assert "'" in result

    def test_html_entity_curly_quotes_decoded(self):
        """HTML entities &ldquo; &rdquo; &lsquo; &rsquo; decoded and normalised."""
        result = sanitize_quotes_for_yaml("&ldquo;hello&rdquo; and &lsquo;world&rsquo;")
        # No curly quote code points remain
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "\u2018" not in result
        assert "\u2019" not in result
        # No raw ASCII double-quote either
        assert '"' not in result
        # All replaced with apostrophe
        assert "'" in result

    def test_html_entity_numeric_curly_quotes_decoded(self):
        """HTML numeric entities &#8216; &#8217; &#8220; &#8221; decoded and normalised."""
        result = sanitize_quotes_for_yaml(
            "&#8220;double&#8221; and &#8216;single&#8217;"
        )
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "\u2018" not in result
        assert "\u2019" not in result
        assert '"' not in result
        assert "'" in result

    def test_idempotent_on_pre_normalized(self):
        """Applying sanitize_quotes_for_yaml twice gives identical result."""
        original = "Next \u201826 \u201crelease\u201d has &ldquo;patch&rdquo;"
        once = sanitize_quotes_for_yaml(original)
        twice = sanitize_quotes_for_yaml(once)
        assert once == twice

    def test_mixed_curly_and_ascii_all_normalized(self):
        """ASCII dq, curly dq, and curly sq all normalised in one pass."""
        result = sanitize_quotes_for_yaml(
            'say "hi" and \u201chello\u201d and \u2018world\u2019'
        )
        assert '"' not in result
        assert "\u201c" not in result
        assert "\u201d" not in result
        assert "\u2018" not in result
        assert "\u2019" not in result


# ---------------------------------------------------------------------------
# 4. The coupling: the cover-title regex is only correct BECAUSE of this
#    sanitizer. Nothing asserted that until 2026-09-22.
# ---------------------------------------------------------------------------


class TestCoverTitleExtractionDependsOnSanitizer:
    """`auto_publish_news` 는 front matter 제목을 정규식으로 되읽는다.

        m_title = re.search(r'^title:\\s*"?([^\\n"]+)"?\\s*$', post_content, re.M)

    `[^\\n"]+` 는 값 안의 `"` 를 만나면 멈춘다. 이스케이프된 큰따옴표가 든 제목이면
    매치가 **통째로 실패**하고, 그 경우 `post_info_for_l20["title"]` 은 초기값인
    빈 문자열로 남는다(포스트 본문은 `---` 로 시작하므로 그 조건도 거짓이다).

    2026-09-22 재현: 빈 제목으로 L20 을 부르면 커버는 정상 생성되지만 헤드라인이
    "Security Update" 라는 일반 문구로 대체된다. 실패가 아니라 **조용한 치환**이다.
    커버 정직성 체계를 가진 저장소에서 제목이 소리 없이 사라지는 셈이다.

    그 경로가 지금 닫혀 있는 이유는 정규식이 견고해서가 아니라
    `sanitize_quotes_for_yaml` 이 모든 큰따옴표류를 작은따옴표로 바꾸기 때문이다.
    즉 **생산자와 소비자가 한 가정을 공유하는데 그 가정을 아무도 단언하지 않았다** —
    이 저장소가 이미 대가를 치른 모양이다(notes: producer-gate must share one fold).

    그래서 여기서는 sanitizer 의 동작이 아니라 **둘의 결합**을 건다.
    """

    @staticmethod
    def _title_regex():
        """정규식을 사본으로 두지 않고 프로덕션 소스에서 읽어 온다.

        여기 복사해 두면 저쪽이 바뀌어도 이 검사는 옛 패턴을 계속 통과시킨다.
        """
        import re

        src = (Path(__file__).resolve().parents[1] / "auto_publish_news.py").read_text(
            encoding="utf-8"
        )
        m = re.search(r"re\.search\(\s*(r'[^']*\^title:[^']*')", src)
        assert m, (
            "auto_publish_news.py 에서 제목 추출 정규식을 찾지 못했다. 추출 방식이 "
            "바뀌었다면(예: YAML 파싱) 이 검사를 그에 맞게 갱신하라 — 찾지 못한 채 "
            "통과시키면 아무것도 검사하지 않게 된다."
        )
        return re.compile(eval(m.group(1)), re.MULTILINE)  # noqa: S307

    @pytest.mark.parametrize(
        "headline",
        [
            '중요한 cPanel 취약점이 "Sorry", Trellix, 그리고 AWS',
            "보안 업데이트 &quot;긴급&quot; 배포",
            "“제로데이” 공격 확산",
            "이미 'single' 인용된 제목",
            "따옴표 없는 평범한 제목",
        ],
    )
    def test_sanitized_titles_survive_the_cover_regex(self, headline: str) -> None:
        sanitized = sanitize_quotes_for_yaml(headline)
        front_matter = f'---\nlayout: post\ntitle: "{sanitized}"\n---\n\n본문\n'

        m = self._title_regex().search(front_matter)
        assert m, (
            f"정규화된 제목 {sanitized!r} 를 커버 추출 정규식이 읽지 못했다. "
            "발행 시 커버 제목이 빈 문자열이 되고, 헤드라인이 'Security Update' "
            "같은 일반 문구로 조용히 대체된다."
        )
        assert m.group(1).strip() == sanitized, (
            f"추출값이 원본과 다르다: {m.group(1).strip()!r} != {sanitized!r}"
        )

    def test_an_unsanitized_title_would_break_it(self) -> None:
        """대조군 — 위 검사가 공허하지 않음을 보인다.

        sanitizer 를 거치지 않은 제목은 실제로 추출에 실패한다. 이 단언이 깨진다면
        정규식이 견고해진 것이므로 결합이 풀린 것이고, 그때는 위 검사도 다시 본다.
        """
        raw = '취약점이 \\"Sorry\\" 라고 말했다'
        front_matter = f'---\nlayout: post\ntitle: "{raw}"\n---\n\n본문\n'
        assert self._title_regex().search(front_matter) is None, (
            "이스케이프된 큰따옴표가 든 제목을 정규식이 읽어냈다. 정규식이 "
            "견고해졌다면 sanitizer 의존이 사라진 것이니 이 클래스의 설명을 갱신하라."
        )
