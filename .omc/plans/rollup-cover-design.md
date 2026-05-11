# Rollup Cover Design — Sibling Layout to L22 Ultra

**Status**: planning
**Created**: 2026-05-11
**Owner**: TBD
**Predecessors**: `upgrade-script-unification.md` (2026-05-10)
**Scope**: 5 low-quality (~8 KB) rollup SVGs + decision on the 04-30 Week4 fit

## 1. Problem Statement

The repository now has two distinct cover *semantics*:

1. **Daily weekly-digest** (e.g. `2026-04-19-Tech_Security_Weekly_Digest_AI_*`) — covers
   one day, picks **3 top stories**, fits the L22 ultra 3-band layout naturally
   (`scripts/lib/svg_l22_generator.py:45` `THEMES`, band y=105/315/525).
2. **Rollup** (week or month index) — covers **7–30 days** with N constituent daily
   digests (7–11 weekly, 20–30 monthly). Carries a *period summary*, not a top-3 list.

The 5 target files were generated before the L22 ultra unification and sit at
7.9–8.3 KB with hand-drawn flat shapes (see
`assets/images/2026-02-28-February_2026_Security_Digest_Monthly_Index.svg:1-100`).
They visually clash with the post-2026-04-26 L22 ultra covers (~50–67 KB).

**Why L22 ultra 3-band does not fit rollups.** The 04-30 Week4 cover was retro-fit
into L22 ultra (`assets/images/2026-04-30-Week4_April_2026_Security_Digest.svg:1-100`).
Examining its 3 picked bands (NPM supply chain / VECT 2.0 / SGLang SSRF) vs. the
post markdown's 7 day-indexed digests, the L22 fit is forced:

- The post's *summary_card.highlights* lists **3 themes** (an editorial pick) but the
  *daily index* shows **7 day-rows** with distinct issues each day.
- Selecting 3 bands drops **57%** of the daily content. The reader cannot see
  "which day had the SAP npm story" from the cover.
- The L22 visual primitives (`v_lock_cve`, `v_network_nodes`) optimize for *one*
  incident per band — a rollup band is inherently *aggregated*, so the visual feels
  decorative rather than informative.
- Monthly rollups are worse: 4 weeks × 3 stories ≈ 12 candidate items must collapse
  into 3 bands. The 02-28 cover hand-curates "Week 1-2 / Week 3 / Week 4" rows in a
  3-card grid (see `02-28 svg:61-83`) — *that* shape (period buckets, not story
  bands) is the right primitive, but it was hand-drawn at 8 KB.

The rollup needs a **period-summary** primitive, not a story-band primitive.

## 2. Proposed Layouts

All targets: 1200×630 viewBox, same header style as L22 (`y=0..80`), same QR block
at translate(1080,504), reuse `THEMES` accent/soft colors.

### A. Calendar grid (7 / 28 cells)

```
+--------- 1200×80 header (period label + week/month badge) -----------+
| Mon  Tue  Wed  Thu  Fri  Sat  Sun                                   |
| [HI] [HI] [ME] [LO] [HI] [ME] [HI]   <- severity color tiles, count |
|--- top-3 highlight strip (mini L22 cards) at y=380 -----------------|
|--- footer stats: daily_count, CVE count, response actions, QR ------|
```

For monthly: 5 rows × 7 columns = 35 tiles (with blanks for days outside month).

- **Pros**: surfaces *all* daily activity; reader sees the threat tempo across days;
  scales weekly → monthly with the same primitive.
- **Cons**: 28-cell monthly grid is dense; severity-only signal is reductive.
- **Surfaces**: per-day severity, daily count, top headlines.
- **Hides**: per-CVE detail, source breakdown.
- **Fit**: weekly ✅ excellent, monthly ✅ good.

### B. Category bar-chart

```
SECURITY     |##############| 18  "n8n Webhooks abused for phishing"
AI/ML        |#########|       12  "AWS Model Context Protocol audit"
CLOUD        |######|            8  "Nginx UI CVE-2026-33032"
DEVOPS       |####|              5  "PHP Composer CLI injection"
BLOCKCHAIN   |##|                3  "Grinex exchange OFAC sanctions"
```

- **Pros**: surfaces topic distribution; matches the blog's category taxonomy
  (security/devsecops/devops/cloud/blockchain — `_config.yml`).
