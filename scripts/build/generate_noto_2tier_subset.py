#!/usr/bin/env python3
"""
Generate a 2-tier woff2 subset of Noto Sans KR for self-hosting.

Strategy
--------
Korean web typography needs ~11k Hangul syllables (U+AC00-U+D7A3). The full
glyph set compresses to ~550 KB per weight in woff2 — too heavy to block first
paint. Frequency analysis of the rendered corpus (posts plus every template,
data file and script that can emit Korean text) shows only ~1k distinct
syllables are ever used. We therefore split into:

  Tier 1 (eager preload, ~205-215 KB / weight)
    * Latin Basic + Supplement + Extended-A (so European loanwords render)
    * Hangul Jamo (composing fallback)
    * CJK punctuation, halfwidth/fullwidth, arrows, geometry, misc symbols
    * Every Hangul syllable that appears anywhere in the corpus

  Tier 2 (on-demand safety net, ~470-500 KB / weight)
    * The Hangul tail: syllables NOT in the corpus

Both tiers share the family name, but their `unicode-range` descriptors are
disjoint: tier-1 declares the syllables it actually contains, tier-2 declares
exactly the tail. A browser therefore fetches tier-2 only when a page renders
a syllable the corpus has never used before — normally never. The tail
descriptor is emitted to `assets/css/font-tier2.css` (see TIER2_CSS_PATH),
which `head-runtime.js` attaches after `load` so it stays off the critical
path.

Before 2026-08-10 tier-2 was fetched unconditionally by the FontFace API on
every first visit — ~996 KB of glyphs no page needed. Keeping the descriptor
generated (not hand-written) is what makes the disjointness a build invariant
rather than a comment.

Source
------
We download the Noto Sans KR variable font (TTF subset) from the upstream
`notofonts/noto-cjk` GitHub repo, then instantiate it at wght=400 and
wght=700 before subsetting. This gives us a single deterministic input and
two static weights without depending on per-weight static OTFs.

Usage
-----
    python3 scripts/build/generate_noto_2tier_subset.py [--top-n N] [--posts-glob '_posts/*.md']

Outputs
-------
    scripts/build/noto_subset_top1k.txt
    assets/css/font-tier2.css
    assets/fonts/noto-sans-kr-{400,700}-{tier1,tier2}.woff2

Idempotent: re-running with the same corpus yields identical bytes.
"""

from __future__ import annotations

import argparse
import io
import os
import sys
import urllib.request
from pathlib import Path

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_FONTS_DIR = REPO_ROOT / "assets" / "fonts"
ASSETS_CSS_DIR = REPO_ROOT / "assets" / "css"
SCRIPTS_BUILD_DIR = REPO_ROOT / "scripts" / "build"
TOP1K_PATH = SCRIPTS_BUILD_DIR / "noto_subset_top1k.txt"
TIER2_CSS_PATH = ASSETS_CSS_DIR / "font-tier2.css"

# Every source that can put a Hangul syllable on a rendered page. `_posts` is
# the bulk; the rest matter because a syllable that appears ONLY in a template,
# data file or script (e.g. a UI label, a news headline) would otherwise land in
# the tail and make a browser fetch ~500 KB of tier-2 for one glyph.
# Deliberately excluded: root-level dev artifacts (analysis_report.json,
# package.json) — never rendered.
CORPUS_GLOBS = (
    "_posts/*.md",
    "_layouts/**/*.html",
    "_includes/**/*.html",
    "_sass/**/*.scss",
    "assets/js/**/*.js",
    "_data/**/*.json",
    "_data/**/*.yml",
    "_config.yml",
    "*.md",
    "*.html",
)

# Pinned upstream source: Noto Sans KR variable font (subset TTF) from
# notofonts/noto-cjk. Pinning to `main` for now — caller can override via env
# `NOTO_VF_URL` if reproducibility against a specific commit is required.
NOTO_VF_URL = os.environ.get(
    "NOTO_VF_URL",
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/Variable/TTF/Subset/NotoSansKR-VF.ttf",
)

# Hangul syllables block
HANGUL_START = 0xAC00
HANGUL_END = 0xD7A3

