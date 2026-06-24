# regen_l20_digest_covers.py

Faithfully regenerate **L20 Hero+2-Card digest covers** through the production
cron render path (`auto_publish_news._render_l20_svg_string`), so the on-disk
SVG is byte-identical to what the unattended publisher would emit. Rasters
(`*_og.png`, `*_og.webp/.avif`, `*_card.webp/.avif`) are rebuilt via
`scripts/_rebuild_all_l20_rasters.build_one` — the L20 digest path does **not**
auto-rasterize.

> Replaces the old one-shot `_regen_june_l20_covers.py` (month-agnostic from the
> start; the "june" name was misleading).

## Why this path only

Digest covers render via **L20**, not L22 (see `CLAUDE.md` → "Cover Generation
System" and the `cover-system` skill). `generate_post_images.py --svg-only`
does **not** reliably drive L20 and can silently fall back to L22. This tool
calls the exact cron function, so it is the single trustworthy way to
regenerate a live digest cover.

## Safety — never clobber non-digest / spec / rollup covers

This renders an **L20 digest** cover for every post it processes. Running it
over a spec-driven cover (`_data/{digest,rollup,l25}_covers/*.yml`), a
rollup/monthly post, or a non-digest **content/guide** post converts that cover
to L20 and breaks the drift / size / honesty gates (`cover-system` skill,
gotcha #1). Two guards:

| Guard | Behavior |
|-------|----------|
| `--targets-file FILE` | Explicit allowlist of post **stems** (one per line, no `.md`). The safe path for heterogeneous months that mix digests, guides, rollups and specs. Overrides `--glob`. Errors if any stem is missing. |
| `--digest-only` (default ON) | Skips any filename that is not a digest (no `*_Weekly_Digest_*` etc., and not `Monthly_Index` / `WeekN_`). Disable with `--no-digest-only` only when you know every match is a digest. |

Building a safe allowlist (exact-stem spec matching avoids the date-collision
trap where a digest shares a date with a guide-post spec):

```python
# pseudo: target = L20 + digest-name + NOT exact-stem spec + NOT monthly/rollup
spec_stems = {p.stem for d in ("digest_covers","l25_covers")
              for p in Path(f"_data/{d}").glob("*.yml")}
```

## Usage

```bash
# Whole month, digest-name-filtered (rollups/guides auto-skipped):
python3 scripts/regen_l20_digest_covers.py --glob "2026-06-*.md"

# Multi-month via pathlib range:
python3 scripts/regen_l20_digest_covers.py --glob "2026-0[123]-*.md"

# Heterogeneous month via explicit allowlist (safest):
python3 scripts/regen_l20_digest_covers.py --targets-file /tmp/targets.txt

# SVG only (skip raster) for a fast gate pre-check:
python3 scripts/regen_l20_digest_covers.py --glob "2026-06-*.md" --skip-raster
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--glob` | `2026-06-*.md` | Post glob under `_posts/` (pathlib ranges OK) |
| `--only` | "" | Substring filter on filename |
| `--exclude` | "" | Comma-separated substrings to skip |
| `--targets-file` | "" | Allowlist of stems; overrides `--glob` |
| `--no-digest-only` | (on) | Disable the digest-name safety filter |
| `--skip-raster` | off | Write SVG only, do not rebuild rasters |

## Always verify afterwards

Cover-only commits run pytest but **not** the CI drift/quality gates. Run the
full suite locally before committing (see `cover-system` skill → "Verify
workflow"):

```bash
PY=.venv/bin/python3
$PY scripts/score_cover_honesty.py --all --baseline scripts/cover_honesty_baseline.txt --strict
$PY scripts/check_svg_quality.py --ci assets/images/
$PY scripts/check_svg_title_ascii.py
$PY scripts/check_svg_size_gate.py --all
$PY scripts/check_l20_sidecard_advisory.py
$PY scripts/upgrade_digest_cover.py --all --check
$PY scripts/upgrade_rollup_cover.py --all --check
$PY scripts/lint_svg_compliance.py --report
$PY -m pytest scripts/tests/ -q
```
