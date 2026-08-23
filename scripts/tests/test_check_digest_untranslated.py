import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_digest_untranslated import check_post, is_untranslated

# --- unit: is_untranslated() heuristic ------------------------------------

_REAL_ENGLISH = (
    "A malvertising operation dubbed SourTrade is making victims' browsers "
    "build the final Windows executable themselves, using a legitimate Bun "
    "runtime as its base instead of serving one complete malicious file. "
    "EDR/SIEM에서 IoC 기반 탐지 룰을 업데이트하세요."
)
_KOR_WITH_UNQUOTED_TITLES = (
    "이번 GFN Thursday에서는 Steam Summer Sale과 GeForce NOW 멤버십 할인이 "
    "결합된 이중 혜택이 제공됩니다. 또한 Devolver 라인업에 Dark Scrolls가 "
    "합류하고, Square Enix의 The Adventures of Elliot: The Millennium Tales도 "
    "추가됩니다."
)
_KOR_WITH_CITED_TITLE = (
    '비트코인 매거진의 칼럼 "The Hyperinflation of 1971 at the Kindergarten"은 '
    "유치원생 수준에서 초인플레이션을 설명합니다. 이 글은 Alex v. Frankenberg가 "
    "작성했습니다."
)
_KOR_CLEAN = (
    "SourTrade라 불리는 악성 광고 캠페인은 피해자의 브라우저가 최종 Windows "
    "실행 파일을 직접 빌드하도록 만듭니다. EDR/SIEM에서 IoC 기반 탐지 룰을 "
    "업데이트하세요."
)
_KOR_WITH_CVE = (
    "이 취약점은 CVE-2026-16723으로 추적되고 있으니, CVSS와 KEV 포함 여부를 "
    "검토한 뒤 유지보수 창과 롤백 플랜을 준비하세요."
)


def test_flags_real_english_prose():
    assert is_untranslated(_REAL_ENGLISH) is True


def test_ignores_korean_with_unquoted_proper_noun_titles():
    # Title-Cased product/article names ("GeForce NOW", "The Adventures of ...")
    # inside Korean prose are cited names, not English prose.
    assert is_untranslated(_KOR_WITH_UNQUOTED_TITLES) is False


def test_ignores_korean_citing_quoted_english_title():
    assert is_untranslated(_KOR_WITH_CITED_TITLE) is False


def test_ignores_clean_korean():
    assert is_untranslated(_KOR_CLEAN) is False


def test_ignores_korean_with_identifiers():
    assert is_untranslated(_KOR_WITH_CVE) is False


# --- integration: check_post() over a whole digest body -------------------

_HEAD = "---\ntitle: x\nimage: /assets/images/x.svg\n---\n\n"


def _write(txt):
    f = tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8")
    f.write(txt)
    f.close()
    return f.name


def test_check_post_flags_english_summary_block():
    body = (
        _HEAD
        + "## 1. 보안 뉴스\n\n### 1.1 항목\n\n#### 요약\n\n"
        + _REAL_ENGLISH
        + "\n\n---\n"
    )
    vs = check_post(_write(body))
    assert vs and any("요약 블록" in v for v in vs)


def test_check_post_flags_english_summary_field():
    body = (
        _HEAD
        + '## 1. 보안 뉴스\n\n{% include news-card.html\n  title="x"\n  summary="'
        + _REAL_ENGLISH.replace('"', "'")
        + '"\n%}\n\n#### 요약\n\n'
        + _KOR_CLEAN
        + "\n\n---\n"
    )
    vs = check_post(_write(body))
    assert vs and any("summary=" in v for v in vs)


def test_check_post_passes_clean_korean_digest():
    body = (
        _HEAD
        + '## 1. 보안 뉴스\n\n### 1.1 항목\n\n{% include news-card.html\n  title="한국어 제목"\n  summary="'
        + _KOR_CLEAN
        + '"\n%}\n\n#### 요약\n\n'
        + _KOR_CLEAN
        + "\n\n---\n"
    )
    assert check_post(_write(body)) == []


def test_check_post_ignores_code_fence_content():
    # An English sentence inside a fenced code block must NOT trip the guard.
    body = (
        _HEAD
        + "## 1. 보안 뉴스\n\n#### 요약\n\n"
        + _KOR_CLEAN
        + "\n\n```\nthe attacker is able to run code with the privileges of the process\n```\n\n---\n"
    )
    assert check_post(_write(body)) == []
