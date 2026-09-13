---
name: cover-system
description: Use BEFORE touching any digest/post cover SVG, the cover generators (svg_l20_hero, svg_l22_generator, svg_l25_single), the routers (l20_dispatch, l22_dispatch), the honesty scorer, or regenerating covers. Maps the runtime cover-generation architecture and the gotchas that cause corpus-wide breakage.
---

# Cover Generation System (runtime architecture + gotchas)

The hand-authoring catalog `docs/guides/digest-cover-layouts.md` describes the
*design* of layouts. THIS skill describes the *code* that actually renders
covers and the traps that have repeatedly caused over-reach regressions.

## Five cover systems (do not confuse them)

| System | Generator | Spec source | How a cover is made | Marker on disk |
|---|---|---|---|---|
| **L20** Hero+2-Card | `scripts/lib/svg_l20_hero.py` (`render_l20_hero`), routed by `scripts/news/l20_dispatch.py` | none (content-driven) | `generate_post_images.py <post> --svg-only --force` | `<!-- profile: high-quality-cover (L20 Hero+2-Card) -->` |
| **L22** stacked-bands | `scripts/lib/svg_l22_generator.py` | `_data/digest_covers/*.yml` for spec covers | `upgrade_digest_cover.py --all` (spec) OR L20 fallback | 3-band structure, no profile comment |
| **L25** single | `scripts/lib/svg_l25_single.py` | `_data/l25_covers/*.yml` | `upgrade_l25_cover.py --all` | `profile: high-quality-cover (2025 upgraded L25-single)` |
| **rollup** | `scripts/lib/svg_rollup_generator.py` | `_data/rollup_covers/*.yml` | `upgrade_rollup_cover.py --all` | `classify()=='rollup'` (size band 38000-83968) |
| **fallback** | `generate_post_images.py::generate_fallback_svg` | none | non-digest posts with no Gemini key | — |

## Dispatch order (the #1 gotcha)

For **digest** posts, `generate_post_images.py::process_post` (around lines
2581 and 2643) renders **L20 first** (`_generate_l20_digest_svg`); L22 is the
**fallback only when L20 fails**. So editing the L22 router (`_L22_KEYWORD_ROUTES`)
does NOT change a live digest cover — it's L20. Verify by rendering and grepping,
never by reading the router. (See `.omc/research/l20_cover_trace_2026_06_01.md`.)

L20 routing: `l20_dispatch.route_visual_id` (`_VISUAL_ROUTES`, first-match-wins)
→ a builder in `svg_l20_hero.VISUAL_BUILDERS`. No-match default is `neutral`
(changed off `cve_chain` 2026-06-02). `_render_visual`'s unknown-key fallback
must stay in lockstep with the router default.

## Honesty rule (enforced)

A cover band must not assert evidence the post lacks: an attack/CVE/breach/C2
visual requires a matching token in the post. Builders hardcode their claim
vocab (`cve_chain` → "CVE REGRESSION CHAIN", `data_exfil` → "DATA EXFILTRATION",
`hub_spoke` → "VICTIM/C2", etc.). Honest classes: `neutral`, `market`,
`security_advisory`.

`scripts/score_cover_honesty.py` is the deterministic scorer (L20/L22/L25
claim-class taxonomy, must stay lockstep with `VISUAL_BUILDERS`). It is a
**BLOCKING** svg-lint CI gate: `--all --baseline scripts/cover_honesty_baseline.txt
--strict`. Legacy FAILs are grandfathered in the baseline; only NEW honesty
regressions fail the build. Never empty/bypass the baseline to make a cover
"pass" — that games the gate. See [[digest_cover_dispatch_l20_over_l22]].

## GOTCHAS (each caused a real corpus-wide regression — do not repeat)

1. **Don't L20-regenerate spec-driven or rollup covers.** A blind
   `generate_post_images.py --force` loop over `grep -iE "Digest|Weekly|Daily"`
   will convert rollup covers (e.g. April Week1-4) and spec-driven covers to
   L20, breaking the `rollup_drift`/`digest_drift` checks and the size-gate
   rollup tests. Before regenerating a cover, check `classify(svg)` and whether
   a `_data/*_covers/*.yml` spec exists; if spec-driven, regenerate via the
   matching `upgrade_*_cover.py`, not the L20 generator.
2. **A shared `gen_qr`/`qr_block` change drifts EVERY spec cover.** The drift
   checks render specs fresh; if the shared QR changes, all on-disk spec covers
   drift until regenerated. Regenerate all spec covers (`upgrade_*_cover.py --all`)
   when changing shared rendering code.
