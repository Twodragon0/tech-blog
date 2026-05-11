# Rollup Cover Design — Phase 0 Data Audit

**Created**: 2026-05-11
**Inputs**: 5 source posts targeted by `.omc/plans/rollup-cover-design.md`
**Purpose**: ground-truth the spec schema decisions (especially `days[]` cardinality, derivation source) before Phase 1 renderer work.

## Per-post audit table

| File | redirect_from | summary_card.highlights | Index table rows | kind | period_label | daily_count | daily_count_source |
|------|---------------|-------------------------|------------------|------|--------------|-------------|--------------------|
| `_posts/2026-01-31-January_2026_Security_Digest_Monthly_Index.md` | none (0) | 3 (월간 종합 / 위협 동향 / 운영 포인트) | **9** (W4 only: 1/23, 1/24, 1/25, 1/26, 1/27, 1/28, 1/29, 1/30, 1/31) | `monthly_index` | `January 2026 (W4)` | 9 | `index_table` |
| `_posts/2026-02-28-February_2026_Security_Digest_Monthly_Index.md` | none (0) | 3 (월간 종합 / 위협 동향 / 운영 포인트) | **22** total across 4 weeks (W1=6, W2=3, W3=6, W4=7) | `monthly_index` | `February 2026` | 22 (rendered as 4 week cells) | `index_table` |
| `_posts/2026-04-05-Week1_April_2026_Security_Digest.md` | 5 entries (4/1..4/5) | 3 (공급망 위협 / 제로데이 / 클라우드 컴플라이언스) | 5 daily rows (4/1, 4/2, 4/3, 4/4, 4/5) | `weekly_rollup` | `April 1-5, 2026` | 5 | `redirect_from` |
| `_posts/2026-04-12-Week2_April_2026_Security_Digest.md` | 7 entries (4/6..4/12) | 3 (APT 집중 / 봇넷·클라우드 / 공급망·멀웨어) | 7 daily rows (4/6..4/12) | `weekly_rollup` | `April 6-12, 2026` | 7 | `redirect_from` |
| `_posts/2026-04-19-Week3_April_2026_Security_Digest.md` | 7 entries (4/13..4/19) | 3 (공급망 침해 / 신규 취약점 / 봇넷 확산) | 7 daily rows (4/13..4/19) | `weekly_rollup` | `April 13-19, 2026` | 7 | `redirect_from` |

## Findings vs. plan

| Plan claim | Reality | Resolution |
|------------|---------|------------|
| Plan §4 says `daily_count: 4` for January (W1-W4) | January is **W4-only with 9 daily digests** (1/23-1/31). No W1-W3 exist. | Render Jan as a 9-cell day strip with `daily_count_source: index_table`. Drop the W1-W4 fallback. |
| Plan §4 says weekly rollups have `daily_count: 7` | April Week 1 only has **5** dailies (4/1-4/5), not 7. Week 2 + Week 3 = 7. | Schema must allow `len(days)` 5-7 for `weekly_rollup`, not strictly == 7. |
| Plan §6.6 says "if missing, lift highlights from markdown body" | All 5 posts **have** `summary_card.highlights` with 3 items each | No fallback needed. Use `summary_card.highlights` directly. |
| Critic flag: monthly indexes lack `redirect_from` | Confirmed — both January and February have 0 `redirect_from` entries. | Use `daily_count_source: index_table` enum for monthly. |
| Critic flag: schema needs `daily_count_source` | Required — derivation differs per kind. | Enum: `{redirect_from, index_table, manual}`. |

## Phase 1 schema implications

- `kind ∈ {weekly_rollup, monthly_index}`
- `daily_count_source ∈ {redirect_from, index_table, manual}` (audit-trail field)
- `severity ∈ {HIGH, MEDIUM, LOW}` per `top_highlights` entry
  - **LOW maps to BLUE** (THEMES.blue), not green — green is reserved for the L22 wiper/ransomware semantic in `2026-04-29.yml:56-79`. Using blue for LOW makes the severity rampage red-amber-blue cleaner and avoids palette collision.
- `len(days)`:
  - `weekly_rollup` → 5-7 (relaxed from plan's strict `== 7`)
  - `monthly_index` → 4-31 inclusive (accommodates Jan's 9 cells and Feb's 4 week-cells)
- `len(top_highlights) == 3` (matches all 5 sources)

## Editorial budget note

5 specs × ~30 min hand-curation = ~2.5h. All highlights extractable from `summary_card.highlights`; day-cell tags must be hand-shortened from the index table to ≤30 chars English. February rollup will use 4 week-aggregated cells (W1/W2/W3/W4) rather than 22 individual day-cells to avoid clutter (each cell carries the week's headline issue).
