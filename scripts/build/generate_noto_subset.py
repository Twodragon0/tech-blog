#!/usr/bin/env python3
"""
Generate a single-tier woff2 subset of Noto Sans KR for self-hosting.

Strategy
--------
The full Hangul syllables block (U+AC00-U+D7A3, 11,172 code points) compresses
to ~550 KB per weight in woff2 — too heavy to block first paint. But we do not
need all of it: the published corpus uses only ~1,035 distinct syllables, and
every one of them lies inside the 2,350 syllables standardised by KS X 1001
(the Wansung set every Korean text encoding since EUC-KR has carried).

So: one face per weight, covering

  * Latin Basic + Supplement + Extended-A (so European loanwords render)
  * Hangul Jamo (composing fallback)
  * CJK punctuation, halfwidth/fullwidth, arrows, geometry, misc symbols
  * KS X 1001 Hangul (2,350 syllables) UNION every syllable observed in
    `_posts/*.md`

Measured 2026-08-07 (fontTools 4.62.1, pinned upstream VF):

    weight 400 -> 278.4 KB
    weight 700 -> 284.4 KB
    total         562.9 KB, versus 1,374.6 KB for the retired 2-tier layout (-59%)

Coverage per weight: 3,230 code points / 5,487 glyphs. That is fewer than the
3,694 code points requested because the upstream VF has no glyph for some of
them (parts of U+FF00-FFEF and U+2600-26FF); the corpus and the full KS X 1001
set are covered, which is what the gate asserts.

Why the 2-tier layout was retired
---------------------------------
It eager-loaded a ~200 KB "tier-1" face (top-1000 corpus syllables) and
lazy-loaded a ~490 KB "tier-2" face holding the remaining ~10,200 syllables.
Two structural defects made that a net loss:

1. **The tiers were disjoint, not overlapping.** tier-1 carried 952 Hangul
   glyphs while its CSS `unicode-range` claimed all 11,172 of U+AC00-D7A3.
   When a syllable fell inside the declared range but had no glyph in the
   face, Chrome went straight to OS system fallback instead of walking the
   CSS fallback stack — so the lazy tier bought nothing for first paint.
2. **The "lazy" load was not lazy.** `head-runtime.js` waited for
   `window.load` then `requestIdleCallback`, but on a warm load that fires
   before FCP, and `FontFace.load()` fetches at `VeryHigh` priority — above
   the tier-1 preload's `High`. 972 KB of rare glyphs (covering 0.02% of body
   text) competed with first paint.

A single face sized between the two removes both defects: no unicode-range
lie, no runtime font injection, ~811 KB less transfer.

Coverage is enforced, not assumed
---------------------------------
`scripts/tests/test_font_glyph_coverage.py` fails CI when any `_posts/*.md`
syllable is missing from the produced woff2 cmap. Cron auto-publishes posts,
so a novel syllable turns the build red instead of silently regressing to
system fallback.

Source
------
We download the Noto Sans KR variable font (TTF subset) from the upstream
`notofonts/noto-cjk` GitHub repo, then instantiate it at wght=400 and
wght=700 before subsetting. This gives us a single deterministic input and
two static weights without depending on per-weight static OTFs.

Usage
-----
    python3 scripts/build/generate_noto_subset.py [--posts-glob '_posts/*.md']

Outputs
-------
    scripts/build/noto_subset_hangul.txt
    assets/fonts/noto-sans-kr-{400,700}-ksx1001.woff2

NOT byte-reproducible
---------------------
Re-running with an unchanged corpus, an unchanged pinned upstream font, the same
fontTools, and even `PYTHONHASHSEED=0` produces woff2 that differ in bytes and
in size by up to ~0.1% (measured 284,892 / 284,984 / 285,036 / 285,120 B across
four runs; glyph count and cmap are identical every time). brotli itself is
deterministic, so the variance originates inside fontTools' subsetting or woff2
transform. Consequences:

  * Never gate on byte equality against the committed files. The authority is
    `scripts/tests/test_font_glyph_coverage.py`, which asserts coverage.
  * build.sh's cold-deploy regen therefore serves bytes that differ slightly
    from the committed ones. Harmless — same coverage, same metrics — and regen
    never commits back, so git history stays clean.
  * The prior version of this docstring claimed idempotency. It was wrong; the
    code path is unchanged, so the claim was wrong then too.
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
SCRIPTS_BUILD_DIR = REPO_ROOT / "scripts" / "build"
HANGUL_LIST_PATH = SCRIPTS_BUILD_DIR / "noto_subset_hangul.txt"

# The filename stem encodes the Hangul coverage basis (`ksx1001`) instead of a
# version hash. vercel.json serves /assets/fonts/*.woff2 with
# `Cache-Control: public, max-age=31536000, immutable`, so swapping the bytes
# under a name a returning visitor already cached would pin them to a stale
# face for up to a year. Any future change to the coverage basis must therefore
# also change this stem.
FONT_STEM = "noto-sans-kr-{weight}-ksx1001"

# Upstream source: Noto Sans KR variable font (subset TTF) from
# notofonts/noto-cjk. Defaults to `main`; build.sh exports a pinned 40-char
# commit SHA (enforced by scripts/tests/test_noto_build_integration.py).
NOTO_VF_URL = os.environ.get(
    "NOTO_VF_URL",
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/Variable/TTF/Subset/NotoSansKR-VF.ttf",
)

# Hangul syllables block
HANGUL_START = 0xAC00
HANGUL_END = 0xD7A3

# KS X 1001 places its 2,350 precomposed Hangul syllables in the EUC-KR
# (Wansung) rows 0xB0-0xC8, cells 0xA1-0xFE — 25 x 94 = 2,350 exactly. We
# enumerate them through Python's stdlib `euc_kr` codec so the set is derived
# offline with no vendored data file and no network call.
KSX1001_LEAD_RANGE = (0xB0, 0xC8)
KSX1001_TRAIL_RANGE = (0xA1, 0xFE)

# Always-included non-Hangul ranges (Latin + Korean Jamo + symbols).
BASE_RANGES = [
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
# Coverage set
# -----------------------------------------------------------------------------


def ksx1001_hangul() -> set[str]:
    """Return the 2,350 KS X 1001 precomposed Hangul syllables."""
    out: set[str] = set()
    lead_lo, lead_hi = KSX1001_LEAD_RANGE
    trail_lo, trail_hi = KSX1001_TRAIL_RANGE
    for lead in range(lead_lo, lead_hi + 1):
        for trail in range(trail_lo, trail_hi + 1):
            ch = bytes([lead, trail]).decode("euc_kr")
            if HANGUL_START <= ord(ch) <= HANGUL_END:
                out.add(ch)
    return out


def hangul_frequency(posts_glob: str) -> tuple[dict[str, int], int]:
    """Count Hangul-syllable frequency across all matching markdown files.

    Returns (counts, total_hangul_chars).
    """
    counts: dict[str, int] = {}
    total = 0
    for path in sorted(REPO_ROOT.glob(posts_glob)):
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


def hangul_coverage(posts_glob: str = "_posts/*.md") -> set[str]:
    """The Hangul syllable set the subset must cover: KS X 1001 + corpus.

    Single source of truth shared by this generator and the CI coverage gate
    (`scripts/tests/test_font_glyph_coverage.py`), so the two cannot drift.
    """
    counts, _ = hangul_frequency(posts_glob)
    return ksx1001_hangul() | set(counts)


def font_path(weight: int) -> Path:
    """On-disk path of the produced woff2 for `weight`."""
    return ASSETS_FONTS_DIR / f"{FONT_STEM.format(weight=weight)}.woff2"


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
    # Clone font so we don't mutate the shared source across weights.
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
    ap.add_argument("--posts-glob", default="_posts/*.md", help="Glob for corpus (default: _posts/*.md)")
    ap.add_argument(
        "--max-kb",
        type=int,
        default=320,
        help="Soft cap per woff2 in KB (default: 320; measured 278-285)",
    )
    args = ap.parse_args()

    ASSETS_FONTS_DIR.mkdir(parents=True, exist_ok=True)
    SCRIPTS_BUILD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Coverage set = KS X 1001 + everything the corpus actually uses
    print(f"[1/4] Hangul coverage analysis on {args.posts_glob} ...")
    counts, total = hangul_frequency(args.posts_glob)
    if total == 0:
        print("  ERROR: no Hangul syllables found. Aborting.", file=sys.stderr)
        return 2
    ksx = ksx1001_hangul()
    corpus = set(counts)
    coverage = ksx | corpus
    print(f"  corpus: {total:,} Hangul chars across {len(corpus):,} distinct syllables")
    print(f"  KS X 1001 Hangul: {len(ksx):,}")
    print(f"  corpus syllables outside KS X 1001: {len(corpus - ksx):,}")
    print(f"  coverage set: {len(coverage):,} syllables (100% of corpus by construction)")

    # Persist the coverage list (sorted by code point so diffs stay small).
    # Also a font-drift-gate source of truth (scripts/dev/check_font_drift.py).
    HANGUL_LIST_PATH.write_text(
        "\n".join(sorted(coverage, key=ord)) + "\n",
        encoding="utf-8",
    )
    print(f"  wrote {HANGUL_LIST_PATH.relative_to(REPO_ROOT)} ({len(coverage)} entries)")

    # 2. Fetch variable font once
    print("[2/4] Downloading Noto Sans KR variable TTF ...")
    try:
        vf_bytes = fetch_vf_bytes()
    except Exception as exc:  # noqa: BLE001
        print(f"  ERROR: failed to fetch source font: {exc}", file=sys.stderr)
        return 3
    print(f"  source size: {len(vf_bytes) / 1024:,.1f} KB")

    # 3. Compute the unicode set
    codepoints = set(expand_ranges(BASE_RANGES))
    codepoints.update(ord(c) for c in coverage)
    print(f"  total codepoints: {len(codepoints):,}")

    # 4. Generate per-weight subsets
    print("[3/4] Subsetting woff2 ...")
    sizes: dict[str, int] = {}
    for weight in (400, 700):
        out = font_path(weight)
        size = subset_woff2(
            instantiate_static(vf_bytes, weight),
            unicodes=sorted(codepoints),
            text="",
            out_path=out,
        )
        sizes[out.name] = size
        print(f"  weight {weight} -> {out.name}: {size / 1024:,.1f} KB")

    # 5. Validate cap
    print("[4/4] Validating size cap ...")
    over = [f"{n} = {s / 1024:.1f} KB (cap {args.max_kb} KB)" for n, s in sizes.items() if s > args.max_kb * 1024]
    if over:
        print("  WARNING: some files exceed the soft cap:")
        for line in over:
            print(f"    - {line}")
    else:
        print("  all files within cap.")

    print("\nSummary:")
    for name in sorted(sizes):
        print(f"  {name}: {sizes[name] / 1024:,.1f} KB")
    print(f"  total: {sum(sizes.values()) / 1024:,.1f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
