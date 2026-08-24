"""Invariants for the 2-tier Noto Sans KR split.

The bandwidth win of the tier split rests on ONE property: the
`unicode-range` in `assets/css/font-tier2.css` must be exactly the set of
Hangul syllables the tier-1 woff2 files do NOT contain. If the two drift
apart the failure is silent in both directions:

  * range too wide (overlaps tier-1) → browsers fetch ~500 KB of tier-2 for
    glyphs tier-1 already had, i.e. back to the pre-2026-08-10 waste.
  * range too narrow (misses part of the tail) → a rare syllable resolves to
    no face at all and renders in the system fallback font forever.

Both artifacts come from one codepoint set in
`scripts/build/generate_noto_2tier_subset.py`, so these tests assert the
on-disk outputs still agree with each other and with the committed woff2
cmaps. Corpus coverage (does tier-1 still cover every published syllable?) is
reported as a WARNING rather than a failure — cron publishes digests without
regenerating fonts, and an uncovered syllable degrades gracefully via tier-2
instead of breaking the build. See docs/optimization/NOTO_SANS_SELF_HOST_RUNBOOK.md.
"""

from __future__ import annotations

import re
import sys
import warnings
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "build"))

from generate_noto_2tier_subset import (  # noqa: E402
    CORPUS_GLOBS,
    HANGUL_END,
    HANGUL_START,
    compact_ranges,
    format_unicode_range,
    hangul_frequency,
    render_tier2_css,
)

TIER2_CSS = REPO_ROOT / "assets" / "css" / "font-tier2.css"
TOP1K = REPO_ROOT / "scripts" / "build" / "noto_subset_top1k.txt"
FONTS_DIR = REPO_ROOT / "assets" / "fonts"

RANGE_RE = re.compile(r"U\+([0-9A-F]{4,6})(?:-([0-9A-F]{4,6}))?")


def _parse_unicode_ranges(css: str) -> list[set[int]]:
    """Return one codepoint set per `unicode-range:` declaration in `css`."""
    out: list[set[int]] = []
    for line in css.splitlines():
        stripped = line.strip()
        if not stripped.startswith("unicode-range:"):
            continue
        cps: set[int] = set()
        for lo_hex, hi_hex in RANGE_RE.findall(stripped):
            lo = int(lo_hex, 16)
            hi = int(hi_hex, 16) if hi_hex else lo
            cps.update(range(lo, hi + 1))
        out.append(cps)
    return out


def _tier1_syllables() -> set[str]:
    return set(TOP1K.read_text(encoding="utf-8").split())


def _cmap_codepoints(woff2: Path) -> set[int]:
    fontTools = pytest.importorskip("fontTools", reason="fonttools not installed")
    assert fontTools  # silence linters; the import is the guard
    from fontTools.ttLib import TTFont

    font = TTFont(woff2)
    try:
        return set(font.getBestCmap().keys())
    finally:
        font.close()


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def test_compact_ranges_collapses_runs():
    assert compact_ranges([5, 6, 7, 10, 12, 13]) == [(5, 7), (10, 10), (12, 13)]


def test_compact_ranges_empty():
    assert compact_ranges([]) == []


def test_format_unicode_range_uses_single_codepoint_form():
    assert format_unicode_range([0xAC00, 0xAC02, 0xAC03]) == "U+AC00, U+AC02-AC03"


def test_format_unicode_range_roundtrips_through_parser():
    cps = {0xAC00, 0xAC01, 0xAC05, 0xD7A3}
    css = f"  unicode-range: {format_unicode_range(cps)};"
    assert _parse_unicode_ranges(css) == [cps]


# ---------------------------------------------------------------------------
# On-disk artifact invariants
# ---------------------------------------------------------------------------


def test_tier2_css_exists_and_declares_both_weights():
    assert TIER2_CSS.exists(), (
        f"{TIER2_CSS} missing — run generate_noto_2tier_subset.py"
    )
    css = TIER2_CSS.read_text(encoding="utf-8")
    assert css.count("@font-face") == 2, "tier-2 must declare weight 400 and 700"
    assert "noto-sans-kr-400-tier2.woff2" in css
    assert "noto-sans-kr-700-tier2.woff2" in css
    assert "font-display: swap" in css


def test_tier2_css_uses_baseurl_safe_relative_font_urls():
    """`url()` must be relative so the GitHub Pages backup (--baseurl /tech-blog) resolves.

    A root-relative `/assets/fonts/...` inside this stylesheet would resolve to
    twodragon0.github.io/assets/fonts/... on the backup origin and 404.
    """
    css = TIER2_CSS.read_text(encoding="utf-8")
    assert "url('/assets/fonts/" not in css
    for weight in (400, 700):
        assert f"url('../fonts/noto-sans-kr-{weight}-tier2.woff2')" in css


