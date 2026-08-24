"""Tests for scripts/rewrite_template_echo_summaries.py.

Measured on the corpus 2026-08-07, before any code was written:

* 271 template-echo summaries in 24 digests — 226 ``news-card`` + 45
  ``news-spotlight-item`` (matching only ``{%`` and only ``news-card`` finds 61)
* 221 of the 226 ``news-card`` items are followed by a prose paragraph
* **0** of the 45 ``news-spotlight-item`` entries are. They sit back to back
  inside a ``{% capture %}`` block, so the "prose" 20 lines below belongs to the
  트렌드 분석 section, not to the article

REPLACE mode therefore repairs only what the post can actually evidence. DROP
mode deletes the ``summary=`` attribute of the 45 spotlight items, because a
sentence claiming an analysis nobody performed is worse than no sentence.

The two modes carry separate runtime contracts and these tests keep them
separate: replace may only touch a summary VALUE, drop may only delete whole
spotlight summary LINES. Neither may launder a change through the other.
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


def _spotlight(summary=_ECHO, title="Nano Banana 프롬프팅 가이드", trailing=False):
    """A spotlight item shaped like the corpus: summary last, one attr per line."""
    lines = [
        "{% include news-spotlight-item.html",
        f'  title="{title}"',
        '  url="https://example.com/n"',
        '  source="Google Cloud Blog"',
        '  tag="Cloud / Platform"',
    ]
    if summary is None:
        pass
    elif trailing:
        # 3 of the 45 keep an attribute after `summary=`.
        lines.insert(-1, f'  summary="{summary}"')
    else:
        lines.append(f'  summary="{summary}"')
    lines.append("%}")
    return "\n".join(lines) + "\n"


def _capture(*items):
    return "{% capture spotlight_items %}\n" + "".join(items) + "{% endcapture %}\n"


def _post(body):
    return _FM + body


def _summary_of(text, index=0):
    cards = list(rw.CARD_RE.finditer(text))
    return rw.SUMMARY_RE.search(cards[index].group(0)).group(2)


# --- the rewrite -------------------------------------------------------------


def test_template_echo_summary_is_replaced_with_the_following_prose():
    out = rw.replace_echo_summaries(_post(_card() + "\n" + _PROSE + "\n"))
    assert "공격 벡터와 영향 범위를 점검하고" not in out
    assert "CVE-2026-20122" in _summary_of(out)


def test_whitespace_control_variant_is_matched():
    out = rw.replace_echo_summaries(_post(_card(dash=True) + "\n" + _PROSE + "\n"))
    assert "CVE-2026-20122" in _summary_of(out)


def test_summary_heading_between_card_and_prose_is_skipped():
    body = _card() + "\n#### 요약\n\n" + _PROSE + "\n"
    assert "CVE-2026-20122" in _summary_of(rw.replace_echo_summaries(_post(body)))


def test_at_most_two_sentences_are_lifted():
    prose = "첫 번째 문장은 이 기사에 대한 충분한 길이의 설명입니다. 두 번째 문장도 마찬가지로 충분히 깁니다. 세 번째 문장은 버려져야 합니다."
    out = rw.replace_echo_summaries(_post(_card() + "\n" + prose + "\n"))
    assert "세 번째 문장" not in _summary_of(out)
    assert "두 번째 문장" in _summary_of(out)


def test_summary_stays_within_the_generator_cap():
    prose = "가" * 260 + "라고 보고되었습니다. 두 번째 문장입니다."
    out = rw.replace_echo_summaries(_post(_card() + "\n" + prose + "\n"))
    for card in rw.CARD_RE.finditer(out):
        found = rw.SUMMARY_RE.search(card.group(0))
        assert len(found.group(2)) <= rw.MAX_SUMMARY_LEN


def test_no_text_is_invented_when_the_helper_would_pad():
    """``_truncate_korean_sentence`` appends "… 등이 확인되었습니다." on its fallback
    path. A generator may write that; a corpus rewrite may not."""
    prose = (
        "첫 문장은 아주 길게 이어지는 설명으로 " * 12
    ).strip() + "입니다. 두 번째 문장입니다."
    src = _post(_card() + "\n" + prose + "\n")
    assert rw.replace_echo_summaries(src) == src


def test_the_replacement_is_copied_from_the_post_body():
    body = _card() + "\n" + _PROSE + "\n"
    value = _summary_of(rw.replace_echo_summaries(_post(body)))
    assert value in _PROSE, "every character must come from the paragraph below"


def test_replace_is_idempotent():
    src = _post(_card() + "\n" + _PROSE + "\n")
    once = rw.replace_echo_summaries(src)
    assert rw.replace_echo_summaries(once) == once


# --- what it must NOT touch --------------------------------------------------


def test_non_template_summary_is_left_alone():
    src = _post(
        _card(summary="이미 기사 고유의 사실을 담은 요약입니다.") + "\n" + _PROSE + "\n"
    )
    assert rw.replace_echo_summaries(src) == src


def test_other_attributes_are_byte_identical():
    image = (
        "https://images.cointelegraph.com/images/528_aHR0cHM6Ly9zMy5jb2ludGVsZWdyYXBo"
        ".jpg?w=1&u=https://s3.example.com/x.jpg"
    )
    src = _post(_card(image=image) + "\n" + _PROSE + "\n")
    out = rw.replace_echo_summaries(src)
    assert out != src
    assert f'  image="{image}"' in out
    assert '  url="https://example.com/a?utm_source=rss"' in out


def test_multiline_liquid_include_is_untouched_outside_the_summary():
    """T1: the corrupted cover images of PR #509 came from exactly this shape."""
    src = _post(_card(image="https://cdn.example.com/p/https://s3.example.com/a.jpg"))
    src += "\n" + _PROSE + "\n"
    out = rw.replace_echo_summaries(src)
    assert not rw.violates_summary_only(src, out)


