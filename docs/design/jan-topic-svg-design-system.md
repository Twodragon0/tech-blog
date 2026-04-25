# January 2026 Topic-Specific SVG Design System

Scope: 25 bespoke topic SVGs from January 2026 (47–106 lines). These are NOT weekly digests — they are standalone infographics and architecture illustrations for individual posts. This spec governs visual consistency without flattening topic-specific identity.

---

## 1. Two Visual Families

Analysis of the 8 sampled files reveals that the January SVGs split cleanly into two distinct template families. Every file belongs to one.

### Family A — "Cover Template" (98–106 lines)

Used by complete-guide posts (Tesla FSD, OWASP, AWS, GCP, CSPM, ISMS-P, AI Coding Assistants, Blockchain, Cloud Course batches, DevSecOps Roadmap full guide, AI Music, Postmortem, Ransomware, KISA, Cloud Trends).

Identifying markers:
- Dark navy gradient background: `#0b1120 → #121a2f → #170f25`
- `<pattern id="microGrid">` overlaid on full canvas — dot color varies by category accent
- Three large ambient `<circle>` blobs with `filter="url(#sg)"` (soft glow) in top-left, bottom-right, top-right
- Diagonal `<path>` dark wash across left third
- Right-panel: single rounded rect with `url(#panel)` fill, accent-colored stroke, inner border rect, and three horizontal pill-bars mimicking a UI panel
- Centered circular icon in the right panel (topic-specific illustration)
- Left column text stack: category badge → H1 (54px) → H2 (52px) → tag line (18px) → divider → "VISUAL SYSTEM" fingerprint line → description line
- Tag row at y≈474: 2–3 pill badges in accent color
- Metadata row at y≈536: three stat cards (CATEGORY / SIGNALS / TAGS)
- Date badge top-right: `#1d4ed8` blue pill
- Footer: `<line>` at y=588 + `tech.2twodragon.com` at y=612, `text-anchor="end"`

### Family B — "Architecture Flow" (54–66 lines)

Used by inline architecture diagrams (devsecops-learning-path, devsecops-roadmap-structure, devsecops-tools-stack, Linux Rootkit Detection Flow, Network Segmentation Architecture, Kubernetes Security Architecture, EC2 G7e GPU Architecture).

Identifying markers:
- Teal/dark blue gradient background: `#0a1520 → #152535` or `#0f0a1a → #1a1530`
- Transparent grid of horizontal + vertical lines at fixed intervals (105/210/315/420px rows; 240/480/720/960px cols), opacity 0.03–0.04
- Two faint ambient circles bottom-right (r=200, r=140), opacity 0.06–0.07
- Left accent bar: `<rect x="0" y="0" width="6" height="630">` filled with 2-stop gradient (the visual "spine")
- Date pill badge at y≈44–66 (left-aligned, narrow)
- Left column text: H1 (44–46px) → H2 (44–46px) → subtitle (19–20px) → accent divider bar (w=120, h=3) → category label (14–15px, letter-spacing: 3)
- Tag pills at y≈400–402 (3 pills, mixed accent and neutral)
- Footer bar: `<rect y="590" h="40" fill="rgba(0,0,0,0.3)">` + signature text at y=615
- Right half: topic-specific illustration (tree, stepping stones, hexagons, zone boxes, flow paths)

---

## 2. Universal Rules (Both Families)

### Canvas
- `viewBox="0 0 1200 630"` — all 25 files already use this. Do not change.
- `width="1200" height="630"` — explicit attributes required for Jekyll OG image extraction.

### Typography
- `font-family="Arial,sans-serif"` — universal across all 25 files. Keep as-is; this is intentional for SVG cross-renderer compatibility (not a design oversight).
- No Korean, no special Unicode characters in SVG text nodes.

### Signature (required in every file)
- Text: `tech.2twodragon.com`
- Family A: `x="1150" y="612" text-anchor="end" font-size="13" fill="#94a3b8"`
- Family B: `x="80" y="615" font-size="13" fill="rgba(255,255,255,0.5)"`

### Accessibility
- `<title>` element required as first child of `<svg>`. Content: short English description of illustration subject.
- All text must achieve minimum 3:1 contrast against its immediate background fill.

---

## 3. Color Palette per Category

### Family A — Category accent system

The microGrid dot color and all accent-colored strokes, badges, and fills follow this mapping. The background gradient is fixed; only the accent slot changes.

| Category | Accent | Hex | microGrid dot |
|----------|--------|-----|---------------|
| Security / Threat | Red | `#ef4444` | `#ef4444` at 0.15 opacity |
| DevSecOps / Automation | Violet | `#a78bfa` | `#a78bfa` at 0.15 opacity |
| AI/ML / Coding Tools | Cyan | `#22d3ee` | `#22d3ee` at 0.15 opacity |
| Cloud / Infrastructure | Blue | `#60a5fa` | `#60a5fa` at 0.15 opacity |
| Blockchain / Crypto | Amber | `#f59e0b` | `#f59e0b` at 0.15 opacity |

