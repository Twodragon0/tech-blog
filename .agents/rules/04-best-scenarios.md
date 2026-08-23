# AGY + OMC + CCG Best Scenarios & Orchestration Matrix

This document defines the 6 battle-tested best execution scenarios utilizing **AGY (Google Antigravity Platform)**, **OMC (Oh-My-Claude / OpenCode Multi-Agent Framework)**, and **CCG (Claude + Codex + Gemini Tri-Model Lane)**.

---

## Tool & Model Hierarchy Matrix

| Tool / Platform | Primary Roles | Best Match Tasks | Cost & Resource Basis |
|---|---|---|---|
| **AGY Native** | System Orchestrator, CLI Runner, Git, Background Tasks, Subagents | Local tests (`pytest`), build scripts, background timers, SVG gates | Free / Local CPU |
| **Gemini (AGY / 2.5/3.7)** | 1M+ Long Context, Fact-Checking, Research, Diff Search | CVE recon, RFC analysis, 100+ post scans, zero-cost high-volume calls | Free Tier / OAuth CLI |
| **OMC (Claude Code / OpenCode)** | Multi-Agent Team, Sisyphus / Ralph Loop, Content Architecture | Technical drafting, deep DevSecOps analysis, Korean technical tone | Tier 1 (Subscription) |
| **Codex (GPT-5.4 / OpenAI Engine)** | AST Code Rigor, Script Engineering, Regex Hardening | Python utilities, GitHub Actions workflows, test mocks, regex checks | Tier 2 (Targeted) |

---

## Master Scenarios Playbook

### Scenario 1: New Technical Blog Post Creation (CCG Tri-Lane)
- **Goal**: Produce a high-depth (3000+ chars), zero-hallucination DevSecOps / Cloud post.
- **Workflow**:
  1. **AGY Recon**: Check existing `_posts/` to prevent duplicate topics. Recommend `/plan` or `/grill-me` if topic scope needs alignment.
  2. **Gemini Recon**: Fetch latest vendor specs, Kubernetes/AWS advisories, and RFC docs.
  3. **Claude Drafting**: Compose post with Korean technical tone, Mermaid architecture diagrams, tables, and implementation checklist.
  4. **Codex Audit**: Review code snippets, configuration YAMLs, and shell commands for syntax validity.
  5. **AGY Gate**: Generate English-only SVG cover, run `scripts/check_posts.py`, `scripts/fix_links_unified.py --fix`, and check timezone compliance (`HH >= 09:00 +0900`).

### Scenario 2: Autonomous Continuous Post Improvement (OMC Ralph Loop + AGY Goal Mode)
- **Goal**: Systematically raise quality score across all existing posts to 90+.
- **Workflow**:
  1. **AGY Goal Mode**: Recommend or trigger `/goal` for autonomous long-running execution.
  2. **Discovery**: `python3 scripts/validate_post_quality.py --all --threshold 85` generates candidates.
  3. **OMC Ralph Loop**: Iterates with promise `POSTS_IMPROVED` (Length >= 3000, 2+ tables, 1+ code block, 1+ checklist).
  4. **CCG Upgrade**: Gemini provides updated 2026 specs, Claude enriches architecture, Codex validates code blocks.
  5. **AGY Gate**: `.venv/bin/pytest scripts/tests/ --cov-fail-under=40` and atomic git commit without `Co-Authored-By`.

### Scenario 3: Daily DevSecOps News Aggregation & Publication (AGY Schedule Cron)
- **Goal**: Aggregate, classify, and publish daily curated tech news.
- **Workflow**:
  1. **AGY Ingestion**: Run `python3 scripts/collect_tech_news.py --hours 24` via `schedule` cron or background task.
  2. **OMC Classifier**: `scripts/news/analyzer.py` scores and tags articles.
  3. **Claude / Template Publish**: `scripts/auto_publish_news.py` creates post with standardized layout.
  4. **Codex / Unit Tests**: Validate template branches with `.venv/bin/pytest scripts/tests/test_news_templates.py`.
  5. **AGY Gate**: Generate news SVG cover and verify with `scripts/verify_images_unified.py --all`.

### Scenario 4: Emergency Incident & CVE Breaking Advisory (CCG Fast-Track)
- **Goal**: Rapidly publish analysis and mitigation guide for high-severity vulnerabilities (CVSS >= 8.0).
- **Workflow**:
  1. **Gemini Recon**: Rapidly extract CVSS vector, affected versions, and attack vectors from NVD / GitHub security advisories.
  2. **Codex Rule**: Draft detection rules (Falco rule, Sigma rule, Rego policy, or K8s Admission Webhook).
  3. **Claude Write-Up**: Compose Incident post with Mermaid sequence diagram, Root Cause Analysis, and actionable checklist.
  4. **AGY Gate**: Generate SVG cover, run `scripts/check_posts.py`, and publish immediately.

### Scenario 5: Script Engineering & Refactoring (OMC Team + CCG Code Review)
- **Goal**: Build or refactor Python utilities in `scripts/` with zero regressions and >=40% test coverage.
- **Workflow**:
  1. **OMC Planner/Architect**: Design module structure and interface.
  2. **Codex Implementation**: Write Python code with type hints, Google docstrings, and strict regex.
  3. **Gemini Security Review**: Audit for secrets masking (`scripts.lib.security.mask_sensitive_info`) and performance.
  4. **AGY Test Verification**: Run `.venv/bin/pytest scripts/tests/`, `ruff check scripts/ --fix`, and `mypy scripts/`.

### Scenario 6: Zero-Debt Repository Quality & Security Audit
- **Goal**: Ensure 100% compliance across dependencies, Sentry quota, SEO, and images.
- **Workflow**:
  1. **AGY Security**: `npm audit`, `bundle audit`, `./scripts/monitor_sentry_quota.sh`.
  2. **OMC Verifier**: Post structure check (`scripts/check_posts.py`), English image check (`scripts/verify_images_unified.py`).
  3. **Gate**: Verify all pre-commit hooks (`scripts/install-hooks.sh`).

---

## Antigravity Slash Commands Reference

| Slash Command | Best Usage Scenario |
|---|---|
| `/goal` | Autonomous overnight / long-running post modernization (Scenario 2) |
| `/schedule` | Setting up recurring news collection or periodic audit cron (Scenario 3) |
| `/plan` | Complex architecture or large-scale multi-file refactoring (Scenario 5) |
| `/grill-me` | Interactive interview before writing a complex technical post (Scenario 1) |
| `/teamwork-preview` | Parallel multi-agent team task distribution (Scenario 5, 6) |
| `/learn` | Persisting new project patterns or rules after critical fixes |
