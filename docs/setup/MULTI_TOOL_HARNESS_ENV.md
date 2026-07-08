# Multi-Tool Harness — Env Var Best Practices

Single reference for environment variables across the Claude Code + Codex
+ Gemini + OMC harness, covering local dev, GitHub Actions, and Vercel
production. Last updated: 2026-05-08.

> **Threat model**: every value listed below is a secret unless marked
> `[public]`. Never commit `.env`, never echo a value in CI logs without
> masking, and rotate immediately if a key appears in a PR diff.

## 1. Tool-stack overview

| Tier | Tool | Trigger | Cost basis |
|------|------|---------|-----------|
| 0 | **Local templates** | `python3 scripts/...` | Free |
| 0 | **Gemini CLI** (OAuth) | `gemini` cmd | Free OAuth quota |
| 1 | **Claude Code** | interactive / OMC skills | Anthropic plan |
| 1 | **Codex / Gemini via OMC `/ask`** | CCG skill | Subagent runs in Claude Code |
| 2 | **DeepSeek API** | api/chat.js, content_generator | $ per token (cache up to 90% off) |
| 2 | **OpenAI API** | scripts/generate_post_images.py | $ per token |
| 3 | **Anthropic / Gemini direct API** | scripts/ai_improve_posts.py | $ per token |

Default order in scripts: **Tier 0 → Tier 1 → Tier 2 → Tier 3**. Skip
to higher tier only when the lower tier returns nothing or hits a circuit
breaker (e.g. Gemini failover to DeepSeek in `enhancer.py`).

## 2. Categorised env vars

### 2.1 LLM API keys (secrets)

| Var | Used by | Notes |
|-----|---------|-------|
| `ANTHROPIC_API_KEY` | Claude SDK / Claude Code | Prefer Claude Code session over direct API for cost. |
| `CLAUDE_API_KEY` | scripts/ai_improve_posts.py | Legacy alias for `ANTHROPIC_API_KEY`; keep in sync. |
| `GEMINI_API_KEY` | scripts/generate_post_images.py, scripts/news/enhancer.py | Free tier 60 RPM. Falls back to DeepSeek on circuit-open. |
| `OPENAI_API_KEY` | scripts/generate_post_images.py (GPT image) | Optional; only when `USE_GPT54_PROMPT_ENHANCER=true`. |
| `DEEPSEEK_API_KEY` | api/chat.js, scripts/news/content_generator.py | Use Context Caching for ≤10% of full price. |

### 2.2 Model selection / feature flags

| Var | Default | Effect |
|-----|---------|--------|
| `DEEPSEEK_MODEL` | `deepseek-chat` | Override to `deepseek-reasoner` for harder prompts. |
| `GPT54_MODEL` | `gpt-5.4` | Set to model snapshot date for stability. |
| `USE_GEMINI_PRO_IMAGE` | `true` | `false` → text-only Gemini path (cheaper). |
| `USE_GPT54_PROMPT_ENHANCER` | `true` | `false` → skip OpenAI enhancement step. |
| `USE_PROFESSIONAL_IMAGE_STYLE` | `true` | Toggles editorial vs casual SVG layout. |
| `USE_L20_HERO` | `1` | `0` falls back to legacy `generate_svg_image` cover. |
| `AUTO_PUBLISH_USE_AI` | `auto` | `auto` / `gemini` / `deepseek` / `template`. |

### 2.3 OAuth / external services (secrets)

| Var | Used by | Notes |
|-----|---------|-------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Gemini OAuth flow | Path to service-account JSON. NEVER commit JSON. |
| `GOOGLE_CLOUD_PROJECT` | Gemini OAuth flow | Project ID for billing/quotas. |
| `BUTTONDOWN_API_KEY` | scripts/test_buttondown_api.py, buttondown-notify workflow | Newsletter dispatch. |
| `LINKEDIN_CLIENT_ID` / `LINKEDIN_CLIENT_SECRET` | scripts/linkedin_oauth.py | OAuth handshake. |
| `SENTRY_DSN` | _includes/sentry.html, build.sh | Production-only injection (see §4). |
| `SLACK_WEBHOOK_URL` | googlebot-access-monitor, slack-* workflows | GH Actions secret only. |
| `VERCEL_TOKEN` | (CI only) | Used by Vercel Action for preview deploys. |

