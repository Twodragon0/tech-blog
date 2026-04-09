# AGENTS.md - AI Agent Coding Guidelines

**Last updated**: 2026-04-08

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

### Git Hooks Setup
```bash
bash scripts/install-hooks.sh                      # Install pre-commit hooks (SVG quality gate + pytest)
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

# Tests (287 tests, ~0.19s — API calls disabled in conftest.py)
pytest scripts/tests/
pytest scripts/tests/ --cov=scripts --cov-fail-under=40
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
from scripts.lib.security import mask_sensitive_info
from scripts.lib.logging_utils import safe_log
```

- **Naming**: `snake_case` (vars/funcs), `PascalCase` (classes), `UPPER_CASE` (constants)
- **Docstrings**: Google-style
- **Type hints**: Always use them
- **File size**: 200-400 lines typical, 800 max

### Security Patterns
```python
# Log with masking (scripts/lib/security.py)
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
├── _posts/              # 132+ blog posts (YYYY-MM-DD-Title.md)
├── _layouts/            # Jekyll layouts (default.html, page.html, post.html, reusable/)
├── _includes/           # Reusable components (see §3a below)
├── _data/               # Jekyll data (collected_news.json, etc.)
├── _sass/               # SCSS source files
├── _drafts/             # Draft posts (not published)
├── assets/
│   ├── css/             # Stylesheets
│   ├── js/              # JavaScript
│   ├── images/          # Images (English filenames ONLY)
│   └── audio/           # Audio files
├── scripts/             # Python/Bash utilities (69 Python + 20+ shell)
│   ├── lib/             # Shared libraries (security.py, logging_utils.py)
│   ├── news/            # News collection modules (analyzer, loader, generator, etc.)
│   ├── tests/           # pytest test suite (287 tests)
│   ├── _archive/        # Deprecated scripts (do not use)
│   └── README.md        # Script guide
├── docs/                # Project documentation
│   ├── guides/          # Content creation guides
│   ├── optimization/    # Performance optimization
│   ├── setup/           # Setup and configuration
│   ├── troubleshooting/ # Troubleshooting guides
│   ├── audits/          # Security/performance audits
│   ├── pdca/            # PDCA cycle records
│   └── pipeline/        # Pipeline documentation
├── api/                 # Vercel Serverless Functions
│   ├── chat.js          # DeepSeek chat endpoint (POST /api/chat)
│   ├── search.js        # Search endpoint
│   ├── markdown.js      # Markdown rendering endpoint
│   └── lib/
│       └── ratelimit.js # Rate limiting (10 req/min per session)
├── .github/
│   └── workflows/       # 21 GitHub Actions workflows (see §9)
├── .claude/
│   ├── agents/          # 9 project sub-agents
│   ├── commands/        # Custom skills (/new-post, /validate-post, etc.)
│   └── rules/           # Coding style, security, testing, performance rules
├── .opencode/           # OpenCode Sisyphus + Ralph Loop config
│   ├── agents/          # OpenCode agents (lead, primary, explore, validate, code)
│   ├── skills/          # Reusable skills (security, validation, cost, governance)
│   └── opencode.json    # Runtime config
├── notes/               # Per-session learnings, decisions, issues, per-pr/
├── data/                # Additional data files
├── certifications/      # Certification content
├── prisma/              # Prisma DB schema (if used)
├── .cursorrules         # Cursor AI rules (detailed)
├── CLAUDE.md            # Claude Code instructions
├── AGENTS.md            # This file
├── SECURITY.md          # Security policy
├── vercel.json          # Vercel deployment config
├── pyproject.toml       # Python tooling config (ruff, mypy, pytest)
└── package.json         # Node.js dependencies
```

### 3a. _includes/ Components

| File | Purpose |
|------|---------|
| `head.html` | HTML `<head>` (SEO, OG tags, JSON-LD) |
| `header.html` | Site navigation |
| `footer.html` | Site footer |
| `giscus.html` | Giscus comments integration |
| `chat-widget.html` | DeepSeek chatbot widget |
| `ai-summary-card.html` | AI-generated post summary card |
| `news-card.html` | News item card component |
| `news-spotlight-section.html` | News spotlight layout |
| `post-card.html` | Post listing card |
| `post-navigation.html` | Prev/next post navigation |
| `share-buttons.html` | SNS share buttons |
| `subscribe-float.html` | Buttondown newsletter subscribe float |
| `toc.html` | Table of contents |
| `sentry.html` | Sentry error tracking init |
| `performance-monitor.html` | Core Web Vitals monitor |
| `mermaid.html` | Mermaid.js diagram renderer |
| `series-nav.html` | Series navigation |
| `audio-player.html` | Audio player component |
| `error-handler.html` | Client-side error handler |
| `adsense.html` | Google AdSense integration |

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
- `security` - Security-related content
- `devsecops` - DevSecOps practices
- `devops` - DevOps tooling and practices
- `cloud` - Cloud services (AWS, GCP, Azure)
- `kubernetes` - Kubernetes and container orchestration
- `finops` - FinOps and cloud cost optimization
- `incident` - Incident analysis and post-mortems

