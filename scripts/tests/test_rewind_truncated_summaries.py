"""Tests for scripts/rewind_truncated_summaries.py.

PR #506 fixed the generator's blind ``ko_summary[:200]`` slice, but the 128 card
summaries already cut mid-sentence stayed that way. Measured 2026-08-07:

* 128 truncated summaries across 79 digests
* rewinding to the last complete sentence keeps 132 chars on average (66%)
* 126 of 128 keep at least one complete sentence; **2 keep none** and are left
  untouched rather than emptied

Rewinding only ever DROPS a trailing partial sentence, so the result is always a
prefix of what was already published — no fetching, no LLM, nothing invented.
That prefix property is the contract these tests pin.
"""
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import rewind_truncated_summaries as rw  # noqa: E402

_FM = '---\nlayout: post\ntitle: "x"\n---\n\n'


def _card(summary, **extra):
    attrs = "".join(f'  {k}="{v}"\n' for k, v in extra.items())
    return (
        "{% include news-card.html\n"
        '  title="제목"\n'
        '  url="https://example.com/a"\n'
        f'  summary="{summary}"\n'
        f"{attrs}"
        '  source="Example"\n'
        "%}\n"
    )


def _truncated(head="가" * 150):
    """A summary shaped like the corpus defect: complete sentence + cut tail."""
    return f"{head}라고 경고합니다. 공격자가 원격으로 루트 접근 권한을 얻을 수 있게 하는 Java 바이트 스트림 역"


# --- the rewind --------------------------------------------------------------


def test_truncated_summary_rewinds_to_the_last_complete_sentence():
    src = _FM + _card(_truncated())
    out = rw.transform(src)
    assert '경고합니다."' in out
    assert "Java 바이트 스트림 역" not in out


def test_result_is_always_a_prefix_of_the_original():
    original = _truncated()
    out = rw.transform(_FM + _card(original))
    new = out.split('summary="')[1].split('"\n')[0]
    assert original.startswith(new), "rewind may only drop a tail, never rewrite"


def test_rewind_keeps_the_sentence_period():
    out = rw.transform(_FM + _card(_truncated()))
    new = out.split('summary="')[1].split('"\n')[0]
    assert new.endswith("다.")


# --- what must NOT change ----------------------------------------------------


def test_summary_with_no_complete_sentence_is_left_alone():
    """2 corpus cards are in this state — emptying them would be worse."""
    src = _FM + _card("가" * 210)
    assert rw.transform(src) == src


def test_short_summary_is_left_alone():
    src = _FM + _card("짧은 요약입니다")
    assert rw.transform(src) == src


def test_properly_terminated_long_summary_is_left_alone():
    src = _FM + _card("가" * 200 + "라고 밝혔습니다.")
    assert rw.transform(src) == src


def test_other_attributes_are_never_touched():
    nested = (
        "https://images.cointelegraph.com/cdn-cgi/image/f=auto,w=1200/"
        "https://s3.cointelegraph.com/uploads/x.jpg"
    )
    out = rw.transform(_FM + _card(_truncated(), image=nested))
    assert f'image="{nested}"' in out


def test_prose_outside_cards_is_untouched():
    body = "본문 문장이 여기 있고 잘리지 않았습니다.\n\n"
    out = rw.transform(_FM + body + _card(_truncated()))
    assert body in out


def test_transform_is_idempotent():
    once = rw.transform(_FM + _card(_truncated()))
    assert rw.transform(once) == once


# --- runtime contract --------------------------------------------------------


def test_shrink_only_contract_rejects_added_text():
    old = _FM + _card(_truncated())
    assert rw._violates_shrink_only(old, old + "extra") is True
    assert rw._violates_shrink_only(old, rw.transform(old)) is False


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("완성된 문장입니다. 잘린 꼬리", "완성된 문장입니다."),
        ("완성된 문장입니다.", "완성된 문장입니다."),
        ("완성 문장 없음", "완성 문장 없음"),
        ("", ""),
    ],
)
def test_rewind_unit(raw, expected):
    assert rw.rewind(raw) == expected


# --- CLI ---------------------------------------------------------------------


def test_cli_dry_run_does_not_write(tmp_path):
    p = tmp_path / "2026-08-07-Tech_Blog_Weekly_Digest_x.md"
    src = _FM + _card(_truncated())
    p.write_text(src, encoding="utf-8")
    assert rw.main([str(p), "--dry-run"]) == 0
    assert p.read_text(encoding="utf-8") == src


def test_non_digest_is_skipped(tmp_path):
    p = tmp_path / "2026-08-07-Some_Guide.md"
    src = _FM + _card(_truncated())
    p.write_text(src, encoding="utf-8")
    assert rw.main([str(p)]) == 0
    assert p.read_text(encoding="utf-8") == src
