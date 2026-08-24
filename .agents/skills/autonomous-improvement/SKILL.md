---
name: autonomous-improvement
description: >-
  Autonomous continuous improvement and modernization loop for tech blog posts.
  Combines AGY Goal mode, OMC Ralph/Sisyphus loop, and CCG tri-model enhancement
  to systematically raise post quality scores above 90+.
---

# Autonomous Continuous Post Improvement Runbook (AGY + OMC + CCG)

This skill orchestrates autonomous, long-running quality modernization loops across the Jekyll blog post library.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   AGY Orchestrator (/goal mode)                        │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 1: Discovery & Quality Scoring (validate_post_quality.py)       │
│  - Filter posts with Score < 85 or missing checklists / tables / SVGs  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 2: OMC Ralph / Sisyphus Loop Execution                          │
│  - Promise: POSTS_IMPROVED                                             │
│  - Subagent Lanes: Explore -> Writer -> Critic -> Verifier             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Gemini 1M Ctx   │       │  Claude (OMC)    │       │  Codex Rigor     │
│  - Upstream RFCs │       │  - Technical RCA │       │  - AST Code      │
│  - 2026 Updates  │       │  - Mermaid Diags │       │  - Regex & Pytest│
└────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Phase 3: Verification & Atomic Gate                                   │
│  - check_posts.py + fix_links_unified.py + verify_images_unified.py    │
│  - .venv/bin/pytest scripts/tests/ --cov-fail-under=40                 │
│  - Atomic commit without Co-Authored-By                                │
└────────────────────────────────────────────────────────────────────────┘
```

## Quality Score Criteria

Every improved post MUST satisfy the following thresholds:
| Metric | Target Threshold | Description |
|---|---|---|
| **Content Length** | >= 3,000 chars | Comprehensive technical depth |
| **Tables** | >= 2 tables | Comparison, configuration, or checklist tables |
| **Code Blocks** | >= 1 block | Validated syntax with language tags |
| **Checklist** | >= 1 checklist | Actionable production verification steps |
| **Visual / Mermaid** | >= 1 diagram | Architecture or flow visualization |
| **Front Matter** | Valid | Date (HH >= 09:00), category, English image |
| **No FAQ Section** | 100% compliant | Absolutely NO FAQ or FAQPage schema |

## Step-by-Step Execution Scenario

### 1. AGY Task Initiation
When running autonomous multi-post modernization, recommend or trigger the `/goal` slash command:
```bash
# Scan and identify candidate posts needing improvement
python3 scripts/validate_post_quality.py --all --threshold 85
```

### 2. Multi-Model Enhancement (CCG)
- **Gemini Phase**: Check latest upstream specifications (e.g. CNCF, AWS, Kubernetes, NIST) and replace outdated practices.
- **Claude Phase**: Refactor post structure, add Mermaid architecture diagrams, write in natural professional Korean DevSecOps tone.
- **Codex Phase**: Audit YAML/Python/Bash snippets for syntax validity and modernize CLI commands (e.g. kubectl, terraform, docker).

### 3. Image & Cover Verification
- Ensure English-only SVG cover exists at `/assets/images/YYYY-MM-DD-English_Title.svg`.
- Run image verification:
```bash
python3 scripts/verify_images_unified.py --all
```

### 4. Zero-Regression Gate & Verification
```bash
# Run structural and link validation
python3 scripts/check_posts.py
python3 scripts/fix_links_unified.py --fix
python3 scripts/check_kst_midnight.py

# Run unit tests
.venv/bin/pytest scripts/tests/ --cov-fail-under=40
```

### 5. Git Commit Protocol
- Atomic commit per improved batch:
```bash
git add _posts/ assets/images/
git commit -m "perf(posts): improve technical depth, architecture diagrams and quality scores for batch"
```
- **Rule**: Never include `Co-Authored-By: Claude` or unmasked secrets.