### Content Rules
- **NO FAQ sections**: Do not add FAQ (자주 묻는 질문) or `schema_type: FAQPage`
- **No FAQPage JSON-LD**: SEO does not require FAQ structured data here
- Focus on technical depth, actionable content, and real examples

---

## 5. Critical Rules

### Images
| Rule | Requirement |
|------|-------------|
| Filename | **English only** - No Korean characters |
| Format | `YYYY-MM-DD-English_Title` (svg, png, jpg) |
| SVG text | **English only** |
| SVG special chars | No `·`, `•`, `—`, `"`, `'` — use ASCII equivalents |
| Encoding | UTF-8 required |
| Conversion | `python3 scripts/rename_images_to_english.py --yes` |

### Code Blocks
| Length | Action |
|--------|--------|
| >10 lines | Replace with GitHub link + HTML comment |
| 3-10 lines | Keep with reference link |
| <3 lines | Keep original |
- Always include language tags: ` ```python `, ` ```bash `, ` ```yaml `

### Security
- **Never** hardcode API keys, passwords, tokens
- **Always** use `os.getenv("API_KEY", "")`
- **Always** mask sensitive data in logs via `scripts/lib/security.py`
- **Never** commit secrets or `.env` files

### Commits
- **No** `Co-Authored-By: Claude` in messages
- Korean or English, concise
- Conventional format: `fix:`, `feat:`, `docs:`, `refactor:`, `perf:`, `ci:`

### Git Pull Upstream Recovery
- If `git pull` fails with `no such ref was fetched`, reset upstream:
  - `git branch --set-upstream-to=origin/main <current-branch>`
- When local changes block pull/rebase, use safe sequence:
  - `git stash push -u -m "temp-before-pull"`
  - `git pull --rebase --autostash`
  - If conflict too large: `git rebase --abort` then `git stash pop`

### Auto-Yes (project / tmp)
- **In-repo or tmp**: Treat confirmations as **yes**
- **Scripts**: Use `--yes` or `-y` flags
- **Env**: `TECH_BLOG_AUTO_YES=1` or `CI=1` skips confirmation in supported scripts

---

## 6. Quality Checklist

### Pre-commit
- [ ] No hardcoded secrets
- [ ] Image filenames are English only
- [ ] SVG files contain only English text
- [ ] Links point to real resources (no example.com)
- [ ] Code blocks have language tags
- [ ] Front matter follows format
- [ ] No FAQ sections added
- [ ] `pytest scripts/tests/` passes (pre-commit hook auto-runs on `auto_publish_news.py` changes)

### Testing
- [ ] Unit tests for utilities in `scripts/tests/`
- [ ] File operations use temp directories
- [ ] Error handling tests included
- [ ] Security validation tests included
- [ ] Coverage >= 40% for `auto_publish_news.py`

---

## 7. Implementation Status

| Feature | Score | Implementation | Next Steps |
|---------|-------|----------------|------------|
| **Security** | 9/10 | CSP, HSTS, Sentry (Free Tier), Masking, Input Validation | Periodic CSP review, dependency updates |
| **Performance** | 9/10 | Service Worker, Caching, Lazy Loading, Critical CSS | Image optimization, bundle size reduction |
| **SEO** | 10/10 | OG, Twitter Cards, JSON-LD, Sitemap, RSS | Maintain current level |
| **User Features** | 9/10 | Giscus, DeepSeek chatbot, Dark/Light mode, Search | Accessibility improvements |
| **Cost Optimization** | 9/10 | API caching, rate limiting, free tier optimization | Monitor usage, optimize further |
| **Operational Efficiency** | 8/10 | 21 GHA workflows, automation scripts, monitoring | Enhanced error recovery |

---

## 8. Daily News Collection System

Automated tech/security news collection and blog draft generation.

### Workflow
```
RSS Feeds (15+) → collect_tech_news.py → _data/collected_news.json
                                              ↓
