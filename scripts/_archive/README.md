# Archived Scripts

This folder contains scripts that are:
- **One-off scripts** - Created for specific tasks that are no longer needed
- **Deprecated scripts** - Superseded by unified or improved versions
- **Experimental scripts** - Testing scripts that are not part of the main workflow

## Why Archived?

These scripts have been archived to:
1. Keep the main `scripts/` directory clean and focused
2. Preserve code for future reference if needed
3. Avoid confusion about which scripts to use

## Archived Scripts

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
