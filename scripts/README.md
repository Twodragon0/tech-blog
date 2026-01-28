# Scripts Guide

Utility scripts for managing the tech blog.

## Quick Start

```bash
# Validate all posts
python3 scripts/check_posts.py

# Fix links
python3 scripts/fix_links_unified.py --fix

# Verify images
python3 scripts/verify_images_unified.py --all

# Convert image names to English
python3 scripts/rename_images_to_english.py --yes
```

## Directory Structure

```
scripts/
├── README.md           # This file
├── requirements.txt    # Python dependencies
├── _archive/           # Deprecated/one-off scripts (see _archive/README.md)
└── *.py, *.sh          # Active script files

# Script documentation:
docs/scripts/           # Script-specific documentation
├── README_DAILY_NEWS.md
├── README_AI_IMPROVEMENT.md
├── README_AUDIO_GENERATION.md
└── ...
```

**Note**: 22 deprecated scripts have been moved to `scripts/_archive/`. See `_archive/README.md` for details.

---

## Primary Scripts (Recommended)

These unified scripts replace multiple older scripts:

| Script | Purpose | Replaces |
|--------|---------|----------|
| `check_posts.py` | Post validation | - |
| `fix_links_unified.py` | Link fixing | `fix_all_links.py`, `fix_github_links.py` |
| `verify_images_unified.py` | Image verification | `check_images.py`, `verify_images.py` |
| `rename_images_to_english.py` | Convert filenames | - |

---

## Scripts by Category

### Post Validation

```bash
# Validate all posts
python3 scripts/check_posts.py

# Validate specific post
python3 scripts/check_posts.py _posts/2025-01-01-example.md

# Check TOC
python3 scripts/check_toc.py
```

### Link Management

```bash
# Check links (dry-run)
python3 scripts/fix_links_unified.py --check

# Fix all links
python3 scripts/fix_links_unified.py --fix

# Validate reference links
python3 scripts/validate_all_reference_links.py
```

### Image Management

```bash
# Verify all images
python3 scripts/verify_images_unified.py --all

# Show posts with missing images
python3 scripts/verify_images_unified.py --missing

# Convert Korean filenames to English
python3 scripts/rename_images_to_english.py --yes

# Generate Gemini CLI commands
python3 scripts/verify_images_unified.py --all --generate-commands
```

### Image Generation

```bash
# Generate post images
export GEMINI_API_KEY="your-key"
python3 scripts/generate_post_images.py --all --force

# Generate missing diagrams
python3 scripts/generate_missing_diagrams.py _posts/2025-01-01-example.md

# Generate OG banners
python3 scripts/generate_og_banner.py
```

### Code Block Images

```bash
# Generate code block images for recent posts
python3 scripts/generate_code_images.py --recent 5

# Generate for all posts (with Dracula theme)
python3 scripts/generate_code_images.py --all --theme dracula

# List available themes
python3 scripts/generate_code_images.py --list-themes

# Options:
#   --theme: monokai, dracula, github-dark, one-dark, nord
#   --max-blocks: Limit code blocks per post
#   --max-lines: Max lines per code block (default: 30)
#   --no-line-numbers: Hide line numbers
#   --no-title-bar: Hide macOS-style title bar
#   --force: Regenerate existing images
```

### KISA Security Notices

```bash
# Collect KISA security notices (last 30 days)
python3 scripts/collect_kisa_security.py

# Generate blog drafts from notices
python3 scripts/collect_kisa_security.py --days 90 --generate-draft --max-drafts 5

# Use cached data
python3 scripts/collect_kisa_security.py --use-cache --generate-draft
```

### Audio/Video Generation

```bash
# Generate audio batch
python3 scripts/generate_audio_batch.py

# Generate video with Remotion
python3 scripts/generate_video_with_remotion.py

# Convert post to video
python3 scripts/generate_post_to_video.py
```

### Daily News