def test_front_matter_is_never_edited():
    fm = (
        "---\nlayout: post\n"
        'description: "… 공격 벡터와 영향 범위를 점검하고, 대응 체크리스트를 제시합니다."\n'
        "---\n\n"
    )
    src = fm + _card() + "\n" + _PROSE + "\n"
    out = rw.replace_echo_summaries(src)
    assert out.startswith(fm)


def test_card_inside_a_code_fence_is_not_rewritten():
    src = _post("```liquid\n" + _card() + "```\n\n" + _PROSE + "\n")
    assert rw.replace_echo_summaries(src) == src


def test_indented_closing_fence_closes_the_block():
    """T3: 2026-02-08 closes its fences with leading whitespace."""
    src = _post("```text\nnoise\n  ```\n\n" + _card() + "\n" + _PROSE + "\n")
    assert "CVE-2026-20122" in _summary_of(rw.replace_echo_summaries(src))


def test_spotlight_items_packed_in_a_capture_block_are_skipped():
    """The measured reality: 45/45 spotlight defects have no prose of their own."""
    src = _post(_capture(_spotlight(), _spotlight()))
    assert rw.replace_echo_summaries(src) == src


def test_card_followed_by_a_table_is_skipped():
    table = "| 원칙 | 설명 |\n|------|------|\n| 투명성 | 설명가능성 요건 |\n"
    src = _post(_card() + "\n" + table)
    assert rw.replace_echo_summaries(src) == src


def test_card_followed_by_a_bullet_lead_in_is_skipped():
    src = _post(_card() + "\n이번 기간 추가 발간물:\n\n- EQST Insight (1월호)\n")
    assert rw.replace_echo_summaries(src) == src


def test_prose_that_is_not_a_finished_sentence_is_skipped():
    src = _post(
        _card() + "\n주요 구성요소는 다음 세 가지 항목으로 구성되어 있습니다:\n"
    )
    assert rw.replace_echo_summaries(src) == src


# --- narrowing the quote: two sentences, else one ----------------------------
#
# A whole paragraph is judged as one unit only in the happy case. When the
# two-sentence candidate is unusable — too long to cut without the helper
# padding it, or trailing into something that is not a finished sentence — the
# first sentence alone is still evidence the post carries, so it is quoted
# instead of abandoning the card to its template echo. Measured: this is the
# entire difference between 6 and 1 unrepairable cards in the corpus.


