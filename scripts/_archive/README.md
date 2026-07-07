# Archived Scripts

This folder contains scripts that are:
- **One-off scripts** - Created for specific tasks that are no longer needed
- **Deprecated scripts** - Superseded by unified or improved versions
- **Experimental scripts** - Testing scripts that are not part of the main workflow
- **Migrated scripts** - Moved to other projects (backups kept here)

## Why Archived?

These scripts have been archived to:
1. Keep the main `scripts/` directory clean and focused
2. Preserve code for future reference if needed
3. Avoid confusion about which scripts to use

## Migrated to online-course (14 scripts)

These audio/video scripts have been migrated to `~/Desktop/online-course/scripts/audio_video/`:

| Script | New Location |
|--------|--------------|
| `generate_audio_batch.py` | `online-course/scripts/audio_video/` |
| `generate_audio_from_improved_scripts.py` | `online-course/scripts/audio_video/` |
| `generate_audio_from_improved_split.py` | `online-course/scripts/audio_video/` |
| `generate_audio_from_script.py` | `online-course/scripts/audio_video/` |
| `generate_enhanced_audio.py` | `online-course/scripts/audio_video/` |
| `generate_tts_simple.py` | `online-course/scripts/audio_video/` |
| `generate_tts_split.py` | `online-course/scripts/audio_video/` |
| `generate_tts_with_voice.py` | `online-course/scripts/audio_video/` |
| `generate_post_to_video.py` | `online-course/scripts/audio_video/` |
| `generate_video_with_remotion.py` | `online-course/scripts/audio_video/` |
| `generate_segment_images.py` | `online-course/scripts/audio_video/` |
| `improve_scripts_for_audio_video.py` | `online-course/scripts/audio_video/` |
| `clean_tts_formatting.py` | `online-course/scripts/audio_video/` |
| `check_audio_generation_status.py` | `online-course/scripts/audio_video/` |

> See [AUDIO_VIDEO_MOVED.md](../AUDIO_VIDEO_MOVED.md) for usage instructions.

## Other Archived Scripts

| Script | Reason |
|--------|--------|
| `generate_postmortem_*.py` | One-off for specific incident post |
| `generate_nano_bananas.py` | Experimental image generator |
| `fix_korean_image_refs.py` | One-off migration script |
| `cleanup_empty_images.py` | One-off cleanup |
| `fix_all_duplicates.py` | One-off duplicate fix |
| `check_unrelated_images.py` | Superseded by `verify_images_unified.py` |
| `remove_unrelated_images.py` | One-off cleanup |
| `enhance_all_posts.py` | Superseded by `ai_improve_posts.py` |
| `enhance_posts_summary.py` | Superseded by `smart_improve_posts.py` |
| `batch_expand_scripts.py` | One-off batch processing |
| `expand_script_with_gemini.py` | Experimental Gemini integration |
| `check_post_structure.py` | Superseded by `check_posts.py` |
| `fix_post_structure.py` | One-off structure fix |
| `fix_missing_fields.py` | One-off front matter fix |
| `final_verify_posts.py` | Superseded by `check_posts.py` |
| `fix_posts.py` | General fix superseded by unified scripts |
| `check_duplicates.py` | One-off duplicate check |
| `fix_image_tags.py` | One-off image tag fix |
| `generate_tts_comparison.py` | Experimental TTS comparison |
| `test_tts_providers.py` | Experimental TTS testing |

## L22 Digest Cover Pipeline (Deprecated)

| Script | Reason |
|--------|--------|
| `regenerate_2026_04_plus_covers.py` | Superseded by `scripts/upgrade_digest_cover.py` reading `_data/digest_covers/*.yml` via the spec-driven `render_bands_svg` flow. This was a one-shot regen tool for 2026-04+ digest covers using the L22 ultra dispatch (`scripts.news.l22_dispatch.generate_l22_digest_svg`). Phase 3 of L22 deprecation plan (archived 2026-05-27). Terminal deletion scheduled for Phase 4 (≥1 week after Phase 3). |

