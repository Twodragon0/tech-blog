"""Tests for scripts/check_digest_proper_nouns.py.

Covers the policy contract (notes/digest-proper-noun-policy.md):
  - deny-by-default allow-list: only listed Hangul forms are flagged/rewritten
  - masking: cited quoted titles / code / URLs / CVE IDs are exempt
  - josa-aware --fix: 구글은 -> Google은, but 구글링 (derived word) is untouched
  - front matter is never modified
  - --fix is idempotent
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from check_digest_proper_nouns import (  # noqa: E402
    ENTITIES,
    check_post,
    find_violations,
    fix_body,
    fix_post,
    main,
    _is_digest_post,
    _split_front_matter,
)

# --- find_violations() -----------------------------------------------------


def test_flags_listed_hangul_form():
    v = find_violations("비트코인 가격이 급등했습니다.")
    assert v == [("비트코인", "Bitcoin", 1)]


def test_counts_multiple_occurrences():
    v = find_violations("구글은 발표했고 구글의 정책은 바뀌었다.")
    assert v == [("구글", "Google", 2)]


def test_ignores_unlisted_hangul_token():
    # 네이버 / 카카오 are not in the allow-list -> never flagged (deny-by-default).
    assert find_violations("네이버와 카카오가 발표했습니다.") == []


def test_english_canonical_is_compliant():
    assert find_violations("Bitcoin surged and Google announced a policy.") == []


def test_detects_intra_document_mixing():
    # Both 비트코인 and Bitcoin in one body -> the Hangul form is still a violation.
    v = find_violations("비트코인 시세와 Bitcoin ETF 흐름을 함께 봅니다.")
    assert v == [("비트코인", "Bitcoin", 1)]


# --- masking (exempt spans) ------------------------------------------------


def test_cited_quoted_title_is_exempt():
    assert find_violations('칼럼 "구글 검색의 미래"를 인용합니다.') == []


def test_news_card_attribute_value_is_fixable():
    # title="..."/summary="..." are translated display copy, NOT cited titles.
    # They MUST canonicalize so the card matches the prose (no intra-doc mixing).
    body = '  title="스위스 은행이 비트코인 거래 시작"\n  source="Bitcoin Magazine"'
    assert find_violations(body) == [("비트코인", "Bitcoin", 1)]
    new, n = fix_body(body)
    assert 'title="스위스 은행이 Bitcoin 거래 시작"' in new and n == 1


def test_inline_code_is_exempt():
    assert find_violations("`구글` 은 코드 안이라 예외입니다.") == []


def test_fenced_code_is_exempt():
    body = "설명\n```\n비트코인 sample\n```\n끝"
    assert find_violations(body) == []


def test_url_is_exempt():
    assert find_violations("자세히는 https://example.com/비트코인 참고.") == []


def test_cve_is_exempt_but_surrounding_entity_flagged():
    v = find_violations("CVE-2026-12345 관련 구글 패치가 나왔다.")
    assert v == [("구글", "Google", 1)]


# --- fix_body(): josa-aware rewriting --------------------------------------


def test_fix_bare_entity():
    new, n = fix_body("비트코인 상승")
    assert new == "Bitcoin 상승" and n == 1


def test_fix_preserves_josa():
    new, n = fix_body("구글은 발표했고 구글의 정책, 구글이 주도.")
    assert new == "Google은 발표했고 Google의 정책, Google이 주도." and n == 3


def test_fix_does_not_mangle_derived_word():
    # 구글링 (to google, a Korean verb) must NOT become 'Google링'.
    new, n = fix_body("사람들이 구글링을 했다.")
    assert new == "사람들이 구글링을 했다." and n == 0


def test_fix_skips_protected_spans():
    body = '인용 "구글" 과 `비트코인` 및 https://x.io/구글 은 그대로, 구글은 변경.'
    new, n = fix_body(body)
    assert '"구글"' in new  # quoted title preserved
    assert "`비트코인`" in new  # inline code preserved
    assert "https://x.io/구글" in new  # url preserved
    assert "Google은 변경" in new  # unprotected occurrence rewritten
    assert n == 1


def test_fix_is_idempotent():
    body = "비트코인과 구글은 이더리움 위에서 동작한다."
    once, _ = fix_body(body)
    twice, n2 = fix_body(once)
    assert once == twice and n2 == 0


def test_all_entities_rewrite():
    for ko, en in ENTITIES.items():
        new, n = fix_body(f"{ko} 관련 소식")
        assert new == f"{en} 관련 소식", f"{ko} should become {en}"
        assert n == 1


# --- 2026-07-30 additions: 메타/시스코 canonical + substring-trap guards --------


def test_meta_company_is_canonicalized_with_josa():
    # 메타의/메타가/메타 (standalone) are the company Meta.
    new, n = fix_body("메타의 광고 랭킹과 메타가 발표한 정책, 그리고 메타 광고.")
    assert new == "Meta의 광고 랭킹과 Meta가 발표한 정책, 그리고 Meta 광고."
    assert n == 3


def test_meta_compound_words_are_not_touched():
    # 메타 + Hangul-non-josa (데/버/분/문) is a compound noun, never Meta.
    body = "메타데이터를 메타버스에서 메타분석하고 메타문자를 처리."
    assert find_violations(body) == []
    new, n = fix_body(body)
    assert new == body and n == 0


def test_cisco_is_canonicalized_but_san_francisco_is_not():
    body = "시스코가 분기 실적을 발표했고 샌프란시스코 지사도 언급했다."
    v = find_violations(body)
    assert v == [("시스코", "Cisco", 1)]  # 샌프란시스코 embedded → not flagged
    new, n = fix_body(body)
    assert new == "Cisco가 분기 실적을 발표했고 샌프란시스코 지사도 언급했다."
    assert n == 1


def test_window_homonym_stays_deferred():
    # 윈도우 is intentionally NOT in ENTITIES (context/exploit window homonym).
    assert "윈도우" not in ENTITIES
    body = "1M 토큰 컨텍스트 윈도우를 갖춘 모델과 윈도우 Defender."
    assert find_violations(body) == []


# --- front matter is never touched -----------------------------------------


def test_front_matter_preserved():
    doc = (
        "---\n"
        'title: "구글의 새 정책"\n'   # front matter Hangul must survive
        "---\n"
        "본문에서 구글은 canonical.\n"
    )
    fm, body = _split_front_matter(doc)
    assert "구글의 새 정책" in fm
    new_body, n = fix_body(body)
    assert "Google은 canonical" in new_body and n == 1


# --- integration: check_post / fix_post / main -----------------------------


def _write_digest(tmp: Path, name: str, body: str) -> Path:
    p = tmp / f"2026-01-01-{name}_Weekly_Digest.md"
    p.write_text(f"---\ntitle: \"x\"\n---\n{body}", encoding="utf-8")
    return p


def test_check_post_reports_violation():
    with tempfile.TemporaryDirectory() as d:
        p = _write_digest(Path(d), "T", "비트코인과 구글 뉴스.")
        vs = check_post(str(p))
        assert any("비트코인 -> Bitcoin" in v for v in vs)
        assert any("구글 -> Google" in v for v in vs)


def test_fix_post_rewrites_and_preserves_front_matter():
    with tempfile.TemporaryDirectory() as d:
        p = _write_digest(Path(d), "T", "구글은 발표했다.")
        n = fix_post(p)
        out = p.read_text(encoding="utf-8")
        assert n == 1
        assert 'title: "x"' in out
        assert "Google은 발표했다." in out


def test_is_digest_post_scope():
    assert _is_digest_post(Path("2026-01-01-X_Weekly_Digest.md")) is True
    assert _is_digest_post(Path("2026-01-01-Regular_Post.md")) is False


def test_main_check_exit_code_on_violation(capsys):
    with tempfile.TemporaryDirectory() as d:
        p = _write_digest(Path(d), "T", "비트코인 뉴스.")
        rc = main([str(p)])
        assert rc == 1


def test_main_fix_then_check_clean(capsys):
    with tempfile.TemporaryDirectory() as d:
        p = _write_digest(Path(d), "T", "비트코인 뉴스.")
        assert main(["--fix", str(p)]) == 0
        capsys.readouterr()
        assert main([str(p)]) == 0  # now compliant
