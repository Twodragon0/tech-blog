# 2026-02-20 Architecture and Content Improvement Report

## Scope

- Code and workflow consistency check for daily news automation
- Today's RSS collection and auto post generation
- Repository-wide post quality reinforcement (summary/link/code-block normalization)

## What Was Executed

### 1) Daily RSS and Auto Posting

- `python3 scripts/collect_tech_news.py --hours 24`
  - Collected **121 unique items** from configured sources
  - Saved to `_data/collected_news.json`
- `python3 scripts/auto_publish_news.py --hours 24 --mode tech-blog`
  - Generated post: `_posts/2026-02-20-Tech_Blog_Weekly_Digest_AI_Data_Cloud.md`
  - Generated image: `assets/images/2026-02-20-Tech_Blog_Weekly_Digest_AI_Data_Cloud.svg`

### 2) Workflow Compatibility Fix (Code Improvement)

- Updated `scripts/generate_news_draft.py` to accept legacy `--use-ai` flag.
- Reason: script docs/workflow expected `--use-ai`, but runtime rejected it.
- Result: command works without breaking existing automation habits.

### 3) Whole-Repository Content Reinforcement

- `python3 scripts/fix_summary_format.py`
  - Applied summary format normalization across posts
- `python3 scripts/replace_code_blocks_with_links.py`
  - Replaced long code blocks with reference-link style in bulk (80 posts updated)
- `python3 scripts/rename_images_to_english.py --yes`
  - Verified naming compliance (no Korean filenames found)
- `python3 scripts/verify_images_unified.py --all`
  - Verified image integrity for all 85 posts (0 issues)
- `python3 scripts/fix_links_unified.py --fix`
  - Applied link normalization and surfaced remaining suspicious placeholders/dummy links

### 4) New Daily Post Quality Hardening

- Added to `_posts/2026-02-20-Tech_Blog_Weekly_Digest_AI_Data_Cloud.md`:
  - `Executive Summary`
  - `위험 스코어카드` table
  - execution checklist section
  - related post cross-reference (`post_url`)
  - Liquid include quoting fix for `ai-summary-card`

Quality check:

- `python3 scripts/validate_post_quality.py _posts/2026-02-20-Tech_Blog_Weekly_Digest_AI_Data_Cloud.md`
- Score improved from **45/100 -> 84/100**

## Architecture Findings

### A. Script and documentation drift

- `generate_news_draft.py` behavior differs from older docs/examples (`--use-ai`).
- This drift can break automated routines and user expectations.

### B. Content quality debt is structural, not one-off

- `check_posts.py` still reports many legacy issues (especially long code blocks and placeholder links) in older posts.
- Most are historical formatting debt, not a single post bug.

### C. Build verification environment mismatch

- Jekyll build could not run in this environment because local Ruby is `2.6.10`, but project requires `>=2.7.0`.

## Recommended Next Improvements (Priority)

1. **P0 - Align runtime and docs automatically**
   - Add CI check that validates script `--help` examples against docs snippets.
2. **P0 - Baseline content quality gate**
   - Add a non-blocking dashboard job first, then block only new/changed posts with severe issues.
3. **P1 - Dummy link triage pipeline**
   - Separate true dummy links from intentionally shown sample URLs in code snippets.
4. **P1 - Ruby toolchain pinning**
   - Add explicit local setup script (or devcontainer) to guarantee Jekyll build reproducibility.
5. **P2 - Progressive refactor of legacy mega-posts**
   - Split oversized posts and externalize very long snippets to GitHub references with concise in-post excerpts.

## Verification Log (Key Results)

- RSS collection: success
- Auto post generation: success
- Image integrity check: success (0 issues)
- New post quality validation: success (84/100)
- Jekyll build: not executable in current runtime (Ruby version mismatch)
