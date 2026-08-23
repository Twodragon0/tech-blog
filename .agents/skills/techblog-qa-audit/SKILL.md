---
name: techblog-qa-audit
description: >-
  Comprehensive quality assurance, security, link integrity, and test suite audit skill.
  Combines AGY local test runners, OMC verifier/security-reviewer, and CCG quality checks.
---

# Tech Blog Comprehensive QA & Audit Runbook (AGY + OMC + CCG)

Use this skill when auditing blog posts, scripts, images, links, SEO tags, or security controls before merging or deploying to production.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Full QA & Security Audit Pipeline                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Tier 1: Posts   │       │  Tier 2: Code    │       │  Tier 3: Sec/Ops │
│  - Front matter  │       │  - Pytest suite  │       │  - Secret Mask   │
│  - English SVGs  │       │  - Ruff & Mypy   │       │  - Sentry Quota  │
│  - Links & TOC   │       │  - Coverage >=40%│       │  - CSP & Headers │
└────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       Master Verification Gate                         │
│                    100% Green / Zero Regression                        │
└────────────────────────────────────────────────────────────────────────┘
```

## Step-by-Step Audit Execution

### 1. Blog Post Structural & Content Audit
```bash
# 1. Check all post front matters and structures
python3 scripts/check_posts.py

# 2. Check and fix broken links
python3 scripts/fix_links_unified.py --fix

# 3. Verify all image references and ensure English filenames
python3 scripts/verify_images_unified.py --all

# 4. Check KST midnight timezone compliance (HH >= 09:00 +0900)
python3 scripts/check_kst_midnight.py
```

### 2. Code Quality & Test Suite Audit
```bash
# 1. Run Python pytest suite
.venv/bin/pytest scripts/tests/

# 2. Lint & format checks
ruff check scripts/
mypy scripts/ --ignore-missing-imports
```

### 3. Security & Operational Health Audit
```bash
# 1. Dependency security check
npm audit --audit-level=moderate
bundle audit --update

# 2. Sentry error tracking & quota monitor
./scripts/monitor_sentry_quota.sh
node scripts/verify_sentry_logs.js
```

### 4. Quality Rules Checklist
- [ ] No hardcoded secrets or API tokens (always use `os.getenv` + `scripts.lib.security.mask_sensitive_info`).
- [ ] All image files and SVG text are in **English only**.
- [ ] No FAQ sections (`자주 묻는 질문`) or `FAQPage` JSON-LD schema added.
- [ ] Post dates have `HH >= 09:00:00 +0900` or explicit `redirect_from`.
- [ ] Code blocks contain language tags (` ```bash `, ` ```yaml `, ` ```python `).
- [ ] Commits follow Conventional Commits without `Co-Authored-By: Claude`.