_posts/ ← Manual Review ← generate_news_draft.py → _drafts/
                                              ↓
                            auto_publish_news.py (template-based)
```

### News Modules (`scripts/news/`)
| Module | Purpose |
|--------|---------|
| `analyzer.py` | Article analysis and scoring |
| `loader.py` | Feed loading and parsing |
| `content_generator.py` | Post content generation |
| `enhancer.py` | Content enhancement |
| `config.py` | News collection config |
| `svg_generator.py` | SVG image generation for news posts |

### Usage
```bash
python3 scripts/collect_tech_news.py --hours 24
python3 scripts/generate_news_draft.py --use-ai --max-posts 10
python3 scripts/auto_publish_news.py   # Template-based auto-publish
```

### Template Branch Rules (`auto_publish_news.py`)
- **Add test when adding branch**: `scripts/tests/test_news_templates.py`
- **Branch order = priority**: Specific keywords (istio, cosign) before general (network, image)
- **Avoid over-matching**: Use specific terms like `admission controller`, `pod security`
- **Pre-commit hook**: Auto-runs pytest on `auto_publish_news.py` or `scripts/tests/` changes
- **Coverage target**: 40%+ for `auto_publish_news.py` (`--cov-fail-under=40` enforced in CI)
- **Test count**: 287 tests / ~0.19s (API calls disabled via conftest.py, lazy import applied)

---

## 9. GitHub Actions Workflows (21 total)

| Workflow | File | Purpose |
|----------|------|---------|
| **AI Blogwatcher** | `ai-blogwatcher.yml` | Primary daily news auto-publish (replaces daily-news schedule) |
| **AI Ops On-Demand** | `ai-ops-on-demand.yml` | Manual AI operations trigger |
| **Buttondown Notify** | `buttondown-notify.yml` | Newsletter notification on new posts |
| **Check SVG** | `check-svg.yml` | SVG quality and English-text validation |
| **Daily News** | `daily-news.yml` | DEPRECATED schedule; manual dispatch only |
| **Deploy Pages** | `deploy-pages.yml` | GitHub Pages deployment (backup) |
| **Generate Images** | `generate-images.yml` | Auto-generate post SVG images |
| **Jekyll Build** | `jekyll.yml` | Jekyll build and test |
| **Lighthouse** | `lighthouse.yml` | Core Web Vitals / Lighthouse audit |
| **Monitoring** | `monitoring.yml` | Site uptime and health monitoring |
| **Monthly Quality** | `monthly-quality-report.yml` | Monthly post quality report |
| **Ops Multi-Agent Loop** | `ops-multi-agent-loop.yml` | Multi-agent operations loop |
| **Ops Priority Loop** | `ops-priority-loop.yml` | Priority task operations loop |
| **Security Audit** | `security-audit.yml` | Dependency and CSP security audit |
| **Sentry Healthcheck** | `sentry-healthcheck.yml` | Sentry quota and health check |
| **Sentry Release** | `sentry-release.yml` | Sentry release tracking on deploy |
| **Slack Category Digest** | `slack-category-digest.yml` | Category digest to Slack |
| **Slack Post Notify** | `slack-post-notify.yml` | New post notification to Slack |
| **SNS Share** | `sns-share.yml` | Auto-share new posts to SNS on push |
| **Ultrawork Loop** | `ultrawork-loop.yml` | Ultrawork automation loop |
| **Vercel Deploy** | `vercel-deploy.yml` | Production Vercel deployment |

---

## 10. Security Best Practices

### Input Validation
- Always validate user inputs (XSS, Injection patterns)
- Sanitize HTML content before rendering
- Validate URLs before use
- API endpoints in `api/` use rate limiting via `api/lib/ratelimit.js`

### Error Handling
- Never expose sensitive info in error messages
- Log detailed errors server-side only
- Provide user-friendly error messages
- Implement automatic retry with exponential backoff

### API Security (Vercel Serverless)
- Rate limiting: 10 requests/minute per session
- Input validation: Check for XSS, Injection patterns
- CORS: Restrict allowed origins
- Timeout: 8 seconds (free tier safe margin)
- API keys: Server-side only via Vercel environment variables

### Dependency Security
```bash
# Regular security audits
npm audit --audit-level=moderate
bundle audit --update