# Tier-1 always-included unicode ranges (covers Latin + Korean Jamo + symbols).
TIER1_BASE_RANGES = [
    (0x0020, 0x007F),  # Latin Basic
    (0x00A0, 0x00FF),  # Latin-1 Supplement
    (0x0100, 0x017F),  # Latin Extended-A
    (0x1100, 0x11FF),  # Hangul Jamo
    (0x3000, 0x303F),  # CJK Symbols and Punctuation
    (0xFF00, 0xFFEF),  # Halfwidth/Fullwidth
    (0x2190, 0x21FF),  # Arrows
    (0x25A0, 0x25FF),  # Geometric Shapes
    (0x2600, 0x26FF),  # Misc Symbols
]

# -----------------------------------------------------------------------------
# Frequency analysis
# -----------------------------------------------------------------------------


def hangul_frequency(globs: tuple[str, ...] | list[str]) -> tuple[dict[str, int], int]:
    """Count Hangul-syllable frequency across every file matching `globs`.

    Returns (counts, total_hangul_chars). Duplicate matches across globs are
    de-duplicated by resolved path so a file counted twice cannot skew the
    frequency ordering.
    """
    counts: dict[str, int] = {}
    total = 0
    seen: set[Path] = set()
    for glob in globs:
        for path in sorted(REPO_ROOT.glob(glob)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                print(f"  ! skipping {path}: {exc}", file=sys.stderr)
                continue
            for ch in text:
                cp = ord(ch)
                if HANGUL_START <= cp <= HANGUL_END:
                    counts[ch] = counts.get(ch, 0) + 1
                    total += 1
    return counts, total


def pick_top_n(counts: dict[str, int], n: int) -> tuple[list[str], int]:
    """Return top-N syllables by frequency (deterministic by code point on ties).

    `n <= 0` means "every syllable in the corpus" — the default, because full
    coverage costs only ~5 KB per weight and is what keeps tier-2 off the wire.
    """
    ordered = sorted(counts.items(), key=lambda kv: (-kv[1], ord(kv[0])))
    chosen = ordered if n <= 0 else ordered[:n]
    covered = sum(c for _, c in chosen)
    return [s for s, _ in chosen], covered


# -----------------------------------------------------------------------------
# unicode-range descriptors
# -----------------------------------------------------------------------------


def compact_ranges(codepoints: set[int] | list[int]) -> list[tuple[int, int]]:
    """Collapse a codepoint set into sorted, inclusive (lo, hi) runs."""
    ordered = sorted(codepoints)
    if not ordered:
        return []
    runs: list[tuple[int, int]] = []
    lo = prev = ordered[0]
    for cp in ordered[1:]:
        if cp == prev + 1:
            prev = cp
            continue
        runs.append((lo, prev))
        lo = prev = cp
    runs.append((lo, prev))
    return runs


def format_unicode_range(codepoints: set[int] | list[int]) -> str:
    """Render a CSS `unicode-range` descriptor value for `codepoints`."""
    return ", ".join(
        f"U+{lo:04X}" if lo == hi else f"U+{lo:04X}-{hi:04X}"
        for lo, hi in compact_ranges(codepoints)
    )


def render_tier2_css(tier2_codepoints: set[int]) -> str:
    """Build assets/css/font-tier2.css — the on-demand tail @font-face pair.

    The `unicode-range` is exactly the tail, i.e. disjoint from what tier-1
    contains. That disjointness is the whole mechanism: the browser resolves a
    page's glyphs against tier-1 and only reaches for these ~500 KB faces when
    a page renders a syllable the corpus has never used.
    """
    ranges = format_unicode_range(tier2_codepoints)
    # `../fonts/` (not `/assets/fonts/`) so the same file works on Vercel and on
    # the GitHub Pages backup, which builds with `--baseurl /tech-blog` — a
    # root-relative url() there resolves to twodragon0.github.io/assets/... (404).
    faces = "\n".join(
        f"""@font-face {{
  font-family: 'Noto Sans KR';
  font-style: normal;
  font-weight: {weight};
  font-display: swap;
  src: url('../fonts/noto-sans-kr-{weight}-tier2.woff2') format('woff2');
  unicode-range: {ranges};
}}"""
        for weight in (400, 700)
    )
    return f"""/* GENERATED by scripts/build/generate_noto_2tier_subset.py — do not edit by hand.
 *
 * Tier-2 = the Hangul tail: syllables absent from
 * scripts/build/noto_subset_top1k.txt (and therefore absent from the tier-1
 * woff2 files preloaded in _includes/font-face.html).
 *
 * Attached after `load` by assets/js/head-runtime.js#loadFontTier2 so it never
 * touches the critical path. Because the unicode-range below is disjoint from
 * tier-1's, the woff2 files referenced here are fetched only when a page
 * actually renders a tail syllable — normally never.
 *
 * Regenerate with: python3 scripts/build/generate_noto_2tier_subset.py
 */
{faces}
"""


# -----------------------------------------------------------------------------
# Font fetching + instancing
# -----------------------------------------------------------------------------


def fetch_vf_bytes() -> bytes:
    """Download the variable Noto Sans KR TTF once per run."""
    print(f"  fetching {NOTO_VF_URL}")
    with urllib.request.urlopen(NOTO_VF_URL, timeout=120) as resp:  # noqa: S310 - pinned URL
        return resp.read()


def instantiate_static(vf_bytes: bytes, weight: int):
    """Instantiate the variable font at wght=`weight`, return a TTFont."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    src = TTFont(io.BytesIO(vf_bytes))
    return instancer.instantiateVariableFont(src, {"wght": weight})


# -----------------------------------------------------------------------------
# Subsetting
# -----------------------------------------------------------------------------


def _make_subsetter():
    from fontTools.subset import Options, Subsetter

    opts = Options()
    opts.flavor = "woff2"
    opts.with_zopfli = False
    opts.desubroutinize = True
    opts.hinting = False
    opts.notdef_outline = True
    opts.recommended_glyphs = True
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.legacy_kern = True
    opts.glyph_names = False
    opts.symbol_cmap = True
    return Options, Subsetter, opts


def subset_woff2(font, *, unicodes: list[int], text: str, out_path: Path) -> int:
    """Subset `font` (a TTFont) to the given unicodes/text, save woff2, return bytes."""
    from fontTools.ttLib import TTFont

    _, Subsetter, opts = _make_subsetter()
    # Clone font so we don't mutate the shared source between tier subsets.
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    work = TTFont(buf)

    subsetter = Subsetter(options=opts)
    subsetter.populate(unicodes=unicodes, text=text)
    subsetter.subset(work)

    work.flavor = "woff2"
    work.save(out_path)
    return out_path.stat().st_size


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def expand_ranges(ranges: list[tuple[int, int]]) -> list[int]:
    out: list[int] = []
    for lo, hi in ranges:
        out.extend(range(lo, hi + 1))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--top-n",
        type=int,
        default=0,
        help="Cap tier-1 to the N most frequent Hangul syllables (default: 0 = every syllable in the corpus)",
    )
    ap.add_argument(
        "--posts-glob",
        default=None,
        help="Restrict the corpus to a single glob instead of the site-wide CORPUS_GLOBS set",
    )
    ap.add_argument(
        "--max-tier1-kb",
        type=int,
        default=230,
        help="Soft cap for tier-1 woff2 KB (default: 230)",
    )
    ap.add_argument(
        "--max-tier2-kb",
        type=int,
        default=500,
        help="Soft cap for tier-2 woff2 KB (default: 500)",
    )
    args = ap.parse_args()

    ASSETS_FONTS_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_CSS_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_BUILD_DIR.mkdir(parents=True, exist_ok=True)

    globs = (args.posts_glob,) if args.posts_glob else CORPUS_GLOBS

    # 1. Frequency analysis
    print(f"[1/4] Hangul frequency analysis on {len(globs)} glob(s) ...")
    counts, total = hangul_frequency(globs)
    if total == 0:
        print("  ERROR: no Hangul syllables found. Aborting.", file=sys.stderr)
        return 2
    print(f"  total Hangul chars: {total:,} across {len(counts):,} unique syllables")

    top_n = min(args.top_n, len(counts)) if args.top_n > 0 else 0
    top_syllables, covered = pick_top_n(counts, top_n)
    coverage_pct = (covered / total) * 100
    label = "all corpus syllables" if top_n == 0 else f"top-{top_n}"
    print(
        f"  {label} ({len(top_syllables):,}) cover {coverage_pct:.2f}% of total Hangul characters"
    )

    # Persist the syllable list (sorted by code point so diffs stay small)
    sorted_for_disk = sorted(top_syllables, key=lambda c: ord(c))
    TOP1K_PATH.write_text(
        "\n".join(sorted_for_disk) + "\n",
        encoding="utf-8",
    )
    print(
        f"  wrote {TOP1K_PATH.relative_to(REPO_ROOT)} ({len(sorted_for_disk)} entries)"
    )

    # 2. Fetch variable font once
    print("[2/4] Downloading Noto Sans KR variable TTF ...")
    try:
        vf_bytes = fetch_vf_bytes()
    except Exception as exc:  # noqa: BLE001
        print(f"  ERROR: failed to fetch source font: {exc}", file=sys.stderr)
        return 3
    print(f"  source size: {len(vf_bytes) / 1024:,.1f} KB")

    # 3. Compute unicode sets
    tier1_codepoints = set(expand_ranges(TIER1_BASE_RANGES))
    tier1_codepoints.update(ord(c) for c in top_syllables)

    all_hangul = set(range(HANGUL_START, HANGUL_END + 1))
    top_hangul_codepoints = {ord(c) for c in top_syllables}
    tier2_codepoints = all_hangul - top_hangul_codepoints

    print(f"  tier-1 codepoints: {len(tier1_codepoints):,}")
    print(f"  tier-2 codepoints: {len(tier2_codepoints):,} (Hangul tail)")

    # The tail descriptor must match the tier-2 subset exactly, so it is written
    # from the same `tier2_codepoints` set the subsetter consumes below.
    tier2_css = render_tier2_css(tier2_codepoints)
    TIER2_CSS_PATH.write_text(tier2_css, encoding="utf-8")
    print(
        f"  wrote {TIER2_CSS_PATH.relative_to(REPO_ROOT)} "
        f"({len(compact_ranges(tier2_codepoints)):,} ranges, {len(tier2_css) / 1024:.1f} KB)"
    )

    # 4. Generate per-weight subsets
    print("[3/4] Subsetting woff2 ...")
    sizes: dict[str, int] = {}
    for weight in (400, 700):
        print(f"  weight {weight}:")
        font = instantiate_static(vf_bytes, weight)

        out1 = ASSETS_FONTS_DIR / f"noto-sans-kr-{weight}-tier1.woff2"
        out2 = ASSETS_FONTS_DIR / f"noto-sans-kr-{weight}-tier2.woff2"

        size1 = subset_woff2(
            font, unicodes=sorted(tier1_codepoints), text="", out_path=out1
        )
        size2 = subset_woff2(
            font, unicodes=sorted(tier2_codepoints), text="", out_path=out2
        )
        sizes[out1.name] = size1
        sizes[out2.name] = size2

        print(f"    tier-1 -> {out1.name}: {size1 / 1024:,.1f} KB")
        print(f"    tier-2 -> {out2.name}: {size2 / 1024:,.1f} KB")

    # 5. Validate caps
    print("[4/4] Validating size caps ...")
    over: list[str] = []
    for name, size in sizes.items():
        cap = args.max_tier1_kb if "tier1" in name else args.max_tier2_kb
        if size > cap * 1024:
            over.append(f"{name} = {size / 1024:.1f} KB (cap {cap} KB)")
    if over:
        print("  WARNING: some files exceed soft caps:")
        for line in over:
            print(f"    - {line}")
        print("  Consider lowering --top-n.")
    else:
        print("  all files within caps.")

    print("\nSummary:")
    print(
        f"  tier-1 covers {len(top_syllables):,} syllables = {coverage_pct:.2f}% of corpus Hangul characters"
    )
    for name in sorted(sizes):
        print(f"  {name}: {sizes[name] / 1024:,.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
