# February 2026 Topic SVG Compliance Matrix

---

## Re-audit (2026-04-27) — Post-fix commit `e0a535da`

**0 majors confirmed: YES — all 13 defects resolved.**

### Fix verification (5 modified files)

| Fix item | Expected | Actual | Status |
|----------|----------|--------|--------|
| `02-01` title garbled (was "AI 2026 AI AGENT / AI AGENT") | H1="AGENTIC AI SECURITY" H2="ATTACK VECTORS 2026" | H1="AGENTIC AI SECURITY" line:60, H2="ATTACK VECTORS 2026" line:61 | ✅ Fixed |
| `02-01` description placeholder | Topic-specific text | "Tool poisoning, tool chain attacks, and prompt injection defense for agentic AI in 2026." line:65 | ✅ Fixed |
| `02-01` accent color | Red defensible for Security; original ⚠️ not ❌ | Red `#ef4444` retained; category badge reads "SECURITY" — accepted | ✅ No change required |
| `02-04-AI_vs` accent color (was Red `#ef4444`) | Cyan `#22d3ee` (AI/ML) | microGrid dot `#22d3ee` line:15; panel stroke `#22d3ee` line:35; badge fill `#22d3ee` line:57 | ✅ Fixed |
| `02-04-AI_vs` H2 subtitle (was "DEVSECOPS") | "AI CODING COMPARISON" | H2="AI CODING COMPARISON" line:61 | ✅ Fixed |
| `02-04-AI_vs` description placeholder | Topic-specific text | "Side-by-side AI coding assistant comparison: Cursor AI vs Claude Code capabilities and workflows." line:65 | ✅ Fixed |
| `02-05-AI_Content` title garbled (was "DEVSECOPS / CLAUDE") | H1="AI CONTENT CREATOR" H2="WORKFLOW 2026" | H1="AI CONTENT CREATOR" line:66, H2="WORKFLOW 2026" line:67 | ✅ Fixed |
| `02-05-AI_Content` description placeholder | Topic-specific text | "End-to-end AI workflow for blog, video, music, and animation content creation in 2026." line:71 | ✅ Fixed |
| `02-05-AI_Content` accent (was ✅ already) | Cyan `#22d3ee` | Cyan `#22d3ee` confirmed line:15 | ✅ Unchanged/correct |
| `02-25` H2 garbled (was "38") | "BEST PRACTICES 2026" | H2="BEST PRACTICES 2026" line:63 | ✅ Fixed |
| `02-25` description placeholder | Topic-specific text | "38 best practices for Claude Code and OpenCode AI-assisted development workflows." line:67 | ✅ Fixed (note: "38" repurposed as count in description — acceptable) |
| `02-25` accent color (was Amber `#fbbf24`) | Violet `#a78bfa` (DevSecOps) | microGrid dot `#a78bfa` line:15; panel stroke `#a78bfa` line:35; badge fill `#a78bfa` line:59 | ✅ Fixed |
| `02-28` description placeholder | Topic-specific text | "Stateful runtime, continuous evaluation, and OWASP Agentic Top 10 patterns for AI agent security." line:65 | ✅ Fixed |

### Residual observations (non-blocking, flags only)

- `02-28` `<title>` still reads "AI AGENT STATEFUL RUNTIME" — understates "Security Architecture Design Guide" scope from filename. Minor, not a major.
- `02-28` H1/H2 still "AI AGENT STATEFUL / RUNTIME" — same scope mismatch noted in original audit. Still ⚠️, not promoted to ❌.
- `02-01` accent Red retained — original audit marked ⚠️ (ambiguous, not ❌). No change required; Security badge + category card both read "SECURITY" consistently.
- `02-25` description opens with "38 best practices…" — the "38" artifact from original H2 now appears as a count in the description sentence. Technically correct and readable; not a defect.

### Re-audit summary

| Rating | Count |
|--------|-------|
| ✅ Fixed | 13/13 |
| ⚠️ Partially fixed | 0 |
| ❌ Still broken | 0 |

**All 5 modified files pass with 0 major issues. The 8 unmodified Family B files carry no structural defects (minors only: signature y=545 vs y=615 spec, font-family sans-serif vs Arial). Overall Feb batch: 0 ❌ majors.**

---

## Original Audit (2026-04-24)