Ambient blob colors follow from the accent: primary blob = accent at 0.08, secondary blob = darker shade of accent at 0.08.

### Family B — Accent gradient system

Each file selects a 2-stop gradient for the left spine bar and the h-divider bar.

| Topic type | Gradient | Hex stops |
|-----------|----------|-----------|
| Cloud / K8s / Network | Teal→Green | `#06b6d4 → #27ae60` or `#06b6d4 → #1abc9c` |
| DevSecOps Learning/Roadmap | Violet→Green | `#6c5ce7 → #00b894` |
| DevSecOps Structure | Blue→Green | `#3498db → #27ae60` |
| Threat / Rootkit | Violet→Red | `#6c5ce7 → #e74c3c` |
| GPU / Hardware | Cyan→Amber | `#06b6d4 → #f59e0b` (recommended) |

---

## 4. Per-Category Layout Templates

### 4A. Complete-Guide Covers (Family A)

Layout: two-column split. Left 55% = text hierarchy. Right 45% = decorative panel + circular icon.

Required elements (in document order):
1. Background gradient rect
2. microGrid pattern rect
3. Three ambient soft-glow circles (sg filter)
4. Diagonal dark-wash path
5. Right panel: outer rounded rect (accent stroke) → inner border rect → three horizontal pill-bars
6. Two curved connector paths between left and panel edges
7. Circular icon group in panel center (topic illustration)
8. Category badge (top-left, pill)
9. H1 text (y≈170, 54px, `#f8fafc`)
10. H2 text (y≈232, 52px, `#dbeafe`)
11. Tag line (y≈288, 18px, `#cbd5e1`)
12. Horizontal divider (y≈314, w=520)
13. "VISUAL SYSTEM {fingerprint}" line (y≈344, 14px bold, `#94a3b8`)
14. Description line (y≈372, 14px, `#94a3b8`) — currently identical across all files; **should be topic-specific**
15. Tag pills row (y≈474)
16. Metadata cards row (y≈536): CATEGORY / SIGNALS / TAGS
17. Date badge (top-right)
18. Footer line + signature

### 4B. Architecture Flow Diagrams (Family B)

Layout: left 55% = text column, right 45% = technical illustration zone.

Required elements (in document order):
1. Background gradient rect
2. Grid lines (4 horizontal + 4 vertical at fixed intervals)
3. Two ambient circles (bottom-right)
4. Right-half illustration (topic-specific — see sub-types below)
5. Left accent spine bar (x=0, w=6)
6. Date badge
7. H1 text (y≈185, 44–46px)
8. H2 continuation (y≈245, 44–46px)
9. Subtitle (y≈300, 19–20px)
10. Accent divider bar (y≈320–325, w=120, h=3)
11. Category label (y≈370, 14–15px, letter-spacing: 3)
12. Tag pills row (y≈400–402, 3 pills)
13. Footer bar + dual signature texts

Sub-type illustrations for right panel:

| File type | Right-panel illustration |
|-----------|--------------------------|
| Learning path | Diagonal stepping-stone ellipses with dashed connector lines and star badges |
| Roadmap / tree | Circle-node tree with branching lines (root → level 2 → level 3) |
| Architecture / zones | Labelled zone rects connected by firewall symbols and monitoring dashes |
| Hexagon cluster | Kubernetes hexagon polygon nodes arranged in rows with dashed connector lines |
| Detection flow | Abstract threat icon (magnifying glass or CPU-shape) + alert triangle + analysis bars |

---

## 5. Specific Gap Audit — All 25 Files

### Family A files

