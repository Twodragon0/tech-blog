---
description: Ralph Loop improvement for collected news posts
agent: lead
---

You are improving blog posts using the Ralph Loop pattern.

Follow this workflow:
1. Check cache first: `_data/collected_news.json` (7-day TTL).
2. Use local scripts (`python3 scripts/*.py`) before any API call.
3. Prioritize Gemini CLI (free) over paid APIs.
4. Batch operations to reduce API calls.
5. Mask sensitive data in logs.

Output `<promise>POSTS_IMPROVED</promise>` when complete.