def test_two_sentence_overflow_falls_back_to_one_sentence():
    """Sentence 1 fits the cap, sentences 1+2 do not. Quote sentence 1."""
    first = "CNCF에서 Harbor 컨테이너 레지스트리를 프로덕션 환경에서 운영하기 위한 가이드를 발표했습니다."
    second = (
        "고가용성과 보안, 스토리지, 모니터링, 네트워크 구성 등 "
        + "다섯 가지 핵심 영역을 중심으로 정리한 " * 6
        + "실무 권장사항입니다."
    )
    assert len(first) <= rw.MAX_SUMMARY_LEN < len(first + " " + second)
    value = _summary_of(
        rw.replace_echo_summaries(_post(_card() + "\n" + first + " " + second + "\n"))
    )
    assert value == first


def test_paragraph_trailing_into_a_byline_still_yields_its_sentences():
    """A trailing "(작성: …)" is not a sentence; it must not veto the two above it."""
    prose = _PROSE + " (작성: Matt Corallo)"
    value = _summary_of(rw.replace_echo_summaries(_post(_card() + "\n" + prose + "\n")))
    assert value in _PROSE
    assert "Matt Corallo" not in value


def test_paragraph_trailing_into_a_colon_lead_in_falls_back_to_one_sentence():
    first = "AWS Korea Blog의 시리즈 2편으로, 7주 만에 구축한 Agentic AI 플랫폼의 핵심 인프라를 다룹니다."
    prose = (
        first
        + " 이번 글의 주제는 엔터프라이즈급 에이전트 시스템의 세 가지 핵심 구성요소입니다:"
    )
    value = _summary_of(rw.replace_echo_summaries(_post(_card() + "\n" + prose + "\n")))
    assert value == first


def test_paragraph_cut_off_mid_sentence_still_yields_its_finished_first():
    """2026-03-16 ships a paragraph the generator truncated mid-word. The first
    sentence survived intact and is the only thing quoted."""
    first = "AI 코딩 에이전트의 동작 방식을 자신의 애플리케이션 백엔드에도 적용할 수 있습니다."
    prose = (
        first
        + " 하나의 에이전트에게 코드 리뷰와 테스트 작성을 모두 맡기면 컨텍스트가 길어지면서 자신이 작성한"
    )
    value = _summary_of(rw.replace_echo_summaries(_post(_card() + "\n" + prose + "\n")))
    assert value == first


def test_fallback_still_refuses_to_invent_when_one_sentence_also_overflows():
    """The narrowing is a second attempt, not a licence to pad. When neither
    candidate survives the no-invented-text check the card is left alone."""
    prose = ("첫 문장은 아주 길게 이어지는 설명으로 " * 12).strip() + "입니다."
    src = _post(_card() + "\n" + prose + "\n")
    assert rw.replace_echo_summaries(src) == src


def test_fallback_does_not_rescue_a_paragraph_with_no_finished_sentence():
    src = _post(
        _card()
        + "\n주요 구성요소는 다음 세 가지 항목으로 충분히 길게 구성되어 있습니다:\n"
    )
    assert rw.replace_echo_summaries(src) == src


# --- Liquid attribute safety -------------------------------------------------


@pytest.mark.parametrize("quote", ['"', "“", "”", "‘", "’"])
def test_quotes_in_the_prose_never_reach_the_attribute(quote):
    prose = (
        f"공격자들은 이미 {quote}지금 수집, 나중에 복호화{quote} 전략을 실행하고 있습니다. "
        "현재의 암호화된 데이터가 안전하다는 가정은 유효하지 않습니다."
    )
    out = rw.replace_echo_summaries(_post(_card() + "\n" + prose + "\n"))
    value = _summary_of(out)
    assert "지금 수집" in value, "the sentence should still be lifted"
    for unsafe in ('"', "“", "”"):
        assert unsafe not in value


def test_prose_containing_liquid_is_rejected():
    src = _post(
        _card() + "\n" + "이 문단은 {% raw %} 태그를 포함하는 긴 설명 문장입니다.\n"
    )
    assert rw.replace_echo_summaries(src) == src


def test_markdown_emphasis_and_code_spans_are_stripped():
    prose = "**개발자 도구**가 새로운 공격 표면으로 부상했으며 `go.sum` 검증이 필요하다고 보고되었습니다."
    value = _summary_of(rw.replace_echo_summaries(_post(_card() + "\n" + prose + "\n")))
    assert "**" not in value and "`" not in value
    assert "개발자 도구" in value and "go.sum" in value


