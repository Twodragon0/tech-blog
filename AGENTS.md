# AGENTS.md - Coding Guidelines for Tech Blog

Last updated: 2026-01-22

This document provides coding guidelines and commands for agents working in this Jekyll-based DevSecOps technical blog repository.

## Quick Reference

| Resource | URL |
|----------|-----|
| **Production** | https://tech.2twodragon.com |
| **Backup** | https://twodragon0.github.io/tech-blog |
| **GitHub** | https://github.com/Twodragon0/tech-blog |
| **RSS** | https://tech.2twodragon.com/feed.xml |

## 1. Build/Lint/Test Commands

### Jekyll Site Commands
```bash
# Start local development server
bundle exec jekyll serve --host 0.0.0.0 --port 4000 --livereload

# Build site for production
bundle exec jekyll build --destination _site

# Clean site cache
bundle exec jekyll clean

# Check for broken links
bundle exec jekyll doctor
```

### Python Script Commands
```bash
# Generate post images and audio (all posts)
python3 scripts/generate_post_images.py --all --force

# Generate images for recent posts only
python3 scripts/generate_post_images.py --recent 5 --force

# Run single test
python3 -m pytest tests/test_specific.py::test_function_name -v

# Lint Python code
ruff check scripts/ --fix
ruff format scripts/

# Type checking
mypy scripts/ --ignore-missing-imports
```

### Image Management
```bash
# Rename images to English filenames
python3 scripts/rename_images_to_english.py --yes

# Check image files (unified script)
python3 scripts/verify_images_unified.py --all
```

### Link Management
```bash
# Fix all links (unified script)
python3 scripts/fix_links_unified.py --fix

# Replace code blocks with links
python3 scripts/replace_code_blocks_with_links.py
```

### Monitoring Scripts
```bash
# Monitor Sentry quota
./scripts/monitor_sentry_quota.sh

# Verify Sentry logs
node scripts/verify_sentry_logs.js

# Check Vercel logs
./scripts/check-vercel-logs.sh
```

## 2. Code Style Guidelines

### Python Code Style
- **Imports**: Use absolute imports, group by standard library, third-party, local
- **Formatting**: Use ruff formatter (Black-compatible)
- **Naming**: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants
- **Docstrings**: Use Google-style docstrings
- **Error Handling**: Use specific exceptions, log errors with context
- **Security**: Never hardcode secrets, use environment variables, mask sensitive data in logs

### Import Organization
```python
# Standard library imports
import os
import sys
import json
from pathlib import Path

# Third-party imports
import requests
from PIL import Image
import frontmatter

# Local imports
from scripts.utils import safe_log
```

### Type Hints
```python
from typing import Dict, List, Optional, Tuple, Union

def process_post(post_path: Path, force: bool = False) -> bool:
    """Process a single blog post.
    
    Args:
        post_path: Path to the markdown file
        force: Whether to force regeneration
        
    Returns:
        True if successful, False otherwise
    """
    pass
```

### Error Handling Pattern
```python
try:
    # Operation that might fail
    result = risky_operation()
except SpecificException as e:
    safe_log(f"Operation failed: {e}", "ERROR")
    return False
except Exception as e:
    safe_log(f"Unexpected error: {e}", "ERROR")
    return False
```

### Logging Security
```python
def safe_log(message: str, level: str = "INFO") -> None:
    """Log message with sensitive data masking."""
    safe_message = mask_sensitive_info(message)
    # Only log validated safe messages
    if _validate_masked_text(safe_message):
        print(f"[{level}] {safe_message}")
```

### File Operations Security
```python
def write_safe_file(file_path: Path, content: str) -> None:
    """Write content to file only if safe."""
    safe_content = mask_sensitive_info(content)
    if _validate_masked_text(safe_content):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(safe_content)
```

### Async/Await Patterns
```python
import asyncio
from typing import Coroutine

async def process_posts_async(posts: List[Path]) -> List[bool]:
    """Process multiple posts concurrently."""
    tasks = [process_single_post(post) for post in posts]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### Configuration Management
```python
# Use environment variables for sensitive data
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
USE_PRO_MODEL = os.getenv("USE_GEMINI_PRO_IMAGE", "false").lower() == "true"