- **Cons**: hides temporal tempo; "top headline per category" implies an editorial
  pick that may not exist for thin categories.
- **Surfaces**: which topic dominated the period, category histogram.
- **Hides**: which day, severity, individual incidents.
- **Fit**: monthly ✅ excellent (broad coverage), weekly ⚠️ low-N bars look sparse.

### C. Timeline strip

```
4/15 ---*---*--------*-- 4/21
        |   |        |
       HI  ME       HI
       SAP MCP      Grinex
```

- **Pros**: temporal narrative; obvious "what happened when."
- **Cons**: only fits ~4–6 pin points before clutter; monthly view becomes a
  scatter.
- **Fit**: weekly ✅ good, monthly ❌ cluttered.

### D. Hybrid (header + 3 mini-bands + footer stats) — *evolution of 04-30*

```
+- header + period badge ---------------------------------------------+
+- top-3 highlight strip: 3 short L22-style cards (180h × 380w) ------+
+- 7×1 severity strip (week) OR 4×1 week-roll strip (month) ----------+
+- footer: daily_count | CVE | sources | QR -------------------------+
```

- **Pros**: keeps L22's editorial top-3 (so the cover has a *story*) **and** the
  per-day overview (so the cover is *complete*); shared header style with L22 ultra.
- **Cons**: ~4 logical zones — risk of crowding.
- **Fit**: weekly ✅ excellent, monthly ✅ good (swap day-strip for week-strip).

## 3. Recommended Layout

**Pick D (Hybrid).** Justification tied to post markdown data
(`_posts/2026-04-19-Week3_April_2026_Security_Digest.md:23-40`):

| Post data | Maps to | Layout zone |
|-----------|---------|-------------|
| `summary_card.highlights` (3 items) | top-3 editorial pick | mini-band strip |
| daily index table (7 rows) | per-day tempo | severity strip |
| `redirect_from` list length | `daily_count` stat | footer |
| `categories` + `tags` | category breakdown | footer chips (optional v1.1) |
| `period` field | display label | header badge |

Hybrid reuses L22's editorial intent (top-3 hero stories) while adding a
**period-completeness** strip — the missing primitive. It also leaves a clean
upgrade path to add category chips in v1.1 without breaking the layout.

For monthly rollups, the only difference: the 7-cell day strip becomes a 4-cell
week strip (W1/W2/W3/W4). Same renderer, parameterized by `daily_count`.

## 4. Implementation Plan (no code in this PR)

### Phase 1 — New renderer: `scripts/lib/svg_rollup_generator.py`

Modeled on `scripts/lib/svg_l22_generator.py:1-50`. Exposes:

```python
def render_rollup_svg(spec: dict) -> str: ...

# Reuses from svg_l22_generator (DO NOT duplicate):
#   THEMES, gen_qr, qr_block (L22:45-99), deco_layer, header gradient
# New primitives (rollup-specific):
#   period_header(label, kind, sfx)          -> top 80px
#   highlight_card(idx, theme, item)         -> top-3 cards (y=110..280)
#   day_strip(items, kind)                   -> y=300..380 (7- or 4-cell)
#   footer_stats(stats, url)                 -> y=400..620 + QR
```

Acceptance: `render_rollup_svg({...})` returns ≥ 45 KB SVG with valid XML, no
script tags, English-only text, QR path matches `gen_qr(canonical_url)`.

### Phase 2 — CLI dispatch

**Decision**: separate CLI `scripts/upgrade_rollup_cover.py`. Trade-off table:

| Option | Pros | Cons |
|--------|------|------|
| `--variant rollup` flag on `upgrade_digest_cover.py` | one entry point; shared `_gather_specs`, `--check`, `--dry-run` | mixed schema validation; two code paths in one file; `bands` list (3) vs `highlights` list (3) + `days` list (7) drift risk |
| **New `upgrade_rollup_cover.py`** | clean spec schema; independent test file; orthogonal CI step | small code duplication of `_gather_specs`/`--check` (~40 LOC) |

Recommend **separate CLI**. The shared bits (`load_spec`, `check`, `_gather_specs`)
factor into a thin helper module `scripts/lib/cover_cli.py` to keep the duplication
to <20 LOC. Lower review surface, no schema-union foot-guns.

### Phase 3 — Spec format: `_data/rollup_covers/<date>.yml`

