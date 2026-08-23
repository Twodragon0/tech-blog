---
name: techblog-post-create
description: >-
  Standard end-to-end procedure for creating a high-quality DevSecOps/Cloud technical blog post
  using AGY local execution, OMC multi-agent writing, and CCG tri-model verification.
---

# Tech Blog Post Creation Runbook (AGY + OMC + CCG)

Follow this procedure when creating a new post for `tech.2twodragon.com`.

## 1. File Naming & Location
- Location: `_posts/YYYY-MM-DD-English_Title.md`
- Filename must contain **ONLY English characters, numbers, and hyphens/underscores**.

## 2. Front Matter Specification
```yaml
---
layout: post
title: "포스트 제목 (한국어 지원)"
date: YYYY-MM-DD 09:00:00 +0900   # HH >= 09:00 (Timezone Rule)
category: security # Choose one: security, devsecops, devops, cloud, kubernetes, finops, incident
categories: [security, cloud]
tags: [aws, kubernetes, security]
excerpt: "150~200자 내외의 요약문 작성"
image: /assets/images/YYYY-MM-DD-English_Title.svg
---
```

## 3. End-to-End Orchestration Workflow

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Phase 1: Recon │       │  Phase 2: Draft │       │  Phase 3: Audit │
│  - Gemini CLI   │  ──►  │  - Claude (OMC) │  ──►  │  - Codex & AST  │
│  - 1M+ Context  │       │  - Mermaid/Tone │       │  - Code Safety  │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                                             │
                                                             ▼
                                                    ┌─────────────────┐
                                                    │  Phase 4: Gate  │
                                                    │  - AGY Pytest   │
                                                    │  - English SVG  │
                                                    │  - Check Posts  │
                                                    └─────────────────┘
```

## 4. Post Writing Quality Standards
- **Depth**: Minimum 3,000+ characters of substantial technical content.
- **Visuals**: Include at least one Mermaid architecture diagram or table comparison.
- **Code Blocks**: Always include language tags (`python`, `bash`, `yaml`).
  - For snippets >10 lines, link to the relevant GitHub repository/file.
- **No FAQ Sections**: Strictly prohibited (`자주 묻는 질문`, `FAQ`, or `FAQPage` schema).
- **Practical Checklists**: Include actionable implementation / checklist section.

## 5. Image & Cover Generation
1. Generate SVG cover image under `assets/images/YYYY-MM-DD-English_Title.svg`.
2. Ensure all text in the SVG is in **English only** (No Korean characters).
3. Validate with: `python3 scripts/verify_images_unified.py --all`.

## 6. Verification Gate (Run Before Completing)
```bash
# 1. Check post structure & front matter
python3 scripts/check_posts.py

# 2. Check broken links
python3 scripts/fix_links_unified.py --fix

# 3. Check timezone consistency
python3 scripts/check_kst_midnight.py
```
