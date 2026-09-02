"""Glyph-coverage gate for the self-hosted Noto Sans KR subsets.

Why this exists
---------------
`_includes/font-face.html` declares `unicode-range: ... U+AC00-D7A3`, i.e. the
whole Hangul syllables block, while each woff2 actually carries 2,350 of those
11,172 code points (KS X 1001 + corpus). Chrome does not walk the CSS fallback
stack for a code point that is inside a declared range but missing from the
face — it goes straight to OS system fallback. So a syllable outside the subset
renders in whatever the visitor's OS happens to have, silently, with no console
warning and no network error.

Cron auto-publishes digest posts, so that regression could land unattended.
This gate reads the real cmap out of the shipped woff2 files and fails when any
`_posts/*.md` syllable is absent. Deterministic, offline, no browser needed.

Fix procedure when this fails: re-run the generator. Its coverage set is
`KS X 1001 UNION corpus`, so it picks up the new syllable automatically:

    export NOTO_VF_URL="$(grep -o "https://[^']*" build.sh | head -1)"
    python3 scripts/build/generate_noto_subset.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "build"))

import generate_noto_subset as gen  # noqa: E402

WEIGHTS = (400, 700)


def _font_cmap(path: Path) -> set[int]:
    """Union of every cmap subtable's code points in `path`."""
    try:
        from fontTools.ttLib import TTFont
    except ImportError as exc:  # pragma: no cover - CI installs fonttools
        pytest.fail(
            "fontTools is required for the font coverage gate. "
            "Install it with `pip install 'fonttools[woff]>=4.55.0'` "
            f"(scripts/requirements-ci.txt pins it for CI). Import error: {exc}"
        )
    font = TTFont(path)
    try:
        codepoints: set[int] = set()
        for table in font["cmap"].tables:
            codepoints.update(table.cmap.keys())
        return codepoints
    finally:
        font.close()


@pytest.fixture(scope="module")
def corpus_counts() -> dict[str, int]:
    counts, total = gen.hangul_frequency("_posts/*.md")
    assert total > 0, "corpus has no Hangul — the gate would be vacuous"
    return counts


@pytest.mark.parametrize("weight", WEIGHTS)
def test_font_file_exists(weight: int) -> None:
    path = gen.font_path(weight)
    assert path.is_file(), f"missing subset: {path.relative_to(REPO_ROOT)}"


@pytest.mark.parametrize("weight", WEIGHTS)
def test_corpus_hangul_fully_covered(weight: int, corpus_counts: dict[str, int]) -> None:
    """Every Hangul syllable published in _posts/ must have a glyph."""
    path = gen.font_path(weight)
    cmap = _font_cmap(path)
    missing = sorted((c for c in corpus_counts if ord(c) not in cmap), key=ord)
    assert not missing, (
        f"{path.name} is missing {len(missing)} Hangul syllable(s) used in _posts/: "
        f"{''.join(missing[:60])}"
        + (" ..." if len(missing) > 60 else "")
        + " — re-run scripts/build/generate_noto_subset.py (see this file's docstring)."
    )


@pytest.mark.parametrize("weight", WEIGHTS)
def test_ksx1001_fully_covered(weight: int) -> None:
    """The declared KS X 1001 baseline must be present, not just the corpus.

    The filename says `ksx1001`; if the shipped face ever stopped carrying the
    full 2,350 the name would be a lie and cache-busting would not have
    happened.
    """
    cmap = _font_cmap(gen.font_path(weight))
    missing = sorted((c for c in gen.ksx1001_hangul() if ord(c) not in cmap), key=ord)
    assert not missing, f"{len(missing)} KS X 1001 syllable(s) missing from weight {weight}"


@pytest.mark.parametrize("weight", WEIGHTS)
def test_base_ranges_covered(weight: int) -> None:
    """Latin + Jamo + punctuation must be present too (spot-checked)."""
    cmap = _font_cmap(gen.font_path(weight))
    for ch in "AZaz09 .,-()/:%":
        assert ord(ch) in cmap, f"weight {weight} lacks {ch!r} (U+{ord(ch):04X})"


def test_hangul_list_matches_generator_coverage() -> None:
    """The checked-in coverage list must equal what the generator would emit.

    `scripts/build/noto_subset_hangul.txt` is a font-drift-gate source of truth
    (scripts/dev/check_font_drift.py). If it drifts from the generator's own
    coverage set, the gate stops meaning anything.
    """
    on_disk = set(gen.HANGUL_LIST_PATH.read_text(encoding="utf-8").split())
    assert on_disk == gen.hangul_coverage("_posts/*.md"), (
        "noto_subset_hangul.txt is stale — re-run scripts/build/generate_noto_subset.py"
    )


@pytest.mark.parametrize("weight", WEIGHTS)
def test_hangul_list_matches_font_cmap(weight: int) -> None:
    """Every syllable in the coverage list is really in the shipped woff2."""
    cmap = _font_cmap(gen.font_path(weight))
    listed = gen.HANGUL_LIST_PATH.read_text(encoding="utf-8").split()
    missing = [c for c in listed if ord(c) not in cmap]
    assert not missing, f"weight {weight} lacks {len(missing)} listed syllable(s)"


def test_no_tier2_font_references_remain() -> None:
    """The retired lazy tier must be gone from the runtime and the fonts dir."""
    leftovers = sorted(p.name for p in (REPO_ROOT / "assets" / "fonts").glob("*tier*.woff2"))
    assert not leftovers, f"stale tier woff2 still committed: {leftovers}"

    for rel in ("_includes/font-face.html", "assets/js/head-runtime.js"):
        text = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "-tier2.woff2" not in text, f"{rel} still references a tier-2 woff2"
        assert "new FontFace(" not in text, f"{rel} still injects a font at runtime"