Separate directory so `upgrade_digest_cover.py --all` (`SPECS_DIR =
_data/digest_covers/`, see `scripts/upgrade_digest_cover.py:72`) does not pick up
rollup YAMLs and crash on the schema mismatch.

CI drift gate updates: extend `check-svg.yml` to glob **both** dirs (see Phase 7).

### Phase 4 — Author 5 YAML specs

One spec per target file. Content derived from each post's markdown:

| File | Source post | period_label | daily_count |
|------|-------------|--------------|-------------|
| `2026-01-31-January_2026_Security_Digest_Monthly_Index.svg` | `_posts/2026-01-31-*.md` | `January 2026` | 4 (W1–W4) |
| `2026-02-28-February_2026_Security_Digest_Monthly_Index.svg` | `_posts/2026-02-28-*.md` | `February 2026` | 4 |
| `2026-04-05-Week1_April_2026_Security_Digest.svg` | `_posts/2026-04-05-*.md` | `April 1–7, 2026` | 7 |
| `2026-04-12-Week2_April_2026_Security_Digest.svg` | `_posts/2026-04-12-*.md` | `April 8–14, 2026` | 7 |
| `2026-04-19-Week3_April_2026_Security_Digest.svg` | `_posts/2026-04-19-*.md` | `April 15–21, 2026` | 7 |

Derive each spec's `highlights` from the post's `summary_card.highlights`. Derive
`days[]` from the daily index table. Derive `daily_count` from `len(redirect_from)`.

### Phase 5 — Render, verify, regenerate downstream variants

1. `python3 scripts/upgrade_rollup_cover.py --all` writes all 5 SVGs.
2. `python3 scripts/upgrade_rollup_cover.py --all --check` proves byte-stability.
3. `python3 scripts/check_cover_qr_urls.py` — confirms each cover's QR path equals
   `gen_qr(_post_url_from_filename(name))` (see
   `scripts/news/l20_dispatch.py:403-420`). Underscore preservation is correct for
   rollup slugs like `Week3_April_2026_Security_Digest`.
4. Regenerate PNG/AVIF/WEBP variants via the existing
   `scripts/generate_post_images.py` rasterization step. Verify each SVG ≥ 50 KB
   (current 8 KB is the proxy for "low quality").

### Phase 6 — 04-30 Week4 migration decision

**Recommendation**: **migrate** the 04-30 Week4 cover to the new rollup layout in
the same PR that ships Phase 1–5.

Rationale:

- Same content semantics (week of 4/22–4/28 with 7 daily digests).
- Keeping it on L22 ultra leaves one "force-fit" outlier in the rollup family —
  visual consistency wins.
- The L22 ultra version drops 4 of 11 daily stories. The rollup hybrid layout
  surfaces all 7 days via the day-strip while keeping the same top-3 editorial pick.
- Migration cost: write 1 YAML spec, delete 1 entry from `_data/digest_covers/`
  if present (verify before deleting — the 04-30 was generated by a hardcoded
  script, may not have a spec yet).

Counter-argument considered: "the L22 version was just shipped, don't churn." Reject
because the file is < 2 weeks old and not yet referenced in any external pipeline
beyond the post page itself.

### Phase 7 — CI integration

Extend `.github/workflows/check-svg.yml`:

```yaml
paths:
  - 'assets/images/*Tech_*Weekly_Digest_*.svg'
  - 'assets/images/*Monthly_Index.svg'              # NEW
  - 'assets/images/*Week[1-5]_*_Digest.svg'         # NEW (catches Week1..Week5)
  - '_data/digest_covers/**.yml'
  - '_data/rollup_covers/**.yml'                    # NEW
  - 'scripts/lib/svg_l22_generator.py'
  - 'scripts/lib/svg_rollup_generator.py'           # NEW
  - 'scripts/upgrade_digest_cover.py'
  - 'scripts/upgrade_rollup_cover.py'               # NEW
```

Job steps:

```
- python3 scripts/upgrade_digest_cover.py --all --check
- python3 scripts/upgrade_rollup_cover.py --all --check     # NEW
- python3 scripts/check_cover_qr_urls.py                    # unchanged, globs both
- pytest scripts/tests/test_upgrade_rollup_cover.py         # NEW (≥ 10 tests)
```

## 5. Spec Schema Proposal (draft)