```bash
# Collect news
python3 scripts/collect_tech_news.py --hours 24

# Generate news draft
python3 scripts/generate_news_draft.py --use-ai --max-posts 10
```

### Post Improvement

```bash
# AI-based improvement (requires API key)
python3 scripts/ai_improve_posts.py

# Template-based improvement (no API key)
python3 scripts/smart_improve_posts.py
```

### SNS Sharing

```bash
# Share to SNS
python3 scripts/share_sns.py

# Auto share new posts
./scripts/auto_share_new_posts.sh
```

### Monitoring

```bash
# Monitor Sentry quota
./scripts/monitor_sentry_quota.sh

# Verify Sentry logs
node scripts/verify_sentry_logs.js

# Check Vercel logs
./scripts/check-vercel-logs.sh
```

---

## Environment Variables

| Variable | Purpose | Required For |
|----------|---------|--------------|
| `GEMINI_API_KEY` | Gemini API | Image generation, AI improvement |
| `CLAUDE_API_KEY` | Claude API | AI improvement |
| `DEEPSEEK_API_KEY` | DeepSeek API | Chat widget |
| `LINKEDIN_CLIENT_ID` | LinkedIn OAuth | SNS sharing |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn OAuth | SNS sharing |

---

## Installation

```bash
pip install -r scripts/requirements.txt
```

---

## Workflow Examples

### After Writing a New Post

```bash
# 1. Validate post
python3 scripts/check_posts.py _posts/2025-01-01-new_post.md

# 2. Verify images
python3 scripts/verify_images_unified.py --missing

# 3. Check links
python3 scripts/fix_links_unified.py --check
```

### Daily Maintenance

```bash
# Validate all posts
python3 scripts/check_posts.py

# Fix links
python3 scripts/fix_links_unified.py --fix

# Verify all images
python3 scripts/verify_images_unified.py --all
```

---

## Documentation

Script documentation is in `docs/scripts/`:

| Document | Topic |
|----------|-------|
| [README_DAILY_NEWS.md](../docs/scripts/README_DAILY_NEWS.md) | Daily news collection |
| [README_AI_IMPROVEMENT.md](../docs/scripts/README_AI_IMPROVEMENT.md) | AI-based post improvement |
| [README_AUDIO_GENERATION.md](../docs/scripts/README_AUDIO_GENERATION.md) | Audio generation |
| [README_POST_IMAGES.md](../docs/scripts/README_POST_IMAGES.md) | Post image generation |
| [README_VIDEO_GENERATION.md](../docs/scripts/README_VIDEO_GENERATION.md) | Video generation |

---

## All Scripts Reference

Complete reference of all 69 active Python scripts and 20 active shell scripts, organized by category.

### Post & Content Validation (4 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `check_posts.py` | Validate post front matter and structure | `--fix` to auto-correct, `--strict` for strict mode |
| `validate_post_quality.py` | Check post quality metrics (readability, length, SEO) | `--min-length`, `--max-length` |
| `check_toc.py` | Verify table of contents in posts | `--auto-add` to generate TOC |
| `add_toc_field.py` | Add TOC field to posts that lack it | `--force` to overwrite existing |

### Link Management (8 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `fix_links_unified.py` | Primary unified link fixer (dry-run or fix) | `--check`, `--fix`, `--verbose` |
| `fix_all_mermaid_safari.py` | Safari Mermaid compatibility fixes | `--dry-run`, `--fix` |
| `fix_dummy_links.py` | Remove dummy/placeholder links | `--dry-run` |
| `fix_mermaid_charts_for_posts.py` | Fix Mermaid diagram syntax in posts | `--fix`, `--verbose` |
| `fix_mermaid_dotted_arrows.py` | Fix dotted arrow syntax in Mermaid | `--fix` |
| `fix_mermaid_syntax.py` | General Mermaid syntax fixes | `--check`, `--fix` |
| `validate_all_reference_links.py` | Validate reference-style links | `--report` |
| `verify_post_links.py` | Verify all post links are valid | `--verbose` |

