#!/usr/bin/env python3
"""The QR-URL fixer has to match the QR block it is pointed at.

Until 2026-08-21 ``_QR_BLOCK_RE`` anchored the scan label on ``x="1122"
y="614"``. The QR geometry then moved — the enlarged 108px block puts the label
at ``x="1134" y="486"`` — and the regex kept compiling, kept running, and
matched nothing:

    Total scanned:      200
    Changed/needs-fix:  0
    Already correct:    0
    No QR block found:  200

``Changed: 0`` is what a healthy corpus prints too, which is why a 100% miss
survived. Two things are pinned here: the matcher is anchored on the label's
text rather than its coordinates (so it spans both geometries), and a total
miss is reported as an error instead of a clean run.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scripts import fix_qr_url_in_covers as _mod  # noqa: E402

ASSETS = REPO / "assets" / "images"

# The two geometries that have shipped. Only the label coordinates differ.
_LEGACY_84PX = (
    '<g transform="translate(1080,504)" filter="url(#softShadow)">'
    '<rect width="100" height="100" fill="#FFFFFF"/>'
    '<path fill="#0A1020" d="M0 0h7v7H0z"/>'
    "</g>\n"
    '<text x="1122" y="614" font-size="11">scan / full post</text>'
)
_CURRENT_108PX = (
    '<g transform="translate(1080,504)" filter="url(#softShadow)">'
    '<rect width="132" height="132" fill="#FFFFFF"/>'
    '<path fill="#0A1020" d="M0 0h7v7H0z"/>'
    "</g>\n"
    '<text x="1134" y="486" font-size="11">scan / full post</text>'
)


def test_matches_the_current_geometry() -> None:
    assert _mod._QR_BLOCK_RE.search(_CURRENT_108PX), (
        "the fixer cannot see the QR block shape that is actually on disk"
    )


def test_still_matches_the_legacy_geometry() -> None:
    """Text-anchoring is only worth it if it spans both revisions."""
    assert _mod._QR_BLOCK_RE.search(_LEGACY_84PX)


def test_is_not_anchored_on_label_coordinates() -> None:
    """The specific defect: a coordinate in the pattern re-breaks on the next tweak."""
    pattern = _mod._QR_BLOCK_RE.pattern
    for coord in ('x=\\"1122\\"', 'y=\\"614\\"', 'x=\\"1134\\"', 'y=\\"486\\"'):
        assert coord not in pattern, (
            f"_QR_BLOCK_RE anchors the scan label on {coord}. The label moved once "
            "already and the pattern silently matched 200/200 covers as 'no QR "
            "block found'. Anchor on the label text."
        )


def test_the_live_corpus_is_actually_matched() -> None:
    """Non-vacuity against reality — this is the regression that occurred.

    A unit test over synthetic strings would have passed throughout the whole
    period the fixer was blind, because the synthetic string was written from
    the same stale assumption as the regex.
    """
    covers = sorted(ASSETS.glob("*Tech_*Weekly_Digest_*.svg"))
    assert covers, f"no digest covers under {ASSETS}"
    missed = [p.name for p in covers if not _mod._QR_BLOCK_RE.search(p.read_text(encoding="utf-8"))]
    assert not missed, (
        f"{len(missed)}/{len(covers)} live covers are invisible to the fixer, "
        f"e.g. {missed[:3]}"
    )


def test_total_miss_is_an_error_not_a_clean_report(tmp_path, monkeypatch, capsys) -> None:
    """Zero matches across every file means the template drifted."""
    cover = tmp_path / "2026-01-01-Tech_Security_Weekly_Digest_Nothing.svg"
    cover.write_text("<svg><!-- no QR block at all --></svg>", encoding="utf-8")
    monkeypatch.setattr(_mod, "ROOT", tmp_path)

    rc = _mod.main(["--check", "--glob", "*.svg"])
    assert rc == 1, "a corpus where nothing matched still reported success"
    assert "no QR block matched in ANY" in capsys.readouterr().err


def test_partial_miss_is_not_an_error(tmp_path, monkeypatch) -> None:
    """Hand-drawn covers legitimately carry no QR; only a TOTAL miss is a defect."""
    (tmp_path / "2026-01-01-Tech_Security_Weekly_Digest_A.svg").write_text(
        _CURRENT_108PX, encoding="utf-8"
    )
    (tmp_path / "2026-01-02-Tech_Security_Weekly_Digest_B.svg").write_text(
        "<svg></svg>", encoding="utf-8"
    )
    monkeypatch.setattr(_mod, "ROOT", tmp_path)
    assert _mod.main(["--check", "--glob", "*.svg"]) == 0