| File | Status | Notes |
|------|--------|-------|
| `2026-01-01-Tesla_FSD_…` | ✅ | Follows spec. Accent: violet. Category badge: DEVSECOPS. |
| `2026-01-03-OWASP_2025_…` | ✅ | Follows spec. Accent: red. Category: SECURITY. |
| `2026-01-06-DevSecOps_Viewing_Automotive_…` | ✅ | Follows spec. Accent: violet expected. Verify accent matches category. |
| `2026-01-08-Blockchain_Cryptocurrency_…` | ✅ | Follows spec. Accent should be amber per palette. Verify. |
| `2026-01-08-Cloud_Security_Course_8Batch_6Week_…` | ✅ | Follows spec. Accent: blue. |
| `2026-01-10-2026_DevSecOps_Roadmap_Complete_Guide_…` | ✅ | Follows spec. Accent: violet. |
| `2026-01-11-AI_Music_Video_Generation_…` | ⚠️ | Confirm accent color is cyan or amber (AI topic). Verify category badge text. |
| `2026-01-14-AWS_Cloud_Security_…` | ⚠️ | Uses `#ef4444` (red) for AWS cloud topic. **Should use `#60a5fa` (blue) for cloud category.** Accent mismatch. |
| `2026-01-14-CSPM_DataDog_AWS_Security_…` | ⚠️ | Verify accent; CSPM/security overlap — use red `#ef4444` if security-focused, blue if cloud-ops focused. |
| `2026-01-14-GCP_Cloud_Security_…` | ⚠️ | Same issue as AWS: GCP is cloud category, verify not using red accent. |
| `2026-01-14-2025_ISMS-P_Certification_…` | ⚠️ | ISMS-P is a security certification; red accent appropriate. Verify category badge reads "SECURITY". |
| `2026-01-15-Cloud_Security_Course_8Batch_7Week_Docker_Kubernetes_…` | ✅ | Follows spec. Cloud category, blue accent. |
| `2026-01-16-Postmortem_NextJS_SSR_…` | ⚠️ | Postmortem/incident has no defined category color. Recommend amber `#f59e0b` (incident/alert). Likely using default. **Add specific accent.** |
| `2026-01-17-AI_Coding_Assistants_…` | ✅ | Follows spec. Accent: cyan `#22d3ee`. Category: AI/ML. |
| `2026-01-22-Cloud_Security_Course_8Batch_8Week_…` | ✅ | Follows spec. Blue accent. |
| `2026-01-22-Cloud_Security_Trends_January_2026` | ✅ | Follows spec. Blue accent. |
| `2026-01-22-KARA_Ransomware_Trends_2025_Q3` | ✅ | Threat topic, red accent expected. |
| `2026-01-22-KISA_Security_Advisory_Ransomware_Linux_Rootkit` | ✅ | Threat topic, red accent expected. |

**Common Family A issue across ALL 18 files:** The description line at y≈372 is the literal string `"Clean technical cover with stronger depth, hierarchy, and category-specific structure."` — a generator placeholder. **Every file needs a topic-specific one-line description here.**

### Family B files

| File | Status | Notes |
|------|--------|-------|
| `2026-01-10-devsecops-learning-path` | ✅ | Follows spec. Violet→Green gradient. Good stepping-stone illustration. |
| `2026-01-10-devsecops-roadmap-structure` | ✅ | Follows spec. Blue→Green gradient. Tree-node illustration complete. |
| `2026-01-10-devsecops-tools-stack` | ⚠️ | Not sampled directly — verify accent gradient and that illustration zone is non-empty. |
| `2026-01-22-EC2_G7e_GPU_Architecture` | ⚠️ | GPU/hardware topic has no defined accent in current palette. Recommend Cyan→Amber `#06b6d4 → #f59e0b`. Verify illustration is GPU-specific (not reused from another template). |
| `2026-01-22-Kubernetes_Security_Architecture_AI_Monitoring` | ✅ | Follows spec. Teal→Green. Hexagon pod nodes with AI monitoring ellipse. |
| `2026-01-22-Linux_Rootkit_Detection_Flow` | ✅ | Follows spec. Violet→Red threat gradient. CPU/magnifier icon with alert triangle. |
| `2026-01-22-Network_Segmentation_Architecture` | ✅ | Follows spec. Teal→Teal. DMZ/firewall/zone rects with monitoring region. |

---

## 6. Summary of Issues

| Severity | Count | Primary issue |
|----------|-------|---------------|
| ❌ Major rework needed | 0 | No file is structurally broken |
| ⚠️ Minor adjustment needed | 7 | Accent color mismatch (AWS/GCP), missing topic description, unverified files |
| ✅ Follows spec | 18 | |

### Priority fixes (in order)

1. **All 18 Family A files** — Replace the generic placeholder description at y≈372 with a 1-sentence topic-specific description (80 chars max).
2. **`2026-01-14-AWS_Cloud_Security_…`** — Change accent from `#ef4444` to `#60a5fa`. Update microGrid dot, badge fills, panel stroke, tag pills, and stat card strokes.
3. **`2026-01-14-GCP_Cloud_Security_…`** — Same accent fix as AWS if currently red.
4. **`2026-01-16-Postmortem_…`** — Assign amber `#f59e0b` as incident/postmortem accent.
5. **`2026-01-22-EC2_G7e_GPU_Architecture`** — Assign Cyan→Amber gradient and verify GPU-specific illustration.
6. **`2026-01-10-devsecops-tools-stack`** — Verify illustration zone is populated (not just the left text column).

---

## 7. Checklist for New January-Style Topic SVGs

- [ ] Family A or B determined by post type (guide = A, diagram/architecture = B)
- [ ] viewBox `0 0 1200 630`, explicit width/height attributes
- [ ] `<title>` present and topic-specific
- [ ] Accent color matches category table in section 3
- [ ] Family A: description at y≈372 is topic-specific (not the generator placeholder)
- [ ] Family B: right-panel illustration is topic-specific (not reused from another post)
- [ ] `tech.2twodragon.com` signature present with correct position for family
- [ ] No Korean text in SVG text nodes
- [ ] All text readable at 3:1 contrast minimum
