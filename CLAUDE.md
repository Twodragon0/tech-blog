# Claude Code Instructions

Instructions for Claude Code when working on this project.

**Last updated**: 2026-01-22

## Quick Reference

| Resource | URL |
|----------|-----|
| **Production** | https://tech.2twodragon.com |
| **Backup** | https://twodragon0.github.io/tech-blog |
| **GitHub** | https://github.com/Twodragon0/tech-blog |

## Project Overview

Jekyll-based DevSecOps technical blog.

- **Topics**: DevSecOps, DevOps, FinOps, Cloud Security, Blockchain
- **Language**: Korean (content), English (code comments)
- **Hosting**: Vercel (production), GitHub Pages (backup)

## Core Principles

### 1. Security First
- **Never hardcode** API keys, passwords, tokens
- Use `os.getenv("API_KEY", "")` for sensitive data
- Mask logs with `mask_sensitive_info()` before output
- Validate with `_validate_masked_text()` before file writes
- **CSP Compliance**: Review CSP headers when adding external scripts
- **Input Validation**: Always validate and sanitize user inputs
- **Error Handling**: Never expose sensitive information in error messages
- **Dependency Security**: Run `npm audit` and `bundle audit` regularly

### 2. Cost Optimization
Priority order for AI operations:
1. **Gemini CLI** (`gemini` command) - Free with OAuth 2.0 ⭐ **최우선**
2. **Local templates** - No API cost
3. **Cursor/Claude Console** - Free allocation
4. **API calls** - Last resort (costs money)

**Cost Management Rules**:
- Use Context Caching for DeepSeek API (up to 90% cost reduction)
- Cache API responses for 7 days when possible
- Monitor API usage with `scripts/monitor_api_usage.py`
- Set rate limits to prevent unexpected costs
- Use off-peak hours for DeepSeek API (50-75% discount)

### 3. Operational Efficiency
- **Automation First**: Use scripts instead of manual work
- **Monitoring**: Check Sentry and Vercel Analytics regularly
- **Error Recovery**: Implement automatic retry with exponential backoff
- **Logging**: Use structured logging with context
- **Performance**: Monitor Core Web Vitals (LCP, FID, CLS)

### 4. UI/UX Excellence
- **Accessibility**: WCAG 2.1 AA compliance required
- **Responsive Design**: Mobile-first approach
- **Performance**: Target LCP < 2.5s, FID < 100ms, CLS < 0.1
- **User Feedback**: Provide loading states and error messages
- **Dark Mode**: Support system preference + manual toggle

### 5. Commit Rules
- **No `Co-Authored-By: Claude`** in commit messages
- Concise messages in Korean or English
- Use conventional commits: `fix:`, `feat:`, `docs:`, `refactor:`

```bash
git commit -m "fix: 보안 경고 수정"
git commit -m "feat: Add new feature"
git commit -m "docs: Update SPEC.md with security improvements"
```

## File Structure

```
tech-blog/
├── _posts/              # Blog posts (YYYY-MM-DD-Title.md)
├── _layouts/            # Jekyll layouts
├── _includes/           # Reusable components
├── assets/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript
│   └── images/          # Images (English filenames only!)
├── scripts/             # Python/Bash utilities
│   └── docs/            # Script documentation
├── docs/                # Project documentation
│   ├── guides/          # Content creation guides
│   ├── optimization/    # Performance guides
│   ├── setup/           # Setup guides
│   └── troubleshooting/ # Troubleshooting guides
├── api/                 # Vercel Serverless Functions
├── .cursorrules         # Detailed Cursor AI rules
├── AGENTS.md            # AI agent coding guidelines
├── CLAUDE.md            # This file
└── SECURITY.md          # Security policy
```

## Post Writing Rules

### Filename Format
- Format: `YYYY-MM-DD-English_Title.md`
- **No Korean in filenames**

