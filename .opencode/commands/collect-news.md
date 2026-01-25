# /collect-news - RSS News Collection Command

## Description
Cost-optimized collection of tech/security news from RSS feeds. Prioritizes cached data and local scripts to minimize API costs.

## Usage
```
/collect-news [--hours=24] [--use-cache=true]
```

## Arguments
- `--hours`: Hours of news to collect (default: 24)
- `--use-cache`: Use cached data when available (default: true)

## Cost Optimization
1. **Check cache first**: Use `_data/collected_news.json` if < 7 days old
2. **Local scripts**: Use `scripts/collect_tech_news.py` (no API cost)
3. **Rate limiting**: Max 15 requests/minute for RSS feeds
4. **Batch processing**: Collect all feeds in single run

## Workflow
1. Check cache validity (7-day TTL)
2. If cache valid, use cached data
3. If cache invalid or missing, run collection script
4. Save to `_data/collected_news.json`
5. Log statistics (total items, by category)

## Completion Promise
Output `<promise>NEWS_COLLECTED</promise>` when complete.

## Security
- Validate RSS feed URLs
- Sanitize collected content
- No hardcoded API keys
- Mask sensitive data in logs
