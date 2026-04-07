<!-- Parent: ../AGENTS.md -->
# scripts/ — AI Agent Guidelines

**Last updated**: 2026-04-08

This directory contains 111 Python scripts and 20+ shell scripts for blog automation.

## Directory Layout

```
scripts/
├── lib/                  # Shared libraries (import these, never duplicate)
│   ├── security.py       # mask_sensitive_info(), _validate_masked_text()
│   └── logging_utils.py  # Structured logging with context
├── news/                 # News collection pipeline modules
│   ├── analyzer.py       # Article analysis and scoring
│   ├── loader.py         # RSS feed loading and parsing
│   ├── content_generator.py  # Post content generation
│   ├── enhancer.py       # Content enhancement
│   ├── config.py         # News collection config
│   └── svg_generator.py  # SVG image generation for news posts
├── tests/                # pytest suite (287 tests, ~0.19s)
│   ├── conftest.py       # Shared fixtures; API calls disabled here
│   ├── test_news_templates.py   # Template branch coverage
│   └── test_*.py         # Other test modules
└── _archive/             # Deprecated scripts — do not use or import
```

## Code Style

```python
# Import order: stdlib → third-party → local
import os
from pathlib import Path

import requests
import frontmatter

from scripts.lib.security import mask_sensitive_info
from scripts.lib.logging_utils import safe_log
```

- Naming: `snake_case` (vars/funcs), `PascalCase` (classes), `UPPER_CASE` (constants)
- Type hints required on all function signatures
- Docstrings: Google-style
- File size: 200-400 lines typical, 800 max

## Security Patterns (mandatory)

Always use `scripts/lib/security.py` for any output that might contain secrets:

```python
from scripts.lib.security import mask_sensitive_info

def safe_log(message: str) -> None:
    print(f"[INFO] {mask_sensitive_info(message)}")
```

Never use `print()` with raw API keys, tokens, or user-supplied data.

## Canonical Scripts

| Script | Purpose | Flags |
|--------|---------|-------|
| `check_posts.py` | Validate front matter and post structure | |
| `fix_links_unified.py` | Validate and fix links | `--fix` |
| `verify_images_unified.py` | Check image file existence | `--all` |
| `rename_images_to_english.py` | Convert Korean filenames | `--yes` |
| `generate_post_images.py` | Generate missing SVG images | `--all` |
| `collect_tech_news.py` | RSS feed aggregation | `--hours N` |
| `generate_news_draft.py` | AI-assisted draft generation | `--use-ai --max-posts N` |
| `auto_publish_news.py` | Template-based auto-publish | |

Do not create new scripts for tasks these already handle.

## Testing

```bash
pytest scripts/tests/                               # Run all tests
pytest scripts/tests/ --cov=scripts --cov-fail-under=40
ruff check scripts/ --fix && ruff format scripts/   # Lint + format
mypy scripts/ --ignore-missing-imports              # Type check
```

- Pre-commit hook auto-runs pytest when `auto_publish_news.py` or `scripts/tests/` changes
- Coverage target: 40%+ for `auto_publish_news.py`
- When adding a template branch in `auto_publish_news.py`, add a corresponding test in `tests/test_news_templates.py`
- Branch order = priority: specific keywords before general ones

## Auto-Yes

Scripts support `--yes` / `-y` flags. Set `TECH_BLOG_AUTO_YES=1` or `CI=1` to skip confirmations.

## _archive/

Scripts in `_archive/` are deprecated. Do not import from them or use them as reference — they may have outdated patterns.
