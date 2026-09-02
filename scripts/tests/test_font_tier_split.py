"""Invariants for the 2-tier Noto Sans KR split.

The bandwidth win of the tier split rests on the `unicode-range` in
`assets/css/font-tier2.css` describing exactly what the tier-2 woff2 files
contain, with no overlap onto tier-1. If the two drift apart the failure is
silent in both directions:

  * range too wide (overlaps tier-1) → browsers fetch tier-2 for glyphs tier-1
    already had, i.e. back to the pre-2026-08-10 waste.
  * range too narrow (misses part of what tier-2 ships) → a rare syllable
    resolves to no face at all and renders in the system fallback font forever.

Both artifacts come from one codepoint set in
`scripts/build/generate_noto_2tier_subset.py`, so these tests assert the
on-disk outputs still agree with each other and with the committed woff2 cmaps.

Two coverage questions are asked here and they are NOT the same question:

``test_every_corpus_syllable_is_covered_by_a_shipped_tier``
    ENFORCING, and a correctness gate. Every Hangul syllable the published
    corpus renders must appear in the cmap of a shipped woff2 — tier-1 OR
    tier-2. Until 2026-09-02 tier-2 carried the entire remaining Hangul block,
    so this held vacuously and no test asserted it; shrinking tier-2 to the
    KS X 1001 margin is what makes it load-bearing. A syllable outside both
    tiers renders in the system fallback font, silently and permanently.

``test_corpus_syllables_outside_tier1_are_reported``
    NON-ENFORCING, and a performance hint. Cron publishes digests without
    regenerating fonts, so a syllable landing in tier-2 rather than tier-1 is
    routine: it costs one deferred stylesheet fetch, not correctness.

See docs/optimization/NOTO_SANS_SELF_HOST_RUNBOOK.md.
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
    ksx1001_syllables,
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


def test_tier2_range_is_disjoint_from_tier1():
    """No syllable may be claimed by both tiers.

    Overlap is the expensive direction: the browser would pull the tier-2
    faces to render glyphs the preloaded tier-1 already carries.
    """
    margin = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))[0]
    covered = {ord(c) for c in _tier1_syllables()}
    overlap = margin & covered
    assert not overlap, (
        f"{len(overlap)} tier-1 syllable(s) also claimed by tier-2 "
        f"(e.g. {''.join(chr(c) for c in sorted(overlap)[:10])}) — "
        "browsers would fetch tier-2 needlessly"
    )


def test_tier2_range_covers_the_declared_ksx1001_margin():
    """Tier-2 must still be the KS X 1001 margin, not just today's corpus tail.

    Pinned because the cheap version of this shrink — ship only the ~20
    syllables the corpus currently uses outside tier-1 — passes every other
    test in this file and every gate in CI, and then breaks the first time a
    digest introduces a novel syllable. The margin is the deliberate part.
    """
    margin = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))[0]
    covered = {ord(c) for c in _tier1_syllables()}
    expected = ksx1001_syllables() - covered
    missing = expected - margin
    assert not missing, (
        f"{len(missing)} KS X 1001 syllable(s) covered by neither tier "
        f"(e.g. {''.join(chr(c) for c in sorted(missing)[:10])}) — "
        "the margin has been narrowed below its documented floor"
    )


def test_tier2_range_stays_inside_hangul_block():
    tail = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))[0]
    stray = {cp for cp in tail if not (HANGUL_START <= cp <= HANGUL_END)}
    assert not stray, (
        f"tier-2 must only claim U+AC00-D7A3, got {len(stray)} stray codepoints"
    )


def test_tier2_css_matches_generator_output():
    """The committed CSS is byte-identical to a fresh render — no hand edits.

    The codepoint set is taken from the shipped weight-400 woff2 cmap rather
    than recomputed from the corpus: that keeps this a check on the CSS text
    (header, url(), descriptor formatting) instead of a second, weaker copy of
    the margin rule, which `test_tier2_range_covers_the_declared_ksx1001_margin`
    already owns.
    """
    margin = {
        cp
        for cp in _cmap_codepoints(FONTS_DIR / "noto-sans-kr-400-tier2.woff2")
        if HANGUL_START <= cp <= HANGUL_END
    }
    assert TIER2_CSS.read_text(encoding="utf-8") == render_tier2_css(margin)


@pytest.mark.parametrize("weight", [400, 700])
def test_woff2_cmaps_match_the_declared_split(weight: int):
    """Each woff2's actual Hangul cmap agrees with the range it is declared under."""
    covered = {ord(c) for c in _tier1_syllables()}
    margin = _parse_unicode_ranges(TIER2_CSS.read_text(encoding="utf-8"))[0]

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
    assert tier2_hangul == margin, (
        f"tier-2 woff2 (weight {weight}) cmap disagrees with the font-tier2.css range: "
        f"{len(margin - tier2_hangul)} declared-but-absent, {len(tier2_hangul - margin)} present-but-undeclared"
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


def test_tier2_stays_a_margin_not_the_whole_block():
    """Tier-2 must not silently regrow into the full Hangul tail.

    Before 2026-09-02 tier-2 spanned all 10,128 non-corpus syllables at 964 KB
    across the two weights, of which the corpus reached 22. Widening the margin
    back to the block would pass every other test here, because every other
    test only asks that the artifacts agree with each other.
    """
    total_kb = 0.0
    for weight in (400, 700):
        size_kb = (
            FONTS_DIR / f"noto-sans-kr-{weight}-tier2.woff2"
        ).stat().st_size / 1024
        assert size_kb <= 120, (
            f"tier-2 weight {weight} is {size_kb:.1f} KB (budget 120 KB) — "
            "the margin has been widened; see --max-tier2-kb in the generator"
        )
        total_kb += size_kb
    assert total_kb <= 240, f"tier-2 totals {total_kb:.1f} KB across both weights"


def _head_modified(woff2: Path) -> int:
    pytest.importorskip("fontTools", reason="fonttools not installed")
    from fontTools.ttLib import TTFont

    font = TTFont(woff2)
    try:
        return int(font["head"].modified)
    finally:
        font.close()


def test_tier2_build_is_not_clock_stamped():
    """Both tier-2 weights must carry ONE `head.modified`, inherited from the source.

    fontTools stamps the wall clock into `head.modified` unless
    `recalcTimestamp` is disabled, which makes the woff2 bytes a function of
    when you built rather than what you built. The tell is that the two weights
    are written seconds apart and so disagree: the committed tier-1 pair, built
    before the fix, reads 3869170260 / 3869170269 — nine seconds. A shared
    value means the timestamp came from the pinned source font instead.

    Tier-1 is deliberately not asserted here. Its bytes are frozen from the
    2026-08-10 build and regenerating them is out of scope for the tier-2
    shrink; a future full regeneration will bring it under this rule too.
    """
    modified = {
        w: _head_modified(FONTS_DIR / f"noto-sans-kr-{w}-tier2.woff2")
        for w in (400, 700)
    }
    assert modified[400] == modified[700], (
        f"tier-2 head.modified differs between weights ({modified}) — the build "
        "is clock-stamped again, so identical inputs no longer yield identical "
        "bytes. See recalcTimestamp in generate_noto_2tier_subset.subset_woff2."
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
# Corpus coverage
# ---------------------------------------------------------------------------


def _shipped_hangul_codepoints() -> set[int]:
    """Every Hangul codepoint reachable from a shipped woff2, across both tiers.

    Read from the woff2 cmaps rather than from `noto_subset_top1k.txt` and
    `font-tier2.css`, because those are declarations: the question this
    answers is what a browser can actually render, and only the fonts know
    that.
    """
    shipped: set[int] = set()
    for weight in (400, 700):
        for tier in ("tier1", "tier2"):
            shipped |= {
                cp
                for cp in _cmap_codepoints(
                    FONTS_DIR / f"noto-sans-kr-{weight}-{tier}.woff2"
                )
                if HANGUL_START <= cp <= HANGUL_END
            }
    return shipped


def test_every_corpus_syllable_is_covered_by_a_shipped_tier():
    """ENFORCING. A published syllable outside tier-1 UNION tier-2 never renders.

    It falls back to whatever the OS supplies, at a different weight and
    metrics, on every visit, forever — and nothing on the page reports it. That
    is why this is an assertion and not the warning below.

    Fix by regenerating the tail so the new syllable is folded in:
        python3 scripts/build/generate_noto_2tier_subset.py --only-tier2
    (or a full run, which additionally promotes it into preloaded tier-1).
    """
    counts, _total = hangul_frequency(CORPUS_GLOBS)
    assert counts, "corpus scan found no Hangul at all — the globs are broken"
    shipped = _shipped_hangul_codepoints()
    uncovered = sorted(
        (c for c in counts if ord(c) not in shipped), key=lambda c: -counts[c]
    )
    assert not uncovered, (
        f"{len(uncovered)} corpus syllable(s) ship in NEITHER tier "
        f"({''.join(uncovered[:20])}) — they render in the system fallback "
        "font. Regenerate: "
        "python3 scripts/build/generate_noto_2tier_subset.py --only-tier2"
    )


def test_corpus_syllables_outside_tier1_are_reported():
    """NON-ENFORCING. Tier-1 misses cost a fetch, not correctness.

    Deliberately separate from the assertion above: cron publishes digests
    without regenerating fonts, so this drifts by design between font rebuilds.
    Promoting it to a failure would make every novel syllable a red main, which
    is not what a deferred stylesheet fetch deserves.
    """
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
