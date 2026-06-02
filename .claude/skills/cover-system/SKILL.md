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