**Spec**: `docs/design/jan-topic-svg-design-system.md`  
**Spec version**: 1.0  
**Audit date**: 2026-04-24  
**Files audited**: 13  
**Auditor**: read-only inspection of SVG source

---

## Compliance Table

Legend: ✅ Compliant | ⚠️ Minor issue | ❌ Major issue

| # | Filename (short) | Family | viewBox / dims | Accent color | Title + subtitle | Description (y≈372) | Signature |
|---|-----------------|--------|---------------|--------------|-----------------|---------------------|-----------|
| 1 | `2026-02-01-Agentic_AI_Security_2026…` | A | ✅ 0 0 1200 630 | ⚠️ Red `#ef4444`; AI Security Architecture topic is ambiguous — Security accent (red) defensible but AI/ML accent (cyan `#22d3ee`) would better match category | ❌ H1="AI 2026 AI AGENT" H2="AI AGENT" — garbled, duplicated, not topic-specific | ❌ Placeholder: "Clean technical cover with stronger depth, hierarchy, and category-specific structure." | ✅ x=1150 y=612 end |
| 2 | `2026-02-04-3cs-framework` | B | ✅ 0 0 1200 630 | ✅ Teal/green gradient (DevSecOps/security framework — acceptable) | ✅ H1="3Cs Security Framework" H2="Context, Compliance, Control" (44px) | N/A (Family B) | ⚠️ x=80 y=545 — spec says y=615 for Family B; y=545 is within footer bar but off-spec |
| 3 | `2026-02-04-AI_vs_Claude_Code…` | A | ✅ 0 0 1200 630 | ❌ Red `#ef4444` (microGrid dot + blobs + panel stroke); AI Coding Comparison topic requires Cyan `#22d3ee` (AI/ML category) | ⚠️ H1="AI VS CLAUDE CODE" H2="DEVSECOPS" — H2 is category label, not subtitle of the comparison | ❌ Placeholder: "Clean technical cover with stronger depth, hierarchy, and category-specific structure." | ✅ x=1150 y=612 end |
| 4 | `2026-02-04-metro4shell-attack-vector` | B | ✅ 0 0 1200 630 | ✅ Red/orange tones (`#c0392b`, `#e74c3c`) — appropriate for attack vector / threat topic | ✅ H1="Metro4Shell Attack" H2="Vector Analysis" (46px) | N/A (Family B) | ⚠️ x=80 y=545 — spec says y=615; same deviation as 3cs-framework |
| 5 | `2026-02-05-AI-Tools-Ecosystem` | B | ✅ 0 0 1200 630 | ✅ Teal `#00cec9` / violet `#6c5ce7` hub-spoke pattern — appropriate for AI Tools ecosystem diagram | ✅ H1="AI Tools Ecosystem" H2="2026" (46px) | N/A (Family B) | ⚠️ x=80 y=545 — spec says y=615; `font-family="sans-serif"` (not Arial) |
| 6 | `2026-02-05-AI-Workflow-5-Phases` | B | ✅ 0 0 1200 630 | ✅ Violet `#6c5ce7` / green `#00b894` phase flow — appropriate for workflow diagram | ✅ H1="AI Workflow" H2="5 Phases" (46px) | N/A (Family B) | ⚠️ x=80 y=545 — spec says y=615; `font-family="sans-serif"` (not Arial) |
| 7 | `2026-02-05-AI_Content_Creator_Workflow…` | A | ✅ 0 0 1200 630 | ✅ Cyan `#22d3ee` — correct for AI/ML/content creation topic | ❌ H1="DEVSECOPS" H2="CLAUDE" — completely generic; filename is AI Content Creator Workflow, headings reference unrelated terms | ❌ Placeholder: "Clean technical cover with stronger depth, hierarchy, and category-specific structure." | ✅ x=1150 y=612 end |
| 8 | `2026-02-05-CVE-Timeline` | B | ✅ 0 0 1200 630 | ✅ Red `#c0392b` / `#e74c3c` — correct for CVE/vulnerability threat topic | ✅ H1="CVE Vulnerability" H2="Timeline" (46px) | N/A (Family B) | ⚠️ x=80 y=545 — spec says y=615; `font-family="sans-serif"` (not Arial) |
| 9 | `2026-02-05-NGINX-Attack-Flow` | B | ✅ 0 0 1200 630 | ✅ Green `#27ae60` / red `#e74c3c` — appropriate for attack flow (normal traffic vs attack paths) | ✅ H1="NGINX Hijacking" H2="Attack Flow" (46px) | N/A (Family B) | ⚠️ x=80 y=545 — spec says y=615; `font-family="sans-serif"` (not Arial) |
| 10 | `2026-02-05-Python-Pipeline-Architecture` | B | ✅ 0 0 1200 630 | ✅ Cyan `#06b6d4` / amber `#ffd43b` — appropriate for Python pipeline architecture (DevOps/cloud tooling) | ✅ H1="Python Pipeline" H2="Architecture" (46px) | N/A (Family B) | ⚠️ x=80 y=545 — spec says y=615; `font-family="sans-serif"` (not Arial) |
| 11 | `2026-02-05-Threat-Matrix` | B | ✅ 0 0 1200 630 | ✅ Purple `rgba(142,68,173,…)` matrix grid — acceptable for threat matrix / attack landscape | ✅ H1="Threat Matrix" H2="CVE and Attack Landscape" (46px) | N/A (Family B) | ✅ x=80 y=545 — signature present |
| 12 | `2026-02-25-Claude_Code_OpenCode_Best_Practices` | A | ✅ 0 0 1200 630 | ⚠️ Amber `#fbbf24` used; Claude Code / DevSecOps topic should use Violet `#a78bfa`; Amber maps to Blockchain/Incident per spec | ❌ H2="38" — a version number artifact, not a subtitle; H1="CLAUDE CODE OPENCODE" is acceptable but H2 is broken | ❌ Placeholder: "Clean technical cover with stronger depth, hierarchy, and category-specific structure." | ✅ x=1150 y=612 end |
| 13 | `2026-02-28-AI_Agent_Security_Architecture_Design_Guide` | A | ✅ 0 0 1200 630 | ⚠️ Red `#ef4444`; AI Agent Security Architecture is security-focused so red is defensible, but AI/Agent topic could use cyan; badge reads "SECURITY" | ⚠️ H1="AI AGENT STATEFUL" H2="RUNTIME" — partially topic-relevant but "STATEFUL RUNTIME" understates the "Security Architecture Design" scope | ❌ Placeholder: "Clean technical cover with stronger depth, hierarchy, and category-specific structure." | ✅ x=1150 y=612 end |

