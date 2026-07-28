# Digest retranslate backfill — security design (재발 방지 B단계)

**Date**: 2026-07-28
**Components**: `scripts/retranslate_digest.py`, `.github/workflows/digest-translate-backfill.yml`
**Detection reused**: `scripts/check_digest_untranslated.py` (Part A)

## Problem

Weekly digests auto-publish. On the **untrusted `repository_dispatch`** path,
`ai-blogwatcher.yml` intentionally zeroes `GEMINI_API_KEY` / `DEEPSEEK_API_KEY`
(MED-1 secret partition, 2026-07-06 audit) so an externally-authored payload can
never reach a live LLM key. With no key, the translation fallback in
`scripts/news/content_generator.py` emits **raw English** RSS text into
`#### 요약` blocks and `summary=` / `title=` fields. Part A detects this; Part B
(this work) corrects it.

## Trust model — why this is safe

Part B runs the LLM over post text that ORIGINATED from untrusted RSS, which
sounds like it re-opens the MED-1 concern. It does not, for four independent
reasons:

1. **The key is never exposed to the dispatch requester.** MED-1's actual worry
   is *secret exfiltration* — a poisoned feed reaching a live key on a path an
   external party can trigger. `digest-translate-backfill.yml` has **no
   `repository_dispatch` trigger** (only `schedule` + `workflow_dispatch`), so an
   external party cannot cause it to run at all. A defense-in-depth
   `if: github.event_name != 'repository_dispatch'` guard on the secret-injecting
   step makes a *future* trigger edit fail-closed (empty key → the script is a
   clean no-op), and the job-level `if` pins the whole job to trusted events.

2. **The content is already committed.** By the time Part B runs, the digest is
   in git (published by the trusted schedule path, or landed via the reviewed PR
   the untrusted path opens). We translate *repository text*, not a live
   attacker-controlled HTTP payload. There is no SSRF/feed-fetch surface here —
   `retranslate_digest.py` does zero network I/O of its own beyond the LLM call.

3. **The LLM output is sanitized before it can become post text.** The model
   result is written into Markdown/Liquid: `summary=`/`title=` attribute values
   (re-escaped to a single quote-free line) and — for `#### 요약` blocks — inline
   into the kramdown-rendered body (raw inline HTML is on) which Jekyll also
   re-processes through Liquid. So the output is NOT structurally inert by
   position; a prompt-injected response containing `<script>`, `{% … %}`, or
   `{{ … }}` plus Hangul would otherwise land as active markup. `_is_valid_korean`
   therefore REJECTS any candidate containing `<`, `{%`, `{{`, or `]]>` (in
   addition to requiring Hangul and bounding length); a rejected candidate is
   fail-safe-dropped and the original English is kept (Part A still flags it).
   There is no tool-use, no shell, no `eval`. Prompt injection in the source can
   at worst change *what validated Korean sentence* gets written — it cannot
   inject active HTML/Liquid, nor escalate to code or network access.

4. **Every translation is output-validated before it is written** (fail-safe):
   - must contain Hangul (`[가-힣]`) — rejects "translation refused"/echoed English,
   - must be ≤ `MAX_LEN_RATIO` (3×) the source length — rejects runaway / injected
     bulk output,
   - `summary=`/`title=` are re-escaped (`_html_escape_quotes`) and whitespace-
     collapsed to a single physical line with no inner double-quote, so the value
     cannot break out of the Liquid attribute or the YAML/Markdown structure.
   If validation fails, the **original English is kept** — we never write suspect
   output. Worst realistic case: the post stays untranslated (Part A's gate still
   flags it) rather than shipping garbage.

Contrast with MED-1: MED-1 protects *the secret* on an externally-triggerable
path by withholding the key. Part B protects *the output* on a
non-externally-triggerable path by validating what the key produces. Different
threat (exfiltration vs. content integrity), different, appropriate control.

## Residual risks + mitigations

| Risk | Mitigation |
|------|------------|
| Prompt injection in RSS-derived source text steers the translation | Output is validated Korean text only; no tool/eval/network surface. Bounded blast radius = one wrong sentence, caught on human PR review. |
| Model emits an over-long / padded response | Length-ratio cap (3×) rejects it, original kept. |
| Model emits English / refuses | Hangul check rejects it, original kept. |
| Broken structure (unescaped quote, newline in attribute) | Single-line + `_html_escape_quotes` on write; `check_posts` / digest gates run on the PR before merge. |
| Future edit adds `repository_dispatch` and leaks a key | Job-level `if` (trusted events only) + step-level `github.event_name != 'repository_dispatch'` guard → empty key → no-op. |
| Direct push to main bypassing review | Job never pushes to main; it opens a PR (graceful-degrade: pushes branch + prints manual-open URL if `gh pr create` is disabled). |

## Non-goals / decisions

- **Does not touch `ai-blogwatcher.yml`** or the digest generator's live
  behavior — this is a separate, additive correction pass.
- **Whole-block translation**: a fully-English 요약 block (English RSS summary +
  short appended Korean advisory) is translated as one unit rather than splicing
  out only the English lead. Simpler and honest; the appended advisory's meaning
  is preserved and the result is validated Korean. Partially-Korean blocks are
  never touched (`is_untranslated` returns False), so this only fires on the true
  fallback regression.
- **Least privilege**: `permissions: contents: write, pull-requests: write`
  only; top-level `permissions: {}`.
