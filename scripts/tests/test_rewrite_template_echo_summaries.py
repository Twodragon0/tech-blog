"""Tests for scripts/rewrite_template_echo_summaries.py.

Measured on the corpus 2026-08-07, before any code was written:

* 271 template-echo summaries in 24 digests — 226 ``news-card`` + 45
  ``news-spotlight-item`` (matching only ``{%`` and only ``news-card`` finds 61)
* 221 of the 226 ``news-card`` items are followed by a prose paragraph
* **0** of the 45 ``news-spotlight-item`` entries are. They sit back to back
  inside a ``{% capture %}`` block, so the "prose" 20 lines below belongs to the
  트렌드 분석 section, not to the article

The transform therefore repairs only what the post can actually evidence, and
the runtime contract pins the rest: nothing outside a card ``summary=`` value
may move.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import rewrite_template_echo_summaries as rw  # noqa: E402

_FM = '---\nlayout: post\ntitle: "x"\n---\n\n'

_ECHO = (
    "Cisco 취약점 공개 이슈를 중심으로 공격 벡터와 영향 범위를 점검하고, "
    "탐지·차단·복구 관점의 우선 대응 항목을 실무 기준으로 정리했습니다."
)
_PROSE = (
    "Cisco가 Catalyst SD-WAN Manager에 영향을 미치는 2개의 취약점이 실제 공격에 "
    "활용되고 있음을 공식 확인했습니다. 핵심 취약점인 CVE-2026-20122는 인증된 원격 "
    "공격자가 임의 파일을 덮어쓸 수 있는 결함입니다."
)


def _card(summary=_ECHO, dash=False, image=None):
    open_tag = "{%- include" if dash else "{% include"
    close_tag = "-%}" if dash else "%}"
    lines = [
        f"{open_tag} news-card.html",
        '  title="[보안] Cisco 취약점 공개"',
        '  url="https://example.com/a?utm_source=rss"',
    ]
    if image:
        lines.append(f'  image="{image}"')
    lines += [
        f'  summary="{summary}"',
        '  source="The Hacker News"',
        '  severity="High"',
        close_tag,
    ]
    return "\n".join(lines) + "\n"


def _post(body):
    return _FM + body


def _summary_of(text, index=0):
    cards = list(rw.CARD_RE.finditer(text))
    return rw.SUMMARY_RE.search(cards[index].group(0)).group(2)


# --- the rewrite -------------------------------------------------------------


def test_template_echo_summary_is_replaced_with_the_following_prose():
    out = rw.transform(_post(_card() + "\n" + _PROSE + "\n"))
    assert "공격 벡터와 영향 범위를 점검하고" not in out
    assert "CVE-2026-20122" in _summary_of(out)


def test_whitespace_control_variant_is_matched():
    out = rw.transform(_post(_card(dash=True) + "\n" + _PROSE + "\n"))
    assert "CVE-2026-20122" in _summary_of(out)


def test_summary_heading_between_card_and_prose_is_skipped():
    body = _card() + "\n#### 요약\n\n" + _PROSE + "\n"
    assert "CVE-2026-20122" in _summary_of(rw.transform(_post(body)))


def test_at_most_two_sentences_are_lifted():
    prose = "첫 번째 문장은 이 기사에 대한 충분한 길이의 설명입니다. 두 번째 문장도 마찬가지로 충분히 깁니다. 세 번째 문장은 버려져야 합니다."
    out = rw.transform(_post(_card() + "\n" + prose + "\n"))
    assert "세 번째 문장" not in _summary_of(out)
    assert "두 번째 문장" in _summary_of(out)


def test_summary_stays_within_the_generator_cap():
    prose = "가" * 260 + "라고 보고되었습니다. 두 번째 문장입니다."
    out = rw.transform(_post(_card() + "\n" + prose + "\n"))
    for card in rw.CARD_RE.finditer(out):
        found = rw.SUMMARY_RE.search(card.group(0))
        assert len(found.group(2)) <= rw.MAX_SUMMARY_LEN


def test_no_text_is_invented_when_the_helper_would_pad():
    """``_truncate_korean_sentence`` appends "… 등이 확인되었습니다." on its fallback
    path. A generator may write that; a corpus rewrite may not."""
    prose = ("첫 문장은 아주 길게 이어지는 설명으로 " * 12).strip() + "입니다. 두 번째 문장입니다."
    src = _post(_card() + "\n" + prose + "\n")
    assert rw.transform(src) == src


def test_the_replacement_is_copied_from_the_post_body():
    body = _card() + "\n" + _PROSE + "\n"
    value = _summary_of(rw.transform(_post(body)))
    assert value in _PROSE, "every character must come from the paragraph below"


def test_transform_is_idempotent():
    src = _post(_card() + "\n" + _PROSE + "\n")
    once = rw.transform(src)
    assert rw.transform(once) == once


# --- what it must NOT touch --------------------------------------------------


def test_non_template_summary_is_left_alone():
    src = _post(_card(summary="이미 기사 고유의 사실을 담은 요약입니다.") + "\n" + _PROSE + "\n")
    assert rw.transform(src) == src


def test_other_attributes_are_byte_identical():
    image = (
        "https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBo"
        ".jpg?w=1&u=https://s3.example.com/x.jpg"
    )
    src = _post(_card(image=image) + "\n" + _PROSE + "\n")
    out = rw.transform(src)
    assert out != src
    assert f'  image="{image}"' in out
    assert '  url="https://example.com/a?utm_source=rss"' in out


def test_multiline_liquid_include_is_untouched_outside_the_summary():
    """T1: the corrupted cover images of PR #509 came from exactly this shape."""
    src = _post(_card(image="https://cdn.example.com/p/https://s3.example.com/a.jpg"))
    src += "\n" + _PROSE + "\n"
    out = rw.transform(src)
    assert not rw.violates_summary_only(src, out)