```yaml
# _data/rollup_covers/2026-04-19.yml
date: 2026-04-19
slug: Week3_April_2026_Security_Digest
kind: weekly_rollup          # weekly_rollup | monthly_index
period_label: "April 15-21, 2026"
period_short: "W3 April"     # header badge, ~10 chars max
daily_count: 7
sfx: AP19                    # 2-4 char gradient/filter id suffix
title: "2026-04-19: Week-3 April rollup - CPUID supply chain, n8n phishing, Nginx UI auth bypass"
aria: |
  Week-3 April 2026 rollup covering 7 daily security digests : CPUID supply
  chain breach distributing tampered CPU-Z, n8n Webhooks abused for phishing
  email delivery, Nginx UI CVE-2026-33032 authentication bypass critical
top_highlights:                # 3 items, maps to mini-band strip y=110..280
  - theme: red
    severity: HIGH
    label: SUPPLY CHAIN
    headline: "CPUID Supply Chain Breach"
    detail: "CPU-Z tampered build pushed via official channel"
    source: "The Hacker News"
  - theme: amber
    severity: HIGH
    label: AUTH BYPASS
    headline: "Nginx UI CVE-2026-33032"
    detail: "Pre-auth admin takeover : patch immediately"
    source: "Nginx Security Advisory"
  - theme: purple
    severity: MEDIUM
    label: BOTNET
    headline: "PowMix botnet, Mirai variant Nexcorium"
    detail: "Operation PowerOFF takedown coordination"
    source: "Microsoft Security"
days:                          # weekly: 7 entries; monthly: 4 entries (W1..W4)
  - { date: "4/13", severity: HIGH,   tag: "CPUID + Marimo RCE" }
  - { date: "4/14", severity: MEDIUM, tag: "JanelaRAT + ransomware report" }
  - { date: "4/15", severity: MEDIUM, tag: "AWS MCP + PHP Composer" }
  - { date: "4/16", severity: HIGH,   tag: "n8n phishing + Nginx UI CVE" }
  - { date: "4/17", severity: HIGH,   tag: "PowMix botnet + Operation PowerOFF" }
  - { date: "4/18", severity: LOW,    tag: "Defender ETL + Google policy" }
  - { date: "4/19", severity: MEDIUM, tag: "Grinex sanctions + Mirai Nexcorium" }
footer:
  daily_digests: 7
  cves_tracked: 4              # count of distinct CVE-202x-yyyyy refs
  categories: [security, devsecops, cloud]
```

**Field justifications**:

- `kind`: drives the day-strip primitive (7-cell vs 4-cell). Single source of truth
  rather than inferring from `len(days)`.
- `period_short`: needed because `period_label` (e.g. "April 15–21, 2026") overflows
  the 188px badge slot at the L22 header style.
- `sfx`: same contract as L22 ultra to avoid `<defs>` id collisions on the post page.
- `severity` enum: `{HIGH, MEDIUM, LOW}` — maps to `THEMES.red.accent`,
  `THEMES.amber.accent`, `THEMES.green.accent`. Reuse L22 palette, no new colors.
- `top_highlights` has exactly 3 items (matches `summary_card.highlights` schema in
  every post). Schema enforces `len(top_highlights) == 3` to mirror L22 ultra's
  3-band invariant — same editorial discipline.
- `days[].tag`: short string, max ~45 chars for legibility.
- `footer.cves_tracked` and `categories`: surfaced as footer chips.

## 6. Risks + Mitigations

| Risk | Mitigation |
|------|------------|
| Visual inconsistency with daily L22 ultra digests | Reuse `THEMES`, `qr_block`, header gradient style verbatim. Visual diff against neighboring L22 covers in PR review. |
| Increased spec maintenance burden (2 spec dirs) | Documented `kind` field disambiguates at-a-glance. CI globs both dirs in one pass. README pointer in each `_data/*_covers/README.md`. |
| Drift detection complexity (two render pipelines) | Both pipelines share the same `--check` contract (byte-identical re-render). CI runs both `--check` steps; either failing blocks the PR. |
| QR URL canonicalization for rollup slugs (`Week3_April_2026_Security_Digest`) | `_post_url_from_filename` already preserves underscores (`scripts/news/l20_dispatch.py:419-420`), and `check_cover_qr_urls.py` enforces it. Verified — no extra mitigation needed beyond running the existing gate. |
| Pre-commit `&` ampersand escape cycle (the 2026-01-26 incident) | Centralize escaping in `svg_rollup_generator.escape_xml()`; reuse the helper from L22 if present. Add a regression test that renders a spec containing `"AT&T"` and asserts `&amp;` in output. |
| Schema drift between weekly and monthly (`days` length 7 vs 4) | Pydantic-style validator in `load_spec()`: `if kind == weekly_rollup: assert len(days) == 7`; `if kind == monthly_index: assert len(days) in (4, 5)`. Reject mismatches with a clear error message. |
| `summary_card.highlights` not present in all 5 source posts | Audit before Phase 4. If missing on a post, lift highlights from the markdown body (the "핵심 이슈" subheadings in each daily section). Document the manual derivation in the spec comment. |

