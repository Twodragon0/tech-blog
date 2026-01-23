# AGENTS.md - AI Agent Coding Guidelines

**Last updated**: 2026-01-22

Coding guidelines for AI agents (Claude, Cursor, Copilot, etc.) working on this Jekyll-based DevSecOps technical blog.

## Quick Reference

| Resource | URL |
|----------|-----|
| **Production** | https://tech.2twodragon.com |
| **Backup** | https://twodragon0.github.io/tech-blog |
| **GitHub** | https://github.com/Twodragon0/tech-blog |
| **RSS** | https://tech.2twodragon.com/feed.xml |

---

## 1. Build/Lint/Test Commands

### Jekyll
```bash
bundle exec jekyll serve --host 0.0.0.0 --port 4000 --livereload
bundle exec jekyll build --destination _site
bundle exec jekyll clean
```

### Python Scripts
```bash
python3 scripts/check_posts.py                    # Validate all posts
python3 scripts/fix_links_unified.py --fix        # Fix links
python3 scripts/verify_images_unified.py --all    # Verify images
python3 scripts/rename_images_to_english.py --yes # Convert image names
python3 scripts/generate_post_images.py --all     # Generate images

# Lint & format
ruff check scripts/ --fix && ruff format scripts/
mypy scripts/ --ignore-missing-imports
```

### Monitoring
```bash
./scripts/monitor_sentry_quota.sh
node scripts/verify_sentry_logs.js
./scripts/check-vercel-logs.sh
```

---

## 2. Code Style Guidelines

### Python
```python
# Standard library
import os
import sys
from pathlib import Path

# Third-party
import requests
import frontmatter

# Local
from scripts.utils import safe_log
```

- **Naming**: `snake_case` (vars/funcs), `PascalCase` (classes), `UPPER_CASE` (constants)
- **Docstrings**: Google-style
- **Type hints**: Always use them

### Security Patterns
```python
# Log with masking
def safe_log(message: str, level: str = "INFO") -> None:
    safe_message = mask_sensitive_info(message)
    if _validate_masked_text(safe_message):
        print(f"[{level}] {safe_message}")

# Write with validation
def write_safe_file(file_path: Path, content: str) -> None:
    safe_content = mask_sensitive_info(content)
    if _validate_masked_text(safe_content):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(safe_content)
```

---

## 3. File Structure

```
tech-blog/
├── _posts/              # Blog posts (YYYY-MM-DD-Title.md)
├── _layouts/            # Jekyll layouts
├── _includes/           # Reusable components
├── assets/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript
│   └── images/          # Images (English filenames ONLY)
├── scripts/             # Python/Bash utilities
│   ├── docs/            # Script-specific documentation
│   └── README.md        # Script guide
├── docs/                # Project documentation
│   ├── guides/          # Content creation guides
│   ├── optimization/    # Performance optimization
│   ├── setup/           # Setup and configuration
│   └── troubleshooting/ # Troubleshooting guides
├── api/                 # Vercel Serverless Functions
├── .cursorrules         # Cursor AI rules (detailed)
├── CLAUDE.md            # Claude Code instructions
├── AGENTS.md            # This file
└── SECURITY.md          # Security policy
```

---

## 4. Post Structure Requirements

### Front Matter
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

### Categories
- `security` - Security-related
- `devsecops` - DevSecOps
- `devops` - DevOps
- `cloud` - Cloud services
- `kubernetes` - Kubernetes
- `finops` - FinOps
- `incident` - Incident analysis

---

## 5. Critical Rules

### Images
| Rule | Requirement |
|------|-------------|
| Filename | **English only** - No Korean characters |
| Format | `YYYY-MM-DD-English_Title.svg\|png\|jpg` |
| SVG text | **English only** |
| Conversion | `scripts/rename_images_to_english.py` |

### Code Blocks
| Length | Action |
|--------|--------|
| >10 lines | Replace with GitHub link + HTML comment |
| 3-10 lines | Keep with reference link |
| <3 lines | Keep original |

### Security
- **Never** hardcode API keys, passwords, tokens
- **Always** use `os.getenv("API_KEY", "")`
- **Always** mask sensitive data in logs
- **Never** commit secrets or `.env` files

### Commits
- **No** `Co-Authored-By: Claude` in messages
- Korean or English, concise

---

## 6. Quality Checklist

### Pre-commit
- [ ] No hardcoded secrets
- [ ] Image filenames are English only
- [ ] SVG files contain only English text
- [ ] Links point to real resources
- [ ] Code blocks have language tags
- [ ] Front matter follows format

### Testing
- [ ] Unit tests for utilities
- [ ] File operations with temp directories
- [ ] Error handling tests
- [ ] Security validation tests

---

## 7. Implementation Status

| Feature | Score | Implementation | Next Steps |
|---------|-------|----------------|------------|
| **Security** | 9/10 | CSP, HSTS, Sentry (Free Tier), Masking, Input Validation | Periodic CSP review, dependency updates |
| **Performance** | 9/10 | Service Worker, Caching, Lazy Loading, Critical CSS | Image optimization, bundle size reduction |
| **SEO** | 10/10 | OG, Twitter Cards, JSON-LD, Sitemap, RSS | Maintain current level |
| **User Features** | 9/10 | Giscus, DeepSeek chatbot, Dark/Light mode, Search | Accessibility improvements |
| **Cost Optimization** | 9/10 | API caching, rate limiting, free tier optimization | Monitor usage, optimize further |
| **Operational Efficiency** | 8/10 | Automation scripts, CI/CD, monitoring | Enhanced error recovery |

---

## 8. Daily News Collection System

Automated tech/security news collection and blog draft generation.

