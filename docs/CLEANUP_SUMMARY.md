# Repository Cleanup Summary

**Date**: 2026-01-23

This document summarizes the repository cleanup and consolidation performed.

## Changes Overview

### 1. Root Directory Cleanup

**Removed temporary files:**
- `ai_improvement_log.txt`
- `ai_improvement.log`
- `ai_improvement.pid`
- `improvement_log.txt`
- `all_images.txt`
- `referenced_images.txt`
- `Untitled.base`
- `Untitled.canvas`

**Removed directories:**
- `.obsidian/` - Obsidian editor config (not needed for blog)

### 2. Documentation Consolidation

**Moved `scripts/docs/` to `docs/scripts/`:**
- 33 script-specific documentation files now in unified `docs/` structure
- Updated `scripts/README.md` with new documentation paths
- Updated `docs/README.md` to include Script Documentation section

**New documentation structure:**
```
docs/
├── pdca/              # Feature-level PDCA (Plan-Do-Check-Act)
├── pipeline/          # Project-level pipeline & architecture
├── scripts/           # Script-specific documentation (NEW LOCATION)
├── guides/            # Content creation guides
├── optimization/      # Performance optimization
├── setup/             # Setup guides
└── troubleshooting/   # Problem solving
```

### 3. Scripts Consolidation

**Created `scripts/_archive/` for deprecated scripts:**
- 22 scripts archived
- Created `_archive/README.md` documenting why each was archived

**Archived scripts:**
| Script | Reason |
|--------|--------|
| `generate_postmortem_*.py` | One-off for specific incident |
| `generate_nano_bananas.py` | Experimental |
| `fix_korean_image_refs.py` | One-off migration |
| `cleanup_empty_images.py` | One-off cleanup |
| `fix_all_duplicates.py` | One-off fix |
| `check_unrelated_images.py` | Superseded |
| `remove_unrelated_images.py` | One-off cleanup |
| `enhance_all_posts.py` | Superseded by `ai_improve_posts.py` |
| `enhance_posts_summary.py` | Superseded |
| `batch_expand_scripts.py` | One-off batch |
| `expand_script_with_gemini.py` | Experimental |
| `check_post_structure.py` | Superseded by `check_posts.py` |
| `fix_post_structure.py` | One-off fix |
| `fix_missing_fields.py` | One-off fix |
| `final_verify_posts.py` | Superseded |
| `fix_posts.py` | General fix superseded |
| `check_duplicates.py` | One-off |
| `fix_image_tags.py` | One-off |
| `generate_tts_comparison.py` | Experimental |
| `test_tts_providers.py` | Experimental |

**Script count:**
- Before: 88 Python scripts
- After: 66 active Python scripts
- Archived: 22 scripts

### 4. .gitignore Updates

**Added patterns:**
```gitignore
# Temporary files
Untitled.*

# Obsidian
.obsidian/

# Image analysis temp files
all_images.txt
referenced_images.txt

# IDE
.vscode/
.idea/

# Ruff cache
.ruff_cache/

# Claude/Cursor session
.claude/
.cursor/
.sisyphus/
```

## Repository Statistics

### Before Cleanup
- Root directory: 63 items
- Python scripts: 88
- Documentation scattered across multiple locations

### After Cleanup
- Root directory: ~55 items (cleaner)
- Python scripts: 66 active + 22 archived
- Documentation consolidated in `docs/` with clear structure

## Benefits

1. **Cleaner root directory** - Temporary files removed
2. **Unified documentation** - All docs now in `docs/` folder
3. **Clearer script organization** - Active vs archived scripts separated
4. **Improved discoverability** - Better README navigation
5. **Reduced confusion** - Deprecated scripts clearly marked

## Primary Scripts (Recommended)

| Task | Script |
|------|--------|
| Post validation | `check_posts.py` |
| Image verification | `verify_images_unified.py` |
| Link fixing | `fix_links_unified.py` |
| Image renaming | `rename_images_to_english.py` |
| Post improvement | `ai_improve_posts.py` or `smart_improve_posts.py` |
| News collection | `collect_tech_news.py` |
| SNS sharing | `share_sns.py` |

## See Also

- [docs/README.md](README.md) - Documentation index
- [scripts/README.md](../scripts/README.md) - Scripts guide
- [scripts/_archive/README.md](../scripts/_archive/README.md) - Archived scripts