### Image Management (3 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `verify_images_unified.py` | Primary unified image verifier | `--all`, `--missing`, `--generate-commands` |
| `rename_images_to_english.py` | Convert Korean filenames to English | `--yes` to auto-confirm, `--dry-run` |
| `fetch_tistory_images.py` | Migrate images from Tistory blog | `--source-dir`, `--output-dir` |

### Image Generation (6 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `generate_post_images.py` | Generate post feature images | `--all`, `--force`, `--recent N` |
| `generate_code_images.py` | Convert code blocks to images | `--theme`, `--max-blocks`, `--max-lines` |
| `generate_missing_diagrams.py` | Generate missing diagrams | `--force` |
| `generate_og_banner.py` | Create Open Graph banners | `--all`, `--force` |
| `generate_aws_diagram.py` | AWS architecture diagrams | `--output-dir` |
| `generate_blog_diagrams.py` | General blog diagrams | `--type` (architecture/flow/process) |

### Audio/Video Generation (12 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `generate_audio_batch.py` | Batch audio generation from posts | `--all`, `--recent N`, `--force` |
| `generate_audio_from_improved_scripts.py` | Audio from improved scripts | `--batch-size`, `--output-dir` |
| `generate_audio_from_improved_split.py` | Split audio generation for long content | `--chunk-size`, `--overlap` |
| `generate_audio_from_script.py` | Single script audio conversion | `--script-file`, `--output` |
| `generate_enhanced_audio.py` | Enhanced audio quality processing | `--quality` (low/medium/high) |
| `generate_tts_simple.py` | Simple TTS generation | `--text`, `--output` |
| `generate_tts_split.py` | Split TTS for long text | `--max-length`, `--overlap` |
| `generate_tts_with_voice.py` | TTS with voice selection | `--voice`, `--language` |
| `generate_post_to_video.py` | Convert post to video | `--all`, `--format` (mp4/webm) |
| `generate_video_with_remotion.py` | Remotion video generation | `--composition`, `--fps` |
| `generate_segment_images.py` | Video segment images | `--segments`, `--resolution` |
| `check_audio_generation_status.py` | Check generation status | `--verbose`, `--retry-failed` |

### Content Improvement (5 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `ai_improve_posts.py` | AI-based post improvement (API required) | `--api` (gemini/claude/deepseek), `--all`, `--recent N` |
| `smart_improve_posts.py` | Template-based improvement (no API) | `--templates-dir`, `--force` |
| `continuous_improve_posts.py` | Continuous improvement loop | `--interval`, `--max-iterations` |
| `improve_post_summary.py` | Improve post summaries | `--all`, `--min-quality` |
| `improve_scripts_for_audio_video.py` | Improve A/V scripts | `--check`, `--improve` |

### News & Newsletter (10 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `collect_tech_news.py` | Collect tech news from RSS/APIs | `--hours`, `--sources` |
| `collect_kisa_security.py` | KISA security notices | `--days`, `--generate-draft`, `--use-cache` |
| `generate_news_draft.py` | Generate news drafts | `--use-ai`, `--max-posts`, `--category` |
| `generate_vendor_news_draft.py` | Vendor-specific news | `--vendor`, `--days` |
| `buttondown_notify.py` | Buttondown email notifications | `--post-id`, `--draft` |
| `buttondown_notify_batch.py` | Batch notifications | `--posts-dir`, `--dry-run` |
| `trigger_buttondown_email.py` | Trigger email send | `--email-id`, `--confirm` |
| `test_buttondown_email_send.py` | Test email sending | `--test-email` |
| `test_buttondown_api.py` | Test Buttondown API | `--endpoint`, `--method` |
| `preview_buttondown_email.py` | Preview email content | `--post-id`, `--html-output` |