### Workflow
```
RSS Feeds (15+) → collect_tech_news.py → _data/collected_news.json
                                              ↓
_posts/ ← Manual Review ← generate_news_draft.py → _drafts/
```

### Usage
```bash
python3 scripts/collect_tech_news.py --hours 24
python3 scripts/generate_news_draft.py --use-ai --max-posts 10
```

---

## 9. Related Documentation

| Document | Purpose |
|----------|---------|
| `.cursorrules` | Detailed Cursor AI rules |
| `CLAUDE.md` | Claude Code instructions |
| `SECURITY.md` | Security policy |
| `docs/README.md` | Documentation index |
| `scripts/README.md` | Script guide |
| `scripts/docs/` | Script-specific docs |

---

## 10. Security Best Practices

### Input Validation
- Always validate user inputs (XSS, Injection patterns)
- Sanitize HTML content before rendering
- Validate URLs and file uploads
- Use parameterized queries (if using databases)

### Error Handling
- Never expose sensitive info in error messages
- Log detailed errors server-side only
- Provide user-friendly error messages
- Implement automatic retry with exponential backoff

### API Security
- Rate limiting: 10 requests/minute per session
- Input validation: Check for XSS, Injection patterns
- CORS: Restrict allowed origins
- Timeout: 8 seconds (free tier safe margin)

### Dependency Security
```bash
# Regular security audits
npm audit --audit-level=moderate
bundle audit --update

# Dependabot enabled for auto-updates
```

## 11. Cost Optimization

### API Usage Priority
1. **Gemini CLI** (OAuth 2.0) - Free ⭐ **First Choice**
2. **Local templates** - No cost
3. **Cursor/Claude Console** - Free allocation
4. **API calls** - Costs money (minimize)

### DeepSeek API Optimization
- **Context Caching**: Up to 90% cost reduction
- **Off-Peak Hours**: UTC 16:30-00:30 (50-75% discount)
- **Conversation History**: Max 10 messages
- **Response Size**: max_tokens=1500

### Monitoring
```bash
# Monitor API usage
python3 scripts/monitor_api_usage.py

# Monitor Sentry quota
./scripts/monitor_sentry_quota.sh

# Check Vercel logs
./scripts/check-vercel-logs.sh
```

## 12. Operational Efficiency

### Monitoring Tools
- **Sentry**: Error tracking, performance monitoring
- **Vercel Analytics**: Web Vitals, user behavior
- **GitHub Actions**: CI/CD status
- **Vercel Log Drains**: Centralized server logs

### Automation Scripts
| Script | Purpose | Efficiency Gain |
|--------|---------|----------------|
| `ai_improve_posts.py` | AI-based post improvement | 80% manual work reduction |
| `generate_post_images.py` | Auto image generation | 90% manual work reduction |
| `fix_links_unified.py` | Link validation & fixing | Prevents broken links |
| `verify_images_unified.py` | Image validation | Ensures all images exist |

### Error Recovery
- Automatic retry with exponential backoff
- Fallback to cached data on API failure
- Offline mode for network errors
- User-friendly error messages

## 13. UI/UX Guidelines

### Accessibility (WCAG 2.1 AA)
- ARIA attributes for all interactive elements
- Keyboard navigation support
- Screen reader compatibility
- Color contrast: 4.5:1 minimum
- Focus indicators clearly visible

### Performance Targets
- **LCP**: < 2.5s
- **FID**: < 100ms
- **CLS**: < 0.1

### User Experience
- Loading states for async operations
- Friendly error messages
- Visual feedback for actions
- Responsive design (mobile-first)

## 14. Ralph Loop - Continuous Post Improvement

OpenCode Sisyphus 모드에서 Ralph Loop를 사용하여 블로그 포스트를 자동으로 개선합니다.

### Configuration

설정 파일: `.opencode/opencode.json`

### Ralph Loop Commands

| Command | Description | Completion Promise |
|---------|-------------|-------------------|
| `/improve-posts` | RSS 수집 및 포스트 개선 | `POSTS_IMPROVED` |
| `/collect-news` | RSS 뉴스 수집 | `NEWS_COLLECTED` |
| `/validate-posts` | 포스트 품질 검증 | `POSTS_VALIDATED` |
| `/generate-images` | 이미지 생성 | `IMAGES_GENERATED` |

### Quality Score Criteria

| Criterion | Weight | Threshold |
|-----------|--------|-----------|
| Content Length | 20% | >= 3000 chars |
| Tables | 15% | >= 2 tables |
| Code Blocks | 15% | >= 1 block |
| Checklist | 10% | >= 1 item |
| Front Matter | 20% | All required |
| English Images | 10% | No Korean |
| Valid Links | 10% | No broken |

### Usage

```bash
# Basic usage
/improve-posts

# Extended collection
/improve-posts --hours=48 --max-posts=10

# High quality threshold
/improve-posts --quality-threshold=90

# Validate only
python3 scripts/validate_post_quality.py --threshold 80
```

### Documentation

자세한 내용은 `docs/scripts/README_RALPH_LOOP.md` 참조.

---

## 15. Summary

1. **Security First**: Mask sensitive info, use env vars, validate inputs
2. **English Filenames**: Images and SVG text must be English
3. **Code Quality**: Language tags, lint, type hints
4. **No Co-Authored-By**: Don't include in commits
5. **Use Unified Scripts**: `check_posts.py`, `fix_links_unified.py`, `verify_images_unified.py`
6. **Cost Optimization**: Gemini CLI first, API calls last
7. **Operational Efficiency**: Automate, monitor, recover automatically
8. **UI/UX Excellence**: Accessibility, performance, user feedback
9. **Ralph Loop**: Use `/improve-posts` for continuous content improvement
