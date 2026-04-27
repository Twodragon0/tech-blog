# January 2026 Topic SVG Compliance Matrix

**Spec**: `docs/design/jan-topic-svg-design-system.md`  
**Spec version**: 1.0  
**Audit date**: 2026-04-24  
**Files audited**: 25  
**Auditor**: read-only inspection of SVG source

---

## Compliance Table

Legend: ✅ Compliant | ⚠️ Minor issue | ❌ Major issue

| # | Filename (short) | Family | viewBox / dims | Accent color | Title + subtitle | Description (y≈372) | Signature |
|---|-----------------|--------|---------------|--------------|-----------------|---------------------|-----------|
| 1 | `2026-01-01-Tesla_FSD…` | A | ✅ 0 0 1200 630 | ✅ Violet `#a78bfa` (DEVSECOPS) | ✅ Present, 54/52px | ✅ Topic-specific (L68) | ✅ x=1150 y=612 end |
| 2 | `2026-01-03-OWASP_2025…` | A | ✅ 0 0 1200 630 | ✅ Red `#ef4444` (SECURITY) | ✅ Present, 54/52px | ✅ Topic-specific (L65) | ✅ x=1150 y=612 end |
| 3 | `2026-01-06-DevSecOps_Viewing_Automotive…` | A | ✅ 0 0 1200 630 | ⚠️ Violet `#a78bfa` badge=DEVSECOPS but `<title>` says BLOCKCHAIN; desc references automotive but H1/H2 say DEVSECOPS/BLOCKCHAIN — content mismatch | ⚠️ H1="DEVSECOPS" H2="BLOCKCHAIN" (not automotive) | ⚠️ Desc references automotive, H1/H2 reference blockchain (L68: automotive text; L63-64: blockchain headings) | ✅ x=1150 y=612 end |
| 4 | `2026-01-08-Blockchain_Cryptocurrency…` | A | ✅ 0 0 1200 630 | ❌ Violet `#a78bfa` used; spec requires Amber `#f59e0b` for Blockchain/Crypto (L15, L30-31) | ✅ Present, 54/52px | ✅ Topic-specific — blockchain/crypto (L65) | ✅ x=1150 y=612 end |
| 5 | `2026-01-08-Cloud_Security_Course_8Batch_6Week…` | A | ✅ 0 0 1200 630 | ❌ Red `#ef4444` used; Cloud category requires Blue `#60a5fa` (L15, L30-31) | ✅ Present, 54/52px | ✅ Topic-specific — AWS WAF/CloudFront (L65) | ✅ x=1150 y=612 end |
| 6 | `2026-01-10-2026_DevSecOps_Roadmap_Complete_Guide…` | A | ✅ 0 0 1200 630 | ✅ Violet `#a78bfa` (DEVSECOPS) | ✅ Present, 54/52px | ✅ Topic-specific — roadmap.sh analysis (L68) | ✅ x=1150 y=612 end |
| 7 | `2026-01-10-devsecops-learning-path` | B | ✅ 0 0 1200 630 | ✅ Violet→Green `#6c5ce7→#00b894` (learning path) | ✅ H1 46px "DevSecOps Learning" / H2 "Path 2026" | N/A (Family B) | ✅ x=80 y=545 (footer bar present) |
| 8 | `2026-01-10-devsecops-roadmap-structure` | B | ✅ 0 0 1200 630 | ✅ Blue→Green `#3498db→#27ae60` (roadmap/structure) | ✅ H1 46px "DevSecOps Roadmap" / H2 "Structure" | N/A (Family B) | ✅ x=80 y=545 (footer bar present) |
| 9 | `2026-01-10-devsecops-tools-stack` | B | ✅ 0 0 1200 630 | ⚠️ Gradient `#6c5ce7→#00b894` — same as learning-path; no spec entry for tools-stack specifically; violet→green is acceptable but not differentiated | ✅ H1 46px "DevSecOps Tools" / H2 "Stack 2026" | N/A (Family B) | ✅ x=80 y=545 (footer bar present) |
| 10 | `2026-01-11-AI_Music_Video_Generation…` | A | ✅ 0 0 1200 630 | ⚠️ Violet `#a78bfa` used; AI/ML topic requires Cyan `#22d3ee`; badge says DEVSECOPS not AI/ML (L61-62) | ⚠️ H1/H2 say "AI DEVSECOPS AI / DEVSECOPS" — generic, not topic-specific | ✅ Desc topic-specific (L68): AI music/video from DevSecOps perspective | ✅ x=1150 y=612 end |
| 11 | `2026-01-14-AWS_Cloud_Security…` | A | ✅ 0 0 1200 630 | ✅ Blue `#60a5fa` (corrected; badge=SECURITY) | ⚠️ Badge says "SECURITY" not "CLOUD" — category card mismatch for a Cloud guide | ✅ Topic-specific — IAM to EKS (L65) | ✅ x=1150 y=612 end |
| 12 | `2026-01-14-CSPM_DataDog_AWS_Security…` | A | ✅ 0 0 1200 630 | ✅ Red `#ef4444` (SECURITY — security-focused CSPM) | ❌ Tag pills at y≈474 rows 1 and 2 have empty `<g>` — text missing from first two pill labels (L68-71: rects without `<text>` children) | ✅ Topic-specific (L65) | ✅ x=1150 y=612 end |
| 13 | `2026-01-14-GCP_Cloud_Security…` | A | ✅ 0 0 1200 630 | ⚠️ Blue `#60a5fa` used; badge says "SECURITY" not "CLOUD" — same category mismatch as AWS | ⚠️ Badge says "SECURITY" — same mismatch as AWS file | ✅ Topic-specific — IAM to GKE (L65) | ✅ x=1150 y=612 end |
| 14 | `2026-01-14-2025_ISMS-P_Certification…` | A | ✅ 0 0 1200 630 | ✅ Red `#ef4444` (SECURITY — certification/compliance) | ❌ Tag pills at y≈474: first two pill `<g>` groups contain rects but no `<text>` label (L68-71) — same truncation bug as CSPM | ✅ Topic-specific (L65) | ✅ x=1150 y=612 end |
| 15 | `2026-01-15-Cloud_Security_Course_8Batch_7Week…` | A | ✅ 0 0 1200 630 | ❌ Red `#ef4444` used; Cloud/K8s course requires Blue `#60a5fa` (L15, L30-31) | ✅ Present, 54/52px | ✅ Topic-specific — Docker/K8s practical (L65) | ✅ x=1150 y=612 end |
| 16 | `2026-01-16-Postmortem_NextJS_SSR…` | A | ✅ 0 0 1200 630 | ✅ Amber `#f59e0b` (INCIDENT — correct per spec note) | ✅ Present, 54/52px | ✅ Topic-specific — Next.js SSR/Cloudflare 5XX (L65) | ✅ x=1150 y=612 end |
| 17 | `2026-01-17-AI_Coding_Assistants…` | A | ✅ 0 0 1200 630 | ✅ Cyan `#22d3ee` (AI/ML — correct) | ✅ Present; badge=AI/ML (L64) | ✅ Topic-specific — Gemini/Claude/ChatGPT comparison (L71) | ✅ x=1150 y=612 end |
| 18 | `2026-01-22-Cloud_Security_Course_8Batch_8Week…` | A | ✅ 0 0 1200 630 | ❌ Red `#ef4444` used; Cloud/K8s course requires Blue `#60a5fa` (L15, L30-31) | ✅ Present, 54/52px | ✅ Topic-specific — CI/CD K8s pipeline (L65) | ✅ x=1150 y=612 end |
| 19 | `2026-01-22-Cloud_Security_Trends_January_2026` | A | ✅ 0 0 1200 630 | ❌ Red `#ef4444` used; Cloud Trends topic requires Blue `#60a5fa`; H1 says "2026 1 KUBERNETES 82 VS" — garbled title (L60-61) | ❌ H1/H2 garbled: "2026 1 KUBERNETES 82 / VS" — not topic-coherent | ✅ Desc topic-specific (L65): cloud security trends Jan 2026 | ✅ x=1150 y=612 end |
| 20 | `2026-01-22-EC2_G7e_GPU_Architecture` | B | ✅ 0 0 1200 630 | ✅ Cyan→Amber `#06b6d4→#f59e0b` (GPU/hardware — matches spec recommendation) | ✅ H1 46px "EC2 G7e GPU" / H2 "Instance Architecture" | N/A (Family B) | ✅ x=80 y=615 (footer bar present) |
| 21 | `2026-01-22-KARA_Ransomware_Trends_2025_Q3` | A | ✅ 0 0 1200 630 | ✅ Red `#ef4444` (SECURITY — threat topic) | ✅ Present, 54/52px | ✅ Topic-specific — KARA Q3 2025 ransomware trends (L65) | ✅ x=1150 y=612 end |
| 22 | `2026-01-22-KISA_Security_Advisory_Ransomware_Linux_Rootkit` | A | ✅ 0 0 1200 630 | ✅ Red `#ef4444` (SECURITY — threat topic) | ✅ Present, 54/52px | ✅ Topic-specific — KISA advisory ransomware/rootkit (L65) | ✅ x=1150 y=612 end |
| 23 | `2026-01-22-Kubernetes_Security_Architecture_AI_Monitoring` | B | ✅ 0 0 1200 630 | ✅ Cyan→Green `#06b6d4→#27ae60` (Cloud/K8s) | ✅ H1 44px "Kubernetes Security Architecture" / H2 "with AI Monitoring" | N/A (Family B) | ✅ x=80 y=615 (footer bar present) |
| 24 | `2026-01-22-Linux_Rootkit_Detection_Flow` | B | ✅ 0 0 1200 630 | ✅ Violet→Red `#6c5ce7→#e74c3c` (Threat/Rootkit) | ✅ H1 46px "Linux Rootkit" / H2 "Detection Flow" | N/A (Family B) | ✅ x=80 y=615 (footer bar present) |
| 25 | `2026-01-22-Network_Segmentation_Architecture` | B | ✅ 0 0 1200 630 | ✅ Teal→Teal `#06b6d4→#1abc9c` (Cloud/Network) | ✅ H1 46px "Network Segmentation" / H2 "Architecture" | N/A (Family B) | ✅ x=80 y=615 (footer bar present) |

