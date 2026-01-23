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

## Security Notes

- **Never** hardcode API keys
- **Always** use environment variables
- **Always** mask sensitive data in logs
- Back up before running batch operations