## One-Shot Cover/Content Migrations (Archived 2026-07-07)

Verified zero-reference across the whole repo (no workflow, hook, cron, `import`, or subprocess call). Completed one-shot seeders/migrations superseded by the current spec-driven cover pipeline (`upgrade_{digest,rollup,l25}_cover.py`, L20 cron render) and unified fixers.

| Script | Reason |
|--------|--------|
| `_seed_2025_l20_batch_f.py` | One-shot: seed L20 specs for 2025 batch F. Specs now committed + maintained by `upgrade_*_cover.py`. |
| `_seed_2025_l20_batch_g.py` | One-shot L20 spec seeder (2025 batch G). |
| `_seed_apr_23_24_l20.py` | One-shot L20 spec seeder (2026-04-23/24 digests). |
| `_seed_april_orphans_l20.py` | One-shot L20 spec seeder (4 orphan April covers). |
| `_seed_feb_l20_batch_d.py` | One-shot L20 spec seeder (Feb batch D). |
| `_seed_feb_l20_batch_e.py` | One-shot L20 spec seeder (Feb batch E). |
| `_seed_jan_l20_batch_a.py` | One-shot L20 spec seeder (Jan batch A). |
| `_seed_jan_l20_batch_b.py` | One-shot L20 spec seeder (Jan batch B). |
| `_seed_jan_l20_batch_c.py` | One-shot L20 spec seeder (Jan batch C). |
| `_seed_march_l20.py` | One-shot L20 spec seeder (13 March 2026 posts). |
| `_seed_may_23_26_l20.py` | One-shot L20 spec seeder (2026-05-23..26 digests). |
| `convert_may_pinned_to_l20.py` | One-shot: convert 12 pinned L22 May covers to L20 (fixed date list). |
| `convert_remaining_news_cards.py` | One-shot: convert remaining 9 posts to `news-card.html` (migration complete). |
| `convert_summary_cards.py` | One-shot: migrate inline `ai-summary-card` HTML to include form (complete). |
| `convert_to_news_cards.py` | One-shot: migrate weekly-digest posts to `news-card.html` (complete). |
| `koreanize_weekly_digest_content.py` | One-shot Korean-ization of weekly digest content. |
| `polish_weekly_digest_text.py` | One-shot weekly-digest text polish. |
| `upgrade_2025_svgs_l25_single.py` | One-shot: upgrade 2025 legacy covers via L25-single (complete). |
| `upgrade_2026_01_02_to_l20_hero.py` | One-shot: regenerate 15 Jan/Feb 2026 digest covers at L20 hero. |
| `regenerate_all_svgs.py` | Superseded pre-L20 template regenerator (would overwrite covers with deprecated style). |
| `regenerate_svgs.py` | Superseded pre-L20 template regenerator. |
| `regenerate_visual_svgs.py` | Superseded keyword-routed visual regenerator (Step-0 deprecated keyword routing). |
| `fix_svg_titles.py` | One-shot: insert missing `<title>` elements (superseded by generator + gates). |
| `fix_svg_truncated_titles.py` | One-shot: repair "..."-truncated SVG title text. |
| `_dedup_practical_blocks.py` | One-shot dedup wrapper; superseded by `python3 scripts/check_posts.py --fix`. |

## Using Archived Scripts

If you need to use an archived script:
1. Review the code first - it may be outdated
2. Test in a safe environment
3. Consider if there's a newer alternative in `scripts/`

## Primary Scripts (Use Instead)

| Task | Use This |
|------|----------|
| Post validation | `check_posts.py` |
| Image verification | `verify_images_unified.py` |
| Link fixing | `fix_links_unified.py` |
| Post improvement | `ai_improve_posts.py` or `smart_improve_posts.py` |