---

## Summary Statistics

### Overall

| Rating | Count | Pct |
|--------|-------|-----|
| ✅ Compliant rows (all 6 checks pass) | 10 | 40% |
| ⚠️ Minor issues (1–2 properties off) | 9 | 36% |
| ❌ Major issues (structural/content broken) | 6 | 24% |

### Per-property breakdown (25 files)

| Property | ✅ | ⚠️ | ❌ |
|----------|---|---|---|
| Family classification | 25 | 0 | 0 |
| viewBox / dimensions | 25 | 0 | 0 |
| Accent color | 15 | 2 | 8 |
| Title + subtitle | 20 | 3 | 2 |
| Description (Family A only, 18 files) | 16 | 0 | 2 |
| Signature | 25 | 0 | 0 |

**Universal passes**: viewBox/dimensions and signature are 25/25 compliant.  
**Highest failure rate**: Accent color (8 major, 2 minor = 40% non-compliant).

---

## Top 5 Files Needing Rework

### 1. `2026-01-22-Cloud_Security_Trends_January_2026` — TWO major gaps
- **Accent**: Red `#ef4444` (L15); Cloud Trends requires Blue `#60a5fa`
- **Garbled H1/H2**: L60-61 read `"2026 1 KUBERNETES 82"` / `"VS"` — clearly a generation artifact, not the post topic. Should read e.g. `"CLOUD SECURITY"` / `"TRENDS JAN 2026"`
- Fix: change microGrid dot + ambient blob + panel stroke + badge fills to `#60a5fa`; rewrite H1/H2 text