# Validate configuration
if not GEMINI_API_KEY and not os.path.exists("prompts/"):
    raise ValueError("Either GEMINI_API_KEY or local prompts directory required")
```

### Testing Patterns
```python
import pytest
from unittest.mock import patch, MagicMock

class TestPostProcessor:
    def test_process_post_success(self, tmp_path):
        """Test successful post processing."""
        # Arrange
        post_file = tmp_path / "test.md"
        post_file.write_text("---\ntitle: Test\n---\nContent")
        
        # Act
        result = process_post(post_file)
        
        # Assert
        assert result is True
        assert (tmp_path / "test.mp3").exists()
    
    @patch('scripts.processor.generate_image_with_gemini')
    def test_process_post_no_api_key(self, mock_generate, tmp_path):
        """Test processing without API key falls back to prompts."""
        # Test fallback behavior
        pass
```

## 3. Cursor Rules Integration

### Project Overview
This is a Jekyll-based technical blog focused on DevSecOps, DevOps, FinOps, and cloud security. Content is written in Korean with practical, real-world experience.

### Core Principles (from .cursorrules)
- **Security First**: All code prioritizes security, uses defense in depth, minimal privilege
- **Practical Focus**: Emphasize real-world experience over theory
- **Structured Documentation**: Consistent post structure with clear sections

### Post Structure Requirements
```yaml
---
layout: post
title: "Title (Korean allowed)"
date: YYYY-MM-DD HH:MM:SS +0900
category: security|devsecops|devops|cloud|kubernetes|finops|incident
categories: [category1, category2]
tags: [tag1, tag2, tag3]
excerpt: "Summary (150-200 chars recommended)"
image: /assets/images/YYYY-MM-DD-English_Title.svg
---
```

### Image Requirements
- **English filenames only**: No Korean characters in image filenames
- **Format**: `YYYY-MM-DD-English_Title.svg|png|jpg`
- **Automatic conversion**: Use `scripts/rename_images_to_english.py` for Korean filenames
- **SVG text**: All text in SVGs must be English (no Korean)

### Code Block Handling
- Long code blocks (>10 lines or >500 chars): Replace with GitHub links
- Short examples (3-10 lines): Keep with reference links
- Very short (<3 lines): Keep original
- Always include language tags: ```python, ```bash, ```yaml

### Security Requirements
- Never hardcode API keys, passwords, tokens
- Use environment variables: `os.getenv("API_KEY", "")`
- Mask sensitive data in logs: `mask_sensitive_info()`
- Validate safe text before file writes: `_validate_masked_text()`

### Commit Rules
- No `Co-Authored-By: Claude` in commit messages
- Commit messages in Korean or English, concise
- Never commit secrets or sensitive files

### Build Commands
```bash
# Jekyll serve with live reload
bundle exec jekyll serve --livereload

# Image filename conversion
python3 scripts/rename_images_to_english.py

# Post image generation
python3 scripts/generate_post_images.py
```

## 4. File Structure Expectations

```
tech-blog/
├── _posts/              # Markdown posts (YYYY-MM-DD-Title.md)
├── _layouts/            # Jekyll layouts
├── _includes/           # Reusable components
├── assets/
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript
│   └── images/         # Images (English filenames only)
├── scripts/            # Python utilities
├── api/                # Vercel serverless functions
└── CLAUDE.md           # Instructions for Claude Code
```

## 5. Quality Assurance Checklist

### Pre-commit Checks
- [ ] No hardcoded secrets or API keys
- [ ] Image filenames are English only
- [ ] SVG files contain only English text
- [ ] Links point to real, existing resources
- [ ] Code blocks follow link replacement rules
- [ ] Front matter follows required format
- [ ] Security functions use proper masking

### Testing Requirements
- [ ] Unit tests for utility functions
- [ ] Integration tests for API calls (with mocks)
- [ ] File operation tests with temporary directories
- [ ] Error handling tests for network failures
- [ ] Security validation tests

### Performance Considerations
- [ ] Limit concurrent API calls to avoid rate limits
- [ ] Use appropriate timeouts for external requests
- [ ] Implement retry logic with exponential backoff
- [ ] Cache expensive operations when possible
- [ ] Monitor memory usage for large file operations