# Dependabot: enabled in repo for auto dependency updates
```

---

## 11. Cost Optimization

### API Usage Priority
1. **Gemini CLI** (OAuth 2.0) - Free ⭐ **First Choice**
2. **Local templates** - No cost
3. **Cursor/Claude Console** - Free allocation
4. **API calls** - Costs money (minimize)

### DeepSeek API Optimization (`api/chat.js`)
- **Context Caching**: Up to 90% cost reduction
- **Off-Peak Hours**: UTC 16:30-00:30 (50-75% discount)
- **Conversation History**: Max 10 messages
- **Response Size**: `max_tokens=1500`

### Monitoring
```bash
python3 scripts/monitor_api_usage.py   # Monitor API usage
./scripts/monitor_sentry_quota.sh      # Monitor Sentry quota
./scripts/check-vercel-logs.sh         # Check Vercel logs
```

---

## 12. Operational Efficiency

### Monitoring Stack
- **Sentry**: Error tracking, performance monitoring (Free Tier optimized)
- **Vercel Analytics**: Web Vitals, user behavior
- **GitHub Actions**: CI/CD status (21 workflows)
- **Vercel Log Drains**: Centralized server logs

### Key Automation Scripts

| Script | Purpose |
|--------|---------|
| `ai_improve_posts.py` | AI-based post improvement |
| `smart_improve_posts.py` | Smart post improvement with scoring |
| `continuous_improve_posts.py` | Continuous improvement loop |
| `generate_post_images.py` | Auto SVG image generation |
| `fix_links_unified.py` | Link validation & fixing |
| `verify_images_unified.py` | Image existence validation |
| `check_posts.py` | Front matter & post structure validation |
| `auto_publish_news.py` | Template-based news post publishing |
| `collect_tech_news.py` | RSS feed aggregation |
| `generate_news_draft.py` | AI-assisted draft generation |
| `share_sns.py` | SNS sharing (Twitter/X, LinkedIn) |
| `buttondown_notify.py` | Buttondown newsletter notification |
| `validate_post_quality.py` | Post quality scoring |
| `rename_images_to_english.py` | Korean→English image filename conversion |
| `setup-worktrees.sh` | Git worktree parallel session setup |

### Scripts Library (`scripts/lib/`)
| Module | Purpose |
|--------|---------|
| `security.py` | `mask_sensitive_info()`, `_validate_masked_text()` |
| `logging_utils.py` | Structured logging with context |

---

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
- Dark/Light mode toggle + system preference

---

## 14. Ralph Loop - Continuous Post Improvement

OpenCode Sisyphus mode with Ralph Loop for automated blog post improvement.

### Configuration

Config file: `.opencode/opencode.json`

### Model Selection Strategy

| Task Type | Model | Reason |
|-----------|-------|--------|
| Content/code generation | Opus 4.6 | High-quality output required |
| Code writing/refactoring | Opus 4.6 | Complex logic, best practices |
| Validation/analysis | Sonnet 4.6 | Rule-based, cost-efficient |
| Read-only exploration | Sonnet 4.6 | Analysis only, no generation |
| Security audit | Sonnet 4.6 | Pattern matching, cost-efficient |

### Ralph Loop Commands

| Command | Model | Description | Completion Promise |
|---------|-------|-------------|-------------------|
| `/improve-posts` | Opus 4.6 | RSS collection and post improvement | `POSTS_IMPROVED` |
| `/collect-news` | Sonnet 4.6 | RSS news collection (cost-optimized) | `NEWS_COLLECTED` |
| `/validate-posts` | Sonnet 4.6 | Post quality validation | `POSTS_VALIDATED` |
| `/generate-images` | Opus 4.6 | Image generation | `IMAGES_GENERATED` |
| `/security-audit` | Sonnet 4.6 | Security audit | `SECURITY_AUDIT_COMPLETE` |
| `/write-code` | Opus 4.6 | Code writing | `CODE_WRITTEN` |
| `/refactor` | Opus 4.6 | Code refactoring | `CODE_REFACTORED` |
| `/fix-bugs` | Opus 4.6 | Bug and security issue fixes | `BUGS_FIXED` |
| `/cost-optimize` | Sonnet 4.6 | API usage optimization analysis | `COST_OPTIMIZED` |

### Quality Score Criteria

| Criterion | Weight | Threshold |
|-----------|--------|-----------|
| Content Length | 20% | >= 3000 chars |
| Tables | 15% | >= 2 tables |
| Code Blocks | 15% | >= 1 block |
| Checklist | 10% | >= 1 item |
| Front Matter | 20% | All required fields |
| English Images | 10% | No Korean filenames |
| Valid Links | 10% | No broken links |

### Usage
```bash
# Start OpenCode in Sisyphus mode
opencode sisyphus

