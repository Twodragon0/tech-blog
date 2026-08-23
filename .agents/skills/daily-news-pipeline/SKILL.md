---
name: daily-news-pipeline
description: >-
  Automated daily DevSecOps news aggregation, AI classification, template generation,
  and publication pipeline using AGY Schedule, OMC Sisyphus, and CCG validation.
---

# Daily DevSecOps News Pipeline (AGY + OMC + CCG)

This skill orchestrates the end-to-end collection, classification, enhancement, and publication of daily security and cloud engineering news.

```
┌────────────────────────────────────────────────────────────────────────┐
│               AGY Background / Cron (/schedule)                        │
│            python3 scripts/collect_tech_news.py --hours 24             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 1: Ingestion & Deduplication                                    │
│  - 15+ RSS feeds loaded into _data/collected_news.json                 │
│  - Filter duplicates, noise, and low-relevance items                   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 2: OMC News Classification & Scoring (scripts/news/)            │
│  - analyzer.py: Category scoring (security, devsecops, cloud, k8s)     │
│  - content_generator.py: Template drafting into _drafts/ or _posts/    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Gemini Fast Ctx │       │  Claude (OMC)    │       │  Codex & Tests   │
│  - Quick CVE scan│       │  - Synthesis     │       │  - auto_publish  │
│  - Zero cost     │       │  - Impact eval   │       │  - Pytest branch │
└────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 3: SVG Generation & Verification Gate                           │
│  - scripts/news/svg_generator.py -> assets/images/YYYY-MM-DD-*.svg     │
│  - .venv/bin/pytest scripts/tests/test_news_templates.py               │
│  - python3 scripts/check_posts.py                                      │
└────────────────────────────────────────────────────────────────────────┘
```

## Key Commands & Workflow

### 1. Ingestion via AGY
```bash
# Ingest past 24 hours of technical feeds
python3 scripts/collect_tech_news.py --hours 24
```

### 2. Draft Generation & Enhancement
```bash
# Generate AI-assisted draft with scoring
python3 scripts/generate_news_draft.py --use-ai --max-posts 10

# Or execute template-based auto publishing
python3 scripts/auto_publish_news.py
```

### 3. Template Branch Rules (`auto_publish_news.py`)
- **Add test when adding branch**: Always update `scripts/tests/test_news_templates.py`.
- **Branch order = priority**: Specific keywords (istio, cosign, falco) before general (network, image).
- **Avoid over-matching**: Use specific terms like `admission controller`, `pod security`.
- **Coverage target**: Maintain >= 40% coverage on `auto_publish_news.py`.

### 4. Verification Gate
```bash
# Verify post structure & metadata
python3 scripts/check_posts.py

# Verify generated news SVG images
python3 scripts/verify_images_unified.py --all

# Run news test suite
.venv/bin/pytest scripts/tests/test_news_templates.py
.venv/bin/pytest scripts/tests/test_news_pipeline.py
```