## 6. Current Implementation Status (2026-01-22)

### Security Features (Score: 9/10)
| Feature | Status | Implementation |
|---------|--------|----------------|
| CSP Headers | ✅ | vercel.json |
| HSTS | ✅ | 1 year, includeSubDomains, preload |
| X-Frame-Options | ✅ | SAMEORIGIN |
| Sentry Error Tracking | ✅ | Free Tier optimized |
| Sensitive Data Masking | ✅ | mask_sensitive_info() |

### Performance Features (Score: 9/10)
| Feature | Status | Implementation |
|---------|--------|----------------|
| Service Worker | ✅ | sw.js (offline support) |
| Resource Caching | ✅ | 1 year for assets |
| Lazy Loading | ✅ | IntersectionObserver |
| Critical CSS | ✅ | Inline for above-fold |
| Image Optimization | ✅ | WebP fallback |

### SEO Features (Score: 10/10)
| Feature | Status | Implementation |
|---------|--------|----------------|
| Open Graph | ✅ | Complete meta tags |
| Twitter Cards | ✅ | summary_large_image |
| JSON-LD | ✅ | BlogPosting schema |
| Sitemap | ✅ | Dynamic generation |
| RSS Feed | ✅ | /feed.xml |

### User Features
| Feature | Status | Implementation |
|---------|--------|----------------|
| Comments | ✅ | Giscus (GitHub Discussions) |
| AI Chatbot | ✅ | DeepSeek v3 |
| Dark/Light Mode | ✅ | System-aware |
| Search | ✅ | Client-side JSON |
| Translation | ✅ | Google Translate + MyMemory |

## 7. Responsive Design Breakpoints

```scss
// Mobile: single column
@media (max-width: 480px) {
  .posts-list { grid-template-columns: 1fr; }
}

// Tablet: two columns
@media (max-width: 768px) {
  .posts-list { grid-template-columns: repeat(2, 1fr); }
}

// Desktop: three columns (default)
.posts-list { grid-template-columns: repeat(3, 1fr); }
```

## 8. Key Configuration Files

| File | Purpose |
|------|---------|
| `_config.yml` | Jekyll configuration |
| `vercel.json` | Vercel deployment, headers, caching |
| `sw.js` | Service Worker for offline support |
| `_includes/head.html` | SEO, meta tags, CSP notes |
| `_includes/sentry.html` | Error tracking (Free tier optimized) |

## 9. Related Posts Configuration

- **Default count**: 3 posts
- **Location**: `_layouts/post.html` (line 106-126)
- **Matching**: By category first, then any posts

## 10. Daily Tech News Collection System

매일 자동으로 기술/보안 뉴스를 수집하고 블로그 초안을 생성하는 시스템입니다.

### 워크플로우
```
RSS Feeds (15+) → collect_tech_news.py → _data/collected_news.json
                                              ↓
_posts/ (게시) ← Manual Review ← generate_news_draft.py → _drafts/
```

### 뉴스 소스 (15개+)
| 카테고리 | 소스 |
|----------|------|
| **한국** | GeekNews, AWS Korea Blog |
| **보안** | AWS Security, MS Security, CISA, Datadog Security Labs, The Hacker News, Krebs on Security, Schneier, OWASP |
| **클라우드** | AWS Blog, Google Cloud, Azure |
| **DevOps** | Kubernetes Blog, CNCF, Hacker News |

### 사용법
```bash
# 뉴스 수집
python3 scripts/collect_tech_news.py --hours 24

# 초안 생성 (AI 요약)
export GEMINI_API_KEY="your-key"
python3 scripts/generate_news_draft.py --use-ai --max-posts 10

# 초안 생성 (기본)
python3 scripts/generate_news_draft.py
```

### GitHub Actions
- **스케줄**: 매일 오전 9시 (KST)
- **워크플로우**: `.github/workflows/daily-news.yml`
- **결과**: PR로 초안 제출, 수동 검토 후 게시

### 필요한 Secrets
| Secret | 설명 | 필수 |
|--------|------|------|
| `GEMINI_API_KEY` | AI 요약 생성용 | 선택 |

### 상세 문서
- `scripts/README_DAILY_NEWS.md`