# --- drop mode ---------------------------------------------------------------


def test_spotlight_echo_summary_line_is_deleted():
    src = _post(_capture(_spotlight(), _spotlight(title="LeakBase 포럼 압수")))
    out = rw.drop_spotlight_echo_summaries(src)
    assert "summary=" not in out
    assert out.count("news-spotlight-item.html") == 2


def test_drop_leaves_a_valid_include_with_every_other_attribute():
    out = rw.drop_spotlight_echo_summaries(_post(_capture(_spotlight())))
    assert out.count("{% include news-spotlight-item.html") == 1
    assert out.count("%}") == _post(_capture(_spotlight())).count("%}")
    for attr in ("title=", "url=", "source=", "tag="):
        assert attr in out
    assert "\n\n%}" not in out, "no blank line should be left where the attr was"


def test_drop_keeps_a_trailing_attribute_after_the_summary():
    """3 of the 45 have another attribute after ``summary=``."""
    src = _post(_capture(_spotlight(trailing=True)))
    out = rw.drop_spotlight_echo_summaries(src)
    assert "summary=" not in out
    assert '  tag="Cloud / Platform"' in out


def test_drop_is_idempotent():
    once = rw.drop_spotlight_echo_summaries(_post(_capture(_spotlight())))
    assert rw.drop_spotlight_echo_summaries(once) == once


def test_spotlight_without_the_template_phrase_is_not_dropped():
    src = _post(
        _capture(_spotlight(summary="Nano Banana 프롬프팅 가이드가 공개되었습니다."))
    )
    assert rw.drop_spotlight_echo_summaries(src) == src


def test_drop_never_touches_a_news_card():
    src = _post(_card() + "\n" + _PROSE + "\n")
    assert rw.drop_spotlight_echo_summaries(src) == src


def test_drop_skips_a_fenced_spotlight_include():
    src = _post("```liquid\n" + _spotlight() + "```\n")
    assert rw.drop_spotlight_echo_summaries(src) == src


def test_replace_and_drop_stay_in_their_own_lane():
    src = _post(_card() + "\n" + _PROSE + "\n\n" + _capture(_spotlight()))
    replaced = rw.replace_echo_summaries(src)
    dropped = rw.drop_spotlight_echo_summaries(src)
    assert "CVE-2026-20122" in replaced and _ECHO in replaced, "spotlight untouched"
    assert _ECHO in dropped.split("news-card.html")[1].split("%}")[0], "card untouched"
    assert dropped.count("summary=") == src.count("summary=") - 1


def test_both_modes_compose_into_transform():
    src = _post(_card() + "\n" + _PROSE + "\n\n" + _capture(_spotlight()))
    out = rw.transform(src)
    assert rw.count_defects(out) == 0


# --- runtime contract: replace -----------------------------------------------


def test_violates_summary_only_accepts_a_summary_change():
    src = _post(_card() + "\n" + _PROSE + "\n")
    assert not rw.violates_summary_only(src, rw.replace_echo_summaries(src))


def test_violates_summary_only_catches_an_edit_outside_the_card():
    src = _post(_card() + "\n" + _PROSE + "\n")
    tampered = src.replace("The Hacker News", "Other Source")
    assert rw.violates_summary_only(src, tampered)


def test_violates_summary_only_catches_an_edit_to_the_prose():
    src = _post(_card() + "\n" + _PROSE + "\n")
    tampered = src.replace("CVE-2026-20122", "CVE-2026-99999")
    assert rw.violates_summary_only(src, tampered)


# --- runtime contract: drop --------------------------------------------------


def test_drop_contract_accepts_the_line_deletion():
    src = _post(_capture(_spotlight()))
    out = rw.drop_spotlight_echo_summaries(src)
    assert out != src
    assert not rw.violates_spotlight_line_drop_only(src, out)


def test_drop_contract_rejects_deleting_another_attribute():
    src = _post(_capture(_spotlight()))
    tampered = src.replace('  url="https://example.com/n"\n', "")
    assert rw.violates_spotlight_line_drop_only(src, tampered)