### Mermaid Management (5 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `convert_mermaid_to_image.py` | Convert Mermaid to images | `--output-format` (svg/png), `--theme` |
| `validate_mermaid_charts.py` | Validate Mermaid charts | `--fix`, `--report` |
| `validate_mermaid_syntax.py` | Check Mermaid syntax | `--verbose` |
| `remove_mermaid_from_summary.py` | Clean Mermaid from summaries | `--fix` |
| `check_mermaid_in_summary.py` | Check for Mermaid in summaries | `--report` |

### SNS/Social Sharing (3 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `share_sns.py` | Share to social networks | `--platform` (twitter/linkedin), `--post-id` |
| `auto_publish_news.py` | Auto-publish news posts | `--schedule`, `--test` |
| `linkedin_oauth.py` | LinkedIn OAuth setup | `--client-id`, `--client-secret` |

### Utility Scripts (13 scripts)

| Script | Purpose | Key Options |
|--------|---------|------------|
| `cleanup_output_directory.py` | Clean output directories | `--dry-run`, `--older-than` (days) |
| `remove_duplicate_original_links.py` | Remove duplicate links | `--dry-run`, `--fix` |
| `fix_summary_format.py` | Fix summary formatting | `--all`, `--fix` |
| `remove_template_sections.py` | Remove template sections | `--sections` (comma-separated) |
| `replace_code_blocks_with_links.py` | Replace code with links | `--dry-run`, `--min-lines` |
| `replace_process_images_with_mermaid.py` | Convert to Mermaid | `--dry-run`, `--backup` |
| `clean_tts_formatting.py` | Clean TTS text formatting | `--fix` |
| `generate_all_scripts.py` | Generate all scripts | `--output-dir`, `--format` |
| `generate_complete_content.py` | Generate complete content | `--all`, `--include-audio` |
| `generate_complete_lecture.py` | Generate lecture content | `--course-id`, `--output` |
| `generate_favicon.py` | Generate favicon | `--size`, `--output` |
| `gemini_oauth_setup.py` | Setup Gemini OAuth | `--client-id` |
| `monitor_api_usage.py` | Monitor API usage | `--api` (gemini/claude/deepseek), `--report` |

### Shell Scripts (20 scripts)

#### Setup & Configuration (8 scripts)

| Script | Purpose |
|--------|---------|
| `setup_gemini_oauth.sh` | Gemini OAuth setup wizard |
| `setup_gemini_api_key.sh` | Gemini API key configuration |
| `setup_ai_keys.sh` | AI keys setup wrapper (all services) |
| `setup_linkedin_keys.sh` | LinkedIn OAuth keys setup |
| `add-deepseek-key.sh` | DeepSeek API key setup |
| `setup-sentry.sh` | Sentry error tracking configuration |
| `update-sentry-token.sh` | Update Sentry access token |
| `install_dependencies.sh` | Install Python and Node dependencies |

#### Automation (4 scripts)

| Script | Purpose |
|--------|---------|
| `start_ai_background.sh` | Start AI background service |
| `run_ai_improvement.sh` | Run AI improvement on posts |
| `setup_tmux_sessions.sh` | Setup tmux development sessions |
| `auto_share_new_posts.sh` | Auto-share new posts to SNS |

#### Monitoring (7 scripts)

| Script | Purpose |
|--------|---------|
| `monitor_sentry_quota.sh` | Monitor Sentry quota usage |
| `monitor_vercel_builds.sh` | Monitor Vercel builds |
| `monitor-security.sh` | Security monitoring (dependencies, config) |
| `check-vercel-logs.sh` | Check Vercel build/runtime logs |
| `setup_vercel_log_drains.sh` | Setup Vercel log drain configuration |
| `vercel_dashboard_setup.sh` | Vercel dashboard initialization |

#### Testing (2 scripts)

| Script | Purpose |
|--------|---------|
| `test-security.sh` | Security testing (linting, audits) |
| `diagnose-chat-api.sh` | Chat API diagnostics |

---

## Security Notes

- **Never** hardcode API keys
- **Always** use environment variables
- **Always** mask sensitive data in logs
- Back up before running batch operations