## 7. Success Criteria

- [ ] 5 rollup covers regenerated at ≥ 50 KB each (current ~8 KB).
- [ ] `python3 scripts/upgrade_rollup_cover.py --all --check` exits 0.
- [ ] `python3 scripts/upgrade_digest_cover.py --all --check` exits 0 (no
      regression on the existing pipeline).
- [ ] `python3 scripts/check_cover_qr_urls.py` exits 0 — every rollup cover's QR
      decodes to its canonical Jekyll permalink.
- [ ] `python3 scripts/check_posts.py` lint passes.
- [ ] PNG / AVIF / WEBP raster variants regenerated for all 5 covers.
- [ ] `pytest scripts/tests/test_upgrade_rollup_cover.py` passes with ≥ 10 tests
      covering: spec load, schema rejection, byte-stable re-render, ampersand
      escape, weekly vs monthly day-strip dispatch.
- [ ] 04-30 Week4 cover migrated and `_data/digest_covers/2026-04-30*.yml` (if it
      exists) removed in the same PR.
- [ ] Visual review: rollup covers share header style with L22 ultra; QR placement
      identical; no jarring palette discontinuity.

## 8. Out-of-Scope for v1

- Interactive elements (hover, click). Static SVG only.
- SMIL `<animate>` beyond what L22 already uses (keep the animation budget at
  L22-parity, not richer).
- Dark/light theme variants. Single dark theme matches L22.
- Auto-generation from post metadata in CI. v1 is hand-authored YAML; auto-gen is
  a future plan that *consumes* this renderer.
- Category breakdown bar chart (Layout B). Defer to v1.1 as footer enrichment.
- Animated week-tempo chart (Layout C timeline). Defer.
- L20 hero compatibility. Rollups are L22-family only.
- Localization. English text only, mirroring current cover policy.

## 9. Related

- `scripts/lib/svg_l22_generator.py` — palette + QR block (shared, no change).
- `scripts/upgrade_digest_cover.py` — sibling renderer, schema reference.
- `scripts/news/l20_dispatch.py:403` — QR URL canonicalization helper.
- `scripts/check_cover_qr_urls.py` — CI gate (no change; globs all weekly digest
  covers).
- `.omc/plans/upgrade-script-unification.md` — completed unification plan; this
  plan extends the same pattern (per-date YAML + parameterized renderer) to the
  rollup family.
- `.omc/plans/pre-april-digest-cover-migration.md` — sibling migration plan for
  pre-April covers.

## Decision Log

- **Why hybrid (D) over calendar grid (A)**: A surfaces day tempo but discards the
  editorial top-3 story — the post header itself promises a "top stories" narrative
  via `summary_card.highlights`. Dropping that narrative on the cover breaks the
  reader's expectation set by the post excerpt.
- **Why separate CLI over `--variant rollup` flag**: schema-union foot-guns. Daily
  digest specs have `bands[3]`; rollup specs have `top_highlights[3]` + `days[7|4]`.
  Forcing both into one validator multiplies the error paths and dilutes the
  `--check` contract.
- **Why migrate the 04-30 Week4 cover**: visual consistency in the rollup family
  outweighs the (small) churn of regenerating a 2-week-old asset. Keeping it on
  L22 leaves an outlier that future readers will flag as a bug.
- **Why preserve underscores in rollup slugs**: `_FILENAME_RE` in
  `l20_dispatch.py:419` already handles `Week3_April_2026_Security_Digest`
  correctly; changing the slug convention now would break every existing
  `redirect_from:` entry across all 5 rollup posts.