def test_drop_contract_rejects_deleting_a_news_card_summary():
    src = _post(_card() + "\n" + _PROSE + "\n")
    tampered = src.replace(f'  summary="{_ECHO}"\n', "")
    assert rw.violates_spotlight_line_drop_only(src, tampered)


def test_drop_contract_rejects_a_rewrite_dressed_as_a_deletion():
    src = _post(_capture(_spotlight()))
    tampered = src.replace(_ECHO, "새로 지어낸 요약입니다.")
    assert rw.violates_spotlight_line_drop_only(src, tampered)


def test_drop_contract_rejects_added_lines():
    src = _post(_capture(_spotlight()))
    assert rw.violates_spotlight_line_drop_only(src, src + "\n추가된 줄\n")


def test_drop_contract_rejects_losing_a_whole_card():
    src = _post(_capture(_spotlight(), _spotlight(title="LeakBase 포럼 압수")))
    tampered = src.replace(_spotlight(title="LeakBase 포럼 압수"), "")
    assert rw.violates_spotlight_line_drop_only(src, tampered)


def test_card_shape_detector_is_independent_of_the_drop_rule():
    """C5: the audit must not call the rule's line bookkeeping."""
    src = _post(_capture(_spotlight()))
    shapes = rw._card_attribute_shapes(src)
    assert shapes == [
        ("news-spotlight-item.html", ["title", "url", "source", "tag", "summary"])
    ]


@pytest.mark.parametrize("mode", ["replace", "drop"])
def test_main_aborts_when_a_mode_breaks_its_contract(mode, tmp_path, monkeypatch):
    post = tmp_path / "2026-03-11-Weekly_Digest_x.md"
    src = _post(_card() + "\n" + _PROSE + "\n\n" + _capture(_spotlight()))
    post.write_text(src, encoding="utf-8")
    rule, contract = rw.MODES[mode]
    monkeypatch.setitem(
        rw.MODES, mode, (lambda text: text.replace("High", "Low"), contract)
    )
    assert rw.main([str(post)]) == 1
    assert post.read_text(encoding="utf-8") == src, "the file must not be written"


# --- CLI ---------------------------------------------------------------------


def test_cli_mode_replace_leaves_spotlight_alone(tmp_path):
    post = tmp_path / "2026-03-11-Weekly_Digest_x.md"
    post.write_text(
        _post(_card() + "\n" + _PROSE + "\n\n" + _capture(_spotlight())),
        encoding="utf-8",
    )
    assert rw.main([str(post), "--mode", "replace"]) == 0
    assert _ECHO in post.read_text(encoding="utf-8")


def test_cli_mode_drop_leaves_news_card_alone(tmp_path):
    post = tmp_path / "2026-03-11-Weekly_Digest_x.md"
    post.write_text(
        _post(_card() + "\n" + _PROSE + "\n\n" + _capture(_spotlight())),
        encoding="utf-8",
    )
    assert rw.main([str(post), "--mode", "drop"]) == 0
    body = post.read_text(encoding="utf-8")
    assert _summary_of(body) == _ECHO, "the news-card echo must survive drop mode"
    assert body.count("summary=") == 1


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
        [
            sys.executable,
            str(REPO / "scripts" / "rewrite_template_echo_summaries.py"),
            "--all",
        ],
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
def test_corpus_replace_never_escapes_the_summary(path):
    original = path.read_text(encoding="utf-8")
    assert not rw.violates_summary_only(original, rw.replace_echo_summaries(original))


@pytest.mark.parametrize(
    "path", sorted((REPO / "_posts").glob("*Weekly_Digest*.md")), ids=lambda p: p.name
)
def test_corpus_drop_only_removes_spotlight_summary_lines(path):
    original = path.read_text(encoding="utf-8")
    dropped = rw.drop_spotlight_echo_summaries(original)
    assert not rw.violates_spotlight_line_drop_only(original, dropped)


@pytest.mark.parametrize(
    "path", sorted((REPO / "_posts").glob("*Weekly_Digest*.md")), ids=lambda p: p.name
)
def test_corpus_both_modes_are_idempotent(path):
    original = path.read_text(encoding="utf-8")
    once = rw.transform(original)
    assert rw.transform(once) == once