def test_front_matter_is_never_edited():
    fm = (
        "---\nlayout: post\n"
        'description: "… 공격 벡터와 영향 범위를 점검하고, 대응 체크리스트를 제시합니다."\n'
        "---\n\n"
    )
    src = fm + _card() + "\n" + _PROSE + "\n"
    out = rw.transform(src)
    assert out.startswith(fm)


def test_card_inside_a_code_fence_is_not_rewritten():
    src = _post("```liquid\n" + _card() + "```\n\n" + _PROSE + "\n")
    assert rw.transform(src) == src


def test_indented_closing_fence_closes_the_block():
    """T3: 2026-02-08 closes its fences with leading whitespace."""
    src = _post("```text\nnoise\n  ```\n\n" + _card() + "\n" + _PROSE + "\n")
    assert "CVE-2026-20122" in _summary_of(rw.transform(src))


def test_spotlight_items_packed_in_a_capture_block_are_skipped():
    """The measured reality: 45/45 spotlight defects have no prose of their own."""
    item = (
        "{% include news-spotlight-item.html\n"
        '  title="Nano Banana 프롬프팅 가이드"\n'
        '  url="https://example.com/n"\n'
        '  source="Google Cloud Blog"\n'
        '  tag="Cloud / Platform"\n'
        f'  summary="{_ECHO}"\n'
        "%}\n"
    )
    src = _post("{% capture spotlight_items %}\n" + item + item + "{% endcapture %}\n")
    assert rw.transform(src) == src


def test_card_followed_by_a_table_is_skipped():
    table = "| 원칙 | 설명 |\n|------|------|\n| 투명성 | 설명가능성 요건 |\n"
    src = _post(_card() + "\n" + table)
    assert rw.transform(src) == src


def test_card_followed_by_a_bullet_lead_in_is_skipped():
    src = _post(_card() + "\n이번 기간 추가 발간물:\n\n- EQST Insight (1월호)\n")
    assert rw.transform(src) == src


def test_prose_that_is_not_a_finished_sentence_is_skipped():
    src = _post(_card() + "\n주요 구성요소는 다음 세 가지 항목으로 구성되어 있습니다:\n")
    assert rw.transform(src) == src


# --- Liquid attribute safety -------------------------------------------------


