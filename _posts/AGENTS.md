<!-- Parent: ../AGENTS.md -->
# _posts/ — AI Agent Guidelines

**Last updated**: 2026-04-08

This directory contains all published blog posts as Markdown files.

## File Naming

```
YYYY-MM-DD-English_Title_With_Underscores.md
```

- Date prefix is mandatory (Jekyll permalink depends on it)
- Title portion must be English only — no Korean characters in filenames
- Use underscores between words, not spaces or hyphens in the title segment

## Required Front Matter

```yaml
---
layout: post
title: "Title (Korean allowed)"
date: YYYY-MM-DD HH:MM:SS +0900
category: security|devsecops|devops|cloud|kubernetes|finops|incident
categories: [primary-category]
tags: [tag1, tag2, tag3]
excerpt: "Summary 150-200 chars for SEO"
image: /assets/images/YYYY-MM-DD-English_Title.svg
---
```

All six fields (`layout`, `title`, `date`, `categories`, `tags`, `excerpt`) are required.
`image` is required; generate with `python3 scripts/generate_post_images.py`.

## Content Rules

- Minimum 3000 characters for quality threshold
- At least 2 tables and 1 code block per post
- Code blocks must have language tags: ` ```python `, ` ```bash `, ` ```yaml `
- Code blocks over 10 lines: replace with GitHub link + HTML comment
- No FAQ sections or `schema_type: FAQPage` — not used here
- Links must point to real resources (no `example.com` placeholders)

## Valid Categories

| Category | Topic |
|----------|-------|
| `security` | Vulnerability, incident response, security architecture |
| `devsecops` | CI/CD security, SAST/DAST, container security |
| `devops` | Infrastructure automation, Kubernetes, CI/CD, monitoring |
| `cloud` | AWS, GCP, Azure architecture and security |
| `kubernetes` | Kubernetes and container orchestration |
| `finops` | Cloud cost optimization, resource governance |
| `incident` | Security incident analysis, post-mortems |

## Validation

```bash
python3 scripts/check_posts.py           # Validate all posts
python3 scripts/fix_links_unified.py --fix   # Fix broken links
python3 scripts/verify_images_unified.py --all  # Verify images exist
```

## Drafts

Draft posts live in `../_drafts/` and are not published until moved here.