# Basic usage
/improve-posts

# Extended collection
/improve-posts --hours=48 --max-posts=10

# High-quality threshold
/improve-posts --quality-threshold=90

# Validation only
/validate-posts

# Security audit
/security-audit
```

### Documentation
- `.opencode/README.md` - OpenCode setup and usage
- `.opencode/agents/` - Agent definitions (lead, primary, explore, validate, code)
- `.opencode/skills/` - Skills (cost-audit, opencode-governance, post-validation, security-review)

---

## 15. Summary

1. **Security First**: Mask sensitive info (`scripts/lib/security.py`), use env vars, validate inputs
2. **English Filenames**: Images and SVG text must be English only
3. **Code Quality**: Language tags, ruff lint, mypy type hints
4. **No Co-Authored-By**: Do not include in commits
5. **Use Canonical Scripts**: `check_posts.py`, `fix_links_unified.py`, `verify_images_unified.py`
6. **Cost Optimization**:
   - Gemini CLI first (free), API calls last
   - Smart model selection (Opus 4.6 for generation, Sonnet 4.6 for validation)
   - Cache first (7-day TTL), local scripts preferred
7. **Operational Efficiency**: 21 GHA workflows, automate monitoring, recover automatically
8. **UI/UX Excellence**: WCAG 2.1 AA, mobile-first, dark mode, Core Web Vitals targets
9. **OpenCode Integration**:
   - Use Sisyphus mode with Ralph Loop
   - `/improve-posts` for continuous content improvement
   - Model selection based on task type (cost optimization)
10. **No FAQ Sections**: Never add FAQ or FAQPage schema to posts

---

## 16. Project Agents (`.claude/agents/`)

| Agent File | Model | Role |
|-----------|-------|------|
| `blog-lead.md` | opus | Project lead, content strategy, task distribution |
| `architect.md` | opus | Jekyll structure design, script architecture |
| `post-researcher.md` | sonnet | Tech blog topic research, trend analysis |
| `post-quality-reviewer.md` | haiku | Post quality validation, markdown linting |
| `post-validator.md` | haiku | Post validity check (front matter, links, images) |
| `security-auditor.md` | sonnet | Security audit, CSP/HSTS, dependency checks |
| `seo-optimizer.md` | haiku | SEO metadata, Open Graph, JSON-LD optimization |
| `performance-analyst.md` | haiku | Core Web Vitals, caching, loading performance |
| `test-engineer.md` | sonnet | Script tests, template branch tests, CI validation |

### Custom Commands (`.claude/commands/`)

| Command | Purpose |
|---------|---------|
| `new-post.md` | `/new-post` — Title/category input → file auto-creation |
| `validate-post.md` | `/validate-post` — Front matter, image, code block validation |
| `techdebt.md` | `/techdebt` — Duplicate code, unused resources, TODO detection |
| `fix-ci.md` | `/fix-ci` — Jekyll build error auto-diagnosis/fix |
| `daily-review.md` | `/daily-review` — Git status, SEO, image comprehensive check |
| `team-create-post.md` | `/team-create-post` — researcher→writer→executor→qa pipeline |
| `team-audit.md` | `/team-audit` — explore+security→architect→executor audit |
| `team-improve.md` | `/team-improve` — explore→critic→executor→reviewer improvement |
| `team-optimize.md` | `/team-optimize` — explore+researcher→analyst→executor optimization |

### Multi-Agent Workflow Patterns

- **New Post**: post-researcher → blog-lead → post-quality-reviewer → post-validator → seo-optimizer
- **Security Audit**: security-auditor → architect → test-engineer
- **Performance**: performance-analyst → architect → test-engineer → performance-analyst
- **Script Dev**: architect → blog-lead → test-engineer → post-validator

---

## 17. Related Documentation

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Claude Code workflow instructions (Plan Mode, Boris Cherny tips) |
| `.cursorrules` | Detailed Cursor AI rules |
| `SECURITY.md` | Security policy |
| `docs/README.md` | Documentation index |
| `scripts/README.md` | Script guide |
| `.opencode/README.md` | OpenCode Sisyphus + Ralph Loop guide |
| `notes/learnings.md` | Technical discoveries and patterns |
| `notes/decisions.md` | Architecture decision records |
| `notes/issues.md` | Known issues and workarounds |
| `.claude/rules/` | Coding style, security, testing, performance rules |
