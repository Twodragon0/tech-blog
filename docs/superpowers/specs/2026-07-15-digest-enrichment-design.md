# Digest Enrichment Design — Source-Grounded Detail + Body Sequence Diagrams

**Date**: 2026-07-15
**Status**: Draft (awaiting user review)
**Author**: brainstorming session

## Problem

Weekly-security-digest posts (181 of 236 posts) have two quality gaps:

1. **Summaries echo the source URL.** Per-item body text is template-generated from
   only the RSS title + a short snippet (cache `content` field is empty, median 0
   chars; `summary` median ~179 chars). The result reads as a paraphrase of the
   headline, not original analysis.
2. **Almost no visual flow.** Only 8 of 236 posts carry a mermaid diagram. Where an
   item describes an attack chain or incident timeline, a sequence diagram would add
   real explanatory value (see the existing `### 공격 흐름` block in
   `2026-07-13-…AI_GPT_Malware.md`).

## Goals

- Make per-item body analysis **more detailed and genuinely original**, grounded in
  the actual source article — **without hallucination**.
- Add **one body-level `sequenceDiagram`** per item **only where a real flow exists**.
- Fix the generator (`scripts/news/content_generator.py`) forward, then **backfill
  the 5 most recent digests as a pilot** before any wider rollout.

## Non-goals / YAGNI

- No diagrams on items without a real flow (blockchain price stories, opinion pieces).
  Forcing a diagram = fabricated flow = slop.
- No summary text asserting facts absent from the fetched source.
- No backfill beyond 5 digests in this iteration. Wider rollout is a **separate**
  future spec, gated on pilot results.
- No mermaid in the summary card (`ai-summary-card`) — a past cleanup
  (`scripts/remove_mermaid_from_summary.py`) deliberately keeps diagrams in the
  **body** only. This design preserves that.

## Hard constraints (learned from repo history)

| Constraint | Source | Enforcement |
|-----------|--------|-------------|
| Honesty: no claim without source evidence | digest fact-check work (~1% hallucination fixed); "실무 포인트" filler removal | extend digest fact-check gate |
| Diagrams in body, never summary card | `remove_mermaid_from_summary.py` | generator places in body; regression check |
| Safari-safe mermaid syntax (no bare `-`, `&`, paren issues) | `fix_all_mermaid_safari.py` | `validate_mermaid_syntax.py` must pass |
| Mermaid renders under enforcing CSP (no eval) | PR #449 `mermaid-csp-render` guard | existing CI guard covers new mermaid posts |
| Cost order: Gemini CLI (free) → local → API | CLAUDE.md §Cost Optimization | expansion uses Gemini CLI first |
| Don't upload user content externally; public news only | org policy | fetch = read-only GET of public article URLs |

## Architecture — two sequenced sub-projects

### Sub-project A — Source-grounded summary detail (implement first)

Components (each small, single-purpose):

1. **`source_fetcher`** (new module under `scripts/news/`)
   - Input: an item's `url`. Output: extracted readable article text + fetch status.
   - Read-only HTTP GET, realistic UA, timeout, robots/ToS-respecting (public news
     articles only). HTML → readable text extraction.
   - **Cache** to `_data/` (e.g. `source_articles_cache.json`) with a 7-day TTL keyed
     by URL hash, mirroring the existing `collected_news.json` 7-day pattern.
   - **Fail-closed**: fetch error / empty body / paywall → return `None`; caller keeps
     the current short summary. Never fabricate.

2. **`summary_expander`** (new function in `content_generator.py` or a sibling module)
   - Input: item + fetched article text. Output: a more detailed, original per-item
     analysis (what happened, who, technical mechanism, DevSecOps impact, response).
   - **Gemini CLI first** (free OAuth) with a prompt that forbids adding facts not in
     the provided source text; **local template fallback** (current behavior) if
     Gemini is unavailable or the source fetch failed.
   - Output length target: enough to stop reading as a headline paraphrase, bounded to
     avoid bloat.

3. **Honesty gate (extend existing digest fact-check)**
   - Verify the expanded text's factual claims are supported by the fetched source.
   - Unsupported claim → reject expansion, fall back to the safe short summary.

### Sub-project B — Body-level sequence diagrams (implement second)

1. **`flow_detector`** (new function)
   - Decide whether an item describes a real sequence-able flow (attack chain,
     exploitation steps, incident timeline). Heuristic keyword pass + LLM classify
     (Gemini first). Default = **no diagram** when uncertain (honest).

2. **`sequence_diagram_builder`** (new function)
   - For a flow-positive item, emit one body-level ```mermaid `sequenceDiagram`,
     placed like the existing `### 공격 흐름` block. Content derived from the fetched
     source (Sub-project A), not invented.
   - **Safari-safe** output (run through the same normalizations
     `fix_mermaid_syntax.py` enforces); must pass `validate_mermaid_syntax.py`.

## Data flow

```
collected_news.json (title, url, short summary)
        │
        ▼  source_fetcher (new, cached 7d, fail-closed)
article text (or None)
        │
        ├─▶ summary_expander (Gemini-first) ─▶ honesty gate ─▶ detailed body analysis
        │                                                      (or safe fallback)
        └─▶ flow_detector ─▶ sequence_diagram_builder ─▶ Safari-safe body mermaid
                                                          (or nothing)
        ▼
content_generator emits post body
        ▼
backfill: regenerate 5 most recent digests
        ▼
gates: validate_mermaid_syntax + mermaid-csp-render + digest fact-check
```

## Error handling

- Fetch failure / paywall / timeout → keep current short summary, no diagram. Logged.
- Gemini unavailable → local template fallback (never blocks generation).
- Diagram fails syntax/CSP validation → drop the diagram (post still valid), log.
- Honesty gate rejects → fall back to safe summary.

Every failure mode degrades to **current behavior**, never to fabricated content.

## Testing / verification

- Unit: `source_fetcher` (mock HTTP, cache TTL, fail-closed), `flow_detector`
  (flow vs no-flow fixtures), `sequence_diagram_builder` (Safari-safe output),
  `summary_expander` (source-grounded, fallback path).
- Integration: regenerate the 5 pilot digests; assert (a) mermaid only on flow items,
  (b) `validate_mermaid_syntax.py` passes, (c) `mermaid-csp-render` passes, (d) digest
  fact-check passes, (e) expanded summaries differ meaningfully from the source snippet
  (not a paraphrase) yet assert nothing unsupported.
- Cost: count Gemini calls; confirm API (paid) not hit.

## Rollout

1. Implement Sub-project A, verify on 5 pilot digests, review output quality.
2. Implement Sub-project B, verify on the same 5.
3. **Stop.** Wider backfill (remaining ~176 digests) is a separate spec, decided after
   reviewing pilot quality + cost.

## Open questions (resolved during brainstorming)

- Diagram scope → per-item, only where flow exists. ✅
- Summary detail source → fetch source article, Gemini-first evidence-based. ✅
- Backfill scope → generator + 5 most recent digests (pilot). ✅
- LLM strategy → Gemini CLI first + local fallback. ✅