def test_tier2_css_weights_share_one_range():
    ranges = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))
    assert len(ranges) == 2, "expected exactly one unicode-range per weight"
    assert ranges[0] == ranges[1], (
        "both weights ship the same tail, so their ranges must match"
    )


def test_tier2_range_is_exact_complement_of_tier1_corpus():
    """The declared tail == all Hangul minus the tier-1 syllable list."""
    tail = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))[0]
    covered = {ord(c) for c in _tier1_syllables()}
    expected = set(range(HANGUL_START, HANGUL_END + 1)) - covered

    overlap = tail & covered
    assert not overlap, (
        f"{len(overlap)} tier-1 syllable(s) also claimed by tier-2 "
        f"(e.g. {''.join(chr(c) for c in sorted(overlap)[:10])}) — "
        "browsers would fetch ~500 KB of tier-2 needlessly"
    )
    missing = expected - tail
    assert not missing, (
        f"{len(missing)} tail codepoint(s) absent from font-tier2.css — "
        "those syllables would silently fall back to the system font"
    )


def test_tier2_range_stays_inside_hangul_block():
    tail = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))[0]
    stray = {cp for cp in tail if not (HANGUL_START <= cp <= HANGUL_END)}
    assert not stray, (
        f"tier-2 must only claim U+AC00-D7A3, got {len(stray)} stray codepoints"
    )


def test_tier2_css_matches_generator_output():
    """The committed CSS is byte-identical to a fresh render — no hand edits."""
    covered = {ord(c) for c in _tier1_syllables()}
    tail = set(range(HANGUL_START, HANGUL_END + 1)) - covered
    assert TIER2_CSS.read_text(encoding="utf-8") == render_tier2_css(tail)


@pytest.mark.parametrize("weight", [400, 700])
def test_woff2_cmaps_match_the_declared_split(weight: int):
    """Each woff2's actual Hangul cmap agrees with the range it is declared under."""
    covered = {ord(c) for c in _tier1_syllables()}
    tail = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))[0]

    tier1_hangul = {
        cp
        for cp in _cmap_codepoints(FONTS_DIR / f"noto-sans-kr-{weight}-tier1.woff2")
        if HANGUL_START <= cp <= HANGUL_END
    }
    tier2_hangul = {
        cp
        for cp in _cmap_codepoints(FONTS_DIR / f"noto-sans-kr-{weight}-tier2.woff2")
        if HANGUL_START <= cp <= HANGUL_END
    }

    assert tier1_hangul == covered, (
        f"tier-1 woff2 (weight {weight}) cmap disagrees with noto_subset_top1k.txt: "
        f"{len(covered - tier1_hangul)} listed-but-absent, {len(tier1_hangul - covered)} present-but-unlisted"
    )
    assert tier2_hangul == tail, (
        f"tier-2 woff2 (weight {weight}) cmap disagrees with the font-tier2.css range: "
        f"{len(tail - tier2_hangul)} declared-but-absent, {len(tier2_hangul - tail)} present-but-undeclared"
    )


def test_tier1_preload_budget_holds():
    """Tier-1 is preloaded on every page — keep it under the 230 KB/weight budget."""
    for weight in (400, 700):
        size_kb = (
            FONTS_DIR / f"noto-sans-kr-{weight}-tier1.woff2"
        ).stat().st_size / 1024
        assert size_kb <= 230, (
            f"tier-1 weight {weight} is {size_kb:.1f} KB (budget 230 KB)"
        )


# ---------------------------------------------------------------------------
# Wiring: nothing may force the tail onto the critical path
# ---------------------------------------------------------------------------


def test_tier2_is_never_preloaded():
    """A `<link rel=preload>` for tier-2 would undo the on-demand behaviour."""
    for name in ("_includes/font-face.html", "_includes/head.html"):
        text = (REPO_ROOT / name).read_text(encoding="utf-8")
        for line in text.splitlines():
            if 'rel="preload"' in line or "rel='preload'" in line:
                assert "tier2" not in line, f"{name} preloads tier-2: {line.strip()}"


def test_head_runtime_holds_no_tier2_loader():
    """Tier-2 must stay declarative — no JS loader, no tainted href assignment.

    The JS path was removed on 2026-08-10: assigning a `data-*` attribute to
    `link.href` tripped CodeQL `js/xss-through-dom`, and the FontFace variant it
    replaced forced the ~996 KB download outright. Line comments are stripped
    first because the surviving comment block names both the file and the
    anti-pattern it warns against.
    """
    js = (REPO_ROOT / "assets" / "js" / "head-runtime.js").read_text(encoding="utf-8")
    code = re.sub(r"^\s*//.*$", "", js, flags=re.MULTILINE)
    for banned in (
        "loadFontTier2",
        "font-tier2.css",
        "tier2.woff2",
        "FontFace",
        "data-font-tier2-href",
    ):
        assert banned not in code, f"head-runtime.js must not reference {banned}"


