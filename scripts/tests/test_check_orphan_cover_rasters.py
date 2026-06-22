"""Tests for the orphan-cover-raster gate."""
from __future__ import annotations

from pathlib import Path

from scripts import check_orphan_cover_rasters as gate


def _touch(p: Path) -> None:
    p.write_bytes(b"x")


def test_clean_when_raster_has_base_svg(tmp_path: Path):
    _touch(tmp_path / "2026-01-01-Foo.svg")
    for suf in ("_og.png", "_og.webp", "_og.avif", "_card.webp", "_card.avif"):
        _touch(tmp_path / f"2026-01-01-Foo{suf}")
    assert gate.orphan_rasters(tmp_path) == []
    assert gate.main([str(tmp_path)]) == 0


def test_flags_raster_without_base_svg(tmp_path: Path):
    # base .svg intentionally absent (simulates a rename leftover)
    _touch(tmp_path / "2026-01-01-Renamed_Old_og.png")
    _touch(tmp_path / "2026-01-01-Renamed_Old_card.webp")
    orphans = gate.orphan_rasters(tmp_path)
    assert {p.name for p in orphans} == {
        "2026-01-01-Renamed_Old_og.png",
        "2026-01-01-Renamed_Old_card.webp",
    }
    assert gate.main([str(tmp_path)]) == 1


def test_ignores_non_raster_files(tmp_path: Path):
    _touch(tmp_path / "2026-01-01-Foo.svg")
    _touch(tmp_path / "robots.txt")
    _touch(tmp_path / "section-tech.svg")
    assert gate.orphan_rasters(tmp_path) == []


def test_live_corpus_has_no_orphan_rasters():
    """Backstop: the live corpus must stay clean (45 orphans removed 2026-06-22)."""
    assert gate.main([]) == 0
