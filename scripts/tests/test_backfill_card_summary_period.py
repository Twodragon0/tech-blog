"""Tests for scripts/backfill_card_summary_period.py.

PR #511 fixed the generator so new summaries keep their sentence-final period,
but the 16 cards already published stayed unterminated. This backfill applies
the SAME helper (`content_generator._restore_sentence_period`) to existing
`summary="…"` attributes — one source of truth, so the corpus and the generator
cannot drift apart.

It edits inside a Liquid include, which is exactly where a context-blind rewrite
corrupted cover images in PR #509. So the contract here is deliberately narrow:
the only permitted change to a file is a `.` appended to a `summary` value.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import backfill_card_summary_period as bf  # noqa: E402

_FM = '---\nlayout: post\ntitle: "x"\n---\n\n'


def _card(summary, include="news-card", open_ws="", close_ws="", **extra):
    attrs = "".join(f'  {k}="{v}"\n' for k, v in extra.items())
    return (
        f"{{%{open_ws} include {include}.html\n"
        '  title="제목"\n'
        '  url="https://example.com/a"\n'
        f'  summary="{summary}"\n'
        f"{attrs}"
        '  source="Example"\n'
        f"{close_ws}%}}\n"
    )


# Every shape the corpus actually uses (C11). `\s` does not match `-`, so the
# `{%-` rows were invisible to this script until 2026-08-07.
_CARD_SHAPES = {
    "plain": {},
    "whitespace_control": {"open_ws": "-", "close_ws": "-"},
    "dash_open_only": {"open_ws": "-"},
    "spotlight": {"include": "news-spotlight-item"},
    "spotlight_dash": {
        "include": "news-spotlight-item",
        "open_ws": "-",
        "close_ws": "-",
    },
}


# --- what gets fixed ---------------------------------------------------------


def test_sentence_ending_summary_gains_its_period():
    out = bf.transform(_FM + _card("공격자가 npm 패키지를 장악했습니다"))
    assert 'summary="공격자가 npm 패키지를 장악했습니다."' in out


def test_multi_sentence_summary_gains_only_the_final_period():
    src = _FM + _card("A가 발생했습니다. B가 확인됐습니다")
    out = bf.transform(src)
    assert 'summary="A가 발생했습니다. B가 확인됐습니다."' in out


@pytest.mark.parametrize("shape,kwargs", sorted(_CARD_SHAPES.items()))
def test_every_card_shape_is_reached(shape, kwargs):
    """C11 recall: a `{%-` or spotlight card must be fixed like a plain one."""
    out = bf.transform(_FM + _card("공격자가 서버를 장악했습니다", **kwargs))
    assert 'summary="공격자가 서버를 장악했습니다."' in out, shape


# --- what must NOT change ----------------------------------------------------


def test_noun_ended_headline_is_left_alone():
    src = _FM + _card("AI 기반 보안 에이전트로 취약점 탐지, 검증, 수정 제안")
    assert bf.transform(src) == src


def test_already_terminated_summary_is_left_alone():
    src = _FM + _card("공격자가 침투했습니다.")
    assert bf.transform(src) == src


def test_other_attributes_are_never_touched():
    """`image=` carries a URL nested in a URL — the PR #509 corruption site."""
    nested = (
        "https://images.cointelegraph.com/cdn-cgi/image/f=auto,w=1200/"
        "https://s3.cointelegraph.com/uploads/x.jpg"
    )
    src = _FM + _card("공격이 확산됐습니다", image=nested)
    out = bf.transform(src)
    assert f'image="{nested}"' in out
    assert 'summary="공격이 확산됐습니다."' in out


def test_prose_outside_cards_is_untouched():
    src = _FM + "본문 문장입니다\n\n" + _card("공격이 확산됐습니다")
    out = bf.transform(src)
    assert "본문 문장입니다\n" in out
    assert "본문 문장입니다." not in out


def test_transform_is_idempotent():
    once = bf.transform(_FM + _card("공격이 확산됐습니다"))
    assert bf.transform(once) == once


# --- the narrow-diff contract ------------------------------------------------


def test_only_change_is_an_appended_period():
    src = _FM + _card("공격이 확산됐습니다", image="https://e.example/a.jpg")
    out = bf.transform(src)
    assert out.replace("확산됐습니다.", "확산됐습니다") == src


def test_uses_the_generator_helper_as_the_single_source_of_truth():
    from scripts.news.content_generator import _restore_sentence_period

    assert bf.restore is _restore_sentence_period


# --- CLI ---------------------------------------------------------------------


def test_cli_dry_run_does_not_write(tmp_path):
    p = tmp_path / "2026-08-07-Tech_Blog_Weekly_Digest_x.md"
    src = _FM + _card("공격이 확산됐습니다")
    p.write_text(src, encoding="utf-8")
    assert bf.main([str(p), "--dry-run"]) == 0
    assert p.read_text(encoding="utf-8") == src


def test_cli_writes_and_reports(tmp_path, capsys):
    p = tmp_path / "2026-08-07-Tech_Blog_Weekly_Digest_x.md"
    p.write_text(_FM + _card("공격이 확산됐습니다"), encoding="utf-8")
    assert bf.main([str(p)]) == 0
    assert 'summary="공격이 확산됐습니다."' in p.read_text(encoding="utf-8")
    assert "FIXED" in capsys.readouterr().out


@pytest.mark.parametrize("name", ["2026-08-07-Some_Guide.md"])
def test_non_digest_is_skipped(tmp_path, name):
    p = tmp_path / name
    src = _FM + _card("공격이 확산됐습니다")
    p.write_text(src, encoding="utf-8")
    assert bf.main([str(p)]) == 0
    assert p.read_text(encoding="utf-8") == src


def test_narrow_diff_check_rejects_a_removed_period():
    """Normalising both sides alone would accept a REMOVAL — direction matters."""
    old = _FM + _card("공격이 확산됐습니다.")
    new = _FM + _card("공격이 확산됐습니다")
    assert bf._violates_narrow_diff(old, new) is True
    assert bf._violates_narrow_diff(new, old) is False


# --- truncated summaries must not be disguised as complete -------------------


def test_truncated_summary_does_not_gain_a_period():
    """A summary cut at the old 200-char hard cap ends mid-thought.

    Some land on a sentence-ending morpheme by coincidence ("…설명했습니다"),
    and appending a period there would make the truncation LOOK complete —
    hiding the defect PR #506 fixed at the generator. 9 corpus cards are in
    this state; they need a re-summary, not punctuation.
    """
    long_cut = "가" * 190 + "라고 설명했습니다"
    assert len(long_cut) >= bf.TRUNCATION_SUSPECT_LEN
    src = _FM + _card(long_cut)
    assert bf.transform(src) == src


def test_short_summary_just_below_the_threshold_is_still_fixed():
    short = "가" * 150 + "라고 설명했습니다"
    assert len(short) < bf.TRUNCATION_SUSPECT_LEN
    assert f'summary="{short}."' in bf.transform(_FM + _card(short))
