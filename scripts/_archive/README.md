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