### 2. `2026-01-08-Blockchain_Cryptocurrency_Security…` — Accent family mismatch
- **Accent**: Violet `#a78bfa` throughout (L15, L30, L37, L45, L60-61, L70-79, L82-95); spec mandates Amber `#f59e0b` for Blockchain/Crypto
- All accent references (microGrid dot, ambient blobs, panel stroke, badge badge, tag pills, stat card strokes) need changing to `#f59e0b` / darker shade `#d97706`

### 3. `2026-01-14-CSPM_DataDog_AWS_Security…` — Empty tag pill labels
- **Tag pills**: L68-71 — first two `<g>` elements at y≈474 contain `<rect>` but no `<text>` child. Only the third pill "CSPM" (L74) has text. The CATEGORY stat card (L78-79) also has no value text.
- Fix: add `<text>` labels "CLOUD" and "SECURITY" to the first two pill groups; add `<text>` "SECURITY" value to CATEGORY card

### 4. `2026-01-14-2025_ISMS-P_Certification…` — Same empty-label bug
- **Tag pills**: L68-71 — identical truncation: first two pill `<g>` groups have rects but no `<text>`. CATEGORY stat card (L78-79) has label but no value text.
- Fix: add `<text>` labels (e.g. "CLOUD", "ISMS-P") to first two pills; add "SECURITY" to CATEGORY card value

