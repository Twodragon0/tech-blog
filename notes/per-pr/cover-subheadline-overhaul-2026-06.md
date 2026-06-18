# Cover subheadline overhaul — 2026-06-18 session (PR #417, #418, #419)

Digest cover cards displayed a bare **source name** ("The Hacker News") as the
subheadline. This session made the displayed subheadline a **content summary**
derived from the highlight title, across the whole 2026-01..06 corpus, while
keeping visual routing / honesty byte-identical.

## What shipped

| PR | Scope | Key change |
|----|-------|------------|
| **#417** | June 17 digest covers + generator | `_content_descriptor()` + `route_hint` decoupling in `scripts/news/l20_dispatch.py`; CI guard `test_ci_honesty_gate_guard.py` |
| **#418** | 06-15, 06-18 covers + Fix A | add `url` to `_GENERIC_TRAILING` (drops junk "FBI URL" bigram); regenerate 06-18 (cron-published with pre-#417 generator) |
| **#419** | Jan–May digest covers (114) | backfill content-descriptor subheadlines across 2026-01..05 via the cron L20 path |

## The core design (route_hint decoupling)

The displayed subheadline is now **display-only**. Visual routing — and therefore
the honest visual class — keys off a new panel field `route_hint` (the original
source/CVE text), NOT the displayed subheadline:

```
_panel_from_source_title:
  display subheadline = content descriptor (title's secondary ASCII entities)
                        OR source/CVE fallback when none
  route_hint          = source/CVE text  (UNCHANGED → routing & honesty identical)
```

Both `route_visual_id` call sites (`_apply_real_content`,
`resolve_digest_band_visuals`) route from `route_hint`, so on-disk visuals and the
honesty scorer's replay stay in lockstep. The honesty gate verdict is unchanged by
construction. Tests: `TestContentDescriptorSubheadline`,
`test_decoupling_is_load_bearing` in `scripts/tests/test_l20_realcontent.py`.

## Examples (source name → content descriptor)

- `Google Vertex` → **AI SDK Bucket** · `Rokarolla` → **Android PIN SMS**
- `Malicious NGINX` → **Configurations React2Shell** · `Cisco Catalyst` → **SD-WAN Controller**
- `Fortinet` → **FortiSandbox** · `Amazon Bedrock` → **Guardrails InvokeGuardrailChecks API**

~21% of cards still fall back to source/CVE — their Korean title carries only one
ASCII entity, the deterministic limit. A Gemini-summary design to close that gap is
drafted at `.omc/plans/cover-subtitle-en-pipeline.md` (critic verdict:
PROCEED-WITH-CHANGES, **recommend defer** — cosmetic gain vs new LLM dependency).

## Verification (every PR)

honesty `--all --strict` exit 0 (no new STALE_RENDER/overclaim) · drift 0
(digest/rollup/l25 specs untouched) · `check_svg_quality` 0 FAIL (no Hangul) ·
title-ascii 0 · size-gate `--strict` exit 0 · pytest 2295+ · live curl confirmed
on tech.2twodragon.com. CI runs `score_cover_honesty.py --all --strict` over the
whole 203-cover corpus on every `assets/images/**.svg` change.

## Decisions / lessons (this session)

- **Regen path gotcha**: `generate_post_images.py --svg-only` has L20 DISABLED
  (`L20_HERO_ENABLED=False`) → L22 fallback. The real L20 generator is the cron
  path `auto_publish_news._render_l20_svg_string`; regenerate via
  `scripts/_regen_june_l20_covers.py`. (memory: `l20-regen-path-gotcha`)
- **Spec safety**: never L20-regenerate spec/rollup covers. Rollup posts
  (Week/Monthly_Index) don't match the `Weekly_Digest` glob; the 3 digest_covers
  specs (04-26/27/28) are reverted after a glob run. Verified spec-leak = 0.
- **Rollup detail is already content** — the small "source" line on rollup covers
  is a deliberate attribution badge, not a source-only subheadline (corrected a
  grep false-positive).
- **Cover↔post matching uses the post `image:` field, not the filename stem** — a
  filename-stem audit produced 9 false "orphans" (incl. the user's reference
  covers); deleting them would have broken live posts. (memory:
  `cover-post-match-by-image-field`)
- **Legacy honesty-baseline covers stay baselined** — the 30 grandfathered FAILs
  share the rich attack-chain style of the user's reference covers; regenerating
  to chase baseline=0 would blander them. baseline is non-blocking. See
  `notes/decisions.md` (2026-06-18 entry).
- **Strategy Michael / Class D** — Korean possessive "의" headline split is
  permanently deferred (marker byte-identical to good cases). See
  `notes/decisions.md`.

## Cron continuity

The next auto-published digest inherits the fix: `_render_l20_svg_string` (the
cron render function) now emits content descriptors — verified 3/3 content
subheadlines rendering 2026-06-18 via the cron path.
