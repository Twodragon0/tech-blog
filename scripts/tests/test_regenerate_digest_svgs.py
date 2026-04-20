#!/usr/bin/env python3
"""regenerate_digest_svgs.py 의 순수 함수 단위 테스트.

side-effect 함수 (파일 쓰기, cairosvg 호출) 는 의도적으로 제외.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.regenerate_digest_svgs import (
    BLUE,
    GREEN,
    ICON_FUNCS,
    PHASE_A,
    PHASE_B,
    POSTS,
    RED,
    CardData,
    Palette,
    _FORBIDDEN_CHARS,
    _iter_targets,
    _pill_width,
    _validate_card,
    _validate_text,
    render_svg,
)


# ---------------------------------------------------------------------------
# _pill_width
# ---------------------------------------------------------------------------


def test_pill_width_minimum_for_empty():
    """빈 라벨도 최소 80 픽셀 보장."""
    assert _pill_width("") == 80


def test_pill_width_minimum_for_short():
    """짧은 라벨(1자)도 최소 80."""
    assert _pill_width("X") == 80


def test_pill_width_grows_with_label():
    """긴 라벨은 최솟값보다 크다."""
    assert _pill_width("ZERO-DAY ALERT CRITICAL") > 80


def test_pill_width_formula():
    """공식 8*len + 32 가 80 초과인 경우 그대로 반환."""
    label = "ABCDEFGHIJ"  # len=10 → 8*10+32=112 > 80
    assert _pill_width(label) == 8 * len(label) + 32


# ---------------------------------------------------------------------------
# _validate_text — Korean 가드
# ---------------------------------------------------------------------------


def test_validate_text_korean_raises():
    """한국어 문자가 있으면 ValueError."""
    with pytest.raises(ValueError, match="Korean"):
        _validate_text("안전보안", "test_field")


def test_validate_text_korean_mixed_raises():
    """영어+한국어 혼합도 거부."""
    with pytest.raises(ValueError, match="Korean"):
        _validate_text("AWS 보안", "test_field")


def test_validate_text_english_ok():
    """순수 영어 + 숫자는 통과."""
    _validate_text("CVE-2026-12345 patched", "test_field")  # no exception


def test_validate_text_empty_ok():
    """빈 문자열은 통과."""
    _validate_text("", "test_field")  # no exception


# ---------------------------------------------------------------------------
# _validate_text — 금지 특수문자 가드
# ---------------------------------------------------------------------------


def test_validate_text_middle_dot_raises():
    """가운뎃점(·, U+00B7) 거부."""
    with pytest.raises(ValueError, match="Forbidden"):
        _validate_text("A\u00b7B", "test_field")


def test_validate_text_em_dash_raises():
    """em dash(—, U+2014) 거부."""
    with pytest.raises(ValueError, match="Forbidden"):
        _validate_text("A\u2014B", "test_field")


def test_validate_text_curly_quote_raises():
    """곡선 따옴표(\u201c) 거부."""
    with pytest.raises(ValueError, match="Forbidden"):
        _validate_text("\u201chello\u201d", "test_field")


def test_validate_text_all_forbidden_chars_covered():
    """_FORBIDDEN_CHARS 에 정의된 모든 문자가 각각 거부된다."""
    for ch in _FORBIDDEN_CHARS:
        with pytest.raises(ValueError):
            _validate_text(ch, "forbidden_char_check")


# ---------------------------------------------------------------------------
# _validate_card
# ---------------------------------------------------------------------------


def test_validate_card_clean_passes():
    """영어 전용 CardData 는 예외 없이 통과."""
    card = CardData(
        label="SUPPLY",
        headline_1="GlassWorm Hits",
        headline_2="72 Exts",
        tag="Open VSX",
        desc_1="Dev tool chain",
        desc_2="turned hostile",
        palette=RED,
    )
    _validate_card("test_basename", card)  # no exception


def test_validate_card_korean_in_label_raises():
    """label 에 한국어가 있으면 ValueError."""
    card = CardData(
        label="보안경고",
        headline_1="Alert",
        headline_2="Critical",
        tag="tag",
        desc_1="desc1",
        desc_2="desc2",
        palette=BLUE,
    )
    with pytest.raises(ValueError, match="Korean"):
        _validate_card("test_basename", card)


def test_validate_card_korean_in_desc_raises():
    """desc_1 에 한국어가 있으면 ValueError."""
    card = CardData(
        label="SUPPLY",
        headline_1="Attack",
        headline_2="Campaign",
        tag="tag",
        desc_1="공격 탐지됨",
        desc_2="clean desc",
        palette=GREEN,
    )
    with pytest.raises(ValueError, match="Korean"):
        _validate_card("test_basename", card)


# ---------------------------------------------------------------------------
# render_svg
# ---------------------------------------------------------------------------


def _make_cards(palette_a=RED, palette_b=BLUE, palette_c=GREEN):
    return (
        CardData("LABEL A", "Head 1A", "Head 2A", "Tag A", "Desc 1A", "Desc 2A", palette_a, "botnet"),
        CardData("LABEL B", "Head 1B", "Head 2B", "Tag B", "Desc 1B", "Desc 2B", palette_b, "identity"),
        CardData("LABEL C", "Head 1C", "Head 2C", "Tag C", "Desc 1C", "Desc 2C", palette_c, "stack"),
    )


def test_render_svg_returns_string():
    """render_svg 는 문자열을 반환한다."""
    result = render_svg("2026-04-17", _make_cards())
    assert isinstance(result, str)


def test_render_svg_contains_date():
    """날짜가 SVG 출력에 포함된다."""
    result = render_svg("2026-04-17", _make_cards())
    assert "2026-04-17" in result


def test_render_svg_contains_svg_tag():
    """유효한 SVG 래퍼로 감싼다."""
    result = render_svg("2026-04-17", _make_cards())
    assert result.strip().startswith("<svg")
    assert result.strip().endswith("</svg>")


def test_render_svg_wrong_card_count_raises():
    """카드가 3개가 아니면 AssertionError."""
    two_cards = _make_cards()[:2]
    with pytest.raises(AssertionError):
        render_svg("2026-04-17", two_cards)


def test_render_svg_includes_all_labels():
    """세 카드의 라벨이 모두 SVG 안에 포함된다."""
    result = render_svg("2026-04-17", _make_cards())
    assert "LABEL A" in result
    assert "LABEL B" in result
    assert "LABEL C" in result


# ---------------------------------------------------------------------------
# _iter_targets
# ---------------------------------------------------------------------------


def test_iter_targets_phase_a():
    """phase='a' 는 PHASE_A 키만 반환."""
    keys = set(_iter_targets("a"))
    assert keys == set(PHASE_A.keys())
    assert not (keys & set(PHASE_B.keys()) - set(PHASE_A.keys()))


def test_iter_targets_phase_b():
    """phase='b' 는 PHASE_B 키만 반환."""
    keys = set(_iter_targets("b"))
    assert keys == set(PHASE_B.keys())


def test_iter_targets_all():
    """phase='all' 은 PHASE_A + PHASE_B 합집합을 포함한다."""
    keys = set(_iter_targets("all"))
    assert set(PHASE_A.keys()).issubset(keys)
    assert set(PHASE_B.keys()).issubset(keys)


def test_iter_targets_all_equals_posts():
    """phase='all' 결과는 POSTS 딕셔너리 키와 동일."""
    assert set(_iter_targets("all")) == set(POSTS.keys())


# ---------------------------------------------------------------------------
# Palette 상수 — 키 검증
# ---------------------------------------------------------------------------


def test_palette_keys_are_distinct():
    """RED / BLUE / GREEN 팔레트 key 는 서로 다르다."""
    assert RED.key == "red"
    assert BLUE.key == "blue"
    assert GREEN.key == "green"


def test_palette_accent_ids():
    """팔레트 accent_id 는 SVG gradient ID 와 일치해야 한다."""
    assert RED.accent_id == "accentRed"
    assert BLUE.accent_id == "accentBlue"
    assert GREEN.accent_id == "accentGreen"


# ---------------------------------------------------------------------------
# ICON_FUNCS — 등록 여부 및 호출 확인
# ---------------------------------------------------------------------------


def test_icon_funcs_known_names():
    """필수 아이콘 이름이 레지스트리에 존재한다."""
    for name in ("botnet", "identity", "stack", "cloud", "alert", "patch", "chip", "bot", "code", "globe", "lock"):
        assert name in ICON_FUNCS, f"Missing icon: {name}"


def test_icon_funcs_callable_and_return_string():
    """각 아이콘 함수가 호출 가능하고 문자열을 반환한다."""
    for name, func in ICON_FUNCS.items():
        result = func("accentBlue").format(cx=160)
        assert isinstance(result, str), f"Icon {name} did not return str"


def test_icon_funcs_contain_transform():
    """각 아이콘 SVG 에는 translate transform 이 포함된다."""
    for name, func in ICON_FUNCS.items():
        result = func("accentRed").format(cx=160)
        assert "translate" in result, f"Icon {name} missing translate"


# ---------------------------------------------------------------------------
# CardData — default icon 동작
# ---------------------------------------------------------------------------


def test_card_data_default_icon_empty():
    """icon 인자 생략 시 빈 문자열이 기본값."""
    card = CardData("L", "H1", "H2", "T", "D1", "D2", RED)
    assert card.icon == ""


def test_card_data_explicit_icon():
    """icon 명시 시 그대로 유지."""
    card = CardData("L", "H1", "H2", "T", "D1", "D2", BLUE, "lock")
    assert card.icon == "lock"


# ---------------------------------------------------------------------------
# Phase payload 건전성 — 실제 데이터가 validator 를 통과하는지 smoke 검사
# ---------------------------------------------------------------------------


def test_phase_a_all_cards_pass_validate():
    """Phase A 모든 카드가 _validate_card 를 통과한다."""
    for basename, (_, cards) in PHASE_A.items():
        for card in cards:
            _validate_card(basename, card)  # no exception


def test_phase_b_all_cards_pass_validate():
    """Phase B 모든 카드가 _validate_card 를 통과한다."""
    for basename, (_, cards) in PHASE_B.items():
        for card in cards:
            _validate_card(basename, card)  # no exception