@pytest.mark.parametrize("quote", ['"', "“", "”", "‘", "’"])
def test_quotes_in_the_prose_never_reach_the_attribute(quote):
    prose = (
        f"공격자들은 이미 {quote}지금 수집, 나중에 복호화{quote} 전략을 실행하고 있습니다. "
        "현재의 암호화된 데이터가 안전하다는 가정은 유효하지 않습니다."
    )
    out = rw.transform(_post(_card() + "\n" + prose + "\n"))
    value = _summary_of(out)
    assert "지금 수집" in value, "the sentence should still be lifted"
    for unsafe in ('"', "“", "”"):
        assert unsafe not in value


def test_prose_containing_liquid_is_rejected():
    src = _post(_card() + "\n" + "이 문단은 {% raw %} 태그를 포함하는 긴 설명 문장입니다.\n")
    assert rw.transform(src) == src


def test_markdown_emphasis_and_code_spans_are_stripped():
    prose = "**개발자 도구**가 새로운 공격 표면으로 부상했으며 `go.sum` 검증이 필요하다고 보고되었습니다."
    value = _summary_of(rw.transform(_post(_card() + "\n" + prose + "\n")))
    assert "**" not in value and "`" not in value
    assert "개발자 도구" in value and "go.sum" in value


# --- runtime contract --------------------------------------------------------


def test_violates_summary_only_accepts_a_summary_change():
    src = _post(_card() + "\n" + _PROSE + "\n")
    assert not rw.violates_summary_only(src, rw.transform(src))


def test_violates_summary_only_catches_an_edit_outside_the_card():
    src = _post(_card() + "\n" + _PROSE + "\n")
    tampered = src.replace("The Hacker News", "Other Source")
    assert rw.violates_summary_only(src, tampered)


def test_violates_summary_only_catches_an_edit_to_the_prose():
    src = _post(_card() + "\n" + _PROSE + "\n")
    tampered = src.replace("CVE-2026-20122", "CVE-2026-99999")
    assert rw.violates_summary_only(src, tampered)


def test_main_aborts_when_the_contract_is_violated(tmp_path, monkeypatch):
    post = tmp_path / "2026-03-11-Weekly_Digest_x.md"
    post.write_text(_post(_card() + "\n" + _PROSE + "\n"), encoding="utf-8")
    monkeypatch.setattr(rw, "transform", lambda text: text.replace("High", "Low"))
    assert rw.main([str(post)]) == 1
    assert "High" in post.read_text(encoding="utf-8"), "the file must not be written"


# --- CLI ---------------------------------------------------------------------


def test_cli_dry_run_does_not_write(tmp_path):
    post = tmp_path / "2026-03-11-Weekly_Digest_x.md"
    src = _post(_card() + "\n" + _PROSE + "\n")
    post.write_text(src, encoding="utf-8")
    assert rw.main([str(post), "--dry-run"]) == 0
    assert post.read_text(encoding="utf-8") == src


def test_cli_writes_without_dry_run(tmp_path):
    post = tmp_path / "2026-03-11-Weekly_Digest_x.md"
    post.write_text(_post(_card() + "\n" + _PROSE + "\n"), encoding="utf-8")
    assert rw.main([str(post)]) == 0
    assert "CVE-2026-20122" in _summary_of(post.read_text(encoding="utf-8"))


def test_non_digest_post_is_skipped(tmp_path):
    post = tmp_path / "2026-03-11-Some_Guide.md"
    src = _post(_card() + "\n" + _PROSE + "\n")
    post.write_text(src, encoding="utf-8")
    assert rw.main([str(post)]) == 0
    assert post.read_text(encoding="utf-8") == src


def test_cli_has_no_all_flag():
    """C6: a writing mode must never default to the whole corpus."""
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "rewrite_template_echo_summaries.py"), "--all"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "unrecognized arguments" in proc.stderr


# --- single source of truth --------------------------------------------------


def test_uses_the_generator_truncation_helper():
    """C8: the corpus and the generator must agree on where a sentence may cut."""
    from scripts.news.content_generator import _truncate_korean_sentence

    assert rw._truncate_korean_sentence is _truncate_korean_sentence


# --- corpus ------------------------------------------------------------------


@pytest.mark.parametrize(
    "path", sorted((REPO / "_posts").glob("*Weekly_Digest*.md")), ids=lambda p: p.name
)
def test_corpus_transform_never_escapes_the_summary(path):
    original = path.read_text(encoding="utf-8")
    assert not rw.violates_summary_only(original, rw.transform(original))
