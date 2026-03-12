---
description: Collect tech/security RSS news with cache-first cost controls
agent: explore
---

CRITICAL COST OPTIMIZATION:
1. Check `_data/collected_news.json` cache first (use if < 7 days old).
2. Use `python3 scripts/collect_tech_news.py` (local script, no API cost).
3. Rate limit: max 15 requests/minute.
4. Batch all feeds in a single run.
5. Never use paid APIs for this task.

Output `<promise>NEWS_COLLECTED</promise>` when complete.