3. **Cover-only commits now run pytest** (pre-commit extended 2026-06-02), but
   they do NOT run the CI drift/quality checks. Run them manually (below).
4. **ASCII gate only checks `<title>`/`<desc>`** — Korean in body `<text>` is
   caught by `check_svg_quality.py`, a SEPARATE CI gate. English-only applies to
   ALL `<text>`.

## Corpus-wide regeneration is permanent — iterate on the 32-cover canary first

A cover regenerated and committed is a new blob **forever**. Git keeps every
version, so a design pass over the corpus costs ~300 blobs whether or not the
design survives. This is the single largest cost in the repository.

Measured 2026-09-13, over the **last 500 commits only**:

| | |
|---|---|
| distinct image paths touched | 2,930 |
| total revisions | **29,177** — a mean of **10 rewrites per image** |
| paths rewritten 2+ times | 2,375 (**81%**) |
| worst single cover | **60** revisions |
| largest single commit | **444** images (`d0289804`) |
| repo size vs HEAD tree | **1,420 MB vs 141 MB** — 90% is history |

The branch names record how it happened: `style-a-pilot` → `style-a-v3-qr` →
`style-a-v4b-infographic` → `style-a-v4c-pure-visual`, plus
`upgrade-digest-svg-quality`. Each variant was rendered across the corpus and
committed. That is iteration cost, not a bug.

**Rule: iterate on the canary, not the corpus.**

1. Change the generator.
2. Render and eyeball **only** the 32-cover sample — `TARGET_SVGS` in
   `scripts/svg_visual_baseline.py`, baselines in `tests/visual-baselines/`
   (32 PNGs + `manifest.json`). It spans L20, unattributed and rollup, which is
   why it catches routing regressions.
3. Iterate there until the design is final.
4. **Only then** run `upgrade_*_cover.py --all` / the L20 loop once.

One corpus pass per accepted design, not one per variant.

### Three fixes that do not work (each was tried and measured)

- **Skipping writes when content is unchanged.** The generators are already
  deterministic — `upgrade_digest_cover.py --all --check` reports `33 specs OK`,
  and rendering the same spec twice leaves the working tree clean. Git stores
  nothing for identical bytes, so there is no duplicate write to suppress.
- **Deleting images from `HEAD`.** Removing a file does not remove its blobs
  from history. It shrinks checkouts, not the repository. (`_unused_archive/` is
  also **not** dead weight — it is the move target of
  `verify_images_unified.py --move-unused-to-archive` and has been used as a
  recovery source.)
- **Deleting merged branches.** Their commits are ancestors of `main`, so every
  object stays reachable. Measured: 15 merged branches deleted, repository size
  unchanged. Worth doing for clarity; worth nothing for size.

The only real levers are the canary rule above, moving rendered covers out of
git, and history rewriting (irreversible — plan first).

Note that `visual-baseline-refresh.yml` **auto-commits on main**, so a generator
change that alters these 32 renders is recorded as the new truth without review.
`visual-baseline-verify.yml` on PRs is the point where both renders exist.

## Verify workflow (run ALL locally before committing cover changes)

```bash
PY=.venv/bin/python3
# drift (spec vs on-disk) — must be 0 each
$PY scripts/upgrade_digest_cover.py --all --check
$PY scripts/upgrade_rollup_cover.py --all --check
$PY scripts/upgrade_l25_cover.py   --all --check
# quality + honesty
$PY scripts/check_svg_quality.py --ci assets/images/      # 0 FAIL (no Korean <text>)
$PY scripts/lint_svg_compliance.py --report               # 0 violations
$PY scripts/score_cover_honesty.py --all --baseline scripts/cover_honesty_baseline.txt --strict  # exit 0
# gates
$PY scripts/check_svg_title_ascii.py
$PY scripts/check_svg_size_gate.py --all
$PY scripts/check_spec_slug_consistency.py
$PY -m pytest scripts/tests/ -q                           # 0 fail
```

Rasterize changed covers with `build_one(svg_name)` from
`scripts/_rebuild_all_l20_rasters.py` (rsvg-convert + PIL → og.png + og/card
.webp/.avif). The L20 digest path does NOT auto-rasterize.

## Empirical-first rule

Render the actual cover and grep the output — do not reason about routing
statically. Every cover regression this codebase has hit was a static-reasoning
error that an empirical render would have caught immediately.
