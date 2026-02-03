# Claude Code Instructions

Instructions for Claude Code when working on this project.

**Last updated**: 2026-02-03

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

## Workflow Strategy (Boris Cherny Tips)

### Plan Mode First (TIP 2)
- **복잡한 작업은 반드시 Plan Mode부터 시작**
- 에너지를 "계획"에 집중하면 구현 1-shot 성공률이 올라감
- 문제가 꼬이면 즉시 Plan Mode로 돌아가 재계획 (밀어붙이지 않기)
- 빌드뿐 아니라 **검증 단계**도 Plan에 포함시킬 것

### Parallel Worktrees (TIP 1)
- 3~5개 git worktree를 동시에 운영하고 각각 별도 Claude 세션 실행
- `bash scripts/setup-worktrees.sh setup` 으로 세팅
- alias: `za`, `zb`, `zc` (작업용), `zd` (분석 전용), `zm` (메인)
- **탭 1개 = 작업 1개 = worktree 1개** 원칙

### Subagent 활용 (TIP 8)
- 더 많은 compute가 필요하면 "use subagents" 를 요청에 추가
- 세부 작업을 subagent에게 넘겨 메인 에이전트 컨텍스트를 깨끗하게 유지

### Strict Verification (TIP 6)
- Claude를 단순 실행자가 아니라 **리뷰어/검증자**로 활용
- 변경사항은 반드시 테스트 통과 후 PR 생성
- 어설픈 수정 시: "지금까지 배운 걸 바탕으로 폐기하고 우아한 해결책으로 다시 구현해"
- 일을 넘기기 전에 스펙을 구체적으로 써서 모호성 제거

### Learning Feedback Loop (TIP 3)
- 교정/수정 후 마지막에: **"CLAUDE.md를 업데이트해서 다음엔 같은 실수 하지 않게 해"**
- `notes/` 디렉토리에 작업별 학습 내용 기록
- PR마다 `notes/per-pr/PR-{number}.md` 업데이트
- CLAUDE.md가 notes를 참조하도록 유지

### Bug Fix Protocol (TIP 5)
- 버그 수정은 Claude에게 맡기되 **micromanage 하지 말 것**
- "실패하는 CI 테스트 고쳐" 한 마디로 충분
- 어떻게 고칠지 간섭하지 않기

## Custom Skills (TIP 4)

하루에 1번 이상 하는 작업은 스킬로 만들어 재사용합니다.

| Skill | Command | Purpose |
|-------|---------|---------|
| 새 포스트 생성 | `/new-post` | 제목/카테고리 입력 → 파일 자동 생성 |
| 포스트 검증 | `/validate-post` | Front matter, 이미지, 코드 블록 검증 |
| 기술 부채 탐지 | `/techdebt` | 중복 코드, 미사용 리소스, TODO 탐지 |
| CI 수정 | `/fix-ci` | Jekyll 빌드 에러 자동 진단/수정 |
| 일일 점검 | `/daily-review` | Git 상태, SEO, 이미지 종합 점검 |

스킬 파일 위치: `.claude/commands/`

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
├── .claude/
│   └── commands/        # Custom skills (/new-post, /validate-post, etc.)
├── notes/               # 작업별 학습/결정/이슈 기록 (TIP 3)
│   ├── learnings.md     # 기술적 발견, 패턴
│   ├── decisions.md     # 아키텍처 결정 기록
│   ├── issues.md        # 알려진 이슈/해결법
│   └── per-pr/          # PR별 노트
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
# Worktree 병렬 세션 (TIP 1)
bash scripts/setup-worktrees.sh setup    # 워크트리 생성
bash scripts/setup-worktrees.sh aliases  # .zshrc alias 출력
bash scripts/setup-worktrees.sh status   # 상태 확인

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

## OpenCode Integration

### OpenCode Sisyphus Mode with Ralph Loop

This project uses OpenCode with Sisyphus mode and Ralph Loop for automated content improvement.

#### Quick Start
```bash
# Start OpenCode in Sisyphus mode
opencode sisyphus

# Run Ralph Loop commands
/improve-posts
/collect-news
/validate-posts
/generate-images
```

#### Model Selection Strategy
- **High-Quality Tasks** (Opus 4.5): Content generation, code writing, image generation
- **Cost-Efficient Tasks** (Sonnet 4): Validation, analysis, read-only operations

#### Cost Optimization
1. **Cache First**: Check `_data/collected_news.json` (7-day TTL) before API calls
2. **Local Scripts**: Use `python3 scripts/*.py` (no API cost)
3. **Gemini CLI**: Free OAuth 2.0 (first choice)
4. **Batch Operations**: Group operations to reduce API calls

#### Security
- All agents follow principle of least privilege
- Sensitive data automatically masked in logs
- Input validation for all commands
- Security audit command available: `/security-audit`

See `.opencode/README.md` for detailed documentation.

## Related Documentation

| Document | Purpose |
|----------|---------|
| `.cursorrules` | Detailed Cursor AI rules (comprehensive) |
| `AGENTS.md` | AI agent coding guidelines |
| `.opencode/README.md` | OpenCode configuration and usage |
| `SECURITY.md` | Security policy |
| `notes/` | 작업별 학습/결정/이슈 기록 (TIP 3) |
| `.claude/commands/` | Custom skills for Claude Code (TIP 4) |
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
- [ ] Caching implemented where possible (7-day TTL)
- [ ] Rate limiting configured
- [ ] Free tier limits respected (Sentry, Vercel)
- [ ] OpenCode model selection optimized (Opus 4.5 for generation, Sonnet 4 for validation)
- [ ] Local scripts used before API calls

### UI/UX Checklist
- [ ] Accessibility: ARIA attributes, keyboard navigation
- [ ] Responsive: Mobile, tablet, desktop tested
- [ ] Dark mode: Works correctly
- [ ] Loading states: Provided for async operations
- [ ] Error handling: User-friendly messages