### 2.4 CI / control flags

| Var | Where | Effect |
|-----|-------|--------|
| `CI` | GH Actions auto-set | Skips interactive prompts (`TECH_BLOG_AUTO_YES` semantics). |
| `TECH_BLOG_AUTO_YES` | local + scripts | `1` → assume yes for confirmation prompts. |
| `TECH_BLOG_NO_AUTO_COMMIT` | scripts/auto_publish_news.py | `1` → don't commit after auto-publish. |
| `GITHUB_TOKEN` | scripts/check_workflow_action_pins.py | Action-pin verification API. |
| `SKIP_VARIANT_CHECK` | scripts/check_post_image_variants.py | `1` → skip raster variant gate (emergencies only). |
| `SKIP_PIN_CHECK` | scripts/check_workflow_action_pins.py | `1` → skip action SHA pin gate. |
| `SKIP_QUOTE_CHECK` | scripts/check_post_quote_safety.py | `1` → skip front-matter quote safety gate. |
| `DEBUG` | universal | `1`/`true`/`yes` → verbose logging. |
| `SITE_URL` | scripts/build_slack_post_message.py | Override default https://tech.2twodragon.com. |

### 2.5 Vercel runtime

| Var | Provided by Vercel | Effect |
|-----|--------------------|--------|
| `VERCEL_ENV` | platform | `production` / `preview` / `development` — used for log gating in api/chat.js. |
| `NODE_ENV` | platform | `production` enables Sentry, disables CORS dev origins. |

## 3. Tool-specific harness vars

### 3.1 Claude Code / OMC

OMC reads its own state — these vars only affect behaviour at the harness layer. Keep them OUT of `.env` (set in shell or `~/.claude/settings.json`).

| Var | Effect |
|-----|--------|
| `DISABLE_OMC` | Disable OMC entirely. |
| `OMC_SKIP_HOOKS` | Comma-separated hook names to skip. |
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` enables teammate mode. |
| `CLAUDE_PLUGIN_ROOT` | Used by OMC plugin scripts. |
| `OMC_STATE_DIR` | Centralized state directory for shared sessions. |

### 3.2 CCG (Claude–Codex–Gemini tri-model)

CCG dispatches sub-prompts via OMC's `/ask codex` and `/ask gemini`. Those sub-tools read their own auth — no extra `.env` keys needed at the CCG layer.

- **Codex**: relies on `gh` CLI auth (token scope `repo`, `workflow`).
- **Gemini**: prefers OAuth (free quota); falls back to `GEMINI_API_KEY` if set.
- **Claude**: uses the active Claude Code session (no key needed).

### 3.3 Codex CLI

| Var | Effect |
|-----|--------|
| `CODEX_HOME` | Codex config / cache dir (default `~/.codex`). |
| `CODEX_DEFAULT_MODEL` | Override default model for non-interactive runs. |
| `CODEX_SANDBOX` | `read-only` / `workspace-write` / `danger-full-access`. Default safe. |

### 3.4 Gemini CLI

| Var | Effect |
|-----|--------|
| `GEMINI_API_KEY` | Optional; OAuth quota preferred. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Service-account fallback (rare). |

### 3.5 Harness (general)

| Var | Effect |
|-----|--------|
| `HARNESS_LOG_LEVEL` | `debug` / `info` / `warn` / `error`. Default `info`. |
| `HARNESS_DRY_RUN` | `1` → planned actions only, no side effects. |

## 4. Vercel build-time injection

Vercel does NOT read `.env` from the repo. Set every secret in
**Project Settings → Environment Variables** with the right scope:

- `Production` — live site
- `Preview` — PR preview deploys
- `Development` — `vercel dev` (rare)

Build-time mapping (see `build.sh` L130-143):

```bash
if [ -n "$SENTRY_DSN" ]; then
  python3 -c "..."  # rewrite _config.yml: sentry_dsn: ""  →  sentry_dsn: "<value>"