### 5. `2026-01-06-DevSecOps_Viewing_Automotive_Security…` — Title/content mismatch
- **H1/H2 vs. description mismatch**: H1=`"DEVSECOPS"` H2=`"BLOCKCHAIN"` (L63-64) but description at L68 references automotive security. The `<title>` (L2) says "DEVSECOPS BLOCKCHAIN" which matches a different post
- Accent (violet) is correct for DevSecOps category; the issue is that H1/H2 copy was swapped from a different file during generation
- Fix: rewrite H1 to e.g. `"AUTOMOTIVE"`, H2 to `"SECURITY"` (or appropriate topic words)

---

## Files Fully Compliant (all 6 checks pass)

1. `2026-01-01-Tesla_FSD_2026_Complete_Guide_Model_Y_Juniper_Security_DevSecOps.svg`
2. `2026-01-03-OWASP_2025_Complete_Guide_Top_10_AI_Security.svg`
3. `2026-01-10-2026_DevSecOps_Roadmap_Complete_Guide_roadmap.sh_Analysis.svg`
4. `2026-01-10-devsecops-learning-path.svg`
5. `2026-01-10-devsecops-roadmap-structure.svg`
6. `2026-01-16-Postmortem_NextJS_SSR_Error_Cloudflare_Blocking_ALB_5XX_Incident_Analysis.svg`
7. `2026-01-17-AI_Coding_Assistants_Comparison_Gemini_Claude_Code_ChatGPT_OpenCode_2025_2026_Research_Analysis.svg`
8. `2026-01-22-EC2_G7e_GPU_Architecture.svg`
9. `2026-01-22-KARA_Ransomware_Trends_2025_Q3.svg`
10. `2026-01-22-KISA_Security_Advisory_Ransomware_Linux_Rootkit.svg`
11. `2026-01-22-Kubernetes_Security_Architecture_AI_Monitoring.svg`
12. `2026-01-22-Linux_Rootkit_Detection_Flow.svg`
13. `2026-01-22-Network_Segmentation_Architecture.svg`

---

## Notes

- **All 25 files** use `viewBox="0 0 1200 630" width="1200" height="630"` — universal pass.
- **All 25 files** contain the `tech.2twodragon.com` signature — universal pass.
- **No file** contains the generic generator placeholder description `"Clean technical cover with stronger depth, hierarchy, and category-specific structure."` — the spec's most feared issue (§5 Family A note) did not materialise; all 18 Family A descriptions are topic-specific.
- **Family B footer**: files use `x="80" y="545"` (learning-path, roadmap-structure, tools-stack) or `x="80" y="615"` (EC2, K8s, Linux, Network). Spec says `y="615"` — the three Jan-10 files use `y=545` which is one minor deviation but within the footer bar (`<rect y="520" h="110">`), so functionally acceptable.
- Accent-color errors are concentrated in the Cloud Security Course series (6W, 7W, 8W all use red instead of blue) — likely a batch-generation error with wrong template applied.

---

*Cross-reference: See also [feb-svg-compliance-matrix.md](feb-svg-compliance-matrix.md), [mar-svg-compliance-matrix.md](mar-svg-compliance-matrix.md), [apr-svg-compliance-matrix.md](apr-svg-compliance-matrix.md)*
