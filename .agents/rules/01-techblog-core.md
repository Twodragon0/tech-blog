# Core Tech Blog Rules (Antigravity & Agents)

## 1. Post Structure & Front Matter
- Posts must live in `_posts/YYYY-MM-DD-English_Title.md`.
- Front matter schema:
```yaml
---
layout: post
title: "Title (Korean allowed)"
date: YYYY-MM-DD HH:MM:SS +0900   # HH >= 09:00 (Timezone Rule)
category: security|devsecops|devops|cloud|kubernetes|finops|incident
categories: [category1, category2]
tags: [tag1, tag2, tag3]
excerpt: "Concise summary (150-200 chars)"
image: /assets/images/YYYY-MM-DD-English_Title.svg
---
```

## 2. Timezone Rule (UTC vs KST)
- `_config.yml` pins `timezone: UTC`.
- Default new posts to `09:00:00 +0900` (or later) so KST day == UTC day.
- If authored with KST `00:00-08:59 +0900`, you MUST add:
```yaml
redirect_from:
  - /posts/{YYYY}/{MM}/{DD}/{slug}/
```

## 3. Image & SVG Guidelines
- **Filename**: English characters only (e.g., `2026-08-22-Zero_Day_Mitigation.svg`).
- **SVG Text**: English only inside `<text>` tags.
- **Special characters in SVG**: No `·`, `•`, `—`, `"`, `'` — use ASCII equivalents.
- **Conversion**: Run `python3 scripts/rename_images_to_english.py --yes` if needed.

## 4. Content Constraints
- **NO FAQ Sections**: Never add FAQ (자주 묻는 질문) sections or `schema_type: FAQPage`.
- **Code Blocks**: Always specify language tags (```python, ```yaml, ```bash). Replace >10 lines code blocks with GitHub links when appropriate.
- **Tone**: Technical depth, real production examples, actionable DevSecOps/Cloud architecture guidance.