### Front Matter
```yaml
---
layout: post
title: "제목 (Korean OK)"
date: YYYY-MM-DD HH:MM:SS +0900
category: [security|devsecops|devops|cloud|kubernetes|finops|incident]
categories: [category1, category2]
tags: [tag1, tag2]
excerpt: "Summary (150-200 chars)"
image: /assets/images/YYYY-MM-DD-English_Title.svg
---
```

### Code Blocks
- **Always** include language tags: ```python, ```bash, ```yaml
- **>10 lines**: Replace with GitHub link + HTML comment for original
- **3-10 lines**: Keep with reference link
- **<3 lines**: Keep original
- **Mask** sensitive data: `YOUR_API_KEY`, `***MASKED***`

## Image Rules

### Filenames
- **English only** - No Korean characters
- Format: `YYYY-MM-DD-English_Title.svg`
- Convert script: `python3 scripts/rename_images_to_english.py`

### SVG Text
- **English only** in SVG text elements
- No special chars: `·`, `•`, `—`, `"`, `'`
- UTF-8 encoding required

## Common Commands

```bash
# Local development
bundle exec jekyll serve --livereload

# Convert image filenames to English
python3 scripts/rename_images_to_english.py --yes

# Generate post images
python3 scripts/generate_post_images.py --all --force

# Validate posts
python3 scripts/check_posts.py

# Fix links
python3 scripts/fix_links_unified.py --fix

# Verify images
python3 scripts/verify_images_unified.py --all
```

## Implementation Status

| Feature | Score | Status | Next Steps |
|---------|-------|--------|------------|
| **Security** | 9/10 | CSP, HSTS, Sentry (Free Tier optimized), Masking, Input Validation | Periodic CSP review, dependency updates |
| **Performance** | 9/10 | Service Worker, Caching, Lazy Loading, Critical CSS | Image optimization, bundle size reduction |
| **SEO** | 10/10 | Open Graph, Twitter Cards, JSON-LD, Sitemap, RSS | Maintain current level |
| **User Features** | 9/10 | Giscus comments, DeepSeek chatbot, Dark/Light mode, Search | Accessibility improvements |
| **Cost Optimization** | 9/10 | API caching, rate limiting, free tier optimization | Monitor usage, optimize further |
| **Operational Efficiency** | 8/10 | Automation scripts, CI/CD, monitoring | Enhanced error recovery |

## Related Documentation

| Document | Purpose |
|----------|---------|
| `.cursorrules` | Detailed Cursor AI rules (comprehensive) |
| `AGENTS.md` | AI agent coding guidelines |
| `SECURITY.md` | Security policy |
| `docs/` | All project documentation |
| `scripts/README.md` | Script documentation |

## Quick Checklist

### Pre-Commit Checklist
- [ ] No hardcoded secrets
- [ ] Image filenames are English only
- [ ] SVG text is English only
- [ ] Code blocks have language tags
- [ ] Links point to real resources (no example.com)
- [ ] Front matter follows format
- [ ] `lsp_diagnostics` clean on changed files

### Security Checklist
- [ ] Input validation implemented
- [ ] Error messages don't expose sensitive info
- [ ] CSP headers reviewed (if adding external scripts)
- [ ] Dependencies audited (`npm audit`, `bundle audit`)
- [ ] API keys use environment variables
- [ ] Logs mask sensitive information

### Performance Checklist
- [ ] Images optimized and lazy-loaded
- [ ] CSS/JS minified for production
- [ ] Service Worker updated (if changed)
- [ ] Cache headers appropriate
- [ ] Core Web Vitals checked

### Cost Optimization Checklist
- [ ] API calls minimized (use Gemini CLI first)
- [ ] Caching implemented where possible
- [ ] Rate limiting configured
- [ ] Free tier limits respected (Sentry, Vercel)

### UI/UX Checklist
- [ ] Accessibility: ARIA attributes, keyboard navigation
- [ ] Responsive: Mobile, tablet, desktop tested
- [ ] Dark mode: Works correctly
- [ ] Loading states: Provided for async operations
- [ ] Error handling: User-friendly messages
