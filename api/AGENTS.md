<!-- Parent: ../AGENTS.md -->
# api/ — AI Agent Guidelines

**Last updated**: 2026-04-08

Vercel Serverless Functions for the blog's dynamic features.

## Files

```
api/
├── chat.js       # POST /api/chat — DeepSeek chatbot endpoint
├── search.js     # GET  /api/search — Post search endpoint
├── markdown.js   # POST /api/markdown — Markdown rendering
└── lib/
    └── ratelimit.js  # Rate limiting (10 req/min per session)
```

## Security Requirements (all endpoints)

- Rate limiting via `api/lib/ratelimit.js` — import on every endpoint
- Input validation: sanitize for XSS and injection patterns before processing
- CORS: restrict allowed origins (do not set `*` in production)
- Timeout: keep handlers under 8 seconds (Vercel free tier limit)
- API keys: read from Vercel environment variables only — never hardcode

```javascript
// Correct: environment variable
const apiKey = process.env.DEEPSEEK_API_KEY;
if (!apiKey) return res.status(500).json({ error: 'API not configured' });

// Wrong: hardcoded
const apiKey = 'sk-xxxxx';
```

## chat.js — DeepSeek API

Cost controls already implemented — do not remove:

| Control | Value | Reason |
|---------|-------|--------|
| Context caching | Enabled | Up to 90% cost reduction |
| `max_tokens` | 1500 | Cap response size |
| Conversation history | 10 messages max | Limit context window cost |

Off-peak hours (UTC 16:30-00:30) get a 50-75% discount — prefer scheduling batch calls during that window.

## Error Handling

```javascript
// Always return structured errors — never leak stack traces
try {
  const result = await callExternalApi();
  return res.status(200).json(result);
} catch (error) {
  console.error('API error:', error);  // Server-side log only
  return res.status(500).json({ error: 'Request failed' });  // User-facing
}
```

## Deployment

Functions are deployed automatically via Vercel on push to `main`.
Config lives in `../vercel.json` (CSP headers, caching rules, function routing).

Secrets are set in Vercel Dashboard → Settings → Environment Variables.
Never commit `.env` files.
