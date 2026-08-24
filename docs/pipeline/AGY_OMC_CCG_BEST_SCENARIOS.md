# AGY + OMC + CCG Multi-Agent Orchestration & Best Scenarios Guide

> **Production Guide**: Google Antigravity (AGY), Oh-My-Claude / OpenCode (OMC), and Claude-Codex-Gemini (CCG) Tri-Model Pipeline Integration.

---

## 1. Executive Summary & Architecture

This repository (`Twodragon0/tech-blog`) operates an enterprise-grade, multi-agent AI collaboration lane that combines three complementary AI platforms:

1. **Google Antigravity (AGY)**:
   - System orchestrator, background task management, slash command engine (`/goal`, `/schedule`, `/plan`, `/grill-me`, `/teamwork-preview`, `/learn`), and native test/validation gatekeeper.
   - Built on top of high-speed Gemini engines (Flash & Pro) with 1M+ context window and free OAuth allocations.

2. **Oh-My-Claude / OpenCode (OMC)**:
   - Multi-agent cognitive network featuring specialized personas (`architect`, `analyst`, `planner`, `debugger`, `executor`, `verifier`, `security-reviewer`, `code-reviewer`, `test-engineer`, `writer`, `critic`).
   - Autonomous execution loops: `autopilot`, `ralph` / `sisyphus` (continuous loop until quality promise is satisfied), `ultrawork` (parallel execution lanes), and `ralplan` (consensus architecture planning).

3. **CCG Tri-Model Lane (Claude + Codex + Gemini)**:
   - **Claude**: Lead architect, content synthesizer, DevSecOps domain tone, and Mermaid visual diagrams.
   - **Codex (GPT-5.4 / OpenAI Engine)**: AST syntax integrity, strict Python scripts, regex expressions, CI YAML configs, and unit test generation.
   - **Gemini**: 1M+ repository context search, CVE advisories, upstream RFC/vendor updates, and zero-cost high-volume batch analysis.

```
                    ┌─────────────────────────────────────────┐
                    │       AGY Orchestration Platform        │
                    │   (Slash Commands & System Runners)     │
                    └────────────────────┬────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌─────────────────┐             ┌─────────────────┐              ┌─────────────────┐
│  OMC / Claude   │             │      Codex      │              │  AGY / Gemini   │
├─────────────────┤             ├─────────────────┤              ├─────────────────┤
│ • Lead Architect│             │ • Syntax Rigor  │              │ • 1M+ Context   │
│ • Korean Tone   │             │ • Script Safety │              │ • Upstream CVEs │
│ • Mermaid Diags │             │ • Pytest AST    │              │ • Free Quota    │
└────────┬────────┘             └────────┬────────┘              └────────┬────────┘
         │                               │                                │
         └───────────────────────────────┼────────────────────────────────┘
                                         ▼
                    ┌─────────────────────────────────────────┐
                    │        Zero-Regression Local Gate       │
                    │ (check_posts -> Pytest -> Git Commit)   │
                    └─────────────────────────────────────────┘
```

---

## 2. Model & Tier Hierarchy

| Tier | Engine / Model | Role & Scope | Cost Basis |
|---|---|---|---|
| **Tier 0** | **AGY Native Runner** | Local command execution, background task runner, file validation | Free / Local CPU |
| **Tier 0** | **Gemini CLI (OAuth) / AGY** | 1M+ codebase search, CVE database querying, broad web reconnaissance | Free OAuth Quota |
| **Tier 1** | **Claude Code & OMC** | Multi-agent orchestration, architectural design, high-depth drafting | Anthropic Plan |
| **Tier 1** | **CCG Tri-Model Lane** | Tri-model synthesis, peer-review & fact-checking consensus | Coordinated Subagents |
| **Tier 2** | **Codex / OpenAI Engine** | AST correctness, regex validation, security detection rules (Falco/Sigma/Rego) | Pay per call |
| **Tier 2** | **DeepSeek API (Cache)** | Context-cached bulk drafting & news summarization (`api/chat.js`) | Low cost tokens |

---

## 3. The 6 Master Execution Scenarios

### Scenario 1: End-to-End DevSecOps Technical Post Creation
- **Trigger**: User requests a new technical post or topic keyword.
- **Protocol**:
  1. **AGY Recon**: Check existing `_posts/` to avoid duplication. Recommend `/plan` or `/grill-me` if scope needs clarification.
  2. **Gemini Recon**: Search upstream RFCs, AWS/Kubernetes release notes, and security advisories.
  3. **Claude Drafting**: Compose Markdown in `_posts/YYYY-MM-DD-English_Title.md` with:
     - Minimum 3,000+ characters of substantial depth.
     - At least 1 Mermaid architecture diagram and 2+ comparison tables.
     - Actionable implementation checklist.
     - Date set to `HH >= 09:00:00 +0900` (UTC timezone rule).
     - **NO FAQ sections** or `FAQPage` JSON-LD schema.
  4. **Codex Audit**: Verify all code blocks (YAML, Bash, Python) for syntax correctness.
  5. **AGY Local Gate**:
     ```bash
     python3 scripts/generate_post_images.py --post _posts/YYYY-MM-DD-English_Title.md
     python3 scripts/check_posts.py
     python3 scripts/fix_links_unified.py --fix
     python3 scripts/check_kst_midnight.py
     ```

