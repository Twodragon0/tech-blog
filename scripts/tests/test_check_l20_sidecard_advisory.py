"""Tests for the side-card advisory regression gate."""
from __future__ import annotations

from pathlib import Path

from scripts import check_l20_sidecard_advisory as gate

_MARKER = "<!-- profile: high-quality-cover (L20 Hero+2-Card) -->"
_HERO = '<g transform="translate(332,360)"><text x="-148" y="-82">SECURITY ADVISORY</text></g>'
_TR = '<g transform="translate(800,230)"><text x="-148" y="-82">SECURITY ADVISORY</text></g>'
_BR = '<g transform="translate(800,490)"><text x="-148" y="-82">SECURITY ADVISORY</text></g>'


def test_hero_advisory_is_allowed():
    svg = f"<svg>{_MARKER}{_HERO}</svg>"
    assert gate._side_card_advisory_offsets(svg) == []


def test_top_right_advisory_flagged():
    svg = f"<svg>{_MARKER}{_TR}</svg>"
    assert len(gate._side_card_advisory_offsets(svg)) == 1


def test_two_side_advisories_flagged():
    svg = f"<svg>{_MARKER}{_HERO}{_TR}{_BR}</svg>"
    # hero allowed, both side cards flagged
    assert len(gate._side_card_advisory_offsets(svg)) == 2


def test_check_file_ok_for_hero_only(tmp_path: Path):
    p = tmp_path / "cover.svg"
    p.write_text(f"<svg>{_MARKER}{_HERO}</svg>", encoding="utf-8")
    ok, _ = gate.check_file(p)
    assert ok is True


def test_check_file_fails_for_side_card(tmp_path: Path):
    p = tmp_path / "cover.svg"
    p.write_text(f"<svg>{_MARKER}{_BR}</svg>", encoding="utf-8")
    ok, msg = gate.check_file(p)
    assert ok is False and "side-card advisory" in msg


def test_non_l20_cover_is_skipped(tmp_path: Path):
    p = tmp_path / "plain.svg"
    p.write_text(f"<svg>{_BR}</svg>", encoding="utf-8")  # has side advisory but no L20 marker
    ok, msg = gate.check_file(p)
    assert ok is True and "skip" in msg


def test_main_exit_codes(tmp_path: Path):
    clean = tmp_path / "clean.svg"
    clean.write_text(f"<svg>{_MARKER}{_HERO}</svg>", encoding="utf-8")
    bad = tmp_path / "bad.svg"
    bad.write_text(f"<svg>{_MARKER}{_TR}</svg>", encoding="utf-8")
    assert gate.main([str(clean)]) == 0
    assert gate.main([str(bad)]) == 1


def test_live_corpus_has_no_side_card_advisory():
    """Backstop: the live corpus must stay clean (the demotion fix held)."""
    assert gate.main([]) == 0
