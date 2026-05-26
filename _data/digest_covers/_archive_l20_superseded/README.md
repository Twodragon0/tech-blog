# Archived L22 Digest Cover Specs

This directory holds 43 weekly-digest cover specs that were superseded by L20
Hero+2-Card equivalents in commits `ecb0564d`, `6810dba6`, `a27a277b`, and
`d7e9cea7` (Jan–May 2026 unification batches).

The files were **archived rather than deleted** so that
`scripts/upgrade_digest_cover.py --all` no longer accidentally re-renders them
back to L22 (the renderer uses non-recursive `Path.glob("*.yml")`, so anything
inside this subdirectory is invisible to it). The full curated history remains
preserved on disk and via `git log --follow` for rollback purposes.

## Why archived, not deleted

- Each entry below has a 1:1 L20 replacement under `_data/l20_covers/` that
  drives the deployed SVG. Keeping the L22 spec live would create renderer
  drift: the next `--all` run would overwrite the L20 SVG with a stale L22
  render and silently lose the visual unification.
- Hand-curated band content (KPIs, source attributions, action recommendations)
  was non-trivial to assemble. Keeping the original is cheaper than
  reconstructing it from git blob history if a date ever needs to revert to
  L22.

## Date map (archived spec → superseding L20 spec)

Every archived `{date}.yml` corresponds to an L20 spec at
`_data/l20_covers/{date}-{slug}.yml`. The slug is the canonical post slug; the
mapping is mechanical and deterministic. The archived spec's `slug:` field
already holds the same value as the L20 spec's filename suffix.

Counts:
- January 2026 (9):  `2026-01-23..2026-01-31`
- February 2026 (21): `2026-02-01, 04..08, 11..13, 17..28`
- March 2026 (1):    `2026-03-23`
- April 2026 (2):    `2026-04-29, 2026-04-30`
- May 2026 (10):     `2026-05-01..2026-05-10`

Total: 43 specs.

## Restoring a single archived spec

If a specific date needs to revert from L20 back to its original L22 layout:

```bash
DATE=2026-05-08
# 1. move the archived spec back into the active directory
git mv _data/digest_covers/_archive_l20_superseded/${DATE}.yml \
       _data/digest_covers/${DATE}.yml

# 2. delete the superseding L20 spec (or it will keep winning the render race)
git rm _data/l20_covers/${DATE}-*.yml

# 3. re-render the L22 SVG from the restored spec
python3 scripts/upgrade_digest_cover.py --spec _data/digest_covers/${DATE}.yml

# 4. rebuild raster variants (use the per-batch helper if available, or)
python3 scripts/build_feb_l20_rasters.py   # adapt the date glob inside
```

## Restoring all 43 archived specs (full rollback)

```bash
git mv _data/digest_covers/_archive_l20_superseded/*.yml _data/digest_covers/
git rm _data/l20_covers/{2026-01-2[3-9],2026-01-3[0-1],2026-02-01,2026-02-0[4-8],2026-02-1[1-3],2026-02-1[7-9],2026-02-2[0-8],2026-03-23,2026-04-{29,30},2026-05-0[1-9],2026-05-10}-*.yml
python3 scripts/upgrade_digest_cover.py --all
```

(Then rebuild rasters and commit.)

## Monthly index migration to L20 (post-archive)

Two posts originally rendered through `scripts/upgrade_rollup_cover.py`
(monthly index pipeline, ~75 KB rollup SVGs) were migrated to the L20
pipeline in commit `1ca3b977` so the entire Jan–May 2026 visual family
stays consistent with `2026-03/04`:

- `2026-01-31-January_2026_Security_Digest_Monthly_Index`
- `2026-02-28-February_2026_Security_Digest_Monthly_Index`

The corresponding `_data/rollup_covers/2026-01-31.yml` and
`_data/rollup_covers/2026-02-28.yml` specs were left in place but are
no longer consulted, because `scripts/upgrade_l20_cover.py --all`
matches `_data/l20_covers/*.yml` first and writes the same SVG path,
overwriting the rollup output. If you ever need to restore the rollup
look:

```bash
# 1. delete the L20 spec
git rm _data/l20_covers/2026-01-31-January_2026_Security_Digest_Monthly_Index.yml
git rm _data/l20_covers/2026-02-28-February_2026_Security_Digest_Monthly_Index.yml

# 2. re-render from the rollup spec (still authoritative for that date)
python3 scripts/upgrade_rollup_cover.py --spec _data/rollup_covers/2026-01-31.yml
python3 scripts/upgrade_rollup_cover.py --spec _data/rollup_covers/2026-02-28.yml
```

Note: `test_known_rollup_dates_classified_correctly` was updated in
the same commit to drop these two stems from its expected-rollup list.

## Related history

- Commit `aba4195c` — initial archive move (43 files).
- Commit `ecb0564d` — Jan + 03-23 L20 batch.
- Commit `6810dba6` — Feb L20 batch.
- Commit `a27a277b` — Mar L20 batch.
- Commit `d7e9cea7` — May pinned + Apr 29/30 L20 batch.
- Commit `218f5709` — L20 decoration layer enrichment.
- Commit `c3751f71` — L20 visual-primitive secondary detail icons.
- Commit `1ca3b977` — Jan + Feb 39 cover conversions + monthly index migration.