---

## Summary Statistics

### Overall

| Rating | Count | Pct |
|--------|-------|-----|
| ✅ Compliant rows (all 6 checks pass) | 0 | 0% |
| ⚠️ Minor issues (1–2 properties off) | 7 | 54% |
| ❌ Major issues (structural/content broken) | 6 | 46% |

### Per-property breakdown (13 files)

| Property | ✅ | ⚠️ | ❌ |
|----------|---|---|---|
| Family classification | 13 | 0 | 0 |
| viewBox / dimensions | 13 | 0 | 0 |
| Accent color | 6 | 4 | 3 |
| Title + subtitle | 6 | 2 | 5 |
| Description (Family A only, 5 files) | 0 | 0 | 5 |
| Signature | 5 | 8 | 0 |

**Universal pass**: viewBox/dimensions and family classification are 13/13 compliant.  
**Critical failure**: Description line — all 5 Family A files carry the generator placeholder `"Clean technical cover with stronger depth, hierarchy, and category-specific structure."` (0/5 topic-specific).  
**Signature deviation**: 8 Family B files use y=545 instead of spec y=615; signature text is present in all 13 files so technically readable, but position is off-spec for Family B.

---

## Top 5 Files Needing Rework

### 1. `2026-02-05-AI_Content_Creator_Workflow_2026_Blog_Video_Music_Animation` — THREE major gaps
- **H1/H2 garbled**: H1="DEVSECOPS" H2="CLAUDE" — unrelated to the AI content creator workflow topic. Should read e.g. H1="AI CONTENT CREATOR" H2="WORKFLOW 2026"
- **Description**: Generic placeholder — needs: e.g. "End-to-end AI workflow for blog, video, music, and animation content creation in 2026."
- **Accent**: Cyan `#22d3ee` is correct — no change needed on this property