def _strip_comments(html: str) -> str:
    """Drop Liquid comments and CSS block comments.

    font-face.html documents the bare `/assets/fonts/...` anti-pattern in prose,
    so scanning the raw file would flag the very comment that warns about it.
    """
    html = re.sub(
        r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}",
        "",
        html,
        flags=re.DOTALL,
    )
    return re.sub(r"/\*.*?\*/", "", html, flags=re.DOTALL)


def test_tier1_font_urls_go_through_relative_url():
    """Tier-1 src + preload must survive the backup's --baseurl "/tech-blog".

    A bare `/assets/fonts/...` resolved to twodragon0.github.io/assets/fonts/...
    on the GitHub Pages backup and 404'd (verified live 2026-08-10: 404 on the
    bare URL, 200 / 206,788 B on the /tech-blog/ prefixed one). The failure was
    silent — Korean fell back to the system font and both preloads were wasted
    404 round-trips. `absolute_url` is NOT an acceptable substitute: it prepends
    site.baseurl onto site.url and breaks the other origin instead.
    """
    body = _strip_comments(
        (REPO_ROOT / "_includes" / "font-face.html").read_text(encoding="utf-8")
    )
    assert "url('/assets/fonts/" not in body, (
        "tier-1 @font-face src bypasses relative_url"
    )
    assert 'href="/assets/fonts/' not in body, (
        "tier-1 preload href bypasses relative_url"
    )
    assert "absolute_url" not in body, (
        "absolute_url prepends site.baseurl — wrong for assets"
    )
    for weight in (400, 700):
        asset = f"/assets/fonts/noto-sans-kr-{weight}-tier1.woff2"
        refs = [ln for ln in body.splitlines() if asset in ln]
        # once in the @font-face src, once in the preload link
        assert len(refs) == 2, f"expected 2 references to {asset}, got {len(refs)}"
        for ref in refs:
            assert "relative_url" in ref, (
                f"tier-1 font URL bypasses relative_url: {ref.strip()}"
            )


def test_strip_comments_keeps_the_guard_honest():
    """The guard must ignore prose in comments but still see real markup."""
    documented = """{%- comment -%}
      Never write url('/assets/fonts/x.woff2') here.
    {%- endcomment -%}
    <style>/* nor href="/assets/fonts/y.woff2" in a CSS comment */</style>"""
    assert "/assets/fonts/" not in _strip_comments(documented)

    offending = """{%- comment -%} docs {%- endcomment -%}
    <style>src: url('/assets/fonts/noto-sans-kr-400-tier1.woff2') format('woff2');</style>"""
    assert "url('/assets/fonts/" in _strip_comments(offending)


def test_font_face_include_links_tier2_as_deferred_css():
    """The tail stylesheet is linked declaratively, non-blocking, baseurl-safe."""
    body = _strip_comments(
        (REPO_ROOT / "_includes" / "font-face.html").read_text(encoding="utf-8")
    )
    links = [ln for ln in body.splitlines() if "font-tier2.css" in ln]
    assert len(links) == 1, (
        f"expected exactly one tier-2 stylesheet link, got {len(links)}"
    )
    link = links[0]
    assert "relative_url" in link, (
        "tier-2 stylesheet href must survive --baseurl /tech-blog"
    )
    assert 'media="print"' in link, "must not block render"
    assert "deferred-css" in link, (
        "the promoter script in head.html flips media to all via this class"
    )
    assert 'rel="stylesheet"' in link
    assert "preload" not in link, (
        "a preload would fetch it eagerly and defeat the deferral"
    )


def test_deferred_css_promoter_still_exists():
    """The tier-2 link relies on head.html's promoter to reach media="all"."""
    head = (REPO_ROOT / "_includes" / "head.html").read_text(encoding="utf-8")
    assert "link.deferred-css" in head, (
        "promoter query gone — tier-2 would stay print-only"
    )
    assert "promotePrintStylesheet" in head


# ---------------------------------------------------------------------------
# Coverage report (warning only — cron publishes without regenerating fonts)
# ---------------------------------------------------------------------------


def test_corpus_coverage_is_reported_not_enforced():
    covered = _tier1_syllables()
    counts, _total = hangul_frequency(CORPUS_GLOBS)
    uncovered = sorted(set(counts) - covered, key=lambda c: -counts[c])
    if uncovered:
        sample = "".join(uncovered[:20])
        warnings.warn(
            f"{len(uncovered)} corpus syllable(s) outside tier-1 (e.g. {sample}) — "
            "they render via on-demand tier-2. Regenerate fonts to fold them into "
            "tier-1: python3 scripts/build/generate_noto_2tier_subset.py",
            UserWarning,
            stacklevel=2,
        )
    assert len(covered) > 900, "tier-1 syllable list looks truncated"