### Scenario 2: Autonomous Continuous Post Improvement (Ralph / Sisyphus Loop)
- **Trigger**: Quality modernization sweep or user running `/goal` / `/improve-posts`.
- **Protocol**:
  1. **AGY Goal Activation**: Trigger `/goal` for overnight autonomous processing.
  2. **Candidate Discovery**: `python3 scripts/validate_post_quality.py --all --threshold 85`.
  3. **OMC Ralph Loop**: Dispatches `explore` -> `writer` -> `critic` -> `verifier` with completion promise `POSTS_IMPROVED`.
  4. **CCG Upgrade**: Gemini brings 2026 specs, Claude enriches technical depth, Codex updates CLI commands.
  5. **AGY Validation Gate**: `.venv/bin/pytest scripts/tests/ --cov-fail-under=40` and atomic git commit without `Co-Authored-By`.

### Scenario 3: Daily DevSecOps News Pipeline & Auto-Publishing
- **Trigger**: Automated schedule via AGY `schedule` cron or GitHub Actions.
- **Protocol**:
  1. **Feed Aggregation**: `python3 scripts/collect_tech_news.py --hours 24`.
  2. **OMC Classifier**: `scripts/news/analyzer.py` scores articles for security/cloud relevance.
  3. **Draft / Publish**: `python3 scripts/auto_publish_news.py` or `python3 scripts/generate_news_draft.py --use-ai`.
  4. **Codex & Test Gate**: `.venv/bin/pytest scripts/tests/test_news_templates.py`.
  5. **Verification**: `python3 scripts/verify_images_unified.py --all`.

### Scenario 4: Fast-Track Zero-Day CVE & Emergency Incident Analysis
- **Trigger**: Breaking CVE advisory (CVSS >= 8.0) or production outage post-mortem.
- **Protocol**:
  1. **Gemini Recon**: Ingest CVE details, CVSS v3/v4 vectors, attack mechanisms, and vendor advisories.
  2. **Codex Detection Rules**: Generate Falco rule, Sigma rule, Rego policy, or K8s Admission Webhook.
  3. **Claude Write-Up**: Compose Incident post with Mermaid attack sequence diagram, Root Cause Analysis, and emergency checklist.
  4. **AGY Gate**: Generate English-only SVG cover, validate structure, and commit.

### Scenario 5: Automation Script Engineering & Tool Modernization
- **Trigger**: Developing new Python utilities in `scripts/` or updating CI workflows.
- **Protocol**:
  1. **OMC Architect**: Define interface and requirements.
  2. **Codex Generator**: Write clean Python code with type hints, Google docstrings, and strict regex.
  3. **Gemini Review**: Verify secret masking (`scripts.lib.security.mask_sensitive_info`) and memory efficiency.
  4. **AGY Pytest Runner**: `.venv/bin/pytest scripts/tests/`, `ruff check scripts/ --fix`, and `mypy scripts/`.

### Scenario 6: Zero-Debt Repository Quality & Security Audit
- **Trigger**: Pre-release verification, `/team-audit`, or weekly security health check.
- **Protocol**:
  1. **Security & Quota Scan**: `npm audit`, `bundle audit`, `./scripts/monitor_sentry_quota.sh`.
  2. **Structural & Image Audit**: `python3 scripts/check_posts.py`, `python3 scripts/verify_images_unified.py --all`.
  3. **Pre-Commit Hooks Gate**: `bash scripts/install-hooks.sh`.

---

## 4. Antigravity Slash Commands & Interaction Matrix

| Slash Command | Best Matching Workflow | Recommended Action |
|---|---|---|
| `/goal` | Autonomous continuous improvement (Scenario 2) | Agent persists until all candidate posts achieve 90+ quality score. |
| `/schedule` | Recurring news collection & health checks (Scenario 3, 6) | Sets background cron or timers for non-blocking automation. |
| `/plan` | Complex architecture & multi-file refactoring (Scenario 5) | Generates phased execution plans before modifying code. |
| `/grill-me` | Pre-writing requirements clarification (Scenario 1) | Interactive interview to align on post tone, scope, and target architecture. |
| `/teamwork-preview` | Multi-agent parallel task execution (Scenario 5, 6) | Previews role allocations across subagents before dispatch. |
| `/learn` | Retaining project conventions after critical bugfixes | Stores learned guidelines in agent memory. |

---

## 5. Security & Masking Standards

- **Strict No-Secrets Rule**: Never commit API keys, tokens, or private endpoints.
- **Masking Function**: All stdout and error logs processing external text must wrap data with `scripts.lib.security.mask_sensitive_info()`.
- **Commit Cleanliness**: Never include `Co-Authored-By: Claude` or unverified AI tags in git commits.