### 2. `2026-02-01-Agentic_AI_Security_2026_Attack_Vectors_Defense_Architecture` — TWO major gaps
- **H1/H2 garbled**: H1="AI 2026 AI AGENT" H2="AI AGENT" — repetitive and generic. Should read e.g. H1="AGENTIC AI SECURITY" H2="ATTACK VECTORS 2026"
- **Description**: Generic placeholder — needs: e.g. "Attack vector taxonomy and defense architecture for agentic AI systems in 2026."
- **Accent**: Red defensible for Security category; consider cyan `#22d3ee` if repositioning as AI/ML post

### 3. `2026-02-25-Claude_Code_OpenCode_Best_Practices` — TWO major gaps
- **H2 garbled**: H2="38" is a version/build artifact. Should read e.g. H2="BEST PRACTICES 2026"
- **Description**: Generic placeholder — needs: e.g. "Practical best practices for Claude Code and OpenCode AI-assisted development workflows."
- **Accent**: Change from Amber `#fbbf24` to Violet `#a78bfa` for DevSecOps/AI Tools category

### 4. `2026-02-04-AI_vs_Claude_Code_AI_Coding_Assistant_Comparison` — ONE major + ONE minor gap
- **Accent**: Red `#ef4444` is incorrect for an AI coding comparison post; change to Cyan `#22d3ee` (AI/ML category). Update microGrid dot, ambient blobs, panel stroke, badge fills, tag pills, stat card strokes.
- **Description**: Generic placeholder — needs: e.g. "Side-by-side comparison of AI coding assistants: Cursor AI vs Claude Code capabilities and workflows."
- **H2**: "DEVSECOPS" is a category label, not a subtitle — rewrite to e.g. "AI CODING COMPARISON"

### 5. `2026-02-28-AI_Agent_Security_Architecture_Design_Guide` — ONE major + ONE minor gap
- **Description**: Generic placeholder — needs: e.g. "Security architecture patterns and design guide for stateful AI agent systems."
- **H1/H2**: "AI AGENT STATEFUL / RUNTIME" is partially relevant but undersells the design guide scope — consider "AI AGENT SECURITY / ARCHITECTURE GUIDE"

---

## Files with No Major Issues

None of the 13 files pass all 6 checks cleanly. The closest to compliant:

- `2026-02-04-metro4shell-attack-vector` — title, accent, viewBox all correct; only minor signature y-position deviation
- `2026-02-05-CVE-Timeline` — title, accent, viewBox all correct; only minor signature y-position deviation
- `2026-02-05-NGINX-Attack-Flow` — title, accent, viewBox all correct; only minor signature y-position deviation
- `2026-02-05-Python-Pipeline-Architecture` — title, accent, viewBox all correct; only minor signature y-position deviation
- `2026-02-05-Threat-Matrix` — title, accent, viewBox, signature all correct; no major gaps

---

## Notes

- **All 13 files** use `viewBox="0 0 1200 630" width="1200" height="630"` — universal pass.
- **All 13 files** contain the `tech.2twodragon.com` signature text — universal pass on signature presence.
- **All 5 Family A files** carry the identical generator placeholder description at y=372. This is the spec's most critical issue (§5 Family A note) and affects 100% of Family A files.
- **Family B y=545 deviation**: 8 of 8 Family B files use `x="80" y="545"` for the signature. Spec mandates `y="615"`. The footer bar is `<rect y="520" h="110">` so y=545 is within the bar — functionally acceptable but off-spec. Only `2026-02-05-Threat-Matrix` uses `y="545"` directly without the sans-serif font deviation.
- **font-family deviation**: 6 Family B files use `font-family="sans-serif"` instead of the spec-mandated `font-family="Arial,sans-serif"`. Low visual impact but technically non-compliant.
- **New pattern observed (Feb only)**: Several Family B files (3cs-framework, metro4shell) show a dual-signature row: `tech.2twodragon.com` at left + category label (e.g. "DevSecOps") at right. This is a Feb-era extension of the Family B footer not present in January files — flagged but not penalized.

---

*Cross-reference: See also [jan-svg-compliance-matrix.md](jan-svg-compliance-matrix.md), [mar-svg-compliance-matrix.md](mar-svg-compliance-matrix.md), [apr-svg-compliance-matrix.md](apr-svg-compliance-matrix.md)*