fi
```

Add similar blocks for any other secret that needs to land in
`_config.yml` so Liquid templates can read it.

## 5. GitHub Actions secrets

Set these via **Repo Settings → Secrets and variables → Actions → Repository secrets**:

| Secret | Used by workflow | Purpose |
|--------|------------------|---------|
| `DEEPSEEK_API_KEY` | ai-blogwatcher.yml, daily-news.yml (deprecated) | Auto-publish digest |
| `GEMINI_API_KEY` | ai-blogwatcher.yml | Image enhancement |
| `OPENAI_API_KEY` | generate-images.yml | Cover regeneration |
| `BUTTONDOWN_API_KEY` | buttondown-notify.yml | Newsletter dispatch |
| `SLACK_WEBHOOK_URL` | googlebot-access-monitor.yml, slack-*.yml | Alert channel |
| `SENTRY_AUTH_TOKEN` | sentry-release.yml | Source-map upload |
| `VERCEL_TOKEN` | vercel-deploy.yml | Manual preview deploys |

CI does NOT inherit secrets across workflows; specify each `secrets:` mapping per-job.

## 6. Local development (.env)

Create `.env` in repo root (gitignored). Recommended layout:

```dotenv
# === LLM API keys ===
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
OPENAI_API_KEY=sk-proj-...
DEEPSEEK_API_KEY=sk-...

# === Model selection ===
DEEPSEEK_MODEL=deepseek-chat
USE_GEMINI_PRO_IMAGE=true
USE_GPT54_PROMPT_ENHANCER=true

# === OAuth ===
GOOGLE_APPLICATION_CREDENTIALS=/abs/path/to/sa.json
GOOGLE_CLOUD_PROJECT=your-gcp-project

# === Newsletter / social ===
BUTTONDOWN_API_KEY=...
LINKEDIN_CLIENT_ID=...
LINKEDIN_CLIENT_SECRET=...

# === Observability ===
SENTRY_DSN=https://...@o.../...

# === Control flags ===
TECH_BLOG_AUTO_YES=1
DEBUG=false
```

`.gitignore` already excludes `.env`, `.env.local`, `.env.*.local`,
`.env.production`, `.env.development`, `.env.test`, `*.env`, `*.key`,
`**/DEEPSEEK_API_KEY`, `**/OPENAI_API_KEY`, `**/GEMINI_API_KEY`.

## 7. Loading patterns

### Python
```python
import os
api_key = os.getenv("DEEPSEEK_API_KEY", "")
if not api_key:
    raise RuntimeError("DEEPSEEK_API_KEY not configured")
```

### Node.js (Vercel functions)
```javascript
const apiKey = process.env.DEEPSEEK_API_KEY;
if (!apiKey) {
  return res.status(503).json({ error: "service_unavailable" });
}
```

### Shell (build.sh)
```bash
if [ -n "$SENTRY_DSN" ]; then
  # safe to use
fi
```

## 8. Security gates

1. **`.gitignore`** must always exclude `.env*` and key files.
2. **Pre-commit** (`scripts/check_post_quote_safety.py` style) should
   scan staged files for hardcoded secrets — pattern: `^(sk-|AIza|gho_|xox[bp]-|eyJ[A-Za-z0-9_-]{20,})`.
3. **Logs**: every script that prints user-derived data MUST run output
   through `mask_sensitive_info()` (see scripts/news/config.py).
4. **CI**: never `cat .env` or `env` in workflow steps. Use
   `${{ secrets.NAME }}` directly.
5. **Rotation**: if a key shows up in a PR diff, rotate within 1 hour.

## 9. Quick verification

```bash
# Sanity check: which API tier is reachable?
python3 - <<'PY'
import os
tiers = {
    "Anthropic": "ANTHROPIC_API_KEY",
    "Gemini":    "GEMINI_API_KEY",
    "OpenAI":    "OPENAI_API_KEY",
    "DeepSeek":  "DEEPSEEK_API_KEY",
}
for name, var in tiers.items():
    set_ = bool(os.getenv(var))
    print(f"  {name:10} {'✓' if set_ else '·'}  {var}")
PY
```

## 10. Trouble-shooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `503` from `/api/chat` | `DEEPSEEK_API_KEY` not set in Vercel | Add via Vercel Dashboard, redeploy. |
| `Gemini circuit breaker OPEN` in build log | Free quota exhausted | Wait or set `USE_GEMINI_PRO_IMAGE=false`. |
| Sentry not capturing errors | `SENTRY_DSN` empty in `_config.yml` | Vercel env var → build.sh injection. |
| GH Actions step "secrets not found" | Job missing `secrets:` mapping | Add to job-level `env:` or `with:`. |
